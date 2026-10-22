# -*- coding: utf-8 -*-
"""簇级 κ 重算：60 条切片样本的真实独立事件数远小于 60，
按真实事件簇聚合后重算逐轴 κ，检验"同事件多篇"是否抬高一致性。
"""
import json,csv,sys,os,collections
sys.stdout.reconfigure(encoding='utf-8')
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(os.path.dirname(HERE))
AX=['a','b','c','d','e','f']
def load(p):
    d={}
    for l in open(p,encoding='utf-8'):
        if l.strip():
            r=json.loads(l); d[r['id']]=r
    return d
A=load(os.path.join(ROOT,'05_编码包','_work','一致性v1','结果_模型A.jsonl'))
B=load(os.path.join(ROOT,'05_编码包','_work','一致性v1','结果_模型B.jsonl'))
meta={x['事件组ID']:x for x in json.load(open(os.path.join(os.path.dirname(ROOT),'_tmp','r2','unified3.json'),encoding='utf-8'))}
def cl(e):
    c=meta.get(e,{}).get('簇') or ''
    return c if c else e          # 无簇标的各自成簇
groups=collections.defaultdict(list)
for e in A: groups[cl(e)].append(e)
print('切片', len(A), '→ 真实事件簇', len(groups))
for k,v in sorted(groups.items(), key=lambda x:-len(x[1]))[:6]:
    print('   ', k, len(v))
def s(v):
    if v is None: return set()
    return {str(x).strip().upper() for x in v} if isinstance(v,list) else {str(v).strip().upper()}
def cohen(pa,pb):
    n=len(pa); po=sum(1 for x,y in zip(pa,pb) if x==y)/n
    ra=sum(pa)/n; rb=sum(pb)/n; pe=ra*rb+(1-ra)*(1-rb)
    return (1.0 if pe==1 else (po-pe)/(1-pe)), po, pe
def axis_kappa(lab1,lab2):
    ks=[]; detail={}
    tiers=sorted({t for v in list(lab1.values())+list(lab2.values()) for t in v})
    for t in tiers:
        pa=[1 if t in lab1[i] else 0 for i in lab1]
        pb=[1 if t in lab2[i] else 0 for i in lab2]
        if sum(pa)+sum(pb)==0: continue
        k,po,pe=cohen(pa,pb)
        ks.append(k); detail[t]=(round(k,3),round(po,3),round(2*po-1,3))
    return (sum(ks)/len(ks) if ks else 0), detail
# 切片级
slA={i:{t for ax in AX for t in s(A[i].get(ax))} for i in A}
slB={i:{t for ax in AX for t in s(B[i].get(ax))} for i in A}
out={'切片级':{}, '簇级':{}, '簇数':len(groups), '切片数':len(A)}
print('\n轴   切片级κ   簇级κ')
for ax in AX:
    la={i:s(A[i].get(ax)) for i in A}; lb={i:s(B[i].get(ax)) for i in A}
    k1,_=axis_kappa(la,lb)
    # 簇级：成员 ≥50% 出现的档
    ca={}; cb={}
    for g,mem in groups.items():
        for src,dst in ((A,ca),(B,cb)):
            cnt=collections.Counter(t for m in mem for t in s(src[m].get(ax)))
            dst[g]={t for t,c in cnt.items() if c>=len(mem)/2}
    k2,_=axis_kappa(ca,cb)
    out['切片级'][ax]=round(k1,3); out['簇级'][ax]=round(k2,3)
    print(f'{ax}    {k1:.3f}     {k2:.3f}')
json.dump(out,open(os.path.join(HERE,'簇级κ.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('\n写出 簇级κ.json')
