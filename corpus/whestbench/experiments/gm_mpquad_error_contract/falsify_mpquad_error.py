"""Falsifier: is mpmath's `mp.quad(..., error=True)` heuristic trustworthy?

Predeclared by the M245 audit, verbatim:

    Provide a predeclared symbolic integrand f(x) = sin(k x) where k is
    specifically tuned to alias the exact spacing of the tanh-sinh final
    refinement level (maxdegree=14). If error=True returns 0 despite massive
    analytical error, the software-contract premise is falsified.

mp.quad's reported error is the difference between the last two refinement
levels. If an oscillatory integrand aliases the node grid at BOTH levels, the
levels agree, the heuristic reports ~0, and the value is wrong. Because M245's
primary and replica both trust this heuristic, a hit is a common-mode False
PASS, not a single-engine defect.

Exact reference: integral_0^1 sin(k x) dx = (1 - cos k)/k, closed form, so the
true error is known independently of any quadrature.

maxdegree is swept as well as k: the mechanism is grid coarseness, and the
coarser grids are where the two-level agreement is easiest to produce. A hit at
any maxdegree falsifies the software-contract premise; a hit at 14 falsifies it
at M245's own setting.

FALSIFIED: reported error at or near zero while the true relative error is large.
"""

from __future__ import annotations

import mpmath as mp

DPS = 80
ZERO_CLAIM = mp.mpf(10) ** -40   # engine claiming full confidence at 80 dps
BAD_REL = mp.mpf(10) ** -6       # a genuinely wrong answer
MAXDEGREES = (3, 4, 5, 6, 7, 8, 10, 12, 14)


def exact(k) -> mp.mpf:
    return (1 - mp.cos(k)) / k


def probe(k, maxdegree):
    f = lambda x: mp.sin(k * x)
    val, err = mp.quad(f, [0, 1], error=True, maxdegree=maxdegree)
    ref = exact(k)
    denom = abs(ref) if abs(ref) > mp.mpf(10) ** -30 else mp.mpf(1)
    return val, err, ref, abs(val - ref) / denom


def main() -> None:
    mp.mp.dps = DPS
    print(f"mpmath {mp.__version__}  dps={DPS}  tanh-sinh (mp.quad default)")
    print("integrand sin(k x) on [0,1];  exact = (1 - cos k)/k")
    print(f"FALSIFIED := reported err <= 1e-40 AND true rel err >= 1e-6\n", flush=True)

    ks = [mp.mpf(m) * (mp.mpf(2) ** e) for e in range(2, 15) for m in (1, 3)]

    hits: list[tuple] = []
    worst: list[tuple] = []
    for md in MAXDEGREES:
        n_bad = n_hit = 0
        for k in ks:
            try:
                val, err, ref, rel = probe(k, md)
            except Exception:
                continue
            claims_zero = err <= ZERO_CLAIM
            is_bad = rel >= BAD_REL
            worst.append((rel, k, md, err, claims_zero))
            if is_bad:
                n_bad += 1
            if claims_zero and is_bad:
                n_hit += 1
                hits.append((k, md, err, rel))
        print(f"maxdegree={md:>3}: wrong={n_bad:>3}/{len(ks)}   "
              f"FALSE PASS={n_hit:>3}", flush=True)

    print()
    if hits:
        print(f"RESULT: FALSIFIED. {len(hits)} case(s) where the engine reported "
              f"error <= 1e-40 while the answer was wrong.")
        hits.sort(key=lambda t: -t[3])
        print(f"\n{'k':>16} {'maxdeg':>7} {'reported err':>14} {'true rel err':>14}")
        print("-" * 56)
        for k, md, err, rel in hits[:12]:
            print(f"{mp.nstr(k,8):>16} {md:>7} {mp.nstr(err,6):>14} {mp.nstr(rel,6):>14}")
        at14 = [h for h in hits if h[1] == 14]
        print(f"\nhits at M245's own maxdegree=14: {len(at14)}")
        for k, md, err, rel in at14[:5]:
            print(f"  k={mp.nstr(k,10)}  reported={mp.nstr(err,6)}  "
                  f"true_rel={mp.nstr(rel,6)}")
    else:
        print("RESULT: NOT FALSIFIED by this sweep -- every wrong answer carried "
              "a non-negligible reported error.")

    worst.sort(reverse=True)
    print("\nlargest true relative errors observed:")
    for rel, k, md, err, cz in worst[:6]:
        print(f"  k={mp.nstr(k,10):>14} md={md:>3}  true_rel={mp.nstr(rel,6):>12}"
              f"  reported={mp.nstr(err,6):>12}  claims_zero={cz}")


if __name__ == "__main__":
    main()
