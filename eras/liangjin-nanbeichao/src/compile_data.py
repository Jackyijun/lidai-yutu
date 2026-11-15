# 汇编：各节点归属 → 疆域多边形（并合 build/cells.pkl 的势力格）→ GEO / DATA，输出 build/out_data.json
#   python src/compile_data.py --report         逐节点列出各单位所领归属点
#   python src/compile_data.py --report 383     只列这一年
# 衔接节点（规范第十八节）：280 年在汉末三国图范围内、581 年在隋及唐初图外缘内，归属与疆域环照搬邻卷，范围外用本图推算。
import json, pickle, colorsys, math, sys
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union, polylabel
from proj import proj, inv
from seeds import SEEDS, SID
from units import U, COL_SPAN
from snaps import NODES, FIRST, expand
import config as C

UK = {u['k']: i for i, u in enumerate(U)}
DEG = 17.453292519943295          # 1° ≈ 17.45 投影单位


def dec(flat):
    x = y = 0; out = []
    for i in range(0, len(flat), 2):
        x += flat[i]; y += flat[i + 1]; out.append((x / 100, y / 100))
    return out


def polys_of(g):
    if g is None or g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    if g.geom_type == 'MultiPolygon': return list(g.geoms)
    if g.geom_type == 'GeometryCollection': return [p for x in g.geoms for p in polys_of(x)]
    return []


def proj_poly(ring_ll):
    a = np.array(ring_ll, float)
    x, y = proj(a[:, 0], a[:, 1])
    return Polygon(list(zip(x, y)))


# ---------------- 衔接数据 ----------------
JUN = {}
for key, path in (('hanmo', C.JUNCTION_HANMO), ('suitang', C.JUNCTION_SUITANG)):
    J = json.load(open(path, encoding='utf-8'))
    if J['frame'] == 'box':
        W, S_, E, N_ = C.HANMO_FRAME
        n = 400
        ring = [(W + (E - W) * i / n, S_) for i in range(n)] + [(E, S_ + (N_ - S_) * i / n) for i in range(n)] + \
               [(E - (E - W) * i / n, N_) for i in range(n)] + [(W, N_ - (N_ - S_) * i / n) for i in range(n)]
    else:
        ring = J['frame']
    J['frame_ll'] = Polygon(ring).buffer(0)
    J['frame_p'] = proj_poly(ring).buffer(0)
    for k, u in J['units'].items():
        assert k in UK, f'衔接政权 {k} 未在 units.py 中定义'
        u['ll'] = unary_union([Polygon(dec(r)).buffer(0) for r in u['rings']])
        u['p'] = unary_union([proj_poly(dec(r)).buffer(0) for r in u['rings']])
    JUN[key] = J

# ---------------- 归属 ----------------
own = [None] * len(SEEDS)
pol, lab, kd = {}, {}, {}
h = []
SN = []
for n in NODES:
    for a, b in n['move'].items():
        assert a in UK and b in UK, (n['y'], a, b)
        own = [b if x == a else x for x in own]
    for uk, lst in n['own'].items():
        assert uk in UK, (n['y'], uk)
        for sid in expand(lst):
            own[SID[sid]] = uk
    for sid in expand(n['drop']): own[SID[sid]] = None
    if n['junction']:
        J = JUN[n['junction']]
        for i, s in enumerate(SEEDS):
            p = Point(s['lon'], s['lat'])
            if not J['frame_ll'].contains(p): continue
            k = next((k for k, u in J['units'].items() if u['ll'].contains(p)), None)
            if k: own[i] = k
            elif own[i] in J['units']: own[i] = None      # 邻卷政权在其范围内只取邻卷疆域
    pol.update(n['pol']); lab.update(n['lab']); kd.update(n['kd'])
    if n['h'] is not None: h = n['h']
    present = sorted(set(x for x in own if x))
    if n['junction']:
        present = sorted(set(present) | set(JUN[n['junction']]['units']))
    for u in present:
        p = pol.get(u, u)
        assert p in present or p == u, (n['y'], u, p)
    SN.append(dict(n=n, own=list(own), present=present,
                   pol={u: (pol.get(u, u) if pol.get(u, u) in present else u) for u in present},
                   lab={u: lab[u] for u in present if u in lab and lab[u] != U[UK[u]]['n']},
                   h=[u for u in h if u in present], kd={u: kd[u] for u in present if u in kd and kd[u] != U[UK[u]]['kind']},
                   seat={u: s for u, s in n['seat'].items() if u in present}))
last = {}
for s in SN:
    for u, v in s['seat'].items(): last[u] = v
    s['seat'] = {u: v for u, v in last.items() if u in s['present'] and s['own'][SID[v]] == u}


def report(year=None):
    for s in SN:
        n = s['n']
        if year and n['y'] != year: continue
        print(f"\n== {n['y']} {n['t']}")
        for u in s['present']:
            ids = [SEEDS[i]['id'] for i, x in enumerate(s['own']) if x == u]
            tag = '' if s['pol'][u] == u else f"（{s['pol'][u]}）"
            print(f"  {u}{tag}{' ＝' + s['lab'][u] if u in s['lab'] else ''}：{len(ids)} " + ' '.join(ids)[:260])


# ---------------- 编码 ----------------
def enc_ll(pts):
    out = []; prev = None; lx = ly = 0
    for lon, lat in pts:
        x, y = int(round(lon * 100)), int(round(lat * 100))
        if (x, y) == prev: continue
        if prev is None: out += [x, y]
        else: out += [x - lx, y - ly]
        lx, ly = x, y; prev = (x, y)
    return out


def enc_proj_ring(coords):
    a = np.array(coords)
    lon, lat = inv(a[:, 0], a[:, 1])
    return enc_ll(zip(lon, lat))


def rings_of(g):
    out = []
    for p in polys_of(g):
        if p.area < 0.6: continue
        for r in [p.exterior] + list(p.interiors):
            if Polygon(r).area < 0.6: continue
            e = enc_proj_ring(r.coords)
            if len(e) >= 8: out.append(e)
    return out


def main():
    build()


def build():
    D = pickle.load(open(C.BUILD / 'cells.pkl', 'rb'))
    CELLS = {k: MultiPolygon(polys_of(v)) for k, v in D['cells'].items()}
    LAND = D['land_p']
    BASE = json.load(open(C.BUILD / 'geo_base.json', encoding='utf-8'))

    def label_of(g):
        ps = polys_of(g.intersection(LAND))
        if not ps: return None
        big = max(ps, key=lambda p: p.area)
        try:
            c = polylabel(big, tolerance=0.5)
        except Exception:
            c = big.representative_point()
        r = big.exterior.distance(c)
        for ring in big.interiors: r = min(r, ring.distance(c))
        lon, lat = inv(c.x, c.y)
        return [round(float(lon), 2), round(float(lat), 2), round(sum(p.area for p in ps) / DEG ** 2, 2), round(r / DEG, 2)]

    snaps_out = []
    POOL, POOLK = [], {}
    for s in SN:
        n = s['n']
        geo_u = {}
        for u in s['present']:
            idx = [i for i, x in enumerate(s['own']) if x == u and i in CELLS]
            g = unary_union([CELLS[i] for i in idx]) if idx else None
            if g is not None and not g.is_empty: geo_u[u] = g
        z, lz = {}, {}
        J = JUN.get(n['junction'])
        verbatim = {}
        if J:
            F = J['frame_p']
            NB = unary_union([ju['p'] for ju in J['units'].values()])
            for u in list(geo_u):
                # 邻卷有的政权：范围内只取邻卷疆域；邻卷没有的政权：只填邻卷留白之处
                g = geo_u[u].difference(F if u in J['units'] else NB)
                if g.is_empty or g.area < 1: del geo_u[u]
                else: geo_u[u] = g
            for u, ju in J['units'].items():
                if u in geo_u:                       # 跨越范围线：邻卷范围内照搬，范围外接本图
                    geo_u[u] = unary_union([ju['p'], geo_u[u]])
                else:
                    verbatim[u] = ju
        if J:   # 校验：跨越范围线的单位，范围内与邻卷一致
            for u, ju in J['units'].items():
                if u in geo_u:
                    d = geo_u[u].intersection(F).symmetric_difference(ju['p'].intersection(F)).area
                    assert d < 2.0, ('衔接不一致', n['y'], u, d)
        for u, g in geo_u.items():
            rr = rings_of(g)
            if not rr: continue
            z[UK[u]] = rr
            L = label_of(g)
            if L: lz[UK[u]] = L
        for u, ju in verbatim.items():
            z[UK[u]] = ju['rings']
            if ju['label']: lz[UK[u]] = ju['label']
        pmap = s['pol']
        multi = {}
        for u, p in pmap.items(): multi.setdefault(p, []).append(u)
        P, LP = {}, {}
        for p, us in multi.items():
            if len(us) < 2: continue
            gs = [geo_u[u] for u in us if u in geo_u]
            if not gs: continue
            g = unary_union(gs)
            P[UK[p]] = rings_of(g)
            L = label_of(g)
            if L: LP[UK[p]] = L
        for dct in (z, P):
            for k in list(dct):
                key = json.dumps(dct[k], separators=(',', ':'))
                if key not in POOLK: POOLK[key] = len(POOL); POOL.append(dct[k])
                dct[k] = POOLK[key]
        snaps_out.append({
            'y': n['y'], 'era': n['era'], 'era2': n['era2'], 't': n['t'], 'd': n['d'],
            'z': z, 'lz': lz, 'p': P, 'lp': LP,
            'own': [UK[x] if x else -1 for x in s['own']],
            'pol': {UK[u]: UK[p] for u, p in pmap.items()},
            'lab': {UK[u]: t for u, t in s['lab'].items()},
            'seat': {UK[u]: SID[v] for u, v in s['seat'].items()},
            'h': [UK[u] for u in s['h']],
            'kd': {UK[u]: k for u, k in s['kd'].items()},
            **({'jn': n['junction']} if n['junction'] else {}),
        })

    # ---------------- 颜色 ----------------
    light, dark = colors(snaps_out)
    for sn in snaps_out:
        t = (sn['y'] - NODES[0]['y']) / (NODES[-1]['y'] - NODES[0]['y'])
        cs = {}
        for k in COL_SPAN:
            u = UK[k]
            if u not in sn['pol']: continue
            a, b = JUN['hanmo']['units'][k], JUN['suitang']['units'][k]
            cs[u] = [mix(a['light'], b['light'], t), mix(a['dark'], b['dark'], t)]
        if cs: sn['col'] = cs

    # 校验：衔接节点的疆域环、注记与颜色与邻卷一致
    for sn in snaps_out:
        if not sn.get('jn'): continue
        J = JUN[sn['jn']]
        for k, ju in J['units'].items():
            u = UK[k]
            col = sn.get('col', {}).get(u, [light[u], dark[u]])
            assert [c.upper() for c in col] == [ju['light'].upper(), ju['dark'].upper()], ('衔接颜色', sn['y'], k, col, ju['light'], ju['dark'])
            if POOL[sn['z'][u]] is ju['rings'] or POOL[sn['z'][u]] == ju['rings']:
                assert sn['lz'].get(u) == ju['label'], ('衔接注记', sn['y'], k)
    print('  [衔接] 280、581 两节点的疆域、注记、颜色与邻卷一致')

    import items_build
    ITEMS, GEO_EXTRA = items_build.build(BASE, SEEDS)

    GEO = {
        'land': [[enc_ll(r) for r in p] for p in BASE['land']],
        'prov': [{'n': p['n'], 'c': p['c'], 'r': [enc_ll(r) for r in p['r']]} for p in BASE['prov']],
        'border': [enc_ll(b) for b in BASE['border']],
        'snaps': snaps_out, 'pool': POOL, 'ext': C.VIEW_EXT, 'first': FIRST, **GEO_EXTRA,
    }
    KIND = {'state': 'state', 'zhen': 'zhen', 'tribe': 'tribe', 'waste': 'tribe', 'misc': 'misc'}
    DATA = {
        'units': [{'k': u['k'], 'n': u['n'], 'kind': KIND[u['kind']], 'note': u['note'], **({'waste': 1} if u['kind'] == 'waste' else {})} for u in U],
        'seeds': [{k: v for k, v in dict(id=s['id'], n=s['n'], mod=s['mod'], lon=s['lon'], lat=s['lat'], t=s['t'], nm=s['nm']).items() if v is not None} for s in SEEDS],
        'items': ITEMS,
    }
    css_l = ' '.join(f'--u-{i}:{light[i]};' for i in range(len(U)))
    css_d = ' '.join(f'--u-{i}:{dark[i]};' for i in range(len(U)))
    json.dump({'GEO': GEO, 'DATA': DATA, 'css_l': css_l, 'css_d': css_d}, open(C.BUILD / 'out_data.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    from collections import Counter
    print('  [汇编] 节点', len(snaps_out), '政权与方镇', len(U), '条目', len(ITEMS), dict(Counter(i['c'] for i in ITEMS)))
    print('  [汇编] GEO', len(json.dumps(GEO, separators=(',', ':'))) // 1024, 'KB · DATA', len(json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))) // 1024, 'KB')


# ---------------- 配色（规范第三节） ----------------
def dark_of(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(hh, min(.82, ll + .07), min(1, ss * 1.25 + .04))
    return '#%02X%02X%02X' % (round(r * 255), round(g * 255), round(b * 255))


def _lin(c): return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
def _gam(c): return 12.92 * c if c <= .0031308 else 1.055 * c ** (1 / 2.4) - .055


def to_oklab(hexc):
    r, g, b = (_lin(int(hexc[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l = .4122214708 * r + .5363325363 * g + .0514459929 * b
    m = .2119034982 * r + .6806995451 * g + .1073969566 * b
    s = .0883024619 * r + .2817188376 * g + .6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    return (.2104542553 * l + .7936177850 * m - .0040720468 * s, 1.9779984951 * l - 2.4285922050 * m + .4505937099 * s,
            .0259040371 * l + .7827717662 * m - .8086757660 * s)


def from_oklab(L, a, b):
    l = (L + .3963377774 * a + .2158037573 * b) ** 3
    m = (L - .1055613458 * a - .0638541728 * b) ** 3
    s = (L - .0894841775 * a - 1.2914855480 * b) ** 3
    rgb = (4.0767416621 * l - 3.3077115913 * m + .2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - .3413193965 * s,
           -.0041960863 * l - .7034186147 * m + 1.7076147010 * s)
    return '#%02X%02X%02X' % tuple(round(min(1, max(0, _gam(min(1, max(0, c))))) * 255) for c in rgb)


def mix(a, b, t):
    if t <= 0: return a
    if t >= 1: return b
    A, B = to_oklab(a), to_oklab(b)
    return from_oklab(*(x + (y - x) * t for x, y in zip(A, B)))


def colors(snaps_out):
    """未指定颜色的单位：在低彩度 OKLCH 色板里，按全部节点的邻接关系贪心选色，与邻居色差尽量大"""
    light, dark = {}, {}
    for key in ('hanmo', 'suitang'):
        for k, ju in JUN[key]['units'].items():
            if k in COL_SPAN: continue
            light[UK[k]] = ju['light']; dark[UK[k]] = ju['dark']
    for i, u in enumerate(U):
        if i not in light and u['col']: light[i] = u['col']
    # 邻接：同一节点里两单位的疆域相接
    adj = {i: set() for i in range(len(U))}
    D = pickle.load(open(C.BUILD / 'cells.pkl', 'rb'))
    cells = D['cells']
    keys = sorted(cells)
    tree = shapely.STRtree([cells[k] for k in keys])
    nb = {}
    for j, k in enumerate(keys):
        nb[k] = [keys[x] for x in tree.query(cells[k].buffer(1.5), predicate='intersects') if keys[x] != k]
    for sn in snaps_out:
        own = sn['own']
        for s, ns in nb.items():
            a = own[s]
            if a < 0: continue
            for t in ns:
                b = own[t]
                if b >= 0 and b != a: adj[a].add(b); adj[b].add(a)
    # 色板：L 0.72—0.82，C 0.035—0.075，色相 12 等分
    pal = []
    for L in (.73, .78, .82):
        for Cc in (.045, .07):
            for hdeg in range(0, 360, 20):
                hr = math.radians(hdeg + (10 if Cc > .05 else 0))
                pal.append(from_oklab(L, Cc * math.cos(hr), Cc * math.sin(hr)))
    order = sorted([i for i in range(len(U)) if i not in light and U[i]['k'] not in COL_SPAN], key=lambda i: (-len(adj[i]), i))
    for i in order:
        used = [to_oklab(light[j]) for j in adj[i] if j in light]
        best, bd = None, -1
        for c in pal:
            q = to_oklab(c)
            d = min((math.dist(q, x) for x in used), default=1)
            if d > bd + 1e-9: best, bd = c, d
        light[i] = best
    for k in COL_SPAN:
        i = UK[k]
        light[i] = JUN['hanmo']['units'][k]['light']; dark[i] = JUN['hanmo']['units'][k]['dark']
    for i in range(len(U)):
        if i not in dark: dark[i] = dark_of(light[i])
    return light, dark


if __name__ == '__main__':
    if '--report' in sys.argv:
        a = sys.argv[sys.argv.index('--report') + 1:]
        report(int(a[0]) if a else None)
    else:
        main()
