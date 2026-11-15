# 从相邻两卷的成品页面提取衔接节点（规范第十八节），写入 geodata/：
#   python tools/junction.py ../hanmosanguo-map ../suitang-map
# 汉末三国图取末节点（280），隋及唐初图取首节点（581）：各政权的疆域环、注记点、名称、颜色与当年别名；
# 隋唐图另记它的外缘（content/frontier.py），本图 581 节点在此外缘内照搬隋唐图。
# 两卷改了衔接节点后重跑此脚本，再 python run.py 重建。
import hashlib, json, re, sys
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent


def load_page(p):
    s = p.read_text(encoding='utf-8')
    out = {}
    for name in ('GEO', 'DATA'):
        m = re.search(r'const %s\s*=\s*' % name, s)
        out[name], _ = json.JSONDecoder().raw_decode(s[m.end():])
    i = s.find('--u-0:'); light = dict(re.findall(r'--u-(\d+):(#[0-9A-Fa-f]{6})', s[i:s.find('}', i)]))
    j = s.find('--u-0:', i + 10); dark = dict(re.findall(r'--u-(\d+):(#[0-9A-Fa-f]{6})', s[j:s.find('}', j)]))
    return out, light, dark, hashlib.sha256(p.read_bytes()).hexdigest()


def extract(repo, idx):
    page = repo / 'docs' / 'index.html'
    o, light, dark, digest = load_page(page)
    G, D = o['GEO'], o['DATA']
    sn = G['snaps'][idx]
    U = D['units']
    units = {}
    for k, v in sn['z'].items():
        u = U[int(k)]
        units[u['k']] = dict(n=u['n'], kind=u['kind'], light=light[k], dark=dark[k], lab=sn['lab'].get(k),
                             rings=G['pool'][v] if isinstance(v, int) else v, label=sn['lz'].get(k))
    return dict(src=f'{repo.name}/docs/index.html', sha256=digest, y=sn['y'], m=sn.get('m'), t=sn['t'], units=units,
                h=[U[i]['k'] for i in sn['h']])


def main(hanmo, suitang):
    hanmo, suitang = Path(hanmo).resolve(), Path(suitang).resolve()
    a = extract(hanmo, -1)
    a['frame'] = 'box'
    json.dump(a, open(ROOT / 'geodata' / 'junction_hanmo280.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    b = extract(suitang, 0)
    spec = importlib.util.spec_from_file_location('st_frontier', suitang / 'content' / 'frontier.py')
    fr = importlib.util.module_from_spec(spec); spec.loader.exec_module(fr)
    b['frame'] = [[round(float(x), 4), round(float(y), 4)] for x, y in fr.outer_lonlat()]
    json.dump(b, open(ROOT / 'geodata' / 'junction_suitang581.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('  [衔接]', a['y'], len(a['units']), '个政权；', b['y'], len(b['units']), '个政权')


if __name__ == '__main__':
    main(*sys.argv[1:3])
