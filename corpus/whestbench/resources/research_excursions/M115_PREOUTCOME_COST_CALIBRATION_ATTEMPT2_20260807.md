# M115 pre-outcome cost calibration attempt 2 - 2026-08-07

## Status: COMPLETE_PENDING_INDEPENDENT_AUDIT

This is a pre-outcome, output-free calibration only.  The requested monotone
wall-proxy protocol completed and the unmodified runner accepted the stored
payload.  This record does **not** create or approve a frozen manifest or a
canonical M115 screen run; the independent audit must decide whether the proxy
is admissible.

## Attempt preservation

Attempt 1 remains intact, including its original REPAIR record and five trace
files, at:

```text
research_excursions/M115_PREOUTCOME_COST_ATTEMPT1_EVIDENCE_20260807/
```

The two valid global-lifecycle traces from the interrupted scalar-dispatch
attempt were also preserved, rather than deleted, at:

```text
research_excursions/M115_PREOUTCOME_COST_ATTEMPT2_PARTIAL_SCALAR_DISPATCH_20260807/
```

Only then was the fixed path recreated for this completed attempt:

```text
m115_projective_arc_nystrom_draft/EXTERNAL_M115_COST_EVIDENCE/  (14 files)
m115_projective_arc_nystrom_draft/EXTERNAL_M115_COST_CALIBRATION.json
```

## Frozen monotone wall-proxy protocol

The reusable builder is
`research_excursions/m115_cost_calibration_builder/measure_m115_cost.py`
(SHA-256 `378c469c35020b87773e87fdf8c00d3b360551b9cebe55f19765d774dfa70886`).
Before any attempt-2 rate was measured it fixed the primitive microbatch counts
by operation kind.  For each primitive signature (kind, dtype, operand shapes,
byte semantics, serialization direction, and artifact format), it performed:

1. one actual warm-up microbatch, not reported as a sample;
2. three actual `time.perf_counter_ns` microbatch timings;
3. division by the fixed microbatch count to form three real per-repetition
   rates; and
4. a conservative per-repetition envelope equal to the maximum raw rate.

Every trace runtime channel is the same frozen envelope multiplied by that
operation's exact contract repetition count.  This avoids favorable sample
selection.  Candidate, base L1, and equal-cost L1 records share a single
primitive-rate table within each network, making the L1 cost exactly affine in
whole frame count.  Exact NPY-bank bytes and actual NPY memmap / full-read /
SHA-256 operations were used for bank operations; lifecycle write, flush,
fsync, replace, and directory operations were real filesystem operations.

The raw samples, envelope derivation, primitive signatures, operation
microbatches, and every network's integer-frame proof are in:

```text
research_excursions/m115_cost_calibration_builder/
M115_ATTEMPT2_RAW_TIMING_PROVENANCE_20260807.json
SHA-256: 8e419a1d910b4a77407d399746109c674d8b52868e84222c761d9aabfb420f0b
```

The timing API is Python's documented high-resolution interval counter:
https://docs.python.org/3.12/library/time.html#time.perf_counter_ns .  QR uses
NumPy's documented QR API:
https://numpy.org/doc/2.3/reference/generated/numpy.linalg.qr.html .

## Pinned runtime and verification

Measurement and verification used the reviewed bundled Python 3.12.13 / NumPy
2.3.5 runtime with `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and
`MKL_NUM_THREADS=1`.

The builder tests passed after the final source change:

```text
test_measure_m115_cost.py
Ran 3 tests in 4.391s - OK
```

Then the unmodified runner accepted the stored payload through:

```python
runner._verify_cost_calibration_payload(
    payload,
    artifact_sha256=runner._sha256(runner.COST_CALIBRATION_PATH),
    evidence_dir=runner.COST_EVIDENCE_DIR,
    runtime_identity=runner._verify_runtime(),
)
```

Verification covered all 14 trace hashes and exact operation multisets (209
operation records); each record has three positive real-derived envelope
channels.  Raw provenance contains 114 primitive rate records, each with three
positive raw rate samples and an envelope equal to their maximum.

## Calibration result

```text
EXTERNAL_M115_COST_CALIBRATION.json
SHA-256: 82e927d8a54f2a61fcfe48e542a624038b3ba0cb50f2dde592be28f21d21ebb1

charged global lifecycle cost per candidate network: 39,195,280,468.00001
recomputed cost ratios: [2.5434341269313316, 2.994438216430221,
                         2.7404858033606083, 2.590790610053943]
equal-cost L1 frame counts: [127, 150, 137, 130]
```

For each network the provenance records `C_equal(f) <= C_candidate` and
`C_equal(f+1) > C_candidate` from the same frozen affine rate table:

```text
network  f    C_equal(f)       C_equal(f+1)     C_candidate
0        127  767,283,377,017.5 773,307,385,926.0 771,766,148,544.4998
1        150  856,619,574,413.0 862,313,979,571.5 859,939,947,919.4998
2        137  792,538,995,165.0 798,307,500,636.0 796,601,725,419.4999
3        130  809,447,970,618.0 815,656,547,964.0 810,300,290,419.4999
```

## Fixed evidence hashes

```text
base_0.json       9deec66dbc7b29afecc7678d3cd1fc39e06742f2e427f756f9f40aec0fa15696
base_1.json       dd406537147b9e5ab1d13ceb13f5177b56d9f63a7e09c115c0cc415f150aaa02
base_2.json       93b9fcf3f89ecad233d2ab9046a17de3c3c53f94cfe174f9baa957d9806d6499
base_3.json       8606f3d46416398010a3e6901ae21dc3d881720c05ca7b31055d7f428dee59ca
candidate_0.json  1c5977d356024d46ee8a6b3cd0ac2ff38932e68db0b12cb545fea2f9230b303d
candidate_1.json  2674fbb9493ebe350246ef34e2c6dde172eac16deca5cecc60fbe8c9c2f4bd0f
candidate_2.json  cf189481414a88eee2aeebe0a3f85cf33b4f5e203f55a7994f4a5a5646c6dd84
candidate_3.json  1b86b90e7edbce526be536d5b29de89a0f00c7048b0b0b65b5ac45e29e21bfad
equal_0.json      8a9db11c4143a3d3fc854f4960b626178475e9d04a4a731f4e96c26aa1f7e1b0
equal_1.json      10415f87d4ef968aedb6eb190bee2d77cb7fac5096b1d4feddd63e7fcf3f54fe
equal_2.json      69c0992205969328624016aa3fe142a22fc763c9bcf50a9ab6f1bcd63090a60a
equal_3.json      d5ab8ecee94d9ea3a2e87baed7c3485697ce47627dc433ac499f91f1125c6ec6
failure_lifecycle.json 70481c9f090ccdd52b84804e1fe2d4d1907e547a8f49ad8bb6264bfd86d4dc7a
success_lifecycle.json 898f5b2cfa3615c2c965af5e266236f88b76044efd85b1547f9c498a4650e0bc
```

## Forbidden-path status

```text
EXTERNAL_FROZEN_M115_MANIFEST.json                 absent
../m115_projective_arc_nystrom_one_shot_20260807/  absent
```

No one-shot API, future M115 seed, target, contest resource, canonical claim,
or output screen was invoked or generated.
