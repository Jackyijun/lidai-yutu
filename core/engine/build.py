# -*- coding: utf-8 -*-
"""统一疆域引擎（第 5 步）：由 v1 数据包推算各节点疆域。

  python core/engine/build.py suitang        输出 build/engine/<短名>.json（几何池 + 各节点 u / ul / pu / pul；
                                             有重要地域的卷另有 regions：燕云十六州的范围线、分界线与注记）

数据包里每个归属点（州府、城邑、参考点）先分得一块「势力格」（全卷一次）；每个节点按「点 → 单位」归属
把格子分类，描出共享界线的覆盖图，单位之并即政权（有两个以上单位的政权另出一层）。

春秋、战国（era.toml [engine] labels = "zhanguo"）的单位注记 ul 照旧页面的写法：每个单位一组 [[经, 纬, 面积, 半径], …]
（最大的一块，另加不小于它 30% 的飞地，最多 3 处），面积按 0.05° 见方的格数计——页面按它定国名字号。
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import shapely
from scipy import ndimage
from shapely.ops import polylabel

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grid as GR          # noqa: E402
from grid import cfg, geo  # noqa: E402
import data as DA          # noqa: E402
import cost as CO          # noqa: E402
import partition as PA     # noqa: E402
import border as TR       # noqa: E402

ROOT = GR.ROOT
import os
OUT = Path(os.environ["ENGINE_OUT"]) if os.environ.get("ENGINE_OUT") else ROOT / "build" / "engine"


def enc_ll(lon, lat):
    out = []; prev = None; lx = ly = 0
    for a, b in zip(lon, lat):
        x, y = int(round(float(a) * 100)), int(round(float(b) * 100))
        if (x, y) == prev:
            continue
        out += [x, y] if prev is None else [x - lx, y - ly]
        lx, ly = x, y; prev = (x, y)
    return out


def rings_of(g):
    mr = cfg()["trace"]["min_ring"]
    out = []
    for p in shapely.get_parts(g):
        if p.area < mr:
            continue
        for r in [p.exterior] + list(p.interiors):
            if shapely.Polygon(r).area < mr:
                continue
            a = np.asarray(r.coords)
            e = enc_ll(*geo.inv(a[:, 0], a[:, 1]))
            if len(e) >= 8:
                out.append(e)
    return out


def label_of(g, land):
    gl = g.intersection(land)
    ps = [p for p in shapely.get_parts(gl) if p.geom_type == "Polygon"]
    if not ps:
        return None
    big = max(ps, key=lambda p: p.area)
    try:
        c = polylabel(big, tolerance=0.5)
    except Exception:
        c = big.representative_point()
    r = big.exterior.distance(c)
    for ring in big.interiors:
        r = min(r, ring.distance(c))
    lon, lat = geo.inv(c.x, c.y)
    return [round(float(lon), 2), round(float(lat), 2), round(sum(p.area for p in ps) / GR.DEG ** 2, 2), round(r / GR.DEG, 2)]


OLD_CELL = 0.05 ** 2    # 战国式页面的注记面积单位：0.05° 见方的格


def labels_zhanguo(g, land):
    """战国式页面的单位注记：陆上最大的一块，另加不小于 max(40 格, 最大块 30%) 的飞地，最多 3 处；面积换成旧页面的格数"""
    gl = g.intersection(land)
    ps = sorted((p for p in shapely.get_parts(gl) if p.geom_type == "Polygon"), key=lambda p: -p.area)
    out = []
    for p in ps[:3]:
        try:
            c = polylabel(p, tolerance=0.5)
        except Exception:
            c = p.representative_point()
        lon, lat = geo.inv(c.x, c.y)
        n = p.area / GR.DEG ** 2 / max(np.cos(np.radians(float(lat))), .2) / OLD_CELL
        if out and n < max(40, out[0][2] * .3):
            continue
        r = p.exterior.distance(c)
        for ring in p.interiors:
            r = min(r, ring.distance(c))
        out.append([round(float(lon), 2), round(float(lat), 2), int(round(n)), round(r / GR.DEG, 2)])
    return out


def zone_lines(polys):
    """覆盖图里相邻多边形之间的共享边（内部分界线，不含外缘），编码同疆域环；短于 0.08° 的不要"""
    if len(polys) < 2:
        return []
    allb = shapely.union_all([p.boundary for p in polys])
    outer = shapely.union_all(polys).boundary
    inner = allb.difference(outer.buffer(1e-6 * GR.DEG))
    if inner.is_empty:
        return []
    inner = shapely.line_merge(inner) if inner.geom_type == "MultiLineString" else inner
    out = []
    for ln in shapely.get_parts(inner):
        if ln.geom_type != "LineString" or ln.length <= 0.08 * GR.DEG:
            continue
        a = np.asarray(ln.coords)
        e = enc_ll(*geo.inv(a[:, 0], a[:, 1]))
        if len(e) >= 4:
            out.append(e)
    return out


AVOID = 1.2      # 重要地域的分区注记离地域总名不足 1.2°（地面距离）的地方不选，同旧构建
ROOM = 0.2       # 分区注记另取位置时，离分区边界至少这么远（度），不够就把 AVOID 减半再找


def far_label(g, land, avoid, step=0.04):
    """g 的陆上最大一块里离边界最远、又不落在 avoid 内的点（按 step° 见方的格点找）；格式同 label_of，找不到为 None"""
    ps = [p for p in shapely.get_parts(g.intersection(land)) if p.geom_type == "Polygon"]
    if not ps:
        return None
    big = max(ps, key=lambda p: p.area)
    x0, y0, x1, y1 = big.bounds
    xs, ys = np.meshgrid(np.arange(x0, x1, step * GR.DEG), np.arange(y0, y1, step * GR.DEG))
    P = shapely.points(xs.ravel(), ys.ravel())
    P = P[shapely.contains(big, P) & ~shapely.contains(avoid, P)]
    if not len(P):
        return None
    d = shapely.distance(big.boundary, P)
    k = int(np.argmax(d))
    lon, lat = geo.inv(shapely.get_x(P[k]), shapely.get_y(P[k]))
    return [round(float(lon), 2), round(float(lat), 2), round(sum(p.area for p in ps) / GR.DEG ** 2, 2), round(float(d[k]) / GR.DEG, 2)]


def _inside(L, g):
    """注记点 L（[经, 纬, …]）是否落在投影坐标的多边形 g 里"""
    x, y = geo.proj(np.array([L[0]]), np.array([L[1]]))
    return bool(g.contains(shapely.Point(x[0], y[0])))


def trace_regions(REG, N, lab_at, win, warp, clip, pins, sp, C, keys):
    """重要地域（燕云十六州）：按地域起始年那个节点的分区，成员点的格子之并描出范围线；各分区再与地域其余部分
    描一次，得分区注记，标了 line 的另出两者之间的分界线。注记取法同疆域（label_of）；分区注记离总名不足 AVOID 的，
    改取避开总名的那一点；分区注记落进它所包含的另一个分区的（宋元卷的山前七州与瀛莫），改在除去那块的部分里取。分区一律按地域起始年的分区描（分区自己的 y0 只管页面上从哪年起显示，如瀛莫 959 归周）。
    返回与 REG 等长的 [{rings, lab, groups: [{lab, lines}]}]"""
    land = shapely.union_all(C["land_xy"])
    out = []
    for y0, mem, groups in REG:
        n0 = next((n for n in N if n[0] >= y0 * 12), None)
        if n0 is None:
            sys.exit(f"重要地域（{y0} 年起）之后没有节点")
        lab = lab_at(n0)
        allm = np.isin(lab, mem)
        U = np.where(allm, 0, -1).astype(np.int32)
        g, _ = TR.polygons(win, U, warp, clip=clip, pins=pins, log=lambda *a: None, simplify=sp.get("simplify"))
        if 0 not in g:
            sys.exit(f"重要地域（{y0} 年起）的成员点在 {n0[0] // 12} 年节点都没有格子：" + "、".join(keys[i] for i in mem))
        rg = g[0]
        L = label_of(rg, C["land_xy"])
        if L is None:
            sys.exit(f"重要地域（{y0} 年起）不在陆上")
        mx, my = geo.proj(np.array([L[0]]), np.array([L[1]]))
        avoid = shapely.Point(mx[0], my[0]).buffer(AVOID * GR.DEG)
        gs, gp = [], []
        for gm, line in groups:
            Ug = np.where(np.isin(lab, gm), 0, np.where(allm, 1, -1)).astype(np.int32)
            gg, _ = TR.polygons(win, Ug, warp, clip=clip, pins=pins, log=lambda *a: None, simplify=sp.get("simplify"))
            if 0 not in gg:
                sys.exit(f"重要地域（{y0} 年起）的分区在 {n0[0] // 12} 年节点没有格子：" + "、".join(keys[i] for i in gm))
            gl = label_of(gg[0], C["land_xy"])
            if gl and _inside(gl, avoid):
                f = far_label(gg[0], land, avoid)
                if f:
                    gl = [f[0], f[1], gl[2], f[3]]
            gp.append(gg[0])
            gs.append({"lab": gl, "lines": zone_lines([gg[0], gg[1]]) if line and 1 in gg else []})
        # 分区注记落进它所包含的另一个分区（宋元卷「山前七州」落在「瀛莫二州属宋」里）：改在除去那些分区的部分里取，
        # 仍避开总名，避开后离边界不到 ROOM 的把避让半径减半再找；字号仍按整个分区的面积
        half = shapely.Point(mx[0], my[0]).buffer(AVOID / 2 * GR.DEG)
        for i, (gm, _) in enumerate(groups):
            gl = gs[i]["lab"]
            inner = [gp[j] for j, (gm2, _) in enumerate(groups) if j != i and set(gm2) < set(gm)]
            if not gl or not inner or not any(_inside(gl, g) for g in inner):
                continue
            rest = gp[i].difference(shapely.union_all(inner))
            f = label_of(rest, C["land_xy"])
            if f is None or _inside(f, avoid):
                f = far_label(rest, land, avoid)
                if f is None or f[3] < ROOM:             # 避开总名后只剩贴边的一条：避让半径减半
                    f = far_label(rest, land, half) or f
            if f:
                gs[i]["lab"] = [f[0], f[1], gl[2], f[3]]
        out.append({"rings": rings_of(rg), "lab": L, "groups": gs})
    return out


def rounded_contains(g, P):
    """g 按页面的坐标精度（经纬度 0.01°，奇偶填充）取整后是否仍严格包含点 P（投影坐标）"""
    lon, lat = geo.inv(P.x, P.y)
    Q = shapely.Point(float(lon), float(lat))
    for p in shapely.get_parts(g):
        if not p.buffer(0.02 * GR.DEG).contains(P):
            continue
        rings = []
        for r in [p.exterior] + list(p.interiors):
            a = np.asarray(r.coords)
            lo, la = geo.inv(a[:, 0], a[:, 1])
            q = shapely.Polygon(np.c_[np.round(lo, 2), np.round(la, 2)])
            rings.append(q if q.is_valid else shapely.make_valid(q))
        if not rings:
            continue
        h = rings[0]
        for q in rings[1:]:
            h = h.symmetric_difference(q)
        if h.contains(Q) and h.boundary.distance(Q) > 1e-9:
            return True
    return False


def keep_points(geoms, own, code, pts, clip, win, units=None):
    """兜底：仍有归属点不在本方疆域内的（多在国界墙交汇处、推算范围边上），在点周围补一个半径 0.6 格的小圆，
    从别的单位里扣掉。原地修改 geoms，返回补过的点的序号。
    贴着本方界线（不到 0.01°）的点再按页面的坐标精度（0.01°）取整后查一遍：取整后落到界线上或界外的也补（多是界河岸边的点）。
    这一查按单位（同一单位的区划块合起来，units 是类别序号 → 类别键）：压在本单位区划块之间的界线上不算"""
    fixed = []
    eps = 0.01 * GR.DEG
    unit_of = (lambda k: units[k].partition("\x1f")[0]) if units is not None else (lambda k: k)
    for i, u in enumerate(own):
        if u is None:
            continue
        P = shapely.Point(pts[i])
        if clip is not None and not clip.contains(P):
            continue                                  # 外缘以外的点本来就不画
        k = code[u]
        if k in geoms and geoms[k].contains(P):
            if geoms[k].boundary.distance(P) > eps:
                continue
            same = [j for j in geoms if unit_of(j) == unit_of(k)]
            g = geoms[k] if len(same) == 1 else shapely.union_all([geoms[j] for j in same])
            if rounded_contains(g, P):
                continue
        disk = P.buffer(0.6 * win.cell, 16)
        for j in list(geoms):
            if j != k and geoms[j].intersects(disk):
                geoms[j] = geoms[j].difference(disk)
        geoms[k] = geoms[k].union(disk) if k in geoms else shapely.MultiPolygon([disk])
        fixed.append(i)
    return fixed


def setup(slug, log=print):
    """一卷的计算窗口与外缘：返回 (spec, win, inner 多边形, clip 多边形或 None, 推算范围多边形)"""
    sp = DA.spec(slug)
    cell = cfg()["grid"]["cell"]
    if sp["outer"] == "frontier":
        fr = DA.frontier(slug)
        fx, fy = geo.proj(fr[:, 0], fr[:, 1])
        reg = shapely.Polygon(np.c_[fx, fy]).buffer(0)
        inner = reg.buffer(cfg()["partition"]["frontier_pad"] * cell)
        clip = reg
    elif sp["outer"] in ("reach", "box"):
        g = shapely.segmentize(DA.region(slug, sp), 0.25)
        reg = shapely.make_valid(CO.to_xy(g))
        inner, clip = reg, None
    else:
        sys.exit(f"{slug}：era.toml [engine] outer 只能是 frontier、reach 或 box")
    xmin, ymin, xmax, ymax = inner.bounds
    win = GR.Window(xmin, xmax, ymin, ymax, pad=2)
    return sp, win, inner, clip, reg


def run(slug, log=None):
    t0 = time.time()
    log = log or (lambda *a: print(f"  [{slug} {time.time() - t0:5.0f}s]", *a, flush=True))
    b = DA.bundle(slug)
    S, N = DA.view(slug)
    sp, win, inner_g, clip, _ = setup(slug, log)
    log("窗口", win.ni, "×", win.nj, f"（格 {win.km():.2f} km，起点 {win.i0}, {win.j0}）；外缘", sp["outer"])

    sx, sy = geo.proj(np.array([s[0] for s in S]), np.array([s[1] for s in S]))
    pts = list(zip(sx, sy))
    bb = CO.bbox_ll(win)
    W = DA.walls(slug, sp)
    C = CO.build(win, DA.land(bb), DA.lakes(b), DA.ranges(), DA.rivers(b, cfg()["cost"]["river"]["weights"]), W, pts, log)
    log("代价", f"{C['cost'][C['land']].min():.2f}—{C['cost'][C['land']].max():.2f}，陆地均值 {C['cost'][C['land']].mean():.2f}")
    inner = CO.mask_of(win, [inner_g])
    reach = None
    if sp["outer"] == "reach":
        R = DA.reach_mult(slug, sp)
        reach = np.array([cfg()["outer"]["reach"] * R.get(s[2], 1.0) for s in S])
        log("可达倍数", len(R), "个点")

    def group(t, act):                              # 本节点生效的有时效墙、参与分区的点
        return (tuple(i for i, v in enumerate(C["var"]) if v[3] <= t < v[4]),
                None if act is None else tuple(i for i, a in enumerate(act) if a))

    labs, where, costs = {}, {}, {}
    for t, _, _, act in N:
        k = group(t, act)
        if k in labs:
            continue
        cost = C["cost"].copy()
        for i in k[0]:
            cost += C["var"][i][1]
        costs[k] = cost
        labs[k], dist, w = PA.run(win, C, pts, inner, cost, reach, act, log, far_islands=sp.get("far_islands", False))
        where.update(w)
        log("最短路完成", "墙", [C["var"][i][0] for i in k[0]] or "常设", "" if act is None else f"参与分区 {sum(act)} 点")
    pins = sorted(set(where.values()))
    wallm = C["wall"].copy()
    for v in C["var"]:
        wallm |= v[2]
    warp = TR.Warp(win, C["river"] | wallm, pins)

    Z = DA.zones(slug, sp, b, N)                    # 二级区划块（汉末卷的州）：按「单位 × 区划块」分类，描完再按单位合并
    SUB = DA.sub(slug, sp, b)                          # 按治所细分一个单位的格子（战国卷的秦郡）：同样按「单位 × 块」分类
    if Z is not None and SUB is not None:
        sys.exit(f"{slug}：[engine] 的 zones 与 sub 只能写一个")
    SEP = "\x1f"
    if Z is not None:
        log("区划块", len({z for row in Z for z in row if z}), "个")
    cls = [own if Z is None else [None if u is None else u if z is None else u + SEP + z for u, z in zip(own, Z[ni])]
           for ni, (_, own, _, _) in enumerate(N)]
    units = {u for own in cls for u in own if u is not None}
    if SUB is not None:
        s_unit, s_hosts, s_near, seats, s_fixed = SUB
        sidx = {s[2]: i for i, s in enumerate(S)}
        s_fixed = [(sidx[p], k) for p, k in s_fixed]     # (归属点序号, 块键)：这个点的势力格整块归这一块
        s_fired = set()
        units |= {s_unit + SEP + k for k, _, _, _ in seats}
        qx, qy = geo.proj(np.array([q[1] for q in seats]), np.array([q[2] for q in seats]))
        s_pts = list(zip(qx, qy))
        s_rc = [tuple(int(round(float(v))) for v in win.rc(x, y)) for x, y in s_pts]
        s_labs = {}
        log("细分", s_unit, len(seats), "个治所")
    units = sorted(units, key=lambda u: (len(u), u))
    code = {u: i for i, u in enumerate(units)}
    ukeys = sorted({u for _, own, _, _ in N for u in own if u is not None}, key=lambda u: (len(u), u))
    pool, poolk = [], {}
    zg_labels = sp.get("labels") == "zhanguo"        # 战国式页面的单位注记（春秋、战国）
    land_u = shapely.union_all(C["land_xy"]) if zg_labels else None

    def put(rr):
        k = json.dumps(rr, separators=(",", ":"))
        if k not in poolk:
            poolk[k] = len(pool); pool.append(rr)
        return poolk[k]

    cache = {}
    out_nodes = []
    for ni, (t, own0, pol, act) in enumerate(N):
        own = cls[ni]
        lab = labs[group(t, act)]
        sc = np.array([-1 if u is None or (act is not None and not act[i]) else code[u] for i, u in enumerate(own)] + [-1], np.int32)   # 末位给 -1
        U = sc[np.where(lab >= 0, lab, len(own))]
        if SUB is not None and s_unit in code:           # 细分：治所落在 HOSTS 疆域里、已始置的参与，就近分走这个单位的格子
            hc = {code[h] for h in s_hosts if h in code}
            near = ndimage.distance_transform_edt(~np.isin(U, list(hc))) <= s_near
            on = tuple(q for q, (_, _, _, y0) in enumerate(seats) if y0 <= t // 12 and 0 <= s_rc[q][0] < win.nj
                       and 0 <= s_rc[q][1] < win.ni and near[s_rc[q]])
            m = U == code[s_unit]
            if on and m.any():
                gk = (group(t, act)[0], on)
                if gk not in s_labs:
                    s_labs[gk] = PA.run(win, C, s_pts, inner, costs[group(t, act)], None,
                                        [q in on for q in range(len(seats))], lambda *a: None)[0]
                sl = s_labs[gk]
                zc = np.array([code[s_unit + SEP + q[0]] for q in seats], np.int32)
                hit = m & (sl >= 0)
                U = U.copy(); U[hit] = zc[sl[hit]]
                own_u = own
                own = [s_unit + SEP + seats[sl[where[i]]][0] if u == s_unit and i in where and sl[where[i]] >= 0 else u
                       for i, u in enumerate(own)]
                live = {seats[q][0] for q in on}
                for pi, bk in s_fixed:                   # sub.fixed：这个点参与分区、属被细分的单位、那一块已有治所时，势力格整块归它
                    if bk in live and own_u[pi] == s_unit and (act is None or act[pi]):
                        fm = m & (lab == pi)
                        if fm.any():
                            U[fm] = code[s_unit + SEP + bk]
                            own = [s_unit + SEP + bk if own_u[i] == s_unit and i in where and fm[where[i]] else o
                                   for i, o in enumerate(own)]
                            own[pi] = s_unit + SEP + bk          # 点自己的格子总在 fm 里，不靠 where（各节点共用一张）
                            s_fired.add(pi)
        h = hashlib.sha1(U.tobytes()).hexdigest()
        if h not in cache:
            g0, _ = TR.polygons(win, U, warp, clip=clip, pins=pins, log=log, simplify=sp.get("simplify"))
            cache[h] = (g0, keep_points(g0, own if act is None else [u if a else None for u, a in zip(own, act)], code, pts, clip, win, units))
            if cache[h][1]:
                log("护点", "、".join(S[i][2] for i in cache[h][1]))
        geoms = cache[h][0]
        if Z is not None or SUB is not None:              # 区划块按单位合并（用一般的并：护点、去碎块后共享边未必逐点重合）
            by_u, by_z = {}, {}
            for k, g in geoms.items():
                uk, _, zk = units[k].partition(SEP)
                by_u.setdefault(uk, []).append(g)
                if zk:
                    by_z.setdefault(zk, []).append(g)
            merged = {uk: (shapely.union_all(gs) if len(gs) > 1 else gs[0]) for uk, gs in by_u.items()}
        else:
            merged = {units[k]: g for k, g in geoms.items()}
        u, ul, g_u = {}, {}, {}
        for key in sorted(merged, key=lambda u: (len(u), u)):
            rr = rings_of(merged[key])
            if not rr:
                continue
            g_u[key] = merged[key]
            u[key] = put(rr)
            L = labels_zhanguo(merged[key], land_u) if zg_labels else label_of(merged[key], C["land_xy"])
            if L:
                ul[key] = L
        # 政权层：有两个以上单位，或唯一的单位不是政权自己（宋元先例）
        multi = {}
        for k, p in pol.items():
            if k in g_u:
                multi.setdefault(p, []).append(k)
        pu, pul = {}, {}
        for p, ks in sorted(multi.items()):
            if len(ks) < 2 and ks[0] == p:
                continue
            g = shapely.coverage_union_all([g_u[k] for k in ks]) if len(ks) > 1 else g_u[ks[0]]
            rr = rings_of(g)
            if rr:
                pu[p] = put(rr)
                L = label_of(g, C["land_xy"])
                if L:
                    pul[p] = L
        nd = {"t": t, "u": u, "ul": ul, "pu": pu, "pul": pul}
        if SUB is not None:                               # 细分块（秦郡）：各块多边形与注记
            zp, zpl = {}, {}
            for zk, gs in sorted(by_z.items()):
                g = shapely.union_all(gs) if len(gs) > 1 else gs[0]
                rr = rings_of(g)
                if rr:
                    zp[zk] = put(rr)
                    if (L := label_of(g, C["land_xy"])):
                        zpl[zk] = L
            nd["zp"], nd["zpl"] = zp, zpl
        if Z is not None:                                 # 区划界（块与块之间的共享边，不含外缘）与区划名
            zg = {zk: (shapely.union_all(gs) if len(gs) > 1 else gs[0]) for zk, gs in sorted(by_z.items())}
            nd["zb"] = put(zone_lines(list(zg.values())))
            zmin = sp.get("zone_label_min", 0) * GR.DEG ** 2
            nd["zl"] = [[zk.split("|")[0]] + L for zk, g in zg.items()
                        if g.area >= zmin and (L := label_of(g, C["land_xy"]))]
        out_nodes.append(nd)
        log(f"节点 {t // 12}.{t % 12 + 1:02d}", len(u), "单位", len(pu), "政权层")

    if SUB is not None and len(s_fired) < len(s_fixed):
        log("sub.fixed 从未生效（归属点不属被细分的单位、不参与分区，或那一郡还没有治所）：", "、".join(S[p][2] for p, _ in s_fixed if p not in s_fired))
    REG = DA.regions(b)
    regions = trace_regions(REG, N, lambda n: labs[group(n[0], n[3])], win, warp, clip, pins, sp, C,
                            [s[2] for s in S]) if REG else None
    if regions:
        log("重要地域", len(regions), "处")

    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"window": [win.i0, win.j0, win.ni, win.nj], "cell": win.cell, "outer": sp["outer"],
            "seeds": {str(i): [int(r), int(c)] for i, (r, c) in where.items()},
            "input": DA.fingerprint(slug, b)}                                  # 第 7 步：eras/<短名>/engine.json 是否过期
    meta["keys"] = {u: b["polities"][int(u)]["key"] for u in ukeys}          # 单位序号 → 单位键（衔接节点按键对上邻卷）
    if SUB is not None:
        meta["sub"] = s_unit
    res = {"era": slug, "geom": pool, "nodes": out_nodes, "meta": meta}
    if regions:
        res["regions"] = regions
    (OUT / f"{slug}.json").write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    np.savez_compressed(OUT / f"{slug}.npz", lab=labs[group(N[-1][0], N[-1][3])], land=C["land"])
    log("完成", len(pool), "块几何 →", f"build/engine/{slug}.json")
    return res


if __name__ == "__main__":
    for s in sys.argv[1:] or ["suitang"]:
        run(s)
