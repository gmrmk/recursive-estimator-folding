# M116b B=2048 second independent pre-execution audit

Date: 2026-08-07  
Scope: repaired `m116b_inplace_l3_draft` only. This audit read its contract,
runner, worker, cost model, operator, tests, earlier hostile audit, and repair
report. It ran only target-free unit/mock checks and the existing 512-row
generated microprobe. It did **not** create the canonical root, claim, result,
failure/terminal ledger, permanent child, or full 64,512-row/depth-32 campaign.
It did not open contest/public/scorer/champion/target material.

## Verdict: PASS_TO_FREEZE

The two defects in the first hostile audit are repaired at the source and
contract boundary. This is a pass to freeze the harness for later separately
authorized one-shot execution, not a pass of any numerical, wall, residual, or
whole-child peak gate. Those gates remain unobserved.

## Recomputed identities

| Item | SHA-256 |
|---|---|
| `campaign_contract.json` | `3c8e362177959a91f16d352eaaf3336e0f85af8985b986a7997f91a06457b734` |
| `campaign_runner.py` raw | `099ee36fd21d15ea2255828784cce606a4aa125710365f239cd8e18e39ad6775` |
| runner normalized self-seal | `05d516630d7e70b3c077e5ebe17d0542cdb4e0a2f80ed10766200d287370d21d` |
| `campaign_worker.py` | `19497a13551592725c8329b01e74fe9c4dc92ffc6b86ae18467b26cff21cefe1` |
| `cost_model.py` | `c2d683adea20582d7d85a740f8109cbb83cb9ac2bc9351c4685f8985dab595ed` |
| `inplace_l3.py` | `114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83` |
| `test_campaign_harness.py` | `dd7729722b47cbef9cd0a5239568bb9f594d42ae91436eaf353392d0f2863c57` |
| `test_inplace_l3.py` | `25bf60c70e33fc4f0419f31dabe8f92d3154387c9a0893744ccbb8a851a98d0e` |

The runtime verifier also matched the frozen executable, Python 3.14.4, NumPy
2.4.6 plus initializer/build hashes, FlopScope 0.10.0+np2.4.6 plus initializer
hash, and all four required one-thread variables. Source hash, runtime, or
contract drift rejects before the claim.

## Self-seal and binding: PASS

`normalized_runner_sha256` substitutes exactly one match of the byte pattern
for the `EXPECTED_CONTRACT_SHA256` assignment. A second matching literal causes
normalization failure. A temporary copy with only that 64-hex value changed
retained the required normalized digest. A same-length change to
`CANONICAL_RUN_ROOT` failed `verify_runner_self_identity` before any claim
could be created. Thus the allowed exclusion closes only the contract/runner
cycle; every other runner byte is authenticated by the contract.

The contract also binds exactly `cost_model.py`, `inplace_l3.py`, and
`campaign_worker.py`; the runner verifies those hashes and the runtime before
constructing `AtomicCampaignLifecycle` or calling `claim`.

## Observed-trace gate design: PASS (future observation remains pending)

The worker constructs its state, 32 float32 weights, and workspace before the
full `BudgetContext`. Inside it the source loop contains exactly one
`multiply_inplace` and one `fnp.maximum(..., out=state)` per weight. The sealed
cost model gives 32 W3 hooks x 32 batched matmul calls = **1,024** actual
matmul calls. Its future observed `context.flops_used` must equal:

```text
32 * 5,912,804,352 + 32 * 64,512 * 256 = 189,738,221,568.
```

The parent gates the child-emitted observed bill and accumulated matmul calls
directly against those two frozen values. It does not substitute the static
single-hook field for the full gate. Target-free mock tests reject 1,023 calls
and 189,738,221,569 billed operations. The worker contract test independently
checks 32 ReLUs, their 528,482,304 billed elements, and the total. No actual
full trace was observed in this audit, so this verifies a fail-closed future
gate rather than reporting a result.

## Lifecycle, firewall, and absolute gates: PASS

The canonical root was absent before and after testing. There is no CLI path;
the source-only `main` raises, and worker authorization is derived from the
exclusive claim bytes. The dispatcher has only executable `l3_inplace` and
otherwise fails closed; the return is the caller-left alias. Seeds are fixed
in the contract for 512/2048 micro, shallow, depth-32, and full prediction.

Claim creation uses `O_CREAT|O_EXCL`, then write/flush/file-fsync and
best-effort directory sync. An injected claim-fsync interruption leaves the
claim present and a second claim is permanently refused. Terminal evidence is
created under a unique pending name, write/flush/file-fsync'd, then
`os.replace`d; duplicate terminal paths are rejected. An injected replace
interruption leaves the pending file and permanently prohibits a retry. These
properties are exercised only under temporary roots.

The contract’s exact absolute L3-only gates remain correctly expressed:
micro bills 47,588,352 (512) and 188,353,536 (2,048); shallow relative
Frobenius <=3e-6 with alias/suffix/right conditions; depth-32 relative
Frobenius <=2e-5 and ReLU mismatch <=2e-4; full parent/child peak <=464 MiB;
predict wall <20 s; residual <=.170 s. No direct/L2 timing comparator exists
or is implied. The child report contains the full-process peak source and the
parent takes the maximum parent/child peak under the declared lifetime scope.

## Target-free execution record

- Pinned harness suite: `15` tests passed, including self-seal, source/runtime
  drift, exact/full trace omission-extra rejection, O_EXCL/fsync/atomic
  lifecycle, temporary-root one-shot behavior, and a real generated 512-row
  microprobe.
- Unpinned operator suite: `11` tests passed, including exact 512/2,048
  cost-model bills, alias/ownership, 2,048+1,024 shallow semantics, and no
  fallback. Its generated FlopScope trace is the allowed 512-row trace; this
  audit did not add a separate live 2,048-row trace.
- `py_compile` passed for contract-bearing modules and tests.
- Independent temporary-copy drift check passed; canonical root remained
  absent.

## Limit

This audit is not evidence that the frozen full child will meet numerical,
whole-child peak, wall, residual, or budget gates. The next action, if
authorized by the campaign owner, is exactly one permanent generated-only
campaign invocation; a failure consumes the claim and may not be retried.
