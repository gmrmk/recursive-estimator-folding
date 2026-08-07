# M113 Independent Result Judge — 2026-08-07

## Verdict: KILL

The frozen, generated-only M113 one-shot is a durable failure.  The fixed
Hermite-tail source-stability gate compared degree 16 against degree 18 and
raised `RuntimeError` with relative Frobenius drift
`3.7176320441102146`.  The predeclared maximum is `0.05`; the observed value
is `74.352640882204292` times the threshold (absolute excess
`3.6676320441102146`).  Under the frozen decision rule, any gate failure is a
kill, with `retry_allowed: false`.

This is a private, target-free artifact audit.  I did not rerun the experiment,
invoke the runner or its validation routine, modify source/claim/failure
artifacts, browse, access a leaderboard, upload, submit, or edit a champion.

## Artifact identity and frozen-source verification

SHA-256 values recomputed from the current bytes:

| Artifact | SHA-256 |
| --- | --- |
| `m113_matrixfree_vertex_draft/FROZEN_SOURCE_MANIFEST.json` | `c977018f050fbad98f9b60a929bc690d9e3b4800d3b39004d24c2760f0b6d62b` |
| `m113_matrixfree_vertex_draft/M113_ONE_SHOT_CLAIM.json` | `a4cc3105546ef672aabd0e8a4f6d30cbc528c1d3f2815ed245572ac6935ecd75` |
| `m113_matrixfree_vertex_draft/m113_generated_only_one_shot_evidence/M113_ONE_SHOT_FAILURE.json` | `e941c554acc25c0c8f3b934e7211d6a71cd6324e4e134aac82a1a62b00d9a222` |

All eight entries in the frozen manifest match their recomputed SHA-256
digests exactly:

| Frozen file | SHA-256 |
| --- | --- |
| `CONFIG.json` | `80a54bf3001716ba7928558b6feb438bd0f26df2a81779a683f1999f9b99c121` |
| `INVENTORY.md` | `6befcefb0651c5fe474f4b51e63315f97ac0a16e81a4387ccb42100ccae37c31` |
| `REFERENCE_AND_PROTOCOL.md` | `8bc4971cf49cc30aee416f5fd0bf0b53e551b84642f45be7304984ccccc432f4` |
| `m113_matrixfree_vertex.py` | `2464ae36c1396f9884340f34778b60eaf86934acaa82ac50ec063f7b0ca28e29` |
| `run_m113_one_shot.py` | `7146f0c009c2c66c82651edddc219a5fcdf313cdfe951bdcda963495312cc62c` |
| `run_target_free_tests.py` | `fa1cbd12fe58bc6b9b9a89d92ec7713f6f6c0139c2fe86c668efb1eb58645cbd` |
| `test_m113_core.py` | `ec72d1550229ce753dc7e0b7731a009fb32da40a4b61915f9e433c5730ca185c` |
| `test_m113_runner.py` | `8ea3a2651f906f5bf83ecb2d8d90ab7441e6169a984ab0cb0fa98971df04a46d` |

The manifest states `frozen_preexecution_pass_m113`, with theorem and cost
judges both `pass`, and binds Python `3.12.13` and NumPy `2.3.5`.  The claim
records that same manifest digest and resolves solely to the fixed evidence
directory.  The hash-verified runner requires both manifest and observed
runtime to equal exactly that Python/NumPy pair before it creates the claim;
it also requires the manifest's exact eight-file inventory and hashes.

## Gate and output audit

`CONFIG.json` fixes `reference_total_edge_degree: 18`,
`reference_tail_comparison_total_edge_degree: 16`, and
`degree16_to_degree18_reference_relative_drift_maximum: 0.05`.  The
hash-verified runner constructs the degree-18 reference and degree-16
comparison, computes their relative Frobenius error, and raises before any
success serialization when it exceeds that bound.  The failure record names
precisely that exception and its traceback locates the raise at runner line
374.

The claimed, fixed evidence directory contains exactly one file:
`M113_ONE_SHOT_FAILURE.json` (1,169 bytes; digest shown above).  There is no
`M113_ONE_SHOT_RESULT.json` or `m113_generated_only_arrays.npz` in the M113
draft, and none under `work/scorefloor_generation`.  This is not selective
omission: in the frozen runner the Hermite check precedes the only array write
and precedes the only success-result write.  Therefore neither a success JSON
nor arrays could be produced on this failure path.  The failure JSON itself
was written by the caught exception path.

## One-shot permanence

The claim exists, has status `started`, is bound to the fixed manifest digest
and fixed evidence directory, and is retained after failure.  The runner
creates that claim atomically before creating the destination; an existing
destination or claim rejects subsequent calls.  The hash-verified test suite
also contains the explicit synthetic failure case asserting that a worker
exception leaves the claim and blocks a second destination.  Together with
the frozen config's `retry_allowed: false`, this prevents a retry of this
attempt.

## Residual uncertainty

This audit establishes the present artifact chain and the frozen code path;
it does not independently re-execute the numerical calculation.  Because
failure occurs before the normal result serializer, the failure artifact has
no separate runtime-attestation field.  Actual runtime conformance is instead
supported indirectly by the hash-verified runner's pre-claim exact-version
checks and the claim/failure sequence.  There is no contrary artifact in the
fixed output path.  This residual limitation does not alter the KILL verdict:
the durable recorded failure is far above the declared gate and cannot be
retried under the frozen protocol.
