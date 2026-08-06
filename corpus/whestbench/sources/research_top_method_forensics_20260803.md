# ARC WhestBench top-method forensics — source log

Accessed 2026-08-03 (America/Chicago). Scope: public Phase-I leaderboard,
public submission ledgers, challenge rules, forum posts, FlopScope fixes, and
public GitHub repositories. No private grader state, submission artifact, or
non-public participant code was accessed.

## Official rules and scoring

- Challenge overview:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026
- Rules v12:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/challenge_rules
- Leaderboard:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards
- ARC announcement:
  https://www.alignment.org/blog/announcing-the-arc-white-box-estimation-challenge/
- Algorithmic-contribution guidance:
  https://discourse.aicrowd.com/t/algorithmic-contribution-prize-guidelines-how-arc-judges-these-prizes-discretion-technical-writeups-llm-usage/18041

Rules v12 §§5.2, 5.5, and 5.6 say submissions may call any other library,
backend, language, executable, or bundled file; work outside FlopScope is
charged through residual wall time. The same rules prohibit modifying
FlopScope or otherwise circumventing budget enforcement. Section 5.3 reserves
the organizer's right to patch material accounting gaps and regrade. Section
5.4 says the live score is only the 50-MLP public half; Phase-I prizes combine
public and hidden halves, and Phase-II prizes use a fresh unseen rerun.

## Live top twelve at the requested threshold

The live public board at collection time had twelve rows with adjusted score
at or below 5e-8. `inst. share` is the mean instrumented FLOP count visible in
the 50-row ledger divided by the page's mean effective compute. Values are
rounded; the pages remain the authoritative records.

| rank | participant | submission | adjusted | raw final MSE | mean effective compute | inst. share | all-layer MSE |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | joe_wanza | [322522](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/322522) | 7.39e-9 | 5.21e-8 | 3.78e10 | 0.0344% | 0.7537 |
| 2 | dpskv5 | [322693](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/322693) | 7.81e-9 | 5.75e-8 | 5.12e10 | 0.00412% | 0.7437 |
| 3 | dstepanov | [322862](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/322862) | 1.41e-8 | 3.57e-8 | 1.07e11 | 0.01196% | 6.99e-5 |
| 4 | ely2sh | [322203](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/322203) | 1.46e-8 | 6.43e-8 | 6.17e10 | 0.02382% | 0.7537 |
| 5 | kaileh57 | [322684](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/322684) | 1.80e-8 | 1.45e-8 | 3.40e11 | 0.00371% | 0.7537 |
| 6 | huang_chung_yi | [322006](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/322006) | 1.98e-8 | 1.65e-7 | 3.44e10 | 0.728% | 7.86e11 |
| 7 | abhinav_gorrepati | [319578](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/319578) | 2.30e-8 | 2.10e-7 | 2.91e10 | 0.0433% | 0.7537 |
| 8 | raghavsk | [322650](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/322650) | 2.80e-8 | 1.83e-7 | 4.19e10 | 0.0685% | 0.7537 |
| 9 | adrianleb | [321700](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/321700) | 3.12e-8 | 6.23e-8 | 1.38e11 | 0.01065% | 0.7537 |
| 10 | mliston | [321175](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/321175) | 3.18e-8 | 3.52e-8 | 2.41e11 | 0.00262% | 106.214 |
| 11 | fklassen | [320595](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/320595) | 3.45e-8 | 1.62e-7 | 5.76e10 | 0.00731% | 3.46e-5 |
| 12 | josu | [320953](https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/320953) | 4.09e-8 | 7.64e-8 | 1.47e11 | 0.00144% | 0.7537 |

Eleven of twelve have instrumented shares below 0.1%; all twelve are below 1%.
Seven have the repeated all-layer value 0.7537, one has 0.7437, and two have
very large all-layer errors. Those diagnostics are consistent with final-row-
only output and placeholder/garbage earlier rows. dstepanov and fklassen are
the two clear exceptions with useful full-layer arrays.

This is an execution-family fingerprint, not an identification of the
underlying estimator. A residual-dominated entry might contain native RQMC,
native ordinary sampling, a compiled analytic method, or public-suite
adaptation. The ledger cannot distinguish them.

## What top participants have actually disclosed

Repository searches for `whestbench` / `arc-whitebox` returned the official
repositories and only three participant research repositories:

- https://github.com/jamesrahenry/arc-whitebox-replication
- https://github.com/ascender1729/whestbench-cumulant-propagation
- https://github.com/itsjustmarsel/whest-teardown

One top-twelve participant has a public project page:
https://github.com/ely2ba/whestbench-ely2sh. Its README names randomized QMC,
variance reduction, CPU execution, and performance engineering as the research
focus, but explicitly keeps implementation and detailed notes private until
after the competition. No public method writeup or code tied to the other top-
twelve submission IDs was found in the forum/GitHub search. Therefore claims
about their exact samplers, native kernels, or target fitting would be
speculation.

High submission counts and final-row-only output also do not prove target
reconstruction. They only make public-suite adaptation plausible. Mathematically,
an exact per-MLP squared-error oracle exposes a target vector `y` through
`q(p)=||p-y||^2/n`: `q(0)` plus probes `q(t e_i)` give
`y_i=(t^2+n(q(0)-q(t e_i)))/(2t)`. This shows why a public score should not be
treated as generalization evidence. Using inferred public targets would not
survive the fresh private suite, and attempting to access or bundle private
reference outputs is expressly prohibited by §5.2.

## Public accounting evidence

- Raw-array/residual-channel report:
  https://discourse.aicrowd.com/t/potential-flopscope-accounting-bypass-bug/18099
- Wall-time channel analysis:
  https://discourse.aicrowd.com/t/recommendation-restoring-the-estimation-framing-neutralizing-the-wall-time-compute-channel/18108
- Reproducible teardown:
  https://github.com/itsjustmarsel/whest-teardown
- Accounting note:
  https://github.com/itsjustmarsel/whest-teardown/blob/main/findings/ACCOUNTING_NOTE.md
- Unbiased-floor pre-registration:
  https://discourse.aicrowd.com/t/a-bet-on-a-floor-filed-before-the-reveal/18105

The forum report independently identifies the same `<0.001` instrumented-share
signature and explains that raw NumPy-backed arithmetic is then priced mainly
by residual wall time. The teardown reproduces a 4096-square matmul billed
4.44x more cheaply through a raw path on its test CPU. These are participant
measurements, not organizer findings, but the live ledgers strongly corroborate
that residual compute dominates the leaders.

The clean conclusion is narrower than “the leaders cheated.” Official rules
allow bundled native code and explicitly price non-FlopScope work via residual
wall time. They also prohibit circumventing budget enforcement, reserve final
code review, and allow accounting fixes/regrades. A disclosed native backend is
inside the written design; intentionally extracting raw buffers to evade the
analytical meter is high disqualification/repricing risk. Exact participant
intent is not public.

### Known historical exploit that is no longer actionable

- Bug report:
  https://discourse.aicrowd.com/t/there-is-a-bug-in-flopscope-numpy-linalg-solve-that-undercounts-batched-right-hand-sides/18082
- Patch:
  https://github.com/AIcrowd/flopscope/pull/150
- Closed FlopScope fixes:
  https://github.com/AIcrowd/flopscope/pulls?q=is%3Apr+is%3Aclosed

The batched-RHS `linalg.solve` underbilling was acknowledged by the organizer,
fixed in PR #150, and affected submissions were regraded. Later fixes include
destination/out handling, einsum billing, dispatch accounting, and empty
contracts. These are evidence that the accounting surface was moving, not
reproducible winning ideas.

## Public method writeups with reproducible ideas

### Randomized rank-1 lattice + exact first row

https://discourse.aicrowd.com/t/unbiased-randomized-qmc-rao-blackwell-for-post-relu-activation-means-method-unbiasedness-proof-and-where-the-frontier-is/18053

Random-shift rank-1 lattice points are inverse-CDF mapped to Gaussian inputs;
the first ReLU row is exact. Reported adjusted score: about 4.10e-7. Scrambled
Sobol tied the lattice, Korobov was sample-count-sensitive, and upstream linear
controls gave only about 1.0–1.2x.

### RQMC prefix + analytic suffix + deployed-noise corrector

https://discourse.aicrowd.com/t/phase-1-write-up-a-variance-bias-budget-for-deep-white-box-mean-estimation-submission-317660/18085

The reported pipeline used a random-shift Roberts lattice through layer 31,
exact layer 1, light empirical-to-Gaussian moment shrinkage, a final Gaussian
closure, measured skew/kurtosis Edgeworth terms, and an offline ridge fitted on
features carrying the same noise as deployment. Adjusted score was 4.47e-7.
The writeup measured a 1.40x lattice gain over equal-budget IID under its
shrinkage, about 8% from sample-skew Edgeworth, and about 23% from the final
corrector. It warns that fitting on converged features fails at deployed sample
count; layerwise re-anchoring, median-of-means, antithetic RQMC, learned
quadrature weights, nonlinear heads, and global spectral features were
negative.

### Structure-aware conditional sampling

https://discourse.aicrowd.com/t/phase-i-submission-structure-aware-estimation-for-random-relu-mlps/18106

Moment propagation classifies neurons as dead/on/kink, a pilot reclassifies
borderline units, antithetic Sobol samples through layer 30, and the final two
layers linearize on-neurons while sampling kink neurons. Columns/rows are
grouped by firing-rate sparsity. Reported adjusted/raw: 1.551e-7 / 2.18e-7.

### Trajectory-calibrated moment chain

https://discourse.aicrowd.com/t/phase-1-write-up-stabilizing-cumulant-propagation-at-depth-32-a-trajectory-calibrated-moment-chain-with-an-error-budget-submission-314695/18097

Per-layer moment errors anticorrelate and cancel, while coherent bias is
amplified about 16:1. Corrections therefore must be fitted on rolled-forward
deployment trajectories. Participation ratio shrank from 128 to 5.2, but the
naive low-rank split had only about 2% possible gain because sampling noise
lives in the same leading subspace. Public code:
https://github.com/jamesrahenry/arc-whitebox-replication

### Gaussian scale correction and cumulant ports

- Scalar correction:
  https://discourse.aicrowd.com/t/phase-1-write-up-characterizing-a-systematic-scale-bias-in-the-gaussian-closure-estimator-submission-314331/18063
- Independent cumulant port:
  https://github.com/ascender1729/whestbench-cumulant-propagation
- Reproducible RQMC/Edgeworth teardown:
  https://github.com/itsjustmarsel/whest-teardown/blob/main/findings/FINDINGS.md

A roughly 0.992 multiplicative correction gave a 3x MSE reduction for one
second-order closure, but higher cumulants, low-rank, recurrence, exact-moment
Edgeworth, and nonlinear correctors did not beat it at depth 32. The independent
cumulant port reports about 1.2e-6 raw final MSE for K=3 at depth 8, not a top
depth-32 result. The teardown reports 2.9e-7 adjusted from scrambled Sobol plus
Edgeworth-K4, localizes the remaining error to deep mean/covariance propagation,
and reports negative K6, saddlepoint, scalar renormalization, and cheap diagonal
K4 closures.

[03:20:00] SAVED: Public top-twelve ledger, official rules, public method
disclosures, accounting evidence, and legal/reproducible method families.
