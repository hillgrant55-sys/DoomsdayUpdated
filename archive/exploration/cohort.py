"""Age-structured (McKendrick-von Foerster) version of the Doomsday model.
State: n(a,t), yearly cohorts. Coalition variable m(N) in [0,1] ("mortality progress").
  hazard  mu(a;m) = mu_pre(a)^(1-m) * mu_mod(a)^m
  m(N)    = x^p/(1+x^p), x = N/Nm
  TFR     F(m) = Finf + (F0-Finf)(1-m^q),  F0 fixed by premodern stationarity (NRR=1 at m=0)
Free parameters: Nm, p, q, Finf, N0."""
import numpy as np, json, sys
from scipy.optimize import least_squares

A = 110; ages = np.arange(A)
def siler(a1,b1,a2,a3,b3): return a1*np.exp(-b1*ages)+a2+a3*np.exp(b3*ages)
MU_PRE = siler(0.33,1.0,0.0125,0.0006,0.070)     # tuned below to e0 ~ 25
MU_MOD = siler(0.003,1.0,0.0001,1.0e-5,0.105)    # limiting schedule, e0 ~ 85
LP, LM = np.log(MU_PRE), np.log(MU_MOD)
phi = np.clip(1-np.abs(ages-28)/14.0,0,None); phi[(ages<15)|(ages>49)]=0; phi/=phi.sum()

def lx(mu): return np.concatenate([[1.0],np.exp(-np.cumsum(mu))[:-1]])   # survivors at exact age a
def e0(mu): l=lx(mu); return np.sum(l*(1-0.5*(1-np.exp(-mu))))
def nrr_per_F(mu): return 0.5*np.sum(phi*lx(mu)*np.exp(-mu/2))
F0 = 1.0/nrr_per_F(MU_PRE)

def run(Nm,p,q,Finf,N0,t_end=2025,full=False):
    l0=lx(MU_PRE)*np.exp(-MU_PRE/2); n=N0*l0/l0.sum()
    yrs=np.arange(1,t_end+1); out=np.empty((len(yrs),6))
    for i,y in enumerate(yrs):
        N=n.sum(); x=(N/Nm)**p; m=x/(1+x)
        mu=np.exp((1-m)*LP+m*LM); F=Finf+(F0-Finf)*(1-m**q)
        births=0.5*F*np.dot(phi,n); surv=np.exp(-mu)
        deaths=np.dot(n,1-surv)+births*(1-np.exp(-mu[0]/2))
        out[i]=(N,births/N,deaths/N,F,m,0.0)
        n=np.concatenate([[births*np.exp(-mu[0]/2)],n[:-1]*surv[:-1]])
        if full: out[i,5]=e0(mu)
    return yrs,out

# ---------------- data ----------------
data=[(1,0.10),(1000,0.20),(1650,0.47),(1750,0.70),(1800,0.90),(1850,1.20),(1900,1.60),(1920,1.86),(1930,2.07),(1940,2.30),
      (1950,2.49),(1955,2.74),(1960,3.02),(1965,3.33),(1970,3.69),(1975,4.07),(1980,4.44),(1985,4.86),(1990,5.33),(1995,5.75),
      (2000,6.17),(2005,6.59),(2010,7.02),(2015,7.47),(2020,7.89),(2025,8.23)]
t=np.array([d[0] for d in data]); Nobs=np.array([d[1] for d in data])
u=t>=1950; tm=(t[u][1:]+t[u][:-1])/2; Nmid=np.sqrt(Nobs[u][1:]*Nobs[u][:-1]); am=np.log(Nobs[u][1:]/Nobs[u][:-1])/5
# independent checks (UN WPP, approximate, entered from memory)
per=np.arange(1952.5,2020,5)
CBR=np.array([36.9,35.4,35.2,34.0,31.4,28.5,27.7,27.4,24.2,22.2,20.9,20.3,19.5,18.5])
CDR=np.array([19.1,17.4,16.2,13.0,11.6,10.7,10.1,9.4,9.1,8.8,8.5,8.1,7.7,7.5])
tT=np.array([1950,1963,1970,1980,1990,2000,2010,2020,2023]); TFR=np.array([4.86,5.3,4.83,3.75,3.31,2.73,2.59,2.35,2.25])
tE=np.array([1800,1900,1950,1970,1980,1990,2000,2010,2019,2023]); E0=np.array([29,32,46.5,56.1,60.6,64.0,66.5,70.1,72.8,73.2])

def resid(th,use_checks=False,fixF=None):
    Nm,p,q,Finf,N0 = th if fixF is None else (th[0],th[1],th[2],fixF,th[3])
    yrs,o=run(Nm,p,q,Finf,N0,full=use_checks); N=o[:,0]
    r=[np.log(N[t-1])-np.log(Nobs)]
    a=np.array([np.log(N[int(b)-1]/N[int(a_)-1])/5 for a_,b in zip(t[u][:-1],t[u][1:])])
    r.append(0.5*(a-am)/am)
    if use_checks:
        r.append(0.5*(o[tT-1,3]-TFR)/TFR); r.append(1.0*(o[tE-1,5]-E0)/E0)
    return np.concatenate(r)

if __name__=="__main__":
    print("premodern e0=%.1f  limit e0=%.1f  F0=%.2f"%(e0(MU_PRE),e0(MU_MOD),F0))
    lo=[0.5,0.5,0.5,0.8,0.03]; hi=[30,5,12,3.0,0.3]; res={}
    for name,chk in (("N_only",False),("N_TFR_e0",True)):
        best=None
        for x0 in ([3.5,1.5,3,1.8,0.09],[6,1.0,2,2.0,0.09],[3,2.0,5,1.5,0.1]):
            r=least_squares(resid,x0,bounds=(lo,hi),args=(chk,),x_scale=[3,1,3,2,0.1])
            if best is None or r.cost<best.cost: best=r
        r=best; nN=len(t); k=len(r.fun)
        try:
            cov=np.linalg.inv(r.jac.T@r.jac)*2*r.cost/(k-5); err=np.sqrt(np.diag(cov))
        except Exception: err=np.full(5,np.nan)
        print(name,"Nm=%.2f p=%.2f q=%.2f Finf=%.2f N0=%.3f"%tuple(r.x),"| err",np.round(err,2),
              "| rms lnN %.3f  rms rate %.3f"%(np.sqrt(np.mean(r.fun[:nN]**2)),np.sqrt(np.mean((r.fun[nN:nN+15]/0.5)**2))))
        res[name]=list(r.x)
    json.dump(res,open('/home/claude/cohort_pars.json','w'))
