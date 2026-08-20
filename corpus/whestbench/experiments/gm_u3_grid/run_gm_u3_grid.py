"""gm_u3_grid -- U3 tail-model fidelity: the (vD x F-pool-shape) bracketing grid.

Implements PREDECLARATION.md in this directory, verbatim. Response-free,
offline, committed JSON inputs only, writes only into this directory.

The statistic is exactly S1b section 2 (`run_s1b.py::run_spread80`): NREP
replicates of the 80-net single-draw max/min spread of D*F, versus the
committed observation 15.531671197493653.

Grid:
  axis 1  vD in {7.57e-4 (DIFF_RATIO 1.1 control), 0.0814, 0.1220}
  axis 2  F in {empirical48, gpd_ext (POT k=12, MLE xi), lognorm_ext (MLE)}
  axis 3  gpd_ext xi swept over the predeclared tail-index grid (Gate B)
  annex   POT threshold k in {6, 16} at MLE xi

Order of operations: STEP 0 (deterministic support bound, can kill without any
Monte Carlo) -> control reproduction asserts -> headline MC grid -> two-signal
verification (numerical-quadrature recomputation, Philox/inverse-CDF repeat,
bitwise repeat) -> gates.
"""
import json
import hashlib
import time
import math
import numpy as np

ROOT = r"C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding"
EXP = ROOT + r"\corpus\whestbench\experiments"
P2_PATH = EXP + r"\pb1_premise_battery\p2_results.json"
M185_PATH = EXP + r"\a_series_granular_adversarial\m185_g0_stage1_checkpoint.json"
A1B_PATH = EXP + r"\a_series_granular_adversarial\a1b_tail_diagnostics.json"
S17_PATH = EXP + r"\s17_ibc_floor\s17_results.json"
S1_PATH = EXP + r"\s1_suite_risk\s1_results.json"
S1B_PATH = EXP + r"\s1b_dispersion_corrected\s1b_results.json"
OUT_JSON = EXP + r"\gm_u3_grid\results.json"

MASTER_SEED = 20260809          # identical to committed S1 / S1b
NREP = 10_000                   # identical to committed run_spread80
NREP_CONFIRM = 200_000          # signal 3
POT_K_PRIMARY = 12
POT_K_ANNEX = (6, 16)
XI_GRID = [-0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
GATE_LO, GATE_HI = 0.20, 0.90
VD_SMALL_MAX = 0.01             # "vD <= 0.01" in the mined falsifier

t0 = time.time()
log_lines = []


def say(s):
    print(s, flush=True)
    log_lines.append(s)


# ---------------------------------------------------------------- inputs
p2 = json.load(open(P2_PATH))
per_net = p2["q1_oracle_headroom"]["per_net"]
NET_KEYS = ("101", "202", "303")
pool_parts = []
for seed, rec in sorted(per_net.items()):
    m = np.asarray(rec["mse_per_rotation"], dtype=np.float64)
    pool_parts.append(m / m.mean())
pool = np.concatenate(pool_parts)
pool = pool / pool.mean()
vF = float(pool.var())
pool_spread = float(pool.max() / pool.min())

s1_committed = json.load(open(S1_PATH))
s1b_committed = json.load(open(S1B_PATH))
assert abs(vF - s1_committed["calibration"]["vF_rotation_factor_variance"]) < 1e-15
assert abs(pool_spread - s1_committed["calibration"]["pool_max_over_min"]) < 1e-12

s17 = json.load(open(S17_PATH))
sig2 = np.array([s17["A_per_net"][k]["sigma2_var(ybar)"] for k in NET_KEYS])
relvar = lambda x, d: float(np.var(x, ddof=d) / np.mean(x) ** 2)
vD_s17_low, vD_s17_high = relvar(sig2, 0), relvar(sig2, 1)

m185 = json.load(open(M185_PATH))
m185_raw = np.array([v["mse_raw"] for v in m185["nets"].values()], dtype=np.float64)
OBS = float(m185_raw.max() / m185_raw.min())
a1b = json.load(open(A1B_PATH))
assert abs(OBS - a1b["spread"]) < 1e-9
LOG_OBS = math.log(OBS)


# ------------------------------------------- difficulty model (verbatim S1b)
def vD_of_ratio(r):
    half = np.log(r) / 2.0
    if half <= 0:
        return 0.0
    d_mean = np.sinh(half) / half
    return float((np.sinh(2 * half) / (2 * half)) / d_mean ** 2 - 1.0)


def ratio_of_vD(target):
    lo, hi = 1.0 + 1e-12, 1e6
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        if vD_of_ratio(mid) < target:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


def make_arm(vD=None, ratio=None):
    if ratio is None:
        ratio = ratio_of_vD(vD)
    vD = vD_of_ratio(ratio)
    half = np.log(ratio) / 2.0
    return {"vD": float(vD), "ratio": float(ratio), "half": float(half),
            "d_mean": float(np.sinh(half) / half)}


ARMS = {
    "vD_7.57e-04": make_arm(ratio=1.1),
    "vD_0.0814": make_arm(vD=vD_s17_low),
    "vD_0.1220": make_arm(vD=vD_s17_high),
}
assert abs(ARMS["vD_7.57e-04"]["vD"]
           - s1_committed["calibration"]["vD_difficulty_variance"]) < 1e-15


def draw_D(rng, shape, arm):
    return np.exp(rng.uniform(-arm["half"], arm["half"], size=shape)) / arm["d_mean"]


# ------------------------------------------------------- GPD tail machinery
srt = np.sort(pool)


def gpd_nll(xi, sigma, y):
    if sigma <= 0:
        return np.inf
    if abs(xi) < 1e-10:
        return len(y) * math.log(sigma) + float(np.sum(y)) / sigma
    z = 1.0 + xi * y / sigma
    if np.any(z <= 1e-300):
        return np.inf
    return len(y) * math.log(sigma) + (1.0 + 1.0 / xi) * float(np.sum(np.log(z)))


def profile_sigma(xi, y):
    """1-D golden-section minimisation of the GPD nll over sigma at fixed xi."""
    ymax, ymean = float(y.max()), float(y.mean())
    lo = math.log(max(1e-6 * ymean, (-xi * ymax) * (1 + 1e-9) if xi < 0 else 1e-6 * ymean))
    hi = math.log(1e4 * ymean)
    gr = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    c, d = b - gr * (b - a), a + gr * (b - a)
    fc, fd = gpd_nll(xi, math.exp(c), y), gpd_nll(xi, math.exp(d), y)
    for _ in range(300):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = gpd_nll(xi, math.exp(c), y)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = gpd_nll(xi, math.exp(d), y)
        if b - a < 1e-13:
            break
    s = math.exp((a + b) / 2)
    return s, gpd_nll(xi, s, y)


def gpd_mle(y):
    xis = np.concatenate([np.linspace(-0.95, 2.0, 600)])
    best = None
    for xi in xis:
        s, nll = profile_sigma(float(xi), y)
        if best is None or nll < best[2]:
            best = (float(xi), s, nll)
    # local refinement
    lo, hi = best[0] - 0.01, best[0] + 0.01
    for _ in range(60):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        n1 = profile_sigma(m1, y)[1]
        n2 = profile_sigma(m2, y)[1]
        if n1 < n2:
            hi = m2
        else:
            lo = m1
    xi = (lo + hi) / 2
    s, nll = profile_sigma(xi, y)
    if nll > best[2]:
        xi, s, nll = best
    return float(xi), float(s), float(nll)


def gpd_profile_ci(y, nll_min, level=3.841):
    """95% profile-likelihood CI for xi (LR, chi2_1)."""
    grid = np.linspace(-0.99, 4.0, 3000)
    ok = []
    for xi in grid:
        _, nll = profile_sigma(float(xi), y)
        if 2 * (nll - nll_min) <= level:
            ok.append(float(xi))
    return (min(ok), max(ok)) if ok else (float("nan"), float("nan"))


def build_pool_spec(kind, k=POT_K_PRIMARY, xi=None):
    """Return a spec dict with a quantile function Ginv(u) on (0,1)."""
    if kind == "empirical48":
        body = srt.copy()

        def ginv(u):
            return srt[np.minimum((u * 48).astype(np.int64), 47)]

        return {"kind": kind, "ginv": ginv, "upper_endpoint": float(srt[-1]),
                "lower_endpoint": float(srt[0]), "xi": None, "sigma": None,
                "u": None, "k": None,
                "mean": float(srt.mean()), "var": float(srt.var())}

    if kind == "gpd_ext":
        nb = 48 - k
        u = float(srt[nb - 1])
        y = srt[nb:] - u
        if xi is None:
            xi_hat, sig, nll = gpd_mle(y)
        else:
            xi_hat = float(xi)
            sig, nll = profile_sigma(xi_hat, y)
        body = srt[:nb].copy()
        pb = nb / 48.0

        def ginv(uu, u=u, xi_hat=xi_hat, sig=sig, pb=pb, body=body, nb=nb):
            out = np.empty_like(uu)
            m = uu < pb
            out[m] = body[np.minimum((uu[m] * 48).astype(np.int64), nb - 1)]
            q = (uu[~m] - pb) / (1 - pb)
            q = np.minimum(q, 1 - 1e-15)
            if abs(xi_hat) < 1e-10:
                out[~m] = u - sig * np.log(1 - q)
            else:
                out[~m] = u + sig / xi_hat * ((1 - q) ** (-xi_hat) - 1.0)
            return out

        upper = (u + sig / (-xi_hat)) if xi_hat < 0 else float("inf")
        mean = (float(body.sum()) + k * (u + sig / (1 - xi_hat))) / 48.0 \
            if xi_hat < 1 else float("inf")
        return {"kind": kind, "ginv": ginv, "upper_endpoint": float(upper),
                "lower_endpoint": float(srt[0]), "xi": float(xi_hat),
                "sigma": float(sig), "u": u, "k": int(k),
                "exceedances": [float(v) for v in y],
                "nll": float(nll), "mean": float(mean), "var": None}

    if kind == "lognorm_ext":
        lg = np.log(srt)
        mu, sd = float(lg.mean()), float(lg.std(ddof=0))   # MLE

        def _ndtri(p):
            # Acklam inverse normal CDF, |rel err| < 1.15e-9
            a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
                 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
            b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
                 6.680131188771972e+01, -1.328068155288572e+01]
            c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
                 -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
            d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
                 3.754408661907416e+00]
            p = np.asarray(p, dtype=np.float64)
            out = np.empty_like(p)
            pl, ph = 0.02425, 1 - 0.02425
            lo, hi = p < pl, p > ph
            mid = ~(lo | hi)
            q = np.sqrt(-2 * np.log(np.where(lo, p, 0.5)))
            out[lo] = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])[lo] / \
                      ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)[lo]
            q = np.sqrt(-2 * np.log(np.where(hi, 1 - p, 0.5)))
            out[hi] = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])[hi] / \
                       ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)[hi]
            q = np.where(mid, p, 0.5) - 0.5
            r = q * q
            out[mid] = ((((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q)[mid] / \
                       (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)[mid]
            return out

        def ginv(uu, mu=mu, sd=sd):
            return np.exp(mu + sd * _ndtri(uu))

        return {"kind": kind, "ginv": ginv, "upper_endpoint": float("inf"),
                "lower_endpoint": 0.0, "xi": None, "sigma": float(sd),
                "u": None, "k": None, "mu_log": mu, "sd_log": sd,
                "mean": float(math.exp(mu + sd * sd / 2)), "var": None}

    raise ValueError(kind)


# ------------------------------------------------ seed layout (verbatim S1b)
def seed_layout():
    root = np.random.SeedSequence(MASTER_SEED)
    r4 = root.spawn(4)
    v, rep = root.spawn(2)
    n100 = root.spawn(1)[0]
    t50 = root.spawn(1)[0]
    t100 = root.spawn(1)[0]
    return r4[0], v, n100, t50, t100


_, VAL_SEED, _, _, _ = seed_layout()


# ------------------------------------------------------------- headline MC
def spread80(arm, spec, nrep=NREP, seedseq=None, gen=None):
    """Committed code path for empirical48; inverse-CDF for the extended pools."""
    ss = VAL_SEED if seedseq is None else seedseq
    rng = np.random.default_rng(ss) if gen is None else np.random.Generator(gen(ss))
    if spec["kind"] == "empirical48" and gen is None:
        idx = rng.integers(0, pool.size, size=(nrep, 80))     # identical to run_s1b
        F = pool[idx]
    else:
        F = spec["ginv"](rng.random((nrep, 80)))
    sim = F * draw_D(rng, (nrep, 80), arm)
    sp = sim.max(axis=1) / sim.min(axis=1)
    p5, p50, p95 = np.percentile(sp, [5, 50, 95])
    p_ge = float((sp >= OBS).mean())
    return {
        "sim_spread_p5": float(p5), "sim_spread_p50": float(p50),
        "sim_spread_p95": float(p95),
        "p_sim_ge_observed": p_ge,
        "p_se": float(math.sqrt(max(p_ge * (1 - p_ge), 1e-12) / nrep)),
        "brackets_observed": bool(p5 <= OBS <= p95),
        "nrep": nrep,
        "sha256": hashlib.sha256(sp.tobytes()).hexdigest(),
    }


# ------------------------ signal 2: independent non-MC quadrature of P(range)
def p_range_ge_quadrature(arm, spec, M=960_000, nshift=4000, pad=2.0):
    """P(max/min >= OBS) for 80 iid draws of D*F, by numerical quadrature of
    P(range of log(D*F) <= log OBS) = INT 80 f(x) [F(x+r) - F(x)]^79 dx.
    Shares no RNG, no sampler and no estimator with the Monte Carlo."""
    u = (np.arange(M) + 0.5) / M
    lf = np.log(spec["ginv"](u))
    lf = lf[np.isfinite(lf)]
    step = LOG_OBS / nshift
    c = -math.log(arm["d_mean"])          # logD ~ U[c-half, c+half]
    half = arm["half"]
    xlo = float(lf.min()) + c - half - pad
    xhi = float(lf.max()) + c + half + pad
    n = int(math.ceil((xhi - xlo) / step)) + 2 * nshift + 4
    x = xlo + step * np.arange(n)
    # CDF of log F on the grid
    lfs = np.sort(lf)
    C = np.searchsorted(lfs, x, side="right") / lfs.size
    A = np.concatenate([[0.0], np.cumsum(0.5 * (C[1:] + C[:-1])) * step])  # antiderivative

    def A_at(z):
        t = (z - xlo) / step
        i = np.clip(np.floor(t).astype(np.int64), 0, n - 2)
        fr = t - i
        return A[i] * (1 - fr) + A[i + 1] * fr

    FL = (A_at(x - c + half) - A_at(x - c - half)) / (2 * half)
    FL = np.clip(FL, 0.0, 1.0)
    Ct = np.clip(np.interp(x - c + half, x, C) - np.interp(x - c - half, x, C), 0, None)
    fL = Ct / (2 * half)
    Fsh = np.empty_like(FL)
    Fsh[:n - nshift] = FL[nshift:]
    Fsh[n - nshift:] = 1.0
    integ = 80.0 * fL * np.clip(Fsh - FL, 0.0, 1.0) ** 79
    _trap = getattr(np, "trapezoid", None) or np.trapz   # numpy 2 renamed trapz
    p_le = float(_trap(integ, dx=step))
    return {"p_sim_ge_observed_quadrature": float(1.0 - p_le),
            "p_range_le_logobs": p_le, "grid_points": int(n), "M_nodes": int(lf.size)}


# ================================================================ STEP 0
say("=" * 78)
say("STEP 0 -- deterministic support bound (no Monte Carlo)")
say(f"observed 80-net spread OBS = {OBS!r}")
say(f"pool: n=48 mean=1 vF={vF!r} max/min={pool_spread!r}")

specs_primary = {
    "empirical48": build_pool_spec("empirical48"),
    "gpd_ext": build_pool_spec("gpd_ext", k=POT_K_PRIMARY),
    "lognorm_ext": build_pool_spec("lognorm_ext"),
}
step0 = {}
for pname, spec in specs_primary.items():
    for aname, arm in ARMS.items():
        bound = spec["upper_endpoint"] / spec["lower_endpoint"] * arm["ratio"] \
            if np.isfinite(spec["upper_endpoint"]) else float("inf")
        dead = bool(np.isfinite(bound) and bound < OBS)
        step0[f"{aname}|{pname}"] = {
            "max_attainable_spread_bound": (float(bound) if np.isfinite(bound) else None),
            "p_ge_obs_is_exactly_zero": dead}
        say(f"  {aname:14s} x {pname:12s} bound="
            f"{('%.4f' % bound) if np.isfinite(bound) else 'inf':>10s}  "
            f"{'DEAD (P=0 exactly)' if dead else 'alive'}")

g = specs_primary["gpd_ext"]
say(f"  gpd_ext(k={POT_K_PRIMARY}) MLE: xi={g['xi']!r} sigma={g['sigma']!r} u={g['u']!r}")
say(f"  lognorm_ext MLE: mu_log={specs_primary['lognorm_ext']['mu_log']!r} "
    f"sd_log={specs_primary['lognorm_ext']['sd_log']!r}")

decisive_keys = [f"{a}|{p}" for a in ARMS if ARMS[a]["vD"] <= VD_SMALL_MAX
                 for p in ("gpd_ext", "lognorm_ext")]
step0_kills_all = all(step0[k]["p_ge_obs_is_exactly_zero"] for k in decisive_keys)
say(f"STEP-0 verdict: decisive cells {decisive_keys} -> "
    f"{'ALL DEAD (step-0 kill)' if step0_kills_all else 'not all dead; MC required'}")
say("=" * 78)

# ============================================ control reproduction (signal 1)
ctrl = spread80(ARMS["vD_7.57e-04"], specs_primary["empirical48"])
ref = s1_committed["crosschecks"]["m185_spread_validation"]
for a, b in [("sim_spread_p5", "model_sim_spread_p5"),
             ("sim_spread_p50", "model_sim_spread_p50"),
             ("sim_spread_p95", "model_sim_spread_p95"),
             ("p_sim_ge_observed", "p_sim_ge_observed")]:
    assert abs(ctrl[a] - ref[b]) <= 1e-12 * max(abs(ref[b]), 1.0), (a, ctrl[a], ref[b])
say("control reproduction vs committed s1_results.json m185_spread_validation: PASS "
    f"(P5={ctrl['sim_spread_p5']:.6f} P50={ctrl['sim_spread_p50']:.6f} "
    f"P95={ctrl['sim_spread_p95']:.6f} P={ctrl['p_sim_ge_observed']:.6f})")

for aname, s1bname in [("vD_0.0814", "s17_low"), ("vD_0.1220", "s17_high")]:
    r = spread80(ARMS[aname], specs_primary["empirical48"])
    rr = s1b_committed["arms"][s1bname]["spread80"]
    for kk in ("sim_spread_p5", "sim_spread_p50", "sim_spread_p95", "p_sim_ge_observed"):
        assert abs(r[kk] - rr[kk]) <= 1e-12 * max(abs(rr[kk]), 1.0), (aname, kk, r[kk], rr[kk])
    say(f"control reproduction vs committed s1b_results.json {s1bname}.spread80: PASS")

# =================================================== headline MC grid (3 x 3)
say("-" * 78)
grid = {}
for aname, arm in ARMS.items():
    for pname, spec in specs_primary.items():
        key = f"{aname}|{pname}"
        if step0[key]["p_ge_obs_is_exactly_zero"]:
            grid[key] = {"skipped_step0_dead": True,
                         "p_sim_ge_observed": 0.0, "p_se": 0.0,
                         "max_attainable_spread_bound":
                             step0[key]["max_attainable_spread_bound"]}
            say(f"{key:28s} P(sim>=OBS)=0 EXACT (step-0 bound "
                f"{step0[key]['max_attainable_spread_bound']:.4f} < {OBS:.4f})")
            continue
        r = spread80(arm, spec)
        rep = spread80(arm, spec)                       # signal 4: bitwise repeat
        r["bitwise_repeat_ok"] = bool(rep["sha256"] == r["sha256"])
        grid[key] = r
        say(f"{key:28s} P5={r['sim_spread_p5']:8.3f} P50={r['sim_spread_p50']:8.3f} "
            f"P95={r['sim_spread_p95']:9.3f}  P(sim>=OBS)={r['p_sim_ge_observed']:.4f} "
            f"(SE {r['p_se']:.4f}) brackets={r['brackets_observed']} "
            f"bitrepeat={r['bitwise_repeat_ok']}")

# ============================================== GATE A on the decisive cells
gateA_cells = {}
for key in decisive_keys:
    p = grid[key]["p_sim_ge_observed"]
    gateA_cells[key] = {"p_sim_ge_observed": p,
                        "inside_gate_interval": bool(GATE_LO <= p <= GATE_HI)}
gateA_pass = any(v["inside_gate_interval"] for v in gateA_cells.values())
say("-" * 78)
say(f"GATE A (decisive cells vD<={VD_SMALL_MAX} x heavy-F, interval "
    f"[{GATE_LO},{GATE_HI}]): "
    f"{'REVIVED_PASS' if gateA_pass else 'KILL_CONFIRMED'}")
for k, v in gateA_cells.items():
    say(f"   {k:28s} P={v['p_sim_ge_observed']:.4f} inside={v['inside_gate_interval']}")

# ================================ signal 2 + 3 on decisive (and control) cells
verify_keys = decisive_keys + ["vD_7.57e-04|empirical48"]
verification = {}
for key in verify_keys:
    aname, pname = key.split("|")
    arm, spec = ARMS[aname], specs_primary[pname]
    if step0[key]["p_ge_obs_is_exactly_zero"]:
        verification[key] = {"step0_exact_zero": True}
        say(f"verify {key:28s}: step-0 exact zero, no MC to cross-check")
        continue
    q = p_range_ge_quadrature(arm, spec)
    conf = spread80(arm, spec, nrep=NREP_CONFIRM,
                    seedseq=np.random.SeedSequence(987654321),
                    gen=np.random.Philox)
    d_quad = abs(q["p_sim_ge_observed_quadrature"] - grid[key]["p_sim_ge_observed"])
    se_c = math.sqrt(max(grid[key]["p_se"] ** 2 + conf["p_se"] ** 2, 1e-24))
    d_conf = abs(conf["p_sim_ge_observed"] - grid[key]["p_sim_ge_observed"])
    verification[key] = {
        "mc": grid[key]["p_sim_ge_observed"],
        "quadrature": q["p_sim_ge_observed_quadrature"],
        "abs_diff_quadrature": d_quad,
        "quadrature_ok_0p01": bool(d_quad <= 0.01),
        "philox_invcdf_200k": conf["p_sim_ge_observed"],
        "abs_diff_confirm": d_conf, "combined_se": se_c,
        "confirm_ok_3se": bool(d_conf <= 3 * se_c),
        "confirm_p5_p50_p95": [conf["sim_spread_p5"], conf["sim_spread_p50"],
                               conf["sim_spread_p95"]],
        "quadrature_detail": q,
    }
    say(f"verify {key:28s}: MC={grid[key]['p_sim_ge_observed']:.4f} "
        f"quad={q['p_sim_ge_observed_quadrature']:.4f} (|d|={d_quad:.4f}) "
        f"Philox200k={conf['p_sim_ge_observed']:.4f} (|d|={d_conf:.4f}, 3SE={3*se_c:.4f})")

# ============================================== GATE B -- the tail-index axis
say("-" * 78)
say("GATE B -- tail-index (xi) sweep at k=12")
nb = 48 - POT_K_PRIMARY
y_exc = srt[nb:] - srt[nb - 1]
xi_hat, sig_hat, nll_min = gpd_mle(y_exc)
ci_lo, ci_hi = gpd_profile_ci(y_exc, nll_min)
say(f"  MLE xi={xi_hat:.5f} sigma={sig_hat:.5f}  nll={nll_min:.5f}; "
    f"95% profile CI for xi = [{ci_lo:.4f}, {ci_hi:.4f}]")
xi_sweep = {}
for xi in XI_GRID:
    spec = build_pool_spec("gpd_ext", k=POT_K_PRIMARY, xi=xi)
    row = {"sigma_profile": spec["sigma"],
           "upper_endpoint": (spec["upper_endpoint"]
                              if np.isfinite(spec["upper_endpoint"]) else None),
           "nll": spec["nll"], "lr_stat_vs_mle": 2 * (spec["nll"] - nll_min),
           "inside_95_profile_ci": bool(2 * (spec["nll"] - nll_min) <= 3.841)}
    for aname, arm in ARMS.items():
        bound = (spec["upper_endpoint"] / spec["lower_endpoint"] * arm["ratio"]
                 if np.isfinite(spec["upper_endpoint"]) else float("inf"))
        if np.isfinite(bound) and bound < OBS:
            row[aname] = {"p_sim_ge_observed": 0.0, "step0_exact_zero": True}
        else:
            rr = spread80(arm, spec)
            row[aname] = {"p_sim_ge_observed": rr["p_sim_ge_observed"],
                          "p5": rr["sim_spread_p5"], "p50": rr["sim_spread_p50"],
                          "p95": rr["sim_spread_p95"], "step0_exact_zero": False}
    xi_sweep[f"{xi}"] = row
    say(f"  xi={xi:+.2f} sigma={spec['sigma']:.4f} LR={row['lr_stat_vs_mle']:7.3f} "
        f"inCI={str(row['inside_95_profile_ci']):5s} | "
        + " ".join(f"{a.split('_')[1]}:P={row[a]['p_sim_ge_observed']:.3f}" for a in ARMS))

small_arm = [a for a in ARMS if ARMS[a]["vD"] <= VD_SMALL_MAX][0]
in_gate_xis = [float(x) for x, r in xi_sweep.items()
               if GATE_LO <= r[small_arm]["p_sim_ge_observed"] <= GATE_HI]
xi_star = min(in_gate_xis) if in_gate_xis else None
gateB_rescues = bool(xi_star is not None and ci_lo <= xi_star <= ci_hi)
say(f"  xi* (smallest xi with P in [{GATE_LO},{GATE_HI}] at {small_arm}) = {xi_star}")
say(f"  GATE B: {'RESCUES (xi* inside 95% profile CI)' if gateB_rescues else 'FAILS TO RESCUE'}")

# ------------------------------------------------------ annex: POT threshold
annex = {}
for k in POT_K_ANNEX:
    spec = build_pool_spec("gpd_ext", k=k)
    row = {"k": k, "u": spec["u"], "xi_mle": spec["xi"], "sigma": spec["sigma"],
           "upper_endpoint": (spec["upper_endpoint"]
                              if np.isfinite(spec["upper_endpoint"]) else None)}
    for aname, arm in ARMS.items():
        bound = (spec["upper_endpoint"] / spec["lower_endpoint"] * arm["ratio"]
                 if np.isfinite(spec["upper_endpoint"]) else float("inf"))
        if np.isfinite(bound) and bound < OBS:
            row[aname] = {"p_sim_ge_observed": 0.0, "step0_exact_zero": True}
        else:
            rr = spread80(arm, spec)
            row[aname] = {"p_sim_ge_observed": rr["p_sim_ge_observed"],
                          "p50": rr["sim_spread_p50"], "step0_exact_zero": False}
    annex[f"k={k}"] = row
    say(f"  annex k={k}: xi_mle={spec['xi']:+.4f} | "
        + " ".join(f"{a.split('_')[1]}:P={row[a]['p_sim_ge_observed']:.3f}" for a in ARMS))

# --------------------------------- side report: vF under each F-pool variant
vF_report = {}
for pname, spec in specs_primary.items():
    u = (np.arange(400_000) + 0.5) / 400_000
    f = spec["ginv"](u)
    f = f / f.mean()
    vF_report[pname] = {"vF_quantile_quadrature": float(f.var()),
                        "max_over_min_of_quantile_nodes": float(f.max() / f.min())}
    say(f"  vF({pname}) = {vF_report[pname]['vF_quantile_quadrature']:.5f} "
        f"(committed empirical-48 vF = {vF:.5f})")

# ------------------------------------------------------------------ verdict
if gateA_pass:
    gate_result = "REVIVED_PASS"
elif gateB_rescues:
    gate_result = "INCONCLUSIVE"
else:
    gate_result = "KILL_CONFIRMED"
say("=" * 78)
say(f"FINAL: GATE A = {'PASS' if gateA_pass else 'KILL'}; "
    f"GATE B = {'RESCUES' if gateB_rescues else 'FAILS TO RESCUE'}; "
    f"gate_result = {gate_result}")

results = {
    "experiment": "gm_u3_grid",
    "date": "2026-08-10",
    "item": "U3 tail-model fidelity -- rotation-tail / difficulty-dispersion identifiability",
    "predeclaration": "PREDECLARATION.md (this directory)",
    "observed_80net_spread": OBS,
    "calibration": {"vF_empirical48": vF, "pool_max_over_min": pool_spread,
                    "pool_sorted": [float(v) for v in srt]},
    "arms": {k: v for k, v in ARMS.items()},
    "pool_specs": {p: {kk: vv for kk, vv in s.items() if kk != "ginv"}
                   for p, s in specs_primary.items()},
    "step0_support_bounds": step0,
    "step0_kills_all_decisive": step0_kills_all,
    "control_reproduction": {
        "s1_m185_spread_validation": {k: ctrl[k] for k in
                                      ("sim_spread_p5", "sim_spread_p50",
                                       "sim_spread_p95", "p_sim_ge_observed")},
        "committed_reference": ref,
        "s1b_s17_low_s17_high": "asserted equal to committed at rel tol 1e-12",
        "passed": True},
    "grid": grid,
    "gate_A": {"interval": [GATE_LO, GATE_HI], "vD_max": VD_SMALL_MAX,
               "decisive_cells": gateA_cells, "pass": gateA_pass},
    "gate_B": {"xi_mle": xi_hat, "sigma_mle": sig_hat, "nll_min": nll_min,
               "profile_ci_95": [ci_lo, ci_hi], "sweep": xi_sweep,
               "xi_star": xi_star, "rescues": gateB_rescues},
    "annex_pot_threshold": annex,
    "vF_by_pool_variant": vF_report,
    "two_signal_verification": verification,
    "gate_result": gate_result,
    "runtime_seconds": round(time.time() - t0, 1),
    "inputs": [P2_PATH, S1_PATH, S1B_PATH, S17_PATH, M185_PATH, A1B_PATH],
}
with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=1)
with open(EXP + r"\gm_u3_grid\run.log", "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")
say(f"wrote {OUT_JSON}  [{time.time()-t0:.1f}s]")
