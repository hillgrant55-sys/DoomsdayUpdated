import sys, json, numpy as np, time
sys.argv=[sys.argv[0],sys.argv[1]]
exec(open('/home/claude/work/model.py').read().split('if __name__=="__main__" and')[0])
from scipy.optimize import differential_evolution, least_squares
import warnings; warnings.filterwarnings('ignore')
t0=time.time(); ts,o=run(*STARTS[0]); print("one run %.1f ms"%(1e3*(time.time()-t0)))
lo=LO.copy(); hi=HI.copy(); lo[0]=5e-4; hi[0]=0.03; hi[2]=5; lo[3]=0.05; hi[3]=30; hi[4]=30; lo[7]=0.05; hi[7]=0.3; hi[8]=0.015
logp=[0,3,4]   # search g,yM,yF in log space
def trf(x):
    th=np.array(x,float); th[logp]=np.exp(th[logp]); return th
def cost(x):
    r=resid(trf(x),{}); return np.sum(np.log1p(r*r/9))
b=[(np.log(lo[i]),np.log(hi[i])) if i in logp else (lo[i],hi[i]) for i in range(9)]
best=None
for seed in (1,2,3):
    de=differential_evolution(cost,b,popsize=14,maxiter=250,tol=1e-7,seed=seed,polish=False,mutation=(0.4,1.0),recombination=0.8)
    th=trf(de.x); r=least_squares(resid,th,bounds=(LO,HI),x_scale=XS,args=({},))
    print(seed,"DE cost %.1f -> chi2 %.1f"%(de.fun,2*r.cost),np.round(r.x,4),{k:round(v,3) for k,v in stats(r.x).items()},"t=%.0fs"%(time.time()-t0),flush=True)
    if best is None or r.cost<best.cost: best=r
dof=len(best.fun)-9; err=np.sqrt(np.diag(np.linalg.pinv(best.jac.T@best.jac)*2*best.cost/dof))
print("BEST",dict(zip(NAMES,np.round(best.x,5)))); print("err ",dict(zip(NAMES,np.round(err,5))))
json.dump(dict(th=list(best.x),err=list(err),chi2=2*best.cost,dof=dof),open('/home/claude/work/best.json','w'))
