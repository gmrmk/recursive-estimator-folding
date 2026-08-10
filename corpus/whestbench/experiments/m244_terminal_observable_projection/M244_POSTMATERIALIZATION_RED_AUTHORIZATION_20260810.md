# M244 post-materialization authorization 1 — missing-module RED only

Date: 2026-08-10 UTC  
Status: `FROZEN_DOCS_ONLY_PENDING_INDEPENDENT_AUDIT_AND_COMMIT`

This append-only overlay closes the authorization gap left after the one-shot
E7 fixture materialization. It is not effective while uncommitted. It becomes
effective only after an independent read-only audit returns PASS and this file
and its matching V4 checksum receipt are committed without byte changes on
`agent/compression-survivor-corpus`.

## Bound fixture seal

The exact fixture-seal commit is:

```text
97f8d9454b942795f6928d809c9a36b621de48f0
```

That commit must be an ancestor of the executing checkout. The following
committed artifacts must remain present with these exact SHA-256 values:

```text
6141568e017dcef24f00208d29b213cfe1263ae27424de24b7175fd9454d3e90  M244_SHA256SUMS_V3_20260809.txt
34700c6dd53221657cf128adf9ed85753307c365437b140d4777d5b5151add99  M244_E7_FIXTURE_AUTHORITY_20260809.json
76387d625f2b042a45db47db690c8750fe925c57ecd75b58a9422680f678fb8d  M244_E7_FIXTURE_MATERIALIZATION_INTENT_20260809.json
e7e2ef1e5edf012481346b95e25bcb32c8bdee4857d2002fa50116f9243a2c33  M244_E7_POSTPUBLICATION_BINDING_RECEIPT_20260809.json
```

The binding receipt must still state all of the following without
reinterpretation:

- `binding_status=PASS_E7_FIXTURE_AUTHORITY_BOUND`;
- `no_retry=true`;
- fixture-authority result SHA-256 `34700c6d...1add99`;
- materialization-intent SHA-256 `76387d62...8fb8d`;
- wall through result publication `0.6947620999999344` seconds, below the
  frozen `30.0` second cap; and
- process peak through result publication `53002240` bytes, below the frozen
  `268435456` byte cap.

All twelve entries in the V3 checksum receipt and all twenty-seven parent and
runtime bindings recorded in the materialization intent must match before the
authorized RED process starts. Any mismatch is `BLOCKED_PARENT_DRIFT`; it
does not authorize repair, rematerialization, candidate creation, or a retry.
The E7 materializer is permanently spent and must not be invoked again.

## Narrow precedence

For authorization fields only, and only after this overlay becomes effective,
the precedence is:

```text
M244_POSTMATERIALIZATION_RED_AUTHORIZATION_20260810.md
M244_PREIMPLEMENTATION_ERRATUM1_20260809.md
M244_FROZEN_MANIFEST_V2_20260809.json
M244_PREDECLARATION_20260809.md
M244_FROZEN_MANIFEST_20260809.json
```

This overlay supersedes the V2 values
`candidate_or_test_creation_authorized=false` and
`execution_authorized=false` only for the single missing-module RED operation
specified below. Every other equation, fixture, tolerance, topology, ABI,
metering rule, cost cap, seed, disposition, and prohibition remains frozen.

## Exact authorization matrix

```text
create test_m244_terminal_observable_projection.py          true, once
execute the initial missing-module RED                      true, once
create M244 RED intent/receipt/checksum documentation       true
create m244_terminal_observable_projection.py               false
execute any candidate implementation                        false
load or evaluate any E3-E6/E7 scientific fixture            false
import NumPy, mpmath, SciPy, FlopScope, M125, M178, or M179  false
run algebra, parity, topology, target, native, or RSS gates  false
use target seeds 244256001..244256005                        false
create or execute an integrated M199/M200 replacement       false
claim component, replacement, efficacy, score, or FLOP credit false
read scorer, truth, sealed cells, credentials, or M245       false
```

No implied permission exists. A `true` value above does not widen any
neighboring `false` value.

## Authorized RED artifact and failure

Exactly one test file may be created:

```text
test_m244_terminal_observable_projection.py
```

The only production path it may probe in this step is the deliberately absent
sibling:

```text
m244_terminal_observable_projection.py
```

The test must be stdlib-only in this step. It must resolve that exact sibling
path without consulting `PYTHONPATH`, installed packages, or another checkout,
then fail because the file does not exist. The intended failure is an
uncaught `FileNotFoundError` naming that exact sibling path. A passing test,
an import from any other path, any scientific import or fixture evaluation,
or any other exception is not the intended RED and is
`BLOCKED_TDD_RED_MISMATCH`.

The RED command and interpreter must be written to a durable docs-only intent
before the process starts. There is at most one RED invocation. Afterward a
durable receipt must record command, exit code, stderr/stdout SHA-256 values,
test-file SHA-256, candidate-path absence, and the exact exception class and
path. A matching failure may be classified only as
`PASS_TDD_RED_MISSING_MODULE_ONLY`; it is not numerical, topology, cost, or
scientific evidence.

## Stop boundary and next authority

After the RED receipt is written, stop. This overlay does not authorize
implementation, completion or execution of the generated G0A suite, target
inputs, native measurement, integration, or credit. A later append-only
authority must bind the test and RED receipt hashes and explicitly authorize
candidate implementation before `m244_terminal_observable_projection.py` is
created.

The frozen accounting interpretation remains unchanged:

- M244 arithmetic floor: `135002112` FLOPs;
- provisional gross named full-terminal deletion: `267453184` FLOPs;
- currently earned or bankable FLOP credit: `0`;
- conditional legacy-background replacement `7.736750160B`: still forbidden
  without a separately predeclared integrated deletion trace.

