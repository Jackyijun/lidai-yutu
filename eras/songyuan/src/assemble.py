# -*- coding: utf-8 -*-
"""把 build/geo.json、build/data.json 与 content/en/ 的英文汇编成本卷的 source.json（单仓第 1 段的产物）。

  python src/assemble.py           严格：有缺译或过期的英文就报错退出
  python src/assemble.py --draft   草稿：缺译、过期处临时显示中文，只给警告

source.json 是旧版页面里内嵌的 GEO、DATA，不含疆域与配色：疆域由统一疆域引擎推算（本卷的 engine.json），
颜色由单仓的 global/palette.toml 定，新页面由单仓 core/web/ 生成（架构整理第三批起本卷不再出页面）。
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import i18n
sys.path.insert(0, str(C.ROOT.parent.parent / "core" / "v1"))
import legacy

def check_english(geo, data, draft):
    missing, stale, unlocked = i18n.check(geo, data)
    from collections import Counter
    bad = missing + stale
    if unlocked:
        print(f"   提醒：{len(unlocked)} 条英文未登记指纹（改完英文后运行 python tools/i18n.py lock）")
    if not bad:
        print("   英文：齐全")
        return
    msg = (f"英文缺译 {len(missing)} 条、过期 {len(stale)} 条："
           + "、".join(f"{f} {n}" for f, n in Counter(f for f, _, _ in bad).items())
           + "。运行 python tools/i18n.py todo 查看清单。")
    if not draft:
        sys.exit("   " + msg + "\n   如只想先看效果，用 python run.py --html --draft（缺译处显示中文）。")
    print("   草稿模式，" + msg)


def main():
    draft = "--draft" in sys.argv[1:]
    geo = json.loads((C.BUILD / "geo.json").read_text(encoding="utf8"))
    data = json.loads((C.BUILD / "data.json").read_text(encoding="utf8"))
    check_english(geo, data, draft)
    geo, data = i18n.attach(geo, data)
    geo["first"] = C.FIRST
    out = C.ROOT / "source.json"
    legacy.write_source(out, geo, data, inline=False)    # 旧版页面的疆域环存在几何池 GEO.pool 里，新页面照旧
    print("wrote", out, out.stat().st_size // 1024, "KB")

if __name__ == "__main__":
    main()
