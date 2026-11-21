# -*- coding: utf-8 -*-
"""民国至新中国初期形势图 · 一键构建本卷的第 1 段：python run.py → source.json（单仓的 core/ 再由它出 v1 与新页面）。

  python run.py               检查史料 → 底图缺失则下载 → 节点归属与底图（build/）→ source.json
  python run.py --html        跳过前三步，只重新汇编 source.json（只改了英文时用）
  python run.py --draft       英文有缺译或过期时也照常汇编（缺译处显示中文），只给警告

疆域由统一疆域引擎推算（单仓根目录 python run.py minguo-xinzhongguo），本卷不再自己算疆域、出页面（2026-11 架构整理第三批起）。
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
    ap = argparse.ArgumentParser(description="民国至新中国初期形势图 第 1 段构建")
    ap.add_argument("--html", action="store_true", help="跳过前三步，只重新汇编 source.json")
    ap.add_argument("--draft", action="store_true", help="英文缺译时也照常汇编（缺译处显示中文）")
    a = ap.parse_args()
    if not a.html:
        step("检查史料", ROOT / "tools" / "check.py")
        step("下载底图（已有则跳过）", SRC / "fetch_data.py")
        step("节点归属与底图", SRC / "build.py")
    step("汇编 source.json", SRC / "assemble.py", ["--draft"] if a.draft else [])
    print(f"\n完成：{ROOT / 'source.json'}")

if __name__ == "__main__":
    main()
