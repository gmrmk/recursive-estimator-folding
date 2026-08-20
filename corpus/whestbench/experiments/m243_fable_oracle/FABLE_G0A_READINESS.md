# FABLE G0A READINESS -- independent M243 oracle (two-agent protocol)

Date: 2026-08-09
Implementer: Fable (compute-runner), independent of Codex Sol's candidate.
Implemented SOLELY from the two hash-verified frozen inputs below.  No file
in `m243_event_local_q4_source_premise/` other than those two was read, and
nothing in that folder was written or touched.

## 1. Hash-verification transcript

First action of the session, before any other read:

```
a53e3cbf58b9bdc290e6abbf3323a1b7e5162a370774dcd918ddb2193340a9c3
  M243_PREDECLARATION_20260809.md          MATCH (predeclaration target)
2f788fdc8d91abb8cd43b9ce82140c12cc5707b49b9f815c56abae105b906895
  M243_FROZEN_MANIFEST_20260809.json       MATCH (manifest target)
```

Shared frozen corpus modules, hash-checked against the manifest's
`parent_sha256` block at import time (the `import_frozen` hook hard-fails
on mismatch and is re-run on every entry-point start):

```
fa3614a22c2250f69f4d891834cc1e7ca6bd8874d67575b87c7d3fa8598f1c5c
  ..\m178_certified_phi2_owent\m178_certified_phi2_owent.py   MATCH
c296c95ede532c1451e0444b9d56b51e96287ef251b11de9cacee0df7d1ea6b1
  ..\m133_ht_hidden_edge\m133_ht_hidden_edge.py               MATCH
520431079e63b4bb82c6fe3db997d875ce31fc4037538eb64ce7fea24bf55cd5
  ..\m151_b1_forward_control\m151_b1_forward_control.py       MATCH
c765fe24818f4ec8928a879e217a530077edff98f729555739202c1f7286f927
  ..\m122_nonzero_bridge_theory\m122_nonzero_bridge.py        MATCH
```

## 2. DEVIATIONS and interpretation decisions (recorded loudly)

D1. **Errata excluded by protocol.** The frozen folder also contains
    `M243_PREIMPLEMENTATION_ERRATUM{,2,3}_20260809.md` and manifests
    V2-V4.  My task restricts reading to the two hash-verified files, so
    this oracle implements the BASE predeclaration + BASE manifest only.
    If Sol's G0A reference follows an erratum chain, any disagreement
    must first be adjudicated against that chain by the orchestrator
    before it is treated as a formula kill.
    OBSERVED DURING THIS SESSION: Sol wrote concurrently into the frozen
    folder (M243_PRELAUNCH_ERRATUM4, MANIFEST_V5, SHA256SUMS_V3, and a
    grown run_m243_g0a.py, mtimes 16:29-16:51 on 2026-08-09).  The two
    hash-verified inputs themselves are byte-identical before and after
    (re-hashed at session end: both MATCH).  The erratum chain is now at
    least four deep; the adjudication note above is therefore not
    hypothetical.

D2. **Shard structure is a task directive, not predeclaration text.**
    The predeclaration defines two 128-draw cells (P0, P1); the split
    into four shards (P0/P1 x occurrence indices 0..63 / 64..127) comes
    from the task instructions and is frozen in `SHARDS`.

D3. **`corr(raw raw^T)`** (section 9) is read as the correlation
    normalization `D^{-1/2} M D^{-1/2}` of the Gram matrix
    `M = raw @ raw.T`.  Alternative reading (`np.corrcoef` of M's rows
    as data vectors) was rejected as less literal.  This is the one
    regeneration fork most worth cross-checking against Sol's G0A run.

D4. **Outer split points.** The text says "split at `g = -alpha_i`"; the
    antithetic fold is even in g with kinks at both `+-alpha_i`, so both
    are used as split points (subsumes the literal requirement).

D5. **`Tree_iijk`** = the order-4 M122 tree convention continued onto the
    `(i,i,j,k)` collision -- a single-entry local evaluation of
    `m122.tree_tensor_continuation`, verified bit-tight against the
    frozen tensor in self-test T5.  Per-node gamma2/gamma3/scale come
    from frozen `m122.power_hermite_coefficient`; the pair bridge comes
    from this oracle's positive-part reference (the frozen m147
    endpoint-safe bridge exists as an alternative and is unused, since
    m122's own `build_state` is width<=8 and G0B cells are width 12).

D6. **RAW1/RAW2** are named but not defined in the frozen text.
    Implemented: RAW1 = single unfolded draw `r(G)b(G) - Wick - Tree`
    (conditional variance as reported); RAW2 = mean of two iid raw calls
    (equal-two-call baseline, Var = Var_RAW1 / 2).

D7. **`V_Delta = Var_q[Delta_e F_e/(2 q_e)]`** of a vector quantity is
    read as the total variance `E||X||^2 - ||E X||^2`.

D8. **Arms.** "actual-M178 arm" = section-4/5 closed forms evaluated in
    float64 through ONE certified `m178.evaluate(a, b, rho)` call per
    event (exactly the candidate's path); "ideal arm" = coefficients
    from direct high-precision integration `E[b He_r]/r!` and
    `E[r He_r]`, which the reference may compute (it never imports the
    proposed beta/R closed forms).

D9. **Bootstrap details.** `upper90` = 90th percentile of the paired
    bootstrap ratio distribution (one index resample drives every ratio
    in a replicate); p99 contributions are per drawn event with
    `np.percentile` linear interpolation; Philox(2430002), 20000
    replicates, exactly as frozen.

D10. **Two-signal cross-check choice.** The per-event Delta is
    re-derived through frozen M122 Hermite-SERIES raw moments.  The
    M122 Gauss-Hermite helper was measured UNCONVERGED at the ReLU kink
    (orders 42/80/160/320 wobble ~1e-4 around the true value) and was
    rejected as a reference signal.

D11. Duplicate G0A events are deduplicated on exact ordered-tuple
    equality (section 8 "duplicate width-3 events are evaluated once").

D12. `mpmath` was not installed in this environment; installed 1.4.1
    via pip (environment note, not a spec deviation).  numpy 2.4.4,
    Python 3.14.4.

## 3. Shared frozen corpus modules used (paths)

- `corpus\whestbench\experiments\m178_certified_phi2_owent\m178_certified_phi2_owent.py`
  -- `evaluate(a,b,rho)` -> (P, A, B, D) for the actual-M178 arm;
  refusals propagate as `OracleHardFail` (fail closed).
- `corpus\whestbench\experiments\m133_ht_hidden_edge\m133_ht_hidden_edge.py`
  -- `collision211_factored_proposal(q, W, uniform_mixture=0.05)` and
  `Factored211Proposal.sample/.probability` for q0 and the frozen
  128-draw event streams.
- `corpus\whestbench\experiments\m151_b1_forward_control\m151_b1_forward_control.py`
  -- `source_feature_211(W, i, j, k)`: the complete three-slot
  aaaa/aaab/aabb feature, flattened with all three slots present.
- `corpus\whestbench\experiments\m122_nonzero_bridge_theory\m122_nonzero_bridge.py`
  -- `power_hermite_coefficient`, `pair/triple_raw_moment_series`,
  `rectified_power_moment`, `tree_tensor_continuation`, `build_state`
  (self-test only, width<=8).

## 4. Self-test outcomes (synthetic fixtures only)

`python test_fable_oracle.py` -- **34/34 PASS** (transcript mirrored in
`selftest_results.json`).  Test precision dps (16, 22) / coarse (12, 16);
production precision stays frozen at (80, 100).  Highlights:

- Bias contract: E[Z_ANTI], E[Z_Q2], E[Z_Q4] all equal Delta;
  residuals ~1e-25 (ideal arms) and ~5e-19 (actual arms).
- Two-signal Delta: nested-quadrature 7.127850257291e-03 vs frozen
  M122 series re-derivation 7.127850257290e-03.
- Gate-1/2 style: all five closed R and all five actual-M178 beta agree
  with direct integration to display precision on the fixture.
- Tree single-entry vs frozen continuation tensor: exact to 1e-12 rel.
- Variance ordering already visible on the fixture:
  RAW1 6.16e-3 > ANTI 3.15e-3 > Q2 2.27e-5 > Q4 1.77e-7.
- Ownership: typed refusals on collisions and on [4]/[3,1]/[2,2]/[1^4];
  q_e hook hard-fails on zero support and on collision draws.
- j<->k swap symmetry and positive diagonal gauge (physical degree
  `lambda_i^2 lambda_j lambda_k`) verified.
- Manifest: real frozen manifest passes format validation; a corrupted
  copy (kept in `selftest_artifacts\`, never the frozen folder) hard-fails.
- Shard plumbing: shard map, checkpoint/resume (6 events, interleaved
  runs, no recompute), wall-clock cap exit, RSS probe (1069 MiB live
  value), aggregator + paired bootstrap on synthetic records.

## 5. Runtime observation (honest cost note)

One full per-event oracle at TEST precision (20, 28) took a measured
176 s on this machine (nested quadrature; node-level caching already in
place).  Even at that test-precision rate, 64 events = 11,264 s > 2 x
5400 s; mpmath arithmetic and tanh-sinh node counts grow with working
digits, so the frozen (80, 100) per-event cost is bounded below by the
measured one.  A 64-event shard therefore spans multiple 5400 s
invocations (derived from the measurement above; the exact (80, 100)
per-event time was not measured -- measuring it is one
`oracle_event(..., dps_pair=(80, 100))` call).  The runner is built for
exactly that: JSONL checkpoint after every event, resume skips completed
occurrences, exit codes 3 (wall) / 4 (memory).

## 6. Readiness statement

The four G0B shard runners are implemented, self-tested end-to-end on
synthetic fixtures, and hash-locked to the frozen inputs:

```
python run_shard.py --shard {0,1,2,3} --authorize-g0b
```

Without `--authorize-g0b` the runner dry-runs (hash checks + manifest
validation + plan print) and exits 0 -- verified for shards 0 and 3.
No G0B evidence run and no long shard was executed, per protocol.
READY for the four G0B shards, pending Sol's G0A PASS trigger
(predeclaration section 11, step 6).  If Sol's G0A fails, stop; nothing
here retunes formulas, cells, tolerances, or charts.
