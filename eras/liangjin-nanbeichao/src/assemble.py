# 并入英文、检查缺译（无 content/en/ 时只出中文版），把 build/out_data.json 汇编成本卷的 source.json（单仓第 1 段的产物）
#   python src/assemble.py           严格：有缺译或过期的英文就报错退出
#   python src/assemble.py --draft   草稿：缺译、过期处临时显示中文，只给警告
# source.json 是旧版页面里内嵌的 GEO、DATA，不含疆域与配色：疆域由统一疆域引擎推算（本卷的 engine.json），
# 颜色由单仓的 global/palette.toml 定，新页面由单仓 core/web/ 生成（架构整理第三批起本卷不再出页面）。
import json, sys
from collections import Counter
import config as C
import i18n
sys.path.insert(0, str(C.ROOT.parent.parent / 'core' / 'v1'))
import legacy


def check_english(geo, data, draft):
    missing, stale, unlocked = i18n.check(geo, data)
    bad = missing + stale
    if unlocked:
        print(f'  [英文] 提醒：{len(unlocked)} 条英文未登记指纹（改完英文后运行 python tools/i18n.py lock）')
    if not bad:
        print('  [英文] 齐全')
        return
    msg = (f'英文缺译 {len(missing)} 条、过期 {len(stale)} 条：'
           + '、'.join(f'{f} {n}' for f, n in Counter(f for f, _, _ in bad).items())
           + '。运行 python tools/i18n.py todo 查看清单。')
    if not draft:
        sys.exit('  [英文] ' + msg + '\n  如只想先看效果，用 python run.py --html --draft（缺译处显示中文）。')
    print('  [英文] 草稿模式，' + msg)


def main(draft=False):
    D = json.load(open(C.BUILD / 'out_data.json', encoding='utf-8'))
    if i18n.EN.exists():
        check_english(D['GEO'], D['DATA'], draft)
        D['GEO'], D['DATA'] = i18n.attach(D['GEO'], D['DATA'])
    else:                                   # 第一轮只交中文：没有 content/en/ 时不查缺译，界面隐藏「中 | EN」
        D['DATA']['noen'] = 1
        print('  [英文] 暂无 content/en/，只出中文版')
    out = C.ROOT / 'source.json'
    legacy.write_source(out, D['GEO'], D['DATA'], inline=False)    # 旧版页面的疆域环存在几何池 GEO.pool 里，新页面照旧
    print(f'  [source.json] {out.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main(draft='--draft' in sys.argv[1:])
