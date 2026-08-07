# M145 second hostile pre-execution audit -- 2026-08-07

## Decision

**REPAIR / INTEGRATION-ONLY -- DO NOT RUN AN EFFICACY SCREEN.**

The repaired M145 packet closes the first audit's proposal-equivariance,
float32-underflow, seed-ownership, and multi-cell-selection failures.  The
spectral proposal, full-mixture weights, and centered whole-frame coefficient
identity are now credible reusable operators.  The packet still does not
cross the pre-execution gate because its isolated sidecar operates on unit QR
frames while the hash-bound Formal-L1 source stores radius-scaled frames, and
because no integrated source constructs the promised pilot surrogate or
proves the complete liveness/cost path.

This disposition is local: M145 is ready to guide an integration
implementation, not ready for an outcome/MSE screen.  No efficacy run,
contest/public/private access, source mutation, submission, designation, or
champion change was performed or authorized here.

## Independent reproduction

The audit independently performed the following non-outcome checks:

| check | result |
|---|---|
| `py_compile` over core, sidecar, crosswalk, two runners, and tests | PASS |
| structural tests discovered by `test_` prefix | **16/16 PASS** in 0.680 s |
| Formal-L1 source hashes and required hook tokens | PASS |
| frozen Formal-L1 tar SHA-256 | `BC2EC39558C76A67B12B587CA4EE70BB1E8921489643D83707E052D086E8AE36` |
| split-Winograd identity | PASS: `3,325,952` billed operations for the 29 declared standard hooks |
| sidecar billed FLOPs | exactly reproduced: `357,099,678` |
| reproduced sidecar residual | `.019723697 s` versus locked `.022555598 s` |
| reproduced setup QR wall | `1.379393 s` versus locked `1.314100 s` |
| reproduced rank / weights | rank 16; `[.94192684, 1.03316307]`; zero bad weights |
| reproduced restoration defect | `8.9406967e-8` |

The locked residual is conservatively larger than this rerun.  Timing
agreement does not validate the integrated Formal-L1 program because the
sidecar never coexisted with its sample-path buffers.

Current repaired-artifact hashes read during this audit:

| artifact | SHA-256 |
|---|---|
| `m145_defensive_acg.py` | `24C63CB7D2C183434283C117F15BE9CD974DADFB3F7279D6707E8B0FD6ED32AB` |
| `m145_flopscope_sidecar.py` | `5016D732632B03EFBE7F92A681D1E93FAB78018B0DCEF9E6CA6A00F5C697056B` |
| `m145_formal_l1_crosswalk.py` | `52054935F2E6C37355B11BA51680932EA2B1670FE7471E662F3E4CD12ABFFA6C` |
| `test_m145_defensive_acg.py` | `A7C5ACC6B139F2C9A34A15571FFC08F6B6DD4A4E591452BA2E43A2098B03596F` |
| `M145_PREEXECUTION_MANIFEST_20260807.json` | `0BA4A44A3E172EDF87C7CEE53C0C75D94A931BBE021D5E27E8F536DB5C212487` |
| `M145_STRUCTURAL_TRACE_20260807.json` | `7FEB7D73FB84413E96532B6A0B5F66ABF3D8A07D39D2F2B527893FBB88EA6605` |

## Gates that now pass

### Spectral covariance and tie fallback: PASS

The coordinate-started block power iteration is gone.  The repaired fitter
forms the full symmetric scatter, selects a separated top-16 spectral
subspace, applies a scalar function to its eigenvalues, and returns the
uniform proposal whenever the selected/unselected boundary is tied within
the frozen float32 tolerance.  Eigenvector signs and rotations inside a fully
retained tied eigenspace cancel in the covariance.

Beyond the shipped generic and exact-tie tests, this audit ran four independent
target-sized `1024 x 256` generated pilots and nontrivial input permutations.
Every fit retained rank 16 and each covariance permutation defect was exactly
`1.1920928955078125e-7`, well inside the declared `2.5e-5` tolerance.
This certifies the proposal-covariance operator, not pathwise equality of an
entire pseudorandom estimator whose base frames must also be transformed.

### Float32 density and full-mixture weight envelope: PASS for the core

For the frozen box `lambda in [.25,1.75]^16`, the closed envelope reproduces

```text
log a_max              81.7482206702
log q_max              80.1387826981
minimum f32 weight      1.5709679873e-35
float32 tiny            1.1754943508e-38
maximum weight          1 / float32(.8)
```

The mixed extreme-box directions independently produced weights
`[1.5709799e-35, 1.2499999, 2.0182240e-4]`.  The implementation evaluates the
full mixture in the log domain and does not substitute the component label.
Thus the first audit's underflow counterexample is repaired.

The production adapter must retain the core's explicit nonfinite,
nonpositive-quadratic, zero-weight, and cap checks.  The current FlopScope
sidecar omits several of those guards and only reports their absence on one
trace; it should not be copied as an unchecked production path.

### Centered complete-frame coefficients: PASS in real arithmetic

For an ordinary mean over `T=126` frames, the frozen coefficients

```text
c_p = (126/4)   * (1 - mean(w))
c_m = (126/122) * w_m
```

expand exactly to `C + mean_m w_m(F_m-C)` in real arithmetic.  Duplicating
each 256-line frame coefficient in the Formal-L1 `[positive, negative]` block
order is correct.  Conditional on an independent pilot and a genuine
conditional-Haar main frame law,

`E_q[w(A) F(R)] = E_Haar[F(R)]` and `E_q[w(A) C] = C`.

The first-moment residual, second-moment residual, four terminal means, and
the downstream tangent are affine/linear in the held sample values, so they
can receive the same coefficient surface.  Pointwise weighting of dependent
frame or Kerdock nodes remains correctly forbidden.

Float32 makes the coefficient sum approximate rather than symbolic; the
shipped worst-surface test allows a `2e-4` frame-sum defect.  This is ordinary
finite-precision bias and must be included in integrated parity, not described
as bit-exact constant ownership.

### Seed ownership and one-cell freeze: PASS

The setup and prediction SeedSequence roots are distinct, all five child
seeds are distinct and replay exactly, pilot/main frames are separated, and
prediction uses independent component, uniform, and ACG children.  The
manifest now exposes one cell only:

`P=1024, r=16, epsilon=.8, 4 pilot frames, 122 main frames`.

There is no remaining rank/pilot grid from which to choose after observing an
outcome.  The adjusted-score gate, rather than raw MSE, is correctly primary.

## Decisive integration failure: radial scale mismatch

The immutable Formal-L1 source at `orthogonal_fold3.py:31` stores

```text
self._gaussian = q.reshape(...) * mean_radius
```

with `mean_radius = rho_256 ~= 15.9843827`.  The sidecar trace instead builds
and transforms an unscaled unit-Q bank.  Its reflector preparation at
`m145_flopscope_sidecar.py:128` uses

```text
v = frame_bank[..., 0, :] - anchor
```

where `anchor` has unit norm.  A Householder transformation preserves norm;
when `frame_bank` is the actual Formal-L1 bank, subtracting a unit anchor from
a radius-`rho` row cannot construct the reflector that maps `rho*q_0` to
`rho*A`.

This audit applied the shipped sidecar operation to an actual radius-scaled
`126 x 256 x 256` bank.  After conditioning:

```text
maximum normalized first-row/anchor defect    0.3486141264
mean first-row/anchor cosine                   0.1259157807
first-row norm range                           [15.9843769, 15.9843884]
```

The same operation with the reflector target changed to `rho * anchor` gave
a maximum directional defect `5.2154e-8`, mean cosine `1.0`, and retained the
correct radius.  This is a narrow repair, but it changes the sidecar source,
trace hash, bill, and restoration test.  Until made, the claimed conditional
frame law is not the law used by the hash-bound Formal-L1 source.

An alternative unit-bank design may scale directions at every sample-path
call, but that changes ownership, arithmetic, memory, and the Formal-L1 hook;
it must be billed rather than inferred.

## Conditional-Haar proof/test mismatch

The shipped conditional-frame tests sign-normalize QR columns using the
diagonal of `R`, which is the standard route to a Haar orthogonal matrix.  The
sidecar runner and Formal-L1 source do not apply that normalization.  Because
the estimator is antipodal row-wise, the unnormalized QR law may be sufficient
on the projective row-frame quotient, but that statement is neither proved nor
tested by the current packet.  The test and traced law are therefore not the
same law.

The integration repair must either:

1. provide a proof and a direct conditional-completion test for the exact
   `fnp.linalg.qr` row-line law used by Formal L1; or
2. sign-normalize the provisional QR frames in both candidate and matched
   comparator, charging the operation and treating it as part of the frozen
   base geometry.

The ACG identity must be established against the exact provisional-frame law,
not an adjacent QR convention.

## Missing Formal-L1 estimator path

The five Formal-L1 source hashes match, and the named hook tokens exist.  That
is a useful stale-source guard.  It is not an implementation.  In particular,
the sidecar receives arbitrary precomputed `y_plus` and `y_minus`; the current
Formal-L1 source never materializes the promised `1024 x 256` per-line
all-output final surrogate before processing main frames.

Formal fold3 materializes pointwise terminal values for kink outputs, reduces
on outputs through means, and supplies dead outputs analytically.  Therefore
`f_surrogate` is currently undefined.  A repair must freeze one of these
before outcome work:

- an exact raw final activation on the 2,048 antipodal pilot paths;
- a completely specified per-line folded surrogate; or
- another all-output pilot statistic with an explicit cost and invariance
  proof.

Any pilot-measurable statistic may legally define `q`, so this does not kill
the probability identity.  It does affect the mechanism, path schedule,
bill, buffers, and claimed hidden-gauge semantics.  If exact raw pilot outputs
are used, the additional final-three-layer products must be included.

The two-stage adapter must also show how pilot activations/regimes survive the
row-blocked workspace being reused for the 122 main frames, how the four pilot
frame contributions defining `C` are retained, and how restoration runs on
every exception path.

## Cost and memory crosswalk: plausible, not certified

The standard first-plus-28 split-Winograd arithmetic is correct: splitting
one row dimension adds one extra right-stack fill, `114,688` operations per
hook and `3,325,952` total.  The six `64,512 x 256` coefficient-product upper
bound of `99,090,432` operations is also a valid simple upper bound for the
two first-layer and four terminal mean surfaces.

The protected `7.715B` effective delta is nevertheless incomplete because:

- the locked sidecar traced unit frames rather than Formal-L1's scaled bank;
- no integrated pilot-surrogate path was billed;
- terminal folded matmul splits and their calls are not enumerated;
- the extra `.050 s` is a reserve, not a native measurement; and
- the `5 MiB` incremental liveness number is a hand crosswalk, not the peak of
  sidecar plus Formal-L1 buffers in one process.

The isolated sidecar process reproduced a peak working set near `300.7 MB`,
while Formal L1 separately measured `474.859 MiB`.  Those peaks cannot be
combined by adding only nominated arrays without an integrated lifetime
trace.  A 20-cycle apply/restore stress test remained numerically small but
did show cumulative bank drift rising from `1.12e-7` to `4.02e-7` and a
representative frame orthogonality defect reaching `1.01e-6`; the deployed
runner should test its full multi-MLP lifetime, not one restore cycle.

Resource headroom remains plausible -- the projected maximum is well below
`258.4B` on the incomplete worksheet -- but it is not yet a certificate.

## Adjusted-score protocol: correct objective, incomplete executable gate

The manifest correctly requires a paired official adjusted-score mean ratio
`<=.80`, upper-90 ratio `<.90`, an upper-90 absolute score below the sealed
M71 proxy, zero failures, and resource limits.  It correctly makes raw MSE
secondary.

Before any efficacy authorization, a separate frozen outcome protocol must
also specify:

- the number and exact seeds/hash of independently generated target-shaped
  networks (at least 20 for a screen);
- the truth-generation accuracy and its independence from candidate fitting;
- the exact comparator/candidate provisional-frame coupling;
- the bootstrap algorithm, replicate count, ratio convention, and handling of
  zero/dead networks;
- subprocess repeats and tail/failure adjudication; and
- an immutable integrated-source hash.

Using the same integer `setup_seed` is not sufficient common-random coupling
because M145 derives provisional frames from a new namespaced child tree.
The matched Formal-L1 comparator should consume exactly the same provisional
pilot/main QR bank with transport disabled, or the protocol must explicitly
model geometry-seed variance.  Otherwise a single setup orientation can be
mistaken for the causal ACG effect.

## Required next gate

M145 may proceed only to **integration implementation and structural tracing**:

1. repair radius-scaled reflection and rerun its anchor/restoration tests;
2. align or prove the exact QR/projective conditional law;
3. freeze and implement the all-output pilot statistic;
4. materialize a hash-bound Formal-L1 descendant with complete coefficient
   hooks, disjoint seed ownership, and exception-safe restoration;
5. run generated, truth-free end-to-end parity, repeat-predict restoration,
   FlopScope, call-count, residual, setup, and peak-working-set traces; and
6. freeze the complete generated-screen manifest listed above.

Only a later independent audit of that integrated artifact can authorize the
single generated efficacy screen.  The present packet is not that artifact.

## Salvage map

- **Preserved component:** full-eigh/tie-fallback covariance, float32 density
  envelope, defensive full-mixture weighting, centered frame coefficients,
  seed tree, one-cell freeze, source-hash guard, and split-bill identity.
- **Failed link:** unit-frame sidecar was asserted to crosswalk directly to a
  radius-scaled Formal-L1 bank.
- **Unresolved integration:** exact provisional QR law, pilot surrogate,
  complete two-stage path, liveness, and common-random comparator.
- **Status language:** repaired mathematical survivor; integration not yet
  implemented; no screened survivor; no validated child; no promotion.
