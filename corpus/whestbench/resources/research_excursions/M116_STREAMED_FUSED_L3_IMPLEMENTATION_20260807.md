# M116 streamed fused L3 cleanroom repair implementation

Date: 2026-08-07  
Scope: isolated generated-only resource/parity falsifier. No benchmark row,
target, truth, scorer, public telemetry, evaluation network, archive, manifest,
or one-shot campaign was opened, created, or run.

## Outcome

The REPAIR-stage source is implemented under
`work/scorefloor_generation/m116_streamed_l3_draft/`. It is additive and does
not import, modify, or package any prior operator. It reimplements the
previously audited Winograd identities in a new source file with a fixed
`BLOCK_ROWS = 2048` contract.

Readiness verdict: **READY FOR INDEPENDENT PREEXECUTION AUDIT, NOT READY FOR
ONE-SHOT EXECUTION.** The cheap target-free unit suite and a small FlopScope
trace pass. An independent auditor must still inspect the source hashes,
frozen configuration, whole-process peak, depth-32 parity, and residual wall
before a manifest or permanent campaign claim is authorized.

## Implemented surface

| file | role |
|---|---|
| `cost_model.py` | exact direct/L1/L2/L3 bills, shape-only minimum dispatcher, and independent streamed L3 expansion |
| `streamed_l3.py` | owned 343-leaf Winograd bank, explicit three-level pack/fold, allocation/alias ledger, diagnostics, and optional FlopScope trace |
| `lifecycle.py` | atomic, draft-directory-fixed `M116_ONE_SHOT_CLAIM.json` claim primitive; it is defined but not invoked |
| `test_streamed_l3.py` | generated-only parity, bill, dispatcher, ownership, primitive, lifecycle, and tracing tests |

The operator owns a full output, outer/middle reuse scratch, a leaf-left bank,
a leaf-product bank, and three distinct right banks. Its hot path uses only
explicit `copyto`, `add`, `subtract`, and `matmul(..., out=...)` operations.
An AST test rejects attribute calls named `stack`, `concatenate`, or `reshape`.

The only intentional storage reuse is temporal:

```text
middle-left storage -> middle products (after the leaf matmul)
outer-left storage  -> outer products  (after the middle fold)
```

The output and every right/leaf bank are separately owned. `ownership_ok`
checks that no owned buffer aliases either input or another owned buffer.

## Exact static resource and billing contracts

For a complete 256-square L3 core, the independent formula is

```text
W3(m, k, n) = 343*D(m/8,k/8,n/8) + 651*(m*k + k*n + m*n)/64,
D(m,k,n) = m*n*(2*k - 1).
```

The fixed row-partition expansion separately sums all leaves, each of the
three left packs, each of the three folds, and the once-only three-level right
pack. The dispatcher compares direct, L1, L2, and L3 only when their full
dimensions divide by 2, 4, or 8 respectively. It never pads or forms an L3
tail: shapes ineligible for L3 downgrade, and odd output width dispatches
direct.

Known checks:

```text
W3(2048,256,256)  =   188,353,536 FLOPs
W3(64512,256,256) = 5,912,804,352 FLOPs, 32 core calls
workspace(2048)   =    37,335,040 bytes
workspace(64512)  =   101,298,176 bytes = 96.60546875 MiB
```

`expected_workspace_bytes` computes the latter ledger without allocating the
full 64,512-row buffer. The full geometry remains a theory/preexecution
resource check; it was not executed.

## FlopScope and generated probes

`trace_generated_probe` is deliberately fail-closed:

* it requires FlopScope to import; it raises `RuntimeError` instead of
  silently using NumPy when it cannot;
* it requires all four thread controls (`OPENBLAS_NUM_THREADS`,
  `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS`) to be exactly
  `1`;
* it creates only a deterministic generated float32 256-square probe;
* it reports the chosen strategy, core/matmul count, and observed billed
  FLOPs.

The local cheap 512-row generated trace observed exactly the static L3 bill
`47,588,352`; this is an accounting microcheck, not a timing or full-liveness
claim.

## Verification performed

Executed with the local WHest/FlopScope Python runtime:

```text
work/whest-v014/Scripts/python.exe -m unittest test_streamed_l3.py
work/whest-v014/Scripts/python.exe -m py_compile cost_model.py lifecycle.py streamed_l3.py test_streamed_l3.py
```

Result: `13` tests passed. The tests are deterministic and generated-only;
they cover a profitable 512-row dense L3 product, a full 2048-row target tile,
static full-shape call/bill expansion, L3-to-L1 downgrade, odd-output direct
dispatch, memory ledger, source primitive prohibition, buffer ownership,
fixed-path one-shot exclusion, pinning, numerical diagnostics, and the cheap
FlopScope bill trace.

No permanent `M116_ONE_SHOT_CLAIM.json` exists in the draft directory, and no
frozen manifest was created. The lifecycle primitive is present solely so a
later explicitly authorized campaign has one atomic, non-retry claim path.

## Audit handoff

An independent preexecution audit should first confirm the formula and actual
FlopScope primitive trace at block boundaries, verify the only legal buffer
reuse points, and decide whether the `2.40625 MiB` inferred full-geometry
margin is sufficient. It must predeclare any process-peak, depth-parity, and
residual-wall gates before running the full generated campaign. Failure of any
one of those gates kills this exact source/configuration; no block-height
retuning is authorized.
