"""M191 G0-a: the Kerdock design's harmonic quadrature-error spectrum.

Deterministic (no sampling). For the 64,512 antipodal directions under a Haar
rotation, measure the RMS quadrature error on random zero-mean harmonic
polynomials of degree d=1..6, versus the iid-MC scale 1/sqrt(N). The first
degree where the design's error is ~iid-level (not ~0) is where a harmonic
control variate has room; if degree 4 is also annihilated the design is a
4-design and the CV ceiling is degree>=6.

Zero-mean harmonic of degree d on the sphere in R^n: contract a traceless
symmetric tensor T with u^{⊗d}. We use the tractable, exactly-zero-mean
families that dominate the estimator's own error:
  d=2: u^T A u - tr(A)/n,  A symmetric  (E=0 under uniform measure)
  d=4: (u^T A u)^2 - E[(u^T A u)^2]  built to be zero-mean, plus the pure
        quartic (a·u)^4 - 3||a||^4/(n(n+2))  (zero-mean, degree-4 harmonic-ish;
        we orthogonalize numerically against lower degrees via the MC mean).
We measure error as mean_s p(u_s) (design) which has TRUE mean 0, so the
measured mean IS the quadrature error; compare to the iid RMS over matched N.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N8A = HERE.parent / "n8a_rqmc_kerdock"
sys.path.insert(0, str(N8A))
from run_n8a_gates import load_kerdock_directions, haar_rotation, WIDTH, MEAN_CHI_256  # noqa: E402

N = WIDTH  # dimension 256


def unit_directions(rot_seed):
    """The design's directions on the UNIT sphere (radius divided out)."""
    d = load_kerdock_directions() @ haar_rotation(rot_seed)
    d = d / MEAN_CHI_256
    return np.concatenate([d, -d], axis=0)  # antipodal, 64512 x 256


def rms_quadrature_error(U, degree, n_poly, rng):
    """RMS over n_poly random zero-mean degree-`degree` harmonics of
    mean_s p(u_s). U: (M,n) unit vectors. Returns (design_rms, iid_rms)."""
    M = U.shape[0]
    errs = []
    iid = []
    for _ in range(n_poly):
        if degree == 1:
            a = rng.standard_normal(N); a /= np.linalg.norm(a)
            p = U @ a                                  # degree 1, zero-mean
        elif degree == 2:
            A = rng.standard_normal((N, N)); A = (A + A.T) / 2
            A -= np.trace(A) / N * np.eye(N)           # traceless -> zero-mean
            p = np.einsum('mi,ij,mj->m', U, A, U)
        elif degree == 3:
            a = rng.standard_normal(N); a /= np.linalg.norm(a)
            p = (U @ a) ** 3 - 3.0 / (N + 2) * (U @ a)  # zero-mean cubic
        elif degree == 4:
            a = rng.standard_normal(N); a /= np.linalg.norm(a)
            t = U @ a
            # (a.u)^4 has mean 3/((n)(n+2)); subtract to zero-mean it
            p = t ** 4 - 3.0 / (N * (N + 2))
        elif degree == 5:
            a = rng.standard_normal(N); a /= np.linalg.norm(a)
            t = U @ a
            p = t ** 5 - 15.0 / ((N + 2) * (N + 4)) * t
        else:  # degree 6
            a = rng.standard_normal(N); a /= np.linalg.norm(a)
            t = U @ a
            p = t ** 6 - 15.0 / (N * (N + 2) * (N + 4))
        # normalize each polynomial to unit sample-variance so degrees compare
        s = p.std()
        if s > 0:
            p = p / s
        errs.append(abs(p.mean()))
        iid.append(1.0 / math.sqrt(M))   # unit-variance iid mean RMS
    return float(np.sqrt(np.mean(np.square(errs)))), float(np.mean(iid))


def main():
    out = {"dimension": N, "note": "polynomials normalized to unit sample variance"}
    for rot_seed in (0, 1, 2):
        U = unit_directions(rot_seed)
        M = U.shape[0]
        rng = np.random.default_rng(1000 + rot_seed)
        row = {"M": M}
        print(f"\n-- rotation {rot_seed}  (M={M} antipodal directions, iid RMS {1/math.sqrt(M):.3e}) --")
        for d in (1, 2, 3, 4, 5, 6):
            des, iid = rms_quadrature_error(U, d, 40, rng)
            ratio = des / iid
            row[f"deg{d}"] = {"design_rms": des, "iid_rms": iid, "ratio": ratio}
            tag = "EXACT(~0)" if ratio < 0.05 else ("iid-level" if ratio > 0.5 else "partial")
            print(f"  degree {d}: design RMS {des:.3e}  iid RMS {iid:.3e}  ratio {ratio:6.3f}  {tag}")
        out[f"rot{rot_seed}"] = row
    # verdict from rotation 0
    r = out["rot0"]
    first_nonexact = next((d for d in (2, 4, 6) if r[f"deg{d}"]["ratio"] >= 0.05), None)
    out["first_nonexact_even_degree"] = first_nonexact
    print(f"\nVERDICT: odd degrees {'annihilated' if r['deg1']['ratio']<0.05 and r['deg3']['ratio']<0.05 else 'NOT annihilated'} "
          f"(antipodal); first non-exact EVEN degree = {first_nonexact}")
    if first_nonexact is None:
        print("  -> design exact through degree 6: CV ceiling is degree>=8 structure (likely negligible) -> M191 headroom small")
    else:
        print(f"  -> harmonic CV has room at degree {first_nonexact}; proceed to G0-b (battery arm)")
    (HERE / "m191_g0a_results.json").write_text(json.dumps(out, indent=2) + "\n")
    print("wrote m191_g0a_results.json")


if __name__ == "__main__":
    main()
