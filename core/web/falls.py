"""灭国表：eras/<卷>/content/falls.tsv → 页面的 DATA.falls（规范第八节「本期新亡」）

九卷同一种写法，一行一条，制表符分隔，第一行是列名：

  年份      前205·10、约前180、622、1945·8（「约」表示约数；「·月」可省，民国写到月）。
            秦汉按本卷的通鉴纪年写（前205·10 即汉二年十月，同节点标签）
  键        地图上的单位名（与本卷单位的中文名一字不差），一条涉及几国用「、」隔开
  方式      灭 篡 废 亡 分裂 降 内属 臣服 并
  标题      年表里的标题，如「西楚亡」「张鲁降」「契丹内属」；用当期图例上的名字
  经过      一句话，年表正文
  年表      是 / 否：年表里已有一行讲同一件事、同一时间（战役或事件写到了结局、都城一行同时写了，
            或节点标题点了它）时写「否」，这条只用来划图例
  title_en  英文标题
  text_en   英文正文（中英同在一行，改中文时顺手改英文；两列都不能空）

字段里的引号照原样读（不按 CSV 的引号规则）；文件可带 BOM（Excel 另存的）。

页面怎么用：图例里上一节点在、这一节点不在、表里又有它的国，灰字划掉（悬停显示标题与年份）；
年表照「年表」一列收进标题与经过，点击跳到这一国在地图上消失的那个节点。地图本身不受影响。
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOW = ("灭", "篡", "废", "亡", "分裂", "降", "内属", "臣服", "并")
COLS = ("年份", "键", "方式", "标题", "经过", "年表", "title_en", "text_en")
YEAR = re.compile(r"^(约)?(前)?(\d+)(?:[·.](\d{1,2}))?$")


def path(slug):
    return ROOT / "eras" / slug / "content" / "falls.tsv"


def parse_year(s):
    """'约前205·10' → (约数, 年, 月或 None)"""
    m = YEAR.match(s.strip())
    if not m:
        raise ValueError(f"年份写法不对：{s!r}")
    yr = int(m.group(3)) * (-1 if m.group(2) else 1)
    mo = int(m.group(4)) if m.group(4) else None
    if mo is not None and not 1 <= mo <= 12:
        raise ValueError(f"月份不对：{s!r}")
    return bool(m.group(1)), yr, mo


def tval(yr, mo, time):
    """换成本卷节点的时间值，年表据此排序、图例据此找最近的节点"""
    if time == "t":                      # 民国：公历月序 年×12+月−1
        return yr * 12 + ((mo or 6) - 1)
    if time == "qinhan":                 # 秦汉：月序；太初改历（前104）以前十月起算新年，故十至十二月属上一公历年
        cy = yr - 1 if mo and mo >= 10 and yr - 1 < -104 else yr
        return cy * 12 + ((mo or 6) - 1)
    if time == "ym":                     # 两晋、隋唐：年 + 月/12（节点为该月之末）
        return yr + ((mo - .5) / 12 if mo else .5)
    return yr                            # 其余按年


def read(slug):
    """读表，返回 [dict(列名→值)]；没有表返回 []"""
    p = path(slug)
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))
    if not rows or tuple(rows[0]) != COLS:
        raise ValueError(f"{p}：第一行应为 {' '.join(COLS)}")
    out = []
    for n, r in enumerate(rows[1:], 2):
        if not any(c.strip() for c in r):
            continue
        if len(r) != len(COLS):
            raise ValueError(f"{p} 第 {n} 行：应有 {len(COLS)} 列，实有 {len(r)} 列")
        out.append(dict(zip(COLS, (c.strip() for c in r)), _line=n))
    return out


def load(slug, units, time):
    """DATA.falls：[{yr, mo, ca, t, ks, how, ti, tie, p, pe, chron}]，按时间排"""
    ix = {}
    for i, u in enumerate(units):
        ix.setdefault(u["n"], []).append(i)
    out = []
    for r in read(slug):
        where = f"{slug} falls.tsv 第 {r['_line']} 行"
        ca, yr, mo = parse_year(r["年份"])
        ks = []
        for k in r["键"].split("、"):
            hit = ix.get(k)
            if not hit:
                raise ValueError(f"{where}：没有叫「{k}」的单位")
            if len(hit) > 1:
                raise ValueError(f"{where}：「{k}」有重名单位")
            ks.append(hit[0])
        if r["方式"] not in HOW:
            raise ValueError(f"{where}：方式应为 {'、'.join(HOW)} 之一")
        if r["年表"] not in ("是", "否"):
            raise ValueError(f"{where}：年表一列应为 是 或 否")
        if not (r["标题"] and r["经过"]):
            raise ValueError(f"{where}：标题、经过不能空")
        if not (r["title_en"] and r["text_en"]):
            raise ValueError(f"{where}：英文标题、英文正文不能空（页面英文界面要用）")
        f = {"yr": yr, "t": tval(yr, mo, time), "ks": ks, "how": r["方式"], "ti": r["标题"], "p": r["经过"]}
        if mo:
            f["mo"] = mo
        if ca:
            f["ca"] = 1
        f["tie"] = r["title_en"]
        f["pe"] = r["text_en"]
        if r["年表"] == "否":
            f["chron"] = False
        out.append(f)
    out.sort(key=lambda f: f["t"])
    return out
