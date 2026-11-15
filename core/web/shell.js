/* 历代舆图 · 各卷页面共用的外壳（规范第十九节第 3 步）
   时间轴（真实年代比例的细条 + 等宽刻度）、深链接、界面语言。各卷模板在自己的脚本里调用。 */
(function () {
  "use strict";
  const LANG_KEY = "lidai-yutu:lang";
  const reduce = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 深链接：#y=…&sel=…&v=…&c=…&z=…&lang=en；旧链接的 #en / #zh 照常认 ---------- */
  const KEYS = ["y", "sel", "v", "c", "z", "lang"];
  function parse(h) {
    h = (h == null ? location.hash : h).replace(/^#/, "");
    if (h === "en" || h === "zh") return { lang: h };
    const st = {};
    for (const part of h.split("&")) {
      const i = part.indexOf("=");
      if (i < 1) continue;
      const k = part.slice(0, i);
      let v = part.slice(i + 1);
      try { v = decodeURIComponent(v); } catch (e) {}
      if (KEYS.includes(k) && v !== "") st[k] = v;
    }
    if (st.lang !== "en" && st.lang !== "zh") delete st.lang;
    return st;
  }
  // 只转义会破坏链接结构的字符，汉字原样保留，链接可读
  const enc = v => String(v).replace(/[%&=#\s?+]/g, c => encodeURIComponent(c));
  function encode(st, def) {
    const out = [];
    for (const k of KEYS) {
      const v = st[k];
      if (v == null || v === "") continue;
      if (k === "lang" && v === "zh") continue;
      if (def && def[k] != null && def[k] === v) continue;
      out.push(k + "=" + enc(v));
    }
    return out.join("&");
  }

  function lang(oldKey) {
    const st = parse();
    if (st.lang) return st.lang;
    try {
      const v = localStorage.getItem(LANG_KEY) || (oldKey && localStorage.getItem(oldKey));
      if (v === "en" || v === "zh") return v;
    } catch (e) {}
    return "zh";
  }
  function saveLang(l) { try { localStorage.setItem(LANG_KEY, l); } catch (e) {} }

  // get() 给出当前状态；apply(st) 把链接里的状态套到页面上；defaults 里与默认值相同的项不写进链接
  function link(o) {
    let started = false, hadHash = false, initial = "", last = null, timer = 0;
    const flush = () => {
      timer = 0;
      if (!started) return;
      const s = encode(o.get(), o.defaults);
      if (s === last) return;
      if (!hadHash && s === initial) return;       // 打开后没动过：地址栏保持干净
      last = s;
      try { history.replaceState(null, "", location.pathname + location.search + (s ? "#" + s : "")); } catch (e) {}
    };
    const api = {
      write() { if (started && !timer) timer = setTimeout(flush, 250); },
      start() {
        const st = parse();
        hadHash = Object.keys(st).some(k => k !== "lang");
        // apply 只设时间、着色、视野；它返回的 post（选中、缩放）等版面随之变动、尺寸观察回调把地图按视野重置之后再做
        const after = f => requestAnimationFrame(() => requestAnimationFrame(f));
        after(() => {
          const post = hadHash ? o.apply(st) : null;
          after(() => {
            if (post) post();
            initial = encode(o.get(), o.defaults);
            last = hadHash ? initial : null;
            started = true;
          });
        });
        addEventListener("hashchange", () => {
          const h = location.hash.replace(/^#/, "");
          if (h === last) return;
          const post = o.apply(parse());
          hadHash = true; last = null;
          after(() => { if (post) post(); api.write(); });
        });
      },
      parse
    };
    return api;
  }

  /* ---------- 时间轴：上为按真实年代比例的细条，下为等宽刻度（年份 / 短标题 / 年号） ---------- */
  // o: root, n, pos(j)→年（可带小数）, label(j), short(j), era(j), cls(j), title(j), axis(y)→刻度文字, aria()→组名, pick(j)
  function timeline(o) {
    const root = o.root;
    root.classList.add("tl");
    root.innerHTML = '<div class="tl-strip" aria-hidden="true"><div class="tl-ln"></div><div class="tl-win"></div></div><div class="tl-ticks" role="group"></div>';
    const strip = root.querySelector(".tl-strip"), win = root.querySelector(".tl-win"), ticks = root.querySelector(".tl-ticks");
    const P = [];
    for (let j = 0; j < o.n; j++) P.push(o.pos(j));
    const Y0 = P[0], Y1 = P[o.n - 1], span = Math.max(Y1 - Y0, 1e-6);
    const pct = y => ((y - Y0) / span * 100).toFixed(3) + "%";
    const marks = [];
    for (let j = 0; j < o.n; j++) {
      const m = document.createElement("i");
      m.className = "tl-m"; m.style.left = pct(P[j]);
      strip.append(m); marks.push(m);
    }
    const btns = [];
    for (let j = 0; j < o.n; j++) {
      const b = document.createElement("button");
      b.className = "tl-tk" + (o.cls ? " " + (o.cls(j) || "") : "").trimEnd();
      b.dataset.j = j; b.setAttribute("aria-pressed", "false");
      b.innerHTML = '<span class="yr"></span><span class="dot"></span><span class="sh"></span><span class="era"></span>';
      b.addEventListener("click", () => o.pick(j));
      ticks.append(b); btns.push(b);
    }
    let cur = -1, labs = [];
    function axisLabels() {
      for (const l of labs) l.remove();
      labs = [];
      const w = strip.clientWidth || 800, want = Math.max(2, Math.min(9, Math.floor(w / 90)));
      const steps = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000];
      let st = steps[steps.length - 1];
      for (const s of steps) if (span / s <= want) { st = s; break; }
      for (let y = Math.ceil(Y0 / st) * st; y <= Y1 + 1e-9; y += st) {
        const x = (y - Y0) / span;
        if (x < .02 || x > .98) continue;
        const d = document.createElement("span");
        d.className = "tl-lb"; d.style.left = pct(y); d.textContent = o.axis ? o.axis(y) : String(y);
        strip.append(d); labs.push(d);
      }
    }
    function relabel() {
      ticks.setAttribute("aria-label", o.aria ? o.aria() : "");
      btns.forEach((b, j) => {
        b.querySelector(".yr").textContent = o.label(j);
        b.querySelector(".sh").textContent = o.short ? o.short(j) || "" : "";
        b.querySelector(".era").textContent = o.era ? o.era(j) || "" : "";
        if (o.title) b.title = o.title(j);
      });
      axisLabels(); winUpdate();
    }
    // 细条上的方框：下方刻度当前露出的那一段
    function winUpdate() {
      if (ticks.scrollWidth <= ticks.clientWidth + 2) { win.hidden = true; return; }
      const l = ticks.scrollLeft, r = l + ticks.clientWidth;
      let a = -1, z = -1;
      btns.forEach((b, j) => { const c = b.offsetLeft + b.offsetWidth / 2; if (c >= l && c <= r) { if (a < 0) a = j; z = j; } });
      if (a < 0) { win.hidden = true; return; }
      win.hidden = false;
      win.style.left = `calc(${pct(P[a])} - 4px)`;
      win.style.width = `calc(${((P[z] - P[a]) / span * 100).toFixed(3)}% + 8px)`;
    }
    ticks.addEventListener("scroll", winUpdate, { passive: true });
    new ResizeObserver(() => { axisLabels(); winUpdate(); }).observe(strip);
    // 点细条：跳到最近的节点
    strip.addEventListener("click", e => {
      const r = strip.getBoundingClientRect(), y = Y0 + (e.clientX - r.left) / r.width * span;
      let best = 0;
      for (let j = 1; j < o.n; j++) if (Math.abs(P[j] - y) < Math.abs(P[best] - y)) best = j;
      o.pick(best);
    });
    function set(j) {
      if (cur >= 0) { btns[cur].setAttribute("aria-pressed", "false"); marks[cur].classList.remove("on"); }
      cur = j;
      btns[j].setAttribute("aria-pressed", "true"); marks[j].classList.add("on");
      const b = btns[j];
      if (ticks.scrollWidth > ticks.clientWidth)
        ticks.scrollTo({ left: b.offsetLeft - ticks.clientWidth / 2 + b.offsetWidth / 2, behavior: reduce() ? "auto" : "smooth" });
      winUpdate();
    }
    return { set, relabel, ticks };
  }

  window.LIDAI = { parse, encode, lang, saveLang, link, timeline };
})();
