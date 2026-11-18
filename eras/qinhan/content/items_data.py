# -*- coding: utf-8 -*-
"""条目数据。年份为纪年年（公元前记负数），月可空。"""

# (名, 英文名, 政权, 经, 纬, [(起, 止) 或 (起年, 月, 止年, 月)], 今地, 英文今地, 说明, 英文说明)
CAPITALS = [
    ("咸阳", "Xianyang", "秦", 108.72, 34.37, [(-212, -207)], "陕西咸阳东", "east of Xianyang, Shaanxi",
     "秦都。始皇徙天下豪富十二万户于咸阳，渭南营阿房宫；前206 年为项羽所焚。", "The Qin capital. The First Emperor moved 120,000 wealthy households here and began the Epang Palace south of the Wei; Xiang Yu burned it in 206 BC."),
    ("陈", "Chen", "张楚", 114.88, 33.73, [(-209, 7, -208, 12)], "河南淮阳", "Huaiyang, Henan", "陈胜张楚之都。", "Capital of Chen Sheng's Zhang Chu."),
    ("彭城", "Pengcheng", "西楚", 117.18, 34.27, [(-208, 9, -202, 12)], "江苏徐州", "Xuzhou, Jiangsu",
     "前208 年楚怀王徙都于此；前206 年为西楚霸王项羽之都。", "King Huai of Chu moved his court here in 208 BC; from 206 BC it was the capital of Xiang Yu, Hegemon-King of Western Chu."),
    ("南郑", "Nanzheng", "汉", 107.03, 33.07, [(-206, 2, -205, 11)], "陕西汉中", "Hanzhong, Shaanxi", "汉王刘邦初都。", "First capital of Liu Bang as king of Han."),
    ("栎阳", "Yueyang", "汉", 109.23, 34.68, [(-205, 11, -200, 2)], "陕西西安阎良区", "Yanliang District, Xi'an, Shaanxi",
     "秦献公旧都。汉王还定三秦后都此，前200 年长乐宫成，徙都长安。", "The old capital of Duke Xian of Qin. The king of Han made it his capital after retaking the Three Qins, moving to Chang'an when the Changle Palace was finished in 200 BC."),
    ("长安", "Chang'an", "汉", 108.88, 34.31, [(-200, 2, 8, 12)], "陕西西安西北（汉长安城）", "northwest of Xi'an, Shaanxi (Han Chang'an city)",
     "西汉都城。萧何营未央宫，惠帝筑城，城周六十余里；武帝起建章宫、凿昆明池。", "The Western Han capital. Xiao He built the Weiyang Palace and Emperor Hui the walls, over sixty li round; Emperor Wu added the Jianzhang Palace and dug the Kunming Pool."),
    ("常安", "Chang'an (Xin)", "新", 108.88, 34.31, [(9, 23)], "陕西西安西北", "northwest of Xi'an, Shaanxi", "王莽改长安为常安，为新都。", "Wang Mang changed the first character of Chang'an's name (长 to 常; the sound is unchanged) and made it the Xin capital."),
    ("洛阳", "Luoyang", "汉", 112.63, 34.72, [(25, 184)], "河南洛阳东（汉魏洛阳故城）", "east of Luoyang, Henan (Han–Wei city site)",
     "25 年光武定都于此，是为东汉；城南北九里、东西六里，号「九六城」。", "Emperor Guangwu made it his capital in 25, founding the Eastern Han; the city, nine li north to south and six east to west, was nicknamed the 'nine-six city'."),
    ("临淄", "Linzi", "齐", 118.3, 36.87, [(-209, 9, -203, 11)], "山东淄博临淄区", "Linzi District, Zibo, Shandong", "田齐故都，秦末诸田复国都此。", "The old Tian Qi capital, where the Tian family re-established Qi at the end of Qin."),
    ("信都（襄国）", "Xindu (Xiangguo)", "赵", 114.5, 37.07, [(-208, 1, -204, 10)], "河北邢台", "Xingtai, Hebei", "赵歇所都；项羽改名襄国，封张耳为常山王都此。", "Zhao Xie's capital; Xiang Yu renamed it Xiangguo and gave it to Zhang Er as king of Changshan."),
    ("蓟", "Ji", "燕", 116.35, 39.9, [(-209, 9, -202, 9)], "北京西南", "southwest Beijing", "燕国故都。", "The old Yan capital."),
    ("番禺", "Panyu", "南越", 113.27, 23.13, [(-204, -112)], "广东广州", "Guangzhou, Guangdong",
     "秦南海郡治，赵佗南越国都。1983 年发现南越王墓（文帝赵眜）。", "Seat of Qin's Nanhai Commandery and capital of Zhao Tuo's Nanyue; the tomb of Zhao Mo, Emperor Wen of Nanyue, was found in 1983."),
    ("东冶", "Dongye", "闽越", 119.3, 26.08, [(-202, 2, -111, 9)], "福建福州", "Fuzhou, Fujian", "闽越王无诸都城。", "Capital of Wuzhu, king of Minyue."),
    ("东瓯", "Dong'ou", "东瓯", 120.65, 28.0, [(-192, -138)], "浙江温州", "Wenzhou, Zhejiang", "东海王摇都城，俗称东瓯。", "Capital of Yao, king of Donghai, commonly called Dong'ou."),
    ("王险城", "Wangxian", "朝鲜", 125.75, 39.02, [(-194, -108)], "朝鲜平壤一带", "Pyongyang area, North Korea",
     "卫氏朝鲜都城；汉置乐浪郡朝鲜县。", "Capital of Wiman Joseon; under Han, Chaoxian County of Lelang Commandery."),
    ("单于庭", "The chanyu's court", "匈奴", 102.6, 47.3, [(-212, 48)], "蒙古国杭爱山东麓（大致）", "eastern foot of the Khangai Mountains, Mongolia (approx.)",
     "匈奴单于王庭，随水草迁徙；龙城为其大会祭天之所。", "The chanyu's moving court, following water and pasture; Longcheng was where the tribes gathered to sacrifice to Heaven."),
    ("赤谷城", "Chigu", "乌孙", 78.4, 42.2, [(-130, 184)], "吉尔吉斯斯坦伊塞克湖东南", "southeast of Lake Issyk-Kul, Kyrgyzstan", "乌孙昆莫（昆弥）治所。", "Seat of the Wusun kunmo (kunmi)."),
    ("贵山城", "Guishan", "大宛", 71.6, 40.5, [(-212, 184)], "费尔干纳盆地西部（地望有争议）", "western Ferghana basin (location disputed)", "大宛王治所。", "Seat of the king of Dayuan (Ferghana)."),
    ("蓝市城", "Lanshi", "大月氏", 66.9, 36.75, [(-130, 40)], "阿富汗巴尔赫", "Balkh, Afghanistan", "大夏都城，大月氏南迁后以为都。", "Capital of Daxia (Bactria); the Great Yuezhi made it their capital after moving south."),
    ("成都", "Chengdu", "成家", 104.06, 30.66, [(25, 36)], "四川成都", "Chengdu, Sichuan", "公孙述成家之都。", "Capital of Gongsun Shu's Chengjia."),
    ("睢阳", "Suiyang", "刘永", 115.65, 34.42, [(25, 27)], "河南商丘南", "south of Shangqiu, Henan", "梁王刘永称帝于此。", "Where Liu Yong, king of Liang, proclaimed himself emperor."),
    ("冀", "Ji", "隗嚣", 105.35, 34.73, [(23, 33)], "甘肃甘谷东", "east of Gangu, Gansu", "隗嚣据陇右的治所。", "Wei Xiao's seat while he held Longyou."),
]

# (名, 英文名, 经, 纬, 年, 月, 胜负, 英文, 主将, 英文, 今地, 英文今地, 说明, 英文说明)
BATTLES = [
    ("戏之战", "Battle of Xi", 109.3, 34.4, -209, 9, "秦 胜 张楚", "Qin defeated Zhang Chu", "章邯 vs 周文", "Zhang Han vs. Zhou Wen",
     "陕西西安临潼区东", "east of Lintong District, Xi'an, Shaanxi", "周文率数十万众入关至戏，章邯以骊山徒击退之。", "Zhou Wen came through the passes to Xi with hundreds of thousands; Zhang Han drove him back with the Lishan labourers."),
    ("临济之战", "Battle of Linji", 114.35, 35.05, -208, 6, "秦 胜 魏·齐", "Qin defeated Wei and Qi", "章邯 vs 魏咎、田儋", "Zhang Han vs. Wei Jiu and Tian Dan",
     "河南封丘东", "east of Fengqiu, Henan", "章邯围临济，夜衔枚击破齐楚救兵，田儋战死，魏咎自焚。", "Zhang Han besieged Linji and broke the Qi–Chu relief army in a night attack; Tian Dan was killed and Wei Jiu burned himself to death."),
    ("定陶之战", "Battle of Dingtao", 115.55, 35.07, -208, 9, "秦 胜 楚", "Qin defeated Chu", "章邯 vs 项梁", "Zhang Han vs. Xiang Liang",
     "山东菏泽定陶区", "Dingtao District, Heze, Shandong", "项梁屡胜而骄，章邯得增援夜袭，项梁战死。", "Xiang Liang grew proud after many victories; Zhang Han, reinforced, attacked by night and killed him."),
    ("巨鹿之战", "Battle of Julu", 115.0, 37.2, -207, 12, "楚 胜 秦", "Chu defeated Qin", "项羽 vs 王离、章邯", "Xiang Yu vs. Wang Li and Zhang Han",
     "河北平乡西南", "southwest of Pingxiang, Hebei", "项羽破釜沉舟，九战绝甬道，虏王离，秦军主力瓦解。", "Xiang Yu sank his boats and broke his pots, cut the Qin supply road in nine battles and captured Wang Li; the main Qin army fell apart."),
    ("新安坑卒", "Massacre at Xin'an", 112.15, 34.73, -206, 11, "楚 坑 秦降卒", "Chu massacred the surrendered Qin troops", "项羽", "Xiang Yu",
     "河南新安", "Xin'an, Henan", "项羽恐秦降卒入关生变，夜击坑二十余万人于新安城南。", "Fearing the surrendered Qin troops would rise once inside the passes, Xiang Yu had more than 200,000 of them killed and buried south of Xin'an by night."),
    ("峣关之战", "Battle of the Yao Pass", 109.3, 34.12, -207, 9, "沛公 胜 秦", "The Lord of Pei defeated Qin", "刘邦 vs 秦将", "Liu Bang vs. Qin generals",
     "陕西蓝田东南", "southeast of Lantian, Shaanxi", "刘邦用张良计，以利诱秦将、绕关袭击，大破秦军于蓝田。", "On Zhang Liang's advice Liu Bang bribed the Qin generals, went round the pass and routed the Qin army at Lantian."),
    ("陈仓之战", "Battle of Chencang", 107.37, 34.37, -206, 8, "汉 胜 雍", "Han defeated Yong", "刘邦、韩信 vs 章邯", "Liu Bang and Han Xin vs. Zhang Han",
     "陕西宝鸡东", "east of Baoji, Shaanxi", "汉军出故道袭雍，章邯败退废丘，是为「暗度陈仓」。", "The Han army came out by the Old Road and fell on Yong; Zhang Han retreated to Feiqiu — 'crossing secretly at Chencang'."),
    ("彭城之战", "Battle of Pengcheng", 117.18, 34.27, -205, 4, "楚 胜 汉", "Chu defeated Han", "项羽 vs 刘邦", "Xiang Yu vs. Liu Bang",
     "江苏徐州", "Xuzhou, Jiangsu", "汉军五十六万入彭城置酒高会，项羽以精兵三万晨袭，汉卒十余万人皆入睢水，睢水为之不流。", "The 560,000-strong Han army feasted in Pengcheng; Xiang Yu struck at dawn with 30,000 picked troops, and more than 100,000 Han soldiers went into the Sui, so that the river stopped flowing."),
    ("京索之战", "Battle of Jing and Suo", 113.4, 34.75, -205, 5, "汉 胜 楚", "Han defeated Chu", "灌婴 vs 楚骑", "Guan Ying vs. Chu cavalry",
     "河南荥阳东南", "southeast of Xingyang, Henan", "汉以灌婴为骑将，破楚骑于京、索之间，楚不能过荥阳而西。", "Han made Guan Ying its cavalry commander, and he beat the Chu horse between Jing and Suo, and Chu could not get past Xingyang to the west."),
    ("安邑之战", "Battle of Anyi", 111.18, 35.12, -205, 9, "汉 胜 西魏", "Han defeated Western Wei", "韩信 vs 魏豹", "Han Xin vs. Wei Bao",
     "山西夏县", "Xia County, Shanxi", "韩信疑兵临晋，以木罂缻自夏阳渡河袭安邑，虏魏豹。", "Han Xin feinted at Linjin, crossed at Xiayang on wooden jars, fell on Anyi and captured Wei Bao."),
    ("井陉之战", "Battle of Jingxing", 114.05, 38.03, -204, 10, "汉 胜 赵", "Han defeated Zhao", "韩信、张耳 vs 陈余", "Han Xin and Zhang Er vs. Chen Yu",
     "河北井陉东", "east of Jingxing, Hebei", "韩信背水列阵，伏兵拔赵壁立汉帜，斩陈余于泜水，擒赵歇。", "Han Xin drew up with his back to the river while hidden troops seized the Zhao camp and raised Han flags; Chen Yu was beheaded on the Zhi and Zhao Xie captured."),
    ("成皋之战", "Battle of Chenggao", 113.2, 34.82, -203, 10, "汉 胜 楚", "Han defeated Chu", "刘邦 vs 曹咎", "Liu Bang vs. Cao Jiu",
     "河南荥阳汜水镇", "Sishui, Xingyang, Henan", "楚大司马曹咎被激出战，半渡汜水为汉所击，自刭；汉复取成皋，据敖仓。", "Goaded into battle, the Chu Grand Marshal Cao Jiu was caught half across the Si River and cut his own throat; Han retook Chenggao and the Ao granary."),
    ("潍水之战", "Battle of the Wei River", 119.35, 36.5, -203, 11, "汉 胜 楚·齐", "Han defeated Chu and Qi", "韩信 vs 龙且", "Han Xin vs. Long Ju",
     "山东潍坊、高密之间", "between Weifang and Gaomi, Shandong", "韩信囊沙壅水，佯败诱龙且渡河，决水击之，斩龙且。", "Han Xin dammed the river with sandbags, feigned defeat to lure Long Ju across, then released the water and beheaded him."),
    ("固陵之战", "Battle of Guling", 114.85, 33.98, -202, 10, "楚 胜 汉", "Chu defeated Han", "项羽 vs 刘邦", "Xiang Yu vs. Liu Bang",
     "河南太康南", "south of Taikang, Henan", "汉王背约追楚，韩信、彭越未至，为项羽所败。", "The king of Han broke the truce to pursue Chu, but Han Xin and Peng Yue did not arrive and he was beaten by Xiang Yu."),
    ("垓下之战", "Battle of Gaixia", 117.55, 33.55, -202, 12, "汉 胜 楚", "Han defeated Chu", "韩信、刘邦 vs 项羽", "Han Xin and Liu Bang vs. Xiang Yu",
     "安徽灵璧东南", "southeast of Lingbi, Anhui", "诸侯合围，四面楚歌；项羽溃围南走，至乌江自刎。", "Surrounded by the allied armies and hearing the songs of Chu on every side, Xiang Yu broke out south and killed himself at Wujiang."),
    ("白登之围", "Siege of Baideng", 113.4, 40.15, -200, 10, "匈奴 围 汉", "The Xiongnu besieged Han", "冒顿 vs 高祖", "Modu vs. Gaozu",
     "山西大同东北", "northeast of Datong, Shanxi", "冒顿以精骑四十万围高祖于白登七日，陈平厚遗阏氏，乃解围一角得出。", "Modu surrounded Gaozu at Baideng with 400,000 picked horsemen for seven days; Chen Ping sent rich gifts to the chanyu's consort, one corner of the ring was opened and Gaozu got out."),
    ("睢阳之守", "Defence of Suiyang", 115.65, 34.42, -154, 2, "梁 守 吴楚", "Liang held out against Wu and Chu", "梁王刘武 vs 刘濞", "Liu Wu, king of Liang, vs. Liu Bi",
     "河南商丘南", "south of Shangqiu, Henan", "吴楚之兵猛攻梁国，梁王坚守睢阳，牵制叛军主力。", "Wu and Chu threw their armies at Liang, but its king held Suiyang and pinned down the rebels' main force."),
    ("下邑之战", "Battle of Xiayi", 116.25, 34.3, -154, 3, "汉 胜 吴楚", "Han defeated Wu and Chu", "周亚夫 vs 刘濞", "Zhou Yafu vs. Liu Bi",
     "安徽砀山东", "east of Dangshan, Anhui", "周亚夫坚壁昌邑，断吴楚粮道；吴楚饥疲北攻，大败于下邑。", "Zhou Yafu stayed behind his walls at Changyi and cut the Wu–Chu supply lines; hungry and exhausted, the rebels attacked north and were crushed at Xiayi."),
    ("龙城之战", "Battle of Longcheng", 113.8, 43.6, -129, 3, "汉 胜 匈奴", "Han defeated the Xiongnu", "卫青 vs 匈奴", "Wei Qing vs. the Xiongnu",
     "地望有争议（一说在今蒙古国境内）", "location disputed (some place it in today's Mongolia)",
     "卫青初次领兵：四将军各将万骑分出上谷、代、云中、雁门，卫青出上谷直捣匈奴大会祭天的龙城，斩首虏七百。公孙敖亡七千骑，李广兵败被俘、"
     "夺马逃归，公孙贺无功。这是汉主动出击匈奴的第一次胜利，卫青封关内侯。",
     "Wei Qing's first command. Four generals each led ten thousand horsemen out from Shanggu, Dai, Yunzhong and Yanmen; Wei Qing struck from "
     "Shanggu at Longcheng, where the Xiongnu tribes gathered to sacrifice to Heaven, and took seven hundred heads and prisoners. Gongsun Ao lost "
     "seven thousand men, Li Guang was beaten and captured and escaped on a stolen horse, and Gongsun He achieved nothing. It was Han's first "
     "victory on the offensive against the Xiongnu, and Wei Qing was made a Marquis Within the Passes."),
    ("雁门之战", "Battle beyond Yanmen", 112.7, 41.3, -128, 9, "汉 胜 匈奴", "Han defeated the Xiongnu", "卫青 vs 匈奴", "Wei Qing vs. the Xiongnu",
     "雁门塞外（大致，今内蒙古中南部）", "beyond the Yanmen frontier, south-central Inner Mongolia (approx.)",
     "元朔元年秋，匈奴二万骑入辽西、渔阳、雁门；卫青以车骑将军将三万骑出雁门，李息出代，斩首虏数千。卫青七次出击匈奴，这是第二次。",
     "In the autumn of Yuanshuo 1, after 20,000 Xiongnu horsemen had raided Liaoxi, Yuyang and Yanmen, Wei Qing, as General of Chariots and "
     "Cavalry, led 30,000 horsemen out of Yanmen while Li Xi set out from Dai; they took several thousand heads and prisoners. It was the second "
     "of Wei Qing's seven campaigns against the Xiongnu."),
    ("河南之战", "Battle for the Ordos", 107.6, 40.3, -127, 3, "汉 胜 匈奴", "Han defeated the Xiongnu", "卫青 vs 白羊王、楼烦王", "Wei Qing vs. the Baiyang and Loufan kings",
     "内蒙古河套", "Hetao, Inner Mongolia",
     "卫青、李息出云中，沿河西进至高阙，迂回南下至陇西，切断河南匈奴与单于庭的联系，走白羊、楼烦王，捕首虏数千、牛羊百余万，全甲兵而还，"
     "尽收河南地；卫青封长平侯。",
     "Wei Qing and Li Xi set out from Yunzhong, followed the river west to Gaoque and swung south to Longxi, cutting the Xiongnu of the Ordos off "
     "from the chanyu's court; they drove off the Baiyang and Loufan kings, took several thousand heads and prisoners and over a million cattle and "
     "sheep, and came home with the army intact, having recovered the whole Ordos. Wei Qing was made Marquis of Changping."),
    ("第一次漠南之战", "First battle south of the Gobi", 108.2, 42.8, -124, 2, "汉 胜 匈奴", "Han defeated the Xiongnu", "卫青 vs 右贤王", "Wei Qing vs. the Wise King of the Right",
     "内蒙古乌拉特中旗海流图以北、中蒙边境一带（大致）", "the Sino-Mongolian border north of Haliut, Urad Middle Banner, Inner Mongolia (approx.)",
     "卫青将三万骑出朔方高阙，北行六七百里，夜围右贤王庭。右贤王以为汉兵不能至，饮醉，惊起，与爱妾一人、壮骑数百溃围北去；汉得裨王十余人、"
     "众男女万五千余人、畜数千百万。武帝遣使就军中拜卫青为大将军。",
     "Wei Qing led 30,000 horsemen out from Gaoque in Shuofang and six or seven hundred li to the north surrounded the camp of the Wise King of the "
     "Right by night. The king, sure that no Han army could reach him, was drunk; he woke and broke out northward with one favourite concubine and a "
     "few hundred picked riders. Han took more than ten lesser kings, over 15,000 men and women and livestock running into the millions, and the "
     "emperor sent an envoy to appoint Wei Qing Grand General in the field."),
    ("第二次漠南之战", "Second battle south of the Gobi", 111.0, 42.6, -123, 4, "汉 胜 匈奴", "Han defeated the Xiongnu", "卫青、霍去病 vs 伊稚斜单于", "Wei Qing and Huo Qubing vs. the chanyu Yizhixie",
     "内蒙古阴山以北（大致）", "north of the Yin Mountains, Inner Mongolia (approx.)",
     "卫青二月、四月两出定襄，斩首虏万余。年十八的剽姚校尉霍去病以轻勇骑八百弃大军数百里赴利，斩首虏二千余，斩单于大父行籍若侯产，"
     "生擒季父罗姑比，以功冠诸军封冠军侯。前将军赵信、右将军苏建以三千余骑独遇单于，全军覆没，赵信降匈奴，苏建独身脱还。",
     "Wei Qing marched out of Dingxiang twice, in the 2nd and 4th months, taking over ten thousand heads and prisoners. Huo Qubing, an "
     "eighteen-year-old serving as Piaoyao Colonel, left the main army hundreds of li behind with eight hundred light horse, took over two thousand heads and "
     "prisoners, killed the chanyu's grand-uncle Chan, Marquis of Jiruo, and captured his uncle Luogubi alive; for outdoing the whole army he was made "
     "Marquis of Guanjun. The General of the Van, Zhao Xin, and the General of the Right, Su Jian, ran into the chanyu's army on their own with more than three thousand "
     "horse and lost them all: Zhao Xin went over to the Xiongnu and Su Jian escaped by himself."),
    ("河西之战", "Hexi campaign", 101.3, 38.1, -121, 6, "汉 胜 匈奴", "Han defeated the Xiongnu", "霍去病 vs 浑邪王、休屠王", "Huo Qubing vs. the Hunye and Xiutu kings",
     "甘肃山丹焉支山一带", "Mount Yanzhi, Shandan, Gansu",
     "春，霍去病将万骑出陇西，六日转战五王国，过焉支山千余里，鏖战皋兰山下，杀折兰王、卢胡王，执浑邪王子，收休屠王祭天金人，斩首虏八千余；"
     "夏，与公孙敖分道出北地，公孙敖失道，霍去病独逾居延，经小月氏至祁连山，斩首虏三万余。秋，浑邪王杀休屠王来降，河西归汉。",
     "In spring Huo Qubing led ten thousand horsemen out of Longxi, fought through five Xiongnu kingdoms in six days and pressed more than a "
     "thousand li past Mount Yanzhi; in a bloody close-quarters fight below Mount Gaolan he killed the Zhelan and Luhu kings, captured the Hunye "
     "king's son, took the Xiutu king's golden statue for worshipping Heaven and over 8,000 heads and prisoners. In summer he and Gongsun Ao set out "
     "from Beidi by separate roads; Gongsun Ao lost his way, and Huo Qubing went on alone past Juyan and through the Lesser Yuezhi lands to the "
     "Qilian Mountains, taking more than 30,000. In autumn the Hunye king killed the Xiutu king and surrendered, and Hexi passed to Han."),
    ("漠北之战", "Battle beyond the Gobi", 104.5, 46.5, -119, 6, "汉 胜 匈奴", "Han defeated the Xiongnu", "卫青、霍去病 vs 伊稚斜单于、左贤王", "Wei Qing and Huo Qubing vs. the chanyu Yizhixie and the Wise King of the Left",
     "蒙古国中部", "central Mongolia",
     "卫青出定襄千余里，遇单于陈兵以待，以武刚车环为营，纵五千骑往击；日暮大风扬沙，汉益纵左右翼绕单于，单于与壮骑数百溃围西北遁，"
     "汉军追至窴颜山赵信城。霍去病出代二千余里，破左贤王，斩首虏七万余，封狼居胥山，禅于姑衍，登临翰海。李广失道后期，自刭。"
     "「是后匈奴远遁，而幕南无王庭。」此役之后二人不复出塞：卫青前后七出击匈奴，斩捕首虏五万余级；霍去病六出，其四出以将军，斩捕首虏十一万余级（《史记》）。",
     "More than a thousand li out of Dingxiang Wei Qing found the chanyu drawn up waiting; he circled his armoured wagons into a laager and loosed "
     "five thousand horse at him. At dusk a gale threw up the sand, Han sent its wings round the chanyu, and he broke out to the north-west with a "
     "few hundred picked riders; the Han army pursued him to Zhao Xin's fort at Mount Tianyan. Huo Qubing marched more than two thousand li from "
     "Dai, crushed the Wise King of the Left, took over 70,000 heads and prisoners, sacrificed to Heaven on Mount Langjuxu and to Earth on Mount "
     "Guyan and climbed to look out over the Hanhai. Li Guang lost his way, arrived too late and cut his own throat. 'After this the Xiongnu fled "
     "far away, and there was no royal court south of the desert.' Neither man took the field again: in all Wei Qing campaigned against the "
     "Xiongnu seven times, taking more than 50,000 heads and prisoners, and Huo Qubing six times, four of them as a general, taking more than "
     "110,000 (Shiji)."),
    ("番禺之战", "Fall of Panyu", 113.27, 23.13, -111, 10, "汉 灭 南越", "Han destroyed Nanyue", "路博德、杨仆 vs 吕嘉", "Lu Bode and Yang Pu vs. Lü Jia",
     "广东广州", "Guangzhou, Guangdong", "楼船将军杨仆纵火烧城，伏波将军路博德招降，南越亡。", "Yang Pu, General of the Towered Ships, set the city on fire while Lu Bode, General Who Calms the Waves, took the surrender; Nanyue fell."),
    ("王险城之战", "Siege of Wangxian", 125.75, 39.02, -108, 6, "汉 灭 朝鲜", "Han destroyed Joseon", "杨仆、荀彘 vs 右渠", "Yang Pu and Xun Zhi vs. Ugeo",
     "朝鲜平壤", "Pyongyang, North Korea", "汉军水陆围城数月，朝鲜大臣杀右渠王来降。", "Han forces besieged the city by land and sea for months until Joseon ministers killed King Ugeo and surrendered."),
    ("楼兰之战", "Capture of Loulan", 89.9, 40.5, -108, 6, "汉 胜 楼兰·车师", "Han defeated Loulan and Jushi", "赵破奴、王恢", "Zhao Ponu and Wang Hui",
     "新疆罗布泊西北", "northwest of Lop Nur, Xinjiang", "赵破奴以轻骑七百虏楼兰王，遂破车师。", "Zhao Ponu captured the king of Loulan with seven hundred light horsemen and went on to break Jushi."),
    ("大宛之战", "War against Dayuan", 71.6, 40.5, -101, 6, "汉 胜 大宛", "Han defeated Dayuan", "李广利 vs 毋寡", "Li Guangli vs. Wugua",
     "费尔干纳盆地", "Ferghana basin", "李广利围贵山城，断其水源，大宛贵人杀王出降，献汗血马。", "Li Guangli besieged Guishan and cut off its water until the nobles killed their king, surrendered and handed over the blood-sweating horses."),
    ("浚稽山之战", "Battle of Mount Junji", 104.0, 44.3, -99, 9, "匈奴 胜 汉", "The Xiongnu defeated Han", "且鞮侯单于 vs 李陵", "The chanyu Qiedihou vs. Li Ling",
     "蒙古国南部（地望有争议）", "southern Mongolia (location disputed)", "李陵以步卒五千深入，遇单于三万骑，转战八日，矢尽而降。", "Li Ling marched deep with five thousand foot and met the chanyu's 30,000 horsemen; after eight days of fighting his arrows ran out and he surrendered."),
    ("燕然山之战", "Battle of Mount Yanran", 104.8, 45.6, -90, 6, "匈奴 胜 汉", "The Xiongnu defeated Han", "狐鹿姑单于 vs 李广利", "The chanyu Hulugu vs. Li Guangli",
     "蒙古国杭爱山", "Khangai Mountains, Mongolia", "李广利闻家族因巫蛊被收，冒进至郅居水，还至燕然山，军溃降匈奴。", "Hearing his family had been arrested in the witchcraft affair, Li Guangli pushed recklessly on to the Zhiju River; on the way back, at Mount Yanran, his army broke and he surrendered to the Xiongnu."),
    ("郅支城之战", "Battle of Zhizhi's fortress", 71.4, 42.9, -36, 10, "汉 胜 郅支", "Han defeated Zhizhi", "陈汤、甘延寿 vs 郅支单于", "Chen Tang and Gan Yanshou vs. the chanyu Zhizhi",
     "哈萨克斯坦塔拉兹一带", "near Taraz, Kazakhstan", "汉与西域诸国兵四万余攻破郅支城，斩单于。", "More than 40,000 Han and Western Regions troops stormed Zhizhi's fortress and beheaded the chanyu."),
    ("昆阳之战", "Battle of Kunyang", 113.42, 33.43, 23, 6, "汉 胜 新", "Han defeated Xin", "刘秀 vs 王寻、王邑", "Liu Xiu vs. Wang Xun and Wang Yi",
     "河南叶县", "Ye County, Henan", "刘秀以三千敢死士冲新军中坚，斩王寻，会大风雨，新军四十万溃散。", "Liu Xiu charged the Xin centre with three thousand men sworn to die and killed Wang Xun; in a great storm the 400,000-strong Xin army scattered."),
    ("崤底之战", "Battle of Xiaodi", 111.6, 34.6, 27, 1, "汉 胜 赤眉", "Han defeated the Red Eyebrows", "冯异 vs 樊崇", "Feng Yi vs. Fan Chong",
     "河南洛宁西北", "northwest of Luoning, Henan", "冯异令士卒以朱涂眉，混入赤眉阵中，大破之，降者八万。", "Feng Yi had his men paint their eyebrows red and mingle with the enemy, routing the Red Eyebrows; 80,000 surrendered."),
    ("临淄之战", "Battle of Linzi", 118.3, 36.87, 29, 10, "汉 胜 张步", "Han defeated Zhang Bu", "耿弇 vs 张步", "Geng Yan vs. Zhang Bu",
     "山东淄博临淄区", "Linzi District, Zibo, Shandong", "耿弇连拔祝阿、西安、临淄，大破张步，平齐地十二郡。", "Geng Yan took Zhu'a, Xi'an (in Qi) and Linzi one after another, routed Zhang Bu and won the twelve commanderies of Qi."),
    ("略阳之战", "Battle of Lüeyang", 105.95, 35.05, 32, 1, "汉 胜 隗嚣", "Han defeated Wei Xiao", "来歙 vs 隗嚣", "Lai Xi vs. Wei Xiao",
     "甘肃秦安东北", "northeast of Qin'an, Gansu", "来歙间道袭取略阳，隗嚣倾兵围攻数月不下，光武亲征。", "Lai Xi seized Lüeyang by a hidden path; Wei Xiao besieged it with his whole army for months in vain, and the emperor came in person."),
    ("荆门之战", "Battle of Jingmen", 111.4, 30.6, 35, 3, "汉 胜 成家", "Han defeated Chengjia", "岑彭 vs 任满、田戎", "Cen Peng vs. Ren Man and Tian Rong",
     "湖北宜都、宜昌之间", "between Yidu and Yichang, Hubei", "岑彭乘东风以楼船冲断浮桥，焚荆门、虎牙之栅，溯江入蜀。", "Cen Peng's tower ships, driven by an east wind, broke the floating bridge and burned the Jingmen–Huya barrier, and he advanced up the Yangzi into Shu."),
    ("成都之战", "Battle of Chengdu", 104.06, 30.66, 36, 11, "汉 胜 成家", "Han defeated Chengjia", "吴汉 vs 公孙述", "Wu Han vs. Gongsun Shu",
     "四川成都", "Chengdu, Sichuan", "吴汉进逼成都，公孙述出战中创，夜死，成家亡。", "Wu Han closed in on Chengdu; Gongsun Shu was wounded in a sortie and died that night, ending Chengjia."),
    ("浪泊之战", "Battle of Langbo", 105.95, 21.2, 42, 6, "汉 胜 征氏", "Han defeated the Trưng sisters", "马援 vs 征侧、征贰", "Ma Yuan vs. Trưng Trắc and Trưng Nhị",
     "越南河内一带", "Hanoi area, Vietnam", "马援缘海而进，随山刊道千余里，破征侧于浪泊，次年斩之。", "Ma Yuan advanced along the coast, cutting a road through the hills for over a thousand li, beat Trưng Trắc at Langbo and beheaded her the next year."),
    ("天山之战", "Battle of the Tianshan", 93.0, 43.6, 73, 2, "汉 胜 北匈奴", "Han defeated the Northern Xiongnu", "窦固、耿忠 vs 呼衍王", "Dou Gu and Geng Zhong vs. the Huyan king",
     "新疆巴里坤湖一带", "Lake Barkol, Xinjiang", "窦固出酒泉，破呼衍王于天山，追至蒲类海，取伊吾卢地。", "Dou Gu marched from Jiuquan, beat the Huyan king in the Tianshan, pursued him to Lake Pulei and took the Yiwulu lands."),
    ("蒲类海之战", "Battle of Lake Pulei", 92.8, 43.65, 74, 11, "汉 胜 北匈奴", "Han defeated the Northern Xiongnu", "窦固、耿秉、刘张 vs 北匈奴", "Dou Gu, Geng Bing and Liu Zhang vs. the Northern Xiongnu",
     "新疆巴里坤湖", "Lake Barkol, Xinjiang",
     "窦固、耿秉、刘张出敦煌昆仑塞，破北匈奴于蒲类海上，遂入车师；耿秉先击车师后王，后王安得出门迎降，前王亦降。于是复置西域都护、戊己校尉。",
     "Dou Gu, Geng Bing and Liu Zhang set out from the Kunlun frontier post of Dunhuang, beat the Northern Xiongnu on the shore of Lake Pulei and "
     "entered Jushi; Geng Bing struck first at the Rear King, An'de, who came out of his gate to surrender, and the Front King submitted too. The "
     "Protector-General and the Wu-Ji colonels were then restored."),
    ("疏勒之守", "Defence of the Shule fort", 89.7, 43.8, 75, 6, "汉 守 疏勒城", "Han held the Shule fort", "耿恭", "Geng Gong",
     "新疆奇台（石城子遗址）", "Shichengzi site, Qitai, Xinjiang", "北匈奴与车师围戊己校尉耿恭于车师后部疏勒城，拜井得泉，坚守经年，生还者十三人。", "The Northern Xiongnu and Jushi besieged the Wu-Ji colonel Geng Gong at the fort of Shule in the Rear Kingdom of Jushi; he found water by bowing to the well and held out for a year, only thirteen men surviving."),
    ("交河城之战", "Battle of Jiaohe", 89.07, 42.95, 76, 1, "汉 胜 车师", "Han defeated Jushi", "段彭、王蒙、皇甫援 vs 车师", "Duan Peng, Wang Meng and Huangfu Yuan vs. Jushi",
     "新疆吐鲁番交河故城", "Jiaohe ruins, Turpan, Xinjiang",
     "建初元年正月，酒泉太守段彭等发张掖、酒泉、敦煌三郡及鄯善兵七千余人，会柳中击车师，攻交河城，斩首三千八百级，北匈奴惊走，车师复降。己校尉关宠已没；"
     "范羌分兵二千越天山迎耿恭。章帝随即罢都护与戊己校尉。",
     "In the 1st month of Jianchu 1 Duan Peng, Administrator of Jiuquan, and others gathered over 7,000 men from Zhangye, Jiuquan, Dunhuang and "
     "Shanshan at Liuzhong, attacked Jushi and stormed Jiaohe, taking 3,800 heads; the Northern Xiongnu fled and Jushi submitted again. The "
     "Ji colonel Guan Chong was already dead; Fan Qiang took 2,000 men over the Tianshan to bring out Geng Gong. Emperor Zhang then abolished the "
     "Protector-General and the Wu-Ji colonels."),
    ("稽落山之战", "Battle of Mount Jiluo", 102.0, 44.6, 89, 6, "汉·南匈奴 胜 北匈奴", "Han and the Southern Xiongnu defeated the Northern Xiongnu", "窦宪、耿秉 vs 北单于", "Dou Xian and Geng Bing vs. the northern chanyu",
     "蒙古国南戈壁一带（地望有争议）", "Ömnögovi, Mongolia (location disputed)", "汉军与南匈奴出塞，大破北单于，降者二十余万人。", "Han troops and the Southern Xiongnu crossed the frontier and crushed the northern chanyu; more than 200,000 surrendered."),
    ("金微山之战", "Battle of the Jinwei Mountains", 89.5, 47.8, 91, 2, "汉 胜 北匈奴", "Han defeated the Northern Xiongnu", "耿夔、任尚 vs 北单于", "Geng Kui and Ren Shang vs. the northern chanyu",
     "阿尔泰山", "Altai Mountains", "汉军出居延塞五千余里，围北单于于金微山，北单于西走。", "The Han army marched over five thousand li from the Juyan frontier and surrounded the northern chanyu at the Jinwei Mountains; he fled west."),
    ("焉耆之战", "Conquest of Karasahr", 86.6, 42.0, 94, 7, "汉 胜 焉耆", "Han defeated Karasahr", "班超 vs 焉耆王广", "Ban Chao vs. Guang, king of Karasahr",
     "新疆焉耆", "Yanqi, Xinjiang", "班超发八国兵七万讨焉耆、危须、尉犁，斩焉耆王，西域悉平。", "Ban Chao raised 70,000 men from eight states against Karasahr, Weixu and Yuli, beheaded the king of Karasahr and pacified the Western Regions."),
    ("平襄之战", "Battle of Pingxiang", 105.12, 35.2, 108, 10, "羌 胜 汉", "The Qiang defeated Han", "滇零 vs 任尚", "Dianling vs. Ren Shang",
     "甘肃通渭西", "west of Tongwei, Gansu", "先零羌大破汉军于平襄，死者八千余人，滇零自称天子于北地。", "The Xianlian Qiang crushed the Han army at Pingxiang, killing over eight thousand, and Dianlian proclaimed himself Son of Heaven in Beidi."),
    ("车师之战", "Battle for Jushi", 89.1, 43.0, 124, 6, "汉 胜 北匈奴", "Han defeated the Northern Xiongnu", "班勇 vs 伊蠡王", "Ban Yong vs. the Yili king",
     "新疆吐鲁番", "Turpan, Xinjiang", "班勇发龟兹、姑墨、温宿兵万余人至车师前王庭，击走北匈奴伊蠡王，前部复通。", "Ban Yong raised over ten thousand troops from Kucha, Gumo and Wensu, marched to the court of the Front King of Jushi and drove off the Northern Xiongnu Yili king, reopening the Front Kingdom."),
    ("射虎谷之战", "Battle of Shehu Valley", 106.0, 34.55, 169, 7, "汉 胜 东羌", "Han defeated the Eastern Qiang", "段颎 vs 东羌", "Duan Jiong vs. the Eastern Qiang",
     "甘肃天水", "Tianshui, Gansu", "段颎分兵夹击，东羌一万九千级授首，东羌平。", "Duan Jiong attacked from both sides, taking 19,000 heads; the Eastern Qiang were put down."),
    ("三将出塞", "The three generals' expedition", 112.5, 43.2, 177, 8, "鲜卑 胜 汉", "The Xianbei defeated Han", "檀石槐 vs 夏育、田晏、臧旻", "Tanshihuai vs. Xia Yu, Tian Yan and Zang Min",
     "内蒙古锡林郭勒一带", "Xilingol, Inner Mongolia", "汉三道出塞二千余里，为鲜卑所败，死者十七八。", "Three Han columns marched over two thousand li beyond the frontier and were routed by the Xianbei, seven or eight in ten killed."),
]

# (名, 英文名, 经, 纬, 年, 月, 今地, 英文今地, 说明, 英文说明)
EVENTS = [
    ("焚书坑儒", "Burning of the books, burying of the scholars", 108.72, 34.37, -213, None, "陕西咸阳", "Xianyang, Shaanxi",
     "前213 年用李斯议焚《诗》《书》百家语；次年坑诸生四百六十余人于咸阳。", "In 213 BC, on Li Si's advice, the Odes, the Documents and the works of the hundred schools were burned; the next year more than 460 scholars were buried at Xianyang."),
    ("沙丘之变", "The Shaqiu plot", 115.2, 37.4, -210, 7, "河北广宗西北", "northwest of Guangzong, Hebei",
     "始皇东巡崩于沙丘平台，赵高、李斯秘不发丧，矫诏赐死扶苏，立胡亥。", "The First Emperor died on tour at Shaqiu; Zhao Gao and Li Si concealed his death, forged an order for Fusu to kill himself and enthroned Huhai."),
    ("大泽乡起事", "Dazexiang uprising", 117.05, 33.55, -209, 7, "安徽宿州东南", "southeast of Suzhou, Anhui",
     "陈胜、吴广遇雨失期，「王侯将相宁有种乎」，斩尉起事，为秦末首义。", "Late because of the rain, Chen Sheng and Wu Guang killed their officers ('are kings, lords, generals and ministers born to it?') — the first rising against Qin."),
    ("约法三章", "The three-article code", 109.05, 34.25, -206, 11, "陕西西安东（霸上）", "Bashang, east of Xi'an, Shaanxi",
     "刘邦入咸阳后还军霸上，与关中父老约法三章：杀人者死，伤人及盗抵罪，余悉除去秦法。", "Back at Bashang after entering Xianyang, Liu Bang agreed three articles with the elders of Guanzhong — death for murder, punishment for injury and theft — abolishing the rest of Qin law."),
    ("鸿门宴", "The Hongmen banquet", 109.27, 34.38, -206, 12, "陕西西安临潼区", "Lintong District, Xi'an, Shaanxi",
     "项羽设宴鸿门，范增使项庄舞剑欲杀刘邦，项伯翼蔽，樊哙闯帐，刘邦脱身。", "At Xiang Yu's banquet at Hongmen, Fan Zeng had Xiang Zhuang perform a sword dance to kill Liu Bang; Xiang Bo shielded him, Fan Kuai burst in and Liu Bang got away."),
    ("火烧咸阳", "Burning of Xianyang", 108.72, 34.37, -206, 12, "陕西咸阳", "Xianyang, Shaanxi", "项羽屠咸阳，杀子婴，烧秦宫室，火三月不灭。", "Xiang Yu sacked Xianyang, killed Ziying and burned the Qin palaces; the fire was not put out for three months."),
    ("乌江自刎", "Death at Wujiang", 118.35, 31.75, -202, 12, "安徽和县东北", "northeast of He County, Anhui", "项羽至乌江，「天之亡我，我何渡为」，自刎而死。", "Reaching Wujiang, Xiang Yu said 'Heaven is destroying me — why should I cross?' and cut his own throat."),
    ("诛韩信", "Execution of Han Xin", 108.88, 34.31, -196, 1, "陕西西安（长乐宫）", "Xi'an, Shaanxi (Changle Palace)", "吕后与萧何诱韩信入长乐宫钟室斩之，夷三族。", "Empress Lü and Xiao He lured Han Xin into the bell room of the Changle Palace and executed him with three branches of his family."),
    ("马邑之谋", "The Mayi ambush", 112.43, 39.33, -133, 6, "山西朔州", "Shuozhou, Shanxi", "汉伏兵三十万于马邑欲诱击单于，事泄未果，和亲遂绝。", "Han hid 300,000 men at Mayi to ambush the chanyu, but the plan leaked; the peace by marriage ended."),
    ("推恩令", "Edict of Grace", 108.88, 34.31, -127, 1, "陕西西安", "Xi'an, Shaanxi", "主父偃献策：许诸侯王推私恩分封子弟为侯，王国由是自析。", "On Zhufu Yan's proposal kings were allowed to grant parts of their lands to younger sons as marquisates, so the kingdoms divided themselves."),
    ("张骞归汉", "Zhang Qian's return", 108.88, 34.31, -126, None, "陕西西安", "Xi'an, Shaanxi", "张骞去十三年，百余人仅二人得还，备言西域诸国之地形物产，史称「凿空」。", "Zhang Qian came back after thirteen years, only two of more than a hundred men surviving, with full reports on the terrain and products of the states of the Western Regions — the 'opening of the void'."),
    ("盐铁官营", "Salt and iron monopolies", 108.88, 34.31, -119, None, "陕西西安", "Xi'an, Shaanxi", "桑弘羊等主持盐铁官营、均输平准、算缗告缗，以济边用。", "Sang Hongyang and others set up state monopolies of salt and iron, equitable transport and price stabilisation, and taxes on merchants to pay for the frontier wars."),
    ("巫蛊之祸", "The witchcraft affair", 108.88, 34.31, -91, 7, "陕西西安", "Xi'an, Shaanxi", "江充诬太子刘据行巫蛊，太子发兵诛江充，兵败自杀，死者数万。", "Jiang Chong accused Crown Prince Liu Ju of witchcraft; the prince raised troops and killed him but was defeated and killed himself, tens of thousands dying."),
    ("轮台诏", "The Luntai edict", 108.88, 34.31, -89, None, "陕西西安", "Xi'an, Shaanxi", "武帝晚年下诏罢轮台屯田，「当今务在禁苛暴，止擅赋，力本农」。", "In his last years Emperor Wu issued an edict dropping the farming garrison at Luntai: 'our task now is to stop harshness, end arbitrary levies and devote ourselves to farming'."),
    ("盐铁会议", "The Salt and Iron debate", 108.88, 34.31, -81, 2, "陕西西安", "Xi'an, Shaanxi", "贤良文学与桑弘羊辩论盐铁官营存废，桓宽录为《盐铁论》。", "Scholars debated with Sang Hongyang whether to keep the salt and iron monopolies; Huan Kuan recorded it as the Discourses on Salt and Iron."),
    ("五将军击匈奴", "The five generals' campaign", 104.0, 44.0, -71, 1, "蒙古国南部", "southern Mongolia", "汉发十五万骑与乌孙夹击匈奴，常惠率乌孙兵获单于父行、嫂、居次。", "Han sent 150,000 horsemen to attack the Xiongnu together with Wusun; Chang Hui and the Wusun captured the chanyu's uncles, sister-in-law and daughters."),
    ("石渠阁会议", "The Shiqu Pavilion council", 108.88, 34.31, -51, None, "陕西西安", "Xi'an, Shaanxi", "宣帝召诸儒于石渠阁讲论五经同异，亲称制临决。", "Emperor Xuan gathered the scholars at the Shiqu Pavilion to debate differences among the Five Classics, deciding the questions himself."),
    ("昭君出塞", "Wang Zhaojun goes beyond the frontier", 110.0, 41.5, -33, 1, "内蒙古阴山一带", "Yin Mountains, Inner Mongolia", "元帝以宫人王嫱嫁呼韩邪单于，号宁胡阏氏，汉匈和亲六十余年。", "Emperor Yuan gave the palace lady Wang Qiang to the chanyu Huhanye as a bride, titled Ninghu Yanzhi; Han and the Xiongnu stayed at peace for over sixty years."),
    ("王莽改制", "Wang Mang's reforms", 108.88, 34.31, 9, None, "陕西西安", "Xi'an, Shaanxi", "王田、私属，五均六筦，屡改币制，改官名地名，扰民尤甚。", "Nationalised land, a ban on selling slaves, price controls and monopolies, repeated changes of coinage and of official and place names — all deeply disruptive."),
    ("黄河南徙", "The Yellow River shifts south", 115.3, 36.0, 11, None, "河北大名、山东一带", "Daming, Hebei and Shandong", "河决魏郡，东南流经清河以东数郡入海，王莽以元城祖坟无水患而不塞，泛滥近六十年。", "The river broke its banks in Wei Commandery and flowed south-east through several commanderies east of Qinghe to the sea; Wang Mang left the breach open because his ancestral tombs at Yuancheng were safe, and the floods went on for nearly sixty years."),
    ("光武即位", "Guangwu's accession", 114.75, 37.65, 25, 6, "河北柏乡北", "north of Baixiang, Hebei", "刘秀即皇帝位于鄗南千秋亭，改元建武。", "Liu Xiu took the throne at the Qianqiu Pavilion south of Hao, with the era name Jianwu."),
    ("马援铜柱", "Ma Yuan's bronze pillars", 107.5, 18.0, 43, None, "越南中部（地望不详）", "central Vietnam (site unknown)", "马援平交趾后立铜柱为汉之极界（传说）。", "After pacifying Jiaozhi Ma Yuan is said to have set up bronze pillars at the limit of Han territory."),
    ("倭奴国奉贡", "The Wa state of Na sends tribute", 130.35, 33.67, 57, 1, "日本福冈志贺岛", "Shikanoshima, Fukuoka, Japan", "倭奴国遣使奉贡，光武赐以印绶；1784 年志贺岛出土「汉委奴国王」金印。", "The Wa state of Na sent envoys and Emperor Guangwu gave it a seal; the gold seal 'King of Na of Wa of Han' was found on Shikanoshima in 1784."),
    ("白马寺", "White Horse Temple", 112.6, 34.72, 68, None, "河南洛阳东", "east of Luoyang, Henan", "明帝遣使求法，迦叶摩腾、竺法兰以白马驮经至洛阳，建白马寺。", "Emperor Ming sent envoys to seek the Buddhist teaching; Kasyapa Matanga and Dharmaratna brought scriptures to Luoyang on a white horse, and the White Horse Temple was built."),
    ("王景治河", "Wang Jing tames the Yellow River", 116.0, 36.1, 69, 4, "河南、山东", "Henan and Shandong", "王景、王吴发卒数十万修汴渠、筑河堤千余里，黄河自此安流八百年。", "Wang Jing and Wang Wu led hundreds of thousands of workers to restore the Bian Canal and build over a thousand li of dykes; the river then flowed quietly for eight hundred years."),
    ("甘英使大秦", "Gan Ying's mission to Da Qin", 61.83, 37.6, 97, None, "（经安息）", "(via Parthia)", "班超遣甘英出使大秦，经安息至条支海滨，闻海广难渡而还。", "Ban Chao sent Gan Ying towards Da Qin; he crossed Parthia to the shore of the sea of Tiaozhi but turned back, told it was too wide to cross."),
    ("蔡伦造纸", "Cai Lun's paper", 112.6, 34.72, 105, None, "河南洛阳", "Luoyang, Henan", "尚方令蔡伦用树皮、麻头、敝布、鱼网造纸，奏上，「天下咸称蔡侯纸」。", "Cai Lun, director of the imperial workshops, made paper from bark, hemp waste, rags and fishing nets and presented it; 'everyone called it Marquis Cai's paper'."),
    ("西域长史", "Chief Clerk of the Western Regions", 89.7, 42.9, 123, None, "新疆鄯善鲁克沁", "Lukqun, Shanshan County, Xinjiang", "以班勇为西域长史，屯柳中，代行都护之职。", "Ban Yong was made Chief Clerk of the Western Regions, garrisoned at Liuzhong and acting in place of a Protector-General."),
    ("张衡地动仪", "Zhang Heng's seismoscope", 112.6, 34.72, 132, None, "河南洛阳", "Luoyang, Henan", "太史令张衡作候风地动仪，138 年测得陇西地震。", "Zhang Heng, the Grand Astrologer, built his seismoscope, which detected an earthquake in Longxi in 138."),
    ("永和羌乱", "The Yonghe Qiang war", 106.5, 35.6, 140, None, "甘肃、宁夏", "Gansu and Ningxia", "且冻、傅难羌反，寇三辅，烧园陵，杀长吏，历五年乃平。", "The Qiedong and Funan Qiang rebelled, raiding the capital region, burning imperial tombs and killing officials; it took five years to suppress."),
    ("党锢之祸", "The Partisan Prohibitions", 112.6, 34.72, 166, None, "河南洛阳", "Luoyang, Henan", "宦官诬李膺等结党，禁锢终身；169 年再兴党狱，死者百余人。", "The eunuchs accused Li Ying and others of forming factions and barred them from office for life; a second purge in 169 killed over a hundred."),
    ("熹平石经", "The Xiping Stone Classics", 112.6, 34.72, 175, None, "河南洛阳（太学）", "Luoyang, Henan (Imperial Academy)", "蔡邕等正定六经文字，刻石立于太学门外。", "Cai Yong and others fixed the texts of the Six Classics, carved them in stone and set them up outside the Imperial Academy."),
    ("浑邪王降", "Surrender of the Hunye king", 103.7, 37.0, -121, 8, "甘肃兰州以北黄河西岸一带（大致）", "west bank of the Yellow River north of Lanzhou, Gansu (approx.)",
     "单于怒浑邪王屡败，欲诛之；浑邪王与休屠王谋降汉，休屠王中悔，浑邪王杀之，并其众。霍去病渡河受降，浑邪王部众多欲遁去，霍去病驰入营中"
     "斩欲亡者八千人，降者四万余，号称十万，汉分处于五郡塞外为五属国。休屠王太子金日磾没入官养马，后为武帝顾命大臣。",
     "The chanyu, furious at the Hunye king's repeated defeats, meant to have him killed; the Hunye king plotted with the Xiutu king to go over to "
     "Han, and when the Xiutu king had second thoughts he killed him and took his people. Huo Qubing crossed the Yellow River to receive the "
     "surrender; when many of the Hunye king's men tried to slip away, he rode into their camp and cut down eight thousand of them. More than 40,000 "
     "surrendered (it was given out as 100,000) and were settled beyond the frontier of five commanderies as five dependent states. The Xiutu "
     "king's heir, Jin Midi, was made a palace slave tending horses and later became one of the ministers Emperor Wu named on his deathbed."),
    ("封狼居胥", "Sacrifice on Mount Langjuxu", 108.9, 48.6, -119, None, "蒙古国肯特山（一说）", "Khentii Mountains, Mongolia (one view)",
     "霍去病破左贤王，封狼居胥山，禅于姑衍，登临翰海。封是筑土为坛祭天，禅是除地祭地，本是天子告成功的大礼；霍去病以此宣示汉兵所至。"
     "「封狼居胥」从此成为武将功业的最高象征，辛弃疾「元嘉草草，封狼居胥，赢得仓皇北顾」即用此典。",
     "Having crushed the Wise King of the Left, Huo Qubing performed the feng sacrifice to Heaven on Mount Langjuxu and the shan sacrifice to Earth "
     "on Mount Guyan, then climbed to look out over the Hanhai. Feng meant raising an earth altar to Heaven and shan clearing the ground to "
     "sacrifice to Earth, rites by which a Son of Heaven announced his achievements; Huo Qubing used them to proclaim how far Han arms had reached. "
     "'Sacrificing on Langjuxu' became the supreme emblem of a general's success, and Xin Qiji's line on the hasty Yuanjia expedition that "
     "dreamed of Langjuxu and ended in a panicked retreat draws on it."),
    ("苏武牧羊", "Su Wu herds sheep", 106.6, 52.0, -100, None, "俄罗斯贝加尔湖一带", "Lake Baikal, Russia",
     "前100 年中郎将苏武持节出使匈奴，因副使张胜参与谋劫单于母阏氏事被扣。单于幽之大窖中，苏武啮雪与旃毛并咽之，数日不死；乃徙北海上无人处，"
     "使牧羝（公羊），曰「羝乳乃得归」。苏武杖汉节牧羊，卧起操持，节旄尽落。前81 年汉匈和亲，汉使以「天子射上林中得雁，足有系帛书」诘单于，"
     "苏武始得归，留匈奴凡十九年。",
     "In 100 BC Su Wu, a General of the Household, went to the Xiongnu as envoy bearing the emperor's tally, and was detained when his deputy Zhang Sheng "
     "was implicated in a plot to kidnap the chanyu's mother. Shut in a cellar, Su Wu chewed snow and swallowed felt and survived for days; he was "
     "then sent to an empty land by the North Sea to herd rams and told he could go home when they gave milk. He herded them leaning on the Han "
     "tally, holding it waking and sleeping until all its tassels had fallen off. When Han and the Xiongnu made peace in 81 BC, a Han envoy "
     "confronted the chanyu with the tale that the emperor had shot a wild goose in the Shanglin park with a silk letter tied to its foot, and Su "
     "Wu was at last allowed home after nineteen years among the Xiongnu."),
    ("勒石燕然", "Inscription on Mount Yanran", 104.554, 45.178, 89, None, "蒙古国中戈壁省德勒格尔杭爱", "Delgerkhangai, Dundgovi Province, Mongolia",
     "窦宪大破北单于后登燕然山，去塞三千余里，令中护军班固作《封燕然山铭》，刻石勒功。摩崖于 1990 年代为当地人发现，2017 年中蒙联合考察队"
     "释读确认，「勒石燕然」从此有了确切的地点。",
     "After crushing the northern chanyu, Dou Xian climbed Mount Yanran, more than three thousand li beyond the frontier, and had his army "
     "protector Ban Gu compose the Inscription for the Feng Sacrifice on Mount Yanran, which was carved into the rock. The cliff inscription was "
     "found by local people in the 1990s and identified by a joint Chinese–Mongolian survey in 2017, giving 'carving the rock at Yanran' a precise "
     "place on the map."),
    ("鸿沟之约", "The Honggou agreement", 113.95, 34.8, -203, 8, "河南荥阳—开封一带鸿沟沿线", "along the Honggou between Xingyang and Kaifeng, Henan",
     "楚汉相持数月，楚兵罢食绝，韩信又进击楚。项羽与汉约，「中分天下，割鸿沟以西者为汉，鸿沟而东者为楚」，归还太公、吕后，解而东归。"
     "汉王欲西归，张良、陈平以为「此天亡楚之时也」，劝其背约追击。",
     "After months of stalemate, with the Chu army exhausted, its food gone and Han Xin advancing on Chu, Xiang Yu agreed with Han to 'divide the "
     "realm in two, the land west of the Honggou to Han and the land east of it to Chu', handed back the king of Han's father and wife and marched "
     "away east. The king of Han meant to go back west, but Zhang Liang and Chen Ping told him that 'this is the moment Heaven has chosen to destroy "
     "Chu' and urged him to break the agreement and pursue."),
]

# (名, 英文名, 经, 纬, 起, 止, 说明, 英文说明)
PEOPLES = [
    ("丁零", "Dingling", 101.0, 52.5, -212, 184, "贝加尔湖以南的游牧部族，冒顿时服属匈奴，东汉时屡击北匈奴。", "Nomads south of Lake Baikal, subject to the Xiongnu under Modu; under the Eastern Han they often attacked the Northern Xiongnu."),
    ("坚昆", "Jiankun", 91.5, 53.0, -212, 184, "叶尼塞河上游的部族（后之黠戛斯），郅支单于曾徙居其地。", "A people of the upper Yenisei (later the Kyrgyz), among whom the chanyu Zhizhi once lived."),
    ("呼揭", "Hujie", 88.0, 48.2, -212, -36, "阿尔泰山南麓的部族，前176 年服属匈奴。", "A people of the southern Altai, subject to the Xiongnu from 176 BC."),
    ("楼烦", "Loufan", 111.0, 40.0, -212, -127, "河套东北的部族，汉初并于匈奴，前127 年为卫青所逐。", "A people north-east of the Ordos, absorbed by the Xiongnu in early Han and driven out by Wei Qing in 127 BC."),
    ("白羊", "Baiyang", 108.0, 39.0, -212, -127, "河套的部族，号白羊王，前127 年为卫青所逐。", "A people of the Ordos under the Baiyang king, driven out by Wei Qing in 127 BC."),
    ("小月氏", "Lesser Yuezhi", 101.5, 37.4, -176, 184, "月氏西迁时留居南山的余部，与羌杂处，东汉时为湟中义从胡。", "The Yuezhi who stayed in the Southern Mountains when the rest went west, living among the Qiang; under the Eastern Han they served as the Huangzhong auxiliaries."),
    ("氐", "Di", 105.5, 33.5, -212, 184, "武都、阴平一带的部族，白马氐最大，武帝时置武都郡。", "A people of Wudu and Yinping, the Baima Di the largest; Wudu Commandery was set up among them under Emperor Wu."),
    ("婼羌", "Ruoqiang", 89.5, 37.8, -212, 184, "阿尔金山一带随畜逐水草的羌人，不田作。", "Qiang of the Altun Mountains who followed their herds and did not farm."),
    ("发羌", "Fa Qiang", 91.0, 31.0, -212, 184, "青藏高原腹地的羌人部落，或以为吐蕃之先。", "Qiang tribes deep in the Tibetan plateau, sometimes thought to be forerunners of the Tibetans."),
    ("濊", "Ye", 128.4, 38.4, -212, 184, "朝鲜半岛东部的部族，前128 年濊君南闾降汉。", "A people of the eastern Korean peninsula; their chief Namnyeo submitted to Han in 128 BC."),
    ("挹娄", "Yilou", 132.0, 46.5, -212, 184, "夫余以东的林中部族，善射，即古之肃慎，曾臣属夫余。", "Forest dwellers east of Buyeo, skilled archers, identified with the ancient Sushen; once subject to Buyeo."),
    ("倭", "Wa", 131.0, 33.8, -212, 184, "日本列岛的倭人，《汉书》称「分为百余国」，57 年倭奴国奉贡。", "The Wa of the Japanese islands, 'divided into more than a hundred states' according to the Han shu; the state of Na sent tribute in 57."),
    ("山越", "Shanyue", 118.3, 29.3, -110, 184, "江南山地的越人，东汉时屡起反抗。", "The Yue of the hills of Jiangnan, who often rose against the Eastern Han."),
    ("骆越", "Luoyue", 107.8, 21.6, -212, 184, "红河流域与岭南西部的越人。", "The Yue of the Red River valley and western Lingnan."),
    ("昆明", "Kunming", 100.3, 25.8, -212, 184, "洱海一带随畜迁徙的部族，屡劫杀汉使，阻通身毒之道。", "Herders around Lake Erhai who repeatedly attacked Han envoys and blocked the route to India."),
    ("奄蔡", "Yancai", 62.0, 46.5, -212, 184, "咸海以北的游牧之国（阿兰聊），控弦十余万。", "A nomadic state north of the Aral Sea (Alanliao, i.e. the Alans), with over a hundred thousand archers."),
]

# (名, 英文名, 经, 纬, 今地, 英文今地, 说明, 英文说明)
PASSES = [
    ("广武（汉王城·霸王城）", "Guangwu (Han King's and Hegemon-King's forts)", 113.47, 34.93, "河南荥阳广武镇", "Guangwu, Xingyang, Henan",
     "荥阳北广武山上，楚汉相持之地。东西两城隔广武涧对峙，相传西为汉王城、东为霸王城，今人也把这道涧叫作鸿沟。前203 年项羽置太公于俎上欲烹之，"
     "刘邦答以「幸分我一杯羹」；项羽请与汉王独身挑战，汉王数项羽十大罪，被伏弩射中胸口，扪足曰「虏中吾指」以安军心。",
     "On Mount Guangwu north of Xingyang, where Chu and Han faced each other for months. Two forts stand on either side of the Guangwu ravine, by "
     "tradition the Han King's fort to the west and the Hegemon-King's to the east, and the ravine itself is nowadays also called the Honggou. In "
     "203 BC Xiang Yu set Liu Bang's father on a chopping block and threatened to boil him; Liu Bang replied that he hoped to be sent a cup of the "
     "broth. When Xiang Yu challenged him to single combat, the king of Han listed Xiang Yu's ten great crimes and was hit in the chest by a hidden "
     "crossbowman; clutching his foot, he cried 'The wretch has hit my toe!' to keep his army steady."),
    ("峣关", "Yao Pass", 109.42, 34.07, "陕西蓝田东南", "southeast of Lantian, Shaanxi", "武关通关中的要隘，刘邦入关曾袭破之。", "The key pass on the road from the Wu Pass into Guanzhong, taken by Liu Bang on his way in."),
    ("临晋关", "Linjin Pass", 110.25, 34.8, "陕西大荔东", "east of Dali, Shaanxi", "黄河蒲津渡口西岸，关中东北门户。", "The west bank of the Pujin ferry over the Yellow River, Guanzhong's north-eastern gate."),
    ("高阙", "Gaoque", 107.35, 41.15, "内蒙古阴山西段狼山", "Langshan, western Yin Mountains, Inner Mongolia", "阴山缺口，赵武灵王置塞，卫青由此出击。", "A gap in the Yin Mountains fortified by King Wuling of Zhao; Wei Qing struck out from here."),
    ("鸡鹿塞", "Jilu frontier post", 106.6, 41.25, "内蒙古磴口西北", "northwest of Dengkou, Inner Mongolia", "朔方郡西北塞口，窦宪出征北匈奴即由此。", "A frontier gate in the north-west of Shuofang Commandery, from which Dou Xian set out against the Northern Xiongnu."),
    ("居延塞", "Juyan frontier", 101.0, 41.9, "内蒙古额济纳旗", "Ejin Banner, Inner Mongolia", "前102 年路博德筑，出土汉简数万枚。", "Built by Lu Bode in 102 BC; tens of thousands of Han wooden slips have been found here."),
    ("乌垒城", "Wulei", 84.6, 41.75, "新疆轮台东", "east of Luntai, Xinjiang", "西域都护治所。", "Seat of the Protector-General of the Western Regions."),
    ("柳中", "Liuzhong", 89.7, 42.9, "新疆鄯善鲁克沁", "Lukqun, Shanshan County, Xinjiang", "东汉戊己校尉、西域长史屯田之所。", "Farming garrison of the Eastern Han Wu-Ji colonel and the Chief Clerk of the Western Regions."),
    ("赵信城", "Zhao Xin's fort", 103.2, 46.8, "蒙古国杭爱山南麓（一说；点位示意）", "southern foot of the Khangai Mountains, Mongolia (one view; approximate)",
     "前123 年赵信兵败复降匈奴，单于以为自次王，以姊妻之，筑城居之，故名。前119 年卫青追单于至窴颜山赵信城，取其积粟食军，留一日，悉烧余粟而还。"
     "史籍只说在窴颜山下，今地无定说：一说在杭爱山南麓（窴颜山为杭爱山南支），图上取此说；一说在色楞格河支流哈努伊河中游，附近有匈奴古城遗址；"
     "蒙古学者曾把南戈壁省巴彦布拉格城址比作赵信城，主持发掘的俄罗斯学者科瓦列夫则认为是汉受降城，城中合葬的士卒经古 DNA 与同位素分析为华北人。"
     "谭其骧《中国历史地图集》不标。",
     "After his defeat in 123 BC Zhao Xin went back over to the Xiongnu; the chanyu made him the Zici king, gave him his elder sister in marriage "
     "and built a fort for him to live in, hence its name. In 119 BC Wei Qing pursued the chanyu to Zhao Xin's fort at Mount Tianyan, fed his army "
     "on the grain stored there, stayed one day and burned the rest. The sources say only that it lay below Mount Tianyan, and its modern site is "
     "unsettled: one view puts it at the southern foot of the Khangai Mountains (Mount Tianyan being a southern spur of the Khangai), which the "
     "map follows; another on the middle Khanuy River, a tributary of the Selenge, near the ruins of a Xiongnu walled town. Mongolian scholars "
     "once identified the walled site of Bayanbulag in Ömnögovi as Zhao Xin's fort, but its excavator, the Russian archaeologist Alexey Kovalev, takes it for the Han fort of "
     "Shouxiang, and ancient DNA and isotope analysis show that the soldiers buried together there came from northern China. Tan Qixiang's Historical "
     "Atlas of China does not mark it."),
    ("令居塞", "Lingju frontier", 103.3, 36.6, "甘肃永登", "Yongdeng, Gansu", "前121 年后筑，河西塞的起点。", "Built after 121 BC, the starting point of the Hexi frontier."),
]

# (名, 英文名, 线, 起年, 今地, 英文今地, 说明, 英文说明)
WALLS = [
    ("河西汉塞", "Han frontier wall of Hexi", [[103.3, 36.6], [102.6, 37.9], [101.4, 38.6], [100.4, 39.1], [99.4, 39.5], [98.5, 39.8],
                                              [97.4, 40.2], [95.8, 40.5], [94.7, 40.4], [93.9, 40.35], [93.1, 40.3], [92.2, 40.3]], -111,
     "甘肃永登—敦煌西", "Yongdeng to west of Dunhuang, Gansu", "前121 年后自令居西筑塞，前111—前101 年延至酒泉、玉门、盐泽，烽燧相望。", "After 121 BC a frontier was built west from Lingju, extended in 111–101 BC to Jiuquan, the Jade Gate and the Salt Marsh, with beacon towers in sight of one another."),
    ("居延塞", "Juyan frontier wall", [[98.9, 39.9], [99.6, 40.4], [100.3, 41.0], [100.8, 41.6], [101.1, 42.0]], -102,
     "甘肃金塔—内蒙古额济纳", "Jinta, Gansu to Ejin, Inner Mongolia", "前102 年路博德筑，沿弱水北至居延泽，遮断匈奴南下河西之路。", "Built by Lu Bode in 102 BC along the Ruo River north to Lake Juyan, blocking the Xiongnu route south into Hexi."),
    ("光禄塞（外城）", "Guanglu frontier (outer walls)", [[106.4, 42.0], [107.6, 41.8], [108.8, 41.6], [109.9, 41.4], [111.0, 41.6], [112.2, 41.9]], -102,
     "内蒙古阴山以北", "north of the Yin Mountains, Inner Mongolia", "前102 年光禄勋徐自为筑五原塞外列城，远者千余里，史称光禄塞。", "Built in 102 BC by Xu Ziwei, Superintendent of the Palace, as a chain of forts beyond the Wuyuan frontier, the farthest more than a thousand li out: the Guanglu frontier."),
]

# 行军路线：每条 dict(名, 英文名, 说明, 英文说明, 点)。点 (地名, 英文地名, 经, 纬, 纪年年, 月)：
# 日期是到达该点的时间（纪年年 + 月，太初以前十至十二月记在新一年）；月不详写 None（按年）。
# 地名空着的是只管走向的折点，日期同下一个有名的点。地图每个节点只画本期走过的一段，此前走过的画虚线。
def R(name, en, note, note_en, pts):
    return dict(name=name, en=en, note=note, note_en=note_en, pts=pts)


ROUTES = [
    # ---------------- 秦末 ----------------
    R("陈胜吴广起事", "Chen Sheng and Wu Guang's rising",
      "戍卒九百人屯大泽乡，遇雨失期，陈胜、吴广杀将尉起事，攻蕲，分兵东略，主力西攻铚、酂、谯、苦等县，行收兵，至陈已有车六七百乘、骑千余、卒数万。",
      "Nine hundred conscripts held up by rain at Dazexiang killed their officers and rose under Chen Sheng and Wu Guang. They took Qi, sent a detachment east, and with the main force struck west, taking Zhi, Cuo, Qiao, Ku and other counties, gathering men as they went; by the time they reached Chen they had six or seven hundred chariots, over a thousand horsemen and tens of thousands of foot.",
      [("大泽乡", "Dazexiang", 117.05, 33.55, -209, 7), ("蕲", "Qi", 116.95, 33.6, -209, 7), ("铚", "Zhi", 116.6, 33.7, -209, 7),
       ("酂", "Cuo", 116.18, 33.95, -209, 7), ("谯", "Qiao", 115.78, 33.85, -209, 7), ("苦", "Ku", 115.5, 33.85, -209, 7),
       ("陈", "Chen", 114.88, 33.73, -209, 7)]),
    R("周文西攻", "Zhou Wen's drive west",
      "陈胜遣周文西击秦，沿途收兵，入函谷关时有车千乘、卒数十万，九月至戏。章邯发骊山刑徒击破之，周文退出关，止曹阳，再败于渑池，自刎。",
      "Chen Sheng sent Zhou Wen west against Qin. Gathering men along the way, he passed the Hangu Pass with a thousand chariots and several hundred thousand men and reached Xi in the 9th month. Zhang Han, arming the Lishan labourers, routed him; Zhou Wen fell back through the pass to Caoyang, was beaten again at Mianchi and cut his own throat.",
      [("陈", "Chen", 114.88, 33.73, -209, 8), ("荥阳", "Xingyang", 113.4, 34.82, -209, 8), ("函谷关", "Hangu Pass", 110.87, 34.63, -209, 9),
       ("戏", "Xi", 109.3, 34.4, -209, 9), ("曹阳", "Caoyang", 110.75, 34.6, -208, 10), ("渑池", "Mianchi", 111.75, 34.77, -208, 11)]),
    R("刘邦入关", "Liu Bang into Guanzhong",
      "楚怀王遣沛公西略地入关。沛公自砀北破东郡尉于成武，攻昌邑不下，西袭陈留，攻开封，破秦将杨熊于曲遇，南屠颍阳；入南阳，降宛，破武关，用张良计袭破峣关下秦军于蓝田，汉元年十月至霸上，子婴出降。",
      "King Huai of Chu sent the Lord of Pei west to win land and enter the passes. From Dang he struck north and beat the commandant of Dong Commandery at Chengwu, failed to take Changyi, fell on Chenliu, attacked Kaifeng, beat the Qin general Yang Xiong at Quyu and sacked Yingyang to the south. He then entered Nanyang, took the surrender of Wan, broke through the Wu Pass and, on Zhang Liang's advice, routed the Qin army below the Yao Pass at Lantian; in the 10th month of Han year 1 he reached Bashang, where Ziying surrendered.",
      [("砀", "Dang", 116.35, 34.42, -208, 9), ("成武", "Chengwu", 115.9, 34.95, -207, 10), ("昌邑", "Changyi", 116.12, 35.25, -207, 2),
       ("陈留", "Chenliu", 114.55, 34.68, -207, 2), ("开封", "Kaifeng", 114.35, 34.75, -207, 3), ("曲遇", "Quyu", 114.0, 34.65, -207, 3),
       ("颍阳", "Yingyang", 113.35, 34.25, -207, 4), ("犨", "Chou", 113.0, 33.75, -207, 6), ("宛", "Wan", 112.53, 33.0, -207, 7),
       ("丹水", "Danshui", 111.3, 33.05, -207, 7), ("武关", "Wu Pass", 110.65, 33.55, -207, 8), ("蓝田", "Lantian", 109.3, 34.12, -207, 9),
       ("霸上", "Bashang", 109.05, 34.25, -206, 10)]),
    R("项羽救赵入关", "Xiang Yu relieves Zhao and enters Guanzhong",
      "宋义、项羽北救赵，宋义留安阳四十六日不进，项羽杀之，引兵渡河，破釜沉舟，大破秦军于巨鹿；章邯降于殷墟。项羽率诸侯兵西进，坑秦降卒二十余万于新安，破函谷关，军鸿门，引兵屠咸阳。",
      "Song Yi and Xiang Yu marched north to relieve Zhao. When Song Yi waited forty-six days at Anyang without advancing, Xiang Yu killed him, crossed the Yellow River, sank his boats, broke his pots and routed the Qin army at Julu; Zhang Han surrendered at the ruins of Yin. Leading the allied armies west, Xiang Yu buried over 200,000 surrendered Qin soldiers alive at Xin'an, forced the Hangu Pass, camped at Hongmen and then sacked Xianyang.",
      [("彭城", "Pengcheng", 117.18, 34.27, -208, 9), ("安阳", "Anyang", 115.55, 34.83, -207, 10), ("巨鹿", "Julu", 115.0, 37.2, -207, 12),
       ("殷墟", "Ruins of Yin", 114.3, 36.12, -207, 7), ("新安", "Xin'an", 112.15, 34.73, -206, 11), ("函谷关", "Hangu Pass", 110.87, 34.63, -206, 12),
       ("鸿门", "Hongmen", 109.27, 34.38, -206, 12), ("咸阳", "Xianyang", 108.72, 34.37, -206, 12)]),
    R("还定三秦", "Retaking the Three Qins",
      "汉王用韩信计，自南郑出故道，袭雍王章邯于陈仓，围废丘，东至咸阳、栎阳，塞王司马欣、翟王董翳皆降。",
      "On Han Xin's plan the king of Han came out of Nanzheng by the Old Road, fell on Zhang Han, king of Yong, at Chencang and besieged Feiqiu, then moved east to Xianyang and Yueyang; Sima Xin, king of Sai, and Dong Yi, king of Di, both surrendered.",
      [("南郑", "Nanzheng", 107.03, 33.07, -206, 8), ("故道", "Gudao (Old Road)", 106.52, 33.91, -206, 8), ("陈仓", "Chencang", 107.37, 34.37, -206, 8),
       ("废丘", "Feiqiu", 108.42, 34.3, -206, 8), ("咸阳", "Xianyang", 108.72, 34.37, -206, 8), ("栎阳", "Yueyang", 109.23, 34.68, -206, 8)]),
    R("彭城之战·汉军东进", "Pengcheng: the Han advance",
      "汉王自临晋渡河，下河内，至洛阳为义帝发丧，率五诸侯兵五十六万东伐楚，四月入彭城，收其货宝美人，日置酒高会。",
      "The king of Han crossed the Yellow River at Linjin, took Henei and, at Luoyang, proclaimed mourning for the Righteous Emperor; leading 560,000 men of five allied lords east against Chu, he entered Pengcheng in the 4th month, seized its treasure and women, and feasted day after day.",
      [("临晋", "Linjin", 109.95, 34.8, -205, 3), ("河内", "Henei", 113.25, 35.1, -205, 3), ("洛阳", "Luoyang", 112.63, 34.72, -205, 3),
       ("外黄", "Waihuang", 114.9, 34.65, -205, 4), ("彭城", "Pengcheng", 117.18, 34.27, -205, 4)]),
    R("彭城之战·项羽回师", "Pengcheng: Xiang Yu's counterstroke",
      "项羽闻汉入彭城，留诸将击齐，自以精兵三万人南从鲁出胡陵，晨击汉军于萧，东至彭城，日中大破汉军；汉卒十余万人入睢水，水为之不流。",
      "Hearing that Han had entered Pengcheng, Xiang Yu left his generals to fight Qi and took 30,000 picked men south through Lu and out by Huling. He struck the Han army at Xiao at dawn, pressed east to Pengcheng and by midday had routed it; more than a hundred thousand Han soldiers were driven into the Sui River until it stopped flowing.",
      [("鲁", "Lu", 116.98, 35.59, -205, 4), ("胡陵", "Huling", 116.6, 35.05, -205, 4), ("萧", "Xiao", 116.95, 34.18, -205, 4),
       ("彭城", "Pengcheng", 117.18, 34.27, -205, 4), ("睢水", "Sui River", 117.55, 33.9, -205, 4)]),
    R("韩信北伐", "Han Xin's northern campaign",
      "韩信自临晋声言渡河，伏兵从夏阳以木罂渡军，袭安邑，虏魏豹；后九月破代于阏与；次年十月东下井陉，背水一战破赵；又东击齐，袭破历下，入临淄，十一月破龙且于潍水。",
      "Han Xin feinted a crossing at Linjin while his men crossed upstream at Xiayang on wooden jars, fell on Anyi and captured Wei Bao; in the intercalary 9th month he broke Dai at Yuyu; in the 10th month of the next year he came down Jingxing and, fighting with his back to the river, destroyed Zhao. He then struck east into Qi, overran Lixia, entered Linzi and in the 11th month beat Long Ju on the Wei River.",
      [("临晋", "Linjin", 109.95, 34.8, -205, 8), ("夏阳", "Xiayang", 110.45, 35.48, -205, 9), ("安邑", "Anyi", 111.18, 35.12, -205, 9),
       ("阏与", "Yuyu", 113.57, 37.33, -205, 9), ("井陉", "Jingxing", 114.05, 38.03, -204, 10), ("平原", "Pingyuan", 116.43, 37.17, -203, 10),
       ("历下", "Lixia", 117.0, 36.65, -203, 10), ("临淄", "Linzi", 118.35, 36.85, -203, 10), ("潍水", "Wei River", 119.35, 36.5, -203, 11)]),
    # ---------------- 西汉 ----------------
    R("卫青龙城", "Wei Qing to Longcheng",
      "元光六年，匈奴入上谷杀略吏民，汉遣四将军各将万骑出击：卫青以车骑将军出上谷，至龙城，斩首虏七百；公孙敖出代、李广出雁门皆败，公孙贺出云中无功。",
      "In Yuanguang 6, after the Xiongnu had raided Shanggu, killing and carrying off officials and people, Han sent four generals with ten thousand horsemen each against them. Wei Qing, as "
      "General of Chariots and Cavalry, went out from Shanggu to Longcheng and took seven hundred heads and prisoners; Gongsun Ao from Dai and Li "
      "Guang from Yanmen were both defeated, and Gongsun He from Yunzhong achieved nothing.",
      [("上谷", "Shanggu", 115.5, 40.4, -129, 3), ("", "", 115.2, 41.7, -129, 3), ("龙城", "Longcheng", 113.8, 43.6, -129, 3)]),
    R("卫青取河南", "Wei Qing takes the Ordos",
      "卫青出云中，沿河西行至高阙，南下至陇西，包抄河南匈奴，走白羊、楼烦王，遂取河南地，置朔方、五原郡。",
      "Wei Qing set out from Yunzhong, followed the river west to Gaoque and swept south to Longxi, enveloping the Xiongnu of the Ordos; he drove off the Baiyang and Loufan kings, took the Ordos and set up Shuofang and Wuyuan commanderies.",
      [("云中", "Yunzhong", 111.3, 40.3, -127, None), ("", "", 109.8, 40.8, -127, None), ("", "", 108.3, 41.0, -127, None),
       ("高阙", "Gaoque", 107.35, 41.15, -127, None), ("", "", 106.6, 40.0, -127, None), ("", "", 106.0, 38.5, -127, None),
       ("", "", 105.5, 37.0, -127, None), ("陇西", "Longxi", 104.5, 36.0, -127, None)]),
    R("卫青夜袭右贤王", "Wei Qing's night raid on the Wise King of the Right",
      "元朔五年春，卫青将三万骑出朔方高阙，诸将合十余万分道并出；北行六七百里，夜至右贤王庭围之，右贤王溃围北走，汉军俘裨王十余人、"
      "众万五千余口而还，卫青就军中拜大将军。",
      "In the spring of Yuanshuo 5 Wei Qing led 30,000 horsemen out from Gaoque in Shuofang, while the other generals, bringing the total to more than 100,000 men, "
      "advanced by separate roads. Six or seven hundred li to the north he reached the camp of the Wise King of the Right by night and surrounded "
      "it; the king broke out and fled north, and the Han army came back with more than ten lesser kings and over 15,000 captives. Wei Qing was "
      "made Grand General in the field.",
      [("高阙", "Gaoque", 107.35, 41.15, -124, 2), ("", "", 107.75, 42.0, -124, 2), ("右贤王庭", "Camp of the Wise King of the Right", 108.2, 42.8, -124, 2)]),
    R("卫青两出定襄", "Wei Qing's two sorties from Dingxiang",
      "元朔六年二月，大将军卫青率中、左、前、右、后、强弩六将军十余万骑出定襄，斩首三千余级，还师休士马于定襄、云中、雁门；四月复出定襄，"
      "斩首虏万余。前将军赵信、右将军苏建并军三千余骑独遇单于，战一日余，汉兵且尽，赵信降匈奴，苏建独身脱还。",
      "In the 2nd month of Yuanshuo 6 the Grand General Wei Qing led six generals and more than 100,000 horsemen out of Dingxiang, took over "
      "3,000 heads and fell back to rest his men and horses in Dingxiang, Yunzhong and Yanmen; in the 4th month he went out from Dingxiang again "
      "and took over 10,000 heads and prisoners. The General of the Van, Zhao Xin, and the General of the Right, Su Jian, whose combined force of more than 3,000 horsemen ran into the "
      "chanyu on their own, fought for more than a day until their men were nearly all gone; Zhao Xin went over to the Xiongnu and Su Jian escaped alone.",
      [("定襄", "Dingxiang", 111.65, 40.4, -123, 2), ("", "", 111.4, 41.6, -123, 4), ("漠南", "South of the Gobi", 111.0, 42.6, -123, 4)]),
    R("霍去病八百骑", "Huo Qubing's eight hundred",
      "同年四月，年十八的剽姚校尉霍去病与轻勇骑八百，弃大军数百里赴利，斩首虏二千零二十八级，斩单于大父行籍若侯产，生捕季父罗姑比，功冠全军，封冠军侯。",
      "In the 4th month of the same year Huo Qubing, the eighteen-year-old Piaoyao Colonel, rode with eight hundred light horse several hundred "
      "li ahead of the main army, took 2,028 heads and prisoners, killed Chan, Marquis of Jiruo, a member of the chanyu's grandfather's "
      "generation, and captured the chanyu's uncle Luogubi; his feat outshone the whole army, and he was made Marquis of Guanjun.",
      [("定襄", "Dingxiang", 111.65, 40.4, -123, 4), ("", "", 111.3, 41.8, -123, 4), ("", "", 110.6, 42.9, -123, 4),
       ("深入数百里", "Several hundred li ahead", 110.0, 43.6, -123, 4)]),
    R("霍去病河西·春", "Huo Qubing in Hexi: spring",
      "元狩二年春，霍去病将万骑出陇西，转战六日，过焉支山千余里，杀折兰王、卢胡王，获休屠王祭天金人。",
      "In the spring of 121 BC Huo Qubing led ten thousand horsemen out of Longxi, fought for six days and pushed over a thousand li past Mount Yanzhi, killing the Zhelan and Luhu kings and taking the golden statue the Xiutu king used to worship Heaven.",
      [("陇西", "Longxi", 103.86, 35.38, -121, 3), ("", "", 102.9, 36.65, -121, 3), ("", "", 102.0, 37.8, -121, 3),
       ("焉支山", "Mount Yanzhi", 101.4, 38.45, -121, 3)]),
    R("霍去病河西·夏", "Huo Qubing in Hexi: summer",
      "同年夏，霍去病出北地，逾居延泽，南下经小月氏，攻祁连山，得酋涂王，斩首虏三万二百级，获五王、五王母、单于阏氏、王子五十九人，相国、将军、当户、都尉六十三人；秋，浑邪王杀休屠王，率四万余人降汉，河西归汉。",
      "That summer Huo Qubing set out from Beidi, passed Lake Juyan, turned south through the Lesser Yuezhi lands and struck at the Qilian Mountains, where he took the Qiutu king and 30,200 heads and "
      "prisoners, capturing five kings and five kings' mothers, the chanyu's consort, fifty-nine princes and sixty-three chancellors, generals, "
      "danghu and commandants. In the autumn the Hunye king killed the Xiutu king and surrendered with over 40,000 people, and Hexi passed to Han.",
      [("北地", "Beidi", 107.6, 36.3, -121, 6), ("", "", 105.8, 38.8, -121, 6), ("", "", 103.2, 40.6, -121, 6),
       ("居延泽", "Lake Juyan", 101.0, 41.9, -121, 6), ("", "", 99.9, 40.4, -121, 6), ("祁连山", "Qilian Mountains", 98.6, 39.3, -121, 6)]),
    R("卫青漠北", "Wei Qing beyond the Gobi",
      "卫青出定襄，北行千余里，遇伊稚斜单于陈兵以待，以武刚车环为营，纵五千骑往击；日暮大风扬沙，汉益纵左右翼绕单于，单于溃围西北走。"
      "卫青追二百余里不及，至窴颜山赵信城，取其积粟食军，留一日，悉烧余粟而还。前将军李广、右将军赵食其并军出东道，惑失道，后大将军，李广引刀自刭。",
      "Wei Qing set out from Dingxiang and marched over a thousand li north, where the chanyu Yizhixie was drawn up waiting. Circling his armoured "
      "wagons into a laager, he loosed five thousand horse at him; at dusk a gale threw up the sand, Han sent its wings round the chanyu, and he "
      "broke out to the north-west. Wei Qing pursued for over two hundred li without catching him, reached Zhao Xin's fort at Mount Tianyan, fed "
      "his army on the grain stored there, stayed one day, burned the rest and turned back. Li Guang, General of the Van, and Zhao Shiqi, General of the Right, sent together by the eastern "
      "road, lost their way and arrived after the battle; Li Guang cut his own throat.",
      [("定襄", "Dingxiang", 111.65, 40.4, -119, None), ("", "", 110.8, 42.5, -119, None), ("", "", 108.5, 44.5, -119, None),
       ("", "", 105.5, 46.0, -119, None), ("窴颜山赵信城", "Zhao Xin's fort, Mount Tianyan", 103.2, 46.8, -119, None)]),
    R("霍去病漠北", "Huo Qubing beyond the Gobi",
      "霍去病出代二千余里，绝大幕，历涉离侯，济弓闾，破左贤王，斩首虏七万余，获屯头王、韩王等三人及将军、相国、当户、都尉八十三人，封狼居胥山，禅于姑衍，登临翰海而还。弓闾一般认为即弓卢水"
      "（克鲁伦河）；翰海所指诸说不一，这里取贝加尔湖说。",
      "Huo Qubing marched more than two thousand li from Dai, crossed the great desert, passed Lihou and crossed the Gonglü, broke the Wise King of "
      "the Left and took over 70,000 heads and prisoners, capturing three kings, among them the Xiongnu kings of Tuntou and Han, and eighty-three generals, "
      "chancellors, danghu and commandants; he sacrificed to Heaven on Mount Langjuxu and to Earth on Mount Guyan, climbed to look out "
      "over the Hanhai and turned back. The Gonglü is usually taken to be the Gonglu River (Kherlen); views differ on what the Hanhai was, and the "
      "map follows the Lake Baikal identification.",
      [("代郡", "Dai", 114.57, 39.84, -119, None), ("", "", 114.2, 42.0, -119, None), ("", "", 112.8, 44.6, -119, None),
       ("弓闾", "Gonglü", 110.7, 47.3, -119, None), ("狼居胥山", "Mount Langjuxu", 108.9, 48.6, -119, None),
       ("姑衍山", "Mount Guyan", 107.1, 48.15, -119, None), ("", "", 106.0, 49.9, -119, None), ("瀚海", "Hanhai", 104.9, 51.5, -119, None)]),
    R("张骞西使·去程", "Zhang Qian's journey west: outbound",
      "张骞出陇西，过河西为匈奴所得，留十余年；乘间西走，经大宛、康居至大月氏，又至大夏，留岁余。",
      "Zhang Qian went out through Longxi and was caught by the Xiongnu as he crossed Hexi; they held him for over ten years. He slipped away west through Dayuan and Kangju to the Great Yuezhi and on to Daxia, where he stayed a year and more.",
      [("长安", "Chang'an", 108.88, 34.31, -139, None), ("陇西", "Longxi", 103.86, 35.38, -139, None), ("河西", "Hexi", 100.4, 39.0, -139, None),
       ("", "", 94.7, 40.1, -129, None), ("", "", 86.6, 42.0, -129, None), ("", "", 83.0, 41.7, -129, None), ("", "", 76.0, 39.5, -129, None),
       ("大宛", "Dayuan", 71.6, 40.5, -129, None), ("康居", "Kangju", 69.2, 41.3, -129, None), ("大月氏", "Great Yuezhi", 67.6, 37.8, -128, None),
       ("大夏", "Daxia", 66.9, 36.75, -128, None)]),
    R("张骞西使·归程", "Zhang Qian's journey west: return",
      "张骞并南山，欲从羌中归，复为匈奴所得，留岁余；军臣单于死，匈奴国内乱，张骞乘机逃归长安。",
      "Zhang Qian went home along the Southern Mountains, meaning to pass through the Qiang lands, but was caught again by the Xiongnu and held for over a year; when the chanyu Junchen died and the Xiongnu fell into turmoil he escaped to Chang'an.",
      [("大夏", "Daxia", 66.9, 36.75, -128, None), ("", "", 71.0, 36.8, -128, None), ("", "", 75.2, 37.8, -128, None), ("", "", 77.2, 38.4, -128, None),
       ("于阗", "Khotan", 79.93, 37.1, -128, None), ("", "", 85.5, 38.1, -128, None), ("楼兰", "Loulan", 88.17, 39.03, -128, None),
       ("羌中", "Qiang lands", 94.0, 36.4, -127, None), ("陇西", "Longxi", 103.86, 35.38, -126, None), ("长安", "Chang'an", 108.88, 34.31, -126, None)]),
    R("路博德伐南越", "Lu Bode against Nanyue",
      "南越相吕嘉反，杀其王及汉使。伏波将军路博德出桂阳，下湟水，与杨仆会师，俱进番禺，元鼎六年冬破番禺，南越亡。",
      "When Lü Jia, chancellor of Nanyue, rebelled and killed his king and the Han envoys, Lu Bode, General Who Calms the Waves, set out from Guiyang, went down the Huang River and joined Yang Pu, advancing with him on Panyu; Panyu fell in the winter of 111 BC and Nanyue fell with it.",
      [("桂阳", "Guiyang", 113.02, 25.8, -112, None), ("", "", 112.75, 24.75, -112, None), ("湟水", "Huang River", 113.05, 24.15, -111, None),
       ("番禺", "Panyu", 113.27, 23.13, -111, None)]),
    R("杨仆伐南越", "Yang Pu against Nanyue",
      "楼船将军杨仆出豫章，越横浦关，下浈水，先陷寻陕、石门，率精卒先至番禺，纵火烧城。",
      "Yang Pu, General of the Towered Ships, set out from Yuzhang, crossed the Hengpu Pass and went down the Zhen River, took Xunxia and Shimen first and reached Panyu ahead of the others with his picked troops, setting the city on fire.",
      [("豫章", "Yuzhang", 115.89, 28.68, -112, None), ("", "", 114.9, 26.8, -112, None), ("横浦关", "Hengpu Pass", 114.33, 25.33, -112, None),
       ("", "", 113.6, 24.8, -111, None), ("石门", "Shimen", 113.25, 23.3, -111, None), ("番禺", "Panyu", 113.27, 23.13, -111, None)]),
    R("杨仆伐朝鲜", "Yang Pu against Joseon",
      "元封二年秋，楼船将军杨仆自齐浮渤海，率齐兵七千先至王险城下，为朝鲜所败，收散卒；次年与左将军荀彘合围，夏，朝鲜相杀其王右渠来降。",
      "In the autumn of 109 BC Yang Pu, General of the Towered Ships, sailed from Qi across the Bohai and reached Wangxian first with seven thousand men of Qi, but was beaten and had to regather his scattered men; the next year he and Xun Zhi, General of the Left, besieged the city together, and in the summer Joseon ministers killed their king Ugeo and surrendered.",
      [("东莱", "Donglai", 120.4, 37.6, -109, None), ("", "", 122.4, 38.4, -109, None), ("列口", "Liekou", 125.25, 38.7, -109, None),
       ("王险城", "Wangxian", 125.72, 39.05, -108, None)]),
    R("荀彘伐朝鲜", "Xun Zhi against Joseon",
      "左将军荀彘将燕、代卒出辽东，初击浿水西军不能破，后破浿水上军，进至王险城下，围其西北。",
      "Xun Zhi, General of the Left, led troops of Yan and Dai out of Liaodong; he failed at first against the Joseon army west of the Pae River, then broke the force on the river, reached Wangxian and besieged it from the north-west.",
      [("襄平", "Xiangping", 123.17, 41.27, -109, None), ("", "", 124.4, 40.15, -109, None), ("", "", 125.3, 39.65, -108, None),
       ("王险城", "Wangxian", 125.72, 39.05, -108, None)]),
    R("李广利伐大宛", "Li Guangli against Dayuan",
      "贰师将军李广利再伐大宛，率六万人出敦煌，过盐泽，屠轮台，西越葱岭北麓，围贵山城四十余日，宛贵人杀其王毋寡请降，汉立昧蔡为王；别将上官桀攻破郁成。",
      "On his second campaign against Dayuan, the Ershi General Li Guangli led 60,000 men out of Dunhuang past the Salt Marsh, sacked Luntai, crossed the northern flank of the Pamirs and besieged Guishan for over forty days, until the nobles of Dayuan killed their king Wugua and surrendered; Han installed Meicai as king. A detachment under Shangguan Jie took Yucheng.",
      [("敦煌", "Dunhuang", 94.7, 40.1, -102, None), ("盐泽", "Salt Marsh", 90.5, 40.5, -102, None), ("", "", 86.2, 41.4, -102, None),
       ("轮台", "Luntai", 84.25, 41.8, -102, None), ("", "", 83.0, 41.7, -101, None), ("", "", 80.3, 41.2, -101, None), ("", "", 76.0, 39.5, -101, None),
       ("", "", 73.5, 40.5, -101, None), ("贵山城", "Guishan", 71.6, 40.5, -101, None)]),
    R("陈汤击郅支", "Chen Tang against Zhizhi",
      "西域副校尉陈汤矫诏发西域诸国兵与屯田吏士四万余人，与都护甘延寿分两道：三校从南道越葱岭、经大宛，三校从北道入赤谷、过乌孙，会于康居，围郅支城，斩郅支单于。",
      "Chen Tang, Deputy Colonel of the Western Regions, forged an edict to raise over 40,000 men from the oasis states and the garrison farms, and with the Protector-General Gan Yanshou marched in two columns — three regiments over the Pamirs by the southern road through Dayuan, three by the northern road through Chigu and Wusun — to meet in Kangju, besiege Zhizhi's fortress and behead the chanyu.",
      [("乌垒", "Wulei", 84.6, 41.75, -36, None), ("温宿", "Wensu", 79.2, 41.2, -36, None), ("赤谷", "Chigu", 78.4, 42.2, -36, None),
       ("", "", 75.5, 42.6, -36, None), ("", "", 73.5, 42.8, -36, None), ("郅支城", "Zhizhi's fortress", 71.4, 42.9, -36, None)]),
    # ---------------- 两汉之际、东汉 ----------------
    R("刘秀徇河北", "Liu Xiu in Hebei",
      "更始元年十月，刘秀以破虏将军行大司马事持节北渡河，镇慰河北州郡，至邯郸、真定，北上蓟；王郎在邯郸称帝，悬赏购之，刘秀自蓟南逃，经饶阳、下曲阳渡滹沱河，至信都，收兵反攻，次年五月破邯郸、诛王郎。建武元年六月即位于鄗，十月入洛阳。",
      "In the 10th month of AD 23 Liu Xiu crossed the Yellow River as acting Grand Marshal with the Gengshi emperor's tally to win over the commanderies of Hebei, passing through Handan and Zhending and north to Ji. When Wang Lang proclaimed himself emperor at Handan and put a price on his head, Liu Xiu fled south from Ji through Raoyang and Xiaquyang, crossed the Hutuo River and reached Xindu, where he raised troops and struck back, taking Handan and killing Wang Lang in the 5th month of 24. He took the throne at Hao in the 6th month of 25 and entered Luoyang in the 10th.",
      [("洛阳", "Luoyang", 112.63, 34.72, 23, 10), ("邯郸", "Handan", 114.48, 36.6, 23, 11), ("真定", "Zhending", 114.57, 38.15, 23, 12),
       ("卢奴", "Lunu", 115.0, 38.85, 24, 1), ("蓟", "Ji", 116.35, 39.88, 24, 1), ("饶阳", "Raoyang", 115.73, 38.23, 24, 1),
       ("下曲阳", "Xiaquyang", 114.98, 38.03, 24, 1), ("信都", "Xindu", 115.57, 37.56, 24, 2), ("柏人", "Boren", 114.65, 37.45, 24, 4),
       ("邯郸", "Handan", 114.48, 36.6, 24, 5), ("鄗", "Hao", 114.75, 37.65, 25, 6), ("洛阳", "Luoyang", 112.63, 34.72, 25, 10)]),
    R("岑彭吴汉伐蜀", "Cen Peng and Wu Han against Shu",
      "建武十一年，岑彭率舟师攻破荆门、虎牙，溯江入江关，至江州，倍道兼行二千余里至武阳，为公孙述所遣刺客所杀；次年吴汉继进，破广都，围成都，十一月公孙述伤重而死，蜀平。",
      "In AD 35 Cen Peng's fleet broke the barrier at Jingmen and Huya, sailed up the Yangzi through the Jiang Pass to Jiangzhou and drove on over two thousand li to Wuyang, where he was murdered by an assassin sent by Gongsun Shu; the next year Wu Han pressed on, took Guangdu and besieged Chengdu, and in the 11th month Gongsun Shu died of his wounds and Shu was won.",
      [("荆门", "Jingmen", 111.4, 30.6, 35, None), ("江关", "Jiang Pass", 109.5, 31.0, 35, None), ("江州", "Jiangzhou", 106.55, 29.56, 35, None),
       ("", "", 104.7, 29.8, 35, None), ("武阳", "Wuyang", 103.85, 30.3, 35, None), ("广都", "Guangdu", 104.05, 30.5, 36, None),
       ("成都", "Chengdu", 104.07, 30.66, 36, None)]),
    R("马援南征", "Ma Yuan's southern campaign",
      "征侧、征贰起兵，岭南六十余城响应。伏波将军马援自合浦缘海而进，随山刊道千余里，破征侧于浪泊，次年斩之，进击九真余部至居风。",
      "When the Trưng sisters rose and more than sixty towns south of the Five Ranges joined them, Ma Yuan, General Who Calms the Waves, advanced from Hepu along the coast, cutting a road through the hills for over a thousand li, beat Trưng Trắc at Langbo, beheaded her the next year and pursued the remnants in Jiuzhen as far as Jufeng.",
      [("合浦", "Hepu", 109.2, 21.7, 42, None), ("", "", 108.2, 21.6, 42, None), ("", "", 107.0, 21.4, 42, None),
       ("浪泊", "Langbo", 105.95, 21.2, 42, None), ("居风", "Jufeng", 105.75, 19.85, 43, None)]),
    R("班超经营西域", "Ban Chao in the Western Regions",
      "永平十六年班超以假司马随窦固击伊吾，旋率吏士三十六人出使：在鄯善夜袭匈奴使者，鄯善降；至于阗，斩巫，于阗王广德杀匈奴使者而降；明年春至疏勒，"
      "执龟兹所立的疏勒王兜题。76 年都护罢后，超还疏勒坚守，78 年率疏勒、康居、于阗、拘弥兵一万攻破姑墨石城，87 年发于阗诸国兵二万五千破莎车，"
      "91 年为都护，居龟兹它乾城，94 年发八国兵七万讨平焉耆。超在西域三十一年，102 年东归，同年卒。",
      "In Yongping 16 Ban Chao, an acting major, fought under Dou Gu at Yiwu and was then sent west with thirty-six men. At Shanshan he fell on "
      "the Xiongnu envoys by night and Shanshan submitted; at Khotan he beheaded a shaman, and King Guangde killed the Xiongnu envoys and "
      "submitted; the next spring he reached Kashgar and seized Douti, the king Kucha had imposed there. After the Protectorate was abandoned in "
      "76 he went back to hold Kashgar; in 78 he led 10,000 men from Kashgar, Kangju, Khotan and Jumi to storm the stone fort of Gumo, in 87 he "
      "took Yarkand with 25,000 men from Khotan and its neighbours, in 91 he became Protector-General at Tuoqian in Kucha, and in 94 he crushed "
      "Karasahr with 70,000 men from eight states. He spent thirty-one years in the Western Regions and went home in 102, dying the same year.",
      [("伊吾卢", "Yiwulu", 93.5, 42.8, 73, 2), ("鄯善", "Shanshan", 88.17, 39.03, 73, None), ("于阗", "Khotan", 79.93, 37.1, 73, None),
       ("疏勒", "Kashgar", 75.98, 39.47, 74, 3), ("姑墨", "Gumo", 80.27, 41.17, 78, None), ("莎车", "Yarkand", 77.25, 38.42, 87, None),
       ("它乾城", "Tuoqian", 82.65, 41.6, 91, None), ("焉耆", "Karasahr", 86.57, 42.05, 94, 7)]),
    R("耿恭还玉门", "Geng Gong's return to the Jade Gate",
      "建初元年正月，援军破车师于交河城，军吏范羌领兵二千越天山，雪深丈余，至疏勒城迎耿恭。耿恭余众随之东归，虏兵追之，且战且行，"
      "发疏勒时尚有二十六人，随路死没，三月至玉门，唯余十三人，衣屦穿决，形容枯槁。",
      "In the 1st month of Jianchu 1, after the relief army had broken Jushi at Jiaohe, the officer Fan Qiang took 2,000 men over the Tianshan "
      "through snow more than a zhang deep to bring out Geng Gong from the fort of Shule. Geng Gong and his remaining men went east with Fan Qiang, fighting off "
      "the pursuing enemy as they marched; twenty-six of them left Shule, men died along the way, and when they reached the Jade Gate in the 3rd month "
      "only thirteen were left, their clothes and shoes in tatters and their faces gaunt.",
      [("疏勒城", "Shule fort", 89.7, 43.8, 76, 1), ("", "", 89.4, 43.3, 76, 2), ("柳中", "Liuzhong", 89.7, 42.9, 76, 2),
       ("", "", 91.6, 42.4, 76, 3), ("", "", 93.0, 41.3, 76, 3), ("玉门关", "Jade Gate", 93.87, 40.35, 76, 3)]),
    R("窦宪燕然", "Dou Xian to Yanran",
      "车骑将军窦宪与南单于等分三道出塞，自出鸡鹿塞，会诸军于涿邪山，大破北单于于稽落山，追至私渠比鞮海，登燕然山，令班固作铭，刻石记功而还。",
      "Dou Xian, General of Chariots and Cavalry, went out beyond the frontier in three columns with the southern chanyu; he set out himself from the Jilu frontier post, joined the other columns at Mount Zhuoye, crushed the northern chanyu at Mount Jiluo, pursued him to Lake Siqubiti, then climbed Mount Yanran, had Ban Gu compose an inscription and carved it in the rock before turning back.",
      [("鸡鹿塞", "Jilu frontier post", 106.6, 41.25, 89, None), ("涿邪山", "Mount Zhuoye", 104.5, 43.0, 89, None), ("稽落山", "Mount Jiluo", 102.0, 44.6, 89, None),
       ("", "", 103.6, 45.35, 89, None), ("燕然山", "Mount Yanran", 104.554, 45.178, 89, None)]),
]


# ---------------- 山川：新增与改动 ----------------
# 新增：(类别, 细类, 古名, 英文古名, 线, 注记点, 今名, 英文今名, 说明, 英文说明)；线为 None 的只有注记（瀚海）
PHYS_NEW = [
    ("range", None, "狼居胥山", "Mount Langjuxu", [[107.6, 48.0], [108.4, 48.5], [109.2, 48.9], [110.0, 49.3]], [108.9, 48.75],   # 与宋元、民国卷的肯特山同一画法
     "肯特山", "Khentii Mountains",
     "前119 年霍去病破左贤王，于此「封」（筑坛祭天）。一般认为即今蒙古国肯特山，也有在今内蒙古境内诸说。",
     "Where Huo Qubing performed the feng sacrifice to Heaven in 119 BC after crushing the Wise King of the Left. Usually identified with the "
     "Khentii Mountains in Mongolia, though some place it in today's Inner Mongolia."),
    ("range", None, "姑衍山", "Mount Guyan", [[106.75, 48.05], [107.1, 48.15], [107.45, 48.25]], [107.1, 48.15],
     "地望不详，在狼居胥山附近", "location unknown, near Mount Langjuxu",
     "霍去病封狼居胥后「禅于姑衍」（除地祭地）。今地不详，一般认为在狼居胥山附近，图上为示意。",
     "After the sacrifice on Mount Langjuxu, Huo Qubing performed the shan sacrifice to Earth on Mount Guyan. Its modern location is unknown; it is "
     "generally placed near Mount Langjuxu, and the map shows it only schematically."),
    ("range", None, "燕然山", "Mount Yanran", [[104.25, 45.1], [104.55, 45.2], [104.95, 45.32]], [104.62, 45.26],
     "德勒格尔杭爱山", "Delgerkhangai hills",
     "汉代的燕然山。89 年窦宪大破北单于后登此山，令班固作铭、刻石记功；2017 年中蒙联合考察队在蒙古国中戈壁省德勒格尔杭爱的山崖上辨认出"
     "《封燕然山铭》摩崖，燕然山的位置由此确定。",
     "The Han dynasty's Mount Yanran. Dou Xian climbed it in 89 after crushing the northern chanyu and had Ban Gu's inscription carved here; in "
     "2017 a joint Chinese–Mongolian survey identified the cliff inscription at Delgerkhangai in Dundgovi Province, Mongolia, fixing where Mount "
     "Yanran was."),
    ("range", None, "焉支山", "Mount Yanzhi", [[101.05, 38.32], [101.4, 38.45], [101.75, 38.56]], [101.4, 38.45],
     "焉支山（大黄山）", "Mount Yanzhi (Dahuang Shan)",
     "河西走廊中段，山丹、永昌之间。前121 年春霍去病过焉支山千余里。匈奴失此山，歌曰「失我焉支山，使我妇女无颜色」。",
     "In the middle of the Hexi Corridor, between Shandan and Yongchang. In the spring of 121 BC Huo Qubing pressed more than a thousand li past it. "
     "Losing it, the Xiongnu sang, 'We have lost our Mount Yanzhi, and our women have lost their colour.'"),
    ("river", "lake", "瀚海", "Hanhai", None, [105.0, 51.85],
     "贝加尔湖南部（一说）", "southern Lake Baikal (one view)",
     "霍去病封狼居胥、禅姑衍之后「登临翰海」而还。翰海所指说法不一：一说即贝加尔湖，一说呼伦湖，一说杭爱山，也有人认为泛指漠北的大湖；"
     "图上取贝加尔湖说。后世「饮马瀚海」即用此典；以「瀚海」专指戈壁沙漠是明代以后的用法。",
     "After the sacrifices on Mount Langjuxu and Mount Guyan, Huo Qubing 'climbed to look out over the Hanhai' and turned back. What the Hanhai "
     "was is disputed: Lake Baikal, Lake Hulun and the Khangai Mountains have all been proposed, and some take it as any great lake beyond the "
     "Gobi; the map follows the Lake Baikal view. Later writers' 'watering horses at the Hanhai' alludes to this; using 'Hanhai' as the standard name for the Gobi "
     "dates only from the Ming."),
]

PHYS_MAJOR = {"狼居胥山", "燕然山"}       # 缩小时也标出来

# 底图（汉末卷）条目的改动：古名 → None（本卷不画）或要改的字段
BASE_EDIT = {
    "毛乌素沙地": None,          # 大片流沙唐中后期（822 年首见记载）才出现，本卷不画
    "燕然山": dict(old="杭爱山", eold="Khangai Mountains",
                note="蒙古高原西部的主脉。汉代的燕然山一般认为是其东南的余脉：2017 年在蒙古国中戈壁省德勒格尔杭爱找到了《封燕然山铭》摩崖（见「燕然山」）。",
                enote="The main range of the western Mongolian plateau. The Han dynasty's Mount Yanran is generally taken to be an outlier to its "
                      "south-east: in 2017 the cliff inscription for the feng sacrifice on Mount Yanran was found at Delgerkhangai in Dundgovi "
                      "Province, Mongolia (see Mount Yanran)."),
    "大漠（瀚海）": dict(old="大漠", eold="Great Desert",
                   note="汉人称「幕」「大幕」，卫青、霍去病「绝幕」北击匈奴即穿越此漠。以「瀚海」专指戈壁是明代以后的事。",
                   enote="The Han called it the mu or the Great Mu; when Wei Qing and Huo Qubing 'crossed the mu' to strike north at the Xiongnu, "
                         "this was the desert they crossed. 'Hanhai' became the standard name for the Gobi only from the Ming."),
    "北海": dict(note="匈奴北境的大湖。前100 年苏武出使匈奴被扣，单于徙之北海上无人处牧羊（见「苏武牧羊」）。湖的南部一说即霍去病「登临翰海」之地（见「瀚海」）。",
               enote="The great lake on the northern edge of the Xiongnu lands. Su Wu, detained by the Xiongnu in 100 BC, was sent to herd sheep in "
                     "an empty land by the North Sea (see Su Wu herds sheep). On one view, followed by this map, its southern part is the Hanhai over which Huo "
                     "Qubing climbed to look out (see Hanhai)."),
    "祁连山": dict(note="颜师古注：「匈奴谓天为祁连。」前121 年夏霍去病逾居延至祁连山，大破匈奴。匈奴失祁连、焉支二山，歌曰「亡我祁连山，使我六畜不蕃息」。",
                enote="Yan Shigu notes that 'the Xiongnu call Heaven qilian'. In the summer of 121 BC Huo Qubing passed Juyan and reached the Qilian "
                      "Mountains, crushing the Xiongnu. Having lost the Qilian and Yanzhi mountains, the Xiongnu sang, 'We have lost our Qilian "
                      "Mountains, and our herds no longer thrive.'"),
    "阴山": dict(note="漠南的屏障，匈奴依以为苑囿。前127 年卫青收河南地，复缮秦塞；侯应称匈奴失阴山之后，「过之未尝不哭也」。",
               enote="The barrier south of the Gobi, which the Xiongnu used as their hunting park. After Wei Qing recovered the Ordos in 127 BC the "
                     "Qin frontier was repaired; Hou Ying said that after losing the Yin Mountains the Xiongnu 'never passed them without weeping'."),
    "蒗荡渠（鸿沟）": dict(old="鸿沟（狼汤渠）", eold="Honggou Canal (Langtang Canal)",
                      geo=[[113.45, 34.9], [113.95, 34.8], [114.35, 34.8], [114.55, 34.45], [114.75, 34.05], [114.88, 33.73], [115.0, 33.45]],
                      note="战国魏惠王时（前360 年起）开凿，自荥阳引河水东经大梁，南下至陈入颍，沟通河、淮；《汉书·地理志》称狼汤渠，北魏《水经注》"
                           "作蒗荡渠。前203 年楚汉相持日久，项羽与汉约「中分天下，割鸿沟以西者为汉，鸿沟而东者为楚」，归还太公、吕后引兵东归；"
                           "汉王用张良、陈平之计背约追击，次年垓下灭楚。后世象棋盘上的「楚河汉界」一般认为即由此而来。走向与战国卷相同。",
                      enote="Dug from 360 BC under King Hui of Wei, it drew water from the Yellow River at Xingyang, ran east past Daliang and then "
                            "south to Chen, where it joined the Ying, linking the Yellow River and the Huai. The treatise on geography in the Hanshu "
                            "calls it the Langtang Canal, and the Northern Wei Commentary on the Water Classic the Langdang Canal. In 203 BC, after "
                            "a long stand-off between Chu and Han, Xiang Yu agreed with Han to 'divide the realm in two, the land west of the Honggou to Han and the "
                            "land east of it to Chu', handed back the king of Han's father and wife and marched his army east; on the advice of Zhang "
                            "Liang and Chen Ping the king of Han broke the agreement and pursued him, destroying Chu at Gaixia the next year. The "
                            "'Chu river, Han border' across the middle of the Chinese chessboard is generally thought to come from this. Drawn along "
                            "the same course as in the Warring States volume."),
    "弓卢水": dict(note="霍去病「济弓闾」，弓闾一般认为即弓卢水。",
                enote="Huo Qubing 'crossed the Gonglü', which is usually taken to be the Gonglu River."),
}
