# -*- coding: utf-8 -*-
"""v1 数据包：各卷第 1 段的产物 eras/<短名>/source.json → v1（附全局 ID）→ build/v1/<短名>.json（规范第十九节）。

  python core/v1/build.py              各卷全部
  python core/v1/build.py songyuan     只做这几卷
  python core/v1/build.py --lenient    eras/<短名>/engine.json 过期或还没有时不停下，这一遍先不带疆域（run.py 重算疆域之前用：
                                       引擎读的就是这一遍的归属）

每一卷：
  1. 往返校验：v1 转回旧格式，除疆域几何与配色外必须与 source.json 完全相同；
  2. 核对 eras/<短名>/era.toml（时间精度、节点数、首屏节点）与数据一致；
  3. 按 global/ 各表给政权、地点、山川条目附上全局 ID（字段 gid）；
  4. 坐标改正（core/v1/overlay.py 的 apply_coords：条目点位与归属点，按全局地点表的城址）；
  5. 疆域换成 eras/<短名>/engine.json（core/v1/engine_geom.py），它是按改后的归属点算的；秦汉卷的疆域在它自己的 source.json 里；
     对方为准的衔接节点上，对方推算范围以内各点的归属按照搬来的疆域对齐（engine_geom.align_own，原归属存在 own_src）；
  6. 其余改正（core/v1/overlay.py：英文译名、山脉改画、标了 step = 3 的内容、时间轴短标题、全局配色、大漠），记在 meta.overlay。
global/ 各表与 build/v1/fixes.json 须先由 core/v1/registry.py 生成；本脚本只读不写。build/ 不入库。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine_geom
import overlay
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
        if p.get("global") is False:               # 春秋、战国的分区点不进全局表，没有全局 ID
            continue
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
    lenient = "--lenient" in sys.argv
    slugs = [a for a in sys.argv[1:] if not a.startswith("--")] or ERAS
    bad = [s for s in slugs if s not in ERAS]
    if bad:
        sys.exit(f"没有这一卷：{'、'.join(bad)}")
    if not (GLOBAL / "places.jsonl").exists():
        sys.exit("global/ 下还没有全局表，先运行 python core/v1/registry.py")
    pl = index(read_jsonl(GLOBAL / "places.jsonl"))
    po = index(read_jsonl(GLOBAL / "polities.jsonl"))
    ph = index(read_jsonl(GLOBAL / "physical.jsonl"))
    seats = seat_index(read_jsonl(GLOBAL / "places.jsonl"))
    fx = OUT / "fixes.json"
    if not fx.exists():
        sys.exit("build/v1/fixes.json 不存在，先运行 python core/v1/registry.py")
    fixes = json.loads(fx.read_text(encoding="utf8"))
    content = load_toml(GLOBAL / "corrections.toml").get("fix", [])
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
        c = overlay.apply_coords(slug, b, fixes.get("coords", []))
        eg = engine_geom.apply(slug, b, strict=not lenient)
        al = engine_geom.align_own(slug, b)
        b["meta"]["overlay"] = ([f"坐标 {c} 处"] if c else []) + ([eg] if eg else []) + ([al] if al else []) + overlay.apply(slug, b, fixes, content)
        path = OUT / f"{slug}.json"
        path.write_text(json.dumps(b, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
        size = path.stat().st_size / 1e6
        print(f"{slug:20s} {'通过' if not probs else '有问题'}  {size:5.1f} MB → build/v1/{slug}.json")
        for d in b["meta"]["overlay"]:
            print("      改正：", d)
        for p in probs:
            print("    ", p)
        failed += bool(probs)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
