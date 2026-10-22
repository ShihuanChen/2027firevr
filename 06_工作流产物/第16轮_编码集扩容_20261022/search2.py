# -*- coding: utf-8 -*-
"""第二轮定向补搜：只补高质量事件（不走缺口轴，专攻细节密度），把主分析集推到 60 起以上。"""
import os, sys, json, csv, importlib.util, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec); sys.argv = ['x']; spec.loader.exec_module(m); return m


bs = load('bs', '精准补搜.py')
gd = load('gd', 'gnews_decode.py')

Q = [
    ('en', 'apartment fire residents thick smoke stairs escape described'),
    ('en', 'high-rise fire stairwell residents escape 11th floor'),
    ('en', 'fire residents balcony rescued ladder apartment block'),
    ('en', 'tower block fire residents describe escape smoke corridor'),
    ('zh', '高层 火灾 疏散 楼梯 浓烟 住户 讲述'),
    ('zh', '住宅楼 火灾 被困 阳台 消防 云梯 救出'),
    ('id', 'kebakaran apartemen penghuni evakuasi tangga asap'),
    ('tr', 'apartman yangını sakinler merdiven duman tahliye'),
    ('pt', 'incêndio prédio moradores escada fumaça evacuados'),
    ('es', 'incendio edificio vecinos escalera humo evacuados'),
    ('fr', 'incendie immeuble habitants escalier fumée évacués'),
    ('ja', 'マンション 火災 住民 階段 煙 避難'),
]

raw = []
seen = set()
for lang, q in Q:
    items = bs.gnews(q, lang)
    n = 0
    for it in items[:40]:
        t = it['title']
        if not (bs.FIRE.search(t) and bs.BLDG.search(t)):
            continue
        if bs.EXCL.search(t):
            continue
        k = t.lower()[:60]
        if k in seen:
            continue
        seen.add(k)
        raw.append(dict(目标='Q', 语言=lang, 查询=q, 源='gnews', 标题=t, URL=it['url'],
                        日期=it.get('seendate', ''), 域名=it.get('domain', '')))
        n += 1
    print(f'{lang} {q[:40]:<40} +{n}')
    time.sleep(2)

p = os.path.join(HERE, '精准补搜_原始2.csv')
with open(p, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['目标', '语言', '查询', '源', '标题', 'URL', '日期', '域名'])
    w.writeheader(); w.writerows(raw)
print('原始2', len(raw))

cmap = json.load(open(os.path.join(HERE, '_work', '链接映射.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, '_work', '链接映射.json')) else {}
cbody = json.load(open(os.path.join(HERE, '_work', '补搜正文.json'), encoding='utf-8')) if os.path.exists(os.path.join(HERE, '_work', '补搜正文.json')) else {}


def work(r):
    u = gd.decode(r['URL']) if r['URL'] not in cmap else cmap[r['URL']]
    cmap[r['URL']] = u
    if u and u not in cbody:
        cbody[u] = bs.extract_body(bs.http_get(u, timeout=18, retries=1))
    return u


with ThreadPoolExecutor(max_workers=16) as ex:
    futs = [ex.submit(work, r) for r in raw]
    for i, f in enumerate(as_completed(futs), 1):
        try:
            f.result()
        except Exception:
            pass
        if i % 50 == 0:
            print('  fetch', i)
json.dump(cmap, open(os.path.join(HERE, '_work', '链接映射.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(cbody, open(os.path.join(HERE, '_work', '补搜正文.json'), 'w', encoding='utf-8'), ensure_ascii=False)

out = []
for r in raw:
    u = cmap.get(r['URL'], '')
    b = cbody.get(u, '')
    if len(b) < 900:
        continue
    if not (bs.FIRE.search(b) and bs.BLDG.search(b)):
        continue
    types = sorted(k for k, rx in bs.DET_C.items() if rx.search(b))
    proc = [t for t in types if t in bs.PROCESS]
    if len(proc) < 4:
        continue
    out.append(dict(目标='Q2', 语言=r['语言'], 标题=r['标题'], URL=u, 域名=r['域名'], 日期=r['日期'],
                    字数=len(b), 过程类数=len(proc), 命中='|'.join(proc), 目标命中='', 证据=b[:200].replace('\n', ' ')))
out.sort(key=lambda x: (-x['过程类数'], -x['字数']))
with open(os.path.join(HERE, '精准补搜_候选2.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys()) if out else ['目标'])
    w.writeheader(); w.writerows(out)
print('候选2', len(out))
for o in out[:30]:
    print(f"p{o['过程类数']:>2} {o['字数']:>4} {o['标题'][:70]} | {o['域名'][:20]}")
