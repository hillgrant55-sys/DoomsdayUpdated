import sys, json, numpy as np, time
seed=int(sys.argv[2]); sys.argv=sys.argv[:2]
exec(open('/home/claude/work/model2.py').read().split('if __name__=="__main__":')[0])
from scipy.optimize import differential_evolution
logp=[0,3,4,11,12,13]
def trf(x):
    th=np.array(x,float); th[logp]=np.exp(th[logp]); return th
def cost(x):
    r=resid(trf(x)); return np.sum(np.log1p(r*r/9))
b=[(np.log(LO[i]),np.log(HI[i])) if i in logp else (LO[i],HI[i]) for i in range(len(LO))]
t0=time.time()
de=differential_evolution(cost,b,popsize=10,maxiter=320,tol=1e-8,seed=seed,polish=False,mutation=(0.4,1.0),recombination=0.8)
th=trf(de.x); print("DE done %.0fs cost %.2f"%(time.time()-t0,de.fun),flush=True)
r=least_squares(resid,th,bounds=(LO,HI),x_scale=XS); r=least_squares(resid,r.x,bounds=(LO,HI),x_scale=XS,loss='linear')
print("chi2 %.1f n=%d"%(2*r.cost,len(r.fun)),dict(zip(NAMES,np.round(r.x,4))),flush=True); print(json.dumps(summary(r.x)))
json.dump(dict(th=list(r.x),chi2=2*r.cost,n=len(r.fun)),open('/home/claude/work/best2_%d.json'%seed,'w'))
