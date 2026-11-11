import sys, pandas as pd, numpy as np
import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RAW=_os.path.join(_ROOT,'data','raw')+'/'; DER=_os.path.join(_ROOT,'data','derived')+'/'
RESDIR=_os.path.join(_ROOT,'results')+'/'; FIG=_os.path.join(_ROOT,'figures')+'/'
MODEL=_os.path.join(_ROOT,'src','model5.py')
pop=pd.read_csv(RAW+'population.csv'); tfr=pd.read_csv(RAW+'children-born-per-woman.csv'); e0=pd.read_csv(RAW+'life-expectancy.csv')
tfr.columns=['Entity','Code','Year','TFR']; e0.columns=['Entity','Code','Year','e0']; pop.columns=['Entity','Code','Year','Pop']
ok=lambda d: d[d.Code.notna() & ~d.Code.astype(str).str.startswith('OWID_') & ~d.Entity.str.contains('(UN)',regex=False) & (d.Code.astype(str).str.len()==3)]
P=ok(pop); T=ok(tfr); E=ok(e0); W=pop[pop.Entity=='World'].set_index('Year').Pop
print("odd entities kept:",[e for e in P.Entity.unique() if any(k in e for k in ('USSR','Yugoslavia','Czechoslovakia','Germany','Sudan','Serbia'))])
for y in (0,1000,1500,1800,1900,1950,2023): print(y,"sum countries / world = %.4f"%(P[P.Year==y].Pop.sum()/W[y]), P[P.Year==y].Entity.nunique())
t75=T[T.Year==1975].set_index('Entity').TFR; t10=T[T.Year==2010].set_index('Entity').TFR
grp={}
for c in P.Entity.unique():
    if c in t75.index and c in t10.index: grp[c]='A' if t75[c]<3 else ('B' if t10[c]<3 else 'C')
P=P.assign(g=P.Entity.map(grp)); print("unclassified share 2023: %.4f"%(P[(P.Year==2023)&P.g.isna()].Pop.sum()/W[2023]))
for g in 'ABC':
    q=P[(P.g==g)&(P.Year==2023)].nlargest(8,'Pop'); print(g,P[(P.g==g)&(P.Year==2023)].Entity.nunique(),"countries, %.2f Bn:"%(q.Pop.sum()/1e9 if False else P[(P.g==g)&(P.Year==2023)].Pop.sum()/1e9),', '.join(q.Entity))
d=P.dropna(subset=['g']).merge(T,on=['Entity','Code','Year'],how='left').merge(E,on=['Entity','Code','Year'],how='left')
rows=[]
for (g,y),x in d.groupby(['g','Year']):
    r=dict(g=g,Year=y,Pop=float(x.Pop.sum())); 
    for c in ('TFR','e0'):
        v=x.dropna(subset=[c]); r[c]=np.average(v[c],weights=v.Pop) if v.Pop.sum()>0.97*x.Pop.sum() else np.nan
    rows.append(r)
R=pd.DataFrame(rows); R=R[R.Year.isin(W.index)]
tot=R.groupby('Year').Pop.sum(); R['Pop']=R.apply(lambda r: float(r.Pop)*float(W[int(r.Year)])/float(tot[r.Year]),axis=1)/1e9      # rescale to world total
R.to_csv(DER+'groups.csv',index=False)
print(R[R.Year.isin([0,1000,1500,1800,1900,1950,1975,2000,2023])].pivot(index='Year',columns='g',values=['Pop','TFR','e0']).round(2).to_string())
