# -*- coding: utf-8 -*-
"""汉末三国形势图 · 一键构建本卷的第 1 段：python run.py → source.json（单仓的 core/ 再由它出 v1 与新页面）。

  python run.py               检查底图 → 底图与归属（build/geo.json、data.json、reach.txt）→ 汇编 source.json
  python run.py --html        跳过底图与归属，只重新汇编（只改了英文译文时用）
  python run.py --draft       英文有缺译或过期时也照常汇编（缺译处临时显示中文），只给警告

疆域由统一疆域引擎推算（单仓根目录 python run.py hanmosanguo），本卷不再自己算疆域、出页面（2026-11 架构整理第三批起）。
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
    ap = argparse.ArgumentParser(description="构建汉末三国形势图的第 1 段")
    ap.add_argument("--html", action="store_true", help="跳过底图与归属，只重新汇编 source.json")
    ap.add_argument("--draft", action="store_true", help="英文缺译或过期时不停下，缺译处显示中文")
    a = ap.parse_args()
    if not a.html:
        step("检查底图", SRC / "fetch_data.py")
        step("底图与归属", SRC / "build.py")
    step("汇编 source.json（并入英文）", SRC / "assemble.py", ["--draft"] if a.draft else [])
    print(f"\n完成：{ROOT / 'source.json'}")

if __name__ == "__main__":
    main()
