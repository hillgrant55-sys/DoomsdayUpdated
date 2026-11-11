import sys, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('/home/claude/work/model4.py').read().split('if __name__=="__main__":')[0])
Z=np.load('traj4.npz'); ts=Z['ts']; o=Z['o']; trN=Z['trN']; trL=Z['trL']; S=np.load('scen4.npz'); F=json.load(open('final4.json')); SC=json.load(open('scen4.json')); d0=F['dates']
N=o[:,:,0].sum(1); L=o[:,:,4].sum(1); rate=o[:,0,7]; UNP=pd.read_csv('unproj.csv').set_index('Year'); AGd=pd.read_csv('ages.csv')
ink='#1f1f1e'; mut='#6b6a64'; grid='#e4e3dd'; C=['#2a78d6','#eb6834','#1baf7a']; GL=['A: fell below 3 before 1975','B: between 1975 and 2010','C: not by 2010']
plt.rcParams.update({'font.size':10.5,'axes.edgecolor':mut,'axes.labelcolor':ink,'xtick.color':mut,'ytick.color':mut,'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Serif'})
def sty(a,title): a.grid(True,color=grid,lw=0.8); a.set_axisbelow(True); a.set_title(title,loc='left',fontsize=11.5,color=ink)
T0d=2026.87
# ---------- Fig 1 ----------
fig,axs=plt.subplots(1,2,figsize=(12,5.4),dpi=160); fig.patch.set_facecolor('white')
a=axs[0]; tl=np.linspace(0,2026.4,3000); w=(ts>=0)&(ts<=2025)
a.plot(T0d-tl,179/(T0d-tl)**0.99,ls=(0,(5,4)),color=mut,lw=1.5,label='1960 law (their Eq. 11)')
a.plot(T0d-ts[w],N[w],color=ink,lw=2,label='This work')
a.plot(T0d-np.maximum(tN,1),W[tN].values,'o',mfc='white',mec=ink,mew=1.2,ms=5,label='World population (2)',zorder=5)
a.set_xscale('log'); a.set_yscale('log'); a.set_xlim(2600,2.5); a.set_ylim(0.08,40); a.set_yticks([0.1,0.3,1,3,10,30]); a.set_yticklabels(['0.1','0.3','1','3','10','30']); a.set_xticks([2027,1027,227,27,3.87]); a.set_xticklabels(['A.D. 0','1000','1800','2000','2023'])
a.set_xlabel('Historical time, spaced by years remaining to 13 November 2026'); a.set_ylabel('N (billions)'); a.legend(frameon=False,loc='upper left',fontsize=9.5); sty(a,"A. The 1960 plot, with 63 more years of data")
a=axs[1]; ya=np.arange(1950,2024); a.plot(W[ya[1:]].values,100*np.log(W[ya[1:]].values/W[ya[:-1]].values),'o',mfc='white',mec=ink,mew=1.0,ms=4,label='Observed, yearly 1950–2023',zorder=5)
yh=np.array([1500,1600,1700,1750,1800,1850,1900,1920,1930,1940,1950]); a.plot(np.sqrt(W[yh[1:]].values*W[yh[:-1]].values),100*np.log(W[yh[1:]].values/W[yh[:-1]].values)/np.diff(yh),'o',mfc='white',mec=mut,mew=1.0,ms=4,label='Observed, 1500–1950',zorder=4)
nn=np.linspace(0.2,11,50); a.plot(nn,100*nn/179,ls=(0,(5,4)),color=mut,lw=1.5,label='1960 law: α = α₀N')
ww=(ts[1:]>=1500)&(ts[1:]<=2200); a.plot(np.sqrt(N[1:]*N[:-1])[ww],(100*np.log(N[1:]/N[:-1])/5)[ww],color=ink,lw=2,label='This work (to 2200)')
a.axhline(0,color=mut,lw=0.8); a.set_xlim(0,11); a.set_ylim(-1,3); a.set_xlabel('N (billions)'); a.set_ylabel('Productivity α (% per year)'); a.legend(frameon=False,loc='upper right',fontsize=9.5); sty(a,'B. Productivity against population')
fig.tight_layout(); fig.savefig('fig1.png',facecolor='white'); plt.close(fig)
# ---------- Fig 2 ----------
fig,axs=plt.subplots(1,3,figsize=(15.5,5.2),dpi=150); fig.patch.set_facecolor('white'); wt=(ts>=1900)&(ts<=2100)
for a,key,dk,ttl,yl,ylim,loc in ((axs[0],1,'TFR','A. Children per woman','Children per woman',(0,7.5),'upper right'),(axs[1],2,'e0','B. Life expectancy at birth','Years',(15,90),'lower right'),(axs[2],None,'ws','C. Share of population aged 15–64','Share',(0.45,0.75),'upper left')):
    for j in range(J):
        v=o[:,j,key] if key else o[:,j,4]/o[:,j,0]; a.plot(ts[wt],v[wt],color=C[j],lw=2,label='Model, group '+'ABC'[j]); a.plot(tr,D[j][dk],'o',mfc='white',mec=C[j],mew=1.4,ms=5,zorder=5)
    a.plot([],[],'o',mfc='white',mec=ink,mew=1.2,ms=5,label='Observed')
    if key==1: a.axhline(FREP,color=mut,lw=1,ls=(0,(2,3))); a.text(1903,FREP+0.12,'replacement',color=mut,fontsize=9)
    a.set_xlim(1900,2100); a.set_ylim(*ylim); a.set_xlabel('Year'); a.set_ylabel(yl); a.legend(frameon=False,loc=loc,fontsize=9.5); sty(a,ttl)
fig.tight_layout(); fig.savefig('fig2.png',facecolor='white'); plt.close(fig)
# ---------- Fig 3 ----------
fig,axs=plt.subplots(1,3,figsize=(15.5,5.4),dpi=150); fig.patch.set_facecolor('white')
a=axs[0]; tb=ts[ts<=2400]; wb=tb>=1900; lo,hi=np.percentile(trN,[5,95],axis=0); w3=(ts>=1900)&(ts<=2400)
a.fill_between(tb[wb],lo[wb],hi[wb],color=mut,alpha=0.2,lw=0,label='5–95% of fit uncertainty'); a.plot(ts[w3],N[w3],color=ink,lw=2.2,label='World population, this work'); a.plot(ts[w3],L[w3],color=C[0],lw=2,label='World workforce (ages 15–64)')
yu=np.arange(2025,2101,5); a.plot(yu,UNP.W[yu].values,'^',mfc='white',mec=ink,mew=1.1,ms=5.5,label='UN medium projection (4)',zorder=5); yo=np.arange(1900,2024,10); a.plot(yo,W[yo].values,'o',mfc='white',mec=ink,mew=1.2,ms=4.5,label='World population (2)',zorder=5)
a.axvline(T0d,color=mut,lw=1,ls=(0,(2,3))); a.text(T0d-6,11.6,'13 Nov 2026',color=mut,fontsize=9,ha='right'); a.set_xlim(1900,2400); a.set_ylim(0,12.5); a.set_xlabel('Year'); a.set_ylabel('Billions'); a.legend(frameon=False,loc='upper right',fontsize=9); sty(a,'A. Population and workforce')
a=axs[1]; w4=(ts>=0)&(ts<=3200); a.plot(ts[w4],L[w4],color=C[0],lw=2,label='World workforce L'); a.axhline(F['Lstar'],color=ink,lw=1.2,ls=(0,(5,4)),label='Critical workforce L* = %.0f million'%(1e3*F['Lstar']))
a.set_yscale('log'); a.set_ylim(0.005,12); a.set_xlim(0,3200); a.set_yticks([0.01,0.1,1,10]); a.set_yticklabels(['0.01','0.1','1','10'])
a.plot([d0['regress']],[F['Lstar']],'o',mfc='white',mec=ink,mew=1.5,ms=8,zorder=6); a.annotate('Doomsday\n6 May 2686',(d0['regress'],F['Lstar']),xytext=(2150,0.02),color=ink,fontsize=10,arrowprops=dict(arrowstyle='-',color=mut,lw=0.8))
a.annotate('Antiquity: a millennium\njust above L*',(300,0.13),xytext=(120,0.012),color=ink,fontsize=10,arrowprops=dict(arrowstyle='-',color=mut,lw=0.8))
a.set_xlabel('Year'); a.set_ylabel('Billions of workers'); a.legend(frameon=False,loc='upper left',fontsize=9.5); sty(a,'B. The coalition falls back through its critical size')
a=axs[2]; sts=S['ts']; w5=(sts>=1900)&(sts<=3000)
for lab,arr,col,ls in (('Baseline',S['o'],ink,'-'),('Machines hold the workforce at its peak',S['oA'],C[1],'-'),('Lives 50 years longer, work to 115',S['oL'],C[2],'-'),('Lives 50 years longer, retire at 65',S['oL65'],C[0],(0,(4,3)))):
    a.plot(sts[w5],100*arr[w5,0,7],color=col,lw=2,ls=ls,label=lab)
a.axhline(0,color=mut,lw=0.8); a.set_xlim(1900,3000); a.set_ylim(-1,19); a.set_xlabel('Year'); a.set_ylabel('Growth of capability T (% per year)'); a.legend(frameon=False,loc='upper right',fontsize=9); sty(a,'C. Rate of progress under the optimists')
fig.tight_layout(); fig.savefig('fig3.png',facecolor='white'); plt.close(fig)
print("ok", "L at 0: %.3f, 500: %.3f, 1000: %.3f"%tuple(np.interp([0,500,1000],ts,L)))
