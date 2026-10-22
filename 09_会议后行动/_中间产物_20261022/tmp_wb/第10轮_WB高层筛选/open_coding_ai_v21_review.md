# open_coding_ai_v21 分歧与疑问

第二编码者（AI）对第 10 轮 20 条高层火灾新闻做开放编码后的分歧记录。仅列需要研究者裁决或复核的事项，不重复编码结果本身。

产物：`open_coding_ai_v21.jsonl`（20 条，evidence_quotes 已逐字回原文校验，0 处失配）、`codebook_review.csv`（17 个候选概念，频次由 jsonl 直接统计）。

---

## 一、证据不足但容易误标的记录

| record_id | 容易被误标成什么 | 正文实际支持什么 |
|---|---|---|
| recvswFF5zBxaO | “居民被困、逃生失败” | 全文无任何住户视角。只有“现场报告表明可能有一人被困”“官员尚未确认”。伤亡与被困均为未确认状态，不可写成事实。 |
| recvswFF5Ad1CR | 80 岁母子死亡 → “身体限制导致无法逃生” | 正文完全没有这两人的察觉、移动、受阻叙述，只写“从受损建筑中被拉出后不治”。年龄是唯一线索，不足以支撑任何断点判断。 |
| recvswFF5AOlh8 | “受害者吸入烟雾失去意识后被烧死”当作已确认 | 该句原文为“两名受害者**很可能**吸入烟雾并失去意识”，属法医推断。与 1205 一家“退入浴室”是两种不同证据等级，混用会污染 action_willingness_gate 与 shelter_in_place_decision。 |
| recvswFF5zFvJP | 22 楼抱幼儿的母亲、28 楼呼吸困难的老年夫妇写入 body_context | 两处均出自“社交媒体上的视频显示”。按任务边界应标“视频线索待核验”，不能作为已核验身体状态；但这两处恰是该条最具设计价值的细节，容易被直接引用。 |
| recvswFF5zfVk0 | “邻居听到争吵声”→ 家庭冲突 / 纵火动机 | 原文仅一句“邻居在火灾前听到公寓里传来争吵声”，无任何因果认定。只能作为未核验的事前线索记录。 |
| recvt0d2bJUEZi | “开门的困难造成恐慌并可能将人困在里面”→ 已发生的逃生失败 | 原文为假设句“**如果**发生火灾，人们疏散，也许在烟雾中……”。全篇没有火灾发生。该条只能支撑“预置脆弱性 + 上报被降级”，不能支撑任何火灾中的实际断点。 |
| recvt0d2bJGyBf | 手印 → 被困者的行动轨迹、滞留位置、通行状态 | 正文只有“楼梯间里留下的铭文和手印”与“12 楼和 14 楼之间”。手印的形成过程、所属个体、当时动作均未报告。该条 10 个候选机制无一有证据，原始 `candidate_mechanisms` 为空数组是刻意留空，不是漏填。 |
| recvswFF5zjT7u | “电梯可作为高层火灾逃生通道” | 钦“乘电梯到了安全地带”是正文原话，但与多数高层火灾电梯停用的结论相反。个案成立，不能外推为设计前提；写入 Design Space 前需明确它的反例地位。 |
| recvt0d2bJNZ1D | 当作一起火灾事件编码 | 全文为广州高层消防调查，无起火事件、无人物行动链。记者本人“侧身挤过、险被绊倒”是唯一动作，属体验性动作，不是住户行动链。 |
| recvswFF5zQovO | “烟雾报警器失效” | 正文只写“全家睡着后未察觉异常，连门外的救援呼喊和敲门声都没听见”，未提该户是否有报警器。只能记为“信息未到达”，不能记为“警报失效”。 |

---

## 二、与 v2 标签边界不清的概念

**1. `action_chain_break` ↔ v2「限制模拟」/「V处境困难」**
19/20 命中，近乎全命中意味着作为单一标签没有区分力——任何火灾都存在某种中断。真正的信息在断点位置：通行 14、救援响应 9、体力/感官 7、感知 6、决定 5、操作 5、结果等待 3、求助 2、解释 2。建议只保留分型后的子概念，或把「断点位置」升级为字段、把「行动链中断」降回 v2 的限制模拟。

**2. `state_dependent_affordance` ↔ `action_chain_break`**
16/20 命中，与上一条大量共线（同一句证据同时支撑“门卡死”和“通行中断”）。二者若不限缩，会一起吞掉全部记录。

**3. `state_dependent_affordance` ↔ `dynamic_action_space`**
前者按“状态”定义，后者按“时间”定义，实操中极难分开：R8「烟雾经通风口扩散使楼梯间变成危险区域」既可读作状态改变也可读作随时间改变。本轮按“是否有明确时序词（先/随后/数分钟后）”勉强区分，判据不稳，需研究者给定优先级。

**4. `multimodal_substitution` ↔ v2「多模态感知剥夺」**
方向相反：v2 做减法（感官被削弱），本概念做加法（通道失效后由另一通道或他人补位）。R3「甜味被误判→砸门声接管」两种读法都成立，是本次最容易双向误标的一对。

**5. `ambiguous_early_cue` ↔ `interpretation_gap`**
前者是线索属性（含义不明确），后者是人的处理（误解/迟疑）。R10「起初，我没在意。我在忙自己的事」两者都像，本轮按“是否点名了替代性解释”区分（有替代性解释→interpretation_gap）。判据可操作但偏细。

**6. `action_sufficiency` 不是机制，是字段**
codebook 自己把它定义为取值型（足够/不足/冲突/未报告）。它无法与 `cue_to_confirmation`、`interpretation_gap` 并列计数，否则同一现象被算两次。建议降为每条记录的一个评分字段。

**7. `social_information_mediation` ↔ v2「社会见证」**
v2 的社会见证是“看到他人痛苦”（共情手段），本概念是“他人把危险信息送到你手上”（信息通道）。概念清楚，但若沿用 v2 的“社会见证”翻译与判定语，会被混为一谈。

**8. `prior_warning_unheeded` 的层级问题**
它不在单条新闻的事件层：R12 的“一年多投诉”、R17 的“三年内同栋再发”、R18 的“2018 至 2025 清理通知无效”，都是跨越数月到数年的制度时间。放进“一次事件的信息—行动链”里会破坏该层的时间一致性。

---

## 三、人工细节提取与正文冲突的地方

**1. `recvswFF5A8UGK` 的 `duplicate_status` 标为 `unique`，但它与 `recvswFF5zVeD8` 是同一事件。**
两条正文都指向布朗克斯波士顿塞科尔住宅 15 楼、燃气爆炸、12:19 起火。VeD8 标了 `same-event-related`，A8UGK 标 `unique`。若不修正，同一事件会被当作两条独立样本计入所有频次。

**2. `recvswFF5A8UGK` 的 `affected_people_explicitly_named` 与实际原文不符。**
该字段三条标注均写作“儿童/婴儿”，但其中两条对应的原文是 `"You know, he's in a wheelchair..."`（轮椅使用者）与 `"The Red Cross reports that they are assisting 56 households and 175 people, including 57 children"`（红十字会总体数据）。轮椅被贴成儿童标签，属明确误标，且这个误标正好抹掉了本条最重要的身体线索。

**3. `recvt0d2bJGyBf` 的 `affected_people_explicitly_named` 依据是纪念修辞，不是本事件受灾者。**
依据原文为 “On this Mother's Day, Grenfell families remember mothers and children who they lost forever”，是家属组织的声明用语，不是该条记录中出现的受灾个体。不应据此标注身体主体。

**4. `recvswFF5zVeD8` 的四个抽取字段内容完全相同。**
`building_evidence`、`event_evidence`、`floor_or_height_evidence`、`information_details` 四列填的都是同一段导语。说明分字段抽取未真正生效，该条的“人工细节提取”实际不含额外线索。

**5. 三条记录的 `title` 被填成了纯数字。**
`recvt0d2bJNZ1D` = `4213`、`recvt0d2bJUEZi` = `5641`、`recvt0d2bJGyBf` = `7165`。标题丢失，只能靠正文与 url 辨认。

**6. `recvt0d2bJUEZi` 的 `information_details` 为空，但正文有本次最集中的“上报失效”证据。**
“打电话的人很难说服接线员这是危及生命的紧急情况”“消防救援局说他们所能做的就是自己打电话给议会”“因为门可以打开，所以不被视为紧急情况”——这三句是 `reporting_friction` 的核心证据，抽取表未收录。同类遗漏也出现在 `recvswFF5zjT7u`（“乘电梯到了安全地带”未进 `information_details`）。

**7. `evidence_quality` 评级与实际可编码度不一致。**
`recvsJ6HjyDgiX` 标 `low` + `source_status: unavailable`，但正文含完整行动链（开门即遇浓黑烟、6 岁女儿、6 户前门被消防损坏、返家未测试），可编码度高于标 `high` 的 `recvswFF5zBxaO`。`recvswFF5zBxaO` 同时标 `high` 与 `source_status: incomplete`，两字段互相矛盾。

---

## 四、需要研究者裁决的项目

1. **同事件对如何处理。** `recvswFF5zVeD8` 与 `recvswFF5A8UGK`（波士顿塞科尔）、`recvswFF5zubYL` 与 `recvswFF5zjT7u`（宏福苑）是否各留一条。本轮两条都编了，但 `codebook_review.csv` 的 `frequency_20` 是记录数，独立事件数会更低（如 `social_information_mediation` 10 条记录实为 9 个事件）。频次口径需先定。
2. **三条非事件类记录是否计入。** `recvt0d2bJNZ1D`（广州调查）、`recvt0d2bJUEZi`（门故障）、`recvt0d2bJGyBf`（手印墙）都不产出生效的信息—行动链。建议单列为“预置状态 / 纪念证据”，不参与 action 类概念计数。
3. **`recvswFF5zjT7u` 的电梯细节如何处置。** 保留为反例注脚，还是作为“电梯在特定火灾中可用”的证据写入空间维度。
4. **`recvswFF5Ad1CR` 是否允许以年龄作为唯一线索。** 若允许，`body_context` 可写 80 岁与 59 岁；若不允许，则该条只剩一名匿名居民的开门见烟。
5. **`recvswFF5zFvJP` 的社交媒体视频细节能否使用。** 22 楼抱幼儿母亲与 28 楼老年夫妇是该条唯一的“弱势群体 + 烟从门下渗入”组合。
6. **外部旁观者视角是否纳入。** `recvswFF5zvlpl` 有一句“对外界来说，从 NH-9 公路和欣登高架路上都能看到的燃烧立面成为了社交媒体上的奇观”——外部可见性成为奇观、内部被困者不知情，这个不对称在 v2 里没有位置，但它是单个案例，本轮未设为候选。
7. **`action_chain_break` 19/20 是否可接受。** 若保留为单一概念，它在统计上等于“所有记录”，无法支撑任何差异化论证。

---

## 五、对候选概念的处置建议

**建议升级为正式维度（跨多条独立记录、边界清楚、能改变 VR 设计）**

| 概念 | 频次 | 理由 |
|---|---|---|
| `door_as_information_boundary` | 7 | 门同时是信息窗口（猫眼 R5、门缝渗烟 R6、开门见火墙 R1）、通行边界（加固门 R6、手动推开 R19）与可被用户动作改变状态的构件（开门致火势加剧 R7）。v2 只把门当“打不开的障碍”，丢掉了一半功能。这是“信息到行动”最直接的缺口。 |
| `shelter_in_place_decision` | 4 | 四种留守形态各不相同：关门堵缝（R5）、退入阳台等救援（R8）、退入浴室（R13）、低层留守（R11）。v2 的移动方式默认所有人都在向外跑。 |
| `social_information_mediation` | 10 | 覆盖最广的社会类概念，证据全是“谁向谁传递了什么”的直接动作，可直接生成 VR 的信息源冲突设计。 |
| `post_event_information_gap` | 4 | 唯一覆盖非在场者（家属、等待返家的居民）的机制：攥手机刷新 R9、“他们什么都不告诉任何人”R10、“只有沉默”R12、返家未测试 R17。 |

**建议限缩或改造**

- `action_chain_break`：只保留断点位置分型，取消“是否中断”这一层。
- `state_dependent_affordance`：限缩为“同一构件在不同时刻或不同状态下的可行性不同”，把预置缺陷（R18、R19）单列为静态子型，否则会与 `dynamic_action_space` 持续混淆。
- `action_sufficiency`：降为字段（足够/不足/冲突/未报告），不作为机制计数。

**保留为候选，待扩充语料**

- `cue_to_confirmation`（10）、`interpretation_gap`（5）、`multimodal_substitution`（4 事件）、`dynamic_action_space`（4）、`social_action_scaffolding`（6 事件）、`ambiguous_early_cue`（4）、`prior_warning_unheeded`（3）、`reporting_friction`（2）、`instruction_reversal`（1 事件）、`action_willingness_gate`（1）。

其中后四个证据偏薄，但不建议现在删除，理由分别是：`prior_warning_unheeded` 支撑的是系统性忽视的论证主线，不能只因频次低而丢；`reporting_friction` 与 `instruction_reversal` 是仅有的两处把“制度摩擦”落到可交互反馈上的证据；`action_willingness_gate`（“许多人害怕走出去，我们不得不说服他们开门”）是全部 20 条里唯一的“信息已到达但行动未启动”，缺失它会把行动失败一律归为能力或环境。

**本轮考虑过但未单列**

- `action_induced_hazard`（用户动作本身触发危险升级，R7 开门致火势加剧）：仅 1 条直接证据，建议并入 `state_dependent_affordance` 作为反向子型。
- `re_entry`（与疏散方向相反的返回，R7 冲回 13 楼、R3 折返取口罩）：2 条，但动机均未报告，无法区分“取物”与“救人”，暂并入 `shelter_in_place_decision` 的决策一侧观察。
- `information_non_arrival`（信息完全未到达且无替代通道，R6 睡熟未听见、R13 睡眠中未察觉）：与 `multimodal_substitution` 构成对照组，建议作为该概念的负例说明，而非独立维度。
- `normative_misjudgment`（“反正邻居也都是这样摆的”，R18）：仅 1 条，且落在制度层而非事件层，暂不列。
- `inspection_information_distortion`（巡查表各项打钩但“障碍物”栏空着，R18）：1 条，作为 `prior_warning_unheeded` 的子证据记录。
