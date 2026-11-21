# -*- coding: utf-8 -*-
"""往返校验：eras/<短名>/source.json → v1 → 旧格式，除疆域几何与配色外必须与 source.json 完全相同。

source.json 没有疆域几何（秦汉卷除外）与疆域色：转回来的旧格式里，几何来自 v1（这时还是空的）、颜色来自 v1 的政权
（这时还没套 global/palette.toml），所以比之前把 source.json 里没有的几何键、DATA.colors 去掉。"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import legacy

ROOT = Path(__file__).resolve().parents[2]


def diff(a, b, path="", out=None, limit=8):
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if type(a) != type(b):
        out.append(f"{path}: 类型 {type(a).__name__} ≠ {type(b).__name__}")
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append(f"{path}/{k}: {'缺' if k not in b else '多'}")
            else:
                diff(a[k], b[k], f"{path}/{k}", out, limit)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f"{path}: 长度 {len(a)} ≠ {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}[{i}]", out, limit)
    elif a != b:
        out.append(f"{path}: {str(a)[:60]} ≠ {str(b)[:60]}")
    return out


def check(slug):
    G, D, form = legacy.load(slug)
    b = legacy.to_v1(slug, G, D, form.get("inline"))
    b = json.loads(json.dumps(b, ensure_ascii=False))       # 经过一次 JSON，确保可序列化
    G2, D2, _ = legacy.from_v1(b)
    for sn, sn2 in zip(G["snaps"], G2["snaps"]):
        for k in legacy.GEOM_KEYS:
            if k not in sn:
                sn2.pop(k, None)
    if "pool" not in G:
        G2.pop("pool", None)
    if "colors" not in D:
        D2.pop("colors", None)
    problems = diff(G, G2, "GEO") + diff(D, D2, "DATA")
    return b, problems


if __name__ == "__main__":
    slugs = sys.argv[1:] or ["chunqiu", "zhanguo", "qinhan", "hanmosanguo", "liangjin-nanbeichao", "suitang", "tangsong", "songyuan", "minguo-xinzhongguo"]
    bad = 0
    for s in slugs:
        b, probs = check(s)
        print(f"{s:20s} {'无损' if not probs else '有差异'}  节点 {len(b['nodes'])} 政权 {len(b['polities'])} 地点 {len(b['places'])} 条目 {len(b['items'])} 几何 {len(b['geom'])}")
        for p in probs:
            print("    ", p)
        bad += bool(probs)
    sys.exit(1 if bad else 0)
