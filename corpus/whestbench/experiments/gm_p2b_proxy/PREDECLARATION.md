# PREDECLARATION -- gm_p2b_proxy (graveyard revival of `p2b_weights_only_rotation_proxy`)

Written 2026-08-10, BEFORE any code in this directory ran. Nothing below is edited
after the first execution; deviations are appended to VERDICT.md under DEVIATIONS.

## 0. Provenance (read first, per the fold method)

Mining record: workflow `wf_436a0c3d-2f0`, journal line 31, revival candidate
`p2b_weights_only_rotation_proxy (reopening gen3_p2_rotation_selection)`.

Ledger records read (read-only):
- `corpus/whestbench/headroom/fold_ledger.json` -> `gen3_p2_rotation_selection`
  (status `killed`; oracle-of-8 = 61.6% recorded unharvested; broken links =
  pilot proxy rho -0.089 and pilot cost 33.4% of B vs a 5% gate)
- same file -> `p2b_weights_only_rotation_proxy` (status `killed`; best pooled
  |rho| = 0.166)

Experiment dirs read (read-only):
- `corpus/whestbench/experiments/pb1_premise_battery/`
  (`run_p2_rotation_selection.py`, `p2_results.json`, `p2b_results.json`,
  `run_p2b_weights_proxy.py`, `p2_partial_net{101,202,303}.npz`)
- `corpus/whestbench/experiments/a_series_granular_adversarial/run_m185_g0.py`
  (`rotated_alphas`, `weight_diagnostics`)
- frozen v3 source (imported read-only, never edited):
  `work/scorefloor_generation/kerdock_l1_owned_buffer/candidate_source_validator_v3/`
  (`base_estimator._diagonal_gaussian_pass`, `estimator.Estimator._haar_rotation`)

## 1. Mechanism under test (verbatim intent of the mining record)

P2b tested three proxies that are all functions of `(rotation, W_1)` only --
layers 2..32 never enter. The mined revival claims the *un-probed* class is the
estimator's own **zero-sample diagonal Gaussian pass on the rotated net, all 32
layers**: for each of the 48 archived (net, rotation) pairs run
`rotated_alphas()` then `weight_diagnostics()`, take
`borderline_frac_overall`, `fold_on_total`, `fold_kink_total`, and correlate
them within-net-ranked against the archived `mse_per_rotation`.

Cost claim being revived: ~5e8 FLOPs for 8 candidate rotations, ~0.2% of
B = 2.72e11, versus P2's 33.4% -- i.e. a selection stage 25x under P2's cost gate.

## 2. STEP-0 ARITHMETIC GATE (run first; STOP if it kills)

The whole revival rests on one premise: **the diagonal Gaussian pass on the
rotated net carries within-net rotation information.** That premise is checkable
in closed form before any experiment runs.

`_diagonal_gaussian_pass` starts at `mu = 0`, `var = 1` (isotropic standard
Gaussian input) and propagates only diagonal moments:

    mu_pre  = mu  @ W                       -> at layer 0: 0 @ W = 0 exactly
    var_pre = var @ (W * W)                 -> at layer 0: var_pre[j] = ||W[:,j]||^2
    sigma   = sqrt(max(var_pre, 1e-12));  alpha = mu_pre / sigma

v3 rotates only the first layer: `W = R.T @ W_1` with `R` orthogonal (Haar, QR
sign-fixed). For any orthogonal `R`,

    || (R.T W_1)[:, j] ||^2 = || R.T W_1[:, j] ||^2 = || W_1[:, j] ||^2 .

Therefore `var_pre` at layer 0 is EXACTLY rotation-invariant, `mu_pre` is
identically zero, `alpha[0] == 0` for every rotation, and the state
`(mu, var)` entering layer 1 is rotation-invariant. By induction every
subsequent layer's `alpha` -- hence every statistic in `weight_diagnostics()` --
is rotation-invariant in exact arithmetic. The only rotation dependence that can
survive is float32 rounding in the QR and in `R.T @ W_1`.

**Step-0 gate (arithmetic, no experiment):** for each net in {101, 202, 303} and
each r in 0..15 compute `R = KerdockV3._haar_rotation(900000 + net*1000 + r, 256)`
and the per-column squared norms of `R.T @ W_1` versus those of `W_1`.

- PREDICTED (on record): max relative deviation < 1e-4 (float32 accumulation
  level), i.e. the layer-0 input to the diagonal pass is rotation-invariant to
  rounding.
- KILL CONDITION: if the deviation IS at rounding level, the mined proxy class
  has zero within-net signal BY CONSTRUCTION and the revival is dead at step 0.
- REVIVE CONDITION: if the deviation is >= 1e-2 relative for some (net, r), the
  invariance argument is wrong and step 1 must be run on its merits.

Step 0 kills or survives on this number alone. If it kills I still run step 1
(it costs minutes and yields the measured rho the record asks for), but the
verdict is already determined and step 1 is reported as CONFIRMATORY, not as a
retune.

## 3. STEP 1 -- the cheapest falsifier exactly as mined

48 calls to `rotated_alphas(he_weights(net), 900000 + net*1000 + r)` followed by
`weight_diagnostics(alphas)`, nets 101/202/303, r = 0..15. No sampling, no
forwards, no truth, no responses.

- y = `p2_results.json -> q1_oracle_headroom.per_net[net].mse_per_rotation`
  (archived, committed, read-only).
- x in {`borderline_frac_overall`, `fold_on_total`, `fold_kink_total`}.
- Statistic: pooled WITHIN-NET-RANKED Spearman, computed exactly as
  `run_p2_rotation_selection.pooled_within_net_rho` (Pearson on within-net
  average ranks pooled over the 48 points).

### Gate numbers (unchanged from P2b; no retuning permitted)

| gate | threshold | direction |
|---|---|---|
| pooled within-net-ranked \|rho\| for ANY of the three diagnostics | >= 0.40 | PASS -> rotation selection reopens |
| per-net Spearman sign consistency for the passing diagnostic | same sign on all 3 nets | required in addition |

- REVIVED_PASS iff some diagnostic has pooled |rho| >= 0.40 AND its three per-net
  Spearman values share one sign (and none is exactly 0).
- KILL_CONFIRMED otherwise. A kill confirms and strengthens the original ledger
  record: the rotation family is then closed on a fourth, deepest proxy class.

## 4. Predicted outcome, on record

I predict **KILL_CONFIRMED**. Concretely, before running:

1. Step 0 max relative column-norm deviation < 1e-4.
2. Every one of the three diagnostics is constant or near-constant within each
   net: predicted within-net relative spread (max-min)/|mean| < 1e-3 for
   `borderline_frac_overall`, and the integer counts `fold_on_total` /
   `fold_kink_total` predicted IDENTICAL across all 16 rotations of a net
   (spread exactly 0), because they are threshold counts over alphas that agree
   to ~1e-7 relative.
3. Pooled within-net-ranked |rho| < 0.40 for all three; with exact ties the
   ranked statistic is degenerate and rho is undefined-or-~0.

The honest prior in the mining record was "probably fails, ~25% [success]". My
step-0 derivation lowers that to ~0: the mined proxy is not weakly informative,
it is *structurally constant* within a net.

## 5. Two-signal verification plan (required for ANY verdict, pass or kill)

- S1 (independent recomputation): the closed-form invariance argument of §2,
  checked numerically on all 48 rotations (column-norm identity).
- S2 (measured degeneracy): the 48 realized diagnostic triples; report the
  within-net min/max/spread of each diagnostic directly, not only the rho.
- S3 (archive anchor, independent of the proxy): re-derive P2's own bitwise
  check -- rebuild `forward_frame_means` for net 101 / r = 0 from
  `he_weights(101)` + `haar_rotation(900000+101*1000+0)` and require BITWISE
  equality with `p2_partial_net101.npz["frame_means"][0]`. This proves the
  seed formula and the archive index mapping this harness relies on.
- S4 (statistic cross-check): every Spearman computed two ways (Pearson on
  average ranks, and the classic 1 - 6*sum d^2 / (n(n^2-1)) formula) and
  asserted equal to 1e-10 on tie-free inputs.
- S5 (null calibration): 10,000 within-net random permutations of the archived
  MSE vector to get the null distribution of the pooled within-net-ranked rho,
  so the measured value is reported against its own null, not against intuition.
- S6 (determinism): one diagonal pass repeated and asserted bitwise identical.

## 6. Cost / envelope

Step 0: 48 QR + matmul at 256x256 -- seconds.
Step 1: 48 x 32 diagonal-pass layers -- seconds.
S3: one 64,512 x 256 x 32-layer forward -- order 1.4e11 FLOPs, minutes.
Total well inside the ~90-minute envelope. No scale-down anticipated.

## 7. Firewall

Writes confined to `corpus/whestbench/experiments/gm_p2b_proxy/`. Frozen v3
imported read-only (`sys.dont_write_bytecode = True`), never edited, never
subclassed-and-mutated. Synthetic He nets only. Archived committed artifacts
read-only. No m245_*/M243/M244/tasks/journal-m245* access. No git, no network,
no submissions, no scorer/holdout/private reads.
