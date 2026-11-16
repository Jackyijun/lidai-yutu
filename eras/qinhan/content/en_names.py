# -*- coding: utf-8 -*-
"""地名、郡国名的英文（拼音）。NAMES 由 tools/en_names.py 生成后手改；缺的由 name() 临时拼出并在构建时提醒。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jun import en_unit  # noqa: E402

NAMES = {}
try:
    from en_names_data import NAMES  # noqa: F401,E402
except ImportError:
    pass

MISSING = set()


def py(s):
    if s in NAMES:
        return NAMES[s]
    try:
        from pypinyin import lazy_pinyin
        sy = lazy_pinyin(s, v_to_u=True)       # 隔音符：a、o、e 开头的音节前加 '
        return "".join(("'" + x) if i and x[:1] in "aoe" else x for i, x in enumerate(sy)).capitalize()
    except ImportError:
        MISSING.add(s)
        return s


def name(n):
    if n in NAMES:
        return NAMES[n]
    if n.endswith(("郡", "国", "尹", "属国")) or n in ("左冯翊", "右扶风", "内史"):
        return en_unit(n, py)
    return py(n)
