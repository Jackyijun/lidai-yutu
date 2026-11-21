# -*- coding: utf-8 -*-
"""归属回归：新引擎的疆域与各卷现有页面（v1 数据包里的几何）逐节点比对。

  python core/engine/regress.py suitang      报告写到 build/engine/<短名>.regress.json，并打印摘要

  1. 点：每个归属点是否落在本方（own）疆域内——新旧各查一遍；
  2. 面：陆地上新旧归属不同的面积占比，逐节点、逐单位；
  3. 线：陆上界线里的长直线段（3° 视野里一眼能看出的直线），新旧各数一遍；
  4. 缝：相邻疆域之间的白缝与叠色（覆盖图是否有效）。
"""
import json
import sys
from functools import reduce
from pathlib import Path

import numpy as np
import shapely

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grid as GR          # noqa: E402
from grid import geo       # noqa: E402
import data as DA          # noqa: E402
import cost as CO          # noqa: E402

ROOT = GR.ROOT
import os
OUT = Path(os.environ["ENGINE_OUT"]) if os.environ.get("ENGINE_OUT") else ROOT / "build" / "engine"


def geom_ll(rings):
    ps = [shapely.Polygon(DA.dec(r)) for r in rings]
    ps = [p if p.is_valid else p.buffer(0) for p in ps]
    return reduce(lambda a, b: a.symmetric_difference(b), ps) if ps else shapely.Polygon()


def geom_xy(rings):
    ps = []
    for r in rings:
        a = np.array(DA.dec(r))
        x, y = geo.proj(a[:, 0], a[:, 1])
        p = shapely.Polygon(np.c_[x, y]); ps.append(p if p.is_valid else p.buffer(0))
    return reduce(lambda a, b: a.symmetric_difference(b), ps) if ps else shapely.Polygon()


def raster(win, gs, keep):
    lab = np.full(win.shape, -1, np.int32)
    for k, g in gs.items():
        if g.is_empty:                     # 旧页面偶有画不出来的单位（环太小）
            continue
        m = CO.mask_of(win, [g])
        lab[m & keep] = k
    return lab


def straight(win, g, land, inner_far, km=20.0):
    """陆上（离外缘 2 格以外）长于 km 的线段数与最长者（km）"""
    n, mx = 0, 0.0
    for p in shapely.get_parts(g):
        for r in [p.exterior] + list(p.interiors):
            a = np.asarray(r.coords)
            L = np.hypot(*np.diff(a, axis=0).T) * GR.KM
            mid = (a[1:] + a[:-1]) / 2
            rr, cc = win.rc(mid[:, 0], mid[:, 1])
            rr = np.clip(np.rint(rr).astype(int), 0, win.nj - 1); cc = np.clip(np.rint(cc).astype(int), 0, win.ni - 1)
            on = land[rr, cc] & inner_far[rr, cc]
            if on.any():
                Lo = L[on]
                n += int((Lo > km).sum()); mx = max(mx, float(Lo.max()))
    return n, mx


def old_bundle(slug):
    """比对的「旧」一方：一般就是 v1 数据包；疆域已换到引擎的卷（第 7 步），v1 里已是引擎的几何，改取 legacy.html 里旧引擎画的"""
    sys.path.insert(0, str(ROOT / "core" / "v1"))
    import engine_geom
    if not engine_geom.migrated(slug):
        return DA.bundle(slug)
    import legacy
    html = (ROOT / "eras" / slug / "legacy.html").read_text(encoding="utf8")
    return legacy.to_v1(slug, *legacy.extract(html))


def run(slug):
    b = old_bundle(slug)
    new = json.loads((OUT / f"{slug}.json").read_text(encoding="utf8"))
    z = np.load(OUT / f"{slug}.npz")
    i0, j0, ni, nj = new["meta"]["window"]
    win = GR.Window.__new__(GR.Window)
    win.cell = new["meta"]["cell"]; win.i0, win.j0, win.ni, win.nj = i0, j0, ni, nj; win.shape = (nj, ni)
    land = z["land"]
    import build as BU
    _, _, _, _, reg = BU.setup(slug)
    keep = land & CO.mask_of(win, [reg])
    far = CO.mask_of(win, [reg.buffer(-2 * win.cell)])
    S, V = DA.view(slug)
    names = {str(i): p["n"] for i, p in enumerate(b["polities"])}

    rep = {"era": slug, "nodes": []}
    tot_ch = tot_land = 0
    for on, nn, vw in zip(b["nodes"], new["nodes"], V):
        assert on["t"] == nn["t"] == vw[0]
        units = sorted(set(on["u"]) | set(nn["u"]), key=lambda u: (len(u), u))
        old_ll = {u: geom_ll(b["geom"][on["u"][u]]) for u in on["u"]}
        new_ll = {u: geom_ll(new["geom"][nn["u"][u]]) for u in nn["u"]}
        # 1 点
        miss = {"old": [], "new": []}
        for i, (lon, lat, key) in enumerate(S):
            u = vw[1][i]
            if u is None or (vw[3] is not None and not vw[3][i]):
                continue
            for tag, G in (("old", old_ll), ("new", new_ll)):
                if u not in G or not G[u].contains(shapely.Point(lon, lat)):
                    hit = [k for k, g in G.items() if g.contains(shapely.Point(lon, lat))]
                    miss[tag].append([key, names[u], names[hit[0]] if hit else None])
        # 2 面
        code = {u: k for k, u in enumerate(units)}
        old_xy = {code[u]: geom_xy(b["geom"][on["u"][u]]) for u in on["u"]}
        new_xy = {code[u]: geom_xy(new["geom"][nn["u"][u]]) for u in nn["u"]}
        lo, ln = raster(win, old_xy, keep), raster(win, new_xy, keep)
        own = (lo >= 0) | (ln >= 0)
        ch = own & (lo != ln)
        cell_km2 = win.km() ** 2
        per = []
        for u in units:
            k = code[u]
            a, bb = int((lo == k).sum()), int((ln == k).sum())
            d = int((ch & ((lo == k) | (ln == k))).sum())
            if a or bb:
                per.append([names[u], round(a * cell_km2), round(bb * cell_km2), round(d / max(a, bb, 1), 3)])
        per.sort(key=lambda x: -x[3])
        # 3 线
        so = [straight(win, g, land, far) for g in old_xy.values()]
        sn = [straight(win, g, land, far) for g in new_xy.values()]
        # 4 缝
        gl = [g for g in new_xy.values()]
        gap_ok = bool(shapely.coverage_is_valid(np.array(gl, dtype=object), gap_width=0.3))
        unc = int((keep & (ln < 0) & (lo >= 0)).sum())
        rec = {"t": on["t"], "title": on["title"],
               "changed": round(float(ch.sum()) / max(1, int(own.sum())), 4),
               "miss_old": miss["old"], "miss_new": miss["new"],
               "straight_old": [sum(x[0] for x in so), round(max(x[1] for x in so), 1)],
               "straight_new": [sum(x[0] for x in sn), round(max(x[1] for x in sn), 1)],
               "coverage_valid": gap_ok, "uncovered_cells": unc, "units": per[:8]}
        rep["nodes"].append(rec)
        tot_ch += int(ch.sum()); tot_land += int(own.sum())
        print(f"{on['t'] // 12}.{on['t'] % 12 + 1:02d} {on['title'][:14]:14s} 变 {rec['changed'] * 100:4.1f}%  "
              f"点出界 旧{len(miss['old'])} 新{len(miss['new'])}  直线>20km 旧{rec['straight_old'][0]} 新{rec['straight_new'][0]}"
              f"（最长 {rec['straight_old'][1]} / {rec['straight_new'][1]} km）  覆盖{'有效' if gap_ok else '有缝'}  漏格 {unc}", flush=True)
    rep["changed"] = round(tot_ch / max(1, tot_land), 4)
    print(f"合计：陆地归属变化 {rep['changed'] * 100:.2f}%")
    (OUT / f"{slug}.regress.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf8")
    return rep


if __name__ == "__main__":
    for s in sys.argv[1:] or ["suitang"]:
        run(s)
