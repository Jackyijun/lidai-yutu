# 历代舆图

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

历代形势图的总览页，依次是题签页眉、时间长卷、图卷目录、凡例。目录里每一卷链到它自己的 GitHub Pages：

| 卷次 | 图 | 地址 |
| --- | --- | --- |
| 卷一 | 春秋列国形势图（前770 — 前476） | https://jackyijun.github.io/chunqiu-map/ |
| 卷二 | 战国列国形势图（前475 — 前212） | https://jackyijun.github.io/zhanguo-map/ |
| 卷三 | 汉末三国形势图（184 — 280） | https://jackyijun.github.io/hanmosanguo-map/ |
| 卷四 | 两晋十六国南北朝形势图（280 — 581） | https://jackyijun.github.io/liangjin-nanbeichao-map/ |
| 卷五 | 隋及唐初形势图（581 — 669） | https://jackyijun.github.io/suitang-map/ |
| 卷六 | 唐末五代形势图（755 — 979；地图本身题「唐宋之际形势图」） | https://jackyijun.github.io/tangsong-map/ |
| 卷七 | 宋辽夏金元形势图（979 — 1279） | https://jackyijun.github.io/songyuan-map/ |
| 卷八 | 民国至新中国初期形势图（1911 — 1954） | https://jackyijun.github.io/minguo-xinzhongguo-map/ |

卷一、卷二首尾相接：春秋图末节点（前476）与战国图首节点（前475）的疆域、配色完全一致。卷三、卷四、卷五也首尾相接：两晋图照搬了两头的衔接节点，首节点与汉末三国图末节点（280），末节点与隋唐图首节点（581）的疆域、配色完全一致。

`index.html` 是自包含的：样式、脚本、八幅缩略图都写在文件里，不加载任何外部资源。色板、字体、细线与各图的《历史形势图统一规范》一致，深浅色跟随系统。

线上地址：https://jackyijun.github.io/lidai-yutu/

## 中英双语

页面右上角「中 | EN」切换，默认中文。中文名「历代舆图」，英文名 Historical Atlas of China。

- 选择记在本机（localStorage 键 `lidai-yutu:lang`）；网址加 `#en` 直接打开英文，加 `#zh` 打开中文；`<html lang>` 随之切换。
- 从目录点进各卷时，链接带上当前语言（`#zh` / `#en`），各图按同样的语言打开。
- 页面文字成对写在同一处：`<span class="zh">…</span><span class="en" lang="en">…</span>`，按 `<html lang>` 只显示一种。时间长卷由页尾脚本生成，朝代与时代分段 `BANDS` 里每项也写了中英两个名字。
- 英文模式下标题与卷名换西文衬线体（Iowan Old Style、Palatino 一类），正文换系统无衬线体，取消中文的大字距，组头改为大写。竖排题签「历代舆图」和两方印保留不变，英文标题排在题签右侧。
- 卷名、主线、着色方式与统计用语都照各图自己的英文版：节点叫 snapshots，州府、州郡叫 prefectures，郡国、郡县叫 commanderies，藩镇写 fanzhen，方镇叫 regional commands，民国卷的城市叫 cities、派系与属地叫 factions and dependencies。卷六英文题名用 Late Tang and the Five Dynasties，与中文首页的「唐末五代」一致；地图本身的英文题名是 Between Tang and Song。
- 缩略图里画了中、英两组注记（`<g class="t-lab zh">`、`<g class="t-lab en">`），也按当前语言只显示一组。英文国名取自各图数据，见下文「生成缩略图」。

## 增加新卷

1. 复制一个 `<li class="juan">` 块，按时代先后放进目录，然后重排卷次（卷一、卷二……；Volume I、Volume II……）。
2. 改这几项：
   - `id`
   - `data-short`、`data-short-en`：时间长卷上显示的中、英短名
   - `data-start`、`data-end`：起止年
3. 改链接、缩略图（见下节），以及卷名、年代、主线、导语、`stats`、缩略图说明 `thumb-cap` 的中英两份。英文照该图自己的英文题名、副题和用语。
4. 在 `:root` 和两个深色块里各加一个 `--m-xx`，作为这一卷的主色，浅色、深色各一个值；`<li>` 上写 `style="--c:var(--m-xx)"`。主色要和时间长卷上相邻的色段分得开。
5. 改封面「凡八卷 · 前770 — 1954」与「Eight volumes · 770 BC – 1954」、目录组头「已成八卷」与「Eight volumes completed」，以及 `<meta name="description">`、`og:description` 和页尾脚本 `DESC` 里的卷名。
6. 如果新卷超出前800 — 1960 的范围，改页尾脚本里的 `R0`、`R1`、`TICKS`，并改「时间长卷」组头的年代范围。朝代与时代分段 `BANDS` 也在同一处（民国卷加入时补了明、清、民国、新中国四段）。

时间长卷不用另外改，它直接读目录里每卷的 `data-start` / `data-end` 画色段。卷名挤在一起时，每个卷名放进最低一行中放得下的那行，长卷随之加高；贴着长卷两端的卷名（如民国卷）会往里挪，不出边界。

### 预告编修中的卷

还没做完的图可以先放一张灰卡：

- `<li>` 加上 class `todo` 和属性 `data-todo="1"`，不写 `--c`。
- `<a class="juan-body" href="…">` 换成 `<article class="juan-body" aria-labelledby="…">`，指向卷名所在的 `<h2>`。
- 缩略图用 `--blank` 生成，后面加一个「编修中」印。印文作为图案保留中文，英文模式下也不换：

```html
<svg class="stamp" viewBox="0 0 96 40" aria-hidden="true">
  <g filter="url(#worn)">
    <rect x="2" y="2" width="92" height="36" rx="2" fill="none" stroke="var(--seal)" stroke-width="2.4"/>
    <rect x="6" y="6" width="84" height="28" rx="1" fill="none" stroke="var(--seal)" stroke-width=".9"/>
    <text x="48" y="20.5" font-size="17" letter-spacing="5" text-anchor="middle" dominant-baseline="central" style="fill:var(--seal);font-family:var(--f-cjk);font-weight:700">编修中</text>
  </g>
</svg>
```

- `stats` 写「编修中」/「In preparation」，`<span class="act">` 写「即将刊行」/「Coming soon」。
- 时间长卷上的这一卷自动画成虚框。

## 生成缩略图

`tools/thumbs.py` 从某张图自己的 `index.html` 里读出内嵌的 GEO / DATA，按那张图的投影和色板，把一个时间节点重绘成 360×270 的小图。只用 Python 3 标准库。

它能处理四种数据结构：

- 战国式（春秋、战国）：节点里有 `s` / `l`。`DATA.kinds` 标为 `tribe` 的戎狄部族画淡色虚线，与图里一致。
- 唐宋式：节点里有 `z` / `p` / `pol`。
- 汉末三国、两晋、隋唐、宋元式：疆域几何放在共享池 `GEO.pool` 里。两晋图的节点还可能带 `kd`（本节点改单位种类，如高句丽 313 年起由部族改按政权画）和 `col`（本节点覆盖单位的浅、深两色），缩略图照节点所记的画。
- 民国式：节点按月分，`t` 记月序号（年 × 12 + 月 − 1），标题存在 `ti`；投影中心取 `GEO.proj`，打开时的节点 `GEO.first` 也记月序号。缩略图说明的年代写成「年.月」，如 1937.12。

注记画中、英两组：

- 中文用当年的国名：春秋、战国先取节点的当年别名 `lab`（如前506年以前的「鲜虞」），再取政权条目的古名。
- 英文取自该图数据：春秋、战国先取节点的当年别名 `labe`，再取政权条目的 `eold`；其余各图依次取节点的当年别名 `labe`、单位的地图短名 `se`、全称 `ne`，去掉括注。
- 英文按估算字宽避让，长名在空格处折成两行，放不下就不标。
- 中文注记的字号随疆域大小定，注记不比疆域宽太多：由几个单位合成的政权原本至少 15px，放不下就照疆域缩小（民国卷的小政权多由几个单位合成，伪蒙疆、中共边区就因此被放得太大）。还可以用 `--zh` 改用短名、用 `--fs` 指定字号，见下。
- 图还没有英文时，用 `--en "编号=英文名;…"` 补缩略图的英文注记（编号即单位编号），它也优先于图里的英文名。

```bash
python3 tools/thumbs.py ../songyuan-map/docs/index.html --id sy --year 1120 --mode pol --out thumbs
```

运行后输出三份文件：

- `thumbs/thumb-sy.svg`：贴进对应卷的 `.thumb-in`。
- `thumbs/thumb-sy.css.txt`：两行颜色 token。浅色那行贴进 `:root`，深色那行贴进两个深色块，和已有的 `/* 缩略图 zg */` 等放在一起。
- `thumbs/thumb-sy.cap.txt`：该节点的年份和中英标题，用来写缩略图说明 `thumb-cap`。

参数：

- `--id`：两三个字母的代号，用作颜色 token 前缀和 clipPath id，各卷不能重复。
- `--year`：取哪一年的节点。
- `--node`：按序号取节点，从 0 数起。同一年有几个节点时用，比如隋唐图按月分节点。
- `--month 年.月`：按年月取节点，用于民国图这样按月分节点的图，如 `--month 1937.12`。
- `--year`、`--month`、`--node` 都不填时，取该图打开时的节点（`GEO.first` 记年份或月序号，`DATA.first` 记序号）；都没有就取第一个。
- `--box 西 东 南 北`：取景的经纬框。不填时用该图源码里 FITS 的 cn 或 all。
- `--mode zhen|pol`：分层模型的着色方式。`zhen` 是藩镇、诸侯、路或派系，为缺省值；`pol` 是政权。
- `--blank`：只画海陆、河流、经纬网，用于编修中的卷。
- `--en "编号=英文名;…"`：补或改英文注记，见上。
- `--zh "编号=中文名;…"`：改中文注记，如用短名（伪蒙疆联合委员会写作「伪蒙疆」）或改称：中共所辖地区在地图上是「中共（边区·根据地）」「中华苏维埃共和国」这类总称，缩略图上按注记所在之地写，1937.07 写作「陕甘苏区」，1937.12 写作「陕甘宁边区」。
- `--fs "编号=字号;…"`：指定中文注记字号（英文随之按 0.82 倍）；写 0 就不标，用于被说明框盖住的注记。

现有八幅的参数：

```bash
python3 tools/thumbs.py <春秋 index.html>       --id cq --year -632 --box 105.5 122.5 28.6 41.0
python3 tools/thumbs.py <战国 index.html>       --id zg --year -300 --box 102.6 124.2 25.6 42.4
python3 tools/thumbs.py <汉末三国 index.html>   --id hs --year 229 --mode zhen --box 97.5 125.5 19 43
python3 tools/thumbs.py <两晋 index.html>       --id lj --mode pol                 # 打开时的节点：401
python3 tools/thumbs.py <隋及唐初 index.html>   --id st --mode pol                 # 打开时的节点：619
python3 tools/thumbs.py <唐宋 index.html>       --id ts --year 820 --mode zhen --box 95 127.5 19 46.5
python3 tools/thumbs.py <宋辽夏金元 index.html> --id sy --year 1120 --mode pol
python3 tools/thumbs.py <民国 index.html>       --id mg --month 1937.07 --box 78 146 17 55 --zh "80=陕甘苏区" --fs "80=9.5;98=0" \
    --en "80=Shaanxi-Gansu Soviet Area"         # 1937.07 七七事变，派系着色（地图打开时是 1937.12）
```
