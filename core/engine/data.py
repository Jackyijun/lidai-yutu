# -*- coding: utf-8 -*-
"""引擎的输入：一卷的 v1 数据包（归属点、节点）加上全局的山川、陆地，以及各卷 era.toml 的 [engine]。

  bundle(slug)            build/v1/<短名>.json
  view(slug)              归属点与各节点的「点 → 单位 → 政权」
  ranges()                全局山脉：每条取一种画法（global/decisions.toml 的 [physical.prefer]，其余取多数卷）
  rivers(b) / lakes(b)    界河与湖：取本卷画的（黄河、淮河等历代改道，各卷画的是本时代的河道）
  land(bbox)              Natural Earth 1:10m 陆地与小岛（经纬度多边形）
  ne_ranges()             Natural Earth 山地多边形
  frontier(slug)          手绘外缘（隋唐、两晋），没有则 None
  fingerprint(slug, b)    引擎输入的指纹（归属点、节点归属、引擎参数、外缘、可达倍数、国界墙、区划、重要地域）：eras/<短名>/engine.json 过期没有，靠它判断
  spec / region / reach_mult / walls    各卷的外缘设置、推算范围、各点可达倍数、国界墙（global/walls.toml）
  zones / sub             二级区划：按 v1 节点的 zone 分块（汉末卷的州）/ 按治所就近细分一个单位的格子（战国卷的秦郡）
  regions(b)              重要地域（唐宋、宋元的燕云十六州）：成员点与分区
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import shapely
from shapely.geometry import shape, box

ROOT = Path(__file__).resolve().parents[2]
V1 = ROOT / "build" / "v1"
NE = ROOT / "geodata" / "ne"
ERAS = ["chunqiu", "zhanguo", "qinhan", "hanmosanguo", "liangjin-nanbeichao", "suitang", "tangsong", "songyuan", "minguo-xinzhongguo"]

try:
    import tomllib
except ImportError:
    import tomli as tomllib

_B = {}


def bundle(slug):
    if slug not in _B:
        p = V1 / f"{slug}.json"
        if not p.exists():
            sys.exit(f"缺 build/v1/{slug}.json，先运行 python run.py --v1")
        b = json.loads(p.read_text(encoding="utf8"))
        if b.get("v") != 2:
            sys.exit(f"build/v1/{slug}.json 是旧版格式（v {b.get('v')}），先运行 python run.py --v1")
        _B[slug] = b
    return _B[slug]


def dec(a):
    """v1 的整数差分序列 → [(经, 纬)]"""
    x = y = 0; out = []
    for i in range(0, len(a) - 1, 2):
        x += a[i]; y += a[i + 1]; out.append((x / 100, y / 100))
    return out


def view(slug, b=None):
    """引擎读入的「点 → 单位 → 政权」（规范第十九节），取 v1 的 places 与各节点的 own / pol：

      seeds  [(经, 纬, 键)]
      nodes  [(t, own, pol, active)]：own = 各点归哪个单位（polities 的序号，字符串；不属任何单位为 None），
             pol = {单位: 政权}，active = 各点这一节点是否参与分区（None 为全部参与）

    归属点写了 t1 的（春秋、战国为早期小国、戎狄补的点，seeds.txt 的 ~年份），t1 以后的节点不参与分区；
    写了 t0 的（seeds.txt 的 ^年份，如战国卷前280 起的下辨），t0 以前的节点不参与分区。
    衔接节点上 v1 的 own 已按照搬来的疆域对齐过的（core/v1/engine_geom.py 的 align_own），取本卷原来的归属 own_src。"""
    b = b or bundle(slug)
    S = [(p["lon"], p["lat"], p["key"]) for p in b["places"]]
    ends = [p.get("t1") for p in b["places"]]
    starts = [p.get("t0") for p in b["places"]]
    some = any(e is not None for e in ends) or any(s is not None for s in starts)
    N = []
    for n in b["nodes"]:
        own = [None if v is None or v < 0 else str(v) for v in n.get("own_src", n["own"])]
        act = [(e is None or n["t"] <= e) and (s is None or n["t"] >= s) for e, s in zip(ends, starts)] if some else None
        N.append((n["t"], own, {k: str(v) for k, v in n["pol"].items()}, act))
    return S, N


# ---------------- 全局山脉 ----------------
def ranges():
    """[(全局 ID, 是否主干, [(经, 纬)])]，每个全局 ID 一条"""
    prefer = tomllib.loads((ROOT / "global" / "decisions.toml").read_text(encoding="utf8")).get("physical", {}).get("prefer", {})
    cand = defaultdict(list)                  # gid → [(卷, 主干, 几何)]
    for slug in ERAS:
        for it in bundle(slug)["items"]:
            if it["c"] == "range" and it.get("geo") and it.get("gid"):
                g = [tuple(p) for p in it["geo"]]
                cand[it["gid"]].append((slug, bool(it.get("major")), g))
    out = []
    for gid in sorted(cand):
        L = cand[gid]
        want = prefer.get(gid, {}).get("era")
        pick = [x for x in L if x[0] == want]
        if not pick:                          # 取画法相同的卷最多的一种；并列取卷次靠后的
            cnt = Counter(tuple(x[2]) for x in L)
            best = max(cnt.values())
            pick = [x for x in reversed(L) if cnt[tuple(x[2])] == best]
        slug, _, g = pick[0]
        major = any(x[1] for x in L if x[2] == g)
        out.append((gid, major, g))
    return out


# ---------------- 本卷的河湖 ----------------
def rivers(b, weights):
    """{全局 ID: [[(经, 纬)], …]}，只取 weights 里列出的界河"""
    its = {it["i"]: it for it in b["items"]}
    out = defaultdict(list)
    for r in b["base"]["rivers"]:
        it = its.get(r.get("it"))
        if it and it.get("gid") in weights:
            out[it["gid"]].append(dec(r["p"]))
    return dict(out)


def lakes(b):
    out = []
    for lk in b["base"]["lakes"]:
        pts = dec(lk["r"])
        if len(pts) >= 4:
            out += [g for g in shapely.get_parts(shapely.make_valid(shapely.Polygon(pts))) if g.geom_type == "Polygon"]
    return out


# ---------------- 陆地 ----------------
_LAND = None


def land(bbox):
    """经纬度 bbox（西, 东, 南, 北）内的陆地多边形列表；东经可大于 180（接缝以东）"""
    global _LAND
    if _LAND is None:
        polys = []
        for nm in ("ne_10m_land", "ne_10m_minor_islands"):
            for f in json.loads((NE / f"{nm}.geojson").read_text(encoding="utf8"))["features"]:
                g = shape(f["geometry"])
                polys += list(shapely.get_parts(g))
        _LAND = polys
    W, E, S, N = bbox
    out = []
    for shift in (0, 360):                    # 接缝以东（东经 180 以东）的陆地平移 360°
        bb = box(W - shift, S, E - shift, N)
        for p in _LAND:
            if p.intersects(bb):
                q = p.intersection(bb)
                if shift:
                    q = shapely.transform(q, lambda a: a + [shift, 0])
                out += [g for g in shapely.get_parts(q) if g.geom_type == "Polygon"]
    return out


_NER = None


def ne_ranges():
    """Natural Earth 山地多边形（Range/mtn，面积 60 平方度以下）"""
    global _NER
    if _NER is None:
        _NER = []
        for f in json.loads((NE / "ne_10m_geography_regions_polys.geojson").read_text(encoding="utf8"))["features"]:
            p = f["properties"]
            if f["geometry"] and p.get("FEATURECLA") == "Range/mtn":
                g = shape(f["geometry"])
                if g.area < 60:
                    _NER.append(g if g.is_valid else shapely.make_valid(g))
    return _NER


# ---------------- 外缘 ----------------
def frontier(slug):
    """手绘外缘（经纬度点列），各卷 content/frontier.py 的 outer_lonlat()；没有则 None"""
    p = ROOT / "eras" / slug / "content" / "frontier.py"
    if not p.exists():
        return None
    return load_source(p, f"frontier_{slug.replace('-', '_')}").outer_lonlat()


# ---------------- 各卷的引擎设置（era.toml 的 [engine]） ----------------
def spec(slug):
    """era.toml 的 [engine]：
      outer = "frontier"   手绘外缘（content/frontier.py 的 outer_lonlat()）
      outer = "reach"      按可达代价定外缘；box = 推算范围 [西, 东, 南, 北]，exclude = 推算范围里剔除的多边形（民国卷的欧洲、非洲），
                           seeds = 写各点可达倍数的史料文件（文本里的 R=倍数，或 Python 文件里的 RM，见 reach_mult）
      outer = "box"        box 以内的陆地全部分给代价最近的点，不按可达代价截断；外缘由不属任何一方的点（·）定（春秋、战国）
      walls = true / prov_walls = true   烧国界墙（全局表 global/walls.toml）/ 今中国省界弱墙（民国）
      simplify = 0.25      覆盖简化容差（格），不写取 config.toml 的 [trace] simplify（0.06）；视野大、节点多的卷放宽，免得页面过大
      far_islands = true   远洋小岛也并入最近的一方（民国卷：殖民地、委任统治地的群岛多没有归属点）；缺省只认离有主地闭运算半径以内的
      zones = true         二级区划（汉末卷的州）：各点所在的区划块取 v1 节点的 zone（本卷第 1 段逐节点写出），
                           按「单位 × 区划」分块描界，另出区划界 zb 与区划名 zl（zone_label_min：标名的最小面积，平方度）
      labels = "zhanguo"   单位注记按战国式页面的写法（春秋、战国）：陆上最大的一块另加飞地，最多 3 处，面积按旧页面的格数
      sub.unit / sub.hosts / sub.near / sub.seats   一个单位的格子再按治所就近细分（战国卷的秦郡）：unit 是被细分的单位，
                           hosts 是治所须落在其疆域里的单位（near：离其疆域不到这么多格的也算），治所取 v1 里 seats 那一类条目
                           （键 k、经纬度、始置年）；另出各块的多边形 zp 与注记 zpl
      sub.fixed            [[归属点, 块], …]：这些归属点的势力格整块归某块，不按治所远近分（战国卷的下辨归陇西郡）
    引擎只读这里、v1 数据包、全局表（山川、国界墙）与各卷的两样史料：手绘外缘 content/frontier.py、写可达倍数的 seeds 文件"""
    t = tomllib.loads((ROOT / "eras" / slug / "era.toml").read_text(encoding="utf8"))
    s = t.get("engine")
    if not s:
        sys.exit(f"eras/{slug}/era.toml 没有 [engine]，这一卷还没接上统一引擎")
    return s


def load_source(p, name):
    """按源文件载入一个 Python 文件（不读 __pycache__：改了又改回、同一秒内大小不变时，按时间戳判断的字节码缓存会用错）"""
    import types
    m = types.ModuleType(name)
    m.__file__ = str(p)
    exec(compile(Path(p).read_text(encoding="utf8"), str(p), "exec"), m.__dict__)
    return m


def era_module(slug, rel):
    """载入一卷自己的 Python 史料文件（seeds 指向的 content/seeds.py），只读其中的常量"""
    p = ROOT / "eras" / slug / rel
    return load_source(p, f"cfg_{slug.replace('-', '_')}_{p.stem}")


def reach_mult(slug, s):
    """各点可达代价倍数，{点 ID: 倍数}，没列的点取 1。seeds 指向本卷的史料：文本文件（或文件夹里的各个 .txt）里每行
    「点 经 纬 归属 …」后面的 R=倍数（唐宋、宋元、民国），或 Python 文件里的 RM 字典（汉末、秦汉）；
    不写 seeds、也没有 content/seeds.txt 的卷一律取 1"""
    out = {}
    p = ROOT / "eras" / slug / s.get("seeds", "content/seeds.txt")
    if "seeds" not in s and not p.exists():
        return out
    if p.suffix == ".py":
        rm = getattr(era_module(slug, s["seeds"]), "RM", None)
        if not isinstance(rm, dict):
            sys.exit(f"eras/{slug}/{s['seeds']}：era.toml [engine] 的 seeds 指向的 Python 文件里要有字典 RM（点 ID → 可达倍数）")
        return {str(k): float(v) for k, v in rm.items()}
    files = sorted(p.glob("*.txt")) if p.is_dir() else [p]
    for f in files:
        for line in f.read_text(encoding="utf8").splitlines():
            t = line.split()
            if not t or t[0].startswith("#"):
                continue
            for x in t[4:]:
                if x.startswith("R="):
                    out[t[0]] = float(x[2:])
    return out


def sub(slug, s, b=None):
    """[engine] sub：(被细分的单位, 治所须落在其中的单位, 容差格数, [(块键, 经, 纬, 始置年)], [(归属点键, 块键)])；
    没写 sub 的卷返回 None。era.toml 里 sub.unit、sub.hosts 写单位键（如「秦」），这里换成节点里的单位序号；治所取 v1 里
    sub.seats 那一类条目（战国卷的 jun：块键是条目的 k，始置年取条目的 t）。sub.fixed 写 [[归属点键, 块键], …]：
    那个归属点的势力格整块归这一块，不按治所远近分（战国卷的下辨归陇西郡，单按郡治远近会分给汉中郡）；
    归属点那年不参与分区、不属被细分的单位，或那一块的治所还没参与时，照常按治所分"""
    if not s.get("sub"):
        return None
    c = s["sub"]
    miss = [k for k in ("unit", "hosts", "seats") if k not in c] if isinstance(c, dict) else ["unit", "hosts", "seats"]
    if miss:
        sys.exit(f"eras/{slug}/era.toml [engine]：sub 要写 sub.unit、sub.hosts、sub.seats（缺 {'、'.join(miss)}；sub.near 可不写）")
    b = b or bundle(slug)
    ix = {p["key"]: str(i) for i, p in enumerate(b["polities"])}
    if c["unit"] not in ix:
        sys.exit(f"eras/{slug}/era.toml [engine] sub.unit：被细分的单位「{c['unit']}」不在本卷的政权表里")
    seats = [(str(it["k"]), float(it["lon"]), float(it["lat"]), it["t"] // 12) for it in b["items"] if it.get("c") == c["seats"]]
    if not seats:
        sys.exit(f"eras/{slug}/era.toml [engine] sub.seats：本卷没有「{c['seats']}」类条目")
    keys = {k for k, _, _, _ in seats}
    places = {p["key"] for p in b["places"]}
    fixed = []
    for e in c.get("fixed", []):
        if not (isinstance(e, list) and len(e) == 2 and all(isinstance(v, str) for v in e) and e[0] in places and e[1] in keys):
            sys.exit(f"eras/{slug}/era.toml [engine] sub.fixed：每项写 [归属点键, 块键]，归属点须在本卷、块键须是已有的治所（{e}）")
        fixed.append((e[0], e[1]))
    if len({p for p, _ in fixed}) != len(fixed):
        sys.exit(f"eras/{slug}/era.toml [engine] sub.fixed：同一个归属点写了两遍")
    return (ix[c["unit"]], tuple(ix[h] for h in c["hosts"] if h in ix), float(c.get("near", 0)), seats, fixed)


def zones(slug, s, b, N):
    """[engine] zones = true：各节点各点所在的区划块（与 N 等长，每项是各点的块键字符串，None 为不分块），取 v1 节点的 zone
    （汉末卷的州块「州|政权」，由本卷第 1 段逐节点写出）；没写 zones 的卷返回 None"""
    if not s.get("zones"):
        return None
    nodes = b["nodes"]
    if len(nodes) != len(N):
        sys.exit(f"{slug}：v1 节点数与引擎读入的节点数不同")
    out = []
    for n, (t, own, pol, act) in zip(nodes, N):
        z = n.get("zone")
        if z is None or len(z) != len(own):
            sys.exit(f"{slug}：era.toml [engine] 写了 zones，v1 节点 {t // 12} 年却没有（或长度不对的）zone；先运行 python run.py {slug}")
        out.append([None if u is None else z[i] for i, u in enumerate(own)])
    return out


def regions(b):
    """重要地域（v1 base.regions，唐宋、宋元的燕云十六州）：[(起年, 成员点序号, [(分区成员点序号, 画不画分界线)])]。
    成员点含 extra（雄州、霸州），由第 1 段构建（eras/<短名>/src/build.py）写进 m"""
    out = []
    for R in (b.get("base") or {}).get("regions", []):
        if "m" not in R or any("m" not in g for g in R.get("groups", [])):
            sys.exit(f"{b.get('era', '')}：v1 base.regions 第 {len(out) + 1} 个地域没写成员点 m（source.json 过期？先运行 python run.py {b.get('era', '<短名>')}）")
        out.append((R["y0"], list(R["m"]), [(list(g["m"]), bool(g.get("line"))) for g in R.get("groups", [])]))
    return out


def view_seeds(b):
    return [(p["lon"], p["lat"], p["key"]) for p in b["places"]]


def region(slug, s):
    """reach 卷的推算范围（经纬度多边形）：box 减去 era.toml [engine] 的 exclude"""
    W, E, S, N = s["box"]
    g = box(W, S, E, N)
    ex = s.get("exclude", [])
    if ex:
        g = g.difference(shapely.union_all([shapely.Polygon(p) for p in ex]))
    return g


def _month(s_):
    y, m = s_.split("."); return int(y) * 12 + int(m) - 1


def wall_table():
    """全局国界墙表 global/walls.toml：ne_skip（今国界里不用的框）、ne_var（有时效的今国界段）、manual（手画的历史界线）"""
    t = tomllib.loads((ROOT / "global" / "walls.toml").read_text(encoding="utf8"))
    bad = lambda msg: sys.exit("global/walls.toml：" + msg)
    names = [w["name"] for w in t.get("ne_skip", [])]
    if len(set(names)) != len(names):
        bad("ne_skip 里有重名的框")
    for k, need in (("ne_skip", ("name", "poly")), ("ne_var", ("name", "skip")), ("manual", ("name", "line"))):
        for w in t.get(k, []):
            miss = [f for f in need if f not in w]
            if miss:
                bad(f"{k}「{w.get('name', '?')}」缺 {'、'.join(miss)}")
            for f in ("from", "to"):
                if f in w and not (isinstance(w[f], str) and len(w[f].split(".")) == 2 and all(x.lstrip("-").isdigit() for x in w[f].split("."))):
                    bad(f"{k}「{w['name']}」的 {f} 要写成带引号的「年.月」，如 \"1953.07\"")
    for w in t.get("ne_var", []):
        if w["skip"] not in names:
            bad(f"ne_var「{w['name']}」的 skip「{w['skip']}」不在 ne_skip 里")
    return t


def walls(slug, s):
    """国界墙（民国式），取全局表 global/walls.toml。返回 dict：fixed = 常设墙折线、prov = 今中国省界（弱墙）、
    var = [(名称, 折线, 起月, 止月)]；折线都是经纬度点列。没有墙的卷返回 None"""
    if not s.get("walls"):
        return None
    T = wall_table()
    skips = {w["name"]: w["poly"] for w in T.get("ne_skip", [])}
    W, E, S, N = s["box"]
    BB = box(W - 1, S - 1, E + 1, N + 1)
    reg = region(slug, s)
    ctry = []
    for f in json.loads((NE / "ne_10m_admin_0_countries_chn.geojson").read_text(encoding="utf8"))["features"]:
        if f["geometry"]:
            g = shape(f["geometry"])
            if g.intersects(BB):
                ctry.append(g.intersection(BB))
    landu = shapely.union_all(land((W - 1, E + 1, S - 1, N + 1)))
    coast = landu.boundary.buffer(0.04)
    bl = shapely.union_all([g.boundary for g in ctry]).difference(coast)
    skip = shapely.union_all([shapely.Polygon(p) for p in skips.values()])
    fixed_g = bl.difference(skip).intersection(reg.buffer(0.5))

    def lines(g):
        return [list(l.coords) for l in shapely.get_parts(shapely.line_merge(g)) if l.geom_type == "LineString" and len(l.coords) > 1]

    def seg(pts):
        return list(shapely.segmentize(shapely.LineString(pts), 0.05).coords)

    timed = lambda w: "from" in w or "to" in w
    span = lambda w: (_month(w["from"]) if "from" in w else -10 ** 9, _month(w["to"]) if "to" in w else 10 ** 9)
    fixed = lines(fixed_g) + [seg(w["line"]) for w in T.get("manual", []) if not timed(w)]
    var = [(w["name"], [seg(w["line"])], *span(w)) for w in T.get("manual", []) if timed(w)]
    var += [(w["name"], lines(bl.intersection(shapely.Polygon(skips[w["skip"]]))), *span(w)) for w in T.get("ne_var", [])]
    prov = []
    if s.get("prov_walls"):
        P = json.loads((ROOT / "geodata" / "prov" / "tangsong.json").read_text(encoding="utf8"))
        pv = [shapely.Polygon(dec(r)) for p in P for r in p["r"] if len(r) >= 6]
        pb = shapely.union_all([g.boundary for g in pv]).difference(coast).difference(fixed_g.buffer(0.1))
        prov = lines(pb)
    return dict(fixed=fixed, prov=prov, var=var)


# ---------------- 引擎输入的指纹（第 7 步） ----------------
def fingerprint(slug, b=None):
    """由引擎读入的东西算一个指纹：归属点与各节点的「点 → 单位 → 政权」（view）、core/engine/config.toml、
    era.toml 的 [engine]（含推算范围 box、exclude）、手绘外缘的点列、各点可达倍数、国界墙表、区划块与细分治所、重要地域的成员点。
    各卷页面疆域取 eras/<短名>/engine.json 时，拿它判断那份结果是不是按当前输入算的。外缘、可达倍数、墙都按读出来的数据算，
    改注释不必重算（架构整理第五批起；此前可达倍数与国界墙漏算，外缘按文件字节算）。
    山脉、界河、陆地等全局底图不计在内（改了要手动重算：python run.py <短名>）。"""
    import hashlib
    b = b or bundle(slug)
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf8")
    S, N = view(slug, b)
    sp = spec(slug)
    h = hashlib.sha1()
    h.update(js([[list(x) for x in S], [[t, own, sorted(pol.items()), act] for t, own, pol, act in N]]))
    h.update((ROOT / "core" / "engine" / "config.toml").read_bytes())
    h.update(js({k: v for k, v in sp.items() if k != "geometry"}))
    fr = frontier(slug)
    if fr is not None:                                # 手绘外缘
        h.update(js(fr.tolist()))
    if sp.get("outer") == "reach":                    # 各点可达倍数
        h.update(js(sorted(reach_mult(slug, sp).items())))
    if sp.get("walls"):                               # 国界墙表（不算说明文字）
        T = wall_table()
        h.update(js({k: [{f: v for f, v in w.items() if f != "note"} for w in T.get(k, [])] for k in ("ne_skip", "ne_var", "manual")}))
    if sp.get("zones"):                               # 区划块
        h.update(js(zones(slug, sp, b, N)))
    if sp.get("sub"):                                 # 细分：治所表
        h.update(js(sub(slug, sp, b)))
    reg = regions(b)
    if reg:                                           # 重要地域：成员点与分区
        h.update(js(reg))
    return h.hexdigest()[:16]
