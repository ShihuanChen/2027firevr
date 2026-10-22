# 开放编码分歧与疑问（open_coding_ai_v21_review，第二编码者独立版）

> 说明：本文件基于第二编码者独立完成的 20 条编码与概念频次统计（`open_coding_ai_v21.jsonl`、`codebook_review.csv`）。频次为本轮独立判断结果，供研究者与第一编码者对照。

## 一、证据不足但容易误标的记录

1. **recvswFF5zBxaO（孟买大西洋大厦）** — 正文几乎无居民侧信息：居民如何察觉、如何行动、被困者身份/状态均未确认。`information_state` 只能从官方视角标"已确认"，`body_context`、`sensory_cue` 多为"未报告"。易误标点：不能把"火势蔓延难以进入"直接推成"居民被困无法逃生"（正文只说"恐一人被困、官方未确认"）。

2. **recvswFF5zaKC6（柏林囤积者公寓）** — 被困母子（26 岁妇女 + 5 岁 + 9 个月婴儿）的察觉与行动完全未报告，只写"救援人员在四楼走廊发现三名失去意识的人"。易误标点：正文有"其他楼层烟雾报警器响了"，不能由此推断"被困者没听到警报"（正文未说明被困者所处楼层与报警器关系）；同样不能把"婴儿死亡"直接归因于"未察觉"。

3. **recvswFF5Ad1CR（东弗拉特布什）** — 死者母子（80 岁 + 59 岁）如何被困、是否知情、是否尝试逃生全未报告，正文只写"消防拉出送医不治"。易误标点：不能用常识补全"老人行动不便所以没逃出来"。

4. **recvswFF5AOlh8（新孟买）** — "一家四口在浴室里，没人知道"是救援者视角；死者为何在浴室、是否主动躲藏、是否感知到火灾均未报告。易误标点：不能把"在浴室"推断为"躲避浓烟的正确自救"或"被烟熏到失去意识才躲进去"。

5. **recvswFF5zjT7u（香港宏福苑居民叙述）** — "泡沫板覆盖窗户会让独居行动不便老人陷入黑暗"是**居民论坛观点**，非正文已核验事实，不能当作已发生的感官剥夺机制。

## 二、与 v2 标签边界不清的概念

1. **action_sufficiency vs interpretation_gap / action_chain_break** — `action_sufficiency`（信息是否足以支持行动）在本轮 20 条中 **0 次被使用**。它的取值"足够/不足/冲突"在编码时落到了 `information_interpretation` 的"信息不足"和 `action_chain_break` 的断点上，没有独立增量。建议并入 `action_chain_break`，或改写为"在哪个行动步骤上信息不足"的定位字段。

2. **state_dependent_affordance vs dynamic_action_space** — 两者语义高度重叠（"门因高温变形卡住"既可说是"单一空间状态改变"也可说是"路径随火势改变"）。建议合并，或明确分工：`state_dependent_affordance` 只标**单点空间**（门/消火栓/出口）的可行性改变，`dynamic_action_space` 只标**整体路径/时间演进**（楼梯全烟、电梯停、火势沿立面蔓延）。

3. **ambiguous_early_cue vs cue_to_confirmation 起点** — 前者描述线索的**初始状态**（甜味/焦糊味/远处火光/窗外火星），后者描述**线索到确认的过程**。同一条记录常两者并现（如柏林：气味=ambiguous，气味→尖叫→开门见烟=cue_to_confirmation），需在 codebook 里给出判例，否则易重复计数。

4. **multimodal_substitution vs social_information_mediation** — 边界在"补偿通道是人还是物"：警报/感官失效后改由**他人**传递信息 → 优先标 `social_information_mediation`；改由**非人际通道或自创手段**（床单绳、破窗让水进入、从邻近公寓进入）→ 标 `multimodal_substitution`；两者并存时并标（如宏福苑 9 楼记录：手机群组=mediation，警报失效的通道替代=substitution）。

## 三、人工细节提取与正文冲突的地方

1. **recvswFF5zFvJP（曼谷）** — 人工细节提取表的"感官受限"标签引用了 "Weak oversight and ageing systems have often turned buildings into risks"，这句讲的是**监管薄弱与老化系统**，与"感官受限"无关，属标签与证据句错配。

2. **recvswFF5zaKC6（柏林）** — 人工提取表把 "170 Feuerwehrleute waren im Großeinsatz"（170 名消防员）标进"老年"类别，属主体误标（消防员非受灾老人）。

3. **recvswFF5zjT7u（香港）** — 人工提取表把 "She was watching television...when she heard a commotion outside"（听到外面骚动）标为"感官受限"，实际是**正常听觉线索接收**，不是感官受限。这正落入任务边界"不把听障/视障等身体状态推断为标签"。

4. **recvswFF5zVeD8 与 recvswFF5A8UGK（布朗克斯两案）** — 同属"燃气爆炸火灾"、同为波士顿塞科尔住宅、时间相近（12:15 / 12:19 凌晨），两案 `duplicate_status` 一个 same-event-related、一个 unique。VeD8 写"坐轮椅的人，消防抬下来"（多人被动救援）；A8UGK 写轮椅住户由邻居帮助、家人陪同下楼（单户主动+互助）。两份不冲突但粒度不同，需研究者确认是否同一事件、是否合并计数。

## 四、需要研究者裁决的项目

1. **同事件记录是否独立计频** — recvswFF5zubYL / recvswFF5zjT7u（宏福苑）、recvswFF5zVeD8 / recvswFF5A8UGK（布朗克斯）两对同事件。若独立计频，`social_information_mediation`、`action_chain_break` 等频次会被同事件放大；建议概念频次同时报"记录数 / 事件数"。

2. **非实时火灾事件是否留在编码集** — recvt0d2bJNZ1D（广州隐患调查）与 recvt0d2bJUEZi（布里斯托尔出口门）无火灾行动链，`information_state`/`action_chain` 大量填"不适用/未报告"。但 JUEZi 贡献了唯一的"隐患报告→机构响应失败"（居民打电话难说服议会）与"唯一出口门"证据；JNZ1D 贡献了"杂物挤占通道、消火栓被埋、防火门常开"的预防性空间证据。建议保留但类型单列（`hazard_report` / `near_miss`），不与其他 18 条实时火灾混计。

3. **recvt0d2bJGyBf（格伦费尔手印墙）** — 无任何实时信息-行动链，`candidate_mechanisms` 仅能编码为"行动链断裂的物证"（手印=被困者挣扎痕迹）。建议移出本轮"信息到行动"编码集，转入纪念/遗址类单列（V_framing）。

4. **recvswFF5zVeD8 的"煤气关掉后仍爆炸"** — 居民报煤气、消防检查"关掉走了"、随后爆炸，构成"信息曾被确认并认为已处置、实则未解除"的**信息冲突/错误解除**。是否单列为新概念（如 `false_clearance`），还是归入 `interpretation_gap` 或 `action_chain_break` 的救援响应断点，需研究者裁决。

5. **recvswFF5zfVk0（芽庄）的"争吵声"线索** — 邻居听到争吵声是否与火灾/死亡相关，正文无法判断；按边界不应推断动机，但该线索本身值得在"起火前信息"维度保留，需研究者决定是否纳入证据。

6. **"气味"类线索的字段归属** — 气味在 5 条记录中出现（recvswFF5z0wlL、zaKC6、zQovO、zVeD8、FHYi0LN2），本轮全部走 `ambiguous_early_cue`；任务边界禁止直接把气味转成硬件方案，已遵守。是否在机制层保留"气味线索"独立子类待裁决。

## 五、建议保留、合并或删除的候选概念

| 处理 | 概念 | 频次 | 理由 |
|---|---|---|---|
| 保留并建议升级 | action_chain_break（含断点位置子分类） | 15/20 | 最高频，直接回答"行动链在哪里中断"，覆盖 v2「限制模拟」遗漏的感知/决定/报告摩擦断点 |
| 保留并建议升级 | multimodal_substitution | 5/20 | v2 完全无对应，警报失效靠手机群组/床单绳/邻近公寓补偿是 VR 独有设计点 |
| 保留 | social_information_mediation | 9/20 | 与 social_action_scaffolding 构成"信息-行动"互补对，v2 只到互助未到信息层 |
| 保留 | social_action_scaffolding | 10/20 | 高频且功能可区分（抬轮椅、背氧气老人、护送、砸门提醒） |
| 保留 | cue_to_confirmation | 9/20 | 补 v2 缺的线索→确认时序维度 |
| 保留 | ambiguous_early_cue | 6/20 | 可作 cue_to_confirmation 的起点子类 |
| 保留为子类 | interpretation_gap | 3/20 | 频率偏低，可作 action_chain_break 的"解释"断点子类 |
| 合并 | state_dependent_affordance → 并入 dynamic_action_space | 8/20 | 与 dynamic_action_space 边界无法稳定区分（门卡住=单点状态改变=路径随火势变），建议合并为"状态依赖的可通行性"，门作为最常见载体单设子类 |
| 降级/删除 | action_sufficiency | 0/20 | 编码中零使用，取值与 information_interpretation、action_chain_break 完全重叠，无独立增量 |
