import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import least_squares, brentq
from scipy.integrate import solve_ivp
exec(open('/home/claude/fit.py').read().split('# 0. original')[0])
def NA(tt, K, M, ts):
    out=[]
    for x in np.atleast_1d(tt):
        f=lambda n: 1/n - np.log(n/(M-n))/M - (ts-x)/K
        out.append(brentq(f,1e-9,M*(1-1e-12)))
    return np.array(out)
def NB(tt,K,tc,T1): return (K/tc)*(np.pi/2-np.arctan((T1-tt)/tc))
pA=np.load('/home/claude/pars.npy'); KA,MA,tsA,KB,tcB,T1B=pA

# observed per-capita rates from UN-era points (5-yr log differences)
u = t>=1950
tm=(t[u][1:]+t[u][:-1])/2; Nm=np.sqrt(N[u][1:]*N[u][:-1]); am=100*np.log(N[u][1:]/N[u][:-1])/5
for a,b,c in zip(tm,Nm,am): print("%.1f  N=%.2f  a=%.2f%%"%(a,b,c))
# logistic (Eq. 2) line through the post-1990 rates
s=tm>=1990; sl,ic=np.polyfit(Nm[s],am[s],1); print("post-1990 linear a(N): slope %.3f %%/Bn, zero at N=%.2f Bn"%(sl,-ic/sl))

# D. saturating coalition term x logistic cap: a = (N/K)(1-N/M)/(1+N/Ns)
def rhsD(n,K,M,Ns): return n*n/K*(1-np.clip(n/M,0,None)**Ns)
def ND(tt,K,M,Ns,N0):
    return solve_ivp(lambda x,n: rhsD(n,K,M,Ns),[1,2110],[N0],t_eval=tt,rtol=1e-9,atol=1e-12,method='LSODA').y[0]
def resD(p):
    K,M,Ns,N0=p; n=ND(t,*p)
    r1=np.log(n)-np.log(N)
    r2=(100*rhsD(Nm,K,M,Ns)/Nm-am)/am          # relative error in growth rate
    return np.concatenate([r1,0.5*r2])
rD=least_squares(resD,[170,10.5,1.5,0.1],bounds=([30,8.3,0.2,0.03],[400,40,12,0.3]))
K,M,Ns,N0=rD.x; nfit=len(t)
print("D: K=%.1f M=%.2f Ns=%.2f N0=%.3f  rms lnN=%.3f  rms rate rel=%.3f  nu-check %.2f"%(K,M,Ns,N0,rms(rD.fun[:nfit]),rms(rD.fun[nfit:]/0.5),100*Ns/K))
J=rD.jac; cov=np.linalg.inv(J.T@J)*np.sum(rD.fun**2)/(len(rD.fun)-4); print("  D errors",np.sqrt(np.diag(cov)))
tt=np.linspace(1,2100,8400); nd=ND(tt,*rD.x); gd=np.gradient(nd,tt)
w=tt>1900; i=np.argmax((gd/nd)[w])
print("D: peak per-capita %.2f%% in %.0f; peak increment %.0f M/yr in %.0f; 2025 rate %.2f%%; N(2050)=%.2f N(2100)=%.2f"%(100*(gd/nd)[w][i],tt[w][i],1e3*gd.max(),tt[np.argmax(gd)],100*np.interp(2025,tt,gd/nd),np.interp(2050,tt,nd),nd[-1]))
# same joint-objective refit for A and B so the comparison is fair
def resA(p):
    K,M,ts=p; return np.concatenate([np.log(NA(t,*p))-np.log(N), 0.5*((100*Nm/K*(1-Nm/M))-am)/am])
rA2=least_squares(resA,[170,11,2030],bounds=([50,8.3,1990],[400,60,2200]))
print("A joint: K=%.1f M=%.2f ts=%.1f rms lnN=%.3f rms rate=%.3f"%(*rA2.x,rms(rA2.fun[:nfit]),rms(rA2.fun[nfit:]/0.5)))
def aB(n,K,tc): x=n*tc/K; return (K/tc**2)*np.sin(x)**2/n
def resB(p):
    K,tc,T1=p; return np.concatenate([np.log(NB(t,*p))-np.log(N), 0.5*(100*aB(Nm,K,tc)-am)/am])
rB2=least_squares(resB,[186,41,2010],bounds=([50,5,1950],[400,200,2100]))
print("B joint: K=%.1f tc=%.1f T1=%.1f Ninf=%.2f rms lnN=%.3f rms rate=%.3f"%(*rB2.x,np.pi*rB2.x[0]/rB2.x[1],rms(rB2.fun[:nfit]),rms(rB2.fun[nfit:]/0.5)))

# ---------- figure ----------
ink='#1f1f1e'; mut='#6b6a64'; grid='#e4e3dd'; cA='#2a78d6'; cB='#eb6834'; cD='#1baf7a'
plt.rcParams.update({'font.size':10,'axes.edgecolor':mut,'axes.labelcolor':ink,'xtick.color':mut,'ytick.color':mut,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(1,2,figsize=(11.5,5.2),dpi=170); fig.patch.set_facecolor('white')
T0d=2026.87; tl=np.unique(np.concatenate([np.linspace(1,1900,400),np.linspace(1900,2026.4,1200)])); tau=T0d-tl
a0=ax[0]
a0.plot(tau,179/tau**0.99,ls=(0,(5,4)),color=mut,lw=1.5,label='Eq. 11 (1960 fit)')
a0.plot(tau,NA(tl,*rA2.x),color=cA,lw=2,label='A: logistic cap')
a0.plot(tau,NB(tl,*rB2.x),color=cB,lw=2,label='B: finite-time cutoff')
a0.plot(tau,ND(tl,*rD.x),color=cD,lw=2,label='C: generalized cap')
a0.plot(T0d-t,N,'o',mfc='white',mec=ink,mew=1.3,ms=5.5,label='World population',zorder=5)
a0.set_xscale('log'); a0.set_yscale('log'); a0.set_xlim(2600,1.2); a0.set_ylim(0.08,30)
a0.set_xlabel('Dooms-time τ = 2026.87 − t  (years)'); a0.set_ylabel('N (billions)')
a0.set_yticks([0.1,0.3,1,3,10]); a0.set_yticklabels(['0.1','0.3','1','3','10'])
a0.set_xticks([2000,200,20,2]); a0.set_xticklabels(['2000','200','20','2'])
a0.grid(True,color=grid,lw=0.8); a0.set_axisbelow(True); a0.legend(frameon=False,loc='lower right',fontsize=9)
a0.set_title('Population on the paper\'s axes',loc='left',fontsize=11,color=ink)
a1=ax[1]; nn=np.linspace(0.3,13,600)
a1.plot(nn,100*nn/179,ls=(0,(5,4)),color=mut,lw=1.5,label='Eq. 3: α = α₀N')
a1.plot(nn,np.clip(100*nn/rA2.x[0]*(1-nn/rA2.x[1]),0,None),color=cA,lw=2,label='A')
a1.plot(nn,100*aB(nn,rB2.x[0],rB2.x[1]),color=cB,lw=2,label='B')
a1.plot(nn,np.clip(100*rhsD(nn,K,M,Ns)/nn,0,None),color=cD,lw=2,label='C')
a1.plot(Nm,am,'o',mfc='white',mec=ink,mew=1.3,ms=5.5,label='Observed, 1950–2025',zorder=5)
hm=np.array([(1700,0.58,np.log(0.70/0.47)),(1775,0.79,np.log(0.9/0.7)*2),(1825,1.04,np.log(1.2/0.9)*2),(1875,1.39,np.log(1.6/1.2)*2),(1910,1.73,np.log(1.86/1.6)*5),(1925,1.96,np.log(2.07/1.86)*10),(1935,2.18,np.log(2.3/2.07)*10),(1945,2.39,np.log(2.49/2.3)*10)])
a1.plot(hm[:,1],hm[:,2],'o',mfc='white',mec=mut,mew=1.1,ms=4.5,label='Observed, 1650–1950',zorder=4)
a1.set_xlim(0,13); a1.set_ylim(0,3); a1.set_xlabel('N (billions)'); a1.set_ylabel('Productivity α = (1/N) dN/dt  (% per year)')
a1.grid(True,color=grid,lw=0.8); a1.set_axisbelow(True); a1.legend(frameon=False,loc='upper right',fontsize=9)
a1.set_title('Productivity versus population',loc='left',fontsize=11,color=ink)
fig.tight_layout(); fig.savefig('/home/claude/doomsday_modified_fits.png',facecolor='white')
