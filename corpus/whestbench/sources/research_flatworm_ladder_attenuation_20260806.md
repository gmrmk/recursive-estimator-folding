# Flatworm ladder attenuation for invariant estimator routing

Date: 2026-08-06

Purpose: translate documented planarian/flatworm nervous-system organization
into a small, falsifiable attenuation operator for the WHestBench recursive
estimator search. This is research inspiration, not a claim that the proposed
equations are a biological model of planarian neural computation.

## What the biology supports

1. **Orthogonal or ladder organization.** Reviews describe paired or multiple
   longitudinal nerve cords connected along the body by transverse commissures.
   In planarians, two ventral longitudinal cords extend from the bilobed brain
   and are linked by transverse nerves/commissures. This supports a two-lane
   longitudinal-plus-cross-coupling topology.
2. **Bilateral/anterior integration.** Planarians integrate multiple sensory
   modalities and can prioritize behavior rather than responding to each
   stimulus independently. Exact circuit pathways remain incompletely mapped.
3. **Temporal attenuation exists.** Direct neurophysiological measurements
   report sensory adaptation and habituation to repeated vibration, with
   dishabituation after a distinct UV stimulus. Recent work also reports
   delayed temporal filtering of periodic UV input. This supports testing a
   leaky/fatiguing state, but not importing a specific synaptic mechanism.

## What the biology does *not* establish

- The sources do not establish that transverse planarian commissures implement
  the exact lateral-inhibition matrix used below.
- They do not establish a transformer, softmax, mixture-of-experts router, or
  Physarum-like conductance law in flatworms.
- Therefore, commissural diffusion, divisive attenuation, and novelty relief
  are explicitly labeled computational hypotheses. They must earn their place
  by matched estimator experiments.

## Ordinary mathematical translation

Let `u[l,e]` be target-free, permutation-invariant evidence for whole estimator
expert `e` at layer/depth position `l`. Let `D[l,e]` be the Physarum conductance
before attenuation. Pair experts only by a predeclared mechanism relation (for
example fixed/Haar geometry or fixed/two-node radial law), never by observed
error.

### Longitudinal cords: leaky evidence memory

```text
m[l] = rho*m[l-1] + (1-rho)*u[l],       rho = 1/2.
```

This is a depth-wise low-pass filter. It is the classical operator suggested by
the longitudinal cords; the dyadic coefficient avoids learned parameters.

### Transverse commissures: paired consensus/contrast

For each frozen pair, with pair-graph Laplacian `L_pair`,

```text
m_tilde[l] = (I - kappa*L_pair)*m[l],   kappa = 1/4.
```

At `kappa=1/4`, the two-channel block is
`[[3/4,1/4],[1/4,3/4]]`: PSD, mass preserving, nonexpansive, and equivariant to
swapping the two lanes. This is computational commissural diffusion, not a
claim of known planarian inhibition.

The observable disagreement is

```text
c[l,e] = abs(m[l,e]-m[l,pair(e)]) /
         (abs(m[l,e])+abs(m[l,pair(e)])+eps).
```

### Habituation: conductance fatigue with continuous novelty relief

```text
f[l] = rho*f[l-1] + (1-rho)*abs(q[l])
r[l] = abs(u[l]-u[l-1]) / (1 + abs(u[l]-u[l-1]))
D_eff[l] = D[l] * (1+r[l]) / (eps+f[l]).
```

Normalize `D_eff` before solving the next unit-demand flow. Repeated large flow
raises fatigue; a changed invariant input supplies bounded, threshold-free
relief. Because routing uses only complete estimator experts, this changes
allocation rather than silently deleting terms inside an estimator.

### Alternative use after the first router falsifier

If a frozen expert bank has an oracle ceiling above the promotion threshold,
no attenuation law can manufacture missing expert accuracy. In that case the
ladder operator is preserved and moved to the response-compression problem:

- lane 1: gate/mean susceptibility response;
- lane 2: active pair-covariance response;
- longitudinal axis: network depth;
- transverse coupling: consensus only where channel cosine is high;
- contrast preservation: retain rank two rather than average the lanes where
  channel cosine falls.

This second translation directly addresses the observed dual-observable
failure: the two response Grams become increasingly orthogonal at later depth,
so scalar averaging erases useful contrast. A flatworm-style ladder should
attenuate shared noise early but keep two lanes late.

## Frozen experimental series

The current Physarum P0/P1 result must remain untouched. A separate P2 compares
on the same fresh states:

1. Physarum only;
2. Physarum + longitudinal leak;
3. Physarum + leak + commissural diffusion;
4. Physarum + leak + commissural diffusion + fatigue/novelty relief.

Primary child gate: at least 10% loss reduction versus Physarum alone, no
symmetry/PSD/resource failures, and no increase in selected expert compute. A
stability-only result is recorded separately and cannot be called an accuracy
promotion. If the expert-bank oracle ceiling is already insufficient, mark the
router child structurally tested but accuracy-nonidentifiable and move the
operator to the two-lane response compressor.

For the response-compressor use, the premise gate is cheaper: show that an
invariant two-lane depth recurrence predicts the depth at which the gate and
active Grams decorrelate, while a scalar lane cannot. Only then implement a
rank-two q3 mixture compressor. No truth-fitted coefficients or post-hoc depth
thresholds are allowed.

Complexity is `O(L E^2)` for `E<=4` router experts, or `O(L)` for the two-lane
response controller, negligible relative to matrix propagation. Exact swap,
neuron-permutation, covariance-factor-gauge, and deterministic-seed tests are
mandatory.

## Primary and review sources

- Laumer et al., **Evolution of flatworm central nervous systems: Insights
  from polyclads**, 2015. Describes longitudinal cords connected by transverse
  commissures in an orthogonal/ladder arrangement.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4612602/
- Inoue et al., **Planarian shows decision-making behavior in response to
  multiple stimuli by integrative brain function**, 2015. Behavioral evidence
  for multisensory integration and explicit caution that the neural pathways
  remain incompletely resolved.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4657317/
- Rouhana et al., **Planarian nociception: Lessons from a scrunching flatworm**,
  2022. Review of the bilobed brain, paired longitudinal cords, and transverse
  nerves forming a grid/ladder.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9362985/
- Haghighat et al., **Neurophysiological measurements of planarian brain
  activity: a unique model for neuroscience research**, 2024. Direct activity
  measurements during sensory adaptation, vibration habituation, and
  UV-induced dishabituation.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11391828/
- **Neuropeptide-mediated temporal sensory filtering in a primordial nervous
  system**, 2025. Reports delayed tracking and temporal filtering of periodic
  UV stimuli in planarians.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11702643/

Search note: the requested academic-search tooling was unavailable locally in
an authenticated form, so the research-lookup skill used web fallback and
prioritized full-text primary/review articles in PubMed Central. No API key was
used. Search results and all cited URLs are preserved here.
