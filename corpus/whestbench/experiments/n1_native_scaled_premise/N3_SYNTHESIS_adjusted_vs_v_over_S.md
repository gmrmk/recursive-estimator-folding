# N3 synthesis: the whole campaign is adjusted = v x 8.74e-6 / S

Derived from N2's measured constants on this machine (response-free, generated
network). This is the honest quantitative model of the path to #1, and it
corrects an error in the earlier framing.

## The derivation

For a Monte-Carlo estimator run on the LEGAL wall-priced native channel
(Rules 5.2: billed_FLOPs ~= 0, cost = 1e11 * residual_seconds):
- variance per estimate v => raw MSE = v / N at N samples (unbiased MC; N1/N2
  confirm v is flat, the noise is measurement, not bias);
- wall to draw N samples = N * tau, tau = seconds/sample on the target
  hardware; on THIS laptop tau0 = 23.77e-6 s (N2, 176.5 GFLOP/s numpy f32);
- on grading hardware S-times faster, tau = tau0 / S;
- score S_adj = MSE * max(0.1, C/B), B = 2.72e11, C = 1e11 * N * tau.

Minimize S_adj over N. Below the floor (C/B <= 0.1) multiplier is pinned 0.1
and S_adj = 0.1 v / N falls with N, so push N to the floor boundary
N* = 0.1 B tau0^{-1} S / 1e11 = 0.272 S / tau0. Above it the multiplier is
C/B and S_adj = (v/N)(N tau / (2.72)) is CONSTANT in N. Both meet at:

  **S_adj(min) = v * 1e11 * tau0 / (0.1 * B) ... = v * 8.74e-6 / S**

(tau0 = 23.77e-6, B = 2.72e11: v * 1e11 * 23.77e-6 / (2.72e11) = v * 8.74e-6.)
At the champion variance v = 0.0199 and S = 1 (this laptop): S_adj = 1.74e-7,
a sane match to the champion's ~2.12e-7 realized under the different
instrumented cost model.

**Both levers divide the score linearly. Lower variance-per-sample (v) and
faster native throughput (S) are exactly interchangeable.** This is the real
two-arm compounding, and it needs NO new closure math — just samples on the
legal channel and a smaller v.

## Correction to the earlier framing

The N2 JSON's "speedup_needed_vs_budget" used BUDGET_S = 2.72 s = the VALIDITY
limit (multiplier ~1.0), NOT the 0.1 floor (0.272 s). The floor bar is ~10x
tighter. The correct, multiplier-optimal statement is the formula above; the
3.34x figure was the wrong denominator for a rank claim.

## What each rank costs (champion v = 0.0199, so S_needed = 1.74e-7 / A)

| target adjusted A | who | S (throughput x this laptop) at v=0.0199 | with a 4x-better control (v=0.005) |
|---|---|---|---|
| 2.12e-7 | champion (instrumented) | 0.82 | 0.21 |
| 4.09e-8 | top-12 cutoff | 4.25 | 1.06 |
| 3.18e-8 | mliston | 5.47 | 1.37 |
| 1.98e-8 | huang_chung_yi | 8.79 | 2.20 |
| 9.2e-9 | SKIBIDI (#1 board A) | 18.9 | 4.7 |
| 7.39e-9 | joe_wanza (#1 board B) | 23.5 | 5.9 |

## Honest feasibility (two signals each, stated as levels)

- **S (native throughput over this laptop's 176 GFLOP/s numpy):** REPORTED, not
  measured on grading hardware. This laptop's numpy is already ~a large
  fraction of its own AVX f32 peak, so S is not free code headroom on THIS
  machine; it comes from (a) 16-vCPU grading hardware vs this laptop's cores
  (~2-4x, ASSUMED), (b) a fused small-matmul native kernel avoiding numpy's
  per-256-call overhead (~1.5-3x, REPORTED from the itsjustmarsel 4.44x
  single-matmul teardown). Realistic S ~ 4-8x; optimistic ~12x. **~24x for #1
  at champion v is beyond the plausible native+hardware envelope.**
- **v (variance per sample):** champion radial+q3 control gives 0.0199 vs plain
  0.041 (N2), a REPORTED 2x. RQMC / better antithetic / the M178/M179 exact
  controls plausibly reach v ~ 0.004-0.01 (DERIVED from the corpus RQMC and
  radial rows; not yet measured end-to-end here). A 4x-better v halves the S
  bar (right column).

## The verdict

**#1 (7.39e-9) needs v/S improved ~24x over (champion 0.0199, this-laptop 1x).**
Split realistically: S ~ 6x (native+hardware) times v ~ 4x (RQMC/controls) =
24x -> lands at joe_wanza. That is the plausible EDGE, not a comfortable plan:
it requires BOTH a strong native kernel on good hardware AND a 4x variance
reduction over the already-tuned champion, simultaneously.

**Top-6 (~1.5-2e-8) needs only ~9-12x combined** (e.g. S~6 x v~2), which is
solidly plausible. So the honest reachable target on this lever is a STRONG
top-tier finish (beating ~10 of the 12 visible leaders), with #1 a genuine but
edge-of-envelope stretch gated on simultaneously maxing both levers.

**The one number that settles S is grading-hardware throughput, measurable only
by a graded submission** (de9ea4e). Everything else here is this-laptop-
relative. That submission is the highest-information action in the campaign and
is user-gated.

## Preserved, and the re-aimed plan

The M178/M179 exact-control chain is NOT dead under this model — it is a v-lever
(variance reduction as a control variate), and adjusted = v x 8.74e-6 / S makes
its payoff precise and score-relevant for the first time: every factor it cuts
from v divides the adjusted score. The A2 native port is the S-lever. Both stay;
the honest headline is "strong top-tier, #1 at the edge," and the gating
measurement is a graded submission.
