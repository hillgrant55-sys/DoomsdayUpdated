import sys, pandas as pd, numpy as np
U=sys.argv[1]
pop=pd.read_csv(U+'/80cc69c6-population.csv'); tfr=pd.read_csv(U+'/abab83cc-children-born-per-woman.csv'); e0=pd.read_csv(U+'/7c8d2eca-life-expectancy.csv'); urb=pd.read_csv(U+'/c50bffc8-population-of-cities-towns-and-villages.csv'); wpp=pd.read_csv(U+'/d0de916b-population-unwpp.csv')
for n,d in (('pop',pop),('tfr',tfr),('e0',e0),('urb',urb),('wpp',wpp)): print(n,d.shape,d.Year.min(),d.Year.max(),d.Entity.nunique(), d.isna().sum().sum())
w=pop[pop.Entity=='World'].set_index('Year').Population
print(w[(w.index>=-1000)&(w.index<1800)].to_string())
print(w[(w.index>=1800)&(w.index<1950)&(w.index%10==0)].to_string())
print(w[(w.index>=1950)&(w.index%5==0)].to_string(), w.index.max())
print((w-wpp[wpp.Entity=='World'].set_index('Year').iloc[:,-1]).dropna().abs().max())
print(e0[e0.Entity=='World'][['Year','Life expectancy']].to_string(index=False))
t=tfr[tfr.Entity=='World'].set_index('Year').iloc[:,-1]; print(t[t.index%5==0].to_string(), t.iloc[-3:].to_string())
print(urb[urb.Entity=='World'].to_string(index=False))
for d,n in ((tfr,'tfr'),(e0,'e0')): print(n,[e for e in d.Entity.unique() if '(' in e or e in('World','Africa','Asia','Europe')])
