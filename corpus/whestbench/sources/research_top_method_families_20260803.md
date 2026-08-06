# ARC WHestBench public method-family audit — 2026-08-03

Accessed 2026-08-03. This preserves the public-source evidence used to open a
new score-oriented generation while leaving the frozen tangent fallback
untouched.

## Official mechanistic-estimation reference

- Paper: https://arxiv.org/abs/2605.05179
- ARC explanation: https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/
- Code: https://github.com/alignment-research-center/mlp_cumulant_propagation

ARC's reference family propagates approximate activation distributions rather
than network samples. Its key machinery is cumulant/Hermite propagation,
including harmonic and diagonal-slice symmetric-tensor representations and
factorized order-3/order-4 variants. The authors report an asymptotic factor-n
advantage over Monte Carlo at fixed depth, but warn that depth dependence is
worse and depth growing with width remains open.

## Public competition write-ups

### RQMC + Rao-Blackwell

Source:
https://discourse.aicrowd.com/t/unbiased-randomized-qmc-rao-blackwell-for-post-relu-activation-means-method-unbiasedness-proof-and-where-the-frontier-is/18053

- Randomly shifted rank-1 lattice inputs plus exact layer-1 ReLU means.
- Reported adjusted score about 4.10e-7 at C/B about 0.42.
- Scrambled Sobol and Kronecker lattice tied per row.
- Input-anchored linear/control-variate families decorrelated at depth 32.

### Sampling-prefix / analytic-suffix hybrid

Source:
https://discourse.aicrowd.com/t/phase-1-write-up-a-variance-bias-budget-for-deep-white-box-mean-estimation-submission-317660/18085

- RQMC through layer 31, light shrinkage toward a Gaussian-closure chain,
  Gaussian-conditional final layer, sample-skew/kurtosis Edgeworth terms, and
  an offline noisy-feature-trained ridge corrector.
- Reported grader adjusted score 4.47e-7 at multiplier 0.1009.
- Two-budget decomposition found 68–73% closure bias under realistic RQMC
  decay; more samples did not repay leaving the 0.1 multiplier floor.
- Exact Wick covariance helped pure covariance propagation by 6.5% but was
  redundant inside the empirical hybrid.
- Low-rank, nonlinear heads, learned quadrature weights, repeated analytic
  anchoring, and input-anchored controls were negative.
- The proposed next frontier was deterministic cumulant propagation with
  offline-learned per-layer closure corrections.

### Structure-aware conditional sampling

Source:
https://discourse.aicrowd.com/t/phase-i-submission-structure-aware-estimation-for-random-relu-mlps/18106

- Moment propagation classifies neurons as dead, on, or kink; pilot samples
  rescue/reclassify uncertain cases.
- Sobol sampling continues through layer 30; final on-neurons are integrated
  linearly while kink neurons remain sampled.
- Sparse activations are sorted/grouped to reduce matrix-multiplication work.
- Reported adjusted score 1.551e-7, raw MSE 2.18e-7.

### Trajectory-calibrated moment chain

Source:
https://discourse.aicrowd.com/t/phase-1-write-up-stabilizing-cumulant-propagation-at-depth-32-a-trajectory-calibrated-moment-chain-with-an-error-budget-submission-314695/18097

- Moment-propagation errors can anticorrelate and cancel across layers while
  coherent bias is amplified about 16:1.
- Per-layer corrections must be fitted on the chain's own rolled-forward
  deployment trajectories; truth-reanchoring and variance-only shrinkage can
  worsen the final result.
- Covariance participation ratio contracted from about 128 to 5.2, but
  sampling noise concentrated in the same leading subspace as signal; merely
  analyzing the complement had a roughly 2% ceiling.

### Scalar-corrected Gaussian closure

Source:
https://discourse.aicrowd.com/t/phase-1-write-up-characterizing-a-systematic-scale-bias-in-the-gaussian-closure-estimator-submission-314331/18063

- A stable multiplicative scale correction reduced second-order closure MSE
  about 3× at zero extra prediction FLOPs.
- Higher-cumulant, low-rank, recurrence, Edgeworth, and nonlinear correctors
  did not beat the scalar at depth 32 in that implementation.

## Why the public top ladder is not an honest target

- Accounting-bypass report:
  https://discourse.aicrowd.com/t/potential-flopscope-accounting-bypass-bug/18099
- Wall-time compute-channel analysis:
  https://discourse.aicrowd.com/t/recommendation-restoring-the-estimation-framing-neutralizing-the-wall-time-compute-channel/18108
- Current rules question:
  https://discourse.aicrowd.com/t/rules-clarification-are-operations-on-the-numpy-backed-arrays-reachable-through-flopscope-numpy-inside-the-intended-accounting-boundary/18122
- Pre-reveal floor prediction:
  https://discourse.aicrowd.com/t/a-bet-on-a-floor-filed-before-the-reveal/18105

Public participants measured instrumented/effective-compute ratios below 0.001
for several top submissions: most real arithmetic was running outside the
instrumented path and being priced only by residual wall time. This can create
an order-of-magnitude apparent score advantage and remains under organizer
clarification. It is excluded from this project under the strict accounting
boundary. An independent pre-reveal estimate placed the honest unbiased floor
near 3.7e-7 adjusted on unseen networks.

## Immediate design consequence

The frozen tangent candidate's WHestBench 0.14 adjusted dev score 2.77486e-7
already clears the public honest-floor estimate, but uses about 0.332B and thus
does not receive the 0.1 multiplier. The high-leverage search is therefore not
"copy the 9.2e-9 leader"; it is a legal joint optimization:

1. move toward 0.1B by conditional/analytic late-layer integration and better
   sparsity accounting;
2. replace lost sample accuracy with trajectory-calibrated moment or
   multifidelity controls whose deployment noise is represented during fit;
3. evaluate raw MSE × max(0.1,C/B), whole-network paired, under WHestBench 0.14;
4. reject any uninstrumented arithmetic path regardless of leaderboard reward.

[03:00:00] SAVED: Public method-family audit with 12 source URLs.
