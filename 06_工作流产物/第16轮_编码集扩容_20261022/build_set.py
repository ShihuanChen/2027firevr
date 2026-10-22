# -*- coding: utf-8 -*-
"""编码集 v4 装配：按上限口径（60–70 事件 / 100–120 切片）重排编码集，并生成打标输入包。

入集规则（按优先级）：
  1 保留现有 51 个入集事件中有正文的
  2 新增本地事件：可重建 T1/T2 + 过程类细节 ≥3 + 不与该事件簇重复
  3 新增外部事件：目标缺口命中（F5/F6/D4/E4/E3/E5/F8）且过程类 ≥3
切片规则：每事件取 1–2 条，按（过程类命中数, 字数）排序；第二条要求过程类 ≥3 且字数 ≥800
"""
import os, sys, json, csv, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\Administrator\WorkBuddy\2026-10-22-12-32-14'
HERE = os.path.dirname(os.path.abspath(__file__))
OUTPKG = os.path.join(ROOT, 'repo', '05_编码包')

LOCAL_ADD = ['E0724', 'E0192', 'E0077', 'E0009', 'E0097', 'E0117', 'E0197', 'E0541', 'E0503',
             'E0046', 'E0127', 'E0766', 'E0106', 'E0801', 'E0148', 'E0021', 'E0020',
             'E0013', 'E0022', 'E0150', 'E0155']
DROP = {'S16', 'S21', 'S28', 'S36'}   # 原文抓不到或抓到的是别的事件，退出编码集
MAX_SLICE = 120


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, '_work', '事件正文清单.csv'), encoding='utf-8-sig')))
    ev = json.load(open(os.path.join(ROOT, '_tmp', 'r2', 'unified3.json'), encoding='utf-8'))
    meta = {x['事件组ID']: x for x in ev}

    # S 系列补抓正文
    cache_path = os.path.join(HERE, '_work', '正文缓存.json')
    cache = json.load(open(cache_path, encoding='utf-8')) if os.path.exists(cache_path) else {}
    have = defaultdict(list)
    for r in rows:
        have[r['事件组ID']].append(r)
    for eid, c in cache.items():
        if c.get('正文') and not any(x['出处'].startswith('URL') and x['字数'] and int(x['字数']) >= 600 for x in have.get(eid, [])):
            have[eid] = [dict(事件组ID=eid, 序=1, 可选篇数=1, key=eid, 出处='URL补抓', 标题=c['标题'],
                              字数=str(len(c['正文'])), 过程类数='0', 命中='', 通稿='',
                              正文=c['正文'], URL=c.get('url', ''), 处置=meta.get(eid, {}).get('处置', '入编码集'),
                              来源=meta.get(eid, {}).get('来源', '补搜新增'))]

    # 外部新增
    ext_path = os.path.join(HERE, '_work', '外部新增.json')
    ext = json.load(open(ext_path, encoding='utf-8')) if os.path.exists(ext_path) else []
    for i, x in enumerate(ext, 1):
        have[x['id']].append(dict(事件组ID=x['id'], 序=1, 可选篇数=1, key=x['id'], 出处='外部补搜',
                                  标题=x['标题'], 字数=str(len(x['正文'])), 过程类数=str(x.get('过程类数', 3)),
                                  命中=x.get('命中', ''), 通稿='', 正文=x['正文'], URL=x.get('URL', ''),
                                  处置='入编码集', 来源='补搜新增'))

    keep, drop = [], []
    for eid, v in have.items():
        st = meta.get(eid, {}).get('处置', '')
        if eid in LOCAL_ADD or eid[:1] in ('X','Y'):
            st = '入编码集'
        if st != '入编码集' or eid in DROP:
            continue
        v = [x for x in v if int(x['字数']) >= 500]
        if not v:
            drop.append((eid, '无可用正文'))
            continue
        v.sort(key=lambda x: (-int(x['过程类数']), -int(x['字数'])))
        keep.append((eid, v))

    # 切片：先事件排序（过程类多、字数长优先）
    keep.sort(key=lambda kv: (-int(kv[1][0]['过程类数']), -int(kv[1][0]['字数']), kv[0]))
    slices = []
    for eid, v in keep:
        slices.append((eid, v[0]))
    # 第二轮补第二条，直到上限
    for eid, v in keep:
        if len(slices) >= MAX_SLICE:
            break
        if len(v) < 2:
            continue
        s2 = v[1]
        if int(s2['过程类数']) >= 3 and int(s2['字数']) >= 800 and s2['标题'] != v[0]['标题']:
            slices.append((eid, s2))

    # 输出
    slices.sort(key=lambda x: (x[0], x[1]['序']))
    cnt = defaultdict(int)
    in_pkg = []
    for eid, s in slices:
        cnt[eid] += 1
        in_pkg.append(dict(切片ID=f'{eid}-{cnt[eid]}', 事件组ID=eid, 标题=s['标题'], 正文=s['正文'][:2000],
                           字数=str(len(s['正文'][:2000])), 过程类数=s['过程类数'], 命中=s['命中'], 出处=s['出处'],
                           URL=s['URL']))
    with open(os.path.join(OUTPKG, '输入包_编码集v4.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['切片ID', '事件组ID', '标题', '正文', '字数', '过程类数', '命中', '出处', 'URL'])
        w.writeheader(); w.writerows(in_pkg)

    evrows = []
    for eid, v in sorted(keep, key=lambda kv: kv[0]):
        m = meta.get(eid, {})
        pc = int(v[0]['过程类数'])
        lv = m.get('层级', '') or ''
        if not lv:
            blob = (v[0]['标题'] or '') + (v[0]['正文'][:600] if v[0].get('正文') else '')
            lv = 'B_高层词无层数' if re.search(r'high-?rise|tower|skyscraper|高层|层住宅|floors|樓|楼层', blob, re.I) else 'D_无层数'
        qg = m.get('质量等级', '') or ('A' if pc >= 7 else 'B' if pc >= 5 else 'C' if pc >= 3 else 'D')
        evrows.append(dict(事件组ID=eid, 标题=v[0]['标题'], 切片数=cnt.get(eid, 0),
                           最佳过程类数=v[0]['过程类数'], 质量分层=('主分析' if pc >= 3 else '补充'),
                           命中=v[0]['命中'][:80], 层级=lv, 质量等级=qg,
                           代表gid=m.get('代表gid', ''),
                           来源=m.get('来源', '补搜新增'), 相对上版=('新增' if eid in LOCAL_ADD or eid[:1] in ('X','Y') else m.get('相对上版', '')),
                           真实事件簇=m.get('簇', ''), 处置理由=('外部补搜·缺口命中' if eid[:1] in ('X','Y') else '')))
    with open(os.path.join(OUTPKG, '编码集v4_事件.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(evrows[0].keys()))
        w.writeheader(); w.writerows(evrows)

    print(f'事件 {len(keep)}，切片 {len(in_pkg)}')
    print('丢弃（无正文）', drop)
    print('每事件切片数分布', sorted({k: v for k, v in cnt.items()}.values())[:5], '…')
    print('单切片事件', sum(1 for k in cnt if cnt[k] == 1), '双切片事件', sum(1 for k in cnt if cnt[k] == 2),
          '三切片以上', sum(1 for k in cnt if cnt[k] > 2))


if __name__ == '__main__':
    main()
