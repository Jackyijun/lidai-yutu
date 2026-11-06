# 历代舆图

历代形势图的总览页，依次是题签页眉、时间长卷、图卷目录、凡例。目录里每一卷链到它自己的 GitHub Pages：

| 卷次 | 图 | 地址 |
| --- | --- | --- |
| 卷一 | 战国列国形势图（前475 — 前212） | https://jackyijun.github.io/zhanguo-map/ |
| 卷二 | 汉末三国形势图（184 — 280） | https://jackyijun.github.io/hanmosanguo-map/ |
| 卷三 | 隋及唐初形势图（581 — 669） | https://jackyijun.github.io/suitang-map/ |
| 卷四 | 唐末五代形势图（755 — 979；地图本身题「唐宋之际形势图」） | https://jackyijun.github.io/tangsong-map/ |
| 卷五 | 宋辽夏金元形势图（979 — 1279） | https://jackyijun.github.io/songyuan-map/ |

`index.html` 是自包含的：样式、脚本、五幅缩略图都写在文件里，不加载任何外部资源。色板、字体、细线与各图的《历史形势图统一规范》一致，深浅色跟随系统。

线上地址：https://jackyijun.github.io/lidai-yutu/

## 增加新卷

1. 复制一个 `<li class="juan">` 块，按时代先后放进目录，然后重排卷次（卷一、卷二……）。
2. 改这几项：
   - `id`
   - `data-short`：时间长卷上显示的短名
   - `data-start`、`data-end`：起止年
3. 改链接、缩略图（见下节）、卷名、年代、主线、导语、`stats` 和缩略图说明 `thumb-cap`。
4. 在 `:root` 和两个深色块里各加一个 `--m-xx`，作为这一卷的主色，浅色、深色各一个值；`<li>` 上写 `style="--c:var(--m-xx)"`。主色要和时间长卷上相邻的色段分得开。
5. 改封面上的「凡五卷 · 前475 — 1279」和目录组头「已成五卷」。
6. 如果新卷超出前500 — 1350 的范围，改页尾脚本里的 `R0`、`R1`、`TICKS`。朝代分段 `BANDS` 也在同一处。

时间长卷不用另外改，它直接读目录里每卷的 `data-start` / `data-end` 画色段。

### 预告编修中的卷

还没做完的图可以先放一张灰卡：

- `<li>` 加上 class `todo` 和属性 `data-todo="1"`，不写 `--c`。
- `<a class="juan-body" href="…">` 换成 `<article class="juan-body" aria-label="…，编修中">`。
- 缩略图用 `--blank` 生成，后面加一个「编修中」印：

```html
<svg class="stamp" viewBox="0 0 96 40" aria-hidden="true">
  <g filter="url(#worn)">
    <rect x="2" y="2" width="92" height="36" rx="2" fill="none" stroke="var(--seal)" stroke-width="2.4"/>
    <rect x="6" y="6" width="84" height="28" rx="1" fill="none" stroke="var(--seal)" stroke-width=".9"/>
    <text x="48" y="20.5" font-size="17" letter-spacing="5" text-anchor="middle" dominant-baseline="central" style="fill:var(--seal);font-family:var(--f-display);font-weight:700">编修中</text>
  </g>
</svg>
```

- `stats` 写「编修中」，`<span class="act">` 写「即将刊行」。
- 时间长卷上的这一卷自动画成虚框。

## 生成缩略图

`tools/thumbs.py` 从某张图自己的 `index.html` 里读出内嵌的 GEO / DATA，按那张图的投影和色板，把一个时间节点重绘成 360×270 的小图。只用 Python 3 标准库。

它能处理三种数据结构：

- 战国式：节点里有 `s` / `l`。
- 唐宋式：节点里有 `z` / `p` / `pol`。
- 汉末三国、隋唐、宋元式：疆域几何放在共享池 `GEO.pool` 里。

```bash
python3 tools/thumbs.py ../songyuan-map/docs/index.html --id sy --year 1141 --mode pol --out thumbs
```

运行后输出两份文件：

- `thumbs/thumb-sy.svg`：贴进对应卷的 `.thumb-in`。
- `thumbs/thumb-sy.css.txt`：两行颜色 token。浅色那行贴进 `:root`，深色那行贴进两个深色块，和已有的 `/* 缩略图 zg */` 等放在一起。

参数：

- `--id`：两三个字母的代号，用作颜色 token 前缀和 clipPath id，各卷不能重复。
- `--year`：取哪一年的节点。
- `--node`：按序号取节点，从 0 数起。同一年有几个节点时用，比如隋唐图按月分节点。
- `--year` 和 `--node` 都不填时，取该图打开时的节点（`GEO.first` 记年份，`DATA.first` 记序号）；都没有就取第一个。
- `--box 西 东 南 北`：取景的经纬框。不填时用该图源码里 FITS 的 cn 或 all。
- `--mode zhen|pol`：分层模型的着色方式。`zhen` 是藩镇、诸侯或路，为缺省值；`pol` 是政权。
- `--blank`：只画海陆、河流、经纬网，用于编修中的卷。

现有五幅的参数：

```bash
python3 tools/thumbs.py <战国 index.html>       --id zg --year -300 --box 102.6 124.2 25.6 42.4
python3 tools/thumbs.py <汉末三国 index.html>   --id hs --year 229 --mode zhen --box 97.5 125.5 19 43
python3 tools/thumbs.py <隋及唐初 index.html>   --id st --mode pol                 # 打开时的节点：619
python3 tools/thumbs.py <唐宋 index.html>       --id ts --year 820 --mode zhen --box 95 127.5 19 46.5
python3 tools/thumbs.py <宋辽夏金元 index.html> --id sy --year 1141 --mode pol
```
