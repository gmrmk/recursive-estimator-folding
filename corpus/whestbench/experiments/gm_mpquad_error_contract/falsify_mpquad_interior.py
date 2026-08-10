"""Sharper falsifier for mp.quad's error heuristic: interior narrow features.

The M245 audit's predeclared falsifier (oscillatory sin(k x)) does NOT fire --
measured separately, 234 probes, zero false passes, every wrong answer loudly
flagged. But oscillation is the wrong attack on tanh-sinh.

tanh-sinh places nodes with double-exponential clustering at the ENDPOINTS, so
the interior is sparsely sampled. A feature narrow enough to fall between
interior nodes is invisible; if it stays invisible across two consecutive
refinement levels, the levels agree, the reported error (their difference) is
~0, and the returned value is wrong. That is a true common-mode False PASS, and
it is the mechanism that matters for M245, whose integrand carries a mandatory
kink at t=|alpha| and whose outer quadrature has fixed panels inserted at
{0, 0.25, 1, 2.5, ...}.

Two probes:
  A. narrow Gaussian bump at an interior point, width swept down;
  B. the same bump, with the audit's fixed-panel style splitting applied, to
     ask whether panel insertion helps or hurts.

Exact reference for the bump on [0,1], centre c, width w:
  integral exp(-((x-c)/w)^2) dx = w*sqrt(pi)/2 * (erf((1-c)/w) + erf(c/w))
"""

from __future__ import annotations

import mpmath as mp

DPS = 80
MAXDEGREE = 14
ZERO_CLAIM = mp.mpf(10) ** -40
BAD_REL = mp.mpf(10) ** -6


def exact_bump(c, w) -> mp.mpf:
    return w * mp.sqrt(mp.pi) / 2 * (mp.erf((1 - c) / w) + mp.erf(c / w))


def run(centre, widths, panels=None, label=""):
    c = mp.mpf(centre)
    print(f"\n=== {label} (centre={mp.nstr(c,6)}"
          f"{', panels=' + str(panels) if panels else ''}) ===")
    print(f"{'width':>12} {'reported err':>14} {'true rel err':>14}  verdict", flush=True)
    hits = []
    for w_ in widths:
        w = mp.mpf(w_)
        f = lambda x: mp.exp(-((x - c) / w) ** 2)
        interval = panels if panels else [0, 1]
        try:
            val, err = mp.quad(f, interval, error=True, maxdegree=MAXDEGREE)
        except Exception as exc:
            print(f"{mp.nstr(w,6):>12} {'EXC':>14} {'-':>14}  {exc}")
            continue
        ref = exact_bump(c, w)
        rel = abs(val - ref) / abs(ref)
        claims_zero = err <= ZERO_CLAIM
        is_bad = rel >= BAD_REL
        verdict = ("*** FALSE PASS ***" if (claims_zero and is_bad)
                   else "wrong, but flagged" if is_bad
                   else "ok")
        if claims_zero and is_bad:
            hits.append((w, err, rel))
        print(f"{mp.nstr(w,6):>12} {mp.nstr(err,6):>14} {mp.nstr(rel,6):>14}  {verdict}",
              flush=True)
    return hits


def main() -> None:
    mp.mp.dps = DPS
    print(f"mpmath {mp.__version__}  dps={DPS}  maxdegree={MAXDEGREE}  tanh-sinh")
    print("FALSIFIED := reported err <= 1e-40 AND true rel err >= 1e-6")

    widths = ["1e-3", "1e-4", "1e-5", "1e-6", "1e-8", "1e-10", "1e-12", "1e-15"]
    all_hits = []
    all_hits += run("0.5", widths, label="A1 interior bump, plain [0,1]")
    all_hits += run("0.3141592653589793", widths,
                    label="A2 interior bump at an irrational centre")
    all_hits += run("0.5", widths, panels=[0, mp.mpf("0.25"), 1],
                    label="B1 bump at 0.5 with audit-style panel split at 0.25")
    all_hits += run("0.5", widths, panels=[0, mp.mpf("0.25"), mp.mpf("0.5"), 1],
                    label="B2 bump at 0.5 with a panel edge ON the feature")

    print("\n" + "=" * 62)
    if all_hits:
        print(f"RESULT: FALSIFIED. {len(all_hits)} case(s) where mp.quad reported "
              f"error <= 1e-40 while the value was wrong.")
        w, err, rel = max(all_hits, key=lambda t: t[2])
        print(f"  worst: width={mp.nstr(w,6)}  reported={mp.nstr(err,6)}  "
              f"true_rel={mp.nstr(rel,6)}")
    else:
        print("RESULT: NOT FALSIFIED by this probe either.")


if __name__ == "__main__":
    main()
