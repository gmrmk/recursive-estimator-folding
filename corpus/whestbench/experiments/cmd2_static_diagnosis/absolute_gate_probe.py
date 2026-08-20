"""Falsification probe: is mp.quad's convergence test ABSOLUTE, and does a
large-magnitude integrand therefore fail the `error <= saved_eps/8` gate?

FIREWALL: mpmath + stdlib only.  No m245 import, no authority read, no rerun of
any GREEN command.  The integrand is a generic scaled Gaussian, not an M245
integrand.
"""

import time

from mpmath import mp

OUT = []


def say(text):
    OUT.append(text)
    print(text)


# Reproduce the exact precision ladder a nested M245 replica call sees at dps=80:
#   ambient 269 -> outer mp.quad extraprec(20) -> 289 = the prec the INNER
#   _request_quad reads mp.eps at, and the prec the inner mp.quad passes to
#   summation().
mp.dps = 80
AMBIENT = mp.prec
mp.prec = AMBIENT + 20          # we are now "inside the outer quad integrand"
INNER_AMBIENT = mp.prec
saved_eps = +mp.eps             # exactly what _request_quad captures
gate = saved_eps / 8

say(f"ambient prec at dps=80          : {AMBIENT}")
say(f"prec inside outer quad integrand: {INNER_AMBIENT}")
say(f"saved_eps                       : {mp.nstr(saved_eps, 8)}")
say(f"M245 gate  error <= saved_eps/8 : {mp.nstr(gate, 8)}")
say("")

say(f"{'scale M':>12} {'panel value':>16} {'returned err':>16} {'err<=eps/8':>11} {'secs':>7}")
for exponent in (0, 3, 5, 6, 8, 12, 20, 40, 61):
    scale = mp.mpf(10) ** exponent
    integrand = lambda t, s=scale: s * mp.exp(-(mp.mpf(t) ** 2) / 2)
    start = time.perf_counter()
    value, err = mp.quad(
        integrand, [mp.mpf(0), mp.mpf("0.25")],
        method="tanh-sinh", maxdegree=14, error=True,
    )
    elapsed = time.perf_counter() - start
    passed = bool(err >= 0 and gate > 0 and err <= gate)
    say(
        f"{'1e' + str(exponent):>12} {mp.nstr(value, 8):>16} "
        f"{mp.nstr(err, 8):>16} {str(passed):>11} {elapsed:7.2f}"
    )

say("")
say("== node census for the replica's 8 frozen inner panels, prec=289 ==")
mp.prec = INNER_AMBIENT
rule = mp._tanh_sinh
panels = [(0.0, 0.25), (0.25, 1.0), (1.0, 2.5), (2.5, 5.0),
          (5.0, 8.0), (8.0, 10.0), (10.0, 16.0), (16.0, "inf")]
say(f"{'panel':>16} " + " ".join(f"{'d' + str(d):>7}" for d in range(1, 9)) + f" {'cum(1..8)':>10}")
for left, right in panels:
    a = mp.mpf(left)
    b = mp.inf if right == "inf" else mp.mpf(right)
    counts = []
    for degree in range(1, 9):
        counts.append(len(rule.get_nodes(a, b, degree, INNER_AMBIENT)))
    label = f"[{left},{right})"
    say(f"{label:>16} " + " ".join(f"{c:>7}" for c in counts) + f" {sum(counts):>10}")

with open("absolute_gate_probe.out.txt", "w", encoding="utf-8") as handle:
    handle.write("\n".join(OUT) + "\n")
