# -*- coding: utf-8 -*-
"""汉末三国形势图 · 全部路径与可调参数。

疆域由单仓的统一疆域引擎推算（era.toml 的 [engine]），颜色由单仓的 global/palette.toml 定：本卷原来的栅格、
通行代价、外缘与多边形参数，以及只给代价栅格用的 ETOPO20 地形，2026-11 架构整理第三批起退役。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
GEODATA = ROOT / "geodata"
BUILD = ROOT / "build"                # 中间产物；本卷的产物是 ROOT / "source.json"

# ---------------------------------------------------------------- 归属范围
# 统一引擎的可达倍数由旧算法的分区半径折算（build.py 的 write_reach）：旧算法里每个种子最远能“够到”的代价距离
# = 半径 × REACH_MULT，半径取 seeds.py 里的 R，缺省按类型。
REACH_DEFAULT = {"z": 2.6, "c": 1.6, "r": 2.2}
REACH_MULT = 1.45
REACH_ENGINE_SCALE = 1.5      # 单仓统一引擎（第 7 步）折算可达倍数时再乘的系数，见 build.py 的 write_reach
REACH_ENGINE_ADJ = {"带方": 0.5}   # 个别点在统一引擎里再乘的系数：带方照折算会越过汉江覆盖三韩

FIRST_YEAR = 229              # 首屏节点
