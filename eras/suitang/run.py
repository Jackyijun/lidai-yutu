# 隋至盛唐形势图 · 一键构建本卷的第 1 段：python run.py → source.json（单仓的 core/ 再由它出 v1 与新页面）
#   python run.py            检查底图 → 底图（build/geo_base.json）→ 汇编 → source.json
#   python run.py --html     已有底图就不重做，只重新汇编（只改了 content/ 的文字或英文译文时用）
#   python run.py --draft    英文缺译时也照常汇编（缺译处显示中文）
# 疆域由统一疆域引擎推算（单仓根目录 python run.py suitang），本卷不再自己算疆域、出页面（2026-11 架构整理第三批起）。
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'content')]


def main():
    ap = argparse.ArgumentParser(description='隋至盛唐形势图 第 1 段构建')
    ap.add_argument('--html', action='store_true', help='已有底图就不重做，只重新汇编')
    ap.add_argument('--draft', action='store_true', help='英文缺译时也照常汇编（缺译处显示中文）')
    a = ap.parse_args()
    import build, assemble
    build.main(full=not a.html)
    assemble.main(draft=a.draft)


if __name__ == '__main__':
    main()
