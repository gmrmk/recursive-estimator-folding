# M145 third hostile pre-execution audit -- 2026-08-07

## Decision

**REPAIR -- DO NOT EXECUTE AN EFFICACY OR CROSS-REFERENCE CAMPAIGN.**

M145's integration repair is materially better than the prior sidecar: the
stored frames have the right radius, the candidate and comparator share a
bitwise provisional bank, pilot materialization precedes proposal fitting,
and the candidate restores/replays on its locked structural instance.  The
mathematical cross-risk identity is also correct under its stated idealized
assumptions.

It is nevertheless not an executable submission candidate or an auditable
efficacy screen.  The deployed source imports ordinary NumPy, which the
contest sandbox expressly forbids.  In addition, the exact conditional
projective-frame law required by the importance weights is still supported
only by low-order simulations, not a proof, while the new reference protocol
targets a float64 forward computation rather than the float32/flopscope
forward used to bake the contest target.  These are correctness gates, not
small engineering nits.

This audit opened no truth, reference, prediction error, MSE, score, rank,
contest row, submission, or champion state.

## Scope and immutable inputs

- Integrated manifest: `M145_INTEGRATED_PREEXECUTION_MANIFEST_20260807.json`,
  SHA-256 `8b35ae221f4565f340c803daf37884d94acfa0cdfc214aa41fc49eacf211d88f`.
- Cross-reference protocol: `M145_CROSS_REFERENCE_RISK_PROTOCOL_20260807.json`,
  SHA-256 `27f1acd19e7a09b1b1d88fec37569eb24601aa6baee92b16227d4b2cbce250eb`.
- Cross-reference derivation: `M145_CROSS_REFERENCE_RISK_DERIVATION_20260807.md`,
  SHA-256 `bfae8a2a31c5e65b1f4380e4d864ddf55d3b4494abeb8a5c6271a752ecf257f3`.
- Formal-L1 remains hash-bound to the declared tar SHA-256
  `bc2ec39558c76a67b12b587ca4ee70bb1e8921489643d83707e052d086e8ae36`.

All 15 entries in `M145_INTEGRATED_HASHES.sha256` and every artifact bound by
the integrated manifest reproduced exactly.  The existing formal-source
crosswalk test also passed.  Hash agreement validates provenance; it does not
turn a restricted-import source or an unproved sampling law into a deployable
one.

## Independent structural reproduction

Using the available starter-kit virtual environment, I ran `py_compile` over
the eight M145 core/runner/test modules and directly invoked every `test_*`
function in both test files.  Result: **32/32 pass**.  This was a structural
run only.  It imported FlopScope `0.8.0rc5+np2.4.6`, whereas the locked native
trace declares `0.10.0+np2.4.6`; therefore it confirms Python-level invariants
and artifact consistency, not binary/runtime equivalence to the trace or to
the official runner.

The locked trace itself supports these narrow facts:

| property | candidate | comparator |
|---|---:|---:|
| first-predict billed FLOPs | 184,270,895,262 | 176,455,830,878 |
| first-predict residual seconds | 0.140116 | 0.121654 |
| first-predict operational peak working set | 481.977 MiB | 448.523 MiB |
| first restore defect | 0 | 0 |
| candidate second-predict hash | bitwise identical | intentionally not run |

The code genuinely multiplies the raw-QR bank by `rho_256` in setup and builds
each Householder vector as `rho*q0-rho*anchor`; this fixes the second audit's
unit/radius mismatch.  The proposal is frozen after the 1024-line pilot
surrogate and before the main reflectors are applied.  The centered coefficient
identity is algebraically sound provided the conditional frame law below is
valid.

## Blocking finding A -- ordinary NumPy makes the candidate non-deployable

The candidate import graph contains ordinary NumPy at module import time:

- `m145_integrated_estimator.py:20`: `import numpy as np`;
- `m145_defensive_acg.py:20`: `import numpy as np`;
- `m145_flopscope_sidecar.py:15`: `import numpy as np`.

The first imports the second and third, so these are not test-only helpers
outside the deployed import graph.  The official starter-kit FAQ says plainly:
`plain import numpy is not available in the grader sandbox`; only
`flopscope.numpy` is available for array math.  The current artifact will
therefore fail during import before `setup()` or `predict()`.

**Required repair:** split development/reference helpers from a deployment
module, remove all direct NumPy imports and NumPy type annotations from the
deployment transitive closure, replace needed constants/operations with
`flopscope.numpy` and standard-library `math`, package the complete source,
and run the official restricted-import validator.  Do not use a host NumPy
install as evidence that this is acceptable.

## Blocking finding B -- conditional raw-QR projective law is not proved

The candidate intentionally uses raw `fnp.linalg.qr` output with no diagonal-R
sign normalization, then conditions a full row frame by a right Householder
map.  Its weights assume

`E[ w(A) F(frame) | pilot ] = E_Haar[F(frame)]`.

For that statement, it is not enough that a row has the correct second and
fourth coordinate moments.  The test at
`test_m145_integrated.py:83-104` uses a width-8, 4096-frame simulation and
checks only coordinate squares/fourths and a conditional squared-coordinate
moment.  It does not establish the complete conditional distribution of the
remaining 255 rows given the anchored first row for the exact QR convention
used at width 256.

Antipodal pairing removes a global row sign.  It does *not* automatically make
an arbitrary raw-QR sign convention harmless for all fixed, weight-aligned,
even ReLU integrands.  The exact missing statement is either:

1. a proof that the raw QR convention's row-line frame is Haar on the needed
   projective Stiefel quotient and that the Householder map preserves the
   conditional completion law; or
2. a deployment-wide, billed construction of sign-correct Haar frames and a
   new trace/cost/memory audit.

The audit's own low-dimensional diagnostic found that raw NumPy QR has oriented
row bias (for example, the first row's first coordinate has a large negative
mean); its sign-invariant marginal moments looked Haar-like.  That is useful
evidence for the projective hypothesis, but is not the missing full conditional
law.  It cannot carry an importance-sampling correctness claim by itself.

## Protected compute/memory cliff -- promising but not certified

The reported first-predict point leaves about 26.33B effective operations
below the declared 258.4B safety line.  That is an encouraging *one-network*
measurement, not a worst-case certificate:

- ReLU regime counts after transport can change the dynamically shaped Formal
  calls, so Formal-L1's historical max plus one measured M145 delta is not a
  deterministic upper bound for M145.
- Candidate trace has 701 predict-time matmul calls, while the report's 1,078
  number includes other accounting contexts; the distinction must be made
  explicit in deployed cost records.
- The trace's first-predict peak is below 512 MiB, but its process peak after
  all verification reaches 609.797 MiB.  The latter is diagnostic contamination
  from repeat/reference checks, not proof of contest failure, but it shows that
  a fresh official-lifecycle peak test is still mandatory.
- The test/runtime version used here differs from the native trace version.

**Required repair:** after the import and law repair, conduct a no-outcome,
fresh-subprocess, target-runtime campaign over the frozen generated networks,
recording only failures, billed calls, residual, and peak memory.  A static
shape-based worst-case bill (or a conservative gate-independent upper bound)
is preferred because the over-budget failure cliff is severe.

## Cross-reference risk protocol

### What passes mathematically

For fixed `W,A` and independent conditionally unbiased references
`R1=I+e1`, `R2=I+e2`,

`E[(A-R1).(A-R2)/256 | W,A] = ||A-I||^2/256`.

The derivation expands correctly, and common `R1,R2` cancel the `R1.R2` term
from the candidate-minus-comparator difference.  Fresh Haar rotations formed
by Gaussian QR **with diagonal-R sign correction** do have the intended Haar
law.  The 384 frozen rotation seeds are unique, their table hash verifies, and
the 103,903,848,824,832-operation offline lower-bound arithmetic is correct.
Eight independent pairs per each of 24 networks is statistically interpretable
as a paired *screen* if every replicate is retained and the stated hierarchical
bootstrap is used.  It is not evidence of private-suite winning performance;
the 24 generated networks remain the outer experimental units.

### Blocking finding C -- numerical target mismatch

The protocol defines references by float64 forward propagation of float32
weights.  The documented official truth generator propagates float32 inputs
and float32 weights through FlopScope `matmul`/ReLU.  Thus the current proof is
for `I_float64(W)`, while the screen needs an estimate of the actual official
float32 target `I_float32(W)`.  The two may be close, but closeness is not a
proof at the intended 1e-7 scale.

The current `2e-11` agreement gate compares two float64 direct evaluators, so
it cannot detect this target mismatch.

**Required repair:** predeclare and implement a direct reference evaluator
whose forward operation/dtype semantics match the official float32 target,
with float64 used only for accumulation if appropriate.  Then make an
independent implementation compare float32 target outputs against the official
local ground-truth primitive on a small, non-efficacy numerical fixture.  If a
float64 surrogate remains desired, it must have a separately bounded
`I_float64-I_float32` bias that is negligible relative to every decision gate.

### Further cross-reference repairs

1. Bind an executable network-generator source/runtime hash, not only prose
   stating PCG64/He generation inherited from the sealed protocol.
2. Bind the planned direct reference code and its input/output/hash-sealing
   firewall before any reference vectors are generated.
3. Keep the pair-level bootstrap, negative estimates, and nonpositive
   denominator fail-closed rule exactly as frozen.  Do not add references or
   retune after seeing a result.
4. Do a truth-free throughput/storage/numerical dry run before any authorized
   cross-risk campaign; 103.9T dense operations is substantial even offline.

## What-if disposition

| branch | condition | consequence | no-regret action |
|---|---|---|---|
| best | restricted-import rewrite, exact projective law, and target-matched references all pass | M145 becomes eligible for a newly frozen efficacy descendant | preserve the existing coupling/restore design; re-audit from source hash |
| likely | import rewrite passes but projective law is unresolved | estimator can be structurally valid but has unquantified importance bias | use sign-correct billed Haar or prove the quotient law before screening |
| worst | source is packaged as-is | sandbox import failure zeroes all predictions | do not package or execute it |
| contrarian | raw QR projective law is exact, but ACG adds no variance reduction | an honest screen fails efficacy without invalidating the sampling algebra | retain radius/pilot/cross-risk components; kill only the fixed M145 operator |
| second order | cross-risk references are precise but target-mismatched | a false development win directs later recursion incorrectly | make target semantics a precondition, not a post-hoc correction |

## Recursive-folding salvage map

- **Preserved components:** radius-scaled reflector, pilot-first all-output
  surrogate, separated seed tree, centered complete-frame coefficient algebra,
  same-bank comparator, canonical restoration, and common-reference
  cross-risk identity.
- **Failed link:** deployment closure imports forbidden NumPy.
- **Unresolved link:** exact raw-QR conditional projective frame law.
- **Newly exposed link:** reference numerical target must match official
  float32 forward semantics.
- **Disposition:** M145 is an **unresolved repaired implementation**, not a
  screened survivor, validated child, promotion, rank, or champion.

No existing champion is altered by this audit.
