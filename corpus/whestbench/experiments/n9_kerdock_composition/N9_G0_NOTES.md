# N9 G0 notes — interaction gates, both components KILLED

Date: 2026-08-08. Predeclaration: `N9_PREDECLARATION.md` (governs).
Runner: `run_n9_g0.py`. Results: `n9_g0_results.json`.

## DEVIATIONS AND FINDINGS (read first)

1. **The predeclaration's fold premise is factually wrong, and that decides
   G0-b.** The predeclaration says "v3 already folds at L1, so the increment
   is L1 -> L3." The frozen v3 source contradicts this:
   `candidate_source_validator_v3/estimator.py` inherits
   `fold3_estimator.Estimator` — the three-terminal-layer dead/on/kink fold
   (`for layer in range(1, mlp.depth - 3)` then explicit layer-30/31/32
   folding). v3's current pipeline ALREADY IS the L3-folded structure; the
   N8c artifacts had already recorded it as "the frozen v3 fold3 pipeline"
   (`run_n8c_g0.py` docstring, `n8c_g0_results.json` arm notes). The "L1"
   in the lineage name `kerdock_l1_owned_buffer` refers to the layer-1
   phased-WHT memory fold, not terminal fold depth. G0-b was executed
   exactly as predeclared (no retuning): both bills are evaluated and
   compared; because the two structures are identical, the billed reduction
   is 0 for EVERY partition input.
2. Analytic diagonal pass and tangent recursion computed in float64 numpy
   instead of the estimator's float32 flopscope arrays. Cross-check in the
   results JSON: max relative f32/f64 difference of the final tangent is
   3.9e-7 / 6.8e-7 / 2.1e-6 per net — immaterial at the ±10% gate scale.
3. G0-a arm (i) is the sampling-stage-isolating plain antipodal downstream
   (N8a arm (a) / N8c plain arm), not the full fold3 pipeline — the same
   sanctioned deviation as N8a/N8c. Anchor: its per-net variances reproduce
   `n8c_g0_results.json` `plain_downstream.variance_ddof1` to 5 significant
   figures (2.0349e-7 / 5.6901e-7 / 2.1781e-7), an independent predecessor
   run.
4. G0-b partitions are the realized dead/on/kink counts from the analytic
   pass (predeclared wording). Pilot refinements are billed but move zero
   units (their outcomes are sample-dependent). This choice cannot affect
   the verdict — see finding 1.
5. G0-b counting uses the t3 per-op bills (`capped_fold3.predict_main_bill`
   constants) in the direct-matmul convention; v3's WHT first product and
   row-blocked Winograd backend are not modeled. Both compared structures
   share them identically, so the reduction ratio is invariant. The metered
   n8c anchor (1.8166e11 / 1.6984e11 / 1.6478e11) sits ~8–10% above this
   static count (1.6734e11 / 1.5520e11 / 1.5030e11) because the deployed
   run's pilot rescues enlarge active sets beyond the analytic structural
   sets and the backends bill their own overheads; same order, per-net
   ordering preserved.

## G0-a (tangent-on-frames): KILL

Paired variance across 16 Haar seeds (>= 12 predeclared), 3 He nets,
Kerdock native count 32,256 (antipodally doubled), frozen lambda
0.9807112198896164 (identical in the tangent tar's `estimator.py` and v3's
`base_estimator.py`), response map transcribed from those sources with
`_radial_covariance = mean_chi(256)^2/256`.

| net | var arm (i) | var arm (ii) | reduction |
|-----|-------------|--------------|-----------|
| 101 | 2.0349e-07  | 1.9654e-07   | +3.41%    |
| 202 | 5.6901e-07  | 5.5864e-07   | +1.82%    |
| 303 | 2.1781e-07  | 2.1521e-07   | +1.19%    |

Mean paired variance reduction **+2.14%** (paired bootstrap 95% CI
[-3.0%, +6.2%]) < 10% -> **tangent component KILLED**.

Second signals that the kill is real and not an implementation artifact:

- **Positive control** (diagnostic, not a gate): the identical response-map
  code on antipodal iid Gaussian sampling at the tangent lineage's native
  n = 14,000 with `_radial_covariance = 1.0` gives reductions +26.0% /
  +41.3% / +36.1% (mean +34.5%) on the same nets — the transcription
  demonstrably works where the lineage says it works.
- **Ceiling robustness** (derived from the reported var/cov rows): the best
  achievable reduction with ANY linear coefficient on frames is
  cov^2/(var_i * var_corr) = 3.7% / 1.9% / 2.0% per net (mean ~2.5%), so
  no lambda — refitting is forbidden anyway — clears 10%. The kill is
  robust to the frozen-lambda choice.
- Internal identity var(ii) = var(i) - 2*cov + var_corr checks per net.

Interpretation: as the predeclaration's redundancy-risk note anticipated
(cf. N5/N8a), the Kerdock frames already suppress the first-layer moment
residual the tangent control subtracts; what remains on frames is mostly
noise the control cannot predict.

## G0-b (fold increment): KILL

Static billed-FLOP count, v3's current pipeline vs the L3-folded variant
structure, realized analytic partitions (per-net a28 = 177/166/168; e.g.
net 101 terminal d/k/o: L30 92/88/76, L31 97/85/74, L32 108/74/74):

| net | bill v3 current | bill L3 variant | reduction |
|-----|-----------------|-----------------|-----------|
| 101 | 1.6734e+11      | 1.6734e+11      | 0.00%     |
| 202 | 1.5520e+11      | 1.5520e+11      | 0.00%     |
| 303 | 1.5030e+11      | 1.5030e+11      | 0.00%     |

Mean billed reduction **0.00%** < 15% -> **fold component KILLED** (the
increment is empty; see finding 1).

Context diagnostics (labeled, non-gating):

- The L3 fold v3 already contains is worth only ~0.8–1.2% of billed FLOPs
  vs an unfolded variant under these analytic partitions: at n = 32,256 the
  three terminal layers are a small fraction of the 28 middle-layer sample
  matmuls, and the fold still bills its kink columns plus pilot/refinement
  overheads.
- Derived ceiling: even if terminal-3-layer folding were FREE, the saving
  vs unfolded is ~3/31 of the sampled-layer work, ~10% < 15% — at this
  width/depth/sample count no terminal-3-layer counting change could have
  cleared the predeclared bar.

## Verdict

**N9 KILLED at G0 — both components dead.** Per the predeclaration: "If
BOTH die: N9 KILLED — and the honest local program is exhausted with the
composition explicitly measured, not assumed." No build occurred (G0
only); G1–G3 are moot.

## Firewall compliance

Synthetic He nets only (seeds 101/202/303, t3-style construction). Frozen
v3 sources read-only; the only asset loaded was the shipped
`kerdock_phases.npz`. From the tangent tar
(`outputs/WHestBench-Phase-II-tangent-candidate.tar.gz`; members:
`estimator.py`, `sobol_owen_u32.npz`, `manifest.json`) only `estimator.py`
was extracted, to a session scratch directory — the `.npz` asset was never
touched. No benchmark truth/scorer/gt/premise files, no public rows, no
submission, no git. All new files live in this experiment directory;
single process, foreground, ~4 minutes of compute (well inside the ~60
minute timebox; replicates kept at 16, above the predeclared minimum 12).
