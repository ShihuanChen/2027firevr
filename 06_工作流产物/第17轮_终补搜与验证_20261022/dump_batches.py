# -*- coding: utf-8 -*-
"""把 96 条切片切成 8 批，每批 12 条，正文截 900 字，供逐批阅读标注。"""
import os, sys, csv
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(os.path.dirname(os.path.dirname(HERE)), '05_编码包')
OUT = os.path.join(HERE, '_batches')
os.makedirs(OUT, exist_ok=True)

rows = list(csv.DictReader(open(os.path.join(PKG, '输入包_编码集v4.csv'), encoding='utf-8-sig')))
B = 12
n = 0
for i in range(0, len(rows), B):
    n += 1
    chunk = rows[i:i + B]
    lines = []
    for r in chunk:
        body = r['正文'][:900].replace('\n', ' ')
        lines.append(f"### {r['切片ID']} | {r['标题'][:70]}\n{body}\n")
    p = os.path.join(OUT, f'batch{n:02d}.txt')
    open(p, 'w', encoding='utf-8').write('\n'.join(lines))
    print(p, len(chunk))
