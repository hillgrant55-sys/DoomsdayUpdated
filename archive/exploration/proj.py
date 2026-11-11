import sys, json, numpy as np, datetime
exec(open('/home/claude/work/model.py').read().split('if __name__=="__main__" and')[0])
import warnings; warnings.filterwarnings('ignore')
best=json.load(open('best.json')); th0=np.array(best['th']); print("free fit chi2 %.1f dof %d"%(best['chi2'],best['dof'])); print(dict(zip(NAMES,np.round(th0,4)))); print(dict(zip(NAMES,np.round(best['err'],4))))
def cross(ts,N,level,after):
    k=np.where((ts[1:]>after)&(N[1:]<level)&(N[:-1]>=level))[0]
    if not len(k): return np.nan
    i=k[0]; return ts[i]+5*np.log(N[i]/level)/np.log(N[i]/N[i+1])
out={}
for Ff in (None,2.02,1.8,1.6,1.45,1.35,1.2):
    if Ff is None: th=th0; chi=best['chi2']
    else:
        st=[list(th0)]+STARTS[:0]; th,r,idx=fit({"Finf":Ff},starts=[list(th0),[0.0043,1.6,0.3,0.1,0.6,2.5,Ff,0.184,0.0056],[0.0043,1.6,0.16,0.06,2.0,1.2,Ff,0.184,0.0056]]); chi=2*r.cost
    ts,o=run(*th,t_end=6000); N=o[:,0]; ip=np.argmax(N[ts<=2600]); s=stats(th)
    d=dict(th=list(th),chi2=chi,stats=s,peak=float(N[ip]),peak_year=int(ts[ip]),N2050=float(N[ts==2050][0]),N2100=float(N[ts==2100][0]),N2200=float(N[ts==2200][0]),
           half=cross(ts,N,N[ip]/2,ts[ip]),below1bn=cross(ts,N,1.0,ts[ip]),below1M=cross(ts,N,1e-3,ts[ip]),last=cross(ts,N,1e-9,ts[ip]),
           r_asym=float(np.log(N[ts==2600][0]/N[ts==2500][0])/100) , tfr2023=float(np.interp(2023,ts,o[:,3])), e2023=float(np.interp(2023,ts,o[:,4])))
    out[str(Ff)]=d
    print("\nFinf=%s chi2=%.1f | peak %.2f Bn in %d | 2050 %.2f 2100 %.2f 2200 %.2f | half-peak %.0f | <1Bn %.0f | <1M %.0f | N<1: %.1f | r=%.2f%%/yr | TFR23 %.2f e0_23 %.1f"%(Ff,chi,d['peak'],d['peak_year'],d['N2050'],d['N2100'],d['N2200'],d['half'],d['below1bn'],d['below1M'],d['last'],100*d['r_asym'],d['tfr2023'],d['e2023']))
    print("   ",dict(zip(NAMES,np.round(th,4))),{k:round(v,3) for k,v in s.items()})
    np.save('traj_%s.npy'%Ff,np.c_[ts,o])
json.dump(out,open('proj.json','w'))
