# -*- coding: utf-8 -*-
"""S2b: 把 503 条 Y 候选压缩到 ~200 条核心候选
策略：去重（同核心词留最长）→ 剔除标题高置信排除信号 → 长文优先
"""
import pandas as pd, sys, re
sys.stdout.reconfigure(encoding='utf-8')

y = pd.read_csv('_第9轮_待用户确认.csv', encoding='utf-8-sig')
print('原始 Y 候选:', len(y))

# 1) 标题级高置信排除（E1-E5，仅标题）
excl = {
    '法律进展': r'arrest|charged|charge|prosecut|lawsuit|indict|起诉|逮捕|被控',
    '纪念哀悼': r'memorial|vigil|mourn|tribute|funeral|哀悼|悼念|纪念仪式',
    '官方声明': r'^officials? |^police |statement|investigation launch|probe',
}
def has_excl(title):
    t = str(title)
    return any(re.search(p, t, re.I) for p in excl.values())
y['排除'] = y['标题'].apply(has_excl)
print('标题含高置信排除信号:', y['排除'].sum())

# 2) 去重：核心词相同的只留正文字数最长一条
def core_words(title):
    t = str(title).lower()
    t = re.sub(r'[0-9]+', '', t)
    words = re.findall(r'[a-z]{4,}|[\u4e00-\u9fff]{2,}', t)
    return ' '.join(sorted(set(words))[:8])
y['核心词'] = y['标题'].apply(core_words)
y = y.sort_values('正文字数', ascending=False)
dedup = y.drop_duplicates(subset='核心词', keep='first')
print('去重后:', len(dedup), '(重复', len(y)-len(dedup), ')')

# 3) 剔除排除信号
keep = dedup[~dedup['排除']]
print('剔除信号后:', len(keep))

# 4) 长文优先，取前 200
final = keep.head(200).copy()
print('最终候选:', len(final))

# 输出
out = final[['gid','标题','正文字数','正文(前2000字)','用户判定1/0']]
out.to_csv('_第9轮_核心候选_200条.csv', index=False, encoding='utf-8-sig')
print('已导出 _第9轮_核心候选_200条.csv')
print('字数范围:', out['正文字数'].min(), '-', out['正文字数'].max())
