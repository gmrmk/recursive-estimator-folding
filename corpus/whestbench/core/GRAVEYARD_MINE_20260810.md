# Graveyard mine — record-level sweep of the full ledger (2026-08-10)

Owner instinct: "there are other historically failed mechanisms and
uncertainties that can be mutated in our graveyard." VERDICT: the instinct
was RIGHT at record resolution. Six Opus-5 miners read ~307 records
(mechanism ledger + uncertainty dispositions) one at a time; Fable-5
judged every proposal against the record's own evidence. Result:
**12 revivals judged falsifier-worthy, 31 salvage items, 29 framing-closes
flagged, 4 stays-dead.** Full per-record detail: workflow wf_436a0c3d-2f0
journal (session archive); this doc is the actionable compression.

Scope guard: the Phase-1 prize path is FROZEN (selection locked
#326094 + #327519) and none of this touches it. Payoff targets: Phase 2
(opens Aug 18), the Aug-17 writeup, and record hygiene.

## The headline finds

1. **The x5 hostile-residual convention killed five records on refuted
   arithmetic** (m145/m153/m157/m160/m163/m164). Every structural gate
   PASSED; the sole binding failure multiplied measured local residual by
   a reported-level "roughly 5x" legacy convention. Fresh hosted graded
   data (post-safeguard update) observes the multiplier at k ~= 1.0
   (hosted C/B 0.650 vs local 178.5e9 agree to 1.0%). At k=1 all five
   workers were far under gate. Falsifier: re-run the EXISTING five-worker
   harness (terra_m160_hostile_deploy/) - response-free, already built.
   If it passes, the self-hosted formal-pilot family is live for Phase 2.
2. **Three "kills" were never run at all** - ledger status=proposed, no
   result field: latent_sparse_radial_cubature (idx 11),
   flatworm_response_ladder (idx 33), ecn psi-swap (idx 35, whose own
   judge left the family formally open and prescribed the exact fold).
   Inaction is not a disposition. Each has a cheap frozen-state falsifier.
3. **The a1b/m185 tail-flag kill was mis-recorded**: the strongest
   correlate in the battery (borderline_frac, Spearman -0.563 vs raw MSE)
   was filed under F5 with P2b's ROTATION numbers (0.12-0.17) - a
   misattribution. Under corrected dispersion (net difficulty real at
   vD ~0.1), a difficulty-flag mechanism is a live Phase-2 question.
   Falsifier: a1b's exact test re-run under the S1b generative model.
4. **Decision-layer re-derivation owed**: U9/S4 portfolio numbers and the
   S1 gates were computed under the refuted vD=7.57e-4; re-run
   run_s4.py/run_s1.py at vD 0.081/0.122 (minutes, committed seeds).
   Phase-1 selection is locked so this changes nothing now - it calibrates
   Phase-2 designation math.
5. Additional falsifier-worthy revivals: m179 producer (unlocks the m199
   blocked component), m116b/c streamed variants (step-0 arithmetic
   first), a4's retired constraint leg (30-second breach arithmetic),
   p2b proxy swap, c1 calibration bound (bootstrap of committed JSON),
   S17 instrument reuse as a diagnostic, U3 tail-fidelity 2-D grid, U4
   suite-size grep.

## Framing-closes (29) - dispositions closed by wording, not evidence

The full list is in the journal; the classes: "OVERTAKEN" closes that
killed the question's context but not its substance (U1 pattern, found
in U3/U5/U13/Gen-3-U14); status labels stronger than their gates (S8
"screened" after 3/3 PASS-gate failure; S12 "PARTIAL" below its
predeclared bar); thresholds inherited rather than derived (S2's rho
gate from P2b's failure level); population accounting (the "238 records"
figure vs actual); and - flagged against TODAY'S work - S1b's sole
validation target was mislabeled "hosted" (it is the local synthetic
m185 stage-1 checkpoint; m185's own firewall field proves it). The v8
writeup wording is corrected in the same commit as this doc. S1b's
vF pooling caveat and range-vs-moment close are recorded as honest
limitations for any future S1c.

## Stays-dead (4) and the clean segments

The M120-M179 lineage is clean for score revival (its kills were version
facts, correctly recorded, except the x5 convention above); the S-series
mechanism kills (S5/S6/S9/S10/S11/S13/S15/S16/S18) all hold on their own
measurements. The seven family boundaries were separately re-attacked and
held (GEN7_ADVERSARIAL_CLOSURE). Nothing in this mine contradicts the
Gen-7 floor result: no revival claims Phase-1 score headroom; the floor
stands.

## Execution queue (fold discipline: cheapest falsifier first, one at a time)

Tier 0 (arithmetic/grep on committed data, minutes): a4 breach
arithmetic; U4 suite-size grep; m116 step-0 bill recovery; c1 bootstrap;
U9/S4 + S1 re-runs at corrected vD.
Tier 1 (existing harnesses, ~CPU-hour): m157/m160 five-worker k=1 rerun;
a1b oracle-flag test under S1b model; p2b proxy swap; S17 sigma^2 reuse.
Tier 2 (build + frozen states): idx 11 / idx 33 / idx 35 never-run
proposals; m179 -> m199 unlock.
Every run gets a ledger predeclaration first; kills remain final;
promotions require the full ladder. Timing: after the writeup files
(Aug 17) unless Jonah pulls any forward - except Tier-0 items feeding
writeup accuracy, which run before filing.
