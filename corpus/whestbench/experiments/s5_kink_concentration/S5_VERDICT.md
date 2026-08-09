# S5 VERDICT — Landau kink-concentration premise

Ledger id: `s5_landau_kink_concentration_premise` · Date: 2026-08-09
Harness: `run_s5.py` · Results: `s5_results.json` · Per-net arrays: `s5_net{101,202,303}_arrays.npz`

## VERDICT: KILL

The champion estimator's per-direction residual energy does NOT concentrate
near the ReLU kink set. Both predeclared kill criteria fired independently:

1. **Pooled near/far decile ratio < 1.5 on every gate combo** — the pooled
   ratios are 0.978 (d1/global), 0.978 (d1/frame), 1.006 (dmin/global),
   1.007 (dmin/frame). Not merely below 1.5: statistically indistinguishable
   from 1.0 (no concentration in either direction).
2. **Sign-inconsistent across nets on every gate combo** — per-net Spearman
   rhos of |r|² vs the distance observables: d1/global {+0.0034, −0.0001,
   −0.0023}, dmin/global {−0.0043, +0.0016, −0.0019} (frame versions nearly
   identical). All |rho| ≲ 1 s.e. under the null (1/√64512 ≈ 0.0039) and the
   signs flip between nets.

No combo came near the PASS bar (ratio ≥ 3 with strict monotone deciles on
≥ 2 of 3 nets): per-net gate-combo ratios span 0.954–1.023 with 3–6
monotonicity violations each; zero nets passed on any combo.

**Consequence per the predeclaration: kink-localized frames are NOT a legal
reopen candidate against the M191 harmonic-dispersion closure. The idea dies
here.**

## Deviations / operationalizations (recorded loudly)

1. **kcount neighbor degeneracy.** "Nearest design neighbor within the same
   frame" is a 510-way tie: all non-antipodal frame-mates of a phased-Hadamard
   row (256 rows × both signs, minus u and −u) are exactly orthogonal, hence
   exactly equidistant at 90°. Operationalized as the MINIMUM Hamming distance
   between layer-1 activation sign patterns over all 510 equidistant
   frame-mates (sign(0) counted +). kcount is diagnostic-only per the gates
   (which name d1/dmin), so this decision is not verdict-bearing.
2. **"Monotone decile trend"** operationalized as strictly decreasing decile
   mean energies from near to far (all 9 successive differences); violation
   counts also reported.
3. **"Sign-inconsistent across nets"** operationalized as the per-net
   direction-level Spearman rho signs not being shared by all 3 nets.
4. **No compute reduction taken** — the full 64,512 directions per net ran
   (~16 s/net); the 16,384 fallback was unnecessary.
5. The classical no-ties Spearman formula cross-check auto-skipped: antipodal
   doubling makes every d1 value an exact tie pair (d1(−u) = d1(u); tie count
   32,256 = n_base, expected). The scipy two-way agreement served as the
   second Spearman signal instead.

## Exact normalizations

- Direction set: frozen Kerdock v3 base (126 phased-Hadamard frames × 256
  rows = 32,256 at exact radius mean_chi(256) = 15.98438266660853), rotated by
  the per-net Haar rotation (seed 900000 + net_seed·1000 + 0, the P2 lineage
  formula, r=0), antipodally doubled → 64,512.
- Forward: n8a/estimator association, pre1 = kerdock @ (Rᵀ W₀); layers 1..31
  post-ReLU matmuls; y(u) = final post-ReLU 256-vector; ybar(u) = its neuron
  mean.
- Residuals: r_global(u) = ybar(u) − mean_design(ybar); r_frame(u) = ybar(u) −
  (512-member antipodal frame mean). Energy = r².
- **d1(u)** = min over layer-1 neurons j of |pre1(u)_j| / ‖(RᵀW₀)[:,j]‖₂ /
  mean_chi — the sine-like angular margin to the nearest first-layer boundary
  (all directions share the radius, so the division by mean_chi is a global
  scale).
- **dmin(u)** = min over layers l=1..32 of the layer-l relative margin
  min_j |pre_l(u)_j| / ‖W_l[:,j]‖₂ / ‖a_{l−1}(u)‖₂, where a_{l−1} is the
  post-ReLU input to layer l (Euclidean point-to-hyperplane distance in the
  layer's own input space, scaled by the incoming activation norm). Layer-1
  term equals d1. Zero-activation rows would get margin 0; none occurred
  (dead_rows_seen = 0 on all nets).
- Deciles: equal-count rank bins. Near = smallest-distance decile for d1/dmin,
  highest-count decile for kcount. Ratio = mean energy(near)/mean energy(far).
- Pooled: per-net energies normalized by net-mean energy, deciles within net,
  pooled decile mean = mean over nets; pooled rho on concatenated
  (observable, normalized energy).

## Numbers (near/far ratio · strict monotone · rho)

| combo | net 101 | net 202 | net 303 | pooled |
|---|---|---|---|---|
| d1/global | 1.014 · F · +0.0034 | 0.954 · F · −0.0001 | 0.967 · F · −0.0023 | **0.978** (rho +0.0003) |
| d1/frame | 1.014 · F · +0.0036 | 0.954 · F · +0.0002 | 0.965 · F · −0.0022 | **0.978** (rho +0.0006) |
| dmin/global | 0.977 · F · −0.0043 | 1.021 · F · +0.0016 | 1.019 · F · −0.0019 | **1.006** (rho −0.0015) |
| dmin/frame | 0.978 · F · −0.0041 | 1.023 · F · +0.0017 | 1.019 · F · −0.0018 | **1.007** (rho −0.0014) |
| kcount (diag) | ~1.00 | ~1.00 | ~1.00 | 0.999 (rho +0.0047, signs consistent but negligible) |

Full-256-vector residual energy diagnostic (net 101): d1 ratio 1.008,
dmin 0.988, kcount 0.966 — same null.

## Verification (two-signal)

- **Two-path design mean**: my forward (pre1 = kerdock @ (RᵀW₀)) vs n8a's own
  `antipodal_forward_mean` with the other association ((kerdock Rᵀ) @ W₀) —
  max relative difference 7.2e−9 across nets.
- **Spearman two-way**: my rank implementation vs `scipy.stats.spearmanr` —
  agreement to ≤ 9e−19 on all three observables (net 101, global).
- **Bitwise repeats**: (a) d1/global decile tables recomputed from the saved
  npz arrays match exactly; (b) the entire pipeline rerun end-to-end
  reproduced every table, pooled entry, and the verdict bit-identically
  (first-run copy kept as `s5_results_run1.json.bak`).
- **Positive control** (diagnostic, circular by construction): binning |r|² by
  deciles of |r| itself yields ratios 849–883 with strict monotonicity on all
  3 nets — the decile machinery detects real structure when present, so the
  kink-observable null is not a broken-binning artifact.

## Limitations

- Observables are per-layer local margins, not geodesic distance to the full
  kink set on the sphere; dmin is a min-over-layers proxy. A concentration
  effect living in a functional of the kink set not captured by min-margins
  would be missed — but d1 (the exact first-layer angular margin, spanning
  ~4 decades: 1e−7 to 3.7e−3) shows the same null, so the simplest form of
  the premise is directly refuted.
- kcount has narrow dynamic range at the 90° neighbor scale (values 84–112,
  concentrated near 104): first-layer kink density at that scale is nearly
  uniform across the design, limiting its resolving power (diagnostic-only).
- One rotation per net (r=0, predeclared), 3 nets, single
  width/depth (256/32). Residual is the design-mean fluctuation proxy
  (whose design-sampled variance is the estimator variance), not a
  truth-referenced error — as specified by the task.
- Rho magnitudes are bounded by sampling noise at n = 64,512: the data
  constrain any true |rho| to ≲ 0.01 — two orders below what a 3x decile
  ratio would require.
