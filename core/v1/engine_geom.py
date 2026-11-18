# -*- coding: utf-8 -*-
"""第 7 步：旧卷的页面疆域改由统一疆域引擎出（core/engine/）。

era.toml 的 [engine] 写 geometry = "engine" 的卷，生成 v1 时把 legacy.html 里旧引擎画的几何（各节点 u / ul / pu / pul）
换成 eras/<短名>/engine.json——那是 core/engine/build.py 的结果，入库，所以 python run.py --web 不必重算疆域，结果也与库版本无关。
归属、文字、条目仍取 legacy.html。

engine.json 记着引擎输入的指纹（core/engine/data.py 的 fingerprint）。归属点或节点归属改了、指纹对不上时：
  strict = True（默认）  停下，提示先运行 python run.py <短名> 重算；
  strict = False         照用 legacy.html 的几何并提示（run.py 在重算之前先出一遍 v1 时用）。

衔接节点（global/junctions.toml 里 shared 的一年）：
  - 本卷是准的一方：照用本卷引擎的结果；
  - 对方是准、对方也已换到引擎：在对方的推算范围（手绘外缘）以内照搬对方引擎的几何，范围以外用本卷的，
    跨线的同一单位两部分合并（单位按键对上）；
  - 对方是准、还没换到引擎：这个节点整个保留 legacy.html 里的几何（旧构建本来就照搬了对方）。
"""
import json
import sys
from functools import reduce
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core" / "engine"))

try:
    import tomllib
except ImportError:
    import tomli as tomllib

PAD_IN = 0.05          # 对方范围以内 0.05° 起整片照搬对方（含对方有意留白之处）；贴着范围线的窄条由本卷补，免得接缝露白
MIN_PART = 0.002       # 合并后丢掉小于此面积（平方度）的碎块


def era_toml(slug):
    return tomllib.loads((ROOT / "eras" / slug / "era.toml").read_text(encoding="utf8"))


def migrated(slug):
    return era_toml(slug).get("engine", {}).get("geometry") == "engine"


def path_of(slug):
    return ROOT / "eras" / slug / "engine.json"


def load(slug):
    p = path_of(slug)
    return json.loads(p.read_text(encoding="utf8")) if p.exists() else None


# ---------------- 几何：v1 的整数差分环 ↔ shapely（经纬度） ----------------
def dec(flat):
    x = y = 0; out = []
    for i in range(0, len(flat) - 1, 2):
        x += flat[i]; y += flat[i + 1]; out.append((x / 100, y / 100))
    return out


def shape_of(rings):
    import shapely
    ps = []
    for r in rings:
        pts = dec(r)
        if len(pts) >= 3:
            p = shapely.Polygon(pts)
            ps.append(p if p.is_valid else shapely.make_valid(p))
    if not ps:
        return shapely.Polygon()
    return reduce(lambda a, b: a.symmetric_difference(b), ps)           # 奇偶填充，与页面一致


def enc_ring(coords):
    out, prev, lx, ly = [], None, 0, 0
    for a, b in coords:
        x, y = int(round(a * 100)), int(round(b * 100))
        if (x, y) == prev:
            continue
        out += [x, y] if prev is None else [x - lx, y - ly]
        lx, ly, prev = x, y, (x, y)
    return out


def rings_of(g):
    import shapely
    out = []
    for p in shapely.get_parts(g):
        if p.geom_type != "Polygon" or p.area < MIN_PART:
            continue
        for r in [p.exterior] + list(p.interiors):
            e = enc_ring(r.coords)
            if len(e) >= 8:
                out.append(e)
    return out


def polys(g):
    import shapely
    if g.is_empty:
        return g
    ps = [p for p in shapely.get_parts(shapely.make_valid(g)) if p.geom_type == "Polygon" and p.area >= MIN_PART]
    return shapely.MultiPolygon(ps) if ps else shapely.Polygon()


# ---------------- 衔接 ----------------
def junction_nodes(slug, b):
    """本卷的衔接节点：[(节点序号, 准的一卷, 对方在这一年的节点序号)]，只列对方为准的"""
    t = tomllib.loads((ROOT / "global" / "junctions.toml").read_text(encoding="utf8"))
    out = []
    for j in t.get("junction", []):
        if j.get("kind") != "shared" or slug not in (j["from"], j["to"]) or j.get("owner") == slug:
            continue
        mine = len(b["nodes"]) - 1 if slug == j["from"] else 0
        theirs = 0 if slug == j["from"] else -1
        out.append((mine, j["owner"], theirs))
    return out


def region_of(owner):
    """准的一卷的推算范围（经纬度多边形）：手绘外缘。按可达代价定外缘的卷换过来时再补"""
    import shapely
    import data as DA
    sp = DA.spec(owner)
    if sp.get("outer") != "frontier":
        sys.exit(f"{owner}：衔接照搬目前只支持手绘外缘的卷（outer = \"frontier\"）")
    fr = DA.frontier(owner)
    return shapely.Polygon(fr).buffer(0)


def merge_node(b, mine, eng_mine, owner, theirs):
    """衔接节点：对方范围以内照搬对方引擎的几何，以外用本卷引擎的。返回本卷单位序号 → shapely"""
    import shapely
    oe = load(owner)
    R = region_of(owner)
    R_in = R.buffer(-PAD_IN)
    on = oe["nodes"][theirs]
    okeys = oe["meta"]["keys"]
    idx = {p["key"]: str(i) for i, p in enumerate(b["polities"])}
    A = {}
    for u, g in on["u"].items():
        k = okeys[u]
        if k not in idx:
            sys.exit(f"衔接节点：{owner} 的单位「{k}」在本卷没有同键的单位")
        A[idx[k]] = shape_of(oe["geom"][g])
    A_all = shapely.union_all(list(A.values()))
    B = {u: shape_of(eng_mine["geom"][g]) for u, g in eng_mine["nodes"][mine]["u"].items()}
    out = {}
    for u in sorted(set(A) | set(B), key=lambda x: (len(x), x)):
        inside = A.get(u, shapely.Polygon())
        outside = B[u].difference(A_all).difference(R_in) if u in B else shapely.Polygon()
        g = polys(inside.union(outside))
        if not g.is_empty:
            out[u] = (g, inside.area, outside.area)
    return out, on, oe


# ---------------- 换几何 ----------------
def apply(slug, b, strict=True, log=print):
    """把 b（v1 数据包，已由 legacy.html 转出）的疆域换成引擎的。返回记进 meta.overlay 的一句话；本卷没换到引擎则 None"""
    if not migrated(slug):
        return None
    import data as DA
    e = load(slug)
    why = None
    if e is None:
        why = f"缺 eras/{slug}/engine.json"
    elif [n["t"] for n in e["nodes"]] != [n["t"] for n in b["nodes"]]:
        why = "engine.json 的节点与本卷对不上"
    elif e["meta"].get("input") != DA.fingerprint(slug, b):
        why = "engine.json 不是按当前的归属算的（归属点、节点归属、引擎参数或外缘改过）"
    if why:
        if strict:
            sys.exit(f"{slug}：{why}，先运行 python run.py {slug} 重算疆域")
        log(f"    {slug}：{why}；这一遍先用 legacy.html 的几何")
        return None

    old_pool, pool, seen = b["geom"], [], {}

    def put(rr):
        k = json.dumps(rr, separators=(",", ":"))
        if k not in seen:
            seen[k] = len(pool); pool.append(rr)
        return seen[k]

    J = {mine: (owner, theirs) for mine, owner, theirs in junction_nodes(slug, b)}
    notes = []
    for i, (n, en) in enumerate(zip(b["nodes"], e["nodes"])):
        owner, theirs = J.get(i, (None, None))
        if owner and not migrated(owner):                    # 对方为准、还没换：整节点保留旧几何
            n["u"] = {k: put(old_pool[g]) for k, g in n["u"].items()}
            n["pu"] = {k: put(old_pool[g]) for k, g in n.get("pu", {}).items()}
            notes.append(f"{n['t'] // 12} 年衔接节点保留旧几何（{owner} 为准，尚未换到引擎）")
            continue
        if owner:                                             # 对方为准、也已换：范围内照搬对方
            geoms, on, oe = merge_node(b, i, e, owner, theirs)
            u, ul = {}, {}
            for k, (g, a_in, a_out) in geoms.items():
                rr = rings_of(g)
                if not rr:
                    continue
                u[k] = put(rr)
                okey = next((ou for ou, kk in oe["meta"]["keys"].items()
                             if b["polities"][int(k)]["key"] == kk), None)
                L = on["ul"].get(okey) if a_in >= a_out and okey is not None else en["ul"].get(k)
                L = L or en["ul"].get(k) or (on["ul"].get(okey) if okey else None)
                if L:
                    ul[k] = L
            pu, pul = {}, {}
            members = {}
            for k, p in n["pol"].items():
                if k in geoms:
                    members.setdefault(str(p), []).append(k)
            import shapely
            for p, ks in sorted(members.items()):
                if len(ks) < 2 and ks[0] == p:
                    continue
                g = polys(shapely.union_all([geoms[k][0] for k in ks]))
                rr = rings_of(g)
                if rr:
                    pu[p] = put(rr)
                    big = max(ks, key=lambda k: geoms[k][0].area)
                    if big in ul:
                        pul[p] = ul[big]
            n["u"], n["ul"], n["pu"], n["pul"] = u, ul, pu, pul
            notes.append(f"{n['t'] // 12} 年衔接节点在{owner}的推算范围内照搬其引擎几何")
            continue
        n["u"] = {k: put(e["geom"][g]) for k, g in en["u"].items()}
        n["ul"] = dict(en["ul"])
        n["pu"] = {k: put(e["geom"][g]) for k, g in en["pu"].items()}
        n["pul"] = dict(en["pul"])
    b["geom"] = pool
    return "疆域：统一引擎（eras/" + slug + "/engine.json）" + ("；" + "；".join(notes) if notes else "")
