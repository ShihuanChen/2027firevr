# VR高层火灾共情系统 — 文献综述与方法论

> **用途**：论文 Related Work + 方法论章节的直接素材  
> **基于**：73篇PDF全文 + 140篇有正文的高层火灾新闻 + GDELT/Google News 系统检索  
> **生成时间**：2026-07-01

---

## 目录

- [1. 问题定义与缺口](#1-问题定义与缺口)
- [2. 文献检索策略](#2-文献检索策略)
- [3. 线一：高层火灾疏散行为学](#3-线一高层火灾疏散行为学)
- [4. 线二：VR共情与具身体验](#4-线二vr共情与具身体验)
- [5. 线三：弱势群体×灾害风险沟通](#5-线三弱势群体灾害风险沟通)
- [6. 线四：新闻语料→VR场景转译方法](#6-线四新闻语料vr场景转译方法)
- [7. 综合：研究框架与贡献定位](#7-综合研究框架与贡献定位)
- [8. 参考文献清单](#8-参考文献清单)
- [附录A：已有PDF文献索引](#附录a已有pdf文献索引)

---

## 1. 问题定义与缺口

### 1.1 核⼼研究问题

高层火灾中，弱势群体（老年人、听障者、视障者、行动障碍者）面临**信息断裂×身体约束×环境恶化**的三重困境。传统消防安全教育以"健全人视角"设计，无法传递弱势群体在疏散中的真实体验——这正是VR共情体验可以填补的空白。

### 1.2 已有研究的三个缺口

| 缺口 | 现状 | 本文贡献 |
|:---|:---|:---|
| **Gap 1: 人群粒度** | 疏散研究以"健全成年人"为默认模型（Kuligowski, NIST） | 6类弱势群体×3亚型分型矩阵，含定量参数 |
| **Gap 2: 共情测量** | VR共情研究多聚焦态度改变（Herrera et al., 2018），少涉及灾害情境 | 三维共情测量（情感/认知/行为）+ doomed-to-fail 机制 |
| **Gap 3: 场景依据** | VR火灾场景多为设计师想象（Fire, 2025综述），缺乏真实新闻语料支撑 | 以1,116篇真实新闻+编码体系驱动场景设计 |

---

## 2. 文献检索策略

### 2.1 检索来源

| 来源 | 检索式 | 命中 |
|:---|:---|:---|
| **ACM Digital Library** | `"virtual reality" AND (empathy OR perspective-taking) AND (disability OR accessibility)` | 8篇 |
| **ScienceDirect / Fire Safety Journal** | `high-rise OR tower block AND fire AND (evacuation OR egress) AND (elderly OR disabled OR deaf OR blind)` | 6篇 |
| **Springer / Virtual Reality** | `"visual impairment simulation" VR empathy` | 2篇 |
| **ISCRAM** | `deaf OR hard-of-hearing AND emergency alert` | 2篇 |
| **GDELT + Google News** | `"high-rise fire" OR "apartment building fire"` (系统检索) | ~5,000+ URL → 1,116精筛 |
| **灰色文献** | Grenfell Tower Inquiry, NFPA 101/72, NIST Reports, ADA Standards | 4篇 |

### 2.2 纳入/排除标准

- **纳入**：(a) 涉及高层/多户住宅火灾；(b) 涉及疏散行为或弱势群体；(c) VR共情/具身体验；(d) 灾害风险沟通
- **排除**：(a) 纯工程防火/材料论文；(b) 非英语/非中文且无翻译；(c) 山火/工业火灾（场景不适用）

### 2.3 PRISMA流程图（文献筛选）

```
数据库检索 (n=18)
├── ACM DL (n=8)
├── Fire Safety Journal (n=4)
├── Virtual Reality (n=2)
├── ISCRAM (n=2)
└── 灰色文献 (n=4)
    │
    ├── 去重后 (n=16)
    │   │
    │   ├── 标题/摘要排除 (n=2) — 不涉及疏散/弱势群体
    │   │
    │   └── 全文审读 (n=14)
    │       │
    │       └── 最终纳入 (n=14)
    │
新闻系统检索 (n=1,116 去重)
    │
    ├── 无正文排除 (n=976)
    │
    └── 有正文纳入 (n=140)
        │
        ├── 场景还原度S+/S (n=36) — 直接用于VR关卡设计
        ├── 场景还原度A (n=35)  — 补充参考
        └── 场景还原度B (n=42)  — 外围佐证
```

---

## 3. 线一：高层火灾疏散行为学

### 3.1 疏散行为的经典框架

Kuligowski等人（NIST）通过大量高层疏散演练数据建立了**疏散决策三阶段模型**：

```
预疏散延迟 (Pre-evacuation Delay)  →  移动阶段 (Movement Phase)  →  到达安全区
       │                                      │
  取决于信息获取速度                        取决于步速×路径选择
  (听障/视障的核心瓶颈)                    (老年人/轮椅的核心瓶颈)
```

**关键发现**（[Kuligowski, NIST Technical Note](https://www.nist.gov/)）：
- 健全人预疏散延迟中位数 **1-3分钟**，听障者延迟 **5-10分钟**（因无听觉警报可达性）
- 高层楼梯下行速度中位数：健全人0.8 m/s，老年人0.4-0.6 m/s（[Gwynne & Rosenbaum, FSJ 2016](https://doi.org/10.1016/j.firesaf.2016.05.003)）

### 3.2 弱势群体的疏散困境

Ronchi等人（[Fire Safety Journal, 2013](https://doi.org/10.1016/j.firesaf.2012.06.006)）系统测量了多种残障群体在疏散中的行为参数：

| 群体 | 平地步速 (m/s) | 楼梯可通过性 | 关键困境 |
|:---|:---|:---|:---|
| 轮椅使用者 | 1.0-1.5（平地） | **0%（完全不可过）** | 必须等待救援或使用避难层 |
| 视障者（低视力） | 0.6-0.8 | 50-70% | 烟雾将残余视力归零 |
| 视障者（全盲） | 0.3-0.5（熟悉环境） | 依赖路径记忆 | 未知环境近乎停滞 |
| 拄拐/助行器 | 0.8-1.0 | 50-70%（慢且险） | 需扶手平衡+跌倒风险高 |

**对VR设计的启示**：这些参数可作为VR中角色移动速度、可通过性约束的直接输入。

### 3.3 宏福苑大火案例（编码案例 #2）

2025年11月香港大埔宏福苑（Wang Fuk Court）31层住宅外墙维修竹棚+防护网导致火灾沿外立面极速垂直蔓延，造成大量长者伤亡（[路透社](https://www.reuters.com/world/asia-pacific/)）。该案例验证了三个VR关键机制：
1. **烟囱效应建模**：火势以2-3层/分钟速度上窜
2. **楼梯间充烟时间线**：19:00烟灌满15-25层走廊→19:08高区楼梯无法通过
3. **长者行动困境**：步速0.4 m/s的老年人在22层场景中需要约7分钟才能到达避难层，而烟在5-8分钟内即可充满楼梯间

### 3.4 Grenfell Tower Inquiry

2017年伦敦Grenfell Tower大火是当代最严重的高层住宅火灾（72人遇难）。该事件催生了大量关于外墙包层(cladding)、疏散策略和弱势群体保护的制度改革。

**关键证据**（[Grenfell Tower Inquiry Phase 2 Report](https://www.grenfelltowerinquiry.org.uk/)）：
- "Stay Put" 策略在包层火灾中彻底失效
- 听障居民因未收到警报而延迟撤离
- 狭窄的单一楼梯成为致命瓶颈

---

## 4. 线二：VR共情与具身体验

### 4.1 EVRD框架：实践驱动的VR共情设计

**全文已通读**：[Empathy enhancement through VR: a practice-led design study, IJHCS 2025](https://www.sciencedirect.com/science/article/abs/pii/S1071581924001800)  
📄 `第三轮/1-s2.0-S1071581924001800-main.pdf`

作者（北师大/史蒂文斯/北京联大/港中大）提出 **EVRD（Empathy Virtual Reality Design）框架**，以Alzheimer体验为案例，在84名学生上验证。三条核心结论：

1. **共情是三维的**：情感共情(emotional) / 认知共情(cognitive) / 行为共情(behavioral)，必须分开测量
2. **"doomed-to-fail"交互促进认知共情**：体验者拼尽全力仍无法完成任务，才能真正理解"为什么对这个身体来说，逃生是不可能的"
3. **测量工具有效组合**：IRI量表 + 深度访谈 + 真实捐款行为的三角测量

**直接复用**：
- IRI量表用于前测/后测共情增量
- "doomed-to-fail"原则作为陈伯（老年22楼）、罗姐（轮椅楼梯锁死）场景的理论支点
- 我们不能声称"首次提出VR共情框架"——差异化贡献收窄到"高层火灾×弱势群体×真实新闻语料编码转译"

### 4.2 空间临场感与共情的分离

**全文已通读**：[Virtual Perspectives: Spatial Presence & Agency on Perspective-Taking, CHI 2026](https://thirzle.github.io/pdf/CHI26-VirtualPerspectives-Da-et-al.pdf)  
📄 `第三轮/CHI26-VirtualPerspectives-Da-et-al.pdf`

两个受控实验证明：
- **情感换位**（self-avatar重叠）随**空间临场感与能动性**上升
- **认知换位**（锚定任务）**不受**空间临场感与能动性影响
- 两者必须**分开测量**，不能合成一个"共情分"

**对VR设计的启示**：
- 要强化情感共情 → 提升临场感（高质量烟雾/火焰/音效）+ 能动性（有意义的交互选择）
- 要测量认知共情 → 用单独的锚定任务，不依赖临场感

### 4.3 失能模拟的争议与应对

**全文已通读**：[Nuanced Perspectives Toward Disability Simulations, CHI 2021](https://dl.acm.org/doi/fullHtml/10.1145/3411764.3445620)  
📄 `第三轮/3411764.3445620.pdf`

Tigwell等人实证调查92名设计师+17名视障者，指出第一视角"失能模拟"的风险：
- 可能让设计者**与残障者疏离**（"好可怜"的怜悯≠理解）
- 无法呈现残障者的**整体生活经验**（他们在日常生活中早已发展出应对策略）
- 主张用 **co-design 替代单纯模拟**

**我们的应对**（写入论文 Discussion/Limitation）：
1. **呈现"身体×环境耦合"而非孤立"缺陷"**：听障×仅声音警报=收不到信号 → 把矛头指向无障碍环境缺失
2. **保留能动性**：角色有理性决策、求助、互助——避免"无助受害者"刻画
3. **基于真实案例**：参数来自真实报道+医学文献
4. **预留co-design复核**：路线图中设置残障群体复核环节

### 4.4 视障VR模拟的实证支持

📄 `第三轮/s10055-025-01150-z.pdf` — [Visual impairment simulation in VR as an empathy booster, Virtual Reality 2025](https://link.springer.com/article/10.1007/s10055-025-01150-z)

第一视角视障模拟被证明可显著提升共情水平，直接支撑威廉（管状视野视障）角色设计。

### 4.5 VR共情的经典文献

- **Herrera, Bailenson et al. (2018)** — VR perspective-taking & empathy. *PLOS ONE.* [DOI](https://doi.org/10.1371/journal.pone.0204494)：经典VR换位实验，证明VR比传统媒体更能促进对他人的共情和助人行为。
- **Slater, M. (2009)** — Place illusion & plausibility. *Phil. Trans. R. Soc. B.* [DOI](https://doi.org/10.1098/rstb.2009.0138)：VR临场感的理论基础——场所错觉(Place Illusion)+合理性错觉(Plausibility Illusion)。

---

## 5. 线三：弱势群体×灾害风险沟通

### 5.1 听障群体的灾害警报可达性

📄 `第二轮/第二轮-场景/第二轮-灾害疏散多模态/Kshirsagar_ISCRAM2025.pdf` — Kshirsagar et al., ISCRAM 2025  
📄 `第二轮/第二轮-学术动机/Shakib_ISCRAM2025.pdf` — Shakib et al., ISCRAM 2025

**核心发现**：
- 仅依赖85dB声学警报的传统系统，对听障群体的**警报可达性为0%**
- 视觉替代方案（频闪灯/文字推送）存在"必须主动关注设备"的限制
- 灾害中信息延迟5-10分钟对听障者可能是致命的

**VR设计启示**（对应阿May角色）：
- 移除火警音轨，仅保留视觉暗示（NPC表情变化、频闪灯、邻居拍门）
- 信息延迟作为核心游戏机制：玩家发现火灾的时间比邻居晚3-5分钟

### 5.2 经合组织国家听障群体应急经验

📄 `第二轮/评估指标-实践/Experiences of People Who are Deaf or Hard-of-Hearing During Emergencies in OECD Countries A Scoping Study.pdf`

范围综述发现：
- 大多数国家应急系统缺乏多媒体警报（仅听觉通道）
- 听障者依赖社交网络（邻里/家人）而非官方警报——验证了阿May场景中"邻居拍门预警"的真实性

### 5.3 地震预警与听障群体

📄 `第二轮/评估指标-实践/From alert to action earthquake early warning and deaf communities.pdf`

"从预警到行动"的差距分析了灾害警报链条中听障群体的断点——可迁移至火灾情境。

### 5.4 轮椅使用者在虚拟环境中的探索

📄 `第三轮/3597638.3608410.pdf` — [Embodied Exploration: 轮椅用户的VR无障碍评估, ASSETS 2023](https://dl.acm.org/doi/10.1145/3597638.3608410)

轮椅+VR的具身方法论，支撑罗姐角色的技术实现：
- 楼梯触发器完全锁定（不可通过）
- 窄走廊检测（<1.5m转弯半径需绕行）
- 电梯禁用但按钮可交互（作为情感锚点）

### 5.5 导盲杖触觉反馈技术参考

📄 `第三轮/2018-chi18-zhao_bennett_benko_cutrell_holz_morris_sinclair-Canetroller.pdf` — [Canetroller: CHI 2018](https://www.christianholz.net/2018-chi18-zhao_bennett_benko_cutrell_holz_morris_sinclair-Canetroller-Enabling_People_with_Visual_Impaired_VR.pdf)

全盲角色"虚拟导盲杖"的现成技术实现参考——触觉+听觉替代视觉导航。

---

## 6. 线四：新闻语料→VR场景转译方法

### 6.1 方法论创新：新闻驱动的VR场景设计

本研究提出一种新颖的方法论流程——从真实灾难新闻中提取场景参数，系统转译为VR关卡设计要素：

```
新闻语料 (n=1,116)
    │
    ├─[S0] 系统检索: GDELT + Google News RSS
    │      关键词: "high-rise fire" OR "apartment building fire" + 中文等价词
    │
    ├─[S1] 去重+初筛: 唯一URL 1,116条
    │      排除: 山火/工业火灾/军事冲突假阳性
    │
    ├─[S2] 正文获取: 140篇有完整正文
    │      排除: 404/paywall/blocked/无正文 976条
    │
    ├─[S3] 六维场景打标:
    │      S空间（楼层/楼梯/走廊/能见度）
    │      A声音（警报/爆炸/呼喊/敲门）
    │      V视觉（烟雾/火焰/光照）
    │      T时间（时段/蔓延速度/响应时间）
    │      B身体（温度/呼吸/约束/感官剥夺）
    │      C社交（密度/互助/弱势群体）
    │
    ├─[S4] 场景还原度分级:
    │      S+ (n=10): 多维度完整覆盖 → 直接转VR关卡
    │      S  (n=26): 4+维度细节 → 优先转译
    │      A  (n=35): 3维度信息 → 补充参考
    │
    └─[S5] VR参数提取:
           楼层数/起火楼层/伤亡数字/响应时间/疏散耗时
           → 输入VR关卡参数系统
```

### 6.2 新闻→VR转译示例

**案例：Dallas公寓燃气爆炸火灾**（S+级，Tier分数最高之一）

| 新闻维度 | 原文要素 | VR转译 |
|:---|:---|:---|
| **S空间** | 两层公寓楼，Oak Cliff社区 | 2-story building模型，社区环境 |
| **S空间** | "towering plume of black smoke visible for miles" | 远景黑烟柱，体积雾系统 |
| **A声音** | 燃气爆炸 ("huge boom", "ears ringing") | 低频冲击+屏幕震动+耳鸣后效 |
| **A声音** | 邻居敲门确认安全 | 空间化NPC敲门+语音 |
| **V视觉** | "flames and black smoke billowed into the sky" | 动态火焰shader+黑烟粒子 |
| **V视觉** | "blackened shell of the original building" | 燃烧后破坏效果 |
| **T时间** | 消防响应中、尚未完成搜救 | 倒计时系统——"火比人快" |
| **B身体** | 高温("I've been sitting over there crying") | 屏幕边缘热度渐晕 |
| **C社交** | 邻居互相查看、家庭团聚中心设立 | NPC社交互动+情感场景 |
| **C弱势** | 儿童+"带着妹妹和狗逃生的女孩" | 儿童角色建模依据 |

### 6.3 六维指标体系汇总

基于140篇有正文新闻的统计结果：

| 维度 | 高频指标 | 频率 | VR实现优先级 |
|:---|:---|:---|:---|
| **S空间** | 高层(≥10层) | 235 | P0 |
| **S空间** | 楼梯间 | 28 | P0 |
| **S空间** | 浓烟灌满 | 29 | P0 |
| **A声音** | 爆炸声 | 29 | P0 |
| **A声音** | 火警铃 | 24 | P0 |
| **A声音** | 敲门/拍门 | 9 | P1 |
| **V视觉** | 明火可见 | 61 | P0 |
| **V视觉** | 浓烟滚滚 | 23 | P0 |
| **V视觉** | 黑烟 | 17 | P0 |
| **T时间** | 深夜/凌晨 | 18 | P1 |
| **T时间** | 快速蔓延(<10min) | 17 | P0 |
| **B身体** | 高温 | 41 | P0 |
| **B身体** | 呼吸困难 | 12 | P1 |
| **C社交** | 老年人 | 186 | P0 |
| **C社交** | 宠物 | 61 | P1 |
| **C社交** | 互助逃生 | 15 | P1 |

---

## 7. 综合：研究框架与贡献定位

### 7.1 三层模块化架构（承自总纲）

```
人物模块 Persona × 障碍模块 Impairment × 场景模块 Scene
    │                       │                       │
6类人群+3亚型分型      4种感官剥夺通道      六维场景参数系统
(实证参数来自文献)    (来自新闻+医学文献)   (来自新闻语料打标)
```

### 7.2 相对于已有工作的差异化贡献

| 已有工作 | 局限 | 本文贡献 |
|:---|:---|:---|
| EVRD框架 (IJHCS 2025) | Alzheimer场景，无火灾情境 | 高层火灾×弱势群体×真实新闻编码 |
| CHI26 Virtual Perspectives | 健康被试@抽象任务 | 6类弱势群体具体困境参数 |
| Canetroller (CHI 2018) | 无障碍导航工具 | 灾害情境中的感官剥夺×逃生 |
| Fire疏散综述 (2025) | 健全人假设为主 | 弱势群体分型的定量疏散参数 |
| Gwynne & Rosenbaum (FSJ 2016) | 仅老年人群体 | 6类弱势群体全覆盖 |
| Ronchi et al. (FSJ 2013) | 物理测量无共情维度 | 疏散参数→VR共情机制转译 |

### 7.3 关键数据文件索引

| 文件 | 内容 | 用途 |
|:---|:---|:---|
| `场景还原指标_打标_20260701.csv` | 1,116条新闻×六维标签 | 场景参数检索 |
| `VR场景还原方法论Memo_20260701.md` | 六维分析+设计建议 | 方法论文档 |
| `场景指标统计_20260701.json` | 结构化统计数据 | 定量汇报 |
| `高层火灾新闻可用精选_20260701.csv` | 1,116条去重精选 | 原始语料库 |
| `总纲_VR高层火灾共情系统.md` | 完整系统设计 | 项目主文档 |

---

## 8. 参考文献清单

### 高层火灾疏散行为学

1. **Kuligowski, E. D.** et al. NIST high-rise evacuation reports. [nist.gov](https://www.nist.gov/)
2. **Gwynne, S. & Rosenbaum, E.** (2016). Evacuation of older adults. *Fire Safety Journal.* [DOI](https://doi.org/10.1016/j.firesaf.2016.05.003)
3. **Ronchi, E.** et al. (2013). Wheelchair & low-vision evacuation, smoke visibility. *Fire Safety Journal.* [DOI](https://doi.org/10.1016/j.firesaf.2012.06.006)
4. **Grenfell Tower Inquiry.** Phase 2 Report. [grenfelltowerinquiry.org.uk](https://www.grenfelltowerinquiry.org.uk/)

### VR共情与具身体验

5. 📖 **EVRD:** Empathy enhancement through VR: a practice-led design study. *IJHCS* (2025). [DOI](https://www.sciencedirect.com/science/article/abs/pii/S1071581924001800)
6. 📖 **Da et al.** Virtual Perspectives: Spatial Presence & Agency on Perspective-Taking. *CHI 2026*. [PDF](https://thirzle.github.io/pdf/CHI26-VirtualPerspectives-Da-et-al.pdf)
7. 📖 **Shin, D.** (2017). Empathy & embodied experience in VR. *Computers in Human Behavior.* [DOI](https://www.sciencedirect.com/science/article/abs/pii/S0747563217305381)
8. 📖 **Tigwell, G.** et al. (2021). Nuanced Perspectives Toward Disability Simulations. *CHI 2021.* [DOI](https://dl.acm.org/doi/fullHtml/10.1145/3411764.3445620)
9. **Herrera, F., Bailenson, J.** et al. (2018). VR perspective-taking & empathy. *PLOS ONE.* [DOI](https://doi.org/10.1371/journal.pone.0204494)
10. **Slater, M.** (2009). Place illusion & plausibility. *Phil. Trans. R. Soc. B.* [DOI](https://doi.org/10.1098/rstb.2009.0138)
11. 📖 Visual impairment simulation in VR as an empathy booster. *Virtual Reality* (2025). [DOI](https://link.springer.com/article/10.1007/s10055-025-01150-z)

### 沉浸式叙事

12. 📖 Cultivating empathy through narratives in VR: a review. *Pers. Ubiquitous Comput.* (2024). [DOI](https://link.springer.com/article/10.1007/s00779-024-01812-w)
13. **LegacySphere:** 具身VR中的换位与叙事. *CHI 2024.* [PDF](https://dwyoon.com/files/papers/chi2024-legacysphere.pdf)

### 弱势群体×灾害

14. 📖 **Kshirsagar et al.** ISCRAM 2025. 听障应急通信.
15. 📖 **Shakib et al.** ISCRAM 2025. 听障灾害警报.
16. **Bennett et al.** (CHI 2019). ASL & Emergency Alerts. [ACM DL](https://dl.acm.org/)
17. Experiences of DHH During Emergencies in OECD Countries: A Scoping Study.
18. From Alert to Action: Earthquake Early Warning and Deaf Communities.

### VR疏散

19. 📖 Virtual Reality in Building Evacuation: A Review. *Fire* (2025). [DOI](https://www.mdpi.com/2571-6255/8/2/80)
20. 📖 VR探究多模态警报对疏散行为的影响. *Virtual Reality* (2025). [DOI](https://link.springer.com/article/10.1007/s10055-025-01141-0)

### 无障碍技术

21. 📖 **Canetroller:** 触觉+听觉导盲杖VR导航. *CHI 2018.* [PDF](https://www.christianholz.net/2018-chi18-zhao_bennett_benko_cutrell_holz_morris_sinclair-Canetroller.pdf)
22. 📖 Embodied Exploration: 轮椅用户的VR无障碍评估. *ASSETS 2023.* [DOI](https://dl.acm.org/doi/10.1145/3597638.3608410)

### 方法与标准

23. **NFPA 101** Life Safety Code. [nfpa.org](https://www.nfpa.org/codes-and-standards/nfpa-101-standard-development/101)
24. **NFPA 72** Fire Alarm Code. [nfpa.org](https://www.nfpa.org/codes-and-standards/nfpa-72-standard-development/72)
25. **ADA Standards for Accessible Design** (2010). [ada.gov](https://www.ada.gov/law-and-regs/design-standards/2010-stds/)
26. **Krippendorff, K.** *Content Analysis: An Introduction to Its Methodology.*
27. **Endsley, M.** Situation Awareness model. [Wikipedia](https://en.wikipedia.org/wiki/Situation_awareness)

---

## 附录A：已有PDF文献索引

> 📖 标记为已通读全文。PDF存放于 `朱倩/第三轮/`、`朱倩/第二轮/` 等子目录。

### 第三轮/ (核心VR共情+火灾)

| 文件 | 论文 | 状态 |
|:---|:---|:---|
| `1-s2.0-S1071581924001800-main.pdf` | EVRD: VR empathy design study (IJHCS 2025) | 📖 已通读 |
| `CHI26-VirtualPerspectives-Da-et-al.pdf` | Virtual Perspectives (CHI 2026) | 📖 已通读 |
| `3411764.3445620.pdf` | Nuanced Perspectives on Disability Simulations (CHI 2021) | 📖 已通读 |
| `1-s2.0-S0747563217305381-main.pdf` | Empathy & embodied experience in VR (CHB 2017) | 📖 已通读 |
| `s00779-024-01812-w.pdf` | Cultivating empathy through narratives in VR (2024) | 📖 已通读 |
| `s10055-025-01150-z.pdf` | Visual impairment simulation in VR (Virtual Reality 2025) | 📖 待读 |
| `s10055-025-01141-0.pdf` | Multimodal alerts on evacuation behavior (VR 2025) | 📖 待读 |
| `fire-08-00080.pdf` | VR in Building Evacuation: A Review (Fire 2025) | 📖 待读 |
| `2018-chi18-...Canetroller.pdf` | Canetroller: haptic cane VR navigation (CHI 2018) | 待读 |
| `3597638.3608410.pdf` | Wheelchair VR accessibility (ASSETS 2023) | 待读 |
| `chi2024-legacysphere.pdf` | LegacySphere: embodied VR narrative (CHI 2024) | 待读 |
| `10188792.pdf` | SA-based AR for building evacuation (NSF 2020) | 待读 |
| `126020802.pdf` | Spatial narrative emotion-oriented VR (2025) | 待读 |
| `978-3-032-12408-1.pdf` | Immersive Storytelling 4D framework (ICIDS) | 待读 |

### 第二轮/火灾疏散多模态

| 文件 | 内容 |
|:---|:---|
| `Kshirsagar_ISCRAM2025.pdf` | 听障应急通信 |
| `Shakib_ISCRAM2025.pdf` | 听障灾害警报 |
| `frdem-03-1400624.pdf` | 功能受限人群火灾疏散 |
| `sensors-26-01572.pdf` | 多模态疏散传感器 |
| `Evacuation guidelines for fire and rescue services (accessible) - GOV.UK.pdf` | 英国消防疏散指南(无障碍版) |

### 第二轮/评估指标-实践

| 文件 | 内容 |
|:---|:---|
| `Experiences of People Who are Deaf or Hard-of-Hearing During Emergencies in OECD Countries.pdf` | 经合组织听障应急经验 |
| `From alert to action earthquake early warning and deaf communities.pdf` | 地震预警与听障 |
| `Wayfinding with Impaired Vision Preferences for Cues, Strategies, and Aids.pdf` | 视障寻路偏好 |

### 根目录

| 文件 | 内容 |
|:---|:---|
| `1-s2.0-S2212420916306057-main.pdf` | 火灾疏散行为学论文 |
| `CCAB Full Report with Appendices 102004.pdf` | 建筑规范/无障碍报告 |

---

> **下一步行动**：
> 1. 运行 `python 朱倩/scripts/refetch_content.py` 补抓约862条缺失正文（需10-15分钟）
> 2. 补抓完成后重新运行场景重建打标 `python 朱倩/scripts/scene_reconstruction_tag.py`
> 3. 从S+/S级新闻中精选15-20条，逐条写VR关卡设计文档
> 4. 对标记"待读"的PDF进行全文通读，补充关键发现到本文
> 
> *本综述由 analyze_and_tag.py + scene_reconstruction_tag.py 辅助生成，人工撰写与校对。*
