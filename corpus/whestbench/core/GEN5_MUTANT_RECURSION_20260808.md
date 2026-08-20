# Generation 5 mutant recursion packet -- 2026-08-08

## Goal and honest status

Goal: produce the lowest private-suite adjusted MSE permitted by the published
WHestBench rules, with every MLP-dependent operation billed, no evaluator or
truth leakage, no lookup/memorization, no accounting bypass, and zero resource
failures.

The current artifact to ship is still **Kerdock v3.1 GUARDS**, SHA-256
`8382e269c9b32e0935492734ddf8182560120f7e9331621aa18839d5d1f4ea06`.
It is bitwise-compatible with the healthy v3 estimator and closes two hostile
failure modes.  It is the best validated artifact, not a demonstrated winning
entry.  The new M192 oracle is the largest fresh mathematical headroom signal,
but M193--M197 prove that the tested truth-free realizations do not harvest it.

## Evidence graph and god nodes

```text
exact radial conditioning (2.141x)
  + Kerdock complete frames (2.016x)
  + antipodal pairing (1.908x)
  + pruning/folding (MSE-neutral cost removal)
  -> v3.1 GUARDS
       |
       +-> remaining high-degree angular / rotation error
       |     |
       |     +-> low-degree harmonic controls: dispersed, killed
       |     +-> rotation selection: oracle exists, proxy information killed
       |     `-> M192 frame-covariance GLS: 87.38% oracle reduction
       |             |
       |             +-> M193 analytic anchor: correlated cross term, killed
       |             +-> M194 independent pilot: finite-output SNR/cost, killed
       |             +-> M195 equal-cost split: destroys degree-4 structure
       |             `-> M197 three-way crossed split: same failure, killed
       |
       `-> weight-analytic higher cumulants
             |
             +-> generic sketches/source sampling: variance or cost killed
             +-> M151 B=1 exact forward source control: static survivor, blocked
             `-> final-row random-projection quotient: new premise, untested
```

The active god nodes are now:

1. the common/contrast error block visible to truth in M192 but not to an
   affordable runtime observable;
2. exact signed higher-order source formation with bounded variance;
3. a target-shape native provider/compiler under inclusive cost;
4. fresh whole-network generalization and hostile resource safety.

Metaphors are normalized before entering this graph.  Padgett/fractal/cymatic
language maps to Haar phase orbits, spherical harmonics, wavelet persistence,
or tensor contractions.  Biological attenuation maps to constrained GLS or
multifidelity control.  No metaphor receives evidence credit.

## The new failure curve and what it implies

M192 learns the error covariance from truth on other outputs and gives panel
ratio `0.126193`.  Its projected-block truth diagnostic gives `0.112710`.
The truth-free anchor curve is:

```text
analytic anchor       1057.899x
independent k=1         97.600x
k=8                     15.831x
k=32                     3.615x
k=64                     1.525x
k=126                    0.671x raw, 1.343x after cost
two 63-frame halves       1.157x at equal cost
three 42-frame crosses    1.369x at equal cost
```

This curve is the inference, not just a list of losses.  Projection identifies
the contrast covariance exactly, while the small cross block needed to correct
the common frame error is estimated with only 224 training outputs.  Pilot
noise times frame contrast overwhelms it.  Increasing pilot precision works
monotonically but becomes a second full estimator before adjusted parity.
Reusing the pilot as a half estimator preserves cost but breaks the Kerdock
degree-4 relation. M197's final distinct crossed topology used two independent
pilots per correction at the same 126-frame budget; its exact unknown-mean
cancellation and sum-one checks passed, but the three-by-42 split worsened all
networks. Therefore another anchor/pilot/frame split is not a prime
candidate; reopening requires a new sigma-algebra, such as an exact conditional
weight observable or late-layer source identity.

## Padgett/harmonic branch disposition

The rigorous phase translation produced no survivor:

- a frozen dyadic Haar phase-persistence selector was 11.46% worse after cost,
  with selection accuracy 45.83% and pooled correlation 0.021;
- a phase-centered sparse second-layer surrogate was genuinely outside the
  earlier first-layer tangent family, but its best read-only setting improved
  only 1.26% raw and worsened one held network before cost;
- centered cubic/bispectral controls were between about 0.6% gain and 5.9%
  loss on the read-only screen;
- randomized harmonic trace probes suffer RMS amplification about 11.6 at
  degree 4, 3,637 at degree 6, and 125,612 at degree 8.

Preserve the exact multifidelity centering identity

    Q(R1) - B [ S(R1) - mean_k S(Rk) ]

because it is randomized-unbiased for exchangeable rotations even when the
surrogate mean is unknown.  Reopen it only when a new cheap surrogate observes
error manufactured in the final third of the network.  Do not search more
wavelet scores, signs, cubic powers, or sparse-layer ranks on the burned cache.

## Prime candidate A -- M151 exact B=1 forward source control

M151 is the strongest exact unfinished branch.  It writes the three-label
fourth-cumulant source as a deterministic 49-node control plus an exact
full-support residual:

    T_211 = C_211 + E[Rhat],
    E[C_211 + Rhat] = T_211.

The source is sent forward through the existing M125b carrier, avoiding the
all-output reverse adjoint that killed M150.  Its five algebra tests pass.  The
known branch bill is 89.708636240B, leaving an inclusive 10.291363760B for the
native B=1 state provider, glue, uncredited carrier calls, allocations, and
priced residual wall time.

This is not yet an estimator.  Its next and only authorized gate is:

- [ ] Build a response-free, positive-gauge and hidden-permutation-covariant
      B=1 state provider.
- [ ] On 24 generated cells, compare exact source/residual variance with fixed
      seeds; require mean residual/source variance ratio `<0.25` and p99
      `<=1.25`.
- [ ] Produce a native target-shape trace including one M125b insertion;
      require inclusive new cost `<=10.291363760B` and peak `<=512 MiB`.
- [ ] Fail closed if any provider/state/hash/source-owner guard fails.

WIP limit is one: no efficacy or truth run until all four boxes pass.

M196 froze this gate and stopped correctly before variance execution.  The
repository currently has no deterministic 49-node B=1 state provider, no
non-cubic target compiler, no bound M147 batch coefficient provider, and no
inclusive native trace.  M179 supplies only `(mu,V)`; M151's compiler is an
exhaustive parity oracle explicitly prohibited at width 256.  Therefore the
24-cell gate is **blocked on named interfaces**, not failed statistically and
not authorized to run with fabricated conditional moments.  See
`experiments/m196_m151_b1_gate/`.

## Prime candidate B -- final-row random-projection quotient regression

The 256 final weight rows are independent projections of one shared
penultimate activation law.  For `z_j=w_j^T h`,

    kappa_q,j = <K_q(h), w_j^(tensor q)>,    q in {3,4}.

A small iid path pilot can estimate scalar k-statistics for all outputs at
once.  Output-fold cross-fitting would regress them only onto an already
certified physical M18/M22 polynomial quotient and then apply a frozen
Gram--Charlier ReLU correction to analytic `(mu,sigma)`.  This changes the old
failed link: the coefficient right-hand side comes from simultaneous final-row
projections rather than layerwise cumulant transport or hidden-edge sampling.

The feature map and its target-shape equivariant emission must be located and
costed before a statistical run; no new learned basis may be invented from
outcomes.  A 4,096-path pilot is roughly 17.2B dense-forward FLOPs.  The
strongest rival is same-cost direct pilot Monte Carlo.

Static/premise gates:

- [ ] Bind the exact existing physical quotient and prove positive-gauge and
      output-permutation covariance at target width.
- [ ] Predeclare pilot sizes and regularization on generated development units.
- [ ] Require out-of-fold cumulant-energy `R^2 >= 0.5`.
- [ ] Require corrected mean MSE to beat same-cost direct pilot MC.
- [ ] Require the gain on 20 independent whole-network units; output neurons
      are not validation replicates.

If the physical quotient cannot be emitted cheaply and equivariantly, kill at
the static gate without touching truth.

## Accelerated recursion compiler

Every future arm receives a packet with these mandatory fields:

```text
identity: generation_id, candidate_id, family_id, arm_index, family_size
champion: artifact hash, statistical-parent hash, compatibility evidence
invariants: objective, score, versions, B, 0.95B safety cap, bias class, legality
lineage: parents, preserved components, changed link, first break, assumptions
mechanism: equation, information set, prediction, rivals, cheapest falsifier
fingerprint: operator/info/cost hashes, symmetry contract, nearest ledger IDs
caches: path, SHA-256, arrays, unit, leakage class, allowed use, read-only flag
budget: static, residual, combined, hostile, delta, deterministic cap
experiment: units, seed map, gates, metric, cluster bootstrap, holdout commitment
multiplicity: <=8 arms/generation, <=2/family, futility-only early looks, Holm final
firewall: proposer cannot see holdout; no public-burned proposal generation
result: packet/results/per-unit/notes/hashes, two-signal check, deviations, verdict
```

Deterministic seed selection:

1. Normalize ledger nodes to validated, preserved, killed, open, or blocked.
2. Connect only a preserved component to the earliest open failed link.
3. Reject renamed metaphors, coefficient-only respins, theorem-subsumed arms,
   contained information sets, over-budget lower bounds, and affine mixtures of
   cached losers.
4. Rank by conservative headroom, evidence grade, cache coverage, cost, then
   multiplicity.
5. Reserve one exact-identity slot and one genuinely new-observable slot.
6. Cache replay may kill an implementation but never promote it.
7. Any mutation invented after seeing a cache result moves to fresh units.

Measured acceleration: reusing the archived bitwise baseline and stopping
failed primary gates would cut the prior PB-1 campaign from 4,375.1s to
1,538.5s (`2.84x`).  Four-replicate futility gates project about 385s for a
flat PB-1-like family (`7--11x` faster).  Cached frame tests are sub-second and
avoid tens of trillions of research-forward operations, but remain premise
tests only.

## What-if oracle map

These branches are scenarios, not evidence:

| scenario | discriminating observation | action |
|---|---|---|
| Omega: M151 source control works | variance gates pass and inclusive provider trace fits | integrate carrier, then 20-net screen |
| Alpha: M151 algebra works but costs > cap | trace exceeds 10.291B or hostile cap | preserve identity, kill provider arithmetic class |
| Beta: final-row quotient works | OOF R2 >=0.5 and beats matched direct MC | fresh 20-net screen, then untouched holdout |
| Delta: quotient is MC in disguise | same-cost MC matches/beats it | kill quotient, retain k-stat diagnostics only |
| Psi: both moonshots fail | both first breaks recur | ship v3.1 GUARDS; frontier remains unpublished math or audited artifact |
| Phi: new arm passes development only | fresh holdout or hostile tail fails | no promotion; localize bias/resource break |

## Definition of a prize answer

A “winning entry” is not a promising equation or an oracle ratio.  It is a
hash-bound package that clears, in order: exact/static contract, cheapest
premise, 20-network screen, multiplicity-corrected development, untouched
whole-network validation, exact cost and wall trace, healthy compatibility,
hostile resource suite, package validation, and an explicitly authorized
official canary.  Until a child clears those gates, v3.1 GUARDS remains the
definitive honest artifact.
