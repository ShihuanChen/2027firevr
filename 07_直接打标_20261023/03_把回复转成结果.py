# -*- coding: utf-8 -*-
"""把网页 AI 的回复（纯文本）转成编码结果 jsonl。

用法：
  1. 把每个 AI 的回复存成 txt，放进 粘贴/ 下，文件名以 A_ / B_ / C_ 开头
     例：粘贴/A_第01批.txt、粘贴/A_第02批.txt、粘贴/B_第01批.txt
     也可以按人分目录：粘贴/A/第01批.txt
  2. python 03_把回复转成结果.py
  3. 合并（在 06_工作流产物/第18轮_三模型全量编码_20261022 下）：
     PROMPT_VER=v4.2-manual python merge_and_kappa.py A B C

脚本只认 json 对象本身，AI 多说了话、加了 markdown 代码块、写成多行，都能抓出来。
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
PASTE = os.path.join(HERE, '粘贴')
OUT = os.path.join(HERE, '结果')
S18 = os.path.join(REPO, '06_工作流产物', '第18轮_三模型全量编码_20261022')
VER = 'v4.2-manual'

sys.path.insert(0, S18)
import run_models as rm          # 复用同一套字段白名单与归一化，避免两份规则漂移


def find_objects(text):
    """按括号配对扫描出所有 {...}，跳过字符串内的括号。"""
    out, i, n = [], 0, len(text)
    while i < n:
        if text[i] != '{':
            i += 1
            continue
        depth, j, instr, esc = 0, i, False, False
        while j < n:
            c = text[j]
            if instr:
                if esc:
                    esc = False
                elif c == '\\':
                    esc = True
                elif c == '"':
                    instr = False
            elif c == '"':
                instr = True
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    out.append(text[i:j + 1])
                    break
            j += 1
        i = j + 1 if j < n else n
    return out


def loads(s):
    for cand in (s,
                 re.sub(r'[\u201c\u201d]', '"', s),
                 re.sub(r',\s*([\]}])', r'\1', re.sub(r'[\u201c\u201d]', '"', s))):
        try:
            v = json.loads(cand)
            return v if isinstance(v, dict) else None
        except Exception:
            continue
    return None


def tag_of(path):
    rel = os.path.relpath(path, PASTE)
    parts = rel.split(os.sep)
    for p in parts[:-1]:                      # 先看子目录
        m = re.match(r'^([A-Za-z])$', p.strip())
        if m:
            return m.group(1).upper()
    m = re.match(r'^([A-Za-z])[_\-\s]', parts[-1])   # 再看文件名前缀
    return m.group(1).upper() if m else None


def main():
    if not os.path.isdir(PASTE):
        print('没有 粘贴/ 目录')
        return
    files = [os.path.join(dp, f) for dp, _, fs in os.walk(PASTE) for f in fs
             if f.lower().endswith(('.txt', '.md'))]
    if not files:
        print('粘贴/ 里还没有文件。把 AI 的回复存成 A_第01批.txt 这样的名字放进去。')
        return

    valid_ids = set()
    import csv
    for r in csv.DictReader(open(os.path.join(REPO, '05_编码包', '输入包_编码集v4.csv'),
                                 encoding='utf-8-sig')):
        valid_ids.add(r['切片ID'])

    os.makedirs(OUT, exist_ok=True)
    buckets, dup, bad = {}, {}, []

    for f in sorted(files):
        tag = tag_of(f)
        if not tag:
            print(f'跳过（文件名没有 A_/B_/C_ 前缀，也没放在 A/B/C 目录里）：{os.path.basename(f)}')
            continue
        raw = open(f, encoding='utf-8', errors='ignore').read()
        got = 0
        for blob in find_objects(raw):
            rec = loads(blob)
            if not rec:
                bad.append((os.path.basename(f), blob[:60]))
                continue
            sid = str(rec.get('id', '')).strip()
            if sid not in valid_ids:
                bad.append((os.path.basename(f), f'id 不认识：{sid}'))
                continue
            if sid in buckets.setdefault(tag, {}):
                dup.setdefault(tag, []).append(sid)
            clean, inv = rm.norm(rec, sid)
            if not any(clean[k] for k in ('a', 'b', 'c', 'd', 'e', 'f')) and clean['off_axis'] != '有':
                bad.append((os.path.basename(f), f'{sid} 六轴全空且 off_axis≠有'))
                continue
            clean.update({'ok': True, 'model': tag, 'tag': tag,
                          'prompt_ver': VER, 'invalid': inv, 'source_file': os.path.basename(f)})
            buckets[tag][sid] = clean
            got += 1
        print(f'{os.path.basename(f):40s} → {tag}  {got} 条')

    allids = set()
    for tag, d in sorted(buckets.items()):
        p = os.path.join(OUT, f'结果_{tag}_{VER}.jsonl')
        with open(p, 'w', encoding='utf-8') as f:
            for sid, rec in d.items():
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        print(f'\n[{tag}] {len(d)} 条 → {os.path.basename(p)}')
        allids |= set(d)

    missing = sorted(valid_ids - allids)
    print(f'\n合计覆盖 {len(allids)}/{len(valid_ids)} 篇')
    if missing:
        print(f'还缺 {len(missing)} 篇：{", ".join(missing[:15])}{" …" if len(missing) > 15 else ""}')
    for tag, ids in dup.items():
        print(f'[{tag}] 重复出现（后写覆盖前写）：{sorted(set(ids))}')
    if bad:
        print(f'\n有 {len(bad)} 段没解析成有效记录：')
        for fn, why in bad[:10]:
            print(f'  {fn}: {why}')
    if allids:
        print('\n下一步：cd 06_工作流产物/第18轮_三模型全量编码_20261022')
        print(f'        PROMPT_VER={VER} python merge_and_kappa.py {" ".join(sorted(buckets))}')


if __name__ == '__main__':
    main()
