# M126 independent judge -- 2026-08-07

## Verdict

**Overall: REPAIR / BLOCKED.**

**PASS_COMPONENT:** the repeated-output orbit counts, exact bridge-tree
contractions, `ABBA/BAAB + ABAB/BABA` aggregate, Rademacher expectation and
variance, hard `[2,2]` collision probe, and the small-width twelve-slot
`[2,1,1]` oracle are mathematically correct on their declared inputs.

**REPAIR:** the delivered module is a float64 NumPy reference, not the fused
float32 FlopScope schedule in the worksheet.  It has no integrated probe
average, response-level variance gate, mixed-precision implementation, frozen
numeric tolerances, or native residual/memory trace.  The collision input
contract also fails to reject nonzero diagonals in three tables, and the
`[2,2]` probe is only algebraically symmetric, not bit-symmetric.

**KILL** either of these stronger claims:

1. M126 is an exact M122 source.  The exact three-label `[2,1,1]`/`aabc`
   collision stratum is absent from the main source and cost ledger.
2. `P=8` is promotable because `94.490251600B` fits a worksheet.  That number
   is arithmetically correct under the stated fused-call and reserve
   conventions, but it is not a native integrated trace and says nothing about
   response-level stochastic error or float32 parity.

All executions used generated Philox arrays only.  No contest data, target,
scorer, champion output, submission, or outcome grid was read.

## Decision table

| claim | decision | independent finding |
|---|---|---|
| orbit multiplicities | **PASS_COMPONENT** | independent labelled-path and multiset enumeration agrees exactly |
| exact tree and sparse-collision formulas | **PASS_COMPONENT** | dense tensor and additional basis-one oracles agree at roundoff |
| hard path aggregate | **PASS_COMPONENT** | `2(B_ab+B_ba)^T E(B_ab+B_ba)` has the claimed orbit weights |
| Rademacher expectation/one-entry variance | **PASS_COMPONENT** | exhaustive sign enumeration agrees |
| `[2,2]` collision probe | **PASS_COMPONENT** | unbiased with the required factor two |
| `[2,1,1]` twelve-slot formulas | **PASS_COMPONENT oracle** | formulas are right, but the stratum is omitted from the source |
| exact M122 source | **KILL** | omitted `[2,1,1]` changes `K31`, `K22`, their diagonals, mean, and covariance |
| 24 exact fused calls/layer | **PASS worksheet** | valid only after an unstated but exact diagonal-k3 fusion |
| float32 and float64 ledger arithmetic | **PASS worksheet** | formulas and dtype rates reproduce; no native fused source trace exists |
| `P8 + M125b = 94.490251600B` | **PASS arithmetic / REPAIR interpretation** | correct sum of two protected worksheets, not a measured candidate total |
| same-probe output symmetry | **REPAIR** | path sample is bit-symmetric; collision sample drifts at roundoff |
| response-level variance certificate | **REPAIR** | exact functional is derivable, but absent; entrywise variances can be wrong by large factors |
| float32 parity gates | **REPAIR** | implementable in principle and a prototype passes one generated case, but no locked implementation or thresholds exist |
| edge or Hadamard mutation | **PRESERVE FOR NEXT FOLD** | fixed-count importance edges look material; Hadamard gives a small exact variance reduction |

## 1. Hash-locked scope and rerun

The three hashes recorded in the recursion ledger still match the current
packet:

```text
f0462b96e7f898812d39b7a39f458f965835523f2a4c7a509c43f62dc7c1011c  code
7c78c5b61bb17ffe19f36bf40c6e72b0cf559b33a4b62eaeea818b7120f620fc  tests
0695954233060b8aa452781d8960a7f9662cbee9643bb94a400f88a9a7235846  theory
```

The committed generated-only suite reran **8/8 PASS**.  Passing the committed
suite is not the verdict by itself; the hostile checks below were separate.

## 2. Orbit multiplicities

There are `4!/2=12` undirected Hamilton paths on four labelled vertices.
Independent enumeration before coalescing equal output labels gives:

```text
AAAB:
  singleton endpoint                 6
  singleton internal                 6

AABB:
  AABB/BBAA block                    4
  ABBA palindrome                    2
  BAAB palindrome                    2
  ABAB/BABA alternating              4
                                      --
                                      12
```

For stars, choosing the center gives `3+1` for `AAAB` and `2+2` for
`AABB`.  For the order-three tree it gives `2+1` for `AAB`.

Independent multiset permutation counts give the collision slot factors:

```text
[3]        1        [2,1]       3
[4]        1        [3,1]       4
[2,2]      6        [2,1,1]    12
```

These agree with `ORBIT_MULTIPLICITIES`.  The distinction between the two
palindromes matters before output exchange; their sum is invariant to the
report's naming convention.

## 3. Exact path aggregate

Let

```text
A = QW,
B_ab = gamma2 * A_:a * W_:b,
E = Q-I,
D_ab = B_ab + B_ba.
```

The residual self and cross tables are

```text
S_ab = B_ab^T E B_ab,
C_ab = B_ab^T E B_ba = C_ba.
```

The two `ABBA/BAAB` copies in each direction and four alternating copies give

```text
2(S_ab+S_ba) + 4 C_ab
  = 2(B_ab+B_ba)^T E (B_ab+B_ba)
  = 2 D_ab^T E D_ab.                                      (1)
```

This is exactly what `path_aabb_residual_probe_sample` estimates.  It is only
the hard residual aggregate: the four block paths remain in the separately
exact cubic `4 U^T Q U` term.  At `a=b`, hard residual plus block residual has
the required total path multiplicity twelve.

The tree formulas also passed the existing independently materialized
order-three/order-four tensors at widths 2--5.  No missing orbit or extra
factor was found.

## 4. Rademacher estimator and cancellation

For one outcome-independent sign vector `z` with `E[zz^T]=I`, define

```text
M_z  = A^T diag(gamma2*z) W,
M_Ez = A^T diag(gamma2*(E z)) W.
```

Then entrywise

```text
E[M_z * M_Ez]   = S,
E[M_z * M_Ez^T] = C,
```

and

```text
2(M_z+M_z^T) * (M_Ez+M_Ez^T)                              (2)
```

is an unbiased, sample-by-sample symmetric estimator of (1).  Expansion of
(2) recovers exactly `2(S+S^T)+4C`.

For fixed `u,v`, independent Rademacher coordinates give

```text
Var[(u^T z)(v^T z)]
 = ||u||^2 ||v||^2 + (u^T v)^2 - 2 sum_i u_i^2 v_i^2.       (3)
```

The fourth-moment enumeration proving (3) leaves the two equal-pair
contractions and subtracts the duplicated all-equal case.  Exhaustive signs
agree with the implementation to roundoff.

The cancellation warning is real, not rhetorical.  A hostile actual
`[2,2]` collision entry was constructed with

```text
u = (1,1,1)/sqrt(3),
v = (1,1,-2)/sqrt(6),
v = E22 u,              diag(E22)=0,
p_aa = W_:a^2 = u.
```

Its exact hard collision value `2 u^T E22 u` is zero to roundoff
(`2.22e-16`), while exhaustive signs give one-probe variance `4/3`.  At
`P=8` the standard deviation is `0.408248`.  Relative error is therefore
unbounded even though the estimator is exactly unbiased.

## 5. `[2,2]` collision estimator

For `p_ab=W_:a*W_:b`, the hard slot contribution is

```text
H22_ab = 2 p_ab^T E22 p_ab.                                (4)
```

With

```text
N_z  = W^T diag(z) W,
N_Ez = W^T diag(E22 z) W,
```

`2 N_z*N_Ez` has expectation (4).  An independent one-edge basis test and
complete sign average recovered the exact table with maximum error
`2.67e-15`.  The factor two is necessary: the other four of the six `[2,2]`
slots live in the already-counted nonhard table.

There is a numerical contract defect.  Across 64 generated same-probe cases,
the path sample was bit-symmetric, but the collision sample was not:

```text
path:       array_equal(sample, sample.T) = true
collision:  array_equal(sample, sample.T) = false
collision maximum antisymmetry             2.08e-17
```

The two GEMMs are symmetric algebraically but their independently accumulated
triangles need not be bit-identical.  A float32 prototype amplified final
`K22` antisymmetry to `3.72e-8`.  A native child must explicitly canonicalize
the collision sample or final table and charge the add/scale.

## 6. `[2,1,1]` formulas and the binding omission

For a canonical triple with repeated label `i` and distinct unordered
singletons `j,k`, direct scattering of all twelve slots gives

```text
K31_ab += Delta_ijk [
    6 W_ia W_ib W_ja W_ka
  + 3 W_ia^2 W_jb W_ka
  + 3 W_ia^2 W_kb W_ja ],                                  (5)

K22_ab += Delta_ijk [
    2 W_ia^2 W_jb W_kb
  + 2 W_ib^2 W_ja W_ka
  + 4 W_ia W_ib (W_ja W_kb + W_jb W_ka) ].                  (6)
```

The coefficients in (5) are `6+3+3`; those in (6) are `2+2+4+4`.
Basis-one hostile tests activated each canonical triple separately at width 6
and compared against all twelve dense slots.  Worst errors in `K31`, `K22`,
and the repeated diagonal were each `2.84e-14`.  The oracle is correct.

But `collision_repeated_exact` explicitly excludes this tensor, and
`flopscope_ledger` sets
`exact_three_label_211_collision_charged=False`.  At width 256 there are

```text
256 * C(255,2) = 8,290,560
```

canonical triples.  The straightforward `J_i=W^T Delta_i W` schedule needs
512 square GEMMs per layer and costs `664.419696640B` protected in float32.
This is why a correct small oracle does not repair the target-width source.

Omitting the stratum changes `K31`, `K22`, their diagonals, the one-delay mean,
and the covariance.  Calling the remaining component an exact M122 source is
therefore **KILL**, not approximation by an innocuous residual.

### Collision input-contract repair

The declared `[2,1]`, `[3,1]`, and `[2,2]` matrices must have zero diagonals so
their ownership is disjoint from `[3]` and `[4]`.  Hostile calls with a
nonzero diagonal in each of `majority3`, `majority4`, and `paired4` were all
accepted.  This does not change the valid-input identities, but it permits
silent double ownership.  The module must reject these three cases.

## 7. Complete output-level variance functional

Entrywise variance is insufficient when one sign vector is shared across
path and collision tables.  For any frozen scalar linear response, collect
all same-probe terms as

```text
Y(z) = z^T H z,
H = Sym[ sum_t 2 c_t u_t v_t^T ].                           (7)
```

Here `c_t` contains the orbit and response coefficient, and `(u_t,v_t)` is
either `(D_ab,E D_ab)` or `(p_ab,E22 p_ab)`.  For Rademacher signs,

```text
E[Y] = trace(H),
Var[Y] = 4 sum_(i<j) H_ij^2.                               (8)
```

For final outputs `o,r` with kernels `H_o,H_r`, the exact covariance is

```text
Cov(Y_o,Y_r) = 4 sum_(i<j) H_o,ij H_r,ij.                  (9)
```

Independent probes divide (8)--(9) by `P`.  Independent layer streams add
layer covariances; reusing one stream across layers instead requires summing
the layer kernels before applying (8).  M126 does not freeze this seed/stream
choice.

A width-6 exhaustive-sign check of a random shared path-plus-collision linear
functional matched (7) samplewise to `3.34e-16`, its mean to `2.78e-17`, and
its variance to `1.39e-17`.  In that case, summing entrywise variances while
ignoring covariance was `2.063x` the exact response variance.  Across 128
generated functionals, the naive/exact ratio ranged from `0.209` to `5.415`
with median `0.839`; 76 underestimated and 52 overestimated.

Therefore a frozen output-level functional or equivalent full covariance
propagation is a binding promotion gate.  Eight realized probes alone cannot
certify it after the fact.

## 8. Cost audit

At width 256 the installed convention gives

```text
M32 = 2*256^3 - 256^2 = 33,488,896,
M64 = 2*M32            = 66,977,792.
```

A native FlopScope 0.10.0 microtrace confirmed one float32 square GEMM has
dtype `float32` and bill `33,488,896`.

### Why the theoretical count is 24, not 25

A literal reading of `collision_repeated_exact` appears to require four k3
collision GEMMs, including `(d3*W^2)^T W`.  The claimed three-call target
schedule is nevertheless algebraically valid by fusing two terms:

```text
E3W                                             one GEMM
(W^2)^T(E3W)                                   one GEMM
[d3*W^2 + 2 W*(E3W)]^T W                      one GEMM.     (10)
```

Equation (10) matched the unfused expression to `2.84e-14` on generated
arrays.  Thus the theoretical exact schedule is

```text
tree blocks             12 square-call equivalents/layer
collision blocks        12 square-call equivalents/layer
                         --
                         24
```

The companion NumPy code does not perform (10), so 24 is a feasible fused
schedule, not a trace of the delivered code.

Each shared probe adds two path and two `[2,2]` GEMMs.  With the declared
`7.2B` raw reserves and one `1.25` factor,

```text
C_source(P,d) = 1.25 [31(24+4P) M_d + 7.2B].                (11)
```

At `P=8`, independent arithmetic reproduces:

| worksheet | protected FLOPs |
|---|---:|
| float64 M126 source | `154.341808640B` |
| float32 M126 source | `81.670904320B` |
| quoted protected M125b | `12.819347280B` |
| **quoted float32 P8 + M125b** | **`94.490251600B`** |

So `94.490251600B` is not an addition error.  The separate M125b independent
judge found that its direct native carrier/background realization is
`12.819202000B` after the same reserve; substituting that trace gives
`94.490106320B`.  The quoted M125b number is slightly conservative because it
charges an extra source insertion while omitting diagonal-write cost.

Neither sum is an integrated trace.  M126 has no native fused source, and the
exact endpoint-aware M125b `K,Hmu,Hv` builder is still untraced.  Pointwise
work, source construction, random-stream handling, memory, and residual call
overhead remain represented only by reserves.

## 9. Float32 parity gates

The gates are technically implementable on the installed CPU stack, but not
implemented in M126.  Every validator currently coerces inputs to float64,
and `flopscope_ledger(dense_gemm_dtype="float32")` merely changes arithmetic
in a dictionary.

An independent generated width-256, `P=8` prototype used true float32 GEMMs,
immediate float64 promotion/accumulation, and same-input float64 references.
Across 57 exercised GEMMs:

```text
max [ |C32-C64| / {4 gamma_256 (|X|^T|Y|)+tiny} ] = 0.01962

relative Frobenius parity:
K3     4.49e-7
K31    5.29e-7
K22    1.93e-7

random frozen response relative difference        1.94e-6
```

This proves that the proposed checks can be computed and that one ordinary
generated case is numerically benign.  It does not establish a gate:

- the production fused association must be tested, not the unfused reference;
- `tiny`, absolute envelopes, Frobenius tolerances, condition cutoffs, and
  failure policy have no frozen numeric values;
- cancellation makes a relative-only response threshold invalid;
- final symmetry must be enforced and billed;
- target-shape peak memory and residual wall time are unmeasured.

The correct status is therefore **REPAIR**, not float32 PASS.

## 10. Orthogonal Hadamard probes

At `n=256`, take `P` distinct rows without replacement from a Walsh-Hadamard
basis and randomize columns by independent signs (plus a frozen row
permutation).  Every marginal probe is Rademacher, the rows are orthogonal,
and the complete `n`-row population has average outer product `I`.

For every fixed scalar quadratic functional, sampling `P` rows without
replacement multiplies the iid-probe variance by the exact finite-population
factor

```text
(n-P)/(n-1).
```

At `n=256,P=8`, this is `248/255=0.972549`: a `2.745%` variance reduction at
the same four-GEMM-per-probe leading cost.  A width-8 exhaustive signed-basis
check reproduced the factor exactly.  This is a valid, modest mutation worth
preserving.

Using all 256 rows is exact for every quadratic table, but the protected
float32 source worksheet becomes about `1.369T` before M125b.  Orthogonality
does not turn exact recovery into a budget-feasible method.

## 11. Edge sampling: material clue, not a passed child

Exact enumeration of all `32,640` residual edges for both operators restores
quartic work.  The leading protected float32 hard-edge work is approximately
`829B` before easy source terms and M125b, so exact edges are not a solution.

The report's independent-Bernoulli Horvitz--Thompson formula is unbiased, but
it controls only expected sample count.  Under a hard FLOP cliff, the realized
count can range up to all edges.  Capping it introduces bias.  A deployable
mutation needs a fixed-count design.

One such repair is fixed-`k` sampling with replacement.  If edge `e` is drawn
with frozen probability `q_e`, then

```text
T_hat = (1/k) sum_s F_(e_s)/q_(e_s)
```

is unbiased and has exactly `k` updates.  At equal leading float32 arithmetic
to `P` four-GEMM probes, choose approximately

```text
k_Q = k_22 = 0.8 P n.
```

For `P=8,n=256`, this is about 1,638 sampled edges per operator per layer.

A twelve-seed generated screen at `n=m=64`, `P=8`, and matched `k=410`
compared full source-table Frobenius MSE:

| fixed-count edge proposal | MSE / Rademacher-P8, range | median |
|---|---:|---:|
| uniform | `0.744 .. 1.078` | `0.919` |
| oracle `q_e proportional ||F_e||_F` | `0.157 .. 0.343` | `0.204` |
| cheap frozen norm upper-bound proxy | `0.169 .. 0.364` | `0.216` |

The cheap proxy used

```text
D_i[a,b] = gamma2_i (A_ia W_ib + W_ia A_ib),

q^path_ij proportional |E_ij| ||D_i||_F ||D_j||_F,
q^22_ij   proportional |E22_ij| ||W_i||^2 ||W_j||^2.
```

It needs only row norms and all-edge scalar weights, rather than exact output
matrices.  This is a material generated clue: importance edges may dominate
plain P8 source-table Frobenius error at matched arithmetic.

It is not a promotion result.  The screen is small-width and ensemble-specific,
uses source-table Frobenius rather than the complete M125b output functional,
omits `[2,1,1]`, and does not price categorical sampling, batched update
layout, allocation, or the very high update-call residual.  Preserve it as a
separately named mutation with fixed-count unbiasedness and the output-level
gate from Section 7.

## 12. Required repairs

1. Choose the source contract explicitly: M124 reduced collisions or exact
   M122 including `[2,1,1]`.  Do not switch names after a result.
2. Implement the fused 24-call source in FlopScope, including (10), explicit
   symmetry, probe averaging, float64 accumulation, and all pointwise work.
3. Reject nonzero diagonals in `majority3`, `majority4`, and `paired4`.
4. Freeze numeric float32 thresholds, `tiny`, stream ownership across layers,
   P, seeds, association order, and failure policy before running any gate.
5. Build the complete response-level kernels/covariances (7)--(9), or an
   equally strong predeclared output-level variance certificate.
6. Trace peak memory, residual wall time, call count, and worst-case billed
   FLOPs in one generated target-shape process.
7. If pursuing edges, use fixed-count unbiased sampling and a blocked/batched
   implementation; test the cheap importance proxy against orthogonal P8 on
   the same output functional and cost.

## Final disposition

Preserve the exact cubic algebra, correct orbit ledger, symmetric hard-path
probe, `[2,2]` estimator, twelve-slot oracle, output-functional formula,
Hadamard finite-population improvement, and fixed-count importance-edge clue.

Do not promote M126, do not call it an exact M122 source, and do not infer
accuracy from `94.490251600B`.  The component verdict is
**PASS_COMPONENT**; the candidate verdict is **REPAIR / BLOCKED**; the exact
source and cost-only promotion claims are **KILL**.

## Stable evidence hashes

| artifact | SHA-256 |
|---|---|
| `m126_repeated_output_contractions.py` | `f0462b96e7f898812d39b7a39f458f965835523f2a4c7a509c43f62dc7c1011c` |
| `test_m126_repeated_output_contractions.py` | `7c78c5b61bb17ffe19f36bf40c6e72b0cf559b33a4b62eaeea818b7120f620fc` |
| M126 theory report | `0695954233060b8aa452781d8960a7f9662cbee9643bb94a400f88a9a7235846` |
| M125b independent judge consumed for the combined worksheet | `f975c4c115ac1b331ddfa47267f840f5d1fa797ebbac752de5aebad922856020` |
| FlopScope initializer | `f49c7b804649223c077505a3380a6fb2baa691e783564be433543fa0ae6f1b06` |
| FlopScope default weights | `9ff1647a0048d2bd23a7a3d76ee0c60bfd3670d03b15ad8bf2b911c2ae19539f` |
| FlopScope dtype billing | `a73a31f495010b462b2053ef4a9881376fcde1d29a2cd488c8adcf9719d46572` |
