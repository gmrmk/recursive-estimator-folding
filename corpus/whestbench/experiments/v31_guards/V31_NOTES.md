# v3.1 GUARDS build notes — M186 empty-regime + M187 finite-output

Date: 2026-08-08 (gate run completed 2026-08-09 02:27 UTC). Governing
evidence: `a_series_granular_adversarial/a4_results.json` + `A3_A4_NOTES.md`
(guard candidates M186/M187 and their cheapest falsifiers). Gate results in
`v31_results.json`; runner `run_v31_gates.py`.

**VERDICT: PASS — G1, G2, G3 all pass.** Candidate archive
`submission_kerdock_v31_guards_20260808.tar.gz`, sha256
`48664830e8709aff01aaad3d5dc9bb4de0ffac00f09b64adc4ea06401d2b8615`.

## Deviations (loud, before anything else)

1. **`sobol_owen_u32.npz` is included although the task text named only the
   `kerdock_phases.npz` asset.** The frozen v3 setup falls back to the base
   estimator for `width != 256`, and that path loads the Sobol asset;
   `whest validate`'s contract check runs at width 4 (v3's own
   `v3_package_manifest.json` records `validate_contract` output shape
   [2, 4]), so G3 cannot pass without it. The frozen v3 VALIDATED package
   shipped both npz files; v3.1 mirrors that surface byte-identically
   (sha256 `050339ec...`, matches the approved-asset hash in the v3
   manifest).
2. **M186 is the catch-the-specific-ValueError variant, not the task's
   "or better" analytic pre-check.** Two reasons. (a) The pre-check would
   run `_diagonal_gaussian_pass` a second time on EVERY net, violating the
   zero-added-billed-cost requirement on healthy nets; the catch variant
   adds exactly 0 billed FLOPs there. (b) Pilot-rescue reachability is not
   analytically decidable: rescue fires on the sampled pilot rows
   (`max(pilot_pre) > 0`), so no alpha-only pre-check can determine whether
   an all-cold layer empties. Uniqueness of the trigger: the message
   `matrix dimensions must be positive` is raised only by
   `cost_model.direct_cost`; in the frozen predict path the row count
   (2·n_base) is a fixed positive constant and the contracted width is the
   previous active count (nonzero, else the previous layer would already
   have raised), so within `predict` the message uniquely identifies an
   empty `next_active`. Any other ValueError is re-raised unchanged.
3. **M187 has a coded second tier the predeclaration did not spell out:**
   entries whose analytic fallback is itself non-finite are clamped
   (`nan_to_num`: inf → ±float32 max, NaN → 0.0 as the information-free
   last resort). On both hostile nets the tier never engaged
   (`m187_entries_clamped = 0`); every non-finite entry received a finite
   analytic mean, so "never zeros — analytic means are the best fallback"
   was honored in full on all observed inputs.
4. **Rotation-seed bookkeeping.** A4's baseline labels mlp.seed 901101
   "n8c rep 0", but the canonical formula used by n8c/n9/wc1/pb1/m185
   (`900000 + net_seed*1000 + r`) gives 1001000 for net 101 rep 0 — the A4
   label is internally inconsistent. G1 uses the canonical formula
   (mlp seeds 1001000 / 1102000 / 1203000 for nets 101 / 202 / 303,
   "t3-style" He construction = the shared n8c `he_weights_np`); the A4
   determinism artifact (seed 901101) is reproduced separately as a
   harness anchor (see cross-checks).
5. **A G0 byte-identity precondition was added** (sha256 of every copied
   frozen file vs the frozen directory, checked at every run) — an
   addition ahead of the predeclared gates, not a change to them.

## What was built

`package_source\` mirrors the frozen v3 package surface byte-for-byte
(all hashes equal to both the frozen candidate dir and
`v3_package_manifest.json`): `base_estimator.py`, `cost_model.py`,
`fold3_estimator.py`, `fold_estimator.py`, `row_blocked_winograd.py`,
`kerdock_phases.npz`, `sobol_owen_u32.npz`, plus the frozen `estimator.py`
riding along renamed `kerdock_v3_estimator.py` (sha256 `076d0a5d...`,
byte-identical). The only new file is `estimator.py` (sha256
`5e7d52156b330bf63ac4ff0e0f38d864b32677f82bc8ed4d1382787a27d3e0c9`):
`class Estimator(kerdock_v3_estimator.Estimator)` overriding `predict`
only.

- **M186**: `super().predict` wrapped; on the specific empty-regime
  ValueError, return the analytic diagonal-pass means for all layers,
  computed on the SAME Haar-rotated net the frozen predict used (the
  rotation is deterministic in `mlp.seed`, so the fallback reproduces the
  analytic means the crashed run had already computed). Billed honestly
  inside the caller's BudgetContext; failure path only.
- **M187**: `fnp.isfinite` scan + reduction on the returned (depth, width)
  stack. All finite → the parent's array object is returned untouched
  (bitwise identity on healthy nets is structural, not incidental).
  Otherwise non-finite entries are replaced from the analytic fallback
  stack; still-non-finite entries (never observed) are clamped as in
  deviation 3. Guard activations in `est.last_guard_report`.
- Healthy-net guard cost: **24,575 billed FLOPs** (measured, constant
  across all three G1 nets) — the isfinite scan + `all` reduction of the
  32×256 stack, billed through flopscope like every frozen op.

## Gate results (first run, no retunes)

**G1 — bitwise identity + billing (PASS).** Per net (v3 vs v3.1, same
setup/seeds, separate subprocesses):

| net | mlp seed | bitwise equal | v3 billed | v3.1 billed | delta | fraction |
|---|---|---|---|---|---|---|
| He 101 | 1001000 | yes | 180,098,814,627 | 180,098,839,202 | +24,575 | 1.365e-7 |
| He 202 | 1102000 | yes | 169,075,184,731 | 169,075,209,306 | +24,575 | 1.453e-7 |
| He 303 | 1203000 | yes | 162,819,252,832 | 162,819,277,407 | +24,575 | 1.509e-7 |

All three ~700x under the +0.1% ceiling; both guards quiet on all three.

**G2 — guards fire on A4's hostile nets (PASS).**

| net | v3 (frozen) | v3.1 | guard fired | v3.1 billed |
|---|---|---|---|---|
| f_negshift (rng 4405, mlp 555006) | ValueError crash, billed 5,159,851,464 = A4 exactly | completes, all-finite | M186 | 5,293,173,363 (2.0% of budget) |
| b_gain_1e3 (rng 4401, mlp 555002) | silent NaN, billed 154,722,710,745 = A4 exactly | completes, all-finite | M187 (164 entries replaced from analytic means, 0 clamped) | 154,856,155,520 (56.9% of budget) |

Both v3.1 runs complete finite within the real 2.72e11 budget.

**G3 — packaging (PASS).** `whest package` (folder mode, pinned v0.14
CLI) rc=0; `validate-package --json` ok=true; `whest validate --json`
(contract, loads + runs) ok=true; `tar -tzf` lists exactly the 10 expected
members (9 sources + packager `manifest.json`), nothing missing, nothing
unexpected, no `__pycache__` — the T3 near-miss rule. Manifest entrypoint
`estimator.Estimator`, api_version 2.0.

## Cross-checks (the second signals)

- **Harness anchor**: the v3 arm re-ran the A4 determinism net (He 101,
  mlp.seed 901101) — output bitwise equal to the stored
  `a4_det_run1.npz` stack and billed exactly 179,197,201,680 (= A4).
- **Failure reproduction**: frozen v3 billed on both hostile nets matches
  `a4_results.json` to the FLOP (5,159,851,464 and 154,722,710,745), and
  the f-net traceback carries the same `matrix dimensions must be
  positive` message.
- **M187 recount**: an independent in-process diagnostic (scratchpad,
  frozen v3 direct) found exactly 164 non-finite entries, all NaN, all in
  the final sampled row 31; analytic rows 0–30 finite; the analytic
  final-layer means finite at all 164 neurons; full analytic fallback
  stack finite everywhere — matching the guard report
  (replaced_analytic=164, clamped=0) from a second derivation.
- **Byte identity**: every copied file's sha256 equals both the frozen
  directory's and `v3_package_manifest.json`'s records; the shipped tar
  was extracted and every member re-hashed against `package_source`
  (0 mismatches); the packager manifest embeds the same frozen hashes.

## Rerun

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& "C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\work\whest-v014\Scripts\python.exe" `
  "C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\v31_guards\run_v31_gates.py"
```

Single foreground process orchestrating per-arm subprocesses (module-name
isolation between frozen v3 and the v3.1 package); ~3 minutes total.
No submission was made; no frozen source was edited; no git commands.
