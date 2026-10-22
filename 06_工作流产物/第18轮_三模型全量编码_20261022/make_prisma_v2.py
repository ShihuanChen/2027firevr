# -*- coding: utf-8 -*-
"""PRISMA 2020 流程图 v2：单调递减版

v1 的问题：把三轮工作（60 起 → +34 → +11 → 终检 −2）串成一条线，
数字上下反复，读者看不出"筛掉了什么"。

v2 改法：按来源拆成并列支线，每条支线只减不增，最后一次性归并。
  A 支线（众包新闻库）8,180 → 6,666 → 1,443 → 1,027 → 291 → 125
  B 支线（定向补搜）    934 → 118 → 44
  归并：125 + 44 = 169 篇素材 → 事件归并去重 → 106 篇 / 103 起

所有数字出处见 07_PRISMA_2020_数字溯源.md。
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "00_核心交付"))

for cand in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC"):
    if any(cand == f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams["axes.unicode_minus"] = False

INK, LINE, FILL, FILL_EX, PHASE = "#1a1a1a", "#4a4a4a", "#f6f6f5", "#ffffff", "#e8e6e1"

fig, ax = plt.subplots(figsize=(7.4, 9.6))
ax.set_xlim(0, 100)
ax.set_ylim(0, 103)
ax.axis("off")


def box(x, y, w, h, title, count=None, fs=7.8, cfs=9.0, fill=FILL, bold_count=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.1",
                                linewidth=0.9, edgecolor=LINE, facecolor=fill, zorder=3))
    cx = x + w / 2
    if count:
        ax.text(cx, y + h * 0.70, title, ha="center", va="center", fontsize=fs, color=INK, zorder=4)
        ax.text(cx, y + h * 0.27, count, ha="center", va="center", fontsize=cfs, color=INK,
                fontweight="bold" if bold_count else "normal", zorder=4)
    else:
        ax.text(cx, y + h / 2, title, ha="center", va="center", fontsize=fs, color=INK,
                zorder=4, linespacing=1.6)


def excluded(x, y, w, h, text):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.9",
                                linewidth=0.7, edgecolor="#9a9a9a", facecolor=FILL_EX,
                                linestyle=(0, (3, 2)), zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=6.4,
            color="#333333", zorder=4, linespacing=1.55)


def arrow(x0, y0, x1, y1, style="-|>", lw=0.9, color=LINE, conn=None):
    kw = dict(arrowstyle=style, mutation_scale=8, linewidth=lw, color=color, zorder=2)
    if conn:
        kw["connectionstyle"] = conn
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), **kw))


# ---- 阶段带 ----
for y0, h, label in [(84, 16, "识别"), (34, 50, "筛选"), (2, 32, "纳入")]:
    ax.add_patch(Rectangle((0.4, y0), 6.0, h, facecolor=PHASE, edgecolor="none", zorder=1))
    ax.text(3.4, y0 + h / 2, label, rotation=90, ha="center", va="center",
            fontsize=9.0, color="#5a5a5a", fontweight="bold", zorder=2)

# ---- 列坐标 ----
AX, AW = 8.5, 34.0        # A 支线
EX, EW = 45.5, 21.0       # 排除框
BX, BW = 69.0, 24.0       # B 支线
ACX, BCX = AX + AW / 2, BX + BW / 2

# ---- A 支线（众包新闻库）----
a = [
    (91.0, "众包新闻帖（全量库）", "n = 8,180"),
    (80.5, "正文完整可解析", "n = 6,666"),
    (70.0, "语义判定为火灾相关", "n = 1,443"),
    (59.5, "同一事件去重后的候选池", "n = 1,027"),
    (49.0, "进入人工逐条精判", "n = 291"),
    (37.0, None, None),          # 125 框单独画（文字较长）
]
for y, t, c in a[:5]:
    box(AX, y, AW, 7.0, t, c)
box(AX, 37.0, AW, 8.6,
    "人工精判保留 109 篇 ＋ 人工补充 16 篇\n（幸存者自述／证词）＝ 素材库 125 篇", fs=7.2)

for i in range(5):
    arrow(ACX, a[i][0], ACX, a[i + 1][0] + (7.0 if i < 4 else 8.6))
arrow(ACX, 37.0, ACX, 30.6)

# ---- A 支线排除框 ----
excluded(EX, 80.5, EW, 7.0, "正文缺失或不可解析\nn = 1,514")
excluded(EX, 70.0, EW, 7.0, "非火灾内容 n = 5,192\n语义判定错误 n = 31")
excluded(EX, 59.5, EW, 7.0, "同一事件的重复报道\nn = 416")
excluded(EX, 49.0, EW, 7.0, "自动条件不满足\n（无高层特征／细节不足）\nn = 736")
excluded(EX, 37.0, EW, 8.6, "过程细节不足\n或通稿碎片\nn = 182")
for y in (80.5, 70.0, 59.5, 49.0, 37.0):
    h = 8.6 if y == 37.0 else 7.0
    arrow(AX + AW, y + h / 2, EX, y + h / 2, style="-|>", lw=0.6, color="#9a9a9a")

# ---- B 支线（定向补搜）----
b = [
    (91.0, "两轮定向补搜命中", "n = 934"),
    (80.5, "自动核验通过（有高层特征＋细节）", "n = 118"),
    (70.0, "逐篇核验后入集", "n = 46 篇（44 起）"),
]
for i, (y, t, c) in enumerate(b):
    box(BX, y, BW, 7.0, t, c, fs=7.0)
    if i < 2:
        arrow(BCX, y, BCX, b[i + 1][0] + 7.0)
ax.text(BCX + 2.0, 78.4, "剔 816 条", ha="left", va="center", fontsize=6.4, color="#666666")
ax.text(BCX + 2.0, 67.4, "剔 72 篇", ha="left", va="center", fontsize=6.4, color="#666666")

# B 支线汇入
arrow(BCX, 70.0, BCX, 32.0, conn=None)  # 先竖直下到汇合框顶

# ---- 归并框 ----
box(14.0, 23.0, 72.0, 7.4,
    "素材汇合　125 篇（众包库）＋ 46 篇（定向补搜）＝ 171 篇", fs=7.6)

box(20.0, 12.5, 60.0, 7.4,
    "事件归并：主库同事件多源报道合并为 60 篇代表篇　−65 篇", fs=7.4)
arrow(50.0, 23.0, 50.0, 19.9)

box(24.0, 3.0, 52.0, 7.4, "最终编码集　103 起事件／106 篇切片", cfs=9.4)
arrow(50.0, 12.5, 50.0, 10.4)

ax.text(50, 100.6, "图 1　语料筛选与编码集构建流程（PRISMA 2020）",
        ha="center", va="center", fontsize=9.8, color=INK, fontweight="bold")
ax.text(50, 0.4, "主分析层 70 起（过程细节 ≥ 3 类）　｜　补充层 33 起",
        ha="center", va="bottom", fontsize=6.8, color="#666666")

fig.subplots_adjust(left=0.005, right=0.995, top=0.985, bottom=0.02)
pdf = os.path.join(OUT_DIR, "07_PRISMA_2020流程图.pdf")
png = os.path.join(OUT_DIR, "07_PRISMA_2020流程图.png")
fig.savefig(pdf, format="pdf")
fig.savefig(png, dpi=300, format="png")
print("saved", pdf)
print("saved", png)
