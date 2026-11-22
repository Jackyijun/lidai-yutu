# -*- coding: utf-8 -*-
"""在新页面上改正的内容（规范第十九节第 3 步起）。

各卷第 1 段的产物（eras/<短名>/source.json）保持原样，作为数据来源；build.py 转成 v1 后在这里套用改正，新页面由改正后的 v1 生成：
  · 坐标（apply_coords，build.py 在换引擎几何之前先套用）：条目点位（都城、关隘等）与归属点（州府等）按 global/places.jsonl 的城址。
    归属点是统一引擎的输入，疆域按改后的点重算；春秋、战国的归属点取自两卷共用的 content/seeds.txt，不进全局表，
    要改直接改那个文件，这里只改两卷的城邑条目；
  · 山川改画（apply_ranges）：decisions.toml [physical.prefer] 写了 page = true 的，各卷都画成选定那一卷的线（武陵山、伏牛山）；
  · 英文译名统一（global/corrections.md「英文」一节）；
  · global/corrections.toml 里标了 step = 3 的内容改正；
  · 时间轴短标题（eras/<短名>/short.tsv）；
  · 全局配色（global/palette.toml，按政权全局 ID；规范第三节）；
  · 大漠的范围（geodata/derived/damo.json，由 tools/damo.py 从生态区改绘，七卷共用；规范第十九节「大漠范围」）；
  · 毛乌素、科尔沁、库布齐三处沙地的范围（geodata/derived/sands.json，由 tools/sands.py 手绘，按卷分档）。
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


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
    # 802 年阇耶跋摩二世统一陆、水真腊，建吴哥王朝。本卷的「文单」此后包括原水真腊之地（2026-11-22 图幅南扩到 10°N 后补上，
    # 见 eras/tangsong/content/snaps.txt 的 805 年节点），这里只改名
    k, p = polity(b, "文单")
    p["n"], p["en"]["n"] = "真腊（吴哥）", "Chenla (Angkor)"
    set_lab(b, k, "文单（陆真腊）", "Wendan (Land Chenla)", range(0, node_index(b, 802)))
    return "唐宋卷「文单（陆真腊）」：802 年以后标「真腊（吴哥）」"


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
    """fixes：build/v1/fixes.json 的 coords。引用是「卷:i:序号」的改条目，「卷:键」的改归属点（连同它所对应的条目）"""
    items = {o["i"]: o for o in b["items"]}
    n = 0
    for f in fixes:
        if f["era"] != slug:
            continue
        key = f["ref"].split(":", 1)[1]
        if key.startswith("i:"):
            o = items[int(key[2:])]
            o["lon"], o["lat"] = f["lon"], f["lat"]
        else:
            p = next(p for p in b["places"] if p["key"] == key)
            p["lon"], p["lat"] = f["lon"], f["lat"]
            if "item" in p:
                o = items[p["item"]]
                o["lon"], o["lat"] = f["lon"], f["lat"]
        n += 1
    return n


def apply_ranges(b, ranges):
    """fixes：build/v1/fixes.json 的 ranges，[{id, geo, anc}]：这些山脉各卷都画成同一条线，注记点随之"""
    by = {r["id"]: r for r in ranges}
    n = 0
    for it in b["items"]:
        r = by.get(it.get("gid"))
        if r and it.get("geo") != r["geo"]:
            it["geo"] = [list(q) for q in r["geo"]]
            if r["anc"]:
                it["anc"] = list(r["anc"])
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


def palette():
    """global/palette.toml 的 [color]：全局 ID → [浅色, 深色]"""
    import tomllib
    return tomllib.loads((ROOT / "global" / "palette.toml").read_text(encoding="utf8")).get("color", {})


MISSING_COLOR = ["#A3A3A3", "#6B6B6B"]   # 缺色时的占位灰（只在 missing_ok 的那一遍用，见 apply_palette）


def apply_palette(b, pal, missing_ok=False):
    """按全局 ID 定政权配色：各卷第 1 段不出颜色（架构整理第三批起；旧构建的贪心配色已冻结进表），
    每个政权都要在 palette.toml 里有颜色，缺了停下。missing_ok（core/v1/build.py 的 --lenient、--draft-colors：
    重算疆域之前那一遍，和 tools/palette.py 选色用的一遍）时先用占位灰，缺的全局 ID 记在 meta.palette_missing。
    节点里逐年渐变的 col（两晋旧构建的高句丽、林邑）一并去掉"""
    import sys
    era = b.get("era", "")
    nogid = [p["key"] for p in b["polities"] if not p.get("gid")]
    if nogid:
        sys.exit(f"{era}：这些政权在全局表里查不到（全局表过期？先运行 python core/v1/registry.py）：" + "、".join(nogid))
    miss = sorted({p["gid"] for p in b["polities"] if p["gid"] not in pal})
    if miss and not missing_ok:
        sys.exit(f"{era}：global/palette.toml 里没有这些政权的颜色：" + "、".join(miss) +
                 "\n  运行 python tools/palette.py 按疆域邻接选色（--write 写进 [color]），再运行 python run.py --web")
    if miss:
        print(f"{era}：global/palette.toml 里还没有这些政权的颜色，暂用灰色：" + "、".join(miss))
        b.setdefault("meta", {})["palette_missing"] = miss
    n, hit = 0, set()
    for i, p in enumerate(b["polities"]):
        c = pal.get(p["gid"], MISSING_COLOR)
        if p["color"] is None or list(p["color"]) != list(c):
            p["color"] = list(c)
            n += 1
        hit.add(str(i))
    for nd in b["nodes"]:
        col = nd.get("col")
        if col:
            for k in [k for k in col if k in hit]:
                del col[k]
            if not col:
                del nd["col"]
    return n


DAMO_NOTE = ("范围据 RESOLVE 生态区（2017）的戈壁三区改绘，扣去漠南草原与河西、居延绿洲（居延扣去汉至元的古绿洲即黑城一带，"
             "连同弱水下游河道与今额济纳绿洲）。",
             "Extent redrawn from the three Gobi ecoregions of RESOLVE Ecoregions 2017, leaving out the steppe south of the desert "
             "and the Hexi and Juyan oases (for Juyan, both the ancient oasis of Han to Yuan times around Khara-Khoto and the lower "
             "Ruoshui with today's Ejin oasis).")
DAMO_NOTE_MODERN = ("范围据 RESOLVE 生态区（2017）的戈壁三区改绘，扣去漠南草原与河西走廊、额济纳绿洲。汉至元的古居延绿洲（黑城一带）"
                    "随弱水下游河道西北移而干涸，元末明初废弃（1372 年明军至亦集乃路），本卷画作荒漠。",
                    "Extent redrawn from the three Gobi ecoregions of RESOLVE Ecoregions 2017, leaving out the steppe south of the desert, "
                    "the Hexi Corridor and the Ejin oasis. The ancient Juyan oasis of Han to Yuan times, around Khara-Khoto, dried up as the "
                    "lower Ruoshui shifted northwest; it was abandoned in the late Yuan and early Ming (Ming troops reached Ejina Circuit "
                    "in 1372), so it is drawn as desert here.")
DAMO_NOTE_QINHAN = ("乌兰布和沙漠北部是汉代朔方郡的垦区，东汉中期以后渐废弃垦，此后才沙化，本卷不画。",
                    "The northern Ulan Buh Desert was farmland in the Han-dynasty Shuofang Commandery; it was gradually abandoned from "
                    "the middle of the Eastern Han onward and only then turned to sand, so it is left out here.")
DAMO_NOTE_HANMO = ("乌兰布和沙漠北部是汉代朔方郡的垦区，东汉中期以后人口锐减，永和五年（140）朔方郡内徙五原，建安二十年（215）省郡，"
                   "垦区先后荒废，此后才渐沙化（北魏刁雍已称薄骨律至沃野「道多深沙」），本卷不画。",
                   "The northern Ulan Buh Desert was farmland in the Han-dynasty Shuofang Commandery. From the middle of the Eastern Han "
                   "the commandery's population fell sharply; it was moved inland to Wuyuan in Yonghe 5 (140) and abolished in Jian'an 20 "
                   "(215), the farmland was abandoned in stages, and only then did the area gradually turn to sand (the Northern Wei "
                   "official Diao Yong already wrote that the road from Bogulü to Woye had \"much deep sand\"), so it is left out here.")
# 大漠按卷分档：秦汉、汉末两卷扣乌兰布和北部的汉代垦区；民国卷只扣今额济纳绿洲
DAMO_VARIANT = {"qinhan": ("han", DAMO_NOTE_QINHAN), "hanmosanguo": ("han", DAMO_NOTE_HANMO), "minguo-xinzhongguo": ("modern", None)}


def apply_damo(slug, b):
    """大漠（全局 ID desert:大碛）换成 tools/damo.py 由生态区改绘的范围（geodata/derived/damo.json），各卷共用；
    原来取的是 Natural Earth 地理区的「GOBI DESERT」注记区，盖住了阴山以北的漠南、河西走廊与胪朐河"""
    import engine_geom
    its = [it for it in b["items"] if it.get("gid") == "desert:大碛"]
    if not its:
        return 0
    dm = json.loads((ROOT / "geodata" / "derived" / "damo.json").read_text(encoding="utf8"))
    variant, extra = DAMO_VARIANT.get(slug, ("all", None))
    rings = dm[variant]
    ids = {it["i"] for it in its}
    base = b["base"]["deserts"]
    at = next(n for n, d in enumerate(base) if d.get("it") in ids)
    keep = [d for d in base if d.get("it") not in ids]
    new = [{"r": engine_geom.enc_ring(r), "it": its[0]["i"]} for r in rings]
    b["base"]["deserts"] = keep[:at] + new + keep[at:]
    for it in its:
        it["anc"] = list(dm["label"])
        zh, en = DAMO_NOTE_MODERN if variant == "modern" else DAMO_NOTE
        if extra:
            zh, en = zh + extra[0], en + " " + extra[1]
        it["note"] = (it.get("note") or "") + zh
        e = it.setdefault("en", {})
        e["note"] = ((e.get("note") or "") + " " + en).strip()
    return len(its)


SANDS_NOTE = {
    "desert:毛乌素沙地": ("范围示意：今毛乌素沙地约 4 万 km²。统万城下本即有沙，本图只按史料所见的流沙画，范围较小。",
                         "The extent is schematic: today the Mu Us covers about 40,000 km². There was sand around Tongwan City "
                         "from the start; this map draws only the drifting sand recorded in the sources, so the area shown is smaller."),
}
SANDS_NOTE_MODERN = {
    "desert:毛乌素沙地": ("范围示意，约当今毛乌素沙地（约 4 万 km²）。",
                         "The extent is schematic and roughly matches today's Mu Us (about 40,000 km²)."),
    "desert:科尔沁沙地": ("范围示意，按今沙地的主体画，比 20 世纪中叶偏大。",
                         "The extent is schematic, drawn from the main body of today's sandy land, so it is somewhat larger than it was in the mid-20th century."),
}
SANDS_NOTE_DEFAULT = ("范围示意。", "The extent is schematic.")


def apply_sands(slug, b):
    """随时代变化的沙地（毛乌素、科尔沁、库布齐）：几何换成 tools/sands.py 手绘的本卷那一档（geodata/derived/sands.json）。
    原来毛乌素取 Natural Earth 的「Mu Us Desert」，其实是整个鄂尔多斯高原；科尔沁、库布齐在各卷史料里只写注记点"""
    import engine_geom
    sd = json.loads((ROOT / "geodata" / "derived" / "sands.json").read_text(encoding="utf8"))
    n = 0
    for gid, eras in sd.items():
        its = [it for it in b["items"] if it.get("gid") == gid]
        if not its:
            if slug in eras:
                raise SystemExit(f"{slug}：geodata/derived/sands.json 有 {gid} 的范围，本卷却没有这个全局 ID 的条目"
                                 "（全局 ID 变了？在 global/decisions.toml 的 [physical.id] 钉住）")
            continue
        if slug not in eras:
            raise SystemExit(f"{slug}：{gid} 在 geodata/derived/sands.json 里没有本卷的范围（tools/sands.py）")
        ids = {it["i"] for it in its}
        base = b["base"]["deserts"]
        at = next((k for k, d in enumerate(base) if d.get("it") in ids), len(base))
        keep = [d for d in base if d.get("it") not in ids]
        new = [{"r": engine_geom.enc_ring(r), "it": its[0]["i"]} for r in eras[slug]]
        b["base"]["deserts"] = keep[:at] + new + keep[at:]
        zh, en = (SANDS_NOTE_MODERN if slug == "minguo-xinzhongguo" else {}).get(gid) or SANDS_NOTE.get(gid, SANDS_NOTE_DEFAULT)
        for it in its:
            it["anc"] = list(eras["label"][slug])
            it["note"] = (it.get("note") or "") + zh
            e = it.setdefault("en", {})
            e["note"] = ((e.get("note") or "") + " " + en).strip()
        n += 1
    return n


def apply(slug, b, fixes, content, missing_ok=False):
    """fixes：registry.py 写出的 build/v1/fixes.json；content：corrections.toml 的 [[fix]]。坐标另由 apply_coords 先改。
    missing_ok：缺色时先用占位灰（见 apply_palette）"""
    done = []
    d = apply_damo(slug, b)
    if d:
        done.append("大漠范围（生态区改绘）")
    d = apply_sands(slug, b)
    if d:
        done.append(f"沙地范围 {d} 处（手绘，按时代）")
    r = apply_ranges(b, fixes.get("ranges", []))
    if r:
        done.append(f"山脉改画 {r} 条")
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
    c = apply_palette(b, palette(), missing_ok)
    if c:
        done.append(f"全局配色 {c} 个政权")
    return done
