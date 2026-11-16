# -*- coding: utf-8 -*-
"""新版页面：v1 数据包 → docs/<短名>/index.html（规范第十九节第 3、4 步）。

  python core/web/assemble.py              各卷全部
  python core/web/assemble.py songyuan     只做这几卷

数据来源是 core/v1/build.py 生成的 build/v1/<短名>.json（已附全局 ID）。各卷的史料与疆域仍由各卷自己的
构建脚本算出，成品存为 eras/<短名>/legacy.html（入库），v1 由它无损转出。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core" / "v1"))
sys.path.insert(0, str(ROOT / "core" / "geo"))
import legacy
from registry import ERAS
import patch
import geo

HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>[hidden]{display:none!important}</style>
"""


def dumps(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def template_for(slug):
    return (ROOT / "eras" / slug / "src" / "template.html").read_text(encoding="utf8")


def item_year(o):
    if o.get("t") is not None:
        return o["t"] // 12
    if o.get("spans"):
        return int(o["spans"][0][0]) // 12
    return None


def tokens(b):
    """深链接用的标识：政权 polity:<全局 ID>，地点 place:<全局 ID>，条目 <类别>:<全局 ID 或古名>；同卷重名再加 @所属政权 或 @年份"""
    from collections import Counter, defaultdict
    pols = b["polities"]
    first = lambda g: g[0][1] if isinstance(g, list) else g
    simple = b["model"] == "simple"
    alias = {}
    base = []
    for o in b["items"]:
        g = o.get("gid")
        g = first(g) if g else None
        base.append(g if g and ":" in g else f"{o['c']}:{g or o['old']}")
    cnt = Counter(base)
    out, seen = [], defaultdict(int)
    pkey = {p["key"]: p["gid"] for p in pols}
    for o, t in zip(b["items"], base):
        if cnt[t] > 1:
            st = o.get("st")
            sg = pols[st]["gid"] if isinstance(st, int) and 0 <= st < len(pols) else pkey.get(st)
            y = item_year(o)
            t = t + "@" + (sg if o["c"] == "capital" and sg else str(y) if y is not None else "")
        seen[t] += 1
        out.append(t if seen[t] == 1 else f"{t}.{seen[t]}")
    if simple:
        # 战国式：政权也是条目（按 item 序号）；城邑类条目兼认 place:<全局 ID>
        n = len(b["items"]) + len(pols)
        arr = [None] * n
        for o, t in zip(b["items"], out):
            arr[o["i"]] = t
        for p in pols:
            arr[p["item"]] = "polity:" + p["gid"]
        places = {first(p["gid"]) for p in b["places"]}
        for o in b["items"]:
            g = o.get("gid")
            if g and not isinstance(g, list) and g in places:
                alias.setdefault("place:" + g, o["i"])
        return {"i": arr}, alias
    u = ["polity:" + p["gid"] for p in pols]
    s = []
    for k, p in enumerate(b["places"]):
        g = p["gid"]
        s.append("place:" + first(g))
        if isinstance(g, list):
            for _, g2 in g[1:]:
                alias.setdefault("place:" + g2, f"s:{k}")
    return {"u": u, "s": s, "i": out}, alias


def shorts(b, G):
    """时间轴短标题：节点自带的 short / en.short"""
    for n, s in zip(b["nodes"], G["snaps"]):
        if n.get("short"):
            s["sh"] = n["short"]
            if n.get("en", {}).get("short"):
                s["she"] = n["en"]["short"]


def render(slug, b, template=None, new=True):
    G, D, colors = legacy.from_v1(b)
    t = template if template is not None else template_for(slug)
    if new:
        shorts(b, G)
        gids, alias = tokens(b)
        simple = "__UCSS_LIGHT__" not in t
        t = patch.patch_simple(t, slug) if simple else patch.patch_layered(t, slug)
        t = patch.patch_geo(t, geo.load(), simple)          # 第 4 步：统一投影、全球底图、地形晕渲
        geo.apply(slug, G)
        t = t.replace("__GIDS__", dumps(gids)).replace("__ALIAS__", dumps(alias))
    if "__UCSS_LIGHT__" in t:                       # 唐宋系：疆域色写成 --u-<序号>
        light = " ".join(f"--u-{i}:{c[0]};" for i, c in enumerate(colors))
        dark = " ".join(f"--u-{i}:{c[1]};" for i, c in enumerate(colors))
        t = t.replace("__UCSS_LIGHT__", light).replace("__UCSS_DARK__", dark)
        t = t.replace("__GEO__", dumps(G)).replace("__DATA__", dumps(D))
        t = t.replace('\n<div class="app">', '\n</head>\n<body>\n<div class="app">', 1)
        return HEAD + t + "\n</body>\n</html>\n"
    # 战国式：疆域色写成 --s-<序号>，模板自带文档外壳
    lt = "".join(f"--s-{i}:{D['colors'][k][0]};" for i, k in enumerate(D["states"]))
    dk = "".join(f"--s-{i}:{D['colors'][k][1]};" for i, k in enumerate(D["states"]))
    t = t.replace("__GEO__", dumps(G)).replace("__DATA__", dumps(D))
    return t.replace("/*__SLIGHT__*/", lt).replace("/*__SDARK__*/", dk)


def main():
    slugs = sys.argv[1:] or ERAS
    for slug in slugs:
        b = json.loads((ROOT / "build" / "v1" / f"{slug}.json").read_text(encoding="utf8"))
        html = render(slug, b)
        out = ROOT / "docs" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf8")
        print(f"{slug:20s} {len(html.encode()) / 1e6:5.1f} MB → docs/{slug}/index.html")


if __name__ == "__main__":
    main()
