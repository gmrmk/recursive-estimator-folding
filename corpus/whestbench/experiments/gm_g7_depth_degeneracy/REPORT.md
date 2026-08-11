# G7 deepened — a width-scaling law for the closure's spectral collapse

**Status: MEASURED. Two of four predeclared predictions supported, one refuted
in the informative direction, one falsified outright — and the falsified one
corrects a mechanism claim I made in this corpus two commits ago.**

Second signal: the He arm at width 256 reproduces `ℓ* = 12` and `10` from
`diag256.log`. Harness admissible.

---

## Headline

| result | value |
|---|---|
| `λ_min` decay, He, width 256 | **0.719 decades per layer** (R² 0.76–0.88) |
| decay rate vs width, He | **∝ n^0.639**, R² = **0.9917** |
| decay rate vs width, Haar-orthogonal | **∝ n^0.927**, R² = **0.9885** |
| `κ` at layer 32, width 256, He (fitted extrapolation) | **≈ 10^27.9** |
| significant digits required at depth 32 | **≈ 28** (float64 carries ~16) |
| effective rank, width 256 | `155.3/256` (60.7%) at layer 1 → `39.5/256` (15.4%) at layer 12 |
| mean \|ρ\| at the trip layer | **0.16** — nowhere near 1 |

---

## P2 — the decay rate is width-dependent, and it is a clean power law

Fitted by least squares on `log10 λ_min` vs layer over the healthy prefix
(3 replicates per cell):

| width | 32 | 64 | 128 | 256 |
|---|---:|---:|---:|---:|
| He, decades/layer | 0.185 | 0.289 | 0.410 | **0.719** |
| Haar-orthogonal | 0.164 | 0.312 | 0.694 | **1.074** |

```
He   :  rate ∝ n^0.639   (R² = 0.9917)
Orth :  rate ∝ n^0.927   (R² = 0.9885)
```

**P2 supported.** The competing account — that the rate is width-independent and
`ℓ*(n)` falls only because `λ_min` starts lower at larger `n` — is refuted: the
rate itself scales, over an 8× width range, with R² > 0.98 on both arms.

## P3 — required precision is linear in depth, and now has a number

`log10 κ` is linear in layer with median R² 0.83 (He, width 256) and 0.89
(orthogonal). Cross-check at the trip layer of the He/256/rep-0 cell:
`λ_min = 2.6552e-13`, `λ_max = 8.213`, so `log10 κ = 13.49`; adding the remaining
20 layers at 0.7188 decades gives **27.9 at depth 32**, matching the independent
regression extrapolation of **27.8**.

**~28 significant digits are required to represent the layer-32 state at width
256.** float64 carries ~16. This supersedes the earlier "~35 digits / `1e35`"
figure, which came from the unstable estimator described below.

## P4 — REFUTED, and this is the most valuable result here

Haar-orthogonal initialization at matched scale does **not** rescue the collapse.

| width | He trips | Orth trips | He rate | Orth rate |
|---:|---|---|---:|---:|
| 32 | none, none, none | none, none, none | 0.185 | 0.164 |
| 64 | 27, 12, 22 | 29, 23, 30 | 0.289 | 0.312 |
| 128 | 18, 18, 12 | 16, 12, 14 | 0.410 | **0.694** |
| 256 | 12, 10, 11 | 13, 11, 11 | 0.719 | **1.074** |

At production width orthogonal init is **worse**, decaying at `n^0.927` against
He's `n^0.639`.

The predeclaration stated the two readings in advance: if orthogonal init
survives, the obstruction belongs to the Gaussian ensemble (narrow); if it also
collapses, the obstruction belongs to **ReLU composition itself** (general and
stronger). The measurement gives the second.

**Dynamical isometry in the weights does not protect the propagated
second-moment state.** Preserving the weight spectrum is irrelevant, because the
nonlinearity — not the weight ensemble — is what destroys the covariance
spectrum. That generalizes G7 well past the competition's He-initialized
networks.

## P1 — FALSIFIED, and it corrects a claim I made two commits ago

Prediction: `λ_min/λ_max` tracks the equicorrelation value
`(1−ρ̄)/(1+(n−1)ρ̄)` within 10×.

**Result: 0 of 24 cells. Median drift 6.4e6×.** The equicorrelation model is not
merely imprecise here, it is the wrong object by six orders of magnitude.

The reason is visible in the trajectory (He, width 256, layer → effective rank,
mean\|ρ\|, max\|ρ\|):

| layer | 1 | 4 | 8 | 12 |
|---|---:|---:|---:|---:|
| effective rank (of 256) | 155.3 | 85.5 | 53.7 | **39.5** |
| mean \|ρ\| | 0.0498 | 0.0929 | 0.1289 | **0.1596** |
| max \|ρ\| | 0.279 | 0.503 | 0.625 | **0.673** |

**Mean correlation barely moves — 0.05 to 0.16 — while the effective rank falls
from 60.7% of the dimension to 15.4%.** This is not "all the angles vanish
together." It is **spectral concentration**: the covariance mass migrates into
progressively fewer directions, leaving an ever-longer tail of near-null ones.
Effective rank halves roughly every **6.6 layers**, while `λ_min` falls
**0.72 decades per layer** — so the spectrum's *dynamic range* explodes far
faster than its bulk concentrates. That gap is the whole phenomenon.

### The correction

`gm_factored_cholesky/REPORT.md` (commit `97a7228`) states this is "the spectral
form of finite-width depth degeneracy," citing exponential angle contraction and
"the measured `max |ρ| = 0.942` and `0.971` at layer 32."

**Those correlation values were measured *after* the recurrence had already gone
non-PSD and been allowed to continue.** They are downstream of the failure, not
evidence for its cause. At the actual trip layer, `max |ρ| = 0.673` and
`mean |ρ| = 0.16`. **I cited post-failure state as a pre-failure mechanism.**

Corrected attribution: the collapse is **progressive rank concentration of the
propagated covariance under ReLU composition**, at a width-scaling rate. The
Jakub & Nica angle-contraction result remains a genuine neighbour in the
literature and the phenomena are plausibly related, but **this corpus has not
measured that link, and P1 is direct evidence against the naive form of it.** Do
not cite the connection as established.

### Estimator correction

The `0.0814` / `0.1202` "median per-layer ratio" figures in
`gm_factored_cholesky/REPORT.md` came from a median of consecutive ratios. That
estimator is unstable: `λ_min` is non-monotone layer to layer (it bounces one to
two orders), so the same cell type gave `0.10`, `0.90`, `0.12` across three
replicates. All rates in this report are **least-squares fits of `log10 λ_min` on
layer**, which use every point and report R². The median-ratio figures are
superseded.

---

## What this licenses for the paper

A negative result with a **measured scaling law**, which is rarer than a negative
result with an anecdote:

> The exact Gaussian closure is structurally unreachable at production depth. Its
> propagated covariance loses `λ_min` at **0.719 decades per layer** at width
> 256, a rate scaling as **n^0.639** across an 8× width range (R² = 0.992), so the
> depth-32 state carries `κ ≈ 10^28` and requires ~28 significant digits against
> float64's ~16. The mechanism is progressive **rank concentration** — effective
> rank falls from 61% to 15% of the dimension by layer 12 while mean correlation
> only reaches 0.16 — and it is a property of **ReLU composition, not of the
> weight ensemble**: Haar-orthogonal initialization at matched scale does not
> rescue it and at width 256 is worse (`n^0.927`).

Three independent routes are now closed with numbers: representation
(`gm_factored_cholesky`, 6/6 unchanged), floor lowering (~1 layer/decade), and
precision (~28 digits, quantified rather than extrapolated from a bad estimator).

## What this does not license

- **No score claim.** Unlimited precision leaves `t2`'s 311× and the 1.40×
  analytic-control cap untouched. A deeper G7 is a better paper, not a better
  score.
- **No claim about the training or generalization literature.** This measures one
  specific object — the zero-order full-covariance recurrence's pre-ReLU
  covariance — at initialization, in float64, depth 32, widths 32–256, two
  initializations, 3 replicates each. The width exponents are fitted on **four**
  width points per arm; they are a strong regularity over that range, not an
  asymptotic theorem.
- **No established link to the angle-contraction literature** (see P1).
- The orthogonal arm is a **mechanism diagnostic**. The competition's networks are
  He-Gaussian and no result from that arm bears on any score, variance, or
  estimator statement.

## Reproduction

```bash
cd corpus/whestbench/experiments/gm_g7_depth_degeneracy
python3 run_degeneracy.py --widths 32,64,128,256 --reps 3 --workers 4
python3 analyze_degeneracy.py
```

Requires the frozen M179/M200 modules (arrive with PR #1; read read-only, never
vendored). Synthetic weights only; He arm via `m200.generated_weights` with the
`gm_m179_m199` `cell_seed` scheme. No clip, floor, ridge, or eigenvalue
truncation. No truth, scorer, holdout, private data, leaderboard, submission, or
champion access.
