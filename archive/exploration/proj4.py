import sys, json, glob, numpy as np, datetime, pandas as pd
AMAX=int(sys.argv[2]) if len(sys.argv)>2 else 110; sys.argv=sys.argv[:2]
exec(open('/home/claude/work/model4.py').read().split('if __name__=="__main__":')[0])
fs=[json.load(open(f)) for f in sorted(glob.glob('/home/claude/work/best4_*.json'))]; print("seeds chi2:",[round(f['chi2'],1) for f in fs]); th=np.array(min(fs,key=lambda x:x['chi2'])['th'])
def cross(ts,v,level,after,down=True):
    c=(v[1:]<level)&(v[:-1]>=level) if down else (v[1:]>level)&(v[:-1]<=level); k=np.where((ts[1:]>after)&c)[0]
    if not len(k): return np.nan
    i=k[0]; return ts[i]+5*(v[i]-level)/(v[i]-v[i+1])
def peak(ts,v,lo=1900,hi=2600):
    w=np.where((ts>=lo)&(ts<=hi))[0]; ip=w[np.argmax(v[w])]
    if ip in (w[0],w[-1]): return float(ts[ip]),float(v[ip])
    y0,y1,y2=v[ip-1:ip+2]; dd=y0-2*y1+y2; off=0.5*(y0-y2)/dd if dd!=0 else 0; return float(ts[ip]+5*off),float(y1-0.25*(y0-y2)*off)
def todate(y):
    if not np.isfinite(y) or y>=9998: return 'never'
    yi=int(np.floor(y)); dt=datetime.date(yi,1,1)+datetime.timedelta(days=(y-yi)*365.2425); return dt.strftime('%A %d %B %Y')
def dates(th,t_end=9000,**kw):
    ts,o=run(th,t_end=t_end,**kw); N=o[:,:,0].sum(1); L=o[:,:,4].sum(1); rate=o[:,0,7]; d={}
    d['peakN_year'],d['peakN']=peak(ts,N); d['peakL_year'],d['peakL']=peak(ts,L); d['peakrate_year'],d['peakrate']=peak(ts,rate)
    d['N2050']=N[ts==2050][0]; d['N2100']=N[ts==2100][0]; d['N2200']=N[ts==2200][0]
    d['rate_half']=cross(ts,rate,d['peakrate']/2,d['peakrate_year']); d['regress']=cross(ts,rate,0.0,d['peakrate_year'])
    d['lt1bn']=cross(ts,N,1.0,d['peakN_year']); d['last']=cross(ts,np.log(np.maximum(N,1e-300)),np.log(1e-9),d['peakN_year'])
    d['old_peak']=float((o[:,:,5].sum(1)/N)[(ts>2000)&(ts<2400)].max()); d['support_min']=float((L/N)[(ts>2000)&(ts<2400)].min())
    return d,ts,o
if __name__=="__main__":
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    r=least_squares(resid,th,bounds=(LO,HI),x_scale=XS); th=r.x; n=len(r.fun); dof=n-len(th); chi=2*r.cost
    cov=np.linalg.pinv(r.jac.T@r.jac)*max(chi/dof,1.0); err=np.sqrt(np.diag(cov))
    print("chi2 %.1f n %d dof %d chi2/dof %.2f"%(chi,n,dof,chi/dof))
    for k,v,e,l,h in zip(NAMES,th,err,LO,HI): print("  %-6s %10.5f +- %.5f%s"%(k,v,e,"  (AT BOUND)" if min(v-l,h-v)<1e-6*max(1,abs(h)) else ""))
    print(json.dumps(summary(th)))
    g,beta,delta=th[:3]; Lstar=(delta/g)**(1/beta) if delta>0 else 0.0; print("L* = %.4f Bn workers"%Lstar)
    d0,ts,o=dates(th); print({k:round(float(v),3) for k,v in d0.items()})
    for k in ('peakN_year','peakL_year','peakrate_year','rate_half','regress','lt1bn','last'): print("  ",k,todate(d0[k]))
    N=o[:,:,0].sum(1); L=o[:,:,4].sum(1); Fw=o[:,:,3].sum(1)/(o[:,:,3]/o[:,:,1]).sum(1); rate=o[:,0,7]
    for y in (0,1000,1500,1800,1900,1950,2000,2023,2050,2100,2150,2200,2300,2500,3000,4000,6000,9000):
        i=np.where(ts>=y)[0][0]; print(y,"N %.4g L %.4g  groups N %s TFR %s e0 %s  wTFR %.2f rate %.4f%%/yr old %.3f"%(N[i],L[i],np.round(o[i,:,0],3),np.round(o[i,:,1],2),np.round(o[i,:,2],1),Fw[i],100*rate[i],o[i,:,5].sum()/N[i]))
    UNP=pd.read_csv('/home/claude/work/unproj.csv').set_index('Year'); print("UN vs model:",{y:(round(float(UNP.W[y]),2),round(float(N[ts==y][0]),2)) for y in (2050,2075,2100)},"C:",{y:(round(float(UNP.C[y]),2),round(float(o[ts==y,2,0][0]),2)) for y in (2050,2100)})
    gd=pd.read_csv('/home/claude/work/gdp.csv'); gy=gd.Year.values; ly=np.interp(gy,ts,((o[:,:,6]-np.log(o[:,:,0]))*o[:,:,0]).sum(1)/N); lg=np.log(gd['GDP per capita'].values); sl,ic=np.polyfit(ly,lg,1); print("GDP check: ln GDPpc vs pop-weighted ln y: slope %.3f r=%.3f"%(sl,np.corrcoef(ly,lg)[0,1]))
    mw=(o[:,:,0]*(o[:,:,2])).sum(1)/N; print("  corr(ln GDPpc, model e0) = %.3f"%np.corrcoef(np.interp(gy,ts,mw),lg)[0,1])
    BR=pd.read_csv('/home/claude/work/births.csv').set_index('Year'); print("births (M/yr) obs vs model:",{y:(round(float(BR.W[y]),1),round(float(1e3*np.interp(y,ts,o[:,:,3].sum(1))),1)) for y in (1950,1990,2023)})
    # uncertainty
    rng=np.random.default_rng(0); 
    try: Lc=np.linalg.cholesky(cov+1e-16*np.eye(len(th)))
    except Exception: w_,v_=np.linalg.eigh(cov); Lc=v_@np.diag(np.sqrt(np.maximum(w_,0)))
    smp=[]; trN=[]; trL=[]
    for i in range(300):
        t2=np.clip(th+Lc@rng.standard_normal(len(th)),LO,HI)
        try: dd,ts2,o2=dates(t2); smp.append(dd); trN.append(o2[:,:,0].sum(1)[ts2<=2400]); trL.append(o2[:,:,4].sum(1)[ts2<=2400])
        except Exception: pass
    Q=pd.DataFrame(smp).astype(float); print(Q.quantile([0.05,0.5,0.95]).round(2).T.to_string()); print("no regress in %.2f of samples; no last person in %.2f"%(Q.regress.isna().mean(),Q['last'].isna().mean()))
    i7=NAMES.index('Finf'); prof={}
    for Ff in (1.2,1.4,1.8,2.02):
        lo=LO.copy(); hi=HI.copy(); lo[i7]=Ff-1e-6; hi[i7]=Ff+1e-6; t0=th.copy(); t0[i7]=Ff
        rp=least_squares(resid,t0,bounds=(lo,hi),x_scale=XS); dp,_,_=dates(rp.x); prof[Ff]=(2*rp.cost,dp); print("profile Finf=%.2f: chi2 %.1f (best %.1f) peakN %.2f in %.0f N2100 %.2f regress %.0f last %.0f"%(Ff,2*rp.cost,chi,dp['peakN'],dp['peakN_year'],dp['N2100'],dp['regress'],dp['last']))
    json.dump(dict(th=list(th),err=list(err),chi2=chi,dof=dof,dates={k:float(v) for k,v in d0.items()},q={k:[float(x) for x in Q[k].quantile([0.05,0.5,0.95])] for k in Q},Lstar=Lstar),open('final4.json','w'))
    np.savez('traj4.npz',ts=ts,o=o,trN=np.array(trN),trL=np.array(trL))
