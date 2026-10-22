# -*- coding: utf-8 -*-
"""图 2 / 图 3：34 档覆盖占位图 + 六轴分布

数据源：第17轮 覆盖统计.json（106 条，off_axis 12）。
输出：00_核心交付/12_图2_34档覆盖占位图.png|pdf
      00_核心交付/13_图3_六轴分布.png|pdf
"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "00_核心交付")
SRC = os.path.join(REPO, "06_工作流产物", "第17轮_终补搜与验证_20261022", "覆盖统计.json")

for cand in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC"):
    if any(cand == f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams["axes.unicode_minus"] = False

D = json.load(open(SRC, encoding="utf-8"))
FREQ = D["档频次"]
N_TOTAL = D["条数"]

AXES = [
    ("a", "信息可达性", ["A1", "A2", "A3", "A4", "A5"],
     ["双通道有效", "仅单通道", "构件遮挡", "信号被日常化", "无可判信号"]),
    ("b", "确认的社会性", ["B1", "B2", "B3", "B4", "B5"],
     ["自身确认", "他人告知", "中介渠道", "统一广播", "始终未确认"]),
    ("c", "可行动集", ["C1", "C2", "C3", "C4", "C5", "C6"],
     ["路径全通", "单路受限", "身体不足", "被外力锁闭", "充烟不可入", "路径归零"]),
    ("d", "决策指向", ["D1", "D2", "D3", "D4", "D5"],
     ["向下撤离", "向上/天台", "固守待援", "跨户移动", "跳楼悬空"]),
    ("e", "能动性来源", ["E1", "E2", "E3", "E4", "E5"],
     ["自行判断", "他人促成", "指令替代", "等而未得", "错误指令"]),
    ("f", "处境主体", ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"],
     ["普通成人", "老年", "儿童", "行动不便", "视障", "听障", "孕/抱婴", "独居"]),
]

INK = "#1a1a1a"
GREY = "#8a8a8a"
# 灰阶三档 + 空缺用点线
C_SUFF = "#3d3d3d"   # ≥3 充足
C_SPARSE = "#b9b9b9"  # 1-2 单点
C_ZERO = "#ffffff"   # 0 空缺


# ---------------- 图 2：34 格占位 ----------------
def fig2():
    fig, ax = plt.subplots(figsize=(7.4, 5.9))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    x0 = 19.0
    cell, gap = 11.7, 0.95
    row_h, row_gap = 10.2, 0.8
    y = 89.5

    for key, name, codes, labels in AXES:
        n_row = 2 if len(codes) > 6 else 1
        per = 4 if n_row == 2 else len(codes)
        cy_mid = y - row_h * n_row / 2
        ax.text(0.8, cy_mid + 1.4, name, ha="left", va="center",
                fontsize=8.2, color=INK, fontweight="bold")
        ax.text(0.8, cy_mid - 2.2, key, ha="left", va="center",
                fontsize=9.0, color=GREY, style="italic")
        for i, (c, lb) in enumerate(zip(codes, labels)):
            r, k = divmod(i, per)
            cx = x0 + k * (cell + gap)
            cy = y - (r + 1) * row_h + 1.5
            n = FREQ.get(c, 0)
            bh = row_h - 3.6
            fill = C_ZERO if n == 0 else (C_SPARSE if n < 3 else C_SUFF)
            ls = (0, (2.2, 1.6)) if n == 0 else "solid"
            ax.add_patch(FancyBboxPatch((cx, cy), cell, bh,
                                        boxstyle="round,pad=0.10,rounding_size=0.6",
                                        linewidth=0.75, edgecolor="#4a4a4a" if n >= 3 else GREY,
                                        facecolor=fill, linestyle=ls, zorder=2))
            tc = "#ffffff" if n >= 3 else INK
            ax.text(cx + cell / 2, cy + bh * 0.68, c, ha="center", va="center",
                    fontsize=7.8, color=tc, fontweight="bold", zorder=3)
            ax.text(cx + cell / 2, cy + bh * 0.31, lb, ha="center", va="center",
                    fontsize=5.6, color=tc, zorder=3)
            ax.text(cx + cell / 2, cy - 1.35, f"n={n}", ha="center", va="center",
                    fontsize=6.4, color="#a33" if n == 0 else INK, zorder=3,
                    fontweight="bold" if n == 0 else "normal")
        y -= row_h * n_row + row_gap

    # 图例
    lx, ly = 19.0, 7.2
    items = [(C_SUFF, "solid", "充足（≥3 例）26 档"), (C_SPARSE, "solid", "单点（1–2 例）7 档"),
             (C_ZERO, (0, (2.2, 1.6)), "空缺（0 例）1 档")]
    for i, (fc, ls, lb) in enumerate(items):
        ax.add_patch(FancyBboxPatch((lx + i * 26.0, ly), 2.8, 2.0,
                                    boxstyle="round,pad=0.08,rounding_size=0.35",
                                    facecolor=fc, edgecolor="#4a4a4a", linewidth=0.7, linestyle=ls))
        ax.text(lx + i * 26.0 + 3.7, ly + 1.0, lb, va="center", fontsize=7.0, color=INK)

    ax.text(50, 96.6, "图 2　六轴 34 档在 106 篇语料中的覆盖", ha="center", va="center",
            fontsize=9.6, color=INK, fontweight="bold")
    ax.text(50, 3.0, f"n = {N_TOTAL} 篇可编码切片；同一篇可命中多档，故各档之和大于 {N_TOTAL}。"
                     f"落在六轴之外者 {D['off_axis']} 篇（{D['off_axis']/N_TOTAL*100:.1f}%）。",
            ha="center", va="bottom", fontsize=6.4, color=GREY)

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(os.path.join(OUT, "12_图2_34档覆盖占位图.png"), dpi=300)
    fig.savefig(os.path.join(OUT, "12_图2_34档覆盖占位图.pdf"))
    print("fig2 ok")


# ---------------- 图 3：六轴分布 ----------------
def fig3():
    ORDER = [
        ("a 信息可达性", ["A2", "A5", "A1", "A4", "A3"]),
        ("b 确认的社会性", ["B1", "B2", "B5", "B4", "B3"]),
        ("c 可行动集", ["C6", "C5", "C1", "C3", "C4", "C2"]),
        ("d 决策指向", ["D1", "D5", "D3", "D4", "D2"]),
        ("e 能动性来源", ["E2", "E1", "E3", "E4", "E5"]),
        ("f 处境主体", ["F3", "F2", "F1", "F4", "F8", "F5", "F7", "F6"]),
    ]
    LBL = {}
    for _, _, codes, labels in AXES:
        for c, l in zip(codes, labels):
            LBL[c] = l
    FIG = [(t, [(f"{c} {LBL[c]}", FREQ.get(c, 0)) for c in codes]) for t, codes in ORDER]
    fig, axes = plt.subplots(2, 3, figsize=(7.6, 4.5))
    for ax, (title, data) in zip(axes.ravel(), FIG):
        labels = [d[0] for d in data][::-1]
        vals = [d[1] for d in data][::-1]
        colors = ["#3d3d3d" if v >= 10 else ("#8f8f8f" if v > 0 else "#dcdcdc") for v in vals]
        ax.barh(range(len(vals)), vals, color=colors, height=0.62, linewidth=0)
        ax.set_yticks(range(len(vals)))
        ax.set_yticklabels(labels, fontsize=5.8)
        ax.set_xlim(0, 44)
        ax.tick_params(axis="x", labelsize=5.4, length=2)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_linewidth(0.5)
        ax.spines["bottom"].set_linewidth(0.5)
        ax.set_title(title, fontsize=7.2, pad=3, color=INK, fontweight="bold")
        for i, v in enumerate(vals):
            ax.text(v + 0.8, i, str(v), va="center", fontsize=5.6, color="#333333")
        ax.grid(axis="x", linewidth=0.35, color="#e2e2e2")
        ax.set_axisbelow(True)

    fig.suptitle("图 3　六轴各档频次（106 篇，可多选）", fontsize=9.0, y=0.985, color=INK,
                 fontweight="bold")
    fig.text(0.5, 0.012, "A2+A5 = 62 篇（58.5%）为「只拿到一条线索或什么都没拿到」；"
                         "C6 32 篇为路径归零；E2 40 篇为他人促成行动。",
             ha="center", fontsize=6.2, color="#555555")
    fig.subplots_adjust(left=0.155, right=0.985, top=0.90, bottom=0.10, wspace=0.72, hspace=0.55)
    fig.savefig(os.path.join(OUT, "13_图3_六轴分布.png"), dpi=300)
    fig.savefig(os.path.join(OUT, "13_图3_六轴分布.pdf"))
    print("fig3 ok")


if __name__ == "__main__":
    fig2()
    fig3()
