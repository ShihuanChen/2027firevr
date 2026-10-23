# -*- coding: utf-8 -*-
"""人工抽检对照：把 A/B/C 三路结果与 00_核心交付/08_人工抽检_参考对照.json 逐轴比对。

κ 回答"重复标注稳不稳"，这里回答"标注对不对"。两者不可互换。

用法：
    cd repo/07_直接打标_20261023
    python 04_人工抽检对照.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
REF = os.path.join(REPO, '00_核心交付', '08_人工抽检_参考对照.json')
RES = os.path.join(HERE, '结果')
VER = 'v4.2-manual'
AXES = ['a', 'b', 'c', 'd', 'e', 'f']
AX_NAME = {'a': 'a 信息可达性', 'b': 'b 确认的社会性', 'c': 'c 可行动集',
           'd': 'd 决策指向', 'e': 'e 能动性来源', 'f': 'f 处境主体'}


def load(tag):
    p = os.path.join(RES, f'结果_{tag}_{VER}.jsonl')
    d = {}
    if not os.path.exists(p):
        return d
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if line:
            o = json.loads(line)
            d[o['id']] = o
    return d


def main():
    ref = {r['切片ID']: r for r in json.load(open(REF, encoding='utf-8'))}
    tags = [t for t in ('A', 'B', 'C') if load(t)]
    data = {t: load(t) for t in tags}

    print('## 逐轴一致率（AI vs 人工参考，12 条）\n')
    print('| 编码者 | 轴 | 可比条数 | 完全一致 | 一致率 | Jaccard |')
    print('|---|---|---|---|---|---|')
    detail = {t: [] for t in tags}
    for t in tags:
        agg = {k: {'n': 0, 'exact': 0, 'jac': 0.0} for k in AXES}
        for sid, rr in ref.items():
            if sid not in data[t]:
                continue
            rec = data[t][sid]
            for k in AXES:
                hu = set(rec.get(k) or [])
                re_ = set(rr.get(k) or [])
                agg[k]['n'] += 1
                eq = hu == re_
                agg[k]['exact'] += int(eq)
                u = hu | re_
                agg[k]['jac'] += (len(hu & re_) / len(u)) if u else 1.0
                if not eq:
                    detail[t].append((sid, k, sorted(hu), sorted(re_)))
        for k in AXES:
            d = agg[k]
            if not d['n']:
                continue
            print(f"| {t} | {AX_NAME[k]} | {d['n']} | {d['exact']} | "
                  f"{d['exact']/d['n']*100:.1f}% | {d['jac']/d['n']:.3f} |")

    # 整条完全一致（六轴全中）
    print('\n## 整条六轴完全一致\n')
    print('| 编码者 | 完全一致条数 | 占可比条数 |')
    print('|---|---|---|')
    for t in tags:
        ids = [s for s in ref if s in data[t]]
        full = 0
        for sid in ids:
            if all(set(data[t][sid].get(k) or []) == set(ref[sid].get(k) or []) for k in AXES):
                full += 1
        print(f"| {t} | {full}/{len(ids)} | {full/len(ids)*100:.1f}% |")

    for t in tags:
        if not detail[t]:
            continue
        print(f'\n## {t} 逐轴分歧\n')
        for sid, k, hu, re_ in detail[t]:
            print(f'- **{sid}** {k}：AI={hu or "无"} 参考={re_ or "无"}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
