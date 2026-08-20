# M134 Hermite graph-degree sampler theory -- 2026-08-07

## Decision

**REPAIR-ONLY / DO NOT PROMOTE.**

There is a genuine new contraction identity.  For every fixed tripartite
Hermite edge-degree configuration `(r,s,t)`, the complete hidden
`[2,1,1]` contribution can be reduced to one masked triangle GEMM, and the
M129 repeated-output probe then needs one output Gram GEMM.  The exact
continued M122 tree is a finite population of only nine factors of the same
form.  Sampling the union therefore estimates the **exact-minus-tree** defect
without materialising an `n^3` collision tensor.  The fixed-configuration
Frechet tangent is also closed: primal plus tangent uses three hidden GEMMs and
two output GEMMs.

That algebra does not produce a target-valid solver.  The proposed
importance/Russian-roulette layer has two fatal gates:

1. the trivariate Hermite graph series is not globally convergent on valid
   correlation matrices; a generated equicorrelation example at `rho=0.975`
   has raw partial sums `3.10, 3.15, 4.10, 22.29, 382.96, 7667.42` at local
   horizons `12,16,20,24,28,32`, whereas `rho=0.2` stabilises to 13 digits;
   and
2. even on three generated low-correlation states where the finite 24-degree
   oracle converges, joint degree/sign sampling has `22.34--93.40x` the
   one-probe variance of the already-built full collision tensor, or
   `44.68--186.81x` the variance of M129 P2.

One first-order sample is arithmetically close to feasible (`97.086B` before
the coefficient/probability builder), but it has neither an exact tail
certificate nor adequate variance.  Two samples leave only `0.319B` before
that builder.  The complete M128 tangent has a `90.681B` optimistic lower
bound but a `145.681B` protected upper at one sample.  No honest `<100B`
exact/finite-variance implementation is certified.

This audit used generated algebra only.  It read no contest model, truth,
scorer, public/private outcome, submission, or champion artifact.

## 1. Exact connected graph expansion

Let

```text
Y_a = sigma_a (alpha_a + G_a)_+,
X_a = Y_a - E[Y_a],
c_a(d) = E[X_a He_d(G_a)],
b_a(d) = E[X_a^2 He_d(G_a)].
```

Thus `c_a(0)=0`.  For `d>=1`, `c_a(d)` is the ordinary ReLU Hermite
coefficient, and

```text
b_a(d) = E[Y_a^2 He_d] - 2 E[Y_a] E[Y_a He_d]
         + [d=0] E[Y_a]^2.
```

For three distinct hidden labels `i,j,k`, central fourth-cumulant ownership is

```text
kappa_iijk = E[X_i^2 X_j X_k]
             - Var(X_i) Cov(X_j,X_k)
             - 2 Cov(X_i,X_j) Cov(X_i,X_k).                 (1)
```

Write `r,s,t` for the numbers of normal-ordered edges `ij,ik,jk`.  The raw
three-node graph coefficient is

```text
b_i(r+s) c_j(r+t) c_k(s+t)
R_ij^r R_ik^s R_jk^t / (r! s! t!).                           (2)
```

Equation (1) has an especially clean incidence subtraction:

- every `(0,0,t)` factor cancels exactly against
  `Var(X_i) Cov(X_j,X_k)`;
- when `t=0` and `r,s>=1`, replace `b_i(r+s)` by
  `b_i(r+s)-2c_i(r)c_i(s)`; and
- all other factors retain (2).

This proves connected-cumulant ownership without forming a fourth-order
moment or subtracting a noisy estimate after transport.  It also explains
M129's count.  At local horizon 24 there are 3678 raw admissible degree
triples.  Centralization deletes the 24 `(0,0,t)` triples, leaving 3654 before
identically-zero coefficient factors are removed.

## 2. One-GEMM contraction of a fixed configuration

For any matrix `E` and integer `q>=0`, define its hollow power

```text
H_q(E)_ab = [a != b] E_ab^q,
```

where `H_0` is the off-diagonal all-ones matrix.  The hollow mask owns all
three exclusions `i!=j`, `i!=k`, `j!=k`, even when an edge degree is zero.

For one oriented factor write

```text
A_i;jk = a_i ell_j r_k H_p(i,j) H_q(i,k) H_s(j,k).            (3)
```

Given a Rademacher vector `z`, put

```text
U = H_p * (ell*z)^T,
V = H_q * (r*z)^T.
```

Then all repeated-label contractions needed by M129 begin with

```text
t_i = sum_jk A_i;jk z_j z_k
    = a_i rowsum( (U @ H_s) * V ).                            (4)
```

Equation (4) is one `n x n` GEMM plus `O(n^2)` Schur/reduction work.  A single
oriented degree factor need not be symmetric in `j,k`; the quadratic form in
`z` automatically takes its symmetric part.  Summing `(r,s,t)` and its
singleton-exchanged partner restores the exact symmetric collision.

The small-width oracle verifies (4) against the dense tensor to `2e-12`.

## 3. Exact-minus-tree ownership in nine more factors

The continued M122 tree on the multiset `(i,i,j,k)` has three star and six
path factors.  Suppressing the common `relu_scale_i^2 relu_scale_j
relu_scale_k`, their edge degrees and local nonlinear coefficient are:

| family | `(ij,ik,jk)` | coefficient before common scale |
|---|---:|---|
| star at repeated `i` | `(1,1,0)` | `2 gamma3_i` |
| star at `j` | `(2,0,1)` | `gamma3_j` |
| star at `k` | `(0,2,1)` | `gamma3_k` |
| path, internal `i,k` | `(0,1,1)` | `2 gamma2_i gamma2_k` |
| path, internal `i,j` | `(1,0,1)` | `2 gamma2_i gamma2_j` |
| path, internal `i,i` | `(1,1,0)` | `2 gamma2_i^2` |
| path, internal `j,k` | `(1,1,1)` | `2 gamma2_j gamma2_k` |
| path, internal `i,k` | `(1,2,0)` | `2 gamma2_i gamma2_k` |
| path, internal `i,j` | `(2,1,0)` | `2 gamma2_i gamma2_j` |

Each row factors into the `a_i ell_j r_k` form in (3).  Add these nine
factors with a negative sign to the Hermite configuration population.  If
`G` is sampled from the combined signed population with probability `p_G`,
then `A_G/p_G` estimates `exact kappa_iijk - continued tree_iijk` directly.
There is no separate tree subtraction and no collision overlap with the
`[4]`, `[3,1]`, or `[2,2]` tables.

The generated width-five oracle verifies the nine-factor sum against the
dense M122 tree continuation to `2e-13`.

## 4. Repeated-output transport and unbiasedness

With physical source-to-output weight `W`, define

```text
u = W^T z,
M = W^T diag(t) W,
d = diag(M).
```

The M129 identities are

```text
K_aaaa = 3 d * u^2,

K_aaab = (3/2) [ M_ab u_a^2 + d_a u_a u_b ],

K_aabb = (1/2) [ d_a u_b^2 + d_b u_a^2 ]
          + 2 M_ab u_a u_b.                                  (5)
```

For a fixed factor, the Rademacher fourth-moment identity and the hollow
support make the expectation of (5) equal all twelve slot placements of that
factor.  Generated widths up to five verify the complete sign average against
M126's dense 211 oracle to `3e-11`.

For a frozen response functional `L`, let `Y_g(z)=L(K(A_g,z))`.  If `G` and
`z` are independent and `p_g>0` on every nonzero factor,

```text
E[Y_G(z)/p_G] = sum_g E_z[Y_g(z)].                             (6)
```

The exact scalar response variance is

```text
Var = sum_g E_z[Y_g(z)^2]/p_g - target^2.                     (7)
```

The variance-minimizing categorical probabilities are proportional to
`sqrt(E_z[Y_g^2])`, which would require the very response computation being
avoided.  M134 instead freezes a weights-only norm proxy built from the local
coefficient norms and the three hollow edge-power norms.  This is legal and
unbiased, but not low variance.

### Conditional independence at depth

At layer `l`, the Gaussian background and all earlier stochastic tangents are
measurable with respect to the previous-layer filtration.  Freeze `p_l` from
that background, then draw a fresh `(G_l,z_l)` independent conditional on the
past.  Equation (6) then holds conditionally and hence unconditionally.  A
retry, outcome-selected probability table, or reuse of a current-layer probe
to choose its own factor is forbidden.

## 5. Frechet tangent

For edge degree `q`,

```text
D H_q[E;Edot] = [q>0] q offdiag(E^(q-1) * Edot).               (8)
```

Differentiate the local Hermite coefficients exactly, freeze the categorical
probabilities at the unperturbed Gaussian background, and apply the product
rule to (4):

```text
D core = rowsum( ((Udot @ H_s) + (U @ Hdot_s))*V
                  + (U @ H_s)*Vdot ).                         (9)
```

The primal `U@H_s` is reused.  Thus primal plus tangent uses three hidden
GEMMs total, not four.  Equations (5) applied to `t` and `tdot` use two output
Gram GEMMs, for five square calls per sampled configuration per source layer.
The nine negative tree factors have the same derivative form; all scale,
`gamma2`, `gamma3`, and bridge product rules are explicit in the companion
module.

The generated finite-difference checks pass at relative tolerance `4e-7` for
both a Hermite factor and a tree-control factor.  Because `p` is frozen, no
score-function derivative belongs to the Frechet source.  Differentiating or
resampling `p(theta+epsilon a)` would change the estimator and require a
separate likelihood-ratio term.

## 6. Russian roulette cannot repair a divergent graph series

Lyne et al. show how a convergent infinite series can be made unbiased by
finite-time stochastic truncation, while warning that the estimate can be
signed.  Cui et al. characterize cost/variance-optimal random horizons for
expected cumulative series.  Both start from a well-defined convergent target;
random truncation does not assign the analytic continuation of a divergent
Taylor series.  See [Lyne et al., arXiv:1306.4032](https://arxiv.org/abs/1306.4032)
and [Cui et al., arXiv:1804.04215](https://arxiv.org/abs/1804.04215).

For shell increments `Delta_h` and survival probabilities
`q_h=P(N>=h)`, the usual estimator is

```text
sum_(h<=N) Delta_h/q_h.
```

Expectation interchange needs at least an integrable envelope; finite
variance additionally needs the corresponding weighted second-moment series.
The M122 three-node expansion has no such global certificate.  Along the
valid equicorrelation path

```text
R(rho) = (1-rho) I + rho 11^T,
```

positive definiteness holds for `-1/2 < rho < 1`.  The graph expansion is the
Taylor expansion about independent coordinates.  For generic unequal nonzero
thresholds its nearest covariance-boundary singularity is at `rho=-1/2`, so a
global claim at large positive `rho` is unavailable.  The deterministic
generated diagnostic makes the failure concrete:

| local horizon | 12 | 16 | 20 | 24 | 28 | 32 |
|---:|---:|---:|---:|---:|---:|---:|
| `rho=0.2` | .679645019601 | .679645019601 | .679645019601 | .679645019601 | .679645019601 | .679645019601 |
| `rho=0.975` | 3.09893 | 3.15062 | 4.09760 | 22.2935 | 382.963 | 7667.42 |

This does **not** assert that the dossier's inter-input kernel correlation is
the same as a within-layer neuron correlation.  It proves the narrower point
needed for fail-closed deployment: positive definiteness and `|rho|<1` do not
certify this graph expansion.  Every target layer would need an independent,
weights-only convergence and second-moment gate.  No such gate has been proved
or priced.

The generalized Gaussian moment identities in
[Mamis, arXiv:2202.00189](https://arxiv.org/abs/2202.00189) justify derivative/
moment rearrangements but do not turn this divergent multivariate Taylor
expansion into a constant-work trivariate orthant formula.

## 7. Exact generated response-variance audit

For width four, all `2^4` Rademacher signs and every active 24-degree factor
plus the nine tree factors were enumerated.  These are exact finite-population
second moments, not Monte Carlo estimates.  A frozen generated linear
combination of `K_aaab` and `K_aabb` served as the one-delay response.

| seed | correlation scale | active factors | joint / hidden-P1 | joint / M129-P2 |
|---:|---:|---:|---:|---:|
| 13411 | 0.12 | 3617 | 55.160 | 110.320 |
| 13412 | 0.30 | 3617 | 22.341 | 44.682 |
| 13413 | 0.50 | 3617 | 93.405 | 186.810 |

`hidden-P1` means the same full defect tensor is already available and only
M129's sign probe remains.  `M129-P2` divides that hidden variance by two.
Consequently M134 needs `45--187` independent joint samples merely to match
M129 P2 on these three generated cases.  That range is already far beyond the
budget before considering a correlation-tail gate.

## 8. Complete target cost boundary

At `n=256`, one float32 square GEMM bills

```text
M = 2 n^3 - n^2 = 33,488,896.
```

There are 31 source layers.

### 8.1 First-order attachment to M126 P8

One joint sample uses one hidden triangle GEMM and one output Gram GEMM.
Applying M126's existing `1.25` protection gives

```text
increment/sample = 1.25 * 31 * 2M = 2.595389440B.
```

| joint samples | M126 P8 + M125b before builder |
|---:|---:|
| 1 | 97.085641040B |
| 2 | 99.681030480B |
| 4 | 104.871809360B |

The finite 24-degree coefficient/power/proxy builder is not free.  A
conservative `1.0B` allowance leaves K1 near `98.086B` and kills K2.  More
importantly, a finite 24-degree table is biased; an exact unbounded proposal
has no certified expected work or variance.  Therefore K1 being arithmetically
plausible does not authorize it.

### 8.2 Complete M128 source tangent

Replace M129's prebuilt 211 collision probe with the on-the-fly factor.  The
unchanged lower base has 66 square calls/layer; the protected-call base has
78.  Each joint primal+tangent sample adds five:

| samples | optimistic lower | protected upper before new builder |
|---:|---:|---:|
| 1 | 90.681030480B | 145.680632144B |
| 2 | 95.871809360B | 152.169105744B |
| 4 | 106.253367120B | 165.146052944B |

The upper includes M129's existing `16.8B` scalar/copy reserves and the
carrier.  K1 would have to remove `>45.681B` from a complete protected ledger;
the graph identity does not do so.  K2 has only `4.128B` optimistic headroom
before every unpriced exact-tail and proxy operation.

For comparison, M126 P8 is `94.490251600B`; M129 P2 is `91.723B` optimistic
and `147.344B` protected.  M134 changes the missing-collision mechanism, but
does not change the base exact-source or tangent bills enough to cross the
protected boundary.

Variance matching is even more decisive.  Each first-order sample costs
`2.595B` protected and each second-order sample adds `5.191B` to the lower
ledger.  The generated requirement of `45--187` samples therefore adds at
least `116.8--485.3B` first-order or `233.6--970.7B` second-order.

## 9. What survives the failure

The following components are promoted as reusable mathematics, not as a
submission candidate:

1. exact connected centralization by deleting `(0,0,t)` and modifying the
   `t=0` row coefficient;
2. the one-GEMM masked-triangle identity (4);
3. the nine-factor exact tree control, which makes defect ownership sampleable;
4. the exact fixed-probability Frechet tangent (8)--(9); and
5. the exact response-level variance formula (7), suitable for judging any
   future degree proposal without outcome data.

The viable mutation is **not** to increase the number of raw degree samples.
It is to first replace the divergent trivariate Taylor expansion by a
constant-work boundary/conditional-Gaussian formula, then use graph sampling
only for a rigorously bounded residual.  A low-correlation-only branch could
also survive if every layer passes a predeclared tail and response-second-
moment certificate, but the present three-case variance audit gives no reason
to spend the remaining budget on it.

## 10. Reproduction

```powershell
& 'work\headroom-recursion\.venv\Scripts\python.exe' -m pytest -q -p no:cacheprovider `
  'work\scorefloor_generation\m134_hermite_graph_sampler\test_m134_hermite_graph_sampler.py'

& 'work\headroom-recursion\.venv\Scripts\python.exe' `
  'work\scorefloor_generation\m134_hermite_graph_sampler\run_m134.py'
```

The test suite has eight passing tests.  `results.json` contains the frozen
generated variance, convergence, and cost ledger.

