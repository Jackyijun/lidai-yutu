# The Spring and Autumn Period

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

An interactive historical map of the Spring and Autumn period (770–476 BC): the territories of the states at 46 points in time (opening with 772 BC, the year before Western Zhou fell); 60 states (Zhou, Jin, Chu, Qi, Qin, Lu, Song, Wey, Zheng, Chen, Cai, Cao, Xu, Yan, Wu and Yue, and lesser states such as Guo, Yu, Xing, Ji, Ju, Zhu, Qunshu and Xu) and 7 Rong and Di tribal peoples (Red Di, White Di, Mountain Rong, Western Rong, Rong of the Yi and Luo, Dali Rong, Huai Yi); ancient and modern names for more than 200 capitals, cities, towns and passes; and battles, covenants and cultural events, the Fangcheng wall of Chu and the Long Wall of Qi, canals, mountains and rivers, and the neighbouring peoples. The interface is bilingual: switch with the "中 | EN" control at the top right of the map.

The map runs straight into the [Warring States map](https://jackyijun.github.io/zhanguo-map/): the two share the same ownership points and the same travel-cost grid, so the last node here (476 BC) and the first Warring States node (475 BC) have pixel-identical territories and colours.

---

## 1. Just open it

Double-click **`docs/index.html`** and open it in any modern browser (Chrome, Edge, Safari, Firefox).

The file is about 1 MB, with all data, styles and scripts embedded: it needs no network, no server and no external libraries. You can copy it to a USB stick, send it to someone, or put it on your own website.

---

## 2. Online

https://jackyijun.github.io/chunqiu-map/

---

## 3. Build locally

You only need to rebuild after changing the historical content (`content/`) or the parameters (`src/config.py`). **Python 3.9 or later** is required.

**macOS / Linux**

```bash
cd chunqiu-map
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py --open
```

**Windows (PowerShell)**

```powershell
cd chunqiu-map
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py --open
```

A full build takes about a minute and then opens the newly built `docs/index.html` in your browser.

| Command | What it does |
|---|---|
| `python run.py` | Download the base map if missing → compute territories → assemble the HTML |
| `python run.py --html` | Reassemble the HTML only (when you changed only `src/template.html`, text in `content/features.py`, or the English in `content/en/`; under a second) |
| `python run.py --draft` | Build even when English translations are missing or out of date (missing ones temporarily show the Chinese); for previews only. Without it the build stops and lists what is missing |
| `python run.py --open` | Open the result in a browser after building |
| `python run.py --preview -632,-546` | Also draw rough territory sketches for these nodes to `build/preview.png`, to check the ownership data |
| `python tools/preview.py -632 110,119,32,38` | Draw sketches only, optionally for a given extent (west,east,south,north) |

The base map data (`geodata/ne/`, about 23 MB) ships with the project, so it builds offline. If you delete it, `run.py` downloads the pinned version (Natural Earth v5.1.2) from GitHub.

The same input always produces a byte-for-byte identical build, so changes can be tracked with git.

When the build finishes, commit docs/index.html along with your changes and push to main; the online page updates automatically.

---

## 4. Directory layout

```
chunqiu-map/
├── run.py                 one-step build
├── requirements.txt
├── docs/
│   ├── index.html         ★ the finished map, a single file (GitHub Pages serves it)
│   └── .nojekyll          tells GitHub Pages to publish the files as they are
├── README.md · README.en.md   Chinese · English documentation
├── content/               ★ historical content (hand-written; this is what you edit)
│   ├── seeds.txt          468 ownership points: name, coordinates, which state held it when
│   │                      (shared with the Warring States map; identical in both repositories)
│   ├── features.py        state profiles, colours, tribal peoples and aliases; 46 time nodes and their
│   │                      timeline labels; capitals, battles, passes, major cities, towns, events and
│   │                      covenants, the Fangcheng and the Qi Long Wall, mountains, rivers, lakes and
│   │                      marshes, canals, peoples, and the fall of each state
│   └── en/                English translations
│       ├── items.json     entries (states, capitals, battles, towns, mountains, rivers…)
│       ├── snaps.json     titles, short labels and summaries of the time nodes
│       ├── misc.json      modern provinces, fall-of-state entries, period aliases
│       ├── zh.lock.json   fingerprint of the Chinese each English string was translated from
│       └── GLOSSARY.md    translation conventions
├── src/
│   ├── config.py          ★ all paths and tunable parameters (grid, costs, smoothing…) and the cost-grid check value COST_SHA
│   ├── fetch_data.py      downloads the Natural Earth base map
│   ├── build.py           computes territories, writes build/geo.json
│   ├── assemble.py        merges the English, checks for missing translations, injects the data into the template, writes docs/index.html
│   ├── i18n.py            shared English-version code: list of translatable fields, fingerprints
│   └── template.html      front end: page structure, styles, interaction script (including Chinese and English interface text)
├── geodata/
│   ├── prov.json          modern provincial boundaries (simplified, pre-encoded)
│   └── ne/                Natural Earth 1:10m GeoJSON (land, minor islands, rivers, lakes)
├── tools/
│   ├── preview.py         matplotlib territory sketches
│   └── i18n.py            English maintenance: status · todo · lock · table
└── build/                 intermediate files (safe to delete)
```

The files in `src/` derive from those of the same name in the Warring States repository, and the territory algorithm is identical. This map additionally has two colourings, States | Suzerain: `build.py` also computes the outline of the Zhou realm for each node, `assemble.py` also merges `ALLEGIANCE`, and `template.html` adds the colouring buttons and a drop-down for views.

---

## 5. How it works

```
content/seeds.txt ──┐
content/features.py ┼─► build.py ─► build/geo.json ─► assemble.py ─► docs/index.html
geodata/ (base map) ┘                                    ▲
                          content/features.py + content/en/ + src/template.html
```

### 1. Why the territories are computed

There are no boundary data for the Spring and Autumn period; what the sources do settle is mostly "such a town belonged to such a state in such a year" or "such a state destroyed such a state". So only the **place → state** ownership and the years it changed are written by hand (`seeds.txt`), and a travel-cost map lets the computer infer the boundaries between states, keeping them on ridges and large rivers where possible.

### 2. Steps in `build.py`

1. **Land**: clip East Asian land from Natural Earth, simplify and encode it.
2. **Cost grid**: one cell per 0.05°. Land costs 1, sea 4.5; every mountain range adds cost according to its "barrier weight", and the ancient Yellow River, the Ji, Yi and Beiluo rivers and the Yangtze, Han and Zhang also add cost; a layer of smooth noise with a fixed random seed is added on top. This grid is identical to the Warring States map's; `COST_SHA` in `config.py` checks it on every build.
3. **Multi-source shortest paths**: a Dijkstra search runs from the ownership points active that year, and each cell goes to the point that is "nearest to walk to". Nodes with the same set of points share one search.
4. **Colouring each node**: look up which state each point belonged to that year, merge the cells into each state's area, smooth with a Gaussian, trace and simplify the outlines. Labels go at the point of each state's largest land area farthest from its edge.
5. **Rivers and lakes**: Natural Earth rivers are matched to ancient names by their English names; the old course of the Yellow River, the Ji, Beiluo, Yi, Luo, Ru, Ying, Si and other rivers are drawn by hand.
6. **Place ownership**: each city, pass and battle looks up whose cell it falls in and takes that point's ownership history, so the tooltip can say "held by such a state in such a year".

### 3. `seeds.txt` syntax

One point per line:

```
name longitude latitude initial-owner [year+owner ...] [~year]
```

- `·` means not held by any of the Zhou states (land of the Rong, Di, Man and Yi, or blank); tribal peoples have their own keys (e.g. `赤狄`, `白狄`).
- Years BC are negative: `-655晋` means held by Jin from 655 BC.
- `~-350` means the point stops taking part in the partition from 350 BC. Every point added for the Spring and Autumn states, the Rong and Di and the early Warring States carries it; from 350 BC only the original Warring States points are used, so the Warring States map's territories from 350 BC on are exactly what they were before these points were added.

Examples:

```
陕 111.2 34.76 虢 -655晋 -453魏 -324秦
潞 113.2 36.1 赤狄 -594晋 -453韩 -262赵 -260秦 -257赵 -247秦
下阳 111.3 34.83 虢 -658晋 -453魏 ~-350
许叶 113.52 33.58 申 -688楚 -576许 -533楚 -529许 -524楚 -506许 -390楚 ~-350
```

### 4. Continuity with the Warring States map

- `content/seeds.txt` is identical in both repositories, and so are the geometry and barrier weights of the mountains and hand-drawn boundary rivers (checked by `COST_SHA`).
- No line changes owner in 475 BC, so this map's 476 BC node and the Warring States map's 475 BC node use the same points, the same grid and the same ownership: their territory polygons and label positions are byte-for-byte identical.
- States on both maps (28 of them, including Qin, Chu, Qi, Jin, Zheng, Wu and Yue) have the same key and the same colour: their light and dark values in `STATE_COLORS` in `features.py` are identical.
- The continuity applies to States colouring. Suzerain colouring exists only on this map, not on the Warring States map.
- When you change `seeds.txt` or the mountains and boundary rivers on one map, make the same change on the other and rebuild both.

### 5. What is in `features.py`

| Name | Contents |
|---|---|
| `STATES` · `STATE_COLORS` | Clan names and profiles of the 67 states and tribal peoples, and light / dark territory colours |
| `STATE_KIND` · `STATE_ALIAS` | Tribal peoples (pale fill, dashed edge, not counted as states); period aliases (Zhongshan labelled "Xianyu" before 506 BC; the Rong of the Yi and Luo labelled "Luhun Rong" from 638 BC) |
| `ALLEGIANCE` | Suzerain colouring: which states are independent and from which year, with the grounds (Chu claims kingship in 704 BC, sends tribute and receives sacrificial meat in 671 BC, asks about the tripods in 606 BC; Wu claims kingship in 585 BC; Yue, Shu and others stand outside the Zhou feudal order, and the rulers of Xu style themselves king). States not listed acknowledge Zhou |
| `SNAPS` · `SNAP_SHORT` | 46 time nodes (772 BC is the opening node): year, title, a summary; the short labels set vertically on the timeline |
| `FIRST` · `PERIOD0` · `PLAY_MS` | The node shown first (632 BC), the start of the first node's period (781 BC, accession of King You), playback interval |
| `CAPITALS` | 91 capitals with start and end years (former capitals are shown as dashed squares) |
| `BATTLES` | 64 battles: year, outcome, commanders, course of events |
| `PASSES` · `CITIES` · `TOWNS` | Passes and fords, major cities, towns |
| `CULTURE` | 48 events, covenants, people and archaeological sites |
| `WALLS` · `RANGES` | The Fangcheng of Chu and the Long Wall of Qi; 24 mountain ranges |
| `NE_RIVERS` · `MANUAL_RIVERS` · `CANALS` · `MARSHES` · `NE_LAKES` · `LAKE_NOTES` · `RIV_OVERRIDE` | Ancient river names, hand-drawn rivers, canals (the Hangou and Heshui, shown from the year they were dug), ancient marshes, lakes |
| `PEOPLES` | 20 labels for neighbouring peoples, shown in the years they existed |
| `FALLS` | The fall of each state in the chronology: year, state, what happened |

### 6. Display rules

- Battles are shown only for the **current period**, i.e. after the previous node (exclusive) up to this node (inclusive); the caption bar lists "Battles this period", and clicking one locates it.
- Events, walls and canals appear only once they have happened; capitals show only the current capitals and former ones.
- Tribal peoples have pale, dash-edged territories and italic labels and are not counted in the header.
- The legend lists only the states alive in this period and those that fell in it (struck through), tribal peoples last.
- Zoom levels: the full view shows only state names, capitals and battles; passes, major cities, towns and modern names appear as you zoom in.
- Two colourings, switched in the header: **States** (each state in its own colour, the default) and **Suzerain**. In Suzerain colouring the Zhou royal domain takes the Zhou colour; states enfeoffed by Zhou that have not claimed kingship acknowledge Zhou and take a paler Zhou colour with hatching (nominally under Zhou, self-governing in practice); states that claim kingship or stand outside the Zhou feudal order are independent and keep their own colours; Chu, after claiming kingship, sent tribute to the Zhou king and received his gifts, so it also counts as acknowledging Zhou from 671 to 607 BC; tribal peoples are unchanged. A heavy line traces the outline of the Zhou realm formed by the royal domain and the states that acknowledge Zhou.
- Views are chosen from a drop-down (All, Central Plains, Jin & Qin, Qi & Lu, Jiang–Han, Wu & Yue).

---

## 6. Common changes

| To do this | Edit | Then run |
|---|---|---|
| Change who held a town in a given year | the matching line in `content/seeds.txt` (syntax above); **make the same change in the Warring States repository** | `python run.py` in both |
| Add a town, pass, battle or event | add a line to the matching list in `content/features.py` | `python run.py --html` |
| Add a time node | add a line to `SNAPS` (year, title, summary) and a short label to `SNAP_SHORT` | `python run.py` |
| Change descriptive text | the notes and node summaries in `features.py` | `python run.py --html` (it will report the matching English as out of date; see the next section) |
| Change the English | `content/en/*.json` | `python tools/i18n.py lock` → `python run.py --html` |
| Change colours | `STATE_COLORS`; for states on both maps, change the Warring States map too | `python run.py --html` |
| Change allegiances in Suzerain colouring | `ALLEGIANCE` (add the English if you change the grounds) | `python run.py` |
| Change interface text | `U` in `src/template.html` (`zh` and `en` sets) | `python run.py --html` |

---

## 7. English version

`docs/index.html` contains both a Chinese and an English interface, Chinese by default; switch with "中 | EN" at the top right of the map. The choice is remembered in the browser, and adding `#en` to the address opens the English directly. In English mode the map is labelled in English only; tooltips, the index, the chronology and the gazetteer add the Chinese name in small type after the English. Search matches both Chinese and English, case-insensitively.

- **The Chinese is the source text.** The English is stored separately in `content/en/` by file, key and field: entries use the key `category:ancient-name` (a second entry of the same category and name gets `#2`), nodes use the year, modern provinces `prov:name`, fall-of-state entries `fall:year`, period aliases `alias:key:name`.
- **Fingerprints.** `zh.lock.json` records the first 10 hex digits of the SHA-1 of the Chinese each English string was translated from. When the Chinese changes, the English counts as out of date; `assemble.py` is strict by default and stops on anything missing or out of date, and only `--draft` lets it through.
- **Tools.** `python tools/i18n.py status` shows counts of missing and out-of-date strings; `todo` exports the Chinese still to translate; `table` exports a Chinese–English table `build/i18n_table.csv`; `lock` records fingerprints.
- **Conventions** are in `content/en/GLOSSARY.md`; they match the Warring States map's, and names shared by the two maps are translated identically.

---

## 8. Tuning

All tunable parameters are in `src/config.py`. **The grid, cost and noise parameters must be the same on both maps**: if you change one, `COST_SHA` stops the build; change both maps together and update the check value.

| Parameter | Effect |
|---|---|
| `RES` | Grid cell size |
| `SEA_COST` | Cost of crossing the sea |
| `NOISE_SEED` · `NOISE_AMP` | Random seed and amplitude of the boundary wobble |
| `RANGE_WIDTH` · `RIVER_COST` | Width of the ridge barrier band, cost of boundary rivers |
| `SMOOTH_SIGMA` · `POLY_SIMPLIFY` | Outline smoothing and simplification tolerance (these affect only the tracing; each map may set its own, but the handoff node is then no longer byte-for-byte identical) |

---

## 9. Sources and reliability

- **Territories**: inferred from the *Zuozhuan*, the *Shiji*, the *Guoyu*, the *Bamboo Annals* and other sources, and from the general outline of the Spring and Autumn maps in volume 1 of Tan Qixiang's *Historical Atlas of China*; compiled with AI assistance and not checked line by line against the original texts. The overall picture and the key years (e.g. Jin's conquest of Guo and Yu in 655 BC, Chengpu in 632 BC, Bi in 597 BC, Qi's conquest of Lai in 567 BC, Wu entering Ying in 506 BC, Song's conquest of Cao in 487 BC, Chu's conquest of Chen in 478 BC) are fairly reliable; the extent of the early states and of the margins (the Rong and Di, the Shu states, the lands south of the Yangtze, Ba and Shu) is rougher.
- **Boundaries**: entirely inferred, schematic lines. They only mean "this area belonged to this state".
- **Lesser states and tribal peoples**: the period had more than a hundred states; the map draws sixty. Lesser states not drawn separately (e.g. Wen, Yuan, Ying, Jiang, Su, Zhuanyu) are merged into a larger neighbour. The distribution of the Rong and Di follows scattered records in the *Zuozhuan* and is schematic.
- **Disputed points** are marked "one view" or "location disputed" on the map, e.g. the Chu capital Danyang, Old Jiang, the early Zhu capital and the moves of Qi (杞) eastward; early Chu draws on both the Dan–Xi and the Jing–Ju theories. The ends of Sui (Zeng) and Xu are not recorded; the map shows them at c. 360 and c. 390 BC.
- **English**: names and notes were translated by AI and independently reviewed; conventions are in `content/en/GLOSSARY.md`. Where the English and the Chinese disagree, the Chinese prevails.
- **Base map**: Natural Earth 1:10m (public domain); modern provincial boundaries are reused from the author's earlier map.

Corrections are welcome.
