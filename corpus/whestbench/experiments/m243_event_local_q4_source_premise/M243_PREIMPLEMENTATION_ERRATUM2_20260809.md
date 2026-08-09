# M243 preimplementation erratum 2 -- execution closure

Date: 2026-08-09

This second no-code erratum closes the remaining execution ambiguities found
by the independent implementation audit.  It was written before any M243
test, module, runner, result, or evidence run.  Authority order is the
original predeclaration, original manifest, erratum 1, V2 manifest, this
erratum, then the V3 manifest.

## X1. Reference ingestion and transitive source

Every generated binary64 fixture scalar enters mpmath as
`mp.mpf(repr(float(value)))`.  SciPy is absent and forbidden.

M147's transitive M129 source is frozen at

```text
corpus/whestbench/experiments/m129_source_frechet_tangent/m129_source_frechet.py
sha256=b7b9d4b0228331972f7fd7b5bd2fb6081ba3053d25daf64f3f8dd0f84e31a6bf
```

## X2. G0A ownership fixture

Only the generated width-5 cell supplies the G0A source-ownership fixture.
After that cell's frozen `A`, diagonal, covariance, and mean draws have been
consumed in the exact order already declared, draw

```text
W = rng.normal(0,1/sqrt(6),size=(5,6)).
```

For events `(0,1,2)` and `(4,0,1)`, require bitwise singleton-swap parity of
M151 `source_feature_211`, flatten `aaaa,aaab,aabb` in C order, and verify
that multiplying by `Z/(2q)` uses the owner factor exactly once.  The
collision parser must refuse `(0,0,0)`, `(0,0,1)`, `(0,1,1)`, and the
four-distinct label tuple `(0,1,2,3)` without evaluating a pair jet.

## X3. Binding candidate ABI

The smallest allowed G0A module surface is

```text
M243DomainRefusal
Q4Packet(beta[5], repeated_R[5], beta_radius[5], base_jet_contained, ...)
q4_packet(state,i,j,k)
conditional_centered_pair(state,i,j,k,g)
folded_distinct_event(state,labels4,g,degree=None|2|4)
```

`degree=None` is raw, `degree=2` is Q2, and `degree=4` is Q4.  The parser
accepts only strict `[2,1,1]`, canonicalizes the two singleton labels without
changing owner multiplicity, and returns typed refusals elsewhere.  Candidate
code may import M147/M178/M151/M133 but not mpmath, SciPy, M213 event values,
or M216 event values.  The pure-mpmath reference is a separate runner.

## X4. G0B quadrature agreement

For ANTI, Q2, and Q4, exploit their exact evenness in the base normal draw and
integrate directly on `[0,+inf)` with half-normal density `2phi(g)`.  Add
`abs(alpha_i)` to the sorted positive panel set

```text
0,.25,1,2.5,5,8,10,16,+inf.
```

For RAW1, RAW2, and the ideal mean reference, use the full panel convention
from erratum 1.  STRAT2 uses its two explicit truncated-normal components.
At both 80 and 100 dps, integrate `mu_Q` and the already-centered integrand
`(Z_Q-mu_Q)^2` directly.  The two precisions must agree within
`2e-9*(1+abs(reference))` for every mean, variance, and bias contribution.
No `E[Z^2]-E[Z]^2`, clipping, alternate panels, or retry is permitted.

## X5. Frozen G0B sharding delegated to Fable

The 256 long event-oracle units are split into exactly four immutable shards:

```text
shard 0: P0 sampled occurrence indices   0..63
shard 1: P0 sampled occurrence indices  64..127
shard 2: P1 sampled occurrence indices   0..63
shard 3: P1 sampled occurrence indices  64..127.
```

All 128 proposal draws for a cell are materialized and hashed before any shard
starts.  A shard may cache unique events only inside itself.  A duplicate in
another shard is recomputed; no cross-shard hidden state or cost credit is
allowed.

Each shard has exactly one authorized launch, a 5400-second wall cap, and a
2048-MiB peak-RSS cap.  It writes one canonical JSON receipt through the
already-audited write-ahead durable publication helper.  The receipt contains
authority hashes, sampled-manifest hash, shard id, ordered occurrence range,
unique/total counts, 80/100 values, actual-M178 and ideal arms, calls, wall,
RSS, and completion flags.  A timeout, missing unit, partial receipt, or
second intent is failure.

After all four receipts exist, one Codex-owned aggregation launch of at most
300 seconds and 2048 MiB verifies hashes, reconstructs the original 128+128
occurrence order, performs the frozen bootstrap, and writes the sole aggregate
result.  Fable does not change thresholds or aggregate/adjudicate its own
receipts.  If G0A has not passed, no shard intent may exist.

## X6. No-run boundary

After this erratum and V3 manifest, create an authority SHA-256 receipt and
commit only the M243 authority documents before any test/module.  Obtain a
second independent no-code audit.  Only a clean PASS authorizes the
missing-module RED.

