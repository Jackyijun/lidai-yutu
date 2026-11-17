# -*- coding: utf-8 -*-
"""节点的年号、标题、短标题、说明（中英）。首尾两个节点的文字由 src/build.py 从邻卷照搬，这里只占位。"""
from texts2 import TEXT2

TEXT = {
    "q212": dict(era="秦始皇三十五年", era_en="First Emperor of Qin, year 35", t="", te="", sh="", she="", d="", de=""),

    "q209a": dict(era="秦二世元年七月", era_en="Second Emperor of Qin, year 1, 7th month",
                  t="大泽乡起事·张楚", te="Uprising at Dazexiang · Zhang Chu", sh="大泽乡", she="Dazexiang",
                  d="前210 年七月始皇崩于沙丘，赵高、李斯矫诏赐死扶苏，立胡亥为二世，蒙恬被逼自杀。二世元年七月，戍卒陈胜、吴广屯大泽乡，遇雨失期，"
                    "斩尉起事，攻下蕲、铚、酂、苦、柘、谯，入陈，陈胜自立为王，号张楚。北边戍卒散去，匈奴渐复度河南。",
                  de="The First Emperor died at Shaqiu in the 7th month of 210 BC; Zhao Gao and Li Si forged an order for Fusu to kill himself and set up Huhai "
                     "as Second Emperor, and Meng Tian was forced to take his own life. In the 7th month of the Second Emperor's first year the conscripts "
                     "Chen Sheng and Wu Guang, held up by rain at Dazexiang and unable to arrive on time, killed their officers and rose, taking Qi, "
                     "Zhi, Cuo, Ku, Zhe and Qiao and entering Chen, where Chen Sheng made himself king of Zhang Chu. With the northern garrisons breaking up, "
                     "the Xiongnu began to cross back into the Ordos."),
    "q209b": dict(era="二世元年九月", era_en="Second Emperor, year 1, 9th month",
                  t="六国复起", te="The six states rise again", sh="六国复起", she="Six states",
                  d="张楚遣将四出：吴广围荥阳，周文西入关至戏，武臣北略赵地，周巿略魏地，邓宗徇九江。八月武臣自立为赵王；九月韩广自立为燕王，"
                    "田儋杀狄令自立为齐王。同月项梁、项羽杀会稽守殷通起兵，刘邦起于沛，称沛公。秦遣少府章邯赦骊山徒击周文。",
                  de="Zhang Chu sent its generals out in all directions: Wu Guang besieged Xingyang, Zhou Wen went west through the passes as far as Xi, "
                     "Wu Chen went north to take the Zhao lands, Zhou Fu the Wei lands and Deng Zong Jiujiang. In the 8th month Wu Chen made himself king of Zhao; in the "
                     "9th Han Guang made himself king of Yan and Tian Dan killed the magistrate of Di and made himself king of Qi. In the same month Xiang "
                     "Liang and Xiang Yu killed Yin Tong, Administrator of Kuaiji, and raised troops, and Liu Bang rose at Pei as Lord of Pei. Qin sent the Privy "
                     "Treasurer Zhang Han with an army of pardoned Lishan labourers against Zhou Wen."),
    "q208a": dict(era="二世二年十二月", era_en="Second Emperor, year 2, 12th month",
                  t="陈胜败死", te="Chen Sheng killed", sh="陈胜死", she="Chen Sheng dies",
                  d="章邯破周文于曹阳、渑池，吴广为部将田臧所杀，荥阳之围解。十二月章邯攻陈，陈胜败走，至下城父为御者庄贾所杀，张楚瓦解。"
                    "赵王武臣为部将李良所杀，张耳、陈余立赵歇为赵王；周巿立魏公子咎为魏王，都临济。张楚余部秦嘉立景驹为楚王。",
                  de="Zhang Han broke Zhou Wen at Caoyang and Mianchi, Wu Guang was killed by his officer Tian Zang and the siege of Xingyang was lifted. In "
                     "the 12th month Zhang Han attacked Chen; Chen Sheng fled and was killed at Xiachengfu by his charioteer Zhuang Jia, and Zhang Chu "
                     "collapsed. Wu Chen, king of Zhao, was killed by his general Li Liang, and Zhang Er and Chen Yu set up Zhao Xie as king of Zhao; Zhou "
                     "Fu set up Prince Jiu of Wei as king of Wei at Linji. Qin Jia, of Zhang Chu's remnant forces, made Jing Ju king of Chu."),
    "q208b": dict(era="二世二年六月", era_en="Second Emperor, year 2, 6th month",
                  t="立楚怀王", te="King Huai of Chu installed", sh="立怀王", she="King Huai",
                  d="项梁渡江北上，并陈婴、英布、蒲将军之众，击杀秦嘉，景驹走死梁地，刘邦来属。章邯破临济，魏王咎自焚，救魏的齐王田儋战死。六月项梁用范增之计，"
                    "于盱台立楚怀王之孙心为楚王，仍号怀王；又立韩公子成为韩王，张良为司徒。齐人立田假为王，田荣不服。",
                  de="Xiang Liang crossed the Yangzi and moved north, absorbing the forces of Chen Ying, Ying Bu and General Pu, killing Qin Jia, while Jing Ju fled and died in Liang; "
                     "Liu Bang joined him. Zhang Han took Linji, the king of Wei burned himself to death and Tian Dan, king of Qi, who had come to Wei's aid, "
                     "fell in battle. In the 6th month, on Fan Zeng's advice, Xiang Liang set up Xin, grandson of King Huai of Chu, as king of Chu at Xuyi, "
                     "still styled King Huai, and made Cheng, a prince of Han (韓), king of Han with Zhang Liang as minister. The men of Qi set up Tian Jia as king, "
                     "which Tian Rong would not accept."),
    "q208c": dict(era="二世二年九月", era_en="Second Emperor, year 2, 9th month",
                  t="定陶之战", te="Battle of Dingtao", sh="定陶之战", she="Dingtao",
                  d="项梁连破秦军于东阿、濮阳、定陶，渐有骄色。秦悉起兵益章邯，九月夜袭定陶，项梁战死。楚怀王自盱台徙都彭城，项羽、刘邦东还。"
                    "章邯以为楚地不足忧，渡河北击赵，破邯郸，徙其民于河内，王离围赵王歇于巨鹿。魏豹复下魏地二十余城，自立为魏王。",
                  de="Xiang Liang beat the Qin armies at Dong'e, Puyang and Dingtao and grew overconfident. Qin threw every man it had into Zhang Han's army, "
                     "which fell on Dingtao by night in the 9th month; Xiang Liang was killed. King Huai moved his court from Xuyi to Pengcheng, and Xiang "
                     "Yu and Liu Bang fell back east. Thinking Chu no longer a threat, Zhang Han crossed the Yellow River to attack Zhao, took Handan and "
                     "moved its people to Henei, while Wang Li besieged King Xie of Zhao at Julu. Wei Bao won back more than twenty cities of Wei and made "
                     "himself king."),
    "q207a": dict(era="二世三年十二月", era_en="Second Emperor, year 3, 12th month",
                  t="巨鹿之战", te="Battle of Julu", sh="巨鹿之战", she="Julu",
                  d="怀王遣宋义、项羽北救赵，遣刘邦西略地入关，约「先入定关中者王之」。宋义逗留安阳，项羽斩之，引兵渡河，「皆沉船，破釜甑」，"
                    "九战绝秦甬道，大破王离军于巨鹿，诸侯军皆作壁上观。战后诸侯将入辕门，莫敢仰视，皆属项羽。章邯退保棘原。",
                  de="King Huai sent Song Yi and Xiang Yu north to relieve Zhao and Liu Bang west into the passes, promising that whoever first took Guanzhong "
                     "would be its king. When Song Yi lingered at Anyang, Xiang Yu beheaded him and led the army across the river, 'sinking the boats and "
                     "smashing the cooking pots'; in nine battles he cut the Qin supply road and routed Wang Li's army at Julu while the allied armies "
                     "watched from their ramparts. Afterwards the allied generals entered his camp gate, none daring to look up, and all "
                     "placed themselves under him. Zhang Han fell back to Jiyuan."),
    "q207b": dict(era="二世三年八月", era_en="Second Emperor, year 3, 8th month",
                  t="章邯降楚·二世被杀", te="Zhang Han surrenders · Second Emperor killed", sh="章邯降", she="Zhang Han yields",
                  d="章邯为赵高所疑，屡败于项羽，七月率二十万众降于殷墟，项羽立之为雍王。刘邦自南阳西进，七月降宛，八月破武关。赵高指鹿为马，"
                    "八月逼杀二世于望夷宫，去帝号，立子婴为秦王。申阳下河南，司马卬定河内。",
                  de="Distrusted by Zhao Gao and repeatedly beaten by Xiang Yu, Zhang Han surrendered with 200,000 men at the ruins of Yin in the 7th month, "
                     "and Xiang Yu named him king of Yong. Liu Bang advanced west from Nanyang, taking the surrender of Wan in the 7th month and forcing Wu "
                     "Pass in the 8th. Zhao Gao, who had called a deer a horse, forced the Second Emperor to kill himself at the Wangyi Palace in the 8th "
                     "month, dropped the imperial title and set up Ziying as king of Qin. Shen Yang took Henan and Sima Ang Henei."),
    "q206a": dict(era="汉元年十月", era_en="Han year 1, 10th month",
                  t="子婴出降·秦亡", te="Ziying surrenders · fall of Qin", sh="秦亡", she="Qin falls",
                  d="子婴诛赵高。汉元年十月，刘邦军至霸上，子婴素车白马，系颈以组，封皇帝玺符节，降于轵道旁，秦亡（通鉴系此年，教科书多作前207）。"
                    "刘邦入咸阳，封府库，还军霸上，与关中父老约法三章。十二月项羽破函谷关，至戏，鸿门宴上刘邦脱身；项羽屠咸阳，杀子婴，焚秦宫室。"
                    "南海尉赵佗绝道自守，闽越无诸亦据闽中自保。",
                  de="Ziying had Zhao Gao put to death. In the 10th month of Han year 1, when Liu Bang's army reached Bashang, Ziying came out in a plain "
                     "white carriage drawn by white horses, a cord round his neck, bearing the sealed imperial seals and tallies, and surrendered beside "
                     "the Zhi road: Qin had fallen (the Tongjian dates this to this year; many textbooks give 207 BC). Liu Bang entered Xianyang, sealed "
                     "the treasuries, returned to Bashang and agreed a three-article code with the elders of Guanzhong. In the 12th month Xiang Yu broke "
                     "through the Hangu Pass to Xi, where Liu Bang slipped away from the Hongmen banquet; Xiang Yu then sacked Xianyang, killed Ziying "
                     "and burned the Qin palaces. Zhao Tuo, commandant of Nanhai, cut the roads and held the south for himself, and Wuzhu of Minyue too "
                     "went his own way."),
    "q206b": dict(era="汉元年二月", era_en="Han year 1, 2nd month",
                  t="分封十八王", te="The Eighteen Kings enfeoffed", sh="十八王", she="18 kings",
                  d="项羽尊怀王为义帝，自立为西楚霸王，王梁楚九郡，都彭城；分天下为十八国：刘邦为汉王，王巴蜀汉中；三分关中，以章邯、司马欣、董翳为雍、塞、翟王"
                    "以拒汉；徙魏豹为西魏王、赵歇为代王、韩广为辽东王、田市为胶东王，立张耳、英布、吴芮、共敖、臧荼、田都、田安、申阳、司马卬诸人为王。"
                    "韩王成随项羽东行，不得就国。四月诸侯各就国，刘邦烧绝栈道入汉中。",
                  de="Xiang Yu honoured King Huai as Righteous Emperor and made himself Hegemon-King of Western Chu, ruling nine commanderies of Liang and "
                     "Chu from Pengcheng, and divided the realm into eighteen kingdoms: Liu Bang became king of Han, with Ba, Shu and Hanzhong; Guanzhong was "
                     "split in three, with Zhang Han, Sima Xin and Dong Yi as kings of Yong, Sai and Di to bottle up Han; Wei Bao was moved to Western Wei, "
                     "Zhao Xie to Dai, Han Guang to Liaodong and Tian Shi to Jiaodong, while Zhang Er, Ying Bu, Wu Rui, Gong Ao, Zang Tu, Tian Du, Tian An, "
                     "Shen Yang and Sima Ang were made kings. Han Cheng, king of Han (韓), was kept with Xiang Yu and never reached his kingdom. In the 4th "
                     "month the lords left for their kingdoms, and Liu Bang burned the plank roads behind him as he entered Hanzhong."),
    "q206c": dict(era="汉元年八月", era_en="Han year 1, 8th month",
                  t="还定三秦·田荣并齐", te="The Three Qins retaken · Tian Rong unites Qi", sh="定三秦", she="Three Qins",
                  d="分封方毕，天下复乱。五月田荣逐田都，六月杀田市，七月又击杀济北王田安，并王三齐。陈余向田荣借兵，谋袭常山王张耳。项羽杀韩王成，以郑昌为韩王。"
                    "八月刘邦用韩信之计，出故道击雍王章邯，章邯退守废丘，塞王司马欣、翟王董翳降汉。臧荼击杀辽东王韩广，并其地。",
                  de="The enfeoffment had barely been made when the realm fell apart again. In the 5th month Tian Rong drove out Tian Du, in the 6th he killed Tian Shi, "
                     "and in the 7th killed Tian An, king of Jibei, taking all three Qi kingdoms; Chen Yu sought troops from Qi to attack Zhang Er, king of "
                     "Changshan. Xiang Yu killed Han Cheng and made Zheng Chang king of Han (韓). In the 8th month Liu Bang, on Han Xin's plan, came out by the Old "
                     "Road against Zhang Han, king of Yong, who fell back to hold Feiqiu, while Sima Xin of Sai and Dong Yi of Di surrendered to Han. Zang Tu "
                     "killed Han Guang, king of Liaodong, and annexed his land."),
    "q205a": dict(era="汉二年四月", era_en="Han year 2, 4th month",
                  t="彭城之战", te="Battle of Pengcheng", sh="彭城之战", she="Pengcheng",
                  d="汉王东出：河南王申阳降，韩信（韩襄王孙）破郑昌，立为韩王，殷王司马卬被虏；陈余逐张耳、复立赵歇，赵歇立陈余为代王。项羽北击田荣，田荣败死，"
                    "齐人立田广。项羽已于十月弑义帝于江中，三月汉王为之发丧，四月率五诸侯兵五十六万人入彭城。项羽以精兵三万自齐回师，大破汉军于彭城、睢水，"
                    "汉王仅以数十骑脱走，诸侯复附楚，魏豹叛汉。",
                  de="The king of Han struck east: Shen Yang, king of Henan, surrendered; Han Xin, grandson of King Xiang of Han (韓), beat Zheng Chang and was "
                     "made king of Han; Sima Ang, king of Yin, was captured. Chen Yu drove out Zhang Er, restored Zhao Xie, who made him king of Dai. "
                     "Xiang Yu went north against Tian Rong, who was defeated and killed, and the men of Qi set up Tian Guang. Earlier, in the 10th month, Xiang Yu had had "
                     "the Righteous Emperor murdered on the Yangzi; in the 3rd month the king of Han proclaimed mourning for him, and in the 4th month led 560,000 men of five "
                     "allied lords into Pengcheng. Xiang Yu came back from Qi with 30,000 picked troops and crushed the Han army at Pengcheng and on the Sui "
                     "River; the king of Han escaped with a few dozen horsemen, the lords went back over to Chu and Wei Bao turned against Han."),
    "q205b": dict(era="汉二年九月", era_en="Han year 2, 9th month",
                  t="韩信破魏代", te="Han Xin conquers Wei and Dai", sh="破魏代", she="Wei & Dai",
                  d="汉王收散卒屯荥阳，萧何发关中兵补之，与楚相持于京、索之间。六月引水灌废丘，章邯自杀，关中尽为汉有，汉王都栎阳。八月韩信击西魏，"
                    "陈船临晋，自夏阳以木罂缻渡军，袭安邑，九月虏魏豹，置河东、太原、上党郡；后九月破代兵，擒夏说于阏与。",
                  de="The king of Han gathered his scattered men at Xingyang, Xiao He sent reinforcements from Guanzhong, and the two sides faced each other "
                     "between Jing and Suo. In the 6th month the Han flooded Feiqiu and Zhang Han killed himself, leaving all Guanzhong to Han, whose king "
                     "ruled from Yueyang. In the 8th month Han Xin attacked Western Wei: he massed boats at Linjin but carried his army across at "
                     "Xiayang on wooden jars, fell on Anyi and in the 9th month captured Wei Bao, making Hedong, Taiyuan and Shangdang commanderies; in the "
                     "intercalary 9th month he broke the Dai army and captured Xia Yue at Yuyu."),
    "q204": dict(era="汉三年", era_en="Han year 3",
                 t="井陉之战·荥阳之困", te="Jingxing · the plight of Xingyang", sh="井陉之战", she="Jingxing",
                 d="十月韩信、张耳以数万人东下井陉，背水为阵，拔赵帜立汉赤帜，破赵军二十万，斩陈余于泜水，擒赵歇；燕王臧荼闻风降汉。十二月九江王英布归汉，"
                   "其地为项羽所并。项羽数断汉甬道，五月纪信诈降，汉王出荥阳；荥阳、成皋相继失守，周苛被杀。汉王北渡河，夺韩信军，复与楚相持于巩、洛。",
                 de="In the 10th month Han Xin and Zhang Er came down the Jingxing pass with a few tens of thousands of men, fought with their backs to a "
                    "river, pulled down the Zhao flags and raised the red flags of Han, routed a Zhao army of 200,000, beheaded Chen Yu on the Zhi River and "
                    "captured Zhao Xie; Zang Tu, king of Yan, promptly submitted to Han. In the 12th month Ying Bu, king of Jiujiang, went over to Han and Xiang "
                    "Yu annexed his land. Xiang Yu repeatedly cut the Han supply road; in the 5th month Ji Xin pretended to surrender so that the king of Han "
                    "could escape from Xingyang. Xingyang and Chenggao fell one after the other and Zhou Ke was killed. The king of Han crossed to the north bank of the "
                    "Yellow River, took over Han Xin's army and again held the line against Chu at Gong and Luo."),
    "q203a": dict(era="汉四年十一月", era_en="Han year 4, 11th month",
                  t="潍水之战", te="Battle of the Wei River", sh="潍水之战", she="Wei River",
                  d="郦食其说降齐王田广，韩信用蒯通之计乘虚袭齐，十月破历下，入临淄，田广烹郦食其东走。项羽遣龙且将二十万救齐，十一月韩信夜囊沙壅潍水上流，"
                    "半渡决之，斩龙且，虏田广，尽定齐地。同月汉王立张耳为赵王。此前十月汉军已大破楚大司马曹咎于汜水，夺回成皋，与项羽对峙于广武。",
                  de="Li Yiji had talked Tian Guang, king of Qi, into submitting, but Han Xin, on Kuai Tong's advice, struck while Qi was off guard: in the 10th "
                     "month he broke Lixia and entered Linzi, and Tian Guang boiled Li Yiji alive and fled east. Xiang Yu sent Long Ju with 200,000 men to "
                     "save Qi; in the 11th month Han Xin dammed the upper Wei River with sandbags by night and released the water when Long Ju's army was "
                     "half across, beheading Long Ju, capturing Tian Guang and taking all Qi. That month the king of Han made Zhang Er king of Zhao. In the 10th month Han had "
                     "crushed the Chu Grand Marshal Cao Jiu on the Si River, retaken Chenggao and come face to face with Xiang Yu at Guangwu."),
    "q203b": dict(era="汉四年九月", era_en="Han year 4, 9th month",
                  t="鸿沟议和", te="The Honggou Canal truce", sh="鸿沟", she="Honggou",
                  d="二月汉王立韩信为齐王；七月立英布为淮南王。彭越往来梁地，绝楚粮道。项羽兵疲食尽，八月与汉约中分天下，割鸿沟以西为汉、以东为楚，"
                    "九月归还太公、吕后，解而东归；汉王用张良、陈平之计，背约追击。",
                  de="In the 2nd month the king of Han made Han Xin king of Qi, and in the 7th made Ying Bu king of Huainan. Peng Yue roamed the Liang lands "
                     "cutting Chu's supply lines. With his men exhausted and his food gone, Xiang Yu agreed in the 8th month to divide the realm with Han at "
                     "the Honggou Canal, Han taking the west and Chu the east. In the 9th month he sent back Liu Bang's father and wife, broke camp and "
                     "turned east; the king of Han, on the advice of Zhang Liang and Chen Ping, broke the treaty and went after him."),
    "q202a": dict(era="汉五年十二月", era_en="Han year 5, 12th month",
                  t="垓下之战", te="Battle of Gaixia", sh="垓下之战", she="Gaixia",
                  d="汉王追项羽至固陵，韩信、彭越不至，汉军败；汉王许以陈以东傅海与齐王、睢阳以北至穀城与彭越，诸侯乃会。十二月韩信、彭越、英布、刘贾"
                    "合围项羽于垓下，夜闻四面楚歌，项羽溃围南走，至乌江自刎。楚地皆降，惟鲁坚守，持项羽首示之乃降。汉又遣卢绾、刘贾击临江王共尉。",
                  de="The king of Han caught up with Xiang Yu at Guling but Han Xin and Peng Yue failed to come, and the Han army was beaten; only when he "
                     "promised the king of Qi the land east of Chen to the sea, and Peng Yue the land from Suiyang north to Gucheng, did the lords join him. "
                     "In the 12th month Han Xin, Peng Yue, Ying Bu and Liu Jia surrounded Xiang Yu at Gaixia; hearing the songs of Chu on every side at "
                     "night, he broke out to the south and cut his own throat at Wujiang. The Chu lands all submitted; only Lu held out until shown Xiang "
                     "Yu's head. Lu Wan and Liu Jia were sent against Gong Wei, king of Linjiang."),
    "q202b": dict(era="汉五年二月", era_en="Han year 5, 2nd month",
                  t="刘邦称帝", te="Liu Bang becomes emperor", sh="称帝", she="Emperor",
                  d="正月徙齐王韩信为楚王，都下邳；立彭越为梁王，都定陶。二月甲午汉王即皇帝位于汜水之阳，是为汉高祖。异姓七王：楚王韩信、梁王彭越、"
                    "淮南王英布、长沙王吴芮、韩王信、赵王张耳、燕王臧荼；关中、巴蜀与关东诸郡为汉直辖。五月罢兵归家，用娄敬之议定都关中（先居栎阳）。",
                  de="In the 1st month Han Xin was moved from Qi to be king of Chu at Xiapi, and Peng Yue was made king of Liang at Dingtao. On the jiawu day "
                     "of the 2nd month the king of Han took the imperial throne north of the Si River: he was Emperor Gaozu of Han. Seven kings of other "
                     "surnames held their own realms — Han Xin of Chu, Peng Yue of Liang, Ying Bu of Huainan, Wu Rui of Changsha, Han Xin of Han (韓), Zhang Er of "
                     "Zhao and Zang Tu of Yan — while Guanzhong, Ba–Shu and the commanderies east of the passes were ruled directly. In the 5th month the "
                     "troops were sent home, and on Lou Jing's advice the capital was fixed in Guanzhong (first at Yueyang)."),
    **TEXT2,
}
