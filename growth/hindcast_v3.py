"""Attempt 3: the absorption model. Rules: growth/PREREGISTRATION_v3.md.
  python3 growth/hindcast_v3.py --stage1   open countries only (development, spent data)
  python3 growth/hindcast_v3.py --stage2   confirmation on held-out countries (run once, only after the gate and agreement)
Writes results/growth_v3_<stage>.json and results/growth_v3_<stage>_forecasts.csv"""
import os, sys, json, numpy as np, pandas as pd
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,ROOT)
from harness.score import score
from harness.holdout import split, is_holdout
STAGE='stage2' if '--stage2' in sys.argv else ('stage1' if '--stage1' in sys.argv else None)
if STAGE is None: sys.exit("say --stage1 or --stage2")
pwt=pd.read_excel(ROOT+'/data/raw/pwt110.xlsx',sheet_name='Data',usecols=['countrycode','year','rgdpna','emp','pop','hc'])
op,ho=split(pwt)
art=pd.read_csv(ROOT+'/data/raw/openalex_articles_by_country_year.csv')
if STAGE=='stage1':
    d=op; del ho
else:
    d=pd.concat([op,ho]); art=pd.concat([art,pd.read_csv(ROOT+'/data/sealed/openalex_articles_by_country_year_HOLDOUT.csv')])
d=d.copy(); d['q']=d.rgdpna/d.emp
P=lambda c: d.pivot(index='countrycode',columns='year',values=c)
Q,EMP,POP,HC=P('q'),P('emp'),P('pop'),P('hc'); ART=art.pivot(index='countrycode',columns='year',values='articles').reindex(Q.index)
def window(C):
    a=ART.reindex(columns=range(C-4,C+1)).fillna(0).mean(axis=1)
    ok=(POP[C]>=1)&Q[C-10].notna()&Q[C].notna()&HC[C].notna()&(a>=20)&EMP[C-10].notna()&EMP[C].notna()
    if C+10 in Q.columns: ok&=Q[C+10].notna()
    n=ok[ok].index; x=pd.DataFrame(index=n)
    x['y']=np.log(Q.loc[n,C+10]/Q.loc[n,C])/10 if C+10 in Q.columns else np.nan
    x['g_lag']=np.log(Q.loc[n,C]/Q.loc[n,C-10])/10; x['gap']=np.log(Q.loc[n,C]).max()-np.log(Q.loc[n,C])
    x['lhc']=np.log(HC.loc[n,C]); x['lhc_gap']=x.lhc*x.gap
    sa=a[n]/a[n].sum(); se=EMP.loc[n,C]/EMP.loc[n,C].sum(); x['art_int']=np.log(sa)-np.log(se); x['art_gap']=x.art_int*x.gap
    x['w']=EMP.loc[n,C]; x['origin']=C; x['held']=[is_holdout(c) for c in n]
    return x
REG={'B3 shrinkage':['g_lag'],'B4 convergence':['gap'],'B5 combined':['g_lag','gap'],
     'A1 Nelson-Phelps':['g_lag','gap','lhc','lhc_gap'],'A2 two faces':['g_lag','gap','lhc','lhc_gap','art_int','art_gap']}
BASE=['B1 persistence','B2 mean','B3 shrinkage','B4 convergence','B5 combined']
def fit(tr,cols):
    X=tr[cols].values; y=tr.y.values; o=tr.origin.values
    Xd=X-np.array([X[o==k].mean(0) for k in o]); yd=y-np.array([y[o==k].mean() for k in o])
    b,*_=np.linalg.lstsq(Xd,yd,rcond=None); a=float(np.mean(y-X@b)); res=yd-Xd@b
    return b,a,float(np.sqrt(np.sum(res**2)/max(len(y)-len(cols)-len(set(o)),1)))
ORIG=[1975,1980,1985,1990,1995,2000,2005,2010,2013]; PRIMARY=[1975,1980,1985,1990,1995,2000]
W={C:window(C) for C in range(1960,2014,5)}; W[2013]=window(2013)
rows=[]; info={}
for C in ORIG:
    te=W[C]; te=te[te.held] if STAGE=='stage2' else te
    fin=sorted([c for c in W if c+10<=C and c%5==0])[-3:]          # three most recent finished windows
    tr=pd.concat([W[c] for c in fin])
    if len(fin)<2 or len(te)==0: continue
    info[C]=dict(n=int(len(te)),train_windows=fin,train_n=int(len(tr)),coef={})
    F={'B1 persistence':(te.g_lag.values,float(np.std(tr.y-tr.g_lag,ddof=1)))}
    m=tr.groupby('origin').g_lag.transform('mean'); F['B2 mean']=(np.full(len(te),te.g_lag.mean()),float(np.std(tr.y-m,ddof=1)))
    for k,cols in REG.items():
        b,a,s=fit(tr,cols); F[k]=(a+te[cols].values@b,s); info[C]['coef'][k]=dict(zip(cols,map(float,b)))
    for k,(v,s) in F.items(): rows.append(pd.DataFrame(dict(model=k,unit=te.index,origin=C,pred=v,lo=v-1.28*s,hi=v+1.28*s,obs=te.y.values,weight=te.w.values)))
f=pd.concat(rows); f.to_csv(ROOT+'/results/growth_v3_%s_forecasts.csv'%STAGE,index=False)
def judge(sub,origins,label):
    S=score(sub,BASE); best=S[S.model.isin(BASE)].sort_values('rmse').model.iloc[0]
    per=pd.concat([score(x,BASE).assign(origin=C) for C,x in sub.groupby('origin')]); piv=per.pivot(index='model',columns='origin',values='rmse').loc[S.model]
    oc=[C for C in origins if C in piv.columns]; need=5 if len(oc)==6 else len(oc)-1
    E=sub.assign(se=(sub.pred-sub.obs)**2).pivot_table(index='unit',columns='model',values='se',aggfunc='sum')
    idx=np.random.default_rng(20261116).integers(0,len(E),size=(2000,len(E))); V={}
    for mdl in ['A1 Nelson-Phelps','A2 two faces']:
        r=np.sqrt(E[mdl].values[idx].sum(1)/E[best].values[idx].sum(1)); g=float(S.set_index('model').rmse[mdl]/S.set_index('model').rmse[best]-1)
        w=int(sum(piv.loc[mdl,C]<piv.loc[best,C] for C in oc))
        V[mdl]=dict(gain=g,wins=w,of=len(oc),boot90=[float(np.percentile(r,5)),float(np.percentile(r,95))],passed=bool(g<=-0.05 and w>=need and np.percentile(r,95)<1))
    print("\n%s: best baseline %s"%(label,best)); x=S.copy()
    for c in ('rmse','rmse_w','mae','bias','width'): x[c]=(100*x[c]).round(3)
    x['coverage']=(100*x.coverage).round(0); x['vs_best_baseline']=(100*x.vs_best_baseline).round(1); print(x.to_string(index=False))
    print((100*piv).round(2).to_string())
    for mdl,v in V.items(): print("  %-18s gain %+5.1f%%  wins %d/%d  bootstrap 90%% [%.3f, %.3f]  -> %s"%(mdl,100*v['gain'],v['wins'],v['of'],*v['boot90'],'PASS' if v['passed'] else 'fail'))
    return dict(best_baseline=best,scores=S.to_dict('records'),per_origin_rmse={m:{str(c):float(v) for c,v in piv.loc[m].items()} for m in piv.index},verdict=V)
out=dict(stage=STAGE,info={str(k):v for k,v in info.items()})
print("countries scored per origin:",{C:info[C]['n'] for C in info},"| training windows:",{C:info[C]['train_windows'] for C in info})
out['all_origins']=judge(f,ORIG,"ALL ORIGINS 1975-2013 (stage 1 gate uses this)")
out['primary']=judge(f[f.origin.isin(PRIMARY)],PRIMARY,"PRIMARY ORIGINS 1975-2000")
co=pd.DataFrame({C:info[C]['coef']['A1 Nelson-Phelps'] for C in info}).T; print("\nA1 coefficients by origin:"); print(co.round(4).to_string())
out['A1_coef_mean']={k:float(v) for k,v in co.mean().items()}
if STAGE=='stage1':
    a=out['all_origins']; g=a['verdict']['A1 Nelson-Phelps']['gain']; out['gate_passed']=bool(g<0)
    print("\nGATE: A1 pooled RMSE vs best baseline over all stage-1 origins: %+.1f%% -> %s"%(100*g,'OPEN' if g<0 else 'CLOSED'))
json.dump(out,open(ROOT+'/results/growth_v3_%s.json'%STAGE,'w'),indent=1)
