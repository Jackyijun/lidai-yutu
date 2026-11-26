# -*- coding: utf-8 -*-
"""新版页面：v1 数据包 → docs/<短名>/index.html（规范第十九节第 3、4 步）。

  python core/web/assemble.py              各卷全部
  python core/web/assemble.py songyuan     只做这几卷

数据来源是 core/v1/build.py 生成的 build/v1/<短名>.json（已附全局 ID）。九卷都套统一模板 core/web/template.html，
各卷不同的文字与开关取 era.toml 的 [web]。春秋、战国两卷的 v1 由 legacy.from_v1 转回的是战国式写法，先经 simple.py 转成
统一模板读的唐宋系写法。各卷的灭国表 eras/<短名>/content/falls.tsv 由 falls.py 读入。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core" / "v1"))
sys.path.insert(0, str(ROOT / "core" / "geo"))
import legacy
from registry import ERAS
import geo
import simple
import falls

HERE = Path(__file__).resolve().parent

HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>[hidden]{display:none!important}</style>
"""


def dumps(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def web_config(slug):
    """era.toml [web]：各卷页面的文字与开关（见 core/web/README.md）"""
    from registry import load_toml
    w = load_toml(ROOT / "eras" / slug / "era.toml").get("web")
    assert w, f"eras/{slug}/era.toml 缺 [web] 一节"
    return w


def shell_css():
    """共用样式：时间轴、播放倍速、刘海屏安全区"""
    return (HERE / "shell.css").read_text(encoding="utf8")


def shell_js():
    """共用脚本：时间轴、深链接、界面语言"""
    return (HERE / "shell.js").read_text(encoding="utf8")


def geo_css(cfg):
    """第 4 步：地形晕渲浓淡（core/geo/config.toml）"""
    r = cfg["relief"]
    return (f"  /* 第 4 步：地形晕渲浓淡（core/geo/config.toml） */\n"
            f"  :root {{ --hill-op:{r['opacity_light']:g}; }}\n"
            f"  @media (prefers-color-scheme: dark) {{ :root:not([data-theme=\"light\"]) {{ --hill-op:{r['opacity_dark']:g}; }} }}\n"
            f"  :root[data-theme=\"dark\"] {{ --hill-op:{r['opacity_dark']:g}; }}\n"
            f"  .hill {{ mix-blend-mode:hard-light; opacity:var(--hill-op); pointer-events:none; }}\n")


ROUTE_KEY = ('<span><svg width="16" height="12"><path d="M1 9 L8 5 L15 3" stroke="var(--c-route)" stroke-width="2" fill="none" stroke-linecap="round"/></svg>'
             '<span id="key3">行军路线</span></span>')


def web_template(slug):
    """统一模板 core/web/template.html，按 era.toml [web] 填各卷的文字与开关"""
    from html import escape
    t = (HERE / "template.html").read_text(encoding="utf8")
    cfg = geo.load()
    w = web_config(slug)
    p = cfg["projection"]
    t = t.replace("  /*__SHELL_CSS__*/\n", shell_css()).replace("__SHELL_JS__\n", shell_js()).replace("  /*__GEO_CSS__*/\n", geo_css(cfg))
    t = (t.replace("__P1__", str(p["parallels"][0])).replace("__P2__", str(p["parallels"][1])).replace("__P0__", str(p["center"][1]))
         .replace("__L0__", str(p["center"][0])).replace("__SEAM__", str(p["seam"])))
    fit0 = w.get("fit0") or w["fits"][0][0]
    opts = "".join(f'        <option value="{v}"{" selected" if v == fit0 else ""}>{escape(zh)}</option>\n' for v, zh, en, box in w["fits"])
    cm = w["cm"]
    btn = lambda key, pressed, title, label: f'        <button data-cm="{key}" aria-pressed="{"true" if pressed else "false"}" title="{escape(title)}">{escape(label)}</button>\n'
    cms = btn("zhen", w["cmode"] == "zhen", cm["zhen_title"][0], cm["zhen"][0]) + btn("pol", w["cmode"] == "pol", cm["pol_title"][0], cm.get("pol", ["政权"])[0])
    if w.get("cmodes") is False:                        # 只有一种着色（战国）：不出按钮
        cms = ""
    for k, v in (("doc_title", escape(w["doc_title"][0])), ("h1", escape(w["h1"][0])), ("sub", escape(w["sub"][0])), ("map_label", escape(w["map_label"][0])),
                 ("key2", escape(w["key2"][0])), ("foot", escape(w["foot"][0], quote=False)), ("inset_h", str(w["inset_h"])),
                 ("key_route", ROUTE_KEY if w.get("key_route") else ""), ("fit_options", opts), ("cmode_buttons", cms)):
        assert "{{" + k + "}}" in t, k
        t = t.replace("{{" + k + "}}", v)
    assert "{{" not in t, t[t.index("{{") - 40:t.index("{{") + 60]
    if w.get("css"):
        i = t.index("\n</style>")
        t = t[:i] + "\n  /* 本卷专属（era.toml [web] css） */\n" + "".join("  " + l + "\n" for l in w["css"].strip().splitlines()) + t[i + 1:]
    js = {k: v for k, v in w.items() if k != "css"}
    return t.replace("__WEB__", dumps(js))


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


def render(slug, b):
    if b["_legacy"]["fam"] == "A":                  # 春秋、战国：战国式写法先转成唐宋系写法（core/web/simple.py）
        G, D, colors, gids, alias = simple.layered(b)
    else:
        G, D, colors = legacy.from_v1(b)
        gids, alias = tokens(b)
    for sn in G["snaps"]:
        sn.pop("zn", None)                          # 汉末：各点的州块只给统一引擎分块用，页面不用
    F = falls.load(slug, D["units"], web_config(slug).get("time", "year"))   # 灭国表 content/falls.tsv（core/web/falls.py）
    if F:
        D["falls"] = F
    t = web_template(slug)
    shorts(b, G)
    geo.apply(slug, G)
    light = " ".join(f"--u-{i}:{c[0]};" for i, c in enumerate(colors))     # 疆域色写成 --u-<序号>
    dark = " ".join(f"--u-{i}:{c[1]};" for i, c in enumerate(colors))
    t = t.replace("__GIDS__", dumps(gids)).replace("__ALIAS__", dumps(alias))
    t = t.replace("__UCSS_LIGHT__", light).replace("__UCSS_DARK__", dark)
    t = t.replace("__GEO__", dumps(G)).replace("__DATA__", dumps(D))
    t = t.replace('\n<div class="app">', '\n</head>\n<body>\n<div class="app">', 1)
    return HEAD + t + "\n</body>\n</html>\n"


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
