# -*- coding: utf-8 -*-
"""把 session transcript 转成可读 markdown：保留对话文本与工具名，剥离系统提示，做脱敏。"""
import os, sys, json, re
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\Administrator\.workbuddy\projects\c-Users-Administrator-WorkBuddy-2026-10-22-12-32-14\55664490-f493-4a40-ae67-d91876632fb1.jsonl'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), '10_过程归档', '对话历史_20261022.md')

PAT = [
    (re.compile(r'sk-[A-Za-z0-9_\-]{16,}'), '<API_KEY>'),
    (re.compile(r'(?:Bearer|token|apikey|api_key|secret|password)\s*[:=]\s*["\']?[A-Za-z0-9._\-]{12,}', re.I), '<CREDENTIAL>'),
    (re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}'), '<EMAIL>'),
    (re.compile(r'C:////*[/////]+Users////*[/////]+Administrator'), 'C:/Users/<user>'),
    (re.compile(r'/c/Users/Administrator'), '/c/Users/<user>'),
    (re.compile(r'\bAdministrator\b'), '<user>'),
    (re.compile(r'\b[0-9a-f]{32,}\b'), '<HASH>'),
]


def clean(t):
    for rx, rep in PAT:
        t = rx.sub(rep, t)
    return t


def strip_sys(t):
    t = re.sub(r'<system-reminder[^>]*>.*?</system-reminder>', '', t, flags=re.S)
    t = re.sub(r'<user-context>.*?</user-context>', '', t, flags=re.S)
    t = re.sub(r'<memory>.*?</memory>', '', t, flags=re.S)
    t = re.sub(r'<available_skills>.*?</available_skills>', '', t, flags=re.S)
    return t.strip()


turns = []
tools = Counter()
for line in open(SRC, encoding='utf-8'):
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get('type') != 'message':
        if d.get('name'):
            tools[d['name']] += 1
        continue
    role = d.get('role')
    cont = d.get('content')
    if isinstance(cont, list):
        buf = []
        for c in cont:
            if not isinstance(c, dict):
                continue
            if c.get('type') in ('text', 'input_text', 'output_text'):
                buf.append(c.get('text', ''))
        txt = '\n'.join(buf)
    elif isinstance(cont, str):
        txt = cont
    else:
        txt = ''
    txt = strip_sys(txt)
    if not txt.strip():
        continue
    turns.append((role, clean(txt), d.get('timestamp')))

# 合并连续同角色
merged = []
for role, txt, ts in turns:
    if merged and merged[-1][0] == role:
        merged[-1] = (role, merged[-1][1] + '\n\n' + txt, merged[-1][2])
    else:
        merged.append((role, txt, ts))

import datetime
lines = ['# 对话历史（2026-10-22，CHI 2027 火灾语料与设计空间）', '',
         '本文件由会话记录自动导出，剥离系统提示、脱敏后用 markdown 保存。',
         '工具调用只记录名称与次数，不保留原始输出（原始输出已作为过程文件单独归档）。', '',
         f'- 对话轮次：{len(merged)}',
         f'- 工具调用：{sum(tools.values())} 次，{len(tools)} 种', '',
         '## 工具使用统计', '', '| 工具 | 次数 |', '|---|---|']
for k, v in tools.most_common():
    lines.append(f'| `{k}` | {v} |')
lines += ['', '---', '']

for i, (role, txt, ts) in enumerate(merged, 1):
    who = {'user': '用户', 'assistant': '助手'}.get(role, role)
    t = ''
    if ts:
        try:
            t = datetime.datetime.fromtimestamp(ts / 1000).strftime('%H:%M:%S')
        except Exception:
            t = ''
    lines.append(f'### [{i}] {who} {t}'.rstrip())
    lines.append('')
    lines.append(txt)
    lines.append('')

open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
print('轮次', len(merged), '工具调用', sum(tools.values()))
print('输出', OUT, f'{os.path.getsize(OUT)/1024:.0f} KB')

# 用户原话索引
uq = [txt for role, txt, _ in merged if role == 'user']
with open(os.path.join(os.path.dirname(os.path.dirname(HERE)), '10_过程归档', '对话历史_用户原话索引.md'), 'w', encoding='utf-8') as fh:
    fh.write('# 用户原话索引（决策轨迹）\n\n按时间顺序，仅保留用户发言全文。\n\n---\n\n')
    for i, t in enumerate(uq, 1):
        fh.write(f'**{i}.** {t}\n\n')
print('用户发言', len(uq), '条')
