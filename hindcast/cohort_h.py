"""Three-group cohort model fitted only on data up to a cutoff year C (hindcast).
Model equations are copied unchanged from src/model5.py; only the data section differs.
Rules: hindcast/PREREGISTRATION.md.   Usage: CUTOFF=1990 python3 cohort_h.py <seed>"""
import os, sys, json, time, numpy as np, pandas as pd, warnings
from scipy.optimize import least_squares, brentq, differential_evolution
warnings.filterwarnings('ignore')
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); RAW=ROOT+'/data/raw/'; RESDIR=ROOT+'/results/'
C=int(os.environ['CUTOFF'])
A_=110; LIM_SHIFT=0; WORK_HI=13; DMAX=0.003; ALT_SHIFT=0; ALT_T0=2030; ALT_DT=50; ALT_WORK=False
ages=np.arange(A_)
def siler(a1,b1,a2,a3,b3): return a1*np.exp(-b1*ages)+a2+a3*np.exp(b3*ages)
LP0=np.log(siler(0.28,0.45,0.007,0.0004,0.072)); LM=np.log(0.003*np.exp(-1.0*ages)+0.0001+1.0e-5*np.exp(0.105*np.maximum(ages-LIM_SHIFT,0)))
G=A_//5; gmid=5*np.arange(G)+2.5
_b=pd.read_csv(RAW+'births-by-age-of-mother.csv'); _b=_b[_b.Entity=='World'].set_index('Year').iloc[:,2:].loc[1950:C]
phi=np.zeros(G); phi[2:11]=_b.sum().values[::-1]/_b.sum().values.sum()   # world births by mother's age, 1950 to cutoff only
def tab(lp,m):
    mu=np.exp((1-m)*lp+m*LM); cum=np.concatenate([[0],np.cumsum(mu)[:-1]]); Lmid=np.exp(-cum-mu/2)
    surv=np.zeros(G); surv[:-1]=Lmid[7::5][:G-1]/Lmid[2::5][:G-1]; return surv,Lmid[:5].mean(),Lmid.sum()
def nrr(lp,m):
    surv,sb,_=tab(lp,m); return 0.5*np.dot(phi,sb*np.concatenate([[1.0],np.cumprod(surv[:-1])]))
FREP=1/nrr(LP0,1.0); MG=np.linspace(0,1,201)
def _lmid(m):
    mu=np.exp((1-m)*LP0+m*LM); cum=np.concatenate([[0],np.cumsum(mu)[:-1]]); return np.exp(-cum-mu/2)
LMID0=np.array([_lmid(m) for m in MG])
LM_STD=LM
if ALT_SHIFT:
    LM=np.log(0.003*np.exp(-1.0*ages)+0.0001+1.0e-5*np.exp(0.105*np.maximum(ages-ALT_SHIFT,0))); LMID_ALT=np.array([_lmid(m) for m in MG]); LM=LM_STD                       # (201,110); scaling premodern hazard by e^c => Lmid^(e^(c(1-m)))
def _from_lmid(Lm):
    surv=np.zeros((Lm.shape[0],G)); den=Lm[:,2::5][:,:G-1]; surv[:,:-1]=np.divide(Lm[:,7::5][:,:G-1],den,out=np.zeros_like(den),where=den>1e-250); return surv,Lm[:,:5].mean(1),Lm.sum(1)
def _nrr0(c):
    surv,sb,_=_from_lmid(LMID0[:1]**np.exp(c)); return 0.5*np.dot(phi,sb[0]*np.concatenate([[1.0],np.cumprod(surv[0][:-1])]))
def tables(F0,base=None):
    c=brentq(lambda lc: F0*_nrr0(lc)-1,-3,3,xtol=1e-10); return _from_lmid((LMID0 if base is None else base)**np.exp(c*(1-MG))[:,None])
NAMES=['g','beta','a','yM','yF','b','Finf','F0A','d','sB','sC','N0A','N0B','N0C','F0B','F0C']; J=3; T_START=-300
def run(th,t_end=2025,dt=5):
    g,beta,a,yM,yF,b,Finf,F0A,d,sB,sC,N0A,N0B,N0C,F0B,F0C=th
    F0=np.array([F0A,F0B,F0C]); tb=[tables(f) for f in F0]; SURV=np.array([t[0] for t in tb]); SB=np.array([t[1] for t in tb]); E0T=np.array([t[2] for t in tb])
    s=np.array([1.0,sB,sC]); N0=np.array([N0A,N0B,N0C]); jj=np.arange(J)
    if ALT_SHIFT: tb2=[tables(f,LMID_ALT) for f in F0]; SURV2=np.array([t[0] for t in tb2]); SB2=np.array([t[1] for t in tb2]); E0T2=np.array([t[2] for t in tb2])
    L=SB[:,0,None]*np.concatenate([np.ones((J,1)),np.cumprod(SURV[:,0,:-1],axis=1)],axis=1); n=N0[:,None]*L/L.sum(1,keepdims=True); T=N0.copy()
    ts=np.arange(T_START,t_end+1,dt); out=np.empty((len(ts),J,6))
    for i,tt in enumerate(ts):
        N=n.sum(1); Nw=N.sum(); z=np.maximum(T/np.maximum(N,1e-300)-1,0.0)
        m=1-(1+z/yM)**(-a); F=Finf+(F0-Finf)/(1+(z/yF)**b)
        u=m*200; k=np.minimum(u.astype(int),199); w=(u-k)[:,None]
        surv=SURV[jj,k]*(1-w)+SURV[jj,k+1]*w; sb=SB[jj,k]*(1-w[:,0])+SB[jj,k+1]*w[:,0]; e0=E0T[jj,k]*(1-w[:,0])+E0T[jj,k+1]*w[:,0]
        w2=0.0
        if ALT_SHIFT and tt>ALT_T0:
            w2=min((tt-ALT_T0)/ALT_DT,1.0); surv=(1-w2)*surv+w2*(SURV2[jj,k]*(1-w)+SURV2[jj,k+1]*w); sb=(1-w2)*sb+w2*(SB2[jj,k]*(1-w[:,0])+SB2[jj,k+1]*w[:,0]); e0=(1-w2)*e0+w2*(E0T2[jj,k]*(1-w[:,0])+E0T2[jj,k+1]*w[:,0])
        x=np.exp(-d*dt) if 1915<=tt<1950 else 1.0
        births=0.5*F*(n@phi); nn=np.empty_like(n); nn[:,0]=births*sb*x; nn[:,1:]=n[:,:-1]*surv[:,:-1]*x
        out[i,:,0]=N; out[i,:,1]=F; out[i,:,2]=e0; out[i,:,3]=births/dt; out[i,:,4]=n[:,3:13].sum(1)+(w2*n[:,13:23].sum(1) if ALT_WORK else 0.0); out[i,:,5]=n[:,13:].sum(1)
        n=nn; T=T*np.exp(np.minimum(s*g*Nw**beta*dt,50.0))
    return ts,out
# ---------------- data, restricted to years <= C for fitting ----------------
pop=pd.read_csv(RAW+'population.csv'); tfr=pd.read_csv(RAW+'children-born-per-woman.csv'); e0d=pd.read_csv(RAW+'life-expectancy.csv')
tfr.columns=['Entity','Code','Year','TFR']; e0d.columns=['Entity','Code','Year','e0']; pop.columns=['Entity','Code','Year','Pop']
ok=lambda d: d[d.Code.notna() & ~d.Code.astype(str).str.startswith('OWID_') & ~d.Entity.str.contains('(UN)',regex=False) & (d.Code.astype(str).str.len()==3)]
P=ok(pop); T=ok(tfr); E=ok(e0d)
Wraw=pop[pop.Entity=='World'].set_index('Year').Pop; W=Wraw/1e9
EW=e0d[e0d.Entity=='World'].set_index('Year').e0; TW=tfr[tfr.Entity=='World'].set_index('Year').TFR
# grouping from pre-cutoff data only: mean TFR over the five years ending at C
tc=T[(T.Year>=C-4)&(T.Year<=C)].groupby('Entity').TFR.mean()
grp={c:('A' if v<3 else ('B' if v<5 else 'C')) for c,v in tc.items()}
P=P.assign(g=P.Entity.map(grp))
d=P.dropna(subset=['g']).merge(T,on=['Entity','Code','Year'],how='left').merge(E,on=['Entity','Code','Year'],how='left')
rows=[]
for (g_,y_),x in d.groupby(['g','Year']):
    r=dict(g=g_,Year=y_,Pop=float(x.Pop.sum()))
    for c in ('TFR','e0'):
        v=x.dropna(subset=[c]); r[c]=np.average(v[c],weights=v.Pop) if v.Pop.sum()>0.97*x.Pop.sum() else np.nan
    rows.append(r)
R=pd.DataFrame(rows); R=R[R.Year.isin(Wraw.index)]
tot=R.groupby('Year').Pop.sum(); R['Pop']=[float(p)*float(Wraw[int(y)])/float(tot[y])/1e9 for p,y in zip(R.Pop,R.Year)]
GRID=np.array(list(range(0,1700,100))+list(range(1700,1950,10))+list(range(1950,2024,5)))
tN=GRID[GRID<=C]; tr=np.arange(1950,C+1,5); tEw=np.array([1770,1800,1820,1850,1870,1900,1913])
sm=lambda S,y,hi=None: S.loc[max(y-2,1950):min(y+2,C if hi is None else hi)].mean()
D={}
for j,gname in enumerate('ABC'):
    x=R[R.g==gname].set_index('Year'); D[j]=dict(N=x.Pop[tN].values,am=np.log(x.Pop[tr].values[1:]/x.Pop[tr].values[:-1])/np.diff(tr),TFR=np.array([sm(x.TFR,y) for y in tr]),e0=np.array([sm(x.e0,y) for y in tr]))
sigN=np.where(tN<1500,0.30,np.where(tN<1950,0.08,0.02)); sigW=np.where(tN<1500,0.15,0.05); pre=tN<1950
def pieces(th):
    ts,o=run(th,t_end=C); lN=np.log(np.maximum(o[:,:,0],1e-300)); r={}
    for j in range(J):
        a=np.interp(tr,ts,lN[:,j])
        r[j]=dict(N=np.interp(tN,ts,lN[:,j])-np.log(D[j]['N']),rate=np.diff(a)/np.diff(tr)-D[j]['am'],TFR=np.interp(tr,ts,o[:,j,1])/D[j]['TFR']-1,e0=np.interp(tr,ts,o[:,j,2])/D[j]['e0']-1)
    Nw=o[:,:,0].sum(1); ew=(o[:,:,0]*o[:,:,2]).sum(1)/Nw
    r['w']=dict(N=np.interp(tN[pre],ts,np.log(Nw))-np.log(W[tN[pre]].values),e0=np.interp(tEw,ts,ew)/EW[tEw].values-1)
    return ts,o,r
NRES=3*(len(tN)+3*len(tr)-1)+pre.sum()+len(tEw)
def resid(th):
    try: ts,o,r=pieces(th)
    except Exception: return np.full(NRES,30.0)
    v=np.concatenate([np.concatenate([r[j]['N']/sigN,r[j]['rate']/0.0015,r[j]['TFR']/0.05,r[j]['e0']/0.04]) for j in range(J)]+[r['w']['N']/sigW[pre],r['w']['e0']/0.04])
    v[~np.isfinite(v)]=30.0; return np.clip(v,-30,30)
#            g     beta a    yM    yF   b   Finf F0A d    sB  sC  N0A   N0B   N0C   F0B F0C
LO=np.array([5e-4,0.5,0.02,0.005,0.02,0.4,0.6,3.5,0.0, 0.2,0.2,0.001,0.001,0.001,3.5,3.5])
HI=np.array([0.03,4.0,5,   30,   30,  8,  2.6,8.5,DMAX,2.0,2.0,0.3,  0.3,  0.3,  8.5,8.5])
XS=np.array([0.005,1,0.3,0.1,1,1,1,3,0.003,0.5,0.5,0.03,0.1,0.02,3,3])
def forecast(th):
    """Model values for the scoring targets, and what the fit implies beyond."""
    ts,o=run(th,t_end=2300); N=o[:,:,0].sum(1); lN=np.log(N); F=o[:,:,3].sum(1)/(o[:,:,3]/o[:,:,1]).sum(1); old=o[:,:,5].sum(1)/N
    n23=float(np.exp(np.interp(2023,ts,lN))); n15=float(np.exp(np.interp(2015,ts,lN))); w=ts>=C; ip=np.argmax(N[w])
    return dict(N2023=n23,g=float(np.log(n23/n15)/8),TFR2023=float(np.interp(2023,ts,F)),old2023=float(np.interp(2023,ts,old)),
                peak=float(N[w][ip]),peak_year=int(ts[w][ip]),N2100=float(N[ts==2100][0]),groupN2023=[float(np.exp(np.interp(2023,ts,lN_))) for lN_ in np.log(o[:,:,0]).T],
                groupTFR2023=[float(np.interp(2023,ts,o[:,j,1])) for j in range(J)])
if __name__=="__main__":
    seed=int(sys.argv[1]); logp=[0,3,4,11,12,13]
    def trf(x):
        th=np.array(x,float); th[logp]=np.exp(th[logp]); return th
    def cost(x):
        r=resid(trf(x)); return np.sum(np.log1p(r*r/9))
    b=[(np.log(LO[i]),np.log(HI[i])) if i in logp else (LO[i],HI[i]) for i in range(len(LO))]
    t0=time.time()
    de=differential_evolution(cost,b,popsize=8,maxiter=200,tol=1e-8,seed=seed,polish=False,mutation=(0.4,1.0),recombination=0.8)
    r=least_squares(resid,np.clip(trf(de.x),LO,HI),bounds=(LO,HI),x_scale=XS); r=least_squares(resid,r.x,bounds=(LO,HI),x_scale=XS)
    gs={g_:dict(n=int(sum(1 for v in grp.values() if v==g_)),pop_cutoff=float(R[(R.g==g_)&(R.Year==C)].Pop.sum()),pop_2023=float(R[(R.g==g_)&(R.Year==2023)].Pop.sum()),
                TFR_cutoff=float(R[(R.g==g_)&(R.Year==C)].TFR.iloc[0]),TFR_2023=float(R[(R.g==g_)&(R.Year==2023)].TFR.iloc[0])) for g_ in 'ABC'}
    out=dict(cutoff=C,seed=seed,chi2=float(2*r.cost),n=int(len(r.fun)),seconds=time.time()-t0,th=dict(zip(NAMES,map(float,r.x))),
             at_bound=[n_ for n_,v,l,h in zip(NAMES,r.x,LO,HI) if min(v-l,h-v)<1e-6*max(1,abs(v))],groups=gs,forecast=forecast(r.x))
    json.dump(out,open(RESDIR+'hindcast_cohort_%d_seed%d.json'%(C,seed),'w'),indent=1)
    print(json.dumps(out)[:600])
