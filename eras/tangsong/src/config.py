# -*- coding: utf-8 -*-
"""唐宋之际形势图 · 构建参数。

改这里会影响底图的范围与精度；史料内容（州府、归属、战役等）在 content/ 目录。改完参数后重新运行 `python run.py`。
疆域由单仓的统一疆域引擎推算（era.toml 的 [engine]），颜色由单仓的 global/palette.toml 定：本卷原来的栅格、
通行代价、疆域多边形与配色参数 2026-11 架构整理第三批起退役。
"""
from pathlib import Path

# ---------------------------------------------------------------- 路径
ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"          # 手写的史料内容
GEODATA = ROOT / "geodata"          # 底图数据
NE_DIR = GEODATA / "ne"             # Natural Earth 1:10m GeoJSON
PROV_JSON = GEODATA / "prov.json"   # 今省界（简化）
BUILD = ROOT / "build"              # 中间产物 geo.json / data.json；本卷的产物是 ROOT / "source.json"

# ---------------------------------------------------------------- 底图来源
# Natural Earth 矢量数据（公有领域），固定到一个提交，保证可复现。
NE_COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"
NE_BASE = f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{NE_COMMIT}/geojson"
NE_FILES = [
    "ne_10m_land",                        # 海陆
    "ne_10m_minor_islands",               # 小岛
    "ne_10m_lakes",                       # 湖泊
    "ne_10m_lakes_historic",              # 历史湖泊（罗布泊）
    "ne_10m_rivers_lake_centerlines",     # 河流
    "ne_10m_admin_0_boundary_lines_land", # 今国界
    "ne_10m_geography_regions_polys",     # 山地、沙漠多边形
]

# ---------------------------------------------------------------- 首屏
FIRST = 820                           # 打开网页时显示的时间节点（年份），写入 GEO.first

# ---------------------------------------------------------------- 范围
# 底图裁到这个范围（旧构建的疆域栅格也是这个范围，写入 GEO.ext）。
EXTENT = (72.0, 136.0, 10.0, 55.0)   # 经度 min, max, 纬度 min, max（2026-11-22 南扩到 10°N，收进吴哥与湄公河三角洲；同宋元卷）

# ---------------------------------------------------------------- 底图简化
SIMPLIFY_LAND = 0.015
LAND_MIN_AREA = 0.004
LAND_HOLE_MIN_AREA = 0.01
SIMPLIFY_BORDER = 0.02
SIMPLIFY_RIVER = 0.015
SIMPLIFY_LAKE = 0.01
