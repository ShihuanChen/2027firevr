# -*- coding: utf-8 -*-
"""S1: 导出第9轮未判池 —— 路由表中未被人工判过的火灾报道"""
import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取路由表（火灾池，去重前 1446）
rt = pd.read_csv('_全量_路由表_K_最终.csv', encoding='utf-8-sig')
rt['gid'] = rt['gid'].astype(str).str.strip()
print('路由表行数:', len(rt))

# 读取金标准（694 已判）
gs = pd.read_csv('_merged_user_labels.csv', encoding='utf-8-sig')
gs_ids = set(gs['gid'].astype(str).str.strip())
print('金标准已判 gid 数:', len(gs_ids))

# 未判池 = 路由表 - 金标准
unjudged = rt[~rt['gid'].isin(gs_ids)].copy()
print('未判池行数:', len(unjudged))

# 取 gid/标题/字数/正文前1200字
def clip(text, n=1200):
    if pd.isna(text):
        return ''
    t = str(text).strip()
    return t[:n] + ('...' if len(t) > n else '')

out = pd.DataFrame({
    'gid': unjudged['gid'],
    '标题': unjudged['标题'],
    '正文字数': unjudged['字数'],
    '正文(前1200字)': unjudged['正文(前2500)'].apply(clip),
})
out.to_csv('_第9轮_未判池.csv', index=False, encoding='utf-8-sig')
print('\n已导出 _第9轮_未判池.csv:', len(out), '条')
print('样例 gid:', out['gid'].head(5).tolist())

# 交叉验证：366 内未判 221 + 366 外未判 934
ck = pd.read_csv('_归档_旧版/_第2批_checkpoint.csv', encoding='utf-8-sig')
ck_ids = set(ck['gid'].astype(str).str.strip())
in366 = len(set(out['gid']) & ck_ids)
print('未判池中在366内:', in366, '| 366外:', len(out) - in366)
