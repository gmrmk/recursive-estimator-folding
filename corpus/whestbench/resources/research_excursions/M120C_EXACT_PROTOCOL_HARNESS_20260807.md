# M120C exact-protocol harness: frozen, target-free, pre-execution only

**Status: `PASS_TO_INDEPENDENT_PREEXEC`.**  The source/configuration/tests are
frozen and their manifest verifies.  This status permits only an independent
pre-execution review of the protocol.  It is **not** an empirical pass: the
27-network binding grid has not been run, no binding output exists, and this
artifact supplies no correction, source, score, or target-shaped result.

## Firewall and scope

M120C is a falsifier for the corrected M120 shared-CP approximation to the
Gaussian `(mu,C)` reverse recurrence.  It uses generated fixed-width ReLU
networks and all terminal outputs only.  The following work is absent by
construction:

- correction oracle or weights-only feedback source;
- `LLQ`, `LLLC`, `LLQQ`, or terminal-Born source ownership/composition;
- public or contest outcomes, targets, scorer, or champion access;
- target-shape efficacy, correction, or full-network experiment.

The prior M120B small-width runner is deprecated and inert.  Its historical
exploratory result is not part of this protocol and cannot be substituted for
the binding grid below.

## Frozen binding plan

The configuration is
[`m120c_protocol_config.py`](../m120_price_normal_ordered_adjoint/m120c_protocol_config.py),
and its hash is bound by
[`m120c_protocol_manifest.json`](../m120_price_normal_ordered_adjoint/m120c_protocol_manifest.json).

| setting | frozen value |
|---|---|
| widths | `{8, 12, 16}` |
| depths (including final affine) | `{2, 3, 4}` |
| networks per `(width,depth)` cell | exactly `3` |
| binding total | exactly `27` generated networks |
| terminal outputs | every output `0,...,width-1` |
| network generator | `numpy.random.Philox` |
| metric directions | four signed, independent `Philox` directions per `(width, depth, hidden layer)` |
| global mean gate | `<= .05` |
| per-cell worst-output gate | `<= .10` |
| variance/norm fail-closed floor | `1e-10` |

The nine triples of numeric network seeds are written prospectively in the
config under the documented `M120C-NET-v1` namespace.  The direction namespace
is `M120C-DIR-v1`, starts from an unrelated root seed, and contains no output,
replica, result, or retry index.  Thus directions cannot be selected from any
observed output error.

The only eventual output path is fixed in advance as
`work/scorefloor_generation/m120_price_normal_ordered_adjoint/out/m120c_binding_result.json`.
There is no result at that path.  This is a **freeze-ready inert** runner, not
a one-shot runner: it makes no atomic/no-retry claim and exposes no CLI grid
execution until a separately reviewed authorization/manifest process exists.

## Gauge-invariant complete-adjoint metric

At every hidden-ReLU input-facing preactivation layer `ell` and every terminal
output `o`, let `b_(ell,o)` be the mean adjoint, `A_(ell,o)` the symmetric
central-covariance adjoint, and

\[
D_\ell=\operatorname{diag}\sqrt{\operatorname{diag}(C_\ell)}.
\]

The harness explicitly standardizes the **complete** adjoint as

\[
s_{\ell,o}=(D_\ell b_{\ell,o},\;D_\ell A_{\ell,o}D_\ell),
\qquad
\lVert s_{\ell,o}\rVert_\star=
\sqrt{\lVert D_\ell b_{\ell,o}\rVert_2^2+
\lVert D_\ell A_{\ell,o}D_\ell\rVert_F^2}.
\]

For a full dense reverse reference `s` and the M120 shared-CP base `s_hat`,
the scalar primary error is

\[
e_{\ell,o}=
\frac{\lVert s_{\ell,o}-\widehat s_{\ell,o}\rVert_\star}
{\lVert s_{\ell,o}\rVert_\star}.
\]

This is not an unstandardized covariance-only proxy.  A zero or near-zero
variance, or a reference complete norm at or below `1e-10`, is a protocol
failure: no epsilon, clipping, denominator replacement, or omitted-output
fallback is allowed.

For each cell, the binding analysis must report all values and enforce

\[
\operatorname{mean}_{\text{all cells, networks, layers, outputs}}e\le .05,
\qquad
\max_{\text{networks, layers, outputs in every cell}} e\le .10.
\]

## Predeclared signed directional contractions

Each independent Philox direction is a fixed unit pair
`q=(q_b,Q_A)` in the same standardized product space.  It is signed and
outcome-free.  The harness records

\[
d_{\ell,o,q}=
\frac{\langle q_b,D_\ell(\widehat b-b)\rangle+
\langle Q_A,D_\ell(\widehat A-A)D_\ell\rangle}
{\lVert s_{\ell,o}\rVert_\star}.
\]

The signed values must be retained; their absolute values are gated with the
**same** aggregation limits: global mean absolute directional contraction at
most `.05`, and each cell's maximum over outputs, networks, layers, and
directions at most `.10`.  No direction is normalized by a selected output or
chosen after seeing a residual.

`evaluate_predeclared_gates` encodes this aggregation before execution.  It
requires exactly one record for every `(width, depth, replica, input-facing
layer, output)` key: `648` records total.  Missing, duplicate, non-finite, or
out-of-grid records fail closed; neither an output nor a direction can be
dropped from an unfavorable cell.

## Simultaneous representation tests

For every hidden layer, M120C applies a positive gauge and a permutation
simultaneously,

\[
T_\ell=P_\ell\operatorname{diag}(g_\ell),\quad g_\ell>0,
\]

with input-output weights transformed by

\[
W_0'=W_0T_0,\quad
W_\ell'=T_{\ell-1}^{-1}W_\ell T_\ell,\quad
W_{\rm final}'=T_{L-1}^{-1}W_{\rm final}.
\]

The terminal preactivation remains invariant.  At each transformed
input-facing layer, the standard state transforms only by its permutation:

\[
D' b'=P^T(Db),\qquad D'A'D'=P^T(DAD)P.
\]

Directions are transported as `q_b'=P^T q_b`, `Q_A'=P^T Q_A P`; their signed
contractions and the complete normalized error must therefore agree to
`1e-10`.  Unit tests cover an entire four-map ReLU chain with simultaneous
hidden transforms, as well as the standardized covariance-adjoint relation.

## Hash binding and inert execution state

The manifest binds SHA-256 hashes for the config, M120C harness, named inert
runner, deprecated old entry point, test, corrected CP implementation, and
the two existing Gaussian-background dependencies.  Its verifier performs
only local file reads and hashes; it samples no network.

The operational entry point,
[`run_m120c_protocol.py`](../m120_price_normal_ordered_adjoint/run_m120c_protocol.py),
returns manifest-verified plan metadata when imported and exits without
execution when invoked as a CLI.  The deprecated
[`run_corrected_cp_generated.py`](../m120_price_normal_ordered_adjoint/run_corrected_cp_generated.py)
is also inert.

The target-free tests in
[`test_m120c_protocol.py`](../m120_price_normal_ordered_adjoint/test_m120c_protocol.py)
pass eight checks: exact frozen grid/seeds, complete standardized gauge and
permutation invariance, zero/near-zero fail-closed behavior at `1e-10`,
independent Philox direction determinism, manifest binding, inert named-runner
metadata, manifest grid/gate drift rejection, complete all-record gate
aggregation, and simultaneous all-hidden ReLU reparameterization.  These are
source tests only; they do not execute any binding network.

## Required next state

An independent reviewer may now audit the manifest, firewall, metric
definition, and fail-closed conditions.  No one may label M120C `AUDIT` or
`KILL` from this pre-execution artifact, and no correction work may begin.
Any later authorized binding run must retain the frozen hashes, all 27 jobs,
all terminal outputs, fixed output path, signed directional ledger, and the
same `.05/.10` gates.
