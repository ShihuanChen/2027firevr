# -*- coding: utf-8 -*-
"""主档 / 附档 分歧归因分析

回答一个问题：多选轴的分歧是集中在「主判定」还是「并存档」上。

口径定义（本脚本唯一实现，文档数字须由本脚本产出）
----------------------------------------------------
对每篇切片的每个轴，取三位编码者各自的有序数组：
  数组首位 = 主档（该轴的主判定）
  数组非首位 = 附档（并存档）

统计单元 = 一次「出现」，即某档在某编码者的该轴数组里出现一次。
  主档出现次数 = 三路非空数组的个数（不是 3×106，因为有空数组）
  附档出现次数 = 三路数组的元素总数 − 主档出现次数

一致性判定（lead_v2 / co_v2 口径）：
  某档在第 t 路出现时，若**另两路在该轴的数组任意位置也含该档**，
  则这次出现算一致；否则算分歧。
  这个口径对主档与附档完全对称——它衡量的是「这个档被认出来没有」，
  而不是「它被放在第几位」，因此主档与附档可直接相减比较。

输出：结果/附档分歧分析.csv（逐档明细）+ 标准输出汇总
"""
import os, sys, json, collections, csv

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.environ.get('RES_DIR') or os.path.join(HERE, '结果')
VER = os.environ.get('PROMPT_VER', 'v4.2-manual')
TAGS = [t for t in (os.environ.get('TAGS') or 'A,B,C').split(',') if t]
AXES = 'abcdef'


def load(tag):
    p = os.path.join(RES, f'结果_{tag}_{VER}.jsonl')
    if not os.path.exists(p):
        p = os.path.join(RES, f'结果_{tag}.jsonl')
    d = {}
    for line in open(p, encoding='utf-8'):
        o = json.loads(line)
        if o.get('ok') and o.get('id'):
            d[o['id']] = o
    return d


def main():
    data = {t: load(t) for t in TAGS}
    ids = sorted(set.intersection(*[set(v.keys()) for v in data.values()]))
    print(f'载入 {({t: len(data[t]) for t in TAGS})}，共有 {len(ids)} 条')

    tot_lead = tot_lead_dis = 0
    tot_co = tot_co_dis = 0
    per = collections.defaultdict(lambda: {
        'lead_n': 0, 'lead_dis': 0, 'co_n': 0, 'co_dis': 0})

    for i in ids:
        for ax in AXES:
            sets = [list(data[t][i].get(ax) or []) for t in TAGS]
            anys = [set(s) for s in sets]
            for ti, s in enumerate(sets):
                if not s:
                    continue
                c = s[0]
                k = sum(1 for a in anys if c in a)
                tot_lead += 1
                per[c]['lead_n'] += 1
                if k < len(TAGS):
                    tot_lead_dis += 1
                    per[c]['lead_dis'] += 1
                for j, c2 in enumerate(s):
                    if j == 0:
                        continue
                    k2 = sum(1 for a in anys if c2 in a)
                    tot_co += 1
                    per[c2]['co_n'] += 1
                    if k2 < len(TAGS):
                        tot_co_dis += 1
                        per[c2]['co_dis'] += 1

    print()
    print('位置 | 出现次数 | 分歧次数 | 分歧率')
    print(f'主档（数组首位） | {tot_lead} | {tot_lead_dis} | '
          f'{100 * tot_lead_dis / tot_lead:.1f}%')
    print(f'附档（非首位） | {tot_co} | {tot_co_dis} | '
          f'{100 * tot_co_dis / tot_co:.1f}%')
    if tot_co:
        print(f'附档分歧率 / 主档分歧率 = '
              f'{(tot_co_dis / tot_co) / (tot_lead_dis / tot_lead):.2f} 倍')

    rows = []
    for c in sorted(per):
        p = per[c]
        rows.append({
            '档': c,
            '主档出现': p['lead_n'], '主档分歧': p['lead_dis'],
            '主档分歧率': round(100 * p['lead_dis'] / p['lead_n'], 1)
            if p['lead_n'] else '',
            '附档出现': p['co_n'], '附档分歧': p['co_dis'],
            '附档分歧率': round(100 * p['co_dis'] / p['co_n'], 1)
            if p['co_n'] else '',
        })
    rows.sort(key=lambda r: (-(r['主档分歧率'] or 0), r['档']))
    out = os.path.join(RES, '附档分歧分析.csv')
    with open(out, 'w', newline='', encoding='utf-8-sig') as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print()
    print('逐档（按主档分歧率降序）:')
    print('档   主档出现/分歧/率        附档出现/分歧/率')
    for r in rows:
        print(f"{r['档']:<4} {r['主档出现']:>3}/{r['主档分歧']:>3}/{r['主档分歧率'] or '-':>5}%"
              f"        {r['附档出现']:>3}/{r['附档分歧']:>3}/{r['附档分歧率'] or '-':>5}%")
    print()
    print('写出', out)


if __name__ == '__main__':
    main()
