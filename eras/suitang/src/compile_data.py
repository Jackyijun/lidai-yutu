# 汇编：各节点归属、底图（build/geo_base.json）、条目 → GEO / DATA，输出 build/out_data.json
# python src/compile_data.py --report 可逐节点列出各单位所领州郡
# 疆域由统一疆域引擎按各节点的归属推算（单仓 core/engine/，结果在本卷的 engine.json），颜色由单仓的 global/palette.toml 定；
# 本卷原来的势力格（src/territory.py → build/cells.pkl）与按势力格并合疆域 2026-11 架构整理第三批起退役。
import json, sys
from shapely.geometry import Polygon
from seeds import SEEDS, SID
from units import U
from snaps import NODES, FIRST, expand
import items as IT
import config as C

UK = {u['k']: i for i, u in enumerate(U)}
BASE = json.load(open(C.BUILD / 'geo_base.json', encoding='utf-8'))

# ---------------- 归属 ----------------
own = [None] * len(SEEDS)
pol = {}; lab = {}; h = []
SN = []
for n in NODES:
    for a, b in n['move'].items():
        own = [b if x == a else x for x in own]
    for uk, lst in n['own'].items():
        assert uk in UK, uk
        for sid in expand(lst):
            own[SID[sid]] = uk
    for sid in expand(n['drop']): own[SID[sid]] = None
    pol.update(n['pol']); lab.update(n['lab'])
    if n['h'] is not None: h = n['h']
    present = sorted(set(x for x in own if x))
    SN.append(dict(n=n, own=list(own), present=present, pol={u: pol.get(u, u) for u in present},
                   lab={u: lab[u] for u in present if u in lab and lab[u] != U[UK[u]]['n']}, h=[u for u in h if u in present],
                   seat={u: s for u, s in n['seat'].items() if u in present}))
# 治所沿用：同一单位的 seat 向后继承
last = {}
for s in SN:
    for u, v in s['seat'].items(): last[u] = v
    s['seat'] = {u: v for u, v in last.items() if u in s['present']}

def report():
    for s in SN:
        n = s['n']
        print(f"\n== {n['y']}.{n['m']} {n['t']}")
        for u in s['present']:
            ids = [SEEDS[i]['id'] for i, x in enumerate(s['own']) if x == u]
            print(f"  {u}（{s['pol'][u]}）：{len(ids)} " + ' '.join(i for i in ids if SEEDS[SID[i]]['t'] != 'r')[:300])


def main():
    build()

# ---------------- 编码 ----------------
def enc_ll(pts):
    out = []; px = py = None; first = True
    lx = ly = 0
    for lon, lat in pts:
        x, y = int(round(lon * 100)), int(round(lat * 100))
        if (x, y) == (px, py): continue
        if first: out += [x, y]; first = False
        else: out += [x - lx, y - ly]
        lx, ly = x, y; px, py = x, y
    return out

def build():
    snaps_out = []
    for s in SN:
        n = s['n']
        snaps_out.append({
            'y': n['y'], 'm': n['m'], 'era': n['era'], 't': n['t'], 'd': n['d'],
            'own': [UK[x] if x else -1 for x in s['own']],
            'pol': {UK[u]: UK[p] for u, p in s['pol'].items()},
            'lab': {UK[u]: t for u, t in s['lab'].items()},
            'seat': {UK[u]: SID[v] for u, v in s['seat'].items()},
            'h': [UK[u] for u in s['h']],
            **({'jn': 'tangsong'} if (n['y'], n['m']) == (755, 12) else {}),   # 衔接节点：疆域照搬唐宋卷 755 年节点
        })

    # ---------------- 条目 ----------------
    ITEMS = []
    def add(it):
        it = {k: v for k, v in it.items() if v is not None}
        it['i'] = len(ITEMS); ITEMS.append(it); return it['i']

    def near_seed(lon, lat):
        for i, s in enumerate(SEEDS):
            if abs(s['lon'] - lon) < .02 and abs(s['lat'] - lat) < .02 and s['t'] != 'r': return i
        return None

    for c in IT.CAP:
        d = dict(c); d['st'] = UK[d['st']]; d['at'] = near_seed(d['lon'], d['lat']); add(d)
    for b in IT.BAT: add(dict(b))
    TSI = {it['i']: it for it in IT.TS}
    pass_ts = [it for it in IT.TS if it['c'] == 'pass' and it['old'] not in IT.DEL_PASS]
    for it in pass_ts:
        d = {k: it[k] for k in ('c', 'old', 'mod', 'lon', 'lat')}
        d['note'] = IT.PASS.get(it['old'], it.get('note', ''))
        add(d)
    for o, m, lon, lat, note, *yrs in IT.NEWPASS:
        add(dict(c='pass', old=o, mod=m, lon=lon, lat=lat, note=note, **({'yrs': yrs[0]} if yrs else {})))
    for e in IT.EV: add(dict(e))
    # 山脉
    ts_map = {}
    for it in IT.TS:
        if it['c'] == 'range':
            d = dict(it); d.pop('i')
            if d['old'] == '大雪山': d['old'] = '大雪山（川西）'
            d['note'] = IT.RANGE_NOTE.get(it['old'], it.get('note', ''))
            ts_map[it['i']] = add(d)
    for o, m, note, geo, anc, major in IT.NEWRANGE:
        add(dict(c='range', old=o, mod=m, note=note, geo=geo, anc=list(anc), major=major))
    # 水系
    for it in IT.TS:
        if it['c'] == 'river':
            if it['old'] in IT.DEL_RIVER or it.get('mod', '').startswith('微山湖') or it['old'] == '梁山泊': continue
            d = dict(it); d.pop('i')
            d['note'] = IT.RIVER_NOTE.get(it['old'], it.get('note', ''))
            ts_map[it['i']] = add(d)
    key_item = {}
    anc_of = {}
    for r in BASE['rivers']:
        if r.get('key'): anc_of.setdefault(r['key'], []).extend(r['p'])
    for key, o, m, note, major in IT.NEWRIV:
        pts = anc_of.get(key)
        if not pts: continue
        a = pts[len(pts) // 2]
        key_item[key] = add(dict(c='river', sub='river', old=o, mod=m, note=note, major=major, anc=[a[0], a[1]]))
    lake_item = {}
    for ne, o, m, note in IT.NEWLAKE:
        lk = [l for l in BASE['lakes'] if l.get('ne') == ne]
        if lk:
            P_ = Polygon(lk[0]['r']); c = P_.representative_point()
            lake_item[ne] = add(dict(c='river', sub='lake', old=o, mod=m, note=note, major=False, anc=[round(c.x, 2), round(c.y, 2)]))
    # 运河
    for it in IT.TS:
        if it['c'] == 'canal':
            d = dict(it); d.pop('i')
            y0, note = IT.CANAL[it['old']]
            if it['old'] == '漕渠': d['old'] = '广通渠（漕渠）'; d['mod'] = '西安—潼关间渭河南岸'
            d['note'] = note; d['y0'] = y0
            ts_map[it['i']] = add(d)
    # 荒漠
    DESERT_NOTE = {'大流沙': '西域南北两道之间的大沙漠，玄奘东归时经其南缘，称“流沙”。', '大碛': '漠南与漠北之间的戈壁，隋唐人称大碛、沙碛；647 年唐于其间开参天可汗道。'}
    DESERT_DROP = {'普纳沙'}   # 毛乌素沙地：大片流沙唐中后期（822 年首见记载）才出现，本卷（到 669 年）不画
    for it in IT.TS:
        if it['c'] == 'desert' and it['old'] not in DESERT_DROP:
            d = dict(it); d.pop('i'); d['note'] = DESERT_NOTE.get(it['old'], it.get('note', ''))
            ts_map[it['i']] = add(d)
    # 行军·行程路线：秦王征战在前（条目号同前），第 8 步补的接在后面
    routes = [{'it': add(dict(c='route', old='秦王李世民征战路线', mod='617—649 年', note=IT.ROUTE_NOTE, anc=[111.3, 35.9])),
               'pts': [[x, y, round(t, 4), n] for x, y, t, n in IT.ROUTE]}]
    for R in IT.ROUTES:
        mid = R['pts'][len(R['pts']) // 2]
        routes.append({'it': add(dict(c='route', old=R['old'], mod=R['mod'], note=R['note'], anc=[mid[0], mid[1]])),
                       'pts': [[x, y, round(t, 4), n] for x, y, t, n in R['pts']]})
    # 诸族
    for o, m, lon, lat, y0, y1, note in IT.PEOPLE:
        add(dict(c='people', old=o, mod=m, lon=lon, lat=lat, y0=y0, y1=y1, note=note))

    # ---------------- GEO ----------------
    def enc_list(pts): return enc_ll(pts)
    GEO = {
        'land': [[enc_list(r) for r in p] for p in BASE['land']],
        'prov': [{'n': p['n'], 'c': p['c'], 'r': [enc_list(r) for r in p['r']]} for p in BASE['prov']],
        'border': [enc_list(b) for b in BASE['border']],
        'rivers': [], 'lakes': [], 'canals': [], 'deserts': [], 'regions': [],
        'snaps': snaps_out, 'routes': routes, 'ext': C.VIEW_EXT,
    }
    for r in BASE['rivers']:
        it = ts_map.get(r['ts_it']) if r.get('ts_it') is not None else key_item.get(r.get('key'))
        if r.get('ts_it') is not None and r['ts_it'] not in ts_map: it = None
        GEO['rivers'].append({'p': enc_list(r['p']), 'k': r['k'], **({'it': it} if it is not None else {})})
    for lk in BASE['lakes']:
        it = ts_map.get(lk['ts_it']) if lk.get('ts_it') is not None else lake_item.get(lk.get('ne'))
        GEO['lakes'].append({'r': enc_list(lk['r']), **({'it': it} if it is not None else {})})
    for c in BASE['canals']: GEO['canals'].append({'p': enc_list(c['p']), 'it': ts_map[c['ts_it']]})
    for d in BASE['deserts']:
        if d.get('ts_it') is None or d['ts_it'] not in ts_map: continue
        GEO['deserts'].append({'r': enc_list(d['r']), 'it': ts_map[d['ts_it']]})

    # ---------------- DATA ----------------
    KIND = {'state': 'state', 'dh': 'zhen', 'tribe': 'tribe', 'misc': 'misc'}
    DATA = {
        'units': [{'k': u['k'], 'n': u['n'], 'kind': KIND[u['kind']], 'note': u['note']} for u in U],
        'seeds': [{k: v for k, v in dict(id=s['id'], n=s['n'], mod=s['mod'], lon=s['lon'], lat=s['lat'], t=s['t'], nm=s['nm'], a=s.get('a'), v=s.get('v')).items() if v is not None} for s in SEEDS],
        'items': ITEMS,
    }
    DATA['first'] = FIRST
    json.dump({'GEO': GEO, 'DATA': DATA}, open(C.BUILD / 'out_data.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    from collections import Counter
    print('  [汇编] 条目', len(ITEMS), dict(Counter(i['c'] for i in ITEMS)))
    print('  [汇编] GEO', len(json.dumps(GEO, separators=(',', ':'))) // 1024, 'KB · DATA', len(json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))) // 1024, 'KB')


if __name__ == '__main__':
    report() if '--report' in sys.argv else main()
