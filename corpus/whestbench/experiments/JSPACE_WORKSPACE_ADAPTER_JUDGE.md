# Independent mathematical/statistical judge: JSpace adapter

Date: 2026-08-06

## Verdict

The cleanroom VJP algebra is correct, the reported synthetic numbers reproduce,
and `E[J^T J]` is a legitimate cancellation-resistant input-sensitivity
operator. The combined candidate is nevertheless **not promotable**.

The current implementation is only an input-to-output (`l=0`) workspace. It
does not implement the layerwise `D_l` bank described by JSpace or by the
adaptation note, and its declared hidden-gauge/estimated-Gram symmetry gate was
not actually exercised. The signed-pursuit implementation also misses its
predeclared materiality gate. Therefore:

- **killed implementation:** current signed pursuit as a material estimator
  component;
- **preserved component:** fresh-probe Hutchinson estimation of the PSD
  input-workspace `G_0=E[D_0^T D_0]`;
- **unresolved family:** layerwise, gauge-normalized, residual-relevant
  workspaces;
- **status:** screened diagnostic survivor, not a validated estimator child and
  not a competition winner.

No official MLP, truth, scorer, API, or private seed was used in this audit.
The builder files were not changed. The inspected builder hashes were:

```text
jspace_adapter.py       0EA3A9A0FD9E653DCEF8761C59CFAA21965CC461A802B3E66D327CF78AEBCFCA
test_jspace_adapter.py  1CC41BACEEE537E41A994B73BBE5CA50C5E1F639A85AC7ED7C753683F7489D3A
run_premise.py          A04B7F803CBDC67BD5E813BABFC999E97F5E575A8A08BB10062A97173799039F
premise_results.json    B82640FAA8CD3E22224AEE5CA4EB4857E5C3B37E5FBB9F7431473CD605D0F3EE
REPORT.md               F0BE0C1E3ED806630F8734B9A6D1749A02D9B290F57CDF1E51D4031ED0E620F1
PREDECLARED_GATE.md     BE20EF169271A187AA7D6C5160945F8B29134507364F9F6F9F0B2420B1430943
```

## Exact dense formulas and orientation

Use the row-forward convention in the adapter:

```text
h_0 = u
z_r = h_(r-1) W_r
R_r = diag(1[z_r > 0])
h_r = h_(r-1) W_r R_r,                 r=1,...,L.
```

For a fixed gate pattern, a row perturbation at layer `l` propagates through

```text
A_l(u) = W_(l+1) R_(l+1) ... W_L R_L.
```

The conventional output-by-state Jacobian is therefore

```text
D_l(u) = A_l(u)^T
       = R_L W_L^T ... R_(l+1) W_(l+1)^T.
```

The two exact empirical workspaces on states `u_s`, `s=1,...,S`, are

```text
M_l = (1/S) sum_s D_l(u_s),
G_l = (1/S) sum_s D_l(u_s)^T D_l(u_s).
```

For an output Rademacher probe `v` with `E[v v^T]=I`, reverse recurrence gives

```text
g_L = v,
g_(r-1) = W_r R_r g_r,
g_l = D_l^T v.
```

Consequently the unbiased estimators are

```text
E_v[v g_l^T | u] = E[v v^T] D_l = D_l,
E_v[g_l g_l^T | u] = D_l^T E[v v^T] D_l = D_l^T D_l.
```

Thus `outer(v,g)` has the correct output-by-state orientation. Reversing the
outer product estimates `D_l^T`, not `D_l`. The builder generates probes inside
the sample loop, so probes are fresh across samples; the nested `K` prefixes
are correlated across reported rungs but remain unbiased.

An exhaustive check over all `2^5` Rademacher probes at width 5 found maximum
absolute errors `4.44e-16` for the signed identity and `1.33e-15` for the
energy identity. The five supplied unit tests also pass independently.

## Independent reproduction

Recomputing all 12 networks from the frozen seeds without invoking
`run_premise.main()` reproduced the report exactly:

| Quantity | Reproduced value |
|---|---:|
| Median `||EJ||_F^2 / E||J||_F^2` | 0.10278713875026457 |
| Range | 0.018385411938323805 to 0.24139556314540186 |
| Networks below 0.75 | 12/12 |
| K=16 median Gram relative error | 0.04090130858236782 |
| K=16 worst Gram relative error | 0.07925882069903932 |
| Nonnegative pursuit successes | 1130/1152 |
| Signed pursuit successes | 1152/1152 |
| Median network residuals, nonnegative/signed | 0.04220575 / 0.03854867 |
| Signed residual reduction | 8.6649% |

The cancellation premise is real at this toy shape. The signed-pursuit effect
is also correctly reported as below both frozen materiality alternatives (20%
residual reduction or 10 percentage-point success increase).

## Adversarial findings

### 1. The adapter is input-only, not layerwise

`exact_workspaces` always builds the complete input-to-output Jacobian, and
`hutchinson_workspaces` retains only the final input VJP. There is no `l`
argument, no intermediate response bank, and no adjacent-depth spectrum. The
hidden-permutation test compensates two hidden weights and then confirms that
the *full input-output function* and `D_0` are unchanged. That is correct but
does not test how an intermediate `D_l` transforms.

The report's 2.813B operation count is valid as a conservative arithmetic
count for the proposed **input-direction** S=128, K=4 signed-plus-energy pilot.
It cannot support a claim that all 32 layer workspaces or a depth band were
scanned. Such a scan is not present in the code.

### 2. The predeclared symmetry gate was only partially implemented

For a hidden permutation `P` and positive diagonal gauge `S`, with row states
`h_l' = h_l P` or `h_l' = h_l S`, the downstream operators obey

```text
D_l' = D_l P,                    G_l' = P^T G_l P,
D_l' = D_l S^(-1),               G_l' = S^(-1) G_l S^(-1).
```

The raw energy Gram is permutation-equivariant but is not invariant to the
legal positive hidden-neuron rescaling. Its eigenvalues can change under that
congruence. If `C_l=E[h_l h_l^T]`, then

```text
C_l' G_l' = S (C_l G_l) S^(-1),
```

so the eigenvalues of `C_l G_l` (equivalently a properly whitened
`C_l^(1/2) G_l C_l^(1/2)`) are gauge-invariant. A numerical width-5 audit left
the represented network bit-identical, changed the raw intermediate Gram by
1.095 relative Frobenius norm, and preserved the generalized spectrum to
`2.22e-15`.

The supplied `positive_scale` check instead multiplies the input radius and
tests ReLU homogeneity. It does not test a hidden gauge. The transformed
Hutchinson estimates are not tested either: only exact workspaces are compared
under coordinate transformations, while estimated workspaces are checked for
deterministic replay. Therefore the literal predeclared requirement that all
exact/estimated Grams pass hidden/permutation/positive-scale tests is unmet.

Also, a generic fixed ReLU network has positive diagonal and permutation
hidden gauges, but no hidden **sign** gauge: `ReLU(-z) != -ReLU(z)`. Signed
pursuit remains a sensible comparator because VJPs themselves are signed, not
because of a nonexistent ReLU sign symmetry.

### 3. Greedy pursuit is not an identifiable minimum-capacity estimator

Both upstream and cleanroom pursuit are matching pursuit without a joint
NNLS/least-squares refit. Correlated atoms can be selected repeatedly, and the
iteration count is then not the number of distinct concepts. Tracing the
frozen cleanroom bank found:

| Mode | Queries with a repeated atom | Repeated selection steps |
|---|---:|---:|
| Nonnegative | 101/1152 | 518 |
| Signed | 13/1152 | 15 |

A three-dimensional counterexample also refutes the docstring's “find the
minimum k” wording. Let

```text
q = (1,1,0)/sqrt(2),
c = 0.9 q + sqrt(0.19) e_3,
dictionary = {c,e_1,e_2}.
```

The query has an exact nonnegative two-atom representation `q=(e_1+e_2)/sqrt(2)`.
Greedy pursuit selects `c,e_1,e_2`, stalls at only 84.61% coverage, and misses
the exact support. Minimum conic support generally needs conditions such as a
spark/coherence/RIP bound; none is established here. Corpus/query separation
does not cure dictionary non-identifiability.

The pursuit measurements remain useful as path-length diagnostics. They must
not be called minimum sparse capacity unless repeated atoms are forbidden,
selected coefficients are jointly refit, and held-out support stability and
dictionary coherence are reported.

### 4. K=4 and top-8 are exploratory

The frozen accuracy gate was at K=16. K=4 was selected from the same projection
curve after observation, so it is a promising cost point, not independently
validated. The top-8 overlap uses an 8-dimensional subspace in dimension 16;
its random-subspace expectation is already `8/16=0.5`. Values near 0.996 are
still strong (the observed lambda-8/lambda-9 gaps were nonzero), but this is a
weakly discriminating toy geometry and cannot establish rank-8 recovery at
dimension 256. A fresh bank should predeclare K=4 and report principal angles,
spectral gaps, and downstream residual prediction.

### 5. Sensitivity is not yet relevance to the estimand

`G_0` measures average squared local sensitivity of the full directional
function. The deployed spherical 5-design has already removed degrees 0 through
5. There is no result here showing that the leading full-function sensitivity
directions predict the remaining even degree-6-and-higher integration error.
Indeed the existing active-subspace bound warns that capture of a pure
degree-6 residual can scale as `(r/d)^6`. This missing error link, not Gram
estimation accuracy, is the binding scientific gate.

## Upstream source claims and transfer limits

The pinned upstream commit is
`54089367f887dde0b076d99bba71d053b67d70ac`. The VJP outer-product orientation
is correct and one fused backward can expose VJPs at all hooked layers.

Two upstream claims require qualification:

1. `_process_all_layers_fused` averages target positions only over the second
   half, then averages gradients over all source positions. It estimates
   `1/(T |Q|) sum_t sum_(t' in Q,t'>=t) D_(t,t')`, not the advertised uniform
   average over all valid `(t,t'>=t)` pairs. At the final identity layer this
   convention yields a scale proportional to `I/T`. Later normalization may
   hide a global scale, but it does not make the stated weighting exact.
2. The repository contains no test tree at the pinned commit, and the results
   text referenced by the README is absent. “Paper-exact” and reported language
   workspace findings are upstream claims, not source-audit conclusions.

The language/token cone gives upstream nonnegative pursuit a semantic story.
WHestBench has no vocabulary, token positions, unembedding, or transformer
residual stream, so none of those phase/workspace conclusions transfer.

## Deployment cost and memory gates at n=256, L=32

Judge-side gates were fixed before ingesting the builder metrics:

- hard competition safety: total billed cost, including the parent, setup,
  elementwise operations, copies, and residual-time charge, must be at most
  `0.98 * 2.72e11 = 2.6656e11`;
- current local mutation envelope: from a 70.59013632B parent inside the 80B
  campaign envelope, spend at most 80% of the 9.40986368B remainder, i.e.
  **7.527890944B** incremental billed operations;
- peak incremental working storage at target shape at most **1.5 GiB**;
- never materialize an `S x L x n x n` Jacobian bank in deployment;
- a layerwise claim requires actual `D_l`/`g_l` outputs and gauge-normalized
  tests; an input-only result may be labeled only `G_0`.

With `c_f=c_v=L(2n^2-n)`, the builder's input-only signed-plus-Gram formula is

```text
C_input(S,K) = S [c_f + K(c_v + 4n^2)].
```

At S=128,K=4 this is **2,813,329,408**, which fits the incremental arithmetic
gate. It is slightly conservative for two batched outer-product matmuls, but it
is not a full FlopScope certificate: eigensolves, RNG, mask handling,
normalization, copies, allocation, precision multipliers, and residual wall
time still need to be charged.

If signed and energy matrices were accumulated at every one of 32 layers, the
same approximation becomes

```text
C_all_layers = S [c_f + K c_v + 4 K L n^2]
             = 6,974,078,976                 (S=128,K=4),
```

before overhead. The code does not perform this computation. Two float32
layerwise matrix banks use about 16 MiB, but materializing every dense
sample/layer Jacobian would use 1 GiB at S=128 (2 GiB in float64) before any
other state and is forbidden by the memory gate. Streaming VJPs are the viable
form.

## Recursive salvage map and next falsifier

Preserve the exact VJP/energy identity, but change the failed mechanisms rather
than retuning thresholds:

1. **Gauge repair:** for any intermediate layer, estimate `C_l` with `G_l` and
   use the generalized/whitened spectrum. Test the estimated covariance law
   under hidden permutations and positive diagonal gauges, not merely input
   homogeneity.
2. **Probe repair:** compare K=4 iid Rademacher probes with a randomized
   without-replacement Hadamard row block. Each marginal still has
   `E[vv^T]=I`; negative dependence may reduce Gram variance at equal VJP cost.
3. **Pursuit repair:** count distinct atoms, prohibit cycling, jointly refit
   selected coefficients (signed least squares or NNLS), and predeclare a
   coherence/support-stability gate. Keep the present iteration count only as a
   path-length observable.
4. **Relevance repair:** estimate a design-residualized energy operator, not the
   full-function `G_0`. Freeze four cells on fresh networks: no control,
   isotropic directions, signed-mean directions, and whitened energy
   directions. Fit on a disjoint pilot and judge only matched degree-6+
   residual error and total billed score.

Promote only if the energy-direction cell beats isotropic and no-control with a
predeclared paired confidence interval below parity, zero resource failures,
and the full cost ledger. A failure there kills only this residual-link
implementation; the exact Hutchinson operator remains reusable for other
conditioned or multilevel observables.
