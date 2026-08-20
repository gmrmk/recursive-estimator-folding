"""
S9 core: bias-free ReLU MLP, exact forward+gradient, and the Crofton kink-transect
estimator for E[f(X)], X ~ N(0, I_d).

Identity being verified (derivation in S9_VERDICT.md):
  (Euler)   f(x) = x . grad f(x)                      exact a.e. (f is 1-homogeneous)
  (Stein)   E[X_i g(X)] = E[d g / d X_i]              Gaussian IBP
  =>        E[f(X)] = E[X . grad f(X)] = E[Laplacian f]  (distributional)
  and the distributional Laplacian of a piecewise-linear f is a surface measure on
  the kink set, giving the Crofton/transect form.

All synthetic, self-generated nets. No external reads.
"""
import numpy as np

SQRT2PI = np.sqrt(2.0 * np.pi)


def phi1(t):
    """Standard normal pdf."""
    return np.exp(-0.5 * t * t) / SQRT2PI


def make_net(d, width, depth, rng, dtype=np.float64):
    """Bias-free ReLU MLP, He init. depth = number of weight layers L.
    W[0]: (width, d); W[1..L-2]: (width, width); W[L-1]: (1, width) scalar output.
    """
    Ws = []
    fan_in = d
    for l in range(depth):
        out = 1 if l == depth - 1 else width
        W = rng.standard_normal((out, fan_in)).astype(dtype) * np.sqrt(2.0 / fan_in)
        Ws.append(W)
        fan_in = out
    return Ws


def forward_grad(Ws, X):
    """Batched forward + exact input gradient.
    X: (N, d).  Returns f: (N,), grad: (N, d).
    grad f(x) = W_1^T D_1 W_2^T D_2 ... W_{L-1}^T D_{L-1} W_L^T restricted to x's mask.
    """
    L = len(Ws)
    h = X
    masks = []
    for l in range(L):
        pre = h @ Ws[l].T  # (N, out)
        if l < L - 1:
            s = (pre > 0.0).astype(X.dtype)
            masks.append(s)
            h = pre * s
        else:
            f = pre[:, 0]
    # backward: seed df/dh_{L-1} = W_L (row), broadcast over batch
    delta = np.broadcast_to(Ws[-1], (X.shape[0], Ws[-1].shape[1])).copy()
    for l in range(L - 2, -1, -1):
        delta = (delta * masks[l]) @ Ws[l]
    return f, delta


def forward_only(Ws, X):
    L = len(Ws)
    h = X
    for l in range(L):
        pre = h @ Ws[l].T
        if l < L - 1:
            h = pre * (pre > 0.0)
        else:
            return pre[:, 0]


def _affine(Ws, masks, base, v):
    """Under fixed hidden masks, every pre-activation is affine in t along x=base+t v.
    Returns (cs, ds, beta) where cs[l], ds[l] are (value, slope) coeffs of hidden
    layer l's pre-activation vector, and beta is the scalar output slope df/dt.
    """
    L = len(Ws)
    hc = base
    hd = v
    cs = []
    ds = []
    for l in range(L - 1):
        pc = Ws[l] @ hc
        pd = Ws[l] @ hd
        cs.append(pc)
        ds.append(pd)
        hc = masks[l] * pc
        hd = masks[l] * pd
    beta = float((Ws[-1] @ hd)[0])  # output slope df/dt
    return cs, ds, beta


def transect_line(Ws, base, v, T=8.0, eps=1e-12):
    """Event-driven sweep of the line x(t) = base + t v, t in [-T, T].
    Finds every kink crossing exactly, records the jump in output slope and the
    Gaussian density phi1(t) at each crossing, tagged by which layer flipped.

    Returns:
      total     = sum_k Dbeta_k * phi1(t_k)        (line contribution, BEFORE x d factor)
      per_layer = array length (L-1) of the same sum split by flipping layer.
      n_events  = number of kink crossings found on the line (for FLOP accounting).
    The unbiased estimator of E[f] is  d * mean_over_lines(total).
    """
    L = len(Ws)
    hidden = L - 1
    # initial masks at t = -T
    x0 = base + (-T) * v
    masks = []
    hh = x0
    for l in range(L):
        pre = Ws[l] @ hh
        if l < L - 1:
            s = (pre > 0.0).astype(np.float64)
            masks.append(s)
            hh = pre * s
    t_cur = -T
    total = 0.0
    n_events = 0
    per_layer = np.zeros(hidden)
    # output slope under current masks
    _, _, beta_prev = _affine(Ws, masks, base, v)
    while True:
        cs, ds, beta_here = _affine(Ws, masks, base, v)
        # candidate crossings for all hidden units
        best_t = np.inf
        best_l = -1
        best_i = -1
        for l in range(hidden):
            c = cs[l]
            dd = ds[l]
            # crossing time -c/dd where dd != 0
            with np.errstate(divide="ignore", invalid="ignore"):
                tstar = -c / dd
            valid = (np.abs(dd) > 0) & (tstar > t_cur + eps)
            if np.any(valid):
                idx = np.where(valid)[0]
                tv = tstar[idx]
                j = np.argmin(tv)
                if tv[j] < best_t:
                    best_t = tv[j]
                    best_l = l
                    best_i = idx[j]
        if not np.isfinite(best_t) or best_t > T:
            break
        # flip the unit, recompute output slope after
        masks[best_l][best_i] = 1.0 - masks[best_l][best_i]
        _, _, beta_after = _affine(Ws, masks, base, v)
        dbeta = beta_after - beta_prev
        w = dbeta * phi1(best_t)
        total += w
        per_layer[best_l] += w
        n_events += 1
        beta_prev = beta_after
        t_cur = best_t
    return total, per_layer, n_events


def sample_line(d, rng):
    """Sample (base, v): v uniform on sphere, base = perpendicular Gaussian offset."""
    g = rng.standard_normal(d)
    v = g / np.linalg.norm(g)
    p = rng.standard_normal(d)
    base = p - (v @ p) * v
    return base, v


if __name__ == "__main__":
    # quick self-test: Euler exactness + transect unbiasedness on a tiny net
    rng = np.random.default_rng(0)
    d, width, depth = 8, 12, 3
    Ws = make_net(d, width, depth, rng)
    X = rng.standard_normal((200000, d))
    f, g = forward_grad(Ws, X)
    euler = (X * g).sum(1)
    print("max |x.gradf - f| =", np.max(np.abs(euler - f)))
    print("MC E[f]      =", f.mean(), "+/-", f.std() / np.sqrt(len(f)))
    # transect
    n_lines = 20000
    vals = np.empty(n_lines)
    for k in range(n_lines):
        base, v = sample_line(d, rng)
        tot, _, _ = transect_line(Ws, base, v)
        vals[k] = d * tot
    print("transect E[f]=", vals.mean(), "+/-", vals.std() / np.sqrt(n_lines))
