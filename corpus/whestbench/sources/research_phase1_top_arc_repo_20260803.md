# Phase-I top-method and ARC repository forensics — source log

Accessed 2026-08-03 (America/Chicago). Scope: current public leaderboard,
official challenge/round guidance, the ARC cumulant-propagation paper and
repository, public participant writeups, public estimator files, and public
Git commit records. No dataset or estimator runs were performed for this
research pass. No private grader state or non-public participant code was
accessed.

## Bottom line

The exact algorithms behind the live #1 and #2 entries are not publicly
recoverable. The most defensible execution-family inference is a native or
highly vectorized, final-layer-only stochastic estimator: radial-exact
Monte Carlo or RQMC, probably with variance reduction and possibly a
conditional/analytic treatment of the last one or two layers. This is an
inference from the public ledgers and disclosed neighboring methods, not an
identification of any participant's private code.

The strongest public evidence in that direction is:

1. The top-twelve ledgers are overwhelmingly residual-time dominated and many
   entries return placeholders for unscored earlier rows.
2. Live top-four participant `ely2sh` publicly names RQMC, variance reduction,
   CPU execution, and performance engineering, while keeping code private:
   https://github.com/ely2ba/whestbench-ely2sh
3. The best disclosed clean Phase-I method is structure-aware conditional
   sampling: antithetic Sobol through layer 30 plus analytic linearization of
   stable neurons in the final two layers. It reports adjusted/raw
   `1.551e-7 / 2.18e-7`:
   https://discourse.aicrowd.com/t/phase-i-submission-structure-aware-estimation-for-random-relu-mlps/18106
4. Public graded radial-exact Monte Carlo reached `6.684538479656953e-7` on
   submission 316676. Its exact submitted source snapshot is public:
   https://github.com/noahmacaulay/whest-starterkit/blob/2227ef3/estimator.py
   and the graded-score commit is:
   https://github.com/noahmacaulay/whest-starterkit/commit/e46a2917c608908cab4fd4c6da118b4906f9d6f2
5. The same repository's public experiments found exact-Haar orthogonal
   directions roughly 18–23% better than that radial baseline on its full
   public protocol, but candidate submissions using the new frame operations
   failed in the grader. That is reproducible research evidence, not a
   successful official score. Key commits:
   https://github.com/noahmacaulay/whest-starterkit/commit/01029c40223ae8d0798905fb7d901c9ab
   https://github.com/noahmacaulay/whest-starterkit/commit/7dc7e0ba0122d474a402a381c4bcabd7d901c9ab
   https://github.com/noahmacaulay/whest-starterkit/commit/fa9e4e2ba647a3d5bebe905ecae400d168196ae9

## Current public board and round caveats

- Live leaderboard:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards
- Current top six observed on 2026-08-03:
  `joe_wanza 7.4e-9`, `dpskv5 7.8e-9`, `dstepanov 1.38e-8`,
  `ely2sh 1.46e-8`, `kaileh57 1.80e-8`, `huang_chung_yi 1.98e-8`.
- Challenge overview:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026
- Phase-I launch:
  https://discourse.aicrowd.com/t/phase-1-launch-deeper-models-and-increased-prizes/18026
- Algorithmic-prize/writeup guidance:
  https://discourse.aicrowd.com/t/algorithmic-contribution-prize-guidelines-how-arc-judges-these-prizes-discretion-technical-writeups-llm-usage/18041
- Town hall summary:
  https://discourse.aicrowd.com/t/townhall-summary-recording/18078

The public ladder is provisional, not the Phase-I winner list. Phase-I
submissions closed 2026-07-31, but the writeup deadline is 2026-08-07 23:59
UTC and prize/final hidden rankings have not been announced as of this access.
The public score is not the hidden half. Phase II requires designating one
entry, which is rerun on a fresh unseen MLP suite; public-suite tuning and
accounting-dependent tricks may not survive that rerun or code review.

## ARC `mlp_cumulant_propagation`: what it does and does not establish

- Paper: https://arxiv.org/abs/2605.05179
- PDF: https://arxiv.org/pdf/2605.05179
- ARC explainer:
  https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/
- Repository:
  https://github.com/alignment-research-center/mlp_cumulant_propagation
- README/API:
  https://github.com/alignment-research-center/mlp_cumulant_propagation/blob/main/README.md
- Harmonic implementation:
  https://github.com/alignment-research-center/mlp_cumulant_propagation/blob/main/src/mlp_kprop/kprop_harmonic.py
- Factorized K3/K4 implementations:
  https://github.com/alignment-research-center/mlp_cumulant_propagation/blob/main/src/mlp_kprop/factor_k3.py
  https://github.com/alignment-research-center/mlp_cumulant_propagation/blob/main/src/mlp_kprop/factor_k4.py
- Experiment script:
  https://github.com/alignment-research-center/mlp_cumulant_propagation/blob/main/scripts/kprop_by_width.py
- Dependencies:
  https://github.com/alignment-research-center/mlp_cumulant_propagation/blob/main/pyproject.toml

ARC develops sample-free Hermite/cumulant distribution propagation. The paper
conjectures mean-squared error scaling like `c_K (L/n)^K`, with a basic
runtime around `c'_K L n^(K+1)` and factorized K3/K4 runtime around
`c''_K L^2 n^K`. The factorization removes roughly one factor of width.

However, it is not a WhestBench submission and is not directly compatible
with the fixed contest sandbox: it is a PyTorch research package with a much
larger dependency set. Its headline empirical comparison is for width 256 and
four hidden layers; the paper's depth experiments extend to 12 hidden layers,
not the Phase-I depth 32. The paper also observes worsening error with depth.
Therefore the repo is a useful source of correction terms and closure
structure, not public evidence for the live winning Phase-I estimator.

## Public WhestBench-compatible cumulant ports

### Independent K3 port

- Repository:
  https://github.com/ascender1729/whestbench-cumulant-propagation
- Estimator:
  https://github.com/ascender1729/whestbench-cumulant-propagation/blob/master/estimator.py
- Results:
  https://github.com/ascender1729/whestbench-cumulant-propagation/blob/master/RESULTS.md

This is a self-contained NumPy/FlopScope port of the ARC method. It reports
bit-exact agreement (within `1e-12`) with selected Torch modules. On the
warmup depth-8 grader, factorized K3 SIMPLE used about `1.71e10` analytical
FLOPs and scored `7.28e-7`; a final-row K2-to-K3 extrapolation reached
`6.65e-7`. These are depth-8 warmup results, not depth-32 Phase-I results.

### Trajectory-calibrated moment chain

- Repository: https://github.com/jamesrahenry/arc-whitebox-replication
- Graded estimator:
  https://github.com/jamesrahenry/arc-whitebox-replication/blob/master/moment_chain/estimator_chain.py
- Writeup:
  https://github.com/jamesrahenry/arc-whitebox-replication/blob/master/WRITEUP.md
- Forum report:
  https://discourse.aicrowd.com/t/phase-1-write-up-stabilizing-cumulant-propagation-at-depth-32-a-trajectory-calibrated-moment-chain-with-an-error-budget-submission-314695/18097

Submission 314695 scored raw `5.89e-6`, adjusted `9.97e-7`. It rolls a
mean/covariance chain forward, uses a K=10 Hermite bivariate Gaussian ReLU
closure, and fits 512 per-layer stabilizer coefficients on the distribution
of its own rollout errors. Its public measurement of plain ARC K2 at depth 32
was mean final MSE `6.28e-5` across 40 challenge networks. The authors state
their sampling-family estimator did better. This strongly cautions against
deploying the ARC closure unchanged at depth 32.

## Other public reproducible estimator families

### Exact radial factorization

For a bias-free ReLU MLP, positive homogeneity gives
`E[f(Z)] = E[R] E[f(U)]` for `Z=RU`, where `U` is uniform on the sphere and
`R` is chi-distributed and independent. Replacing sampled radii by exact
`E[R]` removes one variance component at negligible cost.

- Exact officially graded snapshot:
  https://github.com/noahmacaulay/whest-starterkit/blob/2227ef3/estimator.py
- Graded score record:
  https://github.com/noahmacaulay/whest-starterkit/commit/e46a2917c608908cab4fd4c6da118b4906f9d6f2
- Current shared-Haar signed-orbit candidate:
  https://github.com/noahmacaulay/whest-starterkit/blob/main/estimator.py

The current file is not the successful submitted artifact: its QR/shared-frame
lineage encountered grader evaluation errors. Use the immutable `2227ef3`
snapshot when reproducing the known official result.

### Randomized spherical-radial cubature

- Estimator:
  https://github.com/rcpaffenroth/whest/blob/main/estimator.py

This applies degree-3 spherical-radial cubature: `±E[R] e_i` rotated by
multiple Haar frames, propagated through the full MLP. The code is concrete
and contest-shaped, but no tied public official submission or score was found.

### RQMC plus Edgeworth teardown

- Repository: https://github.com/itsjustmarsel/whest-teardown
- Estimator:
  https://github.com/itsjustmarsel/whest-teardown/blob/main/experiments/02_honest_estimator.py
- Findings:
  https://github.com/itsjustmarsel/whest-teardown/blob/main/findings/FINDINGS.md
- Accounting note:
  https://github.com/itsjustmarsel/whest-teardown/blob/main/findings/ACCOUNTING_NOTE.md

This reports roughly `2.9e-7` adjusted for scrambled Sobol plus an Edgeworth
K4 correction on a public-mini experimental protocol. It is not tied to an
official leaderboard entry, and its protocol is not identical to the grader.

### Disclosed Phase-I RQMC hybrids

- Unbiased randomized rank-1 lattice plus exact first row:
  https://discourse.aicrowd.com/t/unbiased-randomized-qmc-rao-blackwell-for-post-relu-activation-means-method-unbiasedness-proof-and-where-the-frontier-is/18053
  Reported adjusted score: about `4.10e-7`.
- RQMC prefix, analytic final layer, Edgeworth, and deployment-noise ridge:
  https://discourse.aicrowd.com/t/phase-1-write-up-a-variance-bias-budget-for-deep-white-box-mean-estimation-submission-317660/18085
  Reported adjusted score: `4.47e-7`.
- Structure-aware conditional Sobol estimator:
  https://discourse.aicrowd.com/t/phase-i-submission-structure-aware-estimation-for-random-relu-mlps/18106
  Reported adjusted/raw: `1.551e-7 / 2.18e-7`.

## Accounting and integrity caveat

- Public participant report:
  https://discourse.aicrowd.com/t/potential-flopscope-accounting-bypass-bug/18099

The report shows that NumPy-backed raw arrays can perform arithmetic outside
the instrumented analytical counter, leaving residual wall time as the main
charge. The top-ledger signatures are consistent with native/residual-heavy
execution, but that does not prove misconduct: official rules allow other
libraries/backends and bill them through residual time. The rules also forbid
circumventing enforcement and reserve patch/regrade/code-review authority.
Any intended solution should disclose native computation and avoid raw-buffer
extraction whose purpose is evading analytical accounting.

## Search limits and negative findings

Global GitHub searches for the exact top participant handles plus
`whest`/`whestbench` found no obvious public repositories tied to the live
#1, #2, #3, #5, or #6 submission IDs. The only direct top-four public project
found was `ely2sh`, whose code is deliberately private until competition end.
Absence from this search is not proof that no public code exists, but it means
that naming an exact #1 algorithm would currently be speculation.

[2026-08-03] SAVED: current board snapshot, provisional-round caveats, ARC
repository applicability audit, immutable graded radial estimator snapshot,
public cumulant ports, public RQMC/structure-aware methods, and integrity
caveats.
