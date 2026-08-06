# Physarum/MoE target-free routing premise

## Verdict

Kill the fixed P0/P1 specialization. Preserve the invariant graph, electrical
flow, conductance update, entropy/cost barrier, and complete-expert combiner as
router primitives.

The frozen promotion candidate—attention-initialized Physarum top-1—does not
specialize. It selects `fullcov_gaussian` in all 24 states:

| primary metric | result | gate |
|---|---:|---:|
| loss ratio to always Haar+chi2 | 0.866761 | <=0.80 |
| state wins | 18/24 | >=18/24 |
| maximum top-1 load | 1.000 | <=0.75 |
| experts used | 1 | >=2 |
| soft route entropy | 0.9749 | >=0.35 |
| expert-only cost ratio | 0.1327 | <=1 |
| proxy-inclusive cost ratio | 0.5306 | <=1 |

The accuracy, discrete load, and expert-diversity gates fail. Symmetry, cost,
PSD, finite-output, and target-free sequencing checks pass.

More decisively, the frozen expert bank lacks enough headroom for any router:

```text
post-hoc best pure expert per state:       0.833818 x parent loss
post-hoc best convex top-2, 101-point grid: 0.829054 x parent loss
required:                                  <=0.800000.
```

Even a clairvoyant selector cannot pass the frozen 20% gate. Router retuning or
training would therefore be invalid and futile on this bank.

No WHest MLP, public/private truth, scorer, API, or learned weight was used.

## Grounded translation

The experiment implements the safe translation in
[`sources/research_physarum_moe_relu_routing_20260806.md`](../../../sources/research_physarum_moe_relu_routing_20260806.md):
whole moment-safe rules are expert nodes; invariant boundary/covariance/weight
observables form the demand query; edge length combines mismatch and cost; an
electrical pressure solve creates unit flow; and damped conductance follows
flow magnitude with an entropy barrier.

The relevant source-level ideas are preserved:

- Tero-style local conductance adaptation trades transport against network
  cost and robustness;
- the Bonifaci-Mehlhorn-Varma shortest-path result predicts loss of initial
  conductance memory under standard Physarum convergence;
- entropy-regularized flow motivates the nonzero barrier prior;
- sparse MoE work motivates top-1/top-2 whole-expert activation and explicit
  load audits;
- scaled dot-product attention supplies only the fixed compatibility prior,
  not a trained transformer.

The outcome is consistent with that mathematics: after 32 iterations,
uniform- and attention-initialized Physarum have the same top-1 and top-2 expert
sets. Flow converges toward the same cheapest/matched route, washing out the
attention initialization.

## Target-free two-phase contract

The bank contains 24 fresh states:

```text
widths 16,24 x intermediate depths 2,4,6 x four seeds.
```

Each parent uses 32,768 Philox Gaussian inputs plus negatives. Phase one:

1. generate a parent activation cloud;
2. retain only empirical mean/covariance and a fresh downstream matrix;
3. compute ten permutation/gauge-invariant query features;
4. freeze every uniform, attention, Physarum, and attention-Physarum top-1/top-2
   route;
5. discard the particles.

Phase two deterministically regenerates particles, evaluates the four experts,
and finally exposes the uncompressed one-step ReLU mean/covariance reference.
The machine result stores a pre-evaluation route digest. No expert result or
reference statistic can enter selection.

## Complete experts

Every sigma rule exactly recovers affine mean/covariance before ReLU; all rules
return a complete post-ReLU mean and covariance.

| expert | loss ratio to Haar+chi2 | wins vs parent | post-hoc best states |
|---|---:|---:|---:|
| full-covariance Gaussian | 0.866761 | 18 | 16 |
| fixed-axis sqrt(n) sigma | 1.213616 | 5 | 3 |
| seeded-Haar sqrt(n) | 0.995470 | 17 | 4 |
| seeded-Haar chi2 | 1.000000 | 0 | 1 |

There is genuine but weak instance specialization. Full covariance is the best
aggregate expert and wins two-thirds of oracle assignments. The minority
experts do not lower the oracle envelope enough to meet the gate.

The optional covariance-algebra compressor was deliberately excluded. Its
representation report was finalized, but coefficient formation and recurrence
are unresolved, so it is not yet a complete moment-safe rule eligible for this
contract.

## Router ablation

| router | top-k | loss ratio | wins | load pattern | proxy-inclusive cost |
|---|---:|---:|---:|---|---:|
| uniform | 1 | 0.9841 | 11/24 | 6/6/6/6 | 0.7704 |
| uniform | 2 | 0.9834 | 14/24 | 12/12/12/12 | 1.1429 |
| attention | 1 | 0.9966 | 3/24 | 0/0/3/21 | 1.0619 |
| attention | 2 | 0.9960 | 17/24 | 0/0/24/24 | 1.6122 |
| Physarum | 1 | 0.8668 | 18/24 | 24/0/0/0 | 0.5306 |
| Physarum | 2 | 0.8927 | 20/24 | 24/0/24/0 | 1.0663 |
| attention-Physarum | 1 | 0.8668 | 18/24 | 24/0/0/0 | 0.5306 |
| attention-Physarum | 2 | 0.8929 | 20/24 | 24/0/24/0 | 1.0663 |

Load order is `fullcov/fixed/Haar-sqrt/Haar-chi2`.

Top-2 Physarum wins more states but is worse in aggregate than pure fullcov and
exceeds parent compute after routing proxies. This is the mediant warning in
action: mixing positively correlated errors dilutes the better pure rule.

## Why high entropy still collapsed

Attention-Physarum soft weights vary only over these ranges:

```text
fullcov:    0.3277 .. 0.3772
fixed:      0.1674 .. 0.1821
Haar-sqrt:  0.2337 .. 0.2939
Haar-chi2:  0.1721 .. 0.2339.
```

Their normalized entropy is high, but fullcov is always the largest component.
Hard top-1 therefore has 100% fullcov load. Soft allocation entropy is not a
valid substitute for discrete top-k load balancing. A future router would need
an explicit capacity constraint or balanced assignment; adding one here would
change the frozen premise and cannot repair the expert-bank oracle bound.

The primary matches the post-hoc best expert in 16/24 states—exactly the states
where fullcov is best. The query/key map does not recognize the eight minority
specialization states.

## Mediant and complementarity audit

Normalized expert error correlations are:

| | fullcov | fixed | Haar-sqrt | Haar-chi2 |
|---|---:|---:|---:|---:|
| fullcov | 1.000 | 0.895 | 0.924 | 0.934 |
| fixed | 0.895 | 1.000 | 0.814 | 0.831 |
| Haar-sqrt | 0.924 | 0.814 | 1.000 | 0.997 |
| Haar-chi2 | 0.934 | 0.831 | 0.997 | 1.000 |

The two Haar radial experts are nearly redundant at one step. The best oracle
convex top-2 improves the oracle pure selector only from `0.8338` to `0.8291`.
This is insufficient error complementarity, not a routing-optimization problem.

Post-hoc best convex pairs are distributed across fullcov+fixed,
fullcov+Haar-sqrt, fullcov+Haar-chi2, and fixed+Haar-sqrt. That variety confirms
some state dependence, but the gain magnitude remains below contract.

## Rotation and symmetry audits

Only one Haar frame is used per state, seeded by `104729 + state_seed`. Neither
routers nor diagnostics compare rotations. This respects the existing proof
that best-of-fresh-rotation selection is a coin flip.

Under a coordinate permutation:

- invariant query error: `1.11e-16`;
- primary route error: `5.55e-17`;
- coupled expert mean error: `2.22e-15`;
- coupled expert covariance error: `6.00e-15`;
- scaled maximum: `2.27e-15`.

The Haar check uses the coupled frame `Q'=P Q`, establishing distributional
symmetry without selecting a lucky frame. All routed covariances are PSD within
roundoff and no nonfinite output occurs.

## Proxy economics

The query charges one `9n^3` eigensystem and caches it for sigma experts.
Primary top-1 selects cheap full covariance, so total proxy-inclusive cost is
only `0.5306` of the parent; proxies do not erase those savings. They do erase
top-2 savings: Physarum top-2 costs `1.0663`, uniform top-2 `1.1429`, and
attention top-2 `1.6122` times the parent.

The full 24-state two-phase run measured 90.34 MiB peak working set and 579.57
MiB peak pagefile allocation. States are processed sequentially; phase-one
particles are discarded before phase-two regeneration.

## Failed specialization link and next move

The failed link is not the pressure solve. It is the combination of:

1. insufficient oracle headroom in the frozen complete-expert bank; and
2. a fixed compatibility/length map whose top-1 ranking collapses to the best
   aggregate cheap expert.

Preserve:

- invariant demand/expert graph;
- electrical pressure-flow solver;
- damped conductance update and entropy/cost prior;
- target-free route-before-evaluation contract;
- whole-expert raw-second combination and cost ledger.

Do not train or retune the router next. First validate a genuinely complementary
complete expert whose post-hoc oracle bank pushes below `0.80`. Only then can
routing matter. The residual covariance-algebra branch is a promising source
after it acquires deployable coefficient formation; until then it cannot enter
the bank. A later router should use capacity-aware top-k and must re-freeze its
keys and load rule before evaluation.

Artifacts: `PREDECLARED_GATE.md`, `physarum_router.py`, `run_premise.py`,
`premise_results.json`, `resource_audit.json`, `structural_audit.json`,
`decision.json`, and tests in this directory.
