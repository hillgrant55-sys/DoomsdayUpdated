import numpy as np
from scipy.optimize import least_squares, brentq
from scipy.integrate import solve_ivp

# World population (billions). Pre-1950: historical estimates of the kind used in the paper;
# 1950 on: UN World Population Prospects (rounded).
data = [(1,0.10),(1000,0.20),(1650,0.47),(1750,0.70),(1800,0.90),(1850,1.20),(1900,1.60),
        (1920,1.86),(1930,2.07),(1940,2.30),(1950,2.49),(1955,2.74),(1960,3.02),(1965,3.33),
        (1970,3.69),(1975,4.07),(1980,4.44),(1985,4.86),(1990,5.33),(1995,5.75),(2000,6.17),
        (2005,6.59),(2010,7.02),(2015,7.47),(2020,7.89),(2025,8.23)]
t = np.array([d[0] for d in data], float); N = np.array([d[1] for d in data], float)
T0 = 2026.87

def rms(r): return np.sqrt(np.mean(r**2))

# 0. original hyperbola, paper's constants
hyp = lambda tt: 179.0/(T0-tt)**0.99
print("vF hyperbola, all data  rms(ln):", rms(np.log(hyp(t))-np.log(N)))
m = t<=1960
print("vF hyperbola, <=1960    rms(ln):", rms(np.log(hyp(t[m]))-np.log(N[m])))

# A. logistic cap: 1/N - (1/M) ln(N/(M-N)) = (ts - t)/K   (k=1)
def NA(tt, K, M, ts):
    out=[]
    for x in np.atleast_1d(tt):
        f=lambda n: 1/n - np.log(n/(M-n))/M - (ts-x)/K
        out.append(brentq(f,1e-9,M*(1-1e-12)))
    return np.array(out)
rA = least_squares(lambda p: np.log(NA(t,*p))-np.log(N), [180,11,2030], bounds=([50,8.3,1990],[400,60,2200]))
print("A logistic cap: K=%.1f M=%.2f ts=%.1f rms=%.3f"%(*rA.x, rms(rA.fun)))

# B. finite-time (Lorentzian) cutoff: N = (K/tc) arccot((T1-t)/tc)
def NB(tt,K,tc,T1): return (K/tc)*(np.pi/2-np.arctan((T1-tt)/tc))
rB = least_squares(lambda p: np.log(NB(t,*p))-np.log(N), [180,40,2000], bounds=([50,5,1950],[400,200,2100]))
K,tc,T1 = rB.x
print("B time cutoff: K=%.1f tc=%.1f T1=%.1f Ninf=%.2f rms=%.3f"%(K,tc,T1,np.pi*K/tc, rms(rB.fun)))
# Jacobian-based 1-sigma
def errs(r):
    J=r.jac; cov=np.linalg.inv(J.T@J)*np.sum(r.fun**2)/(len(r.fun)-len(r.x)); return np.sqrt(np.diag(cov))
print("  B errors", errs(rB)); print("  A errors", errs(rA))
eB=errs(rB)

# C. generalized cap: dN/dt = N^2/K * (1-(N/M)^nu)
def NC(tt,K,M,nu,N0):
    s=solve_ivp(lambda x,n: n*n/K*(1-(n/M)**nu),[1,2030],[N0],t_eval=tt,rtol=1e-9,atol=1e-12,method='LSODA')
    return s.y[0]
rC = least_squares(lambda p: np.log(NC(t,*p))-np.log(N), [180,11,1,0.09], bounds=([50,8.3,0.05,0.05],[400,80,20,0.2]))
print("C theta cap: K=%.1f M=%.2f nu=%.2f N0=%.3f rms=%.3f"%(*rC.x, rms(rC.fun)))

# diagnostics for B: peak growth rates
tt=np.linspace(1900,2100,2001); nb=NB(tt,K,tc,T1); g=np.gradient(nb,tt)
i=np.argmax(g/nb); print("B: peak per-capita %.2f%%/yr in %.0f at N=%.2f; peak increment %.1f M/yr in %.0f; 2025 rate %.2f%%; N(2100)=%.2f"%(100*(g/nb)[i],tt[i],nb[i],1e3*g.max(),tt[np.argmax(g)],100*np.interp(2025,tt,g/nb),nb[-1]))
na=NA(tt,*rA.x); ga=np.gradient(na,tt); i=np.argmax(ga/na)
print("A: peak per-capita %.2f%%/yr in %.0f; peak increment %.1f M/yr in %.0f; 2025 rate %.2f%%; N(2100)=%.2f"%(100*(ga/na)[i],tt[i],1e3*ga.max(),tt[np.argmax(ga)],100*np.interp(2025,tt,ga/na),na[-1]))
np.save('/home/claude/pars.npy', np.array([*rA.x,*rB.x]))
