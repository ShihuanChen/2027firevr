# -*- coding: utf-8 -*-
"""精准补搜 v2 —— 按 v1 打标的真实缺口定向搜，不搜泛"高层火灾"。

缺口来自 60 切片两模型合并结果：D4=0、E4=0、F5=0、F6=0、E3=1、E5=1、F8=2。
每条查询带目标标签，抓回正文后必须命中该目标的验证正则才算数，杜绝"标题像、正文无"的假命中。

用法：
  python 精准补搜.py --limit 0            # 全跑（约 6-10 分钟）
  python 精准补搜.py --tag F5 --limit 3   # 只跑 F5 前 3 条
产出：精准补搜_原始.csv / 精准补搜_候选.csv / 精准补搜_日志.json
"""
import os, re, sys, json, time, csv, argparse, urllib.request, urllib.parse, urllib.error, difflib
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r'C:\Users\Administrator\WorkBuddy\2026-10-22-12-32-14'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'

# ---------- 目标验证正则：命中才算补上该格 ----------
VERIFY = {
    'F5': re.compile(r'盲人|失明|视障|视力障碍|导盲犬|blind (man|woman|resident|tenant|neighbou?r|occupant)|visually impaired|legally blind|no (puede|podía) ver|ciego', re.I),
    'F6': re.compile(r'聋|听障|失聪|听力障碍|助听器|人工耳蜗|手语|\bdeaf\b|hard of hearing|hearing impaired|hearing loss|strobe|flashing (light|alarm)|聴覚障害|청각장애', re.I),
    'D4': re.compile(r'(climb|jump|crawl|step|lower|help)\w*\s+\w{0,12}\s*(over|across|onto|through)\s+(the\s+)?(balcon|railing|wall|ladder)|(neighbo?r|adjacent|next)\w*\s*(flat|apartment|balcony|unit)|balcony to balcony|through the (neighbo?r|adjoining)|隔壁|邻居(家|的)?(阳台|窗|房)|翻(过|越)|跨(过|到)|爬(到|过)', re.I),
    'E4': re.compile(r'wait\w*\s+(for|until)\s+(the\s+)?(alarm|siren|instruction|word|firefighters|help|rescue)|wait\w*\s+(inside|in (the|their) (flat|apartment|room))|no (one|body) (told|warned|alerted) (us|them|him|her)|never (heard|got) (the )?(alarm|warning)|等(警报|通知|指示|消防|救援)|没人(通知|告知|敲门)|一直等|迟迟', re.I),
    'E3': re.compile(r'(operator|dispatcher|911|999|112|119|control room)[^.]{0,80}(told|instruct|guide|advise|direct)|guided (me|him|her|them|us) (out|through|down|to safety)|接线员|接警员|调度员|电话[^。]{0,12}(指导|引导|指引|指挥)', re.I),
    'E5': re.compile(r'false alarm|thought (it|the alarm)[^.]{0,50}(drill|test|false)|(told|assured)[^.]{0,50}(stay|remain)[^.]{0,30}(inside|in (your|their|the) (unit|flat|apartment|room))|alarm (was )?(switched off|disabled|silenced|turned off)|以为(是)?(演习|演练|误报|假警)|误以为|被告知(没有|没事|不用|留在)', re.I),
    'F8': re.compile(r'独居|独自居住|一人居住|孤寡|liv(ed|ing) alone|alone in (his|her|the) (flat|apartment|home|house)|(by|on) (him|her)self in the', re.I),
    'Q':  re.compile(r'.', re.S),
}

QUERIES = [
    # F5 视障
    ('F5', 'en', '"blind" resident "apartment fire"'),
    ('F5', 'en', 'blind man "led out" fire smoke building'),
    ('F5', 'en', '"guide dog" fire rescue apartment'),
    ('F5', 'en', '"visually impaired" fire evacuated building'),
    ('F5', 'zh', '盲人 火灾 逃生 消防员'),
    ('F5', 'zh', '盲人按摩店 火灾'),
    ('F5', 'es', 'ciego incendio edificio evacuado'),
    # F6 听障
    ('F6', 'en', 'deaf "fire alarm" "did not hear"'),
    ('F6', 'en', 'deaf resident strobe fire apartment'),
    ('F6', 'en', '"hard of hearing" fire escape apartment'),
    ('F6', 'zh', '聋人 火灾 警报 闪光'),
    ('F6', 'zh', '聋哑人 火灾 被困 消防'),
    ('F6', 'ja', '聴覚障害 火災 逃げ遅れ'),
    ('F6', 'ko', '청각장애 화재 대피'),
    # D4 跨户跨楼跨阳台
    ('D4', 'en', 'neighbor climbed balcony fire rescue family'),
    ('D4', 'en', '"balcony to balcony" fire rescue'),
    ('D4', 'en', 'fire "jumped onto" neighbor balcony escape'),
    ('D4', 'zh', '火灾 爬 阳台 邻居 救出'),
    ('D4', 'zh', '火灾 隔壁 阳台 逃生 被困'),
    # E4 等通知等警报
    ('E4', 'en', '"no alarm" residents waited fire tower block'),
    ('E4', 'en', '"waited for the alarm" fire'),
    ('E4', 'zh', '火灾 没听到 警报 一直等'),
    ('E4', 'zh', '火灾 无人通知 住户 不知情'),
    # E3 外部指令替代
    ('E3', 'en', 'dispatcher guided woman out of burning apartment'),
    ('E3', 'en', '"on the phone" 911 guided family out fire'),
    ('E3', 'zh', '119 电话 指导 逃生 被困 火灾'),
    # E5 官方信号致误判
    ('E5', 'en', '"false alarm" tenants did not evacuate fire'),
    ('E5', 'en', '"told to stay inside" fire apartment residents'),
    ('E5', 'zh', '火灾 以为 演习 没有 撤离'),
    ('E5', 'zh', '火灾 警报 关闭 居民 不知'),
    # F8 独居
    ('F8', 'en', '"lived alone" fire apartment neighbor found'),
    ('F8', 'zh', '独居老人 火灾 无人发现'),
    # Q 通用高质量（补事件数）
    ('Q', 'en', 'apartment fire stairwell smoke "could not see" resident escape'),
    ('Q', 'en', 'tower block fire residents corridor smoke escape 2025'),
    ('Q', 'zh', '高层住宅 火灾 楼梯间 浓烟 逃生'),
    # ---- 追加：零格再补一轮同义表述 ----
    ('F5', 'en', 'blind tenant fire evacuated neighbors'),
    ('F5', 'en', 'blind couple apartment fire saved'),
    ('F5', 'zh', '视障 火灾 消防 疏散'),
    ('F5', 'zh', '盲人 火灾 邻居 救出 浓烟'),
    ('F5', 'ja', '視覚障害 火災 避難'),
    ('F6', 'en', 'deaf couple fire apartment no alarm'),
    ('F6', 'en', 'deaf man smoke alarm fire saved neighbor'),
    ('F6', 'zh', '听障 火灾 逃生 手语'),
    ('F6', 'zh', '听障人士 火灾 警报 无法听到'),
    ('D4', 'en', 'climbed across balconies fire escape residents'),
    ('D4', 'en', 'fire through neighbour window escape family'),
    ('E4', 'en', 'nobody knocked fire residents slept'),
    ('E4', 'en', 'residents were not warned fire building'),
    ('E3', 'en', 'dispatcher stayed on the line fire escape apartment'),
    ('E3', 'zh', '接警员 电话 指导 火灾 逃生'),
]

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
 '主体属性': r'elderly|wheelchair|disabled|blind|deaf|pregnan|infant|bedridden|frail|老人|老年|残疾|失能|独居|婴儿|幼儿|孕妇|行动不便',
 '时间序列': r'\d{1,2}[:.]\d{2}\s*(am|pm)?|\d+(\.\d+)?\s*(minutes?|mins?|hours?)\s*(later|after)|分钟|随后|之后|几秒',
}
DET_C = {k: re.compile(v, re.I) for k, v in DET.items()}
PROCESS = ['嗅觉', '热与温度', '警报失效', '警报有效', '声音', '照明失效', '通道被锁', '楼梯间充烟',
           '他人告知', '自行发现', '电梯逃生', '阳台窗口待援', '固守待援', '电话指导', '官方指令',
           '身体搬运', '身体受创', '医疗设备依赖', '跳楼坠落', '消防设施无水', '时间序列']
NONPROC = ['主体属性']

FIRE = re.compile(r'fire|blaze|flame|inferno|smoke|burn|explosion|火|烧|烟|燃|incendio|fuego|humo|火災|煙|화재|حريق|yangın', re.I)
BLDG = re.compile(r'楼|塔|公寓|住宅|小区|大厦|民房|tower|high-?rise|apartment|flat|block|building|hotel|hospital|宿舍|酒店|医院|养老|departamento|edificio|マンション|ビル|아파트|بناية', re.I)
EXCL = re.compile(r'wildfire|bushfire|forest fire|grass fire|wildland|shelling|纪念|anniversary|memorial|arson trial|演练|演习|drill', re.I)


def http_get(url, timeout=25, retries=2):
    for i in range(retries + 1):
        try:
            r = urllib.request.Request(url, headers={'User-Agent': UA,
                                                    'Accept-Language': 'en,zh;q=0.9',
                                                    'Accept': 'text/html,application/xhtml+xml,application/json,*/*'})
            with urllib.request.urlopen(r, timeout=timeout) as resp:
                raw = resp.read()
                enc = resp.headers.get_content_charset()
            for e in ([enc] if enc else []) + ['utf-8', 'gb18030']:
                try:
                    return raw.decode(e)
                except Exception:
                    continue
            return raw.decode('utf-8', 'replace')
        except urllib.error.HTTPError as ex:
            if ex.code in (429, 503) and i < retries:
                time.sleep(7 + i * 6)
                continue
            return None
        except Exception:
            if i < retries:
                time.sleep(2)
                continue
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
    ps = [p for p in ps if len(p) >= 40]
    body = '\n'.join(ps)
    if len(body) < 400:
        allt = ' '.join(doc.text_content().split())
        body = allt if len(allt) > len(body) else body
    return body[:6000]


def norm_title(t):
    t = (t or '').lower()
    t = re.sub(r'\s*[-–—|]\s*[^-–—|]{0,40}$', '', t)
    t = re.sub(r'[^a-z0-9\u4e00-\u9fff ]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def gdelt(q, lang, timespan='3m', mx=100):
    u = 'https://api.gdeltproject.org/api/v2/doc/doc?' + urllib.parse.urlencode({
        'query': f'{q} sourcelang:{lang if lang != "en" else "english"}',
        'mode': 'artlist', 'maxrecords': mx, 'format': 'json',
        'sort': 'hybridrel', 'timespan': timespan})
    t = http_get(u, timeout=60, retries=1)
    if not t or not t.strip().startswith('{'):
        return [], ('EMPTY' if not t else 'NONJSON')
    try:
        return json.loads(t).get('articles', []), None
    except Exception as e:
        return [], f'PARSE {e}'


def gnews(q, lang):
    cfg = {'en': ('en-US', 'US', 'US:en'), 'zh': ('zh-CN', 'CN', 'CN:zh-Hans'),
           'ja': ('ja', 'JP', 'JP:ja'), 'ko': ('ko', 'KR', 'KR:ko'),
           'es': ('es-419', 'CL', 'CL:es-419')}.get(lang, ('en-US', 'US', 'US:en'))
    u = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({
        'q': f'{q} after:2023-01-01 before:2026-10-22', 'hl': cfg[0], 'gl': cfg[1], 'ceid': cfg[2]})
    xml = http_get(u, timeout=30)
    if not xml:
        return []
    out = []
    for it in re.findall(r'<item>(.*?)</item>', xml, re.S)[:40]:
        ti = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', it, re.S)
        li = re.search(r'<link>(.*?)</link>', it, re.S)
        pd = re.search(r'<pubDate>(.*?)</pubDate>', it, re.S)
        sr = re.search(r'<source[^>]*>(.*?)</source>', it, re.S)
        if not ti or not li:
            continue
        out.append({'title': ti.group(1).strip(), 'url': li.group(1).strip(),
                    'seendate': pd.group(1) if pd else '', 'domain': sr.group(1) if sr else 'news.google.com'})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--tag', default='')
    ap.add_argument('--minlen', type=int, default=800)
    ap.add_argument('--mintype', type=int, default=3)
    ap.add_argument('--workers', type=int, default=10)
    ap.add_argument('--sleep', type=float, default=3.0)
    a = ap.parse_args()

    lib = json.load(open(os.path.join(ROOT, '_tmp', 'r2', 'unified3.json'), encoding='utf-8'))
    lib_titles = [norm_title(x['标题']) for x in lib]
    lib_set = set(lib_titles)

    qs = [q for q in QUERIES if not a.tag or q[0] == a.tag]
    if a.limit:
        qs = qs[:a.limit]

    raw, log = [], []
    seen = set()
    for tag, lang, q in qs:
        g, err = ([], 'SKIP') if os.environ.get('NOGDELT') else gdelt(q, lang)
        n_list = gnews(q, lang)
        got = [(tag, lang, q, 'gdelt', x.get('title', ''), x.get('url', ''),
                x.get('seendate', ''), x.get('domain', '')) for x in g]
        got += [(tag, lang, q, 'gnews', x['title'], x['url'], x['seendate'], x['domain']) for x in n_list]
        add = 0
        for r in got:
            key = (norm_title(r[4]), tag)
            if key in seen:
                continue
            seen.add(key)
            raw.append(r); add += 1
        log.append(dict(tag=tag, lang=lang, q=q, gdelt=len(g), gnews=len(n_list), add=add, err=err))
        print(f'[{tag}/{lang}] {q[:52]:<52} gdelt={len(g):>3} gnews={len(n_list):>2} add={add}')
        time.sleep(a.sleep)

    # 先按标题筛掉明显不合格的，再抓正文（省时间）
    cand = []
    for r in raw:
        tag, lang, q, src, title, url, date, dom = r
        if not FIRE.search(title) or not BLDG.search(title):
            if not (tag in ('F5', 'F6') and (FIRE.search(title))):
                continue
        if EXCL.search(title):
            continue
        nt = norm_title(title)
        if nt in lib_set or any(difflib.SequenceMatcher(None, nt, t).ratio() > 0.85 for t in lib_titles[:0]):
            continue
        cand.append(dict(目标=tag, 语言=lang, 查询=q, 源=src, 标题=title, URL=url, 日期=date, 域名=dom))
    print(f'\n标题通过 {len(cand)} / 原始 {len(raw)}，开始抓正文…')

    def work(c):
        body = extract_body(http_get(c['URL'], timeout=20, retries=1))
        c['正文长度'] = len(body)
        c['_body'] = body
        return c

    done = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(work, c) for c in cand]
        for i, f in enumerate(as_completed(futs), 1):
            try:
                done.append(f.result())
            except Exception:
                pass
            if i % 40 == 0:
                print(f'  抓取 {i}/{len(cand)}')

    out = []
    for c in done:
        body = c.pop('_body', '')
        if c['正文长度'] < a.minlen:
            continue
        if not (FIRE.search(body) and BLDG.search(body)):
            continue
        types = sorted(k for k, rx in DET_C.items() if rx.search(body))
        proc = [t for t in types if t in PROCESS]
        if len(proc) < a.mintype:
            continue
        vm = VERIFY[c['目标']].search(body) if c['目标'] in VERIFY else None
        m = vm.group(0) if vm else ''
        if c['目标'] != 'Q' and not m:
            continue
        s = vm.start() if vm else 0
        snip = body[max(0, s - 90):s + 120].replace('\n', ' ')
        c.update(细节类型数=len(proc), 过程类命中='|'.join(proc), 目标证据=snip[:260], 目标命中=m[:60])
        out.append(c)

    out.sort(key=lambda r: (-r['细节类型数'], -r['正文长度']))
    fields = ['目标', '语言', '查询', '源', '标题', 'URL', '日期', '域名', '正文长度', '细节类型数', '过程类命中', '目标命中', '目标证据']
    with open(os.path.join(HERE, '精准补搜_候选.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(out)
    with open(os.path.join(HERE, '精准补搜_原始.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh); w.writerow(['目标', '语言', '查询', '源', '标题', 'URL', '日期', '域名'])
        w.writerows(raw)
    json.dump(log, open(os.path.join(HERE, '精准补搜_日志.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n候选 {len(out)} 条（原始 {len(raw)} → 标题通过 {len(cand)}）')
    for o in out[:20]:
        print(f"  {o['目标']} 长{o['正文长度']:>5} 类{o['细节类型数']:>2} {o['标题'][:70]}")


if __name__ == '__main__':
    main()
