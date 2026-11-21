# 全部路径与可调参数
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEODATA = ROOT / 'geodata'
CONTENT = ROOT / 'content'
BUILD = ROOT / 'build'            # 中间产物；本卷的产物是 ROOT / 'source.json'

# ---------------- 底图 ----------------
EXT = (50, 2, 150, 62)            # 河湖国界数据范围 [西, 南, 东, 北]
LEXT = (20, -12, 176, 72)         # 陆地范围（大于任何视野，免出现假海岸）
VIEW_EXT = [56, 142, 8, 57]       # 页面「全图」范围 [西, 东, 南, 北]

# 疆域由单仓的统一疆域引擎推算（era.toml 的 [engine]；外缘仍是 content/frontier.py），颜色由单仓的 global/palette.toml 定：
# 本卷原来的势力格栅格、代价与界线参数 2026-11 架构整理第三批起退役。
