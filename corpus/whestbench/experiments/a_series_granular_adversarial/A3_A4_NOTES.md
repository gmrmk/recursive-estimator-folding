# A3 + A4 notes — kill-verdict re-audit and hostile-inputs battery

Date: 2026-08-08. Governed by A_SERIES_PREDECLARATION.md sections A3/A4.
Artifacts: `a3_results.json` (run_a3_reaudit.py), `a4_results.json`
(run_a4_hostile.py), `a4_det_run{1,2}.npz` (determinism evidence).
Targeted-rerun budget: 1 of 2 used (light analytic net diagnostic in A3.1);
rerun #2 NOT used.

## A3 — kill-verdict heterogeneity re-audit

| # | Kill under attack | Verdict | Deciding number |
|---|---|---|---|
| A3.1 | M180 Arm C k=4 (net 202 ratio 0.894 vs aggregate 1.196) | **STANDS** | Net-202 per-net paired bootstrap 95% CI [0.669, 1.228] — contains 1.0; P(ratio < 0.90) = 0.53, a coin flip. The sub-unity point is replicate noise. |
| A3.2 | M181 Arm 3 (per-net lambdas −0.035/0.005/0.040) | **STANDS** | ORACLE per-neuron lambda (fit against the 3.5M truth itself): +9.2% in-sample, **−4.1% leave-one-replicate-out**, vs the 10% kill bar. Oracle net-level lambda: 0.006–0.06% reduction (nil). Any implementable fit is strictly worse than the oracle. |
| A3.3 | N8a lattice (per-net ratios 1.43/2.18/2.99) | **STANDS** | Heterogeneity is real (z ≈ 2.3 for 202-vs-303 under a conservative independence assumption) but entirely on the harmless side: the BEST net ratio 1.43 sits 72% above the 0.83 kill bar. No per-net split can flip the kill. |
| A3.4 | N7 (MC control slope −0.783 marginally outside [−1.2, −0.8]) | **STANDS** | Censoring rule excludes zero points (all MSEs ≥ 8.6e-8 > 3.5e-8 worst-case bar) → refit identical. Dropping the noisiest point (n=4096): MC-22 slope −0.783 → **−0.842, inside the band**; mean beta_RQMC −1.099 (full) / −1.097 (drop-4096), both above the −1.25 kill bar. The sanity wobble was the n=4096 point; removing it *restores* validity and the KILL. |

### A3.1 detail — what distinguishes net 202

- 2.8x the baseline sampling variance (5.69e-7 vs 2.03/2.18e-7) and 1.8x the
  truth noise; largest output scale (truth mean-sq 1.32 vs 0.69/0.81; final
  analytic-mean L2 18.8 vs 13.6/14.6).
- In N8a it is the net where Kerdock's edge over plain MC is smallest
  (var_kerdock/var_mc = 0.49 vs 0.35/0.31). Consistent story across M180 and
  N8a: where the structured design's edge over MC shrinks, competing
  randomizations look *relatively* better — but never significantly better
  than the frozen design.
- Adversarial counter-observation: net 303's k=4 CI [1.024, 2.387] excludes
  1.0 — the significant per-net effect that exists runs in the *harmful*
  direction. No conditional-mutation regime found.

### A3.2 detail — the per-neuron ceiling, quantified

Per-rep control-variate directions D were recovered *exactly* from the stored
stacks (D = (arm3 − arm0)/lambda; all 48 replicates usable, none excluded).
Oracle per-neuron lambdas are wildly unstable (sd 460 → 15,391 across nets;
31–42% of neurons need |lambda| > 0.5) because per-neuron D energy is tiny —
there is no stable per-neuron signal that net-level fitting averaged away.
The sign flips in the fitted lambdas are noise around an oracle value of
~0.004–0.012.

### A3 deviations (loud)

1. A3.2 fits the oracle against truth, not a holdout (S80/S20 split data was
   not stored). The oracle *upper-bounds* every implementable fit, so the
   STANDS conclusion is conservative in the right direction. Truth noise
   (1.2–2.2e-8) slightly flatters the oracle; labeled, not corrected.
2. A3.3 has no raw lattice stacks on disk; replicate noise measured from the
   M180 Arm A stacks (same construction/seeds; var matches n8a to ~2e-6
   relative) and the arms treated as independent — this OVERSTATES ratio
   noise (they share the Haar rotation), so z = 2.3 is a lower bound.
3. A3.4 truth noise not stored per net; used the predeclared range's worst
   case (7e-9). Single-variant note: rqmc-22 with the LARGEST-n point dropped
   refits to −1.332 (below −1.25), but that variant discards the most
   informative asymptotic point and the cross-net aggregate stays −1.16 >
   −1.25 under every variant. No verdict changes.

## A4 — hostile-inputs battery on frozen v3

Invocation: run_n8c_g0.py pattern; SetupContext(width=256, depth=32,
flop_budget=int(2.72e11), api_version='2.0', seed=0, submission_dir=V3_DIR);
predict inside BudgetContext(int(2.72e11)) so a breach raises. Baseline
anchor (He net 101, mlp.seed 901101): MSE 5.5e-7 vs 200k truth (noise floor
2.2e-7), billed 1.79e11, wall 3.6 s.

| Input | Completes | Finite | MSE vs 200k truth | Billed / 2.72e11 | Wall s | Verdict |
|---|---|---|---|---|---|---|
| (a) He × 1e-3 | yes | yes | 1.4e-208 (truth ≡ 0) | 2.597e11 (95.5%) | 8.0 | **OK** |
| (b) He × 1e3 | yes | **no (NaN/inf)** | undefined (truth non-finite too) | 1.547e11 | 5.5 | **FAILURE** |
| (c) t3 heavy-tail | yes | yes | 6.1e-8 (beats MC ref 2.1e-7) | 1.764e11 | 5.7 | **OK** |
| (d) rank-32 | yes | yes | 1.1e-7 (MC ref 2.7e-8) | 1.847e11 | 6.6 | **OK** |
| (e) columns rho=0.95 | yes | yes | 1.1e-14 (truth ≡ 0) | 2.597e11 (95.5%) | 8.1 | **DEGRADED*** (adjudicated benign) |
| (f) all-neg shift −3/16 | **no — ValueError** | — | — | 5.2e9 (crash at layer 1) | 1.1 | **FAILURE** |
| (g) He × 1e-38 (denormal) | yes | yes | 0.0 exactly | 2.597e11 (95.5%) | 7.7 | **OK** |
| (h) determinism, 2 subprocesses | yes | yes | — | 1.792e11 both | ~12 each | **OK — bitwise equal, billed equal** |

\* (e) is DEGRADED by the mechanical rule (MSE > 100 × max(MC-ref, noise
floor, 1e-30)) only because the truth is *exactly zero* on this net, which
degenerates every relative bar. Absolute MSE is 1.1e-14 — seven orders
BELOW normal. Skeptic's adjudication: benign spurious positives (~1e-7/neuron
from the analytic dead-neuron fallback and tangent term) on an exactly-dead
net; not a hosted-relevant degradation.

### Findings with hosted analogues → guard-mutation candidates

1. **f_negshift crash (the serious one).** A net whose layer goes fully dead
   (all 256 neurons dead, none pilot-rescued) drives `next_active` to empty;
   the row-blocked Winograd bill is then called with a zero dimension and
   `cost_model.batched_candidate_bill` raises `ValueError: matrix dimensions
   must be positive` (fold3_estimator.py line 143 → row_blocked_winograd.py
   line 88 → cost_model.py line 133). The submission would crash on that MLP.
   Hosted analogue: plausible-but-rare — needs a full-layer death, never seen
   in the 50-MLP hosted ledger, but the consequence is total (worst-case or
   voided score). **Guard mutation candidate M186: empty-regime guard** — if
   any active/kink set is empty, skip the zero-width matmul and emit the
   analytic means for all downstream layers. Cheapest falsifier: rerun
   f_negshift (must complete finite) + bitwise-identical predictions on He
   nets 101/202/303 (guard must be a no-op on healthy nets).
2. **b_gain_1e3 silent NaN.** Activation/analytic-moment overflow at f32
   range propagates NaN to a *returned* prediction (no exception). Hosted
   analogue: weaker (hosted nets are He-scaled), but a single large-scale
   layer suffices and the failure is silent. **Guard mutation candidate
   M187: finite-output guard** — isfinite check on the analytic pass and the
   assembled final vector; clamp/fallback on failure. Cheapest falsifier:
   b_gain_1e3 completes finite + bitwise-identical on healthy nets.
3. **Budget headroom note (no breach observed).** Pruning-hostile nets
   (a, e, g — no on/dead regimes fire) push billing to its no-pruning maximum
   2.597e11 = 95.5% of the 2.72e11 budget. Headroom at the billing worst case
   observed is 4.5%. Not a failure; worth knowing before any mutation that
   adds billed work.

### Robustness certificate (the NULL side)

Heavy tails (t3), rank collapse (32/256), extreme underflow (×1e-3), and
f32-denormal weights (×1e-38) are all handled with finite, sane output —
the denormal and underflow nets return errors at or near machine floor —
and two cold subprocesses reproduce the same normal-net prediction
bit-for-bit with identical billed FLOPs. The champion's failure surface is
confined to (i) fully-dead layers (crash) and (ii) f32 overflow scales
(silent NaN), both named above with guard mutations and falsifiers.

### A4 deviations (loud)

1. `api_version='2.0'` per the task spec (run_n8c_g0.py used 'synthetic');
   the frozen estimator does not branch on api_version.
2. Truth is 200k MC (task-specified), noise floor ~2.2e-7 on healthy nets —
   17.5x n8c's 3.5M truth — so absolute MSEs on healthy nets sit near the
   truth floor; the DEGRADED rule therefore uses a per-net matched-n MC
   reference + noise floor (operationalizing "MSE >> normal"), not raw MSE.
3. Memory usage was not recorded (predeclaration mentions it; the A4 task
   list did not include it and no memory-sensitive behavior was observed —
   all runs are the same fixed-shape pipeline).
4. Findings are EVIDENCE only; the guard candidates require their own
   predeclarations before any estimator change (discipline section of the
   predeclaration).
5. Numbering: M185 was observed to be claimed MID-RUN by the concurrent A2
   tail-hunt worker (run_m185_g0.py appeared in this directory during the A4
   battery), so the guard candidates here are provisionally numbered
   M186/M187 — final numbering is the coordinator's call.
