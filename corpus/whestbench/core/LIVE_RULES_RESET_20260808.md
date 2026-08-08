# Live rules v12 (read 2026-08-08): the native-kernel thesis is dead; reset

Read first-hand from the live challenge + rules v12 (aicrowd.com). Supersedes
the corpus's stale 2026-08-03 forensics. Response-free; no sealed material read.

## The killer facts (rules v12, verbatim consequences)

- **Native/off-flopscope work is PENALIZED, not favored.** 5.5: effective budget
  = flopscope analytical FLOPs + "residual wall-clock time outside flopscope
  operations, converted to FLOPs at an **unfavorable per-second rate**." 5.2:
  "the analytical FLOP calculation gives **favorable treatment to flopscope
  primitives** ... This design encourages a focus on **algorithm design rather
  than on optimizing numeric primitives**." 5.5: "The scoring metric depends on
  analytical FLOP usage and prediction values, **not on wall-clock time**."
- **The residual-time exploit was already PATCHED (2026-08-03).** Challenge
  update: "flopscope v0.10.0, **cost-model fixes, residual-time safeguards**."
  The <0.1%-instrumented-share leaders the corpus saw were exploiting the OLD
  flopscope; that gap is closed.
- **Grader pins your code to ~2 vCPU** (overview widget: "1 core (2 vCPU) for
  your code · 7-core flopscope backend"; rules 5.6 lists a 16-vCPU instance).
  So native code is slow AND unfavorably billed.

**Conclusion: the K1 native-fused-kernel #1 thesis is FALSIFIED by the live
rules.** Going native is triply penalized (fewer cores, unfavorable wall rate,
design intent). RETIRE the native-kernel path (as Track A was retired). The
lever the organizers reward is FLOPSCOPE-EFFICIENT ALGORITHM DESIGN: lower MSE
per flopscope-FLOP.

## What the live rules confirm

- Score = MSE (final-layer primary) with a budget-adjusted improvement for
  under-budget usage, "capped relative to full-budget usage, so cheap-but-
  inaccurate Solutions cannot dominate" (the max(0.1, C/B) floor cap). Exact
  formula + floor value are in the STARTER KIT (checkable locally).
- 50 submissions/team/day; Phase 2 closes Sep 19; up to 2 nominated
  submissions/phase; private fresh rerun decides prizes; LLM use allowed.
- $150k pool: Phase 2 places $50k/$20k/$10k + a $20k Phase-2 Algorithmic
  Contribution prize. The M178/M179 certified provider is squarely
  Algorithmic-Contribution material.

## The reset direction (to verify, not assume)

The champion is an EXPENSIVE sampler (multiplier ~0.698, 70% of budget). Under
budget-adjusted scoring, a CHEAP estimator hitting the floor (mult 0.1) gets a
10x multiplier discount. So the open question is which wins on ADJUSTED score:
- champion: raw 3.089e-7 x 0.698 = 2.12e-7 (known).
- a cheap analytic closure: raw MSE x 0.1. The EXACT (mu,sigma) oracle caps at
  8.76e-7 (x0.1 = 8.76e-8, would beat champion) BUT the ACHIEVABLE diagonal
  closure at depth 32 is far worse (ARC K2 ~6.28e-5 -> x0.1 = 6.3e-6, loses).
  The M178/M179 EXACT full-covariance closure sits between; its real depth-32
  MSE is UNMEASURED and is the pivotal number.

MEASURE (next): the diagonal closure and the M179 full-cov closure depth-32
final-layer raw MSE vs true-network MC, and their adjusted scores at the floor,
vs the champion 2.12e-7. This decides whether an already-built cheap analytic
estimator is a better SUBMISSION than the expensive champion -- the insight the
native-kernel fixation missed.

## Submission status

BLOCKED: no signed-in AIcrowd session exists (in-app browser "Not signed in";
zero connected Chrome extensions) and credentials cannot be entered. The
champion tar is VERIFIED on disk (sha256 bc2ec395...8ae36). Submission awaits a
live session from the user.
