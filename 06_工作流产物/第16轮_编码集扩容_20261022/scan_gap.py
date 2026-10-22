# -*- coding: utf-8 -*-
"""库内缺口扫描：对未入集的 1053 个事件，按六个补搜靶点做关键词命中。

靶点来自 v1 打标结果（60 切片 / 51 事件）的真实分布：
  D4 跨户跨楼跨阳台 = 0    E4 等通知等警报 = 0
  F5 视障 = 0              F6 听障 = 0
  E3 外部指令替代 = 1      E5 官方信号致误判 = 1    F8 独居 = 2
产出：库内命中.csv（事件×靶点×证据句），供人工逐条确认。
"""
import json, re, csv, os, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'C:\Users\Administrator\WorkBuddy\2026-10-22-12-32-14'
TMP = os.path.join(ROOT, '_tmp')
OUT = os.path.dirname(os.path.abspath(__file__))

FAM = {
    'F5_视障': re.compile(
        r'盲人|失明|双目失明|视障|视力障碍|视觉障碍|导盲犬|看不清路'
        r'|blind (man|woman|resident|tenant|neighbou?r|occupant|person)'
        r'|visually impaired|sightless|legally blind', re.I),
    'F6_听障': re.compile(
        r'聋哑|聋人|失聪|听障|听力障碍|助听器|人工耳蜗|手语'
        r'|\bdeaf\b|hard of hearing|hearing impaired|hearing loss'
        r'|strobe (light |alarm)|flashing light alarm', re.I),
    'F8_独居': re.compile(
        r'独居|独自居住|一人居住|独自一人|孤寡'
        r'|liv(ed|ing) alone|alone in (his|her|the) (flat|apartment|home|house)'
        r'|(by|on) (him|her)self in the (flat|apartment|home)', re.I),
    'D4_跨户跨楼': re.compile(
        r'(climb|jump|crawl|step)\w*\s+(over|across|onto|through)\s+(the\s+)?(balcon|railing|partition|wall)'
        r'|(neighbo?r|adjacent|next)\w*\s*(flat|apartment|balcony|unit|block)'
        r'|balcony to balcony|through the (neighbo?r|adjoining)'
        r'|隔壁(邻居|住户|阳台|单元|楼)|翻(过|越)(阳台|栏杆|墙|窗)|跨(过|到)(阳台|隔壁|邻栋)'
        r'|邻栋|相邻(楼栋|单元)|从阳台(爬|翻|跳)', re.I),
    'E3_外部指令': re.compile(
        r'(operator|dispatcher|911|999|112|119|control room)\w*[^.]{0,60}(told|instruct|guide|advise|direct)'
        r'|guided (me|him|her|them|us) (out|through|down)'
        r'|(接线员|接警员|调度员|指挥中心|值班员)[^。]{0,40}(指导|指导|让我|指引|指挥|告知)'
        r'|电话(里|中)?(指导|引导|指引)|(消防|接警)[^。]{0,10}电话[^。]{0,20}(躲|别动|关门|下楼)', re.I),
    'E4_等通知等警报': re.compile(
        r'wait\w*\s+(for|until)\s+(the\s+)?(alarm|siren|instruction|word|firefighters|help)'
        r'|wait\w*\s+(inside|in the (flat|apartment|room))'
        r'|no one (told|warned) (us|them|him|her)[^.]{0,60}(until|before)'
        r'|等(警报|通知|指示|消防|救援)|一直等|迟迟(没有|不见)|等到(消防|警|通知)'
        r'|没人(通知|告知|敲门)', re.I),
    'E5_官方信号致误判': re.compile(
        r'false alarm|th(o|ou)ght (it|the alarm)[^.]{0,40}(drill|test|false)'
        r'|(told|assured)[^.]{0,40}(stay|remain)[^.]{0,20}(inside|in (your|the) (unit|flat|apartment|room))'
        r'|alarm (was )?(switched off|disabled|silenced|turned off)'
        r'|以为(是)?(演习|演练|误报|假警)|误以为|被告知(没有|没事|不用|留在)|警报(被关|关掉|停用|误报)', re.I),
}

def main():
    ev = json.load(open(os.path.join(TMP, 'r2', 'unified3.json'), encoding='utf-8'))
    fin = json.load(open(os.path.join(TMP, 'events_final.json'), encoding='utf-8'))
    mem = {e['evg']: e['members'] for e in fin}
    art = json.load(open(os.path.join(TMP, 'bygid.json'), encoding='utf-8'))
    art = {int(k): v for k, v in art.items()}

    sel = {x['事件组ID'] for x in ev if x['处置'] == '入编码集'}
    rows = []
    for e in ev:
        if e['事件组ID'] in sel:
            continue
        gids = mem.get(e['事件组ID'], [e['代表gid']])
        texts = []
        for g in gids:
            a = art.get(g)
            if a:
                texts.append((g, a.get('标题', ''), a.get('正文(前2000)', '') or ''))
        if not texts:
            continue
        hits = {}
        for fam, rx in FAM.items():
            best = None
            for g, title, txt in texts:
                for m in rx.finditer(txt):
                    s = max(0, m.start() - 60); t = min(len(txt), m.end() + 60)
                    snip = txt[s:t].replace('\n', ' ')
                    if best is None or len(snip):
                        best = (g, snip)
                    break
                if best:
                    break
            if best:
                hits[fam] = best
        if hits:
            longest = max((len(t[2]) for t in texts), default=0)
            rows.append(dict(事件组ID=e['事件组ID'], 标题=e['标题'][:90], 篇数=e['篇数'],
                             过程类数=e['过程类数'], 可重建档=e['可重建档'], 最长正文=longest,
                             命中='|'.join(hits), 来源=e['来源'], 簇=e['簇'][:30],
                             证据=' || '.join(f'{k}: {v[1]}' for k, v in hits.items())[:700]))
    rows.sort(key=lambda r: (-len(r['命中'].split('|')), -r['过程类数'], -r['最长正文']))
    with open(os.path.join(OUT, '库内命中.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    from collections import Counter
    c = Counter()
    for r in rows:
        for k in r['命中'].split('|'):
            c[k] += 1
    print('未入集事件命中', len(rows), '个')
    for k, v in c.most_common():
        print(f'  {k:<14} {v}')
    print()
    for r in rows[:25]:
        print(r['事件组ID'], r['命中'], f"过程{r['过程类数']} 篇{r['篇数']} 长{r['最长正文']}", r['标题'][:60])

if __name__ == '__main__':
    main()
