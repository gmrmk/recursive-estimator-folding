# M237 predeclaration -- durable write-ahead native receipt

Date: 2026-08-09. Frozen before every M237 implementation, test, launch-intent
record, official-worker invocation, native result, aggregate, or G0 readout.

M236 remains permanently
`KILLED_FROZEN_NATIVE_RECEIPT_UNOBSERVABLE`. M237 is a new evidence-transport
child, not a rerun, repair, reinterpretation, or promotion of M236.

## Bounded what-if decision

```text
A stop with B=8 unknown       information gain 0; reject
B durable-receipt child       resolves the sole missing native fact; select
C reopen estimator math       high scope, discards passed evidence; reject
```

## One changed mechanism

Only the host-side native-result transport changes. M237 adds:

1. an exclusive durable launch-intent receipt before `SubprocessRunner.start`;
2. an atomically installed durable complete result JSON while the runner's
   temporary scratch directory still exists; and
3. correct outer-tool forwarding followed by an independent durable-file
   reopen and SHA256 verification.

The estimator, entrypoint, B=8 topology, f64 arithmetic, setup receipt, source
bytes, calls, bills, seeds, thresholds, resource limits, and ordered worker
lifecycle are bit-identical to the frozen M236 artifacts.

## Frozen M236 inputs

```text
M236 compiler
  6C9E9AF9727722CB6ADE5E1CDA56D3F7A0E7BF82EF35EBDAEFA8AA883A854B75
M236 algebra test
  5E2DE041D68B0B07B437D5362D26195D4F7C7C5A1A45058E900BB4BB3AD4B722
M236 official entrypoint
  18D60E0FC02D034CC0E0006CFEDFA15E9188F59697C21294BD53B501AA9BFB25
M236 frozen native runner used as the semantic reference
  CFC797EFE73CF5CD16D022E60983BBC84FDB707907D01FE035DDCD5997DCF675
M236 native static test
  FED9175D374BAC53D2C03E01A405980F5DDE2AD93165CF5E453936B8B1BFB84F
M236 terminal result
  FF69106F5115B5EF68FBDE3683F27BFB341E18BD85594416EAC6708D31AF7969
M236 terminal disposition
  030E7550D94EA3EF740880B86A3CF890539AE55D47AC115A1BB0EE215C22E741
```

M237 may import frozen M236 transport helpers. It may copy/refactor only the
host orchestration required to install the result before scratch cleanup. It
may not edit any M236 file or change a candidate-side code path.

## Durable paths and transaction

The only M237-owned execution artifacts are:

```text
M237_LAUNCH_INTENT_20260809.json
M237_NATIVE_ONE_PROCESS_RESULT_20260809.json
```

Before worker start, both paths and any fixed sibling temporary-result path
must be absent. The runner creates the launch intent with exclusive-create
semantics, flushes and fsyncs it, reopens it, and verifies its bytes. The
intent freezes the candidate, all parent hashes, setup/source seeds, sequence,
resource limits, result path, runner hash, and invocation count `1`.

After setup and the ordered predictions, the runner builds the complete pass
or fail result while still inside the live scratch-directory scope. It writes
that JSON to a new same-directory temporary path, flushes and fsyncs, closes,
atomically installs it at the final path without overwriting a pre-existing
result, then reopens and parses it before scratch cleanup. A pass and a failure
receive identical persistence treatment.

If the process terminates before a complete result is installed, the durable
intent plus absent result is a binding `KILLED_NATIVE_RECEIPT_INCOMPLETE`; no
second worker is permitted. Any pre-existing path, write/flush/fsync/parse/hash
failure, overwrite, non-atomic finalization, or missing receipt kills M237.

The authoritative result is the durable file, not stdout. The invoking tool
must nevertheless forward the full shell return with `text(result)` (or an
equivalent whole-return forwarding primitive), never iterate a presumed
`content` field. After the command, the root independently reopens, parses,
and SHA256-hashes the durable result before adjudication.

## Frozen official-worker gate

Exactly one fresh official worker is authorized:

```text
setup seed        0
sequence          A -> B -> A
A source seed     227700001
B source seed     227710001
setup timeout     5 s; start-to-response < 4 s
predict timeout   60 s
worker cap        512 MiB
acceptance RSS    each cumulative peak strictly < 496 MiB
```

Every prediction must satisfy all M236 gates:

```text
M212 bill          1,249,253,376
M235 bill            864,960,512
combined bill      2,114,213,888
combined residual <= 3.227021568 ms (binding conservative cap)
M235 residual     <= 2.025121700262334 ms
```

Exact operation dictionaries, actual worker PID, setup bill/18 empty owners,
all alias/stride/span laws, receipt and current-field identity, staging-slot
release, finite/symmetric source, direct float32 `[32,256]` response, and raw
A replay must all pass. The result persists every metric and every individual
gate, regardless of disposition.

## Proof order

1. Independent preimplementation audit of this declaration and manifest.
2. Module-absence RED for the M237 durable runner.
3. Static GREEN proving frozen M236 hashes, identical worker semantics, exact
   durable transaction, no overwrite, no runner call during test discovery,
   and aggregate/G0 closure.
4. Independent prenative code audit.
5. Preflight absence check, exclusive durable intent, then exactly one worker.
6. Whole-return forwarding plus independent durable reopen/hash/adjudication.
7. Independent final receipt audit.

The ten-process aggregate and G0 remain closed unless the one-worker durable
receipt is a fully verified pass.

## Stop and credit

Any persistence, lifecycle, source, bill, call, wall, RSS, identity, alias,
response, or replay failure kills fixed M237. No rerun, retune, path repair,
threshold change, or M236 inference is allowed after launch intent exists.

A pass grants only a native-safe B=8 compiler component. It grants no source
efficiency, whole-response MSE, score, submission, leaderboard, or prize
credit.
