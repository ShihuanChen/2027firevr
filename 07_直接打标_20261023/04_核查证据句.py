# -*- coding: utf-8 -*-
"""证据句核查：三路 JSONL 的 evidence 引句与输入正文做精确子串匹配。

只做两件事，不做判断：
  1. 逐条标出精确命中 / 未命中（区分大小写，不去空白）
  2. 未命中的，再试一次「去空白与标点后」的匹配，区分「只是格式差异」与「原文找不到」

输出：结果/证据句核查.csv、结果/证据句未命中.csv
"""
import csv
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
INP = os.path.join(REPO, '05_编码包', '输入包_编码集v4.csv')
RES = os.path.join(HERE, '结果')


def norm(s):
    """只留字母、数字、汉字；其余（空白、标点、弯引号）全部丢掉。"""
    s = unicodedata.normalize('NFKC', s)
    return ''.join(ch for ch in s if unicodedata.category(ch)[0] in 'LN').lower()


def main():
    body = {r['切片ID']: r['正文'] for r in csv.DictReader(open(INP, encoding='utf-8-sig'))}
    rows = []
    for tag in sorted({f.split('_')[1] for f in os.listdir(RES) if f.startswith('结果_')}):
        p = os.path.join(RES, f'结果_{tag}_v4.2-manual.jsonl')
        if not os.path.exists(p):
            continue
        for line in open(p, encoding='utf-8'):
            o = json.loads(line)
            sid = o['id']
            txt = body.get(sid, '')
            ntxt = norm(txt)
            for ev in o.get('evidence', []) or []:
                q = (ev.get('quote') or '').strip()
                if not q:
                    rows.append([tag, sid, ev.get('field', ''), q, '空引句', '', ''])
                    continue
                exact = q in txt
                loose = norm(q) in ntxt if not exact else True
                rows.append([tag, sid, ev.get('field', ''), q,
                             '精确命中' if exact else ('仅格式差异' if loose else '原文找不到'),
                             '是' if exact else '否', '是' if loose else '否'])

    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, '证据句核查.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['路', '切片ID', '字段', '引句', '判定', '精确命中', '去格式后命中'])
        w.writerows(rows)

    bad = [r for r in rows if r[4] != '精确命中']
    with open(os.path.join(RES, '证据句未命中.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['路', '切片ID', '字段', '引句', '判定', '去格式后命中'])
        w.writerows(bad)

    import collections
    print(f'引句总数 {len(rows)}')
    for tag in sorted({r[0] for r in rows}):
        sub = [r for r in rows if r[0] == tag]
        ex = sum(1 for r in sub if r[4] == '精确命中')
        fm = sum(1 for r in sub if r[4] == '仅格式差异')
        nf = sum(1 for r in sub if r[4] == '原文找不到')
        arts = len({r[1] for r in sub if r[4] != '精确命中'})
        print(f'  {tag}: {len(sub)} 条 | 精确 {ex} | 仅格式差异 {fm} | 原文找不到 {nf} | 涉及 {arts} 篇')
    c = collections.Counter(r[4] for r in bad)
    print('\n未精确命中分类：', dict(c))
    print('未精确命中里「原文找不到」的按路：',
          dict(collections.Counter(r[0] for r in bad if r[4] == '原文找不到')))


if __name__ == '__main__':
    main()
