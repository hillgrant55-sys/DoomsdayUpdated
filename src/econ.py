"""Productivity law fitted to world GDP per capita:  dlnA/dt = g L^beta A^-theta - delta
A = y (sig0/sig) (N/N1)^GAM, y = GDPpc/1100, L = workforce (bn, ages 15-64)."""
import sys, numpy as np, pandas as pd
import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RAW=_os.path.join(_ROOT,'data','raw')+'/'; DER=_os.path.join(_ROOT,'data','derived')+'/'
RESDIR=_os.path.join(_ROOT,'results')+'/'; FIG=_os.path.join(_ROOT,'figures')+'/'
MODEL=_os.path.join(_ROOT,'src','model5.py')
from scipy.optimize import least_squares
pop=pd.read_csv(RAW+'population.csv'); Wp=pop[pop.Entity=='World'].set_index('Year').Population/1e9
GWd=pd.read_csv(RAW+'global-average-gdp-per-capita-over-the-long-run.csv').set_index('Year')['GDP per capita']
aw=pd.read_csv(DER+'world_age.csv').set_index('Year'); SIG0=float(aw.work[1950])
yrs=np.arange(1,2026); Ny=np.exp(np.interp(yrs,Wp.index.values.astype(float),np.log(Wp.values))); Ny[yrs>2023]=Wp[2023]*np.exp(0.0085*(yrs[yrs>2023]-2023))
sigy=np.where(yrs<1950,SIG0,np.interp(yrs,aw.index.values.astype(float),aw.work.values)); Ly=sigy*Ny
tG=np.array([1,1000,1500,1600,1700,1820,1850,1870,1900,1920,1940,1950,1960,1970,1980,1990,1995,2000,2005,2010,2015,2020,2025]); sigG=np.where(tG<=1820,0.20,np.where(tG<1950,0.15,0.08))
def Aobs(gam): return (GWd[tG].values/1100.0)*(SIG0/sigy[tG-1])*(Ny[tG-1]/Ny[0])**gam
def integ(p,L=Ly,lnA0=None,n=None):
    g,beta,theta,delta,l0=p; lnA=np.empty(len(L)); x=l0 if lnA0 is None else lnA0
    for i in range(len(L)):
        lnA[i]=x; x+=g*L[i]**beta*np.exp(-theta*x)-delta
        if x>60: lnA[i+1:]=np.inf; break
    return lnA
def fit(gam,fix={}):
    names=['g','beta','theta','delta','lnA1']; lo=np.array([1e-6,0.0,0.0,0.0,-1.0]); hi=np.array([1.0,4.0,3.0,0.2,1.0]); x0s=[[0.01,1.0,0.3,0.001,0.0],[0.03,1.5,1.0,0.003,0.0],[0.005,0.8,0.0,0.0,0.0],[0.05,2.0,1.5,0.01,0.0]]
    idx=[i for i,n in enumerate(names) if n not in fix]; tgt=np.log(Aobs(gam)); best=None
    def res(f):
        p=np.array([fix.get(n,np.nan) for n in names]); p[idx]=f; r=(integ(p)[tG-1]-tgt)/sigG; r[~np.isfinite(r)]=50; return np.clip(r,-50,50)
    for x0 in x0s:
        r=least_squares(res,np.clip(np.array(x0)[idx],lo[idx]+1e-9,hi[idx]-1e-9),bounds=(lo[idx],hi[idx]),x_scale=np.array([0.01,0.5,0.3,0.003,0.1])[idx])
        if best is None or r.cost<best.cost: best=r
    p=np.array([fix.get(n,np.nan) for n in names]); p[idx]=best.x; return p,2*best.cost,best,idx
if __name__=="__main__":
    np.set_printoptions(suppress=True,linewidth=200,precision=4)
    for gam in (1/3,0.0,1.0):
        print("GAM=%.2f  A_obs:"%gam,dict(zip(tG[[0,2,5,8,11,17,22]],np.round(Aobs(gam)[[0,2,5,8,11,17,22]],2))))
        for nm,fx in (("beta only",{'theta':0.0,'delta':0.0}),("+theta",{'delta':0.0}),("+delta",{'theta':0.0}),("all",{})):
            p,chi,r,idx=fit(gam,fx); print("   %-10s chi2 %7.2f  g=%.5f beta=%.3f theta=%.3f delta=%.5f lnA1=%.3f | growth 2025 %.2f%%/yr"%(nm,chi,*p,100*(p[0]*Ly[-1]**p[1]*np.exp(-p[2]*integ(p)[-1])-p[3])))
        if gam==1/3:
            for dl in (0.0005,0.001,0.002,0.004,0.008,0.015,0.03): p,chi,r,idx=fit(gam,{'delta':dl}); print("     delta=%.4f chi2 %.2f beta=%.3f theta=%.3f g=%.4f"%(dl,chi,p[1],p[2],p[0]))
            for thv in (0.0,0.25,0.5,1.0,1.5,2.0,3.0): p,chi,r,idx=fit(gam,{'theta':thv}); print("     theta=%.2f chi2 %.2f beta=%.3f delta=%.5f g=%.4f"%(thv,chi,p[1],p[3],p[0]))
