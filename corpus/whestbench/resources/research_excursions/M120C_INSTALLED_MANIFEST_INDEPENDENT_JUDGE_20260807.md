# M120C Installed Manifest Independent Judge — 2026-08-07

## Verdict

**REPAIR**

The installed sealed-manifest state is not eligible for one-shot execution because its manifest-bound test suite does not pass in full. The only observed failure is a stale freeze-order assertion, but it is inside a source file sealed by the operational manifest and therefore cannot be waived.

No canonical grid was executed for this judgment. The real generated-metric dispatcher was guarded during the test replay and recorded zero calls.

## Non-execution boundary

This review performed only artifact hashing, manifest/runtime validation, static plan algebra, source inspection, and tests whose dispatcher was replaced by a fail-fast guard. It did not:

- call run_authorized_m120c_grid;
- call the real all_generated_metric_records;
- create the canonical outcome root, claim, outcome, or terminal artifacts;
- execute a network grid;
- access contest, public-outcome, target, scorer, or champion information; or
- submit any result.

Two unit tests exercise the owner path only with all_generated_metric_records mocked: one returns an empty tuple to test publication interruption, and one injects a ValueError to test computation failure. The guard around the real dispatcher recorded real_dispatch_calls = 0.

## Sealed artifact bindings

| Artifact | Required SHA-256 | Independently observed SHA-256 | Result |
|---|---|---|---|
| m120c_protocol_manifest.json | a46e838dc13b3d3a9c9aa2ccc4ad6c80ab3c2e0b9362afb02e71e42231f681e0 | a46e838dc13b3d3a9c9aa2ccc4ad6c80ab3c2e0b9362afb02e71e42231f681e0 | PASS |
| M120C_EXTERNAL_EXECUTION_RELEASE_20260807.json | c8ff95deaf0c293b29590cf2f50566e19c8fe9f9e1620d7af6ad39883ad0ee1d | c8ff95deaf0c293b29590cf2f50566e19c8fe9f9e1620d7af6ad39883ad0ee1d | PASS |
| m120c_protocol_manifest_preexec_61968d9818b398dd.json | 61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe | 61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe | PASS |
| M120C_OPERATIONAL_HARNESS_FINAL_INDEPENDENT_AUDIT_20260807.md | ec9b7f8463bda5e8a7780c9c9ac2e20c1c2f282b42c5ce83138ea8eb23fdf3c2 | ec9b7f8463bda5e8a7780c9c9ac2e20c1c2f282b42c5ce83138ea8eb23fdf3c2 | PASS |

The final independent audit is intact, but its 41-test pass was a historical pre-freeze result. It does not establish that the subsequently installed operational-manifest state still passes those same manifest-bound tests.

## Pinned runtime identity

runtime_identity() was computed under the manifest-pinned interpreter.

| Component | Path/version | Independently observed SHA-256 | Result |
|---|---|---|---|
| Python | work/whest-v014/Scripts/python.exe; 3.14.4 | 4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262 | PASS |
| NumPy | work/whest-v014/Lib/site-packages/numpy/__init__.py; 2.4.6 | 65d5e777b6d662ba19cb80800bef3eb999eda7aee51eea62c308feabf679dba4 | PASS |

The observed paths, versions, and hashes exactly match the sealed manifest and release.

## Source-hash closure

All 11 manifest-pinned source files independently matched their sealed hashes.

| Manifest source | SHA-256 | Result |
|---|---|---|
| scorefloor_generation/m120_price_normal_ordered_adjoint/m120c_protocol_config.py | 492ede62bfd0b98ef26c4d6ea59a0237bc606a07e023dcd1f52479334582a119 | PASS |
| scorefloor_generation/m120_price_normal_ordered_adjoint/m120c_protocol_harness.py | cbf75ed3f392f0c29bfd9b2ece13b580d2a9068a930d8dc05d251a74d69201de | PASS |
| scorefloor_generation/m120_price_normal_ordered_adjoint/run_m120c_protocol.py | 9a7ea97be5a632c89a23fbdaee78a66a688ab5f2250fc26cd8deb839c35cd10d | PASS |
| scorefloor_generation/m120_price_normal_ordered_adjoint/m120c_analytic_dense_reference.py | f5e34f8ebc8ff2cafad63ccf55101155c802b01a36828bfc03edc820ad4a65f8 | PASS |
| scorefloor_generation/m120_price_normal_ordered_adjoint/corrected_cp_jacobian.py | 9bd61a90e53c1339a2717dcb3592865f75ff7a007db53952f3c9814d5d427f13 | PASS |
| scorefloor_generation/m120_price_normal_ordered_adjoint/test_m120c_protocol.py | c26449cd9fcb23b231159c489e53d49ba97427bd6f2fb37c6a0aaa13c6d4f4fe | PASS |
| scorefloor_generation/m120_price_normal_ordered_adjoint/test_m120c_operational_harness.py | 6c050d6a9096dd892ee6ed6cb3cd37afd1ff53e190b82f49d93409f61432174d | PASS |
| scorefloor_generation/m120_price_normal_ordered_adjoint/test_m120c_analytic_dense_reference.py | 09c5d12e7534683cdee907b8d61b21af437678604621bd9f0f7eb7b9d9cf5f1f | PASS |
| scorefloor_generation/m120_price_normal_ordered_adjoint/test_corrected_cp_jacobian.py | 8981f955c24f6502a9a6945d96c66cf899430b1d46f43a9ea2fa1259a2a8df5d | PASS |
| scorefloor_generation/fullcov_gaussian_mm/fullcov.py | 091989fbb2249f792f595020e2a475982fd6c5605e51b83065a1837cf51492f6 | PASS |
| scorefloor_generation/adjoint_cumulant/adjoint_born.py | f83a5299de16131a435598a74fd2d6f9c56af6c19b4e7505ae481f4f38ae08bd | PASS |

For the current sealed manifest and its independently computed digest:

- manifest SHA-256 = a46e838dc13b3d3a9c9aa2ccc4ad6c80ab3c2e0b9362afb02e71e42231f681e0;
- closed_manifest_errors(current, digest) = ();
- manifest_errors(current) = ().

The preserved pre-execution manifest remains correctly non-releasable. manifest_errors(preserved) reports the expected fixed-output, execution-mode, atomic/no-retry, and four stale-source-hash mismatches.

## Static frozen-plan algebra

The plan was computed without invoking the dispatcher.

- Jobs: 3 widths × 3 depths × 3 replicas = **27**.
- Records: 3 replicas × sum over widths/depths of width × (depth − 1) = **648**.
- Network seeds: 27 present and 27 unique.
- Direction seeds: 3 widths × [(2−1)+(3−1)+(4−1)] layers × 4 directions = **72**, all unique.
- Numerical overlap between the network-seed and direction-seed namespaces: **0**.

This confirms the exact frozen plan shape statically; it is not evidence of grid execution.

## Installed test replay

The four direct unittest modules were loaded under the pinned interpreter:

- test_m120c_protocol
- test_m120c_operational_harness
- test_m120c_analytic_dense_reference
- test_corrected_cp_jacobian

Result: **41 loaded; 40 passed; 1 failed; real dispatcher calls = 0**.

The failure is:

test_m120c_protocol.M120CProtocolFreezeOrderTests.test_independent_direction_namespace_is_closed_and_old_preexec_manifest_is_not_a_release

At test_m120c_protocol.py line 145, the test requires manifest_errors(Path(CONFIG.manifest_path)) to be truthy. CONFIG.manifest_path now correctly names the current valid sealed operational manifest, so manifest_errors returns (). The assertion still encodes the pre-freeze assumption that CONFIG.manifest_path names the obsolete inert manifest.

This is an installed-state consistency defect: the sealed manifest accepts the current operational manifest while one of its own sealed tests requires that same path to be rejected.

## Release and lifecycle review

The external release state is AUTHORIZED_FOR_INDEPENDENT_MANIFEST_AUDIT_NOT_EXECUTION. Its execution contract says:

- atomic = true;
- one_shot = true;
- retry_allowed = false;
- execution_authorized_by_this_release = false; and
- independent installed-manifest audit required = true.

Static inspection confirms that the owner has no CLI execution path. The callable owner first requires closed-manifest validation against an externally supplied digest, refuses any existing canonical root, creates an exclusive permanent claim, computes once, publishes one fixed outcome, then publishes a hash-bound terminal marker. Fail, pass, and computation-error paths all set retry_allowed false. Existing claim, pending publication, final outcome, terminal, or canonical root states fail closed rather than permit a retry.

The manifest-fixed outcome is:

work/scorefloor_generation/m120_price_normal_ordered_adjoint/out/M120C_EXACT_GENERATED_OUTCOME/m120c_binding_result.json

At the end of this review, all canonical artifacts remained absent:

- canonical root: absent;
- M120C_CLAIM.json: absent;
- m120c_binding_result.json: absent;
- M120C_TERMINAL.json: absent.

## Required repair and reseal

Before any one-shot execution authorization:

1. Amend the stale test so it explicitly applies manifest_errors to m120c_protocol_manifest_preexec_61968d9818b398dd.json and requires rejection.
2. In the same test, independently digest the current CONFIG.manifest_path and require closed_manifest_errors(current, digest) == (), ideally also binding the expected sealed digest.
3. Recompute the changed test source hash and reseal the operational manifest.
4. Update and reseal the external release against the new manifest/source bindings.
5. Replay all 41 tests under the newly pinned manifest/runtime with the real dispatcher fail-fast guarded, require 41/41, and recheck that the canonical root and artifacts remain absent.
6. Obtain a new independent installed-manifest judgment for the resealed state.

Until those steps pass, this judge issues **REPAIR**, not PASS_TO_ONE_SHOT_EXECUTION. No execution token or authorization is granted by this report.

