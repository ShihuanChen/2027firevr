# -*- coding: utf-8 -*-
"""把第四轮补搜的 11 条新增事件追加进编码集与输入包（版本 v4.1，文件名不变以保持引用）。"""
import os, sys, json, csv, re
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(os.path.dirname(os.path.dirname(HERE)), '05_编码包')

new = json.load(open(os.path.join(HERE, '_work', '新增11条.json'), encoding='utf-8'))
print('新增', len(new))

ev_p = os.path.join(PKG, '编码集v4_事件.csv')
pk_p = os.path.join(PKG, '输入包_编码集v4.csv')
ev = list(csv.DictReader(open(ev_p, encoding='utf-8-sig')))
pk = list(csv.DictReader(open(pk_p, encoding='utf-8-sig')))
print('原事件', len(ev), '原切片', len(pk))

exist = {re.sub(r'\W+', '', r['标题'].lower())[:40] for r in ev}
add_ev, add_pk = [], []
for r in new:
    key = re.sub(r'\W+', '', r['标题'].lower())[:40]
    if key in exist:
        print('  跳过重复', r['nid'], r['标题'][:50])
        continue
    pc = int(r['过程类数'])
    blob = r['标题'] + r['正文'][:600]
    lv = 'B_高层词无层数' if re.search(r'high-?rise|tower|高层|楼|flats|apartment building', blob, re.I) else 'D_无层数'
    qg = 'A' if pc >= 7 else 'B' if pc >= 5 else 'C' if pc >= 3 else 'D'
    add_ev.append(dict(事件组ID=r['nid'], 标题=r['标题'], 切片数=1, 最佳过程类数=pc,
                       质量分层='主分析' if pc >= 3 else '补充', 命中=r['命中'][:80],
                       层级=lv, 质量等级=qg, 代表gid='', 来源='第17轮补搜',
                       相对上版='新增', 真实事件簇=r['标题'][:24],
                       处置理由=f'第17轮定向补搜命中（目标缺口），过程类{pc}类'))
    add_pk.append(dict(切片ID=f"{r['nid']}-1", 事件组ID=r['nid'], 标题=r['标题'],
                       正文=r['正文'][:2000], 字数=str(len(r['正文'][:2000])),
                       过程类数=str(pc), 命中=r['命中'], 出处='第17轮补搜', URL=r['URL']))

for p, rows, olds in ((ev_p, ev, add_ev), (pk_p, pk, add_pk)):
    fields = list(rows[0].keys())
    with open(p, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows + olds:
            w.writerow({k: r.get(k, '') for k in fields})
    print(os.path.basename(p), '→', len(rows) + len(olds))

print('新增事件', len(add_ev), '新增切片', len(add_pk))
