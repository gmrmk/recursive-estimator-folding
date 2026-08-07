# M122 nonzero-mean normal-ordered bridge source

## Scope and verdict

This is a **generated-only algebra/reference component**, not a contest
estimator, source of a score claim, or a permission to run an outcome grid.
It repairs the missing *definition* identified in M121: a signed,
nonzero-mean, central `k3/k4` ReLU source whose collision strata and gauge
law are explicit.  It does not repair M121's separate generic `n^4`
all-output `iijj` contraction.  Therefore the current verdict is
**REPAIR -- preserve the source algebra and its projected implementation;
do not promote it to a target-width component**.

The two useful pieces are deliberately separated:

1. exact local Hermite coefficients and exact collision strata, and
2. a signed pair-resummed, distinct-node tree truncation.

The truncation is a declared source model, rather than an assertion that all
deep-network cumulants are exact.

## 1. Local normal-ordered coefficients

Let `X_i = mu_i + sigma_i G_i`, with `G` standard Gaussian, and write
`alpha_i=mu_i/sigma_i`, `Y_i=(X_i)_+`, `m_i=E Y_i`, and `s_i^2=Var(Y_i)`.
For the probabilists' Hermites,

```
Y_i - m_i = sum_{q>=1} h_i[q]/q! He_q(G_i).
```

Gaussian integration by parts gives the exact coefficients

```
h_i[1] = sigma_i Phi(alpha_i)
h_i[q] = sigma_i phi(alpha_i) (-1)^(q-2) He_(q-2)(alpha_i), q >= 2.
```

The first three are therefore

```
h1 = sigma Phi(alpha)
h2 = sigma phi(alpha)
h3 = -sigma alpha phi(alpha).
```

They are the only local coefficients used by a connected three- or four-node
tree: a `k3` tree has degree profile `(2,1,1)`; a `k4` tree has profiles
`(3,1,1,1)` and `(2,2,1,1)`.  No zero-mean symmetry is assumed; in
particular, the cubic vertex `h3` is nonzero whenever `alpha != 0`.

For exact collision strata we also need coefficients of powers.  Put
`J_r(alpha)=E[(alpha+G)_+^r]`.  With `a=-alpha`,

```
I_0(a)=Phi(alpha), I_1(a)=phi(alpha),
I_k(a)=a^(k-1)phi(a)+(k-1)I_(k-2)(a),
J_r(alpha)=sum_{k=0}^r binom(r,k) alpha^(r-k) I_k(-alpha).
```

For `Y^r = sum_q H_r[q]/q! He_q(G)`, `r=1,...,4`,

```
H_r[q] = sigma^r (r!/(r-q)!) J_(r-q)(alpha),                0 <= q <= r
H_r[q] = sigma^r r! (-1)^(q-r-1) He_(q-r-1)(alpha)phi(alpha), q >= r+1.
```

These formulas include `H_r[0]=E[Y^r]`; hence central cumulants are formed
only *after* the raw moments are assembled.  This prevents the common error
of treating raw moments as connected sources.

## 2. Exact signed pair bridge and exact collision strata

For `|rho_ij|<1`, normal ordering gives the exact bivariate identity

```
E[Y_i^a Y_j^b] = sum_{q>=0} H_a,i[q] H_b,j[q] rho_ij^q / q!.
```

It is a signed series: negative correlations alternate rather than being
clipped.  In particular its `a=b=1` version defines the exact pair bridge

```
Q_ij = Cov(Y_i,Y_j)/(s_i s_j),       Q_ii=1.
```

This is the pair resummation.  It retains all two-node normal-ordered paths,
not only the first `rho` term.  The M120 Plackett formula is an independent
closed-form evaluation of the same `a=b=1` quantity and is an appropriate
future endpoint-stable implementation; the finite reference here uses the
series only away from `|rho|=1` and fails closed when its tail indicator does
not converge.

All collision strata are exact *definitions*, using raw moments followed by
the set-partition cumulant formula.  For one or two distinct labels the
univariate formula above and the signed pair series suffice.  The remaining
`k4` collision type `(2,1,1)` has three distinct labels.  Its exact raw
moment uses the tripartite normal-ordered contraction:

```
E[He_a(G_i) He_b(G_j) He_c(G_k)]
 = a! b! c! rho_ij^r_ij rho_ik^r_ik rho_jk^r_jk
     /(r_ij! r_ik! r_jk!),

r_ij=(a+b-c)/2, r_ik=(a+c-b)/2, r_jk=(b+c-a)/2,
```

when these are nonnegative integers, and zero otherwise.  Thus

```
E[Y_i^2Y_jY_k]
 = sum_{a,b,c>=0} H_2,i[a] H_1,j[b] H_1,k[c]
     rho_ij^r_ij rho_ik^r_ik rho_jk^r_jk
     /(r_ij!r_ik!r_jk!).
```

Together with the partition formula this covers `[3]`, `[2,1]`, `[4]`,
`[3,1]`, `[2,2]`, and `[2,1,1]` without inserting a tree approximation into
a repeated-output entry.  It also retains every centralization and slot
multiplicity automatically.

## 3. Distinct-node bridge trees

Define dimensionless local vertices

```
gamma2_i = h2_i s_i / h1_i^2,
gamma3_i = h3_i s_i^2 / h1_i^3.
```

For distinct `i,j,k`, the pair-resummed `k3` source is

```
S3_ijk = s_i s_j s_k [
  gamma2_i Q_ij Q_ik + gamma2_j Q_ij Q_jk + gamma2_k Q_ik Q_jk].
```

For four distinct indices it is

```
S4_ijkl = s_i s_j s_k s_l [
 sum_a gamma3_a product_(b != a) Q_ab
 + (1/2) sum_(pi in S4)
     gamma2_(pi2) gamma2_(pi3)
     Q_(pi1,pi2) Q_(pi2,pi3) Q_(pi3,pi4) ].
```

The `1/2` removes reversal of each undirected path.  The `S4` star is the
nonzero-mean LLLC family; its zero-mean limit vanishes exactly because
`gamma3=0`.  The path is the LLQQ family.  Expanding `Q_ij` at small
correlation gives `Q_ij=h1_i h1_j rho_ij/(s_i s_j)+O(rho_ij^2)`, so the two
formulas reduce exactly to the degree-`(2,1,1)`, `(3,1,1,1)`, and
`(2,2,1,1)` normal-ordered tree diagrams, including their contraction
multiplicities.

The source is central by construction.  Collision entries are *not* taken by
continuing the distinct formula onto diagonals; they use Section 2.

## 4. Permutation and positive-gauge covariance

For a positive diagonal hidden gauge `D`, `mu'=D mu`, `C'=D C D`, and
`Y'=D Y`.  Therefore `alpha`, `rho`, `Q`, `gamma2`, and `gamma3` are
invariant, while `s'=D s`.  The source obeys exactly

```
S_p' = D^(tensor p) S_p, p=3,4.
```

For a permutation `P`, all quantities simply relabel, giving
`S_p'=P^(tensor p)S_p`.  If the next affine map is transformed as
`W'=D^(-1) W` (and the usual matching permutation is applied), then
`W'^T S_p' W'...=W^T S_p W...`.  These are exact source laws, not a claim
about a later rank truncation.

## 5. Contractions and the remaining obstruction

For a probe matrix `U` with `r` columns, set `A=diag(s)U`, `H=Q A`.  The
projected tree tensor has no width-four storage:

```
T3[a,b,c] = <gamma2,
 A_a H_b H_c + A_b H_a H_c + A_c H_a H_b>.

T4_star[a,b,c,d] = sum_(t=1)^4
 <gamma3, A_t product_(v != t) H_v>.

P[a,b,c,d] = sum_yz gamma2_y gamma2_z
 H_y,a A_y,b Q_yz A_z,c H_z,d,
T4_path = (1/2) sum_(pi in S4) P[pi].
```

This costs `O(n^2 r^2+n r^4)` to build the projected `k4` object after
`H=QA`; it is suitable for a *fixed-rank* all-output adjoint factor and has
no `n^4` state.  The same formulas provide diagonal and repeated probe
contractions without forming `S4`.  Exact collision entries are a separate
support of only `O(n^3)` tuples for `k4` (and `O(n^2)` for `k3`); their
fixed-rank projected correction is consequently `O(n^3 r^4)`, not an
`n^4` width tensor.

There is no claim that a generic full-width `T4_iijj` table can be made
sub-`n^4` from an arbitrary dense `Q`.  Its alternating path contains a
Khatri--Rao Gram.  Thus this source repair is compatible with a low-rank
projected pairing, but it does not resolve M121's target-width full-output
obstruction.  Any future M121 integration must use a frozen, independently
verified adjoint factorization and a complete non-overlapping cost ledger.

## 6. Small generated reference gates

`m122_nonzero_bridge.py` and `test_m122_nonzero_bridge.py` are restricted to
`n<=8` generated Gaussian states.  They test:

1. Hermite coefficients against deterministic Gauss--Hermite integration;
2. signed pair and three-node collision series against deterministic
   Gauss--Hermite reference integrals;
3. central cumulant collision strata against direct set-partition evaluation;
4. permutation and positive-gauge covariance of generated small sources; and
5. equality of the low-rank projected formulas with direct contraction of a
   small dense source.

They contain no scorer, contest model, benchmark weights, outcome grid, or
submission artifact.  Passing them validates algebraic identities and the
reference implementation only; it says nothing about efficacy.
