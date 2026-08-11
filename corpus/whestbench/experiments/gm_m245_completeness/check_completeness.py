"""M245 open item: is the span {v_q} complete, or is something orthogonal to it?

The audit filed this as OPEN:

    Completeness: OPEN. Finite SPD proves linear independence, not L^2 closure.
    The density of the non-orthogonal span {v_0, v_1, ...} over the half-normal
    measure requires an explicit weighted-polynomial approximation proof (e.g.
    verifying Carleman's condition). Parseval's identity cannot currently be
    globally invoked.

    Cheapest falsifier: Construct an explicit, non-zero piecewise function
    orthogonal to every v_q under the half-normal measure T >= 0. If found,
    global density fails.

This converts that analytic question into a finite computation. Basis, verbatim
from M245_PREDECLARATION_20260810.md section 3:

    r(g)    = (relu(mu_i + sigma_i g) - m_i)^2
    rbar(g) = r(g)/sigma_i^2 = (relu(alpha + g) - mbar)^2
    S[f](t) = 0.5 (f(t) + f(-t))
    u_q(t)  = S[rbar h_q](t)
    R_q     = E_T[u_q(T)]
    v_q(t)  = u_q(t) - R_q
    G_Q[m,q]= E_T[v_m v_q],  density 2 phi(t) on [0, inf)

with alpha = mu_i/sigma_i and, by the ReLU mean identity,
mbar = m_i/sigma_i = alpha Phi(alpha) + phi(alpha).

## Method, and why it is not mp.quad(error=True)

A companion result in this corpus (gm_mpquad_error_contract) measured that
mp.quad's error heuristic can report an arbitrarily small number on a completely
wrong value, and that its magnitude does not rank correctness -- so it may not
gate anything. It also measured that a panel edge placed ON a feature is
correct at every width tested, while an arbitrary panel edge converted a correct
answer into a silent miss.

Both lessons are applied here: every integral is split at the mandatory kink
t = |alpha| and evaluated by FIXED-ORDER Gauss-Legendre on explicit panels (a
deterministic node set, no adaptive stopping rule, no heuristic), and each Gram
matrix is recomputed at two different node counts. Agreement between the two is
the acceptance criterion; no reported error estimate is consulted.
"""

from __future__ import annotations

import argparse

import mpmath as mp

QMAX_DEFAULT = 8


def setup(alpha):
    alpha = mp.mpf(alpha)
    phi = lambda z: mp.e ** (-z * z / 2) / mp.sqrt(2 * mp.pi)
    Phi = lambda z: (1 + mp.erf(z / mp.sqrt(2))) / 2
    mbar = alpha * Phi(alpha) + phi(alpha)
    return alpha, mbar, phi


def hermites(g, qmax):
    """Orthonormal probabilists' Hermites via the frozen recurrence."""
    h = [mp.mpf(1), g]
    for q in range(1, qmax):
        h.append((g * h[q] - mp.sqrt(q) * h[q - 1]) / mp.sqrt(q + 1))
    return h[: qmax + 1]


def make_basis(alpha, mbar, qmax):
    def rbar(g):
        return (max(alpha + g, mp.mpf(0)) - mbar) ** 2

    def u(q, t):
        hp = hermites(t, qmax)
        hm = hermites(-t, qmax)
        return (rbar(t) * hp[q] + rbar(-t) * hm[q]) / 2

    return u


def gl_nodes(n):
    """Fixed-order Gauss-Legendre nodes/weights on [-1,1] at working precision."""
    nodes = []
    for k in range(1, n + 1):
        x = mp.cos(mp.pi * (k - mp.mpf(1) / 4) / (n + mp.mpf(1) / 2))
        for _ in range(80):
            p0, p1 = mp.mpf(1), mp.mpf(0)
            for j in range(1, n + 1):
                p1, p0 = p0, ((2 * j - 1) * x * p0 - (j - 1) * p1) / j
            dp = n * (x * p0 - p1) / (x * x - 1)
            dx = -p0 / dp
            x += dx
            if abs(dx) < mp.mpf(10) ** (-(mp.mp.dps - 5)):
                break
        p0, p1 = mp.mpf(1), mp.mpf(0)
        for j in range(1, n + 1):
            p1, p0 = p0, ((2 * j - 1) * x * p0 - (j - 1) * p1) / j
        dp = n * (x * p0 - p1) / (x * x - 1)
        nodes.append((x, 2 / ((1 - x * x) * dp * dp)))
    return nodes


def integrator(alpha, tmax, order):
    """E_T[f] = int_0^inf f(t) 2 phi(t) dt, on panels split at the kink."""
    edges = [mp.mpf(0)]
    k = abs(alpha)
    if 0 < k < tmax:
        edges.append(k)
    step = (tmax - edges[-1]) / 6
    edges += [edges[-1] + step * i for i in range(1, 7)]
    base = gl_nodes(order)
    pts = []
    for a, b in zip(edges, edges[1:]):
        half, mid = (b - a) / 2, (a + b) / 2
        for x, w in base:
            t = mid + half * x
            pts.append((t, w * half * 2 * mp.e ** (-t * t / 2) / mp.sqrt(2 * mp.pi)))

    def E(f):
        return mp.fsum(wt * f(t) for t, wt in pts)

    return E


def build(alpha, qmax, order, tmax):
    alpha, mbar, _ = setup(alpha)
    u = make_basis(alpha, mbar, qmax)
    E = integrator(alpha, mp.mpf(tmax), order)
    R = [E(lambda t, q=q: u(q, t)) for q in range(qmax + 1)]
    v = [(lambda t, q=q: u(q, t) - R[q]) for q in range(qmax + 1)]
    G = mp.matrix(qmax + 1, qmax + 1)
    for m in range(qmax + 1):
        for q in range(m, qmax + 1):
            val = E(lambda t, m=m, q=q: v[m](t) * v[q](t))
            G[m, q] = val
            G[q, m] = val
    return alpha, mbar, E, v, G


def residual(E, v, G, w, Q):
    """Relative residual of projecting centered w onto span{v_0..v_Q}."""
    wbar = E(w)
    wc = lambda t: w(t) - wbar
    nrm = E(lambda t: wc(t) ** 2)
    if nrm <= 0:
        return mp.mpf(1)
    d = mp.matrix(Q + 1, 1)
    for q in range(Q + 1):
        d[q] = E(lambda t, q=q: v[q](t) * wc(t))
    A = mp.matrix(Q + 1, Q + 1)
    for m in range(Q + 1):
        for q in range(Q + 1):
            A[m, q] = G[m, q]
    c = mp.lu_solve(A, d)
    explained = mp.fsum(d[q] * c[q] for q in range(Q + 1))
    return (nrm - explained) / nrm


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--alpha", default="0.0")
    ap.add_argument("--qmax", type=int, default=QMAX_DEFAULT)
    ap.add_argument("--dps", type=int, default=60)
    ap.add_argument("--order", type=int, default=60)
    ap.add_argument("--order2", type=int, default=48, help="cross-check order")
    ap.add_argument("--tmax", default="14")
    args = ap.parse_args()

    mp.mp.dps = args.dps
    alpha, mbar, E, v, G = build(args.alpha, args.qmax, args.order, args.tmax)
    print(f"alpha={mp.nstr(alpha,8)}  mbar={mp.nstr(mbar,8)}  "
          f"dps={args.dps}  GL order={args.order}/panel  tmax={args.tmax}")

    # --- cross-engine agreement (replaces any heuristic error estimate) ---
    _, _, E2, v2, G2 = build(args.alpha, args.qmax, args.order2, args.tmax)
    worst = mp.mpf(0)
    for m in range(args.qmax + 1):
        for q in range(args.qmax + 1):
            if G[m, q] != 0:
                worst = max(worst, abs(G2[m, q] - G[m, q]) / abs(G[m, q]))
    print(f"cross-order Gram agreement (order {args.order} vs {args.order2}): "
          f"worst relative diff {mp.nstr(worst, 6)}")
    if worst > mp.mpf(10) ** -20:
        print("  WARNING: quadrature not converged; results below are not admissible")

    # --- conditioning, against the audit's stated ~2.7e5 at alpha=0, Q=4 ---
    print(f"\n{'Q':>3} {'cond(G_Q)':>16}")
    print("-" * 22)
    for Q in range(args.qmax + 1):
        A = mp.matrix(Q + 1, Q + 1)
        for m in range(Q + 1):
            for q in range(Q + 1):
                A[m, q] = G[m, q]
        ev = mp.eigsy(A, eigvals_only=True)
        lo, hi = min(ev), max(ev)
        print(f"{Q:>3} {mp.nstr(hi/lo, 6):>16}"
              + ("   <- audit says ~2.7e5 here" if Q == 4 else ""))

    # --- the falsifier: is anything orthogonal to the whole span? ---
    targets = {
        "degree-1  t": lambda t: t,
        "degree-0.5 sqrt(t)": lambda t: mp.sqrt(t),
        "kink-local |t-|alpha||": lambda t: abs(t - abs(alpha)),
        "bounded  exp(-t)": lambda t: mp.e ** (-t),
        "oscillatory cos(3t)": lambda t: mp.cos(3 * t),
        "control: v_0 itself": lambda t: v[0](t),
    }
    print(f"\nrelative residual after projecting onto span(v_0..v_Q)")
    print(f"{'target':<24}" + "".join(f"{('Q='+str(q)):>12}"
                                      for q in range(args.qmax + 1)))
    print("-" * (24 + 12 * (args.qmax + 1)))
    for name, w in targets.items():
        row = ""
        for Q in range(args.qmax + 1):
            row += f"{mp.nstr(residual(E, v, G, w, Q), 4):>12}"
        print(f"{name:<24}{row}")

    print("\nReading: a residual that decreases toward 0 means the target is being")
    print("captured by the span. A residual that plateaus at a positive value as Q")
    print("grows is an explicit function the span does not reach -- the audit's")
    print("cheapest falsifier for global density.")


if __name__ == "__main__":
    main()
