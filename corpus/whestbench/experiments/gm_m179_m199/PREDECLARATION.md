# PREDECLARATION - graveyard revival gm_m179_m199

Written BEFORE any harness code. Frozen at authoring time; no gate number below
may be changed after a run.

Mining key: `m179_exact_background_archive_producer`
Ledger record: `corpus/whestbench/headroom/fold_ledger.json`
  -> `m179_exact_background_archive_producer`, `m199_composed_cost_reconciliation`,
     `m200_streaming_overlap_fixture`
Cited experiment dirs (READ-ONLY, never edited):
  `m179_background_archive_producer/`, `m199_composed_cost_reconciliation/`,
  `m200_streaming_overlap_fixture/`, `m198_source211_delay_one_adapter/`,
  `m125_source_batched_forward_tangent/`, `m178_certified_phi2_owent/`

## 1. What the original kill actually measured

M199 returned `BLOCKED_OVERLAP`, not `KILL_COST`. Its ledger row
`m125b_legacy_background_replacement_ceiling` (7.73675016B = legacy raw
6.189400128B x 1.25) is classed `unproved_replacement_candidate` with the
literal note:

> "M125b books 32 layers; M179 archives layers 1-31 and omits terminal mu_32,
>  so the full row cannot currently be removed."

The other denial grounds are equally bookkeeping: differing numerical/reserve
conventions, and "no identical call/result/lifetime trace exists". None is a
mathematical obstruction. Consequence: strict composed total 98.013128528B,
strict headroom 1.986871472B against the frozen 100B endpoint.

## 2. Changed premise

M179 (2026-08-07) and M200 (2026-08-09) were both built AFTER M199's blocking
premise was written. M179 supplies the certified metered 31-layer recurrence at
8.304492288B (0.267886848B/layer marginal). M200 supplies exactly the artifact
M199 named as "the only lawful child": a response-free one-pass streaming
composition fixture with an explicit birth/death event ledger.

Mechanically decisive fact discovered while reading (recorded here BEFORE
running): `m200_streaming_overlap.run_streaming_overlap` already performs a
FULL `_m179_stream_step` on the terminal weight `W_(H+1)`. Therefore feeding it
L = 32 weight matrices IS the "32-layer M179 producer": H = 31 archived source
layers plus a terminal layer that emits mu_32. No frozen source file needs to
be edited; the extension is a call-site depth change.

## 3. Mechanism under test

Extend M179's certified recurrence by one layer to emit the terminal mu_32
(same M178 provider, same fail-closed strata, +0.267886848B), and run M200's
streaming fixture as an operand/result/dtype/lifetime-identity trace proving
that the legacy M125b 32-layer background call is REMOVED rather than shadowed.
That converts the 7.73675016B row from `unproved_replacement_candidate` to
proved replacement.

## 4. Quantities and equations

Let (all in FLOPs):

    pairs        = 256*255/2                    = 32640
    per_pair     = F_M178 + F_ASSEMBLY_PER_PAIR = 4048 + 42 = 4090
    pair_layer   = pairs * per_pair             = 133,497,600
    diag_layer   = 256 * (2*316 + 40)           = 172,032
    mm_layer     = flopscope-METERED matmul bill of (mu@W, V@W, W.T@VW)
    per_layer    = pair_layer + diag_layer + mm_layer
    B32          = 32 * per_layer               (32-layer inclusive metered bill)

M199 arithmetic identities used as anchors:

    strict_no_replacement_partial            = 98.013128528 B
    strict_no_replacement_headroom           =  1.986871472 B
    legacy background replacement ceiling    =  7.73675016  B
    conditional_replacement_headroom         =  9.723621632 B
      (identity check 1: 7.73675016 + 1.986871472 = 9.723621632)
      (identity check 2: 100 - 90.276378368      = 9.723621632)

Post-replacement composed total, convention A (M179 billed raw, as metered,
which is the convention in which 98.013128528 was formed):

    T_A = 89.70863624 + B32/1e9 - 7.73675016

Post-replacement composed total, convention B (M179 normalized to the legacy
worksheet's 1.25 protected reserve, as the mined revival mechanism demands):

    T_B = 89.70863624 + 1.25*B32/1e9 - 7.73675016

## 5. Predicted outcome (ON RECORD, before any run)

- STEP 0 metering: mm_layer re-meters to 134,217,216; per_layer = 267,886,848;
  B32 = 8,572,379,136 = 8.572379136e9.
- GATE 0 (the mined gate b) PASSES with margin 9.723621632e9 - 8.572379136e9
  = 1.151242496e9.
- T_A = 90.544265216 B, headroom 9.455734784 B (a 4.76x expansion of strict
  headroom, matching the mined expected_gain "about 90.544B / about 9.456B").
- T_B = 92.687360000 B, headroom 7.312640000 B (still under 100B; recorded
  because under convention B the STRICT no-replacement total is 100.0892516 B,
  i.e. already over the endpoint, so the replacement is what rescues it).
- STEP 1 (widths 2..7, depth 32) passes every M200 gate.
- STEP 2 (width 256, depth 32) passes every M200 gate. Named residual risks, in
  descending order of my prior: (i) parity degradation past 2e-12 from
  ill-conditioning as pair correlations approach 1 at depth 32 (a width-24
  probe reached max|rho| = 0.998540 at layer 32); (ii) fail-closed RHO_MAX
  raise (RHO_MAX = 0.9999999999999998); (iii) wall-clock overrun.

## 6. Arms

### STEP 0 - arithmetic/metering gate (run FIRST, stop if it kills)
Re-meter `mm_layer` live through flopscope 0.10.0 on the pinned interpreter,
recompute `per_layer` and `B32`, and evaluate GATE 0.

### ARM B - M200 frozen harness at depth 32, frozen widths
Widths (2,3,4,5,6,7) x replicates (0,1) = 12 cells, L = 32 weight matrices per
cell (H = 31 source layers + terminal). Seeds derived by the same frozen
formula shape as `m200.frozen_seed`, re-implemented in MY runner because the
frozen function refuses depths outside 3..6. Frozen M200 module is IMPORTED,
never edited.

### ARM C - real-scale run: width 256, depth 32, one seed
The load-bearing arm: the actual N=256 composition geometry. Hard wall cap
60 minutes; per-layer checkpointing; driven in my own foreground.

## 7. Gates (exact numbers)

GATE 0 (mined falsifier clause b):
  KILL if B32 > 9.723621632e9. PASS otherwise.
GATE 0X (convention cross-check, secondary, convention-consistent form):
  KILL if T_A > 100.0 B. Report T_B alongside; T_B > 100.0 B is reported as a
  convention-sensitivity flag, NOT as a kill of the mined gate.

Per-cell gates in ARM B and ARM C (mined falsifier clause a plus M200's own
frozen contract):
  G1 counts == (background_steps, source_packets, conversions, injections,
      transports, terminal_responses, background_rebuilds_inside_stream)
      == (31, 31, 31, 31, 30, 1, 0)
  G2 `LivenessAudit.assert_gate()` passes; max_live_named_objects <= 5; all
      eight retained counters == 0
  G3 parity vs the isolated full-archive reference:
      max abs error over source-terminal AND final-terminal mean/covariance
      <= 2.0e-12
  G4 per-layer impulse max abs error == 0.0 exactly
  G5 LEGACY-CALL SURVEILLANCE (independent, added by me): a monkeypatched
      counter on `m198.build_extended_background` records ZERO calls during the
      measured stream. Non-zero => the legacy 32-layer background call survives
      => KILL_SHADOW.
  G6 EVENT-LEDGER LIFETIME SURVEILLANCE: every EventRecord has
      `death_order is not None` (no buffer survives the stream), and every
      `operation` string lies in the allowed streaming set
      {m200.initial_background.*, m200.borrowed_weight_w_k,
       m200.borrowed_terminal_weight_w_h_plus_1, m200.terminal_w_h_plus_1_response,
       m179.exact_step.*, m198.context_copy.*, m198.delay_one.*,
       m125b.transport.*, m125b.accumulator_after_source_injection,
       fixture_source_bound_to}. Any operation naming a legacy background
      rebuild => KILL_SHADOW.
  G7 TERMINAL mu_32 EXISTS: the terminal stage's emitting layer index == 32,
      and its post-ReLU mean is finite with max|mu_32| > 0.
  G8 RESULT IDENTITY (independent recomputation, the second signal): mu_32 as
      emitted by the streamed 32-layer producer equals mu_32 from an
      independent call to `m179_background_producer.zero_order_recurrence`
      over the same 32 weights, to max abs error <= 1.0e-12. Larger => the
      replacement does not reproduce the legacy terminal readout => KILL.

## 8. Kill conditions / verdict rules

- `KILL_COST`: GATE 0 fails. STOP; do not run ARM B or ARM C.
- `KILL_SHADOW`: G5 or G6 fails in any cell.
- `KILL_PARITY`: G3 or G8 fails in any cell.
- `KILL_REACHABILITY`: the 32-layer producer raises fail-closed (RHO_MAX /
  non-PSD / rank-one) on generic He weights in ARM C, i.e. the 32-layer
  extension is not reachable at the real composition width.
- `REVIVED_PASS`: GATE 0 passes AND every one of G1..G8 passes in ALL ARM B
  cells AND in ARM C.
- `INCONCLUSIVE`: ARM C cannot complete inside the 60-minute cap and ARM B is
  clean. ARM B alone is then reported as the largest completed sub-check.

## 9. Scope discipline

This falsifier tests exactly two of M199's four denial grounds: the 31-vs-32
layer scope, and the missing call/result/lifetime identity trace. It does NOT
claim to resolve the remaining ground (differing numerical/reserve conventions)
beyond reporting both conventions in GATE 0X. A PASS here is a component-level
revival of the composition arithmetic, not an estimator, variance, MSE, score,
or submission claim. M205's other blocker (a missing physical K4/K31/K22
provider) remains untouched.

## 10. Firewall

Synthetic He-Gaussian weights only. No truth, scorer, holdout, private data,
leaderboard, submission, network, or git. All writes confined to
`corpus/whestbench/experiments/gm_m179_m199/`. Frozen sources are imported
read-only. `m245_*`, `M243`, `M244`, `tasks/`, `journal-m245*` are not read,
imported, or touched.
