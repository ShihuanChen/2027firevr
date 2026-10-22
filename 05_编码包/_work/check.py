# -*- coding: utf-8 -*-
"""校验打标结果：键名、枚举值、摘录是否逐字存在于正文（≤30字）。"""
import json, io, sys, re, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

KEYS = ["id","p1","p2","p3","p4","p5","d1","d2","d3","d4","d5","a","b","c","d","e","f",
        "off_axis","off_axis_note","evidence","confidence"]
P1 = {"第一人称自述","记者旁观","官方通稿","混合"}
P2 = {"受灾者","救援者","管理者","旁观者","混合"}
P3 = {"线性顺叙","倒叙","多线并置","时间戳分段"}
P4 = {"逐句可重建","段落级概括","只有结论"}
P5 = {"恐惧","无助","愤怒","悲痛","感激","麻木","未呈现"}
DN = {"有","无","未报告"}
A = {"A1","A2","A3","A4","A5"}
B = {"B1","B2","B3","B4","B5"}
C = {"C1","C2","C3","C4","C5","C6"}
D = {"D1","D2","D3","D4","D5"}
E = {"E1","E2","E3","E4","E5"}
F = {"F1","F2","F3","F4","F5","F6","F7","F8"}
SETS = {"a":A,"b":B,"c":C,"d":D,"e":E,"f":F}

bodies = json.load(io.open('_work/bodies.json', encoding='utf-8'))


def latin_ok(q):
    """中文摘录按字数（<=30 字）；纯英文摘录按词数（<=30 词）。"""
    cjk = sum(1 for ch in q if '\u4e00' <= ch <= '\u9fff')
    if cjk:
        return cjk <= 30
    return len(q.split()) <= 30

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    s = s.replace('\u2019',"'").replace('\u2018',"'").replace('\u201c','"').replace('\u201d','"')
    s = s.replace('\u2014','-').replace('\u2013','-').replace('\u00b7','.')
    s = re.sub(r'\s+', ' ', s)
    return s.lower()

errs = []
seen = set()
lines = [l for l in io.open(sys.argv[1], encoding='utf-8') if l.strip()]
for i, line in enumerate(lines, 1):
    try:
        r = json.loads(line)
    except Exception as ex:
        errs.append(f"L{i} JSON解析失败: {ex}")
        continue
    if list(r.keys()) != KEYS:
        errs.append(f"L{i} 键名/顺序不符: {list(r.keys())}")
    rid = r.get('id')
    if rid in seen:
        errs.append(f"L{i} 重复id {rid}")
    seen.add(rid)
    if rid not in bodies:
        errs.append(f"L{i} id未知 {rid}")
        continue
    body = bodies[rid]['body']
    nb = norm(body)
    for k, ok in (('p1',P1),('p2',P2),('p3',P3),('p4',P4)):
        if r[k] not in ok:
            errs.append(f"{rid}.{k} 枚举非法: {r[k]}")
    for k in ('p5',):
        for v in r[k]:
            if v not in P5:
                errs.append(f"{rid}.{k} 枚举非法: {v}")
    for k in ('d1','d2','d3','d4','d5'):
        if r[k] not in DN:
            errs.append(f"{rid}.{k} 枚举非法: {r[k]}")
    for k, ok in SETS.items():
        for v in r[k]:
            if v not in ok:
                errs.append(f"{rid}.{k} 枚举非法: {v}")
    if r['off_axis'] not in ('有','无'):
        errs.append(f"{rid}.off_axis 非法: {r['off_axis']}")
    if r['off_axis']=='无' and r['off_axis_note']:
        errs.append(f"{rid} off_axis=无 但有 note")
    if r['off_axis']=='有' and not r['off_axis_note']:
        errs.append(f"{rid} off_axis=有 但 note 为空")
    if r['confidence'] not in ('high','low'):
        errs.append(f"{rid}.confidence 非法: {r['confidence']}")
    ev = r['evidence']
    if not isinstance(ev, list) or not ev:
        errs.append(f"{rid} evidence 为空")
        continue
    for e in ev:
        if set(e.keys()) != {'field','quote'}:
            errs.append(f"{rid} evidence 键名不符: {list(e.keys())}")
            continue
        if e['field'] not in KEYS:
            errs.append(f"{rid} evidence.field 非法: {e['field']}")
        q = e['quote']
        if not q:
            errs.append(f"{rid} evidence[{e['field']}] quote 为空")
            continue
        if len(q) > 30 and not latin_ok(q):
            errs.append(f"{rid} evidence[{e['field']}] 摘录超限: {q}")
        if norm(q) not in nb:
            errs.append(f"{rid} evidence[{e['field']}] 摘录不在正文: {q}")
    # 每个有值的轴/字段至少一条对应 evidence
    covered = {e['field'] for e in ev if isinstance(e, dict)}
    for k in ('a','b','c','d','e','f'):
        if r[k] and k not in covered:
            errs.append(f"{rid} 字段 {k} 有取值但无对应 evidence")
    for k in ('d1','d2','d3','d4','d5'):
        if r[k] in ('有','无') and k not in covered:
            errs.append(f"{rid} 字段 {k}={r[k]} 但无对应 evidence")
    for k in ('p1','p2','p3','p4'):
        if k not in covered:
            errs.append(f"{rid} 字段 {k} 无 evidence")

missing = set(bodies) - seen
if missing and '--full' in sys.argv:
    errs.append(f"缺少切片: {sorted(missing)}")

print(f"共 {len(lines)} 行")
if errs:
    print(f"❌ {len(errs)} 处问题:")
    for e in errs:
        print("  -", e)
else:
    print("✅ 全部通过")
