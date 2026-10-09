# -*- coding: utf-8 -*-
"""测试：跑 3 条看 API 与 prompt 是否正常"""
import pandas as pd, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

BASE_URL = "https://www.packyapi.ai/v1"
API_KEY = "sk-Dd6K9Rh5jLiVoB0EvIH0EvHl7k4jK40njDquw4FQ7BmUS2m1"
MODEL = "grok-4.5"

PROMPT = """你是新闻语料筛选器。判断这篇报道是否值得保留为 VR 高层火灾场景重建素材。

【保留标准（满足任一即 Y）】
I1 具身场景细节：正文含可被 VR 重建的空间/环境描写（楼梯、走廊、窗户、阳台、电梯、脚手架、浓烟、火焰蔓延、高温、能见度变化、逃生动作等）
I2 人物叙事：正文含具体人物的逃生/救援经历（谁在什么位置、做了什么动作：爬/跳/逃/被救/呼救、有何感受）

【排除标准（仅标题级判断）】
只有标题本身是纯伤亡通报/官方声明/纪念哀悼/法律进展/简报时才判 N。
注意：正文中出现 "officials said"、"memorial" 等词是新闻常态，不作为 N 的依据！只要正文有具身细节或人物叙事就判 Y。

输出格式（严格）：
判定: Y 或 N
理由: 一句话说明依据"""

def call_grok(title, body):
    text = f"标题：{title}\n正文：{body}"
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text},
        ],
        "max_tokens": 400,
        "temperature": 0.0,
    }
    req = urllib.request.Request(
        BASE_URL + "/chat/completions",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + API_KEY,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data["choices"][0]["message"]["content"]

pool = pd.read_csv('_第9轮_未判池.csv', encoding='utf-8-sig')
for i in range(3):
    row = pool.iloc[i]
    print(f'\n===== 测试 {i+1} gid={row["gid"]} =====')
    print('标题:', str(row['标题'])[:80])
    resp = call_grok(str(row['标题']), str(row['正文(前1200字)']))
    print('回复:', resp[:300])
