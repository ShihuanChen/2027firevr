# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
P='_work/结果_模型A.jsonl'
rows=[json.loads(l) for l in io.open(P,encoding='utf-8') if l.strip()]
D={r['id']:r for r in rows}
def add_ev(r,f,q):
    if not any(e['field']==f and e['quote']==q for e in r['evidence']):
        r['evidence'].append({'field':f,'quote':q})

# E0140: 火情信息未经他人/社媒到达（本人开门确认），d3 = 无
r=D['E0140']; r['d3']='无'
add_ev(r,'d3','I opened up my door and was greeted with thick black smoke')

# E0074: c 轴补第二条证据（走廊起火充满画面）
r=D['E0074']
add_ev(r,'c','a red plume of fire erupts and fills the screen')

io.open(P,'w',encoding='utf-8').write('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n')
print('patch3 done')
