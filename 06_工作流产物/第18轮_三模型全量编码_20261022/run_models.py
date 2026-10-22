# -*- coding: utf-8 -*-
"""第18轮：三模型 × 106 篇全量编码

提示词版本 v4.2（本次修订，对应 Codebook v4.2 的三处判定线改法）：
  d1  加主体限定，拆成 d1（线索驱动）+ d1b（误判后纠正）
  d5  删「社会通道」，改封闭三清单 + 易混线
  a   改固定两步判定（先有无信号，再数来源）

相对 v4.1 的区别（全部记录在 README.md）：
  1. 删除「F5、F6 在现有语料中为零，不要为了填满而误标」——该句是结果引导，
     会让模型主动回避 F5/F6，是 F6=0 的自证机制。
  2. 增加「正文可能因长度限制在 2000 字处截断」一句，避免把截断当成叙事缺陷。
  3. 全部 106 篇（103 起事件）一次性跑完，不再只跑 60 条。
  4. 落盘记录 model / 时间 / usage / 原始返回，任何一格可回溯。
  5. 每条记录写入 prompt_ver，v4.1 与 v4.2 的结果不会混在一起算 κ。

出口协议（两家都支持，改 MODELS 里的 vendor 即可）：
  anthropic → POST {base}/messages        头 x-api-key
  openai    → POST {base}/chat/completions 头 Authorization: Bearer

用法：
  python run_models.py                       # 跑 MODELS 里全部模型
  python run_models.py haiku                 # 只跑某一个
  python run_models.py --show-prompt         # 只打印拼好的提示词，不调 API
  python run_models.py --probe               # 只测各模型通不通，不跑数据
"""
import os, sys, json, csv, time, threading, re
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, '_out')
os.makedirs(OUT, exist_ok=True)

INP = os.path.join(REPO, '05_编码包', '输入包_编码集v4.csv')
CFG = r'C:\Users\Administrator\.workbuddy\models.json'

PROMPT_VERSION = 'v4.2'

# (tag, model, vendor)；vendor 决定出口协议。
# 现状：packyapi 对本机 IP 全部 Claude 模型返回 403 region_restricted，
# 换成任意 OpenAI 兼容出口（deepseek / qwen / moonshot / openai）改这里即可，脚本其余不动。
MODELS = {
    'opus':   ('claude-opus-5', 'anthropic'),
    'sonnet': ('claude-sonnet-5-5', 'anthropic'),
    'haiku':  ('claude-haiku-4-5-20251001', 'anthropic'),
}

PROMPT = '''你是建筑火灾新闻的系统编码员。我会给你一条新闻的标题与正文，你输出一个 JSON 对象，一条一行，不要任何解释文字、不要 markdown 代码块。

【四条铁律】
1. 只依据本条正文判定。正文没写的填「未报告」，禁止用常识、外部知识或其他条目的内容补全。
2. 每个非「未报告」的判定，必须配一句正文逐字摘录（≤30 字）。摘不出来就退回「未报告」。
3. off_axis 只做整篇判断，不做单段判断。只有当整篇报道都不包含任何当事人的火灾过程时才填 off_axis="有"，且 off_axis_note 必须以四类之一开头：
   伤亡通报／司法追责／纯科普／灾后追访／演播室口播（五选一，后接一句话说明）。
   只要正文里有任何一位当事人经历了火灾过程（发现、判断、行动、被困、获救），一律填 off_axis="无"。
   某一段、某一句话归不进六轴，不构成 off_axis="有"；那一段跳过即可，其余照常判定。
   注意 off_axis 与六轴不互斥：整篇没有当事人过程，仍可能从旁证里判出一两条六轴信息，能判就判，判不出就留空。
4. 不确定就填 confidence="low"，不要为了让字段非空而猜。

【关于正文长度】
输入正文可能因长度限制在 2000 字处被截断。截断是采集限制，不是叙事缺陷：只对已出现的文字判定，不要因为末尾突兀就整体降为 low。

【字段一 · 叙事 P，各取一值】
p1 人称：第一人称自述 / 记者旁观 / 官方通稿 / 混合
p2 立场：受灾者 / 救援者 / 管理者 / 旁观者 / 混合
p3 结构：线性顺叙 / 倒叙 / 多线并置 / 时间戳分段
p4 颗粒度：逐句可重建 / 段落级概括 / 只有结论
p5 情感：恐惧 / 无助 / 愤怒 / 悲痛 / 感激 / 麻木 / 未呈现（可多选）

【字段二 · 机制 D，各取 有/无/未报告，d1 除外】
d1 线索驱动：**只看当事人本人**。正文里有没有出现「当事人接收到某个线索（看到烟、闻到味、听到喊、感觉烫）
    → 并且据此改变了行动」这一条链。只要求「线索 → 行动」，**不要求**写出误判或纠正。
   主体限定：警察在调查、消防到场、官方通报、邻居闻到、记者描述现场情况，一律不算 d1——
   那些不是当事人的经历，即使写得很详细也不算。
   取值：线索驱动 / 无 / 未报告
   - 线索驱动：当事人接收到线索并据此行动（跑、躲、喊人、下楼，都算行动）
   - 无：写了当事人，但当事人是被直接告知或被别人带走，正文没有他自己感知线索的环节
   - 未报告：正文没写当事人本人的感知与行动
d1b 误判后纠正：只在 d1="线索驱动" 时判。正文是否明写「先理解成别的东西，后来才改过来」
   （以为是做饭、以为是演习、以为火在别处、以为警报误响）。
   - 有：明写了先错后改    - 无：线索直接理解对，没有误判环节
   - d1 不是「线索驱动」时，d1b 一律填「未报告」

d2 动态可行动空间：可行动空间是否随火势、烟、构件或设施状态发生改变（写成序列）
d3 社会信息中介：危险信息是否经由他人或社会网络到达当事人
d4 社会行动支架：他人是否使原本不可行的行动变得可行（搀扶、背、带路、让进屋里）
d5 通道替代：当事人的**接收通道**是否发生过替代。只承认以下三种，**封闭清单，不在清单里的一律填「无」**：
   - 视→听：看不见（烟遮、断电、无窗、走廊全黑），改靠声音判断方向或位置
   - 听→视：听不见（警报不响、有听力障碍、环境太吵），改靠看烟、看火光、看人往哪跑
   - 行动→被搬：自己走不了或走不动，改由他人背负、搀扶、抬运
   **不算 d5 的五种情形**（这是最容易误标的地方，逐条排除）：
   - 通知、告知、敲门、打电话告诉别人 → 记 d3 或 b 轴，不记 d5
   - 向外求救、挥衣物、打手电、喊救命 → 这是发出信号，不是接收替代，不记 d5
   - 走楼梯、走消防梯、坐电梯、跑出去 → 这是 c／d 轴，不记 d5
   - 消防员到场救人、架云梯、剪防盗网 → 这是救援行动，不记 d5
   - 携带物品、抱宠物、拿行李 → 与通道无关，不记 d5

【字段三 · 设计空间六轴，可多选，首个是主】
a 信息可达性 —— **按固定两步判定，不许跳步、不许并列选**
  第一步：问「有没有任何信号到达当事人」。
     一个都没有 → A5（没有任何可用于判定着火的信号），本轴到此为止，不再往下判。
     有 → 进第二步。
  第二步：问「信号来自几个彼此独立的来源」（来源 = 警报、广播、邻居敲门、可见烟、火光、喊叫、电话通知）。
     只有一个来源，或其余来源都失效 → A2（只有一条通道有效）
     两个及以上同时有效 → A1（至少两条独立通道同时有效）
  第三步（叠加判断，只在第一、二步已定 A1 或 A2 时做）：
     构件挡住视线或阻断感知（泡棉封窗、无窗走廊、施工围挡、门缝封死）→ 加 A3
     信号到了但被当事人按日常经验解释成无害（以为是灰尘、以为是做饭）→ 加 A4
  输出时主干档（A5 或 A2 或 A1）必须排在数组第一个。
  A1 至少两条独立通道同时有效（警报+广播+邻居敲门+可见烟）
  A2 只有一条通道有效，其余失效或不存在
  A3 构件挡住视线或阻断感知（泡棉封窗、无窗走廊、施工围挡、门缝封死）
  A4 有信号但被当事人按日常经验解释成无害（以为是灰尘、以为是做饭）
  A5 没有任何可用于判定着火的信号（闻到异味但查不出源、警报不响、无人告知）
b 确认的社会性
  B1 当事人靠自身感官或亲自行动完成确认，无他人介入
  B2 由具体某个他人告知（邻居、朋友、家人、保安）
  B3 通过群聊、门铃摄像头、社交平台等中介化渠道获知
  B4 由建筑广播、警报系统、官方通知统一发布
  B5 无人告知、无警报、无人敲门，始终未获正式确认
c 可行动集
  C1 楼梯、出口、避难层均可用，无阻断
  C2 只有一条路径，且通行能力受限（宽度、容量）
  C3 路径物理上存在，但当事人身体条件不足以使用
  C4 路径存在但被上锁、铁链、堆物、工程封闭
  C5 路径已被烟充满或成为烟囱，走进去等于进入危险
  C6 所有路径同时不可用，只剩跳楼、悬空等极端选择
d 决策指向
  D1 向下撤离（楼梯或电梯向下离开建筑）
  D2 向上走、上天台、上避难层
  D3 留在房间内关门堵缝、等待救援
  D4 跨户、跨楼、跨阳台移动
  D5 跳楼、悬于窗外、攀爬外立面等非常规离楼
e 能动性来源
  E1 当事人自行判断并自行决定
  E2 行动由他人劝说、带领、搀扶促成
  E3 判断被外部指令替代（接警员、调度、远程指导）
  E4 在等通知、等警报、等指令，行动被制度时序拖住
  E5 官方信号或指令本身使当事人做出错误判断（被告知没事、警报被关闭）
f 处境主体
  F1 普通成人（无特殊身体或社会条件限制）
  F2 老年（明确写年龄或 elderly）
  F3 儿童（未成年，含婴幼儿）
  F4 轮椅或行动不便（依赖轮椅、助行器、卧床）
  F5 视障（明确视力障碍）
  F6 听障（明确听力障碍，或依赖视觉警报）
  F7 孕妇或怀抱婴幼儿
  F8 独居（明确独居、无人可求助）

【易混判定线，务必分清】
A3 是感知被挡；A4 是感知到了但解释错；A5 是没有可用感知。
C3 是门开着但身体过不去；C4 是被外力锁住；C5 是路在但走进去会死；C6 是前几类同时发生导致路径总数为零。
D2 与 D3 同时出现时，看当事人身体最终停在哪里。
E4 是没等到；E5 是等到了错的。
d1 是当事人**自己**感知到线索并因此行动；d3 是**别人**把危险信息送到当事人面前。二者可同时为「有」，但不要互相顶替。
d1b 只问「有没有先错后改」；没有误判不等于 d1 为「无」。

【输出格式】严格如下，一条 JSON 一行，键名不改、不增、不删：
{"id":"切片ID","p1":"","p2":"","p3":"","p4":"","p5":[],"d1":"","d1b":"","d2":"","d3":"","d4":"","d5":"","a":[],"b":[],"c":[],"d":[],"e":[],"f":[],"off_axis":"无","off_axis_note":"","evidence":[{"field":"a","quote":""}],"confidence":"high"}

【示例（此例不入数据集，仅示范格式与判定尺度）】
输入正文要点：五层旧楼，主逃生门被铁链锁死，其余出口上锁，灭火器被拆，消防水管改装为生活用水，楼梯间隔成住人房间。
输出：
{"id":"示例","p1":"记者旁观","p2":"受灾者","p3":"线性顺叙","p4":"逐句可重建","p5":["恐惧","愤怒"],"d1":"线索驱动","d1b":"无","d2":"有","d3":"有","d4":"有","d5":"无","a":["A2","A5"],"b":["B5","B2"],"c":["C4","C6"],"d":["D5","D3"],"e":["E1","E5"],"f":["F1","F8"],"off_axis":"无","off_axis_note":"","evidence":[{"field":"c","quote":"the main escape door was chained shut"},{"field":"b","quote":"nobody came to warn us"}],"confidence":"high"}
（上例中 d5 填「无」是刻意的：被锁住的门属于 c 轴 C4，不是通道替代。走楼梯、被人叫醒、消防到场，也都不记 d5。）

现在开始，只输出 JSON：
标题：{title}
正文：{body}
'''

VALID = {
    'p1': {'第一人称自述', '记者旁观', '官方通稿', '混合'},
    'p2': {'受灾者', '救援者', '管理者', '旁观者', '混合'},
    'p3': {'线性顺叙', '倒叙', '多线并置', '时间戳分段'},
    'p4': {'逐句可重建', '段落级概括', '只有结论'},
    'p5': {'恐惧', '无助', '愤怒', '悲痛', '感激', '麻木', '未呈现'},
    'd1': {'线索驱动', '无', '未报告'}, 'd1b': {'有', '无', '未报告'},
    'd2': {'有', '无', '未报告'}, 'd3': {'有', '无', '未报告'},
    'd4': {'有', '无', '未报告'}, 'd5': {'有', '无', '未报告'},
    'a': {'A1', 'A2', 'A3', 'A4', 'A5'},
    'b': {'B1', 'B2', 'B3', 'B4', 'B5'},
    'c': {'C1', 'C2', 'C3', 'C4', 'C5', 'C6'},
    'd': {'D1', 'D2', 'D3', 'D4', 'D5'},
    'e': {'E1', 'E2', 'E3', 'E4', 'E5'},
    'f': {'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'},
}
MULTI = {'p5', 'a', 'b', 'c', 'd', 'e', 'f'}
LOCK = threading.Lock()


def load_key(idx=0):
    cfg = json.load(open(CFG, encoding='utf-8'))
    c = cfg[idx]
    return c['apiKey'], c['url'].rstrip('/')


def call(model, prompt, key, base, retries=3, vendor='anthropic'):
    """vendor='anthropic' 走 /messages；vendor='openai' 走 /chat/completions。"""
    if vendor == 'openai':
        body = json.dumps({
            'model': model, 'max_tokens': 1200, 'temperature': 0,
            'messages': [{'role': 'user', 'content': prompt}],
        }).encode()
        url, headers = base + '/chat/completions', {
            'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
    else:
        body = json.dumps({
            'model': model, 'max_tokens': 1200, 'temperature': 0,
            'messages': [{'role': 'user', 'content': prompt}],
        }).encode()
        url, headers = base + '/messages', {
            'x-api-key': key, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'}
    last = None
    for i in range(retries + 1):
        req = urllib.request.Request(url, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            if vendor == 'openai':
                ch = d.get('choices') or [{}]
                txt = (ch[0].get('message') or {}).get('content', '') or ''
                return txt, d.get('usage', {}), None
            txt = ''.join(b.get('text', '') for b in d.get('content', []) if b.get('type') == 'text')
            return txt, d.get('usage', {}), None
        except Exception as e:
            last = f'{type(e).__name__}: {e} ' + str(getattr(e, 'read', lambda: b'')()[:200])
            time.sleep(5 + 6 * i)
    return None, None, last


def extract_json(txt):
    if not txt:
        return None, 'empty'
    t = txt.strip()
    t = re.sub(r'^```(?:json)?', '', t).strip()
    t = re.sub(r'```$', '', t).strip()
    try:
        return json.loads(t), None
    except Exception:
        pass
    m = re.search(r'\{.*\}', t, re.S)
    if m:
        try:
            return json.loads(m.group(0)), None
        except Exception as e:
            return None, f'parse: {e}'
    return None, 'no-brace'


def norm(rec, sid):
    out, bad = {}, []
    rec['id'] = sid
    out['id'] = sid
    for f, allowed in VALID.items():
        v = rec.get(f)
        if f in MULTI:
            if v is None:
                v = []
            if isinstance(v, str):
                v = [x for x in re.split(r'[;,、/]', v) if x.strip()]
            vals = [str(x).strip() for x in v if str(x).strip()]
            vals = [x for x in vals if x in allowed]
            out[f] = vals
        else:
            s = str(v).strip() if v is not None else ''
            out[f] = s if s in allowed else '未报告'
            if s not in allowed and s:
                bad.append(f'{f}={s}')
    # d1b 与 d1 的硬校验：d1 不是「线索驱动」时，d1b 不存在
    if out.get('d1') != '线索驱动':
        out['d1b'] = '未报告'
    elif out.get('d1b') not in ('有', '无'):
        out['d1b'] = '未报告'

    note = str(rec.get('off_axis_note', ''))[:200]
    oa = rec.get('off_axis', '无') if rec.get('off_axis') in ('有', '无') else '无'
    CATS = ('伤亡通报', '司法追责', '纯科普', '灾后追访', '演播室口播')
    if oa == '有' and not any(c in note for c in CATS):
        oa = '无'          # 说不出属于哪一类，就不算整篇装不进
    out['off_axis'] = oa
    out['off_axis_note'] = note
    ev = rec.get('evidence') or []
    out['evidence'] = [{'field': str(e.get('field', '')), 'quote': str(e.get('quote', ''))[:80]}
                       for e in ev if isinstance(e, dict)][:12]
    out['confidence'] = rec.get('confidence') if rec.get('confidence') in ('high', 'low') else 'low'
    return out, bad


def main():
    args = [a for a in sys.argv[1:]]
    rows = list(csv.DictReader(open(INP, encoding='utf-8-sig')))

    if '--show-prompt' in args:
        r = rows[0]
        print(PROMPT.replace('{title}', r['标题']).replace('{body}', r['正文']))
        return

    if '--probe' in args:
        key, base = load_key()
        for tag, (model, vendor) in MODELS.items():
            txt, _, err = call(model, '只回复 ok 两个字母', key, base, retries=0, vendor=vendor)
            print(f'[{tag}] {model} ({vendor}) → {"OK " + txt.strip()[:20] if txt else "FAIL " + str(err)[:160]}')
        return

    only = args[0] if args and not args[0].startswith('--') else None
    limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
    key, base = load_key()
    print(f'输入 {len(rows)} 篇 · 提示词 {PROMPT_VERSION}', flush=True)

    for tag, (model, vendor) in MODELS.items():
        if only and only != tag:
            continue
        # v4.2 结果单独落盘：v4.1 的 78 条不与本版混算 κ
        path = os.path.join(OUT, f'结果_{tag}_{PROMPT_VERSION}.jsonl')
        done = set()
        if os.path.exists(path):
            for line in open(path, encoding='utf-8'):
                try:
                    o = json.loads(line)
                    if o.get('ok'):
                        done.add(o['id'])
                except Exception:
                    pass
        todo = [r for r in rows if r['切片ID'] not in done]
        if limit:
            todo = todo[:limit]
        print(f'[{tag}] {model} ({vendor}) 已完成 {len(done)}，本轮待跑 {len(todo)}', flush=True)
        if not todo:
            continue

        def work(r, model=model, vendor=vendor, tag=tag):
            p = PROMPT.replace('{title}', r['标题']).replace('{body}', r['正文'])
            t0 = time.time()
            txt, usage, err = call(model, p, key, base, vendor=vendor)
            rec, perr = extract_json(txt)
            if rec is None:
                return {'id': r['切片ID'], 'model': model, 'ok': False, 'err': err or perr,
                        'raw': (txt or '')[:2000]}
            clean, bad = norm(rec, r['切片ID'])
            axes_any = any(clean[f] for f in ('a', 'b', 'c', 'd', 'e', 'f'))
            if not axes_any and clean['off_axis'] != '有':
                return {'id': r['切片ID'], 'model': model, 'ok': False, 'err': 'axis-empty',
                        'raw': (txt or '')[:2000]}

            clean.update({'model': model, 'tag': tag, 'ok': True, 'sec': round(time.time() - t0, 1),
                          'prompt_ver': PROMPT_VERSION,
                          'usage': usage, 'invalid': bad, 'raw': (txt or '')[:3000],
                          'ts': time.strftime('%Y-%m-%dT%H:%M:%S')})
            return clean

        ok = fail = 0
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs = {ex.submit(work, r): r for r in todo}
            for i, fu in enumerate(as_completed(futs), 1):
                out = fu.result()
                with LOCK:
                    with open(path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(out, ensure_ascii=False) + '\n')
                if out.get('ok'):
                    ok += 1
                else:
                    fail += 1
                    print(f'  ! {out["id"]} {out.get("err")}', flush=True)
                if i % 20 == 0:
                    print(f'  [{tag}] {i}/{len(todo)} ok={ok} fail={fail}', flush=True)
        print(f'[{tag}] 完成 ok={ok} fail={fail}', flush=True)


if __name__ == '__main__':
    main()
