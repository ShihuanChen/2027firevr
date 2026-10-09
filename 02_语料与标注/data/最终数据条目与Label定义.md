# 最终数据条目与Label定义

> 版本: 2026-07-04 | 基于两轮筛选 + VR编码的最终数据结构

---

## 一、最终数据集概览

| 属性 | 值 |
|:---|:---|
| 初始检索 | S0 ≈ 8,900 |
| 去重唯一URL | S1 = 8,072 |
| 有正文（≥100字） | S2 = 140 (目标: Playwright增强后 ≥400) |
| 五维语义通过（≥60分） | S3 = 待评分 |
| 可编码叙事片段 | S4 = 目标 ≥80 |
| 精选样本 | S5 = 目标 50-80 条（每群体 10-15 条） |

---

## 二、数据条目字段定义

每条最终入选的新闻/片段包含以下字段：

```csv
entry_id, source_url, title, full_text, text_length, language, published_date, source_domain,
persona_group, persona_subtype,
round1_score, round1_tier, round2_scores, round2_total_pct, round2_tier,
scene_tier, scene_tags,
narrative_segment_id, axisA_spatial, axisB_constraint, axisC_decision,
vr1_reconstruct, vr2_embody_sensory, vr3_interact_time, vr4_info_gap,
evidence_quote, coder_id, kappa_pair,
notes
```

### 核心字段说明

| 字段 | 类型 | 说明 | 来源阶段 |
|:---|:---|:---|:---|
| `entry_id` | str | 唯一标识符 | 全局 |
| `source_url` | str | 原始新闻链接 | S0 检索 |
| `title` | str | 新闻标题 | S0 检索 |
| `full_text` | str | 抓取到的正文全文 | S2 正文抓取 |
| `persona_group` | enum | 弱势群体类别（见 §三） | S3 五维评分 |
| `persona_subtype` | enum | 亚型（如 low_vision/tunnel_vision/blind） | S4 VR编码 |
| `round2_total_pct` | int | 五维语义评分百分制总分 | S3 五维评分 |
| `round2_tier` | enum | strong_recommend / review / exclude | S3 五维评分 |
| `scene_tier` | enum | S+ / S / A / B / C（场景还原度） | S4 VR编码 |
| `axisA_spatial` | 0-3 | 空间动线评分 | S4 VR编码 |
| `axisB_constraint` | 0-3 | 身体×环境耦合评分 | S4 VR编码 |
| `axisC_decision` | 0-3 | 决策与情感评分 | S4 VR编码 |
| `vr4_info_gap` | str | 信息断裂可体验性（听障/视障核心教学点） | S4 VR编码 |
| `evidence_quote` | str | 原文关键引用 | S4 VR编码 |
| `kappa_pair` | float | 编码者间信度（双人编码时） | S5 精选 |

---

## 三、Label定义

### 3.1 persona_group（弱势群体类别）

| Label | 中文 | 对应总纲角色 | 目标样本量 |
|:---|:---|:---|:---|
| `elderly` | 老年人 | 陈伯 (78岁) | 10-15 条 |
| `hearing_impaired` | 听障者 | 阿May (34岁) | 10-15 条 |
| `visually_impaired` | 视障者 | 威廉 (60岁, 管状视野) | 10-15 条 |
| `mobility_impaired` | 行动障碍者 | 罗姐 (52岁, 轮椅) / 阿福 (40岁, 拐杖) | 10-15 条 |
| `pregnant` | 孕妇 | (待定角色) | 5-8 条 |
| `child` | 儿童 | King仔 (7岁) | 5-8 条 |
| `multiple` | 多群体混合 | 新闻同时涉及多个弱势群体 | 不限 |
| `none` | 无弱势群体 | 仅作为参考/排除 | 不限 |

### 3.2 persona_subtype（亚型）

仅当 persona_group 匹配时使用：

| persona_group | persona_subtype | 说明 |
|:---|:---|:---|
| `visually_impaired` | `low_vision` | 低视力（有残余视力，对比/细节差） |
| `visually_impaired` | `tunnel_vision` | 管状视野（青光眼/RP，中心视力存，周边丧失） |
| `visually_impaired` | `blind` | 全盲（无光感） |
| `mobility_impaired` | `crutches` | 拄拐杖/助行架 |
| `mobility_impaired` | `wheelchair_self` | 手动轮椅（可自主） |
| `mobility_impaired` | `wheelchair_assisted` | 轮椅+无上肢力（需协助） |
| `hearing_impaired` | `deaf` | 全聋 |
| `hearing_impaired` | `hard_of_hearing` | 部分听力损失 |
| `elderly` | `mild` | 轻度行动受限（步速 1.0-1.2 m/s） |
| `elderly` | `severe` | 重度行动受限（步速 0.4-0.6 m/s） |

### 3.3 scene_tier（场景还原度）

| Tier | 含义 | 判定标准 |
|:---|:---|:---|
| `S+` | 极丰富 | 六维标签（空间/声音/视觉/时间/身体/社交）全覆盖，可直接转VR关卡 |
| `S` | 丰富 | 4+ 维度有细节 |
| `A` | 良好 | 3 维度有细节 |
| `B` | 基础 | 1-2 维度有信息 |
| `C` | 不足 | 仅标题信息或极短正文 |

### 3.4 scene_tags（场景六维标签）

| 维度 | 标签示例 | 命中数参考 |
|:---|:---|:---|
| **S**patial 空间 | 高层(≥10层), 楼梯间, 电梯, 窗户/逃生口, 阳台, 浓烟灌满, 走廊/过道, 防火门, 避难层, 能见度<3m | 226 / 34 / 23 / 63 / 16 / 45 |
| **A**udio 声音 | 火警铃, 爆炸声, 敲门/拍门, 邻里呼喊, 消防车警笛, 坍塌声, 信息延迟 | 31 / 31 / 11 / 9 / 8 / 22 / 10 |
| **V**isual 视觉 | 明火可见, 浓烟滚滚, 黑烟, 火光照明, 黑暗, 烟囱效应, 外墙燃烧 | 86 / 32 / 23 / 17 / 9 / 4 / 13 |
| **T**emporal 时间 | 清晨, 深夜/凌晨, 白天, 快速蔓延(<10min), 疏散耗时, 被困时间 | 59 / 22 / 42 / 28 / 14 / 6 |
| **B**ody 身体 | 高温/灼热, 烟雾刺激, 跌倒, 触觉障碍, 呼吸困难, 老年人步速, 轮椅不可通行 | 35 / 22 / 16 / 15 / 2 / 3 / 1 |
| **C**ommunity 社交 | 宠物, 儿童, 家庭单元, 老年人, 恐慌奔逃, 拥挤, 等待救援, 残障者, 孕妇 | 114 / 59 / 48 / 41 / 19 / 18 / 11 / 6 / 1 |

### 3.5 round2_tier（第二轮评分等级）

| Tier | 百分制 | 处理方式 |
|:---|:---|:---|
| `strong_recommend` | ≥75 | 直接进入 S4 VR编码 |
| `review` | 60-74 | 人工复核后决定 |
| `exclude` | <60 | 排除（保留在数据集中备查） |

---

## 四、数据文件清单

| 文件 | 阶段 | 字段 |
|:---|:---|:---|
| `第三轮_标题清单.csv` | S1 | URL, 标题, 来源, 去重状态 |
| `第三轮_含正文.csv` | S2 | +正文, fetch_status, relevance_score |
| `第二轮_精筛.csv` | S3 | +五维评分字段 (round2_*) |
| `第二轮_编码.csv` | S4-S5 | +叙事轴/VR维度编码字段 |
| `高层火灾_最终数据集.json` | S5 | 结构化JSON（便于分析） |

---

## 五、与CHI 2027论文的对应

| 论文章节 | 使用的数据 |
|:---|:---|
| §3.1 Multi-Source Retrieval | S0-S1 检索策略、PRISMA流程图 |
| §3.2 Three-Round Screening | S2-S3 筛选标准、五维评分rubric |
| §3.3 Corpus Statistics | 语言分布、persona分布、scene tag分布 |
| §4 VR Narrative Encoding | S4 编码框架、编码表字段 |
| §5 System Design | S5 精选样本（用于场景设计） |
| Appendix | 完整数据集描述 |
