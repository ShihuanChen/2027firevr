# -*- coding: utf-8 -*-
"""离线自测：不碰任何外部 API，验证 v4.2 跑批与合并链路是否真的能跑。

做法：起一个本地 HTTP 桩，同时实现 /messages 与 /chat/completions，
喂 3 条真语料、3 个假模型、3 种预设回答（含故意构造的脏输出），然后：
  1. 检查落盘文件名是否带 v4.2、prompt_ver 是否写入
  2. 检查硬校验：d1=「无」时 d1b 必须被强制回「未报告」；off_axis=有 但说不出类必须改「无」
  3. 检查断点续跑：第二次跑不应重复调用
  4. 检查 merge_and_kappa 能读新文件并算出 κ（d1b 有变异时应给出数值，不应是 nan）
  5. 检查两种出口协议都通

用法：python _selftest.py
"""
import json, os, sys, csv, shutil, subprocess, threading, tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding='utf-8')

# 三种预设回答，轮转分配，保证有变异可算 κ
ANS = [
    {"p1": "记者旁观", "p2": "受灾者", "p3": "线性顺叙", "p4": "逐句可重建", "p5": ["恐惧"],
     "d1": "线索驱动", "d1b": "无", "d2": "有", "d3": "无", "d4": "无", "d5": "无",
     "a": ["A2"], "b": ["B1"], "c": ["C1"], "d": ["D1"], "e": ["E1"], "f": ["F1"],
     "off_axis": "无", "off_axis_note": "", "evidence": [{"field": "a", "quote": "smoke"}],
     "confidence": "high"},
    # 故意脏：d1=无 却给了 d1b=有，d1b 应被强制回「未报告」
    {"p1": "记者旁观", "p2": "混合", "p3": "倒叙", "p4": "段落级概括", "p5": ["无助"],
     "d1": "无", "d1b": "有", "d2": "无", "d3": "未报告", "d4": "未报告", "d5": "未报告",
     "a": ["A1"], "b": ["B2"], "c": ["C4"], "d": ["D3"], "e": ["E2"], "f": ["F2"],
     "off_axis": "无", "off_axis_note": "", "evidence": [], "confidence": "low"},
    # 故意脏：off_axis=有 但 note 说不出五类，应被强制改「无」→ 六轴全空 → 判 axis-empty 失败
    {"p1": "官方通稿", "p2": "管理者", "p3": "多线并置", "p4": "只有结论", "p5": [],
     "d1": "未报告", "d1b": "未报告", "d2": "未报告", "d3": "未报告", "d4": "未报告", "d5": "未报告",
     "a": [], "b": [], "c": [], "d": [], "e": [], "f": [],
     "off_axis": "有", "off_axis_note": "就是写不进去", "evidence": [], "confidence": "low"},
]
CALLS = {"n": 0}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(n) or b'{}')
        CALLS["n"] += 1
        # 按正文里的切片 ID 决定用哪条预设，保证同一 id 在同一模型下稳定
        txt = body.get('messages', [{}])[-1].get('content', '')
        idx = 0 if 'SLICE_A' in txt else (1 if 'SLICE_B' in txt else 2)
        payload = json.dumps(ANS[idx], ensure_ascii=False)
        if self.path.endswith('/chat/completions'):
            out = {'choices': [{'message': {'content': payload}}], 'usage': {'total_tokens': 1}}
        else:
            out = {'content': [{'type': 'text', 'text': payload}], 'usage': {'input_tokens': 1}}
        b = json.dumps(out).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)


def main():
    srv = ThreadingHTTPServer(('127.0.0.1', 8791), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmp = tempfile.mkdtemp(prefix='selftest_')
    out, res = os.path.join(tmp, '_out'), os.path.join(tmp, '结果')
    os.makedirs(out); os.makedirs(res)

    # 3 条真语料，标题里塞标记，供桩决定回答
    src = list(csv.DictReader(open(os.path.join(HERE, '..', '..', '05_编码包', '输入包_编码集v4.csv'),
                                   encoding='utf-8-sig')))[:3]
    mark = ['SLICE_A', 'SLICE_B', 'SLICE_C']
    inp = os.path.join(tmp, 'in.csv')
    with open(inp, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=src[0].keys()); w.writeheader()
        for r, m in zip(src, mark):
            r['标题'] = m + ' ' + r['标题']
            w.writerow(r)

    cfg = os.path.join(tmp, 'models.json')
    json.dump([{'apiKey': 'test', 'url': 'http://127.0.0.1:8791/v1'}], open(cfg, 'w'))

    env = dict(os.environ, OUT_DIR=out, INP_CSV=inp, MODELS_JSON=cfg, RES_DIR=res,
               MODELS_OVERRIDE=json.dumps({'m1': ['fake-a', 'anthropic'],
                                           'm2': ['fake-b', 'anthropic'],
                                           'm3': ['fake-c', 'openai']}))
    fails = []

    def chk(name, cond, extra=''):
        print(('  PASS ' if cond else '  FAIL ') + name + (('  ' + extra) if extra and not cond else ''))
        if not cond:
            fails.append(name)

    print('【1】跑批（3 条 × 3 模型，本地桩）')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'run_models.py')], env=env,
                       capture_output=True, text=True, encoding='utf-8')
    print('\n'.join('  | ' + l for l in r.stdout.strip().splitlines()))
    if r.returncode:
        print(r.stderr[-1500:])
    files = sorted(os.listdir(out))
    chk('落盘文件名带 v4.2', all(x.endswith('_v4.2.jsonl') for x in files), str(files))
    chk('三个模型都有文件', len(files) == 3, str(files))

    recs = {}
    for fn in files:
        rows = [json.loads(l) for l in open(os.path.join(out, fn), encoding='utf-8')]
        recs[fn] = rows
        chk(f'{fn} 有 prompt_ver=v4.2', all(o.get('prompt_ver') == 'v4.2' for o in rows))
        chk(f'{fn} 有主键', all(o.get('id') for o in rows))
    allrows = [o for rows in recs.values() for o in rows]
    b = [o for o in allrows if o.get('ok') and o.get('d1') == '无']
    chk('d1=无 时 d1b 被强制回未报告', bool(b) and all(o['d1b'] == '未报告' for o in b),
        str([(o['id'], o.get('d1b')) for o in b][:3]))
    chk('六轴全空且 off_axis 说不出类 → 不出现在成功记录里',
        not [o for o in allrows if o.get('ok') and not any(o.get(k) for k in 'abcdef')])
    chk('openai 出口也跑通了', any(o.get('tag') == 'm3' and o.get('ok') for o in allrows))

    print('\n【2】断点续跑（再跑一次：成功的应跳过，失败的重试）')
    n0 = CALLS["n"]
    r = subprocess.run([sys.executable, os.path.join(HERE, 'run_models.py')], env=env,
                       capture_output=True, text=True, encoding='utf-8')
    n_fail = sum(1 for o in allrows if not o.get('ok'))   # 每条失败记录重试一次
    chk('续跑只重试失败条目', CALLS["n"] - n0 == n_fail, f'调用 {n0} → {CALLS["n"]}，失败 {n_fail}')
    chk('续跑跳过成功条目', r.stdout.count('本轮待跑 1') == 3, r.stdout.strip().splitlines()[-1] if r.stdout else '')

    print('\n【3】合并与 κ')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'merge_and_kappa.py')], env=env,
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        print(r.stderr[-1500:])
    chk('合并脚本退出码 0', r.returncode == 0)
    fp = os.path.join(res, '一致性_逐字段.csv')
    chk('生成逐字段表', os.path.exists(fp))
    if os.path.exists(fp):
        rows = list(csv.DictReader(open(fp, encoding='utf-8-sig')))
        chk('逐字段表含 d1b 行', any(x['字段'] == 'd1b' for x in rows), str([x['字段'] for x in rows]))
        d1b = [x for x in rows if x['字段'] == 'd1b']
        chk('d1b 是数值或 n/a，不是 nan 字符串',
            bool(d1b) and d1b[0]['Fleiss_kappa'] not in ('nan', ''), str(d1b))
    chk('生成逐档表', os.path.exists(os.path.join(res, '一致性_逐档.csv')))

    srv.shutdown()
    shutil.rmtree(tmp, ignore_errors=True)
    print('\n' + ('全部通过' if not fails else f'失败 {len(fails)} 项：{fails}'))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
