# Design Space v2.2 candidate

状态：候选版，待第二批补搜验证与老师确认范围

## 核心结构

`线索出现 → 确认与解释 → 行动充分性/断点 → 动态可行动空间 → 社会中介与行动支架`

| 层 | 核心字段/概念 | 说明 |
|---|---|---|
| 线索出现 | `information_source`、`ambiguous_early_cue` | 气味、声音、烟、火光、手机、邻居、消防员等 |
| 确认与解释 | `information_state`、`cue_to_confirmation`、`interpretation_gap` | 线索如何逐步确认，是否被误解或低估 |
| 行动 | `action_sufficiency`、`action_breakpoint` | 信息是否足够；断点位置为感知、解释、决定、通行、操作、身体/感官、求助、救援响应、结果等待 |
| 空间 | `dynamic_action_space` | `temporal_change` 与 `component_state` 两个子类 |
| 社会 | `social_information_mediation`、`social_action_scaffolding` | 谁传递/解释信息，谁让行动变得可行 |

## 暂存子类

- `multimodal_substitution`：感官通道替代 / 社会信息通道替代；
- `door_as_information_boundary`：门作为信息窗口、通行边界和风险状态构件；
- `shelter_in_place_decision`：封门、退入浴室、阳台待援等留守策略；
- `post_event_information_gap`：灾后或非在场者的信息空缺。

## 气味线索

气味属于 `information_source` 与 `ambiguous_early_cue` 的实例。若气味导致误判，另标 `interpretation_gap`；若气味与烟、火光或他人通知共同完成确认，写入 `cue_to_confirmation`。首版 VR 可模拟气味的叙事功能，不要求真实气味硬件。
