"""Score the hindcast against 2023 and draw the summary figure.
Reads results/hindcast_simple.json and results/hindcast_cohort_<cutoff>_seed<k>.json.
Writes results/hindcast_scoreboard.csv, results/hindcast_cohort_chosen.json, figures/fig4_hindcast.png"""
import os, sys, json, subprocess, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); RES=ROOT+'/results/'; RAW=ROOT+'/data/raw/'
S=json.load(open(RES+'hindcast_simple.json')); ON,OG=S['obs']['N2023'],S['obs']['g']
t=pd.read_csv(RAW+'children-born-per-woman.csv'); OT=float(t[(t.Entity=='World')&(t.Year==2023)].iloc[0,-1])
a=pd.read_csv(RAW+'population-by-age-group.csv'); a=a[(a.Entity=='World')&(a.Year==2023)].iloc[0]; OO=float(a['Ages 65+']/a.iloc[3:].sum())
pop=pd.read_csv(RAW+'population.csv'); W=pop[pop.Entity=='World'].set_index('Year').iloc[:,-1]/1e9
rows=[]; chosen={}
for C in (1970,1990,2000):
    c=[json.load(open(RES+'hindcast_cohort_%d_seed%d.json'%(C,s))) for s in (1,2)]
    b=min(c,key=lambda d:(round(d['chi2'],2),d['seed'])); chosen[C]=b; f=b['forecast']   # lower fit-period misfit; exact tie -> seed 1
    rows.append(dict(cutoff=C,model='cohort (seed %d)'%b['seed'],N2023=f['N2023'],g=f['g'],TFR2023=f['TFR2023'],old2023=f['old2023'],note='Finf %.2f; peak %s'%(b['th']['Finf'],'%.1f Bn in %d'%(f['peak'],f['peak_year']) if f['peak_year']<2300 else 'none before 2300')))
    for k,v in S['results'][str(C)].items():
        rows.append(dict(cutoff=C,model=k,N2023=v['N2023'],g=v['g'],note=('diverges by %d'%v['blowup_by'] if v.get('blowup_by') and v['blowup_by']<=2023 else '')+(' constant at bound' if any(v.get('at_bound',[])) else '')))
T=pd.DataFrame(rows); T['err_N_pct']=100*(T.N2023/ON-1); T['err_g_pt']=100*(T.g-OG)
T.to_csv(RES+'hindcast_scoreboard.csv',index=False); json.dump({str(k):v for k,v in chosen.items()},open(RES+'hindcast_cohort_chosen.json','w'),indent=1)
print("observed 2023: N %.3f Bn, growth %.3f%%/yr, TFR %.3f, 65+ %.2f%%"%(ON,100*OG,OT,100*OO))
verdict={}
for C in (1970,1990,2000):
    x=T[T.cutoff==C]; co=x[x.model.str.startswith('cohort')].iloc[0]; nv=x[x.model.str.startswith('naive')]
    bN=all(abs(co.err_N_pct)<abs(e) for e in nv.err_N_pct); bG=all(abs(co.err_g_pt)<abs(e) for e in nv.err_g_pt); w5=abs(co.err_N_pct)<5
    verdict[C]=bool(bN and bG and w5); print("\ncutoff %d: beats all naive on N %s, on growth %s, within 5%% %s -> %s"%(C,bN,bG,w5,'PASS' if verdict[C] else 'FAIL'))
    print("| Model | 2023 population (Bn) | Error | Growth 2015–23 (%/yr) | Error (points) | Note |\n|---|---|---|---|---|---|")
    for _,r in x.iterrows():
        print("| %s | %s | %s | %s | %s | %s |"%(r.model,'%.2f'%r.N2023 if pd.notna(r.N2023) else '—','%+.1f%%'%r.err_N_pct if pd.notna(r.err_N_pct) else '—','%.2f'%(100*r.g) if pd.notna(r.g) else '—','%+.2f'%r.err_g_pt if pd.notna(r.err_g_pt) else '—',r.note))
    print("cohort TFR %.2f (obs %.2f), 65+ %.1f%% (obs %.1f%%)"%(co.TFR2023,OT,100*co.old2023,100*OO))
    b=chosen[C]; print("groups (n, obs 2023 Bn, model 2023 Bn, obs TFR, model TFR):",[(g_,v['n'],round(v['pop_2023'],2),round(b['forecast']['groupN2023'][j],2),round(v['TFR_2023'],2),round(b['forecast']['groupTFR2023'][j],2)) for j,(g_,v) in enumerate(b['groups'].items())])
print("\nPASS at both 1990 and 2000:",verdict[1990] and verdict[2000])
# ---- figure: trajectories ----
code="import os,sys,json,numpy as np\nsys.argv=['x'];g={'__name__':'m','__file__':%r};exec(open(%r).read(),g)\nth=np.array([json.load(open(%r))[os.environ['CUTOFF']]['th'][n] for n in g['NAMES']]);ts,o=g['run'](th,t_end=2100)\nprint(json.dumps([ts.tolist(),o[:,:,0].sum(1).tolist()]))"%(ROOT+'/hindcast/cohort_h.py',ROOT+'/hindcast/cohort_h.py',RES+'hindcast_cohort_chosen.json')
traj={C:json.loads(subprocess.run([sys.executable,'-c',code],env=dict(os.environ,CUTOFF=str(C)),capture_output=True,text=True,check=True).stdout) for C in (1970,1990,2000)}
INK,MUT,GRID='#0b0b0b','#52514e','#e6e5e1'; COL={1970:'#2a78d6',1990:'#eb6834',2000:'#1baf7a'}
plt.rcParams.update({'font.size':10,'axes.edgecolor':MUT,'axes.labelcolor':MUT,'xtick.color':MUT,'ytick.color':MUT})
fig,ax=plt.subplots(figsize=(8,4.8),facecolor='#fcfcfb'); ax.set_facecolor('#fcfcfb')
yo=np.arange(1950,2024); ax.plot(yo,W[yo],color=INK,lw=2.4,zorder=5); ax.annotate('observed',(1968,W[1968]),xytext=(-6,8),textcoords='offset points',ha='right',color=INK)
lab={1970:(2052,0.25),1990:(2052,-0.05),2000:(2052,-0.35)}
for C in (1970,1990,2000):
    ts,N=np.array(traj[C][0]),np.array(traj[C][1]); m=(ts>=C)&(ts<=2050); ax.plot(ts[m],N[m],color=COL[C],lw=2); ax.plot([C],[np.interp(C,ts,N)],'o',ms=7,color=COL[C],mec='#fcfcfb',mew=1.5,zorder=6)
    ax.text(2051,N[m][-1]+lab[C][1],'fitted to %d'%C,color=INK,va='center'); ax.plot([2050],[N[m][-1]],'s',ms=5,color=COL[C])
ax.plot([2023],[ON],'o',ms=8,color=INK,mec='#fcfcfb',mew=1.5,zorder=7); ax.annotate('2023: %.2f Bn'%ON,(2023,ON),xytext=(-8,10),textcoords='offset points',ha='right',color=INK)
ax.set_xlim(1950,2068); ax.set_ylim(2,11.5); ax.set_ylabel('World population (billions)'); ax.grid(axis='y',color=GRID,lw=0.8); ax.set_axisbelow(True)
for s_ in ('top','right'): ax.spines[s_].set_visible(False)
ax.set_title('Cohort model fitted only to data up to each cutoff, run forward',loc='left',color=INK,fontsize=11)
fig.tight_layout(); fig.savefig(ROOT+'/figures/fig4_hindcast.png',dpi=170); print('figure written')
