# Handoff test matrix

Run commands from the repository root. Historical tests are evidence owners;
they are not permission to open an outcome cell or tune a killed mechanism.

## Tier A: bundle and skill integrity

```text
python scripts/verify_whestbench_handoff.py
python tests/test_fold_ledger.py
```

These use only the Python standard library.
The recorded full sweep is in `TEST_SWEEP_20260807.md`.

## Tier B: response-free M154-M177 unit/static tests

Run each test from its owning directory so historical relative imports retain
their frozen semantics. Use the pinned competition Python/FlopScope environment
when a test imports `flopscope`; do not install an unpinned replacement. The
M157 Formal-parent dependencies are included under
`row_blocked_production/candidate_source/`.

```text
m154_analytic_endpoint_partition/test_m154_analytic_endpoint_partition.py
m155_b1_compiler_audit/test_m155_khatri_obstruction.py
m156_extended_domain_star_control/test_m156_extended_domain_star_control.py
terra_m157_selfhosted_formal_pilot/test_m157_selfhosted_formal_pilot.py
m158_generic_orthant_falsifier/test_m158_generic_orthant_falsifier.py
m159_scale_normalized_abi/test_m159_scale_normalized_abi.py
terra_m160_hostile_deploy/test_m160_hostile_audit.py
m161_response_free_source_variance/test_m161_response_free_variance.py
m162_plackett_tallis_falsifier/test_m162_plackett_tallis_falsifier.py
m163_exterior_collision_null/test_m163_exterior_collision_null.py
m164_staged_audit/test_m164_static.py
m165_rank_face_subtraction/test_m165_rank_face_subtraction.py
m166_oriented_collision_null/test_m166_oriented_collision_null.py
m167_collision_owner_unification/test_m167_collision_owner_unification.py
m168_rank2_anchor/test_m168_rank2_anchor.py
m169_m163_call_fusion/test_m169_call_fusion.py
m170_oriented_tensor_rank/test_m170_oriented_tensor_rank.py
m171_rank_stratified_provider/test_m171_rank_stratified_provider.py
m172_selective_22_owner_fusion/test_m172_selective_22_owner_fusion.py
m173_parameter_scaled_boundary_layer/test_m173_parameter_scaled_boundary_layer.py
m174_m169_staging_interface/test_m174_static.py
m175_b8_labelled_background_abi/test_m175_static.py
m176_background_archive_producer/test_m176_static.py
m177_bivariate_relu_primitive/test_m177_bivariate_relu_primitive.py
```

The directory prefix for every line is
`corpus/whestbench/experiments/`. Example:

```text
cd corpus/whestbench/experiments/m177_bivariate_relu_primitive
python test_m177_bivariate_relu_primitive.py
python verify_m177_static.py
```

M165 and M168 additionally require `mpmath==1.3.0`. Install the pin from
`corpus/whestbench/handoff/requirements-repro.txt` into an isolated target or
disposable environment. Do not alter the organizer-authorized environment in
place. M174 intentionally authenticates the installed FlopScope source at its
historical adjacent path; see `TEST_SWEEP_20260807.md` before relocating it.

## Tier C: frozen verifiers and generated resource runners

Static verifiers are safe to run response-free:

```text
m174_m169_staging_interface/verify_m174_static.py
m175_b8_labelled_background_abi/verify_m175_static.py
m176_background_archive_producer/verify_m176_static.py
m177_bivariate_relu_primitive/verify_m177_static.py
```

The following generated/native runners are included for auditability but can
be expensive and environment-specific. Re-run only as exact replication of
their frozen manifest; never alter seeds, batch size, dtype, call order, or
thresholds in place:

```text
m156_extended_domain_star_control/run_m156_native_trace.py
terra_m157_selfhosted_formal_pilot/run_m157_selfhosted_formal_structural.py
terra_m160_hostile_deploy/run_m160_hostile_audit.py
m164_staged_audit/run_m164_native_trace.py
m166_oriented_collision_null/run_m166_static.py
m169_m163_call_fusion/run_m169_parity.py
m169_m163_call_fusion/run_m169_native_trace.py
m170_oriented_tensor_rank/run_m170_static.py
m171_rank_stratified_provider/run_m171_static_audit.py
m172_selective_22_owner_fusion/run_m172_static.py
m173_parameter_scaled_boundary_layer/run_m173_static_audit.py
```

Existing JSON traces and per-experiment checksum files are the frozen record.
A replication mismatch creates a new audit record; it does not authorize
overwriting the historical result.

## Tier D: archived M120-M153 resources/tests

The repository includes the lawful source, tests, manifests, and compact
results for every available M120-M153 directory used by the current autopsy.
Enumerate them with:

```text
git ls-files 'corpus/whestbench/experiments/m1*' \
  'corpus/whestbench/experiments/terra_m1*'
```

Read the owning report and manifest before running an archived test. Some are
protocol, resource, or result judges rather than ordinary unit tests, and some
require a historical pinned environment. Do not bulk-run files merely because
their name begins with `test_`.

## Current authoritative M177 check

Under the pinned WHestBench 0.14.0 / FlopScope 0.10.0 environment:

```text
cd corpus/whestbench/experiments/m177_bivariate_relu_primitive
python test_m177_bivariate_relu_primitive.py
python verify_m177_static.py
```

Expected disposition remains `runtime_candidate=False`: endpoint algebra and
six tests pass, while the certified metered `Phi2`/Owen-`T` provider is absent.
A passing unit test must not be misreported as a runtime candidate or estimator
efficacy result.
