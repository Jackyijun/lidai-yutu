#!/usr/bin/env python3
"""历代舆图 · 缩略图生成器

从某张形势图自己的 index.html 里读出内嵌的 GEO / DATA，按该图自己的投影和色板，
把某一个时间节点的疆域重绘成一幅 360×270 的小图（SVG），供总览页的目录卡片使用。
简单模型（战国式，节点里有 s/l）与分层模型（唐宋式，节点里有 z/p/pol）都能处理。

用法
  python3 tools/thumbs.py 图的index.html --id zg --year -300
  python3 tools/thumbs.py 图的index.html --id ts --year 820 --mode zhen --box 95 127.5 19 46.5
  python3 tools/thumbs.py 图的index.html --id st --blank --box 99 125 21.5 43.5   # 编修中：只画底图

输出（写到 --out 目录，默认当前目录）
  thumb-<id>.svg        直接粘进总览页对应卷的 .thumb-in 里
  thumb-<id>.css.txt    两行颜色 token（浅色一行、深色一行），粘进总览页 :root 与两个深色块
参数
  --box 西 东 南 北     缩略图取景的经纬框；缺省取该图源码里 FITS 的 cn 或 all
  --mode zhen|pol       分层模型的着色：藩镇（缺省）或政权
"""
import argparse, json, math, os, re, sys

W, H = 360, 270
RAD = math.pi / 180


# ---------------------------------------------------------------- 读源码
def extract(path):
    s = open(path, encoding="utf8").read()
    out = {}
    dec = json.JSONDecoder()
    for name in ("GEO", "DATA"):
        m = re.search(r"const %s\s*=\s*" % name, s)
        if not m:
            sys.exit(f"{path} 里没有找到 const {name}")
        out[name], _ = dec.raw_decode(s, m.end())
    return s, out["GEO"], out["DATA"]


def source_center(src):
    m0 = re.search(r"p0\s*=\s*([\d.]+)\s*\*\s*RAD", src)
    m1 = re.search(r"l0\s*=\s*([\d.]+)\s*\*\s*RAD", src)
    if not (m0 and m1):
        sys.exit("源码里找不到投影中心（p0 / l0）")
    return float(m1.group(1)), float(m0.group(1))


def source_box(src):
    m = re.search(r"const FITS\s*=\s*\{(.*?)\};", src, re.S)
    if m:
        for key in ("cn", "all"):
            k = re.search(key + r"\s*:\s*\[([^\]]+)\]", m.group(1))
            if k:
                return [float(v) for v in k.group(1).split(",")]
    sys.exit("源码里找不到 FITS，请用 --box 指定取景")


def css_colors(src, prefix):
    """读 :root 与深色块里的 --<prefix>-N 色值。"""
    root = src[src.index(":root {"):src.index("@media (prefers-color-scheme")]
    dark_block = src[src.index("@media (prefers-color-scheme"):]
    dark_block = dark_block[:dark_block.index("}")]
    pat = r"--%s-(\d+):\s*(#[0-9A-Fa-f]{6})" % prefix
    return dict(re.findall(pat, root)), dict(re.findall(pat, dark_block))


# ---------------------------------------------------------------- 投影与取景
class Albers:
    def __init__(self, l0, p0):
        p1, p2 = 25 * RAD, 47 * RAD
        self.n = (math.sin(p1) + math.sin(p2)) / 2
        self.C = math.cos(p1) ** 2 + 2 * self.n * math.sin(p1)
        self.rho0 = math.sqrt(self.C - 2 * self.n * math.sin(p0 * RAD)) / self.n
        self.l0 = l0 * RAD

    def __call__(self, lon, lat):
        r = math.sqrt(max(self.C - 2 * self.n * math.sin(lat * RAD), 1e-9)) / self.n
        th = self.n * (lon * RAD - self.l0)
        return (r * math.sin(th) * 1000, -(self.rho0 - r * math.cos(th)) * 1000)


class View:
    def __init__(self, pr, box):
        lo0, lo1, la0, la1 = box
        pts = []
        for i in range(25):
            t = i / 24
            pts += [pr(lo0 + (lo1 - lo0) * t, la1), pr(lo0 + (lo1 - lo0) * t, la0),
                    pr(lo0, la0 + (la1 - la0) * t), pr(lo1, la0 + (la1 - la0) * t)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        self.k = min(W / (x1 - x0), H / (y1 - y0))
        self.ox = (W - (x1 - x0) * self.k) / 2 - x0 * self.k
        self.oy = (H - (y1 - y0) * self.k) / 2 - y0 * self.k
        self.pr = pr
        a, b = self.ll((lo0 + lo1) / 2, 34), self.ll((lo0 + lo1) / 2, 35)
        self.ppd = math.hypot(a[0] - b[0], a[1] - b[1])

    def ll(self, lon, lat):
        x, y = self.pr(lon, lat)
        return (x * self.k + self.ox, y * self.k + self.oy)


# ---------------------------------------------------------------- 几何
def decode(flat):
    out, x, y = [], 0, 0
    for i in range(0, len(flat), 2):
        x += flat[i]; y += flat[i + 1]
        out.append((x / 100, y / 100))
    return out


def clip_ring(pts, m=6):
    def clip(poly, inside, inter):
        out = []
        for i in range(len(poly)):
            cur, prev = poly[i], poly[i - 1]
            if inside(cur):
                if not inside(prev): out.append(inter(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(inter(prev, cur))
        return out
    ix = lambda xv: (lambda a, b: (xv, a[1] + (b[1] - a[1]) * (xv - a[0]) / (b[0] - a[0])))
    iy = lambda yv: (lambda a, b: (a[0] + (b[0] - a[0]) * (yv - a[1]) / (b[1] - a[1]), yv))
    poly = pts
    for inside, inter in ((lambda p: p[0] >= -m, ix(-m)), (lambda p: p[0] <= W + m, ix(W + m)),
                          (lambda p: p[1] >= -m, iy(-m)), (lambda p: p[1] <= H + m, iy(H + m))):
        if not poly: break
        poly = clip(poly, inside, inter)
    return poly


def simplify(pts, tol):
    """Douglas-Peucker，迭代实现。"""
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i0, i1 = stack.pop()
        a, b = pts[i0], pts[i1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        best, bi = -1, None
        for i in range(i0 + 1, i1):
            p = pts[i]
            d = abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / L if L > 1e-9 else math.hypot(p[0] - a[0], p[1] - a[1])
            if d > best: best, bi = d, i
        if bi is not None and best > tol:
            keep[bi] = True
            stack += [(i0, bi), (bi, i1)]
    return [p for p, k in zip(pts, keep) if k]


fmt = lambda p: f"{round(p[0], 1):g} {round(p[1], 1):g}"


def ring_d(view, flat, tol=.55):
    pts = clip_ring([view.ll(*q) for q in decode(flat)])
    if len(pts) < 3: return ""
    s = simplify(pts + [pts[0]], tol)[:-1]
    if len(s) < 3: return ""
    xs, ys = [p[0] for p in s], [p[1] for p in s]
    if max(xs) - min(xs) < .8 and max(ys) - min(ys) < .8: return ""
    return "M" + "L".join(fmt(p) for p in s) + "Z"


def rings_d(view, rings, tol=.55):
    return "".join(ring_d(view, r, tol) for r in rings)


def line_d(view, flat, tol=.5):
    runs, cur = [], []
    for p in (view.ll(*q) for q in decode(flat)):
        if -10 <= p[0] <= W + 10 and -10 <= p[1] <= H + 10: cur.append(p)
        else:
            if len(cur) > 1: runs.append(cur)
            cur = []
    if len(cur) > 1: runs.append(cur)
    return "".join("M" + "L".join(fmt(p) for p in simplify(r, tol)) for r in runs)


def graticule(view, box):
    lo0, lo1, la0, la1 = box
    lons = range(int(lo0 // 5 * 5) - 5, int(lo1) + 10, 5)
    lats = range(int(la0 // 5 * 5) - 5, int(la1) + 10, 5)
    d = ""
    for lo in lons:
        d += "M" + "L".join(fmt(p) for p in simplify([view.ll(lo, la / 2) for la in range(lats[0] * 2, lats[-1] * 2 + 1)], .3))
    for la in lats:
        d += "M" + "L".join(fmt(p) for p in simplify([view.ll(lo / 2, la) for lo in range(lons[0] * 2, lons[-1] * 2 + 1)], .3))
    return d


# ---------------------------------------------------------------- 注记与组装
def place_labels(cands):
    placed, out = [], []
    for x, y, t, fs, var in sorted(cands, key=lambda c: -c[3]):
        n = len(t)
        ls = fs * (.32 if n <= 3 else .08)
        w = n * fs + (n - 1) * ls
        bx = (x - w / 2 - 2, y - fs / 2 - 2, x + w / 2 + 2, y + fs / 2 + 2)
        if bx[0] < 2 or bx[2] > W - 2 or bx[1] < 2 or bx[3] > H - 2: continue
        if any(not (bx[2] < b[0] or bx[0] > b[2] or bx[3] < b[1] or bx[1] > b[3]) for b in placed): continue
        placed.append(bx)
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs:.1f}" letter-spacing="{ls:.2f}" '
                   f'style="fill:color-mix(in srgb,var({var}) 45%,var(--ink))">{t}</text>')
    return "".join(out)


def terr_path(d, var, tribe=False, sub=False):
    cls = " ".join(c for c, on in (("tribe", tribe), ("sub", sub)) if on)
    return (f'<path{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} d="{d}" '
            f'style="fill:var({var});stroke:color-mix(in srgb,var({var}) 62%,var(--ink))"/>')


def assemble(mid, land, grat, rivers, terr="", extra="", labels=""):
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
            f'<defs><clipPath id="lc-{mid}"><path d="{land}"/></clipPath></defs>'
            f'<rect class="t-sea" width="{W}" height="{H}"/>'
            f'<path class="t-land" d="{land}"/>'
            f'<path class="t-grat" d="{grat}"/>'
            f'<g class="t-terr" clip-path="url(#lc-{mid})">{terr}</g>{extra}'
            f'<path class="t-coast" d="{land}"/>'
            f'<path class="t-river" d="{rivers}"/>'
            f'<g class="t-lab">{labels}</g></svg>')


def base(view, geo, box):
    land = "".join(rings_d(view, poly, .6) for poly in geo["land"])
    rivers = "".join(line_d(view, r["p"]) for r in geo["rivers"] if r.get("k") == "major")
    return land, graticule(view, box), rivers


def simple_model(mid, geo, data, sn, view):
    states = data["states"]
    terr, cands, light, dark = "", [], [], []
    for st, rings in sn["s"].items():
        var = f"--{mid}-{states.index(st)}"
        d = rings_d(view, rings)
        if not d: continue
        tribe = any(i.get("c") == "state" and i.get("k") == st and i.get("tribe") for i in data["items"]) or st == "义渠"
        terr += terr_path(d, var, tribe=tribe)
        lc, dc = data["colors"][st]
        light.append(f"{var}:{lc}"); dark.append(f"{var}:{dc}")
        anc = max(sn.get("l", {}).get(st, []), key=lambda a: a[2], default=None)
        if anc:
            x, y = view.ll(anc[0], anc[1])
            fs = max(7.5, min(17, anc[3] * view.ppd * .62))
            if fs >= 8: cands.append((x, y, st, fs, var))
    return terr, "", place_labels(cands), light, dark


def layered_model(mid, src, data, sn, view, mode):
    units = data["units"]
    lc, dc = css_colors(src, "u")
    pol = {int(k): v for k, v in sn["pol"].items()}
    multi = {int(k) for k in sn["p"]}
    terr, used = "", set()
    for k, rings in sn["z"].items():
        u = int(k); p = pol.get(u, u)
        if mode != "zhen" and p in multi: continue
        d = rings_d(view, rings)
        if d:
            terr += terr_path(d, f"--{mid}-{u}", tribe=units[u]["kind"] == "tribe", sub=p != u)
            used.add(u)
    if mode != "zhen":
        for k, rings in sn["p"].items():
            d = rings_d(view, rings)
            if d: terr += terr_path(d, f"--{mid}-{k}"); used.add(int(k))
    tops = sorted(set(pol.values()) | {int(k) for k in sn["z"]})
    outl, cands = "", []
    for p in tops:
        if pol.get(p, p) != p and p not in multi: continue
        key = str(p)
        rings = sn["p"].get(key) if p in multi else sn["z"].get(key)
        if rings and units[p]["kind"] != "tribe":
            d = rings_d(view, rings, .5)
            if d: outl += f'<path class="t-polb{" strong" if p in multi else ""}" d="{d}"/>'
        anc = sn["lp"].get(key) if p in multi else sn["lz"].get(key)
        if anc:
            name = re.sub(r"[（(].*?[）)]", "", sn.get("lab", {}).get(key) or units[p]["n"])
            x, y = view.ll(anc[0], anc[1])
            rpx = anc[3] * view.ppd  # 注记点处的内切半径（像素）
            fs = max(7.5, min(18, rpx * .5))
            if len(name) <= 2: fs = max(fs, min(10, rpx * .8))  # 一两字的短名能放进更小的疆域
            if p in multi: fs = max(fs, 15)
            if fs >= 8.5: cands.append((x, y, name, fs, f"--{mid}-{p}")); used.add(p)
    light = [f"--{mid}-{u}:{lc[str(u)]}" for u in sorted(used)]
    dark = [f"--{mid}-{u}:{dc[str(u)]}" for u in sorted(used)]
    return terr, f'<g clip-path="url(#lc-{mid})">{outl}</g>', place_labels(cands), light, dark


def build(path, mid, year=None, box=None, mode="zhen", blank=False, node=None):
    src, geo, data = extract(path)
    box = box or source_box(src)
    view = View(Albers(*source_center(src)), box)
    land, grat, rivers = base(view, geo, box)
    if blank:
        return assemble(mid, land, grat, rivers), "", ""
    snaps = geo["snaps"]
    if node is not None:  # 同一年有几个节点时（如隋唐图按月分节点），用序号指定
        if not 0 <= node < len(snaps):
            sys.exit(f"节点序号应在 0 — {len(snaps) - 1} 之间")
        sn = snaps[node]
    else:
        if year is None:  # 缺省取该图打开时的节点：GEO.first 记年份，DATA.first 记序号
            if "first" in geo:
                year = geo["first"]
            else:
                year = snaps[data.get("first", 0)]["y"] if isinstance(data, dict) else snaps[0]["y"]
        sn = next((s for s in snaps if s["y"] == year), None)
    if sn is None:
        sys.exit(f"没有 {year} 年的节点；可选：{[s['y'] for s in snaps]}")
    pool = geo.get("pool")
    if pool:  # 汉末三国式：疆域几何存于共享池，节点里只记编号
        for key in ("z", "p"):
            sn[key] = {u: pool[v] if isinstance(v, int) else v for u, v in sn.get(key, {}).items()}
    if "s" in sn:
        terr, extra, labels, light, dark = simple_model(mid, geo, data, sn, view)
    else:
        terr, extra, labels, light, dark = layered_model(mid, src, data, sn, view, mode)
    return assemble(mid, land, grat, rivers, terr, extra, labels), ";".join(light), ";".join(dark)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="为历代舆图总览页生成某张形势图的缩略图")
    ap.add_argument("html")
    ap.add_argument("--id", required=True, help="短代号，用作颜色 token 前缀与 clipPath id，如 zg / ts / st")
    ap.add_argument("--year", type=int, help="取哪个节点；缺省取该图打开时的节点（GEO.first），没有则取第一个")
    ap.add_argument("--node", type=int, help="按序号取节点（从 0 起），同一年有多个节点时用")
    ap.add_argument("--box", type=float, nargs=4, metavar=("W", "E", "S", "N"))
    ap.add_argument("--mode", default="zhen", choices=["zhen", "pol"])
    ap.add_argument("--blank", action="store_true")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    svg, light, dark = build(a.html, a.id, a.year, a.box, a.mode, a.blank, a.node)
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, f"thumb-{a.id}.svg"), "w", encoding="utf8").write(svg)
    open(os.path.join(a.out, f"thumb-{a.id}.css.txt"), "w", encoding="utf8").write(f"/* light */ {light}\n/* dark */ {dark}\n")
    print(f"thumb-{a.id}.svg  {len(svg):,} bytes")
