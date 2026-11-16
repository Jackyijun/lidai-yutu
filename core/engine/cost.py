# -*- coding: utf-8 -*-
"""通行代价栅格（规范第十三节第 2 条）。

代价 = (1 + 坡度 + 高原 + 山脊带 + 界河) × (1 ± 噪声)。地形、山脊、噪声只由位置决定；
界河与大湖取节点所在时代那一卷画的（历代改道）。所有平滑都多算一圈边距，同一格在任何窗口里结果相同。
"""
import gzip
import math
import zlib

import numpy as np
import shapely
from scipy import ndimage
from shapely.geometry import LineString

import grid as GR
from grid import cfg, geo

ROOT = GR.ROOT
ETOPO = ROOT / "geodata" / "etopo20"


def to_xy(g):
    g = shapely.transform(g, lambda a: np.column_stack(geo.proj(a[:, 0], a[:, 1])))
    return g if g.is_valid else shapely.make_valid(g)


def mask_of(win, polys_xy):
    """投影坐标多边形 → 布尔栅格（格心在内）"""
    m = np.zeros(win.shape, bool)
    if not polys_xy:
        return m
    u = shapely.union_all(polys_xy)
    shapely.prepare(u)
    xmin, ymin, xmax, ymax = u.bounds
    r0, c0 = win.rc(xmin, ymin); r1, c1 = win.rc(xmax, ymax)
    r0, c0 = max(0, int(math.floor(r0))), max(0, int(math.floor(c0)))
    r1, c1 = min(win.nj, int(math.ceil(r1)) + 1), min(win.ni, int(math.ceil(c1)) + 1)
    if r1 <= r0 or c1 <= c0:
        return m
    x, y = win.xy(np.arange(r0, r1)[:, None], np.arange(c0, c1)[None, :])
    x, y = np.broadcast_arrays(x, y)
    m[r0:r1, c0:c1] = shapely.contains_xy(u, x, y)
    return m


def bbox_ll(win, margin=2.0):
    """窗口对应的经纬度范围（外扩 margin 度）"""
    r = np.r_[np.linspace(0, win.nj, 60), np.full(60, win.nj), np.linspace(win.nj, 0, 60), np.zeros(60)]
    c = np.r_[np.zeros(60), np.linspace(0, win.ni, 60), np.full(60, win.ni), np.linspace(win.ni, 0, 60)]
    lon, lat = geo.inv(*win.xy(r, c))
    return lon.min() - margin, lon.max() + margin, max(-89.0, lat.min() - margin), min(89.0, lat.max() + margin)


# ---------------- 地形 ----------------
_ET = None


def etopo():
    global _ET
    if _ET is None:
        z = np.loadtxt(gzip.open(ETOPO / "etopo20data.gz"))
        lo = np.loadtxt(gzip.open(ETOPO / "etopo20lons.gz")); la = np.loadtxt(gzip.open(ETOPO / "etopo20lats.gz"))
        _ET = (z, lo, la)
    return _ET


def terrain(win, land_m, margin):
    """地形项（窗口外扩 margin 格计算再裁回）：坡度、高原（隋唐式），起伏、高海拔（宋元式），各项权重为 0 即不用"""
    C = cfg()["cost"]
    z, lo, la = etopo()
    rel = ndimage.maximum_filter(z, 3) - ndimage.minimum_filter(z, 3)
    W = GR.Window.__new__(GR.Window)
    W.__dict__.update(win.__dict__)
    W.i0 -= margin; W.j0 -= margin; W.ni += 2 * margin; W.nj += 2 * margin; W.shape = (W.nj, W.ni)
    lon, lat = W.lonlat()
    lon = (lon - lo[0]) % 360 + lo[0]
    fi = (lon - lo[0]) / (lo[1] - lo[0]); fj = (lat - la[0]) / (la[1] - la[0])
    elev = ndimage.map_coordinates(z, [fj, fi], order=1, mode="nearest")
    elev = np.maximum(elev, 0)                # 海面以下一律当 0（陆地上的洼地也按平地算）
    gy, gx = np.gradient(ndimage.gaussian_filter(elev, C["slope_sigma"], mode="nearest"))
    slope = np.hypot(gx, gy) / win.km()       # 米/公里
    lo_, hi_, add = C["plateau"]
    t = C["slope"] * np.clip(slope, 0, C["slope_max"]) + add * np.clip((elev - lo_) / (hi_ - lo_), 0, 1)
    k, cap = C["relief"]
    if k:                                     # ETOPO20 3×3 窗口内高差（每千米加 k，上限 cap 千米）
        rv = ndimage.map_coordinates(rel, [fj, fi], order=1, mode="nearest")
        t = t + k * np.clip(rv / 1000, 0, cap)
    h0, k, cap = C["high"]
    if k:                                     # 高海拔：h0 米以上每千米加 k
        t = t + k * np.clip((elev - h0) / 1000, 0, cap)
    return t[margin:margin + win.nj, margin:margin + win.ni]


# ---------------- 山脊 ----------------
def wiggle(pts_ll, name):
    """手绘脊线加密，按名字定相位横向摆动（投影平面内），两端不动"""
    amp_km, wave_km = cfg()["cost"]["ridge"]["wiggle"]
    ls = LineString(pts_ll)
    n = max(2, int(ls.length / 0.04))
    P = np.array([ls.interpolate(i / n, normalized=True).coords[0] for i in range(n + 1)])
    x, y = geo.proj(P[:, 0], P[:, 1])
    dx = np.gradient(x); dy = np.gradient(y); L = np.hypot(dx, dy) + 1e-9
    s = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))] * GR.KM
    h = zlib.crc32(name.encode("utf8"))
    ph1 = (h % 1000) / 1000 * 2 * math.pi; ph2 = (h // 1000 % 1000) / 1000 * 2 * math.pi
    off = (np.sin(2 * math.pi * s / wave_km + ph1) + .5 * np.sin(2 * math.pi * s / (wave_km / 2.3) + ph2)) * amp_km / 1.5
    taper = np.minimum(1, np.minimum(s, s[-1] - s) / (wave_km / 2))
    off = off * taper / GR.KM
    return x - dy / L * off, y + dx / L * off


def band(win, lines_xy, sigma_km, margin):
    m = GR.burn(win, lines_xy, margin=margin)
    b = GR.gauss_band(m, sigma_km / win.km())
    return b[margin:margin + win.nj, margin:margin + win.ni], m[margin:margin + win.nj, margin:margin + win.ni]


def range_polys(win, bb):
    """Natural Earth 山地多边形整体加一点代价（唐宋、宋元先例）"""
    w, blur = cfg()["cost"]["range_poly"]
    if not w:
        return 0
    import data as DA
    W, E, S, N = bb
    ps = []
    for g in DA.ne_ranges():
        x0, y0, x1, y1 = g.bounds
        for sh in (0, 360):
            if x1 + sh >= W and x0 + sh <= E and y1 >= S and y0 <= N:
                ps.append(to_xy(shapely.transform(g, lambda a, sh=sh: a + [sh, 0])))
    m = int(4 * blur) + 4
    big = GR.Window.__new__(GR.Window); big.__dict__.update(win.__dict__)
    big.i0 -= m; big.j0 -= m; big.ni += 2 * m; big.nj += 2 * m; big.shape = (big.nj, big.ni)
    f = ndimage.gaussian_filter(mask_of(big, ps).astype(float), blur, mode="constant")
    return w * f[m:m + win.nj, m:m + win.ni]


def ridges(win, rng_list, bb):
    R = cfg()["cost"]["ridge"]
    W, E, S, N = bb
    major, minor = [], []
    for gid, mj, pts in rng_list:
        a = np.array(pts, float)
        if np.hypot(*np.diff(a, axis=0).T).sum() < R["min_len"]:
            continue
        if a[:, 0].max() < W or a[:, 0].min() > E or a[:, 1].max() < S or a[:, 1].min() > N:
            continue
        (major if mj else minor).append(wiggle(pts, gid))
    smaj, smin = R["sigma_km"]
    m = int(4 * max(smaj, smin) / win.km()) + 4
    bmaj, _ = band(win, major, smaj, m)
    bmin, _ = band(win, minor, smin, m)
    return np.maximum(R["major"] * bmaj, R["minor"] * bmin), len(major), len(minor)


def rivers(win, riv):
    """riv: {全局 ID: [[(经, 纬)], …]} → (代价项, 界河格)"""
    R = cfg()["cost"]["river"]
    m = int(4 * R["sigma_km"] / win.km()) + 4
    out = np.zeros(win.shape); hit = np.zeros(win.shape, bool)
    for gid, lines in sorted(riv.items()):
        xy = [geo.proj(np.array(l)[:, 0], np.array(l)[:, 1]) for l in lines if len(l) > 1]
        b, h = band(win, xy, R["sigma_km"], m)
        out = np.maximum(out, R["weights"][gid] * b); hit |= h
    return out, hit


def wall_band(win, lines_ll, amp, width_km, margin):
    """墙：amp × exp(-(d / width)²)（d 为到墙线的距离，km）；返回 (代价项, 墙格)"""
    if not lines_ll:
        return np.zeros(win.shape), np.zeros(win.shape, bool)
    xy = [geo.proj(np.array(l)[:, 0], np.array(l)[:, 1]) for l in lines_ll if len(l) > 1]
    m = GR.burn(win, xy, margin=margin)
    d = ndimage.distance_transform_edt(~m) * win.km()
    b = amp * np.exp(-(d / width_km) ** 2)
    return b[margin:margin + win.nj, margin:margin + win.ni], m[margin:margin + win.nj, margin:margin + win.ni]


def carve(win, pts_xy):
    """归属点周围不烧墙：carve[0] km 内为 0，到 carve[1] km 恢复全强度（贴着国界的城镇不被墙带围住）"""
    a, b = cfg()["walls"]["carve"]
    m = np.zeros(win.shape, bool)
    for x, y in pts_xy:
        r, c = win.rc(x, y); r, c = int(round(float(r))), int(round(float(c)))
        if 0 <= r < win.nj and 0 <= c < win.ni:
            m[r, c] = True
    d = ndimage.distance_transform_edt(~m) * win.km()
    return np.clip((d - a) / (b - a), 0, 1)


def noise(win):
    N = cfg()["cost"]["noise"]
    acc = np.zeros(win.shape)
    for k, (s, w) in enumerate(N["scales"]):
        acc += w * win.smooth_noise(1 + k, s)
    acc /= math.sqrt(sum(w * w for _, w in N["scales"]))
    return np.clip(acc, -N["clip"], N["clip"]) / N["clip"]


def build(win, land_ll, lakes_ll, rng_list, riv, walls=None, pts_xy=(), log=print):
    """返回 dict：cost（常设部分）、var（有时效的墙：[(名称, 代价项, 起月, 止月)]）、land（可通行陆地）、lake（大湖）、
    river（界河格）、wall（墙格）、land_xy（投影陆地多边形，供注记取点）"""
    C = cfg()["cost"]
    land_xy = [to_xy(p) for p in land_ll]
    LAND = mask_of(win, land_xy)
    # 比一格还小的岛（太平洋上的环礁等）格心未必落在岛上：每块陆地至少占它所在的那一格
    for p in land_xy:
        for q in shapely.get_parts(p):
            if q.is_empty:
                continue
            pt = q.point_on_surface()
            r, c = win.rc(pt.x, pt.y); r, c = int(round(float(r))), int(round(float(c)))
            if 0 <= r < win.nj and 0 <= c < win.ni:
                LAND[r, c] = True
    big = [to_xy(p) for p in lakes_ll if p.area > C["big_lake"]]
    LAKE = mask_of(win, big) & LAND
    LAND &= ~LAKE
    log("陆地格", int(LAND.sum()), "大湖格", int(LAKE.sum()))
    t = terrain(win, LAND, 8)
    bb = bbox_ll(win)
    r, nmaj, nmin = ridges(win, rng_list, bb)
    rv, hit = rivers(win, riv)
    log("山脊", nmaj, "主干", nmin, "次要；界河", len(riv), "条")
    nz = 1 + C["noise"]["amp"] * noise(win)
    wall = np.zeros(win.shape, bool); wl = np.zeros(win.shape); var = []
    if walls:
        Wc = cfg()["walls"]
        m = int(3 * Wc["width_km"] / win.km()) + 4
        cv = carve(win, pts_xy)
        b, wall = wall_band(win, walls["fixed"], Wc["peak"], Wc["width_km"], m)
        bp, _ = wall_band(win, walls["prov"], Wc["prov"][0], Wc["prov"][1], m)
        wl = (b + bp) * cv
        for name, lines, t0, t1 in walls["var"]:
            bv, mv = wall_band(win, lines, Wc["peak"], Wc["width_km"], m)
            var.append((name, np.round(bv * cv * nz, 6), mv, t0, t1))
        log("国界墙", len(walls["fixed"]), "段；省界", len(walls["prov"]), "段；有时效的墙", [v[0] for v in walls["var"]])
    rp = range_polys(win, bb)
    cost = (1 + t + r + rp + rv + wl) * nz
    cost = np.round(cost, 6)                  # 抹掉 1e-12 量级的浮点尾差：同一格在不同窗口里逐位相同
    land_u = shapely.difference(shapely.union_all(land_xy), shapely.union_all(big)) if big else shapely.union_all(land_xy)
    return dict(cost=cost, var=var, land=LAND, lake=LAKE, river=hit, wall=wall, land_xy=land_u)
