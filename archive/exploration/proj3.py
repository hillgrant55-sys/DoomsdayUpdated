import sys, json, glob, numpy as np, datetime, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('/home/claude/work/model3.py').read().split('if __name__=="__main__":')[0])
fs=[json.load(open(f)) for f in glob.glob('/home/claude/work/best3_*.json')]; b=min(fs,key=lambda x:x['chi2']); th=np.array(b['th'])
print("seeds chi2:",[round(f['chi2'],1) for f in fs])
r=least_squares(resid,th,bounds=(LO,HI),x_scale=XS); th=r.x; n=len(r.fun); dof=n-len(th); chi=2*r.cost
JJ=r.jac; cov=np.linalg.pinv(JJ.T@JJ)*max(chi/dof,1.0); err=np.sqrt(np.diag(cov))
print("chi2 %.1f  n %d  dof %d  chi2/dof %.2f"%(chi,n,dof,chi/dof))
for k,v,e,l,h in zip(NAMES,th,err,LO,HI): print("  %-5s %9.4f +- %.4f %s"%(k,v,e,"  (AT BOUND)" if min(v-l,h-v)<1e-6*max(1,abs(v)) else ""))
S=summary(th); print(json.dumps(S,indent=None))
def cross(ts,N,level,after):
    k=np.where((ts[1:]>after)&(N[1:]<level)&(N[:-1]>=level))[0]
    if not len(k): return np.nan
    i=k[0]; return ts[i]+5*np.log(N[i]/level)/np.log(N[i]/N[i+1])
def dates(th,t_end=9000):
    ts,o=run(th,t_end=t_end); N=o[:,:,0].sum(1); w=ts<=2600; ip=np.argmax(N[w])
    # refine peak with a parabola through the three points around the maximum
    if 0<ip<len(N)-1:
        y0,y1,y2=np.log(N[ip-1:ip+2]); dd=y0-2*y1+y2; off=0.5*(y0-y2)/dd if dd!=0 else 0; pk=ts[ip]+5*off; pv=np.exp(y1-0.25*(y0-y2)*off)
    else: pk,pv=ts[ip],N[ip]
    return dict(peak_year=pk,peak=pv,N2050=N[ts==2050][0],N2100=N[ts==2100][0],N2200=N[ts==2200][0],N2300=N[ts==2300][0],half=cross(ts,N,pv/2,pk),lt1bn=cross(ts,N,1.0,pk),lt1M=cross(ts,N,1e-3,pk),last=cross(ts,N,1e-9,pk),
                r=np.log(N[ts==2500][0]/N[ts==2400][0])/100),ts,o
d0,ts,o=dates(th); print({k:(round(float(v),3)) for k,v in d0.items()})
def todate(y):
    yi=int(np.floor(y)); dt=datetime.date(yi,1,1)+datetime.timedelta(days=(y-yi)*(366 if (yi%4==0 and (yi%100!=0 or yi%400==0)) else 365)); return dt.strftime('%A %d %B %Y')
for k in ('peak_year','half','lt1bn','lt1M','last'):
    if np.isfinite(d0[k]): print(k,todate(d0[k]))
Nw=o[:,:,0].sum(1); Fw=o[:,:,3].sum(1)/(o[:,:,3]/o[:,:,1]).sum(1)
for y in (2023,2050,2100,2200): i=np.where(ts>=y)[0][0]; print(y,"groups N",np.round(o[i,:,0],2),"TFR",np.round(o[i,:,1],2),"e0",np.round(o[i,:,2],1),"world TFR %.2f"%Fw[i])
# ---- uncertainty: sample parameters from the fit covariance ----
rng=np.random.default_rng(0); Lc=np.linalg.cholesky(cov+1e-18*np.eye(len(th))); smp=[]; traj=[]
for i in range(300):
    t2=th+Lc@rng.standard_normal(len(th))
    if np.any(t2<=LO*0.999)|np.any(t2>=HI*1.001): t2=np.clip(t2,LO,HI)
    try: dd,ts2,o2=dates(t2,t_end=9000); smp.append(dd); traj.append(o2[:,:,0].sum(1)[ts2<=2300])
    except Exception: pass
import pandas as pd
Q=pd.DataFrame(smp).astype(float); print("samples",len(Q)); print(Q.quantile([0.05,0.5,0.95]).round(2).to_string()); print("share of samples with no collapse (no N<1 by 9000): %.2f"%Q['last'].isna().mean())
traj=np.array(traj); lo5,hi95=np.percentile(traj,[5,95],axis=0)
# ---- Finf profile ----
i7=NAMES.index('Finf')
for Ff in (1.2,1.6,1.8,2.02):
    lo=LO.copy(); hi=HI.copy(); lo[i7]=Ff-1e-6; hi[i7]=Ff+1e-6; t0=th.copy(); t0[i7]=Ff
    rp=least_squares(resid,t0,bounds=(lo,hi),x_scale=XS); dp,_,_=dates(rp.x); print("profile Finf=%.2f: chi2 %.1f (best %.1f) peak %.2f in %.0f, N2100 %.2f, <1Bn %.0f, last %.0f"%(Ff,2*rp.cost,chi,dp['peak'],dp['peak_year'],dp['N2100'],dp['lt1bn'],dp['last']))
json.dump(dict(th=list(th),err=list(err),chi2=chi,dof=dof,dates={k:float(v) for k,v in d0.items()},q={k:[float(x) for x in Q[k].quantile([0.05,0.5,0.95])] for k in Q}),open('final3.json','w'))
# ---------------- figure ----------------
ink='#1f1f1e'; mut='#6b6a64'; grid='#e4e3dd'; C=['#2a78d6','#eb6834','#1baf7a']; GL=['A: early decline','B: middle','C: late']
plt.rcParams.update({'font.size':10,'axes.edgecolor':mut,'axes.labelcolor':ink,'xtick.color':mut,'ytick.color':mut,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(2,3,figsize=(16.5,9.8),dpi=150); fig.patch.set_facecolor('white')
def sty(a,title): a.grid(True,color=grid,lw=0.8); a.set_axisbelow(True); a.set_title(title,loc='left',fontsize=11,color=ink)
T0d=2026.87
a=axs[0,0]; tl=np.linspace(0,2026.4,3000); w=(ts>=0)&(ts<=2025)
a.plot(T0d-tl,179/(T0d-tl)**0.99,ls=(0,(5,4)),color=mut,lw=1.5,label='Eq. 11 (1960 fit)')
a.plot(T0d-ts[w],Nw[w],color=ink,lw=2,label='Three-group model, world total')
a.plot(T0d-np.maximum(tN,1),W[tN].values,'o',mfc='white',mec=ink,mew=1.2,ms=5,label='World population (your data)',zorder=5)
a.set_xscale('log'); a.set_yscale('log'); a.set_xlim(2600,2.5); a.set_ylim(0.08,30); a.set_yticks([0.1,0.3,1,3,10]); a.set_yticklabels(['0.1','0.3','1','3','10']); a.set_xticks([2000,200,20,3.87]); a.set_xticklabels(['2000','200','20','4'])
a.set_xlabel('Dooms-time τ = 2026.87 − t  (years)'); a.set_ylabel('N (billions)'); a.legend(frameon=False,loc='lower right',fontsize=9); sty(a,"World population on the paper's axes")
a=axs[0,1]; ya=np.arange(1950,2024); am1=100*np.log(W[ya[1:]].values/W[ya[:-1]].values); a.plot(W[ya[1:]].values,am1,'o',mfc='white',mec=ink,mew=1.0,ms=4,label='Observed, yearly 1950–2023',zorder=5)
yh=np.array([1700,1750,1800,1850,1900,1920,1930,1940,1950]); a.plot(np.sqrt(W[yh[1:]].values*W[yh[:-1]].values),100*np.log(W[yh[1:]].values/W[yh[:-1]].values)/np.diff(yh),'o',mfc='white',mec=mut,mew=1.0,ms=4,label='Observed, 1700–1950',zorder=4)
nn=np.linspace(0.3,10,50); a.plot(nn,100*nn/179,ls=(0,(5,4)),color=mut,lw=1.5,label='Eq. 3: α = α₀N')
ww=(ts[1:]>=1500)&(ts[1:]<=2150); a.plot(np.sqrt(Nw[1:]*Nw[:-1])[ww],(100*np.log(Nw[1:]/Nw[:-1])/5)[ww],color=ink,lw=2,label='Model (to 2150)')
a.axhline(0,color=mut,lw=0.8); a.set_xlim(0,10); a.set_ylim(-0.8,3); a.set_xlabel('N (billions)'); a.set_ylabel('Productivity α  (% per year)'); a.legend(frameon=False,loc='upper right',fontsize=9); sty(a,'Productivity versus population')
a=axs[0,2]; cr=pd.read_csv('/home/claude/work/cross.csv'); cr=cr[cr.Year>=1950]; bins=np.arange(35,87.5,2.5); cr['bin']=pd.cut(cr.e0,bins)
gb=cr.groupby('bin',observed=True).apply(lambda x: pd.Series(dict(e=np.average(x.e0,weights=x.Pop),f=np.average(x.TFR,weights=x.Pop))))
a.plot(gb.e,gb.f,'o',mfc='white',mec=ink,mew=1.2,ms=5.5,label='All countries 1950–2023, binned',zorder=5)
zz=np.logspace(-4,6,400); g_,beta_,a_,yM_,yF_,b_,Finf_=th[:7]; mm=1-(1+zz/yM_)**(-a_)
for j,F0_ in enumerate([th[7],th[14],th[15]]): a.plot(np.interp(mm,MG,tables(F0_)[2]),Finf_+(F0_-Finf_)/(1+(zz/yF_)**b_),color=C[j],lw=2,label='Model, group '+'ABC'[j])
a.axhline(FREP,color=mut,lw=1,ls=(0,(2,3))); a.text(21,FREP+0.12,'replacement at low mortality',color=mut,fontsize=9)
a.set_xlim(20,87); a.set_ylim(0,8.5); a.set_xlabel('Life expectancy at birth (years)'); a.set_ylabel('Children per woman'); a.legend(frameon=False,loc='lower left',fontsize=9); sty(a,'Fertility against life expectancy')
wt=(ts>=1900)&(ts<=2100)
for col,key,ttl,yl,ylim in ((0,1,'Children per woman by group','Children per woman',(0,8.5)),(1,2,'Life expectancy by group','Years',(20,90))):
    a=axs[1,col]
    for j in range(J):
        a.plot(ts[wt],o[wt,j,key],color=C[j],lw=2,label='Model, '+GL[j]); a.plot(tr,D[j]['TFR' if key==1 else 'e0'],'o',mfc='white',mec=C[j],mew=1.4,ms=5,zorder=5)

    a.plot([],[],'o',mfc='white',mec=ink,mew=1.2,ms=5,label='Observed (5-year means)')
    if key==1: a.axhline(FREP,color=mut,lw=1,ls=(0,(2,3)))
    a.set_xlim(1900,2112); a.set_ylim(*ylim); a.set_xlabel('Year'); a.set_ylabel(yl); a.legend(frameon=False,loc='upper right' if key==1 else 'lower right',fontsize=9); sty(a,ttl)
a=axs[1,2]; w3=(ts>=1900)&(ts<=2300); tb=ts[ts<=2300]; wb=tb>=1900
a.fill_between(tb[wb],lo5[wb],hi95[wb],color=mut,alpha=0.2,lw=0,label='World, 5–95% of fit uncertainty')
a.plot(ts[w3],Nw[w3],color=ink,lw=2.2,label='World, model')
for j in range(J): a.plot(ts[w3],o[w3,j,0],color=C[j],lw=1.8,label=GL[j]); a.text(2303,o[ts==2300,j,0][0],'ABC'[j],color=ink,fontsize=10,va='center')
yo=np.arange(1900,2024,5); a.plot(yo,W[yo].values,'o',mfc='white',mec=ink,mew=1.2,ms=4.5,label='World population (your data)',zorder=5)
a.axvline(2026.87,color=mut,lw=1,ls=(0,(2,3))); a.text(2022,10.6,'13 Nov 2026',color=mut,fontsize=9,ha='right')
a.set_xlim(1900,2320); a.set_ylim(0,11.5); a.set_xlabel('Year'); a.set_ylabel('N (billions)'); a.legend(frameon=False,loc='upper right',fontsize=9); sty(a,'Projection')
fig.tight_layout(); fig.savefig('/home/claude/work/doomsday_three_group_model.png',facecolor='white')
