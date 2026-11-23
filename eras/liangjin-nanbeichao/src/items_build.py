# 条目汇编：都城、战役、关隘、事件、山川、运河、荒漠、行军路线、诸族 → ITEMS 与 GEO 的水系、荒漠、路线部分
import re
from shapely.geometry import Polygon
import items as IT
from items_hist import CAP, BAT, EV, PEOPLE, ROUTES
from units import U

UK = {u['k']: i for i, u in enumerate(U)}
CAP_AT = {'长安': '雍州', '邺': '相州', '蓟': '幽州', '广固': '青州'}   # 都城名 → 州府点 id
CN = {'正': 1, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11, '十二': 12, '冬': 11, '腊': 12}


def month_of(y, yt):
    """从年份说明里取该年的月份（农历月，不折算），取不到返回 None"""
    m = re.search(rf'{y} 年(?:闰)?(十一|十二|正|十|[一二三四五六七八九]|冬|腊)月', yt)
    if m: return CN[m.group(1)]
    m = re.search(rf'{y} 年(春|夏|秋|冬)', yt)
    if m: return {'春': 2, '夏': 5, '秋': 8, '冬': 11}[m.group(1)]
    return None


def enc_ll(pts):
    out = []; lx = ly = 0; first = True; prev = None
    for lon, lat in pts:
        x, y = int(round(lon * 100)), int(round(lat * 100))
        if (x, y) == prev: continue
        if first: out += [x, y]; first = False
        else: out += [x - lx, y - ly]
        lx, ly = x, y; prev = (x, y)
    return out


def build(BASE, SEEDS):
    ITEMS = []

    def add(it):
        it = {k: v for k, v in it.items() if v is not None}
        it['i'] = len(ITEMS); ITEMS.append(it); return it['i']

    def near_seed(lon, lat):
        best, bd = None, .0009
        for i, s in enumerate(SEEDS):
            if s['t'] == 'r': continue
            d = (s['lon'] - lon) ** 2 + (s['lat'] - lat) ** 2
            if d < bd: best, bd = i, d
        return best

    # 都城取故城（汉长安城、邺城遗址、广固城）、州府点取今城，3 km 内找不到的：按州府点 id 连。
    # 广固：州府点 410 年前名广固，坐标却是其后的东阳城（相距 8 km）；连上只为当期都城处不重画，成了旧都后页面上照画旧都框
    sid = {s['id']: i for i, s in enumerate(SEEDS)}
    for c in CAP:
        assert c['st'] in UK, ('都城政权', c['st'])
        d = dict(c); d['st'] = UK[d['st']]
        d['at'] = sid[CAP_AT[d['old']]] if d['old'] in CAP_AT else near_seed(d['lon'], d['lat']); add(d)
    for b in BAT:
        d = dict(b); y = int(d['y']); d['y'] = y; d['m'] = month_of(y, d['yt']); add(d)
    for e in EV:
        d = dict(e); y = int(d['y']); d['y'] = y; d['m'] = month_of(y, d['yt']); add(d)
    # 关隘：唐宋图所收者只留 PASS 列出的，按语改写
    for it in IT.TS:
        if it['c'] != 'pass' or it['old'] not in IT.PASS: continue
        d = {k: it[k] for k in ('c', 'old', 'mod', 'lon', 'lat')}
        if it['old'] in IT.PASS_LL:
            v = IT.PASS_LL[it['old']]
            if v is None: continue
            d['lon'], d['lat'], d['mod'] = v
        d['note'] = IT.PASS[it['old']]
        add(d)
    for o, m, lon, lat, note in IT.NEWPASS: add(dict(c='pass', old=o, mod=m, lon=lon, lat=lat, note=note))
    # 山脉
    ts_map = {}
    for it in IT.TS:
        if it['c'] != 'range': continue
        d = dict(it); d.pop('i')
        if d['old'] == '大雪山': d['old'] = '大雪山（川西）'
        d['note'] = IT.RANGE_NOTE.get(it['old'], it.get('note', ''))
        ts_map[it['i']] = add(d)
    for o, m, note, geo, anc, major in IT.NEWRANGE:
        add(dict(c='range', old=o, mod=m, note=note, geo=[list(p) for p in geo], anc=list(anc), major=major))
    # 水系
    for it in IT.TS:
        if it['c'] != 'river' or it['old'] in IT.DEL_RIVER: continue
        d = dict(it); d.pop('i')
        d['note'] = IT.RIVER_NOTE.get(f"{it['old']}@{it.get('mod', '')}", IT.RIVER_NOTE.get(it['old'], it.get('note', '')))
        if it['old'] in IT.RIVER_FIX: d['old'], d['mod'] = IT.RIVER_FIX[it['old']]
        ts_map[it['i']] = add(d)
    anc_of = {}
    for r in BASE['rivers']:
        if r.get('key'): anc_of.setdefault(r['key'], []).extend(r['p'])
    key_item = {}
    for key, o, m, note, major in IT.NEWRIV:
        pts = anc_of.get(key)
        if not pts: print('  [条目] 底图缺河流', key); continue
        a = pts[len(pts) // 2]
        key_item[key] = add(dict(c='river', sub='river', old=o, mod=m, note=note, major=major, anc=[a[0], a[1]]))
    lake_item = {}
    for ne, o, m, note in IT.NEWLAKE:
        lk = [l for l in BASE['lakes'] if l.get('ne') == ne]
        if lk:
            c = Polygon(lk[0]['r']).representative_point()
            lake_item[ne] = add(dict(c='river', sub='lake', old=o, mod=m, note=note, major=False, anc=[round(c.x, 2), round(c.y, 2)]))
    # 运河：只收本期已有的
    for it in IT.TS:
        if it['c'] != 'canal' or it['old'] not in IT.CANAL: continue
        d = dict(it); d.pop('i')
        y0, note = IT.CANAL[it['old']]
        if it['old'] in IT.CANAL_NAME: d['old'], d['mod'] = IT.CANAL_NAME[it['old']]
        d['note'] = note; d['y0'] = y0
        ts_map[it['i']] = add(d)
    # 荒漠
    for it in IT.TS:
        if it['c'] != 'desert' or it['old'] in IT.DESERT_DROP: continue
        d = dict(it); d.pop('i'); d['note'] = IT.DESERT_NOTE.get(it['old'], it.get('note', ''))
        ts_map[it['i']] = add(d)
    desert_item = {}
    for d in BASE['deserts']:
        ne = d.get('ne')
        if ne in IT.NEWDESERT and ne not in desert_item:
            o, m, note = IT.NEWDESERT[ne]
            c = Polygon(d['r']).representative_point()
            desert_item[ne] = add(dict(c='desert', old=o, mod=m, note=note, anc=[round(c.x, 2), round(c.y, 2)]))
    # 行军与行程路线
    routes = []
    for R in ROUTES:
        pts = R['pts']
        mid = pts[len(pts) // 2]
        it = add(dict(c='route', old=R['old'], mod=R['mod'], note=R['note'], anc=[mid[0], mid[1]],
                      y=int(pts[0][2]), y1=int(pts[-1][2]), t0=round(pts[0][2], 4), t1=round(pts[-1][2], 4)))
        routes.append({'it': it, 'pts': [[x, y, round(t, 4), n] for x, y, t, n in pts]})
    # 诸族
    for p in PEOPLE: add(dict(c='people', **p))

    G = {'rivers': [], 'lakes': [], 'canals': [], 'deserts': [], 'regions': [], 'routes': routes}
    for r in BASE['rivers']:
        if r.get('ts_it') is not None:
            it = ts_map.get(r['ts_it'])
            if it is None: continue          # 删去的湖泽、河流
        else:
            it = key_item.get(r.get('key'))
        G['rivers'].append({'p': enc_ll(r['p']), 'k': r['k'], **({'it': it} if it is not None else {})})
    for lk in BASE['lakes']:
        if lk.get('ts_it') is not None:
            it = ts_map.get(lk['ts_it'])
            if it is None: continue
        else:
            it = lake_item.get(lk.get('ne'))
        G['lakes'].append({'r': enc_ll(lk['r']), **({'it': it} if it is not None else {})})
    for c in BASE['canals']:
        if c['ts_it'] in ts_map: G['canals'].append({'p': enc_ll(c['p']), 'it': ts_map[c['ts_it']]})
    for d in BASE['deserts']:
        it = ts_map.get(d['ts_it']) if d.get('ts_it') is not None else desert_item.get(d.get('ne'))
        if it is None: continue
        G['deserts'].append({'r': enc_ll(d['r']), 'it': it})
    return ITEMS, G
