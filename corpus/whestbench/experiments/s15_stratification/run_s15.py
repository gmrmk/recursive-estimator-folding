"""S15 -- first-layer stratification premise test
(ledger id s15_firstlayer_stratification_premise).

QUESTION (the last open mechanism door): does a CHEAP first-layer covariate
capture material residual variance of the estimator's per-direction
contribution -- enough to justify a stratified/conditional estimator?

The first-layer output h1(u)=ReLU(W1 @ (r*u)) is a sufficient statistic for
the whole net, so *structure is total*. The question is whether a
LOW-DIMENSIONAL cheap summary of h1 explains variance BEYOND what the
exactly-integrated low-degree harmonics (deg 0,1,2) already capture.

TARGET   f(u) = neuron-averaged final post-ReLU output (== S5 'ybar'); this is
               the estimator's per-direction contribution (the design averages
               f over the directions to estimate the sphere mean).
COVARIATES (first-layer only, ~1/32 forward cost):
  C1 firing rate rho(u) = mean_i 1(a_i>0), a = W1 @ (r*u)  [odd-ish about 0.5]
  C2 first-layer output norm ||h1(u)||_2, h1 = ReLU(a)
  C3 top-k projections of h1(u) onto the leading RIGHT singular vectors of the
     effective first layer (hidden-space directions), k in {1,2,4,8}
  C4 (control) raw first-moment linear statistic <u, w_moment> (degree-1;
     must re-measure ~0 because the base already spans all of degree-1).
DEGREE-<=2 BASIS on u (the design integrates 0,1,2 EXACTLY -> no headroom
     there). Two bases documented:
  Base-B (PRIMARY, conservative): 256 linear singular projections s_m=<u,U_f[:,m]>
     (spans ALL of degree-1) + 256 diagonal squares s_m^2 (captures ||pre1||^2
     = the even part of C2 exactly) + top-16 off-diagonal cross terms s_m s_n.
  Base-A (sensitivity, task-literal lean): top-8 linear + degree-2 within top-8.
  (mean handled by column-centering; no explicit constant column.)

INCREMENTAL R^2 = R2_full - R2_base = fraction of stratifiable residual
variance the cheap covariate explains beyond the exactly-integrated harmonics.
Gate quantity is the OUT-OF-SAMPLE (split-sample) incremental R^2.

PREDECLARED GATES (not softened):
  pooled/per-net incremental R^2 >= 20% on >=2/3 nets -> PASS
  < 5% pooled                                          -> KILL
  5-20%                                                -> INCONCLUSIVE

VERIFICATION:
  1. SPLIT-SAMPLE: coefficients fit on one random half of directions,
     incremental R^2 measured on the held-out half (swap-halves averaged).
     Antipodal pairs kept in the same half (u,-u are deterministically related
     -> splitting them would leak). This OOS number is the gate quantity.
  2. POSITIVE CONTROL: regress f on a KNOWN degree-4 zonal harmonic and confirm
     R^2 ~ M191's 0.18-0.23% for a single harmonic.
  3. Report R2_base itself and interpret it.

FIREWALL: synthetic He nets only; n8a machinery + S5 arrays imported/loaded
read-only (n8a loads the frozen v3 sampling asset kerdock_phases.npz read
only); no dataset/truth/scorer/submission; no git; writes confined to this
directory (s15_stratification).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True  # firewall: no .pyc into other directories

import numpy as np

HERE = Path(__file__).resolve().parent
N8A = HERE.parent / "n8a_rqmc_kerdock" / "run_n8a_gates.py"
S5_DIR = HERE.parent / "s5_kink_concentration"

_spec = importlib.util.spec_from_file_location("run_n8a_gates", N8A)
n8a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(n8a)  # module main() is __main__-guarded: safe

WIDTH = n8a.WIDTH            # 256
DEPTH = n8a.DEPTH            # 32
MEAN_CHI = n8a.MEAN_CHI_256  # 15.98438266660852747
NET_SEEDS = (101, 202, 303)
N_BASE = n8a.N_BASE          # 32,256
N_FULL = 2 * N_BASE          # 64,512

K_C3 = (1, 2, 4, 8)          # C3 top-k projection counts
CROSS_TOPB = 16              # Base-B off-diagonal cross terms over top-16
LEAN_TOPA = 8                # Base-A top-k
RIDGE_REL = 1e-6             # tiny ridge (handles diag-square/const collinearity)

PASS_INCR = 0.20
KILL_INCR = 0.05


def rot_seed(net_seed: int) -> int:
    return 900_000 + net_seed * 1_000 + 0  # r = 0 (S5 / P2 lineage)


# ------------------------------------------------------------ forward / first layer
def first_layer(weights, seed):
    """Effective first layer + base-direction preactivation pre1 (N_BASE,WIDTH)."""
    rot = n8a.haar_rotation(rot_seed(seed))
    first_eff = (rot.T @ weights[0]).astype(np.float32)  # (in, hidden) in kerdock coords
    return rot, first_eff


def full_forward_ybar(weights, first_eff, kerdock):
    """Full 32-layer antipodal forward; returns ybar (N_FULL,) f64 and pre1."""
    pre1 = kerdock @ first_eff
    act = np.concatenate([np.maximum(pre1, np.float32(0.0)),
                          np.maximum(-pre1, np.float32(0.0))], axis=0)
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    ybar = act.astype(np.float64).mean(axis=1)
    return ybar, pre1


# ------------------------------------------------------------ regression helper
def fit_eval(Xtr, ytr, Xte, yte, ridge_rel=RIDGE_REL):
    """Column-centered ridge-stabilized OLS. Returns (r2_insample, r2_oos)."""
    mu = Xtr.mean(axis=0)
    Xtr_c = Xtr - mu
    Xte_c = Xte - mu
    ym = ytr.mean()
    ytr_c = ytr - ym
    XtX = Xtr_c.T @ Xtr_c
    d = np.trace(XtX) / XtX.shape[0]
    XtX_r = XtX + np.eye(XtX.shape[0]) * (ridge_rel * d)
    beta = np.linalg.solve(XtX_r, Xtr_c.T @ ytr_c)
    pred_tr = Xtr_c @ beta + ym
    r2_tr = 1.0 - ((ytr - pred_tr) ** 2).sum() / ((ytr - ym) ** 2).sum()
    pred_te = Xte_c @ beta + ym
    r2_te = 1.0 - ((yte - pred_te) ** 2).sum() / ((yte - yte.mean()) ** 2).sum()
    return float(r2_tr), float(r2_te)


def r2_simple(y, feats):
    """In-sample R^2 of regressing y on [feats] (centered, intercept implicit)."""
    r2_tr, _ = fit_eval(feats, y, feats, y)
    return r2_tr


# ------------------------------------------------------------ feature construction
def build_features(kerdock, first_eff, pre1, f):
    """Build base bases and covariate blocks on the DOUBLED direction set.

    Ordering matches S5 ybar: rows [0:N_BASE]=u, [N_BASE:N_FULL]=-u.
    """
    # ---- SVD of the effective first layer (kerdock-coord input -> hidden) ----
    U_f, S_f, Vt_f = np.linalg.svd(first_eff.astype(np.float64), full_matrices=False)
    # linear singular projections s_m(u) = <u, U_f[:,m]> (degree-1, in kerdock coord)
    s_base = kerdock.astype(np.float64) @ U_f              # (N_BASE, WIDTH)
    s_dbl = np.vstack([s_base, -s_base])                  # odd under antipode

    # ---- covariates on base directions, then doubled ----
    h1_p = np.maximum(pre1, np.float32(0.0)).astype(np.float64)   # h1(u)
    h1_m = np.maximum(-pre1, np.float32(0.0)).astype(np.float64)  # h1(-u)
    # C1 firing rate
    c1 = np.concatenate([(pre1 > 0).mean(axis=1),
                         (pre1 < 0).mean(axis=1)]).astype(np.float64)
    # C2 first-layer output norm ||h1||_2
    c2 = np.concatenate([np.linalg.norm(h1_p, axis=1),
                         np.linalg.norm(h1_m, axis=1)])
    # C3 projections of h1 onto leading right singular vectors (hidden space)
    Vk = Vt_f[:max(K_C3)].T                                # (WIDTH, kmax) hidden-space
    c3_p = h1_p @ Vk
    c3_m = h1_m @ Vk
    c3 = np.vstack([c3_p, c3_m])                            # (N_FULL, kmax)

    # C4 control: raw first-moment linear statistic <u, w_moment>, degree-1.
    kerdock_dbl = np.vstack([kerdock.astype(np.float64), -kerdock.astype(np.float64)])
    fc = f - f.mean()
    w_moment = kerdock_dbl.T @ fc
    w_moment /= max(np.linalg.norm(w_moment), 1e-300)
    c4 = (kerdock_dbl @ w_moment)[:, None]

    # ---- Base-B (primary) ----
    diag_sq = s_dbl ** 2                                    # even; captures ||pre1||^2
    iu = np.triu_indices(CROSS_TOPB, k=1)
    cross = (s_dbl[:, iu[0]] * s_dbl[:, iu[1]])             # even off-diagonal deg-2
    base_B = np.hstack([s_dbl, diag_sq, cross])            # (N_FULL, 256+256+120)

    # ---- Base-A (lean, task-literal) ----
    sA = s_dbl[:, :LEAN_TOPA]
    ia = np.triu_indices(LEAN_TOPA, k=0)                    # incl diagonal
    quadA = sA[:, ia[0]] * sA[:, ia[1]]
    base_A = np.hstack([sA, quadA])                        # (N_FULL, 8+36)

    covs = {
        "C1_firing_rate": c1[:, None],
        "C2_h1_norm": c2[:, None],
        "C4_control_linear": c4,
    }
    for k in K_C3:
        covs[f"C3_top{k}"] = c3[:, :k]
    covs["union_C1_C2_C3top8"] = np.hstack([c1[:, None], c2[:, None], c3[:, :8]])
    return base_A, base_B, covs, S_f


# ------------------------------------------------------------ split-sample eval
def incremental_oos(base, covs, y, split_seed):
    """Swap-halves out-of-sample incremental R^2 per covariate set.

    Antipodal pairs kept together: split BASE indices, take {i, i+N_BASE}.
    Returns dict: base_oos, and per-cov {r2_full_oos, incr_oos, ...}.
    """
    rng = np.random.default_rng(split_seed)
    perm = rng.permutation(N_BASE)
    halfA = perm[: N_BASE // 2]
    halfB = perm[N_BASE // 2:]
    idxA = np.concatenate([halfA, halfA + N_BASE])
    idxB = np.concatenate([halfB, halfB + N_BASE])

    def one_dir(tr_idx, te_idx):
        r2b_tr, r2b_te = fit_eval(base[tr_idx], y[tr_idx], base[te_idx], y[te_idx])
        out = {"base_tr": r2b_tr, "base_te": r2b_te, "cov": {}}
        for name, C in covs.items():
            Xtr = np.hstack([base[tr_idx], C[tr_idx]])
            Xte = np.hstack([base[te_idx], C[te_idx]])
            r2f_tr, r2f_te = fit_eval(Xtr, y[tr_idx], Xte, y[te_idx])
            out["cov"][name] = {"full_tr": r2f_tr, "full_te": r2f_te,
                                "incr_tr": r2f_tr - r2b_tr,
                                "incr_te": r2f_te - r2b_te}
        return out

    AB = one_dir(idxA, idxB)   # fit A, eval B
    BA = one_dir(idxB, idxA)   # fit B, eval A
    res = {
        "base_oos": 0.5 * (AB["base_te"] + BA["base_te"]),
        "base_insample": 0.5 * (AB["base_tr"] + BA["base_tr"]),
        "cov": {},
    }
    for name in covs:
        a, b = AB["cov"][name], BA["cov"][name]
        res["cov"][name] = {
            "r2_full_oos": 0.5 * (a["full_te"] + b["full_te"]),
            "r2_full_insample": 0.5 * (a["full_tr"] + b["full_tr"]),
            "incremental_oos": 0.5 * (a["incr_te"] + b["incr_te"]),
            "incremental_insample": 0.5 * (a["incr_tr"] + b["incr_tr"]),
            "incremental_oos_AB": a["incr_te"],
            "incremental_oos_BA": b["incr_te"],
        }
    return res


# ------------------------------------------------------------ positive control
def positive_control(kerdock, rot, U_f, f, seed):
    """Regress f on a KNOWN degree-4 zonal harmonic; expect R^2 ~ 0.18-0.23%.

    t = <u, axis>/mean_chi.  PURE deg-4 R^2 = increment of t^4 over [1,t^2]
    (removes deg-0/2 confounds mechanically).  RAW = R^2 of [1,t^4]
    (matches M191's contaminated monomial for direct comparison).
    """
    rng = np.random.default_rng(seed)
    kb = kerdock.astype(np.float64)
    axes = {"singular0": U_f[:, 0]}
    for j in range(4):
        a = rng.standard_normal(WIDTH)
        axes[f"random{j}"] = a / np.linalg.norm(a)
    rows = {}
    for name, a in axes.items():
        t_base = (kb @ a) / MEAN_CHI
        t = np.concatenate([t_base, -t_base])
        t2 = t * t
        t4 = t2 * t2
        raw = r2_simple(f, t4[:, None])
        base12 = r2_simple(f, t2[:, None])
        full124 = r2_simple(f, np.column_stack([t2, t4]))
        rows[name] = {"raw_t4_R2": raw,
                      "pure_deg4_R2_increment": full124 - base12}
    pure = [v["pure_deg4_R2_increment"] for v in rows.values()]
    raw = [v["raw_t4_R2"] for v in rows.values()]

    # M191 direct reproduction: raw-t4 (== (a.u)^4) basis on top-8 singular +
    # 4 random axes (M191's deg4 basis).  M191 reported deg4 R^2 ~ 0.0018-0.0023.
    m191_axes = [U_f[:, j] for j in range(8)]
    rr = np.random.default_rng(seed + 42)
    for _ in range(4):
        a = rr.standard_normal(WIDTH)
        m191_axes.append(a / np.linalg.norm(a))
    t4_cols = []
    for a in m191_axes:
        tb = (kb @ a) / MEAN_CHI
        td = np.concatenate([tb, -tb])
        t4_cols.append((td * td) ** 2)
    m191_basis_R2 = r2_simple(f, np.column_stack(t4_cols))

    return {"per_axis": rows,
            "pure_deg4_R2_mean": float(np.mean(pure)),
            "pure_deg4_R2_range": [float(np.min(pure)), float(np.max(pure))],
            "raw_t4_R2_mean": float(np.mean(raw)),
            "raw_t4_R2_range": [float(np.min(raw)), float(np.max(raw))],
            "raw_t4_R2_singular0": rows["singular0"]["raw_t4_R2"],
            "m191_12axis_raw_t4_basis_R2": float(m191_basis_R2),
            "m191_reference_deg4_R2": "0.0018-0.0023 (m191_g0b_results.json)"}


# ------------------------------------------------------------------------- main
def main():
    t0 = time.perf_counter()
    print("S15 first-layer stratification premise test", flush=True)
    kerdock = n8a.load_kerdock_directions()   # (32256,256) f32, read-only rebuild

    results = {
        "ledger_id": "s15_firstlayer_stratification_premise",
        "date": "2026-08-09",
        "config": {
            "net_seeds": list(NET_SEEDS), "depth": DEPTH, "width": WIDTH,
            "rotation_seed_formula": "900000 + net_seed*1000 + 0 (r=0)",
            "direction_set": "full antipodally-doubled Kerdock design (64512), "
                             "no subsample",
            "n_base": N_BASE, "n_full": N_FULL, "radius": MEAN_CHI,
            "target": "f(u) = neuron-averaged final post-ReLU output (S5 ybar)",
            "base_B_primary": "256 linear s_m + 256 diag s_m^2 + top-16 cross "
                              "(=633 cols, spans all deg-1, exact ||pre1||^2)",
            "base_A_lean": "top-8 linear + deg-2 within top-8 (=45 cols)",
            "covariates": "C1 firing rate, C2 ||h1||_2, C3 top-{1,2,4,8} proj of "
                          "h1 onto right singular vecs, C4 control linear, "
                          "union(C1,C2,C3top8)",
            "gate_quantity": "swap-halves OUT-OF-SAMPLE incremental R^2 (Base-B)",
            "gates": {"pass": f"incr >= {PASS_INCR} on >=2/3 nets",
                      "kill": f"pooled incr < {KILL_INCR}",
                      "else": "INCONCLUSIVE"},
        },
        "reuse_verification": {}, "nets": {}, "pooled": {},
        "positive_control": {}, "verdict": None,
    }

    per_net_incr_B = {}   # covname -> [3 nets] OOS incremental under Base-B
    per_net_incr_A = {}
    reuse = results["reuse_verification"]
    reuse["reused_files"] = [str(S5_DIR / f"s5_net{s}_arrays.npz") for s in NET_SEEDS]
    reuse["d1_max_abs_diff"] = {}
    reuse["ybar_recompute_net101_max_abs_diff"] = None

    for seed in NET_SEEDS:
        tn = time.perf_counter()
        weights = n8a.he_mlp_weights(seed)
        rot, first_eff = first_layer(weights, seed)
        pre1 = kerdock @ first_eff  # (N_BASE, WIDTH) f32 -- cheap ~1/32 forward

        # ---- reuse target f from S5 (neuron-averaged final post-ReLU) ----
        arr = np.load(S5_DIR / f"s5_net{seed}_arrays.npz")
        f = arr["ybar"].astype(np.float64)         # (N_FULL,)
        d1_saved = arr["d1"].astype(np.float64)
        arr.close()

        # verify reuse: recompute d1 from my pre1, compare to saved (confirms
        # weights + rotation + first_eff + kerdock all match S5).
        col1 = np.linalg.norm(first_eff.astype(np.float64), axis=0)
        m1 = (np.abs(pre1.astype(np.float64)) / col1[None, :]).min(axis=1) / MEAN_CHI
        d1_mine = np.concatenate([m1, m1])
        d1_diff = float(np.abs(d1_mine - d1_saved).max())
        reuse["d1_max_abs_diff"][str(seed)] = d1_diff

        # net-101 only: full forward recompute of ybar vs saved (end-to-end reuse)
        if seed == 101:
            ybar_re, _ = full_forward_ybar(weights, first_eff, kerdock)
            reuse["ybar_recompute_net101_max_abs_diff"] = float(
                np.abs(ybar_re - f).max())

        # ---- features + regressions ----
        base_A, base_B, covs, S_f = build_features(kerdock, first_eff, pre1, f)

        # full-sample R2 (reported; in-sample, will inflate)
        r2_base_B_in = r2_simple(f, base_B)
        r2_base_A_in = r2_simple(f, base_A)

        # split-sample OOS (gate quantity)
        oB = incremental_oos(base_B, covs, f, 777_000 + seed)
        oA = incremental_oos(base_A, covs, f, 777_000 + seed)

        # positive control
        U_f = np.linalg.svd(first_eff.astype(np.float64),
                            full_matrices=False)[0]
        pc = positive_control(kerdock, rot, U_f, f, 191_000 + seed)

        net_row = {
            "singular_spectrum_first_layer": {
                "s_max": float(S_f[0]), "s_min": float(S_f[-1]),
                "s_median": float(np.median(S_f))},
            "base_B": {"r2_base_insample": r2_base_B_in,
                       "r2_base_oos": oB["base_oos"]},
            "base_A": {"r2_base_insample": r2_base_A_in,
                       "r2_base_oos": oA["base_oos"]},
            "covariate_sets_baseB": oB["cov"],
            "covariate_sets_baseA": oA["cov"],
            "positive_control": pc,
            "wall_s": round(time.perf_counter() - tn, 1),
        }
        results["nets"][str(seed)] = net_row
        results["positive_control"][str(seed)] = {
            "pure_deg4_R2_mean": pc["pure_deg4_R2_mean"],
            "raw_t4_R2_mean": pc["raw_t4_R2_mean"],
            "raw_t4_R2_singular0": pc["raw_t4_R2_singular0"],
            "m191_12axis_raw_t4_basis_R2": pc["m191_12axis_raw_t4_basis_R2"]}

        for name in covs:
            per_net_incr_B.setdefault(name, []).append(
                oB["cov"][name]["incremental_oos"])
            per_net_incr_A.setdefault(name, []).append(
                oA["cov"][name]["incremental_oos"])

        print(f"  net {seed}: R2_base(B)_in={r2_base_B_in:.4f} "
              f"R2_base(B)_oos={oB['base_oos']:.4f}", flush=True)
        for name in ("C1_firing_rate", "C2_h1_norm", "C3_top8",
                     "union_C1_C2_C3top8", "C4_control_linear"):
            print(f"      {name:22s} incr_oos(B)="
                  f"{oB['cov'][name]['incremental_oos']:+.5f}  "
                  f"incr_oos(A)={oA['cov'][name]['incremental_oos']:+.5f}",
                  flush=True)
        print(f"      pos-control: raw-t4 singular0={pc['raw_t4_R2_singular0']:.5f} "
              f"pure-deg4 mean={pc['pure_deg4_R2_mean']:.6f} "
              f"M191-12axis basis R2={pc['m191_12axis_raw_t4_basis_R2']:.5f} "
              f"(ref 0.0018-0.0023)  (d1_diff={d1_diff:.1e}, "
              f"wall={net_row['wall_s']}s)", flush=True)

    # ------------------------------------------------------------ pooled + gates
    pooled = results["pooled"]
    for name in per_net_incr_B:
        vB = per_net_incr_B[name]
        vA = per_net_incr_A[name]
        pooled[name] = {
            "baseB_per_net_incremental_oos": [float(x) for x in vB],
            "baseB_pooled_mean_incremental_oos": float(np.mean(vB)),
            "baseB_n_nets_ge_20pct": int(sum(1 for x in vB if x >= PASS_INCR)),
            "baseA_per_net_incremental_oos": [float(x) for x in vA],
            "baseA_pooled_mean_incremental_oos": float(np.mean(vA)),
        }

    # gate on Base-B (conservative primary). PASS uses the most generous cov set.
    gate_cov_sets = list(per_net_incr_B.keys())
    pass_hit = None
    for name in gate_cov_sets:
        if name == "C4_control_linear":
            continue
        if pooled[name]["baseB_n_nets_ge_20pct"] >= 2:
            pass_hit = name
            break
    # KILL if the most generous (union) pooled incremental < 5%
    union_pooled = pooled["union_C1_C2_C3top8"]["baseB_pooled_mean_incremental_oos"]
    max_pooled = max(pooled[n]["baseB_pooled_mean_incremental_oos"]
                     for n in gate_cov_sets if n != "C4_control_linear")

    if pass_hit is not None:
        verdict = (f"PASS: covariate set {pass_hit} reached OOS incremental "
                   f"R^2 >= {PASS_INCR:.0%} on >=2/3 nets (Base-B).")
    elif max_pooled < KILL_INCR:
        verdict = (f"KILL: residual is covariate-blind. Best pooled OOS "
                   f"incremental R^2 across all cheap first-layer covariate "
                   f"sets = {max_pooled:.4f} (< {KILL_INCR:.0%}); "
                   f"union(C1,C2,C3top8) pooled = {union_pooled:.4f}. No "
                   f"stratification headroom beyond the exactly-integrated "
                   f"degree-<=2 harmonics.")
    else:
        verdict = (f"INCONCLUSIVE: best pooled OOS incremental R^2 "
                   f"= {max_pooled:.4f} in [{KILL_INCR:.0%}, {PASS_INCR:.0%}); "
                   f"neither PASS nor KILL bar met.")

    results["gate_evaluation"] = {
        "gate_quantity": "swap-halves OOS incremental R^2 under Base-B",
        "best_pooled_incremental_oos": max_pooled,
        "union_pooled_incremental_oos": union_pooled,
        "pass_covariate_set": pass_hit,
    }
    results["verdict"] = verdict
    results["total_wall_s"] = round(time.perf_counter() - t0, 1)

    out = HERE / "s15_results.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"\nVERDICT: {verdict}")
    print(f"results -> {out}  (wall {results['total_wall_s']}s)", flush=True)


if __name__ == "__main__":
    main()
