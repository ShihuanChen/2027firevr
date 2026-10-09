# -*- coding: utf-8 -*-
"""探测可用模型：packyapi models 列表 + 测试备用key"""
import sys, json, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def get(url, key, hdr_extra=None):
    headers = {
        "Authorization": "Bearer " + key,
        "User-Agent": UA,
        "Accept": "application/json",
    }
    if hdr_extra:
        headers.update(hdr_extra)
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1) packyapi 模型列表
try:
    data = get("https://www.packyapi.ai/v1/models", "sk-Dd6K9Rh5jLiVoB0EvIH0EvHl7k4jK40njDquw4FQ7BmUS2m1")
    ids = [m['id'] for m in data.get('data', [])]
    print('packyapi 可用模型:', ids[:30])
except Exception as e:
    print('packyapi models 查询失败:', type(e).__name__, str(e)[:200])
