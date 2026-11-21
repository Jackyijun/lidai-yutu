# -*- coding: utf-8 -*-
"""宋辽夏金元形势图 · 数据构建（单仓第 1 段）。

读 content/ 的史料与 geodata/ 的底图，写出 build/geo.json（底图、节点归属）和 build/data.json（条目与说明），
再由 src/assemble.py 汇编成本卷的 source.json。

流程：
  1. 读归属点（seeds.txt）、单位（units.py）、时间节点（snaps.txt）
  2. 各节点“点 → 二级单位 → 政权”的归属
  3. 整理底图（海岸、河湖、运河、山脉、荒漠、今国界）与点、线条目

疆域不在这里算：由统一疆域引擎按各节点的归属推算（单仓 core/engine/，结果在本卷的 engine.json）；颜色由单仓的
global/palette.toml 定。本卷原来的投影平面栅格、通行代价、多源最短路、覆盖图描界与贪心配色 2026-11 架构整理第三批起退役。
"""
import json, re, sys
import shapely
from shapely.geometry import shape, box, LineString, Polygon
from shapely.ops import unary_union

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import config as C
sys.path.insert(0, str(C.CONTENT))
import units as UM
import items as IM

LON0, LON1, LAT0, LAT1 = C.EXTENT
BB = box(LON0 - 1, LAT0 - 1, LON1 + 1, LAT1 + 1)
EXT_BOX = box(LON0, LAT0, LON1, LAT1)

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

# ======================================================================
# 1. 归属点（州府、城邑、区域辅助点）
# ======================================================================
SEEDS = []
for line in open(C.CONTENT / "seeds.txt", encoding="utf8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    t = line.split()
    sid, lo, la, mod = t[0], float(t[1]), float(t[2]), t[3]
    typ, names, reach = "z", None, 1.0
    for x in t[4:]:
        if x in ("c", "r", "z"): typ = x
        elif x.startswith("N="):
            names = []
            for part in x[2:].split(","):
                y, n = part.split(":", 1); names.append([int(y), n])
        elif x.startswith("R="): reach = float(x[2:])
        else: raise SystemExit(f"seeds.txt 无法识别的字段：{line}")
    assert LON0 < lo < LON1 and LAT0 < la < LAT1, ("归属点在全图范围外", sid)
    SEEDS.append(dict(id=sid, n=sid.split("·")[0], lon=lo, lat=la, mod=mod, t=typ, names=names, R=reach))
SID = {s["id"]: i for i, s in enumerate(SEEDS)}
assert len(SID) == len(SEEDS), "seeds.txt 中有重复的 ID：" + str([s["id"] for s in SEEDS if [x["id"] for x in SEEDS].count(s["id"]) > 1][:5])
print("seeds", len(SEEDS))

# ======================================================================
# 2. 单位与时间节点（解析 snaps.txt）
# ======================================================================
UNITS = UM.U
UK = {u["k"]: i for i, u in enumerate(UNITS)}
assert len(UK) == len(UNITS), "units.py 中有重复的键"

SNAPS = []
state = dict(own={}, lab={}, pol={}, seat={}, hatch=set())
cur = None; history = {}; start = None
def snapshot(): return dict(own=dict(state["own"]), lab=dict(state["lab"]), pol=dict(state["pol"]), seat=dict(state["seat"]), hatch=set(state["hatch"]))

for ln, raw in enumerate(open(C.CONTENT / "snaps.txt", encoding="utf8"), 1):
    line = raw.rstrip("\n")
    if not line.strip() or line.lstrip().startswith("#"): continue
    if line.startswith("@"):
        if cur: history[cur["y"]] = snapshot(); SNAPS.append(dict(cur, st=history[cur["y"]]))
        parts = [p.strip() for p in line[1:].split("|")]
        assert len(parts) == 4, ("节点行应有 4 段：年份 | 年号 | 标题 | 概述", ln)
        cur = dict(y=int(parts[0]), era=parts[1], t=parts[2], d=parts[3])
        assert not SNAPS or cur["y"] > SNAPS[-1]["y"], ("节点年份须递增", cur["y"])
        start = dict(own=dict(state["own"]))
        continue
    head, _, body = line.partition(":")
    head = head.strip(); toks = body.split()
    if head in ("割据", "藩属"):            # 整行替换：本节点起这些单位加斜线
        state["hatch"] = set(toks)
        for k in toks: assert k in UK, ("斜线行里的单位不存在", k, ln)
        continue
    if head in ("+藩属", "-藩属"):          # 增减
        for k in toks:
            assert k in UK, ("斜线行里的单位不存在", k, ln)
            (state["hatch"].add if head[0] == "+" else state["hatch"].discard)(k)
        continue
    if head == "·":
        for tk in toks:
            assert tk in SID, ("未知归属点", tk, cur["y"], ln); state["own"][tk] = None
        continue
    m = re.match(r"^([^\[\]{}>]+)(?:\[([^\]]*)\])?(?:\{([^}]*)\})?(?:>(.+))?$", head)
    assert m, ("无法解析的行", ln, head)
    uk, lab, seat, pol = m.group(1).strip(), m.group(2), m.group(3), m.group(4)
    assert uk in UK, ("units.py 里没有这个单位", uk, cur["y"], ln)
    if lab is not None:
        if lab == "": state["lab"].pop(uk, None)
        else: state["lab"][uk] = lab
    if seat is not None:
        if seat == "": state["seat"].pop(uk, None)
        else:
            assert seat in SID, ("治所不在 seeds.txt", seat, ln); state["seat"][uk] = seat
    if pol is not None:
        assert pol.strip() in UK, ("所属政权不存在", pol, ln); state["pol"][uk] = pol.strip()
    for tk in toks:
        if tk.startswith("@"):
            ref = tk[1:]
            if "@" in ref:   # @单位@年份：取该年节点结束时该单位的点
                rk, ry = ref.split("@"); src = history[int(ry)]["own"]
            else:
                rk = ref; src = start["own"]
            assert rk in UK, ("引用的单位不存在", rk, ln)
            lst = [s for s, u in src.items() if u == rk]
            if not lst: print("  WARN 空引用", tk, "in", cur["y"])
            for s in lst: state["own"][s] = uk
        else:
            assert tk in SID, ("未知归属点", tk, cur["y"], uk, ln); state["own"][tk] = uk
history[cur["y"]] = snapshot()
SNAPS.append(dict(cur, st=history[cur["y"]]))
print("snaps", len(SNAPS), [s["y"] for s in SNAPS])
for sn in SNAPS:
    missing = [s["id"] for s in SEEDS if s["id"] not in sn["st"]["own"]]
    if missing: print("  未分配 at", sn["y"], missing[:30], "…" if len(missing) > 30 else "")

def pol_of(st, uk): return st["pol"].get(uk, UNITS[UK[uk]]["pol"])

# ======================================================================
# 3. 各节点的归属（疆域由统一引擎按这些归属推算，见单仓 core/engine/）
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
             lab={str(UK[k]): v for k, v in sorted(st["lab"].items()) if UK[k] in polmap or UK[k] in polmap.values()},
             seat={str(UK[k]): SID[v] for k, v in sorted(st["seat"].items()) if UK[k] in polmap},
             h=sorted(UK[k] for k in st["hatch"] if UK[k] in polmap)))
    print("snap", sn["y"], "units", len(present), "polities", len(set(polmap.values())), flush=True)

# 湖泊的取舍（底图用）、Natural Earth 地理区里的荒漠
SKIP_LAKES = {"South Aral Sea", "North Aral Sea"} | set(getattr(IM, "SKIP_LAKES_EXTRA", ()))   # 今日已萎缩的咸海改用历史湖岸；近代形成的湖不画
KEEP_RESERVOIR = {"Lake Zaysan"}
DESERTPOLY = {}
for f in ne("ne_10m_geography_regions_polys")["features"]:
    p = f["properties"]
    if not f["geometry"]: continue
    g = shape(f["geometry"])
    if not g.intersects(BB): continue
    if p.get("FEATURECLA") == "Desert": DESERTPOLY[p.get("NAME")] = g

# ======================================================================
# 4. 底图要素与条目
# ======================================================================
# 底图（陆地、河湖、今国界）画到 BASE_EXTENT，比疆域范围 EXTENT 大得多
BLON0, BLON1, BLAT0, BLAT1 = C.BASE_EXTENT
BASEBOX = box(BLON0, BLAT0, BLON1, BLAT1)
_lb = []
for nm in ("ne_10m_land", "ne_10m_minor_islands"):
    for f in ne(nm)["features"]:
        if not f["geometry"]: continue
        g = shape(f["geometry"])
        if g.intersects(BASEBOX): _lb += polys_of(g.intersection(BASEBOX))
landB = unary_union(_lb)
LAND_OUT = []
for p in polys_of(landB):
    p = p.simplify(C.SIMPLIFY_LAND)
    if p.is_empty or p.area < C.LAND_MIN_AREA: continue
    for q in polys_of(p):
        rings = [enc_ring(list(q.exterior.coords))] + [enc_ring(list(h.coords)) for h in q.interiors if Polygon(h).area > C.LAND_HOLE_MIN_AREA]
        LAND_OUT.append(rings)
print("land polys", len(LAND_OUT))

# 今国界：由中国视角版国界多边形求相邻边（海岸线不画）
CTRY = [shape(f["geometry"]) for f in ne("ne_10m_admin_0_countries_chn")["features"] if f["geometry"]]
CTRY = [g.intersection(BASEBOX) for g in CTRY if g.intersects(BASEBOX)]
coastbuf = landB.boundary.buffer(0.03)
BORDER = []
_bl = unary_union([g.boundary for g in CTRY]).difference(coastbuf).intersection(BASEBOX)
for ls in lines_of(shapely.line_merge(_bl) if not _bl.is_empty else _bl):
    ls = ls.simplify(C.SIMPLIFY_BORDER)
    if ls.length > 0.08: BORDER.append(enc_ring(list(ls.coords)))
print("border lines", len(BORDER))

PROV = json.load(open(C.PROV_JSON, encoding="utf8"))

ITEMS = []
def add_item(d): d["i"] = len(ITEMS); ITEMS.append(d); return d["i"]

# 河流：Natural Earth 河道 + 手绘古河道，按古名合并为条目
# 河道取底图范围
NE_RV_OUT = []
for f in ne("ne_10m_rivers_lake_centerlines")["features"]:
    g = f["geometry"]
    if not g: continue
    gg = shape(g)
    if not gg.intersects(BASEBOX): continue
    p = f["properties"]
    for ls in lines_of(gg.intersection(BASEBOX)):
        NE_RV_OUT.append((p.get("name"), p.get("scalerank"), ls))
RIVERS = []
river_item = {}
def river_key(n, xs, ys):
    return IM.river_alias(n, xs, ys) if hasattr(IM, "river_alias") else n
for n, sr, ls in NE_RV_OUT:
    pts = list(ls.simplify(C.SIMPLIFY_RIVER).coords)
    if len(pts) < 2: continue
    xs = [x for x, y in pts]; ys = [y for x, y in pts]
    name = river_key(n, xs, ys)
    if name is False: continue                       # 别名函数可以把今河道整段剔除
    info = IM.NE_RIVERS.get(name)
    kind = "faint"
    if sr is not None and sr <= 6: kind = "minor"
    if info: kind = "major" if info[3] else "minor"
    if name in IM.MODERN_SPLIT:                       # 今河道与古河道分叉处：一侧照画，一侧改虚线
        cut = IM.MODERN_SPLIT[name]
        keep = [(x, y) for x, y in pts if cut(x, y)]
        mod_ = [(x, y) for x, y in pts if not cut(x, y)]
        if len(keep) > 1: RIVERS.append(dict(k=kind, p=enc_ring(keep), nm=info[0] if info else None, info=info))
        if len(mod_) > 1: RIVERS.append(dict(k="modern", p=enc_ring(mod_), nm=None))
        continue
    if sr is not None and sr > C.RIVER_MAX_SCALERANK and not info: continue
    RIVERS.append(dict(k=kind, p=enc_ring(pts), nm=(info[0] if info else None), info=info))
for mr in IM.MANUAL_RIVERS:
    RIVERS.append(dict(k="major" if mr["major"] else "minor", p=enc_ring(mr["pts"]), nm=mr["nm"],
                       info=(mr["nm"], mr["mod"], mr["note"], mr["major"]), y0=mr.get("y0"), y1=mr.get("y1"), key=mr.get("key", mr["nm"])))
for r in RIVERS:
    if not r.get("nm"): r["it"] = None; continue
    info = r["info"]; key = r.get("key") or r["nm"]
    if key not in river_item:
        ov = IM.RIVER_ITEM_OVERRIDE.get(key, {})
        river_item[key] = add_item(dict(c="river", sub="river", old=ov.get("old", info[0]), mod=ov.get("mod", info[1]),
                                        note=ov.get("note", info[2]), major=bool(info[3])))
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

LAKEG_OUT = []
for f in ne("ne_10m_lakes")["features"]:
    if not f["geometry"]: continue
    p = f["properties"]; nm = p.get("name")
    if nm in SKIP_LAKES: continue
    if p.get("featurecla") == "Reservoir" and nm not in KEEP_RESERVOIR: continue
    g = shape(f["geometry"])
    if g.intersects(BASEBOX): LAKEG_OUT.append((nm, g.intersection(BASEBOX)))
for f in ne("ne_10m_lakes_historic")["features"]:
    if not f["geometry"]: continue
    nm = f["properties"].get("name")
    if nm in ("Lop Nur", "Aral Sea"):
        g = shape(f["geometry"])
        if g.intersects(BASEBOX): LAKEG_OUT.append((nm, g.intersection(BASEBOX)))
LAKES = []
for n, g in LAKEG_OUT:
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
for cn in IM.CANALS:
    nm, mod, pts, note = cn[:4]
    it = add_item(dict(c="canal", old=nm, mod=mod, note=note, anc=list(LineString(pts).interpolate(0.5, normalized=True).coords[0])))
    CAN.append(dict(p=enc_ring(pts), it=it))
for nm, mod, pts, note, major in IM.RANGES:
    a = LineString(pts).interpolate(0.5, normalized=True)
    add_item(dict(c="range", old=nm, mod=mod, note=note, geo=pts, anc=[round(a.x, 3), round(a.y, 3)], major=bool(major)))
DES = []
for nm, mod, nename, note in IM.DESERTS:
    g = DESERTPOLY.get(nename)
    if g is None: print("  没找到荒漠", nename); continue
    g = g.intersection(EXT_BOX)
    c = g.representative_point()
    it = add_item(dict(c="desert", old=nm, mod=mod, note=note, anc=[round(c.x, 2), round(c.y, 2)]))
    for p in polys_of(g.simplify(0.05)):
        DES.append(dict(r=enc_ring(list(p.exterior.coords)), it=it))

for nm, mod, lo, la, st, yrs, note, at in IM.CAPITALS:
    assert st in UK, ("都城所属政权不存在", st)
    if at: assert at in SID, ("都城关联的归属点不存在", at)
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
for it in ITEMS:
    if "lon" in it: assert LON0 <= it["lon"] <= LON1 and LAT0 <= it["lat"] <= LAT1, ("条目在全图范围外", it["old"])

# 行军路线：每条一组 [经, 纬, 到达年, 地名]，前端按节点年份画出已走过的一段
ROUTES = []
for R in getattr(IM, "ROUTES", []):
    pts = [list(p) for p in R["pts"]]
    it = add_item(dict(c="route", old=R["name"], mod=R["mod"], note=R["note"], y=pts[0][2], y1=pts[-1][2],
                       yt=R.get("yt", f"{pts[0][2]}—{pts[-1][2]}"), anc=pts[len(pts) // 2][:2]))
    ROUTES.append(dict(it=it, pts=pts))

# 重要地域（燕云十六州）：m 是成员点（含 extra），各分区的 m 与 line（画不画分界线）。范围线、分界线与注记由统一引擎
# 按分区描（单仓 core/engine/，结果在本卷 engine.json 的 regions），不在这里算
REG_OUT = []
for R in getattr(IM, "REGIONS", []):
    ids = lambda names: [SID[n] for n in names]
    for n in R["members"] + R.get("extra", []): assert n in SID, ("地域成员不在 seeds.txt", n)
    groups = [dict(n=g["name"], y0=g.get("y0", R["y0"]), m=ids(g["members"] + g.get("extra", [])),
                   **({"line": True} if g.get("line") else {})) for g in R.get("groups", [])]
    it = add_item(dict(c="region", old=R["name"], mod=R["mod"], note=R["note"], tag=R.get("tag", ""), y0=R["y0"], y1=R.get("y1", 9999),
                       members=ids(R["members"])))
    REG_OUT.append(dict(it=it, y0=R["y0"], y1=R.get("y1", 9999), groups=groups, m=ids(R["members"] + R.get("extra", []))))
print("regions", [(ITEMS[r["it"]]["old"], [g["n"] for g in r["groups"]]) for r in REG_OUT])

# ======================================================================
# 输出
# ======================================================================
SEAS = [[n, lo, la, lv] for n, lo, la, lv in getattr(IM, "SEAS", [])]
GEO = dict(land=LAND_OUT, prov=PROV, border=BORDER, rivers=RIV_OUT, lakes=LAKES, canals=CAN, deserts=DES,
           snaps=OUTSN, regions=REG_OUT, routes=ROUTES, seas=SEAS, ext=[LON0, LON1, LAT0, LAT1], base=list(C.BASE_EXTENT), proj=list(C.PROJ))
UOUT = [dict(k=u["k"], n=u["n"], kind=u["kind"], note=u["note"]) for i, u in enumerate(UNITS)]
SOUT = [dict(id=s["id"], n=s["n"], mod=s["mod"], lon=s["lon"], lat=s["lat"], t=s["t"], **({"nm": s["names"]} if s["names"] else {})) for s in SEEDS]
DATA = dict(units=UOUT, seeds=SOUT, items=ITEMS)
C.BUILD.mkdir(exist_ok=True)
json.dump(GEO, open(C.BUILD / "geo.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
json.dump(DATA, open(C.BUILD / "data.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print("geo.json", (C.BUILD / "geo.json").stat().st_size // 1024, "KB; data.json", (C.BUILD / "data.json").stat().st_size // 1024, "KB")
