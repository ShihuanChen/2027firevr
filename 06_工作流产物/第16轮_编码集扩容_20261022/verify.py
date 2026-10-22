# -*- coding: utf-8 -*-
"""候选复核：读 精准补搜_原始.csv，抓正文，逐级统计淘汰原因，按目标输出可读候选。

比 精准补搜.py 多做的事：
 1. 正文落盘缓存（_work/补搜正文.json），复核不用重抓
 2. 打印每一级门槛的存活数，避免"0 条"无法解释
 3. 目标命中句单独成列，人工一眼判断真假命中
"""
import os, re, sys, json, csv, time, urllib.request, urllib.error, difflib, importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('bs', os.path.join(HERE, '精准补搜.py'))
bs = importlib.util.module_from_spec(spec)
sys.argv = ['x']
spec.loader.exec_module(bs)

CACHE = os.path.join(HERE, '_work', '补搜正文.json')
os.makedirs(os.path.dirname(CACHE), exist_ok=True)
cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}

rows = list(csv.DictReader(open(os.path.join(HERE, '精准补搜_原始.csv'), encoding='utf-8-sig')))
print('原始', len(rows))

def get(u):
    if u in cache:
        return cache[u]
    b = bs.extract_body(bs.http_get(u, timeout=20, retries=1))
    cache[u] = b
    return b

todo = [r for r in rows if r['URL'] not in cache]
print('待抓', len(todo))
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(get, r['URL']): r for r in todo}
    for i, f in enumerate(as_completed(futs), 1):
        try:
            f.result()
        except Exception:
            pass
        if i % 40 == 0:
            print('  ', i)
json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)

stat = dict(抓不到=0, 太短=0, 非火灾=0, 类型不足=0, 目标未命中=0, 通过=0)
out = []
for r in rows:
    body = cache.get(r['URL'], '')
    if len(body) < 600:
        stat['抓不到' if len(body) == 0 else '太短'] += 1
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
    out.append(dict(目标=r['目标'], 语言=r['语言'], 标题=r['标题'], URL=r['URL'], 域名=r['域名'],
                    日期=r['日期'], 字数=len(body), 过程类数=len(proc), 命中='|'.join(proc),
                    目标命中=(vm.group(0)[:50] if vm else ''),
                    证据=body[max(0, s - 120):s + 160].replace('\n', ' ')))
print(stat)
out.sort(key=lambda x: (-x['过程类数'], -x['字数']))
fields = list(out[0].keys()) if out else ['目标']
with open(os.path.join(HERE, '精准补搜_候选.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(out)
from collections import Counter
print(Counter(o['目标'] for o in out))
for o in out:
    print(f"{o['目标']} p{o['过程类数']} {o['字数']:>4} {o['标题'][:64]}")
