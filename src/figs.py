import sys, json, numpy as np, pandas as pd, matplotlib, warnings
import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RAW=_os.path.join(_ROOT,'data','raw')+'/'; DER=_os.path.join(_ROOT,'data','derived')+'/'
RESDIR=_os.path.join(_ROOT,'results')+'/'; FIG=_os.path.join(_ROOT,'figures')+'/'
MODEL=_os.path.join(_ROOT,'src','model5.py')
warnings.filterwarnings('ignore'); matplotlib.use('Agg'); import matplotlib.pyplot as plt
g={'__name__':'m','__file__':MODEL}; exec(open(MODEL).read().split('if __name__=="__main__":')[0],g)
Z=np.load(RESDIR+'fig_data.npz'); ts=Z['ts']; o=Z['o']; th=Z['th']; RES=json.load(open(RESDIR+'results.json')); print([k for k in Z.files if k.startswith('c_')])
W=g['W']; D=g['D']; tr=g['tr']; tN=g['tN']; FREP=g['FREP']; Nw=o[:,:,0].sum(1); Lw=o[:,:,4].sum(1); Ow=o[:,:,5].sum(1)
ink='#1f1f1e'; mut='#6b6a64'; grid='#e4e3dd'; C=['#2a78d6','#eb6834','#1baf7a']; GL=['A: early decline','B: middle','C: late']
plt.rcParams.update({'font.size':10.5,'axes.edgecolor':mut,'axes.labelcolor':ink,'xtick.color':mut,'ytick.color':mut,'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Serif'})
def sty(a,title=None):
    a.grid(True,color=grid,lw=0.8); a.set_axisbelow(True)
    if title: a.set_title(title,loc='left',fontsize=11,color=ink)
# ---------- Fig 1 ----------
fig,a=plt.subplots(figsize=(7.2,5.6),dpi=170); T0d=2026.87; tl=np.linspace(0,2026.4,3000); w=(ts>=0)&(ts<=2025)
a.plot(T0d-tl,179/(T0d-tl)**0.99,ls=(0,(5,4)),color=mut,lw=1.5,label='von Foerster et al., Eq. 11')
a.plot(T0d-ts[w],Nw[w],color=ink,lw=2,label='This work')
a.plot(T0d-np.maximum(tN,1),W[tN].values,'o',mfc='white',mec=ink,mew=1.2,ms=5,label='World population, modern estimates',zorder=5)
a.set_xscale('log'); a.set_yscale('log'); a.set_xlim(2600,2.5); a.set_ylim(0.08,30); a.set_yticks([0.1,0.3,1,3,10]); a.set_yticklabels(['100','300','1,000','3,000','10,000']); a.set_xticks([2000,200,20,3.87]); a.set_xticklabels(['2000','200','20','4'])
a.set_xlabel('Years till Friday, November 13, 2026'); a.set_ylabel('Number of humans (millions)'); a.legend(frameon=False,loc='lower right',fontsize=9.5); sty(a); fig.tight_layout(); fig.savefig(FIG+'fig1_doomstime.png',facecolor='white'); plt.close(fig)
# ---------- Fig 2 ----------
fig,axs=plt.subplots(2,2,figsize=(11.5,9.2),dpi=170)
a=axs[0,0]; cr=pd.read_csv(DER+'cross.csv'); cr=cr[cr.Year>=1950]; cr['bin']=pd.cut(cr.e0,np.arange(35,87.5,2.5))
gb=cr.groupby('bin',observed=True).apply(lambda x: pd.Series(dict(e=np.average(x.e0,weights=x.Pop),f=np.average(x.TFR,weights=x.Pop))))
P=dict(zip(g['NAMES'],th)); zz=np.logspace(-4,6,400); mm=1-(1+zz/P['yM'])**(-P['a']); MG=g['MG']
for j,F0_ in enumerate([P['F0A'],P['F0B'],P['F0C']]): a.plot(np.interp(mm,MG,g['tables'](F0_)[2]),P['Finf']+(F0_-P['Finf'])/(1+(zz/P['yF'])**P['b']),color=C[j],lw=2,label='Model, group '+'ABC'[j])
a.plot(gb.e,gb.f,'o',mfc='white',mec=ink,mew=1.2,ms=5.5,label='All countries, 1950–2023',zorder=5)
a.axhline(FREP,color=mut,lw=1,ls=(0,(2,3))); a.text(21,FREP+0.12,'replacement',color=mut,fontsize=9); a.set_xlim(20,87); a.set_ylim(0,8.5); a.set_xlabel('Life expectancy at birth (years)'); a.set_ylabel('Children per woman'); a.legend(frameon=False,loc='lower left',fontsize=9); sty(a,'(a) Fertility against life expectancy')
wt=(ts>=1900)&(ts<=2100)
for a,key,ttl,yl,ylim,loc in ((axs[0,1],1,'(b) Children per woman','Children per woman',(0,8.5),'upper right'),(axs[1,0],2,'(c) Life expectancy at birth','Years',(20,90),'lower right')):
    for j in range(3): a.plot(ts[wt],o[wt,j,key],color=C[j],lw=2,label=GL[j]); a.plot(tr,D[j]['TFR' if key==1 else 'e0'],'o',mfc='white',mec=C[j],mew=1.4,ms=5,zorder=5)
    a.plot([],[],'o',mfc='white',mec=ink,mew=1.2,ms=5,label='Observed')
    if key==1: a.axhline(FREP,color=mut,lw=1,ls=(0,(2,3)))
    a.set_xlim(1900,2100); a.set_ylim(*ylim); a.set_xlabel('Year'); a.set_ylabel(yl); a.legend(frameon=False,loc=loc,fontsize=9); sty(a,ttl)
a=axs[1,1]; aw=pd.read_csv(DER+'world_age.csv').set_index('Year'); yo=np.arange(1950,2024,5)
a.plot(ts[wt],100*(Lw/Nw)[wt],color=C[0],lw=2,label='Ages 15–64, model'); a.plot(yo,100*aw.work[yo],'o',mfc='white',mec=C[0],mew=1.4,ms=5,label='Ages 15–64, observed',zorder=5)
a.plot(ts[wt],100*(Ow/Nw)[wt],color=C[1],lw=2,label='Ages 65 and over, model'); a.plot(yo,100*aw.old[yo],'s',mfc='white',mec=C[1],mew=1.4,ms=5,label='Ages 65 and over, observed',zorder=5)
a.set_xlim(1900,2100); a.set_ylim(0,80); a.set_xlabel('Year'); a.set_ylabel('Share of world population (%)'); a.legend(frameon=False,loc='center left',fontsize=9); sty(a,'(d) Age structure (not fitted)')
fig.tight_layout(); fig.savefig(FIG+'fig2_transition.png',facecolor='white'); plt.close(fig)
# ---------- Fig 3 ----------
fig,axs=plt.subplots(1,3,figsize=(16.5,5.4),dpi=170)
a=axs[0]; w3=(ts>=1900)&(ts<=2300); un=pd.read_csv(DER+'un_proj.csv').set_index('Year')
a.plot(ts[w3],Nw[w3],color=ink,lw=2.2,label='World, this work')
for j in range(3): a.plot(ts[w3],o[w3,j,0],color=C[j],lw=1.8,label=GL[j])
yo=np.arange(1900,2024,10); a.plot(yo,W[yo].values,'o',mfc='white',mec=ink,mew=1.2,ms=4.5,label='World, observed',zorder=5)
yu=np.arange(2030,2101,10); a.plot(yu,un.World[yu],'^',mfc='white',mec=ink,mew=1.2,ms=6,label='World, UN medium projection',zorder=5)
a.axvline(2026.87,color=mut,lw=1,ls=(0,(2,3))); a.text(2022,11.1,'13 Nov 2026',color=mut,fontsize=9,ha='right')
a.set_xlim(1900,2300); a.set_ylim(0,11.8); a.set_xlabel('Year'); a.set_ylabel('Population (billions)'); a.legend(frameon=False,loc='upper right',fontsize=9); sty(a,'(a) Population')
a=axs[1]; cb=Z['c_baseline']; cc=Z['c_research_share_catches_up']; cd=Z['c_delta_0p50']; t=cb[0]; w=t<=2300
a.plot(t[w],cb[3][w],color=C[0],lw=2.2,label='World output'); a.plot(t[w],cc[3][w],color=C[0],lw=1.6,ls=(0,(5,3)),label='World output, research share rising')
a.plot(t[w],cb[2][w],color=C[1],lw=2.2,label='Income per person'); a.plot(t[w],cd[2][w],color=C[1],lw=1.6,ls=(0,(5,3)),label='Income per person, upkeep 0.5% a year')
yd=RES['econ']['baseline']['Y_peak_year']; a.axvline(yd,color=mut,lw=1,ls=(0,(2,3))); a.text(yd+4,0.12,'30 Dec 2069',color=mut,fontsize=9)
a.axhline(1,color=mut,lw=0.8); a.set_xlim(2025,2300); a.set_ylim(0,3.0); a.set_xlabel('Year'); a.set_ylabel('Index, 2025 = 1'); a.legend(frameon=False,loc='upper right',fontsize=9); sty(a,'(b) Output and income')
a=axs[2]; lt=np.load(RESDIR+'long_traj.npy'); w=(ts>=0)&(ts<=4600)&(Nw>0)
a.plot(ts[w],Nw[w]*1e9,color=ink,lw=2.2,label='This work'); wl=(lt[:,0]>=2025)&(lt[:,0]<=4600)&(lt[:,1]>0); a.plot(lt[wl,0],lt[wl,1]*1e9,color=C[2],lw=1.8,label='Ageing delayed 50 years')
tp=np.array([t_ for t_ in tN if t_>=0]); a.plot(tp,W[tp].values*1e9,'o',mfc='white',mec=ink,mew=1.0,ms=3.5,label='Observed',zorder=5)
yl_=RES['demog']['last']; a.plot([yl_],[1],'o',color=ink,ms=6,zorder=6); a.annotate('one person:\n26 March 4348',(yl_,1),xytext=(yl_-1250,30),fontsize=9.5,color=ink,arrowprops=dict(arrowstyle='-',color=mut,lw=0.8))
a.set_yscale('log'); a.set_ylim(0.5,3e10); a.set_xlim(0,4600); a.set_yticks([1,1e3,1e6,1e9]); a.set_yticklabels(['1','1 thousand','1 million','1 billion']); a.set_xlabel('Year'); a.set_ylabel('Population'); a.legend(frameon=False,loc='upper right',fontsize=9); sty(a,'(c) The long run')
fig.tight_layout(); fig.savefig(FIG+'fig3_doomsday.png',facecolor='white'); plt.close(fig)
# extra numbers
cm=Z['c_machines_growing_3p5/yr_from_0p01'] if 'c_machines_growing_3p5/yr_from_0p01' in Z.files else None
for k in Z.files:
    if 'machines_growing' in k:
        c=Z[k]; t=c[0]; Y=c[3]; i0=np.argmax(Y[t<2150]); i1=i0+np.argmin(Y[i0:]); irec=np.where((t>t[i1])&(Y>Y[i0]))[0]; print(k,"local peak %.1f (%.2fx), trough %.1f (%.2fx), regains peak %s"%(t[i0],Y[i0],t[i1],Y[i1],t[irec[0]] if len(irec) else 'never by 2800'))
print("income plateau: ypc 2300 baseline %.2f; output 2100 %.2f 2200 %.2f"%(np.interp(2300,cb[0],cb[2]),np.interp(2100,cb[0],cb[3]),np.interp(2200,cb[0],cb[3])))
print("world 65+ share 2100 %.3f work %.3f; 2025 work %.3f"%(np.interp(2100,ts,Ow/Nw),np.interp(2100,ts,Lw/Nw),np.interp(2025,ts,Lw/Nw)))
