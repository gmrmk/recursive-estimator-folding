# Headroom-recursion packet — Generation 7 (2026-08-10, Opus 5 session)

**Audience: a parallel agent picking up this corpus cold.** Read this before
touching anything. It is written to the `SKILL.md § Offline Headroom
Integration` packet contract: champion state, evaluator/budget margin,
promoted/killed/unresolved, residual correlation among survivors, exactly one
next-mutation request, holdout firewall.

**Branch state.** Work branch `claude/repos-agentic-frontier-e8ixlk` @ `6c8adce`,
based on `main` @ `102bd7c`. The large campaign branch
`agent/compression-survivor-corpus` @ `b688a5d` (draft PR #1, 1607 files, 241
commits) is **not merged**; several artifacts cited here live only there and are
read read-only via `git show`. Sibling repo `heuristic-memory-dual-log` @
`a45fa72`.

**Reading order if you have five minutes:** §1 (the score law) → §3.4 (the width
law) → §6 (the one next mutation) → §7 (traps). Everything else is support.

---

## 0. Session deltas — what is new since `102bd7c`

| commit | what it establishes |
|---|---|
| `d4b49c2` | CI installs declared deps; `requirements.txt` added (networkx, numpy) |
| `9e7ecda` | **SPD width law measured** — `gm_spd_width_scaling` |
| `ad04e4a` | Graveyard run — obstruction regrouping of the failure set |
| `e0f6d89` | **`mp.quad(error=True)` contract FALSIFIED** — `gm_mpquad_error_contract` |
| `c7b058e` | M245 transport Race 1 executed — not reproduced |
| `ae095c1` | M245 Races 2/3 + completeness — none reproduced |
| `6c8adce` | **Additive spectral PSD guard** — `gm_spectral_psd_guard`, 11 tests |

---

## 1. The score law, reduced

From `core/COMPRESSION_SCORE_CALCULUS_20260806.md`, per network:

```
score = MSE · max(0.1, C/B),        B = 2.72e11
```

Put `MSE = v/N` (v = variance per sample) and `C = c·N` (c = billed cost per
sample). Then:

| regime | condition | score |
|---|---|---|
| above floor | `N ≥ 0.1B/c` | `(v/N)(cN/B) = v·c/B` — **independent of N** |
| below floor | `N < 0.1B/c` | `0.1·v/N` — decreasing in N, so worse |

At the boundary `N = 0.1B/c` the second gives `0.1v·c/(0.1B) = v·c/B`. The two
branches meet exactly. Therefore

> **`score* = v·c/B`, and sample count is a level set of the objective.**

This is why every sample-count mutation in the corpus measured neutral: they
moved along a contour. The campaign's own `adjusted = v · 8.74e-6 / S`
(commit `7eb2f63`) is the same identity with `c ∝ 1/S`.

**Two levers only: variance per sample, and billed cost per sample.**

### 1.1 The biller's exchange rate (derived here; verify before doctrine)

Champion `random32,256`: billed arithmetic `185.4069B`, mean *effective* compute
`202.282B`, mean residual wall `0.16875 s`.

```
(202.282 − 185.4069)e9 FLOP / 0.16875 s = 1.000e11 FLOP-equivalents / second
```

**Residual wall is charged at exactly 100 GFLOP/s.** One second of wall costs
`1e11/2.72e11 = 36.8%` of the entire budget. Three consequences:

1. Residual overhead is `16.875B` = **8.34% of effective compute**. Eliminating
   it entirely is worth `1.043x`. That bounds all non-algebraic in-estimator
   engineering.
2. **Native code is billed at ~3.3x its FLOP count** on a ~2 vCPU grader
   (~30 GFLOP/s delivered, 100 GFLOP/s charged). This independently re-derives
   the `t1` LIVE_RULES_RESET conclusion and explains its `k* = 1.42` break-even.
3. The native-kernel `#1` thesis needs **>100 GFLOP/s achieved** on the grader.
   2 vCPU AVX-512 f32 is ~192 GFLOP/s theoretical, ~60–100 achievable — the
   thesis sits on the break-even line.

**Decision rule:** move work from billed arithmetic to native wall only if
measured native throughput exceeds the exchange rate. Otherwise stay
instrumented.

⚠️ Derived from **one** aggregate triple. Confirm against a second network's
`(billed, effective, wall)` before this enters doctrine or a filing.

---

## 2. Champion state

| quantity | value |
|---|---|
| deployable champion | `random32,256` fold3 sampler |
| raw MSE | `3.089512726e-7` |
| adjusted score | `2.257079776e-7` |
| mean effective compute | `202.282B` |
| max effective compute | `250.489B` |
| mean multiplier | `0.7436830511` |
| failures | `0/100` |
| frozen parent | fold3 `39,936` — raw `1.5686923e-7`, adjusted `1.4123151e-7`, **5/100 budget failures** |

Matmul is `184.8217B` of `185.4069B` billed = **99.6844%**, over `215.41` calls.
Buffer-only optimization therefore cannot be the main win.

---

## 3. The ceilings

### 3.1 Analytic control caps at 1.40x — R² arithmetic, not an experiment

A control with correlation ρ multiplies variance by `(1 − ρ²) = (1 − R²)`. From
`n5` (`7530c3a`):

| control | R² | variance factor | improvement |
|---|---:|---:|---:|
| none | 0 | 1.000 | 1.00x |
| layer-1 only (**champion already banks this**) | 0.235 | 0.765 | 1.31x |
| all layers (multilevel) | 0.287 | 0.713 | **1.40x** |
| remaining beyond layer-1 | — | `0.765/0.713` | **1.073x** |

`n5`'s measured `1.07x` is not an artifact — it is `0.765/0.713`. **71.3% of
residual variance is orthogonal to everything with a computable Gaussian mean.**

**Scope:** `n5` states first-order, diagonal, small-net. Do not cite 0.287 as
unconditional.

### 3.2 The same wall from the other side

`t2` (`434c823`) scored the certified exact full-covariance closure as a
*predictor*:

| estimator | bias-MSE | vs sampling |
|---|---:|---:|
| diagonal closure | `7.175e-4` | 2322x |
| exact full-covariance closure | `9.6055e-5` | **311x** |
| sampling champion | `3.0895e-7` | 1x |
| MC noise floor | `1–2e-7` | — |

Exact full covariance buys 7.5x over diagonal and is still 311x from
competitive. Kill gate K1 fired by 46x.

**Root cause:** fresh-private forbids precomputation, so a legal control needs an
analytically known Gaussian mean *for arbitrary weights*. That space is
essentially {linear, quadratic, layer-1 ReLU}. Past layer 1 you need the joint
law of a ReLU-composed Gaussian — precisely what is not Gaussian. `M137`
theorem-obstructs the terminal k3/k4 detour.

### 3.3 In-estimator parallelism caps at 1.04x

Parallelism reduces wall, not billed arithmetic, so it acts only on the 8.34%
residual, further capped by ~2 vCPU. **Parallelize the falsification, not the
estimator.**

### 3.4 NEW — the closure is *undefined* at production width

`gm_m179_m199` returned `MEASURED / KILL_CONFIRMED`: at width 256 the pre-ReLU
covariance leaves the PSD cone at layers **12** and **10** of 32. ARM C is doubly
blocked — `m167.complete_source_reference` is an O(n³)-iteration Python loop with
O(n²) inner work extrapolating past `1e5 s` at width 256, *and* the composed path
fail-closes before layer 32 at any speed.

`gm_spd_width_scaling` (this session) measured it as a width law. `ℓ*` = first
layer with `min eig(C) ≤ 1e-12`; 96 distinct cells merged from three independent
datasets, **0 conflicts**; width-256 reps 0/1 reproduce `diag256.log` exactly
(`12`, `10`) as the predeclared admissibility check.

| width | 32 | 48 | 64 | 80 | 96 | 128 | 160 | 192 | 224 | 256 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P(reach L32) | 0.75 | 0.38 | 0.00 | 0.12 | **0** | **0** | **0** | **0** | **0** | **0** |
| median `ℓ*` | — | 28 | 18.5 | 19.5 | 15.5 | 15.0 | 12.5 | 11.0 | 9.0 | 11.0 |

- **0 of 22 replicates at width ≥ 96 complete 32 layers PSD-safe**, against 21 of
  32 at widths 32–56.
- Spearman **`ρ(width, ℓ*) = −0.743`** over the 74 cells with width ≥ 32
  (censoring "reaches 32" at 33).

**Reported failure:** the predeclared *strict per-width monotonicity* clause
FAILED at the `64 → 72` step (the least-replicated width). It is not asserted;
the rank correlation is the robust statement. `KILL_NO_SCALING` does not fire
only because its second clause (256 not separated from 48) is decisively false.

**Mechanism — two regimes.** Median `|min eig| / (ε·n·λ_max)` at the failure
layer:

| width | 32 | 48 | 64 | 80 | 128 | 192 | 224 |
|---|---:|---:|---:|---:|---:|---:|---:|
| ratio | 431 | 15.6 | 2.63 | 0.154 | 0.59 | 0.248 | 0.0398 |

Below ~64 the floor is reached by **genuine ill-conditioning**, one to three
orders above round-off. From ~80 up the eigenvalue is **at or beneath the
entrywise-assembly noise** — the indefiniteness is representational. An
entrywise-assembled Gram goes indefinite once `λ_min ≲ ε·n·λ_max`, and depth
drives `λ_min` down geometrically.

**Corollary that matters for any filing:** the M179 producer completes all 32
layers anyway — its guard is per-pair (`|ρ| ≤ RHO_MAX`) and never fires. Measured
over 74 cells, **the shipping per-pair guard fired 0 times**, while a spectral
guard fires 18/18 at width ≥ 96. At width 256, layers 11–32 — **69% of the
archived layers** — are downstream of the loss (75% at width 224).

`gm_spectral_psd_guard` (`6c8adce`) is the additive detector. It does **not**
modify the frozen producer. Exact witness in its suite: the equicorrelation
matrix `(1−r)I + r·11ᵀ` has eigenvalues `1+(n−1)r` once and `1−r` with
multiplicity `n−1`; at `r = −1/(n−1)` the first is exactly 0, so the matrix is
singular while every pairwise correlation is exactly `−0.2` at `n=6`. **No
pairwise tightening can ever reach this; the quantity is spectral.**

---

## 4. Live score budget

| # | lever | mechanism | factor | status |
|---|---|---|---:|---|
| 1 | `t3` fold3 + deterministic cap | fixes the 5/100 budget-failure mode; adjusted `1.4123e-7` vs `2.2571e-7` | **1.60x** | built, G1–G4 PASS, **score-unknown** |
| 2 | preallocated Strassen/Winograd | billed `r_C = 0.795427`, depth-32 parity `4.10e-6`, 5 gate changes in 4.19M activations; killed **only** by allocation residual (12.205B eff vs 8.444B direct) | **1.26x** | algebra proven, engineering open |
| 3 | residual-wall elimination | `16.875B` of charged wall | 1.04x | not started |
| 4 | remaining analytic control | §3.1 | 1.07x | ceiling, not a plan |

**Compounded ≈ 2.2x → adjusted ≈ 1.03e-7.** Bars: top-12 `4.3x`, top-6 `9–12x`,
`#1` `23.5x`. **2.2x does not reach top-12.** With the exact-control chain
`KILL_CONFIRMED` at reachability, no remaining v-lever exceeds 1.07x.

Item 2 is now **priced**: the `12.205 − 8.444 = 3.761B` gap is `0.0376 s` of wall
at the §1.1 exchange rate, so the recorded reopening target (L1 residual below
`0.00987 s`) is a concrete engineering target.

---

## 5. Obstruction map (graveyard run, `ad04e4a`)

Automated keyword clustering was tried and **does not work here** — 55%
unassigned against thin ledger text, 41% false-positive-prone against rich
reports. `scripts/build_obstruction_graph.py` ships as a triage index with those
error rates in its docstring; **cite none of its counts.** Groups below were
read and checked.

| group | obstruction | representative corpses |
|---|---|---|
| **G1** | width/dilution: a fixed-dimensional summary of an n-dim state dilutes as O(1/n) | latent q3 r2/r3, gate-aligned split, RB marginals, q3 response-Gram, radial susceptibility, radial dual-observable, fullcov 2n sigma |
| **G2** | four-point vertex: the information is genuinely absent | cavity/Dyson/TAP, copula, terminal analytic k3/k4, repeated-index k3/k4, conditional total-cumulance, constant-modulus transport |
| **G3** | superlinear formation cost | cond-corr spectrum (1.855T), cond-residual-cumulant (129 GiB), adjoint cumulants (O(Ln⁴)), H3 rank-5 k4 |
| **G4** | no exact-mean control for arbitrary weights | constant-anchor inverse residual (**theorem**, grade A), randomized-radial inverse residual, JSpace top/bottom/complement, Fourier/Gegenbauer |
| **G5** | residual wall / allocation | whole-row rectangular Strassen |
| **G6** | sign transport unstable downstream | H2 weight-conditioned (ICC 0.129, 6/6 transfer failures), global blend (−3.74…+3.56), nonlinear shrinkage (CV 54.8%), H3 rank-5 k4 (cosine −1.000) |
| **G7** | **NEW** — entrywise-assembled second-order state loses definiteness with width | M178→M179 chain, multi-direction gate response (5/24 PSD fallbacks), residual covariance-algebra factors (conditioning >1e10) |

**G7 unifies three entries previously filed under three different causes.**

### 5.1 Two structural findings about the record itself

**(a) Three kills are arithmetically one kill.** Gate-aligned scalar split
`0.997502`, RB conditional marginals `0.997502361`, q3 response-Gram
`0.997502340` — three different states, operators and cost bounds agreeing to
**seven significant figures** against a gate of `0.8`. The corpus notes the
agreement pairwise ("only 6.08e-8 better than H10", "H15/H12 = .9999999786") but
still derived **three separate next-mutations**, each costing a ladder run.
Agreement at 1e-8 describes one measurement dominated by a shared parent term
none of them touched. Named cause is already in
`LATENT_GATE_RB_MARGINALS_REPORT`: *"the high-dimensional dilution law in
concrete form … O(1/n) variance into any one neuron."*

**(b) The atlas records death, not revival.** Over the 223 GEN6 records:
`prediction` 223/223 distinct (100%), `kill_condition` 221/223 (99%),
`failed_link` 192/223 (86%) — but **`reopening_condition` is one identical
generic sentence on 177/223 (79%)**, and `approximation_or_materiality` tags
210/223 (94%). The field a graveyard needs is the empty one. This motivated the
`heuristic-memory-dual-log` **v4 obstruction canon** (`a45fa72`).

### 5.2 Methodological obstruction — the screen/production regime gap

Atlas kill conditions name widths **3, 4, 64 — never 256.** Gates are written at
screen width. Two independently measured laws change qualitatively between that
band and n=256: trace-share dilution (`88.4% at n=4 → 3.02% at n=256`) and PSD
loss (§3.4). Predicted corpse signature "passed the screen 8/8, died at
production" — six corpses match.

**Licensed ladder rule (cheap, retrospectively validated):** a screen result may
not promote until its captured-signal statistic is measured at **≥2 widths** and
extrapolates non-vanishing to n=256; a mechanism carrying an n-dimensional
second-order state must additionally report **spectral** PSD at depth.

---

## 6. THE ONE NEXT-MUTATION PROPOSAL (per skill: exactly one mechanism)

**Mechanism: propagate a factored second-order state instead of re-assembling
the covariance entrywise.**

Carry `V = L Lᵀ` (Cholesky) or `V = U Λ Uᵀ` and compose the layer map on the
factor, forming `C = Wᵀ V W` as `(LᵀW)ᵀ(LᵀW)` — a Gram of a real matrix, hence
PSD **by construction** in exact arithmetic and to round-off in floating point.
The current path forms `C` entrywise from M178 Owen-T/Tallis moments, which is
exactly the assembly whose `O(ε)` per-entry error drives `λ_min` negative once
`λ_min ≲ ε·n·λ_max` (§3.4).

**Why this is one mechanism, not a retune.** It changes the *representation* of
the propagated state, not any coefficient, tolerance, rank, or gate. It is the
only untested route in G7, and G7's obstruction is scoped to the dense entrywise
float64 representation — so this mutation attacks the diagnosed failed link
rather than drifting parameters. It does not touch G2's information absence.

**Predicted signature.** `ℓ*` (first spectral loss) rises from ~11 to ≥32 at
width 256 for ≥ 3 of 4 replicates, with the post-ReLU `(μ, V)` matching the
frozen entrywise recurrence to `≤1e-9` relative at every layer where the
entrywise path is still SPD-safe.

**Kill conditions, predeclared.**
- `KILL_NOT_PSD` — any replicate still trips `min eig ≤ 1e-12` before layer 32 at
  width 256. The representation is not the binding cause.
- `KILL_DIVERGENCE` — factored and entrywise paths disagree by `>1e-9` relative
  on the SPD-safe prefix. The two are not computing the same object.
- `KILL_COST` — inclusive metered bill exceeds the M179 frozen `8.30B`
  (`= 3.05%` of B) by more than 25%. Note `LᵀW` is a dense `n×n` product per
  layer, the same order as the existing two matmuls, so this should be tight.

**Explicit non-goal.** Even a clean pass does **not** revive the closure as an
estimator: `t2` measured it at 311x from competitive as a *predictor*, and §3.1
caps the control-variate direction at 1.40x. This mutation would make the
producer *defined* at production width, which is a correctness and
paper-completeness result, not a score lever.

**Cheapest falsifier first.** Run the factored recurrence at width 256, two
seeds, layers 1–32, recording `min eig` per layer — ~100 s per cell by the
`gm_spd_width_scaling` timings. That single measurement fires or clears
`KILL_NOT_PSD` before any archive, ABI, or metering work.

**Second and third in queue (do not start before the above):**
1. Vectorize `m167.complete_source_reference` — the O(n³)-iteration Python loop
   with O(n²) inner work; bitwise-parity tested against the existing loop on
   widths 2–28 where it is tractable. Unblocks the *cost* half of ARM C only.
2. Preallocated Winograd/Strassen reconstruction, targeting L1 residual below
   `0.00987 s` (§4 item 2). The design space (tile shape × preallocation × Winograd
   variant) is ~50–200 configs, each cheap under FlopScope — the one place a
   parallel sweep directly buys score, at *design* time.

---

## 7. Traps — errors made this session, recorded so you do not repeat them

| trap | what happened | cost if repeated |
|---|---|---|
| **`M172` is not a variance gate** | It is `m172_selective_22_owner_fusion`, static tensor-algebra, STATIC OWNER-ALGEBRA PASS, blocked on M174's staging ABI. Commit messages referencing "the M172 variance gate" point at a planned object that does not correspond to this artifact. | An entire plan was built on the misreading before being corrected |
| **`str.find` on a function name matches the `def`** | An ordering probe compared source offsets and matched the *definition* of `_publish_r_and_capture_endpoint` (char 33647) rather than its call site (line 2560), reporting a **false FALSIFIED** on Race 3. | A false positive in a race audit costs as much as a false negative |
| **Leading-degree triangularity does not characterize a span** | Claimed `span{v_q}` was codimension-≤2 and that the degree-1 direction was unreachable. Refuted by measurement: degree-1 residual falls `0.2589 → 3.785e-5`. Folding gives `u_q = ½h_q[(t+α−mbar)² + (−1)^q mbar²]`; the parity-dependent sign lets even/odd combinations reach `h_q` itself. | A false "we found the orthogonal function" claim |
| **`mp.quad(error=True)` cannot gate anything** | Measured: reported error `1.02e-3318200587309268176495050` on a value with true relative error `1.0`. Worse, at the *same* integrand and width, plain `[0,1]` reported `1.0e-175` and was correct while panels `[0,0.25,1]` reported `3.48e-119` and was completely wrong — **the wrong answer reported an error 56 orders of magnitude larger**. Populations interleave; no threshold separates them. | Silent numerical false PASS in any gate that reads it |
| **Arbitrary panel edges cause the failure; edges on the feature fix it** | Panel insertion converted a correct result into a silent total miss; a panel edge **on** the feature was correct at every width. | Use the kink cut; justify every other edge |
| **`pgrep -f <script>` matches the waiting shell itself** | An `until ! pgrep -f "run_x.py"` loop never terminated because the loop's own command string contained the pattern. | A hung wait that looks like a hung job |
| **`@dataclass` + `importlib` by path** | `dataclasses` resolves `cls.__module__` through `sys.modules`; a module loaded by path alone raises `AttributeError: 'NoneType' object has no attribute '__dict__'`. Register in `sys.modules` **before** `exec_module`. | Confusing import failure in any by-path test harness |
| **The supervisor is Windows-only at import** | `from ctypes import wintypes` at module level. Stub `sys.modules["ctypes.wintypes"]` to import on Linux; `evaluate_resource_gate`, `assert_paths_absent`, `_write_exclusive_fsync` and `_publish_owned_json` touch no Windows API and run unchanged. | Wrongly concluding transport logic is untestable off-Windows (I did, initially) |

---

## 8. M245 audit dispositions (this session)

| audit item | its rating | outcome |
|---|---|---|
| SPD theorem | THEOREM | **sound** — `1/(2√(q!))` on `t^{q+2}` "for all parities" is right because for `t > \|α\|` the mirror point sits on the inactive branch `rbar = mbar²` (degree q), so only the active half carries the top degree; no parity cancellation |
| replica identity | THEOREM | **sound** — `S[F]² = ¼[F(t)²+F(−t)²+2F(t)F(−t)]`, symmetry gives `E[F(G)²]=E[F(−G)²]` |
| Christoffel ⇒ importance sampling | REFUTED | **agree** — and it is the G4 pattern: a diagnostic with dominant coefficients is not a provider |
| Plackett endpoint pole | REFUTED | **arithmetic verified** — `0.50412² = 0.25414`, `√(1−0.25414) = 0.86363`, `1/0.86363 = 1.1579`; pole never on the path |
| logistic/Gompertz decay | UNSUPPORTED | **agree** — only `0 ≤ V_∞ ≤ K − P_8` is certified |
| **mpmath heuristic** | Medium/High | **FALSIFIED — the one real defect**, by interior-feature blindness, *not* the predeclared oscillatory aliasing (234 `sin(kx)` probes: **zero** false passes) |
| `G_Q` conditioning `OPEN_REQUIRES_RUN` | Medium/Medium | **PASS by 15 orders** — `κ(G_4) = 2.798e5` at α=0 (audit said ~2.7e5, **confirmed**); `κ(G_8) = 6.7e9–2.0e10` vs the `1e25` gate, at 60 dps not 80 |
| Transport Race 1 | High/High | **not reproduced** — `MAXIMUM_GAP_SECONDS` is a sampling-continuity bound, not a carry-forward age; the +0.11 s scenario yields `pass=False` (a hard FAIL, opposite sign); `rss_gate = max(sampled_peak, lifetime_sum)` is floored by OS counters, so suppressing samples cannot lower the bill |
| Transport Race 2 | High/High | **not reproduced** — fixed five-path namespace, no PID component; `assert_paths_absent` refuses to start; `open("xb")` refuses to overwrite |
| Transport Race 3 | High/High | **not reproduced and inverted** — the burn precedes the receipt (INTENT durable at 2308–2318, `_publish_r_and_capture_endpoint` at 2560; `EXPECTED_TRACE` idx 1 < 10). No attempt counter exists; policy is `no_retry`. **There is no 8-attempt limit to break.** |
| Completeness | Low/Low | **no counterexample** across 5 targets × 3 α; all residuals decrease monotonically. Not a proof of density. |

**Calibration note for the next agent.** The audit's *mathematics* was sound
everywhere checkable; its *risk ratings* were inverted — the three items rated
High/High dissolved on contact, and the single genuine defect was rated
second-lowest. **Run the cheapest falsifier before assigning the probability.**

### 8.1 Real weaknesses found in place of the predeclared ones

- **Sampler coverage hole.** The continuity gate bounds inter-sample *gaps* but
  never requires the series to *cover* the run. Two samples 1 ms apart in a 30 s
  run pass. Harmless for the RSS bill today only because `lifetime_sum`
  dominates — i.e. the sampler is not load-bearing for the quantity it appears
  to police. Repair: require `first_sample ≤ ε`, `wall_exit − last_sample ≤
  MAXIMUM_GAP_SECONDS`, and a minimum count `≈ wall_exit / NOMINAL_SAMPLE_SECONDS`
  (30 s ⇒ ~3000 samples, against the 2 that pass today).
- **Deterministic control-event names.** `control_event_names` derives from the
  intent SHA-256 prefix, so the same intent yields identical names across
  invocations. Safe under `no_retry` + namespace-absent; a collision surface if
  `no_retry` is ever relaxed.
- Structural note: `lifetime_sum = Σ_r max_t RSS_r(t)` while `sampled_peak ≈
  max_t Σ_r RSS_r(t)`, and `max_t Σ_r ≤ Σ_r max_t` always — so whenever peaks
  fall inside the measured window the charge is decided entirely by OS counters,
  and the `max` is a **one-way ratchet**: samples can raise the bill, never lower
  it.

---

## 9. Residual-error correlation among survivors

Unchanged from GEN6 and **not** re-measured this session. The GEN6 statement
stands: survivors' residuals are dominated by the four-point-vertex sector
(G2), which is why composing two G1-family survivors has repeatedly failed the
interaction test. Any new composition still requires the factorial or
residual-covariance test before promotion — nothing here relaxes that.

---

## 10. Holdout firewall (restated)

- Untouched holdout outcomes were **not** read, and are not exposed to mutation
  generation.
- Everything measured this session used **synthetic He-Gaussian weights** via
  `m200.generated_weights` with the `cell_seed` scheme of
  `gm_m179_m199/diag_spd_depth.py`, or pure mpmath/stdlib.
- **No** truth arrays, scorer, holdout, private data, leaderboard, submission,
  network access, or champion mutation. No fixture evaluated, no shard launched.
- **No estimator, variance, MSE, or score claim** is made by any artifact added
  this session. The SPD work measures *definedness*, not accuracy.
- Frozen artifacts (`m179_background_producer.py`,
  `supervise_m245_fixture_materialization.py`, all `*_SHA256SUMS_*`) were read
  **read-only** and never edited; the spectral guard is additive precisely to
  preserve those manifests.

---

## 11. Reproduction

```bash
pip install -r requirements.txt                  # networkx, numpy
python -m unittest discover -s tests -v          # 15 tests, includes the guard

cd corpus/whestbench/experiments/gm_spd_width_scaling
python3 run_spd_width_scaling.py --widths 64,96,128,160,192,224 --reps 4 --controls
python3 run_spd_width_scaling.py --widths 32,40,48,56,72,80 --reps 8 --out transition.json
python3 analyze.py                               # 96 cells, 6 overlaps, 0 conflicts

cd ../gm_mpquad_error_contract
python3 falsify_mpquad_error.py                  # predeclared probe: NOT falsified
python3 falsify_mpquad_interior.py               # FALSIFIED, 15 cases

cd ../gm_transport_race_audit                    # needs PR #1's supervisor
python3 falsify_transport_race1.py
python3 falsify_transport_race23.py              # 9/9

cd ../gm_m245_completeness
python3 check_completeness.py --alpha 0.0  --qmax 8 --dps 60 --order 60 --order2 48
python3 check_completeness.py --alpha -0.6 --qmax 8 --dps 60 --order 60 --order2 48
```

Anything reading `supervise_m245_fixture_materialization.py` requires PR #1's
branch; the scripts refuse with an explicit message rather than vendoring a
frozen artifact.

---

## 12. Verdict

The two score levers are at measured walls and the buildable budget is **~2.2x**,
short of the `4.3x` top-12 bar. The exact-control chain is `KILL_CONFIRMED`, and
this session supplied its *mechanism*: at production width the closure is not
inaccurate, it is **undefined**, with a guard that has never fired.

That makes the **Algorithmic Contribution** the live deliverable — a measured
ceiling on an entire method family, established two independent ways (R² = 0.287
from the control side, 311x plus PSD loss from the prediction side), with a named
obstruction and certified reference code. Nobody publishes the ceiling.

**The single highest-value next action is §6**, because it is the only untested
route in G7 and it resolves in one ~100-second measurement.

**Before any filing cites M178/M179 as certified:** land the spectral guard and
record what it refuses. A provider that silently propagates non-PSD state through
two thirds of its output layers should not carry that word.
