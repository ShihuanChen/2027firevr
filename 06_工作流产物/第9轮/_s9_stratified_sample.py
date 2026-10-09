# -*- coding: utf-8 -*-
"""S1: 第9轮人工先行 —— 分层抽样生成人工确认表
策略：从 1,155 未判池，按 [366内/366外] × [<800 / 800-1500 / >1500字] 分层抽样
- 366外(被第5步过滤)是误杀风险重点，抽样权重更高
- 随机种子固定保证可复现
"""
import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

SEED = 20260816
N_TOTAL = 120  # 抽样总量

rt = pd.read_csv('_全量_路由表_K_最终.csv', encoding='utf-8-sig')
rt['gid'] = rt['gid'].astype(str).str.strip()
gs = pd.read_csv('_merged_user_labels.csv', encoding='utf-8-sig')
gs_ids = set(gs['gid'].astype(str).str.strip())
ck = pd.read_csv('_归档_旧版/_第2批_checkpoint.csv', encoding='utf-8-sig')
ck_ids = set(ck['gid'].astype(str).str.strip())

unjudged = rt[~rt['gid'].isin(gs_ids)].copy()
unjudged['在366内'] = unjudged['gid'].isin(ck_ids)

def bucket(w):
    if w < 800: return '<800'
    if w < 1500: return '800-1500'
    return '>1500'
unjudged['字数档'] = unjudged['字数'].apply(bucket)

# 层分布
print('=== 未判池分层分布 ===')
layer_counts = unjudged.groupby(['在366内', '字数档']).size()
print(layer_counts.to_string())
print('总数:', len(unjudged))

# 抽样分配：366外(被过滤) 与 366内(通过) 按 7:3，每层内按占比
# 366外 84 条，366内 36 条
outer = unjudged[~unjudged['在366内']]
inner = unjudged[unjudged['在366内']]
N_OUTER, N_INNER = int(N_TOTAL * 0.7), N_TOTAL - int(N_TOTAL * 0.7)

def sample_stratified(df, n):
    """按字数档占比分层抽样"""
    if n >= len(df):
        return df.copy()
    out = []
    for b in ['<800', '800-1500', '>1500']:
        sub = df[df['字数档'] == b]
        if len(sub) == 0:
            continue
        take = max(1, round(n * len(sub) / len(df))) if n > len(df) * 0.5 else round(n * len(sub) / len(df))
        out.append(sub.sample(min(take, len(sub)), random_state=SEED))
    res = pd.concat(out)
    # 补足/裁剪到 n
    if len(res) < n:
        rest = df[~df.index.isin(res.index)]
        res = pd.concat([res, rest.sample(n - len(res), random_state=SEED)])
    return res.sample(n, random_state=SEED)  # 打乱顺序

s_outer = sample_stratified(outer, N_OUTER)
s_inner = sample_stratified(inner, N_INNER)
sample = pd.concat([s_outer, s_inner])

# 输出
def clip(text, n=2500):
    if pd.isna(text): return ''
    t = str(text).strip()
    return t[:n] + ('...' if len(t) > n else '')

out = pd.DataFrame({
    'gid': sample['gid'],
    '在366内': sample['在366内'].map({True: '是(通过第5步)', False: '否(第5步被过滤)'}),
    '标题': sample['标题'],
    '正文字数': sample['字数'],
    '正文(前2500字)': sample['正文(前2500)'].apply(clip),
    '用户判定1/0': '',
})
out.to_csv('_第9轮_人工确认_分层抽样.csv', index=False, encoding='utf-8-sig')

print('\n=== 抽样结果 ===')
print('总数:', len(out))
print(out['在366内'].value_counts().to_string())
print(out.groupby(['在366内', '字数档']).size().to_string() if '字数档' in out else '')
# 字数档统计
samp2 = out.copy()
samp2['字数档'] = sample['字数档'].values
print(samp2.groupby(['在366内', '字数档']).size().to_string())
print('\n已导出 _第9轮_人工确认_分层抽样.csv')
