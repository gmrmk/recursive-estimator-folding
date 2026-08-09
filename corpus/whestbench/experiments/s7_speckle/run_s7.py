"""S7 runner (ledger id s7_wavepacket_speckle_correlation).

Wave-packet-through-weight-crystal model: is the estimator's per-direction
residual field defect-scattering speckle with the mean-field deep-ReLU
dispersion relation?

P1 (gated): angular correlation C_r(theta) of the residual field decays with
xi_measured within a factor 2 of the depth-32 mean-field prediction.
P2 (evidence, not gated): per-direction residual energy distribution vs
Exp(1) (fully-developed complex speckle / MB) and chi^2_1 = Gamma(1/2,2)
(real-amplitude speckle -- the physically correct null for a real field).

MEAN-FIELD (predeclared, closed form): c_{l+1} = f(c_l),
f(c) = (sqrt(1-c^2) + c*(pi - arccos c)) / pi, iterated 32 layers from
c_0 = cos(theta).  Residual (mean-removed) normalization choice, documented:
    C_pred(theta) = (c_32(cos theta) - m2) / (1 - m2),  m2 = c_32(0),
because the probe-set mean removal subtracts the component common to all
(near-orthogonal, d=256) directions, whose scale is the theta=90deg plateau
c_32(0).  xi_meanfield = theta where C_pred = 1/2 (1/e also stated).

MEASUREMENT: 3 He nets (seeds 101,202,303; width 256, depth 32) via the
shared constructor he_mlp_weights() in n8a_rqmc_kerdock/run_n8a_gates.py
(imported read-only, never edited); first layer pre-rotated by
haar_rotation(900000 + net*1000 + 0) exactly as the estimator harness does.
Probes: per theta in {0.5,1,2,5,10,20,45,90} deg, 500 great-circle pairs
(u, u_theta), u Haar-random unit; all forwards float32.
r(u) = ybar(u) - m, ybar = neuron-averaged final post-ReLU output.
C_r(theta) = Pearson corr over the 500 pairs (Pearson is shift-invariant, so
the mean-removal constant does not enter C_r; it enters only the prediction
normalization and the energies).

xi_measured: last crossing of raw C_r(theta) = 1/2, linear interpolation in
log(theta); censored at the grid ends if no crossing.  Coherent-monotone
check: no consecutive increase of C_r exceeding 2x the pooled Fisher SE.

PREDECLARED GATES: PASS = xi ratio within [1/2, 2] on >=2/3 nets AND
coherent monotone C_r.  KILL = off by >5x or incoherent.  2x-5x
INCONCLUSIVE.  P2 reported as evidence only.

TWO-SIGNAL CHECKS built in:
  (i)  arccos kernel f(c) re-derived two ways (algebraic identity
       c*(pi-arccos c) = c*pi/2 + c*arcsin c) and Monte-Carlo checked
       against E[relu(x)relu(y)] on 2e6 bivariate normals;
  (ii) C_r repeated at 20deg and 45deg with an independent fresh pair set
       (different probe seed) on every net;
  (iii) vectorized erf (A&S 7.1.26) cross-checked against math.erf.

DEVIATIONS FROM TASK TEXT (recorded loudly, none silent):
  D1. Task says "~2,000 random great-circle arc pairs" but also "for each
      theta, ~500 pairs" with 8 thetas; the per-theta spec governs ->
      4,000 pairs total per net.
  D2. theta=90deg is excluded from the max-ratio-deviation statistic
      because C_pred(90deg)=0 exactly under the predeclared normalization
      (ratio undefined); it still enters the monotonicity/coherence check.
  D3. c_32 = f applied exactly 32 times to cos(theta), as predeclared.  The
      preactivation-count alternative (31 applications) and the post-ReLU
      covariance kernel variant h(c)=(sqrt(1-c^2)+c(pi-arccos c)-1)/(pi-1)
      are reported as robustness rows only, never gated.

FIREWALL: synthetic He nets only; frozen sources imported, never edited;
kerdock_phases.npz read-only; writes confined to s7_speckle/; no git.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N8A_DIR = HERE.parent / "n8a_rqmc_kerdock"
sys.path.insert(0, str(N8A_DIR))
import run_n8a_gates as n8a  # noqa: E402  (frozen source, read-only import)

WIDTH, DEPTH = 256, 32
NET_SEEDS = (101, 202, 303)
THETAS_DEG = (0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 45.0, 90.0)
PAIRS_PER_THETA = 500
PAIR_SEED_BASE = 640_000       # probe pairs: default_rng(PAIR_SEED_BASE + net)
REPEAT_SEED_BASE = 740_000     # independent repeat pairs (two-signal check)
REPEAT_THETAS_DEG = (20.0, 45.0)
BOOT_DRAWS = 1000
BOOT_SEED = 2026_0809
MC_KERNEL_N = 2_000_000
MC_KERNEL_SEED = 550_000


# ------------------------------------------------------------- mean field
def f_kernel(c: np.ndarray) -> np.ndarray:
    """Variance-normalized arccos kernel (predeclared form)."""
    c = np.clip(c, -1.0, 1.0)
    return (np.sqrt(1.0 - c * c) + c * (math.pi - np.arccos(c))) / math.pi


def f_kernel_alt(c: np.ndarray) -> np.ndarray:
    """Same kernel via arcsin identity -- independent implementation path."""
    c = np.clip(c, -1.0, 1.0)
    return (np.sqrt(1.0 - c * c) + c * np.arcsin(c)) / math.pi + 0.5 * c

def h_postrelu(c: np.ndarray) -> np.ndarray:
    """Post-ReLU correlation (mean-removed) given preactivation corr c."""
    c = np.clip(c, -1.0, 1.0)
    return (np.sqrt(1.0 - c * c) + c * (math.pi - np.arccos(c)) - 1.0) / (
        math.pi - 1.0
    )


def iterate_kernel(c0: np.ndarray, layers: int) -> np.ndarray:
    c = np.asarray(c0, dtype=np.float64)
    for _ in range(layers):
        c = f_kernel(c)
    return c


def meanfield_block() -> dict:
    # Two-signal check (i): algebraic identity of the two kernel forms.
    grid = np.linspace(-1.0, 1.0, 20001)
    kernel_form_maxdiff = float(np.max(np.abs(f_kernel(grid) - f_kernel_alt(grid))))
    if kernel_form_maxdiff > 1e-12:
        raise RuntimeError(f"kernel identity check failed: {kernel_form_maxdiff}")

    # Monte-Carlo check of f(c) at c in {0, 0.5, 0.9}.
    rng = np.random.default_rng(MC_KERNEL_SEED)
    mc_rows = []
    for c in (0.0, 0.5, 0.9):
        x = rng.standard_normal(MC_KERNEL_N)
        y = c * x + math.sqrt(1.0 - c * c) * rng.standard_normal(MC_KERNEL_N)
        est = float(
            np.mean(np.maximum(x, 0.0) * np.maximum(y, 0.0))
            / np.mean(np.maximum(x, 0.0) ** 2)
        )
        mc_rows.append(
            {"c": c, "f_closed": float(f_kernel(np.array(c))), "f_mc": est,
             "abs_diff": abs(est - float(f_kernel(np.array(c))))}
        )
        if abs(est - float(f_kernel(np.array(c)))) > 3e-3:
            raise RuntimeError(f"MC kernel check failed at c={c}: {est}")

    thetas_rad = np.deg2rad(np.array(THETAS_DEG))
    m2 = float(iterate_kernel(np.array(0.0), DEPTH))          # c_32(cos 90deg)
    c32_probe = iterate_kernel(np.cos(thetas_rad), DEPTH)
    c_pred_probe = (c32_probe - m2) / (1.0 - m2)

    # Tabulation grid over [0, pi/2].
    grid_deg = np.arange(0.0, 90.0 + 1e-9, 2.5)
    c32_grid = iterate_kernel(np.cos(np.deg2rad(grid_deg)), DEPTH)
    c_pred_grid = (c32_grid - m2) / (1.0 - m2)

    # Robustness variants (D3): 31 applications; post-ReLU kernel on top.
    m2_31 = float(iterate_kernel(np.array(0.0), DEPTH - 1))
    c31_probe = iterate_kernel(np.cos(thetas_rad), DEPTH - 1)
    c_pred31_probe = (c31_probe - m2_31) / (1.0 - m2_31)
    hm2 = float(h_postrelu(np.array(m2_31)))
    c_predh_probe = (h_postrelu(c31_probe) - hm2) / (1.0 - hm2)

    def crossing(level: float) -> float:
        # C_pred is continuous & monotone decreasing in theta; bisect.
        lo, hi = 1e-4, math.pi / 2
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            val = (float(iterate_kernel(np.array(math.cos(mid)), DEPTH)) - m2) / (
                1.0 - m2
            )
            if val > level:
                lo = mid
            else:
                hi = mid
        return math.degrees(0.5 * (lo + hi))

    xi_half = crossing(0.5)
    xi_1e = crossing(1.0 / math.e)
    return {
        "kernel_form_maxdiff": kernel_form_maxdiff,
        "kernel_mc_check": mc_rows,
        "m2_plateau_c32_at_90deg": m2,
        "xi_meanfield_half_deg": xi_half,
        "xi_meanfield_1e_deg": xi_1e,
        "probe_thetas_deg": list(THETAS_DEG),
        "c32_probe": [float(v) for v in c32_probe],
        "c_pred_probe": [float(v) for v in c_pred_probe],
        "c_pred_probe_31layer_variant": [float(v) for v in c_pred31_probe],
        "c_pred_probe_postrelu_variant": [float(v) for v in c_predh_probe],
        "table_grid_deg": [float(v) for v in grid_deg],
        "table_c32": [float(v) for v in c32_grid],
        "table_c_pred": [float(v) for v in c_pred_grid],
    }


# ------------------------------------------------------------ measurement
def make_pairs(rng: np.random.Generator, theta_rad: float, n: int):
    u = rng.standard_normal((n, WIDTH))
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    v = rng.standard_normal((n, WIDTH))
    v -= (np.sum(v * u, axis=1, keepdims=True)) * u
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    ut = math.cos(theta_rad) * u + math.sin(theta_rad) * v
    return u.astype(np.float32), ut.astype(np.float32)


def forward_field(weights, first_eff: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Per-direction final post-ReLU activations, float32, shape (n, WIDTH)."""
    act = np.maximum(points @ first_eff, np.float32(0.0))
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    return act


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.corrcoef(a, b)[0, 1])


def crossing_logtheta(thetas_deg, c_vals, level=0.5):
    """Last crossing of level, linear in log(theta). Returns (xi, censored)."""
    t = np.asarray(thetas_deg, dtype=float)
    c = np.asarray(c_vals, dtype=float)
    if c[0] < level:
        return float(t[0]), "censored_low"
    hits = [i for i in range(len(c) - 1) if c[i] >= level > c[i + 1]]
    if not hits:
        return float(t[-1]), "censored_high"
    i = hits[-1]
    lt = np.log(t)
    frac = (c[i] - level) / (c[i] - c[i + 1])
    return float(np.exp(lt[i] + frac * (lt[i + 1] - lt[i]))), "ok"


# --------------------------------------------------------------- energies
_ERF_P = 0.3275911
_ERF_A = (0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429)


def erf_vec(x: np.ndarray) -> np.ndarray:
    """A&S 7.1.26, |eps|<=1.5e-7; cross-checked against math.erf below."""
    s = np.sign(x)
    ax = np.abs(x)
    t = 1.0 / (1.0 + _ERF_P * ax)
    poly = t * (_ERF_A[0] + t * (_ERF_A[1] + t * (_ERF_A[2] + t * (
        _ERF_A[3] + t * _ERF_A[4]))))
    return s * (1.0 - poly * np.exp(-ax * ax))


def _check_erf() -> float:
    xs = np.linspace(0.0, 5.0, 1001)
    ref = np.array([math.erf(v) for v in xs])
    d = float(np.max(np.abs(erf_vec(xs) - ref)))
    if d > 2e-7:
        raise RuntimeError(f"erf implementation check failed: {d}")
    return d


def ks_distance(e: np.ndarray, cdf) -> float:
    xs = np.sort(np.asarray(e, dtype=np.float64))
    n = xs.size
    F = cdf(xs)
    lo = np.arange(0, n, dtype=np.float64) / n
    hi = np.arange(1, n + 1, dtype=np.float64) / n
    return float(max(np.max(F - lo), np.max(hi - F)))


def cdf_exp1(x):
    return 1.0 - np.exp(-np.maximum(x, 0.0))


def cdf_chi2_1(x):
    return erf_vec(np.sqrt(np.maximum(x, 0.0) / 2.0))


def energy_stats(e: np.ndarray) -> dict:
    e = np.asarray(e, dtype=np.float64)
    e = e / e.mean()
    return {
        "n": int(e.size),
        "ks_exp1": ks_distance(e, cdf_exp1),
        "ks_chi2_1": ks_distance(e, cdf_chi2_1),
        "var": float(e.var()),
        "moment_shape_k": float(1.0 / e.var()),  # Gamma(k): Exp->1, chi2_1->0.5
    }


def perneuron_pooled_stats(res: np.ndarray) -> dict:
    """Per-neuron normalized energies pooled over live neurons.

    Dead neurons (final activation identically zero over the probe set ->
    zero residual energy) are excluded: their 0/0 normalization is undefined
    and they carry no speckle signal.  Live count recorded.
    """
    en = res ** 2
    me = en.mean(axis=0)
    live = me > 0.0
    en = en[:, live] / me[live][None, :]
    out = energy_stats(en.ravel())
    out["n_neurons_live"] = int(live.sum())
    out["n_neurons_dead"] = int((~live).sum())
    return out


# ---------------------------------------------------------------- per net
def run_net(net_seed: int, mf: dict, kerdock_base: np.ndarray) -> dict:
    t0 = time.perf_counter()
    weights = n8a.he_mlp_weights(net_seed)
    rotation = n8a.haar_rotation(900_000 + net_seed * 1_000 + 0)
    first_eff = (rotation.T @ weights[0]).astype(np.float32)

    # -- great-circle pair probes
    rng = np.random.default_rng(PAIR_SEED_BASE + net_seed)
    ybar_u, ybar_t, act_u_all = {}, {}, []
    for th in THETAS_DEG:
        u, ut = make_pairs(rng, math.radians(th), PAIRS_PER_THETA)
        au = forward_field(weights, first_eff, u)
        at = forward_field(weights, first_eff, ut)
        ybar_u[th] = au.astype(np.float64).mean(axis=1)
        ybar_t[th] = at.astype(np.float64).mean(axis=1)
        act_u_all.append(au)
    c_meas = np.array([pearson(ybar_u[t], ybar_t[t]) for t in THETAS_DEG])
    se = 1.0 / math.sqrt(PAIRS_PER_THETA - 3)  # Fisher-z scale, approx on r

    # coherence: no consecutive increase > 2 * pooled SE
    incr = np.diff(c_meas)
    coherent = bool(np.all(incr <= 2.0 * se * math.sqrt(2.0)))

    xi_raw, cens_raw = crossing_logtheta(THETAS_DEG, c_meas, 0.5)
    c_norm = (c_meas - c_meas[-1]) / (c_meas[0] - c_meas[-1])
    xi_norm, cens_norm = crossing_logtheta(THETAS_DEG, c_norm, 0.5)

    # bootstrap CI on xi (raw definition, primary)
    brng = np.random.default_rng(BOOT_SEED + net_seed)
    boot_xi = []
    for _ in range(BOOT_DRAWS):
        cb = []
        for th in THETAS_DEG:
            idx = brng.integers(0, PAIRS_PER_THETA, PAIRS_PER_THETA)
            cb.append(pearson(ybar_u[th][idx], ybar_t[th][idx]))
        boot_xi.append(crossing_logtheta(THETAS_DEG, cb, 0.5)[0])
    xi_ci = (float(np.percentile(boot_xi, 2.5)),
             float(np.percentile(boot_xi, 97.5)))

    # two-signal check (ii): independent fresh pair sets at 20 and 45 deg
    rrng = np.random.default_rng(REPEAT_SEED_BASE + net_seed)
    repeats = []
    for th in REPEAT_THETAS_DEG:
        u, ut = make_pairs(rrng, math.radians(th), PAIRS_PER_THETA)
        cu = forward_field(weights, first_eff, u).astype(np.float64).mean(axis=1)
        ct = forward_field(weights, first_eff, ut).astype(np.float64).mean(axis=1)
        c_rep = pearson(cu, ct)
        c_main = float(c_meas[THETAS_DEG.index(th)])
        repeats.append({
            "theta_deg": th, "c_main": c_main, "c_repeat": c_rep,
            "abs_diff": abs(c_rep - c_main),
            "within_2se_joint": bool(abs(c_rep - c_main)
                                     <= 2.0 * se * math.sqrt(2.0)),
        })

    # ratio deviation vs prediction (D2: 90deg excluded)
    c_pred = np.array(mf["c_pred_probe"])
    mask = np.array(THETAS_DEG) < 89.0
    with np.errstate(divide="ignore"):
        ratios = np.maximum(c_meas[mask] / c_pred[mask],
                            c_pred[mask] / c_meas[mask])
    max_ratio_dev = float(np.max(ratios))

    # -- P2 energies on the Haar u-legs (4000 near-uniform directions)
    yu = np.concatenate([ybar_u[t] for t in THETAS_DEG])
    r_u = yu - yu.mean()
    p2_dir = energy_stats(r_u ** 2)
    act_u = np.concatenate(act_u_all, axis=0).astype(np.float64)  # (4000,256)
    res_u = act_u - act_u.mean(axis=0, keepdims=True)
    p2_neuron = perneuron_pooled_stats(res_u)
    vec_e = (res_u ** 2).mean(axis=1)
    p2_vector = energy_stats(vec_e)

    # -- P2 on the actual design set (antipodally doubled Kerdock, rotated
    #    via the same effective first layer)
    kd = np.concatenate([kerdock_base, -kerdock_base], axis=0)
    act_k = forward_field(weights, first_eff, kd)
    ybar_k = act_k.astype(np.float64).mean(axis=1)
    r_k = ybar_k - ybar_k.mean()
    p2_kerdock_dir = energy_stats(r_k ** 2)
    res_k = act_k.astype(np.float64)
    res_k -= res_k.mean(axis=0, keepdims=True)
    p2_kerdock_neuron = perneuron_pooled_stats(res_k)
    del act_k, res_k

    wall = time.perf_counter() - t0
    row = {
        "net_seed": net_seed,
        "c_meas": [float(v) for v in c_meas],
        "se_per_theta": se,
        "coherent_monotone": coherent,
        "xi_measured_deg_raw": xi_raw, "xi_raw_censoring": cens_raw,
        "xi_measured_deg_norm": xi_norm, "xi_norm_censoring": cens_norm,
        "xi_boot_ci95_deg": xi_ci,
        "xi_ratio_meas_over_mf": xi_raw / mf["xi_meanfield_half_deg"],
        "max_ratio_deviation_excl90": max_ratio_dev,
        "repeat_checks": repeats,
        "p2_direction_energy_haar": p2_dir,
        "p2_perneuron_pooled_haar": p2_neuron,
        "p2_vector_energy_haar": p2_vector,
        "p2_direction_energy_kerdock": p2_kerdock_dir,
        "p2_perneuron_pooled_kerdock": p2_kerdock_neuron,
        "wall_s": round(wall, 1),
    }
    print(
        f"net {net_seed}: C_r={np.array2string(c_meas, precision=3)}  "
        f"xi={xi_raw:.1f}deg (CI [{xi_ci[0]:.1f},{xi_ci[1]:.1f}])  "
        f"ratio={row['xi_ratio_meas_over_mf']:.2f}  coherent={coherent}  "
        f"({wall:.0f}s)", flush=True)
    return row


def design_spacing(kerdock_base: np.ndarray) -> dict:
    """Min inter-direction angle of the design (frames 0..5 spot check +
    the known Kerdock cross-frame coherence 1/16)."""
    frames = kerdock_base.reshape(126, WIDTH, WIDTH)
    unit = frames / np.linalg.norm(frames, axis=2, keepdims=True)
    max_abs_cos = 0.0
    for i in range(6):
        for j in range(i, 6):
            g = np.abs(unit[i] @ unit[j].T)
            if i == j:
                np.fill_diagonal(g, 0.0)
            max_abs_cos = max(max_abs_cos, float(g.max()))
    return {
        "max_abs_cos_frames_0_5": max_abs_cos,
        "min_angle_deg": math.degrees(math.acos(max_abs_cos)),
        "within_frame_angle_deg": 90.0,
        "note": "cross-frame coherence expected 1/16 = 0.0625 (Kerdock)",
    }


def main() -> None:
    t_start = time.perf_counter()
    erf_dev = _check_erf()
    print("mean-field derivation...", flush=True)
    mf = meanfield_block()
    print(
        f"  m2=c32(90deg)={mf['m2_plateau_c32_at_90deg']:.4f}  "
        f"xi_mf(half)={mf['xi_meanfield_half_deg']:.2f}deg  "
        f"xi_mf(1/e)={mf['xi_meanfield_1e_deg']:.2f}deg", flush=True)

    kerdock = n8a.load_kerdock_directions()  # read-only frozen asset
    spacing = design_spacing(kerdock)
    print(
        f"design spacing: min angle {spacing['min_angle_deg']:.2f}deg "
        f"(max |cos| {spacing['max_abs_cos_frames_0_5']:.4f})", flush=True)

    nets = [run_net(s, mf, kerdock) for s in NET_SEEDS]

    ratios = [n["xi_ratio_meas_over_mf"] for n in nets]
    within2 = sum(1 for r in ratios if 0.5 <= r <= 2.0)
    coherent_all = all(n["coherent_monotone"] for n in nets)
    off5 = any(r > 5.0 or r < 0.2 for r in ratios)
    if within2 >= 2 and coherent_all:
        verdict = "PASS"
    elif off5 or not coherent_all:
        verdict = "KILL"
    else:
        verdict = "INCONCLUSIVE"

    results = {
        "ledger_id": "s7_wavepacket_speckle_correlation",
        "date": "2026-08-09",
        "gates": {
            "pass_rule": "xi ratio in [0.5,2] on >=2/3 nets AND coherent "
                         "monotone C_r",
            "kill_rule": ">5x off or incoherent; 2x-5x inconclusive",
            "nets_within_factor2": within2,
            "coherent_all": coherent_all,
        },
        "deviations": [
            "D1: 500 pairs/theta x 8 thetas = 4000 pairs (per-theta spec "
            "governs over the '~2,000 pairs' aggregate in the task text)",
            "D2: theta=90deg excluded from max-ratio-deviation "
            "(C_pred(90)=0 exactly under the mean-removed normalization)",
            "D3: c_32 = f^32(cos theta) as predeclared; 31-layer and "
            "post-ReLU-kernel variants reported unGated",
        ],
        "erf_impl_maxdev_vs_math_erf": erf_dev,
        "meanfield": mf,
        "design_spacing": spacing,
        "nets": nets,
        "xi_ratios": ratios,
        "verdict": verdict,
        "total_wall_s": round(time.perf_counter() - t_start, 1),
    }
    (HERE / "s7_results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nVERDICT: {verdict}  xi_ratios={[round(r,3) for r in ratios]}")
    print(f"results written to {HERE / 's7_results.json'}", flush=True)


if __name__ == "__main__":
    main()
