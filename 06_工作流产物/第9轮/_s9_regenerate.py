# -*- coding: utf-8 -*-
"""重新生成确认表：正文用路由表全文(前2500字)，纯UTF-8输出"""
import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取路由表（火灾池，含完整正文前2500字）
rt = pd.read_csv('_全量_路由表_K_最终.csv', encoding='utf-8-sig', dtype={'gid': str})
rt['gid'] = rt['gid'].str.strip()
print('路由表行数:', len(rt))

# 读取已判金标准
gs = pd.read_csv('_merged_user_labels.csv', encoding='utf-8-sig', dtype={'gid': str})
gs_ids = set(gs['gid'].str.strip())

# 未判池 = 路由表 - 金标准
unjudged = rt[~rt['gid'].isin(gs_ids)].copy()
print('未判池:', len(unjudged))

# 读取第9轮结果
res = pd.read_csv('_第9轮_grok语义.csv', encoding='utf-8-sig', dtype={'gid': str})
res['gid'] = res['gid'].str.strip()
y_gids = set(res[res['判定']=='Y']['gid'])
print('Y 候选:', len(y_gids))

# 从路由表取 Y 候选的完整正文
y = unjudged[unjudged['gid'].isin(y_gids)].copy()
print('匹配到正文的 Y 候选:', len(y))

# 压缩：去重 + 排除信号 + 长文优先（与之前相同逻辑）
import re
excl = {
    '法律进展': r'arrest|charged|charge|prosecut|lawsuit|indict|起诉|逮捕|被控',
    '纪念哀悼': r'memorial|vigil|mourn|tribute|funeral|哀悼|悼念|纪念仪式',
    '官方声明': r'^officials? |^police |statement|investigation launch|probe',
}
def has_excl(title):
    t = str(title)
    return any(re.search(p, t, re.I) for p in excl.values())
y['排除'] = y['标题'].apply(has_excl)

def core_words(title):
    t = str(title).lower()
    t = re.sub(r'[0-9]+', '', t)
    words = re.findall(r'[a-z]{4,}|[\u4e00-\u9fff]{2,}', t)
    return ' '.join(sorted(set(words))[:8])
y['核心词'] = y['标题'].apply(core_words)
y = y.sort_values('字数', ascending=False)
dedup = y.drop_duplicates(subset='核心词', keep='first')
keep = dedup[~dedup['排除']]
final = keep.head(200).copy()
print('压缩后核心候选:', len(final))

def clip(text, n=2500):
    if pd.isna(text): return ''
    t = str(text).strip()
    return t[:n] + ('...' if len(t) > n else '')

out = pd.DataFrame({
    'gid': final['gid'],
    '标题': final['标题'],
    '正文字数': final['字数'],
    '正文(前2500字)': final['正文(前2500)'].apply(clip),
    '用户判定1/0': '',
})
out.to_csv('_第9轮_待用户确认_v2.csv', index=False, encoding='utf-8-sig')
print('已导出 _第9轮_待用户确认_v2.csv:', len(out), '条')
print('正文平均长度:', int(out['正文(前2500字)'].astype(str).str.len().mean()))
