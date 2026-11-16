# -*- coding: utf-8 -*-
"""秦汉形势图 · 构建。

  python run.py            史料 → 归属与条目（有统一引擎的结果就填入疆域）→ docs/index.html
  python run.py --html     只重新拼装 HTML（只改了 src/template.html 时用）
  python run.py --base     先重新生成底图 geodata/base.json（改了 src/basemap.py 时用）

疆域由统一引擎推算（core/engine），要在仓库根目录用 python run.py qinhan 构建：它先出一遍归属、转成 v1 数据包、
推算疆域，再回到这里填入疆域出页面。
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"


def step(title, script):
    print(f"\n== {title} ==")
    t0 = time.time()
    if subprocess.run([sys.executable, str(script)], cwd=ROOT).returncode != 0:
        sys.exit(f"失败：{title}")
    print(f"   用时 {time.time() - t0:.1f}s")


def main():
    a = sys.argv[1:]
    if "--base" in a:
        step("底图", SRC / "basemap.py")
    if "--html" not in a:
        step("归属、条目与疆域", SRC / "build.py")
    step("拼装 HTML", SRC / "assemble.py")
    print(f"\n完成：{ROOT / 'docs' / 'index.html'}")


if __name__ == "__main__":
    main()
