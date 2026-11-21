# 全部路径与可调参数
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEODATA = ROOT / 'geodata'
CONTENT = ROOT / 'content'
BUILD = ROOT / 'build'            # 中间产物；本卷的产物是 ROOT / 'source.json'

# ---------------- 底图 ----------------
EXT = (18, -13, 152, 62)          # 河湖国界数据范围 [西, 南, 东, 北]
LEXT = (-5, -24, 180, 74)         # 陆地范围（大于任何视野，免出现假海岸）
VIEW_EXT = [20, 150, -12, 58]     # 页面「全图」范围 [西, 东, 南, 北]

# 疆域由单仓的统一疆域引擎推算（era.toml 的 [engine]；外缘仍是 content/frontier.py），颜色由单仓的 global/palette.toml 定：
# 本卷原来的势力格栅格、代价与界线参数 2026-11 架构整理第三批起退役。

# ---------------- 衔接（规范第十八节） ----------------
# 280 节点的归属取《汉末三国形势图》280 年疆域（该图范围内），581 节点取《隋及唐初形势图》581 年疆域（该图外缘内）。
# 两份 json 是 2026-11 前从两卷旧版页面提取的疆域环（原 tools/junction.py），现冻结为归属输入，只读 frame 与各政权的 rings；
# 衔接节点画出来的疆域由单仓 core/v1/engine_geom.py 取邻卷的 engine.json。
JUNCTION_HANMO = GEODATA / 'junction_hanmo280.json'
JUNCTION_SUITANG = GEODATA / 'junction_suitang581.json'
HANMO_FRAME = (72.0, 14.75, 136.0, 55.0)   # 汉末三国图疆域推算范围 [西, 南, 东, 北]
