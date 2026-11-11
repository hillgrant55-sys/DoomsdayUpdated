import sys,json,numpy as np
src=open('/home/claude/work/model5.py').read().split('if __name__=="__main__":')[0]
th=np.array(json.load(open('/home/claude/work/best5_d0.003.json'))['th'])
g={'__name__':'m'}; exec(src,g); r=g['resid'](th); print("base chi2 %.1f"%(r@r)); ts,o=g['run'](th,t_end=2300); print(o[ts==2100,:,0].sum(), (o[ts==2023,:,4].sum()/o[ts==2023,:,0].sum()))
g2={'__name__':'m'}; exec(src.replace("A_=110;","A_=165;"),g2); r=g2['resid'](th); print("A_=165 chi2 %.1f"%(r@r))
g3={'__name__':'m'}; exec(src.replace("A_=110;","A_=165;").replace("ALT_SHIFT=0","ALT_SHIFT=50"),g3); ts,o=g3['run'](th,t_end=2300); print("longevity: N2100 %.2f N2200 %.2f e0 2100"%(o[ts==2100,:,0].sum(),o[ts==2200,:,0].sum()),o[ts==2100,:,2])
