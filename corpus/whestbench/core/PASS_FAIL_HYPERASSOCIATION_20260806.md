# Pass/fail hyperassociation ledger

Date: 2026-08-06. This review separates component validity from end-to-end
contest fitness. A branch is promoted only if its entire causal chain passes:

`representation -> observable -> estimator -> cost -> held-out score -> package`.

Passing an earlier link does not rescue a later failure.

`Hard kill` in this ledger means the fully specified implementation failed its
declared gate. It does not dismiss the broader idea family. Passed components
and exact constraints are retained in `SALVAGE_MAP_20260806.md` and may be
reopened only through a new causal mechanism.

## Evidence grades

- **A**: exact theorem or official paired result with preregistered gate.
- **B**: deterministic small-shape premise with exact reference.
- **C**: development-only exploratory measurement.
- **O**: oracle result; proves value of unavailable information, not a method.

## Branch ledger

| Branch | What passed | What failed or remains | Grade | Decision |
|---|---|---|---|---|
| Random 32,256 | Official100, zero failures, Cmax 250.489B, adjusted-score gate; package parity and validation | Raw MSE is 14.71% worse on both-success networks | A | Promoted deployable fallback |
| Recursive fold 39,936 | Strong raw variance on small screens | 5/100 official combined-budget failures; Cmax 294.999B | A | Demoted unsafe |
| Kerdock/MUB | Exact construction, 17 tests, low-degree cubature benefit | Structured activation patterns caused nonlinear cost excess and failures | A/B | Reject deployed form |
| Full-covariance Gaussian | Numerical equivalence, cheap cost, 17.25x over diagonal | Raw MSE 5.43e-5; repeated re-Gaussianization loses finite-width dependence | A | Use as H1 anchor only |
| Terminal true k3/k4 | Oracle MSE about 4.7e-8 | Information is unavailable at acceptable cost | O | Mechanism evidence only |
| Terminal analytic/crossfit k3/k4 | Exact formulas and implementation checks | 0.493% analytic gain; crossfit variance-cost worsened | B/C | Reject terminal-only correction |
| Cavity/Dyson/TAP | Exact DAG/no-self-reaction analysis | Needs a connected four-point vertex; generic state O(n4)/O(n5) | A/B | Hard kill generic form |
| Copula/two-Gaussian | Plausible marginal extension | Dependence is underidentified; propagation too costly | A/B | Hard kill without new structure |
| H3 rank-5 k4 | Algebra/tests; optimal raw k4 mean error 16.83%; nominal cost 40.936B | Optimal downstream correction cosine -1.000 and error 25.88x; CountSketch raw error 49.83% | B | Hard kill |
| Global analytic/sampler blend | Per-network oracle gain 22.15% | Universal coefficient worsened; coefficient sign varies wildly | C/O | Reject scalar blend |
| H2 weight-conditioned coefficient | Clear oracle motivation | Cross-seed ICC 0.129; all six sign-transfer tests fail | C | Block sign prediction |
| Parity/fractal MLMC | Exact unbiased constructions | Variance-cost ratios 1.17--2.98 and direct errors 12.6--500x worse | B/C | Hard kill current folds |
| Nonlinear shrinkage | 5.058% pooled apparent gain | Coefficient CV 54.8%; seed-LOO only 4.79%, below gate | C | Reject instability |
| Exact line conditioning | Exact first-layer integration | At least 496.96 forward equivalents; needs impossible >99.8% VR | A/B | Hard kill cost |
| Active subspace | Pointwise Jacobian rank about 15 | Subspace tumbles across gates; high-degree residual near-isotropic | B/C | Hard kill global subspace |
| Graphify local semantic pass | Local/no-key execution succeeded | Llama3.2 collapsed corpus to 5 nodes and mislabeled types | C | Reject as authority |
| Audited Graphify evidence graph | 54 nodes, 82 typed edges, 8 communities; useful traversal | Centrality depends on encoded edges and is not independent evidence | B | Use for prioritization |
| H1 equivariant residual | 70 finite symmetry-safe features; grouped residual R2 0.662672; scale-only R2 0.648801 | Misses the fixed R2>0.965 gate; graph features add only about 1.4 points over scale | B/C | Hard kill current information family |
| Finite-horizon factorized k3 | Algebra/depth parity 5.19e-15; all H safe; correction cosine 0.8997 | Best H2 adjusted 1.3162e-4, 583.1x worse; correction overshoots ~4.68x | A/B | Hard kill |
| Goal-oriented adjoint cumulants | Exact terminal k3/k4 projections, 3.111B cost, small-n correction cosines 0.951/0.762; restores mean absolute skew to 0.3867 | Public0..4 fullcov gain only 2.12%; full covariance adjoint goes rank1->rank8 and costs O(Ln4) | A/B | Hard kill promotion; preserve terminal operator |
| Weight-identified latent-factor q3,r2 | Original small-width ratio 0.04738, wins 6/7; honest/invariant/non-scalar; forward components and recompression are reusable | Adversarial n64 loses 8/8, ratios 2.928/1.596; top-two trace share falls 88.4% n4 -> 3.02% n256; absolute thresholds break scale homogeneity | B | Kill fixed-r leaf; preserve mixture machinery |
| Latent factor q3,r3 | Invariance passes; 33.075B conservative arithmetic; wins 7/7 vs fullcov on original seven | Ratio 0.0602767 misses <0.035 gate and is 27.22% worse than r2; wins only 2/7 vs parent | B | Kill r3 leaf; do not continue monotone r |
| Adaptive sparse-radial latent closure | Directly targets fixed-r trace collapse with O(r) signed nodes at fixed trace fraction | n64 accuracy, invariance, and target cost pending | pending | Live causal reimplementation |
| Sparse-radial measurement harness | Streaming truth cases stayed ~42.5MB and reproduced first three ratios | Last-bin reducer can append zero-weight components indefinitely; workers reached24.6/13.8GB | A/B | Kill harness only; candidate remains pending behind repaired isolated runner |
| Randomized radial full-sigma | 2x2: fixed8.8716, radial-only9.1062, Haar-only.668802, Haar+chi2.631599; 7/8 wins; all rotations<.8; 70.590B;37MB | Fresh n128 width law and production billing/cost tail unresolved | A/B | Promote combined operator to n128 synthetic audit |
| Randomized radial n128 scaling | Fresh ratio .634997,4/4 wins; rotations .5633/.2825/.9291/.7650;242MB;26.1s; all guards;70.590B | Actual FlopScope parity/billing/residual-wall tail unresolved | A/B | Promote to production port specification/dev audit |
| Randomized radial FlopScope port | Frozen Haar+chi2/q3/seeding; setup-hoisted buffers; exact charged shapes and NumPy parity | Build, parity, zero failures, max combined-cost margin, hot allocation/call tail pending | pending | Live production implementation |
| Full-covariance sigma latent closure | Entire covariance matched to 3.01e-15; exact scale/permutation; 48.381B conservative cost | n64 ratio 8.8716 and 1/8 wins; 2n axes alias ReLU gate/angular structure | B | Kill one-frame sigma leaf; preserve angular constraint |
| Gate-aligned truncated projection mixture | Seven structural tests; 68.640B bound; 8/8 nominal n64 wins; exact conditional moments and gauge/permutation covariance | Aggregate ratio 0.997502 versus <=0.8; generic recompression washes the effect to 0.2498% | B | Kill generic-compressor leaf; preserve stable direction |
| Gate-label path-memory recompression | Exact label moments; permutation/gauge errors <5.2e-16; 62.600B bound; 6/8 wins | Ratio 0.999602513; worse than generic parent 8/8 and erases 84% of its gain | B | Kill local-label memory; labels are not coherent across layers |
| Rao-Blackwellized gate marginals | Exact scalar-conditional first/second ReLU moments; six audits pass; 68.899B; 8/8 stable wins | Ratio 0.997502361 is only 6.08e-8 better than parent; scalar T explains about 1.0303e-4 of coordinate variance | B | Kill marginal-only link; preserve exact integrals and move to cross-neuron state |
| Repeated-index k3/k4 premise | 94/97 material signs; exact compact-state terminal contractions to 3.33e-15 | Aggregate k3/k4/combined fidelity -248.9998/-3578.1022/-2803.7649; only 3/9 energy passes; iijj recurrence O(n4) | A/B | Kill index-omission link; preserve orientation and exact terminal algebra |
| Conditional-correlation spectrum | Rank4 captures 99.3533% off-diagonal energy and 99.1170% material signs; mean/min cosine 0.9847/0.8216; 5/5 tests | Naive dense exact factor discovery costs 1.855T; residual remains tiny under current recursion | A/B | Promote compression premise only; mutate formation link |
| Conditional response-Gram factors | Degree4 rank<=4 proxy recovers 95.0349% covariance energy and 95.9161% signs; mean downstream cosine .9336; 6/6 tests; .5103B | End-to-end recursive survival and actual billed implementation unresolved; 4.97% source energy omitted | A/B | Promote affordable formation component only |
| q3 response-Gram recursion | 8/8 wins vs fullcov; symmetry/PSD; 71.494B; correction norm retained through q3 to 8.22e-16 | Ratio .997502340; source/cov median9.64e-13/max4.63e-7; essentially identical to H12 | B | Kill one-scalar source; preserve affordable response operator |
| Multi-direction gate response | Invariant F-bank, C-orthogonality, exact cancellation/overlap audit; no truth read | Factor-only 25741x was incomplete-source false positive; complete k1 has5/24 PSD fallbacks; k2+ >=108.573B; exact Gaussian partition is no-op | A/B | Kill Gaussian-parent bank; preserve F directions for non-Gaussian state |
| Radial susceptibility compressor | Exact moments/PSD/symmetry/spectrum;71.953B; layer0 wins8/8 | RMS ratio .975251,11/24 wins; mid/late covariance worsens; covariance99.35% error energy | B | Kill single F_phi geometry; preserve pullback |
| Radial dual-observable compressor | Exact moments/PSD/symmetry;71.964B;17/24 wins; repairs several deep groups | Ratio .965944 misses .8; gate/active cosine falls .72-.75 early -> .15-.25 late, so scalar fusion erases contrast | B | Kill scalar fusion; preserve both lanes and rank-two geometry |
| Conditional total-cumulance factors | Exact identity within 3.21e-12; rank4/full covariance fidelity .9961; 94/97 signs; 5 tests; 134MiB peak | Gaussian-within-cell k3/k4/combined fidelity .7560/.7966/.7872; residual cumulants omitted; recurrence unresolved | A/B | Kill Gaussian-cell link; preserve conditioning and covariance factors |
| Conditional residual-cumulant spectrum | Rank4 k3/k4/combined .993974/.984388/.986618; correction .995497; 97/97 signs; rank1 passes; 6 tests | Exact formation 8.063GiB/cell,129GiB/B16 plus O(p3); recurrence absent | A/B | Promote representation only; mutate factor discovery |
| Residual covariance-algebra factors | Fixed12D k3/k4/combined .983464/.969492/.972741;97/97 signs; doubled .995556 | Probe coefficients ill-conditioned/not uniform at n8; values and recurrence unavailable | A/B | Promote algebra only; stable probe formation remains |
| Physarum-attention MoE router | Complete experts, invariant query/flow,18/24 wins, compute below parent | Ratio .866761; all24 select fullcov; bank oracle best pure/top2 .833818/.829054 cannot reach .8 | B | Kill specialization link; preserve router/combiner until a complementary expert exists |
| Flatworm router attenuation | Dyadic leak/commissural algebra and symmetry pass; fatigue balances max load1.0 -> .333 | Leak/diffusion neutral; fatigue loss1.101064,cost4.684x,proxy1.52484x | B | Kill router link; preserve two-lane response topology |
| ECN-Jacobian-MaxEnt q3 | No-ladder ratio .911472 with32/32 wins; exact moments/PSD/Sinkhorn/symmetry/noncollapse;70.593B | Ladder .933606; psi is surrogate, phi hardcoded, and target dense route is89.925B plus38.65GB | B | Kill composite; preserve balanced transport and exact moment decoder only |
| Fourier/Gegenbauer distillation | Exact means, cross-fit, MUB, symmetry, and cost ledger all pass | Layer1 worsens design cost-adjusted variance to1.981x; degree{6,8} is174.995x adjusted,0/16,corr-.0367 | B | Kill dictionaries; preserve exact-mean harness only |
| JSpace response controls | Exact Hutchinson energy Gram and K4 geometry pass; bottom/complement are genuinely new subspaces | Top/bottom/complement all lose every fresh case with near-zero error correlation | B | Terminate estimator controls; preserve G0 offline only |
| Randomized-radial production port | FP32 parity,59.276B billed,71.423B effective,210.6MB,finite outputs | One permitted development row is96.1178x worse adjusted than champion | A/B | Kill direct estimator; preserve Haar/chi/q3 components |
| Constant-anchor inverse residual | Exact collapse and multiplier-aware severity/cost bounds | `a+mean(f-a)=mean(f)` pathwise; no nonconstant exact-mean control exists | A | Kill anchor residualization; require explicit coupled `g(X)` |
| Constant-modulus cumulant transport | Oracle-fed <=12D inverse keeps .926273 combined,.983525 correction,94/94 signs for12.340B if responses free | Exact diagonal nullspace, min k3/k4 ranks.3611/.2051, and no observable k3/k4 RHS | A/B | Preserve algebra; require amplitude-coded probes plus weights-only response recurrence |
| Whole-row rectangular Strassen | Full bill ratio.795427;65536-shape dispatcher and depth32 parity pass | Residual allocations make direct8.444B versus L19.144B and L212.205B effective | A/B | Preserve algebra; replace allocation/reconstruction schedule |

## Cross-branch hyperassociations

### 1. The hidden variable is not simply k4 magnitude; it is transported sign

The terminal oracle proves higher cumulants matter, but terminal analytic,
H2, H3, and nonlinear shrinkage all fail primarily through unstable correction
direction or coefficient sign. Therefore a useful model cannot merely estimate
"how non-Gaussian" a network is. It must preserve signed local source terms and
their transport through subsequent gates.

The adjoint result sharpens this: it restores the missing terminal skew and
preserves local correction signs, yet barely changes target-shape error. The
dominant missing quantity is downstream mean/covariance reclosure bias. Exact
dual transport of that quantity immediately produces dense, output-specific
covariance adjoints and the same four-point bottleneck.

### 2. Local low rank does not imply depth-stable low rank

The pointwise Jacobian is low rank and small-shape k4 tensors have concentrated
pair spectra, yet active subspaces tumble and the optimal rank-5 k4 correction
can reverse sign after transport. ReLU gates rotate the relevant directions.

Applied mutation: do not build a global low-rank state. H1 shares an update rule
but recomputes invariant local messages at every layer and uses multiscale depth
memory. H3 is not hybridized into H1 after its stability failure.

### 3. Oracle value plus proxy failure means an observability problem

True k3/k4 and per-network oracle blending show large possible gains. Weak
analytic/sketched/scalar proxies do not show that the target information is
irrelevant; they show it is not observable through those summaries.

H1's 70 symmetry-safe features obtained only OOF residual R2 0.662672 against
the required 0.965, while a shared scale already obtained 0.648801. This kills
the learned closure at the current information level. The adjoint branch then
showed why richer signed information is expensive: the complete covariance
dual is generically dense after one ReLU pullback.

### 4. Deterministic model error and random sampler error are different species

H2 tried to predict a scramble-specific sign from weights; that is structurally
misaligned. H1 predicts the deterministic residual of a deterministic analytic
closure, which is at least a function of the fixed weights.

Applied mutation: train H1 only on `truth - fullcov(weights)`. Do not contaminate
the target with a sampler seed. Any later sampler control must be tested across
independent scrambles.

### 5. Geometric regularity can worsen computational regularity

Kerdock is excellent in harmonic space but produces expensive structured gate
survival. The 39,936 fold parent also looks strong in mean cost yet fails in the
tail. Competition fitness depends on the distribution of activation-dependent
cost, not a linear per-point estimate.

Applied mutation: candidate gates use zero failures and Cmax headroom, not mean
FLOPs alone. Random 32,256 remains the deployment parent even when another
method has better small-screen raw MSE.

### 6. Fringe metaphors converge only after symmetry quotienting

Retinal prediction, morphogenesis, memristic memory, fractal depth, and
renormalization all independently point to multiscale local innovations plus a
shared global update. Without hidden-permutation, positive-gauge, and input-O(d)
invariance, that architecture becomes a public-network coordinate memorizer.

Applied mutation: H1 features and messages must live on the symmetry quotient;
grouped whole-MLP CV and explicit transformation tests are mandatory.

### 7. A finite mixture can preserve the missing nonlinearity without fitting a copula

The latent q3,r2 branch is genuinely different from the killed scalar mixture
and generic GMM/copula stories: its components are forward-defined by the
weights and survive a later ReLU. Its 95.26% small-width reduction was real.
The adversarial audit then found the missing width law: two factors explain
88.4% of trace at n4 but only 3.02% at n256, and the method loses all eight
fresh n64 cases. This kills fixed-r tensor quadrature, not the forward mixture.

Applied mutations: retain the weight-defined components, analytic rectification,
deterministic compression, and exact symmetry. Replace the failed factor rule
with either adaptive fixed-trace spherical-radial cubature or a full-covariance
2n sigma rule. Both change the causal failure while avoiding q^r child growth.

### 8. Stable marginal signs can coexist with asymptotically vanishing leverage

The gate-aligned split and its exact Rao--Blackwellized marginal child improve
all eight cases, but the latter changes the aggregate ratio by only 6.08e-8.
The measured reason is structural: one scalar gate statistic explains roughly
1.0303e-4 of each coordinate variance, so correcting each marginal remains an
O(1/n) perturbation even when the aggregate direction is correctly aligned.

Applied mutations: preserve the scalar-conditional integrals, but relocate the
state to cross-neuron dependence. Two independent premise tests now ask whether
the missing conditional covariance is rank-four compressible and whether
repeated-index k3/k4 matrices preserve next-layer contraction energy and sign.

## Immediate decision tree

1. Keep the validated random32,256 archive immutable; H1, H2, H3, finite-memory
   k3, and the standalone adjoint branch are now killed for promotion.
2. Preserve the adjoint terminal source operator as a proved 3.111B component,
   but do not fold it into the champion without an independent estimator whose
   residual covariance makes the combined adjusted score favorable.
3. Treat compression by the exact law `r_cost*r_MSE<1`; fewer paths and lower
   numeric precision alone do not create a score gain under this biller.
4. Exact sampler compression is now promoted through fixed8192-row streaming:
   the production child scores.940048x its parent with100/100 paired wins,
   zero failures, and max C222.405B. Freeze its source/package and do not tune
   from public0..99 again.
5. For analytic compression, use the certified64D/58D physical quotient and
   retain the Q2 Price trace operator, but do not claim either supplies the
   right-hand side. The isolated Q2 conditional response is only.28234
   combined; the next predeclared rung changes only Hermite order2->4.
6. The exact descendant has exhausted its authorized public0..99 promotion
   gate. Analytic descendants still require a fresh synthetic/static gate
   before any score. Do not combine failed implementations merely because they
   share vocabulary; every hybrid must expose a new observable and pass an
   interaction test.

## Compression recursion update

The exact-compute chain has now crossed its synthetic engineering boundary.
Fixed8192-row Winograd streaming repairs the integrated branch's sole liveness
failure: peak working set is474.301MiB, effective-compute ratio is.931714, and
prediction/depth parity remains far inside the frozen gates. This creates a
real promotion path, but only through an immutable production port and paired
permitted-development score. The 144-call fragmentation risk remains explicit.

The analytic chain exposed a complementary no-go. Canonicalizing the latent
factor removes the equivalent-rotation defect essentially exactly and repairs
49/201 convergence, yet isolated combined fidelity remains.66364. The grid
presentation was a removable numerical problem; the unchanged Gaussian-copula
state is an information problem. Future descendants must add a signed
higher-order observable or change the prior, not spend more nodes on the grid.

The clean-room PLE sidecar is a storage/locality survivor rather than a third
estimator. Exact layer symmetry compresses the shared Phi/phi atlas31.9x to a
66,632-byte package. Its useful hyperconnection is with the Price--Hermite
operator: a1 through a4 are reconstructed from the same two primitives. Its
limiting connection is the score calculus:41 proxy operations beat the known
float64-promoted path but not an ideal28-operation native-f32 path. Therefore
flash packaging should be fused only into an already-required moment pass.
