# M129: state-dependent source Frechet tangent

Date: 2026-08-07  
Scope: generated-only algebra and cost audit; no contest/public/private outcomes  
Verdict: **REPAIR at mixed-f32 P=2; KILL for the current schedule at P>=4 or all-f64 P>=2**

## 1. Result

M128's missing term `D kappa[a]` is now algebraically closed through the full
M122/M126 source, including the previously omitted fourth-order collision
partition `[2,1,1]` (`aabc`).  The implementation differentiates:

1. the Gaussian background coordinates `(mu,C) -> (sigma,alpha,rho)`;
2. every local rectified Hermite coefficient;
3. the normalized signed bridge `Q` and vertices `gamma2,gamma3`;
4. exact connected collision cumulants `[3]`, `[2,1]`, `[4]`, `[3,1]`,
   `[2,2]`, and `[2,1,1]`;
5. every repeated-output tree, star, path, and sparse-collision contraction;
6. the M126 hard-path and `[2,2]` Hutchinson estimators with a pathwise
   common-random-number tangent.

The important mutation is a new **hollow-quadratic probe** for `[2,1,1]`.
It replaces a naive tensor-vector-plus-three-GEMM schedule by one packed
tensor quadratic and one square GEMM for the primal, repeated once for the
tangent.  It is exactly unbiased and preserves output symmetry sample by
sample.  It needs `O(P n^3)` work and `O(n^3)` streamed state, never `n^4`.

Eight generated-only tests pass, including complete enumeration of all
Rademacher probes at width four and a full dense source/tangent reconstruction
at width three.  The latter proves that tree continuation plus all six
collision strata reproduces the exact small-width source and its finite-
difference derivative.

The cost result is sharp enough to prune the ladder:

- mixed-f32 `P>=4` is above `100B` even under the optimistic dense-call lower
  bound;
- all-float64 `P>=2` is above `100B` even at that lower bound;
- mixed-f32 `P=2` has a lower bound of `91.723B`, but the current protected
  upper envelope is `147.344B`;
- the executable Hermite-series `[2,1,1]` builder is only a reference.  At
  target width/depth, its retained-term count alone is at least `945.273B`, so
  it is killed as a deployment builder.  Preserving `P=2` requires an
  `O(1)`-per-triple closed-form/boundary-jet builder or a proved low-rank
  representation, plus at least `47.344B` removed from the current upper
  envelope.

Thus the missing derivative is not an `O(n^4)` mathematical obstruction.  It
is now a concrete constant-factor and source-construction obstruction.

## 2. Background Frechet map

Let

```text
sigma_i = sqrt(C_ii)
alpha_i = mu_i / sigma_i
rho_ij  = C_ij / (sigma_i sigma_j).
```

For a direction `(mu_dot,C_dot)`, the exact coordinate derivatives are

```text
sigma_dot_i = Cdot_ii / (2 sigma_i)

alpha_dot_i = mudot_i/sigma_i
              - alpha_i sigma_dot_i/sigma_i

rho_dot_ij = Cdot_ij/(sigma_i sigma_j)
             - rho_ij(sigma_dot_i/sigma_i + sigma_dot_j/sigma_j),

rho_dot_ii = 0.
```

The diagonal identity is imposed exactly after symmetry restoration.  This is
not cosmetic: allowing a floating diagonal tangent corrupts the normalized
bridge derivative.

### 2.1 Rectified Hermite coefficients

For

```text
Y = sigma (alpha+G)_+,
h_(p,r) = E[Y^p He_r(G)],
M_s(alpha) = E[(alpha+G)_+^s],
```

the exact local coefficient is

```text
r <= p:
  h_(p,r) = sigma^p p!/(p-r)! M_(p-r)(alpha)

r > p:
  h_(p,r) = sigma^p p! (-1)^k He_k(alpha) phi(alpha),
  k = r-p-1.
```

The alpha derivatives used by the forward dual are

```text
d_alpha M_s = s M_(s-1), s>=1
d_alpha M_0 = phi(alpha)

d_alpha[He_k phi] = -He_(k+1) phi,
```

and `d_sigma h_(p,r)=p h_(p,r)/sigma`.  These formulas include the
distributional ReLU kink exactly.  No deployment finite difference appears.

The rectified mean and scale follow from

```text
m_i = h_(1,0)
s_i^2 = h_(2,0) - m_i^2

sdot_i = [hdot_(2,0) - 2 m_i mdot_i]/(2 s_i).
```

The local tree vertices are

```text
gamma2_i = h_(1,2) s_i / h_(1,1)^2
gamma3_i = h_(1,3) s_i^2 / h_(1,1)^3.
```

M129 differentiates the quotients directly.  In particular it does not use a
log derivative for `gamma3`, because `h_(1,3)=-sigma alpha phi(alpha)` can be
zero at `alpha=0`.

### 2.2 Signed bridge derivative

For a pair raw moment,

```text
R_ij = sum_(r>=0) h_(1,r,i) h_(1,r,j) rho_ij^r/r!,

Q_ij = [R_ij-m_i m_j]/(s_i s_j),  Q_ii=1.
```

Termwise differentiation gives

```text
Rdot_ij = sum_r {
    (hdot_i h_j + h_i hdot_j) rho^r
    + h_i h_j r rho^(r-1) rhodot
  }/r!,

Qdot_ij = [Rdot_ij-mdot_i m_j-m_i mdot_j]/(s_i s_j)
          - Q_ij(sdot_i/s_i+sdot_j/s_j),
Qdot_ii = 0.
```

The reference evaluates both value and tangent at 64 terms and fails closed
unless a 52-term truncation agrees.  This is a small-width certificate, not a
claim that a termwise series is the best target implementation.

## 3. Exact collision derivatives

For three distinct standardized Gaussian nodes, Wick matching of Hermite
degrees gives

```text
E[f0(G0) f1(G1) f2(G2)]
 = sum_(d0,d1,d2)
     h_(0,d0) h_(1,d1) h_(2,d2)
     rho01^r01 rho02^r02 rho12^r12
     /(r01! r02! r12!),

r01=(d0+d1-d2)/2,
r02=(d0+d2-d1)/2,
r12=(d1+d2-d0)/2,
```

where only nonnegative integer matchings contribute.  Product-rule
differentiation of the three local coefficients and three correlation powers
is exact.  Powers `(2,1,1)` provide the only new raw moment needed by the
`[2,1,1]` collision stratum.

For labels `ell_1,...,ell_r`, the connected cumulant is

```text
kappa(ell_1,...,ell_r)
 = sum_(partitions pi)
     (|pi|-1)! (-1)^(|pi|-1)
     product_(B in pi) E[product_(a in B) Y_(ell_a)].
```

Its derivative owns exactly one differentiated block per product:

```text
kappadot = sum_pi coefficient(pi)
           sum_(B in pi) Mdot_B product_(B'!=B) M_B'.
```

For every repeated-index orbit M129 stores the **defect**

```text
Delta = kappa_exact - kappa_tree_continued,
Delta_dot = kappa_exact_dot - kappa_tree_continued_dot.
```

This avoids double counting: the bridge tree is evaluated on all index tuples,
then each collision orbit replaces, rather than supplements, its continued
tree value.

The complete defect inventory is

```text
order 3: [3], [2,1]
order 4: [4], [3,1], [2,2], [2,1,1].
```

Omitting `[2,1,1]` is not a controlled approximation; it omits
`n*C(n-1,2)` generic connected entries.

## 4. Tree, star, path, and hard-source forward dual

The executable implementation uses a literal forward dual

```text
(X,Xdot) @ (Y,Ydot)
  = (XY, Xdot Y + X Ydot),

(X,Xdot) * (Y,Ydot)
  = (XY, Xdot Y + X Ydot).
```

Applying those two rules to the existing M126 formulas produces exact
derivatives for `k3_aab`, `k4_aaab`, and `k4_aabb`.  The physical affine
weight is fixed, but the tree contraction uses

```text
Wtilde = diag(s) W,
Wtilde_dot = diag(sdot) W,
```

so treating the M126 `weight` operand as constant would incorrectly drop every
scale derivative.

For the hard path, with `B=Q Wtilde`, `E=Q-I`, and a Rademacher probe `z`,

```text
M_z  = B^T diag(gamma2*z) Wtilde
M_Ez = B^T diag(gamma2*E*z) Wtilde.
```

The M126 samples are entrywise products of `M_z` and `M_Ez` (or its
transpose).  M129 differentiates `B`, `gamma2`, `E`, and `Wtilde` by the
ordinary product rule while holding the realized `z` fixed.  Therefore

```text
E_z[D_theta Shat(theta,z)[a]]
  = D_theta E_z[Shat(theta,z)][a]
```

whenever the current probe is independent of the incoming direction `a`.

The `[2,2]` collision probe is linear in its defect.  Its tangent simply
replaces the defect matrix by its directional derivative in the moving
factor; the `W^T diag(z) W` factor is constant.

All state and repeated-output tables remain `O(n^2)`.  Tree/path/sparse
collision tangents use `O(n^3)` arithmetic.  No ambient order-four tensor is
formed.

## 5. The `[2,1,1]` / `aabc` contraction

Use packed storage `A_(i;jk)=A_(i;kj)` for `j<k`, with exact zeros whenever
`i=j`, `i=k`, or `j=k`.  Define

```text
S_i(a,b) = sum_(j<k) A_(i;jk)
           [W_(j,a) W_(k,b) + W_(k,a) W_(j,b)].
```

The exact twelve-slot orbit formulas are

```text
K_aaaa[a]
 = 6 sum_i W_(i,a)^2 S_i(a,a)

K_aaab[a,b]
 = 3 sum_i {
       W_(i,a) W_(i,b) S_i(a,a)
       + W_(i,a)^2 S_i(a,b)
     }

K_aabb[a,b]
 = sum_i {
       W_(i,a)^2 S_i(b,b)
       + W_(i,b)^2 S_i(a,a)
       + 4 W_(i,a) W_(i,b) S_i(a,b)
     }.
```

The coefficients are exactly the slot counts:

```text
aaab: 6 + 3 + 3
aabb: 2 + 2 + 4 + 4.
```

### 5.1 Hollow-quadratic estimator

Draw one iid Rademacher vector `z` and set

```text
u_a = sum_j W_(j,a) z_j
t_i = 2 sum_(j<k) A_(i;jk) z_j z_k
M_ab = sum_i W_(i,a) t_i W_(i,b)
d_a = M_aa.
```

Because the singleton pair is hollow,

```text
E[z_j z_k u_a u_b]
 = W_(j,a)W_(k,b)+W_(j,b)W_(k,a),  j!=k.
```

Hence the following one-probe tables are unbiased:

```text
Khat_aaaa[a] = 3 d_a u_a^2

Khat_aaab[a,b]
 = (3/2) [M_ab u_a^2 + d_a u_a u_b]

Khat_aabb[a,b]
 = (1/2) [d_a u_b^2 + d_b u_a^2]
   + 2 M_ab u_a u_b.
```

Every sample obeys

```text
Khat_aabb = Khat_aabb^T
diag(Khat_aaab) = diag(Khat_aabb) = Khat_aaaa.
```

For `A_dot`, reuse the same `z`, form `t_dot`, `M_dot`, and `d_dot`, and
differentiate the three displayed formulas.  Since physical `W` is fixed,
this is one additional packed reduction and one additional square GEMM.

Diagonal leakage is a fatal bias, not a small numerical error.  If any
`A_(i;jj)`, `A_(i;ij)`, or `A_(i;ji)` survives packing, the Rademacher fourth
moment creates trace/self-contraction terms absent from the identity.  The
component validates hollowness and fails closed.

### 5.2 Storage and arithmetic

At `n=256`, full triangular packing has

```text
n*C(n,2) = 8,355,840 entries = 63.75 MiB in float64.
```

After removing collisions, only

```text
n*C(n-1,2) = 8,290,560
```

entries can be nonzero.  `A+A_dot` need about `127.5 MiB` in full triangular
float64 packing and should be streamed one layer at a time.

For one probe/layer, let

```text
G = 2n^3-n^2 = 33,488,896
T = 2n*C(n,2)-n = 16,711,424
V = 2n^2-n = 130,816.
```

The primal+tangent lower bill is

```text
2T + 2G + V = 100,531,456 f32-billed operations.
```

An explicit gather/pair-feature/output allowance gives

```text
100,531,456 + 10*C(n,2) + 66n^2
=105,183,232 per probe/layer.
```

Float64 doubles both.  These bills include the tensor reduction; it is not
hidden inside a reserve.

## 6. Probe and product ownership

The unbiasedness rules are conditional and non-negotiable.

1. **Inside `[2,1,1]`, use the same probe in `t` and `u`.**  The fourth-moment
   identity is the mechanism.  Replacing it by independent probes destroys
   the desired cross pairing and changes the normalization.
2. **Use the same current-layer probe for `A` and `A_dot`.**  This is the
   pathwise derivative of one realized estimator and is unbiased when the
   incoming tangent is fixed conditional on prior layers.
3. **Use fresh keys across feedback.**  If `A_dot` depends on probe-estimated
   earlier sources, the current contraction probe must be independent of the
   sigma-field that produced it.  Key by `(layer,family,probe)` or cross-fit.
   Reusing one probe recursively creates self-contractions and bias.
4. Different linear source families may share a fresh current-layer probe;
   expectation remains correct, though covariance changes.
5. M126's `k3` tables are exact, so the M128 `k3^2` response product needs no
   probe correction in this branch.  If a future mutation makes either factor
   stochastic, use two independent banks or the off-diagonal U-statistic

```text
1/[P(P-1)] sum_(p!=q) khat3_p khat3_q.
```

6. A future retained `k4^2` term likewise requires independent estimates or a
   proved U-statistic.  Squaring one noisy table is biased.

## 7. Co-propagation and the absence of `n^4`

M128's second tangent remains

```text
a_(l+1) = J_l a_l + S_l

b_(l+1) = J_l b_l
          + (1/2)H_l[a_l,a_l]
          + DS_l[a_l]
          + T_l.
```

M129 supplies the previously missing `DS_l[a_l]`.  The background direction
`a_l` is one mean vector plus one symmetric covariance matrix.  Its Frechet
image consists of vector/matrix bridge tangents, `O(n^2)` repeated-output
tables, and a streamed `O(n^3)` `[2,1,1]` defect.  Each probe reduces that
defect before output transport.  Therefore primal source, first tangent,
second tangent, and source derivative can be co-propagated with `O(n^3)` work
per layer at fixed probe count.

The only dense order-four tensor in the repository is the width-small oracle
used by tests.  It is marked as such and is not needed by the probe schedule.

## 8. Complete cost boundary

The ledger combines:

```text
M126 exact primal source                  24 square calls/layer
exact source tangent lower/upper         24 / 36 extra calls/layer
hard path + [2,2], primal+tangent         9P calls/layer
[2,1,1], primal+tangent                  exact T/G/V bill above
M125b protected background/first carrier 12.819347280B
M128 second affine tangent                4.152623104B
protected carrier total                  16.971970384B.
```

The tangent lower count assumes one matrix product per differentiated primal
call.  The upper count enumerates the product-rule terms when both tree
operands move; sparse collision transport has fixed physical `W` and needs one
extra call.  Packing dual values into a wider call does not reduce billed
arithmetic under shape-based FlopScope accounting.

The conservative conditional upper also declares `16.8B` before the `1.25`
source safety factor:

```text
4.0B  existing analytic collision source
8.0B  state/collision derivative plus closed-form [2,1,1] builder contract
1.6B  second response scalars
3.2B  dual copies and allocations.
```

This is a **contract** for a future closed-form builder.  The current termwise
Hermite reference does not meet it.

All values below are total billions of billed operations:

| probes | mixed-f32 lower | mixed-f32 protected upper | float64 lower | float64 protected upper |
|---:|---:|---:|---:|---:|
| 2 | 91.723 | 147.344 | 166.474 | 256.716 |
| 4 | 116.643 | 178.854 | 216.314 | 319.736 |
| 8 | 166.482 | 241.874 | 315.993 | 445.777 |
| 16 | 266.161 | 367.915 | 515.351 | 697.859 |
| 22 | 340.921 | 462.446 | 664.870 | 886.920 |

Consequences:

- `P>=4` mixed-f32 is killed without appeal to variance or efficacy.
- `P>=2` float64 is killed.
- `P=2` mixed-f32 has only `8.277B` between its optimistic lower bound and
  `100B`.  It cannot support the current declared reserves and safety margin.
- To promote `P=2`, an implementation must demonstrate the lower tangent call
  schedule, a closed-form streamed collision builder, total non-GEMM overhead
  below the remaining headroom, and an installed-FlopScope trace.  The current
  protected upper must fall by at least `47.344B`.

### 8.1 Direct Hermite builder is killed

At 24 degrees, the trivariate Hermite sum has `3,678` admissible degree
triples.  Target width has `8,290,560` nonzero packed `[2,1,1]` entries per
layer and `257,007,360` across 31 layers.  Merely visiting each retained term
once costs at least

```text
257,007,360 * 3,678 = 945,273,070,080
```

scalar term visits, before coefficient evaluation, products, tangent work,
copies, or the rest of the method.  The executable series is therefore a
correctness oracle only.  A target implementation needs a constant-work
trivariate truncated-normal boundary formula, low-rank/separable structure,
or a proof that the defect may be removed.  None is currently supplied.

## 9. Generated verification

```text
test_collision_cumulant_dot_includes_211 ... ok
test_complete_bridge_state_frechet_matches_dense_finite_difference ... ok
test_cost_envelope_has_precise_repair_kill_boundary ... ok
test_full_source_and_tangent_decompose_exactly_including_211 ... ok
test_hollow_quadratic_211_probe_is_exact_in_complete_average ... ok
test_local_hermite_coefficient_derivative ... ok
test_path_and_22_probe_tangents_use_common_random_numbers ... ok
test_tree_dual_matches_formula_finite_difference ... ok

Ran 8 tests in 3.067s
OK
```

The strongest test builds the exact generated width-three order-3/order-4
source from M122, transports it densely, and compares both its value and
finite-difference state derivative against

```text
tree continuation
+ [3]/[2,1]/[4]/[3,1]/[2,2] sparse defects
+ dense-small [2,1,1] defect oracle.
```

Complete enumeration of all `2^4` Rademacher probes separately proves that
the hollow-quadratic `[2,1,1]` primal and tangent average to the dense oracle,
including every repeated-output diagonal identity.

## 10. Disposition

### Preserved

- exact background, bridge, vertex, collision, tree, path, and probe Frechet
  formulas;
- the hollow-quadratic `[2,1,1]` estimator;
- common-random pathwise tangent ownership;
- conditional fresh-layer probe rule;
- `O(Pn^3)` source/tangent co-propagation;
- the mixed-f32 `P=2` branch as a narrow repair candidate.

### Killed

- direct 24-term trivariate Hermite construction at target width;
- mixed-f32 `P>=4` for the current complete source+tangent schedule;
- all-float64 `P>=2`;
- recursive reuse of probes across a state that already depends on them;
- naive squares of stochastic cumulant estimates;
- any `[2,1,1]` estimator that permits diagonal leakage.

### Required next mutation

The only honest nonincremental continuation is to attack the two remaining
cost gods together:

1. derive a streamed constant-work trivariate rectified boundary jet for
   `E[Y_i^2 Y_j Y_k]` and its state derivative, or prove exploitable low rank
   in the `[2,1,1]` defect; and
2. algebraically fuse the 12 tree calls so the exact tangent approaches its
   24-call lower count, then measure the installed FlopScope trace.

If either fails to put the complete protected `P=2` bill below `100B`, kill
M128 as a deployable branch while preserving its exact response mathematics.

## 11. Artifacts

| artifact | SHA-256 |
|---|---|
| `m129_source_frechet_tangent/m129_source_frechet.py` | `B7B9D4B0228331972F7FD7B5BD2FB6081BA3053D25DAF64F3F8DD0F84E31A6BF` |
| `m129_source_frechet_tangent/test_m129_source_frechet.py` | `539787960221759664777211B709CDB05DFE870C8312F3C67C12842990C32000` |
