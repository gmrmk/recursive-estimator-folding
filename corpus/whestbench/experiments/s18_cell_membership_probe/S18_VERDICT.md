# S18 verdict -- ReLU cell-membership probe

Ledger id: `s18_cell_membership_probe`
Date: 2026-08-10.  Direction set: full antipodally-doubled Kerdock design
(64,512 directions at radius mean_chi(256)=15.98438), no subsample.
Nets: synthetic He, seeds 101/202/303, width 256, depth 32, bias-free,
one Haar rotation each (seed 900000 + net*1000 + 0) -- the S5/S15 trio.
Target f(u) = S5 ybar (neuron-averaged final post-ReLU), reused read-only.
Base: S15 Base-B (256 linear singular projections + 256 diagonal squares +
top-16 cross = 633 columns; spans all of degree-1, exact ||pre1||^2).
Gate quantity: swap-halves OUT-OF-SAMPLE incremental R^2 beyond Base-B,
antipodal pairs kept in the same half, split seed 777000+net (S15-exact).

## INTERPRETATIONS / DEVIATIONS (recorded up front)

1. Arm (a) `active_count` is treated as a CONTROL and excluded from the
   gate, per the predeclaration's own parenthetical ("this overlaps
   firing-rate - control"). It equals 256 x S15's C1 firing rate (affine, so
   identical R^2) and is used to reproduce S15's cached C1 numbers as a
   pipeline cross-check. Gating it would re-classify S15's already-measured
   and already-killed smooth covariate as a new "signal", contradicting the
   task's framing (the un-probed crack is the NON-smooth combinatorial
   family).
2. "Hashed sign-pattern bucket" is implemented as a collision-free perfect
   hash: the 256 sign bits are packed to 32 bytes and cells are identified by
   exact byte-row uniqueness. No information is lost to hash collisions.
3. "Per-net modal pattern" is computed under BOTH readings -- (i) per-unit
   majority vote over the base directions (over the doubled set every unit is
   active on exactly half the rows by antipodality, so the vote is taken over
   the base half), and (ii) the literal most-frequent full pattern
   (lexicographic tie-break; degenerate here, see census). Both variants are
   gated; the KILL requires both below the bar (conservative in the
   anti-KILL direction).

No other deviations: arms, nets, base, split, and gate bars are exactly as
predeclared.

## VERDICT: KILL -- the window closes; the dispersion family is sealed with no remaining named crack

Every gated cell-membership feature set is below the predeclared
fitting-noise cost 2.63e-5 on all 3 nets. Best gated value = 2.371e-5
(hamming_modal_majority, net 303). No gated set reaches the 1e-4 SIGNAL bar
on ANY net (0 of 3, vs 2+ required). The prediction on record (KILL) is
confirmed.

Gate arithmetic (OOS incremental R^2 beyond Base-B; bar: KILL < 2.63e-5 on
all nets, SIGNAL >= 1e-4 on 2+ nets):

| feature set                | net101     | net202     | net303     | max        | < 2.63e-5 all? |
|----------------------------|------------|------------|------------|------------|----------------|
| (b) cells_k16              | +1.539e-05 | +1.053e-05 | +4.261e-06 | 1.539e-05  | yes |
| (b) cells_k64              | -2.317e-05 | -7.6e-08   | -3.568e-05 | -7.6e-08   | yes |
| (b) cells_k256             | -1.931e-04 | -9.808e-05 | -6.974e-05 | -6.974e-05 | yes |
| (c) hamming_modal_majority | +1.996e-05 | -3.511e-06 | +2.371e-05 | 2.371e-05  | yes |
| (c) hamming_modal_literal  | +2.153e-05 | +2.233e-05 | +2.016e-05 | 2.233e-05  | yes |
| (a) active_count (CONTROL) | +5.112e-03 | +5.945e-03 | +5.719e-03 | --         | not gated |

Uncertainty on the gated numbers: the AB/BA half-split pairs (in the JSON)
and the permutation null (below) both put the single-measurement spread at
~3e-5 to 1e-4 per set; every gated value sits inside its own null spread.

Honest margin notes:
- The best gated value (2.371e-5) is only 0.9x the bar -- a thin pass.  But
  the same set's permutation null reaches |5.3e-5| and its AB/BA halves
  (+1.59e-5 / +3.15e-5) are noise-consistent: there is no evidence of signal,
  just noise near the bar.
- hamming_modal_literal is positive on 3/3 nets (~2.1e-5).  Three same-sign
  draws have probability ~1/8 under a symmetric null -- not significant --
  and its own permutation null spans -4.7e-5..+1.2e-4.  Even if a real
  effect of 2.1e-5 existed there, it sits BELOW the 2.63e-5 per-feature
  profitability floor, so it cannot matter by the predeclared window
  arithmetic (the un-excluded window was [2.63e-5, 1e-4]).
- cells_k256 is consistently NEGATIVE (overfit penalty of 256 no-signal
  indicator coefficients), exactly the null expectation.

## The structural finding: cells do not recur at design spacing

Cell census (identical on all three nets): **all 64,512 directions occupy
64,512 DISTINCT first-layer activation cells** -- every cell is a singleton,
max cell count = 1, zero exact-zero preactivations.  This is the generic
arrangement fact (256 hyperplanes in R^256 realize all sign patterns), and it
makes the mechanism of the KILL transparent: at design spacing, first-layer
cell membership is a per-point unique identifier.  A top-k "most frequent
cell" indicator (frequency ties broken deterministically) is 1 on at most one
direction; fitted on the training half it can only memorize a single training
residual and can never activate on the held-out half.  Cell-identity features
are structurally incapable of out-of-sample generalization here -- and the
measured ~0/negative OOS incrementals confirm it mechanically.  The only
cell-derived quantities that CAN generalize are aggregates (count, Hamming
distance), and those measure at fitting noise.

This closes the last named crack: the residual is uncorrelated not only with
every smooth basis previously measured (zonal harmonics, first-layer moments,
kink distances) but with the arrangement-combinatorial features of the input
point as well, consistent with the god-node's independent chi2_1 speckle
account.

## Two-signal verification

1. **Split-sample OOS R^2** (the gate quantity): swap-halves, antipodal
   pairs never split, S15-exact.  Numbers above.
2. **Permutation null** (predeclared second signal): f shuffled across all
   64,512 directions, 3 permutations per net, identical pipeline.  Per-set
   max |incremental OOS| over the 9 net x perm draws:
   cells_k16 5.6e-5, cells_k64 6.7e-5, cells_k256 1.4e-4,
   hamming_modal_majority 5.3e-5, hamming_modal_literal 1.2e-4,
   active_count 1.3e-4.  The pipeline reports ~0 +- fitting noise under the
   null, and every gated measurement is inside its null spread: confirmed.

Additional instrument checks:
- **S15 C1 reproduction** (pipeline identity): arm (a) OOS incremental vs
  cached `s15_results.json` C1: 5.1115e-3 vs 5.1114e-3 (net101),
  5.9450e-3 vs 5.9441e-3 (202), 5.7191e-3 vs 5.7197e-3 (303) -- match to
  |diff| <= 8.8e-7 (residual difference is the relative-ridge scale change
  from count vs rate).  Base-B OOS R^2 also reproduces S15 exactly:
  0.3609 / 0.4037 / 0.4385.
- **Injection sensitivity**: a synthetic 1e-3 R^2 signal injected along the
  base-residualized Hamming covariate is recovered at 1.53e-3 / 0.89e-3 /
  0.71e-3 -- the instrument detects at the 1e-3 scale (and the recovery
  spread ~ few e-4 is consistent with the null noise); a 1e-4 signal on 2+
  nets could not have been missed by an order of magnitude.
- **Reuse verification**: d1 recomputed from an independent pre1 vs the
  saved S5 arrays: max abs diff = **0.0** on all three nets (bit-exact;
  confirms weights + rotation + W1_eff + kerdock all identical to S5/S15).

## Limitations

- Aggregate covariates ((a), (c)) enter linearly, as in S15; arm (b) is
  inherently nonlinear (indicators).  A nonlinear transform of the Hamming
  scalar is not measured, but it would have to beat a 2.63e-5 bar that the
  raw scalar misses inside noise, and S15 already bounded cheap nonlinear
  first-layer summaries at the % level against far looser bars.
- Cell frequencies (for top-k selection) are computed on the full direction
  set.  They involve only the input side (never f), so no target leakage;
  with an all-singleton census the selection is a deterministic tie-break
  either way.
- 3 permutations per net (9 null draws per set) -- enough to bound the noise
  scale at ~1e-4, not to resolve its tails.
- Only the FIRST-layer arrangement is probed (as predeclared: "the sign
  pattern / activation cell of the input point in the early layers" --
  layer 1 is the only layer whose cell structure is a function of u alone at
  ~1/32 forward cost; deeper patterns compose the same first-layer cells).

## Firewall

Synthetic He nets only; n8a machinery + S5 arrays + S15 results loaded
read-only (n8a loads the frozen v3 sampling asset kerdock_phases.npz
read-only); no dataset/truth/scorer/submission; no git; no touch of
m245_*/M243/M244 or any *_fable_oracle lane; writes confined to this
directory (s18_cell_membership_probe).

## Files
- `run_s18.py` -- harness (S15-mirrored design)
- `s18_results.json` -- full per-net / per-set numbers, census, nulls,
  injection, reuse checks
- `S18_VERDICT.md` -- this document
