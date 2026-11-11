import sys, json, numpy as np
seed=int(sys.argv[2]); sys.argv=sys.argv[:2]
exec(open('/home/claude/work/model4.py').read().split('if __name__=="__main__":')[0])
th0=np.array(json.load(open('/home/claude/work/best4_1.json'))['th']); rng=np.random.default_rng(seed); best=None
for k in range(9):
    s=th0 if (k==0 and seed==1) else np.clip((best.x if (best is not None and k%2==0) else th0)*np.exp(0.25*rng.standard_normal(len(th0))),LO*1.0001+1e-9,HI*0.9999)
    r=least_squares(resid,s,bounds=(LO,HI),x_scale=XS,max_nfev=120)
    if best is None or r.cost<best.cost: best=r
    print(k,"chi2 %.1f (best %.1f)"%(2*r.cost,2*best.cost),flush=True)
json.dump(dict(th=list(best.x),chi2=2*best.cost,n=len(best.fun)),open('/home/claude/work/best4_%d.json'%(10+seed),'w'))
print(dict(zip(NAMES,[float(round(v,5)) for v in best.x]))); print(json.dumps(summary(best.x)))
