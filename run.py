# -*- coding: utf-8 -*-
"""历代舆图 · 单仓构建入口。

  python run.py                    八卷全部照旧构建，再更新首页；产物收进 docs/
  python run.py zhanguo songyuan   只构建这几卷（短名见 python run.py --list）
  python run.py --html             各卷跳过疆域计算，只重新拼装 HTML（须先完整构建过一次）
  python run.py --draft            英文有缺译或过期时也照常生成（缺译处显示中文），只供预览
  python run.py --hub              只更新首页：hub/index.html → docs/index.html
  python run.py --check            不构建，只核对 docs/ 与各卷产物、首页源文件是否一致
  python run.py --v1               不构建，由 docs/ 里的成品重建全局表（global/）并生成各卷 v1 数据包（build/v1/）
  python run.py --list             列出各卷短名

迁移第 1 步（2026-11）：各卷仍用自己原来的构建脚本 eras/<短名>/run.py；本脚本只负责依次调用，
再把 eras/<短名>/docs/index.html 复制到 docs/<短名>/index.html。见规范第十九节。
第 2 步：统一数据格式 v1 与全局表，见 core/v1/FORMAT.md。
"""
import argparse, hashlib, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

# (短名, 图名, 起止)；顺序即卷次
ERAS = [
    ("chunqiu",             "春秋列国形势图",             "前770—前476"),
    ("zhanguo",             "战国列国形势图",             "前475—前212"),
    ("hanmosanguo",         "汉末三国形势图",             "184—280"),
    ("liangjin-nanbeichao", "两晋十六国南北朝形势图",     "280—581"),
    ("suitang",             "隋及唐初形势图",             "581—669"),
    ("tangsong",            "唐宋之际形势图",             "755—979"),
    ("songyuan",            "宋辽夏金元形势图",           "979—1279"),
    ("minguo-xinzhongguo",  "民国至新中国初期形势图",     "1911—1954"),
]
SLUGS = [e[0] for e in ERAS]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def build_era(slug, html=False, draft=False):
    d = ROOT / "eras" / slug
    (d / "build").mkdir(exist_ok=True)   # 有的卷（如唐宋）默认 build/ 已存在，全新克隆时没有
    args = [sys.executable, "run.py"] + (["--html"] if html else []) + (["--draft"] if draft else [])
    print(f"\n==== {slug} ====", flush=True)
    t0 = time.time()
    r = subprocess.run(args, cwd=d)
    if r.returncode != 0:
        sys.exit(f"失败：{slug}")
    out = d / "docs" / "index.html"
    dst = DOCS / slug / "index.html"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(out, dst)
    print(f"==== {slug} 完成（{time.time() - t0:.0f}s）→ docs/{slug}/index.html", flush=True)


def build_hub():
    shutil.copyfile(ROOT / "hub" / "index.html", DOCS / "index.html")
    print("首页 → docs/index.html")


def check():
    bad = 0
    for slug, title, years in ERAS:
        pub, built = DOCS / slug / "index.html", ROOT / "eras" / slug / "docs" / "index.html"
        if not pub.exists():
            state = "docs/ 里缺这一卷"; bad += 1
        elif not built.exists():
            state = "本地还没构建过（无从比对）"
        elif sha(pub) == sha(built):
            state = "一致"
        else:
            state = "不一致：docs/ 不是本地最新构建的结果"; bad += 1
        print(f"  {slug:20s} {title}（{years}）  {state}")
    hub = "一致" if sha(DOCS / "index.html") == sha(ROOT / "hub" / "index.html") else "不一致"
    if hub != "一致":
        bad += 1
    print(f"  {'hub':20s} 历代舆图首页  {hub}")
    return bad


def main():
    ap = argparse.ArgumentParser(description="历代舆图单仓构建")
    ap.add_argument("eras", nargs="*", metavar="短名", help="只构建这几卷；不写则全部")
    ap.add_argument("--html", action="store_true", help="各卷只重新拼装 HTML")
    ap.add_argument("--draft", action="store_true", help="英文缺译时也照常生成")
    ap.add_argument("--hub", action="store_true", help="只更新首页")
    ap.add_argument("--check", action="store_true", help="只核对 docs/ 是否最新")
    ap.add_argument("--v1", action="store_true", help="重建全局表并生成各卷 v1 数据包")
    ap.add_argument("--list", action="store_true", help="列出各卷短名")
    a = ap.parse_args()
    if a.list:
        for slug, title, years in ERAS:
            print(f"{slug:20s} {title}（{years}）")
        return
    if a.check:
        sys.exit(1 if check() else 0)
    if a.v1:
        v1 = ROOT / "core" / "v1"
        for script, extra in (("registry.py", []), ("build.py", a.eras)):
            r = subprocess.run([sys.executable, str(v1 / script)] + extra, cwd=ROOT)
            if r.returncode != 0:
                sys.exit(f"失败：core/v1/{script}")
        return
    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").touch()
    if not a.hub:
        unknown = [e for e in a.eras if e not in SLUGS]
        if unknown:
            sys.exit(f"没有这一卷：{'、'.join(unknown)}（python run.py --list 查看）")
        for slug in (a.eras or SLUGS):
            build_era(slug, a.html, a.draft)
    build_hub()


if __name__ == "__main__":
    main()
