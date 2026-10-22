# open_coding_ai_v21 分歧与疑问

## 1. 证据不足但容易误标的记录

- **recvswFF5zBxaO(孟买大西洋大厦)**:居民侧信息链几乎全部未报告,只有官方时间线。除"救援队难以进入"外不应标任何行动链环节,警惕用常识补全疏散过程。
- **recvsJ6HjygAnl(托利甘吉)**:来源 unavailable,居民如何发现火灾完全未写;只标了"电梯关停+病母下楼"一个有证据的点。
- **recvswFF5zFvJP(曼谷38层)**:22楼母亲抱幼儿、28楼老夫妇两个关键被困细节来自"社交媒体上的视频",按任务边界标为视频线索待核验,不计入已确认事实。
- **recvswFF5AOlh8(新孟买)**:卡莫特母女"吸入烟雾昏迷后被烧死"是消防官推断(原文"很可能"),information_state 标"未察觉"基于推断而非直接证据,需人工确认口径。
- **recvswFF5Ad1CR(布鲁克林母子)**:遇难的母子二人本身在火灾中的位置、行动、信息接触全部未报告;正文只有邻居视角。不要给遇难者补行动链。

## 2. 与 v2 标签边界不清的概念

- **dynamic_action_space vs state_dependent_affordance**:8/6 条记录中过半同时命中两者(门热变形、电梯关停、开门加剧火势)。前者强调"路径随时间变",后者强调"同一构件状态翻转",实际编码中无法稳定区分。建议合并为"状态依赖的可通行性(state-dependent affordance)",门作为最常见载体单设子类。
- **action_sufficiency**:与 A 层 information_state/information_interpretation 功能重叠,作为"机制"频率仅 3 且判断依赖前两者。建议降级为字段取值,不进机制层。
- **action_chain_break vs v2「限制模拟」**:断点中的"操作/通行"类就是限制模拟,但"感知未察觉(马鞍山熟睡一家)""决定(恐惧不敢开门)""报告摩擦"三类断点超出 v2 限制模拟范围——这是 v2 的真实遗漏,建议 action_chain_break 升级正式维度并保留断点位置子分类。
- **social_information_mediation vs social_action_scaffolding**:砸门这个动作既是信息传递又是行动支持(z0wlL、Ad1CR),单动作双标现象存在;区分标准建议按"接受者是否因自身身体限制无法完成动作"——是则 scaffolding,否则 mediation。

## 3. 人工细节提取与正文冲突的地方

- **recvswFF5zFvJP**:人工提取列把"社交媒体上的视频显示……"与幸存者引语直接拼接为一条证据,正文明确该细节来源是社交媒体视频。编码时已拆分为待核验线索,人工提取表在此处隐含了"已确认"的口径。
- **recvswFF5zVeD8 与 recvswFF5A8UGK**:同一事件(波士顿塞科尔住宅,12:15/12:19 凌晨)两份报道。VeD8 写"坐轮椅的人,FDNY 把他们抬下来"(多人被动救援),A8UGK 写轮椅住户由邻居帮助、家人陪同下楼(单户主动+互助)。两份不冲突但细节粒度不同,若合并编码应以 A8UGK 的第一人称叙述为准,VeD8 作官方面补充。
- **recvswFF5zubYL 与 recvswFF5zjT7u**:同为宏福苑事件,zjT7u 中钦姓老妇"乘电梯逃生"与常识性的"火灾电梯停运"相反,正文未说明电梯为何可用。编码时按原文记录为"早期可通行",未做修正——这两条同事件记录建议按双源互补而非独立证据计频。

## 4. 需要研究者裁决的项目

1. **同事件记录是否独立计频**:zubYL/zjT7u(宏福苑)、VeD8/A8UGK(布朗克斯)两对同事件。若独立计频,social_information_mediation、action_chain_break 等频次被同事件放大;建议概念频次同时报"记录数/事件数"。
2. **非事件报道是否留在编码集**:recvt0d2bJNZ1D(广州隐患调查)与 recvt0d2bJUEZi(布里斯托尔门故障)无火灾行动链,信息状态字段大量不适用;但 JUEZi 贡献了唯一的 reporting_friction 与"门作为唯一出口"证据。建议保留但类型单列(hazard_report / near_miss)。
3. **recvt0d2bJGyBf(格伦费尔手印墙)**:无任何信息-行动链可编码,candidate_mechanisms 为空。人工提取表批注"不太相关"。建议移出本轮开放编码集,转入纪念类单列。
4. **"气味"类线索的字段归属**:气味在 5 条记录中出现(z0wlL、zaKC6、zQovO、VeD8、Yi0LN2),全部走 ambiguous_early_cue;任务边界禁止直接把气味转成硬件方案,已遵守,但是否在机制层保留"气味线索"独立子类待裁决。

## 5. 建议保留/合并/删除的候选概念

| 处理 | 概念 | 理由 |
|---|---|---|
| 保留并建议升级 | action_chain_break(含断点位置子分类) | 15/20 最高频,直接回答"行动链在哪里中断",覆盖 v2 遗漏的感知/决定/报告断点 |
| 保留 | cue_to_confirmation | 11/20,信息到行动的主干过程 |
| 保留 | social_information_mediation、social_action_scaffolding | 12/6,高频且功能可区分 |
| 保留 | interpretation_gap、ambiguous_early_cue | 5/5,常配套出现,是行动延迟的直接原因 |
| 合并 | dynamic_action_space + state_dependent_affordance → state-dependent affordance(状态依赖的可通行性) | 边界无法稳定区分,合并后 10+ 条 |
| 降级 | action_sufficiency → A 层字段取值 | 与信息状态字段重叠,机制性弱 |
| 保留观察 | multimodal_substitution | 仅 1 条(宏福苑警铃失效→手机群组),但设计含义强,建议扩语料验证 |
| 新增候选 | prior_warning_unheeded(4条)、shelter_in_place_decision(1)、instruction_reversal(1)、reporting_friction(1) | 前两者值得扩语料验证;后两者先观察 |
