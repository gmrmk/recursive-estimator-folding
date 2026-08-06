# Canonical latent-factor copula audit

## Decision

**Kill the literal fixed-prior candidate; preserve factor-gauge
canonicalization as a reusable operator.**

The mutation repaired the diagnosed numerical defect.  Two matrices `B` and
`BQ` representing exactly the same latent covariance now give a combined
response discrepancy of `1.68e-26` at 49 nodes and `3.01e-26` at 201 nodes,
down from the parent's `0.19931` and `0.02835`.  The 49-versus-201 discrepancy
also falls from `0.12403` to `0.073855`, passing the frozen `0.10` convergence
gate.

That repair does not recover the missing conditional law.  The 49-node
isolated fidelities are `0.72568` for `k3`, `0.64447` for `k4`, and `0.66364`
combined.  All are below `0.80`; all are also below the q4 parent's respective
`0.73214`, `0.65528`, and `0.67342`.  The converged 201-node reference reaches
only `0.67573` combined.  Canonicalizing the covariance presentation can
remove integration-coordinate noise, but it cannot manufacture signed
higher-order state absent from the moments-through-two copula prior.

One of the 96 frozen cells used the predeclared coordinate-projector fallback
because its rank-two factor had no resolvable sign under the fixed primary
seed sequence.  Its measured permutation/gauge defect remained below
`2.45e-26`, but the explicit zero-fallback gate still fails.  This independently
prevents screening the literal implementation.

No WHest row, target, scorer, package, submission, API, official holdout, or
private instance was read.  Accuracy evaluation used only the parent's six
frozen fresh synthetic cases, after the mechanism and gates were written.

## Exactly one changed mechanism

For every inferred rank-four factor `B`, form

```text
S = B' B = V diag(lambda) V'.
```

Nonzero eigenspaces are ordered by decreasing `lambda`.  A simple left
eigenvector's sign is fixed by the first nonzero projection onto a frozen
permutation-equivariant seed.  An exactly repeated eigenspace is resolved from
its left projector, not from the arbitrary basis returned by `eigh`:

```text
P_lambda h_j = U_lambda (U_lambda' h_j),
```

followed by deterministic double Gram--Schmidt.  The frozen seeds are
coordinate functions that commute with any row permutation: `1`, powers of
`diag(BB')`, the row sums `BB'1`, and fixed products of these.  The canonical
factor is the concatenation of the resolved vectors scaled by
`sqrt(lambda)`, with null columns last.

Consequently, generically,

```text
C(BQ) = C(B),          C(B) C(B)' = B B'
```

for every orthogonal `Q`, including reflections.  Exact repeated spectra and
rank deficiency are covered by deterministic tests.  The rectified-Gaussian
response prior, 49/201 Smolyak nodes, scalar moments, clipping, and
total-cumulance calculus are unchanged.

## Gate ledger

| gate | result | status |
|---|---:|---|
| 49-node right-factor discrepancy | `1.68e-26` | pass |
| 201-node right-factor discrepancy | `3.01e-26` | pass |
| coordinate-permutation discrepancy | `3.59e-27` | pass |
| positive-coordinate-gauge discrepancy | `2.44e-26` | pass |
| 49-versus-201 combined discrepancy | `0.073855` | pass |
| isolated k3 fidelity | `0.72568` | **fail** |
| isolated k4 fidelity | `0.64447` | **fail** |
| isolated combined fidelity | `0.66364` | **fail** |
| isolated material signs | `905/1052 = 0.86027` | pass |
| projector fallbacks | `1/96 cells` | **fail** |
| clipping | `481/1152` | pass |
| deterministic tests | `5/5` | pass |
| arithmetic envelope | `74.566119424 B < 80 B` | pass |

The isolated combined shortfall is `0.13636` absolute against the gate.  Even
the 201-node reference is short by `0.12427`.  More accuracy in the same
four-dimensional integration problem is therefore not the next useful spend.

## Transported totals

| metric | canonical 49 | canonical 201 | zero conditional |
|---|---:|---:|---:|
| standardized k3 fidelity | `0.95979` | `0.96012` | `0.78561` |
| standardized k4 fidelity | `0.92270` | `0.93538` | `0.77265` |
| combined fidelity | `0.93083` | `0.94080` | `0.77549` |
| correction fidelity | `0.97746` | `0.97788` | `0.85000` |
| material signs | `56/57` | `56/57` | `55/57` |

Transport passes.  The candidate is only `0.00047` below q4's total combined
reference and remains above the allowed `0.92130` floor.  This confirms that
total transport is robust, while the desired direct conditional repair is not
present.

## What the inversion teaches

The parent's poor 49-node result mixed two errors: arbitrary grid orientation
and a deficient fixed prior.  Canonicalization separates them:

```text
factor-rotation defect:     0.19931  -> 1.68e-26
49/201 discrepancy:         0.12403  -> 0.07386
49-node isolated combined:  0.56923  -> 0.66364
201-node isolated combined: 0.70341  -> 0.67573
```

The 49-node estimate improves by `0.09441` absolute once its arbitrary frame
is removed, proving the orientation mechanism was real.  Yet the canonical
201-node value remains far below `0.80`, and canonical 49/201 now agree well
enough to localize the remaining error to the response prior/state rather
than the sparse-grid gauge.

This is not a theorem against all copula or biological routing ideas.  It is
a constraint on the next recursion: keep the canonical frame, exact
conditional resummation, and compressed contractions, but change the
observable state or prior.  A useful successor must expose a signed
higher-order quantity; another covariance-only frame or denser grid does not
address the measured failure.

## Arithmetic

Canonicalization charges, for every target cell/layer, the `r x n` by `n x r`
Gram contraction, a conservative `20 r^3` symmetric eigensolve, the factor
rotation, ten projector seeds, and feature formation.  At
`n=256,L=32,cells=16,r=4`:

```text
parent 49-node envelope                     74.426875904 B
canonicalization raw                         0.055697408 B
canonicalization float64 plus 25%             0.139243520 B
-----------------------------------------------------------
combined                                     74.566119424 B
headroom                                      5.433880576 B
```

The cost gate passes with `6.79%` of the 80B ceiling remaining.  No dense
third- or fourth-order cumulant tensor is formed.

## Recursive disposition

Passed and preserved:

- deterministic right-factor canonicalization from eigenspaces/projectors;
- exact covariance preservation within the structural tolerance;
- coordinate-permutation and positive-gauge covariance;
- unchanged exact conditional moments and total-cumulance contraction;
- now-converged 49-node sparse rule;
- strong transported-total/correction fidelity;
- `<80 B` arithmetic envelope.

Failed links:

1. Moments through two plus the fixed clipped rectified-Gaussian copula still
   do not determine isolated conditional `k3/k4` to the required fidelity.
2. The literal primary seed sequence needs one reported pivot fallback on a
   frozen rank-two cell, violating the zero-fallback gate even though measured
   symmetry remains excellent.

Untested:

- a new signed state observable coupled to the preserved canonical frame;
- a non-Gaussian or maximum-entropy prior constrained by such an observable;
- whether the fallback can be eliminated by a predeclared equivariant seed
  construction without using target information.

Artifacts: `PREDECLARED_GATE.md`, `canonical_latent_copula.py`,
`test_canonical_latent_copula.py`, `run_fresh_oracle.py`,
`fresh_results.json`, `audit.json`, `decision.json`, and this report.
