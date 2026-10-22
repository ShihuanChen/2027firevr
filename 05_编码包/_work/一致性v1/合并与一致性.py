# -*- coding: utf-8 -*-
"""三模型打标结果合并 + 一致性计算（v4 单条版：一条新闻一次调用，输出全部字段）

用法：
  1) 各家结果存成 结果_模型A.jsonl / _B / _C，一行一条：
     {"id":"E0080","p1":"记者旁观","p2":"受灾者","p3":"线性顺叙","p4":"逐句可重建","p5":["恐惧"],
      "d1":"有","d2":"有","d3":"有","d4":"无","d5":"有",
      "a":["A2"],"b":["B5"],"c":["C4","C6"],"d":["D3"],"e":["E1"],"f":["F2","F8"],
      "off_axis":"无","off_axis_note":"","evidence":[{"field":"c","quote":"..."}],"confidence":"high"}
     主键可用 id / 切片ID / 事件组ID 任一。
  2) python 合并与一致性.py
输出：
  合并结果.csv      每个事件每个字段的最终值 + 票型 + disputed 标记
  一致性.csv        每个字段的模型间一致性（Fleiss kappa 或 Cohen kappa）+ 漏填条数
  待人工抽检.csv    票型全异 / confidence=low / disputed=1 的格子
  off_axis汇总.csv  判「装不进任何取值」的条目与原文，设计空间是否穷尽的直接证据
"""
import json, glob, csv, itertools, collections, os

MODELS = ['A', 'B', 'C']
FIELDS = {
    'A': ['d1', 'd2', 'd3', 'd4', 'd5'],
    'B': ['a', 'b', 'c', 'd', 'e', 'f'],
    'C': ['p1', 'p2', 'p3', 'p4', 'p5'],
}
MULTI = {'a', 'b', 'c', 'd', 'e', 'f', 'p5'}   # 可多选字段，按集合比较


def norm(v):
    if v is None:
        return ('未报告',)
    if isinstance(v, list):
        return tuple(sorted(str(x) for x in v)) or ('未报告',)
    return (str(v),)


def fleiss(kappa_table):
    """kappa_table: list of list, 每个 item 的各类别计数"""
    n_items = len(kappa_table)
    if n_items == 0:
        return float('nan')
    n_raters = sum(kappa_table[0])
    if n_raters < 2:
        return float('nan')
    p_j = [sum(row[j] for row in kappa_table) / (n_items * n_raters)
           for j in range(len(kappa_table[0]))]
    P_i = [(sum(c * c for c in row) - n_raters) / (n_raters * (n_raters - 1)) for row in kappa_table]
    P_bar = sum(P_i) / n_items
    Pe = sum(p * p for p in p_j)
    return float('nan') if Pe == 1 else (P_bar - Pe) / (1 - Pe)


def cohen(a, b):
    labels = sorted(set(a) | set(b))
    n = len(a)
    if n == 0:
        return float('nan')
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return float('nan') if pe == 1 else (po - pe) / (1 - pe)


def load(model):
    """返回 {事件组ID: {字段: 值}}"""
    path = f'结果_模型{model}.jsonl'
    if not os.path.exists(path):
        return {}
    out = {}
    for line in open(path, encoding='utf-8'):
        if not line.strip():
            continue
        r = json.loads(line)
        rid = r.get('事件组ID') or r.get('id') or r.get('切片ID')
        if not rid:
            continue
        out.setdefault(str(rid), {}).update(r)
    return out


def main():
    data = {m: load(m) for m in MODELS}
    present = [m for m in MODELS if data[m]]
    if not present:
        print('没有找到 结果_模型*.jsonl')
        return
    ids = sorted(set().union(*[set(data[m]) for m in present]))

    merged, agree_rows, review_rows = [], [], []
    for group, fields in FIELDS.items():
        for f in fields:
            # 一致性
            seqs = []
            for m in present:
                seqs.append([norm(data[m].get(i, {}).get(f)) for i in ids])
            have = sum(1 for m in present for i in ids if f in data[m].get(i, {}))
            blank = sum(1 for m in present for i in ids if f not in data[m].get(i, {}))
            if have == 0:
                agree_rows.append(dict(字段=f, 组=group, 模型数=len(present), 方法='缺数据',
                                       kappa='', 完全一致条数=0, 总条数=len(ids), 漏填条数=blank))
                continue
            if len(present) == 3:
                vocab = sorted(set().union(*[set(s) for s in seqs]))
                table = [[s.count(v) for v in vocab] for s in zip(*seqs)]
                k = fleiss(table)
                meth = 'Fleiss'
            elif len(present) == 2:
                k = cohen(seqs[0], seqs[1])
                meth = 'Cohen'
            else:
                k, meth = float('nan'), '单模型'
            unanimous = all(len(set(t)) == 1 for t in zip(*seqs)) if len(present) > 1 else True
            agree_rows.append(dict(字段=f, 组=group, 模型数=len(present), 方法=meth,
                                   kappa=round(k, 3) if k == k else '',
                                   完全一致条数=sum(1 for t in zip(*seqs) if len(set(t)) == 1),
                                   总条数=len(ids), 漏填条数=blank))

            # 合并
            for i in ids:
                vals = [norm(data[m].get(i, {}).get(f)) for m in present]
                cnt = collections.Counter(vals)
                top, topn = cnt.most_common(1)[0]
                disputed = 1 if (len(cnt) > 1 and topn < len(present)) else 0
                low = any(str(data[m].get(i, {}).get('confidence', '')).lower() == 'low' for m in present)
                merged.append(dict(事件组ID=i, 组=group, 字段=f,
                                   最终值=' / '.join(top), 票型=topn / len(present),
                                   disputed=disputed, 低置信=1 if low else 0))
                if disputed or low or (len(cnt) == len(present) and len(present) > 1):
                    review_rows.append(dict(事件组ID=i, 组=group, 字段=f,
                                            各家=' | '.join(' / '.join(v) for v in vals),
                                            原因='全异' if len(cnt) == len(present) else ('分歧' if disputed else '低置信')))

    # off_axis 汇总（组 B 专用：设计空间是否穷尽的直接证据）
    off_rows = []
    for i in ids:
        flags = [m for m in present if str(data[m].get(i, {}).get('off_axis')) == '有']
        if flags:
            notes = [f'{m}: {data[m][i].get("off_axis_note", "")}' for m in flags]
            off_rows.append(dict(事件组ID=i, 命中模型数=len(flags), 命中模型='/'.join(flags),
                                 说明=' | '.join(notes)[:600]))
    with open('off_axis汇总.csv', 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['事件组ID', '命中模型数', '命中模型', '说明'])
        w.writeheader()
        w.writerows(off_rows)

    with open('合并结果.csv', 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(merged[0].keys()))
        w.writeheader()
        w.writerows(merged)
    with open('一致性.csv', 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(agree_rows[0].keys()))
        w.writeheader()
        w.writerows(agree_rows)
    with open('待人工抽检.csv', 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(review_rows[0].keys()) if review_rows else ['事件组ID', '组', '字段', '各家', '原因'])
        w.writeheader()
        w.writerows(review_rows)

    print(f'事件 {len(ids)} 条，模型 {len(present)} 个')
    for r in agree_rows:
        print(f"  {r['字段']:<4} {r['组']} {r['方法']:<7} kappa={r['kappa']}  一致 {r['完全一致条数']}/{r['总条数']}  漏填 {r['漏填条数']}")
    bad = [r['字段'] for r in agree_rows if r['漏填条数']]
    if bad:
        print(f'⚠ 有漏填字段：{bad} —— 视为「未报告」参与计算，但需回查模型是否跑完 60 条')
    print(f'待人工抽检 {len(review_rows)} 格')
    print(f'off_axis 命中 {len(off_rows)}/{len(ids)} 条 = {len(off_rows)/max(len(ids),1):.1%}'
          f'（门槛 ≤15%；>15% 说明轴不穷尽，v2.4 应加档）')


if __name__ == '__main__':
    main()
