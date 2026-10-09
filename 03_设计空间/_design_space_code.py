# -*- coding: utf-8 -*-
import json, re, collections

BASE='D:/BaiduSyncdisk/chi2027/朱倩/工作流/'
j=json.load(open(BASE+'_tmp_records.json',encoding='utf-8'))
ff=json.load(open(BASE+'_tmp_fields.json',encoding='utf-8'))
data=j['data']; fidlist=data['field_id_list']; recs=data['data']; rids=data['record_id_list']
fmap={f['id']:f['name'] for f in ff['data']['fields']}
def rec(i): return {fmap.get(fidlist[k]):recs[i][k] for k in range(len(fidlist))}

# ---------- helpers ----------
def get(m,key):
    v=m.get(key)
    return v if isinstance(v,str) else ('' if v is None else str(v))
def toks(s):
    return [t.strip() for t in re.split(r'[,，、/]', s) if t.strip()] if s else []

_zh_pat=None
def has_zh(text,*words):
    return any(w in text for w in words)
_en_pat=None
def has_en(text,*words):
    t=text.lower()
    for w in words:
        if re.search(r'(?<![a-z])'+re.escape(w.lower())+r'(?![a-z])', t):
            return True
    return False

# ---------- allowed options ----------
ALLOWED={
 '叙事视角':['幸存者第一人称','目击者/邻居','救援者','家属/亲友','官方/媒体全知','混合/多视角'],
 '时间结构':['单点瞬间','完整逃生序列','灾后回顾','多时间线交织'],
 '身体主体':['普通成年人','老年人','儿童','轮椅使用者','视障者','听障者','拄拐/助行器','孕妇/抱婴者','宠物','救援者'],
 '感官主导':['视觉','听觉','触觉/温度','运动/前庭','嗅觉暗示'],
 '核心冲突':['逃生vs被困','自救vs互救','信息缺失/警报延迟','时间压力','建筑/设施缺陷','身体限制vs环境障碍'],
 '情感弧线':['恐惧→绝望→获救','恐慌→互助→平静','悲伤/哀悼','愤怒/追责','温情/希望','混合/复杂'],
 '叙事颗粒度':['动作级','场景级','情绪级','数据级'],
 '交互_身体化角色':['陈伯（老年）','阿May（听障）','罗姐（轮椅）','威廉（视障）','King仔（儿童）','阿福（拄拐）','普通成年人','救援者','旁观者'],
 '交互_移动方式':['自由行走','瞬移/节点跳转','受限移动（轮椅/拄拐/爬行）','固定点位','引导路径'],
 '交互_交互动词':['开门/破门','敲門/拍門示警','呼救/拨打119','匍匐/爬行','攀爬/结绳下滑','捂口鼻/湿毛巾','按火警按钮','抱/牵儿童或宠物','推轮椅/协助残障','破窗/跳窗','关闭防火门'],
 '交互_视角转换':['身体替换','时间回放','上帝视角/俯瞰','同步多视角','角色切换','无转换'],
 '交互_共情机制':['感知剥夺','身体限制模拟','时间压力','社会见证','后果呈现','道德选择','亲密关联'],
 '交互_沉浸反馈':['空间音频','视觉遮挡','温度/震动','手柄/触觉阻力','心跳/呼吸UI','字幕/手语/振动提示'],
 '交互_场景控制':['线性叙事','分支选择','沙盒探索','重复训练/纠错','博物馆/纪念碑陈列'],
 '交互_社交共在':['单人','NPC协作/求助','多人协作逃生','旁观者视角'],
}

def clean(vals, field):
    if field not in ALLOWED:
        return vals
    if isinstance(vals,str):
        return vals if vals in ALLOWED[field] else None
    out=[v for v in vals if v in ALLOWED[field]]
    return out

# ---------- persona detection ----------
def personas(m):
    text=get(m,'正文/摘要')+' '+get(m,'标题')
    B=get(m,'SAVTBC_B身体'); C=get(m,'SAVTBC_C社交')
    bodies=set(); roles=set()
    if '老年人' in C or '老年人步速' in B: bodies.add('老年人'); roles.add('陈伯（老年）')
    if '儿童' in C or '儿童身体限制' in B: bodies.add('儿童'); roles.add('King仔（儿童）')
    if '轮椅' in C or '轮椅' in B: bodies.add('轮椅使用者'); roles.add('罗姐（轮椅）')
    if '视觉障碍' in B: bodies.add('视障者'); roles.add('威廉（视障）')
    if '宠物' in C: bodies.add('宠物')
    if '救援者' in C: bodies.add('救援者'); roles.add('救援者')
    if has_zh(text,'听障','聋') or has_en(text,'deaf','hearing impaired','hearing loss'):
        bodies.add('听障者'); roles.add('阿May（听障）')
    if has_zh(text,'拐杖','助行器','拄拐') or has_en(text,'cane','crutch','walker'):
        bodies.add('拄拐/助行器'); roles.add('阿福（拄拐）')
    if has_zh(text,'孕妇') or has_en(text,'pregnant','expectant'):
        bodies.add('孕妇/抱婴者')
    if '残障者' in C and not bodies.intersection({'视障者','听障者','轮椅使用者','拄拐/助行器'}):
        # generic disability, try text
        if has_en(text,'blind','visually impaired') or has_zh(text,'失明','盲人'):
            bodies.add('视障者'); roles.add('威廉（视障）')
        elif has_en(text,'deaf') or has_zh(text,'聋','听障'):
            bodies.add('听障者'); roles.add('阿May（听障）')
        else:
            bodies.add('视障者'); roles.add('威廉（视障）')  # fallback, noted
    if not bodies:
        bodies.add('普通成年人'); roles.add('普通成年人')
    return sorted(bodies), sorted(roles)

# ---------- main coder ----------
def code_one(m):
    text=get(m,'正文/摘要')+' '+get(m,'标题')
    S=get(m,'SAVTBC_S空间'); A=get(m,'SAVTBC_A声音'); V=get(m,'SAVTBC_V视觉')
    T=get(m,'SAVTBC_T时间'); B=get(m,'SAVTBC_B身体'); C=get(m,'SAVTBC_C社交')
    St=toks(S); At=toks(A); Vt=toks(V); Tt=toks(T); Bt=toks(B); Ct=toks(C)
    out={}

    # 身体主体 + 交互_身体化角色 + 视角(身体替换)
    bodies,roles=personas(m)
    out['身体主体']=bodies
    out['交互_身体化角色']=roles

    # 感官主导
    sens=set()
    if Vt: sens.add('视觉')
    if At: sens.add('听觉')
    if any(x in Bt for x in ['高温','灼热','触觉障碍','跌倒','烟雾刺激','体力耗尽']): sens.add('触觉/温度')
    if any(x in Bt for x in ['跌倒','体力耗尽','老年人步速','儿童身体限制']) or any(x in St for x in ['楼梯间','逃生口','电梯']): sens.add('运动/前庭')
    if '浓烟灌满' in St or '浓烟滚滚' in Vt or has_en(text,'smell','odor') or has_zh(text,'气味','烟味'): sens.add('嗅觉暗示')
    if not sens: sens.add('视觉')
    out['感官主导']=sorted(sens)

    # 叙事视角
    if has_en(text,'i was','we were','i escaped','we escaped','my family','i ran') or has_zh(text,'我当时','我们当时','我逃','我记得'):
        persp='幸存者第一人称'
    elif has_zh(text,'家属','母亲','父亲','妻子','丈夫','儿子','女儿','亲人') or has_en(text,"mother","father","wife","husband","son's","daughter's","family"):
        persp='家属/亲友'
    elif has_zh(text,'消防','救援','民警') or has_en(text,'firefighter','rescue worker','paramedic'):
        persp='救援者'
    elif has_zh(text,'邻居','目击','居民','住户') or has_en(text,'neighbor','witness','resident','tenant'):
        persp='目击者/邻居'
    elif has_zh(text,'警方','官方','政府','部门','调查') or has_en(text,'police','officials','authorities','investigation'):
        persp='官方/媒体全知'
    else:
        persp='官方/媒体全知'
    out['叙事视角']=persp

    # 时间结构
    if any(x in Ct for x in ['邻里互助','家庭单元']) and any(k in text.lower() for k in ['died','killed','dead','fatal','葬礼','周年','纪念']):
        ts='灾后回顾'
    elif has_en(text,'died','killed','dead','fatal') or has_zh(text,'遇难','死亡','丧生','哀悼','周年','纪念'):
        ts='灾后回顾'
    elif any(x in text.lower() for x in ['climbed','crawled','descended','fled','escaped','rescued','rushed']) or has_zh(text,'逃生','撤离','爬','逃','救出','下楼'):
        ts='完整逃生序列'
    elif len(St)+len(At)+len(Vt)+len(Bt) <= 2:
        ts='单点瞬间'
    else:
        ts='完整逃生序列'
    out['时间结构']=ts

    # 核心冲突 (priority)
    if any(x in Bt for x in ['老年人步速','儿童身体限制','视觉障碍','触觉障碍']) or '残障者' in Ct or '轮椅' in Ct:
        cc='身体限制vs环境障碍'
    elif '信息延迟' in At:
        cc='信息缺失/警报延迟'
    elif '快速蔓延' in Tt:
        cc='时间压力'
    elif any(x in Ct for x in ['邻里互助','家庭单元','救援者']):
        cc='自救vs互救'
    elif has_zh(text,'缺陷','失效','故障','隐患','不合格') or has_en(text,'defect','faulty','failed','violation','code'):
        cc='建筑/设施缺陷'
    else:
        cc='逃生vs被困'
    out['核心冲突']=cc

    # 情感弧线
    if has_en(text,'died','killed','dead','fatal','mourn') or has_zh(text,'遇难','死亡','丧生','哀悼','痛失'):
        ea='悲伤/哀悼'
    elif has_en(text,'arrest','blame','negligen','lawsuit','charged') or has_zh(text,'追责','逮捕','失责','诉讼','调查','问责'):
        ea='愤怒/追责'
    elif '邻里互助' in Ct or '家庭单元' in Ct:
        ea='温情/希望'
    elif '恐慌奔逃' in Ct:
        ea='恐慌→互助→平静'
    elif any(x in text.lower() for x in ['trapped','rescued','escaped','survived']) or has_zh(text,'被困','获救','逃生','幸存'):
        ea='恐惧→绝望→获救'
    else:
        ea='混合/复杂'
    out['情感弧线']=ea

    # 叙事颗粒度
    action_kw=['climb','crawl','break','open','carry','push','press','knock','fled','ran','descend','jump']
    if sum(1 for k in action_kw if k in text.lower())>=2 or has_zh(text,'爬','破','抱','推','按','敲','逃'):
        ng='动作级'
    elif has_en(text,'percent','died','injured','building') and re.search(r'\d+', text) and ('%' in text or has_en(text,'people','residents')):
        ng='数据级'
    elif has_en(text,'fear','panic','terrified','heartbroken') or has_zh(text,'恐惧','惊慌','绝望','悲痛'):
        ng='情绪级'
    else:
        ng='场景级'
    out['叙事颗粒度']=ng

    # 交互_移动方式
    if '轮椅' in Ct or '轮椅' in Bt or has_en(text,'wheelchair','crawl') or has_zh(text,'轮椅','爬行','拄拐'):
        mv='受限移动（轮椅/拄拐/爬行）'
    elif has_zh(text,'困在','被困') or '固定' in text:
        mv='固定点位'
    elif '救援者' in Ct or has_zh(text,'引导','搀扶','救出'):
        mv='引导路径'
    else:
        mv='自由行走'
    out['交互_移动方式']=mv

    # 交互_交互动词 (multi)
    verbs=set()
    if '敲门' in At or '拍门' in At or has_zh(text,'敲门','拍门','示警') or has_en(text,'knock'): verbs.add('敲門/拍門示警')
    if '邻里呼喊' in At or has_en(text,'scream','shout','help','119','called') or has_zh(text,'呼救','呼喊','拨打'): verbs.add('呼救/拨打119')
    if has_en(text,'crawl','crawled') or has_zh(text,'匍匐','爬行'): verbs.add('匍匐/爬行')
    if has_en(text,'climb','rope','descend','ladder') or has_zh(text,'攀爬','结绳','下滑','梯'): verbs.add('攀爬/结绳下滑')
    if has_en(text,'cover','towel','mask') or has_zh(text,'捂','湿毛巾','口鼻'): verbs.add('捂口鼻/湿毛巾')
    if has_en(text,'alarm','button') or has_zh(text,'火警','警报按钮'): verbs.add('按火警按钮')
    if has_en(text,'carry','child','pet','dog','cat') or has_zh(text,'抱','牵','儿童','宠物'): verbs.add('抱/牵儿童或宠物')
    if '轮椅' in Ct or '轮椅' in Bt or has_en(text,'wheelchair','assist') or has_zh(text,'推轮椅','协助'): verbs.add('推轮椅/协助残障')
    if has_en(text,'window','jump') or has_zh(text,'破窗','跳窗','窗户'): verbs.add('破窗/跳窗')
    if has_en(text,'door','open') or has_zh(text,'开门','破门','防火门'): verbs.add('开门/破门')
    if has_zh(text,'防火门','关闭') or has_en(text,'fire door'): verbs.add('关闭防火门')
    if not verbs: verbs.add('呼救/拨打119')
    out['交互_交互动词']=sorted(verbs)

    # 交互_视角转换
    if roles != ['普通成年人'] and roles != ['普通成年人','救援者'] and '救援者' not in roles:
        vc='身体替换'
    elif '救援者' in roles:
        vc='角色切换'
    else:
        vc='无转换'
    out['交互_视角转换']=vc

    # 交互_共情机制 (multi)
    emp=set()
    if '听障者' in bodies or '视障者' in bodies: emp.add('感知剥夺')
    if any(x in Bt for x in ['老年人步速','儿童身体限制','视觉障碍','触觉障碍']) or '轮椅' in Ct or '轮椅' in Bt or '残障者' in Ct: emp.add('身体限制模拟')
    if '快速蔓延' in Tt or '深夜' in Tt or '凌晨' in Tt: emp.add('时间压力')
    if '邻里互助' in Ct or '目击者/邻居' in [persp] or '救援者' in Ct: emp.add('社会见证')
    if has_en(text,'died','killed','dead','fatal') or has_zh(text,'遇难','死亡','丧生'): emp.add('后果呈现')
    if has_zh(text,'先救','让','放弃','抉择') or has_en(text,'save','sacrifice','choice'): emp.add('道德选择')
    if '家庭单元' in Ct or '宠物' in Ct: emp.add('亲密关联')
    if not emp: emp.add('身体限制模拟')
    out['交互_共情机制']=sorted(emp)

    # 交互_沉浸反馈 (multi)
    fb=set()
    if At: fb.add('空间音频')
    if any(x in Vt for x in ['浓烟滚滚','黑烟','黑暗','浓烟灌满']) or '浓烟' in V: fb.add('视觉遮挡')
    if any(x in Bt for x in ['高温','灼热']): fb.add('温度/震动')
    if '恐慌奔逃' in Ct or '体力耗尽' in Bt: fb.add('心跳/呼吸UI')
    if '听障者' in bodies: fb.add('字幕/手语/振动提示')
    if '开门' in text or 'door' in text.lower() or 'wall' in text.lower(): fb.add('手柄/触觉阻力')
    if not fb: fb.add('空间音频')
    out['交互_沉浸反馈']=sorted(fb)

    # 交互_场景控制
    if has_en(text,'died','killed','anniversar','memorial') or has_zh(text,'遇难','周年','纪念','哀悼'): sc='博物馆/纪念碑陈列'
    elif has_zh(text,'演练','训练','培训') or has_en(text,'drill','training'): sc='重复训练/纠错'
    elif has_zh(text,'探索','自由') or has_en(text,'explore'): sc='沙盒探索'
    else: sc='线性叙事'
    out['交互_场景控制']=sc

    # 交互_社交共在
    if '邻里互助' in Ct or '家庭单元' in Ct: soc='多人协作逃生'
    elif '救援者' in Ct: soc='NPC协作/求助'
    elif '目击者/邻居' == persp: soc='旁观者视角'
    else: soc='单人'
    out['交互_社交共在']=soc

    # 设计空间备注
    note='persona='+('/'.join(roles))+' | 感官='+('/'.join(sorted(sens)))+' | 冲突='+cc+' | 弧线='+ea
    out['设计空间备注']=note

    return out

# ---------- build payload ----------
update_records={}
for i,r in enumerate(recs):
    m=rec(i)
    coded=code_one(m)
    rid=rids[i]
    payload={}
    for field,val in coded.items():
        cv=clean(val,field)
        if cv is None or cv==[] or cv=='':
            continue
        payload[field]=cv
    update_records[rid]=payload

out_obj={'update_records':update_records}
json.dump(out_obj, open(BASE+'_design_space_update.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('records coded:', len(update_records))

# ---------- stats ----------
stats={f:collections.Counter() for f in ALLOWED}
for rid,p in update_records.items():
    for f,v in p.items():
        if f=='设计空间备注': continue
        if isinstance(v,list):
            for x in v: stats[f][x]+=1
        else:
            stats[f][v]+=1
for f in ALLOWED:
    print('\n==',f)
    for k,v in stats[f].most_common(): print(f'   {k}: {v}')

# ---------- sample ----------
print('\n=== SAMPLE (first 6) ===')
for i in range(6):
    m=rec(i); coded=code_one(m); rid=rids[i]
    print(f"[{m.get('编号')}] {m.get('标题')[:50]}")
    for f in ['叙事视角','时间结构','身体主体','感官主导','核心冲突','情感弧线','交互_身体化角色','交互_移动方式','交互_交互动词','交互_共情机制','交互_沉浸反馈','交互_场景控制','交互_社交共在']:
        print(f"    {f}: {coded[f]}")
