# 朱倩 — 高层火灾VR共情系统 项目文件结构（已归类）

根目录只保留导航三件套 + 分类文件夹。零散文件已归位。

```
朱倩/
├── 00_审阅起点.md                         # 👉 人工审阅入口（先看这个）
├── README.md                              # 项目说明
├── PROGRESS.md                            # 进度跟踪
├── STRUCTURE.md                           # 本文件
│
├── docs/                                  # 所有文档（标准/报告/会议/总纲/大纲）
│   ├── 人工审阅批次_Top150.md             # ★ 人工审阅批次（你要读的文件）
│   ├── 第三轮筛选阶段报告.md              # 上一轮六张分析表 + 结论
│   ├── 新闻筛选标准_五维语义评分.md        # 五维评分纳入/排除规则
│   ├── 新闻筛选标准_详细文档.md
│   ├── 总纲_VR高层火灾共情系统.md
│   ├── 论文大纲_CHI2027_Overleaf.tex
│   ├── 文献综述_VR高层火灾共情系统.md
│   ├── 超相关论文_新闻提取与VR设计标准.md
│   ├── CHI获奖论文提取_打标标准与设计参考.md
│   ├── 游戏任务设计_VR指标症状映射.md
│   ├── 技术实现路径.md
│   ├── 操作手册_数据流水线.md
│   ├── 6.11会议.md / 6.24会议.md / 7.8会议.md
│
├── 工作流/                                 # 抓取与处理脚本（核心流水线，勿随意移动内部文件）
│   ├── real_scraper.py                    # 主抓取（GDELT 检索）
│   ├── incremental_search.py              # 增量检索（补抓新 query）
│   ├── refetch_fulltext_playwright.py     # Playwright 抓正文
│   ├── refetch_round3.py                  # 第三轮补抓
│   ├── score_heuristic_batch.py           # 五维启发式评分
│   ├── score_articles.py                  # 大模型评分（需智谱 API）
│   ├── export_review_batch.py             # 导出人工审阅批次
│   ├── config.yaml                        # 配置（含 API key）
│   ├── 第三轮_含正文.csv                   # ★ 主数据（8072 行，406 有正文）
│   ├── 人工审阅批次_含正文.csv             # 审阅批次表格版
│   ├── 候选素材_五维评分.csv               # 候选清单
│   └── README_抓取脚本使用说明.md
│
├── data/                                  # 原始收集 CSV / JSON
│   ├── results_2015~2026.csv / results_merged.csv
│   ├── global_high_rise_fire_details_20260624.csv
│   ├── source_registry_template.csv
│   └── 高层火灾新闻收集.csv
│
├── scripts/                               # 辅助脚本（从根目录归位）
│   ├── f.py / fetch.py / fetch_urls.py
│   ├── fire_news_scrapper.py / increment_search_and_dedup.py
│   └── requirements.txt
│
├── references/                            # 参考文献 PDF（从根目录归位）
│   ├── 1-s2.0-S2212420916306057-main.pdf
│   └── CCAB Full Report with Appendices 102004.pdf
│
├── figures/                               # 论文图表（PRISMA 漏斗图等）
├── image/                                 # 图片素材
├── 第一轮/ 第二轮/ 第三轮/                 # 各轮文献 PDF + 反馈
│
└── ZZ_待清理临时文件/                      # 误生成垃圾（0–8 字节），确认后可删
```
