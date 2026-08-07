# M136 diagram transformer clean-room audit — 2026-08-07

## Verdict

**Killed implementation; preserve the architecture components.** Do not attach
M136-R to the champion, package it for target inference, or treat it as a
submission candidate.

M136-R changes the failed H1 mechanism by compiling the difficult diagrams
explicitly instead of asking a generic weight-space encoder to discover them.
It passes exact hidden-permutation/positive-ReLU-gauge tests and exactly fits a
generated target containing `ABAB`, `ABBA`, `[2,1,1]`, and a delayed response.
Its matched low-order message baseline cannot fit that target.  Yet its
fresh-network result fails the predeclared promotion gate:

```text
anchor MSE                0.0189804973
M136-R MSE                0.0129609711
M136-R / anchor           0.682857
network-bootstrap 95% CI  [0.423198, 0.994847]
required upper endpoint   < 0.500000
```

The point estimate does not reach the requested twofold reduction, and its
confidence upper endpoint is far above it.  The six-channel head is worse
than its matched star-only model (`0.68286` versus `0.50513`).  Retrying with
more width, epochs, data, or a searched feature pool would be forbidden
parameter drift, not a changed causal mechanism.

No contest/public/private model, scorer, leaderboard, submission, or champion
artifact was read by this module or its data generator.  The frozen champion
is unchanged.

## Invariants

| item | M136 declaration |
|---|---|
| objective | Predict only the residual of a fixed diagonal Gaussian anchor for a fresh iid-He ReLU MLP. |
| bias class | Deliberately biased learned correction; never eligible without an independent held-network proof. |
| development | 24 complete fresh networks, seeds `136000..136023`. |
| untouched holdout | 16 complete fresh networks, seeds `137000..137015`; their outcome cannot affect training. |
| teachers | Two independent Gaussian MC streams of 32,768 inputs per network. |
| target worksheet | `n=256`, `L=32`, f32, 24 square-equivalent calls/source layer, 1.25 protection, 2B non-matmul reserve. |
| possible package | Static coefficients and source only; teacher samples, synthetic corpus, fitted labels, and all challenge artifacts are excluded. |

The supplied organizer interpretation permits offline external-MC training for
this branch.  It does not waive the normal package rule check, and cannot
rescue a failed efficacy gate.

## Architecture

M136-A is a compact **diagram-attention neural functional** for chains of
dense ReLU matrices.  It ingests signed dense weights and analytic Gaussian
states; it uses no Gemma or other language-model weights.  The executed M136-R
is the strict low-parameter face of M136-A: it fixes its edge-attention
projections and learns only causal residual coefficients.  The negative result
therefore kills M136-R, not all neural functionals.

### Exact quotient by hidden permutations and positive gauges

For hidden permutations `P_l` and positive diagonal ReLU gauges `D_l`, an MLP
has the same function under

```text
W_l' = D_l P_l W_l P_(l-1)^T D_(l-1)^(-1).
```

Let `r_(l-1)=sqrt(E[h_(l-1)^2])`, and `s_l` be the analytic preactivation
standard deviation.  M136 canonicalizes each signed edge matrix as

```text
Wbar_l = diag(s_l)^(-1) W_l diag(r_(l-1)).
```

It also supplies `alpha_l=mu_l/s_l` and correlation `R_l`.  Then

```text
Wbar_l' = P_l Wbar_l P_(l-1)^T
alpha_l' = P_l alpha_l
R_l' = P_l R_l P_l^T.
```

Hence every internal feature is gauge invariant and permutation equivariant.
The physical final scale appears once only:

```text
estimate = diagonal_Gaussian_anchor + s_L * dimensionless_residual.
```

The executable tests apply independent random hidden permutations and positive
scales at every layer, including output scaling.  They verify the anchor,
features, fitted prediction, and edge-attention primitive to numerical
tolerance.

### Signed bipartite edge attention

For source token `h_j`, destination token `g_i`, and normalized signed edge
`w_ij`, the retained operator is

```text
a_ij = softmax_j(g_i dot h_j / sqrt(d) + 0.5 log(1 + |w_ij|))
message_i = [sum_j a_ij h_j,
             sum_j a_ij w_ij h_j,
             sum_j a_ij w_ij^2 h_j].
```

The first channel is content/magnitude attention; the latter two preserve
signed and even edge information without mistaking a negative MLP weight for
a probability.  Tests use analytic node tokens
`(alpha, phi(alpha), -alpha phi(alpha))` and prove covariance exactly.
M136-R leaves the channel maps fixed.

### Explicit M126/M131 diagram channels

For one source layer let `E=R-I`, `V` be normalized downstream transport,
`g2=phi(alpha)`, and `g3=-alpha phi(alpha)`.  M136 exposes:

```text
star      = V^T [g3_i sum_j E_ij^2]
B2        = diag(g2) V                 B3 = diag(g3) V
ABAB      = diag(B2^T E B2)
ABBA      = diag(B2^T E B3)
q211_i    = (sum_j E_ij)^2 + 2 [E(E 1)]_i - 3 sum_j E_ij^2
collision = V^T [g2_i^2 q211_i]
delay     = (B2^T E B2) star.
```

`q211` is exactly the hollow three-vertex contraction

```text
sum_(j,k distinct and both != i) [Eij Eik + Eij Ejk + Eik Ejk].
```

These are representation channels, **not** a claim that their current
coefficients are exact fixed-network cumulants.  M136 does not erase the
M126/M131 source obstructions.  It names their graph shapes and asks whether a
fresh held-network test supports a learned residual map.  A three-basis causal
lag head `(1, lag, lag^2)` gives six times three coefficients plus intercept:
19 fitted values at tested depth four and target depth 32.

## Exact synthetic test and active nulls

The synthetic representation test draws fresh hollow symmetric graphs and
uses the fixed target

```text
0.7 star - 0.5 ABAB + 0.35 ABBA + 0.9 collision_211 - 0.2 delay.
```

The full compiler/head fits it below `1e-20` MSE.  A matched star-only
low-order message baseline remains above `1e-7`.  This proves representational
sufficiency for the stated polynomial only; it is not ReLU accuracy evidence.

| holdout model | ratio to anchor | 95% network-bootstrap CI | disposition |
|---|---:|---:|---|
| M136-R, all diagrams plus edge attention | 0.68286 | [0.42320, 0.99485] | killed: upper CI > 0.5 |
| matched low-order star | 0.50513 | [0.34013, 0.66496] | does not clear gate |
| network-group shuffled labels | 0.92319 | [0.60321, 1.50599] | active null rejected |

The maximum independent-stream teacher discrepancy is `z=2.773`, below the
predeclared `6` sanity bound.  Mean merged teacher SE is `0.001777`, far below
the anchor RMSE `sqrt(0.01898)`.  This is not an accidental shared-RNG or
teacher-noise result.

The parent falsifiers remain binding: H1's graph out-of-fold `R^2=.6627` was
far below the roughly `.965` correlation required by its attachment; M106's
treatment/null validation ratio `.949` crossed one and its absolute correction
failed.  M136-R changes representation by explicit motifs, but it fails its
own independent gate and cannot be repaired by tuning.

## Target inference/package worksheet — not deployment-certified

There is no target executable because M136-R failed.  This is a conservative
call-schedule worksheet to falsify cost, not an accounting certificate.

At width 256, one f32 square dense product bills `33,488,896` FLOPs.  Reserve
24 square-equivalent calls for each of 31 source layers: downstream transport,
two signed edge-attention banks, ABAB/ABBA pair channels, `[2,1,1]` graph and
transport channels, delayed response, and structured residual allowance.

| mode | raw dense bill | 1.25x protected + 2B reserve | below 80B? |
|---|---:|---:|---|
| f32 | 24.915739B | 33.144673B | yes |
| f64-rate (2x) | 49.831477B | 66.289347B | yes |

This is conditional on a later `flopscope` call trace realizing the 24-call
cap, no dense pair/triple tensors, an independent f32 parity test, and an
official-runner allocation/wall audit.  M126/M131 cost warnings therefore
still bind.  Neither the worksheet nor the 19-float possible package is
authorized for deployment.

## Research basis and salvage

The architecture borrows ordinary attention/symmetry mathematics—not language
model weights—from [Vaswani et al.](https://arxiv.org/abs/1706.03762),
[Pan and Kondor](https://proceedings.mlr.press/v151/pan22a.html), and
[Kofinas et al.](https://arxiv.org/abs/2403.12143).  The closest current
weight-space work, [Vo et al.](https://proceedings.mlr.press/v267/vo25b.html),
also identifies simultaneous permutation/scaling equivariance, expressivity,
and low cost as a hard trade-off.  These primary sources motivate an inductive
bias; none is evidence for an analytic cumulant shortcut.

Preserve:

1. gauge canonicalization by analytic scales;
2. signed bipartite edge attention;
3. exact hollow `q211` ownership;
4. motif representability and symmetry tests; and
5. network-grouped teachers, shuffled-label null, and bootstrap gate.

The failed link is the learned map from these channels to the fixed-network
residual.  Reopen only with a new observable or exact conditional/resummation
identity addressing that link; capacity, data, epoch, or coefficient searches
are not legitimate reopeners.

## Reproduction

```powershell
$py='C:\Users\strid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
Push-Location work\scorefloor_generation\m136_diagram_transformer
& $py -m unittest -v test_m136_diagram_transformer.py
Pop-Location
& $py work\scorefloor_generation\m136_diagram_transformer\m136_diagram_transformer.py
```

The module writes the frozen generated-only results to
`M136_RESULTS_20260807.json`.
