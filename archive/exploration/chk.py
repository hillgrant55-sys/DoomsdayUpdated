import sys,numpy as np
src=open('/home/claude/work/model.py').read().split('if __name__=="__main__" and')[0]
for p in [(0.25,0.5,0.0105,0.0006,0.070),(0.25,0.45,0.008,0.0005,0.070),(0.28,0.45,0.007,0.0004,0.072),(0.30,0.45,0.006,0.0004,0.072),(0.30,0.4,0.005,0.0003,0.075)]:
    g={}; exec(src.replace("siler(0.30,1.0,0.0105,0.0006,0.070)","siler%s"%(p,)),g)
    Lm=g['table'](0)[2]; print(p,"e0 pre %.1f F0 %.2f  survive to 5: %.2f to 15: %.2f"%(g['E0T'][100],g['F0'],Lm[5],Lm[15]))
