# M124 hostile audit: shared k3-selected source projector

## Decision

`KILL` for the M120-linked estimator branch.  `PRESERVE / BLOCKED PENDING M125`
for the independent source-side component.

The decisive external dependency failed before M124's grid was opened: M120C's
frozen one-shot carrier missed its complete-error gates (global `0.084011` vs
`0.05`; worst complete cells `0.1395--0.6300` vs `0.10`).  It would be invalid
to run M124 and then imply that a compressed source fixes a response operator
already falsified on the dense source.  No M124 outcome cell was evaluated.

This does not kill the distinct M125 hypothesis: source-batched forward dense
`(dmu,dC)` tangents may evade the reverse-carrier failure.  M124's grid may be
activated only after that carrier passes independently and is hash-locked.

## What was nevertheless resolved

The mathematically reusable source component is stronger than the initial
dense falsifier:

- nonzero-mean local `gamma2` and `gamma3` vertices are retained;
- exact univariate/bivariate collision cumulants come from a degree-four MGF
  jet around a certified Plackett quadrant scalar;
- the complete collision-corrected k3 mode Gram is evaluated from `O(n^2)`
  sparse defects and `O(n^3)` operations;
- a rank-four eigenspace is used only when its boundary has a strict `2^-36`
  relative gap;
- the exact same-source k3 and k4 projected cores are formed without `G4`;
- standardization, physical-scale restoration, permutation covariance, and
  positive diagonal gauge covariance are explicit; and
- the draft protocol is hash-bearing, generated-only, and execution-inert.

All ten target-free unit tests pass.  The source-only certificate is
`98.8342976B`, after one global 25% protection factor.  This leaves
`53.1657024B` for any non-overlapping M125 carrier.  The legacy M120/M121
complete ledger is `121.6355476B`, retained only as provenance for the killed
branch.

## Why the source component is not promoted

Selection from k3 alone creates no theorem that a rank-four subspace preserves
k4 or its downstream response.  The draft requires `0.80` fidelity for k3 and
k4 separately as well as jointly, and at most `0.50` relative error on the
transported repeated-output k4 slice (`aaaa/aaab/aabb/abbb`, multiplicities
`1/4/6/4`).  These and the `0.50` correction-ratio gate remain genuinely
outcome-bearing.  More importantly,
even passing those gates would validate only compression relative to the
declared bridge-tree source; it would not repair the killed response carrier or
prove agreement with fixed-network cumulants.

The only valid next mutation is carrier-first: independently falsify M125 on
dense sources.  If it survives, this source projector may be attached unchanged
and its predeclared grid frozen at that time, provided M125 costs no more than
`53.1657024B` after non-overlap accounting.  Until then, M124 is a library
component, not a candidate solve.

## Artifact map

- `m124_shared_k3_projector/PRETHEORY.md`: formulas, gates, and cost proof.
- `m124_shared_k3_projector/m124_shared_projector.py`: source algebra.
- `m124_shared_k3_projector/m124_protocol.py`: generated-only draft protocol.
- `m124_shared_k3_projector/run_m124_falsifier.py`: inert runner.
- `m124_shared_k3_projector/DRAFT_MANIFEST.json`: hash-bearing draft state,
  `DRAFT_NOT_FROZEN`, `execution_authorized=false`, `UNOPENED`.
