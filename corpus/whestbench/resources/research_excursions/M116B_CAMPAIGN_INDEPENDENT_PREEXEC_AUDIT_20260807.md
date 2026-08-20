# M116b B=2,048 campaign independent hostile pre-execution audit

Date: 2026-08-07  
Scope: `m116b_inplace_l3_draft` source/contract and allowed target-free
unit, mock, and bounded generated microprobes only. No campaign parent/child
permanent execution, no full 64,512-row one-shot, no canonical claim, no
contest outcome, target, scorer, public material, or champion was opened.

## Verdict: REPAIR — do not freeze or execute this campaign yet

The contract/source/runtime pins, generated microchecks, ownership design,
and temporary-root lifecycle tests are materially sound. However, the
full-run pass gate currently accepts a separately recomputed *static* hook
identity rather than requiring the actual full FlopScope bill and the observed
full per-hook call trace. In addition, the runnable parent bytes are recorded
in the claim but are not pre-bound by the contract before that claim. These
are integrity defects in a campaign whose purpose is to make the full runtime
measurement decisive. Repair and independently re-audit before freezing.

## Identity and prior-audit comparison

Current SHA-256 values (recomputed locally):

| file | SHA-256 |
|---|---|
| `m116b_inplace_l3_draft/campaign_contract.json` | `9e6bb8b1edb3882fd71c768aaff773366a5fa9792a62ad7c66f29192272a3819` |
| `m116b_inplace_l3_draft/campaign_runner.py` | `21a0f6c9156f3d50cfb6b5da2e5221533f7d85df96e6a9dbd95d20fb1509f68d` |
| `m116b_inplace_l3_draft/campaign_worker.py` | `893caf94fa890a24c685c0db8298d2554cf1d424500dbdd81f37a023170c4292` |
| `m116b_inplace_l3_draft/cost_model.py` | `c2d683adea20582d7d85a740f8109cbb83cb9ac2bc9351c4685f8985dab595ed` |
| `m116b_inplace_l3_draft/inplace_l3.py` | `114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83` |
| `m116b_inplace_l3_draft/test_campaign_harness.py` | `0ed19de185c2cdae7a1d5096910d658f68f0a477443fadf313c4c6afd118ca80` |
| `m116b_inplace_l3_draft/test_inplace_l3.py` | `25bf60c70e33fc4f0419f31dabe8f92d3154387c9a0893744ccbb8a851a98d0e` |

The contract hash equals the runner’s `EXPECTED_CONTRACT_SHA256`; its three
declared source hashes exactly match the present cost model, operator, and
worker. The contract pins Python, NumPy, NumPy build fingerprint, FlopScope,
and all four one-thread environment variables. Parent and child both call the
same runtime verifier; the pinned temporary/mock contract tests passed.

This is an improvement over the prior M116b pre-execution audit, which found
no runtime pin or campaign runner. The current B=2,048 builder report and the
prior audit’s arithmetic agree on the source/operator identities and
33.60546875-MiB owned-workspace ledger. That is not a whole-process peak
measurement; the required Windows parent/child measurement remains pending.

## Canonical lifecycle and claim state

At audit start and again after all allowed tests, the fixed root
`m116b_inplace_l3_draft/M116B_B2048_GENERATED_CAMPAIGN` did not exist. Thus no
canonical claim, result, failure ledger, terminal ledger, permanent child, or
full campaign currently exists.

`AtomicCampaignLifecycle.claim` uses `O_CREAT|O_EXCL`; the only public runner
uses the fixed canonical root; the worker rejects every noncanonical claim;
and the parent derives the worker token from exact claim bytes. Temporary-root
mock tests showed first-claim success, second-claim refusal, gate-failure
terminal evidence, and one worker invocation only. A parent/child crash after
the claim leaves the claim in place and therefore blocks retry.

Required hardening before freeze: fsync the claim file and directory after the
exclusive create, and write terminal records through an atomic replace. The
existing claim is a good logical no-retry sentinel, but it is not a durable
crash-persistence protocol as implemented.

## Exact bill and bounded generated probes

The cost model is internally and independently arithmetically consistent:

```text
W3(m,256,256) = 91,644*m + 666,624.
W3(m=64,512; k=n=256) = 91,644*64,512 + 666,624 = 5,912,804,352.
ceil(64,512/2,048) = 32 visible block/core calls per full-width hook.
```

The direct decomposition also agrees: leaf work is `5,576,159,232` and
pack/fold/right work is `336,645,120`, totaling `5,912,804,352`.

Allowed pinned, generated-only checks completed without creating a claim:

| probe | observed result | gate |
|---|---:|---|
| 512-row FlopScope | bill `47,588,352`, core/matmul calls `1`, rel-Fro `1.93824e-6` | pass |
| 2,048-row FlopScope | bill `188,353,536`, core/matmul calls `1`, rel-Fro `2.01006e-6` | pass |
| shallow 3,072 rows | bill `282,196,992`, calls `2`, rel-Fro `1.99491e-6`, returned-left/right/suffix all true | pass |
| depth-32, 512 rows | rel-Fro `6.32932e-6`, ReLU mismatch `1.43051e-6`, finite | pass |

The shallow and depth definitions are honest parity definitions: shallow uses
a direct `original @ right` reference and observes untouched future rows;
depth applies direct and in-place products before each ReLU and counts sign
mismatches of those preactivations. The latter is below the frozen `2e-4`
threshold. These probes do not establish full-forward wall, residual, or peak.

## Ownership, output shape, and peak boundary

`InplaceL3Winograd.multiply_inplace` accepts a writable C-contiguous float32
left matrix and returns that exact same object. It rejects overlap, non-float32
operands, bad shapes, and all unsupported/direct fallbacks before mutation.
It owns no full-height output; the ledger is exactly `35,237,888` bytes. The
worker’s full state is `(64,512,256)`, allocates 32 `(256,256)` weights, and
after each layer checks `returned is state`; this matches caller-left
replacement lifecycle rather than an out-of-place estimator API.

The worker should nevertheless report and gate `state.shape==(64_512,256)`,
float32 state/weights, and an `all_returned_left` boolean explicitly. They are
currently source facts, not full-run report fields.

The proposed peak mechanism is directionally correct for Windows: the parent
polls the spawned child PID with `OpenProcess`/`GetProcessMemoryInfo`, the
child reports monotonic `PeakWorkingSetSize`, and the result takes their
maximum over launch-through-exit. The child’s monotonic peak covers short
intervals missed by the parent’s 20-ms poll. No actual parent-child peak was
measured in this audit; `<=464 MiB` remains pending.

## Required repairs

**Critical — actual full accounting is not gated.** `_full_prediction` reports
`billed_flops` and `full_prediction_matmul_calls`, but `_gate_map` checks only
`full_hook_billed_flops` and `full_hook_matmul_calls` returned by a separate
static `dispatch(64_512,256,256)`. The static values are correct, but a
FlopScope trace/count discrepancy in the executed full forward can still pass.
Record each of the 32 layer-hook observations (or otherwise prove an exact
per-hook trace), and gate the actual billed count/call count against the
contract. If the intended total is the 32-layer sum, make that separate value
and gate explicit; do not conflate it with the per-hook `5,912,804,352 / 32`
identity.

**Critical — parent runner is not pre-bound before claim.** The contract binds
cost model/operator/worker and the runner hard-binds the contract hash. The
parent source hash is merely recorded in the claim after verification, so a
modified parent can create a claim under the unchanged contract. Add a
non-self-referential reviewed parent identity mechanism or explicitly freeze a
separate immutable launcher/manifest that verifies the runner before the
claim. Extend the tests to demonstrate rejection before root creation.

**Important — crash durability is weaker than the no-retry claim.** Add file
and directory flushes for the exclusive claim and atomic terminal writes; test
an interrupted/partial terminal state still rejects a second attempt.

**Important — timing comparison is not present.** The campaign measures L3
predict wall and FlopScope `residual_wall_time_s`; it executes no direct or L2
timed comparator. That is acceptable only if called an absolute frozen L3
wall/residual gate. Any claim of direct/L2/L3 timing superiority would be
unsupported and must be removed or measured under a separately predeclared,
honest equal-work/equal-process protocol.

## Test record

- Pinned temporary-root harness tests: 10/10 passed. They do not invoke the
  real child and cannot create the canonical root.
- Unpinned operator suite: 11/11 passed. It intentionally first asserts that
  a trace rejects absent thread pins, then patches them for its microtrace.
- A combined suite run with pins globally set produced one expected test
  failure: that negative missing-thread assertion no longer raises. This is a
  test-environment incompatibility, not an operator failure; the prescribed
  split runs above pass.

No full prediction, permanent runner, canonical claim, result, failure ledger,
contest access, or champion access occurred during this audit.
