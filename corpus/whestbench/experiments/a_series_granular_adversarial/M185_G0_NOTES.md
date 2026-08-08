# M185 G0 notes -- tail-mechanism hunt (A2), 2026-08-08

## VERDICT

**M185 KILLED, both legs.**

- **Claim 1 (a-priori weight-derived tail flag): KILLED at stage 1.** The
  local tail is real -- floor-corrected per-net MSE spreads **35.3x** (raw
  15.5x) over 80 nets -- but no governing diagnostic reaches |spearman| >=
  0.3 against MSE: pruned_frac +0.243, diag_proxy_l28 +0.264, fold_dead
  +0.167, fold_on +0.285.
- **Claim 2 (pruning/fold-misclassification mechanism): KILLED at stage 2.**
  Relaxing (dead=-3, on=4) or wholly removing (dead=-99) dead-pruning
  improves the 5 worst nets by only **7.1% / 10.1%** (mean-MSE basis;
  paired per-rep 95% CIs top out at +7.0% / +10.5%) against a predeclared
  30% bar, and the median nets move a statistically indistinguishable
  +3.7% / +4.8%. The intervention effect is small and UNIFORM, not
  tail-specific.

**What the tail actually is:** rotation-draw sampling variance, not net
identity. The worst/median group separation collapses from **3.79x on the
stage-1 single draw to 1.12x at R=6 replicates**; within a single net the
six same-net rep MSEs spread 2.3-8.7x; and a median-selected net (1000)
turned out WORST of all ten at R=6 (6.5e-7). The A2 question STRUCTURAL vs
STATISTICAL resolves to **STATISTICAL**: the hosted 11x spread (per-net MC
difficulty constant, A1) is dominated by per-draw variance of the
estimator's own Haar-rotation randomization, with only a small persistent
net-level component (~3x at R=6 across these 10) and a small uniform
pruning-bias component (~4-10%).

## Deviations (loud)

1. **Truth-floor premise was wrong; truth raised to 600k.** The dispatch
   assumed a ~7e-8 floor at 300k samples; the MEASURED floor on net 1000
   was 3.8e-7 (final-layer per-sample variance ~0.11). Because the first
   net ran in ~16s vs the ~26.5s budget, stage-1 truth was raised to 600k
   (floor ~1.9e-7, mse_corr noise ~+/-1.7e-8) BEFORE the main run; net
   1000 was re-measured at 600k. Gates, seeds, and logic unchanged.
2. **Gate-ambiguity resolution (declared before any stage-2 compute).** The
   dispatch kills on "no diagnostic correlates" but gates stage 2 on "only
   if stage 1 finds a tail"; a 35x tail was found while the correlation
   gate failed. Resolved toward MORE falsification pressure: stage 2 ran
   anyway as the direct interventional test (its own gate untouched);
   claim 1 stays killed regardless of the stage-2 outcome. The correlation
   screen operates on single-draw MSEs and is attenuated by the (large,
   see above) draw noise; the interventional gate is immune to that
   attenuation, and it also killed.
3. **Rescue counts not recorded.** The frozen sources do not expose them;
   capturing them would have required monkeypatching the frozen module
   namespace, declined under the subclass-only firewall. Structural fold
   partitions (from the bitwise-reproduced in-predict alphas) and
   threshold-move counts were recorded instead.
4. **Stage-2 replicates R=6 per arm** (rotation seeds 900000+net*1000+r,
   r=0..5, IDENTICAL across arms -> paired comparison; same n_base
   everywhere). The dispatch said "same rotation seeds, same n" without
   fixing R.
5. **No trim needed:** all 80 predeclared nets ran (~27s/net); the
   predeclared auto-trim rule never fired.
6. **Chunked execution:** checkpoint/resume across shell invocations
   (10-min shell cap); all computation foreground in-session; every
   per-net result printed live.
7. all_layer_mse is floor-uncorrected (exploratory only); truth sumsq was
   accumulated at layers 28 and 31 only (the two floors used).
8. api_version="2.0" per the dispatch (n8c had used "synthetic"); the
   frozen v3 ignores the field. Self-checks: same-seed repeat bitwise
   identical; external diag pass reproduces output row 28 bitwise.

## Stage 1 -- 80 nets (seeds 1000..1079), one v3 run each, 600k MC truth

- spread (floor-corrected): **35.3x** (raw 15.5x); spread gate (>=4x) PASSES
- spearman vs floor-corrected MSE (governing marked):

| diagnostic | rho | status |
|---|---|---|
| pruned_frac_overall | +0.243 | **governing** |
| diag_proxy_l28 | +0.264 | **governing** |
| fold_dead_total | +0.167 | **governing** |
| fold_on_total | +0.284 | **governing** |
| fold_kink_total | -0.257 | exploratory |
| borderline_frac_overall | -0.424 | exploratory |
| relax_moves_total | -0.262 | exploratory |
| all_layer_mse | +0.251 | exploratory |
| billed_flops | -0.290 | exploratory |

- correlation gate: FAILS (all governing |rho| < 0.3). Directionally the
  hosted A1 signature DOES reproduce (worse nets: more pruning +0.24,
  fewer billed FLOPs -0.29, worse analytic all-layer MSE +0.25) but below
  bar.
- exploratory borderline_frac at -0.42 is the largest |rho| and is
  ANTI-mechanism (more alpha mass near the dead cut -> LOWER MSE); it was
  not a predeclared governing diagnostic and cannot save the hypothesis.

### Per-net table (sorted by floor-corrected MSE, worst first)

| seed | mse_corr | mse_raw | pruned_frac | proxy28 | fold d/k/o | billed FLOPs |
|---|---|---|---|---|---|---|
| 1054 | 8.155e-07 | 8.993e-07 | 0.2511 | 1.20e-03 | 290/220/258 | 1.626e+11 |
| 1069 | 8.012e-07 | 8.924e-07 | 0.2321 | 6.15e-04 | 285/234/249 | 1.727e+11 |
| 1044 | 7.697e-07 | 8.469e-07 | 0.2160 | 6.41e-04 | 270/270/228 | 1.744e+11 |
| 1063 | 6.645e-07 | 8.156e-07 | 0.2393 | 1.41e-03 | 285/205/278 | 1.697e+11 |
| 1001 | 6.547e-07 | 7.677e-07 | 0.2515 | 8.14e-04 | 281/249/238 | 1.610e+11 |
| 1042 | 5.741e-07 | 6.890e-07 | 0.2313 | 9.60e-04 | 304/196/268 | 1.697e+11 |
| 1008 | 5.687e-07 | 6.526e-07 | 0.2681 | 6.22e-04 | 307/214/247 | 1.525e+11 |
| 1049 | 5.529e-07 | 6.578e-07 | 0.2407 | 1.69e-03 | 281/214/273 | 1.631e+11 |
| 1053 | 5.309e-07 | 6.352e-07 | 0.2398 | 5.59e-04 | 258/258/252 | 1.682e+11 |
| 1035 | 5.112e-07 | 5.665e-07 | 0.2540 | 5.61e-04 | 278/252/238 | 1.595e+11 |
| 1077 | 4.547e-07 | 6.414e-07 | 0.2617 | 1.36e-03 | 297/232/239 | 1.580e+11 |
| 1022 | 4.525e-07 | 6.424e-07 | 0.2743 | 2.32e-03 | 297/211/260 | 1.528e+11 |
| 1011 | 4.474e-07 | 5.853e-07 | 0.2462 | 8.04e-04 | 297/209/262 | 1.657e+11 |
| 1048 | 4.372e-07 | 5.385e-07 | 0.2423 | 9.63e-04 | 256/298/214 | 1.727e+11 |
| 1004 | 4.333e-07 | 6.155e-07 | 0.2351 | 1.92e-03 | 278/211/279 | 1.688e+11 |
| 1040 | 3.949e-07 | 4.601e-07 | 0.2621 | 6.15e-04 | 300/239/229 | 1.555e+11 |
| 1067 | 3.889e-07 | 4.781e-07 | 0.2467 | 8.69e-04 | 265/290/213 | 1.690e+11 |
| 1047 | 3.759e-07 | 4.751e-07 | 0.2455 | 2.10e-03 | 258/260/250 | 1.644e+11 |
| 1070 | 3.713e-07 | 4.712e-07 | 0.2395 | 1.55e-03 | 252/322/194 | 1.744e+11 |
| 1076 | 3.710e-07 | 4.723e-07 | 0.2405 | 1.72e-03 | 253/316/199 | 1.740e+11 |
| 1019 | 3.590e-07 | 4.164e-07 | 0.2326 | 1.13e-03 | 286/261/221 | 1.707e+11 |
| 1034 | 3.382e-07 | 4.013e-07 | 0.2081 | 9.04e-04 | 265/274/229 | 1.796e+11 |
| 1013 | 3.319e-07 | 4.116e-07 | 0.2218 | 5.36e-04 | 282/229/257 | 1.761e+11 |
| 1062 | 2.834e-07 | 3.453e-07 | 0.2388 | 3.78e-04 | 246/298/224 | 1.741e+11 |
| 1029 | 2.809e-07 | 3.751e-07 | 0.2168 | 6.63e-04 | 259/297/212 | 1.798e+11 |
| 1003 | 2.745e-07 | 3.947e-07 | 0.2356 | 7.29e-04 | 277/227/264 | 1.670e+11 |
| 1002 | 2.724e-07 | 4.016e-07 | 0.2359 | 1.22e-03 | 289/253/226 | 1.724e+11 |
| 1021 | 2.674e-07 | 3.177e-07 | 0.1897 | 4.83e-04 | 219/401/148 | 1.987e+11 |
| 1039 | 2.610e-07 | 3.058e-07 | 0.1955 | 1.15e-03 | 258/324/186 | 1.906e+11 |
| 1032 | 2.482e-07 | 3.207e-07 | 0.2158 | 5.04e-04 | 256/286/226 | 1.799e+11 |
| 1079 | 2.415e-07 | 4.022e-07 | 0.2598 | 2.03e-03 | 277/246/245 | 1.583e+11 |
| 1056 | 2.296e-07 | 2.835e-07 | 0.2261 | 9.52e-04 | 306/255/207 | 1.741e+11 |
| 1030 | 2.262e-07 | 3.385e-07 | 0.2359 | 6.66e-04 | 269/248/251 | 1.721e+11 |
| 1005 | 2.242e-07 | 3.042e-07 | 0.2381 | 1.34e-03 | 245/295/228 | 1.701e+11 |
| 1078 | 2.234e-07 | 3.049e-07 | 0.2372 | 9.39e-04 | 257/287/224 | 1.695e+11 |
| 1020 | 2.132e-07 | 2.592e-07 | 0.2489 | 8.11e-04 | 250/347/171 | 1.707e+11 |
| 1016 | 2.015e-07 | 2.455e-07 | 0.2319 | 3.35e-04 | 250/309/209 | 1.796e+11 |
| 1058 | 1.981e-07 | 2.778e-07 | 0.2261 | 7.20e-04 | 274/257/237 | 1.748e+11 |
| 1031 | 1.967e-07 | 3.039e-07 | 0.2444 | 1.12e-03 | 285/256/227 | 1.663e+11 |
| 1045 | 1.949e-07 | 2.731e-07 | 0.2447 | 8.41e-04 | 272/263/233 | 1.645e+11 |
| 1075 | 1.943e-07 | 3.040e-07 | 0.2359 | 1.51e-03 | 273/289/206 | 1.719e+11 |
| 1000 | 1.936e-07 | 3.832e-07 | 0.2394 | 1.80e-03 | 300/237/231 | 1.669e+11 |
| 1071 | 1.903e-07 | 2.892e-07 | 0.2414 | 1.26e-03 | 269/259/240 | 1.725e+11 |
| 1046 | 1.838e-07 | 2.351e-07 | 0.2242 | 3.43e-04 | 246/305/217 | 1.778e+11 |
| 1061 | 1.770e-07 | 3.472e-07 | 0.2429 | 9.22e-04 | 289/212/267 | 1.683e+11 |
| 1027 | 1.709e-07 | 2.129e-07 | 0.2115 | 5.18e-04 | 266/327/175 | 1.859e+11 |
| 1074 | 1.707e-07 | 2.151e-07 | 0.2510 | 9.73e-04 | 277/281/210 | 1.716e+11 |
| 1017 | 1.615e-07 | 3.581e-07 | 0.2559 | 1.16e-03 | 313/180/275 | 1.533e+11 |
| 1066 | 1.576e-07 | 1.820e-07 | 0.2190 | 5.61e-04 | 229/375/164 | 1.828e+11 |
| 1038 | 1.552e-07 | 2.473e-07 | 0.2602 | 2.03e-03 | 310/195/263 | 1.532e+11 |
| 1024 | 1.433e-07 | 2.462e-07 | 0.2289 | 6.77e-04 | 272/239/257 | 1.752e+11 |
| 1072 | 1.421e-07 | 1.877e-07 | 0.2077 | 6.93e-04 | 210/398/160 | 1.938e+11 |
| 1043 | 1.381e-07 | 2.116e-07 | 0.2270 | 6.59e-04 | 259/279/230 | 1.728e+11 |
| 1009 | 1.289e-07 | 2.255e-07 | 0.2232 | 1.63e-03 | 258/290/220 | 1.774e+11 |
| 1006 | 1.285e-07 | 3.167e-07 | 0.2521 | 1.61e-03 | 289/181/298 | 1.627e+11 |
| 1036 | 1.210e-07 | 1.637e-07 | 0.2121 | 9.62e-04 | 289/302/177 | 1.874e+11 |
| 1065 | 1.209e-07 | 1.492e-07 | 0.2154 | 7.36e-04 | 254/332/182 | 1.846e+11 |
| 1033 | 1.125e-07 | 1.540e-07 | 0.2356 | 5.31e-04 | 276/283/209 | 1.755e+11 |
| 1068 | 1.124e-07 | 1.515e-07 | 0.2420 | 3.70e-04 | 272/264/232 | 1.702e+11 |
| 1041 | 1.081e-07 | 2.108e-07 | 0.2420 | 1.03e-03 | 284/248/236 | 1.731e+11 |
| 1055 | 1.079e-07 | 2.200e-07 | 0.2482 | 1.12e-03 | 288/224/256 | 1.623e+11 |
| 1037 | 1.032e-07 | 1.541e-07 | 0.2423 | 7.27e-04 | 273/287/208 | 1.687e+11 |
| 1057 | 1.010e-07 | 1.617e-07 | 0.2314 | 1.27e-03 | 262/309/197 | 1.764e+11 |
| 1073 | 1.009e-07 | 1.319e-07 | 0.2040 | 4.52e-04 | 234/378/156 | 1.935e+11 |
| 1025 | 1.003e-07 | 1.456e-07 | 0.2210 | 8.82e-04 | 320/249/199 | 1.764e+11 |
| 1051 | 9.992e-08 | 1.429e-07 | 0.2259 | 4.81e-04 | 275/281/212 | 1.780e+11 |
| 1028 | 9.306e-08 | 1.103e-07 | 0.2298 | 2.96e-04 | 219/405/144 | 1.834e+11 |
| 1015 | 8.302e-08 | 1.127e-07 | 0.2414 | 7.92e-04 | 262/286/220 | 1.688e+11 |
| 1007 | 8.279e-08 | 1.275e-07 | 0.2331 | 4.52e-04 | 271/272/225 | 1.750e+11 |
| 1023 | 8.017e-08 | 1.393e-07 | 0.2514 | 1.08e-03 | 275/268/225 | 1.589e+11 |
| 1012 | 7.713e-08 | 1.396e-07 | 0.2179 | 1.92e-03 | 299/216/253 | 1.692e+11 |
| 1050 | 7.520e-08 | 1.644e-07 | 0.2157 | 8.47e-04 | 247/302/219 | 1.874e+11 |
| 1064 | 6.751e-08 | 1.032e-07 | 0.2042 | 2.75e-04 | 266/283/219 | 1.865e+11 |
| 1014 | 6.679e-08 | 2.154e-07 | 0.2715 | 1.08e-03 | 298/197/273 | 1.519e+11 |
| 1060 | 6.219e-08 | 8.461e-08 | 0.2063 | 1.87e-04 | 257/316/195 | 1.861e+11 |
| 1010 | 6.086e-08 | 1.643e-07 | 0.2287 | 4.71e-04 | 262/237/269 | 1.726e+11 |
| 1018 | 5.937e-08 | 1.060e-07 | 0.2596 | 3.93e-04 | 286/235/247 | 1.625e+11 |
| 1059 | 4.866e-08 | 1.049e-07 | 0.2247 | 4.06e-04 | 241/316/211 | 1.758e+11 |
| 1052 | 3.616e-08 | 9.319e-08 | 0.2437 | 8.60e-04 | 275/243/250 | 1.677e+11 |
| 1026 | 2.308e-08 | 5.790e-08 | 0.2239 | 6.52e-04 | 270/307/191 | 1.766e+11 |

## Stage 2 -- interventional arms on 5 worst + 5 median nets, 1M MC truth

Arms (subclasses of the frozen v3; sources untouched): default (dead=-2,
on=3), relaxed (dead=-3, on=4), unpruned (dead=-99, on=3; removes
dead-pruning wholly, on-folding retained). R=6 paired rotation seeds.

### Per-net before/after (floor-corrected R=6 mean MSE)

| group | seed | stage-1 draw | default | relaxed | improv | unpruned | improv |
|---|---|---|---|---|---|---|---|
| worst | 1001 | 6.547e-07 | 3.556e-07 | 3.257e-07 | +8.4% | 3.139e-07 | +11.7% |
| worst | 1063 | 6.645e-07 | 5.316e-07 | 4.799e-07 | +9.7% | 4.491e-07 | +15.5% |
| worst | 1044 | 7.697e-07 | 4.427e-07 | 4.277e-07 | +3.4% | 4.308e-07 | +2.7% |
| worst | 1069 | 8.012e-07 | 4.407e-07 | 4.104e-07 | +6.9% | 3.873e-07 | +12.1% |
| worst | 1054 | 8.155e-07 | 3.437e-07 | 3.193e-07 | +7.1% | 3.142e-07 | +8.6% |
| median | 1000 | 1.936e-07 | 6.534e-07 | 6.482e-07 | +0.8% | 6.462e-07 | +1.1% |
| median | 1075 | 1.943e-07 | 3.822e-07 | 3.806e-07 | +0.4% | 3.851e-07 | -0.8% |
| median | 1045 | 1.949e-07 | 2.206e-07 | 2.098e-07 | +4.9% | 2.105e-07 | +4.6% |
| median | 1031 | 1.967e-07 | 4.094e-07 | 3.737e-07 | +8.7% | 3.593e-07 | +12.2% |
| median | 1058 | 1.981e-07 | 2.178e-07 | 2.264e-07 | -3.9% | 2.299e-07 | -5.5% |

- relaxed: worst-group mean improvement +7.1% (bar: >= +30%), median-group mean |change| 3.7% (bar: < 10%) -> confirms: False
- unpruned: worst-group mean improvement +10.1% (bar: >= +30%), median-group mean |change| 4.8% (bar: < 10%) -> confirms: False

- paired per-replicate improvements (n=30 pairs/cell): relaxed worst
  +3.8% [95% CI +0.6, +7.0], relaxed median +1.6% [-1.7, +5.0], unpruned
  worst +6.6% [+2.8, +10.5], unpruned median +1.7% [-2.9, +6.2]. The 30%
  bar is 3-4x beyond every upper CI: the kill is not noise-straddled.
- regression to the mean: worst-group stage-1 mean 7.41e-7 -> R=6 4.23e-7;
  median-group 1.96e-7 -> 3.77e-7; separation 3.79x -> 1.12x.
- within-net single-draw rep spreads (default arm): 2.3x-8.7x.

## Observations for the mutation ladder (NOT acted on here)

- Pruning is a good trade as shipped: unpruned bills 2.40e11 FLOPs (+41%
  vs default 1.70e11, still under the 2.72e11 budget) for a uniform ~2-10%
  MSE reduction. A pruning-off/relaxed variant is a legal, small, uniform
  improvement candidate -- it would need its own predeclared M186+ gate;
  it is NOT a tail fix.
- Any future tail work must target per-draw variance (the estimator's own
  randomization noise), not net-conditional structure: with per-net MC
  difficulty constant (A1) and the tail being draw luck (this run), the
  lever is variance reduction of the randomized estimate, subject to the
  FLOP budget.

## Firewall

Synthetic He nets only (t3-style, seeds 1000..1079); frozen v3 imported
read-only with bytecode writes disabled, subclassed never edited; only
kerdock_phases.npz loaded (the width-256 path never touches the Sobol
asset and deletes _gaussian); no datasets/truth/scorer/submissions; no
git; all writes inside this experiment directory.

## Files

- run_m185_g0.py -- runner (predeclared gates in docstring; checkpoint/resume)
- m185_g0_results.json -- verdict + stage-1 analysis + per-net records +
  stage-2 arms
- m185_g0_stage1_checkpoint.json / m185_g0_stage2_checkpoint.json -- raw
  per-net data incl. pred31/truth31 vectors and per-rep MSEs

