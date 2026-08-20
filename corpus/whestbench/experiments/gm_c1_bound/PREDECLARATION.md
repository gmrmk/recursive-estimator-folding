# PREDECLARATION — gm_c1_bound

Graveyard revival worker, ledger id `c1_local_vs_hosted_calibration`
(mining search key `c1_local_vs_hosted_calibration`).
Written 2026-08-10 BEFORE any computation on the archived rows.
Author: Opus-5 falsifier worker. Work dir:
`corpus/whestbench/experiments/gm_c1_bound/`.

## 0. What the original record says (verbatim inputs, no computation)

From `corpus/whestbench/headroom/fold_ledger.json`, candidate id
`c1_local_vs_hosted_calibration`, status `screened`:

> R = 1.652 (local MC adjusted 1.0686e-6 on 22 completed nets at 97.4% budget,
> v=0.0630, vs hosted reference 6.470e-7) -> OUR LOCAL SUITE IS 1.65x HARDER.
> ... Kerdock v3 1.619e-7 -> ~9.8e-8 (rank ~13-14, at parity with the best
> honest hosted entry oabuod 9.45e-8; MSE x C invariant 2.70e4 vs their
> 2.58e4 = 1.05x, not the 1.7x the uncalibrated local numbers implied)
> ... Deviation recorded: 3/25 nets tripped combined_budget_exhausted at 57344
> samples (97.4% of B); excluded, raw 25-net figure 0.0978 is a
> zero-prediction artifact.

`matched_units: 22`, `failures: 3`, no error bar published anywhere in
`C1_REPORT.md` or the ledger row.

## 1. Mechanism under test (the revival claim)

R = 1.652 was published as a point constant that the whole campaign divides by.
The revival claim is that R is a *statistic of 22 noisy per-net draws*, not a
constant, and additionally that the 3 excluded nets were dropped for being
HARD (highest effective compute), so the published R is a downward-biased
LOWER bound. If both hold, the three downstream claims quoted as point facts
("rank ~13-14", "at parity with oabuod 9.45e-8", "1.05x gap not 1.7x") are not
determined by the data.

## 2. Quantities (equations, fixed now)

Let `A = {a_i}` be the `adjusted_final_layer_score` values of the rows in
`experiments/c1_local_mc_calibration/c1_local_mc25.json -> results.per_mlp`
with `combined_budget_exhausted == false` (predeclared definition of
"completed"; expected |A| = 22). Let `H = 6.470e-7` (hosted MC reference,
verbatim from the record — treated as an exact constant, its own error is
NOT modelled here and that is stated as a limitation).

- Point estimate: `R = mean(A) / H`.
- Dispersion: `sd = stdev(A, ddof=1)`; `CV_mean = sd / (mean(A) * sqrt(n))`;
  relative variance `v_rel = var(A, ddof=1) / mean(A)^2`; spread `max(A)/min(A)`.
- Bootstrap: B = 200,000 resamples of size n with replacement; percentile
  95% CI on `R` = [2.5th, 97.5th] percentile of `mean(A*)/H`.
- Exclusion-bias bounds: let `E` be the 3 excluded rows. Impute each excluded
  net's adjusted score at (a) `median(A)` and (b) `max(A)`, then
  `R_med_imp = mean(A ∪ 3×median(A)) / H`, `R_max_imp = mean(A ∪ 3×max(A)) / H`.
- Downstream propagation: `K(R) = 1.619e-7 / R` (Kerdock v3 hosted
  expectation); parity ratio `P(R) = K(R) / 9.45e-8`.

## 3. Predicted outcome (ON RECORD, before running)

Taken from the mined revival record, which reports having executed this:

- `R = 1.652` reproduces from the archived rows (mean(A) = 1.0686e-6).
- 95% bootstrap CI on R = **[1.04, 2.42]**, 1-sigma **0.36**.
- `v_rel ≈ 1.07`, `max/min ≈ 22.4x` across the 22 completed nets.
- The 3 excluded nets are the 3 highest effective-compute nets
  (2.72–2.74e11 vs completed mean 2.650e11).
- `R_max_imp = 2.36`.
- Therefore the parity claim `P(R) ∈ [0.8, 1.25]` FAILS across the CI:
  at R = 1.04, K = 1.557e-7 and P = 1.65 (Kerdock ~65% behind oabuod);
  at R = 2.42, K = 6.69e-8 and P = 0.71 (Kerdock clearly ahead).

I predict the revival stands: **REVIVED_PASS**.

## 4. Gates (exact numbers, decided now)

Parity band: I adopt C1's OWN comparability band from its own predeclaration,
`[0.8, 1.25]`, applied to `P(R)`. `P(R) ∈ [0.8, 1.25]` solves to
**R ∈ [1.3710, 2.1421]** (R_lo = 1.619e-7/(1.25*9.45e-8),
R_hi = 1.619e-7/(0.8*9.45e-8)). This is the "claims unchanged" interval.

**G0 — reproduction gate (run first, arithmetic only).**
- G0.1 `mean(all 25 adjusted) == results.adjusted_final_layer_score`
  (published 0.09778592927244555) to relative 1e-9.
- G0.2 `|mean(A)/1.0686e-6 - 1| <= 0.005` and `|R - 1.652| <= 0.005`.
- If G0 fails: STOP, verdict INCONCLUSIVE (the falsifier's data premise —
  that the archived rows are the source of the published constant — is broken).
  Do not retune, do not substitute another data source.

**G0b — step-0 arithmetic KILL gate (run before any bootstrap).**
Compute `CV_mean`. If the normal-theory interval
`1.652 * (1 ± 1.96 * CV_mean)` is fully contained in `[1.3710, 2.1421]`
— equivalently `CV_mean <= 0.0868` — then the 22-net sampling error is too
small to move any downstream claim: **STOP, KILL_CONFIRMED**, C1 stands
exactly as written. No bootstrap, no imputation, no retune.

**G1 — main gate (bootstrap, only if G0b does not kill).**
Let `[R_lo, R_hi]` be the 95% percentile bootstrap CI.
- **KILL_CONFIRMED** iff `[R_lo, R_hi] ⊆ [1.3710, 2.1421]`.
- **REVIVED_PASS** iff `[R_lo, R_hi]` leaves `[1.3710, 2.1421]` on at least one
  side (the parity claim changes truth value somewhere inside the CI)
  AND `R_max_imp > R` (exclusion bias is upward, so 1.652 is a lower bound
  through the exclusion channel as claimed).
- If the CI leaves the band but `R_max_imp <= R`, the verdict is
  **INCONCLUSIVE** (half the mechanism failed) — reported as such, not patched.

**G2 — mined-number reproduction (reporting gate, not a verdict gate).**
My `[R_lo, R_hi]` must match the mined `[1.04, 2.42]` within ±0.05 per endpoint
and `R_max_imp` must match the mined 2.36 within ±0.05. A miss is recorded
LOUDLY as a deviation; the verdict is decided on MY numbers either way.

## 5. Two-signal verification (required before any PASS or KILL claim)

1. **Independent recomputation of the data read**: the 25-net mean of
   `adjusted_final_layer_score` must equal the committed top-level
   `results.adjusted_final_layer_score` bit-for-bit-ish (rel 1e-9). This proves
   I am reading the field the report aggregated.
2. **Two independent RNG streams**: percentile bootstrap run twice with
   different bit generators and seeds (numpy PCG64 seed 20260810, Philox seed
   77) at B = 200,000. Endpoints must agree within 0.01 absolute in R.
3. **Analytic cross-derivation**: normal-theory CI `R*(1 ± 1.96*CV_mean)` and a
   Student-t(21) CI computed in closed form from `sd` — an estimator that does
   not resample at all — reported alongside. The bootstrap must be consistent
   with these to within the skew expected of a right-skewed n=22 mean
   (agreement judged by reporting both, not by an automatic tolerance, since
   they are not required to coincide for skewed data).

## 6. Declared limitations / scope (no scope enlargement)

- The hosted reference 6.470e-7 is a single printed number with no error bar;
  its sampling error is NOT modelled. All CIs here are LOCAL-side only, so the
  true CI on R is WIDER than anything I report. Stated, not fixed.
- "rank ~13-14" cannot be tested: it requires a hosted leaderboard read, which
  the firewall forbids (no network, no submissions). Only the parity claim and
  the MSE×C gap claim, both computable from committed constants, are gated.
  This is recorded as a limitation, and the parity band is the operative gate.
- Zero new estimator compute. Committed JSON arithmetic + numpy RNG only.
- No edit to any file outside `experiments/gm_c1_bound/`. No git. No network.

## 7. Kill honesty clause

If G0b or G1 kills, I report KILL_CONFIRMED as a full success and do not
enlarge B, change the band, switch to a BCa/other interval, or re-impute.
