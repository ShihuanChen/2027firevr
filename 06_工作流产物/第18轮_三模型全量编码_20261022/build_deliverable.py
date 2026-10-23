# -*- coding: utf-8 -*-
"""把三家（或任意已跑到的）模型结果合并成一张可直接打开核对的交付表。

规则（与 merge_and_kappa.py 完全一致，公共实现见 merge_lib.py）：
  单选字段：多数票，平票按编码者顺序 A→B→C
  多选轴：真多数票（≥2 名编码者选中才计入），首位代表主档，
          排序按票数降序→首位票降序→档名；无任何档达 2 票时留空
  冲突标记：可用模型之间出现过不一致的值即置 1
  没跑到的切片也保留一行，标「未编码」，不用空行冒充

输出：00_核心交付/16_编码结果_106篇_合并交付版.csv
"""
import os, sys, csv, json, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merge_lib

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT_DIR = os.environ.get('OUT_DIR') or os.path.join(HERE, '_out')
VER = os.environ.get('PROMPT_VER', 'v4.1')
DST = os.environ.get('DST') or os.path.join(
    REPO, '00_核心交付', '16_编码结果_106篇_合并交付版.csv')


def _find_inp():
    """定位输入包 CSV：仓库内是 05_编码包/，交接包内是 02_编码包/，两者都支持。"""
    cands = [
        os.environ.get('INP_CSV'),
        os.path.join(REPO, '05_编码包', '输入包_编码集v4.csv'),
        os.path.join(HERE, '..', '02_编码包', '输入包_编码集v4.csv'),
        os.path.join(HERE, '..', '..', '02_编码包', '输入包_编码集v4.csv'),
    ]
    for c in cands:
        if c and os.path.exists(c):
            return os.path.abspath(c)
    raise FileNotFoundError(
        '找不到 输入包_编码集v4.csv；已尝试：' + ' | '.join(str(c) for c in cands))


INP = _find_inp()

TAGS = [t for t in (os.environ.get('TAGS') or 'opus,sonnet,haiku').split(',') if t]
SINGLE = ['p1', 'p2', 'p3', 'p4', 'd1', 'd1b', 'd2', 'd3', 'd4', 'd5',
          'off_axis', 'confidence']
MULTI = ['p5', 'a', 'b', 'c', 'd', 'e', 'f']


def load(tag):
    p = os.path.join(OUT_DIR, f'结果_{tag}_{VER}.jsonl')
    if not os.path.exists(p):
        p = os.path.join(OUT_DIR, f'结果_{tag}.jsonl')
    d = {}
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get('ok') and o.get('id'):
                d[o['id']] = o       # 同 id 后写覆盖前写
    return d


def main():
    data = {t: load(t) for t in TAGS}
    print('载入', {t: len(v) for t, v in data.items()})
    rows = list(csv.DictReader(open(INP, encoding='utf-8-sig')))
    out = []
    stat = collections.Counter()
    for r in rows:
        sid = r['切片ID']
        have = [t for t in TAGS if sid in data[t]]
        rec = {'切片ID': sid, '事件组ID': r['事件组ID'], '标题': r['标题'],
               '来源': r.get('出处', ''), '字数': r.get('字数', ''), '已编模型数': len(have),
               '已编模型': '+'.join(have) if have else '未编码'}
        conflict = 0
        for f in SINGLE:
            vals = [data[t][sid].get(f) for t in have]
            rec[f] = merge_lib.merge_single(vals, order=have)
            rec[f + '_票型'] = '|'.join(str(v) for v in vals)
            if len({str(v) for v in vals if v not in (None, '')}) > 1:
                conflict += 1
        no_maj_axes = 0
        for f in MULTI:
            sets = [list(data[t][sid].get(f) or []) for t in have]
            vals, no_maj = merge_lib.merge_axis_cell(sets)
            rec[f] = vals
            rec[f + '_票型'] = '|'.join(';'.join(s) for s in sets)
            no_maj_axes += int(no_maj)
            if len({tuple(sorted(s)) for s in sets}) > 1:
                conflict += 1
        rec['无多数票轴数'] = no_maj_axes
        rec['冲突字段数'] = conflict
        out.append(rec)
        stat['已编码' if have else '未编码'] += 1
        stat['双模型' if len(have) >= 2 else ('单模型' if have else '无')] += 1
        stat['有冲突' if conflict else '无冲突'] += 1

    cols = (['切片ID', '事件组ID', '标题', '来源', '字数', '已编模型数', '已编模型']
            + [x for f in SINGLE for x in (f, f + '_票型')]
            + [x for f in MULTI for x in (f, f + '_票型')]
            + ['无多数票轴数', '冲突字段数'])
    with open(DST, 'w', newline='', encoding='utf-8-sig') as fp:
        w = csv.DictWriter(fp, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    print(dict(stat))
    print('写出', DST, len(out), '行', len(cols), '列')


if __name__ == '__main__':
    main()
