# 开放编码 v2.1 AI 第二编码者 — 分歧与疑问

生成：2026-10-21 ｜ 编码者：AI 第二编码者 ｜ 输入：recommended_open_coding_pool.csv（20条）+ recommended_id_chinese_body（中文正文）+ Design_Space_v2.1 codebook + Design Space v2（仅用于理解旧标签）

---

## 一、证据不足但容易误标的记录

| record_id | 风险 | 说明 |
|---|---|---|
| recvswFF5zBxaO | 全条 | 正文纯响应方视角，无任何居民个体的信息-行动链。除"顶层数分钟吞没""一人被困未确认"外全部字段只能填未报告。已标 needs_human_review=true。 |
| recvswFF5zfVk0 | 争吵声 | "邻居在火灾前听到公寓里传来争吵声"是事后归因（管理方转述），**未**编码为 ambiguous_early_cue——它不是危险线索，只是与起火相关的人际前兆。请确认这一处理。 |
| recvswFF5zaKC6 | 母子三人 | 四楼走廊发现母子三人昏迷，但**为何在走廊、如何陷入该状态完全未报告**。极易被误标为"疏散受阻"或"感知失败"，本编码仅记录事实（位置+状态），未推断过程。 |
| recvswFF5zQovO | 宣传性修辞 | "敏锐洞察力""守护安全防线"等为宣传文本，仅采信火光/焦糊味/门缝浓烟等事实性描述。被困者"未察觉"依据是当事人事后自述原句（可靠）。 |
| recvsJ6HjygAnl | 全条 | 证据质量 low：起火原因（祭祀灯）为居民转述推测；"惊慌地下来了"为报道用语，未据此推断心理状态。已标 needs_human_review=true。 |
| recvt0d2bJGyBf | 手印含义 | "为生命而挣扎的有力痕迹"是家属/报道解读，不是行为过程记录。本编码未生成任何候选机制标签，仅保留空间证据。 |

## 二、与 v2 标签边界不清的概念

1. **dynamic_action_space vs state_dependent_affordance**：两者高度相邻。本编码的操作性区分：前者=路径可用性**随时间**重算（火势蔓延、排查推进、指令反转）；后者=**同一空间实体的状态机**（门/电梯/消火栓/通道的状态决定通行性）。案例：香港水柱"鞭长莫及"（两者皆可挂）按 state_dependent_affordance 编码；疏散指令 10 分钟反转按 dynamic_action_space 编码。建议在冻结版 codebook 写明该区分规则。
2. **action_sufficiency vs interpretation_gap**：Vile Parle 案例（recvswFF5zqygs）信息充分且无误解，但"信息触发返回查看"恰恰是致命的——说明"信息充分"不等于"行动正确"。两概念应联合编码，不能互相替代。
3. **social_action_scaffolding vs v2 E3/E6**：v2 的"指引"是动词枚举；本概念强调**依赖关系**（谁使谁的动作变得可行）。消防抬轮椅者、邻居帮开门、消防多次劝说——这些在 v2 只会落到"互救"分类标签，机制层面是空白。
4. **multimodal_substitution 的边界**：马鞍山案例中火光被遮挡→靠嗅觉逐层定位，是"通道失效→替代通道"；香港案例是"警报失效→社会网络替代"。两者都编入了，但前者更接近感知层、后者更接近社会层。若要冻结，建议在定义中明确两条子路径：**感知通道替代** 与 **社会通道替代**。

## 三、人工细节提取与正文冲突/需注意处

1. **两对同事件记录**：recvswFF5zVeD8 与 recvswFF5A8UGK（布朗克斯比沃纳街爆炸，同一事件）；recvswFF5zubYL 与 recvswFF5zjT7u（香港宏福苑，记者直击 vs 人物特写）。池表 duplicate_status 均标 unique，但编码时按同一事件处理并互相注明。**计算 frequency 时若去重，相关概念频次会下降**（multimodal_substitution 4→3，social_action_scaffolding 7→6 等）。
2. **电梯状态两向证据**：香港钦姓妇女**乘电梯**成功下楼（recvswFF5zjT7u）vs 加尔各答米特拉因**电梯关闭**步行 18 楼（recvsJ6HjygAnl）。VR 设计不应默认"火灾=电梯不可用"；正文证据支持两种状态。
3. **香港记录的警铃证据**：recvswFF5zubYL 中"多位不同楼栋的居民没听到警铃"是记者走访原句；recvswFF5zjT7u（路透转写）无此细节。两者不冲突，但警铃失效的证据仅来自前者。
4. **编码位置说明**：recvt0d2bJNZ1D、recvt0d2bJUEZi、recvt0d2bJGyBf 三条中文正文为单段落长文，evidence location 标为"中文正文（单段）"，段落级定位不可用。
5. **CSV 编码**：两份输入 CSV 为 GBK 编码（非 UTF-8），本次已解码处理；后续流水线建议统一 UTF-8。

## 四、需要研究者裁决的项目

| # | 裁决项 | 选项 |
|---|---|---|
| 1 | recvswFF5zBxaO（孟买班德拉）无个体行动链，是否保留在开放编码集？ | 保留（作为环境/响应素材）｜降级｜移出 |
| 2 | recvt0d2bJNZ1D（广州隐患调查）与 recvt0d2bJUEZi（Bristol 门故障）是**事前/未遂**记录，无火灾事件。是否单列"隐患呈现型"子类？ | 单列子类｜留在集合内正常编码｜移出 |
| 3 | recvt0d2bJGyBf（格伦费尔手印墙）纪念类，按 v2 流程"纪念馆式条目标 V_framing 单列备注"。是否移出本轮集合？ | 移出并单列｜保留 |
| 4 | 新增候选概念 informed_sheltering（4条）与 authority_instruction_dynamics（4条）是否进入下一轮比较？ | 进入｜并入现有概念｜删除 |
| 5 | door_interaction_risk（5条）建议并入 cue_to_confirmation 子类而非单列，是否同意？ | 并入｜单列 |
| 6 | aftermath_affordance（3条）建议并入 state_dependent_affordance 加时间参数，是否同意？ | 并入｜单列 |
| 7 | 同事件去重后 frequency 重算，候选概念的"多条独立记录"升级条件（codebook §5）如何计数？ | 按事件去重计数｜按记录计数 |

## 五、候选概念保留/合并/删除建议汇总

| 概念 | frequency_20 | 建议 | 理由 |
|---|---|---|---|
| cue_to_confirmation | 9 | 保留 | 跨洲独立多记录；v2 信息呈现无时间过程 |
| interpretation_gap | 4 | 保留 | "知道但错判"与 v2 "信息缺失"（不知道）边界清晰 |
| action_sufficiency | 6 | 保留 | 梯度概念，覆盖信息两端极端案例 |
| action_chain_break | 12 | 保留 | 频次最高；断点定位是 v2 限制模拟的明确缺口 |
| dynamic_action_space | 10 | 保留（与下条写明区分规则） | 状态随时间重算路径 |
| social_information_mediation | 10 | 保留 | 信息接力（群组→人传人）是 v2 完全空白的机制 |
| social_action_scaffolding | 7 | 保留 | 依赖关系机制，v2 互救标签无法表达 |
| ambiguous_early_cue | 6 | 保留 | 与感知剥夺分属前后阶段，证据均为明示原句 |
| state_dependent_affordance | 10 | 保留 | 含电梯可用/前门被破坏等反直觉状态，纠正默认假设 |
| multimodal_substitution | 4 | 保留（建议定义两条子路径） | 香港警报→群组→人传人替代链证据最完整 |
| informed_sheltering（新增） | 4 | 建议进入下一轮 | 留守是信息驱动的主动决策，非"被困"结果 |
| authority_instruction_dynamics（新增） | 4 | 建议进入下一轮 | 指令反转（不必疏散→全员疏散）是可信张力源 |
| door_interaction_risk（新增） | 5 | 建议并入 cue_to_confirmation | 是后者的特例，单列会双标 |
| aftermath_affordance（新增） | 3 | 建议并入 state_dependent_affordance | 加时间参数即可覆盖 |
