# Factored Cholesky propagation — KILLED at its cheapest gate, and the real
# mechanism identified

**Status: `KILL_NO_GAIN` FIRED. The mutation is dead.** In exchange it produced
something better than a pass: the actual cause of the SPD loss, which is **not**
what this corpus (and I) had recorded.

## Harness admissibility

The predeclared second signal: the dense column must reproduce
`gm_spd_width_scaling`'s `ell*` for the same cell. **4/4 known cells
REPRODUCED** — `(256,0)→12`, `(256,1)→10`, `(192,0)→12`, `(128,0)→18`.

## The three predeclared gates

| gate | result |
|---|---|
| `KILL_DIVERGENCE` | **not fired** — worst relative gap `2.6e-15` vs the `1e-9` bound. Dense and Gram compute the same object to machine precision, so the comparison is admissible. |
| `KILL_UPSTREAM` | **not fired** — `V'` is never non-PSD *at or before* the dense trip. It goes negative one to two layers *after* (dense 12 → `V'` 13; dense 10 → `V'` 12), which is the downstream consequence of feeding `relu_moments` an already-degenerate `C`. |
| `KILL_NO_GAIN` | **FIRED — 2/2 at width 256, and in fact 6/6 across all cells.** |

## The decisive result

`ell*` for the two paths, identical in every cell:

| width | rep | dense `ell*` | **Gram `ell*`** | `V'` non-PSD | Cholesky refuses | max rel gap |
|---:|---:|---:|---:|---:|---:|---:|
| 128 | 0 | 18 | **18** | — | — | 2.6e-15 |
| 128 | 1 | 18 | **18** | 21 | 21 | 2.0e-15 |
| 192 | 0 | 12 | **12** | 14 | 14 | 1.6e-15 |
| 192 | 1 | 14 | **14** | 18 | 18 | 1.9e-15 |
| 256 | 0 | 12 | **12** | 13 | 13 | 2.0e-15 |
| 256 | 1 | 10 | **10** | 12 | 12 | 2.0e-15 |

**Making `C` positive semidefinite by construction changes nothing about when it
trips the floor.** Not one layer, in any cell.

The reason, in hindsight, is elementary and I should have seen it before
proposing the mutation: a Gram matrix `M^T M` is guaranteed PSD, so its `lambda_min`
cannot go *negative* — but nothing stops `lambda_min` from going *small*. The gate
is `min eig <= 1e-12`, a **floor** test, not a sign test. The Gram form defends
against the wrong failure.

## The real mechanism — correcting a claim in this corpus

The width-256 trajectory, `lambda_min(C)` per layer:

| layer | 1 | 2 | 4 | 6 | 8 | 10 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `lambda_min` (rep 0) | 5.00e-5 | 1.07e-7 | 2.82e-7 | 2.00e-8 | 5.35e-12 | 2.33e-11 | **2.66e-13** |
| `lambda_max` | 7.66 | 7.67 | 9.36 | 7.82 | 8.00 | 7.42 | 8.21 |

`lambda_max` stays `O(8)` throughout while `lambda_min` collapses. **Median
per-layer ratio `lambda_min(l+1)/lambda_min(l)` = 0.0814 (rep 0) and 0.1202
(rep 1)** — roughly one order of magnitude lost per layer, geometrically.

Arithmetic that closes the question:

- **Lowering the `1e-12` floor by one decade buys ~0.92 layers** (rep 0) or
  ~1.09 (rep 1).
- **Reaching layer 32 from layer 12 needs ~21.8 decades of floor.**
- That implies `lambda_min ~ 1e-34` against `lambda_max ~ 8` at layer 32, i.e. a
  condition number near **`1e35`**. float64 carries ~16 significant digits. **The
  layer-32 state is not representable in float64 at all**, by roughly nineteen
  orders of magnitude.

### What this corrects

`gm_spd_width_scaling/REPORT.md` and `RECURSION_PACKET_GEN7 section 3.4` state
that at production width "the indefiniteness is round-off in the dense entrywise
representation." **That inference was wrong, and this experiment is the direct
test of it.**

The evidence that misled it was real but circumstantial: at the failure layer
`|lambda_min| / (eps * n * lambda_max)` falls to `O(1)` and below, which shows the
eigenvalue is *indistinguishable from* round-off. I read that as round-off
*causing* the trip. It does not. Remove the assembly error entirely — which the
Gram form does — and the trip layer is unchanged in 6 of 6 cells.

**Corrected statement: `lambda_min` decays geometrically with depth as a property
of the propagated covariance itself. Round-off is concurrent, not causal.** The
assembly-scale ratio remains a correct measurement; only the causal reading was
wrong.

### The phenomenon has a name, and this corpus already sourced it

This is the covariance-spectrum shadow of **depth degeneracy**: Jakub & Nica,
*Vanishing Angles in Fully Connected ReLU Networks on Initialization*
(arXiv:2302.09712, JMLR 25:239), already listed in
`sources/research_physics_depth_finitewidth_20260810.md` as "exact per-layer
angle-contraction recursion at finite width, **exponential** decay where infinite
width predicts polynomial."

Exponential angle contraction means neuron correlations approach 1 with depth —
consistent with the measured `max |rho| = 0.942` and `0.971` at layer 32 — and a
correlation matrix whose off-diagonals approach 1 is one whose smallest
eigenvalue approaches 0. The geometric `lambda_min` collapse measured here is
that theorem expressed in the spectrum, and the finite-width **exponential** rate
is exactly why depth 32 is unreachable while depth 6 was fine.

## What is now closed, and what is not

**Closed.**
- Factored/Gram propagation does not extend reach. Measured, 6/6.
- Lowering the variance floor does not extend reach: ~1 layer per decade.
- Higher float precision is now **quantified rather than speculated**: reaching
  layer 32 needs ~35 significant digits, so float128 (~34 digits) is marginal at
  best and `mpmath` at `dps >= 50` would be required — an enormous cost against a
  closure already measured 311x from competitive as a predictor (`t2`).

**Not closed.**
- This says nothing about G2 (the four-point vertex / information absence). That
  kill stands on separate evidence.
- No estimator, variance, MSE, or score claim. Even unlimited precision would
  leave the `t2` 311x gap and the 1.40x analytic-control cap (R^2 = 0.287)
  untouched. **The G7 obstruction being deeper does not make the score arm
  better.**
- The measurement is float64, He-Gaussian init, depth 32, widths 128–256. The
  degeneracy literature predicts the rate depends on architecture and
  initialization; other regimes are untested here.

## Consequence for the write-up

The Algorithmic Contribution claim strengthens and simplifies. It was:
*"the exact Gaussian closure is inaccurate (311x) and, at production width,
undefined."* It becomes:

> The exact Gaussian closure is **structurally unreachable** at production depth.
> Its propagated covariance loses roughly one order of magnitude of `lambda_min`
> per layer — the spectral form of finite-width depth degeneracy — so the
> layer-32 state at width 256 carries a condition number near `1e35` and is not
> representable in double precision. This is a property of the object, not of the
> implementation: it survives exact-PSD-by-construction propagation, and no
> floor, representation, or double-precision arithmetic reaches it.

A negative result with a named mechanism, a measured rate, a published theorem
behind it, and a falsified alternative explanation — including one this corpus
had itself recorded.

## Reproduction

```bash
cd corpus/whestbench/experiments/gm_factored_cholesky
python3 run_factored_diagnosis.py --widths 128,192,256 --reps 2
```

Requires the frozen M179/M200 modules (they arrive with PR #1; read read-only,
never vendored). Synthetic He-Gaussian weights via `m200.generated_weights` with
the `gm_m179_m199` `cell_seed` scheme. No truth, scorer, holdout, private data,
leaderboard, submission, network, or champion access. No clip, floor, ridge, or
eigenvalue truncation anywhere.
