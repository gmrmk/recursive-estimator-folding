# Codex sealed proposal AJ1 v2: cross-fitted residual reflection coupling

Canonicalization: UTF-8, no BOM, LF line endings, one final newline.

Status: proposal bytes only. This file grants no scientific execution,
implementation, package, upload, scorer, truth, holdout, or submission authority.

This v2 is a prospective repair of private v1 SHA-256
`E8431D0656A072FE6F3A6744481EB96CFCFF20CB0F4E8A7DF114269CEAAA74C6`.
The v1 bytes remain immutable and receive no evidence credit through this file.

## 1. Evidence boundary and objective

Common challenge root: Git commit
`571abcf76d48f26247cb6c03da36b45563c9e446`.

The only post-root corrections used by AJ1 are enumerated here; no umbrella
reference to later channel prose imports evidence:

- anti-J action/cross-design Erratum 1, commit
  `8666da2cdb65582b24de6a4a73b977b713575efd`, path
  `corpus/whestbench/core/CODEX_ANTI_J_PREMUTATION_LADDER_ERRATUM1_20260811.md`,
  SHA-256
  `59613C80C3EF0750BC312786FC56985D5BED8F82405DE7E56588B33D0AE950A0`;
- Codex hostile audit, commit `c0e44c2`, path
  `corpus/whestbench/core/CODEX_OPUS_P4_P5_P6_HOSTILE_AUDIT_20260811.md`,
  SHA-256
  `A70395D7FBE388FD97689A85F021D03547CCA3CE710F901A49BD7317A35C9635`;
- that audit's append-only Erratum 1, commit `02c25b3`, path
  `corpus/whestbench/core/CODEX_OPUS_P4_P5_P6_HOSTILE_AUDIT_ERRATUM1_20260811.md`,
  SHA-256
  `6590A638588FC111FB1193B4BAFBFB7E42C765054F7118F9A2F0E6AF1A8BE7CF`;
- P1 evidence Erratum 1, commit `05d3197`, path
  `corpus/whestbench/papers/P1_SPECKLE_THEOREM_EVIDENCE_ERRATUM1_20260811.md`,
  SHA-256
  `83E6FD80C0354AE412F45D8B525F6F3CB9F0A2DD426BDA9C5CC16C122B153127`.

The post-charter R0 and M192 measurements, post-charter cmd2 helper probes, and
accidental NumPy archive comparisons are explicitly excluded. Static algebra
that does not depend on those outputs remains admissible under the cited
errata. Later evidence may rebut this proposal after reveal; it cannot enter
these proposal bytes retroactively.

Frozen incumbent `W0` is Kerdock v3.1 GUARDS, archive SHA-256
`8382E269C9B32E0935492734DDF8182560120F7E9331621AA18839D5D1F4EA06`.
It remains the only integrated artifact and the fallback if AJ1 fails.

AJ1 asks one question:

> Can a weight-conditioned, cross-fitted input reflection change the coupling
> of two individually Haar-valid 63-frame estimators enough to reduce their
> joint error, after paying for an independent path pilot and the full operator?

AJ1 is not an exact duplicate of the killed diagonal odd/even cumulant
surrogate, terminal JSpace top/bottom/complement, exact all-output reverse
adjoint, fixed zonal reweighting, or truth-free GLS. It is a prospective child
of the still-open anti-J M4b lineage and earns no separate novelty credit.

## 2. Honest forecast

There is no positive empirical anti-J signal. Previous terminal JSpace links
were near zero, and finite-sample negative spectra are structurally confounded.
Therefore the pre-evidence planning forecast is deliberately skeptical:

- subjective 90% adjusted-score ratio interval versus `W0`: `[0.75, 1.30]`;
- planning median: `1.02`;
- conditional winner tail, only after every premise gate passes: ratio
  `[0.18, 0.50]`;
- honest-tier stretch target under the provisional Phase-1 scale: upper 90%
  confidence bound on the complete adjusted-score ratio `<=0.20`.

These are decision forecasts, not measured confidence intervals. At `W0`'s
approximately `1.8321e-7`, the unconditional interval is approximately
`[1.3741e-7, 2.3817e-7]`; the target ratio `0.20` is approximately
`3.6642e-8`. This is not the literal public-number-one ratio. Before any AJ1
execution under published Phase-2 rules, bind a separate literal eligible-board
target

```text
r_board = best officially eligible adjusted score / revalidated W0 score.
```

The source, timestamp, eligibility rule, and both scores are frozen before AJ1
data. Candidate promotion uses the scientific gates below; a number-one claim
additionally requires the corresponding held-out upper bound to be `<=r_board`.
Phase-2 score law, evaluator pins, architecture set, residual
policy, and native-code policy are unknown until the organizer publishes them.
External rules may replace only rule-dependent legality, billing, and score
formulas. They may not retune AJ1's rank, layer band, streams, action counts,
transfer statistic, scientific thresholds, panels, or stop rules. If a rule
change makes those scientific choices unsuitable, AJ1 fails under this seal;
it does not adapt after seeing evidence.

## 3. Exact model convention

Use column hidden states. For layer `l=1..L`, with raw weight matrix `W_l`,

```text
z_l(x) = W_l^T h_{l-1}(x),
h_l(x) = ReLU(z_l(x)),
D_l(x) = diag(1[z_l(x)>0]),
K_l(x) = partial h_l(x) / partial x.
```

AJ1's primary architecture is frozen at input dimension `d=256`, hidden width
`n=256`, and depth `L=32`. Depths 8 and 16 are only the declared transfer
controls. The primary layer band is frozen as the first eight post-ReLU layers
`calL={1,...,8}` with `omega_l=1/8`. Rank is frozen at `r=1`; there is no rank
or layer-band sweep. If Phase 2 requires any other primary `d`, `n`, or `L`, AJ1
fails under this seal. It does not resize the null-count argument, frame
geometry, chart, fixtures, streams, or layer band.

## 4. Deterministic external chart

Construct a weight-only diagonal Gaussian reference, independent of every
pilot and production rotation. Use the incumbent's exact source literal
`rbar=MEAN_CHI_256=15.98438266660852747`, matching its fixed-radius angular
estimator, and initialize `m_0=0`,
`v_0=rbar^2/d`. For every unit i,

```text
mu_li  = sum_j W_l[j,i] m_(l-1),j,
tau2_li = sum_j W_l[j,i]^2 v_(l-1),j,
alpha_li = mu_li / sqrt(tau2_li),
m_li = sqrt(tau2_li) phi(alpha_li) + mu_li Phi(alpha_li),
q_li = (mu_li^2+tau2_li) Phi(alpha_li)
       + mu_li sqrt(tau2_li) phi(alpha_li),
v_li = q_li - m_li^2.
```

Set

```text
Sigma_l^0 = diag(v_l),
W_l^0 = diag(v_l^(-1/2)).
```

`Sigma_l^0` is a centered covariance reference, not a true deep covariance.
Fail if any `tau2_li` or `v_li` is nonpositive or nonfinite. No epsilon, ridge,
floor, pseudowhitener, or fold-fitted whitening is allowed.

Freeze the exact hidden-coordinate contract. For a permutation `P_l` and a
positive diagonal matrix `A_l`, write `G_l=P_l A_l` and transform

```text
h_l' = G_l h_l,
K_l' = G_l K_l,
Sigma_l^(0 prime) = G_l Sigma_l^0 G_l^T,
W_l^(0 prime) = P_l A_l^(-1) W_l^0 P_l^T.
```

Because `A_l` and `W_l^0` are diagonal,

```text
W_l^(0 prime) K_l' = P_l W_l^0 K_l,
Y_l' = P_l Y_l,
E_l' = P_l E_l P_l^T,
H' = H.
```

The covariance reference transforms by congruence; the whitener transforms
inversely. Conflating those two laws is a contract failure.

## 5. Frozen independent streams

All stochastic objects are deterministic, public, truth-free, and
domain-separated before observation. References below to iid, Haar, and
unbiased sampling are probability-model statements for the declared ideal
randomness law. Executable PCG64 streams are finite deterministic
pseudo-samples; they receive no exact-randomness or coverage claim, and direct
held-out gates remain mandatory. The 64-bit role identifiers are:

```text
discovery residual D_R1: 0xA110000000000001
discovery tangent  D_K1: 0xA110000000000002
discovery residual D_R2: 0xA110000000000003
discovery tangent  D_K2: 0xA110000000000004
transfer residual  T_R1: 0xA110000000000005
transfer tangent   T_K1: 0xA110000000000006
transfer residual  T_R2: 0xA110000000000007
transfer tangent   T_K2: 0xA110000000000008
shared path pilot Pi:    0xA110000000000009
Lanczos pair-1 start:    0xA110000000000011
Lanczos pair-2 start:    0xA110000000000012
random reflection:       0xA110000000000030
held-out rotations:      0xA110000000001000
bootstrap:               0xA110000000000040
truth replica 0:         0xA110000000000050
truth replica 1:         0xA110000000000051
```

Set `AJ1_STREAM_VERSION=2` and enumerate

```text
panel_code = {provider:0, premise:1, confirmation:2, depth8:3, depth16:4,
              depth32:5, hostile:6, synthetic_contract:7, truth:8}.
```

Except for the exact incumbent/held-out production-`Q` construction specified
below, every stochastic object is generated from the fixed-width uint32 tuple

```text
(AJ1_STREAM_VERSION,
 role_lo, role_hi,
 panel_code,
 api_mlp_seed_lo, api_mlp_seed_hi,
 depth,
 replicate_index,
 sample_index,
 block_index).
```

Here `lo=value & 0xffffffff` and `hi=value >> 32`. Range-check every field and
serialize in the displayed little-endian word order. Feed that exact word array
to the pinned `numpy.random.SeedSequence`, then instantiate pinned
`numpy.random.PCG64` and `numpy.random.Generator`. Do not flatten fields by
addition, XOR, truncation, an unspecified hash, or mutable spawn order. The
pre-evidence manifest binds the helper source/hash, NumPy version, BitGenerator,
normal-generation method, reduction order, and every tuple used. Before any
network forward, an exact tuple census proves uniqueness except for explicitly
declared common-random-number pairings, and exact replay tests reproduce every
synthetic-contract stream byte for byte.

Each operator fold contains exactly `S=128` independent normalized-Gaussian
states. For every fold/sample object, draw a fresh float64 vector
`g=(g_1,...,g_d)` with iid `N(0,1)` coordinates from that object's complete
tuple, compute `s=sum_i g_i^2` in increasing coordinate order, and set

```text
x = rbar * g / sqrt(s),       rbar = 15.98438266660852747.
```

Nonfinite input, norm, square root, or output, or `s<=0`, fails the invocation.
There is no rejection, redraw, orthogonalization, antipodal completion, QR, or
row/column reuse from a shared matrix. In real arithmetic these are iid
Haar-uniform directions on the sphere scaled by `rbar`. Their executable source
and per-state bill are manifest-bound. The eight folds therefore use 1,024
independent fixed-radius states. Discovery pairs are mutually independent;
transfer pairs are mutually independent and independent of discovery.

`Pi` is one separate ideal-Haar rotation, implemented by the exact pinned
finite QR algorithm below, of the incumbent point set. It contains
incumbent complete frames 0..3: 1,024 base directions and, after including
their antipodes, 2,048 paths. Frame 0 supplies 256 base directions/512 paths
for the ordinary pilot. Frames 0..3 supply 1,024 base directions/2,048 paths
for the fold pilot. This exactly matches the incumbent's pilot/fold roles while
remaining independent of production `Q`. Every `Pi` path uses radius `rbar`.
`Pi` produces no final estimate. It is fully billed and supplies every
pilot-dependent prune/fold/guard decision in both repaired production arms.

The fold generator above is not the incumbent `d-by-d` QR-Haar rotation. `Pi`
uses its tuple-derived PCG64 `Generator`, then matches the incumbent draw/QR/sign
path: draw `raw` with `standard_normal((d,d),dtype=fnp.float32)`, compute the
manifest-bound QR mode, backend, version, and memory layout, multiply column `j`
of `Q` by `-1` iff `T_jj<0`, and make no determinant correction to `+1`.

Each held-out rotation instead has an exact public integer seed. From the
complete held-out-rotation tuple for base network identity and replicate `m`,
construct the pinned `SeedSequence`, call
`generate_state(2,dtype=uint32)` exactly once, and set

```text
rotation_seed_m = int(state[0]) | (int(state[1]) << 32).
```

The census rejects any duplicate held-out seed within the complete experiment;
there is no redraw. Create an Arm-0 panel view with identical width, depth,
weights, and name but `mlp.seed=rotation_seed_m`, and invoke the immutable W0
archive itself. W0 therefore constructs `Q_m` with its exact
`default_rng(rotation_seed_m)`, float32 draw, QR, and sign path, and the meter
records that same invocation's complete output, branch, FLOPs, wall, and RSS.
Repaired Arms 1/2/R independently reconstruct that exact `Q_m` with the same
incumbent function and use it only as their paired production rotation; their
operator/fold tuples continue to use the original base-network `api_mlp_seed`,
not `rotation_seed_m`.

The deployed repaired provider has no held-out replicate selector. On an actual
API MLP it freezes

```text
Q_provider = _haar_rotation(int(base_mlp.seed),base_mlp.width)
```

using the exact incumbent function and source bytes. Its `Pi`, discovery,
transfer, operator, fallback-reservation, and all other provider tuples use the
same base `mlp.seed`. A `rotation_seed_m` exists only inside predeclared
held-out/depth evidence panels and can never choose or alter deployed behavior.

Static source census must prove that on a guard-quiet W0 path `mlp.seed` affects
the estimator only through this absorbed `Q_m`; merely copying the seed into the
rotated MLP may not alter a downstream branch or RNG. Any M186/M187 activation
already fails the confirmation panel, so its seed-dependent fallback cannot be
used. Truth and network-cluster identity are functions of the unchanged weights
and base identity, never the held-out rotation seed. Nonfinite `raw`, `Q`, or
`T`, an exactly zero diagonal, or float64-checked
`||Q^T Q-I||_F>1e-4` fails that invocation; there is no redraw. The ideal
real-arithmetic law is Haar on `O(d)`, not only `SO(d)`.

The immutable original W0 archive remains packaged separately, byte-for-byte
unchanged, and is the implementation invoked for every Arm-0 held-out
realization, deployed W0, and runtime fallback. It is never overwritten,
relinked, or rebuilt by an AJ seam refactor. Each Arm-0 error, cost, wall, RSS,
and guard record therefore comes from one and the same immutable-W0 invocation
at the same `rotation_seed_m`; no hybrid output/cost product is legal.

A separate pure repaired core, shared only by Arms 1/2/R, accepts the explicit
ordered triple `(pilot_Q,production_Q_A,production_Q_B)`. The first production
matrix is used only for frozen half `D_A=0..62`; the second only for
`D_B=63..125`. Arm 1 calls `(Pi,Q,Q)`, Arm 2 calls
`(Pi,Q,R_AJ@Q)`, and Arm R calls `(Pi,Q,R_random@Q)`. A synthetic contract proves
that `(Pi,Q,Q)` equals the intended common-pilot two-half 126-frame affine union,
with each ordered half consuming only its designated production matrix. The
source bill includes both production-matrix arguments and both half calls; it
never prices or substitutes a one-matrix full-rotation path. Arms 1/2/R alone
must have identical call graph, trace schema, and source bill. There is one
common repaired core, never a copied or arm-specialized panel kernel. The
manifest verifies frozen
archive member `kerdock_v3_estimator.py` SHA-256
`076D0A5D81891DDCBB4509DC6E2BFF5459D935B5556490A85D98DAC60759AACF`
and guard member `estimator.py` SHA-256
`5E7D52156B330BF63AC4FF0E0F38D864B32677F82BC8ED4D1382787A27D3E0C9`
for the untouched W0 package before building the separate AJ experimental core.

Use `sample_index` for a fold direction, `replicate_index` for a held-out
rotation, and `block_index` for a bootstrap replicate or subobject; unused
indices are zero. The random-control direction is the first draw at its role
tuple with all three indices zero. A replica swap exchanges the complete
`(residual role,tangent role,Lanczos-start role)` tuple, never only its label.

The public base API field `mlp.seed` is lawful and supplies the
`api_mlp_seed` tuple field. The derived `rotation_seed_m` is a separate public
experimental rotation key used only by the immutable Arm-0 view and the exact
paired-Q reconstruction in repaired arms; it never replaces base identity in
an operator, truth, or bootstrap tuple. No unexposed generator seed,
evaluator-internal state, truth, score, or held-out label may enter a stream.
Failure to reproduce any tuple, seed, or stream exactly is an invocation
failure, not permission to substitute another generator.

## 6. Cross-fitted residual operator

For each layer and every residual fold `F` in
`{D_R1,D_R2,T_R1,T_R2}`, let

```text
hbar_l^F = (1/128) sum_s h_l(x_s^F),
Z_l^F = [h_l(x_1^F)-hbar_l^F ... h_l(x_128^F)-hbar_l^F],
Sigmahat_l^F = Z_l^F (Z_l^F)^T / 127,
Y_l^F = W_l^0 Z_l^F,
E_l^F = Y_l^F (Y_l^F)^T / 127 - I.
```

This Bessel normalization is tied to iid states and an empirically fitted fold
mean. No structured or antipodal pilot may silently reuse it.

For a residual fold `R` and an independent tangent/receiver fold `K`, define

```text
H(R,K) = (1/8) sum_l E_(x in K)[
           K_l(x)^T (W_l^0)^T E_l^R W_l^0 K_l(x)
         ].
```

`H_true` denotes the corresponding product-population operator under the
declared ideal fixed-radius law: replace `E_l^R` by the population centered
residual `W_l^0 Cov[h_l(x)] (W_l^0)^T-I` and take the receiving expectation over
an independent draw. It is not a finite-PCG64 or finite-fold identity.

The two discovery operators are

```text
H_1 = H(D_R1,D_K1),
H_2 = H(D_R2,D_K2).
```

Their complete data tuples are disjoint, so `H_1` and `H_2` are independent
conditional on the fixed weights and deterministic chart. Each residual is
measurable only from its named residual fold; it is evaluated through an
independent receiving fold. No opposite-fold moment enters its construction.

For a raw JVP `t_l=K_l q`, apply the residual without materializing `E_l`:

```text
a_l = W_l^0 t_l,
b_l = Y_l [Y_l^T a_l] / 127 - a_l,
s_l = (1/8) (W_l^0)^T b_l.
```

One stopped-gradient reverse sweep with all `s_l` returns the per-state sum
`sum_l K_l^T s_l`. Average over the receiving fold. Differentiating the
empirical covariance itself is forbidden; this is only a covariance matvec.

## 7. Fixed eigensolver and projector

For each of `H_1` and `H_2`, build a six-action, fully reorthogonalized
symmetric Krylov/Rayleigh--Ritz basis. Use one domain-separated normalized
Rademacher start. For `j=1,...,6`, evaluate and retain

```text
z_j = H_r q_j.
```

This is the only operator action at step `j`. For `j<6`, obtain `q_(j+1)` by
exactly two increasing-index modified-Gram--Schmidt passes of `z_j` against
`q_1,...,q_j`, then normalize. A nonfinite quantity or a post-reorthogonalized
norm `<=1e-14*max(1,||z_j||_2)` before `q_6` exists is fail-closed breakdown.
There is no restart, replacement direction, outcome-selected action, or seventh
action.

All operator/eigensolver arithmetic is float64. Source accumulation order is
increasing layer, sample, then coordinate; reorthogonalization is increasing
Krylov index. JVP/VJP adjoint and operator-symmetry controls must satisfy

```text
|<p,Kq>-<K^T p,q>| <= 1e-10 max(1,|<p,Kq>|,|<K^T p,q>|),
|p^T Hq-q^T Hp|   <= 1e-10 max(1,|p^T Hq|,|q^T Hp|).
```

In the adjoint identity, `Kq` is the concatenation of the eight cached layer
JVPs in increasing layer then hidden-coordinate order, and `p` is the
concatenation of the eight exact stopped-gradient layer sources in that same
order. The inner products use increasing flattened index. Cached symmetry
pairs are the manifest-bound action pairs already present in `Q_6,Z_6`; no
free test vector or extra target action is permitted.

### Deterministic execution schedule

The normative reference schedule is one process, one worker, one native math
thread, and no GPU. It executes each six-step Krylov chain sequentially and
performs every reduction in the displayed order. Before numerical-library
import, the manifest binds all thread environment variables, effective BLAS
configuration, floating-point mode, process start method, dependency binaries,
CPU affinity policy, and memory layout.

Parallel execution is disabled unless published Phase-2 rules explicitly
permit it and the authoritative meter accounts for the complete descendant
process tree. Otherwise the manifest sets `P=1`. If permitted, the immutable
pre-evidence manifest binds exactly one positive worker cap `P` and every task
key

```text
(stage_id,panel_code,depth,api_mlp_seed,arm_code,replicate_index,
 role_id,action_index,sample_index,block_index).
```

`P` is selected and frozen in the manifest only from published rules and static
source/resource proofs, never from a synthetic-contract result, AJ1 value,
generated-network timing, truth, score, guard activation, or observed failure.
The later synthetic schedule contract can only validate or kill that frozen
choice; it cannot choose another `P` or fall back to serial within the same
family. The global barriers are exactly `STATIC -> SYNTHETIC_FIXTURES -> PREMISE
-> TRUTH -> ARM0 -> ARM1_GATE -> ARM2_AND_ARMR -> PRIMARY_REDUCER ->
DEPTH_HOSTILE`; no later-barrier task starts early.

Within each manifest-bound wave, sort its complete task keys lexicographically
and assign rank `k` to worker slot `k mod P` under the pinned `spawn` start
method. Every coordinator and worker process uses exactly one native math
thread; every manifest-bound BLAS, OpenMP, and runtime thread count equals one,
and `P` is the total cap on simultaneously executing computation workers,
including the coordinator whenever it performs floating work. There is no work
stealing, dynamic batching, retry, fork inheritance,
mutable shared RNG, unordered container, asynchronous reduction, JIT
specialization, or completion-order decision. A worker slot processes its
assigned keys in increasing key order and may write multiple shards. For every
task key, its assigned worker writes exactly one immutable canonical result
shard containing only deterministic numerical payload, branch, guard trace,
and exact source-operation counts. Its name, schema, serialization, bytes, and
SHA-256 depend only on that complete task key and deterministic result, never
on worker identity, `P`, assignment, completion order, wall time, RSS, or other
schedule-sensitive observation. Multiple deterministic outputs of one task are
fields of that one canonical shard.

Measured wall, RSS, operating-system timing, process identities, and other
schedule-sensitive fields live in a separate immutable meter receipt keyed by
the complete task key and deterministic-payload SHA-256. The coordinator joins
a receipt to a payload only by both keys and rejects any missing, duplicate,
unexpected, or mismatched pair. Meter receipts are structurally validated and
checked against frozen legal bounds but are excluded from `P=1` versus parallel
bitwise equality. Workers never write a shared accumulator. The coordinator rejects any
missing, duplicate, unexpected, or noncanonical key/shard pair and performs all
floating reductions in increasing layer, sample, coordinate, network seed,
rotation, and output-coordinate order as applicable. A leaf may run in parallel
only if it uses the same per-sample operations and shapes as the reference;
cross-sample GEMM reassociation is a different family.

`H_1` and `H_2` may execute concurrently and results are assigned by label,
never completion order. Actions 1..6 inside either operator remain sequential.
After both Ritz results freeze `u`, the two final Rayleigh actions and two
transfer-JVP banks may execute concurrently only in a non-scored experimental
wave or under the provider exception below. Repaired arms use separate fresh
process trees and share no cache. Within a completed non-provider barrier,
independent whole networks, the two truth replicas and their preindexed chunks,
unscored rotations, and bootstrap arithmetic may run concurrently; their
reducers still consume only canonical key order.

Every provider invocation whose meter receipt can enter `g_(a,m)` executes in
an isolated wave with no sibling network, rotation, or arm workload. Its
effective computation-worker count is one unless the published meter and score
law plus a pre-evidence static proof establish that the complete per-invocation
`g` is invariant to the selected internal concurrent schedule. No observed
timing, RSS, cost, or AJ value may supply that proof. Without it, H1/H2,
Rayleigh banks, Arm 2/Arm R, networks, and rotations are sequential for scored
provider records even if non-scored evidence uses `P>1`. If an invariant
provider schedule is lawfully proved, every descendant belongs to that one
isolated invocation and its complete process-tree receipt; still no two scored
provider invocations overlap.

A pre-network synthetic contract requires bitwise equality between `P=1` and
the selected parallel schedule for every deterministic numerical action,
projector, transfer statistic, transform, and scientific/control gate state,
plus bitwise equality of the complete canonical mapping
`{task_key: SHA256(task_shard_bytes)}`. Schedule-sensitive resource gate states
and meter receipts are validated separately and are not claimed bitwise equal.
Failure kills that manifest schedule. A serial replacement is a new
manifest/family that reruns every static gate and inherits no PASS; failure never
permits a scientific-target reference rerun or an extra H action.

Set

```text
Q_6 = [q_1 ... q_6],
Z_6 = [z_1 ... z_6],
A_6 = Q_6^T Z_6,
B_6 = (A_6+A_6^T)/2.
```

Require

```text
||Q_6^T Q_6-I||_F <= 1e-10,
||A_6-A_6^T||_F <= 1e-10*max(1,||A_6||_F).
```

Diagonalize dense symmetric `B_6` in ascending order. For its lowest normalized
eigenvector `y_r`, set

```text
u_r = Q_6 y_r,
lambda_r = lambda_min(B_6),
rho_r = ||Z_6 y_r-lambda_r Q_6 y_r||_2.
```

The second-lowest value comes from the same `B_6`. The direct residual consumes
only the six cached actions. Nonfinite output fails; an exact tie is handled
only by the frozen gap gate and cannot pass it. Repeat the pure `A_6/B_6`
formation, eigensolve, projector, and direct-residual computation from cloned
cached `Q_6,Z_6` buffers; it must be bitwise identical and consumes no H action.
No target operator rerun is hidden in this control.

Let `(lambda_1,u_1)` and `(lambda_2,u_2)` be the two lowest Ritz pairs. Align
the sign of `u_2` to make `u_1^T u_2>=0` and set

```text
u = (u_1+u_2) / ||u_1+u_2||,
P_AJ = u u^T,
R_AJ = I - 2 P_AJ.
```

Fail if the denominator vanishes. Require

```text
P_AJ^T=P_AJ,
P_AJ^2=P_AJ,
R_AJ^T R_AJ=I,
R_AJ^2=I.
```

with Frobenius residual at most `1e-10*max(1,||object||_F)` for every displayed
identity. Hidden-gauge/permutation and complete discovery-replica-swap controls
use relative tolerance `1e-9` and must preserve the rank-one projector, not an
eigenvector sign. A replica swap includes both fold streams and the attached
Lanczos start. After these checks, `u` is frozen before any transfer fold is
read; transfer data may neither reorient nor refit it.

The code convention is left action:

```text
Q_prime = R_AJ @ Q,
```

because the physical rows are `S @ Q.T` and the reflected rows must be
`S @ Q.T @ R_AJ`. A frozen noncommuting 2-by-2 contract test must distinguish
this from the wrong `Q @ R_AJ` action before any network forward.

## 8. Independent fixed-direction transfer premise gate

Centered `S=128` covariance in width 256 forces at least 129 exact `-1` modes
of every single-fold `E_l`. Negative sign, negative count, and discovery-only
Ritz magnitude are therefore non-evidence. AJ1 does not attach a p-value to a
small empirical null bank. Instead, it removes eigenvector-selection bias by
freezing `u` on the discovery folds and testing only that fixed direction on
four fresh folds.

For transfer tangent fold `T_Kb`, define

```text
a_l(x) = W_l^0 K_l(x) u,
M_l^b = (1/128) sum_(x in T_Kb) a_l(x) a_l(x)^T,
T_ab = (1/8) sum_l trace(E_l^(T_Ra) M_l^b),  a,b in {1,2}.
```

Conditional on the weights, deterministic chart, and discovery data, `u` is
fixed. The empirically centered `1/(S-1)` Bessel covariance is unbiased because
each residual fold contains 128 iid Haar states. The uncentered `1/S` tangent
second moment is unbiased for the same reason. Every residual fold is
independent of every tangent fold. Consequently, before conditioning on any
pass event, each `T_ab` is an unbiased estimator of the corresponding
fixed-direction quadratic form `u^T H_true u`. The four cross-pairs are useful
replication views but are dependent because they reuse two residual and two
tangent banks; they are not four independent tests. Transfer uses primal
forwards and one forward JVP per tangent state; it uses no VJP, eigensolve,
direction update, sign update, or retry.

Four exact synthetic fixtures precede any network. The strict-six eigensolver
fixture is

```text
H_6 = diag(-3,-2,-1,1,2,3,0,0),
q_1 = (1,1,1,1,1,1,0,0)^T/sqrt(6).
```

It injects that start, issues exactly six `H_6` actions without pre-six
breakdown, and returns `lambda=-3`, projector `e_1 e_1^T`, and direct residual
at most `1e-10`. The separate rank-one action/transfer fixture uses
`W^0=K=I`, `E=-e_1 e_1^T`, and supplied direction `u=e_1`; it tests
`Hq=-(e_1^Tq)e_1` and a strictly negative independent-transfer statistic but
does not pass through the strict-six eigensolver. `E=0` returns loud
`NO_SIGNAL`, never PASS. The noncommuting action fixture uses
`Q=[[0,-1],[1,0]]`, `R=diag(-1,1)`, and `W=[[1,2],[3,5]]`; it matches
`Q.T @ R @ W` and differs from the wrong-side construction.

After `u` is frozen, spend exactly one additional `H_1 u` action and one
additional `H_2 u` action and compute the final-direction discovery Rayleigh
values

```text
q_D1 = u^T H_1 u,
q_D2 = u^T H_2 u.
```

AJ1 fails at the operator premise unless all conditions hold:

1. `lambda_1<0` and `lambda_2<0`;
2. squared projector overlap `(u_1^T u_2)^2 >= 0.80`;
3. each direct cached-action Ritz residual `rho_r` is
   `<=0.05*|lambda_r|`;
4. for each replica, the next-lowest minus lowest Ritz value is
   `>=0.25*|lambda_r|`;
5. `q_D1<0` and `q_D2<0`;
6. all four `T_ab<0`;
7. with `m_D=max(-q_D1,-q_D2)`, every `-T_ab >= 0.25*m_D`;
8. `min_ab(-T_ab) >= 0.25*max_ab(-T_ab)`;
9. hidden permutation/positive-gauge, complete replica swap, deterministic
   postprocessing repeat, adjoint, symmetry, projector, and action fixtures
   pass.

For the random control, draw exactly one normalized float64 iid-Gaussian vector
from the frozen random-control tuple and call it `u_random`. Do not inspect its
overlap with `u`, reject it, advance a block, or redraw. Set
`R_random=I-2u_random u_random^T`; report overlap descriptively only. The
confirmation panel compares its directly measured coupling/score with AJ1 under
the same topology and billing rule. Geometric distinction earns no credit.

This gate may be reported only as `TRANSFER_SCREEN_PASS`. It is an effect-size
replication, not a significance test, p-value, GREEN, or interval certificate.
The ungated `T_ab` estimators are conditionally unbiased; their displayed
values after conditioning on PASS are selected and must not be described as
unbiased estimates. The screen estimates a direction from rank-deficient
empirical residual covariances. Rank deficiency alone gives that direction no
credit and neither proves nor disproves a population negative mode. Only
independent held-out output covariance and direct
bias/MSE/score confirmation can promote AJ1.

## 9. Static bill and legality gate

Before the pilot-JVP premise is authorized, freeze source-level bills for:

- the diagonal reference;
- 512 residual-fold primal forwards and 512 tangent-fold primal forwards
  through layers 1..8, using eight disjoint 128-state folds;
- fourteen discovery H actions: six on `H_1`, six on `H_2`, and the two
  final-direction Rayleigh actions;
- 256 transfer forward-JVP evaluations, with no transfer VJP or eigensolve;
- the exact 2,048-path shared path pilot through its incumbent pilot/fold
  routes;
- centering, implicit-Y products, whitening, sources, reverse accumulation,
  reorthogonalization, Ritz solve, reflection, copies, and reductions;
- the directly measured random-reflection control in scientific panels;
- full production arms, guards, fallback, residual wall, peak RSS, and every
  failure path.

The fourteen target H actions are exact: six on each discovery operator and
one final-direction Rayleigh action on each. The target symmetry check reuses
`A_6=Q_6^T Z_6`; every per-action adjoint check reuses the JVP, source, and VJP
already computed by that action; deterministic postprocessing repeats only the
cached `Q_6,Z_6` algebra. Synthetic matrix, gauge, permutation, and action
fixtures are fixture-only. None performs an undisclosed target H action. Any
implementation that reruns a target action, JVP, VJP, forward, or provider for
a control changes the source bill and the proposal-family manifest before
evidence or fails.

No dense all-output Jacobian or all-output covariance adjoint is permitted.
All numerical work must pass through the announced legal Phase-2 meter. Every
setup, pilot, JVP, VJP, eigensolve, and transformation is billed. The source
ledger must separate experimental panel cost from per-MLP deployed-provider
cost; offline evidence does not discount provider work. No native extension,
evaluator internals, unexposed/private generator seed, scorer output, truth,
or held-out label
enters selection. Public generated network weights enter only through the
declared weight-conditioned chart/operator.

Let `C_setup,max` be the source-billed worst-case cost of every per-invocation
AJ1 operation completed before the production/fallback branch, including the
chart, 1,024 fold states and forwards, fourteen H actions, 256 transfer JVPs,
`Pi`, RNG, reductions, eigensolves, branch controls, allocations, copies, and
guards. Let `C_AJ,max` and `C_W0,max` be authoritative complete worst-case
production bills from frozen source. Static approval requires strict
inequalities

```text
C_setup,max + C_AJ,max < B,
C_setup,max + C_W0,max < B,
C_setup,max <= 0.20 C_W0,max,
```

and corresponding strict wall-time and peak-RSS limits. Symbolic bills,
optimistic partial worksheets, and measured-average shapes cannot satisfy this
gate. Provider cost and experimental panel/fixture cost are separate ledgers;
neither discounts the other.

For each manifest-bound parallel wave with fixed worker assignment `A_w`, bind

```text
F_wave,max = sum_t F_t,max + F_ordered_reduce,max,
T_wave,max = T_spawn,max
             + max_w sum_(t in A_w) T_t,max(P)
             + T_merge,max + T_teardown,max,
R_wave,max = R_parent,max + sum_w R_worker,w,max
             + R_IPC,max + R_shards,max.
```

Concurrency never divides the charged FLOPs or authoritative cost. Copies,
serialization, hashes, IPC, synchronization, spawn, cancellation, join, and
teardown are charged under the published meter. Wall is the end-to-end critical
path including contention and cleanup. Peak RSS is the simultaneous aggregate
process-tree working set, including parent, all live children, IPC buffers, and
shards under the published shared/private-page rule; it is never `max(worker)`.
No copy-on-write or ideal-speedup credit is allowed without an authoritative
rule and exact witness.

Before starting each setup stage, the runtime reserves the complete remaining
worst-case W0 cost, wall time, and memory from the authoritative W0 ledger. If
the next stage could make exact W0 completion impossible under any hard limit,
do not start it: execute W0 immediately. On later chart, discovery, transfer,
numerical, resource, or stream failure, discard every AJ1 quantity and execute
the unmodified W0 bytes on their original production stream. Already-spent AJ1
setup remains billed. Any fallback on a premise, confirmation, or depth panel
kills promotion. Fallback exists only for lawful private-network completion
and for the explicitly predeclared hostile fallback fixtures below.

Before a parallel wave, reserve its complete worst-case work, the maximum work
every launched task can spend before cancellation is observed, teardown/join,
and full remaining W0 completion. A wave is atomic: no later barrier starts
until all tasks finish or the frozen deadline expires. Missing, duplicate,
noncanonical, nonfinite, crashed, or timed-out shards fail without retry or
rescheduling. On failure, charge all launched work, terminate and join every
child, discard all AJ1 shards, verify memory release, and only then execute W0.

Static fail conditions:

- projected worst-case total cost reaches the hard budget;
- provisional operator overhead exceeds `0.20*C_W0` before any measured
  covariance gain;
- peak/resource/timeout headroom is absent;
- either complete success or complete fallback path violates a hard limit;
- the Phase-2 rule announcement makes any path unlawful or prevents the frozen
  scientific gates from being evaluated without changing the mechanism.

## 10. Three-arm attribution, random control, and cheapest scientific kill

Only after both sealed proposals are revealed, the owner has immutably selected
exactly one proposal family before premise evidence, and a separate
owner-approved authority exists, run rungs in this order:

```text
Arm 0: exact immutable W0 on the same-weight panel view with
       mlp.seed=rotation_seed_m; output and complete cost/resource record are
       captured from that single invocation.
Arm 1: full common AJ setup; 6 H1 + 6 H2 + 2 Rayleigh actions; 256 transfer
       JVPs; full Pi; core arguments (Pi,Q,Q); common transform kernel with
       c=0 and v=u supplies production_Q_B=Q.
Arm 2: identical common setup/actions; core arguments (Pi,Q,R_AJ@Q); common
       transform kernel with c=1,v=u supplies production_Q_B=R_AJ@Q.
Arm R: identical common setup/actions; common transform kernel with
       c=1,v=u_random supplies production_Q_B=R_random@Q; core arguments
       (Pi,Q,R_random@Q); panel control only.
```

In every held-out statistic, `W0`/`Arm 0` means the output and complete
cost/resource record of that same immutable-W0 invocation at
`rotation_seed_m`. The bootstrap preserves the pair; it never combines an error
at one Q with a bill, wall time, RSS, branch, or guard record from another Q.

Arm 1 is the cheapest full-estimator kill. It measures the cost, bias, and
variance debt of separating the path pilot before reflection receives credit.
Arm 1, Arm 2, and Arm R execute the same manifest-bound repaired source and the same
setup/operator/transfer path in fresh processes with no cross-arm cache reuse.
The final kernel is

```text
production_Q_A = Q,
Q64 = float64(Q),
v64 = float64(v) / ||float64(v)||_2,
production_Q_B = cast_to_Q_dtype[Q64 - 2*float64(c)*v64*(v64^T Q64)].
```

The norm and inner products use increasing coordinate order; both production
matrices have dtype and memory layout exactly equal to `Q`. Nonfinite
`v64`/`production_Q_B`, a nonpositive norm, or float64-checked
`||production_Q_B^T production_Q_B-I||_F>1e-4` fails. `c` is runtime data
and is never compile-time specialized or zero-elided. The same call graph,
shapes, operations,
allocations, copies, transform trace, and source bill execute for every repaired
arm; no JIT/value specialization is allowed. A synthetic `c=0` fixture requires
`production_Q_A` and `production_Q_B` both to be bitwise `Q`. A common-`Pi`
half-decomposition fixture separately hashes each ordered 63-frame result and
requires their affine recombination to equal exactly the intended common-pilot
126-frame functional; swapping the two production arguments must be detected by
a noncommuting asymmetric fixture. Complete measured wall, RSS, and score remain
arm-specific because downstream data can differ. Thus Arm2/Arm1 isolates the
reflection action rather than operator or transform cost. Arm 0 is the exact
immutable incumbent and performs no AJ setup.
Arm 1 clears topology only if all three co-primary bounds hold:

```text
upper96.667[complete adjusted-score ratio Arm1/W0] <= 1.05,
upper96.667[BiasNI(Arm1:W0)] <= 0.05,
upper96.667[mean_W V_Arm1(W)/mean_W V_W0(W)] <= 1.05.
```

These use Bonferroni allocation for familywise one-sided 90% empirical
bootstrap coverage. Failure kills AJ1 before Arm 2. Arm R executes the same
setup and differs only at the final transform. It tests whether
weight-conditioned direction selection beats one frozen independent
Haar-axis reflection;
it can kill mechanism credit but can never become a post-result replacement
proposal.

For Arm 2, freeze incumbent complete frames `D_A=0..62` under `Q` and
`D_B=63..125` under `R_AJ @ Q`; retain all antipodes and equal arm weight 1/2.
At `R=I`, the direction multiset is the incumbent's 126 frames, though the
independent pilot makes the estimator topology different.
Arm R uses the identical split and weights with `D_B` under `R_random @ Q`.

Conditional on fixed weights, `Pi`, every operator decision, and independence
from the held-out rotation, each fixed node under `Q~Haar(O(d))` has the
spherical marginal, and every fixed `R in O(d)` gives `RQ~Haar(O(d))`. This
full-matrix statement is not asserted for `Q~Haar(SO(d))`, because a
Householder has determinant `-1`. The finite pre-guard combined estimator must
be the affine equal-weight average `Y_C=(Y_A+Y_B)/2`; no adaptive or nonlinear
cross-half decision is permitted. Under these exact conditions Arm 2 and Arm R
introduce zero reflection-induced bias in ideal real arithmetic for that finite
pre-guard functional. The theorem does not pass through M186 or M187: their
fallback, `isfinite`, `where`, and `nan_to_num` behavior is nonlinear. Every
confirmation and depth arm invocation records both guard counters, and any
M186 or M187 activation on Arm 0/1/2/R is a panel FAIL. Only the explicitly
named hostile/collapsed fixtures may exercise their declared guard/fallback
path, with no theorem or promotion credit. A private-provider activation
remains a completion safeguard but supplies no reflection-bias claim.
This is a marginal-Haar theorem, not a claim that a 63-frame subset remains an
exact design. Pilot/topology approximation and finite arithmetic can still
produce benchmark bias, so the direct bias confidence gate remains mandatory.

Within each fixed network and fixed `Pi`, center over held-out Haar rotations:

```text
kappa_AB(R) = 2 Cov(Y_A,Y_B) / (Var_A+Var_B)
            = 1 - Var(Y_A-Y_B)/(Var_A+Var_B).
```

Before any arm output is read, build two independent truth replicas per network.
Each replica uses exactly `N_truth=3,538,944=54*65,536` iid float32 Gaussian
inputs in 54 equal chunks, its own frozen truth role, the complete truth stream
tuple, the frozen generated weights, and the exact final-layer float32 forward
used by the reference builder. Accumulate each chunk in float64 and retain all
54 chunk means plus their canonical hashes. The two replicas are independent
of each other and of every AJ/arm stream. Their builder source, dependency
versions, per-network inputs, costs, and output hashes are sealed before arm
execution. Direction discovery, transfer, and provider processes cannot open
truth files; only the post-output reducer can. This truth execution requires a
separate authority and supplies no estimator input.

The scored reference functional is frozen as the final hidden-layer mean vector
under iid float32 Gaussian input, so `p=256`; intermediate analytic stack rows
are guard/diagnostic outputs and never enter these scientific sufficient
statistics. For network W and `M` held-out rotations, let the two truth means be
`truth_W^(0)` and `truth_W^(1)` and define

```text
Ybar_a = (1/M) sum_m Y_(a,m),
V_a(W) = [1/(p(M-1))] sum_m ||Y_(a,m)-Ybar_a||^2,
C_AB(W)= [1/(p(M-1))] sum_m
         <Y_(A,m)-Ybar_A, Y_(B,m)-Ybar_B>,
S_a(W) = <Ybar_a-truth_W^(0),Ybar_a-truth_W^(1)>/p,
b2hat_a(W) = S_a(W)-V_a(W)/M,
MSEhat_a(W) = S_a(W)+[(M-1)/M]V_a(W).

Y_(C,m) = [Y_(A,m)+Y_(B,m)]/2,
Ybar_C = (1/M) sum_m Y_(C,m),
V_C(W) = [1/(p(M-1))] sum_m ||Y_(C,m)-Ybar_C||^2,
S_C(W) = <Ybar_C-truth_W^(0),Ybar_C-truth_W^(1)>/p,
b2hat_C(W) = S_C(W)-V_C(W)/M,
MSEhat_C(W) = S_C(W)+[(M-1)/M]V_C(W).
```

Under the frozen independence, `b2hat` is a signed unbiased squared-bias
estimator and `MSEhat` is an unbiased MSE estimator. `b2hat` is never floored,
made absolute, or renamed as a nonnegative observed bias. Define every repaired
arm's `V`, `b2hat`, and `MSEhat` from its combined estimator, not a half arm.
Evaluate W0 directly on the paired panel; never reconstruct it from repaired
arms. Bootstrap the 54 truth chunks independently inside each truth replica as
an additional independent level.

Adjusted score preserves the within-rotation error/cost coupling. For every
complete arm output, including `C` for a repaired arm, define

```text
L_(a,m)(W) = <Y_(a,m)-truth_W^(0),Y_(a,m)-truth_W^(1)>/p,
g_(a,m)(W) = announced complete score multiplier computed from the cost and
             resource record of that exact same arm/network/rotation invocation,
Scorehat_a(W) = (1/M) sum_m L_(a,m)(W) * g_(a,m)(W).
```

Thus `MSEhat_a=(1/M)sum_m L_(a,m)` remains the raw-MSE statistic, but it is
never multiplied by a separately averaged multiplier. Every bootstrap rotation
draw moves the complete atomic tuple `(Y,cost,wall,RSS,branch,guards)` together
and recomputes `L`, `g`, and their product. Aggregate adjusted score uses equal
network weights, and every displayed adjusted-score ratio `X/Y` means
`sum_W Scorehat_X(W) / sum_W Scorehat_Y(W)`. Only a static proof that `g` is
identical for every `m` could algebraically simplify this mean of products; no
observed equality may do so.

For the point estimate and separately for every bootstrap replicate, require
finite `g_(a,m)>0` for every invocation and strictly positive finite
`sum_W Scorehat_a(W)` for every arm entering any adjusted-score numerator or
denominator. Otherwise the panel fails before forming a ratio; it never floors,
drops, takes an absolute value, imputes, or converts the result to a favorable
sign. Individual `L_(a,m)` and `b2hat` values remain signed.

Define the stable bias noninferiority statistic

```text
BiasNI(X:Y) =
  sum_W [b2hat_X(W)-b2hat_Y(W)] / sum_W MSEhat_W0(W).
```

A nonpositive denominator, undefined truth chunk, or nonpositive complete
aggregate `MSEhat` is FAIL. Never ratio two near-zero bias estimates.

Use equal network weights and form

```text
kappa_panel = 2 sum_W C_AB(W) / sum_W [V_A(W)+V_B(W)].
```

Never average per-network kappas and never pool raw outputs across truths.
In every gate, `kappa_panel(I)` is computed from Arm 1 and
`kappa_panel(R_AJ)` from Arm 2 using the displayed sufficient-statistic ratio.
Complete adjusted score uses the displayed `Scorehat`, the same-invocation
complete arm records, and only the score law bound before evidence. Raw-MSE and
bias gates continue to use `MSEhat` and `b2hat`.

Reflection credit requires all five co-primary gates:

```text
upper98[kappa_panel(R_AJ)-kappa_panel(I)] <= -0.20,
upper98[complete adjusted-score ratio Arm2/Arm1] <= 0.95,
upper98[complete adjusted-score ratio Arm2/W0] <= 0.80,
upper98[BiasNI(Arm2:Arm1)] <= 0.05,
upper98[complete adjusted-score ratio Arm2/ArmR] <= 0.95.
```

Five one-sided `98%` bounds use Bonferroni allocation for familywise one-sided
90% empirical bootstrap coverage. `Arm2/Arm1` is the primary causal score
contrast, W0 is incumbent performance, and ArmR is mechanism specificity.

The separate honest-tier stretch gate is

```text
upper90[complete adjusted-score ratio Arm2/W0] <= 0.20.
```

It has only its stated pointwise empirical interpretation and is not part of
the five-gate simultaneous family. A literal number-one claim additionally
requires the pre-evidence `r_board` gate from Section 2.

Truth-free covariance may screen the premise, but only matched direct MSE,
bias, billed cost, residual wall, peak memory, failure, and adjusted score can
promote it.

## 11. Panels, sensitivity axis, and multiplicity

No truth result may tune rank, layer band, fold count, action count, transfer
threshold, or gate.
The premise panel is six generated whole networks with seeds
`8110401..8110406`; it executes only chart, discovery, and fixed-direction
transfer and reads no truth or held-out provider output. The confirmation panel
is twelve disjoint networks with seeds `8110501..8110512` and twelve paired
rotations per network. The depth-transfer panel uses seeds `8110801..8110804`
and eight rotations at each transfer depth.

Every premise network must individually pass every chart, discovery, numerical,
and fixed-direction transfer gate. No network may be pooled away, dropped, or
converted to fallback. Every confirmation network must individually complete
the same frozen operator screen and every requested arm. The five co-primary
reflection gates are applied to the confirmation panel only; the premise panel
can kill but cannot promote. There is no survivor-only confirmation subset.

Within every confirmation network, each held-out rotation is
common-random-number paired across Arm 0, Arm 1, Arm 2, and Arm R. The depth
panel pairs every requested arm analogously. Operator/transfer folds and `Pi`
remain fixed for that network and independent of those rotations. Network
seeds, rotations, and all four arm labels are frozen before any truth is read.

All confidence bounds use 50,000 deterministic paired hierarchical bootstrap
replicates from the frozen bootstrap role. For replicate `b=0..49,999` and
outer occurrence `o=0..N_W-1`, a fresh complete tuple with
`api_mlp_seed=0,replicate_index=b,sample_index=o,block_index=0` draws one
network index by pinned `Generator.integers(0,N_W,dtype=uint32,endpoint=False)`.
Do not deduplicate repeated networks. Every occurrence, including duplicate
draws of the same network, receives independent inner draws:

```text
paired rotation draw m: block_index = 0x10000000 + m,
truth-0 chunk draw c:    block_index = 0x20000000 + c,
truth-1 chunk draw c:    block_index = 0x30000000 + c.
```

Those inner tuples use the selected public network seed, the same `b,o`, and
draw respectively from `[0,M)` or `[0,54)`. Each tuple creates one fresh
Generator and one integer; no mutable draw stream is shared. For an occurrence,
the same paired rotation indices apply to every arm and move each complete
atomic `(Y,cost,wall,RSS,branch,guards)` record together, while truth-replica chunk
draws are independent of rotations and of each other. Recompute the two truth
means from their selected equal-size chunk means, then recompute every
occurrence-level sufficient statistic, `b2hat`, `MSEhat`, kappa numerator and
denominator, `L_(a,m)`, `g_(a,m)`, `Scorehat`, and resource/cost field. Aggregate the `N_W`
occurrences with equal weight in increasing outer-position order. This exact
rule—not one reused inner draw per unique network—is manifest-bound.
After sorting the 50,000 replicate statistics ascending, `upper_q` is the
one-based order statistic at index `ceil(q*50000)`. No interpolation, BCa,
optional stopping, or post-failure increase in sample size is allowed. These
are predeclared empirical bootstrap bounds, not finite-sample coverage
certificates.

Any nonfinite statistic, zero or negative variance denominator, missing arm,
fallback, failed invocation, or undefined bootstrap replicate is a panel FAIL;
it is never dropped, floored, imputed, or converted to a favorable infinity.

The primary production point is depth 32. The declared sensitivity axis is
depth/gate coherence:

```text
depths 8, 16, 32; same width, the same first-eight-layer band, and all other
frozen AJ1 parameters.
```

The premise panel may kill but cannot promote. The confirmation panel is the
promotion authority. At depth 8 and depth 16, require both point estimates
`kappa_panel(R_AJ)-kappa_panel(I)<0` and complete adjusted-score ratio
`Arm2/Arm1<1`; failure of either sign is a transfer failure, not a tuning
invitation. These depth checks are predeclared descriptive vetoes, not
simultaneous confidence statements.

Hostile and metamorphic fixtures are frozen nonpromotional controls, never
tuning axes. Bind committed A4 generator commit
`78bc4513b430fefdaa9145e16e04102e52cdf627`, path
`corpus/whestbench/experiments/a_series_granular_adversarial/run_a4_hostile.py`,
and source SHA-256
`52CBA048E782673E3E8ACF4CEC2F1052153A493B7B0462CF82990E74293FDA09`.
Its exact seven families are `a_gain_1e-3`, `b_gain_1e3`, `c_t3_heavy`,
`d_rank32`, `e_corr_rho095`, `f_negshift`, and `g_gain_1e-38`. The manifest
enumerates every official `mlp.seed` and construction parameter. Each family
is one standalone metered AJ1 invocation and must end in either a complete
finite in-budget result or its predeclared exact in-budget W0 fallback. Crash,
hang, nonfinite output, silent drop, redraw, or parameter repair kills AJ1.
Fallback here proves only fail-safe behavior and grants no promotion credit.

Add a collapsed-chart fixture from frozen base seed 101 by setting layer 4's
weight matrix exactly to zero. It must fail the chart before operator credit and
execute exact W0 fallback while retaining every spent setup charge.

Add two base-seed-101 metamorphic pairs under `z_l=W_l^T h_(l-1)`, with
`P_0=P_32=I` and `G_0=G_32=I`:

- permutation: hidden-layer reversal `P_l e_i=e_(255-i)` and
  `W_l'=P_(l-1) W_l P_l^T`;
- positive ReLU gauge: hidden-layer diagonal `G_l(ii)=2^4` for even `i` and
  `2^-4` for odd `i`, with `W_l'=G_(l-1)^(-1) W_l G_l`.

Each pair uses identical complete stream tuples, and both the untransformed and
transformed member must complete the AJ success path with both guards quiet;
fallback by either member fails the metamorphic pair. The manifest classifies
each compared tensor by its frozen implementation dtype; no result-dependent
cast or tolerance class is permitted. For every float64 chart, covariance,
whitener, residual-action, input-operator, projector, or transfer tensor
`X_prime` and the exact analytic permutation/gauge image `X_star`, require

```text
||X_prime-X_star||_F <= 1e-9*(1+||X_star||_F).
```

For float32 primal hidden states and production intermediates, whose legal
permutation can change dot-product accumulation order, freeze the distinct
prospective predicate

```text
||X_prime-X_star||_F <= 1e-4*(1+||X_star||_F).
```

Chart covariance/whitener tensors and residual actions use their displayed
`P/G` maps. The input-space operator, rank-one projector, and transfer direction
are invariant under a hidden-coordinate change and use the float64 predicate;
eigenvector sign is removed through the projector. Final provider outputs require
`||Y'-Y||_2 <= 1e-4*(1+||Y||_2)`. The collapsed-chart and seven A4 fixtures
retain only their separately declared fallback behavior. No observed result may
relax a tolerance. All fixture work is metered experimental cost and never
discounts provider cost. No other unnamed mandatory control exists; any future
control is a separately sealed falsifier that may kill but cannot tune, rescue,
or replace AJ1.

## 12. Integration path

1. Bind final Phase-2 rules and revalidate exact `W0` archive bytes.
2. Before the first synthetic or scientific forward, JVP, VJP, chart, truth,
   premise, or output value is observed, build all four complete Arm 0/1/2/R provider
   paths and one immutable implementation manifest. It binds this proposal;
   immutable W0; held-out rotation-seed derivation and paired-Q reconstruction;
   the common repaired setup/operator/transfer core; every arm wrapper/archive; stream
   helper; truth builder; tests; source bills; fallback; panels; reducers;
   serial/parallel schedules; process/thread environment; task/batch map;
   ordered reduction; concurrency bills; gates; hostile fixtures; runtime;
   dependencies; and exact hashes. No field may be filled from a later run.
3. Under separate no-forward authority, run source inspection, import/schema
   tests, dimensional contracts, synthetic matrix contracts, and static bills
   against those frozen bytes. These checks read no generated weight, chart,
   pilot, provider, truth, or score value.
4. After independent no-forward static PASS, a separate synthetic-forward-only
   authority may run the already frozen deterministic synthetic MLP, provider,
   guard, strict-six, rank-one, zero, noncommuting, c=0, half-decomposition, and
   serial/parallel equivalence fixtures. This rung may inspect only its
   hand-constructed synthetic inputs and outputs. It may not read generated or
   challenge-network weights, scientific chart/fold/pilot values, premise or
   held-out providers, truth, score, leaderboard state, or hosted results. Every
   result is pass/fail only: failure kills this manifest; it cannot change `P`,
   a tolerance, a byte, a stream, or any scientific choice. Meter and seal the
   complete fixture record.
5. After synthetic-fixture PASS, run the truth-free premise/fixed-direction
   transfer screen with meters and a receipt;
   stop on anything other than `TRANSFER_SCREEN_PASS`.
6. Only after that PASS, generate and hash the two independent truth replicas
   under truth-only authority; seal them from every selector/provider.
7. Run Arm 0 then Arm 1 on the frozen confirmation design; stop before Arm 2/R
   on topology debt, fallback, or a failed Arm-1 family gate.
8. Run already frozen Arm 2 and Arm R, then let the reducer read sealed outputs
   and truth and compute the predeclared covariance, bias, MSE, resource, and
   score gates.
9. Run the already frozen depth and hostile controls; rebuild the exact
   pre-evidence archive bytes and verify members, guards, bills, resources, and
   reproducibility.
10. One hosted canary is permitted only under published Phase-2 authority and
   explicit user approval.

The first synthetic or scientific numeric observation finds the implementation
manifest already sealed. A later byte or parameter change invalidates every AJ1
result and starts a new proposal family; it is never an in-place repair.

## 13. Proposal-family identity

The AJ1 family is exactly
`(proposal_sha256,pre_evidence_manifest_sha256)`. The manifest binds every
scientific and executable degree of freedom: chart, covariance reference,
generator and tuples, `Pi`, folds, rank, layer band, actions, Rayleigh--Ritz
rule, transfer, controls, frame split, weights, arm topology, truth,
statistics, gates, panels, bootstrap, hostile fixtures, fallback, serial and
parallel schedules, process/thread environment, task map, ordered reduction,
concurrency bills, source, tests, archive members, runtime, and dependencies.

After the first synthetic or scientific numeric observation, any change to a bound item,
including a bug fix, tolerance, draw, or fallback, creates AJ2 or another newly
sealed family and reruns from zero. It inherits no AJ1 premise, confirmation,
or hostile evidence. Before any premise data, the owner must select exactly one
revealed proposal family or approve a canonical NULL. Running multiple
proposals and selecting the favorable one is forbidden unless a separately
sealed cross-proposal multiplicity design exists first. A published rule may
bind a symbolic rule-dependent field only by append-only pre-execution
amendment; incompatible rules kill AJ1 rather than retune it.

## 14. Stop rule and disposition

Stop immediately on any static cost/resource illegality, chart failure,
rank-null self-deception, discovery-replica instability, fixed-direction
transfer failure, wrong-side action, fallback, Arm-1 topology debt, failure to
beat the random control, insufficient covariance improvement, bias increase,
depth-transfer reversal, resource failure, or score gate miss. Do not change
rank, layer band, fold count, action count, frame split, statistic, or threshold
after a failure.

`BOTH_KILLED` is honourable and leaves GUARDS unchanged. AJ1 earns candidate
status only after the complete integrated gates above. Until then it is one
high-upside, low-prior, cost-unproven proposal with a bounded sequence of
predeclared fatal tests. No cheapness or feasibility claim exists until the
manifest-bound source ledger proves both success and fallback paths.
