# 历代舆图

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

历代形势图的总览页，依次是题签页眉、时间长卷、图卷目录、凡例。目录里每一卷链到本仓库发布的新页面；各卷原来的网址保留为旧版（卷目右上角「旧版 ↗」），不再更新：

| 卷次 | 图 | 地址 | 旧版 |
| --- | --- | --- | --- |
| 卷一 | 春秋列国形势图（前770 — 前476） | https://jackyijun.github.io/lidai-yutu/chunqiu/ | https://jackyijun.github.io/chunqiu-map/ |
| 卷二 | 战国列国形势图（前475 — 前212） | https://jackyijun.github.io/lidai-yutu/zhanguo/ | https://jackyijun.github.io/zhanguo-map/ |
| 卷三 | 秦汉形势图（前212 — 184） | https://jackyijun.github.io/lidai-yutu/qinhan/ | （单仓新编，无旧版） |
| 卷四 | 汉末三国形势图（184 — 280） | https://jackyijun.github.io/lidai-yutu/hanmosanguo/ | https://jackyijun.github.io/hanmosanguo-map/ |
| 卷五 | 两晋十六国南北朝形势图（280 — 581） | https://jackyijun.github.io/lidai-yutu/liangjin-nanbeichao/ | https://jackyijun.github.io/liangjin-nanbeichao-map/ |
| 卷六 | 隋及唐初形势图（581 — 669） | https://jackyijun.github.io/lidai-yutu/suitang/ | https://jackyijun.github.io/suitang-map/ |
| 卷七 | 唐末五代形势图（755 — 979；地图本身题「唐宋之际形势图」） | https://jackyijun.github.io/lidai-yutu/tangsong/ | https://jackyijun.github.io/tangsong-map/ |
| 卷八 | 宋辽夏金元形势图（979 — 1279） | https://jackyijun.github.io/lidai-yutu/songyuan/ | https://jackyijun.github.io/songyuan-map/ |
| 卷九 | 民国至新中国初期形势图（1911 — 1954） | https://jackyijun.github.io/lidai-yutu/minguo-xinzhongguo/ | https://jackyijun.github.io/minguo-xinzhongguo-map/ |

卷一至卷六首尾相接，相邻两卷衔接节点的疆域、配色完全一致：春秋图末节点（前476）与战国图首节点（前475）；战国图末节点与秦汉图首节点（前212）；秦汉图末节点与汉末三国图首节点（184）；汉末三国图末节点与两晋图首节点（280）；两晋图末节点与隋唐图首节点（581）。秦汉、两晋两图都照搬了两头的衔接节点。

首页源文件 `hub/index.html` 是自包含的（构建时原样复制到 `docs/index.html` 发布）：样式、脚本、九幅缩略图都写在文件里，不加载任何外部资源。色板、字体、细线与各图的《历史形势图统一规范》一致，深浅色跟随系统。

线上地址：https://jackyijun.github.io/lidai-yutu/

## 单仓（2026-11 起迁移中）

本仓库正在改造成整部图集的单仓：原有八卷的代码、史料和底图都已搬进来，新增的秦汉卷直接在单仓里编，以后的统一数据格式、全局地点表、统一投影与地形、统一疆域引擎和首页的时间轴模式，都在这里做。步骤与进度见《历史形势图统一规范》第十九节。各卷原来的仓库和网址保留为旧版，不再修改。

```
lidai-yutu/
├── run.py                 构建入口
├── requirements.txt       八卷共用的依赖
├── requirements-lock.txt  能逐字节重现线上版本的依赖版本
├── hub/index.html         首页源文件
├── eras/<短名>/           各卷：content/ 史料、src/ 构建代码、tools/、run.py，照旧可以单独构建；
│                          era.toml 卷的基本信息；legacy.html 旧构建的成品（数据来源）；short.tsv 时间轴短标题
├── core/v1/               统一数据格式 v1：格式说明 FORMAT.md、旧格式转换、全局表生成、第 3 步的改正
├── core/web/              统一前端：由 v1 生成各卷新页面（统一模板、时间轴、深链接），说明见 core/web/README.md
├── core/geo/              统一投影、全球底图、地形晕渲：参数集中在 config.toml，说明见 core/geo/README.md
├── core/engine/           统一疆域引擎（九卷的疆域都由它出）：参数集中在 config.toml，说明见 core/engine/README.md
├── global/                全局表：地点、政权、山川、译名；palette.toml 全局配色；decisions.toml 人工决定；review/ 审定清单
├── geodata/               底图只存一份（ne/、etopo20/、prov/、derived/）；各卷 geodata/ 里是指向这里的符号链接；
│                          relief/<短名>/ 各卷的地形晕渲图、world/<短名>.json 各卷范围以外的全球陆地（由 core/geo 生成，入库）
├── tools/thumbs.py        首页缩略图
├── tools/colorcheck.py    配色普查：各卷相邻政权的色差
└── docs/                  GitHub Pages 发布目录：index.html 是首页，<短名>/index.html 是各卷
```

各卷短名是旧仓库名去掉 `-map`：chunqiu、zhanguo、hanmosanguo、liangjin-nanbeichao、suitang、tangsong、songyuan、minguo-xinzhongguo；秦汉卷没有旧仓库，短名 qinhan。构建分三段：各卷仍用自己原来的构建脚本推算疆域，成品存为 `eras/<短名>/legacy.html`；由它重建全局表、转成 v1 数据并套用第 3 步的改正；再由 v1 生成新页面 `docs/<短名>/index.html`，同时并入 `geodata/relief/`、`geodata/world/` 里预先生成的地形晕渲与全球底图。已换到统一疆域引擎的卷（`era.toml` 的 `[engine]` 写 `geometry = "engine"`，秦汉以外的八卷都已写上），疆域改由引擎按 v1 的归属推算，结果存为 `eras/<短名>/engine.json`（入库），生成 v1 时换掉 legacy.html 里旧引擎画的几何；`python run.py` 构建这几卷时会自动重算。

```bash
pip install -r requirements.txt
python run.py                    # 九卷全部构建：疆域 → v1 数据 → 新页面，再更新首页
python run.py zhanguo songyuan   # 只构建这几卷
python run.py --html             # 各卷跳过疆域计算，只重新拼装（须先完整构建过一次）
python run.py --web              # 不重算疆域，只由 legacy.html 重建全局表、v1 数据和新页面（改短标题、译名与内容改正后用这个；改了归属点坐标或归属要按卷重算）
python run.py --v1               # 只重建全局表与各卷 v1 数据包（build/v1/，不入库）
python run.py --geo              # 重新生成地形晕渲与全球底图，再出新页面（改了 core/geo/config.toml 里投影、分档、底图参数后用；第一次会下载晕渲原图约 42 MB）
python run.py --engine           # 统一疆域引擎陪跑：由 v1 数据重算秦汉以外八卷的疆域，逐节点与旧引擎画的疆域比对（build/engine/，不改页面）
python run.py --hub              # 只更新首页
python run.py --check            # 核对 legacy.html、docs/ 是否是本地最新构建的结果
python run.py --list             # 列出各卷短名
```

GitHub Pages 的发布来源设为 `main` 分支的 `/docs`。

九卷配色统一由 [`global/palette.toml`](global/palette.toml) 按政权的全局 ID 定，同一政权在各卷同色。主朝取五德之色（轻量版，低饱和）：秦水德尚黑，两汉、隋、宋火德尚赤（蜀汉承汉，浅一档），新、曹魏、唐土德尚黄，晋金德尚白；其余政权按九卷各节点里的邻接避让，相邻的两块不撞色。民国卷保持原色，只改了与英属地分不开的荷兰、西藏地方政府、阿富汗。改了配色用 `python3 tools/colorcheck.py` 复查（要先跑 `python run.py --web` 或 `--v1`），再重出首页缩略图。

七卷的大漠（大碛、戈壁）原先取 Natural Earth 地理区里「GOBI DESERT」的注记范围，把阴山以北的漠南、河西走廊和胪朐河都盖了进去。现在改由 [`tools/damo.py`](tools/damo.py) 从 RESOLVE 生态区（2017）的三个戈壁生态区改绘（数据在 [`geodata/resolve/`](geodata/resolve/README.md)，CC-BY 4.0）：扣去漠南草原（中段压在《新唐书·地理志》所记的入碛处，约北纬 43°）、河西走廊与居延绿洲、杭爱山南麓以北，秦汉卷另扣乌兰布和沙漠北部的汉代垦区；生成 v1 时换进各卷（`core/v1/overlay.py`）。戈壁本体两千年里在这张图的尺度上看不出变化；随时代变化的是沙地与绿洲，毛乌素沙地已按卷处理，其余以后逐代补。

架构整理第一批（2026-11-20）：秦汉至民国七卷的页面模板合成 [`core/web/template.html`](core/web/template.html) 一份（原来七份，相互差两三百到五百多行），图层有数据就画，各卷不同的文字与少数开关（时间单位、斜线画法等）写进各卷 `era.toml` 的 `[web]`，`core/web/patch.py` 只剩春秋、战国两卷用。合并时写了脚本逐卷比对新旧页面：逐个节点、两种着色、各视野、缩放、点索引各组、图例开关、地图悬停与点击、检索、键盘、年表、对照表、英文、深链接、深色、窄屏，每步之后比 DOM，另在几种状态下逐像素比截图；差别只在有意统一的几处：本期只一年时写一个年份；节点说明里本期路线的「行军」只写一次；行军路线的画法、路线名的位置各卷一致，点选路线时收进整条路线、不在本期时跳到路线结束的节点，索引里的路线条目选中后列出全程各站；运河的开凿年份在索引里也写；民国卷公路的线型同汉末古道；年表里的都城迁移都写成「某都某地」。同时改正了几处旧毛病：选中州府时的缩放偶尔不对（误拿州府序号查条目类别）；秦汉卷对照表里诸族的年代误显示为月序号，深链接里不写月份的年份会错到上一年；倍速按钮的英文提示。秦汉卷的长城、驰道照旧画在运河之下（`[web]` 的 `lines_under_canal`）。

第 7 步之后补上了原定在第 5—7 步做的改正（2026-11-19）。改正清单 [`global/corrections.md`](global/corrections.md) 里的坐标，现在都在生成 v1 时套用，连同疆域引擎用的归属点（州府、郡国治所等），疆域按改后的点重算，九卷陆地归属变化 0.01%—0.23%。春秋、战国的归属点不在 v1 里，直接改在两卷共用的 `content/seeds.txt`。一个点只有一个坐标：同一条有几段年代对不上城址的（治所迁城、改名），取最长的一段；最长的一段不到本条年代一半的不改（10 处，如两晋卷 581 年按隋制改名的几处）；挪过去会与别的点重合的，在 `global/decisions.toml` 的 `[places.keep]` 写明不改（两晋卷的乐成与乐寿同在献县，留在河间）。武陵山（秦汉至民国七卷原画成西北—东南走向）、伏牛山（春秋、战国原画成西南—东北走向）在页面上改画成 `global/decisions.toml` 选定的那一条（`page = true`）；引擎本来就用这一条，疆域不受影响。唐宋卷的真腊在 802 年以后只改名、不扩疆域：本卷图幅南到北纬 15.5°，吴哥与湄公河三角洲都在图外。两晋卷原把瀛州、沧州、贝州、德州、棣州在 307—349 年一直画给晋，在后赵境内成了几块飞地；现在河间（瀛州）、清河（贝州）、渤海（沧州）314 年随冀州归石勒；平原（德州）、乐陵厌次（棣州）是邵续、段匹磾据守的晋地，平原 320 年石虎擒邵续后归后赵，厌次 321 年失守后归后赵。疆域重算后，秦汉卷有 6 个郡国的选色漂移，在 `global/palette.toml` 钉回原色。改了 `decisions.toml` 的城址或各卷的归属，要用 `python run.py <短名>` 重算疆域：`--web` 发现引擎输入的指纹对不上，会停下。

迁移第 7 步把旧卷逐个换到统一疆域引擎，先换了隋唐、两晋两卷（2026-11-17）：两卷的归属、文字、条目都不变，疆域由引擎按各节点的归属重算，陆地归属变化隋唐约 5.6%、两晋约 6.9%，多在归属点稀疏的塔里木、青藏边缘、东北与南海诸国；每个归属点都落在本方疆域里，界线上没有长直线段。581 年衔接节点在隋唐卷的手绘外缘以内照搬隋唐的引擎几何，两卷一致；280 年衔接节点暂时保留照搬汉末卷的旧几何，等汉末卷换过来。第二批宋元、民国两卷（2026-11-18）陆地归属变化约 9.8%、2.5%：中亚、青藏边缘、阿拉伯半岛一带变化较多，民国卷有国界墙压着，变化最小；旧版两卷合计约 1500 个节点次的城邑点画在别家疆域里，新版没有。这两卷视野大、节点多，界线的简化容差放宽到 0.25 格（约 1.8 km，`era.toml` 的 `[engine]` 写 `simplify`），页面体积与旧版相当（照引擎默认值，民国卷要 21 MB）。979 年衔接节点以宋元卷为准。第三批唐宋卷（2026-11-18）陆地归属变化约 10.8%：塔里木盆地南缘只留绿洲，泥婆罗退回到喜马拉雅南麓，京畿南界推到秦岭；旧引擎画的是折线，每个节点有一千五百多段长于 20 km 的直线，新版每个节点只剩二十来段。979 年衔接节点在唐宋卷的推算范围内照搬宋元卷的引擎几何，两卷一致（宋元卷 979 年的女真改为不属辽，唐宋卷的室韦、阻卜改作辽的属部）。唐宋卷用引擎默认的简化容差，界线随地形走，折点约为旧版的七倍，页面由 2.7 MB 增到 5.9 MB（压缩传输约 1.9 MB）。第四批汉末卷（2026-11-19）陆地归属变化约 12.7%，多在夫余、高句丽、林邑、鲜卑、诸羌的外缘与中原诸侯之间；州界改由引擎按「诸侯 × 州」分块描出，与诸侯界线共用一条边；外缘的远近由旧版各点的分区半径折算。同批修了引擎的一处毛病：远洋小岛和推算范围边上的碎块原来会被平滑成有主，归给隔海的政权（如宋元卷的马里亚纳归日本），现在只认离有主地约 85 km 以内的，唐宋、宋元、秦汉三卷随之重算，民国卷的殖民地群岛照旧。184、280 两处衔接随之照搬汉末卷的新疆域。第五批春秋、战国两卷（2026-11-19）换完，八卷的疆域都由引擎出：推算范围同旧构建，范围内的陆地都分给最近的点（陆路够不着的远岛除外），外缘由不属任何一方的点撑出来，与旧版一样；陆地归属变化约 12.1%、7.1%，多在巴、蜀、义渠、西戎这些山地国家的边缘与中原小国之间，疆域不再画到海上（旧版战国末节点的秦盖住了台湾、琉球）。周天下外缘与秦郡界也由引擎出；两卷共用的归属点在西北补了武威、张掖、阿拉善、居延四个无主点，前212 年秦的西北界因此在贺兰山—黄河一线，不再铺满河西走廊与阿拉善。两卷前476 / 前475 的衔接节点 28 国逐字节相同，秦汉卷前212 照搬战国卷的新疆域。界线简化容差同宋元、民国放宽到 0.25 格，两页 1.8 → 2.3 MB、1.5 → 2.0 MB。同批给引擎的「护点」加了一查：坐标按 0.01° 存，取整后压在界线上的归属点（多在界河岸边，如战国卷的内黄、汉末卷的白马）也补圆圈回本方，汉末卷 195—200 年白马一带因此差一块约 30 km² 的小圆，其余已换的卷逐字节不变。

迁移第 6 步在单仓里新编了[秦汉卷](eras/qinhan/README.md)（前212 — 184，五十七个节点），补上战国与汉末三国之间的空档；汉末三国卷随之删去 94 年的序幕节点，从 184 年黄巾起事开始，卷次顺延。秦汉卷是第一部直接用统一疆域引擎出疆域的卷：`eras/qinhan/src/` 由史料生成归属与条目，引擎（`core/engine/`）推算郡国疆域，衔接节点照搬战国末、汉末首；构建要走两遍，`python run.py` 会自动做。加卷时各卷的全局 ID 不变，自动取名会变的在 `global/decisions.toml` 里钉住。

迁移第 5 步写成了统一疆域引擎 [`core/engine/`](core/engine/README.md)：一张铺在统一投影上的全球格网（约 7 km 一格），格子的位置、地形、山脉、随机扰动只由经纬度决定，同一个地方在哪一卷代价都一样，相邻两卷将来可以共用归属点；外缘可以手绘（隋唐、两晋），也可以按可达代价定（宋元、民国），民国卷的国界墙也并了进来。第 5 步时只陪跑：拿两晋、隋唐、宋元、民国四卷的归属数据重算，与现有页面逐节点比对，页面不变；第 7 步起各卷逐个换过去。

迁移第 4 步统一了投影、加上了全球底图和地形晕渲：八卷改用同一个 Albers 投影（中央经线 105°E、原点纬线 35°N），接缝挪到大西洋 30°W；缩到最小能看到全世界（南极洲除外），各卷范围以外补上 Natural Earth 1:50m 的陆地与大湖；地形晕渲取自 Natural Earth 1:10m Shaded Relief，分辨率按地区分三档（中国本部及周边 2 km、亚欧大陆 5 km、全球 10 km），同一个地方在哪一卷都一样清楚，图例里可以关掉。每页因此增加 0.6—1.2 MB。浓淡、分档等参数都在 [`core/geo/config.toml`](core/geo/config.toml)，说明见 [`core/geo/README.md`](core/geo/README.md)。

迁移第 3 步上线了统一前端：八卷新页面共用一套时间轴（上为按真实年代比例的细条，下为等宽刻度：年份 / 短标题 / 年号）和深链接（地址栏 `#y=1127&sel=polity:金&lang=en` 这样记下当前节点、选中对象、视野、着色、缩放与语言，可直接分享），播放都可切 1× / 2×，界面语言各卷与首页共用；地图本身与旧版逐项相同，只先改了不牵动疆域的点位、英文译名和几处名称（见 `global/corrections.md`）。说明见 [`core/web/README.md`](core/web/README.md)。

迁移第 2 步定下了八卷共用的数据格式 v1，并把八卷的地点、政权、山川、译名归并成全局表，每个对象有一个跨卷的全局 ID。现在 v1 由各卷成品转出（转回旧格式逐字节相同），页面不受影响；自动归并判断不了的列在 `global/review/` 里，审定后写进 `global/decisions.toml`。格式、ID 规则和审定流程见 [`core/v1/FORMAT.md`](core/v1/FORMAT.md)。

疆域计算对 numpy、scipy、scikit-image、shapely 的版本敏感：版本不同，算出的界线会有约 0.01° 的末位差，春秋、战国两卷还会因代价栅格指纹不符而停下。要逐字节重现线上版本，用 `requirements-lock.txt` 里的版本（Python 3.13）。

## 中英双语

页面右上角「中 | EN」切换，默认中文。中文名「历代舆图」，英文名 Historical Atlas of China。

- 选择记在本机（localStorage 键 `lidai-yutu:lang`）；网址加 `#en` 直接打开英文，加 `#zh` 打开中文；`<html lang>` 随之切换。
- 从目录点进各卷时，链接带上当前语言（`#zh` / `#en`），各图按同样的语言打开；各卷新页面也读写同一个 `lidai-yutu:lang`。
- 页面文字成对写在同一处：`<span class="zh">…</span><span class="en" lang="en">…</span>`，按 `<html lang>` 只显示一种。时间长卷由页尾脚本生成，朝代与时代分段 `BANDS` 里每项也写了中英两个名字。
- 英文模式下标题与卷名换西文衬线体（Iowan Old Style、Palatino 一类），正文换系统无衬线体，取消中文的大字距，组头改为大写。竖排题签「历代舆图」和两方印保留不变，英文标题排在题签右侧。
- 卷名、主线、着色方式与统计用语都照各图自己的英文版：节点叫 snapshots，州府、州郡叫 prefectures，郡国、郡县叫 commanderies，藩镇写 fanzhen，方镇叫 regional commands，民国卷的城市叫 cities、派系与属地叫 factions and dependencies。卷七（唐末五代）英文题名用 Late Tang and the Five Dynasties，与中文首页的「唐末五代」一致；地图本身的英文题名是 Between Tang and Song。
- 缩略图里画了中、英两组注记（`<g class="t-lab zh">`、`<g class="t-lab en">`），也按当前语言只显示一组。英文国名取自各图数据，见下文「生成缩略图」。

## 增加新卷

以下改的都是 `hub/index.html`；改完运行 `python run.py --hub`，更新发布用的 `docs/index.html`。

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
- 注记标在该图自己的注记点上。统一引擎按整块疆域找注记点（离边界最远处），大政权的注记点常落在取景框外，缩略图上就不标了；用 `--inframe` 指定的单位，注记点在框外时改标在框内那部分疆域里离边界、框边都最远处（唐宋卷的吐蕃、宋元卷的吐蕃诸部）。没有默认打开：全开会在框边多出许多挤着的小注记。
- 图还没有英文时，用 `--en "编号=英文名;…"` 补缩略图的英文注记（编号即单位编号），它也优先于图里的英文名。

```bash
python3 tools/thumbs.py docs/songyuan/index.html --id sy --year 1120 --mode pol --out thumbs
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
- `--fs "编号=字号;…"`：指定中文注记字号（英文随之按 0.82 倍）；写 0 就不标，用于被说明框盖住的注记。春秋、战国两图按国名写，如 `--fs "淮夷=8"`：疆域略小、按规则字号不到 8 就不标的，可以这样保住。
- `--inframe "编号;…"`：注记点在取景框外时改标在框内的单位，见上；春秋、战国两图写国名。

现有九幅的参数：

```bash
python3 tools/thumbs.py <春秋 index.html>       --id cq --year -632 --box 105.5 122.5 28.6 41.0 --fs "淮夷=8;舒=8"
python3 tools/thumbs.py <战国 index.html>       --id zg --year -300 --box 102.6 124.2 25.6 42.4
python3 tools/thumbs.py <秦汉 index.html>       --id qh --mode pol --box 78 132 16 50   # 打开时的节点：前108
python3 tools/thumbs.py <汉末三国 index.html>   --id hs --year 229 --mode zhen --box 97.5 125.5 19 43
python3 tools/thumbs.py <两晋 index.html>       --id lj --mode pol                 # 打开时的节点：401
python3 tools/thumbs.py <隋及唐初 index.html>   --id st --mode pol                 # 打开时的节点：619
python3 tools/thumbs.py <唐宋 index.html>       --id ts --year 820 --mode zhen --box 95 127.5 19 46.5 --inframe 2 --fs "19=10"   # 吐蕃、新罗
python3 tools/thumbs.py <宋辽夏金元 index.html> --id sy --year 1120 --mode pol --inframe 86   # 吐蕃诸部
python3 tools/thumbs.py <民国 index.html>       --id mg --month 1937.07 --box 78 146 17 55 --zh "80=陕甘苏区" --fs "80=9.5;98=0" \
    --en "80=Shaanxi-Gansu Soviet Area"         # 1937.07 七七事变，派系着色（地图打开时是 1937.12）
```
