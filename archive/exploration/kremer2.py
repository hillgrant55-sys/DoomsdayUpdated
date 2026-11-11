import numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import kremer as K
from kremer import *

# ---- variant: two-parameter mortality response m = z^c/(1+z^c), z=(y-1)/yM ----
def run2(g,yM,c,yF,b,Finf,N0,t_end=2025,dt=5):
    L=table(0)[2].reshape(G,5).mean(1); n=N0*L/L.sum()
    m0=min(g*N0*TG/DLS,0.5); y=1+yM*(m0/(1-m0))**(1/c); T=y*N0
    ts=np.arange(0,t_end+1,dt); out=np.empty((len(ts),7))
    for i,tt in enumerate(ts):
        N=n.sum(); y=T/N; z=(max(y-1,0)/yM)**c; m=z/(1+z)
        F=Finf+(F0-Finf)/(1+(max(y-1,0)/yF)**b)
        surv,sb,Lmid=table(m); births=0.5*F*np.dot(phi,n)
        nn=np.empty(G); nn[0]=births*sb; nn[1:]=n[:-1]*surv[:-1]
        out[i]=(N,births/N/dt,(N+births-nn.sum())/N/dt,F,Lmid.sum(),y,m); n=nn; T*=np.exp(g*N*dt)
    return ts,out
def resid2(th,mode=1,fixF=None):
    th=list(th)
    if fixF is not None: th=th[:5]+[fixF]+th[5:]
    ts,o=run2(*th); N=o[:,0]
    if not np.all(np.isfinite(N)) or N.min()<=0: return np.full(26+14+19,10.0)
    a=np.log(N[ix[u]][1:]/N[ix[u]][:-1])/5
    return np.concatenate([np.log(N[ix])-np.log(Nobs),0.5*(a-am)/am,0.5*(np.interp(tT,ts,o[:,3])-TFR)/TFR,(np.interp(tE,ts,o[:,4])-E0)/E0])
lo2=[0.002,0.01,0.3,0.02,0.5,0.5,0.03]; hi2=[0.02,20,6,60,8,3.0,0.3]; xs2=[0.005,0.3,1,0.3,2,2,0.1]
st2=([0.0057,0.3,1,0.24,1.6,1.9,0.09],[0.0057,0.6,0.6,0.5,2,1.8,0.09],[0.0057,0.15,1.5,0.3,3,2.0,0.09],[0.0057,1.0,0.8,1.0,1.5,1.7,0.09])
def fit2(fixF=None):
    best=None
    for x0 in st2:
        x0=list(x0); l,h,s=list(lo2),list(hi2),list(xs2)
        if fixF is not None:
            for v in (x0,l,h,s): v.pop(5)
        try: r=least_squares(resid2,x0,bounds=(l,h),args=(1,fixF),x_scale=s)
        except Exception: continue
        if best is None or r.cost<best.cost: best=r
    return best
def report(name,ts,o,r):
    N=o[:,0]; ip=np.argmax(N); f=r.fun
    print(name,"| rms lnN %.3f rate %.3f TFR %.3f e0 %.3f"%(np.sqrt(np.mean(f[:26]**2)),np.sqrt(np.mean((f[26:40]/.5)**2)),np.sqrt(np.mean((f[40:49]/.5)**2)),np.sqrt(np.mean(f[49:]**2))))
    print("   peak %.2f Bn in %d; N(2050)=%.2f N(2100)=%.2f N(2200)=%.2f"%(N[ip],ts[ip],N[ts==2050][0],N[ts==2100][0],N[ts==2200][0]))
    print("   TFR",np.round(np.interp(tT,ts,o[:,3]),2)); print("   e0 ",np.round(np.interp(tE,ts,o[:,4]),1))
    print("   CBR",np.round(1e3*np.interp(per+2.5,ts,o[:,1]),1)); print("   CDR",np.round(1e3*np.interp(per+2.5,ts,o[:,2]),1))
    a=np.log(N[ix[u]][1:]/N[ix[u]][:-1])/5; print("   rate model",np.round(100*a,2)); print("   rate obs  ",np.round(100*am,2))

r1=K.fit(1); ts,o1=run(*r1.x,t_end=2300); f=np.concatenate([r1.fun]); report("BASE  "+str(np.round(r1.x,4)),ts,o1,r1)
r2=fit2(); ts,o2=run2(*r2.x,t_end=2300); report("VAR   "+str(np.round(r2.x,4)),ts,o2,r2)
k=len(r2.fun)
try: print("   VAR err",np.round(np.sqrt(np.diag(np.linalg.inv(r2.jac.T@r2.jac)*2*r2.cost/(k-7))),4))
except Exception as e: print(e)
usevar = r2.cost < 0.9*r1.cost
print("use variant:",usevar, r1.cost, r2.cost)
runX = run2 if usevar else run; o=o2 if usevar else o1
prof={}
for Ff in (1.5,1.7,2.1):
    rp = fit2(Ff) if usevar else K.fit(1,Ff)
    th=list(rp.x); pos=5 if usevar else 4; th=th[:pos]+[Ff]+th[pos:]
    tsp,op=runX(*th,t_end=2300); Np=op[:,0]; ip=np.argmax(Np); prof[Ff]=Np
    print("  Finf=%.1f: cost %.4f (best %.4f) peak %.2f in %d, N(2100)=%.2f, N(2200)=%.2f"%(Ff,rp.cost,min(r1.cost,r2.cost) if usevar else r1.cost,Np[ip],tsp[ip],Np[tsp==2100][0],Np[tsp==2200][0]))
np.savez('/home/claude/model_out.npz',ts=ts,o=o,p15=prof[1.5],p17=prof[1.7],p21=prof[2.1])

# ---------------- figure ----------------
ink='#1f1f1e'; mut='#6b6a64'; grid='#e4e3dd'; c1='#2a78d6'; c2='#eb6834'
plt.rcParams.update({'font.size':10,'axes.edgecolor':mut,'axes.labelcolor':ink,'xtick.color':mut,'ytick.color':mut,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(2,2,figsize=(11.5,9.6),dpi=170); fig.patch.set_facecolor('white')
def sty(a,title): a.grid(True,color=grid,lw=0.8); a.set_axisbelow(True); a.set_title(title,loc='left',fontsize=11,color=ink)
T0d=2026.87; N=o[:,0]; w=ts<=2025
a=axs[0,0]; tl=np.linspace(0,2026.4,3000)
a.plot(T0d-tl,179/(T0d-tl)**0.99,ls=(0,(5,4)),color=mut,lw=1.5,label='Eq. 11 (1960 fit)')
a.plot(T0d-ts[w],N[w],color=c1,lw=2,label='Two-variable cohort model')
a.plot(T0d-np.maximum(t,1),Nobs,'o',mfc='white',mec=ink,mew=1.3,ms=5.5,label='World population',zorder=5)
a.set_xscale('log'); a.set_yscale('log'); a.set_xlim(2600,1.2); a.set_ylim(0.08,30)
a.set_yticks([0.1,0.3,1,3,10]); a.set_yticklabels(['0.1','0.3','1','3','10']); a.set_xticks([2000,200,20,2]); a.set_xticklabels(['2000','200','20','2'])
a.set_xlabel('Dooms-time τ = 2026.87 − t  (years)'); a.set_ylabel('N (billions)'); a.legend(frameon=False,loc='lower right',fontsize=9); sty(a,"Population on the paper's axes")
a=axs[0,1]; rate=100*np.log(N[1:]/N[:-1])/5; Ng=np.sqrt(N[1:]*N[:-1]); ww=(ts[1:]<=2060)&(ts[1:]>=50)
nn=np.linspace(0.3,11,50); a.plot(nn,100*nn/179,ls=(0,(5,4)),color=mut,lw=1.5,label='Eq. 3: α = α₀N')
a.plot(Ng[ww],rate[ww],color=c1,lw=2,label='Model (to 2060)')
a.plot(Nmid,100*am,'o',mfc='white',mec=ink,mew=1.3,ms=5.5,label='Observed, 1950–2025',zorder=5)
hm=np.array([(0.58,np.log(0.70/0.47)),(0.79,np.log(0.9/0.7)*2),(1.04,np.log(1.2/0.9)*2),(1.39,np.log(1.6/1.2)*2),(1.73,np.log(1.86/1.6)*5),(1.96,np.log(2.07/1.86)*10),(2.18,np.log(2.3/2.07)*10),(2.39,np.log(2.49/2.3)*10)])
a.plot(hm[:,0],hm[:,1],'o',mfc='white',mec=mut,mew=1.1,ms=4.5,label='Observed, 1650–1950',zorder=4)
a.set_xlim(0,11); a.set_ylim(0,3); a.set_xlabel('N (billions)'); a.set_ylabel('Productivity α  (% per year)'); a.legend(frameon=False,loc='upper right',fontsize=9); sty(a,'Productivity versus population')
a=axs[1,0]; w2=(ts>=1800)&(ts<=2150)
a.plot(ts[w2]+2.5,1e3*o[w2,1],color=c1,lw=2,label='Model fertility γ'); a.plot(ts[w2]+2.5,1e3*o[w2,2],color=c2,lw=2,label='Model mortality θ')
a.plot(per,CBR,'o',mfc='white',mec=ink,mew=1.3,ms=5.5,label='Observed births (not fitted)',zorder=5); a.plot(per,CDR,'s',mfc=ink,mec=ink,ms=4.5,label='Observed deaths (not fitted)',zorder=5)
a.set_xlim(1800,2150); a.set_ylim(0,45); a.set_xlabel('Year'); a.set_ylabel('Rate per 1,000 people per year'); a.legend(frameon=False,loc='lower left',fontsize=9); sty(a,'Fertility and mortality, the two terms of α = γ − θ')
a=axs[1,1]; w3=(ts>=1900)&(ts<=2200)
a.fill_between(ts[w3],prof[1.5][w3],prof[2.1][w3],color=c1,alpha=0.15,lw=0,label='Long-run fertility 1.5 to 2.1')
a.plot(ts[w3],N[w3],color=c1,lw=2,label='Model, best fit')
m3=t>=1900; a.plot(t[m3],Nobs[m3],'o',mfc='white',mec=ink,mew=1.3,ms=5.5,label='World population',zorder=5)
a.plot([2050,2084,2100],[9.66,10.29,10.18],'^',mfc='white',mec=ink,mew=1.3,ms=7,label='UN 2024 medium projection',zorder=5)
a.axvline(2026.87,color=mut,lw=1,ls=(0,(2,3))); a.text(2023,11.3,'13 Nov 2026',color=mut,fontsize=9,ha='right')
a.set_xlim(1900,2200); a.set_ylim(0,12); a.set_xlabel('Year'); a.set_ylabel('N (billions)'); a.legend(frameon=False,loc='lower right',fontsize=9); sty(a,'Projection')
fig.tight_layout(); fig.savefig('/home/claude/doomsday_two_variable_model.png',facecolor='white')
