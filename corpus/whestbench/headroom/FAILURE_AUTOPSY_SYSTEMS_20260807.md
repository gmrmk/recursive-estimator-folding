# WHestBench recursion failure autopsy: systems and experiment layer

Date: 2026-08-07  
Scope: ledger candidates M104--M176, target-free/static/native/resource evidence
only. This document intentionally does not read a scorer, truth, leaderboard,
submission, or champion artifact. `Killed` below means the stated implementation
at its stated gate failed; it is not a verdict on a broader mathematical family.

## Executive finding

The apparent failure curve has three superposed curves, not one:

1. **Estimator signal failure.** Exact-zero features and learned associations
   repeatedly had no stable held-out relationship to the final error.
2. **Representation/conditioning failure.** Several local identities survive,
   but either a full-state contribution, near-rank-deficient endpoint, or
   collision stratum was omitted or ill-conditioned.
3. **Deployment-interface failure.** A few components pass algebra and even a
   component resource trace, but cannot be reached by an actual, labelled,
   FlopScope-metered caller without changing semantics.

Treating all three as "the method did not work" would be a category error.
Conversely, treating a local pass as an estimator win would be equally wrong.

The ledger contains 73 M104--M176-labelled records. They are deliberately more
fine-grained than independent estimator trials: many are audits, repairs, or
component proofs. The table groups them by their *first causal break*.

## Representative causal autopsies

| Family / records | Mechanism tested | First broken link | Evidence class and decisive observation | What remains valid | Resurrection condition |
|---|---|---|---|---|---|
| Protocol durability: M104--M105 | Seeded, clipped nested-Hermite association experiment with a raw control | The experiment contract, before target exposure | Independent pre-execution audits found unseeded model construction, declared-but-unused gradient clipping, then a raw arm with 2,880 dead first-layer parameters (2,441 live vs. 5,321 treatment). | Self-contained runner structure, tolerance-based symmetry tests, durable reference/checkpoint idea, gamma decomposition. | A fresh protocol must have identical active capacity, logged seed/order/optimizer semantics, per-event persistence, and a target-free causal-ablation test. No parameter retune repairs a confounded null. |
| Learned association: M106 | Active shuffled-association null for Hermite carrier | Stable causal signal | Frozen generated run: validation treatment/null mean-MSE ratio 0.9489 with bootstrap [0.7718, 1.1956]; treatment wins 46.1%. The depth-6 interaction is suggestive but absolute quality fails. | Gauge/symmetry controls, active-null discipline, depth-sensitive routing clue. | Change bias class/observable: an exact control or identity must use the association, then beat a matched active null on independent whole networks. |
| First-layer exact-zero controls: M107, M110--M112, M115 | Gegenbauer, nodal occupancy, sign-pair, connected-kernel, and projective controls | Proxy-to-downstream association | M107 held charged geometric ratio 1.243; M110 1.074; M111 1.069; M112 1.158. M115 raw ratios 1.46--1.86 and charged pooled 4.676. All had substantial prechecks and cross-fit/provenance gates. | Exact mean identities, corrected spherical occupancy constant, gauge repairs, first-pre reuse, pair-field and kernel constructions. | Demonstrate a new downstream-gate-aware label/identity *before* fitting. Training-only reversals identify association overfit, not a coefficient-tuning opportunity. |
| Harmonic/"physics" feature explosion: M108--M109 | Heat/cymatic Gegenbauer band and gate-tube occupancy | High-dimensional amplitude/mean specification | Unit-variance band fourth moment about 2.047e23; centered energy inherits it. M109 also used the wrong spherical density exponent, creating fixed conditional mean -3.888e-4, and a gauge-dependent path mixture. | Stable recurrence; bounded-tube intuition; normalized-axis requirement. | Any harmonic atom needs a certified amplitude/tail bound and exact conditional mean under every gauge before a network run. |
| Sketched/full cumulant state: M113, M117--M120, M123--M124 | Sketch or low-rank connected Hermite/k4 state; normal-ordered Price carrier | Missing full-state/collision contribution, not a runner bug | M113 drift 3.7176 vs. 0.05 (74.35x). M120 omitted connected Price residual E: global error .0840 vs .05; every cell failed despite benign directional probes. M124 missed a nonzero three-label [2,1,1]/aabc collision. | Graph-orbit enumeration, self-swap symmetrization, exact local Price/Jacobian algebra, source Gram/projector components. | A fresh carrier must include the omitted stratum/state or furnish a theorem that bounds it in the *full norm*, not random-direction tests. |
| Collision cost wall: M117--M118, M123, M140, M150--M151, M155, M170 | Exact repeated-label or masked Khatri/adjoint contractions | Dense/structured action cost | aabc collision support alone drove M117 to 390.066B. M118's best separated version was already 283.763B before omitted work. M155: one f64 G@K is 8.607B/layer, 266.806B over 31 layers. M170 proves 2+3+2 = 7 product families in its dense normal form; six alone cost 15.572B. | Equality ownership, quadratic jets, source/dual associativity, Khatri obstruction, oriented-triangle edge. | Change the arithmetic class: an exact unmasked domain lift, a proven structured triangular kernel compiler, or a different representation. Lowering ranks/terms within the same masked dense action is ruled out. |
| Exact compiler that passed the wrong gate: M156 -> M161 | Complete-domain star control plus five-product compiler | Source variance, after compiler legality/resource pass | M156 has 155 GEMMs, 10.426B bill, and passes its component resource projection. M161 then finds collision rows carry 99.9978--99.99999% of residual second moment; pooled residual/raw is 3.201e8 and collision p99/raw 3.753e12. | Complete-domain conservation, five-product compiler, domain-lift idea. | Replace the collision-support/control mechanism and run source-variance gates before any efficacy claim. A low bill cannot redeem a tail-bomb control. |
| Call/allocation residual wall: M116b--c, M153, M157, M160, M163--M164 | Exact L3 arithmetic, prefix reuse, self-hosted pilot, exterior collision-null compiler | Dispatch/allocation residual, not billed arithmetic | L3: 1,024 calls -> .6105 s and 512 -> .3285 s, both above .170 s gate, while arithmetic/parity pass. M164: fixed 10.445B bill and 155 GEMMs, but 9.456--10.639 ms vs. 7.149 ms allowed; all five projections 101.153--101.745B. M153 and M157 retain useful reuse but fail hostile budget tails (2/5 in M157/M160; max 278.273B vs. 258.4B safety). | Exact transforms, parity certificates, guarded prefix cache, self-hosted ordering theorem, exterior null identity. | Cut call count/allocation lifetime at the actual caller and remeasure fresh hostile tails. Arithmetic savings do not imply score savings when wall seconds are billed at 1e11 FLOP/s. |
| Endpoint, ABI, and conditioning: M147, M149, M158--M159, M162, M171, M173 | Bivariate/trivariate noncentral ReLU provider with rank-aware endpoint treatment | A fixed global coordinate/rule is not uniform over legal PSD states | M149 defects 6.48e-6 / 1.54e-3. Literal M158 2e-8 physical ABI is impossible: nearest-float error 2.7586e-5. M162's fixed 87-node error is 4.12e-8 near rho=.999 with derivative 1.068e7. M171's GL10 error floor .00208873 is >104,436x tolerance. M173 fixes only the hostile transverse rank-2 layer: value 9.15e-9, tangent 9.43e-8, static 561,152 ops. | M147 pair algebra; M159 dyadic scaling; M154 rank-one partition; M165/M168 connected-first anchors; M173 boundary-layer split. | A rank-stratified, parameter-scaled provider with symbolic envelope bounds and all faces (SPD, transverse/nontransverse, zero marginal, outward cone), then native metered certification. Do not reuse a fixed-node global rule. |
| Sampling/proposal dynamics: M131, M133--M139, M141, M143, M145--M146, M148 | Hidden-edge/triple samplers, factor conditioning, ACG/pilot adaptation, controls | Variance/cost or endpoint-provider dependency | M133 achieves .8151x source MSE only above 102.255B; M134 partial sums reach 7,667.42; M135 real 14x Rao--Blackwell gain is non-generic (generic rank >=234 and density-ratio L2 fails below it). M138 variance trend nonmonotone; M139 upper90 1.115. M145 has 2/5 hostile resource failures; M146 structural residual up to .262s. | Exact HH/frozen-q/tangent laws, conductance proposals, local factor law, full-support rescue, pilot ordering. | Show a generic integrability/variance certificate and inclusive native resource trace; proposals may not depend on an unresolved endpoint provider or an unpriced adaptive side path. |
| Moment-only terminal closure: M137 | Map exact first four terminal moments to E[ReLU] | Identifiability | Normal and symmetric three-atom distributions share first four moments but ReLU means .398942 and .288675. Frozen numerical result also needed reproducibility repair. | Moment feasibility witness and interval gate. | Add sufficient distributional information or an explicit error theorem; no four-moment resummation can certify number-one accuracy. |
| Ownership and collision relabelling: M166--M172 | Oriented exterior controls and physical [4]/[3,1]/[2,2] ownership | Cost or semantic ownership, depending on branch | M166 collision null is exact but needs 7 f64 product families (18.493B); f32 reconstruction error 9.24e-7 receives no credit. M167 exact owner maps pass but M163 ijj differs from physical K22/2 by .240--.751. M172 static ownership passes 8/8, but its variance gate is sealed by M174. | Oriented null identity, true iii/iik/iji/ijj ownership maps, retirement/double-count checks, M172 static algebra. | An exact affordable compiler plus an explicit source-owner conversion; never relabel a control as physical cumulant ownership solely because its tensor shape matches. |
| Two-axis call fusion: M169 -> M174--M176 | Batch 31 Z products and 124 post-Z products through two legal batched matmuls | No actual producer-to-caller ABI | M169 bitwise parity, 155 -> 2 matmuls, 10.477B, p99 5.322 ms, hostile totals 98.213--99.140B. M174 finds no labelled full V_l/J/source producer; M175 B=8 only has conditional 85.522 MiB workspace; M176 localizes the first missing primitive to exact, endpoint-complete, metered bivariate ReLU values and derivatives. | Batch compiler, B=8 liveness schedule, zero-order versus signed-carrier separation, M125b carrier linearity. | Build one thing only: a labelled FlopScope exact/fail-closed bivariate ReLU value-and-Jacobian producer with a target-shaped integrated trace. After it passes, independently implement Source211 -> TangentState ownership conversion. |

## Recurring system laws extracted from the failures

1. **First-break law.** Preserve the earliest failed dependency, not the most
   visible downstream symptom. M174--M176 show that changing stack size,
   liveness, or casts cannot repair a missing endpoint-complete primitive;
   M161 shows that passing a compiler cannot repair a variance explosion.

2. **Inclusive-cost law.** The score sees billed FLOPs *plus* residual wall
   time. A 1 ms residual change is 0.1B FLOP-equivalent. The M116 two-point
   experiment and M164 155-call trace make call count/allocation a primary
   design variable, not an implementation afterthought.

3. **State-completeness law.** A few favorable directions, a low Frobenius
   rank, or a local identity are insufficient under repeated nonnormal
   transport. M120's omitted E and M124's aabc omission survived easier tests
   yet materially changed the full state. Full-norm residual ownership must be
   audited before compression claims.

4. **Proxy-distance law.** Exact zero mean, invariance, and a training gain
   only establish that a feature is legal and fitted. M107/M110/M111/M112/M115
   demonstrate that the missing object was stable downstream-gate phase. A
   proxy needs a predeclared causal route to the final residual and an active
   null, not another regression fit.

5. **Boundary-layer law.** A numerical primitive must be organized by rank
   face and singular scale. Fixed quadrature can look good in ordinary states
   yet be wrong by orders of magnitude near legal PSD boundaries. M159 plus
   M154/M165/M168/M173 is the useful constructive thread: scale first,
   subtract connected anchors, then certify the remaining layer.

## What the curve says about inference

The productive inference is not "more exotic features" or "more aggressive
compression." It is a constrained causal graph:

```text
exact source identity
  -> complete ownership / variance control
  -> endpoint-complete background + Jacobian primitive
  -> labelled source-to-carrier ABI
  -> inclusive call/liveness trace
  -> held-out estimator efficacy
```

Every arrow has independently failed at least once. The immediate high-value
work is the earliest unresolved arrow, the exact metered bivariate
value-and-Jacobian primitive. It is a prerequisite, not evidence that the
eventual source correction will improve score. Once that exists, M169's
call-fusion and M172's ownership static pass become testable components rather
than speculative gains.

## Adversarial warning: do not overread the curve

This is a selected search ledger, not a random sample of all legal
estimators. It is enriched for sophisticated branches with strict kill gates;
the apparent concentration of failures can therefore exaggerate the
impossibility of a new representation. Several rows share inherited code,
cost models, or generated diagnostics, so they must not be counted as
independent evidence. In particular:

- M169 is a **conditional resource survivor**, not a deployable improvement.
- M173 is a **screened hostile-face certificate**, not a generic provider.
- M172 is **static algebra**, not variance or efficacy evidence.
- M154/M165/M168 are **face-local mathematical survivors**, not a complete
  endpoint engine.

The curve should tighten the next falsifier and prevent repeated category
errors. It must not be used to claim a global lower bound, a winning entry,
or that unexplored analytic routes cannot work.

## Frozen evidence index

- `headroom_recursion/fold_ledger.json` (candidate dispositions and invariants)
- `m164_staged_audit/M164_NATIVE_AUDIT_REPORT_20260807.md`
- `m161_response_free_source_variance/M161_SOURCE_VARIANCE_REPORT_20260807.md`
- `m169_m163_call_fusion/M169_NATIVE_AUDIT_REPORT_20260807.md`
- `m170_oriented_tensor_rank/M170_ORIENTED_TENSOR_RANK_REPORT_20260807.md`
- `m171_rank_stratified_provider/M171_RANK_STRATIFIED_PROVIDER_REPORT_20260807.md`
- `m172_selective_22_owner_fusion/M172_STATIC_REPORT_20260807.md`
- `m173_parameter_scaled_boundary_layer/M173_PARAMETER_SCALED_BOUNDARY_LAYER_REPORT_20260807.md`
- `m174_m169_staging_interface/M174_STAGING_INTERFACE_AUDIT_20260807.md`
- `m175_b8_labelled_background_abi/M175_B8_LABELLED_BACKGROUND_ABI_AUDIT_20260807.md`
- `m176_background_archive_producer/M176_EXACT_BACKGROUND_ARCHIVE_NO_GO_20260807.md`

All claims here are transcriptions/syntheses of these frozen local records;
no score-bearing output was generated while preparing this autopsy.
