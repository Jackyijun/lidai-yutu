# -*- coding: utf-8 -*-
"""春秋、战国两卷改用统一模板（core/web/template.html）：把两卷的数据转成统一模板读的写法（唐宋系旧格式）。

两卷的 v1 早已是「点 → 单位 → 政权」的分层写法（架构整理第二批），只是页面还用战国式模板，
由 legacy.from_v1 转回战国式旧格式。这里在那份战国式 GEO、DATA 上再转一步：

  诸侯国、戎狄部族        → 单位 units（kind state / tribe），政权层取 v1 节点的 pol（春秋：奉周的诸侯归「周」）
  名城要邑、一般城邑条目  → 州府 seeds（t = z / t），各节点的归属 own 按条目的归属变化 tl 推到节点年份
  事件·变法（culture）    → 事件 event
  长城、驰道直道          → 线状地物 road（sub = wall / road），长城的废弃年记 gone
  水系里的运河            → 运河 canal
  秦郡（jun）、秦郡界 j   → 原样保留，统一模板另画（有数据就画）
  灭国 falls              → 年表另收

疆域、注记点、归属点都不动：页面上的疆域与 engine.json 逐字相同，只是换一种写法交给模板。
"""
import legacy

MAJOR_RANGE = {"太行山", "南山", "燕山", "五岭", "大别山", "大巴山", "阴山"}      # 战国式模板里小比例尺也标名的山
MAJOR_RIVER = {"河", "江", "淮水", "济水", "汉水", "渭水"}


def parse_tl(s):
    out = []
    for part in s.split(";"):
        y, k = part.split(":", 1)
        out.append((int(y), k or None))
    return out


def owner_at(tl, y):
    o = None
    for y0, k in tl:
        if y >= y0:
            o = k
    return o


def en_of(it, fields=("old", "mod", "note", "yt", "sides", "cmd", "zhi")):
    e = {f: it["e" + f] for f in fields if it.get("e" + f)}
    return e


def era_engine(slug):
    import tomllib
    from pathlib import Path
    p = Path(__file__).resolve().parents[2] / "eras" / slug / "era.toml"
    return tomllib.loads(p.read_text(encoding="utf8")).get("engine", {})


def layered(b):
    """v1（战国式两卷）→ (GEO, DATA, 疆域色, 深链接标识, 旧链接别名)，写法同唐宋系旧格式"""
    G0, D0, _ = legacy.from_v1(b)
    keys = list(D0["states"])
    ix = {k: i for i, k in enumerate(keys)}
    st_items = {it["k"]: it for it in D0["items"] if it["c"] == "state"}
    kinds = D0.get("kinds", {})

    # 单位：诸侯国与戎狄部族
    units, colors = [], []
    for p in b["polities"]:
        k = p["key"]
        si = st_items[k]
        u = {"k": k, "n": si["old"], "kind": kinds.get(k, "state"), "note": si.get("note", ""), "mod": si.get("mod", "")}
        if si.get("eold"):
            u["ne"] = si["eold"]
            short = si["eold"].split(" (")[0]
            if short != si["eold"]:
                u["se"] = short
        if si.get("enote"):
            u["notee"] = si["enote"]
        if si.get("emod"):
            u["mode"] = si["emod"]
        units.append(u)
        colors.append(p["color"])

    # 州府：名城要邑（z）与一般城邑（c）
    seeds, seed_tl, seed_of = [], [], {}
    for it in D0["items"]:
        if it["c"] not in ("city", "town"):
            continue
        s = {"id": it["old"], "n": it["old"], "mod": it.get("mod", ""), "lon": it["lon"], "lat": it["lat"],
             "t": "z" if it["c"] == "city" else "t"}
        if it.get("note"):
            s["note"] = it["note"]
        if it.get("eold"):
            s["ne"] = it["eold"]
        if it.get("emod"):
            s["mode"] = it["emod"]
        if it.get("enote"):
            s["notee"] = it["enote"]
        seed_of[it["i"]] = len(seeds)
        seeds.append(s)
        seed_tl.append(parse_tl(it["tl"]) if it.get("tl") else [])

    # 条目：其余各类，重新编号
    items, new_i = [], {}
    for it in D0["items"]:
        if it["c"] in ("state", "city", "town"):
            continue
        new_i[it["i"]] = len(items)
        items.append(it)
    out = []
    for n, it in enumerate(items):
        c = it["c"]
        o = {"c": c, "old": it["old"], "mod": it.get("mod", ""), "note": it.get("note", ""), "i": n}
        e = en_of(it)
        if e:
            o["e"] = e
        for f in ("lon", "lat", "anc", "geo", "sub", "rx", "ry", "yt", "sides", "cmd", "k", "zhi", "alias"):
            if f in it:
                o[f] = it[f]
        if c == "capital":
            o["st"] = ix[it["st"]]
            o["yrs"] = [[it["y0"], it["y1"]]]
            # 都城不挂州府点（at）：两卷的国都与城邑条目本来分开，旧都照画旧都小框（规范第五节「春秋、战国都画小框」）
        elif c in ("battle", "culture"):
            o["y"] = it["y"]
            if c == "culture":
                o["c"] = "event"
        elif c == "people":
            o["y0"], o["y1"] = it["y0"], it["y1"]
        elif c == "jun":
            o["y0"] = it["y0"]
            o["tl"] = parse_tl(it["tl"]) if it.get("tl") else []
        elif c in ("wall", "road"):
            o["c"] = "road"
            o["sub"] = c
            o["y"] = it["y"]
            if "y1" in it:
                o["gone"] = it["y1"]           # 废弃之年：此后淡显（秦统一后的内地长城）
            if c == "road" and o["geo"] and not isinstance(o["geo"][0][0], list):
                o["geo"] = [o["geo"]]
        elif c == "river":
            if it.get("sub") == "canal":
                o["c"] = "canal"
                if "y" in it:
                    o["y0"] = it["y"]
            if it["old"] in MAJOR_RIVER:
                o["major"] = True
        elif c == "range":
            if it["old"] in MAJOR_RANGE:
                o["major"] = True
        out.append(o)

    # 底图：河流、湖泊、运河的条目号随之改
    G = {}
    for k in ("land", "prov", "rivers", "lakes", "canals"):
        G[k] = G0[k]
    for k in ("rivers", "lakes", "canals"):
        G[k] = [dict(r, it=new_i[r["it"]]) if r.get("it") is not None else r for r in G[k]]
    G["border"], G["deserts"] = [], []
    G["first"] = G0["first"]

    # 节点
    snaps = []
    for n, s0 in zip(b["nodes"], G0["snaps"]):
        y = s0["y"]
        idx = lambda d: {str(ix[k]): v for k, v in d.items()}
        lz = {str(ix[k]): [[lo, la, a * 0.0025, r] for lo, la, a, r in v] for k, v in s0["l"].items()}   # 面积：0.05° 格数 → 平方度
        pol = {u: int(p) for u, p in n["pol"].items()}
        sn = {"y": y, "t": s0["t"], "d": s0["d"], "te": s0["te"], "de": s0["de"], "era": "", "erae": "",
              "z": idx(s0["s"]), "lz": lz, "p": {}, "lp": {}, "pol": pol, "seat": {},
              "own": [ix.get(owner_at(tl, y), -1) if owner_at(tl, y) is not None else -1 for tl in seed_tl],
              "lab": idx(s0.get("lab", {})), "labe": idx(s0.get("labe", {}))}
        if "周" in ix and str(ix["周"]) not in sn["lab"] and units[ix["周"]]["n"] != "周":
            sn["lab"][str(ix["周"])] = "周"           # 王畿在图上只标「周」（战国式页面的写法）
        multi = {p for u, p in pol.items() if int(u) != p}
        for p in multi:                                   # 奉周的诸侯并入「周」：周天下外缘就是政权「周」的疆域
            sp = str(p)
            if sp in n["pu"]:
                sn["p"][sp] = b["geom"][n["pu"][sp]]
                if sp in n.get("pul", {}):
                    sn["lp"][sp] = n["pul"][sp]
        sn["h"] = sorted(int(u) for u, p in pol.items() if int(u) != p)
        if s0.get("j"):
            sn["j"] = s0["j"]
        snaps.append(sn)
    G["snaps"] = snaps
    # 秦郡：郡治在秦（及卫）境内、已置郡的节点（era.toml [engine] sub.hosts，同统一引擎细分秦郡的规则）
    hosts = set(eng.get("sub", {}).get("hosts", [])) if (eng := era_engine(b["era"])) else set()
    for o in out:
        if o["c"] == "jun":
            o["live"] = [j for j, sn in enumerate(snaps) if o["y0"] <= sn["y"] and owner_at(o["tl"], sn["y"]) in hosts]
    for o in out:
        o.pop("tl", None)

    D = {"units": units, "seeds": seeds, "items": out}
    for k in ("falls", "alleg", "p0"):
        if k in D0:
            D[k] = D0[k]
    if "falls" in D:
        D["falls"] = [dict(f, u=ix[f["k"]]) if f.get("k") in ix else f for f in D["falls"]]

    # 深链接：政权、地点用全局 ID，条目用「类别:全局 ID 或古名」；战国式旧链接（city: / town: / culture: / place:）另作别名
    first = lambda g: g[0][1] if isinstance(g, list) else g
    u_tok = ["polity:" + p["gid"] for p in b["polities"]]
    s_tok, alias = [], {}
    for it in D0["items"]:
        if it["i"] in seed_of:
            g = first(it.get("gid")) or it["old"]
            s_tok.append("place:" + g)
            alias.setdefault(f"{it['c']}:{g}", "s:" + str(seed_of[it['i']]))
    from collections import Counter, defaultdict
    base = []
    for it, o in zip(items, out):
        g = first(it.get("gid"))
        base.append(g if g and ":" in g else f"{o['c']}:{g or it['old']}")
    cnt, seen, i_tok = Counter(base), defaultdict(int), []
    for it, o, t in zip(items, out, base):
        if cnt[t] > 1:
            yv = it.get("y", it.get("y0"))
            t = t + "@" + (b["polities"][o["st"]]["gid"] if o["c"] == "capital" else str(yv) if yv is not None else "")
        seen[t] += 1
        t = t if seen[t] == 1 else f"{t}.{seen[t]}"
        i_tok.append(t)
        if it["c"] != o["c"] and t.startswith(o["c"] + ":"):
            alias.setdefault(it["c"] + t[len(o["c"]):], "i:" + str(o["i"]))
    for it, o in zip(items, out):                       # 战国式页面里都城、关隘条目也认 place:<全局 ID>
        g = first(it.get("gid"))
        if g and ":" not in g and it["c"] in ("capital", "pass"):
            alias.setdefault("place:" + g, "i:" + str(o["i"]))
    # 战国式页面的条目标识（原由 assemble.py tokens 生成）与此写法相同：同名条目加 @所属政权的全局 ID（都城）或 @年份；
    # 只有城邑改成了地点、事件改了类别名，上面已补别名
    return G, D, colors, {"u": u_tok, "s": s_tok, "i": i_tok}, alias
