# WHestBench hyperconnection corpus

Generated: 2026-08-06. This is a curated, evidence-typed corpus for local
Graphify extraction. It distinguishes theorem, measurement, oracle experiment,
hypothesis, metaphor translation, and rejected mechanism. A connection is not
evidence merely because it is aesthetically appealing.

In this corpus, `HARD KILL` is local to one specified implementation and gate.
It preserves proved identities, useful operators, measurements, and unresolved
families for causally different reimplementations. See
`SALVAGE_MAP_20260806.md` for the living operator bank.

## Objective and constraints

The target is the vector mean of the final ReLU activations of a fixed,
bias-free, width-256, depth-32 Gaussian-He MLP under a standard Gaussian input.
The installed WHestBench 0.14 scorer uses

`score = MSE * max(0.1, (billed_FLOPs + 1e11 * residual_seconds) / 2.72e11)`.

The estimator must be universal across fresh private MLPs. Public-network
lookup, hidden-target recovery, counter manipulation, uninstrumented dependent
arithmetic, and over-budget tricks are illegal. Offline training on generated
or public development MLPs is allowed, provided inference features come from
the submitted weights and are legally computed at runtime.

Development indices are 0..599. Indices 600..799 are locked until a mechanism
and coefficient grid are frozen. Indices 800..999 are prohibited for this
generation because they were previously used. Promotion requires a paired
network bootstrap 95% interval below zero, no failures, and no material tail
regression.

## Frozen measured parent and promoted champion

The immutable fallback is an orthogonal three-level recursive-fold sampler
with 39,936 points. On official indices 0..4 it had raw MSE
1.5686923e-7, adjusted score 1.4123151e-7, mean effective compute 248.963B,
and zero failures. Source:
`../fold3_n39936_influence_r8_test/official5.json`.

A plain random 32,256-point child was promoted after the predeclared paired
100-network screen on public indices 0..99. Its official aggregate raw MSE was
3.089512726e-7, adjusted score 2.257079776e-7, mean effective compute 202.282B,
maximum effective compute 250.489B, and failures 0/100. The uncensored paired
bootstrap interval for child-minus-parent adjusted score was
[-4.017637049e-2, -1.955091686e-3]. The parent failed combined-budget
enforcement on 5/100 networks. On the 95 both-success networks, the child had
14.71% worse raw MSE but 6.44% better adjusted score. This is a cost-robustness
promotion, not a claim of lower sampling variance or global optimality. Source:
`../random32256_paired100/REPORT.md`.

## Exact mathematical structure

Positive homogeneity radializes the Gaussian integral exactly:
`E_x f(x) = E[chi_256] E_u f(u)` on the unit sphere. Antipodal averaging kills
all odd spherical harmonics. Orthonormal frames integrate degree <=2 exactly.
A complete maximal real mutually unbiased basis union integrates degrees <=5
with antipodes. The exact Kerdock family in dimension 256 has 129 bases and
33,024 lines.

The corrected harmonic ledger is important. For the full 129-basis union,
`A4=0`, `A6=2.06203521`, and `A8=1.99804807`; it is false that every even
degree >=8 is exactly 2. For a 126-basis trim, `A4=0.04742218`,
`A6=2.06057070`, `A8=1.99809410`, and `A10=2.00006589`.

The constructed 126-basis design reduced raw error relative to matched random
points on a tiny screen, but its structured activation pattern made official
cost nonlinear and excessive. The 90-basis variant averaged 282.214B effective
compute and failed 4/5 networks. A pure WHT/layer-2/Strassen construction was
also invalid at 415.521B billed and 807.727B effective compute. Therefore exact
design quality is not equivalent to contest fitness.

## Sampling and point-placement findings

For a rotation-invariant random field with spectrum `a_l`, a cubature rule has
error `sum_l a_l M_l`. The design already removes low degrees, while most
surviving error lies in even degrees >=6. Fixed kernel reweighting is uniform
because the antipodally closed MUB Gram matrix has constant row sums.
Quadratic and low-degree control variates are annihilated by the design.

Adding a less efficient independent point family is dilutive under the
score-cost mediant law. Rotation selection from two unbiased estimates is a
coin flip. Active-subspace methods fail because gate patterns tumble: local
Jacobians are low rank but their singular subspaces rotate across inputs, and
the design residual is high-degree and near-isotropic.

Dyadic/fractal/recursive folding is useful only when each fold supplies
negative covariance per billed operation. Direct parity folds worsened error
by 12.6 to 500 times. Unbiased multilevel variants had variance-cost products
1.17 to 2.98 times the parent, so they were rejected. Tau is a naming metaphor,
not a free variance identity.

## Analytic closure findings

Full-covariance Gaussian moment matching propagates the exact covariance under
each dense linear layer and applies an analytic bivariate ReLU moment map. Nine
tests passed and the FlopScope implementation matched NumPy to 1.38e-14. On
official indices 0..4 it achieved raw MSE 5.42815345e-5 and adjusted score
5.42815345e-6 at 6.1894B billed and 16.141B effective compute, zero failures.
This was 17.25 times better than a diagonal closure but 38.8 times above the
cheap-analytic promotion gate. Increasing quadrature order from 10 to 96
changed predictions by only 1.33e-10, so repeated Gaussian reclosure—not
quadrature—is the bottleneck.

An exact oracle using final preactivation mean and variance with Gaussian
closure has MSE 8.76e-7. Oracle true terminal third and fourth cumulants with a
Gram-Charlier correction reach about 4.7e-8. Thus k3/k4 information is valuable
if it can be computed accurately and cheaply.

One-shot analytic terminal k3 correction improved only 0.493%. Cross-fitted
sampled k3/k4 improved -0.0042% out of fold and increased variance-cost by
1.0012. The final distribution is not repaired by a noisy terminal-only
estimate.

The full factorized K=3 SIMPLE recurrence costs at least 290.212B before
lower-order work and cannot fit. A BASE ablation without fourth-cumulant power
corrections may fit around 196--202B but is a biased, unpromoted research
candidate. Its CP rank grows by new width-column blocks at each ReLU.

Cumulant truncation errors are nearly orthogonal across order, so scalar
Shanks, Aitken, and Richardson acceleration explode or saturate. The expansion
parameter is L/n, not 1/n. Second and third order errors do not share a stable
geometric mode.

## Cavity, Dyson, TAP, and four-point vertices

A feed-forward network is a directed acyclic graph with no reuse of a weight
matrix in a recurrent feedback loop. Consequently its Onsager self-reaction
term is zero, and the corresponding Dyson feedback series is nilpotent rather
than an infinite resummation. Mean, covariance, and third cumulant do not
identify the next ReLU mean: an explicit closure counterexample exists.

A connected four-point vertex is required for generic finite-width correction.
A dense fixed-instance fourth-order state requires O(n^4) storage and O(n^5)
transport, far outside the O(L n^3) envelope. Cavity/TAP can be revived only if
a fixed-weight low-rank or separable four-point vertex is proved to remain
closed under every dense linear and ReLU layer. Source:
`../cavity_dyson/REPORT.md`.

## Copula and mixture findings

A two-Gaussian mixture can match additional marginal moments, but mean,
covariance, and univariate moments leave n(n-1)/2+1 unidentified dependence
degrees of freedom. Gaussian initialization collapses the two components.
A scale split constrained to match fourth moments also collapses. ReLU
marginals contain atoms, so a copula is not identified by the available state.
Generic k3 output propagation is O(n^4) and k4 is worse. This branch was
rejected absent additional weight-derived dependence structure.

## Controls, hybrids, and shrinkage

A global sampler/full-covariance hybrid fitted on 20 networks worsened raw MSE
by 0.765%. Its per-network oracle coefficient would improve 22.15%, but oracle
coefficients range from -3.74 to +3.56, showing that the useful signal is
network-specific and sign-changing. This is a bridge clue: a universal scalar
control is dead, but a weight-conditioned equivariant coefficient may still be
testable if predicted out of network.

Nonlinear shrinkage achieved 5.058% pooled apparent improvement, but its
coefficient CV was 54.8%, its seed ratio was 2.06, and stable seed-leave-one-out
improvement was only 4.79%, below the predeclared 5% gate. It was rejected.

Approximate-mean controls help only when their external mean error is below the
sampler standard error. Depth-truncated surrogate correlation rises with depth
but probe dilution falls in opposition; usable correlation times dilution stays
between 0.11 and 0.23.

## Cross-domain translations

These are mechanism proposals, not claims of success.

Retinal predictive coding translates to a residual pyramid: propagate a cheap
global Gaussian prediction, then model only layerwise innovations at several
depth scales. It does not imply literal quantum image formation.

Biological morphogenesis translates to repeated local update plus global
normalization. For this network, a candidate implementation is a
permutation-equivariant message-passing model over neuron nodes, with edge
features from weights and node features from analytic moments. Shared update
rules across layers preserve relabeling symmetry and can emit final-neuron
residual corrections.

Memristive hysteresis translates to compressed depth memory: exponentially
weighted or multiscale summaries of how mean, variance, skew proxies, gate
probability, effective rank, and correlation concentration evolve through the
32 layers. The physical analogy contributes a feature design, not a theorem.

Fractal series and tau folding translate to dyadic multiresolution. Candidate
features compare layers 1,2,4,8,16,32 and successive innovations. Candidate
estimators may telescope these scales only if measured covariance justifies
the cost. The rejected parity-MLMC results forbid assuming that telescoping is
automatically beneficial.

Quantum superposition translates classically to signed orthogonal probes,
Hadamard transforms, and antithetic cancellation. Those mechanisms are already
represented by frames, MUBs, WHTs, and recursive folds. Quantum terminology
does not create unbilled amplitudes or a hardware speedup in this CPU contest.

Tensor-network thinking translates to low-rank CP, Tucker, tensor-train, or
random sketch representations of the connected four-point vertex. The central
question is not compression at one layer but closure and rank growth under all
linear/ReLU updates.

Renormalization translates to finding a small state whose update absorbs
discarded cumulants into learned scale-dependent couplings. The no-go for
fixed scalar sequence acceleration means those couplings must depend on the
actual weights and layer state.

## Surviving hyperconnection candidates

### H1: equivariant learned residual closure

Compose full-covariance analytic propagation, layerwise depth-memory features,
randomized low-rank k4 sketches, and permutation-equivariant message passing.
Train offline on development MLPs to predict `truth - analytic_prediction`,
grouped strictly by whole MLP. This attacks the fixed-instance finite-width
residual without storing a dense four-point tensor. It is legal in principle.

The model graph must quotient three exact nuisance symmetries: arbitrary
hidden-neuron permutations, positive ReLU gauge rescaling between adjacent
layers, and orthogonal rotation of the Gaussian input basis. A raw-weight GNN
that does not enforce these symmetries can learn public-set coordinates rather
than a universal correction. Candidate defect nodes are layerwise Hermite
sources derived from the full-covariance closure. Candidate message edges are
gauge-fixed contractions; candidate aggregators include correlation
center-surround, signed-versus-absolute cancellation, and dyadic depth memory.
The cheap proposed feature graph costs below 0.22B operations; an optional
fourth-power proxy adds about 1.07B. Source:
`../equivariant_graph_spec/FEATURE_GRAPH.md`.

The quantitative kill gate is severe. Improving full-covariance raw MSE from
5.43e-5 to about 1.9e-6 requires out-of-network residual R^2 greater than
0.965, before inference cost. A small premise model should be killed
immediately if grouped cross-validation is far below this threshold.

Result: HARD KILL for the current feature family on public indices 0..99.
Nested 5x4 whole-MLP CV gave residual R2 0.662672 with bootstrap interval
[0.622890, 0.697078], versus the fixed 0.965 gate. A shared scale already gave
0.648801; all 70 graph features added only about 1.4 R2 points. Per-network
oracle pure-scale R2 was only 0.72465. Symmetry checks passed at about 1e-11,
so the failure is information/observability rather than leakage or broken
equivariance. Source: `../equivariant_residual_model/REPORT.md`.

### H2: weight-conditioned sampler/control coefficient

The scalar hybrid failed while per-network oracle blending improved 22.15%.
Predict the sign and magnitude of a network-specific coefficient from cheap
permutation-invariant weight and analytic-state summaries, trained out of
network. It must beat the sampler after accounting for analytic inference cost
and coefficient-estimation bias. This is a narrower and cheaper precursor to
H1.

Existing evidence strongly weakens sign prediction: the coefficient's
intraclass correlation is only 0.129 and all six cross-seed oracle-transfer
checks failed. Weight-only features cannot predict randomness introduced by a
fresh sampler scramble. At most, the graph may predict the seed-averaged
coefficient or residual magnitude. H2 must therefore be trained and evaluated
across independent sampler seeds; same-seed coefficient fitting is leakage.

### H3: dynamically truncated k3/k4 tensor sketch

Maintain only the connected directions whose estimated contribution to the
final ReLU mean exceeds their transport cost. Use deterministic randomized
projections seeded by the MLP seed, explicit error monitors, and a hard rank
cap. The premise gate is <=30% k4 error with stable correction signs on small
exact networks and projected runtime cost <=50B. A sketch that is accurate at
one layer but loses closure over depth is rejected.

Static accounting gives a bare cost of 8.187B per retained pair rank across
the 32-layer network. Rank 5 costs 40.936B; rank 6 costs 49.124B before
recompression and lower-order work; rank 7 is impossible at 57.311B. Exact
uncompressed transport is about 33.020T. Therefore a rank-5 optimistic
pair-eigen ceiling is the decisive cheap falsifier. Source:
`../k4_tensor_sketch/DERIVATION.md`.

Result: HARD KILL on public index 0, widths 8/12/16 and depth 4. The
optimistic optimal pair-eigen rank-5 ceiling had mean raw k4 error 16.83% and
worst 29.80%, but the downstream correction reached cosine -1.000 and 25.88x
relative error. CountSketch had mean raw error 49.83%, worst 115.82%, and
minimum sign agreement 62.5%. The 40.936B optimistic cost excluded sketch
construction and k3 work. The branch fails the predeclared stability gate and
must not be promoted. Source: `../k4_tensor_sketch/REPORT.md`.

### H4: random 32,256-point cost mutation

This changes no mathematical bias class. It tests whether the scorer's fixed
and residual overhead make fewer plain random points better in adjusted score
than the higher-cost recursive-fold parent. Result: PROMOTED after the frozen
100-network paired screen. The packaged local champion has SHA-256
`1874f9cac4be962dbd4f919bffc38dedf23b428ea6cbd7847a813c87d7ba7333`.
It passed estimator tests, package validation, bit-exact source/package parity,
and the 0..99 official screen with zero failures. This remains the locally
best validated candidate, not a demonstrated competition winner.

### H5: finite-horizon base-factor k3 transport

Truncate the cubic correction's depth memory to horizons 2, 4, 8, 12, and 16
to test whether forgetting acts as a stable renormalization. The independent
ARC NumPy parity check passed to 5.19e-15, and the scored path was corrected to
remain float32 after a CDF promotion defect was found.

Result: HARD KILL on public index 0. The best horizon, H=2, had raw MSE
1.1010e-3, adjusted score 1.3162e-4, and effective compute 32.516B: 583.1x
worse adjusted than the champion and 14.51x worse raw than same-index full
covariance. Its correction direction was informative (cosine 0.8997 with the
needed full-covariance residual) but overshot by about 4.68x. Even a
truth-assisted optimal scalar coefficient produced raw MSE 1.445e-5 and could
not beat the champion at the 0.1 multiplier floor. Short memory damps an
unstable expansion; it does not close it. Source: `../k3_base_factor/REPORT.md`.

### H6: goal-oriented adjoint cumulants

Reverse the contraction order: inject each layer's leading connected Hermite
source once and contract it with a downstream response matrix, requesting only
the 256 terminal diagonal cumulants. The retained projections are exact:
`s3(p)=3 sum_i p_i w2_i v_i^2` and
`s4(p)=4 sum_i p_i w3_i v_i^3 + 12 u^T C u`, with
`v=C(p*w1)` and `u=p*w2*v`. Dense-tensor and reverse-contraction tests agree
to at most 3e-11. The full isolated terminal fold costs 3.111411200B.

Result: HARD KILL as a standalone estimator, PRESERVE as a component. On exact
small networks the final k3/k4 correction cosines were 0.9514/0.7621 with
98.33%/93.33% material sign agreement. It repaired mean absolute skew from the
terminal-Hermite estimate 0.0317 to 0.3867, close to the raw oracle scale 0.38.
Nevertheless public0..4 full-covariance MSE improved only 2.12%, from
5.428155e-5 to 5.312933e-5, and one network regressed. Correcting the dominant
downstream mean/covariance bias requires covariance adjoints; one exact ReLU
pullback maps rank-one `ww^T` to `diag(w) K diag(w)`, generically full rank.
Across all outputs this needs O(n3) state and O(Ln4) work. Source:
`../adjoint_cumulant/REPORT.md`.

### H7: weight-identified latent-factor mixture closure

Retain q Gaussian components per layer. For each component, propagate its full
covariance, take r leading simple covariance eigenfactors, integrate those
factors with q-point Gauss-Hermite nodes while rectifying the diagonal residual
analytically, then deterministically recompress q^(r+1) children to q
equal-mass bins. The components are constructed forward from the weights and
current explicit state, so this avoids fitting an underidentified generic GMM
or copula. Exact fallbacks at repeated eigenspaces and score ties preserve the
permutation/gauge rule.

Result: FIXED-r IMPLEMENTATION KILLED; MIXTURE COMPONENTS PRESERVED. On seven
small synthetic networks, q=3,r=2 achieved a real summed-MSE ratio 0.04738 and
won 6/7. An independent audit found no leakage or orientation error, but on
fresh n=64 cases it lost 8/8, with ratios 2.928 at L16 and 1.596 at L32. The
mechanism is explicit: the top-two trace share falls from 88.4% at n4 to 3.02%
at n256, so fixed-r diagonalizes nearly all target-width dependence. The audit
also found a near-|rho|=1 comparator defect and absolute tolerances that break
scale homogeneity. A one-knob r=3 mutation scored ratio 0.0602767, 27.22% worse
than r=2, because extra tensor resolution was aliased by the same three-bin
compressor. Preserve forward weight-defined components, analytic diagonal
rectification, deterministic recompression, and symmetry; replace the rank and
quadrature law. Sources: `../latent_factor_closure/ADVERSARIAL_AUDIT.md` and
`../latent_factor_rank3/REPORT.md`.

### H8: adaptive fixed-trace spherical-radial latent closure

Keep the preserved q=3 mixture machinery, but choose enough leading covariance
factors to capture a fixed trace fraction and replace q^r tensor quadrature
with the signed rule `+-sqrt(r)e_j`, 2r nodes. This matches the selected-factor
covariance with O(r) children, so r can grow with width without exponential
mixture growth. A relative eigengap rule replaces the scale-breaking absolute
threshold. Premise gate: on the frozen fresh n64 audit cases, ratio <=0.8,
at least 6/8 wins, exact scale/permutation invariance, and conservative target
arithmetic below 80B. Status: premise running, no WHest data or scorer.

### H9: full-covariance spherical-radial sigma mixture

Keep q=3 deterministic recompression but remove factor truncation entirely.
For each component use the unique symmetric PSD square root `L=V^(1/2)` and
the 2n equal-weight nodes `mu +- sqrt(n)L e_j`. The rule matches the entire
Gaussian covariance, grows linearly rather than exponentially, and its node
set is permutation-equivariant. It directly tests whether fixed-r trace loss or
three-component recompression is the binding failure. It uses the same frozen
n64 ratio/win/invariance/<80B gate as H8. Status: premise running, no WHest data
or scorer.

## Rejected attractive stories

Literal quantum retinal pigment, generic memristor language, tau numerology,
reaction-diffusion without an equivariant update, generic active subspaces,
generic copulas, generic TAP/AMP, fixed scalar resummation, fixed kernel
reweighting, direct parity folds, and public-set memorization are not viable
solutions under current evidence. They may be cited only through the concrete
computational translations above.
