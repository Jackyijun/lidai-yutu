# 统一数据格式 v1

规范第十九节迁移第 2 步的产物：各卷共用的一套数据格式，以及跨卷的全局表。

**现状（2026-11）**：各卷的史料仍写在各卷自己的源文件里，照旧用各卷的 `run.py` 构建，成品存为 `eras/<短名>/legacy.html`（入库，是数据来源）。v1 数据包由 legacy.html 转出，转回旧格式与原来逐字节相同（往返无损）。第 3 步起，`build.py` 在往返校验之后套用不牵动疆域的改正（`core/v1/overlay.py`），新页面 `docs/<短名>/` 由改正后的 v1 生成（`core/web/`）。之后各卷逐步改成直接写 v1，旧格式随之退役。

## 文件

| 路径 | 内容 | 入库 |
| --- | --- | --- |
| `core/v1/legacy.py` | 旧格式 ⇄ v1 转换（两套旧模型都支持） | 是 |
| `core/v1/roundtrip.py` | 往返校验：成品 → v1 → 旧格式，必须与原来完全相同 | 是 |
| `core/v1/registry.py` | 由各卷归并出全局表，生成审定清单 | 是 |
| `core/v1/build.py` | 生成各卷 v1 数据包，附全局 ID，套用第 3 步的改正 | 是 |
| `core/v1/overlay.py` | 第 3 步先行的改正：条目点位、英文译名、标了 step = 3 的内容、时间轴短标题；全局配色 | 是 |
| `eras/<短名>/legacy.html` | 各卷旧构建脚本的成品，v1 的数据来源 | 是（构建生成） |
| `eras/<短名>/short.tsv` | 时间轴短标题（唐宋系；战国式写在各卷源文件里） | 是（手写） |
| `global/places.jsonl` | 全局地点表 | 是 |
| `global/polities.jsonl` | 全局政权表（含二级单位：藩镇、路、派系等） | 是 |
| `global/physical.jsonl` | 全局山川表（山脉、河流、运河、沙漠、长城、道路） | 是 |
| `global/glossary.jsonl` | 全局译名表 | 是 |
| `global/decisions.toml` | 人工决定：地点定组与城址、治所迁城、政权合并与 ID、山川画法、译名 | 是（手写） |
| `global/palette.toml` | 全局配色：按政权全局 ID 定浅、深两色，五德主色（规范第三节）；`core/v1/overlay.py` 套用 | 是 |
| `global/corrections.toml` | 各卷页面里要改的内容（坐标以外） | 是（手写） |
| `global/corrections.md` | 各卷改正清单：坐标、内容、英文 | 是 |
| `global/junctions.toml` | 相邻两卷的衔接与空档 | 是（手写） |
| `global/review/*.md` | 审定清单 | 是 |
| `global/stats.json` | 各表条数 | 是 |
| `eras/<短名>/era.toml` | 卷的基本信息 | 是（手写） |
| `build/v1/<短名>.json` | 各卷 v1 数据包 | 否 |
| `build/v1/fixes.json` | registry.py 推出的坐标、英文改正，供 build.py 套用 | 否 |

全局表和审定清单都由 `registry.py` 生成，不要手改；要改结果，写进 `decisions.toml` 再重建。

## 命令

```
python core/v1/roundtrip.py         往返校验各卷（也可只写几卷的短名）
python core/v1/registry.py          重建 global/ 下的全局表与审定清单
python core/v1/build.py             生成 build/v1/<短名>.json（先往返校验，再附全局 ID）
python run.py --v1                  以上后两步一起做
python run.py --web                 再加上生成新页面（core/web/assemble.py → docs/<短名>/）
```

`registry.py` 和 `build.py` 读 TOML，需要 Python 3.11 以上；3.10 及以下先 `pip install tomli`。全局表的输出与 Python 的哈希种子无关，同样的输入每次生成的文件逐字节相同，便于看 diff。

## 时间

v1 里所有时间都是**月序号** `t = 年 × 12 + (月 − 1)`。

- 年份沿用各卷写法：公元前记负数，没有公元 0 年（前 1 年之后是 1 年）。前 632 年 1 月是 `-632 × 12 = -7584`。跨公元前后算年数时要减 1。
- 只精确到年的**节点**取该年最后一个月（`年 × 12 + 11`）：节点表示「到这一年为止」的形势。
- 只精确到年的**条目**（战役、事件、人物等）取该年年中（`年 × 12 + 6`）。
- `tp` 记精度：`"y"` 按年，`"m"` 按月。隋唐卷月份不详的事件（旧格式 `m: 0`）记 `tp: "y"`。
- 秦汉卷的旧格式节点 `y` 本身就是月序号（`core/v1/legacy.py` 的 `MONTHLY`），按年、按月由节点的 `tp` 记；月序号按真实先后（夏正年），显示时按通鉴纪年换算（太初改历前104 以前，十至十二月记在下一年）。按年的节点太初以前取九月，以后取十二月，不取「年 × 12 + 11」。
- 年段（如都城存续）`[a, b]` 两端都含，换算成 `[a × 12, b × 12 + 11]`。
- `-999999` 表示「本卷开始以前」（旧格式战国式写 `-9999`，唐宋系写 `0`）。

## 数据包

`build/v1/<短名>.json` 的顶层：

| 字段 | 含义 |
| --- | --- |
| `v` | 格式版本，现为 `1` |
| `era` | 卷短名 |
| `model` | `simple`（战国式：春秋、战国）或 `layered`（唐宋系：其余各卷） |
| `time` | `year` 或 `month`（隋唐、民国、秦汉按月） |
| `first` | 打开页面时停在哪个节点（月序号） |
| `meta` | 取自 `era.toml`：卷次、图名、短名、起止年 |
| `geom` | 几何池，见下 |
| `base` | 底图图层：`land` `prov` `border` `rivers` `lakes` `canals` `deserts` `seas` `regions` `routes`（各卷有多有少）。`routes` 是行军路线（隋唐、民国、秦汉）：每条 `{it: 条目序号, pts: [[经, 纬, 到达月序号, 地名, …]], pe: [英文地名]}`，地名空着的是折点；页面每个节点只画本期走过的一段 |
| `extent` | 视野：`ext`（经纬度范围）`base`（底图范围）`extpoly` `proj`（投影参数） |
| `polities` | 政权与二级单位 |
| `places` | 地点（州府、城邑） |
| `nodes` | 时间节点 |
| `items` | 条目：都城、战役、关隘、山川、事件、人物等 |
| `ext` | 各卷特有的字段，见下 |
| `_legacy` | 只供转回旧格式，新代码不要读 |

### 几何池 `geom`

每一项是一块疆域：若干个环，每个环是经纬度乘 100 后的整数差分序列 `[x0, y0, dx1, dy1, dx2, dy2, …]`，按奇偶规则填充（环套环即挖空）。节点里写的是几何池的序号；相邻节点没变的疆域共用一项。

### 政权 `polities`

| 字段 | 含义 |
| --- | --- |
| `key` | 卷内的键 |
| `gid` | 全局 ID（`global/polities.jsonl`） |
| `n` | 名称 |
| `kind` | `state` 政权、`zhen` 二级单位（藩镇、方镇、路、派系……）、`tribe` 部族 |
| `color` | `[浅色, 深色]`；`global/palette.toml` 列了的政权按它改 |
| `note` `mod` | 说明、族姓等 |
| `en` | 英文：`n` `s` `note` `mod` |
| `item` `x` `waste` | 各模型特有（战国式政权对应的条目序号；唐宋系的标记） |

### 地点 `places`

| 字段 | 含义 |
| --- | --- |
| `key` | 卷内的键（唐宋系是州府 id；战国式是 `i:<条目序号>`） |
| `gid` | 全局 ID（`global/places.jsonl`）。治所迁过城的州府是按年代分段的列表 `[[起始月序号, 全局 ID], …]`，如两晋卷的相州 580 年前是邺、此后是安阳 |
| `n` `mod` | 名称、今地 |
| `lon` `lat` | 经纬度 |
| `kind` | 唐宋系 `z` 州府、`c` 军镇城戍、`r` 只参与归属计算不标名的参考点；战国式 `capital` `city` `town` `pass` |
| `names` | 改名：`[[t, 名], …]` |
| `owners` | 战国式：归属变化 `[[t, 政权键], …]`；唐宋系的归属在节点的 `own` 里 |
| `jn` `jnm` `note` | 郡名、郡名变化、说明 |
| `en` | 英文 |

### 节点 `nodes`

| 字段 | 含义 |
| --- | --- |
| `t` `tp` | 时间、精度 |
| `title` `desc` `short` | 标题、说明、时间轴短标题（战国式写在源文件里，唐宋系由 `eras/<短名>/short.tsv` 并入） |
| `era` `era2` | 年号、并行年号（唐宋系） |
| `en` | 英文：`title` `desc` `short` `era` `era2` `lab` |
| `u` | 单位疆域：`{单位: 几何序号}`。战国式的单位是政权键，唐宋系是 `polities` 的序号（字符串） |
| `ul` | 单位标注位置 |
| `pu` `pul` | 唐宋系：政权层疆域与标注位置 |
| `pol` | 单位所属政权：`{单位: 政权}` |
| `own` `seat` | 唐宋系：各州府归属、治所 |
| `h` | 本节点突出显示的单位 |
| `lab` `kd` `col` | 本节点改用的标注名、单位类别、配色（与 `polities` 里不同时才写；`global/palette.toml` 定了色的政权不再逐节点改色） |
| `jn` | 两晋卷：本节点读入相邻卷的衔接疆域 |
| `ext` | 战国式 `j` `w`，唐宋系 `zb` `zl` |

单位的写法两套模型还不一样（政权键 / 序号）。第 5 步的统一疆域引擎读入时把两种模型合成一种「点 → 单位 → 政权」（`core/engine/data.py` 的 `view()`；春秋、战国取两卷共用的 `content/seeds.txt`）；v1 本身到第 7 步各卷换引擎时再改成这一种写法、单位一律用全局 ID（民国卷有两个政权的全局 ID 都是「日本」，届时先拆开）。

### 条目 `items`

| 字段 | 含义 |
| --- | --- |
| `i` | 序号 |
| `c` | 类别：`capital` `battle` `pass` `city` `town` `culture` `people` `event` `range` `river` `canal` `desert` `wall` `road` `route` `jun` `region` `conc` `rail` `air` 等 |
| `gid` | 都城、关隘指向全局地点；山川指向全局山川 |
| `old` `mod` `note` | 古名、今名、说明 |
| `lon` `lat` `geo` `anc` | 位置、线状几何、标注锚点 |
| `t` `t1` `tp` | 时点或起止 |
| `spans` | 多段年段（都城存续等） |
| `owners` | 战国式：归属变化 |
| `anim` | 两晋行军路线的动画时间（小数年，原样保留） |
| `at` | 都城所在的州府（`places` 序号） |
| `en` | 英文 |
| `_tf` `_yrs` `_e` | 只供转回旧格式 |

### 各卷特有 `ext`

| 字段 | 卷 | 含义 |
| --- | --- | --- |
| `falls` | 春秋、战国 | 灭国事件 |
| `alleg` | 春秋 | 各国的从属关系变化（「共主」着色用） |
| `playms` | 春秋、战国 | 播放时每个节点停留的毫秒数 |
| `p0` | 春秋、战国 | 年表从哪一年之后开始列事件 |
| `zhoue` | 汉末 | 州名英文 |
| `en` | 民国 | 界面英文 |

## 全局 ID 与引用

**引用**指各卷里的一条，写成 `卷短名:键`：政权 `tangsong:契丹`；唐宋系州府 `songyuan:相州`；条目 `chunqiu:i:303`（战国式的地点也是条目）。全局表的 `refs` 和审定清单里都用这种写法，`decisions.toml` 也一样。

**全局 ID** 是可读的中文名：

- 地点：各卷最常用的名字（不含括号）。同名的几处，引用最多的一处用本名，其余加今地，如 `西奈（埃及西奈半岛）`。
- 政权：各卷叫法不同时，取出现节点最多的一卷的叫法。同名的政权，统一王朝与南北朝诸朝用本名，同名的先秦诸侯国、十国政权加首见卷，如 `宋`（赵宋）与 `宋·春秋`、`陈`（南朝陈）与 `陈·春秋`、`唐`（李唐）与 `唐·春秋`。同名的二级单位一律注所属政权，如 `河北东路（宋）`、`河北东路（金）`。
- 山川：`类别:今名`，如 `river:黄河`、`range:秦岭`（各卷古名不一，今名通用）；今名是「已湮」「河南荥阳东北」这类说明时用古名。重名的用带括注的今名，如 `river:汉江（朝鲜半岛）`。
- 以上都可在 `decisions.toml` 里改；改后重名会报错。
- **已发布的 ID 不改**：深链接 `sel=place:…` 等跨卷通用。加卷（如第 6 步的秦汉卷）后，自动取名可能因多了一卷的写法而变；这时在 `[places.id]` `[polities.id]` `[physical.id]` 里把受影响的组钉回原 ID（引用写组里原有的一条，不写新卷的）。只有新卷把原本分开的两组连成一处时，ID 才不得不变，沿用其中一组的。

## 全局表怎么归并

**地点**。候选是各卷的地点，加上不在地点表里的都城、关隘条目。两两比较（同一卷内也比）：

1. 相距 1 km 以内：同一卷，或有一个名字相同，或今地相同 → 合并。
2. 相距 2 km 以内：有一个名字相同，或今地相同 → 合并。
3. 相距 30 km 以内：有一个名字相同 → 合并。
4. 都城条目的 `at` 指向的州府，相距 5 km 以内 → 合并。

「名字」把括号、顿号、间隔号里的写法也拆开算，如「长安（大兴城）」同时算「长安」「大兴城」。合并后坐标取各卷用得最多的一个；各卷坐标相距超过 2 km 的，在 `sites` 里逐个列出及所属卷。最远两点超过 40 km，或城址相距超过 5 km 的，列入 `review/places.md`。

字段：`id` `n` `names`（各卷用过的全部名字）`mod` `lon` `lat`（今天所在或最后一个城址）`eras` `refs` `en` `en_variants` `sites` `seats` `note`。

- `sites`：城址。人工审定过的写成 `[{lon, lat, from?, to?, note?}]`，`from` `to` 是起止年（都含），如长安 582 年前是汉长安城、583 年起是隋唐长安城；没审定、各卷坐标又相距 2 km 以上的，列出各卷各自的坐标 `[{lon, lat, eras}]`。
- `seats`：治所迁城挂过来的州府 `[{ref, from, to}]`，如两晋卷的相州 280—579 年挂在邺、580—581 年挂在安阳。

**地点的审定规则**（2026-11-15 与用户定）：

1. 同一座城，只是各卷取点不同：统一成最准的一个坐标。
2. 同一座城（同名，或只是改名），城被毁后在近处重建、或短距离迁址：仍是一个地点，坐标按年代分段。例：长安（汉城 → 隋大兴城）、洛阳（汉魏故城 → 隋唐城）、晋阳（979 年毁 → 唐明镇新城）、青州（广固 → 东阳城）。
3. 另一座城（原本就在、或另起新城，另有名字）：拆开。州郡治所从甲城迁到乙城时，这个州那一条按年代挂到两城上。例：邺与安阳（580 年相州移治）、上都与桓州、熊津与泗沘、定陶与菏泽。
4. 相距 40 km 以上的一律拆开。

各卷坐标与审定后的城址相距 2 km 以上的，自动列进 `global/corrections.md`，生成 v1 时照改（见下文「改正」）。

**政权**。同名（名称或键相同）、不同卷的两个政权，在下列情形合并：前后两段相隔不超过 60 年；或者前一段延续到前一卷末尾、后一段从后一卷开头出现，且两卷相邻（隔着空档首尾相接）。相隔更久、英文名又相同的（春秋的宋与赵宋），按不同政权处理，列入 `review/polities.md` 供核对。英文名不同的也列在那里；配色由 `global/palette.toml` 统一，套用后各卷仍不同的也列出（应为空）。

字段：`id` `n` `names` `kind`（以最后一卷为准；部族升为政权的另有 `kinds` 记各卷）`eras` `refs` `colors`（各卷 `[浅, 深]`，已套用 `global/palette.toml`）`en`。

改名、改国号的同一政权（契丹 → 辽，定难军 → 西夏，林邑 → 环王 → 占城），在 `decisions.toml` 的 `[polities] merge` 里合成一条。

**山川**。山脉、河流、运河、沙漠、长城、道路。几何完全相同的合并；类别相同、不同卷、名称或今名有一个相同、锚点相距不远（河流山脉 400 km，其他 150 km）的合并；今名完全相同、锚点在 1500 km 以内的也合并（长江、黄河在各卷的锚点可以相距很远）。各卷画法偏差超过 30 km 的列入 `review/physical.md`。

字段：`id` `c` `n` `names` `mod` `eras` `refs` `en` `en_variants` `time`（各卷所记起止，如运河开凿之年；`[t, null]` 表示从 t 起一直存在）`geo_variants` `geo_dev_km` `geo_from`（各卷画法不同时以哪一卷的几何为准）`note`。

随年代改道的河道（黄河故道、北流、南流夺淮，民国黄泛区）现在还是各卷底图 `base.rivers` 里带 `y0` `y1` 的线，没有并进山川表；第 4 步换全局底图时一起处理。

**译名**。每个全局对象、每个中文写法一条：`id` `kind` `zh` `en`。同一中文名各卷英文不同的：

- 统一成一种写法（`variants` 记原来各卷的写法，要改的卷列进改正清单）。山川默认统一成用得最多的写法，次数相同取较晚一卷；地点、政权要人工定。
- 或按时代各用各的（`by_era`）：不同时期的通行写法（麴氏高昌 Gaochang、回鹘高昌 Qocho；先秦的「河」He、此后的 Yellow River），或关隘与同名县城是两个对象（潼关 Tong Pass / Tongguan）。`en` 取最后一卷的写法。

各卷 `GLOSSARY.md` 里的行文约定还没并进来。

**衔接**。`registry.py` 比较相邻两卷在衔接年份的节点：共有政权的疆域重合度（交集 ÷ 并集），只在一边出现的政权，以及名字不同但疆域相交的（可能是同一政权改了名，也可能是一卷单列、另一卷并入了别的政权），写进 `review/junctions.md`。

## 审定流程

1. 运行 `python core/v1/registry.py`。
2. 看 `global/review/` 下的清单：`places.md` `polities.md` `physical.md` `glossary.md` `junctions.md`。每条都附了引用。
3. 把决定写进 `global/decisions.toml`（文件里有写法示例）：

| 段 | 写法 | 用途 |
| --- | --- | --- |
| `[[place]]` | `id`；`anchor`（自动归并出的那一组里任一条，整组照收）或 `refs`（人工列出的成员）；`add`；`mod`；`sites`；`note` | 定一个地点：成员、ID、城址 |
| `[[seat]]` | `ref`；`by = [[年份, 地点 ID], …]` | 治所迁城：这一条按年代挂到不同地点 |
| `[places]` | `split` `merge` `[places.id]` | 简单的拆、合、改 ID |
| `[polities]` | `merge`；`[polities.id]` | 合并政权、定 ID |
| `[physical]` | `split`；`[physical.id]`；`[physical.prefer]` `ID = {era, note}` | 拆出不是同一对象的；钉住 ID；各卷画法不同时以哪一卷为准 |
| `[glossary]` | `by_era`；`[glossary.unify]` `"ID|中文" = "English"` | 译名按时代各用各的，或统一成一种 |

4. 各卷页面里要改的内容（名称、归属、画错的山川等），写进 `global/corrections.toml`。
5. 再运行 `registry.py`，看清单、`global/corrections.md` 和 `git diff global/` 是否如愿。

配色不同的政权这一步只列出；统一时改按五德主色、邻接避让重定，写在 `global/palette.toml`（2026-11-17 定，见规范第三节）。

**第 2 步的审定已于 2026-11-15 完成**：68 处地点、16 处山川、168 处译名、979 年衔接都已定下，写在 `decisions.toml` 与 `corrections.toml` 里；各卷要改的坐标、内容、英文见 `global/corrections.md`。

## era.toml

每卷一份，手写：

| 字段 | 含义 |
| --- | --- |
| `slug` `volume` | 短名、卷次 |
| `title` `title_en` `short` `short_en` | 图名、短名（中英） |
| `years` | 起止年（含），与总页一致 |
| `time` `model` | 时间精度、数据模型 |
| `first` | 首屏节点：按年的卷写年，按月的卷写 `[年, 月]` |
| `nodes` | 节点数 |
| `[coloring]` | 着色切换：`modes`（按钮文字与代号）、`default` |
| `[layers]` | 用到的条目类别及条数 |
| `[projection]` | 新页面的投影参数（第 4 步起各卷统一，以 `core/geo/config.toml` 为准）；`legacy` 记旧版页面的原点纬线、中央经线 |
| `[engine]` | 统一疆域引擎的外缘设置（第 5 步，目前两晋、隋唐、宋元、民国、秦汉有；秦汉写 `production = true`，疆域直接由引擎出，见根目录 `run.py` 的两遍构建；第 7 步起旧卷写 `geometry = "engine"`（现为隋唐、两晋），页面疆域取 `eras/<短名>/engine.json`，生成 v1 时换进去，见 `core/v1/engine_geom.py`）：`outer` 为 `frontier`（手绘外缘）或 `reach`（按可达代价，另写推算范围 `box`、写 `R=` 倍数的 `seeds` 文件、设置文件 `config`、国界墙 `walls` 与省界 `prov_walls`），见 `core/engine/README.md` |
| `[junction.prev]` `[junction.next]` | 与前后两卷的衔接 |
| `[legacy]` | 旧仓库、旧网址、新网址 |

`build.py` 会核对 `time` `model` `nodes` `first` 与数据一致。

## junctions.toml

`[[junction]]`：`from` `to` `year` `kind`（`shared` 共用节点 / `adjacent` 相邻两年）`owner`（共用节点时以哪一卷为准）`note`。

`[[gap]]`：`after` `before` `years` `plan`（准备由哪一卷补上）。

## 改正（overlay，第 3 步起）

`build.py` 往返校验通过、附上全局 ID 之后，由 `core/v1/overlay.py` 在 v1 数据包上套用以下改正，记在 `meta.overlay`；`legacy.html` 与各卷源文件不动：

- **坐标**：`registry.py` 按 `decisions.toml` 的城址推出的坐标改正（`global/corrections.md`「坐标」一节，写在 `build/v1/fixes.json` 的 `coords`），条目点位与归属点都改；归属点连同它对应的条目一起挪。归属点是统一引擎的输入，所以坐标在换引擎几何（`engine_geom.py`）之前先套用（`overlay.apply_coords`，`registry.py` 生成全局表时同样先套用），`engine.json` 的指纹按改后的坐标算。一个点只有一个坐标：同一条有几段年代对不上城址的（治所迁城、改名），取最长的一段；最长的一段不到本条年代一半的不改；挪过去会与别的点重合之类的，写进 `decisions.toml` 的 `[places.keep]`（引用 = 原因），也不改；状态栏写「不改」与原因。春秋、战国的归属点不在 v1 里，改在两卷共用的 `content/seeds.txt`（第 3 步只改了唐宋系的都城、关隘等条目，归属点 2026-11-19 改完）。
- **山川改画**：`decisions.toml` 的 `[physical.prefer]` 写了 `page = true` 的，各卷页面上都画成选定那一卷的线与注记点（`fixes.json` 的 `ranges`；武陵山、伏牛山）。
- **英文译名**：`corrections.md`「英文」一节全部。
- **内容**：`global/corrections.toml` 里标了 `step = 3` 的，`id` 对应 `overlay.py` 里的改正函数。
- **时间轴短标题**：`eras/<短名>/short.tsv`，每个节点一行（按月的卷写 `年.月`），中文不超过 5 字。

`corrections.md` 末栏「状态」标明新页面已改，或为什么不改。
