# -*- coding: utf-8 -*-
"""
批量补搜 v1 —— 脚本化补搜，替代逐条网页搜索。

用法：
  python 批量补搜.py --source both --limit 0        # 全量（约 8-12 分钟）
  python 批量补搜.py --source gdelt --limit 6      # 只跑前 6 个查询试水

产出（同目录）：
  补搜候选_原始.csv   所有命中，未过滤
  补搜候选_过滤.csv   过了质量门槛的，按细节类型数排序，供人工/AI 判定
  补搜日志.json       每个查询的返回量与错误

质量门槛（沿用第 12–14 轮迭代口径）：
  1. 标题同时含「火灾词」与「建筑词」
  2. 正文 ≥ 800 字符（可 --minlen 调）
  3. 细节类型 ≥ 3 类（25 类正则，与饱和验证脚本同源）
  4. 排除：演练、野火/森林火、战争致火、纪念、纯政策通稿
  5. 与库内 6666 条标题相似度 < 0.75（去除已收录）
"""
import os, re, sys, json, time, csv, argparse, hashlib, difflib, urllib.request, urllib.parse, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r'C:\Users\Administrator\WorkBuddy\2026-10-22-12-32-14'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'

# ---------- 查询矩阵：细节优先，不是"高层火灾"这种泛词 ----------
# 每个查询都强制带一个"可重建细节"锚点（楼梯间/锁死/警报/轮椅/固守/避难层）
QUERIES = [
    # 英文 · 通道与空间（宽查询 + 本地细节门槛，GDELT 多词 AND 太严会归零）
    ('en', '"apartment fire" (stairwell OR trapped)'),
    ('en', '"high-rise fire" (stairwell OR smoke)'),
    ('en', 'fire (stairwell OR "escape route") residents'),
    ('en', 'fire ("locked" OR "chained") exit residents'),
    ('en', 'fire corridor smoke "could not see"'),
    ('en', 'fire "tower block" residents smoke'),
    # 英文 · 警报与确认
    ('en', 'fire ("no alarm" OR "alarm did not") apartment'),
    ('en', 'fire neighbor ("knocked" OR "warned") residents'),
    ('en', 'fire residents ("nobody told us" OR "no warning")'),
    # 英文 · 身体与固守
    ('en', 'fire wheelchair trapped apartment stairs'),
    ('en', 'fire "shelter in place" residents'),
    ('en', 'fire "refuge floor" tower'),
    ('en', 'fire oxygen tank resident evacuated'),
    ('en', 'fire balcony "waiting to be rescued"'),
    # 英文 · 极端退出
    ('en', 'fire residents ("jumped" OR "fell") window apartment'),
    ('en', 'fire elevator smoke residents high-rise'),
    # 多语
    ('zh', '高层建筑 火灾 楼梯间'),
    ('zh', '住宅 火灾 防盗窗 被困'),
    ('zh', '火灾 消防栓 没水 高层'),
    ('es', 'incendio edificio escalera humo vecinos'),
    ('ja', 'マンション 火災 階段 煙'),
    ('ko', '아파트 화재 계단 연기'),
]

FIRE = re.compile(r'fire|blaze|flame|inferno|smoke|burn|explosion|火|烧|烟|燃|incendio|fuego|humo|火災|煙|화재|연기|حريق|yangın|duman', re.I)
BLDG = re.compile(r'楼|塔|公寓|住宅|小区|大厦|民房|tower|high-?rise|apartment|flat|block|building|hotel|hospital|宿舍|酒店|医院|养老|departamento|edificio|マンション|ビル|아파트|بناية|apartman|rezidans', re.I)
EXCL = re.compile(r'wildfire|bushfire|forest fire|grass fire|drill|演练|演习|wildland|war\b|shelling|纪念|anniversary|memorial|arson trial|policy|条例|整治|排查|培训|科普', re.I)

# 25 类细节（与 饱和验证_25类细节.py 同源）
DET = {
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
 '时间序列': r'\d{1,2}[:.]\d{2}\s*(am|pm)?|\d+(\.\d+)?\s*(minutes?|mins?|hours?)\s*(later|after)|分钟|随后|之后|几秒|\d{1,2}\s*点\d{0,2}',
 '主体属性': r'elderly|wheelchair|disabled|blind|deaf|pregnan|infant|bedridden|frail|老人|老年|残疾|失能|独居|婴儿|幼儿|孕妇|行动不便',
}
DET_C = {k: re.compile(v, re.I) for k, v in DET.items()}


def norm_title(t):
    t = (t or '').lower()
    t = re.sub(r'\s*[-–—|]\s*[^-–—|]{0,40}$', '', t)
    t = re.sub(r'[^a-z0-9\u4e00-\u9fff ]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


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
                time.sleep(6 + i * 5)
                continue
            return None
        except Exception:
            if i < retries:
                time.sleep(2)
                continue
            return None
    return None


def extract_body(html):
    """lxml 简易正文抽取：去 script/style/nav，取 <p> 合并"""
    if not html:
        return ''
    try:
        from lxml import html as LH
        doc = LH.fromstring(html)
    except Exception:
        return ''
    for bad in doc.xpath('//script|//style|//nav|//header|//footer|//aside|//form|//noscript'):
        bad.getparent().remove(bad)
    ps = [(' '.join(p.text_content().split())) for p in doc.xpath('//p')]
    ps = [p for p in ps if len(p) >= 40]
    body = '\n'.join(ps)
    if len(body) < 400:
        allt = ' '.join(doc.text_content().split())
        body = allt if len(allt) > len(body) else body
    return body[:6000]


def gdelt(q, lang, timespan='4y', mx=100):
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
    """Google News RSS：中文补位，只取标题与来源"""
    cfg = {'en': ('en-US', 'US', 'US:en'), 'zh': ('zh-CN', 'CN', 'CN:zh-Hans'),
           'ja': ('ja', 'JP', 'JP:ja'), 'es': ('es-419', 'CL', 'CL:es-419')}.get(lang, ('en-US', 'US', 'US:en'))
    u = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({
        'q': f'{q} after:2023-01-01 before:2026-10-22', 'hl': cfg[0], 'gl': cfg[1], 'ceid': cfg[2]})
    xml = http_get(u, timeout=30)
    if not xml:
        return []
    items = re.findall(r'<item>(.*?)</item>', xml, re.S)
    out = []
    for it in items[:40]:
        ti = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', it, re.S)
        li = re.search(r'<link>(.*?)</link>', it, re.S)
        pd = re.search(r'<pubDate>(.*?)</pubDate>', it, re.S)
        sr = re.search(r'<source[^>]*>(.*?)</source>', it, re.S)
        if not ti or not li:
            continue
        out.append({'title': ti.group(1).strip(), 'url': li.group(1).strip(),
                    'seendate': pd.group(1) if pd else '', 'domain': sr.group(1) if sr else 'news.google.com'})
    return out


def score(title, body):
    types = [k for k, c in DET_C.items() if c.search(body or '')]
    types_t = [k for k, c in DET_C.items() if c.search(title or '')]
    alltypes = sorted(set(types) | set(types_t))
    return alltypes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default='both', choices=['gdelt', 'gnews', 'both'])
    ap.add_argument('--limit', type=int, default=0, help='只跑前 N 个查询，0=全部')
    ap.add_argument('--minlen', type=int, default=800)
    ap.add_argument('--mintype', type=int, default=3)
    ap.add_argument('--timespan', default='4y')
    ap.add_argument('--fetch-body', action='store_true', default=True)
    ap.add_argument('--max-fetch', type=int, default=200)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--sleep', type=float, default=11.0)
    args = ap.parse_args()

    # 库内已有标题，用于去重
    lib_norm = set()
    try:
        B = json.load(open(os.path.join(ROOT, '_tmp', 'bygid.json'), encoding='utf-8'))
        for v in B.values():
            if v.get('标题'):
                lib_norm.add(norm_title(v['标题']))
        print(f'库内标题 {len(lib_norm)} 条，用于去重')
    except Exception as e:
        print('库内标题读取失败，跳过去重:', e)

    qs = QUERIES if not args.limit else QUERIES[:args.limit]
    raw, log = [], []
    seen_url, seen_title = set(), set()

    for lang, q in qs:
        got = 0
        if args.source in ('gdelt', 'both'):
            arts, err = gdelt(q, lang, args.timespan)
            log.append({'src': 'gdelt', 'lang': lang, 'q': q, 'n': len(arts), 'err': err})
            for a in arts:
                u = a.get('url') or ''
                if not u or u in seen_url:
                    continue
                seen_url.add(u)
                raw.append({'src': 'gdelt', 'query': q, 'lang': lang,
                            'title': (a.get('title') or '').strip(), 'url': u,
                            'date': a.get('seendate', ''), 'domain': a.get('domain', ''), 'body': ''})
                got += 1
            time.sleep(max(args.sleep, 5.5))  # GDELT 限速
        if args.source in ('gnews', 'both') and lang in ('en', 'zh', 'ja', 'es'):
            for a in gnews(q, lang):
                u = a.get('url') or ''
                if not u or u in seen_url:
                    continue
                seen_url.add(u)
                raw.append({'src': 'gnews', 'query': q, 'lang': lang,
                            'title': a.get('title', ''), 'url': u,
                            'date': a.get('seendate', ''), 'domain': a.get('domain', ''), 'body': ''})
                got += 1
            time.sleep(1.5)
        print(f'  [{lang}] {q[:56]:<58} +{got}')

    print(f'\n原始命中 {len(raw)} 条')

    # 标题门槛 + 库内去重
    stage = []
    for r in raw:
        t = r['title']
        if not (FIRE.search(t) and BLDG.search(t)):
            continue
        if EXCL.search(t):
            continue
        nt = norm_title(t)
        if nt in lib_norm or nt in seen_title:
            continue
        # 与库内模糊去重
        if lib_norm and max((difflib.SequenceMatcher(None, nt, x).ratio() for x in lib_norm), default=0) >= 0.75:
            continue
        seen_title.add(nt)
        stage.append(r)
    print(f'标题门槛 + 去重后 {len(stage)} 条')

    # 抓正文
    if args.fetch_body and stage:
        stage = [r for r in stage if r['src'] == 'gdelt'] + [r for r in stage if r['src'] != 'gdelt']
        todo = [r for r in stage if r['src'] == 'gdelt'][:args.max_fetch]
        print(f'抓正文 {len(todo)} 条（并发 6）...')
        done = 0
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            fut = {ex.submit(lambda rr: extract_body(http_get(rr['url'], timeout=12, retries=0)), r): r for r in todo}
            for f in as_completed(fut):
                r = fut[f]
                try:
                    r['body'] = f.result() or ''
                except Exception:
                    r['body'] = ''
                done += 1
                if done % 20 == 0:
                    print(f'  {done}/{len(todo)}')

    # 质量门槛
    passed = []
    for r in stage:
        body = r.get('body') or ''
        if r['src'] != 'gdelt':
            body = body or ''
        types = score(r['title'], body)
        r['types'] = types
        r['n_types'] = len(types)
        r['chars'] = len(body)
        if r['src'] == 'gdelt' and len(body) < args.minlen:
            continue
        if len(types) < args.mintype:
            continue
        passed.append(r)
    passed.sort(key=lambda x: (-x['n_types'], -x['chars']))

    # 输出
    with open(os.path.join(HERE, '补搜候选_原始.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['src', 'lang', 'query', 'title', 'url', 'date', 'domain',
                                           'chars', 'n_types', 'types', 'body'])
        w.writeheader()
        for r in raw:
            w.writerow({**{k: r.get(k, '') for k in w.fieldnames[:-2]},
                        'chars': len(r.get('body') or ''),
                        'n_types': '', 'types': '', 'body': (r.get('body') or '')[:2000]})
    with open(os.path.join(HERE, '补搜候选_过滤.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['序号', 'src', 'lang', 'title', 'url', 'date', 'domain',
                                           'chars', 'n_types', 'types', 'body'])
        w.writeheader()
        for i, r in enumerate(passed, 1):
            w.writerow({'序号': i, 'src': r['src'], 'lang': r['lang'], 'title': r['title'], 'url': r['url'],
                        'date': r['date'], 'domain': r['domain'], 'chars': r['chars'],
                        'n_types': r['n_types'], 'types': '／'.join(r['types']), 'body': (r['body'] or '')[:2000]})
    json.dump(log, open(os.path.join(HERE, '补搜日志.json'), 'w'), ensure_ascii=False, indent=1)

    print(f'\n过质量门槛 {len(passed)} 条 → 补搜候选_过滤.csv')
    for r in passed[:25]:
        print(f"  {r['n_types']:>2}类 {r['chars']:>5}字 {r['lang']} {r['title'][:66]}")


if __name__ == '__main__':
    main()
