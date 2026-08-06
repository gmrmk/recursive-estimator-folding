# Adversarial audit: latent-factor closure

## Verdict

**FAIL for promotion of the fixed `q=3,r=2` mechanism.** The implementation is
target-free and its small-width improvement is real, but the evidence does not
generalize toward the target width. In a fresh synthetic width sweep the method
lost to a numerically corrected full-covariance closure on **all 8/8 width-64
networks**. Aggregate candidate/fullcov MSE ratios were 2.928 at `L=16` and
1.596 at `L=32`. This reverses the reported width-4/8/16 result before reaching
`n=256`.

The reported 0.04738 aggregate ratio is **not caused by target leakage or by the
comparator's numerical bug**. It is genuine small-width behavior, but it is
fragile, dominated by a high-error case, and mechanistically tied to a rank-two
factor that captures a rapidly shrinking fraction of covariance as width grows.

Audit scope was synthetic only. No WHest scorer, public/private model, truth
array, or competition dataset was read or run. The audited source hashes were:

```text
latent_factor_closure.py DB71FC14E0ABDC234738A5A917F91BF2948CB710FEEF7E3105C528D554987DD3
run_premise.py          15DA7B277FC422754DDA99510B9B00B914ED6D9F8584A477AF9C791E28ECB1BD
premise_results.json    C6955D5FBAA8EAC6EA2799CC72E5BBE6C0FCE74DCC87148A5670C6FA10E6DAC8
test_invariance.py      87C9585FA457B8C59FD07F9D2AB9F60A71294B6B9BEFEE1D6E7C9BD9B873BB22
```

## Findings

| check | result | evidence |
|---|---|---|
| Target/reference leakage | **PASS** | Static scan found no file/data/reference access in `latent_factor_closure.py`; its output depends only on supplied weights and fixed hyperparameters. References enter only `score_predictions` after inference. |
| Weight orientation and shapes | **PASS** for the fixed square model | `forward` uses row states `X @ W`; mean and covariance use `mu @ W` and `W.T @ Sigma @ W`. A one-layer analytic check matched the fullcov result exactly; the wrong orientation differed by 0.268 max-abs. |
| Diagonal Gaussian ReLU moments | **PASS** | The implemented first and second moments match the standard univariate formulas. |
| Claimed exact full-covariance ReLU moments | **FAIL (numerical)** | `phi2_gauss10` is only 10-node quadrature. At zero means and `rho=-0.9999`, it returns an impossible raw cross-moment `-0.00726166` versus the exact positive `1.50053e-7`; at `rho=+0.9999` absolute error is `0.00726181`. Premise trajectories do reach `|rho|>0.99`. |
| Comparator-bug sensitivity | **PASS for the small-width ratio** | Replacing the 10-node CDF integral with 256/512-node quadrature changes aggregate fullcov MSE from `0.05699147` to `0.05681645`, and the candidate ratio only from `0.0473808` to `0.0475268`. The 256/512 prediction discrepancy is at most `7.20e-11` over the seven cases. |
| Permutation/sign gauge | **PASS on tested generic spectra** | Both original tests pass; end-to-end permutation discrepancy was previously `2.22e-15`. Reduction preserves mixture mean/covariance to `1.11e-16`/`1.78e-15`. |
| Eigen/tie numerical gauge | **FAIL (scale discontinuity)** | `leading_factors` uses `scale=max(lambda_max,1)`, so `diag(2,1,.5)` retains rank one at scales 1 and `1e-8`, but abruptly returns rank zero at `1e-12`. Scaling only the first layer by `1e-6` caused an 11.67% violation of expected output homogeneity. The absolute residual floor and score-tie tolerance have the same issue. |
| Reference harness | **WARN** | MC references are correctly separated and use fixed Philox antithetic paths. GH17 is a deterministic quadrature approximation, not exact truth: an independent 4,194,304-base-sample check on `n=4,L=16,seed=202` differed by 41.1 reported MC standard errors on one small output (`3.01e-5` absolute). This does not explain the large estimator gap. |
| Original-case concentration | **WARN** | One `n=4,L=16` case supplies 84.0% of corrected fullcov summed MSE. Removing it raises the ratio from `0.0475` to `0.2854`, still below the declared 0.80 premise gate. Median case ratio is `0.0320`; one of seven cases loses (`1.0423` after comparator correction). |
| Fresh small-width seeds | **PASS, but heterogeneous** | On 24 new `n=8,16` networks, candidate wins 21/24; aggregate ratio `0.1646`, median `0.1324`, worst `14.33`. Removing the largest baseline-error case gives `0.2985`. The effect is real but not uniformly safe. |
| Width extrapolation | **HARD FAIL** | At `n=32`, ratios are `0.5606` (`L=16`, 5/6 wins) and `0.9169` (`L=32`, 4/6). At `n=64`, ratios are `2.9281` and `1.5959`, with 0/4 wins in each depth group. Independent 4x-larger MC reruns confirmed representative ratios `2.8280` and `1.1492`. |

## Why the reversal is mechanistically expected

The selected rank-two factors explain most of a small Wishart covariance but a
vanishing share as width grows. Across 16 fresh first-layer matrices per width,
the mean top-two trace fractions were:

```text
n=4:   0.8838
n=8:   0.6168
n=16:  0.3730
n=32:  0.2146
n=64:  0.1144
n=128: 0.0586
n=256: 0.0302
```

Everything outside those two factors is diagonalized. Thus the branch is close
to a rich mixture at `n=4`, but approaches a diagonal-residual closure at target
width. The observed transition from strong wins at 8/16 to consistent losses at
64 is aligned with this mechanism, not random reference noise.

There is also avoidable bias at the first layer, where the preactivation is
exactly Gaussian: on a fresh `n=7` one-layer network, fullcov matched the exact
mean to machine zero while `q3,r2` had max-abs error `0.01683` because finite
factor quadrature was applied before any non-Gaussian hidden law existed.

## Supported conclusion

The code is an honest, identified, non-scalar assumed-density construction, and
the reported small-width result is reproducible. It is **not a viable target-
width survivor in fixed rank-two form**. Do not spend an official scorer read or
fold it into the champion. Any successor must first solve the width law—for
example, a rank or structured-factor budget whose captured covariance/dependence
does not collapse from 88% to 3%—and must pass a target-free `n>=64` synthetic
gate. The 10-node bivariate comparator and absolute eigengap/tie thresholds also
need correction before further evidence is trusted.

## Reproducible checks

Run from this directory with the NumPy-enabled project interpreter:

```powershell
& '..\..\whest-v014\Scripts\python.exe' -m unittest -v test_invariance.py
& '..\..\whest-v014\Scripts\python.exe' adversarial_checks.py
& '..\..\whest-v014\Scripts\python.exe' adversarial_seed_sweep.py
& '..\..\whest-v014\Scripts\python.exe' adversarial_width_sweep.py
```

Machine-readable outputs are `adversarial_checks.json`,
`adversarial_seed_sweep.json`, and `adversarial_width_sweep.json`. The audit
scripts regenerate only iid-He synthetic weights and exact forward paths; none
imports WHestBench or reads competition data.
