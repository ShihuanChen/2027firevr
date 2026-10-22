# -*- coding: utf-8 -*-
"""编码集正文装配：为每个候选事件取回可用正文（库内 2000 字 + S 系列按 URL 回抓）。

产出：
  _work/正文缓存.json    {gid 或 Sxx: {标题, 正文, 来源}}
  _work/事件正文清单.csv  每个事件的可选切片（按细节类型数、字数排序）
"""
import os, re, sys, json, csv, time, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\Administrator\WorkBuddy\2026-10-22-12-32-14'
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, '_work')
os.makedirs(WORK, exist_ok=True)
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'

DET = {
 '嗅觉': r'smell|smelled|smelt|odor|odour|stench|fumes|闻|焦味|刺鼻|呛鼻',
 '热与温度': r'\bheat\b|\bhot\b|scorching|temperature|烫|高温|灼|炙烤',
 '警报失效': r'(no|not|never|fail\w*)\s+\w{0,12}\s*(alarm|siren)|alarm\w*\s+(did not|didn.t|never|fail\w*)|(警报|警铃|报警器|火警)\S{0,8}(没响|未响|不响|失灵|失效|关闭|关掉)|without (an )?alarm',
 '警报有效': r'alarm\w*\s+(sounded|went off|rang|activated)|(警报|警铃|报警器)\S{0,6}(响了|响起|启动)',
 '声音': r'shout|scream|yell|bang|knock|shatter|crackl|喊|尖叫|敲|爆裂|呼救|噼啪',
 '照明失效': r'pitch.black|no (emergency )?light\w*|torch|flashlight|blackout|黑|停电|断电|手电|手机灯',
 '通道被锁': r'(door|gate|exit|stair)\w*\s*\w{0,15}\s*(lock|chain|jam|barred|block)|lock\w*\s+(door|gate|exit)|锁|反锁|铁链|封死|堵住|无法打开',
 '楼梯间充烟': r'(stair\w*|corridor)\s*\w{0,20}\s*(smoke|filled)|smoke\w*\s+(fill|swept|engulf)\w*\s+(the )?(stair|corridor)|楼梯\S{0,8}烟|走廊\S{0,8}(烟|黑)',
 '他人告知': r'neighbo\w*\s+(knock|warn|alert|told)|(friend|relative|colleague)\w*\s*(call|messag|text|told)|knock\w*\s+on|邻居\S{0,10}(敲门|告知|喊)|打电话(告诉|通知)',
 '自行发现': r'(saw|spotted|noticed|smelled)\s+(the\s+)?(flame|smoke|fire)|(看|发现|闻)\S{0,6}(火|烟)',
 '电梯逃生': r'(took|used|use)\s+(the\s+)?(lift|elevator)|by (lift|elevator)|乘(电梯|升降机)|坐电梯',
 '阳台窗口待援': r'(on|to|at)\s+the\s+balcony|from (the )?window|window ledge|阳台|窗口\S{0,6}(求救|挥手|等待)|空调外机',
 '固守待援': r'shelter\w*\s+in\s+place|stay\w*\s+(put|inside|in\s+(the|your)\s+(flat|apartment|room))|(关门|堵住门缝|湿毛巾|固守|等待救援|待在(房间|浴室|屋内))',
 '电话指导': r'(operator|dispatcher|911|999|119)\w*\s*\w{0,20}\s*(told|instruct|guide|advise)|接警员|电话\S{0,6}指导|调度员',
 '官方指令': r'broadcast|loudspeaker|public address|told (residents|occupants) to (leave|evacuate)|广播|通知\S{0,6}撤离|指令',
 '身体搬运': r'(carried|carry|piggyback|stair chair)\w*\s*\w{0,15}\s*(out|down|to safety)?|(抱|背|抬|搀)\S{0,6}(下楼|出去|转移)|楼梯椅',
 '身体受创': r'chok|cough|inhal|unconscious|dizzy|asphyx|呛|窒息|昏迷|熏|头晕|中毒|烧伤',
 '医疗设备依赖': r'(oxygen|medical)\s+(cylinder|tank|equipment)|oxygen\s+(mask|therapy)|氧气(瓶|罐|机)|呼吸机|轮椅|wheelchair',
 '跳楼坠落': r'(jump|jumped|fell|leap)\w*\s*\w{0,12}\s*(from|out|to (his|their) death)|跳(楼|下)|坠落|窗外',
 '消防设施无水': r'(no|not any)\s+water\s+(came|came out)|hose\w*\s+\w{0,12}\s*(dry|no water)|(消防喉|消火栓|消防栓|水枪)\S{0,10}(没水|无水)|dry riser',
 '疏散遗漏': r'(missed|overlook|unaccount|not (found|checked|searched))|未(逐户|排查|发现)|遗漏|漏(了|掉)',
 '主体属性': r'elderly|wheelchair|disabled|blind|deaf|pregnan|infant|bedridden|frail|老人|老年|残疾|失能|独居|婴儿|幼儿|孕妇|行动不便',
 '时间序列': r'\d{1,2}[:.]\d{2}\s*(am|pm)?|\d+(\.\d+)?\s*(minutes?|mins?|hours?)\s*(later|after)|分钟|随后|之后|几秒',
 '调查听证': r'hearing|inquiry|inquest|investigat\w+\s+(report|committee)|听证|调查(报告|委员会)',
 '情绪叙事': r'tears|crying|wept|grief|devastat|guilt|terrif|情绪|哭|泪|悲痛|自责|恐惧',
 '政策通稿': r'safety campaign|inspection|rectif|regulat\w+\s+overhaul|专项(检查|整治)|排查|隐患(整治|排查)',
}
DET_C = {k: re.compile(v, re.I) for k, v in DET.items()}
PROCESS = ['嗅觉','热与温度','警报失效','警报有效','声音','照明失效','通道被锁','楼梯间充烟','他人告知',
           '自行发现','电梯逃生','阳台窗口待援','固守待援','电话指导','官方指令','身体搬运','身体受创',
           '医疗设备依赖','跳楼坠落','消防设施无水','疏散遗漏','时间序列']


def http_get(url, timeout=25, retries=2):
    for i in range(retries + 1):
        try:
            r = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'})
            with urllib.request.urlopen(r, timeout=timeout) as resp:
                raw = resp.read(); enc = resp.headers.get_content_charset()
            for e in ([enc] if enc else []) + ['utf-8', 'gb18030']:
                try:
                    return raw.decode(e)
                except Exception:
                    continue
            return raw.decode('utf-8', 'replace')
        except urllib.error.HTTPError as ex:
            if ex.code in (429, 503) and i < retries:
                time.sleep(6); continue
            return None
        except Exception:
            if i < retries:
                time.sleep(2); continue
            return None
    return None


def extract_body(html):
    if not html:
        return ''
    try:
        from lxml import html as LH
        doc = LH.fromstring(html)
    except Exception:
        return ''
    for bad in doc.xpath('//script|//style|//nav|//header|//footer|//aside|//form|//noscript'):
        try:
            bad.getparent().remove(bad)
        except Exception:
            pass
    ps = [(' '.join(p.text_content().split())) for p in doc.xpath('//p')]
    ps = [p for p in ps if len(p) >= 30]
    body = '\n'.join(ps)
    if len(body) < 300:
        allt = ' '.join(doc.text_content().split())
        body = allt if len(allt) > len(body) else body
    return body[:4000]


def main():
    ev = json.load(open(os.path.join(ROOT, '_tmp', 'r2', 'unified3.json'), encoding='utf-8'))
    fin = json.load(open(os.path.join(ROOT, '_tmp', 'events_final.json'), encoding='utf-8'))
    mem = {e['evg']: e['members'] for e in fin}
    art = json.load(open(os.path.join(ROOT, '_tmp', 'bygid.json'), encoding='utf-8'))
    art = {int(k): v for k, v in art.items()}
    cache_path = os.path.join(WORK, '正文缓存.json')
    cache = json.load(open(cache_path, encoding='utf-8')) if os.path.exists(cache_path) else {}

    rows = []
    for e in ev:
        eid = e['事件组ID']
        texts = []
        if eid in mem or e['代表gid'] in art:
            for g in mem.get(eid, [e['代表gid']]):
                a = art.get(g)
                if a and a.get('正文(前2000)'):
                    texts.append(dict(key=str(g), 标题=a.get('标题', ''), 正文=a['正文(前2000)'], 出处='库内'))
        if not texts and e.get('URL'):
            if eid in cache and cache[eid].get('正文'):
                c = cache[eid]
                texts.append(dict(key=eid, 标题=c['标题'], 正文=c['正文'], 出处='URL缓存'))
            else:
                b = extract_body(http_get(e['URL'], timeout=25))
                print(f'  回抓 {eid} {len(b)} 字 {e["URL"][:50]}')
                cache[eid] = dict(标题=e['标题'], 正文=b, url=e['URL'])
                if b:
                    texts.append(dict(key=eid, 标题=e['标题'], 正文=b, 出处='URL新抓'))
        for t in texts:
            t['字数'] = len(t['正文'])
            t['细节类'] = [k for k, rx in DET_C.items() if rx.search(t['正文'])]
            t['过程类数'] = len([x for x in t['细节类'] if x in PROCESS])
            t['通稿判据'] = '通稿' if (t['过程类数'] <= 2 and len([x for x in t['细节类'] if x in ('主体属性','调查听证','政策通稿','情绪叙事')]) >= 3) else ''
        texts.sort(key=lambda t: (-t['过程类数'], -t['字数']))
        for i, t in enumerate(texts, 1):
            rows.append(dict(事件组ID=eid, 序=i, 可选篇数=len(texts), key=t['key'], 出处=t['出处'],
                             标题=t['标题'], 字数=t['字数'], 过程类数=t['过程类数'],
                             命中='|'.join(t['细节类']), 通稿=t['通稿判据'],
                             正文=t['正文'], URL=e.get('URL', ''), 处置=e['处置'], 来源=e['来源']))
    json.dump(cache, open(cache_path, 'w', encoding='utf-8'), ensure_ascii=False)
    with open(os.path.join(WORK, '事件正文清单.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    ok = len({r['事件组ID'] for r in rows if r['字数'] >= 600})
    print(f'事件 {len(ev)}，有可用正文 {ok}，切片候选 {len(rows)}')

if __name__ == '__main__':
    main()
