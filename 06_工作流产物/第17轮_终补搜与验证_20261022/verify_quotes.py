# -*- coding: utf-8 -*-
"""证据句可溯源率检查：参考标注的 ev 是否能逐字在输入包正文中找到。
用法：python verify_quotes.py [标注json] [输入包csv]
"""
import json,csv,re,sys,os
sys.stdout.reconfigure(encoding='utf-8')
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
lab=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'参考标注_106.json')
pk=sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,'05_编码包','输入包_编码集v4.csv')
def norm(s): return re.sub(r'[^\w\u4e00-\u9fff]+','',s or '').lower()
ref=json.load(open(lab,encoding='utf-8'))
inp={r['切片ID']:r for r in csv.DictReader(open(pk,encoding='utf-8-sig'))}
hit=part=miss=0; bad=[]
for r in ref:
    sid=r['切片ID']; body=norm(inp.get(sid,{}).get('正文','')); ev=r.get('ev') or ''
    if not ev.strip(): continue
    segs=[s for s in re.split(r'[；;/、。]', ev) if len(s.strip())>=6] or [ev]
    ratio=sum(1 for s in segs if norm(s) and norm(s) in body)/len(segs)
    if ratio==1: hit+=1
    elif ratio>=0.5: part+=1
    else: miss+=1; bad.append((sid,ev[:60]))
tot=hit+part+miss
print(f'证据句 {tot} 条：完全可溯源 {hit}（{hit/tot*100:.1f}%）、半数 {part}、不可溯源 {miss}')
for b in bad: print('  未命中',b[0],b[1])
