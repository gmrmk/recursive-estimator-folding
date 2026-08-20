# M243 prelaunch erratum 4 — one-PID write-ahead resource witness

Date: 2026-08-09  
Status: **FROZEN BEFORE ANY G0A LAUNCH; HARNESS REPAIR ONLY**

This erratum follows the final authority at commit
`49a5ee1abc13a31d6e2ac8930110f4e6afa6d087`.  It changes no estimator,
formula, fixture, event, tail point, precision, quadrature panel, tolerance,
resource cap, firewall, or stop rule.  It only repairs defects found by two
independent static audits of the first unexecuted G0A runner snapshot:

```text
m243_g0a_reference.py
  b03e9b2ddda22d8ea147c0720ca8644c91bff2d22c8f82bd057b91a55bdc2c25
run_m243_g0a.py
  11b75549c7c5bd4f41c588aa38bc62c348c1136ebfc565d6ba87e09bb6c7f3d0
```

That runner snapshot was never imported, compiled, or executed.  No G0A
intent, temporary result, result, resource witness, G0B artifact, response,
truth, score, challenge-weight, integration, or submission artifact exists at
the time of this erratum.

## Z1. One process, delayed scientific runtime

The repaired G0A launch remains exactly one Python process and one PID.  It
must record `process_count=1` and `launcher_pid == scientific_worker_pid`.
No subprocess, shell child, helper process, or second scientific worker is
permitted.  It must record `scientific_worker_start_count=1`.

At module import time, the runner may import only the Python standard library
and the pinned, side-effect-free M237 durable helper.  Every scientific import
(`numpy`, `mpmath`, M122/M129/M133/M147/M151/M178, the M243 candidate, and the
independent M243 reference) must occur inside one
`_load_scientific_runtime()` call made only after the write-ahead intent and
watchdog are live.  Importing the runner as a module must create no file,
start no thread, and execute no experiment.

## Z2. Binding transport and exact order

The sole launch owns these paths:

```text
intent      = M243_G0A_LAUNCH_INTENT_20260809.json
result_temp = .M243_G0A_RESULT_20260809.json.tmp
result      = M243_G0A_RESULT_20260809.json
receipt     = M243_G0A_POSTPUBLICATION_RECEIPT_20260809.json
```

All four must be absent before launch.  The exact order is:

1. Perform the four-path absence check and static stdlib-only source/hash and
   interpreter-identity preflight.  No scientific module may be imported.
2. Exclusive-create, fsync, reopen, parse, and hash-verify the intent through
   `write_launch_intent_exclusive`.  The intent records expected authority,
   dependency, reference, and static-runner hashes; the exact interpreter;
   one PID/process; resource caps; firewall; and all transport paths.
3. On verified intent return, set `t0=time.perf_counter()`, start the typed
   Win32 watchdog, and synchronously checkpoint it.
4. Call `_load_scientific_runtime()`, then perform environment, package,
   firewall, and complete frozen-hash preflight.  Any import or preflight
   failure is now after intent and must lead to a durable FAIL or, if durable
   publication itself fails, an intent-without-receipt permanent failure.
5. Run exactly the already-frozen eight-event G0A gate.
6. Perform postflight, canonical serialization, fsync, and hard-link
   publication of `result` through `publish_native_result` while the watchdog
   remains live.
7. Immediately after `publish_native_result` returns, synchronously sample
   elapsed wall and process lifetime peak working set, then stop/join the
   watchdog inside a `BaseException`-protected stop path.
8. Exclusive-create, fsync, reopen, parse, and hash-verify the tiny canonical
   `receipt` through `write_launch_intent_exclusive`.

The measured 2700-second/2048-MiB interval begins after verified write-ahead
intent and before every scientific import; it ends only after durable RESULT
publication and the synchronous post-publication sample.  Intent transport
and the final tiny receipt publication are control-plane operations outside
that scientific interval.  This explicit endpoint resolves the unavoidable
fact that immutable RESULT bytes cannot contain a measurement taken after
their own completed publication.

## Z3. Provisional result and binding verdict

`M243_G0A_RESULT_20260809.json` is a scientific component receipt, not by
itself an authorization token.  It must say:

```text
adjudication_status = PROVISIONAL_PENDING_POSTPUBLICATION_RECEIPT
resource_adjudication = PENDING
g0a_pass = null
postpublication_receipt_required = true
postpublication_receipt_path = M243_G0A_POSTPUBLICATION_RECEIPT_20260809.json
g0b_sample_manifest_authorized = false
g0b_shards_authorized = false
relaunch_authorized = false
```

The binding verdict exists only in
`M243_G0A_POSTPUBLICATION_RECEIPT_20260809.json`.  The receipt must contain the
intent and RESULT hashes, runner/reference before-and-after hashes, PID and
process count, component verdict, exact elapsed wall, lifetime peak working
set, watchdog poll/breach/exception receipt, publication success, and all
firewall booleans.  It may set `g0a_pass=true` and
`g0b_sample_manifest_authorized=true` iff:

- the component receipt passes every frozen G0A gate and exact census;
- RESULT publication completed and its hash matches the receipt;
- the full measured interval passed both resource caps;
- no exception, interrupt, missing gate, unexpected gate, hash drift, or
  partial completion occurred; and
- intent, RESULT, and receipt bind the same one PID and authority snapshot.

The receipt always sets `g0b_shards_authorized=false` and
`relaunch_authorized=false`.

The receipt may authorize Codex only to construct the frozen sampled manifest;
it never directly authorizes Fable's shards.  RESULT alone can never open G0B.

Any intent without a valid matching receipt, any partial receipt, any second
intent, or any transport/hash mismatch is permanent G0A failure.  No relaunch
or threshold/cell/statistic repair is authorized.

## Z4. Mechanical fail-closed repairs

The repaired runner must additionally:

1. bind Win64 APIs exactly:

   ```python
   GetCurrentProcess.argtypes = ()
   GetCurrentProcess.restype = wintypes.HANDLE
   GetProcessMemoryInfo.argtypes = (
       wintypes.HANDLE,
       ctypes.POINTER(_ProcessMemoryCountersEx),
       wintypes.DWORD,
   )
   GetProcessMemoryInfo.restype = wintypes.BOOL
   ```

2. keep watchdog `join()` and final sampling inside `BaseException` handling
   so its own pending `KeyboardInterrupt` cannot suppress FAIL publication;
3. canonically tag nonfinite binary64 payload values instead of raising during
   result serialization; every such value still fails its scientific gate;
4. test the independently constructed 80-digit and 100-digit integrated
   candidate intervals separately for `Delta_ref` containment; cross-precision
   disagreement remains a separate gate and may not widen either interval;
5. preflight-hash all twelve parent artifacts frozen in the original
   manifest, the transitive M129 source, M237 helper, candidate, tests/static
   receipt, and the independently reviewed reference at
   `b03e9b2ddda22d8ea147c0720ca8644c91bff2d22c8f82bd057b91a55bdc2c25`;
   hash-only M213/M216/M224/M226 checks do not import their event values; and
6. return a nonzero process status for a binding G0A FAIL when control reaches
   normal witness publication.  The witness, not exit status alone, remains
   authoritative.

The runner cannot self-pin its own future repaired hash.  Before launch, a
new static validation receipt must freeze the repaired runner and reference
hashes, verify this erratum and its manifest/checksum receipt, and receive two
independent read-only PASS judgments.  Those exact hashes must be recorded in
the intent and remain unchanged through the witness.

## Z5. Preserved boundaries

G0A still grants at most a generated-only formula/component premise.  It
grants no total-support, provider, native-cost, source-variance, response,
truth, score, challenge-weight, leaderboard, integration, or submission
credit.  M196's B1/provider/compiler/native-trace firewall is unchanged.
No ledger, graph, champion, or claim-status edit is authorized by this
erratum or by a future G0A PASS.

## Z6. Exact downstream trigger

After a true binding receipt, Codex alone may create and validate the one
frozen sampled manifest.  Fable may act only on a committed append-only
`AGENT_CHANNEL.md` stanza with exactly:

```text
M243-G0B-FOUR-SHARD-TRIGGER-V1
g0a_pass=true
g0a_result_sha256=<64 lowercase hex>
g0a_postpublication_receipt_sha256=<64 lowercase hex>
sampled_manifest_sha256=<64 lowercase hex>
shard_count=4
```

Fable must locally verify both G0A hashes, their binding, the true receipt,
the sampled-manifest hash, frozen authority hashes, and absence of all shard
intent paths.  Maestro/WebSocket traffic, RESULT alone, receipt alone,
sampled-manifest existence alone, or an uncommitted mailbox message is not a
valid trigger.
