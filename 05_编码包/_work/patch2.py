# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
P='_work/结果_模型A.jsonl'
rows=[json.loads(l) for l in io.open(P,encoding='utf-8') if l.strip()]
D={r['id']:r for r in rows}
def add_ev(r,f,q):
    if not any(e['field']==f and e['quote']==q for e in r['evidence']):
        r['evidence'].append({'field':f,'quote':q})
def drop_ev(r,f,sub):
    r['evidence']=[e for e in r['evidence'] if not (e['field']==f and sub in e['quote'])]

# ---- E0242：C2 无证据支撑，撤；d1 有（醒来->下楼->无人伤亡）；d5 用轮椅句 ----
r=D['E0242']
r['c']=['C3']
drop_ev(r,'c','We had to come down 12 flights of stairs')
r['d1']='有'
add_ev(r,'d1','we all were asleep, and then there was a big explosion')
drop_ev(r,'d5','My neighbor is the one who helped me')
add_ev(r,'d5','he’s in a wheelchair, and I had to struggle down the stairs with my three kids')

# ---- E0140：d1 判无（呈现逃生但无线索解释链），配证据 ----
r=D['E0140']
r['d1']='无'
add_ev(r,'d1','I opened up my door and was greeted with thick black smoke')

# ---- E0164：b 补 B1（烟渗入门下=自主感官确认） ----
r=D['E0164']
r['b']=['B4','B1']
add_ev(r,'b','smoke seeped under a door')

io.open(P,'w',encoding='utf-8').write('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n')
print('patch2 done')
