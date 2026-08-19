# Designation policy — pre-positioned for the Phase-2 rules post

Written 2026-08-19, **before** the Phase-2 rules landed, so that the designation
call is a lookup and not a deliberation on the day. Nothing here designates
anything: it names, per rule fork, which candidate goes in which slot, what must
be measured first, and the two zero-cost questions that go to the organizers the
hour the rules post.

Evidence tags: **[O]** observed (run or read this session) · **[D]** derived from
observations by shown steps · **[R]** reported by a document or a third party ·
**[A]** assumed. Every load-bearing number carries one.

Designation lock: **Sep 19**. Private re-run: **2026-09-20..30**, the only ranking
that pays. [R: `CONTINUATION_PLAN_20260817.md` §0c, §1.4]

---

## 0. The four facts the whole tree rests on

**F1 — the scoring law.** `S = MSE x max(FLOOR, C/B)`, `B = 2.72e11`, and
`C = analytical_FLOPs + 100e9 x residual_seconds`. The decomposition was verified
in source and receipts. [O: channel 2026-08-18 ~19:0x; law also at
`AGENT_CHANNEL.md:3478`, `:8711`; `B` at
`handoff/ORGANIZER_CLARIFICATION_QUESTIONS_20260807.md` Q1]

**F2 — the incumbent's anchor.** `row_blocked_production`: `C = 222.405e9`,
public-100 `S = 2.1218e-7`, standing ~7th on publicly declared adjusted scores.
[O: channel 2026-08-18 ~16:4x, ~18:2x, ~20:0x] From F1 this pins the raw
suite MSE at **`2.594949e-7`** [D, computed this session], and that number is
invariant under every lever in the candidate set except the 129 swap — the fold
is an exact reschedule, so it moves `C` alone.

**F3 — the flat-budget theorem** (trim_qewas, organizer-reproduced; competitor
topic 18182 [R — the topic id is reported to me, not verified against Discourse
this session; the theorem itself is corroborated in the sweep at channel
2026-08-18 ~16:0x]). For a pure Monte-Carlo estimator `MSE = sigma^2/N` and
`C = cN`, so above the floor `S = sigma^2 c / B` for **every** `N`, and at the
floor point `N* = FLOOR·B/c` it takes the same value; below `N*` it is strictly
worse. Floor-drop is therefore exactly neutral for pure MC. Verified numerically
this session at both candidate floors: ratio to `N*` is `1.000000` at
`N* , 2N* , 8N* , 64N*` and `2.0 / 8.0` at `N*/2, N*/8`. [O]

The consequence that governs this memo: **the theorem does not cover us.** Our
MSE is decoupled from `C` (a deterministic design, not a sample count), so both
live levers sit in the two regimes the theorem excludes — (i) exact reschedule
(MSE fixed, `C` down) and (ii) MSE down at fixed `C`. It also tells us no rival
can gain by dialling `N` down, which is why every declared gain ahead of us reads
as prediction-preserving arithmetic. [D from F3 + channel 2026-08-18 ~16:0x]

**F4 — suite-draw variance is almost entirely idiosyncratic.** S1 measured the
rotation-draw component at **99.79%** of across-suite variance
(`vF·(1+vD) = 0.3645` vs `vD = 7.6e-4`). [O:
`experiments/s1_suite_risk/S1_VERDICT.md`] So the net-difficulty component that
would cancel in a head-to-head ranking against rivals on a shared suite is worth
0.21% — **rank noise on the private re-run is essentially our full suite noise.**
S1's model is multiplicative (`MSE = S·D·mean(F_1..F_R)`), so its coefficient of
variation transfers to any mean: **CV = 0.08541 at R=1, 0.03507 at R=6**, on a
50-net suite. [D, computed this session from S1's own table] S1's Limitation 1
records that the model understates the tail (simulated 80-net spread 9.14-11.94x
vs observed 15.53x), so these are lower bounds.

---

## 1. The candidate set, priced across the forks

All numbers below computed this session from F1/F2 [O]. `m` is the residual-wall
multiplier the depth-6 route realizes against the deployed 0.1606 s/net;
`C_post(m) = (126.7 + 18.815·m)e9` [O: channel 2026-08-18 ~19:0x, ~20:5x], and
`m ≈ 2` is **measured** on probe nets (residual ratio 1.86-2.03, flops ratio
0.712-0.725, effective-C ratio 0.811-0.829) [O: channel 2026-08-18 ~21:2x].

### 1a. λ survives (residual seconds priced into C) — the current law

| Candidate | C | C/B | Score | vs incumbent |
|---|---|---|---|---|
| incumbent `row_blocked` | 222.4B | 0.8177 | 2.1218e-7 | 1.000x |
| fold, m=1 | 145.5B | 0.5350 | 1.3882e-7 | 0.654x |
| **fold, m=2 (measured)** | 164.3B | 0.6042 | **1.5677e-7** | 0.739x |
| fold, m=3 | 183.1B | 0.6733 | 1.7472e-7 | 0.823x |
| 129 swap alone @0.78 | 222.4B | 0.8177 | 1.6550e-7 | 0.780x |
| 129 swap alone @0.86 | 222.4B | 0.8177 | 1.8247e-7 | 0.860x |
| **fold m=2 + 129 @0.78** | 164.3B | 0.6042 | **1.2228e-7** | 0.576x |
| fold m=2 + 129 @0.82 | 164.3B | 0.6042 | 1.2856e-7 | 0.606x |
| **fold m=2 + 129 @0.86** | 164.3B | 0.6042 | **1.3483e-7** | 0.635x |

Cross-checks that hold: the m-curve ratios reproduce the triple-derived
`0.6542 / 0.7387 / 0.8232` at m = 1/2/3 [O: channel 2026-08-18 ~20:5x]; the
falsifier line `C >= 200B` trips at `m = 3.9`; break-even against the incumbent at
`m* = 5.085`. Measured `m ≈ 2` sits far inside both.

**Floor is inert on this branch.** Every candidate has `C/B ∈ [0.535, 0.818]`,
above both 0.1 and 0.5. Recomputed at `FLOOR = 0.5`: every score in the table is
**identical to the last digit**. [O, this session] This sharpens rather than
contradicts the channel's ~16:4x note that the floor question "is now MATERIAL":
that entry's concern was proximity — the superseded 153.5B estimate sat only just
above the 136B binding point, so further compute work would hit the wall. On the
revised m-curve the fold bottoms at 145.5B (m=1) and the floor still does not
bind here. **Materiality has moved off this branch entirely and onto λ-dies**
(§1b), where the fold crosses below 136B outright.

### 1b. λ dies (residual channel deleted)

`m` becomes irrelevant — the fold's C collapses to its analytical part, 126.7B,
and the entire m-risk evaporates.

| Candidate | C | C/B | Score @0.1 | Score @0.5 | floor binds? |
|---|---|---|---|---|---|
| incumbent (analytical only) | 174.8-177.9B [D] | 0.643-0.654 | 1.667-1.698e-7 | same | no |
| **fold** | 126.7B [O] | **0.4658** | **1.2088e-7** | **1.2975e-7** | **yes at 0.5** |
| fold + 129 @0.78 | 126.7B | 0.4658 | 9.4283e-8 | 1.0120e-7 | yes at 0.5 |
| fold + 129 @0.86 | 126.7B | 0.4658 | 1.0395e-7 | 1.1158e-7 | yes at 0.5 |

The incumbent's analytical-only C is **[D]**, back-solved from the fold's measured
flops ratio 0.712-0.725; it is the one number in this memo that must be read
directly off the itemized receipt before it is used (see §3, M4).

**This is the only branch where the floor question changes a number.** The fold
crosses below `C/B = 0.5`, so the answer is worth exactly **1.0734x** on the fold
(1.2975e-7 at floor 0.5 vs 1.2088e-7 at floor 0.1) [O, computed]. Note the MSE
lever keeps paying at the floor — 129@0.78 on top of a floored fold still buys
0.780x — because the floor caps the multiplier, not the MSE.

### 1c. λ capped at a per-MLP wall-time ceiling τ

The fold as built runs at `m ≈ 2`, i.e. `≈ 0.321 s/net` against the incumbent's
0.1606. [O: channel 2026-08-18 ~19:0x, ~21:2x]

| τ (s/net) | max m | fold as built | C | Score |
|---|---|---|---|---|
| 0.1606 (incumbent's own) | 1.00 | **does not fit** | 145.5B if re-engineered | 1.3882e-7 |
| 0.20 | 1.25 | does not fit | 150.1B | 1.4323e-7 |
| 0.25 | 1.56 | does not fit | 156.0B | 1.4882e-7 |
| 0.3212 | 2.00 | fits | 164.3B | 1.5677e-7 |
| 0.50 | 3.11 | fits | 164.3B | 1.5677e-7 |

The perverse structure worth seeing before the day: **a tight cap is score-good
and admissibility-bad.** Forcing `m ≤ 1` would improve the fold to 1.3882e-7 —
but only if the route can actually be made to run inside τ, which is unproven
engineering, not a pricing choice. A cap at or below the incumbent's own residual
makes the fold inadmissible as built.

---

## 2. The decision tree

Twelve leaves: λ (survives / dies / capped) × FLOOR (0.1 / 0.5) × slots (2 / 1).
The FLOOR axis is **provably inert** except under λ-dies (§1a: identical scores to
the last digit at both floors), so those leaves are collapsed with the arithmetic
that licenses the collapse. Slot-1 policy is "highest expected rank"; slot-2
policy is the standing recommendation — **highest-variance lawful candidate, not
second-safest; expected value is the wrong criterion for a second slot** [R:
`CONTINUATION_PLAN_20260817.md` §6].

### The three statistical warrants used at every leaf

**W1 — portfolio (measured).** S4, 100,000 suites per cell, harness cross-checked
against S1 through a different sampling route (SD ratio 0.9958). [O:
`experiments/s4_portfolio/S4_VERDICT.md`]

| Threshold | 1 slot | 2 decorrelated slots | gain |
|---|---|---|---|
| 1.55e-7 | 0.0285 | 0.0570 | **+2.85 pp (2.00x)** |
| 1.60e-7 | 0.0637 | 0.1237 | **+6.00 pp (1.94x)** |
| 1.70e-7 | 0.2063 | 0.3713 | **+16.50 pp (1.80x)** |

Two *correlated* slots buy nothing (rho=1 collapses to the single-entry column),
and a second entry built for variance reduction (R=6) adds `+0.00/+0.00/+1.53 pp`
— it removes exactly the tail mass a portfolio needs. **Variance reduction is a
defence play; decorrelation is the offence play.** The Phase-1 pair
(#326094 / #327519, bit-exact twins [O: channel 2026-08-10 15:4x]) sat at rho=1
and carried zero portfolio value; do not reproduce that shape in Phase 2.

**W2 — multiplicity and power (re-run this session).** Codex's two calibrators
both execute offline on this machine and both reproduce his committed reports.
[O — entry points `pyproject.toml:29-30`; sources
`src/headroom_recursion/folding/{policy_simulation,joint_fwer_simulation}.py`]

- `whest-fwer-calibrate` at full budget — 1476 cells × 20,000 campaigns =
  **29.52M campaigns, 3m55s, `BOUNDED_JOINT_PASS`**. Joint allocated alpha
  `5/128 = 0.0390625`; per-cell tail budget `1/147600`; max accepted campaign
  errors per cell 664; **worst observed cell 70 errors / 20,000** in
  `predictable_adaptive_scale · independent · forced_null_winner_amid_7_alternatives`;
  **0 of 1476 cells failed**. Structural diff against
  `experiments/whest/reports/joint-fwer-switchpoint-calibration.json`: **exactly one
  differing leaf out of the whole report** (see the honesty note below).
- `whest-policy-calibrate` (fractal ladder, 20,000 campaigns) — `KERNEL_FAIL`,
  and the committed reference fails identically. Null side **passes** (worst
  simulated false-promotion rate 28/20,000 = 0.0014, Hoeffding bound 0.01430,
  under `horizon_alpha = 63/3200 = 0.019688`); power side **fails**:
  **8224/20,000 = 41.12% against a 90% floor** at a planted effect of mean 0.27,
  half-width 0.1. Structural diff against
  `promotion-policy-fractal-graph-calibration.json`: **one differing leaf**.

**W3 — the R-posture is two-sided, and no rule fork decides it.** Rotation
splitting is mean-preserving and budget-free (S1 measured the mean shift at
+0.021%), so it is a pure variance dial. It is also symmetric: it buys the
defended position by spending the overtake mass. Priced at the leaves that
matter, `P(beat rival)` at R=1 → R=6 [D, lognormal marginal matched to S1's mean
and its measured CV]:

| Candidate (mean) | vs ely2sh 1.196e-7 | vs pranay212 1.23e-7 | vs mliston 1.334e-7 | vs Puffi 9.10e-8 |
|---|---|---|---|---|
| fold m=2 + 129@0.82 (1.286e-7) | 0.211 → **0.021** | 0.317 → **0.107** | 0.683 → **0.858** | 0.000 → 0.000 |
| fold alone, λ-dies @0.1 (1.209e-7) | 0.467 → 0.388 | 0.598 → 0.697 | 0.885 → **0.998** | 0.001 → 0.000 |
| fold + 129@0.82, λ-dies @0.1 (9.91e-8) | 0.988 → **1.000** | 0.995 → **1.000** | 1.000 → 1.000 | 0.169 → **0.008** |

Read the row, not the headline: R=6 raises every lock below us toward certainty
and collapses every reach above us toward zero. **R is therefore chosen last, in
September, from the position we actually hold** — S1's own rule — and it is listed
in each leaf below as a default that the September board can overturn, never as a
consequence of the rule fork.

**What W2 means for designation, stated at its earned level.** The promotion
kernel is calibrated to be Type-I-safe and is measurably underpowered. That
asymmetry is the *right* shape for slot 1 (never designate a candidate whose gain
could be noise) and the *wrong* shape for slot 2 (where a 41%-detected real effect
is exactly the bet worth taking). This is the statistical warrant for the
asymmetric slot policy, not a decoration on it.

**Honesty note on W2, carried rather than buried.** In both reproductions the one
differing field is the promotion-policy digest — mine
`3be59fa3b24ff14aa8d0e904d0bce530de77dd6cb1cc8ed69d192d3cc45434f8`, the reports of
record `239abfb1417067a74c9abee3bdadd2f0e3767a29c972cdf67733d67a86be88bf` — while
every simulated quantity is identical. The on-disk
`experiments/whest/cases/promotion-policy-v3.json` is untracked (`git status` =
`??`), so the policy-of-record cannot be recovered from history. The difference
therefore lies in a field the kernel does not consume. **Cause not isolated.**
Settling check, ~10 minutes: bisect the canonical bytes against the digest in
`promotion.py:505`. This is a provenance defect in a predeclared-gate artifact and
it must be closed before any designation cites a FWER number as authority.

### 2.1 λ SURVIVES — floor 0.1 or 0.5 (identical; §1a)

| | **2 slots** | **1 slot** |
|---|---|---|
| **Designate** | **Slot 1: fold m=2 + 129 swap** (1.22-1.35e-7). **Slot 2: fold m=2 alone** (1.5677e-7), decorrelated from slot 1 by grader-rooted seed spawning. | **fold m=2 + 129 swap** if the 129 cell clears its predeclared margin; **fold m=2 alone** if the cell returns INCONCLUSIVE. |
| **Why** | Slot 1 takes the best measured mean. Slot 2 is *not* the second-best mean — it is the candidate that fails independently: it shares no MSE mechanism with slot 1, so a 129 regression on fresh seeds cannot take both. W1 prices the decorrelation at +2.85/+6.00/+16.50 pp; W2 licenses putting the underpowered-but-real 129 gain in the slot whose job is variance. | With one slot the portfolio lever is gone and the R-choice becomes the entire play. At 1.29e-7 we land mid-band — ahead of mliston/baltsat/SOX, behind ely2sh/pranay212 — which is the position W3 shows R cannot resolve for free: **R=6** takes mliston from 0.68 to 0.86 and simultaneously gives up ely2sh (0.21 → 0.02). **Default R=1** while any rival above us is reachable; flip to R=6 only if the September board puts our expected score ahead of the nearest one. |
| **If the 129 cell fails (>0.95)** | Slot 1: fold m=2 (1.5677e-7). Slot 2: fold m=1 variant if the residual can be halved, else a decorrelated seed-map twin of slot 1 — W1's +6.00 pp is available at zero research risk. | fold m=2, R=1. At 1.5677e-7 we are a chaser against the whole 1.19-1.55e-7 band and must keep the overtake mass. |

### 2.2 λ DIES — **floor 0.1**

| | **2 slots** | **1 slot** |
|---|---|---|
| **Designate** | **Slot 1: fold + 129 swap** (9.43e-8 to 1.04e-7). **Slot 2: fold alone** (1.2088e-7). | **fold + 129 swap** on a cleared cell; **fold alone** otherwise. |
| **Why** | This is the branch the campaign pre-committed to as primary [R: `CONTINUATION_PLAN_20260817.md` §0c]. The fold's m-risk is gone, so the fold is unambiguous and the only live uncertainty is the 129 MSE ratio — exactly the uncertainty slot 2 exists to hedge. At 9.4e-8 slot 1 would sit at or ahead of the declared front (Puffi 9.10e-8 [R]). | Same choice, no hedge. **R is a genuine fork here, not a default.** At ~9.9e-8 we sit level with the declared front: W3 prices R=6 as locking every rival below us to ~1.000 while cutting the overtake of Puffi from 0.169 to 0.008. That is "certainty of second against a one-in-six shot at first" — a prize-structure question the September board settles, not a rules question. Carry both postures to Sep 19. |
| **Also true here** | Every wall-heavy candidate held under §5 of the continuation plan releases at once, and the Codex-clone survivors become clean wins [R: `CONTINUATION_PLAN_20260817.md` §2]. Those are *later* levers; they do not change this designation. | |

### 2.3 λ DIES — **floor 0.5** (the one leaf where the floor bites)

| | **2 slots** | **1 slot** |
|---|---|---|
| **Designate** | **Slot 1: fold + 129 swap** (1.012e-7 to 1.116e-7). **Slot 2: fold alone** (1.2975e-7). | **fold + 129 swap** on a cleared cell; **fold alone** otherwise. |
| **Why** | Same ordering as 2.2 — but every score is 1.0734x worse because the multiplier is pinned at 0.5 while C/B sits at 0.4658. Critically, **the ordering does not change**: the floor caps the multiplier, not the MSE, so the 129 swap still pays its full 0.780x. Designation is therefore floor-robust; only the expected placement moves. | Same choice. The R fork is the same as 2.2 but leans further toward defence: the floor costs us 7.34%, which pushes our mean to ~1.06e-7 and drops the Puffi overtake to 0.037 at R=1 — the reach is nearly gone, so **default R=6** and hold the locked band. |
| **The trap to name out loud** | At floor 0.5 the compute lane's terminal ceiling is `C = 136B` — every FLOP removed below that is worth **exactly zero**. Any Phase-2 compute work planned after designation must be re-justified against that wall. At floor 0.1 the ceiling is `C = 27.2B` and the lane stays open. | |

### 2.4 λ CAPPED — floor 0.1 or 0.5 (identical unless τ < 0.0794 s/net)

A cap bounds `C` from above, so the floor can only bite if τ is tight enough to
force `C < 136B`, i.e. `m < 0.4943`, i.e. **τ < 0.0794 s/net** — half the
incumbent's own residual. [D, this session] At any plausible cap the floor axis is
inert here and 2.3's ceiling warning does not apply.

| | **2 slots** | **1 slot** |
|---|---|---|
| **τ ≥ 0.3212 s/net** | Identical to 2.1 — the fold fits as built. | Identical to 2.1. |
| **τ < 0.3212 s/net** | **Slot 1: incumbent `row_blocked` (2.1218e-7), unmodified.** **Slot 2: the re-engineered fold**, designated only if it is measured admissible inside τ before Sep 19. | **incumbent**, unless the re-engineered fold has a *measured* admissible run. |
| **Why** | This is the only leaf where the incumbent is the right slot-1 answer, and the reason is admissibility, not score. A designated entry that breaches a hard wall-time clause scores nothing; a 0.739x improvement is not worth a non-zero probability of a void submission. Slot 2 is precisely where an admissibility gamble belongs — its failure costs the slot, not the campaign. W2's shape says the same thing: put the thing that might not clear its gate in the slot built to absorb that. | With one slot the gamble is unaffordable. Designate the incumbent and spend Phase 2 making the fold fit for the write-up rather than the score. |

### 2.5 What no leaf changes

- **Nothing is designated on an unrun cell.** Every leaf above that names the 129
  swap is conditional on the cell clearing its own predeclared margin
  (pre-registered band **0.78-0.86**, falsifier **MSE ratio > 0.95**) [O: channel
  2026-08-19 ~01:0x]. On INCONCLUSIVE the fallback in each cell applies.
- **Never two correlated slots.** W1 measures that shape at zero value.
- **R is chosen last**, from the position we actually hold against the field, per
  S1's rule — chaser keeps R=1 and the overtake mass, leader takes R=6 and the
  defended position. [R: `S1_VERDICT.md`; `ORACLE_PASS_DESIGNATION_20260810.md`]
- **FlopScope-mandatory is orthogonal to the choice** but adds a metered port to
  every designated candidate; it changes the schedule, not the ranking. [R:
  `CONTINUATION_PLAN_20260817.md` §2]

---

## 3. What must be measured before designation, per leaf

Every item is already queued or named in the record; none is new work invented by
this memo.

| # | Measurement | Gates which leaves | Status |
|---|---|---|---|
| **M1** | **The one Public100 re-measurement of the fold** — billed C + per-net raw-MSE parity + wall residual, recorded together in a single run with the frozen argv in the frozen venv. Parity law: per-net `\|MSE ratio − 1\| ≤ 5e-4`, aggregate `≤ 1e-4`. | **All twelve.** Nothing is designated on the m-curve prediction. | Queued behind the D1/D5/D6 fix round and a re-verify against the candidate's own `FOLD_FLOOR_SPLICE_PRODUCTION_GATE.md`. [O: channel 2026-08-19 ~00:3x] |
| **M2** | **The 129 cell, three arms** (126-Haar / 129-MUB / Kerdock-126), studentized metric, 5% margin from measured bootstrap power, identity frame last, per-net Haar rotation. | Every leaf naming the 129 swap. | Designed and ready; harness runs **HELD** until M1 completes — CPU contention would pollute both runs' residual seconds. [O: channel 2026-08-18 ~22:3x] |
| **M3** | **The 129 swap's own compute cost.** The cell discharges MSE but **not memory** (+2.25 MiB, routed to a separate build stage on PASS), and its effect on billed C is not yet a measured number. | 2.1-2.3 slot 1. A 129 swap that raises C can erase its own MSE gain. | Named in the cell design; **must be read off the same receipt as M2**. [O: channel 2026-08-18 ~22:3x] |
| **M4** | **The incumbent's analytical-only C**, read directly from the itemized FlopScope receipt with the residual term zeroed. | 2.2, 2.3 — it is the only [D] number in the λ-dies table and the whole branch's comparison baseline. | Free; the receipt is already itemized by the verified decomposition `C = analytical + 100e9 × residual_seconds`. [O: channel 2026-08-18 ~19:0x] |
| **M5** | **The fold's residual seconds under the cap**, measured on the Public100 harness rather than probe nets. Probe measurement is 1.86-2.03x the deployed 0.1606 s/net. | All of 2.4. Admissibility is a measured fact or it is not a fact. | Falls out of M1's wall trace. [O: channel 2026-08-18 ~21:2x] |
| **M6** | **Slot decorrelation legality and construction** — the rules read for a materially-identical / duplicate-entry clause, then grader-rooted spawning (`master = default_rng(mlp.seed)`; `spawn(2)`; predeclared child index; never search indices). | Every 2-slot leaf. Phase-1 sources permitted it; **Phase-2 sources conflict** and no designation may rely on it without written confirmation. | Mechanism settled and superseded-once; legality read is a rules-post action. [R: `ORACLE_PASS_DESIGNATION_20260810.md` Door B] |
| **M7** | **The 1 GiB resource-ceiling provenance**, independently confirmed by the verifier. The fold measured 615.68 MiB peak; 512 MiB was the incumbent's self-declaration, not law. | Any leaf designating the fold. | Named in the loop-3 ruling as a verifier obligation. [O: channel 2026-08-19 ~00:3x] |
| **M8** | **The promotion-policy digest reconciliation** (W2 honesty note). | Any leaf whose write-up or predeclaration cites a FWER number as authority. | ~10 minutes; not yet queued — **this memo queues it.** [O, this session] |

Sequencing that the record already fixes: **M1 → (M2 + M3) → designation**, with
M4/M8 runnable in parallel today, M6 firing the hour the rules post, and M5/M7
falling out of M1.

---

## 4. The two questions to send the organizers the moment the rules land

Both are zero-cost, both are documented inconsistencies rather than requests for
advantage, and both should go in one short message the hour the rules post.

### Q1 — Which score floor is authoritative for Phase-2 grading, 0.1 or 0.5?

> The score law is `S = MSE x max(FLOOR, C/B)` with `B = 2.72e11`. The starter-kit
> and official materials record `FLOOR = 0.1`; the overview page records
> `FLOOR = 0.5`. Which value governs Phase-2 grading and the private re-run?

**Why it is asked, in the message:** the two values are not equivalent for a
deterministic estimator. The flat-budget theorem recently reproduced on the forum
shows the floor is irrelevant to a pure Monte-Carlo entry — every budget above
`N*` scores identically at either floor — but our estimator's error is decoupled
from its sample count, so the floor is a hard ceiling on the compute lane rather
than a neutral constant. **What the answer changes for us, precisely:** our
post-fold `C/B` lands at `0.4658` if residual wall time is not priced, which is
below 0.5 and above 0.1; the answer is worth `1.0734x` on our score and moves the
terminal value of all further compute work from `C = 27.2B` to `C = 136B`.

Standing status: forum treated as authoritative for 0.1, the overview page's 0.5
read as a doc inconsistency rather than a Phase-2 change — but that reading is
ours, unconfirmed, and it is now load-bearing. [R:
`CONTINUATION_PLAN_20260817.md` §0c; drafted long-form as Q1 in
`handoff/ORGANIZER_CLARIFICATION_QUESTIONS_20260807.md`]

### Q2 — How many entries may a team designate for the private re-run, one or two?

> Rules v12 §5.3 reads "designate one (1)"; the submission site presents two
> slots; Phase 1 was selected with two. A contestant raised the conflict on the
> forum and it is unanswered. Which governs Phase 2, and if two: are materially
> identical or seed-variant entries permitted in both slots?

**Why it is asked, in the message:** the answer changes the designation
construction, not merely the count. Our own bootstrap over 100,000 simulated
suites measures a second *decorrelated* entry as worth +2.85 / +6.00 / +16.50
percentage points of hit probability at the three thresholds we care about, and a
second *correlated* entry as worth zero — so the count and the duplicate rule
together decide whether the second slot is a portfolio or a formality. We will not
build a seed-variant entry without a written answer to the second half.

Standing status: "Rules v12 s5.3 'designate one (1)' vs the site's two", flagged
and unwalked since 2026-08-10; the Phase-1 pair we advanced were bit-exact twins.
[O: `AGENT_CHANNEL.md:2822`; channel 2026-08-10 15:4x]

**Do not bundle a third question.** Q3-Q5 of the 2026-08-07 draft (native-backend
pricing, deadline reconciliation, prize overlap) are either superseded or
non-blocking for designation; adding them dilutes two questions that each name a
specific decision they unblock.

---

## 5. Residual risk on this memo

- **The rules had not posted when this was written.** Every leaf is conditional on
  the fork text; if Phase 2 introduces a fork this tree does not have an axis for
  — a seed-protocol change, a per-account limit, an eligibility clause — the tree
  is void on that axis and the Ψ response applies: re-verify both slots against
  the new text the hour it posts. [R: `WHAT_IF_FORECAST_20260817.md` Ψ]
- **Every score in §1 is a prediction until M1 lands.** The m-curve is
  triple-derived and `m ≈ 2` is measured on probe nets, not on the Public100.
- **The λ-dies incumbent baseline is [D], not [O]** — back-solved from a probe
  flops ratio. M4 settles it and costs nothing.
- **The rival scores are [R]** — publicly declared, never verified by us, and one
  of them (ednacob 1.845e-8) sits below what kaileh57's Arb-certified LP permits
  any fixed nonnegative rule at that support. Treat the front as unreliable and
  the reachable band (1.19-1.55e-7) as the real target. [R: channel 2026-08-18
  ~16:0x]
- **S1/S4's variance model is a 50-net suite.** If the private suite is 100 nets
  the model's own `1/sqrt(n)` law puts CV at 0.06039 (R=1) / 0.02480 (R=6); the
  qualitative ordering of every leaf is unchanged, the P(beat) figures are not.
  S1's own limitation — the model understates the observed tail — makes all widths
  lower bounds.
- **W2's calibration is a bounded synthetic family, not proof.** Codex's own
  report records `production_strong_fwer_established = false` and
  `conditional_null_assumption_verified = false`; the scope line disclaims proof of
  the real suite conditional null, signed preregistration, and global slot
  uniqueness. It is used here as a warrant for a *policy shape*, and for nothing
  stronger.
