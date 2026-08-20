# M175 — fixed B=8 labelled zero-order background/source ABI audit

## Disposition

**NO-GO IN CURRENT CODE — exact labelled producer absent.**  M175 changes
only the interface/liveness mechanism identified by M174: replace M169's
unlawful all-31 precondition with four fixed consecutive blocks `[8,8,8,7]`.
The intended schedule is lawful in principle, but no current code can produce
its required immutable block bundle without changing the mathematical
semantics or crossing an unmetered boundary.  No integration runner, native
trace, resource pass, efficacy call, or candidate promotion is created.

No response, truth, scorer, leaderboard, submission, champion, or outcome
artifact was read or changed.

## Frozen mechanism and required ABI

For a block of layers `l=a..b`, the only allowed dependency order is:

```text
zero-order (mu,V) transition using W_l only
  -> retain immutable BackgroundEntry[l] =
       {layer=l, W_l, mu_l, V_l, J_(l+1), source_slot_owner}
  -> M163 compile from exactly (W_l,V_l)
  -> explicit Source211 -> TangentState conversion at its declared layer
  -> M125b carrier transition through its declared next layer
  -> release all block-local materialization after last consumer
```

The frozen blocks are `[1..8]`, `[9..16]`, `[17..24]`, `[25..31]`.  `V_l`
is always the zero-order covariance state; the signed `TangentState`
covariance may never be projected, clipped, or fed back into that recurrence.
`W_l` is the immutable model weight with cast provenance.  `mu_l` is the
matching zero-order post-ReLU mean.  `J_(l+1)` is the complete M125b local
Jacobian that maps a post-layer-`l` tangent through the next affine/ReLU.

This is a design contract, not an implementation claim: its source-owner
field must name an algebraic formula, not merely say “M163 output”.

## First broken link: no exact metered BackgroundArchive producer

The production base remains diagonal-only.  It advances `var`, so it cannot
produce a single full `V_l`.

The only target-shaped full-covariance code is
`fullcov_gaussian_mm/estimator.py`.  It overwrites one `covariance` state and
returns stacked means only; it neither retains `V_l` nor constructs any M125b
`LocalReluJacobian`.  More importantly, it is not semantically interchangeable
with the required exact background: it floors variances at `1e-24`, clips
correlations to `[-1+1e-12,1-1e-12]`, and evaluates the bivariate CDF through
the explicitly named fixed ten-node `_phi2_gauss10` approximation.  Reusing
it would silently replace the exact/no-clipping M163 domain and the exact
M125b Jacobian premise by a different numerical closure.

Writing a new background loop would not be a mere archive wrapper.  It must
define and meter the complete noncentral bivariate ReLU moments and every
derivative block (`p,r,K,Hmu,Hv`) at all 31 layers, pin their endpoint policy,
preserve casts/rounding, and prove their relation to `V_l`.  No such producer
exists in the frozen path.  Therefore this is the first broken link.

## Independent second break: Source211 is not a TangentState

M163 produces the contracted fourth-order source slots

```text
Source211 = (aaaa: R^256, aaab: R^(256x256), aabb: R^(256x256)).
```

M125b consumes a post-ReLU first-order tangent

```text
TangentState = (mean: R^256, covariance: Sym(256)).
```

These share shapes only partially; their meanings, normalization, injection
layer, and carrier ownership are different.  M163 has no `TangentState`,
`LocalReluJacobian`, or conversion function.  M125b has neither `Source211`
nor a source-slot conversion interface; it accepts unlabelled Python lists of
already-constructed sources, weights, and Jacobians using ordinary NumPy.
Thus no lawful conversion is implied by memory layout or shape.  Any cast or
reinterpretation would be an unproved semantic change, not ABI plumbing.

The necessary repair is an independently verified, layer-labelled formula
for each M163 source slot's contribution to `(b_l,B_l)` plus an exact
ownership subtraction against all M172 physical owners.  This is distinct
from the background-producer repair and is not attempted here.

## Fixed B=8 liveness, conditional only

If both missing interfaces existed, fixed blocks reduce the largest M169
workspace to `85.52151489257812 MiB`.  The retained current-block f64 `V`
archive is `4 MiB`; 31 raw f32 immutable model weights occupy `7.75 MiB`.
M169 would issue two batched matmuls per block, hence eight dispatches total;
its pack arithmetic across all blocks remains `32,505,856` billed FLOPs.

Those numbers deliberately exclude the absent exact background work, local
Jacobian arrays, source conversion buffers, source-provider data, M125b
carrier, Python/BLAS overhead, and a target-shaped wall trace.  They are not
a `<512 MiB` proof and cannot inherit M169's all-stack p99 result.  M175 does
not claim a safe `C`, RSS, or wall margin.

## Salvage and next causal mutation

Preserve the B=8 dependency schedule, the zero-order/source separation, and
the M169 independent-product packing layout.  The all-31 staging application
remains blocked; no conclusion is drawn about M163 algebra, M172 ownership,
or M125b carrier linearity.

The next permissible mutation must address exactly one first link: build a
fully labelled, FlopScope-metered *exact* BackgroundArchive/Jacobian producer
with a declared endpoint policy and target-shaped integration trace.  It must
not also invent the Source211-to-TangentState conversion.  Only after that
passes can the second, separately audited conversion mutation open.
