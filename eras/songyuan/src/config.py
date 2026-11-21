# -*- coding: utf-8 -*-
"""宋辽夏金元形势图 · 构建参数。

改这里会影响底图的范围与精度；史料内容（州府、归属、战役等）在 content/ 目录。改完参数后重新运行 `python run.py`。
疆域由单仓的统一疆域引擎推算（era.toml 的 [engine]），颜色由单仓的 global/palette.toml 定：本卷原来的栅格、
通行代价、分区与外缘、疆域多边形、配色参数，以及只给代价栅格用的 ETOPO20 地形，2026-11 架构整理第三批起退役。
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
    "ne_10m_geography_regions_polys",     # 山地、沙漠多边形
]

# ---------------------------------------------------------------- 范围与投影
# 全图范围：西起中欧（列格尼卡、蒂萨河），东至日本；南到占城、真腊，北到诺夫哥罗德、叶尼塞河中游。
EXTENT = (14.0, 146.0, 10.0, 62.0)
# 底图范围：比疆域范围大得多。陆地、河湖、今国界画到这里，拖到疆域范围外也仍是完整的底图（西经 25° 至东经 180°，南纬 11° 至北纬 82°）。
BASE_EXTENT = (-25.0, 180.0, -11.0, 82.0)
# 旧版页面的投影（Albers 等积圆锥：标准纬线 25°N、47°N，原点纬线 38°N，中央经线 95°E），写进 GEO.proj；
# 新页面用单仓统一的投影（core/geo/config.toml）。
PROJ = (25.0, 47.0, 38.0, 95.0)      # 标准纬线1, 标准纬线2, 原点纬线, 中央经线
FIRST = 1120                          # 首屏节点（年份）：宋辽夏金四国并存，与首选视野「宋辽金夏」一致；写进 GEO.first

# ---------------------------------------------------------------- 底图简化
SIMPLIFY_LAND = 0.018
LAND_MIN_AREA = 0.004
LAND_HOLE_MIN_AREA = 0.01
SIMPLIFY_BORDER = 0.02
SIMPLIFY_RIVER = 0.015
SIMPLIFY_LAKE = 0.01
RIVER_MAX_SCALERANK = 6   # 未命名河流保留到这一级（数字越小越大）
