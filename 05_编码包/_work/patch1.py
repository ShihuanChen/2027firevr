# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
P='_work/结果_模型A.jsonl'
rows=[json.loads(l) for l in io.open(P,encoding='utf-8') if l.strip()]
D={r['id']:r for r in rows}

def add_ev(r, field, quote):
    if not any(e['field']==field and e['quote']==quote for e in r['evidence']):
        r['evidence'].append({'field':field,'quote':quote})

def drop_ev(r, field, quote_sub):
    r['evidence']=[e for e in r['evidence'] if not (e['field']==field and quote_sub in e['quote'])]

# ---- E0140: 门开见浓黑烟 = 单通道有效(A2)，非物理屏蔽(A3) ----
r=D['E0140']; r['a']=['A2']
add_ev(r,'a','I opened up my door and was greeted with thick black smoke, it was terrifying.')

# ---- E0023: 主角 Calderon 自身感官确认燃气(B1)；居民侧始终未获正式确认(B5) ----
r=D['E0023']; r['b']=['B1','B5']
add_ev(r,'b','I smelled the gas and heard the hissing sound of gas, so I taped a blanket around the hole and left.')
add_ev(r,'b','when “an explosion occurred” on the top floor around 12:15 a.m.')
r['e']=['E1']
add_ev(r,'e','so I taped a blanket around the hole and left')

# ---- E0074: 同事件同口径；C 轴证据换成"走廊成瓦砾" ----
r=D['E0074']; r['b']=['B1','B5']
add_ev(r,'b','He taped a blanket over the hole and fled after he heard and smelled gas')
add_ev(r,'b','The leaking gas spread to the 17th floor, where it ignited')
r['c']=['C5']
drop_ev(r,'c','severe structural damage')
add_ev(r,'c','the hallway is full of rubble')
r['e']=['E1']
add_ev(r,'e','He taped a blanket over the hole and fled')

# ---- E0075 / E0142: 楼梯仍可走但充满烟 -> C5（非 C6） ----
for rid in ('E0075','E0142'):
    r=D[rid]; r['c']=['C5']
    drop_ev(r,'c','severe structural damage')
    add_ev(r,'c','escaping the heavy smoke')
    # d3 改判无：火情信息由本人听觉获得，非经他人/社媒
    r['d3']='无'
    drop_ev(r,'d3','their neighbors scrambled downstairs')
    add_ev(r,'d3','she "heard a big boom,"')

# ---- E0105: f 补 F3；d3 改判无 ----
r=D['E0105']; r['f']=['F7','F3','F1']
r['d3']='无'
add_ev(r,'d3','The fact that half of the building is gone and you felt it')
add_ev(r,'d1','The fact that half of the building is gone and you felt it')
add_ev(r,'d1','Luckily, I asked somebody, I asked was anybody injured? No injuries occurred.')

# ---- E0164: a 轴第二通道换成"烟从门下渗入"；b 轴 B4 保留 ----
r=D['E0164']
drop_ev(r,'a','People were crying out from balconies')
add_ev(r,'a','smoke seeped under a door')

# ---- E0242: 补 b=B1；c 改 C3+C2；d 去 D3；e 改 E1+E2；d5 证据换成邻居协助 ----
r=D['E0242']; r['b']=['B1']
add_ev(r,'b','we all were asleep, and then there was a big explosion')
r['c']=['C3','C2']
drop_ev(r,'c','dangling with his legs out of the building')
add_ev(r,'c','We had to come down 12 flights of stairs')
r['d']=['D1','D5']
drop_ev(r,'d','Residents of the lower floors stayed in the building during the firefighting efforts')
r['e']=['E1','E2']
add_ev(r,'e','We had to come down 12 flights of stairs')
drop_ev(r,'d5','he’s in a wheelchair')
add_ev(r,'d5','My neighbor is the one who helped me')
add_ev(r,'f','Me and my kids, we all were asleep, and then there was a big explosion')

io.open(P,'w',encoding='utf-8').write('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n')
print('patched', len(rows))
