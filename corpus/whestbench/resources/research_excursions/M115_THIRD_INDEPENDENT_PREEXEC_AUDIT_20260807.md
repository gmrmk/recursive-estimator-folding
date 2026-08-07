# M115 third independent pre-execution audit - 2026-08-07

## Verdict: PASS_TO_FREEZE

This is a fresh source-only re-audit of
`m115_projective_arc_nystrom_draft`.  It did not create a manifest,
cost-calibration/evidence artifact, canonical claim, or generated run.

## Prior blocker repaired

The previous independent audit's lifecycle undercharge is repaired and the
repair is fail-closed:

- The success global trace has exactly two `mkdir` operations, exactly five
  durable artifacts (claim, raw NPZ, events, result, terminal ledger), five
  serialize-write operations, and six artifact-hash read repetitions.
- Each artifact operation fixes its filename, serialization format, byte rule,
  byte charge, direction, repetitions, allocation, and copy count.  The trace
  verifier requires the exact operation-label multiset, exact record schema,
  recomputed bills/totals, and a hash of every external trace file.
- Raw NPZ (1,025,434 bytes) and phase events (868 bytes) are exact layouts.
  Variable JSON artifacts are bounded before writing by their frozen structural
  byte ceilings, and those same source-fixed ceilings are charged.
- The failure reserve has the same two mkdirs, all six possible durable
  artifacts (including failure), two full atomic cycles for every
  temp/create/write/flush/fsync/replace operation, and a separate
  `failure_reserve_bank_terminal_rehash` with four repetitions.  It dominates
  success, including a failed terminal-ledger attempt followed by the
  failure-ledger path.
- Candidate records charge the four NPY banks independently for write, three
  hash-read passes, and evaluator read.  The verified totals are 104,858,112
  bytes for four physical banks, three times that for normal bank hashing, and
  one time for evaluator reads.  The failure trace adds the source-fixed
  four-bank terminal rehash.
- The global cost is `max(success_lifecycle, failure_lifecycle)` and is added
  in full to *each* candidate network before every candidate/base ratio.  It
  is not amortized across four networks.

## Remaining freeze gates verified

- Runtime gate pins Python 3.12.13, the reviewed bundled executable and NumPy
  2.3.5 module path, build fingerprint, and one-thread BLAS/OMP/MKL
  environment.  It also rejects a shadowed core import.
- The manifest, when eventually supplied externally, must bind the exact
  nine-file source surface by SHA-256 and must bind the exact canonical path,
  frozen schedule, no-retry policy, and hashed calibration artifact.
- The four literal weight seeds and all 204 literal landmark/evaluation seeds
  are unique and independent of weights.  There is no data loader, network
  client, scorer, target, champion access, output-directory argument, or
  manifest-path argument in the runner.
- The mathematical control retains its conditional exact-zero identity:
  `E[(H(U)^T c)^2 / (c^T M c) - 1] = 0`, followed by the antipodal average.
  The implementation rejects nonpositive denominators rather than flooring or
  resampling.  It checks the analytic diagonal, PSD, endpoint separation,
  dual arc-cosine agreement, propagated per-landmark drift bounds, and uses
  Decimal only as a stated regression rather than an extrapolated runtime
  proof.
- Cross-fitting is one row per complete Haar frame, with 40 training and 10
  held frames per fold, training-only uncentered RMS, no intercept, and no
  held normalization.  The all-four precheck barrier precedes every deep
  evaluator; decision boundaries are strict and every non-pass is terminal
  with no retry.

## Executed source-only gate

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
C:\Users\strid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe run_target_free_tests.py
Ran 46 tests in 6.646s — OK
```

## Audited source hashes

```text
CONFIG.json                         57131152b7c247fb843b2a97ba3187f021ab25ece0df387d6dc52839cf4d85bd
INVENTORY.md                        a443cd42b3bee3c5d5dd5540e348d4df963fa8c6cde5df5e9e49fe774a4d1cf0
REFERENCE_AND_PROTOCOL.md           6b0d0dd2c6b5bed605ce9f63d971964efd1e27b97272b6ebc8160469bc2e8152
m115_projective_arc_nystrom.py      d19d3e744d183d71b0f40f65050f7794b49467bb2a05f7f6fcaebb24e2bae189
run_m115_generated_only.py          ce4d622b368dd928886b24c47dc9de8125dc46097f39fa07825ec04ae2c7bc5b
run_target_free_tests.py            d9ff643701a32a9dfc1440c30d7d203fd16d0c3363a0dcc7406f213d3a4f7a63
test_m115_core.py                   eb4b71c4da8eb001fda40bcd0d182222a14552358973d35061080606782a6b93
test_m115_protocol.py               5c2a0ea16493b4f38be874555e0de224fd8ede0762bb0dd16e3db5d59297af20
test_m115_runner.py                 98e5dc1d11e89fdec52f6f5bb07ac5e3063a9db2585f1cb877a31c69e51f28ff
```

## Forbidden-path absence, before and after source tests

```text
EXTERNAL_FROZEN_M115_MANIFEST.json                  absent
EXTERNAL_M115_COST_CALIBRATION.json                 absent
EXTERNAL_M115_COST_EVIDENCE/                        absent
../m115_projective_arc_nystrom_one_shot_20260807/   absent
```

The source is authorized to proceed only to external freeze.  This verdict is
not an execution authorization and does not substitute for the missing,
separately reviewed external manifest and hashed pre-outcome calibration.
