# M121 bridge-source normal-adjoint theory and cost audit — 2026-08-07

## Verdict: REPAIR

M121 contains a valid, useful *interface theorem*: given a finite symmetric
local k3/k4 source at hidden ReLU ell, its one-affine-map, one-next-ReLU
first-Edgeworth conversion to a central mean/covariance defect is exact to
first order. That defect can then be paired with the M120 all-output
mean/covariance adjoint without a generic output-by-width-four state.

It is **not implementable from the stated M85 rank-4 component**. M85 has no
nonzero-mean local source, its target-width rank-4 factor is obtained only by
dense HOSVD of an order-four tensor, and the M85 terminal family overlaps the
terminal Born LLQ/LLQQ diagrams. Its reported 0.580B is not a per-layer source
cost. No manifest, grid, source implementation, numerical outcome, public or
official data, scorer, champion, or submission was created or used here.

## Frozen inputs

| Subject | SHA-256 |
|---|---|
| M121 PRETHEORY.md | 2d20dd013666cf90fb0d320b98755924c237d75fff56dff3ab323d77e776bd75 |
| M120 normal-ordered theory audit | ec681ad77d518054b6ae08164ca390f58caa18f92be37083a54519d1b1566dd4 |
| M85 source | f7d486a9d35dd29c2ce3bf5cce8e9c9975ba36495ac862b627732b5c6db4a466 |
| M85 frozen runner | aac9651835512d985440499d4cff84f02b354a471b8ba080285f6c47d1f9e0fb |
| M85 tests | 680ede16c67d7807057b1a3059c61dfb9409328a7a157d96a5d30ecb743cea35 |
| M85 derivation | 37a599a2177341203acd92e3e1fefff2330037cf0400dfb608431245a3f6110c |
| M85 report | 264c2da9a5ec0151da4f4ac7d7b6fcd8d1970dd5d5a86dc8db1926aca53792cf |
| M85 independent judge | 5c048f6b9c44133575f0a38f530084ebc9e32b6ff57e8572845cdd44e42412de |
| M85 gates | 433c9008611645009ca2b861d75193fab00993815c930d0f96928d1f9bc2ccac |
| M85 results snapshot | 9a4a1f60f25dcaeaf071570fcba7ef7875f8b5bd492e807fc51d9b8a1df4596d |
| M85 hash inventory | 6026eee681c066b6794c6ea35823e5d64fe29cfe304f0c12f6018b18721fc019 |
| M85 multiplicity audit | 39a1f80263f6bd580e26c51302b27c62535c1c4e1accbd2441596d90d249abfe |
| terminal Born report | 9ff6d7d610f362952d190118a3d319b18f4c089f187923380e840e1947fa0584 |

The M85 hash inventory still agrees with each of its seven listed source/result
files. The independent judge's target-width factor-construction objection is
therefore a current source fact, not a stale comparison.

## 1. Exact one-delay Edgeworth interface

Use column-vector notation for this derivation. Let the Gaussian background at
the source layer be h_ell, let S3 and S4 be its supplied connected central
cumulants, and let

    z = W^T h_ell,       z ~ N(mu, C) on the background.

The one affine map transports the supplied source exactly:

    T3_abc = sum_ijk W_ia W_jb W_kc S3_ijk,
    T4_abcd = sum_ijkl W_ia W_jb W_kc W_ld S4_ijkl.

For a first-Born Edgeworth perturbation, with all k3^2 and source-source terms
excluded, integration by parts gives

    delta E[f(z)] =
        (1/6)  T3_abc E_G[partial_abc f(z)]
      + (1/24) T4_abcd E_G[partial_abcd f(z)].

Thus the sign is positive in normal-ordered derivative form. The negative skew
coefficient in the usual scalar ReLU formula comes from the distributional
third derivative of ReLU, not from a changed Edgeworth sign.

Write v_i=C_ii, sigma_i=sqrt(v_i), alpha_i=mu_i/sigma_i, and

    f_i = density of z_i at zero = phi(alpha_i)/sigma_i,
    f_i' = (mu_i/v_i) f_i,
    f_i'' = ((mu_i^2/v_i^2)-1/v_i) f_i.

The immediate mean defect is exactly

    delta m_i =
      -(T3_iii/6) f_i'
      +(T4_iiii/24) f_i''

    = sigma_i phi(alpha_i) [
        -(T3_iii/sigma_i^3) alpha_i/6
        +(T4_iiii/sigma_i^4) (alpha_i^2-1)/24 ].

This agrees with M85's scalar Gram--Charlier expression when the supplied
source is its diagonal transport. It is an exact conversion of that source,
not evidence that the M85 bridge-tree source is an exact joint cumulant.

### Off-diagonal central covariance, including symmetric slots

For i != j define D_ab^(ij) = E_G[rho^(a)(z_i) rho^(b)(z_j)], with
rho(x)=max(x,0). Only a+b=3 or 4 is needed. Let

    s_j|i^2 = v_j-C_ij^2/v_i,
    u_j|i = mu_j-C_ij mu_i/v_i,
    a_j|i = u_j|i/s_j|i,
    P_j|i = Phi(a_j|i),
    R_j|i = s_j|i phi(a_j|i)+u_j|i Phi(a_j|i),
    beta_j|i = C_ij/v_i.

At conditioning value z_i=0, the needed coefficients are

    D30 = -(f_i' R_j|i + f_i beta_j|i P_j|i)
    D21 =  f_i P_j|i
    D12 =  f_j P_i|j
    D03 = -(f_j' R_i|j + f_j beta_i|j P_i|j)

    D40 = f_i'' R_j|i + 2 f_i' beta_j|i P_j|i
          + f_i beta_j|i^2 phi(a_j|i)/s_j|i
    D31 = -(f_i' P_j|i + f_i beta_j|i phi(a_j|i)/s_j|i)
    D22 = density_2((0,0); mu_{ij}, C_{ij})
    D13 = D31 with i and j exchanged
    D04 = D40 with i and j exchanged.

These follow directly from rho'=1{x>0}, rho''=delta,
rho'''=delta', and rho''''=delta''. For example D30 is
minus the derivative at zero of f_{z_i}(x) E[rho(z_j)|z_i=x].

The raw second-moment defect has all symmetric tensor-slot multiplicities:

    delta R_ij =
      (1/6) [
        T3_iii D30 + 3 T3_iij D21
        + 3 T3_ijj D12 + T3_jjj D03
      ]
      +(1/24) [
        T4_iiii D40 + 4 T4_iiij D31 + 6 T4_iijj D22
        + 4 T4_ijjj D13 + T4_jjjj D04
      ].

The central-covariance defect is then

    delta V_ij = delta R_ij - m_j delta m_i - m_i delta m_j.

For the diagonal, rho(x)^2 has derivatives 2rho, 2rho', 2delta,
and 2delta'. Therefore

    delta R_ii = (T3_iii/3) f_i - (T4_iiii/12) f_i',
    delta V_ii = delta R_ii - 2 m_i delta m_i.

There is no extra hidden factor of two in these formulas. In the subsequent
M120 symmetric-matrix pairing it must be used once as

    <A,delta V> = sum_i A_ii delta V_ii
                  + 2 sum_{i<j} A_ij delta V_ij.

The factors 3, 3 and 4, 6, 4 above count Edgeworth tensor slots; the final
factor two counts the two off-diagonal covariance entries. Conflating them
would double count.

## 2. A factorized contraction exists only after a valid source factor exists

If a symmetric Tucker factorization is genuinely supplied,

    S3 = C3 x_1 U3 x_2 U3 x_3 U3,
    S4 = C4 x_1 U4 x_2 U4 x_3 U4 x_4 U4,

then F3=W^T U3 and F4=W^T U4 give the transported sources. (M85 actually
constructs the order-three and order-four HOSVD factors separately.) The only
entries required by the one-delay response are T3_iii, T3_iij, T3_ijj and
their order-four counterparts T4_iiii, T4_iiij, T4_iijj, T4_ijjj, T4_jjjj.

They can be formed without n^4 storage:

    M3_i,r = C3_pqr F3_i,p F3_i,q,
    T3_iij = (M3 F3^T)_ij,

and, with Q_i,pq=F4_i,p F4_i,q,

    M4_i,s = C4_pqrs F4_i,p F4_i,q F4_i,r,
    T4_iiij = (M4 F4^T)_ij,
    T4_iijj = (Q C4_(2,2) Q^T)_ij.

Symmetry supplies the exchanged patterns. The work after F is
O(n r^3+n^2 r+n r^4+n^2 r^2), plus dense bivariate Gaussian coefficient
matrices. For frozen r=4 this is not an n^4 object. Pairing a dense delta V
with M120's shared CP all-output adjoint also needs only

    q_s = (U^A_s)^T delta V U^A_s,
    Delta J_o = B_:o^T delta m + sum_s G_o,s q_s,

where U^A,G are the M120 covariance-adjoint factors rather than the M85
source factors. A straightforward implementation costs one delta V by U^A
matmul at each
layer, not one dense covariance pullback per output.

This conditional result does **not** make the stated M85 source usable.
M85's actual hosvd_shared first materialises S4 with n^4 entries and performs
an SVD of its mode unfolding. At n=256 that is 4,294,967,296 float64 entries
(32 GiB before work space); even the stated Gram route is about 2.199e12 raw
multiply-adds. No nonmaterialising, permutation/gauge-controlled construction
of the rank-4 U and C4 appears in M85.

For the uncompressed bridge-tree source, k3 all-pair repeated contractions can
be reorganized with QW and Hadamard products in O(n^3). The k4 alternating
path T4_iijj contains the generic Khatri--Rao Gram

    sum_bc Q_bc (QW)_b,i W_c,i W_b,j (QW)_c,j.

For arbitrary dense bridge Q and W this is an n^2-by-n Khatri--Rao product;
ordinary dense contraction is n^4. M85 supplies neither a factorization nor a
proof eliminating that term. Consequently an exact n^4-free *uncompressed*
M121 contraction is unavailable from the checked source. A new
nonmaterialising factor-construction theorem, not a rank assertion, is the
repair gate.

## 3. Target arithmetic: 0.580B is not per source layer

Actual M85 target_bill(rank=4) has n=256 and layers=32:

| Charged item in the M85 function | Raw FLOPs |
|---|---:|
| rank-4 k3 symmetric core queries | 15,728,640 |
| rank-4 k4 symmetric core queries | 165,150,720 |
| one Gram/bridge setup | 34,865,152 |
| two rank-4 affine transports through all 31 maps | 16,252,928 |
| total raw | 231,997,440 |
| float64-times-two and 25% charged total | 579,993,600 |

The last row is the reported 0.580B. Its 16,252,928 transport term is already
2 * 31 * 4 * 256^2: two source orders through **all 31** affine maps. It is
not one one-map source charge, and multiplying 0.580B by 31 counts those
transports 31 times.

Even under the unsupported assumption that a rank-4 factor/core is available
for free, a correctly separated 31-source ledger is only conditional:

| Conditional item | charged FLOPs |
|---|---:|
| 31 local k3/k4 core query sets | 14.018150400B |
| 31 one-affine transports of both orders | 0.040632320B |
| one M85-style setup, if genuinely reusable | 0.087162880B |
| setup if incorrectly/really required at all 31 layers | 2.702049280B |

Those figures exclude factor construction, the nonzero-mean source
generalization, bivariate response assembly, CP source pairing, pointwise
operations, copies, and all M120 work. They are neither an implementation
ledger nor a justification for a 31-times-0.580B estimate.

M120's audited complete reverse plus Gaussian background is already at least
105.910B. A direct shared-CP pairing of a dense delta V at all 31 layers has a
further lower-bound-shaped sum of one n-by-n by n-by-R_l product per layer:

    sum_l M(256,256,R_l) = 16.641B

when R_l follows M120's additive reset schedule. A future ledger must show
whether its factorized bivariate response reuses or exceeds that operation and
must apply the requested contingency only once to a non-overlapping call
graph. The available M85 HOSVD construction alone is far beyond 258.4B, so no
complete target cost certificate exists.

## 4. Invariance and omission tests

### Permutation and positive gauge

For a hidden permutation P, take h'=P^T h, W'=P^T W, U'=P^T U. Then
W'^T U'=W^T U, while the source, delta m, and delta V merely permute at the
source layer. The next-layer defect and terminal scalar are invariant.

For a positive diagonal ReLU gauge D, take h'=D h and W'=D^-1 W. Physical
cumulants transform as S_r'=D^(tensor r) S_r and U'=D U, again giving
W'^T U'=W^T U. The standardized M85 bridge itself is gauge invariant away
from degeneracy, while its scale factors provide the physical covariance
weights.

These are algebraic pass conditions for an exact supplied tensor. The present
rank-4 HOSVD truncation is not a proved gauge-covariant operation: diagonal
rescaling changes its singular subspace, and a cutoff through a singular-value
tie is not a permutation-covariant selection. M85 also clips correlations and
floors variances, which cannot be silently inherited as an exact
gauge-covariant source. A repair must use variance-standardized factor
construction with explicit scale restoration, deterministic treatment of
degenerate subspaces, and fail-closed zero-variance handling.

Required target-free algebra gates are simultaneous P and D transforms of
small dense sources, followed by equality of transported T3/T4, delta m,
delta V, and every all-output M120 contraction to 1e-10. The rank-4
factorized result must match its dense same-source result before any
approximation test.

### Source-source and terminal-Born ownership

At weak bridge order,

    M85 T3 = LLQ + higher bridge terms,
    M85 T4 at zero mean = LLQQ path family + higher bridge terms.

The terminal Born operator owns LLQ and LLQQ directly; its LLLC term vanishes
at zero mean but is required at nonzero mean. At the final one-layer incidence,
M121's immediate Edgeworth conversion is the same terminal ReLU response to
the same transported source. Thus the M85/M121 and terminal-Born families are
not disjoint: adding them duplicates at least LLQ and LLQQ.

M121 must therefore run alone unless a future diagram table subtracts an
exact, explicitly labelled intersection. It must not add terminal Born's
3.111B to an M121 cost or correction as an independent benefit. The first-Born
expansion also omits all source-source interactions, the k3^2/H6 term,
connected Price-residual E propagation, and cumulant feedback after the one
allowed conversion. These omissions are legitimate only if they remain
declared; they cannot be restored post outcome.

## 5. Additional fatal interface gap: M85 is zero-mean only

M85 bridge_source accepts only covariance. Its pair bridge, repeated-index
quadrature, Hermite constants, and tree formulas assume Z~N(0,C). M121 wants
one source at every hidden layer, but a Gaussian ReLU trajectory generically
has nonzero preactivation means after the first hidden layer. In that setting
the pair bridge and local Hermite coefficients depend on alpha=mu/sigma, and
the formerly absent cubic local vertex/LLLC response need not vanish.

Consequently M85 rank 4 cannot presently be inserted at the 31 proposed
locations. Generalizing it is not a one-line call-signature change: it requires
a nonzero-mean signed bivariate bridge, repeated-index k3/k4 source,
normal-ordered local vertices, gauge analysis, and a fresh multiplicity-split
falsifier. Until then the phrase 31-source total has no defined source
operator.

## Required repair before IMPLEMENT_COMPONENT

1. Provide a nonmaterialising, target-costed construction of the M85 rank-4
   factor/core, or an exact factorized replacement of the alternating k4 path.
   It must include factor construction and never materialise an n^4 tensor.
2. Generalize the local bridge source from covariance-only zero-mean Gaussian
   inputs to the actual nonzero-mean (mu,C) background, with explicit
   fail-closed endpoint/variance rules.
3. Freeze and verify the equations in section 1 against dense all-output
   first-Born derivatives at widths 8, 12, and 16; include diagonal and
   off-diagonal central covariance, the 1/6 and 1/24 factors, 3/3 and
   4/6/4 slots, and the symmetric covariance pairing.
4. Prove permutation and positive-gauge covariance of the *truncated*
   factorized source, including degeneracy handling, rather than only of an
   ideal full tensor.
5. Run the one-layer diagram-incidence test. Unless it supplies exact
   subtraction, prohibit any terminal Born plus M121 union and retain all
   LLQ/LLLC/LLQQ ownership labels.
6. Reconstruct one complete non-overlapping FlopScope/memory ledger, including
   source construction, response, M120 pairing, and one contingency. Kill the
   candidate before efficacy if it exceeds 258.4B or has an unresolved n^4
   contraction.

The one-delay normal-order conversion and the conditional supplied-factor
contraction should be preserved. The current M121 proposal is a repairable
theory interface, not an implementation component or an outcome candidate.
