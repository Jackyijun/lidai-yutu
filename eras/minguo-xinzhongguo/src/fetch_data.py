# -*- coding: utf-8 -*-
"""下载底图：Natural Earth（固定提交）。
仓库已附带 geodata/，离线即可构建；已有的文件会跳过，加 --force 重新下载。"""
import sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

def get(url, dst, force):
    if dst.exists() and dst.stat().st_size > 0 and not force:
        print("ok  ", dst.name); return
    print("get ", url)
    tmp = dst.with_suffix(dst.suffix + ".part")
    urllib.request.urlretrieve(url, tmp)
    tmp.replace(dst)
    print("     ", dst.stat().st_size // 1024, "KB")

def main(force=False):
    C.NE_DIR.mkdir(parents=True, exist_ok=True)
    for name in C.NE_FILES:
        get(f"{C.NE_BASE}/{name}.geojson", C.NE_DIR / f"{name}.geojson", force)

if __name__ == "__main__":
    main(force="--force" in sys.argv)
