# VERDICT — gm_c1_bound / `c1_local_vs_hosted_calibration`

**GATE RESULT: REVIVED_PASS.** The predeclared main gate G1 did not kill.
R = 1.652 is not a constant: its local-only 95% bootstrap CI is
**[1.036, 2.423]** (width 1.387), **1.80x wider** than the interval
`[1.371, 2.142]` (width 0.771) inside which C1's downstream parity claim keeps
its truth value. The parity claim ("Kerdock v3 effectively at parity with
oabuod 9.45e-8") flips status at both ends of the CI, and only 68.3% of the
bootstrap distribution leaves it standing (22.4% below the band, 9.3% above).

## DEVIATIONS (loud, read these first)

1. **"rank ~13-14" was NOT tested.** It needs a hosted leaderboard read; the
   firewall forbids network. Predeclared as a limitation in §6 of
   PREDECLARATION.md; the operative gate is the parity band only, computed
   from committed constants. The rank claim's status is therefore *untested*,
   not *unchanged*.
2. **The CI is a LOWER BOUND on width.** The hosted reference 6.470e-7 is a
   single printed number with no error bar; its sampling error is not
   modelled. Every interval here is local-side only, so the true CI on R is
   wider than what is reported.
3. **The mined "exclusion bias is upward" sub-claim is NOT supported by the
   data.** My predeclared test for it (`R_max_imp > R`) passed — but that test
   is true by construction for any non-degenerate sample, i.e. I predeclared an
   uninformative sub-gate. The substantive check (post-hoc, `exclusion_direction.py`)
   says: within the 22 completed nets, Spearman(effective_compute, adjusted)
   = **+0.0695**, permutation p(two-sided) = **0.761** / **0.757** on two
   independent RNG streams; Pearson = -0.0830; Spearman(flops_used, adjusted)
   = -0.2919. And **median-imputation gives R = 1.5735, BELOW the point
   R = 1.6517.** So the exclusion channel bounds R in roughly [1.574, 2.356]
   without a data-supported direction. The mined phrase "the truth sits above
   1.652 more often than below" is an assumption, not a measurement.
4. `attack.py` and `exclusion_direction.py` were **not predeclared**. They were
   run after G1 to attack my own PASS, and both are reported in full regardless
   of outcome. No gate, band, interval type, or B was changed after any result.

## Step 0 (G0 + G0b) — ran first, did not kill

| check | value |
|---|---|
| mean of all 25 archived `adjusted_final_layer_score` | 0.09778592927244556 |
| committed `results.adjusted_final_layer_score` | 0.09778592927244555 |
| relative error (G0.1) | **1.42e-16** — PASS |
| mean of the 22 completed | 1.0686276000992886e-06 (published 1.0686e-6) |
| R recomputed | **1.6516655333837535** (published 1.652), abs err 3.34e-4 — PASS |
| CV of the mean | **0.2207** vs G0b kill threshold **0.0869** |
| G0b normal interval | [0.9375, 2.3665] — not inside [1.3706, 2.1415] |
| **G0b** | **NO KILL** — proceed |

Dispersion of the 22 (nobody had computed these): sd = 1.1061e-6,
relative variance **1.0714** (mined: 1.07), max/min spread **22.415x**
(mined: 22.4x), min 2.1704e-7 / median 6.4735e-7 / max 4.8650e-6.

## G1 — main gate

Percentile bootstrap, B = 200,000, resampling the 22 completed adjusted scores.

| quantity | value |
|---|---|
| R point | **1.6517** |
| **95% CI (percentile bootstrap)** | **[1.0362, 2.4230]** |
| 1-sigma (bootstrap) | 0.3556 |
| SE analytic (sd/sqrt(n)/H) | 0.36448 |
| jackknife SE (no RNG at all) | 0.36448320938468 |
| CI 95% normal-analytic | [0.9373, 2.3661] |
| CI 95% Student-t(21) | [0.8937, 2.4096] |
| claims-unchanged band for R | [1.3706, 2.1415] |
| CI inside band? | **NO** |
| bootstrap P(R inside band) | **0.6826** |

Propagated to the downstream numbers C1 published as point facts:

| candidate | local adjusted | hosted at R=1.652 | hosted band across the CI |
|---|---|---|---|
| Kerdock v3 | 1.619e-7 | 9.802e-8 | **[6.682e-8, 1.562e-7]** |
| two-axis L2 | 2.102e-7 | 1.273e-7 | [8.675e-8, 2.029e-7] |
| L1 champion | 2.122e-7 | 1.285e-7 | [8.758e-8, 2.048e-7] |

Parity ratio P(R) = (1.619e-7/R)/9.45e-8: **1.037 at the point estimate,
1.653 at CI-lo (Kerdock's hosted expectation 1.65x WORSE than oabuod), 0.707
at CI-hi (0.707x, i.e. 1.41x BETTER).** C1's own comparability band is
[0.8, 1.25]; the CI runs through it and out of both sides.

## Two-signal verification

1. **Data read, independent recomputation.** The 25-row mean of the archived
   `adjusted_final_layer_score` field reproduces the committed top-level
   aggregate to 1.42e-16 relative. I am reading the exact field the report
   aggregated.
2. **Two independent RNG streams.** PCG64/seed 20260810 gives
   [1.03702, 2.41911]; Philox/seed 77 gives [1.03545, 2.42694]. Endpoint
   agreement 0.0016 and 0.0078, both inside the predeclared 0.01.
3. **Non-resampling cross-derivation.** The jackknife SE (deterministic, no
   RNG) is 0.364483209384680 against the closed-form sd/(sqrt(n)·H) =
   0.364483209384680 — an exact match, and the normal and t intervals reach
   the same verdict as the bootstrap by a route that never resamples.
4. **G2, mined-number reproduction.** Mined CI [1.04, 2.42] vs mine
   [1.036, 2.423]: |Δ| = 0.0038 / 0.0030. Mined max-imputed 2.36 vs mine
   2.3558: |Δ| = 0.0042. All inside the predeclared ±0.05. The mined record's
   arithmetic is confirmed independently.

## Attack on my own PASS (post-hoc)

Counter-hypothesis: the wide CI is an artifact of one outlier net
(max adjusted 4.865e-6). **The attack does not land** — and it makes C1 worse,
not better:

| sample | R | 95% CI | inside band? |
|---|---|---|---|
| full 22 | 1.6517 | [1.0366, 2.4232] | no |
| drop top 1 (n=21) | **1.3722** | [0.9347, 1.8698] | no |
| drop top 2 (n=20) | **1.2276** | [0.8564, 1.6507] | no |
| trim min and max (n=20) | 1.4241 | [0.9716, 1.9391] | no |

Removing one net moves the *point estimate itself* from 1.652 to 1.372 — onto
the exact edge of the claims band — and removing two moves it to 1.228, which
is inside C1's own predeclared "suites comparable, case (A)" region [0.8, 1.25]
that the report ruled out. The single published constant is one net away from
a different qualitative verdict.

## What stands and what does not

- **Stands:** the *direction*. R > 1.25 (C1's "local suite harder" verdict)
  holds at the point estimate and at every imputation, and the bootstrap gives
  **P(R > 1.25) = 0.8763 / 0.8751** on the two RNG streams
  (P(R > 0.8) = 0.9991 / 0.9990), so the coarse verdict "local is harder" is
  not seriously in doubt — though it is not the >0.95 the report's flat
  language implies. The C1 run itself is arithmetically clean: every published
  figure reproduces from the archive.
- **Does not stand:** R as a *point constant with no error bar*, and the three
  downstream statements quoted as facts. "At parity with oabuod", "rank 13-14",
  and "a 1.05x gap, not 1.7x" are all inside the noise of a 22-net mean with
  relative variance 1.07.
- **Correct restatement for Phase 2:** R = 1.65, 95% CI [1.04, 2.42]
  (local sampling error only; hosted-side error additional and unquantified);
  exclusion channel adds roughly [1.57, 2.36] with no data-supported direction.
  Kerdock v3 hosted expectation 9.8e-8 with band [6.7e-8, 1.56e-7].

## Files

`PREDECLARATION.md`, `step0.py`/`step0.json`, `g1_bootstrap.py`/`g1_bootstrap.json`,
`attack.py`/`attack.json`, `exclusion_direction.py`/`exclusion_direction.json`,
`tail_probs.json`, `finalize.py`, `results.json`, `VERDICT.md`.
Source (read-only): `../c1_local_mc_calibration/c1_local_mc25.json`.
No file outside this directory was written. No git, no network, no submissions,
no truth/scorer/holdout reads, zero estimator compute.
