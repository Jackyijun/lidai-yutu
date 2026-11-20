# -*- coding: utf-8 -*-
"""历代舆图 · 单仓构建入口。

  python run.py                    九卷全部构建：各卷算疆域 → v1 数据 → 新页面，再更新首页；产物收进 docs/
  python run.py zhanguo songyuan   只构建这几卷（短名见 python run.py --list）
  python run.py --html             各卷跳过疆域计算，只重新拼装（须先完整构建过一次）
  python run.py --draft            英文有缺译或过期时也照常生成（缺译处显示中文），只供预览
  python run.py --web              不重算各卷，只由 eras/<短名>/legacy.html 重建全局表、v1 数据和新页面
  python run.py --v1               只重建全局表（global/）与各卷 v1 数据包（build/v1/），不出页面
  python run.py --geo              重新生成地形晕渲与全球底图（geodata/relief/、geodata/world/），再出新页面；
                                   改了 core/geo/config.toml 里投影、分档、底图的参数后用。第一次运行会下载晕渲原图（约 42 MB）
  python run.py --engine           统一疆域引擎陪跑：由 v1 数据重算疆域（build/engine/），逐节点与旧引擎画的疆域比对，不改页面；
                                   只做 era.toml 里有 [engine] 的卷，也可指定短名
                                   （秦汉卷的疆域本来就由引擎出图：python run.py qinhan 时自动两遍构建，见 eras/qinhan/run.py；
                                    已换到引擎的旧卷（[engine] geometry = "engine"，第 7 步）构建时自动重算 eras/<短名>/engine.json）
  python run.py --hub              只更新首页：hub/index.html → docs/index.html
  python run.py --check            不构建，只核对 docs/ 与各卷成品、首页源文件是否一致
  python run.py --list             列出各卷短名

构建分三段（规范第十九节）：
  1. 各卷仍用自己原来的构建脚本 eras/<短名>/run.py 推算疆域、拼成旧版页面，存为 eras/<短名>/legacy.html（入库，是数据来源）；
  2. core/v1/registry.py 由九卷 legacy.html 重建全局表，core/v1/build.py 转成 v1 数据包并套用第 3 步的改正（build/v1/，不入库）；
  3. core/web/assemble.py 由 v1 数据生成新页面 docs/<短名>/index.html（共用时间轴、深链接等，见 core/web/）；
     统一投影、全球底图、地形晕渲（第 4 步）由 core/geo/ 预先生成到 geodata/relief/、geodata/world/（入库），出页面时并入。
统一疆域引擎（第 5 步）在 core/engine/。第 7 步起旧卷逐个换过去：era.toml [engine] 写 geometry = "engine" 的卷，
第 1 段照旧出归属、文字与条目，疆域则由引擎按 v1 数据推算，结果存为 eras/<短名>/engine.json（入库），第 2 段生成 v1 时换进去
（core/v1/engine_geom.py；衔接节点按 global/junctions.toml 照搬为准的一卷）。各卷都换完后，第 1 段的疆域计算退役。
"""
import argparse, hashlib, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

# (短名, 图名, 起止)；顺序即卷次
ERAS = [
    ("chunqiu",             "春秋列国形势图",             "前770—前476"),
    ("zhanguo",             "战国列国形势图",             "前475—前212"),
    ("qinhan",              "秦汉形势图",                 "前212—184"),
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
    """第 1 段：各卷原来的构建脚本 → eras/<短名>/legacy.html"""
    d = ROOT / "eras" / slug
    (d / "build").mkdir(exist_ok=True)   # 有的卷（如唐宋）默认 build/ 已存在，全新克隆时没有
    args = [sys.executable, "run.py"] + (["--html"] if html else []) + (["--draft"] if draft else [])
    print(f"\n==== {slug} ====", flush=True)
    t0 = time.time()
    r = subprocess.run(args, cwd=d)
    if r.returncode != 0:
        sys.exit(f"失败：{slug}")
    shutil.copyfile(d / "docs" / "index.html", d / "legacy.html")
    print(f"==== {slug} 完成（{time.time() - t0:.0f}s）→ eras/{slug}/legacy.html", flush=True)


def run_core(eras, web=True, geo=False, lenient=False):
    """第 2、3 段：全局表 → v1 数据 →（地形晕渲与全球底图）→ 新页面。
    lenient：已换到引擎的卷 engine.json 过期时先用旧几何（重算疆域之前出 v1 用）"""
    steps = [("v1/registry.py", []), ("v1/build.py", eras + (["--lenient"] if lenient else []))]
    if geo: steps += [("geo/relief.py", eras), ("geo/world.py", eras)]
    if web: steps += [("web/assemble.py", eras)]
    for script, extra in steps:
        r = subprocess.run([sys.executable, str(ROOT / "core" / script)] + extra, cwd=ROOT)
        if r.returncode != 0:
            sys.exit(f"失败：core/{script}")


def production_eras():
    """疆域直接由统一引擎出图的卷（era.toml [engine] production = true）：两遍构建"""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    return [s for s in SLUGS if tomllib.loads((ROOT / "eras" / s / "era.toml").read_text(encoding="utf8")).get("engine", {}).get("production")]


def engine_pass(slugs, html=False, draft=False, v1_fresh=False):
    """第一遍出的归属 → v1 → 统一引擎推算疆域 → 再构建一遍，把疆域填回去"""
    todo = [s for s in slugs if s in production_eras()]
    if not todo or html:
        return False
    if not v1_fresh:
        run_core([], web=False, lenient=True)
    for slug in todo:
        r = subprocess.run([sys.executable, str(ROOT / "core" / "engine" / "build.py"), slug], cwd=ROOT)
        if r.returncode != 0:
            sys.exit(f"失败：core/engine/build.py {slug}")
        build_era(slug, html, draft)
    return True


def migrated_eras():
    """第 7 步已换到统一引擎的旧卷（era.toml [engine] geometry = "engine"）"""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    return [s for s in SLUGS if tomllib.loads((ROOT / "eras" / s / "era.toml").read_text(encoding="utf8")).get("engine", {}).get("geometry") == "engine"]


def engine_pages(slugs, html=False, v1_fresh=False):
    """已换到引擎的旧卷：按刚出的归属重算疆域 → eras/<短名>/engine.json（入库），第 2 段生成 v1 时换进去。
    返回是否刚出过一遍 v1"""
    todo = [s for s in slugs if s in migrated_eras()]
    if not todo or html:
        return v1_fresh
    if not v1_fresh:
        run_core([], web=False, lenient=True)
    for slug in todo:
        r = subprocess.run([sys.executable, str(ROOT / "core" / "engine" / "build.py"), slug], cwd=ROOT)
        if r.returncode != 0:
            sys.exit(f"失败：core/engine/build.py {slug}")
        shutil.copyfile(ROOT / "build" / "engine" / f"{slug}.json", ROOT / "eras" / slug / "engine.json")
        print(f"==== {slug} 疆域 → eras/{slug}/engine.json", flush=True)
    return True


def engine_eras():
    """era.toml 里有 [engine] 的卷"""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    return [s for s in SLUGS if "engine" in tomllib.loads((ROOT / "eras" / s / "era.toml").read_text(encoding="utf8")) and s not in production_eras()]


def run_engine(eras):
    """第 5 步：统一疆域引擎陪跑。先重建九卷的 v1 数据（全局山脉取自九卷），再逐卷推算疆域、与现有页面比对"""
    run_core([], web=False, lenient=True)
    todo = eras or engine_eras()
    for slug in todo:
        for script in ("engine/build.py", "engine/regress.py"):
            r = subprocess.run([sys.executable, str(ROOT / "core" / script), slug], cwd=ROOT)
            if r.returncode != 0:
                sys.exit(f"失败：core/{script} {slug}")
    print("\n比对结果在 build/engine/<短名>.regress.json；页面没有改动（已换到引擎的卷，比的是旧引擎画的 legacy.html）")


def build_hub():
    shutil.copyfile(ROOT / "hub" / "index.html", DOCS / "index.html")
    print("首页 → docs/index.html")


def check():
    sys.path.insert(0, str(ROOT / "core" / "web"))
    sys.path.insert(0, str(ROOT / "core" / "v1"))
    import json
    import assemble
    bad = 0
    for slug, title, years in ERAS:
        leg, built, pub = ROOT / "eras" / slug / "legacy.html", ROOT / "eras" / slug / "docs" / "index.html", DOCS / slug / "index.html"
        v1 = ROOT / "build" / "v1" / f"{slug}.json"
        notes = []
        if not leg.exists():
            notes.append("缺 legacy.html"); bad += 1
        elif built.exists() and sha(leg) != sha(built):
            notes.append("legacy.html 不是本地最新构建的结果"); bad += 1
        if not pub.exists():
            notes.append("docs/ 里缺这一卷"); bad += 1
        elif not v1.exists():
            notes.append("还没生成 v1 数据（无从比对新页面）")
        else:
            b = json.loads(v1.read_text(encoding="utf8"))
            if assemble.render(slug, b) != pub.read_text(encoding="utf8"):
                notes.append("docs/ 不是由当前 v1 数据生成的"); bad += 1
            if slug in migrated_eras():
                sys.path.insert(0, str(ROOT / "core" / "engine"))
                import data as DA
                eng = ROOT / "eras" / slug / "engine.json"
                if not eng.exists() or json.loads(eng.read_text(encoding="utf8"))["meta"].get("input") != DA.fingerprint(slug, b):
                    notes.append("engine.json 不是按当前归属算的（python run.py " + slug + " 重算）"); bad += 1
        print(f"  {slug:20s} {title}（{years}）  {'；'.join(notes) or '一致'}")
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
    ap.add_argument("--web", action="store_true", help="不重算各卷，只重建全局表、v1 数据和新页面")
    ap.add_argument("--v1", action="store_true", help="只重建全局表与 v1 数据包")
    ap.add_argument("--geo", action="store_true", help="重新生成地形晕渲与全球底图，再出新页面")
    ap.add_argument("--engine", action="store_true", help="统一疆域引擎陪跑：重算疆域并与现有页面比对，不改页面")
    ap.add_argument("--hub", action="store_true", help="只更新首页")
    ap.add_argument("--check", action="store_true", help="只核对 docs/ 是否最新")
    ap.add_argument("--list", action="store_true", help="列出各卷短名")
    a = ap.parse_args()
    if a.list:
        for slug, title, years in ERAS:
            print(f"{slug:20s} {title}（{years}）")
        return
    if a.check:
        sys.exit(1 if check() else 0)
    unknown = [e for e in a.eras if e not in SLUGS]
    if unknown:
        sys.exit(f"没有这一卷：{'、'.join(unknown)}（python run.py --list 查看）")
    if a.engine:
        run_engine(a.eras)
        return
    if a.v1 or a.web or a.geo:
        run_core(a.eras, web=a.web or a.geo, geo=a.geo)
        return
    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").touch()
    if not a.hub:
        for slug in (a.eras or SLUGS):
            build_era(slug, a.html, a.draft)
        # 已换到引擎的旧卷先重算 engine.json：秦汉卷第二遍构建要照搬战国卷（前212）、汉末卷（184）的引擎疆域
        fresh = engine_pages(a.eras or SLUGS, a.html)
        engine_pass(a.eras or SLUGS, a.html, a.draft, v1_fresh=fresh)
        run_core(a.eras)
    build_hub()


if __name__ == "__main__":
    main()
