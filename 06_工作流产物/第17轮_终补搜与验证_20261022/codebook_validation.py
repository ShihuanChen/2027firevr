# -*- coding: utf-8 -*-
"""Codebook 判定线验证：双模型逐字段 Cohen's κ + bootstrap CI + 逐档分歧定位。
口径：每个字段对两个标注者做一次 κ；六轴按"逐档二分"算再平均，避免多选字段无法直接算 κ。
"""
import os, sys, json, csv, random
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(os.path.dirname(os.path.dirname(HERE)), '05_编码包')
WORK = os.path.join(PKG, '_work', '一致性v1')

A = {x['id']: x for x in (json.loads(l) for l in open(os.path.join(WORK, '结果_模型A.jsonl'), encoding='utf-8') if l.strip())}
B = {x['id']: x for x in (json.loads(l) for l in open(os.path.join(WORK, '结果_模型B.jsonl'), encoding='utf-8') if l.strip())}
IDS = sorted(set(A) & set(B))
print('共同切片', len(IDS))

SINGLE = ['p1', 'p2', 'p3', 'p4', 'p5', 'd1', 'd2', 'd3', 'd4', 'd5', 'off_axis', 'confidence']
AXES = ['a', 'b', 'c', 'd', 'e', 'f']


def norm_single(v):
    if isinstance(v, list):
        return v[0] if v else '未报告'
    return v if v not in (None, '') else '未报告'


def cohen(pa, pb):
    n = len(pa)
    if n == 0:
        return None
    po = sum(1 for x, y in zip(pa, pb) if x == y) / n
    ca, cb = Counter(pa), Counter(pb)
    pe = sum(ca[k] / n * cb[k] / n for k in set(ca) | set(cb))
    if pe >= 1:
        return dict(kappa=1.0, po=po, pe=pe, n=n)
    return dict(kappa=(po - pe) / (1 - pe), po=po, pe=pe, n=n)


def boot(pa, pb, k=1000):
    idx = list(range(len(pa)))
    vals = []
    for _ in range(k):
        s = [random.choice(idx) for _ in idx]
        r = cohen([pa[i] for i in s], [pb[i] for i in s])
        if r:
            vals.append(r['kappa'])
    vals.sort()
    return (round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals))], 3)) if vals else (None, None)


def agree_label(k):
    if k is None:
        return ''
    if k >= 0.8:
        return '几乎完全一致'
    if k >= 0.6:
        return '实质一致'
    if k >= 0.4:
        return '中等'
    if k >= 0.2:
        return '弱'
    return '不可用'


report = {'字段级': {}, '逐档': {}, '总体': {}}

print()
print(f"{'字段':<10}{'κ':>7}{'95%CI':>18}{'一致率':>8}   评价")
for f in SINGLE:
    pa = [norm_single(A[i].get(f)) for i in IDS]
    pb = [norm_single(B[i].get(f)) for i in IDS]
    r = cohen(pa, pb)
    if not r:
        continue
    lo, hi = boot(pa, pb)
    report['字段级'][f] = dict(kappa=round(r['kappa'], 3), ci=[lo, hi], po=round(r['po'], 3), n=r['n'],
                             label=agree_label(r['kappa']))
    print(f"{f:<10}{r['kappa']:>7.3f}   [{lo}, {hi}]   {r['po']*100:>5.1f}%   {agree_label(r['kappa'])}")

print()
print('六轴（逐档二分后平均）')
for ax in AXES:
    ks, pos, hits, tot = [], 0, 0, 0
    detail = {}
    vals = set()
    for i in IDS:
        vals |= set(A[i].get(ax) or []) | set(B[i].get(ax) or [])
    for v in sorted(vals):
        pa = [1 if v in (A[i].get(ax) or []) else 0 for i in IDS]
        pb = [1 if v in (B[i].get(ax) or []) else 0 for i in IDS]
        r = cohen(pa, pb)
        if r:
            ks.append(r['kappa'])
            detail[v] = dict(k=round(r['kappa'], 3), po=round(r['po'], 3),
                             pabak=round(2 * r['po'] - 1, 3))
            pos += sum(pa); hits += sum(1 for x, y in zip(pa, pb) if x == y); tot += len(pa)
    m = sum(ks) / len(ks) if ks else 0
    report['逐档'][ax] = detail
    report['字段级'][ax] = dict(kappa=round(m, 3), po=round(hits / tot, 3) if tot else None,
                              n=len(IDS), label=agree_label(m), 档位=detail)
    print(f"{ax}  档均κ={m:>6.3f}  逐档一致率={hits/tot*100:>5.1f}%   {agree_label(m)}")
    print('     ' + '  '.join(f"{k}:k={v['k']}/po={v['po']}/pabak={v['pabak']}" for k, v in detail.items()))

low = [(f, v['kappa']) for f, v in report['字段级'].items() if v['kappa'] < 0.4]
print()
print('κ<0.4 需改线的字段：', low)

# 合并编码本身（作为"读得最透"的上限参照）
# 分歧格数直接从两份原件算，不依赖合并结果表的 disputed 标记
dis = 0; tot = 0
for f in SINGLE:
    for i in IDS:
        tot += 1
        if norm_single(A[i].get(f)) != norm_single(B[i].get(f)):
            dis += 1
for ax in AXES:
    for i in IDS:
        tot += 1
        if set(A[i].get(ax) or []) != set(B[i].get(ax) or []):
            dis += 1
print(f'分歧格 {dis}/{tot} = {dis/tot*100:.1f}%')
report['总体'] = dict(切片数=len(IDS), 分歧格=dis, 总格=tot,
                    off_axis有=sum(1 for i in IDS if norm_single(A[i].get('off_axis')) == '有'))

json.dump(report, open(os.path.join(HERE, 'codebook_验证.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('写入 codebook_验证.json')
