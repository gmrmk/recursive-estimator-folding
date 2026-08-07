# M116c B=4096 hostile independent pre-execution audit — 2026-08-07

## Verdict: `REPAIR`

The B=4096 source, accounting, runtime seal, unit tests, and bounded operator
checks are internally consistent.  It is genuinely distinct from the consumed
M116b B=2048 identity, and the M116b evidence remains intact.  However, the
draft is **not freeze-safe**: its claimed execution authorization is a public
Python module global, `campaign_runner.EXECUTION_TOKEN`.  Any importer can
call
`run_authorized_generated_campaign(campaign_runner.EXECUTION_TOKEN)` and
thereby create the canonical root and launch the full campaign.  The CLI
refusal is therefore not a non-forgeable execution boundary.

No repair was made in this audit.  No final manifest, M116c canonical root,
claim, terminal artifact, full 64,512-row/depth-32 campaign, public/contest
data access, scorer, target, or champion access was created or used.

## Scope and unchanged M116b evidence

M116b remains a separate, consumed identity:
`M116B_B2048_GENERATED_20260807`.  Its canonical directory contains all three
terminal artifacts, unchanged:

- `M116B_B2048_CLAIM.json`
- `M116B_B2048_FAILURE.json`
- `M116B_B2048_TERMINAL.json`

Every file listed in M116b's frozen manifest re-hashed to its frozen SHA-256,
including its contract, runner, worker, cost model, operator, and both test
files.  This establishes that the B=2048 artifacts were neither altered nor
deleted by the B=4096 draft/audit.

M116c has a separate directory, run identity
`M116C_B4096_GENERATED_20260807`, contract hash
`e33904248e2b03d8df5452c85325644429e8f973334c0f679c425cb8a3c80a23`,
output-root name `M116C_B4096_GENERATED_CAMPAIGN`, and new seed set:

```text
micro_512=116900     micro_4096=116904
shallow=116907       depth32=116932
full_prediction=116964512
```

The M116c canonical root was absent before the audit, after source/unit
checks, and after the bounded microcheck.  No M116c `*MANIFEST*` file exists.

## Source, contract, and runtime seals

The independently recomputed source hashes agree with the M116c contract:

| item | SHA-256 |
|---|---|
| cost model | `ee1d0dc3f9f15239cc7561c6437545c5c316f8148d9b70060217488428c6a2e3` |
| in-place operator | `114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83` |
| worker | `fb57b77643bc779f6fc283ee08b5d4f3f083dd857c8d8f62074d3ad88df237f4` |
| runner raw bytes | `590a22409a3a92a6f5982ebd9997e547b61d48466b2d775fd932d6dbf0b80682` |
| normalized runner self-seal | `b413aa4c76dd519ad8726c445985d3e6f85f07968f2c7a0cc8169f7aafbe7787` |

`campaign_runner.load_contract()` verifies the contract raw hash literal and
the normalized runner self-seal.  It then verifies all three contracted source
hashes.  The pinned Python executable/version/hash, NumPy version/path/build
fingerprint, FlopScope version/path/hash, and four one-thread environment
variables exactly matched the contract.

The contract fixes `generated_only=true` and `retry_allowed=false`.  The child
constructs only fresh local float32 arrays and fixed-seed depth-32 weights; no
network client library is imported by the parent.  Temporary-root tests verify
exclusive claim creation, fsync-interruption consumption, non-overwriting
terminal writes, and prohibition of a second claim/retry.

## B=4096 executable and independent accounting

`BLOCK_ROWS` is `4096` in the cost model and is imported by every actual
operator allocation and iteration boundary.  The independently expanded
ledger and the real dispatcher agree:

| row count | executable strategy | core calls | billed FLOPs |
|---:|---|---:|---:|
| 512 | `l3_inplace` | 1 | 47,588,352 |
| 4,096 | `l3_inplace` | 1 | 376,040,448 |
| 64,512 | `l3_inplace` | 16 | 5,912,804,352 |

Unsupported shapes fail before mutation; the code returns no direct or L2
fallback under an L3 label.  `multiply_inplace` returns the caller-left alias,
checks writable C-contiguous f32 storage and non-overlap with all owned
buffers, captures the full left hierarchy before overwriting a block, and does
not own a full-height output.

The exact owned workspace is independently reproduced by allocations and the
formula:

```text
row banks:   3,976 * 4,096 = 16,285,696 f32 elements
right banks:                   666,624 f32 elements
total:                      16,952,320 f32 elements
workspace:                 67,809,280 bytes = 64.66796875 MiB
```

For 32 layers, the static full trace is exact:

```text
16 hook matmul calls/layer * 32 = 512 matmul calls
32 ReLUs * 64,512 * 256        = 528,482,304 billed elements
32 * 5,912,804,352 + ReLUs     = 189,738,221,568 billed FLOPs
```

The worker's static `full_prediction_trace_contract` and the contract both
produce these values.  The later parent gate compares actual metered total and
actual counted calls to these exact values.

## Bounded checks actually run

Only source, temporary-root lifecycle tests, and bounded probes were run under
the pinned one-thread WHest runtime:

- `py_compile` passed for every contract-bearing module and test.
- `python -m unittest test_inplace_l3.py test_campaign_harness.py` passed:
  **26 tests**.  Lifecycle tests monkey-patch the canonical root to a temporary
  directory; static inspection finds every test call to the full-campaign
  function inside such a patch.  Tests therefore cannot create the real root.
- A generated 4,096-row operator microcheck, with no canonical root, yielded
  exactly one L3 core/matmul call and `376,040,448` billed FLOPs; it returned
  the same left object, was finite, preserved the right input, and had relative
  Frobenius error `1.9649163152480837e-06` (below `3e-6`).

No full prediction, whole-process peak, prediction wall, or residual was
observed.  Those remain future one-shot gates:

```text
full finite/numerical gates: shallow <=3e-6; depth-32 <=2e-5;
  ReLU mismatch <=2e-4
parent/child peak <=464 MiB
prediction wall <20 s
absolute L3 residual <=0.170 s
```

The adverse, unmeasured forecast is correctly stated in `PRETHEORY.md`:

```text
0.6105131132062525 s * (512 / 1024) = 0.30525655660312625 s,
```

which remains above the residual gate and gives no success presumption.

## Blocking authority defect

The runner's `main()` rejects CLI use, and the child requires a claim-derived
hash.  Those facts are insufficient: `EXECUTION_TOKEN = object()` is exported
at module scope, and the full entry point accepts precisely that object by
identity.  A caller importing the module can retrieve the object and call the
entry point directly.  The test suite itself demonstrates this call shape while
redirecting the root to temporary storage.

Consequently, this audit has **no execution authority**, and the real root is
absent, but the source does not enforce the intended absence of authority for
other importers.  Before any freeze, repair must make the full-campaign trigger
unavailable from the checked-in source or require a genuinely external,
owner-controlled authorization mechanism.  That repair must be independently
re-audited with no M116c canonical-root creation.
