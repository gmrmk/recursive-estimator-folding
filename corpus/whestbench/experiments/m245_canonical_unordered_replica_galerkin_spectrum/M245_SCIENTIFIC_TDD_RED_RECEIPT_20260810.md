# M245 scientific four-lane RED receipt

Date: 2026-08-10

Status: `PASS_TEST_FIRST_FOUR_INDEPENDENT_MISSING_IMPLEMENTATION_REDS`.

This receipt freezes scientific test tissue only. It is not scientific
evidence, a shard trigger, a static-review verdict, a launch authorization, or
permission to evaluate any event in the frozen E00:E07 census.

## Bound authority at RED

```text
d4dc4a5d82006e2324de4a01aceabda14106ad13  repository HEAD observed before RED receipt publication
0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b  M245_FROZEN_MANIFEST_V2_20260810.json
2e56bd140b71527f640e1c1afbbc347fcca601fa4f0ec83f711c69a29e2b444e  M245_SHA256SUMS_V2_20260810.txt
```

The committed V2 and checksum had already received the two required
postpublication read-only PASS audits. The scientific sequence in section 12
therefore authorized tests-first work but no scientific implementation or
execution existed when these REDs were observed.

## Frozen test bytes

```text
223dcc0eae654adc663bd5a26e99da737da6caa8304b9a5bdd8525b9b84b5fe2  test_m245_primary_core.py
2fafd424836a388838ee912925cf24a332c881ffa07bef1cf29265f3291de44c  test_m245_replica_core.py
1933f16628650440883b1675af0ce1057543ded34fec12fca0700ccc9b9d0382  test_m245_scientific_transport.py
a8558becaf0c832347b758b585450527712583730ed3397b8cb79abea05a6ebe  test_m245_aggregation.py
```

Byte lengths at freeze were respectively `24757`, `17099`, `23005`, and
`13970`.

The suites independently freeze:

- primary V2/hash/API/analytic-math/numerical-gate/curve-ladder contracts;
- a separately implemented replica V2/hash/API/unary-factorization/agreement
  contract with a primary-import firewall;
- the exact four-shard, two-one-event-invocation namespace, S/L/W topology,
  immutable hard-link publication, resource caps, trigger, result, checkpoint,
  final-receipt, and lossless ordered per-`mp.quad` call ledger contracts; and
- stdlib-only four-PASS-receipt aggregation with no new quadrature, solve,
  transform, fit, event deletion, or relabeling.

All executable numerical examples in the frozen tests are named dummy cells
outside E00:E07. The committed V2 may be opened only for read-only byte/hash,
census, array-receipt, and shard-map validation; the tests forbid calling a
scientific evaluator on a V2 fixture outside its future shard intent.

## Interpreter and working directory

Exact interpreter:

```text
C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe
sha256=4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262
```

Exact working directory:

```text
C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m245_canonical_unordered_replica_galerkin_spectrum
```

Before the four commands, all five future implementation files were absent:

```text
m245_primary_core.py              absent
m245_replica_core.py              absent
run_m245_scientific_shard.py      absent
m245_scientific_worker.py         absent
aggregate_m245_spectrum.py        absent
```

## RED 1: missing primary core

UTC interval: `2026-08-10T03:44:58.1508908Z` through
`2026-08-10T03:44:58.5917725Z`.

Exact command:

```powershell
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_primary_core.py
```

Observed exit code `1`, `Ran 1 test in 0.000s`, `FAILED (errors=1)`, with
terminal cause:

```text
ModuleNotFoundError: No module named 'm245_primary_core'
```

## RED 2: missing independent replica core

UTC interval: `2026-08-10T03:45:04.1166238Z` through
`2026-08-10T03:45:04.2855443Z`.

Exact command:

```powershell
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_replica_core.py
```

Observed exit code `1`, `Ran 1 test in 0.000s`, `FAILED (errors=1)`, with
terminal cause:

```text
ModuleNotFoundError: No module named 'm245_replica_core'
```

## RED 3: missing shard supervisor/runner

UTC interval: `2026-08-10T03:45:09.6763582Z` through
`2026-08-10T03:45:09.8305403Z`.

Exact command:

```powershell
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_scientific_transport.py
```

Observed exit code `1`, `Ran 1 test in 0.000s`, `FAILED (errors=1)`, with
terminal cause:

```text
ModuleNotFoundError: No module named 'run_m245_scientific_shard'
```

The transport suite also freezes `m245_scientific_worker.py` as the sole
scientific W below the missing stdlib S; it was absent and was not imported
because S was missing first.

## RED 4: missing stdlib-only aggregation

UTC interval: `2026-08-10T03:45:14.9933965Z` through
`2026-08-10T03:45:15.1449273Z`.

Exact command:

```powershell
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_aggregation.py
```

Observed exit code `1`, `Ran 1 test in 0.000s`, `FAILED (errors=1)`, with
terminal cause:

```text
ModuleNotFoundError: No module named 'aggregate_m245_spectrum'
```

## Test-first boundary

Each RED failed at its first missing non-stdlib module import, before test
discovery could execute a test method. Thus these commands performed no M245
quadrature, Hermite evaluation, Galerkin construction, replica moment, curve
fit, fixture regeneration, frozen-event evaluation, shard intent, checkpoint,
result publication, aggregation, response, truth/scorer read, network access,
submission, or credit claim.

Implementation may now target these exact frozen test bytes in four separate
lanes. Before any shard trigger, the primary, replica, worker, supervisor,
aggregation, and all four test hashes must be frozen and independently audited
as required by sections 11 and 12. A GREEN test is still not a shard launch.
