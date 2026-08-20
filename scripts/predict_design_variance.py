"""Predict a spherical design's estimator variance analytically, before building it.

For a bias-free He-initialised ReLU MLP the rotation-averaged two-point function
of the output is exactly an iterated arc-cosine kernel.  Expanding it in
Gegenbauer polynomials gives the per-degree energy of the estimand; pairing that
with a design's per-degree defect gives the variance without touching a network:

    K(c)   = kappa^depth(c),   kappa(c) = (sqrt(1-c^2) + (pi - arccos c) c) / pi
    K(c)   = sum_l  b_l P_l(c)
    A_l    = (1/N^2) sum_{i,j} P_l(<u_i,u_j>)          the design defect
    Var    = sum_{l>=1} b_l A_l

This exists because on 2026-08-12 a design change was proposed, gated, built and
measured before anyone asked what it was worth.  The answer was computable in
advance, and it was half a percent against a 2.33% bar.

Usage:  python scripts/predict_design_variance.py
"""

from __future__ import annotations

from fractions import Fraction as F

import numpy as np

D = 256          # ambient dimension
DEPTH = 32       # network depth
LMAX = 80       # even degrees 2..LMAX; the tail decays slowly and must be resolved


def kappa(c: np.ndarray) -> np.ndarray:
    """One ReLU layer's correlation map, norm-preserving under He init."""
    c = np.clip(c, -1.0, 1.0)
    return (np.sqrt(np.maximum(0.0, 1.0 - c * c)) + (np.pi - np.arccos(c)) * c) / np.pi


def two_point(c: np.ndarray, depth: int = DEPTH) -> np.ndarray:
    for _ in range(depth):
        c = kappa(c)
    return c


def gegenbauer_normalised(lmax: int, c: np.ndarray, d: int = D) -> dict[int, np.ndarray]:
    """P_l with P_l(1) = 1, by the standard three-term recurrence."""
    P = {0: np.ones_like(c), 1: c.copy()}
    for l in range(1, lmax):
        P[l + 1] = ((2 * l + d - 2) * c * P[l] - (l + d - 3) * P[l - 1]) / (l + 1)
    # renormalise so P_l(1) = 1
    one = np.ones(1)
    Q = {0: one, 1: one}
    for l in range(1, lmax):
        Q[l + 1] = ((2 * l + d - 2) * Q[l] - (l + d - 3) * Q[l - 1]) / (l + 1)
    return {l: P[l] / Q[l][0] for l in P}


def expand(depth: int = DEPTH, lmax: int = LMAX, d: int = D, dps: int = 60) -> dict[int, float]:
    """Gegenbauer coefficients b_l of the depth-`depth` two-point function.

    MUST run in extended precision.  kappa^32(0) = 0.9747, so K is nearly
    constant and the coefficients above degree 2 are ~1e-3 of b_0 with the
    higher ones smaller still.  A float64 grid quadrature differences
    near-cancelling integrals and returns NEGATIVE b_l, which is impossible for
    squared norms -- that is exactly how the first version of this script
    failed, producing a 293% degree-4 share and a negative variance ratio.
    """
    import mpmath as mp
    mp.mp.dps = dps
    lam = mp.mpf(d - 2) / 2

    def kap(c):
        return (mp.sqrt(1 - c * c) + (mp.pi - mp.acos(c)) * c) / mp.pi

    def Kf(c):
        for _ in range(depth):
            c = kap(c)
        return c

    def Pn(l, t):
        a, bb = mp.mpf(1), 2 * lam * t
        if l == 0:
            return a
        if l == 1:
            return bb
        for k in range(2, l + 1):
            a, bb = bb, (2 * (k + lam - 1) * t * bb - (k + 2 * lam - 2) * a) / k
        return bb

    one = mp.mpf(1)

    def Pf(l, t):
        return Pn(l, t) / Pn(l, one)

    def w(c):
        return (1 - c * c) ** ((mp.mpf(d) - 3) / 2)

    pts = [-1, mp.mpf("-0.3"), 0, mp.mpf("0.3"), 1]
    b: dict[int, float] = {}
    for l in range(0, lmax + 1, 2):
        num = mp.quad(lambda c: Kf(c) * Pf(l, c) * w(c), pts)
        den = mp.quad(lambda c: Pf(l, c) ** 2 * w(c), pts)
        b[l] = float(num / den)
        if l > 0 and b[l] < 0:
            raise AssertionError(
                f"b_{l} = {b[l]:.3e} is negative; energies cannot be. "
                f"Raise dps above {dps}."
            )
    for l in range(1, lmax + 1, 2):
        b[l] = 0.0
    return b


def design_defect(l: int, m: int, d: int = D) -> float:
    """Exact A_l for m antipodally doubled mutually unbiased bases.

    Valid for EVEN l only.  At odd l the true defect is zero by antipodal
    cancellation and this expression returns a nonzero value.
    """
    if l % 2:
        return 0.0
    lam = F(d - 2, 2)

    def C(n, t):
        a, bb = F(1), 2 * lam * t
        if n == 0:
            return a
        if n == 1:
            return bb
        for k in range(2, n + 1):
            a, bb = bb, (2 * (k + lam - 1) * t * bb - (k + 2 * lam - 2) * a) / k
        return bb

    def P(n, t):
        return C(n, t) / C(n, F(1))

    N = 512 * m
    s = 2 * P(l, F(1)) + 510 * P(l, F(0)) + 512 * (m - 1) * P(l, F(1, 16))
    return float(s / N)


def variance(m: int, b: dict[int, float], lmax: int = LMAX) -> tuple[float, dict[int, float]]:
    terms = {l: b[l] * design_defect(l, m) for l in range(2, lmax + 1, 2)}
    return sum(terms.values()), terms


def main() -> None:
    b = expand()
    v126, t126 = variance(126, b)
    v129, t129 = variance(129, b)

    print(f"two-point function: iterated arc-cosine, depth {DEPTH}, d = {D}")
    print(f"  kappa^{DEPTH}(0)   = {two_point(np.array([0.0]))[0]:.6f}   "
          f"(the output coherence cone)")
    print()
    print("per-degree energy share of the estimand variance, 126-frame design")
    tot = sum(t126.values())
    cum = 0.0
    for l in sorted(t126):
        share = t126[l] / tot
        cum += share
        if l <= 12 or share > 1e-3:
            print(f"  degree {l:2d}   A_l = {design_defect(l,126):.6e}   "
                  f"share = {share*100:7.4f}%   cumulative = {cum*100:6.2f}%")
    deg4 = t126[4] / tot
    ge8 = sum(v for l, v in t126.items() if l >= 8) / tot
    print()
    print(f"  degree-4 share            {deg4*100:.4f}%")
    print(f"  degrees >= 8 share        {ge8*100:.2f}%")
    print()
    print("what completing the design to 129 frames is worth")
    print(f"  V129 / V126               {v129/v126:.6f}")
    print(f"  cost ratio (129/126)      {129/126:.6f}")
    print(f"  predicted SCORE ratio     {(v129/v126)*(129/126):.5f}")
    print(f"  break-even needs          < 1.0")
    print()
    print("cross-check against the independent audit and the committed record")
    for label, got, want in [
        ("degree-4 share %", deg4 * 100, 0.4497),
        ("degrees >= 8 share %", ge8 * 100, 86.0),
        ("V129/V126", v129 / v126, 0.972445),
    ]:
        rel = abs(got - want) / abs(want)
        print(f"  {label:22s} predicted {got:10.4f}   audit {want:10.4f}   "
              f"{'AGREE' if rel < 0.15 else 'DISAGREE'} ({rel*100:.1f}%)")


if __name__ == "__main__":
    main()
