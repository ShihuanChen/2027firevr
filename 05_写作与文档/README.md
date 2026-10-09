# 高层火灾新闻采集脚本

仓库包含用于收集与“高层火灾”相关新闻的脚本和依赖清单。

主要文件
- `scripts/collect_highrise_fires.py`: 主采集脚本（支持 Google News RSS + 可选 Bing News API）。
- `requirements.txt`: Python 依赖列表。

快速开始

1. 建议创建并激活 Python 虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 运行脚本（示例）：

```bash
python scripts/collect_highrise_fires.py --query "高层火灾" --start 2015-01-01 --end 2026-06-20 --max 1200 --output highrise_fires.csv
```

可选：使用 Bing News API 获取更多结果

1. 申请 Bing News API Key（Azure 或 Microsoft Cognitive Services）。
2. 在环境变量中设置 `BING_NEWS_KEY`，或通过 `--bing-key` 参数传入：

```bash
export BING_NEWS_KEY="your_key_here"  # Windows PowerShell: $Env:BING_NEWS_KEY="your_key_here"
python scripts/collect_highrise_fires.py --bing-key "$BING_NEWS_KEY" --max 2000 --output all.csv
```

注意与建议
- Google News RSS 返回的是近期聚合条目，单次请求数量有限；要收集千条以上新闻，建议分批按时间区间或多关键词循环查询并去重。
- 若需高吞吐量与完整正文抓取，建议配合代理池与并发爬虫，并遵守目标站点的 robots.txt 与使用条款。
- `newspaper3k` 用于提取正文并非必需，但能提升 `content` 字段质量；在部分站点上可能失败。

如果你愿意，我可以：
- 把脚本改为并发抓取并分段保存结果（按年或按月），方便合并成千条以上数据；
- 增加对 `NewsAPI.org` 的支持；
- 帮你用已有的 API Key（如果提供）跑一轮采集并返回样例 CSV。
