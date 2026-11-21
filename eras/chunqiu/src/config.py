"""全部路径与可调参数。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"          # 史料内容（手写）
GEODATA = ROOT / "geodata"          # 底图数据
NE = GEODATA / "ne"                 # Natural Earth 1:10m GeoJSON
BUILD = ROOT / "build"              # 中间产物（可随时删除）；本卷的产物是 ROOT / "source.json"

# Natural Earth 固定版本（与仓库内 geodata/ne/ 完全一致）
NE_TAG = "v5.1.2"
NE_FILES = ["ne_10m_land", "ne_10m_minor_islands", "ne_10m_rivers_lake_centerlines", "ne_10m_lakes"]

# 底图裁剪范围（西, 南, 东, 北）
BBOX = (96.0, 17.5, 129.0, 45.5)
LAND_SIMPLIFY = 0.012               # 海岸线简化容差（度）

# 疆域不在本卷算：由单仓的统一疆域引擎推算（era.toml 的 [engine]），原来的栅格参数与代价栅格校验值 COST_SHA 2026-11 退役
