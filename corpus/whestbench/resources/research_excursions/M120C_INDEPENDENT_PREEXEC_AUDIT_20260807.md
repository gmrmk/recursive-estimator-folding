# M120C independent preexecution audit - 2026-08-07

## Verdict: REPAIR

Do not execute the 27-network binding grid. M120C has a correctly frozen grid,
useful metric/gate primitives, and a structurally correct central-covariance
shared-CP local recurrence, but it is not an executable one-shot protocol. The
named runner is deliberately inert, explicitly disclaims atomic/no-retry
semantics, and contains no binding evaluator. The available dense reference is
also finite-difference/ten-point-quadrature code with variance floors and
correlation clipping, not the exact fail-closed Jacobian required by the frozen
theory protocol. Finally, the manifest verifier accepts omission of reviewed
source bindings.

This is a repair of the execution and reference protocol, not a kill of the
M120 `pp^T + D` shared-CP mechanism.

## Scope and untouched state

I independently reviewed the M120 theory protocol, the M120C protocol report,
configuration, harness, manifest, named runner, deprecated M120B runner,
corrected Jacobian implementation, both test files, and the two imported
Gaussian-background dependencies. I did not run the binding grid, sample any
of its 27 networks, access a correction source, target, scorer, contest object,
or champion artifact, or mutate any M120C source.

Before and after the source/unit checks, both the fixed result and its parent
directory were absent:

```text
work/scorefloor_generation/m120_price_normal_ordered_adjoint/out/
work/scorefloor_generation/m120_price_normal_ordered_adjoint/out/m120c_binding_result.json
```

No one-shot invocation is authorized by this verdict, and the reviewed source
does not contain one.

## Preserved passes

### Frozen combinatorial plan and firewall - PASS

The configuration contains exactly widths `{8,12,16}`, depths `{2,3,4}`
(including the final affine map), three numeric seeds per cell, and 27 unique
network entries. The nine network-seed triples agree with the documented
arithmetic namespace. The direction namespace produces 72 unique Philox seeds
(four for every width/depth/hidden-layer coordinate), is disjoint from all 27
network seeds, and accepts no output, replica, result, or retry index. The
expected all-output metric key set has exactly 648 entries.

The inspected M120C paths contain no network client, target/scorer loader, or
champion access. The old wrong-grid entry point
`run_corrected_cp_generated.py` is inert.

### Metric and gate algebra - PASS in isolation

`standardized_state` implements the declared product state

```text
(D*b, D*A*D), D = diag(sqrt(diag(C)))
```

and `standardized_complete_error` uses its complete Euclidean/Frobenius norm.
`evaluate_predeclared_gates` requires exactly one row for every one of the 648
keys, rejects duplicates, omissions, extras, nonfinite complete errors, and
missing/nonfinite four-direction vectors, retains signed directions, and gates
their absolute values at the same global `.05` and per-cell `.10` limits. Its
record weighting is the declared mean over cells/networks/layers/outputs rather
than a selected-output statistic.

The standardized state and signed contraction transform correctly under the
tested simultaneous `P diag(g)` coordinate transformation. The separate chain
test confirms the declared all-hidden ReLU reparameterization preserves its
terminal preactivation for the tested width-8/depth-4 fixture.

### Corrected central-covariance recurrence - structural PASS

The implementation includes both covariance-to-mean and
covariance-to-variance cross blocks, the independent symmetric-slot factor of
two, `p*b + c_mu`, `r*b + c_v`, the off-diagonal Price action, and the signed
central-covariance diagonal overwrite. The CP base uses `p p^T` for inherited
atoms and the signed reset

```text
delta - p^2 * diag(A)
```

on identity atoms. Unit checks reproduce the univariate derivative
`1/2 - 1/(2*pi)`, match the implementation's dense finite-difference oracle,
and show the E=0 CP factorization matches the dense base for the tested small
fixtures. The additive-rank and 99.72088832B lower-bound arithmetic also
recompute.

These are genuine surviving components. They do not supply the missing binding
runner or certify the dense reference as exact.

## R1 - no fixed-path atomic no-retry one-shot runner

This is a release blocker and is explicit in the source:

- `CONFIG.execution_mode` is `FROZEN_INERT_NO_CLI`;
- `CONFIG.atomic_no_retry_claim` is `False`;
- the manifest repeats both declarations;
- `run_m120c_protocol.py` only verifies plan metadata and then exits;
- the protocol report says the runner makes no atomic/no-retry claim.

There is no exclusive claim consumed before the first Philox sample, no fixed
canonical path resolution independent of the caller's current directory, no
same-directory temporary result, flush, file fsync, atomic replace, durable
failure/terminal ledger, concurrency guard, or permanent retry barrier. The
configured output is merely a relative string. The existing unit test
positively asserts that this inert state is the expected behavior, so its pass
is evidence of R1 rather than evidence that R1 is closed.

The gate result also stores per-cell maps under tuple keys such as `(8,2)`;
that object is not directly JSON serializable. No fixed 648-row result schema
or atomic serializer exists.

## R2 - the frozen Philox binding computation is metadata only

`binding_plan()` says `bit_generator="Philox"`, but no reviewed function
consumes the plan to generate a network or to compute a binding record. The
only available weight generator in `corrected_cp_jacobian.py` calls
`np.random.default_rng(seed)`, which is PCG64, not the frozen Philox generator.

Likewise, no call graph:

1. dispatches exactly the 27 configured network seeds once;
2. retains every terminal output and every hidden input-facing layer;
3. records full dense and CP `D*b` and `D*A*D` states;
4. forms the 648 complete normalized errors;
5. evaluates all four predeclared signed directions for every row;
6. applies simultaneous gauge/permutation checks to the actual dense and CP
   reverse recurrences; or
7. writes the complete signed ledger and frozen aggregate gates.

`reverse_generated_network` cannot stand in for that runner. It returns only
source-facing dense arrays and whole-array, unstandardized layer metrics; it
does not retain per-layer/per-output standardized states or signed directional
records. Its existing generated unit grid is widths `{3,4,5}`, depths `{3,4}`,
two replicas, and PCG64 - precisely the superseded M120B geometry.

## R3 - the claimed exact reference is approximate and not fail-closed

The frozen protocol asks for an exact dense complete central-covariance
Jacobian and zero/near-zero variance rejection at `1e-10`. The reviewed
reference does not meet that contract:

- `fullcov.py::phi2_gauss10` explicitly describes itself as an approximate
  ten-point Gauss-Legendre bivariate-normal CDF and clips correlations to
  `[-1+1e-12,1-1e-12]`;
- `fullcov.py::relu_gaussian_moments` floors variances at `1e-24` and clips
  correlations instead of failing closed;
- `local_kernels` obtains both dense cross blocks by central differences with
  default scale `2e-5`, and its SPD gate is not an error certificate;
- `terminal_relu_adjoint` floors terminal variance at `1e-14`;
- `local_kernels` accepts every positive variance rather than rejecting values
  at or below `1e-10`.

The `1e-10` test covers only the isolated `standardized_state` helper. It does
not exercise the Gaussian background, local kernels, terminal adjoint, dense
reverse, or CP reverse on degenerate and near-degenerate cases. The local
finite-difference test uses the same approximate moment routine on both sides
and admits `1e-7` relative error; it cannot certify an exact reference or a
`1e-10` end-to-end fail-closed condition.

An analytic/automatic-differentiation implementation with an independent
accuracy certificate could close this blocker. A high-accuracy numerical
reference could also be used if its prospective error bound is small relative
to `.05/.10` and every clamp/floor condition is rejected rather than silently
changed. The current source has neither.

## R4 - source-hash verification is open-set and accepts omissions

The checked-in manifest's listed hashes currently match. Its verifier does not
require the exact reviewed key set, however. It iterates over whichever
`source_sha256` entries the manifest happens to supply and checks only that the
map is nonempty. In a temporary source-only mutation probe, I retained only
the config hash and removed the other seven entries. `manifest_errors()`
returned the empty tuple:

```text
retained_key scorefloor_generation/m120_price_normal_ordered_adjoint/m120c_protocol_config.py
errors ()
```

The verifier also ignores `manifest_status`, the exact firewall, extra root
fields, and an exact source-key set. The manifest does not bind
`test_corrected_cp_jacobian.py`, even though that is the only direct regression
suite for the corrected Jacobian. No externally fixed manifest hash, pinned
Python/NumPy identity, or runner self-seal prevents replacement of the manifest
and simultaneous contraction of its source list.

Therefore current manifest verification proves consistency with an
attacker-selected nonempty subset, not closure of the reviewed implementation.

## R5 - representation and degeneracy tests stop before the actual adjoint

The simultaneous hidden-transform test checks only terminal network outputs.
The standardized-adjoint test manually transforms one supplied state. Neither
runs the dense and CP reverse recurrences on the same simultaneously
reparameterized network and compares every hidden standardized state,
complete error, and signed contraction. The transformation helper checks
matrix shape but does not verify that a supplied matrix is a permutation, and
the gauge/permutation schedule is not frozen for the 27 binding jobs.

The only near-zero tests call `standardized_state` on a synthetic diagonal
matrix. They do not establish that the actual reference/CP call graph rejects
zero or near-zero variance before a floor, clip, division, or finite
difference. This must be repaired together with R2 and R3, not treated as a
standalone passing representation certificate.

## Required repair before a new audit

1. Implement a single fixed-path owner that verifies a pinned runtime, an
   externally fixed manifest hash, and an exact source-key/schema set, then
   atomically consumes a permanent claim before any network sample. Add atomic
   result/failure/terminal writes, flush/fsync/replace, concurrency exclusion,
   and no retry after any consumed attempt. Keep the M120B wrong-grid runner
   inert.
2. Implement exactly the frozen 27-job dispatcher with
   `np.random.Generator(np.random.Philox(network_seed))`; reject any missing,
   extra, repeated, reordered-by-outcome, or nonnumeric seed/job.
3. Produce one JSON-safe record for every 648
   `(width,depth,replica,layer,output)` keys, including the reference norm,
   complete error, all four signed contractions, seed identities, and enough
   raw standardized-state evidence to recompute every aggregate. Preserve
   signed values and apply the frozen `.05/.10` gates once.
4. Replace or rigorously certify the approximate/floored dense reference.
   Enforce the `1e-10` zero/near-zero gate throughout background propagation,
   local kernels, terminal initialization, dense reverse, CP reverse, and
   direction contraction before any quotient or clamp.
5. Freeze and execute simultaneous positive-gauge/permutation schedules against
   both actual reverse implementations at all hidden layers. Validate actual
   permutation matrices, transport directions, and require state/error/signed
   contraction agreement at `1e-10`.
6. Add omission/extra/hash-drift manifest tests, Philox dispatch-count tests,
   missing/duplicate record tests, JSON round-trip/recompute tests, and
   interruption/concurrency/no-retry lifecycle tests.

Only after those source repairs pass a new independent audit should an auditor
publish an exact one-shot invocation. Do not infer an empirical component kill
from the earlier wrong-grid adverse result, and do not run the 27-network grid
under the present source.

## Source/unit verification performed

Local Python 3.14.4 environment used for source/unit checks only:

```text
work/whest-v014/Scripts/python.exe -m unittest -v test_m120c_protocol.py test_corrected_cp_jacobian.py
```

Result: `14 tests`, all passed in `0.241s`. `py_compile` passed for the seven
reviewed Python source/test entry points. A separate read-only schedule check
reported:

```text
jobs 27
network_unique 27
directions 72
direction_unique 72
namespace_overlap 0
metric_keys 648
manifest_errors ()
```

These passes validate the currently tested primitives. They do not override
R1-R5 because the tests intentionally omit the binding evaluator and assert
the inert runner state.

## Reviewed SHA-256 hashes

| File | SHA-256 |
|---|---|
| `m120c_protocol_config.py` | `e184385a6021c44653c5168768e2912ff94119806e66e9921987117087cbc3bf` |
| `m120c_protocol_harness.py` | `58b91067c13a66ada75f5e32e4d8883ce8495b8b7a167fbfce97a4b62569a788` |
| `m120c_protocol_manifest.json` | `61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe` |
| `run_m120c_protocol.py` | `d9eeb0e4a16d98cafc2507ea748091a388fab046211e459610de5be7b291fe10` |
| `run_corrected_cp_generated.py` | `221ffec93fec343dedef8479db89fa8dbc3522ab32a3699c3ddbb92e7237c3c5` |
| `test_m120c_protocol.py` | `b559bdb72c750f5d1451a4168f63d768af02f791382983a7c0b7f4e35908701d` |
| `corrected_cp_jacobian.py` | `9bd61a90e53c1339a2717dcb3592865f75ff7a007db53952f3c9814d5d427f13` |
| `test_corrected_cp_jacobian.py` | `8981f955c24f6502a9a6945d96c66cf899430b1d46f43a9ea2fa1259a2a8df5d` |
| `fullcov_gaussian_mm/fullcov.py` | `091989fbb2249f792f595020e2a475982fd6c5605e51b83065a1837cf51492f6` |
| `adjoint_cumulant/adjoint_born.py` | `f83a5299de16131a435598a74fd2d6f9c56af6c19b4e7505ae481f4f38ae08bd` |
| `M120_NORMAL_ORDERED_PRICE_ADJOINT_THEORY_20260807.md` | `ec681ad77d518054b6ae08164ca390f58caa18f92be37083a54519d1b1566dd4` |
| `M120C_EXACT_PROTOCOL_HARNESS_20260807.md` | `c4eeb472aabeef14e47eba8820146f29e8f4ef8ef64365a7d9adf27e4db4faa0` |
