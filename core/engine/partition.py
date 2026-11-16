# -*- coding: utf-8 -*-
"""分区（规范第十三节第 3、4 条）：以全部归属点为源跑一次 16 邻接多源最短路，每格归代价距离最近的点。

手绘外缘的卷（隋唐、两晋）：栅格只建在外缘以内，外缘以外不属任何政权。
疆域向海面延伸 fill_sea 格、大湖全部填满（页面按陆地裁剪）。
"""
import math

import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

from grid import cfg

STEPS16 = ((0, 1), (1, -1), (1, 0), (1, 1), (1, -2), (1, 2), (2, -1), (2, 1))
STEPS8 = ((0, 1), (1, -1), (1, 0), (1, 1))


def graph(cost, node):
    nj, ni = node.shape
    nid = np.full(node.shape, -1, np.int64)
    NN = int(node.sum()); nid[node] = np.arange(NN)
    rows, cols, wts = [], [], []
    steps = STEPS16 if cfg()["partition"]["neighbors"] == 16 else STEPS8
    for dr, dc in steps:
        L = math.hypot(dr, dc)
        sa = (slice(0, nj - dr), slice(0, ni - dc) if dc >= 0 else slice(-dc, ni))
        sb = (slice(dr, nj), slice(dc, ni) if dc >= 0 else slice(0, ni + dc))
        a, b = nid[sa], nid[sb]
        ok = (a >= 0) & (b >= 0)
        rows.append(a[ok]); cols.append(b[ok]); wts.append(L * (cost[sa][ok] + cost[sb][ok]) / 2)
    G = coo_matrix((np.concatenate(wts), (np.concatenate(rows), np.concatenate(cols))), shape=(NN, NN)).tocsr()
    return G, nid


def snap(win, node, nid, pts, active=None, log=print):
    """归属点 → 起点格；落在海里的就近挪到陆地，两点同格的挪到旁边；active 为 False 的点不参与"""
    K = cfg()["partition"]["snap"]
    starts, owner, where = [], [], {}
    taken = set()
    for i, (x, y) in enumerate(pts):
        if active is not None and not active[i]:
            continue
        r, c = (int(round(float(v))) for v in win.rc(x, y))
        if not (0 <= r < win.nj and 0 <= c < win.ni):
            log("归属点在范围外", i); continue
        if not node[r, c]:
            sub = node[max(0, r - K):r + K + 1, max(0, c - K):c + K + 1]
            ys, xs = np.nonzero(sub)
            if len(ys) == 0:
                log("归属点在海中", i); continue
            j = np.argmin((ys - min(r, K)) ** 2 + (xs - min(c, K)) ** 2)
            r, c = max(0, r - K) + ys[j], max(0, c - K) + xs[j]
        if (r, c) in taken:
            for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < win.nj and 0 <= cc < win.ni and node[rr, cc] and (rr, cc) not in taken:
                    r, c = rr, cc; break
        taken.add((r, c)); where[i] = (r, c)
        starts.append(int(nid[r, c])); owner.append(i)
    return starts, owner, where


def outer_reach(lab, D, node, reach):
    """可达代价定外缘（规范第十三节第 4 条）：超出该点可达代价的格子为无主地；外缘闭运算填平圆弧间的凹口，
    小空隙并回，再高斯平滑（海面与推算范围以外当作有主，免得海岛、半岛尖被磨掉）。owned 格归最近的可达格的点"""
    O = cfg()["outer"]
    inreach = node & (lab >= 0) & (D <= reach[np.clip(lab, 0, None)])
    dil = ndimage.distance_transform_edt(~inreach) <= O["close"]
    closed = (ndimage.distance_transform_edt(dil) > O["close"]) & node
    lbl, nl = ndimage.label(node & ~closed)
    if nl:
        sz = ndimage.sum(np.ones_like(lbl), lbl, range(1, nl + 1))
        closed |= np.isin(lbl, np.nonzero(sz < O["hole_max"])[0] + 1)
    owned = (ndimage.gaussian_filter((closed | ~node).astype(float), O["edge_sigma"]) > .5) & node
    _, (jr, jc) = ndimage.distance_transform_edt(~inreach, return_indices=True)
    return np.where(owned, lab[jr, jc], -1).astype(np.int32)


def run(win, C, pts, inner, cost=None, reach=None, active=None, log=print):
    """返回每格归属点序号 lab（-1 无主或界外）、到最近点的代价距离 dist、各点的起点格。
    inner：栅格只建在这里（手绘外缘或推算范围）；reach：各点的可达代价（None 则不限，外缘由 inner 定）"""
    node = C["land"] & inner
    G, nid = graph(C["cost"] if cost is None else cost, node)
    log("图", int(node.sum()), "点", G.nnz, "边")
    starts, owner, where = snap(win, node, nid, pts, active, log)
    dist, _, src = dijkstra(G, directed=False, indices=starts, min_only=True, return_predecessors=True)
    seed_of = np.full(G.shape[0], -1, np.int32)
    seed_of[np.array(starts)] = np.array(owner)
    lab_n = np.where(src >= 0, seed_of[np.maximum(src, 0)], -1)
    lab = np.full(win.shape, -1, np.int32); lab[node] = lab_n
    D = np.full(win.shape, np.inf); D[node] = dist
    unreached = np.zeros(win.shape, bool); unreached[node] = lab_n < 0
    if reach is not None:
        lab = outer_reach(lab, D, node, reach)
        log("可达范围内陆地", int((lab >= 0).sum()), "/", int(node.sum()))
    # 疆域向海面、大湖延伸；没有归属点够得着的孤岛就近并入（都只在 inner 以内）
    d, (ir, ic) = ndimage.distance_transform_edt(lab < 0, return_indices=True)
    ext = lab[ir, ic]
    fillable = ~C["land"] if reach is not None else (~C["land"] | unreached)   # 按可达代价的卷：够不着的岛仍是无主
    ok = (lab < 0) & inner & fillable & (C["lake"] | (d <= cfg()["partition"]["fill_sea"]))
    lab = np.where(ok, ext, lab)
    log("未达", int(unreached.sum()))
    return lab, D, where
