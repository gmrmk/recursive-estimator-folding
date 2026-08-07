# M146 independent hostile pre-execution audit -- 2026-08-07

## Verdict: REPAIR

**Do not implement the frozen premise as written and do not run an efficacy,
development, confirmation, response, or contest cell.**  The central adaptive
Hansen--Hurwitz theorem is correct, the three-bank law is algebraically
factorable, and the pilot coefficient magnitude is a genuinely new observable.
Those passed components justify repair rather than killing the operator.

The frozen executable contract is nevertheless incomplete at three binding
boundaries:

1. no generated-state constructor or endpoint-safe M131 certificate path is
   frozen;
2. no executable role-aware sampler, heterogeneous-phase five-product scatter,
   or exact definitions of two efficacy gates are frozen; and
3. the `97.692352720B` worksheet has no kernel-level non-overlap proof and puts
   a serial pilot barrier behind only 25 ms of incremental wall reserve.

The first problem is now concrete rather than hypothetical.  M143's audited
one-shot generated run failed before producing an outcome because
`m122_nonzero_bridge.NonzeroBridgeFailClosed` rejected a pair near a Gaussian
endpoint.  M146's widths 12--32 cannot use M129's `build_state_frechet` at all,
because its M122 constructor accepts width at most eight.  The width-capable
M131 `build_zero_sampling_frechet` avoids that width limit, but its downstream
pair/triple Hermite routines still refuse any selected raw correlation with
absolute value above `.80`.  The manifest does not say which constructor it
uses and does not define the generated means/covariances.  Reusing M143's
propagated chain can therefore reproduce the same fail-closed boundary.

This audit performed no premise or efficacy run and created no authorization.

## 1. What passes exactly

### 1.1 Adaptive-pilot unbiasedness

For ordered distinct triples `e=(i,j,k)`, put

```text
G_e = Delta_e F_e,
T   = (1/2) sum_e G_e.
```

Let the `P` pilot draws be iid from `q0`.  Let `F_P` contain the complete
ordered pilot, its exact sampled coefficients, feature norms, and the fitted
`q1`.  Conditional on `F_P`, every one of the `M=K-P` main draws has law `q1`,
so

```text
E[G_E/(2 q1(E|F_P)) | F_P] = T.
```

The same identity under `q0` holds for every pilot draw.  Therefore

```text
T_hat = (1/K) [sum_pilot G_e/(2q0(e)) + sum_main G_e/(2q1(e|pilot))]
```

is unbiased.  Reusing pilot integrand values to fit the future proposal does
not introduce bias.  The proof depends on the manifest's fixed `P`, fixed `K`,
ordinary (not self-normalized) HH denominators, and prohibition on using a main
draw to fit the proposal that scores that draw.

The denominator and scale are also correct for the vector target.  M133 samples
both singleton orders, whereas one canonical source unit has `j<k`; hence the
factor `1/2`.  Every row must carry `Delta_e/[2 K q_phase(e)]`.  It would be
wrong to divide either phase by its own count unless the two phase means were
then multiplied by the deterministic `P/K` and `M/K` weights.  The manifest's
formula is equivalent to the correct construction.

The result is exactly unbiased for the finite population formed by the
numerically certified M131 coefficients.  Any M131 quadrature error remains
the same separate approximation boundary as in M133; adaptivity does not
repair or enlarge that proof.

### 1.2 Variance identity

For the trace/Frobenius vector loss,

```text
V(q) = sum_e ||G_e||_F^2/(4q(e)) - ||T||_F^2.
```

The conditional main error has zero mean given the complete pilot, so it is
uncorrelated with every pilot-measurable random variable.  Pilot draws are iid.
Consequently

```text
tr Var(T_hat) = [P V(q0) + M E_pilot V(q1)] / K^2.
```

Relative to `K` base draws, whenever `V(q0)>0`, this gives exactly

```text
R_total = P/K + (M/K) R_main = 1/8 + (7/8) R_main.
```

The stated `.714285714...` main-law threshold for a `.75` total ratio is
correct.  The executable protocol still needs a fail-closed rule for a zero or
numerically unresolved `V(q0)` denominator.

### 1.3 Realized pilot magnitude

For the source metric explicitly limited to `(F31,F22)`, the ideal fixed
importance law is proportional to

```text
A_e = |Delta_e| sqrt(||F31_e||_F^2 + ||F22_e||_F^2).
```

The claim that this is computable in `O(n)` per sampled pilot triple is valid.
Each feature is a fixed sum of rank-one matrices, and

```text
<u v^T, a b^T>_F = (u.a)(v.b)
```

reduces its squared norm to a fixed number of length-`n` reductions.  No dense
per-triple `n x n` feature is mathematically required and no extra M131
coefficient evaluation is required.  This is source information, not a final
response or target-label query, so there is no hidden per-sample response
call in the proposed observable.

The metric scope must remain explicit: M133 also returns `k4_aaaa=diag(F31)`.
Equation (3) is the ideal law for the frozen `(aaab,aabb)` premise loss, not for
a norm that independently counts `aaaa` again and not for the final M121/M125
response metric.

### 1.4 Three-bank factorization

The adapted mass

```text
h1(i,j,k) = R_i^2 U_j U_k [X_ij X_ik + X_ij Y_jk + X_ik Y_jk]
```

has exact `O(n^2)` setup and `O(n)` categorical sampling per draw.

For bank A, with `a_j=U_j X_ij`, the centre normalizer

```text
R_i^2[(sum_j a_j)^2-sum_j a_j^2]
```

counts every ordered distinct pair `(j,k)` exactly once.  Choosing `j`
proportional to `a_j(sum a-a_j)` and then `k != j` proportional to `a_k`
produces `R_i^2 U_j U_k X_ij X_ik` exactly.

For bank B centred at singleton `j`, put

```text
l_i=R_i^2 X_ij,  r_k=U_k Y_jk,
D_j=(sum_i l_i)(sum_k r_k)-sum_i l_i r_i.
```

Choosing `j` proportional to `U_j D_j`, then `i` proportional to
`l_i(sum r-r_i)`, then `k != i` proportional to `r_k` gives the second term.
The exchanged singleton construction gives the third.  Their analytic
normalizers sum to `Z1`; direct tuple evaluation of `h1/Z1` is `O(1)` after
the tables exist.

The current M133 `Factored211Proposal` cannot represent this law because it
has one common node vector and one common edge matrix.  M146 needs a new
role-aware proposal class rather than an unsafe reinterpretation of the M133
fields.

### 1.5 Symmetries and support

The proposed physical strength `tau_v=s_v||W_v||` is invariant under a
positive ReLU gauge.  `Delta_ijk` and `F_ijk` have reciprocal homogeneous
degrees, so `A_e`, the learned fields, both proposal laws, and every HH
contribution are invariant in exact arithmetic.  All node/edge operations are
label-local and the edge states are unordered, giving hidden-label permutation
covariance in distribution.  Depositing both repeated--singleton edges and
treating the two singleton banks as exchanged copies preserves `j,k`
symmetry.

The defensive support statement

```text
q1 = .25 q0 + .75 qad >= .25 q0 > 0
```

is correct.  The stronger prose claim that `q1` has *exactly* 5% uniform mass
needs a degenerate-case correction.  It is exactly 5% only when the structural
normalizers are positive.  If `Z0=Z1=0`, both documented fallbacks are fully
uniform and `q1` is 100% uniform.  The invariant needed for HH is the lower
bound `q1(e)>=.05/N` (indeed larger under fallback), not an exact mixture label.

### 1.6 Recursive novelty

M146 is not a retuning of M133, M139, or M143.  Its new information is the
realized exact sampled integrand magnitude `|Delta_e| ||F_e||` from a disjoint
pilot.  M133 uses a static quadratic bridge surrogate, M139 used a static
partial-correlation envelope, and M143 used static sign-scrambled suffix path
energy.  The pilot-to-future adaptation is a new observable and a new causal
operator.  The lawful theorem and proposal factorization should be preserved
even if the frozen implementation later fails its variance gate.

## 2. Binding repairs before implementation

### 2.1 Freeze an endpoint-safe generated state path

The manifest says only "fresh generated finite means and positive-definite
covariances."  It does not give the matrix formula, association order, dtype,
or layer-to-layer construction.  It also does not state whether M131 receives
`build_zero_sampling_frechet` or M129 `build_state_frechet`.

That omission blocks the premise:

* `build_state_frechet` delegates to M122 and rejects width above eight, while
  every frozen M146 width is 12 or greater.
* `build_zero_sampling_frechet` supports these widths, but the pair and triple
  series used by `conditional_collision211_defect_dot` reject selected
  correlations with `|rho|>.80` and can fail their coarse/fine tail tests.
* M143's newly available one-shot evidence shows that its propagated generated
  chain already reached the endpoint refusal before any efficacy output.

A repair must freeze one of two honest paths before implementation: (a) an
explicit width-capable generated family whose every frozen state is required
to pass the unchanged M131 certificate with zero retries, or (b) an audited
endpoint-safe exact coefficient evaluator.  Seed replacement, silently
dropping failed triples/cells, correlation clipping, or relaxing the
certificate after observing an outcome is prohibited.  A certificate failure
must be recorded and must fail the entire frozen screen.

### 2.2 Complete the executable estimator contract

The repaired manifest and implementation must freeze:

1. the exact generated chain and source-layer aggregation used to define one
   record's source Frobenius error;
2. an explicit `t=1,...,P` convention for `lambda_t=rho^(P-t)` (the
   pseudocount means an off-by-one common scale changes the proposal);
3. a dependency-free exact Gram-norm routine and its target dtype/association
   order, tested against dense `F31/F22` construction;
4. a role-aware three-bank class with exact `probability` and `sample`
   methods, uniform fallbacks, stable mixture evaluation, and no rejection;
5. a five-product function that accepts one concatenated row batch and the
   already computed heterogeneous scale vector `Delta/[2Kq_phase]`; M133's
   existing `_hh_scales` API accepts only one proposal and cannot implement
   this contract directly;
6. exact all-zero, nonfinite, underflow, zero-bank, and zero-baseline-variance
   behavior;
7. the estimator of `R_main`.  Because exhaustive generated tables are
   promised, the clean definition is the exact finite-population `V(q1)` for
   each frozen pilot followed by a prespecified aggregation; deriving it
   post-hoc from the noisy total ratio is not equivalent;
8. the definition of the p99 squared-contribution statistic, including which
   phase(s), norm, empirical quantile convention, pooling unit, and ratio of
   quantiles versus quantile of ratios; and
9. exact score-shuffle semantics and gate recomputation from record-level
   data, including zero denominators and strict/non-strict comparisons.

Until these are frozen, two independent implementations can satisfy the prose
and produce different proposals, costs, and gate decisions.

### 2.3 Replace the static cost assertion with a non-overlap crosswalk

The inherited `94.940940240B` M133 sheet legitimately owns the same 512 exact
coefficient calls and the same five rectangular products.  Splitting those
512 calls into pilot and main phases does not itself rebill them, and
concatenating phase rows can in principle retain five products.

The incremental worksheet is not yet independently auditable:

* the pilot-norm line allows `2048=8n` scalar units per pilot triple, while the
  generic rank-one Gram expansion contains many more length-`n` dot products;
  an optimized fused monomial kernel may still be cheap, but its exact kernel
  and bill are absent;
* the main "mixture probability/scans" line allows only `128=n/2` units per
  target draw even though a fresh factored sample normally performs multiple
  length-`n` categorical scans.  Some sampling work may replace work already
  owned by M133, but the base-versus-replacement crosswalk is not stated;
* allocation/copy reserves are not tied to named buffers or calls; and
* the pilot creates a serial coefficient-evaluation barrier before proposal
  construction.  Across 31 layers, a 25 ms incremental residual allowance is
  only `2.5B`, leaving `2.307647280B` below the branch ceiling.  Previous
  official/local wall inflation makes this a cliff risk, not spare budget.

Implementation may proceed only after a structural trace source accounts for
every new or replaced operation at target width, dtype, and call shape.  Before
any efficacy authorization, an integrated native float32 trace must prove
incremental billed arithmetic `<=251,412,480`, incremental residual
`<=.025 s`, finite probabilities/weights, peak-memory safety, and zero
resource failures.  A miss kills this deployment configuration; the remaining
2.31B may not be silently consumed.

### 2.4 Refresh lineage evidence

The theory and manifest say M143's response outcome is unopened.  That was
true when they were hashed, but the current authoritative state now contains
`M143_DEVELOPMENT_FAILURE_20260807.md` (SHA-256
`66fb3b5ad00162004db8574e6ff229f1a9510c399614b3d81de789f9688dfee9`).
It records a protocol/certificate failure and no efficacy result.  M146's
lineage must be updated to say that M143's mechanism remains unresolved but
its frozen implementation failed the endpoint-safe generated-state link.  This
does not make M146 a retune; it supplies the new certificate constraint in
section 2.1.

## 3. Firewall and evidence audit

The current firewall is fail-closed:

* `execution_authorized`, `promotion_authorized`, and
  `confirmation_authorized` are all false;
* no runner, authorization, or result is declared present;
* development and confirmation units are disjoint in the manifest; and
* the formal champion hash and parent source hashes reproduce exactly.

Verified SHA-256 pins:

| artifact | SHA-256 |
|---|---|
| M146 theory | `870a28b3b46d1710855be74e076d3fd364a6bada24bf31fe7f4f5bea5ea6938f` |
| M146 frozen manifest | `1d9d5a906fd43da503dc017fff02d2ffff55cc498109cb734f2c658d5e077094` |
| M131 implementation | `1bb1912b82f8d7b7a204bc19d0d260a9050f02e83b8e87d322188632882ecac3` |
| M133 implementation | `c296c95ede532c1451e0444b9d56b51e96287ef251b11de9cacee0df7d1ea6b1` |
| M139 implementation | `291e72eac67526da1dfc48bb22f278b4a2f29830f188cf0a93b1a7524dba3832` |
| M143 proposal implementation | `5dab449d9ceff7099e04f4521415e781592e6eec260636dd4e81688c9dc6d9bb` |

The holdout intent is good, but the missing generated-cell formula and missing
record/gate definitions mean the frozen premise is not yet reproducible.  The
repair must update its hash, add implementation/tests/trace hashes, and retain
the separate root authorization boundary.  No confirmation may be opened by
a source-premise pass; a new response protocol remains mandatory.

## 4. Required evidence for the next audit

Before a verdict can become `PASS_TO_IMPLEMENT` or `PASS_TO_SCREEN`, provide:

1. exhaustive small-`n` normalization and probability checks for all three
   adapted banks, the defensive mixture, and every zero-normalizer fallback;
2. empirical sampler-frequency checks against exhaustive probabilities;
3. dense-versus-Gram feature-norm tests, including extreme finite scales;
4. direct-scatter versus heterogeneous five-product equality with pilot and
   main rows in one batch;
5. exact/Monte-Carlo checks of the conditional expectation and variance
   identity on tiny enumerated populations (algebra tests, not efficacy);
6. simultaneous gauge, hidden-label permutation, and singleton-exchange tests
   of magnitudes, fitted states, probabilities, samples in distribution, and
   HH outputs;
7. a width-capable generated-state/certificate test for every frozen cell with
   no retry, clipping, or cell removal;
8. a target-shape FlopScope structural trace plus integrated native residual
   and peak-memory trace; and
9. a one-shot authorization/receipt protocol that recomputes every pooled and
   per-family gate from complete record-level results.

## Final disposition

**REPAIR / NO PREMISE EXECUTION.**  Preserve the adaptive-HH theorem, the
`1/8+7/8 R_main` dilution law, the exact pilot magnitude, and the role-aware
factorization.  Repair the generated-state certificate, executable protocol,
degenerate support wording, lineage, and cost crosswalk.  This is a promising
new information operator, but it is not yet a runnable candidate, an efficacy
result, a target-ready estimator, a champion, or a winning entry.
