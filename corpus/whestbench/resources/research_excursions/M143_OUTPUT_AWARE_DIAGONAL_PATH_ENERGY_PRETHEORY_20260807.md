# M143 output-aware diagonal path-energy proposal -- repaired pre-theory

## Decision state

**FIREWALL REPAIRED / RESPONSE OUTCOME STILL UNOPENED / SECOND INDEPENDENT
ROOT RE-AUDIT REQUIRED.**
M143 is a proposal-only child of M133.  It retains M131's exact sampled
`[2,1,1]` coefficient, M133's `1/(2Kq)` Hansen--Hurwitz weight, five batched
products, and `K=2n`.  The independent pre-execution audit correctly found
that the first draft conflated two proposal changes, had an ambiguous gate
index, silently floored zero strengths, and lacked a runnable frozen protocol
and native dtype trace.  A subsequent hostile audit accepted those repairs
but found a forgeable confirmation prerequisite and a reusable development
authorization.  Those two firewall defects are now also repaired before
opening any response result.

No contest model, truth, scorer, public/private outcome, leaderboard,
submission, or champion artifact was read or used.  The only executed target-
shaped cell is a fresh-synthetic float32 FlopScope structural trace; it has no
network response or score.

## Exact index map and path-energy sketch

Let `W[r]` map post-ReLU activation coordinates at layer `r` to pre-ReLU
coordinates at `r+1`.  Let

```text
p[r,a] = Phi(alpha[r+1,a])
```

be the Gaussian ReLU mean derivative *after* `W[r]`.  Define terminal energy
and the backward recurrence

```text
E[R+1] = 1,
G[r]   = p[r]^2 o E[r+1],
E[r]   = W[r]^2 G[r],
```

where squares and `o` are elementwise and the final expression is an ordinary
matrix--vector product.  The proposal API consumes only the cached `E[r]`:

```text
tau[r] = s[r] o sqrt(E[r]).
```

The direct helper is explicitly named
`output_aware_node_strength_from_gated_downstream_energy`; its third argument
must be `G[r]=p[r]^2 o E[r+1]`.  A test proves this path equals the cached API.

This recurrence is the exact analytically integrated second moment of a
*sign-scrambled mean-channel path sketch*.  If the terminal probe and every
hidden interface carry independent unit-variance Rademacher signs, then

```text
E[r,i] = E_(g,S)[(J_r(S) g)_i^2].
```

A terminal sign alone would retain coherent cross-path terms.  M143 does not
make that false claim, and it does not assert that `E` is the complete
mean/covariance M121 response adjoint.

## Composite ownership and physical source scale

M143 is explicitly a two-component composite:

1. a preserved M139 component,

```text
s[r,i] = sqrt( Var(ReLU(Z[r,i])) ),
```

computed from the same frozen Gaussian background, and

2. the new diagonal suffix energy `E[r,i]` above.

For `Z~N(mu,v)`, the implementation evaluates

```text
m1 = sqrt(v) phi(alpha) + mu Phi(alpha),
m2 = (mu^2+v) Phi(alpha) + mu sqrt(v) phi(alpha),
s  = sqrt(m2-m1^2).
```

Finite `mu` and strictly positive finite `v` are required.  A nonpositive or
nonfinite rectified variance fails closed; no scale floor is allowed.

The frozen attribution arm is

```text
tau_scale[r,i] = s[r,i] ||W[r,i,:]||_2.
```

Original M133 remains

```text
tau_M133[r,i] = ||W[r,i,:]||_2.
```

Thus the response protocol can separately measure the whole composite against
M133 and the incremental diagonal-suffix mechanism against `scale_only`.
The scale-only arm is diagnostic and cannot be selected or promoted alone.

## Proposal law, exact zeros, and unbiasedness

Put `S=abs(B-I)` for the frozen bridge.  For ordered distinct `(i,j,k)`,

```text
h(i,j,k) = tau_i^2 tau_j tau_k
           [S_ij S_ik + S_ij S_jk + S_ik S_jk],
q(i,j,k) = .95 h(i,j,k)/Z + .05/[n(n-1)(n-2)],
Z = sum_(ordered distinct) h.
```

If `Z=0`, `q` is exactly uniform.  Individual zero-strength units receive
exactly the uniform rescue mass.  The former `finfo.tiny` substitution has
been removed; enumerated tests verify the published zero-strength law.

Each proposal is deep-copied into read-only arrays and hashed before any exact
coefficient is constructed or any HH draw is made.  For every frozen `q>0`,

```text
E_q[ Delta_(ijk) F_(ijk)/(2q_(ijk)) ]
  = sum_(i,j<k) Delta_(ijk) F_(ijk).
```

`Delta` remains the M131 paired conditional-boundary coefficient and `F`
remains the M133 five-product feature.  M143 therefore changes sampling
variance, not coefficient bias.

## Invariance

For simultaneous hidden positive gauges

```text
W[r]' = D[r]^-1 W[r] D[r+1],
s[r]' = D[r] s[r],
```

the recursion gives `E[r]'=D[r]^-2 E[r]`, hence `tau[r]'=tau[r]`.  Simultaneous
layer permutations simply relabel `E`, `s`, bridge entries, and proposal
probabilities.  Tests now cover the whole three-map chain, including bridge
and selected proposal probabilities, rather than isolated rows only.

## Frozen response protocol and firewall

`run_m143_generated.py` is complete but inert without a separate root
authorization JSON bound to the manifest hash.  It freezes:

* `PCG64DXSM` with child keys containing split, family, width, cell seed,
  method, repetition, layer, and purpose;
* independent method draw streams (`common_random_numbers=false`);
* one immutable `q` snapshot per `(cell,layer,method)` before coefficient
  construction;
* M131 orders `32/48`, 24 series terms, and disagreement `<=4e-5`;
* exhaustive exact local `[2,1,1]` response as reference;
* complete M121 one-delay conversion and M125b generated coalescing as the
  shared diagnostic carrier, with no target-ready claim;
* 64 replicates and `K=2n`;
* 10,000 bootstrap resamples of paired `(cell,repetition)` MSE records; and
* unopened confirmation widths/seeds behind a second authorization and a
  hashed development result that passed every gate.

The authorization boundary is now machine-enforced.  Every development or
confirmation authorization binds candidate `M143`, exact split, current
manifest SHA-256, current runner SHA-256, the exact absolute output path, a
16--128 character nonce, its canonical identifier
`m143-SHA256(nonce)`, and the canonical absolute nonce-ledger receipt path.
The CLI rejects a relative or different output path.  Before constructing any
response, it exclusively creates the canonical receipt with
`O_CREAT|O_EXCL`; the same nonce/identifier therefore remains consumed after
a crash, output deletion, authorization-file change, or output-path change.
The output is also written with exclusive mode.  Every result records the
authorization-file absolute path and hash, identifier, nonce, split, bound
output, and exact receipt path and hash.

Confirmation has a separate one-shot authorization.  It additionally binds
the exact absolute development-result path and SHA-256 and exact absolute
development-authorization path and SHA-256.  Before confirmation can consume
its own receipt, the runner independently checks the development candidate,
split, current manifest, current runner, exact frozen `CONFIG`, exact
authorization provenance, and the exact canonical receipt payload.  It then
requires no protocol failures and exact coverage of both families, widths
`[5,6]`, seeds `[143701,143702]`, 64 repetitions, all three methods, every
cell, and every proposal-snapshot layer.  Pooled and per-family primary and
attribution summaries, bootstrap upper bounds, and width trends are recomputed
from the stored per-repetition records.  Claimed pass booleans never open
confirmation unless they exactly agree with that recomputation and every
predeclared gate passes.

Two development chain families are frozen to prevent the diagonal generator
from manufacturing apparent path predictability:

```text
diagonal: W=.82 I + .035 G,
iid_he:   W_ij ~ N(0,2/n), with no diagonal privilege.
```

The primary M143/M133 gate and the causal M143/scale-only attribution gate
must pass both pooled and separately in *each* family.  An M131 certification
failure in either family fails target extrapolation; it does not authorize a
seed retry or removal of that family.

The predeclared gates are

```text
primary M143/M133:
  pooled ratio <= .75,
  one-sided bootstrap upper-90 < .90,
  no adverse width trend;

attribution M143/scale_only:
  pooled ratio <= .90,
  one-sided bootstrap upper-90 < 1.00,
  no adverse width trend.
```

Every line applies pooled and within both chain families.  `scale_only/M133`
is report-only.

## Randomness and tangent scope

The sign-scrambled path energy is analytically integrated and adds no proposal
randomness.  HH draws use independent child streams after `q` is frozen.  No
draw, exact coefficient, or response may adapt its own proposal, so no two-
stage debiasing is needed.

The inherited frozen-q tangent is authorized only for source/background
tangents at fixed network weights:

```text
E_q0[ Delta_dot F/(2q0) ].
```

A weight tangent would require

```text
E_q0[(Delta_dot F + Delta F_dot)/(2q0)]
```

and is prohibited in M143 because `F_dot` is not implemented here.  Neither
case contains `qdot` or a score-function term.

## Float32 native structural trace and non-overlap crosswalk

Generated algebra remains float64.  The target proposal path is pinned to
float32 and was traced with FlopScope `0.10.0+np2.4.6` at
`n=256,L=31,K=512`.  The trace includes the `p^2` path recurrence, physical
source-scale strength, residual/weighted edge tables, all three bank
normalizers, target-sized centre/two-endpoint categorical scans, and exact
sampled-q gathers.

```text
native billed proposal structure       0.067900646B
native residual                         0.0135320001 s
25%-protected native proposal           0.084875808B
M133 complete protected K=512          94.940940240B
minus old protected proposal setup     -0.121896960B
plus protected M143 replacement         0.084875808B
complete non-overlap crosswalk         94.903919088B
```

M133's existing 100 ms / 10B whole-estimator wall reserve is retained.  The
standalone 13.5 ms proposal residual is below that reserve and is not added a
second time.  M133's carrier, hard edges, five products, exact-coefficient
reserve, buffer reserve, and wall reserve remain unchanged and nonoverlapping.
This is still a protected crosswalk, not a measured integrated target
estimator.

## Evidence and disposition

Twenty-one algebra/protocol-only tests pass: ten algebra invariants and eleven
protocol/firewall tests.  They cover the sign-scrambled identity, direct versus
cached `p^2` indexing, exact source and downstream gauge laws, permutation
covariance, physical source-scale definition, scale-only arm, exact
zero-strength behavior, immutable proposal snapshots, uniform fallback, cost
invariants, exact pooled-AND-per-family gate conjunction, strict uncertainty
thresholds, child-stream separation, and embedded dependency hashes.  The
hostile tests additionally reject stale manifest/runner/config identities,
noncanonical authorization IDs, a different output, nonce reuse after output
deletion or path change, a forged receipt payload, a hand-written asserted
pass with failing records, and missing family/record coverage.  A complete
fabricated passing fixture is accepted only after independent gate
recomputation.  These tests use temporary synthetic JSON and never call a
generated response cell.  The module, runner, and both test sources compile.

The repaired evidence hashes are:

| artifact | SHA-256 |
|---|---|
| hostile re-audit requiring this repair | `f3ad7b51699bc7792e1a9262d124a9357aed44456f13815e1132751f85770468` |
| manifest | `6338584fdf89813c6e6f0c2c46bc72ccbcb22b5d600a6766ba8d6bf319bce215` |
| M143 module | `5dab449d9ceff7099e04f4521415e781592e6eec260636dd4e81688c9dc6d9bb` |
| M143 runner | `1f0d31ec7e28d98cd84fc64fac3bc3a67293f6060d14f085f8f0005c92a9a81c` |
| proposal algebra tests | `e81cb683b61876f69efcdbc9ccd3d07ae090dc35f9d6a3c9a9bf342256b46b5d` |
| protocol/firewall tests | `8113e1c580272a8432d34862d4fb876d45980df4dcabafbf72f168bd52901f78` |
| trace script | `5e43d90af6d519e7deef29ba242ab53eb6f4ecfbd1d6a9c491495acc778e9a52` |
| stored structural trace | `1e63e4520863d368363a2d6c5c3b0f84f8438ba2aaa07202c9b5812ae0ade341` |
| cost crosswalk | `24a28714a8d1735ae0cf4261c5cc3a2d37fc3c17e8084fb13cd0722c623e7617` |

The branch remains **registered, not promoted**.  The next lawful action is
an independent second re-audit of the repaired hashes.  Only a clean PASS may
allow root to issue one canonical authorization for one development response
screen.  No confirmation, contest evaluation, champion replacement, or
submission is authorized.
