import numpy as np, time
from s9_core import make_net, forward_only, transect_line, sample_line

rng = np.random.default_rng(3)
d, width = 6, 4
Ws = make_net(d, width, 2, rng)   # depth-1: W[0]:(width,d), W[1]:(1,width)
W0, Wout = Ws[0], Ws[1][0]
exact = np.sum(Wout * np.linalg.norm(W0, axis=1)) / np.sqrt(2 * np.pi)
print("analytic E[f] =", exact)

X = rng.standard_normal((3000000, d))
f = forward_only(Ws, X)
print("MC E[f]       =", f.mean(), "+/-", f.std() / np.sqrt(len(f)))

n = 150000
vals = np.empty(n)
t0 = time.time()
for k in range(n):
    base, v = sample_line(d, rng)
    tot, _, _ = transect_line(Ws, base, v)
    vals[k] = d * tot
se = vals.std() / np.sqrt(n)
print("transect E[f] =", vals.mean(), "+/-", se, " (%.1fs)" % (time.time() - t0))
print("z vs analytic =", (vals.mean() - exact) / se)
