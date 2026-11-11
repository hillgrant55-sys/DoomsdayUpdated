import sys, json, numpy as np, pandas as pd
src=open('/home/claude/work/proj4.py').read().split('\nif __name__=="__main__":')[0].replace("AMAX=int(sys.argv[2]) if len(sys.argv)>2 else 110; sys.argv=sys.argv[:2]","AMAX=180")
exec(src)
F=json.load(open('final4.json')); th=np.array(F['th']); g,beta,delta=th[:3]; res={}
d0,ts,o=dates(th); res['baseline']=d0; print("baseline(AMAX=180)",{k:round(float(v),2) for k,v in d0.items()})
N0=o[:,:,0].sum(1); L0=o[:,:,4].sum(1); r0=o[:,0,7]
# decline rate
i1,i2=np.where(ts==2300)[0][0],np.where(ts==2500)[0][0]; rdec=np.log(N0[i2]/N0[i1])/200; print("asymptotic decline %.3f%%/yr, halving %.0f yr; people at regress %.3f Bn"%(100*rdec,np.log(2)/-rdec,np.interp(d0['regress'],ts,N0)))
res['decline_rate']=rdec; res['N_at_regress']=float(np.interp(d0['regress'],ts,N0))
# --- machines hold the effective workforce at its peak
class Hold:
    def __init__(s): s.pk=0
    def __call__(s,tt,T,L):
        s.pk=max(s.pk,L); return (s.pk-L) if tt>=2030 else 0.0
dA,tsA,oA=dates(th,machines=Hold()); res['ai_hold']=dA; print("AI hold:",{k:round(float(v),2) for k,v in dA.items()})
# --- self-improving machines: M = f0 * L(2030) * T_A/T_A(2030); integrate capability with baseline workforce
def singular(f0,t0=2030):
    Lf=lambda t: np.interp(t,ts,L0); lT=0.0; t=t0; dt=0.002; M0=f0*Lf(t0)
    while t<2600:
        rate=g*(Lf(t)+M0*np.exp(lT))**beta-delta
        if rate>10: return t
        lT+=rate*dt; t+=dt
    return np.nan
for f0 in (0.01,0.1,1.0): res['sing_%g'%f0]=singular(f0); print("self-improving machines, initial share %g of workforce in 2030: singular at %.2f  %s"%(f0,res['sing_%g'%f0],todate(res['sing_%g'%f0])))
# --- longevity: limit schedule stretched by 132/82 between 2040 and 2100
kmax=1.61; st=lambda tt: 1.0 if tt<2040 else (kmax if tt>=2100 else 1+(kmax-1)*(tt-2040)/60)
for nm,wt in (("long_retire65",65),("long_work115",115)):
    dl,tsl,ol=dates(th,stretch=st,work_to=wt); res[nm]=dl; print(nm,{k:round(float(v),2) for k,v in dl.items()},"e0 2200 %.1f"%ol[tsl==2200,0,2][0])
    if wt==115: oL=ol
    else: oL65=ol
print("space: two isolated halves make %.3f of the progress of the whole; self-sustaining colony needs %.0f M workers = %.0f M people at support ratio %.3f"%(2**(1-beta),1e3*F['Lstar'],1e3*F['Lstar']/d0['support_min'],d0['support_min']))
json.dump({k:(v if not isinstance(v,dict) else {a:float(b) for a,b in v.items()}) for k,v in res.items()},open('scen4.json','w'),default=float)
np.savez('scen4.npz',ts=ts,o=o,oA=oA,oL=oL,oL65=oL65)
