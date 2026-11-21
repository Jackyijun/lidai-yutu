"""底图与点要素归属：读 content/，输出 build/geo.json（陆地、河湖、今省界、各节点、城邑等点要素的归属沿革）。

疆域不在这里算：页面上的疆域由统一疆域引擎按 content/seeds.txt 的归属推算（单仓 core/engine/，结果在本卷的 engine.json）。
本卷原来的栅格分区（代价栅格 + 多源最短路 + 描线）2026-11 架构整理第三批起退役。"""
import json, re, sys
from shapely.geometry import shape, box, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import unary_union
import config as C
sys.path.insert(0, str(C.CONTENT))
import features as F

NE = str(C.NE) + "/"
clipbox = box(*C.BBOX)

def enc_ring(coords, closed=True):
    out = []; px = py = 0
    pts = [(int(round(x * 100)), int(round(y * 100))) for x, y in coords]
    if closed and len(pts) > 1 and pts[0] == pts[-1]: pts = pts[:-1]
    dd = []
    for x, y in pts:
        if dd and (x, y) == (px, py): continue
        dd += [x - px, y - py]; px, py = x, y
    return dd

def polys_of(g):
    if g.is_empty: return []
    if isinstance(g, Polygon): return [g]
    if isinstance(g, MultiPolygon): return list(g.geoms)
    return [p for gg in getattr(g, "geoms", []) for p in polys_of(gg)]

def lines_of(g):
    if g.is_empty: return []
    if isinstance(g, LineString): return [g]
    if isinstance(g, MultiLineString): return list(g.geoms)
    return [l for gg in getattr(g, "geoms", []) for l in lines_of(gg)]

# ---------- 陆地 ----------
land_geoms = []
for fn in ["ne_10m_land.geojson", "ne_10m_minor_islands.geojson"]:
    for f in json.load(open(NE + fn))["features"]:
        g = shape(f["geometry"])
        if not g.intersects(clipbox): continue
        land_geoms.append(g.intersection(clipbox))
land = unary_union(land_geoms)
land_s = land.simplify(C.LAND_SIMPLIFY, preserve_topology=True)
LAND = []
for p in polys_of(land_s):
    if p.area < 0.004: continue
    LAND.append([enc_ring(p.exterior.coords)] + [enc_ring(i.coords) for i in p.interiors if Polygon(i).area > 0.004])
print("land polys", len(LAND), sum(len(r) for p in LAND for r in p) // 2, "pts")

# ---------- 种子 ----------
# 语法：名称 经度 纬度 初始归属 [年份归属 ...] [~年份]
#   “~-350” 表示该点从前350 起不再参与分区（为前350 以前的小国、戎狄补的点）。
seeds = []
for line in open(C.CONTENT / "seeds.txt", encoding="utf8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    parts = line.split()
    nm, lo, la = parts[0], float(parts[1]), float(parts[2])
    tl = [[-9999, None if parts[3] == "·" else parts[3]]]
    end = None
    for tok in parts[4:]:
        if tok.startswith("~"):
            end = int(tok[1:]); continue
        m = re.match(r"(-?\d+)(.+)", tok)
        tl.append([int(m.group(1)), None if m.group(2) == "·" else m.group(2)])
    seeds.append(dict(n=nm, lon=lo, lat=la, tl=tl, end=end))
print("seeds", len(seeds), "（其中前350 以前专用", sum(s["end"] is not None for s in seeds), "）")
def owner(tl, y):
    o = None
    for t, s in tl:
        if y >= t: o = s
    return o

# ---------- 河流 ----------
ne_riv = json.load(open(NE + "ne_10m_rivers_lake_centerlines.geojson"))["features"]
RIV = []
for f in ne_riv:
    p = f["properties"]; nm = p.get("name")
    if not f["geometry"]: continue
    g = shape(f["geometry"])
    if not g.intersects(clipbox): continue
    if p.get("featurecla") == "Lake Centerline" and nm not in ("Gan", "Yuan"): continue
    if nm in ("Hudi", "Huang", "Min", "Quan", "Ying", "Hai", "Jinsha", "Tongtian", "Zi") and nm != "Huang":
        if nm in ("Hudi", "Quan", "Ying", "Hai", "Tongtian", "Zi"): continue
        if nm == "Min" and g.bounds[0] < 110: continue
    for l in lines_of(g.intersection(clipbox)):
        ls = l.simplify(0.01)
        if nm == "Huang":
            # 以 113.1°E 为界：以西为“河”，以东为今黄河下游（古今异道）
            west = ls.intersection(box(90, 20, 113.1, 46)); east = ls.intersection(box(113.1, 20, 130, 46))
            for part in lines_of(west): RIV.append(dict(n="河", m="黄河", k="major", p=enc_ring(list(part.coords), False)))
            for part in lines_of(east): RIV.append(dict(n=None, m="今黄河下游", k="modern", p=enc_ring(list(part.coords), False)))
            continue
        if nm in F.NE_RIVERS:
            a, mo, note = F.NE_RIVERS[nm]
            kind = "major" if nm in ("Chang Jiang", "Yangtze", "Huai") else "minor"
            RIV.append(dict(n=a, m=mo, k=kind, note=note, p=enc_ring(list(ls.coords), False)))
        elif nm in F.NE_RIVERS_MINOR or nm is None:
            if ls.length < 0.4: continue
            RIV.append(dict(n=None, m=None, k="faint", p=enc_ring(list(ls.coords), False)))
for (a, mo, note, w, pts, kind) in F.MANUAL_RIVERS:
    RIV.append(dict(n=a, m=mo, k=kind, note=note, p=enc_ring(pts, False)))
CAN = []
for cn in F.CANALS:          # (名, 今名, 注, 点列) 或 (名, 今名, 开凿年, 注, 点列)
    a, mo, *mid, pts = cn
    d = dict(n=a, m=mo, note=mid[-1], p=enc_ring(pts, False))
    if len(mid) == 2: d["y"] = mid[0]
    CAN.append(d)

LAK = []
for f in json.load(open(NE + "ne_10m_lakes.geojson"))["features"]:
    nm = f["properties"].get("name")
    if nm not in F.NE_LAKES or not f["geometry"]: continue
    g = shape(f["geometry"]).simplify(0.01)
    for p in polys_of(g):
        c = p.representative_point()
        a, mo = F.NE_LAKES[nm]
        LAK.append(dict(n=a, m=mo, c=[round(c.x, 2), round(c.y, 2)], r=enc_ring(p.exterior.coords)))

# ---------- 今省界（简化，已预先编码） ----------
PROV = json.load(open(C.GEODATA / "prov.json", encoding="utf8"))

# ---------- 点要素所落的归属点 ----------
# 分区随年代可能不同（前350 起部分点退出），点要素的归属沿革按各段拼接。各点在各段落在哪个归属点写在
# content/links.txt（架构整理第三批起冻结，不再按旧构建的分区格子查），沿革取那个归属点在 seeds.txt 里的归属沿革
_starts = [-9999] + sorted({s["end"] for s in seeds if s["end"] is not None})
SIDX = {s["n"]: i for i, s in enumerate(seeds)}
assert len(SIDX) == len(seeds), "seeds.txt 里有重名的归属点"
LINKS = {}
for line in open(C.CONTENT / "links.txt", encoding="utf8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    parts = line.split()
    try:
        segs = [[-9999, parts[1]]] + [[int(y), n] for y, n in (tok.split(":", 1) for tok in parts[2:])]
    except (IndexError, ValueError):
        sys.exit(f"content/links.txt 这一行写得不对（应为「键 归属点 [年份:归属点 …]」）：{line}")
    if parts[0] in LINKS: sys.exit(f"content/links.txt：{parts[0]} 写了两遍")
    ys = [y for y, _ in segs[1:]]
    if ys != sorted(set(ys)) or any(y not in _starts[1:] for y in ys):
        sys.exit(f"content/links.txt：{parts[0]} 的年份只能是分区换段的年份 {_starts[1:]}，且从早到晚")
    for y, n in segs:
        if n not in SIDX: sys.exit(f"content/links.txt：{parts[0]} 写的归属点「{n}」不在 seeds.txt 里")
    LINKS[parts[0]] = segs
def seed_at(key):
    if key not in LINKS:
        sys.exit(f"content/links.txt 里没有「{key}」：新加的点要写明落在哪个归属点")
    out = []
    for i, y0 in enumerate(_starts):
        y1 = _starts[i + 1] if i + 1 < len(_starts) else 10 ** 6
        s = seeds[SIDX[owner(LINKS[key], y0)]]
        if s["end"] is not None and y0 >= s["end"]:
            sys.exit(f"content/links.txt：{key} 在 {y0} 年起落在「{s['n']}」，这个归属点那时已不参与分区（~{s['end']}）")
        tl = s["tl"]
        for t, o in [[y0, owner(tl, y0)]] + [[t, o] for t, o in tl if y0 < t < y1]:
            if not out or out[-1][1] != o: out.append([t, o])
    return out

def tl_str(tl): return ";".join(f"{t}:{s or ''}" for t, s in tl)

# ---------- 节点 ----------
# 只出年份、标题、概述（assemble.py 另补别名、英文）；live 是当年有疆域的国（占着参与分区的归属点），
# 当年别名只给这些国标（原先看旧分区里这国有没有格子，两者一致）
SN = []
for (y, title, desc) in F.SNAPS:
    live = sorted({owner(s["tl"], y) for s in seeds if owner(s["tl"], y) and (s["end"] is None or y < s["end"])})
    SN.append(dict(y=y, t=title, d=desc, live=live))

OUT = dict(land=LAND, prov=PROV, rivers=RIV, canals=CAN, lakes=LAK, snaps=SN)
if getattr(F, "FIRST", None) is not None: OUT["first"] = F.FIRST     # 首屏节点年份
pts_owner = {}
for grp in (F.CAPITALS, F.CITIES, F.PASSES, F.BATTLES, F.CULTURE, F.TOWNS):
    for it in grp:
        pts_owner[it[0] + "@" + str(it[2])] = tl_str(seed_at(it[0] + "@" + str(it[2])))
for it in getattr(F, "JUN", []):
    pts_owner["郡:" + it[0]] = tl_str(seed_at("郡:" + it[0]))
stale = sorted(set(LINKS) - set(pts_owner))
if stale: sys.exit("content/links.txt 里这些点已不在 features.py：" + "、".join(stale))
OUT["own"] = pts_owner
C.BUILD.mkdir(exist_ok=True)
json.dump(OUT, open(C.BUILD / "geo.json", "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
print("geo.json", (C.BUILD / "geo.json").stat().st_size // 1024, "KB")
