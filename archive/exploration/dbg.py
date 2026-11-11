import sys, json, numpy as np
exec(open('/home/claude/work/model.py').read().split('if __name__=="__main__" and')[0])
import warnings; warnings.filterwarnings('ignore')
def show(th):
    ts,o=run(*th); k=((ts%250==0)&(ts<1750))|((ts>=1750)&(ts%25==0))|(ts>=1950)&(ts%10==0)
    print(np.array2string(np.c_[ts[k],o[k][:,[0,3,4,5,6]],np.interp(ts[k],W.index,W.values)],precision=3,suppress_small=True)); print({k:round(v,3) for k,v in stats(th).items()})
show(json.load(open('best.json'))['th'])
show([0.0057,1.0,1.48,1.0,0.363,2.66,2.05,0.05,0.0075])
