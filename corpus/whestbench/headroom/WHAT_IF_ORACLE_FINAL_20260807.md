# What-if oracle: mutant-math deployment tree

Status: live decision memo.  Update measured leaves; never retroactively change
their gates.  Probabilities are judgment ranges, not calibrated frequencies.

## Fixed facts

- Immutable validated L1 sampler: adjusted `2.121762464e-7`, zero failures.
- Immutable sealed M71 v3 challenger: projected adjusted about `2.05e-7`;
  engineering-valid but not a newly scored claim.
- Sampling point placement is already near its average-case floor.  A decisive
  raw-error leap must be weight analytic; an engineering mutation can still
  improve the adjusted score by lowering charged compute.
- No upload, submission, designation, or champion replacement is authorized by
  this memo.

## Branch A -- M116b/M116c exact in-place L3

**Question.** Does exact arithmetic compression save more billed compute than
its 32 calls per layer add in residual wall time, without changing prediction?

**Frozen evidence required.** Actual 32-layer trace identity, depth parity,
`<=464 MiB` whole-child peak, wall `<20 s`, residual `<=.170 s`, no failure,
and a permanent one-shot lifecycle.

**Observed M116b leaf.** The permanent B=2,048 one-shot passed exact trace,
numerical parity, finiteness, `186.582 MiB` peak, and `17.716 s` prediction
wall.  It failed only residual: `.610513 s > .170 s`.  At `lambda=1e11` this
adds `61.0513B` flop-equivalents and destroys the arithmetic advantage.  The
identity is consumed and killed; it cannot be retried.

**M116c mutation.** Preserve the exact core and change only B=2,048 to B=4,096,
cutting full matmul calls from 1,024 to 512 while keeping the exact bill
`189.738221568B`.  Workspace rises from `33.6055` to `64.6680 MiB`; it needs a
fresh whole-process peak proof.  The deliberately adverse proportional residual
forecast is `.305257 s`, still above the unchanged `.170 s` gate.  Therefore
M116c is a falsifier, not a presumed rescue; source/release audits must pass
before one new identity may run.

**Current judgment.** M116b is definitively killed.  M116c has low probability
of its full residual pass but high information value: it tests whether residual
is predominantly per-call or pack/fold work.  Even a pass is an engineering
gain, not the order-of-magnitude raw-error mechanism required for leaderboard
rank one.

## Branch B -- M115 projective arc-cosine Nyström control

**Question.** Do continuous, exact-zero first-layer projective ReLU features
retain a stable downstream projection after whole-frame cross-fitting, unlike
the killed sign/nodal/pair controls?

**Frozen evidence required.** Independent source/cost/numerical audit, then one
generated-only four-network run.  Kill on any raw network ratio `>=1`, or any
charged geometric/pooled/bootstrap-q90 ratio `>=.90`.  Ratios `.65-.90` are
mechanism evidence only; a winning path requires `<.65` plus an unchanged
fresh-outer-block repeat.

**If it passes below .65.** Build an independent pilot/main-rotation MUB port;
charge the pilot bases and feature contractions.  Do not cross-fit within one
shared MUB rotation.  This is the fastest plausible raw-variance mutation.

**If it fails.** Preserve the exact projective mean law and numerical/cost
certificate.  Close first-layer learned controls as a family unless a child
changes the observable layer or supplies an analytic coefficient.

**Current judgment.** Low-to-moderate probability after four prior covariance
reversals; high upside if it passes because it is conditionally unbiased.

## Branch C -- M120b normal-ordered central-covariance adjoint

**Question.** Can the dominant finite-width feedback be resummed as exact
separable plus signed diagonal-reset atoms, with only the connected gate
residual omitted, and can a nonduplicated local source be contracted against
that adjoint?

**Known positive edge.** M120 exactly repairs M119's `R=I` diagonal no-go and
changes all-output rank growth from multiplicative to additive, at most 8,192
atoms.  Exploratory generated Price-block evidence gives `E/K=.01957` and one
depth-32 pullback error `.03144`, cosine `.999593`.

**Known negative edge.** The exploratory raw Price diagonal is wrong for
central covariance.  The corrected full reverse needs 215 variable GEMMs,
`99.721B` before background and `105.910B` including it.  It still has no
owned non-Gaussian source; exact propagated `E` is infeasible.

**Required ladder.** (1) 1D and dense small-width complete-Jacobian identity;
(2) frozen generated widths 8/12/16 with global error `<=.05` and every-cell
worst output `<=.10`; (3) target-shape generated actual-adjoint E audit and
native cost/memory trace; (4) one source with an explicit
LLQ/LLLC/LLQQ ownership subtraction; (5) only then a correction bank.

**If all pass.** This is the only current branch with order-of-magnitude raw
error potential.  It becomes the analytic-prize candidate, possibly fused
with an independent exact sampler only after a covariance/error and mediant
analysis proves the fusion is not dilutive.

**If Jacobian or source fails.** Preserve the normal-ordered split as a theorem
and close covariance-adjoint compression.  Do not revive generic Nyström,
ordinary E eigentruncation, or unowned terminal-Born addition.

**Current judgment.** High scientific leverage, low near-term end-to-end pass
probability.  The component is worth executing because its next falsifier is
cheap and decisive.

## Portfolio decision

1. M116b is closed. Execute M116c and M115 only after their independent freeze
   and external-release audits.
2. Execute M120b's target-free component identity regardless of A/B outcomes;
   it cannot contaminate them and is the sole surviving analytic god-node path.
3. Default deployment remains the immutable L1/M71 portfolio if all leaves
   fail.  Failure is evidence: it narrows the honest frontier to near-floor
   sampling plus unpublished/full higher-cumulant mathematics.
4. A public-board score far below the proved sampling floor is not evidence
   that any of these frozen gates should be loosened.
