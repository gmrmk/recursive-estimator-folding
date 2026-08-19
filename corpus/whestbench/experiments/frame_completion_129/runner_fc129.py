"""frame_completion_129_three_arm_regime_decomposition_v1 -- the cell runner.

Three Public100 harness invocations under one sealed authorization:

  arm A  126 Haar-random orthonormal frames  (the shipped row-blocked carrier)
  arm B  the 129-frame real-MUB completion   ({I} u {H diag(phi_s)/16})
  arm C  the Kerdock-126 design              ({H diag(phi_s)/16, s = 2..127})

Same dataset, same split, same 100 networks in the same order, same harness
seed, same flop budget, same estimator code apart from setup()'s frame set.
Pairing is per network and holds across all three arms.

--------------------------------------------------------------------------
THIRD-ARM NOTE (amendment H2, AGENT_CHANNEL.md [2026-08-19 ~01:0x UTC],
"PRE-REGISTRATION - the A_4 reconciliation law, filed BEFORE the 129 cell
runs")
--------------------------------------------------------------------------
Arm C exists to DECOMPOSE the arm A -> arm B contrast, and it is REPORTED,
never gated.  Arm A -> arm B moves two things at once: the design family (Haar
-> mutually unbiased) and the point count (126 -> 129 frames).  Arm C holds the
point count at arm A's value and the design family at arm B's, which splits the
contrast into its two physical causes:

    A -> C   DESIGN QUALITY.  Same 126 frames, same billed rows; A_4 falls from
             3.136387e-05 to 7.350908e-07, a factor of exactly 128/3.
    C -> B   COMPLETION.      Same design family; A_4 falls from 7.350908e-07
             to exactly zero, and the score law charges for three more frames.

The identity log R(A->B) = log R(A->C) + log R(C->B) is exact, so the split is
an accounting of the same measured quantity rather than a second hypothesis.
H2 predicts the design-quality leg carries most of the gain and the completion
leg is small; the structural forecast in this runner puts the design-quality
share of the forecast log gain at 0.858, which is a prediction, not a result.

THE GATE DOES NOT BECOME A THREE-WAY TEST.  Exactly one scalar is gated --
frame_completion_129_margin_t, the studentized distance of the arm A vs arm B
adjusted-score ratio from the declared margin.  Arm C cannot move it, cannot
create a second chance at PASS, and is not compared against the margin at any
point.  Arm C is held to the same structural integrity checks as A and B
(no failed networks, off the score-multiplier floor, identical network order,
finite positive entries) and a violation there is a fail-closed protocol kill,
because all three arms run back to back on one host under one authorization and
a structural failure in any of them impugns the environment the other two ran
in.  What arm C can never do is change a disposition.

--------------------------------------------------------------------------
The gated statistic is the FLOP-only adjusted-score ratio.  The harness's own
per-MLP score multiplier is max(0.1, C_m/B) with C_m = F_m + lambda*R_m, and
R_m is residual wall time -- machine noise that is not reproducible and that
measured 12% of C on this host.  F_m is bit-reproducible (verified).  So the
primary estimand recomputes the same score law with the wall-time channel held
out, and the lawful lambda-included ratio rides along as a reported co-primary.
Neither is chosen after seeing the run; this paragraph is the predeclaration.

Emits exactly one JSON object on the last stdout line.  Any structural failure
prints a diagnostic JSON and exits nonzero, which the harness records as
PROTOCOL_KILL_MALFORMED_METRICS -- a broken measurement must never be able to
look like a KILL.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

# ------------------------------------------------------------------ constants
REPO = Path("C:/Users/strid/.claude/skills/recursive-estimator-folding")
CELL = REPO / "corpus/whestbench/experiments/frame_completion_129"
WORKROOT = Path(
    "C:/Users/strid/Documents/Codex/2026-08-02/https-chatgpt-com-share-6a5556ed-2e1c"
)
# The pinned v0.14 console script.  NOT `python -m whestbench.cli`: that module
# carries no __main__ guard and exits silently with no output, which would have
# spent the cell's one authorization on a protocol kill.  Verified off protocol.
WHEST = WORKROOT / "work/whest-v014/Scripts/whest.exe"
DATASET = WORKROOT / "work/whest-full"

HARNESS_SEED = 0
BOOTSTRAP_SEED = 20260818
N_MLPS = 100
FLOP_BUDGET = 272_000_000_000
BOOTSTRAP_DRAWS = 20_000

ARMS = ("armA", "armB", "armC")

# Declared margin on the adjusted-score ratio.  Set between the two competing
# public claims this cell adjudicates (a ~19% completion gain and a ~0.9% one)
# and an order of magnitude above the smaller, so that PASS and KILL each name
# one of them.  Fixed before any production run.
MARGIN = 0.05
T_CRIT = 1.9842169515086827          # two-sided 95%, Student t, df = 99

WIDTH = 256
FRAMES_A, FRAMES_B, FRAMES_C = 126, 129, 126

# Pre-registered H1 priors (AGENT_CHANNEL.md [2026-08-19 ~01:0x UTC]).  These
# are REPORTED comparisons against a prior filed before any production run.
# They gate nothing; the only gated scalar is the margin statistic below.
H1_MSE_RATIO_BAND = (0.78, 0.86)
H1_FALSIFIER_MSE_RATIO = 0.95

# Below this the log-gain denominator is too small for a share to mean
# anything, and the decomposition is reported as its two legs only.
LOG_SHARE_EPS = 1e-3

# Gross-breakage band on arm A's aggregate raw final-layer MSE.  Wide on
# purpose: it exists to catch a broken asset, a wrong dataset or a wrong
# estimator, not to discriminate any hypothesis.  Applied to arm A alone,
# because arm A is the shipped carrier whose value is already known; arms B
# and C carry the quantities under test and must not be banded.
ARM_A_MSE_BAND = (2.0e-7, 4.5e-7)


def fail(reason: str, **extra):
    payload = {"runner_failure": reason,
               "config": {"seeds": [HARNESS_SEED, BOOTSTRAP_SEED]}}
    payload.update(extra)
    print(json.dumps(payload, sort_keys=True))
    sys.exit(1)


# ------------------------------------------------------- exact design defects
def gegenbauer(l: int, t: Fraction, d: int = WIDTH) -> Fraction:
    """P_l for S^(d-1) normalized to P_l(1) = 1, exact rational recurrence
    (k + d - 2) P_(k+1) = (2k + d - 2) t P_k - k P_(k-1)."""
    if l == 0:
        return Fraction(1)
    prev, cur = Fraction(1), t
    for k in range(1, l):
        cur, prev = (
            (Fraction(2 * k + d - 2) * t * cur - Fraction(k) * prev)
            / Fraction(k + d - 2),
            cur,
        )
    return cur


def defect_mub(l: int, m: int, d: int = WIDTH) -> Fraction:
    """A_l for m antipodally doubled mutually unbiased bases.  From any point
    the inner products are +1, -1, 2(d-1) zeros inside its own doubled frame,
    and 2d(m-1) at +-1/sqrt(d).  Even l only; odd l vanishes by antipodality
    and this formula does not apply there.

    Arm C is covered by this branch as well as arm B: the Kerdock trim is a
    mutually unbiased family, so any 126-subset of it has all cross inner
    products at modulus 1/sqrt(d)."""
    inv = Fraction(1, int(math.isqrt(d)))
    return (
        Fraction(2) * gegenbauer(l, Fraction(1), d)
        + Fraction(2 * (d - 1)) * gegenbauer(l, Fraction(0), d)
        + Fraction(2 * d * (m - 1)) * gegenbauer(l, inv, d)
    ) / Fraction(2 * d * m)


def defect_random(l: int, m: int, d: int = WIDTH) -> Fraction:
    """E[A_l] for m Haar-random orthonormal frames, antipodally doubled.  Each
    cross-frame row is marginally uniform on the sphere and E[P_l] = 0 there
    for l >= 1, so only the own-frame block survives."""
    return (
        Fraction(2) * gegenbauer(l, Fraction(1), d)
        + Fraction(2 * (d - 1)) * gegenbauer(l, Fraction(0), d)
    ) / Fraction(2 * d * m)


# ------------------------------------------------------------- harness driver
def run_arm(name: str) -> dict:
    out = CELL / f"report_{name}.json"
    argv = [
        str(WHEST), "run",
        "--estimator", str(CELL / name / "estimator.py"),
        "--dataset", str(DATASET),
        "--split", "full",
        "--n-mlps", str(N_MLPS),
        "--runner", "subprocess",
        "--seed", str(HARNESS_SEED),
        "--flop-budget", str(FLOP_BUDGET),
        "--detail", "full",
        "--format", "json",
    ]
    proc = subprocess.run(argv, capture_output=True, text=True, errors="replace")
    if proc.returncode != 0:
        fail(f"{name}: harness exited {proc.returncode}",
             stderr_tail=(proc.stderr or "")[-1200:])
    try:
        report = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        fail(f"{name}: harness stdout was not JSON",
             stdout_head=(proc.stdout or "")[:600])
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


# ------------------------------------------------------------------- analysis
def _channels(name: str, report: dict) -> dict:
    """Pull one arm's per-network channels and fail closed on anything that is
    not a measurement."""
    results = report.get("results", {})
    per_mlp = results.get("per_mlp") or []
    if len(per_mlp) != N_MLPS:
        fail("arm length mismatch", arm=name, n=len(per_mlp), expected=N_MLPS)
    if int(results.get("n_failed_mlps", 1)):
        fail("a network failed; a zeroed prediction is not a measurement",
             arm=name, failed=results.get("n_failed_mlps"),
             breakdown=results.get("failure_breakdown"))
    out = {
        "names": [e.get("mlp_name") for e in per_mlp],
        "mse": np.array([e["final_layer_mse"] for e in per_mlp], dtype=np.float64),
        "flops": np.array([e["flops_used"] for e in per_mlp], dtype=np.float64),
        "compute": np.array([e["effective_compute"] for e in per_mlp],
                            dtype=np.float64),
        "lawful": np.array([e["adjusted_final_layer_score"] for e in per_mlp],
                           dtype=np.float64),
    }
    for label in ("mse", "flops", "lawful"):
        arr = out[label]
        if not np.all(np.isfinite(arr)) or not np.all(arr > 0):
            fail(f"{label} carries a nonfinite or nonpositive entry", arm=name)
    # The 1/N-vs-cost break-even this cell is about only exists above the 0.1
    # multiplier floor; at the floor the cost channel is pinned and the gate
    # premise is void.
    out["mult"] = np.maximum(0.1, out["flops"] / FLOP_BUDGET)
    if float(out["mult"].min()) <= 0.1:
        fail("a network sits on the score-multiplier floor; the metered-regime "
             "premise of the break-even does not hold",
             arm=name, min_mult=float(out["mult"].min()))
    out["score_flop"] = out["mse"] * out["mult"]
    return out


def analyse(reports: dict) -> dict:
    arm = {name: _channels(name, reports[name]) for name in ARMS}

    # Pairing across all three arms, element by element.
    base = arm["armA"]["names"]
    for name in ARMS[1:]:
        other = arm[name]["names"]
        if base != other:
            first = next(i for i, (x, y) in enumerate(zip(base, other)) if x != y)
            fail("pairing broken: network order differs between arms",
                 arm=name, first_divergence=first, a=base[first], b=other[first])

    agg_mse_a = float(arm["armA"]["mse"].mean())
    if not (ARM_A_MSE_BAND[0] <= agg_mse_a <= ARM_A_MSE_BAND[1]):
        fail("arm A aggregate raw MSE is outside the gross-breakage band",
             observed=agg_mse_a, band=list(ARM_A_MSE_BAND))

    # Equal network weights, mean of per-network products -- the campaign's
    # Scorehat convention and the harness's own aggregate.  A ratio of means,
    # never a mean of ratios.
    def ratio(field, num, den):
        return float(arm[num][field].mean() / arm[den][field].mean())

    r_flop_ab = ratio("score_flop", "armB", "armA")     # THE GATED CONTRAST
    r_flop_ac = ratio("score_flop", "armC", "armA")     # design quality
    r_flop_cb = ratio("score_flop", "armB", "armC")     # completion
    r_lawful_ab = ratio("lawful", "armB", "armA")
    r_mse_ab = ratio("mse", "armB", "armA")
    r_mse_ac = ratio("mse", "armC", "armA")
    r_mse_cb = ratio("mse", "armB", "armC")

    # One resampling of network indices, applied to every arm, so the bootstrap
    # respects the pairing exactly as the point estimates do.
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    idx = rng.integers(0, N_MLPS, size=(BOOTSTRAP_DRAWS, N_MLPS))

    def boot_log(field, num, den):
        return np.log(arm[num][field][idx].mean(axis=1)
                      / arm[den][field][idx].mean(axis=1))

    boot_ab = boot_log("score_flop", "armB", "armA")
    boot_ac = boot_log("score_flop", "armC", "armA")
    boot_cb = boot_log("score_flop", "armB", "armC")
    boot_lawful = boot_log("lawful", "armB", "armA")

    se_ab = float(boot_ab.std(ddof=1))
    if not math.isfinite(se_ab) or se_ab <= 0.0:
        fail("bootstrap standard error is degenerate", se=se_ab)

    metric = (math.log(r_flop_ab) - math.log(1.0 - MARGIN)) / se_ab

    def ci95(samples):
        lo, hi = np.percentile(samples, [2.5, 97.5])
        return [float(math.exp(lo)), float(math.exp(hi))]

    # Per-network billed-FLOP ratio.  Arms A and B differ by a fixed +3/126 in
    # row count and arms A and C by nothing at all, so a per-network departure
    # from those constants is the fold's dead/kink/on regime split moving
    # between arms -- the one confound this design cannot remove, reported
    # rather than gated.
    f_ratio_ab = arm["armB"]["flops"] / arm["armA"]["flops"]
    f_ratio_ac = arm["armC"]["flops"] / arm["armA"]["flops"]
    row_ratio_ab = (FRAMES_B * WIDTH) / (FRAMES_A * WIDTH)
    row_ratio_ac = (FRAMES_C * WIDTH) / (FRAMES_A * WIDTH)

    a_a = {l: defect_random(l, FRAMES_A) for l in (4, 6, 8)}
    a_b = {l: defect_mub(l, FRAMES_B) for l in (4, 6, 8)}
    a_c = {l: defect_mub(l, FRAMES_C) for l in (4, 6, 8)}
    if a_b[4] != 0:
        fail("the 129-frame completion's degree-four defect is not exactly zero; "
             "the structural premise of the cell is broken")
    # The design-quality leg's own structural premise, checked in exact rational
    # arithmetic: the Haar-frame degree-four defect is 128/3 times the Kerdock
    # one at equal point count.  A broken recurrence fails here, not silently.
    if a_a[4] / a_c[4] != Fraction(128, 3):
        fail("the degree-four suppression between arm A and arm C is not the "
             "exact structural constant; the defect recurrence is broken",
             observed=float(a_a[4] / a_c[4]))

    # Structural forecast from the manuscript's committed variance shares for
    # the Kerdock carrier.  Arm C's forecast variance is that committed value
    # BY CONSTRUCTION (the per-degree energies were solved from it), so the arm
    # C forecast is an identity, not an independent prediction; the arm A and
    # arm B forecasts are the predictive content.
    v126k = 2.4977e-07
    share4, share8 = 0.004497, 0.86
    share6 = 1.0 - share4 - share8
    energy = {4: share4 * v126k / float(a_c[4]),
              6: share6 * v126k / float(a_c[6]),
              8: share8 * v126k / float(a_c[8])}

    def forecast(defects):
        return sum(energy[l] * float(defects[l]) for l in (4, 6, 8))

    v_a, v_b, v_c = forecast(a_a), forecast(a_b), forecast(a_c)
    log_gain_ab = math.log(r_mse_ab)
    forecast_share = (math.log(v_c / v_a) / math.log(v_b / v_a)) if v_b != v_a else None

    return {
        # ---- THE ONE GATED SCALAR: arm A vs arm B, the completion question.
        "frame_completion_129_margin_t": metric,
        "verdict_inputs": {
            "gated_contrast": "armA_vs_armB",
            "margin": MARGIN,
            "t_crit": T_CRIT,
            "score_flop_ratio": r_flop_ab,
            "score_flop_ci95": ci95(boot_ab),
            "score_flop_bootstrap_se_log": se_ab,
        },
        "co_primary_lawful": {
            "score_lambda_ratio": r_lawful_ab,
            "score_lambda_ci95": ci95(boot_lawful),
            "score_lambda_bootstrap_se_log": float(boot_lawful.std(ddof=1)),
            "agrees_in_sign_with_primary":
                (r_lawful_ab - 1.0) * (r_flop_ab - 1.0) >= 0.0,
        },
        # ---- REPORTED, NEVER GATED: the third arm's decomposition (H2).
        "decomposition_arm_c": {
            "role": "reported_co_primary_not_gated",
            "design_quality_leg_a_to_c": {
                "score_flop_ratio": r_flop_ac,
                "score_flop_ci95": ci95(boot_ac),
                "score_flop_bootstrap_se_log": float(boot_ac.std(ddof=1)),
                "raw_mse_ratio": r_mse_ac,
            },
            "completion_leg_c_to_b": {
                "score_flop_ratio": r_flop_cb,
                "score_flop_ci95": ci95(boot_cb),
                "score_flop_bootstrap_se_log": float(boot_cb.std(ddof=1)),
                "raw_mse_ratio": r_mse_cb,
            },
            "log_additivity_residual":
                math.log(r_flop_ab) - math.log(r_flop_ac) - math.log(r_flop_cb),
            "design_quality_share_of_log_gain":
                (math.log(r_mse_ac) / log_gain_ab
                 if abs(log_gain_ab) >= LOG_SHARE_EPS else None),
            "h2_prediction": "most of the gain is design quality, not completion",
            "h2_forecast_design_quality_share": forecast_share,
        },
        "h1_pre_registered_check": {
            "role": "reported_prior_versus_outcome_not_gated",
            "mse_ratio_band": list(H1_MSE_RATIO_BAND),
            "mse_ratio_observed_a_to_b": r_mse_ab,
            "inside_band": H1_MSE_RATIO_BAND[0] <= r_mse_ab <= H1_MSE_RATIO_BAND[1],
            "falsifier_threshold": H1_FALSIFIER_MSE_RATIO,
            "falsified": r_mse_ab > H1_FALSIFIER_MSE_RATIO,
        },
        "components": {
            "raw_mse_ratio": r_mse_ab,
            "aggregate_mse_arm_a": agg_mse_a,
            "aggregate_mse_arm_b": float(arm["armB"]["mse"].mean()),
            "aggregate_mse_arm_c": float(arm["armC"]["mse"].mean()),
            "effective_compute_ratio_a_to_b": ratio("compute", "armB", "armA"),
            "effective_compute_ratio_a_to_c": ratio("compute", "armC", "armA"),
            "billed_flop_ratio_a_to_b": ratio("flops", "armB", "armA"),
            "billed_flop_ratio_a_to_c": ratio("flops", "armC", "armA"),
            "row_count_ratio_a_to_b": row_ratio_ab,
            "row_count_ratio_a_to_c": row_ratio_ac,
            "mean_multiplier_arm_a": float(arm["armA"]["mult"].mean()),
            "mean_multiplier_arm_b": float(arm["armB"]["mult"].mean()),
            "mean_multiplier_arm_c": float(arm["armC"]["mult"].mean()),
        },
        "regime_confound_instrument": {
            "a_to_b_per_net_flop_ratio_min": float(f_ratio_ab.min()),
            "a_to_b_per_net_flop_ratio_median": float(np.median(f_ratio_ab)),
            "a_to_b_per_net_flop_ratio_max": float(f_ratio_ab.max()),
            "a_to_b_nets_within_half_percent_of_row_ratio":
                int(np.sum(np.abs(f_ratio_ab - row_ratio_ab) <= 0.005)),
            "a_to_c_per_net_flop_ratio_min": float(f_ratio_ac.min()),
            "a_to_c_per_net_flop_ratio_median": float(np.median(f_ratio_ac)),
            "a_to_c_per_net_flop_ratio_max": float(f_ratio_ac.max()),
            "a_to_c_nets_within_half_percent_of_row_ratio":
                int(np.sum(np.abs(f_ratio_ac - row_ratio_ac) <= 0.005)),
        },
        "structure": {
            "a4_arm_a_random_frames": float(a_a[4]),
            "a4_arm_b_mub_completion": float(a_b[4]),
            "a4_arm_c_kerdock_design": float(a_c[4]),
            "a6_arm_a": float(a_a[6]), "a6_arm_b": float(a_b[6]),
            "a6_arm_c": float(a_c[6]),
            "a8_arm_a": float(a_a[8]), "a8_arm_b": float(a_b[8]),
            "a8_arm_c": float(a_c[8]),
            "a4_suppression_factor_arm_a_over_arm_c": float(a_a[4] / a_c[4]),
            "forecast_variance_arm_a": v_a,
            "forecast_variance_arm_b": v_b,
            "forecast_variance_arm_c": v_c,
            "forecast_mse_ratio_a_to_b": v_b / v_a,
            "forecast_mse_ratio_a_to_c": v_c / v_a,
            "forecast_mse_ratio_c_to_b": v_b / v_c,
            "forecast_minus_measured_mse_ratio_a_to_b": (v_b / v_a) - r_mse_ab,
            "forecast_minus_measured_mse_ratio_a_to_c": (v_c / v_a) - r_mse_ac,
        },
        "config": {"seeds": [HARNESS_SEED, BOOTSTRAP_SEED]},
    }


def main() -> int:
    required = [WHEST, DATASET]
    for name in ARMS:
        required.append(CELL / name / "estimator.py")
    required.append(CELL / "armB/kerdock_phases.npz")
    required.append(CELL / "armC/kerdock_phases.npz")
    for path in required:
        if not path.exists():
            fail("declared input is missing at run time", path=str(path))
    reports = {name: run_arm(name) for name in ARMS}
    print(json.dumps(analyse(reports), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
