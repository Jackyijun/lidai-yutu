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
  - 对方是准、对方也已换到引擎：在对方的推算范围（手绘外缘，或可达代价卷的 box 减 EXCLUDE）以内照搬对方引擎的几何，
    范围以外用本卷的，跨线的同一单位两部分合并；对方的几何先裁到本卷自己的推算范围，
    本卷范围以外对方才有的单位不照搬。对方的单位依次按同键、同全局 ID（global/polities.jsonl）、
    所属政权（对方政权层几何过半落在哪个本卷单位）对上本卷的单位，对不上的那块用本卷自己的几何；
  - 对方是准、还没换到引擎：这个节点整个保留 legacy.html 里的几何（旧构建本来就照搬了对方）。

区划界（汉末卷的州界，节点 ext 的 zb / zl）：引擎按 era.toml [engine] 的 zones 分块时一并换成引擎的，否则照旧。

重要地域（唐宋、宋元的燕云十六州，base.regions）：范围线、分区之间的分界线与分区注记，连同地域条目的注记位置
（lab / anc），换成引擎按地域起始年那个节点的分区描的（engine.json 的 regions）。

春秋、战国：春秋共主着色的「周天下」就是政权层「周」（pu），同其他卷一并换；战国卷的秦郡界（ext j）取引擎按郡治
细分秦的各块（[engine] sub，结果里的 zp）。以战国卷为准的秦汉卷前212 节点由秦汉卷自己的构建照搬
（eras/qinhan/src/build.py 的 zg_engine_212）。
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


def gid_of():
    """全局政权表的引用 → 全局 ID，{"卷:单位键": ID}（取 global/polities.jsonl，即上一次生成的全局表；同一政权各卷键不同时靠它对上）"""
    out = {}
    for line in (ROOT / "global" / "polities.jsonl").read_text(encoding="utf8").splitlines():
        if line.strip():
            d = json.loads(line)
            for r in d.get("refs", []):
                out[r] = d["id"]
    return out


def region_of(slug):
    """一卷的推算范围（经纬度多边形）：手绘外缘（outer = "frontier"），或按可达代价定外缘的卷的 box 减去 EXCLUDE（outer = "reach"）"""
    import shapely
    import data as DA
    sp = DA.spec(slug)
    if sp.get("outer") == "frontier":
        return shapely.Polygon(DA.frontier(slug)).buffer(0)
    if sp.get("outer") in ("reach", "box"):
        return DA.region(slug, sp)
    sys.exit(f"{slug}：era.toml 的 [engine] 没写 outer，算不出推算范围")


def merge_node(slug, b, mine, eng_mine, owner, theirs):
    """衔接节点：对方范围以内照搬对方引擎的几何，以外用本卷引擎的。返回本卷单位序号 → shapely"""
    import shapely
    oe = load(owner)
    R = region_of(owner)
    R_in = R.buffer(-PAD_IN)
    M = region_of(slug)                                  # 本卷自己的推算范围：对方的几何只取这里面的
    on = oe["nodes"][theirs]
    okeys = oe["meta"]["keys"]
    idx = {p["key"]: str(i) for i, p in enumerate(b["polities"])}
    G = gid_of()
    by_gid = {G[f"{slug}:{p['key']}"]: str(i) for i, p in enumerate(b["polities"]) if f"{slug}:{p['key']}" in G}
    ogid = {k: G.get(f"{owner}:{k}") for k in okeys.values()}
    PU = {p: shape_of(oe["geom"][g]) for p, g in on.get("pu", {}).items()}   # 对方多单位政权的合并疆域

    def okey_all():
        """对方 v1 的单位表（序号 → 键）；引擎结果只记了画出来的单位，多单位政权本身的键要从这里取"""
        f = ROOT / "build" / "v1" / f"{owner}.json"
        if not f.exists():
            sys.exit(f"衔接节点：缺 build/v1/{owner}.json，先构建 {owner}")
        return [p["key"] for p in json.loads(f.read_text(encoding="utf8"))["polities"]]

    def pol_of(u, a):
        """对方单位 u 所属的政权（取包含它最多的合并疆域），无则 None"""
        best = max(PU.items(), key=lambda kv: kv[1].intersection(a).area, default=(None, None))
        return best[0] if best[0] is not None and best[1].intersection(a).area > 0.5 * a.area else None

    A, lost = {}, []
    for u, g in on["u"].items():
        k = okeys[u]
        a = polys(shape_of(oe["geom"][g]).intersection(M))
        if a.is_empty:
            continue                                     # 整个在本卷范围以外（如宋元卷的欧洲诸国）
        # 对上本卷的单位：同键 → 全局表里是同一政权（宋元卷的西夏 = 唐宋卷的定难）→ 所属政权对上本卷的单位
        # （宋元卷宋的各路 = 唐宋卷的宋，辽的各道与乌古敌烈 = 唐宋卷的契丹）
        mine_k = idx.get(k) or by_gid.get(ogid.get(k))
        if mine_k is None:
            p = pol_of(u, a)
            if p is not None:
                pk = okeys.get(p) or okey_all()[int(p)]
                mine_k = idx.get(pk) or by_gid.get(G.get(f"{owner}:{pk}"))
        if mine_k is None:
            lost.append(a)                               # 本卷没有对应的单位（如宋元卷伸到 72°E 以东的萨曼）：这里用本卷自己的几何
            continue
        A[mine_k] = polys(A[mine_k].union(a)) if mine_k in A else a
    A_all = shapely.union_all(list(A.values()))
    if lost:
        R_in = R_in.difference(shapely.union_all(lost))
    B = {u: shape_of(eng_mine["geom"][g]) for u, g in eng_mine["nodes"][mine]["u"].items()}
    out = {}
    for u in sorted(set(A) | set(B), key=lambda x: (len(x), x)):
        inside = A.get(u, shapely.Polygon())
        # 对方有的单位：范围以内只用对方的；对方没有的单位（对方留白处，如汉末卷 280 年没画的天竺、扶南、倭）照本卷画
        outside = (B[u].difference(A_all).difference(R_in) if u in A else B[u].difference(A_all)) if u in B else shapely.Polygon()
        g = polys(inside.union(outside))
        if not g.is_empty:
            out[u] = (g, inside.area, outside.area)
    return out, on, oe, ogid


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
        keep = owner and (not migrated(owner) or not path_of(owner).exists())
        ext = n.get("ext") or {}
        if "zb" in ext:                                       # 区划界（汉末卷的州界）：引擎有就换，没有照旧（序号换到新的几何池）
            if "zb" in en and not keep:
                ext["zb"], ext["zl"] = put(e["geom"][en["zb"]]), en["zl"]
            else:
                ext["zb"] = put(old_pool[ext["zb"]])
        if keep:                                              # 对方为准、还没换（或还没算出 engine.json）：整节点保留旧几何
            n["u"] = {k: put(old_pool[g]) for k, g in n["u"].items()}
            n["pu"] = {k: put(old_pool[g]) for k, g in n.get("pu", {}).items()}
            notes.append(f"{n['t'] // 12} 年衔接节点保留旧几何（{owner} 为准，尚未换到引擎）")
            continue
        if owner:                                             # 对方为准、也已换：范围内照搬对方
            geoms, on, oe, ogid = merge_node(slug, b, i, e, owner, theirs)
            u, ul = {}, {}
            for k, (g, a_in, a_out) in geoms.items():
                rr = rings_of(g)
                if not rr:
                    continue
                u[k] = put(rr)
                me = b["polities"][int(k)]
                okey = next((ou for ou, kk in oe["meta"]["keys"].items() if me["key"] == kk), None) \
                    or next((ou for ou, kk in oe["meta"]["keys"].items()
                             if ogid.get(kk) and ogid.get(kk) == gid_of().get(f"{slug}:{me['key']}")), None)
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
        if "j" in ext:                                        # 秦郡（战国卷）：引擎按郡治细分秦的各块（zp）；环直接写在节点里
            ext["j"] = {k: e["geom"][g] for k, g in en.get("zp", {}).items()}
    RB, RE = (b.get("base") or {}).get("regions", []), e.get("regions", [])
    if len(RB) != len(RE) or any(len(R["groups"]) != len(E["groups"]) for R, E in zip(RB, RE)):
        sys.exit(f"{slug}：engine.json 的重要地域与本卷对不上，先运行 python run.py {slug} 重算疆域")
    byi = {it["i"]: it for it in b["items"]}
    for R, E in zip(RB, RE):                                  # 重要地域（燕云十六州）：范围线、分界线与注记换成引擎的
        R["rings"] = E["rings"]
        for g, eg in zip(R["groups"], E["groups"]):
            g["lab"], g["lines"] = eg["lab"], eg["lines"]
        it = byi[R["it"]]
        it["lab"], it["anc"] = E["lab"], E["lab"][:2]
    b["geom"] = pool
    return "疆域：统一引擎（eras/" + slug + "/engine.json）" + ("；" + "；".join(notes) if notes else "")
