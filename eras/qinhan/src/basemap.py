# -*- coding: utf-8 -*-
"""底图：陆地、河流、湖泊、运河、荒漠、今国界、今省界，以及山川类条目（古名、今名、英文）。

  python src/basemap.py        生成 geodata/base.json（入库；底图不常改，平时构建不重跑）

中国本部（东经 72—136°、北纬 14—55°）的河湖、山川条目沿用汉末卷（读 eras/hanmosanguo/source.json），
范围以外补 Natural Earth 1:10m。黄河下游分两道：西汉河道（取战国卷的「古黄河」）画到 11 年河决魏郡为止，
此后是东汉河道（汉末卷的河道）；前132—前109 年另画瓠子决河南泛的一道。时间都是月序号（年 × 12 + 月 − 1）。
"""
import json
import sys
from pathlib import Path

import shapely
from shapely.geometry import shape, box, LineString, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
sys.path.insert(0, str(C.REPO / "core" / "v1"))
import legacy  # noqa: E402

BEGIN = -9999 * 12          # 「自古就有」：年 -9999（不用 v1 的 -999999，免得与旧格式「自始」的写法混淆）


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


def ne(name):
    return json.loads((C.NE / f"{name}.geojson").read_text(encoding="utf8"))["features"]


EXT = box(C.EXT[0], C.EXT[1], C.EXT[2], C.EXT[3])
HM = box(*C.HM_BOX)


def parts(g, kind):
    return [p for p in shapely.get_parts(g) if p.geom_type == kind and not p.is_empty]


# ---------------- 汉末卷的底图与山川条目 ----------------
def hanmo():
    G, D, _ = legacy.load("hanmosanguo")
    return G, D


DROP_CANAL = {"白沟", "利漕渠", "平虏渠", "泉州渠", "新河", "破冈渎"}          # 汉末以后才开
CANAL_Y0 = {"漕渠": -129, "灵渠": -214, "汴渠（汳水）": 69}                   # 开凿年份；其余视为本卷以前已有
DROP_ROAD = {"傥骆道", "阴平道"}                                              # 三国时才通行
ROAD_Y0 = {"褒斜道": -119, "子午道": 5}
DROP_PASS = {"濡须坞", "合肥新城", "牛渚", "沓中", "江油", "剑阁", "潼关"}     # 汉末三国才有


def physical_items(D):
    """汉末卷的河流、山脉、荒漠、运河、古道、关隘条目 → 本卷条目（时间换成月序号）。返回 (条目, 旧序号→新序号)"""
    keep, remap = [], {}
    for it in D["items"]:
        c = it["c"]
        if c not in ("river", "range", "desert", "canal", "road", "pass"):
            continue
        o = dict(it)
        if c == "canal":
            if o["old"] in DROP_CANAL:
                continue
            y = CANAL_Y0.get(o["old"])
            o["y0"] = BEGIN if y is None else y * 12
        if c == "road":
            if o["old"] in DROP_ROAD:
                continue
            y = ROAD_Y0.get(o["old"])
            if y is not None:
                o["y"] = y * 12
        if c == "pass" and o["old"] in DROP_PASS:
            continue
        remap[it["i"]] = len(keep)
        o["i"] = len(keep)
        keep.append(o)
    return keep, remap


# ---------------- 河流 ----------------
NE_RIV = {  # Natural Earth 名称 → 等级（只取汉末卷范围以外的部分）
    "Amu  Darya": "major", "Panj": "minor", "Syr  Darya": "major", "Naryn": "minor", "Zarafshon": "minor",
    "Murghob": "faint", "Harirud": "faint", "Helmand": "minor", "Indus": "minor", "Kabul": "faint",
    "Chu": "minor", "Talas": "faint", "Ili": "minor", "Irtysh": "minor", "Ob": "minor", "Yenisey": "major",
    "Angara": "minor", "Selenga": "minor", "Amur": "major", "Ussuri": "minor", "Lena": "minor",
    "Mekong": "major", "Chao Phraya": "minor", "Ayeyarwady": "minor", "Salween": "minor", "Ganges": "minor",
    "Sutlej": "faint", "Chenab": "faint", "Jhelum": "faint", "Ishim": "faint", "Tobol": "faint", "Ural": "minor",
}


def rivers(G, remap, items):
    out = []
    hh = {remap[i] for i, it in enumerate(hanmo_items) if it["c"] == "river" and it.get("mod") == "黄河" and i in remap}
    huang = next(iter(hh))
    for r in G["rivers"]:
        pts = dec(r["p"])
        o = {"k": r["k"], "p": enc(pts)}
        if r.get("it") is not None and r["it"] in remap:
            o["it"] = remap[r["it"]]
        # 东汉河道（汉末卷黄河下游，荥阳以东）：11 年河决魏郡以后
        if o.get("it") == huang and pts[0][0] > 113.5 and pts[-1][0] > 118:
            o["y0"] = 11 * 12
        out.append(o)
    # 西汉河道：战国卷的古黄河，到 11 年为止
    G2, _, _ = legacy.load("zhanguo")
    for r in G2["rivers"]:
        if (r.get("m") or "").startswith("古黄河"):
            out.append({"k": "major", "p": r["p"], "it": huang, "y1": 11 * 12 - 1})
    # 瓠子决口：前132 年河决瓠子，东南注巨野泽、通于淮泗，前109 年塞
    huzi = [(115.05, 35.72), (115.45, 35.55), (115.85, 35.42), (116.1, 35.35), (116.45, 35.05), (116.8, 34.7), (117.15, 34.3)]
    out.append({"k": "minor", "p": enc(huzi), "it": huang, "y0": -132 * 12, "y1": -109 * 12 + 11})
    # 汉末卷范围以外
    covered = shapely.union_all([LineString(dec(r["p"])) for r in G["rivers"] if len(r["p"]) >= 4]).buffer(0.12)
    for f in ne("ne_10m_rivers_lake_centerlines"):
        k = NE_RIV.get(f["properties"].get("name"))
        if not k:
            continue
        g = shape(f["geometry"]).intersection(EXT).difference(HM).difference(covered)
        for ln in parts(g, "LineString"):
            if ln.length < 0.3:
                continue
            out.append({"k": k, "p": enc(list(ln.simplify(0.02).coords))})
    return out


def lakes(G, remap):
    out = [dict(r=l["r"], **({"it": remap[l["it"]]} if l.get("it") in remap else {})) for l in G["lakes"]]
    for f in ne("ne_10m_lakes"):
        pr = f["properties"]
        if "Reservoir" in (pr.get("featurecla") or "") or (pr.get("name") or "").startswith("Aral"):
            continue
        g = shape(f["geometry"])
        if not g.intersects(EXT) or HM.contains(g.centroid):
            continue
        for p in parts(g, "Polygon"):
            if p.area >= 0.05:
                out.append({"r": enc(list(p.simplify(0.02).exterior.coords))})
    for f in ne("ne_10m_lakes_historic"):
        if "Aral" in (f["properties"].get("name") or ""):
            for p in parts(shape(f["geometry"]), "Polygon"):
                if p.area >= 0.05:
                    out.append({"r": enc(list(p.simplify(0.02).exterior.coords))})
    return out


def deserts(G, remap):
    out = [dict(r=d["r"], **({"it": remap[d["it"]]} if d.get("it") in remap else {})) for d in G["deserts"]]
    for f in ne("ne_10m_geography_regions_polys"):
        nm = (f["properties"].get("NAME") or "").upper()
        if nm in ("GARAGUM DESERT", "QIZILQUM DESERT"):
            for p in parts(shape(f["geometry"]).intersection(EXT), "Polygon"):
                if p.area >= 1:
                    out.append({"r": enc(list(p.simplify(0.1).exterior.coords))})
    return out


def land():
    polys = []
    for nm in ("ne_10m_land", "ne_10m_minor_islands"):
        for f in ne(nm):
            g = shape(f["geometry"])
            if g.intersects(EXT):
                polys += parts(g.intersection(EXT), "Polygon")
    u = shapely.union_all(polys)
    out = []
    for p in parts(u, "Polygon"):
        if p.area < 0.01:
            continue
        q = p.simplify(0.01, preserve_topology=True)
        rings = [enc(list(q.exterior.coords))] + [enc(list(r.coords)) for r in q.interiors if Polygon(r).area > 0.01]
        out.append(rings)
    return out


def border():
    out = []
    for f in ne("ne_10m_admin_0_boundary_lines_land"):
        g = shape(f["geometry"]).intersection(EXT)
        for ln in parts(g, "LineString"):
            if ln.length >= 0.05:
                out.append(enc(list(ln.simplify(0.015).coords)))
    return out


hanmo_items = []


def main():
    global hanmo_items
    G, D = hanmo()
    hanmo_items = D["items"]
    items, remap = physical_items(D)
    canals = [dict(p=c["p"], it=remap[c["it"]], y0=items[remap[c["it"]]]["y0"]) for c in G["canals"] if c["it"] in remap]
    base = dict(land=land(), prov=G["prov"], border=border(), rivers=rivers(G, remap, items), lakes=lakes(G, remap),
                canals=canals, deserts=deserts(G, remap), items=items,
                _note="由 src/basemap.py 生成：中国本部取汉末卷底图与山川条目，其外补 Natural Earth 1:10m；时间为月序号")
    C.GEODATA.mkdir(exist_ok=True)
    (C.GEODATA / "base.json").write_text(json.dumps(base, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print("   陆地", len(base["land"]), "河流", len(base["rivers"]), "湖泊", len(base["lakes"]), "运河", len(canals),
          "荒漠", len(base["deserts"]), "国界", len(base["border"]), "条目", len(items))


if __name__ == "__main__":
    main()
