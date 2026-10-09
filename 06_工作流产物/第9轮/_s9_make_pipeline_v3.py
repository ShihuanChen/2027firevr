# -*- coding: utf-8 -*-
"""生成数据筛选管线图 V3（5 层漏斗：8,180→6,666→1,443→1,027→109 + 16 篇附注）"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm

for f in ['Microsoft YaHei', 'SimHei', 'Arial']:
    try:
        fm.findfont(f, fallback_to_default=False)
        plt.rcParams['font.sans-serif'] = [f]
        break
    except Exception:
        continue
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(16, 7.2), dpi=150)
ax.set_xlim(0, 16); ax.set_ylim(0, 7.2); ax.axis('off')

# 标题
ax.text(8, 6.75, '图 4-1  数据筛选管线：AI 漏斗 + 人工精判', ha='center', va='center',
        fontsize=20, fontweight='bold', color='#222222')

# 5 层漏斗 + SAVTBC 终点
steps = [
    (0.55, '8,180', '检索命中', 'GDELT + Google/Bing\n三块关键词 AND', '#D8E8F8', '#1F5E9E'),
    (2.95, '6,666', '正文有效', '去死链/空文\n/<300 字', '#D8E8F8', '#1F5E9E'),
    (5.35, '1,443', 'AI 判火灾', 'Grok 读正文语义\n误留率 0%', '#D8E8F8', '#1F5E9E'),
    (7.75, '1,027', '同事件去重', '每事件只留\n场景最丰富一篇', '#D8E8F8', '#1F5E9E'),
    (10.15, '109', '人工精判保留', '在 1,027 候选池上\n按 I1/I2 二元标准裁决', '#E7F2DD', '#3B6D11'),
    (12.85, 'SAVTBC', '六维打标 → VR', 'S93 A70 V95 T88\nB88 C98 → 六角色关卡', '#FBEAD2', '#B56A00'),
]

W, H = 1.95, 3.4
y_bottom = 2.6
for i, (x, num, name, desc, fc, ec) in enumerate(steps):
    box = FancyBboxPatch((x, y_bottom), W, H, boxstyle='round,pad=0.08,rounding_size=0.15',
                         fc=fc, ec=ec, lw=2.2)
    ax.add_patch(box)
    ax.text(x + W/2, y_bottom + H - 0.62, num, ha='center', va='center',
            fontsize=26, fontweight='bold', color=ec)
    ax.text(x + W/2, y_bottom + H - 1.35, name, ha='center', va='center',
            fontsize=15, fontweight='bold', color='#222222')
    ax.text(x + W/2, y_bottom + 0.72, desc, ha='center', va='center',
            fontsize=10.5, color='#333333', linespacing=1.5)
    ax.text(x + 0.10, y_bottom + H - 0.32, f'{i+1}', ha='left', va='top',
            fontsize=10, color='#888888')

for i in range(len(steps) - 1):
    x1 = steps[i][0] + W; x2 = steps[i+1][0]
    arr = FancyArrowPatch((x1 + 0.06, y_bottom + H/2), (x2 - 0.06, y_bottom + H/2),
                          arrowstyle='-|>', mutation_scale=22, lw=2.0, color='#666666')
    ax.add_patch(arr)

# 16 篇补充附注框（独立于漏斗，标注不参与漏斗）
note_x, note_y, note_w, note_h = 10.15, 0.9, 4.65, 1.15
note = FancyBboxPatch((note_x, note_y), note_w, note_h,
                      boxstyle='round,pad=0.08,rounding_size=0.12',
                      fc='#FDF3E7', ec='#B56A00', lw=1.5, linestyle='--')
ax.add_patch(note)
ax.text(note_x + note_w/2, note_y + note_h/2,
        '附注：另有 16 篇人工补充高价值报道\n（幸存者自述/证词，不参与漏斗）',
        ha='center', va='center', fontsize=10.5, color='#B56A00', linespacing=1.5)

# 底部色带图例
legend = [
    (0.55, '#D8E8F8', 'AI 自动处理（干粗活：召回与压缩）'),
    (6.40, '#E7F2DD', '人工裁决（定标准、做保留判断）'),
    (11.30, '#FBEAD2', '最终结果（进 VR 场景重建）'),
]
for x, color, label in legend:
    ax.add_patch(plt.Rectangle((x, 0.25), 0.75, 0.5, fc=color, ec='#999999', lw=1))
    ax.text(x + 0.95, 0.5, label, ha='left', va='center', fontsize=11.5, color='#222222')

plt.tight_layout()
out = 'D:/BaiduSyncdisk/chi2027/朱倩/工作流/_管线图_5层漏斗_V3.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
print('saved:', out)