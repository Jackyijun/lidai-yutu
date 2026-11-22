# -*- coding: utf-8 -*-
"""逐节点核对各卷的归属点是否落在页面所画的、它所属单位的疆域里：python tools/pointcheck.py [卷短名 …] [--tol 公里] [--all]

读 build/v1/<卷>.json（页面用的就是这份：疆域已换成统一引擎的结果，衔接节点已照搬邻卷并对齐归属）。
每个节点、每个有归属的点：所属单位在这个节点画了疆域，就看点在不在里面；单位没有单独的疆域、画在上一层政权里的，看政权的疆域。
离疆域超过容差（缺省 3 km）的列出来。缺省只查城、州府等点（kind 不是 r 的）；
r 是只为推算疆域设的区域点，平滑、描界后落在界外几公里很常见，加 --all 才一起查（春秋、战国卷的点全是 r）。
当年不参与分区的点（v1 地点的 t0、t1，即 seeds.txt 的 ^年份、~年份；规则同 core/engine/data.py 的 view）不查。
v1 数据包还没有疆域（两遍构建的第一遍）时报错退出，免得「查了 0 个」被当成通过。
原民国卷 tools/verify.py（规范第十三节的验收项）只查那一卷、读旧构建的 geo.json；这里各卷通用。只读，不改任何文件。
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import shapely
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points

ROOT = Path(__file__).resolve().parent.parent
ERAS = ["chunqiu", "zhanguo", "qinhan", "hanmosanguo", "liangjin-nanbeichao", "suitang", "tangsong", "songyuan", "minguo-xinzhongguo"]


def shape(b, gi, cache):
    """v1 的几何：每环首点绝对、其余相对，坐标 ×100；多环按奇偶规则叠（与页面填充一致）"""
    if gi not in cache:
        g = Polygon()
        for flat in b["geom"][gi]:
            x = y = 0
            pts = []
            for i in range(0, len(flat), 2):
                x += flat[i]
                y += flat[i + 1]
                pts.append((x / 100, y / 100))
            if len(pts) >= 3:
                g = g.symmetric_difference(polygonal(shapely.make_valid(Polygon(pts))))
        cache[gi] = g
    return cache[gi]


def polygonal(g):
    """make_valid 可能连带线、点（退化的环），只留面"""
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    parts = [x for x in getattr(g, "geoms", []) if x.geom_type in ("Polygon", "MultiPolygon")]
    return shapely.unary_union(parts) if parts else Polygon()


def km(a, b):
    """两点（经, 纬）的大圆距离，公里"""
    la1, lo1, la2, lo2 = map(math.radians, (a.y, a.x, b.y, b.x))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(min(1, math.sqrt(h)))


def year(t):
    y = t // 12
    return f"前{-y}" if y < 0 else str(y)


def check(slug, tol, all_kinds):
    b = json.load(open(ROOT / "build" / "v1" / f"{slug}.json", encoding="utf8"))
    P, U = b["places"], b["polities"]
    if not any(n.get("u") or n.get("pu") for n in b["nodes"]):
        sys.exit(f"{slug}：build/v1/{slug}.json 还没有疆域（两遍构建的第一遍？），先完整构建：python run.py {slug}")
    cache, bad, n_checked = {}, defaultdict(list), 0
    for node in b["nodes"]:
        geo_u, geo_p, pol = node.get("u", {}), node.get("pu", {}), node.get("pol", {})
        for i, u in enumerate(node.get("own", [])):
            if u is None or u < 0 or (P[i]["kind"] == "r" and not all_kinds):
                continue
            t0, t1 = P[i].get("t0"), P[i].get("t1")
            if (t1 is not None and node["t"] > t1) or (t0 is not None and node["t"] < t0):
                continue                       # 当年不参与分区的点（退出的、还没开始的）
            k = str(u)
            gi = geo_u.get(k)
            if gi is None:
                gi = geo_p.get(str(pol.get(k, k)))
            if gi is None:                     # 这个单位在本节点没画疆域（如只标注不填色的部族）：不查
                continue
            n_checked += 1
            p = Point(P[i]["lon"], P[i]["lat"])
            g = shape(b, gi, cache)
            if g.contains(p):
                continue
            d = km(p, nearest_points(g, p)[0]) if not g.is_empty else -1
            if d < 0 or d > tol:
                bad[(P[i]["key"], U[u]["key"])].append((node["t"], round(d, 1)))
    return n_checked, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*", default=ERAS)
    ap.add_argument("--tol", type=float, default=3.0, help="容差，公里（缺省 3）")
    ap.add_argument("--all", action="store_true", help="连区域点（kind r）一起查")
    a = ap.parse_args()
    total = 0
    for slug in a.slugs:
        if slug not in ERAS:
            sys.exit(f"没有这一卷：{slug}（可选：{'、'.join(ERAS)}）")
        n, bad = check(slug, a.tol, a.all)
        total += len(bad)
        print(f"== {slug}：查了 {n} 个点次，落在本单位疆域外超过 {a.tol:g} km 的 {len(bad)} 个点"
              + ("（本卷的点全是区域点，加 --all 才查）" if n == 0 and not a.all else ""))
        for (key, unit), v in sorted(bad.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            t, d = v[0]
            far = "该单位疆域为空" if d < 0 else f"偏 {d} km"
            print(f"   {key} → {unit}：{len(v)} 个节点，如 {year(t)}（{far}）")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
