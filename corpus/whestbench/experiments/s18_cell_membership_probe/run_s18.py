"""S18 -- ReLU cell-membership probe (ledger id s18_cell_membership_probe).

Closes the LAST named crack in the dispersion kill family: all prior measured
covariate bases were SMOOTH (zonal harmonics, first-layer moments, kink
distances).  Never measured: NON-SMOOTH, arrangement-combinatorial features --
the first-layer ReLU cell membership (sign pattern / activation cell) of the
input point.

DESIGN (mirrors S15 s15_stratification exactly: same 3 nets, same target
f(u) = S5 ybar reused read-only, same Base-B degree-<=2 harmonic basis, same
swap-halves antipodal-pair-preserving split, split seed 777000+net).

FEATURE SETS on the first-layer sign pattern bits(u) = 1(pre1(u) > 0):
  (a) active_count : per-direction count of active units (== 256 * S15's C1
      firing rate).  CONTROL per the predeclaration ("this overlaps
      firing-rate"): NOT gated; its role is to reproduce S15's cached C1
      incremental (pipeline cross-check).
  (b) cells_k16 / cells_k64 / cells_k256 : indicator columns for membership in
      the top-k most frequent activation cells (k = 16, 64, 256).  "Hashed
      sign-pattern bucket" implemented as a COLLISION-FREE perfect hash: the
      256 bits are packed to 32 bytes and cells identified by exact byte-row
      uniqueness (np.unique axis=0).  Ties in frequency broken
      lexicographically on the packed bytes (deterministic).
  (c) hamming_modal_majority : Hamming distance of bits(u) to the per-net
      modal pattern, modal = per-unit MAJORITY vote over the BASE directions
      (over the doubled set every unit is active on exactly half the rows, so
      the majority is taken over the base half).
      hamming_modal_literal  : Hamming distance to the literal most-frequent
      full pattern (ties broken lexicographically).  Both variants are gated;
      KILL for arm (c) requires BOTH below the bar (conservative).

GATE (predeclared, quantity = swap-halves OUT-OF-SAMPLE incremental R^2
beyond Base-B, per net):
  all gated sets ((b) x 3, (c) x 2) < 2.63e-5 on all 3 nets  -> KILL
  any gated set >= 1e-4 on 2+ nets                            -> SIGNAL
  otherwise                                                   -> INCONCLUSIVE

PREDICTION on record: KILL (residual is independent chi2_1 speckle,
uncorrelated with ANY function of the input point at design spacing).

TWO-SIGNAL VERIFICATION:
  1. split-sample OOS R^2 (the gate quantity itself);
  2. permutation null: shuffle f across directions (3 perms/net), same
     pipeline must report incremental R^2 ~ 0 +- fitting noise;
  plus: S15 C1 reproduction via arm (a) against the cached s15_results.json,
  d1 reuse check vs the S5 arrays (bit-exact expected), and an injection
  instrument check (synthetic ~1e-3 R^2 signal along the Hamming covariate
  must be recovered).

FIREWALL: synthetic He nets only; n8a machinery + S5 arrays + S15 results
loaded read-only; no dataset/truth/scorer/submission; no git; no touch of
m245_*/M243/M244; writes confined to this directory.
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
S15_JSON = HERE.parent / "s15_stratification" / "s15_results.json"

_spec = importlib.util.spec_from_file_location("run_n8a_gates", N8A)
n8a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(n8a)  # module main() is __main__-guarded: safe

WIDTH = n8a.WIDTH            # 256
DEPTH = n8a.DEPTH            # 32
MEAN_CHI = n8a.MEAN_CHI_256
NET_SEEDS = (101, 202, 303)
N_BASE = n8a.N_BASE          # 32,256
N_FULL = 2 * N_BASE          # 64,512

CROSS_TOPB = 16              # Base-B off-diagonal cross terms (S15 exact)
RIDGE_REL = 1e-6             # S15 exact
K_CELLS = (16, 64, 256)

NOISE_COST = 2.63e-5         # predeclared per-feature fitting-noise cost
SIGNAL_BAR = 1e-4            # predeclared genuine-signal bar
N_PERM = 3                   # permutation-null draws per net
GATED_SETS = ("cells_k16", "cells_k64", "cells_k256",
              "hamming_modal_majority", "hamming_modal_literal")


def rot_seed(net_seed: int) -> int:
    return 900_000 + net_seed * 1_000 + 0  # r = 0 (S5 / S15 lineage)


# ------------------------------------------------------------ regression (S15 exact)
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


def split_indices(split_seed):
    """S15-exact swap-halves split; antipodal pairs {i, i+N_BASE} together."""
    rng = np.random.default_rng(split_seed)
    perm = rng.permutation(N_BASE)
    halfA = perm[: N_BASE // 2]
    halfB = perm[N_BASE // 2:]
    idxA = np.concatenate([halfA, halfA + N_BASE])
    idxB = np.concatenate([halfB, halfB + N_BASE])
    return idxA, idxB


def incremental_oos(base, covs, y, split_seed):
    """Swap-halves OOS incremental R^2 per covariate set (S15 exact)."""
    idxA, idxB = split_indices(split_seed)

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

    AB = one_dir(idxA, idxB)
    BA = one_dir(idxB, idxA)
    res = {
        "base_oos": 0.5 * (AB["base_te"] + BA["base_te"]),
        "base_insample": 0.5 * (AB["base_tr"] + BA["base_tr"]),
        "cov": {},
    }
    for name in covs:
        a, b = AB["cov"][name], BA["cov"][name]
        res["cov"][name] = {
            "r2_full_oos": 0.5 * (a["full_te"] + b["full_te"]),
            "incremental_oos": 0.5 * (a["incr_te"] + b["incr_te"]),
            "incremental_insample": 0.5 * (a["incr_tr"] + b["incr_tr"]),
            "incremental_oos_AB": a["incr_te"],
            "incremental_oos_BA": b["incr_te"],
        }
    return res


# ------------------------------------------------------------ bases and features
def build_base_B(kerdock, first_eff):
    """S15 Base-B: 256 linear s_m + 256 diag s_m^2 + top-16 cross (633 cols)."""
    U_f = np.linalg.svd(first_eff.astype(np.float64), full_matrices=False)[0]
    s_base = kerdock.astype(np.float64) @ U_f
    s_dbl = np.vstack([s_base, -s_base])
    diag_sq = s_dbl ** 2
    iu = np.triu_indices(CROSS_TOPB, k=1)
    cross = s_dbl[:, iu[0]] * s_dbl[:, iu[1]]
    return np.hstack([s_dbl, diag_sq, cross])


def build_cell_features(pre1):
    """Sign-pattern features on the doubled direction set.

    bits row layout matches ybar: [0:N_BASE] = u (pre1 > 0), [N_BASE:] = -u
    (pre1 < 0).  Returns (covs dict, census dict, bits).
    """
    bits_u = pre1 > 0
    bits_mu = pre1 < 0
    n_exact_zero = int((pre1 == 0).sum())
    bits = np.vstack([bits_u, bits_mu])                     # (N_FULL, 256) bool

    # (a) active count (== 256 * S15 C1 firing rate; affine -> identical R^2)
    cnt = bits.sum(axis=1).astype(np.float64)

    # (b) exact cell identity via packed bytes (collision-free perfect hash)
    packed = np.packbits(bits, axis=1)                      # (N_FULL, 32) uint8
    cells, inverse, counts = np.unique(
        packed, axis=0, return_inverse=True, return_counts=True)
    inverse = inverse.ravel()
    # np.unique returns cells in lexicographic packed-byte order, so a stable
    # argsort on -counts breaks frequency ties lexicographically.
    order = np.argsort(-counts, kind="stable")
    census = {
        "n_directions": int(N_FULL),
        "n_distinct_cells": int(cells.shape[0]),
        "n_singleton_cells": int((counts == 1).sum()),
        "max_cell_count": int(counts.max()),
        "top10_cell_counts": [int(c) for c in counts[order[:10]]],
        "n_exact_zero_preactivations": n_exact_zero,
    }
    covs = {"active_count": cnt[:, None]}
    for k in K_CELLS:
        top_ids = order[:k]
        ind = (inverse[:, None] == top_ids[None, :]).astype(np.float64)
        covs[f"cells_k{k}"] = ind

    # (c) Hamming distance to the per-net modal pattern -- two readings.
    # majority: per-unit majority vote over BASE directions (doubled set is
    # exactly tied at 1/2 per unit by antipodality).
    maj = (bits_u.sum(axis=0) > (N_BASE / 2.0))             # (256,) bool
    dham_maj = (bits != maj[None, :]).sum(axis=1).astype(np.float64)
    # literal: the most frequent full pattern (tie-break lexicographic).
    modal_packed = cells[order[0]]
    modal_bits = np.unpackbits(modal_packed)[:WIDTH].astype(bool)
    dham_lit = (bits != modal_bits[None, :]).sum(axis=1).astype(np.float64)
    covs["hamming_modal_majority"] = dham_maj[:, None]
    covs["hamming_modal_literal"] = dham_lit[:, None]
    census["modal_majority_vs_literal_hamming"] = int(
        (maj != modal_bits).sum())
    return covs, census


# ------------------------------------------------------------ instrument check
def injection_check(base, covs, f, split_seed, inj_r2=1e-3):
    """Inject a synthetic ~inj_r2 signal along the Hamming covariate; the
    pipeline must recover it.  Confirms sensitivity far above the 2.63e-5 bar."""
    z = covs["hamming_modal_majority"][:, 0].copy()
    # residualize z against the base in-sample (so the injected signal is
    # orthogonal to degree-<=2 and lands entirely in the incremental)
    mu = base.mean(axis=0)
    Bc = base - mu
    XtX = Bc.T @ Bc
    d = np.trace(XtX) / XtX.shape[0]
    beta = np.linalg.solve(XtX + np.eye(XtX.shape[0]) * (RIDGE_REL * d),
                           Bc.T @ (z - z.mean()))
    z_perp = (z - z.mean()) - Bc @ beta
    c = np.sqrt(inj_r2 * f.var() / z_perp.var())
    f_inj = f + c * z_perp
    res = incremental_oos(
        base, {"hamming_modal_majority": covs["hamming_modal_majority"]},
        f_inj, split_seed)
    pre = incremental_oos(
        base, {"hamming_modal_majority": covs["hamming_modal_majority"]},
        f, split_seed)["cov"]["hamming_modal_majority"]["incremental_oos"]
    got = res["cov"]["hamming_modal_majority"]["incremental_oos"]
    return {"injected_r2": inj_r2,
            "recovered_incremental_oos": got,
            "preexisting_incremental_oos": pre,
            "net_recovered": got - pre}


# ------------------------------------------------------------------------- main
def main():
    t0 = time.perf_counter()
    print("S18 ReLU cell-membership probe", flush=True)
    kerdock = n8a.load_kerdock_directions()

    s15 = json.loads(S15_JSON.read_text(encoding="utf-8"))

    results = {
        "ledger_id": "s18_cell_membership_probe",
        "date": "2026-08-10",
        "config": {
            "net_seeds": list(NET_SEEDS), "depth": DEPTH, "width": WIDTH,
            "rotation_seed_formula": "900000 + net_seed*1000 + 0 (r=0)",
            "n_base": N_BASE, "n_full": N_FULL, "radius": MEAN_CHI,
            "target": "f(u) = S5 ybar (neuron-averaged final post-ReLU)",
            "base": "S15 Base-B: 256 linear s_m + 256 diag s_m^2 + top-16 "
                    "cross = 633 cols (spans all deg-1, exact ||pre1||^2)",
            "feature_sets": {
                "active_count": "CONTROL (== 256*S15 C1), not gated",
                "cells_k{16,64,256}": "top-k most-frequent-cell indicators, "
                                      "exact packed-bit cell identity",
                "hamming_modal_majority": "Hamming dist to per-unit majority "
                                          "pattern (over base directions)",
                "hamming_modal_literal": "Hamming dist to most-frequent full "
                                         "pattern (lexicographic tie-break)",
            },
            "gate_quantity": "swap-halves OOS incremental R^2 beyond Base-B",
            "gates": {
                "kill": f"all gated sets < {NOISE_COST} on all 3 nets",
                "signal": f"any gated set >= {SIGNAL_BAR} on 2+ nets",
                "else": "INCONCLUSIVE",
                "gated_sets": list(GATED_SETS),
            },
            "prediction_on_record": "KILL",
            "interpretations": [
                "arm (a) active_count treated as CONTROL per the "
                "predeclaration parenthetical; excluded from gating; used to "
                "reproduce S15 C1 (pipeline cross-check)",
                "'hashed sign-pattern bucket' implemented as collision-free "
                "exact packed-bit cell identity (a perfect hash)",
                "'modal pattern' computed under BOTH readings (bitwise "
                "majority; literal most-frequent pattern); both gated, KILL "
                "requires both below bar",
            ],
        },
        "reuse_verification": {"d1_max_abs_diff": {},
                               "s15_c1_reproduction": {}},
        "census": {}, "nets": {}, "permutation_null": {},
        "instrument_injection": {}, "gate_evaluation": {}, "verdict": None,
    }

    per_set_per_net = {}     # set -> [3 net OOS incrementals]
    null_pool = {}           # set -> list over nets x perms

    for seed in NET_SEEDS:
        tn = time.perf_counter()
        weights = n8a.he_mlp_weights(seed)
        rot = n8a.haar_rotation(rot_seed(seed))
        first_eff = (rot.T @ weights[0]).astype(np.float32)
        pre1 = kerdock @ first_eff                     # (N_BASE, WIDTH) f32

        arr = np.load(S5_DIR / f"s5_net{seed}_arrays.npz")
        f = arr["ybar"].astype(np.float64)
        d1_saved = arr["d1"].astype(np.float64)
        arr.close()

        # reuse check: recompute d1 from my pre1, compare (S15-exact formula)
        col1 = np.linalg.norm(first_eff.astype(np.float64), axis=0)
        m1 = (np.abs(pre1.astype(np.float64)) / col1[None, :]).min(axis=1) / MEAN_CHI
        d1_diff = float(np.abs(np.concatenate([m1, m1]) - d1_saved).max())
        results["reuse_verification"]["d1_max_abs_diff"][str(seed)] = d1_diff

        base_B = build_base_B(kerdock, first_eff)
        covs, census = build_cell_features(pre1)
        results["census"][str(seed)] = census

        split_seed = 777_000 + seed
        o = incremental_oos(base_B, covs, f, split_seed)

        # S15 C1 reproduction (arm (a) == affine transform of C1)
        c1_ref = (s15["nets"][str(seed)]["covariate_sets_baseB"]
                  ["C1_firing_rate"]["incremental_oos"])
        results["reuse_verification"]["s15_c1_reproduction"][str(seed)] = {
            "s15_C1_incremental_oos": c1_ref,
            "s18_active_count_incremental_oos":
                o["cov"]["active_count"]["incremental_oos"],
            "abs_diff": abs(c1_ref -
                            o["cov"]["active_count"]["incremental_oos"]),
        }

        # permutation null (3 perms, same split, same pipeline)
        nulls = {}
        rngp = np.random.default_rng(555_000 + seed)
        for p in range(N_PERM):
            fp = f[rngp.permutation(N_FULL)]
            op = incremental_oos(base_B, covs, fp, split_seed)
            for name in covs:
                nulls.setdefault(name, []).append(
                    op["cov"][name]["incremental_oos"])
                null_pool.setdefault(name, []).append(
                    op["cov"][name]["incremental_oos"])
        results["permutation_null"][str(seed)] = {
            name: {"incremental_oos_per_perm": v,
                   "mean": float(np.mean(v)),
                   "max_abs": float(np.max(np.abs(v)))}
            for name, v in nulls.items()}

        # instrument injection check
        inj = injection_check(base_B, covs, f, split_seed)
        results["instrument_injection"][str(seed)] = inj

        results["nets"][str(seed)] = {
            "base_B": {"r2_base_oos": o["base_oos"],
                       "r2_base_insample": o["base_insample"]},
            "covariate_sets": o["cov"],
            "wall_s": round(time.perf_counter() - tn, 1),
        }
        for name in covs:
            per_set_per_net.setdefault(name, []).append(
                o["cov"][name]["incremental_oos"])

        print(f"  net {seed}: base_oos={o['base_oos']:.4f} "
              f"cells: {census['n_distinct_cells']} distinct / "
              f"{census['n_singleton_cells']} singleton / "
              f"max_count={census['max_cell_count']} "
              f"(d1_diff={d1_diff:.1e})", flush=True)
        for name in covs:
            r = o["cov"][name]
            print(f"      {name:24s} incr_oos={r['incremental_oos']:+.3e}  "
                  f"(AB {r['incremental_oos_AB']:+.3e} / "
                  f"BA {r['incremental_oos_BA']:+.3e})  "
                  f"null_max_abs={max(abs(x) for x in nulls[name]):.1e}",
                  flush=True)
        print(f"      injection: recovered {inj['recovered_incremental_oos']:.2e} "
              f"of injected {inj['injected_r2']:.0e} "
              f"(wall={results['nets'][str(seed)]['wall_s']}s)", flush=True)

    # ------------------------------------------------------------ gate
    gate = results["gate_evaluation"]
    gate["per_set_per_net_incremental_oos"] = {
        k: [float(x) for x in v] for k, v in per_set_per_net.items()}
    gate["noise_cost_bar"] = NOISE_COST
    gate["signal_bar"] = SIGNAL_BAR
    kill_ok = all(x < NOISE_COST
                  for name in GATED_SETS for x in per_set_per_net[name])
    signal_sets = [name for name in GATED_SETS
                   if sum(1 for x in per_set_per_net[name]
                          if x >= SIGNAL_BAR) >= 2]
    gate["all_gated_below_noise_cost_all_nets"] = bool(kill_ok)
    gate["signal_sets_ge_1e-4_on_2plus_nets"] = signal_sets
    best_name = max(GATED_SETS, key=lambda n: max(per_set_per_net[n]))
    best_val = max(per_set_per_net[best_name])
    gate["best_gated_incremental_oos"] = {"set": best_name,
                                          "value": float(best_val)}
    gate["null_pool_max_abs_per_set"] = {
        name: float(np.max(np.abs(null_pool[name]))) for name in null_pool}

    if signal_sets:
        verdict = (f"SIGNAL: gated set(s) {signal_sets} reached OOS "
                   f"incremental R^2 >= {SIGNAL_BAR} on 2+ nets.")
    elif kill_ok:
        verdict = (f"KILL: every gated cell-membership feature set is below "
                   f"the fitting-noise cost {NOISE_COST} on all 3 nets "
                   f"(best = {best_val:.3e} for {best_name}). The last named "
                   f"crack in the dispersion family closes.")
    else:
        verdict = (f"INCONCLUSIVE: best gated OOS incremental R^2 = "
                   f"{best_val:.3e} ({best_name}) in [{NOISE_COST}, "
                   f"{SIGNAL_BAR}) on at least one net; neither bar met.")
    results["verdict"] = verdict
    results["total_wall_s"] = round(time.perf_counter() - t0, 1)

    out = HERE / "s18_results.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"\nVERDICT: {verdict}")
    print(f"results -> {out}  (wall {results['total_wall_s']}s)", flush=True)


if __name__ == "__main__":
    main()
