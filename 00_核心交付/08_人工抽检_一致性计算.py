# -*- coding: utf-8 -*-
"""人机一致率计算：读 08_人工抽检_12条.csv（你填好后）+ 参考对照，输出逐轴一致率表。

用法：
    cd repo/00_核心交付
    python 08_人工抽检_一致性计算.py

判定规则：某轴完全一致（档位集合相同）记 1，否则记 0。同时报告 Jaccard 部分一致，
避免"只多标了一个档"和"完全标错"被算成同一件事。
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILLED = os.path.join(HERE, "08_人工抽检_12条.csv")
REF = os.path.join(HERE, "08_人工抽检_参考对照.json")
AXES = ["a", "b", "c", "d", "e", "f"]
AX_NAME = {"a": "a 信息可达性", "b": "b 确认的社会性", "c": "c 可行动集",
           "d": "d 决策指向", "e": "e 能动性来源", "f": "f 处境主体"}


def parse(v):
    if not v:
        return None
    if isinstance(v, list):
        return {str(x).strip().upper() for x in v if str(x).strip()}
    return {x.strip().upper() for x in str(v).replace("，", ";").replace(",", ";").replace("/", ";").split(";")
            if x.strip()}


def cell(v):
    """返回 (是否填了, 档位集合)。填「无」= 该轴无档可判，记为空集；留空 = 漏填，不计入分母。"""
    if v is None or not str(v).strip():
        return False, set()
    s = parse(v) or set()
    s = {x for x in s if x not in ("无", "NONE", "NA", "-")}
    return True, s


def main():
    rows = list(csv.DictReader(open(FILLED, encoding="utf-8-sig")))
    ref = {r["切片ID"]: r for r in json.load(open(REF, encoding="utf-8"))}

    filled = [r for r in rows if any(cell(r.get(k))[0] for k in AXES)]
    if not filled:
        print("还没填。先按 08_人工抽检_说明.md 编完 12 条再跑。")
        return

    per_axis = {k: {"n": 0, "exact": 0, "jac": 0.0, "blank": 0} for k in AXES}
    off = {"n": 0, "exact": 0}
    detail = []

    for r in filled:
        sid = r["切片ID"]
        rr = ref.get(sid, {})
        line = {"切片ID": sid, "分歧轴": [], "空白轴": []}
        for k in AXES:
            ok_h, hu = cell(r.get(k))
            _, re_ = cell(rr.get(k))          # 参考为空 = 该轴无档可判，记空集
            if not ok_h:
                per_axis[k]["blank"] += 1
                line["空白轴"].append(k)
                continue
            per_axis[k]["n"] += 1
            eq = hu == re_
            per_axis[k]["exact"] += int(eq)
            union = hu | re_
            per_axis[k]["jac"] += (len(hu & re_) / len(union)) if union else 1.0
            if not eq:
                line["分歧轴"].append(f"{k}: 你={sorted(hu) or '无'} 参考={sorted(re_) or '无'}")
        if r.get("off_axis") and rr.get("off_axis"):
            off["n"] += 1
            off["exact"] += int(str(r["off_axis"]).strip() == str(rr["off_axis"]).strip())
        detail.append(line)

    print("\n## 逐轴一致率（%d 条已填）\n" % len(filled))
    print("| 轴 | 可比条数 | 完全一致 | 一致率 | Jaccard 部分一致 |")
    print("|---|---|---|---|---|")
    tot_n = tot_e = 0
    for k in AXES:
        d = per_axis[k]
        if not d["n"]:
            continue
        tot_n += d["n"]
        tot_e += d["exact"]
        print(f"| {AX_NAME[k]} | {d['n']} | {d['exact']} | {d['exact']/d['n']*100:.1f}% | {d['jac']/d['n']:.3f} |")
    if tot_n:
        print(f"| **合计** | {tot_n} | {tot_e} | **{tot_e/tot_n*100:.1f}%** | — |")
    if off["n"]:
        print(f"\noff_axis 一致 {off['exact']}/{off['n']} = {off['exact']/off['n']*100:.1f}%")

    n_low = sum(1 for r in filled if str(r.get("confidence", "")).strip().lower() == "low")
    print(f"\n你判 low 的条数：{n_low}/{len(filled)}")

    blank = sum(per_axis[k]["blank"] for k in AXES)
    if blank:
        print(f"⚠️ 有 {blank} 个轴格留空（留空不计入分母）。该轴确实无档可判时请填「无」，不要留空。")

    print("\n## 逐条分歧\n")
    any_dis = False
    for line in detail:
        if line["分歧轴"]:
            any_dis = True
            print(f"- **{line['切片ID']}**")
            for x in line["分歧轴"]:
                print(f"  - {x}")
    if not any_dis:
        print("无分歧。")

    print("\n提醒：一致率 ≥85% 允许模型单独承担；70–85% 模型作初标、人工复核；<70% 该轴判定线重写。")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
