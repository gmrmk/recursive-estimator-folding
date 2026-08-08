# N8a build notes — KILLED AT G0 (premise gate)

Date: 2026-08-08. Predeclaration: N8A_PREDECLARATION.md (governs).

## DEVIATIONS FROM THE PREDECLARATION (read first)

1. **G0 downstream is the plain antipodal ReLU forward mean, not the full
   fold3 pipeline.** The predeclared phrase "matched downstream processing"
   was read as "identical between arms (a) and (b)", and the
   sampling-stage-isolating downstream (antipodal doubling + ReLU forward +
   final-layer mean, the same downstream shape as N7's `rqmc_mean`) was used
   for both arms. The full fold3/pilot-rescue pipeline was reserved for G2,
   which was never reached. The kill margin (see below) is ~2.5x on the
   safe side of the threshold, so this choice is not outcome-carrying.
2. **Arm (a) replicate randomization is the Haar rotation seed.** The frozen
   estimator seeds its Haar rotation with `mlp.seed` (deterministic per
   net); the rotation is the construction's only stochastic device, so
   replicate variance was measured over independent rotation seeds. The
   arms are paired: replicate r of arm (b) shares arm (a)'s rotation and
   adds its own Cranley-Patterson shift.
3. **Arm (b) is radially conditioned to the v3 fixed radius** (the
   `base_estimator.py` conditioning path, scale-to-mean-chi), because that
   is the draw-stage swap G1 would actually have shipped — it keeps the
   frozen `_radial_covariance` constant and the tangent correction valid.
   The unconditioned N7 construction would additionally perturb the bias
   mechanism, which the predeclaration forbids ("changes variance, not the
   bias mechanism").
4. **R = 16 replicates per net** (the predeclaration fixes 3 nets for G0
   but is silent on replicates).
5. **A diagnostic iid arm (radially conditioned MC) was added** — not a
   gate, recorded only to locate both constructions against a common
   baseline.
6. **Multithreaded BLAS was used.** G0 has no FLOP metering (t3's
   thread-pinning exists for metering fidelity); single process throughout.
7. **G1–G3 were never implemented** — no variant source, no
   `package_source/`, no package. Predeclared stop at the first broken
   link. `run_n8a_gates.py` therefore contains G0 only, with an explicit
   stop.

## What the v3 sampler actually is (G0 premise finding)

The frozen Kerdock M71 v3 sampler at the width-256 benchmark contract is
**not iid — it is a deterministic structured spherical construction**:

- `kerdock_phases.npz` (the estimator's own shipped sampling asset,
  confirmed from `estimator.py`: it is loaded in `setup()` and consumed by
  the first sample product) packs 128 sign vectors; the trim `[2:128]`
  keeps 126 phase vectors in {-1,+1}^256.
- The effective first-layer directions are the rows of
  `mean_chi(256) * H_norm @ diag(phase_s)` for s = 2..127: 126 orthonormal
  phased-Hadamard (Kerdock-code) frames x 256 rows = 32,256 directions,
  every one with exact radius mean_chi(256) = 15.98438 (fixed-radius
  spherical design; `radial_conditioning=True` with
  `_radial_covariance = mean_chi^2/256`).
- Antipodal doubling in fold3 (`ReLU(x)`, `ReLU(-x)`) brings the evaluation
  count to 64,512.
- The only randomization is a Haar rotation (float32 QR, sign-fixed),
  seeded per net by `mlp.seed` and absorbed into `W1`.
- The Owen-scrambled Sobol asset (`sobol_owen_u32.npz`) is used **only** on
  the width != 256 fallback path and was neither needed nor loaded.

So the predeclaration's structured branch applied: paired variance of the
existing construction vs Kronecker+CP antithetic at matched sample count.

## G0 result — KILL

3 He-init f32 width-256 depth-32 synthetic nets (t3-style construction,
seeds 101/202/303), native count 32,256 (+antipodal), 16 paired replicates:

| net | var (a) Kerdock | var (b) lattice | ratio b/a | a/MC diag | b/MC diag |
|-----|----------------|-----------------|-----------|-----------|-----------|
| 101 | 2.035e-07 | 4.446e-07 | 2.185 | 0.355 | 0.775 |
| 202 | 5.690e-07 | 8.140e-07 | 1.430 | 0.492 | 0.704 |
| 303 | 2.178e-07 | 6.510e-07 | 2.989 | 0.312 | 0.932 |

- Aggregate (geometric mean) ratio **b/a = 2.106**, paired bootstrap 95% CI
  **[1.645, 2.645]** — the entire CI is above 1.0, i.e. the lattice is
  significantly *worse*, not merely short of the predeclared 1.2x gain.
- Kill rule: ratio > 0.83 kills. **2.106 > 0.83 — KILL.**

Reading of the diagnostics: the Kerdock frame construction already beats
radially conditioned iid MC by 2.0–3.2x at this sample count (a/MC =
0.31–0.49), while the Kronecker+CP lattice manages only 1.07–1.42x over the
same baseline (b/MC = 0.70–0.93; consistent with N7's gains being an
against-iid measurement that shrinks once the radial degree of freedom is
conditioned away). The N7 mechanism's headroom is a strict subset of what
the orthogonal-frame + fixed-radius + antipodal structure already
captures — and the frames capture more. The first broken link is the N8a
premise itself; per the predeclaration, no build, no tuning, no G1–G3.

## Artifacts

- `run_n8a_gates.py` — G0 runner (exactly what was executed).
- `n8a_results.json` — machine-readable per-net variances, ratios, CI,
  verdict.
- `N8A_BUILD_NOTES.md` — this file.
- No variant source, no package (never reached).

Environment: pinned `work/whest-v014/Scripts/python.exe` (Python 3.14.4,
numpy 2.4.6), single process, ~6 min total compute. Frozen v3 directory
was read only; nothing outside `n8a_rqmc_kerdock/` was modified.
