# -*- coding: utf-8 -*-
"""各卷的页面疆域由统一疆域引擎出（core/engine/，第 7 步起）。

era.toml 的 [engine] 写 geometry = "engine" 的卷（秦汉以外的八卷），生成 v1 时把疆域（各节点 u / ul / pu / pul，
战国卷的秦郡 ext j、汉末卷的州界 ext zb / zl，唐宋、宋元的重要地域）填成 eras/<短名>/engine.json——那是
core/engine/build.py 的结果，入库，所以 python run.py --web 不必重算疆域，结果也与库版本无关。归属、文字、条目取
各卷第 1 段的 source.json，那里面没有疆域（架构整理第三批起；此前取 legacy.html，换掉旧构建画的几何）。

engine.json 记着引擎输入的指纹（core/engine/data.py 的 fingerprint）。归属点或节点归属改了、指纹对不上时：
  strict = True（默认）  停下，提示先运行 python run.py <短名> 重算；
  strict = False         这一遍不带疆域并提示（run.py 在重算之前先出一遍 v1 给引擎读时用）。

衔接节点（global/junctions.toml 里 shared 的一年）：
  - 本卷是准的一方：照用本卷引擎的结果；
  - 对方是准：在对方的推算范围（手绘外缘，或可达代价卷的 box 减 exclude）以内照搬对方引擎的几何，
    范围以外用本卷的，跨线的同一单位两部分合并；对方的几何先裁到本卷自己的推算范围，
    本卷范围以外对方才有的单位不照搬。对方的单位依次按同键、同全局 ID（global/polities.jsonl）、
    所属政权（对方政权层几何过半落在哪个本卷单位）对上本卷的单位，对不上的那块用本卷自己的几何；
    对方的 engine.json 缺了时（engine.json 入库，一般不会缺）：strict 停下，否则这一遍先用本卷自己的。

衔接节点的归属对齐（align_own，架构整理第四批）：对方为准的衔接节点上，疆域在对方的推算范围以内是照搬来的，
  本卷各点自己记的归属可能与画出来的对不上。生成 v1 时，范围以内（含边上）的点一律改归画出来包含它的单位；不在任何
  一块里、离某块不到 0.01° 的（压在界线上）取最近的一块，本卷原来的单位也是最近的就不改；落在两块重叠的碎片里也先取
  原来的单位；离各块都超过 0.01° 的（落在空白处）不归任何单位。本卷原来的归属另存在节点的 own_src（对齐改了点才有），
  统一引擎读的是 own_src（core/engine/data.py 的 view），所以引擎的输入与指纹不变。秦汉卷的两头衔接疆域由它自己的构建
  照搬，同样在这里对齐。衔接节点是本卷的首节点或末节点，年份须与 global/junctions.toml 记的一致，否则停下。

区划界（汉末卷的州界，节点 ext 的 zb / zl）：引擎按 era.toml [engine] 的 zones 分块时出。

春秋、战国：春秋共主着色的「周天下」就是政权层「周」（pu），同其他卷一并换；战国卷的秦郡界（ext j）取引擎按郡治
细分秦的各块（[engine] sub，结果里的 zp）。以战国卷为准的秦汉卷前212 节点由秦汉卷自己的构建照搬
（eras/qinhan/src/build.py 的 zg_engine_212）。

重要地域（唐宋、宋元的燕云十六州，base.regions）：范围线、分区之间的分界线与分区注记，连同地域条目的注记位置
（lab / anc），换成引擎按地域起始年那个节点的分区描的（engine.json 的 regions）。各键插在旧格式原来的位置，页面里的次序不变。
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
        if b["nodes"][mine]["t"] // 12 != j["year"]:
            sys.exit(f"{slug}：global/junctions.toml 记着与{j['owner']}在 {j['year']} 年共用节点，本卷{'末' if mine else '首'}节点却是 "
                     f"{b['nodes'][mine]['t'] // 12} 年")
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
    """一卷的推算范围（经纬度多边形）：手绘外缘（outer = "frontier"），或按可达代价定外缘的卷的 box 减去 exclude（outer = "reach"）"""
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

    keys_all = []

    def okey_all():
        """对方的单位表（序号 → 键）；引擎结果只记了画出来的单位，多单位政权本身的键要从这里取。
        由对方的 source.json 转出（与它 v1 的政权次序相同），不靠 build/v1：全新克隆第一次构建时那里还是空的"""
        if not keys_all:
            import legacy
            keys_all.extend(p["key"] for p in legacy.bundle_of(owner)["polities"])
        return keys_all

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


SNAP = 0.01           # 归属对齐：不在任何单位里、离某块不到 0.01°（页面的坐标精度）的点归最近的一块（原来的单位也最近就不改）


def align_own(slug, b):
    """对方为准的衔接节点：对方推算范围以内的点，归属改成画出来包含它的单位（见文首）。
    节点还没有疆域（--lenient 那一遍引擎结果过期、秦汉卷第一遍）就不动。返回记进 meta.overlay 的一句话，没改则 None"""
    import shapely
    notes = []
    for mine, owner, _ in junction_nodes(slug, b):
        n = b["nodes"][mine]
        if not n.get("u"):
            continue
        R = region_of(owner)
        keys = sorted(n["u"], key=lambda k: (len(k), k))
        shapes = [shape_of(b["geom"][n["u"][k]]) for k in keys]
        tree = shapely.STRtree(shapes)
        src = n.get("own_src", n["own"])                 # 再对齐一遍（已有 own_src）时从本卷原来的归属算起
        src_n = [-1 if v is None else v for v in src]    # v1 的 own 不归任何单位记 -1
        new = list(src_n)
        both = []
        for i, p in enumerate(b["places"]):
            pt = shapely.Point(p["lon"], p["lat"])
            if not R.covers(pt):                         # 压在推算范围边上的也算在内
                continue
            hit = sorted(tree.query(pt, predicate="within"))
            if not hit:                                  # 压在界线上或贴着界线：本卷原来的单位在最近的几块里就不改，否则取最近的
                near = sorted((shapes[j].distance(pt), j) for j in tree.query(pt.buffer(SNAP)) if shapes[j].distance(pt) <= SNAP)
                hit = [j for d, j in near if d <= near[0][0] + 1e-9] if near else []
            elif len(hit) > 1:                           # 落在两块重叠的碎片里（环按 0.01° 取整后偶有）：同样先取原来的单位
                both.append(p["key"])
            hit = [j for j in hit if keys[j] == str(src_n[i])] or hit[:1]
            new[i] = int(keys[hit[0]]) if hit else -1
        changed = sum(a != c for a, c in zip(src_n, new))
        miss = sorted({b["polities"][v]["key"] for v in new if v >= 0 and str(v) not in n["pol"]})
        if miss:
            sys.exit(f"{slug}：{n['t'] // 12} 年衔接节点对齐后有点归到节点政权表里没有的单位：" + "、".join(miss))
        if changed:
            n["own_src"] = list(src)
            n["own"] = new
            notes.append(f"{n['t'] // 12} 年衔接节点 {changed} 个点的归属按{era_toml(owner)['short']}卷照搬来的疆域对齐"
                         + (f"（{'、'.join(both)} 落在两块重叠处）" if both else ""))
        elif "own_src" in n:
            n["own"] = n.pop("own_src")
    return "；".join(notes) or None


def align_retired(slug, b):
    """era.toml [engine] 写 align_retired = true 的卷（隋唐卷 670 年起改用唐宋卷的归属点）：已退出分区的点（v1 地点的 t1 已过）
    不再决定疆域，它们在各节点的归属改成画出来包含它的单位（规则同 align_own）；对齐以后不再领有任何点、也没有疆域的单位
    （670 年起的附国，745 年起的单于、安北、安东等）从节点的政权表里去掉，免得图例里有名无地。
    对方为准的衔接节点上的点已由 align_own 对齐，这里只去掉有名无地的单位。原归属存在 own_src，引擎的输入与指纹不变。
    返回记进 meta.overlay 的一句话，没改则 None"""
    if not era_toml(slug).get("engine", {}).get("align_retired"):
        return None
    import shapely
    shared = {m for m, _, _ in junction_nodes(slug, b)}
    moved, dropped = 0, set()
    for j, n in enumerate(b["nodes"]):
        if not n.get("u"):
            continue
        idle = [i for i, p in enumerate(b["places"]) if p.get("t1") is not None and n["t"] > p["t1"]]
        if not idle:
            continue
        if j not in shared:
            keys = sorted(n["u"], key=lambda k: (len(k), k))
            shapes = [shape_of(b["geom"][n["u"][k]]) for k in keys]
            tree = shapely.STRtree(shapes)
            src = n.get("own_src", n["own"])
            src_n = [-1 if v is None else v for v in src]
            new = list(src_n)
            for i in idle:
                p = b["places"][i]
                pt = shapely.Point(p["lon"], p["lat"])
                hit = sorted(tree.query(pt, predicate="within"))
                if not hit:
                    near = sorted((shapes[q].distance(pt), q) for q in tree.query(pt.buffer(SNAP)) if shapes[q].distance(pt) <= SNAP)
                    hit = [q for d, q in near if d <= near[0][0] + 1e-9] if near else []
                hit = [q for q in hit if keys[q] == str(src_n[i])] or hit[:1]
                new[i] = int(keys[hit[0]]) if hit else -1
            ch = sum(a != c for a, c in zip(src_n, new))
            if ch:
                n["own_src"] = list(src)
                n["own"] = new
                moved += ch
        live = {v for v in n["own"] if v is not None and v >= 0}
        parents = {str(v) for k, v in n["pol"].items() if k != str(v)}
        gone = [k for k in n["pol"] if int(k) not in live and k not in n["u"] and k not in n.get("pu", {}) and k not in parents]
        if gone and "pol_src" not in n:
            n["pol_src"] = dict(n["pol"])                # 引擎读原来的政权表（core/engine/data.py 的 view），指纹不变
        for k in gone:
            n["pol"].pop(k, None)
            n.get("lab", {}).pop(k, None)
            n.get("seat", {}).pop(k, None)
            if "h" in n:
                n["h"] = [u for u in n["h"] if str(u) != k]
            for d in (n.get("en", {}).get("lab", {}),):
                d.pop(k, None)
            dropped.add(b["polities"][int(k)]["key"])
    if not moved and not dropped:
        return None
    return (f"670 年起退出分区的点按各节点画出来的疆域对齐归属（共 {moved} 个点次）" +
            (f"；有名无地的单位从节点里去掉：{'、'.join(sorted(dropped))}" if dropped else ""))


# ---------------- 换几何 ----------------
def put_after(d, after, kv):
    """把 kv 的各键写进 d、放在 after 键之后（after 不在 d 里就放在最后），其余键的次序不变：
    source.json 里没有这些几何键，补上后与旧格式的次序一致，页面逐字节不变"""
    out = {}
    for k, v in d.items():
        if k in kv:
            continue
        out[k] = v
        if k == after:
            out.update(kv)
    if after not in d:
        out.update(kv)
    d.clear()
    d.update(out)


def apply(slug, b, strict=True, log=print):
    """把 b（v1 数据包，由 source.json 转出）的疆域填成引擎的。返回记进 meta.overlay 的一句话；本卷不由引擎出几何（秦汉卷）则 None"""
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
        log(f"    {slug}：{why}；这一遍先不带疆域")
        return None

    pool, seen = [], {}

    def put(rr):
        k = json.dumps(rr, separators=(",", ":"))
        if k not in seen:
            seen[k] = len(pool); pool.append(rr)
        return seen[k]

    J = {mine: (owner, theirs) for mine, owner, theirs in junction_nodes(slug, b)}
    notes = []
    for i, (n, en) in enumerate(zip(b["nodes"], e["nodes"])):
        owner, theirs = J.get(i, (None, None))
        if owner and not (migrated(owner) and path_of(owner).exists()):
            if strict:
                sys.exit(f"{slug}：{n['t'] // 12} 年衔接节点以{owner}为准，缺 eras/{owner}/engine.json，先运行 python run.py {owner}")
            log(f"    {slug}：{n['t'] // 12} 年衔接节点以{owner}为准，{owner}还没有 engine.json，这一遍先用本卷的")
            owner = None
        if "zb" in en:                                        # 区划界（汉末卷的州界）
            ext = n.setdefault("ext", {})
            ext["zb"], ext["zl"] = put(e["geom"][en["zb"]]), en["zl"]
        if owner:                                             # 对方为准：范围内照搬对方
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
        ext = n.get("ext") or {}
        if "j" in ext:                                        # 秦郡（战国卷）：引擎按郡治细分秦的各块（zp）；环直接写在节点里
            ext["j"] = {k: e["geom"][g] for k, g in en.get("zp", {}).items()}
    RB, RE = (b.get("base") or {}).get("regions", []), e.get("regions", [])
    if len(RB) != len(RE) or any(len(R["groups"]) != len(E["groups"]) for R, E in zip(RB, RE)):
        sys.exit(f"{slug}：engine.json 的重要地域与本卷对不上，先运行 python run.py {slug} 重算疆域")
    byi = {it["i"]: it for it in b["items"]}
    for R, E in zip(RB, RE):                                  # 重要地域（燕云十六州）：范围线、分界线与注记换成引擎的
        put_after(R, "y1" if "y1" in R else "y0", {"rings": E["rings"]})
        for g, eg in zip(R["groups"], E["groups"]):
            put_after(g, "y0", {"lab": eg["lab"], "lines": eg["lines"]})
        put_after(byi[R["it"]], "members", {"anc": E["lab"][:2], "lab": E["lab"]})
    b["geom"] = pool
    return "疆域：统一引擎（eras/" + slug + "/engine.json）" + ("；" + "；".join(notes) if notes else "")
