# U9 designation-threshold refresh (Sep 19 decision analysis)

Date: 2026-08-10. Analysis only — NOT a submission. Reuses the committed S1
suite-risk and S4 portfolio bootstrap machinery verbatim (same model, same
seeds) with the reported threshold grid re-pointed at the CURRENT
post-re-grade board and read against the S17 point-evaluation floor.

- Harness: `run_u9.py` (this dir). Outputs: `u9_tables.json`.
- Reused: `s1_suite_risk/run_s1.py`, `s4_portfolio/run_s4.py` (model + seeds).
- Reference floor: `s17_ibc_floor/s17_results.json`.
- Board source: `core/RAYAN53_FORENSICS_20260810.md` + task board (reported level).

## Two-signal verification (cross-check)

The refresh uses the identical master seeds as the committed runs, so at the
thresholds the committed runs already reported, the re-run must reproduce them
exactly. It does (asserted in the harness, both PASS):

| quantity | committed | U9 re-run |
|---|---|---|
| S1 P(champion<1.6e-7) R=1 | 0.06434 | 0.06434 |
| S1 P(champion<1.6e-7) R=6 | 0.0001 | 0.0001 |
| S1 P(champion<1.0e-7) all R | 0.0 | 0.0 |
| S4 baseline P(A<1.6e-7) | 0.06373 | 0.06373 |
| S4 Door B P(min<1.6e-7) | 0.12373 | 0.12373 |
| S4 Door B P(min<1.55e-7) | 0.05701 | 0.05701 |
| S4 Door A P(min<1.6e-7) | 0.93972 | 0.93972 |
| S4 Door A P(min<1.55e-7) | 0.87683 | 0.87683 |

The new-threshold P-values ride the same seed streams and the same anchor
(champion 1.83e-7 adjusted). MC batch SE from S4 is ~1e-3 on the near-rival-band
probabilities; the 1.3e-7 and lower cells are small-count (SE ~2-3e-5).

## Current board (reported)

Score law S = MSE * max(0.1, C/B), B = 2.72e11 (adjusted = the graded number).

- rayan53 1.5e-9 adjusted — accounting / compute-multiplier position (winnow-exposed).
- joe_wanza 2.11e-8 adjusted — over-budget (5.27x) + public-suite overfit (winnow-exposed).
- Honest band ~2.1e-8 .. 7.4e-8: ednacob 4.62e-8, dpskv5 3.68e-8, huang 4.62e-8,
  dstepanov ~6e-8, ely2sh 6.26e-8, oabuod 7.35e-8.
- Near-rival band ~1.55e-7 .. 1.6e-7: natasha, shiv_m, SOX.
- Us: champion 1.832e-7 adjusted (2.818e-7 raw).

S17 floor: champion sits 1.79x above the point-evaluation sampling cost floor
(near-optimal in the point-eval class). ednacob sits 2.2x-4.0x BELOW that same
floor — the honest band is only reachable by seed-side extraction we do not own.

---

## Task 1 — S1: P(champion suite-score < T) by rotation budget R

Champion anchored at 1.83e-7; suite score = mean over 50 nets of
S * D_i * mean(F_i1..F_iR). R splits the rotation budget (variance / R, mean
preserved). 100,000 synthetic suites per cell.

| T (adjusted) | R=1 | R=2 | R=4 | R=6 |
|---|---|---|---|---|
| 5.0e-8  | 0        | 0       | 0       | 0      |
| 7.5e-8  | 0        | 0       | 0       | 0      |
| 1.0e-7  | 0        | 0       | 0       | 0      |
| 1.3e-7  | 1e-5     | 0       | 0       | 0      |
| 1.55e-7 | 0.02939  | 0.00317 | 9e-5    | 0      |
| 1.6e-7  | 0.06434  | 0.01431 | 0.00107 | 0.0001 |

Suite-score dispersion: R=1 SD 1.563e-8, P5-P95 [1.583e-7, 2.097e-7];
R=6 SD 6.42e-9, P5-P95 [1.725e-7, 1.937e-7].

Reading: R-splitting moves the WRONG way for reaching any cutoff below the
champion mean. It reduces variance, concentrating the distribution around
1.83e-7 and SHRINKING the lower tail (R=6 P(<1.6e-7)=0.0001 is 640x smaller
than R=1's 0.064). To reach a threshold below your mean you want the widest
distribution, R=1. No R variant reaches below 1.3e-7 with any probability, and
nothing reaches the honest band (<=7.4e-8) at all.

---

## Task 2 — S4: P(at least one designated entry < T), two slots

Slot A = champion (1.83e-7, R=1). Slot B:
- Door B = decorrelated same-mean duplicate (spawn(2); Gaussian copula rho=0.0;
  residual score correlation 0.24% from the shared 50-net difficulty draw).
- Door A = fold3cap (mean 1.41e-7, R=1; canary-pending, weak 5-net evidence).

P(min(A,B) < T), 100,000 joint suites, CI95 in brackets:

| T | baseline P(A<T) | Door B  P(>=1 < T) | factor | Door A  P(>=1 < T) |
|---|---|---|---|---|
| 5.0e-8  | 0                  | 0                  | —    | 0                  |
| 7.5e-8  | 0                  | 0                  | —    | 0                  |
| 1.0e-7  | 0                  | 0                  | —    | 3e-5 [~0,7e-5]     |
| 1.3e-7  | 6e-5 [2e-5,1e-4]   | 9e-5 [3e-5,2e-4]   | 1.5x | 0.1846 [0.182,0.187] |
| 1.55e-7 | 0.02849 [0.027,0.030] | 0.05701 [0.056,0.058] | 2.00x | 0.87683 [0.875,0.878] |
| 1.6e-7  | 0.06373 [0.062,0.066] | 0.12373 [0.122,0.125] | 1.94x | 0.93972 [0.939,0.941] |

The doubling: Door B ~2.0x the single-designation tail at the near-rival band
(1.55-1.6e-7), exactly the decorrelation gain S4 certified — two independent
shots at the lower tail, base rate low enough that P(min<T) ~ 2*P(A<T). The
factor falls below 2 only where the base rate is already large (union
saturates) or where it is small-count (1.3e-7).

Door A dominates because fold3cap's mean 1.41e-7 sits BELOW the near-rival
thresholds, so its own marginal clears them ~87-94% of the time. But Door A too
collapses below its mean: 0.185 at 1.3e-7, 3e-5 at 1.0e-7, 0 at the honest band.
Door A's power is entirely contingent on the canary confirming ~1.41e-7 (U2).

---

## Task 3 — Decision table by prize-cutoff scenario

Best 2-slot designation under the S4 union rule (P at least one entry beats the
cutoff), with the S17 floor incorporated (no R-variant or portfolio move over
the point-eval champion reaches below the honest band).

| cutoff scenario | best 2-slot designation | P(win) | contingency |
|---|---|---|---|
| honest-band FLOOR ~2.0e-8 (rayan53/joe_wanza region) | none reaches it | **0** | unreachable — champion P5 is 1.583e-7, ~8x above |
| honest-band MID ~4.6e-8 (ednacob) | none reaches it | **0** | unreachable — requires seed-side extraction (S17) |
| honest-band CEIL ~7.4e-8 (oabuod) | none reaches it | **0** | unreachable — all designations 0 below 1.0e-7 |
| near-rival ~1.55e-7 | Door A (champion + fold3cap) | **0.877** | fold3cap canary must confirm ~1.41e-7 (U2) |
| " (fallback if canary fails) | Door B (champion + decorrelated dup) | **0.057** | organizer OK on duplicate nomination (U1) |
| " (no valid 2nd slot) | champion single | 0.028 | — |
| near-rival top ~1.6e-7 | Door A (champion + fold3cap) | **0.940** | U2 canary |
| " (fallback) | Door B (champion + decorrelated dup) | **0.124** | U1 |
| " (single) | champion single | 0.064 | — |

Below 1.3e-7 every designation is P<=1.8e-4; at and below 1.0e-7 every
designation available to us is P=0. The decision table is flat-zero across the
entire honest band; it only comes alive in the near-rival band.

---

## Task 4 — Honest reachability headline

No prize cutoff BELOW the near-rival band (~1.55-1.6e-7) is reachable by us.

The champion is pinned at 1.83e-7 adjusted, at the point-evaluation sampling
floor (S17: 1.79x above the cost-floor invariant, certified near-optimal in
class). The two levers we hold both fail to cross the honest band:

1. R-splitting (S1) reduces variance without moving the mean, which shrinks —
   not grows — the lower tail; it makes low cutoffs LESS reachable, not more.
2. Portfolio designation (S4) at best doubles the tail (Door B) or, if the
   fold3cap canary holds, shifts one slot's mean to 1.41e-7 (Door A). Door A
   tops out around its own mean: it reaches ~1.3-1.41e-7 with real probability
   and nothing below 1.0e-7.

The honest band (2.1e-8 .. 7.4e-8) sits 2.2x-4.0x BELOW our point-eval floor
(ednacob, S17): reaching it demands seed-side / weight-access extraction outside
our point-evaluation class, which the firewall and our optimality proofs
exclude. Our realistic designation targets therefore sit at the near-rival band
(~1.55-1.6e-7), and — only if the fold3cap canary confirms — just below it at
~1.41e-7 via Door A. Everything from the honest band down is out of reach by any
designation move on the current champion.

## Recommended 2-slot designation (decision-relevant cutoff)

The operative cutoff is fixed by the tables, not assumed: the near-rival band
(~1.55-1.6e-7) is the ONLY region where the choice of designation changes
P(win). Below 1.3e-7 every option is 0 (Task 1, Task 3), and at any cutoff at or
above the champion mean 1.83e-7 the champion clears it alone (P~1) so the second
slot is idle. Between those, the win probability swings from 0.028 to 0.94
purely on the designation. The recommendation for the Sep 19 slot decision is
therefore stated at the near-rival band:

- PRIMARY: Door A = champion + fold3cap (1.41e-7). Win probability 0.88 at a
  1.55e-7 cutoff, 0.94 at 1.6e-7 — roughly 15x Door B and 30x the single
  champion. Gated on the fold3cap canary confirming the ~1.41e-7 mean (U2). If
  the canary confirms, designate Door A.
- FALLBACK: Door B = champion + decorrelated same-mean duplicate. Win
  probability 0.057 at 1.55e-7, 0.124 at 1.6e-7 — ~2x the single-champion
  baseline (the S4-certified decorrelation gain). Gated on the organizer answer
  that duplicate nomination is permitted (U1). Use Door B only if the canary
  fails or is unresolved by Sep 19.

Neither door, and no R variant, buys any probability at a cutoff inside the
honest band; that region is decided by mechanism we do not have, not by
designation strategy.

## Deviations / notes

- The INPUT path `core/RAYAN53_FORENSICS_20260810.md` resolves to
  `corpus/whestbench/core/RAYAN53_FORENSICS_20260810.md` (found; board numbers
  match the task verbatim). No board field was re-derived — all board levels are
  reported.
- S1 R=1 P(<1.55e-7)=0.02939 and S4 baseline P(A<1.55e-7)=0.02849 are the same
  quantity computed under the two independent committed seed streams; they agree
  within MC error (~1.7 sigma on the 100k estimate). Consistent, not a conflict.
- No protected dir touched (m243/m244/m245/*_fable_oracle); no truth/scorer/
  submission; synthetic + cached inputs only; writes confined to this dir.
