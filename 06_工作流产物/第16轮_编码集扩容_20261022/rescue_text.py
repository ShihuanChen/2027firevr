# -*- coding: utf-8 -*-
"""补抓缺失正文：S01/S02/S03 原无 URL，S16/S21/S28/S36 原站反爬。
按事件关键词重搜一次，取能抓到的最长正文，写入 _work/正文缓存.json（与 build_texts 共用）。
"""
import os, sys, json, importlib.util, urllib.parse, re
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('bs', os.path.join(HERE, '精准补搜.py'))
bs = importlib.util.module_from_spec(spec); sys.argv = ['x']; spec.loader.exec_module(bs)
spec2 = importlib.util.spec_from_file_location('gd', os.path.join(HERE, 'gnews_decode.py'))
gd = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(gd)

CACHE = os.path.join(HERE, '_work', '正文缓存.json')
cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}

TARGETS = {
    'S01': [('en', 'Marshalltown fire Johannesburg Usindiso building'), ('en', 'Johannesburg inner city fire hijacked building survivors')],
    'S02': [('es', 'incendio Campanar Valencia edificio'), ('en', 'Valencia Campanar apartment block fire survivors')],
    'S03': [('en', 'Grand Kartal hotel fire Kartalkaya survivors'), ('en', 'Kartalkaya ski resort hotel fire guests escape')],
    'S16': [('zh', '九旬老人 火灾 救援 教科书'), ('zh', '老人 被困 火场 消防 救出 高层')],
    'S21': [('en', 'Dwarka fire three fell electronic lock apartment'), ('en', 'Dwarka Delhi fire died falling building locked')],
    'S28': [('en', 'residents carry children climb balconies escape fire'), ('en', 'Vietnam apartment fire residents climbed balconies')],
    'S36': [('zh', '高层公寓 火灾 被困 悬在窗外'), ('zh', '公寓 火灾 1死2伤 窗外 被困')],
}

for eid, qs in TARGETS.items():
    best = cache.get(eid)
    if best and len(best.get('正文', '')) >= 600:
        print(eid, '已有', len(best['正文']))
        continue
    best_body, best_title, best_url = '', '', ''
    for lang, q in qs:
        items = bs.gnews(q, lang)
        print(f'  {eid} {q[:40]} -> {len(items)}')
        for it in items[:8]:
            real = gd.decode(it['url'])
            if not real:
                continue
            body = bs.extract_body(bs.http_get(real, timeout=18, retries=1))
            if len(body) > len(best_body):
                best_body, best_title, best_url = body, it['title'], real
        if len(best_body) >= 1200:
            break
    if best_body:
        cache[eid] = dict(标题=best_title or eid, 正文=best_body[:4000], url=best_url)
        print(eid, '抓到', len(best_body), best_title[:60])
    else:
        print(eid, '仍失败')

json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
