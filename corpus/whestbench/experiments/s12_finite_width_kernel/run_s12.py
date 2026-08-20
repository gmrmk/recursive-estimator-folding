"""S12 — finite-width-corrected correlation kernel capstone (writeup, non-candidate).

Ledger id: s12_finite_width_kernel_capstone. Pure math + comparison to committed
S7/S8 data. No nets are run except the EXACT-in-distribution scalar kernel chain
for route (b) verification (bias-free He ReLU diagonal-kernel law is exactly a
scalar recursion; see route (b) notes). Reads committed s7_results.json and
s8_results.json READ-ONLY. Writes only into this directory.

PREDECLARED OPERATIONALIZATIONS (fixed here, before the first run; the task text
+ research brief research_physics_depth_finitewidth_20260810.md govern):

Route (a) — Jakub-Nica finite-width angle flow (arXiv:2302.09712, Approx. 1):
  A1. Primary recursion (GATED):  ln sin^2 th_{l+1} = ln sin^2 th_l - (2/(3pi)) th_l - rho(n)
      with the brief's full rho(n) = ln((n+5)/(n-1)) - 10n/(n+5)^2 + 6n/(n-1)^2
      (= 2/n + O(1/n^2)); n = 256, D = 32 steps, th_0 in the 8 S7 probe angles.
  A2. sin^2 -> correlation mapping (documented + justified in the verdict):
      raw output correlation c_raw(th0) := cos th_32(th0) (th_l IS the angle
      between the two activation vectors, so cos of it IS the raw correlation);
      normalized prediction uses S7's committed mean-removed normalization with
      the flow's own 90-deg plateau as the coherent component:
        c_pred_fw(th0) = (cos th_32(th0) - cos th_32(90deg)) / (1 - cos th_32(90deg)).
      (Verified consistent: applying the same functional to S7's committed
      mean-field c32 values reproduces S7's committed c_pred to ~1e-12.)
  A3. CI for the hit/miss count (S7 json carries no per-angle CI; task fallback
      rule applied): primary half-width = 2 * se_per_theta = 2*0.0448561 =
      0.0897123 (>= the +-0.045 floor). Sensitivity rows at +-0.045 (1 SE) and
      +-0.1269 (2*sqrt2*SE, the "joint" scale) are REPORTED, not gated.
  A4. Curve gate: >= 5 of 7 angles (90 deg excluded) inside the primary CI on
      >= 2 of 3 nets.
  A5. Perturbation transmission: T_l := d th_{l+1} / d th_l along the flow,
      analytic form T_l = exp(-(b*th_l+rho)/2) * (cos th_l - (b/2) sin th_l)/cos th_{l+1},
      b = 2/(3pi)  (checked against central finite differences).
      "Typical value" (GATED) := geometric mean of T_l over l = 1..31 of the
      th_0 = 90 deg trajectory (the S8 probe design is mutually ~90 deg, so the
      ambient S8 trajectory starts at 90 deg; l = 0 is excluded because the
      sin^2 parameterization folds exactly at th = pi/2, making dth_1/dth_0
      there a sign artifact — the l=0 value is reported separately).
      Sensitivity (REPORTED): arithmetic mean, median, mid-network l=8..24
      geomean, |T| geomean incl. l=0, the 45-deg trajectory geomean, the
      squared (variance-transmission) version T^2, and the sin^2-flow factor
      exp(-b*th_l - rho) per layer.
  A6. Transmission gate: typical in [0.83, 0.91] (brackets S8's committed
      0.869/0.879/0.876; those are refit here from s8_results.json as a check).
  A7. Route (a) verdict: DERIVED if A4 and A6 both pass; PARTIAL if exactly
      one; MISS if neither.
  A8. UNGATED variants (reported for honesty/diagnosis): rho -> 2/n; the
      brief's refined mu(th,n) recursion (adds -8th/(15 pi n) and
      -(2/(9pi^2) - 68/(45pi^2 n)) th^2); the "hybrid" flow replacing the
      small-angle term -(2/(3pi))th with the EXACT mean-field log-sin^2
      contraction lambda(th) = ln(sin^2 arccos f(cos th) / sin^2 th) while
      keeping -rho(n) (J&N's own consistency check: their th-term is the
      small-angle expansion of lambda); and each with rho = 0 (mean-field
      limit; hybrid rho=0 must reproduce S7's committed c32 exactly).

Route (b) — D/n kernel fluctuation:
  B1. Reconstructed 5-line computation (assumptions in the verdict):
      Var[K_{l+1} | K_l] = (5/n) K_l^2  (exact Gaussian/ReLU moments),
      independent multiplicative compounding over D layers =>
      E[K_D^2]/E[K_D]^2 = (1+5/n)^D  ~ exp(5D/n) = exp(0.625) = 1.868 at
      D/n = 32/256;  Var[ln K_D] ~ 5D/n.  Verified by an EXACT-in-distribution
      scalar chain MC (the diagonal preactivation kernel of a bias-free He ReLU
      net is exactly K_{l+1} = (2/n) sum_i relu(z_i)^2, z_i iid N(0, K_l)).
  B2. Mapping to xi inflation (the predeclared model, its one loud assumption
      named in the verdict): the realized per-net normalized correlation curve
      is c_G(th) = c_mf(th)^G — i.e. the accumulated log-decay is the mean-field
      log-decay times the net's multiplicative kernel-fluctuation factor G,
      identified with the depth-D kernel factor: ln G ~ N(-s2/2, s2),
      s2 = 5D/n = 0.625, E[G] = 1 (the kernel-mean normalization that the
      compounding derivation fixes exactly).
  B3. Expected inflation (GATED) := E[xi_G]/xi_mf by MC (2e6 draws, seed
      20260812) where xi_G solves c_mf(th)^G = 1/2 on the exact mean-field
      normalized curve (fine 0.01-deg grid, verified against S7's committed
      table).  Analytic exponential-tail cross-check: for a pure exponential
      curve xi_G/xi = 1/G exactly, so E = exp(s2) = 1.868; the MC machinery is
      validated by reproducing that number on a synthetic pure-exponential
      curve.  Gate: expected inflation in [1.5, 2.4].
  B4. Honesty rows (REPORTED): median inflation, quantiles, model-implied
      per-net scatter vs the measured {1.70, 1.77, 2.20} spread.

Overall: task's predeclared fallback — if route (a) curve is mostly outside
AND route (b) inflation is outside [1.3, 3], the laws stay EMPIRICAL.
"""

import json
import time
from pathlib import Path

import numpy as np

T0 = time.time()
HERE = Path(__file__).resolve().parent
S7_JSON = HERE.parent / "s7_speckle" / "s7_results.json"
S8_JSON = HERE.parent / "s8_layer_profile" / "s8_results.json"

N_WIDTH = 256
DEPTH = 32
BETA = 2.0 / (3.0 * np.pi)
THETAS0_DEG = np.array([0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 45.0, 90.0])
CI_PRIMARY = None  # set from committed se_per_theta below (2x)
CI_FLOOR = 0.045
KERNEL_MC_NETS = 200_000
KERNEL_MC_SEED = 20260811
XI_MC_DRAWS = 2_000_000
XI_MC_SEED = 20260812

s7 = json.loads(S7_JSON.read_text())
s8 = json.loads(S8_JSON.read_text())

# ----------------------------------------------------------------------------
# Shared mean-field machinery (Cho-Saul / arccos kernel), verified vs S7.
# ----------------------------------------------------------------------------

def f_map(c):
    """Infinite-width ReLU correlation map f(c) = [sin th + (pi-th) cos th]/pi."""
    c = np.clip(c, -1.0, 1.0)
    th = np.arccos(c)
    return (np.sin(th) + (np.pi - th) * c) / np.pi


def c32_meanfield(theta_rad, depth=DEPTH):
    c = np.cos(np.asarray(theta_rad, dtype=np.float64))
    for _ in range(depth):
        c = f_map(c)
    return c


def rho_full(n):
    return np.log((n + 5) / (n - 1)) - 10 * n / (n + 5) ** 2 + 6 * n / (n - 1) ** 2


# ----------------------------------------------------------------------------
# Route (a): flows
# ----------------------------------------------------------------------------

def theta_from_u(u):
    return np.arcsin(np.sqrt(np.minimum(np.exp(u), 1.0)))


def flow(theta0_rad, rho, depth=DEPTH, mode="verbatim", n=N_WIDTH):
    """Iterate the log-sin^2 recursion; return theta trajectory (depth+1,)."""
    u = np.log(np.sin(theta0_rad) ** 2) if theta0_rad < np.pi / 2 else 0.0
    thetas = [theta0_rad]
    for _ in range(depth):
        th = thetas[-1]
        if mode == "verbatim":
            du = -BETA * th - rho
        elif mode == "refined":
            du = (-BETA * th - rho - 8.0 * th / (15.0 * np.pi * n)
                  - (2.0 / (9.0 * np.pi ** 2) - 68.0 / (45.0 * np.pi ** 2 * n)) * th ** 2)
        elif mode == "hybrid":
            thp = np.arccos(f_map(np.cos(th)))
            du = 2.0 * (np.log(np.sin(thp)) - np.log(np.sin(th))) - rho
        else:
            raise ValueError(mode)
        u = u + du
        thetas.append(theta_from_u(u))
    return np.array(thetas)


def flow_multiplicative(theta0_rad, rho, depth=DEPTH):
    """Same verbatim flow in the s = sin^2 parameterization (implementation check)."""
    s = np.sin(theta0_rad) ** 2 if theta0_rad < np.pi / 2 else 1.0
    thetas = [theta0_rad]
    for _ in range(depth):
        th = thetas[-1]
        s = s * np.exp(-BETA * th - rho)
        thetas.append(np.arcsin(np.sqrt(min(s, 1.0))))
    return np.array(thetas)


def transmission_analytic(traj, rho):
    """T_l = d th_{l+1}/d th_l along a trajectory (regularized form)."""
    th = traj[:-1]
    thn = traj[1:]
    return np.exp(-(BETA * th + rho) / 2.0) * (np.cos(th) - (BETA / 2.0) * np.sin(th)) / np.cos(thn)


def transmission_fd(traj, rho, h=1e-7):
    def one_step(th):
        s = np.sin(th) ** 2 * np.exp(-BETA * th - rho)
        return np.arcsin(np.sqrt(np.minimum(s, 1.0)))
    th = traj[:-1]
    return (one_step(th + h) - one_step(th - h)) / (2 * h)


rho = float(rho_full(N_WIDTH))
rho_simple = 2.0 / N_WIDTH

# rho(n) asymptotic sanity: rho(n)*n -> 2
rho_asym = {str(n): float(rho_full(n) * n) for n in (256, 4096, 65536, 2**24)}

th0_rad = np.deg2rad(THETAS0_DEG)

trajs = {}          # primary verbatim, full rho
trajs_alt = {}      # multiplicative-parameterization check
variants = {"rho2n": {}, "refined": {}, "hybrid": {}, "verbatim_rho0": {}, "hybrid_rho0": {}}
for d, t in zip(THETAS0_DEG, th0_rad):
    key = f"{d:g}"
    trajs[key] = flow(t, rho, mode="verbatim")
    trajs_alt[key] = flow_multiplicative(t, rho)
    variants["rho2n"][key] = flow(t, rho_simple, mode="verbatim")
    variants["refined"][key] = flow(t, rho, mode="refined")
    variants["hybrid"][key] = flow(t, rho, mode="hybrid")
    variants["verbatim_rho0"][key] = flow(t, 0.0, mode="verbatim")
    variants["hybrid_rho0"][key] = flow(t, 0.0, mode="hybrid")

param_check_max = max(float(np.max(np.abs(trajs[k] - trajs_alt[k]))) for k in trajs)

# hybrid rho=0 must reproduce S7's committed mean-field c32 exactly
c32_hybrid_rho0 = np.array([np.cos(variants["hybrid_rho0"][f"{d:g}"][-1]) for d in THETAS0_DEG])
c32_committed = np.array(s7["meanfield"]["c32_probe"])
meanfield_repro_maxdiff = float(np.max(np.abs(c32_hybrid_rho0 - c32_committed)))

# verbatim rho=0 vs exact mean-field (quantifies small-angle truncation error alone)
c32_verbatim_rho0 = np.array([np.cos(variants["verbatim_rho0"][f"{d:g}"][-1]) for d in THETAS0_DEG])
verbatim_truncation_err = (c32_verbatim_rho0 - c32_committed).tolist()

# normalization-functional verification: S7's committed normalization reproduced
m2 = c32_committed[-1]
c_pred_from_committed = (c32_committed - m2) / (1.0 - m2)
norm_functional_maxdiff = float(np.max(np.abs(
    c_pred_from_committed - np.array(s7["meanfield"]["c_pred_probe"]))))


def normalized_curve(traj_dict):
    craw = np.array([np.cos(traj_dict[f"{d:g}"][-1]) for d in THETAS0_DEG])
    plateau = craw[-1]
    return craw, (craw - plateau) / (1.0 - plateau)


c_raw_fw, c_pred_fw = normalized_curve(trajs)
variant_curves = {}
for name, vt in variants.items():
    vr, vn = normalized_curve(vt)
    variant_curves[name] = {"c_raw": vr.tolist(), "c_pred": vn.tolist()}

# --- hit/miss vs committed S7 measurements -----------------------------------
se = float(s7["nets"][0]["se_per_theta"])
CI_PRIMARY = 2.0 * se
ci_bands = {"primary_2se": CI_PRIMARY, "floor_1se": CI_FLOOR, "joint_2sqrt2se": 2.0 * np.sqrt(2.0) * se}

nets = {str(nd["net_seed"]): np.array(nd["c_meas"]) for nd in s7["nets"]}

hitmiss = {}
for band_name, half in ci_bands.items():
    hitmiss[band_name] = {}
    for seed, cm in nets.items():
        resid = c_pred_fw[:7] - cm[:7]            # 90 deg excluded
        hits = np.abs(resid) <= half
        hitmiss[band_name][seed] = {
            "resid": resid.tolist(),
            "hit": hits.tolist(),
            "n_hit_of_7": int(hits.sum()),
        }

n_hits_primary = {s: hitmiss["primary_2se"][s]["n_hit_of_7"] for s in nets}
nets_passing_curve = sum(1 for v in n_hits_primary.values() if v >= 5)
gate_a_curve = nets_passing_curve >= 2

# variant hit counts (reported)
variant_hits = {}
for name, vc in variant_curves.items():
    vh = {}
    for seed, cm in nets.items():
        vh[seed] = int(np.sum(np.abs(np.array(vc["c_pred"])[:7] - cm[:7]) <= CI_PRIMARY))
    variant_hits[name] = vh

# --- implied half-height xi of the route-(a) curves (REPORTED, not gated) -----
def flow_endpoint_grid(theta0_rad_grid, rho_val, mode="verbatim"):
    u = 2.0 * np.log(np.sin(theta0_rad_grid))
    th = theta0_rad_grid.copy()
    for _ in range(DEPTH):
        if mode == "verbatim":
            u = u - BETA * th - rho_val
        else:  # hybrid
            thp = np.arccos(f_map(np.cos(th)))
            u = u + 2.0 * (np.log(np.sin(thp)) - np.log(np.sin(th))) - rho_val
        th = theta_from_u(u)
    return th


fw_grid_deg = np.arange(0.01, 90.0 + 1e-9, 0.01)
xi_fw = {}
for mode in ("verbatim", "hybrid"):
    th32 = flow_endpoint_grid(np.deg2rad(fw_grid_deg), rho, mode=mode)
    craw = np.cos(th32)
    cnorm = (craw - craw[-1]) / (1.0 - craw[-1])
    xi_v = float(np.interp(0.5, cnorm[::-1], fw_grid_deg[::-1]))
    xi_fw[mode] = {"xi_half_deg": xi_v, "plateau_c_raw_90": float(craw[-1])}

# --- transmission -------------------------------------------------------------
traj90 = trajs["90"]
traj45 = trajs["45"]
T90 = transmission_analytic(traj90, rho)
T45 = transmission_analytic(traj45, rho)
T90_fd = transmission_fd(traj90, rho)
fd_check_max_rel = float(np.max(np.abs((T90 - T90_fd) / T90_fd)))

typical = float(np.exp(np.mean(np.log(T90[1:]))))           # GATED
sens = {
    "geomean_l1_31_90deg": typical,
    "geomean_absT_l0_31_90deg": float(np.exp(np.mean(np.log(np.abs(T90))))),
    "arith_mean_l1_31_90deg": float(np.mean(T90[1:])),
    "median_l1_31_90deg": float(np.median(T90[1:])),
    "geomean_l8_24_90deg": float(np.exp(np.mean(np.log(T90[8:25])))),
    "geomean_l1_31_45deg": float(np.exp(np.mean(np.log(T45[1:])))),
    "typical_squared_variance_version": typical ** 2,
    "sin2_factor_geomean_l0_31_90deg": float(np.exp(np.mean(-(BETA * traj90[:-1] + rho)))),
    "T_l0_90deg_fold_artifact": float(T90[0]),
}
gate_a_transmission = 0.83 <= typical <= 0.91

route_a_verdict = ("DERIVED" if (gate_a_curve and gate_a_transmission)
                   else "PARTIAL" if (gate_a_curve or gate_a_transmission)
                   else "MISS")

# --- S8 refit cross-check -----------------------------------------------------
s8_refit = {}
for seed in ("101", "202", "303"):
    v = np.array(s8["per_net"][seed]["v_l_mean"])
    ll = np.arange(len(v))
    slope, _ = np.polyfit(ll, np.log(v), 1)
    s8_refit[seed] = float(np.exp(slope))
s8_committed = {"101": 0.869, "202": 0.879, "303": 0.876}

# ----------------------------------------------------------------------------
# Route (b)
# ----------------------------------------------------------------------------

# B1 moments, verified by quadrature on N(0,1):  E relu(z)^2 = 1/2, E relu(z)^4 = 3/2
g = np.random.default_rng(1)  # only for quadrature nodes fallback; use analytic instead
zs, ws = np.polynomial.hermite_e.hermegauss(199)
wnorm = ws / np.sqrt(2 * np.pi)
relu2 = np.sum(wnorm * np.maximum(zs, 0.0) ** 2)
relu4 = np.sum(wnorm * np.maximum(zs, 0.0) ** 4)
moment_check = {"E_relu2_minus_half": float(relu2 - 0.5),
                "E_relu4_minus_1p5": float(relu4 - 1.5)}
var_phi2 = relu4 - relu2 ** 2          # = 5/4
per_layer_var_coeff = float(N_WIDTH * (2.0 / N_WIDTH) ** 2 * N_WIDTH * var_phi2 / N_WIDTH)  # = 4*var_phi2/1 -> 5
# Var[K_{l+1}|K_l] = (2/n)^2 * n * Var[relu(z)^2] * K_l^2 = (5/n) K_l^2
per_layer_var_over_K2 = float((2.0 / N_WIDTH) ** 2 * N_WIDTH * var_phi2)  # 5/n

s2 = 5.0 * DEPTH / N_WIDTH                       # 0.625
kernel_factor_analytic = float(np.exp(s2))       # 1.868
kernel_factor_product = float((1.0 + 5.0 / N_WIDTH) ** DEPTH)

# exact-in-distribution scalar chain MC (bias-free He ReLU diagonal kernel law)
rng = np.random.default_rng(KERNEL_MC_SEED)
chunk = 25_000
sumK = sumK2 = sumlnK = sumlnK2 = 0.0
sumK_31 = sumK2_31 = 0.0
done = 0
while done < KERNEL_MC_NETS:
    m = min(chunk, KERNEL_MC_NETS - done)
    K = np.ones(m)
    K31 = None
    for layer in range(DEPTH):
        z = rng.standard_normal((m, N_WIDTH))
        K = (2.0 / N_WIDTH) * np.sum(np.maximum(z * np.sqrt(K)[:, None], 0.0) ** 2, axis=1)
        if layer == DEPTH - 2:
            K31 = K.copy()
    sumK += K.sum(); sumK2 += (K ** 2).sum()
    lnK = np.log(K)
    sumlnK += lnK.sum(); sumlnK2 += (lnK ** 2).sum()
    sumK_31 += K31.sum(); sumK2_31 += (K31 ** 2).sum()
    done += m
NN = KERNEL_MC_NETS
EK, EK2 = sumK / NN, sumK2 / NN
mc_factor_32 = float(EK2 / EK ** 2)
mc_var_lnK = float(sumlnK2 / NN - (sumlnK / NN) ** 2)
mc_factor_31 = float((sumK2_31 / NN) / (sumK_31 / NN) ** 2)
# rough SE of the factor via lognormal delta approx: rel SE ~ sqrt(e^{4s2}-1)/sqrt(N)
mc_factor_relse = float(np.sqrt(np.exp(4 * s2) - 1.0) / np.sqrt(NN))

# --- fine mean-field normalized curve + xi ------------------------------------
grid_deg = np.arange(0.0, 90.0 + 1e-9, 0.01)
c32_fine = c32_meanfield(np.deg2rad(grid_deg))
cn_fine = (c32_fine - c32_fine[-1]) / (1.0 - c32_fine[-1])
mono_ok = bool(np.all(np.diff(cn_fine) < 0))
# verify fine curve against committed table values (2.5-deg grid)
tg = np.array(s7["meanfield"]["table_grid_deg"])
tc = np.array(s7["meanfield"]["table_c32"])
idx = np.round(tg / 0.01).astype(int)
fine_vs_table_maxdiff = float(np.max(np.abs(c32_fine[idx] - tc)))


def xi_half(y_target):
    """theta (deg) where cn_fine first crosses y_target (linear interp)."""
    return float(np.interp(y_target, cn_fine[::-1], grid_deg[::-1]))


xi_mf = xi_half(0.5)
xi_mf_committed = float(s7["meanfield"]["xi_meanfield_half_deg"])

# xi inflation MC under c_G = c_mf^G, lnG ~ N(-s2/2, s2)
rng2 = np.random.default_rng(XI_MC_SEED)
lnG = rng2.normal(-s2 / 2.0, np.sqrt(s2), XI_MC_DRAWS)
G = np.exp(lnG)
y = 0.5 ** (1.0 / G)                      # need c_mf(xi) = 0.5^{1/G}
xi_draws = np.interp(y, cn_fine[::-1], grid_deg[::-1])
censor_hi = float(np.mean(xi_draws >= 89.99))
ratio = xi_draws / xi_mf
xi_infl_mean = float(np.mean(ratio))
xi_infl_median = float(np.median(ratio))
xi_infl_q = {q: float(np.quantile(ratio, q / 100.0)) for q in (2.5, 25, 75, 97.5)}
xi_infl_mc_se = float(np.std(ratio) / np.sqrt(XI_MC_DRAWS))
p_in_measured_band = float(np.mean((ratio >= 1.5) & (ratio <= 2.4)))

# MC machinery validation on a pure exponential curve (analytic answer e^{s2})
grid_x = np.arange(0.0, 400.0, 0.01)
cexp = np.exp(-grid_x)                    # xi = ln 2
y2 = 0.5 ** (1.0 / G)
xi_exp = np.interp(y2, cexp[::-1], grid_x[::-1]) / np.log(2.0)
pure_exp_mc_mean = float(np.mean(np.where(y2 > cexp[-1], xi_exp, np.nan)))
pure_exp_censor = float(np.mean(y2 <= cexp[-1]))

measured_ratios = [float(r) for r in s7["xi_ratios"]]

gate_b = 1.5 <= xi_infl_mean <= 2.4
route_b_verdict = "DERIVED" if gate_b else ("PARTIAL" if 1.3 <= xi_infl_mean <= 3.0 else "MISS")

curve_mostly_outside = all(v < 4 for v in n_hits_primary.values())
overall_empirical = (curve_mostly_outside and not (1.3 <= xi_infl_mean <= 3.0))

# ----------------------------------------------------------------------------
# Emit
# ----------------------------------------------------------------------------
results = {
    "ledger_id": "s12_finite_width_kernel_capstone",
    "date": "2026-08-09",
    "firewall": ("pure math + read-only committed s7/s8 jsons + exact scalar kernel-chain MC; "
                 "no datasets, no truth/scorer, no git; writes confined to s12_finite_width_kernel/"),
    "config": {
        "n_width": N_WIDTH, "depth": DEPTH, "beta_2_over_3pi": BETA,
        "rho_full": rho, "rho_2_over_n": rho_simple,
        "thetas0_deg": THETAS0_DEG.tolist(),
        "ci_primary_halfwidth": CI_PRIMARY, "ci_bands": {k: float(v) for k, v in ci_bands.items()},
        "kernel_mc": {"nets": KERNEL_MC_NETS, "seed": KERNEL_MC_SEED},
        "xi_mc": {"draws": XI_MC_DRAWS, "seed": XI_MC_SEED},
    },
    "checks": {
        "rho_times_n_asymptote_to_2": rho_asym,
        "flow_parameterization_maxdiff_rad": param_check_max,
        "hybrid_rho0_vs_committed_c32_maxdiff": meanfield_repro_maxdiff,
        "norm_functional_vs_committed_cpred_maxdiff": norm_functional_maxdiff,
        "transmission_fd_vs_analytic_max_rel": fd_check_max_rel,
        "verbatim_rho0_minus_exact_meanfield_c32": verbatim_truncation_err,
        "relu_moment_quadrature": moment_check,
        "fine_c32_vs_committed_table_maxdiff": fine_vs_table_maxdiff,
        "cn_fine_strictly_monotone": mono_ok,
        "xi_mf_recomputed_deg": xi_mf,
        "xi_mf_committed_deg": xi_mf_committed,
        "pure_exponential_mc_mean_vs_exp_s2": {
            "mc": pure_exp_mc_mean, "analytic": kernel_factor_analytic,
            "censor_frac": pure_exp_censor},
        "kernel_chain_mc": {
            "factor_D32": mc_factor_32, "factor_D31": mc_factor_31,
            "rel_se_approx": mc_factor_relse,
            "var_lnK_D32": mc_var_lnK, "predicted_var_lnK": s2,
            "predicted_factor_exp": kernel_factor_analytic,
            "predicted_factor_product": kernel_factor_product},
    },
    "route_a": {
        "flow_theta_deg_by_theta0": {k: np.rad2deg(v).tolist() for k, v in trajs.items()},
        "c_raw_fw": c_raw_fw.tolist(),
        "c_pred_fw": c_pred_fw.tolist(),
        "c_pred_meanfield_committed": s7["meanfield"]["c_pred_probe"],
        "c_meas_by_net": {k: v.tolist() for k, v in nets.items()},
        "hitmiss": hitmiss,
        "n_hits_primary_of_7": n_hits_primary,
        "nets_passing_curve_ge5of7": nets_passing_curve,
        "variant_curves": variant_curves,
        "variant_hits_primary": variant_hits,
        "transmission": {
            "T_per_layer_90deg": T90.tolist(),
            "T_per_layer_45deg": T45.tolist(),
            "typical_GATED": typical,
            "sensitivity": sens,
        },
        "xi_half_of_fw_curve_reported": {m: {**v, "ratio_over_mf": v["xi_half_deg"] / xi_mf}
                                          for m, v in xi_fw.items()},
        "s8_transmission_refit": s8_refit,
        "s8_transmission_committed": s8_committed,
        "gates": {"curve_ge5of7_on_ge2nets": gate_a_curve,
                  "transmission_in_083_091": gate_a_transmission},
        "verdict": route_a_verdict,
    },
    "route_b": {
        "s2_var_lnK": s2,
        "per_layer_var_over_K2_times_n": float(per_layer_var_over_K2 * N_WIDTH),
        "kernel_factor_analytic_exp5DoverN": kernel_factor_analytic,
        "kernel_factor_exact_product": kernel_factor_product,
        "kernel_factor_mc": mc_factor_32,
        "xi_mf_deg": xi_mf,
        "xi_inflation": {
            "expected_GATED": xi_infl_mean,
            "mc_se": xi_infl_mc_se,
            "median": xi_infl_median,
            "quantiles_pct": xi_infl_q,
            "censor_frac_at_90deg": censor_hi,
            "analytic_exponential_tail": kernel_factor_analytic,
            "p_model_ratio_in_1p5_2p4": p_in_measured_band,
        },
        "measured_ratios": measured_ratios,
        "gate": {"expected_inflation_in_1p5_2p4": gate_b},
        "verdict": route_b_verdict,
    },
    "overall": {
        "route_a": route_a_verdict,
        "route_b": route_b_verdict,
        "empirical_fallback_fires": overall_empirical,
    },
    "deviations": [],
    "wall_s": round(time.time() - T0, 1),
}

(HERE / "s12_results.json").write_text(json.dumps(results, indent=2))

print(json.dumps({k: results[k] for k in ("checks", "overall")}, indent=2))
print("route_a gates:", results["route_a"]["gates"], "hits:", n_hits_primary,
      "typical T:", round(typical, 4))
print("route_b expected inflation:", round(xi_infl_mean, 4),
      "median:", round(xi_infl_median, 4), "analytic:", round(kernel_factor_analytic, 4))
print("wall_s:", results["wall_s"])
