# -*- coding: utf-8 -*-
"""把 build/geo.json、build/data.json 汇编成本卷的 source.json（单仓第 1 段的产物）。
英文与中文写在同一处（content/ 各文件），不另设译文表。
source.json 是旧版页面里内嵌的 GEO、DATA；本卷的疆域本来就由统一引擎出（第二遍构建填进来），所以连同疆域一起写，
不含配色：颜色由单仓的 global/palette.toml 定，新页面由单仓 core/web/ 生成（架构整理第三批起本卷不再出页面）。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402
sys.path.insert(0, str(C.REPO / "core" / "v1"))
import legacy  # noqa: E402


def main():
    geo = json.loads((C.BUILD / "geo.json").read_text(encoding="utf8"))
    data = json.loads((C.BUILD / "data.json").read_text(encoding="utf8"))
    out = C.ROOT / "source.json"
    legacy.write_source(out, geo, data)
    print(f"   {out.relative_to(C.ROOT)}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
