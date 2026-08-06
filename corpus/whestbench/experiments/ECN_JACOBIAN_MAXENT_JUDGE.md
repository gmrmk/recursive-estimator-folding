# Independent adversarial math/statistics judgment

## Disposition

**FAIL as a deployable ECN/Jacobian/optimization-prior compressor.**

**PASS as a deterministic synthetic result showing that one particular
target-free soft partition beats its generic comparator on the generator that
was constructed for it.**  The full ladder implementation remains a correctly
recorded `killed implementation`.  Failure is local, but it is not localized
as narrowly as the builder claims: the failed boundary is the
`ladder-feature <-> surrogate-metric` interface, with attenuation only one
possible cause.

The no-ladder branch is statistically convincing *inside this frozen synthetic
ensemble*, but it is not a screened competition survivor: its ratio is
`0.91147`, not `<=0.80`; its metric is not the claimed analytic observable
Jacobian; and the target cost uses an unsupported component count.

I did not modify or run any residual-skip implementation.

## Independent reproduction

- All manifest entries match the current files.
- Gate SHA256: `253d1de490e129a3d788fddfe07e4bfba51ea885a63560291fb53dd9db3cdd28`.
- Frozen implementation SHA256: `f0bb3eba809483dff9f76e8d9add616ee1898280af876d27e240a8e129f26333`.
- Builder result SHA256: `7145e35265119b59549419699686bc3c0ffd5921e5c258fb35ebc5b8a9f812ba`.
- An independent full rerun produced the same result hash byte for byte.
- The six builder tests independently pass.
- File times are consistent with gate -> implementation manifest -> result ->
  report order.  This is good provenance hygiene, though ordinary timestamps
  are not a cryptographic proof of chronology.

## Claim-by-claim verdict

| Claim | Verdict | Independent finding |
|---|---|---|
| Hashes and reported aggregates are reproducible | **PASS** | Full rerun is bit-identical. |
| Routing reads no analytic truth/reference | **PASS, narrow** | Replacing `exact_observable` by arbitrary million-scale values changes RMS only; assignments and predictions are bit-identical. |
| The synthetic result is independent evidence for WHest | **FAIL** | The generator makes final means/scales from the same gate/active trajectories given to `psi`. This is a favorable premise, not competition validation. |
| `psi` is an analytic observable-Jacobian pullback | **FAIL** | The implemented active feature is not log scale, and the same derivative matrix is applied to semantically different ladder coordinates without a chain rule. |
| Pullback distances are finite, symmetric, nonnegative | **PASS** | Direct rerun and eigenvalue checks pass. This establishes an SPD surrogate metric, not its Jacobian interpretation. |
| Component and coordinate-permutation equivariance | **PASS** | All 32 seeds and all four methods: maxima `4.44e-16` and `5.55e-16`. |
| Positive coordinate-gauge covariance | **PASS independently** | Not actually tested by the builder's named “coordinate gauge” test, which is a permutation. Independent positive diagonal rescalings over all 32 seeds give maximum relative error `1.10e-15`. |
| `tau` solves balanced entropy-regularized transport | **PASS** | Sinkhorn row/column constraints hold; maximum independently reconstructed assignment/coupling residual is `2.04e-13`, below `2e-10`. |
| `tau` implements a Młynarski optimization prior | **FAIL** | There is no stated `q(theta) exp(beta U)/Z`, utility calibration, beta inference, beta-null/hard-max comparison, or uncertainty audit. |
| MaxEnt contributes something beyond soft clustering | **FAIL as phrased** | It is exactly deterministic balanced entropy-regularized soft k-medoids with center/farthest prototypes. “Entropic OT” is accurate; “optimization prior” adds no implemented mechanism. |
| `epsilon=1` is fixed without reference leakage | **PASS, qualified** | It is target-free, but raw effective temperature is instance-adaptive because costs are divided by their current median. |
| Sinkhorn uses a frozen iteration count | **FAIL** | Code stops adaptively every 10 iterations, observed range 20--60, with a possible maximum of 5,000. The cost ledger charges 64. |
| Assignments do not collapse on these data | **PASS empirically** | Median mutual information is `0.174` nats no-ladder and `0.156` ladder (15.8% and 14.2% of `log 3`); routing is soft but nonzero. |
| The hard-rank criterion generally certifies noncollapse | **FAIL** | Near-uniform rows with tiny cyclic perturbations have balanced argmax occupancy and rank 3 while mutual information tends to zero. The present criterion is not a certificate. |
| Medoids are unambiguous on the frozen ensemble | **PASS** | Minimum recorded relative gap `1.72e-5`; all are distinct. Selection is unweighted, which is harmless only because current weights are equal. |
| `phi` preserves total moments and PSD | **PASS in frozen shape** | Maximum mean/covariance residuals `3.30e-14`/`3.64e-14`; minimum bin eigenvalue `0.512875`; no repair used. The total-moment algebra is correct. |
| `phi` is an exact general decoder | **FAIL** | It hard-codes `K_COMPONENTS=48`, `DIM=6`, and `Q_BINS=3`. A valid 8-component input raises `IndexError` at index 8. Any eigenvalue repair also makes literal equality only tolerance-exact. |
| Aggregate ratio is computed correctly | **PASS, with spec warning** | Reported values are ratios of pooled coordinate RMS, equivalently `sqrt(mean unit_MSE_candidate / mean unit_MSE_generic)`. The gate's “per-unit ... divided” wording is ambiguous, but mean/median/geometric unit ratios give the same disposition. |
| No-ladder 32/32 wins are statistically meaningful | **PASS internally** | One-sided paired sign `p=2^-32=2.33e-10`; whole-state bootstrap 95% interval for pooled ratio `[0.8942,0.9291]`. This is not external validation and still misses the 0.80 gate. |
| Ladder 30/32 wins establish material improvement | **FAIL primary effect** | Sign `p=1.23e-7`, but pooled ratio is `0.93361`, bootstrap 95% `[0.9196,0.9478]`, far above 0.80. |
| Ladder failure is localized only to attenuation | **FAIL** | No-ladder vs ladder changes feature semantics, while the metric still assumes final gate/log-scale coordinates. Attenuation and metric-interface mismatch are confounded. |
| Contrast recovery validates the ladder information path | **FAIL as evidence of usefulness** | `2*(left-right)=pre_left-pre_right` is an algebraic identity. The recovered value still contains longitudinal memory and is not the raw final gate-active contrast. |
| Projected target cost is conservatively `<80B` | **FAIL** | The ledger assumes 8 routed components without derivation, while the frozen synthetic test uses 48 and the Haar+chi2 q3 expansion has `K=4qn=3072`. |

## Statistics and aggregation audit

Independent values from the 32 matched whole-state units:

| Method | Pooled ratio | Mean unit ratio | Median unit ratio | Bootstrap 95% | Wins |
|---|---:|---:|---:|---:|---:|
| scalar dual | 1.004208 | 1.004477 | 1.001727 | [1.0019, 1.0068] | 8/32 |
| Jacobian-named, no ladder | 0.911472 | 0.914201 | 0.922277 | [0.8942, 0.9291] | 32/32 |
| Jacobian-named + ladder | 0.933606 | 0.936736 | 0.939502 | [0.9196, 0.9478] | 30/32 |

The units are correctly whole synthetic instances; the 48 components and six
coordinates are not falsely counted as independent sign-test observations.
The no-ladder effect is robust on this generator and should be preserved as an
internal premise. It is an 8.85% pooled improvement, not the required 20%.

## Reference and utility leakage audit

`build_geometry`, medoid selection, cost median, `epsilon`, Sinkhorn, and the
decoder do not access `exact_observable`. The output prediction is invariant
when that reference is replaced. There is therefore no direct reference leak.

There are two important limitations:

1. The ensemble itself is target-aligned. `alpha_out` and `log_scale` are made
   from gate/active memories, and those trajectories are supplied to the
   candidate. That is legitimate for a synthetic premise but makes the result
   unsurprising and weak as external evidence.
2. No Młynarski-style utility is implemented. The local source note requires a
   stated base measure, target-free utility, beta comparison/calibration, and
   fresh-seed risk curve. None appears in code or results. Sinkhorn's Gibbs
   kernel can be described as a constrained maximum-entropy coupling, but that
   is not the paper's optimization-prior analysis.

## The Jacobian claim fails mathematically

For a marginal written as `z=sigma(alpha+epsilon)`, define

```text
h(alpha)=alpha Phi(alpha)+phi(alpha),
E relu(z)=sigma h(alpha).
```

The exact derivatives with respect to `(alpha, ell=log sigma)` are

```text
d/dalpha = sigma Phi(alpha),
d/dell   = sigma h(alpha).
```

The code instead uses final features `[Phi(alpha), active_response]`, sets
`sigma_hat=exp(active_response)`, and treats the active-response coordinate as
`log sigma`. It is not. Across the 32 frozen instances:

- median relative `||sigma_hat-sigma||/||sigma||` is `35.7%`
  (range 31.3%--39.6%);
- `sigma_hat/sigma` ranges from `0.482` to `3.135`;
- active response versus actual log scale has median correlation `-0.397`
  (range `-0.547` to `-0.251`).

For the ladder method the mismatch is stronger: its raw coordinates are
`[consensus, recovered_precontrast]`, but the same gate/log-scale derivative
matrix is applied after only a robust scale change. There is no derivative of
the observable through the ladder map. `J.T J + delta I` is SPD, but it is a
heuristic metric, not an analytic pullback Jacobian.

## Sinkhorn and decoder audit

The coupling is the solution of balanced entropic soft clustering with the
clipped standardized cost. Its constraints and current medoids pass. The
builder should rename the mechanism accordingly and report an information
criterion such as mutual information, not hard argmax occupancy alone.

The total-moment decoder identity is sound for normalized weights, nonnegative
row-normalized assignments, positive bin mass, and the frozen array shape. PSD
follows because each bin covariance is a weighted within-plus-between
covariance. The reusable claim needs qualification:

- array sizes are global constants, not inferred from inputs;
- Sinkhorn rows are only numerically normalized;
- clipping a tolerated negative eigenvalue perturbs the reconstructed raw
  second moment, albeit by the clipping tolerance;
- the target 8-component assumption is incompatible with the present decoder.

Thus `phi` is a passed algebraic component and a failed deployment artifact.

## Cost counter-audit

The recorded arithmetic is internally reproduced:

```text
parent                  70,590,136,320
claimed compressor          2,502,656
claimed total           70,592,638,976
```

But the claim is not conservative. It assumes `K=8`; neither the synthetic
experiment (`K=48`) nor the randomized-radial expansion supports that number.
For the actual steady Haar+chi2 child cloud,

```text
K = 4 q n = 3072,  p = 2n = 512.
```

Using the builder's own `4 K^2 p` geometry formula gives

```text
geometry                19,327,352,832
64-step transport            4,718,592
builder decoder               2,359,296
projected total          89,924,567,040  (>80B by 9.925B).
```

Worse, `pairwise_metric_distances` materializes a `K x K x p` float64 delta
array: about **38.65 GB** at target shape. The ledger also omits robust median
selection/sorting, feature construction through depth, covariance accumulation,
eigendecompositions, allocation/wall cost, float64 billing, and the possible
5,000 Sinkhorn iterations. The `<80B` gate therefore fails unless an upstream
proof reduces the routed set to at most eight components before this operator;
no such proof is present.

## Flatworm failure locality

The paired evidence does prove that the complete *implemented ladder feature
map* is worse than the no-ladder feature map: it loses 27/32 head-to-head and
has a 2.43% RMS penalty. It does not prove that longitudinal attenuation itself
is the unique cause. The methods differ in all of these linked semantics:

- final response versus depth-smoothed response;
- active lane versus recovered lane contrast;
- a metric derived as if both representations meant gate/log scale;
- feature scale and consequently the regularizer.

The correct status is:

```text
killed implementation: fixed ladder + mismatched surrogate metric
passed component: exact consensus/contrast algebra
unresolved family: attenuation under a chain-rule-correct metric
```

This preserves failure locality without granting an unsupported causal story.

## Residual-skip judgment

A frozen residual skip is potentially a **causally novel topology change**, not
mere parameter drift, because it restores a direct final-feature information
path alongside the depth memory. It is admissible only if all of the following
are frozen before fresh seeds:

1. no learned blend coefficient or result-selected block weight;
2. a correctly dimensioned metric for the direct and ladder blocks;
3. a comparator against the no-ladder parent, not only generic q3;
4. proof that any gain is not simply reversion to the already-better no-ladder
   representation;
5. an actual target-shape cost/memory bound.

Appending final features and reusing the present 12-dimensional surrogate
metric would be a shape/semantic error. Tuning a skip coefficient on these 32
units would be parameter drift. The proposed mutation is therefore
**conditionally admissible but not ready to run**.

## Exact next admissible mutation or stop

**Stop the residual-skip ladder until `psi` and target cost are repaired.** The
next single-mechanism accuracy mutation may change only `psi`, on a fresh seed
band, while holding `tau`, `phi`, q3, and the no-ladder topology fixed:

1. Use actual component coordinates
   `theta=[alpha, ell]`, with `ell=0.5 log diag(C)`.
2. Use the exact Jacobian blocks
   `J_alpha=diag(sigma Phi(alpha))` and
   `J_ell=diag(sigma h(alpha))`.
3. Verify them by central finite differences before accuracy is read.
4. For components `i,j`, use the symmetric local pullback
   `Delta^T (G_i+G_j) Delta / 2`, with only a predeclared numerical ridge.
5. Make decoder loops shape-generic and run Sinkhorn for exactly 64 iterations,
   failing rather than silently extending if marginals miss tolerance.
6. Before any accuracy run, resolve the routed component count. If it is
   `4qn`, dense all-pairs transport is stopped; a separately gated streaming
   `O(K q p)` transport mutation is required.
7. On fresh whole-instance seeds, require the original `<=0.80`, 24/32 gate
   and compare against both generic and the frozen no-ladder surrogate.

Only if that corrected no-ladder rung survives may a zero-coefficient residual
skip be added as a new generation with a factorial interaction test. If the
exact-Jacobian rung does not retain the synthetic advantage, preserve entropic
transport and total-moment decoding, locally kill this `psi`, and stop the ECN
ladder family rather than tuning its constants.
