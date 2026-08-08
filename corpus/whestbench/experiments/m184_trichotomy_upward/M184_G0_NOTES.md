# M184 G0 notes — trichotomy upward (static count)

Date: 2026-08-08. Runner: `run_m184_g0.py`. Results: `m184_g0_results.json`.
Wall time 0.5 s. Pinned python: work\whest-v014 (numpy 2.4.6, plain numpy,
sanctioned).

## VERDICT: KILL

Projected net billed reduction is 0.00% on all three nets (gate: KILL
< 15%). Not a modeling near-miss: the dynamic program that prices on-run
folding never found a single profitable fold segment on any layer of any
net, at the predeclared threshold or at any lax threshold probed. The
mechanism's premise — mid-layer certain-on populations large enough to
compose past — does not exist at width 256.

| net | v3 billed | M184 billed | reduction |
|-----|-----------|-------------|-----------|
| 101 | 181.67e9  | 181.67e9    | 0.00%     |
| 202 | 170.03e9  | 170.03e9    | 0.00%     |
| 303 | 163.48e9  | 163.48e9    | 0.00%     |

The predeclaration's honesty bound called this exact failure mode:
"Mid-layer certain-on fractions at width 256 may be small (alpha must be
large for ALL 64k samples); the static count decides in minutes." It did.

## Thresholds and the misclassification calculation

Certain-on(l,j): alpha[l][j] > +6.7 AND min over the 512 pilot paths > 0.
Certain-dead(l,j): alpha[l][j] < -6.7 AND max over the 512 pilot paths <= 0.

Calculation (predeclared requirement): under the diagonal-Gaussian
surrogate for the sampling distribution, the per-sample tail mass at
alpha = 6.7 is Phi(-6.7) = erfc(6.7/sqrt 2)/2 = 1.042e-11. Union bound
over all n = 2 x 32,256 = 64,512 realized sample paths:
64,512 x 1.042e-11 = 6.72e-7 < 1e-6 per neuron (value recorded in the
JSON). The predeclaration's illustrative alpha = 4 fails this bound by
six orders of magnitude (64,512 x Phi(-4) ~= 2.0 expected flips), hence
6.7. The 512-path pilot min/max is the second, distribution-free signal
on the pilot paths themselves; a G1 build would still gate exact
equality per the predeclaration.

## Per-layer certain-on / certain-dead fractions (the killing numbers)

Full per-layer tables are in the JSON (`nets[*].per_layer`). Summary:

- Layers 1–9 (all nets): certain-on count = 0. Nothing to fold where the
  matmuls are widest.
- Certain-on rises only near the fold boundary and peaks at layer 28:
  net 101: 32/189 active (16.9%); net 202: 29/179 (16.2%);
  net 303: 39/182 (21.4%).
- Break-even for even a single-layer fold: the matmul-term saving is
  on_l x (a_{l-1} + a_{l+1}) - a_{l-1} x a_{l+1}, positive only when
  on_l exceeds a_{l-1}a_{l+1}/(a_{l-1}+a_{l+1}) ~= 85–95 neurons at the
  realized deep-layer active widths (~170–190). Observed maximum
  anywhere: 39. The mechanism is short of break-even by a factor ~2.3x
  at its single best layer, and infinitely short everywhere else.
- Certain-dead: nonzero counts appear from layer ~8 onward (up to 37 at
  net 101 layer 27), but every certain-dead neuron is already inside
  v3's pruned set on every layer of every net (asserted at runtime, see
  increment accounting).
- Interpretation against the predeclaration's premise: the measured rank
  collapse (participation ratio 128 -> 5.2) does NOT convert into
  per-neuron sign certainty at width 256 — mid-layer |alpha| stays
  overwhelmingly inside the kink band; the collapse is a covariance
  phenomenon, not a per-coordinate margin phenomenon.

## Threshold sensitivity (kill robustness)

Reduction stays exactly 0.00% on all three nets even under lax
thresholds that do NOT satisfy the exactness bound (pilot-confirm
unchanged): alpha > 5.0 (max on 57), alpha > 4.0 (max on 69), alpha >
3.0 = v3's own fold band edge (max on 83, still < 85–95 break-even; DP
longest segment still 1 everywhere). The kill is not an artifact of the
6.7 margin: no legal OR illegal threshold in [3.0, 6.7] produces one
profitable fold.

## Billed model and increment accounting

Pricing: v0.10 conventions verbatim from t3 `capped_fold3.py` (matmul
2mkn-mn; pointwise 1/elem; fancy-index gather 4/output element; sort
8 n ceil(log2 n); int concat 2/elem). v3-specific substitutions: the
loop sample matmul is billed by the frozen
`cost_model.owned_batched_candidate_bill` (RowBlockedBatchedWinograd's
own bill authority, ported as plain arithmetic); the first product is
the exact phased-WHT butterfly billed op-by-op (14 n w ~= 0.116e9,
vs ~4.2e9 direct). Fold section and tangent recursion ported
structurally from `predict_main_bill`.

Increment accounting, as predeclared:

- (a) dead-column skips: increment = 0 by construction, verified.
  v3's loop pruning drops every column with alpha < -2 whose 512-row
  pilot never fires; certain-dead (alpha < -6.7 AND pilot silent) is a
  strict subset, so certain-dead intersect v3-active = empty (runtime
  assertion on all 84 layer instances). M184 adds no dead skip v3 does
  not already take.
- (b) on-run composition: billed via a DP over collapse schedules.
  A segment folds certain-on columns at layers m+1..e-1 (per-sample
  work only on kink columns; each carrier's fold matrix updated once
  per net per layer at full matmul price — the "W^3 once" precompute),
  then collapses at layer e. The M184 arm also pays, per fold step: the
  on-candidate pilot confirmation matmul, index sorts, and all gathers
  at 4/element. The length-1 segment reproduces v3's per-layer bill
  EXACTLY (asserted against an independently written v3 bill on every
  layer of every net), so the v3 schedule is always feasible for the
  DP: M184_total <= v3_total holds by construction, and the observed
  equality means no fold segment anywhere pays for itself.
- (c) gather/sort overhead at 4/element: charged inside both arms at
  identical prices (and additionally against every fold step's slices).

## Deviations (loud)

1. Pilot paths: the predeclaration names "one 512-path Kerdock pilot".
   The runner forwards 2048 paths (first 4 trimmed frames + antipodes,
   exact radius, one Haar rotation seeded like v3's predict) — the
   extra 3 frames exist ONLY to replay v3's fold-layer partitions
   row-for-row (v3's fold pilot consults 2048 rows; both arms share
   this fold section, so it only affects the common denominator).
   Certain-on/dead classification uses only the 512-path block, which
   is row-for-row v3's own loop pilot.
2. Analytic diagonal pass computed in float64 (frozen estimator runs
   float32). Analysis-side only; the +-6.7 margin makes classification
   insensitive to the precision difference. Frozen sources untouched.
3. Two common-bill terms are rough models, stated as such: the Haar QR
   (2 w^3 stand-in; flopscope's QR price is unobservable in a plain-
   numpy static count) and the diagonal pass (~5 w^2 per layer). Both
   are identical in both arms and total ~0.03% of the bill; they cannot
   move a reduction that is exactly 0.
4. Gate ambiguity ("the projected net billed reduction" — per net vs
   aggregate) resolved conservatively both ways: KILL if any net or the
   geomean < 15%; PROMOTE only if all nets and the geomean >= 20%.
   Moot here (all identically 0).
5. One modeling defect was caught by the built-in cross-check during
   the first run and fixed before any verdict: v3's code gathers the
   layer weight rows twice when the cold-pilot branch runs (pilot +
   product) and capped_fold3 bills both; the segment model initially
   billed the row gather once (delta 4 a_prev w = 262,144/layer). The
   fix bills it in the plain-gather state; the len-1 == v3 equality now
   holds exactly on all 84 instances. No retuning of any gate.
6. M184 is forced to collapse to a materialized activation before the
   fold section (minimal-diff G1 assumption; feeding carriers into the
   frozen fold3 terminal code would be a larger diff). Conservative:
   could only have hidden additional savings, and the DP found none to
   extend anyway.

## Runtime verification signals

- mean_chi(256) formula check and Kerdock frame exact-radius check pass.
- v3-pruned columns are silent on the 512-path pilot block (asserted) —
  validates that the full-net pilot forward equals v3's pruned/folded
  pipeline row-for-row on pilot rows.
- certain-dead intersect v3-active = empty (asserted, all layers/nets).
- Independent double-implementation of the v3 layer bill vs the DP's
  length-1 segment: exact integer equality on all 84 layer instances.

## Firewall compliance

Synthetic He nets only (seeds 101/202/303, t3-style construction
verbatim from m180). The only file loaded: the frozen estimator's own
shipped `kerdock_phases.npz` (read-only). No datasets, truth, scorer,
or submission access; no git; all writes inside this experiment
directory. Frozen candidate sources read, never modified.

## Disposition

M184 is killed at G0. The kill is structural, not marginal: certain-on
mass is zero where the network is wide and ~2.3x below break-even at its
single best layer, robust across every threshold from the predeclared
6.7 down to an illegally lax 3.0. Per the predeclaration the kill is
final; the G1–G4 ladder is not entered. This was the last mined
mechanism standing from the M182 list.
