# M115 installed-manifest independent judge

Date: 2026-08-07  
Verdict: **PASS_TO_EXECUTE** — only the exact frozen generated-only one-shot
below is released. This is not a claim that its numerical screen will pass.

## Scope and non-execution statement

This was a read-only installed-manifest audit. It did not invoke
`run_authorized_one_shot`, execute the generated screen, create a claim,
create the canonical root, generate any future weight stack, access a contest
object/target/scorer/champion, or submit anything. The canonical root was
absent before this audit and remained absent after every validator:

```text
C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation\m115_projective_arc_nystrom_one_shot_20260807
```

The external manifest is now installed, rather than absent as it was for the
pre-execution audit. Its independently computed SHA-256 is exactly:

```text
13744c7f023294fb17805e84ceeb8653dacecf1371b43d3e574d0786b26eac89
```

## Frozen source surface

The manifest binds exactly these nine files. Direct SHA-256 recomputation
matched every manifest entry and the runner's own exact-set/hash check.

| file | SHA-256 |
|---|---|
| `CONFIG.json` | `57131152b7c247fb843b2a97ba3187f021ab25ece0df387d6dc52839cf4d85bd` |
| `INVENTORY.md` | `a443cd42b3bee3c5d5dd5540e348d4df963fa8c6cde5df5e9e49fe774a4d1cf0` |
| `REFERENCE_AND_PROTOCOL.md` | `6b0d0dd2c6b5bed605ce9f63d971964efd1e27b97272b6ebc8160469bc2e8152` |
| `m115_projective_arc_nystrom.py` | `d19d3e744d183d71b0f40f65050f7794b49467bb2a05f7f6fcaebb24e2bae189` |
| `run_m115_generated_only.py` | `ce4d622b368dd928886b24c47dc9de8125dc46097f39fa07825ec04ae2c7bc5b` |
| `run_target_free_tests.py` | `d9ff643701a32a9dfc1440c30d7d203fd16d0c3363a0dcc7406f213d3a4f7a63` |
| `test_m115_core.py` | `eb4b71c4da8eb001fda40bcd0d182222a14552358973d35061080606782a6b93` |
| `test_m115_protocol.py` | `5c2a0ea16493b4f38be874555e0de224fd8ede0762bb0dd16e3db5d59297af20` |
| `test_m115_runner.py` | `98e5dc1d11e89fdec52f6f5bb07ac5e3063a9db2585f1cb877a31c69e51f28ff` |

## Runtime, canonical identity, and firewall

The read-only runner check used exactly Python 3.12.13 at
`C:\Users\strid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`,
NumPy 2.3.5 at the corresponding bundled `numpy\__init__.py`, and the exact
NumPy/BLAS build fingerprint:

```text
dcf0de4fcb893ae900ea39ae9cce6e041c6046dc2996068c5c9151d0cd795447
```

All three thread variables were exactly `1`: `OPENBLAS_NUM_THREADS`,
`OMP_NUM_THREADS`, and `MKL_NUM_THREADS`.

The manifest and runner agree on the only run identity:

```text
run_id: m115-repaired-generated-only-115001-115004-v1
claim-before-weight-generation: true
retry_allowed: false
```

`_verify_external_manifest` requires the exact canonical path, schedule
`[115001,115002,115003,115004]`, 50 frames, five folds, 128 landmarks, ridge
`0.001`, frame rows only, no feature centering/intercept/held normalization/
denominator floor, and no retry. It also requires the exact generated-He-only
firewall: no contest instances, truth, leaderboard/scorer, or champion
access. `scope` is `screen_only=true`, `submission_authorized=false`, and
`champion_replacement_authorized=false`.

The source creates the root with `os.mkdir` only after authorization, frozen
configuration checks, runtime verification, and manifest verification. That
directory existence is the permanent retry barrier; it is created before any
future frozen-seed weight generation. There is no output-path or manifest-path
argument. A screen pass is source-defined as `OOF_RISK_ONLY`, with champion
mutation permanently false; it is not a submission or champion replacement.

## Cost calibration and independent evidence

The manifest pins `EXTERNAL_M115_COST_CALIBRATION.json` to:

```text
82e927d8a54f2a61fcfe48e542a624038b3ba0cb50f2dde592be28f21d21ebb1
```

The fixed evidence directory contains exactly 14 files; each was independently
hashed and accepted by the runner's schema, operation-multiset, total-recompute,
and descriptor-hash validation.

| evidence | SHA-256 |
|---|---|
| `base_0.json` | `9deec66dbc7b29afecc7678d3cd1fc39e06742f2e427f756f9f40aec0fa15696` |
| `base_1.json` | `dd406537147b9e5ab1d13ceb13f5177b56d9f63a7e09c115c0cc415f150aaa02` |
| `base_2.json` | `93b9fcf3f89ecad233d2ab9046a17de3c3c53f94cfe174f9baa957d9806d6499` |
| `base_3.json` | `8606f3d46416398010a3e6901ae21dc3d881720c05ca7b31055d7f428dee59ca` |
| `candidate_0.json` | `1c5977d356024d46ee8a6b3cd0ac2ff38932e68db0b12cb545fea2f9230b303d` |
| `candidate_1.json` | `2674fbb9493ebe350246ef34e2c6dde172eac16deca5cecc60fbe8c9c2f4bd0f` |
| `candidate_2.json` | `cf189481414a88eee2aeebe0a3f85cf33b4f5e203f55a7994f4a5a5646c6dd84` |
| `candidate_3.json` | `1b86b90e7edbce526be536d5b29de89a0f00c7048b0b0b65b5ac45e29e21bfad` |
| `equal_0.json` | `8a9db11c4143a3d3fc854f4960b626178475e9d04a4a731f4e96c26aa1f7e1b0` |
| `equal_1.json` | `10415f87d4ef968aedb6eb190bee2d77cb7fac5096b1d4feddd63e7fcf3f54fe` |
| `equal_2.json` | `69c0992205969328624016aa3fe142a22fc763c9bcf50a9ab6f1bcd63090a60a` |
| `equal_3.json` | `d5ab8ecee94d9ea3a2e87baed7c3485697ce47627dc433ac499f91f1125c6ec6` |
| `failure_lifecycle.json` | `70481c9f090ccdd52b84804e1fe2d4d1907e547a8f49ad8bb6264bfd86d4dc7a` |
| `success_lifecycle.json` | `898f5b2cfa3615c2c965af5e266236f88b76044efd85b1547f9c498a4650e0bc` |

No `charged_cost_multiplier` key appears in the manifest or calibration; the
runner's recursive forbidden-key check passed. Instead it recomputed the
candidate/base effective-cost ratios from closed operation ledgers, charging
the non-amortized dominant lifecycle cost `39,195,280,468.00001` to each
candidate. These are calibration costs, not numerical-screen outcomes:

| network | candidate/base cost ratio | base/candidate frames | maximal equal-cost L1 frames |
|---:|---:|---:|---:|
| 0 | 2.5434341269313316 | 50 / 50 | 127 |
| 1 | 2.9944382164302210 | 50 / 50 | 150 |
| 2 | 2.7404858033606083 | 50 / 50 | 137 |
| 3 | 2.5907906100539430 | 50 / 50 | 130 |

The recomputed conservative maximum is `2.994438216430221`. The runner
verified that each equal-cost comparator adds legal independent frames, costs
no more than its candidate, and leaves less than one affordable next frame.

The manifest's cited independent audits both resolve and hash exactly:

| audit | SHA-256 | manifest verdict |
|---|---|---|
| `M115_THIRD_INDEPENDENT_PREEXEC_AUDIT_20260807.md` | `2b7eecf2b42c4f3f338ea3d3ccf5ecc6380f0ba9ee77e06b600def8e855334d6` | `PASS_TO_FREEZE` |
| `M115_PREOUTCOME_COST_CALIBRATION_INDEPENDENT_AUDIT_20260807.md` | `b915142b2f5ef9a2f481005dd35b98f0d72acdc69a941bde7c0bd945399227cb` | `PASS_TO_MANIFEST` |

## Validator evidence and remaining unknowns

Under the pinned runtime and one-thread environment, the following read-only
checks completed successfully: `_config_guards()`, `_verify_runtime()`, and
`_verify_external_manifest(runtime)`. The last check validates the nine-file
surface, exact manifest protocol/canonical/firewall fields, calibration hash,
all 14 evidence artifacts, no-free-multiplier rule, static inventory, closed
operation contracts, deterministic bill/byte totals, cost ratios, equal-frame
maximality, and storage/memory constraints. It did not call any screen or
create a file in the canonical root.

No generated numerical result exists. The four raw network variance ratios,
four charged numerical ratios, charged geometric ratio, charged pooled ratio,
and exact four-network bootstrap q90 are all **unobserved**. The screen may
therefore still end terminally in
`KILL_M115_REPAIRED_IMPLEMENTATION_NO_RETRY`; this manifest verdict does not
predict an `OOF_RISK_ONLY` outcome.

## Exact released one-shot

Do not execute this command from this audit. It is the sole released call and
irreversibly creates the canonical root/claim; any later attempt is rejected.

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
& 'C:\Users\strid\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation\m115_projective_arc_nystrom_draft\run_m115_generated_only.py' `
  --execute-token 'M115_GENERATED_ONLY_ONE_SHOT_AFTER_EXTERNAL_FREEZE'
```

Any deviation in token, runtime, thread environment, manifest hash, source
hashes, calibration/evidence, canonical path, or root absence is a
**REPAIR/KILL** condition rather than permission to create another run.
