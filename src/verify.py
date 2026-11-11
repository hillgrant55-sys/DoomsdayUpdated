import sys, numpy as np, pandas as pd, json
import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RAW=_os.path.join(_ROOT,'data','raw')+'/'; DER=_os.path.join(_ROOT,'data','derived')+'/'
RESDIR=_os.path.join(_ROOT,'results')+'/'; FIG=_os.path.join(_ROOT,'figures')+'/'
MODEL=_os.path.join(_ROOT,'src','model5.py')
Z=np.load(RESDIR+'fig_data.npz'); ts=Z['ts']; o=Z['o']; cb=Z['c_baseline']; t=cb[0]; Y=cb[3]
k=np.where((t>2070)&(Y<1))[0][0]; print("output back to 2025 level:",t[k]); print("income per person 2100/2200/2300/2500:",[round(float(np.interp(y,t,cb[2])),2) for y in (2100,2200,2300,2500)]); print("x 2092ish; workforce growth 2090-2095: %.2f%%"%(100*np.log(o[ts==2095,:,4].sum()/o[ts==2090,:,4].sum())/5))
print("model TFR C at 2020/2025:",o[ts==2020,2,1],o[ts==2025,2,1]," world N 2025 model",o[ts==2025,:,0].sum())
print("65+ share 2025 %.3f 2100 %.3f; work 2025 %.3f 2100 %.3f"%tuple(float(o[ts==y,:,c].sum()/o[ts==y,:,0].sum()) for c,y in ((5,2025),(5,2100),(4,2025),(4,2100))))
pop=pd.read_csv(RAW+'population.csv'); pop.columns=['Entity','Code','Year','Pop']; res=pd.read_csv(RAW+'researchers-in-rd-per-million-people-vs-gdp-pc.csv'); res.columns=['Entity','Code','Year','RD','GDP','reg']
rr=res.merge(pop[['Entity','Year','Pop']],on=['Entity','Year']).dropna(subset=['RD']); rr=rr[rr.Code.astype(str).str.len()==3]; rr=rr[~rr.Entity.str.contains('(',regex=False)]; rr['tot']=rr.RD*rr.Pop/1e6
n0=rr[(rr.Year>=1998)&(rr.Year<=2002)].groupby('Entity').tot.mean(); n1=rr[(rr.Year>=2018)&(rr.Year<=2022)].groupby('Entity').tot.mean(); c=n0.index.intersection(n1.index); d=(n1[c]-n0[c]).sort_values(ascending=False)
print("researcher growth total %.2f M; top contributors:"%(d.sum()/1e6)); print((d.head(6)/1e6).round(2).to_string()); print("growth excl. China: %.2f%%/yr"%(100*np.log((n1[c].sum()-n1.get('China',0))/(n0[c].sum()-n0.get('China',0)))/20))
W=pop[pop.Entity=='World'].set_index('Year').Pop; print("world pop year 0: %.0f M; 2023 %.2f Bn; growth 2022-23 %.2f%%; max annual growth %.2f%% in %d"%(W[0]/1e6,W[2023]/1e9,100*np.log(W[2023]/W[2022]),100*np.log(W.loc[1951:2023].values/W.loc[1950:2022].values).max(),1951+int(np.argmax(np.log(W.loc[1951:2023].values/W.loc[1950:2022].values)))))
