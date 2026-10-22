# -*- coding: utf-8 -*-
"""生成 PRISMA 2020 流程图（矢量 PDF + 300dpi PNG）。
数字全部来自已有产出文件，逐跳对应见 07_PRISMA_2020_数字溯源.md。
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "00_核心交付"))

# ---- 字体 ----
for cand in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC"):
    if any(cand == f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams["axes.unicode_minus"] = False

INK = "#1a1a1a"
LINE = "#4a4a4a"
FILL = "#f5f5f4"
FILL_EX = "#ffffff"
PHASE = "#e8e6e1"

# ---- 画布 ----
W, H = 7.2, 10.4
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box(x, y, w, h, title, count=None, sub=None, fill=FILL, fs=8.4, cfs=8.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.35,rounding_size=1.2",
                                linewidth=0.9, edgecolor=LINE, facecolor=fill, zorder=3))
    cx = x + w / 2
    if count:
        ax.text(cx, y + h * 0.66, title, ha="center", va="center", fontsize=fs, color=INK, zorder=4)
        ax.text(cx, y + h * 0.30, count, ha="center", va="center", fontsize=cfs,
                color=INK, fontweight="bold", zorder=4)
    else:
        ax.text(cx, y + h / 2, title, ha="center", va="center", fontsize=fs, color=INK, zorder=4)
    if sub:
        ax.text(cx, y - 1.1, sub, ha="center", va="top", fontsize=6.8, color="#666666", zorder=4)


def excluded(x, y, w, h, text):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0",
                                linewidth=0.7, edgecolor="#9a9a9a", facecolor=FILL_EX,
                                linestyle=(0, (3, 2)), zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7.0,
            color="#333333", zorder=4, linespacing=1.5)


def down(x, y0, y1):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle="-|>", mutation_scale=8,
                                 linewidth=0.9, color=LINE, zorder=2))


def right(x0, y0, x1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y0), arrowstyle="-|>", mutation_scale=7,
                                 linewidth=0.7, color="#9a9a9a", zorder=2))


# ---- 阶段带 ----
bands = [(80.5, 19.5, "识别"), (25.5, 55.0, "筛选"), (1.0, 24.5, "纳入")]
for y0, h, label in bands:
    ax.add_patch(Rectangle((0.5, y0), 7.5, h, facecolor=PHASE, edgecolor="none", zorder=1))
    ax.text(4.25, y0 + h / 2, label, rotation=90, ha="center", va="center",
            fontsize=9.2, color="#5a5a5a", fontweight="bold", zorder=2)

LB, LW = 13.0, 54.0          # 左列 box 的 x 与宽
RB, RW = 70.5, 28.0          # 右侧排除框的 x 与宽
CX = 40.0                    # 主流程竖线 x

# ---- 盒子定义 ----
# (y 底部, 高, 标题, 计数)
b1 = (91.0, 7.6, "检索获得的众包新闻帖", "n = 8,180")
b2 = (80.0, 7.6, "正文完整可解析", "n = 6,666")
b3 = (67.0, 7.6, "AI 语义判定为火灾相关", "n = 1,443")
b4 = (55.0, 7.6, "同一事件去重后的候选池", "n = 1,027")
b5 = (44.0, 7.6, "进入人工逐条精判", "n = 291")
b6 = (33.0, 7.6, "人工精判保留", "n = 109")
b7 = (24.0, 7.0, "另有补充高价值报道  n = 16\n素材库合计  n = 125（可编码正文 122 篇）", None)
b8 = (14.0, 7.0, "事件归并后的可重建事件", "n = 60 起 / 62 篇")
b9 = (4.0, 8.2, "最终编码集", "n = 105 起事件 / 107 篇切片")

for y, h, t, c in (b1, b2, b3, b4, b5, b6):
    box(LB, y, LW, h, t, c)
box(LB, b7[0], LW, b7[1], b7[2], fs=8.0)
box(LB, b8[0], LW, b8[1], b8[2], b8[3])
box(LB, b9[0], LW, b9[1], b9[2], b9[3])

# ---- 排除框 ----
excluded(RB, 80.0, RW, 7.6, "正文缺失或不可解析\nn = 1,514")
excluded(RB, 67.0, RW, 7.6, "非火灾内容  n = 5,192\n判定错误  n = 31")
excluded(RB, 55.0, RW, 7.6, "同一事件重复报道\nn = 416")
excluded(RB, 44.0, RW, 7.6, "高置信剔除，未进入人工精判\nn = 736")
excluded(RB, 33.0, RW, 7.6, "过程细节不足或通稿碎片\nn = 182")

# ---- 竖线 ----
for a, b in ((b1, b2), (b2, b3), (b3, b4), (b4, b5), (b5, b6), (b6, b7), (b7, b8), (b8, b9)):
    down(CX, a[0], b[0] + b[1])

# ---- 横向排除箭头 ----
for b in (b2, b3, b4, b5, b6):
    right(LB + LW, b[0] + b[1] / 2, RB)

# ---- 补搜标注（在 b8 下方另起两条支线，用文字块表达） ----
ax.add_patch(Rectangle((LB, 0.4), LW, 1.4, facecolor="none", edgecolor="none"))
ax.text(LB + LW / 2, 1.1,
        "第 16 轮定向补搜 +34 起  →  94 起 / 96 篇　｜　第 17 轮缺口专项补搜 +11 起  →  105 起 / 107 篇",
        ha="center", va="center", fontsize=6.9, color="#333333")
ax.text(LB + LW / 2, -0.9,
        "主分析层 71 起（过程细节 ≥ 3 类）　补充层 34 起",
        ha="center", va="center", fontsize=6.9, color="#666666")

ax.text(50, 99.2, "图 1　语料筛选与编码集构建流程（PRISMA 2020）",
        ha="center", va="center", fontsize=9.6, color=INK, fontweight="bold")

fig.subplots_adjust(left=0.01, right=0.99, top=0.985, bottom=0.035)
pdf = os.path.join(OUT_DIR, "07_PRISMA_2020流程图.pdf")
png = os.path.join(OUT_DIR, "07_PRISMA_2020流程图.png")
fig.savefig(pdf, format="pdf")
fig.savefig(png, dpi=300, format="png")
print("saved", pdf)
print("saved", png)
