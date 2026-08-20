# M245 repaired scientific four-lane RED receipt V2

Date: 2026-08-10 UTC

Status: `PASS_REPAIRED_TEST_FIRST_FOUR_INDEPENDENT_MISSING_IMPLEMENTATION_REDS_V2`.

This receipt freezes repaired scientific test tissue only. It is not
scientific evidence, implementation authority, a GREEN result, a shard
trigger, a launch authorization, or permission to evaluate any frozen
`E00:E07` event.

## Authority and chronology

```text
979f7c35334ff0df09ad134255fddf23f944237f  repository HEAD and upstream at RED
dddd874b19c15396da8981b20db3aa260831e7cb  sealed V2 fixture-authority commit
0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b  M245_FROZEN_MANIFEST_V2_20260810.json
2e56bd140b71527f640e1c1afbbc347fcca601fa4f0ec83f711c69a29e2b444e  M245_SHA256SUMS_V2_20260810.txt
8641de9ec301ba402b87e50dd8c5e3322a6532313f1d603c54356a4137e21587  M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md
401629468b5ec1f2eb5447b650b10f27fb47ba7ce3af74c740a230feeefcceaf  M245_SHA256SUMS_V2_OVERLAY2_20260810.txt
5497b1397a62bbfb4f3be73a02f2b63872e01f2bd4795b77232e7c6c287beb85  M245_SCIENTIFIC_TDD_RED_RECEIPT_20260810.md
```

The first RED receipt preserves historical hash/output claims only. Its four
original untracked test bytes were overwritten before commit and are not
independently reconstructible. Erratum2 superseded their implementation
authorization, explicitly permitted adoption and completion of the
pre-existing provisional repair drafts only after commit `979f7c3`, and then
permitted one fresh missing-module RED per independently audited repaired
test.

The repaired tests were completed only after that authority commit. Exact
read-only hostile review then returned PASS for:

- primary and replica test hashes below, including the end-to-end asymmetric
  antithetic `mu_rep` control; and
- transport and aggregation test hashes below, including the exact
  `O->S->L->W` meter/witness, down-closed attempt, lossless event-union, and
  real first-containing Git authorization controls.

No repaired RED command ran before both reviews passed.

## Frozen repaired test bytes

```text
355820f372c0e0b7b466ed98f3db2a36b92142927c494406b3f5dbdb5c26d626  test_m245_primary_core.py  39898 bytes
e7eceb023b725badb06d59773b7813d2083d3dfd33fffa7fd35fcedf2055fa21  test_m245_replica_core.py  30542 bytes
112869bf75a127ae706dcc1346c070f128c15c74a125d1818646fbf46fd5294d  test_m245_scientific_transport.py  116873 bytes
6d723cde0a9784cc20bf0a41b25ab4599f8c103f1c3de04cba0d6e8b9336a4e6  test_m245_aggregation.py  59098 bytes
```

All four files passed static AST inspection and `git diff --check`. The two
independent hostile audits inspected source text only: they performed no
import, compilation, test, fixture evaluation, or scientific execution.

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

## Pre-RED absence census

Immediately before RED 1, all six production paths were absent:

```text
m245_primary_core.py                    absent
m245_replica_core.py                    absent
m245_scientific_worker.py               absent
run_m245_scientific_shard.py            absent
launch_m245_scientific_invocation.py    absent
aggregate_m245_spectrum.py              absent
```

All eight durable shard-intent paths under
`corpus/whestbench/experiments/m245_fable_spectrum_shards` were absent:

```text
M245_S0_I1_E00_INTENT_20260810.json  absent
M245_S0_I2_E01_INTENT_20260810.json  absent
M245_S1_I1_E02_INTENT_20260810.json  absent
M245_S1_I2_E03_INTENT_20260810.json  absent
M245_S2_I1_E04_INTENT_20260810.json  absent
M245_S2_I2_E05_INTENT_20260810.json  absent
M245_S3_I1_E06_INTENT_20260810.json  absent
M245_S3_I2_E07_INTENT_20260810.json  absent
```

## RED 1: primary core absent

UTC interval: `2026-08-10T05:29:21.9573407Z` through
`2026-08-10T05:29:22.2002370Z`.

Exact test invocation:

```powershell
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_primary_core.py
```

Observed exit code `1`. Captured combined output:

```text
test_m245_primary_core (unittest.loader._FailedTest.test_m245_primary_core) ... ERROR

======================================================================
ERROR: test_m245_primary_core (unittest.loader._FailedTest.test_m245_primary_core)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_m245_primary_core
Traceback (most recent call last):
  File "C:\Python314\Lib\unittest\loader.py", line 137, in loadTestsFromName
    module = __import__(module_name)
  File "C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m245_canonical_unordered_replica_galerkin_spectrum\test_m245_primary_core.py", line 24, in <module>
    import m245_primary_core as primary
ModuleNotFoundError: No module named 'm245_primary_core'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

## RED 2: independent replica core absent

UTC interval: `2026-08-10T05:29:30.8520234Z` through
`2026-08-10T05:29:31.0250904Z`.

Exact test invocation:

```powershell
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_replica_core.py
```

Observed exit code `1`. Captured combined output:

```text
test_m245_replica_core (unittest.loader._FailedTest.test_m245_replica_core) ... ERROR

======================================================================
ERROR: test_m245_replica_core (unittest.loader._FailedTest.test_m245_replica_core)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_m245_replica_core
Traceback (most recent call last):
  File "C:\Python314\Lib\unittest\loader.py", line 137, in loadTestsFromName
    module = __import__(module_name)
  File "C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m245_canonical_unordered_replica_galerkin_spectrum\test_m245_replica_core.py", line 24, in <module>
    import m245_replica_core as replica
ModuleNotFoundError: No module named 'm245_replica_core'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

## RED 3: shard supervisor and outer launcher absent

UTC interval: `2026-08-10T05:29:38.4169250Z` through
`2026-08-10T05:29:38.6315010Z`.

Exact test invocation:

```powershell
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_scientific_transport.py
```

Observed exit code `1`. Captured combined output:

```text
test_m245_scientific_transport (unittest.loader._FailedTest.test_m245_scientific_transport) ... ERROR

======================================================================
ERROR: test_m245_scientific_transport (unittest.loader._FailedTest.test_m245_scientific_transport)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_m245_scientific_transport
Traceback (most recent call last):
  File "C:\Python314\Lib\unittest\loader.py", line 137, in loadTestsFromName
    module = __import__(module_name)
  File "C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m245_canonical_unordered_replica_galerkin_spectrum\test_m245_scientific_transport.py", line 23, in <module>
    import run_m245_scientific_shard as runner
ModuleNotFoundError: No module named 'run_m245_scientific_shard'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

`launch_m245_scientific_invocation.py` and `m245_scientific_worker.py` were
also absent. The first missing supervisor import prevented any later import or
test method from executing.

## RED 4: stdlib-only aggregation absent

UTC interval: `2026-08-10T05:29:44.8621488Z` through
`2026-08-10T05:29:45.0674942Z`.

Exact test invocation:

```powershell
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_aggregation.py
```

Observed exit code `1`. Captured combined output:

```text
test_m245_aggregation (unittest.loader._FailedTest.test_m245_aggregation) ... ERROR

======================================================================
ERROR: test_m245_aggregation (unittest.loader._FailedTest.test_m245_aggregation)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_m245_aggregation
Traceback (most recent call last):
  File "C:\Python314\Lib\unittest\loader.py", line 137, in loadTestsFromName
    module = __import__(module_name)
  File "C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m245_canonical_unordered_replica_galerkin_spectrum\test_m245_aggregation.py", line 21, in <module>
    import aggregate_m245_spectrum as aggregation
ModuleNotFoundError: No module named 'aggregate_m245_spectrum'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

## Zero-scientific-execution census

Each command stopped during unittest module loading at its first intended
missing production import. In every lane:

```text
test_methods_executed=0
frozen_events_opened_or_evaluated=0
mpmath_imports=0
mp_quad_requests=0
Hermite_or_Galerkin_evaluations=0
replica_integrals=0
scientific_workers_created=0
child_processes_created=0
shard_intents_created=0
checkpoints_or_results_created=0
aggregations_created=0
network_or_submission_actions=0
```

The four loader failures are the intended independent RED evidence. They do
not count as scientific shard attempts and consume none of the eight durable
attempt namespaces.

## Stop line

Erratum2 permits only this V2 receipt and its checksum after the four repaired
REDs. No implementation, GREEN test, static promotion, pretrigger census,
trigger, shard, aggregation, provider, response, score, or credit is
authorized by this receipt.

The next lawful action is a separate append-only implementation authorization
that binds these exact tests and this receipt. Until that authority is
independently audited and committed, all six production files must remain
absent.
