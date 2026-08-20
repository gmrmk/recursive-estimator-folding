# M245 prematerialization erratum 1 -- external supervisor and terminal meter witness

Date: 2026-08-10

Status: `FROZEN_AUTHORITY_REPAIR_ONLY_NO_MATERIALIZATION`.

This append-only erratum was written after authority commit
`c4468c3d330f968ce1a3b376d56aa1f6b640e709` and before any M245
materializer, supervisor, transport test, static-validation receipt, intent,
fixture V2, postpublication receipt, terminal meter witness, scientific code,
or scientific execution. It supersedes only conflicting fixture-transport,
process-topology, ownership, and resource-metering language in section 10 of
`M245_PREDECLARATION_20260810.md` and the matching V1 manifest fields. All V1
mathematics, fixtures, generation rules, frozen census, shard ownership,
scientific gates, firewall, and no-credit boundaries remain unchanged. The
superseded V1 surface expressly includes its fixture argv, environment and
import-startup policy, four-path namespace, worker-owned intent sequence,
process topology/ownership, and resource/receipt endpoint.

## E1. Bound V1 authority

The immutable V1 authority is:

```text
c4468c3d330f968ce1a3b376d56aa1f6b640e709  authority commit
aa9ca84d48e840435d350fbab3be3f1c98356b541d54a018968cfa16b97f2512  M245_PREDECLARATION_20260810.md
17a9df68304c7b06dd29957cc6fd4180242a9cc1bafb79e30c35f2426825b6b4  M245_FROZEN_MANIFEST_V1_20260810.json
0fbc35bfa2e77993e19d50d03ebfdda8851b137cdde18e6ef6613172c8c565c9  M245_SHA256SUMS_V1_20260810.txt
```

All repository, venv, base-runtime, parent, and package roots and hashes remain
those frozen by V1. Before any import by the scientific worker, both the
supervisor and worker must resolve exactly one root for each namespace and
rehash every V1-bound file. A missing path, alternate root, symlink/junction
escape, file-type mismatch, or hash mismatch is `BLOCKED_PARENT_DRIFT` and
burns no scientific work only if it occurs before the exclusive intent. After
intent publication every failure is permanent and no retry is authorized.

## E2. Exact three-process topology

Fixture materialization uses exactly this topology:

```text
external stdlib supervisor S
  -> exact venv launcher redirector L
       -> exactly one scientific worker W
```

The frozen paths are:

```text
authority directory:
C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m245_canonical_unordered_replica_galerkin_spectrum

S interpreter and W OS image:
C:\Python314\python.exe

S source:
supervise_m245_fixture_materialization.py

L image and W logical venv interpreter:
C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe

W source:
materialize_m245_fixtures.py
```

`S` is launched with no user arguments by the exact argv

```text
[C:\Python314\python.exe, -I, -B, -S, -u,
 <authority-directory>\supervise_m245_fixture_materialization.py]
```

and launches `L` with the exact argv

```text
[C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe,
 -B, -P, -s, -S, -u,
 <authority-directory>\materialize_m245_fixtures.py]
```

All three processes use the authority directory as cwd. `W` accepts no user
arguments; its `sys.argv` is exactly the absolute worker-source path. The OS
image of `S` and `W` must be `C:\Python314\python.exe` with V1 SHA-256
`7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a`.
The image of `L` and `W.sys.executable` must be the venv redirector with V1
SHA-256 `4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262`;
`W.sys._base_executable` must resolve to the base interpreter. The exact future
source and dummy-test hashes are bound by the committed static-validation
receipt and rehashed by `S` and `W`.

`S` creates `L` suspended, assigns it to a fresh Windows Job Object configured
with kill-on-close, an active-process limit of two, and an associated completion
port, then resumes `L`. Any equivalent implementation is allowed only if it
provably prevents a descendant from running before job membership and emits an
equivalent complete process-event record; this equivalence must be frozen by a
new authority erratum before implementation. Job notifications must show
exactly two total job processes, `L` and `W`, and no third process at any time.
At the measured `R` endpoint `TotalProcesses==2`, the distinct job PID census
is exactly `{L,W}`, and both remain live and idle at the `EXIT` barrier. They
exit only after the endpoint and before `T` publication.

`S` collision-refusingly creates four initially nonsignaled manual-reset events
named exactly `Local\M245_<p>_READY`, `Local\M245_<p>_GO`,
`Local\M245_<p>_DONE`, and `Local\M245_<p>_EXIT`, where `<p>` is the first
32 lowercase hex characters of the intent SHA-256. `ERROR_ALREADY_EXISTS` is
permanent failure. Before importing NumPy, `W` opens those intent-bound events,
emits exactly one newline-terminated canonical `M245_W_READY` JSON record on
inherited stdout, signals `READY`, and waits. `S` captures stdout through an
inherited pipe, requires stderr to remain empty, and may signal `GO` only after
validating the READY record and the job
notification for `W`, opening and retaining the `W` process handle, and
verifying `W`'s PID, parent PID `L`, creation time, image path/hash, cwd, argv,
environment digest, source hash, and job membership. After publishing and
verifying V2, `W` emits exactly one newline-terminated canonical `M245_W_DONE`
JSON record binding V2 on the same stdout pipe, signals `DONE`, and waits on
`EXIT` without releasing its
arrays or exiting; the redirector `L` must remain waiting for `W`. At this
barrier `S` validates V2, samples current working sets, cross-checks the Job,
and publishes/fsyncs/reopens/hashes provisional `R` while `L` and `W` remain
live and idle. After the endpoint it captures all three live peak/CPU counters,
signals `EXIT`; `W` immediately calls `os._exit(0)` without Python teardown,
then `L` exits. `S` waits for both and retains both handles
for final exit-code and conservative final CPU accounting. Failure before `GO`
closes the kill-on-close job and is permanent because the intent already
exists. `L` creates exactly `W` and no other process; `W` is childless. Neither
may escape the job. READY and DONE are the only worker stdout records; stderr
must be empty. No control file, log, checkpoint, or sixth authority path is
permitted.

`S` requires `-I -B -S -u`: its ambient `PYTHON*` variables are ignored and it
runs isolated/safe-path, without bytecode, site, `.pth`, or buffered output.
`L/W` require `-B -P -s -S -u`: they receive the sanitized child environment,
including the effective frozen `PYTHONHASHSEED`, while blocking bytecode,
unsafe script/cwd prepending, user site, site/`.pth`, and buffering. `S` records for `S`, `L`,
and `W`: PID, parent PID, OS creation `FILETIME`,
image path and SHA-256, argv, cwd, job membership, opened process-handle access
mask, handle acquisition time, exit code, and kernel/user CPU times. PID alone
never establishes identity; creation time plus the retained handle is binding.

## E3. Exact environment and import boundary

`S` must never persist or forward its ambient environment. It constructs a
minimal sanitized child environment containing exactly the following
canonical, sorted UTF-8 key/value map, commits that map and its SHA-256 inside
the intent, and passes it to `L`. `W` reconstructs and verifies the identical
map and digest before NumPy import. No unlisted key, credential, token, proxy,
cloud setting, or inherited secret is recorded or passed:

```text
BLIS_NUM_THREADS=1
COMSPEC=C:\Windows\System32\cmd.exe
MKL_DYNAMIC=FALSE
MKL_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1
OMP_DYNAMIC=FALSE
OMP_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
PATH=C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts;C:\Python314;C:\Windows\System32;C:\Windows
PATHEXT=.COM;.EXE;.BAT;.CMD
PYTHONDONTWRITEBYTECODE=1
PYTHONHASHSEED=0
PYTHONNOUSERSITE=1
SYSTEMROOT=C:\Windows
TEMP=C:\Users\strid\AppData\Local\Temp
TMP=C:\Users\strid\AppData\Local\Temp
VECLIB_MAXIMUM_THREADS=1
WINDIR=C:\Windows
```

In particular `PYTHONHOME`, `PYTHONPATH`, `PYTHONSTARTUP`, `PYTHONINSPECT`, all
proxy variables, and all credential/token variables are absent. `S` records
only the sanitized child map, never the ambient map. `S` imports only the
standard library. `L` is an inert hash-bound redirector. `W` imports only the
standard library until it has verified the intent, authority/runtime hashes,
identity, environment, cwd/argv, job membership, and `READY/GO` release.
Before signaling `READY`, `W` verifies `sys.flags.no_site==1`,
`sys.flags.no_user_site==1`, `sys.flags.safe_path==1`,
`sys.dont_write_bytecode is True`, that the exact venv site-packages path is absent from
`sys.path`, and that neither `numpy` nor any `numpy.*` name exists in
`sys.modules`. After `GO`, `W` directly inserts exactly
`C:\Users\strid\.venvs\whestbench-frozen-m178\Lib\site-packages` once at
`sys.path[0]`, without importing `site` or processing `.pth` files, verifies
the resulting path, and performs the sole `import numpy as np`. It requires
`np.__version__ == '2.4.6'`. No other process may import NumPy and no process
may use the network.

## E4. Five-path one-shot namespace and ownership

The exact initially absent namespace is:

```text
M245_FIXTURE_MATERIALIZATION_INTENT_20260810.json
.M245_FROZEN_MANIFEST_V2_20260810.json.tmp
M245_FROZEN_MANIFEST_V2_20260810.json
M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT_20260810.json
M245_FIXTURE_MATERIALIZATION_TERMINAL_METER_WITNESS_20260810.json
```

All five paths must be absent before `S` creates anything. `S` owns and is the
only writer of the intent `I`, postpublication receipt `R`, and terminal meter
witness `T`. `W` owns fixture generation and is the only writer of the
temporary and final V2 paths. `L` writes nothing. `W` may write no receipt,
checkpoint, log, cache, bytecode, or other authority-directory path.

This five-path namespace supersedes V1's four-path namespace. It also
supersedes V1 materializer steps 1 and 2: only `S` requires all five paths
absent and creates `I`. On entry, `W` must instead require the immutable,
hash-bound `I` to be present and require the V2 temp, final V2, `R`, and `T` to
be absent. `W` must never create, rewrite, or claim ownership of `I`.

`S` exclusively creates canonical `I`, flushes and fsyncs it, then reopens,
parses, byte-compares, and hashes it before spawning `L`. The intent binds all
five paths, authority/runtime/source/test/static-receipt hashes, exact argv,
cwd, complete environment and digest, job/handshake policy, resource caps, and
the permanent no-retry rule. The event names are derived deterministically
from the intent SHA-256 and create no filesystem path.

After `GO`, `W` performs the unchanged V1 fixture generation exactly once and
publishes only V2 by the V1/M237 same-directory exclusive-temp, file-fsync,
reopen/parse/hash, create-if-absent hard-link, device/inode/length/bytes/hash
verification, and temp-unlink sequence. Rename/replace is forbidden. `W`
reports the immutable V2 hash and status to `S`, signals `DONE`, and remains
alive at the `EXIT` barrier. After the live-handle resource/topology sample,
`S` independently reopens and validates V2, publishes and verifies provisional
`R` while `W` and `L` remain at the barrier, captures the endpoint counters,
and only then releases `EXIT` and observes both exits.

## E5. Metered endpoint, receipt R, and terminal witness T

The resource scope is the complete set `{S,L,W}`. Control-plane work is not
free. `S` is included in CPU and memory accounting even though it performs the
measurement; applying V1's unchanged 268,435,456-byte cap to `{S,L,W}` is a
conservative tightening of the former launcher/worker scope. The binding start time `t0` is `S`'s OS creation `FILETIME` from
`GetProcessTimes`, not first Python bytecode, intent creation, or child launch.
The measured endpoint is the first instant after `S` has exclusively created
canonical `R`, flushed and fsynced it, reopened it, parsed it, verified its
bytes, and computed its SHA-256. Immediately after that hash, `S` calls
`GetSystemTimePreciseAsFileTime`; its returned `FILETIME` is the frozen
endpoint clock value. Clock failure or an endpoint earlier than `t0` is
binding failure. `T` publication is outside this endpoint.
After confirmed `W` and `L` exit, `S` calls the same API again to freeze
`child_exit_FILETIME`; failure is binding failure.

`R` is explicitly provisional. It binds `I`, V2, the pre-exit identities and
Job census, all hashes, and the declaration that only a passing `T` can
validate fixture authority. It cannot bind future exit codes or the later
`ActiveProcesses==0` observation and does not claim a self-referential final
resource measurement.

`S` samples the concurrent sum of current `WorkingSetSize` for retained
handles `{S,L,W}` at a nominal interval no greater than 10 ms, on every job
notification, immediately before and after child release/exit, through the
`R` endpoint, and until both job processes exit. It records every timestamp and the largest observed sampling
gap. This is named only `max_sampled_concurrent_working_set_bytes`; it is not
called a gap-free or true process-tree peak.

Immediately after the `R` endpoint, while `L` and `W` remain live at the
`EXIT` barrier, `S` captures all three `PeakWorkingSetSize` values explicitly
labelled lifetime-to-endpoint and
CPU counters. It then signals `EXIT`, waits for child exit, and captures final
exit codes and final CPU counters. The larger pre/post-exit CPU values are
used. These post-endpoint queries and orderly-exit costs are conservative; no
subtraction or backdating is allowed. Define

```text
rss_sampled = max_t sum_p WorkingSetSize_p(t)
rss_lifetime_sum = sum_p PeakWorkingSetSize_p lifetime-to-endpoint
rss_gate = max(rss_sampled, rss_lifetime_sum)
cpu_sum = sum_p (KernelTime_p + UserTime_p)
wall = endpoint_FILETIME - S_creation_FILETIME
wall_child_exit = child_exit_FILETIME - S_creation_FILETIME
```

for `p in {S,L,W}`. The lifetime sum is deliberately conservative and need
not represent concurrent use. The binding gates are

```text
rss_gate <= 268435456 bytes
wall <= 30.0 seconds
wall_child_exit <= 30.0 seconds
cpu_sum finite, nonnegative, and fully reported in 100 ns units and seconds
largest observed sampling gap <= 0.100 seconds
```

No independent CPU cap is introduced by this erratum; CPU is mandatory
evidence and may not be omitted or described as uncharged. Missing handles,
unavailable counters, PID reuse ambiguity, an incomplete sample, counter
rollback, negative wall, topology drift, cap miss, or inability to prove the
endpoint is binding failure.

Only after the endpoint does `S` construct and exclusively publish canonical
`T`. `T` binds the exact path, byte length, and SHA-256 of `R`, plus `I` and V2
hashes; the three retained-handle identity records; the complete job census;
all raw and derived CPU/RSS/wall measurements; caps; sampling schedule and
maximum gap; the post-exit `ActiveProcesses==0` observation and exit codes;
both wall values; the observed pre-`T` state (`I`, V2, and `R` present, V2 temp and
`T` absent); the expected `T` path; and one terminal status. `S` flushes and
fsyncs `T`, then reopens, parses, byte-compares, and hashes it outside the
explicitly delimited `R` endpoint. `T` contains no claim about its own
publication time, cost, existence, durability, bytes, or hash. Those facts
are established only by the later independent read-only audit and checksum
receipt. The outside-endpoint rule may not be generalized to scientific work
or to `I`, V2, or `R`.

The sole passing status is `PASS_M245_FIXTURE_AUTHORITY_BOUND`. Missing,
partial, noncanonical, failing, or unpublished `T` leaves `I`, V2, and `R`
provisional and invalid forever. A failure while publishing `I`, V2, `R`, or
`T`, a residual V2 temp, or any post-intent exception is permanent
`BLOCKED_FIXTURE_AUTHORITY_NO_RETRY`; no second materialization is authorized.

## E6. Frozen TDD, static-audit, and launch order

No action below is implicitly complete. The only authorized sequence is:

1. Commit this erratum, its manifest overlay, and their checksum receipt.
2. Write dummy-only transport tests first for the supervisor, worker boundary,
   five-path refusal, hard-link publication, job/handshake state machine, and
   `R`/`T` accounting. Tests use temporary paths and dummy data outside the
   frozen census and must preserve a missing-implementation RED.
3. Implement `S` and `W`; keep `S` stdlib-only and keep NumPy behind `W`'s
   verified `GO` boundary. Do not materialize or preview a frozen fixture.
4. Run only the dummy transport tests. Obtain two distinct independent,
   read-only static PASS audits of the exact supervisor, worker, test, this
   erratum, and overlay hashes.
5. Create a canonical committed static-validation receipt containing the two
   normalized distinct reviewer identities, every audited hash and PASS
   verdict, the exact V1 authority commit/hashes, and a no-scientific-execution
   declaration. Both `S` and `W` must bind its SHA-256.
6. Perform a fresh read-only prelaunch audit proving all five execution paths
   absent and all committed hashes exact. Obtain a separate explicit one-shot
   launch authorization. A static PASS alone does not launch anything.
7. Invoke `S` exactly once. Direct invocation of `L` or `W` is forbidden.
8. Only a passing `T` permits committing V2, `R`, `T`, and a V2 checksum
   receipt. Then obtain two fresh independent read-only audits before any
   scientific test, primary, replica, shard, or aggregation work.

This erratum creates no candidate/test/scientific-execution authority, spends
no fixture launch, and changes no seed, fixture, threshold, or credit.

## E7. Effective precedence

For prematerialization transport and accounting, precedence is:

```text
M245_PREMATERIALIZATION_ERRATUM1_20260810.md
M245_FROZEN_MANIFEST_V1_OVERLAY1_20260810.json
M245_PREDECLARATION_20260810.md
M245_FROZEN_MANIFEST_V1_20260810.json
```

The overlay checksum receipt authenticates this chain but does not add
semantic authority. Any conflict is resolved by the first applicable item.
All unmentioned V1 rules remain frozen.
