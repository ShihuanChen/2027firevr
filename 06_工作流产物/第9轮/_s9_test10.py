# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import _s9_grok_review_v2 as m

pool = pd.read_csv('_第9轮_未判池.csv', encoding='utf-8-sig')
pool['gid'] = pool['gid'].astype(str).str.strip()
test = pool.head(10)
print('测试条数:', len(test), flush=True)

results = []
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = [ex.submit(m.process_one, row) for idx, row in test.iterrows()]
    for f in as_completed(futs):
        results.append(f.result())

df = pd.DataFrame(results)
print(df[['gid', '判定', '理由']].to_string())
print()
print('判定分布:', df['判定'].value_counts().to_dict())
