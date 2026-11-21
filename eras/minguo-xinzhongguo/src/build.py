# -*- coding: utf-8 -*-
"""民国形势图 · 数据构建（单仓第 1 段）。

读 content/ 的史料与 geodata/ 的底图，写出 build/geo.json（底图、节点归属）和 build/data.json（条目与说明），
再由 src/assemble.py 汇编成本卷的 source.json。

流程：
  1. 读节点、归属点、单位与各节点归属（src/content.py）
  2. 各节点“点 → 二级单位 → 政权”的归属
  3. 整理底图（海岸、河湖、运河、山脉、荒漠、今国界，东端跨过日期变更线）与点、线条目

疆域不在这里算：由统一疆域引擎按各节点的归属推算（单仓 core/engine/，结果在本卷的 engine.json；推算范围的 EXCLUDE
与国界墙仍写在 src/config.py，由引擎读取）；颜色由单仓的 global/palette.toml 定。本卷原来的投影平面栅格、通行代价、
多源最短路、覆盖图描界与贪心配色 2026-11 架构整理第三批起退役。
"""
import json, sys
import shapely
from shapely.geometry import shape, box, LineString, Polygon
from shapely.ops import unary_union
from shapely import affinity

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import config as C
import content as CT
sys.path.insert(0, str(C.CONTENT))
import geo as GM

LON0, LON1, LAT0, LAT1 = C.EXTENT
BB = box(LON0 - 1, LAT0 - 1, LON1 + 1, LAT1 + 1)
EXT_BOX = box(LON0, LAT0, LON1, LAT1)
EXT_POLY = EXT_BOX.difference(unary_union([Polygon(p) for p in C.EXCLUDE]))

def enc_ring(coords):
    """坐标 ×100 取整后差分编码；前端 decode() 还原。"""
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
    if g is None or g.is_empty: return []
    if g.geom_type == "Polygon": return [g]
    if g.geom_type in ("MultiPolygon", "GeometryCollection"): return [p for x in g.geoms for p in polys_of(x)]
    return []
def lines_of(g):
    if g is None or g.is_empty: return []
    if g.geom_type == "LineString": return [g]
    if g.geom_type in ("MultiLineString", "GeometryCollection"): return [p for x in g.geoms for p in lines_of(x)]
    return []
def ne(name): return json.load(open(C.NE_DIR / f"{name}.geojson", encoding="utf8"))
WEST = box(-180, -90, C.BASE_EXTENT[1] - 360, 90)
def wrapped(g, clip):
    """把西经部分（日期变更线以东）平移 360° 接到东边，再裁到 clip。"""
    parts = [g.intersection(clip)] if g.intersects(clip) else []
    if g.intersects(WEST): parts.append(affinity.translate(g.intersection(WEST), 360, 0).intersection(clip))
    return [p for p in parts if not p.is_empty]

def densify_ll(g, step=0.25):
    """经纬度多边形加密后再投影，免得长直边投影后偏离纬线弧。"""
    return shapely.segmentize(g, step)

# ======================================================================
# 1. 史料
# ======================================================================
D = CT.load_all()
if CT.ERR:
    for e in CT.ERR[:60]: print("错误", e)
    sys.exit(f"史料有 {len(CT.ERR)} 处错误，先运行 python3 tools/check.py 修正")
for w in CT.WARN[:20]: print("提醒", w)
NODES, SEEDS, UNITS, STATES, IT = D["nodes"], D["seeds"], D["units"], D["states"], D["items"]
SID = {s["id"]: i for i, s in enumerate(SEEDS)}
UK = {u["k"]: i for i, u in enumerate(UNITS)}
for s in SEEDS:
    if not (LON0 < s["lon"] < LON1 and LAT0 < s["lat"] < LAT1): sys.exit("归属点在推算范围外：" + s["id"])
print("nodes", len(NODES), "seeds", len(SEEDS), "units", len(UNITS))
def pol_of(st, uk): return st["pol"].get(uk, UNITS[UK[uk]]["pol"])

# ======================================================================
# 2. 各节点的归属（疆域由统一引擎按这些归属推算，见单仓 core/engine/）
# ======================================================================
OUTSN = []
for nd, st in zip(NODES, STATES):
    own_seed = [-1] * len(SEEDS)
    for sid, uk in st["own"].items():
        if uk is not None: own_seed[SID[sid]] = UK[uk]
    present = sorted(set(x for x in own_seed if x >= 0))
    polmap = {u: UK[pol_of(st, UNITS[u]["k"])] for u in present}
    OUTSN.append(dict(y=nd["y"], m=nd["m"], t=nd["t"], era=nd["era"], ti=nd["title"], d=nd["d"],
             own=own_seed,
             pol={str(u): p for u, p in polmap.items()},
             lab={str(UK[k]): v for k, v in sorted(st["lab"].items()) if UK[k] in polmap or UK[k] in polmap.values()},
             seat={str(UK[k]): SID[v] for k, v in sorted(st["seat"].items()) if UK[k] in polmap},
             h=sorted(UK[k] for k in st["hatch"] if UK[k] in polmap or UK[k] in polmap.values())))
print("snaps", len(OUTSN))

# 底图要素用到的湖泊取舍、荒漠多边形、今国界与今省界
SKIP_LAKES = {"South Aral Sea", "North Aral Sea"} | set(getattr(GM, "SKIP_LAKES_EXTRA", ()))
KEEP_RESERVOIR = {"Lake Zaysan"}
DESERTPOLY = {}
for f in ne("ne_10m_geography_regions_polys")["features"]:
    p = f["properties"]
    if not f["geometry"]: continue
    g = shape(f["geometry"])
    if not g.intersects(BB): continue
    if p.get("FEATURECLA") == "Desert": DESERTPOLY[p.get("NAME")] = g
CTRY_ALL = [(f["properties"]["ADM0_A3"], shape(f["geometry"])) for f in ne("ne_10m_admin_0_countries_chn")["features"] if f["geometry"]]
PROV = json.load(open(C.PROV_JSON, encoding="utf8"))

# ======================================================================
# 3. 底图要素与条目
# ======================================================================
BLON0, BLON1, BLAT0, BLAT1 = C.BASE_EXTENT
BASEBOX = box(BLON0, BLAT0, min(180, BLON1), BLAT1)
_lb = []
for nm in ("ne_10m_land", "ne_10m_minor_islands"):
    for f in ne(nm)["features"]:
        if not f["geometry"]: continue
        for g in wrapped(shape(f["geometry"]), box(BLON0, BLAT0, BLON1, BLAT1)): _lb += polys_of(g)
landB = unary_union(_lb)
LAND_OUT = []
for p in polys_of(landB):
    p = p.simplify(C.SIMPLIFY_LAND)
    if p.is_empty or p.area < C.LAND_MIN_AREA: continue
    for q in polys_of(p):
        rings = [enc_ring(list(q.exterior.coords))] + [enc_ring(list(h.coords)) for h in q.interiors if Polygon(h).area > C.LAND_HOLE_MIN_AREA]
        LAND_OUT.append(rings)
print("land polys", len(LAND_OUT))

CTRY = []
for a, g in CTRY_ALL:
    for gg in wrapped(g, box(BLON0, BLAT0, BLON1, BLAT1)): CTRY.append(gg)
coastbuf = landB.boundary.buffer(0.03)
BORDER = []
_bl2 = unary_union([g.boundary for g in CTRY]).difference(coastbuf)
for ls in lines_of(shapely.line_merge(_bl2) if not _bl2.is_empty else _bl2):
    ls = ls.simplify(C.SIMPLIFY_BORDER)
    if ls.length > 0.08: BORDER.append(enc_ring(list(ls.coords)))
print("border lines", len(BORDER))
EXTPOLY = [enc_ring(list(densify_ll(p, 0.5).exterior.coords)) for p in polys_of(EXT_POLY)]

ITEMS = []
def add_item(d): d["i"] = len(ITEMS); ITEMS.append(d); return d["i"]

# 河流
NE_RV_OUT = []
for f in ne("ne_10m_rivers_lake_centerlines")["features"]:
    g = f["geometry"]
    if not g: continue
    p = f["properties"]
    for gg in wrapped(shape(g), box(BLON0, BLAT0, BLON1, BLAT1)):
        for ls in lines_of(gg): NE_RV_OUT.append((p.get("name"), p.get("scalerank"), ls))
RIVERS = []
river_item = {}
TB0, TB1 = CT.T(GM.HUANG_BREAK[0]), CT.T(GM.HUANG_BREAK[1])
for n, sr, ls in NE_RV_OUT:
    pts = list(ls.simplify(C.SIMPLIFY_RIVER).coords)
    if len(pts) < 2: continue
    xs = [x for x, y in pts]; ys = [y for x, y in pts]
    name = GM.river_alias(n, xs, ys)
    if name is False: continue
    info = GM.NE_RIVERS.get(name)
    kind = "faint"
    if sr is not None and sr <= 6: kind = "minor"
    if info: kind = "major" if info[3] else "minor"
    if sr is not None and sr > C.RIVER_MAX_SCALERANK and not info: continue
    if name == "Huang" and max(xs) > GM.HUANG_CUT_LON:
        # 花园口以下：1938.06—1947.03 改道，期间不画
        west = [(x, y) for x, y in pts if x <= GM.HUANG_CUT_LON]; east = [(x, y) for x, y in pts if x >= GM.HUANG_CUT_LON - 0.02]
        if len(west) > 1: RIVERS.append(dict(k=kind, p=enc_ring(west), nm=info[0], info=info, key="Huang"))
        if len(east) > 1:
            RIVERS.append(dict(k=kind, p=enc_ring(east), nm=info[0], info=info, key="Huang", y1=TB0))
            RIVERS.append(dict(k=kind, p=enc_ring(east), nm=info[0], info=info, key="Huang", y0=TB1))
        continue
    RIVERS.append(dict(k=kind, p=enc_ring(pts), nm=(info[0] if info else None), info=info, key=name if info else None))
for mr in GM.MANUAL_RIVERS:
    RIVERS.append(dict(k="major" if mr["major"] else "minor", p=enc_ring(mr["pts"]), nm=mr["nm"],
                       info=(mr["nm"], mr["mod"], mr["note"], mr["major"]), y0=CT.T(mr.get("y0")), y1=CT.T(mr.get("y1")), key=mr.get("key", mr["nm"])))
for r in RIVERS:
    if not r.get("nm"): r["it"] = None; continue
    info = r["info"]; key = r["nm"]
    if key not in river_item:
        river_item[key] = add_item(dict(c="river", sub="river", old=info[0], mod=info[1], note=info[2], major=bool(info[3]),
                                        **({"y0": r["y0"]} if r.get("y0") is not None and r.get("key") == "黄泛" else {}),
                                        **({"y1": r["y1"]} if r.get("y1") is not None and r.get("key") == "黄泛" else {})))
    r["it"] = river_item[key]
seglen = {}
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
RIV_OUT = []
for r in RIVERS:
    d = dict(k=r["k"], p=r["p"])
    if r.get("it") is not None: d["it"] = r["it"]
    if r.get("y0") is not None: d["y0"] = r["y0"]
    if r.get("y1") is not None: d["y1"] = r["y1"]
    RIV_OUT.append(d)
print("rivers", len(RIV_OUT), "named", len(river_item))

LAKES = []
for f in ne("ne_10m_lakes")["features"] + [x for x in ne("ne_10m_lakes_historic")["features"] if x["properties"].get("name") in ("Lop Nur", "Aral Sea")]:
    if not f["geometry"]: continue
    p = f["properties"]; nm = p.get("name")
    if nm in SKIP_LAKES: continue
    if p.get("featurecla") == "Reservoir" and nm not in KEEP_RESERVOIR: continue
    for g in wrapped(shape(f["geometry"]), box(BLON0, BLAT0, BLON1, BLAT1)):
        info = GM.NE_LAKES.get(nm)
        if not info and g.area < 0.03: continue
        for pp in polys_of(g.simplify(0.01)):
            if pp.area < 0.004: continue
            it = None
            if info:
                ex = [x for x in ITEMS if x["c"] == "river" and x.get("sub") == "lake" and x["old"] == info[0]]
                if ex: it = ex[0]["i"]
                else:
                    c = pp.representative_point()
                    it = add_item(dict(c="river", sub="lake", old=info[0], mod=info[1], note=info[2], anc=[round(c.x, 2), round(c.y, 2)]))
            LAKES.append(dict(r=enc_ring(list(pp.exterior.coords)), **({"it": it} if it is not None else {})))
CAN = []
for nm, mod, pts, note in GM.CANALS:
    it = add_item(dict(c="canal", old=nm, mod=mod, note=note, anc=list(LineString(pts).interpolate(0.5, normalized=True).coords[0])))
    CAN.append(dict(p=enc_ring(pts), it=it))
for nm, mod, pts, note, major in GM.RANGES:
    a = LineString(pts).interpolate(0.5, normalized=True)
    add_item(dict(c="range", old=nm, mod=mod if mod != nm else "", note=note, geo=pts, anc=[round(a.x, 3), round(a.y, 3)], major=bool(major)))
DES = []
for nm, mod, nename, note in GM.DESERTS:
    g = DESERTPOLY.get(nename)
    if g is None: print("  没找到荒漠", nename); continue
    g = g.intersection(EXT_BOX)
    c = g.representative_point()
    it = add_item(dict(c="desert", old=nm, mod=mod if mod != nm else "", note=note, anc=[round(c.x, 2), round(c.y, 2)]))
    for p in polys_of(g.simplify(0.05)):
        DES.append(dict(r=enc_ring(list(p.exterior.coords)), it=it))

# 点状条目
for x in IT["capitals"]:
    add_item(dict(c="capital", old=x["old"], mod=x["mod"], lon=x["lon"], lat=x["lat"], st=UK[x["st"]], yrs=x["yrs"], note=x["note"], at=SID.get(x["at"]) if x["at"] else None))
for x in IT["battles"]:
    add_item(dict(c="battle", old=x["old"], mod=x["mod"], lon=x["lon"], lat=x["lat"], t=x["t"], t1=x["t1"], yt=x["yt"], sides=x["sides"], cmd=x["cmd"], note=x["note"]))
for x in IT["passes"]:
    add_item(dict(c="pass", old=x["old"], mod=x["mod"], lon=x["lon"], lat=x["lat"], note=x["note"]))
for x in IT["events"]:
    add_item(dict(c="event", old=x["old"], mod=x["mod"], lon=x["lon"], lat=x["lat"], t=x["t"], t1=x["t1"], yt=x["yt"], note=x["note"]))
for x in IT["concs"]:
    add_item(dict(c="conc", old=x["old"], mod=x["mod"], lon=x["lon"], lat=x["lat"], st=UK[x["st"]], t0=x["t0"], t1=x["t1"] if x["t1"] is not None else 9999 * 12, note=x["note"]))
for x in IT["lines"]:
    a = LineString(x["geo"]).interpolate(0.5, normalized=True)
    add_item(dict(c=x["c"], old=x["old"], mod=x["mod"], geo=x["geo"], anc=[round(a.x, 3), round(a.y, 3)], t0=x["t0"], t1=x["t1"] if x["t1"] is not None else 9999 * 12, note=x["note"]))
# 行军路线：每条一组 [经, 纬, 到达月序, 地名]，前端按节点画出已走过的一段
ROUTES = []
for R in IT["routes"]:
    pts = [list(p) for p in R["pts"]]
    it = add_item(dict(c="route", old=R["name"], mod=R["mod"], note=R["note"], side=R["side"], t=pts[0][2], t1=pts[-1][2], yt=R["yt"], anc=pts[len(pts) // 2][:2]))
    ROUTES.append(dict(it=it, pts=pts))
print("items", len(ITEMS), "routes", len(ROUTES))

# ======================================================================
# 输出
# ======================================================================
SEAS = [[n, lo, la, lv] for n, lo, la, lv in GM.SEAS]
FIRST = next((nd["t"] for nd in NODES if nd["id"] == C.FIRST), NODES[0]["t"])
GEO = dict(land=LAND_OUT, prov=PROV, border=BORDER, rivers=RIV_OUT, lakes=LAKES, canals=CAN, deserts=DES,
           snaps=OUTSN, routes=ROUTES, seas=SEAS, ext=[LON0, LON1, LAT0, LAT1], extpoly=EXTPOLY,
           base=list(C.BASE_EXTENT), proj=list(C.PROJ), first=FIRST)
UOUT = [dict(k=u["k"], n=u["n"], kind=u["kind"], note=u.get("note", "")) for u in UNITS]
SOUT = [dict(id=s["id"], n=s["n"], mod=s["mod"], lon=s["lon"], lat=s["lat"], t=s["t"], **({"nm": s["names"]} if s["names"] else {})) for s in SEEDS]
DATA = dict(units=UOUT, seeds=SOUT, items=ITEMS)
C.BUILD.mkdir(exist_ok=True)
json.dump(GEO, open(C.BUILD / "geo.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
json.dump(DATA, open(C.BUILD / "data.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print("geo.json", (C.BUILD / "geo.json").stat().st_size // 1024, "KB; data.json", (C.BUILD / "data.json").stat().st_size // 1024, "KB")
