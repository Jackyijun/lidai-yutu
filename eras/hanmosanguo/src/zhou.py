# -*- coding: utf-8 -*-
"""郡国、州的归属：某年某地属哪个州（220 年前东汉十三州，三国按魏蜀吴各自的州，晋按太康十九州）。

src/build.py 用它给「单位 × 州」分块画州界；统一疆域引擎（第 7 步）用 zone_of 做同样的分块
（era.toml 的 [engine] zones = "src/zhou.py"）。
"""
import importlib.util
import sys
from pathlib import Path

_SEEDS = Path(__file__).resolve().parent.parent / "content" / "seeds.py"
_m = sys.modules.get("seeds")
if _m is not None and Path(getattr(_m, "__file__", "")).resolve() == _SEEDS:
    SEEDS = _m.SEEDS                                  # build.py 已载入本卷的 content/seeds.py
else:                                                 # 统一引擎里单独载入，免得与别卷同名的 seeds 模块相混
    _spec = importlib.util.spec_from_file_location("hanmosanguo_seeds", _SEEDS)
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
    SEEDS = _m.SEEDS

JUN = {s["id"]: s for s in SEEDS if s["t"] == "z"}
STATES = ("汉", "曹", "刘备", "孙", "晋")        # 州界只在这几个政权内部画


def jun_of(s):
    return s["id"] if s["t"] == "z" else (s["j"] if s["j"] in JUN else None)

def zhou_han(s):
    j = jun_of(s)
    return JUN[j]["j"] if j else None

WEI = {"河南尹": "司州", "河内郡": "司州", "河东郡": "司州", "弘农郡": "司州",
       "京兆尹": "雍州", "左冯翊": "雍州", "右扶风": "雍州", "汉阳郡": "雍州", "陇西郡": "雍州", "安定郡": "雍州", "北地郡": "雍州", "武都郡": "雍州", "阴平": "雍州"}
JIN = {"河南尹": "司州", "河内郡": "司州", "河东郡": "司州", "弘农郡": "司州", "魏郡": "司州",
       "京兆尹": "雍州", "左冯翊": "雍州", "右扶风": "雍州", "安定郡": "雍州", "北地郡": "雍州",
       "汉阳郡": "秦州", "陇西郡": "秦州", "武都郡": "秦州", "阴平": "秦州",
       "汉中郡": "梁州", "巴郡": "梁州", "广汉郡": "梁州",
       "益州郡": "宁州", "永昌郡": "宁州",
       "辽东郡": "平州", "玄菟郡": "平州", "乐浪郡": "平州", "辽东属国": "平州",
       "平原郡": "冀州", "南海郡": "广州", "苍梧郡": "广州", "郁林郡": "广州"}
SEED_JIN = {"始安": "广州", "曲江": "广州", "临贺": "广州", "上庸": "荆州", "房陵": "荆州", "西城": "荆州"}
SEED_WEI = {"上庸": "荆州", "房陵": "荆州", "西城": "荆州"}

def zhou_of(s, y, owner_k):
    """某年某地属哪个州：220 年前用东汉十三州，三国用魏蜀吴各自的州，晋用太康十九州。"""
    j = jun_of(s)
    if not j: return None
    han = JUN[j]["j"]
    if y < 220: return han
    if y < 265:
        if owner_k == "刘备": return "益州"
        if owner_k == "孙":
            if han == "交州" and y >= 264 and j in ("南海郡", "苍梧郡", "郁林郡"): return "广州"
            return han
        return SEED_WEI.get(s["id"]) or WEI.get(j) or han
    if owner_k == "孙":
        if han == "交州" and (j in ("南海郡", "苍梧郡", "郁林郡") or s["id"] in ("临贺",)): return "广州"
        if s["id"] in ("始安", "曲江"): return "广州"
        return han
    return SEED_JIN.get(s["id"]) or JIN.get(j) or han


BY_ID = {s["id"]: s for s in SEEDS}


def zone_of(place, y, unit, polity, kind):
    """统一引擎：某年某点所在的州块 (州, 政权)，与 build.py 的分块相同；部族、弃地、不属郡的点为 None"""
    if not unit or kind in ("tribe", "waste"):
        return None
    s = BY_ID.get(place)
    zh = zhou_of(s, y, unit) if s else None
    if not zh:
        return None
    return (zh, polity if polity in STATES else ("汉" if y < 220 else polity))
