# M114: gauge-canonical particle support-residual closure

**Scope.** Research and design only.  This note does not run a network forward,
generate a training set, read contest targets/scorers, create a learned artifact,
or modify a submission.  It assumes the rules audit described in the request:
offline training on independently generated iid-He networks and a bundled
learned artifact of at most 50 MiB are lawful; evaluator inference is offline.

## Decision first

**Do not begin a full amortized-training campaign now.**  The one proposal with
a genuinely new information path is worth at most one small, frozen,
generated-only falsifier.  It is not a high-confidence replacement for the
current sampler.

The proposal is a *canonical-gauge particle support-residual closure* (CG-PSR):

```text
fixed nested spherical-QMC base (many actual sample paths)
        +
gauge-canonical, full-Gram and sampled gate-pair graph recurrence
        -> learned residual of that particular base estimate
        -> 256 output means
```

It is materially different from the killed signed/absolute/squared node
student: it supplies (i) the full first-layer Gram as a permutation-equivariant
edge graph and (ii) actual, sample-path gate intersections at every depth.  It
does **not** claim a finite exact moment closure.  Its prediction is a biased,
amortized quadrature correction.

That distinction matters.  The prior cleanroom student reached
`1.8470e-5` generated-test MSE and its target-informed 50-channel per-network
oracle still reached `1.1267e-5`, while the stated twofold admission reference
was `1.5447e-7`.  More width or another ordinary attention layer cannot repair
that representation.  CG-PSR earns a test only because the old state saw the
first Gram through row summaries and contained no actual deep gate-pair graph.
There is no source theorem that says the new finite particle state is
sufficient, and the existing Hermite/cumulant work is a strong negative prior.

The operational recommendation is therefore:

1. Freeze and run the small falsifier in this note only if a day or two of
   generated-only CPU time is available.
2. Promote to a real training schedule only on a large held-network effect,
   not on loss curves or a source-theory analogy.
3. If it fails any kill condition, retire *amortized closure as a campaign
   branch* for this deadline.  Do not retry with more width, more attention,
   different optimizers, or a different seed.

## Problem and non-negotiable symmetries

Let `W_l` map layer `l-1` to layer `l`, with `W_l` shaped `256 x 256` and
`L=32`.  Write

\[
 z_l=W_l h_{l-1},\qquad h_l=[z_l]_+,
\]

with a final linear or final ReLU head as required by the benchmark.  The
construction below works for either head; only the final sampling head changes.
The target is `m(W)=E_X[f_W(X)]` for `X ~ N(0,I_256)`.

For hidden layers `1,...,L-1`, the positive ReLU gauge is

\[
 W_l' = D_lW_lD_{l-1}^{-1},\qquad D_0=D_L=I,\quad D_l\succ0.
\]

It leaves `f_W` exactly unchanged.  Independent hidden-neuron permutations
act as

\[
 W_l'=P_lW_lP_{l-1}^{T},\qquad P_0=I.
\]

They leave the target invariant for hidden layers and permute the 256-vector
at the output when `P_L` is included.  A legal model must obey

\[
 \widehat m(g\cdot W)=P_L\widehat m(W)
\]

for any composition of these actions.  That is an architectural condition,
not an augmentation hoped to be learned from iid-He data.

This memo deliberately makes **no exact input-orthogonal-invariance claim**.
The true Gaussian integral has it, but a frozen finite direction bank does not
have it sample-by-sample.  The requested hidden-permutation and ReLU-gauge
symmetries are exact in real arithmetic.  If the evaluator also actively
tests arbitrary rotations/permutations of input coordinates, the fixed-QMC
base below is disqualified unless the sampling protocol itself is changed.

## Why the obvious learned closure is already ruled out

The relevant local evidence is unusually decisive.

| Fact already established locally | Consequence for M114 |
|---|---|
| A 32-channel, signed/absolute/squared gauge-normalized recurrence was cheap and symmetry-aware but missed the admission scale by about 120x. | Do not call another low-order transport state a new mechanism. |
| Its message-50 *target-informed per-network* oracle was still about 73x above the admission scale. | A fixed feature bank without the missing interaction statistic is dead before universal training is considered. |
| The first-layer Gram reached that state only through row summaries. | The full Gram must be an explicit edge graph, not more scalar row moments. |
| The missing object is signed cross-coordinate gate-boundary/intersection information. | The only economical new proxy is a sampled gate-intersection matrix at each layer. |
| Hermite association has depth-sensitive signal but no robust target-shape result; deterministic finite cumulant closures are unsupported. | Treat all learned corrections as biased regressors, never as analytic identities or control variates. |

The first-layer ReLU law does have exact Gaussian pair formulas; the
arc-cosine kernel is the appropriate source for that limited fact
([Cho and Saul, 2009](https://proceedings.neurips.cc/paper/2009/hash/5751ec3e9a4feab575962e78e006250d-Abstract.html)).
It does not make later layers Gaussian after a ReLU.  A finite particle/gate
state is therefore an approximation to the support-function recursion, not a
moment theorem.

## Candidate: CG-PSR

### 1. A deterministic, nested base estimator

Bias-free ReLU networks are positively homogeneous.  With `X=RU`, where
`U` is uniform on the unit sphere and independent of `R=||X||`,

\[
 m(W)=E[R]\,E_U[f_W(U)],\qquad
 E[R]=\sqrt{2}\,\frac{\Gamma((257)/2)}{\Gamma(128)}.
\]

Use a frozen, nested, antipodal spherical bank
`{(u_t,-u_t)}_{t=1}^{N/2}` that is generated independently of all MLP weights.
The concrete deployment candidate is `N=8,192` *actual forward directions*,
chosen as a nested prefix of complete randomly rotated/Kerdock-style bases
only if that exact construction is legal and reproducible in the eventual
runtime.  Otherwise use a predeclared independent Haar-orthobasis bank.  The
bank must be included or reproducibly generated from a fixed public seed; it
may not be tuned against benchmark networks.

\[
 B_N(W)=\frac{E[R]}{N}\sum_{t=1}^{N/2}
        \left(f_W(u_t)+f_W(-u_t)\right).
\]

`B_N` is an approximate quadrature for a fixed bank, not an exact conditional
expectation.  Antipodes remove the odd angular component exactly.  The nested
bank permits a fair paired comparison with a larger independent or extended
bank during generated-only training.

The learned model returns

\[
 \widehat m(W)=B_N(W)+\Delta_\theta(C(W),\mathcal P(W),B_N(W)).
\]

The residual target is the error of **this exact frozen bank**,
`m(W)-B_N(W)`.  Training a direct mean predictor and adding it to a short
sampler is forbidden by design: it destroys the causal interpretation and
makes it too easy to hide a bad direct predictor in a blend.

### 2. Canonical positive-gauge representative

Raw individual weights are not positive-gauge invariant.  Fix the gauge once
before the learned graph is built.  Let `a_lij=W_lij^2`; set boundary log
scales `u_0=u_L=0`; and minimize over interior node potentials

\[
 E(u;W)=\sum_{l=1}^{L}\sum_{i,j}a_{l,ij}
        \exp\{2(u_{l,i}-u_{l-1,j})\}. \tag{1}
\]

For dense iid-He matrices this strictly convex, boundary-anchored problem has
a unique minimizer.  Its stationarity condition is an interpretable balance:

\[
 \sum_j \bar W_{l,ij}^2 = \sum_k \bar W_{l+1,ki}^2,
 \quad 1\le l<L,
\]

where

\[
 \bar W_l=C_l(W)=\operatorname{diag}(e^{u_l})W_l
                    \operatorname{diag}(e^{-u_{l-1}}). \tag{2}
\]

If `W'` is gauge transformed with log scales `a_l`, then
`u(W')=u(W)-a` and hence `C(W')=C(W)`.  A hidden permutation simply permutes
the unique potential vector and the rows/columns of `C`.  Thus (2) converts a
gauge orbit into a permutation-equivariant canonical graph without choosing a
neuron order.

This is a **mathematical** normalization.  A production solver must be
charged, must report the balance residual, and must clear a transformed-input
equivariance test.  A fixed small number of iterations initialized at zero is
not enough to claim exact gauge invariance: it need not commute with an
arbitrary change of gauge.  Use a converged deterministic convex solver with
a frozen relative residual tolerance, or kill the candidate.  Zero rows have
probability zero under iid-He but must fail closed rather than receive an
unrecorded floor.

The rescaling symmetry itself is standard for ReLU networks; Path-SGD is a
primary reference for treating this geometry as an invariance rather than a
data-augmentation heuristic ([Neyshabur, Salakhutdinov, and Srebro,
2015](https://proceedings.neurips.cc/paper/2015/hash/eaa32c96f620053cf442ad32258076b9-Abstract.html)).

### 3. Exact feature graph

Use `J=64` designated antipodal paths from the `N`-direction base for the
learned state.  They are a fixed subset, not a learned selection.  All `N`
paths still contribute to `B_N`; only `J` are retained as particle evidence.
This prevents the gate graph from doubling the cost of the entire quadrature.

For every hidden layer `l` and unit `i`, create one node `v_(l,i)`.  There are
`31*256` hidden nodes plus 256 output nodes.  There are three kinds of edge.

| Edge | Attribute | Purpose |
|---|---|---|
| Directed inter-layer `(l-1,j)->(l,i)` | `bar W_lij` through `[w, w^2, w^3, abs(w)]` | signed transport and amplitude-aware path information. |
| First-layer pair `(1,i)<->(1,j)` | exact normalized Gram `rho_ij=(bar W_1 bar W_1^T)_ij/(sqrt(G_iiG_jj)+eps)` through `[rho,rho^2,rho^3]` | supplies the full input-induced correlation graph missing from the killed student. |
| Same-layer pair `(l,i)<->(l,j)` | sampled centered gate correlation `Q_lij=J^-1 sum_t g_lit g_ljt`, `g=1{z>0}-J^-1 sum_t 1{z>0}` | supplies observed two-gate intersections after each nonlinearity. |

The gate attribute is invariant to a positive rescaling of a preactivation and
permutation-covariant in its unit indices.  It is only a rank-`J` empirical
proxy for the actual gate law.  This is the entire high-upside hypothesis;
do not describe it as a recovered cumulant tensor.

For a linear final benchmark head, omit the final `Q_L` message (equivalently,
feed a fixed zero pair-message); for a final ReLU head, form it exactly as at
the hidden layers.  This is a head-interface choice, not a model-selection
knob.

At node `(l,i)`, retain the particle statistics

\[
 p_{l,i}=[\operatorname{mean}(h),\operatorname{mean}(h^2),
           \operatorname{mean}(h^3),\operatorname{mean}(h^4),
           \operatorname{mean}{\bf1}\{z>0\},
           \operatorname{mean}(|z|),\log(\operatorname{var}(h)+\epsilon)].
\]

They are computed on the canonical-weight particle forward.  Since canonical
and raw networks compute the same output function, using the canonical path
does not change `B_N`; it only makes internal features gauge invariant.

The following recurrence is the complete proposed learned feature graph.  It
is deliberately a tensorized message-passing operator, not per-edge MLP
attention over two million scalar edges.

```text
s_0,j = one shared learned constant for every input coordinate j       # 64 dims

for l = 1 ... L:
    directed_q[i,:] = sum_j psi_q(bar_W_l[i,j]) A_q s_(l-1,j)          q=1..4
    t_l,i            = MLP_in_shared([directed_1:4, p_l,i,
                                       broadcast(global_(l-1)), depth_embedding(l)])
    gate_q[i,:]      = sum_j chi_q(Q_l[i,j])      B_q t_l,j            q=1..3
    gram_q[i,:]      = sum_j chi_q(rho[i,j])      H_q t_1,j            l=1 only
    z_l              = induced-set-attention(global_(l-1), {t_l,i,gate_l,i,p_l,i})
    s_l,i            = MLP_out_shared([t_l,i, gate_1:3,
                                        gram_1:3 if l=1,
                                        broadcast(z_l), depth_embedding(l)])
end

delta_i = scale_i * head([s_L,i, normalized B_N,i, global_L])
mhat_i  = B_N,i + delta_i
```

Here `A_q`, `B_q`, and `H_q` project a 64-channel state to 12 channels before
the matrix contraction.  `psi=[w,w^2,w^3,|w|]`; `chi=[x,x^2,x^3]`; the MLP has
one 128-wide hidden layer; and induced set attention uses 16 global tokens of
width 64.  Parameters are shared across depths, with a 32-entry FiLM/depth
embedding.  `scale_i` is a predeclared, finite particle RMS scale with an
all-zero-output fallback.  It conditions the residual numerically; it is not
a claim of a new output-scale symmetry.

The recurrence has one forward algorithmic sweep along network depth.  It does
not use a 7,936-token full transformer, does not flatten the two million
weights, and does not assign an embedding to a hidden neuron identity.  Deep
Sets supplies the basic permutation-invariant/equivariant construction
([Zaheer et al., 2017](https://proceedings.neurips.cc/paper_files/paper/2017/file/f22e4747da1aa27e363d86d40ff442fe-Paper.pdf));
the induced-token component is the scalable interaction mechanism in the
[authors' Set Transformer implementation](https://github.com/juho-lee/set_transformer).
The matrix-contraction form is a dense, weighted instance of the message
passing template of [Gilmer et al., 2017](https://proceedings.mlr.press/v70/gilmer17a.html).
Those sources justify the symmetry-compatible building blocks, not the claim
that this recurrence learns the desired integral.

### 4. Symmetry proof sketch

1. Equation (2) is gauge invariant and hidden-permutation equivariant by
   uniqueness of the minimizer of (1).
2. The particle forward through `C(W)` has hidden activations merely relabeled
   under hidden permutations.  A positive gauge has already been removed;
   gate indicators are also unchanged by positive rescaling.
3. Each directed or pair message is a sum over the neighbor index with a
   shared map.  It therefore relabels its receiving node under a permutation.
4. Set-to-token attention is invariant to node order; token-to-set broadcast
   is equivariant.  Shared pointwise MLPs preserve that property.
5. The `B_N` forward is the original network function, so it is gauge
   invariant and output-permutation covariant.  The residual head and final
   addition preserve the same law.

The numerical audit must apply independent permutations at first, middle, and
last hidden layers and positive factors in `[2^-8,2^8]` at the same layers.
Report absolute and scale-aware errors separately; never let near-zero output
coordinates turn a relative division into a pass.

## Training and distillation plan

### Target construction

For a generated iid-He network `W`, form the frozen deployment base `B_N(W)`.
Independently estimate `m(W)` with two disjoint high-fidelity spherical banks
or two independent scrambled/rotated blocks, giving `Y_A,Y_B`.  The regression
label is

\[
 D(W)=\tfrac12(Y_A+Y_B)-B_N(W).
\]

The split discrepancy estimates teacher noise on a *whole network*, not on
the 256 correlated output coordinates.  It must be recorded and used to
inverse-variance weight the loss only after clipping weights by a predeclared
rule.  Never use the same particle directions to make both `B_N` and its
teacher label if claiming independent label-noise diagnostics.

Randomized QMC and antithetic constructions can reduce variance for suitable
integrands, but their favorable asymptotic claims rely on regularity that a
deep ReLU gate arrangement does not automatically satisfy.  Owen's
[local-antithetic RQMC paper](https://arxiv.org/abs/0811.0528) is a reason to
measure the gain, not a license to assume it here.

Use an output-equivariant residual loss, grouped by MLP rather than treating
outputs as independent draws:

\[
 \mathcal L=\frac1{|\mathcal B|}\sum_{W\in\mathcal B}
  \omega(W)\,\frac1{256}\sum_i
  \operatorname{Huber}_{\kappa}\left(
   \frac{B_{N,i}+\Delta_{\theta,i}-Y_i}{s_i+\epsilon}\right).
\]

`s_i` is a frozen robust scale from the independent teacher replicas.  A final
held-network metric is always unnormalized raw MSE and the official
cost-adjusted objective; the normalized Huber loss is only an optimization
device.  Train a direct residual head, a no-gate ablation, and a shuffled-label
negative control from the beginning.  A post-hoc blend coefficient is not
allowed.

### Multi-fidelity schedule, if and only if the falsifier passes

The only plausible CPU schedule is a curriculum with a small model
(roughly 0.5--1.5 million FP32 parameters), not a 10--12M-parameter graph
transformer.

| Tier | Generated networks | Direction count | Role |
|---|---:|---:|---|
| A | 10k--20k target-shape networks | `B_N` plus an independent 2,048-direction teacher | cheap residual pretraining; labels are noisy and downweighted. |
| B | 2k--4k target-shape networks | `B_N` plus two independent 32,768-direction teachers | main high-fidelity fine tune and noise calibration. |
| C | 512 new target-shape networks | `B_N` plus two independent 65,536-direction teachers | frozen validation/test, never revisited for training. |

Use network seeds, not output rows or QMC directions, as the split unit.  The
particle branch uses only `J=64` retained paths while the base is evaluated
once and stored as a 256-vector.  Recompute the small particle graph during
epochs from the generated seed; do **not** cache a huge bank of `256 x 256`
gate matrices or silently use a feature database that cannot be rebuilt.

Small-width/depth pretraining may help initialize the shared recurrence, but
it has no promotion value and cannot replace tier-B/C target-shape evidence:
the local signal is depth sensitive.

### Teacher-noise and sample-complexity reality

There is no honest fixed sample count until the target-shape output variance
is measured.  For a scalar path variance `v_i(W)`, a genuinely independent
mean teacher with `S` paths has conditional variance about `v_i(W)/S` before
any QMC gain.  The necessary condition for distinguishing a desired MSE
improvement `g` is

\[
 E_W\!\left[\tfrac1{256}\sum_i v_i(W)/S\right] \le 0.1g. \tag{3}
\]

The `0.1` is a frozen label-noise reserve, not a theorem.  If the two teacher
replicas violate (3), increase teacher paths or kill the learned screen;
training on a noisier label cannot establish the requested residual reduction.
For a paired, whole-network score difference `d(W)`, a 95% normal planning
approximation requires

\[
 N_{net}\gtrsim \left(1.96\,s_d/g\right)^2. \tag{4}
\]

where `s_d` is estimated only in the pilot.  The 256 output coordinates do
not multiply `N_net` in (4), because they share a network, a teacher bank, and
large common gate fluctuations.

The arithmetic is marginal but not fantastical; the data discipline is the
larger obstacle.  A 256-by-256, 32-matrix forward costs roughly
`2*32*256^2 = 4.19M` floating operations per input direction before framework
overhead.  Thus a 32,768-direction teacher costs about 137 GFLOP per network.
Four thousand such teacher networks cost roughly 550 TFLOP for one replica,
before the deployment-base passes, a second replica, balancing, or training.
The tiers above are therefore of order **1--3 PFLOP** of dense CPU work.
On eight physical CPU cores, a sustained 30--100 GFLOP/s end-to-end rate puts
the ideal dense-matmul time near 3--28 hours; Python dispatch, small-matrix
efficiency, teacher duplication, and failed/restarted jobs can readily make it
two to four days.  This consumes essentially all of the stated window and
still does not buy a theorem of generalization.

For the learned training pass, `J=64` particles cost only about 268 MFLOP per
network forward, but replaying 20k networks for 20 epochs is still about
107 TFLOP before backward and graph contractions.  Keep the model small and
the epoch budget frozen.  A claim that 50 MiB of weights is the bottleneck is
incorrect: teacher generation and repeated feature construction are.

## Inference, artifact, and compute envelope

The numbers below are **shape lower bounds**, not a FlopScope accounting
certificate.  Any implementation must be re-billed through the benchmark's
instrumented path; compilation may be useful for an offline prototype but may
not hide counted arithmetic.  The current PyTorch documentation describes
`torch.compile`/Inductor as a performance facility, not a replacement for an
external arithmetic ledger ([PyTorch documentation](https://docs.pytorch.org/docs/stable/generated/torch.compile.html)).

For `N=8,192` total base directions and `J=64` particle directions:

| Component | Approximate FLOP lower bound | Comment |
|---|---:|---|
| `B_N` MLP forwards | 34.36B | `2*N*L*256^2`; dominates. |
| Canonical gauge solve | 0.1--1B | iteration count and `exp` treatment must be measured; do not undercharge it. |
| First Gram and `J` gate correlations | <0.35B | dense products at 256 width, if only the retained paths are used. |
| Four directed and three pair contractions | <0.5B | with 12 projected channels; charge all `W^2`, `W^3`, and absolute transforms. |
| Tokens, MLPs, head, storage movement | <0.2B arithmetic, unknown residual | must be measured, not presumed free. |
| **Planning total** | **<37B plus measured residual** | leaves a wide margin under 272B, but is not in the 0.1-floor regime. |

This cost is about one fifth of the current 190B effective-cost champion, so
a score win requires a real variance-per-cost improvement, not merely the
usual `MSE proportional to 1/N` sampling trade.  If the base is a simple
subsample of the champion's design, its first-order raw-MSE increase is nearly
the reciprocal cost reduction and is score-neutral.  The residual must remove
the extra quadrature error; that is the one hypothesis being tested.

A conservative artifact allocation is:

| Item | Cap |
|---|---:|
| Shared CG-PSR FP32 parameters, including tokens/depth FiLM | 6 MiB |
| Frozen particle/QMC direction seeds or FP32 bank | 4.1 MiB for 4,096 stored positive directions; less if reproducibly generated |
| Model metadata, checksum, architecture/config | <1 MiB |
| Package/source/serialization reserve | 15 MiB |
| **Hard package target** | **<30 MiB; reject at 45 MiB** |

Keeping the learned state far below 50 MiB is intentional.  FP16/int8 should
not be justified as a billed-FLOP saving when the benchmark charges arithmetic
by operation rather than dtype; use a numerically stable format and prove
parity instead.

## Frozen small falsifier

This is the only experiment this note recommends.  It must be frozen before
any generated target-shape forward and must not open contest material.

### Fixed configuration

```text
network law:      iid He, width 256, depth 32, bias-free, exact target head
base:             fixed antipodal spherical bank, N=8,192 executed directions
particle subset:  J=64, fixed indices of that bank
model:            the CG-PSR graph above, 64 node channels, 12 projections,
                  16 global tokens, <=1.5M FP32 parameters
training seeds:   0..383 (384 whole networks)
validation seeds: 384..447 (64 whole networks)
test seeds:       448..511 (64 whole networks, read once)
teacher:          two independent 32,768-direction banks per network
optimizer:        AdamW, fixed one-cycle schedule, 12 epochs, no sweep
comparison:       B_N; no-gate CG-PSR ablation; shuffled-residual control
```

All QMC bank seeds, iid-He seeds, code hashes, package versions, direction
ordering, balance tolerance, scale fallback, stopping rules, and decision
thresholds must be written to a manifest before teacher generation.  The
teacher replicas are averaged only after their split discrepancy has been
saved.

### Static tests before a single target forward

1. Exact algebra tests for (1)--(2): stationarity, uniqueness failure on a
   deliberately zero row, and canonical equality after random positive gauges.
2. Independent hidden permutations at layers 1, 16, and 31; output permutation
   covariance; and positive gauges at the same layers.  Require an agreed
   mixed absolute/relative error below `1e-5` in FP32 and a float64 shadow
   agreement below `1e-8` on small synthetic shapes.
3. QMC-bank antipodal pairing, unit norms, seed reconstruction, no duplicate
   direction, and no train/teacher bank overlap.
4. Shape ledger including canonicalization, powers/absolute values, gate Gram,
   all contractions, particle forward, residual time, and peak memory.
   Refuse to run if the conservative maximum cannot remain below 80B and the
   hard 272B cap.
5. Artifact dry serialization under 45 MiB with no generated weights, labels,
   outputs, or benchmark identifier inside it.

### Promotion and kill rules

Let `R = MSE_test(CG-PSR)/MSE_test(B_N)`, calculated per network then reported
with a 10,000-resample whole-network bootstrap.  Let `R_no_gate` be the same
ratio for the ablation that deletes all `Q_l` pair messages but preserves base,
Gram, cost class, and parameter budget.

**Kill permanently** if any static/resource/symmetry test fails, label-noise
MSE exceeds 10% of the observed candidate-vs-base improvement, the shuffled
control improves, `upper95(R) >= 0.85`, or
`upper95(R/R_no_gate) >= 0.90`.  The last two conditions respectively demand a
large held effect and evidence that sampled gate pairs, not generic capacity,
caused it.  A result in the gap is *ambiguous and retired*; it does not license
a second seed or hyperparameter sweep.

**Advance once** only if all tests pass, `upper95(R) < 0.70`,
`upper95(R/R_no_gate) < 0.85`, every test network is non-worse on the
cost-adjusted objective after measured billing, and the independent teacher
split supports the label-noise reserve.  This is deliberately much stronger
than the roughly few-percent reduction that might repay 37B versus the
existing sampler.  A small effect cannot justify spending the remaining days
on a highly correlated high-fidelity data set.

The initial 64-network test is underpowered for a final score claim.  A pass
only authorizes the tier-B/C generated schedule and, later, the firewall's
separate predeclared development/selection process.  It authorizes neither a
submission mutation nor a public-label fit.

## What would falsify the central mechanism

| Observation | Conclusion | Action |
|---|---|---|
| Canonical gauge residual or transformed prediction fails | implementation cannot honestly claim the required symmetry | kill; do not weaken the metric. |
| Full CG-PSR helps but the no-gate ablation matches it | capacity/Gram/statistics, not deep gate intersections, produced the result | kill this mechanism; no attention retune. |
| Per-network training fits but held networks do not | residual is QMC-bank/weight-instance memorization | kill; more generated seeds are not a rescue without a new representation theorem. |
| `B_N` is already score-neutral under measured billing and correction is small | ordinary sampling law dominates | return to exact sampler compression. |
| Teacher split noise is comparable to the desired gain | evidence cannot discriminate the hypothesis | increase teacher accuracy only if the predeclared cost still fits; otherwise kill. |
| Gate branch shows a large held effect and survives every symmetry/label check | the missing representation may be real | proceed once to the full external-data schedule. |

## Literature and repository record

The following are sources for the ingredients, not endorsements of a claimed
solution.

1. [Zaheer et al., *Deep Sets*, NeurIPS 2017](https://proceedings.neurips.cc/paper_files/paper/2017/file/f22e4747da1aa27e363d86d40ff442fe-Paper.pdf): characterization motivating shared maps plus symmetric aggregation.
2. [Lee et al., *Set Transformer*, ICML 2019](https://proceedings.mlr.press/v97/lee19d.html) and the [authors' official repository](https://github.com/juho-lee/set_transformer): inducing attention for set interactions without full quadratic self-attention.
3. [Gilmer et al., *Neural Message Passing for Quantum Chemistry*, ICML 2017](https://proceedings.mlr.press/v70/gilmer17a.html): message/update/readout decomposition for permutation-respecting graph computation.
4. [Neyshabur, Salakhutdinov, and Srebro, *Path-SGD*, NeurIPS 2015](https://proceedings.neurips.cc/paper/2015/hash/eaa32c96f620053cf442ad32258076b9-Abstract.html): positive rescaling is a genuine ReLU-network symmetry.
5. [Cho and Saul, *Kernel Methods for Deep Learning*, NeurIPS 2009](https://proceedings.neurips.cc/paper/2009/hash/5751ec3e9a4feab575962e78e006250d-Abstract.html): exact one-layer ReLU/arc-cosine Gaussian pair structure; it does not close a finite fixed network after many ReLUs.
6. [Owen, *Local antithetic sampling with scrambled nets*](https://arxiv.org/abs/0811.0528): motivation for measuring, rather than assuming, randomized-QMC/antithetic benefit on a nonsmooth high-dimensional integrand.
7. [Google DeepMind CLRS repository](https://github.com/google-deepmind/clrs) and [Velickovic and Blundell's neural algorithmic reasoning article](https://arxiv.org/abs/2105.02761): rationale for a tied algorithmic recurrence rather than a flattened weight regressor.  They supply no evidence that this specific support-function algorithm is learnable.
8. [PyTorch `torch.compile` documentation](https://docs.pytorch.org/docs/stable/generated/torch.compile.html): current implementation reference only; benchmark accounting must remain independently auditable.

## Final disposition

CG-PSR is the **highest-upside lawful amortized design that is not merely the
already-killed low-order student**.  Its full-Gram plus actual gate-pair state
is the smallest identifiable change that targets the localized missing
information.  It can be permutation-equivariant, positive-ReLU-gauge
invariant/covariant, under 50 MiB, and plausibly around 37B planning FLOP at
inference.

It is nevertheless a **distraction as a full project today**.  A finite bank
of 64 particle gates has no closure theorem, the earlier learned ceiling is
hostile, and a credible target-shape teacher/data program consumes most of the
remaining CPU window.  The correct allocation is one precommitted falsifier
with the severe `R<0.70` and gate-ablation requirements above.  Without that
result, retain the exact sampler/compression path and do not manufacture a
new neural-algorithmic branch from architecture vocabulary alone.
