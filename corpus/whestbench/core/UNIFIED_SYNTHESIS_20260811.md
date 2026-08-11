# Unified synthesis: what the whole campaign adds up to

Date: 2026-08-11. Scope: reconciles `arc-whitebox-estimator` (the executable repo, last
touched 2026-07-10) with this corpus (2026-08-06), and states the one law that explains all
31 kills. Every number below is quoted from a file in one of the two repos or measured
locally on fresh synthetic networks; nothing here used an official row, the scorer, or the
private suite.

## 0. The escalation, first

**The remaining gap to the leaderboard is a legality decision, not an engineering deficit.**

`sources/research_top_method_forensics_20260803.md` measured the instrumented FLOP share of
the top twelve public entries. **Eleven of twelve are below 0.1%; all twelve are below 1%.**
Their effective compute is therefore almost entirely *residual wall time*, priced at 1e11
FLOP/s — i.e. the real arithmetic is running outside the instrumented path. Seven of the
twelve also report the identical all-layer MSE `0.7537`, the signature of emitting the
scored final row and placeholder garbage everywhere else.

`sources/research_top_method_families_20260803.md:95-103` records both the finding and this
campaign's response:

> Public participants measured instrumented/effective-compute ratios below 0.001 for several
> top submissions: most real arithmetic was running outside the instrumented path and being
> priced only by residual wall time. This can create an order-of-magnitude apparent score
> advantage and **remains under organizer clarification**. It is **excluded from this project
> under the strict accounting boundary.** An independent pre-reveal estimate placed the
> honest unbiased floor near **3.7e-7 adjusted** on unseen networks.

Two consequences follow, and they should be read together:

1. The deployed champion at `2.257079776e-7` **already beats the pre-registered honest floor
   of 3.7e-7 by 1.64x.** By the standard this campaign set for itself, it is not behind.
2. The ~24x that separates it from rank 1 sits almost entirely in a channel the campaign
   deliberately refused, under `SKILL.md`'s "preserve the stricter interpretation and request
   an official clarification before submission."

The correct next action on that gap is **to request the clarification**, not to write code.
Everything downstream of that decision is worth 1.02x–1.23x (§4). Nothing found in 31 kills
is worth 24x.

## 1. Correction: the target arithmetic was wrong in both repos

`arc-whitebox-estimator/tasks/journal-whestbench.md:26` states:

> Leaderboard top ~9e-8 adjusted => need final_mse ~9e-7 at the 0.1 floor.

That is a units error, and it propagated. `sources/research_competition_ladder_20260803.md`
records the Phase-I public ladder as rank 1 = **`9.2e-9` adjusted with `9.24e-8` final-layer
MSE**. The journal's "9e-8 adjusted" is the leader's *raw MSE*. The later forensics snapshot
has rank 1 at `7.39e-9` adjusted.

| quantity | value |
|---|---:|
| champion adjusted | `2.257079776e-7` |
| rank 1 adjusted (Phase-I ladder) | `9.2e-9` |
| **true adjusted gap** | **24.5x** (30.5x against the `7.39e-9` snapshot) |
| max obtainable from cost alone (`0.743683 → 0.1` floor) | **7.44x** |
| raw-MSE improvement still required at the floor | **3.30x** |

The champion's multiplier is `0.743683`, so cost reduction is capped at `7.4368x` — and the
leader is already sitting on the floor (`9.2e-9 / 9.24e-8 = 0.0996`). A 3.30x raw-MSE gain
*and* a 13x cost cut are jointly required. Sections 2–4 show why that is unreachable inside
this estimator family.

## 2. The one law

```
score = MSE × max(0.1, C/B),   C = billed_FLOPs + 1e11·residual_s,   B = 2.72e11
promotion  ⟺  r_C · r_V < 1
```

Read as an efficiency `E = MSE × C`, the 31 kills sort into four classes:

| Family | Why it dies | Kills |
|---|---|---:|
| **Sampling reallocation** — blending, shrinkage, anchoring, routing, inverse-residual | For a pure `1/N` sampler with cost `∝ N`, `E = V·c₀` is invariant in `N`. `a + mean(f−a) = mean(f)` exactly; a mixture is a weighted mediant of pure `c·v` efficiencies and can never beat the best one. | ~6 |
| **Analytic / biased closure** | `E = bias²·C` and `bias²` does not fall with `C`. At its best *and* cheapest — full-covariance, raw `5.428e-5` at `6.1894B`, already floored — it scores `5.428e-6`, **24x worse than champion**. It needs 24x in *accuracy*; ~15 mutations moved it <1%. | ~15 |
| **Control variates** | Equal-compute ratio is `κ(1−ρ²)`. Measured `ρ² ≈ 0.001–0.0026` against cost multipliers `κ ≈ 1.75–4.43`. The control cannot pay its own freight. (Not, as one might guess, because `Var(e−c)=V_e+V_c` at `β=1`; with cross-fit `β` a null control is merely neutral.) | ~6 |
| **Exact arithmetic compression** | `r_V ≡ 1`, so the gate collapses to `r_C < 1` and is decidable by cost measurement alone, with no statistical oracle. **The only family that can still move.** | 2 |

### 2a. Where the flatness claim needs qualifying

`COMPRESSION_SCORE_CALCULUS_20260806.md:38-42` states that path-count changes give
`r_C·r_V ≈ 1`, i.e. no first-order gain. The campaign's own promotion contradicts the strict
form. From `RANDOM32256_PAIRED100_REPORT.md`, on the 95 both-success networks:

| | N | raw MSE | adjusted |
|---|---:|---:|---:|
| parent | 39,936 | `2.738346309e-7` | `2.439277675e-7` |
| child | 32,256 | `3.141091507e-7` | `2.282126128e-7` |

`r_N = 0.8077` but `r_V = 1.1471`, not `1/r_N = 1.2381`; with `r_C = 0.8156` the product is
`0.9356 < 1`. So MSE is **not** exactly `∝ 1/N` here, and cost is **not** exactly `∝ N`.
A fixed setup cost `c_f` and an `N`-independent error floor `B²` both break the invariance
and create an interior optimum `N* = sqrt(V·c_f / (B²·c₀))`.

This is a **two-point fit on a subset selected by parent cost**, so it is a hypothesis, not a
result — and it is bounded: driving `N` all the way to the multiplier floor predicts
`≈2.39e-7`, *worse* than today. The honest statement is that flatness holds exactly for an
idealised `1/N` sampler, approximately for this one, and that locating `B²` (likely residing
in the frozen first-layer moment tangent or the pilot pruning) is worth more as a diagnostic
than as a score chase. **Measuring the `MSE`-vs-`1/N` intercept on synthetic networks is the
cheapest open experiment in the campaign.**

## 3. Exact gate-fold depth: killed by measurement (new, this session)

The champion folds dead/always-on/kink neurons over the **final three layers only**. No
ledger candidate and no salvage row had ever proposed extending it — a genuine gap in the
only family §2 says can still move. It is now closed.

Window algebra: a folded window costs `256 + 2·Σ|KINK_l|` against a baseline `256k`, so an
interior layer pays exactly when `p_l < 0.5`, and
`r_C = 1 − (1/L)·Σ_{p_l<0.5}(1 − 2p_l)`.

Measured (`arc-whitebox-estimator/src/gate_census.py`, fresh synthetic He n256/L32 nets,
under the champion's own geometry — 126 Haar frames × 256 columns × antipodes = 64,512
directions):

| direction count | foldable interior layers | achievable `r_C` |
|---|---:|---:|
| 64,512 (deployed) | 6 / 31 | **0.9780** |
| 16,384 | 7 / 31 | 0.9664 |
| 4,096 | 8 / 31 | 0.9507 |
| 1,024 | 12 / 31 | 0.9263 |

`p(l)` falls monotonically with depth but **plateaus at 0.48–0.56 from layer 27 onward**,
never clearing the threshold. An independent closed-form derivation from the ReLU arc-cosine
correlation map `c_{l+1} = (√(1−c²) + c(π − arccos c))/π` predicts `κ_l ≥ 0.514` with the
minimum at the last layer — agreeing with the measurement. Three further facts seal it:

- `0.9780` is a **ceiling**, assuming exact classification is free. It is not: obtaining it
  costs the arithmetic the fold avoids.
- The cheap Cauchy–Schwarz certificate `w_i·h_ref > ‖w_i‖R` is `√n ≈ 16x` too loose and
  certifies **nothing** — deployable `r_C = 1.0000`.
- The window model above *omits* kink→kink coupling inside a window, so the true condition is
  strictly tighter than `p_l < 0.5`. The kill is therefore conservative.

**Constraint learned: exact gate folding is sample-count-limited.** `p` rises with the
direction count, so accuracy and foldability are in direct tension. fold3's depth was not a
shortcut — three layers is essentially the whole available ceiling. Ledger:
`exact_gate_fold_depth_k`.

## 4. What is actually left

| lever | effect | state |
|---|---:|---|
| Uninstrumented execution channel | ~24x | **Legality question — needs organizer clarification. Excluded under the current boundary.** |
| Rectangular Strassen, preallocated `out=` / Winograd | 1.23x | Algebra passes (`r_C = 0.795427`); blocked on allocation residual `< 0.00987s` |
| Path-count re-optimisation at `N*` | ~1.14x, unconfirmed | Two-point fit; test the `MSE`-vs-`1/N` intercept locally first |
| Exact gate-fold depth | 1.02x ceiling, 1.00x deployable | **Killed §3** |
| Analytic closure | needs 24x accuracy | Killed, 15 forms |
| Control variates | `κ(1−ρ²) > 1` | Killed, 6 forms |

## 5. Repo reconciliation

`arc-whitebox-estimator` was abandoned mid-ladder with a frozen "Next action" — RUNG 3, the
exact bivariate rectified-Gaussian kernel plus cumulant/Hermite correction — which this
corpus subsequently executed and hard-killed in ~15 forms (`k3_finite_horizon` at 583x;
`goal_oriented_adjoint_cumulant` at +2.12%; `h3_rank5_k4` at downstream cosine −1.000; the
gate-split family pinned at ratio 0.9975 against a required 0.8). Resuming it as written
re-enters a branch with a 31-deep kill record. Its journal also carried the units error of §1
and a stale frozen Goal block (`max(0.5, ·)`, `B ≈ 3.4e10`) contradicted by its own
confirmed-spec block fifteen lines later. Both are corrected there, and that repo now carries
`docs/UNIFIED_SOLVE.md` pointing here.
