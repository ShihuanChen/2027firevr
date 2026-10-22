# -*- coding: utf-8 -*-
"""第三轮定向补搜：专打 F6 听障，兼补 E4/D2/A2 等单点档。
相对前两轮的三处放宽：
1) 标题只要求含火灾词，不强制含建筑词（"deaf man died in house fire" 不含 apartment）
2) 目标命中不依赖 VERIFY 正则，用独立命中词表，多语种
3) 过程类门槛从 3 降到 2，但字数门槛提到 700（听障报道短，但要够写过程）
"""
import os, sys, json, csv, re, time, importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
R16 = os.path.join(os.path.dirname(HERE), '第16轮_编码集扩容_20261022')


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname) if os.path.exists(os.path.join(HERE, fname)) else os.path.join(R16, fname))
    m = importlib.util.module_from_spec(spec); sys.argv = ['x']; spec.loader.exec_module(m); return m


bs = load('bs', '精准补搜.py')
gd = load('gd', 'gnews_decode.py')

# 目标 -> (命中词表, 过程类门槛, 字数门槛)
HIT = {
    'F6': (r'deaf|hard of hearing|hearing[- ]impaired|sign language|nonverbal alarm|strobe|flashing alarm|'
           r'听障|聋|失聪|听力障碍|聴覚障害|聴覚|청각장애|농아|sord[oa]|surdo|surd[oa]|sourd[e]?|gehörlos|'
           r'tunarungu|kuulovammai|nepočujúc|głuch|neslyšíc|глух', 2, 700),
    'F5': (r'blind|visually impaired|vision impaired|guide dog|low vision|'
           r'视障|盲人|失明|全盲|視覚障害|盲導犬|시각장애|ciego|ciega|invid|aveugle|blind', 2, 700),
    'E4': (r'wait(ed|ing) for (instruct|direct|order|police|firefighter|announce)|told to (stay|remain|wait)|'
           r'stayed put|stay-put|shelter in place|await(ed|ing) rescue|等待指令|等待通知|等待救援|等待广播|'
           r'被告知留在|原地等待|待援', 3, 780),
    'D2': (r'roof(?:top)?|terrace|upper floor|climbed (?:up|to)|went up to|'
           r'天台|楼顶|屋顶|避难层|向上|上が|옥상', 3, 780),
    'A2': (r'only (?:one )?(?:exit|stair|staircase|way out)|single (?:exit|staircase)|'
           r'唯一的?(?:出口|楼梯)|只有一(?:个|条)(?:出口|楼梯)|单一出口', 3, 700),
    'C4': (r'padlock|chained|locked (?:exit|door|gate)|blocked (?:exit|stair)|debris|stored goods|'
           r'锁死|铁链|上锁|堆物|杂物|封堵|堵塞', 3, 700),
}

Q = [
    # F6 主线
    ('F6', 'en', 'deaf man died apartment fire no smoke alarm'),
    ('F6', 'en', 'deaf woman killed house fire hearing impaired'),
    ('F6', 'en', 'deaf couple apartment fire rescued neighbours'),
    ('F6', 'en', 'deaf residents high rise fire evacuation strobe'),
    ('F6', 'en', 'hard of hearing tenant fire building escaped'),
    ('F6', 'en', 'flashing strobe alarm deaf family house fire'),
    ('F6', 'en', 'deaf student dormitory fire evacuation'),
    ('F6', 'en', 'deaf woman fire alarm could not hear died'),
    ('F6', 'en', 'sign language interpreter fire evacuation deaf residents'),
    ('F6', 'zh', '听障 火灾 身亡'),
    ('F6', 'zh', '聋人 火灾 逃生'),
    ('F6', 'zh', '听力障碍 火灾 警报 听不见'),
    ('F6', 'zh', '听障 独居 火灾 邻居'),
    ('F6', 'ja', '聴覚障害者 火災 逃げ遅れ'),
    ('F6', 'ja', '聴覚障害 火災 避難 サイレン'),
    ('F6', 'ko', '청각장애 화재 사망'),
    ('F6', 'ko', '청각장애인 화재 대피'),
    ('F6', 'es', 'sordo incendio edificio murió'),
    ('F6', 'es', 'sordos incendio evacuación alerta'),
    ('F6', 'pt', 'surdo incêndio prédio morreu'),
    ('F6', 'fr', 'sourd incendie immeuble alerte'),
    ('F6', 'de', 'Gehörloser Brand Wohnung Alarm'),
    ('F6', 'id', 'tunarungu kebakaran apartemen'),
    ('F6', 'tr', 'işitme engelli yangın apartman'),
    # 其余单点档
    ('E4', 'en', 'residents waited for instructions fire building evacuation delayed'),
    ('E4', 'en', 'told to stay inside apartment fire residents'),
    ('E4', 'zh', '住户 等待 通知 火灾 未及时撤离'),
    ('D2', 'en', 'residents climbed to rooftop fire escape helicopter'),
    ('D2', 'zh', '天台 火灾 被困 消防 救下'),
    ('A2', 'en', 'single staircase apartment fire trapped residents'),
    ('C4', 'en', 'locked fire exit residents died apartment'),
    ('C4', 'zh', '消防通道 锁死 火灾'),
]

print('查询数', len(Q))
raw, seen = [], set()
for tag, lang, q in Q:
    try:
        items = bs.gnews(q, lang)
    except Exception as e:
        print('  ERR', q[:30], e); items = []
    n = 0
    for it in items[:40]:
        t = it['title']
        if not bs.FIRE.search(t):
            continue
        if bs.EXCL.search(t):
            continue
        k = re.sub(r'\W+', '', t.lower())[:50]
        if k in seen:
            continue
        seen.add(k)
        raw.append(dict(目标=tag, 语言=lang, 查询=q, 源='gnews', 标题=t, URL=it['url'],
                        日期=it.get('seendate', ''), 域名=it.get('domain', '')))
        n += 1
    print(f'  {tag} {lang} {q[:42]:<42} +{n}')
    time.sleep(1.5)

print('原始', len(raw))
with open(os.path.join(HERE, '补搜3_原始.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['目标', '语言', '查询', '源', '标题', 'URL', '日期', '域名'])
    w.writeheader(); w.writerows(raw)

MAP = os.path.join(R16, '_work', '链接映射.json')
BODY = os.path.join(R16, '_work', '补搜正文.json')
cmap = json.load(open(MAP, encoding='utf-8')) if os.path.exists(MAP) else {}
cbody = json.load(open(BODY, encoding='utf-8')) if os.path.exists(BODY) else {}


def resolve(r):
    u = r['URL']
    if u not in cmap:
        try:
            cmap[u] = gd.decode(u)
        except Exception:
            cmap[u] = ''
    u = cmap[u] or ''
    if u and u not in cbody:
        try:
            cbody[u] = bs.extract_body(bs.http_get(u, timeout=18, retries=1))
        except Exception:
            cbody[u] = ''
    return r


with ThreadPoolExecutor(max_workers=12) as ex:
    futs = [ex.submit(resolve, r) for r in raw]
    for i, f in enumerate(as_completed(futs), 1):
        try:
            f.result()
        except Exception:
            pass
        if i % 40 == 0:
            print('  抓取', i)
json.dump(cmap, open(MAP, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(cbody, open(BODY, 'w', encoding='utf-8'), ensure_ascii=False)

stat = dict(解码失败=0, 抓不到=0, 太短=0, 非火灾=0, 类型不足=0, 目标未命中=0, 通过=0)
out = []
for r in raw:
    u = cmap.get(r['URL'], '')
    if not u:
        stat['解码失败'] += 1; continue
    body = cbody.get(u, '')
    if not body:
        stat['抓不到'] += 1; continue
    pat, pmin, cmin = HIT[r['目标']]
    if len(body) < cmin:
        stat['太短'] += 1; continue
    if not (bs.FIRE.search(body) and bs.BLDG.search(body)):
        stat['非火灾'] += 1; continue
    types = sorted(k for k, rx in bs.DET_C.items() if rx.search(body))
    proc = [t for t in types if t in bs.PROCESS]
    if len(proc) < pmin:
        stat['类型不足'] += 1; continue
    vm = re.search(pat, body, re.I)
    if not vm:
        stat['目标未命中'] += 1; continue
    stat['通过'] += 1
    s = vm.start()
    out.append(dict(目标=r['目标'], 语言=r['语言'], 标题=r['标题'], URL=u, 域名=r['域名'], 日期=r['日期'],
                    字数=len(body), 过程类数=len(proc), 命中='|'.join(proc),
                    目标命中=vm.group(0)[:40],
                    证据=body[max(0, s - 150):s + 190].replace('\n', ' ')))
print(stat)
out.sort(key=lambda x: (-x['过程类数'], -x['字数']))
with open(os.path.join(HERE, '补搜3_候选.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys()) if out else ['目标'])
    w.writeheader(); w.writerows(out)
print('候选', len(out))
for o in out:
    print(f"{o['目标']} p{o['过程类数']} {o['字数']:>5} {o['标题'][:70]}")
