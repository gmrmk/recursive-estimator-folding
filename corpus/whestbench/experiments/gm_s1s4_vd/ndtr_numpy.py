"""Vectorized ndtr for the PINNED interpreter, which has numpy 2.4.6 and NO scipy.

DEVIATION D5 (declared): the committed `s4_portfolio/run_s4.py` imports
`scipy.special.ndtr`; the pinned python
(work/whest-v014/Scripts/python.exe) has no scipy. Rather than switch
interpreters, ndtr is reimplemented here as 0.5*erfc(-x/sqrt(2)) with W. J.
Cody's CALERF rational approximation (the same algorithm cephes/scipy use), and
validated against the C library's math.erfc. Acceptance test for the substitute
is the S4 control arm reproducing the committed s4_results.json numbers.
"""
import numpy as np

_A = [3.16112374387056560e00, 1.13864154151050156e02, 3.77485237685302021e02,
      3.20937758913846947e03, 1.85777706184603153e-1]
_B = [2.36012909523441209e01, 2.44024637934444173e02, 1.28261652607737228e03,
      2.84423683343917062e03]
_C = [5.64188496988670089e-1, 8.88314979438837594e00, 6.61191906371416295e01,
      2.98635138197400131e02, 8.81952221241769090e02, 1.71204761263407058e03,
      2.05107837782607147e03, 1.23033935479799725e03, 2.15311535474403846e-8]
_D = [1.57449261107098347e01, 1.17693950891312499e02, 5.37181101862009858e02,
      1.62138957456669019e03, 3.29079923573345963e03, 4.36261909014324716e03,
      3.43936767414372164e03, 1.23033935480374942e03]
_P = [3.05326634961232344e-1, 3.60344899949804439e-1, 1.25781726111229246e-1,
      1.60837851487422766e-2, 6.58749161529837803e-4, 1.63153871373020978e-2]
_Q = [2.56852019228982242e00, 1.87295284992346047e00, 5.27905102951428412e-1,
      6.05183413124413191e-2, 2.33520497626869185e-3]
_SQRPI = 5.6418958354775628695e-1          # 1/sqrt(pi)
_THRESH = 0.46875


def _erfc_pos(y):
    """erfc(y) for y >= 0 (array)."""
    out = np.empty_like(y)

    m1 = y <= _THRESH
    if m1.any():
        yy = y[m1]
        z = yy * yy
        xnum = _A[4] * z
        xden = z.copy()
        for i in range(3):
            xnum = (xnum + _A[i]) * z
            xden = (xden + _B[i]) * z
        out[m1] = 1.0 - yy * (xnum + _A[3]) / (xden + _B[3])

    m2 = (~m1) & (y <= 4.0)
    if m2.any():
        yy = y[m2]
        xnum = _C[8] * yy
        xden = yy.copy()
        for i in range(7):
            xnum = (xnum + _C[i]) * yy
            xden = (xden + _D[i]) * yy
        res = (xnum + _C[7]) / (xden + _D[7])
        ysq = np.trunc(yy * 16.0) / 16.0
        dele = (yy - ysq) * (yy + ysq)
        out[m2] = np.exp(-ysq * ysq) * np.exp(-dele) * res

    m3 = y > 4.0
    if m3.any():
        yy = y[m3]
        z = 1.0 / (yy * yy)
        xnum = _P[5] * z
        xden = z.copy()
        for i in range(4):
            xnum = (xnum + _P[i]) * z
            xden = (xden + _Q[i]) * z
        res = z * (xnum + _P[4]) / (xden + _Q[4])
        res = (_SQRPI - res) / yy
        ysq = np.trunc(yy * 16.0) / 16.0
        dele = (yy - ysq) * (yy + ysq)
        out[m3] = np.exp(-ysq * ysq) * np.exp(-dele) * res
    return out


def erfc(x):
    x = np.asarray(x, dtype=np.float64)
    y = np.abs(x)
    r = _erfc_pos(y)
    return np.where(x < 0.0, 2.0 - r, r)


def ndtr(x):
    """Standard normal CDF, drop-in for scipy.special.ndtr."""
    x = np.asarray(x, dtype=np.float64)
    return 0.5 * erfc(-x / np.sqrt(2.0))


if __name__ == "__main__":
    import math, json, os
    rng = np.random.default_rng(20260810)
    pts = np.concatenate([
        rng.standard_normal(200_000),
        rng.uniform(-40, 40, 50_000),
        np.linspace(-9, 9, 50_000),
        np.array([0.0, 0.46875, -0.46875, 4.0, -4.0, 1e-300, -1e-300]),
    ])
    mine = ndtr(pts)
    ref = np.array([0.5 * math.erfc(-v / math.sqrt(2.0)) for v in pts])
    nz = ref > 0
    rel = np.abs(mine[nz] / ref[nz] - 1.0)
    ulp = np.abs(mine - ref) / np.maximum(np.spacing(np.abs(ref)), 5e-324)
    rep = {"n_points": int(pts.size),
           "max_rel_diff_vs_math.erfc": float(rel.max()),
           "mean_rel_diff": float(rel.mean()),
           "max_ulp_diff": float(ulp.max()),
           "frac_bitwise_identical": float((mine == ref).mean()),
           "erfc_max_rel_vs_math": float(max(
               abs(erfc(np.array([v]))[0] / math.erfc(v) - 1.0)
               for v in np.concatenate([rng.standard_normal(2000), rng.uniform(0, 25, 2000)])
               if math.erfc(v) > 0))}
    print(json.dumps(rep, indent=1))
    json.dump(rep, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "ndtr_validation.json"), "w"), indent=1)
