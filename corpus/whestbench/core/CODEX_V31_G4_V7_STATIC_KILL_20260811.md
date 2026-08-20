# V31-G4 v7 static promotion kill (2026-08-11)

Status: **KILLED AS A PROMOTION CANDIDATE BY ITS SEALED GATE**. Preserve the
passing grouped-kernel component as engineering evidence. This is not a claim
that the child violates the contest's official memory ceiling.

## Bound objects

- Proposal:
  `CODEX_V31_G4_EXACT_CALL_FUSION_PROPOSAL_20260811.md`, SHA-256
  `77EED01B6A7EF002BED93B4B81A0F2C7F9499B3A0395D5820A70728B50B9A326`.
- Source/evidence commit: `d87db78d8b29dfb08e6bdaa4b6cb6c7d7712ea44`.
- Preexecution manifest v7: SHA-256
  `F1F04CCD5858BA3A1BC93851CCF64324B4DDA5F1E93A98BBB00CB2FB8722182C`.
- Parent: immutable Kerdock v3.1 GUARDS archive SHA-256
  `8382E269C9B32E0935492734DDF8182560120F7E9331621AA18839D5D1F4EA06`.

The v7 component remains a valid `COMPONENT_SYNTHETIC_PASS_ONLY`: 25/25 tests
passed in both module orders, production-row parent/child output words and
analytical bills matched on the sealed even and odd-tail cases, and L1 wrapper
calls fell from 16 to 5 (32 to 10 including odd tails). None of that overrides
the proposal's resource and score gates.

## Decisive resource contradiction

The proposal itself fixes these simultaneously retained workspaces:

```text
parent row-blocked workspace       19,349,504 bytes
G4 grouped workspace               63,438,848 bytes
increment                          44,089,344 bytes
increment in MiB                   42.046875 MiB
```

The parent allocates the same `64,512 x 256` float32 activation
(`66,060,288` bytes) inside prediction. The child moves that allocation into
setup and binds it permanently; it does not remove a predict-time live object.
The child's grouped left/product banks are simultaneously live during each
grouped contraction, and the bound activation/views persist after return. No
teardown or phase-exclusive replacement compensates for the additional
`44,089,344` bytes.

This directly contradicts the proposal's literal promotion condition:

> no regression on worst-case wall, simultaneous RSS, cleanup, or return.

The proposal's own projected peak is about `494.738 MiB`, versus the committed
`452.691 MiB` unmodified-core receipt. Existing retained-ballast receipts show
near-one-for-one working-set increases, supporting the lifetime result. An OS
RSS receipt is not algebraically identical to array bytes, but the sealed
protocol gives no promotion credit without a source-lifetime proof, and current
source proves a larger simultaneously live footprint with no offset.

This is a **self-gate kill**, not an official 64-GiB legality failure. Replacing
"no regression" with "below 512 MiB" after seeing the v7 evidence would define
a new child and requires a fresh pre-evidence identity.

## Score-law consequence under the pinned Phase-1 runtime

Under WHestBench 0.14.0 and FlopScope 0.10.0,

```text
C = F + 1e11 * residual
residual = wall - trusted-backend time - timed FlopScope-wrapper overhead
```

V31-G4 leaves `F` and the estimator output unchanged. NumPy/BLAS time and the
timed FlopScope wrapper body are excluded from residual. The only possible
score gain is an unmeasured reduction in participant Python outside those
timers: outer loop/slice/view work, argument construction, and tiny wrapper
prefixes before the FlopScope timer starts. Moving `fnp.empty` to setup does not
itself lower the metered residual and worsens lifetime.

The proposal independently kills on a nonmaterial official-score effect. No
score-bearing gain has been measured, and Phase-2 scoring is not yet bound.

## Disposition

1. Do not run a generated-network or hosted promotion panel for this sealed
   V31-G4 identity.
2. Preserve commit `d87db78` as exact grouped-kernel engineering evidence.
3. GUARDS remains the sole integrated candidate.
4. A memory-cap rather than no-regression variant is a new child, not a repair
   to this result.
5. The analytical-bill-saving V5-d3 family remains separately gated and does
   not inherit V31-G4 evidence.

No generated network, truth, scorer, hosted endpoint, selection, or submission
was touched to reach this static disposition.
