# -*- coding: utf-8 -*-
"""描界（规范第十三节第 5、6 条）：分类栅格 → 共享界线的覆盖图。

每类的指示栅格作高斯平滑，每格归平滑值最大的一类；界线描在相邻两类平滑值相等处（沿格边线性插值，
三类以上交汇处取交点均值）。界线网络全图只描一次、两侧共用，再做几轮拉普拉斯平滑，相邻疆域之间
既无白缝也无叠色。然后加位移场、整体覆盖简化。
"""
import numpy as np
import shapely
from scipy import ndimage
from scipy.sparse import coo_matrix
from shapely.ops import unary_union

from grid import cfg


def faces_of(lab, pins=(), log=print):
    """lab：每格的类（-1 = 无主或界外）；pins：[(行, 列)] 归属点所在格，平滑后仍归本类。
    返回 {类: 多边形（格坐标 x=列, y=行）}"""
    T = cfg()["trace"]
    NY, NX = lab.shape
    sig = T["smooth"]; pad = int(4 * sig) + 3
    classes = [-1] + sorted(set(int(v) for v in np.unique(lab)) - {-1})
    objs = ndimage.find_objects(lab + 1)

    cache = {}

    def field(k):
        if k in cache:
            return cache[k]
        if k == -1:
            v = 0, NY, 0, NX, ndimage.gaussian_filter((lab == -1).astype(float), sig, mode="nearest")
        else:
            sl = objs[k]
            r0, r1 = max(0, sl[0].start - pad), min(NY, sl[0].stop + pad)
            c0, c1 = max(0, sl[1].start - pad), min(NX, sl[1].stop + pad)
            v = r0, r1, c0, c1, ndimage.gaussian_filter((lab[r0:r1, c0:c1] == k).astype(float), sig, mode="constant")
        cache[k] = v
        return v

    best = np.full((NY, NX), -1.0); arg = np.full((NY, NX), -1, np.int32)
    for k in classes:
        r0, r1, c0, c1, f = field(k)
        sub = best[r0:r1, c0:c1]; up = f > sub
        sub[up] = f[up]; arg[r0:r1, c0:c1][up] = k
    for r, c in pins:                         # 归属点所在格及其紧邻的同类格不因平滑改归别类（单点飞地不被抹掉）
        k = lab[r, c]
        if k < 0:
            continue
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = r + dr, c + dc
                if 0 <= rr < NY and 0 <= cc < NX and lab[rr, cc] == k:
                    arg[rr, cc] = k
    gone = [k for k in classes[1:] if not (arg == k).any()]
    for k in gone:
        arg[lab == k] = k

    hr, hc = np.nonzero(arg[:, :-1] != arg[:, 1:])
    vr, vc = np.nonzero(arg[:-1, :] != arg[1:, :])
    er = np.r_[hr, vr]; ec = np.r_[hc, vc]
    qr = np.r_[hr, vr + 1]; qc = np.r_[hc + 1, vc]
    A = arg[er, ec]; B = arg[qr, qc]
    fAp, fAq, fBp, fBq = (np.zeros(len(er)) for _ in range(4))
    for k in classes:
        r0, r1, c0, c1, f = field(k)
        for m, (o1, o2) in ((A == k, (fAp, fAq)), (B == k, (fBp, fBq))):
            idx = np.nonzero(m)[0]
            if len(idx) == 0:
                continue
            o1[idx] = f[er[idx] - r0, ec[idx] - c0]; o2[idx] = f[qr[idx] - r0, qc[idx] - c0]
    cache.clear()
    dp, dq = fAp - fBp, fAq - fBq
    den = dp - dq
    t = np.clip(np.where(np.abs(den) > 1e-12, dp / np.where(np.abs(den) > 1e-12, den, 1), .5), 1e-3, 1 - 1e-3)
    nh = len(hr)
    px = np.r_[hc + t[:nh], vc.astype(float)]
    py = np.r_[hr.astype(float), vr + t[nh:]]
    hid = np.full((NY, NX), -1, np.int64); vid = np.full((NY, NX), -1, np.int64)
    hid[hr, hc] = np.arange(nh); vid[vr, vc] = nh + np.arange(len(vr))
    sq = np.stack([hid[:-1, :-1], vid[:-1, 1:], hid[1:, :-1], vid[:-1, :-1]], -1).reshape(-1, 4)
    n = (sq >= 0).sum(1)
    E = len(px)
    edges = []
    two = sq[n == 2]
    if len(two):
        edges.append(np.sort(two, 1)[:, 2:])
    many = sq[n >= 3]
    jx, jy = np.zeros(0), np.zeros(0)
    if len(many):
        ok = many >= 0
        jx = np.where(ok, px[np.maximum(many, 0)], 0).sum(1) / ok.sum(1)
        jy = np.where(ok, py[np.maximum(many, 0)], 0).sum(1) / ok.sum(1)
        jid = E + np.arange(len(many))
        for j in range(4):
            m = ok[:, j]
            edges.append(np.c_[many[m, j], jid[m]])
    edges = np.concatenate(edges)
    P = np.c_[np.r_[px, jx], np.r_[py, jy]]
    faces = list(shapely.get_parts(shapely.polygonize(shapely.linestrings(P[edges]))))

    fa = shapely.area(np.array(faces, dtype=object))
    reps = shapely.point_on_surface(np.array(faces, dtype=object))
    cls = []
    for fc, p in zip(faces, reps):
        r, c = int(round(p.y)), int(round(p.x))
        k = None
        for dr, dc in ((0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < NY and 0 <= cc < NX and fc.contains(shapely.Point(cc, rr)):
                k = int(arg[rr, cc]); break
        cls.append(int(arg[min(NY - 1, max(0, r)), min(NX - 1, max(0, c))]) if k is None else k)
    small = fa < T["min_face"]
    for k in sorted(set(cls)):
        small[max((i for i, c in enumerate(cls) if c == k), key=lambda i: fa[i])] = False
    if len(pins):                             # 含归属点的面不并
        ftree = shapely.STRtree(faces)
        pp = shapely.points([(c, r) for r, c in pins])
        hit = ftree.query(pp, predicate="within")
        for j in np.unique(hit[1]):
            small[j] = False
    tree = shapely.STRtree(faces)
    nm = 0
    for i in np.argsort(fa, kind="stable"):
        if not small[i]:
            continue
        best_c, best_l = cls[i], 0.0
        for j in sorted(tree.query(faces[i], predicate="intersects")):
            if j == i:
                continue
            L = faces[i].boundary.intersection(faces[j].boundary).length
            if L > best_l + 1e-9:
                best_c, best_l = cls[j], L
        nm += best_c != cls[i]; cls[i] = best_c
    V = len(P)
    adj = coo_matrix((np.ones(2 * len(edges)), (np.r_[edges[:, 0], edges[:, 1]], np.r_[edges[:, 1], edges[:, 0]])), shape=(V, V)).tocsr()
    deg = np.asarray(adj.sum(1)).ravel()
    step, rounds = T["laplace"]
    lam = np.where(deg == 2, step, np.where(deg >= 3, step * .5, 0))[:, None]
    Q = P.copy()
    for _ in range(rounds):
        Q = Q + lam * (adj @ Q / np.maximum(deg, 1)[:, None] - Q)
    new = list(shapely.get_parts(shapely.polygonize(shapely.linestrings(Q[edges]))))
    if len(new) == len(faces):
        tree = shapely.STRtree(faces)
        ncls = []
        for g in new:
            js = tree.query(g, predicate="intersects")
            ncls.append(cls[max(js, key=lambda j: g.intersection(faces[j]).area)])
        faces, cls = new, ncls
    else:
        log("平滑后面数不符，沿用未平滑界线", len(new), len(faces))
    by = {}
    for fc, k in zip(faces, cls):
        by.setdefault(k, []).append(fc)
    out = {}
    for k in sorted(by):
        try:
            out[k] = shapely.coverage_union_all(by[k])
        except Exception:
            out[k] = unary_union(by[k])
    return out, arg


class Warp:
    """位移场：两种尺度的平滑随机场（全局，与卷无关），给界线带上河曲一样的小弯。
    界河两侧 taper 格内渐减为 0（否则沿河的分界会被推离河道）；界线上的点挪动后离任何归属点
    都不得近于 pin 格（否则挨得很近的两个点之间的界线可能被推过点去，单点的飞地会被挤没）。"""

    def __init__(self, win, river, pins=()):
        W = cfg()["trace"]["warp"]
        self.dr = np.zeros(win.shape); self.dc = np.zeros(win.shape)
        for k, (s, amp) in enumerate(W["scales"]):
            self.dr += amp * win.smooth_noise(101 + 2 * k, s)
            self.dc += amp * win.smooth_noise(102 + 2 * k, s)
        if river is not None and river.any() and W["taper"] > 0:
            d = ndimage.distance_transform_edt(~river) / W["taper"]
            f = np.clip(d, 0, 1); f = f * f * (3 - 2 * f)
            self.dr *= f; self.dc *= f
        self.dp = None
        if len(pins):
            m = np.zeros(win.shape, bool)
            for r, c in pins:
                m[r, c] = True
            self.dp = ndimage.distance_transform_edt(~m)
        self.pin = W["pin"]
        self.win = win

    def __call__(self, a):
        c, r = a[:, 0], a[:, 1]
        dr = ndimage.map_coordinates(self.dr, [r, c], order=1, mode="nearest")
        dc = ndimage.map_coordinates(self.dc, [r, c], order=1, mode="nearest")
        if self.dp is not None:
            d = ndimage.map_coordinates(self.dp, [r, c], order=1, mode="nearest")
            mag = np.hypot(dr, dc)
            k = np.minimum(1, np.maximum(0, d - self.pin) / np.maximum(mag, 1e-9))
            dr = dr * k; dc = dc * k
        x, y = self.win.xy(r + dr, c + dc)
        return np.c_[x, y]


def polygons(win, lab, warp, clip=None, pins=(), log=print):
    """分类栅格 → {类: 投影坐标多边形}（已加位移、覆盖简化、按外缘裁剪、去掉碎块）"""
    T = cfg()["trace"]
    by, arg = faces_of(lab, pins, log)
    keys = sorted(by)
    cov = [shapely.transform(by[k], warp) for k in keys]
    cov = shapely.coverage_simplify(np.array(cov, dtype=object), tolerance=T["simplify"] * win.cell)
    out = {}
    for k, g in zip(keys, cov):
        if k < 0:
            continue
        g = g.buffer(0)
        if clip is not None:
            g = g.intersection(clip)
        ps = [p for p in shapely.get_parts(g) if p.geom_type == "Polygon" and p.area > T["min_part"]]
        if ps:
            out[k] = shapely.MultiPolygon(ps)
    return out, arg
