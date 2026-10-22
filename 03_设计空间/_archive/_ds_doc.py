# -*- coding: utf-8 -*-
import json, html
from collections import Counter

d = json.load(open('工作流/_verify.json', encoding='utf-8'))
fields = d['data']['fields']; rids = d['data']['record_id_list']; recs = d['data']['data']
def rec_to_dict(r): return {fields[i]: r[i] for i in range(len(fields))}
def g(rec, name):
    v = rec.get(name)
    if isinstance(v, list): return '、'.join(v) if v else ''
    return (v or '').strip()
def esc(s): return html.escape(str(s), quote=True)

# distributions
def dist(field):
    c = Counter()
    for r in recs:
        rec = rec_to_dict(r)
        v = rec.get(field)
        if isinstance(v, list):
            for x in v: c[x]+=1
        elif v: c[v]+=1
    return c

bld = dist('建筑类型'); cas = dist('伤亡等级'); reg = dist('地区')
body = dist('身体主体'); conf = dist('核心冲突')
six_c = Counter()
for r in recs:
    s = g(rec_to_dict(r),'六角色对接')
    if s: six_c[s]+=1

# conflict -> design implication
conf2impl = {
 '身体限制vs环境障碍':'身体限制模拟（轮椅/拄拐/爬楼/体力）',
 '信息缺失/警报延迟':'感知剥夺 + 替代告警通道（字幕/振动/闪烁）',
 '自救vs互救':'道德选择机制（救谁/先救谁）',
 '逃生vs被困':'时间压力 + 路径选择张力',
 '时间压力':'火势蔓延倒计时可视化',
 '建筑/设施缺陷':'环境叙事 + 事后反思',
}
def impl(rec):
    c = g(rec,'核心冲突')
    base = conf2impl.get(c, '作为共情叙事素材')
    em = g(rec,'交互_共情机制')
    return base + (f'；共情机制：{em}' if em else '')

# group notes
groups = {}
gorder = ['威廉 视障','阿May 听障','罗姐 轮椅','阿福 拄拐','陈伯 老年','King仔 儿童']
for k,r in enumerate(recs):
    rec = rec_to_dict(r)
    six = g(rec,'六角色对接')
    key = six if six else '—（无特定弱势群体 / 普通成年人视角）'
    groups.setdefault(key, []).append((rids[k], rec))

def note_li(rid, rec):
    code=g(rec,'编号'); title=g(rec,'标题')[:70]
    nar='｜'.join(filter(None,[g(rec,'叙事视角'),g(rec,'时间结构'),g(rec,'核心冲突'),g(rec,'情感弧线')]))
    inter='｜'.join(filter(None,[g(rec,'交互_身体化角色'),g(rec,'交互_移动方式'),g(rec,'交互_交互动词'),g(rec,'交互_共情机制')]))
    vr=g(rec,'VR场景对应角色')
    im=impl(rec)
    return (f"<li><b>【{esc(code)}】{esc(title)}</b><br/>"
            f"叙事：{esc(nar)}<br/>"
            f"交互：{esc(inter)}<br/>"
            f"VR映射：{esc(vr)}<br/>"
            f"设计启示：{esc(im)}</li>")

# build body
B = []
B.append('<title>Design Space · VR 高层火灾共情系统新闻语料</title>')

B.append('<h1>一、做 Design Space 与打标的目的是什么</h1>')
B.append('<p>我们手上有 125 条真实的高层 / 集合住宅火灾新闻。它们杂乱、非结构化，每篇讲的故事各不相同。'
         'Design Space（设计空间）＋ 打标（coding）的目的，是把这 125 条"现实碎片"翻译成一套"可用于设计 VR 共情系统"的结构化语言。具体三层目的：</p>')
B.append('<ol>'
 '<li><b>扎根（Grounding）</b>：让 VR 场景不是拍脑袋想的，而是来自真实火灾中弱势群体真实遭遇的证据。每一条标签都能回溯到正文里的某一句话（I1 / I2 证据句）。</li>'
 '<li><b>找规律（Pattern mining）</b>：在 125 条上做统计，回答"哪些弱势群体出现最多？哪些空间 / 感官 / 冲突最高频？"——这些分布直接变成论文的<b>设计要求（design requirements）</b>与贡献点。</li>'
 '<li><b>可追溯的设计映射（Traceable mapping）</b>：叙事维度 → 交互维度的映射规则（如"信息缺失 / 警报延迟"→"感知剥夺 + 字幕 / 振动提示"），把"新闻里发生了什么"直接变成"VR 里要模拟什么"。</li>'
 '</ol>')
B.append('<p>打标不是给每篇文章贴个漂亮标签就结束；<b>标签是手段，上面三层才是目的</b>。最终交付物是论文方法章里的"设计要求 + 典型案例"，而不是这张表本身。</p>')

B.append('<h1>二、为什么当前打标"看起来不清晰"，以及正确读法</h1>')
B.append('<p>表里标签有两类来源，容易混：</p>')
B.append('<ul>'
 '<li><b>结构化 select 字段</b>（叙事视角 / 核心冲突 / 交互_共情机制 …）：是我用规则从 SAVTBC 标签＋正文<b>自动推导的第一稿（AI 初稿）</b>，覆盖全但粗，且是单选 / 多选的有限枚举，丢掉了原文的细微差别。作用是"快速看宏观分布"，不是金标准。</li>'
 '<li><b>文字锚定字段</b>（I1 / I2 证据句、VR场景对应角色、设计空间备注）：给每条标签"锚定"回原文的句子 / 短句，用来核查标签对不对。</li>'
 '</ul>')
B.append('<p>"打标不清晰"是<b>预期内</b>的：第一稿本来就该被人工逐条复核、修正、合并。表里"AI规则初稿·待人工复核"的备注就是提示这一点。'
         '正确读法是：先用 select 字段看宏观分布，再用 I1 / I2 证据句抽查具体某条是否靠谱，最后在论文里把"分布 + 典型案例"写成设计要求。</p>')

B.append('<h1>三、设计空间框架（两套维度 × 八字段）</h1>')
B.append('<p><b>维度一 · VR 新闻叙事（Narrative）</b>：叙事视角、时间结构、空间层级、身体主体、感官主导、核心冲突、情感弧线、叙事颗粒度。</p>')
B.append('<p><b>维度二 · 空间交互设计（Interaction）</b>：交互_身体化角色、交互_移动方式、交互_交互动词、交互_视角转换、交互_共情机制、交互_沉浸反馈、交互_场景控制、交互_社交共在。</p>')
B.append('<p>映射规则（核心）：叙事视角→身体化角色 / 视角转换；空间层级→移动方式 / 交互动词；身体主体→共情机制；核心冲突→共情机制 / 场景控制；情感弧线→场景控制 / 社交共在。完整取值表见飞书 Base 字段与编码方案 v0.1。</p>')

B.append('<h1>四、125 条语料的分布发现（支撑论文论点）</h1>')
B.append('<p><b>建筑类型</b>：'+ '，'.join(f"{k} {v}" for k,v in bld.most_common()) +
         '。→ 近半数（59 条）为高层住宅，直接支撑"高层火灾"的选题聚焦。</p>')
B.append('<p><b>伤亡等级</b>：'+ '，'.join(f"{k} {v}" for k,v in cas.most_common()) +
         '。→ 死亡与群死群伤合计 53 条，说明语料天然携带强共情张力。</p>')
B.append('<p><b>地区</b>：'+ '，'.join(f"{k} {v}" for k,v in reg.most_common()) +
         '。→ 北美主导，但含 19 条中国香港案例（宏福苑等），利于跨文化对比。</p>')
B.append('<p><b>六角色对接（弱势群体覆盖）</b>：'+ '，'.join(f"{k} {v}" for k,v in six_c.most_common()) +
         '；另有 33 条无特定弱势群体（普通成年人 / 救援者视角）。→ 老年、儿童覆盖充足；'
         '轮椅（1）、拄拐（3）样本偏少，是已知素材缺口，论文中需显式说明并建议后续补充。</p>')
B.append('<p><b>核心冲突</b>：'+ '，'.join(f"{k} {v}" for k,v in conf.most_common()) +
         '。→ "身体限制 vs 环境障碍"与"信息缺失 / 警报延迟"高频，恰好对应六角色的身体限制与感知剥夺设计主轴。</p>')

B.append('<h1>五、逐篇文字标注（按六角色分组）</h1>')
B.append('<p>以下为每条新闻的"文字"层标注：叙事要点｜交互要点｜VR 映射｜设计启示。编号对应飞书 Base「最终保留」表。</p>')
for key in gorder + ['—（无特定弱势群体 / 普通成年人视角）']:
    if key not in groups: continue
    B.append(f'<h2>{esc(key)}（{len(groups[key])} 条）</h2>')
    B.append('<ul>')
    for rid, rec in groups[key]:
        B.append(note_li(rid, rec))
    B.append('</ul>')

xml = '\n'.join(B)
open('工作流/_ds_doc.xml','w',encoding='utf-8').write(xml)
print('XML bytes:', len(xml))
print('sections:', xml.count('<h1>'), 'h2:', xml.count('<h2>'), 'li:', xml.count('<li>'))
