# -*- coding: utf-8 -*-
"""S1 v3: 串行分批版（稳定优先），每批20条，断点续传
原因：Windows 下 ThreadPoolExecutor 异常静默崩溃，改串行保证可追踪
"""
import pandas as pd, sys, os, time, json, re
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, urllib.error

BASE_URL = "https://www.packyapi.ai/v1"
API_KEY = "sk-Dd6K9Rh5jLiVoB0EvIH0EvHl7k4jK40njDquw4FQ7BmUS2m1"
MODEL = "grok-4.5"
MAX_TOKENS = 300
BATCH = 20
OUT_FILE = '_第9轮_grok语义.csv'
POOL_FILE = '_第9轮_未判池.csv'
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

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


def call_grok(title, body, retries=5):
    text = f"标题：{title}\n正文：{body}"
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text},
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.0,
    }
    last_err = ''
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                BASE_URL + "/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + API_KEY,
                    "User-Agent": UA,
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            last_err = f'HTTP_{e.code}'
            if e.code in (429, 503) and attempt < retries - 1:
                time.sleep(6 + attempt * 6)
                continue
            return f'__{last_err}__'
        except Exception as e:
            last_err = type(e).__name__
            if attempt < retries - 1:
                time.sleep(4)
                continue
            return f'__ERR_{last_err}__'


def parse(content):
    if content.startswith('__'):
        return 'E', content
    if '<think>' in content:
        content = content.split('</think>')[-1]
    m = re.search(r'判定\s*[:：]\s*(Y|N|y|n)', content)
    verdict = m.group(1).upper() if m else 'E'
    r = re.search(r'理由\s*[:：]\s*(.+)', content, re.S)
    reason = r.group(1).strip()[:150] if r else ''
    return verdict, reason


def main(limit=None):
    pool = pd.read_csv(POOL_FILE, encoding='utf-8-sig')
    pool['gid'] = pool['gid'].astype(str).str.strip()
    if limit:
        pool = pool.head(limit)
    print(f'本次池子: {len(pool)} 条', flush=True)

    done = {}
    if os.path.exists(OUT_FILE):
        df_done = pd.read_csv(OUT_FILE, encoding='utf-8-sig')
        df_done['gid'] = df_done['gid'].astype(str).str.strip()
        done = dict(zip(df_done['gid'], df_done['判定']))
        print(f'断点续传: 已有 {len(done)} 条', flush=True)

    remaining = pool[~pool['gid'].isin(done.keys())]
    print(f'待处理: {len(remaining)} 条', flush=True)

    results = [{'gid': k, '判定': v, '理由': ''} for k, v in done.items()]

    rows = list(remaining.iterrows())
    pos = 0
    total = len(rows)
    while pos < total:
        batch = rows[pos:pos + BATCH]
        print(f'--- 批 {pos//BATCH+1}/{(total+BATCH-1)//BATCH} ({pos}-{min(pos+BATCH,total)}) ---', flush=True)
        for idx, row in batch:
            gid = str(row['gid'])
            content = call_grok(str(row['标题']), str(row['正文(前1200字)']))
            if content.startswith('__'):
                time.sleep(4)
                content = call_grok(str(row['标题']), str(row['正文(前1200字)']))
            verdict, reason = parse(content)
            results.append({'gid': gid, '判定': verdict, '理由': reason})
            if len(results) % 20 == 0:
                print(f'  {len(results)} 条完成', flush=True)
        pd.DataFrame(results).to_csv(OUT_FILE, index=False, encoding='utf-8-sig')
        print(f'  批保存, 累计 {len(results)}', flush=True)
        pos += BATCH

    df_final = pd.DataFrame(results)
    df_final.to_csv(OUT_FILE, index=False, encoding='utf-8-sig')
    print('\n=== 完成 ===', flush=True)
    print('总数:', len(df_final), flush=True)
    print(df_final['判定'].value_counts().to_string(), flush=True)
    errs = df_final[df_final['判定'] == 'E']
    print('E 数:', len(errs), flush=True)


if __name__ == '__main__':
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit)
