# -*- coding: utf-8 -*-
"""引擎的输入：一卷的 v1 数据包（归属点、节点）加上全局的山川、陆地，以及各卷 era.toml 的 [engine]。

  bundle(slug)            build/v1/<短名>.json
  view(slug)              统一格式的归属点与节点（两种政权模型合成一种「点 → 单位 → 政权」）
  ranges()                全局山脉：每条取一种画法（global/decisions.toml 的 [physical.prefer]，其余取多数卷）
  rivers(b) / lakes(b)    界河与湖：取本卷画的（黄河、淮河等历代改道，各卷画的是本时代的河道）
  land(bbox)              Natural Earth 1:10m 陆地与小岛（经纬度多边形）
  ne_ranges()             Natural Earth 山地多边形
  frontier(slug)          手绘外缘（隋唐、两晋），没有则 None
  fingerprint(slug, b)    引擎输入的指纹（归属点、节点归属、引擎参数、外缘设置）：eras/<短名>/engine.json 过期没有，靠它判断
  spec / region / reach_mult / walls    各卷的外缘设置、推算范围、各点可达倍数、国界墙
"""
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import shapely
from shapely.geometry import shape, box

ROOT = Path(__file__).resolve().parents[2]
V1 = ROOT / "build" / "v1"
NE = ROOT / "geodata" / "ne"
ERAS = ["chunqiu", "zhanguo", "qinhan", "hanmosanguo", "liangjin-nanbeichao", "suitang", "tangsong", "songyuan", "minguo-xinzhongguo"]

try:
    import tomllib
except ImportError:
    import tomli as tomllib

_B = {}


def bundle(slug):
    if slug not in _B:
        p = V1 / f"{slug}.json"
        if not p.exists():
            sys.exit(f"缺 build/v1/{slug}.json，先运行 python run.py --v1")
        _B[slug] = json.loads(p.read_text(encoding="utf8"))
    return _B[slug]


def dec(a):
    """v1 的整数差分序列 → [(经, 纬)]"""
    x = y = 0; out = []
    for i in range(0, len(a) - 1, 2):
        x += a[i]; y += a[i + 1]; out.append((x / 100, y / 100))
    return out


def view(slug, b=None):
    """引擎读入的统一格式：两种政权模型合成一种「点 → 单位 → 政权」（规范第十九节）。

      seeds  [(经, 纬, 键)]
      nodes  [(t, own, pol, active)]：own = 各点归哪个单位（单位键或 None），pol = {单位键: 政权键}，
             active = 各点这一节点是否参与分区（None 为全部参与）

    单位键就是 v1 节点 u 的键。分层卷（唐宋系六卷）取 v1 的 places 与节点 own / pol。
    简单卷（春秋、战国）的 v1 里没有分区用的归属点，取两卷共用的 content/seeds.txt（归属沿革、~年份退出）：
    单位是诸侯国，政权是它自己；春秋另按 ALLEGIANCE 把奉周的诸侯归到「周」，政权层的外缘就是共主着色的「周天下」。"""
    b = b or bundle(slug)
    if b["model"] == "layered":
        S = [(p["lon"], p["lat"], p["key"]) for p in b["places"]]
        N = []
        for n in b["nodes"]:
            own = [None if v is None or v < 0 else str(v) for v in n["own"]]
            N.append((n["t"], own, {k: str(v) for k, v in n["pol"].items()}, None))
        return S, N
    seeds_ = []
    for line in (ROOT / "eras" / slug / "content" / "seeds.txt").read_text(encoding="utf8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        t = line.split()
        tl = [(-10 ** 9, None if t[3] == "·" else t[3])]
        end = None
        for tok in t[4:]:
            if tok.startswith("~"):
                end = int(tok[1:]); continue
            i = 1 if tok[0] == "-" else 0
            while tok[i].isdigit():
                i += 1
            tl.append((int(tok[:i]), None if tok[i:] == "·" else tok[i:]))
        seeds_.append((float(t[1]), float(t[2]), t[0], tl, end))
    feats = era_module(slug, "content/features.py") if (ROOT / "eras" / slug / "content" / "features.py").exists() else None
    alleg = getattr(feats, "ALLEGIANCE", None)
    kind = getattr(feats, "STATE_KIND", {}) if feats else {}
    keys = {p["key"] for p in b["polities"]}
    N = []
    for n in b["nodes"]:
        y = n["t"] // 12
        own, act = [], []
        for _, _, _, tl, end in seeds_:
            o = None
            for t0, k in tl:
                if y >= t0:
                    o = k
            own.append(o if o in keys else None)
            act.append(end is None or y < end)
        units = sorted({o for o, a in zip(own, act) if o and a})
        pol = {}
        for k in units:
            p = k
            if alleg is not None and k != "周" and kind.get(k) != "tribe":
                st = "奉周"
                for y0, s_, *_ in alleg.get(k, []):
                    if y >= y0:
                        st = s_
                p = "周" if st == "奉周" else k
            pol[k] = p
        N.append((n["t"], own, pol, act))
    return [(lo, la, nm) for lo, la, nm, _, _ in seeds_], N


# ---------------- 全局山脉 ----------------
def ranges():
    """[(全局 ID, 是否主干, [(经, 纬)])]，每个全局 ID 一条"""
    prefer = tomllib.loads((ROOT / "global" / "decisions.toml").read_text(encoding="utf8")).get("physical", {}).get("prefer", {})
    cand = defaultdict(list)                  # gid → [(卷, 主干, 几何)]
    for slug in ERAS:
        for it in bundle(slug)["items"]:
            if it["c"] == "range" and it.get("geo") and it.get("gid"):
                g = [tuple(p) for p in it["geo"]]
                cand[it["gid"]].append((slug, bool(it.get("major")), g))
    out = []
    for gid in sorted(cand):
        L = cand[gid]
        want = prefer.get(gid, {}).get("era")
        pick = [x for x in L if x[0] == want]
        if not pick:                          # 取画法相同的卷最多的一种；并列取卷次靠后的
            cnt = Counter(tuple(x[2]) for x in L)
            best = max(cnt.values())
            pick = [x for x in reversed(L) if cnt[tuple(x[2])] == best]
        slug, _, g = pick[0]
        major = any(x[1] for x in L if x[2] == g)
        out.append((gid, major, g))
    return out


# ---------------- 本卷的河湖 ----------------
def rivers(b, weights):
    """{全局 ID: [[(经, 纬)], …]}，只取 weights 里列出的界河"""
    its = {it["i"]: it for it in b["items"]}
    out = defaultdict(list)
    for r in b["base"]["rivers"]:
        it = its.get(r.get("it"))
        if it and it.get("gid") in weights:
            out[it["gid"]].append(dec(r["p"]))
    return dict(out)


def lakes(b):
    out = []
    for lk in b["base"]["lakes"]:
        pts = dec(lk["r"])
        if len(pts) >= 4:
            out += [g for g in shapely.get_parts(shapely.make_valid(shapely.Polygon(pts))) if g.geom_type == "Polygon"]
    return out


# ---------------- 陆地 ----------------
_LAND = None


def land(bbox):
    """经纬度 bbox（西, 东, 南, 北）内的陆地多边形列表；东经可大于 180（接缝以东）"""
    global _LAND
    if _LAND is None:
        polys = []
        for nm in ("ne_10m_land", "ne_10m_minor_islands"):
            for f in json.loads((NE / f"{nm}.geojson").read_text(encoding="utf8"))["features"]:
                g = shape(f["geometry"])
                polys += list(shapely.get_parts(g))
        _LAND = polys
    W, E, S, N = bbox
    out = []
    for shift in (0, 360):                    # 接缝以东（东经 180 以东）的陆地平移 360°
        bb = box(W - shift, S, E - shift, N)
        for p in _LAND:
            if p.intersects(bb):
                q = p.intersection(bb)
                if shift:
                    q = shapely.transform(q, lambda a: a + [shift, 0])
                out += [g for g in shapely.get_parts(q) if g.geom_type == "Polygon"]
    return out


_NER = None


def ne_ranges():
    """Natural Earth 山地多边形（Range/mtn，面积 60 平方度以下）"""
    global _NER
    if _NER is None:
        _NER = []
        for f in json.loads((NE / "ne_10m_geography_regions_polys.geojson").read_text(encoding="utf8"))["features"]:
            p = f["properties"]
            if f["geometry"] and p.get("FEATURECLA") == "Range/mtn":
                g = shape(f["geometry"])
                if g.area < 60:
                    _NER.append(g if g.is_valid else shapely.make_valid(g))
    return _NER


# ---------------- 外缘 ----------------
def frontier(slug):
    """手绘外缘（经纬度点列），各卷 content/frontier.py 的 outer_lonlat()；没有则 None"""
    p = ROOT / "eras" / slug / "content" / "frontier.py"
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"frontier_{slug.replace('-', '_')}", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.outer_lonlat()


# ---------------- 各卷的引擎设置（era.toml 的 [engine]） ----------------
def spec(slug):
    """era.toml 的 [engine]：
      outer = "frontier"   手绘外缘（content/frontier.py）
      outer = "reach"      按可达代价定外缘；box = 推算范围 [西, 东, 南, 北]，seeds = 写 R=倍数 的归属点文件
      config = "src/config.py"   这一卷自己的设置文件，读其中的 EXCLUDE（推算范围里剔除的多边形）与国界墙
      walls = true / prov_walls = true   烧国界墙 / 今中国省界弱墙（民国）"""
    t = tomllib.loads((ROOT / "eras" / slug / "era.toml").read_text(encoding="utf8"))
    s = t.get("engine")
    if not s:
        sys.exit(f"eras/{slug}/era.toml 没有 [engine]，这一卷还没接上统一引擎")
    return s


def era_module(slug, rel):
    """载入一卷自己的 Python 设置文件（如 src/config.py），只读其中的常量"""
    p = ROOT / "eras" / slug / rel
    spec_ = importlib.util.spec_from_file_location(f"cfg_{slug.replace('-', '_')}_{p.stem}", p)
    m = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(m)
    return m


def reach_mult(slug, s):
    """各点可达代价倍数：seeds 文件里的 R=倍数，{点 ID: 倍数}"""
    out = {}
    p = ROOT / "eras" / slug / s.get("seeds", "content/seeds.txt")
    files = sorted(p.glob("*.txt")) if p.is_dir() else [p]
    for f in files:
        for line in f.read_text(encoding="utf8").splitlines():
            t = line.split()
            if not t or t[0].startswith("#"):
                continue
            for x in t[4:]:
                if x.startswith("R="):
                    out[t[0]] = float(x[2:])
    return out


def region(slug, s):
    """reach 卷的推算范围（经纬度多边形）：box 减去设置文件里的 EXCLUDE"""
    W, E, S, N = s["box"]
    g = box(W, S, E, N)
    ex = getattr(era_module(slug, s["config"]), "EXCLUDE", []) if s.get("config") else []
    if ex:
        g = g.difference(shapely.union_all([shapely.Polygon(p) for p in ex]))
    return g


def _month(s_):
    y, m = s_.split("."); return int(y) * 12 + int(m) - 1


def walls(slug, s):
    """国界墙（民国式）。返回 dict：fixed = 常设墙折线、prov = 今中国省界（弱墙）、var = [(名称, 折线, 起月, 止月)]；
    折线都是经纬度点列。没有墙的卷返回 None"""
    if not s.get("walls"):
        return None
    m = era_module(slug, s["config"])
    W, E, S, N = s["box"]
    BB = box(W - 1, S - 1, E + 1, N + 1)
    reg = region(slug, s)
    ctry = []
    for f in json.loads((NE / "ne_10m_admin_0_countries_chn.geojson").read_text(encoding="utf8"))["features"]:
        if f["geometry"]:
            g = shape(f["geometry"])
            if g.intersects(BB):
                ctry.append(g.intersection(BB))
    landu = shapely.union_all(land((W - 1, E + 1, S - 1, N + 1)))
    coast = landu.boundary.buffer(0.04)
    bl = shapely.union_all([g.boundary for g in ctry]).difference(coast)
    skip = shapely.union_all([shapely.Polygon(p) for p in m.WALL_SKIP])
    fixed_g = bl.difference(skip).intersection(reg.buffer(0.5))

    def lines(g):
        return [list(l.coords) for l in shapely.get_parts(shapely.line_merge(g)) if l.geom_type == "LineString" and len(l.coords) > 1]

    def seg(pts):
        return list(shapely.segmentize(shapely.LineString(pts), 0.05).coords)

    fixed = lines(fixed_g) + [seg(w[1]) for w in m.MANUAL_WALLS if len(w) == 2]
    var = []
    for w in m.MANUAL_WALLS:
        if len(w) > 2:
            var.append((w[0], [seg(w[1])], _month(w[2]) if w[2] else -10 ** 9, _month(w[3]) if w[3] else 10 ** 9))
    for nm, ib, a, b_ in m.VAR_NE_WALLS:
        var.append((nm, lines(bl.intersection(shapely.Polygon(m.WALL_SKIP[ib]))), _month(a) if a else -10 ** 9, _month(b_) if b_ else 10 ** 9))
    prov = []
    if s.get("prov_walls"):
        P = json.loads((ROOT / "geodata" / "prov" / "tangsong.json").read_text(encoding="utf8"))
        pv = [shapely.Polygon(dec(r)) for p in P for r in p["r"] if len(r) >= 6]
        pb = shapely.union_all([g.boundary for g in pv]).difference(coast).difference(fixed_g.buffer(0.1))
        prov = lines(pb)
    return dict(fixed=fixed, prov=prov, var=var)


# ---------------- 引擎输入的指纹（第 7 步） ----------------
def fingerprint(slug, b=None):
    """由引擎读入的东西算一个指纹：归属点与各节点的「点 → 单位 → 政权」（view）、core/engine/config.toml、
    era.toml 的 [engine]、手绘外缘文件。各卷页面疆域取 eras/<短名>/engine.json 时，拿它判断那份结果是不是按当前归属算的。
    山脉、界河、陆地等全局底图不计在内（改了要手动重算：python run.py <短名>）。"""
    import hashlib
    S, N = view(slug, b)
    h = hashlib.sha1()
    h.update(json.dumps([[list(x) for x in S], [[t, own, sorted(pol.items()), act] for t, own, pol, act in N]],
                        ensure_ascii=False, separators=(",", ":")).encode("utf8"))
    h.update((ROOT / "core" / "engine" / "config.toml").read_bytes())
    h.update(json.dumps({k: v for k, v in spec(slug).items() if k != "geometry"}, sort_keys=True, ensure_ascii=False).encode("utf8"))
    fr = ROOT / "eras" / slug / "content" / "frontier.py"
    if fr.exists():
        h.update(fr.read_bytes())
    return h.hexdigest()[:16]
