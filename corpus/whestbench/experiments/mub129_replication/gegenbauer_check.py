"""C3: independent structural cross-check for M-MUB129-R.

Standalone by design.  It imports nothing from run_mub129_replication.py, reads
no archive, draws no randomness, and touches no network: the design defect
below is a pure function of the angle set of m mutually unbiased bases in
R^256, antipodally doubled.  Sharing no code path with the variance run is the
whole point of it.

Exact Gegenbauer design defect, in fractions.Fraction throughout:

    A_l = (1/N) * [ 2*P_l(1) + 510*P_l(0) + 512*(m-1)*P_l(1/16) ],   N = 512m

with P_l the degree-l Gegenbauer polynomial for S^{d-1}, d = 256, normalised to
P_l(1) = 1.  The inner-product multiset seen from any point of the design is
{+1 (itself), -1 (antipode), 0 with multiplicity 510 (rest of own frame),
+-1/16 with multiplicity 512(m-1) (all other frames)}; for even l the signs
collapse, which is what the formula encodes.

A_l = 0  <=>  the design is exact at degree l.  Expected: degree 4 exactly zero
at m = 129 and strictly positive at m = 126.

Two independent routes are computed and must agree exactly:
  route A  evaluate P_l at t in {1, 0, 1/16} by the three-term recurrence and
           weight by the distance distribution (the formula above);
  route B  expand P_l into coefficients and contract them against the exact
           raw moments (1/N) sum_y <x,y>^k of the same angle set.
"""

from __future__ import annotations

import json
from fractions import Fraction as F
from pathlib import Path

D = 256
HERE = Path(__file__).resolve().parent


def gegenbauer_coeffs(l: int, d: int = D) -> list[F]:
    """Coefficients (ascending) of the degree-l Gegenbauer polynomial for
    S^{d-1}, normalised to P_l(1) = 1.

    P_0 = 1, P_1 = t,
    (l + d - 2) P_{l+1} = (2l + d - 2) t P_l - l P_{l-1}
    """
    prev: list[F] = [F(1)]
    if l == 0:
        return prev
    cur: list[F] = [F(0), F(1)]
    for k in range(1, l):
        shifted = [F(0)] + cur                       # t * P_k
        nxt = [F(2 * k + d - 2) * c for c in shifted]
        for i, c in enumerate(prev):
            nxt[i] -= F(k) * c
        nxt = [c / F(k + d - 2) for c in nxt]
        prev, cur = cur, nxt
    return cur


def poly_eval(coeffs: list[F], t: F) -> F:
    acc = F(0)
    for c in reversed(coeffs):
        acc = acc * t + c
    return acc


def raw_moment(k: int, m: int) -> F:
    """(1/N) sum_y <x,y>^k over the whole design, exact.  N = 512m."""
    n = 512 * m
    total = F(1) ** k + F(-1) ** k + F(510) * (F(0) ** k if k > 0 else F(1))
    total += F(512 * (m - 1)) * (F(1, 16) ** k + F(-1, 16) ** k) / 2
    return total / F(n)


def defect_route_a(l: int, m: int) -> F:
    c = gegenbauer_coeffs(l)
    n = 512 * m
    val = (F(2) * poly_eval(c, F(1))
           + F(510) * poly_eval(c, F(0))
           + F(512 * (m - 1)) * poly_eval(c, F(1, 16)))
    return val / F(n)


def defect_route_b(l: int, m: int) -> F:
    c = gegenbauer_coeffs(l)
    return sum((c[k] * raw_moment(k, m) for k in range(len(c))), F(0))


def main() -> None:
    out: dict = {
        "check": "C3 exact Gegenbauer design defect",
        "d": D,
        "normalisation": "P_l(1) = 1",
        "degrees": {},
    }
    disagreements = []
    for l in (2, 4, 6):
        row = {}
        for m in (126, 128, 129):
            a = defect_route_a(l, m)
            b = defect_route_b(l, m)
            if a != b:
                disagreements.append((l, m, str(a), str(b)))
            row[f"m_{m}"] = {
                "exact": str(a),
                "float": float(a),
                "is_exactly_zero": a == 0,
                "is_negative": a < 0,
            }
        out["degrees"][f"degree_{l}"] = row

    out["routes_agree_exactly"] = not disagreements
    out["route_disagreements"] = disagreements
    d4 = out["degrees"]["degree_4"]
    out["expected_degree4_zero_at_129"] = d4["m_129"]["is_exactly_zero"]
    out["expected_degree4_nonzero_at_126"] = not d4["m_126"]["is_exactly_zero"]
    out["original_run_reported"] = {
        "A4_m126": 7.350908201315546e-07,
        "A4_m129": 0.0,
        "A6_m126": 3.194089008420301e-05,
        "A6_m129": 3.122025216144244e-05,
        "A2_all": 0.0,
    }
    out["matches_original_A4_m126"] = (
        abs(d4["m_126"]["float"] - 7.350908201315546e-07) <= 1e-18)
    (HERE / "GEGENBAUER_CHECK.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
