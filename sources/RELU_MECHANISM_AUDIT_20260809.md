# ReLU mechanism audit for WHestBench

Date: 2026-08-09
Scope: source-driven, response-free audit. No contest instance, truth, scorer,
leaderboard, submission, or champion artifact was read or changed.

## Question

Do the six supplied papers add a new observable, exact identity, lawful control
mean, or arithmetic circuit for estimating the mean of a **fixed**, bias-free,
32-layer ReLU network? Training improvements and model replacement do not count
as estimator information.

## 1. DPReLU and its initialization

Source: Yang et al., *DPReLU: Dynamic Parametric Rectified Linear Unit and Its
Proper Weight Initialization Method* (2023), DOI
`10.1007/s44196-023-00186-w`.

The proposed activation is

```text
g(x) = beta (x-threshold) + bias,  x >= threshold
       alpha(x-threshold) + bias,  x <  threshold.
```

Under independent symmetric zero-mean weights/inputs and with threshold and
bias set to zero, the paper derives

```text
Var(W_l) = 4 / ((n_in+n_out)(alpha^2+beta^2)).
```

WHestBench consequence: the target is already fixed at the special case
`alpha=0, beta=1, threshold=bias=0`, with immutable He weights. Training the
four parameters or reinitializing weights changes the target. Used only as a
surrogate, its two linear branches live inside the already-audited
PReLU/second-moment-closure family and supply no exact mean for the target
residual. The paper preserves a useful diagnostic---effective slopes and active
fractions---but that diagnostic is already represented by gate occupancy and
full-covariance state. No candidate is opened.

Reopening condition: derive an exact, billed, weights-only expectation of a
nonconstant target-minus-DPReLU residual, not fitted activation parameters.

## 2. Review of ReLU-derived activations

Source: Bai, *RELU-Function and Derived Function Review* (2022), DOI
`10.1051/shsconf/202214402006`.

This is a training-oriented review and small MNIST comparison of ReLU, leaky
ReLU, PReLU/RReLU, SELU, GELU, and SignReLU. It gives no deep fixed-network
integration identity. Its experimental ranking is architecture/training
specific and is not evidence about estimator variance.

The one structurally different atom is SignReLU, reviewed as

```text
g_a(x) = x,                 x >= 0
         a*x/(abs(x)+1),    x < 0.
```

The negative softsign branch is bounded but destroys positive homogeneity, so
it forfeits WHestBench's exact radial reduction. Its deep expectation is not
known analytically, so a SignReLU control would inherit the approximate-mean
barrier. Boundedness alone is not a control variate.

Reopening condition: an exact conditional mean for a nonconstant SignReLU
residual whose covariance survives the 5-design, plus inclusive cost below the
matched direct estimator. Merely swapping the activation is invalid.

## 3. Original SignReLU paper

Source: Lin and Shen, *Research on convolutional neural network based on
improved Relu piecewise activation function* (2018), DOI
`10.1016/j.procs.2018.04.239`.

The paper trains a modified CNN on CIFAR-10 and reports convergence and
classification effects. It does not estimate the Gaussian input integral of an
unchanged ReLU network. The mechanism is therefore model replacement, not a
new WHestBench information source. It is subsumed by the activation-surrogate
analysis above.

## 4. Data-dependent ReLU/output initialization

Source: Aguirre and Fuentes, *Improving Weight Initialization of ReLU and
Output Layers* (2019), DOI `10.1007/978-3-030-30484-3_15`.

The method performs an initialization-set pass, orthogonalizes each layer,
sets the bias of neuron `j` from the `(1-f)` order statistic of its pre-ReLU
samples to enforce active fraction `f`, rescales to a desired variance, and
sets the output matrix by least squares:

```text
b_j = -order_statistic_(floor((1-f)n))(H[:,j])
W_out = pinv(H_last) Y.
```

For WHestBench, orthogonalization, bias insertion, and rescaling change the
given weights/network. The output pseudoinverse additionally requires labelled
targets `Y`; no such training target exists in the challenge. The lawful tissue
is narrower: orthogonal frames and active-fraction diagnostics. Both are
already represented in the Kerdock/frame and gate-occupancy branches. The
paper does not reopen output-row regression, because its pseudoinverse is
supervised rather than a target-free identity.

Reopening condition: an unbiased active-fraction stratification rule with a
known inclusion probability and a strict matched-cost variance proof. It may
allocate samples; it may not edit weights or learn from truth.

## 5. ReLU for inference acceleration

Source: Patel, Goel, and Shai, *ReLU for Inference Acceleration* (withdrawn
ICLR 2024 submission), OpenReview `9ydLP7como`.

The paper replaces smooth activations with ReLU during inference and uses
knowledge-distillation training to limit accuracy loss. Its signal is a
model/hardware trade, not an integral identity. WHestBench already uses ReLU;
retraining or substituting an activation changes the target, and the contest
cost model bills primitive array operations rather than the paper's proposed
accelerator. The only preserved tissue is the general value of exact operation
fusion, already covered more strongly by the WHT/Winograd/call-fusion work.

Reopening condition: an arithmetic-identical lowering under FlopScope with a
measured inclusive bill and parity. Distillation is not admissible evidence.

## 6. Weight precision versus neuron count

Source: He and Papakonstantinou, *The Effect of Weight Precision on the Neuron
Count in Deep ReLU Networks* (ICML 2024), PMLR 235:18010--18018.

The paper separates three resources: neuron count, weight precision, and the
time used to construct a network description. Exponential preprocessing can
pack Boolean computation into fewer ReLU nodes by paying in precision; when
precision is charged in network size, or the description is generated in
polynomial time, the apparent free compression disappears.

WHestBench consequence: this is a useful **anti-shortcut boundary** for ideas
that propose packing the 32-layer computation into huge constants, flash
embeddings, or unbilled high-precision weights. It does not prohibit exact
factorization of the given fixed matrices, structured WHT/Strassen circuits,
or estimator-specific algebra; those must still pay their actual construction,
precision, and primitive-operation bill. The paper supplies no estimator
observable and opens no score candidate.

## Consolidated disposition

| source mechanism | new target information? | lawful tissue | disposition |
|---|---:|---|---|
| DPReLU / initialization | no | slope and active-fraction diagnostics | contained by closure/gate-state work |
| activation review | no | catalogue of surrogate atoms | research context only |
| SignReLU | no | bounded negative branch | blocked on exact mean and lost homogeneity |
| data-dependent initialization | no | orthogonal frame and activity stratification ideas | model editing/label dependence excluded |
| inference ReLU substitution | no | exact fusion motivation | contained by engineering ladder |
| precision-for-neurons | no | resource-accounting no-free-lunch | new adversarial kill boundary, not estimator |

None of the six sources changes the live mathematical bottleneck. M198 screens
the lawful owner-labelled `Source211 -> TangentState` delay-one map, M200
passes a generated one-stream M179/M198/M125b layer-binding fixture, and M205
proves a structured rank-one physical-owner control algebra. The first missing
information-changing link is therefore a layer-bound provider for physical
`K4`, directed `K31`, symmetric `K22`, and distinct `C211`, followed by a
complete caller-replacement/native trace. The
sources sharpen what **cannot** be claimed: training gains, alternate
activations, supervised pseudoinverses, hardware-only speedups, and precision
packing do not become fixed-network integration gains.
