# S2 — paid-information rotation weighting — VERDICT (2026-08-09)

## VERDICT: KILL — G0-CORRELATION pooled |rho| = 0.122 < 0.40 (predeclared gate)

Ledger id: s2_paid_information_rotation_weighting. Governing predeclaration:
the 2026-08-09 dispatch task. Harness: run_s2_gates.py. Results:
s2_results.json. Checkpoints: s2_partial_net{101,202,303}.npz. Run log:
_run.log. G0-EFFECT was NOT run — the predeclared stop on a failed
correlation gate applies.

## DEVIATIONS / INTERPRETATION DECISIONS (loud, none silent)

1. **No deviations from the task's arms or gates.** Both predeclared arms
   were implemented as specified; the gate was applied untouched; the run
   stopped exactly at the failed gate.
2. **Reduced direction count = Kerdock frames 0..31** (deterministic
   prefix, the P2 pilot convention): 8,192 antipodal pairs = 16,384
   evaluations per rotation. 32 ≈ 126/4 is the per-rotation budget a K=4
   budget split would actually pay, so the correlation was measured in the
   mechanism's operating regime. All 3 cached-truth nets (101/202/303),
   all 16 rotations per net (task allowed 2–3 nets, 8–16 rotations;
   directions were reduced before rotations, per instruction).
3. **Proxy** = mean over S=64 seeded balanced pair-splits and 256 neurons
   of (meanA − meanB)²/4; split index sets shared across (net, rotation).
   The closed form E[proxy] = s²/P (ddof-1 pair variance / n_pairs) was
   computed as the second derivation of the gate quantity; a single-split
   variant is reported as a practical diagnostic.
4. **"Pooled rho" = Pearson on WITHIN-NET ranks** pooled over the 48
   (net, rotation) points — the recorded P2-lineage convention (weighting
   happens within a net). LOUD FLAG: the naive raw-pooled diagnostic is
   +0.442 (split-avg) / +0.411 (closed form), i.e. ABOVE 0.4, but it is
   manufactured by across-net scale exactly as P2 documented — net 202 has
   both the largest proxies and the largest MSEs; within every single net
   the correlation is weak and sign-inconsistent (+0.11 / −0.30 / +0.56
   split-avg; +0.10 / −0.03 / +0.07 closed form). A weighting scheme
   operates within a net and cannot harvest an across-net scale artifact.
   The gate was applied to the within-net version, as predeclared.
5. **Archive usage.** p2_partial_net*.npz stores per-rotation FRAME means
   only (16×126×256), no pair-level data, so the archive alone could not
   carry the pair-level proxy; it was used read-only for the construction
   cross-checks and a non-gating frame-level diagnostic.

## Numbers of record (G0-CORRELATION)

Reduced-budget (32-frame) panel MSE: net101 mean 1.497e-6 (spread
12.0×), net202 2.326e-6 (3.9×), net303 1.485e-6 (7.5×) — the across-
rotation MSE spread the mechanism hoped to harvest is real at this budget.

Proxy (half-sample disagreement) across-rotation spread: only 1.40–1.48×
per net — the paid-sample dispersion is nearly rotation-invariant while
the realized QMC error varies 4–12×. This is the mechanical reason the
proxy dies.

| rho vs realized MSE      | net101 | net202 | net303 | pooled within-net | pooled raw (diag) |
|--------------------------|-------:|-------:|-------:|------------------:|------------------:|
| split-avg proxy (GATE)   | +0.106 | −0.297 | +0.556 | **+0.122**        | +0.442            |
| closed-form s²/P (check) | +0.097 | −0.026 | +0.071 | +0.047            | +0.411            |
| single split (diag)      | −0.035 | +0.491 | −0.326 | +0.043            | +0.109            |

Gate: pooled within-net |rho| = 0.122 < 0.40 → **KILL**. Bootstrap 95% CI
(4,000 draws, rotations resampled within net, seed 20260810):
[−0.153, +0.375] — the CI never reaches the gate from either side.

Archive full-budget frame-level diagnostic (non-gating): pooled within-net
−0.103 (per-net −0.462/+0.388/−0.235), consistent with the killed P2
frame-variance proxy (−0.340) in being weak and sign-unstable.

G0-EFFECT: not run (predeclared stop). MSE ratio and bias check therefore
not measured.

## Cross-checks (two-signal)

- Gate quantity re-derived a second way: the closed-form s²/P proxy
  (infinite-split limit, no split Monte-Carlo noise) gives pooled
  within-net rho +0.047 — confirms the KILL independently of the split
  sampling. The split-avg vs closed-form max relative deviation is 18.9%,
  consistent with the expected sqrt(2/64) ≈ 17.7% Monte-Carlo error per
  scalar; with proxy spreads of only ~1.4× this noise rescrambles ranks,
  which is itself evidence the proxy signal is below its own noise floor
  at any practical split count.
- Bitwise full-budget repeat of net101/r0 against the archived P2 frame
  means: identical (np.array_equal) — construction chain (weights,
  rotation seeds, Kerdock loader, forward) reproduces the P2 lineage
  exactly.
- Reduced-forward frame means vs archived frame_means[:, :32, :]: max abs
  diff 4.32e-7 (max rel 3.7e-5), float32 blocking-order tolerance — the
  reduced simulation is the archived one restricted to 32 frames.
- Pair-mean bookkeeping == direct overall mean, asserted every forward
  (atol 1e-12).
- Spearman via Pearson-on-ranks == 6Σd²/(n(n²−1)) formula, asserted for
  every rho.

## Limitations

- 16 rotations/net → per-net rho has wide sampling error; the pooled
  48-point statistic with bootstrap CI is the governing read, and its CI
  upper bound (+0.375) still misses the gate.
- The proxy was evaluated at one reduced budget (32 frames). At larger
  budgets the proxy's own noise shrinks, but the closed-form (noise-free)
  proxy already fails (+0.047), and the archive frame-level diagnostic at
  the FULL 126-frame budget is also weak (−0.103) — budget is not the
  bottleneck; rotation-invariance of the sample dispersion is.
- Split index sets shared across rotations (predeclared decision 3)
  correlate proxy noise across rotations; the closed-form check is immune
  to this and agrees on the KILL.
- Truth noise floors (1.2e-8–3.5e-8) are ≤ 2% of the reduced-budget MSEs;
  raw MSE was used, matching the P2 lineage.

## Constraint handed forward

The S2 mechanism assumed the paid samples reveal per-rotation quality via
half-sample disagreement. Measured: the disagreement (equivalently the
per-pair sample variance) varies only ~1.4× across rotations while the
realized integration error varies 4–12×. The Kerdock-rotation error is a
deterministic equidistribution property essentially invisible to iid-style
variance statistics of the sample itself — the same wall P2 (frame
variance, −0.34), the P2 pilot (−0.089) and P2b (weights-only, best
0.166) hit. Any future reopening needs a proxy sensitive to the
equidistribution error itself (e.g. discrepancy-like or truth-anchored
signals), not sample dispersion.

## Files

- run_s2_gates.py — harness (this experiment's only executable)
- s2_results.json — full numbers of record
- s2_partial_net101.npz, s2_partial_net202.npz, s2_partial_net303.npz —
  per-net checkpoints (fresh frame/pair statistics + rotations 0–3 pair
  means, retained for reproducibility)
- _run.log — console log of the recorded run

Read-only inputs (exact paths):
- ..\pb1_premise_battery\p2_results.json
- ..\pb1_premise_battery\p2_partial_net{101,202,303}.npz
- ..\m181_terminal_smoothing\m181_truth_net{101,202,303}.npz
- ..\..\..\..\..\..\work\scorefloor_generation\kerdock_l1_owned_buffer\candidate_source_validator_v3\kerdock_phases.npz
