# M223 predeclaration — M179-fused streaming physical-owner packet

Status: **predeclared before code; generated-only seam prototype, not
integrated or promoted.**  M223 reads no truth, response, scorer, target,
weights outside generated tests, leaderboard, submission, or efficacy record.

## Exact single mechanism and the present seam limitation

Change exactly one mechanism: at an M179 off-diagonal SPD pair evaluation,
retain the *same object* returned by the one M178 call and the same endpoint
unary/boundary cache long enough to emit `(K4, K31, K22)` before the pair state
is retired.  `K31(i,j)` is directed, `K22(i,j)` symmetric, and `K4(i)` is the
univariate connected fourth cumulant.

The current M179 `pair_moments` owns and discards its local `M178Result` and
does not expose a fusion seam.  Core edits are forbidden for this mutation.
Therefore this folder may prove a seam-compatible **one-call prototype** only;
it must not call the old function and label the result reused.  A later native
caller must pass the object-identity and call-trace gate before any incremental
cost credit, M179 reuse, or architecture-C integration is claimed.

## Shared exact algebra

For each SPD pair, standardize M179's `(a_i,a_j,sigma_i,sigma_j,rho)` and call
M178 once, obtaining the object `J=(P,Da,Db,Dr)`.  Endpoint caches hold
`Phi(alpha)`, `phi(alpha)`, and raw unary positive-part moments through order
four.  The M179 pair bundle and the M220 boundary recurrence both consume that
same cache and **the identical `J` object**.  Owner algebra is M220 unchanged:
joint bases `J01,J02,J10,J20` retain the other orthant indicator; marginals
enter only in the connected conversion.

```
kappa4  = E[(X_+-m)^4] - 3 Var(X_+)^2
kappa31 = central31 - 3 Var(X_+) Cov(X_+,Y_+)
kappa22 = central22 - Var(X_+) Var(Y_+) - 2 Cov(X_+,Y_+)^2.
```

No tree is subtracted.  Thus this packet is a physical connected-owner packet,
not a K4/K31/K22 defect compiler or a collision residual proposal.

## Live ABI and retirement

`LayerPrecontext(layer, epoch, a, C, provenance)` owns the live generated
pre-ReLU arrays by reference—no copy is authorized.  It yields a packet with
the same context object, pair indices, layer, epoch, source object ids, and
one-use lease.  `consume(context)` requires object identity and matching
metadata, marks the packet retired, and rejects every duplicate or foreign
consume.  Completion closes the context and rejects later emission.  This is
a lifecycle assertion, not an all-pairs storage premise.

### Frozen selective event-local ABI

`FrozenOwnerSelection(layer, epoch, pair_indices, k4_indices)` is constructed
before a layer's M179 loop begins. It is immutable and only answers membership
for the identical live `LayerPrecontext`; it never derives, ranks, retunes, or
samples indices. When the existing pair loop reaches a selected pair, a future
native seam may emit and immediately consume the one shared-owner packet. A
selected `k4` index is emitted from M179's already-computed diagonal unary
cache, not by a new unary call. Unselected pairs/nodes emit no owner packet.

The prototype can test this ABI and its one-packet liveness, but cannot claim
that old M179 actually supplies the required jet/unary objects. With `E`
selected pair events its owner-arithmetic ceiling is `512*E`; the all-pair
`E=1,011,840` amount remains the conservative worst case below. Selection
contains no source coefficient, proposal law, response, or variance claim.

## Exactness and hostile gates

1. M179-field parity against `m179_relu_pair_assembly.pair_moments` on a
   frozen hostile SPD grid.
2. M220/M129 parity for raw and connected `(3,1)/(2,2)` owners on fixed and
   random nonzero-mean SPD cells.
3. `id(packet.m179_jet) == id(packet.owner_jet)` and exactly one M178 call per
   off-diagonal SPD packet.  A fake/refused/nonfinite jet is a typed refusal.
4. Swap maps the directed `K31(i,j)` to reverse orientation and preserves
   `K22`; positive diagonal gauge has degrees 4, `(3,1)`, `(2,2)`.
5. Rank-one/non-SPD refuses; exact variance-zero paths are not silently
   promoted as M179 fusion (M179 has separate direct limits).
6. Foreign context, epoch/pair substitution, stale precontext ids, duplicate
   consumption, and emission after close all fail closed.

## Cost, copies, allocation, and wall gates

M179's already-paid 4,048-FLOP M178 call is **zero incremental only after gate
3 succeeds at the native caller**.  The fused prototype must make no second
M178/Phi/phi invocation for owners.  The predeclared maximum owner arithmetic
increment is **512 charged FLOPs/SPD pair**, exclusive of already-paid M179
work.  For `31*256*255/2 = 1,011,840` unordered pair events, that ceiling is
**518,062,080 FLOPs (0.518062080B)**, below M214's unclaimed 6.824272176B but
not reserved against its other unknowns.

The target admission gate is a single generated 31-layer trace showing: exact
incremental FlopScope delta `<=512*1,011,840`; M178 delta exactly zero relative
to unfused M179; zero copies of `a,C` per packet; no all-pairs owner allocation;
bounded packet/stream allocation; and hostile-five wall delta converted at
`1e11 FLOPs/s`.  Until that native trace exists, copies/allocation/wall are
unknown and the incremental bill is **not credited**.

## Explicit non-claims

This does not repair M167/M205's producer-lifetime gap, M212/M213's collision
provider gate, M214's unknown DAG nodes, or M220's target FlopScope receipt.
It supplies no tree, source coefficient, M198 conversion, variance reduction,
score, or architecture-C pass.
