# 历代舆图

历代形势图的总览页：题签页眉、时间长卷、图卷目录、凡例。目录里每一卷链到它自己的 GitHub Pages：

| 卷次 | 图 | 地址 | 状态 |
| --- | --- | --- | --- |
| 卷一 | 战国列国形势图（前475 — 前221） | https://jackyijun.github.io/zhanguo-map/ | 已成 |
| 卷二 | 隋末唐初形势图（611 — 628，拟） | https://jackyijun.github.io/suitang-map/ | 编修中，不可点 |
| 卷三 | 唐宋之际形势图（755 — 979） | https://jackyijun.github.io/tangsong-map/ | 已成 |

`index.html` 自包含：样式、脚本、三幅缩略图都在文件里，不加载任何外部资源。色板、字体、细线与两张图的《历史形势图统一规范》一致，深浅色跟随系统。

## 部署

1. 在 GitHub 新建仓库 `jack-history-maps`。名字可以换，页面里的链接都是绝对地址，不受仓库名影响。
2. 把本文件夹的内容放进仓库根目录并推送。
3. 仓库 Settings → Pages → Build and deployment：Source 选 Deploy from a branch，分支 `main`，目录 `/ (root)`。
4. 稍等一两分钟，打开 https://jackyijun.github.io/jack-history-maps/

## 隋末唐初上线

在 `index.html` 里搜「卷二 · 隋末唐初」，改这几处：

1. `<li class="juan todo" id="juan-suitang" … data-todo="1">`
   - 去掉 `todo` 和 `data-todo="1"`
   - 加上 `style="--c:var(--m-st)"`
   - 把 `data-start` / `data-end` 改成定稿的起止年
2. `<article class="juan-body" aria-label="…">` 换成 `<a class="juan-body" href="https://jackyijun.github.io/suitang-map/">`，结尾的 `</article>` 换成 `</a>`。
3. 缩略图：
   - 用下文的工具重新生成，替换 `.thumb-in` 里的第一个 `<svg>`
   - 删掉第二个 `<svg class="stamp">`（「编修中」印）
   - 仿照另外两卷加一行 `<span class="thumb-cap">…</span>`
4. 文字：
   - 起止年去掉「（拟）」
   - 改导语
   - `stats` 换成「N 节点 · N 条目 · …」
   - `<span class="act">即将刊行</span>` 换成 `<span class="act">展卷 <span>→</span></span>`
5. 在 `:root` 和两个深色块里各加一个 `--m-st`（浅色、深色两值），用这一卷主政权的疆域色。
6. 目录组头的「已成二卷 · 编修一卷」改成「已成三卷」。

时间长卷不用改，它直接读目录里每卷的 `data-start` / `data-end` 画色段。

## 生成缩略图

`tools/thumbs.py` 从某张图自己的 `index.html` 里读出内嵌的 GEO / DATA，按那张图的投影和色板，把一个时间节点重绘成 360×270 的小图。战国式简单模型和唐宋式分层模型都能处理。只用 Python 3 标准库。

```bash
python3 tools/thumbs.py ../suitang-map/index.html --id st --year 618 --box 99 125 21.5 43.5 --out thumbs
```

它会输出两份文件：

- `thumbs/thumb-st.svg`：贴进对应卷的 `.thumb-in`。
- `thumbs/thumb-st.css.txt`：两行颜色 token。浅色那行贴进 `:root`，深色那行贴进两个深色块，与已有的 `/* 缩略图 zg */`、`/* 缩略图 ts */` 放在一起。

参数说明：

- `--id`：两三个字母的代号，用作颜色 token 前缀和 clipPath id，各卷不能重复。
- `--year`：取哪个节点；不填则取第一个。
- `--box 西 东 南 北`：取景的经纬框；不填则用该图源码里 FITS 的 cn 或 all。
- `--mode zhen|pol`：分层模型的着色，藩镇（缺省）或政权。
- `--blank`：只画海陆、河流、经纬网，用于编修中的卷。

现有三幅的参数如下：

```bash
python3 tools/thumbs.py ../zhanguo-map/index.html  --id zg --year -300 --box 102.6 124.2 25.6 42.4
python3 tools/thumbs.py ../tangsong-map/index.html --id ts --year 820 --mode zhen --box 95 127.5 19 46.5
python3 tools/thumbs.py ../tangsong-map/index.html --id st --blank --box 99 125 21.5 43.5   # 卷二占位，借唐宋图的底图
```

## 增加新卷

1. 复制一个 `<li class="juan">` 块，按时代先后放进目录，重排卷次（卷一、卷二……）。
2. 改 `id`、`data-short`（时间长卷上显示的短名）、`data-start`、`data-end`。
3. 改链接、缩略图和文字。
4. 封面上的「凡三卷 · 前475 — 979」与目录组头的计数一起改。
5. 如果新卷超出前500 — 1050，改页尾脚本里的 `R0`、`R1`、`TICKS`；朝代分段在同处的 `BANDS`。
