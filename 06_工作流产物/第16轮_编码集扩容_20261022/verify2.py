# -*- coding: utf-8 -*-
"""候选复核 v2：先解码 Google News 跳转链接，再抓正文，逐级统计淘汰原因。"""
import os, sys, json, csv, importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec); sys.argv = ['x']; spec.loader.exec_module(m); return m


bs = load('bs', '精准补搜.py')
gd = load('gd', 'gnews_decode.py')

MAP = os.path.join(HERE, '_work', '链接映射.json')
BODY = os.path.join(HERE, '_work', '补搜正文.json')
cmap = json.load(open(MAP, encoding='utf-8')) if os.path.exists(MAP) else {}
cbody = json.load(open(BODY, encoding='utf-8')) if os.path.exists(BODY) else {}

rows = list(csv.DictReader(open(os.path.join(HERE, '精准补搜_原始.csv'), encoding='utf-8-sig')))
print('原始', len(rows))


def resolve(r):
    u = r['URL']
    if r['源'] == 'gnews':
        if u not in cmap:
            cmap[u] = gd.decode(u)
        u = cmap[u] or ''
    if u and u not in cbody:
        cbody[u] = bs.extract_body(bs.http_get(u, timeout=20, retries=1))
    return u


todo = [r for r in rows if not (r['URL'] in cbody or (r['源'] == 'gnews' and cmap.get(r['URL'], 'X') == ''))]
print('待处理', len(todo))
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = [ex.submit(resolve, r) for r in todo]
    for i, f in enumerate(as_completed(futs), 1):
        try:
            f.result()
        except Exception:
            pass
        if i % 50 == 0:
            print('  ', i)
json.dump(cmap, open(MAP, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(cbody, open(BODY, 'w', encoding='utf-8'), ensure_ascii=False)

stat = dict(解码失败=0, 抓不到=0, 太短=0, 非火灾=0, 类型不足=0, 目标未命中=0, 通过=0)
out = []
for r in rows:
    u = cmap.get(r['URL'], r['URL']) if r['源'] == 'gnews' else r['URL']
    if r['源'] == 'gnews' and not u:
        stat['解码失败'] += 1
        continue
    body = cbody.get(u, '')
    if not body:
        stat['抓不到'] += 1
        continue
    if len(body) < 600:
        stat['太短'] += 1
        continue
    if not (bs.FIRE.search(body) and bs.BLDG.search(body)):
        stat['非火灾'] += 1
        continue
    types = sorted(k for k, rx in bs.DET_C.items() if rx.search(body))
    proc = [t for t in types if t in bs.PROCESS]
    if len(proc) < 3:
        stat['类型不足'] += 1
        continue
    vm = bs.VERIFY[r['目标']].search(body) if r['目标'] in bs.VERIFY else None
    if r['目标'] != 'Q' and not vm:
        stat['目标未命中'] += 1
        continue
    stat['通过'] += 1
    s = vm.start() if vm else 0
    out.append(dict(目标=r['目标'], 语言=r['语言'], 标题=r['标题'], URL=u, 域名=r['域名'], 日期=r['日期'],
                    字数=len(body), 过程类数=len(proc), 命中='|'.join(proc),
                    目标命中=(vm.group(0)[:50] if vm else ''),
                    证据=body[max(0, s - 130):s + 170].replace('\n', ' ')))
print(stat)
out.sort(key=lambda x: (-x['过程类数'], -x['字数']))
with open(os.path.join(HERE, '精准补搜_候选.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys()) if out else ['目标'])
    w.writeheader(); w.writerows(out)
from collections import Counter
print(Counter(o['目标'] for o in out))
for o in out:
    print(f"{o['目标']} p{o['过程类数']:>2} {o['字数']:>4} {o['标题'][:70]}")
