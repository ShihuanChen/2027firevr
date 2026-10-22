# -*- coding: utf-8 -*-
"""合并 8 批标注，做自洽清洗与 34 档覆盖统计。"""
import os, sys, json, glob
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

recs = []
for p in sorted(glob.glob(os.path.join(HERE, '_labeled', 'batch*.jsonl'))):
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if line:
            recs.append(json.loads(line))

# 清洗：off_axis=有 但六轴非空 -> 说明给出了判定，改判无
fixed = 0
for r in recs:
    ax = [k for k in 'abcdef' if r.get(k)]
    if r['off_axis'] == '有' and ax:
        r['off_axis'] = '无'
        r['note'] = r.get('note', '') + '（原判off_axis有，因给出轴判定改判无）'
        fixed += 1

print('标注条数', len(recs), '自洽修正', fixed)
print('off_axis 有', sum(1 for r in recs if r['off_axis'] == '有'),
      f"({sum(1 for r in recs if r['off_axis']=='有')/len(recs)*100:.1f}%)")

ALL = {'a': ['A1', 'A2', 'A3', 'A4', 'A5'],
       'b': ['B1', 'B2', 'B3', 'B4', 'B5'],
       'c': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
       'd': ['D1', 'D2', 'D3', 'D4', 'D5'],
       'e': ['E1', 'E2', 'E3', 'E4', 'E5'],
       'f': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8']}
cnt = Counter()
inst = defaultdict(list)
for r in recs:
    for k in 'abcdef':
        for v in r.get(k, []):
            cnt[v] += 1
            inst[v].append(r['切片ID'])

print()
print(f"{'档':<4}{'实例':>4}   档位名 / 判定")
NAME = {}
# 从设计空间文档抓档名
import re
ds = open(os.path.join(os.path.dirname(os.path.dirname(HERE)), '00_核心交付', '01_设计空间_v3_六轴34档.md'), encoding='utf-8').read()
for m in re.finditer(r'^\| ([A-F]\d) \| ([^|]+) \|', ds, re.M):
    NAME[m.group(1)] = m.group(2).strip()

empty, single, ok = [], [], []
for ax, vals in ALL.items():
    for v in vals:
        n = cnt[v]
        tag = '空档' if n == 0 else ('单点' if n <= 2 else '充足')
        (empty if n == 0 else single if n <= 2 else ok).append(v)
        print(f'{v:<4}{n:>4}   {tag}  {NAME.get(v,"")[:18]}  {"、".join(inst[v][:4])}')

print()
print('充足(>=3)', len(ok), ok)
print('单点(1-2)', len(single), single)
print('空档(0)', len(empty), empty)

json.dump(recs, open(os.path.join(HERE, '参考标注_96.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
summary = dict(条数=len(recs), off_axis=sum(1 for r in recs if r['off_axis'] == '有'),
               档频次=dict(cnt), 充足=ok, 单点=single, 空档=empty)
json.dump(summary, open(os.path.join(HERE, '覆盖统计.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n写入 参考标注_96.json / 覆盖统计.json')
