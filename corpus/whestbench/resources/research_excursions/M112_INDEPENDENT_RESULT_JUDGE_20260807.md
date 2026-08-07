# M112 independent result judgment — 2026-08-07

## Verdict: `KILL`

The sole frozen deterministic fixed-bank association diagnostic is killed by its declared screen. This decision neither promotes an estimator nor changes a champion. The connected-field / raw-Frobenius-kernel mechanism remains a nonworking diagnostic component only; it is not an estimator or a promoted candidate.

## Scope and method

I did **not** rerun the analyzer, make a network request, modify the frozen manifest, sentinel, result, or NPZ, or open `m112_results.json`. I read the produced kernel/residual NPZ and loaded only the authorized M111 `raw_outputs` member needed to compute the four denominators. Each trace risk was recomputed as `sum((X - mean_frame(X))^2)/(50 - 1)`, then the ratios and frozen 1.15 charge were derived independently of the result JSON.

Transparency note: the read-only calculation accidentally enumerated source-NPZ member *names* while opening it. It did not index, deserialize, copy, calculate on, or inspect any control/result/metadata values. The calculations below use only `raw_outputs` and the produced `crossfit_residuals`; no control values were loaded.

## Recomputed screen

| Network | Base trace covariance | Residual trace covariance | Raw ratio | Charged ratio (×1.15) |
|---:|---:|---:|---:|---:|
| 0 | 0.005128449927511058 | 0.005182415098499435 | 1.0105227060322626 | 1.1621011119371019 |
| 1 | 0.011321033568427046 | 0.011442082918153865 | 1.0106924291845940 | 1.1622962935622830 |
| 2 | 0.009735452898612728 | 0.009786955625692156 | 1.0052902240518022 | 1.1560837576595724 |
| 3 | 0.013778777396519722 | 0.013811691802851630 | 1.0023887755339034 | 1.1527470918639888 |

* Raw geometric mean: `1.0072173212283930`.
* Raw pooled ratio: `1.0064916803148687`.
* Charged geometric mean: `1.1582999194126520`.
* Charged pooled ratio: `1.1574654323620990`.

The proposed assertion that charged values are under `1.15` is false: every charged network ratio is above `1.15` (and above `1.0`). The source-defined classification therefore has exactly these three reasons, in this order:

1. `one_or_more_charged_network_ratios_at_least_1`
2. `charged_geometric_mean_ratio_above_0.90`
3. `charged_pooled_ratio_at_least_1`

`classify_screen` consequently returns `KILL`; no PASS-only M112b follow-up is authorized, and `champion_mutation_authorized` is statically `False`.

## Frozen binding and artifact integrity

All nine current source hashes equal the frozen manifest entries. The frozen manifest SHA-256 is `00cdfe590f9f7af40f972ce94ad29bca1bf14df1f88637d2ab51d4f87d1f808c`. The manifested opaque M111 archive binding is `4f82e547901ecba643ee648c74656818c429ca38a9d9290fa907c8db26fd752e`.

| Artifact | SHA-256 |
|---|---|
| Frozen manifest | `00cdfe590f9f7af40f972ce94ad29bca1bf14df1f88637d2ab51d4f87d1f808c` |
| Durable one-shot sentinel | `f13210b90093485b5a830c3cef3d1052e852f98c496e35bd9f915f42929614ea` |
| Produced kernel/residual NPZ | `eaa2a34d543d33fbeb7c694eab8a12ac389a433ceb34b5b67c7c27c0106bdad1` |
| Result JSON (hash only; contents not opened) | `66580ef8348e8c0ab226fbc6f61fd8f2359ec6a5e99bf5db712bb9a0bf23886a` |
| Raw kernel array C-byte payload | `ad2a83724107b7c564e64110168c80abd6bcd338992db1fbe3546ffbd71eb175` |
| Residual array C-byte payload | `22ad6651fb89c07fc5c2f9293103816ded764425dc060f5e9678b5e1ecebf231` |

The produced NPZ contains `raw_frobenius_kernels` (`float64`, `(4, 50, 50)`) and `crossfit_residuals` (`float64`, `(4, 50, 256)`).

## One-shot status and non-promotion

The sole canonical output directory contains the sentinel, the produced NPZ, and the result file, with no failure receipt or second output artifact. The sentinel says `m112_reuse_diagnostic_one_shot_consumed_no_retry` and binds the same manifest, input, theory, audit, runtime, cost, and association schedule as the frozen manifest. Source inspection confirms the sentinel is created with `O_CREAT | O_EXCL` before array loading, alternate output directories are rejected, and only temporary artifact files—not the sentinel—are ever unlinked. The existing sentinel therefore permanently prevents a supported retry, whether the original path succeeded or failed.

No champion mutation was performed or is authorized by this diagnostic. The fixed-bank conditional-unbiasedness claim remains retracted, independently of this adverse screen result.
