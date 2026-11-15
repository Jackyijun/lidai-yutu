# -*- coding: utf-8 -*-
"""把各卷旧模板改成新页面模板（规范第十九节第 3 步）。

各卷的地图绘制逻辑原样保留，只换上共用外壳：时间轴、深链接、界面语言键、播放倍速、刘海屏安全区、源码链接。
每处改动都按原文锚定，锚点对不上就报错，不会悄悄漏改。第 5–7 步改为按 v1 数据直接出图的统一模板后，本文件退役。
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


# ---------------- 唐宋系（layered） ----------------

LINK_LAYERED = r"""
  /* ---------------- 深链接（core/web/shell.js） ---------------- */
  const GIDS = __GIDS__, ALIAS = __ALIAS__;
  const tokOf = k => { const [t, i] = parseKey(k); return (GIDS[t] && GIDS[t][i]) || null; };
  const TOK = new Map();
  for (const t in GIDS) GIDS[t].forEach((g, i) => { if (g && !TOK.has(g)) TOK.set(g, keyOf(t, i)); });
  for (const g in ALIAS) if (!TOK.has(g)) TOK.set(g, ALIAS[g]);
  const snapLabel = j => SNAPS[j].m ? `${SNAPS[j].y}.${SNAPS[j].m}` : String(SNAPS[j].y);
  function snapOfLabel(v) {
    const [a, b] = String(v).split("."), y = +a, m = b ? +b : 12;
    if (!isFinite(y) || !isFinite(m)) return si;
    const want = y * 12 + m - 1, j = SNAPS.findIndex(s => s.y * 12 + (s.m || 12) - 1 >= want);
    return j < 0 ? SNAPS.length - 1 : j;
  }
  function viewTok() {
    const f = fitTarget(activeFit);
    if (Math.abs(view.k / f.k - 1) < .02 && Math.hypot(view.cx - f.cx, view.cy - f.cy) * view.k < 4) return null;
    const c = inv(W / 2, H / 2);
    return `${+(view.k / f.k).toFixed(2)}/${c[0].toFixed(2)}/${c[1].toFixed(2)}`;
  }
  const FIT0 = activeFit, CM0 = cmode;
  LINK = LIDAI.link({
    defaults: { v: FIT0, c: CM0 },
    get: () => ({ y: snapLabel(si), sel: selected ? tokOf(selected) : null, v: activeFit, c: cmode, z: stage.dataset.view === "map" ? viewTok() : null, lang: LANG }),
    apply: st => {
      if (st.lang && st.lang !== LANG) setLang(st.lang);
      const cm = st.c || CM0, cb = document.querySelector(`#cmode [data-cm="${cm}"]`);
      if (cb) { cmode = cm; document.querySelectorAll("#cmode button").forEach(x => x.setAttribute("aria-pressed", x === cb ? "true" : "false")); }
      const v = st.v && FITS[st.v] ? st.v : FIT0;
      activeFit = v; document.getElementById("fit").value = v;
      if (stage.dataset.view !== "map") setMode("map");
      const j = st.y != null ? snapOfLabel(st.y) : si;
      if (j !== si) setSnap(j, false);
      selected = null; hovered = null;
      buildTerr(); render(); buildIndex(); markRows();
      return () => {
        fitTo(activeFit, false);
        const k = st.sel && TOK.get(st.sel);
        if (k) select(k, false);
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

TL_LAYERED = r"""  // 时间轴（core/web/shell.js）：上为按真实年代比例的细条，下为等宽刻度：年份 / 短标题 / 年号
  const TL = LIDAI.timeline({
    root: document.getElementById("tl"), n: SNAPS.length,
    pos: j => SNAPS[j].y + (SNAPS[j].m ? (SNAPS[j].m - .5) / 12 : .5),
    label: j => { const s = SNAPS[j]; return __YRLABEL__; },
    short: j => { const s = SNAPS[j]; return (LANG === "en" ? s.she || s.sh : s.sh) || ""; },
    era: j => { const s = SNAPS[j]; return __ERA__; },
    cls: j => { const s = SNAPS[j]; return (__CLS__).trim(); },
    title: j => { const s = SNAPS[j]; return __TITLE__; },
    aria: () => LZ("年代", "Snapshots"),
    pick: j => { stopPlay(); setSnap(j, true); }
  });
  function labelTicks() { TL.relabel(); }
"""

SPEED_JS = r"""
  // 倍速：1× 每节点 __MS1__ 秒，2× 减半
  let speed = 1;
  const speedBtn = document.getElementById("speed");
  const speedTitle = () => { speedBtn.title = LZ(`播放速度：${speed}×（点击切换 ${speed === 1 ? 2 : 1}×）`, `Playback speed ${speed}× (click for ${speed === 1 ? 2 : 1}×)`); speedBtn.setAttribute("aria-label", LZ("播放速度", "Playback speed")); };
  speedBtn.addEventListener("click", () => {
    speed = speed === 1 ? 2 : 1;
    speedBtn.textContent = speed + "×"; speedBtn.setAttribute("aria-pressed", speed === 2 ? "true" : "false");
    speedTitle();
    if (playT) { clearInterval(playT); playT = setInterval(() => { if (si >= SNAPS.length - 1) { stopPlay(); return; } setSnap(si + 1); }, __MS__ / speed); }
  });
  speedTitle();
"""

PCOL_HTML = """    <div class="pcol">
      <button class="play" id="play" aria-label="播放时间轴" title="播放">
        <svg id="playicon" width="14" height="14" viewBox="0 0 14 14"><path d="M3 2 12 7 3 12Z" fill="currentColor"/></svg>
      </button>
      <button class="speed" id="speed" aria-pressed="false" title="播放速度：1×（点击切换 2×）">1×</button>
    </div>
"""


def common_head(t, slug):
    # 旧模板里 claude.ai 预览外壳留下的首行，换成统一文档头（assemble 里加）
    if t.startswith("<!doctype"):
        t = t.split("\n", 1)[1]
    t = re1(t, r'href="https://github\.com/Jackyijun/[a-z-]+"', f'href="{REPO}"', "源码链接")
    i = t.index("\n</style>")
    t = t[:i] + "\n" + shell_css() + t[i:]
    return t


def patch_layered(t, slug):
    t = common_head(t, slug)
    t = sub1(t, '<div class="ticks" id="ticks" role="group" aria-label="年代"></div>', '<div id="tl"></div>', "时间轴容器")
    # 倍速（汉末三国、隋唐原无）
    if 'id="speed"' not in t:
        t = re1(t, r'    <button class="play" id="play"[^\n]*\n[^\n]*\n    </button>\n', PCOL_HTML, "播放按钮")
        m = re.search(r'(    playT = setInterval\(\(\) => \{ if \(si >= SNAPS\.length - 1\) \{ stopPlay\(\); return; \} setSnap\(si \+ 1\); \}, )(\d+)(\);\n  \}\);\n)', t)
        if not m:
            raise PatchError("播放计时：锚点缺失")
        ms = m.group(2)
        t = t[:m.start()] + m.group(1) + ms + " / speed" + m.group(3) + SPEED_JS.replace("__MS1__", str(int(ms) / 1000)).replace("__MS__", ms) + t[m.end():]
    # 共用外壳脚本放在主脚本之前
    t = sub1(t, '  "use strict";\n', '  "use strict";\n  let LINK = null, ANIM = 0;\n  const touch = () => { if (LINK) LINK.write(); };\n', "严格模式")
    t = sub1(t, "\n<script>\n", "\n<script>\n" + shell_js() + "</script>\n<script>\n", "主脚本")
    # 界面语言：链接 > 共用键 lidai-yutu:lang > 本卷旧键
    t = re1(t, r'try \{ const h = location\.hash\.slice\(1\); LANG = h === "en" \|\| h === "zh" \? h : localStorage\.getItem\("([a-z-]+:lang)"\) === "en" \? "en" : "zh"; \} catch \(e\) \{\}',
            lambda m: f'LANG = LIDAI.lang("{m.group(1)}");', "语言初值")
    t = re1(t, r'    try \{ localStorage\.setItem\("[a-z-]+:lang", l\); \} catch \(e\) \{\}\n    try \{ history\.replaceState\([^\n]*\n',
            "    LIDAI.saveLang(l);\n", "语言保存")
    t = re1(t, r'  addEventListener\("hashchange", \(\) => \{ const h = location\.hash\.slice\(1\); if \(h === "en" \|\| h === "zh"\) setLang\(h\); \}\);\n',
            "", "旧 hashchange")
    # 视图：动画可被打断；补 fitTarget 供深链接比对
    t = sub1(t, "    if (!animate || reduce()) { Object.assign(view, target); render(); return; }\n    const from = { ...view }, t0 = performance.now(), dur = 480;\n",
             "    const aid = ++ANIM;\n    if (!animate || reduce()) { Object.assign(view, target); render(); return; }\n    const from = { ...view }, t0 = performance.now(), dur = 480;\n", "setView")
    t = sub1(t, "    (function step(t) {\n      const u = Math.min(1, (t - t0) / dur)",
             "    (function step(t) {\n      if (aid !== ANIM) return;\n      const u = Math.min(1, (t - t0) / dur)", "setView 动画")
    i, j = block_after(t, "  function fitTo(key, animate) {", "fitTo")
    fit = t[i:j]
    m = re.search(r"\n    setView\((.*), animate\);\n  \}\n$", fit)
    if not m:
        raise PatchError("fitTo：末句不是 setView")
    cxy, k = m.group(1).rsplit(", ", 1)
    cx, cy = cxy.rsplit(", ", 1)
    tgt = fit.replace("  function fitTo(key, animate) {", "  function fitTarget(key) {").replace(m.group(0), f"\n    return {{ cx: {cx}, cy: {cy}, k: Math.max(KMIN, Math.min(KMAX, {k})) }};\n  }}\n")
    t = t[:j] + tgt + t[j:]
    t = sub1(t, "  function render() {\n", "  function render() {\n    touch();\n", "render")
    t = sub1(t, "  function markRows() {\n", "  function markRows() {\n    touch();\n", "markRows")
    # 时间轴
    i = t.index('  const ticks = document.getElementById("ticks");\n')
    i2, j2 = block_after(t, "  SNAPS.forEach((s, j) => {\n    const b = document.createElement(\"button\");", "刻度生成")
    gen = t[i2:j2]
    cls = re.search(r'b\.className = "tick" \+ (.*?); b\.dataset\.j', gen).group(1)
    yr = re.search(r'<span class="yr">(.*?)</span>', gen).group(1)
    yrexpr = "`" + yr + "`"
    i3, j3 = block_after(t, "  function labelTicks() {", "labelTicks")
    lab = t[i3:j3]
    era = re.search(r'b\.querySelector\("\.tt"\)\.textContent = (.*?);', lab).group(1)
    title = re.search(r"b\.title = (.*?);\s*b\.querySelector", lab, re.S).group(1)
    if not (i < i2 < j2 <= i3):
        raise PatchError("时间轴：块次序不对")
    tl = TL_LAYERED.replace("__YRLABEL__", yrexpr).replace("__ERA__", era).replace("__CLS__", cls).replace("__TITLE__", title)
    t = t[:i] + tl + t[j3:]
    t = sub1(t, '    ticks.querySelectorAll(".tick").forEach(b => b.setAttribute("aria-pressed", +b.dataset.j === j ? "true" : "false"));\n', "    TL.set(j);\n", "setSnap 刻度")
    t = re1(t, r'    const tk = ticks\.querySelector\(`\[data-j="\$\{j\}"\]`\);\n    if \(tk && ticks\.scrollWidth > ticks\.clientWidth\) ticks\.scrollTo\([^\n]*\n', "", "setSnap 滚动")
    if "ticks." in t.split("</script>\n<script>\n", 1)[1]:
        raise PatchError("时间轴：仍有 ticks 引用")
    # 深链接：启动最后
    t = sub1(t, "  resize();\n})();\n", "  resize();\n" + LINK_LAYERED + "})();\n", "启动")
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
    const f = fitTarget(activeFit);
    if (Math.abs(view.k / f.k - 1) < .02 && Math.hypot(view.cx - f.cx, view.cy - f.cy) * view.k < 4) return null;
    const c = inv(W / 2, H / 2);
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
    t = sub1(t, "    if (!animate || reduce()) { Object.assign(view, target); render(); return; }\n    const from = { ...view }, t0 = performance.now(), dur = 480;\n",
             "    const aid = ++ANIM;\n    if (!animate || reduce()) { Object.assign(view, target); render(); return; }\n    const from = { ...view }, t0 = performance.now(), dur = 480;\n", "setView")
    t = sub1(t, "    (function step(t) {\n      const u = Math.min(1, (t - t0) / dur)",
             "    (function step(t) {\n      if (aid !== ANIM) return;\n      const u = Math.min(1, (t - t0) / dur)", "setView 动画")
    i, j = block_after(t, "  function fitTo(key, animate) {", "fitTo")
    fit = t[i:j]
    m = re.search(r"\n    setView\((.*), animate\);\n  \}\n$", fit)
    cxy, k = m.group(1).rsplit(", ", 1)
    cx, cy = cxy.rsplit(", ", 1)
    tgt = fit.replace("  function fitTo(key, animate) {", "  function fitTarget(key) {").replace(m.group(0), f"\n    return {{ cx: {cx}, cy: {cy}, k: Math.max(0.6, Math.min(60, {k})) }};\n  }}\n")
    t = t[:j] + tgt + t[j:]
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
