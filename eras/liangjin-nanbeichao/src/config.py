# 全部路径与可调参数
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEODATA = ROOT / 'geodata'
CONTENT = ROOT / 'content'
BUILD = ROOT / 'build'
DOCS = ROOT / 'docs'
SRC = ROOT / 'src'

TITLE = '两晋十六国南北朝形势图'
REPO = 'https://github.com/Jackyijun/liangjin-nanbeichao-map'

# ---------------- 底图 ----------------
EXT = (18, -13, 152, 62)          # 河湖国界数据范围 [西, 南, 东, 北]
LEXT = (-5, -24, 180, 74)         # 陆地范围（大于任何视野，免出现假海岸）
VIEW_EXT = [20, 150, -12, 58]     # 页面「全图」范围 [西, 东, 南, 北]

# ---------------- 疆域栅格（规范第十三节） ----------------
# 投影与《隋及唐初形势图》相同（102°E / 36°N），581 年衔接节点在两图上逐像素一致
GRID_BOX = (18, 150, -12, 56)     # 计算范围 [西, 东, 南, 北]（须盖住 content/frontier.py 的外缘）
GRID_CLIP = True                  # 栅格只建在外缘之内（外缘外接矩形 + 边距），省内存
PX = 1.0                          # 格边长（投影单位，1 单位 ≈ 6.37 km；约 0.057°）
BIG_LAKE = 0.15                   # 面积（平方度）以上的湖不可通行
SEED_SNAP = 15                    # 归属点落在海里时，向最近陆地格挪动的最大格数

# 代价：平地 1 + 坡度 + 高原 + 山脊带 + 界河，再乘多尺度噪声（与隋唐图相同）
SLOPE_K = 0.32
SLOPE_MAX = 40
PLATEAU = (3000, 4500, 0.8)
RIDGE_MAJOR = 8.0
RIDGE_MINOR = 3.5
RIDGE_W = 1.6
RIDGE_MIN_LEN = 0.8
RIDGE_WIGGLE = 0.07
RIVER_W = 1.1
BORDER_RIVERS = {                 # 唐宋图条目号 / 补充河流键 → 加价
    11: 5.0,   # 江
    43: 5.0,   # 河
    32: 5.0,   # 淮水：南北朝长期以淮为界，比隋唐图加重
    15: 2.5,   # 汉水
    42: 2.5,   # 汉江
    'amu': 2.5,  # 乌浒水
    'syr': 2.0,  # 药杀水
    'euph': 2.5,  # 幼发拉底河：罗马与波斯的界河
}
NOISE_AMP = 0.38
NOISE_SCALES = ((3, .25), (8, .35), (20, .40))
SEED = 383                        # 随机种子（固定，保证逐字节可重建）

# 界线形状
WARP = ((4.0, 0.7), (10.0, 0.9))
SMOOTH_SIGMA = 1.2
LAPLACE = (0.5, 3)
MIN_FACE = 2.0
SIMPLIFY = 0.06
FILL_SEA = 6
MIN_PART = 0.3

# ---------------- 衔接（规范第十八节） ----------------
# 280 节点取《汉末三国形势图》280 年疆域（该图范围内），581 节点取《隋及唐初形势图》581 年疆域（该图外缘内）
JUNCTION_HANMO = GEODATA / 'junction_hanmo280.json'
JUNCTION_SUITANG = GEODATA / 'junction_suitang581.json'
HANMO_FRAME = (72.0, 14.75, 136.0, 55.0)   # 汉末三国图疆域推算范围 [西, 南, 东, 北]
