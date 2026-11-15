# -*- coding: utf-8 -*-
"""旧格式 ↔ v1 的转换（规范第十九节第 2 步）。

旧格式：各卷 docs/<短名>/index.html 里内嵌的 GEO、DATA 两块 JSON，加上注入 CSS 的疆域色。
v1：每卷一份 JSON（build/v1/<短名>.json），字段与写法八卷统一，格式见 core/v1/FORMAT.md。

  extract(html)              从成品页面取出 GEO、DATA 与疆域色
  to_v1(slug, G, D, colors)  旧格式 → v1（不含全局 ID；ID 由 core/v1/build.py 另行挂上）
  from_v1(bundle)            v1 → 旧格式（GEO、DATA、疆域色），用来证明转换无损

v1 是从各卷成品派生出来的交换格式，不是手写的源文件。
"""
import json
import re

DEC = json.JSONDecoder()
BEGIN = -999999          # 「自始」：旧格式里的 0 / -9999 年
MONTHLY = {"minguo-xinzhongguo"}   # 旧格式里整数时间就是月序号的卷


# ---------------------------------------------------------------- 取数

def extract(html):
    out = {}
    for name in ("GEO", "DATA"):
        i = html.index(f"const {name} = ") + len(f"const {name} = ")
        out[name], _ = DEC.raw_decode(html, i)
    colors = None
    for var in ("u", "s"):
        runs = re.findall(r"((?:--%s-\d+:#[0-9A-Fa-f]{3,8};\s?)+)" % var, html)
        if runs:
            light = re.findall(r"--%s-(\d+):(#[0-9A-Fa-f]{3,8});" % var, runs[0])
            dark = re.findall(r"--%s-(\d+):(#[0-9A-Fa-f]{3,8});" % var, runs[1])
            colors = [[l[1], d[1]] for l, d in zip(light, dark)]
            break
    return out["GEO"], out["DATA"], colors


# ---------------------------------------------------------------- 时间

def tm(y, m=None):
    """年（+ 月）→ 月序号 t = 年 × 12 + 月 − 1。"""
    return y * 12 + (m - 1)


def year_end(y):
    return y * 12 + 11


def year_mid(y):
    return y * 12 + 6


class Clock:
    """把一卷旧格式里的各种时间换成 v1 的月序号，并能换回去。"""

    def __init__(self, slug, fam):
        self.monthly = slug in MONTHLY
        self.begin = -9999 if fam == "A" else 0   # 旧格式里表示「自始」的写法：战国式 -9999，唐宋系 0

    # 「从某年起」：名称沿革、归属变化
    def since(self, v):
        if v == self.begin:
            return BEGIN
        return v if self.monthly else v * 12

    def since_back(self, v):
        if v == BEGIN:
            return self.begin
        return v if self.monthly else v // 12

    # 年段（含两端），如都城为都年段、诸族存续
    def span(self, a, b):
        if self.monthly:
            return [a, b]
        return [a * 12, b * 12 + 11]

    def span_back(self, s):
        if self.monthly:
            return list(s)
        return [s[0] // 12, (s[1] - 11) // 12]


# ---------------------------------------------------------------- 几何

class Pool:
    """几何池：相同的环组只存一份。"""

    def __init__(self, base=None):
        self.items = list(base or [])
        self.index = {json.dumps(g, separators=(",", ":")): i for i, g in enumerate(self.items)}

    def add(self, g):
        k = json.dumps(g, separators=(",", ":"))
        if k not in self.index:
            self.index[k] = len(self.items)
            self.items.append(g)
        return self.index[k]


# ---------------------------------------------------------------- 条目

A_EN = {"eold": "old", "emod": "mod", "enote": "note", "eyt": "yt", "esides": "sides", "ecmd": "cmd", "ezhi": "zhi"}
TIME_KEYS = ("y", "m", "y1", "m1", "y0", "yrs", "t", "t0", "t1", "tl")


def item_to_v1(it, clock, slug):
    out, tf = {}, [k for k in TIME_KEYS if k in it]
    en = {}
    for k, v in it.items():
        if k in A_EN:
            en[A_EN[k]] = v
        elif k == "e":
            en.update(v)
        elif k in TIME_KEYS:
            continue
        else:
            out[k] = v
    if "e" in it:
        out["_e"] = 1                    # 唐宋系英文写在 e 里；战国式是 eold 等平铺字段
    if en:
        out["en"] = en
    # 时间：t 起点（或时点）、t1 终点、spans 多段年段、tp 精度（y 年 / m 月）
    if "tl" in it:                       # 战国式：所在地归属变化
        out["owners"] = []
        for part in it["tl"].split(";"):
            y, k = part.split(":", 1)
            out["owners"].append([clock.since(int(y)), k])
    if "yrs" in it:
        if all(isinstance(v, int) for ab in it["yrs"] for v in ab):
            out["spans"] = [clock.span(a, b) for a, b in it["yrs"]]
        else:                            # 两晋、隋唐的为都年段带小数（年中迁都）：换算后另存原值
            out["spans"] = [[round(a * 12, 3), round(b * 12, 3)] for a, b in it["yrs"]]
            out["_yrs"] = it["yrs"]
    if "y0" in it and ("y1" in it or it.get("c") in ("capital", "people", "region", "jun")):
        out["t"], out["t1"] = clock.span(it["y0"], it.get("y1", it["y0"]))
        if "y1" not in it:
            out["t1"] = None
        out["tp"] = "y"
    elif "y0" in it:                     # 运河开凿之年等：从某年起
        out["t"], out["tp"] = clock.since(it["y0"]), "y"
    if "y" in it:
        if it.get("m"):
            out["t"], out["tp"] = tm(it["y"], it["m"]), "m"
        else:
            out["t"], out["tp"] = year_mid(it["y"]), "y"
        if "y1" in it:
            out["t1"] = tm(it["y1"], it["m1"]) if "m1" in it else year_mid(it["y1"])
    if slug in MONTHLY and ("t" in it or "t0" in it):
        out["t"] = it.get("t", it.get("t0"))
        out["t1"] = it.get("t1")
        out["tp"] = "m"
    elif "t0" in it:                     # 两晋行军路线的动画时间（小数年），原样留着
        out["anim"] = [it["t0"], it["t1"]]
    if "y1" in it and "y" not in it and "y0" not in it:
        out["t1"] = year_mid(it["y1"])
    out["_tf"] = ",".join(tf)
    return out


def item_from_v1(o, clock, slug):
    it = {}
    tf = o["_tf"].split(",") if o["_tf"] else []
    for k, v in o.items():
        if k in ("en", "_e", "_tf", "_yrs", "owners", "spans", "t", "t1", "tp", "anim"):
            continue
        it[k] = v
    if "y" in tf:
        t = o["t"]
        monthly = o.get("tp") == "m"
        it["y"] = (t + (0 if monthly else -6)) // 12
        if "m" in tf:                    # 隋唐：月份不详的条目写 m = 0，按年中
            it["m"] = t % 12 + 1 if monthly else 0
        if "y1" in tf:
            t1 = o["t1"]
            it["y1"] = (t1 + (0 if "m1" in tf else -6)) // 12
            if "m1" in tf:
                it["m1"] = t1 % 12 + 1
    if "y0" in tf:
        if "y1" in tf or it.get("c") in ("capital", "people", "region", "jun"):
            a, b = clock.span_back([o["t"], o["t1"] if o["t1"] is not None else o["t"] + 11])
            it["y0"] = a
            if "y1" in tf:
                it["y1"] = b
        else:
            it["y0"] = clock.since_back(o["t"])
    if "y1" in tf and "y" not in tf and "y0" not in tf:
        it["y1"] = (o["t1"] - 6) // 12
    if "yrs" in tf:
        it["yrs"] = o["_yrs"] if "_yrs" in o else [clock.span_back(s) for s in o["spans"]]
    if slug in MONTHLY:
        if "t" in tf:
            it["t"] = o["t"]
        if "t0" in tf:
            it["t0"] = o["t"]
        if "t1" in tf:
            it["t1"] = o["t1"]
    elif "t0" in tf:
        it["t0"], it["t1"] = o["anim"]
    if "tl" in tf:
        it["tl"] = ";".join(f"{clock.since_back(t)}:{k}" for t, k in o["owners"])
    en = o.get("en")
    if en is not None:
        if o.get("_e"):
            it["e"] = en
        else:
            rev = {v: k for k, v in A_EN.items()}
            for k, v in en.items():
                it[rev[k]] = v
    return _order(it, o)


def _order(d, ref):
    return d   # 字典比较不看顺序；成品重新拼装时由各卷自己的 assemble 决定顺序


# ---------------------------------------------------------------- 节点

def node_to_v1(sn, clock, pool, inline, fam):
    n = {}
    if fam == "A":
        n["t"], n["tp"] = year_end(sn["y"]), "y"
        n["title"], n["desc"] = sn["t"], sn["d"]
        n["en"] = {"title": sn["te"], "desc": sn["de"]}
        n["short"] = sn["sh"]
        n["en"]["short"] = sn["she"]
        n["u"] = {k: pool.add(v) for k, v in sn["s"].items()}
        n["ul"] = sn["l"]
        n["pol"] = {k: k for k in sn["s"]}
        if "lab" in sn:
            n["lab"] = sn["lab"]
            n["en"]["lab"] = sn["labe"]
        n["ext"] = {k: sn[k] for k in ("j", "w") if k in sn}
        return n
    if "ti" in sn:                       # 民国：t 是月序号，标题在 ti
        n["t"], n["tp"], n["title"] = sn["t"], "m", sn["ti"]
    elif "m" in sn:
        n["t"], n["tp"], n["title"] = tm(sn["y"], sn["m"]), "m", sn["t"]
    else:
        n["t"], n["tp"], n["title"] = year_end(sn["y"]), "y", sn["t"]
    n["desc"] = sn["d"]
    n["era"] = sn["era"]
    en = {"title": sn["te"], "desc": sn["de"], "era": sn["erae"]}
    if "era2" in sn:
        n["era2"] = sn["era2"]
    if "era2e" in sn:
        en["era2"] = sn["era2e"]
    if inline:
        n["u"] = {k: pool.add(v) for k, v in sn["z"].items()}
        n["pu"] = {k: pool.add(v) for k, v in sn["p"].items()}
    else:
        n["u"], n["pu"] = sn["z"], sn["p"]
    n["ul"], n["pul"] = sn["lz"], sn["lp"]
    for k in ("pol", "own", "seat", "h", "lab", "kd", "col", "jn"):
        if k in sn:
            n[k] = sn[k]
    en["lab"] = sn["labe"]
    n["en"] = en
    ext = {k: sn[k] for k in ("zb", "zl") if k in sn}
    if ext:
        n["ext"] = ext
    return n


def node_from_v1(n, form, pool, inline, fam):
    if fam == "A":
        sn = {"y": (n["t"] - 11) // 12, "t": n["title"], "d": n["desc"],
              "s": {k: pool[i] for k, i in n["u"].items()}, "l": n["ul"],
              "sh": n["short"], "te": n["en"]["title"], "she": n["en"]["short"], "de": n["en"]["desc"]}
        sn.update(n.get("ext", {}))
        if "lab" in n:
            sn["lab"], sn["labe"] = n["lab"], n["en"]["lab"]
        return sn
    sn = {}
    if form == "ymt":
        sn.update(y=n["t"] // 12, m=n["t"] % 12 + 1, t=n["t"], ti=n["title"])
    elif form == "ym":
        sn.update(y=n["t"] // 12, m=n["t"] % 12 + 1, t=n["title"])
    else:
        sn.update(y=(n["t"] - 11) // 12, t=n["title"])
    sn["d"], sn["era"] = n["desc"], n["era"]
    if "era2" in n:
        sn["era2"] = n["era2"]
    if inline:
        sn["z"] = {k: pool[i] for k, i in n["u"].items()}
        sn["p"] = {k: pool[i] for k, i in n["pu"].items()}
    else:
        sn["z"], sn["p"] = n["u"], n["pu"]
    sn["lz"], sn["lp"] = n["ul"], n["pul"]
    for k in ("pol", "own", "seat", "h", "lab", "kd", "col", "jn"):
        if k in n:
            sn[k] = n[k]
    en = n["en"]
    sn.update(te=en["title"], de=en["desc"], erae=en["era"], labe=en["lab"])
    if "era2" in en:
        sn["era2e"] = en["era2"]
    sn.update(n.get("ext", {}))
    return sn


# ---------------------------------------------------------------- 整卷

BASE_KEYS = ("land", "prov", "border", "rivers", "lakes", "canals", "deserts", "seas", "regions", "routes")
EXTENT_KEYS = ("ext", "base", "extpoly", "proj")


def to_v1(slug, G, D, colors):
    fam = "A" if "states" in D else "B"
    clock = Clock(slug, fam)
    sn0 = G["snaps"][0]
    if fam == "A":
        inline = True
        pool = Pool()
        form = "y"
    else:
        z0 = next(iter(sn0["z"].values()))
        inline = isinstance(z0, list)
        pool = Pool(None if inline else G["pool"])
        form = "ymt" if "ti" in sn0 else ("ym" if "m" in sn0 else "y")
    nodes = [node_to_v1(sn, clock, pool, inline, fam) for sn in G["snaps"]]

    # 底图与图层：v1.0 沿用旧结构，只把隋唐的单条 route 并进 routes
    base = {k: G[k] for k in BASE_KEYS if k in G}
    if "route" in G:
        base["routes"] = [G["route"]]
    extent = {k: G[k] for k in EXTENT_KEYS if k in G}

    items, polities, places = [], [], []
    if fam == "A":
        state_items = {it["k"]: it for it in D["items"] if it["c"] == "state"}
        for k in D["states"]:
            si = state_items[k]
            polities.append({"key": k, "n": si["old"], "mod": si["mod"], "note": si["note"],
                             "kind": D["kinds"].get(k, "state"), "color": D["colors"][k], "item": si["i"],
                             "en": {"n": si["eold"], "mod": si["emod"], "note": si["enote"]}})
        for it in D["items"]:
            if it["c"] == "state":
                continue
            o = item_to_v1(it, clock, slug)
            items.append(o)
            if it["c"] in ("capital", "city", "town", "pass") and "tl" in it:
                places.append({"key": f"i:{it['i']}", "n": it["old"], "mod": it["mod"], "lon": it["lon"],
                               "lat": it["lat"], "kind": it["c"], "owners": o["owners"], "item": it["i"],
                               "en": {"n": it.get("eold"), "mod": it.get("emod")}})
    else:
        for i, u in enumerate(D["units"]):
            p = {"key": u["k"], "n": u["n"], "kind": u["kind"], "note": u["note"],
                 "en": {k2: u[k] for k, k2 in (("ne", "n"), ("se", "s"), ("notee", "note")) if k in u},
                 "color": colors[i]}
            for k in ("x", "waste"):
                if k in u:
                    p[k] = u[k]
            polities.append(p)
        for s in D["seeds"]:
            p = {"key": s["id"], "n": s["n"], "mod": s["mod"], "lon": s["lon"], "lat": s["lat"], "kind": s["t"]}
            if "nm" in s:
                p["names"] = [[clock.since(t), nm] for t, nm in s["nm"]]
            for k in ("jn", "jnm", "note"):
                if k in s:
                    p[k] = [[clock.since(t), v] for t, v in s[k]] if k == "jnm" else s[k]
            en = {k2: s[k] for k, k2 in (("ne", "n"), ("nme", "names"), ("mode", "mod"), ("notee", "note"),
                                         ("jne", "jn"), ("jnme", "jnm")) if k in s}
            if en:
                p["en"] = en
            places.append(p)
        items = [item_to_v1(it, clock, slug) for it in D["items"]]

    first = G.get("first")
    if first is None:                    # 隋唐把首屏记成节点序号
        first_t = nodes[D["first"]]["t"]
    elif fam == "A" or form == "y":
        first_t = year_end(first)
    else:
        first_t = first
    ext = {}
    for k in ("falls", "alleg", "playms", "p0"):
        if k in D:
            ext[k] = D[k]
    if "zhoue" in G:
        ext["zhoue"] = G["zhoue"]
    if "en" in D:
        ext["en"] = D["en"]
    bundle = {
        "v": 1, "era": slug, "model": "simple" if fam == "A" else "layered",
        "time": "month" if form in ("ym", "ymt") else "year",
        "first": first_t, "geom": pool.items, "base": base, "extent": extent,
        "polities": polities, "places": places, "nodes": nodes, "items": items, "ext": ext,
        "_legacy": {"fam": fam, "form": form, "inline": inline, "pool": "pool" in G,
                    "route1": "route" in G, "first": "G" if first is not None else "D",
                    "colors": colors if fam == "B" else None},
    }
    return bundle


def from_v1(b):
    lg, slug = b["_legacy"], b["era"]
    fam, form, inline = lg["fam"], lg["form"], lg["inline"]
    clock = Clock(slug, fam)
    pool = b["geom"]
    G, D = {}, {}
    for k, v in b["base"].items():
        G[k] = v
    if lg["route1"]:
        G["route"] = G.pop("routes")[0]
    G.update(b["extent"])
    if "zhoue" in b["ext"]:
        G["zhoue"] = b["ext"]["zhoue"]
    G["snaps"] = [node_from_v1(n, form, pool, inline, fam) for n in b["nodes"]]
    if fam == "B" and not inline:
        G["pool"] = pool
    if lg["first"] == "G":
        G["first"] = b["first"] if (fam == "B" and form != "y") else (b["first"] - 11) // 12
    else:
        D["first"] = [n["t"] for n in b["nodes"]].index(b["first"])
    colors = None
    if fam == "A":
        D["states"] = [p["key"] for p in b["polities"]]
        D["colors"] = {p["key"]: p["color"] for p in b["polities"]}
        D["kinds"] = {p["key"]: p["kind"] for p in b["polities"] if p["kind"] != "state"}
        items = [item_from_v1(o, clock, slug) for o in b["items"]]
        for p in b["polities"]:
            items.append({"c": "state", "k": p["key"], "old": p["n"], "mod": p["mod"], "note": p["note"],
                          "i": p["item"], "eold": p["en"]["n"], "emod": p["en"]["mod"], "enote": p["en"]["note"]})
        D["items"] = sorted(items, key=lambda it: it["i"])
    else:
        units, colors = [], []
        for p in b["polities"]:
            u = {"k": p["key"], "n": p["n"], "kind": p["kind"], "note": p["note"]}
            for k, k2 in (("ne", "n"), ("se", "s"), ("notee", "note")):
                if k2 in p["en"]:
                    u[k] = p["en"][k2]
            for k in ("x", "waste"):
                if k in p:
                    u[k] = p[k]
            units.append(u)
            colors.append(p["color"])
        D["units"] = units
        seeds = []
        for p in b["places"]:
            s = {"id": p["key"], "n": p["n"], "mod": p["mod"], "lon": p["lon"], "lat": p["lat"], "t": p["kind"]}
            if "names" in p:
                s["nm"] = [[clock.since_back(t), nm] for t, nm in p["names"]]
            for k in ("jn", "note"):
                if k in p:
                    s[k] = p[k]
            if "jnm" in p:
                s["jnm"] = [[clock.since_back(t), v] for t, v in p["jnm"]]
            for k, k2 in (("ne", "n"), ("nme", "names"), ("mode", "mod"), ("notee", "note"), ("jne", "jn"), ("jnme", "jnm")):
                if k2 in p.get("en", {}):
                    s[k] = p["en"][k2]
            seeds.append(s)
        D["seeds"] = seeds
        D["items"] = [item_from_v1(o, clock, slug) for o in b["items"]]
    for k in ("falls", "alleg", "playms", "p0"):
        if k in b["ext"]:
            D[k] = b["ext"][k]
    if "en" in b["ext"]:
        D["en"] = b["ext"]["en"]
    return G, D, colors
