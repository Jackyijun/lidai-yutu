# 汇编：各节点归属、底图（build/geo_base.json）、条目 → GEO / DATA，输出 build/out_data.json
#   python src/compile_data.py --report         逐节点列出各单位所领归属点
#   python src/compile_data.py --report 383     只列这一年
# 衔接节点（规范第十八节）：280 年在汉末三国图范围内、581 年在隋及唐初图外缘内，归属照邻卷定，逐点写在 content/junction.py。
# 疆域由统一疆域引擎按各节点的归属推算（单仓 core/engine/，结果在本卷的 engine.json；衔接节点的疆域取邻卷的 engine.json），
# 颜色由单仓的 global/palette.toml 定；本卷原来的势力格（src/territory.py → build/cells.pkl）、按势力格并合疆域与贪心配色
# 2026-11 架构整理第三批起退役。
import json, sys
from seeds import SEEDS, SID
from units import U
from snaps import NODES, FIRST, expand
import junction as JN
import config as C

UK = {u['k']: i for i, u in enumerate(U)}

# ---------------- 衔接数据 ----------------
for key in ('hanmo', 'suitang'):
    for k in list(JN.OWN[key]) + JN.UNITS[key]:
        assert k in UK, f'content/junction.py：衔接政权 {k} 未在 units.py 中定义'
    for sid in [s for lst in JN.OWN[key].values() for s in lst] + JN.DROP[key]:
        assert sid in SID, f'content/junction.py：没有归属点 {sid}'

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
    if n['junction']:                                     # 邻卷范围以内的点照邻卷定（content/junction.py）
        for uk, lst in JN.OWN[n['junction']].items():
            for sid in lst: own[SID[sid]] = uk
        for sid in JN.DROP[n['junction']]: own[SID[sid]] = None
    pol.update(n['pol']); lab.update(n['lab']); kd.update(n['kd'])
    if n['h'] is not None: h = n['h']
    present = sorted(set(x for x in own if x))
    if n['junction']:
        present = sorted(set(present) | set(JN.UNITS[n['junction']]))
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


def main():
    build()


def build():
    BASE = json.load(open(C.BUILD / 'geo_base.json', encoding='utf-8'))
    snaps_out = []
    for s in SN:
        n = s['n']
        snaps_out.append({
            'y': n['y'], 'era': n['era'], 'era2': n['era2'], 't': n['t'], 'd': n['d'],
            'own': [UK[x] if x else -1 for x in s['own']],
            'pol': {UK[u]: UK[p] for u, p in s['pol'].items()},
            'lab': {UK[u]: t for u, t in s['lab'].items()},
            'seat': {UK[u]: SID[v] for u, v in s['seat'].items()},
            'h': [UK[u] for u in s['h']],
            'kd': {UK[u]: k for u, k in s['kd'].items()},
            **({'jn': n['junction']} if n['junction'] else {}),
        })

    import items_build
    ITEMS, GEO_EXTRA = items_build.build(BASE, SEEDS)

    GEO = {
        'land': [[enc_ll(r) for r in p] for p in BASE['land']],
        'prov': [{'n': p['n'], 'c': p['c'], 'r': [enc_ll(r) for r in p['r']]} for p in BASE['prov']],
        'border': [enc_ll(b) for b in BASE['border']],
        'snaps': snaps_out, 'ext': C.VIEW_EXT, 'first': FIRST, **GEO_EXTRA,
    }
    KIND = {'state': 'state', 'zhen': 'zhen', 'tribe': 'tribe', 'waste': 'tribe', 'misc': 'misc'}
    DATA = {
        'units': [{'k': u['k'], 'n': u['n'], 'kind': KIND[u['kind']], 'note': u['note'], **({'waste': 1} if u['kind'] == 'waste' else {})} for u in U],
        'seeds': [{k: v for k, v in dict(id=s['id'], n=s['n'], mod=s['mod'], lon=s['lon'], lat=s['lat'], t=s['t'], nm=s['nm']).items() if v is not None} for s in SEEDS],
        'items': ITEMS,
    }
    json.dump({'GEO': GEO, 'DATA': DATA}, open(C.BUILD / 'out_data.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    from collections import Counter
    print('  [汇编] 节点', len(snaps_out), '政权与方镇', len(U), '条目', len(ITEMS), dict(Counter(i['c'] for i in ITEMS)))
    print('  [汇编] GEO', len(json.dumps(GEO, separators=(',', ':'))) // 1024, 'KB · DATA', len(json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))) // 1024, 'KB')


if __name__ == '__main__':
    if '--report' in sys.argv:
        a = sys.argv[sys.argv.index('--report') + 1:]
        report(int(a[0]) if a else None)
    else:
        main()
