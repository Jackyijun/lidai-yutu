# -*- coding: utf-8 -*-
"""配色普查：各卷每个节点里相邻（或相近）疆域的感知色差（CIEDE2000，按页面的填色不透明度叠在底色上算）。

  python3 tools/colorcheck.py [短名...] [--zhen] [--dark] [--json]

读 build/v1/<短名>.json（先跑 python run.py --v1 或 --web）。缺省按政权着色（春秋即共主着色：奉周的诸侯并入周）、浅色底；
--zhen 按单位着色（郡国、方镇、路、派系；春秋、战国是各诸侯国，即两卷页面缺省的着色），--dark 深色底。列出：相邻且色差小于 10、相距 3° 以内且色差小于 4、同色的政权对。
--json 把明细写到 build/colorcheck.json。改 global/palette.toml 后用它复查（规范第三节）。
"""
import json, math, sys
from pathlib import Path
from collections import defaultdict
import shapely
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[1]
ERAS = ["chunqiu", "zhanguo", "qinhan", "hanmosanguo", "liangjin-nanbeichao", "suitang", "tangsong", "songyuan", "minguo-xinzhongguo"]
LAND = {"light": "#ECEBE3", "dark": "#1C1E22"}
OP = {"light": (.5, .5 * .62), "dark": (.34, .34 * .62)}


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def blend(c, bg, a):
    return tuple(a * x + (1 - a) * y for x, y in zip(hx(c), hx(bg)))


def lab(rgb):
    def lin(v):
        return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    r, g, b = map(lin, rgb)
    X = (r * .4124 + g * .3576 + b * .1805) / .95047
    Y = (r * .2126 + g * .7152 + b * .0722)
    Z = (r * .0193 + g * .1192 + b * .9505) / 1.08883
    f = lambda t: t ** (1 / 3) if t > .008856 else 7.787 * t + 16 / 116
    return (116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z)))


def de2000(l1, l2):
    L1, a1, b1 = l1; L2, a2, b2 = l2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = .5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dh = h2p - h1p
    if C1p * C2p == 0: dh = 0
    elif dh > 180: dh -= 360
    elif dh < -180: dh += 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0: hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180: hbp = (h1p + h2p) / 2
    elif h1p + h2p < 360: hbp = (h1p + h2p + 360) / 2
    else: hbp = (h1p + h2p - 360) / 2
    T = 1 - .17 * math.cos(math.radians(hbp - 30)) + .24 * math.cos(math.radians(2 * hbp)) + .32 * math.cos(math.radians(3 * hbp + 6)) - .2 * math.cos(math.radians(4 * hbp - 63))
    dth = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    RC = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    SL = 1 + .015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2)
    SC, SH = 1 + .045 * Cbp, 1 + .015 * Cbp * T
    RT = -math.sin(math.radians(2 * dth)) * RC
    return math.sqrt((dLp / SL) ** 2 + (dCp / SC) ** 2 + (dHp / SH) ** 2 + RT * (dCp / SC) * (dHp / SH))


def rings(d, gi):
    out = []
    for r in d["geom"][gi]:
        x, y, pts = r[0], r[1], [(r[0] / 100, r[1] / 100)]
        for i in range(2, len(r), 2):
            x += r[i]; y += r[i + 1]; pts.append((x / 100, y / 100))
        if len(pts) >= 4:
            out.append(pts)
    return out


def geom(d, gi, cache={}):
    key = (id(d), gi)
    if key not in cache:
        g = None
        for r in rings(d, gi):
            p = Polygon(r).buffer(0)
            g = p if g is None else g.symmetric_difference(p)
        cache[key] = g if g is not None else Polygon()
    return cache[key]


def regions(d, n, zhen=False):
    """节点 n 在页面上画出来的填色块：[(键, 政权序号/键, 几何)]"""
    P = d["polities"]
    pol = {u: str(p) for u, p in n.get("pol", {}).items()}
    multi = set(n.get("pu", {}))
    out = []
    for u, g in n["u"].items():
        if not zhen and pol.get(u, u) in multi:
            continue
        out.append((u, u, geom(d, g)))
    if not zhen:
        for p, g in n["pu"].items():
            out.append((p, p, geom(d, g)))
    return out


def run(era, zhen=False, mode="light"):
    d = json.load(open(f"{ROOT}/build/v1/{era}.json"))
    P = d["polities"]
    pinfo = lambda k: P[int(k)]
    issues = []
    for ni, n in enumerate(d["nodes"]):
        R = regions(d, n, zhen)
        col = n.get("col") or {}
        info = []
        for k, pk, g in R:
            p = pinfo(pk)
            c = (col.get(k) or p["color"])[0 if mode == "light" else 1]
            a = OP[mode][1 if p["kind"] == "tribe" else 0]
            info.append((p["n"], p["kind"], c, lab(blend(c, LAND[mode], a)), g, p["key"]))
        for i in range(len(info)):
            for j in range(i + 1, len(info)):
                A, B = info[i], info[j]
                if A[0] == B[0]:
                    continue
                dist = A[4].distance(B[4])
                if dist > 3:
                    continue
                de = de2000(A[3], B[3])
                adj = dist < .05
                if (adj and de < 10) or (de < 4 and dist <= 3) or (A[2] == B[2]):
                    shared = A[4].boundary.intersection(B[4].buffer(.05)).length if adj else 0
                    issues.append(dict(era=era, node=n.get("short") or n["title"], t=n["t"], a=A[0], b=B[0], ca=A[2], cb=B[2],
                                       ka=A[1], kb=B[1], de=round(de, 1), adj=adj, dist=round(dist, 2), shared=round(shared, 1)))
    return issues


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    zhen = "--zhen" in sys.argv
    mode = "dark" if "--dark" in sys.argv else "light"
    allis = []
    for era in args or ERAS:
        iss = run(era, zhen, mode)
        allis += iss
        pairs = defaultdict(list)
        for x in iss:
            pairs[tuple(sorted([x["a"], x["b"]]))].append(x)
        bad = sorted(pairs.items(), key=lambda kv: min(x["de"] for x in kv[1]))
        print(f"== {era}: {len(pairs)} 对（{sum(1 for v in pairs.values() if any(x['adj'] for x in v))} 对相邻）")
        for (a, b), xs in bad[:400]:
            x = min(xs, key=lambda x: x["de"])
            ca, ka, cb, kb = (x["ca"], x["ka"], x["cb"], x["kb"]) if x["a"] == a else (x["cb"], x["kb"], x["ca"], x["ka"])
            print(f"  ΔE {x['de']:>5}  {'相邻' if any(y['adj'] for y in xs) else '相近'}  {a}({ca},{ka[0]}) / {b}({cb},{kb[0]})  ×{len(xs)} 节点  如 {x['node']}")
    if "--json" in sys.argv:
        json.dump(allis, open(ROOT / "build" / "colorcheck.json", "w"), ensure_ascii=False)
