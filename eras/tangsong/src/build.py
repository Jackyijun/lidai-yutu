# -*- coding: utf-8 -*-
"""唐宋之际形势图 · 数据构建（单仓第 1 段）。

读 content/ 的史料与 geodata/ 的底图，写出 build/geo.json（底图、节点归属）和 build/data.json（条目与说明），
再由 src/assemble.py 汇编成本卷的 source.json。

流程：
  1. 读州府种子（seeds.txt）
  2. 解析时间节点 DSL（snaps.txt），得到每个节点“州 → 藩镇 → 政权”的归属
  3. 读底图（陆地、湖泊、荒漠、河道）
  4. 各节点的归属
  5. 整理底图（海岸、河湖、运河、山脉、荒漠）与点要素

疆域不在这里算：由统一疆域引擎按各节点的归属推算（单仓 core/engine/，结果在本卷的 engine.json）；颜色由单仓的
global/palette.toml 定。本卷原来的栅格分区（海陆栅格、代价栅格、多源最短路、描线）与贪心配色 2026-11 架构整理第三批起退役。
"""
import json, sys
from shapely.geometry import shape, box, LineString, Polygon
from shapely.ops import unary_union

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import config as C
sys.path.insert(0, str(C.CONTENT))
import units as UM
import items as IM

LON0, LON1, LAT0, LAT1 = C.EXTENT
BB = box(LON0 - 1, LAT0 - 1, LON1 + 1, LAT1 + 1)

def enc_ring(coords):
    """坐标 ×100 取整后差分编码，大幅缩小 JSON 体积；前端 decode() 还原。"""
    out = []; px = py = 0
    for i, (x, y) in enumerate(coords):
        X, Y = int(round(x * 100)), int(round(y * 100))
        if i == 0: out += [X, Y]
        else:
            if X == px and Y == py: continue
            out += [X - px, Y - py]
        px, py = X, Y
    return out

def polys_of(g):
    if g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    if g.geom_type == "MultiPolygon": return list(g.geoms)
    if g.geom_type == "GeometryCollection": return [p for x in g.geoms for p in polys_of(x)]
    return []
def lines_of(g):
    if g.is_empty: return []
    if g.geom_type == "LineString": return [g]
    if g.geom_type == "MultiLineString": return list(g.geoms)
    if g.geom_type == "GeometryCollection": return [p for x in g.geoms for p in lines_of(x)]
    return []
def ne(name): return json.load(open(C.NE_DIR / f"{name}.geojson", encoding="utf8"))

# ======================================================================
# 1. 种子（州府、城邑、区域辅助点）
# ======================================================================
SEEDS = []
for line in open(C.CONTENT / "seeds.txt", encoding="utf8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    t = line.split()
    sid, lo, la, mod = t[0], float(t[1]), float(t[2]), t[3]
    typ, names = "z", None
    for x in t[4:]:
        if x in ("c", "r", "z"): typ = x
        elif x.startswith("N="):
            names = []
            for part in x[2:].split(","):
                y, n = part.split(":", 1); names.append([int(y), n])
    disp = sid.split("·")[0]   # “新州·岭南” 显示为 “新州”
    SEEDS.append(dict(id=sid, n=disp, lon=lo, lat=la, mod=mod, t=typ, names=names))
SID = {s["id"]: i for i, s in enumerate(SEEDS)}
assert len(SID) == len(SEEDS), "seeds.txt 中有重复的 ID"
print("seeds", len(SEEDS))

# ======================================================================
# 2. 单位与时间节点（解析 snaps.txt）
# ======================================================================
UNITS = UM.U
UK = {u["k"]: i for i, u in enumerate(UNITS)}
assert len(UK) == len(UNITS), "units.py 中有重复的键"

import snapdsl
SNAPS = snapdsl.parse(C.CONTENT / "snaps.txt", SID, UK)
print("snaps", [s["y"] for s in SNAPS])

for sn in SNAPS:
    missing = [s["id"] for s in SEEDS if s["id"] not in sn["st"]["own"]]
    if missing: print("  unassigned at", sn["y"], missing)

def pol_of(st, uk): return st["pol"].get(uk, UNITS[UK[uk]]["pol"])

# ======================================================================
# 3. 读底图：陆地、湖泊、Natural Earth 地理区（荒漠）、河道
# ======================================================================
LANDG = []
for f in ne("ne_10m_land")["features"]:
    LANDG += polys_of(shape(f["geometry"]).intersection(BB))
for f in ne("ne_10m_minor_islands")["features"]:
    g = shape(f["geometry"])
    if g.intersects(BB): LANDG += polys_of(g.intersection(BB))
landU = unary_union(LANDG)
LAKEG = []
for f in ne("ne_10m_lakes")["features"]:
    if not f["geometry"]: continue
    g = shape(f["geometry"])
    if g.intersects(BB): LAKEG.append((f["properties"].get("name"), g.intersection(BB)))
for f in ne("ne_10m_lakes_historic")["features"]:
    if not f["geometry"]: continue
    g = shape(f["geometry"])
    if g.intersects(BB) and f["properties"].get("name") == "Lop Nur": LAKEG.append(("Lop Nur", g.intersection(BB)))
DESERTPOLY = {}
for f in ne("ne_10m_geography_regions_polys")["features"]:
    p = f["properties"]
    if not f["geometry"]: continue
    g = shape(f["geometry"])
    if not g.intersects(BB): continue
    if p.get("FEATURECLA") == "Desert": DESERTPOLY[p.get("NAME")] = g
NE_RV = []
for f in ne("ne_10m_rivers_lake_centerlines")["features"]:
    g = f["geometry"]
    if not g: continue
    gg = shape(g)
    if not gg.intersects(BB): continue
    p = f["properties"]
    for ls in lines_of(gg.intersection(BB)):
        NE_RV.append((p.get("name"), p.get("scalerank"), ls))

# ======================================================================
# 4. 各节点的归属（疆域由统一引擎按这些归属推算，见单仓 core/engine/）
# ======================================================================
OUTSN = []
for sn in SNAPS:
    st = sn["st"]
    own_seed = [-1] * len(SEEDS)
    for sid, uk in st["own"].items():
        if uk is not None: own_seed[SID[sid]] = UK[uk]
    present = sorted({u for u in own_seed if u >= 0})
    polmap = {u: UK[pol_of(st, UNITS[u]["k"])] for u in present}
    OUTSN.append(dict(y=sn["y"], era=sn["era"], t=sn["t"], d=sn["d"],
             own=own_seed,
             pol={str(u): p for u, p in polmap.items()},
             lab={str(UK[k]): v for k, v in st["lab"].items() if UK[k] in polmap or UK[k] in polmap.values()},
             seat={str(UK[k]): SID[v] for k, v in st["seat"].items() if UK[k] in polmap},
             h=sorted(UK[k] for k in st["hatch"] if UK[k] in polmap)))
    print("snap", sn["y"], "units", len(present), "polities", len(set(polmap.values())))

# ======================================================================
# 5. 底图要素与条目
# ======================================================================
LAND_OUT = []
for p in polys_of(landU.intersection(box(LON0 - 0.5, LAT0 - 0.5, LON1 + 0.5, LAT1 + 0.5))):
    p = p.simplify(C.SIMPLIFY_LAND)
    if p.is_empty or p.area < C.LAND_MIN_AREA: continue
    for q in polys_of(p):
        rings = [enc_ring(list(q.exterior.coords))] + [enc_ring(list(h.coords)) for h in q.interiors if Polygon(h).area > C.LAND_HOLE_MIN_AREA]
        LAND_OUT.append(rings)
print("land polys", len(LAND_OUT))

BORDER = []
for f in ne("ne_10m_admin_0_boundary_lines_land")["features"]:
    g = shape(f["geometry"])
    if not g.intersects(BB): continue
    for ls in lines_of(g.intersection(box(LON0, LAT0, LON1, LAT1))):
        ls = ls.simplify(C.SIMPLIFY_BORDER)
        if ls.length > 0.05: BORDER.append(enc_ring(list(ls.coords)))

PROV = json.load(open(C.PROV_JSON, encoding="utf8"))

ITEMS = []
def add_item(d): d["i"] = len(ITEMS); ITEMS.append(d); return d["i"]

# 河流：Natural Earth 河道 + 手绘古河道，按古名合并为条目
RIVERS = []
river_item = {}
# 同一古名的河分几段时，条目的今名与说明取 NE_RIVERS 里写在最前的那一段（而不是底图里先遇到的那段）
RIVER_PRIMARY = {}
for _k, _v in IM.NE_RIVERS.items(): RIVER_PRIMARY.setdefault(_v[0], _v)
for n, sr, ls in NE_RV:
    if n == "Hudi": continue
    pts = list(ls.simplify(C.SIMPLIFY_RIVER).coords)
    if len(pts) < 2: continue
    xs = [x for x, y in pts]
    name = n
    if n == "Han" and min(xs) > 120: name = "Han_kr"
    if n == "Min" and min(xs) > 110: info = ("闽江", "闽江", "建溪、富屯溪汇合后经福州入海。", 0)
    else: info = IM.NE_RIVERS.get(name)
    kind = "faint"
    if sr is not None and sr <= 6: kind = "minor"
    if info: kind = "major" if info[3] else "minor"
    if n == "Huang" and min(xs) > 110:     # 今黄河下游：郑州以西照画，以东改成虚线“今河道”
        west = [(x, y) for x, y in pts if x <= 113.65]
        east = [(x, y) for x, y in pts if x >= 113.55]
        if len(west) > 1: RIVERS.append(dict(k="major", p=enc_ring(west), it=None, nm="河"))
        if len(east) > 1: RIVERS.append(dict(k="modern", p=enc_ring(east), it=None, nm=None))
        continue
    if sr is not None and sr >= 9 and not info: continue
    RIVERS.append(dict(k=kind, p=enc_ring(pts), nm=(info[0] if info else None), info=info))
for nm, mod, pts, note, major in IM.MANUAL_RIVERS:
    RIVERS.append(dict(k="major" if major else "minor", p=enc_ring(pts), nm=nm, info=(nm, mod, note, major), manual=True))
for r in RIVERS:
    if not r.get("nm"): r["it"] = None; continue
    info = r.get("info")
    key = r["nm"]
    if key not in river_item:
        if info is None: info = IM.NE_RIVERS["Huang"]
        if not r.get("manual"): info = RIVER_PRIMARY.get(key, info)
        mod = info[1]; note = info[2]
        if key == "河": mod, note = "黄河", IM.MANUAL_RIVERS[0][3]
        if key == "淮水": mod, note = "淮河", "淮水。958 年以前，后周与南唐以淮为界，此后以长江为界。唐至北宋时淮河经泗州、楚州独流入海（1194 年后黄河夺淮，下游淤塞形成洪泽湖）。"
        river_item[key] = add_item(dict(c="river", sub="river", old=key, mod=mod, note=note, major=bool(info[3])))
    r["it"] = river_item[key]
seglen = {}   # 注记锚点：每条河最长一段的中点
for r in RIVERS:
    if r.get("it") is None: continue
    x = y = 0; pts = []
    for i in range(0, len(r["p"]), 2): x += r["p"][i]; y += r["p"][i + 1]; pts.append((x / 100, y / 100))
    if len(pts) < 2: continue
    L = LineString(pts).length
    if L > seglen.get(r["it"], (0, None))[0]:
        mid = LineString(pts).interpolate(0.5, normalized=True)
        seglen[r["it"]] = (L, [round(mid.x, 3), round(mid.y, 3)])
for it, (L, a) in seglen.items(): ITEMS[it]["anc"] = a
RIV_OUT = [dict(k=r["k"], p=r["p"], **({"it": r["it"]} if r.get("it") is not None else {})) for r in RIVERS]
print("rivers", len(RIV_OUT), "named", len(river_item))

LAKES = []
for n, g in LAKEG:
    info = IM.NE_LAKES.get(n)
    if not info and g.area < 0.03: continue
    for p in polys_of(g.simplify(C.SIMPLIFY_LAKE)):
        if p.area < 0.004: continue
        it = None
        if info:
            ex = [x for x in ITEMS if x["c"] == "river" and x.get("sub") == "lake" and x["old"] == info[0] and x["mod"] == info[1]]
            if ex: it = ex[0]["i"]
            else:
                c = p.representative_point()
                it = add_item(dict(c="river", sub="lake", old=info[0], mod=info[1], note=info[2], anc=[round(c.x, 2), round(c.y, 2)]))
        LAKES.append(dict(r=enc_ring(list(p.exterior.coords)), **({"it": it} if it is not None else {})))
for nm, mod, lo, la, rx, ry, note in IM.MARSHES:
    add_item(dict(c="river", sub="marsh", old=nm, mod=mod, note=note, lon=lo, lat=la, rx=rx, ry=ry, anc=[lo, la]))
CAN = []
for nm, mod, pts, note in IM.CANALS:
    it = add_item(dict(c="canal", old=nm, mod=mod, note=note, anc=list(LineString(pts).interpolate(0.5, normalized=True).coords[0])))
    CAN.append(dict(p=enc_ring(pts), it=it))
for nm, mod, pts, note, major in IM.RANGES:
    a = LineString(pts).interpolate(0.5, normalized=True)
    add_item(dict(c="range", old=nm, mod=mod, note=note, geo=pts, anc=[round(a.x, 3), round(a.y, 3)], major=bool(major)))
DES = []
for nm, mod, nename, note in IM.DESERTS:
    if isinstance(nename, tuple):     # 范围手绘：这里只出条目与注记点，几何由单仓 core/v1/overlay.py 换进（geodata/derived/sands.json）
        add_item(dict(c="desert", old=nm, mod=mod, note=note, anc=list(nename)))
        continue
    g = DESERTPOLY.get(nename)
    if g is None: print("no desert", nename); continue
    c = g.representative_point()
    it = add_item(dict(c="desert", old=nm, mod=mod, note=note, anc=[round(c.x, 2), round(c.y, 2)]))
    for p in polys_of(g.simplify(0.05)):
        DES.append(dict(r=enc_ring(list(p.exterior.coords)), it=it))

for nm, mod, lo, la, st, yrs, note, at in IM.CAPITALS:
    assert st in UK, ("都城所属政权不存在", st)
    add_item(dict(c="capital", old=nm, mod=mod, lon=lo, lat=la, st=UK[st], yrs=yrs, note=note, at=SID.get(at) if at else None))
for nm, mod, lo, la, y, yt, sides, cmd, note in IM.BATTLES:
    add_item(dict(c="battle", old=nm, mod=mod, lon=lo, lat=la, y=y, yt=yt, sides=sides, cmd=cmd, note=note))
for nm, mod, lo, la, note in IM.PASSES:
    add_item(dict(c="pass", old=nm, mod=mod, lon=lo, lat=la, note=note))
EVENT_END = getattr(IM, "EVENT_END", {})
for nm, mod, lo, la, y, yt, note in IM.EVENTS:
    d = dict(c="event", old=nm, mod=mod, lon=lo, lat=la, y=y, yt=yt, note=note)
    if nm in EVENT_END: d["y1"] = EVENT_END[nm]
    add_item(d)
for nm, lo, la, y0, y1, note in IM.PEOPLES:
    add_item(dict(c="people", old=nm, mod="", lon=lo, lat=la, y0=y0, y1=y1, note=note))

# 行军路线：每条一组 [经, 纬, 到达年, 地名]，前端按节点年份画出已走过的一段
ROUTES = []
for R in getattr(IM, "ROUTES", []):
    pts = [list(p) for p in R["pts"]]
    it = add_item(dict(c="route", old=R["name"], mod=R["mod"], note=R["note"], y=pts[0][2], y1=pts[-1][2],
                       yt=R.get("yt", f"{pts[0][2]}—{pts[-1][2]}"), anc=pts[len(pts) // 2][:2]))
    ROUTES.append(dict(it=it, pts=pts))

# 重要地域（如燕云十六州）：m 是成员点（含 extra），各分区的 m 与 line（画不画分界线）。范围线、分界线与注记由统一引擎
# 按分区描（单仓 core/engine/，结果在本卷 engine.json 的 regions），不在这里算
REG_OUT = []
for R in getattr(IM, "REGIONS", []):
    ids = lambda names: [SID[n] for n in names]
    for n in R["members"] + R.get("extra", []): assert n in SID, ("地域成员不在 seeds.txt", n)
    groups = [dict(n=g["name"], y0=g.get("y0", R["y0"]), m=ids(g["members"] + g.get("extra", [])),
                   **({"line": True} if g.get("line") else {})) for g in R.get("groups", [])]
    it = add_item(dict(c="region", old=R["name"], mod=R["mod"], note=R["note"], y0=R["y0"], members=ids(R["members"])))
    REG_OUT.append(dict(it=it, y0=R["y0"], groups=groups, m=ids(R["members"] + R.get("extra", []))))
print("regions", [(ITEMS[r["it"]]["old"], [g["n"] for g in r["groups"]]) for r in REG_OUT])

# ======================================================================
# 输出
# ======================================================================
GEO = dict(land=LAND_OUT, prov=PROV, border=BORDER, rivers=RIV_OUT, lakes=LAKES, canals=CAN, deserts=DES, snaps=OUTSN, regions=REG_OUT, routes=ROUTES,
           ext=[LON0, LON1, LAT0, LAT1], first=C.FIRST)
UOUT = [dict(k=u["k"], n=u["n"], kind=u["kind"], note=u["note"]) for i, u in enumerate(UNITS)]
SOUT = [dict(id=s["id"], n=s["n"], mod=s["mod"], lon=s["lon"], lat=s["lat"], t=s["t"], **({"nm": s["names"]} if s["names"] else {})) for s in SEEDS]
DATA = dict(units=UOUT, seeds=SOUT, items=ITEMS)
C.BUILD.mkdir(exist_ok=True)
json.dump(GEO, open(C.BUILD / "geo.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
json.dump(DATA, open(C.BUILD / "data.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print("geo.json", (C.BUILD / "geo.json").stat().st_size // 1024, "KB; data.json", (C.BUILD / "data.json").stat().st_size // 1024, "KB")
