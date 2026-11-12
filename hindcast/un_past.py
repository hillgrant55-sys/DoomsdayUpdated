"""Score the UN's past medium projections of world population against 2023.
Data: data/raw/world-population-projections-by-un-prospects-revision.csv (Our World in Data).
The file gives projections every 5 years; 2023 is obtained by log-linear interpolation between 2020 and 2025.
Writes results/hindcast_un.json"""
import os, json, numpy as np, pandas as pd
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d=pd.read_csv(ROOT+'/data/raw/world-population-projections-by-un-prospects-revision.csv').set_index('Year')
obs=d['Latest observed data']/1e9; ON=float(obs[2023]); OG=float(np.log(obs[2023]/obs[2015])/8)
out={}
for c in [c for c in d.columns if c.endswith('projection')]:
    s=d[c].dropna()/1e9; r=dict(first_year=int(s.index.min()),last_year=int(s.index.max()))
    if 2020 in s.index and 2025 in s.index:
        n23=float(np.exp(np.log(s[2020])+0.6*np.log(s[2025]/s[2020]))); r.update(N2020=float(s[2020]),err_2020=float(s[2020]/obs[2020]-1),N2023=n23,err_N=n23/ON-1)
        if 2015 in s.index: r.update(g=float(np.log(n23/s[2015])/8),err_g_pt=float(100*(np.log(n23/s[2015])/8-OG)))
    b=int(s.index.min()); r['base_err']=float(s[b]/obs[b]-1) if b in obs.dropna().index else None
    if 'N2023' in r and r['base_err'] is not None: r['err_growth_factor']=float((r['N2023']/s[b])/(ON/obs[b])-1)   # error in projected growth from the first projected year, removing the base-data error
    out[c]=r
json.dump(dict(obs=dict(N2023=ON,g=OG),un=out),open(ROOT+'/results/hindcast_un.json','w'),indent=1)
print("observed N2023 %.3f g %.3f%%"%(ON,100*OG))
for k,v in out.items():
    if 'N2023' in v: print("%-16s gf err %+.1f%%  first yr %d (base err %+.1f%%)  2020: %.3f (%+.1f%%)  2023 interp: %.3f (%+.1f%%)  g %s"%(k,100*v.get('err_growth_factor',float('nan')),v['first_year'],100*v['base_err'],v['N2020'],100*v['err_2020'],v['N2023'],100*v['err_N'],'%.2f%% (%+.2f)'%(100*v['g'],v['err_g_pt']) if 'g' in v else 'n/a'))
