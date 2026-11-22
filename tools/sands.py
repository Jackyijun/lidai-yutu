# -*- coding: utf-8 -*-
"""随时代变化的沙地：范围手绘，按卷分档（规范第十九节「大漠范围」「沙地与绿洲」）。

  python3 tools/sands.py [--plot build/sands.png]

写 geodata/derived/sands.json：{全局 ID: {卷短名: [环…], "label": {卷短名: [经, 纬]}}}。生成 v1 时由
core/v1/overlay.py 换掉各卷这些荒漠条目的几何（条目本身写在各卷史料里；新加的条目在史料里只写注记点）。
范围都是示意，依据见各段注释；画法照 tools/damo.py：开、闭运算磨圆，再化简。

  · 毛乌素沙地（唐宋、宋元、民国三卷；秦汉至隋唐不画）。原取 Natural Earth 的「Mu Us Desert」，那块其实是
    整个鄂尔多斯高原（约 15.8 万 km²），连库布齐与东胜一带的梁地都盖住了。改为：
      唐宋卷：夏州（统万城）以北、以西的流沙。统万城下本即有沙（王尚义、董靖保 2001），长庆二年（822）夏州
      「飞沙为堆，高及城堞」，是史书所见最早的大片流沙；
      宋元卷：大一些。994 年宋太宗毁夏州城、迁其民于绥、银等州，宋夏之间的瀚海多沙；
      民国卷：今毛乌素沙地的范围（约 4 万 km²），南缘大体在明长城一线，明后期以来变化不大（邓辉等 2007）。
  · 科尔沁沙地（宋元、民国两卷）。西辽河流域辽代以前是疏林草原、无流动沙丘；10 世纪末起沙化突进，王守春（2000）
    认为主要由气候变化造成，韩茂莉（2004）指出辽代州城周边在沙地上垦殖是扰动的关键地区；元、明以游牧为主，植被渐复，
    清末放垦与 1950 年代起的几次大规模垦荒后沙地再次扩大，20 世纪「科尔沁草原」变成「科尔沁沙地」（乌兰图雅 2000、2002）。
    唐宋卷及以前不画。
      宋元卷：西拉木伦河、老哈河汇流处至西辽河中游；
      民国卷：约当 20 世纪中叶，取今科尔沁沙地的主体（西辽河、新开河、教来河之间）而略收东北一角，仍偏大。
  · 库布齐沙漠（民国卷）：黄河南岸，与毛乌素之间隔着东胜梁地。沙海形成于全新世，汉唐间曾再活化，但早期范围无从推定，
    各卷不画。
同样的输入，输出逐字节相同。
"""
import json
import sys
from pathlib import Path

from shapely.geometry import Polygon
from shapely.validation import explain_validity

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "geodata" / "derived" / "sands.json"

SMOOTH = 0.08     # 开、闭运算的半径（度）
SIMPLIFY = 0.02

SANDS = {
    "desert:毛乌素沙地": {
        "tangsong": ([(108.0, 38.05), (108.2, 37.8), (108.7, 37.8), (109.2, 38.05), (109.35, 38.35), (109.0, 38.6),
                      (108.5, 38.65), (108.1, 38.4)], (108.65, 38.25)),
        "songyuan": ([(107.55, 38.1), (107.6, 37.75), (108.3, 37.65), (108.9, 37.75), (109.4, 38.05), (109.6, 38.45),
                      (109.3, 38.8), (108.8, 38.95), (108.2, 38.8), (107.75, 38.45)], (108.6, 38.3)),
        "minguo-xinzhongguo": ([(107.3, 38.2), (107.25, 37.75), (107.55, 37.55), (108.2, 37.55), (108.8, 37.6), (109.3, 37.95),
                                (109.75, 38.3), (110.25, 38.6), (110.55, 38.95), (110.35, 39.2), (109.95, 39.45), (109.55, 39.55),
                                (109.1, 39.4), (108.6, 39.2), (108.1, 38.95), (107.6, 38.6)], (108.75, 38.5)),
    },
    "desert:科尔沁沙地": {
        "songyuan": ([(119.7, 43.0), (120.3, 42.85), (121.0, 42.85), (121.7, 42.95), (122.3, 43.2), (122.4, 43.55),
                      (121.8, 43.75), (121.0, 43.75), (120.4, 43.6), (119.9, 43.35)], (121.0, 43.3)),
        "minguo-xinzhongguo": ([(119.3, 42.95), (119.9, 42.7), (120.5, 42.6), (121.2, 42.6), (121.9, 42.5), (122.5, 42.45),
                                (122.95, 42.7), (123.3, 43.1), (123.45, 43.5), (123.2, 43.8), (122.6, 43.9), (122.0, 44.05),
                                (121.5, 44.2), (120.9, 44.1), (120.4, 43.95), (119.95, 43.55), (119.5, 43.25)], (121.4, 43.5)),
    },
    "desert:库布齐沙漠": {
        "minguo-xinzhongguo": ([(107.25, 39.85), (107.7, 39.9), (108.4, 40.05), (109.2, 40.15), (110.0, 40.1), (110.7, 40.0),
                                (111.0, 40.02), (110.95, 40.15), (110.6, 40.22), (109.9, 40.38), (109.1, 40.42), (108.3, 40.4),
                                (107.6, 40.25), (107.15, 40.1)], (109.3, 40.3)),
    },
}


def smooth(pts):
    P = Polygon(pts)
    if not P.is_valid:                              # 顶点顺序画错、边相交：缓冲会悄悄丢掉一块
        raise SystemExit(f"tools/sands.py：多边形 {pts[:2]}… 自相交（{explain_validity(P)}）")
    g = P.buffer(SMOOTH).buffer(-2 * SMOOTH).buffer(SMOOTH).simplify(SIMPLIFY)
    if g.is_empty or g.geom_type != "Polygon":      # 手绘的多边形有窄于 2 × SMOOTH 的颈部，磨圆后断开或消失
        raise SystemExit(f"tools/sands.py：多边形 {pts[:2]}… 磨圆后成了{'空' if g.is_empty else ' ' + g.geom_type}，把窄处画宽一些")
    return [[round(x, 2), round(y, 2)] for x, y in g.exterior.coords]


def build():
    out = {}
    for gid, eras in SANDS.items():
        out[gid] = {"label": {}}
        for slug, (pts, lab) in eras.items():
            out[gid][slug] = [smooth(pts)]
            out[gid]["label"][slug] = list(lab)
    return out


def main():
    out = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf8")
    import math
    for gid, eras in out.items():
        for slug, rings in eras.items():
            if slug == "label":
                continue
            a = sum(Polygon(r).area * 111.32 ** 2 * math.cos(math.radians(Polygon(r).centroid.y)) for r in rings)   # 近似面积
            print(f"{gid:16s} {slug:20s} 约 {a:,.0f} km²")
    print("→", OUT.relative_to(ROOT))
    if "--plot" in sys.argv:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 7))
        for gid, eras in out.items():
            for slug, rings in eras.items():
                if slug != "label":
                    for r in rings:
                        ax.plot(*zip(*r), lw=1, label=f"{gid} {slug}")
        ax.set_aspect(1.3)
        fig.savefig(sys.argv[sys.argv.index("--plot") + 1], bbox_inches="tight")


if __name__ == "__main__":
    main()
