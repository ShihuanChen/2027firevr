# -*- coding: utf-8 -*-
"""生成「直接打标」批次文件：每个文件 = 完整提示词 + 5 篇正文，一次全选复制即可。

不做任何 API 调用。产出的 txt 就是给网页版 AI 粘贴用的。
用法：python build_batches.py
"""
import ast
import csv
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
INP = os.path.join(REPO, '05_编码包', '输入包_编码集v4.csv')
MER = os.path.join(REPO, '00_核心交付', '16_编码结果_106篇_合并交付版.csv')
CHK = os.path.join(REPO, '00_核心交付', '08_人工抽检_12条.csv')
SRC = os.path.join(REPO, '06_工作流产物', '第18轮_三模型全量编码_20261022', 'run_models.py')
OUT = os.path.join(HERE, '批次')
PER = 5            # 每批篇数
SEED = 20261023
SEED_N = 40        # 前 8 批 = 精挑 40 篇，覆盖全部档位


def base_prompt():
    """从 run_models.py 取 v4.2 提示词常量，改成多篇版。"""
    tree = ast.parse(open(SRC, encoding='utf-8').read())
    p = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'PROMPT':
            p = ast.literal_eval(node.value)
    assert p, 'run_models.py 里找不到 PROMPT 常量'

    cut = p.index('现在开始，只输出 JSON：')
    head = p[:cut]

    head = head.replace(
        '我会给你一条新闻的标题与正文，你输出一个 JSON 对象，一条一行，不要任何解释文字、不要 markdown 代码块。',
        '我会给你 {N} 篇新闻的标题与正文。每篇输出一个 JSON 对象，一行一篇，共 {N} 行。'
        '不要任何解释文字、不要 markdown 代码块、不要把多篇合并成一个对象。')
    head = head.replace(
        '4. 不确定就填 confidence="low"，不要为了让字段非空而猜。',
        '4. 不确定就填 confidence="low"，不要为了让字段非空而猜。\n'
        '5. 各篇之间独立判定，不要跨篇参照，也不要为了"和上一篇一致"而改自己的判断。\n'
        '6. 每行的 id 必须照抄我标注的切片ID（形如 E0004-1），不要改、不要省略。')
    head = head.replace(
        '【输出格式】严格如下，一条 JSON 一行，键名不改、不增、不删：',
        '【输出格式】严格如下，每篇一条 JSON，一行一条，键名不改、不增、不删：')
    return head.rstrip()


def toks(s):
    return [t.strip() for t in re.split(r'[;,]', s or '') if t.strip()]


def main():
    rows = list(csv.DictReader(open(INP, encoding='utf-8-sig')))
    mer = {r['切片ID']: r for r in csv.DictReader(open(MER, encoding='utf-8-sig'))}
    order = {r['切片ID']: i for i, r in enumerate(rows)}

    def codes(sid):
        r = mer.get(sid) or {}
        s = set()
        for ax in 'abcdef':
            s.update(toks(r.get(ax)))
        if (r.get('off_axis') or '').strip() == '有':
            s.add('OFF')
        return s

    universe = set()
    for sid in mer:
        universe |= codes(sid)

    # 种子：12 条人工抽检（本身按稀有档 + 分歧最大挑的）
    seed = [r['切片ID'] for r in csv.DictReader(open(CHK, encoding='utf-8-sig'))]
    seed = [s for s in seed if s in order]

    picked, cov = list(dict.fromkeys(seed)), set()
    for s in picked:
        cov |= codes(s)
    while len(picked) < SEED_N:
        best = max((s for s in order if s not in picked),
                   key=lambda s: (len(codes(s) - cov), -order[s]))
        if not (codes(best) - cov):
            break
        picked.append(best)
        cov |= codes(best)
    while len(picked) < SEED_N:                       # 覆盖满了就按原顺序补
        for s in order:
            if s not in picked:
                picked.append(s)
                break

    miss = sorted(universe - cov)
    print(f'精挑 {len(picked)} 篇，覆盖 {len(cov)}/{len(universe)} 个档', end='')
    print(f'，缺 {miss}' if miss else '，全覆盖')

    random.seed(SEED)
    head_set = picked[:]
    random.shuffle(head_set)
    tail = [s for s in order if s not in set(head_set)]
    random.shuffle(tail)
    seq = head_set + tail

    byid = {r['切片ID']: r for r in rows}
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.txt'):
            os.remove(os.path.join(OUT, f))

    # 末尾不足 3 篇就并进前一批，避免多开一次对话
    chunks = [seq[i:i + PER] for i in range(0, len(seq), PER)]
    if len(chunks) > 1 and len(chunks[-1]) < 3:
        chunks[-2].extend(chunks.pop())

    tpl = base_prompt()
    open(os.path.join(HERE, '01_提示词_模板.txt'), 'w', encoding='utf-8').write(tpl + '\n')
    n = 0
    for chunk in chunks:
        n += 1
        bi = sum(len(c) for c in chunks[:n - 1])
        k = len(chunk)
        parts = [tpl.replace('{N}', str(k))]
        parts.append(f'以下是 {k} 篇。只输出 {k} 行 JSON，不要任何其他文字：\n')
        for i, sid in enumerate(chunk, 1):
            r = byid[sid]
            parts.append(f'【第 {i} 篇】切片ID：{sid}')
            parts.append(f'标题：{r["标题"]}')
            parts.append(f'正文：\n{r["正文"].strip()}\n')
        txt = '\n'.join(parts)
        name = f'第{n:02d}批_{"精选" if bi < SEED_N else "其余"}_{chunk[0]}等{k}篇.txt'
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(txt)

    print(f'已生成 {n} 批 → {OUT}')
    print(f'前 {SEED_N // PER} 批为精选 {SEED_N} 篇，后 {n - SEED_N // PER} 批为其余 {len(tail)} 篇')
    import json
    json.dump(seq, open(os.path.join(HERE, '批次顺序.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
