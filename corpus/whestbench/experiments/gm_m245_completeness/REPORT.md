# M245 completeness — no orthogonal function found, and two audit numbers settled

**Status: the predeclared falsifier did NOT succeed. No function orthogonal to
the span was found at any tested `alpha`. This supports density; it does not
prove it.** Two separate audit items are closed as a by-product.

Answers the audit's open item:

> **Completeness: OPEN.** Finite SPD proves linear independence, not `L²`
> closure … Parseval's identity cannot currently be globally invoked.
> *Cheapest falsifier:* construct an explicit, non-zero piecewise function
> orthogonal to every `v_q` under the half-normal measure `T ≥ 0`.

## Setup

Basis taken verbatim from `M245_PREDECLARATION_20260810.md` §3, with
`alpha = mu_i/sigma_i` and, by the ReLU mean identity,
`mbar = m_i/sigma_i = alpha·Φ(alpha) + φ(alpha)`, giving
`rbar(g) = (relu(alpha+g) − mbar)²` — quadratic on the active branch, constant
`mbar²` on the inactive one, with the mandatory kink at `t = |alpha|`.

## Method — deliberately not `mp.quad(error=True)`

The companion result `gm_mpquad_error_contract` measured that mp.quad's error
heuristic can report an arbitrarily small number on a completely wrong value and
that its magnitude does not rank correctness, and that an arbitrary panel edge
can convert a correct answer into a silent miss while a panel edge **on** the
feature is correct at every width.

Both lessons are applied: every integral is split at the kink `t = |alpha|` and
evaluated by **fixed-order Gauss–Legendre on explicit panels** — a deterministic
node set with no adaptive stopping rule — and each Gram matrix is recomputed at
two node counts (60 and 48 per panel). Agreement is the acceptance criterion.

**Measured agreement: worst relative difference `3.0e-59` (α=0), `1.2e-58`
(α=0.75), `1.1e-59` (α=−0.6)** at `dps=60`. Converged, with no heuristic
consulted.

## Result 1 — the conditioning item is closed

The audit filed *"`G_Q` spectral spread is massive. At `alpha=0` and `Q=4`, the
condition number is measurable on the order of `2.7×10^5` … OPEN_REQUIRES_RUN to
observe if `κ ≤ 1e25` survives."*

| Q | κ(G_Q), α=0 | α=0.75 | α=−0.6 |
|---:|---:|---:|---:|
| 4 | **2.798e5** | 3.955e5 | 2.078e6 |
| 8 | **6.658e9** | 6.878e9 | 2.032e10 |

- **The audit's `~2.7e5` at `alpha=0, Q=4` is confirmed** — measured `2.798e5`.
  It is an `alpha=0` figure; at `alpha=−0.6` the same `Q` is 7× worse.
- **`κ(G_8) ≈ 6.7e9`–`2.0e10`, i.e. 15 orders of magnitude below the `1e25`
  gate.** `OPEN_REQUIRES_RUN` resolves to PASS with enormous margin, and the
  concern that unpivoted Cholesky at `Q=8` would exhaust an 80-dps budget is not
  supported: 60 dps was already ample.

## Result 2 — no orthogonal function found

Relative residual after projecting a centered target onto `span(v_0…v_Q)`.

**α = 0**

| target | Q=0 | Q=2 | Q=4 | Q=6 | Q=8 |
|---|---:|---:|---:|---:|---:|
| degree-1 `t` | 0.2589 | 0.09778 | 0.01652 | 6.142e-4 | **3.785e-5** |
| `sqrt(t)` | 0.4722 | 0.2527 | 0.05824 | 0.004917 | 0.001149 |
| `exp(−t)` | 0.5679 | 0.2696 | 0.04657 | 0.001739 | 1.072e-4 |
| `cos(3t)` | 0.9990 | 0.6957 | 0.01427 | 0.01267 | 9.931e-4 |
| control `v_0` | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

**α = 0.75** (genuine interior kink): degree-1 `0.0623 → 0.00105`;
kink-local `|t−|alpha||` `0.5244 → 0.00509`; `cos(3t)` `0.953 → 0.0115`.

**α = −0.6** (worst conditioning, slowest decay): degree-1 `0.4051 → 0.00812`;
kink-local `0.2356 → 0.05312`; `cos(3t)` `0.988 → 0.0239`.

**Every target's residual decreases; none plateaus.** Smooth, non-smooth
(`sqrt(t)`, `|t−|alpha||`), bounded, and oscillatory candidates are all captured.
The `v_0` control is exactly 0 as required.

## Correction to an earlier claim of mine

Last turn I argued that because `v_q` has leading degree `q+2`, the span is a
codimension-≤2 subspace of the polynomials and the **degree-1 direction might be
unreachable**, and proposed that as the likely explicit orthogonal function.
**That was wrong, and the measurement refutes it**: degree-1 `t` has residual
falling from 0.2589 to 3.785e-5 across `Q=0…8` at `alpha=0`.

The error: leading-degree triangularity gives a *lower bound* on degrees present,
not a characterization of the span. Folding makes
`u_q(t) = ½ h_q(t)[(t + alpha − mbar)² + (−1)^q mbar²]`, so the quadratic factor
carries a **parity-dependent** sign. Even- and odd-`q` combinations therefore
reach `h_q(t)` itself, and the span is far richer than "polynomials of degree
≥ 2". The audit's SPD derivation was right and my extrapolation from it was not.

## What this licenses, and what it does not

**Licensed.** No counterexample exists among five structurally diverse
candidates at three values of `alpha`, including non-smooth functions aimed at
the kink — the natural place for a density failure to hide. Combined with the
determinacy argument (half-normal moments grow like `(n/e)^{n/2}`, so
`Σ m_n^{−1/(2n)} ~ Σ n^{−1/4}` diverges and Carleman's condition holds, and the
quadratic window only shifts moments by two), density is the reasonable working
hypothesis.

**Not licensed.** *Failing to find an orthogonal function is not a proof of
density.* Five candidates are not a spanning argument, and Parseval still may not
be invoked globally. The audit's stance — only `0 ≤ V_∞ ≤ K − P_8` is certified,
extrapolations are finite falsification descriptions — remains correct and this
result does not change it. The item should move from `OPEN` to **"no
counterexample found; consistent with density; formal proof still outstanding"**,
which the audit itself rated *Probability: Low, Consequence: Low* and needed only
before a later provider child claims global optimality.

**Regime note.** `alpha < 0` is the hard case: worst conditioning (`2.0e10` at
`Q=8`) and slowest residual decay (kink-local still `0.053` at `Q=8` versus
`0.005` at `alpha=0.75`). If a density failure exists anywhere, negative `alpha`
near the kink is where to look next.

## Reproduction

```bash
pip install mpmath
python3 check_completeness.py --alpha 0.0  --qmax 8 --dps 60 --order 60 --order2 48
python3 check_completeness.py --alpha 0.75 --qmax 8 --dps 60 --order 60 --order2 48
python3 check_completeness.py --alpha -0.6 --qmax 8 --dps 60 --order 60 --order2 48
```

Pure mpmath, ~2 minutes per alpha. No corpus data, truth, scorer, holdout,
private data, leaderboard, submission, or champion access. No estimator,
variance, MSE, or score claim.
