# M245 scientific implementation authorization 1 -- dummy-only GREEN

Date: 2026-08-10 UTC  
Status: `FROZEN_DOCS_ONLY_PENDING_INDEPENDENT_AUDIT_AND_COMMIT`

This append-only authorization closes the implementation gap after the
repaired four-lane RED bundle. It authorizes construction and dummy-only
verification of one exact six-file implementation candidate. It is not a
scientific launch, pretrigger census, trigger, shard, aggregation, provider,
response, score, or credit authority.

This file is ineffective while uncommitted. It becomes effective only if an
independent read-only audit returns `PASS`, then this file and
`M245_SHA256SUMS_SCIENTIFIC_IMPLEMENTATION_AUTHORIZATION_20260810.txt` are
committed without byte changes in one docs-only commit whose sole parent is
`a0520dfb018f3a457587a060959ddfc44e1ed2ef`. That commit may add exactly those
two files and may not change any bound artifact. Its future commit hash is not
embedded here.

## I1.1 Authority lineage and precedence

The exact lineage is:

```text
dddd874b19c15396da8981b20db3aa260831e7cb  sealed V2 fixture authority
979f7c35334ff0df09ad134255fddf23f944237f  Erratum2 repaired-RED authority
65ffe3f82198609acd88594266a8c3c3ba1d9640  frozen repaired-RED ancestor
a0520dfb018f3a457587a060959ddfc44e1ed2ef  coordination-only AGENT_CHANNEL parent
```

The commits have the first-parent relations `a0520df... -> 65ffe3f... ->
979f7c...`, and the V2 commit is an ancestor of all three. Interposed commit
`a0520df...` changes only `AGENT_CHANNEL.md` to record the Fable coordination
handoff; it changes no bound RED artifact and is not a scientific trigger or
launch authority. The implementation-authority commit must have `a0520df...`
as its sole parent.

For authorization fields only, this file supersedes the implementation and
GREEN prohibitions in section E2.2 of
`M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md` and the stop line of
`M245_SCIENTIFIC_TDD_RED_RECEIPT_V2_20260810.md`, and only to the narrow extent
listed below. Erratum2 E2.3--E2.10, the V2 science, numerical policy,
dispositions, resource rules, firewalls, and no-credit boundary remain
unchanged. A permission below never widens a neighboring prohibition.

The live bound authority and RED artifacts are:

```text
0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b  M245_FROZEN_MANIFEST_V2_20260810.json
2e56bd140b71527f640e1c1afbbc347fcca601fa4f0ec83f711c69a29e2b444e  M245_SHA256SUMS_V2_20260810.txt
8641de9ec301ba402b87e50dd8c5e3322a6532313f1d603c54356a4137e21587  M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md
401629468b5ec1f2eb5447b650b10f27fb47ba7ce3af74c740a230feeefcceaf  M245_SHA256SUMS_V2_OVERLAY2_20260810.txt
5497b1397a62bbfb4f3be73a02f2b63872e01f2bd4795b77232e7c6c287beb85  M245_SCIENTIFIC_TDD_RED_RECEIPT_20260810.md
ea6aae1a8fa82e5e8f2fa2f89574e9f46f178e138dbea24a99b38f550ccfec57  M245_SCIENTIFIC_TDD_RED_RECEIPT_V2_20260810.md
669df0111cbda4c0d7a2d4b694254e54ba9b85f69eaf3f6aefb5b16fa296893d  M245_SHA256SUMS_SCIENTIFIC_TDD_RED_V2_20260810.txt
355820f372c0e0b7b466ed98f3db2a36b92142927c494406b3f5dbdb5c26d626  test_m245_primary_core.py
e7eceb023b725badb06d59773b7813d2083d3dfd33fffa7fd35fcedf2055fa21  test_m245_replica_core.py
112869bf75a127ae706dcc1346c070f128c15c74a125d1818646fbf46fd5294d  test_m245_scientific_transport.py
6d723cde0a9784cc20bf0a41b25ab4599f8c103f1c3de04cba0d6e8b9336a4e6  test_m245_aggregation.py
```

The first receipt also records these four historical, pre-repair test hashes:

```text
223dcc0eae654adc663bd5a26e99da737da6caa8304b9a5bdd8525b9b84b5fe2  historical test_m245_primary_core.py
2fafd424836a388838ee912925cf24a332c881ffa07bef1cf29265f3291de44c  historical test_m245_replica_core.py
1933f16628650440883b1675af0ce1057543ded34fec12fca0700ccc9b9d0382  historical test_m245_scientific_transport.py
a8558becaf0c832347b758b585450527712583730ed3397b8cb79abea05a6ebe  historical test_m245_aggregation.py
```

Those historical bytes were never committed, no longer exist at the live
paths, and are not implementation targets. They remain bound only as honest
RED history. The four repaired hashes in the preceding table are the sole
test authority for this implementation.

Any byte drift, missing artifact, non-ancestor checkout, alternate path, or
different parent is `BLOCKED_IMPLEMENTATION_PARENT_DRIFT`. It authorizes no
repair, substitution, execution, or inference.

## I1.2 Exact state at authorization freeze

At immediate parent `a0520df...`, with frozen RED ancestor `65ffe3f...`, all
six production paths are lexically absent:

```text
m245_primary_core.py                    absent
m245_replica_core.py                    absent
m245_scientific_worker.py               absent
run_m245_scientific_shard.py            absent
launch_m245_scientific_invocation.py    absent
aggregate_m245_spectrum.py              absent
```

The four repaired tests and both RED receipts are present at the exact hashes
in I1.1. The V2 RED checksum is present at its exact hash. No GREEN output,
implementation/static-validation receipt, real shard namespace, pretrigger
census, scientific trigger, aggregation authority, aggregation intent,
aggregation output, or aggregation receipt exists. In particular these paths
are absent:

```text
M245_SCIENTIFIC_TDD_GREEN_RECEIPT_20260810.md
M245_SHA256SUMS_SCIENTIFIC_TDD_GREEN_20260810.txt
M245_SCIENTIFIC_STATIC_AUDIT_CONTRACT_20260810.md
M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json
M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json
M245_SCIENTIFIC_STATIC_VALIDATION_RECEIPT_20260810.json
M245_PRETRIGGER_ZERO_INTENT_CENSUS_20260810.json
M245_AGGREGATION_INPUT_AUTHORIZATION_20260810.json
.M245_AGGREGATION_INTENT_20260810.json.tmp
M245_AGGREGATION_INTENT_20260810.json
.M245_AGGREGATED_SPECTRUM_20260810.json.tmp
M245_AGGREGATED_SPECTRUM_20260810.json
.M245_AGGREGATION_RECEIPT_20260810.json.tmp
M245_AGGREGATION_RECEIPT_20260810.json
```

The real directory
`corpus/whestbench/experiments/m245_fable_spectrum_shards` is absent, hence all
eight E00:E07 durable intent, result, checkpoint, meter, provisional receipt,
terminal-witness, and final-shard paths are absent. The implementation owner
must repeat this exact census after the implementation-authority commit and
before creating the first production file. Any unexpected presence is a hard
stop.

## I1.3 Exact authorization matrix

```text
create the six production files in I1.4                    true, once each
edit or replace any of the four frozen tests               false
create any seventh M245 production/helper module           false
perform read-only static inspection of the six sources     true
run the four exact dummy-only GREEN commands in I1.7       true, once each
create test-owned transient dummy files/processes          true, I1.7 only
create the GREEN receipt and non-self-hashing checksum      true, once
commit the exact GREEN candidate/evidence after success    true, once
evaluate E00:E07 or decode a real fixture into math         false
use fixture values beyond canonical schema/hash checks     false
run a production main/outer/supervisor/worker dispatch     false
emit the pretrigger zero-intent census                      false
create a scientific trigger or AGENT_CHANNEL GO entry      false
create any real shard namespace file or durable intent     false
create an aggregation input authorization                  false
aggregate real receipts or publish authority-dir output    false
exercise frozen dummy aggregation in isolated temp dirs    true, I1.7 only
read scorer, truth, response, holdout, or sealed cells      false
construct or deploy a provider or estimator response       false
claim science, efficacy, score, FLOP, component, or credit  false
network access, submission, retry, redraw, or reseed        false
```

The authorized dummy process-tree probe in the transport test is not a shard
attempt. It must use only a test-owned temporary directory and the literal
dummy event declared by the frozen test. It may not touch the real shard
directory or any E00:E07 namespace. The authorized dummy aggregation tests
may create only their isolated temporary files and temporary Git repositories;
they may not create an M245 aggregation artifact in the authority directory.

## I1.4 Frozen six-file implementation split

Exactly these six sibling production files may be created:

```text
P  m245_primary_core.py
R  m245_replica_core.py
W  m245_scientific_worker.py
S  run_m245_scientific_shard.py
O  launch_m245_scientific_invocation.py
A  aggregate_m245_spectrum.py
```

No new shared M245 helper is permitted. The exact APIs, constants, schemas,
gates, and hostile dummy controls are those frozen in the four repaired tests
and Erratum2. Implementing only enough to return constants or zero-valued
stubs is forbidden and is designed to fail the nonzero controls.

### P -- primary mathematical core

`m245_primary_core.py` owns the independent Plackett/bivariate-ReLU route,
Hermite and incomplete-moment recurrences, analytic `R` and `G`, Cholesky and
projection ladders, ordinary-beta comparator, finite-law diagnostics, primary
schemas, and primary validation gates. It may import `mpmath` but may not call
or alias `mp.quad`; every quadrature request receives the injected
`quad_gateway`. It may not import R, any earlier M245/M243/M178 scientific
implementation, NumPy, SciPy, subprocess/network code, or a common scientific
helper.

### R -- independent replica core

`m245_replica_core.py` independently reimplements authority verification,
binary64 decoding, canonical event handling, repeated-coordinate mean/window,
conditional factorization, unary positive-part means, replica moments, cache
scope, and replica validation. It may not import P, consume a P value/cache,
reuse the Plackett construction, or import a common M245 scientific helper.
It may import `mpmath` but may not call or alias `mp.quad`; all integration is
through the injected `quad_gateway`. Similar source text required by the same
mathematics is not shared runtime state.

### W -- sole scientific gateway

`m245_scientific_worker.py` is the only role that imports both P and R and the
only M245 source containing a project `mp.quad` call. The sole call site is
inside `_instrumented_quad`, with the frozen literal policy and lossless
request/completion ledger of Erratum2 E2.6. W injects that gateway explicitly
into every primary and replica event call. W may create no child and may write
no M245 file. Its future production path remains unreachable in this phase;
only its dummy APIs may be exercised by the frozen tests.

### O/S/L/W transport

`launch_m245_scientific_invocation.py` is O and
`run_m245_scientific_shard.py` is S. Both are stdlib-only and may not import P,
R, W, mpmath, NumPy, SciPy, network libraries, or prior scientific lineages.
Their frozen production topology is exactly `O -> S -> L -> W`, where L is
the inert venv launcher and is not a seventh project file. O owns the outer
meter, terminal witness, and invocation-two final-shard receipt; S owns the
durable intent and inner result/checkpoint/meter/provisional receipt; L owns
no file; W owns no file. The exact argv, cwd, environment, Job Object,
hard-link publication, down-closed attempt order, terminal boundary, and
resource-union rules remain Erratum2 E2.3--E2.9.

Production command dispatch in O, S, and W must fail closed without a future
hash-bound committed trigger. This authorization does not supply that trigger.
Only the frozen transport test's isolated dummy probe may create O/S/L/W
dummy identities in this phase, and it must report zero scientific imports.

### A -- stdlib-only aggregation

`aggregate_m245_spectrum.py` is a stdlib-only file verifier, exact family-rule
reducer, immutable publisher, and receipt builder. It may not import P, R, W,
O, S, mpmath, NumPy, SciPy, or any scientific lineage; call quadrature, solve,
fit, transform, or recompute science; or expose an in-memory receipt bypass.
Its production entry must fail closed without the separately committed
aggregation input authorization described in Erratum2 E2.10. Only the frozen
aggregation test's temporary dummy inputs may exercise its pure validation
and publication APIs in this phase; no authority-directory aggregation output
is permitted.

## I1.5 Fixture and sealed-event firewall during implementation/GREEN

The committed V2 may be opened only to:

1. verify its full-file SHA-256 and canonical JSON bytes;
2. verify artifact/schema names, the exact E00:E07 labels, census order, shard
   ownership, no-redraw flags, and `scientific_quantities_evaluated=[]`; and
3. treat each array receipt as opaque bytes while verifying declared dtype,
   shape, byte length, raw-hex consistency, and hashes.

No real `mu`, `C`, `alpha`, correlation, binary64 array element, or derived
fixture scalar may be decoded, converted to `mpf`, printed, selected, passed
to P/R/W, or used in any formula. `load_verified_v2` may validate the envelope
but may not dispatch an event. Array-decoder and event-evaluator tests must use
only their frozen dummy receipts and dummy event dictionaries outside E00:E07.

No command in this phase may invoke O, S, W, or A as a production script, use
`--emit-pretrigger-zero-intent-census`, create the real shard directory, or
publish an authority-directory artifact other than the GREEN receipt and its
checksum.

## I1.6 Pre-GREEN static freeze

All six implementation files must be complete before GREEN 1. Before any
test command, the owner performs read-only source inspection proving at least:

1. the four test files still have the I1.1 hashes;
2. exactly the six I1.4 production paths exist and no seventh M245 production
   helper was added;
3. P and R do not import one another and contain no direct/aliased `mp.quad`;
4. W contains the sole project-source `mp.quad` call inside
   `_instrumented_quad` and injects `quad_gateway` into both cores;
5. O and S are stdlib-only and freeze `O -> S -> L -> W` without executing it;
6. A is stdlib-only and cannot import/recompute scientific work;
7. no real shard/census/trigger/aggregation path has appeared; and
8. all six source SHA-256 values are captured before GREEN 1.

The six source bytes and four test bytes are immutable across all four GREEN
commands. An edit after the first command invalidates the run set and is
`BLOCKED_GREEN_HASH_DRIFT`; this authority permits no rerun. Static inspection
must not import, compile, or execute a production module and must not read a
real fixture value.

## I1.7 Exact dummy-only GREEN commands

The exact interpreter is:

```text
C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe
sha256=4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262
```

The exact working directory is:

```text
C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m245_canonical_unordered_replica_galerkin_spectrum
```

After I1.6 passes, execute exactly once each, serially and in this order:

```powershell
& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_primary_core.py

& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_replica_core.py

& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_scientific_transport.py

& 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe' `
  -B -m unittest -v test_m245_aggregation.py
```

No combined discovery, parallel runner, coverage wrapper, pytest, alternate
interpreter, alternate cwd, environment injection, test selection, skip,
expected-failure conversion, or second attempt is authorized. A nonzero exit,
hang, source/test drift, real event access, unexpected authority-directory
publication, or real-namespace creation is a binding
`FAIL_IMPLEMENTATION_GREEN_STOP_NO_RERUN`. It is not permission to patch and
try again; a new append-only repair authority would be required.

The tests may perform their exact frozen dummy high-precision calculations,
dummy hard-link transactions, dummy O/S/L/W probe, and temporary Git/input
checks. They may not transform those controls into an E00:E07 result.

## I1.8 GREEN evidence and candidate freeze

Only if all four commands exit zero may the owner create:

```text
M245_SCIENTIFIC_TDD_GREEN_RECEIPT_20260810.md
M245_SHA256SUMS_SCIENTIFIC_TDD_GREEN_20260810.txt
```

The receipt must bind the implementation-authority commit, all six source
hashes and byte lengths, all four frozen test hashes, exact command argv/cwd,
UTC intervals, exit codes, complete captured stdout/stderr hashes and byte
lengths, and a post-command census proving:

```text
E00:E07 decoded_or_evaluated=0
real_fixture_values_used=0
production_dispatches=0
real_shard_directories_or_files_created=0
pretrigger_censuses_created=0
scientific_triggers_created=0
aggregation_authorities_or_outputs_created=0
responses_or_providers_created=0
network_or_submission_actions=0
```

The GREEN checksum may list the receipt, this authority, its checksum, the six
sources, four tests, both RED receipts, RED checksum, Erratum2/overlay, and V2
authority files. It must not list or hash itself. The GREEN receipt must not
contain its own hash, its checksum hash, or a future commit hash. This removes
all self-hash and future-commit cycles.

After receipt publication, commit the exact six sources and the two GREEN
evidence files once without changing any source or test byte. That is a frozen
implementation candidate only. It confers no scientific authority.

## I1.9 Mandatory stop and later static-audit/trigger sequence

Stop immediately after the GREEN candidate/evidence commit. This authority
does not authorize either static-audit artifact, a pretrigger census, a
trigger, or a shard.

The next append-only authority must bind the exact committed hashes and freeze
this sequence before any scientific launch:

1. create `M245_SCIENTIFIC_STATIC_AUDIT_CONTRACT_20260810.md` binding the exact
   six source, four test, authority, RED, and GREEN evidence bytes;
2. obtain two independent, read-only, nonexecuting exact-hash reviews by
   distinct reviewers, neither of whom edits a reviewed byte;
3. publish `M245_SCIENTIFIC_STATIC_AUDIT_A_20260810.json` and
   `M245_SCIENTIFIC_STATIC_AUDIT_B_20260810.json`, each binding the same source
   set and returning an explicit PASS or FAIL;
4. only after two PASSes, publish
   `M245_SCIENTIFIC_STATIC_VALIDATION_RECEIPT_20260810.json` and commit the
   exact audited set without byte drift; and
5. under a further explicit trigger authority, run and commit the stdlib-only
   pretrigger zero-intent census, then bind its real first-containing commit
   and exact bytes in the trigger.

No audit majority, repair-in-place, post-audit source edit, silent re-GREEN,
or audit of different hashes is valid. A PASS through I1.8 proves only that
the dummy contract tests accept one implementation. It says nothing about an
E00:E07 value, runtime, convergence, estimator usefulness, contest score, or
deployability.
