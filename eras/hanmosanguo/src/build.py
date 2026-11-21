# -*- coding: utf-8 -*-
"""汉末三国形势图 · 数据构建（单仓第 1 段）。

读 content/ 的史料与 geodata/ 的底图，写出 build/geo.json（底图、各节点归属）与 build/data.json（条目与说明），
再由 src/assemble.py 汇编成本卷的 source.json；另写 build/reach.txt（统一疆域引擎用的各点可达倍数）。

疆域与州界不在这里算：由统一疆域引擎按各节点的归属推算（单仓 core/engine/，结果在本卷的 engine.json；州的划法在
src/zhou.py，引擎也读它）；颜色由单仓的 global/palette.toml 定。本卷原来的代价栅格、多源最短路、覆盖图描界
（src/terrain.py）2026-11 架构整理第三批起退役。
"""
import json, sys
from collections import Counter
from shapely.geometry import Polygon

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import config as C
sys.path.insert(0, str(C.CONTENT))
from seeds import SEEDS
from units import UNITS
from nodes import NODES
import items as I

UK = {u["k"]: i for i, u in enumerate(UNITS)}
SI = {s["id"]: i for i, s in enumerate(SEEDS)}
assert len(SI) == len(SEEDS), "种子 id 重复"
HATCH = {"公孙氏", "士燮", "张鲁", "黑山"}       # 名义臣属、实则自立（斜线）
from zhou import jun_of, zhou_han, zhou_of   # 郡的归属与州（统一引擎画州界读 zhou.py 的 zone_of，划法相同）


# ================================================================ 归属
def seeds_in(kind, key):
    out = []
    for i, s in enumerate(SEEDS):
        if kind == "Z" and zhou_han(s) == key: out.append(i)
        elif kind == "J" and jun_of(s) == key: out.append(i)
        elif kind == "G" and s["j"] == key: out.append(i)
        elif kind == "ID" and s["id"].startswith(key): out.append(i)
        elif kind == "C" and s["id"] == key: out.append(i)
    if not out: raise KeyError(f"nodes.py：{kind} {key} 没有匹配的种子")
    return out

def ownership():
    """逐节点执行 nodes.py 的操作，得到每个种子归哪个单位、单位属哪个政权。"""
    state = [None] * len(SEEDS)
    pol, lab, seat = {}, {}, {}
    out = []
    for nd in NODES:
        y = nd["y"]
        for op in nd["ops"]:
            if op[0] == "ALL":
                for i, s in enumerate(SEEDS):
                    if jun_of(s): state[i] = op[1]
            elif op[0] == "REPL":
                state = [op[2] if x == op[1] else x for x in state]
                if op[1] in seat: seat[op[2]] = seat.get(op[2], seat[op[1]])
            else:
                kind, key, u = op
                for i in seeds_in(kind, key): state[i] = u
        if y >= 192:        # 林邑自 192 年立国
            state[SI["象林"]] = "林邑"; state[SI["林邑南"]] = "林邑"
        pol.update(nd["pol"]); lab.update(nd["lab"]); seat.update(nd["seat"])
        present = sorted(set(x for x in state if x), key=lambda k: UK[k])
        P = {k: pol.get(k) or UNITS[UK[k]].get("pol") or k for k in present}
        keys = sorted(set(present) | set(P.values()), key=lambda k: UK[k])
        out.append(dict(nd=nd, own=list(state), pol=P, lab={k: lab[k] for k in keys if k in lab},
                        seat={k: seat[k] for k in present if k in seat}))
    return out


# ================================================================ 节点
def dec(flat):
    """差分编码（经纬度 ×100 取整）→ 点列"""
    out = []; x = y = 0
    for i in range(0, len(flat), 2):
        x += flat[i]; y += flat[i + 1]; out.append((x / 100, y / 100))
    return out


def enc(pts):
    """点列 → 差分编码"""
    out = []; px = py = 0
    for lo, la in pts:
        X = int(round(lo * 100)); Y = int(round(la * 100))
        out += [X - px, Y - py]; px, py = X, Y
    return out


def zhou_names():
    """各节点有郡国落在其中的州（按 src/zhou.py 的划法；部族、弃地不算）：州名注记由统一引擎标，英文要先备齐"""
    names = set()
    for r in ownership():
        y = r["nd"]["y"]
        for i, k in enumerate(r["own"]):
            if k and UNITS[UK[k]]["kind"] not in ("tribe", "waste"):
                z = zhou_of(SEEDS[i], y, k)
                if z: names.add(z)
    return sorted(names)


def node_rows():
    """各节点的归属、所属政权、别名、治所、斜线（疆域由统一引擎按这些推算）"""
    snaps = []
    for r in ownership():
        nd = r["nd"]; y = nd["y"]; own = r["own"]
        snaps.append(dict(y=y, era=nd["era"], era2=nd["era2"], t=nd["t"], d=nd["d"],
                          own=[UK[x] if x else -1 for x in own],
                          pol={UK[k]: UK[p] for k, p in r["pol"].items()},
                          lab={UK[k]: v for k, v in r["lab"].items() if v != UNITS[UK[k]]["n"]},
                          seat={UK[k]: SI[v] for k, v in r["seat"].items()},
                          h=[UK[k] for k in r["pol"] if k in HATCH or (k == "南匈奴" and r["pol"][k] == "汉")]))   # 184 年南匈奴内属于汉
        print(f"   {y:>4}  {len(set(x for x in own if x)):>2} 单位", flush=True)
    return snaps


# ================================================================ 条目
def build_items(base):
    TIT = {int(k): v for k, v in base["items"].items()}
    items = []
    def add(d):
        d["i"] = len(items); items.append(d); return d["i"]

    river_map = {}
    for i0 in sorted(TIT):
        it = TIT[i0]
        if it["c"] != "river": continue
        if it["old"] in I.DROP_LAKES: river_map[i0] = None; continue
        d = dict(c="river", sub=it["sub"], old=it["old"], mod=it["mod"], note="", major=it.get("major") or False)
        if it["old"] in I.RIVER_RENAME:
            o, m, n, mj = I.RIVER_RENAME[it["old"]]
            d.update(old=o, mod=m, note=n)
            if mj is not None: d["major"] = mj
        for k in ("anc", "lon", "lat", "rx", "ry"):
            if k in it: d[k] = it[k]
        river_map[i0] = add(d)
    for (o, m, lon, lat, rx, ry, n) in I.NEW_MARSHES:
        add(dict(c="river", sub="marsh", old=o, mod=m, note=n, major=False, lon=lon, lat=lat, rx=rx, ry=ry))
    new_river_lines = []
    JI = next(i for i in items if i.get("old") == "济水")["i"]
    for (o, m, line, k, anc, n) in I.NEW_RIVERS:
        if o == "济水（上游）":
            new_river_lines.append(dict(k=k, p=enc(line), it=JI)); continue
        idx = add(dict(c="river", sub="river", old=o, mod=m, note=n, major=False, anc=anc))
        new_river_lines.append(dict(k=k, p=enc(line), it=idx))

    canals_geo = []
    for (o, m, line, y0, anc, n) in I.CANALS:
        idx = add(dict(c="canal", old=o, mod=m, note=n, anc=anc, y0=y0))
        canals_geo.append(dict(p=enc(line), it=idx, y0=y0))
    for c in base["canals"]:
        old = TIT[c["it"]]["old"]
        if old in I.CANAL_KEEP:
            o, m, y0, n = I.CANAL_KEEP[old]
            idx = add(dict(c="canal", old=o, mod=m, note=n, anc=TIT[c["it"]]["anc"], y0=y0))
            canals_geo.append(dict(p=c["p"], it=idx, y0=y0))

    for i0 in sorted(TIT):
        it = TIT[i0]
        if it["c"] != "range": continue
        d = dict(c="range", old=it["old"], mod=it["mod"], note="", geo=it["geo"], anc=it["anc"], major=it.get("major") or False)
        if it["old"] in I.RANGE_RENAME:
            o, m, n, mj = I.RANGE_RENAME[it["old"]]
            d.update(old=o, mod=m, note=n, major=mj)
        add(d)
    for (o, m, geo, anc, mj, n) in I.NEW_RANGES:
        add(dict(c="range", old=o, mod=m, note=n, geo=geo, anc=anc, major=mj))

    DES = {"大流沙": ("流沙", "塔克拉玛干沙漠"), "大碛": ("大漠（瀚海）", "戈壁"), "普纳沙": ("毛乌素沙地", "毛乌素沙地")}
    DES_DROP = {"普纳沙"}      # 毛乌素沙地：大片流沙唐中后期（822 年首见记载）才出现，本卷不画
    desert_map = {}
    for i0 in sorted(TIT):
        it = TIT[i0]
        if it["c"] != "desert" or it["old"] in DES_DROP: continue
        o, m = DES.get(it["old"], (it["old"], it["mod"]))
        desert_map[i0] = add(dict(c="desert", old=o, mod=m, note="", anc=it["anc"]))

    for (o, m, geo, anc, n) in I.ROADS:
        add(dict(c="road", old=o, mod=m, note=n, geo=geo, anc=anc, major=True))
    for (o, m, lon, lat, st, yrs, at, n) in I.CAPITALS:
        add(dict(c="capital", old=o, mod=m, note=n, lon=lon, lat=lat, st=UK[st], yrs=yrs, at=SI[at]))
    for (o, m, lon, lat, y, yt, sides, cmd, n) in I.BATTLES:
        add(dict(c="battle", old=o, mod=m, note=n, lon=lon, lat=lat, y=y, yt=yt, sides=sides, cmd=cmd))
    for (o, m, lon, lat, n) in I.PASSES:
        add(dict(c="pass", old=o, mod=m, note=n, lon=lon, lat=lat))
    for (o, m, lon, lat, y, yt, n) in I.EVENTS:
        add(dict(c="event", old=o, mod=m, note=n, lon=lon, lat=lat, y=y, yt=yt))
    for (o, lon, lat, y0, y1, n) in I.PEOPLE:
        add(dict(c="people", old=o, mod="", note=n, lon=lon, lat=lat, y0=y0, y1=y1))

    rivers = []
    for r in base["rivers"]:
        it = r.get("it")
        if it is not None:
            if river_map.get(it) is None: continue
            r = dict(r, it=river_map[it])
        rivers.append(r)
    rivers += new_river_lines
    lakes = []
    for l in base["lakes"]:
        it = l.get("it")
        if it is not None and river_map.get(it) is None: continue
        c = Polygon(dec(l["r"])).centroid
        if any(abs(c.x - a) < 0.15 and abs(c.y - b) < 0.15 for a, b in I.DROP_LAKE_RINGS): continue
        if it is None and 108.6 < c.x < 109.1 and 40.8 < c.y < 41.1: continue   # 乌梁素海（近代形成）
        lakes.append(dict(l, it=river_map[it]) if it is not None else l)
    deserts = [dict(d, it=desert_map[d["it"]]) for d in base["deserts"] if d["it"] in desert_map]
    return items, dict(rivers=rivers, lakes=lakes, canals=canals_geo, deserts=deserts)


# 郡国治所在地图上标城名，郡名放进提示框
CITY = {"河南尹": "洛阳", "京兆尹": "长安", "魏郡": "邺", "南阳郡": "宛", "南郡": "江陵", "蜀郡": "成都", "广汉郡": "雒", "巴郡": "江州",
        "东郡": "濮阳", "东海郡": "郯", "汉阳郡": "冀", "陇西郡": "狄道", "武都郡": "下辨", "武威郡": "姑臧", "太原郡": "晋阳", "涿郡": "涿",
        "广阳郡": "蓟", "辽东郡": "襄平", "齐国": "临淄", "山阳郡": "昌邑", "济阴郡": "定陶", "梁国": "睢阳", "陈国": "陈", "鲁国": "鲁",
        "安平国": "信都", "赵国": "邯郸", "勃海郡": "南皮", "南海郡": "番禺", "吴郡": "吴", "彭城国": "彭城", "下邳国": "下邳", "广陵郡": "广陵",
        "平原郡": "平原", "陈留郡": "陈留", "弘农郡": "弘农", "河内郡": "怀", "长沙郡": "临湘", "交趾郡": "龙编", "苍梧郡": "广信", "汉中郡": "南郑",
        "丹阳郡": "宛陵", "会稽郡": "山阴", "豫章郡": "南昌", "九江郡": "阴陵", "庐江郡": "舒", "颍川郡": "阳翟", "汝南郡": "平舆", "河东郡": "安邑"}

def build_seeds():
    out = []
    for s in SEEDS:
        d = dict(id=s["id"], n=s["n"], mod=s["mod"], lon=s["lon"], lat=s["lat"], t=s["t"])
        if s["id"] in CITY:
            d["n"] = CITY[s["id"]]; d["jn"] = s["n"]
            if s.get("nm"): d["jnm"] = s["nm"]
        elif s.get("nm"): d["nm"] = s["nm"]
        if s.get("note"): d["note"] = s["note"]
        out.append(d)
    return out


def write_reach():
    """统一疆域引擎（单仓第 7 步）用的各点可达倍数，写到 build/reach.txt（era.toml 的 [engine] seeds）。
    旧算法的可达距离是「分区半径（度）× REACH_MULT」个代价·度；引擎的是 [outer] reach 个代价·投影单位（1° 约 17.45 投影单位）。
    两套代价的尺度不同（引擎的地形项更重），照字面折算外缘会缩进去一成多，所以再乘 REACH_ENGINE_SCALE（1.5：试过 1、1.5、2，
    1.5 时全卷有主陆地面积与旧版最接近、归属变化最小）。单独构建本卷（不在单仓里）时没有引擎设置，不写。"""
    import math
    eng = C.ROOT.parent.parent / "core" / "engine" / "config.toml"
    if not eng.exists(): return
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    base = tomllib.loads(eng.read_text(encoding="utf8"))["outer"]["reach"]
    deg = 1000 * math.pi / 180
    k = C.REACH_MULT * deg / base * C.REACH_ENGINE_SCALE
    rows = [f"{s['id']} {s['lon']} {s['lat']} - R={(s.get('R') or C.REACH_DEFAULT[s['t']]) * k * C.REACH_ENGINE_ADJ.get(s['id'], 1):.3f}\n"
            for s in SEEDS]
    (C.BUILD / "reach.txt").write_text("# 由 src/build.py 从 content/seeds.py 写出：点 经 纬 - R=可达倍数（分区半径折算，见 write_reach）\n"
                                       + "".join(rows), encoding="utf8")


def main():
    base = json.load(open(C.GEODATA / "base.json", encoding="utf8"))
    items, layers = build_items(base)
    snaps = node_rows()
    GEO = dict(land=base["land"], prov=base["prov"], border=base["border"], **layers,
               snaps=snaps, regions=[], ext=[72.0, 136.0, 15.5, 55.0], first=C.FIRST_YEAR)
    GEO["zhou"] = zhou_names()                  # 给 i18n 配州名英文（GEO.zhoue）用，汇编 source.json 时去掉
    DATA = dict(units=[dict(k=u["k"], n=u["n"], kind=u["kind"], note=u["note"], **({"x": 1} if u.get("x") else {})) for u in UNITS],
                seeds=build_seeds(), items=items)
    C.BUILD.mkdir(exist_ok=True)
    dump = lambda o, p: open(p, "w", encoding="utf8").write(json.dumps(o, ensure_ascii=False, separators=(",", ":")))
    dump(GEO, C.BUILD / "geo.json"); dump(DATA, C.BUILD / "data.json")
    write_reach()
    print(f"   {len(snaps)} 个节点 · {len(items)} 条目 · {len(SEEDS)} 个郡国城邑点 · {len(UNITS)} 个政权诸侯部族")
    print("   " + " ".join(f"{k} {v}" for k, v in Counter(i['c'] for i in items).most_common()))


if __name__ == "__main__":
    main()
