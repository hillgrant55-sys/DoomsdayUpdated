"""Growth-law hindcast. Rules: growth/PREREGISTRATION.md. Writes results/growth_hindcast.json and results/growth_forecasts.csv"""
import os, sys, json, numpy as np, pandas as pd
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); RAW=ROOT+'/data/raw/'; sys.path.insert(0,ROOT)
from harness.score import score
r=pd.read_csv(RAW+'researchers-in-rd-per-million-people-vs-gdp-pc.csv'); r.columns=['Entity','Code','Year','rpm','gdp','region']
p=pd.read_csv(RAW+'population.csv'); p.columns=['Entity','Code','Year','pop']
a=pd.read_csv(RAW+'population-by-age-group.csv'); a['work']=a['Ages 25-64']+a['Ages 15-24']
d=r.merge(p[['Entity','Year','pop']],on=['Entity','Year'],how='left').merge(a[['Entity','Year','work']],on=['Entity','Year'],how='left')
d['q']=d.gdp*d['pop']/d.work; d['R']=d.rpm*d['pop']/1e6
ctry=d[d.Code.notna()&(d.Code.astype(str).str.len()==3)&~d.Code.astype(str).str.startswith('OWID')]
Q=ctry.pivot(index='Entity',columns='Year',values='q'); RPM=ctry.pivot(index='Entity',columns='Year',values='rpm'); RR=ctry.pivot(index='Entity',columns='Year',values='R')
POP=ctry.pivot(index='Entity',columns='Year',values='pop'); WK=ctry.pivot(index='Entity',columns='Year',values='work')
near=lambda T,t: T.loc[:,[y for y in range(t-2,t+3) if y in T.columns]].mean(axis=1)
gr=lambda T,t0,t1: np.log(T[t1]/T[t0])/(t1-t0)
def ols(X,y):
    X=np.column_stack([np.ones(len(y))]+list(X)); b,*_=np.linalg.lstsq(X,y,rcond=None); res=y-X@b
    return b,float(np.sqrt(np.sum(res**2)/max(len(y)-X.shape[1],1)))
def pred(b,X): return np.column_stack([np.ones(len(X[0]))]+list(X))@b
BASE=['B1 persistence','B2 mean','B3 shrinkage','B4 convergence']
out={}; allf=[]
for C,m in ((2005,2000),(2010,2003)):
    out[C]={}
    for T in (2019,2023):
        ok=(POP[C]>=1e6)&Q[[1996,m,C,T]].notna().all(axis=1)&near(RPM,1996).notna()&near(RPM,m).notna()&near(RPM,C).notna()&WK[[m,C,T]].notna().all(axis=1)
        n=ok[ok].index; g1=gr(Q,1996,m)[n].values; g2=gr(Q,m,C)[n].values; gall=gr(Q,1996,C)[n].values; obs=gr(Q,C,T)[n].values; w=WK[C][n].values
        lq_m=np.log(Q[m][n].values); lq_C=np.log(Q[C][n].values)
        tr={'M1 research intensity':np.log(near(RPM,m)[n].values),'M2 researcher growth':np.log(near(RR,m)[n].values/near(RR,1996)[n].values)/(m-1996),
            'M3 head count':gr(WK,m,C)[n].values,'M4 scale':np.log(near(RR,m)[n].values)}
        fc={'M1 research intensity':np.log(near(RPM,C)[n].values),'M2 researcher growth':np.log(near(RR,C)[n].values/near(RR,m)[n].values)/(C-m),
            'M3 head count':gr(WK,C,T)[n].values,'M4 scale':np.log(near(RR,C)[n].values)}
        s12=float(np.std(g2-g1,ddof=1)); F={}; coef={}
        F['B1 persistence']=(gall,s12); F['B2 mean']=(np.full(len(n),gall.mean()),s12)
        b,s=ols([g1],g2); F['B3 shrinkage']=(pred(b,[g2]),s); coef['B3 shrinkage']=b.tolist()
        b,s=ols([lq_m],g2); F['B4 convergence']=(pred(b,[lq_C]),s); coef['B4 convergence']=b.tolist()
        for k in tr:
            b,s=ols([lq_m,tr[k]],g2); F[k]=(pred(b,[lq_C,fc[k]]),s); coef[k]=b.tolist()
        df=pd.concat([pd.DataFrame(dict(model=k,unit=n,pred=v,lo=v-1.28*s,hi=v+1.28*s,obs=obs,weight=w)) for k,(v,s) in F.items()]); df['cutoff']=C; df['end']=T; allf.append(df)
        sc=score(df,BASE)
        out[C][T]=dict(n=int(len(n)),countries=list(n),obs_mean=float(obs.mean()),train_mean=float(gall.mean()),scores=sc.to_dict('records'),coef=coef)
        print("\ncutoff %d, test to %d: %d countries; mean growth training %.2f%%, test %.2f%%"%(C,T,len(n),100*gall.mean(),100*obs.mean()))
        x=sc.copy(); 
        for c in ('rmse','rmse_w','mae','bias','width'): x[c]=(100*x[c]).round(2)
        x['coverage']=(100*x.coverage).round(0); x['vs_best_baseline']=(100*x.vs_best_baseline).round(1); print(x.drop(columns='n').to_string(index=False))
    # world law
    wd=d[d.Entity=='World'].set_index('Year'); wq=wd.q; wR=wd.R
    nearw=lambda S,t: S.loc[[y for y in range(t-2,t+3) if y in S.index]].dropna().mean()
    x0=np.log(wq[C]/wq[1996])/(C-1996); n0=np.log(nearw(wR,C)/nearw(wR,1996))/(C-1996); lam=n0/x0
    n1=np.log(nearw(wR,2019)/nearw(wR,C))/(2019-C); lnq=0.0; lnR=0.0
    for _ in range(2019-C): lnq+=x0*np.exp(lnR-lam*lnq); lnR+=n1
    obsw=np.log(wq[2019]/wq[C])/(2019-C)
    out[C]['world']=dict(train_growth=float(x0),researcher_growth_train=float(n0),researcher_growth_test=float(n1),lam=float(lam),pred_constant=float(x0),pred_law=float(lnq/(2019-C)),obs=float(obsw))
    print("world: training growth %.2f%%, researchers %.2f%% then %.2f%%, lambda %.2f | (a) constant %.2f%%  (b) law %.2f%%  observed %.2f%%"%(100*x0,100*n0,100*n1,lam,100*x0,100*lnq/(2019-C),100*obsw))
json.dump({str(k):{str(kk):vv for kk,vv in v.items()} for k,v in out.items()},open(ROOT+'/results/growth_hindcast.json','w'),indent=1)
pd.concat(allf).to_csv(ROOT+'/results/growth_forecasts.csv',index=False)

# ---- Deviation (see RESULTS.md): the file has no world researcher figure before 2000, so the world law cannot be run as preregistered.
# Substitute: the fixed country sample treated as one economy (summed output, working-age population and researchers).
agg={}
for C in (2005,2010):
    n=out[C][2019]['countries']; G=(ctry[ctry.Entity.isin(n)].assign(gdp_tot=lambda x:x.gdp*x['pop'])); 
    qa=lambda t: G[G.Year==t].gdp_tot.sum()/G[G.Year==t].work.sum(); Ra=lambda t: near(RR,t)[n].sum()
    x0=np.log(qa(C)/qa(1996))/(C-1996); n0=np.log(Ra(C)/Ra(1996))/(C-1996); lam=n0/x0; n1=np.log(Ra(2019)/Ra(C))/(2019-C); lnq=0.0; lnR=0.0
    for _ in range(2019-C): lnq+=x0*np.exp(lnR-lam*lnq); lnR+=n1
    agg[C]=dict(train_growth=float(x0),researcher_growth_train=float(n0),researcher_growth_test=float(n1),lam=float(lam),pred_constant=float(x0),pred_law=float(lnq/(2019-C)),obs=float(np.log(qa(2019)/qa(C))/(2019-C)))
    print("sample as one economy, cutoff %d: growth %.2f%%, researchers %.2f%% then %.2f%%, lambda %.2f | (a) %.2f%% (b) %.2f%% observed %.2f%%"%(C,100*x0,100*n0,100*n1,lam,100*x0,100*lnq/(2019-C),100*agg[C]['obs']))
J=json.load(open(ROOT+'/results/growth_hindcast.json')); J['sample_aggregate_law']={str(k):v for k,v in agg.items()}; json.dump(J,open(ROOT+'/results/growth_hindcast.json','w'),indent=1)
