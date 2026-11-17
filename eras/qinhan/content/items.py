# -*- coding: utf-8 -*-
"""条目：都城、战役、事件、诸族、关隘、长城、道路、行军路线（山川、运河、古道、汉末已有的关隘取自 geodata/base.json）。

行军路线另出底图图层 routes（与隋唐、民国卷同一格式）。

日期一律写纪年年（+月），与节点一样按通鉴纪年换成月序号。"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from nodes import t_of  # noqa: E402
from items_data import CAPITALS, BATTLES, EVENTS, PEOPLES, PASSES, WALLS, ROUTES  # noqa: E402


def ylab(y, en=False):
    if en:
        return f"{-y} BC" if y < 0 else (f"AD {y}" if y < 1000 else str(y))
    return f"前{-y}" if y < 0 else str(y)


def ytext(a, b=None, en=False):
    if b is None or b == a:
        return ylab(a, en)
    return f"{ylab(a, en)}–{ylab(b, en)}" if en else f"{ylab(a)}—{ylab(b)}"


def span_t(sp):
    """都城年段 → [起, 止) 月序号。(起年, 止年) 取整年；(起年, 月, 止年, 月) 精确到月，止月那个月起已不是都城"""
    if len(sp) == 4:
        return [t_of(sp[0], sp[1]), t_of(sp[2], sp[3])]
    a, b = sp
    return [t_of(a, 1 if a > -104 else 10), t_of(b, 12 if b >= -104 else 9)]


def build(base, SEEDS, UK, zg_items):
    items = []

    def add(o):
        o["i"] = len(items)
        items.append(o)
        return o

    for it in base["items"]:
        o = {k: v for k, v in it.items() if k != "i"}
        add(o)
    # 都城
    near = lambda lon, lat: next((i for i, s in enumerate(SEEDS) if abs(s["lon"] - lon) < .15 and abs(s["lat"] - lat) < .15), None)
    for (old, en_old, unit, lon, lat, spans, mod, en_mod, note, en_note) in CAPITALS:
        o = dict(c="capital", old=old, mod=mod, note=note, lon=lon, lat=lat, st=UK[unit],
                 yrs=[span_t(sp) for sp in spans],
                 e=dict(old=en_old, mod=en_mod, note=en_note))
        at = near(lon, lat)
        if at is not None:
            o["at"] = at
        add(o)
    for (old, en_old, lon, lat, y, m, sides, en_sides, cmd, en_cmd, mod, en_mod, note, en_note) in BATTLES:
        add(dict(c="battle", old=old, mod=mod, note=note, lon=lon, lat=lat, y=t_of(y, m or 6), yt=ytext(y), sides=sides, cmd=cmd,
                 e=dict(old=en_old, mod=en_mod, note=en_note, yt=ytext(y, en=True), sides=en_sides, cmd=en_cmd)))
    for (old, en_old, lon, lat, y, m, mod, en_mod, note, en_note) in EVENTS:
        add(dict(c="event", old=old, mod=mod, note=note, lon=lon, lat=lat, y=t_of(y, m or 6), yt=ytext(y),
                 e=dict(old=en_old, mod=en_mod, note=en_note, yt=ytext(y, en=True))))
    for (old, en_old, lon, lat, a, b, note, en_note) in PEOPLES:
        add(dict(c="people", old=old, mod="", note=note, lon=lon, lat=lat, y0=t_of(a, 1 if a > -104 else 10),
                 y1=t_of(b, 12 if b >= -104 else 9), e=dict(old=en_old, note=en_note)))
    for (old, en_old, lon, lat, mod, en_mod, note, en_note) in PASSES:
        add(dict(c="pass", old=old, mod=mod, note=note, lon=lon, lat=lat, e=dict(old=en_old, mod=en_mod, note=en_note)))
    # 长城、驰道直道：战国卷的取过来，汉塞新画
    for it in zg_items:
        if not ((it["c"] == "wall" and it.get("y1") is None) or it["c"] == "road"):
            continue
        add(dict(c="road", sub="wall" if it["c"] == "wall" else "road", old=it["old"], mod=it["mod"], note=it["note"],
                 geo=it["geo"], anc=it["anc"], major=True, y=t_of(int(it["y"]), 9),
                 e=dict(old=it.get("eold", ""), mod=it.get("emod", ""), note=it.get("enote", ""))))
    for (old, en_old, geo, y, mod, en_mod, note, en_note) in WALLS:
        add(dict(c="road", sub="wall", old=old, mod=mod, note=note, geo=geo, anc=geo[len(geo) // 2], major=True, y=t_of(y, 9),
                 e=dict(old=en_old, mod=en_mod, note=en_note)))
    # 行军路线：条目 + 底图 routes（每点 [经, 纬, 月序号, 地名, 精度]），前端按节点画出已走过的一段
    routes = []
    for R in ROUTES:
        pts, pe = [], []
        for (n, ne, lon, lat, y, m) in R["pts"]:
            pts.append([lon, lat, t_of(y, m), n, "m" if m else "y"])
            pe.append(ne)
        # 折点（无名）取下一个有名点的日期，保证每段的到达时间都有名可查
        for j in range(len(pts) - 2, -1, -1):
            if not pts[j][3]:
                pts[j][2], pts[j][4] = pts[j + 1][2], pts[j + 1][4]
        ys = [y for (_, _, _, _, y, _) in R["pts"]]
        it = add(dict(c="route", old=R["name"], mod="", note=R["note"], y=pts[0][2], y1=pts[-1][2], yt=ytext(ys[0], ys[-1]),
                      anc=pts[len(pts) // 2][:2], e=dict(old=R["en"], note=R["note_en"], yt=ytext(ys[0], ys[-1], en=True))))
        routes.append(dict(it=it["i"], pts=pts, pe=pe))
    return items, {"routes": routes}
