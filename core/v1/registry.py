# -*- coding: utf-8 -*-
"""全局表：把各卷里的地点、政权、山川归并成跨卷的同一个对象，给出全局 ID（规范第十九节第 2 步）。

  python core/v1/registry.py        重建 global/ 下的各表与 global/review/ 下的审定清单

迁移期间各卷的史料仍是各卷自己的源文件，全局表由本脚本从各卷成品归并而来；
人工判断（哪些该合、哪些该拆、ID 叫什么）写在 global/decisions.toml，重建时照办。
各卷改为直接引用全局 ID 之后，全局表本身就成为源文件。
"""
import collections
import json
import math
import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:                       # Python 3.10 及以下：pip install tomli
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legacy

ROOT = Path(__file__).resolve().parents[2]
GLOBAL = ROOT / "global"
REVIEW = GLOBAL / "review"
ERAS = ["chunqiu", "zhanguo", "qinhan", "hanmosanguo", "liangjin-nanbeichao", "suitang", "tangsong", "songyuan", "minguo-xinzhongguo"]
ERA_ZH = {"chunqiu": "春秋", "zhanguo": "战国", "qinhan": "秦汉", "hanmosanguo": "汉末", "liangjin-nanbeichao": "两晋",
          "suitang": "隋唐", "tangsong": "唐宋", "songyuan": "宋元", "minguo-xinzhongguo": "民国"}


def load_bundles():
    import engine_geom
    out = {}
    for slug in ERAS:
        html = (ROOT / "eras" / slug / "legacy.html").read_text(encoding="utf8")
        out[slug] = legacy.to_v1(slug, *legacy.extract(html))
        engine_geom.apply(slug, out[slug], strict=False, log=lambda *a: None)    # 疆域已换到统一引擎的卷（第 7 步）
    return out


def load_toml(p):
    if tomllib is None:
        sys.exit(f"读 {p.name} 需要 Python 3.11 以上，或先 pip install tomli")
    return tomllib.loads(Path(p).read_text(encoding="utf8"))


def load_decisions():
    p = GLOBAL / "decisions.toml"
    return load_toml(p) if p.exists() else {}


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[1], a[0], b[1], b[0]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(min(1, math.sqrt(h)))


def tokens(name):
    """「长安（大兴城）」→ {长安（大兴城）, 长安, 大兴城}"""
    out = {name}
    for part in re.split(r"[（）()、，,/·]", name):
        part = part.strip()
        if part:
            out.add(part)
    return out


class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def mod_same(a, b):
    a, b = (a or "").strip(), (b or "").strip()
    if not a or not b:
        return False
    if a == b:
        return True
    short, long_ = sorted((a, b), key=len)
    return len(short) >= 4 and short in long_


def dup_check(rows, what, sect):
    c = collections.Counter(r["id"] for r in rows)
    dups = [k for k, v in c.items() if v > 1]
    if dups:
        sys.exit(f"{what}全局 ID 重复：{'、'.join(dups)}。检查 global/decisions.toml 的 [{sect}.id]，"
                 f"把原来占着这个名字的一组也改个 ID。")


# ---------------------------------------------------------------- 地点

def place_candidates(B):
    cands = []
    for slug in ERAS:
        b = B[slug]
        seen_items = set()
        for p in b["places"]:
            names = {p["n"]} | {nm for _, nm in p.get("names", [])}
            if "jn" in p:
                names.add(p["jn"])
            en = p.get("en", {}).get("n")
            cands.append({"ref": f"{slug}:{p['key']}", "era": slug, "names": names, "mod": p.get("mod", ""),
                          "ll": (p["lon"], p["lat"]), "kind": p["kind"], "en": en, "main": p["n"]})
            if "item" in p:
                seen_items.add(p["item"])
        for it in b["items"]:
            if it["c"] in ("capital", "pass") and "lon" in it and it["i"] not in seen_items:
                cands.append({"ref": f"{slug}:i:{it['i']}", "era": slug, "names": {it["old"]}, "mod": it.get("mod", ""),
                              "ll": (it["lon"], it["lat"]), "kind": it["c"], "en": it.get("en", {}).get("old"),
                              "main": it["old"], "at": it.get("at")})
    for c in cands:
        c["tok"] = set().union(*(tokens(n) for n in c["names"]))
    return cands


def cluster_places(cands, dec):
    n = len(cands)
    uf = UF(n)
    split = set(dec.get("places", {}).get("split", [])) | manual_refs(dec)
    grid = collections.defaultdict(list)
    for i, c in enumerate(cands):
        grid[(int(c["ll"][0] // 0.5), int(c["ll"][1] // 0.5))].append(i)
    reason = {}
    for i, c in enumerate(cands):
        gx, gy = int(c["ll"][0] // 0.5), int(c["ll"][1] // 0.5)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in grid[(gx + dx, gy + dy)]:
                    if j <= i:
                        continue
                    d = cands[j]
                    if c["ref"] in split or d["ref"] in split:
                        continue
                    dist = km(c["ll"], d["ll"])
                    shared = c["tok"] & d["tok"]
                    if dist <= 1.0 and (c["era"] == d["era"] or shared or mod_same(c["mod"], d["mod"])):
                        uf.union(i, j)
                    elif dist <= 2.0 and (shared or mod_same(c["mod"], d["mod"])):
                        uf.union(i, j)
                    elif dist <= 30 and shared:
                        uf.union(i, j)
                        reason[(i, j)] = dist
    # 同一卷里，都城条目以 at 指向所在的州府
    by_ref = {c["ref"]: i for i, c in enumerate(cands)}
    for i, c in enumerate(cands):
        at = c.get("at")
        if isinstance(at, int):
            slug = c["era"]
            j = by_ref.get(f"{slug}:{PLACE_KEYS[slug][at]}") if at < len(PLACE_KEYS[slug]) else None
            if j is not None and km(c["ll"], cands[j]["ll"]) <= 5 and c["ref"] not in split and cands[j]["ref"] not in split:
                uf.union(i, j)
    # 人工决定：合并（拆出的在上面已经不参与自动归并）
    for group in dec.get("places", {}).get("merge", []):
        idx = [by_ref[r] for r in group if r in by_ref]
        for a in idx[1:]:
            uf.union(idx[0], a)
    groups = collections.defaultdict(list)
    for i in range(n):
        groups[uf.find(i)].append(i)
    return list(groups.values())


PLACE_KEYS = {}


def manual_refs(dec):
    """人工定组（[[place]] 的 refs、add）和治所迁城（[[seat]]）的条目：不参与自动归并"""
    out = set()
    for pl in dec.get("place", []):
        out |= set(pl.get("refs", [])) | set(pl.get("add", []))
    for st in dec.get("seat", []):
        out.add(st["ref"])
    return out


def era_years(slug):
    meta = load_toml(ROOT / "eras" / slug / "era.toml")
    return tuple(meta["years"])


def ref_years(B, ref):
    """一条引用在本卷里存在的年代（首尾年）。条目看它的年段或时点，州府看全卷"""
    slug, key = ref.split(":", 1)
    y0, y1 = era_years(slug)
    if key.startswith("i:"):
        it = next((x for x in B[slug]["items"] if x["i"] == int(key[2:])), None)
        if it:
            ts = []
            for a, b in it.get("spans", []):
                ts += [a, b]
            if "t" in it and it["t"] is not None and it["t"] > legacy.BEGIN:
                ts.append(it["t"])
            if it.get("t1") is not None:
                ts.append(it["t1"])
            ts = [t for t in ts if t > legacy.BEGIN]
            if ts:
                return max(y0, min(ts) // 12), min(y1, max(ts) // 12)
    return y0, y1


def site_for(sites, y0, y1):
    """与年代 [y0, y1] 有交集的城址"""
    out = []
    for st in sites:
        a, b = st.get("from", -99999), st.get("to", 99999)
        if a <= y1 and b >= y0:
            out.append(st)
    return out or sites


def build_places(B, dec):
    for slug in ERAS:
        PLACE_KEYS[slug] = [p["key"] for p in B[slug]["places"]]
    cands = place_candidates(B)
    groups = cluster_places(cands, dec)
    by_ref = {c["ref"]: i for i, c in enumerate(cands)}
    seat_refs = {st["ref"] for st in dec.get("seat", [])}
    decided = {}                          # 组的序号 → [[place]] 决定
    gi_of = {i: k for k, g in enumerate(groups) for i in g}
    groups = [list(g) for g in groups]
    for pl in dec.get("place", []):
        if "refs" in pl:
            members = [by_ref[r] for r in pl["refs"] if r in by_ref]
            missing = [r for r in pl["refs"] if r not in by_ref]
            if missing:
                sys.exit(f"[[place]] {pl['id']}：查不到 {'、'.join(missing)}")
            for i in members:             # 人工定组的成员各自是单独一组，挪到第一个成员那一组
                groups[gi_of[i]] = [x for x in groups[gi_of[i]] if x != i]
            k = gi_of[members[0]] if members else len(groups)
            if not members:
                groups.append([])
            groups[k] = members
        else:
            if pl["anchor"] not in by_ref:
                sys.exit(f"[[place]] {pl['id']}：查不到 anchor {pl['anchor']}")
            k = gi_of[by_ref[pl["anchor"]]]
            for r in pl.get("add", []):
                i = by_ref[r]
                groups[gi_of[i]] = [x for x in groups[gi_of[i]] if x != i]
                groups[k].append(i)
        decided[k] = pl
    for r in seat_refs:                   # 治所迁城的条目不单独成地点，按年代挂到别的地点上
        i = by_ref[r]
        groups[gi_of[i]] = [x for x in groups[gi_of[i]] if x != i]
    keep = [(k, g) for k, g in enumerate(groups) if g or k in decided]
    places, review = [], []
    names_used = collections.Counter()
    pre = []
    for k, g in keep:
        cs = [cands[i] for i in g]
        pl = decided.get(k)
        if pl and not cs:                 # 只有治所挂靠、没有本身条目的地点
            st = pl["sites"][-1]
            pre.append((g, cs, pl["id"], collections.Counter(), (st["lon"], st["lat"]), 0, 0, collections.Counter(), pl))
            names_used[pl["id"]] += 1
            continue
        cnt = collections.Counter(c["main"] for c in cs)
        tokc = collections.Counter(t for c in cs for t in c["tok"] if not re.search(r"[（(]", t))
        name = max(tokc, key=lambda t: (tokc[t], cnt.get(t, 0), -len(t), t))
        mods = collections.Counter(c["mod"] for c in cs if c["mod"])
        llc = collections.Counter(c["ll"] for c in cs)
        ll = llc.most_common(1)[0][0]
        spread = max(km(ll, c["ll"]) for c in cs)
        diam = max((km(a["ll"], b["ll"]) for a in cs for b in cs), default=0) if len(cs) < 60 else spread * 2
        ens = collections.Counter(c["en"] for c in cs if c["en"])
        if pl:
            name = pl["id"]
            if "sites" in pl:
                cur = [st for st in pl["sites"] if "to" not in st] or pl["sites"]
                ll = (cur[0]["lon"], cur[0]["lat"])
        pre.append((g, cs, name, mods, ll, spread, diam, ens, pl))
        names_used[name] += 1
    seen = collections.Counter()
    ids = set()
    pre.sort(key=lambda x: (-len(x[1]), x[2], x[4]))
    corrections = []
    for g, cs, name, mods, ll, spread, diam, ens, pl in pre:
        at_ll = collections.Counter(c["mod"] for c in cs if c["mod"] and c["ll"] == ll)
        mod = (at_ll or mods).most_common(1)[0][0] if mods else ""
        if pl and pl.get("mod"):
            mod = pl["mod"]
        pid = name
        if names_used[name] > 1 and not pl:
            seen[name] += 1
            if seen[name] > 1 or any(x[8] and x[8]["id"] == name for x in pre):  # 同名的第一处（引用最多的）用本名，其余加今地
                pid = f"{name}（{mod or f'{ll[0]:.2f},{ll[1]:.2f}'}）"
        k = 2
        base = pid
        while pid in ids:
            pid, k = f"{base}#{k}", k + 1
        ids.add(pid)
        for ref, newid in dec.get("places", {}).get("id", {}).items():
            if ref in {c["ref"] for c in cs}:
                pid = newid
        sites = []
        if pl and "sites" in pl:
            sites = [dict(st) for st in pl["sites"]]
            for c in cs:                      # 各条坐标与它那个年代的城址不符的，记入改正清单
                y0, y1 = ref_years(B, c["ref"])
                ok = [st for st in site_for(sites, y0, y1) if km(c["ll"], (st["lon"], st["lat"])) <= 2.0]
                if not ok:
                    st = min(site_for(sites, y0, y1), key=lambda st: km(c["ll"], (st["lon"], st["lat"])))
                    corrections.append((pid, c, y0, y1, st))
        elif spread > 2:
            by_site = collections.defaultdict(set)
            for c in cs:
                by_site[c["ll"]].add(c["era"])
            sites = [{"lon": s[0], "lat": s[1], "eras": sorted(e, key=ERAS.index)} for s, e in sorted(by_site.items())]
        rec = {"id": pid, "n": name, "names": sorted({t for c in cs for t in c["names"]}),
               "mod": mod, "lon": ll[0], "lat": ll[1], "eras": sorted({c["era"] for c in cs}, key=ERAS.index),
               "refs": sorted(c["ref"] for c in cs)}
        if ens:
            rec["en"] = ens.most_common(1)[0][0]
        if len(ens) > 1:
            rec["en_variants"] = sorted(ens)
        if sites:
            rec["sites"] = sites
        if pl and pl.get("note"):
            rec["note"] = pl["note"]
        places.append(rec)
        if not pl and (spread > 5 or diam > 40):
            review.append((pid, cs, spread, diam, mods))
    # 治所迁城：同一条在不同年代挂到不同的地点
    by_id = {r["id"]: r for r in places}
    for st in dec.get("seat", []):
        c = cands[by_ref[st["ref"]]]
        y0, y1 = era_years(c["era"])
        steps = st["by"]
        for n, (y, pid) in enumerate(steps):
            a = y0 if n == 0 else max(y0, y)
            b = y1 if n == len(steps) - 1 else min(y1, steps[n + 1][0] - 1)
            if a > b:
                continue
            if pid not in by_id:
                sys.exit(f"[[seat]] {st['ref']}：没有地点 {pid}")
            rec = by_id[pid]
            rec.setdefault("seats", []).append({"ref": st["ref"], "from": a, "to": b})
            if st["ref"].split(":")[0] not in rec["eras"]:
                rec["eras"] = sorted(set(rec["eras"]) | {c["era"]}, key=ERAS.index)
            rec["names"] = sorted(set(rec["names"]) | c["names"])
            sites = rec.get("sites") or [{"lon": rec["lon"], "lat": rec["lat"]}]
            if not any(km(c["ll"], (x["lon"], x["lat"])) <= 2.0 for x in site_for(sites, a, b)):
                x = min(site_for(sites, a, b), key=lambda x: km(c["ll"], (x["lon"], x["lat"])))
                corrections.append((pid, c, a, b, x))
    dup_check(places, "地点", "places")
    places.sort(key=lambda r: (r["lon"], r["lat"], r["id"]))
    return places, review, cands, corrections


# ---------------------------------------------------------------- 政权

def active_range(b, key):
    ts = [n["t"] for n in b["nodes"] if key in n.get("u", {}) or key in n.get("pu", {})]
    return (min(ts), max(ts)) if ts else None


def build_polities(B, dec):
    cands = []
    for slug in ERAS:
        b = B[slug]
        t0, t1 = b["nodes"][0]["t"], b["nodes"][-1]["t"]
        for p in b["polities"]:
            key = p["key"]
            # 分层模型的节点里，单位以序号出现
            if b["model"] == "layered":
                idx = str(b["polities"].index(p))
                ts = [n["t"] for n in b["nodes"] if idx in n.get("u", {}) or idx in n.get("pu", {})]
                rng = (min(ts), max(ts)) if ts else None
                nn = len(ts)
                parent = next((b["polities"][int(n["pol"][idx])]["n"] for n in b["nodes"]
                               if str(n.get("pol", {}).get(idx, idx)) != idx), None)
            else:
                rng = active_range(b, key)
                nn = sum(1 for n in b["nodes"] if key in n.get("u", {}))
                parent = None
            cands.append({"ref": f"{slug}:{key}", "era": slug, "key": key, "n": p["n"], "en": p.get("en", {}).get("n"),
                          "kind": p["kind"], "color": p["color"], "rng": rng, "edge": (t0, t1), "nn": nn, "parent": parent})
    uf = UF(len(cands))
    by_name = collections.defaultdict(list)
    for i, c in enumerate(cands):
        by_name[c["n"]].append(i)
        if c["key"] != c["n"]:
            by_name[c["key"]].append(i)
    flagged = []
    order = {s: k for k, s in enumerate(ERAS)}
    for name, idx in by_name.items():
        idx = sorted(set(idx), key=lambda i: (order[cands[i]["era"]], i))
        for a_i, a in enumerate(idx):
            for b_ in idx[a_i + 1:]:
                A, Bc = cands[a], cands[b_]
                if A["era"] == Bc["era"] or not A["rng"] or not Bc["rng"]:
                    continue
                first, second = (A, Bc) if A["rng"][0] <= Bc["rng"][0] else (Bc, A)
                gap = (second["rng"][0] - first["rng"][1]) / 12
                bridge = (first["rng"][1] == first["edge"][1] and second["rng"][0] == second["edge"][0]
                          and abs(order[second["era"]] - order[first["era"]]) == 1)
                if gap <= 60 or bridge:
                    uf.union(a, b_)
                elif first["en"] and first["en"] == second["en"] and first["kind"] == second["kind"] == "state":
                    flagged.append((first, second, gap))
    for group in dec.get("polities", {}).get("merge", []):
        ids = [i for i, c in enumerate(cands) if c["ref"] in group]
        for a in ids[1:]:
            uf.union(ids[0], a)
    flagged = [(a, b_, gap) for a, b_, gap in flagged
               if uf.find(cands.index(a)) != uf.find(cands.index(b_))]
    groups = collections.defaultdict(list)
    for i in range(len(cands)):
        groups[uf.find(i)].append(i)
    names = collections.Counter()
    pre = []
    for g in groups.values():
        cs = sorted((cands[i] for i in g), key=lambda c: order[c["era"]])
        w = collections.Counter()
        for c in cs:                      # 各卷叫法不同时，取出现节点最多的一卷的叫法
            w[c["n"]] += c["nn"] + 0.001
        name = max(w, key=lambda k: (w[k], k))
        names[name] += 1
        pre.append((cs, name))
    pre.sort(key=lambda x: (-sum(c["nn"] for c in x[0]), order[x[0][0]["era"]], x[1]))
    seen, out, colors_review, en_review = collections.Counter(), [], [], []
    pal = load_toml(GLOBAL / "palette.toml")
    wude, pcol = pal.get("wude", {}), pal.get("color", {})
    for g, de in wude.get("gid", {}).items():
        if pcol.get(g, [None])[0] != wude.get(de):
            sys.exit(f"global/palette.toml：{g} 定为{de}，[color] 里却是 {pcol.get(g)}")
    for cs, name in pre:
        pid = name
        if names[name] > 1:
            seen[name] += 1
            par = cs[0].get("parent")
            if cs[0]["kind"] == "zhen" and par:   # 同名的二级单位（宋、金都有河北东路）一律注所属政权
                pid = f"{name}（{par}）"
            elif seen[name] > 1:                  # 其余同名的，第一个用本名，后面的加首见卷
                pid = f"{name}·{ERA_ZH[cs[0]['era']]}"
        for ref, newid in dec.get("polities", {}).get("id", {}).items():
            if ref in {c["ref"] for c in cs}:
                pid = newid
        ens = collections.Counter(c["en"] for c in cs if c["en"])
        rec = {"id": pid, "n": name, "kind": cs[-1]["kind"],     # 部族升为政权的（契丹→辽），以最后一卷为准
               "eras": [c["era"] for c in cs], "refs": [c["ref"] for c in cs],
               "colors": {c["era"]: pcol.get(pid, c["color"]) for c in cs}}
        if ens:
            rec["en"] = ens.most_common(1)[0][0]
        if len({c["n"] for c in cs}) > 1:
            rec["names"] = sorted({c["n"] for c in cs})
        if len({c["kind"] for c in cs}) > 1:
            rec["kinds"] = {c["era"]: c["kind"] for c in cs}
        out.append(rec)
        if len({tuple(v) for v in rec["colors"].values()}) > 1:
            colors_review.append((pid, cs))
        if len(ens) > 1:
            en_review.append((pid, cs))
    dup_check(out, "政权", "polities")
    stale = sorted(set(pcol) - {r["id"] for r in out})
    if stale:
        sys.exit(f"global/palette.toml 里这些全局 ID 已不存在：{'、'.join(stale)}")
    out.sort(key=lambda r: (ERAS.index(r["eras"][0]), r["id"]))
    return out, flagged, colors_review, en_review, cands


# ---------------------------------------------------------------- 山川

PHYS = ("range", "river", "canal", "desert", "wall", "road")
FEATURE_END = ("河", "江", "湖", "水", "山", "岭", "泽", "渠", "漠", "脉", "海", "错", "泊", "峡", "原", "地", "城", "道",
               "路", "川", "溪", "池", "淀", "湾", "塘", "陂", "堰", "沟", "峰", "峪", "坂", "谷", "运河", "沙漠")


def clean_mod(m):
    """今名是不是一个干净的地物名（不是「已湮」「河南荥阳东北」这类说明）"""
    m = (m or "").strip()
    return bool(re.fullmatch(r"[\u4e00-\u9fff·]{2,10}", m)) and m.endswith(FEATURE_END) \
        and not re.search(r"已|约|今|一带|境内?$|^(河北|河南|山东|山西|陕西|江苏|浙江|安徽|江西|湖北|湖南|四川|甘肃|广东|广西|福建|云南|贵州)", m)


def head(name):
    return re.split(r"[（(]", name)[0].strip() or name


def build_physical(B, dec):
    pdec = dec.get("physical", {})
    split = set(pdec.get("split", []))
    cands = []
    for slug in ERAS:
        for it in B[slug]["items"]:
            if it["c"] in PHYS:
                key = (it.get("mod") or "").strip() or it["old"]
                cands.append({"ref": f"{slug}:i:{it['i']}", "era": slug, "c": it["c"], "old": it["old"], "mod": it.get("mod", ""),
                              "geo": it.get("geo"), "anc": it.get("anc") or ([it["lon"], it["lat"]] if "lon" in it else None),
                              "en": it.get("en", {}).get("old"), "sub": it.get("sub"),
                              "t": it.get("t"), "t1": it.get("t1"),
                              "tok": tokens(it["old"]) | ({it["mod"]} if it.get("mod") else set())})
    uf = UF(len(cands))
    by_geo = collections.defaultdict(list)
    for i, c in enumerate(cands):
        if c["geo"]:
            by_geo[json.dumps(c["geo"])].append(i)
    for idx in by_geo.values():
        for a in idx[1:]:
            uf.union(idx[0], a)
    for i, c in enumerate(cands):
        for j in range(i + 1, len(cands)):
            d = cands[j]
            if c["c"] != d["c"] or c["era"] == d["era"]:
                continue
            if (c["ref"] in split) != (d["ref"] in split):   # 人工拆出的，只与同样拆出的、几何相同的合并
                continue
            if not (c["tok"] & d["tok"]) and not (clean_mod(c["mod"]) and c["mod"].strip() == d["mod"].strip()):
                continue
            if c["anc"] and d["anc"] and km(c["anc"], d["anc"]) <= (400 if c["c"] in ("river", "range") else 150):
                uf.union(i, j)
            elif (clean_mod(c["mod"]) and c["mod"].strip() == d["mod"].strip() and c["anc"] and d["anc"]
                  and km(c["anc"], d["anc"]) <= 1500):  # 长江、黄河这样的长河，各卷锚点可以相距很远
                uf.union(i, j)
    groups = collections.defaultdict(list)
    for i in range(len(cands)):
        groups[uf.find(i)].append(i)
    out, review, ids = [], [], set()
    for g in groups.values():
        cs = sorted((cands[i] for i in g), key=lambda c: ERAS.index(c["era"]))
        # ID 用今名（各卷通用、最好认）；今名不是干净的地物名时，用古名括号前的部分。次数相同取较晚一卷的
        mods = [c["mod"].strip() for c in cs if clean_mod(c["mod"])]
        pool_ = mods or [head(c["old"]) for c in cs]
        cnt = collections.Counter(pool_)
        name = max(cnt, key=lambda k: (cnt[k], pool_[::-1].index(k) * -1, k))
        pid = f"{cs[0]['c']}:{name}"
        if pid in ids:                    # 重名：先用带括注的今名（汉江（朝鲜半岛）），再用别的古名，最后用卷名
            full = next((c["mod"].strip() for c in cs if c["mod"].strip().startswith(name + "（")), "")
            alt = next((head(c["old"]) for c in cs if head(c["old"]) != name), "")
            pid = f"{cs[0]['c']}:{full}" if full else f"{cs[0]['c']}:{name}（{alt or ERA_ZH[cs[0]['era']]}）"
        k = 2
        base = pid
        while pid in ids:
            pid, k = f"{base}#{k}", k + 1
        for ref, newid in pdec.get("id", {}).items():   # 钉住已发布的 ID
            if ref in {c["ref"] for c in cs}:
                pid = newid
        ids.add(pid)
        geos ={json.dumps(c["geo"]) for c in cs if c["geo"]}
        rec = {"id": pid, "c": cs[0]["c"], "n": name, "names": sorted({c["old"] for c in cs}),
               "mod": collections.Counter(c["mod"] for c in cs if c["mod"]).most_common(1)[0][0] if any(c["mod"] for c in cs) else "",
               "eras": sorted({c["era"] for c in cs}, key=ERAS.index), "refs": [c["ref"] for c in cs]}
        ens = collections.Counter(c["en"] for c in cs if c["en"])
        if ens:
            rec["en"] = ens.most_common(1)[0][0]
        if len(ens) > 1:
            rec["en_variants"] = sorted(ens)
        times = {c["era"]: [c["t"], c["t1"]] for c in cs if c["t"] is not None}
        if times:                         # 运河开凿、长城修筑等：各卷所记起止（月序号，t1 为空表示一直存在）
            rec["time"] = times
        if len(geos) > 1:
            rec["geo_variants"] = len(geos)
            pts = [json.loads(gj) for gj in geos]
            dev = max(max(min(km(p, q) for q in other) for p in one) for one in pts for other in pts if one is not other)
            rec["geo_dev_km"] = round(dev)
            pref = next((v for k2, v in pdec.get("prefer", {}).items() if k2 == pid), None)
            if pref:
                rec["geo_from"] = pref["era"]
                if pref.get("note"):
                    rec["note"] = pref["note"]
            elif dev > 30:
                review.append((pid, cs, dev))
        out.append(rec)
    out.sort(key=lambda r: (r["c"], r["id"]))
    return out, review, cands


# ---------------------------------------------------------------- 衔接

JUNCTIONS = [("chunqiu", "zhanguo"), ("zhanguo", "qinhan"), ("qinhan", "hanmosanguo"), ("hanmosanguo", "liangjin-nanbeichao"),
             ("liangjin-nanbeichao", "suitang"), ("tangsong", "songyuan")]


def shape_of(b, g):
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    from shapely.validation import make_valid
    rings = b["geom"][g] if isinstance(g, int) else g
    polys = []
    for flat in rings:
        x = y = 0
        pts = []
        for i in range(0, len(flat), 2):
            x += flat[i]
            y += flat[i + 1]
            pts.append((x / 100, y / 100))
        if len(pts) >= 3:
            polys.append(make_valid(Polygon(pts)))
    out = None
    for q in polys:                        # 奇偶填充：重叠处挖空
        out = q if out is None else out.symmetric_difference(q)
    return out


def node_shapes(b, node):
    """节点上各政权（顶层）的疆域：有政权层几何（pu）用它，否则把归属该政权的各单位合起来。"""
    from shapely.ops import unary_union
    pol = node.get("pol", {})
    parts = collections.defaultdict(list)
    for k, g in node.get("u", {}).items():
        top = str(pol.get(k, k))
        parts[top].append(shape_of(b, g))
    out = {}
    for top, shs in parts.items():
        out[top] = unary_union([x for x in shs if x is not None and not x.is_empty])
    for k, g in node.get("pu", {}).items():
        out[k] = shape_of(b, g)
    if b["model"] == "layered":
        out = {b["polities"][int(k)]["key"]: v for k, v in out.items()}
    return out


def build_junctions(B, polities):
    ref2id = {r: p["id"] for p in polities for r in p["refs"]}
    rows, report = [], []
    for a, z in JUNCTIONS:
        na, nz = B[a]["nodes"][-1], B[z]["nodes"][0]
        sa, sz = node_shapes(B[a], na), node_shapes(B[z], nz)
        ia = {ref2id[f"{a}:{k}"]: v for k, v in sa.items()}
        iz = {ref2id[f"{z}:{k}"]: v for k, v in sz.items()}
        common = sorted(set(ia) & set(iz))
        # 只比两卷都画到的范围：一卷图幅截掉的边角（如唐宋卷东到 136°E，宋元卷画到日本全境）不算画法不一致
        from shapely.ops import unary_union
        drawn = lambda d: unary_union([v for v in d.values() if v is not None and not v.is_empty])
        both = drawn(sa).intersection(drawn(sz))
        ious = []
        for pid in common:
            A, Z = ia[pid], iz[pid]
            if A is None or Z is None or A.is_empty or Z.is_empty:
                continue
            A2, Z2 = A.intersection(both), Z.intersection(both)
            u = A2.union(Z2).area
            ious.append((pid, A2.intersection(Z2).area / u if u else 1.0, A.area, Z.area))
        # 只在一边出现的政权，两两比对疆域：重合度高的多半是同一政权在两卷里名字不同
        id2ref = {}
        for k in sa:
            id2ref[ref2id[f"{a}:{k}"]] = f"{a}:{k}"
        for k in sz:
            id2ref[ref2id[f"{z}:{k}"]] = f"{z}:{k}"
        rename = []
        for pa in sorted(set(ia) - set(iz)):
            for pz in sorted(set(iz) - set(ia)):
                A, Z = ia[pa], iz[pz]
                if A is None or Z is None or A.is_empty or Z.is_empty or not A.intersects(Z):
                    continue
                inter = A.intersection(Z).area
                iou = inter / A.union(Z).area
                cover = inter / min(A.area, Z.area)       # 小的一方有多少落在大的一方里
                if iou >= 0.25 or cover >= 0.6:
                    rename.append((pa, pz, iou, cover, A.area, Z.area, id2ref[pa], id2ref[pz]))
        rows.append({"from": a, "to": z, "t_from": na["t"], "t_to": nz["t"], "same_time": na["t"] // 12 == nz["t"] // 12, "rename": rename,
                     "only_from": sorted(set(ia) - set(iz)), "only_to": sorted(set(iz) - set(ia)), "ious": ious})
    return rows


# ---------------------------------------------------------------- 输出

def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "\\|").replace("\n", " ") for x in r) + " |")
    return "\n".join(out)


def main():
    B = load_bundles()
    dec = load_decisions()
    places, p_review, cands, p_fix = build_places(B, dec)
    polities, flagged, colors_review, en_review, po_cands = build_polities(B, dec)
    physical, phys_review, ph_cands = build_physical(B, dec)
    write_jsonl(GLOBAL / "places.jsonl", places)
    write_jsonl(GLOBAL / "polities.jsonl", polities)
    write_jsonl(GLOBAL / "physical.jsonl", physical)
    REVIEW.mkdir(parents=True, exist_ok=True)

    # 地点审定清单
    rows = []
    for pid, cs, spread, diam, mods in sorted(p_review, key=lambda x: -x[3]):
        detail = "；".join(f"{ERA_ZH[c['era']]} {c['main']} {c['ll'][0]:.2f},{c['ll'][1]:.2f}（{c['mod']}）`{c['ref']}`"
                          for c in sorted(cs, key=lambda c: (ERAS.index(c["era"]), c["ref"])))
        kind = "范围过大，可能误合" if diam > 40 else "城址相距超过 5 km"
        rows.append((pid, kind, f"{diam:.0f}", detail))
    (REVIEW / "places.md").write_text(
        "# 地点审定清单\n\n自动归并后仍需人工判断的地点。每行列出各卷的写法、坐标与今地。\n\n"
        "- 城址相距超过 5 km：同一地点在不同卷里坐标不同。可能是城址确有迁移（如汉长安城与隋唐长安城），也可能是某卷坐标取点不同。\n"
        "- 范围过大：归并后最远两点超过 40 km，可能把同名的两处误合在一起，需要拆开。\n\n"
        "决定写进 `global/decisions.toml`（`[[place]]` 定组、城址与 ID，`[[seat]]` 治所迁城），再运行 `python core/v1/registry.py` 重建。"
        "已经写进 `[[place]]` 的地点不再列在这里。\n\n"
        + md_table(["全局 ID", "问题", "最远距离 km", "各卷写法"], rows) + "\n", encoding="utf8")

    rows = []
    for pid, cs in colors_review:
        rows.append((pid, "；".join(f"{ERA_ZH[c['era']]} {c['n']} {c['color'][0]}" for c in cs)))
    rows2 = [(f"{a['n']}（{ERA_ZH[a['era']]}）↔ {b['n']}（{ERA_ZH[b['era']]}）", a["en"], f"{gap:.0f}") for a, b, gap in flagged]
    rows3 = [(pid, "；".join(f"{ERA_ZH[c['era']]} {c['en']}" for c in cs)) for pid, cs in en_review]
    (REVIEW / "polities.md").write_text(
        "# 政权审定清单\n\n## 同一政权、各卷配色不同\n\n同一政权跨卷同色，由 `global/palette.toml` 统一（规范第三节）；下面列的是套用全局配色后仍然不同的，应为空。\n\n"
        + md_table(["全局 ID", "各卷名称与浅色"], rows)
        + "\n\n## 同名、同英文名，但时间不连续，未合并\n\n按规则当作不同政权（前后两段相隔超过 60 年，又不是隔着空档首尾相接）。若其实是同一政权，写进 `[polities] merge`。\n\n"
        + md_table(["两处", "英文名", "相隔年数"], rows2)
        + "\n\n## 同一政权、各卷英文名不同\n\n" + md_table(["全局 ID", "各卷英文名"], rows3) + "\n", encoding="utf8")

    rows = []
    for pid, cs, dev in sorted(phys_review, key=lambda x: -x[2]):
        rows.append((pid, f"{dev:.0f}", "；".join(f"{ERA_ZH[c['era']]} {c['old']}" for c in cs)))
    (REVIEW / "physical.md").write_text(
        "# 山川审定清单\n\n同一山脉、长城或道路在各卷里画法不同、最大偏差超过 30 km 的。第 4、5 步换成全局山川数据时，要定以哪一卷的画法为准，或重新勾画。\n\n"
        + md_table(["全局 ID", "最大偏差 km", "各卷名称"], rows) + "\n", encoding="utf8")

    # 译名：每个全局对象、每个中文写法一条。同一中文名各卷英文不同的：
    #   山川默认统一成用得最多的写法（次数相同取较晚一卷）；地点、政权要人工定（统一，或按时代各用各的）
    gdec = dec.get("glossary", {})
    by_era, unify = set(gdec.get("by_era", [])), gdec.get("unify", {})
    ref2c = {c["ref"]: c for c in cands}
    po2c = {c["ref"]: c for c in po_cands}
    ph2c = {c["ref"]: c for c in ph_cands}
    gl_rows, glossary, en_fix = [], [], []

    def gloss(kind, rid, members, auto):
        by = collections.defaultdict(list)
        for zh, en, era in members:
            if en:
                by[zh].append((en, era))
        for zh, st in by.items():
            st = sorted(set(st), key=lambda x: (ERAS.index(x[1]), x[0]))
            ens = collections.Counter(e for e, _ in st)
            eras_of = lambda e: [ERA_ZH[a] for a in ERAS if (e, a) in set(st)]
            row = {"id": rid, "kind": kind, "zh": zh}
            key = f"{rid}|{zh}"
            if len(ens) == 1:
                row["en"] = st[0][0]
            elif key in by_era:
                row["en"] = st[-1][0]
                row["by_era"] = {e: eras_of(e) for e in sorted(ens)}
            elif key in unify or auto:
                best = unify.get(key) or max(ens, key=lambda e: (ens[e], max(ERAS.index(a) for x, a in st if x == e)))
                row["en"] = best
                row["variants"] = {e: eras_of(e) for e in sorted(ens)}
                for e, era in st:
                    if e != best:
                        en_fix.append((era, {"place": "地点", "polity": "政权", "physical": "山川"}[kind], rid, zh, e, best))
            else:
                row["en"] = max(ens, key=lambda e: (ens[e], max(ERAS.index(a) for x, a in st if x == e)))
                row["variants"] = {e: eras_of(e) for e in sorted(ens)}
                gl_rows.append(({"place": "地点", "polity": "政权"}[kind], rid, zh,
                                "；".join(f"{e}（{'、'.join(eras_of(e))}）" for e in sorted(ens))))
            glossary.append(row)

    for p in places:
        refs = p["refs"] + [x["ref"] for x in p.get("seats", [])]
        gloss("place", p["id"], [(ref2c[r]["main"], ref2c[r]["en"], ref2c[r]["era"]) for r in refs], False)
    for rec in polities:
        gloss("polity", rec["id"], [(po2c[r]["n"], po2c[r]["en"], po2c[r]["era"]) for r in rec["refs"]], False)
    for rec in physical:
        gloss("physical", rec["id"], [(ph2c[r]["old"], ph2c[r]["en"], ph2c[r]["era"]) for r in rec["refs"]], True)
    write_jsonl(GLOBAL / "glossary.jsonl", glossary)
    (REVIEW / "glossary.md").write_text(
        "# 译名审定清单\n\n地点、政权里，同一个对象、同一个中文名，各卷英文写法不同、还没定的。"
        "定下来的写进 `global/decisions.toml` 的 `[glossary]`：`unify` 统一成一种写法（其余卷列进改正清单），"
        "`by_era` 按时代各用各的（如麴氏高昌作 Gaochang、回鹘高昌作 Qocho）。山川默认统一成用得最多的写法。\n\n"
        + (md_table(["类别", "全局 ID", "中文", "各卷英文"], gl_rows) if gl_rows else "（已全部审定）") + "\n", encoding="utf8")

    # 衔接年份：前一卷最后一个节点与后一卷第一个节点
    jrows = build_junctions(B, polities)
    parts = ["# 衔接审定清单\n\n相邻两卷在衔接年份各画了一次疆域。`global/junctions.toml` 里记着每个衔接年份以哪一卷为准；"
             "这里列出两卷在衔接节点上的差别，供核对。重合度 = 交集面积 ÷ 并集面积，1 表示完全一样；"
             "只在两卷都画到的范围内比（图幅边缘被一卷截掉的部分不算），面积栏仍是各卷画出的全部面积。\n"]
    for r in jrows:
        yy = lambda t: f"前{-(t // 12)}" if t < 0 else str(t // 12)
        same = "同一年" if r["same_time"] else f"相邻两年（{yy(r['t_from'])} / {yy(r['t_to'])}）"
        low = [x for x in r["ious"] if x[1] < 0.98]
        parts.append(f"\n## {ERA_ZH[r['from']]} → {ERA_ZH[r['to']]}（{same}）\n\n"
                     f"共有政权 {len(r['ious'])} 个，其中疆域完全一致（重合度 ≥ 0.98）{len(r['ious']) - len(low)} 个。\n")
        if low:
            parts.append(md_table(["全局 ID", "重合度", f"{ERA_ZH[r['from']]}面积", f"{ERA_ZH[r['to']]}面积"],
                                  [(pid, f"{iou:.2f}", f"{aa:.1f}", f"{zz:.1f}") for pid, iou, aa, zz in sorted(low, key=lambda x: x[1])]) + "\n")
        if r["rename"]:
            parts.append(f"\n两卷名字不同、疆域相交的政权。重合度高的多半是同一政权换了名字（若是，把末栏抄进 `global/decisions.toml` 的 `[polities] merge`）；"
                         f"重合度低而「小者落入」高的，是一卷单列、另一卷并入了别的政权（如一卷单列的部族，另一卷画在宗主政权的范围里），这类不要合并，属于衔接年份画法不一致。\n\n"
                         + md_table([ERA_ZH[r["from"]], ERA_ZH[r["to"]], "重合度", "小者落入", "面积", "decisions.toml"],
                                    [(x, y, f"{iou:.2f}", f"{cov:.2f}", f"{aa:.0f} / {zz:.0f}", f'`["{ra}", "{rz}"],`')
                                     for x, y, iou, cov, aa, zz, ra, rz in sorted(r["rename"], key=lambda q: -q[2])]) + "\n")
        if r["only_from"]:
            parts.append(f"\n只在{ERA_ZH[r['from']]}卷衔接节点上有：{'、'.join(r['only_from'])}\n")
        if r["only_to"]:
            parts.append(f"\n只在{ERA_ZH[r['to']]}卷衔接节点上有：{'、'.join(r['only_to'])}\n")
    (REVIEW / "junctions.md").write_text("".join(parts), encoding="utf8")

    # 改正清单：各卷页面里要改的地方（坐标由 [[place]]、[[seat]] 推出，其余手写在 corrections.toml）
    # 不牵动疆域的（条目点位、英文、标了 step = 3 的内容）第 3 步已在新页面上改（core/v1/overlay.py），其余留到第 5—7 步
    import overlay
    yy = lambda y: f"前{-y}" if y < 0 else str(y)
    S3, S5 = "新页面已改", "第 5—7 步"
    rows, coords = [], []
    for pid, c, y0, y1, st in sorted(p_fix, key=lambda x: (ERAS.index(x[1]["era"]), x[0], x[1]["ref"])):
        ok = overlay.page_coord_ok(c["era"], c["ref"])
        rows.append((ERA_ZH[c["era"]], f"{c['main']} `{c['ref']}`", pid, f"{yy(y0)}—{yy(y1)}",
                     f"{c['ll'][0]:.2f},{c['ll'][1]:.2f}", f"{st['lon']:.2f},{st['lat']:.2f}", st.get("note", ""), S3 if ok else S5))
        coords.append({"era": c["era"], "ref": c["ref"], "id": pid, "lon": st["lon"], "lat": st["lat"]})
    fixes = load_toml(GLOBAL / "corrections.toml").get("fix", []) if (GLOBAL / "corrections.toml").exists() else []
    rows2 = [("、".join(ERA_ZH.get(e, e) for e in f["era"].split("、")), f.get("at", ""), f["what"], f.get("why", ""),
              S3 if f.get("step") == 3 else S5) for f in fixes]
    rows3 = [(ERA_ZH[era], kind, rid, zh, e, best, S3) for era, kind, rid, zh, e, best in
             sorted(en_fix, key=lambda x: (ERAS.index(x[0]), x[1], x[2]))]
    KIND = {"地点": "place", "政权": "polity", "山川": "physical"}
    (ROOT / "build" / "v1").mkdir(parents=True, exist_ok=True)
    (ROOT / "build" / "v1" / "fixes.json").write_text(json.dumps({
        "coords": coords,
        "en": [{"era": era, "kind": KIND[kind], "id": rid, "zh": zh, "cur": e, "best": best} for era, kind, rid, zh, e, best in en_fix],
    }, ensure_ascii=False, indent=0), encoding="utf8")
    n3 = sum(r[-1] == S3 for r in rows)
    (GLOBAL / "corrections.md").write_text(
        "# 各卷改正清单\n\n第 2 步审定出来、各卷页面里要改的地方。全局表已经按改正后的写。"
        "不牵动疆域的（都城、关隘等条目的点位，英文译名，部分内容）第 3 步已在新页面上改，见末栏「新页面已改」"
        "（`core/v1/overlay.py` 在生成 v1 数据时套用，各卷原始数据暂不动）；"
        "牵动疆域的（州府与春秋、战国城邑这些归属点的坐标、疆域本身）留到第 5—7 步重算疆域时改。"
        "本文件由 `python core/v1/registry.py` 生成，内容改正手写在 `global/corrections.toml`。\n\n"
        f"## 坐标（{len(rows)} 处，新页面已改 {n3} 处）\n\n与全局地点表里那个年代的城址相距 2 km 以上的（坐标精度约 1 km）。\n\n"
        + md_table(["卷", "条目", "全局地点", "年代", "现坐标", "应为", "城址", "状态"], rows)
        + f"\n\n## 内容（{len(rows2)} 处）\n\n" + md_table(["卷", "年代", "改什么", "依据", "状态"], rows2)
        + f"\n\n## 英文（{len(rows3)} 处）\n\n同一对象、同一中文名，统一成一种英文写法后，各卷要改的。\n\n"
        + md_table(["卷", "类别", "全局 ID", "中文", "现在", "改为", "状态"], rows3) + "\n",
        encoding="utf8")

    # 汇总
    multi = [p for p in places if len(p["eras"]) > 1]
    stats = {
        "地点": len(places), "跨卷地点": len(multi), "地点待审": len(p_review), "坐标改正": len(p_fix),
        "政权与二级单位": len(polities), "跨卷政权": sum(1 for p in polities if len(p["eras"]) > 1),
        "配色不同": len(colors_review), "同名未合并": len(flagged), "英文名不同的政权": len(en_review),
        "山川": len(physical), "跨卷山川": sum(1 for p in physical if len(p["eras"]) > 1), "山川待审": len(phys_review),
        "译名待审": len(gl_rows), "英文改正": len(en_fix),
        "衔接不一致": {f"{r['from']}→{r['to']}": sum(1 for x in r["ious"] if x[1] < 0.98) for r in jrows},
    }
    (GLOBAL / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
    for k, v in stats.items():
        print(f"{k:12s} {v}")


if __name__ == "__main__":
    main()
