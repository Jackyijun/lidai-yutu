# -*- coding: utf-8 -*-
"""政权与部族（郡国单位在 src/build.py 里按用到的郡国自动生成，说明写治所）。

col：沿用邻卷的颜色写「zg:键」（战国卷）、「hm:键」（汉末卷），自定写色值，空着则按邻接关系从色板里挑。
kind：state 政权，tribe 部族（疆域按部族画法），zhen 二级单位（郡国、王国）。
"""

# 键, 名, 种类, 颜色, 说明, 英文名, 英文说明
_P = [
    ("秦", "秦", "state", "zg:秦", "前221 年秦王政灭六国，称始皇帝，分天下为三十六郡，后增至四十余郡；书同文、车同轨，统一度量衡。北逐匈奴、南取百越，筑长城、修驰道直道。前210 年始皇崩于沙丘，赵高、李斯矫诏立胡亥；前209 年陈胜起事，前207 年子婴降刘邦，秦亡（通鉴系于汉元年十月，即前206 年）。",
     "Qin", "In 221 BC King Zheng of Qin destroyed the six states, took the title First Emperor and divided the realm into thirty-six commanderies, later more than forty; he standardised the script, axle widths, weights and measures. Qin drove the Xiongnu north and conquered the Hundred Yue, building the Great Wall, the imperial highways and the Straight Road. The First Emperor died at Shaqiu in 210 BC and Zhao Gao and Li Si forged his will to enthrone Huhai; Chen Sheng rose in 209 BC, and Ziying surrendered to Liu Bang in 207 BC, ending Qin (dated by the Tongjian to the 10th month of Han year 1, i.e. 206 BC)."),
    ("卫", "卫", "state", "zg:卫", "秦并天下后唯卫君角仍守野王一隅，前209 年被秦二世废为庶人，卫绝祀。",
     "Wey", "After the Qin unification only Lord Jue of Wey still held a corner around Yewang; in 209 BC the Second Emperor deposed him, making him a commoner, and the line of Wey came to an end."),
    ("张楚", "张楚", "state", "zg:楚", "前209 年七月陈胜、吴广起于大泽乡，陈胜据陈称王，国号张楚，遣诸将四出略地；当年冬周文西攻至戏，败还。前208 年十二月陈胜为庄贾所杀，张楚瓦解。",
     "Zhang Chu", "In the 7th month of 209 BC Chen Sheng and Wu Guang rose at Dazexiang; Chen Sheng took Chen and proclaimed himself king of Zhang Chu, sending his generals out in all directions to seize territory. That winter Zhou Wen advanced west as far as Xi before being driven back. In the 12th month of 208 BC Chen Sheng was murdered by Zhuang Jia and Zhang Chu collapsed."),
    ("楚", "楚", "state", "zg:楚", "项梁、项羽起兵会稽，前208 年六月于盱台立楚怀王之孙心为楚王（仍号怀王），号令诸侯。巨鹿之战后诸侯将皆属项羽；前206 年正月项羽尊怀王为义帝，二月自立为西楚霸王。",
     "Chu", "Xiang Liang and Xiang Yu raised troops at Kuaiji, and in the 6th month of 208 BC at Xuyi set up Xin, grandson of King Huai of Chu, as king of Chu (still styled King Huai), to command the allied lords. After Julu all the allied generals came under Xiang Yu; in the 1st month of 206 BC Xiang Yu honoured King Huai as Righteous Emperor, and in the 2nd month made himself Hegemon-King of Western Chu."),
    ("西楚", "西楚", "state", "zg:楚", "项羽自立为西楚霸王，王梁楚九郡，都彭城，分封十八王。前205 年彭城一战大破汉军，与汉相持于荥阳、成皋；前203 年鸿沟议和，次年垓下败亡，楚地皆降。",
     "Western Chu", "Xiang Yu made himself Hegemon-King of Western Chu, ruling nine commanderies of Liang and Chu from Pengcheng, and enfeoffed eighteen kings. In 205 BC he routed the Han army at Pengcheng and held Han at bay around Xingyang and Chenggao; after the Honggou Canal truce of 203 BC he was defeated at Gaixia and died the following year and the Chu lands submitted."),
    ("赵", "赵", "state", "zg:赵", "前209 年八月武臣自立为赵王，旋为部将所杀；张耳、陈余立赵歇为王，都信都（襄国）。巨鹿之战前与张耳被秦军围于巨鹿城。分封后赵歇徙为代王，陈余逐张耳、迎赵歇复王赵；前204 年韩信破赵于井陉，斩陈余，擒赵歇。",
     "Zhao", "In the 8th month of 209 BC Wu Chen made himself king of Zhao and was soon killed by one of his generals; Zhang Er and Chen Yu then set up Zhao Xie as king at Xindu (Xiangguo); before the battle of Julu he and Zhang Er were besieged by Qin in the city of Julu. At the enfeoffment Zhao Xie was moved to Dai, but Chen Yu drove out Zhang Er and brought him back as king of Zhao; in 204 BC Han Xin broke Zhao at Jingxing, beheading Chen Yu and capturing Zhao Xie."),
    ("齐", "齐", "state", "zg:齐", "前209 年田儋自立为齐王；田儋战死后田荣立田市。分封时项羽三分齐地，田荣不服，并三齐自立；田荣死后其弟田横立田广。前203 年韩信破齐，田广被俘，田横逃入海岛。",
     "Qi", "In 209 BC Tian Dan made himself king of Qi; after he fell in battle Tian Rong set up Tian Shi. Xiang Yu split Qi in three at the enfeoffment, but Tian Rong refused to accept it and took all three for himself; after his death his brother Tian Heng set up Tian Guang. In 203 BC Han Xin conquered Qi, Tian Guang was captured and Tian Heng fled to an island."),
    ("燕", "燕", "state", "zg:燕", "前209 年韩广自立为燕王。分封时项羽以燕将臧荼为燕王、徙韩广为辽东王，臧荼随即击杀韩广，并辽东。前204 年降汉；前202 年反，被擒，卢绾继为燕王。",
     "Yan", "Han Guang made himself king of Yan in 209 BC. At the enfeoffment Xiang Yu made the Yan general Zang Tu king of Yan and moved Han Guang to Liaodong, whereupon Zang Tu killed Han Guang and annexed Liaodong. Yan submitted to Han in 204 BC; Zang Tu rebelled in 202 BC and was captured, and Lu Wan became king of Yan."),
    ("魏", "魏", "state", "zg:魏", "前209 年魏咎被立为魏王，都临济；前208 年章邯破临济，魏咎自焚。其弟魏豹复得魏地，分封时被徙为西魏王（见「西魏」）。",
     "Wei", "Wei Jiu was set up as king of Wei at Linji in 209 BC; when Zhang Han took Linji in 208 BC, Wei Jiu burned himself to death. His brother Wei Bao recovered the Wei lands and at the enfeoffment was moved to be king of Western Wei (see Western Wei)."),
    ("韩", "韩", "state", "zg:韩", "前208 年项梁立韩国公子成为韩王，张良为司徒，略取韩地。分封时韩成不得就国，为项羽所杀；后韩王信（韩襄王孙）随汉定韩地，前205 年立为韩王。",
     "Han (韓)", "In 208 BC Xiang Liang made Prince Cheng of the old Han royal house king of Han (韓), with Zhang Liang as minister, to win back the Han lands. At the enfeoffment Han Cheng was not allowed to go to his kingdom and was killed by Xiang Yu; later Han Xin (a grandson of King Xiang of Han (韓), not the general Han Xin), fighting for Liu Bang, took the Han (韓) lands and was made king of Han (韓) in 205 BC."),
    ("汉", "汉", "state", "hm:汉", "前206 年二月刘邦受封为汉王，王巴蜀汉中，都南郑；同年八月还定三秦，前202 年灭项羽，即皇帝位，都长安。汉承秦制而郡国并行：王国自置官吏，七国之乱后削藩、推恩，王国渐与郡同。武帝北逐匈奴、通西域，南平南越、西南夷，东灭朝鲜，疆域大拓。9 年王莽代汉；25 年刘秀称帝，都洛阳（东汉），36 年复一统。",
     "Han", "Liu Bang was enfeoffed as king of Han in the 2nd month of 206 BC, ruling Ba, Shu and Hanzhong from Nanzheng; that 8th month he retook the Three Qins, and in 202 BC, having destroyed Xiang Yu, he took the imperial title with his capital at Chang'an. Han kept the Qin system but ran commanderies and kingdoms side by side: kings appointed their own officials until, after the Rebellion of the Seven States, as the kingdoms were cut back and then divided under the Edict of Grace, they became little different from commanderies. Emperor Wu drove back the Xiongnu, opened the Western Regions, conquered Nanyue and the Southwestern peoples and destroyed Joseon, greatly enlarging the empire. Wang Mang took the throne in AD 9; Liu Xiu proclaimed himself emperor in 25 with his capital at Luoyang (Eastern Han) and reunited the realm in 36."),
    ("雍", "雍", "state", "#8A7298", "秦降将章邯，前206 年受封为雍王，王咸阳以西，都废丘。同年八月刘邦还定三秦，章邯困守废丘，前205 年城破自杀。",
     "Yong", "Zhang Han, the surrendered Qin general, was made king of Yong in 206 BC, ruling the land west of Xianyang from Feiqiu. When Liu Bang retook the Three Qins that 8th month Zhang Han was besieged in Feiqiu, and killed himself when it fell in 205 BC."),
    ("塞", "塞", "state", "#D4B08B", "秦降将司马欣，前206 年受封为塞王，王咸阳以东至河，都栎阳；同年降汉。",
     "Sai", "Sima Xin, a surrendered Qin general, was made king of Sai in 206 BC, ruling from Xianyang east to the Yellow River with his capital at Yueyang; he submitted to Han the same year."),
    ("翟", "翟", "state", "#5C9B83", "秦降将董翳，前206 年受封为翟王，王上郡，都高奴；同年降汉。",
     "Di", "Dong Yi, a surrendered Qin general, was made king of Di in 206 BC, ruling Shang Commandery from Gaonu; he submitted to Han the same year."),
    ("西魏", "西魏", "state", "zg:魏", "前206 年魏豹徙封西魏王，王河东，都平阳。前205 年从汉伐楚，彭城败后叛汉；同年九月韩信木罂渡河，虏魏豹，置河东、太原、上党郡。",
     "Western Wei", "Wei Bao was moved to be king of Western Wei in 206 BC, ruling Hedong from Pingyang. In 205 BC he joined Han against Chu but turned against Han after Pengcheng; that 9th month Han Xin crossed the Yellow River on wooden jars and captured him, and Hedong, Taiyuan and Shangdang became commanderies."),
    ("河南", "河南", "state", "#86A8CC", "赵将申阳先下河南，前206 年受封为河南王，都洛阳；前205 年降汉，以其地为河南郡。",
     "Henan", "Shen Yang, a Zhao general who had first taken Henan, was made king of Henan in 206 BC with his capital at Luoyang; he submitted to Han in 205 BC and his land became Henan Commandery."),
    ("殷", "殷", "state", "#A0756A", "赵将司马卬定河内，前206 年受封为殷王，都朝歌。前205 年汉虏司马卬，以其地为河内郡。",
     "Yin", "Sima Ang, a Zhao general who had taken Henei, was made king of Yin in 206 BC with his capital at Zhaoge. Han captured him in 205 BC and made his land Henei Commandery."),
    ("代", "代", "state", "#C3B888", "前206 年赵歇徙为代王；陈余迎赵歇复王赵，赵歇立陈余为代王，陈余留赵辅政，使夏说守代。前205 年后九月韩信破代，擒夏说。",
     "Dai", "Zhao Xie was moved to be king of Dai in 206 BC; when Chen Yu brought him back to Zhao, Zhao Xie made Chen Yu king of Dai; Chen Yu stayed at Zhao Xie's side and left Xia Yue to hold Dai. Han Xin broke Dai and captured Xia Yue in the intercalary 9th month of 205 BC."),
    ("常山", "常山", "state", "#B091BF", "前206 年张耳受封为常山王，王赵地，都襄国；前205 年陈余袭破之，张耳奔汉。",
     "Changshan", "Zhang Er was made king of Changshan in 206 BC, ruling the Zhao lands from Xiangguo; Chen Yu attacked and broke him in 205 BC and Zhang Er fled to Han."),
    ("九江", "九江", "state", "#DDA99A", "楚将英布（黥布），前206 年受封为九江王，都六。前204 年归汉，九江之地为项羽所并；前203 年改封淮南王。",
     "Jiujiang", "Ying Bu (Qing Bu), a Chu general, was made king of Jiujiang in 206 BC with his capital at Lu. He went over to Han in 204 BC and Xiang Yu took his land; in 203 BC he was re-enfeoffed as king of Huainan."),
    ("衡山", "衡山", "state", "#87C2D3", "番君吴芮，前206 年受封为衡山王，都邾。前202 年徙为长沙王。",
     "Hengshan", "Wu Rui, Lord of Po, was made king of Hengshan in 206 BC with his capital at Zhu. In 202 BC he was moved to be king of Changsha."),
    ("临江", "临江", "state", "#A8A86A", "楚柱国共敖，前206 年受封为临江王，都江陵；其子共尉嗣立，前202 年汉虏之。",
     "Linjiang", "Gong Ao, a pillar of state of Chu, was made king of Linjiang in 206 BC with his capital at Jiangling; his son Gong Wei succeeded him and was captured by Han in 202 BC."),
    ("辽东", "辽东", "state", "#95C4A7", "前206 年韩广由燕王徙为辽东王，都无终；不肯就国，同年为臧荼所杀，辽东并于燕。",
     "Liaodong", "In 206 BC Han Guang was moved from Yan to be king of Liaodong at Wuzhong; he refused to go and was killed by Zang Tu the same year, Liaodong passing to Yan."),
    ("胶东", "胶东", "state", "#D3A8C7", "前206 年田市徙为胶东王，都即墨；田荣怒而击杀之。",
     "Jiaodong", "Tian Shi was moved to be king of Jiaodong at Jimo in 206 BC; Tian Rong, enraged, attacked and killed him."),
    ("济北", "济北", "state", "#8985B8", "齐将田安，前206 年受封为济北王，都博阳；同年为田荣所杀。",
     "Jibei", "Tian An, a Qi general, was made king of Jibei at Boyang in 206 BC and killed by Tian Rong the same year."),
    ("新", "新", "state", "#B39A72", "王莽以外戚辅政，元始年间封安汉公、宰衡；8 年十二月称帝，国号新，改元始建国（9）。托古改制：王田、私属，五均六筦，屡改币制与郡县名，又贬四夷王号，与匈奴、西域、高句丽失和。17 年起绿林、赤眉相继而起，23 年昆阳大败，长安城破，王莽被杀。",
     "Xin", "Wang Mang ruled for the Han court as an imperial in-law, being made Duke Who Secures the Han and Chief Steward in the Yuanshi years; in the 12th month of AD 8 he took the throne, naming his dynasty Xin with the era Shijianguo (AD 9). His reforms, modelled on antiquity, nationalised land and banned the sale of slaves, set up state monopolies and price controls, repeatedly changed the coinage and the names of commanderies and counties, and demoted the rulers of the neighbouring peoples, falling out with the Xiongnu, the Western Regions and Goguryeo. The Lülin and Red Eyebrows rose from 17; after the disaster at Kunyang in 23 Chang'an fell and Wang Mang was killed."),
    ("更始", "更始", "state", "#C8A86E", "绿林军拥立的汉宗室刘玄，23 年二月称帝，年号更始；昆阳之战后入洛阳、长安。25 年赤眉入长安，更始降，旋被杀。",
     "Gengshi", "Liu Xuan, a member of the Han royal clan raised up by the Lülin army, proclaimed himself emperor in the 2nd month of AD 23 with the era name Gengshi, and after Kunyang entered Luoyang and Chang'an. When the Red Eyebrows took Chang'an in 25 he surrendered and was soon killed."),
    ("赤眉", "赤眉", "state", "#C3866E", "琅邪人樊崇等 18 年起于莒，以朱涂眉为号。25 年立刘盆子为帝，入长安；27 年粮尽东归，降刘秀于宜阳。",
     "Red Eyebrows", "Fan Chong and others from Langya rose at Ju in AD 18, painting their eyebrows red to mark themselves. In 25 they set up Liu Penzi as emperor and entered Chang'an; in 27, out of food, they turned east and surrendered to Liu Xiu at Yiyang."),
    ("隗嚣", "隗嚣", "state", "#9E8E6A", "天水隗嚣 23 年起兵，据陇右，称西州上将军，先附更始、后附刘秀，30 年反汉，31 年称臣公孙述。33 年病死，34 年其子隗纯降。",
     "Wei Xiao", "Wei Xiao of Tianshui rose in AD 23 and held Longyou as Supreme General of the Western Province, submitting first to Gengshi and then to Liu Xiu; in 30 he turned against Han, and in 31 declared himself a vassal of Gongsun Shu. He died of illness in 33 and his son Wei Chun surrendered in 34."),
    ("成家", "成家", "state", "#A9A06C", "导江卒正公孙述 25 年在成都称帝，国号成家，据巴蜀。36 年吴汉攻破成都，公孙述伤重而死。",
     "Chengjia", "Gongsun Shu, governor of Daojiang, proclaimed himself emperor at Chengdu in AD 25, naming his state Chengjia and holding Ba and Shu. Wu Han took Chengdu in 36 and Gongsun Shu died of his wounds."),
    ("刘永", "刘永", "state", "#BBA0B8", "梁王刘永 25 年在睢阳称帝，据梁、楚、沛之地；27 年败死，其子刘纡 29 年覆灭。",
     "Liu Yong", "Liu Yong, king of Liang, proclaimed himself emperor at Suiyang in AD 25, holding Liang, Chu and Pei; he was defeated and killed in 27, and his son Liu Yu was wiped out in 29."),
    ("张步", "张步", "state", "#A792B5", "琅邪张步据齐地十二郡，受刘永封为齐王；29 年耿弇破之于临淄，张步降。",
     "Zhang Bu", "Zhang Bu of Langya held twelve commanderies of Qi and was made king of Qi by Liu Yong; Geng Yan broke him at Linzi in AD 29 and he surrendered."),
    ("董宪", "董宪", "state", "#B5A0A8", "董宪据东海郯县，受刘永封为海西王；30 年败死。",
     "Dong Xian", "Dong Xian held Tan in Donghai and was made king of Haixi by Liu Yong; he was defeated and killed in AD 30."),
    ("彭宠", "彭宠", "state", "#9C9DBE", "渔阳太守彭宠 26 年反于渔阳，27 年自立为燕王；29 年为奴所杀。",
     "Peng Chong", "Peng Chong, governor of Yuyang, rebelled in AD 26 and made himself king of Yan in 27; he was murdered by his slaves in 29."),
    ("秦丰", "秦丰", "state", "#A2B49A", "秦丰据南郡黎丘，自号楚黎王；29 年降，被杀。",
     "Qin Feng", "Qin Feng held Liqiu in Nan Commandery as King of Chu-Li; he surrendered and was executed in AD 29."),
    ("李宪", "李宪", "state", "#B0B48A", "庐江李宪据舒称淮南王，后称帝；30 年败死。",
     "Li Xian", "Li Xian of Lujiang held the city of Shu (in Lujiang) as king of Huainan and later as emperor; he was defeated and killed in AD 30."),
    ("卢芳", "卢芳", "state", "#9A8E7C", "安定卢芳诈称汉武帝曾孙刘文伯，在匈奴支持下据五原、朔方、云中、定襄、雁门五郡，29 年称帝于九原；40 年降汉，旋复入匈奴。",
     "Lu Fang", "Lu Fang of Anding, falsely claiming to be Liu Wenbo, a great-grandson of Emperor Wu, held the five commanderies of Wuyuan, Shuofang, Yunzhong, Dingxiang and Yanmen with Xiongnu support and proclaimed himself emperor at Jiuyuan in AD 29; he surrendered to Han in 40 but soon went back to the Xiongnu."),
    ("窦融", "河西（窦融）", "state", "hm:河西诸郡", "更始时窦融为张掖属国都尉，据河西五郡，号河西大将军，保境安民；29 年归附刘秀，36 年入朝，河西归东汉。",
     "Hexi (Dou Rong)", "Under Gengshi Dou Rong was commandant of the Zhangye Dependent State and held the five commanderies of Hexi as Grand General of Hexi, keeping the region at peace; he submitted to Liu Xiu in AD 29 and went to court in 36, and Hexi passed to the Eastern Han."),
    ("黄巾", "黄巾", "state", "hm:黄巾", "巨鹿人张角以太平道传教十余年，信众数十万，分三十六方。184 年二月以「苍天已死，黄天当立」为号同日起事，七州二十八郡响应。",
     "Yellow Turbans", "Zhang Jue of Julu spent more than ten years spreading the Way of Great Peace, gaining hundreds of thousands of followers organised in thirty-six divisions. In the 2nd month of 184 they rose on a single day under the slogan \"The Blue Heaven is dead; the Yellow Heaven shall rise\", with twenty-eight commanderies in seven provinces responding."),
    ("凉州叛军", "凉州叛军", "state", "hm:韩遂", "184 年冬北地先零羌与枹罕、河关群盗反，劫持边章、韩遂，攻杀金城太守，凉州大乱。",
     "Liang Province rebels", "In the winter of 184 the Xianlian Qiang of Beidi and bandits of Fuhan and Heguan rose, seized Bian Zhang and Han Sui, and killed the governor of Jincheng, throwing Liang Province into chaos."),
    ("宋建", "宋建", "state", "hm:宋建", "枹罕宋建 184 年乘凉州之乱自立，号河首平汉王，割据三十余年。",
     "Song Jian", "Song Jian of Fuhan took advantage of the disorder in Liang Province in 184 to set himself up as King of the Yellow River's Head Who Pacifies Han, holding out for more than thirty years."),
    # ---------------- 北方草原 ----------------
    ("匈奴", "匈奴", "tribe", "hm:北匈奴", "秦时头曼单于居漠南，前214 年为蒙恬所逐。前209 年冒顿杀父自立，东灭东胡，西走月氏，南并楼烦、白羊，北服丁零、坚昆，控弦三十余万，前200 年围汉高祖于白登。汉初和亲；武帝时屡遭重创，远遁漠北。前57 年五单于争立，后分为呼韩邪、郅支两部；呼韩邪称臣于汉。48 年再分南北。",
     "Xiongnu", "Under Qin the chanyu Touman lived south of the Gobi until Meng Tian drove him out in 214 BC. In 209 BC Modu killed his father and took power; he destroyed the Donghu to the east, drove off the Yuezhi to the west, absorbed the Loufan and Baiyang to the south and subdued the Dingling and Jiankun to the north, commanding over 300,000 archers, and in 200 BC besieged Emperor Gaozu of Han at Baideng. Early Han bought peace with marriage alliances; under Emperor Wu the Xiongnu suffered heavy defeats and withdrew north of the Gobi. In 57 BC five chanyus contended and the Xiongnu split between Huhanye and Zhizhi, Huhanye becoming a Han vassal. In AD 48 they split again into north and south."),
    ("呼韩邪", "呼韩邪（南匈奴）", "tribe", "hm:南匈奴", "五单于争立中，呼韩邪单于为郅支所败，前53 年遣子入侍，前51 年亲朝甘泉宫，称臣于汉，居光禄塞下；前43 年北归单于庭。",
     "Huhanye (southern Xiongnu)", "Defeated by Zhizhi in the struggle of the five chanyus, Huhanye sent his son to serve at the Han court in 53 BC, came in person to the Ganquan Palace in 51 BC and declared himself a Han vassal, living near the Guanglu Fort; he returned north to the chanyu's court in 43 BC."),
    ("郅支", "郅支（北匈奴）", "tribe", "hm:北匈奴", "郅支单于据漠北，前49 年西击坚昆、乌揭，徙居坚昆；前44 年杀汉使，西投康居，筑郅支城于都赖水。前36 年陈汤、甘延寿发西域兵攻杀之。",
     "Zhizhi (northern Xiongnu)", "The chanyu Zhizhi held the north of the Gobi; in 49 BC he struck west at the Jiankun and Wujie and moved to the Jiankun lands, and in 44 BC, having killed a Han envoy, went west to Kangju and built a fortress on the Talas. In 36 BC Chen Tang and Gan Yanshou raised the forces of the Western Regions and killed him."),
    ("北匈奴", "北匈奴", "tribe", "hm:北匈奴", "48 年匈奴分裂，蒲奴单于据漠北，是为北匈奴。73 年起汉屡出击，89 年窦宪破之于稽落山，91 年北单于西遁，余部或降鲜卑；残部活动于蒲类、伊吾一带，屡寇西域。",
     "Northern Xiongnu", "When the Xiongnu split in AD 48 the chanyu Punu held the north of the Gobi: these were the Northern Xiongnu. Han attacked them repeatedly from 73; Dou Xian crushed them at Mount Jiluo in 89, and in 91 the northern chanyu fled west, many of his people joining the Xianbei, while remnants roamed around Pulei and Yiwu, raiding the Western Regions."),
    ("南匈奴", "南匈奴", "tribe", "hm:南匈奴", "48 年匈奴南边八部共立日逐王比为呼韩邪单于，附汉，是为南匈奴。50 年入居西河美稷，汉置使匈奴中郎将监护；单于遣诸部分屯北地、朔方、五原、云中、定襄、雁门、代郡，为汉守边。89—91 年随窦宪击破北匈奴。此后一直作为内属部族居于北边诸郡，188 年单于羌渠为国人所杀，其子於夫罗流寓河东；216 年曹操分其众为五部。图上 50 年以后画作内属于汉（斜线）。",
     "Southern Xiongnu", "In AD 48 the eight southern Xiongnu tribes made Bi, the Rizhu king, chanyu with the title Huhanye; he submitted to Han, and these were the Southern Xiongnu. In 50 they settled at Meiji in Xihe under a Han General of the Household Sent to the Xiongnu, and the chanyu stationed his tribes in Beidi, Shuofang, Wuyuan, Yunzhong, Dingxiang, Yanmen and Dai to guard the frontier for Han. In 89–91 they fought beside Dou Xian to crush the Northern Xiongnu. From then on they lived inside the northern commanderies as a dependent people; in 188 the chanyu Qiangqu was killed by his own people and his son Yufuluo was stranded in Hedong, and in 216 Cao Cao divided them into five divisions. From 50 the map shows them as nominally submitted to Han (hatched)."),
    # 匈奴诸部（「郡国」着色下分部显示，「政权」着色下合为匈奴；界线为示意）
    ("单于本部", "单于本部", "tribe", None, "单于直辖之地。《史记·匈奴列传》：「单于之庭直代、云中。」前123 年单于用赵信计「益北绝幕」，王庭北移；前119 年漠北之战后「漠南无王庭」。王庭所在史无确地，图上标在杭爱山东麓只是大致；各部之间也无明界，沿山川示意。",
     "Chanyu's own domain", "Land under the chanyu's direct rule. The Shiji says the chanyu's court lay opposite Dai and Yunzhong; in 123 BC, on Zhao Xin's advice, the chanyu moved 'further north across the Gobi', and after the battle beyond the Gobi (119 BC) 'there was no royal court south of the Gobi'. The sources fix no site for the court, so its place at the eastern foot of the Khangai Mountains is only approximate; nor do they give borders between the divisions, which the map draws along mountains and rivers as a sketch."),
    ("左贤王", "左贤王", "tribe", None, "匈奴左方（东方）诸王将之地，左贤王常为单于储副。《史记·匈奴列传》：「诸左方王将居东方，直上谷以往者，东接秽貉、朝鲜。」前119 年霍去病出代郡破左贤王，封狼居胥山。界线为示意。",
     "Wise King of the Left", "Land of the kings and generals of the Xiongnu left (east); the Wise King of the Left was usually the chanyu's heir. The Shiji says they lived in the east, opposite Shanggu and beyond, bordering the Ye-Maek and Joseon. In 119 BC Huo Qubing came out of Dai, broke the Wise King of the Left and sacrificed on Mount Langjuxu. The borders are a sketch."),
    ("右贤王", "右贤王", "tribe", None, "匈奴右方（西方）诸王将之地。《史记·匈奴列传》：「右方王将居西方，直上郡以西，接月氏、氐、羌。」前124 年卫青出高阙，夜围右贤王，右贤王仅以身免。界线为示意。",
     "Wise King of the Right", "Land of the kings and generals of the Xiongnu right (west). The Shiji says they lived in the west, opposite Shang Commandery and beyond, bordering the Yuezhi, the Di and the Qiang. In 124 BC Wei Qing came out through Gaoque and surrounded the Wise King of the Right by night; the king barely escaped with his life. The borders are a sketch."),
    ("浑邪王", "浑邪王", "tribe", None, "河西走廊西部，属匈奴右方。《汉书·地理志》张掖郡下：「故匈奴昆邪王地。」昆邪即浑邪。前121 年霍去病两击河西后，浑邪王杀休屠王，率众四万余人降汉。",
     "Hunye king", "The western Hexi Corridor, part of the Xiongnu right. The Han shu Treatise on Geography notes under Zhangye that it was 'formerly the land of the Xiongnu Kunye king' (Kunye being Hunye). After Huo Qubing's two strikes into Hexi in 121 BC the Hunye king killed the Xiutu king and surrendered to Han with over 40,000 people."),
    ("休屠王", "休屠王", "tribe", None, "河西走廊东部，属匈奴右方。《汉书·地理志》武威郡下：「故匈奴休屠王地。」前121 年霍去病获休屠王祭天金人；同年休屠王欲降而悔，为浑邪王所杀，其子金日磾入汉。",
     "Xiutu king", "The eastern Hexi Corridor, part of the Xiongnu right. The Han shu Treatise on Geography notes under Wuwei that it was 'formerly the land of the Xiongnu Xiutu king'. In 121 BC Huo Qubing took the golden statue the Xiutu king used to worship Heaven; that year the king, having agreed to surrender, changed his mind and was killed by the Hunye king, and his son Jin Midi went to Han."),
    ("楼烦白羊", "楼烦王·白羊王", "tribe", None, "河南地（河套）的楼烦王、白羊王。前209 年后匈奴乘秦末之乱复度河南；前127 年卫青取河南，「走白羊、楼烦王」，置朔方、五原郡。",
     "Loufan and Baiyang kings", "The Loufan and Baiyang kings of the Ordos, the land 'south of the River' inside the Yellow River bend. The Xiongnu crossed back into the Ordos in the chaos after 209 BC; in 127 BC Wei Qing took the Ordos, 'driving off the Baiyang and Loufan kings', and set up Shuofang and Wuyuan commanderies."),
    ("南边八部", "南边八部（日逐王比）", "tribe", None, "王莽末至建武年间，单于舆以比为右薁鞬日逐王，部领匈奴南边八部及乌桓（《后汉书·南匈奴列传》）。48 年八部共立比为呼韩邪单于，即南匈奴。",
     "Eight southern tribes (Bi, the Rizhu king)", "Under the chanyu Yu (from the end of Wang Mang's reign into the Jianwu era) Bi was the Right Yujian Rizhu king, in charge of the eight southern Xiongnu tribes and the Wuhuan (Hou Han shu, Southern Xiongnu). In AD 48 the eight tribes made Bi chanyu as Huhanye: these became the Southern Xiongnu."),
    ("北单于本部", "北单于本部", "tribe", None, "北单于直辖的漠北之地，王庭在今蒙古国杭爱山东麓一带。89 年窦宪破之于稽落山，91 年耿夔围北单于于金微山，北单于西遁。界线为示意。",
     "Northern chanyu's own domain", "The land north of the Gobi under the northern chanyu's direct rule, with his court around the eastern foot of the Khangai Mountains. Dou Xian crushed him at Mount Jiluo in 89, and in 91 Geng Kui surrounded him at the Jinwei Mountains and he fled west. The borders are a sketch."),
    ("呼衍王", "呼衍王", "tribe", None, "北匈奴西部的呼衍氏贵种，常在蒲类海（今巴里坤湖）一带游牧，控制车师、伊吾，屡寇西域（《后汉书·西域传》）。73 年窦固破之于天山，124 年后班勇屡与之争车师。界线为示意。",
     "Huyan king", "The noble Huyan clan in the west of the Northern Xiongnu lands, who roamed around Lake Pulei (Lake Barkol), controlled Jushi and Yiwu and raided the Western Regions again and again (Hou Han shu, Western Regions). Dou Gu beat them in the Tianshan in 73, and from 124 Ban Yong fought them repeatedly for Jushi. The borders are a sketch."),
    ("东胡", "东胡", "tribe", "#8F9A6A", "战国以来居燕北的游牧部族，秦末强盛，向冒顿索宝马、阏氏与弃地；前206 年为冒顿所灭，余众退保乌桓山、鲜卑山，分为乌桓、鲜卑。",
     "Donghu", "Nomads living north of Yan since the Warring States, the Donghu grew strong at the end of Qin and demanded of Modu his best horse, his consort and the empty land between them; Modu destroyed them in 206 BC, and the survivors withdrew to the Wuhuan and Xianbei mountains, becoming the Wuhuan and the Xianbei."),
    ("乌桓", "乌桓", "tribe", "hm:乌桓", "东胡余部，居乌桓山，役属匈奴。前119 年汉破匈奴左地，徙乌桓于上谷、渔阳、右北平、辽西、辽东五郡塞外，置护乌桓校尉。49 年入居塞内。",
     "Wuhuan", "Remnants of the Donghu living around the Wuhuan Mountains and subject to the Xiongnu. After Han broke the Xiongnu left wing in 119 BC the Wuhuan were moved beyond the frontier of the five commanderies from Shanggu to Liaodong under a Protector of the Wuhuan. In AD 49 they moved inside the frontier."),
    ("鲜卑", "鲜卑", "tribe", "hm:鲜卑", "东胡余部，居鲜卑山（大兴安岭）。东汉初渐南下，北匈奴西遁后尽据其地，余众十余万落自号鲜卑。156 年前后檀石槐统一诸部，分东、中、西三部，东接夫余、西接乌孙，177 年大败汉军。",
     "Xianbei", "Remnants of the Donghu living in the Xianbei Mountains (the Greater Khingan). They moved south in the early Eastern Han, and after the Northern Xiongnu fled west took over all their land, more than a hundred thousand Xiongnu households calling themselves Xianbei. Around 156 Tanshihuai united the tribes in eastern, central and western divisions reaching from Buyeo to Wusun, and in 177 he routed a Han army."),
    # ---------------- 西域与中亚 ----------------
    ("月氏", "月氏", "tribe", "#9BA16E", "秦汉之际居敦煌、祁连间，一度强于匈奴。前176 年前后为冒顿所破，大部西迁伊犁，称大月氏；余众入南山羌中，为小月氏。",
     "Yuezhi", "At the end of Qin the Yuezhi lived between Dunhuang and the Qilian Mountains and were once stronger than the Xiongnu. Around 176 BC Modu defeated them; most moved west to the Ili valley as the Great Yuezhi, while the rest went into the Qiang lands of the Southern Mountains as the Lesser Yuezhi."),
    ("大月氏", "大月氏", "tribe", "#9BA16E", "月氏西迁伊犁后，前130 年前后又为乌孙所逐，南下妫水（阿姆河），臣服大夏，都妫水北，后居蓝市城。张骞前128 年至此，欲结之共击匈奴，不得要领。分五翕侯，1 世纪贵霜翕侯统一诸部。",
     "Great Yuezhi", "After moving to the Ili valley the Yuezhi were driven out again by the Wusun around 130 BC and went south to the Oxus (Amu Darya), subduing Daxia (Bactria) and making their court north of the river, later at Lanshi. Zhang Qian reached them in 128 BC hoping to ally against the Xiongnu, without success. They were divided among five yabghus, and in the 1st century AD the Kushan yabghu united them."),
    ("塞种", "塞种", "tribe", "#A8A479", "居伊犁河、楚河流域的游牧部族（Saka）。前176 年前后为西迁的月氏所逐，南下葱岭，一部入罽宾。",
     "Saka", "Nomads of the Ili and Chu valleys. Driven out by the westward-moving Yuezhi around 176 BC, they went south over the Pamirs, some reaching Jibin."),
    ("乌孙", "乌孙", "tribe", "#7FA39A", "本与月氏同居敦煌、祁连间。昆莫猎骄靡长于匈奴，前130 年前后西击大月氏，据伊犁河谷，都赤谷城。武帝以细君、解忧公主和亲，前71 年与汉夹击匈奴；前53 年分大小昆弥，西域都护护之。",
     "Wusun", "The Wusun once lived beside the Yuezhi between Dunhuang and the Qilian Mountains. Their kunmo Liejiaomi, raised among the Xiongnu, attacked the Great Yuezhi around 130 BC and took the Ili valley, with his court at Chigu. Emperor Wu sent the princesses Xijun and Jieyou as brides; in 71 BC Wusun and Han attacked the Xiongnu together, and in 53 BC the realm was split between a greater and a lesser kunmi, both under the Protector-General."),
    ("大宛", "大宛", "state", "#B79778", "费尔干纳盆地的城郭之国，都贵山城，产汗血马。前104—前101 年李广利两伐大宛，立亲汉的昧蔡为王，西域震动。",
     "Dayuan (Ferghana)", "A city-state of the Ferghana basin with its capital at Guishan, famed for its 'blood-sweating' horses. Li Guangli's two campaigns of 104–101 BC installed the pro-Han Meicai as king and shook the Western Regions."),
    ("康居", "康居", "tribe", "#A88F7A", "锡尔河中下游与塔什干一带的游牧之国，冬居乐越匿地，夏居卑阗城。郅支单于曾西投康居，筑城都赖水。东汉时并有粟特诸城。",
     "Kangju", "A nomadic state of the middle and lower Syr Darya and the Tashkent region, wintering at Leyueni and summering at Beitian. The chanyu Zhizhi took refuge with Kangju and built his fortress on the Talas. In the Eastern Han Kangju also held the Sogdian cities."),
    ("大夏", "大夏", "state", "#B6A487", "阿姆河上游的巴克特里亚（希腊—巴克特里亚王国），城郭林立而兵弱，前130 年前后臣属西迁的大月氏。",
     "Daxia (Bactria)", "Bactria on the upper Oxus (the Greco-Bactrian kingdom), rich in walled towns but weak in arms; around 130 BC it fell under the Great Yuezhi."),
    ("安息", "安息", "state", "#9C8AA8", "帕提亚帝国，前247 年立国，东境达木鹿（马雷），地方数千里。前115 年前后汉使至安息，安息以大鸟卵及黎轩善眩人献汉。97 年班超遣甘英出使大秦，至安息西界条支海滨而还。",
     "Anxi (Parthia)", "The Parthian empire, founded in 247 BC, whose eastern frontier reached Merv (modern Mary); its land stretched thousands of li. Han envoys reached Parthia around 115 BC, and it sent Han ostrich eggs and conjurors from Lixuan. In AD 97 Ban Chao sent Gan Ying towards Da Qin; he reached the Parthian western frontier at the sea of Tiaozhi and turned back."),
    ("乌弋山离", "乌弋山离", "state", "#B39F8E", "今阿富汗南部、伊朗东部（锡斯坦、阿拉霍西亚）的国家，《汉书》称其地暑热、出狮子犀牛，去长安万二千二百里；1 世纪归贵霜。",
     "Wuyishanli", "A state of southern Afghanistan and eastern Iran (Sistan and Arachosia) which the Han shu describes as hot, with lions and rhinoceroses, 12,200 li from Chang'an; it passed to the Kushans in the 1st century."),
    ("罽宾", "罽宾", "state", "#AE9AA6", "今喀布尔河流域至克什米尔一带，塞种南下所建之国。武帝以后屡杀汉使，成帝时汉绝之。1 世纪后半为贵霜所并。",
     "Jibin", "The lands from the Kabul valley to Kashmir, ruled by Saka who had come south. It repeatedly killed Han envoys after Emperor Wu's time and Han broke off relations under Emperor Cheng. It was absorbed by the Kushans in the later 1st century."),
    ("贵霜", "贵霜", "state", "#8F9AB0", "大月氏五翕侯之一，1 世纪前半丘就却统一五部，自立为王，南侵罽宾、高附，阎膏珍时兼有天竺西北。90 年遣副王谢率七万众越葱岭攻班超，粮尽而退。",
     "Kushan Empire", "One of the five Yuezhi yabghus. In the first half of the 1st century Kujula Kadphises united the five and made himself king, invading Jibin and Gaofu; under Vima Taktu (Yangaozhen) the Kushans also held north-western India. In AD 90 the viceroy Xie led 70,000 men over the Pamirs against Ban Chao but withdrew when supplies ran out."),
    ("西域诸国", "西域诸国", "tribe", "hm:西域诸国", "塔里木盆地周缘的城郭诸国，《汉书》称三十六国，后分至五十余国。汉初役属匈奴，匈奴设僮仆都尉；前60 年匈奴日逐王降汉，郑吉为西域都护，诸国内属。新莽时绝；东汉 74、91 年两度复置都护，107 年又罢，123 年后以西域长史领之。",
     "States of the Western Regions", "The walled oasis states around the Tarim Basin, thirty-six according to the Han shu and later over fifty. In early Han they were subject to the Xiongnu, who kept a Commandant of Slaves there; in 60 BC the Xiongnu Rizhu king surrendered to Han, Zheng Ji became Protector-General and the states submitted. They were lost under Wang Mang; the Eastern Han restored the Protector-General in 74 and 91, abolished the post again in 107 and from 123 governed through a Chief Clerk of the Western Regions."),
    ("北道诸国", "北道诸国（龟兹·焉耆）", "tribe", None, "塔里木盆地北缘的龟兹、姑墨、温宿、尉头、焉耆、尉犁诸国。龟兹王建为匈奴所立，「倚恃虏威，据有北道」；75 年焉耆、龟兹攻没都护陈睦。91 年龟兹、姑墨、温宿降班超，94 年班超斩焉耆王广，北道始平。图上 74、76、89 年单独画出，画作役属北匈奴，其余年份并入西域诸国。",
     "Northern-route states (Kucha and Karasahr)", "Kucha, Gumo, Wensu, Weitou, Karasahr and Yuli on the northern rim of the Tarim Basin. Jian, king of Kucha, had been set up by the Xiongnu and, 'relying on the barbarians' power, held the northern route'; in 75 Karasahr and Kucha attacked and killed the Protector-General Chen Mu. Kucha, Gumo and Wensu submitted to Ban Chao in 91, and in 94 Ban Chao beheaded Guang, king of Karasahr, and the northern route was finally pacified. The map draws them separately in 74, 76 and 89, as subject to the Northern Xiongnu; in other years they are part of the States of the Western Regions."),
    ("班超", "班超所据诸国", "tribe", None, "班超经营西域时据为根本的南道诸国。73 年班超以三十六人使鄯善、于阗，皆降；74 年至疏勒，执龟兹所立的疏勒王兜题，立故王兄子忠。76 年罢都护，班超奉诏东归，于阗王侯抱马脚号泣，超遂还疏勒，与疏勒、于阗坚守，以其兵攻姑墨（78）、破莎车（87），91 年为西域都护。图上 73、76、89 年单独画出，画作内属于汉（斜线）。",
     "States held by Ban Chao", "The southern-route states that were Ban Chao's base in the Western Regions. In 73 he went with thirty-six men to Shanshan and Khotan, and both submitted; in 74 he reached Kashgar, seized Douti, the king Kucha had imposed there, and set up Zhong, a nephew of the former king. When the Protectorate was abandoned in 76 Ban Chao was ordered home, but at Khotan the king and nobles clung weeping to his horse's legs, and he went back to Kashgar and held on there and in Khotan, using their troops against Gumo (78) and Yarkand (87); in 91 he became Protector-General. The map draws them separately in 73, 76 and 89, as submitting to Han (hatched)."),
    ("羌", "羌", "tribe", "hm:羌", "河湟与青海一带的部族，种落繁多，先零、烧当最强。汉置护羌校尉，屡有反叛；东汉 107—118、140—145、159—169 年羌乱迭起，凉州残破。",
     "Qiang tribes", "Peoples of the Yellow River and Huangshui valleys (Hehuang) and Qinghai, divided into many tribes of which the Xianlian and Shaodang were the strongest. Han appointed a Protector of the Qiang, but revolts were frequent; under the Eastern Han the Qiang wars of 107–118, 140–145 and 159–169 left Liang Province in ruins."),
    # ---------------- 南方 ----------------
    ("南越", "南越", "state", "#8FAE8C", "秦南海尉赵佗，秦亡后绝道自守，击并桂林、象郡，前204 年自立为南越武王，都番禺；前196 年受汉封，吕后时称帝，又攻并瓯雒。前112 年丞相吕嘉反汉，次年汉灭南越，置九郡。",
     "Nanyue", "Zhao Tuo, the Qin commandant of Nanhai, cut the roads after Qin fell and annexed Guilin and Xiang commanderies, making himself King Wu of Nanyue in 204 BC with his capital at Panyu. He accepted a Han title in 196 BC, proclaimed himself emperor under Empress Lü and annexed Âu Lạc. In 112 BC the chancellor Lü Jia rebelled against Han, and the next year Han destroyed Nanyue and set up nine commanderies."),
    ("瓯雒", "瓯雒", "state", "#9DB58A", "红河三角洲的安阳王之国（越南史称瓯雒国），前180 年前后为南越所并，置交趾、九真二郡守之。",
     "Âu Lạc", "The kingdom of King An Dương in the Red River delta, absorbed by Nanyue around 180 BC and governed as the commanderies of Jiaozhi and Jiuzhen."),
    ("闽越", "闽越", "state", "#89A88E", "越王勾践之后无诸，秦时废为君长；佐汉灭楚，前202 年封闽越王，都东冶。前138 年围东瓯，前135 年攻南越，屡与汉为敌；前110 年汉灭之，徙其民于江淮。",
     "Minyue", "Wuzhu, a descendant of King Goujian of Yue, was reduced to a chieftain under Qin; he helped Han destroy Chu and was made king of Minyue at Dongye in 202 BC. Minyue besieged Dong'ou in 138 BC and attacked Nanyue in 135 BC, repeatedly defying Han; Han destroyed it in 110 BC and moved its people to the Yangzi–Huai region."),
    ("东瓯", "东瓯", "state", "#95B59A", "无诸同族的摇，佐汉有功，前192 年封东海王，都东瓯（今温州），俗称东瓯王。前138 年为闽越所围，汉救之，东瓯举国四万余人内徙江淮。",
     "Dong'ou", "Yao, a kinsman of Wuzhu, was rewarded for helping Han and made king of Donghai at Dong'ou (modern Wenzhou) in 192 BC, commonly called the king of Dong'ou. Besieged by Minyue in 138 BC and relieved by Han, the whole kingdom of over forty thousand people moved inland to the Yangzi–Huai region."),
    ("夜郎", "夜郎", "state", "#9AAB78", "西南夷中最大的君长国，在今贵州西部。前135 年唐蒙通夜郎，置犍为郡；前111 年夜郎王入朝受印，以其地为牂柯郡。",
     "Yelang", "The largest of the southwestern chiefdoms, in western Guizhou. Tang Meng opened the route to Yelang in 135 BC and Qianwei Commandery was set up; in 111 BC the king of Yelang came to court and received a seal, and his land became Zangke Commandery."),
    ("滇", "滇", "state", "#A0AD80", "滇池一带的君长国，战国时楚将庄蹻入滇称王。前109 年汉兵临滇，滇王举国降，赐滇王之印，置益州郡。",
     "Dian", "A chiefdom around Lake Dian, where the Chu general Zhuang Qiao had made himself king in the Warring States period. When Han troops arrived in 109 BC the king of Dian surrendered his whole kingdom, received the seal of King of Dian, and Yizhou Commandery was set up."),
    ("邛都", "邛都", "state", "#A4A27E", "安宁河谷的君长国，与筰都并称邛筰。前111 年置越嶲郡。",
     "Qiongdu", "A chiefdom of the Anning valley, named together with Zuodu as Qiong–Zuo. Yuexi Commandery was set up there in 111 BC."),
    ("哀牢", "哀牢", "state", "#93A882", "澜沧江以西的部族国家，东汉 51 年一部内附，69 年哀牢王柳貌率众内属，置永昌郡，汉地西至伊洛瓦底江。",
     "Ailao", "A tribal state west of the Mekong. Part of it submitted to Han in AD 51, and in 69 King Liumao of Ailao brought his people in; Yongchang Commandery was set up, carrying Han territory west to the Irrawaddy."),
    ("西南夷", "西南夷", "tribe", "#A7A485", "巴蜀以南、以西的众多部族：冉駹、筰都、白马、昆明、嶲、靡莫等，大者为君长国，小者随畜迁徙。武帝时陆续置郡，昆明诸部屡阻通身毒之道。",
     "Southwestern peoples", "The many peoples south and west of Ba and Shu — the Ranmang, Zuodu, Baima, Kunming, Xi, Mimo and others — some organised as chiefdoms, others herders on the move. Emperor Wu brought them under commanderies one by one, though the Kunming tribes repeatedly blocked the route to India."),
    # ---------------- 东北 ----------------
    ("朝鲜", "朝鲜", "state", "#9A9ABF", "秦汉之际为箕氏朝鲜（王否、王准）。前194 年燕人卫满率众东渡浿水，逐准王，都王险城，役属真番、临屯，是为卫氏朝鲜。前109 年汉遣杨仆、荀彘水陆并进，次年王险城降，置乐浪、真番、临屯、玄菟四郡。",
     "Joseon", "At the end of Qin, Joseon was ruled by the Gija line (kings Bu and Jun). In 194 BC Wiman of Yan crossed the Pae River with his followers, drove out King Jun and ruled from Wangxian, making Zhenfan and Lintun his dependencies: this was Wiman Joseon. Han sent Yang Pu and Xun Zhi by sea and land in 109 BC; Wangxian surrendered the next year and the four commanderies of Lelang, Zhenfan, Lintun and Xuantu were set up."),
    ("濊貊", "濊貊", "tribe", "#8E96B0", "东北亚的濊、貊诸部，分布于鸭绿江、浑江流域至朝鲜半岛东部。前128 年濊君南闾降汉，置苍海郡，二年而罢。",
     "Ye-Maek", "The Ye and Maek peoples of north-east Asia, from the Yalu and Hun valleys to the east of the Korean peninsula. In 128 BC the Ye chief Namnyeo submitted to Han and Canghai Commandery was set up, abolished two years later."),
    ("沃沮", "沃沮", "tribe", "#97A0B5", "朝鲜半岛东北的部族，汉初属卫氏朝鲜，汉武帝以后属玄菟、乐浪；30 年罢东部都尉后自立，旋臣属高句丽。",
     "Okjeo", "A people of the north-east of the Korean peninsula, subject first to Wiman Joseon and after Emperor Wu to Xuantu and Lelang; after the Eastern Commandant was abolished in AD 30 they became independent but were soon subject to Goguryeo."),
    ("夫余", "夫余", "tribe", "hm:夫余", "松嫩平原的农牧之国，都今吉林市一带，与汉亲善，东汉时屡遣使朝贡。",
     "Buyeo", "A farming and herding state of the Songnen plain with its capital near modern Jilin City, friendly to Han; it sent envoys to the Eastern Han court many times."),
    ("高句丽", "高句丽", "tribe", "hm:高句丽", "前37 年朱蒙于卒本（今桓仁）立国，3 年迁都国内城（今集安）。王莽时改称下句丽；东汉时屡寇辽东、玄菟。",
     "Goguryeo", "Founded at Jolbon (Huanren) by Jumong in 37 BC, Goguryeo moved its capital to Gungnae (Ji'an) in AD 3. Wang Mang renamed it Xia-Gouli; under the Eastern Han it repeatedly raided Liaodong and Xuantu."),
    ("辰国", "辰国（三韩）", "tribe", "#9FA2C0", "朝鲜半岛南部诸部，汉初称辰国，准王南奔后称韩王；东汉时分为马韩、辰韩、弁韩，共七十八国，以马韩为大。",
     "Jin (Samhan)", "The peoples of the southern Korean peninsula, called Jin in early Han; King Jun, fleeing south, styled himself King of Han (韓) there. Under the Eastern Han they formed the Mahan, Jinhan and Byeonhan — seventy-eight small states, Mahan the largest."),
]

# 王国（二级单位）的说明：键 → (说明, 英文说明)。郡的说明由 src/build.py 写治所
KINGDOM_NOTE = {
    "楚国": ("汉初韩信为楚王，前201 年废，分淮西为楚国（刘交，都彭城）、淮东为荆国。前154 年被削东海郡，楚王遂参与七国之乱；乱后只领彭城一郡之地。",
             "Han Xin was king of Chu in early Han until deposed in 201 BC; west of the Huai became Chu under Liu Jiao (capital Pengcheng) and east of it Jing. Stripped of Donghai in 154 BC, its king joined the Rebellion of the Seven States; afterwards it held only the area of Pengcheng."),
    "荆国": ("前201 年以淮东五十余城封刘贾为荆王，都吴；前196 年刘贾为英布所杀，国除，前195 年改封刘濞为吴王。", "Liu Jia was made king of Jing in 201 BC with over fifty towns east of the Huai, ruling from Wu; he was killed by Ying Bu in 196 BC and the kingdom was refounded as Wu under Liu Bi in 195 BC."),
    "吴国": ("刘濞为吴王，都广陵，煮海为盐、即山铸钱，富甲诸侯；前154 年首倡七国之乱，兵败国除。", "Liu Bi, king of Wu, ruled from Guangling, boiling sea water for salt and minting coin from the copper of its hills, the richest of the kings; he led the Rebellion of the Seven States in 154 BC and his kingdom was abolished after his defeat."),
    "江都国": ("七国之乱后以故吴地封刘非为江都王，都广陵；前121 年刘建谋反国除，前117 年改置广陵国。", "After the Rebellion of the Seven States the old Wu lands were given to Liu Fei as king of Jiangdu at Guangling; his son Liu Jian plotted rebellion and the kingdom was abolished in 121 BC, and in 117 BC the Kingdom of Guangling was set up in its place."),
    "齐国": ("汉初齐国（刘肥）领七十余城，为诸侯王之最大者；后屡被分割，前164 年分为六国，前127 年齐王刘次昌自杀国除。", "The early Han kingdom of Qi under Liu Fei held more than seventy towns, the largest of all; it was repeatedly divided, into six kingdoms in 164 BC, and abolished when its king Liu Cichang killed himself in 127 BC."),
    "赵国": ("汉初赵国领邯郸、巨鹿、常山、清河诸郡，张耳、张敖后为刘如意、刘友等；七国之乱后国除，前152 年复置，地渐小。", "Early Han Zhao held Handan, Julu, Changshan and Qinghe under Zhang Er and Zhang Ao and then Liu Ruyi, Liu You and others; abolished after the Rebellion of the Seven States, it was restored in 152 BC on a smaller scale."),
    "燕国": ("汉初燕国领广阳、上谷至辽东诸郡；臧荼、卢绾后为刘建、刘泽等，前128 年国除，前117 年刘旦复封，前80 年谋反国除。", "Early Han Yan held the commanderies from Guangyang and Shanggu to Liaodong under Zang Tu and Lu Wan and then Liu Jian, Liu Ze and others; abolished in 128 BC, it was refounded for Liu Dan in 117 BC and abolished again after his plot of 80 BC."),
    "代国": ("前196 年封刘恒为代王，都中都，后为文帝；领代、雁门、太原等郡，前114 年代王刘义徙清河，代国除。", "Liu Heng, later Emperor Wen, was made king of Dai in 196 BC with his capital at Zhongdu; Dai held Dai, Yanmen and Taiyuan commanderies until its king Liu Yi was moved to Qinghe in 114 BC and the kingdom was abolished."),
    "梁国": ("彭越为梁王，都定陶；前196 年被诛，改封刘恢。文帝子梁孝王刘武领四十余城，七国之乱中坚守睢阳；前144 年分梁为五国。", "Peng Yue was king of Liang at Dingtao until executed in 196 BC; Liu Hui replaced him. Liu Wu, Emperor Wen's son, held over forty towns as King Xiao of Liang and held Suiyang during the Rebellion of the Seven States; in 144 BC Liang was split into five."),
    "淮南国": ("英布为淮南王，前196 年反，次年兵败被杀，改封刘长；刘长前174 年谋反废死。前164 年三分淮南，刘安为淮南王，前122 年谋反国除。", "Ying Bu was king of Huainan until his revolt in 196 BC (he was killed the following year), then Liu Chang, who was deposed for plotting in 174 BC. In 164 BC Huainan was split in three, Liu An becoming king of Huainan; he was found plotting in 122 BC and the kingdom was abolished."),
    "长沙国": ("吴芮为长沙王，是汉初唯一存续的异姓王国，传五世至前157 年无后国除；前155 年景帝封子刘发为长沙王。", "Wu Rui's Changsha was the only kingdom under a king outside the imperial Liu clan to survive early Han, lasting five generations until it died out in 157 BC; in 155 BC Emperor Jing made his son Liu Fa king of Changsha."),
    "韩国": ("韩王信（韩襄王孙）随汉定韩地，前205 年立为韩王，都阳翟；前201 年徙太原，都马邑，同年降匈奴。", "Han Xin, a grandson of King Xiang of Han (韓) and not the general of the same name, won back the Han (韓) lands for Liu Bang and was made king of Han (韓) at Yangdi in 205 BC; moved to Taiyuan with his capital at Mayi in 201 BC, he went over to the Xiongnu the same year."),
    "淮阳国": ("汉初以颍川、淮阳封刘友，后屡废屡置；宣帝时以陈为淮阳国。", "First given to Liu You with Yingchuan and Huaiyang in early Han, the kingdom was repeatedly abolished and restored; under Emperor Xuan it was re-established around Chen."),
    "琅邪国": ("吕后割齐之琅邪封刘泽为琅邪王；前179 年刘泽徙燕，地还齐。", "Empress Lü carved Langya out of Qi for Liu Ze; in 179 BC he was moved to Yan and the land went back to Qi."),
    "济北国": ("前164 年齐分出的王国之一，领泰山以北之地。", "One of the kingdoms carved out of Qi in 164 BC, holding the land north of Mount Tai."),
    "济南国": ("前164 年齐分出的王国之一，济南王刘辟光参与七国之乱，国除为郡。", "One of the kingdoms carved out of Qi in 164 BC; its king Liu Piguang joined the Rebellion of the Seven States and it became a commandery."),
    "胶西国": ("前164 年齐分出的王国，七国之乱中胶西王刘卬为首谋之一，兵败自杀；后封刘端，前108 年国除。", "Carved out of Qi in 164 BC; its king Liu Ang was among the leaders of the Rebellion of the Seven States and killed himself after defeat; Liu Duan then held it until it was abolished in 108 BC."),
    "衡山国": ("前164 年淮南三分之一，刘勃、刘赐先后为王；前122 年刘赐谋反国除。", "One of the three parts of Huainan from 164 BC, ruled by Liu Bo and then Liu Ci; abolished when Liu Ci was found plotting in 122 BC."),
    "庐江国": ("前164 年淮南三分之一，刘赐为王，前153 年徙衡山，国除为郡。", "One of the three parts of Huainan from 164 BC under Liu Ci, who was moved to Hengshan in 153 BC, the kingdom becoming a commandery."),
    "济东国": ("前144 年梁分为五之一，以东平之地封刘彭离；前116 年国除。", "One of the five parts of Liang from 144 BC, the area of Dongping given to Liu Pengli; abolished in 116 BC."),
    "常山国": ("前145 年封刘舜为常山王，前114 年国除，分其地为真定国与常山郡。", "Liu Shun was made king of Changshan in 145 BC; in 114 BC the kingdom was abolished and split into the Kingdom of Zhending and Changshan Commandery."),
}

# 部族的分部：单位 → 所属部族（节点的 polmap 未另写时用这里）
SUB = {"单于本部": "匈奴", "左贤王": "匈奴", "右贤王": "匈奴", "浑邪王": "匈奴", "休屠王": "匈奴", "楼烦白羊": "匈奴", "南边八部": "匈奴",
       "北单于本部": "北匈奴", "呼衍王": "北匈奴"}

PALETTE = ["#6B8DAA", "#7E9A6A", "#B5675A", "#8C7DB3", "#D8BC8F", "#8A7298", "#9C8BC0", "#86A8CC", "#B9A65C", "#70B3AA",
           "#A8A86A", "#B091BF", "#CCAAD0", "#A0756A", "#A0C29C", "#87C2D3", "#C3B888", "#ACB4E1", "#C1946F", "#95C4A7",
           "#DDA99A", "#8CC5B3", "#D3A8C7", "#8985B8", "#5C9B83", "#D4B08B"]


def units():
    return [dict(k=k, n=n, kind=kind, col=col, note=note, ne=ne, notee=notee) for k, n, kind, col, note, ne, notee in _P]


def dark(hx):
    r, g, b = int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16)
    f = lambda v, k: max(0, min(255, int(round(v * k))))
    return "#%02X%02X%02X" % (f(r, 1.13), f(g, 1.11), f(b, 1.07))


def colors(U, adj, zg, hm):
    """zg / hm：邻卷的 {键: [浅, 深]}。郡国按邻接关系贪心取色（与相邻的、与所属政权的颜色都不同）"""
    light = [None] * len(U)
    fixed = {}                            # 承自邻卷的：浅、深两色都照搬（衔接规则：同键同色）
    for i, u in enumerate(U):
        c = u.get("col")
        if c and c.startswith("zg:"):
            light[i], fixed[i] = zg[c[3:]][0], zg[c[3:]][1]
        elif c and c.startswith("hm:"):
            light[i], fixed[i] = hm[c[3:]][0], hm[c[3:]][1]
        elif c:
            light[i] = c
    order = sorted([i for i in range(len(U)) if light[i] is None], key=lambda i: -len(adj.get(i, ())))
    use = {c: 0 for c in PALETTE}
    for i in order:
        bad = {light[j] for j in adj.get(i, ()) if light[j]}
        cand = [c for c in PALETTE if c not in bad] or PALETTE
        c = min(cand, key=lambda c: (use[c], PALETTE.index(c)))
        light[i] = c
        use[c] += 1
    return dict(light=light, dark=[fixed.get(i) or dark(c) for i, c in enumerate(light)])


# 郡的说明（得名、建郡年代）：接在「治某」之后。(中文, 英文)
JUN_NOTE = {
    "朔方郡": ("前127 年卫青收河南地后，用主父偃之议置，募民十万口徙之，筑朔方城。郡名取《诗·小雅·出车》「天子命我，城彼朔方」。",
            "Set up on Zhufu Yan's advice after Wei Qing recovered the Ordos in 127 BC; a hundred thousand settlers were recruited for it and the city "
            "of Shuofang was built. The name comes from 'Chu che' in the Odes: 'The Son of Heaven bade me wall the north (shuofang).'"),
    "五原郡": ("前127 年卫青收河南地后，以秦九原郡故地置，与朔方郡同时。",
            "Set up on the old ground of Qin's Jiuyuan Commandery after Wei Qing recovered the Ordos in 127 BC, at the same time as Shuofang."),
    "酒泉郡": ("郡名得于「其水若酒」（应劭注《汉书·地理志》），后世又有霍去病倾御酒入泉、与将士共饮的传说。故匈奴浑邪王地。建郡年份《汉书》"
            "有二说：〈武帝纪〉在元狩二年（前121），〈地理志〉在太初元年（前104），今人考证多以为晚于〈武帝纪〉所记。图上从前121 年起画，"
            "张掖、敦煌分出以前，河西走廊西部都画作酒泉郡。",
            "Named, according to Ying Shao's note on the treatise on geography in the Hanshu, because 'its water is like wine (jiu)'; a later legend "
            "has Huo Qubing pouring the emperor's gift of wine into the spring to share it with his men. Formerly the land of the Hunye king. The "
            "Hanshu gives two dates: 121 BC in the Annals of Emperor Wu and 104 BC in the treatise on geography, and modern scholars mostly think "
            "it came later than the Annals say. The map shows it from 121 BC, with the western Hexi Corridor drawn as Jiuquan until Zhangye and "
            "Dunhuang were split off."),
    "张掖郡": ("「张国臂掖，故曰张掖」（应劭注），取伸张汉之臂腋、断匈奴右臂之意。故匈奴浑邪王地。〈武帝纪〉元鼎六年（前111）分置，"
            "〈地理志〉作太初元年（前104）；图上取前111 年。",
            "'It stretches out the arm and armpit of the state, hence Zhangye' (Ying Shao): it extended Han's reach and cut off the Xiongnu's "
            "right arm. Formerly the land of the Hunye king. Split off in 111 BC according to the Annals of Emperor Wu, in 104 BC according to the "
            "treatise on geography; the map uses 111 BC."),
    "敦煌郡": ("「敦，大也；煌，盛也」（应劭注）。〈武帝纪〉元鼎六年（前111）分置，〈地理志〉作后元元年（前88）分酒泉置；图上取前111 年。"
            "西有玉门关、阳关，是通西域的门户。",
            "'Dun means great, huang means flourishing' (Ying Shao). Split off in 111 BC according to the Annals of Emperor Wu, or from Jiuquan in "
            "88 BC according to the treatise on geography; the map uses 111 BC. The Yumen and Yang passes to its west were the gateways to the "
            "Western Regions."),
    "武威郡": ("郡名一般释为彰显汉之武功军威。故匈奴休屠王地，霍去病所获休屠王祭天金人即出此地。〈武帝纪〉以为元狩二年（前121）与酒泉同置，"
            "〈地理志〉作太初四年（前101），今人或以为迟至昭宣之际；图上从太初年间（前102）起画，此前画在张掖郡（更早是酒泉郡）内。",
            "The name is usually explained as displaying Han's martial might. Formerly the land of the Xiutu king, whose golden statue for "
            "worshipping Heaven Huo Qubing captured. The Annals of Emperor Wu have it set up together with Jiuquan in 121 BC, the treatise on "
            "geography in 101 BC, and some modern scholars put it as late as the reigns of Emperors Zhao and Xuan; the map shows it from the Taichu "
            "years (102 BC), and before that as part of Zhangye (earlier, Jiuquan)."),
    "金城郡": ("前81 年分天水、陇西、张掖郡置。郡名一说初筑城时得金，一说取「金城汤池」坚固之意（《汉书·地理志》注引应劭、臣瓒）。",
            "Formed in 81 BC from parts of Tianshui, Longxi and Zhangye. The name is explained either as gold having been found when the walls were "
            "first built or as meaning 'a city of metal', impregnable (Ying Shao and Chen Zan, in the notes to the treatise on geography)."),
}
