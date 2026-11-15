# 英文译名体例（春秋列国形势图）

本图英文版的写法约定，与战国列国形势图的体例（zhanguo-map 仓库 `content/en/GLOSSARY.md`）一致，两图同名同译。总原则见《历史形势图统一规范》第十五节：只译中文已有的内容，不增不减；中文有误先改中文。

## 一、拼音

- 汉语拼音，不标声调；音节界限有歧义时加撇号：Xi'an、Chang'an。
- 多音字按地名旧读：乾时 Ganshi、乾溪 Ganxi、大原 Taiyuan（大读太）、不羹 Bulang、费 Bi、须句 Xuqu、华不注 Huafuzhu、栎 Li（郑之栎邑）、叶 She、六 Lu、番 Po、召陵 Shaoling、城父 Chengfu、句吴 Gouwu、会稽 Kuaiji、令支 Lingzhi、蓼 Liao、鄢 Yan、郪 Qi、繻葛 Xuge、鞌 An、邲 Bi、檇李 Zuili、柏举 Baiju、虢 Guo、郐 Kuai、鄫 Zeng、郯 Tan、莒 Ju、邾 Zhu。
- 人名多音字：管仲 Guan Zhong、伍员 Wu Yun（伍子胥 Wu Zixu）、子产 Zichan、叔向 Shuxiang、先轸 Xian Zhen、郤克 Xi Ke、栾书 Luan Shu。

## 二、国名

| 中文 | 英文 | 说明 |
| --- | --- | --- |
| 周（王畿） | Zhou (royal domain) | 同战国图 |
| 秦 楚 齐 燕 宋 鲁 越 巴 蜀 义渠 | Qin, Chu, Qi, Yan, Song, Lu, Yue, Ba, Shu, Yiqu | 同战国图 |
| 卫 | **Wey** | 同战国图，区别于魏 Wei |
| 中山（春秋称鲜虞） | Zhongshan（Xianyu） | 当年别名单独登记 |
| 晋 郑 陈 蔡 曹 吴 | Jin, Zheng, Chen, Cai, Cao, Wu | |
| 虢 东虢 虞 古魏 霍 耿 芮 梁 滑 庸 邢 郐 | Guo, East Guo, Yu, Old Wei, Huo, Geng, Rui, Liang, Hua, Yong, Xing, Kuai | 古魏为西周姬姓魏国，区别于战国魏 |
| 杞 莒 邾 滕 薛 郯 鄫 纪 莱 谭 遂 曲沃 | Qi, Ju, Zhu, Teng, Xue, Tan, Zeng, Ji, Lai, Tan, Sui, Quwo | |
| 许 申 息 邓 随 唐 黄 江 胡 沈 顿 蓼 六 群舒 巢 钟离 徐 | Xu, Shen, Xi, Deng, Sui, Tang, Huang, Jiang, Hu, Shen, Dun, Liao, Lu, Qunshu, Chao, Zhongli, Xu | |

**同音国名（经作者审定）**：齐/杞（Qi）、鲁/六（Lu）、申/沈（Shen）、许/徐（Xu）、随/遂（Sui）、谭/郯（Tan）都写相同拼音，不加声调、不另造区别；悬停、索引与图例在英文名后附汉字原名。地名同理：岐 Qi（“秦收岐西”作 west of Mount Qi，岐指岐山）、长岸 Chang'an、津 Jin、邲/费 Bi。

## 三、地名、四、人名与称号、五、书名、六、条目名、七、年代

与战国图体例相同：通名 Pass / Ford / Mount / Mountains / River / Marsh / Canal；今地由小到大逗号分隔；君主“谥号 + 爵 + of + 国”（Duke Huan of Qi、King Zhuang of Chu、Viscount Jian of Zhao）；战役 Battle of X，胜负 A defeated B，主将 A vs. B；公元前写 BC 放在最后。

春秋特有：
- 故城、遗址：… ruins（Han–Wei Luoyang ruins、Zhu state ruins）；故绛 Old Jiang。
- 之役、之战一律作 Battle of X（王官之役 Battle of Wangguan）；泽作 Marsh（笠泽之战 Battle of Li Marsh）；津作地名时照音（津之战 Battle of Jin），作渡口时作 Ford（茅津 Maojin Ford）。
- 氏（部族）作 lineage：潞氏 Lu lineage、皋落氏 Gaoluo lineage。
- 通行英文名优先：三家分晋 Partition of Jin，田氏代齐 Usurpation of Qi by Tian，弭兵之会 Assembly to end war，假道灭虢 Borrowing a road to conquer Guo，卧薪尝胆 Sleeping on brushwood and tasting gall，初税亩 First land tax by area (chushuimu)。
- 会盟：Covenant of X（践土之盟 Covenant of Jiantu）、Assembly at X（葵丘之会 Assembly at Kuiqiu）。
- 霸主 hegemon；卿 minister / ministerial lineage；六卿 the Six Ministerial Lineages。
- 《左传》 Zuozhuan，《春秋》 the Chunqiu (Spring and Autumn Annals)，《国语》 Guoyu，《公羊传》 Gongyang zhuan，《穀梁传》 Guliang zhuan。

## 八、诸族

戎 Rong，狄 Di，夷 Yi，蛮 Man：西戎 Western Rong、赤狄 Red Di、白狄 White Di、山戎 Mountain Rong、伊洛之戎 Rong of the Yi and Luo、陆浑之戎 Luhun Rong、大荔 Dali Rong、淮夷 Huai Yi、长狄 Tall Di、犬戎 Quanrong。

## 九、维护

同战国图：译文在 `content/en/`，每条英文登记所据中文的指纹（`zh.lock.json`），改了中文须补改英文后 `python tools/i18n.py lock`。
