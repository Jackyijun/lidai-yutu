# -*- coding: utf-8 -*-
"""全球统一格网与随机场。

格网铺在统一投影（core/geo/config.toml）的平面上，格边长 cell；第 (i, j) 格的格心在
x = (i + .5) · cell、y = (j + .5) · cell。各卷只取一个矩形窗口 [i0, i0 + ni) × [j0, j0 + nj)，
数组下标 [r, c] = [j - j0, i - i0]。

随机场（代价噪声、界线位移场）按 tile × tile 格分块生成白噪声，每块的种子只由（全局种子、
场的编号、块号）决定；高斯平滑时多取一圈边距，再按理论标准差归一化。所以同一格在任何窗口里
取到的值都一样，与卷、与窗口大小无关。
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core" / "geo"))
import geo  # noqa: E402

try:
    import tomllib
except ImportError:
    import tomli as tomllib

_CFG = None


def cfg():
    """core/engine/config.toml；试参数时可用环境变量 ENGINE_CONFIG 指向另一份"""
    global _CFG
    if _CFG is None:
        import os
        p = os.environ.get("ENGINE_CONFIG") or (Path(__file__).resolve().parent / "config.toml")
        _CFG = tomllib.loads(Path(p).read_text(encoding="utf8"))
    return _CFG


KM = geo.km_per_unit()          # 1 投影单位合多少 km
DEG = 1000 * math.pi / 180      # 1 纬度合多少投影单位


class Window:
    """一卷的计算窗口。"""

    def __init__(self, x0, x1, y0, y1, pad=0):
        c = cfg()["grid"]["cell"]
        self.cell = c
        self.i0 = math.floor(x0 / c) - pad
        self.j0 = math.floor(y0 / c) - pad
        self.ni = math.ceil(x1 / c) + pad - self.i0
        self.nj = math.ceil(y1 / c) + pad - self.j0
        self.shape = (self.nj, self.ni)

    # 下标 ↔ 投影坐标
    def xy(self, r, c):
        return (self.i0 + np.asarray(c) + .5) * self.cell, (self.j0 + np.asarray(r) + .5) * self.cell

    def rc(self, x, y):
        return np.asarray(y) / self.cell - .5 - self.j0, np.asarray(x) / self.cell - .5 - self.i0

    def centers(self):
        """格心的投影坐标（二维）"""
        x, y = self.xy(np.arange(self.nj)[:, None], np.arange(self.ni)[None, :])
        return np.broadcast_to(x, self.shape), np.broadcast_to(y, self.shape)

    def lonlat(self):
        x, y = self.centers()
        return geo.inv(x, y)

    def km(self):
        return self.cell * KM

    # ---------------- 随机场 ----------------
    def white(self, stream, margin):
        """窗口外扩 margin 格的白噪声（float64），按块生成，种子与窗口无关"""
        T = cfg()["grid"]["tile"]; seed = cfg()["grid"]["seed"]
        r0, c0 = self.j0 - margin, self.i0 - margin
        h, w = self.nj + 2 * margin, self.ni + 2 * margin
        out = np.empty((h, w))
        OFF = 1 << 20                          # 块号可能为负，种子须非负
        for tj in range(r0 // T, (r0 + h - 1) // T + 1):
            for ti in range(c0 // T, (c0 + w - 1) // T + 1):
                blk = np.random.default_rng([seed, stream, tj + OFF, ti + OFF]).standard_normal((T, T))
                a0, a1 = max(r0, tj * T), min(r0 + h, (tj + 1) * T)
                b0, b1 = max(c0, ti * T), min(c0 + w, (ti + 1) * T)
                out[a0 - r0:a1 - r0, b0 - c0:b1 - c0] = blk[a0 - tj * T:a1 - tj * T, b0 - ti * T:b1 - ti * T]
        return out

    def smooth_noise(self, stream, sigma):
        """白噪声高斯平滑后归一到单位标准差（按卷积核算出的理论值，不随窗口变）"""
        rad = int(4.0 * sigma + .5)
        m = rad + 2
        f = ndimage.gaussian_filter(self.white(stream, m), sigma, mode="constant", truncate=4.0)
        x = np.arange(-rad, rad + 1)
        k = np.exp(-.5 * (x / sigma) ** 2); k /= k.sum()
        return f[m:m + self.nj, m:m + self.ni] / float((k * k).sum())


def gauss_band(mask, sigma_cells):
    """到 mask 的距离 → 高斯形 0—1 带"""
    if not mask.any():
        return np.zeros(mask.shape)
    d = ndimage.distance_transform_edt(~mask)
    return np.exp(-d * d / (2 * sigma_cells * sigma_cells))


def burn(win, lines_xy, step=1 / 3, margin=0):
    """投影坐标折线 → 布尔栅格（沿线每 step 格取样，就近取格）；margin 为数组比窗口多出的一圈"""
    h, w = win.nj + 2 * margin, win.ni + 2 * margin
    m = np.zeros((h, w), bool)
    for x, y in lines_xy:
        r, c = win.rc(x, y)
        r = r + margin; c = c + margin
        for k in range(len(r) - 1):
            n = max(2, int(math.hypot(r[k + 1] - r[k], c[k + 1] - c[k]) / step) + 1)
            rr = np.rint(np.linspace(r[k], r[k + 1], n)).astype(np.int64)
            cc = np.rint(np.linspace(c[k], c[k + 1], n)).astype(np.int64)
            ok = (rr >= 0) & (rr < h) & (cc >= 0) & (cc < w)
            m[rr[ok], cc[ok]] = True
    return m
