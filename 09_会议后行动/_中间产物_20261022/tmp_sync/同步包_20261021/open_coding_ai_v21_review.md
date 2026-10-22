# 开放编码第二轮（AI 第二编码者）分歧与疑问

对象：第10轮 WB 高层候选 20 条（`recommended_open_coding_pool.csv`）
编码者：AI 第二编码者（独立开放编码，未参考旧人工标签取值）
依据：中文正文（`recommended_id_chinese_body.csv`）；候选池 CSV 的分列摘要仅用于定位，不作为事实来源
输出：`open_coding_ai_v21.jsonl`（20 行）、`codebook_review.csv`（11 行）

---

## 一、证据不足但容易误标的记录

| record_id | 问题 | 易误标之处 |
|---|---|---|
| recvswFF5zBxaO（大西洋大厦） | 全篇无个体视角，只有官方时间线与两名旁观者发言；“可能有一人被困”始终未被官方确认 | 容易被当作“存在被困者→社会救援成功”的完整叙事；实际 `action_chain` 中“确认”环节缺位，不应标 `cue_to_confirmation` |
| recvswFF5zAOlh8（新孟买两起） | 两起火灾并列，个体信息获取过程几乎全缺；84 岁卧床老人“未能及时疏散”的原因正文未写 | 容易被标 `ambiguous_early_cue` / `cue_to_confirmation`（无任何线索描述）；也不应把 84 岁老人的死亡标为身体限制导致的失败——正文未建立因果 |
| recvt0d2bJNZ1D（广州调查） | 非事件新闻，是隐患调查 | 容易被误当作“有火灾场景”从而误标 `dynamic_action_space`；其空间约束是常态隐患（杂物、闭门器坏损、无照明），不是火中状态变化 |
| recvt0d2bJUEZi（布里斯托尔 Gilley House） | 非火灾，是唯一出口门失效的潜在风险 | 容易被误标 `cue_to_confirmation`（无火灾线索）；其价值在“机构把紧急信息降级为非紧急”的响应失效层 |
| recvt0d2bJGyBf（格伦费尔手印墙） | 无行动链、无信息获取过程 | 容易被误标任何行动类候选；实际属后果/遗存议题 |
| recvsJ6HjygAnl（托利甘吉） | 起火原因正文两处冲突（居民推测庙宇灯 vs 初步估计短路），且无个体现场感知 | 容易被当作“已确认的灯引燃”，本轮只记为推测 |
| recvsJ6HjyDgiX（Abbey View） | 只有开门见浓烟一个感知节点，无火中完整行动链；其余为事后处置与舆论 | 容易被标 `social_action_scaffolding` 为“消防/机构互助”，但其证据是事后安置与清洁，与火中行动无因果关系 |
| recvswFF5zAd1CR（Flatbush 两名巴巴多斯遇难者） | 幸存者视角与遇难者视角断裂；两人为何未逃出完全未报告 | 容易被用幸存者的“抓钥匙跑出去”反推遇难者动作，属无证据推断 |

---

## 二、与 v2 标签边界不清的概念

1. **`cue_to_confirmation` vs v2「信息呈现」**
   v2「信息呈现」判定依据是“报道里有伤亡数字、时间线、楼层信息、地图、官方通报”，属叙述层信息；本轮概念判的是线索在事件中被察觉与确认的**过程顺序**。二者判定证据不同，但读者易混。建议在 codebook 中明确写“呈现=文本给了什么；确认=人物何时知道”。

2. **`dynamic_action_space` vs `state_dependent_affordance`**
   20 条中重合 15 条，差异仅在是否强调“同一空间随火/烟/门/救援状态改变可行性”。本轮建议合并为一个概念 + 一个子项，否则两套维度会互相吞噬。

3. **`social_information_mediation` vs v2「社会见证」**
   v2「社会见证」是使用者看到他人痛苦与互助（旁观式）；本轮是信息经由他人/网络传递（中介式）。在 v2 的 `交互_共情机制` 里两者都可能被误选，需要显式区分“看到”与“经由”。

4. **`social_action_scaffolding` vs v2「E6 交互动词」**
   E6 是动作清单（开门、破窗、背负、指引）；本轮强调动作的**社会使能关系**（抬轮椅、逐户敲门引导、砸窗注水、破门救人）。建议 E6 保留动作层，新增一列“动作的社会使能者”。

5. **`action_chain_break` vs v2「限制模拟」/「V处境困难」**
   v2 只判“是否存在约束”，本轮判“约束发生在链条哪一环”。二者同向但不同粒度；建议 `action_chain_break` 作为位置化字段挂在 `限制模拟` 之下，而非平行维度。

6. **`multimodal_substitution` vs `social_information_mediation`**
   本轮 4 条标 `multimodal_substitution` 的实例（甜味→敲门、煤气味→电话、呼救→报警、窗外观看→撤离）实为“他人替代了被削弱的感知通道”，两种读法都成立。这是本轮最需要裁决的边界。

---

## 三、人工细节提取与正文冲突的地方

| 位置 | 冲突 |
|---|---|
| recvswFF5zAd1CR / recvswFF5zAOlh8 等 | 候选池 CSV 的 `sensory_details` / `action_details` 列把“建筑结构、门位置”等场景描述与正文原句混编，本轮未采信其断言性表述（候选池 `spatial_details` 对该条给出的是门/走廊等静态描述，正文实际未提）。 |
| recvswFF5zubYL（香港大埔） | 候选池 `spatial_details` 含窗框材料（推测性结构描述），正文实际表述为“发泡胶板”贴于**住户窗户通风位置**，属住户个人封堵行为而非建筑结构缺陷。二者性质不同，本轮按正文记为住户行为。 |
| recvswFF5zFvJP（曼谷 38 层） | 候选池中多个个体细节（22 层母亲、28 岁老年夫妇）源自社交媒体视频，正文本身标为“社交媒体上的视频显示”。本轮在 `sensory_cue`/`body_context` 保留但未作为事实证据，列入人工复核。 |
| recvswFF5zBxaO | 候选池 `sensory_details` 与正文一致，但正文明确“官员尚未确认”是否有人被困；候选池的 `affected_people_explicitly_named` 类推为空，本轮维持空。 |
| recvsJ6HjygAnl | 正文两处起火原因冲突（居民推测庙宇灯 / 初步估计短路），候选池未标此冲突，本轮已标为 `needs_human_review`。 |
| recvswFHYi0LN2 | 正文两处爆炸位置表述冲突：纽约消防局称“焚化炉竖井”，布朗克斯区主席称“锅炉房”。本轮记入 `uncertainty`。 |
| recvswFF5zjT7u / recvswFF5zubYL | 两条均涉香港宏福苑，但一处记 128 死 200 失踪、一处记 44 死 279 失联，统计口径与时点不同；且是否为同一事件的不同报道需核对。 |

---

## 四、需要研究者裁决的项目

1. **是否保留本轮 20 条中的低证据记录**。recvswFF5zBxaO、recvswFF5zAOlh8、recvsJ6HjygAnl、recvsJ6HjyDgiX、recvt0d2bJNZ1D、recvt0d2bJUEZi、recvt0d2bJGyBf 共 7 条在本轮被标 `needs_human_review=true`：其中 3 条（广州调查、Gilley House、手印墙）并非火灾事件，后 2 条无“信息到行动”链条。若本轮目的是检查 v2 的“信息到行动”机制，这 3 条应移出事件语料、另作“前置条件/响应失效”材料。
2. **`multimodal_substitution` 的边界与存废**（4 条，证据偏弱）。
3. **`dynamic_action_space` 与 `state_dependent_affordance` 是否合并**。
4. **香港宏福苑两条记录是否合并为一条事件**（避免语料重复计数，并统一伤亡口径）。
5. **Brownx 两条纽约记录（recvswFF5zVeD8 与 recvswFF5zA8UGK）是否同一事件的不同报道**：同一地址（比沃纳街）、同一开发项目（波士顿塞科尔住宅）、但死亡与受伤数字不同（1死14伤 vs 1死15伤）。若为同一事件，需去重。
6. **`physical_trace_removal`（格伦费尔手印墙）是否另立一条线**：属“后果呈现/纪念”，与本轮研究问题不同层。

---

## 五、候选概念去留建议

| 概念 | 建议 | 理由 |
|---|---|---|
| `cue_to_confirmation` | 保留 | 12/20 条有可判的确认顺序，跨中印德美港越多国；填补 v2「信息呈现」只判“给了什么”的空缺 |
| `interpretation_gap` | 保留 | 4 条独立证据且是链条必要中间态；v2 完全没有对应维度 |
| `action_sufficiency` | 保留 | 9 条出现且取值可分（足够/不足/冲突）；直接连接“信息”与“行动” |
| `action_chain_break` | 保留 | 19 条有可定位断点；应作为 v2「限制模拟/V处境困难」的位置化子字段 |
| `dynamic_action_space` | 保留（吸收 `state_dependent_affordance`） | 16 条；空间状态时间演化是 v2「环境模拟」缺失的维度 |
| `social_information_mediation` | 保留 | 14 条；直接对应“社会关系如何影响信息获得”，v2 只有旁观式「社会见证」 |
| `social_action_scaffolding` | 保留 | 11 条；与 v2「E6 交互动词」互补而非重复（后者动作、此关系） |
| `ambiguous_early_cue` | 保留 | 6 条；是 `cue_to_confirmation` 的起点，气味只是实例之一（另有争吵声、骚动、火星、煤气味） |
| `state_dependent_affordance` | 合并入 `dynamic_action_space` | 重合 15/20，单列会造成维度重叠；建议作为“空间状态随时间变化”子项 |
| `multimodal_substitution` | 暂缓（hold） | 4 条且多为弱证据；与 `social_information_mediation`、`cue_to_confirmation` 边界不清。建议第二轮编码后复核，若仍无法给出与二者互斥的判定证据则删除 |
| `physical_trace_removal` | 删除（本轮不纳入） | 仅 1 条、属纪念/后果议题，与“信息到行动”不同层；如需保留应挂在 v2「后果呈现」下 |
