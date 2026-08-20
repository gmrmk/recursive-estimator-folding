# M245 scientific transport/test erratum 2 -- reconstructible launch and union contract

Date: 2026-08-10 UTC  
Status: `FROZEN_DOCS_ONLY_REPAIRED_RED_AUTHORITY_PENDING_AUDIT_AND_COMMIT`

This append-only erratum closes hostile-review blocker H1 in the scientific
transport and aggregation tests. It supersedes only conflicting transport,
test, receipt, trigger, resource, and aggregation language in sections 11 and
12 of `M245_PREDECLARATION_20260810.md` and the concluding implementation
authorization in `M245_SCIENTIFIC_TDD_RED_RECEIPT_20260810.md`.

All M245 mathematics, the E00:E07 census and shard assignments, binary-input
authority, 80/100-digit rules, quadrature tolerances, analytic and solve gates,
finite geometric/logistic/Gompertz ladder, firewall, dispositions, and
no-credit boundary remain byte-for-byte conceptually unchanged. Nothing here
authorizes scientific evaluation or gives estimator, deployment, score, or
FLOP credit.

## E2.1 Bound authority and superseded RED surface

The authority lineage is:

```text
c4468c3d330f968ce1a3b376d56aa1f6b640e709  V1 authority commit
853b30cf5ef8f87788aab6cee73218edddd6f466  prematerialization repair commit
c8a1ef39f49dba2540edd1bf19f0ac6e694a5adb  fixture transport commit
dddd874b19c15396da8981b20db3aa260831e7cb  sealed V2 fixture-authority commit
0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b  M245_FROZEN_MANIFEST_V2_20260810.json
2e56bd140b71527f640e1c1afbbc347fcca601fa4f0ec83f711c69a29e2b444e  M245_SHA256SUMS_V2_20260810.txt
```

The first scientific RED receipt preserves the recorded commands, outputs,
exit codes, missing-module causes, and the then-observed four test hashes as
honest pre-repair evidence:

```text
5497b1397a62bbfb4f3be73a02f2b63872e01f2bd4795b77232e7c6c287beb85  M245_SCIENTIFIC_TDD_RED_RECEIPT_20260810.md
223dcc0eae654adc663bd5a26e99da737da6caa8304b9a5bdd8525b9b84b5fe2  test_m245_primary_core.py
2fafd424836a388838ee912925cf24a332c881ffa07bef1cf29265f3291de44c  test_m245_replica_core.py
1933f16628650440883b1675af0ce1057543ded34fec12fca0700ccc9b9d0382  test_m245_scientific_transport.py
a8558becaf0c832347b758b585450527712583730ed3397b8cb79abea05a6ebe  test_m245_aggregation.py
```

The original four test bytes were never committed and no longer exist at the
live paths; only their hashes and execution-output claims remain in the first
receipt. They are therefore not independently reconstructible source
artifacts and are not described as byte-preserved. The recorded REDs support
the historical claim that the five production modules were absent, but their
test surface does not close H1. The sentence authorizing implementation
against those exact bytes is superseded. Their status is now
`RECORDED_PRE_REPAIR_REDS_NOT_IMPLEMENTATION_AUTHORITY`.

## E2.2 Narrow authorization and stop line

After this erratum and its checksum overlay receive an independent read-only
PASS and are committed without byte changes, they authorize only:

1. repair of the four existing scientific test files named above;
2. static, dummy-only inspection of those repaired tests;
3. one fresh missing-module RED invocation for each repaired test; and
4. creation of the append-only receipt
   `M245_SCIENTIFIC_TDD_RED_RECEIPT_V2_20260810.md` and its checksum.

The repaired REDs may read V2 only to verify bytes, hashes, schema, census, and
shard ownership. They may use dummy events outside E00:E07. They may not
evaluate a frozen event or create a shard path.

Four unexecuted, unfrozen provisional repair drafts were created while this
authority itself was under review. They have no retroactive authority and may
not be run or frozen before the authority commit. After that commit, the exact
drafts may be adopted as repair inputs, completed, independently read-only
audited, and only then used for the four fresh RED invocations. The V2 RED
receipt must state this chronology and bind the actual post-commit test bytes;
it must not imply that their pre-commit editing was an authorized test run.

The following six files must remain absent throughout this repaired-RED step:

```text
m245_primary_core.py
m245_replica_core.py
m245_scientific_worker.py
run_m245_scientific_shard.py
launch_m245_scientific_invocation.py
aggregate_m245_spectrum.py
```

No implementation, GREEN run, scientific import, E00:E07 evaluation, shard
intent, external supervisor launch, aggregation, or trigger is authorized.
After the four repaired missing-module failures and V2 RED receipt are frozen,
stop for a separate implementation authority and two fresh static audits.

## E2.3 Meaning of the eight-launch cap

`max_launches_total=8` counts durable shard invocation attempts. It does
**not** mean eight total OS process creations. Each attempt is one unique
`(shard_id,invocation_index)` pair and consumes its namespace permanently when
`S` successfully hard-link-publishes, reopens, byte-verifies, parses, and
hash-verifies that pair's exclusive write-ahead intent. That durable intent is
the exact burn point.

Before the burn point `S` is stdlib-only, may perform only committed-source,
path, trigger, environment, and hash preflight, and may not create `L`, import
a scientific dependency, read a fixture array value, or call scientific code.
A process-start or preflight failure before intent publication is a typed
`UNCONSUMED_STDLIB_PREFLIGHT_FAILURE`, not a scientific attempt. Codex may
launch a fresh `O` again only while all exact files for that pair remain lexically
absent and the committed trigger, HEAD, argv, cwd, environment digest, and
source hashes are unchanged. No observation or scientific selection exists
before the burn point. Once the intent exists, every failure is permanent and
no relaunch is permitted.

The complete successful census has exactly eight attempts:

```text
(0,1,E00) (0,2,E01) (1,1,E02) (1,2,E03)
(2,1,E04) (2,2,E05) (3,1,E06) (3,2,E07)
```

Every successful burned attempt has four distinct OS identities: outer stdlib launch
observer `O`, stdlib shard supervisor `S`, inert venv launcher redirector `L`,
and scientific worker `W`. Thus a successful complete census observes eight
of each role while consuming eight -- not thirty-two -- attempt slots. All
four roles must have distinct PID plus creation-FILETIME identities. PID alone
is never identity. The later Codex aggregation launch has its separate
one-launch cap and is not one of these eight.

A burned attempt that fails before `L` or `W` exists records the exact observed
identity prefix and typed missing roles; it is permanent FAIL, not a false
four-role census. Only the complete-success census has eight of every role.

Failure, timeout, exception, nonfinite/over-threshold quadrature error,
resource breach, publication failure, or hash drift consumes that unique
attempt and yields the existing binding local-kill disposition. It never
opens a replacement, third invocation, retry, redraw, or reseed.

## E2.4 Exact O/S/L/W topology, argv, cwd, and ownership

The user-authorized operational handoff after Fable's session limit makes
Codex `/root` the sole shard owner and external caller for M245. This sentence
supersedes V1's operational assignment to Fable only; it changes no science,
census, order, cap, or firewall. No Fable process, session, checkpoint, or
uncommitted transcript is an execution dependency.

All four roles use this cwd:

```text
C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m245_canonical_unordered_replica_galerkin_spectrum
```

For shard `s` and invocation `i`, the external argv for `O` is exactly:

```text
[C:\Python314\python.exe, -I, -B, -S, -u,
 <authority-directory>\launch_m245_scientific_invocation.py,
 --shard-id, <canonical decimal s>,
 --invocation-index, <canonical decimal i>]
```

`O` launches `S` exactly once, with `shell=False` and exact cwd/environment:

```text
[C:\Python314\python.exe, -I, -B, -S, -u,
 <authority-directory>\run_m245_scientific_shard.py,
 --shard-id, <canonical decimal s>,
 --invocation-index, <canonical decimal i>]
```

`S` launches `L` exactly once with:

```text
[C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe,
 -B, -P, -s, -S, -u,
 <authority-directory>\m245_scientific_worker.py]
```

`W.sys.argv` contains only the absolute worker-source path. The shard,
invocation, event, immutable intent path, and trigger digest reach `W` through
the exact frozen child environment and are revalidated against the intent
before scientific import. No additional positional argument, shell, module
mode, response file, alternate cwd, or ambient `PYTHONPATH` is allowed.

The images and hashes remain the V1-bound binaries:

```text
O, S, and W OS image: C:\Python314\python.exe
sha256=7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a
L image and W logical sys.executable:
C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe
sha256=4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262
```

The only process tree is `O -> S -> L -> W`. `S` creates `L` suspended, assigns
`L` to a fresh Job Object with active-process limit two and completion port,
then resumes it; the redirector creates exactly one `W`. The job contains
exactly `L,W`; `O` and `S` are outside the job but inside the charged resource
scope. `W` has no child. `O` and `S` are stdlib-only; `L` executes no project
code; `W` is the only role allowed to import mpmath and the two scientific
cores after the verified `READY/GO` barrier.

Ownership is exclusive:

- Codex `/root` is the only external caller and may only launch `O` with the
  exact argv/cwd/environment after the committed trigger;
- `O` launches and retains exact `S`, observes its complete lifetime, owns the
  terminal invocation witness, and on invocation two owns the final-shard
  receipt;
- `S` exclusively creates the intent and is the sole writer/publisher of all
  result, checkpoint, meter, and provisional invocation-receipt files;
- `L` owns no M245 file and only redirects/waits;
- `W` reads the immutable intent, computes one assigned event, emits framed
  canonical records to `S`, then waits at `DONE/EXIT`; it writes no file; and
- only invocation-two `O` may publish the final-shard receipt, after it has
  opened and verified invocation one's terminal witness plus both
  invocations' exact result, checkpoint, meter, and provisional receipt
  paths/hashes. A caller-supplied prior hash is forbidden.

Every durable JSON publication, including intent and both receipt kinds, uses
its exact same-directory temporary path, exclusive temporary creation,
flush/fsync/reopen/byte/hash verification, create-if-absent hard-link
publication, final reopen/identity/byte/hash verification, and temporary
unlink. Rename/replace, direct final-path writing, and mutable append are
forbidden.

## E2.5 Exact invocation namespace and external zero-intent census

For stem `M245_S{s}_I{i}_{event}`, the pair namespace contains exactly:

```text
.{stem}_INTENT_20260810.json.tmp
{stem}_INTENT_20260810.json
.{stem}_RESULT_20260810.json.tmp
{stem}_RESULT_20260810.json
.{stem}_CHECKPOINT_20260810.json.tmp
{stem}_CHECKPOINT_20260810.json
.{stem}_METER_20260810.json.tmp
{stem}_METER_20260810.json
.{stem}_RECEIPT_20260810.json.tmp
{stem}_RECEIPT_20260810.json
.{stem}_TERMINAL_WITNESS_20260810.json.tmp
{stem}_TERMINAL_WITNESS_20260810.json
M245_S{s}_FINAL_RECEIPT_20260810.json.tmp
M245_S{s}_FINAL_RECEIPT_20260810.json   # invocation two only
```

`S` owns intent/result/checkpoint/meter/provisional receipt. `O` owns terminal
witness and, for invocation two only, final-shard receipt. All live shard files reside only under
`corpus/whestbench/experiments/m245_fable_spectrum_shards`.

Before a trigger may be written, Codex runs the future runner's hash-bound
stdlib-only census mode with exact argv:

```text
[C:\Python314\python.exe, -I, -B, -S, -u,
 <authority-directory>\run_m245_scientific_shard.py,
 --emit-pretrigger-zero-intent-census]
```

This mode must exit before any scientific import, create no child, and inspect
these exact eight intent paths:

```text
M245_S0_I1_E00_INTENT_20260810.json
M245_S0_I2_E01_INTENT_20260810.json
M245_S1_I1_E02_INTENT_20260810.json
M245_S1_I2_E03_INTENT_20260810.json
M245_S2_I1_E04_INTENT_20260810.json
M245_S2_I2_E05_INTENT_20260810.json
M245_S3_I1_E06_INTENT_20260810.json
M245_S3_I2_E07_INTENT_20260810.json
```

It must publish immutable
`M245_PRETRIGGER_ZERO_INTENT_CENSUS_20260810.json` in the authority directory,
using exact temporary
`.M245_PRETRIGGER_ZERO_INTENT_CENSUS_20260810.json.tmp` and the E2.4
hard-link transaction,
recording the resolved shard directory, exact ordered paths, an `lstat`
absence observation for each path, observer identity, UTC interval, repository
parent HEAD observed before publication, exact runner source hash/argv/cwd,
and `observed_present_count=0`. The census cannot contain the hash of its own
future commit. It must be committed before the trigger; the trigger separately
binds the actual census-containing commit plus the census exact bytes/hash. A caller-supplied
integer, glob count, Maestro statement, or runner self-assertion is not this
external observation. Every `S` also repeats the exact eight-path absence/
prior-path check immediately before its own exclusive intent; the committed
census does not waive that fail-closed check.

For `(0,1)` all eight intents must still be absent. Every later attempt must
observe a down-closed subset of the exact eight paths: `(0,1)` must be present
and PASS before any other attempt; an invocation two additionally requires
its own invocation-one result/checkpoint/meter/provisional receipt plus
terminal witness to be present, exactly cross-bound, and terminally PASS;
and no invocation two may precede its invocation one. Other concurrently
completed paths may be present only if their canonical intents bind the same
trigger and satisfy this partial order. The target intent and every temporary
for the target must be lexically absent. Any outside path, malformed present
intent, failed predecessor, or non-down-closed set is refusal. This exact
partial-order rule replaces an unspecified integer or glob count.

## E2.6 Sole quadrature gateway and lossless call ledger

There is one dynamic gateway for every M245 `mp.quad` request. It is owned by
`m245_scientific_worker.py` and injected into the primary and replica cores.
Neither core may call `mp.quad` directly, import the other core, or instantiate
an alternate wrapper. Across the three scientific source files there is
exactly one project-source `mp.quad` call site: inside this gateway.

The gateway alone may apply the frozen literal policy
`method='tanh-sinh', maxdegree=14, error=True`. It saves `mp.eps` before entry,
allocates monotonically increasing request and completion indices, records
parent request/depth for nesting, and writes one lossless ledger record for
every request, including a request that raises. Each record contains at least:

```text
invocation/shard/event, engine, precision_dps, cache_scope_id,
request_index, completion_index, parent_request_index, nesting_depth,
quantity, call_role, panel_path, exact left/right endpoints,
method, maxdegree, error_api, saved_mp_eps,
mp_quad_invoked, cache_disposition,
returned_value, returned_error, value_finite, error_finite,
error_le_saved_mp_eps_over_8, exception_type/message_sha256, pass
```

Every finite mpf value is serialized losslessly by sign, integer mantissa,
binary exponent, and bitcount; infinities are typed endpoints, never decimal
approximations. Entry order and completion order are both preserved. The
gateway summary must be exactly reconstructible from the ledger: request
count, actual `mp.quad` call count, cache-hit count, outer-call count, nested-
call count, every per-call gate, and the outer-panel error sums. Cache scope is
limited to one `(invocation,event,engine,precision)` and cannot cross engines,
precisions, events, invocations, or shards. Nested raw error sums remain
diagnostic only, exactly as the V1 authority requires.

The repaired tests must AST-prove the single call site and dynamically prove
that dropped, duplicated, reordered, unparented, uncompleted, failed, direct,
or policy-drifted requests are rejected. A summary counter supplied separately
from the gateway ledger is not completeness evidence.

## E2.7 Reconstructible O/S/L/W resource evidence

Each invocation publishes an immutable inner meter from `S` plus an immutable
outer terminal witness from `O`; summary-only resource fields are
insufficient. Every sample records:

```text
sample_index, QueryPerformanceCounter tick/frequency, UTC FILETIME,
for every locally observed role: PID, creation FILETIME, image hash,
alive/exit state, current working-set bytes, peak working-set bytes,
cumulative kernel-time 100ns, cumulative user-time 100ns
```

`S` samples `S,L,W` from before `L` creation through verified result and
checkpoint publication, `DONE/EXIT`, and clean `W,L` exit. `O` samples `O,S`
from before spawning `S` through `S` exit and any invocation-two final-shard
publication. Both streams have gaps no larger than `0.100000000` seconds and
retain handles so PID reuse cannot change identity. The inner stream includes
the exact Job completion-port and `L,W` PID census.

The chronology is deliberately non-self-referential:

1. `W` sends the complete canonical event object and waits at `DONE`.
2. `S` verifies and durably publishes provisional science result/checkpoint
   while both meters remain live.
3. `S` releases `EXIT`, samples through clean `W,L` exit, closes and publishes
   its raw meter, publishes a provisional invocation receipt binding exact
   result/checkpoint/meter bytes and hashes, then exits. None confers PASS.
4. `O` retains and samples `S` through clean exit and rejects a hang/nonzero
   exit. Invocation-two `O` may then publish the final-shard receipt from the
   exact immutable inputs.
5. `O` freezes its raw stream only after optional final-shard publication and
   publishes the terminal invocation witness binding both meters, all inner
   artifacts, the final-shard receipt when applicable, complete resource
   reductions, and `S`'s clean exit.

The terminal witness's own publication in step 5 is explicitly outside its
sampled interval because a file cannot attest to events after its immutable
bytes are fixed. After either meter closes, its owner may execute only stdlib
canonical serialization, hashing, hard-link publication, reopen verification,
cleanup, and exit. No mpmath/core call, scientific transformation, fixture
access, or policy decision is legal. Missing/failed terminal-witness
publication is permanent FAIL. Only the `O` terminal witness, never an inner
result or provisional receipt, confers invocation PASS. This finite terminal
boundary mirrors the sealed fixture materializer.

The terminal witness reductions are recomputable exactly from the bound inner
and outer streams:

- full wall seconds = terminal endpoint FILETIME after `S` exit and optional
  final-shard publication minus retained `O`-process creation FILETIME;
- full CPU seconds = final cumulative kernel+user 100ns counters for
  `O,S,L,W`, each starting at process creation, with no baseline subtraction;
- sampled concurrent RSS uses the union of inner and outer QPC ticks after
  requiring one frequency/clock domain. At each union tick it carries each
  identity's most recent sample forward for at most `0.100000000` seconds,
  counts each `(PID,creation_FILETIME)` once, and for duplicated `S` uses
  `max(inner_S,outer_S)` for current and peak bytes. A missing prior sample,
  over-age carry, frequency/clock/identity disagreement, or ambiguous overlap
  fails; no implementation-chosen interpolation is allowed;
- lifetime-peak upper is the sum of maximum observed lifetime
  `PeakWorkingSetSize` for `O,S,L,W`, including all startup and durability; and
- RSS gate value = max(maximum merged concurrent RSS, lifetime-peak upper).

QPC ticks/frequency are a monotonic gap cross-check, not an undefined external
launch timestamp. Global CPU is the exact sum of the eight terminal-witness
CPU reductions. Every raw/summary mismatch, missing identity/sample, counter
rollback, sampling gap breach, incomplete exit, wrong job census, full wall
over 5400, scientific work after 5100, RSS gate over 2147483648, or global CPU
over 43200 is binding failure. `O,S,L,W` are all charged. The 300-second
post-science reserve covers barrier, inner durability, final-shard publication,
and terminal-witness preparation. Only the witness's own finite publication
is excluded, and it cannot contain science.

## E2.8 Unified final-shard union schema

Transport and aggregation use one schema only:
`m245-final-shard-receipt-v2`. Its exact top-level key set is:

```text
artifact, schema, shard_id, events_in_order, event_results,
invocation_receipts, authority_sha256, resource_union,
no_cross_shard_cache, firewall, status
```

`events_in_order` is the exact assigned pair. `event_results` is a two-element
ordered lossless union. Each element has exactly:

```text
event_id, fixture_array_sha256,
primary_by_precision, replica_by_precision,
cross_precision_gates, primary_replica_gates,
analytic_solve_energy_beta_gates, curve_report,
quad_gateway_ledger_refs, only_future_bound,
gate_verdict, firewall, forbidden_credit
```

`primary_by_precision` contains the complete immutable primary event objects
at 80 and 100 digits; `replica_by_precision` contains the complete immutable
replica event objects at 80 and 100 digits. No field is summarized away.
`quad_gateway_ledger_refs` binds the exact per-engine/per-precision ledger
hashes and counts. `invocation_receipts` binds path, SHA-256, event, index, and
provisional status for both inner receipts plus path, SHA-256, and PASS for
invocation one's outer terminal witness. Invocation two's witness is published
afterward and binds this final-shard receipt. `resource_union` contains the
complete invocation-one resource witness plus invocation-two's inner meter and
explicit `invocation_two_terminal_witness_required=true`; it cannot claim the
future invocation-two outer resource values.

Invocation-two `O` publishes the final shard receipt only after reopening
invocation one's terminal witness and these exact eight inner immutable
inputs: invocation-one and invocation-two result, checkpoint, meter, and
provisional receipt. Each witness binds its invocation's four inner files by
exact path, bytes, SHA-256, identity, event, and index; invocation two's
terminal witness additionally binds invocation one's four files and witness
plus the final-shard receipt. The publisher may not accept caller-supplied
event dictionaries or hashes. Its
event objects must be canonical-byte equal to the corresponding objects in
the two immutable result files. Both the transport validator and aggregator
validator consume this same v2 schema and reject v1, extra/missing keys,
reordered events, lossy summaries, or recomputed science.

Because invocation-two's terminal witness must observe final-shard
publication, the final-shard receipt status is exactly
`PROVISIONAL_SHARD_ASSEMBLY_AWAITING_I2_TERMINAL_WITNESS`, never standalone
PASS. The subsequently published invocation-two terminal witness binds its
bytes/hash and carries `PASS_M245_SHARD_BOUND`. The immutable pair is the
binding shard PASS and supersedes V1's impossible standalone-future-witness
reading.

## E2.9 Complete trigger binding

The only **shard** trigger remains one committed append-only
`AGENT_CHANNEL.md` message from Codex. Its canonical payload must bind exact
SHA-256 values for all of:

1. V1, erratum1/overlay1, V2, this erratum2, and every checksum overlay;
2. fixture supervisor, fixture worker, fixture transport test, fixture TDD and
   static-validation receipts, fixture intent, V2, R, and T;
3. `m245_primary_core.py`, `m245_replica_core.py`,
   `m245_scientific_worker.py`, `run_m245_scientific_shard.py`,
   `launch_m245_scientific_invocation.py`, and `aggregate_m245_spectrum.py`;
4. all four repaired scientific tests;
5. the original scientific RED receipt and repaired V2 RED receipt;
6. every scientific static-audit contract/receipt and two normalized,
   distinct independent PASS reviewer records; and
7. the committed external zero-intent census receipt, its exact eight ordered
   paths, `observed_present_count=0`, and its repository commit.

The trigger also binds the exact shard assignment, O/S/L/W argv and source
hashes, unified final-receipt schema version, aggregation schema/version, and
the exact four future final-shard receipt paths. Those future receipts do not
yet exist, so the trigger binds their paths and schemas, never invented future
hashes.
Each invocation intent independently records the SHA-256 of the exact trigger
message bytes read from the committed `AGENT_CHANNEL.md` Git blob; the trigger
payload is not required to contain an impossible self-hash. A generic
`future_artifacts` list,
`prior_shard_intent_count=0`, reviewer names without receipt hashes, omitted
aggregation/test/TDD/static hashes, or an uncommitted Maestro message is
invalid. `O` rehashes every trigger-bound file before spawning `S`; `S`
independently repeats the census before intent publication.

## E2.10 Immutable-file aggregation and exact family rule

Aggregation is Codex-owned and remains forbidden until four immutable
provisional final-shard v2 receipts are each bound by their invocation-two
`PASS_M245_SHARD_BOUND` witness and all eight terminal witnesses PASS. After
all exist, a separate
Codex-owned stdlib-only action publishes and commits
`M245_AGGREGATION_INPUT_AUTHORIZATION_20260810.json` via exact temporary
`.M245_AGGREGATION_INPUT_AUTHORIZATION_20260810.json.tmp` and the E2.4
hard-link transaction. That authorization binds
the shard trigger hash, the exact four final-receipt and eight witness paths,
their now-observed bytes/SHA-256/file identities/statuses, the observed parent HEAD, aggregate
argv/cwd/source hash, and zero prior aggregate intent/result paths. It cannot
contain the hash of its own future commit. The authorization JSON plus the Git
commit that first contains those exact bytes and no aggregate output is the
sole aggregation launch authority. There is no second `AGENT_CHANNEL.md`
trigger and no future self-hash field. The aggregator verifies that commit and
blob before its exclusive intent. No aggregation process starts before it.

The aggregator's public entry point accepts only that committed authorization,
the exact four authorized provisional final-receipt paths/hashes, and the exact
eight authorized terminal-witness paths/hashes. It must not accept
caller-supplied parsed dictionaries or lists as authority. It opens all twelve
exact regular non-reparse files plus the authorization blob, retains handles,
records file identities/lengths, reads canonical bytes, verifies SHA-256,
schema/census, every final-receipt-to-invocation-two-witness binding, and the
authorization's first-containing Git commit, and only then parses. Reopen
bytes and identities must agree before output.

The aggregate result is a lossless ordered concatenation of E00:E07. It may
verify and copy fields and perform this one exact family reduction for each of
`geometric`, `logistic`, and `Gompertz`:

```text
family_label = NOT_FALSIFIED_ON_Q0_8
    iff every event E01:E07 has event_label NOT_FALSIFIED_ON_Q0_8;
family_label = FALSIFIED otherwise.
```

E00 must be exactly `ENDPOINT_CONTROL/NA` for all three families and is not a
vote. There is no majority rule, missing-value rule, pooled rescue, alternate
label, case folding, refit, transform, or extrapolation. The only copied
future statement remains
`0<=additional_explainable_energy_beyond_Q8<=K-P8`.

Aggregation uses its exclusive intent, immutable hard-link result publication,
and postpublication receipt. Its receipt binds all four provisional final
receipts, all eight terminal witnesses, and the aggregation authorization by
exact path/identity/bytes/hash plus the authorization commit and output
bytes/hash. A mutable source file, in-memory-only input,
rename/replace, second output, retry, scientific import, quadrature, solve,
transform, fit, dropped/relabelled event, or nonexact family rule is binding
aggregation failure.

## E2.11 Repaired RED completion criterion

The repaired tests must encode every E2.3--E2.10 rule using only static source
inspection and dummy artifacts/events outside E00:E07. The four fresh RED
commands must fail first and only because their respective production module
is absent, before test discovery executes scientific work. The V2 RED receipt
must bind the repaired test hashes, exact commands, outputs, exit codes,
missing-module causes, absence of all six implementation files, absence of
all eight shard intents, and a zero-scientific-execution census.

They must also close the original H1 zero-stub surface. The primary dummy
suite requires a nonzero correlated Plackett control at both signs, finite
Hermites through degree 20, direct-vs-analytic all nine `R_q` and all 45
upper-triangle `G_mq` entries, every leading Cholesky/eigenvalue/condition and
solve-residual gate, and nonzero Q=0/4/8 direct-residual and beta-dominance
identities. The replica dummy suite requires a nonzero correlated unary-factor
control, independently rebuilt `r` and mean, explicit `sign(0)` behavior,
same-sign and cross-sign replica identities, and proof that caches are fresh
across engine, precision, event, invocation, and shard. A constant-zero
primary, replica, ledger, meter, or receipt stub must fail.

A repaired RED PASS is test tissue only. It does not authorize implementation,
GREEN execution, static promotion, a trigger, a shard, aggregation, or credit.
The next action after a frozen repaired RED receipt is a separate append-only
implementation authorization.
