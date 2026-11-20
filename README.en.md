# Historical Atlas of China

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

The index page of the historical map series, in order: the title-slip header, the timeline, the contents and the notes. Each volume in the contents links to the new page published from this repository; each volume's original address is kept as the old version ("Old version ↗" at the top right of each entry) and is no longer updated:

| Volume | Map | Address | Old version |
| --- | --- | --- | --- |
| I | The Spring and Autumn Period (770–476 BC) | https://jackyijun.github.io/lidai-yutu/chunqiu/ | https://jackyijun.github.io/chunqiu-map/ |
| II | The Warring States (475–212 BC) | https://jackyijun.github.io/lidai-yutu/zhanguo/ | https://jackyijun.github.io/zhanguo-map/ |
| III | Qin and Han (212 BC–AD 184) | https://jackyijun.github.io/lidai-yutu/qinhan/ | (new in this repository, no old version) |
| IV | Late Han and the Three Kingdoms (184–280) | https://jackyijun.github.io/lidai-yutu/hanmosanguo/ | https://jackyijun.github.io/hanmosanguo-map/ |
| V | Jin, Sixteen Kingdoms and Northern and Southern Dynasties (280–581) | https://jackyijun.github.io/lidai-yutu/liangjin-nanbeichao/ | https://jackyijun.github.io/liangjin-nanbeichao-map/ |
| VI | Sui and Early Tang (581–669) | https://jackyijun.github.io/lidai-yutu/suitang/ | https://jackyijun.github.io/suitang-map/ |
| VII | Late Tang and the Five Dynasties (755–979; the map itself is titled Between Tang and Song) | https://jackyijun.github.io/lidai-yutu/tangsong/ | https://jackyijun.github.io/tangsong-map/ |
| VIII | Song · Liao · Xia · Jin · Yuan (979–1279) | https://jackyijun.github.io/lidai-yutu/songyuan/ | https://jackyijun.github.io/songyuan-map/ |
| IX | Republican China to the Early PRC (1911–1954) | https://jackyijun.github.io/lidai-yutu/minguo-xinzhongguo/ | https://jackyijun.github.io/minguo-xinzhongguo-map/ |

Volumes I to VI join without a seam: at each junction the two neighboring volumes have identical territory and colors. The last snapshot of the Spring and Autumn map (476 BC) matches the first of the Warring States map (475 BC); the last of the Warring States map matches the first of the Qin and Han map (212 BC); the last of the Qin and Han map matches the first of the Late Han map (184); the last of the Late Han map matches the first of the Jin map (280); and the last of the Jin map matches the first of the Sui–Tang map (581). The Qin and Han map and the Jin map both copy the junction snapshots at either end.

The hub's source file `hub/index.html` is self-contained (the build copies it unchanged to `docs/index.html` for publishing): its styles, script and all nine thumbnails are written into the file, and it loads no outside resources. Its palette, fonts and hairlines match the maps' shared style guide (历史形势图统一规范), and it follows the system's light or dark setting.

Live page: https://jackyijun.github.io/lidai-yutu/

## Single repository (migration in progress since November 2026)

This repository is being turned into a single repository for the whole atlas: the code, source material and base data of the original eight volumes have moved in, the new Qin and Han volume was compiled here directly, and the unified data format, global gazetteer, shared projection and terrain, unified territory engine and the hub's timeline mode will all be built here. Steps and progress are in section 19 of the style guide (历史形势图统一规范). Each volume's old repository and address are kept as the old edition and no longer change.

```
lidai-yutu/
├── run.py                 build entry point
├── requirements.txt       dependencies shared by all volumes
├── requirements-lock.txt  versions that reproduce the published pages byte for byte
├── hub/index.html         source of the hub page
├── eras/<slug>/           each volume: content/ sources, src/ build code, tools/, run.py; each still builds on its own;
│                          era.toml describes the volume; legacy.html the old build's output (the data source); short.tsv timeline short titles
├── core/v1/               unified data format v1: spec FORMAT.md (in Chinese), legacy conversion, global-table generation, step-3 corrections
├── core/web/              unified front end: builds each volume's new page from v1 (timeline, deep links); see core/web/README.md (in Chinese)
├── core/geo/              unified projection, world base map, terrain relief: all parameters in config.toml; see core/geo/README.md (in Chinese)
├── core/engine/           unified territory engine (it draws the territory of all nine volumes): parameters gathered in config.toml; see core/engine/README.md (in Chinese)
├── global/                global tables: places, polities, physical features, glossary; palette.toml the shared palette; decisions.toml manual decisions; review/ lists to review
├── geodata/               one copy of the base data (ne/, etopo20/, prov/, derived/); each volume's geodata/ holds symlinks to it;
│                          relief/<slug>/ each volume's relief images, world/<slug>.json the world land outside each volume (made by core/geo, committed)
├── tools/thumbs.py        hub thumbnails
├── tools/colorcheck.py    palette survey: colour difference between neighbouring polities in every volume
└── docs/                  published by GitHub Pages: index.html is the hub, <slug>/index.html each volume
```

A volume's slug is its old repository name without `-map`: chunqiu, zhanguo, hanmosanguo, liangjin-nanbeichao, suitang, tangsong, songyuan, minguo-xinzhongguo; the Qin and Han volume has no old repository and its slug is qinhan. The build has three stages: each volume still computes its territory with its own original build script and saves the result as `eras/<slug>/legacy.html`; from these the global tables are rebuilt, the data converted to v1 and the step-3 corrections applied; and the new pages `docs/<slug>/index.html` are generated from v1, with the terrain relief and world base map pre-generated in `geodata/relief/` and `geodata/world/` merged in. Volumes that have switched to the unified territory engine (`geometry = "engine"` under `[engine]` in `era.toml`; now all volumes except Qin and Han) take their territory from the engine, computed from the ownership in the v1 data and saved as `eras/<slug>/engine.json` (committed); it replaces the old engine's geometry from legacy.html when the v1 data are built, and `python run.py` recomputes it automatically when it builds those volumes.

```bash
pip install -r requirements.txt
python run.py                    # build all nine volumes: territory → v1 data → new pages, then update the hub
python run.py zhanguo songyuan   # build only these volumes
python run.py --html             # skip the territory computation, only reassemble (needs one full build first)
python run.py --web              # no territory computation: rebuild the global tables, v1 data and new pages from legacy.html
python run.py --geo              # regenerate the terrain relief and world base map, then the new pages (after changing projection, tiers or base-map settings in core/geo/config.toml; the first run downloads the ~42 MB relief source)
python run.py --v1               # only rebuild the global tables and each volume's v1 bundle (build/v1/, not tracked)
python run.py --engine           # unified territory engine, comparison run: recompute the territory of every volume except Qin and Han from v1 data and compare each snapshot with the territory drawn by the old engines (build/engine/; the pages are not changed)
python run.py --hub              # only update the hub
python run.py --check            # check whether legacy.html and docs/ hold the latest local builds
python run.py --list             # list the volume slugs
```

GitHub Pages publishes from the `/docs` folder of the `main` branch.

All nine volumes now take their colours from [`global/palette.toml`](global/palette.toml), keyed by each polity's global ID, so a polity has the same colour in every volume. The main dynasties take the colour of their phase in the Five Phases cycle, in a light, low-saturation form: Qin (Water) black, the two Han dynasties, Sui and Song (Fire) red, with Shu Han, heir to Han, a shade lighter; Xin, Cao Wei and Tang (Earth) yellow; Jin (Metal) white. The other polities were recoloured where needed so that no two neighbouring territories in any snapshot clash. The Republican volume keeps its colours, except for the Netherlands, the Tibetan government and Afghanistan, which could not be told apart from British territory. After changing colours, rerun `python3 tools/colorcheck.py` (after `python run.py --web` or `--v1`) and regenerate the hub thumbnails.

The Great Desert (Gobi) in seven volumes used to take its extent from the "GOBI DESERT" label area in Natural Earth's geographic regions, which also covered the steppe north of the Yin Mountains, the Hexi Corridor and the Kherlen River. It is now redrawn by [`tools/damo.py`](tools/damo.py) from the three Gobi ecoregions of RESOLVE Ecoregions 2017 (data in [`geodata/resolve/`](geodata/resolve/README.md), CC-BY 4.0), leaving out the steppe south of the desert (its central stretch ends where the *New Book of Tang* geography treatise has the road enter the desert, at about 43°N), the Hexi Corridor and the Juyan oasis, and the land north of the southern foothills of the Khangai Mountains; the Qin and Han volume also leaves out the Han farmland in the northern Ulan Buh Desert. The new outline replaces the old one in every volume when the v1 data are generated (`core/v1/overlay.py`). At the scale of these maps the Gobi itself shows no visible change over two thousand years; what changed were the sandy lands and oases: the Mu Us Desert is already handled volume by volume, and the others will be added period by period.

Migration step 7 switches the older volumes to the unified territory engine one by one, starting with Sui–Tang and Jin (17 November 2026). Their ownership, text and entries are unchanged; the territory is recomputed by the engine from each snapshot's ownership, and about 5.6% of the land changes hands in Sui–Tang and 6.9% in Jin, mostly where seeds are sparse: the Tarim Basin, the edges of the Tibetan Plateau, the northeast and the states of the southern seas. Every seed now lies inside its own territory and the borders have no long straight runs. The 581 junction snapshot copies the Sui–Tang engine geometry inside the Sui–Tang volume's hand-drawn outer edge, so the two volumes agree; the 280 junction keeps the old geometry copied from the Late Han volume until that volume switches too. The second batch, Song–Yuan and Republican (18 November 2026), changes about 9.8% and 2.5% of the land: most in Central Asia, the edges of the Tibetan Plateau and Arabia, and least in the Republican volume, where the national-border walls hold the lines. In the old pages the two volumes together had about 1,500 snapshot placements of towns inside someone else's territory; the new pages have none. Because these two volumes cover a wide area over many snapshots, their borders are simplified with a tolerance of 0.25 cells (about 1.8 km; `simplify` in the `[engine]` section of `era.toml`), which keeps the pages about as large as before (at the engine default the Republican page would be 21 MB). The 979 junction follows the Song–Yuan volume. The third batch, Tang–Song (18 November 2026), changes the owner of about 10.8% of the land: only the oases remain on the southern rim of the Tarim Basin, Nepal is pulled back to the southern slopes of the Himalayas, and the capital region now reaches south to the Qinling Mountains. The old engine drew borders as straight-line segments, more than 1,500 of them longer than 20 km in each snapshot; the new version has only about twenty per snapshot. The 979 junction snapshot copies the Song–Yuan engine geometry within the Tang–Song volume's computed area, so the two volumes agree (the Song–Yuan volume's 979 snapshot no longer puts the Jurchens under the Liao, and the Tang–Song volume now treats the Shiwei and Zubu as dependent tribes of the Liao). Tang–Song uses the engine's default simplification tolerance; its borders follow the terrain and have about seven times as many vertices as before, and the page has grown from 2.7 MB to 5.9 MB (about 1.9 MB compressed in transfer). The fourth batch, Late Han (19 November 2026), changes the owner of about 12.7% of the land, mostly on the outer edges of Buyeo, Goguryeo, Linyi, the Xianbei and the Qiang, and between the warlords of the Central Plains. Province borders are now drawn by the engine from warlord × province blocks, so they share their edges with the warlord borders, and how far the outer edges reach is converted from each seed's old partition radius. The same batch fixes a flaw in the engine: small islands far out at sea, and fragments at the edge of the computed area, used to be smoothed into owned land and given to a state across the sea (the Song–Yuan volume gave the Marianas to Japan, for example). Now they get an owner only if they lie within about 85 km of owned land, and the Qin and Han, Tang–Song and Song–Yuan volumes were recomputed with this rule; the colonial island groups in the Republican volume are kept as before. The 184 and 280 junctions now copy the new Late Han territory. The fifth batch, Spring and Autumn and Warring States (19 November 2026), completes the switch: the engine now draws the territory of all eight older volumes. The computed area is the same as in the old build, all land inside it goes to the nearest seed (except far-off islands that cannot be reached over land), and the outer edge is set by seeds that belong to no state, as before. About 12.1% of the land changes hands in Spring and Autumn and 7.1% in Warring States, mostly on the edges of the mountain states (Ba, Shu, Yiqu, the Western Rong) and between the small states of the Central Plains, and territory is no longer drawn out over the sea (in the old version, Qin in the last Warring States snapshot covered Taiwan and the Ryukyus). The outline of the Zhou realm (in Suzerain coloring) and the Qin commandery boundaries are also drawn by the engine. Four unowned seeds in the northwest (Wuwei, Zhangye, Alxa and Juyan) were added to the seed file the two volumes share, so that in 212 BC Qin's northwestern border runs along the Helan Mountains and the Yellow River instead of filling the Hexi Corridor and Alxa. At the 476/475 BC junction the territories of all 28 states are byte-for-byte identical, and the Qin and Han volume's 212 BC snapshot copies the new Warring States territory. As in the Song–Yuan and Republican volumes, borders are simplified with the looser tolerance of 0.25 cells; the two pages grow from 1.8 to 2.3 MB and from 1.5 to 2.0 MB. The same batch adds one more check to the engine's seed protection: coordinates are stored to 0.01°, and a seed that the rounded border passes exactly through (usually one on the bank of a border river, such as Neihuang in the Warring States volume and Baima in the Late Han volume) now also gets a small disc that pulls it back into its own territory. In the Late Han volume this changes the owner of about 30 km² around Baima in the snapshots from 195 to 200; the other volumes switched earlier come out byte-for-byte identical.

Migration step 6 compiled the [Qin and Han volume](eras/qinhan/README.en.md) (212 BC–AD 184, 57 snapshots) in this repository, filling the gap between the Warring States and Late Han. The Late Han and the Three Kingdoms volume accordingly dropped its prologue snapshot for AD 94 and now opens with the Yellow Turban Uprising in 184, and the later volumes were renumbered. Qin and Han is the first volume whose territory comes straight from the unified territory engine: `eras/qinhan/src/` turns the source material into ownership data and entries, the engine (`core/engine/`) computes the commanderies' territory, and the junction snapshots are copied from the end of the Warring States and the start of Late Han; the build takes two passes, which `python run.py` does automatically. Adding a volume leaves the other volumes' global IDs unchanged: any that automatic naming would change are pinned in `global/decisions.toml`.

Migration step 5 wrote the unified territory engine, [`core/engine/`](core/engine/README.md) (in Chinese). It works on one world-wide grid laid over the shared projection (about 7 km per cell); the position of each cell, the terrain, the mountain ranges and the random variation depend only on longitude and latitude, so a place costs the same in every volume and neighbouring volumes will be able to share their territory seeds. The outer edge can be hand-drawn (the Jin and Sui–Tang volumes) or set by how far each seed reaches (the Song–Yuan and Republican volumes), and the Republican volume's border walls are built in. In step 5 the engine only ran alongside: it recomputed four volumes from their own ownership data and compared every snapshot with the current pages, which stayed unchanged; from step 7 the volumes switch over one by one.

Migration step 4 unified the projection and added a world base map and terrain relief. All eight volumes now use one Albers projection (central meridian 105°E, origin latitude 35°N), with the seam moved to 30°W in the Atlantic; zoomed all the way out the whole world is shown (except Antarctica), with Natural Earth 1:50m land and large lakes outside each volume's own area. The relief comes from Natural Earth 1:10m Shaded Relief, in three tiers by region (China proper and its surroundings 2 km, Eurasia 5 km, the rest of the world 10 km), so a place looks equally sharp in every volume; it can be switched off in the legend. Each page grows by 0.6–1.2 MB. Opacity, tiers and other settings are all in [`core/geo/config.toml`](core/geo/config.toml); see [`core/geo/README.md`](core/geo/README.md) (in Chinese).

Migration step 3 put a unified front end online: the eight new pages share one timeline (a thin strip on a true time scale above evenly spaced ticks showing year / short title / reign era) and deep links (the address records the current snapshot, the selected object, the view, the coloring, the zoom and the language, as in `#y=1127&sel=polity:金&lang=en`, ready to share); every volume plays at 1× or 2×, and the interface language is shared by all volumes and the hub. The maps themselves are the same as the old versions, apart from corrections that do not touch territory: point locations, English names and a few names (see `global/corrections.md`). See [`core/web/README.md`](core/web/README.md) (in Chinese).

Migration step 2 defined data format v1, shared by all eight volumes, and merged the places, polities, physical features and translations of the eight volumes into global tables in which every object has a cross-volume global ID. For now v1 is converted from each volume's built page (converting back gives byte-identical data), so the pages are unaffected; cases the automatic merge cannot decide are listed in `global/review/`, and decisions go into `global/decisions.toml`. The format, the ID rules and the review process are described in [`core/v1/FORMAT.md`](core/v1/FORMAT.md) (in Chinese).

The territory computation is sensitive to the versions of numpy, scipy, scikit-image and shapely: other versions move borders by about 0.01° in the last digit, and the Spring and Autumn and Warring States volumes stop because their cost-grid fingerprint no longer matches. To reproduce the published pages byte for byte, use the versions in `requirements-lock.txt` (Python 3.13).

## Bilingual

The 中 | EN switch at the top right changes the language; Chinese is the default. The Chinese name is 历代舆图 and the English name Historical Atlas of China.

- The choice is saved on the device (localStorage key `lidai-yutu:lang`). Adding `#en` to the address opens the English page, and `#zh` the Chinese one; `<html lang>` changes with it.
- Links from the contents into each volume carry the current language (`#zh` / `#en`), so each map opens in the same language; the new volume pages read and write the same `lidai-yutu:lang`.
- Page text is written in pairs in the same place: `<span class="zh">…</span><span class="en" lang="en">…</span>`, and only the one matching `<html lang>` is shown. The timeline is built by the script at the end of the page; each entry in its dynasty and period bands `BANDS` also carries a Chinese and an English name.
- In English the headings and volume titles switch to a Latin serif (Iowan Old Style, Palatino and the like) and the body text to the system sans-serif; the wide CJK letter-spacing is dropped and group headings are set in capitals. The vertical title slip 历代舆图 and the two seals stay as they are, with the English title set to the right of the slip.
- Volume titles, subtitles, coloring modes and the terms in the stats lines follow each map's own English version: time nodes are snapshots, 州府 and 州郡 are prefectures, 郡国 and 郡县 are commanderies, 藩镇 is written fanzhen, and 方镇 are regional commands; in the Republican volume, 城市 are cities and 派系与属地 are factions and dependencies. Volume VII is titled Late Tang and the Five Dynasties in English, matching 唐末五代 on the Chinese page; the map's own English title is Between Tang and Song.
- Each thumbnail holds two sets of labels, Chinese and English (`<g class="t-lab zh">`, `<g class="t-lab en">`), and also shows only the one for the current language. The English names come from each map's data; see "Generating thumbnails" below.

## Adding a volume

The steps below edit `hub/index.html`; afterwards run `python run.py --hub` to update `docs/index.html`, the published copy.

1. Copy an `<li class="juan">` block, put it into the contents in date order, and renumber the volumes (卷一, 卷二 …; Volume I, Volume II …).
2. Change these:
   - `id`
   - `data-short`, `data-short-en`: the short Chinese and English names shown on the timeline
   - `data-start`, `data-end`: first and last year
3. Change the link and the thumbnail (see the next section), and both language versions of the title, years, subtitle, description, `stats` and the thumbnail caption `thumb-cap`. Take the English from that map's own English title, subtitle and terms.
4. Add an `--m-xx` to `:root` and to both dark blocks as the volume's main color, one light and one dark value, and write `style="--c:var(--m-xx)"` on the `<li>`. The color should stand apart from its neighbors on the timeline.
5. Update the cover's 「凡八卷 · 前770 — 1954」 and "Eight volumes · 770 BC – 1954", the contents heading 「已成八卷」 and "Eight volumes completed", and the volume names in `<meta name="description">`, in `og:description` and in `DESC` in the script at the end of the page.
6. If the new volume falls outside 800 BC – 1960, change `R0`, `R1` and `TICKS` in the script at the end of the page, and the year range in the Timeline heading. The dynasty and period bands `BANDS` are in the same place (the Ming, Qing, Republic of China and People's Republic of China bands were added with the Republican volume).

The timeline needs no other change: it draws each volume's bar straight from that volume's `data-start` / `data-end`. Where volume names crowd together, each name goes on the lowest row that has room for it, and the timeline grows taller to match; a name at either end of the timeline (such as the Republican volume's) is moved inward so that it stays inside.

### Announcing a volume in preparation

A map that is not finished yet can be shown as a gray card first:

- Add the class `todo` and the attribute `data-todo="1"` to the `<li>`, and leave out `--c`.
- Replace `<a class="juan-body" href="…">` with `<article class="juan-body" aria-labelledby="…">`, pointing at the `<h2>` that holds the title.
- Generate the thumbnail with `--blank` and add an 编修中 ("in preparation") stamp after it. The stamp keeps its Chinese text as an emblem and is not switched in English:

```html
<svg class="stamp" viewBox="0 0 96 40" aria-hidden="true">
  <g filter="url(#worn)">
    <rect x="2" y="2" width="92" height="36" rx="2" fill="none" stroke="var(--seal)" stroke-width="2.4"/>
    <rect x="6" y="6" width="84" height="28" rx="1" fill="none" stroke="var(--seal)" stroke-width=".9"/>
    <text x="48" y="20.5" font-size="17" letter-spacing="5" text-anchor="middle" dominant-baseline="central" style="fill:var(--seal);font-family:var(--f-cjk);font-weight:700">编修中</text>
  </g>
</svg>
```

- Write 「编修中」 / "In preparation" in `stats`, and 「即将刊行」 / "Coming soon" in `<span class="act">`.
- The timeline draws that volume as a dashed box automatically.

## Generating thumbnails

`tools/thumbs.py` reads the GEO / DATA embedded in a map's own `index.html` and, using that map's projection and palette, redraws one time node as a 360×270 image. It uses only the Python 3 standard library.

It handles four data layouts:

- Warring States (also the Spring and Autumn map): nodes hold `s` / `l`. Rong and Di peoples marked `tribe` in `DATA.kinds` are drawn pale and dashed, as on the map.
- Tang–Song: nodes hold `z` / `p` / `pol`.
- Late Han, Jin, Sui–Tang and Song–Yuan: territory geometry sits in the shared pool `GEO.pool`. Nodes in the Jin map may also carry `kd` (a change of unit kind at that node, as when Goguryeo is drawn as a state rather than a tribe from 313) and `col` (light and dark colors overriding the unit's own at that node); the thumbnail follows what the node records.
- Republican: nodes are monthly, `t` holds a month index (year × 12 + month − 1) and the title is in `ti`; the projection center comes from `GEO.proj`, and the opening node `GEO.first` is also a month index. The caption gives the date as year.month, e.g. 1937.12.

Labels are drawn in two sets:

- Chinese labels use the state names of that year: for the Spring and Autumn and Warring States maps, the node's period alias `lab` first (such as 鲜虞 before 506 BC), then the old name in the state's entry.
- English is taken from the map's data. For the Spring and Autumn and Warring States maps it is the node's period alias `labe`, or else the `eold` of the state's entry. For the other maps it is, in order of preference, the node's period alias `labe`, the unit's short map name `se`, or its full name `ne`, with anything in parentheses removed.
- English labels are spaced by estimated text width, long names break onto two lines at a space, and a name that will not fit is left out.
- Chinese label size follows the size of the territory, and a label is not allowed to run much wider than its territory: a state made up of several units used to get at least 15px, and now shrinks to fit when that is too wide (in the Republican volume many small states are made up of several units, which is why Puppet Mengjiang and the CPC border regions were drawn too large). `--zh` can switch to a short name and `--fs` can set the size; see below.
- Labels sit at the map's own label points. The unified engine finds each label point over the whole territory (the point farthest from its border), so for a large state that point often falls outside the thumbnail frame and the label is left out. For units given with `--inframe`, a label point outside the frame is moved into the part of the territory inside the frame, to the spot farthest from both the territory's border and the frame edge (Tibet in the Tang–Song volume, the Tibetan tribes in the Song–Yuan volume). This is off by default: turned on for every unit, it would add many small labels crowded along the frame edges.
- For a map that has no English yet, `--en "id=English name;…"` supplies the English thumbnail labels (keyed by unit id); these also take precedence over the map's own English names.

```bash
python3 tools/thumbs.py docs/songyuan/index.html --id sy --year 1120 --mode pol --out thumbs
```

It writes three files:

- `thumbs/thumb-sy.svg`: paste it into that volume's `.thumb-in`.
- `thumbs/thumb-sy.css.txt`: two lines of color tokens. Paste the light line into `:root` and the dark line into both dark blocks, next to the existing `/* 缩略图 zg */` and the others.
- `thumbs/thumb-sy.cap.txt`: the node's year and its Chinese and English titles, for writing the thumbnail caption `thumb-cap`.

Options:

- `--id`: a two- or three-letter code, used as the color-token prefix and clipPath id. Each volume needs its own.
- `--year`: which year's node to draw.
- `--node`: pick the node by index, counting from 0. Use it when one year has several nodes, as in the Sui–Tang map, which has month-level nodes.
- `--month YEAR.MONTH`: pick the node by year and month, for maps with monthly nodes such as the Republican map, e.g. `--month 1937.12`.
- With none of `--year`, `--month` or `--node`, the tool takes the node the map opens on (`GEO.first` holds a year or a month index, `DATA.first` an index), or else the first node.
- `--box W E S N`: the longitude/latitude frame. Without it the tool uses FITS cn or all from the map's source.
- `--mode zhen|pol`: coloring for the layered model. `zhen` (fanzhen, warlords, circuits or factions) is the default; `pol` colors by state.
- `--blank`: draw only land, sea, rivers and the graticule, for a volume in preparation.
- `--en "id=English name;…"`: add or override English labels, as above.
- `--zh "id=Chinese name;…"`: override a Chinese label, for a short name (伪蒙疆 for 伪蒙疆联合委员会) or a different name: the map gives the CPC-held areas a collective name such as 中共（边区·根据地） or 中华苏维埃共和国, and the thumbnail names the area the label sits on instead, 陕甘苏区 (Shaanxi-Gansu Soviet Area) at 1937.07 and 陕甘宁边区 (Shaanxi-Gansu-Ningxia Border Region) at 1937.12.
- `--fs "id=size;…"`: set the size of a Chinese label (the English follows at 0.82 times); 0 leaves the label out, for a label hidden under the caption. For the Spring and Autumn and Warring States maps, use the state name, e.g. `--fs "淮夷=8"`: this keeps the label of a slightly small territory whose computed size is under 8 and would otherwise be dropped.
- `--inframe "id;…"`: units whose label point is moved inside the frame when it falls outside, as above; for the Spring and Autumn and Warring States maps, use state names.

The settings for the current nine:

```bash
python3 tools/thumbs.py <Spring and Autumn index.html> --id cq --year -632 --box 105.5 122.5 28.6 41.0 --fs "淮夷=8;舒=8"
python3 tools/thumbs.py <Warring States index.html> --id zg --year -300 --box 102.6 124.2 25.6 42.4
python3 tools/thumbs.py <Qin and Han index.html>    --id qh --mode pol --box 78 132 16 50   # opening node: 108 BC
python3 tools/thumbs.py <Late Han index.html>       --id hs --year 229 --mode zhen --box 97.5 125.5 19 43
python3 tools/thumbs.py <Jin index.html>            --id lj --mode pol                 # opening node: 401
python3 tools/thumbs.py <Sui–Tang index.html>       --id st --mode pol                 # opening node: 619
python3 tools/thumbs.py <Tang–Song index.html>      --id ts --year 820 --mode zhen --box 95 127.5 19 46.5 --inframe 2 --fs "19=10"   # Tibet, Silla
python3 tools/thumbs.py <Song–Yuan index.html>      --id sy --year 1120 --mode pol --inframe 86   # Tibetan tribes
python3 tools/thumbs.py <Republican index.html>     --id mg --month 1937.07 --box 78 146 17 55 --zh "80=陕甘苏区" --fs "80=9.5;98=0" \
    --en "80=Shaanxi-Gansu Soviet Area"         # 1937.07, Lugou Bridge Incident, colored by faction (the map opens on 1937.12)
```
