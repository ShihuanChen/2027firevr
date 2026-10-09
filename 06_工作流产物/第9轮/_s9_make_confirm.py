# -*- coding: utf-8 -*-
"""S2: 生成第9轮待用户确认表（Y候选503条）+ 重试E条"""
import pandas as pd, sys, json, urllib.request, urllib.error, time
sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
KEY = 'sk-Ce0ocw6NDUyIzL3MmNpq9ABQiISH3bmyUIm6IRim5EknHsRw'

# 1) 读结果
res = pd.read_csv('_第9轮_grok语义.csv', encoding='utf-8-sig')
res['gid'] = res['gid'].astype(str).str.strip()
print('结果总数:', len(res))
print('Y:', (res['判定']=='Y').sum(), 'N:', (res['判定']=='N').sum(), 'E:', (res['判定']=='E').sum())

# 2) E 条信息
err = res[res['判定']=='E']
if len(err):
    print('\nE 条 gid:', err['gid'].tolist(), '理由:', err['理由'].tolist())

# 3) 读未判池正文，合并 Y 候选
pool = pd.read_csv('_第9轮_未判池.csv', encoding='utf-8-sig')
pool['gid'] = pool['gid'].astype(str).str.strip()
y = res[res['判定']=='Y'].copy()
y = y.merge(pool[['gid','标题','正文字数','正文(前1200字)']], on='gid', how='left')

# 4) 按正文字数降序（长文优先看）
y = y.sort_values('正文字数', ascending=False)
print('\nY 候选:', len(y))

# 5) 输出确认表（正文用前2000字）
def clip(text, n=2000):
    if pd.isna(text): return ''
    t = str(text).strip()
    return t[:n] + ('...' if len(t) > n else '')

out = pd.DataFrame({
    'gid': y['gid'],
    '标题': y['标题'],
    '正文字数': y['正文字数'],
    '正文(前2000字)': y['正文(前1200字)'].apply(clip),
    '用户判定1/0': '',
})
out.to_csv('_第9轮_待用户确认.csv', index=False, encoding='utf-8-sig')
print('已导出 _第9轮_待用户确认.csv:', len(out), '条')
print(out['正文字数'].describe().to_string())

# 6) E 条单独重试（正文截断到800字避免400）
if len(err):
    e_gid = err['gid'].iloc[0]
    erow = pool[pool['gid']==e_gid]
    if len(erow):
        r = erow.iloc[0]
        print(f'\n重试 E 条 {e_gid}: {str(r["标题"])[:60]}')
        body = str(r['正文(前1200字)'])[:800]
        PROMPT = '''你是新闻语料筛选器。判断这篇报道是否值得保留为 VR 高层火灾场景重建素材。
【保留标准（满足任一即 Y）】I1 具身场景细节：正文含可被 VR 重建的空间/环境描写（楼梯、走廊、窗户、阳台、电梯、浓烟、火焰蔓延、高温、能见度、逃生动作等）；I2 人物叙事：正文含具体人物的逃生/救援经历。
【排除标准（仅标题级判断）】只有标题本身是纯伤亡通报/官方声明/纪念哀悼/法律进展/简报时才判 N。
输出格式（严格）：判定: Y 或 N\n理由: 一句话'''
        payload = {'model': 'qwen3.5-flash', 'messages': [{'role':'system','content':PROMPT},{'role':'user','content':f'标题：{str(r["标题"])}\n正文：{body}'}], 'max_tokens': 300, 'temperature': 0.0}
        req = urllib.request.Request('https://www.packyapi.ai/v1/chat/completions',
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type':'application/json','Authorization':'Bearer '+KEY,'User-Agent':UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                content = data['choices'][0]['message']['content']
                print('重试成功:', content[:200])
                # 更新结果文件
                m = None
                import re
                mm = re.search(r'判定\s*[:：]\s*(Y|N|y|n)', content)
                if mm:
                    verdict = mm.group(1).upper()
                    res.loc[res['gid']==e_gid, '判定'] = verdict
                    res.to_csv('_第9轮_grok语义.csv', index=False, encoding='utf-8-sig')
                    print(f'已更新: gid {e_gid} -> {verdict}')
        except urllib.error.HTTPError as e2:
            print(f'重试仍失败: {e2.code}')
        except Exception as e3:
            print(f'重试异常: {type(e3).__name__} {str(e3)[:100]}')
