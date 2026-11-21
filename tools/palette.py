# -*- coding: utf-8 -*-
"""给 global/palette.toml 里还没有颜色的政权选色（规范第三节「疆域色」）：按各卷统一引擎算出的疆域里与谁相邻、相近，
在低彩度 OKLCH 色板里挑与邻居色差最大、又不像同卷主朝色（五德）的一个。已有的颜色一概不动。

  python tools/palette.py                列出缺色的政权和建议色（只列不写）
  python tools/palette.py --write        建议色写进 global/palette.toml 的 [color] 末尾
  python tools/palette.py --gid 甲 乙     给这几个政权重选（已有颜色的也重选，按其余政权现在的颜色避让），只列不写

用法：加了新政权以后 python run.py 会在生成 v1 时停下报缺色（这时疆域已按新归属算好），运行本工具选色，--write，
再 python run.py --web。本工具先运行 core/v1/registry.py 与 core/v1/build.py --draft-colors（缺色的先用占位灰）出一遍 v1。

色差的算法同 tools/colorcheck.py：浅、深两种底色上按页面的填色不透明度（部族、弃地、未定之地另乘 0.62，同页面）叠在陆地色上，量 CIEDE2000；
相邻（共享边界）的按边界长度加权，要求色差 12 以上，相距 3° 以内的要求 5 以上；政权、单位两种着色都算，深色底权重减半。
候选色：OKLCH 明度 0.60—0.80、彩度 0.04—0.08、色相每 10°；弃地、未定之地只用近灰的色；只出现在民国卷的政权只在民国卷
「其余」色带（土黄—橄榄—绿—青绿）里选：国民党、共产党、日伪等派系另有色带，要照派系手定。深色由浅色在 OKLCH 里提亮 0.06、
加彩 0.015 得出，同 palette.toml 现有的做法。
"""
import json
import math
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import shapely

sys.path.insert(0, str(Path(__file__).resolve().parent))
from colorcheck import ROOT, ERAS, LAND, OP, hx, blend, lab, de2000, regions  # noqa: E402

try:
    import tomllib
except ImportError:
    import tomli as tomllib

PALETTE = ROOT / "global" / "palette.toml"


# ---------------- OKLCH ----------------
def _lin(c): return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
def _gam(c): return 12.92 * c if c <= .0031308 else 1.055 * c ** (1 / 2.4) - .055


def to_oklab(h):
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l = .4122214708 * r + .5363325363 * g + .0514459929 * b
    m = .2119034982 * r + .6806995451 * g + .1073969566 * b
    s = .0883024619 * r + .2817188376 * g + .6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    return (.2104542553 * l + .7936177850 * m - .0040720468 * s, 1.9779984951 * l - 2.4285922050 * m + .4505937099 * s,
            .0259040371 * l + .7827717662 * m - .8086757660 * s)


def oklab_rgb(L, a, b):
    l = (L + .3963377774 * a + .2158037573 * b) ** 3
    m = (L - .1055613458 * a - .0638541728 * b) ** 3
    s = (L - .0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + .2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - .3413193965 * s,
            -.0041960863 * l - .7034186147 * m + 1.7076147010 * s)


def in_gamut(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    return all(-.001 <= x <= 1.001 for x in oklab_rgb(L, a, b))


def oklch(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    return "#%02X%02X%02X" % tuple(round(min(1, max(0, _gam(min(1, max(0, c))))) * 255) for c in oklab_rgb(L, a, b))


def dark_of(h, lift=.06, clift=.015, lmax=.86):
    """深色：浅色在 OKLCH 里提亮 0.06、加彩 0.015（出色域就逐步减彩）"""
    L, a, b = to_oklab(h)
    C, hue = math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360
    L2, C2 = min(lmax, L + lift), C + clift
    while C2 > 0 and not in_gamut(L2, C2, hue):
        C2 -= .005
    return oklch(L2, max(C2, 0), hue)


CAND = sorted({oklch(L, C, h) for L in (.60, .65, .70, .75, .80) for C in (.04, .06, .08)
               for h in range(0, 360, 10) if in_gamut(L, C, h)})
NEUTRAL = sorted({oklch(L, C, h) for L in (.68, .72, .76, .80) for C in (.01, .02, .03)
                  for h in range(0, 360, 20) if in_gamut(L, C, h)})
MG_OTHER = sorted({oklch(L, C, h) for L in (.62, .68, .74, .80) for C in (.045, .062)
                   for h in range(50, 195, 8) if in_gamut(L, C, h)})


def tribe(kind):
    """页面上淡色填充的几类（core/web/template.html 的 soft）：填色不透明度再乘 0.62"""
    return kind in ("tribe", "waste", "misc")


def blended(col, mode, kind):
    return lab(blend(col, LAND[mode], OP[mode][1 if tribe(kind) else 0]))


# ---------------- 读数据 ----------------
def refresh_v1():
    for args in (["core/v1/registry.py"], ["core/v1/build.py", "--draft-colors"]):
        r = subprocess.run([sys.executable, str(ROOT / args[0])] + args[1:], cwd=ROOT)
        if r.returncode != 0:
            sys.exit(f"失败：{' '.join(args)}（疆域过期就先运行 python run.py 重算）")


def load():
    B = {}
    for era in ERAS:
        p = ROOT / "build" / "v1" / f"{era}.json"
        if not p.exists():
            sys.exit(f"没有 build/v1/{era}.json")
        B[era] = json.loads(p.read_text(encoding="utf8"))
    return B


def neighbours(B, targets):
    """targets 里每个全局 ID 在各卷各节点、两种着色下的邻居：gid → [(邻居 gid, 邻居 kind, 本方 kind, 相邻否, 权重, 卷)]"""
    nb = defaultdict(list)
    for era, d in B.items():
        P = d["polities"]
        if not any(p["gid"] in targets for p in P):
            continue
        for zhen in (False, True):
            for n in d["nodes"]:
                R = regions(d, n, zhen)
                G = [g for _, _, g in R]
                tree = shapely.STRtree(G)
                for i, (_, pk, g) in enumerate(R):
                    A = P[int(pk)]
                    if A["gid"] not in targets or g.is_empty:
                        continue
                    for j in tree.query(g, predicate="dwithin", distance=3):
                        j = int(j)
                        Bp = P[int(R[j][1])]
                        if j == i or Bp["gid"] == A["gid"] or G[j].is_empty:
                            continue
                        dist = g.distance(G[j])
                        adj = dist < .05
                        w = max(g.boundary.intersection(G[j].buffer(.06)).length, .3) if adj else .2 / (1 + dist)
                        nb[A["gid"]].append((Bp["gid"], Bp["kind"], A["kind"], adj, w * (1 if not zhen else .35), era))
    return nb


def main():
    write = "--write" in sys.argv
    bad = [a for a in sys.argv[1:] if a.startswith("--") and a not in ("--write", "--gid")]
    if bad:
        sys.exit("不认识的选项：" + " ".join(bad) + "（只有 --write、--gid）")
    gids = [a for a in sys.argv[1:] if not a.startswith("--")]
    if gids and "--gid" not in sys.argv:
        sys.exit("要给指定的政权重选，写 --gid 再列全局 ID")
    if "--gid" in sys.argv and not gids:
        sys.exit("--gid 后面要列全局 ID")
    if write and gids:
        sys.exit("--gid 只列不写：要改已有政权的颜色，照建议手改 global/palette.toml")
    refresh_v1()
    B = load()
    pal = tomllib.loads(PALETTE.read_text(encoding="utf8"))
    colors = {g: tuple(c) for g, c in pal.get("color", {}).items()}
    wude = pal.get("wude", {})
    anchors = {g: wude[w] for g, w in pal.get("wude", {}).get("gid", {}).items()} if isinstance(wude.get("gid"), dict) else {}
    occ = defaultdict(set)          # gid → 出现在哪些卷
    kind = {}
    for era, d in B.items():
        for p in d["polities"]:
            occ[p["gid"]].add(era)
            kind.setdefault(p["gid"], p["kind"])
    missing = sorted({g for d in B.values() for g in d.get("meta", {}).get("palette_missing", [])})
    targets = list(gids or missing)
    unknown = [g for g in targets if g not in occ]
    if unknown:
        sys.exit("这些全局 ID 不在任何一卷里：" + "、".join(unknown))
    for g in [g for g in targets if g in anchors]:
        print(f"{g}：五德主色由 palette.toml 的 [wude] 定，不重选")
        targets.remove(g)
    if not targets:
        if not gids:
            print("palette.toml 里每个政权都有颜色，没有要选的（给已有的重选用 --gid）")
        return
    nb = neighbours(B, set(targets))
    weight = {g: sum(e[4] for e in nb[g] if e[3]) for g in targets}
    fixed = {g: c for g, c in colors.items() if g not in targets}
    picked = {}
    for g in sorted(targets, key=lambda g: -weight[g]):
        eras = occ[g]
        if kind[g] in ("waste", "misc"):
            base, band = NEUTRAL, "近灰"
        elif eras == {"minguo-xinzhongguo"}:
            base, band = MG_OTHER, "民国卷「其余」色带"
        else:
            base, band = CAND, "低彩度色板"
        cur = {**fixed, **picked}
        edges = [(h, cur[h], hk, gk, adj, w) for h, hk, gk, adj, w, _ in nb[g] if h in cur]   # 还没选色的邻居先不管
        anc = [a for a in anchors if a != g and occ.get(a, set()) & eras]
        best = None
        for c in base:
            dk = dark_of(c)
            cost = 0.0
            for _, hc, hk, gk, adj, w in edges:
                for m, mw, mine, theirs in (("light", 1.0, c, hc[0]), ("dark", .5, dk, hc[1])):
                    de = de2000(blended(mine, m, gk), blended(theirs, m, hk))
                    T = 12.0 if adj else 5.0
                    cost += mw * w * max(T - de, 0) ** 2 / T ** 2
                    if adj:
                        cost += mw * w * 3 * max(6 - de, 0) / 6
            for a in anc:                    # 同卷里不要像主朝的五德色
                de = de2000(lab(hx(c)), lab(hx(anchors[a])))
                cost += .6 * (weight[g] + 2) * max(10 - de, 0) / 10
            if best is None or cost < best[0]:
                best = (cost, c, dk)
        _, c, dk = best
        picked[g] = (c, dk)
        near = sorted({(round(de2000(blended(c, "light", gk), blended(hc[0], "light", hk)), 1), h)
                       for h, hc, hk, gk, adj, w in edges if adj})
        print(f"{g}（{'、'.join(sorted(eras, key=ERAS.index))}；{band}）→ {c} / {dk}" + (f"  —— {kind[g]}" if kind[g] != "state" else ""))
        if near:
            print("    相邻的政权与浅色底上的色差（最小的几个）：" + "，".join(f"{h} {de}" for de, h in near[:5]))
        else:
            print("    没有相邻的政权")
        if g in colors:
            print(f"    现在的颜色：{colors[g][0]} / {colors[g][1]}")
    if write:
        lines = PALETTE.read_text(encoding="utf8").rstrip("\n").split("\n")
        heads = [l.strip() for l in lines if l.strip().startswith("[")]
        if not heads or heads[-1] != "[color]":
            sys.exit("global/palette.toml 的最后一节不是 [color]，没法接在末尾写：请手动补上")
        lines.append(f"# tools/palette.py 按疆域邻接选的（{date.today().isoformat()}）")
        lines += [f'"{g}" = ["{c}", "{dk}"]' for g, (c, dk) in picked.items()]
        PALETTE.write_text("\n".join(lines) + "\n", encoding="utf8")
        print(f"写进 global/palette.toml {len(picked)} 个；接着运行 python run.py --web，再用 tools/colorcheck.py 复查")


if __name__ == "__main__":
    main()
