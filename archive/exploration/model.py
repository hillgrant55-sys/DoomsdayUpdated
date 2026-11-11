"""Two-variable cohort Doomsday model, refit on the uploaded OWID/UN world series.
State: 5-yr age groups n, capability T. y=T/N.  dT/dt = g N^beta T
  mortality progress m = 1-(1+(y-1)/yM)^-a ; hazard = premodern^(1-m) * limit^m ; extra hazard d in 1915-1949
  TFR F = Finf + (F0-Finf)/(1+((y-1)/yF)^b)"""
import sys, json, numpy as np, pandas as pd
from scipy.optimize import least_squares
U=sys.argv[1]
A=110; ages=np.arange(A)
def siler(a1,b1,a2,a3,b3): return a1*np.exp(-b1*ages)+a2+a3*np.exp(b3*ages)
LP=np.log(siler(0.28,0.45,0.007,0.0004,0.072)); LM=np.log(siler(0.003,1.0,0.0001,1.0e-5,0.105))
G=22; gmid=5*np.arange(G)+2.5
phi=np.clip(1-np.abs(gmid-28)/14.0,0,None); phi[(gmid<15)|(gmid>50)]=0; phi/=phi.sum()
def table(m):
    mu=np.exp((1-m)*LP+m*LM); cum=np.concatenate([[0],np.cumsum(mu)[:-1]]); Lmid=np.exp(-cum-mu/2)
    surv=np.zeros(G); surv[:-1]=Lmid[7::5][:G-1]/Lmid[2::5][:G-1]; return surv,Lmid[:5].mean(),Lmid
def nrrF(m):
    surv,sb,_=table(m); L=sb*np.concatenate([[1.0],np.cumprod(surv[:-1])])   # exact survivorship of the 5-yr projection
    return 0.5*np.dot(phi,L)
F0=1/nrrF(0.0); FREP=1/nrrF(1.0)
MG=np.linspace(-0.2,1,601); _t=[table(m) for m in MG]
SURV=np.array([x[0] for x in _t]); SB=np.array([x[1] for x in _t]); E0T=np.array([x[2].sum() for x in _t])
def fast(m):
    u=(min(max(m,-0.2),1.0)+0.2)/1.2*600; i=min(int(u),599); w=u-i
    return SURV[i]*(1-w)+SURV[i+1]*w, SB[i]*(1-w)+SB[i+1]*w, E0T[i]*(1-w)+E0T[i+1]*w
T_START=-300
def run(g,beta,a,yM,yF,b,Finf,N0,d,t_end=2025,dt=5):
    sv,sb0,_=table(0); L=sb0*np.concatenate([[1.0],np.cumprod(sv[:-1])]); n=N0*L/L.sum(); T=N0
    ts=np.arange(T_START,t_end+1,dt); out=np.empty((len(ts),7))
    for i,tt in enumerate(ts):
        N=n.sum(); y=T/N; z=max(y-1,0.0)
        m=1-(1+z/yM)**(-a); F=Finf+(F0-Finf)/(1+(z/yF)**b)
        surv,sb,e0m=fast(m); x=np.exp(-d*dt) if 1915<=tt<1950 else 1.0
        births=0.5*F*np.dot(phi,n); nn=np.empty(G); nn[0]=births*sb*x; nn[1:]=n[:-1]*surv[:-1]*x
        out[i]=(N,births/N/dt,(N+births-nn.sum())/N/dt,F,e0m,y,m); n=nn; T*=np.exp(g*N**beta*dt)
        if N<1e-10: out[i+1:]=out[i]; out[i+1:,0]=0; break
    return ts,out
# ---------- data ----------
pop=pd.read_csv(U+'/80cc69c6-population.csv'); W=pop[pop.Entity=='World'].set_index('Year').Population/1e9
tfr=pd.read_csv(U+'/abab83cc-children-born-per-woman.csv'); TF=tfr[tfr.Entity=='World'].set_index('Year').iloc[:,-1]
e0d=pd.read_csv(U+'/7c8d2eca-life-expectancy.csv'); E=e0d[e0d.Entity=='World'].set_index('Year')['Life expectancy']
tN=np.array(list(range(0,1700,100))+list(range(1700,1950,10))+list(range(1950,2021,5))+[2023]); Nobs=W[tN].values
sig=np.where(tN<1500,0.15,np.where(tN<1950,0.05,0.02))
tr=np.array(list(range(1950,2021,5))+[2023]); am=np.log(W[tr].values[1:]/W[tr].values[:-1])/np.diff(tr); trm=(tr[1:]+tr[:-1])/2
tT=tr.copy(); TFo=np.array([TF.loc[max(y-2,1950):min(y+2,2023)].mean() for y in tT])      # 5-yr smoothed
tE=np.array([1770,1800,1820,1850,1870,1900,1913,1950,1955,1965,1970,1975,1980,1985,1990,1995,2000,2005,2010,2015,2019,2023]); Eo=E[tE].values
def pieces(th):
    ts,o=run(*th); lN=np.interp(tN,ts,np.log(np.maximum(o[:,0],1e-12))); lr=np.interp(tr,ts,np.log(np.maximum(o[:,0],1e-12)))
    return ts,o,(lN-np.log(Nobs)), (np.diff(lr)/np.diff(tr)-am)/am, (np.interp(tT,ts,o[:,3])-TFo)/TFo, (np.interp(tE,ts,o[:,4])-Eo)/Eo
NAMES=['g','beta','a','yM','yF','b','Finf','N0','d']
LO=np.array([1e-4,0.3,0.05,0.01,0.02,0.5,0.5,0.03,0.0]); HI=np.array([0.05,4.0,10,50,50,8,3.0,0.5,0.02]); XS=np.array([0.005,1,1,0.5,0.3,2,2,0.2,0.003])
def resid(free,fixed):
    th=np.array([fixed.get(n,np.nan) for n in NAMES]); th[np.isnan(th)]=free
    try: ts,o,rN,rr,rT,rE=pieces(th)
    except Exception: return np.full(len(tN)+len(am)+len(tT)+len(tE),30.0)
    r=np.concatenate([rN/sig,rr/0.10,rT/0.05,rE/0.04]); r[~np.isfinite(r)]=30.0; return r
STARTS=[[0.006,1.5,1.5,1.0,0.36,2.6,2.0,0.2,0.005],[0.006,2.0,2.5,1.0,0.25,1.6,1.8,0.21,0.005],[0.005,1.2,1.0,0.5,0.5,2,1.6,0.19,0.005],[0.007,1.8,0.6,0.2,0.3,2,1.5,0.2,0.003],[0.0055,1.0,1.5,1.0,0.36,2.6,2.0,0.1,0.007],[0.008,2.5,1.5,0.5,0.3,2,1.8,0.21,0.004]]
def fit(fixed={},starts=STARTS):
    idx=[i for i,n in enumerate(NAMES) if n not in fixed]; best=None
    for s in starts:
        r=least_squares(resid,np.array(s)[idx],bounds=(LO[idx],HI[idx]),x_scale=XS[idx],args=(fixed,))
        if best is None or r.cost<best.cost: best=r
    th=np.array([fixed.get(n,np.nan) for n in NAMES]); th[np.isnan(th)]=best.x; return th,best,idx
def stats(th):
    ts,o,rN,rr,rT,rE=pieces(th); f=lambda x: np.sqrt(np.mean(x**2))
    return dict(lnN_pre1500=f(rN[tN<1500]),lnN_1500_1949=f(rN[(tN>=1500)&(tN<1950)]),lnN_1950on=f(rN[tN>=1950]),rate=f(rr),TFR=f(rT),e0=f(rE))
if __name__=="__main__" and len(sys.argv)>2:
    th=STARTS[0]; ts,o=run(*th); print('e0 pre',E0T[100],'F0',F0); k=(ts%250==0)|(ts>1900)&(ts%25==0)
    print(np.c_[ts[k],np.round(o[k][:,[0,3,4,5,6]],3)]); print(stats(th)); sys.exit()
if __name__=="__main__":
    print("F0=%.2f replacement at limit mortality=%.3f"%(F0,FREP))
    res={}
    for name,fx in (("free",{}),("beta1",{"beta":1.0})):
        th,r,idx=fit(fx); chi=2*r.cost; dof=len(r.fun)-len(idx)
        try: err=np.sqrt(np.diag(np.linalg.inv(r.jac.T@r.jac)*chi/dof))
        except Exception: err=np.full(len(idx),np.nan)
        print(name,"chi2=%.1f dof=%d"%(chi,dof)); print("  ",dict(zip(NAMES,np.round(th,4)))); print("   err",dict(zip([NAMES[i] for i in idx],np.round(err,4)))); print("  ",{k:round(v,3) for k,v in stats(th).items()})
        res[name]=dict(th=list(th),chi2=chi,err=list(err))
    json.dump(res,open('/home/claude/work/fit.json','w'))
