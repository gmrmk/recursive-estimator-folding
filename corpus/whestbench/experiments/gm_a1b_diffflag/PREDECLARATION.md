# PREDECLARATION - gm_a1b_diffflag (graveyard revival falsifier)

Written BEFORE any harness code. Mining search key: `a1b_tail_apriori_flag`.
Mining records read: journal.jsonl lines 21 (agent a51c5a26d5f4ce651, mid-mseries)
and 32 (agent a4616c405a1d48131, nseries) of
`wf_436a0c3d-2f0/journal.jsonl`. Ledger records read: `a1b_tail_apriori_flag`
and `m185_tail_pruning_mechanism` in `corpus/whestbench/headroom/fold_ledger.json`.
Cited experiment dirs read: `a_series_granular_adversarial/` (a1b_tail_diagnostics.py,
a1b_tail_diagnostics.json, m185_g0_stage1_checkpoint.json, m185_g0_stage2_checkpoint.json),
`pb1_premise_battery/p2_results.json`, `s1b_dispersion_corrected/` (run_s1b.py, s1b_results.json).

## 1. Mechanism under test

A1b concluded "NO RELIABLE A-PRIORI FLAG" because its best weight-derived
diagnostic reached top-quartile precision/recall 0.50/0.50 against per-net
`mse_raw` on 80 synthetic nets, read as "coin flip". The mined changed premise
(S1b dispersion correction) is that `mse_raw` is a SINGLE rotation draw, so the
target is mostly rotation-draw noise, and 0.50 may already BE the ceiling that a
PERFECT net-difficulty oracle would score. If so, a1b measured its own noise
ceiling and its verdict sentence is stated above its earned level.

## 2. Equation / quantity

Generative model (S1b, `run_s1b.py`, unchanged):

    MSE_i = S * D_i * F_i
    D_i   = exp(U(-h, h)) / ((sinh h)/h),  Var(D)/E[D]^2 = vD
    F_i   ~ Uniform draw with replacement from the archived 48-value P2 pool
            (`p2_results.json` q1_oracle_headroom.per_net[*].mse_per_rotation,
             per-net mean-normalised then globally mean-normalised); vF = pool.var()
    S     constant -> irrelevant to rank statistics

PERFECT ORACLE = D_i exactly (zero-error knowledge of net difficulty).
A1b's exact scoring code is reused verbatim (`a1b_tail_diagnostics.py` lines 27-64):

    rho     = Pearson corr of ranks (argsort-argsort), no tie handling
    thr     = np.quantile(flag, 0.75);  flagged = flag >= thr
    tail    = mse >= np.quantile(mse, 0.75)
    prec    = tp/(tp+fp),  rec = tp/(tp+fn)

n = 80 nets per replicate, matching a1b.
Arms: vD in {7.568879454111777e-4 (old_control), 0.08135950765383865 (s17_low),
0.12203926148075797 (s17_high)}; vF = 0.3641995628656461. All four constants are
taken verbatim from `s1b_results.json`.

## 3. Predicted outcome (ON RECORD, before running)

From the nseries mining record's own executed numbers (0.501 / 0.536) and the
analytic attenuation it quotes (0.465 / 0.543):

| vD | predicted oracle Spearman | predicted oracle precision = recall |
|---|---|---|
| 7.57e-4 | ~0.05-0.08 | ~0.26-0.29 |
| 0.0814  | ~0.43-0.47 | ~0.50 |
| 0.1220  | ~0.50-0.54 | ~0.54 |

I predict the perfect oracle does NOT reach 0.65 precision at either corrected
vD, i.e. a1b's measured 0.50/0.50 is at or within noise of the perfect-oracle
ceiling under the corrected dispersion model.

Realizable-gain bound: predicted <= 0 (no positive suite gain) at all three vD.

## 4. Step-0 arithmetic gate (run FIRST, no Monte Carlo)

Compute the closed-form Spearman ceiling two ways:
  rho_lin(vD) = sqrt(vD/(vD+vF))            [relative-variance attenuation]
  rho_log(vD) = sqrt(vlogD/(vlogD+vlogF))   [log-scale attenuation, vlogD = h^2/3]

STEP-0 KILL: if rho ceiling >= 0.75 at BOTH corrected vD under BOTH formulas,
STOP immediately and report KILL_CONFIRMED (the perfect oracle is then plainly
far above a1b's measured 0.5627/0.50 and the original "diagnostics are weak"
reading stands without further compute).

## 5. Main gate (verbatim from the mined cheapest_falsifier)

> "If the perfect oracle scores materially above a1b's measured 0.50
> (say >= 0.65), the diagnostics really were weak and the kill stands as written."

Decision statistic: MC mean of oracle top-quartile precision (= recall by
construction; both quartile sets have exactly 20 of 80 members), n = 80.

- **KILL_CONFIRMED** if mean oracle precision >= 0.65 at BOTH vD = 0.0814 and
  vD = 0.1220.
- **REVIVED_PASS** if mean oracle precision <= 0.60 at BOTH corrected vD AND
  a1b's measured 0.50 lies inside the central 90% of the oracle's per-replicate
  precision distribution at at least one corrected vD (i.e. a perfect oracle
  routinely scores what a1b scored).
- **INCONCLUSIVE** if the mean lands in (0.60, 0.65) at either corrected vD, or
  if the two conditions above conflict.

No retuning past a failed gate. Gate numbers are fixed here.

## 6. Realizable-gain bound (secondary reported quantity, per vD)

Recomputed independently from `m185_g0_stage2_checkpoint.json` (committed,
read-only). Per-net adjusted score s = mse_raw * billed_flops_mean; groups are
the checkpoint's own `selection.worst` / `selection.median` (5 nets each):

    g_worst = geomean_i in worst  ( s_relaxed,i / s_default,i )
    g_med   = geomean_i in median ( s_relaxed,i / s_default,i )

Policy: "relax pruning on the top quartile flagged by the perfect difficulty
oracle". Expected suite score change (positive = better):

    gain(vD) = 0.25 * [ prec(vD) * (1 - g_worst) + (1 - prec(vD)) * (1 - g_med) ]
    break-even precision  prec* = (g_med - 1) / ((g_med - 1) + (1 - g_worst))

Reported per vD alongside prec(vD). This is a BOUND: it assumes zero-cost,
zero-error routing and the checkpoint's own group effect sizes.

## 7. Two-signal verification (required before any verdict)

1. Split-sample: two disjoint seed streams (100_000 reps each), means must agree
   within the pooled MC standard error x 3.
2. Independent analytic recomputation: population-limit (n -> inf) oracle
   precision computed by exact enumeration over the 48-point F pool crossed with
   a fine deterministic D grid - a completely different code path from the MC.
3. Bitwise repeat: same seed, sha256 of the per-replicate precision array equal.
4. Null control: an oracle drawn independently of D (permutation) must give
   precision 0.25 +- MC error at every vD; and vD -> large must give -> 1.0.
5. Provenance cross-check: reproduce a1b_tail_diagnostics.json exactly
   (all 7 Spearmans, flag_precision, flag_recall, spread) from the frozen
   stage-1 checkpoint before trusting the protocol re-implementation.

## 8. Firewall / envelope

Synthetic + committed cached JSON only. No truth/scorer/holdout reads, no
network, no git, no submissions. Nothing under m245_*/M243/M244/tasks/journal-m245*
is read. Writes confined to this directory. Expected wall time: minutes, far
inside the ~90-minute envelope.
