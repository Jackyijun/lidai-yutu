# -*- coding: utf-8 -*-
"""唐宋之际形势图 · 一键构建本卷的第 1 段：python run.py → source.json（单仓的 core/ 再由它出 v1 与新页面）。

  python run.py               底图缺失则下载 → 底图与归属（build/geo.json、data.json）→ 汇编 source.json
  python run.py --html        跳过底图与归属，只重新汇编（只改了英文译文时用）
  python run.py --draft       英文有缺译或过期时也照常汇编（缺译处显示中文）；默认会报错停下

疆域由统一疆域引擎推算（单仓根目录 python run.py tangsong），本卷不再自己算疆域、配色、出页面（2026-11 架构整理第三批起）。
"""
import argparse, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

def step(title, script, args=()):
    print(f"\n== {title} ==")
    t0 = time.time()
    r = subprocess.run([sys.executable, str(script), *args], cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"失败：{title}")
    print(f"   用时 {time.time() - t0:.1f}s")

def main():
    ap = argparse.ArgumentParser(description="构建唐宋之际形势图的第 1 段")
    ap.add_argument("--html", action="store_true", help="跳过底图与归属，只重新汇编 source.json")
    ap.add_argument("--draft", action="store_true", help="英文缺译时不报错，缺译处显示中文")
    a = ap.parse_args()
    if not a.html:
        step("下载底图（已有则跳过）", SRC / "fetch_data.py")
        step("底图与归属", SRC / "build.py")
    step("汇编 source.json", SRC / "assemble.py", ["--draft"] if a.draft else [])
    print(f"\n完成：{ROOT / 'source.json'}")

if __name__ == "__main__":
    main()
