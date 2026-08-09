import numpy as np, time
from s9_core import make_net, transect_line, sample_line
rng = np.random.default_rng(1)
d, width, depth = 16, 16, 4
Ws = make_net(d, width, depth, rng)
# count kinks + time
n=2000
t0=time.time()
nk=0; vals=np.empty(n)
for k in range(n):
    base,v=sample_line(d,rng)
    # instrument: count events by re-running quickly
    tot,pl=transect_line(Ws,base,v)
    vals[k]=d*tot
dt=time.time()-t0
print("%.2f ms/line, mean=%.4f se=%.4f"%(1000*dt/n, vals.mean(), vals.std()/np.sqrt(n)))
