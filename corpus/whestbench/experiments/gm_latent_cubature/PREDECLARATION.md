# PREDECLARATION - gm_latent_cubature

Written 2026-08-10 BEFORE any experiment code was authored.
Graveyard revival item: `gm_latent_cubature`, mining key `latent_sparse_radial_cubature`.
Target ledger record: `corpus/whestbench/headroom/fold_ledger.json` candidate index 11,
`id = latent_sparse_radial_cubature`, `status = proposed`, **no `result` field**.

## 1. What the original kill actually measured

Index 11 was never measured. Its sibling index 12
(`latent_sparse_radial_harness`) was killed: two in-process Python workers reached
24.6 GB and 13.8 GB working set and were stopped externally after completing only
3 of the predeclared 8 width-64 cases.
`corpus/whestbench/experiments/LATENT_SPARSE_RESOURCE_POSTMORTEM.md` localises the
fault statically to `reduce_components`: on the last equal-mass bin the loop can
reach `remaining > eps*total`, `capacity == 0`, hence `take == 0`, appending a
zero-weight `GaussianComponent` forever with no bin-advance branch available.
The postmortem states in terms that this is "an orchestration/resource-containment
failure around a nonreturning implementation path, not evidence about sparse-radial
estimator accuracy or mathematical viability", and directs that the frozen `tau=0.5`
mathematical candidate stay pending.

## 2. Changed premise

The repair the postmortem demanded now exists and has been exercised by the sibling
lineage: index 13 (`latent_randomized_radial`) contains the same q=3 equal-mass
compressor **with a zero-progress last-bin guard** and ran the identical eight-case
bank at 37.04 MB peak; index 14 ran fresh n=128 cases at 241.91 MB peak with
"reducer guards pass". So the missing measurement is now a re-freeze, not new
engineering.

## 3. Mechanism under test (unchanged from the frozen candidate)

Frozen implementation
`work/scorefloor_generation/latent_sparse_cubature/latent_sparse_cubature.py`
(SHA-256 `A31FD018...C4F24C`), frozen contract `premise_contract.json`
(SHA-256 `DF2EF00F...C97A400A`). Both are read-only inputs; neither file is edited.

Weight-defined Gaussian-mixture state, analytic coordinatewise Gaussian ReLU
moments, deterministic q=3 equal-mass recompression. Per parent component with
preactivation covariance `S`:

- eigendecompose `S = sum_i lambda_i v_i v_i^T`, `lambda` sorted descending;
- adaptive rank `r` = smallest rank with `sum_{i<=r} lambda_i >= tau * tr(S)`,
  `tau = 0.50`, extended through any relative eigengap tie
  (`<= 1e-10 * lambda_1`), refusing a non-identifiable repeated selected
  eigenspace by returning rank 0;
- factors `F = V_{:r} diag(sqrt(lambda_{:r}))`, residual variance
  `diag(S) - rowsum(F*F)`;
- signed spherical-radial nodes `mu +/- sqrt(r) * F_{:,j}`, each with weight
  `w_parent / (2r)`, giving `2r` children per parent (`O(qr)`, not `q^r`).

The ONLY change is the revival mechanism itself: `reduce_components` is replaced,
by in-process monkeypatch of the imported frozen module (never by editing the
frozen file), with the zero-progress-guarded equal-mass compressor whose structure
is copied from index 13's `randomized_radial.py`:
last bin absorbs `remaining`; otherwise `capacity = max(target - bin_mass, 0)` and
`capacity <= tol` advances the bin; `take <= 0` raises `ArithmeticError`.
The frozen `relative_gap_tolerance = 1e-10` and the frozen bin-advance threshold
semantics are preserved. Each of the eight cases runs in its own separately
killable child process with an externally enforced RSS watchdog and wall clock.

## 4. Quantities and gates (verbatim from index 11's own `kill_condition`
   and `PREDECLARED_GATE.md`)

Eight frozen fresh width-64 cases: depth 16 seeds 18560/18561/18562/18563 and
depth 32 seeds 18720/18721/18722/18723. Weights iid `N(0, 2/n)` from
`np.random.default_rng(seed).normal(0.0, sqrt(2/n), (n,n))` per layer.
Truth and comparator predictions are read from the banked
`work/scorefloor_generation/latent_full_sigma/fresh_n64_results.json`; **no truth
generation, no WHest data, no scorer, no holdout, no API, no network.**

- `MSE_case = mean((prediction - truth)^2)`.
- `R = sum_cases MSE_candidate / sum_cases MSE_correctedfullcov`.
- `W = #{cases : MSE_candidate < MSE_correctedfullcov}`.

GATE 1 (accuracy): KILL if `R > 0.80`.
GATE 2 (wins):     KILL if `W < 6` of 8.
GATE 3 (invariance): KILL if permutation or positive-scale equivariance fails at
  relative tolerance `1e-10`, or if the adaptive ranks differ under either map.
GATE 4 (step-0 arithmetic): KILL if the conservative `n=256, L=32` target
  operation count under FlopScope 0.10.0 pricing is `>= 80e9`.

Survival requires all four. Per the FOLD method, **GATE 4 is run first and the run
stops there if it kills.**

## 5. Step-0 arithmetic definition

FlopScope 0.10.0 is the installed pinned version
(`flopscope 0.10.0+np2.4.6`). Its per-op weights are read from the installed
package (`flopscope._weights.get_weight`), not from memory: gather/sort family
(`take`, `sort`, `argsort`, `searchsorted`) weight 4.0; copy family
(`copy`, `concatenate`) weight 1.0; `zeros`/`empty` weight 0.0; base cost is
element count.

Static conservative envelope, per layer, `q=3`, worst case `r <= n`,
`M <= 2qn` children (index 11's own declared envelope):
`2q n^3` covariance sandwiches + `9q n^3` component eigendecompositions +
`9 n^3` recompression eigensolve + `12q n^3` child moment/rebin passes +
`2 n^3` remainder = `80 n^3` per layer = `80 L n^3 = 42,949,672,960` at
`n=256, L=32`.
Data-movement terms omitted by that 2026-08 envelope but billed by FlopScope
0.10.0, priced conservatively at worst case:
per-child `np.diag(n)` fill `M * n^2 = 2qn * n^2 = 6 n^3` at weight 1.0;
per-parent eigenvector gather `4 n^2`, eigenvalue gather `4n`, `argsort` `4n`,
`searchsorted` `4n`, factor copy `n*r <= n^2`, times `q`;
compressor `argsort`/gather over `M` scores `8M`.
Total charged, then `x1.25` contingency exactly as index 13 charged its 70.590B.

Cross-check (second, independent signal for GATE 4): an element-count instrument
wrapped around the actual estimator run at `n=64` and `n=128`, `L=32`, tallying
observed elements per FlopScope op category, extrapolated to `n=256` by fitted
power law, then priced with the same installed weights. The two numbers must
land on the same side of the 80e9 threshold.

## 6. Predicted outcome, on the record, before running

- GATE 4 (step 0): **PASSES** (does not kill). Point prediction: static charged
  total `86 L n^3 = 46.18e9`, `57.7e9` with 25% contingency; empirical
  extrapolation far lower because the observed adaptive rank is small
  (`rank_mean ~ 4` at `n=64` in the original partial trace), not `r = n`.
  Both well below `80e9`.
- GATE 1 (accuracy): **FAILS -> KILL.** Point prediction `R` in `[1.0, 3.0]`,
  centred near `1.3`. Basis: the original partial run's own three completed cases
  give `adaptive_ratio_to_corrected_fullcov = 1.2774834128062247` with case ratios
  `3.293371022811928, 0.7635702249674016, 1.0545677012793533`; and the frozen
  full-rank parent of this rule (fixed covariance axes, single radius `sqrt(n)`)
  scores aggregate ratio `8.8716` / 1-of-8 wins in both
  `latent_full_sigma/fresh_n64_results.json` and index 13's factorial cell
  `fixed_axes__sqrt_n`. Index 13 established that the causal repair is angular
  randomisation (Haar), which this candidate does not have.
- GATE 2 (wins): **FAILS -> KILL.** Point prediction `W <= 3` of 8.
- GATE 3 (invariance): PASSES (the original run already recorded permutation
  `2.04e-16` and positive-scale `<= 4.27e-16` with `ranks_equal: true`);
  re-run here for completeness.
- Overall predicted verdict: **KILL_CONFIRMED** at the accuracy gate.
- Predicted expected gain: zero for the score. Payoff is closing one of exactly
  three no-result records in the 242-record ledger.

An outcome of `R <= 0.80` AND `W >= 6` would be `REVIVED_PASS` and I would report
it as such. I will not retune tau, q, the radius, the case set, or the seeds after
seeing any number. There is no arm here other than the one frozen candidate.

## 7. Two-signal verification plan for any claim

1. **Weights/bank seal**: recompute the corrected-fullcov comparator predictions
   from my regenerated weights with the frozen `corrected_fullcov.py` and require
   max abs deviation from the banked `corrected_fullcov_prediction` `<= 1e-12`,
   and banked `baseline_mse` reproduced to `<= 1e-18` absolute.
2. **Repair-neutrality seal**: my repaired-reducer candidate MSEs for the three
   cases the original run completed (seeds 18560/18561/18562) must match
   `latent_sparse_cubature/premise_results.json`
   `adaptive_tau05_sparse_radial.mse` to `<= 1e-12` relative. This proves the
   zero-progress guard changed no mathematics on cases that terminated.
3. **Bit-repeat**: the full eight-case bank is run a second time in fresh child
   processes; every case MSE must be bitwise identical.

## 8. Resource containment and firewall

- Each case in its own `subprocess`; RSS watchdog samples
  `GetProcessMemoryInfo` every 0.25 s and hard-exits at
  `2,000,000,000` bytes working set; per-case wall limit 600 s;
  total compute envelope 90 minutes.
- BLAS pinned to one thread before NumPy import.
- Writes confined to
  `corpus/whestbench/experiments/gm_latent_cubature/`.
- Read-only elsewhere. No git. No network. No submissions. No reads of
  truth/scorer/private/holdout. No contact with `m245_*`/`M243`/`M244`/`tasks`/
  `journal-m245*`.
- If the falsifier cannot run cleanly inside 90 minutes I return BLOCKED with the
  precise obstruction rather than silently scaling down.
