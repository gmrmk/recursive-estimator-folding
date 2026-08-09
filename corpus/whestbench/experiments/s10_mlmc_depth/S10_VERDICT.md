# S10 -- MLMC over depth: increment-variance verdict

**ledger id:** `s10_mlmc_depth_increment_variance`
**date:** 2026-08-09
**verdict:** **DEAD.** Closed-form MLMC-over-depth gain = **0.056x** (geomean
over 3 nets), far below the predeclared 1.1x kill line. The depth-fidelity
family is fully dead: a depth telescope does not beat single-level sampling
of the full net for E[f_L].

## Gate outcome (predeclared)
- gain >= 1.3x -> full-arm proposal
- gain < 1.1x -> depth-fidelity family fully dead   <-- **THIS**
- 1.1-1.3x -> inconclusive

Aggregate MLMC gain **0.0561x** (per net 101/202/303 = 0.0429 / 0.0693 /
0.0593). Not merely below the line -- MLMC is ~18x *worse* than the champion.

## Choices / notes (no gate or arm deviations)
- **Scalar target.** `g_l(u)` = neuron-average of the post-ReLU activation
  after the first `l` weight matrices, starting from direction `u`. The first
  matmul carries the per-net Haar rotation (`first_eff = rotation.T @ W0`) and
  antipodal doubling happens right after it -- both exactly as the champion's
  `antipodal_forward_mean`. `g_32(u)` is therefore the neuron-mean of the
  layer-32 output, and `E_u[g_32]` **is** the champion target `E[f_L]`
  (final-layer neuron-mean). **No target gap** -- the telescope estimates the
  champion's quantity exactly, not a surrogate.
- **Limitation.** Per-draw variances are the *empirical* variance of `g` across
  the structured, antipodally-doubled Kerdock design (64,512 points/net; the
  full design, not the optional 16,384 subsample). For a fixed-radius
  well-spread design this second moment estimates the population `Var_u` under
  the intended sphere ensemble; confirmed by the iid cross-check below.
- **FLOP model.** One layer-matmul = `WIDTH^2 = 65,536` MACs per direction
  (ReLU + neuron-mean are O(WIDTH), negligible). `cost(g_l) = l`. Increment
  `Y_l = g_{l+1}-g_l` costs `l+1` (one forward to depth `l+1`; `g_l` is the
  byproduct at depth `l`). Base level `E[g_1]` costs 1. Single-level `E[g_32]`
  costs `c_32 = 32`. The constant `WIDTH^2` cancels in every ratio.
- The MLMC allocation includes the base level `E[g_1]` (cost 1), required for
  the telescope `E[g_32] = E[g_1] + sum_{l=1}^{31} E[g_{l+1}-g_l]` to be
  unbiased. Both MLMC and single-level are exactly unbiased for `E[g_32]`
  (finite ladder, no truncation bias).

## Why it dies: the increments do not decouple
The whole premise of MLMC is that the *coupled* increment
`g_{l+1}(u) - g_l(u)` (common `u`) has variance that collapses with depth, so
the expensive deep levels are cheap-variance. Measured, it does not:

- `V_full = Var_u[g_32]` ~ 8.0e-3 / 1.6e-2 / 1.1e-2 (nets 101/202/303).
- `V_1 = Var_u[g_2-g_1]` ~ 2.7e-3 for all three -- already a *third* of
  `V_full`, and it barely shrinks with depth.
- The full-range coupled correction `Var_u[g_32 - g_1]` ~ 7.76e-3 (net 101) is
  **nearly equal to `V_full` = 7.9e-3**: deep and shallow neuron-means are
  almost uncorrelated, so telescoping buys essentially nothing.

Mechanistically: a He-init ReLU layer preserves activation scale but is close
to an independent nonlinear re-mixing of the neuron-mean, so each layer injects
fresh variance into `g_l` rather than refining a converging quantity.

### V_l decay fit vs the 0.87 law
Geometric fit `V_l ~ A*rho^l` (l=1..31), mean over nets:
- **variance decay rho = 0.925** (per-net 0.920 / 0.927 / 0.929).
- **mean-defect decay rho = 1.017** -- the increment *means*
  `E[g_{l+1}-g_l]` do **not** decay at all (they wander ~+/-0.01-0.08); the
  truncated net is a persistently biased estimate of the full net whose bias
  per layer does not vanish.

Neither reproduces the prior brief's **0.87/layer** "defect decay." The
variance decays *slower* than 0.87 (0.925), and the mean defect is flat (~1.0).

**Sensitivity (net-101 anchors, `V_1`,`V_base`,`V_full`):** even if `V_l`
followed the prior's optimistic 0.87/layer law exactly, the closed-form MLMC
gain would be only **0.050x**. The break-even decay for a 1.3x gain is
**rho ≈ 0.53** -- the increment variance would have to *halve every layer*.
Reality is 0.925. The nomination fails on its own assumed number, by a wide
margin.

## Gain computation (closed form, matched billed FLOPs)
Levels: base `(V_0=Var[g_1], c_0=1)` and `l=1..31 (V_l=Var[g_{l+1}-g_l],
c_l=l+1)`.
- MLMC work-normalized variance `W_mlmc = (sum_levels sqrt(V_l c_l))^2`.
- Single-level `W_single = V_full * c_32 = V_full * 32`.
- **gain = W_single / W_mlmc = 0.0561x** (geomean; >1 would mean MLMC wins).

The many intermediate levels, each with slowly-decaying variance and cost up to
32, make `sum sqrt(V_l c_l)` large. Adding levels *hurts*: this is why the full
ladder (0.056x) is far worse than the two-level estimate below.

### Rhee-Glynn randomized single-term cross-check
Unbiased single-term estimator; work-normalized variance uses level *second
moments* `W_rg = (sum_levels sqrt(E[Delta_l^2] c_l))^2`.
- **gain_rg = 0.0104x** (geomean). Even more emphatically dead, as expected
  (second moments >= variances, and the non-decaying increment means inflate
  `E[Delta_l^2]`). Same direction, same verdict: no depth telescope helps.

### Reproduction of the prior fleets' two-level MFMC (~1.0x)
From the same ladder, a two-level MFMC (base `g_1` cost 1 + full correction
`g_32-g_1` cost 32) gives gain **0.835 / 0.950 / 0.920** (geomean **0.90x**),
matching the prior brief's "~1.0x (dead)." This independently validates the
machinery and **decisively resolves the two-brief disagreement**: the full MLMC
ladder is not "possibly live" -- it is ~16x worse than the already-dead
two-level estimate, because slow variance decay makes every added level a net
cost.

## Two-signal verification
1. **Independent iid-Gaussian resample** (radius mean_chi, own seeds) of
   `V_full` and `V_1` agrees with the Kerdock-design values within **1.3%**:
   V_full ratios 1.006 / 1.009 / 0.989; V_1 ratios 1.013 / 1.007 / 1.010.
   The variances are population properties, not a design artifact.
2. **Cross-estimator agreement**: closed-form MLMC (0.056x), Rhee-Glynn
   (0.010x), and reproduced two-level MFMC (0.90x) all place the depth
   telescope below single-level, with the full ladder worst.

## Files
- `run_s10.py` -- harness (imports frozen n8a constructor/directions read-only).
- `s10_results.json` -- per-net V_l, increment/level means, costs, allocation,
  gains, decay fits, iid cross-check.
- `S10_VERDICT.md` -- this file.
