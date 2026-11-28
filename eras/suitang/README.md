# 隋至盛唐形势图

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

581—755 年，从隋文帝代周到唐玄宗天宝十四载安史之乱前夕，42 个时间节点：隋末群雄与唐初统一按月细分，670 年起的 16 个节点写吐蕃、后突厥、突骑施、大食、渤海、南诏的兴衰与天宝十节度。含行军与行程路线（秦王征战、玄奘西行、王玄策出使、高仙芝远征等 16 条）、古今地名对照、年表与对照表。755 年节点与《唐宋之际形势图》首节点共用，疆域相同。中英双语，单文件网页，无外部依赖。

## 一、直接看

单仓根目录构建后打开 **`docs/suitang/index.html`**：页面由单仓 `core/web/` 统一生成，数据、样式、脚本全部内嵌，不联网、不需要服务器。本目录自 2026-11 架构整理第三批起不再出页面。

- 语言：地图右上角「中 | EN」切换（年表、对照表视图里在内容区右上角），选择会记在浏览器里；网址末尾加 `#en` 直接打开英文版。英文界面里地图只标英文，悬停说明、索引、年表、对照表在英文名后附注汉字原名；检索中英文都可以，英文不必打变音符号。

## 二、线上地址

https://jackyijun.github.io/lidai-yutu/suitang/

旧版（原仓库 `Jackyijun/suitang-map` 用本卷旧构建出的页面，保持原样）：https://jackyijun.github.io/suitang-map/

## 三、本地构建

在单仓根目录构建（Python 版本与依赖见单仓 README）：

```bash
python run.py suitang  # 本卷第 1 段 → 统一引擎重算疆域（engine.json）→ v1 数据 → docs/suitang/index.html
python run.py --web    # 不重算，只由各卷的 source.json、engine.json 重建 v1 数据与新页面
```

本目录的 `run.py` 是第 1 段：由 `content/` 的史料与 `geodata/` 的底图写出 **`source.json`**（节点归属、文字、条目与底图，不含疆域与配色，入库），单仓由它转成 v1 数据。疆域由统一疆域引擎（单仓 `core/engine/`）按各节点的归属推算，结果存在本目录的 `engine.json`（入库）；颜色由单仓 `global/palette.toml` 定；页面由单仓 `core/web/` 生成。本卷原来的疆域推算、配色与页面模板 2026-11 架构整理第三批起退役。

| 命令（本目录） | 作用 |
|---|---|
| `python run.py` | 检查底图 → 底图（`build/geo_base.json`）→ 各节点归属与条目 → 汇编 `source.json` |
| `python run.py --html` | 已有底图就不重做，只重新汇编（只改了 `content/` 的文字或英文译文时用） |
| `python run.py --draft` | 英文有缺译或过期时也照常汇编（缺译处显示中文）；默认严格，会停下 |

改了 `content/` 以后，从单仓根目录 `python run.py suitang` 重建这一卷（第 1 段、疆域、页面一次做完）。只在本目录跑 `run.py` 不会更新 `engine.json` 和页面；归属变了而疆域没重算时，单仓 `python run.py --web` 发现引擎输入的指纹对不上，会停下。

同一份输入，`source.json` 逐字节一致，可以用 git 追踪改动。

## 四、目录结构

```
eras/suitang/
├── run.py              第 1 段构建入口：→ source.json
├── era.toml            卷的基本信息（卷次、首屏、统一引擎的设置、衔接、页面文字）
├── source.json         ★ 第 1 段的产物（入库）：节点归属、文字、条目与底图，单仓的 v1 数据由它转出
├── engine.json         统一疆域引擎算出的各节点疆域（入库；单仓 python run.py suitang 时重算）
├── short.tsv           时间轴短标题
├── README.md           说明（中文）
├── README.en.md        说明（英文）
├── content/            史料（手写）
│   ├── seeds.py        577 个归属点：州郡城邑（显示）与仅参与分区的辅助点，含今地与名称沿革（670 年起补入的点由 seeds_late.py 读入）
│   ├── seeds_late.py   670 年起的归属点：唐宋卷补入的点（IMPORT）、退出分区的点（RETIRE）、669—758 年的名称沿革（NM_LATE，每行注明依据）、670 年起显示的区域点（SHOW）
│   ├── units.py        政权、都护府、羁縻府州、部族：名称、按语
│   ├── snaps.py        42 个时间节点：标题、概述、各单位所领州郡、治所、别名
│   ├── snaps_tables.py 755 年节点各点的归属（TS755，照唐宋卷 755 年节点）；670 年补入的点接续 669 年的归属（INHERIT670）
│   ├── items.py        都城、战役、关隘、事件、山川按语、诸族、行军·行程路线（16 条）
│   ├── falls.tsv       灭国表：年份、亡国（地图上的国名）、经过与英文，九卷同一写法（见 core/web/README.md「灭国表」）
│   ├── frontier.py     全图外缘（北疆按主流唐极盛图手绘；统一引擎按它定推算范围）
│   └── en/             英文版：与上面各文件对应的译文（JSON）、zh.lock.json 中文指纹、GLOSSARY.md 译名体例
├── src/
│   ├── config.py       路径与底图范围
│   ├── fetch_data.py   校验 geodata/，缺失时从 GitHub 下载固定版本
│   ├── build.py        底图与汇编，输出 build/*.json
│   ├── basemap.py      底图：陆地、湖泊、河流、运河、荒漠、今国界、今省界
│   ├── compile_data.py 各节点归属、底图、条目 → GEO / DATA
│   ├── i18n.py         英文版：列出需要翻译的条目、检查缺译与过期、把译文并入数据
│   └── assemble.py     并入英文、检查缺译，汇编成 source.json
├── geodata/            底图，随仓库附带，离线可构建
├── tools/
│   └── i18n.py         英文版维护：status / todo / lock / table
└── build/              中间产物
```

## 五、工作原理

> 单仓新页面（`docs/suitang/`）的疆域，第 7 步（2026-11-17）起改由统一疆域引擎推算（`core/engine/`，结果在本目录的 `engine.json`，根目录 `python run.py suitang` 时自动重算）；归属、文字、条目仍出自本卷。

**第 1 段**：`build.py` 检查底图 → `basemap.py` 出底图 → `compile_data.py` 按 `content/snaps.py` 定各节点的归属、汇编条目 → `assemble.py` 并入英文，写成 `source.json`。

**670 年起的归属点与 755 年衔接**（第 8 步，2026-11-27）：755 年节点与《唐宋之际形势图》首节点共用（规范第十八节「共用归属点」）。在唐宋卷的推算范围（72°—136°E、10°—55°N）以内，670 年起各节点与唐宋卷用同一组点：唐宋卷独有的 111 个点 670 年起补入分区（`seeds_late.py` 的 `IMPORT`，坐标、今地、类型取唐宋卷 `content/seeds.txt`，只存一份），另补渤海旧国（东牟山，698 年起）；本卷独有的 69 个点 669 年后退出分区（`RETIRE`，仍照常显示）。范围以外（咸海、葱岭以西、天竺、贝加尔湖以北）照用本卷的点。

- `era.toml` 的 `[engine]` 写 `pins = "active"`：每个节点只护本节点参与分区的点，669 年以前 26 个节点的疆域与补点以前逐字节相同。
- `[engine]` 写 `align_retired = true`：生成 v1 时（`core/v1/engine_geom.py`），退出分区的点按各节点画出来的疆域对齐归属；只剩这种点、地图上没有疆域的单位从节点里去掉（670 年起的附国·东女诸羌，745 年起的单于、安东、安北，755 年的靺鞨）。原归属与政权表存在 `own_src`、`pol_src`，引擎读原来的，输入与指纹不受对齐影响。
- 755 年节点以唐宋卷为准（`global/junctions.toml`）：唐宋卷推算范围以内照搬唐宋卷的疆域，各点归属照唐宋卷 755 年节点（`snaps_tables.py` 的 `TS755`）。唐宋卷 755 年节点改了，这里要跟着改；构建时 `core/v1` 会核对两卷衔接节点。
- 本卷原是区域点、唐宋卷是州府城邑的 33 处（明州、温州、泉州、容州，新罗的完山州、尚州、溟州等）670 年起（州置得晚的从置州之年起）照唐宋卷显示（`SHOW`）。

> 下面讲的疆域推算、配色与页面模板是本卷旧构建的做法，2026-11 架构整理第三批起已从本目录删去（第 1 段只出 `source.json`），留作说明旧版页面怎么来的。

**旧构建的疆域算法**（原 `src/territory.py`，参数原在 `src/config.py`）：

1. **栅格**：东经 46°—148°、北纬 3°—60°，每格约 6.4 km（0.057°）。海与面积 0.15 平方度以上的湖不可通行。
2. **代价**：平地 1，加 ETOPO20 坡度与高原海拔；山脉脊线烧出高斯形高代价带（主干峰值 +8，次要 +3.5），手绘脊线先加一点横向摆动；江、河、淮、汉与乌浒水、药杀水另加代价；最后乘 ±38% 的多尺度平滑噪声。
3. **分区**：以全部 465 个归属点为源跑一次 16 邻接（含马步）多源 Dijkstra，每格归代价距离最近的点，得到各点的「势力格」。界线因此顺山脊、大河走。
4. **外缘**：全图外缘取 `content/frontier.py` 的手绘线（北起咸海北岸，循哈萨克丘陵北缘、额尔齐斯河、阿尔泰山、叶尼塞河中游，绕贝加尔湖北端，经石勒喀河、黑龙江至入海口）。海面、大湖与近岸小岛就近延伸，页面再按陆地裁剪；台湾、济州、对马等离岸较远又无归属点的岛屿留空。
5. **描界**：每类的指示栅格作高斯平滑（σ 1.2 格），界线描在相邻两类平滑值相等处，沿格边线性插值，三类以上交汇处取交点均值。整张图的界线网络只描一次、两侧共用，再做三轮拉普拉斯平滑，抹掉格点插值留下的小折角。
6. **成面**：界线网络成面，按格心归类，零星碎块并入相邻一方；再加一层平滑位移场（约 1—2 格，两种尺度），让平原上的界线带上河曲一样的小弯；最后用 GEOS `coverage_simplify` 整体简化。相邻势力格共用同一条边，无缝无叠。
7. **按节点合并**：`compile_data.py` 按各节点的归属把势力格并成单位（政权、都护府）与政权的疆域，注记取最大陆块的不可达极点；相邻节点没变的几何只存一份（`GEO.pool`）。

**旧版页面**：原 `template.html` 是唐宋之际形势图的前端，按《历史形势图统一规范》改写，中英切换的做法同《宋辽夏金元形势图》；原 `assemble.py` 先用 `src/i18n.py` 并入英文、检查缺译，再把 `__GEO__`、`__DATA__`、`__UCSS_LIGHT__`、`__UCSS_DARK__` 四个占位符换成数据，输出单文件。

## 六、常见修改

- **改某个节点的归属**：编辑 `content/snaps.py` 里该节点的 `own`（单位 → 州郡列表，`#HB` 之类是地区简写），然后在单仓根目录 `python run.py suitang`（疆域要重算）。
- **加一个州郡或辅助点**：在 `content/seeds.py` 加一行（`名|今地|经度|纬度|类型|地区|名称沿革`，类型 z 州府、c 城邑、r 仅参与分区），再在 `snaps.py` 里分配归属，然后在单仓根目录 `python run.py suitang`（疆域要重算）。新的州郡名、今地要在 `content/en/seeds.json` 补英文。
- **改 670 年以后的名称**：编辑 `content/seeds_late.py` 的 `NM_LATE`（`年份:名称` 逗号相连，构建只取到 755 年），每行注释写依据；唐宋卷 755—757 年三个节点的名称要一致（`eras/tangsong/content/seeds.txt` 的 `N=`）。
- **改按语、战役、事件**：编辑 `content/items.py` 或 `units.py`，在 `content/en/` 对应的 JSON 里同步改英文，`python tools/i18n.py lock` 后本目录 `python run.py --html`，再在单仓根目录 `python run.py --web`。
- **改北疆外缘**：编辑 `content/frontier.py` 的 `NORTH` 折线（经纬度），然后在单仓根目录 `python run.py suitang`（统一引擎按它定推算范围）。
- **改样式或交互**：页面模板在单仓 `core/web/`（各卷共用，各卷不同的文字与开关写在 `era.toml` 的 `[web]`），改后在单仓根目录 `python run.py --web`。
- **改颜色**：在单仓 `global/palette.toml` 里改这个政权（按全局 ID，见 `global/polities.jsonl`）的浅、深两色，再在单仓根目录 `python run.py --web`；同一政权在各卷同色。

## 七、英文版

中文是源文本，英文按同样的键写在 `content/en/` 里：

| 文件 | 内容 | 键 |
|---|---|---|
| `units.json` | 政权、都护府、部族：全称 `n`、地图短名 `s`、说明 `note` | 单位键（如 `唐`） |
| `labels.json` | 节点里的当年别名（`snaps.py` 的 `lab`） | 中文别名 |
| `seeds.json` | 州郡城邑：今地 `mod`、各时期名称 `n` | 点的 ID |
| `items.json` | 条目：`old` `mod` `note` `yt` `sides` `cmd`，路线地名 `p` | `类别:古名`（如 `battle:虎牢之战`）；同名条目加 `@政权` 或 `@今地` |
| `snaps.json` | 时间节点：年号 `era`、标题 `t`、说明 `d` | `年-月`（如 `618-05`） |
| `misc.json` | 今省名 `prov` | 中文名 |

`zh.lock.json` 记着每条英文写成时对应中文的指纹（sha1 前 10 位）。中文改了而英文没改，构建就报“过期”。译名与写法的规矩见 `content/en/GLOSSARY.md`（拼音、郡县镇与都护府的译法、外国地名、农历月份、战役胜负的写法等）。

**改了中文之后**：

1. `python tools/i18n.py status` 看有几条缺译、过期；
2. `python tools/i18n.py todo` 列出这些条目的中文，到对应 JSON 里补写或改写英文；
3. `python tools/i18n.py lock` 记下新的中文指纹；
4. `python run.py --html` 重新汇编 `source.json`（严格模式，缺译会报错），再在单仓根目录 `python run.py --web`。

`python tools/i18n.py table` 导出全部中英对照到 `build/i18n-review.tsv`，便于审校。

## 八、调参

疆域的推算参数不在本卷：统一引擎的通用参数在单仓 `core/engine/config.toml`，本卷的外缘、推算范围、简化容差等写在 `era.toml` 的 `[engine]`；颜色在单仓 `global/palette.toml`。本卷原来的栅格、代价、平滑与配色参数 2026-11 架构整理第三批起随旧构建一并退役。

本卷 `src/config.py` 里只剩路径与底图范围；全图外缘仍是 `content/frontier.py`。

## 九、资料与可靠程度

疆域据《隋书》、两《唐书》、《资治通鉴》《唐会要》及谭其骧《中国历史地图集》第五册大意推定，以州郡为单位、沿山川划界，仅为示意；755 年节点照《唐宋之际形势图》。670 年以后的州郡名称逐点考证（两《唐书·地理志》《元和郡县图志》等），依据写在 `content/seeds_late.py` 每行注释里。羁縻都护、都督府多为名义统属，草原诸部并无确切界线；北疆外缘按主流唐极盛图的通行画法手绘。今地取遗址或所在城市。

英文译名按 `content/en/GLOSSARY.md` 的体例：汉字圈地名用拼音，汉字圈以外用当时当地名称的通行英文写法，日期照写农历月序、不换算公历。

底图：Natural Earth 5.1.2（陆地、湖泊、河流、今国界），河湖运河、今省界与部分山川关隘条目沿用《唐宋之际形势图》。
