import sys, json, numpy as np, time
seed=int(sys.argv[2]); sys.argv=sys.argv[:2]
exec(open('/home/claude/work/model4.py').read().split('if __name__=="__main__":')[0])
from scipy.optimize import differential_evolution
lo=LO.copy(); hi=HI.copy(); lo[3]=1e-4; lo[15]=1e-3; lo[2]=0.0
logp=[3,5,7,15,16,17,18]
def trf(x):
    th=np.array(x,float); th[logp]=np.exp(th[logp]); return th
def cost(x):
    r=resid(trf(x)); return np.sum(np.log1p(r*r/9))
b=[(np.log(lo[i]),np.log(hi[i])) if i in logp else (lo[i],hi[i]) for i in range(len(lo))]
t0=time.time(); best=[1e99]
def cb(xk,convergence=None):
    c=cost(xk)
    if c<best[0]-1: best[0]=c; print("  t=%.0fs cost %.1f"%(time.time()-t0,c),np.round(trf(xk),4),flush=True)
de=differential_evolution(cost,b,popsize=8,maxiter=int(sys.argv[3]) if len(sys.argv)>3 else 300,tol=1e-8,seed=seed,polish=False,mutation=(0.4,1.0),recombination=0.8,callback=cb)
th=trf(de.x); print("DE done %.0fs cost %.2f"%(time.time()-t0,de.fun),flush=True)
r=least_squares(resid,np.clip(th,LO,HI),bounds=(LO,HI),x_scale=XS); r=least_squares(resid,r.x,bounds=(LO,HI),x_scale=XS)
print("chi2 %.1f n=%d"%(2*r.cost,len(r.fun)),dict(zip(NAMES,np.round(r.x,4))),flush=True); print(json.dumps(summary(r.x)))
json.dump(dict(th=list(r.x),chi2=2*r.cost,n=len(r.fun)),open('/home/claude/work/best4_%d.json'%seed,'w'))
