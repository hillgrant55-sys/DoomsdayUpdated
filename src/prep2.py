import sys, pandas as pd, numpy as np, json
import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RAW=_os.path.join(_ROOT,'data','raw')+'/'; DER=_os.path.join(_ROOT,'data','derived')+'/'
RESDIR=_os.path.join(_ROOT,'results')+'/'; FIG=_os.path.join(_ROOT,'figures')+'/'
MODEL=_os.path.join(_ROOT,'src','model5.py')
rd=lambda f: pd.read_csv(RAW+f)
pop=rd('population.csv'); tfr=rd('children-born-per-woman.csv'); age=rd('population-by-age-group.csv'); prj=rd('population-with-un-projections.csv')
bth=rd('births-by-age-of-mother.csv'); res=rd('researchers-in-rd-per-million-people-vs-gdp-pc.csv'); mig=rd('migrant-stock-share.csv'); gdpw=rd('global-average-gdp-per-capita-over-the-long-run.csv')
tfr.columns=['Entity','Code','Year','TFR']; pop.columns=['Entity','Code','Year','Pop']
ok=lambda d: d[d.Code.notna() & ~d.Code.astype(str).str.startswith('OWID_') & ~d.Entity.str.contains('(UN)',regex=False) & (d.Code.astype(str).str.len()==3)]
T=ok(tfr); t75=T[T.Year==1975].set_index('Entity').TFR; t10=T[T.Year==2010].set_index('Entity').TFR
grp={c:('A' if t75[c]<3 else ('B' if t10[c]<3 else 'C')) for c in t75.index if c in t10.index}
P=ok(pop).assign(g=lambda d:d.Entity.map(grp)).dropna(subset=['g'])
out={}
# age structure
a=ok(age).assign(g=lambda d:d.Entity.map(grp)).dropna(subset=['g']); a.columns=['Entity','Code','Year','o65','a2564','a1524','a514','u5','g']
ag=a.groupby(['g','Year'])[['o65','a2564','a1524','a514','u5']].sum(); ag['N']=ag.sum(axis=1); ag['work']=(ag.a2564+ag.a1524)/ag.N; ag['old']=ag.o65/ag.N; ag['young']=(ag.a514+ag.u5)/ag.N
aw=age[age.Entity=='World'].set_index('Year').iloc[:,2:]; aw.columns=['o65','a2564','a1524','a514','u5']; aw['N']=aw.sum(axis=1); aw['work']=(aw.a2564+aw.a1524)/aw.N; aw['old']=aw.o65/aw.N
print("age coverage vs world 2023: %.4f"%(ag.xs(2023,level='Year').N.sum()/aw.N[2023]))
print(pd.concat({g:ag.xs(g).loc[[1950,1975,2000,2023],['work','old']] for g in 'ABC'},axis=1).round(3).to_string()); print(aw.loc[[1950,1975,2000,2023],['work','old']].round(3).to_string())
# UN projections by group
p=ok(prj).assign(g=lambda d:d.Entity.map(grp)).dropna(subset=['g']); p['N']=p['Population'].fillna(p['Population (Projected)']).astype(float)
pg=p.groupby(['g','Year']).N.sum().unstack(0)/1e9; pw=prj[prj.Entity=='World'].set_index('Year'); pw=(pw['Population'].fillna(pw['Population (Projected)'])/1e9)
print("UN projection (Bn):"); print(pd.concat([pg.loc[[2023,2050,2075,2100]],pw.loc[[2023,2050,2075,2100]].rename('World')],axis=1).round(2).to_string()); print("UN world peak: %.3f in %d"%(pw.max(),pw.idxmax())); print("group peaks:",{g:(round(pg[g].max(),2),int(pg[g].idxmax())) for g in 'ABC'})
# births by age of mother
b=bth[bth.Entity=='World'].set_index('Year').iloc[:,2:]; mids=np.array([52.5,47.5,42.5,37.5,32.5,27.5,22.5,17.5,12.5]); mac=(b.values*mids).sum(1)/b.values.sum(1)
print("world mean age of mothers at birth:",{y:round(float(m),2) for y,m in zip(b.index,mac) if y in (1950,1975,2000,2023)})
bg=ok(bth).assign(g=lambda d:d.Entity.map(grp)).dropna(subset=['g']); 
for g in 'ABC':
    x=bg[bg.g==g].groupby('Year').sum(numeric_only=True); x=x[[c for c in b.columns]]; print(" ",g,{y:round(float((x.loc[y].values*mids).sum()/x.loc[y].values.sum()),2) for y in (1950,2000,2023)})
phi=b.loc[1950:2023].sum().values[::-1]; phi=phi/phi.sum(); print("births distribution 10-14..50-54:",np.round(phi,4))
# GDP per capita
gw=gdpw.set_index('Year')['GDP per capita']; r=ok(res).assign(g=lambda d:d.Entity.map(grp)).dropna(subset=['g']); r.columns=['Entity','Code','Year','RD','GDP','reg','g']
r=r.merge(P[['Entity','Year','Pop']],on=['Entity','Year'],how='left')
x=r.dropna(subset=['GDP','Pop']); gg=x.groupby(['g','Year']).apply(lambda d: np.average(d.GDP,weights=d.Pop)).unstack(0); cov=x.groupby(['g','Year']).Pop.sum().unstack(0)/P[P.Year.isin(gg.index)].groupby(['g','Year']).Pop.sum().unstack(0)
print("group GDP pc:"); print(gg.loc[[1990,2000,2010,2023]].round(0).to_string()); print("coverage",cov.loc[[1990,2023]].round(3).to_string()); print("world GDPpc check 2023: groups %.0f vs file %.0f"%(np.average(gg.loc[2023],weights=[P[(P.g==g)&(P.Year==2023)].Pop.sum() for g in 'ABC']),gw[2023]))
# researchers: constant set of countries reporting near 2000 and 2020
rr=r.dropna(subset=['RD','Pop']); rr=rr.assign(tot=rr.RD*rr.Pop/1e6)
def near(y):
    z=rr[(rr.Year>=y-2)&(rr.Year<=y+2)]; return z.groupby('Entity').tot.mean()
r0,r1=near(2000),near(2020); common=r0.index.intersection(r1.index); popc=P[(P.Year==2020)&P.Entity.isin(common)].Pop.sum()/P[P.Year==2020].Pop.sum()
print("researchers: %d countries (%.0f%% of world pop): %.2f M (2000) -> %.2f M (2020), growth %.2f%%/yr; world GDPpc growth 2000-2020 %.2f%%/yr; 1990-2000 %.2f"%(len(common),100*popc,r0[common].sum()/1e6,r1[common].sum()/1e6,100*np.log(r1[common].sum()/r0[common].sum())/20,100*np.log(gw[2019]/gw[2000])/19,100*np.log(gw[2000]/gw[1990])/10))
print("researchers 2020 by group (M):",{g:round(r1[[c for c in common if grp[c]==g]].sum()/1e6,2) for g in 'ABC'})
# migrants
m=ok(mig).assign(g=lambda d:d.Entity.map(grp)).dropna(subset=['g']); m.columns=['Entity','Code','Year','share','reg','g']; m=m.merge(P[['Entity','Year','Pop']],on=['Entity','Year'])
print("foreign-born share % by group:"); print(m.groupby(['g','Year']).apply(lambda d: np.average(d.share,weights=d.Pop)).unstack(0).round(1).to_string())
# save
ag.reset_index().to_csv(DER+'group_age.csv',index=False); aw.reset_index().to_csv(DER+'world_age.csv',index=False); pg.assign(World=pw).reset_index().to_csv(DER+'un_proj.csv',index=False); gg.reset_index().to_csv(DER+'group_gdp.csv',index=False)
json.dump(dict(phi=list(map(float,phi))),open(DER+'phi.json','w'))
