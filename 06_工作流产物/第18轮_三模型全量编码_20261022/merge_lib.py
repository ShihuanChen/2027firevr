# -*- coding: utf-8 -*-
"""多编码者合并规则（唯一权威实现）

merge_and_kappa.py 与 build_deliverable.py 共用本模块，保证两份交付物
逐格一致。历史版本两个脚本各写一套，导致 238/636 格取值不同。

口径
----
单选字段：多数票；平票取票型字符串里第一个（并列时按编码者顺序 A→B→C）。

多选轴：**真多数票**——某个档被 ≥2 名编码者选中才计入合并结果。
  排序（保住「首位=主档、非首位=附档」的位置语义）：
    1. 票数降序
    2. 「被几位编码者放在首位」降序（主档优先）
    3. 档名字典序
  若三路完全对立、没有任何档达到 2 票：该轴合并值留空（不编造共识），
  并在「无多数票轴数」列记 1。该情形共 61/636 格。

不使用并集回退：并集会把「三方各标一个不同档」读成「同时属于三档」，
并集下 C1+C5（codebook 判为互斥）出现 12 次，多数票下只 4 次。
"""
import collections

MAJORITY = 2          # 3 名编码者 → 至少 2 票


def merge_single(vals, order=None):
    """单选字段合并。vals 为各编码者的取值列表，order 用于平票时的优先序。"""
    vals = [v for v in vals if v not in (None, '')]
    if not vals:
        return ''
    c = collections.Counter(vals)
    top = max(c.values())
    tied = [v for v, k in c.items() if k == top]
    if len(tied) == 1:
        return tied[0]
    # 平票：按 order（编码者顺序）取最先出现者
    if order:
        for v in vals:
            if v in tied:
                return v
    return tied[0]


def merge_multi(sets):
    """多选轴合并。

    返回 (合并值列表, 是否无多数票)。
    sets: 每个编码者给出的有序列表（首位=主档）。
    """
    sets = [list(s or []) for s in sets]
    n = len(sets)
    thr = MAJORITY if n >= 3 else max(1, (n + 1) // 2)

    vote = collections.Counter()
    first_vote = collections.Counter()
    for s in sets:
        for c in s:
            vote[c] += 1
        if s:
            first_vote[s[0]] += 1

    maj = {c for c, k in vote.items() if k >= thr}
    if not maj:
        return [], True

    ordered = sorted(maj, key=lambda c: (-vote[c], -first_vote[c], c))
    return ordered, False


def merge_axis_cell(sets):
    """多选轴合并成单元格字符串；首位代表主档。"""
    vals, no_maj = merge_multi(sets)
    return ';'.join(vals), no_maj
