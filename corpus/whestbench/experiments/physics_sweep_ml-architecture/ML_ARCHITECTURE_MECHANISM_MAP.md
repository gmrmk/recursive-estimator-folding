# ml-architecture cluster — mechanism map (read-only sweep, 2026-08-10)

Firewall: no estimator executed, no measurement taken, no git, no network. Every
number below is quoted from a committed artifact and cited to it.

## Verdict table

| # | concept | sharpest mechanism for THIS problem | verdict | evidence |
|---|---------|-------------------------------------|---------|----------|
| 1 | ResNet / residual connections | ReLU(z)=z/2+|z|/2; estimate the odd half by its exact zero mean, sample only the even half | ALREADY-KILLED (as a variance lever) | `s16_residual_norm_decomposition_confirm`: MSE ratio vs antipodal champion **1.000000**, max final-vector dev **0.0**, layer-1 identity bit-exact on 8.26M entries x3 nets |
| 2 | ResNet, Form 1 (near-identity perturbation) | treat y_l = y_{l-1} + F_l and expand in small F | ALREADY-KILLED | same record: per-layer R_l = mean\|\|F_l\|\|/mean\|\|y_l\|\| = 1.108 / 1.162 / 1.231, all > 1 — no near-identity structure |
| 3 | LayerNorm | positive homogeneity f(u)=\|\|u\|\| f(u/\|\|u\|\|) -> condition the radius exactly at E[chi_256] | ALREADY-IN-CHAMPION | `kerdock_v3_estimator.py` `MEAN_CHI_256 = 15.98438266660852747`, `radial_conditioning = True`; `wc1_winner_ablation_map` scores it **2.141x** MSE if removed (CI [1.509, 3.042]) |
| 4 | CNN pooling | 4x4 block-average each 256x256 weight matrix -> width-64 surrogate as an MFMC low-fidelity level | ALREADY-KILLED | `s13_width_pooled_mfmc_premise`: geomean gain **0.9552x** [0.9520, 0.9589]; rho 0.071-0.176 vs 0.489 required; width-128 arm 0.8415x -> **no sweet spot on the width axis at any width** |
| 5 | Self-attention (learned closure over neurons) | shared multi-head transport-equivariant message passing to predict the closure defect | ALREADY-KILLED | m92 / m96 / m97 / m98 / m99 / m136, all `killed_protocol` or `killed_pretarget` |
| 6 | Self-attention (as direction reweighting) | softmax/kernel-weighted combination of the 64,512 per-direction estimates | FORBIDDEN-BY-THEOREM | design is a group orbit -> LP-optimal weights are uniform (F4, kriging/BLUE dead by symmetry); S7 min inter-direction angle arccos(1/16) = **86.42 deg** makes the kernel ~identity; measured instances m192/m193/m194/m195/m197/s2 all killed |
| 7 | Multi-head latent attention (MLA) | low-rank joint compression of the propagated 256-dim state / of the degree-4 error operator | FORBIDDEN-BY-THEOREM | S6 maximal flatness (participation rank ~32,266 ~ N; top-100 eigenvalues 0.32% of tr(D^2)); measured instances `weight_identified_latent_factor`, `latent_factor_rank3`, `m135_conditional_lowrank_source` killed |
| 8 | KV-cache: weight-only precompute shared across directions | cache the composed linear operator on certain-on runs and reuse it for every direction | ALREADY-KILLED at the extension, ALREADY-IN-CHAMPION at the terminal 3 layers | `m184_trichotomy_upward_g0`: **0.00%** billed reduction on all 3 nets; certain-on count is **0 at layers 1-9** and peaks at 39/~185 at layer 28, 2.3x short of break-even (~85-95); holds under illegally lax alpha in {5,4,3} |
| 9 | KV-cache: cell-hit reuse across directions | two directions in the same ReLU cell share the composed affine map | ALREADY-KILLED (hit rate exactly 0) | `s18_cell_membership_probe`: all 64,512 directions occupy **64,512 distinct singleton first-layer cells**; corroborated by S7's 86.42-deg minimum angle |
| 10 | KV-cache: arithmetic subexpression reuse down the direction axis | Strassen/Winograd recursion over the 64,512-row batch | ALREADY-IN-CHAMPION at level 1; deeper ALREADY-KILLED | `row_blocked_winograd_production` promoted (r_prod = 7,427,768,320/8,439,201,792 = **0.88015058**); `uf1_strassen_flop_only_accounting` killed — integrated optimum **depth 2 at 1.057x**, depth 4 = **0.638x** (net loss, +1.26 s/MLP residual) |
| 11 | KV-cache: antipodal even/odd share at the first deep hook | see below | **UNTESTED** | not present in `fold3_estimator.py`; not in the 265-record ledger |
| 12 | K-means on first-layer cells | cluster sign patterns, share one affine map per cluster | FORBIDDEN-BY-MEASUREMENT | S18 singletons: cluster == point, zero compression; S18 combinatorial covariates measured **2.371e-5 < 2.63e-5** noise bar, inside its own permutation null |
| 13 | K-means on weight/neuron structure | cluster the 256 columns per layer, share the computation (a learned width surrogate) | FORBIDDEN-BY-THEOREM | strictly a better-chosen point on the axis S13 closed at the axis level: no intermediate width meets the required-rho curve; the kill mechanism (exact-weight fingerprint, S8 0.87/layer, S7 coherence cone c32 = 0.9747) is grouping-independent |
| 14 | Single-core quantised recursive inference brick | int8/fp16 activations+weights, bit-serial kernel, off-meter native backend | FORBIDDEN-BY-RULE + ALREADY-KILLED, three independent ways | (a) `COMPRESSION_SCORE_CALCULUS_20260806.md:187` — FlopScope charges float16, int8 and float32 **at the same arithmetic rate**; (b) `n8b_disclosed_native_backend`: one-core-pinned sustained **81.6-93.9 GFLOP/s < lambda = 1e11**, a 0.94x regression; (c) `m183_f32_hotpath_falsifier`: f64 lane already **0.00%** of 1.5803e11 — no precision headroom exists |
| 15 | Layer folding | dead columns vanish, always-on columns compose algebraically into the next weight | ALREADY-IN-CHAMPION | `fold3_estimator.py` `folded30_to31` / `folded29_to31_on`; WC1: fold exactly MSE-neutral (1.00003 [0.9992, 1.0010]), saves **4.8% B**; prune saves **25.1% B** |

## The one untested survivor (#11), specified

The champion's antipodal doubling stacks `ReLU(P)` over `ReLU(-P)` where
`P = MEAN_CHI_256 * H diag(p_s) W1'` is the 32,256 x 256 phased-WHT first
preactivation (`fold3_estimator.py:78-81`). The very first deep hook then bills a
full **64,512 x 256 @ 256 x 256** product. But

    ReLU(P) @ W2  = ( |P| @ W2 + P @ W2 ) / 2
    ReLU(-P) @ W2 = ( |P| @ W2 - P @ W2 ) / 2

so the two halves share one value, `|P| @ W2`, and the second term is
weight-only-composable: `P @ W2 = MEAN_CHI_256 * H diag(p_s) (W1' W2)`, i.e. one
256^3 weight product hoisted out of the direction axis plus 126 phased WHTs.
This is the KV-cache analogue in its exact form: the shared "key/value" is
`W1' W2` and `|P| @ W2`, and the antipodal pair is the two "queries" that reuse it.

Static cost, from committed numbers only:

- present first hook, direct: 64512 * 256 * 511 = **8,439,201,792** FLOPs
  (`uf1` price table, exact; equals 5.198% of seed-11's direct deep-hook bill,
  `uf1_attack_eligibility/attack_stage3.json`)
- replacement: `|P| @ W2` at 32,256 rows = 4,219,600,896; plus `W1' W2` at
  256*256*511 = 33,489,408; plus 126 phased WHTs ~ 7.4e7; plus one add, one
  subtract and one scale over 2 x 32,256 x 256 ~ 3.3e7
- net direct saving ~ **4.08e9**; Winograd-charged (hook 1 is k-even, therefore
  eligible; r = 0.88015058) saving ~ **3.56e9**
- against seed-11 `total_charged` **167,353,743,187**: **~2.1% of C**
- C/B 0.650 -> ~0.636; adjusted 1.832e-7 -> ~1.79e-7, i.e. **~1.02x**

Why it is not forbidden: it touches neither god node A (it changes no estimator
output in exact arithmetic, so the speckle is untouched and the design is
unchanged) nor god node B (the 2-design is unchanged). It lives under god node C
(the FLOP meter), which F6 declares exhausted — but F6's evidence (M183 0.00%,
M184 0.00%, N8b 0.94e11, UF1 1.057x) is about precision, mid-layer composition,
off-meter execution and Strassen depth. None of the four evaluated the
antipodal even/odd share, and the ledger contains no record of it.

Why the magnitude is honestly small: it applies to exactly one hook. The
antipodal relation is destroyed by the layer-2 ReLU, so there is no second layer
to harvest. 1.02x is below UF1's own already-rejected 1.057x integrated optimum.

Cheapest falsifier (response-free, no scoring data, no estimator run):
a static FLOP recount. Instrument the frozen v3 `predict` under a
`BudgetContext` on 5 generated nets (seeds 11-15, the UF1 panel), take the
metered `op_log`, and recompute the bill with hook 1 replaced by the factored
schedule using the frozen price table (matmul = m*n*(2k-1); add/sub/mul/copyto =
1/element). GATE: promote to a parity arm only if the recount shows >= 2.0%
reduction in `total_charged` on all 5 seeds AND the fp32 parity of the factored
route against the direct route is <= 1e-5 relative (the M71/M72 lineage gate;
those measured 4.301e-8 and 5.114e-8). KILL if < 1.5% on any seed, or if parity
exceeds 1e-5 — the cancellation `(|P|@W2 - P@W2)/2` reconstructs rows that are
exactly zero in the direct route, so parity is the real risk, not the arithmetic.

## What did NOT map to a mechanism

Nothing in this cluster mapped to "no precise mechanism" — every concept had a
writable operator. The cluster's honest yield is 13 kills, 1 already-in-champion
family, and 1 small untested cost lever.
