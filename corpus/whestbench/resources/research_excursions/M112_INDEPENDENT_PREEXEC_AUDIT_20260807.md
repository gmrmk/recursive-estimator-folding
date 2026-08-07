# M112 independent pre-execution audit -- 2026-08-07

## Final repaired-source re-audit -- verdict: PASS_TO_FREEZE

The current M112 draft passes the source-only gate for **one deterministic
association diagnostic**.  It does not pass as an estimator, does not validate
the ideal-Haar theorem on the fixed bank, and cannot promote a champion.  A
favorable diagnostic can authorize only a newly specified M112b with frame
roots statistically generated independently of all weight roots.

The evidence firewall remained closed throughout this audit.  I did not open,
hash, list, deserialize, or inspect any M111 raw/result/control/metadata
artifact; I created no manifest and did not execute the analyzer.

### Final verification

* **Hoist and call graph:** On the exact 50-frame path,
  `normalized_first_axes(W1)` and `sign_covariance(axes)` execute exactly once
  per network.  Every frame calls only
  `connected_gate_matrix_from_axes_sigma`.  An independent full-size spy check
  returned call counts `(1, 1)` and audit counts `(1, 1)`.
* **Wrapper equivalence and orientation:** The public one-frame wrapper and
  the new hoisted helper produced bit-identical C matrices and identical audit
  records on a target-free generated case.  The helper retains `Q.T @ axes`,
  `V.T @ V/d - Sigma`, explicit zero diagonal, float64 arithmetic, and exact
  symmetry.  No mathematical orientation or normalization changed.
* **Cost coverage:** Independent recomputation gives baseline
  `435,381,862,400`, enumerated all-precision increment `43,500,851,200`,
  reserve `10,875,212,800`, and total `489,757,926,400` f32-equivalents.  The
  resulting factor is `1.1248928094989012`, below the frozen pre-outcome charge
  `1.15`.  The previous repeated-Sigma underestimate is eliminated by the
  actual production call graph.  The analyzer computes all raw and charged
  per-network/geometric/pooled ratios internally; no outcome ratio enters the
  manifest.
* **Semantics:** Theory, protocol, config, runtime result schema, and tests all
  explicitly retract fixed-bank conditional-zero/unbiasedness and require
  fresh independently rooted M112b after any favorable diagnostic.  No
  current estimator, contest access, deployment, or champion mutation is
  authorized.
* **Lifecycle:** The supported API has one canonical output directory and no
  output-path argument.  An atomic `O_EXCL` sentinel is written before array
  loading and remains across success, failure, interruption, or partial
  artifact cleanup.  Direct-worker and alternate-directory paths fail closed.
* **Bindings and firewall:** The manifest schema binds the exact nine-file
  source surface, repaired theory, independent audit, cost report/config,
  executable and NumPy fingerprints, schedule, four W1 hashes, four frame-bank
  hashes, and exact input path/archive hash.  Only `raw_outputs` and integer
  `provenance` are loadable; static review found no deep forward, target,
  scorer, submission, network, API, or M111-module access.
* **Runtime and tests:** The declared Graphify runtime is genuinely CPython
  3.12.13 / NumPy 2.4.4 and matches its configured executable and NumPy-file
  SHA-256 values.  It is distinct from the Codex bundled NumPy 2.3.5 runtime.
  All **39/39** target-free tests passed in the declared Graphify runtime.

### Final association hashes

Schedule: `5905d437506fb73ad097ac88d19067d72b814877cc85bbf82516b40b40d97210`.

| Seed | W1 float32 SHA-256 | 50-frame block float32 SHA-256 | Axes/Sigma calls |
|---:|---|---|---:|
| 111001 | `549dd69033ab83f8e44d69ff14cf34cefb3c1463523ea68ff80ce0d5f0999b45` | `83677119a86b8c23d764755b15296f50105a536340d708e70f7134781af6029a` | 1 / 1 |
| 111002 | `800ddec2eed07c25ef99b8f9e2f90edd62fb2d8322cb8d0933ce2a0e854dba6b` | `d01ec2e58c440970559af065d7f335ee4f7a83d9f3dd839668397de9aeae360b` | 1 / 1 |
| 111003 | `b9410b1e7864f5974acd8ae5ee1ebe413e1d2436b95616524094f0b68b236e10` | `a642ce4c6b4b535b06c755f6cd33bec25e567134e5dbb6adf7b62fedd97c0685` | 1 / 1 |
| 111004 | `04e84389a02527c11d5b3858f432e6c1ba291474a51146aca277fe83a2edef04` | `9a6638b9873bdfc7e5da9884858c59ff63be664d6f42a397137b1995c38a0279` | 1 / 1 |

### Final audited source hashes (SHA-256)

| File | SHA-256 |
|---|---|
| `research_excursions/M112_CONNECTED_GATE_KERNEL_THEORY_20260807.md` | `5f8e5f12de65d3c910ed82ab18a05b9fb5f4994a1bd44bfaba61f52d422240c0` |
| `m112_connected_gate_kernel_draft/ANALYSIS_CONFIG.json` | `e8087ec583157c213c1e35d09d2d4b5d5b810965a1fe85e6106886af33d30b57` |
| `m112_connected_gate_kernel_draft/COST_CALIBRATION.md` | `46f44a02948804cb6c0dc3eecc9bd410c9112873f4b4afd4e78ef4ab4c19233a` |
| `m112_connected_gate_kernel_draft/INVENTORY.md` | `fd9a1c5ed6f3e92977f3c43b8a5a02a9a6b4440857db05028246f28e9714ec9c` |
| `m112_connected_gate_kernel_draft/REFERENCE_AND_PROTOCOL.md` | `f049a26b3b33592ef0c961041175365e81e97457cd68c6160d32e79a18f12ee6` |
| `m112_connected_gate_kernel_draft/analyze_m112_one_shot.py` | `ef72d28d2d91bd8c84a2c8b97baf5ff66f57e82c5c461eaf3c26dcb26fa19fe9` |
| `m112_connected_gate_kernel_draft/m112_connected_gate_kernel.py` | `a0a9c053f9b96167be5f051056a66c71c59c4d5ef2bd523bf59e2f7de1782545` |
| `m112_connected_gate_kernel_draft/run_target_free_tests.py` | `73afac282dd921fbe402a82ff5b93a6e209617395f656a6a27dc0d7709eee9c4` |
| `m112_connected_gate_kernel_draft/test_m112_analyzer.py` | `d18c1b893f4263d2787aeddfac7c43f7dd792f6a3971f387c0b532d193c42878` |
| `m112_connected_gate_kernel_draft/test_m112_core.py` | `2245d50971fda00f5c3db1ba1085614d91a5f58eb7a598cba065224ebafad664` |

**Release boundary:** `PASS_TO_FREEZE` authorizes preparation of the external
independent-audit release and frozen manifest for the one supported diagnostic
path only.  The manifest must use these exact source hashes and the declared
runtime/association hashes.  Any source change, runtime drift, alternative
path, retry, output-dependent calibration, or broader claim invalidates this
verdict and requires another audit.

---

## Superseded second-pass audit -- verdict: BLOCK

This section supersedes the first-pass disposition below for the repaired
source hashes listed here.  The evidence firewall remained closed: I did not
open, hash, list, deserialize, or otherwise inspect an M111 raw/result/control/
metadata artifact; I did not create a manifest or run the analyzer.

Most first-pass blockers are repaired:

* The fixed M111 hash bank is now explicitly only a deterministic association
  diagnostic.  The theory, protocol, config, result schema, and tests retract
  fixed-bank conditional-zero/unbiasedness.  A favorable result authorizes
  only a separately frozen M112b whose frame roots are statistically generated
  independently of weight roots.
* `classify_screen` now receives four base/adjusted trace risks plus the
  pre-outcome factor `1.15`; it internally calculates raw and charged
  per-network, geometric, and pooled ratios.  The manifest's exact cost schema
  rejects an injected outcome/performance ratio.
* The CLI has no output-directory argument.  One canonical output path and an
  `O_EXCL` sentinel claim the experiment before array loading; the sentinel
  survives success and failure and prevents an alternate-directory retry
  through the supported API.
* The manifest binds all nine source files, repaired theory, independent audit,
  runtime, cost report/config, schedule, W1, frame blocks, exact input path and
  archive hash.  Regenerated W1/frame hashes are checked again before a kernel
  is used.  This conclusion assumes the honest workflow's stable local
  filesystem; the code still reopens the input pathname after hashing rather
  than carrying a verified file handle.
* The runtime discrepancy is resolved, not papered over.  Two Python 3.12.13
  environments exist: the Codex bundled runtime has NumPy 2.3.5, while the
  separately pinned Graphify runtime really has NumPy 2.4.4.  M112 declares the
  latter, and its executable/NumPy paths and SHA-256 values exactly match the
  live runtime.  All 38 target-free tests passed using only that declared
  executable.

### Remaining blocker: the 1.15 cost charge does not cover the code that would run

`static_cost_accounting()` bills normalized axes and
`Sigma = asin(A.T @ A)/(2*pi)` once per network.  The implementation actually
calls `connected_gate_matrix(first_weight, frame)` inside the 50-frame loop;
that function recomputes both `normalized_first_axes(first_weight)` and
`sign_covariance(axes)` on every call.  Thus the charge and the implementation
have different call graphs.

Across four networks, relative to the frozen bill, the omitted work is:

| Repeated operation mistakenly billed once/network | Missing f64 operations |
|---|---:|
| 49 additional `A.T @ A` products per network | 6,576,668,672 |
| 49 additional axes-normalization allowances per network | 51,380,224 |
| 49 additional Gram/arcsine/audit allowances per network | 411,041,792 |
| **Total omitted f64** | **7,039,090,688** |

At the declared 2x float64 charge this is 14,078,181,376 additional f32
equivalents.  Reapplying the same 25% reserve produces

```
baseline                         = 435,381,862,400
corrected enumerated increment   =  57,579,032,576
corrected 25% reserve            =  14,394,758,144
corrected total                  = 507,355,653,120
corrected factor                 = 1.16531187202712
```

That exceeds the frozen `1.15`, so the source's own claimed conservative gate
is false.  The passing cost test only compares the config to the same mistaken
static formula and therefore cannot detect the call-count mismatch.

**Exact repair.**  Hoist `axes = normalized_first_axes(W1)` and
`Sigma = sign_covariance(axes)` out of the frame loop and pass those immutable
arrays into a helper that computes only `Q.T @ axes`, V, and
`V.T @ V/d - Sigma`.  Keep the public one-frame formula as a wrapper if useful.
Add a target-free call-count test asserting exactly one axes normalization and
one Sigma construction per network for 50 frames.  Recompute all source hashes,
rerun the 38+ tests in the exact pinned Graphify runtime, and request another
independent source-only audit.  Alternatively raise the frozen charge above
the corrected bound, but hoisting is algebraically identical and strictly
better.

This is a **blocked repaired implementation**, not a family-level rejection.
The connected pair field, raw Frobenius kernel, diagnostic-only retraction,
hash firewall, and one-shot machinery remain preserved components.  No
manifest, evidence run, M112b, champion mutation, or contest access is
authorized by this re-audit.

### Re-audited source hashes (SHA-256)

| File | SHA-256 |
|---|---|
| `research_excursions/M112_CONNECTED_GATE_KERNEL_THEORY_20260807.md` | `5f8e5f12de65d3c910ed82ab18a05b9fb5f4994a1bd44bfaba61f52d422240c0` |
| `m112_connected_gate_kernel_draft/ANALYSIS_CONFIG.json` | `e8087ec583157c213c1e35d09d2d4b5d5b810965a1fe85e6106886af33d30b57` |
| `m112_connected_gate_kernel_draft/COST_CALIBRATION.md` | `46f44a02948804cb6c0dc3eecc9bd410c9112873f4b4afd4e78ef4ab4c19233a` |
| `m112_connected_gate_kernel_draft/INVENTORY.md` | `fd9a1c5ed6f3e92977f3c43b8a5a02a9a6b4440857db05028246f28e9714ec9c` |
| `m112_connected_gate_kernel_draft/REFERENCE_AND_PROTOCOL.md` | `f049a26b3b33592ef0c961041175365e81e97457cd68c6160d32e79a18f12ee6` |
| `m112_connected_gate_kernel_draft/analyze_m112_one_shot.py` | `ef72d28d2d91bd8c84a2c8b97baf5ff66f57e82c5c461eaf3c26dcb26fa19fe9` |
| `m112_connected_gate_kernel_draft/m112_connected_gate_kernel.py` | `70a7187766c5f431a5ad17d4235abcc8abe5248aef067b74b05e2250bc3a6ec5` |
| `m112_connected_gate_kernel_draft/run_target_free_tests.py` | `73afac282dd921fbe402a82ff5b93a6e209617395f656a6a27dc0d7709eee9c4` |
| `m112_connected_gate_kernel_draft/test_m112_analyzer.py` | `d18c1b893f4263d2787aeddfac7c43f7dd792f6a3971f387c0b532d193c42878` |
| `m112_connected_gate_kernel_draft/test_m112_core.py` | `4e16c8511608423e488889c477eb19f1a482672158b5d52bdd4a73f05a82958e` |

### Target-free association hashes in the declared runtime

Schedule: `5905d437506fb73ad097ac88d19067d72b814877cc85bbf82516b40b40d97210`.

| Seed | W1 float32 SHA-256 | 50-frame block float32 SHA-256 |
|---:|---|---|
| 111001 | `549dd69033ab83f8e44d69ff14cf34cefb3c1463523ea68ff80ce0d5f0999b45` | `83677119a86b8c23d764755b15296f50105a536340d708e70f7134781af6029a` |
| 111002 | `800ddec2eed07c25ef99b8f9e2f90edd62fb2d8322cb8d0933ce2a0e854dba6b` | `d01ec2e58c440970559af065d7f335ee4f7a83d9f3dd839668397de9aeae360b` |
| 111003 | `b9410b1e7864f5974acd8ae5ee1ebe413e1d2436b95616524094f0b68b236e10` | `a642ce4c6b4b535b06c755f6cd33bec25e567134e5dbb6adf7b62fedd97c0685` |
| 111004 | `04e84389a02527c11d5b3858f432e6c1ba291474a51146aca277fe83a2edef04` | `9a6638b9873bdfc7e5da9884858c59ff63be664d6f42a397137b1995c38a0279` |

---

## Superseded first-pass audit

## Verdict: BLOCK

M112 must **not** be frozen and must not read the reuse-bank archive in its
current form.  The mathematical core is coherent under its *ideal*
independent-Haar experiment, and the cleanroom has several good protections.
However, the implemented seed schedule does not instantiate that experiment,
and the equal-cost gate has an outcome/order-of-information error.  Either
would make a purported pass uninterpretable.  There are also material
one-shot, replay, runtime, and official-cost gaps.

This is a source-only audit.  I did **not** open, hash, list, deserialize, or
otherwise inspect an M111 result, metadata, control, or raw NPZ value.  I did
not create a manifest and did not execute `analyze_m112_one_shot.py`.

## What passes in the source model

* **Orientation and formula.**  `dots = Q.T @ A` treats the columns of the
  canonical QR frame as directions.  `V.T @ V / d - Sigma` has the stated
  orientation.  Under a truly Haar-uniform frame independent of the weights,
  each column is marginally uniform and
  `E[(1{q^T a_i>0}-1/2)(1{q^T a_k>0}-1/2)] = asin(a_i^T a_k)/(2*pi)`.
  Thus the theory's conditional-zero calculation is correct **under that
  stated probability space**.
* **Diagonal, symmetry, and kernel.**  The code explicitly zeros the
  diagonal after the float64 computation, checks exact symmetry, and uses the
  uncentered/un-normalized Frobenius Gram.  No held-row norm, cosine feature,
  kernel centering, or intercept is reachable through the public cross-fit
  routine.
* **Cross-fit algebra.**  Training-response centering is confined to the
  training rows.  With a training-measurable coefficient and an independent
  held frame, the raw held correction has conditional mean zero.  Fold
  allocation is deterministic (`frame_index % 5`) and all 200 expected
  provenance rows are checked.
* **Firewall surface.**  Static review found no network, scorer, submission,
  deep-forward, or M111-module import.  The NPZ reader indexes only
  `raw_outputs` and `provenance`, with `allow_pickle=False`; the schema and
  all provenance fields are subsequently checked.  This is a good narrow data
  surface, subject to the lifecycle repairs below.
* **Numerics tested without any evidence data.**  With the pinned workspace
  runtime (Python 3.12.13, NumPy 2.3.5), all 28 target-free tests passed.  A
  core-only regeneration of the first 50 frames for one prescribed seed gave
  float64 C/K arrays, exact C symmetry, and maximum frame Gram defect
  `2.2798360532760853e-08`, below the frozen `2e-6` tolerance.  No output
  frame values were loaded.  The normal/QR seed-law tests confirm M112's own
  reproducibility, not compatibility with the historical M111 frame arrays.

## Blocking findings

### B1. The implementation does not supply the independent Haar randomness
required by its exact-zero theorem

`regenerate_first_weight(weight_seed)` and
`keyed_frame_seed(weight_seed, frame_index)` both derive from the same
`weight_seed`.  The latter is a deterministic SHA-256 transformation of that
seed.  Therefore the actual code has

```
W1 = H(weight_seed)
Q_r = G(weight_seed, r)
```

rather than `Q_r independent of W1`.  Conditional on the seed (and, for an
injective practical generator, effectively conditional on `W1`), the frames
are fixed.  A cryptographic hash may be a useful pseudorandom heuristic but
does not make `E[C_r | W1] = 0` an exact mathematical statement.  This is not
a small numerical caveat: the theorem is the only justification for using the
learned correction as an unbiased control.

**Required repair.**  Choose one of these mutually exclusive paths before a
new audit:

1. Make M112 a randomized estimator: draw an independent Haar/QR seed from a
   precommitted entropy source, retain it only for replay, and make fresh
   output frames with that same independent draw.  State the bias class as
   randomized-unbiased (over the algorithmic draw), not deterministic
   conditionally unbiased.  The existing M111 bank cannot supply this proof.
2. Retain the existing reused frames only as a pseudorandom, ensemble-level
   heuristic OOF diagnostic.  Remove every "exact"/unbiased/control-variate
   claim, prohibit promotion from that diagnostic, and require a fresh
   independent-randomness validation before deployment.

A fixed public salt is a replay mechanism, not by itself a conditional-
unbiasedness proof; the experiment must include a draw independent of the
weights.

### B2. `equal_cost.measured_ratio` is semantically impossible to freeze
before M112 outcome analysis

The manifest accepts a prefilled scalar called `measured_ratio`, and
`classify_screen` treats it as a final equal-cost performance ratio.  But the
numerator of such a ratio is the variance/risk of the cross-fitted residual
and is unknown until `raw_outputs` have been analyzed.  A number frozen before
that event can be a **cost multiplier**, not an outcome-level performance
ratio.  As written, it is either arbitrary, outcome-leaking, or mislabeled.

**Required repair.**  Freeze a hashed pre-outcome cost calibration containing
an official measured candidate cost, base per-frame cost, and either
`N_base` (the integer number of base frames affordable at M112's cost) or the
corresponding score-aware multiplier `m`.  Then compute the outcome-dependent
quantity only inside the analyzer.  For the currently declared covariance
proxy and `R=50`, the simple equal-cost proxy is

```
rho_raw[j]     = trCov(residual[j]) / trCov(raw_outputs[j])
m              = N_base / R
rho_charged[j] = m * rho_raw[j]
```

because M112 averages `R` blocks whereas the equal-cost base averages
`N_base` blocks.  If the official score's cost multiplier is used instead,
freeze that exact mapping before analysis and calculate its result from
`rho_raw` inside the analyzer.  Gate predeclared charged per-network and
charged geometric ratios, and label them *OOF risk proxies*: overlapping
cross-fit training sets still prevent a direct estimator-variance claim.

### B3. The promised one-shot and release binding are not durable

`run_authorized_one_shot` accepts an arbitrary `output_dir` and only refuses
artifacts already in that particular directory.  The same source, manifest,
and input can be executed again by choosing another directory.  The known
execution token is not a durable claim.  This contradicts the "one-shot/no
retry" protocol.

In addition, the manifest verifies only the strings
`theory_audit == "pass"` and `cost_audit == "pass"`; it does not bind a
theory audit, independent audit, cost-calibration report, runtime, or their
hashes.  `ANALYSIS_CONFIG.json` contains a theory-report hash but the runner
does not verify it.  The raw archive is hashed and later reopened by pathname,
leaving a time-of-check/time-of-use window.  The core module is imported
before source hashes are verified.

**Required repair.**  Bind a single canonical output/receipt path and reject
all CLI alternatives.  Atomically create a durable `claimed` receipt before
input loading; retain it on success and failure, so no second location can
rerun the experiment.  Bind SHA-256 hashes and canonical paths for the theory
report, independent audit, cost calibration, runtime/package lock, and input
release.  Load from a verified immutable copy or an already-open file handle,
not by reopening a pathname after hashing.  Execute from a fresh isolated
staging directory made only of the manifest-listed files (`-I -B` or an
equivalent controlled launcher), so the loaded module bytes are the bytes
that were verified.

### B4. Reuse compatibility is not established

M112 regenerates W1 and Q from seeds using NumPy's normal generator and QR,
then pairs those C matrices with historical output rows.  Provenance records
the seed but not a W1 or Q-frame digest, and neither the runtime nor BLAS/LAPACK
implementation is pinned by the manifest.  A QR or RNG-version difference can
pair `Y_r` with a different `C_r`: that may preserve a zero-mean heuristic but
invalidates the claimed actual-output/pair coupling and can silently erase or
manufacture a screen signal.

**Required repair.**  Bind exact Python/NumPy/BLAS versions and verified W1
and complete-frame-bank digests produced before any M112 result read.  Better,
place non-outcome W1/Q digests in the raw provenance release and verify them
before deserializing output values.  If that provenance cannot be supplied,
the reuse bank is not a valid causal test of M112.

### B5. The cost and memory document is a lower-bound worksheet, not a full
official accounting

The core records float32 seed-law regeneration but float64 C, K, and ridge
work.  The reported dense-FMA figures do not apply the contest's float64
twofold billing multiplier; the three float64 subtotals alone require that
multiplier before QR, arcsine, allocations/copies, solver implementation,
wall residual, and base forwards are considered.  The counts cover four
offline screen networks rather than one deployable MLP and there is no
FlopScope/official-runner trace.  The stated 25 MiB is one retained dense C
block, not a measured peak including QR, axes, Sigma, dots, gates, temporary
matmul buffers, output/residual arrays, and allocator overhead.

**Required repair.**  Produce a pre-outcome official-environment trace for
one candidate MLP and its equal-cost base comparator, including float64
billing, every operation/copy/reshape, QR legality and charge, failed paths,
and residual wall time.  Freeze its report/hash and use it only to determine
the cost multiplier in B2.  Record a measured peak memory and a safety
margin.  Do not call the current scalar worksheet a full bill.

### B6. The target-free test command is not self-contained or sufficiently
binding

Invoking the documented script through the shell's default `python` selected
Python 3.14, where NumPy was absent, and failed before test collection.  It
passed only after explicitly selecting the workspace Python 3.12.13 runtime.
No dependency lock or runtime assertion is part of the eight-file surface.
The current tests also do not cover B1, B2, durable output identity, review
hashes, archive TOCTOU, environment/frame digests, or official float64 cost
conversion.

**Required repair.**  Add a locked runtime specification and launcher,
emit interpreter/NumPy/BLAS fingerprints in the pre-execution audit, and add
negative tests for each repair above.  Re-run all tests in the locked runtime
after the source is changed, then request a fresh independent audit.

## Audit disposition

The reusable mathematical components are preserved: the centered pair field,
raw Frobenius feature, and training-only response centering all remain valid
operators under a genuinely independent frame experiment.  The failed links
are the randomness/provenance claim, the equal-cost decision semantics, and
the execution/accounting lifecycle.  This is a **killed implementation at the
pre-execution gate**, not a rejection of connected gate-pair controls as a
research family.

No manifest, evidence result, submission, or champion mutation is authorized
by this audit.  After the listed repairs, M112 must begin again at a fresh
source-only audit; it must not be patched and then run against this bank
without re-freezing the full source surface.

## Audited file hashes (SHA-256)

| File | SHA-256 |
|---|---|
| `research_excursions/M112_CONNECTED_GATE_KERNEL_THEORY_20260807.md` | `3a83750049820131e47cfabed06a2e5fda53b597289abe7a9963e964ba10a480` |
| `m112_connected_gate_kernel_draft/ANALYSIS_CONFIG.json` | `7d7a1ca9c4e8eb4f688d0f482608aba74678542a435a06f87e94d54d2f35fab0` |
| `m112_connected_gate_kernel_draft/INVENTORY.md` | `d54dcf1a8248abca814bc1bec17396b11cf6499b690c171be1ee2c0e9eb92f87` |
| `m112_connected_gate_kernel_draft/REFERENCE_AND_PROTOCOL.md` | `102bb1c19421a835089aedea14ecc8fa88d87f72170ed9b8c59f234361c86231` |
| `m112_connected_gate_kernel_draft/analyze_m112_one_shot.py` | `531acad6a02361a4fac9cc89d05a7f0fdc38d680a1b6d85753455b999f6748ca` |
| `m112_connected_gate_kernel_draft/m112_connected_gate_kernel.py` | `6eb482650902b6d856143f9ddfbe4d2f24596559d26d2363779e0201ec3618c7` |
| `m112_connected_gate_kernel_draft/run_target_free_tests.py` | `ebe94e00d42569677f537d2d4a35b109c2c9f3ce3a94501c0424c848cd3b7538` |
| `m112_connected_gate_kernel_draft/test_m112_analyzer.py` | `ff8bfb25ca652722ceacc24afe15762a5ccaa8e5e035e89ea0bdb6672052b220` |
| `m112_connected_gate_kernel_draft/test_m112_core.py` | `6d2a2c8a4be273977c758dae72872374a900732a9bd137873522af185164d649` |
