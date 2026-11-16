# -*- coding: utf-8 -*-
"""秦汉形势图的路径与常量。疆域推算的参数不在这里：统一引擎的设置见 core/engine/config.toml 与 era.toml [engine]。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent.parent
CONTENT = ROOT / "content"
GEODATA = ROOT / "geodata"
BUILD = ROOT / "build"
DOCS = ROOT / "docs"
TEMPLATE = ROOT / "src" / "template.html"
OUT_HTML = DOCS / "index.html"
NE = REPO / "geodata" / "ne"

EXT = (50.0, 2.0, 152.0, 62.0)      # 河湖、国界数据范围 [西, 南, 东, 北]
VIEW = [55.0, 145.0, 8.0, 58.0]      # 页面「全图」范围 [西, 东, 南, 北]，也是疆域推算范围
HM_BOX = (72.0, 14.0, 136.0, 55.0)   # 汉末卷底图的范围：其内的河湖沿用汉末卷，其外取 Natural Earth

TAICHU = -104                        # 太初改历：此前以十月为岁首
FIRST = (-108, 9)                    # 首屏节点：前108 年（元封三年，年末取九月）
