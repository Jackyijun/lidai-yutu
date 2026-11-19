# -*- coding: utf-8 -*-
"""秦汉形势图：史料 → 旧格式 GEO / DATA（build/geo.json、data.json、colors.json）。

  python src/build.py          有 build/engine/qinhan.json（统一引擎的推算结果）就填入疆域，没有则只出归属、不出疆域

疆域不在这里算。构建分两遍（见 run.py）：第一遍出归属 → 由 core/v1 转成 v1 数据包 → core/engine/build.py qinhan
推算疆域 → 第二遍把疆域填进来。首尾两个节点照搬邻卷：前212 取战国卷末节点的秦疆与秦郡郡界，184 取汉末卷首节点的疆域，
本卷推算出的郡国裁进照搬来的外廓里。时间一律是月序号 t = 年 × 12 + 月 − 1（年按夏正，见 README「纪年」）。
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import shapely
from shapely.geometry import Point, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402
sys.path.insert(0, str(C.REPO / "core" / "v1"))
import legacy  # noqa: E402
sys.path.insert(0, str(C.ROOT))
sys.path.insert(0, str(C.CONTENT))
import jun as J, seeds as SD, units as UN, nodes as ND, items as IT, en_names as EN  # noqa: E402,E401

INF = -10 ** 6


# ================================================================ 工具
def dec(f):
    x = y = 0
    out = []
    for i in range(0, len(f), 2):
        x += f[i]; y += f[i + 1]
        out.append((x / 100, y / 100))
    return out


def enc(pts):
    out, lx, ly, prev = [], 0, 0, None
    for a, b in pts:
        x, y = int(round(a * 100)), int(round(b * 100))
        if (x, y) == prev:
            continue
        out += [x, y] if prev is None else [x - lx, y - ly]
        lx, ly, prev = x, y, (x, y)
    return out


def geom_of(rings):
    """旧格式的环组（奇偶填充）→ shapely 多边形"""
    g = None
    for r in rings:
        p = shapely.make_valid(Polygon(dec(r)))
        p = shapely.union_all(polys_of(p)) if p.geom_type == "GeometryCollection" else p
        g = p if g is None else g.symmetric_difference(p)
    if g is None:
        return Polygon()
    return shapely.union_all(polys_of(g)) if g.geom_type == "GeometryCollection" else g


def polys_of(g):
    """拆到单个多边形为止（make_valid 可能给出嵌套的集合）"""
    out, stack = [], [g]
    while stack:
        x = stack.pop()
        if x.geom_type == "Polygon":
            out.append(x)
        elif x.geom_type in ("MultiPolygon", "GeometryCollection"):
            stack.extend(shapely.get_parts(x))
    return out


def rings_of(g, min_area=0.004):
    out = []
    for p in polys_of(g):
        if p.area < min_area:
            continue
        for r in [p.exterior] + list(p.interiors):
            if Polygon(r).area < min_area:
                continue
            e = enc(list(r.coords))
            if len(e) >= 8:
                out.append(e)
    return out


def tl_at(tl, t):
    """沿革 [(年, 值)] 在月序号 t 时的值；年按夏正年的正月起算"""
    v = None
    for y, val in tl:
        if y == INF or t >= y * 12:
            v = val
    return v


def yr_label(t, tp="y"):
    """月序号 → 显示用的（纪年年, 月）：太初（前104）以前十月至十二月记在下一年（以十月为岁首）"""
    y, m = t // 12, t % 12 + 1
    if y < C.TAICHU and m >= 10:
        y += 1
    return y, m


def label_t(y, m):
    """纪年年 + 月 → 月序号（yr_label 的反函数）"""
    if y <= C.TAICHU and m >= 10:
        y -= 1
    return y * 12 + m - 1


def ytxt(y, en=False):
    if en:
        return f"{-y} BC" if y < 0 else f"AD {y}" if y < 100 else str(y)
    return f"前{-y}" if y < 0 else str(y)


# ================================================================ 邻卷
def legacy_of(slug):
    return legacy.extract((C.REPO / "eras" / slug / "legacy.html").read_text(encoding="utf8"))


ZG = legacy_of("zhanguo")
HM = legacy_of("hanmosanguo")
ZG_LAST = ZG[0]["snaps"][-1]
ZG_JUN = {it["k"]: it for it in ZG[1]["items"] if it["c"] == "jun"}
# 秦郡治所的坐标与战国卷同名城邑条目不符的，取城邑条目（同地同坐标）
QIN_SEAT_LL = {"肤施": (109.8, 38.0)}     # 战国卷秦郡表记在米脂一带，城邑条目 zhanguo:i:161 在榆林东南
QIN_POLY = {J.qin_unit(k): geom_of(r) for k, r in ZG_LAST["j"].items()}
HM_184 = next(s for s in HM[0]["snaps"] if s["y"] == 184)


def hm_engine_184():
    """汉末卷已换到统一引擎（第 7 步）时，184 节点的疆域改取它的 eras/hanmosanguo/engine.json，与汉末卷新页面一致；
    归属、文字仍取 legacy.html。engine.json 里的单位按单位键对回 legacy.html 的序号"""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    hm = C.REPO / "eras" / "hanmosanguo"
    if tomllib.loads((hm / "era.toml").read_text(encoding="utf8")).get("engine", {}).get("geometry") != "engine":
        return
    e = json.loads((hm / "engine.json").read_text(encoding="utf8"))
    en = next(n for n in e["nodes"] if n["t"] // 12 == 184)
    idx = {u["k"]: str(i) for i, u in enumerate(HM[1]["units"])}
    key = e["meta"]["keys"]
    HM_184["z"] = {idx[key[k]]: e["geom"][g] for k, g in en["u"].items()}
    HM_184["p"] = {idx[key[k]]: e["geom"][g] for k, g in en["pu"].items()}


hm_engine_184()


def hm_rings(v):
    return HM[0]["pool"][v] if isinstance(v, int) else v


# ================================================================ 归属点
def load_seeds():
    import importlib.util
    p = C.REPO / "eras" / "hanmosanguo" / "content" / "seeds.py"
    spec = importlib.util.spec_from_file_location("hm_seeds", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    hm_en = {s["id"]: s for s in HM[1]["seeds"]}
    out = []
    for s in m.SEEDS:
        if s["id"] in SD.DROP:
            continue
        d = s["id"] if s["t"] == "z" else s["j"]
        e = hm_en.get(s["id"], {})
        # 名字照汉末卷成品：郡治点写治所城名（东郡 → 濮阳），与英文 ne 一致
        # 按语不照搬：汉末卷的按语多写 184 年以后的事、东汉的治所，放在本卷会错位
        o = dict(id=s["id"], n=e.get("n") or s["n"], t=s["t"], lon=s["lon"], lat=s["lat"], mod=s["mod"], note="", dj=d)
        for k in ("ne", "mode"):
            if e.get(k):
                o[k] = e[k]
        out.append(o)
    have = {s["id"] for s in out}
    for s in SD.NEW:
        if s["id"] in have:
            sys.exit(f"归属点重名：{s['id']}")
        o = dict(id=s["id"], n=s["n"], t=s["t"], lon=s["lon"], lat=s["lat"], mod=s["mod"], note="", dj=None)
        if s.get("ne"): o["ne"] = s["ne"]
        if s.get("mode"): o["mode"] = s["mode"]
        out.append(o)
    # 秦郡治所（只参与分区）
    for k, it in ZG_JUN.items():
        lon, lat = QIN_SEAT_LL.get(it["zhi"], (float(it["lon"]), float(it["lat"])))
        if any(abs(s["lon"] - lon) < .12 and abs(s["lat"] - lat) < .12 for s in out):
            continue
        out.append(dict(id=f"秦·{it['zhi']}", n=it["zhi"], t="r", lon=lon, lat=lat, mod="", note="", dj=None, qj=J.qin_unit(k)))
    unknown = [k for k in list(SD.TL) + list(SD.XO) + list(SD.DO) + list(SD.QO) if k not in {s["id"] for s in out}]
    if unknown:
        sys.exit("沿革里写了不存在的点：" + "、".join(unknown))
    for s in out:
        s["tl"] = SD.TL.get(s["id"], [(INF, "@")])
        if s["id"] in SD.DO:
            s["dj"] = SD.DO[s["id"]]
        x = SD.XO.get(s["id"])
        if x is None and s["dj"]:
            x = J.XH_OF_DH.get(s["dj"], s["dj"])
        s["xj"] = x if isinstance(x, list) else ([(INF, x)] if x else None)
        if s["id"] in SD.QO:
            s["qj"] = SD.QO[s["id"]]
        elif "qj" not in s:
            P = Point(s["lon"], s["lat"])
            s["qj"] = next((k for k, g in QIN_POLY.items() if g.contains(P)), None)
    # 某套郡制下没有归属的点，取最近的有归属的点
    for key in ("qj", "xj", "dj"):
        have = [s for s in out if s[key]]
        for s in out:
            if not s[key]:
                nb = min(have, key=lambda o: (o["lon"] - s["lon"]) ** 2 + (o["lat"] - s["lat"]) ** 2)
                s[key] = nb[key]
                s["_near_" + key] = nb["id"]
    return out


SEEDS = load_seeds()
SI = {s["id"]: i for i, s in enumerate(SEEDS)}


def jun_at(s, node):
    sys_ = node["sys"]
    if sys_ == "Q":
        return s["qj"]
    if sys_ == "X":
        return tl_at(s["xj"], node["t"])
    return s["dj"]


# ================================================================ 单位
UNITS = UN.units()                       # 政权、部族
UK = {u["k"]: i for i, u in enumerate(UNITS)}


def add_unit(k, kind="zhen", **kw):
    if k in UK:
        return UK[k]
    UK[k] = len(UNITS)
    UNITS.append(dict(k=k, n=kw.get("n", k), kind=kind, note=kw.get("note", ""), ne=kw.get("ne", EN.name(k)),
                      notee=kw.get("notee", ""), col=kw.get("col")))
    return UK[k]


def jun_note(k):
    """郡国的说明：治所"""
    if k in J.XIHAN or k in J.XIHAN_EXTRA:
        seat, _, _, se = (J.XIHAN.get(k) or J.XIHAN_EXTRA[k])
        return f"治{seat}。", f"Seat at {se}."
    if k in {J.qin_unit(q) for q in ZG_JUN}:
        it = next(it for q, it in ZG_JUN.items() if J.qin_unit(q) == k)
        return it["note"] + ("" if it["note"].endswith("。") else "。") + f"治{it['zhi']}。", (it.get("enote") or "") + f" Seat at {it.get('ezhi', '')}."
    if k in DH_SEAT:                      # 汉末卷的点名就是郡国名的，治所按《续汉书·郡国志》补
        seat, se = DH_SEAT[k]
        return (f"治{seat}。", f"Seat at {se}.") if seat else ("", "")
    hm = next((s for s in SEEDS if s["id"] == k and s["t"] == "z"), None)
    if hm:
        return f"治{hm['n']}。", f"Seat at {hm.get('ne', EN.name(hm['n']))}."
    return "", ""


DH_SEAT = {"清河国": ("甘陵", "Ganling"), "任城国": ("任城", "Rencheng"), "牂牁郡": ("故且兰", "Guqielan"),
           "越巂郡": ("邛都", "Qiongdu"), "辽东属国": ("昌辽", "Changliao"), "沛国": ("相", "Xiang"),
           "乐安国": ("临济", "Linji"), "北海国": ("剧", "Ju"), "居延属国": ("居延", "Juyan"),
           "永昌郡": ("不韦", "Buwei"), "张掖属国": ("", "")}


# ================================================================ 节点
def junction_text():
    """首尾节点的文字照搬邻卷"""
    import csv
    first, last = ND.NODES[0], ND.NODES[-1]
    z = ZG_LAST
    first.update(title=z["t"], desc=z["d"], title_en=z["te"], desc_en=z["de"], short=z["sh"], short_en=z["she"])
    h = HM_184
    last.update(era=h["era"], era_en=h["erae"], title=h["t"], desc=h["d"], title_en=h["te"], desc_en=h["de"])
    with open(C.REPO / "eras" / "hanmosanguo" / "short.tsv", encoding="utf8") as f:
        for r in csv.DictReader((l for l in f if not l.startswith("#")), delimiter="\t"):
            if r["节点"].strip() == "184":
                last.update(short=r["短标题"].strip(), short_en=r["英文"].strip())


junction_text()


def node_rows():
    rows = []
    for nd in ND.NODES:
        own, pol, lab, labe, seat = [None] * len(SEEDS), {}, {}, {}, {}
        grp = {}                                   # 郡 → (单位, 政权)
        for u, p, members in nd["groups"]:
            for m in members:
                grp[m] = (u, p)
        for i, s in enumerate(SEEDS):
            o = nd["ext"].get(s["id"], tl_at(s["tl"], nd["t"]))
            if o is None or o == "·":
                continue
            if o == "@":
                j = jun_at(s, nd)
                pr = nd["pred"](s) if nd.get("pred") else None
                u, p = pr if pr else grp.get(j, (j, nd["cent"]))
                if p is None:
                    continue
            else:
                u, p = o, nd["polmap"].get(o, UN.SUB.get(o, o))
            own[i] = u
            pol[u] = p
        for u in dict.fromkeys(pol.values()):          # 保持先后次序（集合的次序随哈希种子变，成品就不可复现）
            pol.setdefault(u, u)
        rows.append(dict(nd=nd, own=own, pol=pol))
    return rows


# ================================================================ 疆域（统一引擎的结果）
def engine_geoms():
    p = C.REPO / "build" / "engine" / "qinhan.json"
    if not p.exists():
        return None
    e = json.loads(p.read_text(encoding="utf8"))
    return e


def fill_gaps(units, outline, others=()):
    """把 units（键 → 多边形）裁进 outline，outline 里没被覆盖的部分并给共边最长的单位"""
    out = {k: g.intersection(outline) for k, g in units.items()}
    out = {k: g for k, g in out.items() if not g.is_empty and g.area > 1e-4}
    cov = shapely.union_all(list(out.values())) if out else Polygon()
    gap = outline.difference(cov)
    for part in shapely.get_parts(gap):
        if part.area < 1e-5 or not out:
            continue
        best = max(out, key=lambda k: part.buffer(0.02).intersection(out[k]).area)
        out[best] = out[best].union(part)
    return out


def junction(i, row, z, lz, p, lp):
    """首尾节点照搬邻卷：返回改过的 z / p（单位序号 → 多边形）"""
    nd = row["nd"]
    if nd.get("junction") == "zhanguo":
        # 战国卷的秦疆外缘在海上画得很宽（那一卷的底图没有台湾、海南、济州岛），本卷底图有，这几个岛扣出去
        isl = shapely.union_all([shapely.box(119.8, 21.8, 122.2, 25.5), shapely.box(108.4, 17.9, 111.3, 20.3), shapely.box(126.1, 33.1, 127.0, 33.6)])
        qin = geom_of(ZG_LAST["s"]["秦"]).difference(isl)
        wei = geom_of(ZG_LAST["s"]["卫"])
        inner = {UK[k]: g for k, g in QIN_POLY.items() if k in UK}
        zz = {u: g for u, g in z.items() if row["pol"].get(UNITS[u]["k"]) not in ("秦", "卫")}
        # 秦以外的单位：扣掉照搬来的秦、卫；秦本身的郡用战国卷的郡界
        for u in list(zz):
            zz[u] = zz[u].difference(qin).difference(wei)
        zz.update(fill_gaps(inner, qin))
        zz[UK["卫"]] = wei
        pp = {UK["秦"]: qin}
        return zz, pp
    if nd.get("junction") == "hanmosanguo":
        hmu = {u["k"]: i for i, u in enumerate(HM[1]["units"])}
        han = geom_of(hm_rings(HM_184["z"][str(hmu["汉"])]))
        # 汉的外廓取汉末卷的政权外廓（含内属的南匈奴）；没有就用汉这个单位本身
        hp = HM_184.get("p", {}).get(str(hmu["汉"]))
        han_outline = geom_of(hm_rings(hp)) if hp is not None else han
        zz = {}
        copied = {}
        for k, v in HM_184["z"].items():
            uk = HM[1]["units"][int(k)]["k"]
            mine = ND.HM_UNIT.get(uk, uk)
            if uk == "汉" or mine not in UK:
                continue
            copied[UK[mine]] = geom_of(hm_rings(v))
            # 照搬来的单位（如乌桓）本卷此时可能没有归属点：归属照汉末卷写
            pk = HM[1]["units"][int(HM_184["pol"][k])]["k"]
            row["pol"].setdefault(mine, ND.HM_UNIT.get(pk, pk))
        cut = shapely.union_all(list(copied.values()) + [han])
        hanu = {u: g for u, g in z.items() if row["pol"].get(UNITS[u]["k"]) == "汉"}
        zz.update(fill_gaps(hanu, han))
        zz.update(copied)
        for u, g in z.items():
            if u not in zz and u not in hanu:
                g2 = g.difference(cut)
                if not g2.is_empty:
                    zz[u] = g2
        return zz, {UK["汉"]: han_outline}
    return z, p


LAND = None                                        # 底图陆地（标注位置只按陆地部分算，main 里载入）


def label_of(g):
    if LAND is not None:                           # 首节点照搬战国卷的秦疆画到了海上：标注只按陆上部分算
        try:
            gl = shapely.make_valid(g).intersection(LAND)
        except shapely.errors.GEOSException:
            gl = shapely.make_valid(g).buffer(0.001).intersection(LAND)
        gl = shapely.union_all(polys_of(gl)) if not gl.is_empty else gl
        if not gl.is_empty and gl.area > 0.02 * g.area:
            g = gl
    ps = polys_of(g)
    if not ps:
        return None
    big = max(ps, key=lambda q: q.area)
    from shapely.ops import polylabel
    try:
        c = polylabel(big, tolerance=0.02)
    except Exception:
        c = big.representative_point()
    r = big.exterior.distance(c)
    return [round(c.x, 2), round(c.y, 2), round(sum(q.area for q in ps), 2), round(r, 2)]


def boundary_lines(polys):
    """各郡国多边形之间的共边（郡界图层）"""
    if len(polys) < 2:
        return []
    lines = shapely.union_all([q.boundary for q in polys])
    outer = shapely.union_all(polys).boundary.buffer(0.03)
    inner = lines.difference(outer)
    inner = shapely.line_merge(inner) if not inner.is_empty else inner
    return [enc(list(l.coords)) for l in shapely.get_parts(inner) if l.geom_type == "LineString" and l.length > 0.08]


# ================================================================ 主程序
def main():
    rows = node_rows()
    for r in rows:                                 # 本卷用到的郡国单位（按点的次序，保证两遍构建的单位序号一致）
        for u in dict.fromkeys(x for x in r["own"] if x):
            if u not in UK:
                zh, en = UN.KINGDOM_NOTE.get(u) or jun_note(u)
                if u in UN.JUN_NOTE:                   # 郡的得名、建郡年代
                    zh, en = zh + UN.JUN_NOTE[u][0], (en + " " if en else "") + UN.JUN_NOTE[u][1]
                add_unit(u, "zhen", note=zh, notee=en)
        for u, p in r["pol"].items():
            if u not in UK or p not in UK:
                sys.exit(f"{r['nd']['label']}：单位 {u} 或政权 {p} 没有定义")
    global LAND
    base = json.loads((C.GEODATA / "base.json").read_text(encoding="utf8"))
    LAND = shapely.union_all([geom_of(p) for p in base["land"]])       # 每块陆地是一组环（奇偶填充）
    eng = engine_geoms()
    pool, where = [], {}

    def put(v):
        k = json.dumps(v, separators=(",", ":"))
        if k not in where:
            where[k] = len(pool); pool.append(v)
        return where[k]

    snaps = []
    adj = defaultdict(set)
    zl_en = {}                                     # 郡名注记的英文：zl 里用了本节点别名或非郡国单位名的，补进 GEO.zhoue
    for i, r in enumerate(rows):
        nd = r["nd"]
        z, lz, p, lp, zb, zl = {}, {}, {}, {}, [], []
        if eng and len(eng["nodes"]) == len(rows):
            en_ = eng["nodes"][i]
            zg = {int(k): geom_of(eng["geom"][v]) for k, v in en_["u"].items()}
            pg = {int(k): geom_of(eng["geom"][v]) for k, v in en_["pu"].items()}
            zg, pg = junction(i, r, zg, None, pg, None)
            for u, g in zg.items():
                rr = rings_of(g)
                if rr:
                    z[u] = put(rr)
                    L = label_of(g)
                    if L: lz[u] = L
            members = defaultdict(list)
            for uk, pk in r["pol"].items():
                if UK[uk] in zg:
                    members[pk].append(UK[uk])
            for pk, us in members.items():
                pu = UK[pk]
                if len(us) > 1 or us[0] != pu:
                    g = pg.get(pu) or shapely.union_all([zg[u] for u in us])
                    rr = rings_of(g)
                    if rr:
                        p[pu] = put(rr)
                        L = label_of(g)
                        if L: lp[pu] = L
                    # 郡界：多郡国政权内部的界线与郡国名
                    if len(us) > 1 and UNITS[pu]["kind"] != "tribe":
                        zb += boundary_lines([zg[u] for u in us])
                        for u in us:
                            if u in lz and lz[u][2] >= 0.6:
                                k = UNITS[u]["k"]
                                if k in nd["lab"]:         # 本节点有别名（如 73 年「鄯善·于阗（附汉）」）就标别名
                                    name, name_en = nd["lab"][k], nd["lab_en"].get(k, UNITS[u]["ne"])
                                else:
                                    name, name_en = UNITS[u]["n"], UNITS[u]["ne"]
                                if UNITS[u]["kind"] != "zhen" or k in nd["lab"]:
                                    assert zl_en.get(name, name_en) == name_en, (name, zl_en[name], name_en)
                                    zl_en[name] = name_en
                                zl.append([name] + lz[u])
            ks = list(zg)
            for a in range(len(ks)):
                for b in range(a + 1, len(ks)):
                    if zg[ks[a]].distance(zg[ks[b]]) < 0.05:
                        adj[ks[a]].add(ks[b]); adj[ks[b]].add(ks[a])
        sn = dict(y=nd["t"], tp=nd["tp"], era=nd["era"], era2=nd.get("era2", ""), t=nd["title"], d=nd["desc"],
                  z=z, lz=lz, p=p, lp=lp,
                  own=[UK[x] if x else -1 for x in r["own"]],
                  pol={UK[k]: UK[v] for k, v in r["pol"].items()},
                  lab={UK[k]: v for k, v in nd["lab"].items() if k in UK},
                  seat={UK[k]: SI[v] for k, v in nd["seat"].items() if k in UK and v in SI},
                  h=[UK[k] for k in nd["h"] if k in UK],
                  zb=put(zb), zl=zl,
                  erae=nd["era_en"], te=nd["title_en"], de=nd["desc_en"],
                  labe={UK[k]: v for k, v in nd["lab_en"].items() if k in UK},
                  sh=nd["short"], she=nd["short_en"])
        if nd.get("era2_en"):
            sn["era2e"] = nd["era2_en"]
        snaps.append(sn)
        print(f"   {nd['label']:>10}  {len(set(x for x in r['own'] if x)):>3} 单位  {len(p)} 政权层", flush=True)

    items, layers = IT.build(base, SEEDS, UK, ZG[1]["items"])
    hm_col = {u["k"]: HM[2][i] for i, u in enumerate(HM[1]["units"])}
    colors = UN.colors(UNITS, adj, ZG[1]["colors"], hm_col)
    first = next(s["y"] for s in snaps if s["y"] == label_t(*C.FIRST))
    bmap, regeo = layers.pop("base_map"), layers.pop("regeo")

    def remap(layer):                              # 底图图层的 it 换成本卷条目序号，删去的条目连同几何一并去掉
        out = []
        for x in layer:
            if "it" in x:
                if bmap.get(x["it"]) is None:
                    continue
                x = dict(x, it=bmap[x["it"]])
                if x["it"] in regeo:               # 改画的线（鸿沟与战国卷取同一走向）
                    x["p"] = enc(regeo[x["it"]])
            out.append(x)
        return out
    GEO = dict(land=base["land"], prov=base["prov"], border=base["border"], rivers=remap(base["rivers"]), lakes=remap(base["lakes"]),
               canals=remap(base["canals"]), deserts=remap(base["deserts"]), snaps=snaps, pool=pool, regions=[],
               ext=[C.VIEW[0], C.VIEW[1], C.VIEW[2], C.VIEW[3]], first=first,
               zhoue={**{u["n"]: u["ne"] for u in UNITS if u["kind"] == "zhen"}, **zl_en}, **layers)
    seeds_out = []
    for s in SEEDS:
        o = {k: s[k] for k in ("id", "n", "mod", "lon", "lat", "t")}
        if s.get("note"): o["note"] = s["note"]
        o["ne"] = s.get("ne") or EN.name(s["n"])
        o["mode"] = s.get("mode") or ""
        if s.get("notee"): o["notee"] = s["notee"]
        seeds_out.append(o)
    DATA = dict(units=[dict(k=u["k"], n=u["n"], kind=u["kind"], note=u["note"], ne=u["ne"], notee=u["notee"],
                            **({"x": 1} if u.get("x") else {})) for u in UNITS],
                seeds=seeds_out, items=items)
    C.BUILD.mkdir(exist_ok=True)
    # 统一引擎的可达倍数（era.toml [engine] seeds）
    (C.BUILD / "reach.txt").write_text("# 由 src/build.py 从 content/seeds.py 写出：点 经 纬 - R=倍数\n" + "".join(
        f"{k} {SEEDS[SI[k]]['lon']} {SEEDS[SI[k]]['lat']} - R={v}\n" for k, v in SD.RM.items() if k in SI), encoding="utf8")
    dump = lambda o, q: q.write_text(json.dumps(o, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    dump(GEO, C.BUILD / "geo.json"); dump(DATA, C.BUILD / "data.json"); dump(colors, C.BUILD / "colors.json")
    print(f"   {len(snaps)} 个节点 · {len(items)} 条目 · {len(SEEDS)} 个归属点 · {len(UNITS)} 个单位"
          + ("" if eng else "（还没有疆域：先跑统一引擎）"))
    print("   " + " ".join(f"{k} {v}" for k, v in Counter(i['c'] for i in items).most_common()))


if __name__ == "__main__":
    main()
