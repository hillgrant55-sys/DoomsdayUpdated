"""Doomsday model v4: three groups, cohorts, productivity with maintenance cost.
Group j (A early, B middle, C late fertility decline), 5-yr cohorts n_j, productivity A_j.
  workforce L_j = ages 15-64, support ratio sig_j = L_j/N_j
  living standard   y_j = A_j (sig_j/sig0_j) (N0_j/N_j)^gam            (gam = share of fixed resources)
  progress          dlnA_j/dt = s_j delta (R-1) + kap delta R max(m_j,0) ln(A_A/A_j),   R = ((L_w+M)/Leq)^beta A_A^-theta
                    (delta = maintenance cost; Leq = workforce that just maintains premodern capability A=1)
  mortality         m_j = 1-(1+zeff/yM)^-a,  zeff = z_j^(1-om) z_A^om,  z = max(y-1,0); hazard = premodern^(1-m) limit^m
  fertility         F_j = Finf + (F0_j-Finf)/(1+(q/qF)^b),  q = m/(1-m)
  premodern hazard scaled per group so TFR=F0_j is replacement at m=0; extra hazard D_SHOCK in 1915-1949."""
import sys, json, numpy as np, pandas as pd, warnings
from scipy.optimize import least_squares, brentq
warnings.filterwarnings('ignore')
U=sys.argv[1]; W_='/home/claude/work/'
A_=110; G=A_//5; LIM_SHIFT=0; WORK_HI=13; GAM=1/3; D_SHOCK=0.002          # scenario switches (overridden by exec-replace)
ages=np.arange(A_)
def siler(a1,b1,a2,a3,b3,x): return a1*np.exp(-b1*x)+a2+a3*np.exp(b3*x)
LP0=np.log(siler(0.28,0.45,0.007,0.0004,0.072,ages)); LM=np.log(siler(0.003,1.0,0.0001,1.0e-5,0.105,np.maximum(ages-LIM_SHIFT,0)*np.where(ages<LIM_SHIFT,0.0,1.0)+np.where(ages<LIM_SHIFT,np.minimum(ages,30.0),0.0)*0+0.0)) if LIM_SHIFT==0 else None
if LIM_SHIFT:   # senescence delayed by LIM_SHIFT years: infant term unchanged, ageing term shifted
    LM=np.log(0.003*np.exp(-1.0*ages)+0.0001+1.0e-5*np.exp(0.105*np.maximum(ages-LIM_SHIFT,0)))
gmid=5*np.arange(G)+2.5
phi=np.zeros(G); phi[2:11]=json.load(open(W_+'phi.json'))['phi']          # observed world distribution of births by mother's age, 1950-2023
MG=np.linspace(-0.5,1,301)
def _lmid(m):
    mu=np.exp((1-m)*LP0+m*LM); cum=np.concatenate([[0],np.cumsum(mu)[:-1]]); return np.exp(-cum-mu/2)
LMID0=np.array([_lmid(m) for m in MG])
def _from_lmid(Lm):
    surv=np.zeros((Lm.shape[0],G)); surv[:,:-1]=Lm[:,7::5][:,:G-1]/Lm[:,2::5][:,:G-1]; return surv,Lm[:,:5].mean(1),Lm.sum(1)
def _nrr0(c):
    surv,sb,_=_from_lmid(LMID0[100:101]**np.exp(c)); return 0.5*np.dot(phi,sb[0]*np.concatenate([[1.0],np.cumprod(surv[0][:-1])]))
def tables(F0):
    c=brentq(lambda lc: F0*_nrr0(lc)-1,-4,4,xtol=1e-10); return _from_lmid(LMID0**np.exp(c*(1-MG))[:,None])
s_,sb_,_=_from_lmid(LMID0[-1:]); FREP=1/(0.5*np.dot(phi,sb_[0]*np.concatenate([[1.0],np.cumprod(s_[0][:-1])]))); E0LIM=float(_from_lmid(LMID0[-1:])[2][0])
NAMES=['Leq','beta','theta','delta','a','yM','om','qF','b','Finf','F0A','F0B','F0C','sB','sC','kap','N0A','N0B','N0C']; J=3; T_START=-300
def run(th,t_end=2025,dt=5,mach=0.0,t_mach=2025,state=None):
    Leq,beta,theta,delta,a,yM,om,qF,b,Finf,F0A,F0B,F0C,sB,sC,kap,N0A,N0B,N0C=th
    F0=np.array([F0A,F0B,F0C]); tb=[tables(f) for f in F0]; SURV=np.array([t[0] for t in tb]); SB=np.array([t[1] for t in tb]); E0T=np.array([t[2] for t in tb])
    s=np.array([1.0,sB,sC]); N0=np.array([N0A,N0B,N0C]); jj=np.arange(J)
    L=SB[:,100,None]*np.concatenate([np.ones((J,1)),np.cumprod(SURV[:,100,:-1],axis=1)],axis=1); n=N0[:,None]*L/L.sum(1,keepdims=True); A=np.ones(J)
    sig0=n[:,3:WORK_HI].sum(1)/n.sum(1); ts=np.arange(T_START,t_end+1,dt); out=np.empty((len(ts),J,8)); Mref=None; aux=np.empty((len(ts),3))
    for i,tt in enumerate(ts):
        N=n.sum(1); Lj=n[:,3:WORK_HI].sum(1); Lw=Lj.sum(); sig=Lj/np.maximum(N,1e-300)
        y=A*(sig/sig0)*(N0/np.maximum(N,1e-300))**GAM; z=np.maximum(y-1,0.0); zeff=z**(1-om)*z[0]**om
        m=np.where(y<1,np.maximum(y-1,-0.5),1-(1+zeff/yM)**(-a)); q=np.maximum(m,0)/np.maximum(1-m,1e-12); F=Finf+(F0-Finf)/(1+(q/qF)**b)
        u=(m+0.5)*200; k=np.minimum(u.astype(int),299); w=(u-k)[:,None]
        surv=SURV[jj,k]*(1-w)+SURV[jj,k+1]*w; sb=SB[jj,k]*(1-w[:,0])+SB[jj,k+1]*w[:,0]; e0=E0T[jj,k]*(1-w[:,0])+E0T[jj,k+1]*w[:,0]
        x=np.exp(-D_SHOCK*dt) if 1915<=tt<1950 else 1.0
        births=0.5*F*(n@phi); nn=np.empty_like(n); nn[:,0]=births*sb*x; nn[:,1:]=n[:,:-1]*surv[:,:-1]*x
        M=0.0
        if mach>0 and tt>=t_mach:
            if Mref is None: Mref=(Lw,A[0])
            M=mach*Mref[0]*A[0]/Mref[1]
        R=((Lw+M)/Leq)**beta*A[0]**(-theta)
        out[i,:,0]=N; out[i,:,1]=F; out[i,:,2]=e0; out[i,:,3]=births/dt; out[i,:,4]=y; out[i,:,5]=Lj; out[i,:,6]=n[:,13:].sum(1); out[i,:,7]=A; aux[i]=(R,Lw,M)
        n=nn; A=A*np.exp(np.clip(delta*(s*(R-1)+kap*R*np.maximum(m,0)*np.log(np.maximum(A[0]/A,1.0)))*dt,-50,50)); 
        if A[0]>1e30: out[i+1:]=np.nan; aux[i+1:]=np.nan; break
    return ts,out,aux
# ---------------- data ----------------
R_=pd.read_csv(W_+'groups.csv'); pop=pd.read_csv(U+'/80cc69c6-population.csv'); W=pop[pop.Entity=='World'].set_index('Year').Population/1e9
e0d=pd.read_csv(U+'/7c8d2eca-life-expectancy.csv'); EW=e0d[e0d.Entity=='World'].set_index('Year')['Life expectancy']
tfd=pd.read_csv(U+'/abab83cc-children-born-per-woman.csv'); TW=tfd[tfd.Entity=='World'].set_index('Year').iloc[:,-1]
GW=pd.read_csv(U+'/e765659f-global-average-gdp-per-capita-over-the-long-run.csv').set_index('Year')['GDP per capita']/1100.0     # living standard, subsistence = 1
GG=pd.read_csv(W_+'group_gdp.csv').set_index('Year')/1100.0
tN=np.array(list(range(0,1700,100))+list(range(1700,1950,10))+list(range(1950,2021,5))+[2023])
tr=np.array(list(range(1950,2021,5))+[2023]); tEw=np.array([1770,1800,1820,1850,1870,1900,1913])
tG=np.array([1,1000,1500,1600,1700,1820,1850,1870,1900,1920,1940,1950,1960,1970,1980,1990,1995,2000,2005,2010,2015,2020,2025]); sigG=np.where(tG<=1820,0.20,np.where(tG<1950,0.15,0.08))
tGg=np.array([1990,1995,2000,2005,2010,2015,2020,2023])
sm=lambda S,y: S.loc[max(y-2,1950):min(y+2,2023)].mean()
D={}
for j,gname in enumerate('ABC'):
    x=R_[R_.g==gname].set_index('Year'); D[j]=dict(N=x.Pop[tN].values,am=np.log(x.Pop[tr].values[1:]/x.Pop[tr].values[:-1])/np.diff(tr),TFR=np.array([sm(x.TFR,y) for y in tr]),e0=np.array([sm(x.e0,y) for y in tr]),gdp=GG[gname][tGg].values)
sigN=np.where(tN<1500,0.30,np.where(tN<1950,0.08,0.02)); sigW=np.where(tN<1500,0.15,0.05); pre=tN<1950
def pieces(th):
    ts,o,aux=run(th); lN=np.log(np.maximum(o[:,:,0],1e-300)); r={}
    for j in range(J):
        a=np.interp(tr,ts,lN[:,j])
        r[j]=dict(N=np.interp(tN,ts,lN[:,j])-np.log(D[j]['N']),rate=np.diff(a)/np.diff(tr)-D[j]['am'],TFR=np.interp(tr,ts,o[:,j,1])/D[j]['TFR']-1,e0=np.interp(tr,ts,o[:,j,2])/D[j]['e0']-1,gdp=np.interp(tGg,ts,np.log(o[:,j,4]))-np.log(D[j]['gdp']))
    Nw=o[:,:,0].sum(1); ew=(o[:,:,0]*o[:,:,2]).sum(1)/Nw; yw=(o[:,:,0]*o[:,:,4]).sum(1)/Nw
    r['w']=dict(N=np.interp(tN[pre],ts,np.log(Nw))-np.log(W[tN[pre]].values),e0=np.interp(tEw,ts,ew)/EW[tEw].values-1,gdp=np.interp(tG,ts,np.log(yw))-np.log(GW[tG].values))
    return ts,o,r
NRES=3*(len(tN)+3*len(tr)-1+len(tGg))+pre.sum()+len(tEw)+len(tG)
def resid(th):
    try: ts,o,r=pieces(th)
    except Exception: return np.full(NRES,30.0)
    v=np.concatenate([np.concatenate([r[j]['N']/sigN,r[j]['rate']/0.0015,r[j]['TFR']/0.05,r[j]['e0']/0.04,r[j]['gdp']/0.12]) for j in range(J)]+[r['w']['N']/sigW[pre],r['w']['e0']/0.04,r['w']['gdp']/sigG])
    v[~np.isfinite(v)]=30.0; return np.clip(v,-30,30)
#            g     beta theta delta  a    yM    om   qF    b   Finf F0A F0B F0C  sB   sC   kap  N0A   N0B   N0C
LO=np.array([0.03,0.2, 0.0, 0.0,  0.1, 0.2, 0.0, 0.2, 0.5, 0.8, 3.5,4.5,5.0, 0.2, 0.1, 0.0, 0.005,0.03,0.003])
HI=np.array([0.20, 3.0, 2.5, 0.15, 5.0, 60., 1.0, 30., 8.0, 2.4, 7.5,8.0,8.5, 1.5, 1.5, 3.0, 0.1, 0.3, 0.1])
XS=np.array([0.01,0.5, 0.3, 0.01, 0.5, 3.0, 0.3, 2.0, 1.0, 0.5, 2.0,2.0,2.0, 0.3, 0.3, 0.3, 0.02,0.1, 0.02])
def summary(th):
    ts,o,r=pieces(th); f=lambda x: float(np.sqrt(np.mean(np.asarray(x)**2)))
    s={('grp '+'ABC'[j]): dict(lnN_pre1500=round(f(r[j]['N'][tN<1500]),3),lnN_1500_1949=round(f(r[j]['N'][(tN>=1500)&pre]),3),lnN_1950on=round(f(r[j]['N'][~pre]),3),rate_pct=round(100*f(r[j]['rate']),3),TFR=round(f(r[j]['TFR']),3),e0=round(f(r[j]['e0']),3),gdp=round(f(r[j]['gdp']),3)) for j in range(J)}
    Nw=o[:,:,0].sum(1); lw=np.interp(tr,ts,np.log(Nw)); amw=np.log(W[tr].values[1:]/W[tr].values[:-1])/np.diff(tr); Fw=o[:,:,3].sum(1)/(o[:,:,3]/o[:,:,1]).sum(1)
    s['world']=dict(lnN_pre1500=round(f(r['w']['N'][tN[pre]<1500]),3),lnN_1500_1949=round(f(r['w']['N'][tN[pre]>=1500]),3),lnN_1950on=round(f(np.interp(tN[~pre],ts,np.log(Nw))-np.log(W[tN[~pre]].values)),3),
        rate_rel=round(f((np.diff(lw)/np.diff(tr)-amw)/amw),3),TFR=round(f(np.interp(tr,ts,Fw)/np.array([sm(TW,y) for y in tr])-1),3),e0=round(f(np.interp(tr,ts,(o[:,:,0]*o[:,:,2]).sum(1)/Nw)/np.array([sm(EW,y) for y in tr])-1),3),gdp_pre1950=round(f(r['w']['gdp'][tG<1950]),3),gdp_1950on=round(f(r['w']['gdp'][tG>=1950]),3))
    return s
if __name__=="__main__":
    import time
    th=np.array([float(sys.argv[2]) if len(sys.argv)>2 else 0.125,1.0,0.7,0.02,1.0,4.5,0.3,3.0,2.0,1.5,4.6,5.8,7.0,0.8,0.6,0.5,0.03,0.17,0.03]); t0=time.time(); r=resid(th); print("eval %.1f ms, n=%d (%d), chi2=%.0f, Frep=%.3f e0lim=%.1f"%(1e3*(time.time()-t0),len(r),NRES,r@r,FREP,E0LIM))
    ts,o,aux=run(th); k=np.isin(ts,[-300,0,1000,1500,1800,1900,1950,2000,2025]); np.set_printoptions(linewidth=220,suppress=True)
    print("N\n",np.c_[ts[k],o[k,:,0].round(3)],"\ny\n",o[k,:,4].round(2),"\ne0\n",o[k,:,2].round(1),"\nF\n",o[k,:,1].round(2),"\nR,Lw\n",aux[k,:2].round(4))
