# -*- coding: utf-8 -*-
"""统一疆域引擎（第 5 步）：由 v1 数据包推算各节点疆域。

  python core/engine/build.py suitang        输出 build/engine/<短名>.json（几何池 + 各节点 u / ul / pu / pul）

数据包里每个归属点（州府、城邑、参考点）先分得一块「势力格」（全卷一次）；每个节点按「点 → 单位」归属
把格子分类，描出共享界线的覆盖图，单位之并即政权（有两个以上单位的政权另出一层）。
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import shapely
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


def keep_points(geoms, own, code, pts, clip, win):
    """兜底：仍有归属点不在本方疆域内的（多在国界墙交汇处、推算范围边上），在点周围补一个半径 0.6 格的小圆，
    从别的单位里扣掉。原地修改 geoms，返回补过的点的序号"""
    fixed = []
    for i, u in enumerate(own):
        if u is None:
            continue
        P = shapely.Point(pts[i])
        if clip is not None and not clip.contains(P):
            continue                                  # 外缘以外的点本来就不画
        k = code[u]
        if k in geoms and geoms[k].contains(P):
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
    elif sp["outer"] == "reach":
        g = shapely.segmentize(DA.region(slug, sp), 0.25)
        reg = shapely.make_valid(CO.to_xy(g))
        inner, clip = reg, None
    else:
        sys.exit(f"{slug}：era.toml [engine] outer 只能是 frontier 或 reach")
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

    labs, where = {}, {}
    for t, _, _, act in N:
        k = group(t, act)
        if k in labs:
            continue
        cost = C["cost"].copy()
        for i in k[0]:
            cost += C["var"][i][1]
        labs[k], dist, w = PA.run(win, C, pts, inner, cost, reach, act, log, far_islands=sp.get("far_islands", False))
        where.update(w)
        log("最短路完成", "墙", [C["var"][i][0] for i in k[0]] or "常设", "" if act is None else f"参与分区 {sum(act)} 点")
    pins = sorted(set(where.values()))
    wallm = C["wall"].copy()
    for v in C["var"]:
        wallm |= v[2]
    warp = TR.Warp(win, C["river"] | wallm, pins)

    Z = DA.zones(slug, sp, b, N)                    # 二级区划块（汉末卷的州）：按「单位 × 区划块」分类，描完再按单位合并
    SEP = "\x1f"
    if Z is not None:
        log("区划块", len({z for row in Z for z in row if z}), "个")
    cls = [own if Z is None else [None if u is None else u if z is None else u + SEP + z for u, z in zip(own, Z[ni])]
           for ni, (_, own, _, _) in enumerate(N)]
    units = sorted({u for own in cls for u in own if u is not None}, key=lambda u: (len(u), u))
    code = {u: i for i, u in enumerate(units)}
    ukeys = sorted({u for _, own, _, _ in N for u in own if u is not None}, key=lambda u: (len(u), u))
    pool, poolk = [], {}

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
        h = hashlib.sha1(U.tobytes()).hexdigest()
        if h not in cache:
            g0, _ = TR.polygons(win, U, warp, clip=clip, pins=pins, log=log, simplify=sp.get("simplify"))
            cache[h] = (g0, keep_points(g0, own if act is None else [u if a else None for u, a in zip(own, act)], code, pts, clip, win))
            if cache[h][1]:
                log("护点", "、".join(S[i][2] for i in cache[h][1]))
        geoms = cache[h][0]
        if Z is not None:                                 # 区划块按单位合并（用一般的并：护点、去碎块后共享边未必逐点重合）
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
            L = label_of(merged[key], C["land_xy"])
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
        if Z is not None:                                 # 区划界（块与块之间的共享边，不含外缘）与区划名
            zg = {zk: (shapely.union_all(gs) if len(gs) > 1 else gs[0]) for zk, gs in sorted(by_z.items())}
            nd["zb"] = put(zone_lines(list(zg.values())))
            zmin = sp.get("zone_label_min", 0) * GR.DEG ** 2
            nd["zl"] = [[zk.split("|")[0]] + L for zk, g in zg.items()
                        if g.area >= zmin and (L := label_of(g, C["land_xy"]))]
        out_nodes.append(nd)
        log(f"节点 {t // 12}.{t % 12 + 1:02d}", len(u), "单位", len(pu), "政权层")

    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"window": [win.i0, win.j0, win.ni, win.nj], "cell": win.cell, "outer": sp["outer"],
            "seeds": {str(i): [int(r), int(c)] for i, (r, c) in where.items()},
            "input": DA.fingerprint(slug, b)}                                  # 第 7 步：eras/<短名>/engine.json 是否过期
    if b["model"] == "layered":
        meta["keys"] = {u: b["polities"][int(u)]["key"] for u in ukeys}      # 单位序号 → 单位键（衔接节点按键对上邻卷）
    res = {"era": slug, "geom": pool, "nodes": out_nodes, "meta": meta}
    (OUT / f"{slug}.json").write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    np.savez_compressed(OUT / f"{slug}.npz", lab=labs[group(N[-1][0], N[-1][3])], land=C["land"])
    log("完成", len(pool), "块几何 →", f"build/engine/{slug}.json")
    return res


if __name__ == "__main__":
    for s in sys.argv[1:] or ["suitang"]:
        run(s)
