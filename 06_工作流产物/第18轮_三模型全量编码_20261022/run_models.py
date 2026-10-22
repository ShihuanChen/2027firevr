# -*- coding: utf-8 -*-
"""第18轮：三模型 × 106 篇全量编码

与 v4 单条提示词的差别（全部记录在 01_本轮变更说明.md）：
  1. 删除「F5、F6 在现有语料中为零，不要为了填满而误标」——该句是结果引导，
     会让模型主动回避 F5/F6，是 F6=0 的自证机制。
  2. 增加「正文可能因长度限制在 2000 字处截断」一句，避免把截断当成叙事缺陷。
  3. 全部 106 篇（103 起事件）一次性跑完，不再只跑 60 条。
  4. 落盘记录 model / 时间 / usage / 原始返回，任何一格可回溯。

用法：
  python run_models.py                 # 跑全部三模型
  python run_models.py haiku           # 只跑某一个
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

# 三家=同一厂商三个能力档，跨厂商锚点靠已有的 DeepSeek 60 条（见 05_跨厂商锚点.md）
MODELS = {
    'opus':   'claude-opus-5',
    'sonnet': 'claude-sonnet-5-5',
    'haiku':  'claude-haiku-4-5-20251001',
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

【字段二 · 机制 D，各取 有/无/未报告】
d1 线索确认解释：报道是否呈现「最初线索 → 当事人如何理解 → 是否被纠正」的完整过程
d2 动态可行动空间：可行动空间是否随火势、烟、构件或设施状态发生改变（写成序列）
d3 社会信息中介：危险信息是否经由他人或社会网络到达当事人
d4 社会行动支架：他人是否使原本不可行的行动变得可行（搀扶、背、带路、让进屋里）
d5 通道替代：视觉、听觉、触觉、社会通道之间是否发生过替代（看不见改听、听不见改看、走不了改被人搬）

【字段三 · 设计空间六轴，可多选，首个是主】
a 信息可达性
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

【输出格式】严格如下，一条 JSON 一行，键名不改、不增、不删：
{"id":"切片ID","p1":"","p2":"","p3":"","p4":"","p5":[],"d1":"","d2":"","d3":"","d4":"","d5":"","a":[],"b":[],"c":[],"d":[],"e":[],"f":[],"off_axis":"无","off_axis_note":"","evidence":[{"field":"a","quote":""}],"confidence":"high"}

【示例（此例不入数据集，仅示范格式与判定尺度）】
输入正文要点：五层旧楼，主逃生门被铁链锁死，其余出口上锁，灭火器被拆，消防水管改装为生活用水，楼梯间隔成住人房间。
输出：
{"id":"示例","p1":"记者旁观","p2":"受灾者","p3":"线性顺叙","p4":"逐句可重建","p5":["恐惧","愤怒"],"d1":"有","d2":"有","d3":"有","d4":"有","d5":"有","a":["A2","A5"],"b":["B5","B2"],"c":["C4","C6"],"d":["D5","D3"],"e":["E1","E5"],"f":["F1","F8"],"off_axis":"无","off_axis_note":"","evidence":[{"field":"c","quote":"the main escape door was chained shut"},{"field":"b","quote":"nobody came to warn us"}],"confidence":"high"}

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
    'd1': {'有', '无', '未报告'}, 'd2': {'有', '无', '未报告'}, 'd3': {'有', '无', '未报告'},
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


def load_key():
    cfg = json.load(open(CFG, encoding='utf-8'))
    return cfg[0]['apiKey'], cfg[0]['url'].rstrip('/')


def call(model, prompt, key, base, retries=3):
    body = json.dumps({
        'model': model, 'max_tokens': 1200, 'temperature': 0,
        'messages': [{'role': 'user', 'content': prompt}],
    }).encode()
    last = None
    for i in range(retries + 1):
        req = urllib.request.Request(base + '/messages', data=body, headers={
            'x-api-key': key, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
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
    only = sys.argv[1] if len(sys.argv) > 1 else None
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    key, base = load_key()
    rows = list(csv.DictReader(open(INP, encoding='utf-8-sig')))
    print(f'输入 {len(rows)} 篇', flush=True)

    for tag, model in MODELS.items():
        if only and only != tag:
            continue
        path = os.path.join(OUT, f'结果_{tag}.jsonl')
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
        print(f'[{tag}] {model} 已完成 {len(done)}，本轮待跑 {len(todo)}', flush=True)
        if not todo:
            continue

        def work(r):
            p = PROMPT.replace('{title}', r['标题']).replace('{body}', r['正文'])
            t0 = time.time()
            txt, usage, err = call(model, p, key, base)
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
