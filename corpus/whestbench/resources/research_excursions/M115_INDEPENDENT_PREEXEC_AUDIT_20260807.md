# M115 independent source-only preexecution audit — 2026-08-07

## Verdict: REPAIR

Do **not** advance this source state to `PASS_TO_COST_CALIBRATION`, create a
manifest, create cost evidence, claim a run directory, or run the generated
screen.  The exact-control mathematics, fixed protocol, and most fail-closed
runner controls are sound.  Two source-level release blockers remain:

1. The hashed cost-trace schema still accepts arbitrary scalar bills for
   material operations whose shape/dtype/volume are not enforced, including
   QR, the deep forwards, serialization, and several I/O operations.
2. The Decimal/Higham numerical guard establishes special-function agreement
   only on a 513-point grid and a highly structured `W1=I` fixture.  It does
   not certify the actual arbitrary Gram entries that future weights would
   produce, especially near the `-1`/`+1` endpoints.

This is a repair disposition for the frozen implementation, not a rejection of
the projective arc-cosine control family.

## Scope and immutable state

This was a fresh source-only review of the M115 draft, its configuration,
protocol, runner, and target-free tests.  No contest/public/private instance,
target, truth, scorer, leaderboard, champion artifact, network/API, M115
release manifest, actual cost evidence, claim, output, or generated-network
outcome was accessed or created.  The target-free test suite creates only
ephemeral synthetic fixtures in its own temporary directories; none remains
at an M115 release path.

At the end of review all four guarded release paths were absent:

- `m115_projective_arc_nystrom_draft/EXTERNAL_FROZEN_M115_MANIFEST.json`
- `m115_projective_arc_nystrom_draft/EXTERNAL_M115_COST_CALIBRATION.json`
- `m115_projective_arc_nystrom_draft/EXTERNAL_M115_COST_EVIDENCE/`
- sibling `m115_projective_arc_nystrom_one_shot_20260807/`

The current SHA-256 source surface that the future manifest must bind is:

| File | SHA-256 |
|---|---|
| `CONFIG.json` | `941d65ec9524cd7becc4e63e1f676697ac64255b9ce5c682d1ea42b958e33a7c` |
| `INVENTORY.md` | `9e27d438cbe8a16734e4d1fc9f20eaf67f76122ff96817dd6eb7f307a1071b9c` |
| `REFERENCE_AND_PROTOCOL.md` | `c0f30f5e24753449253e997aae549212176bc5b2c8e665030b9774e3608c61a4` |
| `m115_projective_arc_nystrom.py` | `067eeb2bcbc79e5846330e79337a5011d59f236c0fe41d28ce562c4538dfea64` |
| `run_m115_generated_only.py` | `ee884599b8c9c883844d508699356d33c1444415d936181e0f761b1b5ba1ca02` |
| `run_target_free_tests.py` | `d9ff643701a32a9dfc1440c30d7d203fd16d0c3363a0dcc7406f213d3a4f7a63` |
| `test_m115_core.py` | `6f53b25e1ee77efc636db3d890aa39db8598b3eef42ed0181c3e85c547a9bc23` |
| `test_m115_protocol.py` | `5c2a0ea16493b4f38be874555e0de224fd8ede0762bb0dd16e3db5d59297af20` |
| `test_m115_runner.py` | `53e9aa6a8fe0a2daf4106ebddf1001deefe711c711c942d4142a16be4049a4f7` |

The only execution was target-free:

```text
OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=MKL_NUM_THREADS=1
C:\Users\strid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe run_target_free_tests.py
40 tests passed in 4.616 s
```

It verified `Python 3.12.13`, `NumPy 2.3.5`, and the bundled NumPy module path.

## Mathematics and frozen protocol — PASS

### Exact zero mean, orientation, and antipodal treatment

The row-batch implementation uses `x @ W1`; therefore the `i`-th gate normal
is the *column* `a_i=W1[:, i]/||W1[:, i]||`.  With `U` uniform on
`S^(d-1)` and `H_i(U)=[a_i^T U]_+`, the source uses

```text
M_ik = E[H_i(U) H_k(U)] = kappa(a_i^T a_k)/(2d)
kappa(t) = (sqrt(1-t^2) + t(pi-acos(t)))/pi.
```

For every fixed oriented landmark `z_l`, `c_l=H(z_l)` and
`D_l=c_l^T M c_l`, so

```text
E[(H(U)^T c_l)^2] = c_l^T E[H(U)H(U)^T]c_l = D_l,
E[phi_l(U)] = 0,
phi_l(U) = (H(U)^T c_l)^2/D_l - 1.
```

Consequently `psi_l(U)=(phi_l(U)+phi_l(-U))/2` is both exactly conditional
zero-mean and even.  The implementation has the correct `+/-` ReLU products,
and it divides the f64 frame preactivation by the original *column* norms
before forming the control.  No output at a landmark is evaluated.

### Denominators, PSD, and symmetries

`M` is mathematically PSD as `E[HH^T]`; the code also symmetrizes it, restores
the exact diagonal `1/(2d)`, and fail-closes if the eigenvalue audit is below
its relative tolerance.  It rejects zero W1 columns, zero landmark activation
vectors, nonfinite/nonpositive denominators, and excessive compensated-vs-BLAS
denominator disagreement.  It has no denominator floor or landmark resampling.

The Jensen lower certificate is valid for nonnegative `c`:

```text
D_l = E[(c_l^T H(U))^2]
    >= (E[c_l^T H(U)])^2
     = mu_d^2 (sum_i c_li)^2 > 0.
```

Positive first-layer gauge leaves the normalized axes unchanged.  A hidden
permutation permutes axes/moment/activation coordinates together; a coupled
orthogonal input rotation preserves all landmark-axis inner products; and the
antipodal definition is even.  Source tests exercise all four, including
output-permutation equivariance of the cross-fit correction.

### Whole-frame cross-fit and decision rule

The only estimator rows are the 50 complete Haar-frame means
`P_r=mean_b psi(q_rb)` and the corresponding 256-output frame means.  Folds
are exactly `frame_index mod 5`: 40 training frames and 10 held frames.  Each
fold uses uncentered training RMS, centers only the training response, applies
the training-only inverse RMS linearly to *raw* held `P`, and forbids feature
centering, an intercept, held normalization, and ridge changes.  The
hold-out-response mutation test confirms the held prediction is not fitted on
its own response.

All 204 landmark/evaluation seeds are literal, globally distinct, disjoint
from the four weight seeds and two numerical-audit seeds, and are not a
function of a weight seed.  They are correctly described as one deterministic
PRNG realization; ideal-Haar independence remains the theorem's law.

Screen gates are strict: a raw ratio `>=1`, charged geometric or pooled ratio
`>=0.90`, or exact 4^4 bootstrap q90 `>=0.90` kills.  Only a strict pass gets
`OOF_RISK_ONLY`; it authorizes neither a parameter retry nor a champion action.

## Runner, locks, and lifecycle — PASS with a durability caveat

The runner has fixed resolved paths; the CLI accepts only the exact execution
token, not output/manifest/calibration overrides.  Manifest validation requires
the exact nine-file source surface and current hashes, pins the canonical run
identity/path, checks a fixed calibration descriptor, and rejects free
`charged_cost_multiplier` fields.  Runtime validation requires the exact
bundled Python executable, NumPy module path/version, build fingerprint, core
import path, and single-thread BLAS/OMP/MKL environment.

Trace filenames must be plain basenames and resolve directly below the fixed
evidence directory.  Manifest source names are an exact allow-list and must
resolve directly below the source root.  These checks prevent the externally
supplied manifest or evidence descriptors from escaping their allowed paths.

The one-shot path verifies configuration/runtime/manifest/calibration before
`os.mkdir` atomically claims the one canonical directory and before it can
generate a future weight.  It then writes claim, evidence, event/result or
failure, and a terminal ledger through same-directory temporary files, file
`fsync`, and atomic replace.  All four output-free prechecks are completed
before the first deep forward; the bank is rehashed and has a fixed f64 shape
before evaluation.  The failure path attempts both durable failure and terminal
ledger records, while the surviving claim directory remains fail-closed.

Caveat: as the protocol itself acknowledges, neither `mkdir` nor rename is
followed by a directory-metadata flush, so a power/filesystem failure cannot be
claimed universally durable.  That limitation is honestly stated and does not
create a retry path in the normal filesystem model.

## Independent static recomputation — PASS as an inventory, insufficient as a release trace

Using `billed_matmul(m,k,n,f64)=2*(2mkn-mn)`, `d=w=o=256`, `m=128`,
50 frames, 40 training frames/fold, I independently obtain:

| Item | Billed operations / bytes |
|---|---:|
| f64 `A.T @ A` | 66,977,792 |
| f64 landmark activation | 33,488,896 |
| f64 `M @ C` | 33,488,896 |
| one f64 landmark projection | 1,674,444,800 |
| both antipodal projections | 3,348,889,600 |
| f64 W1/frame products (`first_pre`) | 3,348,889,600 |
| f32-to-f64 W1 conversion | 131,072 |
| file-bank copy | 6,553,600 |
| conservative QR allowance | 89,478,486 |
| five ridge/fit/predict allowances | 55,843,840 |
| scalar/special-function allowance | 34,078,720 |
| compensated denominator work | 16,842,752 |
| **incremental total** | **7,034,663,254** |

The memory arithmetic also agrees with source: 2,512,896 B = 2.396484375 MiB
streaming state; four retained `32 x 256 x 256` f32 stacks = 33,554,432 B =
32 MiB; combined resident lower inventory = 36,067,328 B = 34.396484375 MiB.
Each f64 bank is 26,214,400 B = 25 MiB; all four are 104,857,600 B = 100 MiB.
With a conservative 4 KiB/file header allowance the physical upper is
104,873,984 B, and write + hash-read + evaluator-read is 314,621,952 B.
The code correctly calls this file-backed storage and makes no flash/SSD claim;
the later calibration must measure the volume, allocation/copy, I/O, memory,
and wall-time reserves.

### R1 — blocked: material cost traces are not schema-complete

The hash chain is real (manifest hashes calibration; calibration hashes each
trace), and a ratio is recomputed rather than read as a top-level multiplier.
However, `_recompute_shape_billed_flops` returns `None` for `file_io` and
`flopscope_measured_total`.  The generic parser then permits any nonnegative
`billed_flops` scalar and permits an empty `operand_shapes` list.  `dtype` is
also unconstrained for these operation classes.

That applies to required candidate labels for the compensated denominator
certificate, allocations/copies, atomic evidence writes, Haar QR, ridge and
prediction, special functions/scalars, bank flush/hash/evaluator reads.  The
validator checks only their labels and broad op class, not a nonzero bill,
shape/dtype/element count, byte count, serialization payload, or call count.
The base-L1 and equal-cost-L1 traces have still less prescribed material-call
content.  Thus a hash can faithfully bind an incomplete trace, and a scalar
can stand in for QR/forward/serialization/I/O work.  The mandatory-increment
floor covers the f64 W1/frame and two landmark projections but excludes the
other inventory components above.

This fails the required evidence property: the trace schema must not accept a
free scalar or omit materialized dtype/shape/volume costs.  It also leaves the
raw `.npz` serialization and terminal JSON evidence only as the weak condition
`atomic_evidence_write_bytes > 0`, rather than a data-derived reserve.

## Numerical certificate — REPAIR

The target certificate has good components: standard-library `Decimal` at
80 digits, Gauss-Legendre pi, an exact-factorial check of `rho_256`, correct
reduced `asin` series recurrence, a Hadamard/identity denominator reference,
the f32/f64 first-preactivation bridge, and a per-landmark `gamma_256`-style
propagated bound.  The latter rightly retains the computed denominator rather
than replacing/flooring it.

### R2 — blocked: finite-grid agreement is not an arbitrary-input error bound

The elementary-function allowance is justified by comparing the NumPy kernel
with Decimal at only 513 points `j/256`.  An actual W1 Gram matrix can contain
any float64 correlation in `[-1,1]`, including values much closer to the
endpoints than that grid.  Near `-1`, both kernel forms involve cancellation;
agreement between two non-directed floating evaluations is not a bound on
their common error.  The `W1=I`/Hadamard certificate exercises only
correlations 0 and 1.  The synthetic random fixture evaluates the proposed
bound but does not compare its arbitrary correlations/denominators to an
independent high-precision reference.

Therefore the current `3e-14` elementary-function allowance is an empirical
regression threshold, not a certificate that supports the claimed
per-landmark `<=1e-9` mean-drift bound for future generated W1.  The exact
spherical theorem remains valid; the numerical implementation's stated bound
does not yet follow from the source evidence.

## Minimal next step

Make one source-only repair set, without creating release artifacts:

1. Replace generic `file_io`/`flopscope_measured_total` scalar acceptance with
   an exact, per-label schema for candidate, base, and equal-cost traces:
   required dtype, operand/result shapes, calls, derived flop/copy counts,
   byte volumes, nonzero serialization/atomic-write totals, f64/f32 forwards,
   QR, bank write/flush/hash/evaluator reads, three wall samples, and a
   deterministic reserve tied to the actual raw/evidence artifact layouts.
2. Make the numerical guard data-dependent: high-precision (or certified
   interval/directed-rounding) checks at every actual Gram/kernel/denominator
   entry, including endpoint-adjacent cases, and include a hostile near-endpoint
   target-free regression.  A finite Decimal grid may remain a regression test
   but cannot be the certificate.

Then rerun target-free tests under the pinned runtime and request a fresh
independent preexecution audit.  No manifest, calibration, cost evidence, or
generated screen is authorized before that audit returns `PASS_TO_COST_CALIBRATION`.
