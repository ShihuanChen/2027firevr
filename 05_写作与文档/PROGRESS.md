# 项目进度追踪

> 更新: 2026-07-04 | 目标: CHI 2027 投稿 (Deadline: 2026-09-10)

---

## ✅ 已完成

| # | 任务 | 文件 | 状态 |
|:---|:---|:---|:---:|
| 1 | 正文抓取脚本 (Playwright增强) | `工作流/refetch_fulltext_playwright.py` | ✅ |
| 2 | 五维语义评分脚本 (GLM API) | `工作流/score_articles.py` | ✅ |
| 3 | 筛选标准详细文档 | `docs/新闻筛选标准_五维语义评分.md` | ✅ |
| 4 | 论文大纲 LaTeX (Overleaf-ready) | `论文大纲_CHI2027_Overleaf.tex` | ✅ |
| 5 | 中文版 PRISMA 流程图 | `figures/screening_flowchart_v2_cn.html` | ✅ |
| 6 | 最终数据条目与Label定义 | `data/最终数据条目与Label定义.md` | ✅ |
| 7 | 操作手册 | `docs/操作手册_数据流水线.md` | ✅ |
| 8 | 依赖更新 | `requirements.txt` | ✅ |

---

## 🔄 进行中 / 待执行

| # | 任务 | 优先级 | 说明 |
|:---|:---|:---:|:---|
| 1 | **安装 Playwright** | 🔴高 | `pip install playwright && python -m playwright install chromium` |
| 2 | **跑正文补抓** | 🔴高 | `python 工作流/refetch_fulltext_playwright.py --input 工作流/第三轮_含正文.csv --only-keep --workers 4` |
| 3 | **跑五维评分** | 🔴高 | 正文≥200条后: `python 工作流/score_articles.py --input xxx_补充正文.csv --workers 4` |
| 4 | 人工复核60-74分条目 | 🟡中 | 评分完成后 |
| 5 | VR编码 (S4) | 🟡中 | 复核完成后 |
| 6 | 更新流程图数字 | 🟢低 | 最终数据确定后 |
| 7 | 上传Overleaf开始写作 | 🟢低 | 数据完整后 |

---

## 📊 数据漏斗当前状态

```
S0 = 8,900  →  S1 = 8,072  →  S2 = 140  →  S3 = ?  →  S4 = ?  →  S5 = ?
   检索        去重+预筛       正文抓取      五维评分     VR编码     精选
```

**瓶颈**: S2 (正文抓取) 仅 140 条。目标通过 Playwright 增强到 ≥400。

---

## ⚠️ 已知风险

1. **反爬**: 部分网站有 Cloudflare/验证码，Playwright 可能不够 → 备选: nodriver
2. **API额度**: GLM API 可能有调用限制，注意不要超额
3. **论文长度**: CHI 2027 要求 5,000-8,000 词，当前大纲各节需控制字数
4. **匿名化**: 投稿时需移除所有作者信息（LaTeX 已设置 `anonymous`）
5. **中文新闻缺失**: GDELT 以英文为主，中文火灾报道覆盖率低

---

## 📁 关键文件速查

| 想做什么 | 看哪个文件 |
|:---|:---|
| 理解整个项目 | `总纲_VR高层火灾共情系统.md` |
| 开始写论文 | `论文大纲_CHI2027_Overleaf.tex` |
| 补抓新闻正文 | `工作流/refetch_fulltext_playwright.py` |
| 五维语义评分 | `工作流/score_articles.py` |
| 看筛选标准 | `docs/新闻筛选标准_五维语义评分.md` |
| 看数据定义 | `data/最终数据条目与Label定义.md` |
| 看文献综述 | `docs/文献综述_VR高层火灾共情系统.md` |
| 看场景设计 | `总纲_VR高层火灾共情系统.md` §5-6 |
| 看VR编码框架 | `总纲_VR高层火灾共情系统.md` §4 |
| 看操作步骤 | `docs/操作手册_数据流水线.md` |
