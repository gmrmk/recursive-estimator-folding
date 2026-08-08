# T3 predeclaration — fold3-39936 with a deterministic per-network sample cap

Date: 2026-08-08 (before code). Task T3 of the reset plan, re-scoped per the
D-PM adjudication.

## The failure this fixes (measured, historical)

SALVAGE_MAP_20260806.md row 1: fold3 at n_base=39,936 suffered 5/100 budget
failures at n=100 from its activation-dependent cost tail — a strict failure
zero-predicts at multiplier 1, which erased the family's gain and is why the
32,256-point mutation became champion. The 5-net record (official5.json:
adjusted 1.4123151e-7 vs champion 2.1218e-7, mean C 248.963e9) shows the
family's upside when it does NOT breach. The cap exists to remove exactly the
breach mode, deterministically, and nothing else.

## Mechanism

A subclass of the frozen estimator_n39936 lineage that, per network, BEFORE
the main sampling run:
1. Runs the analytic diagonal pass + a pilot-identical simulation of the
   layer-loop active-set evolution (deterministic: frozen frame tensor +
   network weights only — the same pilot rows the real run uses).
2. From the realized active-set sizes (and terminal dead/kink/on partitions),
   evaluates a per-path billed-FLOP cost model c(n) and total-cost model
   C_pred(n) (main run + pilot + analytic overhead).
3. Chooses n_eff = the largest multiple of 256 (whole frames; frames are iid,
   so a prefix is statistically valid) with n_eff <= 39,936 and
   C_pred(n_eff) <= CAP where CAP = 0.9 * B = 244.8e9.
4. Slices the frozen frame tensor to n_eff rows, shadows self.n_base = n_eff
   on the instance, and delegates to the UNMODIFIED parent predict()
   (verbatim reuse of the audited math; the subprocess runner constructs a
   fresh instance per network, so instance shadowing is safe; restore in a
   finally block regardless).

No other change. Same 7-module package surface, same seed discipline, same
moment-tangent lambda, same radial control.

## Equation

n_eff = max { n = 256k : n <= 39936, C_pred(n) <= 244.8e9 },
C_pred(n) = overhead_fixed + sum_l cost_l(n; active/kink structure),
cost model calibrated once against metered billed FLOPs (G1).

## Gates (cheapest falsifier first; any failure = stop, first broken link)

- **G1 (cost-model calibration)**: on 3 synthetic He-init width-256 depth-32
  nets, C_pred(39936) must match the actually metered billed FLOPs of the
  uncapped estimator within ratio [0.98, 1.06] (never underestimating by more
  than 2%). KILL if the model underestimates billed cost by >2% on any net —
  an underestimating cap cannot guarantee the budget.
- **G2 (adversarial worst case, the point of the mutation)**: construct a
  low-pruning adversarial net (weights biased so alpha >= dead_alpha nearly
  everywhere). The capped estimator must (a) choose n_eff < 39,936, (b) run
  to completion, and (c) show metered C <= 0.9B + 2% tolerance. KILL if any
  of the three fails.
- **G3 (regression on easy nets)**: on the 3 G1 nets, if C_pred(39936) <=
  CAP then n_eff == 39,936 and the capped estimator's output is BITWISE
  IDENTICAL to the uncapped one (the cap must be a no-op off the tail).
- **G4 (package)**: whest validate-package passes on the packaged candidate
  in the pinned v0.14 env.
- **NO LOCAL SCORE GATE** (predeclared): public 0..99 is overused (R9) and
  the reserved 600..799 read is not spent here. Score evidence comes only
  from GRADED submissions at user-return (quota is the non-scarce currency).
  Until then the candidate's disposition is "engineering-gated,
  score-unknown" and may not be represented as a numerical winner.

## Bias class

Same deliberately-biased sampler family as the parent (pilot-rescue bias
unchanged). The cap adds NO new estimator bias on non-breaching networks
(G3 bitwise identity); on would-have-breached networks it trades a strict
failure (zero-prediction, multiplier 1) for a valid estimate at reduced n —
strictly dominant under the score law for any floor.

## Resource ceiling

Local G1/G2 runs: synthetic nets only, single process, minutes each. No
public rows, no sealed cells, no submission.
