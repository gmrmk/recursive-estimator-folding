# M200 predeclaration: streaming M179 -> M198 -> M125b overlap fixture

Status: `PREDECLARED_NOT_EXECUTED`.

M199 ended `BLOCKED_OVERLAP`. M200 changes exactly one link: replace separate
archive/carrier construction with a response-free streaming harness that passes
one live M179 layer object directly into M198 and M125b. The Source211 packet is
a nonzero generated fixture with creation cost explicitly unknown. M200 cannot
claim provider, estimator, target cost, variance, MSE, or outcome credit.

## One changed mechanism

For generated square networks only:

```text
for ell in 1..L:
    layer = exact_m179_step(previous_background, W_ell)
    tangent = m125b_transport(tangent, W_ell, layer.J)  # ell > 1
    packet = fixture_source_bound_to(layer)             # provider UNKNOWN
    tangent += m198_delay_one(packet, layer)
    release ell-only buffers
```

The harness must not call M198's full `build_extended_background` helper after
an M179 step, retain a dense order-3 `distinct_211` table, or construct one
suffix state per source.

## Frozen generated screen

- widths `2..7`;
- depths `3,4,5,6`;
- two fixed Philox seeds per `(width, depth)`;
- float64 only;
- nonzero deterministic compact Source211 fixtures satisfying
  `aaaa == diag(aaab)` and symmetric `aabb`;
- a separate full-archive reference may be built only outside the measured
  streaming path.

## Frozen semantic gates

1. Streamed terminal tangent agrees with full-archive labelled M125b reference
   within `2e-12` in every mean/covariance entry.
2. Every M125b transport receives the exact Jacobian object emitted by that
   M179 layer; every M198 conversion receives the exact `a,C,mu` arrays emitted
   by the same layer. Copies are events, never aliases.
3. Every fixture packet is bound to the exact layer number, network/weight
   digest, weight object, and declared input-covariance object. Cross-layer
   substitution, weight substitution, covariance substitution, reorder,
   duplicate, and terminal reinjection fail closed.
4. Counts equal `L` background steps, `L` source packets/conversions/injections,
   `L-1` tangent transports, and one terminal record. M198 background rebuild
   count is exactly zero inside the stream.
5. The live-set audit retains only previous/current background, one tangent,
   one fixture packet, and current scratch. It retains no full archive and no
   dense rank-3 array.
6. The event ledger records operation name, dtype, shape, logical buffer ID,
   digest, birth/death order, alias/copy class, and whether native cost is
   measured or explicitly unknown.

Any gate failure kills this streaming ABI child while preserving M179, M198,
and M125b separately.

## Frozen disposition rules

- `STREAMING_SEMANTIC_PASS_NATIVE_COST_BLOCKED`: every semantic/liveness gate
  passes; all fixture/provider and unmetered M198 costs remain explicit.
- `KILLED_STREAMING_ALIAS_OR_PARITY`: any semantic/liveness/count gate fails.
- M200 can never return `COST_COHERENT_COMPONENT`, a variance pass, an
  estimator promotion, or a winning-entry claim.

## Firewall

No contest model, truth, response, scorer, leaderboard, submission, champion,
or private data may be accessed. No API or remote service is used.
