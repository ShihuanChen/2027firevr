# -*- coding: utf-8 -*-
"""调试 403：看 Cloudflare 拦截详情"""
import sys, json, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://www.packyapi.ai/v1"
API_KEY = "sk-Dd6K9Rh5jLiVoB0EvIH0EvHl7k4jK40njDquw4FQ7BmUS2m1"

payload = {
    "model": "grok-4.5",
    "messages": [{"role": "user", "content": "hi"}],
    "max_tokens": 10,
}
UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]
for ua in UAS:
    try:
        req = urllib.request.Request(
            BASE_URL + "/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + API_KEY,
                "User-Agent": ua,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Origin": "https://www.packyapi.ai",
                "Referer": "https://www.packyapi.ai/",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f'UA[{ua[:40]}...] -> OK', resp.read().decode()[:200])
            break
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:300]
        print(f'UA[{ua[:40]}...] -> {e.code}: {body}')
    except Exception as e:
        print(f'UA[{ua[:40]}...] -> ERR {type(e).__name__}: {str(e)[:150]}')
