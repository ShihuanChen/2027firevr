# -*- coding: utf-8 -*-
"""测试备用混元 key（OpenAI 兼容尝试 + 腾讯云混元原生格式）"""
import sys, json, urllib.request, urllib.error, hashlib, hmac, time
sys.stdout.reconfigure(encoding='utf-8')

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# 混元 key（config.yaml）
AK = "ak-20260714-938aa34ae2a4e4ecef85005c1c8af514"
SK = "sk-Tl0lZC03nzqJYiLY11OYIonMBWmV347hNgJZvSnnFNkrrUaE"

# 尝试1：OpenAI 兼容聚合网关（可能是 one-api/new-api 形式）
for base in ["https://api.hunyuan.cloud.tencent.com/v1", "https://hunyuan.cloud.tencent.com/v1"]:
    try:
        payload = {"model": "hunyuan-turbo", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10}
        req = urllib.request.Request(base + "/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + SK,
                     "User-Agent": UA, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f'{base}: OK ->', resp.read().decode()[:200])
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:200]
        print(f'{base}: {e.code} {body}')
    except Exception as e:
        print(f'{base}: ERR {type(e).__name__} {str(e)[:120]}')

# 尝试2：智谱旧 key（之前余额不足）
try:
    payload = {"model": "glm-5.1", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10}
    req = urllib.request.Request("https://open.bigmodel.cn/api/paas/v4/chat/completions",
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json", "Authorization": "Bearer f373e63981aa499abbc8eeec1c682808.e87pBnU9Kjy8gDrW",
                 "User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        print(f'zhipu glm-5.1: OK ->', resp.read().decode()[:200])
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')[:200]
    print(f'zhipu glm-5.1: {e.code} {body}')
except Exception as e:
    print(f'zhipu glm-5.1: ERR {type(e).__name__} {str(e)[:120]}')
