import numpy as np, time
from s9_core import make_net, forward_grad, forward_only, transect_line, sample_line

rng = np.random.default_rng(1)
# Stage A MC+grad timing
d, width, depth = 16, 16, 4
Ws = make_net(d, width, depth, rng)
chunk = 500000
t0=time.time()
X = rng.standard_normal((chunk, d))
f,g = forward_grad(Ws, X)
print("fwd+grad %d samples: %.2fs, max|x.gradf-f|=%.2e"%(chunk, time.time()-t0, np.max(np.abs((X*g).sum(1)-f))))
t0=time.time()
X = rng.standard_normal((chunk, d)); f=forward_only(Ws,X)
print("fwd-only %d samples: %.3fs"%(chunk, time.time()-t0))

# Stage B net: event counts + transect timing
d,width,depth = 64,64,8
Ws = make_net(d,width,depth,rng)
n=300
t0=time.time(); evs=[]; vals=np.empty(n)
for k in range(n):
    base,v=sample_line(d,rng)
    tot,pl,ne=transect_line(Ws,base,v)
    vals[k]=d*tot; evs.append(ne)
dt=time.time()-t0
evs=np.array(evs)
print("StageB net: %.2f ms/line, mean_events=%.1f (min %d max %d)"%(1000*dt/n, evs.mean(), evs.min(), evs.max()))
print("StageB transect single-line: mean=%.4f std=%.4f"%(vals.mean(), vals.std()))
# MC var on stageB net
X=rng.standard_normal((500000,d)); f=forward_only(Ws,X)
print("StageB MC E[f]=%.4f  Var[f]=%.5f"%(f.mean(), f.var()))
