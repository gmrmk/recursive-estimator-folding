# Failure curve and what it says about the inference problem

Status: living response-free synthesis.  This document does not promote an
estimator, authorize an outcome read, change the immutable champion, or claim
a leaderboard result.

## The curve

The **score law** has an L-shaped tradeoff; the heterogeneous experiments do
not themselves define a fitted geometric curve. Their defensible empirical
shape is a sawtooth dependency frontier rather than a random graveyard:

The current recursion ledger contains 176 named mechanisms. Its labels mix
killed leaves, screened components, audits, and two historical promotions,
but the overwhelming mass is falsification rather than promotion. The shape
below is therefore supported by repeated mechanism-level evidence, not by a
handful of anecdotes.

```text
raw error
  ^
  | analytic bias wall  * * *
  |                     *
  |                     *     exact higher-order transport
  |                     *     hits tensor/rank/call wall
  |        sampling  *--*-------------------------------> cost
  |        floor
  +------------------------------------------------------------>
```

There are four successive regimes.

1. **Geometry-dominated sampling.**  Antipodes, frames, spherical designs,
   rotations, and exact radialization removed low-degree and radial variance.
   This yielded the large early gains.  The formal local champion is raw
   `3.089460087e-7`, adjusted `2.121762464e-7`, already near the estimated
   design-sampling floor.
2. **Information-dominated sampling.**  Balanced draws, orthogonal arrays,
   static singularity-aware proposals, Jacobian subspaces, and local routers
   rearranged nearly the same observations.  Their gains became unstable or
   adverse with width.  The missing variable was not another index law.
3. **Bias-dominated analytic closure.**  Gaussian/covariance and finite-moment
   closures are cheap but miss fixed-instance connected higher-order
   dependence.  Even granting exact terminal `(mu,sigma)` leaves a measured
   `8.76e-7` cap, while granting exact `(mu,sigma,k3,k4)` gives a `4.7e-8`
   oracle.  That gap identifies the information class, not an optimizer bug.
4. **Exactness-dominated transport.**  Local noncentral `[2,1,1]` mathematics
   can be exact, but generic global realization hits one of three cliffs:
   endpoint certification, masked Khatri--Rao aggregation, or dense all-output
   response transport.  Adaptive variants then encounter a fourth cliff:
   residual wall time and call-count tails.

The score law explains the flattening.  Abstractly,

```text
MSE = bias^2 + variance / samples,
effective cost = billed arithmetic + lambda * residual wall.
```

After the design removes the easy bias/variance modes, increasing samples
mostly trades `1/N` variance against `N` cost, so adjusted score barely moves.
Cheap analytic methods lower cost but retain a dominant structural bias.
Exact high-order methods remove that bias but expand the state or call graph.
The useful mutation must cross both arms of the L at once.

## What the failures identify about the target

The unknown is not the whole network mean.  It is a small residual with a very
specific phenotype:

- even spherical degree at least six after the design;
- created mainly in the last third of depth;
- output- and weight-instance-specific with changing sign;
- locally visible in noncentral three-label ReLU boundary geometry;
- globally full-rank after gate subspaces tumble through depth;
- heavy enough in its influence tails that average proposal fidelity is not a
  sufficient statistic.

This reconciles results that otherwise look contradictory.  A local Gaussian
block can have rank two and admit a 14x Rao--Blackwell gain, while the global
width-256 response still needs rank at least 234.  A proposal can resemble the
coefficient yet worsen output variance, because the relevant inner product is
with the downstream influence, not with source amplitude.  A mathematically
cheaper kernel can score worse because each extra allocation/call becomes
`lambda * wall`.

## The inference architecture implied by the curve

The surviving architecture is an exact control decomposition:

```text
exact target source Delta
       = cheap deterministic control c
       + exactly sampled residual (Delta-c)
                         |
                         v
              one coalesced forward carrier
```

For any frozen deterministic control and a full-support proposal,

```text
C = sum c_e F_e,
Rhat = mean ((Delta_e-c_e) F_e / q_e),
E[C + Rhat] = sum Delta_e F_e.
```

Therefore a bad control does not create bias; it fails only through residual
variance or cost.  This converts approximation quality into a falsifiable
variance question and is why M148's conservation law is more valuable than
any literal copula fit.

M155 and M156 sharpen the compiler side.  Masking collision labels inside the
deterministic covariance-star control creates a generic symmetric Khatri--Rao
action costing `266.806B` across 31 layers.  Extending the control to all
ordered triples and assigning target coefficient zero on collisions removes
that mask exactly.  The deterministic source then compiles in five ordinary
GEMMs per layer; the collision residual cancels the artificial control in
expectation.  M156 passed seven algebra tests and five fresh native traces:
155 GEMMs, `10.426269184B` bill, and a worst 5x-new-wall combined projection
of `99.598997666B` inside its 100B branch envelope.

M161 then provides the decisive negative result.  Exact source conservation
still holds to `1.43e-14`, but artificial collision rows consume
`99.9978%--99.99999%` of residual source second moment.  Pooled residual/raw
variance is `3.201e8`, its upper-90 is `7.397e8`, and collision p99/raw p99 is
`3.753e12`.  The domain-lift/compiler mechanism survives; the complete-domain
covariance-star **control** is killed.  A control's support cannot greatly
exceed the target's support unless the extra part is deterministic or
algebraically null.  Exact cancellation in expectation is not enough under
Hansen--Hurwitz tails.

M163 is the first support-aware repair.  The correlation exterior Gram factor
`G_ij=1-R_ij^2` has `G_ii=0`; with `A=V o G` and
`cE_ijk=-2 A_ij A_ik`, the control vanishes exactly on the three collision
patterns that jointly own `99.5336%--99.9970%` of M161's collision energy
(`iii`, `iik`, and `iji`).  No explicit mask or Khatri action returns. Five
tests pass and the static compiler is `13.0769472B` inside the `14.0191212B`
slot. M164 then closes this deployment before efficacy: five fresh workers
are finite, invariant, and bill only `10.444656904B`, but their residual wall
is `9.456--10.639 ms` versus `7.149 ms` permitted. Every hostile projection
lands at `101.153--101.745B`. The exterior collision-null identity survives;
this 155-dispatch realization does not.

M166 removes the remaining `ijj` face as well. It orients covariance edges
into disjoint permutation-covariant supports `A,B` and uses
`c_ijk=-(A_ij B_ik+B_ij A_ik)`, which is zero on all four collision patterns.
The exact algebra and seven-product compiler pass, but float64 costs
`18.492784640B`, missing the slot by `4.473663440B`. A `9.246B` float32
worksheet has `9.24e-7` reconstruction error and no exactness or variance
credit. Thus collision support is algebraically solvable; exact cheap emission
remains unsolved.

M167 resolves whether owner bookkeeping can make that support free. Collision
triples do map exactly into the physical fourth-cumulant classes:
`iii -> K4/6`, `iik/iji -> K31/3`, and the two `ijj` representatives to
`K22/2`; the former separate owners must be retired. But M163's `ijj` control
is not the physical `K22/2` coefficient (generated mismatches `.240--.751`).
Owner unification removes artificial zero-target semantics and double count;
it does not remove the `[2,2]` residual or its Khatri-class transport.

M157 attacks a separate wall: instead of evaluating a redundant 32-layer
dense proposal pilot, let the already-required Formal pilot define the
pilot-only proposal.  Its structural trace removes 32 products and
`7.439248181B`, while replay and frame restoration remain exact.  Because the
proposal statistic changes, this is a new estimator branch rather than
memoization.  M160's resource gate finds all five workers finite, replayable,
ordered, and exactly restoring below `387.152 MiB` RSS, but two hostile
projections exceed `258.4B`, reaching `278.273B`.  The deployable configuration
is killed before efficacy; reuse of an already-required pilot remains a valid
component.

M158 exposes a numerical-contract error rather than an integration theorem:
at large admissible scale, float64 output spacing itself exceeds a universal
`2e-8` absolute coefficient tolerance.  The correct descendant factors
positive homogeneity and certifies a dimensionless value with an ulp-aware
absolute-plus-relative reconstruction bound.  More quadrature cannot repair
an impossible output ABI.

M162 supplies the smallest exact analytic inventory: Tallis reduces the
twelve required raw moments to one trivariate orthant probability, three
bivariate facets, three univariate edges, and one vertex density.  A fixed
87-node Plackett line is nevertheless not a provider: centered errors are
`4.12e-8` at correlation `.999` and `3.93e-8` at `.999999`, while the exact
correlation derivative reaches `1.068e7` at the nearest rank face.  A viable
endpoint must cancel the rank singularity symbolically before numerical
integration, then use a rank-aware interval certificate. M165 proves that
cancellation exists on a rank-one opening if the *connected defect* is
assembled first: after subtracting its rank-one value and cone tangent,
`Delta(epsilon)=Delta0+3.983346315428913 epsilon-1.4681 epsilon^(3/2)+O(epsilon^2)`,
and `u=epsilon*v^2` regularizes the endpoint. This is a rank-one component,
not a generic provider: rank-two anchors, zero faces, interval constants, and
the `606,720`-operation certificate remain open.

M168 closes the mathematical rank-two anchor gap on the regular stratum. A
canonical 2D support-plane wedge gives the connected defect and a finite
one-sided Price/coarea tangent when all marginals are positive and every kink
pair crosses transversely. The corrected formula needs 20 indicator-weighted
planar terms plus 16 kink-line terms; omitting ReLU indicators was falsified.
Rank-preserving finite differences agree below `2.8e-13` and a rank-three
opening agrees to `1.33e-6`. The source-only worksheet fits only at a
hypothetical 10-node rule (`571,904` operations; 11 nodes give `627,456`), and
there is no uniform error or native-bill certificate. Thus the rank-two
mathematics survives while the generic provider remains closed.

M169 proves that M164's dispatch wall was contingent rather than structural.
Batching all 31 first products and all 124 post-products along legal NumPy
batch axes preserves bitwise output while reducing 155 dense dispatches to
two. Five fresh target-shaped runs bill `10.477162760B`, have residual p99
`5.322 ms`, and project to `98.213--99.140B`; the resource gate passes.
M174 then exposes the next bend in the curve: the generated compiler assumes
31 already-owned labelled full covariance states, but the production base
propagates only diagonal variance and no actual caller supplies the exact
`M163 slot -> M125b TangentState` conversion. Thus scheduling is solved only
conditionally; state provenance and lifetime are now the binding interface.

M170 separates a structural failure from an implementation failure. In the
audited dense-product normal form the oriented all-collision-null control has
independent ranks `2+3+2=7`; exact integer minors certify the lower bound, and
even six float64 families cost `15.572336640B` before overhead. More dense
polarization is therefore not a mutation target. The surviving opposite-
triangle structure requires a different arithmetic class, not another search
over dense decompositions.

M171 and M173 give the complementary lesson. M171's fixed physical-coordinate
GL10 certificate fails by over `104,436x` on a lawful near-parallel rank-two
family because derivatives scale as `eta^-20`. M173 changes to the boundary-
layer coordinate `u=u*+eta t`, removes that false singularity analytically,
and certifies the hostile channel at `9.1466e-9` value error and `9.4299e-8`
tangent error within `561,152` static operations. This is a genuine repair of
one chart, not an all-PSD provider: symbolic envelopes, SPD states,
nontransverse collisions, zero marginals, and native metering remain open.

M172 likewise separates algebra from deployment. Selective physical `[2,2]`
owner fusion passes all eight static checks and conservation through widths
2--7, but development remains sealed because M174 invalidates the assumed
caller ABI. A correct source identity is not yet an executable estimator.

## The derivative of the failure curve

The useful information is not merely where candidates fail, but how the
failure location moves as each upstream obstruction is removed:

| removed obstruction | next exposed obstruction | inference |
|---|---|---|
| radial/low-degree variation | high-degree sampling floor | the easy mass is geometric |
| extra samples/proposals | fixed-instance analytic bias | more observations do not reveal the missing statistic |
| Gaussian closure bias | connected `k3/k4` state size | the missing statistic is higher-order dependence |
| collision support errors | dense tensor/product rank | exactness must be compiled structurally |
| 155-call runtime wall | missing labelled `V/J/source` ABI | compute is feasible only if the right state already exists |
| missing background ABI | endpoint-complete bivariate value/Jacobian | interfaces expose their hidden mathematical dependencies |
| fixed-node endpoint panel | scaled boundary layer | some numerical divergences are coordinate artifacts |

This migration narrows the latent variable on the attempted branch. It says
the target residual may be locally simple but is globally hard to carry. This
is a working causal map, not proof that every legal winning estimator must
follow the same route: the gates use non-comparable evidence and descendants
were deliberately selected to repair predecessor failures. The next estimator
on this branch should therefore minimize *state creation and transport*, not
local approximation error.

M175 tests M174's fixed `B=8` repair and stops one dependency earlier than a
resource trace. The schedule is coherent only conditionally: current code has
no exact labelled metered producer for `(W_l,mu_l,V_l,J_l)`, and array-shape
compatibility does not define the missing `Source211 -> TangentState`
semantics. Consequently the first live mutation is no longer block staging;
it is to construct or falsify the exact zero-order background producer while
leaving source conversion frozen as an independent mechanism.

M176 pins that producer's exact recurrence and reveals that the dependency
frontier is cyclic rather than monotone. The recurrence needs a noncentral
bivariate ReLU value **and Jacobian** on every PSD endpoint stratum. Existing
FlopScope code uses a GL10 approximation, variance floors, and correlation
clipping; the exact-formula prototype is adaptive ordinary NumPy without a
metered uniform certificate. Thus the chain loops back:

```text
endpoint calculus -> exact background (mu,V,J) -> bounded staging
                 -> source carrier -> endpoint/source control
```

Storage did not cause this failure. It merely forced the hidden mathematical
precondition to become explicit.

M177 then isolates that primitive and closes the current installed-runtime
route. The PSD-stratum algebra is coherent and tested, but FlopScope supplies
billed univariate `Phi/phi` without a certified `Phi2`/Owen-`T` primitive or
remainder contract. The known floor is `556` FLOPs per unordered positive pair
before the unaccounted bivariate-CDF work. Rank-one limits admit only feasible
one-sided tangents, and a generic zero-variance JVP is path-underdetermined.
The mathematics survives; the lawful metered numerical provider does not yet
exist.

## God nodes, ordered by leverage

1. **Residual alignment and support.**  A deterministic control must reduce the complete
   source-to-output influence variance, with upper-90 ratio `< .25`, p99 ratio
   `<= 1.25`, and no adverse width trend. It must vanish on zero-target strata
   or pay for their exact deterministic subtraction. Coefficientwise
   resemblance and expectation-level cancellation are not enough.
2. **Labelled zero-order state producer.**  Define and meter the exact
   recurrence producing `mu_l`, full `V_l`, and frozen `J_l`; do not reuse the
   diagonal production base or clipped/floored exploratory fullcov code merely
   because its arrays have compatible shapes.
3. **Bounded-lifetime staging and source ABI.**  Once that producer exists,
   carry its states in fixed blocks and separately prove the M163-source to
   M125b tangent conversion without feeding the source carrier back into the
   background. M175 confirms that a schedule alone supplies neither semantic
   link.
4. **Scale-normalized stratified endpoint primitive.**  The distinct-label exact
   coefficient must cover every PSD stratum without a numerically impossible
   absolute contract. M173 covers only one transverse boundary layer.
5. **Collision-null compiler.**  Preserve M156's full-domain dense source
   identity, but require algebraic zero support on repeated labels as in M163;
   never reintroduce the masked Khatri product.
6. **Dispatch fusion.** M169 has solved the isolated 155-to-2 call transform;
   the remaining requirement is to retain its gain inside a lawful caller and
   bounded-lifetime staging scheme.
7. **Single forward carrier.**  Coalesce all source injections into the
   existing inhomogeneous tangent.  Generic all-output adjoints are full-rank
   and cost about `1.029T` in the audited construction.
8. **Call-tail envelope.**  Require fresh-process residual and memory tails,
   not only a FLOP worksheet.  The over-budget cliff dominates marginal
   accuracy.

## Decisions implied by the curve

- Do not spend the remaining window on more points, rotations, static proposal
  tuning, fixed-rank global factors, or richer terminal four-moment selectors.
- Keep failures as typed components: local factor conditioning, balanced
  sampling, positive envelopes, endpoint partitions, and pilot memoization can
  reappear only when a new causal edge supplies conditioning information or
  removes work.
- Close the M156 complete-domain covariance-star control. Preserve its domain
  lift and five-product compiler; the next control must be algebraically null
  on the binding collision patterns without reinstating M155's explicit mask.
- Close the M163 deployment after M164's `5/5` hostile resource failure. Keep
  the exterior null as a typed algebraic component; do not open its sealed
  efficacy cells until a lower-dispatch descendant passes a fresh native gate.
- Preserve M166's all-collision-null orientation, but close its exact float64
  compiler and withhold credit from the uncertified float32 descendant.
- Adopt M167's collision-owner mapping in any complete-domain descendant, but
  do not relabel a control coefficient as physical `K22/2`; ownership repair
  carries no compiler or variance credit.
- Close M157 as a deployable configuration after M160. Preserve its pilot
  reuse/order mechanism for a future branch with a separately reduced call
  graph; do not open an efficacy protocol.
- Treat scale normalization as mandatory for every endpoint certificate.
- Preserve M162's Tallis inventory and M165's rank-one subtraction, but close
  fixed common-node Plackett rules. A provider still needs separate rank-two
  handling, zero-face dispatch, interval constants, and native cost. M168 now
  supplies the transverse positive-marginal rank-two anchor/tangent only;
  refuse nontransverse and zero-marginal faces until separately certified.
- Preserve M169 as a bitwise resource survivor, but do not open efficacy from
  its synthetic all-layer stacks. M174 proves its caller precondition is not
  presently lawful.
- Preserve M172's selective `[2,2]` ownership algebra. Development and
  confirmation remain sealed until the actual staging/carrier ABI passes.
- Admit M173 only as a hostile transverse boundary-layer certificate. It
  repairs M171's coordinate failure, not the missing all-PSD provider.
- Mutate M174 with exactly one fixed response-free interface change: a
  labelled `B=8` zero-order archive/carrier pipeline. M175 has now refused
  this composition because both the exact background producer and slot
  conversion are absent; preserve the schedule only conditionally.
- Split M175's compound precondition. Build or falsify the exact labelled,
  metered zero-order background producer first. Do not simultaneously invent
  source-slot semantics or open variance/outcome cells.
- M176 has falsified that producer using current primitives. The next single
  mutation is the endpoint-complete, scale-normalized bivariate ReLU
  value-and-Jacobian primitive; archive and source-carrier work remain sealed.
- M177 preserves the endpoint dispatcher but falsifies its current runtime:
  require a certified fixed/bounded-cost `Phi2`/Owen-`T` value-and-derivative
  evaluator before reopening M176. Never assign zero cost to the absent
  primitive or substitute clipping/flooring under the same name.

The central inference is concise: **we no longer need a better approximation
of the dominant network behavior. We need a cheap exact control for the tiny
late-layer connected residual, a stratified boundary calculus for its singular
faces, and a bounded-lifetime labelled state carrier. It must be judged in the
downstream influence metric under the real call-time budget.**
