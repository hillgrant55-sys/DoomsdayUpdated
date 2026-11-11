import sys, json, numpy as np, pandas as pd, datetime, warnings
import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RAW=_os.path.join(_ROOT,'data','raw')+'/'; DER=_os.path.join(_ROOT,'data','derived')+'/'
RESDIR=_os.path.join(_ROOT,'results')+'/'; FIG=_os.path.join(_ROOT,'figures')+'/'
MODEL=_os.path.join(_ROOT,'src','model5.py')
warnings.filterwarnings('ignore')
src=open(MODEL).read().split('if __name__=="__main__":')[0]
g={'__name__':'m','__file__':MODEL}; exec(src,g); run=g['run']; NAMES=g['NAMES']; LO=g['LO']; HI=g['HI']
th=np.array(json.load(open(RESDIR+'best5_d0.003.json'))['th'])
r=g['least_squares'](g['resid'],th,bounds=(LO,HI),x_scale=g['XS']); th=r.x; n=len(r.fun); dof=n-len(th); chi=2*r.cost
cov=np.linalg.pinv(r.jac.T@r.jac)*max(chi/dof,1.0); err=np.sqrt(np.diag(cov)); RES={}
print("DEMOGRAPHY chi2 %.1f n %d dof %d chi2/dof %.2f"%(chi,n,dof,chi/dof))
for k,v,e,l,h in zip(NAMES,th,err,LO,HI): print("  %-5s %9.4f +- %.4f%s"%(k,v,e,"  (at bound)" if min(v-l,h-v)<1e-6*max(1,abs(v)) else ""))
S=g['summary'](th); print(json.dumps(S)); RES['fit']=dict(chi2=chi,n=n,dof=dof,th=dict(zip(NAMES,map(float,th))),err=dict(zip(NAMES,map(float,err))),summary=S)
def todate(y):
    if not np.isfinite(y): return 'never'
    yi=int(np.floor(y)); leap=(yi%4==0 and (yi%100!=0 or yi%400==0)); dt=datetime.date(yi,1,1)+datetime.timedelta(days=int((y-yi)*(366 if leap else 365))); return dt.strftime('%A %d %B %Y')
def cross(ts,N,level,after):
    k=np.where((ts[1:]>after)&(N[1:]<level)&(N[:-1]>=level))[0]
    if not len(k): return np.nan
    i=k[0]; return ts[i]+(ts[i+1]-ts[i])*np.log(N[i]/level)/np.log(N[i]/N[i+1])
def peak(ts,v,lo=1900,hi=2800):
    w=np.where((ts>=lo)&(ts<=hi))[0]; ip=w[np.argmax(v[w])]
    if ip in (w[0],w[-1]): return float(ts[ip]),float(v[ip])
    y0,y1,y2=np.log(v[ip-1:ip+2]); dd=y0-2*y1+y2; off=0.5*(y0-y2)/dd if dd!=0 else 0; return float(ts[ip]+(ts[ip+1]-ts[ip])*off),float(np.exp(y1-0.25*(y0-y2)*off))
def demog(run_,th_,t_end=7000):
    ts,o=run_(th_,t_end=t_end); N=o[:,:,0].sum(1); L=o[:,:,4].sum(1); pk,pv=peak(ts,N); lk,lv=peak(ts,L)
    d=dict(peak_year=pk,peak=pv,work_peak_year=lk,work_peak=lv,N2050=float(N[ts==2050][0]),N2100=float(N[ts==2100][0]),N2200=float(N[ts==2200][0]),half=cross(ts,N,pv/2,pk),lt1bn=cross(ts,N,1.0,pk),last=cross(ts,N,1e-9,pk),
           r_asym=float(np.log(N[ts==2600][0]/N[ts==2500][0])/100)); return d,ts,o
d0,ts,o=demog(run,th); RES['demog']=d0; print({k:round(float(v),3) for k,v in d0.items()}); 
for k in ('peak_year','work_peak_year','half','lt1bn','last'): print("  ",k,todate(d0[k]))
Nw=o[:,:,0].sum(1); Lw=o[:,:,4].sum(1); Ow=o[:,:,5].sum(1); Fw=o[:,:,3].sum(1)/(o[:,:,3]/o[:,:,1]).sum(1)
for y in (2025,2050,2100,2200):
    i=np.where(ts==y)[0][0]; print(y,"N",np.round(o[i,:,0],2),"TFR",np.round(o[i,:,1],2),"e0",np.round(o[i,:,2],1),"| world N %.2f TFR %.2f work %.3f old %.3f"%(Nw[i],Fw[i],Lw[i]/Nw[i],Ow[i]/Nw[i]))
RES['halving_years']=float(np.log(2)/-d0['r_asym']); print("asymptotic decline %.3f%%/yr, halving %.0f yr"%(100*d0['r_asym'],RES['halving_years']))
# ---- age-structure validation (not fitted) ----
aw=pd.read_csv(DER+'world_age.csv').set_index('Year'); ag=pd.read_csv(DER+'group_age.csv'); yv=np.arange(1950,2021,5)
f=lambda x: float(np.sqrt(np.mean(np.asarray(x)**2)))
val=dict(world_work=f(np.interp(yv,ts,Lw/Nw)-aw.work[yv].values),world_old=f(np.interp(yv,ts,Ow/Nw)-aw.old[yv].values))
for j,gn in enumerate('ABC'):
    x=ag[ag.g==gn].set_index('Year'); val['work_'+gn]=f(np.interp(yv,ts,o[:,j,4]/o[:,j,0])-x.work[yv].values); val['old_'+gn]=f(np.interp(yv,ts,o[:,j,5]/o[:,j,0])-x.old[yv].values)
print("age validation rms (share points):",{k:round(v,3) for k,v in val.items()}); print("  2020 world work: model %.3f obs %.3f; old: model %.3f obs %.3f"%(np.interp(2020,ts,Lw/Nw),aw.work[2020],np.interp(2020,ts,Ow/Nw),aw.old[2020])); RES['age_val']=val
RES['age2020']=dict(work_model=float(np.interp(2020,ts,Lw/Nw)),work_obs=float(aw.work[2020]),old_model=float(np.interp(2020,ts,Ow/Nw)),old_obs=float(aw.old[2020]))
# ---- UN benchmark ----
un=pd.read_csv(DER+'un_proj.csv').set_index('Year'); RES['un']={}
for y in (2050,2100):
    i=np.where(ts==y)[0][0]; RES['un'][y]=dict(model=[float(v) for v in o[i,:,0]]+[float(Nw[i])],un=[float(un[c][y]) for c in ('A','B','C','World')]); print("UN %d: model"%y,np.round(RES['un'][y]['model'],2),"UN",np.round(RES['un'][y]['un'],2))
RES['un_peak']=dict(year=int(un.World.idxmax()),value=float(un.World.max()))
# ---- uncertainty: demographic parameters ----
rng=np.random.default_rng(1); Lc=np.linalg.cholesky(cov+1e-18*np.eye(len(th))); smp=[]; traj=[]; trajL=[]; trajS=[]
for i in range(0):
    t2=np.clip(th+Lc@rng.standard_normal(len(th)),LO,HI)
    try: dd,ts2,o2=demog(run,t2); smp.append(dd); traj.append(o2[:,:,0].sum(1)); trajL.append(o2[:,:,4].sum(1))
    except Exception as e: pass

# ---- Finf profile ----
i7=NAMES.index('Finf'); RES['profile']={}
for Ff in (1.2,1.8,2.02):
    lo=LO.copy(); hi=HI.copy(); lo[i7]=Ff-1e-6; hi[i7]=Ff+1e-6; t0=th.copy(); t0[i7]=Ff; rp=g['least_squares'](g['resid'],t0,bounds=(lo,hi),x_scale=g['XS']); dp,_,_=demog(run,rp.x)
    RES['profile'][Ff]=dict(chi2=2*rp.cost,**{k:float(v) for k,v in dp.items()}); print("profile Finf=%.2f chi2 %.1f (best %.1f): peak %.2f in %.0f, N2100 %.2f, last %.0f"%(Ff,2*rp.cost,chi,dp['peak'],dp['peak_year'],dp['N2100'],dp['last']))
# ================= ECONOMICS (calibrated, not fitted) =================
pop=pd.read_csv(RAW+'population.csv'); pop.columns=['Entity','Code','Year','Pop']; res=pd.read_csv(RAW+'researchers-in-rd-per-million-people-vs-gdp-pc.csv'); res.columns=['Entity','Code','Year','RD','GDP','reg']
okc=lambda d: d[d.Code.notna() & ~d.Code.astype(str).str.startswith('OWID_') & ~d.Entity.str.contains('(',regex=False) & (d.Code.astype(str).str.len()==3)]
rr=okc(res).merge(okc(pop)[['Entity','Year','Pop']],on=['Entity','Year']).dropna(subset=['RD']); rr['tot']=rr.RD*rr.Pop/1e6
GWd=pd.read_csv(RAW+'global-average-gdp-per-capita-over-the-long-run.csv').set_index('Year')['GDP per capita']
def near(y):
    z=rr[(rr.Year>=y-2)&(rr.Year<=y+2)]; return z.groupby('Entity').tot.mean(), z.groupby('Entity').Pop.mean()
RES['research']={}
for y0,y1 in ((2000,2020),(2005,2020),(2010,2020)):
    (r0,p0),(r1,p1)=near(y0),near(y1); c=r0.index.intersection(r1.index); nR=np.log(r1[c].sum()/r0[c].sum())/(y1-y0); ye=min(y1,2019)
    xg=np.log(GWd[ye]/GWd[y0])/(ye-y0)-np.log(aw.work[ye]/aw.work[y0])/(ye-y0)
    RES['research']["%d-%d"%(y0,y1)]=dict(countries=len(c),researchers0=float(r0[c].sum()/1e6),researchers1=float(r1[c].sum()/1e6),nR=float(nR),x=float(xg),theta=float(nR/xg),pop_share=float(p1[c].sum()/Wp) if (Wp:=float(pop[(pop.Entity=='World')&(pop.Year==y1)].Pop.iloc[0])) else 0)
    print("researchers %d-%d: %d countries (%.0f%% of world), %.2f->%.2f M, growth %.2f%%/yr; GDP per worker growth %.2f%%/yr; theta/beta = %.2f"%(y0,y1,len(c),100*RES['research']["%d-%d"%(y0,y1)]['pop_share'],r0[c].sum()/1e6,r1[c].sum()/1e6,100*nR,100*xg,nR/xg))
THETA=RES['research']['2000-2020']['theta']; X0=RES['research']['2000-2020']['x']
# research intensity headroom: world researchers per person vs early-decline group (latest values)
grpmap=pd.read_csv(DER+'cross.csv'); 
tf=pd.read_csv(RAW+'children-born-per-woman.csv'); tf.columns=['Entity','Code','Year','TFR']; t75=tf[tf.Year==1975].set_index('Entity').TFR
(r1,p1)=near(2020); inA=[c for c in r1.index if c in t75.index and t75[c]<3]; RHO=float((r1[inA].sum()/p1[inA].sum())/(r1.sum()/p1.sum())); print("research intensity: early group / covered world = %.2f"%RHO); RES['rho_max']=RHO
def econ(ts_,N_,L_,theta=THETA,x0=X0,delta=0.0,rho_max=1.0,mu=0.0,kappa=1.0,t_end=2800,dt=0.1,beta=1.0,nu=0.0):
    t=np.arange(2025,t_end+dt/2,dt); N=np.exp(np.interp(t,ts_,np.log(np.maximum(N_,1e-300)))); L=np.exp(np.interp(t,ts_,np.log(np.maximum(L_,1e-300)))); sig=L/N
    lnA=np.zeros(len(t)); x=np.zeros(len(t)); blow=np.nan
    for i in range(len(t)):
        rho=1+(rho_max-1)*min(max((t[i]-2025)/50,0),1); R=(L[i]/L[0]*rho+mu*np.exp(min(kappa*lnA[i]+nu*(t[i]-2025),300)))/(1+mu)
        x[i]=(x0+delta)*R**beta*np.exp(-theta*lnA[i])-delta
        if i+1<len(t):
            lnA[i+1]=lnA[i]+x[i]*dt
            if lnA[i+1]>60: blow=t[i+1]; lnA[i+1:]=np.nan; x[i+1:]=np.nan; break
    ypc=np.exp(lnA)*sig/sig[0]; Y=ypc*N/N[0]; out=dict(blow=float(blow))
    if np.isfinite(blow): return out,t,x,ypc,Y
    ip=np.argmax(Y); out['Y_peak']=float(Y[ip]); out['Y_peak_year']=np.nan
    if 0<ip<len(t)-1:
        y0,y1,y2=np.log(Y[ip-1:ip+2]); dd=y0-2*y1+y2; out['Y_peak_year']=float(t[ip]+dt*(0.5*(y0-y2)/dd if dd!=0 else 0))
    ip2=np.argmax(ypc); out['ypc_peak_year']=float(t[ip2]) if ip2<len(t)-1 else np.nan; out['ypc_peak']=float(ypc[ip2])
    for lev in (0.01,0.005): k=np.where(x<lev)[0]; out['x_below_%g'%lev]=float(t[k[0]]) if len(k) else np.nan
    for y in (2050,2100,2200,2300): out['ypc_%d'%y]=float(np.interp(y,t,ypc)); out['Y_%d'%y]=float(np.interp(y,t,Y)); out['x_%d'%y]=float(np.interp(y,t,x))
    return out,t,x,ypc,Y
E={}; curves={}
def rep(name,**kw):
    tsx=kw.pop('ts_',ts); Nx=kw.pop('N_',Nw); Lx=kw.pop('L_',Lw); e,t,x,ypc,Y=econ(tsx,Nx,Lx,**kw); E[name]=e; curves[name]=(t,x,ypc,Y)
    if np.isfinite(e['blow']): print("  %-34s SINGULARITY in %.1f  (%s)"%(name,e['blow'],todate(e['blow'])))
    else: print("  %-34s output peak %.1f (%s) at %.2fx | income/person 2100 %.2fx 2200 %.2fx, peak %s | growth 2050 %.2f%% 2100 %.2f%% | <1%% in %.0f, <0.5%% in %.0f"%(name,e['Y_peak_year'],todate(e['Y_peak_year']),e['Y_peak'],e['ypc_2100'],e['ypc_2200'],('%.0f'%e['ypc_peak_year']) if np.isfinite(e['ypc_peak_year']) else 'none',100*e['x_2050'],100*e['x_2100'],e['x_below_0.01'],e['x_below_0.005']))
print("ECONOMICS: theta=%.2f x0=%.2f%%/yr"%(THETA,100*X0))
rep('baseline'); rep('theta 1.0',theta=1.0); rep('theta 2.2',theta=2.2); rep('research share catches up',rho_max=RHO)
for dl in (0.0025,0.005,0.01): rep('delta %.2f%%'%(100*dl),delta=dl)
rep('no ideas effect (theta=0, x const)',theta=0.0,beta=0.0)
for mu in (0.01,0.1):
    for kp in (1.0,THETA,2.0,3.0): rep('machines mu=%g kappa=%.2f'%(mu,kp),mu=mu,kappa=kp)
# UN population with model age shares, to 2100
tu=np.arange(2025,2101,5); Nun=un.World[tu].values; Lun=Nun*np.interp(tu,ts,Lw/Nw); e,t,x,ypc,Y=econ(tu,Nun,Lun,t_end=2100); E['UN population to 2100']=e; print("  UN population: output peak",e.get('Y_peak_year'),"growth 2100 %.2f%%, workforce growth 2095-2100 %.2f%%/yr"%(100*e['x_2100'],100*np.log(Lun[-1]/Lun[-2])/5))
# demographic uncertainty on the baseline economic date

# ---- longevity ----
RES['longevity']={}
for nm,rp in (("pension age unchanged",[("ALT_SHIFT=0","ALT_SHIFT=50")]),("working life +50",[("ALT_SHIFT=0","ALT_SHIFT=50"),("ALT_WORK=False","ALT_WORK=True")])):
    s2=src.replace("A_=110;","A_=165;")
    for a_,b_ in rp: s2=s2.replace(a_,b_)
    g3={'__name__':'m','__file__':MODEL}; exec(s2,g3); dl,tsl,ol=demog(g3['run'],th); Nl=ol[:,:,0].sum(1); Ll=ol[:,:,4].sum(1); e,t,x,ypc,Y=econ(tsl,Nl,Ll); curves['long '+nm]=(t,x,ypc,Y); i=np.where(tsl==2100)[0][0]
    RES['longevity'][nm]=dict(demog={k:float(v) for k,v in dl.items()},econ=e,e0_2100=[float(v) for v in ol[i,:,2]],work2100=float(Ll[i]/Nl[i]),old2100=float(ol[i,:,5].sum()/Nl[i]))
    print("LONGEVITY (%s): peak %.2f Bn in %.0f; N2100 %.2f; last %.0f (%s); e0 2100 %s; work share 2100 %.2f, 65+ %.2f; output peak %s at %.2fx; income 2100 %.2fx"%(nm,dl['peak'],dl['peak_year'],dl['N2100'],dl['last'],todate(dl['last']),np.round(ol[i,:,2],0),Ll[i]/Nl[i],ol[i,:,5].sum()/Nl[i],e.get('Y_peak_year'),e.get('Y_peak',np.nan),e.get('ypc_2100',np.nan)))
    if nm.startswith('pension'): np.save(RESDIR+'long_traj.npy',np.c_[tsl,Nl])
for mu in (0.01,0.1):
    rep('machines growing 3.5%%/yr from %g'%mu,mu=mu,kappa=0.0,nu=RES['research']['2000-2020']['nR'])
    e,t,x,ypc,Y=econ(ts,Nw,Lw,mu=mu,kappa=2.0,t_end=6000,dt=0.25); print("  machines mu=%g kappa=2 long horizon: singularity"%mu,e['blow'])
# sensitivity to modelling choices: shock cap
thf=np.array(json.load(open(RESDIR+'best5_d0.03.json'))['th']); gf={'__name__':'m','__file__':MODEL}; exec(src.replace('DMAX=0.003','DMAX=0.03'),gf); df,tsf,of=demog(gf['run'],thf); ef=econ(tsf,of[:,:,0].sum(1),of[:,:,4].sum(1))[0]
RES['alt_free_shock']=dict(demog={k:float(v) for k,v in df.items()},econ=ef,Finf=float(thf[NAMES.index('Finf')]),d=float(thf[NAMES.index('d')]))
print("ALT free shock: Finf %.2f d %.4f peak %.2f in %.1f, N2100 %.2f, last %.0f (%s); output peak %.1f"%(thf[NAMES.index('Finf')],thf[NAMES.index('d')],df['peak'],df['peak_year'],df['N2100'],df['last'],todate(df['last']),ef['Y_peak_year']))
lo=LO.copy(); hi=HI.copy(); lo[i7]=1.2-1e-6; hi[i7]=1.2+1e-6; t0=th.copy(); t0[i7]=1.2; rp=g['least_squares'](g['resid'],t0,bounds=(lo,hi),x_scale=g['XS']); dp,tsp,op=demog(run,rp.x); ep=econ(tsp,op[:,:,0].sum(1),op[:,:,4].sum(1))[0]; print("ALT Finf 1.2: output peak %.1f last %.0f"%(ep['Y_peak_year'],dp['last'])); RES['alt_F12']=dict(demog={k:float(v) for k,v in dp.items()},econ=ep)
np.save(RESDIR+'alt_free_traj.npy',np.c_[tsf,of[:,:,0].sum(1)])
print("BASELINE economic doomsday:",E['baseline']['Y_peak_year'],todate(E['baseline']['Y_peak_year']))
RES['econ']=E; RES['theta']=THETA; RES['x0']=X0
json.dump(RES,open(RESDIR+'results.json','w'),indent=1,default=float)
np.savez(RESDIR+'fig_data.npz',ts=ts,o=o,th=th,**{('c_'+k.replace(' ','_').replace('=','').replace('%','').replace('.','p').replace('(','').replace(')','').replace(',','').replace('+','')):np.array(v) for k,v in curves.items()})
print("curve keys:",[k for k in curves])
