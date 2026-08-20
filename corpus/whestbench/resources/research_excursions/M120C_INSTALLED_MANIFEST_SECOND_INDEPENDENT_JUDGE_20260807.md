# M120C installed manifest second independent judge - 2026-08-07

## Verdict: `PASS_TO_ONE_SHOT_EXECUTION`

The resealed M120C installed state passes the required second independent
manifest audit. The stale installed-manifest test contract identified by the
first judge was repaired, the operational manifest was resealed against that
single changed test hash, and both required runtime lanes now pass all 41 tests
with zero calls to the real generated-grid dispatcher.

This judgment completes the release's required second independent audit. The
only valid one-shot owner token for this installed state is the raw sealed
manifest SHA-256:

```text
a501fe1bf03d80b430eaa852be980d27822e1945f913b60f151ce1cd88cd1645
```

The verdict does not execute the owner and does not weaken any one-shot
condition. Execution remains a distinct explicit action. It must use exactly
the digest above under the pinned runtime, while the canonical root is absent;
any mismatch or pre-existing claim/pending/outcome/terminal state fails closed,
and no retry is permitted.

This judge did not directly import the `run_authorized_m120c_grid` symbol, call
the authorized owner, call the real `all_generated_metric_records`, create a
manifest, execute a generated network grid, create canonical lifecycle state,
or access contest, target, scorer, public-outcome, leaderboard, or champion
data. The scoped tests necessarily load the owner module; their two owner-path
probes replace its dispatcher with an empty result or injected failure. Outer
fail-fast guards independently recorded zero real dispatcher calls.

## Required artifact chain

| artifact | required SHA-256 | observed SHA-256 | result |
|---|---|---|---|
| installed `m120c_protocol_manifest.json` v2 | `a501fe1bf03d80b430eaa852be980d27822e1945f913b60f151ce1cd88cd1645` | `a501fe1bf03d80b430eaa852be980d27822e1945f913b60f151ce1cd88cd1645` | PASS |
| resealed release v2 | `f7c10fab510a06b6177a5703cf622dd7a63c790d624bec40a80d4ed37aff1b73` | `f7c10fab510a06b6177a5703cf622dd7a63c790d624bec40a80d4ed37aff1b73` | PASS |
| archived sealed manifest v1 | `a46e838dc13b3d3a9c9aa2ccc4ad6c80ab3c2e0b9362afb02e71e42231f681e0` | `a46e838dc13b3d3a9c9aa2ccc4ad6c80ab3c2e0b9362afb02e71e42231f681e0` | PASS |
| repaired `test_m120c_protocol.py` | `fdc1c5c88a19ec0a3a4a180fe3d95579d2da1a4e928edb9b113ef9402bd43e02` | `fdc1c5c88a19ec0a3a4a180fe3d95579d2da1a4e928edb9b113ef9402bd43e02` | PASS |
| final operational harness audit | `ec9b7f8463bda5e8a7780c9c9ac2e20c1c2f282b42c5ce83138ea8eb23fdf3c2` | `ec9b7f8463bda5e8a7780c9c9ac2e20c1c2f282b42c5ce83138ea8eb23fdf3c2` | PASS |
| first installed-manifest judge | `26ddc50af7097a41a860498bb865e4a5ac560e256cd3911703cda9ea1cf50486` | `26ddc50af7097a41a860498bb865e4a5ac560e256cd3911703cda9ea1cf50486` | PASS |
| preserved preexecution manifest | `61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe` | `61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe` | PASS |

The release JSON itself is exactly schema 2 with

```text
release_id = M120C-EXTERNAL-EXECUTION-RESEAL-v2-20260807
state      = AUTHORIZED_FOR_SECOND_INDEPENDENT_MANIFEST_AUDIT_NOT_EXECUTION
```

Its sealed-manifest path, digest, `OPERATIONAL_SEALED` status, archived-v1
binding, repaired-test binding, final-audit binding, and first-judge binding all
match the observed artifacts. Its execution contract remains exactly:

```text
atomic                                      true
one_shot                                    true
retry_allowed                               false
execution_authorized_by_this_release        false
second_independent_manifest_audit_required  true
```

That pre-judgment state is correct: the release file did not authorize itself.
This independent `PASS_TO_ONE_SHOT_EXECUTION` verdict is the required second
judgment, while the manifest digest remains the exact owner token.

## Proof that manifest v1 to v2 changed only one test hash

Both manifests are 3,301 bytes. A recursive comparison of their parsed JSON
trees found exactly one differing leaf:

```text
source_sha256/
  scorefloor_generation/m120_price_normal_ordered_adjoint/test_m120c_protocol.py
```

Its values are:

```text
v1  c26449cd9fcb23b231159c489e53d49ba97427bd6f2fb37c6a0aaa13c6d4f4fe
v2  fdc1c5c88a19ec0a3a4a180fe3d95579d2da1a4e928edb9b113ef9402bd43e02
```

There were no added, removed, reordered, or differently formatted fields. The
strong raw-byte check also passed: the v2 byte string contains the new digest
once, the v1 byte string contains the old digest once, and replacing that one
64-byte v2 digest with the v1 digest reproduces the entire archived v1 file
byte-for-byte. Sixty character positions differ because four hexadecimal
positions happen to coincide. This proves the release's declared reseal delta,
not merely structural similarity.

## Complete installed source closure

All 11 v2 manifest source bindings independently matched the actual files:

| source | SHA-256 |
|---|---|
| `m120c_protocol_config.py` | `492ede62bfd0b98ef26c4d6ea59a0237bc606a07e023dcd1f52479334582a119` |
| `m120c_protocol_harness.py` | `cbf75ed3f392f0c29bfd9b2ece13b580d2a9068a930d8dc05d251a74d69201de` |
| `run_m120c_protocol.py` | `9a7ea97be5a632c89a23fbdaee78a66a688ab5f2250fc26cd8deb839c35cd10d` |
| `m120c_analytic_dense_reference.py` | `f5e34f8ebc8ff2cafad63ccf55101155c802b01a36828bfc03edc820ad4a65f8` |
| `corrected_cp_jacobian.py` | `9bd61a90e53c1339a2717dcb3592865f75ff7a007db53952f3c9814d5d427f13` |
| `test_m120c_protocol.py` | `fdc1c5c88a19ec0a3a4a180fe3d95579d2da1a4e928edb9b113ef9402bd43e02` |
| `test_m120c_operational_harness.py` | `6c050d6a9096dd892ee6ed6cb3cd37afd1ff53e190b82f49d93409f61432174d` |
| `test_m120c_analytic_dense_reference.py` | `09c5d12e7534683cdee907b8d61b21af437678604621bd9f0f7eb7b9d9cf5f1f` |
| `test_corrected_cp_jacobian.py` | `8981f955c24f6502a9a6945d96c66cf899430b1d46f43a9ea2fa1259a2a8df5d` |
| `fullcov.py` | `091989fbb2249f792f595020e2a475982fd6c5605e51b83065a1837cf51492f6` |
| `adjoint_born.py` | `f83a5299de16131a435598a74fd2d6f9c56af6c19b4e7505ae481f4f38ae08bd` |

The manifest key set is exactly equal to the harness's declared expected source
set. No bound source was missing and there was no unrecognized extra binding.

## Pinned-runtime installed validation

The pinned interpreter and NumPy identity were independently recomputed:

```text
Python executable  work/whest-v014/Scripts/python.exe
Python version     3.14.4
Python SHA-256     4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262
NumPy version      2.4.6
NumPy init SHA-256 65d5e777b6d662ba19cb80800bef3eb999eda7aee51eea62c308feabf679dba4
```

The runtime dictionary is identical in the installed manifest and release.
Using the independently observed manifest digest:

```text
closed_manifest_errors(installed, a501fe1b...) == ()
manifest_errors(installed)                     == ()
```

The guarded pinned `unittest` replay reported:

```text
tests run              41
failures               0
errors                 0
real dispatcher calls  runner=0, harness=0
```

The stale freeze-order assertion is therefore repaired in the installed state.
It now explicitly requires the preserved preexecution manifest to reject and
requires the current installed manifest to accept under its pinned runtime.

## Headroom runtime-only semantics

The separate Headroom recursion environment was:

```text
Python executable  work/headroom-recursion/.venv/Scripts/python.exe
Python version     3.12.13
Python SHA-256     5912d0884b23c0343983a864c6064242391e2265536f50b88624857e353882c9
NumPy version      2.5.1
NumPy init SHA-256 a6958cb364663b7acce81ccfd58eeb65a2b34d5376157f924777b97211a73be4
pytest version     9.1.1
```

Under that deliberately non-pinned runtime:

```text
closed_manifest_errors(installed, a501fe1b...)
    == ("runtime identity mismatch",)
manifest_errors(installed) == ()
pytest: 41 passed, 26 subtests passed
real dispatcher calls: runner=0, harness=0
```

This is the required runtime-only behavior. The repaired test does not pretend
that Headroom is the execution runtime: when runtime identity differs, it
requires exactly the single runtime mismatch while still proving all source,
schema, grid, firewall, and digest bindings are intact. Actual one-shot
execution remains pinned to `whest-v014`.

## Static frozen-plan and no-dispatch proof

The plan was recomputed from the parsed frozen configuration without importing
or calling the generated dispatcher:

```text
3 widths x 3 depths x 3 replicas                27 jobs
sum width x (depth - 1) x 3 over all cells      648 records
network Philox seeds                            27 present, 27 unique
network seed algebra                            exact
signed-direction Philox schedule                72 directions
```

AST inspection of all four test modules found zero direct calls to
`all_generated_metric_records`. During both runtime replays, fail-fast guards
were installed on both the owner alias and harness definition. Both counters
remained zero. The two source-only owner tests temporarily replace the owner
alias inside their own contexts, so they exercise publication/error state
transitions without reaching generated computation.

## One-shot/no-retry lifecycle and firewall

Static owner ordering is exactly:

```text
closed manifest preflight
  -> reject existing canonical root
  -> exclusive permanent claim
  -> one generated dispatcher call
  -> one canonical outcome publication
  -> hash-bound terminal publication
```

The owner has no grid-running CLI. The lifecycle creates the root with
`exist_ok=False`, uses `O_EXCL` artifact creation, completes the repaired
full-write loop before fsync, and rejects any existing pending or final
publication artifact. Pass, fail, and computation-error payloads all bind
`retry_allowed: false`. No retry loop or alternate output path exists.

The release and installed manifest firewall are identical to the harness's
exact expected tuple:

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

Static inspection of all 11 bound source files found no network client, HTTP
URL, AIcrowd, leaderboard, scorer, target, public-result, or champion-access
path. This judgment accessed none of those data classes.

## Canonical state at judgment

The manifest-fixed outcome remains:

```text
work/scorefloor_generation/m120_price_normal_ordered_adjoint/
  out/M120C_EXACT_GENERATED_OUTCOME/m120c_binding_result.json
```

At the start and completion of this review:

```text
out/ parent                               absent
M120C_EXACT_GENERATED_OUTCOME/ root       absent
M120C_CLAIM.json                          absent
m120c_binding_result.json                 absent
M120C_TERMINAL.json                       absent
```

No one-shot state has been consumed.

## Execution boundary

All requested installed-state conditions are satisfied. A later explicit owner
invocation may therefore proceed exactly once with the pinned interpreter and
the manifest token
`a501fe1bf03d80b430eaa852be980d27822e1945f913b60f151ce1cd88cd1645`.
It must not substitute the release-file hash, archived v1 hash, report hash, or
any self-computed value from modified bytes. The call itself is outside this
audit and remains subject to the generated-only firewall and permanent
no-retry claim.

Final verdict: `PASS_TO_ONE_SHOT_EXECUTION`.
