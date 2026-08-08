"""WC-1 Winner-Ablation catalog for the frozen Kerdock v3 estimator.

This is an AUDIT harness, not a promotion ladder.  Baseline = the full
validated composition (frozen ``estimator.Estimator``).  Each arm is a subclass
that disables exactly ONE winner component; each arm REPORTS its paired
final-layer MSE ratio vs the baseline (with a bootstrap 95% CI), its billed
FLOPs, and its worst-net behaviour.  Nothing here edits a frozen source.

Panel nets: synthetic He-init width-256 depth-32 nets (t3-style, seeds
101/202/303), byte-identical to the recipe m181/m180/n8c used.  Truth: the
cached m181 3.5M-sample final-layer mean vectors are reused read-only (verified
this session: a 300k independent MC on he(101) matched the cached net101 means
to relative L2 5e-4, pure MC noise at that sample count).

Firewall: cached m181 truths + kerdock_phases.npz + sobol_owen_u32.npz read
ONLY; frozen v3 chain imported read-only (bytecode writes disabled); synthetic
nets only; no dataset / truth-of-record / scorer / submission access; single
process; all writes stay inside this wc1 directory.

Rotation seeds: mlp.seed drives the estimator's Haar rotation (the estimator's
own randomization).  >= 12 replicate seeds per net give the paired sample.

Arm construction (documented deviations are LOUD in WC1_NOTES.md):
  A_frames     replace the 126-frame phased-Hadamard design with matched-n
               (32256) iid Gaussian directions, radially conditioned to the
               SAME mean-chi radius.  Isolates the spherical-design gain.
               [setup override -> iid substrate; radial_conditioning stays True]
  A_radial     iid substrate with radial_conditioning=False: true chi-radius
               directions + the frozen quadratic radius control-variate weights
               (the False branch already in the frozen predict).  Disables the
               exact mean-radius placement.  Shares the iid substrate with
               A_frames, so the ISOLATED radial effect = ratio(A_radial) /
               ratio(A_frames); the raw vs-baseline ratio bundles the design.
  A_prune      dead_alpha = -1e9: no cold-neuron pruning / pilot rescue; dense
               forward.  [single class-attr override]
  A_fold       on_alpha = +1e9: no analytic on-neuron folding of the 3 terminal
               layers; every non-dead terminal neuron is explicitly sampled
               (the fold's kink path).  Dead-analytic (pruning) is left intact
               so this isolates the fold, not the pruning.  [single class-attr
               override -- see WC1_NOTES.md for why this is the faithful fold
               ablation and no predict rewrite is needed]
  A_tangent    moment_tangent_lambda = 0.0: drop the first-moment tangent
               correction.  [single class-attr override]
  A_antithetic disable antipodal pairing: 2*n_base (64512) INDEPENDENT iid
               directions each sampled once (matched TOTAL sample count so
               downstream billing is comparable), instead of n_base directions
               and their antipodes.  [predict override -- fold3 body copied
               verbatim except the activation-construction block]
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True  # do not write .pyc into the frozen v3 dir

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c"
)
V3_DIR = (
    ROOT / "work" / "scorefloor_generation" / "kerdock_l1_owned_buffer"
    / "candidate_source_validator_v3"
)
M181_DIR = (
    ROOT / "publish" / "recursive-estimator-folding" / "corpus" / "whestbench"
    / "experiments" / "m181_terminal_smoothing"
)
sys.path.insert(0, str(V3_DIR))

import flopscope as flops           # noqa: E402
import flopscope.numpy as fnp       # noqa: E402
from whestbench import SetupContext  # noqa: E402
from whestbench.domain import MLP    # noqa: E402

flops.configure(symmetry_warnings=False)

from estimator import Estimator as KerdockV3            # noqa: E402 (frozen)
from base_estimator import _assemble_vector             # noqa: E402
from base_estimator import _diagonal_gaussian_pass      # noqa: E402
from fold_estimator import _initial_regimes             # noqa: E402
from fold_estimator import _refine_dead, _refine_on     # noqa: E402
from row_blocked_winograd import BLOCK_ROWS             # noqa: E402
from row_blocked_winograd import RowBlockedBatchedWinograd  # noqa: E402

WIDTH, DEPTH = 256, 32
N_FRAMES = 126
N_BASE = N_FRAMES * WIDTH                 # 32,256 base directions
NET_SEEDS = (101, 202, 303)
REPLICATES = 12                            # >= predeclared 12
BUDGET_B = 272e9                           # competition budget B
METER_BUDGET = 10 ** 15                     # FlopScope meter ceiling
BOOTSTRAP_DRAWS = 4000
MEAN_CHI_256 = 15.98438266660852747

# audit-flag thresholds (from WC1_SPEC.md gates)
LOAD_BEARING_RATIO = 1.20                   # >= this worsening => load-bearing
REMOVABLE_MSE_TOL = 0.03                    # |ratio-1| < this AND bills > 2%B
REMOVABLE_BILL_FRAC = 0.02                  # of B
TAIL_DRIVER_FACTOR = 1.5                    # worst delta >= factor * mean delta


def he_mlp_weights(seed: int) -> list[np.ndarray]:
    """He-init f32 width-256 depth-32 net (t3-style; verbatim from m181)."""
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


def rot_seed(net_seed: int, rep: int) -> int:
    """Rotation-seed formula shared with n8a/n8c/m180/m181."""
    return 900_000 + net_seed * 1_000 + rep


def mean_radius_chi(width: int) -> float:
    """E[chi_width] = sqrt(2) * Gamma((w+1)/2) / Gamma(w/2) (= MEAN_CHI_256)."""
    return math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((width + 1.0) / 2.0)
        - math.lgamma(width / 2.0)
    )


# --------------------------------------------------------------------- arms
class _IIDSubstrate(KerdockV3):
    """Replace the frozen phased-Hadamard design with iid Gaussian directions.

    Everything downstream of the first product (antipodal pairing, pruning /
    pilot rescue, the 3-layer fold, the tangent correction, the row-blocked
    Winograd billing) is inherited unchanged from the frozen v3.  Only the
    sample DESIGN changes.  The design is fixed at setup (seeded by ctx.seed);
    per-rep variation comes from the inherited Haar rotation, exactly as for
    the frozen phased design.
    """

    _n_dirs = N_BASE

    def setup(self, ctx) -> None:
        self._context_width = ctx.width
        rng = fnp.random.default_rng(ctx.seed)
        gaussian = rng.standard_normal(
            (self._n_dirs, ctx.width), dtype=fnp.float32
        )
        if self.radial_conditioning:
            mean_radius = mean_radius_chi(ctx.width)
            radii = fnp.sqrt(fnp.sum(gaussian * gaussian, axis=1))
            gaussian = gaussian * (
                mean_radius / fnp.maximum(radii, 1e-12)
            )[:, None]
            self._radial_covariance = mean_radius * mean_radius / ctx.width
        else:
            self._radial_covariance = 1.0
        self._gaussian = gaussian
        self._winograd = RowBlockedBatchedWinograd(
            2 * self.n_base, ctx.width, BLOCK_ROWS
        )

    def _initial_sample_state(self):
        return self._gaussian

    def _first_sample_matmul(self, values, weight, *, out=None):
        return fnp.matmul(values, weight, out=out)


class A_frames(_IIDSubstrate):
    """iid directions at the frozen mean-chi radius (exact-radius sphere)."""

    radial_conditioning = True


class A_radial(_IIDSubstrate):
    """iid directions with TRUE chi radius + frozen quadratic CV weights."""

    radial_conditioning = False


class A_prune(KerdockV3):
    """No cold-neuron pruning / pilot rescue: dense forward."""

    dead_alpha = -1.0e9


class A_fold(KerdockV3):
    """No analytic on-fold of the terminal 3 layers: sample them (kink)."""

    on_alpha = 1.0e9


class A_tangent(KerdockV3):
    """Drop the first-moment tangent correction."""

    moment_tangent_lambda = 0.0


class A_antithetic(_IIDSubstrate):
    """2*n_base INDEPENDENT directions, no antipodal pairing (matched count).

    ``predict`` reproduces ``estimator.Estimator.predict`` (Haar wrapper) and
    ``fold3_estimator.Estimator.predict`` (body) VERBATIM, except the
    activation-construction block: instead of filling the back half with the
    antipode ``ReLU(-first_pre)``, all 2*n_base rows are filled from
    ``ReLU(first_pre)`` of 2*n_base independent directions.  radial_conditioning
    stays True (final_weights=None), matching A_frames so the isolated
    antithetic effect = ratio(A_antithetic) / ratio(A_frames).
    """

    radial_conditioning = True
    _n_dirs = 2 * N_BASE

    def predict(self, mlp, budget):  # Haar wrapper, mirrors frozen estimator.py
        if mlp.width != WIDTH:
            return super().predict(mlp, budget)
        rotation = self._haar_rotation(int(mlp.seed), mlp.width)
        first_weight = rotation.T @ mlp.weights[0]
        self._trace_stage("haar_absorbed")
        rotated = MLP(
            width=mlp.width, depth=mlp.depth,
            weights=[first_weight, *mlp.weights[1:]],
            seed=mlp.seed, name=mlp.name,
        )
        return self._predict_independent(rotated, budget)

    def _predict_independent(self, mlp, budget):
        # ---- fold3_estimator.Estimator.predict body (verbatim) ----------
        _ = budget
        z = self._initial_sample_state()
        if z is None:
            raise RuntimeError("setup() did not initialize the Gaussian net")

        analytic_means, analytic_alphas, firing, analytic_sigmas = (
            _diagonal_gaussian_pass(mlp)
        )
        if self.radial_conditioning:
            final_weights = None
        else:  # not reached (radial_conditioning=True); kept for fidelity
            radius_sq = fnp.sum(z * z, axis=1)
            q1 = radius_sq - 257.0
            q2 = radius_sq * radius_sq - 66563.0
            base_weights = (
                1.0 - (2600.0 / 537689.0) * q1 + (3.0 / 537689.0) * q2
            )
            final_weights = fnp.concatenate((base_weights, base_weights), axis=0)

        # >>> WC1 DEVIATION (antithetic ablation): independent, not antipodal.
        # Frozen v3 fills activation[:n_base]=ReLU(first_pre) and
        # activation[n_base:]=ReLU(-first_pre).  Here z has 2*n_base independent
        # rows and every row is ReLU(z @ W0); no antipode is formed.
        activation = fnp.empty((2 * self.n_base, mlp.width), dtype=fnp.float32)
        pre = self._first_sample_matmul(z, mlp.weights[0], out=activation)
        del z
        self._release_initial_sample_state()
        self._trace_stage("first_preactivation")
        x = activation
        fnp.maximum(pre, 0.0, out=x)
        del pre
        self._trace_stage("independent_activation")
        # <<< end WC1 DEVIATION.  Everything below is verbatim fold3.

        sigma0 = fnp.sqrt(fnp.sum(mlp.weights[0] * mlp.weights[0], axis=0))
        exact_first_mean = sigma0 / fnp.sqrt(2.0 * fnp.pi)
        first_moment_residual = fnp.mean(x, axis=0) - exact_first_mean
        first_variance_residual = (
            fnp.mean(x * x, axis=0)
            - 0.5 * self._radial_covariance * sigma0 * sigma0
        ) - 2.0 * exact_first_mean * first_moment_residual
        additional_tangent = self._additional_tangent(
            mlp, analytic_means, analytic_alphas, firing, analytic_sigmas,
            x, exact_first_mean, first_moment_residual, first_variance_residual,
        )

        active = fnp.arange(mlp.width)
        for layer in range(1, mlp.depth - 3):
            structural_active = fnp.flatnonzero(
                analytic_alphas[layer] >= self.dead_alpha
            )
            cold = fnp.flatnonzero(analytic_alphas[layer] < self.dead_alpha)
            if cold.shape[0] > 0:
                pilot_x = fnp.concatenate(
                    (
                        x[: self.pilot_base],
                        x[self.n_base : self.n_base + self.pilot_base],
                    ),
                    axis=0,
                )
                pilot_pre = pilot_x @ mlp.weights[layer][active, :][:, cold]
                fired = fnp.max(pilot_pre, axis=0) > 0.0
                rescued = cold[fnp.flatnonzero(fired)]
                next_active = fnp.sort(
                    fnp.concatenate((structural_active, rescued), axis=0)
                )
            else:
                next_active = structural_active
            pre = self._sample_matmul(
                x[:, : active.shape[0]],
                mlp.weights[layer][active, :][:, next_active],
                firing[layer - 1][active],
                out=activation[:, : next_active.shape[0]],
            )
            fnp.maximum(pre, 0.0, out=pre)
            x = pre
            active = next_active
            self._trace_stage(f"sample_layer_{layer}")

        pilot_n = min(self.fold_pilot_base, self.n_base)
        pilot_x29 = fnp.concatenate(
            (x[:pilot_n], x[self.n_base : self.n_base + pilot_n]), axis=0
        )

        layer30 = mlp.depth - 3
        dead30, kink30, on30 = _initial_regimes(
            analytic_alphas[layer30], self.dead_alpha, self.on_alpha
        )
        weight30 = mlp.weights[layer30][active, :]
        if dead30.shape[0] > 0:
            dead30, rescued30 = _refine_dead(
                dead30, pilot_x29 @ weight30[:, dead30]
            )
            kink30 = fnp.concatenate((kink30, rescued30), axis=0)
        if on30.shape[0] > 0:
            on30, demoted30 = _refine_on(on30, pilot_x29 @ weight30[:, on30])
            kink30 = fnp.concatenate((kink30, demoted30), axis=0)
        kink30 = fnp.sort(kink30)
        x30_kink = fnp.maximum(x @ weight30[:, kink30], 0.0)
        pilot_x30_kink = fnp.concatenate(
            (x30_kink[:pilot_n], x30_kink[self.n_base : self.n_base + pilot_n]),
            axis=0,
        )

        layer31 = mlp.depth - 2
        dead31, kink31, on31 = _initial_regimes(
            analytic_alphas[layer31], self.dead_alpha, self.on_alpha
        )
        weight31 = mlp.weights[layer31]

        def folded30_to31(columns):
            return weight30[:, on30] @ weight31[on30, :][:, columns]

        def pre31(columns, pilot):
            left = pilot_x29 if pilot else x
            middle = pilot_x30_kink if pilot else x30_kink
            return (
                left @ folded30_to31(columns)
                + middle @ weight31[kink30, :][:, columns]
            )

        if dead31.shape[0] > 0:
            dead31, rescued31 = _refine_dead(dead31, pre31(dead31, True))
            kink31 = fnp.concatenate((kink31, rescued31), axis=0)
        if on31.shape[0] > 0:
            on31, demoted31 = _refine_on(on31, pre31(on31, True))
            kink31 = fnp.concatenate((kink31, demoted31), axis=0)
        kink31 = fnp.sort(kink31)
        x31_kink = fnp.maximum(pre31(kink31, False), 0.0)
        pilot_x31_kink = fnp.concatenate(
            (x31_kink[:pilot_n], x31_kink[self.n_base : self.n_base + pilot_n]),
            axis=0,
        )

        layer32 = mlp.depth - 1
        dead32, kink32, on32 = _initial_regimes(
            analytic_alphas[layer32], self.dead_alpha, self.on_alpha
        )
        weight32 = mlp.weights[layer32]
        folded29_to31_on = folded30_to31(on31)
        kink30_to31_on = weight31[kink30, :][:, on31]

        def pre32(columns, pilot):
            left = pilot_x29 if pilot else x
            middle = pilot_x30_kink if pilot else x30_kink
            right = pilot_x31_kink if pilot else x31_kink
            return (
                left @ (folded29_to31_on @ weight32[on31, :][:, columns])
                + middle @ (kink30_to31_on @ weight32[on31, :][:, columns])
                + right @ weight32[kink31, :][:, columns]
            )

        if dead32.shape[0] > 0:
            dead32, rescued32 = _refine_dead(dead32, pre32(dead32, True))
            kink32 = fnp.concatenate((kink32, rescued32), axis=0)
        if on32.shape[0] > 0:
            on32, demoted32 = _refine_on(on32, pre32(on32, True))
            kink32 = fnp.concatenate((kink32, demoted32), axis=0)
        kink32 = fnp.sort(kink32)

        index_parts = []
        value_parts = []
        if kink32.shape[0] > 0:
            sampled_kink = self._weighted_mean(
                fnp.maximum(pre32(kink32, False), 0.0), final_weights
            )
            index_parts.append(kink32)
            value_parts.append(sampled_kink)
        if on32.shape[0] > 0:
            mean_on = (
                self._weighted_mean(x, final_weights)
                @ (folded29_to31_on @ weight32[on31, :][:, on32])
                + self._weighted_mean(x30_kink, final_weights)
                @ (kink30_to31_on @ weight32[on31, :][:, on32])
                + self._weighted_mean(x31_kink, final_weights)
                @ weight32[kink31, :][:, on32]
            )
            index_parts.append(on32)
            value_parts.append(mean_on)
        if dead32.shape[0] > 0:
            index_parts.append(dead32)
            value_parts.append(analytic_means[layer32][dead32])
        final_mean = _assemble_vector(index_parts, value_parts)

        delta_mean = first_moment_residual
        delta_var = first_variance_residual
        for layer in range(1, mlp.depth):
            weight = mlp.weights[layer]
            delta_pre_mean = delta_mean @ weight
            delta_pre_var = delta_var @ (weight * weight)
            phi = fnp.exp(-0.5 * analytic_alphas[layer] ** 2) / fnp.sqrt(
                2.0 * fnp.pi
            )
            next_delta_mean = (
                firing[layer] * delta_pre_mean
                + (phi / (2.0 * analytic_sigmas[layer])) * delta_pre_var
            )
            layer_mean = analytic_means[layer]
            next_delta_var = (
                2.0 * layer_mean * delta_pre_mean
                + firing[layer] * delta_pre_var
                - 2.0 * layer_mean * next_delta_mean
            )
            delta_mean = next_delta_mean
            delta_var = next_delta_var
        final_mean = final_mean - self.moment_tangent_lambda * delta_mean
        if additional_tangent is not None:
            final_mean = final_mean - additional_tangent

        return fnp.stack((*analytic_means[:-1], final_mean), axis=0)


ARMS = {
    "A_frames": A_frames,
    "A_radial": A_radial,
    "A_prune": A_prune,
    "A_fold": A_fold,
    "A_tangent": A_tangent,
    "A_antithetic": A_antithetic,
}


# ----------------------------------------------------------------- running
def load_truths() -> dict:
    truths = {}
    for s in NET_SEEDS:
        z = np.load(M181_DIR / f"m181_truth_net{s}.npz")
        truths[s] = {
            "means": np.asarray(z["means"], dtype=np.float64),
            "noise_final": float(z["noise_final"]),
        }
    return truths


def run_config(name: str, cls, nets_f: dict, truths: dict) -> dict:
    """Return per-net arrays of (final-layer MSE, billed FLOPs) over reps."""
    est = cls()
    est.setup(SetupContext(
        width=WIDTH, depth=DEPTH, flop_budget=int(BUDGET_B),
        api_version="2.0", seed=0, submission_dir=str(V3_DIR),
    ))
    per_net = {}
    for s in NET_SEEDS:
        weights = nets_f[s]
        truth = truths[s]["means"]
        mses = np.empty(REPLICATES, dtype=np.float64)
        billed = np.empty(REPLICATES, dtype=np.int64)
        t0 = time.perf_counter()
        for r in range(REPLICATES):
            mlp = MLP(width=WIDTH, depth=DEPTH, weights=weights,
                      seed=rot_seed(s, r), name=f"wc1-{name}-{s}-{r}")
            mlp.validate()
            with flops.BudgetContext(METER_BUDGET, quiet=True) as ctx:
                out = est.predict(mlp, METER_BUDGET)
            final = np.asarray(out).astype(np.float64)[-1]
            mses[r] = float(np.mean((final - truth) ** 2))
            billed[r] = int(ctx.flops_used)
        wall = time.perf_counter() - t0
        per_net[s] = {"mse": mses, "billed": billed}
        print(
            f"  [{name}] net {s}: mean_mse={mses.mean():.4e} "
            f"billed={billed.mean():.4e} ({billed.mean()/BUDGET_B*100:.1f}% B) "
            f"{wall:.0f}s",
            flush=True,
        )
    return per_net


def summarize(name, arm_net, base_net, boot_rng) -> dict:
    """Paired MSE ratio + bootstrap CI + worst-net + billed + flags."""
    arm_all = np.concatenate([arm_net[s]["mse"] for s in NET_SEEDS])
    base_all = np.concatenate([base_net[s]["mse"] for s in NET_SEEDS])
    ratio = float(arm_all.mean() / base_all.mean())

    per_net_ratio = {}
    deltas = []
    for s in NET_SEEDS:
        pr = float(arm_net[s]["mse"].mean() / base_net[s]["mse"].mean())
        per_net_ratio[s] = pr
        deltas.append(pr - 1.0)
    deltas = np.asarray(deltas)
    worst_idx = int(np.argmax(deltas))
    worst_net = NET_SEEDS[worst_idx]
    worst_ratio = float(per_net_ratio[worst_net])
    mean_delta = float(deltas.mean())
    worst_delta = float(deltas.max())

    # paired bootstrap: resample reps within each net (same idx for arm+base)
    boots = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for b in range(BOOTSTRAP_DRAWS):
        num = 0.0
        den = 0.0
        for s in NET_SEEDS:
            idx = boot_rng.integers(0, REPLICATES, size=REPLICATES)
            num += arm_net[s]["mse"][idx].sum()
            den += base_net[s]["mse"][idx].sum()
        boots[b] = num / den
    ci = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))

    arm_bill = float(np.concatenate([arm_net[s]["billed"] for s in NET_SEEDS]).mean())
    base_bill = float(np.concatenate([base_net[s]["billed"] for s in NET_SEEDS]).mean())
    billed_delta = arm_bill - base_bill           # arm - baseline
    component_bill = base_bill - arm_bill          # + => component costs this

    load_bearing = ratio >= LOAD_BEARING_RATIO
    removable = (abs(ratio - 1.0) < REMOVABLE_MSE_TOL) and (
        component_bill > REMOVABLE_BILL_FRAC * BUDGET_B
    )
    tail_driver = (worst_delta > 0.0) and (
        worst_delta >= TAIL_DRIVER_FACTOR * mean_delta
    )
    flags = []
    if load_bearing:
        flags.append("LOAD-BEARING")
    if removable:
        flags.append("REMOVABLE")
    if tail_driver:
        flags.append("TAIL-DRIVER")
    if not flags:
        flags.append("NEUTRAL")

    return {
        "mse_ratio_vs_baseline": ratio,
        "mse_ratio_ci95": ci,
        "per_net_ratio": {str(s): per_net_ratio[s] for s in NET_SEEDS},
        "worst_net": int(worst_net),
        "worst_net_ratio": worst_ratio,
        "mean_delta": mean_delta,
        "worst_delta": worst_delta,
        "tail_ratio_worst_over_mean": (
            float(worst_delta / mean_delta) if mean_delta > 0 else None
        ),
        "billed_mean_flops": arm_bill,
        "baseline_billed_mean_flops": base_bill,
        "billed_delta_vs_baseline": billed_delta,
        "component_billed_flops": component_bill,
        "component_billed_frac_of_B": component_bill / BUDGET_B,
        "per_net_mean_mse": {str(s): float(arm_net[s]["mse"].mean()) for s in NET_SEEDS},
        "per_net_billed_mean": {str(s): float(arm_net[s]["billed"].mean()) for s in NET_SEEDS},
        "flags": flags,
    }


def main() -> None:
    t_start = time.perf_counter()
    print("WC-1 winner ablation: loading truths + nets", flush=True)
    truths = load_truths()
    nets_f = {s: [fnp.asarray(w) for w in he_mlp_weights(s)] for s in NET_SEEDS}

    results = {
        "date": "2026-08-08",
        "spec": "WC1_SPEC.md",
        "kind": "audit (each arm reports; nothing promotes)",
        "firewall": (
            "cached m181 truths + kerdock_phases.npz + sobol read-only; frozen "
            "v3 imported read-only (no bytecode); synthetic He nets only; no "
            "dataset/truth-of-record/scorer/submission; single process; writes "
            "only in wc1 dir"
        ),
        "constants": {
            "width": WIDTH, "depth": DEPTH, "n_base": N_BASE,
            "net_seeds": list(NET_SEEDS), "replicates": REPLICATES,
            "budget_B": BUDGET_B, "meter_budget": METER_BUDGET,
            "rotation_seed_formula": "900000 + net_seed*1000 + rep",
            "truth": "m181 3.5M final-layer means (reused read-only)",
            "flags": {
                "LOAD-BEARING": ">= 20% MSE worsening (ratio >= 1.20)",
                "REMOVABLE": "|ratio-1| < 3% AND component bills > 2% of B",
                "TAIL-DRIVER": "worst-net delta >= 1.5x mean-net delta",
            },
        },
        "baseline": {},
        "arms": {},
    }
    out_path = HERE / "wc1_results.json"

    def flush_json():
        out_path.write_text(
            json.dumps(results, indent=2, sort_keys=True, default=float) + "\n",
            encoding="utf-8",
        )

    # ---- baseline (frozen v3) ----
    print("\n== baseline (frozen Kerdock v3) ==", flush=True)
    base_net = run_config("baseline", KerdockV3, nets_f, truths)
    base_all = np.concatenate([base_net[s]["mse"] for s in NET_SEEDS])
    base_bill_all = np.concatenate([base_net[s]["billed"] for s in NET_SEEDS])
    results["baseline"] = {
        "mean_final_mse": float(base_all.mean()),
        "per_net_mean_mse": {str(s): float(base_net[s]["mse"].mean()) for s in NET_SEEDS},
        "billed_mean_flops": float(base_bill_all.mean()),
        "billed_frac_of_B": float(base_bill_all.mean() / BUDGET_B),
        "per_net_billed_mean": {str(s): float(base_net[s]["billed"].mean()) for s in NET_SEEDS},
    }
    flush_json()

    # ---- arms ----
    boot_rng = np.random.default_rng(20260808)
    for name, cls in ARMS.items():
        print(f"\n== arm {name} ==", flush=True)
        arm_net = run_config(name, cls, nets_f, truths)
        results["arms"][name] = summarize(name, arm_net, base_net, boot_rng)
        r = results["arms"][name]
        print(
            f"  -> ratio={r['mse_ratio_vs_baseline']:.4f} "
            f"CI[{r['mse_ratio_ci95'][0]:.4f},{r['mse_ratio_ci95'][1]:.4f}] "
            f"worst_net_ratio={r['worst_net_ratio']:.4f} "
            f"billed_delta={r['billed_delta_vs_baseline']:.3e} "
            f"flags={r['flags']}",
            flush=True,
        )
        flush_json()

    # ---- isolated (iid-substrate) derived ratios ----
    arms = results["arms"]
    derived = {}
    if "A_frames" in arms:
        rf = arms["A_frames"]["mse_ratio_vs_baseline"]
        if "A_radial" in arms:
            derived["A_radial_isolated_over_frames"] = (
                arms["A_radial"]["mse_ratio_vs_baseline"] / rf
            )
        if "A_antithetic" in arms:
            derived["A_antithetic_isolated_over_frames"] = (
                arms["A_antithetic"]["mse_ratio_vs_baseline"] / rf
            )
    results["derived_isolated_ratios"] = derived

    # ---- marginal-value map, sorted by |MSE delta| ----
    mvmap = []
    for name, r in arms.items():
        mvmap.append({
            "component": name,
            "mse_ratio": r["mse_ratio_vs_baseline"],
            "mse_ratio_ci95": r["mse_ratio_ci95"],
            "abs_mse_delta": abs(r["mse_ratio_vs_baseline"] - 1.0),
            "billed_delta_vs_baseline": r["billed_delta_vs_baseline"],
            "component_billed_frac_of_B": r["component_billed_frac_of_B"],
            "worst_net_ratio": r["worst_net_ratio"],
            "flags": r["flags"],
        })
    mvmap.sort(key=lambda d: d["abs_mse_delta"], reverse=True)
    results["marginal_value_map"] = mvmap
    results["wall_seconds"] = round(time.perf_counter() - t_start, 1)
    flush_json()

    print(f"\nDONE in {results['wall_seconds']}s -> {out_path}", flush=True)
    print("\nMARGINAL-VALUE MAP (sorted by |MSE delta|):", flush=True)
    for d in mvmap:
        print(
            f"  {d['component']:<13} ratio={d['mse_ratio']:.4f} "
            f"CI[{d['mse_ratio_ci95'][0]:.4f},{d['mse_ratio_ci95'][1]:.4f}] "
            f"billed_dfrac={d['billed_delta_vs_baseline']/BUDGET_B*100:+.1f}%B "
            f"worst={d['worst_net_ratio']:.3f} {d['flags']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
