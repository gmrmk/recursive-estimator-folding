"""Independent arithmetic cross-check for the cmd2 setUpClass diagnosis.

FIREWALL: imports ONLY mpmath + stdlib.  Imports NO m245 module, reads NO
authority artifact, reruns NO part of the M245 GREEN sequence.  Every constant
below was transcribed by hand from test_m245_replica_core.py (read, not
imported).  This is arithmetic only.
"""

from fractions import Fraction
import math
import time

from mpmath import mp

OUT = []


def say(text):
    OUT.append(text)
    print(text)


# ---------------------------------------------------------------- A. rho_c
# _varying_dummy_event(): mu=(0.10,-0.20,0.30);
# C = [[1,0.30,-0.25],[0.30,1,-0.075],[-0.25,-0.075,1]]   (binary64 literals)
F = Fraction
c00, c01, c02 = F(1.0), F(0.30), F(-0.25)
c11, c12 = F(1.0), F(-0.075)
c22 = F(1.0)
mu0, mu1, mu2 = F(0.10), F(-0.20), F(0.30)

say("== A. exact binary64 rational arithmetic on the varying dummy event ==")
say(f"fl(0.30)*fl(-0.25)         = {float(c01 * c02)!r}")
say(f"fl(-0.075)                 = {float(c12)!r}")
say(f"C_jk - C_ij*C_ik/C_ii == 0 : {c12 - c01 * c02 / c00 == 0}")

var_j = c11 - c01 * c01 / c00
var_k = c22 - c02 * c02 / c00
det = (
    c00 * (c11 * c22 - c12 * c12)
    - c01 * (c01 * c22 - c12 * c02)
    + c02 * (c01 * c12 - c11 * c02)
)
say(f"variance_j = {float(var_j)!r} > 0 : {var_j > 0}")
say(f"variance_k = {float(var_k)!r} > 0 : {var_k > 0}")
say(f"leading 2x2 minor = {float(c00 * c11 - c01 * c01)!r} > 0 : {c00 * c11 - c01 * c01 > 0}")
say(f"det(C)     = {float(det)!r} > 0 : {det > 0}")
say(f"symmetric exactly          : True (built from one symmetric tuple)")
say(f"=> rho_c == 0 EXACTLY, so ell=0, s=1, eta=0")

# ------------------------------------------------------------- B. bounds
alpha = abs(mu0 / F(1))  # sigma_i = sqrt(C00) = 1 exactly
base = [0.0, 0.25, 1.0, 2.5, 5.0, 8.0, 10.0, 16.0]
say("")
say("== B. _outer_panel_bounds census ==")
say(f"alpha = |mu_i/sigma_i| = {float(alpha)!r}")
say(f"alpha collides with a base panel : {any(F(v) == alpha for v in base)}")
bounds = sorted(base + [float(alpha)]) + [math.inf]
say(f"outer bounds = {bounds}")
say(f"outer panel count = {len(bounds) - 1}  (last panel is [16, inf))")

# ------------------------------------------------- C. precision / eps ladder
say("")
say("== C. precision and absolute-gate ladder ==")
for dps in (80, 100):
    mp.dps = dps
    p_ambient = mp.prec
    mp.prec = p_ambient + 20          # inside outer quad's extraprec(20)
    p_outer = mp.prec
    eps_inner_gate = mp.eps / 8       # saved_eps/8 seen by the INNER _request_quad
    mp.prec = p_outer + 20            # inside inner quad's extraprec(20)
    p_eval = mp.prec
    say(
        f"dps={dps}: ambient prec={p_ambient} bits | outer-quad prec={p_outer} "
        f"| inner-eval prec={p_eval} bits (~{p_eval / 3.3219:.1f} digits)"
    )
    say(f"         inner absolute gate  saved_eps/8 = {mp.nstr(eps_inner_gate, 6)}")
    floor = mp.mpf(2) ** (-p_eval)
    say(f"         round-off floor per unit magnitude = 2^-{p_eval} = {mp.nstr(floor, 6)}")
    m_max = eps_inner_gate / floor
    say(f"         MAX integrand magnitude that can meet the gate: |M| <= {mp.nstr(m_max, 6)}")

# -------------------------------------- D. tanh-sinh node reach on [16, inf)
say("")
say("== D. mpmath tanh-sinh node reach for the outer panel [16, inf) ==")
for dps, ambient in ((80, None), (100, None)):
    mp.dps = dps
    prec_outer = mp.prec + 20         # prec argument mp.quad passes to summation
    mp.prec = prec_outer
    rule = mp._tanh_sinh
    for degree in (1, 2):
        nodes = rule.get_nodes(mp.mpf(16), mp.inf, degree, prec_outer)
        tmax = max(x for x, w in nodes)
        say(
            f"dps={dps} prec={prec_outer} degree={degree}: {len(nodes)} nodes, "
            f"max node g = {mp.nstr(tmax, 8)}"
        )

# ------------------------- E. magnitude of the replica inner integrand vs g
say("")
say("== E. independent re-derivation of |b-panel| magnitude vs outer node g ==")
mp.dps = 80
mp.prec = mp.prec + 40                # inner evaluation precision at dps=80


def relumean(nu, sigma):
    a = nu / sigma
    return sigma * (a * (mp.erfc(-a / mp.sqrt(2)) / 2) + mp.exp(-(a * a) / 2) / mp.sqrt(2 * mp.pi))


s_j = mp.sqrt(mp.mpf(91) / 100)
s_k = mp.sqrt(mp.mpf(9375) / 10000)
gj = relumean(mp.mpf(-0.20), mp.mpf(1))
gk = relumean(mp.mpf(0.30), mp.mpf(1))
# panel [0,0.25] weight of 2*phi(t): 2*(Phi(0.25)-Phi(0))
panel_w = mp.erf(mp.mpf(0.25) / mp.sqrt(2))

say(f"global_relu_mean_j = {mp.nstr(gj, 10)}   global_relu_mean_k = {mp.nstr(gk, 10)}")
say(f"weight of inner panel [0,0.25] for 2*phi = {mp.nstr(panel_w, 10)}")
rows = []
for g in (mp.mpf(16), mp.mpf(10) ** 3, mp.mpf(10) ** 6, mp.mpf(10) ** 10, mp.mpf(10) ** 20):
    nu_j = mp.mpf("-0.20") + mp.mpf("0.30") * g
    nu_k = mp.mpf("0.30") - mp.mpf("0.25") * g
    cj = relumean(nu_j, s_j) - gj
    ck = relumean(nu_k, s_k) - gk
    panel = 2 * cj * ck * panel_w
    rows.append((g, panel))
    say(f"g = {mp.nstr(g, 4):>12}  |b-panel[0,0.25]| = {mp.nstr(abs(panel), 8)}")

mp.dps = 80
p_eval = mp.prec + 40
gate = None
mp.prec = mp.prec + 20
gate = mp.eps / 8
mp.prec = p_eval
say(f"inner absolute gate at dps=80 = {mp.nstr(gate, 6)}")
say(f"round-off floor for magnitude M is ~M*2^-{p_eval}")
say(
    "=> the gate becomes unsatisfiable once |M| exceeds "
    f"{mp.nstr(gate * (mp.mpf(2) ** p_eval), 6)}"
)

# ------------------------------------------------ F. erfc cost calibration
say("")
say("== F. mpmath primitive cost at the replica's inner evaluation precision ==")
for prec in (309, 376):
    mp.prec = prec
    x = mp.mpf(7) / 10
    n = 2000
    t0 = time.perf_counter()
    for _ in range(n):
        mp.erfc(x)
    t_erfc = (time.perf_counter() - t0) / n
    t0 = time.perf_counter()
    for _ in range(n):
        mp.exp(x)
    t_exp = (time.perf_counter() - t0) / n
    say(
        f"prec={prec}: erfc = {t_erfc * 1e6:8.2f} us   exp = {t_exp * 1e6:8.2f} us"
    )

with open("independent_arithmetic_check.out.txt", "w", encoding="utf-8") as handle:
    handle.write("\n".join(OUT) + "\n")
