# M116b B=2,048 generated-only campaign harness (superseded)

Date: 2026-08-07  
Status: SUPERSEDED_BY_REPAIR; see `M116B_B2048_GENERATED_CAMPAIGN_HARNESS_REPAIR_20260807.md`.

## Scope and result

This change builds the future generated-only B=2,048 campaign harness without
changing the audited operator. It did not create the fixed campaign directory,
claim/sentinel, result, failure ledger, or any permanent/full run. It did not
open champions, target rows, truths, scorers, public material, evaluation
networks, or a contest surface.

The canonical future root is:

~~~
work/scorefloor_generation/m116b_inplace_l3_draft/M116B_B2048_GENERATED_CAMPAIGN
~~~

It did not exist after source/test verification. A module CLI is deliberately
disabled. Only the later in-process owner-token entry point can create the
atomic fixed-root claim; this source build did not invoke it. Lifecycle tests
use temporary directories and a mocked child only.

## Frozen source and contract identities

| item | SHA-256 |
|---|---|
| m116b_inplace_l3_draft/cost_model.py | c2d683adea20582d7d85a740f8109cbb83cb9ac2bc9351c4685f8985dab595ed |
| m116b_inplace_l3_draft/inplace_l3.py | 114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83 |
| m116b_inplace_l3_draft/campaign_contract.json | 9e6bb8b1edb3882fd71c768aaff773366a5fa9792a62ad7c66f29192272a3819 |
| m116b_inplace_l3_draft/campaign_runner.py | 21a0f6c9156f3d50cfb6b5da2e5221533f7d85df96e6a9dbd95d20fb1509f68d |
| m116b_inplace_l3_draft/campaign_worker.py | 893caf94fa890a24c685c0db8298d2554cf1d424500dbdd81f37a023170c4292 |
| m116b_inplace_l3_draft/test_campaign_harness.py | 0ed19de185c2cdae7a1d5096910d658f68f0a477443fadf313c4c6afd118ca80 |
| audited operator test | 25bf60c70e33fc4f0419f31dabe8f92d3154387c9a0893744ccbb8a851a98d0e |

The runner hard-codes the contract SHA-256 above. The contract hashes the
audited cost model, audited operator, and child worker. The runner records its
own source SHA-256 and the contract SHA-256 in the claim/result, avoiding a
self-referential config-hash cycle while retaining a complete run identity.
Any contract change fails before the claim; any hashed core/worker source
change fails before the claim.

## Runtime pin

The contract requires this exact observed WHest runtime:

| component | required identity |
|---|---|
| Python | 3.14.4; work/whest-v014/Scripts/python.exe; SHA-256 4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262 |
| NumPy | 2.4.6; work/whest-v014/Lib/site-packages/numpy/__init__.py; SHA-256 65d5e777b6d662ba19cb80800bef3eb999eda7aee51eea62c308feabf679dba4 |
| NumPy build fingerprint | fb5905933699a015e02a1e6254a9fc5aadc4a81f4ed03878632d09370684d1e0 |
| FlopScope | 0.10.0+np2.4.6; work/whest-v014/Lib/site-packages/flopscope/__init__.py; SHA-256 f49c7b804649223c077505a3380a6fb2baa691e783564be433543fa0ae6f1b06 |
| threads | OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, NUMEXPR_NUM_THREADS=1 |

Both parent and child independently verify executable/package paths, versions,
hashes, the NumPy build fingerprint, and the four thread variables. A mismatch
fails before the child executes any generated work.

## Fixed generated-only protocol and gates

The only frozen geometry is float32, width 256, B=2,048, full rows 64,512,
and depth 32. Seeds are fixed: micro 512=116762, micro 2048=118298,
shallow 2,048+1,024=116207, depth-32=116320, and full prediction=11664512.
All data are generated locally with NumPy; the source has no network client,
external loader, or selectable output path.

| gate | required result |
|---|---:|
| full hook static dispatch | 5,912,804,352 billed operations and 32 batched matmul calls |
| FlopScope microchecks | exact bill/calls at 512 and 2,048 rows |
| shallow 2,048+1,024 probe | finite, returned-left identity, untouched future rows/right, relative Frobenius <=3e-6 |
| depth-32 512-row parity | finite, relative Frobenius <=2e-5, ReLU mismatch fraction <=2e-4 |
| parent-child Windows peak | <=464 MiB |
| full generated depth-32 forward | finite, zero failure, no retry, wall <20 s, residual <=0.170 s |

The child makes the two micro probes, the 3,072-row shallow tail probe, the
512-row depth-32 direct/in-place parity probe, and the full 64,512-row,
32-layer in-place forward. The latter reports per-hook static identity,
full-forward call count, FlopScope bill, finite state, wall, and residual.
No current result is asserted because the child was not launched.

## Lifecycle and Windows peak design

The parent verifies frozen identity before creating the fixed root. It writes
M116B_B2048_CLAIM.json with O_CREAT|O_EXCL and binds the run ID, contract hash,
source hashes, and runtime identity. It then derives a child authorization
from the exact claim bytes. The child accepts only that authorization and the
same fixed claim path. Any existing claim rejects the run permanently.

The parent launches the pinned Python child and uses Windows OpenProcess plus
PSAPI GetProcessMemoryInfo on its PID until exit. The report records:

- parent monitor PeakWorkingSetSize;
- child-reported PeakWorkingSetSize;
- their maximum as peak_working_set_mib;
- measurement scope parent_child_lifetime_setup_through_exit;
- monitor sample count and total child lifetime wall.

This boundary begins at child process launch, therefore includes runtime load,
generated setup/weights/workspace, all preflight probes, full prediction, and
lifecycle execution. On success, gate failure, or internal error the claimed
root receives a terminal ledger; no path retries the child.

## Source-only verification

The new contract/lifecycle/worker tests passed under the pinned runtime with
the required thread environment:

~~~
python -m unittest -v test_campaign_harness.py
10 tests passed
~~~

Those tests cover source/config hash drift, exact runtime drift, fixed B=2,048
gates, atomic claims, temporary-root success/failure terminal ledgers, no
retry, disabled CLI, claim-derived child authorization, and a real cheap
512-row FlopScope microprobe.

The original audited operator suite was run separately with the thread
variables deliberately absent because it asserts that an unpinned trace fails
before patching those variables itself:

~~~
python -m unittest -v test_inplace_l3.py
11 tests passed
python -m py_compile cost_model.py inplace_l3.py test_inplace_l3.py
                   campaign_runner.py campaign_worker.py test_campaign_harness.py
passed
~~~

This pre-repair record is retained for provenance only. The repaired harness
stops at PASS_TO_REAUDIT; all numerical, wall, residual, and peak gates remain
PENDING rather than passed.
