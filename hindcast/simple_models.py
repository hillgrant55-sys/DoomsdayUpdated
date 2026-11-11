"""Hindcast of single-equation world-population models and naive baselines.
Rules: hindcast/PREREGISTRATION.md. Output: results/hindcast_simple.json"""
import os, json, numpy as np, pandas as pd, warnings
from scipy.optimize import least_squares, differential_evolution
from scipy.integrate import solve_ivp
from scipy.special import expi
warnings.filterwarnings('ignore')
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); RAW=ROOT+'/data/raw/'
pop=pd.read_csv(RAW+'population.csv'); W=pop[pop.Entity=='World'].set_index('Year').iloc[:,-1]/1e9
GRID=np.array(list(range(0,1700,100))+list(range(1700,1950,10))+list(range(1950,2024,5)))
OBS_N=float(W[2023]); OBS_G=float(np.log(W[2023]/W[2015])/8)
def sig(t): return np.where(t<1500,0.15,np.where(t<1950,0.05,0.02))
def ode(rhs,N0,t0,tt):
    # finite-time blow-up: the solution is frozen once it passes 1000 Bn and reported as infinite from then on
    tu=np.unique(tt); s=solve_ivp(lambda t,n: [0.0] if (n[0]>1e3 or not np.isfinite(n[0])) else rhs(t,max(n[0],1e-9)),[t0,max(tu.max(),t0+1)],[N0],t_eval=tu,rtol=1e-7,atol=1e-11,method='LSODA')
    v=np.full(len(tu),np.nan); v[:len(s.t)]=s.y[0]; v[v>=1e3]=np.inf
    return v[np.searchsorted(tu,tt)]
def m_hyper(p,tt,t0f): K,k,t0=p; return np.where(t0-tt>0,K/np.maximum(t0-tt,1e-9)**k,np.inf)
def m_kap(p,tt,t0f): K,tau,T1=p; return (K/tau)*(np.pi/2-np.arctan((T1-tt)/tau))
def m_cap(p,tt,t0f): a,b,M,N0=p; return ode(lambda t,n: a*n**(1+b)*(1-n/M),N0,t0f,tt)
def m_zt(p,tt,t0f):
    # dN/dt=(N/tau)exp(KN) is separable: t(N)=t0+tau*[Ei(-K N)-Ei(-K N0)]; tabulate t(N) and invert by interpolation
    tau,K,N0=p; K=K if abs(K)>1e-9 else 1e-9
    Ng=N0*np.exp(np.linspace(0,np.log(1e3/N0),6000)); tg=t0f+tau*(expi(-K*Ng)-expi(-K*N0)); ok=np.isfinite(tg)
    v=np.exp(np.interp(tt,tg[ok],np.log(Ng[ok]),right=np.inf)); v[v>=999]=np.inf; return v
MODELS={'hyperbola':(m_hyper,[[180,1.0,2030],[300,1.2,2050],[100,0.8,2010]],([1,0.3,None],[1e5,3,2500])),
        'kapitza':(m_kap,[[180,45,2005],[200,40,1995],[160,60,2020]],([10,5,None],[1e4,400,2300])),
        'capped':(m_cap,[[0.005,1.0,11,0.2],[0.003,1.5,20,0.25],[0.01,0.5,9,0.2]],([1e-6,0.0,None,0.01],[1.0,4.0,200,3.0])),
        'exp_rate':(m_zt,[[2000,0.5,0.2],[1500,0.3,0.25],[3000,1.0,0.2]],([10,-5,0.01],[1e5,5,3.0]))}
out={}
for C in (1970,1990,2000):
    out[C]={}
    for win,t0f in (('from_0',0),('from_1650',1650)):
        tt=GRID[(GRID>=t0f)&(GRID<=C)].astype(float); y=np.log(W[tt.astype(int)].values); s=sig(tt)
        for name,(f,starts,(lo,hi)) in MODELS.items():
            lo=list(lo); hi=list(hi)
            if name=='hyperbola': lo[2]=C+0.5
            if name=='kapitza': lo[2]=1900
            if name=='capped': lo[2]=float(W[C])*1.001
            if name in('capped','exp_rate'): starts=[st[:-1]+[float(W[int(tt[0])])] for st in starts]
            def res(p):
                v=f(p,tt,t0f); r=(np.log(np.maximum(v,1e-12))-y)/s; r[~np.isfinite(r)]=50; return np.clip(r,-50,50)
            best=None
            # global search (differential evolution on the robustified misfit) plus the hand-chosen starts, each polished by least squares
            lg=[i for i in range(len(lo)) if lo[i]>0 and hi[i]/lo[i]>100]
            def unp(x):
                p=np.array(x,float); p[lg]=np.exp(p[lg]); return p
            bb=[(np.log(lo[i]),np.log(hi[i])) if i in lg else (lo[i],hi[i]) for i in range(len(lo))]
            if name in ('hyperbola','kapitza'):   # closed form: cheap enough for differential evolution
                de=differential_evolution(lambda x: float(np.sum(np.log1p(res(unp(x))**2))),bb,popsize=12,maxiter=150,tol=1e-9,seed=1,polish=False); extra=[unp(de.x)]
            else:                                  # ODE models: 12 random starts drawn uniformly in the (log) box
                rng=np.random.default_rng(1); extra=[unp([rng.uniform(l_,h_) for l_,h_ in bb]) for _ in range(12)]
            for st in extra+starts:
                st=np.clip(st,np.array(lo)*1.0001+1e-12,np.array(hi)*0.9999)
                try: r=least_squares(res,st,bounds=(lo,hi),x_scale=np.maximum(np.abs(st),1e-3))
                except Exception as e_: print('  fit error',C,win,name,repr(e_)[:200]); continue
                if best is None or r.cost<best.cost: best=r
            tp=np.array([float(tt[0]),2015.0,2023.0]) if name in('capped','exp_rate') else np.array([2015.0,2023.0])
            v=f(best.x,tp,t0f); n15,n23=v[-2],v[-1]
            ok=np.isfinite(n23) and np.isfinite(n15) and n23>0 and n15>0
            tb=np.arange(float(C),2301.0); vb=f(best.x,tb,t0f) if name not in('capped','exp_rate') else f(best.x,np.concatenate([[float(tt[0])],tb]),t0f)[1:]
            bad=~np.isfinite(vb)|(vb>1e3); blow=float(tb[np.argmax(bad)]) if bad.any() else None
            out[C][name+'/'+win]=dict(blowup_by=blow,params=[float(x) for x in best.x],rms_fit=float(np.sqrt(np.mean((best.fun*s)**2))),N2023=float(n23) if ok else None,
                err_N=float(n23/OBS_N-1) if ok else None,g=float(np.log(n23/n15)/8) if ok else None,at_bound=[bool(min(x-l,h-x)<1e-6*max(1,abs(x))) for x,l,h in zip(best.x,lo,hi)])
    # naive baselines
    g5=np.log(W[C]/W[C-5])/5; inc=(W[C]-W[C-5])/5
    yrs=np.arange(C-20,C+1,5); gr=np.log(W[yrs[1:]].values/W[yrs[:-1]].values)/5; mid=(yrs[1:]+yrs[:-1])/2; sl,ic=np.polyfit(mid,gr,1)
    def trend(T):
        t=np.arange(C,T)+0.5; return float(W[C]*np.exp(np.sum(np.maximum(sl*t+ic,0.0))))
    nb={'naive_const_growth':(float(W[C]*np.exp(g5*(2023-C))),float(g5)),'naive_const_increment':(float(W[C]+inc*(2023-C)),float(np.log((W[C]+inc*(2023-C))/(W[C]+inc*(2015-C)))/8)),
        'naive_rate_trend':(trend(2023),float(np.log(trend(2023)/trend(2015))/8))}
    for k,(n,g) in nb.items(): out[C][k]=dict(N2023=n,err_N=n/OBS_N-1,g=g)
json.dump(dict(obs=dict(N2023=OBS_N,g=OBS_G),results=out),open(ROOT+'/results/hindcast_simple.json','w'),indent=1)
print("observed: N2023 %.3f Bn, growth 2015-23 %.3f%%/yr"%(OBS_N,100*OBS_G))
for C in out:
    print("cutoff",C)
    for k,v in out[C].items():
        print("  %-26s N2023 %s  err %s  g %s  %s"%(k,'%7.2f'%v['N2023'] if v['N2023'] else '   none','%+7.1f%%'%(100*v['err_N']) if v['err_N'] is not None else '    n/a','%.2f%%'%(100*v['g']) if v['g'] is not None else 'n/a',('fit rms %.3f'%v['rms_fit']+(' BOUND' if any(v['at_bound']) else '')) if 'rms_fit' in v else ''))
