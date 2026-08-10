# VERDICT -- gm_p2b_proxy (revival of `p2b_weights_only_rotation_proxy`)

**KILL_CONFIRMED at step 0, confirmed again at step 1.** The original ledger
record stands and is strengthened: the mined "deep zero-sample diagonal-pass"
proxy class does not merely correlate weakly with per-rotation MSE, it is
**exactly constant across rotations within a net** and therefore carries zero
within-net selection information by construction.

## DEVIATIONS (recorded loudly, top of file)

1. **S3 anchor initially non-bitwise; cause diagnosed and fixed, not absorbed.**
   The first run of `s3_archive_anchor.py` reproduced the archived P2 forward for
   net 101 / r = 0 to `max_abs_diff = 3.6833807826042175e-07` (r = 15:
   `4.0442682802677155e-07`) but **not** bitwise, against a predeclared bitwise
   requirement. Hypothesis tested directly: `run_p2_rotation_selection.py` sets
   `OMP_NUM_THREADS / OPENBLAS_NUM_THREADS / MKL_NUM_THREADS = 6` before
   importing numpy; my first run did not, so the f32 BLAS reduction order
   differed. Re-run with those three lines added verbatim:
   `bitwise_equal_to_archive = true`, `max_abs_diff = 0.0` for **both** r = 0 and
   r = 15. The three lines are now in the script with a comment naming the
   deviation. No gate number was touched.
2. **Step 1 was run even though step 0 killed.** Predeclaration section 2 allowed
   this explicitly and labelled it CONFIRMATORY. It is not a retune: the gate
   numbers (|rho| >= 0.40, per-net sign consistency) are P2b's own and unchanged,
   and step 1 was reported as it came out.
3. `rotated_alphas()` and `weight_diagnostics()` are reproduced verbatim in
   `step1_deep_diag_proxy.py` rather than imported, because `run_m185_g0.py` is a
   checkpointed CLI harness that is not importable standalone. The bodies are
   unchanged and call the same frozen v3 functions.
4. Scope was not enlarged. Nets 101/202/303, r = 0..15, seeds
   900000 + net*1000 + r, exactly as mined. No truth file was read; the target
   vector is the committed `p2_results.json` archive.

## STEP 0 -- arithmetic gate (the decisive result)

Closed form, derived before running anything (PREDECLARATION section 2):
`_diagonal_gaussian_pass` starts at `mu = 0`, `var = 1`, so at layer 0
`mu_pre = 0 @ (R.T W1) = 0` and
`var_pre[j] = ||(R.T W1)[:,j]||^2 = ||W1[:,j]||^2` for any orthogonal `R`.
v3 rotates the first layer only. Hence the whole `(mu, var)` trajectory, every
`alpha`, and every statistic in `weight_diagnostics()` is **rotation-invariant in
exact arithmetic**. Only float32 rounding can survive.

Measured over all 48 rotations (`step0_results.json`):

| quantity | value | predeclared gate |
|---|---|---|
| max relative deviation of layer-0 `var_pre`, rotated vs unrotated | **4.558046e-07** (net 202, r = 3) | `< 1e-4` -> KILL; `>= 1e-2` -> revival survives |
| max `|R.T R - I|` over the 48 frozen Haar rotations | 2.073e-08 | context |

`4.558046e-07 < 1e-4` -> **STEP 0 KILLS.** The revival's premise is false.

## STEP 1 -- the cheapest falsifier exactly as mined (confirmatory)

48 calls to `rotated_alphas()` + `weight_diagnostics()`, nets 101/202/303,
r = 0..15, seeds 900000 + net*1000 + r; y = `p2_results.json ->
q1_oracle_headroom.per_net[net].mse_per_rotation`. Wall: 18.9 s.

### Measured within-net degeneracy (S2) -- distinct values out of 16 rotations

| diagnostic | net 101 | net 202 | net 303 |
|---|---|---|---|
| `borderline_frac_overall` | **1** (0.09835379464285714) | **1** (0.09249441964285714) | **1** (0.08551897321428571) |
| `fold_on_total` | **1** (224) | **1** (242) | **1** (241) |
| `fold_kink_total` | **1** (247) | **1** (260) | **1** (247) |

`abs_spread = 0.0` and `rel_spread = 0.0` in all nine cells.

### The mined statistic vs the unchanged P2b gate

| diagnostic | per-net Spearman (101, 202, 303) | pooled within-net-ranked rho | sign consistent | gate \|rho\| >= 0.40 |
|---|---|---|---|---|
| `borderline_frac_overall` | 0.0, 0.0, 0.0 | **+0.0000** | False | **FAIL** |
| `fold_on_total` | 0.0, 0.0, 0.0 | **+0.0000** | False | **FAIL** |
| `fold_kink_total` | 0.0, 0.0, 0.0 | **+0.0000** | False | **FAIL** |

For comparison, the original P2b's best was proxy B (deg-6) at pooled
rho = -0.1656862745098039. The deeper class scores **exactly 0**, i.e. strictly
worse, not better.

### Permutation null (S5), 10,000 within-net permutations, seed 20260810

`null_mean = 0.0`, `null_sd = 0.0`, `two_sided_p = 1.0`,
`frac_null_draws_reaching_gate = 0.0`. Because x is constant within each net,
the pooled statistic is identically zero **against every possible target
vector**. The proxy cannot reach the gate for any y, not just for this y.

### Per-layer alpha spread across the 16 rotations (S2-extended)

`layer0_alpha_all_zero = true` for all three nets (alpha[0] is exactly 0 for
every rotation, as derived). Max absolute alpha spread over rotations, any
layer: net 101 `6.528751428369617e-09`, net 202 `7.055529493982249e-09`,
net 303 `7.941793001009500e-09` (max relative 4.723e-05, 5.860e-06, 1.070e-06 --
all on near-zero alphas). The entire rotation signal available to this proxy
class is ~1e-9 absolute in alpha, which no threshold count resolves.

## Two-signal verification

- **S1** closed-form orthogonal-invariance argument, checked numerically on all
  48 rotations (step 0, 4.558046e-07).
- **S2** independent measurement of realized degeneracy: 1 distinct value out of
  16, all nine (diagnostic, net) cells.
- **S3** archive anchor: rebuilt P2 forward, net 101 r = 0 and r = 15, **bitwise
  equal** to `p2_partial_net101.npz["frame_means"][r]` (`max_abs_diff = 0.0`),
  while the wrong-index control differs by `0.09482479421421885` -- the seed
  formula and archive index mapping are confirmed, not assumed.
- **S4** Spearman computed two ways; with x fully tied the d^2 formula is
  reported as a diagnostic only and the tie flag `x_has_ties = true` is recorded.
- **S5** permutation null (above).
- **S6** determinism: repeated diagonal pass, alpha layer 31 bitwise identical
  (`true`). Additional repeat under a different BLAS thread count reproduced
  `within_net_degeneracy_S2`, `statistics` and `permutation_null_S5` byte-for-byte
  identical JSON; only the float64 fingerprint fields `alpha_l31_mean` /
  `alpha_l31_sum_abs` moved, by 1.936e-15 / 5.653e-16 relative.

## What this settles for the writeup

- The mining record's **cost** claim is confirmed and can be quoted: the diagonal
  pass costs 4.194304e+07 FLOPs per candidate rotation, 3.35544320e+08 for k = 8,
  = **0.1234% of B = 2.72e11**, versus P2's pilot at **33.427% of B**. A 271x
  cheaper selection stage does exist.
- It buys nothing. The statistic it computes is constant within a net, so the
  61.6% oracle-of-8 headroom stays unharvested.
- The reason is sharper than "the deep diagnostics track output scale, which is
  constant within a net" (the mining record's own partial-correlation
  conjecture). The true reason is an exact invariance: a diagonal Gaussian pass
  from an isotropic input is blind to an orthogonal rotation of the first layer,
  at every depth. Any proxy built from `_diagonal_gaussian_pass` on the rotated
  net is provably a zero-information rotation selector -- no experiment needed to
  reject the next member of this family.
- The rotation family is now closed on a fourth class, and closed by proof rather
  than by a weak correlation: sample statistics (pilot rho -0.089, cost 33.4%B),
  full frame-dispersion (rho -0.340, killed on economics), first-layer weights-only
  (best |rho| 0.166), and deep zero-sample diagonal-pass (rho exactly 0, by
  invariance).

## Files

- `PREDECLARATION.md` (written before any code ran)
- `step0_invariance_gate.py`, `step0_results.json`
- `step1_deep_diag_proxy.py`, `step1_results.json`
- `s3_archive_anchor.py`, `s3_anchor_results.json`
- `results.json` (machine-readable verdict + decisive numbers)
