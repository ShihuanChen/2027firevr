# -*- coding: utf-8 -*-
"""S1: 第9轮 Grok 语义复核 —— 并发版，带503重试和断点续传
对未判池 1,155 条按编码手册 I1/I2 标准判 Y/N，排除标准仅标题级
"""
import pandas as pd, sys, os, time, json, re
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://www.packyapi.ai/v1"
API_KEY = "sk-Dd6K9Rh5jLiVoB0EvIH0EvHl7k4jK40njDquw4FQ7BmUS2m1"
MODEL = "grok-4.5"
MAX_TOKENS = 300
CONCURRENCY = 8
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


def call_grok(title, body, retries=4):
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
            if e.code in (429, 503) and attempt < retries - 1:
                time.sleep(5 + attempt * 5)  # 限流等待
                continue
            return f'__HTTP_{e.code}__'
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)
                continue
            return f'__ERR_{type(e).__name__}__'


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


def process_one(row):
    gid = str(row['gid'])
    title = str(row['标题'])
    body = str(row['正文(前1200字)'])
    content = call_grok(title, body)
    if content.startswith('__'):
        # 失败重试一次
        time.sleep(3)
        content = call_grok(title, body)
    verdict, reason = parse(content)
    return {'gid': gid, '判定': verdict, '理由': reason}


def main():
    pool = pd.read_csv(POOL_FILE, encoding='utf-8-sig')
    pool['gid'] = pool['gid'].astype(str).str.strip()
    print(f'未判池总数: {len(pool)}')

    # 断点续传
    done = {}
    if os.path.exists(OUT_FILE):
        df_done = pd.read_csv(OUT_FILE, encoding='utf-8-sig')
        df_done['gid'] = df_done['gid'].astype(str).str.strip()
        done = dict(zip(df_done['gid'], df_done['判定']))
        print(f'已存在结果: {len(done)} 条')

    remaining = pool[~pool['gid'].isin(done.keys())]
    print(f'待处理: {len(remaining)} 条')

    results = [{'gid': k, '判定': v, '理由': ''} for k, v in done.items()]

    if len(remaining) == 0:
        print('全部已完成')
    else:
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
            futures = {ex.submit(process_one, row): idx for idx, row in remaining.iterrows()}
            n_done = 0
            for fut in as_completed(futures):
                results.append(fut.result())
                n_done += 1
                if n_done % 50 == 0:
                    df_tmp = pd.DataFrame(results)
                    df_tmp.to_csv(OUT_FILE, index=False, encoding='utf-8-sig')
                    print(f'  {n_done}/{len(remaining)} 完成, 已存checkpoint', flush=True)

    df_final = pd.DataFrame(results)
    df_final.to_csv(OUT_FILE, index=False, encoding='utf-8-sig')
    print('\n=== 完成 ===')
    print('总判定数:', len(df_final))
    print(df_final['判定'].value_counts().to_string())
    errs = df_final[df_final['判定'] == 'E']
    print('E 错误数:', len(errs))
    if len(errs):
        print('E 样例:', errs['理由'].head(5).tolist())


if __name__ == '__main__':
    main()
