# Design Space v2.1 候选开放编码 Codebook

状态：开放编码阶段候选版，不是最终冻结版  
适用对象：第10轮 WB 高层候选 20 条  
输入：`06_工作流产物/第10轮_WB高层筛选/recommended_open_coding_pool.csv` 与 `06_工作流产物/同步包_20261021/recommended_id_chinese_body.xlsx`

## 1. 使用原则

这轮任务是把新闻中的可核验细节整理成候选概念，检查 v2 设计空间是否遗漏关键机制。不要为了填满字段而推断新闻没有写出的身体、感知或动机。每个非空标签都必须有证据句或明确段落定位；“未报告”不等于“没有”。

这轮不要求决定最终 VR 角色，也不要求把每个现象直接归入最终设计空间。新增概念先标为候选，待跨记录比较后再决定是否升级。

## 2. 固定字段

### A. 新闻证据层

| 字段 | 取值/写法 |
|---|---|
| `core_fact` | 一句话写事件、地点、关键后果 |
| `information_source` | 警报、声音、气味、烟雾/火光、手机/社交媒体、邻居/家属、消防员/官方、现场媒体、其他 |
| `information_state` | 未察觉 / 模糊线索 / 已察觉未确认 / 已确认 / 被明确通知 / 信息冲突 / 未报告 |
| `information_interpretation` | 正确理解 / 初始误解 / 无法判断 / 信息不足 / 信息冲突 / 不适用 |
| `information_confirmation_path` | 从线索到确认的顺序，用箭头写，例如“气味→尖叫→开门见烟→确认火灾” |
| `action_chain` | 发现→确认→移动/留守→受阻→求助/互助→结果；缺失环节写“未报告” |
| `action_breakpoint` | 感知、解释、决定、通行、操作、体力/感官、求助、救援响应、结果等待、无明确断点 |
| `spatial_affordance` | 当时可通行/不可通行/条件性通行/随状态变化；写明楼梯、门、走廊、窗、阳台、电梯等 |
| `social_mediation` | 无 / 邻居传递 / 家属传递 / 社区群组 / 消防员或官方 / 路人 / 多方接力；附作用 |
| `body_context` | 正文明确出现的身体、年龄、儿童、轮椅、疾病、行动或感知状态；没有就填未报告 |
| `sensory_cue` | 烟、火光、爆炸声、警报、喊叫、气味、热、震动、黑暗、视觉遮挡等 |
| `evidence_quote` | 支撑本条判断的原文或准确中文译文；一条记录可有多条 |

### B. 候选设计机制层

可多选，但每一项必须能回指 A 层证据。

| 候选概念 | 定义 | 不要这样标 |
|---|---|---|
| `cue_to_confirmation` | 危险线索逐步变成确认信息的过程 | 仅因为出现警报就标 |
| `interpretation_gap` | 线索出现，但人物误解、迟疑或无法判断其含义 | 仅凭“害怕”推断误解 |
| `action_sufficiency` | 信息是否足以支持下一步行动；取足够/不足/冲突/未报告 | 信息出现即等于行动足够 |
| `action_chain_break` | 行动链在感知、判断、通行、操作、求助或救援处断裂 | 把所有困难笼统标为行动中断 |
| `dynamic_action_space` | 烟、火、门、电梯、拥挤、救援等状态使路径随时间改变 | 静态楼梯或房间描述 |
| `social_information_mediation` | 他人或社会网络传递、解释、确认或补足危险信息 | 仅出现邻居但未发挥信息/行动作用 |
| `social_action_scaffolding` | 他人让原本不可行的动作变得可行，如敲门、背负、抬轮椅、引导 | 一般人物出现 |
| `ambiguous_early_cue` | 气味、轻微烟、骚动、远处声响等早期但含义不明确线索 | 已明确确认的火灾信息 |
| `state_dependent_affordance` | 同一空间因火势、烟雾、爆炸、门状态或救援状态而改变可行性 | 只写“有楼梯” |
| `multimodal_substitution` | 一个感官/信息通道失效后，依靠另一通道或他人补偿 | 没有证据的无障碍设计推测 |

## 3. 与 v2 的关系

- `cue_to_confirmation`、`interpretation_gap`、`action_sufficiency`：细化原“信息呈现”，暂不单独冻结为正式维度。
- `action_chain_break`：细化原“限制模拟”和 `V处境困难`，记录断点位置。
- `dynamic_action_space`、`state_dependent_affordance`：细化原“环境模拟”和 E5 移动方式，记录空间状态变化。
- `social_information_mediation`、`social_action_scaffolding`：细化原社会关系与互助机制。
- `ambiguous_early_cue`：保留为候选，气味只是其中一种实例。
- `multimodal_substitution`：用于记录警报失效后依靠手机、邻居、视觉或触觉提示的情况。

## 4. 输出要求

每条记录输出一行 JSON，字段必须完整。多值字段使用数组；没有证据使用空数组或 `未报告`，不要编造。每个候选机制附 `evidence_refs`，引用 `evidence_quote` 的编号。

另附一份 `codebook_review.csv`，每行一个候选概念，包含：`concept`、`frequency_20`、`record_ids`、`distinct_from_v2`、`design_implication`、`keep_as_candidate`、`reason`。

## 5. 升级为设计空间维度的条件

候选概念只有同时满足以下条件，才建议进入下一版正式 Design Space：

1. 至少出现在多条相互独立的记录中；
2. 与现有 v2 概念边界清楚；
3. 会改变 VR 的信息通道、空间状态、行动反馈、角色关系或叙事控制；
4. 能由正文证据支持，而非由 VR 想象反推。
