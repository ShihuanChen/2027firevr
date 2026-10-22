# -*- coding: utf-8 -*-
"""由 open_coding_ai_v21.jsonl 派生 codebook_review.csv（频次不手填，全部来自编码结果）"""
import json, csv, os, collections

D = os.path.dirname(os.path.abspath(__file__))
rs = [json.loads(l) for l in open(os.path.join(D, "open_coding_ai_v21.jsonl"), encoding="utf-8")]

cnt = collections.OrderedDict()
for r in rs:
    for m in r["candidate_mechanisms"]:
        cnt.setdefault(m["concept"], []).append(r["record_id"])

# 同事件去重（用于判断“独立记录数”）
SAME_EVENT = {
    "recvswFF5zVeD8": "bronx_boston_secor",
    "recvswFF5A8UGK": "bronx_boston_secor",
    "recvswFF5zubYL": "taipo_wangfuk",
    "recvswFF5zjT7u": "taipo_wangfuk",
}
def indep(ids):
    seen, out = set(), []
    for i in ids:
        k = SAME_EVENT.get(i, i)
        if k not in seen:
            seen.add(k); out.append(i)
    return out

ROWS = [
 dict(concept="cue_to_confirmation",
  distinct_from_v2="v2“信息呈现”只要求披露隐患与风险，无时间结构；本概念要求线索→确认的时序推进，可独立判定。",
  design_implication="决定 VR 信息投放节奏：先给弱线索、再给可确认证据，让体验者经历“不确定→确定”的过渡，而非开场即告知。",
  keep="是",
  reason="10/20、10 个独立事件，且能区分“直接目视火焰”（如 R4）与“多步推进”（如 R3 气味→砸门、R6 火光→气味梯度→门缝烟）。建议升级为信息通道维度的时序子项。"),
 dict(concept="interpretation_gap",
  distinct_from_v2="v2 无“误解”位置：多模态感知剥夺只写感知被削弱，不写被削弱后如何被错误归因。",
  design_implication="支撑 VR 的关键张力：给体验者真实的模糊线索（甜味/怪味/走廊骚动），但不给正确答案，让错误归因成为可体验的一步，再以环境证据纠正。",
  keep="是",
  reason="5/20、5 个独立事件，四例均为“气味或骚动被归因为日常”（R3 甜味→烹饪、R5 怪味→烧糊、R10 骚动→没在意）。证据干净，边界清楚。"),
 dict(concept="action_sufficiency",
  distinct_from_v2="v2 无“信息是否够用”的判定；现有标签只描述信息呈现方式，不评价其是否支撑下一步动作。",
  design_implication="可作为每条场景的信息-行动匹配度评分，用于设计“信息充足但路径不可行”“信息不足却必须决策”两类不同关卡。",
  keep="是（但降为字段）",
  reason="5/20。问题在于 codebook 自身把它定义为取值型（足够/不足/冲突/未报告），本质是字段而非机制；与 cue_to_confirmation 并列会重复计数。建议保留为每条记录的一个评分字段。"),
 dict(concept="action_chain_break",
  distinct_from_v2="与 v2“限制模拟”“V处境困难”高度重叠；唯一增量是必须写明断点位置，而非笼统记为困难。",
  design_implication="断点位置直接对应 VR 的失效反馈类型：感知断点→提示通道；通行断点→碰撞与路径重算；体力断点→运动参数；求助断点→NPC 响应延迟。",
  keep="是（必须分型）",
  reason="19/20 近乎全命中，作为单一标签几乎没有区分力（任何火灾都有某种中断）。实际有信息量的是 action_breakpoint 字段里的位置分型：通行 14、体力/感官 7、救援响应 9、感知 6、决定 5、操作 5、结果等待 3、求助 2、解释 2。建议只保留分型后的子概念。"),
 dict(concept="dynamic_action_space",
  distinct_from_v2="v2“环境模拟”是静态环境还原；本概念要求同一路径的可行性随时间改变，必须有时序对照。",
  design_implication="决定关卡是否做“同一空间的前后对照”：入场时可通行的楼梯，数分钟后成为致命通道，这是 2D 新闻无法给出的信息。",
  keep="是",
  reason="4/20，但四例均为强证据且类型不同（烟经通风口使楼梯失效 R8、走廊充烟 R4、外墙跨楼跳跃传播 R9、楼梯容量拥堵 R15）。与 state_dependent_affordance 需明确分工：前者=时间维度，后者=状态维度。"),
 dict(concept="social_information_mediation",
  distinct_from_v2="v2 无社会信息通道；虽有“社会见证”共情手段，但那是看到他人痛苦，不是他人把危险信息送到你手上。",
  design_implication="决定 VR 里谁说话、说什么、可信度如何：管理方群发消息（R3）、邻居砸门（R3/R6）、社区群组（R9）、消防员逐户敲门（R14）。可设计信息源冲突（官方延时 vs 邻居即时）。",
  keep="是",
  reason="10/20、9 个独立事件，是所有社会类概念中覆盖最广的，且证据均为可引用的直接动作（谁向谁传递）。建议升级为独立维度。"),
 dict(concept="social_action_scaffolding",
  distinct_from_v2="v2“互救”只记有没有人帮忙；本概念要求他人使原本不可行的动作变为可行，需指明被替代的能力。",
  design_implication="直接生成协作交互设计：抬轮椅下 12 层（R10/R11）、连氧气瓶抬人（R1）、逐户敲门引导（R6）、空中平台接下（R8）。可设计“必须依赖他人才能完成”的强制协作机制。",
  keep="是",
  reason="7/20、6 个独立事件，且被替代的能力各不相同（轮椅/供氧/引导/机械平台），区分度好。"),
 dict(concept="ambiguous_early_cue",
  distinct_from_v2="v2 的“多模态感知剥夺”是感官被削弱；本概念是感官仍在工作但信号含义不明确，二者不等价。",
  design_implication="支撑 VR 开场设计：不放大火灾，先给一个说不清的信号（甜味、远处火光、走廊骚动），让体验者自己决定要不要反应。",
  keep="是",
  reason="4/20，且全部集中在气味与远处火光，气味类仅 3 条。频次偏低，但概念边界清楚、不可被其它标签替代，建议保留为候选并扩充语料验证。"),
 dict(concept="state_dependent_affordance",
  distinct_from_v2="v2“限制模拟”只列固定约束（门打不开、逃生门上锁）；本概念要求同一空间因火势、烟、门状态或救援状态改变可行性。",
  design_implication="决定同一场景的可通行性是否具备状态机：门受热变形（R1）、门被消防破坏（R17）、门需用力手动推开（R19）、浴室可藏却不可被找到（R13）。",
  keep="是（但需限缩）",
  reason="16/20，过宽。若不加限缩，会与 action_chain_break 一起吞掉全部记录。建议限定为“同一构件在不同时刻/不同状态下可行性不同”，并把“预置缺陷”（R18、R19）单列为静态子型。"),
 dict(concept="multimodal_substitution",
  distinct_from_v2="v2 的感知剥夺只做减法（削弱感官）；本概念做加法（通道失效后由另一通道或他人补位），是相反方向。",
  design_implication="决定 VR 的无障碍兜底与信息冗余设计：警报失效时是否保留手机群组、邻里喊话、窗外火星这三条替代通道。",
  keep="是",
  reason="5/20、4 个独立事件。R9 是最完整的实例（警铃未响→手机群组→人传人→窗外火星）。需注意 R6 是反例：信息完全未到达且无任何替代通道，不能计入本概念，应另设“信息未到达”。"),
 dict(concept="door_as_information_boundary",
  distinct_from_v2="全新。v2 把门只当通行构件（开门/破门/门打不开）；未承认门同时是室内判断外部状态的唯一信息通道。",
  design_implication="这是“信息到行动”最直接的缺口：VR 里门应同时承担三种功能——信息窗口（猫眼/门缝/开门瞬间）、通行边界、状态可被用户体验动作改变。开门这一动作必须被设计成有后果的决策点。",
  keep="是（优先升级）",
  reason="7/20。猫眼判断“楼梯间全是烟”后改为留守（R5）、门缝渗烟定位起火点（R6）、开门致火势加剧（R7）、开门见火墙（R1）、开门见走廊烟（R14/R17）、门后状态未知（R3）、门无法推开（R19）。跨 7 个独立事件，且全部是可直接实现为交互的构件级证据。"),
 dict(concept="shelter_in_place_decision",
  distinct_from_v2="全新。v2 的“移动方式”只有走/爬/扶梯/跳楼，默认所有人都在往外跑；没有“基于信息判断后决定不走”这一支。",
  design_implication="VR 必须提供“留守”作为合法选项并给出后果反馈：关门堵缝（R5）、退入阳台等救援（R8）、退入浴室（R13）、低层留守（R11）。否则会把真实策略简化为单向逃生。",
  keep="是（优先升级）",
  reason="4/20、4 个独立事件，且四种留守形态各不相同（封门/阳台避难/浴室隐藏/分层留守）。这是当前 v2 叙事控制维度完全缺失的一类决策。"),
 dict(concept="post_event_information_gap",
  distinct_from_v2="全新。v2 的“后果呈现”只展示伤亡与废墟，不处理事件进行中与事后的信息真空。",
  design_implication="支撑另一类 VR 场景：不是逃生体验，而是等待信息的人（家属刷新手机、辨认遗体、不知能否返家）。可作为多视角叙事的一支，与逃生视角并置。",
  keep="是",
  reason="4/20、3 个独立事件（庇护中心攥手机刷新 R9、“他们什么都不告诉任何人”R10、只有沉默 R12、返家未测试 R17）。是唯一能覆盖非在场者视角的机制。"),
 dict(concept="prior_warning_unheeded",
  distinct_from_v2="全新，且不在单条新闻的事件层：v2 全部维度都在描述火灾当次，无法表达“危险早已被指出却无人行动”。",
  design_implication="决定 VR 是否加入“事前”层：投诉记录、清理通知、居民论坛预警。这直接对应系统性忽视的论证，而不只是个体悲情。",
  keep="是（需明确层级）",
  reason="3/20（居民一年多投诉与论坛预警 R12、三年内同栋再发火灾 R17、2018 至 2025 清理通知无效 R18）。属制度/时间跨度层，超出“一次事件的信息—行动链”，建议单列一级而非并入事件层。"),
 dict(concept="reporting_friction",
  distinct_from_v2="全新。v2 无“求助通道本身失效”这一环，限制模拟只做物理约束。",
  design_implication="可设计“求助无回应”的交互：报告被转接、被降级为非紧急、跨机构推诿。这是把制度摩擦转化为可体验反馈的直接手段。",
  keep="候选",
  reason="2/20（转接未完成即爆炸 R15、难以说服接线员且跨机构推诿 R19）。概念清楚但证据仅 2 条，其中 R19 的火灾情境为假设句。建议保留待扩充。"),
 dict(concept="instruction_reversal",
  distinct_from_v2="全新。v2 无权威指令维度；信息冲突在 v2 里没有位置。",
  design_implication="VR 可设计指令冲突：先被告知不必疏散，十分钟后要求全员撤离。这是 2D 叙述难以传达、而 VR 可以通过时间压力直接制造的高张力节点。",
  keep="候选",
  reason="仅 1 个独立事件（R10 与 R11 为同一事件的两篇报道）。证据质量高（原话可引），但单事件不足以支撑升级，需扩充语料。"),
 dict(concept="action_willingness_gate",
  distinct_from_v2="全新。v2 把行动失败归因于身体或环境（身体限制 vs 环境障碍），没有“能做但不愿/不敢做”这一支。",
  design_implication="决定 VR 是否允许体验者拒绝行动，并让拒绝产生后果；同时决定NPC是否具备说服能力（R13 中消防需多次劝说才开门）。",
  keep="候选",
  reason="仅 1/20（新孟买“许多人害怕走出去，我们不得不说服他们开门”；21 岁男性反锁浴室经多次劝说获救）。这是“信息已到达但行动未启动”的唯一实例，概念价值高但证据单薄。"),
]

path = os.path.join(D, "codebook_review.csv")
with open(path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["concept", "frequency_20", "record_ids", "distinct_from_v2",
                "design_implication", "keep_as_candidate", "reason"])
    for row in ROWS:
        ids = cnt.get(row["concept"], [])
        w.writerow([row["concept"], len(ids), ";".join(ids),
                    row["distinct_from_v2"], row["design_implication"],
                    row["keep"], row["reason"]])

print("rows:", len(ROWS))
print("concept not found in coding:", [r["concept"] for r in ROWS if r["concept"] not in cnt])
print("coded but not reviewed:", [k for k in cnt if k not in [r["concept"] for r in ROWS]])
print("written:", path)
