# Historical Atlas of China

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

The index page of the historical map series, in order: the title-slip header, the timeline, the contents and the notes. Each volume in the contents links to its own GitHub Pages site:

| Volume | Map | Address |
| --- | --- | --- |
| I | The Warring States (475–212 BC) | https://jackyijun.github.io/zhanguo-map/ |
| II | Late Han and the Three Kingdoms (184–280) | https://jackyijun.github.io/hanmosanguo-map/ |
| III | Sui and Early Tang (581–669) | https://jackyijun.github.io/suitang-map/ |
| IV | Late Tang and the Five Dynasties (755–979; the map itself is titled Between Tang and Song) | https://jackyijun.github.io/tangsong-map/ |
| V | Song · Liao · Xia · Jin · Yuan (979–1279) | https://jackyijun.github.io/songyuan-map/ |

`index.html` is self-contained: its styles, script and all five thumbnails are written into the file, and it loads no outside resources. Its palette, fonts and hairlines match the maps' shared style guide (历史形势图统一规范), and it follows the system's light or dark setting.

Live page: https://jackyijun.github.io/lidai-yutu/

## Bilingual

The 中 | EN switch at the top right changes the language; Chinese is the default. The Chinese name is 历代舆图 and the English name Historical Atlas of China.

- The choice is saved on the device (localStorage key `lidai-yutu:lang`). Adding `#en` to the address opens the English page, and `#zh` the Chinese one; `<html lang>` changes with it.
- Links from the contents into each volume carry the current language (`#zh` / `#en`), so each map opens in the same language.
- Page text is written in pairs in the same place: `<span class="zh">…</span><span class="en" lang="en">…</span>`, and only the one matching `<html lang>` is shown. The timeline is built by the script at the end of the page; each entry in its dynasty bands `BANDS` also carries a Chinese and an English name.
- In English the headings and volume titles switch to a Latin serif (Iowan Old Style, Palatino and the like) and the body text to the system sans-serif; the wide CJK letter-spacing is dropped and group headings are set in capitals. The vertical title slip 历代舆图 and the two seals stay as they are, with the English title set to the right of the slip.
- Volume titles, subtitles, coloring modes and the terms in the stats lines follow each map's own English version: time nodes are snapshots, 州府 and 州郡 are prefectures, 郡国 are commanderies, and 藩镇 is written fanzhen. Volume IV is titled Late Tang and the Five Dynasties in English, matching 唐末五代 on the Chinese page; the map's own English title is Between Tang and Song.
- Each thumbnail holds two sets of labels, Chinese and English (`<g class="t-lab zh">`, `<g class="t-lab en">`), and also shows only the one for the current language. The English names come from each map's data; see "Generating thumbnails" below.

## Adding a volume

1. Copy an `<li class="juan">` block, put it into the contents in date order, and renumber the volumes (卷一, 卷二 …; Volume I, Volume II …).
2. Change these:
   - `id`
   - `data-short`, `data-short-en`: the short Chinese and English names shown on the timeline
   - `data-start`, `data-end`: first and last year
3. Change the link and the thumbnail (see the next section), and both language versions of the title, years, subtitle, description, `stats` and the thumbnail caption `thumb-cap`. Take the English from that map's own English title, subtitle and terms.
4. Add an `--m-xx` to `:root` and to both dark blocks as the volume's main color, one light and one dark value, and write `style="--c:var(--m-xx)"` on the `<li>`. The color should stand apart from its neighbors on the timeline.
5. Update the cover's 「凡五卷 · 前475 — 1279」 and "Five volumes · 475 BC – 1279", the contents heading 「已成五卷」 and "Five volumes completed", and the volume names in `<meta name="description">` and in `DESC` in the script at the end of the page.
6. If the new volume falls outside 500 BC – 1350, change `R0`, `R1` and `TICKS` in the script at the end of the page. The dynasty bands `BANDS` are in the same place.

The timeline needs no other change: it draws each volume's bar straight from that volume's `data-start` / `data-end`.

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

It handles three data layouts:

- Warring States: nodes hold `s` / `l`.
- Tang–Song: nodes hold `z` / `p` / `pol`.
- Late Han, Sui–Tang and Song–Yuan: territory geometry sits in the shared pool `GEO.pool`.

Labels are drawn in two sets:

- Chinese labels use the state names of that year, as before.
- English is taken from the map's data. For the Warring States it is the `eold` of each state's entry. For the other maps it is, in order of preference, the node's period alias `labe`, the unit's short map name `se`, or its full name `ne`, with anything in parentheses removed.
- English labels are spaced by estimated text width, long names break onto two lines at a space, and a name that will not fit is left out.

```bash
python3 tools/thumbs.py ../songyuan-map/docs/index.html --id sy --year 1141 --mode pol --out thumbs
```

It writes three files:

- `thumbs/thumb-sy.svg`: paste it into that volume's `.thumb-in`.
- `thumbs/thumb-sy.css.txt`: two lines of color tokens. Paste the light line into `:root` and the dark line into both dark blocks, next to the existing `/* 缩略图 zg */` and the others.
- `thumbs/thumb-sy.cap.txt`: the node's year and its Chinese and English titles, for writing the thumbnail caption `thumb-cap`.

Options:

- `--id`: a two- or three-letter code, used as the color-token prefix and clipPath id. Each volume needs its own.
- `--year`: which year's node to draw.
- `--node`: pick the node by index, counting from 0. Use it when one year has several nodes, as in the Sui–Tang map, which has month-level nodes.
- With neither `--year` nor `--node`, the tool takes the node the map opens on (`GEO.first` holds a year, `DATA.first` an index), or else the first node.
- `--box W E S N`: the longitude/latitude frame. Without it the tool uses FITS cn or all from the map's source.
- `--mode zhen|pol`: coloring for the layered model. `zhen` (fanzhen, warlords or circuits) is the default; `pol` colors by state.
- `--blank`: draw only land, sea, rivers and the graticule, for a volume in preparation.

The settings for the current five:

```bash
python3 tools/thumbs.py <Warring States index.html> --id zg --year -300 --box 102.6 124.2 25.6 42.4
python3 tools/thumbs.py <Late Han index.html>       --id hs --year 229 --mode zhen --box 97.5 125.5 19 43
python3 tools/thumbs.py <Sui–Tang index.html>       --id st --mode pol                 # opening node: 619
python3 tools/thumbs.py <Tang–Song index.html>      --id ts --year 820 --mode zhen --box 95 127.5 19 46.5
python3 tools/thumbs.py <Song–Yuan index.html>      --id sy --year 1141 --mode pol
```
