# M130 — direct output-slice repair for the missing `aabc` collision

Date: 2026-08-07.  Scope is generated-array algebra only.  No contest model,
truth, scorer, public/private row, candidate artifact, upload, or submission
was opened or changed.

## Decision

**REPAIR / preserved component; not IMPLEMENT-ready.**

M124 and M126 omitted the exact three-label `[2,1,1]` collision.  That is a
real source omission, rather than an ignorable diagonal: the supplied local
audit measured nontrivial source and transported repeated-slice changes.  This
pass establishes two new, exact facts for the M118 *quadratic jet* of that
collision:

1. the complete twelve-slot `aaab` output slice has an exact `O(n^3)` dense
   matrix formula;
2. the complete `aabb` slice is an exact repeated-pair `O(n^3)` term plus an
   unbiased direct Rademacher contraction whose exhaustive-sign average equals
   the full twelve-slot small-width oracle.

The pass does **not** claim that the quadratic jet is the exact nonzero-mean
three-variable ReLU vertex, that two probes have acceptable variance, or that
the resulting source has adequate final-layer accuracy.  Those are the next
gates.  The repaired component must replace, not add to, any other `[2,1,1]`
source representation; collision and all-distinct ownership remains disjoint.

## 1. Object, scales, and ownership

Let `g(t)=max(t,0)`.  For standardized distinct Gaussian axes
`(A,B,C)` with correlations `x=R_ab`, `y=R_ac`, and `z=R_bc`, M118 derived

```
F(x,y,z) = cum(g(A),g(A),g(B),g(C))
         = (x*y + x*z + y*z)/(4*pi) + O(||(x,y,z)||^3).
```

Write `c=1/(4*pi)`, `Q=R`, `S=Q-I`, and let `W[i,a]` be an affine map from
source coordinates to output coordinates.  On the exact three-label support,
the quadratic source is

```
K[i,i,j,k] = c*(Q[i,j]*Q[i,k] + Q[i,j]*Q[j,k] + Q[i,k]*Q[j,k]),
            i,j,k all distinct,
```

scattered to all twelve permutations of `(i,i,j,k)`.  It is zero whenever a
third equality occurs.  In a physical, non-unit-variance layer one must use
`Q=D^{-1} Sigma D^{-1}` and `W_eff=D W`; equivalently the source has its
factor `s_i^2 s_j s_k`.  This is positive-diagonal ReLU-gauge covariant:
`D -> D G`, `W -> G^{-1}W` leaves `D W` invariant.  A permutation sends
`(Q,W)` to `(PQP^T,PW)` and leaves every output slice unchanged.

The complete fourth-order source is partitioned before transport:

```
K4 = P_all-distinct K4_bulk + P_[4],[31],[22] K4_small + P_[211] K4_aabc.
```

`P_[211] K4_aabc` is this component.  Adding it to a bulk operator that also
contains collisions double counts.  Replacing an old M124/M126 source means
using the same ownership convention throughout the source, tangent carrier,
and response.

## 2. Exact slot multiplicities

For a canonical source multiset `(i,i,j,k)`, `j<k`, the twelve permutations
give the following output-slice accounting.

| slice | source labels feeding output groups | multiplicity |
|---|---|---:|
| `aaab` | `a: i,j,k`, `b:i` | 6 |
| `aaab` | `a:i,i,k`, `b:j` | 3 |
| `aaab` | `a:i,i,j`, `b:k` | 3 |
| `aabb` | `a:i,i`, `b:j,k` | 2 |
| `aabb` | `a:j,k`, `b:i,i` | 2 |
| `aabb` | `a:i,j`, `b:i,k` | 4 |
| `aabb` | `a:i,k`, `b:i,j` | 4 |

Each column sums to twelve.  This is why a single `i,i,j,k` placement cannot
be treated as a symmetric fourth cumulant.

## 3. The exact cubic `aaab` identity

Define Hadamard powers `S2=S*S`, `W2=W*W`, `W3=W2*W`, and

```
P  = Q @ W        A   = S @ W        D   = S @ W2
D2 = S2 @ W       D22 = S2 @ W2.
```

The ordered singleton-pair aggregate for a fixed repeated source label is

```
Vxy = A*A - S2 @ W2
Vxz = S @ (W*P) - D2*W - S @ W2
V   = c*(Vxy + 2*Vxz).
```

The aggregate with the output-side singleton distinguished is

```
Uxy = S @ (W2*P) - S @ W3 - D22*W
Uxz = D*P - S2 @ W3 - D*W
Uyz = S @ (W*D) - D2*W2
U   = c*(Uxy + Uxz + Uyz).
```

Then the exact transported output table is simply

```
K4_aaab = 3 * ((W*V)^T @ W + U^T @ W).                 (M130.1)
```

Every matrix product is ordinary dense `n x n` work, so (M130.1) is
`O(n^3)` storage `O(n^2)`.  It is an algebraic identity for the quadratic
source, not a factorization or fitted compression.

## 4. `aabb`: exact easy part and an honest direct stochastic hard part

The repeated-pair placements are also exact and cubic:

```
K4_aabb,repeated = W2^T @ V + V^T @ W2.                (M130.2)
```

The remaining split-pair term is

```
4*c * sum_(i,j,k distinct)
   [ Sij*Sik + Sij*Sjk + Sik*Sjk ]
   outer(Wi*Wj, Wi*Wk).                                 (M130.3)
```

It is generically a fourth-order output contraction.  M130 does not relabel
that obstruction as exact cubic.  Instead, for a Rademacher vector `z`, it
uses `E[z_r z_s]=delta_rs` to form the three terms of (M130.3).  Shared
`T=S@(z*W)` and `s=S@z` give:

```
XY_raw = ((W*A)^T @ (z*W)) * (s^T@W)[None,:]
XY_bad = (W^T@(z*W)) * (W^T@((S2@z)*W))
XZ_raw = ((W*T)^T@W) * (s^T@W)[None,:]
XZ_bad = (W*(S2@W))^T @ W2
YZ_raw = (W^T@(s*W)) * (W^T@T)
YZ_bad = W2^T @ (W*(S2@W)).
```

Here `*` between output matrices is entrywise.  The exact one-probe
estimator is

```
K4_aabb^(z) = K4_aabb,repeated
  + 4*c*(XY_raw-XY_bad + XZ_raw-XZ_bad + YZ_raw-YZ_bad). (M130.4)
```

`XY_bad` removes `j=k`; `XZ_bad` removes `i=k`; `YZ_bad` removes `i=j`.
Thus no forbidden lower collision enters the `[2,1,1]` support.  This directly
links to M126: M126's probe mechanism is valid for a hard pair table, while
M130 supplies the previously missing three-label source and charges its extra
orientation/collision-removal work explicitly.  A low-rank deflation of `S`
could replace portions of (M130.4) exactly only after a certified residual
factorization and a separately charged residual-probe variance gate; it may
not borrow M126's old four-call ledger.

## 5. Higher vertex terms and certification

The full `F` is a non-polynomial trivariate truncated-Gaussian vertex.  A
future extension may use a fixed Price/Taylor or Chebyshev polynomial

```
F_P(x,y,z)=sum_(r+s+t<=P) c_rst x^r y^s z^t,
```

with `c_rst=c_rts`, standardized first and transported with `D W`.  Each
monomial admits the same excluded-index inclusion/exclusion pattern as
(M130.1); its `aaab` aggregate is still a finite number of Hadamard powers
and dense products.  Its `aabb` split term still needs a probe or certified
factor action.  This is a deterministic low-degree separated *extension
plan*, not a certificate.

Before using degree `P>2`, freeze a weak/strong domain, derivative/interval
Price bound (or interval trivariate quadrature), degree, all coefficients,
and a propagated absolute source-action error budget.  Near singular distinct
triples must fail closed.  Smooth sampled agreement, a fitted polynomial, or
a cancellation in a final score cannot certify the omitted remainder.

## 6. Installed cost accounting

FlopScope's installed schedule bills a square `256x256` float32 GEMM at
`33,488,896` and float64 at twice that, `66,977,792`.  The new code's static
ledger charges, per each of 31 source layers:

| component | square-call equivalents/layer |
|---|---:|
| exact `aaab`, exact repeated `aabb`, and exact forbidden-diagonal corrections | 15 |
| one full `aabb` Rademacher sample | 8 |

It also reserves `30*n^2` scalar/copy operations per layer and multiplies the
whole source subtotal by the one-time 1.25 safety factor.  Result:

| dtype, probes | raw FLOPs | effective FLOPs |
|---|---:|---:|
| f64, 0 (incomplete `aabb`) | 31.206B | 39.007B |
| f64, 2 | 64.427B | 80.533B |
| f32, 2 | 32.244B | 40.305B |

Those are component costs only: they exclude construction/certification of a
full vertex, the source-to-final tangent carrier, response/Edgeworth work,
runtime residual, and any M124/M126 work that is replaced.  In particular,
they are not a legal end-to-end bill and do not establish budget headroom.

## 7. Target-free tests and evidence

Implementation:

* `m130_direct_aabc_collision/m130_direct_aabc_collision.py`
* `m130_direct_aabc_collision/test_m130_direct_aabc_collision.py`

The generated tests pass on 2026-08-07:

1. exact formula (M130.1) versus the independent twelve-slot dense oracle,
   widths 3 through 7;
2. exact repeated-pair part (M130.2) versus its explicit source slots;
3. full dense `aabb` reference versus the twelve-slot oracle;
4. exhaustive `2^4` Rademacher average of (M130.4) versus that exact `aabb`
   reference;
5. hidden permutation and explicit positive-gauge covariance;
6. f32/f64 installed-cost constants.

Command:

```powershell
& 'work\headroom-recursion\.venv\Scripts\python.exe' -m unittest -v `
  'work\scorefloor_generation\m130_direct_aabc_collision\test_m130_direct_aabc_collision.py'
```

All six tests pass.  They test algebra, slots, and accounting on generated
small widths; they do not test contest accuracy or resource use.

## 8. Promotion gates

Promote no component yet.  A subsequent generated-only gate must predeclare:

1. exact/full-vertex or interval-certified polynomial error for `F`, including
   nonzero means and physical scales;
2. probe count or residual factor rank, with variance and cross-layer
   accumulation bound for `aabb`;
3. collision/bulk ownership when composed with M124/M126;
4. source-to-final tangent/response placement and a complete f32/f64 bill;
5. finite-difference and dense small-width tests through the chosen carrier;
6. target-free source-capture/fidelity thresholds before any public split.

The M124/M126 implementations are therefore **repaired in diagnosis**, not
silently approved.  The reusable result is the exact output-aligned quadratic
operator and the falsifiable full-`aabb` probe, which change the failed link
from “unrepresented three-label source” to “vertex remainder and probe
variance must be certified.”
