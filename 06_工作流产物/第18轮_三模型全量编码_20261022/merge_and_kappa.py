# -*- coding: utf-8 -*-
"""三模型一致性汇总：Fleiss' κ + 逐档 PABAK + 簇级 bootstrap CI

输入：_out/结果_{opus,sonnet,haiku}.jsonl（run_models.py 产出）
      ../../05_编码包/输入包_编码集v4.csv（切片ID → 事件组ID）
输出：一致性_逐字段.csv / 一致性_逐档.csv / 合并结果.csv / 报告.md

三个口径同时给，缺一不可：
  κ        多编码者一致性（三模型用 Fleiss' κ）
  PABAK     2Po−1，解决极端边际下的假性归零
  簇级 CI   bootstrap 重采样单位是事件，不是切片
"""
import os, sys, json, csv, random, collections, math

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, '_out')
INP = os.path.join(REPO, '05_编码包', '输入包_编码集v4.csv')
RES = os.path.join(HERE, '结果')

TAGS = ['opus', 'sonnet', 'haiku']
AXES = {'a': ['A1', 'A2', 'A3', 'A4', 'A5'],
        'b': ['B1', 'B2', 'B3', 'B4', 'B5'],
        'c': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
        'd': ['D1', 'D2', 'D3', 'D4', 'D5'],
        'e': ['E1', 'E2', 'E3', 'E4', 'E5'],
        'f': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8']}
MULTI = list(AXES) + ['p5']
SINGLE = ['p1', 'p2', 'p3', 'p4', 'd1', 'd1b', 'd2', 'd3', 'd4', 'd5']
VER = os.environ.get('PROMPT_VER', 'v4.2')   # v4.1 的 78 条不与之混算
random.seed(20261022)


def load():
    data = {}
    for t in TAGS:
        p = os.path.join(OUT, f'结果_{t}_{VER}.jsonl')
        if not os.path.exists(p):
            p2 = os.path.join(OUT, f'结果_{t}.jsonl')   # 回退：v4.1 旧文件
            p = p2 if os.path.exists(p2) else p
        if not os.path.exists(p):
            continue
        latest = {}
        for line in open(p, encoding='utf-8'):
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get('ok') and o.get('id'):
                latest[o['id']] = o          # 同 id 后写覆盖前写
        data[t] = latest
        print(f'  载入 {t}: {len(latest)} 条 ({os.path.basename(p)})')
    return data


def fleiss(rows, k):
    """rows: list of count vectors (每 item 各类别计数), k=raters"""
    n = len(rows)
    if n == 0:
        return float('nan')
    pj = [sum(r[j] for r in rows) / (n * k) for j in range(len(rows[0]))]
    Pi = [(sum(c * c for c in r) - k) / (k * (k - 1)) for r in rows]
    Pbar = sum(Pi) / n
    Pe = sum(p * p for p in pj)
    return float('nan') if abs(1 - Pe) < 1e-12 else (Pbar - Pe) / (1 - Pe)


def pabak_binary(votes):
    """votes: list of 0/1，返回 PABAK = 2Po-1（三 rater 用平均两两一致）"""
    n = len(votes)
    if n < 2:
        return float('nan')
    pairs = tot = 0
    agree = 0
    for i in range(n):
        for j in range(i + 1, n):
            tot += 1
            if votes[i] == votes[j]:
                agree += 1
    return 2 * (agree / tot) - 1 if tot else float('nan')


def cohen(a, b):
    """二分类 Cohen κ"""
    n = len(a)
    if n == 0:
        return float('nan')
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa1, pb1 = sum(a) / n, sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return float('nan') if abs(1 - pe) < 1e-12 else (po - pe) / (1 - pe)


def boot_ci(units, fn, B=1000):
    vals = []
    n = len(units)
    if n < 3:
        return (float('nan'), float('nan'))
    for _ in range(B):
        s = [units[random.randrange(n)] for _ in range(n)]
        v = fn(s)
        if not math.isnan(v):
            vals.append(v)
    if len(vals) < 50:
        return (float('nan'), float('nan'))
    vals.sort()
    return (vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1])


def main():
    data = load()
    want = [a for a in sys.argv[1:] if a in TAGS]
    tags = want if want else [t for t in TAGS if t in data]
    print('可用模型', {t: len(data[t]) for t in tags})
    common = set.intersection(*[set(data[t]) for t in tags]) if tags else set()
    ids = sorted(common)
    print('三模型共有', len(ids))

    ev = {r['切片ID']: r['事件组ID'] for r in
          csv.DictReader(open(INP, encoding='utf-8-sig'))}

    # ---------- 逐字段 ----------
    field_rows = []
    for f in SINGLE:
        cats = sorted({str(data[t][i].get(f)) for t in tags for i in ids})
        idx = {c: j for j, c in enumerate(cats)}
        per = []
        for i in ids:
            cnt = [0] * len(cats)
            for t in tags:
                cnt[idx[str(data[t][i].get(f))]] += 1
            per.append(cnt)
        k = fleiss(per, len(tags))
        po = sum(sum(c * c for c in r) - len(tags) for r in per) / (len(per) * len(tags) * (len(tags) - 1))
        # 全样本只有一个类别时 κ 无定义（Pe=1），报 nan 会误导，标成"单一取值"并单列
        if k != k:
            field_rows.append({'字段': f, '类别数': len(cats), 'Fleiss_kappa': 'n/a',
                               '一致率': round(po, 3), '主类别': cats[0],
                               '主类别占比': round(sum(r[0] for r in per) / (len(per) * len(tags)), 3)})
            continue
        main = max(range(len(cats)), key=lambda j: sum(r[j] for r in per))
        field_rows.append({'字段': f, '类别数': len(cats), 'Fleiss_kappa': round(k, 3),
                           '一致率': round(po, 3), '主类别': cats[main],
                           '主类别占比': round(sum(r[main] for r in per) / (len(per) * len(tags)), 3)})

    # ---------- 逐档（多选）----------
    def binary_vectors(f, code):
        """返回 {id: [v_t1, v_t2, v_t3]}，1=该模型标了这档"""
        return {i: [1 if code in (data[t][i].get(f) or []) else 0 for t in tags] for i in ids}

    tier_rows = []
    for f, codes in AXES.items():
        for code in codes:
            bv = binary_vectors(f, code)
            units = [(ev.get(i, i), bv[i]) for i in ids]
            # 三 rater 的 κ 用 Fleiss 二分类
            per = []
            for i in ids:
                c1 = sum(bv[i]); cnt = [len(tags) - c1, c1]
                per.append(cnt)
            if len(tags) == 2:
                k = cohen([bv[i][0] for i in ids], [bv[i][1] for i in ids])
            else:
                k = fleiss(per, len(tags))
            # PABAK：平均两两一致
            ag, tot = 0, 0
            for i in ids:
                for x in range(len(tags)):
                    for y in range(x + 1, len(tags)):
                        tot += 1
                        ag += (bv[i][x] == bv[i][y])
            po = ag / tot if tot else float('nan')
            pab = 2 * po - 1 if tot else float('nan')
            # 簇级 bootstrap：重采样事件
            def fn(sample, f=f, code=code):
                ag2 = tot2 = 0
                for evid, v in sample:
                    for x in range(len(tags)):
                        for y in range(x + 1, len(tags)):
                            tot2 += 1
                            ag2 += (v[x] == v[y])
                return 2 * (ag2 / tot2) - 1 if tot2 else float('nan')
            lo, hi = boot_ci(units, fn, B=500)
            tier_rows.append({'轴': f, '档': code, '命中篇数': sum(1 for i in ids if any(bv[i])),
                              'Fleiss_kappa': round(k, 3), 'PABAK': round(pab, 3),
                              'PABAK_CI_low': round(lo, 3), 'PABAK_CI_high': round(hi, 3)})

    # ---------- 轴级 ----------
    axis_rows = []
    for f in AXES:
        sub = [r for r in tier_rows if r['轴'] == f]
        kv = [r['Fleiss_kappa'] for r in sub if not (isinstance(r['Fleiss_kappa'], float) and math.isnan(r['Fleiss_kappa']))]
        axis_rows.append({'轴': f,
                          '档均_kappa': round(sum(kv) / len(kv), 3) if kv else float('nan'),
                          '档均_PABAK': round(sum(r['PABAK'] for r in sub) / len(sub), 3)})

    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, '一致性_逐字段.csv'), 'w', newline='', encoding='utf-8-sig') as fp:
        w = csv.DictWriter(fp, fieldnames=list(field_rows[0]))
        w.writeheader(); w.writerows(field_rows)
    with open(os.path.join(RES, '一致性_逐档.csv'), 'w', newline='', encoding='utf-8-sig') as fp:
        w = csv.DictWriter(fp, fieldnames=list(tier_rows[0]))
        w.writeheader(); w.writerows(tier_rows)
    with open(os.path.join(RES, '一致性_轴级.csv'), 'w', newline='', encoding='utf-8-sig') as fp:
        w = csv.DictWriter(fp, fieldnames=list(axis_rows[0]))
        w.writeheader(); w.writerows(axis_rows)

    # ---------- 合并（多数票）----------
    merged = []
    for i in ids:
        row = {'切片ID': i, '事件组ID': ev.get(i, '')}
        for f in SINGLE:
            vs = [str(data[t][i].get(f)) for t in tags]
            row[f] = collections.Counter(vs).most_common(1)[0][0]
            row[f + '_票型'] = '|'.join(vs)
        for f in AXES:
            sets = [set(data[t][i].get(f) or []) for t in tags]
            row[f] = ';'.join(sorted(set.union(*sets) & set.intersection(*sets) or set.union(*sets)))
            row[f + '_并集型'] = '|'.join(';'.join(sorted(s)) for s in sets)
        offv = [data[t][i].get('off_axis') for t in tags]
        row['off_axis'] = collections.Counter(offv).most_common(1)[0][0]
        merged.append(row)
    with open(os.path.join(RES, '合并结果.csv'), 'w', newline='', encoding='utf-8-sig') as fp:
        w = csv.DictWriter(fp, fieldnames=list(merged[0]))
        w.writeheader(); w.writerows(merged)

    # ---------- 报告 ----------
    lines = ['# 三模型一致性（106 篇）', '',
             f'模型：{", ".join(tags)}；共有条目 {len(ids)}；重采样单位=事件簇', '',
             '## 轴级', '', '| 轴 | 档均 κ | 档均 PABAK |', '|---|---|---|']
    for r in axis_rows:
        lines.append(f"| {r['轴']} | {r['档均_kappa']} | {r['档均_PABAK']} |")
    lines += ['', '## 逐字段', '', '| 字段 | Fleiss κ | 一致率 | 主类别 | 主类别占比 |', '|---|---|---|---|---|']
    for r in field_rows:
        lines.append(f"| {r['字段']} | {r['Fleiss_kappa']} | {r['一致率']} | {r['主类别']} | {r['主类别占比']} |")
    lines += ['', '## 逐档（按 PABAK 升序，前 10）', '',
              '| 轴 | 档 | 命中 | κ | PABAK | 95% CI |', '|---|---|---|---|---|---|']
    for r in sorted(tier_rows, key=lambda x: x['PABAK'])[:10]:
        lines.append(f"| {r['轴']} | {r['档']} | {r['命中篇数']} | {r['Fleiss_kappa']} | "
                     f"{r['PABAK']} | [{r['PABAK_CI_low']}, {r['PABAK_CI_high']}] |")
    open(os.path.join(RES, '报告.md'), 'w', encoding='utf-8').write('\n'.join(lines))
    print('\n'.join(lines[:30]))
    print('\n输出目录', RES)


if __name__ == '__main__':
    main()
