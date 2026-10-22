# -*- coding: utf-8 -*-
"""从作废结果恢复切片 ID

作废原因：run_models.py 的 norm() 漏了 out['id']，108+72+26 条结果没有主键。
恢复办法：模型返回的 evidence.quote 是正文逐字摘录，用最长 quote 在 106 篇正文里做
唯一子串匹配，命中即确定该条属于哪个切片。命中不唯一或零命中则放弃。

输出：_out/结果_{tag}_修复.jsonl
"""
import os, json, csv, sys, re
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OLD = os.path.join(HERE, '_out_作废_无id字段')
NEW = os.path.join(HERE, '_out')
INP = os.path.join(REPO, '05_编码包', '输入包_编码集v4.csv')
os.makedirs(NEW, exist_ok=True)

rows = list(csv.DictReader(open(INP, encoding='utf-8-sig')))
texts = {r['切片ID']: re.sub(r'\s+', ' ', r['正文']) for r in rows}


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def locate(rec):
    quotes = [norm(e.get('quote', '')) for e in (rec.get('evidence') or []) if e.get('quote')]
    # 取三个最长的 quote，长的更容易唯一命中
    quotes = sorted({q for q in quotes if len(q) >= 12}, key=len, reverse=True)[:4]
    for q in quotes:
        hits = [sid for sid, t in texts.items() if q in t]
        if len(hits) == 1:
            return hits[0], q
    # 退一步：用 off_axis_note 或 raw 里的特征串匹配
    return None, None


def main():
    total = ok = 0
    for tag in ('opus', 'sonnet', 'haiku'):
        src = os.path.join(OLD, f'结果_{tag}.jsonl')
        if not os.path.exists(src):
            continue
        out, stat, seen = [], {'unique': 0, 'fail': 0}, {}
        for line in open(src, encoding='utf-8'):
            o = json.loads(line)
            if not o.get('ok'):
                continue
            total += 1
            sid, q = locate(o)
            if not sid:
                stat['fail'] += 1
                continue
            if sid in seen:
                # 同一条被重复恢复，保留 evidence 更长的那份
                if len(json.dumps(o.get('evidence', []))) <= len(json.dumps(seen[sid].get('evidence', []))):
                    continue
            o['id'] = sid
            o['recovered_by'] = q[:40]
            seen[sid] = o
            stat['unique'] += 1
        with open(os.path.join(NEW, f'结果_{tag}.jsonl'), 'w', encoding='utf-8') as f:
            for o in seen.values():
                f.write(json.dumps(o, ensure_ascii=False) + '\n')
        ok += len(seen)
        print(f'[{tag}] 原 {stat["unique"] + stat["fail"]} 条，唯一定位 {stat["unique"]}，'
              f'失败 {stat["fail"]}，去重后 {len(seen)}')
    print(f'合计 {total} 条，恢复 {ok}')


if __name__ == '__main__':
    main()
