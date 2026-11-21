# -*- coding: utf-8 -*-
"""检查底图：geodata/base.json 随仓库附带。原来另下载 ETOPO20 地形给代价栅格用，2026-11 起本卷不再自己算疆域，不再需要。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

def main():
    if not (C.GEODATA / "base.json").exists():
        sys.exit("缺少 geodata/base.json（底图），请从仓库重新获取")
    print("   底图齐全")

if __name__ == "__main__":
    main()
