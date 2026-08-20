# M-MUB129-R — predeclaration: higher-power replication of M-MUB129

**Author:** opus-5 (replication agent). **Written:** 2026-08-11, before any
measurement code for this experiment existed.
**Replicates:** M-MUB129, predeclared at commit `be3eb44`, result committed at
`97f6ec8` (`corpus/whestbench/experiments/mub129_completion/`).
**Lane:** L7 generation (design-side). No kill is revived by this.

## 0. This is an informed replication, and says so

This is **not** a blind run. The original result is already on disk and is
restated here in full, because pretending not to have seen it would be the
dishonest option:

- geomean variance ratio `V129/V126` = **0.915252**
- geomean **score** ratio (variance ratio x 129/126) = **0.937044**
- per-network score ratios, n = 3: **0.9941 / 0.8790 / 0.9415**
- verdict **SURVIVES_K1**, on 3 networks x 16 rotations.

The weakness being addressed is entirely one of power, not of direction:
network 0 cleared the bar by 0.6%, and n = 3 cannot support an interval. The
original's clause K3 forbids changing `R`, the network count, or the seeds
after seeing the value, so the original experiment is **sealed and will not be
edited**. This is a separate experiment with its own seeds and its own gate.

Because the point estimate is known in advance, the discipline that matters
here is that **the bar does not move**. The K1 bar below is bit-identical to
the original's, and the interval kill is fixed before the interval exists.

## 1. Mechanism under test (unchanged from the original)

The deployed GUARDS design uses 126 phased-Hadamard frames
(`kerdock_v3_estimator.py:47,51,52`), antipodally doubled to 64,512 points:
1,280 points below the Delsarte-Goethals-Seidel floor of 65,792 for an
antipodal 4-design in `S^255`. Completing to 129 frames (66,048 points) clears
the floor by 256 and makes the design exact at degree 4, hence an exact
5-design. The 129th frame is the standard basis; all 128 phase frames already
ship in the frozen archive `experiments/v31_guards/package_source/
kerdock_phases.npz`.

**Hypothesis under test:** the variance removed by completing 126 -> 129 frames
exceeds the 2.381% compute increase, and does so by a margin whose 95% interval
excludes break-even.

## 2. Why this needs no truth, scorer, or holdout read

For a fixed equal-weight point set randomly rotated by Haar `R`,

```
E_R[(1/N) sum_i f(R u_i)] = (1/N) sum_i E_R[f(R u_i)] = integral f
```

exactly, for every point set. The estimator is therefore **exactly unbiased**,
so `MSE = Var_R` identically, and a variance comparison over rotation draws is
a complete comparison of estimator quality. Everything below runs on locally
generated He-initialised development networks.

**No truth read, no scorer read, no holdout, no challenge network, no
submission, no leaderboard contact.** This clause is non-negotiable: if any
step of the execution would require reading truth, the run stops and the
situation is reported instead of being worked around.

## 3. Design of the experiment — every count fixed here, before any code

| quantity | value, fixed now |
|---|---|
| networks `K` | **16** |
| rotations per network `R` | **24** |
| network seeds | `NET_SEED_BASE + k`, **`NET_SEED_BASE = 31415926`**, `k = 0..15` |
| rotation seeds | `ROT_SEED_BASE + 1000*k + r`, **`ROT_SEED_BASE = 27182818`**, `r = 0..23` |
| bootstrap seed | **`BOOT_SEED = 16180339`** |
| bootstrap resamples `B` | **10,000** |
| interval percentiles | **2.5 / 97.5** |
| dimension / depth | `D = 256`, `DEPTH = 32` (unchanged) |
| deployed slice | `phases[2:128]` -> 126 frames (unchanged) |
| cost ratio | `129/126 = 1.0238095...` (unchanged, conservative) |

The original used `NET_SEED_BASE = 20260812`, `ROT_SEED_BASE = 76543210`. The
seed bases above are deliberately different and disjoint in range, so the 16
networks and 384 rotations here are **fresh draws**, not a superset of the
original's three networks.

Both estimators come from **one shared forward pass**: all 129 frames are
evaluated once per (network, rotation), and

- `Q_126` = mean over frames `s = 2..127` (the deployed slice),
- `Q_129` = mean over all 129 frames (standard basis + `s = 0..127`),

are formed from the same per-frame means, antipodally doubled in both cases.
Paired on identical networks and identical rotations, which is the
maximum-power comparison available.

Primary per-network statistic, on the final-layer (depth-32) mean vector:

```
V126_k = mean_over_neurons Var_R[ Q_126 ]     (ddof = 1, over the 24 rotations)
V129_k = mean_over_neurons Var_R[ Q_129 ]
ratio_k = V129_k / V126_k
score_k = ratio_k * 129/126
```

Point estimate: `geomean_score = exp(mean_k log score_k)` over all 16 networks.

**Interval, predeclared in full now.** Paired bootstrap over **networks** (the
network is the resampling unit; rotations are not resampled, they are the
within-unit variance estimator). Draw `B = 10,000` resamples of size 16 with
replacement from the 16 values `log score_k`, using
`numpy.random.default_rng(16180339)`; the bootstrap statistic is
`exp(mean of the resampled logs)`; the interval is the **2.5th and 97.5th
percentiles** of those 10,000 values (`numpy.percentile`, default linear
interpolation). Because the pairing is inside each network's log ratio, this
is a paired interval.

The run may be **checkpointed per network** and resumed (wall-clock limits of
the execution harness). Resumption recomputes nothing already checkpointed and
cannot change a seed or a count, since every seed is a pure function of `k` and
`r` fixed in this table.

## 4. Kill conditions, fixed before any value exists

**K1 (primary, bit-identical to the original's bar).** KILL the completion if

```
geomean_score = (geomean_k V129_k/V126_k) * (129/126) >= 1.0
```

i.e. KILL unless the geomean variance ratio is below
**`126/129 = 0.9767441860465116`** — unless the completion removes more than
**2.3256%** of the rotation-draw variance. The bar is the cost arithmetic and
nothing else. It does not move for any reason.

**K1b (secondary, the interval the original could not support).** KILL if

```
upper end (97.5th percentile) of the 95% bootstrap interval on
geomean_score  >=  1.0
```

A point estimate below 1.0 whose interval touches break-even is **not** a
survival at this power level. Both K1 and K1b must clear for the verdict to be
`SURVIVES_K1_AND_INTERVAL`. If K1 clears and K1b fires, the verdict is
`KILLED_K1B_INTERVAL_TOUCHES_BREAKEVEN` and it is reported as a kill.

**K2 (structural precondition, read before K1).** KILL if any of:
(a) the frozen archive holds fewer than 128 phase rows;
(b) the 129 candidate frames are not pairwise mutually unbiased at exactly
`|<x,y>| = 1/16` across frames;
(c) the 66,048-point antipodal set fails the degree-4 moment identity
`sum_y <x,y>^4 = 3N/(d(d+2)) = 3` in exact rational arithmetic.

**K3 (protocol).** KILL with zero credit on: any change to the K1 bar, the K1b
rule, `K`, `R`, the seed bases, the bootstrap count, or the percentiles after
seeing any variance number; any truth, scorer, or holdout read; any use of a
challenge network; any edit to the sealed `mub129_completion/` experiment.

## 5. Reporting obligations, fixed now

- **All 16 per-network ratios are reported raw** — `V126_k`, `V129_k`,
  `ratio_k`, `score_k` for every `k`, in `RESULTS.json` and in the final
  report. Reporting only a summary is itself a protocol violation. The spread,
  including any network that fails to clear 1.0 individually, is reported
  whatever it looks like.
- The result is compared to the original's point estimate 0.937044 by stating
  whether that value lies inside this run's 95% interval. This comparison has
  **no gate authority** — it is a consistency observation, not a test.

## 6. Cross-checks, predeclared as verification and not as gates

- **C1 (arithmetic).** Each `V126_k`, `V129_k` is recomputed by an independent
  hand-written sum-of-squared-deviations formula and must agree with the
  primary `numpy.var(ddof=1)` path to within `1e-10` relative. Any
  disagreement is reported.
- **C2 (bitwise repeat).** After the main loop, network 0 / rotation 0 is
  recomputed from freshly constructed weights and a freshly constructed
  rotation at the same seeds; the resulting 129-frame mean vector must match
  the value cached during the main loop **bitwise**. Any mismatch is reported.
- **C3 (independent structural check, separate code path).** In a standalone
  script sharing no code with the runner, the exact Gegenbauer design defect

  ```
  A_l = (1/N) * [ 2*P_l(1) + 510*P_l(0) + 512*(m-1)*P_l(1/16) ],   N = 512m
  ```

  with `P_l` the degree-`l` Gegenbauer polynomial for `S^255` normalised to
  `P_l(1) = 1`, is computed in `fractions.Fraction` for `l = 2, 4, 6` at
  `m = 126` and `m = 129`. Expected: degree 4 exactly zero at `m = 129` and
  nonzero at `m = 126`. The original run reported `A_4(126) = 7.351e-07` and
  `A_4(129) = 0` exactly. **If this run produces anything different, that is a
  finding and is reported loudly rather than reconciled.**

## 7. What each outcome licenses

- **K1 or K1b fires:** the 129-frame completion is dead as a score lever at
  this power. The design-axis closure result (DGS/Moller at degrees 4 and 6)
  is a theorem about what cannot be done and is untouched by either outcome.
- **Both clear:** licenses *writing* a source-level candidate and its own cost
  predeclaration. It does **not** authorise a submission, a selection change, a
  package, or any hosted run. Those need Jonah's explicit word.

GUARDS remains the incumbent throughout. Nothing here touches deployed bytes.
