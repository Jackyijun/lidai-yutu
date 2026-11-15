# 英文版译名与体例（GLOSSARY）

中文是源文本，英文按同一套键写在本目录的 `*.json` 里（结构见 `src/i18n.py` 开头）。本文件记录译名体例，新增或修改英文时照此执行；同一个名称在全图各处必须写法一致（地图注记、悬停说明、索引、对照表、年表、节点说明）。本图夹在《汉末三国形势图》（hanmosanguo-map，到 280 年）与《隋及唐初形势图》（suitang-map，从 581 年）之间，总原则与两卷的 GLOSSARY 相同；同一个中文名在两卷已有英文的，本图照用（同名同译），两卷写法不一时在下面写明取哪一种。

## 一、总原则

1. **说真话**：英文只翻译中文已有的内容，不增不减；中文本身有误时先改中文，再改英文（并运行 `python tools/i18n.py lock`）。
2. **通俗写法，全图统一**：采用英文读者最常见的写法（Fei River、Kumarajiva、Hephthalites、Gupta、Constantinople），不用学术转写。美式拼写（color、labor、center）。拼音撇号用直撇（Chang'an、Xi'an）。
3. **地名用当时当地的名称**：汉字圈的地名用拼音转写中文古名；汉字圈以外用当时当地名称的通行英文写法，不把中文译音再转回拼音（朅盘陀 Kabandha、特牧城 Vyadhapura、阿㝹罗陀补罗 Anuradhapura、特拉布宗 Trapezus、阿得水 Atil、文荼山 Vindhya Range）；只见于汉文史籍、别无通行写法的南海诸国照拼（盘盘 Panpan、丹丹 Dandan、婆利 Poli、诃罗单 Heluodan）。
4. **今地 / 今名**用今天的通行英文名和行政区（Xi'an, Shaanxi；Gimhae, South Gyeongsang, South Korea；İzmit, Türkiye）。方位写 “northwest of Linfen, Shanxi”；“一带” 写 “around …”；“一说” 写 “(or …)”；“地望有争议” 写 “(location disputed)”；“X—Y” 两地之间写 “X to Y”，路线的起讫用 en dash。土耳其作 Türkiye。
5. **地图注记不加中文里没有的消歧义**：同音的不同名称照写，靠位置、年代和悬停里的汉字区分（后凉、后梁都作 Later Liang；苻健、苻坚都作 Fu Jian；萧绎、萧懿都作 Xiao Yi；王浚、王濬都作 Wang Jun）。同一段说明里同时出现、不分开就会读错的同音人名，在英文名后加汉字区分：Fu Jian (苻健) / Fu Jian (苻坚)、Wang Yan (王衍)、Xiao Yi (萧懿)。
6. **中文名自带括注的照译**：晋（西晋·东晋）Jin (Western and Eastern Jin)、北凉（河西王）Northern Liang (King of Hexi)。括注里的「·」英文改用逗号或 and。政权全称可括注英文通行的别称（Linyi (Champa)、Hephthalites (White Huns)），地图短名（s）不括注。
7. 英文界面里，地图注记只显示英文；悬停说明、索引、对照表、年表在英文名后附注汉字原名。
8. **按语末的“（今名）”**表示条目名称是今名、当时没有这个名称；英文放在按语最末，写作 “The name is modern.”。

## 二、拼音与通名

| 类别 | 写法 | 例 |
|---|---|---|
| 拼音 | 不标声调；音节界限有歧义时加撇号；ü 保留 | Chang'an、Jian'an、Lü Guang、Lüliang、Bogulü |
| 多音字、旧读 | 按古地名、人名的传统读音 | 冯翊 Pingyi、会稽 Kuaiji、枹罕 Fuhan、乐都 Ledu、涂中 Chuzhong、西都 Xidu、碻磝 Qiao'ao、般阳 Panyang、浚仪 Junyi、沌口 Zhuankou、广阿 Guang'e、笮桥 Zuoqiao、越巂 Yuexi、濡水 Nuan River、㶟水 Lei River（均从汉末卷）、乞伏乾归 Qifu Gangui、万俟 Moqi、尉迟 Yuchi、尉元 Yu Yuan（单姓尉，与尉迟不同）、曹嶷 Cao Ni、太兴（年号）Taixing |
| 州（作政区：行文、官衔、方镇、势力注记、节点标题、视野名） | X Province | 荆州刺史 Inspector of Jing Province、王敦（荆江）Wang Dun (Jing and Jiang)、河西·凉州 Hexi & Liang Province |
| 州（作州治地名：归属点名称、点状条目名） | 单音节专名连写，多音节分写 Zhou；与隋唐卷一致 | 雍州 Yongzhou、原州（高平）Yuanzhou (Gaoping)、西宁州 Xining Zhou、相州之战 Battle of Xiangzhou |
| 郡 | X Commandery | 冯翊郡（临晋）Pingyi Commandery (Linjin)、乐浪郡 Lelang Commandery |
| 县 | X County（单字县名、带“县”字的） | 郑县 Zheng County、汧县 Qian County；两字县名直接拼（临晋 Linjin） |
| 国（王国、封国） | X Kingdom | 睢阳（梁国）Suiyang (Liang Kingdom) |
| 镇 | X Garrison | 统万镇 Tongwan Garrison、怀朔镇 Huaishuo Garrison；六镇 Six Garrisons |
| 城（城名的一部分） | City；朝鲜半岛高句丽的城作 Fortress | 统万城 Tongwan City、宁平城 Ningping City；国内城 Gungnae Fortress |
| 故地 | former X lands | 朔方故地 former Shuofang lands；真腊故地 Chenla homeland |
| 关 / 塞 / 陉 / 口 | Pass / Fort / Defile / Pass；已成专名者照拼 | 潼关 Tong Pass、卢龙塞 Lulong Fort、句注陉 Gouzhu Defile、井陉口 Jingxing Pass、古北口 Gubeikou、濡须口 Ruxukou |
| 水 / 河 / 江 | X River | 淝水 Fei River、湨水 Ju River、汾水 Fen River；江 Yangtze、河 Yellow River |
| 山 | 山脉 X Mountains；单峰、小山 Mount X | 太行山 Taihang Mountains；邙山 Mount Mang、钟山 Mount Zhong、蒜山 Mount Suan、覆舟山 Mount Fuzhou |
| 洲（江中沙洲） | X Islet | 峥嵘洲 Zhengrong Islet、桑落洲 Sangluo Islet |
| 陂 | 连写 | 白木陂 Baimubei；参合陂 Canhe Slope（英文通行名） |
| 蛮 / 夷 / 诸部 | tribes / peoples（不用 barbarian） | 蛮 Man tribes、五溪蛮 Five Streams tribes、诸羌 Qiang tribes |

## 三、政权、官爵与称号

| 中文 | 英文 | 说明 |
|---|---|---|
| 西晋 / 东晋 | Western Jin / Eastern Jin | 地图短名 Jin |
| 十六国 | Former / Later / Southern / Northern / Western + 国号 | 前赵 Former Zhao、后燕 Later Yan、北凉 Northern Liang、西秦 Western Qin；汉赵 Han Zhao、成汉 Cheng Han、冉魏 Ran Wei、翟魏 Zhai Wei |
| 南朝 | Song (Liu Song)、Qi (Southern Qi)、Liang、Chen | 地图短名 Song、Qi |
| 北朝 | Northern Wei、Eastern Wei、Western Wei、Northern Qi、Northern Zhou | |
| 晋宗室诸王、南朝宗王 | Name, Prince of X | 齐王司马冏 Sima Jiong, Prince of Qi；湘东王萧绎 Xiao Yi, Prince of Xiangdong |
| 十六国、诸胡君主自称的王 | King of X | 刘渊称汉王 King of Han、吕光三河王 King of Sanhe、天王 Heavenly King、大单于 Grand Chanyu |
| 称帝 / 即位 / 代 | proclaims himself emperor / takes the throne / replaces | 节点标题用一般现在时：Liu Song replaces Jin |
| 刺史 / 太守 / 内史 / 相 | Inspector / Administrator / Administrator / Chancellor | 荆州刺史 Inspector of Jing Province；历阳内史 Administrator of Liyang；广陵相 Chancellor of Guangling |
| 都督 / 大都督 / 总管 | Area Commander / Grand Area Commander / Superior Area Commander | |
| 大行台 | Grand Branch Department Director | 河南道大行台 Grand Branch Department Director of the Henan Circuit |
| 丞相 / 相国 / 大丞相 / 大司马 / 太尉 | Chancellor / Chancellor of State / Grand Chancellor / Grand Marshal / Grand Commandant | |
| 方镇 | regional command | 界面按钮 Commands；索引 Regional commands |
| 北府（兵） | Northern Headquarters (Army) | |
| 霸府 | headquarters | 高欢（晋阳霸府）Gao Huan (Jinyang headquarters) |
| 可汗 / 牙帐 | Qaghan / royal camp | 社仑 Shelun、阿那瓌 Anagui、土门 Tumen、伊利可汗 Il Qaghan（与隋唐卷颉利可汗 Illig Qaghan 区分）、室点密 Istämi |
| 流民 | refugees | 六郡流民 the refugees of six commanderies |
| 降户 | people who had surrendered | 六镇降户 Six Garrisons people who had surrendered（标题里作 Surrendered Six Garrisons people） |

## 四、人名、族名

- 汉人名姓在前、拼音；复姓连写（Sima Yue、Murong Ke、Tuoba Gui、Yuwen Tai、Helian Bobo、Juqu Mengxun、Tufa Rutan、Qifu Guoren、Erzhu Rong、Heba Yue、Houmochen Yue、Poliuhan Baling、Moqi Chounu、Hulü Guang）。帝王用 “Emperor + 谥号 + of + 朝”（Emperor Xiaowen of the Northern Wei、Emperor Wu of Liang）；废帝、后主照中文（Former Deposed Emperor、Last Ruler of Qi、Marquis of Donghun）。
- 族名照拼汉文史籍名：Xianbei、Xiongnu、Jie、Di、Qiang、Dingling、Lushui Hu、Tiefu、Jihu、Qihu；敕勒 Chile、高车 Gaoche、铁勒 Tiele；柔然 Rouran；嚈哒 Hephthalites；寄多罗 Kidarites。
- 朝鲜半岛用新罗马字（Goguryeo、Baekje、Silla、Gaya、Hanseong、Ungjin、Sabi、Geumseong、Gwansanseong；国王 King Jangsu、King Gwanggaeto、King Geunchogo）；日本用平文式（Wa、Yamato、Asuka、Nanotsu no Miyake）；越南保留声调符号（Lý Bí、Triệu Quang Phục、Lý Phật Tử、Vạn Xuân）。
- 西方与南亚用通行英文名：Diocletian、Constantine、Julian、Valens、Justinian、Belisarius、Zemarchus、Shapur II、Peroz、Khosrow I、Chandragupta、Samudragupta、Mihirakula、Yashodharman；Ctesiphon、Nicomedia、Antioch、Edessa、Pataliputra、Ujjayini、Valabhi、Kanchipuram。
- 书名、篇名译出意思：《晋书》Book of Jin、《魏书》Book of Wei、《洛阳伽蓝记》Record of the Buddhist Monasteries of Luoyang、《佛国记》Record of the Buddhist Kingdoms、《兰亭集序》Preface to the Orchid Pavilion Poems、《徙戎论》Essay on Moving the Rong。

## 五、年代

- 照写农历月序，不换算公历：383 年十一月 → 11th month, 383；闰十二月 → intercalary 12th month；正月 → 1st month；冬 → winter 279；跨年 → winter 279 – 3rd month, 280；同年 → 2nd–4th month, 450。
- 东亚以外的事件用儒略历月名（August 378、May 330）。
- 年号：拼音 + 序数（Taikang 1、Taiyuan 8），不写 “1st year of”。另一方年号写在括号或说明栏开头，加政权前缀：Wei: Tianxing 4 · Later Qin: Hongshi 3。无年号的纪年照中文：后赵赵王元年 Later Zhao: King of Zhao 1、西魏废帝元年 Western Wei: Deposed Emperor 1、北周孝闵帝元年 Northern Zhou: Emperor Xiaomin 1。
- 约 → c.；“一说” → (or …)；“X 年起” → from X；“X 世纪中叶” → mid-Xth century。

## 六、战役

- 名称：Battle of X / Siege of X / Fall of X / Raid on X；中文写成句子的照译（赫连定被擒 Capture of Helian Ding、突厥破柔然 The Turks crush the Rouran）。英文通行名照用（Battle of the Fei River、Battle of Canhe Slope、Battle of Adrianople）。
- 同名战役在英文里补年份（Battle of Luoyang (328) / (365)、Battle of Mount Mang (543) / (564)），这是第一节第 5 条的唯一例外。
- 交战结果 “A defeated B”；主将 “A and B vs. C”。部族、民族名前加 the（the Hephthalites、the Erzhu），政权名不加；节点标题与路线名里政权名前不加 the（Fall of Southern Yan），说明文字里照英文习惯加（the Later Zhao、the Northern Wei）。

## 七、与邻卷的取舍

- 与隋唐卷 581 年节点共有的政权、州名照隋唐卷英文，即使与本图第二、三节的写法不同：交州（李佛子）Jiaozhou (Lý Phật Tử)、高宝宁（营州）Gao Baoning (Yingzhou)、杨坚代周·隋朝建立 Yang Jian supplants the Zhou · Sui founded。
- 汉末卷与隋唐卷写法不一的：濡水取汉末卷 Nuan River；今地 “一带” 取隋唐卷 around X。
- 沿用隋唐卷的按语按本卷体例统一：“（今名）” 写 The name is modern.，“中原” 写 Central Plain（隋唐卷作 Central Plains）；作行政区的幽州在按语里写 You Province（隋唐卷作 Youzhou）。
- 本图改正了隋唐卷两处写法：筑紫（那津官家）Nanotsu no Miyake（隋唐卷作 Natsu）、特拉布宗用当时名称 Trapezus。

## 八、维护

- `python tools/i18n.py status`：缺译、过期、未登记指纹的条数。
- `python tools/i18n.py todo [文件]`：逐条列出缺译与过期的中文。
- 改完英文：`python tools/i18n.py lock` 记下中文指纹；以后中文一改，对应英文就会报“过期”。
- `python run.py --html` 默认严格：有缺译或过期就停下；`--draft` 允许先出草稿（缺译处显示中文）。
- `python tools/i18n.py table` 导出中英对照表 `build/i18n-review.tsv` 供审校。
