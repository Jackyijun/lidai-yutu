# 历代舆图

历代形势图的总览页：题签页眉、时间长卷、图卷目录、凡例。目录里每一卷链到它自己的 GitHub Pages：

| 卷次 | 图 | 地址 | 状态 |
| --- | --- | --- | --- |
| 卷一 | 战国列国形势图（前475 — 前212） | https://jackyijun.github.io/zhanguo-map/ | 已成 |
| 卷二 | 汉末三国形势图（184 — 280） | https://jackyijun.github.io/hanmosanguo-map/ | 已成 |
| 卷三 | 隋及唐初形势图（581 — 669） | https://jackyijun.github.io/suitang-map/ | 编修中，不可点 |
| 卷四 | 唐宋之际形势图（755 — 979） | https://jackyijun.github.io/tangsong-map/ | 已成 |

`index.html` 是自包含的：样式、脚本、四幅缩略图都写在文件里，不加载任何外部资源。色板、字体、细线与各图的《历史形势图统一规范》一致，深浅色跟随系统。

线上地址：https://jackyijun.github.io/lidai-yutu/

## 更新部署

用本文件夹里的 `index.html`、`README.md`、`tools/` 覆盖仓库根目录的同名文件，然后提交并推送。Pages 会在一两分钟内自动更新。

首次部署时的设置：仓库 Settings → Pages，Source 选 Deploy from a branch，分支选 `main`，目录选 `/ (root)`。

## 隋及唐初上线

在 `index.html` 里搜「卷三 · 隋及唐初」，改下面几处：

1. `<li class="juan todo" id="juan-suitang" … data-todo="1">`
   - 去掉 `todo` 和 `data-todo="1"`。
   - 加上 `style="--c:var(--m-st)"`。
   - 如果起止年有变，同步改 `data-start` / `data-end`。
2. 把 `<article class="juan-body" aria-label="…">` 换成 `<a class="juan-body" href="https://jackyijun.github.io/suitang-map/">`，结尾的 `</article>` 换成 `</a>`。
3. 缩略图：
   - 用下文的工具重新生成，替换 `.thumb-in` 里的第一个 `<svg>`。
   - 删掉第二个 `<svg class="stamp">`，也就是「编修中」印。
   - 仿照其他卷，加一行 `<span class="thumb-cap">…</span>`。
4. 文字：
   - 改导语，删掉「本卷正在编修」一句。
   - `stats` 换成「N 节点 · N 条目 · …」。
   - 把 `<span class="act">即将刊行</span>` 换成 `<span class="act">展卷 <span>→</span></span>`。
5. 在 `:root` 和两个深色块里各加一个 `--m-st`，浅色、深色各一个值，取这一卷主政权的疆域色。
6. 目录组头的「已成三卷 · 编修一卷」改成「已成四卷」。

时间长卷不用改，它直接读目录里每卷的 `data-start` / `data-end` 画色段。

## 生成缩略图

`tools/thumbs.py` 从某张图自己的 `index.html` 里读出内嵌的 GEO / DATA，按那张图的投影和色板，把一个时间节点重绘成 360×270 的小图。它只用 Python 3 标准库。三种数据结构都能处理：

- 战国式：节点里有 `s` / `l`。
- 唐宋式：节点里有 `z` / `p` / `pol`。
- 汉末三国式：同唐宋式，但疆域几何放在共享池 `GEO.pool` 里。

```bash
python3 tools/thumbs.py ../suitang-map/docs/index.html --id st --year 618 --out thumbs
```

运行后输出两份文件：

- `thumbs/thumb-st.svg`：贴进对应卷的 `.thumb-in`。
- `thumbs/thumb-st.css.txt`：两行颜色 token。浅色那行贴进 `:root`，深色那行贴进两个深色块，和已有的 `/* 缩略图 zg */` 等放在一起。

参数说明：

- `--id`：两三个字母的代号，用作颜色 token 前缀和 clipPath id，各卷不能重复。
- `--year`：取哪个节点。不填时取该图打开时的节点（`GEO.first`），没有就取第一个。
- `--box 西 东 南 北`：取景的经纬框。不填时用该图源码里 FITS 的 cn 或 all。
- `--mode zhen|pol`：分层模型的着色方式，`zhen` 为藩镇或诸侯（缺省），`pol` 为政权。
- `--blank`：只画海陆、河流、经纬网，用于编修中的卷。

现有四幅的参数：

```bash
python3 tools/thumbs.py <战国 index.html>     --id zg --year -300 --box 102.6 124.2 25.6 42.4
python3 tools/thumbs.py <汉末三国 index.html> --id hs --year 229 --mode zhen --box 97.5 125.5 19 43
python3 tools/thumbs.py <隋及唐初 index.html> --id st --blank --box 99 125 21.5 43.5
python3 tools/thumbs.py <唐宋 index.html>     --id ts --year 820 --mode zhen --box 95 127.5 19 46.5
```

## 增加新卷

1. 复制一个 `<li class="juan">` 块，按时代先后放进目录，然后重排卷次（卷一、卷二……）。
2. 改 `id`、`data-short`（时间长卷上显示的短名）、`data-start`、`data-end`。
3. 改链接、缩略图和文字；在三处色板里各加一个 `--m-xx` 作为这一卷的主色。
4. 改封面上的「凡四卷 · 前475 — 979」和目录组头的计数。
5. 如果新卷超出前500 — 1050 的范围，改页尾脚本里的 `R0`、`R1`、`TICKS`。朝代分段 `BANDS` 也在同一处。
