# WHestBench equivariant relationship graph

Status: design only; no scorer, network forward, dataset row, or holdout was
opened for this document.  It is a bounded Generation-next specification, not
a promoted estimator.  Every proposed relation is grounded in an existing
workspace result.  No index at or above 599 is authorized by this plan.

## Executive decision

Graphify can help organize and query the *research evidence graph*, but it is
not itself a numerical estimator of the WHestBench integral.  The useful
translation is:

1. use a locally curated Graphify graph to connect mechanisms, operators,
   evidence, costs, and falsifiers;
2. compile the surviving connections into a small numerical graph operator on
   the realized MLP weights; and
3. train only the final low-dimensional closure coefficients, with complete
   MLPs (never individual output coordinates) as the cross-validation groups.

The numerical graph must respect three exact symmetries.  This is the most
important constraint in the entire design:

- hidden neurons may be permuted independently in every layer;
- a hidden ReLU neuron may be positively rescaled if its outgoing weights are
  inversely rescaled; and
- because the input is isotropic Gaussian, an orthogonal change of input basis
  must not change the answer.

A graph on raw weight coordinates violates the third symmetry.  A conventional
message-passing graph on raw edge weights violates the positive-rescaling
symmetry.  Either can look impressive on the public networks and fail on fresh
private networks.  The construction below explicitly quotients both out.

There are two hypotheses:

- **H1 -- equivariant residual closure:** predict the systematic residual of
  the cheap full-covariance Gaussian closure from symmetry-safe graph features.
  This is the only graph branch with theoretical championship headroom, but it
  needs out-of-network residual R-squared above 0.965 merely to survive and
  about 0.974 to beat the frozen adjusted-score champion.
- **H2 -- conditioned hybrid coefficient:** predict how much of a centered
  covariance-response control to apply to a sampler.  Existing cross-seed
  evidence says the *realized* oracle sign is mostly integration noise and
  therefore cannot be inferred from weights alone.  H2 is restricted to the
  seed-averaged coefficient/magnitude; a graph is not allowed to pretend that
  it can foresee unobserved scramble noise.

## 1. Two different graphs

### 1.1 Research evidence hypergraph (Graphify's job)

Use the local reports as the only corpus.  Each extracted claim must retain a
relative file path, section heading, and any numerical value on which it
depends.  The useful node types are:

| Node type | Examples |
|---|---|
| `MECHANISM` | Gaussian reclosure, terminal skew, covariance response, harmonic annihilation |
| `OPERATOR` | full-covariance pass, rank-8 influence sketch, dyadic depth fold |
| `INVARIANT` | antipodality, hidden permutation, positive gauge, input O(256) |
| `EVIDENCE` | raw MSE, correction cosine, cross-seed ICC, FLOP count |
| `FALSIFIER` | oracle cap, seed transfer failure, budget lower bound |
| `COST` | measured FLOPs, effective compute, wall-risk class |
| `HYPOTHESIS` | H1 residual closure, H2 response magnitude |

Allowed relation types are `SUPPORTS`, `CONTRADICTS`, `REQUIRES`,
`COMPOSES_WITH`, `DUPLICATES`, `BREAKS_SYMMETRY`, `HAS_COST`, and
`TESTED_ON`.  A relation without provenance is omitted rather than inferred.

The high-value hyperconnections that this graph should expose are:

1. `fullcov reclosure bias` + `true terminal k3/k4 oracle signal` -> the
   missing information is created throughout the network and should be
   represented as layerwise defect sources transported to the output, not as
   another terminal-only fit;
2. `low-rank influence sketch survives a tiny premise` + `active subspaces
   tumble by input` -> influence sketches are plausible *features of a
   response*, not evidence that the input integral is globally low-dimensional;
3. `full k3 does not close a ReLU step` + `four-point vertex is generic` -> a
   learned graph may approximate selected output-relevant fourth-order
   contractions, but must not claim an exact cumulant recurrence;
4. `hybrid oracle ICC = 0.129` + `all six cross-seed oracle transfers worsen`
   -> a deterministic weight graph cannot recover realization-specific error;
5. `late layers manufacture the design-surviving content` + `terminal moment
   oracles work` -> multiscale depth localization is more defensible than a
   single global graph embedding;
6. `5-design annihilates low harmonic degrees` + `sampler is near its linear
   design floor` -> H1 should attack weight-analytic bias, while H2 should add
   only a very cheap control.  A fancier point-placement graph has little
   remaining headroom.

Graphify is therefore a provenance-preserving hypothesis engine.  The final
estimator must be a small, auditable FlopScope implementation and must not
depend on Graphify, a language model, an API, or a local database.

### 1.2 Numerical model graph (estimator's job)

For layers `l=1,...,L`, create neuron nodes `v[l,i]`, `i=1,...,n`.
For `l>1`, a directed bipartite edge from `v[l-1,j]` to `v[l,i]` carries the
realized weight `W[l][j,i]`.  Do **not** create labeled input-coordinate nodes.
The first-layer relation is instead the invariant Gram matrix

```text
G1 = W1.T @ W1
R1[i,j] = G1[i,j] / sqrt(G1[i,i] G1[j,j]).
```

`R1` is unchanged by `W1 -> Q W1` for any orthogonal input rotation `Q` and
transforms equivariantly under a permutation of first-layer neurons.

Optional layer nodes `a[l]` store pooled layer statistics.  Output nodes are
the final-layer neuron nodes; relabeling outputs must relabel predictions in
exactly the same way.

## 2. Exact symmetry contract

Let `P[l]` be hidden-layer permutation matrices and `D[l]` positive diagonal
matrices.  The network function is unchanged under

```text
W1' = Q W1 P[1] D[1]
Wl' = D[l-1]^-1 P[l-1].T Wl P[l] D[l],  2 <= l < L
WL' = D[L-1]^-1 P[L-1].T WL P[L]
```

where `Q` is orthogonal and `P[L]` merely relabels outputs.  (`D[L]` is not a
hidden gauge; positively scaling a final output must positively scale the
predicted answer.)

The implementation must pass four property tests before any target is read:

1. random hidden permutations change no prediction except the requested final
   output permutation;
2. random positive hidden gauges over at least four orders of magnitude change
   predictions only at floating-point tolerance;
3. a random input Haar rotation leaves predictions invariant; and
4. positive scaling of a final output column scales that predicted coordinate.

### 2.1 Gauge-fixed edge coordinates

Run the existing diagonal analytic pass.  For each node define

```text
mu_z[l,i] = sum_j m[l-1,j] Wl[j,i]
q_z[l,i]  = sum_j v[l-1,j] Wl[j,i]^2
s[l,i]    = sqrt(max(q_z[l,i], eps))
alpha      = mu_z / s
p          = Phi(alpha)
m          = mu_z p + s phi(alpha)
e2         = (q_z + mu_z^2) p + mu_z s phi(alpha)
v          = max(e2 - m^2, 0)
a          = sqrt(max(e2, eps)).
```

For `l>1`, the dimensionless edge coordinate is

```text
t[l,j,i] = a[l-1,j] Wl[j,i] / s[l,i].
```

Under any positive hidden-neuron rescaling, numerator and denominator acquire
the same factors, so `t` is invariant.  The final correction is predicted in
dimensionless units and multiplied by `s[L,i]`, giving the required output
scale equivariance.

Allowed local node features are dimensionless:

```text
[1, alpha, Phi(alpha), phi(alpha), m/s, v/s^2,
 phi(alpha)*alpha, phi(alpha)*(alpha^2-1),
 1{|alpha|<0.5}, 1{|alpha|<1}, 1{alpha>3}].
```

Hard indicators may be replaced by fixed smooth hinges, but their thresholds
must be declared before evaluation.  Hidden absolute norms and neuron indices
are forbidden features.

## 3. Relation channels

### 3.1 Signed Hermite edge bank

Let `x=sqrt(n)*t`.  For `q=1,...,4`, use standardized probabilists' Hermites

```text
E1(x)=x
E2(x)=(x^2-1)/sqrt(2)
E3(x)=(x^3-3x)/sqrt(6)
E4(x)=(x^4-6x^2+3)/sqrt(24).
```

Given a `k`-column source state `H[l-1]`, one relation message is

```text
M_q[l] = E_q(x[l]).T @ H[l-1] / sqrt(n).
```

The four channels expose signed paths and second-through-fourth weight
concentrations without storing a third- or fourth-order neuron tensor.  They
are an ansatz for useful contractions, not an exact cumulant closure.

Add explicit ON/OFF channels

```text
M_plus  = max(t,0).T @ H
M_minus = max(-t,0).T @ H
```

and the signed/absolute cancellation diagnostic

```text
chi = abs(M_plus-M_minus) / (M_plus+M_minus+eps).
```

This is the legitimate mathematical content of an "interference" analogy:
positive and negative path contributions cancel.  There is no physical
quantum state or quantum speedup in this classical real-valued scorer.

### 3.2 First-layer correlation relations

For the first layer, use `R1`, not raw `W1`.  Per-node correlation features are

```text
c_k[i] = mean_{j != i} R1[i,j]^k,  k=2,3,4,6
c_abs[i] = mean_{j != i} abs(R1[i,j])
c_max[i] = max_{j != i} abs(R1[i,j]).
```

The first message round may use `R1 @ H`, `abs(R1) @ H`, and `(R1*R1) @ H`.
These are input-rotation invariant and neuron-permutation equivariant.

### 3.3 Defect-source response recurrence

The full-covariance and Hermite reports jointly imply that repeated Gaussian
reclosure suppresses non-Gaussian structure, while true terminal k3/k4 matter.
Represent this as local source terms injected at every layer and transported
through a normalized susceptibility graph.

For source channel `c`, use

```text
u_c[l] = eta_c[l] + p[l] * (t[l].T @ u_c[l-1]),
```

with candidate injections

```text
eta_curv = phi(alpha)
eta_k3   = -alpha*phi(alpha)
eta_k4   = (alpha^2-1)*phi(alpha)
eta_kink = phi(alpha) * 1{|alpha|<1}
eta_ipr  = sum_j t[j,i]^4 / (sum_j t[j,i]^2 + eps)^2
eta_cancel = 1 - abs(sum_j t[j,i])/(sum_j abs(t[j,i])+eps).
```

No coefficient in this recurrence is claimed to equal the missing cumulant.
The output vectors are features whose usefulness must be established by
out-of-network prediction.

### 3.4 Correlation center-surround and morphogen channels

H1 already computes a full covariance at each layer.  Let `C[l]` be that
closure covariance and `Rc[l]` its normalized correlation.  Define a canonical
row-stochastic adjacency

```text
A = (abs(Rc)-I) / row_sum(abs(Rc)-I).
```

For a local defect vector `eta`, the center-surround contrast is

```text
center_surround = eta - A @ eta.
```

A two-rate graph diffusion (the only concrete content retained from a
morphogenesis/Turing analogy) is

```text
slow = (1-0.125)*eta + 0.125*A@eta
fast = (1-0.5)*eta   + 0.5*A@eta
pattern = slow-fast.
```

The rates are fixed premise constants, not fit on a validation set.  There is
no Euclidean neuron lattice, so convolutional neighborhoods, spots, stripes,
or reaction chemistry are empty metaphors and are rejected.  The correlation
graph is the only canonical within-layer topology available here.

### 3.5 Memristic/fading-memory channels

The model has no physical memristor.  A useful operational translation is a
bank of constrained exponential depth memories:

```text
u_beta[l] = beta * p[l]*(t[l].T@u_beta[l-1]) + (1-beta)*eta[l]
beta in {1/2, 3/4, 7/8, 15/16}.
```

These channels test whether closure defects have a short or long effective
depth memory.  The constants are dyadic and predeclared.  If grouped CV does
not improve over the ordinary susceptibility channel, the entire memristic
bank is removed.

### 3.6 Fractal series and tau folding

There is no evidence of literal fractal geometry.  The defensible operation is
a dyadic Haar decomposition of the 32-layer sequence of pooled defect signals.
Store block sums/contrasts on

```text
{1}, {2..3}, {4..7}, {8..15}, {16..31}, {32}
```

and the ordinary Haar contrasts at scales 1, 2, 4, 8, and 16.  This directly
tests the existing observation that relevant residual content is created late
in depth while keeping the basis fixed and small.

"Tau folding" is translated literally as a `tau=2*pi` Fourier readout over
layer index:

```text
F_k^cos = sum_l eta_bar[l] cos(tau*k*l/L)
F_k^sin = sum_l eta_bar[l] sin(tau*k*l/L),  k=1,2,3.
```

Because the feed-forward depth axis is not periodic, this bank has weaker
premise support than the Haar bank.  It is diagnostic-only and must be dropped
unless nested grouped CV selects it without degrading any outer fold.

### 3.7 Tensor/four-point proxies

The cavity report proves that `(mean,covariance,skew)` does not close a ReLU
step and that a generic fixed-instance four-point vertex is too large.  The
cheap graph therefore uses only explicitly labeled proxies:

```text
diag_R2[i] = sum_j Rc[i,j]^2
edge_ipr[i] = sum_j t[j,i]^4 / (sum_j t[j,i]^2+eps)^2.
```

An optional second rung computes `Rc2=Rc@Rc` and

```text
diag_R4[i] = sum_j Rc2[i,j]^2.
```

This costs one dense `n x n` square per layer, about 1.07B FLOPs over 32
layers.  It is still only a Gaussian/correlation four-step contraction, not
the missing connected fourth cumulant.  Fixed labeled random probes are not
used: a particular probe matrix would break exact neuron-permutation
equivariance.

## 4. H1: equivariant residual closure

### 4.1 Target and model

Let `a[W,o]` be the deterministic full-covariance Gaussian prediction and
`y[W,o]` the public truth.  Predict

```text
y_hat[W,o] = a[W,o] + s[L,o] * z_theta(features[W,o]).
```

The first premise model is ridge regression on the fixed graph features.  It
is deliberately not a deep GNN: with only hundreds of independent MLPs, a
large nonlinear model would turn 256 correlated outputs into fake sample
size.  The standardizer, ridge coefficient, feature subset, and penalty are
fit only inside training folds.

Only if the fixed-feature ridge clears the premise gate should a shared
two-layer node MLP be tried.  Its parameters must be shared across layers;
layer position enters through the fixed Haar/depth features.  Width should be
at most 16, and total learned parameters at most 2,000.

### 4.2 Cheapest grouped-CV premise

1. Use only public development MLPs `0..119`.  Run the unscored NumPy
   full-covariance reference and extract the fixed relation features.  The
   existing report measured roughly 0.09 seconds per Gaussian closure on the
   local BLAS build; this premise does not need the official scorer.
2. Use six outer folds of 20 **whole MLPs**.  All 256 outputs of an MLP remain
   in the same fold.  Use five inner MLP-group folds to choose from a tiny
   ridge grid and the nested feature families:

   ```text
   A: analytic local features only
   B: A + signed/absolute response channels
   C: B + Haar/memory channels
   D: C + center-surround channels
   ```

   Tau and optional `diag_R4` are not in the first screen.
3. Report pooled original-unit MSE, per-network MSE, out-of-fold residual
   R-squared relative to `a`, fold range, worst-network ratio, and the exact
   symmetry-test error.
4. Premise promotion requires all of:

   - out-of-fold residual R-squared `> 0.965`;
   - every outer fold has positive residual R-squared;
   - network-cluster bootstrap lower bound `> 0.94`;
   - no network MSE exceeds the anchor by more than 2x; and
   - all four symmetry tests pass.

5. Freeze the complete pipeline before any new slice is inspected.  A later
   confirmation may use an untouched subset below 599.  This document does
   not authorize that read.

The gate is intentionally severe.  The measured anchor MSE is
`5.428e-5`; reaching `1.90e-6` needs about 96.5% residual variance removal.
Beating the frozen adjusted score near `1.41e-7` at the score floor requires
roughly `1.41e-6` raw MSE, or about 97.4% removal.  A visually good 80--90%
R-squared graph is still not competitive.

## 5. H2: graph-conditioned hybrid coefficient

### 5.1 Identifiability boundary

For baseline sampler prediction `p0`, response direction `d=p1-p0`, and error
`e=p0-y`, the per-cell oracle scalar is

```text
lambda_star = -<e,d>/||d||^2.
```

Existing evidence on networks `0..19`, setup seeds `0,1,2`, found cross-seed
oracle correlations only `0.080, 0.162, 0.094`, sign agreement `60--70%`, ICC
`0.129`, and worse MSE for all six cross-seed oracle transfers.  Consequently:

- `lambda_star(W,seed)` is not a weight-identifiable label;
- a weight graph may model only the seed-averaged risk coefficient
  `E_seed[lambda_star ||d||^2 | W] / E_seed[||d||^2 | W]`; and
- sample-derived summaries may be included only if available at inference,
  but must beat the already failed frame disagreements and response summaries.

Any claim that Graphify can infer the unseen scramble-error sign from weights
alone is rejected before training.

### 5.2 Cheapest linear graph gate

For network-level graph features `x(W)`, fit `lambda=x beta` directly under the
actual squared-error objective.  Ridge normal equations are

```text
A = sum_{W,s} ||d_Ws||^2 x_W x_W.T + gamma I
b = -sum_{W,s} x_W <e_Ws,d_Ws>
beta = solve(A,b).
```

This weighting avoids unstable division by tiny response energies.  Clip only
at a predeclared range such as `[-2,3]`.  A quantized version rounds to
`{-2,-1,0,1,2}`; existing evidence says coefficient precision is not the
bottleneck, so quantization is a regularizer, not a FLOP shortcut.

Use the already captured `0..19 x seeds 0..2` only for a nested fivefold
whole-MLP premise.  Compare, in order:

1. one pooled scalar coefficient;
2. pooled scalar plus late-kink fraction;
3. pooled scalar plus at most eight graph features; and
4. graph features plus already-available response summaries.

Every seed for a held-out MLP stays in its outer test fold.  The graph model
must improve on the pooled scalar, not merely on `lambda=0`.  Require positive
gain on each of the three seeds and a MLP-cluster bootstrap interval below
zero.  Given only 20 independent MLPs, this can revive a premise but cannot
promote a submission.

If that screen passes, freeze it and test on `20..119` using the existing
seed-0 capture; only a subsequent multi-seed capture could establish
seed-stable deployment.  The full-covariance response used in the old cache is
too expensive for the current near-budget sampler.  A deployable descendant
must repeat the test with the independent rank-8 influence response (measured
increment about `0.310B` FLOPs in its older parent) or another response whose
actual current-parent cost is measured.  The low reported rank-8/dense
correction cosine (`0.346` on five networks) forbids assuming coefficient
transfer between those directions.

An output-wise equivariant coefficient is a later rung only:

```text
lambda[W,s,o] = clip(c + h_theta(output_node_features), -2, 3).
```

It must be trained with `d[o]^2` weighting and MLP-group folds.  Output-wise
splitting is forbidden because the 256 outputs share all upstream weights and
are not 256 independent training examples.

## 6. FLOP and wall-risk ledger

At `n=256`, one dense `n x n` GEMM is about `33.49M` billed FLOPs, and one
`n x n` by `n x k` message multiply is approximately `2 n^2 k`.

| Component | Estimated incremental billed FLOPs |
|---|---:|
| first-layer invariant Gram | `0.0335B` |
| four edge-relation channels, `k=8`, 31 transitions | `~0.130B` |
| correlation/center-surround messages, `k=8`, 32 layers | `~0.034B` |
| node updates, pools, Haar/memory summaries | `<0.020B` |
| **cheap relation graph** | **`<0.22B` target** |
| optional exact `Rc@Rc` at every layer | `~1.07B` |
| measured standalone full-covariance anchor | `6.189B` analytical FLOPs |
| measured rank-8 response increment in older parent | `0.310B` |

The graph matrices with different edge bases should be packed where the
accounting backend permits a single matmul.  Setup-constant coefficient arrays
must be allocated once.  Reshapes, gathers, and many tiny calls can dominate
residual-wall charges even when the arithmetic ledger is small, so the
official cold subprocess remains authoritative before packaging.

For H1, a `~6.5B` analytic estimator remains at the 0.1 multiplier floor; raw
accuracy dominates.  For H2, the frozen sampler is already near `249B`
effective compute, so even the cheap graph plus rank-8 response must buy more
raw MSE than its compute fraction and wall risk.  No graph feature is free.

## 7. Leakage, legality, and falsification guards

### Data firewall

- No index `>=599` may be loaded under this plan.
- Never use dataset index, filename, serialized hash, MLP seed, or ordering as
  an input feature.
- Truth is a training label only.  Target-derived normalization, feature
  selection, early stopping, or coefficient clipping must be fit inside the
  training fold.
- All outputs and all setup seeds belonging to one MLP stay in one fold.
- A locked/confirmation slice is opened only once after the full model,
  feature family, coefficients, and hashes are frozen.

### Fresh-network contract

- Train a universal equivariant mapping, never a nearest-network lookup.
- Run a label-shuffle control.  It must return approximately zero OOF
  residual R-squared.
- Run a fingerprint audit against weight norms/hashes even though none are
  features; unexpectedly high nearest-neighbor performance invalidates the
  result.
- Report performance by network, not only by 256 output coordinates.

### Inference contract

- Bundle fixed coefficients and small assets in the submission.
- Every MLP-dependent operation, including feature extraction, standardizing,
  graph messages, and learned readout, must use FlopScope.
- No Graphify, Python subprocess, model server, Ollama, API, NumPy escape, or
  online adaptation at evaluation time.
- Non-finite features fall back to the frozen parent/anchor; count and report
  every fallback.

### Scientific falsifiers

Kill H1 if it misses `R^2=0.965`, if any outer fold is negative, or if its gain
vanishes after grouping by MLP.  Kill H2 if graph conditioning fails to beat a
single pooled coefficient on every setup seed, or if raw gain does not repay
measured compute.  Kill any biological, fractal, tau, memristic, tensor, or
interference channel that is not selected in nested grouped CV.  Metaphorical
novelty is not evidence.

## 8. Priority order and deepest insights

1. **Build H1 fixed graph features first.**  It is cheap, symmetry-correct,
   and attacks the only measured analytic gap large enough to matter.  Its
   96.5--97.4% gate will kill it quickly if the residual is not structurally
   learnable.
2. **Use H2 primarily as a no-go/identifiability test.**  The evidence already
   predicts that weight-conditioned sign inference will fail because most
   oracle variation belongs to the scramble, not the MLP.
3. **The most promising cross-domain synthesis is source localization plus
   response transport:** Hermite-shaped local defect sources, correlation
   center-surround contrasts, dyadic depth readouts, and signed/absolute path
   cancellation.  Each is a concrete graph operation tied to a measured
   failure of Gaussian reclosure.
4. **The strongest invariant is the positive ReLU gauge, not merely neuron
   permutation.**  Enforcing it removes an enormous family of public-set
   shortcuts and makes fresh-network generalization materially more credible.
5. **Do not confuse a relation graph with a low-dimensional input subspace.**
   The graph is over neurons, weights, and moment responses.  It does not
   contradict the measured tumbling of input Jacobian subspaces.
6. **Do not claim quantum, biological, memristive, or fractal physics.**  The
   retained content is respectively signed cancellation, correlation-graph
   diffusion, fading depth memory, and dyadic multiresolution.  Those
   operations live or die by the same grouped-CV and FLOP gates as everything
   else.

## 9. Existing local evidence used

- `fullcov_gaussian_mm/REPORT.md`: `5.428e-5` raw MSE, `6.189B` analytical
  FLOPs, and failed scalar residual alignment.
- `final_hermite_cumulants/REPORT.md`: true terminal k3/k4 oracle signal and
  analytic attenuation of skew/kurtosis.
- `cavity_dyson/REPORT.md`: non-closure of `(m,C,T)` and generic four-point
  vertex cost.
- `lowrank_covariance/REPORT.md`: independent influence rank-8 premise,
  `0.310B` measured incremental FLOPs, and low dense/sketch direction cosine.
- `hybrids/TARGET_FREE_LAMBDA_GATES.md` and
  `hybrids/multiseed_oracle_analysis.json`: hybrid sign non-identifiability,
  ICC `0.129`, and cross-seed transfer failures.
- `hybrids/regime_quantization_dev0_119.json`: a small crossfit scalar feature
  model gained about 6.16% on one development protocol, but does not overturn
  the multi-seed identifiability result.
- `nonlinear_shrinkage/REPORT.md`: per-network amplitude instability despite a
  small pooled gain.
- `antipodal_parity_fold/RESULTS.md`: direct and unbiased recursive parity
  folds are cost-dilutive.
- `exact_line_conditioning/REPORT.md`: literal affine-line conditioning is
  killed by region growth.

No claim in this specification supersedes those reports.  The graph is a new,
falsifiable composition of their surviving information.
