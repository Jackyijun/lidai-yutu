# -*- coding: utf-8 -*-
"""把春秋、战国两卷的旧模板改成新页面模板（规范第十九节第 3 步）。

秦汉至民国七卷已合成统一模板 core/web/template.html（2026-11-20），不再经过这里。春秋、战国的地图绘制逻辑
原样保留，只换上共用外壳：时间轴、深链接、界面语言键、播放倍速、刘海屏安全区、源码链接，以及第 4 步的统一投影、
全球底图与地形晕渲。每处改动都按原文锚定，锚点对不上就报错，不会悄悄漏改。两卷改用统一模板后，本文件退役。
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = "https://github.com/Jackyijun/lidai-yutu"


class PatchError(Exception):
    pass


def sub1(t, old, new, what, count=1):
    """原文替换，要求恰好出现 count 次"""
    n = t.count(old)
    if n != count:
        raise PatchError(f"{what}：锚点出现 {n} 次（应为 {count}）\n{old[:160]}")
    return t.replace(old, new)


def re1(t, pat, repl, what, flags=0):
    t2, n = re.subn(pat, repl, t, count=0, flags=flags)
    if n != 1:
        raise PatchError(f"{what}：正则匹配 {n} 次（应为 1）\n{pat[:160]}")
    return t2


def block_after(t, start, what):
    """从 start 起到与其第一个 { 配对的 } 为止（含其后的换行）"""
    i = t.find(start)
    if i < 0 or t.find(start, i + 1) >= 0:
        raise PatchError(f"{what}：起始锚点缺失或重复")
    j = t.index("{", i)
    depth = 0
    for k in range(j, len(t)):
        if t[k] == "{":
            depth += 1
        elif t[k] == "}":
            depth -= 1
            if depth == 0:
                end = k + 1
                if t[end:end + 2] == ");":
                    end += 2
                if t[end:end + 1] == ";":
                    end += 1
                if t[end:end + 1] == "\n":
                    end += 1
                return i, end
    raise PatchError(f"{what}：括号不配对")


def shell_css():
    return (HERE / "shell.css").read_text(encoding="utf8")


def shell_js():
    return (HERE / "shell.js").read_text(encoding="utf8")


def common_head(t, slug):
    # 旧模板里 claude.ai 预览外壳留下的首行，换成统一文档头（assemble 里加）
    if t.startswith("<!doctype"):
        t = t.split("\n", 1)[1]
    t = re1(t, r'href="https://github\.com/Jackyijun/[a-z-]+"', f'href="{REPO}"', "源码链接")
    i = t.index("\n</style>")
    t = t[:i] + "\n" + shell_css() + t[i:]
    return t


# ---------------- 战国式（simple） ----------------

LINK_SIMPLE = r"""
  /* ---------------- 深链接（core/web/shell.js） ---------------- */
  const GIDS = __GIDS__, ALIAS = __ALIAS__;
  const tokOf = i => GIDS.i[i] || null;
  const TOK = new Map();
  GIDS.i.forEach((g, i) => { if (g && !TOK.has(g)) TOK.set(g, i); });
  for (const g in ALIAS) if (!TOK.has(g)) TOK.set(g, ALIAS[g]);
  function snapOfLabel(v) {
    const y = parseInt(v, 10);
    if (!isFinite(y)) return si;
    const j = SNAPS.findIndex(s => s.y >= y);
    return j < 0 ? SNAPS.length - 1 : j;
  }
  function viewTok() {
    if (atFit()) return null;
    const f = fitTarget(activeFit), c = inv(W / 2, H / 2);
    return `${+(view.k / f.k).toFixed(2)}/${c[0].toFixed(2)}/${c[1].toFixed(2)}`;
  }
  const FIT0 = activeFit__C0__;
  LINK = LIDAI.link({
    defaults: { v: FIT0__CDEF__ },
    get: () => ({ y: String(SNAPS[si].y), sel: selected != null ? tokOf(selected) : null, v: activeFit__CGET__, z: stage.dataset.view === "map" ? viewTok() : null, lang: LANG }),
    apply: st => {
      if (st.lang && st.lang !== LANG) setLang(st.lang);
      const v = st.v && FITS[st.v] ? st.v : FIT0, vs = document.getElementById("views");
      activeFit = v;
      if (vs.tagName === "SELECT") vs.value = v; else vs.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x.dataset.fit === v ? "true" : "false"));__CAPPLY__
      if (stage.dataset.view !== "map") setMode("map");
      const j = st.y != null ? snapOfLabel(st.y) : si;
      if (j !== si) setSnap(j, false);
      selected = null; hovered = null;
      buildStates(); render(); buildIndex(); markRows();
      return () => {
        fitTo(activeFit, false);
        const i = st.sel != null ? TOK.get(st.sel) : undefined;
        if (i != null) select(i, false);
        if (st.z) {
          const [z, lo, la] = st.z.split("/").map(Number);
          if ([z, lo, la].every(isFinite) && z > 0) { const f = fitTarget(activeFit), p = proj(lo, la); setView(p[0], p[1], f.k * z, false); }
        }
        buildIndex();
      };
    }
  });
  LINK.start();
"""

RESIZE_OLD = """  function resize() {
    const box = document.getElementById("mapwrap").getBoundingClientRect();
    W = Math.max(300, box.width); H = Math.max(240, box.height);
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    fitTo(activeFit, false);
  }
"""


def resize_js():
    # 地图区尺寸变了怎么办（atFit、resize 两个函数）：与七卷合用的 template.html 逐字相同，从那里取
    t = (HERE / "template.html").read_text(encoding="utf8")
    a = t.index("  // 视图是不是当前视野的整幅")
    b = t.index("\n  }\n", t.index("  function resize() {", a)) + len("\n  }\n")
    return t[a:b]


TL_SIMPLE = r"""  // 时间轴（core/web/shell.js）：上为按真实年代比例的细条，下为等宽刻度：年份 / 短标题
  const TL = LIDAI.timeline({
    root: document.getElementById("tl"), n: SNAPS.length,
    pos: j => SNAPS[j].y + .5,
    label: j => yr(SNAPS[j].y),
    short: j => SS(SNAPS[j]),
    era: () => "",
    title: j => `${yr(SNAPS[j].y)} ${ST(SNAPS[j])}`,
    axis: y => yr(y),
    aria: () => t("years"),
    pick: j => { stopPlay(); setSnap(j, true); }
  });
  TL.relabel();
"""


def patch_simple(t, slug):
    t = sub1(t, '<meta name="viewport" content="width=device-width,initial-scale=1">', '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">', "viewport")
    t = common_head(t, slug)
    # 疆域不透明度与唐宋系一致
    t = sub1(t, "--s-op:.52; --s-op-hi:.64;", "--s-op:.5; --s-op-hi:.66;", "浅色不透明度")
    t = sub1(t, "--s-op:.34; --s-op-hi:.46;", "--s-op:.34; --s-op-hi:.5;", "深色不透明度", count=2)
    i = t.index("\n</style>")
    t = t[:i] + "\n  .masthead { padding-left:max(20px, env(safe-area-inset-left, 0px)); padding-right:max(20px, env(safe-area-inset-right, 0px)); }" + t[i:]
    t = sub1(t, '<div class="axiswrap" id="axiswrap"><div class="axis" id="axis" role="group" aria-label="年代" data-ta="years"></div></div>', '<div id="tl"></div>', "时间轴容器")
    t = sub1(t, '  "use strict";\n', '  "use strict";\n  let LINK = null, ANIM = 0;\n  const touch = () => { if (LINK) LINK.write(); };\n', "严格模式")
    t = sub1(t, "\n<script>\n", "\n<script>\n" + shell_js() + "</script>\n<script>\n", "主脚本")
    t = re1(t, r'  try \{ LANG = location\.hash === "#en" \? "en" : location\.hash === "#zh" \? "zh" : \(localStorage\.getItem\("([a-z]+-lang)"\) \|\| "zh"\); \} catch \(e\) \{[^\n]*\}\n',
            lambda m: f'  LANG = LIDAI.lang("{m.group(1)}");\n', "语言初值")
    t = re1(t, r'    try \{ localStorage\.setItem\("[a-z]+-lang", l\); \} catch \(e\) \{\}\n    try \{ history\.replaceState\([^\n]*\n',
            "    LIDAI.saveLang(l);\n", "语言保存")
    t = sub1(t, "    buildAxis(); setSnap(si, false);\n", "    TL.relabel(); setSnap(si, false);\n", "切换语言重排时间轴")
    # 视图
    t = sub1(t, "  function setView(cx, cy, k, animate) {\n",
             "  let FLIGHT = null;     // 正在飞的视图动画 { target, fit, aid }：fit 为飞回当前视野的整幅（见 resize）\n  function setView(cx, cy, k, animate, fit) {\n", "setView 参数")
    t = sub1(t, "    if (!animate || reduce()) { Object.assign(view, target); render(); return; }\n    const from = { ...view }, t0 = performance.now(), dur = 480;\n",
             "    const aid = ++ANIM;\n    FLIGHT = null;\n    if (!animate || reduce()) { Object.assign(view, target); render(); return; }\n"
             "    const from = { ...view }, t0 = performance.now(), dur = 480;\n    FLIGHT = { target, fit: !!fit, aid };\n", "setView")
    t = sub1(t, "    (function step(t) {\n      const u = Math.min(1, (t - t0) / dur)",
             "    (function step(t) {\n      if (aid !== ANIM) return;\n      const u = Math.min(1, (t - t0) / dur)", "setView 动画")
    t = sub1(t, "      render(); if (u < 1) requestAnimationFrame(step);\n    })(t0);\n",
             "      render(); if (u < 1) requestAnimationFrame(step); else if (FLIGHT && FLIGHT.aid === aid) FLIGHT = null;\n    })(t0);\n", "setView 收尾")
    i, j = block_after(t, "  function fitTo(key, animate) {", "fitTo")
    fit = t[i:j]
    m = re.search(r"\n    setView\((.*), animate\);\n  \}\n$", fit)
    cxy, k = m.group(1).rsplit(", ", 1)
    cx, cy = cxy.rsplit(", ", 1)
    tgt = fit.replace("  function fitTo(key, animate) {", "  function fitTarget(key, leg = !legBody.hidden) {").replace(m.group(0), f"\n    return {{ cx: {cx}, cy: {cy}, k: Math.max(0.6, Math.min(60, {k})) }};\n  }}\n")
    if tgt.count("(!legBody.hidden && W > ") != 1:
        raise PatchError("fitTarget：图例让位的写法变了")
    tgt = tgt.replace("(!legBody.hidden && W > ", "(leg && W > ")
    t = t[:i] + fit.replace(m.group(0), m.group(0).replace(", animate);", ", animate, true);")) + tgt + t[j:]
    # 地图区尺寸变了：整幅的重新收进，放大过的保持倍数与中心，飞行中的照飞（与 core/web/template.html 的 resize 相同）
    t = sub1(t, RESIZE_OLD, resize_js(), "resize")
    t = sub1(t, '    if (m === "map") requestAnimationFrame(() => { const keep = { ...view }; resize(); if (keep.k !== 1) { Object.assign(view, keep); render(); } });\n',
             '    if (m === "map") requestAnimationFrame(resize);\n', "切回地图")
    t = sub1(t, "  function render() {\n", "  function render() {\n    touch();\n", "render")
    t = sub1(t, "  function markRows() { ", "  function markRows() { touch(); ", "markRows")
    # 时间轴：换掉旧轴（保留 ST/SD_/SS）
    a = t.index('  const axis = document.getElementById("axis"), axiswrap = document.getElementById("axiswrap");\n')
    b = t.index("  const ST = sn => ")
    t = t[:a] + t[b:]
    i, j = block_after(t, "  function buildAxis() {", "buildAxis")
    t = t[:i] + t[j:]
    t = sub1(t, "  buildAxis();\n", TL_SIMPLE, "buildAxis 调用")
    i, j = block_after(t, "  function placeLbl(node, x) {", "placeLbl")
    t = t[:i] + t[j:]
    t = re1(t, r'    axis\.querySelectorAll\("\.sd"\)\.forEach\([^\n]*\n    document\.getElementById\("axfill"\)\.style\.width = pct\(s\.y\);\n    const btn = axis\.querySelector\([^\n]*\n    requestAnimationFrame\(\(\) => \{\n[^\n]*\n    \}\);\n',
            "    TL.set(j);\n", "setSnap 刻度")
    main = t.split("</script>\n<script>\n", 1)[1]
    for w in ("axis.", "axiswrap", "pct(", "buildAxis", "TY0"):
        if w in main:
            raise PatchError(f"时间轴：仍有 {w} 引用")
    link = LINK_SIMPLE
    if "let colorBy" in t:      # 春秋：诸侯 / 共主两种着色
        link = (link.replace("__C0__", ", CB0 = colorBy").replace("__CDEF__", ", c: CB0").replace("__CGET__", ", c: colorBy")
                .replace("__CAPPLY__", """
      const cb = st.c || CB0, cbb = document.querySelector(`#colorby [data-cb="${cb}"]`);
      if (cbb) { colorBy = cb; document.querySelectorAll("#colorby button").forEach(x => x.setAttribute("aria-pressed", x === cbb ? "true" : "false")); buildLegendStates(); }"""))
    else:
        link = link.replace("__C0__", "").replace("__CDEF__", "").replace("__CGET__", "").replace("__CAPPLY__", "")
    t = sub1(t, "  resize();\n})();\n", "  resize();\n" + link + "})();\n", "启动")
    return t


# ---------------- 第 4 步：统一投影、全球底图、地形晕渲（各卷共用，参数在 core/geo/config.toml） ----------------

GEO_LAND = r"""  // 第 4 步（core/geo）：全球底图垫在本卷陆地下面（伸进本卷范围一窄条，拼接处不露缝）。海岸线从两份多边形描出：
  // 本卷陆地跳过落在范围边上的切边，全球陆地跳过本卷范围以内的部分，两者都跳过接缝上的切边
  const WB = GEO.world ? GEO.world.box : null, near = (u, v) => Math.abs(u - v) < .011;
  const onSeam = (a, b) => (near(a[0], __SEAM__) && near(b[0], __SEAM__)) || (near(a[0], __SEAM__ + 360) && near(b[0], __SEAM__ + 360));
  const edge = p => (near(p[0], WB[0]) ? 1 : 0) | (near(p[0], WB[1]) ? 2 : 0) | (near(p[1], WB[2]) ? 4 : 0) | (near(p[1], WB[3]) ? 8 : 0);
  const inBox = p => p[0] > WB[0] - .011 && p[0] < WB[1] + .011 && p[1] > WB[2] - .011 && p[1] < WB[3] + .011;
  function coastD(rings, world) {
    let d = "";
    for (const r of rings) {
      const ll = []; let x = 0, y = 0;
      for (let i = 0; i < r.length; i += 2) { x += r[i]; y += r[i + 1]; ll.push([x / 100, y / 100]); }
      ll.push(ll[0]);
      let pen = false;
      for (let i = 1; i < ll.length; i++) {
        const a = ll[i - 1], b = ll[i];
        if (WB && (onSeam(a, b) || (world ? inBox(a) && inBox(b) : edge(a) & edge(b)))) { pen = false; continue; }
        const pb = proj(b[0], b[1]);
        if (!pen) { const pa = proj(a[0], a[1]); d += "M" + pa[0].toFixed(1) + " " + pa[1].toFixed(1); pen = true; }
        d += "L" + pb[0].toFixed(1) + " " + pb[1].toFixed(1);
      }
    }
    return d;
  }
  const worldD = GEO.world ? GEO.world.fill.map(p => p.map(r => P(decode(r), true)).join(" ")).join(" ") : "";
  // 两份陆地各描一道陆地色的细边，盖住拼接处抗锯齿留下的细缝（真正的海岸线另有描边压在上面）
  if (worldD) lLand.append(el("path", { d: worldD, fill: "var(--land)", stroke: "var(--land)", "stroke-width": 1, "vector-effect": "non-scaling-stroke", "fill-rule": "evenodd" }));
  lLand.append(el("path", { d: landD, fill: "var(--land)", stroke: "var(--land)", "stroke-width": 1, "vector-effect": "non-scaling-stroke", "fill-rule": "evenodd" }));
  if (GEO.world) for (const r of GEO.world.lakes) lLand.append(el("path", { d: P(decode(r), true), fill: "var(--water-fill)", stroke: "var(--water)", "stroke-width": .7, "vector-effect": "non-scaling-stroke" }));
  lLand.append(el("path", { d: coastD(GEO.land.flat(), false) + (GEO.world ? coastD(GEO.world.fill.flat(), true) : ""), fill: "none", stroke: "var(--coast)", "stroke-width": .8, "vector-effect": "non-scaling-stroke", "stroke-linejoin": "round" }));
  // 地形晕渲：粗档在下、细档在上，先普通叠成一张，再整体 hard-light（浓淡见 --hill-op），只画在陆地上
  if (GEO.hill) {
    const hc = el("clipPath", { id: "hillclip" });
    hc.append(el("path", { d: landD, "clip-rule": "evenodd" }));
    if (worldD) hc.append(el("path", { d: worldD, "clip-rule": "evenodd" }));
    defs.append(hc);
    const g = el("g", { class: "hill", "clip-path": "url(#hillclip)" });
    for (const H of GEO.hill) g.append(el("image", { href: H.src, x: H.x, y: H.y, width: H.w, height: H.h, preserveAspectRatio: "none" }));
    lHill.append(g);
  }
"""

SYM_RELIEF = """    relief: '<path d="M1 12 5.5 4 8.5 8.5 10.5 6 13 12Z" fill="var(--ink-3)" opacity=".55"/><path d="M5.5 4 4 12H1Z" fill="var(--ink)" opacity=".5"/>',\n"""


def geo_css(cfg):
    r = cfg["relief"]
    return (f"  /* 第 4 步：地形晕渲浓淡（core/geo/config.toml） */\n"
            f"  :root {{ --hill-op:{r['opacity_light']:g}; }}\n"
            f"  @media (prefers-color-scheme: dark) {{ :root:not([data-theme=\"light\"]) {{ --hill-op:{r['opacity_dark']:g}; }} }}\n"
            f"  :root[data-theme=\"dark\"] {{ --hill-op:{r['opacity_dark']:g}; }}\n"
            f"  .hill {{ mix-blend-mode:hard-light; opacity:var(--hill-op); pointer-events:none; }}\n")


def patch_geo(t, cfg, simple=True):
    """第 4 步：统一投影、全球底图、地形晕渲（统一模板里已写好，这里只给战国式模板用）"""
    assert simple, "唐宋系已改用 core/web/template.html"
    p = cfg["projection"]
    # 1. 统一投影（民国卷的前端读 GEO.proj，由 core/geo/geo.py 改数据）
    if "GEO.proj.map(v => v * RAD)" not in t:
        t = re1(t, r"const p1 = \d+ \* RAD, p2 = \d+ \* RAD, p0 = \d+ \* RAD, l0 = \d+ \* RAD;",
                f"const p1 = {p['parallels'][0]} * RAD, p2 = {p['parallels'][1]} * RAD, p0 = {p['center'][1]} * RAD, l0 = {p['center'][0]} * RAD;",
                "投影参数")
    # 2. 接缝
    t = sub1(t, "  function proj(lon, lat) {\n", f"  function proj(lon, lat) {{\n    if (lon < {p['seam']}) lon += 360;\n", "接缝")
    # 3. 晕渲图层：疆域之上、界线与注记之下
    if simple:
        t = sub1(t, 'lState = layer("state"), ', 'lState = layer("state"), lHill = layer("hill"), ', "晕渲图层")
    else:
        t = sub1(t, 'lHatch = layer("hatch"), ', 'lHatch = layer("hatch"), lHill = layer("hill"), ', "晕渲图层")
    # 4. 陆地、全球底图、海岸线、晕渲
    old = ('  lLand.append(el("path", { d: landD, fill: "var(--land)", stroke: "none", "fill-rule": "evenodd" }));\n'
           '  lLand.append(el("path", { d: landD, fill: "none", stroke: "var(--coast)", "stroke-width": .8, "vector-effect": "non-scaling-stroke", "stroke-linejoin": "round" }));\n')
    t = sub1(t, old, GEO_LAND.replace("__SEAM__", str(p["seam"])), "陆地绘制")
    # 5. 图例开关「地形」
    if simple:
        t = sub1(t, '{ id:"territory", zh:"疆域", en:"Territories" }, ', '{ id:"territory", zh:"疆域", en:"Territories" }, { id:"relief", zh:"地形", en:"Relief" }, ', "图例项")
        t = sub1(t, 'const n = L.id === "territory" || L.id === "prov" ? ""', 'const n = L.id === "territory" || L.id === "prov" || L.id === "relief" ? ""', "图例计数")
        t = sub1(t, 'if (!["territory", "prov"].includes(LAYERS[j].id) && !ITEMS.some', 'if (!["territory", "relief", "prov"].includes(LAYERS[j].id) && !ITEMS.some', "图例筛选")
    else:
        t = re1(t, r'(\{ id: "terr", name: "疆域", en: "Territor(?:y|ies)" \}, )', r'\1{ id: "relief", name: "地形", en: "Relief" }, ', "图例项")
    t = sub1(t, "    range: '", SYM_RELIEF + "    range: '", "图例图标")
    t = sub1(t, '    b.setAttribute("aria-pressed", layerOn[id] ? "true" : "false");\n',
             '    b.setAttribute("aria-pressed", layerOn[id] ? "true" : "false");\n'
             '    if (id === "relief") lHill.setAttribute("display", layerOn.relief ? "inline" : "none");\n', "图例开关")
    # 6. 浓淡
    i = t.index("\n</style>")
    return t[:i] + "\n" + geo_css(cfg) + t[i:]
