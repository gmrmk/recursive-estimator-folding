# Pass/fail hyperassociation ledger

Date: 2026-08-06. This review separates component validity from end-to-end
contest fitness. A branch is promoted only if its entire causal chain passes:

`representation -> observable -> estimator -> cost -> held-out score -> package`.

Passing an earlier link does not rescue a later failure.

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
| Audited Graphify evidence graph | 49 nodes, 65 typed edges, 10 communities; useful traversal | Centrality depends on encoded edges and is not independent evidence | B | Use for prioritization |
| H1 equivariant residual | 70 finite symmetry-safe features; grouped residual R2 0.662672; scale-only R2 0.648801 | Misses the fixed R2>0.965 gate; graph features add only about 1.4 points over scale | B/C | Hard kill current information family |
| Finite-horizon factorized k3 | Algebra/depth parity 5.19e-15; all H safe; correction cosine 0.8997 | Best H2 adjusted 1.3162e-4, 583.1x worse; correction overshoots ~4.68x | A/B | Hard kill |
| Goal-oriented adjoint cumulants | Exact terminal k3/k4 projections, 3.111B cost, small-n correction cosines 0.951/0.762; restores mean absolute skew to 0.3867 | Public0..4 fullcov gain only 2.12%; full covariance adjoint goes rank1->rank8 and costs O(Ln4) | A/B | Hard kill promotion; preserve terminal operator |
| Weight-identified latent-factor closure q3,r2 | Synthetic summed-MSE ratio 0.04738 vs fullcov, wins 6/7; exact permutation/gauge; affine-rank2 means; bounded 27-to-3 recompression | Only seven small networks; 26.2B cost is unbilled arithmetic; legal eigensolver and width-256 behavior unknown | B | Survives premise; advance one rung only |

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

The latent q3,r2 branch is different from the killed scalar mixture and generic
GMM/copula stories. Its components are forward-defined by weight-conditioned
covariance eigenfactors, not inferred from insufficient low moments, and they
remain distinct through the next ReLU before deterministic recompression. The
synthetic 95.26% reduction is therefore a real premise pass, while still not
proving that the approximation survives width 256 or legal FlopScope billing.

Applied mutation: advance only q3,r2 to a counted target-shape smoke. Preserve
the exact invariance fallback at repeated eigenspaces, store child residuals
diagonally, and kill before any score screen if eigensolver accounting or Cmax
headroom fails.

## Immediate decision tree

1. Keep the validated random32,256 archive immutable; H1, H2, H3, finite-memory
   k3, and the standalone adjoint branch are now killed for promotion.
2. Preserve the adjoint terminal source operator as a proved 3.111B component,
   but do not fold it into the champion without an independent estimator whose
   residual covariance makes the combined adjusted score favorable.
3. Advance only latent q3,r2 to a legal FlopScope target-shape cost/stability
   smoke, followed by one predeclared public0 no-scorer accuracy check only if
   the resource gate passes.
4. Independently audit the synthetic reference and closure implementation;
   a 0.04738 ratio is strong enough that baseline or orientation bugs must be
   excluded before trust increases.
5. Do not combine dead branches merely because they share vocabulary; every
   hybrid must supply a new observable and pass an interaction test.
