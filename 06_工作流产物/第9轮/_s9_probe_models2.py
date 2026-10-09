# -*- coding: utf-8 -*-
"""深度探测：models 原始返回 + 常见模型名直接试 chat"""
import sys, json, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
KEY = "sk-Dd6K9Rh5jLiVoB0EvIH0EvHl7k4jK40njDquw4FQ7BmUS2m1"
BASE = "https://www.packyapi.ai/v1"

# 1) models 原始响应
try:
    req = urllib.request.Request(BASE + "/models", headers={
        "Authorization": "Bearer " + KEY, "User-Agent": UA,
        "Accept": "application/json", "Origin": "https://www.packyapi.ai",
        "Referer": "https://www.packyapi.ai/",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode('utf-8')
        print('models 原始返回:', raw[:800])
except Exception as e:
    print('models 失败:', type(e).__name__, str(e)[:200])

# 2) 试常见模型名
for model in ["grok-4.5", "grok-4", "grok-3", "grok-3-mini", "grok-2", "grok-latest", "deepseek-v3", "deepseek-chat", "claude-3-5-sonnet", "gpt-4o"]:
    payload = {"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10}
    try:
        req = urllib.request.Request(BASE + "/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY,
                     "User-Agent": UA, "Accept": "application/json",
                     "Origin": "https://www.packyapi.ai", "Referer": "https://www.packyapi.ai/"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f'{model}: OK ->', resp.read().decode()[:120])
            break
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:150]
        print(f'{model}: {e.code} {body}')
    except Exception as e:
        print(f'{model}: ERR {type(e).__name__} {str(e)[:100]}')
