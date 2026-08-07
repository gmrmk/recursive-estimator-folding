# M120C operational harness second independent audit - 2026-08-07

## Verdict: `REPAIR`

Do not create the externally sealed schema-2 manifest and do not execute the
27-network/648-record grid yet.

The five deterministic blockers from the first operational audit are repaired:

1. configuration, runner, and lifecycle now name one exact outcome path;
2. gate cell keys are deterministic JSON strings in configuration order;
3. computation and publication are separated so a publication interruption
   cannot create a second, opposite failure outcome;
4. manifest digest verification and parsing consume one identical byte read;
5. the exact source closure now binds the executed `fullcov.py` and
   `adjoint_born.py` modules.

All **37/37 scoped tests passed**, including the new regression tests for those
repairs. Independent replay also passed the 27-Philox/648-record algebra, one
deepest/widest bounded analytic job, actual permutation/gauge recurrence,
claim-before-compute, no-retry, old-manifest rejection, runtime identity,
firewall, and the complete 11-file transitive local source closure.

One release-critical durability defect remains. `AtomicLifecycle` performs each
exclusive artifact write with one unchecked `os.write` call. A legal short write
can therefore publish a truncated outcome and then publish a terminal whose hash
describes the intended bytes rather than the bytes actually committed. This was
reproduced with a multi-megabyte outcome. It violates the claimed hash-bound,
exactly-one authoritative outcome protocol and is a narrow operational repair,
not a mathematical failure of M120C.

This audit did not edit the candidate, create a manifest, call the 27-job
dispatcher, execute the grid, or touch the canonical lifecycle root. All
mutation probes used temporary directories or in-memory manifest objects.

## Audited source identity

| file | SHA-256 |
|---|---|
| `m120c_protocol_config.py` | `492ede62bfd0b98ef26c4d6ea59a0237bc606a07e023dcd1f52479334582a119` |
| `m120c_protocol_harness.py` | `114c6990230c88864a7e2b85b999e7ff20bf9f0b73d98090fe21d7fe16ece475` |
| `run_m120c_protocol.py` | `9a7ea97be5a632c89a23fbdaee78a66a688ab5f2250fc26cd8deb839c35cd10d` |
| `m120c_analytic_dense_reference.py` | `f5e34f8ebc8ff2cafad63ccf55101155c802b01a36828bfc03edc820ad4a65f8` |
| `corrected_cp_jacobian.py` | `9bd61a90e53c1339a2717dcb3592865f75ff7a007db53952f3c9814d5d427f13` |
| `test_m120c_protocol.py` | `c26449cd9fcb23b231159c489e53d49ba97427bd6f2fb37c6a0aaa13c6d4f4fe` |
| `test_m120c_operational_harness.py` | `a64cdd1256b3a4a8bd49d7e2d0d280b8f2ba93f86258403b3dc166b16599bd1d` |
| `test_m120c_analytic_dense_reference.py` | `09c5d12e7534683cdee907b8d61b21af437678604621bd9f0f7eb7b9d9cf5f1f` |
| `test_corrected_cp_jacobian.py` | `8981f955c24f6502a9a6945d96c66cf899430b1d46f43a9ea2fa1259a2a8df5d` |
| executed `fullcov.py` | `091989fbb2249f792f595020e2a475982fd6c5605e51b83065a1837cf51492f6` |
| executed `adjoint_born.py` | `f83a5299de16131a435598a74fd2d6f9c56af6c19b4e7505ae481f4f38ae08bd` |
| checked-in obsolete manifest | `61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe` |

Pinned audit runtime:

```text
Python executable SHA-256  4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262
Python version            3.14.4
NumPy init SHA-256         65d5e777b6d662ba19cb80800bef3eb999eda7aee51eea62c308feabf679dba4
NumPy version              2.4.6
```

## Prior blockers: independent closure replay

### Exact outcome identity - `PASS`

The configuration defines

```text
.../out/M120C_EXACT_GENERATED_OUTCOME/m120c_binding_result.json
```

and the harness now derives both `CANONICAL_OUTCOME_PATH` and its root directly
from that value. Import-time code rejects any deviation from the source-derived
fixed path. A temporary lifecycle uses the exact canonical filename. Independent
checks established

```text
Path(CONFIG.output_path) == CANONICAL_OUTCOME_PATH
CANONICAL_OUTCOME_PATH.parent == CANONICAL_OUTCOME_ROOT
```

The canonical root was absent before and after the audit.

### JSON-safe ordered gates - `PASS`

A synthetic ledger containing all 648 required rows was evaluated. Both cell
maps serialize and deserialize exactly, and their insertion order is

```text
w8_d2, w8_d3, w8_d4,
w12_d2, w12_d3, w12_d4,
w16_d2, w16_d3, w16_d4
```

No tuple keys remain in the publication payload.

### One outcome and no opposite publication after injected boundaries - `PASS`

The runner's computation `try` now ends before success/fail publication. An
injected interruption after outcome replacement propagates directly; it is not
caught as a computation failure and does not attempt an error outcome. Separate
temporary-root probes at `after_outcome_pending`, `after_terminal_pending`, and
`after_outcome_replace` left at most one final outcome, preserved the pending
forensic evidence appropriate to the boundary, and permanently rejected both a
second outcome and a second claim. No legacy `M120C_RESULT.json` or
`M120C_FAILURE.json` appeared.

With normal full writes, the sole outcome, sole terminal, and claim were the
only final artifacts, and the terminal hash equaled the hash of the actual
outcome file.

### One-read manifest digest and parse - `PASS`

`closed_manifest_errors` now captures `raw = path.read_bytes()` once, decodes
that buffer, and computes `sha256(raw)`. An in-memory complete schema-2 manifest
whose object raises on a second `read_bytes` call passed with exactly one call
and no errors. Thus the externally supplied digest binds the bytes that are
actually parsed, including under Windows path semantics.

### Exact transitive local source closure - `PASS`

An independent AST import traversal started from the nine operational and test
modules and resolved the dynamically exposed local imports in
`corrected_cp_jacobian.py`. The reachable set was exactly 11 files and was
set-equal to `EXPECTED_SOURCE_KEYS`: no missing and no extra keys.

In particular, it includes

```text
scorefloor_generation/fullcov_gaussian_mm/fullcov.py
scorefloor_generation/adjoint_cumulant/adjoint_born.py
```

Both modules are imported and executed by the CP carrier and are now hash-bound.

## Remaining blocker: unchecked short writes - `REPAIR`

The current exclusive writer is operationally equivalent to

```python
fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_BINARY)
try:
    os.write(fd, data)
    os.fsync(fd)
finally:
    os.close(fd)
```

`os.write` is permitted to write fewer than `len(data)` bytes. The return value
must be consumed; a successful return is not a full-write guarantee. This is
especially relevant to the multi-megabyte evidence ledger and remains a valid
failure mode on Windows.

The hostile probe patched only the first outcome `os.write` so that it performed
a real write of one third of the supplied buffer and returned that short count.
The second call, which wrote the terminal, was normal. Observed result:

```text
publish_outcome returned normally       true
intended outcome bytes                  4,194,328
actual committed outcome bytes          1,398,109
actual outcome JSON parseable           false
final outcome exists                    true
final terminal exists                   true
terminal outcome SHA-256                145f51ce7ec303d09075e034c629b17696a176790b7988baceeb8f53ecb38ef7
actual outcome SHA-256                  96a0a646392c408b93ea8a5f8030ce88b56ca54122ad7fe137dcff67fa8681c4
hashes equal                            false
```

This is not merely a pending/interruption state. Both final artifacts exist and
publication reports success, while the final outcome is truncated and the
terminal falsely certifies a different byte string. The same primitive writes
the claim and terminal, so a short claim can also be accepted as authorization
evidence and a short terminal can be silently finalized.

Required repair:

1. write through a `memoryview` in a loop until the full buffer is consumed;
2. retry `InterruptedError` without advancing the view;
3. treat a returned count `<= 0` or a count outside the remaining length as a
   fail-closed write error;
4. call `fsync` only after every intended byte has been written;
5. preserve the pending artifact on any failure so no retry can reinterpret the
   consumed run;
6. add regression probes for short, zero, and interrupted writes of claim,
   outcome, and terminal, including a multi-megabyte outcome and a final check
   that the terminal digest equals the bytes actually committed.

Hashing the truncated file after the fact is not an acceptable substitute: it
would merely authenticate incomplete or invalid JSON. The primitive must ensure
complete durable bytes before either same-directory rename.

## Frozen plan, analytic use, and representation evidence

The prospective plan remains exact without dispatching it:

```text
3 widths x 3 depths x 3 replicas       27 jobs
unique network Philox seeds            27
seed formula                           root + 100000*w + 1000*d + replica
sum over jobs of (depth-1)*width       648 records
predeclared direction seeds            72 unique Philox seeds
direction formula                      root + 10000*w + 1000*d + 100*layer + k
```

The direction namespace contains no output, replica, outcome, selection, or
retry index.

One independently selected maximum bounded job `(width=16, depth=4, replica=0)`
was executed through the per-job primitive, not the dispatcher. It emitted all
48 layer/output rows. Instrumentation observed three calls to
`analytic_local_kernels` and three calls to `analytic_dense_pullback`; every row
was finite and contained both complete standardized reference and CP states.
The actual scheduled simultaneous hidden permutation/positive-gauge check also
passed on that same job. This reconfirms operational use of the approved
analytic reference and the complete representation invariant at a multi-hidden
shape.

## Claim, manifest, firewall, and tests

A mocked no-grid runner probe observed the permanent claim on disk inside the
first computation callback. The run then published one normal temporary outcome
and terminal; a second call was rejected because the root was consumed. Thus
claim-before-compute and no-retry are structurally active, apart from the shared
short-write primitive identified above.

The checked-in schema-1 manifest remains non-authorizing. Even when supplied
with its own raw SHA-256, the operational checker rejected it for schema/status,
root field set, fixed output, execution mode, atomic declaration, runtime, and
source key set.

Static compile and import inspection of all 11 bound local files passed. No
`requests`, `urllib`, `socket`, HTTP URL, AIcrowd, or leaderboard access was
found. The exact firewall remains:

```text
generated networks only
no correction oracle
no source construction
no public or contest outcomes
no targets
no scorer
no champion access
no target-shape efficacy execution
```

Executed test command used the pinned interpreter and one thread for BLAS/OpenMP:

```text
python -m unittest -v \
  test_m120c_protocol \
  test_m120c_operational_harness \
  test_m120c_analytic_dense_reference \
  test_corrected_cp_jacobian

Ran 37 tests in 0.462s - OK
```

No test invoked `all_generated_metric_records` against the real dispatcher.

## Release decision

The repair is close: all five previously known blockers are now closed and the
mathematical/analytic evidence remains intact. But an external freeze would
bind a one-shot run whose writer can silently commit fewer bytes than the
terminal claims. Because the root is intentionally non-retryable, that defect
must be fixed before consuming it.

After the full-write primitive and its hostile regressions are added, recompute
all affected hashes and perform one final independent source-only audit with the
schema-2 manifest and canonical root still absent. Until then the honest verdict
is `REPAIR`, not `PASS_TO_EXTERNAL_FREEZE`.
