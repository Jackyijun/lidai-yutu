# Jin, Sixteen Kingdoms and Northern and Southern Dynasties

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

280–581, from the Western Jin conquest of Wu that reunified the realm to Emperor Wen of Sui replacing the Zhou, in 122 snapshots: the War of the Eight Princes, the Disaster of Yongjia, the Sixteen Kingdoms of the Five Hu, the Eastern Jin and the Southern Dynasties of Song, Qi, Liang and Chen, the Northern Wei's unification of the north, the Eastern and Western Wei and Northern Qi and Northern Zhou, up to the founding of the Sui. The view reaches the Eastern Roman Empire and Sasanian Persia in the west, the steppe north of the Gobi in the north, and Simhala and the states of the Southern Seas in the south — everything in contact with the Chinese world is on the map. It has a regional-command coloring, 15 campaign and journey routes (Zu Ti's northern expedition, Faxian's journey west, Liu Yu's northern expeditions, Hou Jing's rebellion and others), historical and modern place names, a timeline and a gazetteer, in Chinese and English. A single web page with no outside dependencies.

The map joins seamlessly with the Late Han and Three Kingdoms map and the Sui and Early Tang map: the 280 snapshot copies the borders, colors and state names of the last snapshot of the Late Han and Three Kingdoms map, and the 581 snapshot copies the first snapshot of the Sui and Early Tang map, so the three volumes read as one (see section 5, "Joining the neighboring maps").

## 1. Just open it

Open `docs/index.html` in a browser; it works offline. The 中 | EN switch at the top right changes the language.

- **Timeline**: one cell per snapshot, with the Jin or Southern Dynasties era of that year under it; the eras of the northern states are given at the start of the caption. Tick dots with a dashed ring are Western Jin, with a solid ring Eastern Jin and the Sixteen Kingdoms, square dots the Northern and Southern Dynasties. ▶ plays the timeline, and the 1× / 2× button next to it changes the speed; ← → step through the snapshots.
- **Coloring**: "States" colors by state; "Commands" colors the Western Jin princes, the regional commands of the Eastern Jin and Southern Dynasties, and the Erzhu, Gao Huan and others at the end of the Northern Wei separately. Hatching marks nominal vassals that were in fact independent; dashed territories are tribes.
- **Views**: the drop-down has 23 views, from "Eight Princes & Yongjia", "Sixteen Kingdoms & the north" and "North–South division" to "Sasanians & Eastern Rome", "India & Simhala" and "Southern Seas".
- Battles and events are shown only for the period covered by the current snapshot (after the previous snapshot, up to this one); for campaign routes, the stretch covered in the current period is drawn solid with arrows, earlier stretches dashed. Click any territory, town, battle, mountain or river for a note.

## 2. Live page

https://jackyijun.github.io/liangjin-nanbeichao-map/

## 3. Building locally

Requires Python 3.10 or later.

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                 # full rebuild, about 1.5 minutes, writes docs/index.html
python run.py --html          # only content/ allegiances or text changed: reuse the computed territory, about half a minute
python run.py --open          # open in a browser after building
python run.py --html --draft  # build the page even if English is missing or stale (missing English shows Chinese); strict by default
python run.py --preview 383   # also write a territory sketch for that year, build/preview-383.png
```

Rebuilding from the same input gives a byte-identical `docs/index.html` (the random seed is fixed).

When the build is done, commit `docs/index.html` along with your changes and push to `main`; the live page updates automatically (GitHub Pages publishes from `/docs`).

## 4. Layout

```
liangjin-nanbeichao-map/
├── run.py              one-step build
├── requirements.txt    numpy, scipy, shapely ≥ 2.1, scikit-image, matplotlib
├── README.md           description (Chinese)
├── README.en.md        description (English), matching README.md section by section
├── docs/
│   ├── index.html      the finished page, a single file
│   └── .nojekyll
├── content/            historical data (hand-written)
│   ├── seeds.py        560 allegiance points: 192 commandery/county seats and 133 towns (shown), 235 helper points used only for partitioning; with modern locations and name histories
│   ├── groups.py       point groups (#关中 Guanzhong, #河西 Hexi, #淮南 Huainan …) used when writing snapshots
│   ├── units.py        186 units: 101 states, 44 regional commands, 41 tribes; names, colors, notes
│   ├── snaps.py        how snapshots are written, and their collection; the snapshots themselves are in the four files below
│   ├── snaps_xijin.py  Western Jin, 280–316 (20 snapshots)
│   ├── snaps_dongjin.py Eastern Jin and the early Sixteen Kingdoms, 318–383 (27)
│   ├── snaps_shiliu.py later Sixteen Kingdoms, 384–439 (32)
│   ├── snaps_nanbei.py Northern and Southern Dynasties, 442–581 (43)
│   ├── items.py        notes for passes, mountains, rivers and lakes, canals and deserts (geometry from the Tang–Song map, text rewritten for this period)
│   ├── items_hist.py   87 capitals, 108 battles, 65 events, 24 peoples, 15 campaign and journey routes
│   ├── frontier.py     the outer edge of the map (east and north as in the Sui–Tang map, widened to the west and south)
│   └── en/             English: six json files (units, labels, seeds, items, snaps, misc), the zh.lock.json fingerprints and the GLOSSARY.md naming conventions
├── src/
│   ├── config.py       all paths and tunable parameters
│   ├── fetch_data.py   checks geodata/ and downloads pinned versions from GitHub if anything is missing
│   ├── build.py        computes territory, writes build/*.json
│   ├── basemap.py      base map: land, lakes, rivers, canals, deserts, modern national and provincial borders
│   ├── territory.py    the territory algorithm (see below)
│   ├── compile_data.py allegiance per snapshot → territory polygons → GEO / DATA; copies the neighbors' joining snapshots; colors
│   ├── items_build.py  compiles the entries: capitals, battles, events, landforms, routes, peoples
│   ├── proj.py         Albers equal-area conic projection (the same as in the page)
│   ├── i18n.py         English: checks for missing and stale translations and merges them into the data
│   ├── assemble.py     merges the English, checks for gaps, fills the template and writes docs/index.html
│   └── template.html   front end
├── geodata/            base map and joining data, shipped with the repository so it builds offline
│   ├── junction_hanmo280.json    territory rings, colors and names of the 280 snapshot of the Late Han and Three Kingdoms map
│   └── junction_suitang581.json  territory rings, colors and names of the 581 snapshot of the Sui and Early Tang map
├── tools/
│   ├── junction.py     re-extracts the joining data from the two neighboring maps' repositories
│   ├── i18n.py         English maintenance: status / todo / lock / table
│   └── preview.py      matplotlib territory sketch
└── build/              intermediate files
```

## 5. How it works

> From migration step 7 (17 November 2026) the territory on the new page in the single repository (`docs/liangjin-nanbeichao/`) is computed by the unified territory engine (`core/engine/`; the result is `engine.json` in this folder, recomputed automatically by `python run.py liangjin-nanbeichao` at the repository root). Ownership, text and entries still come from this volume. The two junction snapshots copy the neighboring volumes' engine geometry: the 581 snapshot within the Sui–Tang volume's hand-drawn outer edge, and the 280 snapshot (since the Late Han volume moved to the engine on 19 November 2026) within the Late Han volume's computed area; where the neighboring volume leaves land blank, this volume draws its own. What follows describes this volume's own older algorithm, now used only for the old page and `legacy.html`.

**Territory algorithm** (`src/territory.py`, parameters in `src/config.py`), taken over from the Sui and Early Tang map, with the same projection center (102°E / 36°N):

1. **Grid**: the projected plane is cut into equal cells about 6.4 km across, built only inside the map's outer edge (about 1676 × 1281 cells). Sea and lakes larger than 0.15 square degrees are impassable.
2. **Cost**: 1 on the flat, plus ETOPO20 slope and plateau altitude; mountain ridgelines burn in Gaussian bands of high cost (peak +8 for main ranges, +3.5 for minor ones) — this map adds the Hindu Kush, Caucasus, Taurus, Zagros, Alborz and Vindhya; the Yangtze, Yellow River, Huai and Han, the Oxus, the Jaxartes and the Euphrates add extra cost (the Huai weighs more than in the Sui–Tang map, since it was long the border between north and south); finally the cost is multiplied by ±38% multi-scale smoothed noise.
3. **Partition**: one 16-neighbor (knight's-move) multi-source Dijkstra from all 560 points assigns every cell to the point nearest in cost distance, giving each point its "sphere" — computed once.
4. **Outer edge**: hand-drawn in `content/frontier.py`. East and north as in the Sui–Tang map; west to the Aegean, taking in Eastern Roman Asia Minor, Syria and Egypt, the whole Sasanian realm, the Caucasus and the Arabian Peninsula, and the steppe north of the Black Sea and the Caspian; south to Simhala, the Malay Peninsula, Sumatra and Java.
5. **Tracing and polygons**: boundaries are traced where the smoothed values of two neighboring classes are equal, once for the whole map and shared by both sides, then given three rounds of Laplacian smoothing and a smooth displacement field, and finally simplified together with GEOS `coverage_simplify`. Neighboring spheres share the same edge, with no gaps or overlaps.
6. **Merging per snapshot**: each snapshot changes the allegiance of the one before (`own` overrides, `move` reassigns wholesale); `compile_data.py` merges the spheres into the territory of units (states, regional commands, tribes) and of states; labels go at the pole of inaccessibility of the largest landmass; geometry unchanged between snapshots is stored only once (`GEO.pool`).
7. **Colors**: states that exist in a joining year take the neighboring map's colors; the main states are chosen by hand; the rest are picked greedily from a low-chroma OKLCH palette according to their adjacency across all snapshots. Goguryeo and Linyi have different colors in the two neighboring maps, so their color shifts snapshot by snapshot from the Late Han map's to the Sui–Tang map's.

**The page**: `template.html` is adapted from the front end of the Sui and Early Tang map and, following the series style guide (历史形势图统一规范), adds the regional-command coloring, northern eras, multiple campaign routes, the promotion of tribes to states within a snapshot (Goguryeo, the Rouran and the Gaoche are drawn as states rather than tribes from a certain snapshot), per-snapshot colors and speed control; `assemble.py` replaces the four placeholders `__GEO__`, `__DATA__`, `__UCSS_LIGHT__` and `__UCSS_DARK__` with the data and writes a single file.

**Joining the neighboring maps** (section 18 of the style guide):

- **280**: inside the area where the Late Han and Three Kingdoms map computes territory (72°–136°E, 14.75°–55°N), the territory rings, label points, colors and names of Jin, the Xianbei, Buyeo, Goguryeo, the Qiang, the states of the Western Regions, Linyi and the "abandoned lands" are copied from that map's 280 snapshot; gaps that map leaves blank are filled by this map's states, and the area outside it is computed by this map. Between 280 and the next snapshot (289), the northwestern and northeastern borders switch to this map's own points, so there is one small jump.
- **581**: inside the outer edge of the Sui and Early Tang map, 41 units — Sui, Chen, the Later Liang, the Turks, the Tuyuhun, Goguryeo, Baekje, Silla, Wa and others — are copied from that map's 581 snapshot; the commandery names switch in 581 to that map's Kaihuang prefecture names, and the capital names of Sui, Goguryeo, Wa, Gaochang, the Tibetan Empire and Yangtong match it. The snapshot summary is also taken from that map; the English names of states and places shared with the two maps follow their English.
- `tools/junction.py` extracts the two sets of joining data from the neighboring maps' repositories:

```bash
python tools/junction.py ../hanmosanguo-map ../suitang-map
python run.py
```

If a neighboring map changes its joining snapshot, run these two lines again. The build checks that the territory rings, label points and light and dark colors copied into the joining snapshots match the neighboring map (for units reaching beyond the neighbor's area, only the part inside it is compared), and stops if they do not.

## 6. Common changes

- **Change an allegiance in a snapshot**: edit the snapshot's `own` in `content/snaps_*.py` (unit → list of points; `#关中` and the like are groups in `groups.py`), then `python run.py --html`. Within one snapshot, a unit written later takes precedence.
- **Add a commandery, county or helper point**: add a line to `content/seeds.py` (`key|name|modern place|longitude|latitude|type|region|name history`; type z commandery seat, c town, r partitioning only), assign it in the snapshots, then `python run.py` (the spheres must be recomputed).
- **Change notes, battles, events, capitals or routes**: edit `content/items_hist.py`, `items.py` or `units.py`, then `python run.py --html`. Route points are written as (longitude, latitude, year + month/12, place name).
- **Change the outer edge**: edit `content/frontier.py`, then `python run.py`.
- **Change style or interaction**: edit `src/template.html`, then `python run.py --html`.
- **Whenever you change Chinese text**, change the English to match and run `python tools/i18n.py lock`; otherwise the build stops (see below).

## 7. English version

The 中 | EN switch at the top right changes the language; Chinese is the default. Adding `#en` to the address opens the English page directly, and the choice is saved on the device (localStorage key `liangjin-nanbeichao-map:lang`). In English the map shows only English labels; tooltips, the index, the timeline and the gazetteer add the original Chinese after each English name. The northern eras, the notes on the joining snapshots, the view names and the legend footnote are all in English as well.

- **Translations** live in `content/en/`: `units.json` for states, regional commands and tribes (full name, map label, note), `labels.json` for period names in the snapshots, `seeds.json` for commanderies, counties and towns (modern place and the names of each period), `items.json` for entries (keyed by `category:historical name`, with @state or @modern place added for duplicates; route place names under p), `snaps.json` for snapshots (era, northern era, title, summary) and `misc.json` for modern province names. `src/i18n.py` merges them in at build time.
- **Staleness check**: `content/en/zh.lock.json` records a fingerprint (the first 10 characters of a sha1) of the Chinese each English text was written from. If the Chinese changes and the English does not, the build reports it as stale and stops; `python run.py --html --draft` builds a draft anyway.
- **Maintenance**: `python tools/i18n.py status` counts missing and stale entries; `todo` lists the Chinese still to translate; `lock` records the fingerprints after the English has been updated; `table` exports a side-by-side table, `build/i18n-review.tsv`.
- **Conventions**: see `content/en/GLOSSARY.md`. Names are translated the same as in the Late Han and Three Kingdoms and the Sui and Early Tang maps; 州 as an administrative region is "X Province", as the name of a seat it is written as in the Sui–Tang map (Yongzhou); lunar months are given as they are ("3rd month, 383") without conversion; battles with the same name get a year.

## 8. Tuning

All in `src/config.py`:

| Parameter | Effect |
| --- | --- |
| `PX` | cell size; smaller gives finer borders and a slower build |
| `RIDGE_MAJOR` / `RIDGE_MINOR` / `RIDGE_W` | height and width of the ridge bands; higher keeps borders closer to ridgelines |
| `BORDER_RIVERS` | border rivers and their extra cost |
| `NOISE_AMP` / `NOISE_SCALES` | cost noise; larger gives more winding borders |
| `WARP` | scale and amplitude (in cells) of the displacement field |
| `SMOOTH_SIGMA` / `LAPLACE` | Gaussian smoothing before tracing and network smoothing after |
| `SIMPLIFY` | coverage simplification tolerance; larger gives a smaller file and more angular borders |
| `SEED` | random seed |

## 9. Sources and reliability

Borders are inferred in outline from the Book of Jin, the eight histories of the Northern and Southern Dynasties (Book of Song, Book of Southern Qi, Book of Liang, Book of Chen, Book of Wei, Book of Northern Qi, Book of Zhou, History of the Southern Dynasties, History of the Northern Dynasties), the Zizhi tongjian, the reconstituted Annals of the Sixteen Kingdoms and vols. 3–4 of Tan Qixiang's Historical Atlas of China; territory is assigned commandery by commandery and bounded along mountains and rivers, so it is only indicative. The Sixteen Kingdoms changed hands so often that places which changed masters several times in one year are drawn as they stood at the year's end; regional commands and dependencies that were nominal vassals but in fact independent are hatched; the peoples of the steppe and the plateau had no fixed borders. Sasanian Persia, Rome, India and the states of the Southern Seas are drawn only in broad outline, following standard world-history atlases. Modern locations are those of the site or the city it lies in.

Base map: Natural Earth 5.1.2 (land, lakes, rivers, modern national borders) and ETOPO20 relief (shipped with matplotlib/basemap 1.4.1); rivers, lakes and canals, modern provincial borders and some landforms and passes come from the Between Tang and Song map.
