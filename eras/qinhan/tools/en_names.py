# -*- coding: utf-8 -*-
"""重新生成 content/en_names_data.py：郡国名与没有英文的地名的拼音（需要 pypinyin）。生成后多音字等照 FIX 改。

  python tools/en_names.py      先 python run.py 出一遍 build/data.json
"""
import json
import sys
from pathlib import Path

from pypinyin import lazy_pinyin

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "content"))
from jun import en_unit  # noqa: E402

FIX = {"会稽": "Kuaiji", "觻得": "Lude", "且虑": "Julü", "菑川": "Zichuan", "千乘": "Qiancheng", "车师": "Jushi", "犍为": "Qianwei",
       "牂柯": "Zangke", "牂牁": "Zangke", "越嶲": "Yuexi", "越巂": "Yuexi", "枹罕": "Fuhan", "番和": "Panhe", "句町": "Gouding",
       "句章": "Gouzhang", "沓氏": "Tashi", "栎阳": "Yueyang", "下邳": "Xiapi", "僰道": "Bodao", "琅邪": "Langye", "乐浪": "Lelang",
       "乐安": "Le'an", "朱提": "Zhuti", "允吾": "Yunwu", "番禺": "Panyu", "单于庭": "The chanyu's court", "龟兹": "Kucha",
       "大宛": "Dayuan", "六安": "Lu'an", "六": "Lu", "郯": "Tan", "郴": "Chen", "鄗": "Hao", "盱眙": "Xuyi", "阆中": "Langzhong",
       "宕渠": "Dangqu", "鱼复": "Yufu", "涪": "Fu", "涪陵": "Fuling", "麊泠": "Miling", "咸驩": "Xianhuan", "卢容": "Lurong",
       "象林": "Xianglin", "番和县": "Panhe", "氐道": "Didao", "狄道": "Didao", "冥安": "Ming'an", "令居": "Lingju", "居延": "Juyan",
       "朝歌": "Zhaoge", "襄国": "Xiangguo", "废丘": "Feiqiu", "高奴": "Gaonu", "邾": "Zhu", "博阳": "Boyang", "王险城": "Wangxian",
       "羸𨻻": "Leilou", "瞫都": "Tandu", "霅": "Zha", "东暆": "Dongyi", "笮都": "Zuodu", "胥浦": "Xupu", "且兰": "Qielan",
       "毋敛": "Wulian", "定莋": "Dingzuo", "会无": "Huiwu", "叶榆": "Yeyu", "博南": "Bonan", "哀牢": "Ailao", "滇池": "Dianchi", "信都": "Xindu", "武都": "Wudu", "儋耳": "Dan'er"}


def py(s):
    if s in FIX:
        return FIX[s]
    for k in sorted(FIX, key=len, reverse=True):
        if k in s and len(k) >= 2:
            rest = s.replace(k, "\0")
            parts = rest.split("\0")
            return FIX[k].join("".join(lazy_pinyin(p)) for p in parts).capitalize() if parts[0] == "" else \
                ("".join(lazy_pinyin(parts[0])) + FIX[k].lower() + "".join(lazy_pinyin(parts[1]))).capitalize()
    return "".join(lazy_pinyin(s)).capitalize()


def main():
    D = json.loads((ROOT / "build" / "data.json").read_text(encoding="utf8"))
    names = {}
    for u in D["units"]:
        if u["kind"] == "zhen":
            n = u["n"]
            names[n] = en_unit(n, py)
    for s in D["seeds"]:
        if s["t"] != "r":
            names.setdefault(s["n"], py(s["n"]))
    for k, v in FIX.items():
        names.setdefault(k, v)
    out = "# -*- coding: utf-8 -*-\n# 由 tools/en_names.py 生成（pypinyin + 多音字表），可以手改\nNAMES = {\n"
    out += "".join(f"    {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)},\n" for k, v in sorted(names.items()))
    out += "}\n"
    (ROOT / "content" / "en_names_data.py").write_text(out, encoding="utf8")
    print(len(names), "个名字 → content/en_names_data.py")


if __name__ == "__main__":
    main()
