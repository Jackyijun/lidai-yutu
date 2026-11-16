# -*- coding: utf-8 -*-
"""第 4 步：统一投影、全球底图、地形晕渲的共用部分。

  load()              读 core/geo/config.toml
  proj() / inv()      统一 Albers 投影（numpy），与前端 proj() 同一组数
  era_boxes(b)        由 v1 数据包算出一卷的「全图」范围（晕渲取这一块）与陆地范围（全球底图挖掉这一块）
  apply(slug, G)      出页面时把 geodata/relief/<短名>/、geodata/world/<短名>.json 并入 GEO，
                      本卷陆地被范围切出的长直边加密，投影改成统一的一组数
"""
import base64, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RELIEF = ROOT / "geodata" / "relief"
WORLD = ROOT / "geodata" / "world"

try:
    import tomllib
except ImportError:                       # Python 3.10 及以下：pip install tomli
    import tomli as tomllib

_CFG = None


def load():
    global _CFG
    if _CFG is None:
        _CFG = tomllib.loads((HERE / "config.toml").read_text(encoding="utf8"))
    return _CFG


def consts():
    c = load()["projection"]
    p1, p2 = c["parallels"]; l0, b0 = c["center"]
    rad = math.pi / 180
    nn = (math.sin(p1 * rad) + math.sin(p2 * rad)) / 2
    cc = math.cos(p1 * rad) ** 2 + 2 * nn * math.sin(p1 * rad)
    rho0 = math.sqrt(cc - 2 * nn * math.sin(b0 * rad)) / nn
    return dict(p1=p1, p2=p2, l0=l0, b0=b0, nn=nn, cc=cc, rho0=rho0, scl=c["scale"], seam=c["seam"])


def proj(lon, lat):
    import numpy as np
    k = consts(); rad = math.pi / 180
    lon = np.where(lon < k["seam"], lon + 360, lon)
    r = np.sqrt(np.maximum(k["cc"] - 2 * k["nn"] * np.sin(lat * rad), 1e-9)) / k["nn"]
    th = k["nn"] * (lon - k["l0"]) * rad
    return r * np.sin(th) * k["scl"], -(k["rho0"] - r * np.cos(th)) * k["scl"]


def inv(x, y):
    import numpy as np
    k = consts(); rad = math.pi / 180
    X, Y = x / k["scl"], -y / k["scl"]
    rr = np.hypot(X, k["rho0"] - Y)
    th = np.arctan2(X, k["rho0"] - Y)
    lat = np.arcsin(np.clip((k["cc"] - rr * rr * k["nn"] ** 2) / (2 * k["nn"]), -1, 1)) / rad
    return k["l0"] + th / k["nn"] / rad, lat


def km_per_unit():
    return 6371.0 / consts()["scl"]


# ---------------- 范围 ----------------
def _rings(land):
    for poly in land:
        for r in poly:
            x = y = 0; pts = []
            for i in range(0, len(r) - 1, 2):
                x += r[i]; y += r[i + 1]; pts.append((x, y))
            yield pts


def land_bbox(land):
    xs, ys = [], []
    for pts in _rings(land):
        xs += [p[0] for p in pts]; ys += [p[1] for p in pts]
    return [min(xs) / 100, max(xs) / 100, min(ys) / 100, max(ys) / 100]


def era_boxes(b):
    """返回 (ext, box)：ext 本卷「全图」范围，box 本卷陆地范围（西、东、南、北）。"""
    land = b["base"]["land"]
    lb = land_bbox(land)
    ex = b.get("extent") or {}
    ext = list(ex["ext"]) if ex.get("ext") else lb
    box = list(ex["base"]) if ex.get("base") else lb
    return [float(v) for v in ext], [float(v) for v in box]


# ---------------- 出页面 ----------------
def densify(land, seg):
    """长边按 seg 度加点（整数插值，结果确定）。本卷陆地被范围切出的直边可长达几十度，
    不加点的话投影后成了弦，和全球底图的弧之间会露出一道海。"""
    lim = round(seg * 100)
    out = []
    for poly in land:
        po = []
        for r in poly:
            pts = []; x = y = 0
            for i in range(0, len(r) - 1, 2):
                x += r[i]; y += r[i + 1]; pts.append((x, y))
            if pts and pts[0] != pts[-1]: pts.append(pts[0]); closed = False
            else: closed = True
            dense = [pts[0]]
            for (a, bq), (c, d) in zip(pts, pts[1:]):
                n = max(1, math.ceil(max(abs(c - a), abs(d - bq)) / lim))
                for j in range(1, n + 1):
                    dense.append((a + round((c - a) * j / n), bq + round((d - bq) * j / n)))
            if not closed: dense.pop()
            flat = [dense[0][0], dense[0][1]]
            for (a, bq), (c, d) in zip(dense, dense[1:]):
                flat += [c - a, d - bq]
            po.append(flat)
        out.append(po)
    return out


def apply(slug, G):
    """把第 4 步的数据并入页面的 GEO（旧版回读核对时不调用）。"""
    cfg = load()
    p = cfg["projection"]
    if "proj" in G:                              # 宋元、民国把投影参数存在 GEO.proj（民国的前端直接读它）
        G["proj"] = [p["parallels"][0], p["parallels"][1], p["center"][1], p["center"][0]]
    G["land"] = densify(G["land"], cfg["world"]["segment"])
    wf = WORLD / f"{slug}.json"
    idx = RELIEF / slug / "index.json"
    if not wf.exists() or not idx.exists():
        raise SystemExit(f"缺少 {wf.relative_to(ROOT)} 或 {idx.relative_to(ROOT)}：先运行 python run.py --geo")
    G["world"] = json.loads(wf.read_text(encoding="utf8"))
    hill = []
    for L in json.loads(idx.read_text(encoding="utf8"))["layers"]:
        data = (RELIEF / slug / L["file"]).read_bytes()
        hill.append(dict(km=L["km"], x=L["x"], y=L["y"], w=L["w"], h=L["h"],
                         src="data:image/webp;base64," + base64.b64encode(data).decode()))
    G["hill"] = hill
    return G
