# Graveyard run — re-reading every major corpse against the width evidence

Date: 2026-08-10. Descriptive re-analysis of the recorded failure set. **No
estimator, variance, MSE, score, champion, promotion, or submission claim is
made or implied.** Nothing here revives, promotes, or kills a candidate by
itself; each grouping is a hypothesis with its record cited, to be settled by
the external ladder.

## Why re-read now

A graveyard run is only worth doing when something changed that could move a
premise. Three things changed:

1. **`gm_m179_m199`** returned `KILL_CONFIRMED`: the exact zero-order
   full-covariance recurrence fail-closes at layer 12 of 32 at width 256.
2. **`gm_spd_width_scaling`** (this session) measured that as a width effect:
   **0 of 22 replicates at width ≥ 96 complete 32 layers PSD-safe**, Spearman
   `ρ(width, ℓ*) = −0.743` over 74 cells with width ≥ 32, and the large-width
   mechanism is round-off in the dense entrywise representation.
3. The score law reduces to `score = v·c/B` above the multiplier floor, with
   residual wall priced at a derived `1.000e11` FLOP-equivalents per second.

## Method, and its measured limits

Automated keyword clustering over the records was tried and is **not reliable**,
measured both ways:

- against the atlas's own text, 88 of 161 killed records (55%) match no
  obstruction — including three that are documented elsewhere as width-dilution
  deaths;
- against the experiment reports, coverage rises to 75% but `allocation`-type
  words match 41% of 374 files.

So the groupings below were assigned by reading each record. `scripts/
build_obstruction_graph.py` is retained as a triage index with those error
rates in its docstring; **its counts are not cited as evidence anywhere here.**

---

## Finding 1 — the screen rung and the production rung are different regimes

**The load-bearing observation of this run.**

Across the atlas, kill conditions name widths **3, 4, and 64. None names width
256.** The ladder's screen gates are written at screen width, and promotion
reasoning treats a screen result as a scaled-down production result.

Two *independently measured* laws say that is not what it is:

| law | measured at | statement |
|---|---|---|
| **trace-share dilution** | `LATENT_FACTOR_ADVERSARIAL_AUDIT` | top-two trace share falls **88.4% at n=4 → 3.02% at n=256**; fixed-`r` captured signal vanishes with width |
| **PSD loss** | `gm_spd_width_scaling` (new) | **0/22 replicates at width ≥ 96 reach depth 32**; 21/32 do at widths 32–56 |

Both change *qualitatively* between the screen band (n ≤ 128) and n = 256, and
both act on exactly the object most candidates carry: an n-dimensional
second-order state.

This predicts a specific corpse signature — **"passed the screen 8/8, died at
production"** — and the graveyard contains a cluster of exactly that shape:

| corpse | screen result | production/aggregate result |
|---|---|---|
| Gate-aligned scalar split | 8/8 n64 wins | ratio 0.997502 vs gate ≤0.8 |
| RB conditional marginals | 8/8 stable n64 wins | ratio 0.997502361 |
| q3 response-Gram recursion | 8/8 wins vs fullcov | ratio 0.997502340 |
| Radial susceptibility compressor | layer-0 8/8 wins | 2.475% aggregate, 11/24 wins |
| Weight-identified latent q3,r2 | small-width ratio 0.04738, 6/7 wins | n64 loses 8/8 |
| Full-covariance 2n sigma mixture | covariance matched to 3.01e-15 | n64 ratio 8.8716, 1/8 wins |

**This is not a claim that those mechanisms are wrong.** It is a claim that the
rung which passed them was not measuring the regime they were promoted into.

### What it licenses — a width-transfer gate

A cheap, checkable ladder rule, expressible in `fold_ledger.py`:

> Before a screen result may promote, the mechanism's captured-signal statistic
> must be measured at **≥ 2 widths**, and its extrapolation to n = 256 must be
> non-vanishing. A mechanism carrying an n-dimensional second-order state must
> additionally report spectral PSD at depth, not only per-pair guards.

Applied retrospectively, the first clause would have flagged the latent-factor
family before its full ladder run (the audit that found `88.4% → 3.02%` was run
*after* the kill). The second clause is what `relu_moments` is missing today.

---

## Finding 2 — three kills that are arithmetically one kill

| corpse | recorded aggregate ratio |
|---|---|
| Gate-aligned scalar split | `0.997502` |
| RB conditional marginals | `0.997502361` |
| q3 response-Gram recursion | `0.997502340` |

Three mechanisms with different state, different operators and different cost
bounds agree to **seven significant figures**. The corpus notices this pairwise
— "only 6.08e-8 better than H10", "H15/H12 = .9999999786" — but the salvage map
still derives **three separate next-admissible mutations** from them, each of
which then cost a ladder run.

Agreement to 1e-8 in a quantity whose gate is 0.8 does not describe three
mechanisms. It describes one measurement, dominated by a shared parent term
that all three corrections leave untouched. The honest reading: **the harness
was not resolving the mechanisms at all**, and the three "independent"
confirmations of the gate-split family are one confirmation.

Its named cause is already in the corpus, in `LATENT_GATE_RB_MARGINALS_REPORT`:
*"the high-dimensional dilution law in concrete form ... `O(1/n)` variance into
any one neuron."* That is Finding 1's dilution law, reappearing as an
identical number three times.

**What it licenses:** a ledger rule that a new candidate whose primary metric
matches an existing record to within the gate's resolution is *not* independent
evidence and may not spawn a separate mutation branch until the shared term is
separated out.

---

## Finding 3 — the atlas records death, not revival

Measured across the 223 GEN6 records:

| field | distinct | reading |
|---|---|---|
| `prediction` | 223/223 (100%) | fully specific |
| `kill_condition` | 221/223 (99%) | fully specific |
| `failed_link` | 192/223 (86%) | largely specific |
| **`reopening_condition`** | **47/223 (21%)** | **one generic sentence on 177 records (79%)** |
| `approximation_or_materiality` | tags 210/223 (94%) | no discriminating power |

The atlas answers *why did this die* very well and *what would bring it back*
almost not at all. A graveyard run needs the second field, which is why this
document exists as prose rather than as a query over the artifact.

---

## The corpse table

Grouped by the specific obstruction that killed them. `post-SPD` records
whether `gm_spd_width_scaling` changes the entry's status.

### G1 — width/dilution regime (the largest group)

| corpse | preserved | obstruction | post-SPD |
|---|---|---|---|
| Weight-identified latent q3,r2 | mixture machinery, invariance | trace share 88.4%→3.02% | unchanged |
| Latent factor q3,r3 | invariance, 33.075B arithmetic | monotone `r` does not repair dilution | unchanged |
| Gate-aligned scalar split | exact conditional moments | O(1/n) dilution (see Finding 2) | unchanged |
| RB conditional marginals | exact scalar-conditional integrals | same measurement as above | unchanged |
| q3 response-Gram recursion | affordable response operator | same measurement as above | unchanged |
| Radial susceptibility compressor | exact q3 moments, pullback | single scalar geometry dilutes | unchanged |
| Radial dual-observable fusion | both response Grams, rank-two geometry | scalar fusion erases contrast | unchanged |
| Full-covariance 2n sigma mixture | covariance to 3.01e-15, cost bound | second moments are not the missing observable | **newly constrained** — its parent representation is undefined at n=256 |

### G2 — the four-point vertex (information genuinely absent)

| corpse | preserved | obstruction |
|---|---|---|
| Cavity/Dyson/TAP | exact DAG no-self-reaction proof | connected vertex needs O(n⁴)/O(n⁵) |
| Copula / two-Gaussian | marginal extension | dependence underidentified |
| Terminal analytic k3/k4 | exact Hermite formulas | 0.493% gain; `M137` theorem-obstructs |
| Repeated-index k3/k4 | exact O(n²) compact state | all-distinct cancellation destroyed |
| Conditional total-cumulance | exact binned identity, rank-4 factors | within-cell residual cumulants omitted |
| Constant-modulus transport | ≤12D algebra, 94/94 signs | probes exactly blind to trace-free diagonal |

This group is **not** touched by the SPD result: it fails on information, not
on representation. `M137` is a theorem and stays a design constraint.

### G3 — superlinear formation cost

Conditional-correlation spectrum (1.855T dense discovery), conditional
residual-cumulant spectrum (8.063 GiB/cell, 129 GiB), goal-oriented adjoint
cumulants (O(Ln⁴)), H3 rank-5 k4. Representation compresses; *discovery* does
not. Unchanged by the SPD result.

### G4 — no exact-mean control

Constant-anchor inverse residual (`a + mean(f−a) = mean(f)` pathwise — a
theorem, grade A), randomized-radial inverse residual, JSpace top/bottom/
complement (near-zero error correlation), Fourier/Gegenbauer distillation.
The binding constraint is structural: fresh-private forbids precomputation, so
a legal control needs an analytically known mean for arbitrary weights.

### G5 — residual wall / allocation

Whole-row rectangular Strassen: billed `r_C = 0.795427` with depth-32 parity
`4.10e-6`, killed **only** by Python allocation residual (12.205B effective vs
8.444B direct). With the exchange rate now derived at `1.000e11` FLOP/s, the
gap is `≈0.0376 s` of wall. The recorded reopening target — L1 residual below
`0.00987 s` — is therefore a wall-time engineering target with an explicit
price, not a vague one. **This remains the best-evidenced live score item in
the graveyard.**

### G6 — sign transport

H2 weight-conditioned blend (cross-seed ICC 0.129, 6/6 transfer failures),
global analytic/sampler blend (sign varies −3.74 to +3.56), nonlinear shrinkage
(CV 54.8%), H3 rank-5 k4 (downstream cosine −1.000). Magnitude is recoverable;
transported sign is not. Unchanged.

### G7 — numerical / PSD (the group this run adds)

| corpse | obstruction | status |
|---|---|---|
| M178→M179→M176→Source211→M175 chain | non-PSD at production width | `KILL_CONFIRMED`; now with a **measured width mechanism** |
| Multi-direction gate response | complete k1 has 5/24 PSD fallbacks | re-read as the same obstruction |
| Residual covariance-algebra factors | probe systems condition above 1e10 | re-read as the same obstruction |

Before this run these three were filed under three different causes. They share
one: **a second-order state assembled entrywise and propagated densely loses
definiteness as width grows.**

---

## What this run licenses

1. **A width-transfer gate** in the ladder (Finding 1). Cheap, retrospectively
   validated, and expressible as a `fold_ledger.py` audit rule.
2. **A resolution rule** (Finding 2): a candidate matching an existing record
   to within gate resolution is not independent evidence.
3. **A spectral guard** on `relu_moments` — it gates on diagonal variance and
   pairwise `ρ`, never on the spectrum, so it silently accepts non-PSD state
   from layer ~10–12 at width 256. This is a correctness defect in a component
   described as certified, and it is independent of every ceiling question.
4. **One untested repair, named honestly**: the large-width failure is round-off
   in the *dense entrywise* representation. A factored (Cholesky /
   eigendecomposition) propagation preserves PSD by construction and has never
   been tried. It is the natural next mutation for G7 and it is **not** closed
   by anything in this corpus.

## What this run does not license

- **No revival of any G2, G3, G4 or G6 corpse.** Nothing measured here touches
  information absence, discovery cost, exact-mean availability, or sign
  transport. Those kills stand on their own evidence.
- **No score claim.** The two levers remain walled: analytic controls cap at
  1.40x by the R² arithmetic (of which the champion has already banked 1.31x),
  and the native/throughput arm is priced out by the exchange rate. Nothing in
  this run changes the ~2.2x budget of already-proven components.
- **No claim that Gaussian closures are impossible.** G7's obstruction is
  scoped to a dense entrywise float64 representation at depth 32 and width 256.
- **No claim from the automated matcher.** Its measured error rates disqualify
  its counts; only the read-and-checked assignments above are asserted.
