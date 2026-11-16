# -*- coding: utf-8 -*-
"""地形晕渲：Natural Earth 1:10m Shaded Relief → 各卷的分档晕渲图（geodata/relief/<短名>/，入库）。

  python core/geo/relief.py [短名 ...]     不写短名则八卷全做；需要先有 build/v1/<短名>.json

原图（SR_HR.zip，约 42 MB）不入库：第一次运行时下载到 build/raw/ 并校验 sha256，解压后存一份 .npy 备用。
网络不通时，手动下载 config.toml 里 [relief] source 那个文件放到 build/raw/ 即可。

做法（参数都在 core/geo/config.toml）：
  · 分辨率按地区定、不按卷定。每一档在统一投影平面上有一套全局像素格（第 i 列像素中心 x = (i + .5) × 步长），
    各卷只是从里面取一块，所以同一个地方在哪一卷都是同样的灰度，等于从一张总图里裁剪。
  · 档三取全球；档一、档二只取本卷「全图」范围以内的部分，在自己那一块的边上留 1° 透明度渐变，盖在粗档上。
  · 灰度编成 hard-light 用：平地 = 128，阴坡 < 128，阳坡 > 128；页面里几张图先普通叠成一张，再整体 hard-light 混合。
  · 粗档里被细档完全盖住的像素改成平地（省体积，看不出差别）。
"""
import hashlib, io, json, math, sys, urllib.request, zipfile
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import geo

ROOT = geo.ROOT
RAW = ROOT / "build" / "raw"
V1 = ROOT / "build" / "v1"
_CACHE = {}


def source():
    """返回原图数组（行 = 纬度自北向南，列 = 经度自西向东，1′ 一格）。"""
    if "sr" in _CACHE: return _CACHE["sr"]
    cfg = geo.load()["relief"]
    RAW.mkdir(parents=True, exist_ok=True)
    z = RAW / Path(cfg["source"]).name
    npy = RAW / "SR_HR.npy"
    if not z.exists():
        print("下载", cfg["source"])
        urllib.request.urlretrieve(cfg["source"], z.with_suffix(".part"))
        z.with_suffix(".part").replace(z)
    h = hashlib.sha256(z.read_bytes()).hexdigest()
    if h != cfg["sha256"]:
        sys.exit(f"{z.name} 校验失败：{h}（应为 {cfg['sha256']}）")
    if not npy.exists():
        Image.MAX_IMAGE_PIXELS = None
        with zipfile.ZipFile(z) as zf:
            name = next(n for n in zf.namelist() if n.lower().endswith(".tif"))
            a = np.asarray(Image.open(io.BytesIO(zf.read(name))))
        np.save(npy, a)
    _CACHE["sr"] = np.load(npy, mmap_mode="r")
    return _CACHE["sr"]


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def isect(a, b):
    r = (max(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), min(a[3], b[3]))
    return r if r[0] < r[1] and r[2] < r[3] else None


def bbox(lo0, lo1, la0, la1, n=200):
    t = np.linspace(0, 1, n)
    lon = np.concatenate([lo0 + (lo1 - lo0) * t, np.full(n, lo1), lo1 + (lo0 - lo1) * t, np.full(n, lo0)])
    lat = np.concatenate([np.full(n, la1), la1 + (la0 - la1) * t, np.full(n, la0), la0 + (la1 - la0) * t])
    x, y = geo.proj(lon, lat)
    return x.min(), y.min(), x.max(), y.max()


def sample(sr, lon, lat, km, region):
    """按目标像素大小先模糊再双线性取值。范围跨度超过 180° 时用 4 倍下采样的全球原图，经度回绕。"""
    if region[1] - region[0] > 180:
        key = ("blur", km)
        if key not in _CACHE:
            a = np.asarray(sr, dtype=np.float32)
            d4 = a.reshape(a.shape[0] // 4, 4, a.shape[1] // 4, 4).mean(axis=(1, 3))
            sig = max(0.0, 0.5 * km / 7.4 - .3)
            _CACHE[key] = ndimage.gaussian_filter(d4, sig, mode=("nearest", "wrap")) if sig > 0 else d4
        win = _CACHE[key]
        lw = (lon + 180) % 360 - 180
        return ndimage.map_coordinates(win, [(90 - lat) * 15 - .5, (lw + 180) * 15 - .5], order=1, mode="nearest")
    lo0, lo1, la0, la1 = region
    c0, c1 = max(int((lo0 - 1 + 180) * 60), 0), int((lo1 + 1 + 180) * 60)
    r0, r1 = max(int((90 - la1 - 1) * 60), 0), int((90 - la0 + 1) * 60)
    win = np.asarray(sr[r0:r1, c0:c1], dtype=np.float32)
    src_km = 1.853 * math.cos(math.radians(min(abs(la0), abs(la1)) if la0 * la1 > 0 else 0))
    sig = max(0.0, 0.5 * km / max(src_km, .5) - .3)
    if sig > 0: win = ndimage.gaussian_filter(win, sig)
    return ndimage.map_coordinates(win, [(90 - lat) * 60 - .5 - r0, (lon + 180) * 60 - .5 - c0], order=1, mode="nearest")


def crop(sr, tier, region, ramp):
    cfg = geo.load()["relief"]
    step = tier["km"] / geo.km_per_unit()
    x0, y0, x1, y1 = bbox(*region)
    i0, i1 = math.floor(x0 / step), math.ceil(x1 / step)
    j0, j1 = math.floor(y0 / step), math.ceil(y1 / step)
    X, Y = np.meshgrid((np.arange(i0, i1) + .5) * step, (np.arange(j0, j1) + .5) * step)
    lon, lat = geo.inv(X, Y)
    inside = (lon >= region[0]) & (lon < region[1]) & (lat >= region[2]) & (lat <= region[3])
    d = sample(sr, lon, lat, tier["km"], region) - cfg["flat"]
    g = np.where(inside, 128 + np.where(d < 0, d * cfg["shade"], d * cfg["light"]), 128)
    a = None
    if ramp > 0:
        dist = np.minimum.reduce([lon - region[0], region[1] - lon, lat - region[2], region[3] - lat])
        a = smooth(dist / ramp)
    return dict(g=np.clip(np.rint(g), 0, 255).astype(np.uint8), a=a, lon=lon, lat=lat, region=region, tier=tier,
                x=i0 * step, y=j0 * step, w=(i1 - i0) * step, h=(j1 - j0) * step, px=[int(i1 - i0), int(j1 - j0)])


def encode(g, a, q):
    if a is None: im = Image.fromarray(g, "L")
    else: im = Image.fromarray(np.dstack([g, g, g, np.clip(np.rint(a * 255), 0, 255).astype(np.uint8)]), "RGBA")
    buf = io.BytesIO(); im.save(buf, "WEBP", quality=q, method=6, alpha_quality=60)
    return buf.getvalue()


def era(slug, sr):
    cfg = geo.load()["relief"]
    b = json.loads((V1 / f"{slug}.json").read_text(encoding="utf8"))
    ext, _ = geo.era_boxes(b)
    out = []
    for t in sorted(cfg["tier"], key=lambda t: -t["km"]):       # 粗档在下、细档在上
        if "box" not in t: out.append(crop(sr, t, tuple(cfg["world"]), 0))
        else:
            r = isect(ext, t["box"])
            if r: out.append(crop(sr, t, r, cfg["ramp"]))
    for k, c in enumerate(out):                                   # 粗档里被更细的档完全盖住的像素改成平地
        for f in out[k + 1:]:
            r = f["region"]; pad = cfg["ramp"] + c["tier"]["km"] / 111 * 2
            cov = (c["lon"] > r[0] + pad) & (c["lon"] < r[1] - pad) & (c["lat"] > r[2] + pad) & (c["lat"] < r[3] - pad)
            c["g"][cov] = 128
    d = geo.RELIEF / slug
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.webp"): f.unlink()
    layers = []
    for c in out:
        data = encode(c["g"], c["a"], cfg["quality"])
        name = c["tier"]["id"] + ".webp"
        (d / name).write_bytes(data)
        layers.append(dict(id=c["tier"]["id"], km=c["tier"]["km"], file=name, px=c["px"], bytes=len(data),
                           x=round(float(c["x"]), 4), y=round(float(c["y"]), 4), w=round(float(c["w"]), 4), h=round(float(c["h"]), 4),
                           region=[round(float(v), 4) for v in c["region"]]))
    idx = dict(source=cfg["sha256"], ext=ext, layers=layers)
    (d / "index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
    tot = sum(l["bytes"] for l in layers)
    print(f"{slug:20s} " + "  ".join(f"{l['id']} {l['km']:g} km {l['px'][0]}×{l['px'][1]} {l['bytes'] // 1024} KB" for l in layers)
          + f"  合计 {tot / 1e6:.2f} MB（页面里 base64 后约 {tot * 4 / 3 / 1e6:.2f} MB）")


def main(slugs):
    sr = source()
    for s in slugs: era(s, sr)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    from run import SLUGS
    main(sys.argv[1:] or SLUGS)
