# M116b B=2,048 harness repair: pre-execution re-audit package

Date: 2026-08-07  
Status: PASS_TO_REAUDIT — source and temporary-test evidence only; no campaign was executed.

## Scope boundary

This repair changes only the campaign harness, its frozen contract, and its
source-only tests. It does not modify `inplace_l3.py`, run a full prediction,
create the canonical campaign directory, create a claim, open any target or
contest material, or access a network. The canonical root is still absent:

~~~
work/scorefloor_generation/m116b_inplace_l3_draft/M116B_B2048_GENERATED_CAMPAIGN
~~~

The earlier harness report is superseded by this repair record.

## Full-prediction metered trace

The frozen full geometry is 64,512 rows by width 256 at depth 32, with
B=2,048. `state`, the 32 weights, and the L3 workspace are constructed before
`BudgetContext`. Inside that context the only source-level operations are 32
calls to `workspace.multiply_inplace(state, weight)` and 32
`fnp.maximum(state, 0.0, out=state)` ReLUs. W3 accounts for its own
copy/packing/folding work inside each call; there is no other source-level copy
or conversion in the metered region.

| metered component | derivation | exact bill / calls |
|---|---:|---:|
| one 64,512-row W3 hook | frozen audited dispatch | 5,912,804,352 bill; 32 matmul calls |
| 32 hooks | 32 × hook | 189,209,739,264 bill; 1,024 matmul calls |
| 32 in-place ReLUs | 32 × 64,512 × 256 elements | 528,482,304 bill; 32 calls |
| full context | hooks + ReLUs | 189,738,221,568 bill; 1,024 matmul calls |

The ReLU element billing was independently checked under the pinned FlopScope
runtime on a safe 512-by-256 `fnp.maximum(..., out=...)` probe: exactly
131,072 billed operations, i.e. one per element. The worker now emits its
observed `BudgetContext.flops_used` as `full_prediction_billed_flops` and its
observed accumulated W3 matmul count as `full_prediction_matmul_calls`. The
parent gates those two observed values exactly against the frozen totals; it
does not use the separately reported single-hook identity as the full-trace
gate. Regression tests reject both an omitted matmul call (1,023) and an
extra billed operation.

## Pre-claim sealing and durable lifecycle

The contract carries a normalized SHA-256 for `campaign_runner.py`. The
normalization replaces exactly one byte sequence: the value literal in
`EXPECTED_CONTRACT_SHA256`. It replaces no other field, comment, whitespace,
or line ending. The runner verifies that normalized SHA-256 in `load_contract`
before runtime verification and before the O_EXCL claim. This avoids only the
contract/runner hash cycle: once the contract is finalized its hash is inserted
into that excluded literal, while any other runner-byte change fails the
pre-claim self-seal.

The claim is written through a newly-created `O_CREAT|O_EXCL` descriptor,
flushed, and `fsync`'d before the child can be started. A failed file `fsync`
leaves the claim in place, consuming the run and prohibiting retry. Terminal
JSON is written to a unique pending file, flushed and `fsync`'d, then published
with `os.replace`; directory syncing is requested best-effort where Windows
permits it. Existing targets cannot be overwritten; an interrupted replace
leaves the pending name, which permanently prohibits a rewrite attempt.

Wall and residual gates are explicitly absolute, L3-only constraints:
`absolute_l3_only_no_direct_or_l2_comparator`. There is no timing comparator
against direct or L2 code.

## Frozen identities

| item | SHA-256 |
|---|---|
| `cost_model.py` | `c2d683adea20582d7d85a740f8109cbb83cb9ac2bc9351c4685f8985dab595ed` |
| `inplace_l3.py` | `114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83` |
| `campaign_contract.json` | `3c8e362177959a91f16d352eaaf3336e0f85af8985b986a7997f91a06457b734` |
| `campaign_runner.py` (raw) | `099ee36fd21d15ea2255828784cce606a4aa125710365f239cd8e18e39ad6775` |
| `campaign_runner.py` (normalized self-seal) | `05d516630d7e70b3c077e5ebe17d0542cdb4e0a2f80ed10766200d287370d21d` |
| `campaign_worker.py` | `19497a13551592725c8329b01e74fe9c4dc92ffc6b86ae18467b26cff21cefe1` |
| `test_campaign_harness.py` | `dd7729722b47cbef9cd0a5239568bb9f594d42ae91436eaf353392d0f2863c57` |
| `test_inplace_l3.py` | `25bf60c70e33fc4f0419f31dabe8f92d3154387c9a0893744ccbb8a851a98d0e` |

The contract retains the previously pinned Python 3.14.4, NumPy 2.4.6,
FlopScope 0.10.0+np2.4.6, package/executable hashes, NumPy build fingerprint,
and one-thread environment. Its child-worker hash and runner normalized
self-seal are checked before a claim.

## Source-only verification

Under the pinned runtime and all four required one-thread variables:

~~~
python -m unittest -v test_campaign_harness.py
15 tests passed
~~~

The suite covers exact full-trace gates, omitted/extra trace rejection,
normalized self-sealing, source/runtime drift, claim fsync interruption,
pending/duplicate terminal writes, temporary-root one-shot failure/success,
and no worker retry. It does not launch the full child.

With the thread variables deliberately absent (as required by that suite's
fail-closed environment test):

~~~
python -m unittest -v test_inplace_l3.py
11 tests passed
python -m py_compile cost_model.py inplace_l3.py test_inplace_l3.py \
    campaign_runner.py campaign_worker.py test_campaign_harness.py
passed
~~~

All actual campaign numerical, wall, residual, and peak outcomes remain
unmeasured and are not claimed as passed. The next permitted state is an
independent source re-audit, not execution.
