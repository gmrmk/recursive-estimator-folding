# M125 source-batched forward Gaussian tangent theory -- 2026-08-07

## Decision

**REPAIR** as a complete M122/M121 mutation.

**M125b component verdict: PASSED_CARRIER_COMPONENT.**  This verdict covers
only the source-agnostic generated carrier and its equivalence proof.  It is
not a passed source builder, response-bearing estimator, or full candidate.

The response carrier is not the remaining problem.  An already-constructed
post-ReLU defect `(delta mean, delta central covariance)` can be propagated
exactly, densely, and much more cheaply in the forward direction than M120's
256-objective reverse recurrence.  The complete Price kernel, its connected
`E` part, both mean/covariance cross blocks, and the direct diagonal limits all
fit in an ordinary `n + n^2` tangent state.

There are two carrier schedules:

* **M125**, the requested independently visible source batch, uses 465
  downstream stages and is an exact `O(L^2 n^3)` replacement for the M120
  reverse carrier.
* **M125b**, a mechanism-changing child, uses the exact inhomogeneous tangent
  recurrence.  It needs only 30 stages and 31 source additions, hence
  `O(L n^3)`.  A generated-only implementation and equivalence test are now
  present.  This carrier is **IMPLEMENT_COMPONENT**.

The complete candidate is still not implementable.  M122/M121 does not supply
31 exact target-width defects.  Its generic fourth-order alternating `ABAB`
path produces the same Khatri--Rao `iijj` obstruction already identified in
M121--M123.  M124's shared-k3 rank-four interface is affordable but is a
projected source model, not an exact representation of the M122 source.  The
minimal certified Krylov construction for even the necessary zero-mean path
subset, when attached to the 465-stage M125 carrier, exceeds the 258.4B safety
line.  M125b restores possible budget headroom, but the missing nonzero stars,
collisions, cores, response construction, and exactness certificate have not
been charged into that headroom.

No contest model, public/private datum, outcome grid, scorer, champion, or
submission artifact was read or produced.

## 1. Ownership and the indexing that prevents a double charge

Use 32 post-ReLU Gaussian-closure layers numbered `0,...,31`.  An M122 source
formed at post-ReLU layer `ell`, `ell=0,...,30`, is transported through the
next affine map and converted by the M121 one-delay Edgeworth response at
ReLU `ell+1`.  Its owned interface is therefore

```text
s_k = (b_k, B_k),       k=ell+1 in {1,...,31},
b_k in R^(1 x n),       B_k in Sym_n.
```

`s_k` is inserted **after** ReLU `k`.  It must not be sent through the
Jacobian of ReLU `k` again.  If `J_q` denotes the complete frozen-background
Gaussian affine-plus-ReLU tangent from post layer `q-1` to post layer `q`,
then the final contribution of source `k` is

```text
delta x_31^(k) = J_31 J_30 ... J_(k+1) s_k.                 (1)
```

The product is empty for `k=31`.  Thus the number of downstream stages is

```text
sum_(k=1)^31 (31-k) = 30+29+...+0 = 465.                  (2)
```

Using 496 stages would apply the 31 one-delay source conversions a second
time.  Using only 30 sources would drop the final owned source.

The terminal source `s_31` already is the final ReLU Edgeworth response to
the source transported from layer 30.  Terminal Born owns that same direct
incidence.  Adding terminal Born's `LLQ/LLLC/LLQQ` response to M125 therefore
duplicates at least that term, and the weak-bridge expansions overlap at
earlier sources as well.  M125/M125b must run alone unless a future diagram
ledger gives an exact labelled subtraction.  Connected Gaussian Price `E`
is different: it belongs to each downstream Gaussian Jacobian and is required
for (1); it is not another cumulant source.

All sources are evaluated on the frozen Gaussian background.  Source-source,
`k3^2/H6`, and cumulant-feedback terms remain absent first-Born terms.  That
omission is exactly what makes source addition linear.

## 2. Complete row-oriented local tangent

Let `(u,U)` be a post-ReLU tangent, with `u` a row and `U=U^T` a signed
central-covariance tangent.  For the next weight `W`, row orientation gives

```text
a = u W,
A = W^T U W.                                                (3)
```

`U` and `A` are derivatives and need not be positive semidefinite.

At the following Gaussian preactivation let

```text
sigma_i = sqrt(C_ii),       alpha_i = mu_i/sigma_i,
p_i = Phi(alpha_i),         r_i = phi(alpha_i)/(2 sigma_i),
m_i = E ReLU(X_i),
K_ij = P(X_i>0, X_j>0).
```

The full `K` may be written conceptually as `p p^T + D + E`; using `K`
directly includes both the normal-ordered pair term and connected residual
`E` without separately materialising or charging either one.

For `i != j`, define the exact central-covariance cross blocks

```text
Hmu_ij = E[1{X_i>0} ReLU(X_j)] - p_i m_j,

Hv_ij = .5 f_Xi(0) E[ReLU(X_j) | X_i=0] - r_i m_j.          (4)
```

The forward Jacobian is

```text
u_i^+ = p_i a_i + r_i A_ii,                                 (5)

U_ij^+ = K_ij A_ij
       + Hmu_ij a_i + Hmu_ji a_j
       + Hv_ij A_ii + Hv_ji A_jj,             i != j,       (6)

U_ii^+ = 2 m_i(1-p_i) a_i + (p_i-2m_i r_i) A_ii.            (7)
```

Equation (7) is a direct univariate limit, not a near-diagonal bivariate
substitution.  In matrix form, with `q=diag(A)`,

```text
Mmu = Hmu .* a[:,None],       Mv = Hv .* q[:,None],
U^+ = K.*A + (Mmu+Mmu^T) + (Mv+Mv^T),                       (8)
```

followed by the exact diagonal overwrite (7).  This grouping makes every
off-diagonal pair bit-symmetric.  The two-sided GEMM in (3) is symmetric only
algebraically, so the generated implementation also pays for
`A <- .5*(A+A^T)` before (8).

The M120C analytic formulas evaluate `K,Hmu,Hv` without covariance clipping
or a substituted diagonal.  A target implementation must reuse the quadrant,
conditional-CDF, and joint-density intermediates from the Gaussian background
when building these kernels.  Constructing a separate `E` and then adding it
to `K` would be a double computation.  The old `fullcov.py` trace is a cost
anchor, not an acceptable exact numerical implementation: it floors variances
and clips correlations.

## 3. Equality to the dense all-output adjoint

Put `X=R^n x Sym_n` with pairing

```text
<(b,B),(u,U)> = b u^T + tr(B^T U).                           (9)
```

For source `s_k`, let `F_k=J_31...J_(k+1)` and let `P_mu` project the final
state onto its 256 mean coordinates.  The forward answer is

```text
y^(k) = P_mu F_k s_k.                                       (10)
```

For output basis covector `e_o`, the exact dense reverse answer is

```text
y_o^(k)
 = <e_o, P_mu F_k s_k>
 = <F_k^* P_mu^* e_o, s_k>.                                 (11)
```

Equation (11) is precisely the dense-adjoint contraction.  Stacking it for
all `o=1,...,256` gives (10), including the symmetric-coordinate factor of
two implicit in the Frobenius pairing for off-diagonal storage.  M120 carried
256 output covectors backward.  M125 carries one `n+n^2` directional state
forward for each of 31 sources.  No approximation has been introduced by
changing orientation.

Linearity also gives

```text
delta y = sum_(k=1)^31 P_mu F_k s_k.                         (12)
```

This proof requires the complete blocks (5)--(7).  Price-only propagation or
omitting `Hmu`, `Hv`, or the direct diagonal is not adjoint-equivalent.

## 4. M125b: exact coalescing, not ordinary batching

Define

```text
z_1 = s_1,
z_k = J_k z_(k-1) + s_k,                 k=2,...,31.         (13)
```

Induction gives

```text
z_k = sum_(q=1)^k J_k J_(k-1) ... J_(q+1) s_q.              (14)
```

The base case is immediate.  Applying `J_(k+1)` to (14) and adding
`s_(k+1)` proves the next case.  At `k=31`, (14) is exactly (12).  This is
valid because every `J_k` and every `s_k` is frozen on the unperturbed
Gaussian background.  It introduces no source-source term and preserves the
source ownership table even though it no longer retains 31 diagnostic output
vectors.

An ordinary batch axis does **not** save analytical FLOPs.  For batch size
`b`,

```text
(b,n)@(n,n)       bills b M(1,n,n),
(b,n,n)@(n,n)     bills b M(n,n,n),
(n,n)@(b,n,n)     bills b M(n,n,n),
```

and all elementwise work is multiplied by `b`.  Dynamic identity-preserving
batching therefore retains the 465-stage bill.  M125b is cheaper because it
uses superposition before applying the common linear map; its lower bill is a
real mechanism change, not a backend batching credit.

The generated-only test uses Philox states at width 5, six source insertions,
full signed covariances, arbitrary complete local blocks, and five dense
maps.  It matches explicit per-source suffix propagation for every final mean
and covariance entry.  A second test checks (3), all off-diagonal terms in
(6), and the direct diagonal (7).  Both tests pass.

## 5. Exact carrier FlopScope ledger

For installed FlopScope 0.10.0,

```text
M(a,b,c) = 2abc-ac.
```

The installed billing source, not the stale starter-kit prose, is binding:
`flopscope/data/default_weights.json:476-488` assigns float64 multiplier
`2.0`, and `_dtype_billing.py` applies that multiplier.  The following bills
therefore double every float64 arithmetic count once.  The measured Gaussian
background number is already a native dtype-aware FlopScope bill and is not
doubled again.

At `n=256`, one complete tangent stage has these non-overlapping calls:

| item | exact shape/calls per stage | base operations | installed f64 bill |
|---|---:|---:|---:|
| affine mean | `(1,256)@(256,256)` | 130,816 | 261,632 |
| covariance right map | `(256,256)@(256,256)` | 33,488,896 | 66,977,792 |
| covariance left map | `(256,256)@(256,256)` | 33,488,896 | 66,977,792 |
| exact symmetry canonicalization | one add + one multiply on `(256,256)` | 131,072 | 262,144 |
| ReLU mean and exact diagonal | six vector multiply/add calls | 1,536 | 3,072 |
| ReLU off-diagonal/full matrix | three multiplies + four adds on `(256,256)` | 458,752 | 917,504 |
| **one complete stage** | -- | **67,699,968** | **135,399,936** |

The ReLU rows total `7n^2+6n=460,288` base operations.  Indexing,
transposes, diagonal views, and the diagonal overwrite are zero-FLOP data
operations under FlopScope; their backend time and memory writes are still
real.

### M125: 465 independently visible suffix stages

| carrier item | calls | installed bill |
|---|---:|---:|
| mean affine | 465 `(1,n)@(n,n)` | 0.121658880B |
| covariance affine | 930 square GEMMs | 62.289346560B |
| exact symmetry canonicalization | 465 add/scale pairs | 0.121896960B |
| complete ReLU tangent | 465 | 0.428067840B |
| sum 31 final mean vectors and add background mean | 32 vector adds | 0.000016384B |
| **M125 carrier** | -- | **62.960986624B** |
| audited 32-layer Gaussian background trace | one | **6.189400128B** |
| **raw dtype-billed carrier plus background** | -- | **69.150386752B** |
| **one global 25% protection factor** | -- | **86.437983440B** |

This is `19.472016560B` below M120's killed `105.910B` pre-source lower
bound, even though M125 includes a 25% reserve and M120's number excluded
pointwise derivative construction and copies.  Both are below 258.4B before
source construction; that does not make either one a complete candidate.

### M125b: 30 stages and 31 source additions

| carrier item | calls | installed bill |
|---|---:|---:|
| 30 complete stages | 30 means, 60 square GEMMs, 30 symmetry pairs, 30 ReLUs | 4.061998080B |
| inject 31 `(n+n^2)` defects | 31 covariance adds + 31 mean adds | 0.004079104B |
| add final correction to background mean | one `(256,)` add | 0.000000512B |
| **M125b carrier** | -- | **4.066077696B** |
| audited Gaussian background trace | one | **6.189400128B** |
| **raw dtype-billed carrier plus background** | -- | **10.255477824B** |
| **one global 25% protection factor** | -- | **12.819347280B** |

The implementation can assign `s_1` rather than add it, but the table charges
all 31 insertions as requested.  It is consequently a conservative exact-call
ledger for the implemented recurrence.

### Source-side interface: what is and is not certified

The M124 worksheet can be attached without its obsolete
`dense_defect_cp_pairing=16.641B` row, because M125 consumes the dense defect
directly.  Its remaining raw, already dtype-billed source-side rows are:

| conditional M124 source row | raw bill |
|---|---:|
| k3 factor and eigensolve equivalents | 56.060411904B |
| tree path cores | 11.214520320B |
| nonzero star cores | 0.160000000B |
| collision cores | 6.000000000B |
| one-affine shared-factor transports | 0.032505856B |
| analytic collision source scalars | 4.000000000B |
| one-delay response scalar reserve | 1.600000000B |
| copies/allocation reserve | 1.600000000B |
| **conditional source total** | **80.667438080B** |

With one global margin, this conditional interface gives

```text
M124 + M125  : 1.25*(80.667438080 + 69.150386752)
              = 187.272281040B < 258.4B,

M124 + M125b : 1.25*(80.667438080 + 10.255477824)
              = 113.653644880B < 258.4B.                   (15)
```

These are feasibility worksheets, **not exact-source certificates**.  The
factor/eigensolve row is expressed as 837 square-GEMM equivalents, and the
star, collision, response, and copy rows are reserves rather than a frozen
native call trace.  More importantly, M124 selects a rank-four space from k3;
it has no theorem that this preserves the generic k4 source or its final
response.

The M123 minimal nontrivial rank-four Krylov construction plus a fail-closed
residual costs `215.417323520B` after its own float64 and 25% charges for the
necessary zero-mean path subset alone.  Combining like margins gives

```text
M123 subset + M125  = 301.855306960B > 258.4B,              (16)
M123 subset + M125b = 228.236670800B < 258.4B.              (17)
```

Equation (16) kills the complete 465-stage schedule through the only audited
certified factor-construction route.  Equation (17) leaves
`30.163329200B`, but every nonzero-mean star, exact collision correction,
projected core, one-delay response, copy, and endpoint-stable kernel is a
positive missing charge.  It is a repair window, not a cost certificate.

## 6. The binding source god node

The fourth-order path core from M122 can be written, for a probe `A` and
`H=QA`, as

```text
P[a,b,c,d]
 = sum_yz gamma2_y gamma2_z
   H[y,a] A[y,b] Q[y,z] A[z,c] H[z,d].                      (18)
```

Most repeated-output assignments in `T4(i,i,j,j)`, including adjacent
`AABB` patterns, reorganize into a fixed number of dense matrix products and
therefore all-pairs `O(n^3)` work.  The alternating assignment is

```text
P[i,j,i,j]
 = sum_yz (gamma2_y H[y,i]A[y,j]) Q[y,z]
          (gamma2_z A[z,i]H[z,j]).                          (19)
```

The `n^2` pair columns in (19) are Khatri--Rao columns.  Applying a generic
dense `Q` to all of them is an `(n,n)@(n,n^2)` operation, hence `O(n^4)`.
M123's independent mode-Gram audit found the same boundary: the 144 ordered
path-pair contractions collapse to 16 symmetry orbits, 13 explicit `O(n^3)`
matrix formulas, and hard Khatri--Rao orbits 8, 14, and 15.  No checked
identity removes the generic alternating support.

A rank-four projection reduces the pair bank from `n^2` to `r^2=16`, but a
generic dense M122 source is not exactly rank four.  Therefore the binding god
node is source-side, not response-side:

1. derive an exact all-pairs sub-`n^4` identity for (19), or
2. supply a deterministic, gauge/permutation-covariant factor construction
   with a proved same-source error contract and a complete target bill.

Until one of those exists, the phrase "31 independently owned defects" is an
interface assumption, not a constructed exact object.  Rank-four source
construction remains the sole asymptotic carrier blocker, while endpoint
stability, collision implementation, and diagram ownership remain mandatory
integration gates.

## 7. Permutation and positive-gauge covariance

For a hidden permutation `P_l`, use row-coordinate convention

```text
h_l' = h_l P_l,
m_l' = m_l P_l,
V_l' = P_l^T V_l P_l,
W_(l+1)' = P_l^T W_(l+1) P_(l+1).                           (20)
```

Tangents and sources transform as `u'=uP`, `U'=P^TUP`.  Equations (3)--(8)
then relabel exactly, and (1), (12), and (13) are covariant.  Set the final
`P_31=I` when final output labels are fixed.

For positive diagonal gauges `D_l`,

```text
h_l' = h_l D_l,
m_l' = m_l D_l,
V_l' = D_l V_l D_l,
W_(l+1)' = D_l^(-1) W_(l+1) D_(l+1).                       (21)
```

Again `u'=uD`, `U'=DUD`.  Standardized `alpha`, correlations, quadrant
probabilities, and M122 dimensionless vertices are invariant; physical means,
covariances, and sources acquire their coordinate scales.  Positive ReLU
homogeneity makes every stage commute with (21).  A variance floor,
correlation clip, coordinate-seeded truncation, or singular-subspace tie
selection breaks this exact statement.  A target path must fail closed or
transform the whole degenerate subspace covariantly.

## 8. Conditioning and memory/copy ledger

* The Gaussian background covariance must be finite, exactly symmetric, and
  comfortably positive definite.  Near-zero variance and
  `abs(rho) -> 1` are rejection domains, not invitations to clip.
* A tangent covariance is signed.  Never PSD-project, eigenvalue-floor, or
  correlation-normalize it.
* Use float64 and canonicalize each two-sided covariance product as shown in
  (3).  Check the pre-canonical antisymmetric residual and every finite value.
* Long products can amplify cancellation.  Preserve deterministic layer
  order; do not norm-clip or renormalize a tangent unless an exact gauge
  transformation and inverse restoration are recorded.
* M125b can have stronger cancellation than separately retained sources.
  Its generated equality is numerical, not bitwise.  A target test must compare
  it with explicit superposition under mixed absolute/relative tolerances and
  reject material disagreement.

Data movement is zero FLOPs in FlopScope but consumes backend time.  A
streamed float64 carrier needs three `n x n` matrices (current, next, GEMM/
ReLU scratch), about 1.5 MiB, plus negligible mean buffers.  Useful caches are
approximately:

| live/cache item | float64 memory |
|---|---:|
| 32 weights, if cast and retained | 16.0 MiB |
| 31 post-background `(m,V)` states for source construction | 15.6 MiB |
| 31 sets of `K,Hmu,Hv,p,r` | 46.6 MiB |
| streamed tangent matrices and background scratch | about 3.0 MiB |
| one streamed dense source defect | about 0.50 MiB |
| **carrier-side subtotal** | **about 81.7 MiB** |

Retaining both pre- and post-Gaussian state stacks adds about 16 MiB.  Keeping
all 31 tangent batches instead of streaming adds roughly 46.5 MiB for three
matrix banks and gives no FLOP reduction.  `astype`, cache copies, diagonal
writes, transposes, stacking, and final output assembly charge zero FLOPs but
must appear in a native backend-time trace.  M124's 1.6B copy/allocation row
is a reserve; no exact source-side allocation trace exists, which is another
reason (15) is conditional.

## 9. Required repair before any outcome protocol

1. Keep `m125_forward_tangent.py` as a generated-only carrier component and
   retain its explicit-superposition/M125b equality test.
2. Prefer M125b for any future final-sum integration; retain M125 only as the
   per-source oracle and attribution path.
3. Construct every `s_k` with an exact, endpoint-stable M122/M121 source path,
   or freeze an explicitly approximate projected-source contract.  Do not call
   the latter the exact M122 source.
4. Resolve the alternating `ABAB` Khatri--Rao node or provide a certified
   factor construction.  Charge nonzero stars, all collision strata, cores,
   one-delay response, kernel construction, copies, and residual wall time.
5. Freeze the source/terminal-Born incidence table and prohibit their union
   absent exact subtraction.
6. Obtain a native FlopScope 0.10 trace of the complete source plus M125b path,
   and apply the 25% reserve exactly once.

Until those gates close, no outcome grid is justified.
