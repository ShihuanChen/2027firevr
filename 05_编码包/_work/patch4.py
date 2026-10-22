# -*- coding: utf-8 -*-
"""patch4: 复核 7 类判定问题后的定向修正"""
import json, io, os

P = os.path.join(os.path.dirname(__file__), '结果_模型A.jsonl')
rows = [json.loads(l) for l in io.open(P, encoding='utf-8')]
D = {r['id']: r for r in rows}

def drop_ev(r, field, quote=None):
    r['evidence'] = [e for e in r['evidence']
                     if not (e['field'] == field and (quote is None or e['quote'] == quote))]

def add_ev(r, field, quote):
    r['evidence'].append({'field': field, 'quote': quote})

def set_ev(r, field, quotes):
    drop_ev(r, field)
    for q in quotes:
        add_ev(r, field, q)

# ---------- E0010 / E0011 / E0017: Bronx 燃气爆炸 ----------
# D5 极端退出（悬于窗外求救）此前漏标
for rid, vac in (('E0010', 'all 148 apartments vacated'),
                 ('E0011', 'all 148 apartments vacated'),
                 ('E0017', 'All 148 apartments were evacuated')):
    r = D[rid]
    r['d'] = ['D1', 'D5']
    set_ev(r, 'd', [vac, 'people were seen leaning out of windows calling for help'])

# E0017 的 d4 证据错位：原用 "trapping some firefighters in an elevator"（属电梯失效，非行动支架）
r = D['E0017']
r['d4'] = '有'
set_ev(r, 'd4', ['firefighters rescued residents in freezing temperatures'])

# ---------- E0073 / E0138: 高层疏散评论（专家稿） ----------
# 楼梯为唯一可靠路线 + 疏散速度远低于预期 -> C2 单一通道且通行能力受限
for rid in ('E0073', 'E0138'):
    r = D[rid]
    r['c'] = ['C2']
    set_ev(r, 'c', ['Stairwells are the only reliable escape route in most buildings.',
                    'Stair descent in real evacuations is far slower than most people expect.'])
    r['d'] = ['D1']
    set_ev(r, 'd', ['more than 900 people have been reportedly evacuated from the Wang Fuk Court'])

# E0138 的 d2：补上"实际火场速度骤降"的序列端点
r = D['E0138']
r['d2'] = '有'
set_ev(r, 'd2', ['Under controlled or drill conditions people move down at around 0.4-0.7 metres per second.',
                  'But in an actual emergency, especially in high-rise fires, this can drop sharply'])

# ---------- E0209: 香港火灾调查（聚苯板封窗） ----------
# 封窗 = A3 物理屏蔽（轴定义卡锚例：泡棉封窗）；C4 工程封闭保留为次
r = D['E0209']
r['a'] = ['A3']
r['c'] = ['C4']
set_ev(r, 'a', ['police found polystyrene boards blocking windows at the renovation site',
                'some windows in an unaffected block had been sealed with foam'])
set_ev(r, 'c', ['police found polystyrene boards blocking windows at the renovation site'])

# ---------- E0064: Thorncliffe Park 火灾调查 ----------
# 火在墙体夹层内隐蔽燃烧 30 分钟无报警/无人通知 -> A3 + A5
r = D['E0064']
r['a'] = ['A3', 'A5']
set_ev(r, 'a', ['the fire burned within concealed spaces between the structures',
                'Toronto Fire Services was not notified of the fire for over 30 minutes'])
r['d2'] = '有'
set_ev(r, 'd2', ['The blaze quickly grew from a two-alarm call into a five-alarm fire and spread to a neighbouring building'])

# ---------- E0082: 迪拜 Al Barsha ----------
# d5 通道替代需显示替代动作本身；a 轴补第二条（唯一有效通道 = 敲门）
r = D['E0082']
set_ev(r, 'a', ['fire alarms failed to sound',
                'knocked on neighbours’ doors to alert them of the danger'])
set_ev(r, 'd5', ['knocked on neighbours’ doors to alert them of the danger'])

# ---------- E0213: 家人敲门救人 -> d3 社会信息中介 ----------
r = D['E0213']
r['d3'] = '有'
set_ev(r, 'd3', ['Yip’s mother had stayed behind to knock on neighbours’ doors, saving the lives of four people'])

# ---------- E0018: 通风排烟恢复可行动空间 ----------
r = D['E0018']
set_ev(r, 'd2', ['The fire is now out and firefighters are using ventilation to clear smoke from the affected areas'])

io.open(P, 'w', encoding='utf-8', newline='\n').write(
    '\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n')
print('patch4 done,', len(rows), 'rows')
