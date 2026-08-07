# M115 pre-outcome cost calibration - 2026-08-07

## Verdict: REPAIR

No calibration artifact was published because the runner's frozen equal-cost
L1 comparator gate failed on the first real candidate network.  This document
is an evidence-preserving stop record, not a manifest or an execution
authorization.

## Exact blocker

All five retained traces are hash-valid under
`run_m115_generated_only._verify_trace`, but network 0 has no accepted
equal-cost record from the measured attempt:

```text
candidate effective cost                         706,569,200,264.0
dominant global failure lifecycle cost            27,792,690,468.0
candidate plus global target                     734,361,890,732.0
base L1(50) effective cost                       260,281,577,938.0
measured equal-cost L1(136) effective cost       710,933,534,694.0
unspent target cost                               23,428,356,038.0
one-frame average incremental cost                 5,240,139,032.05
```

The equal trace is below target but leaves more than one affordable
increment: `23,428,356,038.0 >= 5,240,139,032.05`.  The runner therefore
rejects it.  A prior real 139-frame probe was over target, so this was not
resolved by inventing a fractional frame, mutating a timing, or cherry-picking
samples.  The builder stopped before network 1, and before writing
`EXTERNAL_M115_COST_CALIBRATION.json`.

Repair requires a reviewed, deterministic comparator-calibration method that
can satisfy the runner's strict whole-frame equal-cost inequality under three
real timing samples.  Do not create a manifest or screen run until that method
is reviewed and the full four-network calibration validates.

## Retained, runner-validated pre-outcome traces

```text
EXTERNAL_M115_COST_EVIDENCE/success_lifecycle.json
644f00ae46c3d9d4c193a5d0b64b38f7b6b2f9b4ed8e8d10505b9442ad133fe0
frames=0 effective_cost=12,055,770,106.0

EXTERNAL_M115_COST_EVIDENCE/failure_lifecycle.json
ac924aa5482f730cde5fbf76e9994ab7c45064079978649cdd7f78a2c2bdaf73
frames=0 effective_cost=27,792,690,468.000004

EXTERNAL_M115_COST_EVIDENCE/candidate_0.json
fe0bf5e6adb1988ef22883ac82f135d23830d164a023b63e32819d26296fedcd
frames=50 effective_cost=706,569,200,264.0

EXTERNAL_M115_COST_EVIDENCE/base_0.json
c42e1af255909164d538baf480f8d40aa6126397d536a2d1098bfe93f9e944a8
frames=50 effective_cost=260,281,577,938.0

EXTERNAL_M115_COST_EVIDENCE/equal_0.json
44996b0b5257cfa81847b820bd170acf14463cf2eea2ccc85fb301523198d4ce
frames=136 effective_cost=710,933,534,694.0
```

The evidence directory is intentionally incomplete (5 of the required 14
fixed trace files) and must not be presented as a completed calibration.

## Measurement method and provenance

The reusable builder is
`research_excursions/m115_cost_calibration_builder/measure_m115_cost.py`
(SHA-256 `73be8e41acc95d2bef056961baaec49bc07bc37b076210816d6f6942f19888f8`).
It ran under the reviewed bundled Python 3.12.13 / NumPy 2.3.5 runtime with
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and `MKL_NUM_THREADS=1`.

For every record it attempted, the three samples were real
`time.perf_counter_ns` intervals around the declared contract's full
repetition count.  Matrix products used NumPy `@`; QR used `numpy.linalg.qr`;
copies and elementwise work used ndarray copy / `np.maximum`; scalar work used
the corresponding `math.fsum` contractions or `np.linalg.solve`; file bank
work used exact-shape float64 NPY memmaps, full byte reads, and SHA-256;
lifecycle work used real `mkdir`, exclusive temp create, exact-byte writes,
flush, fsync, and replace.  All buffers were disposable calibration buffers
from a separate calibration seed root, not M115 future weights or target data.

The timer choice follows Python's documented high-resolution interval counter:
https://docs.python.org/3.12/library/time.html#time.perf_counter_ns .  The QR
operation follows NumPy's documented QR factorization API:
https://numpy.org/doc/2.3/reference/generated/numpy.linalg.qr.html .

The builder test passed after its aggregate-rounding repair:

```text
test_measure_m115_cost.py
Ran 1 test in 4.786s - OK
```

## Forbidden-path status at stop

```text
EXTERNAL_FROZEN_M115_MANIFEST.json                 absent
EXTERNAL_M115_COST_CALIBRATION.json                absent
../m115_projective_arc_nystrom_one_shot_20260807/  absent
```

No M115 one-shot API was invoked.  No future M115 weights, target, contest
resource, canonical claim directory, or output screen was generated.
