# M113 independent theory judge — third focused pre-execution audit

**Date:** 2026-08-07  
**Disposition:** **PASS_TO_FREEZE**  
**Scope:** current source only, focused on the repaired self-swap estimator,
its expectation certificate and revised charge, and the permanent atomic
one-shot claim; prior mathematical/source properties were replayed as
regression checks.  
**Firewall:** no manifest was created, no candidate was run, and no contest
instance, target, scorer, deep forward, M111 evidence, champion artifact,
network, API, or submission path was accessed.

## Verdict

Both blockers from the second audit are repaired:

1. self-pair-swap graphs now use independent edge-occurrence sketches and the
   unbiased finite symmetric estimator
   `(A B^T+B A^T)/2`; and
2. release now has one fixed output directory and one fixed atomic permanent
   claim, so success, worker failure, and concurrent invocation all consume or
   lose the same unique attempt.

The corrected extra contractions are charged. All 33 target-free tests pass
under the exact bundled runtime, and the prior edge-order, orbit, collision,
threshold, gauge, permutation, tail, and metric properties remain green.

This pass authorizes creation of an external frozen-source manifest only. It
is not authorization to execute M113, not a measured survivor, and not a
competition-facing claim.

## Exact audited hashes

| File | SHA-256 |
|---|---|
| `CONFIG.json` | `80a54bf3001716ba7928558b6feb438bd0f26df2a81779a683f1999f9b99c121` |
| `INVENTORY.md` | `6befcefb0651c5fe474f4b51e63315f97ac0a16e81a4387ccb42100ccae37c31` |
| `m113_matrixfree_vertex.py` | `2464ae36c1396f9884340f34778b60eaf86934acaa82ac50ec063f7b0ca28e29` |
| `REFERENCE_AND_PROTOCOL.md` | `8bc4971cf49cc30aee416f5fd0bf0b53e551b84642f45be7304984ccccc432f4` |
| `run_m113_one_shot.py` | `7146f0c009c2c66c82651edddc219a5fcdf313cdfe951bdcda963495312cc62c` |
| `run_target_free_tests.py` | `fa1cbd12fe58bc6b9b9a89d92ec7713f6f6c0139c2fe86c668efb1eb58645cbd` |
| `test_m113_core.py` | `ec72d1550229ce753dc7e0b7731a009fb32da40a4b61915f9e433c5730ca185c` |
| `test_m113_runner.py` | `8ea3a2651f906f5bf83ecb2d8d90ab7441e6169a984ab0cb0fa98971df04a46d` |

Any change to any hash invalidates this disposition and requires another
audit. The future manifest must contain exactly this eight-file inventory.

## 1. Self-swap estimator

For a self-pair-swap graph the exact graph kernel is

\[
K=LPL^T,
\]

where `P=P^T` swaps the `b/c` tensor axes. It is symmetric but generally
indefinite. The repaired `sketch_frame_for_graph` no longer identifies the
`b` and `c` CountSketch frames. Every edge occurrence receives its independent
hash/sign row. Consequently the sketched left and right factors remain
distinct.

`apply_factor_terms` and `materialize_factor_terms` now use

\[
\widehat K_{self}=\frac12(A B^T+B A^T).             \tag{1}
\]

Because ordinary TensorSketch has
`E[A B^T]=LPL^T`, equation (1) is symmetric for every frozen sketch and
unbiased:

\[
E\widehat K_{self}=\frac12(K+K^T)=K.
\]

It counts the one labeled self graph once. A two-member orbit continues to
use `A B^T+B A^T`, with each term representing one of the two labeled graphs.
Thus the old PSD laundering and the possible orbit multiplicity defect are
both absent.

## 2. Independent expectation certificate

The frozen theorem certificate uses only a generated `d=5` Gaussian factor,
weight seed `708`, graph

```text
(u,a,b,c,d,v) = (0,1,1,1,0,0),
```

width `32`, and 4,096 sketch seeds beginning at `113500`. The operational
candidate seed `113032` is outside the bank. The bank averages all sketches;
it does not select a seed, tune a width, inspect a target, or touch the future
`d=12` candidate result.

Observed frozen certificate:

```text
exact symmetry relative error                  1.403820681986597e-16
exact minimum eigenvalue                      -2.193750780655717e-2
deliberately false PSD minimum eigenvalue      2.580597875783238e-4
first independent left/right relative mismatch 1.1247176291920864
4096-sketch mean relative Frobenius error       1.5710387562099117e-2
```

The `0.0157104` mean error is below the frozen `0.08` gate by a factor of
`5.09`. It is also at the natural `N^(-1/2)=1/64=0.015625` scale for 4,096
independent pseudorandom frames. The certificate is an implementation-level
expectation sanity check, not a confidence interval or a replacement for the
analytic CountSketch expectation theorem.

It is not circular in the materialize/action sense. The bank average uses
randomized TensorSketch factors while the comparator uses explicit unsketched
Kronecker factors. As an additional independent audit, I constructed this
graph directly from its correlation monomial

\[
d_{i,2}d_{j,1}d_{k,2}d_{l,1}R_{ik}R_{il}R_{jk}
\]

without `build_single_s4_graph_factors`. Its relative difference from the
unsketched certificate kernel was

```text
5.937698949472921e-16
```

and its independent symmetry error was `1.993750819686856e-17`. This
triangulates direct graph algebra, explicit tensor factors, and randomized
sketch expectation rather than checking one representation against itself.

## 3. Exact revised cost

At `n=256`, `m=32`, and `q=12`, one labeled graph action consists of

```text
(m x n^2) @ (n^2 x q)
(n^2 x m) @ (m x q)
```

and bills

```text
50,331,264 + 49,545,216 = 99,876,480 FLOPs.
```

The degree-3 research ledger contains 10 `S3` and 16 `S4` labeled graphs.
Four `S4` graphs are self-swap and equation (1) requires one additional
transpose graph action for each. Hence

```text
graph-action equivalents per source = 10 + 16 + 4 = 30
one source action                     = 30 * 99,876,480
                                      = 2,996,294,400
two actions over 32 activations       = 2 * 32 * 2,996,294,400
                                      = 191,762,841,600
```

Adding the frozen feature-build estimate and earlier transport ledgers gives

```text
range actions                 191,762,841,600
feature build                  17,448,304,640
covariance transport            2,080,000,000
k4 transport                   16,640,000,000
k3 transport                    8,320,000,000
known subtotal                236,251,146,240
272B nominal headroom          35,748,853,760
```

The source computation, configuration gate, protocol, and tests all reproduce
these integers. This remains a conservative research arithmetic ledger, not a
claim that omitted full-response banks, QR/SVD, residual time, or a deployable
deep recurrence fit in the remaining headroom.

## 4. Atomic permanent one-shot claim

The operational entry point no longer accepts an output directory. It binds
the fixed paths

```text
M113_ONE_SHOT_CLAIM.json
m113_generated_only_one_shot_evidence/
```

inside the hashed source directory. The sequence is:

1. verify the literal token;
2. verify manifest status, theorem/cost passes, exact eight-file hashes, and
   exact Python/NumPy versions;
3. verify the config agrees with the runner's fixed claim, output, and runtime;
4. reject a pre-existing fixed output;
5. atomically create the fixed claim with `O_CREAT|O_EXCL`, recording manifest
   hash, resolved output path, and `started` state;
6. create the fixed output directory and invoke the capability-gated worker.

The claim is never removed or replaced. `O_EXCL` makes concurrent filesystem
creation atomic; the two-thread test produces exactly one winner and one
blocked attempt. A normal synthetic success leaves the claim and blocks a
different destination. A synthetic worker exception writes a durable failure,
leaves the claim, and blocks a second destination. Wrong-token and invalid-
manifest paths do not create a claim. Imports and the entire target-free suite
leave the fixed claim and output absent.

The worker additionally refuses a non-fixed output, a missing global claim,
or a call without the module-owned capability. This is an operational
one-shot firewall, not a defense against deliberately editing frozen source or
deleting artifacts; either action would violate the audited protocol and hash
chain.

## 5. Runtime and regression replay

The current suite was executed with

```text
C:\Users\strid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
Python 3.12.13
NumPy 2.3.5
```

Result:

```text
SUMMARY passed=33 failed=0
```

After the replay:

```text
FROZEN_SOURCE_MANIFEST.json              absent
M113_ONE_SHOT_CLAIM.json                 absent
m113_generated_only_one_shot_evidence/   absent
```

Regression coverage confirms the previously passed properties remain intact:

- correct `b/c` cross-edge ordering;
- complete labeled pair-swap orbits without double counting;
- zero- and nonzero-threshold Hermite coefficients;
- exact dense source agreement, repeated-index collision agreement, and
  symmetry;
- exact-factor and sketched matrix-free action agreement;
- actual fixed-frame hidden permutation covariance;
- standardized positive-gauge invariance;
- deterministic but seed-sensitive sketching;
- exact SVD/Frobenius range metric definitions;
- graph counts and degree-16/18 protocol gates; and
- inert imports, exact manifest inventory, and external-evidence firewall.

## Final disposition

**PASS_TO_FREEZE.** The two second-audit blockers are repaired without
regression. The source may now be frozen by an external manifest containing
the exact hashes above, `theorem_judge: pass`, `cost_judge: pass`, status
`frozen_preexecution_pass_m113`, and runtime
`{"python":"3.12.13","numpy":"2.3.5"}`.

No source, configuration, protocol, or test file may change after that
manifest is created. Execution remains a separate, irreversible one-shot
decision.
