# -*- coding: utf-8 -*-
"""第 3 步在新页面上先行改正的内容（规范第十九节第 3 步）。

各卷成品（eras/<短名>/legacy.html）保持原样，作为数据来源；build.py 转成 v1 后在这里套用改正，新页面由改正后的 v1 生成。
只改不牵动疆域的：
  · 条目点位（都城、关隘等）的坐标，按 global/places.jsonl 的城址；州府（唐宋系）与春秋、战国的城邑条目是疆域归属点，留到第 5—7 步；
  · 英文译名统一（global/corrections.md「英文」一节）；
  · global/corrections.toml 里标了 step = 3 的内容改正；
  · 时间轴短标题（eras/<短名>/short.tsv）。
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAYERED = {"hanmosanguo", "liangjin-nanbeichao", "suitang", "tangsong", "songyuan", "minguo-xinzhongguo"}


def page_coord_ok(era, ref):
    """坐标改正能否在第 3 步先改：唐宋系的条目（非州府）"""
    return era in LAYERED and ref.startswith(f"{era}:i:")


def node_index(b, year):
    """year 之后（含）的第一个节点序号"""
    for j, n in enumerate(b["nodes"]):
        if n["t"] // 12 >= year:
            return j
    return len(b["nodes"])


def set_lab(b, k, zh, en, nodes):
    for j in nodes:
        n = b["nodes"][j]
        n.setdefault("lab", {})[str(k)] = zh
        n.setdefault("en", {}).setdefault("lab", {})[str(k)] = en


def polity(b, key):
    for k, p in enumerate(b["polities"]):
        if p["key"] == key:
            return k, p
    raise KeyError(key)


# ---- global/corrections.toml 里 step = 3 的改正，按 id ----

def fix_tangsong_zhancheng(b):
    # 林邑 → 环王（8 世纪中叶）→ 占城（9 世纪后期）：本名改作「占城」，此前的节点标「环王」
    k, p = polity(b, "环王")
    p["n"], p["en"]["n"] = "占城", "Champa"
    set_lab(b, k, "环王", "Huanwang", range(0, node_index(b, 877)))
    return "唐宋卷「环王（占城）」：877 年以后标「占城」，此前标「环王」"


def fix_tangsong_chenla(b):
    # 802 年阇耶跋摩二世统一陆、水真腊，建吴哥王朝；疆域扩大留到第 5—7 步
    k, p = polity(b, "文单")
    p["n"], p["en"]["n"] = "真腊（吴哥）", "Chenla (Angkor)"
    set_lab(b, k, "文单（陆真腊）", "Wendan (Land Chenla)", range(0, node_index(b, 802)))
    return "唐宋卷「文单（陆真腊）」：802 年以后标「真腊（吴哥）」（疆域留到第 5—7 步）"


def fix_songyuan_indrapura(b):
    for p in b["places"]:
        if p["key"] == "因陀罗补罗":
            p["names"] = [x for x in p["names"] if x[1] != "毗阇耶（迁都）"]
            p["en"]["names"] = [x for x in p["en"]["names"] if x != "Vijaya (capital moved)"]
            return "宋元卷州府「因陀罗补罗」：去掉 1000 年改名「毗阇耶（迁都）」"
    raise KeyError("因陀罗补罗")


HAN_CHANGAN = {"lon": 108.88, "lat": 34.31, "mod": "陕西西安西北（汉长安城）", "mode": "Northwest of Xi'an, Shaanxi (Han Chang'an)"}


def fix_daxing(b):
    out = []
    for o in b["items"]:
        if o["c"] == "capital" and o["old"] == "大兴城（长安）":
            if b["era"] == "liangjin-nanbeichao":
                # 本卷只到 581 年：隋初仍居汉长安城
                o["old"], o["en"]["old"] = "长安", "Chang'an"
                o["lon"], o["lat"] = HAN_CHANGAN["lon"], HAN_CHANGAN["lat"]
                o["mod"], o["en"]["mod"] = HAN_CHANGAN["mod"], HAN_CHANGAN["mode"]
                out.append("两晋卷 581 年都城「大兴城（长安）」改回「长安」，坐标用汉长安城")
            elif b["era"] == "suitang":
                # 隋及唐初卷：581—583 年在汉长安城，583 年三月迁入大兴城；拆成两段
                a, z = o["_yrs"][0]
                n = dict(o)
                n.update(old="长安", lon=HAN_CHANGAN["lon"], lat=HAN_CHANGAN["lat"], mod=HAN_CHANGAN["mod"], i=len(b["items"]),
                         _yrs=[[a, 583]], spans=[[a * 12, 583 * 12]])
                n["en"] = dict(o.get("en", {}), old="Chang'an", mod=HAN_CHANGAN["mode"])
                n["note"] = "隋初沿用汉长安城为都，开皇二年（582）六月命宇文恺于其东南营建新都，三年（583）三月迁入，名大兴城。"
                n["en"]["note"] = "The early Sui court used the old Han city of Chang'an as its capital; in the 6th month of 582 Yuwen Kai was ordered to build a new capital to its southeast, which the court moved into in the 3rd month of 583 and named Daxing City."
                o["_yrs"] = [[583, z]]
                o["spans"] = [[583 * 12, o["spans"][0][1]]]
                b["items"].append(n)
                out.append("隋唐卷都城「大兴城（长安）」拆为 581—583 年「长安」（汉长安城）与 583 年起「大兴城（长安）」")
    return "；".join(out) if out else None


CONTENT = {
    "tangsong-zhancheng": fix_tangsong_zhancheng,
    "tangsong-chenla": fix_tangsong_chenla,
    "songyuan-indrapura": fix_songyuan_indrapura,
    "daxing": fix_daxing,
}


# ---- 套用 ----

def first_gid(g):
    return g[0][1] if isinstance(g, list) else g


def gids_of(g):
    return [x[1] for x in g] if isinstance(g, list) else [g]


def apply_coords(slug, b, fixes):
    n = 0
    for f in fixes:
        if f["era"] != slug or not page_coord_ok(slug, f["ref"]):
            continue
        i = int(f["ref"].rsplit(":", 1)[1])
        o = b["items"][i]
        assert o["i"] == i, (slug, i)
        o["lon"], o["lat"] = f["lon"], f["lat"]
        n += 1
    return n


def swap(d, k, cur, best):
    if isinstance(d.get(k), str) and d[k] == cur:
        d[k] = best
        return 1
    if isinstance(d.get(k), list):
        c = 0
        for j, v in enumerate(d[k]):
            if v == cur:
                d[k][j] = best
                c += 1
        return c
    return 0


def apply_en(slug, b, fixes):
    n = 0
    for f in fixes:
        if f["era"] != slug:
            continue
        rid, zh, cur, best = f["id"], f["zh"], f["cur"], f["best"]
        hit = 0
        if f["kind"] == "polity":
            for k, p in enumerate(b["polities"]):
                if p.get("gid") == rid:
                    hit += swap(p["en"], "n", cur, best) + swap(p["en"], "s", cur, best)
                    for nd in b["nodes"]:
                        hit += swap(nd.get("en", {}).get("lab", {}), str(k), cur, best)
        else:
            if f["kind"] == "place":
                for p in b["places"]:
                    if rid in gids_of(p.get("gid") or []):
                        hit += swap(p["en"], "n", cur, best) + swap(p["en"], "names", cur, best)
            for o in b["items"]:
                if o.get("gid") and rid in gids_of(o["gid"]) and "en" in o:
                    hit += swap(o["en"], "old", cur, best)
        n += bool(hit)
    return n


def apply_shorts(slug, b):
    p = ROOT / "eras" / slug / "short.tsv"
    if not p.exists():
        return 0
    rows = {}
    with open(p, encoding="utf8") as f:
        for r in csv.DictReader((line for line in f if not line.startswith("#")), delimiter="\t"):
            rows[r["节点"].strip()] = r
    n = 0
    for nd in b["nodes"]:
        y, m = nd["t"] // 12, nd["t"] % 12 + 1
        key = f"{y}.{m}" if b["time"] == "month" else str(y)
        r = rows.get(key)
        if r and r["短标题"].strip():
            nd["short"] = r["短标题"].strip()
            if r.get("英文", "").strip():
                nd.setdefault("en", {})["short"] = r["英文"].strip()
            n += 1
    return n


def apply(slug, b, fixes, content):
    """fixes：registry.py 写出的 build/v1/fixes.json；content：corrections.toml 的 [[fix]]"""
    done = []
    c = apply_coords(slug, b, fixes.get("coords", []))
    if c:
        done.append(f"条目坐标 {c} 处")
    e = apply_en(slug, b, fixes.get("en", []))
    if e:
        done.append(f"英文译名 {e} 处")
    for f in content:
        if f.get("step") != 3 or slug not in f["era"].split("、"):
            continue
        r = CONTENT[f["id"]](b)
        if r:
            done.append(r)
    s = apply_shorts(slug, b)
    if s:
        done.append(f"时间轴短标题 {s} 个")
    return done
