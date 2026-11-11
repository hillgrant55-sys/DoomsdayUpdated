"""Doomsday model with (i) age structure (McKendrick-von Foerster, 5-yr cohorts) and
(ii) a second state variable T ("capability" of the coalition), dT/dt = g N T.
y = T/N is the living standard relative to subsistence (y=1: births balance deaths).
  mortality progress  m(y) = 1 - y^-a          hazard mu(a;m) = mu_pre(a)^(1-m) mu_mod(a)^m
  fertility (TFR)     F(y) = Finf + (F0-Finf)/(1+((y-1)/yF)^b),  F0 fixed by NRR=1 at y=1
While N can keep up with T (slow era) y stays just above 1 and dN/dt = g N^2 (paper's Eq. 3, k=1).
Free parameters: g, a, yF, b, Finf, N0."""
import numpy as np, json
from scipy.optimize import least_squares
A=110; ages=np.arange(A)
def siler(a1,b1,a2,a3,b3): return a1*np.exp(-b1*ages)+a2+a3*np.exp(b3*ages)
LP=np.log(siler(0.33,1.0,0.0125,0.0006,0.070)); LM=np.log(siler(0.003,1.0,0.0001,1.0e-5,0.105))
G=22; gmid=5*np.arange(G)+2.5
phi=np.clip(1-np.abs(gmid-28)/14.0,0,None); phi[(gmid<15)|(gmid>50)]=0; phi/=phi.sum()
def table(m):
    mu=np.exp((1-m)*LP+m*LM); cum=np.concatenate([[0],np.cumsum(mu)[:-1]]); Lmid=np.exp(-cum-mu/2)   # l(a+0.5)
    surv=np.zeros(G); surv[:-1]=Lmid[7::5][:G-1]/Lmid[2::5][:G-1]       # group g -> g+1
    sb=Lmid[:5].mean()                                                  # births -> group 0 at end of step
    return surv,sb,Lmid
def e0_of(m): return table(m)[2].sum()
def nrrF(m): L=table(m)[2]; return 0.5*np.dot(phi,L.reshape(G,5).mean(1))
F0=1/nrrF(0.0); TG=28.0; DLS=np.log(nrrF(1.0)/nrrF(0.0))   # d ln(survival to childbearing)/dm, roughly

def run(g,a,yF,b,Finf,N0,t_end=2025,dt=5):
    L=table(0)[2].reshape(G,5).mean(1); n=N0*L/L.sum()
    y=1+g*N0*TG/(a*DLS); T=y*N0
    ts=np.arange(0,t_end+1,dt); out=np.empty((len(ts),7))
    for i,tt in enumerate(ts):
        N=n.sum(); y=max(T/N,1e-6); m=min(max(1-y**(-a),-0.5),1.0)
        F=Finf+(F0-Finf)/(1+(max(y-1,0)/yF)**b)
        surv,sb,Lmid=table(m)
        births=0.5*F*np.dot(phi,n)                 # over the 5-yr step
        nn=np.empty(G); nn[0]=births*sb; nn[1:]=n[:-1]*surv[:-1]
        deaths=N+births-nn.sum()
        out[i]=(N,births/N/dt,deaths/N/dt,F,Lmid.sum(),y,m)
        n=nn; T*=np.exp(g*N*dt)
    return ts,out

data=[(0,0.10),(1000,0.20),(1650,0.47),(1750,0.70),(1800,0.90),(1850,1.20),(1900,1.60),(1920,1.86),(1930,2.07),(1940,2.30),
      (1950,2.49),(1955,2.74),(1960,3.02),(1965,3.33),(1970,3.69),(1975,4.07),(1980,4.44),(1985,4.86),(1990,5.33),(1995,5.75),
      (2000,6.17),(2005,6.59),(2010,7.02),(2015,7.47),(2020,7.89),(2025,8.23)]
t=np.array([d[0] for d in data]); Nobs=np.array([d[1] for d in data]); ix=t//5
u=t>=1950; am=np.log(Nobs[u][1:]/Nobs[u][:-1])/5; Nmid=np.sqrt(Nobs[u][1:]*Nobs[u][:-1]); tmid=(t[u][1:]+t[u][:-1])/2
# independent series (UN WPP / Maddison, approximate, from memory)
per=np.arange(1952.5,2020,5)
CBR=np.array([36.9,35.4,35.2,34.0,31.4,28.5,27.7,27.4,24.2,22.2,20.9,20.3,19.5,18.5])
CDR=np.array([19.1,17.4,16.2,13.0,11.6,10.7,10.1,9.4,9.1,8.8,8.5,8.1,7.7,7.5])
tT=np.array([1950,1963,1970,1980,1990,2000,2010,2020,2023]); TFR=np.array([4.86,5.3,4.83,3.75,3.31,2.73,2.59,2.35,2.25])
tE=np.array([1800,1900,1950,1970,1980,1990,2000,2010,2019,2023]); E0=np.array([29,32,46.5,56.1,60.6,64.0,66.5,70.1,72.8,73.2])
tY=np.array([0,1000,1500,1820,1870,1913,1950,1973,2003,2008]); GDP=np.array([467,453,566,666,870,1524,2111,4083,6516,7614.])

def resid(th,mode=0,fixF=None):
    th=list(th)
    if fixF is not None: th=th[:4]+[fixF]+th[4:]
    ts,o=run(*th); N=o[:,0]
    if not np.all(np.isfinite(N)): return np.full(200,10.0)[:26+14+(19 if mode else 0)]
    r=[np.log(N[ix])-np.log(Nobs)]
    a=np.log(N[ix[u]][1:]/N[ix[u]][:-1])/5; r.append(0.5*(a-am)/am)
    if mode:
        r.append(0.5*(np.interp(tT,ts,o[:,3])-TFR)/TFR); r.append(1.0*(np.interp(tE,ts,o[:,4])-E0)/E0)
    return np.concatenate(r)
lo=[0.002,0.05,0.2,0.5,0.5,0.03]; hi=[0.02,5,60,8,3.0,0.3]; xs=[0.005,1,5,2,2,0.1]
starts=([0.0056,0.6,3,2,1.8,0.09],[0.0056,0.3,8,1.5,2.0,0.09],[0.006,1.5,2,3,1.5,0.1],[0.005,0.15,15,2,1.8,0.1])
def fit(mode,fixF=None):
    best=None
    for x0 in starts:
        x0=list(x0); l,h,s=list(lo),list(hi),list(xs)
        if fixF is not None:
            for v in (x0,l,h,s): v.pop(4)
        try: r=least_squares(resid,x0,bounds=(l,h),args=(mode,fixF),x_scale=s)
        except Exception as e: continue
        if best is None or r.cost<best.cost: best=r
    return best
def full(th):
    th=list(th)
    return th
if __name__=="__main__":
    print("premodern e0=%.1f limit e0=%.1f F0=%.2f"%(e0_of(0),e0_of(1),F0)); res={}
    for name,mode in (("N_only",0),("N_TFR_e0",1)):
        r=fit(mode); k=len(r.fun)
        try: err=np.sqrt(np.diag(np.linalg.inv(r.jac.T@r.jac)*2*r.cost/(k-6)))
        except Exception: err=np.full(6,np.nan)
        print(name,"g=%.5f (K=%.0f) a=%.3f yF=%.2f b=%.2f Finf=%.2f N0=%.3f"%(r.x[0],1/r.x[0],*r.x[1:]),"\n   err",np.round(err,4),
              "| rms lnN %.3f rate %.3f"%(np.sqrt(np.mean(r.fun[:26]**2)),np.sqrt(np.mean((r.fun[26:40]/0.5)**2))))
        ts,o=run(*r.x,t_end=2300); N=o[:,0]; ip=np.argmax(N)
        print("   peak %.2f Bn in %d; N(2050)=%.2f N(2100)=%.2f N(2200)=%.2f"%(N[ip],ts[ip],N[ts==2050][0],N[ts==2100][0],N[ts==2200][0]))
        print("   TFR model",np.round(np.interp(tT,ts,o[:,3]),2),"\n   TFR obs  ",TFR)
        print("   e0 model ",np.round(np.interp(tE,ts,o[:,4]),1),"\n   e0 obs   ",E0)
        print("   CBR model",np.round(1e3*np.interp(per+2.5,ts,o[:,1]),1),"\n   CDR model",np.round(1e3*np.interp(per+2.5,ts,o[:,2]),1))
        print("   y model  ",np.round(np.interp(tY,ts,o[:,5]),2),"\n   GDPpc/450",np.round(GDP/450,2))
        res[name]=list(r.x)
    json.dump(res,open('/home/claude/kremer_pars.json','w'))
