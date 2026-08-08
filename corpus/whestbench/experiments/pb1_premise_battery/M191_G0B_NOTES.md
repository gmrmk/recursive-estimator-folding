# M191 G0-b notes — harmonic control-variate battery arm

Date: 2026-08-08. Governing predeclaration: `M191_HARMONIC_PREDECLARATION.md`
(section G0-b). Runner: `run_m191_g0b.py`. Results: `m191_g0b_results.json`.

## VERDICT: KILL (final)

cv_both (split-sample, the predeclared gate arm): panel-MSE ratio **0.99168**
= reduction **+0.83%**, bootstrap 95% CI **[-0.63%, +2.36%]** (ratio CI
[0.97639, 1.00633]). The kill bar was 10%; the arm delivered under 1% and the
CI includes zero. The predeclaration's honesty bound named this branch
verbatim — "if the final-layer functions' energy above the exact degree is
spread across many harmonics (high effective dimension), the sampled
projection is itself noisy and the CV gains little" — and the R^2 diagnostic
below confirms it is the measured failure mode, not an implementation bound.

## Deviations (loudly, first)

1. **Plain numpy, no flopscope metering** — the sanctioned G0 deviation
   (N8a/M180/M181 precedent, restated in the tasking).
2. **16 rotation seeds** (>= the predeclared 12), seed formula
   `900000 + net*1000 + rep` — chosen to match the cached m181 stacks
   exactly, which buys the bitwise baseline cross-check below.
3. **W_1 convention made operational**: the code stores the first layer as
   `weights[0]` with shape (in, out), the TRANSPOSE of the math-convention
   W_1. "Top k=8 right singular vectors of W_1" is implemented as the top
   input-space singular directions = the first 8 columns of U in
   `weights[0] = U S V^T` (identically the right singular vectors of the
   math-convention W_1 = weights[0]^T). Top singular values ~2.58-2.79
   (well-separated from the bulk edge, so the choice is stable).
4. **Split construction**: "a random half of the samples" implemented as a
   uniform random permutation of all 64,512 sample rows, halves
   32,256/32,256, seed `777000 + net*1000 + rep`. Antipodal partners may
   land in different halves (p4/p6 are even, so their p-rows are duplicated
   across partners regardless).
5. **Unit directions row-normalized to exact unit norm** (the f32 design
   rows carry ~1e-6 relative radius jitter; normalization removes any
   constant-offset leakage into the zero-mean constants c4/c6).
6. **Honesty caveat on "stays unbiased"** (predeclaration wording): the
   split-sample independence argument is exact under iid sampling; here both
   halves share the per-rep Haar rotation, so a priori independence fails.
   Measured: bias^2 (N8c decomposition) is ~0 within decomposition noise on
   every net for baseline, split CV, AND no-split CV (net 101: -1.6e-8 both;
   net 202: -6.9e-9 split vs -2.8e-9 no-split; net 303: +3.1e-9 split vs
   +3.0e-9 no-split, baseline +4.1e-9). At 16 seeds the bias the no-split
   shortcut introduces is BELOW the seed-noise floor — neither variant shows
   detectable bias; the split machinery cost nothing and protected nothing
   measurable at this replication.

## Config

3 synthetic He f32 256x32 nets (seeds 101/202/303, t3-style, n8a machinery
imported read-only); 64,512 Kerdock antipodal directions per rotation seed
(exact chi-mean radius 15.984383, shared Haar rotation); truth = cached m181
3.5M iid MC final-layer means (read-only), measured noise floors
1.229e-8 / 2.219e-8 / 1.504e-8 subtracted from every MSE; bootstrap 4000
paired draws over rotation-seed indices shared across variants per draw;
geomean panel aggregation (M180/M181 conventions); `floored_draws = 0`.

Basis: 12 directions (8 weight-derived + 4 fixed He-random controls, seed
191042, shared across nets) x 2 degrees = 24 functions;
p4_a(u) = (a.u)^4 - 3/(n(n+2)), p6_a(u) = (a.u)^6 - 15/(n(n+2)(n+4)),
n = 256, each normalized to unit sample-std (exactly scale-invariant for the
estimator: beta = cov/var absorbs column scaling). Betas are the predeclared
UNIVARIATE per-k form, summed over k — not a joint fit.

## Panel results (noise-subtracted MSE ratio vs plain-mean baseline)

| variant | panel ratio (geomean) | reduction | bootstrap 95% CI (ratio) | gate |
|---|---|---|---|---|
| cv_both (split, GATE ARM) | **0.99168** | +0.83% | [0.97639, 1.00633] | **KILL** |
| cv_deg4 only (split) | 0.99582 | +0.42% | [0.98977, 1.00213] | (diagnostic) |
| cv_deg6 only (split) | 0.99417 | +0.58% | [0.98275, 1.00452] | (diagnostic) |
| cv_both no-split | 0.99596 | +0.40% | [0.98411, 1.00669] | (diagnostic) |

Per-net cv_both ratios: 101 -> 0.98690, 202 -> 1.01235, 303 -> 0.97614.
Baseline noise-subtracted MSEs: 1.874e-7 / 5.650e-7 / 2.219e-7 (raw
1.997e-7 / 5.872e-7 / 2.369e-7 — bitwise equal to m181 Arm 0).

## Mechanism diagnostics (the calibration the predeclaration required)

- **R^2 of f_j on the basis (joint, per-neuron, mean over neurons/seeds)**:
  net 101: both 0.00226 (deg4 0.00180, deg6 0.00105);
  net 202: both 0.00290 (deg4 0.00232, deg6 0.00133);
  net 303: both 0.00293 (deg4 0.00231, deg6 0.00132).
  The 24-function basis explains **~0.23-0.29%** of per-neuron variance.
  The final-layer functions' degree-4/6 energy is spread across the
  ~1.8e8-dimensional degree-4 (and larger degree-6) harmonic spaces at
  d = 256; a 12-direction ridge basis captures a fraction consistent with
  ~basis-dimension/space-dimension. This is the predeclared honesty-bound
  branch, measured.
- **deg-4 vs deg-6 split**: deg6-only recovers slightly MORE than deg4-only
  (+0.58% vs +0.42%) despite lower R^2 — consistent with G0-a's error
  spectrum: the design retains only ~11% of iid error at degree 4 but ~40%
  at degree 6, so per unit of aligned energy there is ~13x more removable
  error variance at degree 6 ((0.40/0.11)^2). The mechanism ceiling for ANY
  ridge-type CV family on this design is therefore set by the degree-6+
  aligned share, and a 12-direction basis holds ~0.1% of it.
- **Quadrature consistency vs G0-a** (this basis, raw column means / iid
  RMS): deg4 0.106/0.104/0.116, deg6 0.403/0.396/0.422 across nets — the
  weight-derived directions see the same design error spectrum G0-a measured
  with random harmonics (0.098-0.107 and 0.348-0.433). The CV had exactly
  the room G0-a promised; the aligned share of f was the missing factor.

## Verification signals (two-signal protocol)

1. **Cached reference reproduced bitwise**: the baseline 16-rep stacks equal
   the m181 `arm0_baseline` stacks with max |diff| = 0.0 on all three nets
   (`m181_arm0_crosscheck` in the results JSON) — same seeds, same op order,
   same BLAS threading.
2. **Independent re-derivation of the headline number**: the cv_both panel
   geomean recomputed from the checkpointed partial npz files through a
   separate code path (flat dot-product sums, explicit counts, no shared
   functions) gives 0.991682 vs the harness's 0.9916816 — agreement to 6
   decimals, per-net ratios matching to 6 decimals.
3. **G0-a consistency** (above): the design's error spectrum on this basis
   matches the deterministic G0-a measurement per degree, per net.

## Disposition

M191 G0-b is KILLED: the weight-derived degree-4/6 harmonic control variate
recovers +0.83% [CI -0.63%, +2.36%] of panel MSE against a 10% kill bar. The
kill is a mechanism kill, not an implementation kill: the basis sees the
design's non-exact degrees at exactly the G0-a-measured error levels, the
betas fit cleanly, no bias is introduced — but the estimator functions hold
only ~0.25% of their variance in any 12-direction ridge subspace at d = 256,
so there is almost no aligned error to remove. Scaling the basis is not a
rescue path inside M191's gates: closing even the deg-6 share would need a
basis dimension comparable to the harmonic space itself. No retuning was
performed after the gate read.

## Files

- `run_m191_g0b.py` — gate runner (probe / per-net / aggregate)
- `m191_g0b_results.json` — machine-readable per-net tables, CIs, verdict
- `m191_g0b_partial_net{101,202,303}.npz` — per-seed estimate stacks,
  R^2 arrays, raw basis quadrature means, top singular values
- `M191_G0B_NOTES.md` — this file
