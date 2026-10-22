# -*- coding: utf-8 -*-
"""22 类细分细节类型的饱和验证：baseline 122 篇 vs 两轮补搜"""
import json, csv, re, sys, collections, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\Administrator\WorkBuddy\2026-10-22-12-32-14')

P = {
    '嗅觉': r'smell|smelled|smelt|odor|odour|stench|fumes|闻|焦味|刺鼻|呛鼻',
    '热与温度': r'\bheat\b|\bhot\b|scorching|temperature|烫|高温|灼|炙烤',
    '警报失效': r'(no|not|never|fail\w*)\s+\w{0,12}\s*(alarm|siren)|alarm\w*\s+(did not|didn.t|never|fail\w*)|(警报|警铃|报警器|火警)\S{0,8}(没响|未响|不响|失灵|失效|关闭|关掉)|without (an )?alarm',
    '警报有效': r'alarm\w*\s+(sounded|went off|rang|activated)|(警报|警铃|报警器)\S{0,6}(响了|响起|启动)',
    '声音': r'shout|scream|yell|bang|knock|shatter|crackl|喊|尖叫|敲|爆裂|呼救|噼啪',
    '照明失效': r'pitch.black|no (emergency )?light\w*|torch|flashlight|blackout|黑|停电|断电|手电|手机灯',
    '通道被锁': r'(door|gate|exit|stair)\w*\s*\w{0,15}\s*(lock|chain|jam|barred|block)|lock\w*\s+(door|gate|exit)|锁|反锁|铁链|封死|堵住|无法打开',
    '楼梯间充烟': r'(stair\w*|corridor)\s*\w{0,20}\s*(smoke|filled)|smoke\w*\s+(fill|swept|engulf)\w*\s+(the )?(stair|corridor)|楼梯\S{0,8}烟|走廊\S{0,8}(烟|黑)',
    '他人告知': r'neighbo\w*\s+(knock|warn|alert|told)|(friend|relative|colleague)\w*\s*(call|messag|text|told)|knock\w*\s+on|邻居\S{0,10}(敲门|告知|喊)|朋友\S{0,6}(电话|短信)|打电话(告诉|通知)',
    '自行发现': r'(saw|spotted|noticed|smelled)\s+(the\s+)?(flame|smoke|fire)|(看|发现|闻)\S{0,6}(火|烟)|自己\S{0,4}(发现|察觉)',
    '电梯逃生': r'(took|used|use)\s+(the\s+)?(lift|elevator)|by (lift|elevator)|乘(电梯|升降机)|坐电梯|进了电梯',
    '阳台窗口待援': r'(on|to|at)\s+the\s+balcony|from (the )?window|window ledge|阳台|窗口\S{0,6}(求救|挥手|等待)|空调外机',
    '固守待援': r'shelter\w*\s+in\s+place|stay\w*\s+(put|inside|in\s+(the|your)\s+(flat|apartment|room))|(关门|堵住门缝|湿毛巾|固守|等待救援|待在(房间|浴室|屋内))',
    '电话指导': r'(operator|dispatcher|911|999|119)\w*\s*\w{0,20}\s*(told|instruct|guide|advise)|接警员|电话\S{0,6}指导|调度员',
    '官方指令': r'broadcast|loudspeaker|public address|told (residents|occupants) to (leave|evacuate)|广播|通知\S{0,6}撤离|指令',
    '身体搬运': r'(carried|carry|piggyback|stair chair)\w*\s*\w{0,15}\s*(out|down|to safety)?|(抱|背|抬|搀)\S{0,6}(下楼|出去|转移)|楼梯椅',
    '身体受创': r'chok|cough|inhal|unconscious|dizzy|asphyx|呛|窒息|昏迷|熏|头晕|中毒|烧伤',
    '医疗设备依赖': r'(oxygen|medical)\s+(cylinder|tank|equipment)|oxygen\s+(mask|therapy)|氧气(瓶|罐|机)|呼吸机|轮椅|wheelchair',
    '跳楼坠落': r'(jump|jumped|fell|leap)\w*\s*\w{0,12}\s*(from|out|to (his|their) death)|跳(楼|下)|坠落|窗外',
    '消防设施无水': r'(no|not any)\s+water\s+(came|came out)|hose\w*\s+\w{0,12}\s*(dry|no water)|(消防喉|消火栓|消防栓|水枪)\S{0,10}(没水|无水)|dry riser',
    '调查听证': r'hearing|inquiry|inquest|investigat\w+\s+(report|committee)|听证|调查(报告|委员会)|独立委员会',
    '情绪叙事': r'tears|crying|wept|grief|devastat|guilt|terrif|情绪|哭|泪|悲痛|自责|恐惧',
    '政策通稿': r'safety campaign|inspection|rectif|regulat\w+\s+overhaul|专项(检查|整治)|排查|隐患(整治|排查)|通知要求',
    '时间序列': r'\d{1,2}[:.]\d{2}\s*(am|pm)?|\d+\s*(minutes?|mins?|hours?)\s*(later|after)|分钟|随后|之后|几秒|\d{1,2}\s*点\d{0,2}',
    '主体属性': r'elderly|wheelchair|disabled|blind|deaf|pregnan|infant|bedridden|frail|老人|老年|残疾|失能|独居|婴儿|幼儿|孕妇|行动不便',
}
C = {k: re.compile(v, re.I) for k, v in P.items()}

rows = list(csv.DictReader(open('repo/05_编码包/输入包_60事件.csv', encoding='utf-8-sig')))
ev = {e['evg']: e for e in json.load(open('_tmp/events_final.json', encoding='utf-8'))}
B = {int(k): v for k, v in json.load(open('_tmp/bygid.json', encoding='utf-8')).items()}

docs = []
for r in rows:
    for g in ev.get(r['事件组ID'], {}).get('members', []):
        t = (B.get(g, {}).get('正文(前2000)') or '')
        if t.strip():
            docs.append(t)

hit = {k: sum(1 for t in docs if c.search(t)) for k, c in C.items()}
zero = [k for k, v in hit.items() if v == 0]
print('篇数', len(docs), ' 类型数', len(P))
for k, v in sorted(hit.items(), key=lambda x: x[1]):
    print(f'  {k:<10} {v:>4}  {v/len(docs)*100:5.1f}%')
print('\n零命中类型:', zero or '无')

per = collections.defaultdict(set)
for eid_g in docs:
    pass
per = collections.defaultdict(set)
for r in rows:
    for g in ev.get(r['事件组ID'], {}).get('members', []):
        t = (B.get(g, {}).get('正文(前2000)') or '')
        for k, c in C.items():
            if c.search(t):
                per[r['事件组ID']].add(k)
cnt = collections.Counter(len(v) for v in per.values())
print('\n事件级类型数分布', dict(sorted(cnt.items())))
print('平均 %.2f' % (sum(len(v) for v in per.values()) / len(per)))
print('≤3 类的事件', sum(1 for v in per.values() if len(v) <= 3))
print('≥8 类的事件', sum(1 for v in per.values() if len(v) >= 8))
json.dump({'hit': hit, 'per_event_n': {k: len(v) for k, v in per.items()}},
          open('_tmp/sat22.json', 'w'), ensure_ascii=False, indent=1)
