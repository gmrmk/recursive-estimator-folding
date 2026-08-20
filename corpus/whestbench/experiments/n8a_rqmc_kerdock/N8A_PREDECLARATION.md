# N8a predeclaration — RQMC-ified Kerdock sampling core

Date: 2026-08-08 (before code). First mutation of the honest constant-factor
stack (journal Next action after the N7 kill).

## Mechanism

Replace the iid (or whatever it currently is) draw stage of the frozen
Kerdock M71 v3 estimator with the antithetic Kronecker-lattice +
Cranley-Patterson construction that measured 1.5-2.7x variance gains vs iid
at large N in N7 — IF AND ONLY IF the premise holds that Kerdock's current
sampling is not already an equivalent structured set.

## Premise gate G0 (cheapest falsifier, BEFORE any build)

Read the v3 candidate source (kerdock_l1_owned_buffer/
candidate_source_validator_v3/) and determine the sampling construction
(the packaged kerdock_phases.npz suggests a Kerdock-code structured set).
- If the sampler is already a low-discrepancy/structured construction:
  measure, on 3 synthetic He nets at the estimator's native sample count, the
  paired variance of (a) the existing construction vs (b) Kronecker+CP
  antithetic at MATCHED sample count and matched downstream processing.
  KILL N8a if (b)/(a) variance ratio > 0.83 (i.e., less than 1.2x gain) —
  the lattice adds nothing over the existing structure.
- If the sampler is iid: proceed to the build with the same 1.2x kill gate
  on the paired full-estimator comparison.

## Build gates (only if G0 survives)

- G1: the variant is the frozen v3 with ONLY the draw stage replaced;
  bitwise-identical processing downstream; diff surface = the sampling
  construction.
- G2 (paired factorial, synthetic nets only, n>=6 nets x 4 replicates):
  paired raw-MSE ratio <= 0.83 (>=1.2x better) with a bootstrap CI excluding
  1.0; billed-FLOP delta within +2% of v3; peak memory not above v3's
  (its 1.445 MiB hosted margin is the binding constraint — ANY memory
  regression kills).
- G3: package (folder mode), validate-package + contract validate + member
  listing (the T3 near-miss rule).

## Bias class

Same deliberately-biased family as v3 (pilot-rescue bias unchanged); the
draw-stage swap changes variance, not the bias mechanism. Engineering-gated;
NO local score run (public rows stay descriptive-burned); graded evidence at
user-return only.

## Firewall

Synthetic nets only; frozen v3 sources untouched; no sealed cells; no
submission; all work metered through flopscope in the variant.
