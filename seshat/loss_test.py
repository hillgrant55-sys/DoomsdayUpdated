"""Knowledge-loss test. Rules: seshat/PREREGISTRATION.md.
  python3 seshat/loss_test.py --open      open regions (primary test)
  python3 seshat/loss_test.py --holdout   held-out regions (replication; run once)
Writes results/seshat_loss_<stage>.json"""
import os, sys, json, hashlib, numpy as np, pandas as pd
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE='holdout' if '--holdout' in sys.argv else ('open' if '--open' in sys.argv else None)
if STAGE is None: sys.exit("say --open or --holdout")
held=lambda n: hashlib.sha256(str(n).encode()).hexdigest()[0] in '01234'
F=ROOT+'/data/external/seshat/Equinox_Data/Equinox_on_GitHub_June9_2022.xlsx'
d=pd.read_excel(F,sheet_name='AggrSCWarAgriRelig')
d=d[d.NGA.map(held)==(STAGE=='holdout')].copy()
NUM=['Time','Pop','Infra','Info','Money','Metal','Project','Weapon','Animal','Armor','Defense']
for c in NUM: d[c]=pd.to_numeric(d[c],errors='coerce').replace(-999,np.nan)
d['C']=d[['Infra','Info','Money']].sum(axis=1,min_count=3)
d['M']=d[['Metal','Project','Weapon','Animal','Armor','Defense']].sum(axis=1,min_count=6)
d['real']=d.uniq.astype(str).str.strip().str.lower()=='y'
# one row per region-century: if several, keep real rows; if still several, the century is ambiguous and dropped
g=d.groupby(['NGA','Time'])
n_multi=int((g.size()>1).sum())
d=d[d.real|~d.set_index(['NGA','Time']).index.isin(d[d.real].set_index(['NGA','Time']).index)]
cnt=d.groupby(['NGA','Time']).size(); amb=cnt[cnt>1].index
d=d.set_index(['NGA','Time']); d=d[~d.index.isin(amb)]
def transitions(out):
    rows=[]
    for (nga,t),r in d.iterrows():
        try: a=d.loc[(nga,t-100)]; b=d.loc[(nga,t+100)]
        except KeyError: continue
        if not (a.real and r.real and b.real): continue
        if any(pd.isna(x) for x in (a.Pop,r.Pop,r[out],b[out])): continue
        rows.append(dict(NGA=nga,t=int(t),dpop=float(r.Pop-a.Pop),decl=bool(r.Pop-a.Pop<=-0.15),loss=bool(b[out]<r[out]-1e-9),polchange=bool(b.PolID!=r.PolID)))
    return pd.DataFrame(rows)
def rr_mh(x,decl):
    num=den=0.0
    for s in (False,True):
        m=(x.polchange.values==s); e=decl[m]; l=x.loss.values[m]; N=m.sum()
        if N==0: continue
        a=(e&l).sum(); n1=e.sum(); c=(~e&l).sum(); n0=(~e).sum()
        num+=a*n0/N; den+=c*n1/N
    return num/den if den>0 else (np.inf if num>0 else np.nan)
def test(out,B=10000,seed=20261116):
    x=transitions(out).reset_index(drop=True); decl=x.decl.values.copy(); obs=rr_mh(x,decl)
    rng=np.random.default_rng(seed); groups=[np.where(x.NGA.values==n)[0] for n in x.NGA.unique()]; ge=0
    for _ in range(B):
        pd_=decl.copy()
        for gi in groups: pd_[gi]=rng.permutation(decl[gi])
        r=rr_mh(x,pd_); ge+= (r>=obs) if np.isfinite(obs) else (r==np.inf)
    tab={}
    for s in (False,True):
        for e in (False,True):
            m=(x.polchange==s)&(x.decl==e); tab[f"{'polity change' if s else 'same polity'} / {'sharp decline' if e else 'no sharp decline'}"]=dict(n=int(m.sum()),losses=int(x.loss[m].sum()),rate=float(x.loss[m].mean()) if m.sum() else None)
    return dict(n=int(len(x)),regions=int(x.NGA.nunique()),declines=int(x.decl.sum()),losses=int(x.loss.sum()),loss_rate=float(x.loss.mean()),
                crude_rr=float(x.loss[x.decl].mean()/x.loss[~x.decl].mean()) if x.loss[~x.decl].mean()>0 and x.decl.any() else None,
                rr_mh=float(obs),p_perm=float((1+ge)/(1+B)),table=tab,
                loss_rate_polchange=float(x.loss[x.polchange].mean()) if x.polchange.any() else None,loss_rate_samepolity=float(x.loss[~x.polchange].mean()) if (~x.polchange).any() else None), x
res={'stage':STAGE,'region_centuries_with_several_rows':n_multi,'ambiguous_dropped':int(len(amb))}
for name,out in (('capability (Infra+Info+Money)','C'),('military technology (6 components)','M')):
    r,x=test(out); res[name]=r; x.to_csv(ROOT+'/results/seshat_loss_%s_%s.csv'%(STAGE,out),index=False)
    print("\n== %s, %s regions =="%(name,STAGE))
    print("transitions %d in %d regions; sharp declines %d; losses %d (%.1f%%)"%(r['n'],r['regions'],r['declines'],r['losses'],100*r['loss_rate']))
    for k,v in r['table'].items(): print("   %-40s n=%4d losses=%3d rate=%s"%(k,v['n'],v['losses'],'%.3f'%v['rate'] if v['rate'] is not None else '-'))
    print("   loss rate at polity change %.3f, within polity %.3f"%(r['loss_rate_polchange'] or 0,r['loss_rate_samepolity'] or 0))
    print("   crude RR %s | Mantel-Haenszel RR %.2f | permutation p %.4f"%('%.2f'%r['crude_rr'] if r['crude_rr'] else '-',r['rr_mh'],r['p_perm']))
print("\nregion-centuries with several rows: %d; ambiguous dropped: %d"%(n_multi,len(amb)))
json.dump(res,open(ROOT+'/results/seshat_loss_%s.json'%STAGE,'w'),indent=1)
