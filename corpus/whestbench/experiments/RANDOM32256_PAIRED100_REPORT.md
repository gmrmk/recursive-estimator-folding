# Random orthogonal fold3 32,256 versus frozen 39,936: paired public-100 resolution

**Date:** 2026-08-06  
**Decision:** **PROMOTE `random32256` over the frozen `random39936` parent under the predeclared official gate.**  
**Scope:** public dataset indices 0--99 only; no index at or above 100 was evaluated, no locked data was accessed, and nothing was submitted.

## Outcome

The 32,256-base child passes every declared candidate condition:

- one-million-resample paired network-cluster bootstrap 95% percentile CI for candidate-minus-parent adjusted score is strictly negative: `[-4.017637049e-2, -1.955091686e-3]`;
- candidate failures: `0/100`;
- candidate maximum effective compute: `250.488783B`, leaving `21.511217B` below the 272B hard budget and remaining below the predeclared safety threshold `0.95 * 272B = 258.4B`.

The frozen 39,936 parent failed combined-budget enforcement on 5/100 public networks and reached maximum effective compute `294.998930B`. Those failures are official outcomes, not censored observations. They produce zeroed predictions and dominate the uncensored official bootstrap. The promotion is therefore primarily a **cost-robustness win**, not evidence that the smaller child has lower raw sampling error.

On the 95 networks where both branches completed, the child has 14.71% worse raw MSE but 6.44% better adjusted score. This descriptive sensitivity was not substituted into the predeclared promotion test.

## Protocol

| Field | Value |
|---|---|
| WHestBench | `0.14.0` |
| FlopScope | `0.10.0` |
| Runner | official `subprocess` |
| Dataset | `work/whest-full`, split `full` |
| Dataset SHA-256 | `5b00938b6bd809fe80acef08772c5654edf467863225ca9e304b76c779ecf433` |
| Public indices | `0..99` |
| Setup seed | `0` |
| Per-network budget | `272000000000` |
| Execution | two sequential CLI runs; candidate completed before parent started; no parallel scoring |
| Bootstrap | 1,000,000 paired network-cluster resamples; seed `20260806`; percentile CI via `numpy.quantile(method='linear')` |

The earlier 0--19 ledger in `design8_reconstruction/premise_results.json` retained only aggregates and a bootstrap summary. It did not retain the required per-network raw, adjusted, and effective-compute records. Because WHestBench 0.14 has no `--start-index` run option, both branches were rerun consistently on 0--99 rather than splicing incomparable artifacts.

The required resource skill could not run because `psutil` is absent from both the default and WHest virtual environments. The official `whest doctor --format json` fallback confirmed WHestBench 0.14, OpenBLAS with 16 threads, 213.5 GiB free disk, and a writable workspace. The benchmark remained sequential at the scorer level regardless of available cores.

## Official aggregates

| Branch | Raw final MSE | Adjusted score | Mean C | Max C | Failures |
|---|---:|---:|---:|---:|---:|
| Random fold3 32,256 | `3.089512726e-7` | `2.257079776e-7` | `202.281790B` | `250.488783B` | `0/100` |
| Frozen random fold3 39,936 | `1.825637643e-2`* | `1.825634802e-2`* | `248.465717B` | `294.998930B` | `5/100` |

`*` The parent aggregate includes five official failure outputs, which WHestBench sets to zero before scoring. It is a valid competition result but is not a meaningful estimate of the parent's successful-run sampling MSE.

Candidate analytical FLOPs averaged `185.406853B` and peaked at `218.822855B`. Parent analytical FLOPs averaged `229.305186B` and peaked at `270.692930B`; residual-time charging pushed five parent networks over the combined 272B budget.

## Parent failures

All five were `combined_budget_exhausted`; there were no analytical-budget, predict-time, residual-limit, or Python-exception failures.

| Index | MLP | FLOPs | Residual time | Effective C | Budget excess |
|---:|---|---:|---:|---:|---:|
| 1 | `jimmy-brady` | `242.990570B` | `0.294288s` | `272.419410B` | `0.419410B` |
| 39 | `kristina-wilkinson` | `263.101295B` | `0.206192s` | `283.720525B` | `11.720525B` |
| 43 | `elizabeth-hess` | `246.122061B` | `0.273283s` | `273.450381B` | `1.450381B` |
| 74 | `mark-sanchez` | `257.725633B` | `0.183446s` | `276.070234B` | `4.070234B` |
| 80 | `wendy-clayton` | `270.692930B` | `0.243060s` | `294.998930B` | `22.998930B` |

The child completed those same indices legally. No failure was removed, retried, or replaced.

## Paired inference

For network \(i\), the predeclared cluster statistic is

\[
d_i=s_{i,32256}-s_{i,39936},
\]

where each \(s_i\) is WHestBench's official per-network adjusted score, including the failure multiplier and zeroed prediction where applicable. One bootstrap resample draws 100 network indices with replacement and records \(\bar d^*\).

Official uncensored result:

- mean adjusted difference: `-1.825612231e-2`;
- candidate wins: `53/100` networks;
- bootstrap 95% CI: `[-4.017637049e-2, -1.955091686e-3]`;
- `P(bootstrap mean difference < 0) = 0.999650`.

The interval is strictly below zero, satisfying the declared statistical gate. It is very wide because the parent failure penalties are orders of magnitude larger than ordinary successful-network MSEs.

### Both-success descriptive sensitivity

This is reported transparently but was **not** used for promotion and did not replace the official 100-network bootstrap:

| Quantity | Value |
|---|---:|
| Networks where both completed | `95` |
| Candidate adjusted score | `2.282126128e-7` |
| Parent adjusted score | `2.439277675e-7` |
| Mean candidate-minus-parent adjusted difference | `-1.571515473e-8` |
| Relative adjusted change | `-6.4425%` |
| Candidate wins | `48/95` |
| Candidate raw MSE | `3.141091507e-7` |
| Parent raw MSE | `2.738346309e-7` |
| Relative raw change | `+14.7076%` |

Thus the smaller rule gives up raw accuracy, as expected, but more than repays it through lower effective compute on this development slice. The official all-100 promotion additionally captures the larger parent's lack of compute robustness.

## Promotion gate

| Requirement | Result | Pass? |
|---|---|---|
| CI upper endpoint strictly below zero | `-1.955091686e-3` | Yes |
| Candidate failures | `0/100` | Yes |
| Candidate max C safely below 272B | `250.488783B < 258.4B < 272B` | Yes |

**Decision: promote the unchanged 32,256 child over the frozen 39,936 parent.** The parent failures are recorded as comparison outcomes, not added as an unstated condition that the candidate could never satisfy.

This decision does not assert that 32,256 is globally optimal, and it does not license further tuning on indices 0--99. It resolves only the predeclared parent/child comparison.

## Exact commands

The harness ran these commands sequentially from the workspace root with `PYTHONUTF8=1`.

Candidate:

```powershell
'work\whest-v014\Scripts\whest.exe' run --estimator 'work\scorefloor_generation\design8_reconstruction\estimator_random_n32256.py' --dataset 'work\whest-full' --split full --n-mlps 100 --runner subprocess --seed 0 --flop-budget 272000000000 --detail full --format json
```

Frozen parent:

```powershell
'work\whest-v014\Scripts\whest.exe' run --estimator 'work\scorefloor_generation\orthogonal_fold3\estimator_n39936.py' --dataset 'work\whest-full' --split full --n-mlps 100 --runner subprocess --seed 0 --flop-budget 272000000000 --detail full --format json
```

Analysis:

```powershell
work\whest-v014\Scripts\python.exe work\scorefloor_generation\random32256_paired100\analyze.py
```

Candidate elapsed wall time was `510.063s`; parent elapsed wall time was `540.032s`. Both CLI processes returned zero. Empty stderr hashes confirm no CLI warning or traceback output.

## SHA-256 ledger

### Frozen estimator/runtime inputs

```text
b5314e98d1814af6e014b642591b0549b151e0d9b03e99ed9e913d30490bc638  work\scorefloor_generation\design8_reconstruction\estimator_random_n32256.py
92523138da2d00907816eddb05605b8bfe3f6e7588ce63536f73cc115eab4054  work\scorefloor_generation\orthogonal_fold3\estimator_n39936.py
7dbee34ecec4936adc77a232cd7b7ade3dfff6d35282708455bf4450847035d6  work\scorefloor_generation\orthogonal_fold3\orthogonal_fold3.py
505a726f4d6dbdb1946edf7d3806b3f2ee795d06be2cad10a8de0cc58ff04ab7  work\scorefloor_generation\fold3_estimator.py
888a44d9c886df88cf8933398c154e113f530f3dc2705282170820a101dd674a  work\whest-v014\Scripts\whest.exe
```

### Harness and result artifacts

```text
6bffee974dbbf86f32beeb01599ac5c266fcbd7d132b037ca7ed5ca079af0ee5  run_official.py
ad01bc4dfec4bad3e897685fe733561d80dff0c916d981debd5d8063f38e9efa  analyze.py
5fa222d040a6ed6f3f82cadabdae80dbb353826479eaad39ed63acb3e47b6248  run_metadata.json
b7dbd03e498773f45ed873b3f10cae1e93b99bdfb2d87bb506a891ae29dcf88b  candidate_random32256_official100.json
33328e7dd227a71b3232df6f73358effd4a2a4524cf48f332e85bd18da9bb8a9  parent_random39936_official100.json
c63b03a6fc32e38a625ee2af53214df22b5deddf70181c804258d062e5e92c71  paired100_results.json
9ea313d4ce3d685c79d2ca497766e8b6700d0e89412f50fb977c877f355bf457  paired100_results.npz
```

The two stderr logs are empty and both hash to the SHA-256 empty-file digest `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Artifacts

- `paired100_results.json`: protocol, aggregates, bootstrap result, promotion gate, and all 100 per-network raw/adjusted/C/failure records.
- `paired100_results.npz`: paired numerical arrays plus all 1,000,000 bootstrap means.
- `candidate_random32256_official100.json` and `parent_random39936_official100.json`: unmodified official full-detail reports.
- `run_metadata.json`: timestamps, exact argv, source/output hashes, return codes, and sequential-run provenance.
- `run_official.py` and `analyze.py`: reproducible frozen harness and analysis.

Validation confirmed exactly 100 records with minimum index 0 and maximum index 99. Every main NPZ paired vector has length 100, and `bootstrap_means` has length 1,000,000.
