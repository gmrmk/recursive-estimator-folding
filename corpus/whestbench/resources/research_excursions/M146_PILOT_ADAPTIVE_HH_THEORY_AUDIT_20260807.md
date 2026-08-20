# M146 pilot-adaptive Hansen--Hurwitz source proposal -- hostile theory audit

Date: 2026-08-07  
Disposition: **DEPLOYMENT CONFIGURATION KILLED ON NATIVE COST / COMPONENTS PRESERVED / NO EFFICACY RUN**  
Scope: generated mathematics plus a fresh-synthetic target-shape structural trace only

## Executive verdict

M146 is the first member of the M133 proposal line that does not try to infer
the hard `[2,1,1]` coefficient solely from a static surrogate.  It spends a
fixed `P=K/8` prefix of the already-budgeted exact coefficient evaluations,
measures the actual invariant magnitude of those sampled source contributions,
fits one bounded role-aware factorization, and uses it only for the remaining
`K-P` draws.  Every draw retains its own ordinary Hansen--Hurwitz denominator.

The mathematical operator survives hostile audit for three precise reasons.

1. Conditioning on the complete pilot makes the main proposal fixed.  The
   main HH average is therefore unbiased conditionally, while the pilot HH
   average is unbiased unconditionally.  Their combination uses deterministic
   count weights.  Reusing the pilot values to fit the main proposal does not
   create bias.
2. The exact source coefficient, not target truth, supplies the new observable.
   This is a genuine change from M139's failed static partial-correlation
   envelope and M143's protocol-failed output-path-energy implementation.
3. The learned law remains a sum of three positive tree banks, so its exact
   normalizer and sampler cost `O(n^2)`, not `O(n^3)`.  Pilot and main rows can
   be concatenated into M133's same five rectangular products.

The deployment configuration does **not** survive.  A paired native float32
target-shape structural trace measured `369,162,631` incremental billed work
against the frozen `251,412,480` gate and `0.262182186 s` maximum paired
incremental residual against the `0.025 s` gate.  With the frozen 25% arithmetic
protection, the non-overlap complete cost is `121.620612118B`, above the branch's
`100B` ceiling.  Under the observed worst official/local residual factor of
five, it projects to `226.493486475B`, a `2.385625x` cost ratio to M133.  These
misses kill M146 before any generated efficacy test.

There is no variance theorem.  The pilot dilution is severe: at target
`P/K=1/8`, a total variance ratio of `.75` requires the adapted **main** law to
reach at most `.714286` of the base variance.  The pilot sees only `3P=192`
node incidences and `3P=192` edge incidences in a population of 256 nodes and
32,640 edges.  Node generalization is plausible; direct edge reinforcement is
mostly extrapolation from single hits.  The generated premise is now closed,
not merely unauthorized: the structural cost falsifier failed first.

The repaired module and tests expose the proposal algebra, exact sampling,
Gram norm, heterogeneous five-product scales, and frozen gates.  Generated
state construction and exact coefficient certification remain behind a typed
endpoint-safe provider interface pending M147.  No endpoint constructor or
runner was invented to bypass that certification boundary.

No contest model, target truth, scorer, public/private response, leaderboard,
submission, or champion outcome was read or used in deriving this candidate.

## 1. Non-negotiable recursion invariants

### Objective and score

The contest target is the final-layer mean vector.  The official adjusted
score has the recorded form

```text
score = MSE_final * max(.1, C / 272e9),
C = billed_FLOPs + 1e11 * residual_wall_seconds.
```

M146 is only a source estimator inside the M121/M125 analytic carrier.  The
M133 branch uses a stricter complete protected ceiling of `100B` to preserve
score efficiency and cliff margin.  Passing that branch ceiling is necessary,
not sufficient, for a contest candidate.

### Frozen champion

M146 does not mutate the formal local champion:

```text
submission_formal_local_champion_l1_20260806.tar.gz
SHA-256 bc2ec39558c76a67b12b587ca4ee70bb1e8921489643d83707e052d086e8ae36
public-100 raw MSE       3.089460087e-7
public-100 adjusted      2.121762464e-7
failures                 0/100
```

No package, designation, or submission action is authorized here.

### Legality, accounting, and bias class

- Inputs are only the supplied network weights, the Gaussian background state,
  and randomness owned by the estimator seed.
- The exact M131 coefficient is an analytic function of that state.  It is not
  a benchmark target or hidden label.
- Every proposal has explicit positive support.  No rejected draw, post-hoc
  normalization, unbilled target call, or accounting bypass exists.
- In exact real arithmetic the estimator is exactly unbiased for the same
  finite-population `[2,1,1]` source total as M133.  Quadrature error remains
  M131's separately certified numerical approximation.
- Development, confirmation, and contest units remain disjoint.  The frozen
  structural cost miss closes the generated premise and cannot promote M146.

## 2. What changed relative to M133, M139, and M143

Let `e=(i,j,k)` denote an ordered distinct triple, with `i` the repeated label
and `j,k` the interchangeable singleton labels.  Let

```text
G_e = Delta_e F_e,
T   = (1/2) sum_e G_e.
```

M131 supplies the exact sampled connected-minus-tree coefficient `Delta_e`.
M133 supplies the coefficient-free repeated-output feature `F_e`, the factor
`1/2` for ordered singleton ownership, and the five-product scatter.

The relevant lineage is:

| branch | observable used by the proposal | failure boundary | M146 relation |
|---|---|---|---|
| M133 | bridge quadratic conductance and downstream row norms | `K=2n` affordable but width-32 P8 ratio `1.223`; `K=3n` variance-surviving but protected cost `102.255B` | preserves exact coefficient, HH ownership, and five products; changes the information available to the proposal |
| M139 | source scale plus a fixed rank-4 positive partial-correlation envelope | response ratio `1.04159`, upper-90 `1.11467`, adverse width trend | does not retune rank, ridge, cap, or latent strength; uses realized exact coefficient magnitudes instead |
| M143 | source scale plus a static sign-scrambled downstream path-energy sketch | frozen implementation terminated before response construction when the generated Gaussian bridge state approached an endpoint; no efficacy result exists | its output-aware mechanism remains unresolved, but its failed endpoint-safe certification is now the typed boundary that M146 refuses to bypass |

This is not a claim that slime moulds or memristors compute neural cumulants.
The metaphor has been reduced to an ordinary adaptive-importance operator:

```text
conductance     -> positive proposal mass,
deposited flux  -> bounded pilot contribution score,
fading memory   -> fixed exponential age weights,
homeostasis     -> neutral pseudocount and clipped log factors,
exploration     -> exact 5% uniform rescue plus 25% base-proposal carryover.
```

## 3. Frozen base law

Let `B` be the standardized Gaussian bridge and put

```text
S_uv = |B_uv| for u != v,      S_uu = 0.
```

Let `s_v=sqrt(Var(ReLU(Z_v)))` from the same frozen Gaussian background and
let `W_v` be row `v` of the downstream weight.  The physical strength

```text
tau_v = s_v ||W_v||_2
```

is invariant to a positive ReLU gauge.  The base mass is

```text
h0(i,j,k) = tau_i^2 tau_j tau_k [
    S_ij S_ik + S_ij S_jk + S_ik S_jk
].                                                        (1)
```

For `N=n(n-1)(n-2)` and `epsilon=.05`,

```text
q0(e) = (1-epsilon) h0(e)/Z0 + epsilon/N,   Z0=sum_e h0(e), (2)
```

with exact uniform interpretation if `Z0=0`.  This is the gauge-completed
scale-only descendant already isolated by M139/M143, not M139's killed rank-4
partial envelope and not M143's output-aware path energy.

## 4. Pilot observable: exact invariant source magnitude

The pilot contains `P=K/8` draws `E_t~q0`, with target `K=512`, `P=64`.
For each draw, M131 already evaluates `Delta_t`.  No extra coefficient call is
made.  M146 additionally computes

```text
A_t = |Delta_t| sqrt(||F31_t||_F^2 + ||F22_t||_F^2).       (3)
```

This norm does not require a dense per-triple matrix.  Write

```text
F31 = 6 (xyz) x^T + 3 (x^2 z) y^T + 3 (x^2 y) z^T,
F22 = 2[x^2 (yz)^T + (yz)(x^2)^T]
    + 4[(xy)(xz)^T + (xz)(xy)^T].                         (4)
```

For rank-one matrices,

```text
<u v^T, a b^T>_F = (u.a)(v.b).                            (5)
```

Equations (4)--(5) give both norms from a fixed number of length-`n` dot
products, `O(n)` per pilot triple and no `n x n` temporary.

For trace-Frobenius source loss, the unattainable ideal fixed proposal is

```text
q*(e) proportional to ||G_e||_F = A_e.                    (6)
```

The log correction that would turn `q0` into (6) is therefore
`log(A_e/q0(e))` up to an additive constant.  M146 observes it only on the
pilot.

If all pilot `A_t` vanish, adaptation is exactly neutral.  Otherwise set

```text
A_floor = 2^-24 max_t A_t,
l_t     = log(max(A_t,A_floor)/q0(E_t)),
lambda_t= rho^(P-t),                rho=31/32,
l_bar   = sum_t lambda_t l_t / sum_t lambda_t,
r_t     = clip((l_t-l_bar)/log(16), -1, 1).               (7)
```

The centering in (7) is proposal training only.  It never replaces or
normalizes an HH weight.  The returned estimator is never self-normalized.

## 5. Role-aware fading conductances

The pilot forms four bounded state fields.  With pseudocount `kappa=1`, define

```text
g_R(v)  = sum_t lambda_t r_t 1[i_t=v]
          / (kappa + sum_t lambda_t 1[i_t=v]),

g_S(v)  = sum_t lambda_t r_t (1[j_t=v]+1[k_t=v])
          / (kappa + sum_t lambda_t (1[j_t=v]+1[k_t=v])),

g_RS(u,v) = sum_t lambda_t r_t [1[{u,v}={i_t,j_t}]
                               +1[{u,v}={i_t,k_t}]]
          / (kappa + the same incidence sum),

g_SS(u,v) = sum_t lambda_t r_t 1[{u,v}={j_t,k_t}]
          / (kappa + the same incidence sum).             (8)
```

Unseen coordinates have state zero.  Every state lies in `[-1,1]`.  Convert
them to positive, factor-two-bounded multipliers:

```text
a_R(v)  = exp(log(2) g_R(v)),
a_S(v)  = exp(log(2) g_S(v)),
c_RS(u,v)=exp(log(2) g_RS(u,v)),
c_SS(u,v)=exp(log(2) g_SS(u,v)).                           (9)
```

The adapted structural mass is

```text
R_i = tau_i a_R(i),                 U_j = tau_j a_S(j),
X_uv = S_uv c_RS(u,v),              Y_uv = S_uv c_SS(u,v),

h1(i,j,k) = R_i^2 U_j U_k [
    X_ij X_ik + X_ij Y_jk + X_ik Y_jk
].                                                        (10)
```

Singleton symmetry is exact.  Equation (10) remains three factored tree
banks.  For example, the first bank chooses repeated centre `i` with mass

```text
R_i^2 [ (sum_j U_j X_ij)^2 - sum_j (U_j X_ij)^2 ],        (11)
```

then two distinct endpoints.  For the second bank, at singleton centre `j`,

```text
left_i  = R_i^2 X_ij,
right_k = U_k Y_jk,
centre mass = U_j[(sum_i left_i)(sum_k right_k)
                  - sum_i left_i right_i].                (12)
```

The third bank exchanges the singleton names.  Thus construction, exact
normalization, probability evaluation, and sampling remain `O(n^2)`.

Let

```text
q_ad(e) = .95 h1(e)/Z1 + .05/N                           (13)
```

with uniform fallback when `Z1=0`.  The main law is the defensive mixture

```text
q1(e | pilot) = beta q0(e) + (1-beta) q_ad(e),
beta = 1/4.                                               (14)
```

It follows that `q1>=q0/4`.  In every nondegenerate component the explicit
uniform rescue is exactly 5%; a zero-normalizer component is defined as 100%
uniform, so the effective uniform share is at least 5%, not always exactly 5%.
The factor bounds do not prove improvement, but they prevent unbounded learned
conductance ratios; (14) prevents complete abandonment of the structural base.

## 6. Exact estimator and the pilot-reuse proof

Draw `P` pilot triples from `q0`, fit (7)--(14), then draw `M=K-P` main triples
conditionally independently from `q1`.  Return

```text
T_hat = (1/K) [
    sum_(t=1)^P     G_(E_t)/(2 q0(E_t))
  + sum_(t=P+1)^K   G_(E_t)/(2 q1(E_t | pilot))
].                                                        (15)
```

The two row groups use phase-specific scale entries but are concatenated
before M133's same five rectangular products.  There are not ten products.

Let `F_P` be the sigma-field generated by the complete ordered pilot, its exact
coefficients, and the fitted proposal.  Since every main draw is from the
probability in its own denominator,

```text
E[ G_E/(2q1(E|F_P)) | F_P ] = (1/2)sum_e G_e = T.         (16)
```

The pilot law similarly gives

```text
E[ G_E/(2q0(E)) ] = T.                                   (17)
```

Taking expectations in (15) yields

```text
E[T_hat] = (P/K)T + (M/K)T = T.                          (18)
```

This proof explicitly allows the pilot's sampled integrand values to determine
`q1`.  What would invalidate it is any of the following:

- replacing the deterministic `P/K,M/K` weights by a pilot-chosen mixture;
- reweighting pilot draws retroactively by `q1`;
- normalizing HH weights by their realized sum;
- fitting on any main draw and then evaluating that same draw under the fitted
  proposal;
- dropping or retrying an inconvenient pilot; or
- choosing `P`, `K`, or a stopping time from the observed scores and dividing
  by that random count.

All six operations are prohibited by the manifest.

## 7. Exact variance accounting and the dilution barrier

For a fixed proposal `q`, define

```text
V(q) = sum_e ||G_e||_F^2/(4q(e)) - ||T||_F^2.             (19)
```

Conditional main errors have mean zero, so their covariance with every pilot
measurable quantity is zero.  Consequently

```text
tr Var(T_hat)
 = [P V(q0) + M E_pilot V(q1)] / K^2.                    (20)
```

Relative to `K` base draws,

```text
R_total = f + (1-f) R_main,
f=P/K=1/8,
R_main=E V(q1)/V(q0).                                    (21)
```

The arithmetic consequences are binding:

| desired total ratio to base | required `R_main` |
|---:|---:|
| `.817661` (only enough to erase M133's width-32 `1.223x` P8 deficit) | `.791613` |
| `.750000` (frozen premise effect gate) | `.714286` |
| `.666667` (same variance as increasing `K=2n` to `K=3n`) | `.619048` |

Thus the pilot is not free merely because its coefficient calls are reused.
It contributes base-law variance for one eighth of the estimate and leaves
seven eighths on which to repay that dilution.

The defensive mixture gives the second-moment bound

```text
sum_e ||G_e||^2/(4q1(e)) <= 4 sum_e ||G_e||^2/(4q0(e)).  (22)
```

It does **not** imply `V(q1)<=4V(q0)` because subtracting `||T||^2` affects the
ratio.  Uniform rescue makes all moments finite on the finite population; it
does not make a bad proposal good.

## 8. Multiple adaptive rounds: lawful theorem, rejected deployment

Let `F_(t-1)` contain all earlier draws and let a full-support `q_t` be
`F_(t-1)`-measurable.  If `E_t|F_(t-1)~q_t`, then

```text
Z_t = G_(E_t)/(2q_t(E_t)),
E[Z_t-T | F_(t-1)] = 0.                                  (23)
```

For a fixed deterministic `K`, `K^-1 sum_t Z_t` is unbiased even if every
proposal is updated.  The centered increments are a martingale-difference
sequence.  This is the precise mathematical content of repeated memristive
adaptation.

M146 nevertheless freezes one update only.  Rebuilding a factorized proposal
after small blocks consumes call/allocation headroom; recent-score feedback can
chase cancellation noise; and adaptive stopping followed by division by the
random count is not covered by (23).  A later multi-round child must change
that cost/variance mechanism and receive its own manifest.  It is not an
implicit tuning option here.

## 9. Gauge and permutation invariance

Under a positive hidden-unit gauge `D=diag(d_v)>0`,

```text
s_v'       = d_v s_v,
W_v'       = W_v/d_v,
tau_v'     = tau_v,
Delta_ijk' = d_i^2 d_j d_k Delta_ijk,
F_ijk'     = F_ijk/(d_i^2 d_j d_k).                      (24)
```

Therefore `A_e`, `q0`, every pilot log score, all four state fields, `q_ad`,
and `q1` are invariant.  Each HH matrix contribution `Delta_e F_e/q_phase(e)`
is invariant as well.

Under a simultaneous hidden-label permutation, `S`, `tau`, pilot triples,
state fields, and both proposals merely relabel.  The proposal law is
permutation covariant in distribution.  The implementation must not select
top-index pivots or use label-order tie breaking.  Ordered singleton ownership
remains symmetric because `j,k` enter (8)--(14) symmetrically.

## 10. RNG ownership and tangent boundary

The frozen premise protocol uses `numpy.random.Generator(PCG64DXSM)` with
child keys containing

```text
(master, split, family, width, cell_seed, method, repetition,
 layer, phase, purpose).
```

`pilot_draw`, `proposal_shuffle`, `main_draw`, and `bootstrap` have disjoint
purpose codes.  The candidate and score-shuffle attribution arm share one
read-only pilot snapshot by design; their main streams are disjoint.  All
other methods have disjoint method streams.  Exact tables and proposal states
are hashed before main draws.  No seed retry is permitted.

For a Frechet response, both `q0` and the pilot-fitted `q1` must be frozen at
the unperturbed state.  A source/background tangent at fixed weights uses the
same `Delta_dot F/(2q)` ownership as M133.  A weight tangent also needs
`Delta F_dot/(2q)` and is prohibited until separately implemented and tested.
No `qdot` or score-function term belongs to the frozen-proposal pathwise
derivative.

## 11. Native target-shape cost falsifier

The initial worksheet allowed at most `251,412,480` protected incremental
arithmetic and `0.025 s` incremental residual on top of M133's protected
complete `94,940,940,240`.  Those were frozen kill gates, not estimates to be
reinterpreted after measurement.

The repaired implementation was traced in float32 at `n=256`, 31 source
layers, `K=512`, `P=64`, and `M=448`.  Three paired measurements compared a
replacement M133 proposal path with the M146 proposal path.  The trace includes
the proposal banks, exact normalizers, target-sized categorical scans,
sampled-probability gathers, batched pilot Gram norm, fading node/edge states,
defensive mixture, heterogeneous phase scales, and the serial pilot-before-main
barrier.  It excludes the same 512 M131 coefficient calls, the same five
rectangular source products, and the common M125b carrier and hard samplers.

| quantity | frozen gate | measured | pass |
|---|---:|---:|:---:|
| incremental billed work | `251,412,480` | `369,162,631` | no |
| protected incremental arithmetic | `251,412,480` | `461,453,289` | no |
| maximum paired incremental residual | `0.025 s` | `0.262182186 s` | no |
| complete non-overlap protected | `100,000,000,000` | `121,620,612,118` | no |

The three nonnegative paired residual deltas were `0.242362111`,
`0.262182186`, and `0.247649703 s`.  The local structural cost ratio to M133 is
`1.281013`.  Applying the previously observed worst official/local residual
factor of five projects `1.310910929 s` incremental residual and
`226,493,486,475` complete protected work: `126.493B` over the branch ceiling
and `2.385625x` M133.  It remains about `45.507B` below the official `272B`
cliff, but that does not rescue branch efficiency or headroom.

All frozen structural gates fail.  The disposition is therefore
`KILL_M146_DEPLOYMENT_CONFIGURATION_PRESERVE_ADAPTIVE_HH_THEOREM`.  No
optimization, retuning, seed retry, parameter change, or generated efficacy
screen is permitted under M146 after this result.

## 12. Deep what-if oracle

The uncertainty was sharpened to one variable: **does a `1/8` exact pilot
predict at least a `28.6%` reduction in the remaining conditional source
variance, across both structured and iid-He generated chains?**

| branch | evidence-compatible mechanism | quantitative trigger | action |
|---|---|---|---|
| Omega: local flux is real | higher-order `Delta F` magnitude clusters by repeated node and bridge edge beyond the static quadratic jet | `R_main<=.60`, total `<=.65`, attribution beats shuffled scores | preserve as a response-screen survivor; do not promote |
| Alpha: node signal, sparse edge noise | node fields generalize but almost every learned edge is a one-hit estimate | `.714<R_main<.90` or adverse width trend | kill this configuration; salvage node-only state for a separately frozen child |
| Delta: reinforcement chases rare rescue hits | `A/q0` has a heavy tail and clipped single hits redirect too much mass | total ratio `>=1`, p99 HH norm worsens, or one family fails | kill complete implementation; retain only the conditional-unbiasedness theorem |
| Psi: source norm points the wrong way | source Frobenius variance falls but M121/M125 output response amplifies a different signed direction | source gate passes, later response gate fails | preserve pilot machinery; replace the observable only if a cheap exact response adjoint is found |
| Phi: static priors already own the signal | exact pilot scores are explained by source scale or a future endpoint-safe output prior | candidate does not beat score-shuffle/neutral attribution | kill as redundant; do not retune fading or caps |
| Infinity: repeated updates look better in-sample | more rounds exploit pilot ordering but add calls or use random stopping | only post-hoc round counts win | reject; fixed one-round M146 remains the only tested definition |

The structural cost branch fired before these efficacy branches could be
observed.  They remain a salvage map for a genuinely new descendant whose
mechanism changes the measured call/allocation cost, not permission to run or
retune M146.  Any descendant must retain phase-specific denominators and fixed
counts and must not infer output improvement from source improvement.

The non-obvious 1% insight is that the pilot's coefficient calls are free only
in **cost**, not in **information allocation**.  Equation (21) makes the
one-eighth variance tax unavoidable.  Most informal adaptive-IS proposals
omit that term and consequently overstate their attainable gain.

## 13. Repaired executable boundary and closed premise

The repaired implementation now exposes and tests the complete non-endpoint
surface:

1. exact role-aware three-bank `q0`, `q_ad`, and defensive `q1`, including
   explicit 100% uniform semantics for degenerate banks;
2. no-rejection ordered-distinct sampling and exact proposal probabilities;
3. fixed-index fading fields with duplicate handling, score-shuffle attribution,
   nonfinite rejection, and bounded factors;
4. the exact batched `F31/F22` Gram norm in frozen float32/float64 association;
5. heterogeneous pilot/main phase scales concatenated into exactly five
   products, with a direct parity reference;
6. exact `R_main`, mixed-phase p99, premise completeness, paired bootstrap, and
   pooled-plus-per-family gate conjunction; and
7. snapshot hashing plus a typed `EndpointSafe211Provider` interface.

Fourteen unit tests pass.  They cover exhaustive normalizers, probabilities,
singleton symmetry, empirical sampling, degenerate banks, NaN/collision
handling, time indexing, duplicate and shuffled attribution, dense Gram parity,
extreme gauges, heterogeneous five-product parity, the conditional-expectation
identity, the variance identity, p99 and gate semantics, endpoint lockout, and
snapshot digests.

The typed endpoint interface deliberately has no constructor.  M143's frozen
implementation failed before efficacy because its generated Gaussian bridge
state approached a Gaussian endpoint and the exact coefficient certificate
refused it.  M146 therefore cannot construct generated states, certify M131
coefficients, or perform an integrated endpoint trace until an independently
audited M147 provider exists.  The executable boundary today is proposal
algebra, metrics, tests, and the fresh-synthetic structural trace only.

The formerly frozen generated premise would have compared `q0`, M133, M146,
and a score-shuffle attribution arm across diagonal and iid-He generated
families.  It was not run.  The native cost gates failed first, so the premise
and confirmation are now closed.  No source ratio, `R_main`, p99 efficacy,
response efficacy, or target-ready claim exists.

## 14. Kill and salvage map

### Passed static components

- conditional pilot-to-main HH unbiasedness, including reuse of pilot values;
- fixed-round martingale generalization;
- exact source-norm observable from `O(n)` Gram arithmetic;
- positive role-aware three-bank factorization with exact normalizer;
- gauge and permutation covariance;
- fixed-count heterogeneous five-product reuse;
- exact tail/gate machinery and completeness semantics; and
- typed fail-closed endpoint-provider boundary.

### Unresolved links

- whether `P=n/4` is enough to estimate transferable node/edge structure;
- whether clipped fading states predict unseen triples rather than memorize
  pilot incidence;
- whether source Frobenius magnitude aligns with final response variance;
- whether an endpoint-safe generated coefficient provider can be certified;
- whether a fused descendant can remove the measured call/allocation barrier;
  and
- interaction with a future endpoint-safe output-aware prior.

### Frozen kill conditions

The native cost miss has fired the frozen kill.  Do not reopen M146 by changing
`P`, `rho`, `kappa`, factor cap, defensive weight, rescue mass, seed, bootstrap
gate, or endpoint family.  Preserve the theorem, exact sampler, typed endpoint
boundary, five-product API, and metrics as reusable components.  A lawful child
must materially repair the measured cost mechanism--for example by fusing the
proposal into an already-paid carrier--and must receive a new identifier,
manifest, trace, and audit before any efficacy work.

## 15. Sources and evidence pins

The finite-population inverse-probability foundation is Hansen and Hurwitz,
*On the Theory of Sampling from Finite Populations* (1943),
DOI `10.1214/aoms/1177731356`.  The fixed defensive-mixture idea is consistent
with Hesterberg, *Weighted Average Importance Sampling and Defensive Mixture
Distributions* (1995), DOI `10.1080/00401706.1995.10484303`.  Neither source
proves that the M146 reinforcement lowers this integrand's variance; equations
(16)--(23) are the complete local argument needed for unbiasedness.

Pinned parent artifacts at this audit:

| artifact | SHA-256 |
|---|---|
| M131 implementation | `1bb1912b82f8d7b7a204bc19d0d260a9050f02e83b8e87d322188632882ecac3` |
| M133 implementation | `c296c95ede532c1451e0444b9d56b51e96287ef251b11de9cacee0df7d1ea6b1` |
| M139 implementation | `291e72eac67526da1dfc48bb22f278b4a2f29830f188cf0a93b1a7524dba3832` |
| M143 proposal implementation | `5dab449d9ceff7099e04f4521415e781592e6eec260636dd4e81688c9dc6d9bb` |
| M143 development-failure record | `66fb3b5ad00162004db8574e6ff229f1a9510c399614b3d81de789f9688dfee9` |
| independent M146 pre-execution audit | `95019883b42374a5098dbb9828c4d395fbdf008627df68921b6253ba75e54f82` |
| repaired M146 implementation | `e230c237794247c20523ca087a1fc1e4c4d7c17ce705f750f7d0b40fd2fa3d2d` |
| repaired M146 tests | `fca750a64163080165c1baac723844872d04c3350a6b165f696674d065ac560e` |
| structural trace runner | `6ab04d775b1aa71b42c40f8a18c3ea927cabbd4e07aab6fae9c05335bbe24476` |
| structural trace result | `03939a0efcb1beaf631c01cc35ef092f0dc750cb576a5c95d77a5f85b76e2755` |
| frozen cost crosswalk | `031c04b128c2a98b14e8f9edfebd331ca90251770257e32498bd08b0b6113ca4` |

The result is deliberately narrow: M146 is a mathematically lawful adaptive-HH
component inside a **killed deployment configuration**.  It is not an efficacy
result, target-ready estimator, champion, leaderboard entry, or winning claim.
