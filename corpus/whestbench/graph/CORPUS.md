# WHestBench hyperconnection corpus

Generated: 2026-08-06. This is a curated, evidence-typed corpus for local
Graphify extraction. It distinguishes theorem, measurement, oracle experiment,
hypothesis, metaphor translation, and rejected mechanism. A connection is not
evidence merely because it is aesthetically appealing.

In this corpus, `HARD KILL` is local to one specified implementation and gate.
It preserves proved identities, useful operators, measurements, and unresolved
families for causally different reimplementations. See
`../SALVAGE_MAP_20260806.md` for the living operator bank.

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

The historical access audit supersedes the earlier split description: public
indices 0..799 are burned by completed score-bearing development or validation
analyses, so any local public result is descriptive only. Indices 800..999
were historically designated as an internal lockbox, but their actual access
status requires a separate audit and they are not authorized for this generation. No
locally available public slice is an independent promotion holdout; only the
organizer private suite is untouched. Promotion therefore requires a
data-custodian-approved fresh evaluation, a paired network bootstrap 95%
interval below zero, no failures, and no material tail regression.

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
set is permutation-equivariant. Result: IMPLEMENTATION KILLED, CONSTRAINT
PRESERVED. Covariance relative error was 3.01e-15, scale/permutation passed,
and conservative cost was 48.381B, but the frozen n64 ratio was 8.8716 with
only 1/8 wins. Removing rank collapse and matching second moments is therefore
insufficient: the low-degree axes severely alias ReLU angular gate crossings,
with the three-bin compressor a possible secondary loss. Any descendant must
change the angular observable, not tune these radii or axes from the same data.
Source: `../latent_full_sigma/REPORT.md`.

### H10: gate-aligned truncated projection mixture

Keep the forward q=3 mixture and deterministic recompression, but replace
variance-ranked quadrature by a projection chosen from ReLU boundary mass. For
each Gaussian component define `b_i=sigma_i phi(mu_i/sigma_i)`, solve `C a=b`,
standardize `T=a^T(Z-mu)`, and partition T into three equal-probability normal
bins. The conditional mean and covariance of Z in each bin are closed form;
each child then passes through the exact Gaussian ReLU moment map. Under a
positive coordinate gauge D, b transforms as Db and a as D^-1 a, so T is
invariant; neuron permutations commute as well. This attacks angular gate
crossings without fixed-r trace loss or exponential nodes. It uses the frozen
n64 ratio<=0.8, wins>=6/8, exact invariance, and <80B conservative-cost gate.
Result: GENERIC-COMPRESSOR IMPLEMENTATION KILLED; DIRECTION PRESERVED. The
operator passed seven structural tests, exact scale/permutation covariance, and
a 68.640B conservative cost bound. It improved all 8/8 frozen n64 cases, unlike
the variance-ranked and sigma-point leaves, but aggregate ratio was 0.997502:
only a 0.2498% reduction versus the required 20%. The stable sign is mechanism
evidence; the effect is about 80x too small. Exact moment recombination plus the
generic three-bin compressor washes out almost all gate-conditional state.
Source: `../latent_gate_split/REPORT.md`.

### H11: gate-label path-memory recompression

Keep H10's boundary direction, relative solve, equal-probability truncated
moments, Gaussian ReLU map, q=3, and frozen n64 cases. Change only compression:
aggregate children by inherited low/central/high split label across parent
components, then moment-match one Gaussian per label. This is a memristic/path-
memory translation with a precise operation: preserve the nonlinear state label
that the generic leading-covariance compressor erased. Result: IMPLEMENTATION
KILLED; MEMORY REQUIREMENT REFINED. Label aggregation passed exact moments,
permutation/gauge errors below 5.2e-16, a 62.600B bound, and 6/8 wins, but ratio
was 0.999602513. It was worse than H10's generic compressor on all 8/8 cases
and erased about 84% of H10's already-small gain. The low/central/high label is
redefined by a different local direction every layer, so its name is not a
coherent transported physical state. Source: `../latent_gate_memory/REPORT.md`.

### H12: Rao-Blackwellized conditional ReLU marginals

Return to H10's better generic compressor and preserve the direction, bins,
q=3, and fullcov correlation map. Change only the earliest lossy link: for each
coordinate and truncation bin, integrate the exact conditional Gaussian
`Z_i|T=t` to obtain `E[ReLU(Z_i)|bin]` and its second moment. Reconstruct a PSD
child covariance from these exact marginal variances and the parent's
Gaussianized correlation matrix. This preserves scalar-conditional skew before
compression at O(q^2 K n) incremental work rather than carrying exponential
components. Result: MARGINAL-ONLY IMPLEMENTATION KILLED; EXACT INTEGRALS
PRESERVED. Six numerical, PSD, symmetry, and cost tests passed, all 8/8 cases
improved, and the cost bound was 68.899B. But the aggregate ratio was
0.997502361, only 6.08e-8 better than H10 and far above the <=0.8 materiality
gate. The scalar statistic explains only about 1.0303e-4 of each neuron's
variance, making the largest within-child marginal correction 1.12e-7. The
unresolved signal is therefore moved from univariate conditional skew to
cross-neuron conditional dependence. Source:
`../latent_gate_rb_marginals/REPORT.md`.

### H13: repeated-index cumulant premise

The first cross-neuron mutation retains third- and fourth-cumulant entries with
at most two distinct indices: k3(iii), k3(iij), k4(iiii), k4(iiij), and
k4(iijj). This is O(n^2) state and admits O(n^3) terminal contractions, but a
dense layerwise recurrence is not assumed. The oracle premise is tested first
on fresh n=8/12/16 depth-2--4 networks. It survives only if it preserves at
least 80% of squared next-layer contraction energy and 80% of material
correction signs. Result: INDEX-OMISSION IMPLEMENTATION KILLED; ORIENTATION AND
TERMINAL ALGEBRA PRESERVED. Material signs were 94/97, yet aggregate
standardized k3/k4/combined fidelities were -248.9998/-3578.1022/-2803.7649
and only 3/9 cases passed all energy gates. Sample doubling confirmed the
depth-four failure. All-distinct entries provide essential cancellation, and
the exact dense iijj recurrence remains O(n^4). Source:
`../pair_repeated_cumulants/REPORT.md`.

### H14: conditional-correlation spectrum

The second cross-neuron mutation integrates exact bivariate ReLU covariances
conditioned on H10's scalar truncation and subtracts the Gaussianized child
covariance. It measures whether this missing matrix is low-rank rather than
assuming it. Rank 1/2/4/8 approximations are tested on fresh n=12/16/24 cases;
rank <=4 must retain 80% of Frobenius energy and 80% of material downstream
signs. Result: COMPRESSION PREMISE SURVIVED; DENSE FORMATION LINK FAILED.
Rank four retains 99.3533% of aggregate off-diagonal energy and 99.1170% of
material downstream signs, with mean/minimum correction cosine 0.9847/0.8216.
Known factors apply for about 0.212B with contingency, while the literal exact
nested bivariate construction costs 1.855T. The tail bins carry essentially all
the energy and effective participation rank has median 3.53. Source:
`../conditional_corr_spectrum/REPORT.md`.

### H15: conditional response-Gram factors

Preserve H14's frozen exact correction cells, rank-four target, downstream
probes, and gates. Change only dense factor discovery: construct coordinatewise
univariate response vectors from `g_i(t)=E[ReLU(Z_i)|T=t]` and a predeclared
centered low-order Hermite/derivative basis, then form a signed response Gram
without enumerating bivariate conditional covariances. The child must recover
at least 80% of H14's energy and material signs, pass symmetry, and remain
below 80B conservative target arithmetic. Result: FORMATION PREMISE SURVIVED.
The fixed degree-four rank-at-most-four proxy recovers 95.0349% of aggregate
off-diagonal energy and 95.9161% of material downstream signs, with mean
correction cosine 0.9336. PSD, permutation, scaling, inheritance, and numerical
tests pass 6/6. Conservative incremental arithmetic, including the exact
diagonal correction, is 0.5103B. About 4.97% remains in the conditional-
covariance expectation. Source:
`../conditional_corr_spectrum_response_gram/REPORT.md`.

### H16: conditional law-of-total-cumulance factors

Preserve H13's frozen exact contraction targets, material-sign definition, and
convergence audit. Replace only deletion of all-distinct entries: express
directional third/fourth cumulants using the law of total cumulance under a
scalar-conditioned or small-rank conditional state. Conditional mean-response
vectors and signed conditional-covariance factors retain all index sectors
implicitly, and contractions are formed directly with each next-layer row
without materializing n^3/n^4 tensors. The predeclared factor order must retain
80% standardized k3/k4 energy and material signs with a sub-O(n^4) recurrence.
Result: GAUSSIAN-WITHIN-CELL IMPLEMENTATION KILLED; EXACT IDENTITY AND
COVARIANCE FACTORS PRESERVED. The exact binned identity reproduces targets
within 3.21e-12; rank-four versus full conditional covariance has combined
fidelity 0.9961. But dropping residual conditional cumulants yields
k3/k4/combined fidelity 0.7560/0.7966/0.7872, below 0.8, despite 94/97 signs.
The failed link is omitted within-cell c3/k4, not covariance rank. Source:
`../conditional_total_cumulance/REPORT.md`.

### H17: q3 response-Gram recursion

Freeze H15's degree, quadrature, rank-four factors, exact diagonal correction,
and zero fitted gain. Insert the correction at every appropriate child/layer of
H10's q=3 gate-split recursion while retaining the generic compressor and the
frozen n64 cases. Compare corrected fullcov, H10, H12, and this child. Survival
requires aggregate ratio <=0.8, at least 6/8 wins, exact symmetry, and <80B
conservative arithmetic. Pre/post-compressor factor norms separate intrinsically
small source from compressor washout. Result: ONE-SCALAR RECURSIVE SOURCE
KILLED; RESPONSE OPERATOR PRESERVED. The child wins 8/8 versus fullcov and
passes PSD, n64 symmetry, and 71.494B cost, but ratio 0.997502340 misses the
0.8 gate and is essentially identical to H12. Generic q3 reduction retains
the global correction norm to 8.22e-16. The source is intrinsically tiny:
median/max correction-to-covariance 9.64e-13/4.63e-7. Source:
`../latent_gate_response_gram/REPORT.md`.

### H18: conditional residual-cumulant spectrum

Preserve H16's exact cells, total-cumulance identity, next-layer weights,
material signs, and convergence bank. Change only the Gaussian residual: use a
rank-r mode-1 unfolding for conditional k3, giving contractions
`(u_s.w)(w^T V_s w)`, and a signed pair-unfolding for conditional k4, giving
`lambda_s (w^T A_s w)^2`. These forms retain all-distinct entries with O(rn2)
state and O(rn3) terminal work. Rank four must preserve 80% k3/k4/combined
contraction fidelity and material signs. Result: REPRESENTATION SURVIVED;
FORMATION/RECURRENCE WITHHELD. Rank-four k3/k4/combined fidelity is
0.993974/0.984388/0.986618 with correction fidelity 0.995497 and 97/97 signs;
rank one also passes. The downstream ReLU correction error is 0.058235x the
Gaussian-cell error. But exact k4 pair formation costs 8.063GiB per cell,
129.0GiB for B16, plus O(p^3) eigensolving. Source:
`../conditional_residual_cumulant_spectrum/REPORT.md`.

### H19: randomized two-radius sigma closure

Preserve the failed full-covariance sigma rule's exact covariance, q=3
compressor, frozen n64 cases, and cost model. Factorially change two local
links: fixed covariance-square-root axes versus preseeded Haar frames, and the
single radius `sqrt(n)` versus a positive two-node Gauss rule for the chi_n
radius matching moments through degree three. The 2x2 ablation separates
angular gate alias from radial homogeneity error. Rotation results are averaged,
never best-picked; distributional permutation/gauge symmetry, peak memory,
ratio<=0.8, wins>=6/8, and <80B are frozen gates. Primary grounding is Genz--
Monahan stochastic spherical-radial integration. Result: N64 FACTORIAL
SURVIVED. Fixed/sqrt(n) and fixed/chi2 ratios are 8.8716/9.1062; seeded Haar
alone reaches 0.668802, and Haar+chi2 reaches 0.631599 with 7/8 wins. Every
predeclared rotation is below 0.8. Structural error is 1.50e-14, peak working
set 37.04MB, and conservative target cost 70.590B. No truth was generated.
Sources: `../latent_randomized_radial/REPORT.md` and
`../../sources/research_randomized_radial_cubature_20260806.md`.

### H20: multi-direction gate response

Preserve H15's exact degree-four response operator and change only the scalar
conditioning source. Let `g_i=phi(mu_i/sigma_i)/sigma_i` and form the invariant
boundary-susceptibility Gram `F=diag(g) C diag(g)`. Its eigenvectors define an
orthogonal direction bank in standardized susceptibility coordinates. Add the
per-direction signed factors for k=1/2/4/8 and, only if cost permits, 16; never
form q^k Cartesian components or select directions from outcomes. Because H17
is about 80x short, the truth-free premise requires a credible >=80x source
amplification, symmetry, PSD, and <80B before n64 truth. Result: GAUSSIAN-
PARENT FINITE-BANK IMPLEMENTATION KILLED; INVARIANT DIRECTIONS PRESERVED. The
initial 25,741x factor-only amplification omitted its cancelling Gaussianized-
split bias. Exact conditioning/recombination of a Gaussian is a no-op. In the
complete source k1 has five PSD fallbacks in 24 states, while k2+ costs at least
108.573B. No truth was read. Source:
`../multidirection_gate_response/REPORT.md`.

### H21: sparse-radial harness separation

The frozen adaptive tau=0.5 candidate has no eight-case verdict. Two harness
workers reached 24.6GB and 13.8GB because the last generic compression bin can
enter a zero-progress loop with `remaining>eps`, `capacity=0`, and `take=0`,
appending zero-weight components indefinitely. Streaming truth itself stayed
near 42.5MB and reproduced the first three earlier ratios. This kills only the
in-process measurement harness. A valid re-audit must freeze the reducer repair
and run every case in an externally RSS/time-limited child. Source:
`../latent_sparse_cubature/RESOURCE_POSTMORTEM.md`.

### H22: residual covariance-algebra formation

Preserve H18's exact residual targets and rank-four contraction gate. Constrain
the k3 quadratic matrices and k4 pair factors to a fixed <=12-dimensional
algebra generated by already-available rank-four conditional covariance
factors, their symmetric products, diagonal response directions, and trace
terms. This oracle premise asks whether the 129GiB dense factors can be
identified inside existing state before inventing matrix-free probes. It must
retain 80% actual next-row k3/k4/combined fidelity and signs with O(Br2n2)
state/O(Br2n3) terminal work. Result: ALGEBRA REPRESENTATION SURVIVED;
COEFFICIENT FORMATION/RECURRENCE WITHHELD. K3/k4/combined fidelity is
0.983464/0.969492/0.972741 with 97/97 signs; doubled combined is 0.995556.
Repeated probes are locally identifying for n12/n16 but not uniformly at n8,
and conditioning can exceed 1e10. Source:
`../conditional_residual_covariance_algebra/REPORT.md`.

### H23: randomized-radial n128 scaling

Freeze H19's combined operator, q=3 compressor, four rotation seeds, and
arithmetic averaging. Generate four fresh iid-He n128/L32 synthetic networks
and streamed 65,536-antithetic references under external RSS/time limits and a
zero-progress reducer assertion. Survival requires aggregate ratio<=0.8,
wins>=3/4, every rotation aggregate<=1.0, exact structure, <2GB peak, and the
same <80B n256 cost. Passing authorizes a production FlopScope specification,
not public scoring by itself. Result: WIDTH LAW SURVIVED. Aggregate ratio is
0.634996973 with 4/4 wins. Per-rotation ratios are
0.5633/0.2825/0.9291/0.7650; peak working set is 241.91MB, maximum wall 26.1s,
and every structural/resource/reducer guard passes. Target arithmetic remains
70.590B. Source: `../latent_randomized_radial_n128/REPORT.md`; the exact
production contract is in `PRODUCTION_PORT_SPEC.md`.

### H24: randomized-radial susceptibility compressor

Reuse H20's invariant susceptibility coordinate only where it is meaningful:
the genuinely non-Gaussian Haar+chi2 point cloud from H19. Clone the n64 parent
and change only q3 recompression. Against the same uncompressed point cloud
passed through one more weight/ReLU, the susceptibility-aware compressor must
reduce aggregate mean+covariance observable error by 20% versus generic and
win 75% of states, while preserving moments, symmetry, PSD, and <80B cost. The
frozen n128 parent remains untouched. Result: SINGLE-SUSCEPTIBILITY COMPRESSOR
KILLED; PULLBACK PRESERVED. It passes exact moments, PSD, symmetry, spectrum,
and 71.953B cost, wins all 8 layer-zero states, but reaches only ratio 0.975251
and 11/24 wins. Mid/late covariance worsens; covariance is 99.35% of generic
observable-error energy. Source:
`../randomized_radial_susceptibility_compressor/REPORT.md`.

### H25: Physarum-attention mixture-of-experts router

Translate slime-mold adaptation into a parameter-free graph algorithm. Demand
nodes are invariant ReLU-boundary/covariance observables; expert nodes are
whole moment-safe rules (fullcov, fixed sigma, Haar/sqrt, Haar/chi2). Edge
length combines conservative cost and structural mismatch. Electrical flow
`q=(D/ell) Delta p` obeys conservation, and conductance updates as
`D<-(1-eta)D+eta|q|`; fixed scaled-dot attention initializes D and the entropy
barrier attenuates collapse. P0/P1 freezes tau=1,gamma=1,eta=.25,32 steps and
top1/top2 with no learned weights. On fresh n16/n24 one-step states, the hybrid
must beat always-Haar+chi2 error by 20%, win 75%, remain compute-neutral, and
pass symmetry/load gates. Mediant and rotation-selection certificates remain
binding. Result: FIXED SPECIALIZATION LINK KILLED; ROUTER GRAPH PRESERVED. The
primary top1 ratio is 0.866761 with 18/24 wins and compute below the parent, but
all 24 states select fullcov. The frozen bank itself has hard best-pure and
best-convex-top2 ratios 0.833818 and 0.829054, so routing alone cannot reach the
0.80 gate. Add a genuinely complementary complete expert before rerouting.
Source: `../physarum_moe_router/REPORT.md` and
`../../sources/research_physarum_moe_relu_routing_20260806.md`.

### H26: randomized-radial FlopScope production port

Freeze H19/H23's Haar+chi2 operator, q=3 compressor, per-MLP deterministic
rotation seed, and no coefficient tuning. Hoist square-root/rotation buffers
and reshapes to setup, use exact charged shapes, and compare every ported stage
to the NumPy reference. The development gate requires finite outputs, numerical
parity, zero failures, and safe maximum combined cost—not merely 70.590B
abstract arithmetic. Only allowed development rows may be touched; locked and
prohibited rows remain untouched. The FP32 port survives its synthetic target
gate: six test groups and 200 internal-stage comparisons pass, maximum absolute
parity error is 6.44e-6, billed work is 59.276B, residual-adjusted compute is
71.423B, and peak working set is 210.6MB. Exact declared call counts, finite
nonnegative output, PSD tolerance, and zero-progress guards pass. Preserve this
hash-frozen implementation as the production reference; official-row and
mixed-precision decisions remain separate. Sources:
`../latent_randomized_radial_n128/PRODUCTION_PORT_SPEC.md` and
`../latent_randomized_radial_fp32_port/REPORT.md`.

### H27: randomized-radial dual-observable compressor

Preserve H24's exact q3 contract and non-Gaussian point cloud. Change only the
direction geometry to the parameter-free normalized sum
`F_gate/tr(F_gate)+F_active/tr(F_active)`, where
`F_active=diag(Phi(alpha)) R diag(Phi(alpha))`. The first term retains gate/mean
susceptibility; the second targets the active linear pair-covariance response
that dominates H24's error. The top fixed direction/bank must reach ratio<=0.8
and >=18/24 wins with the same structure and <80B gates. The s^2 tail partition
remains a separate future link. Result: SCALAR FUSION KILLED; BOTH LANES
PRESERVED. It reaches ratio 0.965944 and 17/24 wins while passing all structural
and 71.964B gates. Gate/active channel cosine falls from about 0.72-0.75 early
to 0.15-0.25 late, so scalar averaging is the diagnosed failure. Preserve a
rank-two response subspace and test the T^2 tail separately. Source:
`../randomized_radial_dual_observable_compressor/REPORT.md`.

### H28: flatworm-ladder attenuation

Translate only documented flatworm organization: paired longitudinal cords,
transverse commissures, and measured habituation/dishabituation. For invariant
expert or response evidence `u_l`, use dyadic longitudinal memory
`m_l=.5m_(l-1)+.5u_l`; couple predeclared pairs by the nonexpansive block
`[[.75,.25],[.25,.75]]`; and attenuate conductance with leaky flow fatigue and
bounded novelty relief. The biology motivates the topology, not the equations.
The router P2 balances all four experts but worsens loss to 1.101064, selected
expert cost to 4.684x, and proxy-inclusive cost to 1.52484x; leak and
commissural cells are exactly neutral. Kill router attenuation, preserve the
two-lane response translation. That translation maps H27's gate and active
Grams to separate longitudinal lanes, smooths shared early signal, and retains
late contrast. Source: `../flatworm_ladder_attenuator/REPORT.md` and
`../../sources/research_flatworm_ladder_attenuation_20260806.md`.

### H29: ECN-Jacobian MaxEnt constrained compression

Borrow only the defensible ECN pattern `psi -> tau -> phi`: extract invariant
gate/active response features, transform them in a cheap observable-Jacobian
pullback metric with a maximum-entropy optimization prior, then remap into a
q=3 mixture that exactly preserves mass, mean, raw second moment, and PSD.
Literal finite-field elliptic curves are excluded because modular quantization
does not preserve the continuous Gaussian identities. Following Mlynarski et
al., the route prior is `q(theta) exp(beta U(theta;W))/Z`; beta measures trust
in a target-free variance-minus-cost utility and is frozen on disjoint
cleanroom networks. A flatworm two-lane recurrence is an ablation, not a
truth-fitted depth schedule. The no-ladder cell reproducibly reaches ratio
0.911472 with 32/32 wins; the fixed flatworm cell is 0.933606. Independent
audit rejects the deployable claim. The feature metric is an SPD surrogate,
not the claimed analytic observable Jacobian; the optimizer is balanced
entropic soft k-medoids, not a Mlynarski prior; the decoder is hardcoded to
K48/d6; and the target cloud K=4qn=3072 projects to 89.925B plus a 38.65GB
dense delta tensor. Preserve balanced transport and the exact total-moment
decoder algebra. The next legal rung replaces only psi by the exact ReLU
Jacobian in (alpha,log sigma), makes phi shape-generic, fixes 64 transport
steps, and resolves streaming target cost before accuracy. Sources:
`../ecn_jacobian_maxent_compressor/REPORT.md`,
`../ecn_jacobian_maxent_compressor/JUDGE_MATH_STAT.md`,
`../../sources/research_ecn_jacobian_maxent_routing_20260806.md`, and
`../../sources/research_mlynarski_optimization_priors_20260806.md`.

### H30: Fourier/Gegenbauer exact-mean weight distillation

Distill each disclosed teacher network into a small analytic-mean control
student. A pilot fits shallow ReLU ridges, Gaussian sine/cosine features, or
spherical zonal harmonics aligned by a frozen weight/Jacobian rule; an
independent residual set estimates `f-g`. The Fourier systems-biology paper
motivates spectral enrichment but its time-grid FFT is not copied: neuron-index
FFT would break permutation symmetry. The strongest cell starts at even
spherical degrees >=6, directly targeting the broad residual not annihilated
by the antipodal 5-design. Feature means are exact, and all pilot/fit/teacher
costs count. The frozen student dictionaries fail. A layer-one ReLU control
improves iid pointwise variance to 0.656x but worsens design-surviving raw and
cost-adjusted variance to 1.145x and 1.981x. The degree-{6,8} Gegenbauer student
scores 91.141x raw and 174.995x cost-adjusted with 0/16 wins and control-error
correlation -0.0367. Reject these directions; preserve exact-mean, cross-fit,
MUB, and cost-ledger machinery for a response-aligned dictionary. Sources:
`../weight_distilled_multifidelity/REPORT.md` and
`../../sources/research_fourier_enhanced_distillation_20260806.md`.

### H31: JSpace fused-Jacobian response lens

Audit JSpace at commit `54089367f887dde0b076d99bba71d053b67d70ac` under
its MIT license. Its transferable mechanism is a fused Hutchinson VJP: one
reverse traversal for an output probe yields downstream response vectors at
every layer. The transformer-specific vocabulary, token positions, unembedding,
and sparse nonnegative semantic cone do not exist in WHestBench. The cleanroom
translation compares the signed lens `E[D_l]` against the energy lens
`E[D_l^T D_l]`, because input-dependent ReLU gates can cancel the former while
preserving the latter. Nonnegative pursuit is only an ablation; signed pursuit
is the symmetry-compatible comparator. A passing lens may define a frozen
layer band and Jacobian-response atoms for H30's exact-mean cross-fit harness.
It may not select depths or directions using official truth. The cleanroom
geometry premise survives: `E[J]` retains median 0.102787 of Jacobian energy,
while `E[J^T J]` has effective rank 5.587 and top-eight energy 0.930047.
K=4 Hutchinson reaches exploratory median Gram error 0.08566 and top-eight
overlap 0.99574 for input-only projected target cost 2.813B. Signed pursuit
improves residual only 8.66% and success 1.91 points, below its gate. Independent
audit confirms the exact VJP identity but rejects layerwise/gauge/capacity
claims. The exactly-once error link then fails decisively: energy-lens controls
score 4.75763x raw and 21.0923x cost-adjusted, 0/16 wins, correlation .05057;
signed-J is 9.1184x and isotropic 4.28796x. Preserve G0 only as an offline
diagnostic. Sources:
`../jspace_workspace_adapter/REPORT.md`,
`../jspace_workspace_adapter/JUDGE_MATH_STAT.md`,
`../jspace_gram_aligned_control/REPORT.md`,
`../../sources/research_jspace_adaptation_20260806.md`, and
`../../sources/research_jspace_source_audit_20260806.md`.

### H32: production closure external falsifier

The hash-frozen randomized-radial FP32 port passes engineering: six tests,
200 internal-stage parity cells, exact call counts,59.276B billed,71.423B
residual-adjusted, and210.6MB peak. Under a gate frozen before access, it was
run exactly once on the lowest untouched permitted development row, index100.
Accuracy is raw8.38117e-5 and adjusted2.16946e-5, or96.1178x worse than the
deployed sampler champion. Kill the direct replacement claim; preserve the
Haar angular de-aliasing, chi radial nodes, guarded q3 compressor, and FP32
implementation only as components. At the same multiplier, the one-row versus
aggregate 96.1178x comparison corresponds to MSE retention .0104039, RMSE
.101999, or R2 .989596. This is a severity threshold, not a population theorem
because the units are unmatched; a real child must pass paired residual
variance per total cost. Sources:
`../latent_randomized_radial_fp32_port/REPORT.md`,
`../latent_randomized_radial_fp32_port/JUDGE_COST_LEGALITY.md`, and
`../latent_randomized_radial_fp32_port/DEVELOPMENT_INDEX100_REPORT.md`.

### H33: failure inversion, not sign reversal

For an exact-mean fitted control `HB`, replacing H by -H replaces B by -B and
does not change the estimator. Likewise `a+mean(f-a)=mean(f)`, so sampling a
constant analytic residual is exactly the pure sampler. Two causal inversions
remain admissible on fresh cleanroom seeds: use bottom or top-orthogonal-
complement G0 directions instead of top sensitivity modes; or supply a new
per-sample analytic surrogate with an exact mean and matched residual-cost
advantage. The structural inversion is now closed. Bottom-G0 and top-orthogonal
controls improve 29.87% and 24.64% versus top-G0, proving the subspace change
is real, but remain4.246x/4.563x raw,18.825x/20.247x cost-adjusted,0/16 wins,
and near-zero correlation. Terminate JSpace controls. The analytic-residual
collapse/cost audit remains the only inversion calculation in flight. Sources:
`../FAILURE_INVERSION_CALCULUS_20260806.md` and
`../jspace_inverse_complement_control/REPORT.md`.

### H34: compression is cost-times-variance, not fewer bits

Above the 0.1 multiplier floor, a compressed child wins exactly when
`r_cost*r_MSE<1`. Reducing only the number of Monte Carlo paths is first-order
neutral because cost falls as N while variance rises as 1/N. The promoted
random32,256 breakdown is 184.822B matmul work out of185.407B billed,99.684%
across about215 calls; exact matrix-product geometry is therefore the only
immediate engineering compression target. FP16/int8 alone are not cheaper
under FlopScope. The signed higher-cumulant representation remains genuinely
compressible: an oracle-fed <=12D/rank4 inverse retains .926273 combined and
.983525 correction fidelity with94/94 signs. Its first formation mechanism is
locally killed. Constant-modulus Rademacher/Hadamard probes are exactly blind
to the trace-free diagonal algebra direction, recover minimum k3/k4 core-rank
fractions only .3611/.2051, and antipodal pairing adds zero rank. The deeper
obstruction is observability: probabilities, means, diagonal covariance, and
four covariance factors determine only order<=2 and supply no directional
k3/k4 right-hand side. If those responses were free the full route costs only
12.340B; sampling them under80B permits about10719 paths,670/cell, with ideal
skew/kurtosis errors .095/.189. Kill constant-modulus coefficient formation;
preserve the <=12D contraction. Reopen only with nonconstant-amplitude probes
and a weights-only Price/Hermite higher-moment response recurrence. Sources:
`../COMPRESSION_SCORE_CALCULUS_20260806.md`,
`../randomized_radial_inverse_residual/REPORT.md`, and
`../compressed_residual_cumulant_transport/REPORT.md`.

### H35: exact sampler compression reaches the allocation wall

The deployed sampler spends99.684% of billed work in matrix products, so a
fresh whole-row rectangular Strassen child changed only that link. Its
shape-only dispatcher is never worse in billed arithmetic over all65536
`k,n<=256` pairs. At the full `(64512x256)@(256x256)` product, L2 hybrid bills
6.713B versus8.439B direct, ratio.795427. Sixteen synthetic products reach
maximum absolute/relative error5.25e-6/6.38e-7; a fresh depth32 ReLU chain has
relative error4.10e-6 and only5/4194304 gate changes. Algebra and precision
therefore pass. The implementation fails the scorer's actual cost. Direct
effective proxy is8.444B, while L1 sequential/fused and L2 hybrid reach
9.144B/9.602B/12.205B with wall ratios5.28x/6.20x/14.51x. Fully fused L2 needs
496.125MiB before reconstruction. Kill this allocation graph; preserve the
whole-row/ragged formulas. The next causal child must use preallocated `out=`
buffers or a different Winograd reconstruction and cut L1 residual below
about.00987s merely for parity. Source:
`../exact_sampler_compression/REPORT.md`.

### H36: amplitude-coded probes expose the physical quotient

Change only H34's constant-modulus probe law to128 normalized-Gaussian sphere
lines. The trace-free diagonal response becomes material in every nontrivial
cell, with RMS.06967-.18121, zero duplicate lines, and permutation/orthogonal
defects below4.09e-15. Literal core rank remains64/84 for k3 and58/78 for k4,
so the frozen full-coordinate gate fails. This is not missing physical signal:
linear-times-quadratic and quadratic-times-quadratic coefficient arrays map to
homogeneous cubic/quartic polynomials, and both coordinate systems contain a
20D symmetrization gauge. Exact physical cores recover below5.66e-15 relative
error despite that gauge. Nonzero conditions are below30.35/52.54;
combined/correction fidelity is.980382/.991939 with97/98 signs; free-response
cost is12.342916B. Kill the redundant parameterization, preserve amplitude
geometry. The next rung freezes a deterministic64D/58D quotient basis while a
separate Price/Hermite branch attacks the still-missing weights-only response.
Source: `../amplitude_coded_cumulant_probes/REPORT.md`.

### H37: the cumulant quotient is exact gauge removal

The frozen amplitude design, a complete ordinary-monomial coefficient map,
and a response-free SVD quotient agree in all144 cells. For141 nontrivial
cells the cubic coefficients reduce84->64 and the quartic coefficients
reduce78->58; the missing20 dimensions are exactly the kernels of full
symmetrization. Maximum reduced conditions are30.3514/52.5370. Responses,
physical cores, and coordinate equivariance reproduce below9.82e-15, while
combined/correction fidelity remains.980382/.991939 with97/98 signs. This
certifies physical coefficient savings of23.81%/25.64%, but does not yet cut
dominant runtime because the response-free SVD remains charged. Quotienting
removes gauge; it does not create the missing weights-only directional k3/k4
right-hand side. Source: `../cumulant_polynomial_quotient/REPORT.md`.

### H38: Price--Hermite Q2 transports signal but cannot form the RHS

From conditional means and diagonal-plus-rank4 covariance, exact ReLU Price
coefficients define a linear-plus-quadratic Gaussian chaos. Its connected
Wick identities compute k3/k4 by small trace contractions without dense
cumulant tensors. Fast and dense formulas agree below2.42e-16; permutation
and positive-gauge defects stay below6.3e-16; the conservative total envelope
is61.286B. On the frozen suite, transported totals improve from the
zero-conditional baseline to.90194 combined,.96478 final-correction fidelity,
and60/61 signs. The direct within-cell RHS fails: conditional k3/k4/combined
fidelity is.67069/.16234/.28234, and41.75% of factor rows clip. Thus the
operator is useful compressed transport, but moments through2 do not identify
the missing signed conditional energy. Preserve Price coefficients and trace
algebra; change only H2->H4 connected Wick response order inside H37's
physical quotient. Source:
`../price_hermite_higher_moment_response/REPORT.md`.

### H39: preallocation repairs residual cost, not small-GEMM throughput

Three separately frozen Winograd mutations isolate the exact-compute wall.
Sequential preallocation, one batched seven-product matmul, and contiguous
packing all pass billed/effective score proxies at.88206-.88615x direct,
residual time.263-.527ms, float32 relative error about6.04e-7, depth32 error
below2.96e-6 with at most2/4194304 gate flips, and conservative peak memory
below481MiB. The batched child is strongest: billed/effective ratios
.880151/.885099 and a score break-even raw-MSE ratio1.129817. Yet frozen
total-wall ratios are1.55874/1.54559/1.70148, all above1.5. Packing worsens
the result. Allocation/reconstruction is no longer the failed link; one-core
half-width BLAS throughput plus Winograd memory traffic is. Preserve the
score-side batched operator, but do not modify the champion without a
genuinely new kernel mechanism and an estimator-level gate. Source:
`../preallocated_strassen_compression/REPORT.md`.

### H40: independent compression judge narrows the honest upside

The score product law is per-network; aggregate ratios require score-weighted
paired products. The ideal unchanged-prediction floor gain is7.3056x, not the
mean-multiplier ratio7.4368x. Mutation B's.885099x result is one full-product
proxy. Even granting it to all184.822B matmul work inside202.282B mean cost
gives only.8950165x whole-entry cost, an optimistic10.50% ceiling and about
2.0201e-7 adjusted score under unchanged uniform predictions. Actual eligible
fraction, integrated residual, live memory, and MSE parity are unmeasured.
Therefore validated deployable compression gain is0%; optimistic exact upside
is0-10.5%. Amplitude/quotient results remain oracle-RHS geometry, and Q2
correction uses supplied conditional state plus exact downstream mean/variance
for isolation. Source: `../compression_judge/JUDGE.md`.

### H41: Q4 finds higher-moment signal but explodes the contraction

Holding the Q2 state fixed and adding exact ReLU coefficients through order4
raises isolated conditional k3/k4/combined fidelity from
.670685/.162341/.282335 to.732135/.655277/.673419. Transported
combined/correction reaches.931300/.979659 with60/61 signs. Exact
graph/automorphism folding, symmetric-power identities, Q2 reduction,
permutation, and positive-gauge tests pass below2.075e-14. The child still
misses every.8 isolated energy gate, while40 cubic and428 quartic folded
terms cost a conservative35.115T,438.94x the80B ceiling. Preserve the exact
operators; do not try Q6. Condition on the rank4 common factor and integrate
the exact independent conditional response over four dimensions instead.
Source: `../price_hermite_q4_response/REPORT.md`.

### H42: relative wall was a campaign gate, not a score term

Local source tracing proves effective compute is billed FLOPs plus1e11 times
residual user time. Counted NumPy/BLAS backend time and FlopScope overhead are
reported separately and excluded from residual. Total wall binds only through
absolute limits:30s host response and60s worker context locally. Thus the
preallocated branch's1.5x parent-relative wall gate cannot be retroactively
passed, but its failure does not kill score viability. A pessimistic median
29-full-call extrapolation is about6.67s, not a bound. Open a causally new
full-entry synthetic Batched-B trace with setup<4s,predict<20s,complete C,
memory liveness,eligible shapes,and prediction parity before any data row.
Source: `../wall_rule_audit/AUDIT.md`.

### H43: full-entry Batched-B saves score cost and fails only liveness

The actual fresh synthetic random32,256 fold3 geometry ran atn_base32256 with
no extrapolation. Batched Winograd selected16/29 hooks covering57.416% of
their direct bill. Analytical/effective work fell170.531B->159.493B and
186.485B->175.521B, ratio.941206. Prediction parity is4.56e-8 relative;
depth32 error2.49e-6 with1/4194304 gate change; setup.646s,predict4.427s;
dispatch and explicit full/even/odd/ragged probes pass. The only failed gate
is measured peak working set667.328MiB versus512MiB, while end set478.883MiB
proves transient workspace/activation overlap. Preserve the 5.88% effective
cost reduction. Row-block the left/products at fixed8192 rows, pack right
operands once, and reconstruct directly into the final output; every billed
term is linear in row count. Source:
`../integrated_batched_winograd/REPORT.md`.

### H44: common-factor conditioning compresses Q4 by472x but exposes prior error

Conditioning the rectified-Gaussian copula on its rank4 common factor makes
coordinates independent and analytically resums every Hermite order. A fixed
49-node four-dimensional Smolyak rule reduces the conservative envelope from
35.115T to74.427B and keeps transported combined/correction fidelity
.935843/.979747. Direct response remains wrong: isolated k3/k4/combined is
.72739/.52036/.56923, while the201-node reference reaches only
.72658/.69626/.70341. The49-node rule also fails convergence(.12403 squared
discrepancy) and arbitrary factor rotation(.19931). Preserve exact conditional
moments and total-cumulance integration. Canonicalization can repair grid
gauge, but no Gaussian quadrature creates the missing signed within-cell
non-Gaussian state; a per-layer innovation observable is the next information
link. Source: `../latent_copula_resummation/REPORT.md`.

### H45: fixed8192-row streaming clears the exact-compute engineering gates

The integrated Winograd score operator was preserved while only its transient
liveness graph changed. Streaming the seven left/product stacks in fixed8192
row blocks reduces operator workspace from283.9375MiB to91.4375MiB and peak
working set from667.328MiB to474.301MiB. On the actual n_base32256 synthetic
geometry, analytical work falls170.531B->159.493B and effective compute falls
188.819B->175.926B, ratio.931714, with exactly11.037909953B FLOPs saved.
Whole-prediction relative drift is4.282e-8; depth drift is2.486e-6 with one
gate change in4194304; static and ragged billing audits have zero mismatches.
All frozen synthetic gates and five tests pass. This is a screened engineering
survivor, not yet a champion: the next rung is an immutable production port
and separately frozen paired score on permitted development rows. Source:
`../row_blocked_winograd/REPORT.md`.

### H46: factor gauge is repaired, but the Gaussian copula prior still fails

Canonicalizing the rank-four factor through eigenspaces/projectors of B^T B
reduces equivalent-rotation defect from.19931 to1.68e-26 and49/201 discrepancy
from.12403 to.07386. Transported combined fidelity remains.93083 and cost is
74.5661B. Yet isolated k3/k4/combined is only.72568/.64447/.66364, and the
canonical201-node combined result is.67573; one of96 cells also triggers the
forbidden projector fallback. Thus arbitrary sparse-grid orientation was a
real numerical defect, but not the information bottleneck. Preserve the
canonical gauge operator; another grid cannot create missing signed
higher-order layer state. Source: `../canonical_latent_copula/REPORT.md`.

### H47: a clean-room PLE pattern compresses static analytic response tables

The Gemma4 PLE architectural separation was translated without model weights,
outputs, downloads, or APIs. Exact layer invariance factors a duplicated
2,097,536-byte Phi/phi response atlas into one65,672-byte shared atlas plus
descriptors/schedules; the complete package is66,632 bytes and maximum
expanded-response error is1.994e-7. Five fresh subprocesses give a.763 median
factorized/parent warm-latency ratio and eight tests pass. Conservative lookup
accounting is41 operations/query versus56 for the known float64-promoted path,
but loses to a hypothetical native-float3228-operation lower bound. Flash is
cold immutable storage; setup preloads65.5KiB and CPU/RAM performs the math.
Preserve the sidecar/locality mechanism, but do not fold it into the champion
until a fused whole-estimator cost gate passes. Source:
`../ple_flash_sidecar/REPORT.md`.

### H48: production row-blocked Winograd is the new validated local champion

The exact fixed8192-row survivor was ported into an immutable seven-module
descendant of random32,256 fold3. It passed131072 shape-bill checks,96768 row
partitions, package validation, synthetic parity/depth/memory gates, and stable
source hashes before any score. On the one frozen paired run over already-used
public rows0..99, adjusted score falls2.257079776e-7->2.121762464e-7,
ratio.940047616 (-5.99524%). Raw MSE ratio is.999982962; mean effective compute
ratio is.938554853; max child C is222.405357B; failures are0/100 and the child
wins100/100. A one-million paired network bootstrap gives score-ratio95% CI
[.936501313,.943475999]. The validated tar contains exactly seven Python
modules plus manifest and remains unsubmitted. This is the new local champion,
not a guaranteed private-suite winner. Source:
`../row_blocked_production/REPORT.md`.

### H49: exact terminal-Q2 resummation proves the state, not the map, is wrong

The terminal Q2 chaos has an exact characteristic function, so its positive
part can be integrated without a finite Edgeworth truncation. Four structural
tests, six Monte Carlo scalar cases, orthogonal invariance, and a54.924B
conservative target envelope pass. On the frozen reused public0..4 gate, the
exact Fourier map scores5.389991258e-5 versus5.388358479e-5 for native Q2
Edgeworth, ratio1.000303; variance rescaling is1.002602. Therefore another
terminal quadrature, cumulant order, or scalar response formula cannot repair
this state. Preserve the exact characteristic-function positive-part operator;
the upstream signed innovation is binding. Source:
`../quadratic_chaos_fourier/REPORT.md`.

### H50: coordinate-product TT cross is killed at the first dense ReLU

A three-node Gaussian product grid was tested as a vector-valued TT-cross
route that could share each forward query across all outputs. The weighted
unfolding is an oracle rank ceiling: its Frobenius norm is exactly the discrete
product-measure L2 norm. At5e-4 relative tolerance, one dense ridge ReLU needs
balanced ranks21--52 across frozen dimensions/orders; a nondegenerate
width10/depth4 output needs197--207. Rank8 leaves.0064--.0118 ridge error and
.364--.382 deep error. The maximum nominal target one-sweep query count is
32,908,032 before pivoting or additional sweeps. Kill standard full-function
TT-cross/PCE quadrature; preserve weighted-unfolding rank tests and all-output
query sharing as separate observations. Source:
`../tensor_train_gaussian_cross/REPORT.md`.

### H51: signed gate-boundary innovations expose a strong mean direction

An exact Gram--Charlier boundary operator computes ReLU raw moments through
four and feeds a weights-only signed H1+H2 latent recurrence. Across six fresh
clean-room cases, signed feedback cuts final-mean SSE to.231176x erased or
Gaussian reclosure with6/6 wins; stripping sign is much worse. Seven tests,
permutation/gauge covariance, validity rescue, and a44.248B envelope pass.
The carrier fails: terminal k3/k4/combined fidelity is.61225/-1.32430/-.84622
and18.06% of q2 marginal skews clip. Preserve the boundary integrals, signed
inversion, and causal mean direction; kill the literal q2 state. Source:
`../signed_gate_innovation/REPORT.md`.

### H52: an exact diagonal vertex proves the missing innovation is cross-neuron

Keeping q2's correlated sector and transporting exact marginal residuals as
`eta_p dot W^p` reconstructs every supplied marginal at identity, preserves
symmetry, passes six tests, and costs44.289B. On a disjoint nine-case bank it
retains sign utility and scores.710670x erased with7/9 wins. It does not repair
the state: mean SSE is1.14035x the q2 parent and k4/combined worsens to
-8.90676/-6.74770. Only0.00915% relative marginal-skew residual energy remains,
while cross-coordinate terminal k3 is still wrong. Thus the required object is
a coherent low-rank cross-coordinate signed vertex retaining all-distinct
cancellation, not denser marginal cumulants or a fitted scalar. Source:
`../diagonal_vertex_innovation/REPORT.md`.

### H53: fused two-level row Winograd passes the synthetic exact-compute gate

The current fixed8192-row L1 operator was composed with a fixed6144-row fully
fused L2 schedule: outer transforms feed49 inner leaves, one batched matmul
evaluates them per block, and overwrite-safe buffers share the L1 aliases.
Across131072 shape checks and96768 row partitions, no dispatcher bills worse
or mismatches the analytic law. A fresh full synthetic entry gives analytical
ratio.962950, effective ratio.943797, wall ratio.926760, peak492.441MiB,
prediction error4.732e-8, and depth error4.709e-6 with7/4194304 gate flips;
five tests pass. This is a screened survivor, not yet a champion. Freeze its
dispatcher/block sizes and require an immutable production package plus a
separately declared paired score gate. Source: `../two_axis_winograd/REPORT.md`.

### H54: causal composition replaces an exponential mashup search

Fifty-nine live uncertainties are now registered with exact resolving tests,
and every reusable component has a typed input/output, bias class, cost, and
diagram ownership boundary. The immediate coherent super-candidate is
random32,256 -> row-L1 -> fused-L2 exact compute. The coherent analytic path is
fullcov -> signed gate-boundary innovation -> missing cross-coordinate lift ->
64D/58D quotient -> rank4/12D total-cumulance transport -> exact positive-part
map. Routers, JSpace geometry, PLE storage, and sampler controls can attach
only after their required observable/expert interfaces exist. Summing killed
leaves is forbidden when it double counts diagrams, repeats a no-op, or mixes
independent point families under the mediant law. Sources:
`../UNCERTAINTY_REGISTER_20260806.md` and
`../COMPOSITION_CLOSURE_20260806.md`.

### H55: ownership, source rank, chaos closure, and launchability form four separate gates

M71 shows that the Kerdock/WHT geometry can be made deployable when **active
path ownership** is explicit: one activation backing plus row-local Winograd
overwrite passes generated parity, billing, residual, and a478.555MiB peak.
This is an engineering survivor, not an accuracy result. M76 adds only a
target-neutral validator fallback; its sealed package validates while the
width256 path is bitwise unchanged. M77 then kills the frozen descriptive
launcher before WHest starts: a duplicate `Path`/`PATH` process-environment
key yields zero candidate rows, so no score conclusion exists and no rerun is
allowed.

M73 and M74 divide the analytic bottleneck cleanly. The signed first-gate
source has exact CP linear transport, but fixed CP rank loses the source or
requires348.966B charged source formation. TT retains non-diagonal linear
structure (rank8 depth2 combined fidelity.984247), yet a finite Hermite
alphabet has first-gate k4 error.769328 and the next preactivation is already
non-Gaussian. The resulting graph edges are: `active-path ownership ->
deployability`; `signed-source formation -> rank compression`; `ReLU source
alphabet -> chaos closure`; and `frozen operational launcher -> evidence
availability`. These are causal gates, not interchangeable optimizations.
Sources: `../kerdock_l1_owned_buffer/REPORT.md`,
`../kerdock_l1_owned_buffer_production/DESCRIPTIVE_REPORT.md`,
`../m73_signed_source/{DERIVATION.md,results.json}`, and
`../m74_chaos_tn/{DERIVATION.md,results.json}`.

## Current non-working translations

Literal quantum retinal pigment, generic memristor language, tau numerology,
reaction-diffusion without an equivariant update, generic active subspaces,
generic copulas, generic TAP/AMP, fixed scalar resummation, fixed kernel
reweighting, direct parity folds, and public-set memorization do not currently
supply a working legal mechanism. Their tested implementations remain evidence
and mutation prompts; a descendant must name the changed causal link and pass
the same external gates rather than relying on the metaphor alone.

### H56: M78 separates an exact common-frame endpoint from MLMC efficiency

The registered homogeneous Huber ladder is a genuine exact finite source when
every adjacent level, antipode, and final residual share the same outer Haar
frame:

```text
common-frame Huber endpoint telescope -> exact angular ReLU endpoint
outer-Haar randomization + radial covariance -> marginal Gaussian mean
```

The synthetic unit cell passes finite-telescope cancellation (`2.776e-17`),
the level-20 limit diagnostic, and a lower coarse variance on all four frozen
generated units. Its observed correction decay is also real: the physical
exponent is `beta=2.592495`. These are preserved deterministic operators and
diagnostics, not an efficiency result. The frozen gate asked for a *positive*
log2-variance slope, while the recorded decaying sequence has slope
`-2.592495`; the independent judge correctly keeps that literal gate failed.

The causal failure is instead:

```text
early coupled Huber corrections + two whole Huber evaluations
    -> sum sqrt(V_l C_l)
    -> MLMC variance-times-work rho = 3.0985..3.2836 (mean 3.1576)
    -> registered Huber/Haar unit-cell rejection
```

The independent accounting recomputation confirms every `rho>1`; even adding
a nonnegative common Haar-frame construction charge leaves the optimistic
infimum above one. A roulette estimator was not executed. Preserve only its
conditional theorem: a future child must predeclare an independent survival
sequence, charge sampled levels, and change the coupling/cost mechanism. It
cannot delete early corrections, reinterpret the slope, or promote the base
variance reduction.

### H57: M79 separates a valid contrast diagnostic from shrinkage utility

M79's streamed common-axis contrast statistic and direct stream form a valid
deterministic accounting chain:

```text
streamed contrast sums -> unbiased trace contrast-variance diagnostic
diagnostic overhead -> 1,045-path cost-matched direct baseline
contrast signal-to-noise -> utility of common-axis shrinkage
```

The first two arrows pass: the direct comparator costs 39,125,056 operations,
below M79's 39,128,843 proxy, and its 21 extra paths are deterministic stream
continuations. The numerical nonnegative clamp was inactive in the reported
units, but must be explicit in a future predeclaration. The nonlinear shrinker
is nevertheless biased conditional on fixed weights because its lambda is
sample-random; the unbiased diagnostic does not change that bias class.

The utility arrow fails on all four frozen whole-network units. Their true
contrast energy is `328..401` times the estimated contrast-noise energy,
lambda is only `.002476..003069`, and M79/direct-cost ratios are
`1.026241..1.075922` (mean `1.049986`, 90% bootstrap
`[1.035346,1.071690]`). Thus nearly inactive contraction plus the streaming
statistics loses to direct sampling. Preserve the Vhat/LOO/risk identities and
the separate known-variance spherical-Gaussian James--Stein theorem; kill this
same-run common-axis positive-part rule, post-hoc unit selection, and any
claim of an M71 or official-score improvement. A declared independent
ensemble-Bayes prior would be a distinct future family, not an M79 repair.

### H58: M80 keeps Kerdock tangent recurrence as an unresolved edge

M80 supplies a clean fixed-coefficient, exact matched-work comparison after a
geometry change:

```text
Haar-rotated Kerdock node + fixed network -> E_Q Delta = 0
    -> MSE-difference cancels to population rotation-variance difference
matched factorial tangent work -> frozen/zero conditional variance ratio
```

The identity is deliberately narrow. It validates comparison of the retained
inherited tangent with `lambda=0` over the population of Haar rotations, not
truth error, estimator bias, MSE, or score. Frozen replay, hash, and equal
tangent-work checks pass. The aggregate ratio `.9793799245` is directionally
favorable, but seed 271 is adverse (`1.0044348946`) and no LONO ratio satisfies
the declared `<.97` strength threshold. M80 therefore cannot delete the
recurrence and cannot retune its inherited coefficient.

```text
Kerdock geometry + inherited tangent -> heterogeneous variance response
    -> M80 screened/uncertain
```

Preserve the factorial harness and the fixed-coefficient Haar-variance
criterion. The unresolved causal edge is whether a distinct, preregistered
Kerdock-specific coefficient or removal can stabilize at fixed network and
hosted conditions, after charging the removal's real cost.

### H59: M81 kills full129 on the static ownership/cost edge

The full real-MUB union has a real structural benefit: its 129 antipodal
directions form an exact spherical 5-design, with `A2=A4=0`; trimming to 126
directions leaves `A4=.047422179`. But the retained coordinate-basis members
increase paths by `43/42` (`64512->66048`).

```text
full129 degree-four exactness -> possible low-order variance benefit
43/42 path count + persistent terminal state -> hosted memory margin failure
unmeasured variance benefit + proportional cost -> no Pareto promotion
```

The minimal persistent increment `1.75195 MiB` exceeds M71's `1.44531 MiB`
margin before terminal arrays. The proportional `198.408B` C envelope is not
a source-level bill, and adjusted-score break-even requires a raw MSE gain
above `2.3256%`. Thus static exactness does not repair the ownership/cost
edge. Preserve the full construction, coordinate handling, exactness proof,
and algebra; a reopened child must alter path/terminal ownership or measure
subproportional cost, then pass fresh resource and hosted validation.

### H60: M82 separates conditional variance from causal geometry and MSE

M82 lawfully maps M71's geometry seed to its Haar orientation and formal L1's
seed to independent QR Haar frames, and it deterministically computes the
conditional output-covariance trace on four fixed networks. Its aggregate
Kerdock/Haar ratio is `.9025561669`, but its whole-network bootstrap95%
interval `[.60132681,1.35006446]` crosses one, with two networks favoring Haar.

```text
frozen Kerdock WHT/owned-buffer backend -> conditional variance
frozen L1 QR-Haar/row-blocked backend -> conditional variance
different operation schedules and randomizations -> backend-confounded ratio
```

This is not a geometry-only intervention: the cells are not software-identical
and do not use common random numbers. Moreover
`MSE(T|W)=tr Var_R(T|W)+||E_R[T|W]-target(W)||^2`; neither target nor conditional
mean was observed. The ratio therefore supports neither a causal geometry
claim nor any MSE, bias, adjusted-score, or winner inference. Preserve the
seed-law, covariance-trace, and whole-network-bootstrap operators. Reopen
only with a preregistered common numerical path plus a distinct bias/MSE
observable; no seed selection or coordinate bootstrap repairs this evidence.

### H61: source formation is distinct from transport and compression

M85, M87, M90, and M91 separate a previously conflated causal chain:

```text
fixed-network 3-/4-unique non-Gaussian source
    -> transport or motif contraction
    -> compression or stochastic sketch
    -> terminal mean estimate
```

Exact bivariate bridges, shared-middle contractions, signed low-rank factors,
and unbiased trace probes are downstream consumers. None manufactures the
required source. M85's novel multiplicity strata fail even when aggregate
entries look good; M87 omits a source whose construction is itself over
budget; M90 shows only the nonlinear bridge residual is low-rank; M91 shows
the full-cycle sketch retains ordinary `1/s` variance. Every child must expose
and bill a source observable before compression, and must test 1-/2-/3-/4-
unique index strata separately.

### H62: connected first-chaos cancellation opens only a narrow door

For centered standardized ReLU `g(Z)=c1 Z+H(Z)`, the pure all-linear Gaussian
connected third and fourth cumulants vanish exactly. The survivor is not a
free deletion of every linear-looking cycle: a four-cycle has Hermite vertex
degrees `(2,2,2,2)` and coefficient `1/(pi-1)^2`, so it is nonzero.

```text
raw bridge full-rank linear bulk -> absent in pure connected k3/k4
mixed H/linear vertices -> necessary fixed-network source -> unresolved
```

Preserve the first-chaos split and diagram-degree rule. A successor must build
the mixed vertices with repeated-index parity and a complete resource trace;
M93 licenses no subtraction from M87's billed cycle.

### H63: boundary exactness and boundary efficiency are separate nodes

M86 proves the signed spherical coarea/output-fan identity, and M95 validates
a local d=2 inclusion probability equal to the preceding sector gap divided
by `2*pi`. M89 and M95 then kill complete-circle and uniform-first-crossing
economics by wide equal-work margins.

```text
exact signed facet calculus -> mathematical target
computable output-facet inclusion law -> unbiased proposal
proposal variance times complete work -> deployment value
```

Only the first node is general. Future boundary work must change the proposal,
prove one-owner output-facet coverage, retain zero-jump events explicitly, and
beat direct antipodal sampling after all failed roots and adjoints are billed.

### H64: transport attention is a carrier, not an observable

M98 independently validates a permutation-equivariant source-to-current
transport, a correctly trained zero-message control, and a message-only
intervention that leaves the Gaussian anchor bitwise fixed. It nevertheless
fails validation and extrapolation coverage, full-versus-control, and causal
edge-removal gates.

```text
permutation-safe transport + local Gaussian fields -> modest predictive signal
missing weights-derived closure state -> no nonincremental gain
```

M98 closes parameter and epoch retuning of this carrier. A successor must add
a mathematically distinct, weights-computable state and show by prospective
ablation that this state, not carrier capacity, produces the gain.

### H65: learned causal comparisons require capacity and optimizer parity

M97 fails because its node control is trained with messages and evaluated
without them. M98 repairs that mode but uses an undeclared optimizer-order
seed difference. M99 then compares a 4,601-parameter Hermite arm with a 2,441-
parameter raw arm. These are protocol failures, not favorable evidence.

A valid comparison uses the same input width and parameterization, a bitwise
identical initial state, separately reset identical whole-network training
orders, the same target/anchor, retained reference precision per network, and
a model artifact only if every gate passes. Zero-padding a raw 45-channel
control into a common 188-input carrier isolates added features while a
feature-specific shuffle tests their node association.

### H66: the input layer is an identity-chaos boundary

The source before the first affine map is an identity standard Gaussian, not
a rectified source. Its exact Hermite response is
`(gamma1,gamma2,gamma3,gamma4)=(1,0,0,0)`. Node-specific rectified-normal
responses begin only after the first ReLU gate.

```text
identity input boundary -> first affine transport
rectified hidden source -> node-specific gamma(alpha)
```

M99 violates this boundary and injects spurious degree-two and degree-four
input responses, so it is rejected before targets. M100 repairs the boundary
and matches raw-control architecture, but remains a generated hypothesis with
no target, training, score, or deployment evidence until its frozen gates are
executed and independently judged.

### H67: Hermite transport decomposes into raw scale plus centered association

For each edge kernel `K_r in {W,abs(W),W^2}`, source state `S`, and source
Hermite mask `gamma_q`, the transported message obeys the exact identity

```text
K_r^T diag(gamma_q) S
  = mean(gamma_q) K_r^T S
  + K_r^T diag(gamma_q-mean(gamma_q)) S.
```

The first term is a scaled raw transport. The second is a genuinely new
source-node/edge/state association unless the mask is constant or a specific
nullspace cancels it. Four masks are structured functions of one scalar alpha,
not twelve independent information sources. A clean learned successor keeps
the raw transport explicitly and appends only the centered residual, with a
same-architecture raw-plus-zero-residual control. This makes the baseline a
nested submodel and tests the actual new observable rather than replacing it.

### H68: stable tails and coherent ablations are part of the mathematics

The exact standardized rectified-normal Hermite responses tend to zero as
`alpha -> -infinity` and to `(1,0,0,0)` as `alpha -> +infinity`. Computing
`Phi(alpha)` as `.5*(1+erf(alpha/sqrt(2)))` catastrophically cancels in the
negative tail; a variance clamp then turns roundoff into coefficients as large
as `2.1e8` at alpha `-6`. Float64 postpones but does not remove this failure.

A valid carrier computes the lower tail with `erfc`, evaluates truncated
moments/variance stably in float64 or by Mills-ratio asymptotics, tests both
dtypes across the tails, and only then casts. An association shuffle must move
the whole four-component gamma row together; independent per-q permutations
destroy the identities linking coefficients and confound node association
with invalid cross-channel geometry. Zeroing the centered residual while
preserving raw messages is the clean primary ablation.

### H69: M104/M105 repair reproducibility and evidence, but not causal capacity

M104 freezes a complete nested-Hermite runner with tolerant permutation tests
and per-network checkpoints, but is rejected before targets: construction is
not seeded, declared gradient clipping is not executed, required tail and
decomposition regressions are omitted, the promised shuffle is not measured,
and numeric gate summaries are discarded. M105 repairs those defects: it seeds
before construction, reads and applies the frozen optimizer/clipping settings,
passes tail/decomposition/layer-zero/symmetry checks, retains summaries, and
measures the shuffle descriptively. No target, training, reference, learned
artifact, or resource trace was run by either rejected packet.

### H70: nominal capacity is not effective capacity

M105 stores 5,321 parameters in both arms, but its raw arm feeds literal zeros
to all 180 centered channels of a `233 -> 16` first carrier layer. The
resulting `180 * 16 = 2,880` weights have exactly zero gradient, leaving a
2,441-parameter effective trainable upper bound versus 5,321 live treatment
parameters. A full-versus-raw result therefore confounds centered-Hermite
association with added active feature-mixing capacity and cannot be the sole
binding attribution gate.

### H71: an active shuffled-association null is the causal repair

The repair is a separately trained active-null arm that keeps all 233 inputs
and 2,880 centered-slot weights live, but coherently permutes each whole
four-coordinate gamma row by deterministic network/layer seeds in both
training and evaluation. It preserves gamma marginals and centered-slot
variance while removing source-to-current association. The existing M105
coherent shuffle is only a post-training descriptive sensitivity check; it
cannot repair the trained-control confound. M106 freezes this null as the sole
binding mechanism control, with raw and centered-zero only descriptive.

### H72: durable failure evidence needs one owner

M105's inner build handler writes detailed failed-network context, then
rethrows; the outer handler overwrites that record with generic
`phase=build`. The final artifact can therefore lose the failed split, index,
seed, and shape. A successor needs one authoritative writer or explicit
context propagation, so the failure path is as forensically complete as the
success path.

### H73: Phase-2 transformer legality is conditional, not a loophole

The rules audit permits a small deterministic transformer/attenuator only when
it ships with pickle-free frozen parameters, uses permitted runtime operations,
and bills all per-MLP feature, attention, routing, and residual work. It must
be generated-data trained, target-independent, network-free, and within
compute/time/memory/package limits. Runtime Torch, APIs, external models,
hidden state, and uninstrumented arithmetic treated as a billing escape are
forbidden or unusable. The published Phase-2 multiplier floor conflicts between
live prose (`0.5`) and local/official v0.14 materials (`0.1`), so width or
sample-count designation requires organizer confirmation.

### H74: M106 is an empirical kill with preserved causal machinery

M106 ran once on hash-frozen generated-only splits and is killed as a learned
recursive terminal estimator. All 416 references passed final precision with
no escalation, but every binding performance and attribution gate failed.
Validation treatment geometric anchor-MSE ratio was `0.476268`, arithmetic
bootstrap-95 was `1.396287`, and coverage at ratio `<=0.10` was `0.085938`.
Extrapolation gave `0.483090`, `0.734339`, and `0.062500`, respectively. No
learned artifact, target-scale resource trace, package, upload, submission, or
contest-data evaluation exists. Preserve the stable gamma/decomposition math,
active-null control, reference firewall, and durable raw-evidence harness.

### H75: validation establishes association parity, not causal gain

M106's active null keeps all 233 inputs and all 5,321 parameters live while a
fixed coherent whole-gamma-row permutation removes source-node association.
Treatment/null validation aggregate mean-MSE ratio was `0.948938`, bootstrap
interval `[0.771820,1.195607]`; treatment won `46.09%`, and its paired
geometric ratio was `1.066918`. This is parity and fails the predeclared
fourfold gate. The null is a validated ensemble-matched causal control, not a
deployable estimator: its fixed row pairing is deliberately non-equivariant.

### H76: the depth-6 association effect is exploratory only

On the post-hoc width-12/depth-6 slice, treatment/null aggregate mean-MSE ratio
was `0.632981 [0.476066,0.847632]`, paired geometric ratio was `0.573731
[0.439064,0.747783]`, and treatment won `71.875%`. Absolute quality still
failed badly: geometric anchor ratio `0.483090`, arithmetic ratio `0.620992`,
and only `2/32` networks reached `<=0.10`. Correct association may become more
informative with depth, or the non-equivariant null may become more destructive.
This unregistered interaction is a mechanism clue only; it cannot justify an
M106 retry, target-scale extrapolation, checkpoint selection, or promotion.

### H77: deterministic association-to-mean closure is hard-killed

The exact centered association `C(W)` retains source-node/edge/state pairing,
but it is not a fixed-network expectation or a third/fourth cumulant identity.
A learned deterministic `C -> mean` or low-rank moment correction remains an
approximate-mean estimator, lacks an exact debiasing identity, and is not closed
through 31 ReLU layers. It is hard-killed unless a future derivation supplies
an exact fixed-weight source identity, a bound on every omitted contribution at
`L/n=1/8`, and an exact-mean debiasing theorem.

### H78: M107 changes bias class to exact-zero degree-6/8 controls

The surviving bridge uses centered association only to choose frozen
coefficients or directions for even degree-6/8 input controls whose conditional
mean is proved exactly zero. Subtracting those controls from sampled MLP output
preserves the exact conditional mean for every frozen network, even when the
coefficient predictor is inaccurate. Odd degrees are already antithetically
killed and degree two is frame-exact. For the actual spherical/radial sampler,
the control must use its analytic matched-law mean or prove zero angular mean;
Gaussian Hermite zero-mean cannot simply be assumed after changing the sampling
law. M107 is one cheap falsifier, not a promoted estimator.

### H79: held-block independence marks the bias-class boundary

Weights-only coefficients frozen before sampled paths are conditionally
unbiased without cross-fitting. If coefficient estimation uses sampled frame
blocks, it must be cross-fitted: fit an oracle or ridge coefficient on seven
independent blocks and score only the held eighth. The first falsifier compares
held-frame `variance(residual)/variance(base) * cost_ratio` with one; a value
`>=1`, or a benefit unchanged by coherent association shuffle, hard-kills the
bridge. This independence is what changes the proposal from deterministic
approximate-mean regression to an exact-mean sampling control.

### H80: the M106 launch defect is localized to a redundant precheck

Immediately before launch, root successfully verified all ten manifest hashes
and absence of target/model artifacts. A wrapper then repeated those checks
using paths relative to a working directory already inside the packet; both
lookups failed nonterminally, after which the frozen runner executed exactly
once and its artifacts independently recomputed exactly. This is an honest
orchestration defect in a redundant precheck, not an estimator or evidence
defect, and it does not authorize a retry.

### H81: M107 is a degree-4/6/8 exact-zero spherical control, not degree-6/8 only

H78/H79 described an earlier proposal and are superseded here on dictionary
and split details. The frozen M107 run used six controls: normalized spherical
Gegenbauer degrees `4,6,8`, each mixed over normalized W1-column gate axes by
either uniform weights or frozen normalized squared downstream-path energy.
For `U ~ Unif(S^255)` and every weights-fixed unit axis `a`,

```text
E[P_l(a.U)] = 0,  l > 0
E[sum_j omega_j(W) P_l(a_j(W).U) | W] = 0.
```

The complete Haar frame annihilates degree two, not degree four; degree four
therefore belongs in the L1-frame dictionary even though a true spherical
5-design would remove it. M107 reused `first_pre` to obtain the cosines and a
single stable recurrence through degree eight. Because output-specific ridge
coefficients used sampled paths, the actual information screen fit on 16
independent training frames and evaluated raw, no-intercept adjustments on 16
independent held frames. This independence preserves the exact conditional
mean; the discarded training paths produce the explicit twofold cost dilution.

### H82: M107 fails on all four held networks through unstable association

M107 passed 24/24 preexecution tests, source/provenance checks, rank-six design
checks, recurrence and numeric guards, then worsened held trace variance on
every fresh generated width-256/depth-32 network:

```text
held adjusted/base ratios  1.2349683  1.2533812  1.3637836  1.1312104
geometric information      1.2431025
pooled information         1.2561862
exact bootstrap q05/q90   [1.1819513, 1.3025892]
charged-efficiency proxy   2.5181387
```

Training-only ratios `0.68854--0.76158` reverse above parity on every held
network. The killed link is stable frame-level covariance/coefficient transfer,
not the exact-zero theorem, W1 orientation, first-pre reuse, recurrence,
cross-fit boundary, or generated-only evidence harness. Ridge, degree, split,
mixture, axis, and seed retuning are not licensed by this result.

### H83: cymatic heat amplitude and energy die at the fourth moment

M108 translates a Chladni displacement into a fixed even spherical heat band
over degrees `8,10,...,32`, centered at degree 18, and Chladni intensity into
`B^2-1`. Both have sound recurrence and exact mean laws, but exact no-network
Gauss--Jacobi and Dirichlet calculations expose a fatal high-dimensional tail:

```text
single-axis E[B^4]                         2.046953098540e23
Var(B^2-1)                                 2.046953098540e23
linear-band kurtosis after frame+256 axes  3.123400620022e18
```

The energy branch breaches its frozen excess-kurtosis cap of 50 by roughly 21
orders of magnitude. Squaring self-convolves the band into degrees through 64;
aggregation cannot average away the single-axis fourth moment. Heat and
Poisson coefficient vectors are almost identical on the frozen band (cosine
`0.9999410374`), so changing the physics label is not a causal repair. M108's
scaled-linear and centered-energy implementations are killed before any
network, while the exact recurrence and mean identities remain preserved.

### H84: M109 changes only the tail edge to bounded nodal occupancy

The proposed cymatic descendant replaces amplitude with one frozen gate-band
occupancy:

```text
h_a(U) = 1(|a.U| <= 1/16) - p_256
p_256  = I_(1/256)(1/2,255/2)
       = 0.682130341244403596600209971528792088853759588749794131865380443105933790468481686914264874848114296246759912424716118285.
```

Since `(a.U)^2 ~ Beta(1/2,255/2)`, the atom has exact weights-conditional
spherical mean zero and is bounded. M109 retains only two nonadaptive mixtures,
uniform and normalized squared downstream-path energy, and reuses L1's
`first_pre` cosines. This is a one-causal-edge mutation of M108: bound the
needle-like amplitude before centering. It is an unrun, target-free, unfrozen
source draft, not a score, survivor, or submission candidate. Its discontinuous
broad spectrum may still have zero useful held covariance or lose after full
cost. Only the specified no-network beta-law/invariance/moment gate may precede
a separately frozen generated screen; the `1/16` threshold cannot be swept.

### H85: M109's bounded tail passes, but its exact source fails statically

An independent no-network judge rejects the current M109 draft before freeze.
For `U ~ Unif(S^255)` and fixed unit `a`, the density exponent is
`(d-3)/2=126.5`, not 126. The correct fixed-band probability is

```text
p_true = I_(1/256)(1/2,255/2)
       = 0.68174151824134440702724427524261793438128145340916676300176860652683781465121576471930478207314735154551264739774652570560463612775821697079...
```

The draft's `0.6821303412444035966...` comes from integrating
`(1-t^2)^126` against a prefactor for the 126.5 law. Its implemented atom
therefore has mean `p_true-p_draft = -0.00038882300305918957...`, not zero.
The duplicated polynomial test repeats the same dimensional error and cannot
independently certify it.

The uniform normalized-axis mixture is positive-ReLU-gauge invariant. The
squared-path mixture is not: under `W1[:,j] -> c_j W1[:,j]` and
`W2[j,:] -> W2[j,:]/c_j`, its path weight gains `c_j^-2` while the normalized
axis stays fixed. A possible `||W1[:,j]||^2` compensation is a new operator,
not a repair that can be inserted post hoc.

The current M109 source/configuration is thus killed preexecution on mean law
and representation invariance. The bounded indicator still removes M108's
astronomical amplitude tail, and the corrected uniform family remains an
unimplemented, unresolved salvage atom. No network, target, scorer, freeze,
package, or submission was run.
