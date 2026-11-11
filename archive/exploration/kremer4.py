"""Base two-variable cohort model + one exogenous term: extra mortality d (per year, all ages) during 1915-1949."""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from kremer import *
def run4(g,a,yF,b,Finf,N0,d,t_end=2025,dt=5):
    L=table(0)[2].reshape(G,5).mean(1); n=N0*L/L.sum(); y=1+g*N0*TG/(a*DLS); T=y*N0
    ts=np.arange(0,t_end+1,dt); out=np.empty((len(ts),7))
    for i,tt in enumerate(ts):
        N=n.sum(); y=max(T/N,1e-6); m=min(max(1-y**(-a),-0.5),1.0)
        F=Finf+(F0-Finf)/(1+(max(y-1,0)/yF)**b)
        surv,sb,Lmid=table(m); x=np.exp(-d*dt) if 1915<=tt<1950 else 1.0
        births=0.5*F*np.dot(phi,n); nn=np.empty(G); nn[0]=births*sb*x; nn[1:]=n[:-1]*surv[:-1]*x
        out[i]=(N,births/N/dt,(N+births-nn.sum())/N/dt,F,Lmid.sum(),y,m); n=nn; T*=np.exp(g*N*dt)
    return ts,out
def resid4(th,fix=None):
    th=list(th)
    if fix is not None: th=th[:4]+[fix]+th[4:]
    ts,o=run4(*th); N=o[:,0]
    if not np.all(np.isfinite(o)) or N.min()<=0: return np.full(59,10.0)
    a=np.log(N[ix[u]][1:]/N[ix[u]][:-1])/5
    return np.concatenate([np.log(N[ix])-np.log(Nobs),0.5*(a-am)/am,0.5*(np.interp(tT,ts,o[:,3])-TFR)/TFR,(np.interp(tE,ts,o[:,4])-E0)/E0])
lo4=[0.002,0.05,0.02,0.5,0.5,0.03,0.0]; hi4=[0.02,8,60,8,3.0,0.3,0.02]; xs4=[0.005,1,0.3,2,2,0.1,0.003]
st4=([0.0057,2.5,0.24,1.6,1.87,0.088,0.003],[0.0057,1.5,0.5,2,1.9,0.088,0.005],[0.0057,4,0.15,2.5,1.8,0.088,0.002])
def fit4(fix=None):
    best=None
    for x0 in st4:
        x0=list(x0); l,h,s=list(lo4),list(hi4),list(xs4)
        if fix is not None:
            for v in (x0,l,h,s): v.pop(4)
        r=least_squares(resid4,x0,bounds=(l,h),args=(fix,),x_scale=s)
        if best is None or r.cost<best.cost: best=r
    return best
r=fit4(); th=r.x; ts,o=run4(*th,t_end=2300); N=o[:,0]; f=r.fun; ip=np.argmax(N)
print("g=%.5f (K=%.0f) a=%.2f yF=%.3f b=%.2f Finf=%.2f N0=%.3f d=%.4f"%(th[0],1/th[0],*th[1:]))
print("err",np.round(np.sqrt(np.diag(np.linalg.inv(r.jac.T@r.jac)*2*r.cost/(len(f)-7))),4))
print("cost %.4f | rms lnN %.3f rate %.3f TFR %.3f e0 %.3f"%(r.cost,np.sqrt(np.mean(f[:26]**2)),np.sqrt(np.mean((f[26:40]/.5)**2)),np.sqrt(np.mean((f[40:49]/.5)**2)),np.sqrt(np.mean(f[49:]**2))))
print("peak %.2f Bn in %d; N(2050)=%.2f N(2100)=%.2f N(2200)=%.2f"%(N[ip],ts[ip],N[ts==2050][0],N[ts==2100][0],N[ts==2200][0]))
print("TFR",np.round(np.interp(tT,ts,o[:,3]),2),"\n   ",TFR); print("e0 ",np.round(np.interp(tE,ts,o[:,4]),1),"\n   ",E0)
cb=1e3*np.interp(per+2.5,ts,o[:,1]); cd=1e3*np.interp(per+2.5,ts,o[:,2])
print("CBR",np.round(cb,1),"\n   ",CBR); print("CDR",np.round(cd,1),"\n   ",CDR); print("out-of-sample rms: CBR %.3f CDR %.3f"%(np.sqrt(np.mean((cb/CBR-1)**2)),np.sqrt(np.mean((cd/CDR-1)**2))))
a_=np.log(N[ix[u]][1:]/N[ix[u]][:-1])/5; print("rate",np.round(100*a_,2),"\n    ",np.round(100*am,2))
# deficit caused by the shock: rerun with d=0
th0=list(th); th0[6]=0; N0_=run4(*th0,t_end=2300)[1][:,0]; print("1950 deficit vs no-shock run: %.1f%%; 2025: %.1f%%"%(100*(1-N[ts==1950][0]/N0_[ts==1950][0]),100*(1-N[ts==2025][0]/N0_[ts==2025][0])))
prof={}
for Ff in (1.5,1.7,2.1):
    rp=fit4(Ff); t2=list(rp.x); t2=t2[:4]+[Ff]+t2[4:]; tsp,op=run4(*t2,t_end=2300); Np=op[:,0]; ip=np.argmax(Np); prof[Ff]=Np
    print("  Finf=%.1f: cost %.4f peak %.2f in %d, N(2050)=%.2f N(2100)=%.2f N(2200)=%.2f"%(Ff,rp.cost,Np[ip],tsp[ip],Np[tsp==2050][0],Np[tsp==2100][0],Np[tsp==2200][0]))
exec(open('/home/claude/kremer2.py').read().split('# ---------------- figure ----------------')[1])
