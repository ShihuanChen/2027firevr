# -*- coding: utf-8 -*-
"""34 档覆盖粗筛：对 96 条编码集切片，按档位定义写正则，输出每档候选数与证据片段。
用途：定位空档与单点档，供人工逐档核证；不替代正式编码。
"""
import os, sys, re, csv, json
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(os.path.dirname(os.path.dirname(HERE)), '05_编码包')

AX = {
    'A1': (r'(警报|警铃|广播|火警钟).{0,120}(敲门|砸门|邻居|喊|叫)|(敲门|砸门|邻居|喊).{0,120}(警报|警铃|广播|火警钟)'
           r'|alarm.{0,120}(knock|shout|neighbo)|(knock|shout|neighbo).{0,120}alarm'),
    'A2': (r'唯一的?(警报|通道|出口)|只有一(条|个|种)|警报(响|响过).{0,60}(没有|无人|不见)|single (exit|stair|alarm)'),
    'A3': (r'封(窗|板|死)|发泡胶|围挡|无窗|封住|遮挡|看不到(室外|外面)|视线被|covered the windows|boarded'),
    'A4': (r'以为(是|没事|着|谁家)|误以为|以为是|平时(也|经常)|经常(响|有)|误报|没在意|没当回事|当作|'
           r'thought it was|assumed it was|false alarm'),
    'A5': (r'没有(听到|听见|任何)(警报|声音|动静)|警报(没响|未响|不响)|熟睡|睡梦中|毫不知情|毫无察觉|未察觉|'
           r'没人(通知|叫|告诉)|did not hear|never heard|asleep'),
    'B1': (r'开门(查看|一看|看)|开窗(查看|一看)|摸(了)?门(把手)?|亲自(查看|去看)|出去(查看|看)|走出去看|'
           r'opened the (door|window)'),
    'B2': (r'邻居(敲|喊|叫|通知|提醒|告诉)|敲(门|门叫)|踹门|砸门|室友(叫|喊)|家人(叫|喊|通知)|'
           r'保安(通知|喊)|管理员(通知|喊)|neighbo.{0,20}(knock|warn|alert|bang)'),
    'B3': (r'接到.{0,6}(电话|消息)|打电话(告诉|通知)|微信|群里|朋友圈|社交媒体|手机(上|看)|看新闻|电视|'
           r'门铃|监控|短信|called (him|her|them)|phone (call|rang)|social media'),
    'B4': (r'广播|消防(车|队).{0,10}(喊话|广播)|警报(响|声)|警铃|疏散(通知|广播)|楼内广播|'
           r'PA system|announcement|siren|alarm (sounded|went off)'),
    'B5': (r'没有人(通知|来|敲门)|无人(通知|告知)|没收到(任何)?通知|事后才(知道|发现)|'
           r'no one (told|warned|knocked)|never (notified|warned)'),
    'C1': (r'(沿着|顺着|从).{0,6}楼梯(走|下|逃)|安全出口|逃生梯|走楼梯|楼梯(间)?(下去|下楼)|'
           r'emergency stair|stairwell.{0,30}(descend|down|fled)'),
    'C2': (r'唯一的?(出口|楼梯|通道)|只有一(条|个)(楼梯|出口|通道)|狭窄|single (exit|staircase)|narrow stair'),
    'C3': (r'轮椅|行动不便|走不动|无法(行走|下楼)|卧床|抱不动|体力不支|腿脚|瘫痪|mobility|wheelchair'),
    'C4': (r'(门|通道|出口).{0,10}(锁|铁链|焊|封)|锁死|上锁|铁链|杂物(堆|阻)|堆放|堵塞|封堵|'
           r'padlock|chained|locked|blocked (exit|stair)'),
    'C5': (r'烟囱|充满(浓烟|烟)|浓烟(弥漫|滚滚)|能见度|呛|无法呼吸|烟气(弥漫|窜)|smoke-filled|thick smoke'),
    'C6': (r'只能(跳|从窗)|不得不(跳|悬)|无路可逃|所有(出口|通道).{0,10}(封|断)|'
           r'no way out|only (option|way) (was )?to jump'),
    'D1': (r'下楼|往下(走|跑)|向?下(疏散|撤离)|撤到楼下|逃到(楼)?下|descend|went down|fled downstairs'),
    'D2': (r'天台|楼顶|屋顶|避难层|往上(走|跑)|爬上(楼顶|天台)|rooftop|roof of the building'),
    'D3': (r'关(上)?(门|窗)|堵(门缝|住门)|湿毛巾|毛巾(捂|塞)|浴室|卫生间|固守|待援|等待救援|shelter in place|stayed in'),
    'D4': (r'阳台.{0,10}(到|跨|翻)|翻(过|越)(阳台|窗)|爬到隔壁|隔壁(户|单元|阳台)|相邻(阳台|楼)|'
           r'balcony to balcony|climbed (across|over) (to )?(the )?(neighbo|next)'),
    'D5': (r'跳(下|楼|窗)|坠楼|悬(在|于)窗外|挂在窗外|攀爬(外墙|外立面)|jump(ed)? (from|out)|hung from the window'),
    'E1': (r'自己(判断|决定|发现|意识)|主动(决定|离开|下楼)|自行(判断|疏散|撤离)|决定(自己|先)|'
           r'decided to (leave|go|get out)'),
    'E2': (r'(搀|扶|拉|背|抱)(着|起)?.{0,8}(走|下|逃|出)|带(着|领).{0,8}(下楼|逃|疏散|离开)|抱着(孩子|老人)走|'
           r'helped (him|her|them) (out|down|escape)|carried (him|her|them) out'),
    'E3': (r'(119|110|120|999|911).{0,20}(电话|指导|指挥|指引)|接警(员|人)|调度(员|中心)|远程(指导|指引)|'
           r'电话(里|中)(指导|教|让)|dispatcher.{0,30}(told|instruct|guide)'),
    'E4': (r'等待(指令|通知|广播|救援|指示)|等(通知|指令|广播|人来)|被告知(留在|待在|等待)|原地(等待|不动)|'
           r'stay(ed)? put|wait(ed|ing) for (instruction|order|help)'),
    'E5': (r'误报|假(警报|火警)|以为没事|称(没事|安全)|解除(警报|警戒)|被告知(没事|安全)|'
           r'false alarm|told (it was|there was) (nothing|no fire)'),
    'F1': None,
    'F2': (r'老年|老人|阿婆|阿伯|老翁|老太|七旬|八旬|九旬|岁.{0,4}(老人|男|女)|elderly|\b[6-9]\d[- ]year[- ]old'),
    'F3': (r'儿童|孩子|小孩|幼(儿|童)|婴|小童|男童|女童|\d{1,2}岁(的)?(男|女)?(孩|儿|童)|'
           r'\b(child|children|toddler|infant|boy|girl)\b'),
    'F4': (r'轮椅|行动不便|拄拐|助行器|卧床|残障|残疾|腿脚不便|mobility (challenge|issue|problem)|wheelchair'),
    'F5': (r'盲|视障|视力(障碍|残疾|不好)|失明|全盲|看不见(路|东西)|guide dog|blind|visually impaired'),
    'F6': (r'聋|听障|听力(障碍|残疾|不好)|听不见|失聪|deaf|hard of hearing|hearing[- ]impaired|sign language'),
    'F7': (r'孕妇|怀孕|身怀|待产|抱(着|起).{0,4}(婴|孩子|娃|宝宝)|婴儿|襁褓|pregnan|\bwith (a|her) baby\b'),
    'F8': (r'独居|独自(一人)?(住|在家|生活)|一个人住|无人(同住|相伴)|孤身|'
           r'lived alone|living alone|by (him|her)self'),
}
RX = {k: (re.compile(v, re.I) if v else None) for k, v in AX.items()}

rows = list(csv.DictReader(open(os.path.join(PKG, '输入包_编码集v4.csv'), encoding='utf-8-sig')))
print('切片', len(rows))

hit = defaultdict(list)
for r in rows:
    body = r['正文']
    for ax, rx in RX.items():
        if rx is None:
            continue
        m = rx.search(body)
        if m:
            s = m.start()
            hit[ax].append(dict(切片ID=r['切片ID'], 标题=r['标题'][:50],
                                证据=body[max(0, s - 60):s + 90].replace('\n', ' ')))

print()
print(f"{'档':<4}{'候选数':>5}  证据样例")
for ax in AX:
    n = len(hit[ax])
    tag = '' if n >= 3 else ('  ← 单点' if n >= 1 else '  ← 空')
    eg = hit[ax][0]['证据'][:70] if n else ''
    print(f'{ax:<4}{n:>5}{tag}  {eg}')

json.dump(hit, open(os.path.join(HERE, 'axis_scan.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'axis_scan.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['层级', '档', '候选数', '切片ID', '证据'])
    for ax in AX:
        for h in hit[ax]:
            w.writerow([ax[0], ax, len(hit[ax]), h['切片ID'], h['证据']])
print('\n写入 axis_scan.csv / axis_scan.json')
