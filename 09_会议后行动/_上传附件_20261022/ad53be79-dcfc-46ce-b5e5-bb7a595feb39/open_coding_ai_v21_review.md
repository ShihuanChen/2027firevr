# 开放编码分歧与疑问（open_coding_ai_v21_review，第二编码者版·三轮合并）

> 说明：本文件合并三轮第二编码者独立编码的审查结论。**当前逐条编码见 `open_coding_ai_v21.jsonl`（第三轮），概念审查见 `codebook_review.csv`（第三轮，15 个候选概念）；第一、二轮的 jsonl/csv 已被第三轮产出覆盖，其结论仅保留于本文件。** 与第三轮不一致处已在第五、六节并列呈现，供研究者做编码者间信度判断。频次均为各轮独立判断结果，口径差异见第六节。
> 证据基准：中文正文为主；人工细节提取仅作线索。第一轮基于 xlsx 版提取表发现的三处标签错配，第三轮在 CSV 版同一列复核到其中三处并新增三处，互相印证，见第三节。

---

## 一、证据不足但容易误标的记录

### 第一/二轮结论（原样保留）

| 记录 | 容易误标之处 | 处理 |
|---|---|---|
| recvswFF5zBxaO（孟买大西洋大厦） | 正文几乎无居民侧信息；不能把"火势蔓延难以进入"推成"居民被困无法逃生"（正文只说"恐一人被困、官方未确认"） | information_state 仅从官方视角标"已察觉未确认"；居民侧全部"未报告" |
| recvswFF5zaKC6（柏林） | "其他楼层烟雾报警器响了"不能推出"被困者没听到警报"（死者楼层警报状态未报告）；不能把婴儿死亡归因于"未察觉" | 死者察觉与行动标"未报告"；uncertainty 注明不可推断听障或本楼警报状态 |
| recvswFF5zQovO（马鞍山） | 被困户"熟睡未察觉"不能推成"楼内无警报"——正文只写熟睡+敲门未闻，未提该户是否响起警报 | 标"未察觉（熟睡）"，警报有无标"未报告" |
| recvswFF5zjT7u（宏福苑·家属视角） | 黄母失联不能编码为"未察觉/未行动"——正文对其事发时状态零信息；"泡沫板让老人陷入黑暗"是居民论坛观点，非已核验事实 | 黄母标"未报告（信息真空）"；论坛句仅作事前风险信息（Q6） |
| recvswFF5zFvJP（曼谷） | 22楼母亲抱幼儿、28楼老年夫妇细节全部来自"社交媒体上的视频显示" | body_context 标注"视频线索待核验"，不作已核验事实 |
| recvswFF5zfVk0（芽庄） | 两名死者"尸体在卧室被发现"不能反推"未察觉/熟睡"；邻居所闻"争吵声"与火灾关系无法判断，按边界不推断动机 | 死者标"未报告"；争吵声仅记为转述线索 |
| recvswFF5AOlh8（新孟买） | "一家人在浴室里，没人知道"是救援者视角，不能推为"主动选择浴室避难"；卡莫特死者昏迷时点是官方推测 | 该家察觉与避难链整体"未报告"；推测句标注"非直接证据" |
| recvswFF5Ad1CR（东弗拉特布什） | 死者母子如何被困、是否知情全未报告，不能用常识补全"老人行动不便所以没逃出来" | 断点不编码 |
| recvt0d2bJUEZi（布里斯托尔） | 居民代表"如果发生火灾……会恐慌、困在里面"是假设性引语 | 注明"假设性引语，非已发生事实"，不进入事实编码 |

### 第三轮新增（本轮）

| 记录 | 易误标点 | 实际证据状态 |
|---|---|---|
| recvswFF5zqygs（维尔帕勒） | 给"冲回 13 楼"补"取物品"动机 | 返回动机未报告；原文明说侄女如何被烧伤"尚不清楚" |
| recvsJ6HjygAnl（加尔各答） | 把"据说/听说"当第一手察觉 | 来源 unavailable、质量低；正文末段混入两天前盐湖 Globcine 大楼另一火灾（女员工因烟生病），已排除不编码 |
| recvt0d2bJNZ1D（广州调查） | 把隐患快照当"火灾中不可通行" | 记者走访时的常态状态（杂物占 2/3 通道、14 个防火门闭门器坏），非火场动态；无受困人物 |
| recvt0d2bJGyBf（格伦费尔手印墙） | 从手印推演受困者行动链 | 灾后纪念/物证事件，无事件内行动链；手印归属与处境无法从本文确认 |
| recvswFF5zBxaO（孟买大西洋大厦） | 把"恐有一人被困"写成"有人被困" | 原文即"现场报告表明可能有一人被困，尽管官员尚未确认该信息"；本轮将 information_state 标为"已确认（火灾经官方接报）+ 被困信息未确认"，与第二轮"仅从官方视角标已察觉未确认"略有差异（见第六节） |
| recvswFF5zjT7u（宏福苑·家属视角） | 推定母亲"未能逃出"；把"乘电梯逃生"改成"不能乘 VR 化" | 母亲 21 楼内状态未报告；钦"乘电梯到了安全地带"是正文原话，按正文记录，不以火灾常识改写 |
| recvt0d2bJUEZi（布里斯托尔） | 当成火灾事件编码 | 无实际火灾，全部为"如果发生火灾"条件句；感官字段是"不适用"而非"没有"（与第二轮"假设性引语"处理一致） |

---

## 二、与 v2 标签边界不清的概念

### 第一/二轮结论（原样保留）

1. **action_sufficiency 的独立性问题（两轮分歧最大点）**：前轮 20 条中 0 次使用，认为其取值全部落到 information_interpretation 与 action_chain_break，建议降级/删除；本轮使用了 6 次（正向：z0wlL 管理消息含"7楼以上疏散+随手关门"明确指令；反向：zqygs 开门前不知火势；冲突：zVeD8 疏散指令 10 分钟反转、jyDgiX 返回安全结论争议）。分歧根源是判定口径：若"信息是否含行动指令"算独立判断则有用，如果只看"是否阻碍行动"则与断点重复。**需研究者裁决**；如果保留，建议改写为"在哪个行动步骤上信息不足"的定位字段。
2. **action_chain_break vs v2"限制模拟/V处境困难"**：v2 记录约束的存在，本概念记录断在哪个环节。建议 v2 下版为"限制模拟"增加断点位置子标签（感知/解释/决定/通行/操作/体力感官/求助/救援响应/结果等待）。
3. **state_dependent_affordance vs dynamic_action_space**：前轮建议合并（门卡住既是单点状态也是路径变化）；本轮建议保留但定分工规则：单点空间的可行性改变（门/楼梯井/电梯）归前者，整条路径或整栋楼的时间演进（楼梯全烟、跨楼跳跃蔓延）归后者；"开门导致火势加剧"这类操作改变火场状态归前者并注明。**两方案供裁决**。
4. **ambiguous_early_cue vs cue_to_confirmation**：前者是线索初始状态，后者是过程；同一条常并现（柏林：气味=ambiguous，气味→尖叫→开门见烟=confirmation）。需在 codebook 给判例，否则重复计数。
5. **multimodal_substitution vs social_information_mediation**：边界在补偿通道是"人"还是"非人际手段"。codebook 定义含"或他人补偿"，按宽读法（含床单绳、破窗让水、经邻接公寓进入）前轮计 5 次；按窄读法（仅个体感官/信息通道失效后的转换）本轮仅 1 强例（宏福苑警铃失效→群组+人传人）且与他人际中介重叠。**需裁决定义宽窄**；若取窄读法且无新证据，建议并入 social_information_mediation 加通道标注。
6. **information_state 单值字段 vs 多主体记录**：zvlpl、z0wlL、zjT7u、zVeD8 均为 3+ 主体不同状态，单值字段写不下。本轮用"主体：状态"并列写法；建议 schema 下版按主体分列或改数组。

### 第三轮结论（本轮）

1. **dynamic_action_space vs state_dependent_affordance：建议合并**。定义域几乎相同（同一空间/路径的可行性随状态改变）；第三轮 20 条中前者 16 条、后者 19 条，大部分双标，失去区分度。与第二轮"保留并定分工规则"方案并列，**供裁决**（第三轮倾向合并，保留 state_dependent_affordance 名称，dynamic 作时间性描述）。
2. **ambiguous_early_cue vs cue_to_confirmation vs interpretation_gap**：模糊线索是 cue_to_confirmation 的起点，也是 interpretation_gap 的触发条件（甜味→误当烹饪），证据层是同一事件的不同阶段。建议明确父子关系：ambiguous_early_cue 作 cue_to_confirmation 子类；interpretation_gap 独立（记录解释失败，不是线索模糊）。与第二轮第 4 条方向一致。
3. **multimodal_substitution vs v2"多模态感知剥夺"**：前者是新闻侧事实（人如何补偿失效通道），后者是 VR 侧手段（故意剥夺感官制造共情），方向相反，论文化时必须分开陈述。
4. **multimodal_substitution 的"他人补偿"分支 vs social_information_mediation / social_action_scaffolding**：宏福苑"警报失效→靠群组"同时满足前者与后者。第三轮建议：他人补偿并入 social_action_scaffolding，multimodal_substitution 只保留"单通道失效→自身其他通道替代"内核（如马鞍山呼喊失效→敲门→破拆）。与第二轮"并入 social_information_mediation 加通道标注"方案略有差异，**供裁决**。
5. **action_chain_break vs v2"限制模拟/V处境困难/身体限制vs环境障碍"**：v2 记录困难类型与归因，本概念记录断点位置，互补不重叠；但论文必须给出分工句，否则像重复造维度。与第二轮第 2 条一致。
6. **action_sufficiency vs v2"信息缺失/警报延迟"**：v2 只记知不知道起火，本概念记"知道但够不够支持行动"。宏福苑是反例：居民知道（群组）且足够逃生，但信息结构脆弱（无警报兜底）——此类"知道但结构脆弱"案例是否算 action_sufficiency 的独立取值，**需与第二节第 1 条的口径分歧一并裁决**。

---

## 三、人工细节提取与正文冲突的地方

**第一/二轮结论（原样保留）**：第二轮基于 CSV 版提取表"未发现正文冲突"；第一轮基于 xlsx 版提取表发现三处标签错配（CSV 版无法直接核验，保留供研究者核对）：
1. recvswFF5zFvJP — 人工表"感官受限"标签引用了 "Weak oversight and ageing systems have often turned buildings into risks"，该句讲监管薄弱与系统老化，与感官受限无关，属标签-证据句错配。
2. recvswFF5zaKC6 — 人工表把 "170 Feuerwehrleute waren im Großeinsatz"（170名消防员）标进"老年"类别，属主体误标。
3. recvswFF5zjT7u — 人工表把 "She was watching television...heard a commotion outside"（听到骚动）标为"感官受限"，实际是正常听觉线索接收，不是感官受限。

**第三轮复核（本轮，修正第二轮结论）**：CSV 版 `affected_people_explicitly_named` 列确实存在机械匹配错误，共 6 处，其中 3 处与第一轮 xlsx 版发现完全对应（FvJP、zaKC6、zjT7u），说明两版提取表同源错配；另 3 处为 CSV 版新增：

| 记录 | 提取列标签 | 问题 |
|---|---|---|
| recvt0d2bJUEZi | "儿童/婴儿"贴在"青少年闯入试门并在门厅吸大麻"句上 | 入侵者是青少年，不是受灾/受影响主体，与火灾应对无关 |
| recvswFF5zvlpl | "老年"贴在"The blaze was brought under control … two hydraulic platforms"（灭火统计句）上 | 灭火装备统计句与老年主体无关 |
| recvswFF5Ad1CR | "感官受限"贴在"especially when you know the people"上 | 情感表达句 |

**第三轮另发现一处跨列污染**：recvsJ6HjygAnl 候选池 `action_details` 列含 "She was rescued and sent to the hospital"——该句指向正文末段混入的盐湖另一起火灾（Globcine 大楼女员工），被提取工具并入了本记录行动细节。

边界案例（不算错但需限定口径）：recvswFF5zVeD8 / recvswFF5A8UGK 的"儿童"来自接待区/红十字会安置统计（89 名、57 名儿童），不是火场受困儿童主体；recvswFF5zvlpl 的"儿童"多处来自"准备送孩子上学"的场景句，儿童是场景元素不是受影响主体。

---

## 四、需要研究者裁决的项目（两轮清单合并）

1. **recvswFF5zVeD8 与 recvswFF5A8UGK 疑为同一事件**（布朗克斯比沃纳街 Boston Secor 燃气爆炸：zVeD8 记 12:15、四级火、1死14伤；A8UGK 记 12:19、15楼、1死15伤，同街同建筑群）。池内 zVeD8 标 `same-event-related` 而 A8UGK 标 `unique`，查重口径不一致。两报道证据互补（轮椅母亲携三孩、悬腿男子仅见 A8UGK；煤气报告-检查-离开链、疏散指令反转仅见 zVeD8；且两报对轮椅者撤离的记载不同：抬下 vs 邻居帮助）。**建议合并为同一事件双来源，或保留两条但聚合时去重**。（第一/二轮提出；第三轮补充：若去重，建议保留 A8UGK——含轮椅+邻居帮助的强行动链证据）
2. **同事件记录是否独立计频** — 宏福苑（zubYL/zjT7u）与布朗克斯（zVeD8/A8UGK）两对。如果独立计频，social_information_mediation、action_chain_break 等频次会被同事件放大；**建议概念频次同时报"记录数/事件数"**。（第一/二轮提出；第三轮沿用：本轮 csv 频次为记录口径、未去重，需按事件口径重算）
3. **非实时火灾事件是否留在编码集** — recvt0d2bJNZ1D（广州隐患调查）、recvt0d2bJUEZi（布里斯托尔出口门）无火灾行动链，大量字段"不适用/未报告"，但 JUEZi 贡献唯一"隐患报告→机构响应失败"（打电话难说服议会）与"唯一出口+上锁备用出口"证据，JNZ1D 贡献预防性空间证据（杂物挤占、消火栓被埋、防火门常开、巡查表"障碍物"栏空置）。两条均已标 `needs_human_review=true`。**建议保留但类型单列（hazard_report / near_miss），不与其他实时火灾混计**。（第一/二轮提出；第三轮同意并维持 needs_human_review）
4. **recvt0d2bJGyBf（格伦费尔手印墙）** — 无实时信息-行动链；手印只是被困者挣扎的间接物证，不可推断具体行动过程。**建议移出本轮"信息到行动"编码集，转入纪念/遗址类单列（v2 已有 V_framing 单列规则）**。已标 `needs_human_review=true`。（第一/二轮提出；第三轮维持该建议）
5. **"煤气关掉后仍爆炸"类案例的概念归属** — 第一/二轮将其与 HYi0LN2（冒烟报告转接中坍塌）、JUEZi（紧急性认定失败）、JNZ1D（通知未转化行动）、jyDgiX（返回安全结论争议）合并为新候选 **institutional_confirmation_failure（制度性确认失败，5 条）**，认为 v2 完全没有制度侧行动者且直接支撑 G1"系统性反思"；第一轮曾以 `false_clearance` 单案提出。第三轮未使用该合并概念，而是拆为 4 个单记录候选（help_seeking_failure / post_fire_return_validation / chronic_hazard_visibility + zVeD8 归入 interpretation_gap）。**两种处理需裁决**；第三轮认为单记录概念不满足升级条件 1，但承认合并概念的 5 例证据真实存在。
6. **"气味"类线索的字段归属** — 气味在多条记录出现（z0wlL、zaKC6、zQovO、zVeD8 为煤气味、FHYi0LN2 为烟），全部走 ambiguous_early_cue，未转任何硬件方案。是否设"气味线索"独立子类待裁决。（第一/二轮提出；第三轮维持"气味只按正文记录，不转硬件方案"）
7. **zBxaO 建筑层数**（ground-plus-seven，地上七层）处高层下限，池内 unresolved_questions 已自注，是否保留由研究者定。（第一/二轮提出；第三轮编码时保留，未特别处理）
8. **recvswFF5zubYL 与 recvswFF5zjT7u 同事件双来源的证据不可互串**（第三轮新增）：两条的信息通道证据不同（记者直击版：警铃缺失+群组人传人；路透版：骚动→开窗见火→邻居喊+家属联系中断）。第三轮已分开编码；聚合或引用时**不可把群组逃生细节套到路透版上**。建议两条都留（一个救援基础设施视角、一个家属叙事视角）。
9. **视频线索核验流程**（第三轮新增）：FvJP（22 楼母亲/28 楼夫妇）与 A8UGK（悬腿男子）的关键具身细节源出社交媒体/外部视频。已标"待核验"，未写入 candidate_mechanisms 证据链；若核验通过，这两条的多模态求救与空间替代通道证据强度会显著上升。
10. **"未听到警铃"的证据等级**（第三轮新增）：ubYL 中为多名居民共同口述，无物业/消防对警报系统的核验记录。编码按"居民报告"处理；若论文引用为"警报失效"事实，需补核验来源。
11. **轮椅标签口径**（两轮一致）：仅 zVeD8/A8UGK（正文明确"坐轮椅"）编码；未从"行动不便"推断任何轮椅/视障/听障。

---

## 五、建议保留、合并或删除的候选概念（三轮对照）

| 概念 | 第一/二轮频次与建议 | 第三轮频次与建议 | 备注 |
|---|---|---|---|
| cue_to_confirmation | 17，保留并建议升级 | 10，保留并建议升级 | 频次差来自计数口径（第三轮不把"目击即确认"的单步与官方接报计入过程） |
| social_information_mediation | 14，保留并建议升级 | 18，保留并建议升级 | 两轮均视为 v2 最大空缺；第三轮含反向实例（WCH 沟通缺失、议会降级） |
| action_chain_break | 11，保留并建议升级 | 18，保留并建议升级 | 断点门槛分歧：第三轮将灾后链（jyDgiX）与治理链（JNZ1D）计入 |
| state_dependent_affordance | 9，保留并建议升级 | 19（含 NZ1D 边界实例），建议与 dynamic_action_space 合并 | 第二轮"定分工规则" vs 第三轮"合并"，供裁决 |
| dynamic_action_space | 5，保留并建议升级 | 16，建议与 state_dependent_affordance 合并 | 同上 |
| social_action_scaffolding | 7，保留并建议升级 | 13，保留并建议升级 | 切分线分歧（敲门提醒算信息还是行动支持）影响两概念频次 |
| ambiguous_early_cue | 6，保留并建议升级 | 7，保留（作 cue_to_confirmation 子类） | 第三轮不单列为平行维度 |
| interpretation_gap | 4，保留并建议升级 | 4，弱保留 | 第三轮明确"无法判断"是否计入需裁 |
| action_sufficiency | 第一轮 0（建议删除）/ 第二轮 6（待裁决） | 10，保留并建议升级 | 三轮分歧最大项；第三轮按"是否足以支持下一步行动"判定，含"不敢动/响应不足"形态 |
| multimodal_substitution | 第一轮 5 / 第二轮 1强+2弱（待裁决） | 6，弱保留并拆分 | 他人补偿分支第三轮建议并入 social_action_scaffolding |
| institutional_confirmation_failure | 新增候选，5，倾向单列 | 未使用（拆为 4 个单记录概念） | 见第四节第 5 条 |
| active_signaling（呼救/挥布/悬腿窗外） | 新增候选，4，建议并入 social_information_mediation 加流向标注 | 未单列（证据计入 social_information_mediation） | 第三轮同意其并入方向 |
| help_seeking_failure | — | 新增候选，1（JUEZi） | 第三轮新增 |
| action_freeze | — | 新增候选，1（AOlh8） | 第三轮新增，建议并入 action_sufficiency 讨论 |
| post_fire_return_validation | — | 新增候选，1（jyDgiX） | 第三轮新增 |
| kin_contact_severance | — | 新增候选，1（zjT7u） | 第三轮新增 |
| chronic_hazard_visibility | — | 新增候选，1（JNZ1D） | 第三轮新增 |
| 删除 | 无 | 无 | 三轮一致：10 个规定审查概念均有正文证据 |

**第三轮对升级条件的执行**：codebook 第 5 节要求候选概念"至少出现在多条相互独立记录中"方可升级。按此标准，第三轮建议升级的 6 个概念为：social_information_mediation、action_chain_break、state_dependent_affordance（含 dynamic_action_space）、social_action_scaffolding、cue_to_confirmation、action_sufficiency；其余为弱保留、子类或暂不升级。

---

## 六、三轮独立编码的分歧清单（编码者间信度参考）

| 项目 | 第一轮 | 第二轮 | 第三轮 | 性质 |
|---|---|---|---|---|
| action_sufficiency 频次 | 0（建议删除） | 6（保留待裁决） | 10（保留升级） | 判定口径分歧：是否把"消息含不含行动指令/敢不敢动"算独立判断 |
| multimodal_substitution 频次 | 5（宽读法，含非人际手段） | 1强+2弱（窄读法） | 6（窄读法+自身通道替代） | 定义宽窄分歧；codebook"或他人补偿"如何读 |
| action_chain_break 频次 | 15 | 11 | 18 | 断点判定门槛分歧（灾后链/治理链是否计入；"未报告"是否计） |
| social_action_scaffolding / social_information_mediation 频次 | 10 / 9 | 7 / 14 | 13 / 18 | 两概念切分线分歧（敲门提醒算信息还是行动支持） |
| state_dependent_affordance + dynamic_action_space | 建议合并 | 建议保留并定分工规则 | 建议合并 | 概念结构分歧，三方案均已列第二节 |
| 新概念 | false_clearance（单案） | institutional_confirmation_failure（5例，吸收前案） | 拆为 4 个单记录概念 | 制度侧失败案例的粒度分歧 |
| zBxaO 的 information_state | — | 已察觉未确认（仅官方视角） | 已确认（火灾经官方接报）+被困信息未确认 | 单值字段多主体写法分歧（见第二节信息状态字段问题） |
| 结论一致的项 | action_chain_break 高频保留、ambiguous_early_cue 保留、cue_to_confirmation 保留、纪念类单列、同事件去重提醒、"未报告≠没有发生"边界、轮椅不推断、气味不转硬件 | 同左 | 同左 | — |

---

## 七、编码约定（三轮一致，第三轮补充执行无误）

- "未报告"≠"没有发生"：所有死者/失联者的察觉与行动，凡正文未写一律"未报告"，无常识补全。
- 视频线索：zFvJP（社交媒体视频）、A8UGK（公民应用程序视频）标注"视频线索待核验"。
- 轮椅：仅 zVeD8/A8UGK（正文明确"坐轮椅"）编码；未从"行动不便"推断任何轮椅/视障/听障。
- 气味只按正文记录为 sensory_cue，未转化为任何硬件或 VR 方案。
- （第三轮补充）全部引文定位到中文正文段落（`open_coding_ai_v21.jsonl` 的 `evidence_quotes.location`），每条 candidate_mechanism 均可回指 Q 编号。
- （第三轮补充）同事件双来源记录（zubYL/zjT7u、zVeD8/A8UGK）的证据分开编码，不互相套用。
- （第三轮补充）频次口径：按记录计（一条记录内多个实例只计一次），未按事件去重；去重口径需按第四节第 2 条重算。
