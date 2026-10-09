# -*- coding: utf-8 -*-
"""S2: 第9轮 Grok 语义复核 —— 对未判池按编码手册 I1/I2 标准判定 Y/N
- 排除标准仅标题级（正文 officials said/memorial 等不作为 N 依据）
- 分批跑 + 断点续传（每批存 checkpoint）
"""
import pandas as pd, sys, os, time, json, re
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---- 配置 ----
BASE_URL = "https://www.packyapi.ai/v1"
API_KEY = "sk-Dd6K9Rh5jLiVoB0EvIH0EvHl7k4jK40njDquw4FQ7BmUS2m1"
MODEL = "grok-4.5"
BATCH = 50          # 每批条数
CONCURRENCY = 12    # 并发
MAX_TOKENS = 400
OUT_FILE = '_第9轮_grok语义.csv'
CKPT_FILE = '_第9轮_checkpoint.csv'
POOL_FILE = '_第9轮_未判池.csv'

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
        "max_tokens": MAX_TOKENS,
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
    content = data["choices"][0]["message"]["content"]
    return content


def parse(content):
    """从回复中提取 Y/N 和理由，跳过 <think> 块"""
    if '<think>' in content:
        content = content.split('</think>')[-1]
    m = re.search(r'判定\s*[:：]\s*(Y|N|y|n)', content)
    verdict = m.group(1).upper() if m else 'E'
    r = re.search(r'理由\s*[:：]\s*(.+)', content, re.S)
    reason = r.group(1).strip()[:200] if r else ''
    return verdict, reason


def run_batch(items):
    """串行跑一个批次（并发在外部线程池实现，这里先串行保证稳定）"""
    results = []
    for i, (idx, row) in enumerate(items):
        gid = str(row['gid'])
        title = str(row['标题'])
        body = str(row['正文(前1200字)'])
        try:
            content = call_grok(title, body)
            verdict, reason = parse(content)
            if verdict == 'E':
                # 重试一次
                content = call_grok(title, body)
                verdict, reason = parse(content)
        except Exception as e:
            verdict, reason = 'E', f'ERR: {str(e)[:100]}'
        results.append({'gid': gid, '判定': verdict, '理由': reason})
        # 打印进度
        if (i + 1) % 10 == 0:
            print(f'  batch内 {i+1}/{len(items)} 完成', flush=True)
        time.sleep(0.2)  # 限速
    return results


def main():
    pool = pd.read_csv(POOL_FILE, encoding='utf-8-sig')
    pool['gid'] = pool['gid'].astype(str).str.strip()
    print(f'未判池总数: {len(pool)}')

    # 断点续传：读取已完成的
    done = {}
    if os.path.exists(OUT_FILE):
        df_done = pd.read_csv(OUT_FILE, encoding='utf-8-sig')
        df_done['gid'] = df_done['gid'].astype(str).str.strip()
        done = dict(zip(df_done['gid'], df_done['判定']))
        print(f'已存在结果: {len(done)} 条')

    remaining = pool[~pool['gid'].isin(done)].copy()
    print(f'待处理: {len(remaining)} 条')

    all_results = [{'gid': k, '判定': v, '理由': ''} for k, v in done.items()]
    all_done_gids = set(done.keys())

    total = len(remaining)
    pos = 0
    while pos < total:
        batch = list(remaining.iloc[pos:pos+BATCH].iterrows())
        print(f'\n--- 批次 {pos//BATCH + 1}/{(total+BATCH-1)//BATCH} (处理 {pos}-{min(pos+BATCH,total)}) ---', flush=True)
        results = run_batch(batch)
        for r in results:
            all_results.append(r)
            all_done_gids.add(r['gid'])
        # 存 checkpoint
        df_out = pd.DataFrame(all_results)
        df_out.to_csv(OUT_FILE, index=False, encoding='utf-8-sig')
        pos += BATCH
        print(f'  已保存 {len(all_results)} 条到 {OUT_FILE}', flush=True)

    df_final = pd.DataFrame(all_results)
    df_final.to_csv(OUT_FILE, index=False, encoding='utf-8-sig')
    print('\n=== 完成 ===')
    print('总判定数:', len(df_final))
    print(df_final['判定'].value_counts().to_string())


if __name__ == '__main__':
    main()
