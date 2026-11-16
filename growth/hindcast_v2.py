"""Second coalition test. Rules: growth/PREREGISTRATION_v2.md.
Usage: python3 growth/hindcast_v2.py            (non-held-out countries)
       python3 growth/hindcast_v2.py --holdout  (held-out countries; only after a pass, once)
Writes results/growth_v2[_holdout].json and results/growth_v2[_holdout]_forecasts.csv"""
import os, sys, json, numpy as np, pandas as pd
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,ROOT)
from harness.score import score
from harness.holdout import split
HOLD='--holdout' in sys.argv; TAG='_holdout' if HOLD else ''
pwt=pd.read_excel(ROOT+'/data/raw/pwt110.xlsx',sheet_name='Data',usecols=['countrycode','year','rgdpna','emp','pop','hc'])
op,ho=split(pwt); d=ho if HOLD else op; del pwt,op,ho
art=pd.read_csv(ROOT+('/data/sealed/openalex_articles_by_country_year_HOLDOUT.csv' if HOLD else '/data/raw/openalex_articles_by_country_year.csv'))
d['q']=d.rgdpna/d.emp
P=lambda c: d.pivot(index='countrycode',columns='year',values=c)
Q,EMP,POP,HC=P('q'),P('emp'),P('pop'),P('hc'); ART=art.pivot(index='countrycode',columns='year',values='articles').reindex(Q.index)
def window(C):
    """Predictors and target for origin C. Target is NaN if C+10 is beyond the data."""
    a=ART.reindex(columns=range(C-4,C+1)).fillna(0).mean(axis=1)
    ok=(POP[C]>=1)&Q[C-10].notna()&Q[C].notna()&HC[C].notna()&(a>=20)&EMP[C-10].notna()&EMP[C].notna()
    if C+10 in Q.columns: ok&=Q[C+10].notna()
    n=ok[ok].index; x=pd.DataFrame(index=n)
    x['y']=np.log(Q.loc[n,C+10]/Q.loc[n,C])/10 if C+10 in Q.columns else np.nan
    x['g_lag']=np.log(Q.loc[n,C]/Q.loc[n,C-10])/10; x['lq']=np.log(Q.loc[n,C])-np.log(Q.loc[n,C]).max()
    x['emp_g']=np.log(EMP.loc[n,C]/EMP.loc[n,C-10])/10; x['lhc']=np.log(HC.loc[n,C])
    sa=a[n]/a[n].sum(); se=EMP.loc[n,C]/EMP.loc[n,C].sum(); x['art_int']=np.log(sa)-np.log(se); x['art_scale']=np.log(sa); x['w']=EMP.loc[n,C]; x['origin']=C
    return x
REG={'B3 shrinkage':['g_lag'],'B4 convergence':['lq'],'B5 combined':['g_lag','lq'],'M1 head count':['g_lag','lq','emp_g'],'M2 human capital':['g_lag','lq','lhc'],
     'M3 research intensity':['g_lag','lq','art_int'],'M4 research scale':['g_lag','lq','art_scale'],'M5 all four':['g_lag','lq','emp_g','lhc','art_int','art_scale']}
BASE=['B1 persistence','B2 mean','B3 shrinkage','B4 convergence','B5 combined']
def fit(tr,cols):
    """Least squares with origin fixed effects; returns slopes, the observation-weighted mean intercept, residual sd."""
    X=tr[cols].values; y=tr.y.values; o=tr.origin.values
    Xd=X-np.array([X[o==k].mean(0) for k in o]); yd=y-np.array([y[o==k].mean() for k in o])
    b,*_=np.linalg.lstsq(Xd,yd,rcond=None); a=float(np.mean(y-X@b)); res=yd-Xd@b
    return b,a,float(np.sqrt(np.sum(res**2)/max(len(y)-len(cols)-len(set(o)),1)))
ORIG=[1975,1980,1985,1990,1995,2000,2005,2010,2013]; PRIMARY=[1975,1980,1985,1990,1995,2000]
allw={C:window(C) for C in range(1960,2001,5)}; rows=[]; info={}
for C in ORIG:
    te=window(C); tr=pd.concat([allw[c] for c in allw if c+10<=C])
    if tr.origin.nunique()<2 or len(te)==0: continue
    info[C]=dict(n=int(len(te)),train_windows=sorted(int(c) for c in tr.origin.unique()),train_n=int(len(tr)),coef={})
    F={'B1 persistence':(te.g_lag.values,float(np.std(tr.y-tr.g_lag,ddof=1)))}
    m=tr.groupby('origin').g_lag.transform('mean'); F['B2 mean']=(np.full(len(te),te.g_lag.mean()),float(np.std(tr.y-m,ddof=1)))
    for k,cols in REG.items():
        b,a,s=fit(tr,cols); F[k]=(a+te[cols].values@b,s); info[C]['coef'][k]=dict(zip(cols,map(float,b)))
    for k,(v,s) in F.items(): rows.append(pd.DataFrame(dict(model=k,unit=te.index,origin=C,pred=v,lo=v-1.28*s,hi=v+1.28*s,obs=te.y.values,weight=te.w.values)))
f=pd.concat(rows); f.to_csv(ROOT+'/results/growth_v2%s_forecasts.csv'%TAG,index=False)
pr=f[f.origin.isin(PRIMARY)]; sec=f[~f.origin.isin(PRIMARY)]
S=score(pr,BASE); best=S[S.model.isin(BASE)].sort_values('rmse').model.iloc[0]
per=pd.concat([score(x,BASE).assign(origin=C) for C,x in f.groupby('origin')])
piv=per.pivot(index='model',columns='origin',values='rmse').loc[S.model]
wins={m:int(sum(piv.loc[m,C]<piv.loc[best,C] for C in PRIMARY if C in piv.columns)) for m in REG if m.startswith('M')}
# bootstrap over countries (forecasts are not refitted; whole countries are resampled with all their origins)
rng=np.random.default_rng(20261116); E=pr.assign(se=(pr.pred-pr.obs)**2).pivot_table(index='unit',columns='model',values='se',aggfunc='sum'); N=pr[pr.model==best].groupby('unit').size().reindex(E.index)
boot={}
idx=rng.integers(0,len(E),size=(2000,len(E)))
for m in [k for k in REG if k.startswith('M')]:
    r=np.sqrt(E[m].values[idx].sum(1)/E[best].values[idx].sum(1)); boot[m]=[float(np.percentile(r,5)),float(np.percentile(r,95))]
nprim=len([C for C in PRIMARY if C in piv.columns]); need=5 if nprim==6 else nprim-1
verdict={m:dict(gain=float(S.set_index('model').rmse[m]/S.set_index('model').rmse[best]-1),wins=wins[m],of=nprim,boot90=boot[m],
                passed=bool(S.set_index('model').rmse[m]/S.set_index('model').rmse[best]-1<=-0.05 and wins[m]>=need and boot[m][1]<1)) for m in boot}
json.dump(dict(holdout=HOLD,best_baseline=best,primary=S.to_dict('records'),secondary=score(sec,BASE).to_dict('records') if len(sec) else [],per_origin_rmse={str(m):{str(c):float(v) for c,v in piv.loc[m].items()} for m in piv.index},
               verdict=verdict,info={str(k):v for k,v in info.items()}),open(ROOT+'/results/growth_v2%s.json'%TAG,'w'),indent=1)
pd.set_option('display.width',220)
print("countries per origin:",{C:info[C]['n'] for C in info}); print("best baseline (primary origins):",best)
x=S.copy(); 
for c in ('rmse','rmse_w','mae','bias','width'): x[c]=(100*x[c]).round(3)
x['coverage']=(100*x.coverage).round(0); x['vs_best_baseline']=(100*x.vs_best_baseline).round(1); print("\nPRIMARY (origins 1975-2000), pooled:"); print(x.to_string(index=False))
print("\nRMSE by origin (pct points):"); print((100*piv).round(2).to_string())
if len(sec):
    y=score(sec,BASE); print("\nSECONDARY (origins 2005-2013), pooled RMSE:"); print((100*y.set_index('model').rmse).round(3).to_string())
print("\nVERDICT:"); 
for m,v in verdict.items(): print("  %-22s gain %+5.1f%%  wins %d/%d  bootstrap 90%% ratio [%.3f, %.3f]  -> %s"%(m,100*v['gain'],v['wins'],v['of'],*v['boot90'],'PASS' if v['passed'] else 'fail'))
print("mean coefficients across origins, M5:",{k:round(float(np.mean([info[C]['coef']['M5 all four'][k] for C in info])),4) for k in REG['M5 all four']})
