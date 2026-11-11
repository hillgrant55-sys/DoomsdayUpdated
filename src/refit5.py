import sys, re, json, numpy as np
import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RAW=_os.path.join(_ROOT,'data','raw')+'/'; DER=_os.path.join(_ROOT,'data','derived')+'/'
RESDIR=_os.path.join(_ROOT,'results')+'/'; FIG=_os.path.join(_ROOT,'figures')+'/'
MODEL=_os.path.join(_ROOT,'src','model5.py')
src=open(MODEL).read().split('if __name__=="__main__":')[0]
b=json.load(open(RESDIR+'start_params.json')); th0=np.array(b['th'])
for dmax in (0.03,0.003):
    g={'__name__':'m','__file__':MODEL}; exec(re.sub(r"DMAX=[0-9.]+","DMAX=%g"%dmax,src,count=1),g)
    t=np.clip(th0,g['LO'],g['HI']); best=None
    for k in range(3):
        r=g['least_squares'](g['resid'],t,bounds=(g['LO'],g['HI']),x_scale=g['XS']); t=r.x
    print("dmax=%g chi2 %.1f"%(dmax,2*r.cost),dict(zip(g['NAMES'],np.round(r.x,4)))); print("  ",json.dumps(g['summary'](r.x)))
    json.dump(dict(th=list(r.x),chi2=2*r.cost,n=len(r.fun)),open(RESDIR+'best5_d%g.json'%dmax,'w'))
