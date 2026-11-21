"""一键构建本卷的第 1 段：python run.py  →  source.json（单仓的 core/ 再由它出 v1 与新页面）

  python run.py              底图缺失则下载 → 底图与点要素归属（build/geo.json）→ 汇编 source.json
  python run.py --html       跳过底图与归属，只重新汇编（只改了 content/features.py 里的文字或英文译文时用）
  python run.py --draft      英文有缺译时也照样汇编（缺译处临时显示中文），只供预览

疆域由统一疆域引擎推算（单仓根目录 python run.py chunqiu），本卷不再自己算疆域、出页面（2026-11 架构整理第三批起）。
"""
import argparse, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

def step(name, script, *args):
    t = time.time()
    print(f"── {name}")
    r = subprocess.run([sys.executable, str(SRC / script), *args], cwd=ROOT)
    if r.returncode:
        sys.exit(f"失败：{script}")
    print(f"   完成（{time.time() - t:.1f}s）")

def main():
    ap = argparse.ArgumentParser(description="构建春秋列国形势图的第 1 段")
    ap.add_argument("--html", action="store_true", help="只重新汇编 source.json")
    ap.add_argument("--draft", action="store_true", help="允许英文缺译或过期，只供预览")
    a = ap.parse_args()
    if not a.html:
        step("检查底图", "fetch_data.py")
        step("底图与归属", "build.py")
    elif not (ROOT / "build" / "geo.json").exists():
        sys.exit("build/geo.json 不存在，请先完整运行一次 python run.py")
    step("汇编 source.json", "assemble.py", *(["--draft"] if a.draft else []))
    out = ROOT / "source.json"
    print(f"完成：{out}（{out.stat().st_size // 1024} KB）")

if __name__ == "__main__":
    main()
