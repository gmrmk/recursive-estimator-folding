# M120C operational harness final independent audit - 2026-08-07

## Verdict: `PASS_TO_EXTERNAL_FREEZE`

The repaired M120C operational harness is ready for an independently sealed
schema-2 manifest. This verdict authorizes the **external freeze step only**. It
does not itself authorize execution of the 27-network/648-record grid.

The unchecked-short-write blocker from the second audit is closed. The writer
now loops over a `memoryview`, advances only by a strictly positive exact Python
integer no larger than the remaining buffer, retries `InterruptedError` without
advancing, and calls `fsync` only after all intended bytes have been accepted.
Independent attacks covered actual short writes, zero, negative, oversized,
floating-point, NumPy-integer, Boolean, and `None` return values at claim,
outcome, and terminal stages. A multi-megabyte claim and outcome were persisted
exactly, and the terminal digest matched the SHA-256 of the actual outcome file.

All five blockers from the first operational audit remain closed. The exact
41-test scoped suite passed. Independent replay also passed the prospective
27-Philox/648-record algebra, deepest/widest bounded analytic job, actual
permutation/gauge recurrence, exact source closure, one-read manifest identity,
claim-before-compute/no-retry, old-manifest rejection, runtime identity, and
firewall checks.

This audit did not edit candidate source, create or rewrite a manifest, invoke
`all_generated_metric_records`, execute the binding grid, or create the
canonical claim/outcome/terminal root. All lifecycle mutation probes used
temporary directories, and the complete schema-2 manifest probe existed only
as an in-memory byte string.

## Frozen source identity

| file | SHA-256 |
|---|---|
| `m120c_protocol_config.py` | `492ede62bfd0b98ef26c4d6ea59a0237bc606a07e023dcd1f52479334582a119` |
| `m120c_protocol_harness.py` | `cbf75ed3f392f0c29bfd9b2ece13b580d2a9068a930d8dc05d251a74d69201de` |
| `run_m120c_protocol.py` | `9a7ea97be5a632c89a23fbdaee78a66a688ab5f2250fc26cd8deb839c35cd10d` |
| `m120c_analytic_dense_reference.py` | `f5e34f8ebc8ff2cafad63ccf55101155c802b01a36828bfc03edc820ad4a65f8` |
| `corrected_cp_jacobian.py` | `9bd61a90e53c1339a2717dcb3592865f75ff7a007db53952f3c9814d5d427f13` |
| `test_m120c_protocol.py` | `c26449cd9fcb23b231159c489e53d49ba97427bd6f2fb37c6a0aaa13c6d4f4fe` |
| `test_m120c_operational_harness.py` | `6c050d6a9096dd892ee6ed6cb3cd37afd1ff53e190b82f49d93409f61432174d` |
| `test_m120c_analytic_dense_reference.py` | `09c5d12e7534683cdee907b8d61b21af437678604621bd9f0f7eb7b9d9cf5f1f` |
| `test_corrected_cp_jacobian.py` | `8981f955c24f6502a9a6945d96c66cf899430b1d46f43a9ea2fa1259a2a8df5d` |
| executed `fullcov.py` | `091989fbb2249f792f595020e2a475982fd6c5605e51b83065a1837cf51492f6` |
| executed `adjoint_born.py` | `f83a5299de16131a435598a74fd2d6f9c56af6c19b4e7505ae481f4f38ae08bd` |
| checked-in obsolete manifest | `61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe` |

Pinned runtime identity:

```text
Python executable SHA-256  4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262
Python version              3.14.4
NumPy init SHA-256          65d5e777b6d662ba19cb80800bef3eb999eda7aee51eea62c308feabf679dba4
NumPy version               2.4.6
```

## R1: hostile write and lifecycle audit - `PASS`

### Multi-megabyte real short writes

The mock did not merely lie about return counts. Each call performed a real
write of at most half the remaining memoryview and returned the actual short
count. It forced multiple writes for every artifact:

| artifact | intended bytes | actual bytes | `os.write` calls | exact |
|---|---:|---:|---:|---|
| claim | 1,048,646 | 1,048,646 | 22 | yes |
| outcome | 4,194,444 | 4,194,444 | 24 | yes |
| terminal | 155-byte class | identical canonical bytes | 9 | yes |

There were exactly three `fsync` calls, each after the corresponding complete
write sequence. Final files were exactly:

```text
M120C_CLAIM.json
M120C_TERMINAL.json
m120c_binding_result.json
```

The actual persisted outcome SHA-256 was

```text
8aba0b233716473a8d1fbef931f5fb7ecdb268de0b5778fd93d2e2ea8d55110e
```

and the parsed terminal contained that identical digest. The outcome was also
byte-equal to the canonical serialization produced before publication.

This closes the exact corruption reproduced in the second audit, where one
unchecked write had silently committed only one third of the intended outcome
while finalizing a terminal for different bytes.

### Interrupted writes

An `InterruptedError` was injected before the first successful write of each of
claim, outcome, and terminal. All three interruptions were retried; no buffer
position was advanced by the exception. The three final artifacts were exact,
three fsyncs occurred, and the terminal digest matched the actual outcome.

### Invalid byte-count matrix

The following hostile return classes were each injected independently:

```text
0
-1
len(remaining) + 1
1.0
numpy.int64(1)
True
None
```

Every class was tested at all three stages, for 21 independent stage/type
combinations. `type(written) is int` correctly excludes Boolean and NumPy
integer subclasses as well as floats and `None`.

| injected stage | observed invariant |
|---|---|
| claim | `ProtocolFailClosed`; zero fsyncs; authorized runner made zero compute calls; no outcome or terminal; root permanently consumed |
| outcome | `ProtocolFailClosed`; zero fsyncs; outcome pending retained; no final outcome or terminal; second publication rejected |
| terminal | completed outcome pending fsynced once; invalid terminal rejected before its fsync; both pending files retained; no final outcome or terminal; second publication rejected |

All 21 combinations satisfied the expected fsync count, retained the applicable
audit evidence, produced no final outcome or terminal, and permanently rejected
retry. A separate authorized-runner probe with a zero-count claim confirmed the
claim failure occurs before `all_generated_metric_records`: computation call
count was zero, outcome and terminal were absent, and the second runner call was
blocked by the consumed root.

### Publication-boundary interruptions

Independent fault injection was repeated after each publication boundary:

| boundary | final outcome count | retained evidence | retry |
|---|---:|---|---|
| after outcome pending | 0 | claim + outcome pending | blocked |
| after terminal pending | 0 | claim + both pending files | blocked |
| after outcome replace | 1 | claim + final outcome + terminal pending | blocked |
| after terminal replace | 1 | claim + final outcome + final terminal | blocked |

The runner's publication remains outside its computation exception handler, so
a publication interruption does not attempt an opposite error outcome. No
legacy `M120C_RESULT.json` or `M120C_FAILURE.json` was produced.

## Prior five repair closures - `PASS`

### One canonical config/lifecycle path

Independent equality checks passed:

```text
Path(CONFIG.output_path) == CANONICAL_OUTCOME_PATH
CANONICAL_OUTCOME_PATH.parent == CANONICAL_OUTCOME_ROOT
```

The lifecycle uses `m120c_binding_result.json`, exactly the filename sealed by
configuration. Import-time source-derived path validation remains active.

### JSON-safe ordered gates

A complete synthetic 648-record ledger passed exact JSON round-trip. Both cell
maps use deterministic string keys in this order:

```text
w8_d2, w8_d3, w8_d4,
w12_d2, w12_d3, w12_d4,
w16_d2, w16_d3, w16_d4
```

### Exactly one outcome and hash-bound terminal

Normal publication produced one canonical outcome and one terminal whose digest
equals the bytes read back from the outcome. Every interruption or invalid write
either retained only pending evidence or retained the already committed single
outcome; no second/opposite outcome path exists.

### Single-read manifest identity

An in-memory complete schema-2 manifest object raises if `read_bytes` is called
twice. `closed_manifest_errors` called it exactly once and returned no errors
when supplied the SHA-256 of those same captured bytes. Hash verification and
JSON parsing therefore bind one identical byte string.

### Complete transitive local source closure

An independent AST import traversal from the nine operational/test roots found
exactly 11 reachable local source files. That set was exactly equal to
`EXPECTED_SOURCE_KEYS`, with no missing or extra entries, including:

```text
scorefloor_generation/fullcov_gaussian_mm/fullcov.py
scorefloor_generation/adjoint_cumulant/adjoint_born.py
```

Both imported CP dependencies are now part of the external hash contract.

## R2/R5: frozen mathematics and representation - `PASS`

The prospective combinatorics were recomputed without running the dispatcher:

```text
3 widths x 3 depths x 3 replicas       27 jobs
unique network Philox seeds            27
network seed formula                   root + 100000*w + 1000*d + replica
sum over jobs of (depth-1)*width       648 records
unique signed-direction Philox seeds   72
direction seed formula                 root + 10000*w + 1000*d + 100*layer + k
network/direction seed overlap         0
```

The direction namespace contains no output, replica, outcome, selection, or
retry index.

One maximum bounded job `(width=16, depth=4, replica=0)` was evaluated through
the per-job primitive only. It produced all 48 hidden-layer/output records.
Instrumentation observed three actual `analytic_local_kernels` calls and three
actual `analytic_dense_pullback` calls. Every metric and signed direction was
finite, and every row contained the complete standardized reference and CP
states. The frozen simultaneous hidden permutation/positive-gauge recurrence
check passed on the same deepest/widest job.

Thus the approved analytic reference remains operationally used, and the actual
dense/CP recurrence comparison—not merely a helper identity—retains the
representation invariant.

## Manifest, runtime, firewall, and tests - `PASS`

The checked-in schema-1 manifest remains non-authorizing. Even with its actual
raw digest supplied, the operational checker rejected it for schema/status,
root field set, fixed output path, execution mode, atomic declaration, runtime,
and source key set. No schema-2 manifest was written by this audit.

All 11 bound files compiled in memory. Static import/text inspection found no
`requests`, `urllib`, `socket`, HTTP URL, AIcrowd, or leaderboard access. The
exact manifest firewall remains:

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

The scoped test command used the pinned runtime with all relevant thread counts
fixed to one:

```text
python -m unittest -v \
  test_m120c_protocol \
  test_m120c_operational_harness \
  test_m120c_analytic_dense_reference \
  test_corrected_cp_jacobian

Ran 41 tests in 0.546s - OK
```

Neither the test suite nor the independent probes called the real 27-job
dispatcher.

## Absent canonical state and release boundary

Before and after every check:

```text
out/M120C_EXACT_GENERATED_OUTCOME/   absent
canonical claim                     absent
canonical outcome                   absent
canonical terminal                  absent
operational schema-2 manifest       absent
```

The source bytes, runtime identity, tests, and complete import closure are now
sufficiently closed for an independent party to construct and seal the schema-2
manifest against the hashes above. After that distinct freeze artifact is
created, execution still requires a separate explicit authorization carrying
the independently communicated raw manifest SHA-256.

Final verdict: `PASS_TO_EXTERNAL_FREEZE`.
