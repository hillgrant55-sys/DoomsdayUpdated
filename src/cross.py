import sys, pandas as pd, numpy as np
import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RAW=_os.path.join(_ROOT,'data','raw')+'/'; DER=_os.path.join(_ROOT,'data','derived')+'/'
RESDIR=_os.path.join(_ROOT,'results')+'/'; FIG=_os.path.join(_ROOT,'figures')+'/'
MODEL=_os.path.join(_ROOT,'src','model5.py')
pop=pd.read_csv(RAW+'population.csv'); tfr=pd.read_csv(RAW+'children-born-per-woman.csv'); e0=pd.read_csv(RAW+'life-expectancy.csv')
tfr.columns=['Entity','Code','Year','TFR']; e0.columns=['Entity','Code','Year','e0']; pop.columns=['Entity','Code','Year','Pop']
ok=lambda d: d[d.Code.notna() & ~d.Code.astype(str).str.startswith('OWID_')]
d=ok(tfr).merge(ok(e0),on=['Entity','Code','Year']).merge(ok(pop),on=['Entity','Code','Year'])
print("countries:",d.Entity.nunique(),"years",d.Year.min(),d.Year.max())
wm=lambda g,c: np.average(g[c],weights=g.Pop)
y=d[d.Year==2023]; print("2023 coverage of world pop: %.3f"%(y.Pop.sum()/8.0917e9))
print("\n2023 by life-expectancy band: n, pop (Bn), pop-weighted TFR, share below 2.02")
for lo,hi in ((0,60),(60,65),(65,70),(70,75),(75,78),(78,80),(80,82),(82,90),(78,90),(80,90)):
    g=y[(y.e0>=lo)&(y.e0<hi)]
    if len(g): print("  e0 %2d-%2d: %3d  %.2f  %.2f  %.2f"%(lo,hi,len(g),g.Pop.sum()/1e9,wm(g,'TFR'),(g.Pop*(g.TFR<2.02)).sum()/g.Pop.sum()))
print("\nSame bands in earlier years (pop-weighted TFR for e0>=78 / 80):")
for yr in (1990,2000,2010,2015,2019,2023):
    g=d[d.Year==yr]; a=g[g.e0>=78]; b=g[g.e0>=80]; print("  %d  >=78: %.2f (%.2f Bn)   >=80: %s"%(yr,wm(a,'TFR') if len(a) else np.nan,a.Pop.sum()/1e9,("%.2f (%.2f Bn)"%(wm(b,'TFR'),b.Pop.sum()/1e9)) if len(b) else "-"))
print("\nFixed cohort: countries with TFR<2.02 in 1995; their pop-weighted TFR over time")
c=d[(d.Year==1995)&(d.TFR<2.02)].Entity; print("  n=%d, pop 2023 %.2f Bn"%(len(c),y[y.Entity.isin(c)].Pop.sum()/1e9))
for yr in (1995,2000,2005,2010,2015,2019,2023): g=d[(d.Year==yr)&d.Entity.isin(c)]; print("  %d %.3f"%(yr,wm(g,'TFR')))
print("\nShare of world population living in countries below 2.02:")
for yr in (1960,1980,1990,2000,2010,2020,2023): g=d[d.Year==yr]; print("  %d %.2f"%(yr,(g.Pop*(g.TFR<2.02)).sum()/g.Pop.sum()))
print("\nlowest 2023 (pop>20M):"); print(y[y.Pop>2e7].nsmallest(8,'TFR')[['Entity','TFR','e0']].to_string(index=False))
# TFR as function of e0, all country-years since 1950, pop-weighted mean by 2.5-yr e0 bins: early (1950-1989) vs late (1990-2023)
print("\nTFR vs e0, pop-weighted, by period")
bins=np.arange(40,87.5,2.5); d['bin']=pd.cut(d.e0,bins)
for nm,g in (("1950-89",d[(d.Year>=1950)&(d.Year<1990)]),("1990-2023",d[d.Year>=1990])):
    print(nm,g.groupby('bin',observed=True).apply(lambda x: round(wm(x,'TFR'),2)).to_dict())
d[['Entity','Year','TFR','e0','Pop']].to_csv(DER+'cross.csv',index=False)
