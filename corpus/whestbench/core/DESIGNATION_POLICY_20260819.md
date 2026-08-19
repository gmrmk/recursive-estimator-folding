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

> **BANNER ADDED 2026-08-19 BY THE v2 REVISION BLOCK (see the end of this file).**
> Sections 1, 2 and 3 below are v1 and are **superseded on their numbers**. The fold
> is priced there at a `C` ratio of `0.739`; the measured paired ratio is
> `0.8388/0.8447`, and on the measured basis the folded `row_blocked` candidate is
> **worse than the unfolded `kerdock_v3` candidate we already hold**. The band quoted
> in §2.5 is the superseded `0.78-0.86`. Nothing in v1 has been deleted — read it for
> the reasoning, then take every number from v2. The v2 tables are the output of
> `core/designation_repricing.py`.

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

---

# v2 — REVISION BLOCK, 2026-08-19 (append-only; v1 above is unaltered)

Filed against the four-lens ultrareview and its adversarial merge (`wf_b708199c-ca4`;
full report `tasks/wgrvbok7a.output`; channel entry 2026-08-19T07:07:56Z). v2 repairs
six defects in v1's arithmetic. It changes numbers and two leaf answers. It does not
change v1's slot doctrine, its warrants W1-W3, or its measurement queue.

**The caveat that travels with every number below that is derived from
`experiments/fold_floor_splice/full.json`: pending round-4 bill repair re-run.** The
committed `full.json` was produced under a static bill known wrong in both directions
(an unpriced `m*n` copy-out on the fallback branch, and an `m*k` operand copy charged
to a direct branch that never performs it), and that bill drives route selection, so
every measured ratio here can move in either direction when the sweep is re-run.
[O: `FOLD_FLOOR_SPLICE_PRODUCTION_GATE.md` addendum 2026-08-19T06:12:13Z;
`candidate_source/depth6_winograd.py:939-941`]

---

## v2.0 The verdict in one paragraph

On the measured paired basis the fold is not a slot-1 candidate on the `row_blocked`
host. Folded `row_blocked` lands at `1.780e-7` against the unfolded `kerdock_v3`
candidate already in hand at `1.6190838e-7`: the fold **loses by 9.9%**. v1's `0.739`
came from dividing a local-scale analytical absolute by a record-scale total. The
fold's value survives only as part of the `fold + 129` stack, and only if the 129 cell
returns a raw-MSE ratio at or below **`r* = 0.8886`**, which is inside the amended band
`[0.78, 0.93]` but excludes its upper quarter. The host fork is therefore the whole
decision rather than a tiebreak.

---

## v2.1 The method fix — price by ratio, on one stated scale

v1 formed absolutes: it back-solved a suite MSE from one network's `C`, then rebuilt
each candidate's `C` from a hand-carried curve. v2 never forms an absolute. It prices
every candidate as a **ratio against the incumbent's own recorded public-100 score**,
because that recorded number already carries its own suite MSE and its own per-network
multipliers.

Two checks were cited to license the change, both in the script's `--selfcheck`. The
second one holds. **The first does not, and is withdrawn as a licence below.**

1. **WITHDRAWN 2026-08-19 (hostile verify): this check is an identity, not a licence.**
   `1.6190837992231567e-7 / 2.121762464e-7 = 0.763084382` does agree to nine digits with
   the figure printed in T4's `mean ratio` column — but that column is itself the ratio
   of the two aggregate scores, not a mean of per-network ratios. Two signals establish
   that: T4's *other* row reproduces the same way from its own two aggregates
   (`1.6190837992231567e-7 / 2.101976249e-7 = 0.770267409` against its printed
   `0.770267409`), and a mean of per-network ratios could not track a ratio of means to
   ten significant figures on a suite with 65/100 paired wins and a heavy win-side tail.
   T4's bootstrap is also 200,000 resamples, seed 20260808, not a million. Both sides of
   the comparison are the same quantity, so it passes by construction and warrants
   nothing. [O: `T4_REPORT.md` rows 26-27, both recomputed exactly] What survives is
   algebra rather than that check: the adjusted score is `mean_i(MSE_i x mult_i)`, so a
   `C` change that is a **common factor across networks** and stays above the floor
   moves the score by exactly that factor [D]. Whether the fold's `C` ratio is common
   across networks is the per-network receipt named in v2.10, and it is **UNSETTLED**.
2. **Products of aggregates do not.** The incumbent's own recorded raw MSE times its
   own mean multiplier is `3.089460087e-7 x 189.852556e9/2.72e11 = 2.1564e-7`, against
   the recorded score `2.121762464e-7`. The product form over-states by **+1.633%** on
   the very suite it is computed from. The production report says so in its own words:
   "This is a true paired score comparison, not a product of aggregate ratios." [O]

**The one scale, stated.** Every v2 table is on the **deployed suite-mean basis** for
`row_blocked`: `C = 189.852556e9`, analytical `= 173.794058e9`, residual
`= 0.160585 s/net`, recorded score `2.121762464e-7`, recorded raw MSE `3.089460087e-7`,
all measured over the same 100 scored networks the score lives on. [O:
`experiments/ROW_BLOCKED_WINOGRAD_PRODUCTION_REPORT.md`, child column] The two other
scales in the record are named here once so they are never silently mixed again:

| scale | analytical | residual term | total `C` | what it is |
|---|---:|---:|---:|---|
| **suite mean (v2's basis)** | `173.794058B` [O] | `16.0585B` [O] | `189.852556B` [O] | mean over all 100 scored nets |
| record max-`C` net | `203.590357B` [D] | `18.815B` [D] | `222.405357B` [O] | one network, the worst-case `C` |
| local paired probe | `186.406006B` [O] | `16.072830B` [O] | `202.478836B` [O] | 2 synthetic nets, `full.json` parent |

The residual halves agree across all three (`0.160585` deployed mean against
`0.160728 / 0.158453` on the probe nets, inside 0.1% and 1.3%). The analytical halves
do not, and that is where v1's error lives.

---

## v2.2 The scale mix that produced the old headline (B2 / rank-1)

v1 §1 priced `C_post(m) = (126.7 + 18.815m)e9` over `222.405357e9`. The numerator's
`126.7e9` is a **local-scale** analytical quantity, measured against a local paired
parent of `202.478836e9`. The denominator's `222.405357e9` is the **record max-`C`
network**. The two belong to different populations, and the ratio between them is not
a compute saving.

Three arithmetic consequences, each checkable:

- **The old headline reproduces exactly, so this is not a straw man.**
  `(126.7 + 2 x 18.815)/222.405357 = 0.738876`, times `2.121762464e-7` gives
  `1.5677e-7`. That is v1 §1a's row, to the digit. [O, `--selfcheck` item 2]
- **v1's own derived suite MSE is 16.0% low.** F2 divides the recorded score by the
  record network's multiplier and gets `2.594949e-7`. The incumbent's recorded raw MSE
  is `3.089460087e-7`. Ratio `0.83994`. [O: `SUBMISSION_DOSSIER_20260808.md` row 3 and
  the production report agree on `3.0895e-7`] Any leaf that used the derived MSE
  inherited the mix.
- **The ratio is scale-robust; the absolute is not.** Apply the two **measured
  half-ratios** (analytical `0.712046`, residual `2.308659`) to each scale's own split
  and the effective-`C` ratio lands in the same place every time: `0.8471` on the
  suite-mean split [D, script `--suite-scale`], `0.8471` on the record-net split [D],
  against `0.8388 / 0.8447` measured directly on the probe pair [O]. Three independent
  routes to ~0.84. None of them is 0.739.

**Measured paired basis, read verbatim from `full.json` `end_to_end.routes.floor_L4`
against `end_to_end.incumbent` in the same run [O, pending round-4 bill repair
re-run]:**

| net | child flops | child residual | child `C` | parent `C` | `effective_C_ratio` |
|---|---:|---:|---:|---:|---:|
| 0 | `132,729,573,911` | `0.371067 s` | `169.836254B` | `202.478836B` | **`0.8387852`** |
| 1 | `135,136,725,535` | `0.355609 s` | `170.697585B` | `202.070095B` | **`0.8447444`** |

`flops + 1e11 x residual == effective_C` to `1.8e-16` relative on net 0 and `1.5e-15`
on net 1, which re-verifies F1's decomposition against a third artifact. [O,
`--selfcheck` item 1, whose printed `rel=` values are quoted verbatim in v2.10.
CORRECTED 2026-08-19: this line previously claimed `1.8e-16` on both nets, which the
script's own output contradicts by an order of magnitude on net 1.]

### The row v1 does not contain

| candidate | basis | score | vs unfolded `kerdock_v3` `1.6190838e-7` |
|---|---|---:|---:|
| **folded `row_blocked`** | measured paired, net 0 | **`1.7797e-7`** | **`1.0992x`, 9.9% WORSE** |
| folded `row_blocked` | measured paired, net 1 | `1.7923e-7` | `1.1070x`, 10.7% worse |
| folded `row_blocked` | suite-scale projection [D] | `1.7973e-7` | `1.1101x`, 11.0% worse |
| unfolded `kerdock_v3` | recorded, T4 official-100 | `1.6190838e-7` [O] | `1.0000x` |

`2.1218e-7 x 0.8388 = 1.780e-7`. The fold at its measured strength on its measured
host does not beat a candidate the campaign already holds. Neither the manuscript nor
v1 contains this comparison.

---

## v2.3 λ SURVIVES — re-priced (script output)

`python -B designation_repricing.py --lambda-mode survives --floor 0.1`
(identical at `--floor 0.5`; every `C/B` below is above both floors)

| candidate | C (this scale) | C/B | score | vs incumbent | vs unfolded kerdock_v3 |
|---|---:|---:|---:|---:|---:|
| incumbent row_blocked | 189.853B | 0.6980 | 2.1218e-7 | 1.0000x | 1.3105x |
| fold | 159.246B | 0.5855 | 1.7797e-7 | 0.8388x | 1.0992x |
| fold + 129 @ raw-MSE 0.78 | 163.037B | 0.5994 | 1.4212e-7 | 0.6698x | 0.8778x |
| fold + 129 @ raw-MSE 0.86 | 163.037B | 0.5994 | 1.5670e-7 | 0.7385x | 0.9678x |
| fold + 129 @ raw-MSE 0.93 | 163.037B | 0.5994 | 1.6945e-7 | 0.7986x | 1.0466x |

```
break-even raw-MSE ratio at which fold+129 matches unfolded kerdock_v3 (1.6191e-7): r* = 0.88859
  amended pre-registered band [0.78, 0.93]; falsifier > 0.95
  -> the stack beats the candidate we already hold only on the band's lower 72.4% (r in [0.78, 0.8886])
```

`python -B designation_repricing.py --lambda-mode survives --suite-scale`
(`C_ratio = 0.8470936`, the measured half-ratios projected onto the deployed suite's
own analytical/residual split)

| candidate | C (this scale) | C/B | score | vs incumbent | vs unfolded kerdock_v3 |
|---|---:|---:|---:|---:|---:|
| incumbent row_blocked | 189.853B | 0.6980 | 2.1218e-7 | 1.0000x | 1.3105x |
| fold | 160.823B | 0.5913 | 1.7973e-7 | 0.8471x | 1.1101x |
| fold + 129 @ raw-MSE 0.78 | 164.652B | 0.6053 | 1.4353e-7 | 0.6765x | 0.8865x |
| fold + 129 @ raw-MSE 0.86 | 164.652B | 0.6053 | 1.5825e-7 | 0.7458x | 0.9774x |
| fold + 129 @ raw-MSE 0.93 | 164.652B | 0.6053 | 1.7113e-7 | 0.8066x | 1.0570x |

```
break-even raw-MSE ratio at which fold+129 matches unfolded kerdock_v3 (1.6191e-7): r* = 0.87988
  amended pre-registered band [0.78, 0.93]; falsifier > 0.95
  -> the stack beats the candidate we already hold only on the band's lower 66.6% (r in [0.78, 0.8799])
```

On the net-1 basis (`--basis floor_L4_net1`), `r* = 0.88232`. The three bases therefore
put `r*` at `0.8799 / 0.8823 / 0.8886`.

**`r*` is the number the 129 cell is now for.** The cell's amended band is
`[0.78, 0.93]`; `r*` sits at `0.880-0.889` depending on basis. A PASS in the band's
lower two-thirds makes `fold + 129` the best candidate the campaign owns. A PASS in the
upper quarter leaves the unfolded `kerdock_v3` candidate ahead of the whole stack. v1
had no leaf for that outcome because on v1's arithmetic every 129 row won.

---

## v2.4 The 129 rows carry their own point-count factor (C5) and the amended band (C8)

**C5.** The completion bills proportional to point count, and 129 frames over 126 is
exactly `43/42 = 1.0238095238...`. [O: `CODEX_HANDOFF_20260810.md:131`;
`s11_full129_breakeven/S11_VERDICT.md:48`] v1 held `C` fixed across all three 129 rows.
The cell's pre-registered band is explicitly on the **raw** MSE ratio, so the compute
cost is additional to it and not already inside it. [O: `spec.json`
`predicted_signature`] Every 129 row in v2 carries the factor in its `C` column:
`159.246B -> 163.037B` under λ-survives, `123.749B -> 126.696B` under λ-dies. Effect on
the headline row: `fold + 129 @0.78` moves from `1.3882e-7` to **`1.4212e-7`**, a
uniform `+2.38%` on all three.

The factor is applied to the whole of `C` rather than to its analytical half alone.
That is the conservative direction and it is [A] on the split; **M3 is the measurement
that settles it**, and it must be read off the same receipt as M2.

**C8.** The band `0.78-0.86` is superseded. Every occurrence in this policy, meaning
v1 §1a's three 129 rows, §2.1's fallback wording and §2.5's "pre-registered band" line,
is replaced by the amended band **`[0.78, 0.93]`**, filed 2026-08-19 ~02:1x UTC, commit
`0486668` ("band widened honestly"), after the regime audit found three unreconciled
quantifications of Kerdock-versus-iid degree-4 suppression (9.1x, 21x, 42.7x). The
falsifier is unchanged at raw-MSE ratio `> 0.95`. [O: channel; manuscript §11, §13]

**Open, and not fixable from this file:** `experiments/frame_completion_129/spec.json`
still carries `0.78-0.86` and contains no amendment text, while the channel entry that
sealed it states the seal-time spec carries the amendment verbatim. The cell is
unpredeclared and its authorization unspent, so the repair is free now and becomes a
protocol violation once predeclared. **Owner action, strictly before predeclare.**

---

## v2.5 λ CAPPED — admissibility re-derived from the measured residual (B8 / C4)

v1 ran two incompatible residual bases at once. §1a's `C_post(m)` carries `18.815e9`
per unit `m`, which is a residual base of `0.18815 s/net`; §1c tabulates `0.1606m`.
The two are **17.2% apart** (`18.815/16.0585 = 1.17165`), and the reason is now
identified: `18.815e9` is the **record max-`C` network's own residual term**
(`222.405357 - 203.590357`), not the deployed mean. Neither base is a measurement of
the fold.

**One residual base, stated: the deployed suite mean `0.160585 s/net` [O]. The fold's
residual is measured directly rather than derived from a coefficient, and `m` is an
output, not an input.**

Measured: fold residual `0.371067 s/net` (net 0) and `0.355609 s/net` (net 1), against
same-run parents `0.160728` and `0.158453`, giving `m = 2.3087 / 2.2443` [O, pending
round-4 bill repair re-run]. Cross-check: the deployed mean scaled by the measured
ratio, `0.160585 x 2.3086588 = 0.370736`, agrees with the direct measurement to
**0.089%**.

`python -B designation_repricing.py --lambda-mode capped`

```
ADMISSIBILITY on the measured residual base (floor_L4_net0): fold 0.370736 s/net against parent 0.160585 s/net, m = 2.3087 [O]
```

| tau (s/net) | fold as built (measured) | verdict | implied m |
|---|---:|---|---:|
| 0.1606 | 0.370736 | BREACH | 2.3087 |
| 0.2000 | 0.370736 | BREACH | 2.3087 |
| 0.2500 | 0.370736 | BREACH | 2.3087 |
| 0.3212 | 0.370736 | BREACH | 2.3087 |
| 0.3556 | 0.370736 | BREACH | 2.3087 |
| 0.3711 | 0.370736 | fits | 2.3087 |
| 0.5000 | 0.370736 | fits | 2.3087 |

**Leaf 2.4 flips.** v1 recorded `tau = 0.3212` as "fits" and drew the
incumbent-designation boundary there. By measurement the fold as built breaches
`0.3212`, and the boundary moves to `tau < 0.3711`. The two branches of that leaf
designate different slot-1 candidates, so this is a decision change, not a rounding
change.

Two qualifiers carried rather than buried. First, `m` inherits an unbounded environment
component: `check_end_to_end` measures the incumbent once, in the first ~40 s of a
~9-minute single-process sweep, and never again, while the child's exposure window per
predict is 5-10x longer; the unchanged incumbent has measured `0.1503 / 0.1606 / 0.1717`
across runs, a 14% spread. The A-B-A repair is queued for M1 and is a two-line change.
Second, admissibility is a measured fact about the fold **as built**; it is not a claim
about a re-engineered route that has never been measured.

---

## v2.6 λ DIES — both sides collapsed, and it is the HOSTILE branch (B4 / rank-4)

v1 collapsed **our** `C` to its analytical part and left the incumbent's at
`222.405357e9`. Under λ-dies the incumbent's residual term is deleted too. Three
figures for the same quantity, in repair order:

| pricing | fold-vs-incumbent `C` ratio | relative to v1 |
|---|---:|---:|
| v1: `126.7 / 222.405357` (incumbent uncollapsed) | `0.56968` | `1.0000x` |
| collapse the incumbent only: `126.7 / 203.590357` | `0.62233` | `1.0924x` |
| **v2: measured analytical ratio, both sides same scale** | **`0.71205`** | **`1.2499x`** |

v1's λ-dies branch was flattered by **9.2%** from the one-sided collapse and by
**25.0%** once the local-scale `126.7e9` absolute is replaced by the measured
analytical ratio against the same-run parent.

`python -B designation_repricing.py --lambda-mode dies --floor 0.1`

| candidate | C (this scale) | C/B | score | vs incumbent | vs unfolded kerdock_v3 |
|---|---:|---:|---:|---:|---:|
| incumbent row_blocked | 173.794B | 0.6389 | 2.1218e-7 | 1.0000x | 1.3105x |
| fold | 123.749B | 0.4550 | 1.5108e-7 | 0.7120x | 0.9331x |
| fold + 129 @ raw-MSE 0.78 | 126.696B | 0.4658 | 1.2065e-7 | 0.5686x | 0.7452x |
| fold + 129 @ raw-MSE 0.86 | 126.696B | 0.4658 | 1.3302e-7 | 0.6269x | 0.8216x |
| fold + 129 @ raw-MSE 0.93 | 126.696B | 0.4658 | 1.4385e-7 | 0.6780x | 0.8885x |

```
break-even raw-MSE ratio at which fold+129 matches unfolded kerdock_v3 (1.6191e-7): r* = 1.04676
  amended pre-registered band [0.78, 0.93]; falsifier > 0.95
  -> r* is above the band's upper edge: the stack wins across the whole band
```

`python -B designation_repricing.py --lambda-mode dies --floor 0.5`

| candidate | C (this scale) | C/B | score | vs incumbent | vs unfolded kerdock_v3 |
|---|---:|---:|---:|---:|---:|
| incumbent row_blocked | 173.794B | 0.6389 | 2.1218e-7 | 1.0000x | 1.3105x |
| fold | 123.749B | 0.4550 (floored) | 1.6604e-7 | 0.7825x | 1.0255x |
| fold + 129 @ raw-MSE 0.78 | 126.696B | 0.4658 (floored) | 1.2951e-7 | 0.6104x | 0.7999x |
| fold + 129 @ raw-MSE 0.86 | 126.696B | 0.4658 (floored) | 1.4279e-7 | 0.6730x | 0.8819x |
| fold + 129 @ raw-MSE 0.93 | 126.696B | 0.4658 (floored) | 1.5441e-7 | 0.7278x | 0.9537x |

```
break-even raw-MSE ratio at which fold+129 matches unfolded kerdock_v3 (1.6191e-7): r* = 0.97514
  amended pre-registered band [0.78, 0.93]; falsifier > 0.95
  -> r* is above the band's upper edge: the stack wins across the whole band
```

Under λ-dies the `fold + 129` stack beats the unfolded `kerdock_v3` candidate across
the whole amended band at either floor, which is the one branch where v1's designation
ordering survives the re-price intact. The reason is mechanical rather than favourable:
deleting the residual term removes the fold's only measured **cost**, and the fold's
analytical win is the half that transfers.

v1 reported `1.2088e-7` and `1.2975e-7` for the fold on these two leaves. The repaired
figures are `1.5108e-7` and `1.6604e-7`. The floor still binds at `0.5`, and the 129
lever still pays its full ratio under the floor because the floor caps the multiplier
rather than the MSE. One correction to v1's confidence about it: the score law applies
`max(FLOOR, C_i/B)` **per network**, so under λ-dies at floor 0.5 some networks bind and
others do not. The aggregate test above is an approximation and only M1's per-network
receipt settles it. [D]

### The rival-response caveat, which v1 has no column for

**λ-dies is the hostile branch, not the friendly one.** The fold is a pure compute
lever: `rel_dev_vs_incumbent = 1.0189e-07` and `output_ratio_vs_incumbent =
1.0000000026` on `floor_L4`, i.e. MSE parity to seven digits [O, pending round-4 bill
repair re-run]. Its entire value is the multiplier. A rules change that deletes or
floors the compute term therefore **deletes our lever and leaves the MSE-lever rivals
untouched**, and Puffi, at the declared front, has already published a MUB-129
ablation, which is a design lever of exactly the kind λ-dies preserves. [R]

Two consequences for how this branch may be read:

1. **No cross-regime comparison is admissible.** Every λ-dies score in v1 was computed
   for us alone and then compared against a rival front declared under the current
   rules. If λ changes, it changes for everyone. v1 §2.2's sentence "at 9.4e-8 slot 1
   would sit at or ahead of the declared front" is **withdrawn**; v2's λ-dies tables
   carry ratios against our own incumbent and nothing else.
2. **The pre-commitment in `CONTINUATION_PLAN` §0c to λ-dies as the primary branch is a
   bet on a branch adverse to our candidate class.** It is retained as a plan, not as a
   preference.

---

## v2.7 The host fork is now the decision, not a tiebreak

The fold's win is carrier-free at the operator (metered `flops_ratio 0.6524` at
(4096,256,256) and `0.7145` at (256,256,256), FlopScope's own measurement [O]), while
its residual **cost** scales with the host's residual base. `kerdock_v3` carries a
residual base of `0.080 s/net` against `row_blocked`'s `0.160585`, a residual share of
`4.48%` of `C` against `8.46%`, so the same measured half-ratios buy more there:

| host | suite-scale `C` ratio from the same measured halves | folded score | admissible at `tau` |
|---|---:|---:|---|
| `row_blocked` | `0.8471` [D] | `1.7973e-7` | `tau >= 0.3711` only |
| `kerdock_v3` | **`0.7836`** [D, portability [A]] | **`1.2687e-7`** | `tau >= 0.2000` |

`python -B designation_repricing.py --lambda-mode survives --host kerdock_v3 --suite-scale`

| candidate | C (this scale) | C/B | score | vs incumbent | vs unfolded kerdock_v3 |
|---|---:|---:|---:|---:|---:|
| incumbent kerdock_v3 | 178.463B | 0.6561 | 1.6191e-7 | 1.0000x | 1.0000x |
| fold | 139.847B | 0.5141 | 1.2687e-7 | 0.7836x | 0.7836x |
| fold + 129 @ raw-MSE 0.78 | 143.176B | 0.5264 | 1.0132e-7 | 0.6258x | 0.6258x |
| fold + 129 @ raw-MSE 0.86 | 143.176B | 0.5264 | 1.1171e-7 | 0.6900x | 0.6900x |
| fold + 129 @ raw-MSE 0.93 | 143.176B | 0.5264 | 1.2080e-7 | 0.7461x | 0.7461x |

```
break-even raw-MSE ratio at which fold+129 matches unfolded kerdock_v3 (1.6191e-7): r* = 1.24646
  amended pre-registered band [0.78, 0.93]; falsifier > 0.95
  -> r* is above the band's upper edge: the stack wins across the whole band
```

> **CORRECTED 2026-08-19 (hostile verify).** This block previously read `r* = 1.16447`,
> which is the output of `--host kerdock_v3` *without* `--suite-scale`; the command
> quoted above emits `1.24646`. The table above it was always the `--suite-scale` run.
> The line is struck either way (see below), so no designation moved; the authoring
> verifier missed it because its skip list excluded every `break-even` line. [O]

**Read only the `fold` row of that table.** The script applies the 129 band to whatever
host it is given; on this host the three 129 rows are **inapplicable and are struck**,
because the completion's MSE lane is measured dead on Kerdock (`~0.176%`, s11 plus the
dual-witness certificate). That is the whole reason the cell was built for the Haar
carrier, where `A_4` is `128/3` larger. The `r* = 1.24646` line is struck with them.

On the surviving row the folded `kerdock_v3` candidate at `1.2687e-7` beats **every**
`row_blocked` candidate in the λ-survives branch, including `fold + 129` at the band's
optimistic edge (`1.4212e-7`).

**This is [A] on one link and must not be designated until that link is [O]:** the
`0.712046` analytical ratio is assumed to port to `kerdock_v3`'s deployed route. The
settling check is a source read of minutes, of exactly the kind Phase 1 did for
`row_blocked` (`row_blocked_winograd.py:88` gave `owned_batched` at `471,711,744`/call).
Until it exists, the kerdock rows above are a projection.

The second-order point is that this pair is genuinely decorrelated in W1's sense (a
different carrier, a different MSE lane, a different admissibility profile), which is
what v1's slot 2 ("fold alone") is not: it shares carrier, compute mechanism and suite
draw with v1's slot 1, the `rho = 1` shape W1 prices at zero.

---

## v2.8 What the re-price does to §2's leaves

Only two leaf answers move. The slot doctrine, W1-W3 and §2.5's standing rules are
unchanged.

| leaf | v1 answer | v2 answer | why it moved |
|---|---|---|---|
| **2.1** λ survives, 2 slots | Slot 1 `fold + 129`; slot 2 `fold alone` | Slot 1 `fold + 129` **conditional on the cell returning `r <= 0.8886`**; slot 2 the folded `kerdock_v3` host once its route read lands, else the unfolded `kerdock_v3` | `fold alone` at `1.780e-7` loses to a candidate already held, so it is not a slot-2 candidate on score, and it is not decorrelated from slot 1 either |
| **2.1** λ survives, 1 slot | `fold + 129`, else `fold alone` | `fold + 129` if the cell clears **and** `r <= 0.8886`; otherwise **unfolded `kerdock_v3`**, not `fold alone` | same arithmetic |
| **2.4** λ capped | incumbent at `tau < 0.3212` | incumbent at `tau < 0.3711` on the `row_blocked` host; for `0.2000 <= tau < 0.3711` the folded `kerdock_v3` is the admissible candidate if its route read lands | the fold as built breaches `0.3212` by measurement |
| 2.2 / 2.3 λ dies | unchanged ordering | unchanged ordering, re-priced numbers, cross-regime comparisons deleted | the 129 lever keeps paying under the floor; only the magnitudes moved |

**Unchanged and re-affirmed:** nothing is designated on an unrun cell; never two
correlated slots; `R` is chosen last in September from the position actually held;
FlopScope-mandatory adds a metered port to every candidate. v1 §2.5's claim that
FlopScope-mandatory "changes the schedule, not the ranking" is **withdrawn**: the fold's
win is a metered-FLOP win whose `m` is set by batched leaf dispatch in native numpy, and
a mandatory port re-serializes exactly that dispatch, so under that rule `m` is
re-measured from scratch. It is an axis this tree does not have, and the Ψ response
applies to it.

---

## v2.9 Pre-committed M1 interpretation bands (F9) — filed before the run, JSON only

Filed before M1 lands so that the reading of the measurement cannot be re-narrated
after the fact. Verbatim from the pre-commitment; no prose paraphrase is authoritative.

```json
{
  "predeclaration": "M1 interpretation bands and crowning rule",
  "filed": "2026-08-19, before the one Public100 measurement",
  "reported_as": "paired child/parent ratios on the same Public100 run",
  "bands": {
    "FULL_TRANSFER": {
      "condition": "FLOP ratio <= 0.65 AND C ratio <= 0.78",
      "meaning": "the suite ladder's savings carried to the Haar host; the analytical anchor holds",
      "disposition": "crown at the headline"
    },
    "PARTIAL_NON_TRANSFER": {
      "condition": "FLOP ratio 0.69-0.75 with C ratio 0.80-0.88",
      "meaning": "this is what every committed measurement predicts",
      "disposition": "crown WITH mechanical attribution: decompose the realized analytical bill against the fold's own closed form (sum realized_candidate_bill over the predict's dispatches; deterministic, host-independent, no extra run) and attribute the residue to the Kerdock-lineage suite tiers BY NAME. If realized non-transfer exceeds the declared 1.55%, the manuscript is CORRECTED, not re-described."
    },
    "MARGINAL": {
      "condition": "C ratio 0.88-0.95",
      "meaning": "still a win under Gate B's 0.98 clause",
      "disposition": "crown as verified win, headline WITHDRAWN"
    },
    "FAILURE": {
      "condition": "C ratio > 0.98 OR per-net |MSE ratio - 1| > 5e-4 OR aggregate |MSE ratio - 1| > 1e-4",
      "disposition": "no crown; a parity breach voids the candidate"
    }
  },
  "crowning_rule": {
    "pairing": "crown only on the paired end-to-end C ratio from ONE run",
    "incumbent_measured_twice": "the incumbent is measured TWICE in that same run, A-B-A, before and after the child routes; report m against both, and the spread between the two A blocks is the in-run measurement of the environment component",
    "never_mix_scales": "never combine the local synthetic analytical incumbent with the record analytical incumbent inside one ratio; the superseded 126.7 + 18.815m curve did exactly that and it is the sole source of the -26% headline",
    "companion_witness": "record process_time alongside perf_counter per rep and store wall - cpu, to separate descheduling from clock throttling"
  },
  "standing_note": "the committed paired measurement (effective_C_ratio 0.8388/0.8447) already sits inside PARTIAL_NON_TRANSFER, so the predicted disposition is crown-with-attribution, not crown-at-headline"
}
```

The last line is the one that binds hardest: **on the measurement already in hand, the
pre-committed reading of M1 is PARTIAL, and PARTIAL means the headline is not crowned.**

---

## v2.10 Reproduction, and what v2 does not settle

**Reproduction.** Every v2 table is the output of `core/designation_repricing.py`
(exact `Fraction` arithmetic, stdlib only, run with `-B`). Parameters, per C13:
`(lambda_mode, floor, B, residual_constant, suite_size, host, C_ratio)`, plus `--basis`
to select the measured net and `--suite-scale` to project the measured half-ratios onto
the deployed suite's split. The hour the Phase-2 rules post, the response is a script
run rather than a re-derivation: a change to the floor, to `B`, to the residual
conversion constant, to the private suite size, or to the host is a flag.

`python -B designation_repricing.py --selfcheck` runs four discriminating checks:

```
[ok] 1/floor_L4_net0: flops + 1e11*residual == effective_C, rel=1.77e-16
[ok] 1/floor_L4_net1: flops + 1e11*residual == effective_C, rel=1.52e-15
[ok] 2: v1 curve reproduces its 1.5677e-7 headline -> 1.5677e-7 at C/B ratio 0.738876
[ok] 3: product form 2.1564e-7 vs recorded 2.1218e-7, bias +1.633%
[ok] 4: aggregate score ratio 0.763084382 vs T4 printed mean-ratio column 0.763084382 (IDENTITY, transcription check only)
SELFCHECK PASS
```

Check 2 is the discriminating one: if v2's model of v1 were wrong, the replaced
headline would not reproduce. **Check 4 is not discriminating** — see the withdrawal in
v2.1; it was relabelled in the script on 2026-08-19 so the output states its own status.

**What v2 does not settle.**

- **The round-4 re-run.** Every `full.json`-derived number carries the standing caveat.
  The repaired bill changes route selection, so `0.8388`, `0.8447`, both `m` values and
  the admissibility table can all move. No designation may cite them until the sweep is
  re-run on the repaired bill.
- **The local-to-hosted map.** The campaign owns two calibrations that disagree by a
  factor of 1.87 in opposite directions (`gm_c1_bound` at `R = 1.65 [1.04, 2.42]`
  against the one paired graded anchor at `R = 0.884`, with Codex's median test
  independently reaching parity). Every "we would sit at X against the front" sentence
  in the record silently assumes 1:1. v2 states no position against any rival for that
  reason, and the divergence map is the settling check.
- **M3.** Whether the `43/42` point-count factor applies to the whole of `C` or to its
  analytical half alone.
- **The kerdock route read.** v2.7's host rows are [A] on portability until the source
  read lands.
- **The Phase-2 rules text.** No Phase-2 rules or criteria document exists anywhere in
  the corpus; the only rules texts are eleven days old and Phase 1. The λ axis, the
  floor axis, FlopScope-mandatory, the seed protocol, the submission limit and the
  private suite size are all decided by that text and by nothing computable here.
- **The aggregate-ratio approximation itself.** v2's ratios reproduce a true paired
  ratio to nine digits on the one pair where both are recorded (`--selfcheck` 4). That
  is one pair, not a theorem. Any candidate whose per-network `C` distribution differs
  in shape from the incumbent's, the floored λ-dies leaves in particular, needs the
  per-network receipt rather than the aggregate.
