"""Bisect the magnitude at which mp.quad(tanh-sinh, maxdegree=14) stops meeting
the absolute gate `err <= mp.eps/8`, at the exact precision a nested M245
replica inner call runs at (dps=80 -> ambient 269 -> +20 = 289).

FIREWALL: mpmath + stdlib only.  No m245 import, no authority read, no rerun.
The integrand shape `constant * exp(-t^2/2)` is the shape the replica's inner
integrand collapses to for the varying dummy event (rho_c == 0 makes the inner
conditional means independent of the inner variable).
"""

import time

from mpmath import mp

OUT = []


def say(text):
    OUT.append(text)
    print(text)


mp.dps = 80
mp.prec = mp.prec + 20            # inside the outer quad integrand
saved_eps = +mp.eps
gate = saved_eps / 8
say(f"prec={mp.prec}  saved_eps={mp.nstr(saved_eps, 8)}  gate={mp.nstr(gate, 8)}")
say("")
say(f"{'scale':>8} {'panel value':>16} {'returned err':>15} {'pass':>6} {'secs':>7}")

results = {}
for exponent in (45, 50, 53, 55, 56, 57, 58, 59, 60, 61):
    scale = mp.mpf(10) ** exponent
    integrand = lambda t, s=scale: s * mp.exp(-(mp.mpf(t) ** 2) / 2)
    start = time.perf_counter()
    value, err = mp.quad(
        integrand, [mp.mpf(0), mp.mpf("0.25")],
        method="tanh-sinh", maxdegree=14, error=True,
    )
    elapsed = time.perf_counter() - start
    passed = bool(err >= 0 and err <= gate)
    results[exponent] = passed
    say(
        f"{'1e' + str(exponent):>8} {mp.nstr(value, 8):>16} {mp.nstr(err, 8):>15} "
        f"{str(passed):>6} {elapsed:7.2f}"
    )

failing = sorted(e for e, ok in results.items() if not ok)
passing = sorted(e for e, ok in results.items() if ok)
say("")
say(f"passing exponents: {passing}")
say(f"failing exponents: {failing}")
say("")
say("Replica inner panel [0,0.25] value at the degree-1 node of the outer")
say("panel [16,inf) (g = 2.5179e61):  ~ -8.5e59   (|value| ~ 1e60)")

with open("threshold_bisect.out.txt", "w", encoding="utf-8") as handle:
    handle.write("\n".join(OUT) + "\n")
