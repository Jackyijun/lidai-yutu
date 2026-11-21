# -*- coding: utf-8 -*-
"""民国形势图 · 构建参数。

改这里会影响底图的范围与精度；史料内容（归属点、各节点归属、战役等）在 content/ 目录。改完参数后重新运行 `python run.py`。
疆域由单仓的统一疆域引擎推算（era.toml 的 [engine]，推算范围 box、exclude 也写在那里），国界墙在单仓的 global/walls.toml
（2026-11-21 由这里搬去），墙的强度等参数在 core/engine/config.toml；颜色由单仓的 global/palette.toml 定。
本卷原来的栅格、通行代价、分区与外缘、疆域多边形、配色参数，以及只给代价栅格用的 ETOPO20 地形，2026-11 架构整理第三批起退役。
"""
from pathlib import Path

# ---------------------------------------------------------------- 路径
ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"          # 手写的史料内容
GEODATA = ROOT / "geodata"          # 底图数据
NE_DIR = GEODATA / "ne"             # Natural Earth 1:10m GeoJSON
PROV_JSON = GEODATA / "prov.json"   # 今中国省界（简化）
BUILD = ROOT / "build"              # 中间产物 geo.json / data.json；本卷的产物是 ROOT / "source.json"

# ---------------------------------------------------------------- 底图来源
# Natural Earth 矢量数据（公有领域），固定到一个提交，保证可复现。
NE_COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"
NE_BASE = f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{NE_COMMIT}/geojson"
NE_FILES = [
    "ne_10m_land",                        # 海陆
    "ne_10m_minor_islands",               # 小岛
    "ne_10m_lakes",                       # 湖泊
    "ne_10m_lakes_historic",              # 历史湖泊（咸海旧岸、罗布泊）
    "ne_10m_rivers_lake_centerlines",     # 河流
    "ne_10m_admin_0_countries_chn",       # 今国界（中国视角版本）
    "ne_10m_geography_regions_polys",     # 沙漠多边形
]
# ---------------------------------------------------------------- 范围与投影
# 疆域推算范围：全亚洲的框，再剔除乌拉尔—里海—高加索以北的欧洲、黑海以西的巴尔干与红海以西的非洲。两样都写在本卷 era.toml 的
# [engine]（box、exclude），统一疆域引擎与这里读同一份；这里用来在页面上给推算范围以外罩一层薄纸色（GEO.extpoly）。
try:
    import tomllib
except ImportError:
    import tomli as tomllib
_ENGINE = tomllib.loads((ROOT / "era.toml").read_text(encoding="utf8"))["engine"]
EXTENT = tuple(_ENGINE["box"])        # 西, 东, 南, 北
EXCLUDE = _ENGINE["exclude"]          # [[[经, 纬], …], …]
# 底图范围：比疆域范围大。陆地、河湖、今国界画到这里（东界跨过国际日期变更线，含夏威夷、中途岛；西界含地中海东部）
BASE_EXTENT = (5.0, 215.0, -30.0, 82.0)
# Albers 等积圆锥：标准纬线 25°N、47°N；中央经线 103°E、原点纬线 32°N，取亚洲中心。页面用同一组数（GEO.proj）。
PROJ = (25.0, 47.0, 32.0, 103.0)      # 标准纬线1, 标准纬线2, 原点纬线, 中央经线
FIRST = "1937.12"                     # 首屏节点

# ---------------------------------------------------------------- 底图简化
SIMPLIFY_LAND = 0.018
LAND_MIN_AREA = 0.004
LAND_HOLE_MIN_AREA = 0.01
SIMPLIFY_BORDER = 0.02
SIMPLIFY_RIVER = 0.015
RIVER_MAX_SCALERANK = 6   # 未命名河流保留到这一级（数字越小越大）
