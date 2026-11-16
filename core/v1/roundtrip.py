# -*- coding: utf-8 -*-
"""往返校验：成品页面 → v1 → 旧格式，必须与原来的 GEO、DATA、疆域色完全相同。"""
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
    html = (ROOT / "eras" / slug / "legacy.html").read_text(encoding="utf8")
    G, D, colors = legacy.extract(html)
    b = legacy.to_v1(slug, G, D, colors)
    b = json.loads(json.dumps(b, ensure_ascii=False))       # 经过一次 JSON，确保可序列化
    G2, D2, c2 = legacy.from_v1(b)
    problems = diff(G, G2, "GEO") + diff(D, D2, "DATA")
    if b["_legacy"]["fam"] == "B" and colors != c2:
        problems.append("疆域色不同")
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
