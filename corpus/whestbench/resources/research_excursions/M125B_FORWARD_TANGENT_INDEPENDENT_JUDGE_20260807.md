# M125b forward-tangent independent judge -- 2026-08-07

## Verdict

**Overall: REPAIR.**

The mathematical carrier is a **PASS**.  For an already-owned post-ReLU
mean/central-covariance defect and already-built exact Gaussian-ReLU
Jacobians, the row-oriented forward tangent is correct, including its
off-diagonal symmetry factors and direct diagonal limits.  The 31 frozen
source suffixes coalesce exactly into one 30-stage inhomogeneous recurrence.

Two stronger claims do not pass:

1. **KILL the claim that `12.819347280B` is an exact installed-FlopScope call
   trace.**  It is a conservative worksheet.  A native FlopScope 0.10.0
   realization bills a missing 512-FLOP diagonal write per stage, while the
   worksheet deliberately charges a nonexistent 31st source addition.  The
   latter overcharge is larger, so the published number remains conservative
   for the tested carrier, but it is not exact under either convention.
2. **REPAIR before treating this as a complete mutation or estimator.**  The
   exact `LocalReluJacobian` builder, exact M122 source builder, fused native
   implementation, allocation/residual trace, and source-ownership contract
   are absent.  In particular, the old full-covariance Gaussian trace is an
   exact cost anchor but uses clipped/floored numerical kernels and does not
   itself certify or expose the exact `H_mu,H_v` arrays consumed here.

No contest datum, scorer, target, champion output, or submission artifact was
read or executed.  Every numerical check below used locally generated Philox
Gaussian arrays.

## Decision table

| claim | decision | independent finding |
|---|---|---|
| affine Gaussian tangent orientation | **PASS** | row mean is `u W`; covariance is `W^T U W` |
| ReLU mean tangent | **PASS** | `p_i a_i + r_i A_ii` |
| off-diagonal central-covariance tangent | **PASS** | Price, both mean blocks, and both variance blocks have the right slots and factors |
| diagonal limits | **PASS** | direct univariate derivatives agree with finite differences; no singular bivariate substitution |
| forward/adjoint equivalence | **PASS** | Frobenius duality against M120 is at roundoff |
| 31 suffixes versus one recurrence | **PASS** | 465 explicit stages equal 30 coalesced stages on a frozen background |
| semantic layer labels | **REPAIR** | generic list lengths are checked, but `s_1..s_31` and `J_2..J_31` labels are not machine-enforced |
| terminal-source ownership | **PASS with prohibition** | `s_31` has an empty suffix; adding terminal Born without an incidence subtraction double counts |
| quoted carrier cost | **REPAIR** | conservative overall, but not an exact native call trace |
| complete M122/M125b mutation | **REPAIR** | exact source construction and native integration remain unresolved |

## 1. Independent local derivation

Let a row-oriented Gaussian state have background mean `mu`, central
covariance `C`, and signed tangent `(u,U)`.  For the next affine map with
weight `W`, differentiation gives

```text
a = u W,
A = W^T U W.
```

`U` and `A` are derivatives; they need only be symmetric, not positive
semidefinite.

At the next ReLU, define

```text
sigma_i^2 = C_ii,             alpha_i = mu_i/sigma_i,
p_i = Phi(alpha_i),           r_i = phi(alpha_i)/(2 sigma_i),
m_i = E[ReLU(X_i)],           K_ij = P(X_i>0,X_j>0).
```

For a Gaussian directional perturbation `(a,A)`, Price differentiation is

```text
delta E[g(X)]
  = E[grad g(X)] . a + (1/2) <E[Hess g(X)], A>_F.
```

Applied to the univariate ReLU mean, this gives

```text
delta m_i = p_i a_i + r_i A_ii.                         (1)
```

For `i != j`, differentiation of
`Cov(ReLU(X_i),ReLU(X_j))` gives

```text
delta V_ij
  = K_ij A_ij
  + Hmu_ij a_i + Hmu_ji a_j
  + Hv_ij A_ii + Hv_ji A_jj,                            (2)

Hmu_ij = E[1{X_i>0} ReLU(X_j)] - p_i m_j,

Hv_ij  = (1/2) f_Xi(0) E[ReLU(X_j) | X_i=0] - r_i m_j.
```

There is no missing factor of two in `K_ij A_ij`: in the symmetric full-matrix
parameterization, the `ij` and `ji` Hessian terms each carry `1/2`, and they
sum to this one term.  Conversely, an adjoint stored with a full Frobenius
pairing must carry the corresponding two-triangle factor.  M120 does so.

The diagonal should not be obtained as a limit of the bivariate formula.
For

```text
s_i = E[ReLU(X_i)^2],     V_ii = s_i - m_i^2,
```

the exact derivatives are

```text
d s_i / d mu_i = 2 m_i,   d s_i / d C_ii = p_i,

delta V_ii
  = 2 m_i (1-p_i) a_i + (p_i - 2 m_i r_i) A_ii.          (3)
```

Equations (1)--(3) are exactly the blocks implemented by
`m125_forward_tangent.py`.  `Hmu * a[:,None]` supplies the `ij` term and its
transpose supplies the `ji` term; `Hv` has the same orientation.  The generic
matrix diagonal is then correctly replaced by (3).

## 2. Generated numerical falsification

The committed generated-only tests passed:

```text
M125 forward-tangent tests:                     2 / 2
M120 analytic/pullback reference tests:        14 / 14
```

An additional eight-case width-4 Philox pass compared the M125 local tangent
against central differences of the M120 exact Gaussian-ReLU moment map:

| central-difference step | worst mean error | worst covariance error |
|---:|---:|---:|
| `2e-4` | `3.03e-10` | `1.529e-8` |
| `1e-4` | `7.53e-11` | `3.821e-9` |
| `5e-5` | `1.92e-11` | `9.542e-10` |

The approximately fourfold covariance-error contraction on each step halving
is the expected second-order central-difference signature.  A complete
affine-plus-ReLU check at step `5e-5` had worst errors `2.967e-11` for the mean
and `7.534e-10` for the covariance.

For random final mean and symmetric-covariance covectors, the identity

```text
<lambda, J delta> = <J* lambda, delta>
```

agreed with M120's dense analytic pullback to `7.77e-16`.  A separate
16-case Philox pass over dimensions 2--5 found worst local mean/covariance
errors `9.31e-10` and `2.85e-9`, and forward/pullback duality error
`1.95e-16`.  These checks include signed, indefinite covariance tangents.

One evidence repair is still worthwhile: M125's own two tests use fabricated
local kernels and restate the block formula.  A durable committed regression
should construct exact Gaussian kernels through M120, finite-difference them,
and test forward/pullback duality.  The independent checks above establish the
result for this judge but are not currently in the M125 test file.

## 3. Source recurrence and indexing

With sources inserted after ReLUs `1,...,31` and frozen tangent maps
`J_2,...,J_31`, the explicit final correction is

```text
sum_(q=1)^31 J_31 J_30 ... J_(q+1) s_q,                    (4)
```

where the suffix is empty for `q=31`.  Its stage count is

```text
30 + 29 + ... + 0 = 465.
```

Define instead

```text
z_1 = s_1,
z_k = J_k z_(k-1) + s_k,       k=2,...,31.                 (5)
```

Induction expands (5) into (4).  The coalesced carrier therefore needs exactly
30 Jacobian applications and 30 actual additions of a new source; `s_1` is an
assignment.  This is exact only because all `J_k` and all sources are frozen on
the same unperturbed Gaussian background.  Recomputing a Jacobian after an
injection would introduce source-source terms and leave the certified
first-Born model.

An instrumented 31-source generated oracle recorded exactly `465`
`tangent_stage` calls for explicit suffix propagation and `30` for the
coalesced recurrence.  An isolated `s_31` took the empty suffix and returned
bit-exactly.  Across five further Philox seeds, the worst explicit/coalesced
differences were `8.88e-16` in the mean and `4.44e-16` in the covariance.

The code's zero-based lists implement the correct suffix:

```text
sources[0]  = s_1,
weights[0], jacobians[0] = J_2,
...
sources[30] = s_31,
weights[29], jacobians[29] = J_31.
```

Its length check proves only `len(sources)=len(maps)+1`; it cannot prove that a
caller supplied these semantic labels.  A complete integration needs a
labelled source/map contract or an explicit assertion generated from layer
indices.  Otherwise a syntactically valid `J_1..J_30` list would silently
apply the wrong suffix.

### Terminal ownership

`s_31` is already the immediate final-ReLU Edgeworth response of the source
transported from post layer 30.  It must not pass through another ReLU
Jacobian.  Terminal Born's `LLQ/LLLC/LLQQ` family owns the same direct final
incidence (with the known zero-mean specializations).  Therefore:

- M125/M125b alone is consistent;
- M125/M125b plus terminal Born is **KILL** unless a labelled diagram ledger
  supplies an exact intersection subtraction;
- the connected Gaussian Price kernel `K` in downstream Jacobians is not a
  second cumulant source and must remain.

The terminal covariance part of `s_31` is also dead if the only requested
output is the final mean.  A production carrier may add only `s_31.mean`, but
that optimization must be frozen in its own native trace rather than mixed
with the generic full-state accounting.

## 4. Installed FlopScope audit

The audited local runtime is:

```text
Python       3.14.4
NumPy        2.4.6
FlopScope    0.10.0 distribution, 0.10.0+np2.4.6 banner
```

`default_weights.json` assigns float64 rate `2.0`, and `_dtype_billing.py`
applies it.  A generated width-256 native microtrace of the complete tangent
stage produced:

| installed operation | calls | billed FLOPs |
|---|---:|---:|
| `matmul` | 3 | `134,217,216` |
| `add` | 7 | `656,384` |
| `multiply` | 8 | `526,336` |
| `diag` extraction | 3 | `0` |
| `fill_diagonal` | 1 | `512` |
| **stage total** | -- | **`135,400,448`** |

The report's `135,399,936` omits `fill_diagonal`.  FlopScope 0.10.0 documents
and traces that write as `n` base operations, hence `2n=512` in float64.
Basic transpose/diagonal views remain zero in this realization.

A full generated native trace of the 30-stage recurrence, 30 actual source
injections, and one final background-mean add produced:

| operation | calls | billed FLOPs |
|---|---:|---:|
| `matmul` | 90 | `4,026,516,480` |
| `add` | 271 | `23,639,552` |
| `multiply` | 240 | `15,790,080` |
| `diag` | 90 | `0` |
| `fill_diagonal` | 30 | `15,360` |
| **actual traced carrier** | -- | **`4,065,961,472`** |

The independent generated target-shape trace of the cited 32-layer Gaussian
background reproduced **exactly**:

```text
6,189,400,128 billed FLOPs.
```

Thus the tested native carrier plus the cost anchor is

```text
raw                         =  4,065,961,472 + 6,189,400,128
                            = 10,255,361,600,

raw times 1.25 reserve      = 12,819,202,000.                (6)
```

The dossier instead charges all 31 source insertions even though `s_1` is an
assignment.  One full float64 `(n+n^2)` insertion costs `131,584`.  Its
worksheet therefore simultaneously:

- undercharges 30 diagonal writes by `15,360`;
- overcharges one source insertion by `131,584`;
- remains conservative for the tested recurrence by `116,224` raw FLOPs, or
  `145,280` after the 1.25 reserve.

That explains why quoted `12,819,347,280` is above (6) despite the missing
operation.  If the report insists on its artificial 31-add convention and
also charges every native operation, the corresponding figure is instead

```text
carrier                     =  4,066,093,056,
carrier + background        = 10,255,493,184,
times 1.25                  = 12,819,366,480.                (7)
```

The 1.25 factor in (6)--(7) is a planning reserve, not an operation emitted by
FlopScope.  It must not be described as an installed billed-FLOP trace.

### Why even the corrected arithmetic is not a complete cost certificate

`m125_forward_tangent.py` imports ordinary NumPy and accepts five already-made
Jacobian blocks.  It is a generated mathematical carrier, not the native
scored implementation that was traced above.  The background anchor computes
Gaussian moments, but its current implementation clips correlations, floors
variances, and does not return the exact endpoint-aware M120 Jacobian contract.
Additional work is needed to form or retain exact `Hmu` and `Hv`; no native
call ledger proves that this assembly is free.  Source construction is also
outside the carrier, and residual wall time/allocation have not been measured
for an integrated process.

Consequently, `12.819...B` is useful headroom arithmetic, not authorization to
claim a deployable 12.819B estimator.

## 5. Binding blockers and disposition

The carrier should be kept.  The following repairs are required before any
complete-candidate or efficacy gate:

1. Build exact endpoint-aware `K,Hmu,Hv` blocks in FlopScope, preferably fused
   with the Gaussian background, and record a native operation trace.
2. Add the labelled `s_1..s_31` / `J_2..J_31` contract and a committed
   M125-versus-M120 finite-difference/duality test.
3. Solve or explicitly approximate the M122 alternating `ABAB/iijj`
   Khatri--Rao source obstruction.  A projected rank-four source is not an
   exact source certificate.
4. Trace the integrated source builder, response construction, carrier,
   allocations, peak memory, and residual time in one generated target-shape
   process.
5. Preserve the terminal-Born exclusion unless an exact diagram-incidence
   subtraction is proved and tested.

**Final adjudication:** `PASSED_CARRIER_COMPONENT`; **REPAIR** the cost claim
and integration; **KILL** any exact-trace claim for `12.819347280B` and any
unsubtracted terminal-Born hybrid.

## 6. Rehashed evidence

| artifact | SHA-256 |
|---|---|
| `m125_forward_tangent.py` | `fbc9fe32357801b22f0313d4043022e81e2764ff3bf4be94f0dfe3ddb3d1ed32` |
| `test_m125_forward_tangent.py` | `1fea02791adb9e29e6913ec3a1e4a4a46ac765c999725c3f128a729a1516643b` |
| M125 `PRETHEORY.md` | `5a6b5b96c74093b5fd90bdd475e86d5aaac68df4770ca807fae41bce33b7ad9c` |
| M125 theory report | `99dea1651ecb6c73f6368b461dfc2bb23864d45b15f06c32f35c83dea393c69e` |
| M125 component report | `4854ec5aa6c3d0b903612534a8555e7b1dbea04e21b47de4b8086808a8e2a6df` |
| M120 analytic dense reference | `f5e34f8ebc8ff2cafad63ccf55101155c802b01a36828bfc03edc820ad4a65f8` |
| M120 analytic reference tests | `09c5d12e7534683cdee907b8d61b21af437678604621bd9f0f7eb7b9d9cf5f1f` |
| full-covariance cost-anchor estimator | `4ad95e6cb5af482331a6a849f9d4d8299d0f06f741514b8204a194b7cabee951` |
| FlopScope initializer | `f49c7b804649223c077505a3380a6fb2baa691e783564be433543fa0ae6f1b06` |
| FlopScope default weights | `9ff1647a0048d2bd23a7a3d76ee0c60bfd3670d03b15ad8bf2b911c2ae19539f` |
| FlopScope dtype billing | `a73a31f495010b462b2053ef4a9881376fcde1d29a2cd488c8adcf9719d46572` |
