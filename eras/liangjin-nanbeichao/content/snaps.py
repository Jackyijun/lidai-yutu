# 时间节点：每个节点在上一节点归属基础上改动（规范第六节）
#   own   {单位: [归属点或 '#组名']}：按书写顺序覆盖；同一节点里后写的优先
#   move  {旧单位: 新单位}：整体改归（如“晋”改“宋”）
#   drop  [归属点]：改为无主
#   pol   {单位: 所属政权}：二级单位（方镇）在“政权”着色下并入哪个政权
#   lab   {单位: 当年别名}；seat {单位: 治所归属点}；h [加斜线的单位]（名义臣属、实则自立），给出即整体替换
#   kd    {单位: 种类}：从本节点起改按此种类画（高句丽 313 年起由部族改按政权画）
#   junction 'hanmo' / 'suitang'：衔接节点，邻卷范围内的归属与疆域照搬邻卷（规范第十八节）
from seeds import SEEDS, SID
from groups import G

BYREG = {}
for s in SEEDS: BYREG.setdefault(s['reg'], []).append(s['id'])


def expand(lst):
    out = []
    for x in lst:
        if x.startswith('#'):
            k = x[1:]
            assert k in G or k in BYREG, x
            out += G.get(k) or BYREG[k]
        else:
            assert x in SID, x
            out.append(x)
    return out


NODES = []


def node(y, era, t, d, own=None, pol=None, lab=None, seat=None, h=None, drop=None, move=None, kd=None, era2='', junction=None):
    NODES.append(dict(y=y, era=era, era2=era2, t=t, d=d.strip(), own=own or {}, pol=pol or {}, lab=lab or {}, seat=seat or {},
                      h=h, drop=drop or [], move=move or {}, kd=kd or {}, junction=junction))


FIRST = 401   # 首屏节点（年份）

from snaps_xijin import *      # noqa: E402,F401,F403  280—316
from snaps_dongjin import *    # noqa: E402,F401,F403  317—383
from snaps_shiliu import *     # noqa: E402,F401,F403  384—439
from snaps_nanbei import *     # noqa: E402,F401,F403  440—581
