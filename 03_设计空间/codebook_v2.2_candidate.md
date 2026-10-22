# Codebook v2.2 candidate

状态：候选版。用于第二批补搜验证，未冻结。

每条记录必须有正文证据；未出现填“未报告”，不按常识补全。

| 字段 | 类型 | 取值 |
|---|---|---|
| `information_source` | 多选 | 警报、声音、气味、烟/火光、手机/社交媒体、邻居/家属、消防员/官方、媒体、其他 |
| `information_state` | 单选 | 未察觉、模糊线索、察觉未确认、已确认、被通知、冲突、未报告、不适用 |
| `information_interpretation` | 单选 | 正确理解、初始误解、无法判断、信息不足、冲突、未报告、不适用 |
| `action_sufficiency` | 单选字段 | 足够、不足、冲突、未报告、不适用 |
| `action_breakpoint` | 多选 | 感知、解释、决定、通行、操作、身体/感官、求助、救援响应、结果等待、未报告、不适用 |
| `dynamic_action_space` | 多选 | `temporal_change`、`component_state`、未报告、不适用 |
| `social_information_mediation` | 多选 | 邻居、家属、社区群组、消防员/官方、电话/短信、路人、机构接力、无、未报告 |
| `social_action_scaffolding` | 多选 | 破门、搬运/抬人、引导、协助移动、提供物资、劝说行动、无、未报告 |
| `ambiguous_early_cue` | 多选 | 气味、声音/骚动、烟、火光、其他、无、未报告 |
| `interpretation_gap` | 多选 | 日常化误判、危险低估、来源冲突、信息含义不明、无、未报告 |
| `multimodal_substitution` | 多选 | 感官通道替代、社会信息通道替代、无、未报告 |
| `material_type` | 单选 | 实时事件、隐患/未遂、纪念/灾后、政策/机制支持、其他 |
| `event_id` | 文本 | 同一事件使用同一 ID；无法确认写 `event_uncertain` |

## 候选子类

`door_as_information_boundary`、`shelter_in_place_decision`、`post_event_information_gap` 暂放 `candidate_subclass`，只有跨独立事件反复出现并改变 VR 设计决策时才升级。

## 输出

逐条 JSONL、概念审查 CSV、分歧 Markdown。每次模型运行建立独立文件夹，命名为 `模型_版本_日期_运行号`，禁止覆盖其他模型或上一轮文件。
