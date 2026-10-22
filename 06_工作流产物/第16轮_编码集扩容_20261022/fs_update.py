# -*- coding: utf-8 -*-
"""把编码集 v4 写回飞书：02_编码集 对齐（更新/新建/删除），01_事件库总表 打标（新增/剔除）。

用法：python fs_update.py --dry   只打印将要发生的变化
      python fs_update.py         实际写入
"""
import os, sys, json, csv, subprocess, collections
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r'C:\Users\Administrator\WorkBuddy\2026-10-22-12-32-14'
LARK = r'C:\Users\Administrator\.workbuddy\binaries\node\cli-connector-packages\lark-cli.cmd'
BASE = 'MBmvbhTH1aYGRzsmFYpcbuU3n6f'
T_COD = 'tblPUwolf7lTuRQO'
T_LIB = 'tblYb5NBvziWJJ69'
DRY = '--dry' in sys.argv


def jf(obj, name='_work/payload.json'):
    fp = os.path.join(HERE, name)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    json.dump(obj, open(fp, 'w', encoding='utf-8'), ensure_ascii=False)
    return '@' + fp


def run(args, check=True):
    r = subprocess.run([LARK] + args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if check and not r.stdout.strip():
        print('EMPTY', args[:4], r.stderr[:300]); return {'ok': False}
    try:
        return json.loads(r.stdout)
    except Exception:
        print('NONJSON', args[:4], r.stdout[:300]); return {'ok': False}


def list_records(table):
    out = run(['base', '+record-list', '--base-token', BASE, '--table-id', table,
               '--format', 'json', '--limit', '200', '--offset', str(off)]) if False else None
    recs, off = [], 0
    while True:
        d = run(['base', '+record-list', '--base-token', BASE, '--table-id', table,
                 '--format', 'json', '--limit', '200', '--offset', str(off)])
        if not d.get('ok'):
            break
        dd = d['data']
        fields = dd['fields']
        for rid, row in zip(dd['record_id_list'], dd['data']):
            recs.append((rid, dict(zip(fields, row))))
        if not dd.get('has_more'):
            break
        off += 200
    return recs


def main():
    ev = list(csv.DictReader(open(os.path.join(ROOT, 'repo', '05_编码包', '编码集v4_事件.csv'), encoding='utf-8-sig')))
    ext = {}
    for x in json.load(open(os.path.join(HERE, '_work', '外部新增.json'), encoding='utf-8')):
        ext.setdefault(x['id'], x)
    new_ids = {r['事件组ID'] for r in ev}

    # ---- 02 编码集 ----
    cur = list_records(T_COD)
    cur_map = {str(v.get('事件组ID')): rid for rid, v in cur}
    print(f'02 现有 {len(cur)} 条；目标 {len(ev)} 条')

    def rec_of(r):
        eid = r['事件组ID']
        d = dict(事件组ID=eid, 标题=r['标题'], 真实事件簇=r['真实事件簇'], 来源=[r['来源']],
                 相对上版=[r['相对上版']], 过程类细节=int(r['最佳过程类数']), 命中细节=r['命中'],
                 备注=f"质量分层:{r['质量分层']}｜切片{r['切片数']}")
        if r['代表gid']:
            d['代表gid'] = int(r['代表gid'])
        if r['质量等级']:
            d['质量等级'] = [r['质量等级']]
        lv = r['层级']
        if lv.startswith('A_'):
            d['层级'] = ['A_明确7层以上']
        elif lv.startswith('B_'):
            d['层级'] = ['B_高层词无层数']
        elif lv.startswith('C_'):
            d['层级'] = ['C_低层查漏']
        if eid in ext:
            d['备注'] += f"｜缺口:{ext[eid]['目标']}｜{ext[eid].get('备注', '')}"
        return d

    to_update = [(cur_map[r['事件组ID']], rec_of(r)) for r in ev if r['事件组ID'] in cur_map]
    to_create = [rec_of(r) for r in ev if r['事件组ID'] not in cur_map]
    to_delete = [rid for eid, rid in cur_map.items() if eid not in new_ids]
    print(f'  更新 {len(to_update)}，新建 {len(to_create)}，删除 {len(to_delete)}')

    if not DRY:
        for i in range(0, len(to_update), 100):
            chunk = to_update[i:i + 100]
            d = run(['base', '+record-batch-update', '--base-token', BASE, '--table-id', T_COD,
                     '--json', jf({'update_records': [{'record_id': rid, 'fields': f} for rid, f in chunk]})])
            print('   update', i, d.get('ok'))
        for i in range(0, len(to_create), 100):
            chunk = to_create[i:i + 100]
            d = run(['base', '+record-batch-create', '--base-token', BASE, '--table-id', T_COD,
                     '--json', jf({'create_records': chunk})])
            print('   create', i, d.get('ok'))
        if to_delete:
            d = run(['base', '+record-delete', '--base-token', BASE, '--table-id', T_COD, '--yes',
                     '--json', jf({'record_id_list': to_delete})])
            print('   delete', d.get('ok'), len(to_delete))

    # ---- 01 总表 ----
    lib = list_records(T_LIB)
    lib_map = {str(v.get('事件组ID')): rid for rid, v in lib}
    print(f'01 现有 {len(lib)} 条')
    LOCAL_ADD = ['E0724', 'E0192', 'E0077', 'E0009', 'E0097', 'E0117', 'E0197', 'E0541', 'E0503',
                 'E0046', 'E0127', 'E0766', 'E0106', 'E0801', 'E0148', 'E0021', 'E0020',
                 'E0013', 'E0022', 'E0150', 'E0155']
    DROP = {'S16', 'S21', 'S28', 'S36'}
    ups = []
    for eid in LOCAL_ADD:
        if eid in lib_map:
            ups.append({'record_id': lib_map[eid], 'fields': {'处置': ['入编码集'], '相对上版': ['新增'],
                                                              '处置理由': '本轮补充：过程细节≥3，细节密度达标'}})
    for eid in DROP:
        if eid in lib_map:
            ups.append({'record_id': lib_map[eid], 'fields': {'处置': ['剔除'], '相对上版': ['删除'],
                                                              '处置理由': '原文多次抓取失败或抓到的是别的事件，无可用正文'}})
    lib_ids = {str(v.get('事件组ID')) for rid, v in lib}
    creates = []
    for eid, x in ext.items():
        if eid in lib_ids:
            continue
        creates.append(dict(事件组ID=eid, 事件名=x['标题'], 处置=['入编码集'], 相对上版=['新增'],
                            来源=['补搜新增'], 篇数=1, 过程类细节=x['过程类数'], 命中细节=x['命中'],
                            URL=x['URL'], 处置理由=f"外部定向补搜·缺口{x['目标']}：{x.get('备注', '')}"))
    print(f'  01 更新 {len(ups)}，新建 {len(creates)}')
    if not DRY:
        if ups:
            d = run(['base', '+record-batch-update', '--base-token', BASE, '--table-id', T_LIB,
                     '--json', jf({'update_records': ups})])
            print('   lib update', d.get('ok'))
        if creates:
            d = run(['base', '+record-batch-create', '--base-token', BASE, '--table-id', T_LIB,
                     '--json', jf({'create_records': creates})])
            print('   lib create', d.get('ok'), len(creates))
    else:
        print('   [dry] 更新样例', ups[:2])
        print('   [dry] 新建样例', creates[:2])


if __name__ == '__main__':
    main()
