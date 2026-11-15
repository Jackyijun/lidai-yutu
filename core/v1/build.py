# -*- coding: utf-8 -*-
"""v1 数据包：成品页面 → v1（附全局 ID）→ build/v1/<短名>.json（规范第十九节第 2 步）。

  python core/v1/build.py              八卷全部
  python core/v1/build.py songyuan     只做这几卷

每一卷：
  1. 往返校验：v1 转回旧格式，必须与成品里的 GEO、DATA、疆域色完全相同；
  2. 核对 eras/<短名>/era.toml（时间精度、数据模型、节点数、首屏节点）与数据一致；
  3. 按 global/ 各表给政权、地点、山川条目附上全局 ID（字段 gid）。
global/ 各表须先由 core/v1/registry.py 生成；本脚本只读不写。build/ 不入库。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roundtrip
from registry import ERAS, GLOBAL, ROOT, load_toml

OUT = ROOT / "build" / "v1"


def read_jsonl(p):
    with open(p, encoding="utf8") as f:
        return [json.loads(line) for line in f if line.strip()]


def index(rows):
    return {r: row["id"] for row in rows for r in row["refs"]}


def seat_index(rows):
    """治所迁城的州府：ref → [[起始月序号, 全局 ID], …]，按时间排"""
    out = {}
    for row in rows:
        for st in row.get("seats", []):
            out.setdefault(st["ref"], []).append([st["from"] * 12, row["id"]])
    return {k: sorted(v) for k, v in out.items()}


def check_era_toml(slug, b):
    meta = load_toml(ROOT / "eras" / slug / "era.toml")
    probs = []
    if meta["slug"] != slug:
        probs.append(f"era.toml 的 slug 是 {meta['slug']}")
    if meta["time"] != b["time"]:
        probs.append(f"era.toml 时间精度 {meta['time']}，数据是 {b['time']}")
    if meta["model"] != b["model"]:
        probs.append(f"era.toml 数据模型 {meta['model']}，数据是 {b['model']}")
    if meta["nodes"] != len(b["nodes"]):
        probs.append(f"era.toml 节点数 {meta['nodes']}，数据有 {len(b['nodes'])}")
    f = meta["first"]
    want = f[0] * 12 + f[1] - 1 if isinstance(f, list) else f * 12 + 11
    if want != b["first"]:
        probs.append(f"era.toml 首屏 {f}，数据是月序号 {b['first']}")
    y0, y1 = meta["years"]
    ts = [n["t"] for n in b["nodes"]]
    if min(ts) // 12 < y0 - 200 or max(ts) // 12 > y1:     # 首个节点可以是前代背景（如汉末卷的东汉鼎盛）
        probs.append(f"节点时间 {min(ts) // 12}—{max(ts) // 12} 超出 era.toml 起止 {y0}—{y1}")
    return meta, probs


def attach(slug, b, pl, po, ph, seats):
    missing = []
    for p in b["polities"]:
        ref = f"{slug}:{p['key']}"
        p["gid"] = po.get(ref) or missing.append(ref)
    for p in b["places"]:
        ref = f"{slug}:{p['key']}"
        # 治所迁城的：gid 是按年代分段的列表 [[起始月序号, 全局 ID], …]
        p["gid"] = pl.get(ref) or seats.get(ref) or missing.append(ref)
    for it in b["items"]:
        ref = f"{slug}:i:{it['i']}"
        if it["c"] in ("capital", "pass") and "lon" in it:
            it["gid"] = pl.get(ref) or missing.append(ref)
        elif ref in ph:
            it["gid"] = ph[ref]
        elif ref in pl:
            it["gid"] = pl[ref]
    return [m for m in missing if m]


def main():
    slugs = sys.argv[1:] or ERAS
    bad = [s for s in slugs if s not in ERAS]
    if bad:
        sys.exit(f"没有这一卷：{'、'.join(bad)}")
    if not (GLOBAL / "places.jsonl").exists():
        sys.exit("global/ 下还没有全局表，先运行 python core/v1/registry.py")
    pl = index(read_jsonl(GLOBAL / "places.jsonl"))
    po = index(read_jsonl(GLOBAL / "polities.jsonl"))
    ph = index(read_jsonl(GLOBAL / "physical.jsonl"))
    seats = seat_index(read_jsonl(GLOBAL / "places.jsonl"))
    OUT.mkdir(parents=True, exist_ok=True)
    failed = 0
    for slug in slugs:
        b, probs = roundtrip.check(slug)
        meta, p2 = check_era_toml(slug, b)
        probs += p2
        missing = attach(slug, b, pl, po, ph, seats)
        if missing:
            probs.append(f"{len(missing)} 条在全局表里查不到（全局表过期？先运行 registry.py）：{'、'.join(missing[:5])}")
        b["meta"] = {k: meta[k] for k in ("volume", "title", "title_en", "short", "short_en", "years")}
        path = OUT / f"{slug}.json"
        path.write_text(json.dumps(b, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
        size = path.stat().st_size / 1e6
        print(f"{slug:20s} {'通过' if not probs else '有问题'}  {size:5.1f} MB → build/v1/{slug}.json")
        for p in probs:
            print("    ", p)
        failed += bool(probs)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
