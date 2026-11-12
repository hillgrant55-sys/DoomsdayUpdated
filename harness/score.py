"""Shared scoring for hindcasts: point error, bias, interval coverage, skill against a baseline.
A forecast table has one row per (model, unit) with columns: model, unit, pred, lo, hi, obs, weight."""
import numpy as np, pandas as pd
def score(df, baseline=None):
    rows=[]
    for m,x in df.groupby('model',sort=False):
        e=x.pred-x.obs; w=x.weight/x.weight.sum()
        rows.append(dict(model=m,n=len(x),rmse=float(np.sqrt(np.mean(e**2))),rmse_w=float(np.sqrt(np.sum(w*e**2))),mae=float(np.mean(np.abs(e))),
                         bias=float(np.mean(e)),coverage=float(np.mean((x.obs>=x.lo)&(x.obs<=x.hi))),width=float(np.mean(x.hi-x.lo))))
    s=pd.DataFrame(rows)
    if baseline is not None:
        b=s[s.model.isin(baseline)].rmse.min(); s['vs_best_baseline']=s.rmse/b-1
    return s
