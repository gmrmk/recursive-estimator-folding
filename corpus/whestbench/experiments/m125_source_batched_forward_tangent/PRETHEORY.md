# M125/M125b forward tangent pretheory

## Verdict: REPAIR

**M125b: PASSED_CARRIER_COMPONENT** -- generated source-agnostic carrier only,
with protected carrier-plus-background bill `12.819347280B`.  This is not a
full-candidate verdict.

The dense forward carrier is exact and generated-source implementable.  The
full M122/M121 candidate is not: exact target-width source-defect construction
still contains the generic fourth-order alternating-path Khatri--Rao node.

Preserve two distinct schedules:

* **M125 oracle:** keep every source identity and propagate its complete
  suffix.  There are `30+...+0=465` affine-plus-ReLU tangent stages.
* **M125b component:** propagate one accumulated tangent and inject the next
  independently constructed source.  It is **IMPLEMENT_COMPONENT** as a
  generated-only carrier: 30 stages and 31 additions, with the same final 256
  means.

No outcome grid, benchmark datum, scorer, champion, or submission belongs in
this directory.

## Frozen interface and delay-one indexing

An M122 source at post-ReLU layer `ell=0,...,30` is transported through the
next affine and converted by M121 at ReLU `k=ell+1`.  M125 consumes the
already-converted post-ReLU defect

```text
s_k=(b_k,B_k),     b_k in R^(1 x n), B_k in Sym_n,
k=1,...,31.
```

If `J_k` maps a post-layer-`k-1` tangent through affine `W_k` and ReLU `k`,
then

```text
final(s_k) = J_31 ... J_(k+1) s_k.
```

The terminal `s_31` has an empty suffix.  Applying `J_k` to `s_k` would
double the one-delay conversion and produce the erroneous 496-stage ledger.
Adding terminal Born duplicates the direct `s_31` response and overlapping
`LLQ/LLLC/LLQQ` source diagrams.  M125/M125b runs alone absent exact
subtraction.

## Complete tangent map

For row-oriented `(u,U)` and weight `W`,

```text
a=uW,              A=W^T U W,
A <- .5*(A+A^T).
```

On the frozen Gaussian preactivation define

```text
p_i=Phi(alpha_i), r_i=phi(alpha_i)/(2 sigma_i),
K_ij=P(X_i>0,X_j>0),
Hmu_ij=E[1{X_i>0}ReLU(X_j)]-p_i m_j,
Hv_ij=.5 f_Xi(0)E[ReLU(X_j)|X_i=0]-r_i m_j.
```

Then

```text
u_i^+ = p_i a_i+r_i A_ii,

U_ij^+ = K_ij A_ij + Hmu_ij a_i+Hmu_ji a_j
                    + Hv_ij A_ii+Hv_ji A_jj,       i!=j,

U_ii^+ = 2m_i(1-p_i)a_i+(p_i-2m_i r_i)A_ii.
```

The full `K` includes connected Price `E`; `Hmu`, `Hv`, and the direct
diagonal are mandatory.  A tangent covariance is signed and must never be
PSD-projected or floored.

For matrix evaluation, set `q=diag(A)`,

```text
Mmu=Hmu.*a[:,None], Mv=Hv.*q[:,None],
U^+=K.*A+(Mmu+Mmu.T)+(Mv+Mv.T),
```

then overwrite the diagonal exactly.  The paired grouping plus the explicit
affine canonicalization produces an exactly symmetric stored matrix.

## Adjoint equivalence and M125b induction

With the Frobenius pairing on `R^n x Sym_n`, for every output basis covector
`e_o` and source `s`,

```text
<e_o, P_mu J s> = <J^* P_mu^* e_o, s>.
```

Thus stacking all 256 forward mean components is exactly the dense all-output
adjoint contraction.  It avoids M120's 256 covectors; it does not approximate
the Gaussian Jacobian.

For M125b,

```text
z_1=s_1,
z_k=J_k z_(k-1)+s_k,  k=2,...,31.
```

Induction gives

```text
z_k=sum_(q=1)^k J_k...J_(q+1)s_q,
```

so `z_31` is the explicit per-source sum.  Ordinary batched GEMMs bill
linearly in batch size and do not save FLOPs.  M125b is cheaper because exact
linearity coalesces active sources before their common suffix.  It retains
final output equality but not individual source diagnostics.

## Installed FlopScope 0.10 ledger

Installed source is authoritative: `data/default_weights.json:476-488` gives
float64 multiplier `2.0`, applied by `_dtype_billing.py`.  The old primer's
same-cost statement is stale.  The measured background bill below is already
dtype-aware.

At `n=256`, one tangent stage has base count

```text
M(1,n,n) + 2M(n,n,n) + 2n^2 + (7n^2+6n)
= 67,699,968,
```

or `135,399,936` installed float64 FLOPs.

| item | raw dtype-billed | after one 1.25 factor |
|---|---:|---:|
| M125 465-stage carrier + final response | 62.960986624B | 78.701233280B |
| audited Gaussian background | 6.189400128B | 7.736750160B |
| **M125 carrier + background** | **69.150386752B** | **86.437983440B** |
| M125b 30-stage carrier + 31 injections | 4.066077696B | 5.082597120B |
| **M125b carrier + background** | **10.255477824B** | **12.819347280B** |

M120's killed complete-reverse matmul/background lower bound was `105.910B`
before its scalar/copy work.  M125's protected carrier number is lower, and
M125b is much lower.

Removing M124's obsolete 16.641B adjoint-pairing row leaves a conditional
projected-source worksheet of `80.667438080B` raw.  With one global margin:

```text
M124-projected + M125  =187.272281040B <258.4B,
M124-projected + M125b =113.653644880B <258.4B.
```

This is not an exact-source certificate.  M124's k3-selected rank four is an
approximation and several rows are reserves/equivalent calls rather than a
native trace.

M123's necessary zero-mean path factor plus residual already costs
`215.417323520B` after protection.  It gives

```text
M123 subset + M125  =301.855306960B >258.4B,
M123 subset + M125b =228.236670800B <258.4B,
```

with only `30.163329200B` left in the second line before all missing nonzero
stars, exact collisions, cores, response, copies, and endpoint-stable kernels.

## Binding source repair

For M122's fourth-order path,

```text
P[a,b,c,d]=sum_yz gamma_y gamma_z
 H[y,a]A[y,b] Q[y,z] A[z,c]H[z,d].
```

Nonalternating repeated-output patterns admit all-pairs `O(n^3)` matrix
identities.  The alternating term

```text
P[i,j,i,j]=sum_yz (gamma_y H[y,i]A[y,j])Q[y,z]
                    (gamma_z A[z,i]H[z,j])
```

has `n^2` Khatri--Rao pair columns and generically costs `O(n^4)`.  M123's
16-orbit audit independently leaves hard orbits 8, 14, and 15.  A rank-four
projection makes the contraction cheap but does not make it exact.

The full mutation remains REPAIR until either this node has an exact sub-`n^4`
identity or a deterministic permutation/gauge-covariant source factor has a
proved contract and complete bill.

## Invariance, conditioning, and generated gates

For row-coordinate permutations and positive gauges,

```text
h'=hP,  V'=P^T V P, W'=P^T W P_next,
h'=hD,  V'=D V D,   W'=D^(-1)W D_next.
```

Tangents/sources transform by the same laws, and both carriers commute with
them.  Floors, correlation clips, and coordinate-selected tied subspaces do
not.  Reject nonfinite/non-SPD backgrounds, tiny variances, and correlations
near singular endpoints.  Preserve signed tangent covariances and deterministic
addition order.

Generated-only gates currently pass:

1. explicit source suffix sum equals M125b for all final mean and covariance
   entries on a Philox width-5, six-source chain;
2. row-oriented affine transport, connected/full Price term, both cross
   blocks, and the direct diagonal match an independently assembled width-2
   reference; and
3. every stored covariance is exactly symmetric after canonicalization.

The carrier-side streamed working set is about 82 MiB with cached weights,
background states, and 31 `K,Hmu,Hv,p,r` sets.  Data copies/stacking are
zero-FLOP but must be present in a future native backend-time/source trace.
