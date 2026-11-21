# -*- coding: utf-8 -*-
"""汉末三国形势图 · 全部路径与可调参数。

疆域由单仓的统一疆域引擎推算（era.toml 的 [engine]），颜色由单仓的 global/palette.toml 定：本卷原来的栅格、
通行代价、外缘与多边形参数，以及只给代价栅格用的 ETOPO20 地形，2026-11 架构整理第三批起退役。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
GEODATA = ROOT / "geodata"
BUILD = ROOT / "build"                # 中间产物；本卷的产物是 ROOT / "source.json"

FIRST_YEAR = 229              # 首屏节点
