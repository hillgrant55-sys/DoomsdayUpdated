"""Three-group, two-variable cohort Doomsday model.
Groups (fixed country sets): A early fertility decline (TFR<3 in 1975), B middle (TFR<3 by 2010), C late.
Each group j: 5-yr cohorts n_j, capability T_j with dT_j/dt = s_j g N_world^beta T_j (s_A=1), y_j=T_j/N_j.
  m = 1-(1+(y-1)/yM)^-a ; hazard = premodern^(1-m) limit^m ; TFR = Finf+(F0-Finf)/(1+((y-1)/yF)^b)
  premodern hazard scaled so that TFR=F0 is exactly replacement at y=1. Extra hazard d in 1915-1949."""
import sys, json, numpy as np, pandas as pd, warnings
from scipy.optimize import least_squares, brentq
warnings.filterwarnings('ignore')
U=sys.argv[1]
A_=110; ages=np.arange(A_)
def siler(a1,b1,a2,a3,b3): return a1*np.exp(-b1*ages)+a2+a3*np.exp(b3*ages)
LP0=np.log(siler(0.28,0.45,0.007,0.0004,0.072)); LM=np.log(siler(0.003,1.0,0.0001,1.0e-5,0.105))
G=22; gmid=5*np.arange(G)+2.5
phi=np.clip(1-np.abs(gmid-28)/14.0,0,None); phi[(gmid<15)|(gmid>50)]=0; phi/=phi.sum()
def tab(lp,m):
    mu=np.exp((1-m)*lp+m*LM); cum=np.concatenate([[0],np.cumsum(mu)[:-1]]); Lmid=np.exp(-cum-mu/2)
    surv=np.zeros(G); surv[:-1]=Lmid[7::5][:G-1]/Lmid[2::5][:G-1]; return surv,Lmid[:5].mean(),Lmid.sum()
def nrr(lp,m):
    surv,sb,_=tab(lp,m); return 0.5*np.dot(phi,sb*np.concatenate([[1.0],np.cumprod(surv[:-1])]))
FREP=1/nrr(LP0,1.0); MG=np.linspace(0,1,201)
def _lmid(m):
    mu=np.exp((1-m)*LP0+m*LM); cum=np.concatenate([[0],np.cumsum(mu)[:-1]]); return np.exp(-cum-mu/2)
LMID0=np.array([_lmid(m) for m in MG])                       # (201,110); scaling premodern hazard by e^c => Lmid^(e^(c(1-m)))
def _from_lmid(Lm):
    surv=np.zeros((Lm.shape[0],G)); surv[:,:-1]=Lm[:,7::5][:,:G-1]/Lm[:,2::5][:,:G-1]; return surv,Lm[:,:5].mean(1),Lm.sum(1)
def _nrr0(c):
    surv,sb,_=_from_lmid(LMID0[:1]**np.exp(c)); return 0.5*np.dot(phi,sb[0]*np.concatenate([[1.0],np.cumprod(surv[0][:-1])]))
def tables(F0):
    c=brentq(lambda lc: F0*_nrr0(lc)-1,-3,3,xtol=1e-10); return _from_lmid(LMID0**np.exp(c*(1-MG))[:,None])
NAMES=['g','beta','a','yM','yF','b','Finf','F0','d','sB','sC','N0A','N0B','N0C']; J=3; T_START=-300
def run(th,t_end=2025,dt=5):
    g,beta,a,yM,yF,b,Finf,F0,d,sB,sC,N0A,N0B,N0C=th
    SURV,SB,E0T=tables(F0); s=np.array([1.0,sB,sC]); N0=np.array([N0A,N0B,N0C])
    L=SB[0]*np.concatenate([[1.0],np.cumprod(SURV[0][:-1])]); n=np.outer(N0,L/L.sum()); T=N0.copy()
    ts=np.arange(T_START,t_end+1,dt); out=np.empty((len(ts),J,4))
    for i,tt in enumerate(ts):
        N=n.sum(1); Nw=N.sum(); z=np.maximum(T/np.maximum(N,1e-300)-1,0.0)
        m=1-(1+z/yM)**(-a); F=Finf+(F0-Finf)/(1+(z/yF)**b)
        u=m*200; k=np.minimum(u.astype(int),199); w=(u-k)[:,None]
        surv=SURV[k]*(1-w)+SURV[k+1]*w; sb=SB[k]*(1-w[:,0])+SB[k+1]*w[:,0]; e0=E0T[k]*(1-w[:,0])+E0T[k+1]*w[:,0]
        x=np.exp(-d*dt) if 1915<=tt<1950 else 1.0
        births=0.5*F*(n@phi); nn=np.empty_like(n); nn[:,0]=births*sb*x; nn[:,1:]=n[:,:-1]*surv[:,:-1]*x
        out[i,:,0]=N; out[i,:,1]=F; out[i,:,2]=e0; out[i,:,3]=births/dt
        n=nn; T=T*np.exp(np.minimum(s*g*Nw**beta*dt,50.0))
    return ts,out
# ---------------- data ----------------
R=pd.read_csv('/home/claude/work/groups.csv'); pop=pd.read_csv(U+'/80cc69c6-population.csv'); W=pop[pop.Entity=='World'].set_index('Year').Population/1e9
e0d=pd.read_csv(U+'/7c8d2eca-life-expectancy.csv'); EW=e0d[e0d.Entity=='World'].set_index('Year')['Life expectancy']
tfd=pd.read_csv(U+'/abab83cc-children-born-per-woman.csv'); TW=tfd[tfd.Entity=='World'].set_index('Year').iloc[:,-1]
tN=np.array(list(range(0,1700,100))+list(range(1700,1950,10))+list(range(1950,2021,5))+[2023])
tr=np.array(list(range(1950,2021,5))+[2023]); tEw=np.array([1770,1800,1820,1850,1870,1900,1913])
sm=lambda S,y: S.loc[max(y-2,1950):min(y+2,2023)].mean()
D={}
for j,gname in enumerate('ABC'):
    x=R[R.g==gname].set_index('Year'); D[j]=dict(N=x.Pop[tN].values,am=np.log(x.Pop[tr].values[1:]/x.Pop[tr].values[:-1])/np.diff(tr),TFR=np.array([sm(x.TFR,y) for y in tr]),e0=np.array([sm(x.e0,y) for y in tr]))
sigN=np.where(tN<1500,0.30,np.where(tN<1950,0.08,0.02)); sigW=np.where(tN<1500,0.15,0.05); pre=tN<1950
def pieces(th):
    ts,o=run(th); lN=np.log(np.maximum(o[:,:,0],1e-300)); r={}; 
    for j in range(J):
        a=np.interp(tr,ts,lN[:,j])
        r[j]=dict(N=np.interp(tN,ts,lN[:,j])-np.log(D[j]['N']),rate=np.diff(a)/np.diff(tr)-D[j]['am'],TFR=np.interp(tr,ts,o[:,j,1])/D[j]['TFR']-1,e0=np.interp(tr,ts,o[:,j,2])/D[j]['e0']-1)
    Nw=o[:,:,0].sum(1); ew=(o[:,:,0]*o[:,:,2]).sum(1)/Nw
    r['w']=dict(N=np.interp(tN[pre],ts,np.log(Nw))-np.log(W[tN[pre]].values),e0=np.interp(tEw,ts,ew)/EW[tEw].values-1)
    return ts,o,r
def resid(th):
    try: ts,o,r=pieces(th)
    except Exception: return np.full(3*(len(tN)+3*len(tr)-1)+pre.sum()+len(tEw),30.0)
    v=np.concatenate([np.concatenate([r[j]['N']/sigN,r[j]['rate']/0.0015,r[j]['TFR']/0.05,r[j]['e0']/0.04]) for j in range(J)]+[r['w']['N']/sigW[pre],r['w']['e0']/0.04])
    v[~np.isfinite(v)]=30.0; return np.clip(v,-30,30)
LO=np.array([5e-4,0.5,0.02,0.005,0.02,0.4,0.6,5.0,0.0,0.3,0.3,0.01,0.05,0.005]); HI=np.array([0.03,4.0,5,30,30,8,2.6,7.5,0.015,1.5,1.5,0.1,0.3,0.1])
XS=np.array([0.005,1,0.3,0.1,1,1,1,3,0.003,0.5,0.5,0.03,0.1,0.02])
def summary(th):
    ts,o,r=pieces(th); f=lambda x: float(np.sqrt(np.mean(np.asarray(x)**2)))
    s={('grp '+'ABC'[j]): dict(lnN_pre1500=round(f(r[j]['N'][tN<1500]),3),lnN_1500_1949=round(f(r[j]['N'][(tN>=1500)&pre]),3),lnN_1950on=round(f(r[j]['N'][~pre]),3),rate_pct=round(100*f(r[j]['rate']),3),TFR=round(f(r[j]['TFR']),3),e0=round(f(r[j]['e0']),3)) for j in range(J)}
    Nw=o[:,:,0].sum(1); lw=np.interp(tr,ts,np.log(Nw)); amw=np.log(W[tr].values[1:]/W[tr].values[:-1])/np.diff(tr)
    Fw=o[:,:,3].sum(1)/ (o[:,:,3]/o[:,:,1]).sum(1)      # births-consistent world TFR
    s['world']=dict(lnN_pre1500=round(f(r['w']['N'][tN[pre]<1500]),3),lnN_1500_1949=round(f(r['w']['N'][tN[pre]>=1500]),3),lnN_1950on=round(f(np.interp(tN[~pre],ts,np.log(Nw))-np.log(W[tN[~pre]].values)),3),
        rate_rel=round(f((np.diff(lw)/np.diff(tr)-amw)/amw),3),TFR=round(f(np.interp(tr,ts,Fw)/np.array([sm(TW,y) for y in tr])-1),3),e0=round(f(np.interp(tr,ts,(o[:,:,0]*o[:,:,2]).sum(1)/Nw)/np.array([sm(EW,y) for y in tr])-1),3))
    return s
if __name__=="__main__":
    import time
    th=[0.0043,1.6,0.16,0.05,1.0,1.8,1.45,6.2,0.004,0.7,0.6,0.03,0.17,0.02]; t0=time.time(); r=resid(np.array(th)); print("eval %.1f ms, n=%d, chi2=%.0f, Frep=%.3f"%(1e3*(time.time()-t0),len(r),r@r,FREP))
    t0=time.time(); r=resid(np.array(th)); print("cached eval %.1f ms"%(1e3*(time.time()-t0))); print(json.dumps(summary(th),indent=0))
