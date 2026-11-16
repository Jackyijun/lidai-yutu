# -*- coding: utf-8 -*-
"""全球底图：各卷范围以外的陆地与大湖（geodata/world/<短名>.json，入库）。

  python core/geo/world.py [短名 ...]     不写短名则各卷全做；需要先有 build/v1/<短名>.json

全球陆地用 Natural Earth 1:50m、大湖用 1:10m（geodata/ne/ 已随仓库附带），化简后只存一份；
各卷挖掉本卷陆地范围（那里仍用本卷自己的 1:10m 陆地；挖时向里缩 0.1°，让两块陆地叠一窄条，拼接处不露缝），按接缝（config.toml 的 seam）切开、西半边东移 360°，
南极洲不画，长边加密。海岸线不另存：前端从多边形描出——本卷陆地跳过落在范围边上的切边，
全球陆地跳过落在本卷范围以内的部分（叠着的那一窄条与切边），两者都跳过接缝上的切边。

文件格式：{"box": [西, 东, 南, 北], "fill": [[环, …], …], "lakes": [环, …]}，环是「经纬度 × 100 取整后的差分数组」。
"""
import json, sys
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import shape, box as Box, Polygon, MultiPolygon
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import geo

ROOT = geo.ROOT
V1 = ROOT / "build" / "v1"
_CACHE = {}


def shift(g):
    w = geo.load()["world"]; seam = geo.load()["projection"]["seam"]
    east = g.intersection(Box(seam, w["south"], 180, 90))
    west = g.intersection(Box(-180, w["south"], seam, 90))
    west = shapely.transform(west, lambda c: c + np.array([360, 0]))
    return unary_union([east, west])


def polys(g):
    if g.is_empty: return []
    return [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if isinstance(p, Polygon) and not p.is_empty]


def world():
    if "w" in _CACHE: return _CACHE["w"]
    w = geo.load()["world"]
    fs = json.loads((ROOT / w["land"]).read_text(encoding="utf8"))["features"]
    land = shift(unary_union([shape(f["geometry"]) for f in fs]).buffer(0)).simplify(w["simplify"], preserve_topology=True)
    land = MultiPolygon([p for p in polys(land) if p.area >= w["min_area"]])
    fs = json.loads((ROOT / w["lakes"]).read_text(encoding="utf8"))["features"]
    lk = [g for g in (shape(f["geometry"]).buffer(0) for f in fs) if g.area >= w["lake_area"]]
    lakes = shift(unary_union(lk)).simplify(w["simplify"], preserve_topology=True)
    lakes = MultiPolygon([p for p in polys(lakes) if p.area >= w["lake_area"] * .5])
    _CACHE["w"] = (land, lakes)
    return land, lakes


def enc(coords):
    a = np.rint(np.asarray(coords)[:, :2] * 100).astype(np.int64)
    return np.vstack([a[:1], np.diff(a, axis=0)]).ravel().tolist()


def era(slug):
    w = geo.load()["world"]
    b = json.loads((V1 / f"{slug}.json").read_text(encoding="utf8"))
    _, bx = geo.era_boxes(b)
    land, lakes = world()
    o = w["overlap"]                       # 伸进本卷范围一点，压在本卷陆地下面，拼接处不露缝
    B = Box(bx[0] + o, bx[2] + o, bx[1] - o, bx[3] - o)
    out = shapely.segmentize(land.difference(B), w["segment"])
    fill = [[enc(p.exterior.coords)] + [enc(r.coords) for r in p.interiors] for p in polys(out)]
    lk = [enc(p.exterior.coords) for p in polys(shapely.segmentize(lakes.difference(B), w["segment"]))]
    res = dict(box=[round(v, 2) for v in bx], fill=fill, lakes=lk)
    geo.WORLD.mkdir(parents=True, exist_ok=True)
    s = json.dumps(res, separators=(",", ":"))
    (geo.WORLD / f"{slug}.json").write_text(s + "\n", encoding="utf8")
    print(f"{slug:20s} 范围 {bx}  陆地 {len(fill)} 块  大湖 {len(lk)} 个  {len(s) / 1e3:.0f} KB")


def main(slugs):
    for s in slugs: era(s)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    from run import SLUGS
    main(sys.argv[1:] or SLUGS)
