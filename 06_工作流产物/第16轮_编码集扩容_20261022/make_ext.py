# -*- coding: utf-8 -*-
"""把人工确认过的外部候选写成 外部新增.json，供 build_set 装配。

只收正文 ≥800 字、且人工看过证据句确认命中的条目。
"""
import os, sys, json, csv, re
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

# (编号, 标题关键词, 目标轴, 备注)
PICK = [
    ('X01', "blind man’s dog helped him safely get down", 'F5', '9/11 北塔 78 层，视障者由导盲犬带出'),
    ('X02', "Bukit Panjang fire; SCDF has to forcibly ente", 'F5/F8', '新加坡 12 层组屋，视障老人被消防员带出、独居老人死亡'),
    ('X02', "77-year-old woman dies after fire in Bukit Panjang", 'F5/F8', '同一场火的第二篇，独居+行动不便'),
    ('X03', "Edmonton arson fire survivor reeling after neighbour", 'D4', '翻阳台到云梯'),
    ('X04', "Latin America’s Deadliest High-Rise Fire", 'D4', '波哥大 Avianca 高层，阳台到阳台下移'),
    ('X05', "Stretched Blanket to Save a Four-Year-Old", 'D4', '四岁童爬到隔壁空置户阳台'),
    ('X06', "RCMP officers save lives in daring fire response", 'D4', '骑警翻阳台进入起火户'),
    ('X07', "15岁女孩一通电话救了一家人", 'E3', '15 楼，119 远程指导固守'),
    ('X08', "接警员远程指导为生命护航", 'E3', '常德津市，接警员远程指导'),
    ('X09', "Hundreds displaced after fire in Center City Philadelphia high-rise", 'E5', '一年五六次误报，警报被日常化'),
    ('X10', "Man killed in NYC apartment fire was a hoarder", 'F8', '独居+囤积可燃物'),
    ('X11', "Three killed in Bronx building fires in final three days", 'F8', '独居老人死于公寓火灾'),
    ('X12', "Woman, 86, dies in Queens NYCHA apartment fire", 'F8', '独居、无子女、囤积'),
    ('X13', "Oak Park explosion, fire in residential building", 'F8', '独居'),
    ('X14', "Fire kills one, leaves more than 20 displaced at Denton", 'F8', '独居退伍军人'),
    ('X16', "Elderly Mumbai couple climbed down water pipes", 'Q', '孟买老年夫妇顺水管下爬'),
    ('X17', "Sharjah fire: Five dead in Al Nahda high-rise", 'Q', '沙迦高层，逃生失败'),
    ('X18', "Police officer rescues residents from fire at Levittown", 'Q', '警员救人'),
    ('X19', "江西一楼房起火，45人待在家中均获救", 'Q', '同一栋楼两种选择的对照'),
    ('X20', "No one to face justice after fire gutted Warrington", 'Q', '英国排屋，过程细节 7 类'),
    ('Y01', "母女困窗外堕楼", 'Q', '江苏，母女困窗外、女童坠亡，C6/D5'),
    ('Y02', "Fire in Australia’s tallest building", 'Q', '澳洲最高住宅楼，垂直疏散'),
    ('Y03', "15 injured in Des Plaines explosion", 'Q', '公寓爆炸，多人受伤'),
    ('Y04', "2-alarm apartment fire in Fremont", 'Q', '弗里蒙特二级火警'),
    ('Y04', "2 women who died from injuries in fatal Fremont", 'Q', '同一场火第二篇'),
    ('Y05', "Early morning fire levels Arkadelphia apartment", 'Q', '整栋公寓烧毁'),
    ('Y06', "Dramatic Michigan apartment fire rescue seen on helmet cam", 'Q', '随身摄像头记录的救援'),
    ('Y07', "4 killed, including child, in New York fire that forced people to jump", 'Q', '被迫跳窗'),
]

cand = list(csv.DictReader(open(os.path.join(HERE, '精准补搜_候选.csv'), encoding='utf-8-sig')))
if os.path.exists(os.path.join(HERE, '精准补搜_候选2.csv')):
    cand += list(csv.DictReader(open(os.path.join(HERE, '精准补搜_候选2.csv'), encoding='utf-8-sig')))
body = json.load(open(os.path.join(HERE, '_work', '补搜正文.json'), encoding='utf-8'))
out, miss = [], []
for xid, kw, tag, note in PICK:
    hit = [c for c in cand if kw in c['标题']]
    if not hit:
        miss.append((xid, kw)); continue
    c = hit[0]
    b = body.get(c['URL'], '')
    if len(b) < 780:
        miss.append((xid, 'body ' + str(len(b)))); continue
    out.append(dict(id=xid, 标题=c['标题'], 正文=b[:4000], URL=c['URL'], 目标=tag,
                    过程类数=int(c['过程类数']), 命中=c['命中'], 备注=note))
json.dump(out, open(os.path.join(HERE, '_work', '外部新增.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('写入', len(out), '条；缺', miss)
for o in out:
    print(' ', o['id'], o['目标'], len(o['正文']), o['标题'][:60])
