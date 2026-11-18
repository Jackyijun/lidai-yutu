# -*- coding: utf-8 -*-
"""大漠（戈壁）的范围：由生态区改绘，七卷共用（规范第十九节「大漠范围」）。

  python3 tools/damo.py [--plot build/damo.png]

读 geodata/resolve/gobi_ecoregions.geojson（RESOLVE Ecoregions 2017 的三个戈壁生态区：东戈壁荒漠草原、
戈壁湖谷荒漠草原、阿拉善高原半荒漠；CC-BY 4.0，出处见同目录 README），写 geodata/derived/damo.json。
生成 v1 时由 core/v1/overlay.py 换掉各卷「大漠／大碛／戈壁」（全局 ID desert:大碛）原来的几何。

三区合并后扣掉：
  · 漠南：阴山、狼山以北到「碛口线」。中段压在唐人入碛处（《新唐书·地理志》中受降城北行五百九十里入碛，约北纬 43°），
    二连浩特一带约 43.6°，东到东经 114° 尖灭；西段压在汉外长城（光禄塞列城）以北，第一次漠南之战的右贤王庭在线南；
  · 河西走廊绿洲带与祁连山前（张掖、酒泉、瓜州、玉门关、民勤）；腾格里沙漠以南；
  · 漠北：杭爱山南麓以北（西段北界顺山麓压到北纬 46° 上下）；
  · 居延：弱水下游河谷与居延绿洲（汉至元屯垦，今额济纳绿洲），从河西一侧切进去，免得成为孔洞；
  · 秦汉卷另扣乌兰布和沙漠北部的汉代垦区（侯仁之、俞伟超、李宝田 1965），东汉以后弃垦才沙化。
同样的输入，输出逐字节相同。
"""
import json
import sys
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "geodata" / "resolve" / "gobi_ecoregions.geojson"
OUT = ROOT / "geodata" / "derived" / "damo.json"

# 漠南（阴山、狼山以北至碛口线）
MOBAN = [(106.55, 41.1), (106.25, 41.6), (106.2, 42.2), (106.6, 42.65), (107.5, 42.85), (108.5, 43.0), (109.5, 43.0), (110.5, 43.05), (111.5, 43.35),
         (112.4, 43.7), (113.6, 44.4), (114.6, 45.2), (118.0, 45.2), (118.0, 40.0), (107.3, 40.0), (107.15, 40.7)]
# 河西走廊绿洲带、祁连山前（含民勤绿洲），腾格里沙漠以南
HEXI = [(92.5, 36.0), (92.5, 40.6), (94.0, 40.75), (95.5, 40.75), (96.8, 40.45), (98.0, 40.05), (99.2, 39.8), (100.0, 39.55),
        (100.8, 39.25), (101.6, 38.95), (102.5, 38.95), (103.3, 38.95), (103.6, 38.3), (103.75, 37.85), (104.3, 37.55),
        (105.0, 37.45), (105.6, 37.6), (106.2, 37.9), (106.2, 36.0)]
# 漠北：杭爱山南麓以北
MOBEI = [(90.0, 45.9), (96.0, 45.95), (97.5, 46.25), (99.5, 46.15), (101.0, 46.05), (102.5, 46.2), (104.2, 46.35), (104.2, 50.0), (90.0, 50.0)]
# 弱水下游（金塔—额济纳，汉居延塞沿线）与居延绿洲
RUOSHUI = [(98.9, 39.75), (99.3, 40.1), (99.6, 40.4), (100.3, 41.0), (100.8, 41.6), (101.05, 41.95)]
JUYAN = (101.1, 42.05)
# 秦汉卷：乌兰布和沙漠北部的汉代垦区（朔方郡窳浑、临戎、三封一带）
ULANBUH_HAN = [(106.15, 40.2), (106.15, 40.95), (106.75, 41.05), (107.05, 40.6), (106.85, 40.2)]

SMOOTH = 0.15     # 开、闭运算的半径（度），磨掉切线留下的直角
SIMPLIFY = 0.03
MIN_PART = 0.3    # 小于此面积（平方度）的碎块丢掉
LABEL = (107.6, 44.75)   # 注记点：漠南、漠北之间的戈壁带正中


def load():
    fc = json.loads(SRC.read_text(encoding="utf8"))
    return unary_union([shape(f["geometry"]).buffer(0) for f in fc["features"]])


def parts(g):
    gs = [p for p in getattr(g, "geoms", [g]) if p.area >= MIN_PART]
    return [Polygon(p.exterior) for p in sorted(gs, key=lambda p: -p.area)]      # 不留孔洞：页面上每个环单独填点纹


def build():
    u = load()
    g = u.difference(Polygon(MOBAN)).difference(Polygon(HEXI)).difference(Polygon(MOBEI))
    g = g.buffer(-SMOOTH).buffer(2 * SMOOTH).buffer(-SMOOTH)
    jy = unary_union([LineString(RUOSHUI).buffer(0.12), Point(JUYAN).buffer(0.32)])
    g = g.difference(jy)
    base = unary_union(parts(g))
    han = base.difference(Polygon(ULANBUH_HAN))
    out = {}
    for k, v in (("all", base), ("qinhan", han)):
        out[k] = [[[round(x, 2), round(y, 2)] for x, y in p.simplify(SIMPLIFY).exterior.coords] for p in parts(v)]
    out["label"] = list(LABEL)
    return out, u, base, han


def main():
    out, u, base, han = build()
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf8")
    print(f"大漠：{len(out['all'])} 块，{base.area:.1f} 平方度（秦汉卷 {han.area:.1f}）→ {OUT.relative_to(ROOT)}")
    if "--plot" in sys.argv:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 7))
        for p in getattr(u, "geoms", [u]):
            ax.plot(*p.exterior.xy, color="#999", lw=.6)
        for r in out["all"]:
            ax.fill(*zip(*r), fc="#e6c27a", ec="#8a6a2a", lw=1)
        for r in out["qinhan"]:
            ax.plot(*zip(*r), color="#2a7a2a", lw=.8, ls=":")
        ax.set_aspect(1.3)
        fig.savefig(sys.argv[sys.argv.index("--plot") + 1], bbox_inches="tight")


if __name__ == "__main__":
    main()
