# Qin and Han

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

An interactive historical map from the Qin empire to the Yellow Turbans (212 BC–AD 184), in Chinese and English; Volume III of the Historical Atlas of China. It has 57 snapshots, 16 of them, covering the fall of Qin and the Chu–Han contention (209–202 BC), month by month. The first snapshot joins the last snapshot of the Warring States volume and the last joins the first snapshot of the Late Han and the Three Kingdoms volume, with identical territory and colors at both junctions. The allegiance of 163 commanderies and kingdoms (the Qin commanderies, the Western Han commanderies and kingdoms of AD 2, and those of the Eastern Han) is recorded at every snapshot, and the map can be colored by state or by commandery. There are also 77 states and tribal peoples, 22 capitals, 50 battles, 37 events, 30 passes and 16 peoples on the frontiers, and three layers: commandery boundaries, long walls and roads, and campaign routes (31, advancing snapshot by snapshot: the stretch covered by the current snapshot is drawn solid with arrows, earlier stretches dashed). In the commanderies view the Xiongnu are divided according to the *Shiji*, the *Han shu* and the *Hou Han shu* (the chanyu's own domain, the Wise Kings of the Left and Right, the Hunye and Xiutu kings and others). North of the Gobi the map marks Mount Langjuxu, Mount Guyan, the Hanhai (following the Lake Baikal view) and Mount Yanran (where the Yanran inscription was found in 2017), and places Zhao Xin's fort, whose site is disputed, approximately at the southern foot of the Khangai Mountains; the Honggou canal follows the same course as in the Warring States volume and is drawn above the imperial highway. The Mu Us sands are not drawn, since open drifting sand appeared there only in the later Tang. The view reaches west to eastern Parthia (55°E).

This volume was compiled in the single repository in November 2026 (migration step 6), so it has no old repository or old address. It is also the first volume whose territory comes straight from the unified territory engine (`core/engine/`).

---

## 1. Viewing

- Online: https://jackyijun.github.io/lidai-yutu/qinhan/
- Locally: build from the repository root and open `docs/qinhan/index.html` (data, styles and script are all embedded; no network needed).
- Deep links: after `#` the address bar records the current snapshot, selection, view, coloring, zoom and language, e.g. `#y=-206.2&sel=polity:西楚&lang=en`. Monthly snapshots are written as year.month in the *Zizhi tongjian* reckoning: `-206.2` is the 2nd month of Han year 1 (the Eighteen Kings enfeoffed).

## 2. Building

From the repository root:

```bash
python run.py qinhan        # full build (two passes, see below)
python run.py --web         # no territory computation: rebuild the global tables, v1 data and new pages from each volume's source.json and engine.json
```

The territory comes from the unified engine, so the build takes two passes, which `run.py` does automatically:

1. `eras/qinhan/src/build.py --first` turns the source material into ownership data and entries (no geometry yet; it also skips the neighboring volumes' territory, since their engine.json may not have been recomputed yet) and assembles them into `source.json`;
2. this is converted to a v1 bundle, and `core/engine/build.py qinhan` computes the commanderies' territory at every snapshot and writes it to `build/engine/qinhan.json` at the repository root (not tracked);
3. `build.py` runs again, fills in the territory, merges the state outlines and commandery boundaries, and writes `source.json` (this volume's source.json includes the territory and is tracked); the repository then makes the v1 data and new page from it.

When working inside this folder only:

```bash
cd eras/qinhan
python run.py               # source → ownership and entries, territory from the last engine run → source.json
python run.py --html        # only reassemble source.json (when build/ already holds this pass's results)
python run.py --base        # first regenerate the base map geodata/base.json (after changing src/basemap.py)
```

After changing ownership (`content/seeds.py`, `nodes*.py`), run the full build from the repository root; otherwise the territory stays as it was after the last full build. After changing only text, `python run.py` here followed by `python run.py --web` at the root is enough.

## 3. Dates

Years follow the *Zizhi tongjian*: before the Taichu calendar reform (104 BC) the year began in the 10th month, so the 10th to 12th months belong to the new year. The Battle of Gaixia, for example, in the 12th month of Han year 5, is dated 202 BC, month 12, which comes before month 1 of the same year.

- The source material always gives the reckoned year and month (`node(key, year, month)` in `content/nodes.py`, and the years of entries).
- The build converts them into a month index in true order, t = (calendar year) × 12 + month − 1 (`nodes.t_of`): before Taichu, the 10th to 12th months take the previous year. Yearly snapshots give no month and take the 9th month (the end of the year) before Taichu and the 12th after it.
- The page converts back to the reckoned year for display (`yParts` / `yTxt` / `sLab` in the template); positions on the timeline follow the true order.

## 4. Where the territory comes from

### Ownership points (`content/seeds.py`)

- The commandery seats, towns and reference points of the Late Han volume (coordinates, names and English copied; notes not copied);
- the Qin commandery seats of the Warring States volume (used only for the partition, not labeled);
- points added in this volume (`S()`): seats of commanderies that existed only under Western Han, the capitals of the Chu–Han kings, reference points in Lingnan, the lands of the Southwestern Yi, Korea, the Western Regions, the steppe and Central Asia, and the unowned islands of Japan, the Ryukyus, Taiwan and Jeju.

Each point has an ownership history `TL`: `[(year, owner)]`, where the owner is a state key, `@` (a commandery of the central dynasty) or `·` (no owner). For points owned by `@`, the snapshot's commandery system decides which commandery they belong to:

| System | Snapshots | Commandery of a point |
| --- | --- | --- |
| Q Qin commanderies | 212–180 BC | frozen in `content/qinjun.py` (originally decided from the Qin commandery boundaries in the last snapshot of the Warring States volume's old build; `QO` can override) |
| X Western Han units | 164 BC–AD 23 | converted from the Eastern Han unit by `jun.XH_OF_DH` (`XO` can override, also by period) |
| D Eastern Han units | AD 25–184 | the unit recorded in the Late Han volume (`DO` can override) |

A point with no unit in a given system takes the unit of the nearest point that has one in that system.

### Snapshots (`content/nodes.py`, `nodes_later.py`)

Each snapshot gives the commandery system `sys`, the central dynasty `cent`, the `groups` that merge commanderies into one unit (kingdoms, warlords), points changed only in that snapshot `ext`, which state the peoples and dependencies answer to `polmap`, names for the year `lab`, hatching `h` and capitals `seat`. Under the X system the vassal kingdoms are added automatically by year from `KINGDOMS`, their extent approximated by the AD 2 units.

### Computation and junctions

- The unified engine computes each unit's territory from the ownership points on the world-wide grid (outer edge by reach cost, `[engine]` in `era.toml`; each point's reach factor `R=` is set in `seeds.py` and written to `build/reach.txt` at build time).
- The 212 BC snapshot copies the last snapshot of the Warring States volume: the outlines of Qin and Wey and the boundaries of the 51 Qin commanderies, and the text as well. Since the Warring States volume moved to the unified engine (19 November 2026), the outlines and commandery boundaries come from `eras/zhanguo/engine.json` (where the engine subdivides Qin by commandery seat), matching the new Warring States page. The old build drew Qin's territory out over the sea, so Taiwan, Hainan and Jeju used to be cut out; the engine's outer edge follows the coast, so nothing is cut out anymore. Which Qin commandery each place belongs to (the Q system) used to be decided by the commandery boundaries drawn by the Warring States volume's old build. Since the third batch of the architecture cleanup (20 November 2026), the result has been frozen in `content/qinjun.py` (a place not listed there still takes the commandery of the nearest place that has one), and the colors of all commanderies and kingdoms are now set in `global/palette.toml`. Neither changes when the Warring States territory changes. Whenever the Warring States territory is recomputed, this volume must be rebuilt as well (`python run.py zhanguo qinhan` at the repository root does both in one run).
- The AD 184 snapshot copies the first snapshot of the Late Han volume: the state outlines are copied, and Han's commanderies, computed by the engine, are clipped to the Late Han volume's outline of Han with the gaps filled. Since the Late Han volume moved to the unified engine (19 November 2026), the outlines come from `eras/hanmosanguo/engine.json`, matching the new Late Han page; whenever the Late Han territory is recomputed, this volume must be rebuilt as well.
- Colors: all colors are set in the repository's `global/palette.toml` (by global polity ID; states shared with the Warring States and Late Han volumes have the same colors there). Formerly, states shared with those volumes took their colors from them (written `zg:` / `hm:` in `units.py`) and the rest were taken from a palette by adjacency; that was retired with the old build in the third batch of the architecture cleanup (November 2026).

## 5. Layout

```
eras/qinhan/
├── run.py                 stage-1 build entry point (one pass): → source.json
├── era.toml               basic facts (volume number, opening snapshot, coloring, engine settings, junctions)
├── source.json            ★ the stage-1 output (tracked, territory included), from which the repository's v1 data is converted
├── content/
│   ├── seeds.py           ownership points and their histories
│   ├── jun.py             Qin commandery names, the 103 Western Han units, Eastern → Western Han conversion, English names of units
│   ├── qinjun.py          which Qin commandery each place belongs to (frozen; originally decided from the commandery boundaries of the Warring States volume's old build)
│   ├── nodes.py           snapshots of Qin, Chu–Han and early Han (Q system), and t_of
│   ├── nodes_later.py     snapshots of Western Han, Xin and Eastern Han (X / D systems), and KINGDOMS
│   ├── texts.py, texts2.py  snapshot titles, reign years and summaries (Chinese and English)
│   ├── units.py           notes on states and peoples (Chinese and English)
│   ├── items.py, items_data.py  capitals, battles, events, peoples, passes, long walls, roads, campaign routes
│   └── en_names.py, en_names_data.py  English for place and commandery names (generated by tools/en_names.py, then edited by hand)
├── src/
│   ├── config.py          paths and constants (extent, Taichu, opening snapshot)
│   ├── basemap.py         base map: rivers, lakes and physical entries of the Late Han volume within its extent, Natural Earth outside it
│   ├── build.py           source → GEO / DATA in the old format (build/geo.json, data.json, plus build/reach.txt for the engine)
│   └── assemble.py        assembles source.json
├── geodata/base.json      base map (generated by src/basemap.py, tracked)
└── tools/en_names.py      generates content/en_names_data.py
```

## 6. Common changes

| To change | Edit | Then |
| --- | --- | --- |
| who held a point in a given year | `TL` in `content/seeds.py` | `python run.py qinhan` at the root |
| the kingdoms or warlords in a snapshot | `groups`, `ext`, `KINGDOMS` in `content/nodes*.py` | the same |
| snapshot titles and summaries | `content/texts*.py` (Chinese and English together) | `python run.py` here, `python run.py --web` at the root |
| capitals, battles, events and other entries | `content/items_data.py` (Chinese and English together) | the same |
| notes on states | `content/units.py` | the same |
| colors | the repository's `global/palette.toml` (by global polity ID) | `python run.py --web` at the root |
| English place names | the hand-edited block at the end of `content/en_names_data.py` | the same |
| the interface | the repository's `core/web/` (shared by the volumes; this volume's own text and switches are under `[web]` in `era.toml`) | `python run.py --web` at the root |

The text and territory of the junction snapshots (212 BC, AD 184) are copied from the neighboring volumes by `build.py`; do not change them in this volume. When a neighboring volume changes, rebuild this one.

## 7. Sources and reliability

Territories are inferred in outline from the *Shiji*, the *Han shu*, the *Hou Han shu*, the *Zizhi tongjian* and vol. 2 of Tan Qixiang's *Historical Atlas of China*, and computed by the unified territory engine from commandery seats and county towns, with borders following mountains and rivers; they are approximate. Commanderies and kingdoms follow the Treatise on Geography of the *Han shu* (AD 2) and the Treatise on Commanderies and Kingdoms of the *Xu Han shu*; up to 180 BC the Qin commanderies are used. Kingdoms appear and disappear as in the Tables of the Kings in the *Han shu*, their extent approximated by the AD 2 units, so the borders of the early Han kingdoms are rough. The ranges of the peoples of the steppe, the Western Regions and Central Asia are drawn roughly from reference points, with dates taken from the major events in the histories (such as the Xiongnu defeat of the Yuezhi in 176 BC, the founding of the Protectorate of the Western Regions in 60 BC, and the northern chanyu's flight west in AD 91). The Xiongnu divisions follow the *Shiji* (the kings of the left in the east, opposite Shanggu and beyond; the kings of the right in the west, opposite Shang Commandery and beyond; the chanyu's court opposite Dai and Yunzhong), the Treatise on Geography of the *Han shu*, which places the lands of the Xiutu and Hunye kings in Wuwei and Zhangye, and the Southern Xiongnu and Western Regions chapters of the *Hou Han shu*; the sources give no borders between them, so the borders on the map are only a sketch. From AD 50, when the Southern Xiongnu settled at Meiji in Xihe, they are shown as nominally submitted to Han (hatched). The stops and months of the campaign routes come from the annals and biographies of the *Shiji*, the *Han shu* and the *Hou Han shu* and from the *Zizhi tongjian*; the course between stops is often inferred. Mount Yanran is placed at the cliff inscription for the feng sacrifice on Mount Yanran identified by a joint Chinese–Mongolian survey at Delgerkhangai, Dundgovi Province, Mongolia, in 2017; Mount Langjuxu follows the Khentii identification and the Hanhai the Lake Baikal one, both disputed. The Mu Us sands are left off following historical-geography research since Hou Renzhi (Tongwan City in 413 "overlooked broad marshes"; sand "heaped as high as the battlements" at Xiazhou in 822). The volume was compiled with AI assistance and has not been checked line by line against the original texts.
