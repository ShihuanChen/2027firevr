# -*- coding: utf-8 -*-
"""数字一致性总校验：以数据文件为唯一真值，检查所有文档里的口径是否与之一致。
用法：python check_consistency.py
"""
import csv,json,re,sys,os,glob
sys.stdout.reconfigure(encoding='utf-8')
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ev=list(csv.DictReader(open(os.path.join(ROOT,'05_编码包','编码集v4_事件.csv'),encoding='utf-8-sig')))
pk=list(csv.DictReader(open(os.path.join(ROOT,'05_编码包','输入包_编码集v4.csv'),encoding='utf-8-sig')))
lab=json.load(open(os.path.join(ROOT,'06_工作流产物','第17轮_终补搜与验证_20261022','参考标注_106.json'),encoding='utf-8'))
N_E,N_S=len(ev),len(pk)
oa=sum(1 for r in lab if r.get('off_axis')=='有')
main=sum(1 for r in ev if r['质量分层']=='主分析'); sup=sum(1 for r in ev if r['质量分层']=='补充')
single=sum(1 for r in ev if r['切片数']=='1')
truth=dict(事件=N_E,切片=N_S,标注=len(lab),主分析=main,补充=sup,off_axis=oa,off_pct=round(oa/N_S*100,1),单篇事件=single)
print('【真值】',truth)
ok=True
def chk(cond,msg):
    global ok
    print(('  PASS ' if cond else '  FAIL ')+msg); ok = ok and cond
chk(len(lab)==N_S, f'参考标注条数 {len(lab)} == 切片数 {N_S}')
chk(main+sup==N_E, f'主分析 {main} + 补充 {sup} == 事件数 {N_E}')
pairs={f'{truth["事件"]} 起事件 / {truth["切片"]} 篇', f'{truth["事件"]} 起 / {truth["切片"]} 篇',
       f'{truth["事件"]} 事件 / {truth["切片"]} 切片', f'{truth["事件"]} 起事件、{truth["切片"]} 篇切片'}
bad=[]
for p in glob.glob(os.path.join(ROOT,'**','*.md'),recursive=True):
    if '_archive' in p or '10_过程归档' in p or '对话历史' in p: continue
    t=open(p,encoding='utf-8').read()
    for m in re.finditer(r'(\d{2,3}) 起事件\s*/\s*(\d{2,3}) 篇', t):
        if int(m.group(1))!=N_E or int(m.group(2))!=N_S:
            bad.append((os.path.relpath(p,ROOT), m.group(0)))
chk(not bad, f'文档中的"X 起事件 / Y 篇"全部等于真值。不一致：{bad[:5]}')

# ---- 第 18 轮新增：补搜支线与全角斜杠口径 ----
RAW = [472-1, 88-1, 183-1, 195-1]   # 四份原始 csv 行数去表头
N_RAW = sum(RAW)
CAND = [59-1, 13-1, 13-1, 37-1]      # 四份候选 csv
N_CAND = sum(CAND)
n_sup = sum(1 for r in ev if r['来源'] in ('补搜新增', '第17轮补搜'))
n_orig = sum(1 for r in ev if r['来源'] == '原始库')
n_slice_orig = sum(int(r['切片数']) for r in ev if r['来源'] == '原始库')
n_slice_sup = sum(int(r['切片数']) for r in ev if r['来源'] in ('补搜新增', '第17轮补搜'))
pool = 125 + n_slice_sup
chk(N_RAW == 934, f'补搜原始记录 {N_RAW} == 934')
chk(N_CAND == 118, f'补搜候选 {N_CAND} == 118')
chk(n_sup == 44, f'补搜入集事件 {n_sup} == 44')
chk(n_orig == 59, f'原始库事件 {n_orig} == 59')
chk(n_slice_orig == 60, f'原始库切片 {n_slice_orig} == 60')
chk(n_slice_sup == 46, f'补搜切片 {n_slice_sup} == 46')
chk(pool == 171, f'汇合素材 {pool} == 171')
chk(pool - N_S == 65, f'主库事件归并合并篇数 {pool - N_S} == 65')
# 补搜支线的剔除数只能按篇算：118 - 46 = 72。写成 74 或 118-44 都是把事件当篇减
chk(N_CAND - n_slice_sup == 72, f'补搜剔除篇数 {N_CAND} - {n_slice_sup} == 72')
bad74 = [p for p in glob.glob(os.path.join(ROOT, '**', '*.md'), recursive=True)
         if '24_核查回应' not in p and ('剔 74' in open(p, encoding='utf-8').read()
                                        or '118 − 44' in open(p, encoding='utf-8').read())]
chk(not bad74, f'不得出现「剔 74」或「118 − 44」：{bad74}')
chk(round(oa/N_S*100,1) == 11.3, f'off_axis 占比 {round(oa/N_S*100,1)}% == 11.3%')

# 全角斜杠与"起／篇"写法也要查
pat = re.compile(r'(\d{2,3})\s*起事件?\s*[/／、]\s*(\d{2,3})\s*篇')
bad2 = []
for pth in glob.glob(os.path.join(ROOT,'**','*.md'),recursive=True):
    if '_archive' in pth or '10_过程归档' in pth or '对话历史' in pth: continue
    t = open(pth,encoding='utf-8').read()
    for m in pat.finditer(t):
        if int(m.group(1)) != N_E or int(m.group(2)) != N_S:
            bad2.append((os.path.relpath(pth,ROOT), m.group(0)))
chk(not bad2, f'全角写法一致。不一致：{bad2[:5]}')

print('\n结论：', '一致' if ok else '存在不一致，逐条修')
