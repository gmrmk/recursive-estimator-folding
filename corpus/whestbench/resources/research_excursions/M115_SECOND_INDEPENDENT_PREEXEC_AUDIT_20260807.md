# M115 second independent preexecution audit — 2026-08-07

## Verdict: REPAIR

Do not freeze, create a manifest/calibration/evidence artifact, claim the
canonical directory, or run the generated screen.  The previous numerical and
operation-record blockers are substantially repaired, but the proposed
cost-calibration trace is still not an exact account of the real durable
success lifecycle.  This is a source-only repair disposition, not a rejection
of the projective arc-cosine control construction.

## Scope and preserved state

I independently read every checked-in source, protocol, inventory, runner,
and target-free test in `m115_projective_arc_nystrom_draft`, and compared the
repair against `M115_INDEPENDENT_PREEXEC_AUDIT_20260807.md`.  I did not read
any target, scorer, contest, champion, network, or release artifact; I did
not create a manifest, calibration, evidence directory, claim, or generated
network outcome.

Immediately before and after the test run, these paths were absent:

- `EXTERNAL_FROZEN_M115_MANIFEST.json`
- `EXTERNAL_M115_COST_CALIBRATION.json`
- `EXTERNAL_M115_COST_EVIDENCE/`
- sibling `m115_projective_arc_nystrom_one_shot_20260807/`

## What is now verified

### Exact operation schema and bank arithmetic — PASS, except lifecycle R1

`_verify_trace` requires an exact root and record-field schema, a unique
label multiset equal to the per-kind contract, the pinned runtime identity,
three finite wall samples per record, and independently recomputed bill,
allocation, copy, serialized-write, serialized-read, and runtime-vector
aggregates.  The contract derives matrix products from dtype and operand
shapes; derives QR, copy, elementwise, scalar, RNG, hash/read/write, flush,
fsync, and replace charges from the stated operation.  Extra, omitted, opaque,
inconsistent-bill, aggregate, runtime-identity, and fixed bank-byte records
are rejected.  No top-level charged multiplier is accepted.

The NPY bank arithmetic is exact and independently recomputed:

```text
one bank payload = 50 * 256 * 256 * 8 = 26,214,400 bytes
four payloads    = 104,857,600 bytes
four v1 headers  = 4 * 128 = 512 bytes
four NPY files   = 104,858,112 bytes
```

The runner creates a C-order `float64 (50,256,256)` NPY memmap, flushes it,
checks its exact 26,214,528-byte file size, hashes it before/after the barrier
as required, and reads it as the evaluator input.  The candidate contract
therefore correctly accounts for the 104,858,112-byte writes, three bank-hash
passes, and evaluator reads at the stated volumes.

### Numerical certificate — PASS

The Decimal 513-point grid is explicitly regression-only.  It is not used as
the runtime Gram-error bound.  Every actual cache construction instead:

- rejects every off-diagonal correlation at distance `<= 1e-10` from either
  endpoint;
- evaluates the arc-cosine kernel with independent acos and asin forms,
  rejecting disagreement above `3e-14`, then enlarges every observed-entry
  uncertainty by a frozen 64-ULP envelope;
- symmetrizes the moment, restores its analytic diagonal, and rejects a
  non-PSD eigenvalue audit;
- independently contracts each denominator with `math.fsum`, rejects the
  BLAS/compensated discrepancy, and propagates normalization, dot-product,
  dual-kernel, and ULP errors into a per-landmark mean-drift bound;
- fails closed when that bound exceeds `1e-9`, or if any zero/nonfinite
  denominator or near-endpoint correlation survives.

The identity/Hadamard Decimal fixture, exact `rho_256` factorial check, and
f32/f64 first-preactivation bridge remain useful regression checks, but no
longer stand in for the actual-entry runtime certificate.  The source also
correctly implements the exact-zero law, columns-as-first-layer axes,
antipodal averaging, positive gauge/hidden-permutation/coupled-rotation
invariance, complete-frame rows, five 40/10 folds, training-response-only
centering, raw-held mappings, fixed ridge, no feature centering/intercept/held
normalization, and the generated-only firewall.

## R1 — release blocker: atomic evidence trace is neither byte-derived nor a complete lifecycle multiset

The repaired schema is exact only relative to its contract.  The candidate
contract contains one `atomic_evidence_serialization`, one evidence hash read,
one fsync, and one replace *per network* (four of each overall).  Their byte
fields are intentionally `None` in the contract; `_verify_trace` accepts any
positive equal `element_count_per_repetition` and
`serialized_bytes_per_repetition`.  The target-free fixture demonstrates this
by supplying the arbitrary values `250000 + network_index`, not values derived
from an actual serialization.

That is insufficient for an operation-derived lifecycle.  A successful real
run executes at least five durable atomic artifact writes overall, not four:

1. `claim.json` before future weight generation;
2. raw `npz` evidence;
3. phase-events JSON;
4. result JSON;
5. terminal ledger JSON.

Each has a same-directory temp file, write, flush, fsync, and atomic replace.
The result also hashes raw evidence and phase events; the terminal ledger
hashes claim/raw/events/result and all four banks.  Thus the contract both
undercounts success-path temp/fsync/replace operations and permits arbitrary
evidence byte volumes/hashes unrelated to the actual JSON/NPZ serialization.
It also has no operation records for directory creation (`mkdir`) that begins
the claim and creates the bank directory.  Hashing a calibration trace cannot
repair omissions from its fixed operation multiset.

The current negative test covers a one-byte change to the *fixed* NPY record,
plus extra/omitted/aggregate/runtime tampering.  It does not establish the
required one-byte failure for evidence serialization: a coordinated change of
an atomic record's positive byte count, its recomputed bill, and its totals is
accepted, because there is no source-derived expected byte count.  It also
does not assert the actual five-artifact success multiset or its six evidence
hash reads (two for result construction and four in terminal enumeration).

### Required repair

Before a new audit, define the cost-trace operations from the fixed success
lifecycle, not an abstract reserve.  Give each claim/raw/event/result/ledger
artifact its own fixed label with its actual serialization format, exact byte
source (or a frozen, mechanically derived layout from the measured bytes),
temp write, flush, fsync, replace, and all subsequent hash reads.  Record the
two directory creations explicitly as zero-billed lifecycle actions.  Make
the verifier recompute the complete success-path multiset and bytes from that
artifact layout, and add tests that reject a one-byte evidence change even
when the record bill and totals are recomputed, as well as missing/extra
temp/flush/fsync/replace/hash records.

## Target-free validation

Only the target-free suite was run, under the pinned bundled Python with
`OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=MKL_NUM_THREADS=1`:

```text
C:\Users\strid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe run_target_free_tests.py
Ran 43 tests in 5.831s — OK
```

It includes runtime pinning, generated-only/no-client checks, claim/barrier
tests, numerical endpoint and Decimal-role tests, cross-fit/symmetry/exact-zero
tests, and the existing trace tamper tests.  Passing tests do not remove R1,
because their trace fixture itself relies on the unconstrained atomic counts.

## Reviewed source hashes

| File | SHA-256 |
|---|---|
| `CONFIG.json` | `57131152b7c247fb843b2a97ba3187f021ab25ece0df387d6dc52839cf4d85bd` |
| `INVENTORY.md` | `51724dc98553ab40590d6023c4aaac9f081fb88944657cadbb315963b039e001` |
| `REFERENCE_AND_PROTOCOL.md` | `9d8686d30417949e9fdec35344fc0bd7a1f5a2eb97fc03cf6c3f5c04cea7e285` |
| `m115_projective_arc_nystrom.py` | `d19d3e744d183d71b0f40f65050f7794b49467bb2a05f7f6fcaebb24e2bae189` |
| `run_m115_generated_only.py` | `5dc0a86d630ef2be5fd1b12a80d9a62c2f91870261af9c19279553b530900873` |
| `run_target_free_tests.py` | `d9ff643701a32a9dfc1440c30d7d203fd16d0c3363a0dcc7406f213d3a4f7a63` |
| `test_m115_core.py` | `eb4b71c4da8eb001fda40bcd0d182222a14552358973d35061080606782a6b93` |
| `test_m115_protocol.py` | `5c2a0ea16493b4f38be874555e0de224fd8ede0762bb0dd16e3db5d59297af20` |
| `test_m115_runner.py` | `2ddcfcff718d4745d75e6ad9aaf764bdaf28e7cf21634d8af6e0284156ba0ab8` |

