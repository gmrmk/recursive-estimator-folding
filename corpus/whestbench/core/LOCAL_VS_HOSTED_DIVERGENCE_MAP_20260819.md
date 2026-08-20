# Local↔hosted divergence map — the named contract delta (2026-08-19)

**Scope.** Everything the campaign knows about how a LOCAL adjusted score converts
to a HOSTED adjusted score, consolidated into one document, every number
re-derived this session from the source artifacts rather than copied from prose.
This supersedes the scattered readings in `experiments/c1_local_mc_calibration/C1_REPORT.md`,
`experiments/gm_c1_bound/VERDICT.md`, `CODEX_HANDOFF_20260810.md` §4.1/§4.2, and
`SUBMISSION_RESULT_20260808.md`. Where those disagree, this file states which one
is right and why.

**Evidence tags.** `[O]` observed — computed or read this session from the named
file. `[D]` derived — follows from `[O]` numbers by arithmetic shown here.
`[R]` reported — a committed corpus document says so and I did not re-derive it.
`[A]` assumed — a default chosen here, labelled with its settling check.
`[R*]` reported **and pending round-4 bill repair re-run** — see §0b.

**Compute discipline.** Zero harness runs. No FlopScope. No production
measurement. `experiments/fold_floor_splice/` was read only. All arithmetic is
exact-rational or `decimal` at 28–40 digits under `python -B`; the two intervals
that need a sampling distribution use a deterministic jackknife and the delta
method, never an RNG.

---

## 0. Verdict

**R = 1.65 is retired in both directions.** It is not a suite-difficulty
constant; it is the skew of a 22-net panel, and its own successor measurement
killed it. Nothing in the corpus may divide a local score by 1.65 to project a
hosted score, and nothing may multiply by 1.65 either.

**The honest map is R ≈ 1 with a mildly adverse anchor.** Three independent
routes put the local→hosted transfer at parity or slightly against us: the
MC-lane median matches the grader's printed MC reference to **+0.055 %**; the one
paired graded observation puts the champion lane at **R = 0.884** (hosted ~13 %
worse than local); and the campaign's own same-day post-mortem on the graded
submission recorded the same thing in plain words before either statistic was
computed.

**The band that every position-vs-front statement must carry until a second
paired anchor exists: R ∈ [0.707, 1.105] at 95 %, point 0.884.** That band is
one-anchor-wide and it is the dominant uncertainty in every "we would sit at or
ahead of the front" sentence now in the designation file.

**The consequence that changes a decision.** `DESIGNATION_POLICY_20260819.md` §2.2
compares local candidate scores directly against hosted leaderboard numbers,
which is the R = 1 assumption used silently. That default is defensible — it is
the best point estimate available — but at the anchor point (R = 0.884) the
λ-dies slot-1 candidate lands *behind* Puffi rather than level with it, and W3's
R-posture table understates its own variance budget by omitting the transfer
term entirely (§10).

### 0b. The `full.json` caveat, stated once and applied throughout

Every fold-lane local score in this file (`1.5677e-7`, `1.2856e-7`, `1.2088e-7`,
`1.2975e-7`, `9.4283e-8`, and the C values `126.7B` / `164.3B` behind them) is a
**cost-model output**, not a measured 100-net score. Those models sit in the same
lineage as `experiments/fold_floor_splice/full.json`, whose bill was wrong **in
both directions**. All such numbers are tagged `[R*]` and carry the standing
caveat: **pending round-4 bill repair re-run.** They are included because the
divergence map is what converts them, not because their local values are settled.
`D-A3a` and `D-A3b` remain blocking on that tree [R,
`FOLD_FLOOR_SPLICE_PRODUCTION_GATE.md` addendum 2026-08-19T06:12:13Z].

The two lanes that are **not** subject to that caveat are the kerdock_v3 anchor
(a completed 100-net local run, `matched_units: 100`, 0 failures) and the C1 MC
panel (a completed 25-net local run). Those carry their own error bars and
nothing else.

---

## 1. Why there is no single R

R has been used as if it were one scalar. It is not. It is **estimator-lane
specific**, and the corpus contains measurements from two different lanes that do
not agree and are not required to:

| lane | what was compared | value |
|---|---|---|
| **MC lane** | our plain budget-matched antithetic MC on local nets vs the grader's printed MC reference on the hosted 50 | mean-ratio **1.6517**, median-ratio **1.0005** |
| **Champion lane** | Kerdock v3 on local 0..99 vs the *same frozen artifact* graded on the hosted 50 | **0.884** |

A suite-difficulty ratio measured on plain Monte Carlo transfers to a structured
estimator only if the variance-reduction factor is the same on both suites. It is
not: the design's exact degree-≤2 integration removes a variance term whose size
is itself suite-dependent. `SUBMISSION_RESULT_20260808.md` named this mechanism on
the day of grading [R] and it is the reason the MC-lane number was never
transferable.

**Operational rule.** Only the champion lane's R may be used to project a
champion-lineage candidate. The MC lane's median parity is corroborating evidence
about suite difficulty in general; its mean is a corpse (§2).

---

## 2. Source 1 — `gm_c1_bound`: R = 1.6517, CI [1.0362, 2.4230], and why the CI is
the least of its problems

### 2.1 Recomputed from the raw artifact, not from the verdict

I re-read `experiments/c1_local_mc_calibration/c1_local_mc25.json` (UTF-8 BOM;
`utf-8-sig`) and recomputed the panel with exact `Fraction` arithmetic over the
25 `per_mlp` rows [O]:

| quantity | recomputed this session `[O]` | committed | agreement |
|---|---|---|---|
| completed nets | 22 (excluded: `dustin-merritt`, `riley-king`, `daniel-miller`, all `combined_budget_exhausted`) | 22 of 25 | exact |
| mean adjusted | `1.0686276000992886e-6` | `1.0686276000992886e-6` | **difference 0.0** |
| median adjusted | `6.473545958232132e-7` | `6.473546e-7` | rel −6.5e-9 |
| sd | `1.1060968297993356e-6` | `1.1061e-6` | 3e-6 rel |
| relative variance | `1.0713552980437124` | `1.0714` | 4e-5 rel |
| max/min | `22.41507823565832` | `22.415x` | exact to printed |
| 25-row mean (incl. failures) | `0.09778592927244556` | `0.09778592927244555` | 1 ulp |
| **R = mean / 6.470e-7** | **`1.6516655333837535`** | `1.6516655333837535` | **exact** |
| SE = sd/√n/H | `0.36448320938468015` | jackknife `0.364483209384680` | **exact** |

The C1 run is arithmetically clean. Every published figure reproduces from the
archive, and the analytic SE reproduces the jackknife SE to the printed digits by
a route that never resamples. That was never the defect.

### 2.2 The interval, and DEVIATION 2

95 % percentile bootstrap (B = 200 000, two RNG streams, endpoint agreement
0.0016 / 0.0078): **[1.0362, 2.4230]**, width 1.3868 [R, `gm_c1_bound/VERDICT.md`].
The band inside which C1's downstream parity claim keeps its truth value is
[1.3706, 2.1415], width 0.7709; the ratio is **1.79887x** [D, recomputed]. Only
**68.26 %** of the bootstrap mass leaves the parity claim standing. `P(R > 1.25)`
= 0.8763 / 0.8751 across the two streams [R], so even the coarse direction is
0.88, not the >0.95 the C1 report's flat language implies.

**DEVIATION 2, carried forward verbatim in force.** *Every interval on R in
`gm_c1_bound` is local-side only. The hosted reference `6.470e-7` is a single
printed number with no error bar; its sampling error is not modelled. So
`[1.0362, 2.4230]` is a **lower bound on width**, not a confidence interval on the
transfer.* [R]

This matters more than it looks. §3 measures the hosted side's dispersion directly
for the first time, and the hosted 50-net mean carries an **8.89 %** standard error
[O]. Folding a comparable term into C1's interval widens it further in both
directions. No statement anywhere in the corpus may treat `6.470e-7` as exact.

### 2.3 The exclusion channel

3 of 25 nets tripped `combined_budget_exhausted` at 97.4 % of budget and were
dropped. `gm_c1_bound` bounds the channel at roughly **[1.574, 2.356]**:
median-imputation gives R = **1.5735**, *below* the point estimate, and
max-imputation gives 2.3558 [R]. Spearman(effective_compute, adjusted) = **+0.0695**,
permutation p = 0.761 / 0.757; Pearson = −0.0830; Spearman(flops_used, adjusted)
= −0.2919 [R]. **There is no data-supported direction to the exclusion bias.** The
mined phrase "the truth sits above 1.652 more often than below" is an assumption
and was never a measurement.

### 2.4 The single-net fragility

Dropping the largest net moves the **point** from 1.6517 to **1.3722**; dropping
two moves it to **1.2276**, inside C1's own predeclared "suites comparable"
region [0.8, 1.25] that the report ruled out [R]. One net separates the published
constant from the opposite qualitative verdict.

---

## 3. Source 2 — the one paired graded anchor, #326094

This is the only observation in the corpus where **the same frozen estimator
artifact** has both a local score and a hosted grade. It is the highest-quality
evidence about the transfer that exists, and it is n = 1 at the artifact level.

### 3.1 The two sides

**Local.** Ledger record 183, `t4_kerdock_v3_descriptive_rescore`, read from
`headroom/fold_ledger.json` [O]: `"COMPLETED, 0/100 failures. Adjusted
1.6190837992e-7 (raw 2.4938875569e-7, mean mult 0.6561, mean C 178.463e9, MAX C
209.575e9 = 23% under B)"`, `matched_units: 100`. I recomputed the mean of the 100
`per_mlp` adjusted scores in
`experiments/t4_kerdock_descriptive_rescore/kerdock_v3_official100.json`:
`1.6190837992231575e-7`, matching the ledger to **1.4e-11 relative** [O]. Zero
failures of any kind confirmed field-by-field.

**Hosted.** Submission #326094, graded 2026-08-08, 50/50, zero failures: adjusted
**1.832e-7**, final-layer MSE **2.818e-7** [R, `SUBMISSION_RESULT_20260808.md`,
`CODEX_HANDOFF_20260810.md` §2.1]. I recomputed the mean of the 50 per-net rows in
`experiments/a_series_granular_adversarial/a1_hosted_ledger.json`:
**`1.831340e-7`**, which reproduces the committed `1.832e-7` to **−3.6e-4
relative** [O]. The residual gap is the ledger's 3-significant-figure rounding;
perturbing every row by ±½ ulp moves the mean only to `1.82742e-7 / 1.83526e-7`
and R to `0.8860 / 0.8822` [O]. Rounding is not load-bearing.

### 3.2 R at the anchor

| statistic | value | tag |
|---|---|---|
| **R = local mean / hosted mean** (recomputed both sides) | **0.8840978732639254** | `[O]` |
| R from the committed printed figures `1.6190837992e-7 / 1.832e-7` | `0.8837793663755459` | `[D]` |
| R from geometric means (`1.3342536e-7 / 1.5570e-7`) | `0.8569388628649331` | `[O]` |
| R from medians (`1.270457e-7 / 1.620e-7`) | `0.7842324994676293` | `[O]` |

Every robust variant of the statistic is **at or below** the mean ratio. The right
tail that manufactured 1.65 in the MC lane does not exist here; if anything the
champion lane's robust statistics are slightly more adverse than its mean.

### 3.3 The decomposition — the gap is suite difficulty, not accounting

| component | local | hosted | ratio hosted/local |
|---|---|---|---|
| raw final-layer MSE | `2.4938875569e-7` | `2.818e-7` | **1.129963 (+13.00 %)** `[D]` |
| score-weighted multiplier (`adjusted / raw`) | `0.649221` | `0.650106` | **1.001364 (+0.14 %)** `[D]` |
| adjusted score | `1.6190837992e-7` | `1.832e-7` | **1.131496 (+13.15 %)** `[D]` |

Exact identity check: `(local_raw / hosted_raw) × (mult_local / mult_hosted) =
0.8837793663755459`, reproducing R to every digit [O]. The hosted multiplier
independently reproduces the committed `C/B = 0.6501064584811923` and
`C = 0.6501064584811923 × B = 176.828956706884e9` against the pinned-basis
`178.5e9` and the T4 mean `178.462975e9` [D, agreement 1.0 %].

**Read this table before quoting the anchor.** The two multipliers agree to
0.14 %. Whatever the cost lane is doing, it is doing the same thing on both
suites. The entire 13 % adjusted gap is raw MSE. The transfer risk is a
suite-difficulty risk, not a billing or accounting risk.

*Note on `0.656` vs `0.650`.* The corpus quotes the anchor's multiplier pair as
`0.656 → 0.650`, a 0.9 % gap. `0.6561138779836238` is T4's **mean of the per-net
multipliers** [R]; the multiplier that actually converts the score is the
**score-weighted** one, `adjusted / raw = 0.649221` [O], because the adjusted
score is `mean(MSE_i × mult_i)`, not `mean(MSE) × mean(mult)`. On the correct
convention the two suites' multipliers agree to 0.14 %, not 0.9 %. Either
convention supports the same conclusion; the score-weighted one supports it four
times harder.

### 3.4 Dispersion, measured on both sides for the first time

Neither side's per-net spread had been computed against the other. Both are
recomputed here from the per-net artifacts [O]:

| | hosted 50 (#326094) | local 100 (T4) |
|---|---|---|
| n | 50 | 100 |
| mean | `1.831340e-7` | `1.6190838e-7` |
| median | `1.620e-7` | `1.270457e-7` |
| sd | `1.151222e-7` | `1.125306e-7` |
| **per-net CV** | **0.628623** | **0.695026** |
| **SE of the mean** | **8.890 %** | **6.950 %** |
| Q1 / Q3 | `1.0525e-7` / `2.2575e-7` | `8.8543e-8` / `2.0795e-7` |
| min / max | `5.42e-8` / `5.96e-7` | `4.3575e-8` / `6.2453e-7` |
| max/min | `10.996x` | `14.332x` |

Cross-checks that hold: the hosted IQR reproduces the committed `[1.05e-7, 2.26e-7]`
and the committed min/max, and `max/min = 10.996` reproduces the handoff's
`11.00x` [O vs R]. The hosted suite is **less** dispersed than the local one
(CV 0.629 vs 0.695), which is the opposite of the "our suite is harder" story and
consistent with the transfer being adverse rather than favourable.

---

## 4. Source 3 — the median test, parity by an independent route

`CODEX_HANDOFF_20260810.md` §4.1 (ledger 260, `gen8_c1_ratio_artifact_and_anchor_se`,
status **killed**): the local MC panel's **median is `6.473546e-7`** against the
grader's printed **`6.470e-7`** [R]. Recomputed exactly this session:
`6.473545958232132e-7`, ratio **`1.0005480615505613`**, i.e. **+0.0548 %** [O].

The structural point is the one that closes the case. `mean/median = 1.65076081`
and `mean/printed = 1.65166553` agree to **0.0548 %** [O] — the same figure, and
not by coincidence: they agree *because* the median equals the printed reference.
The "difficulty ratio" was numerically identical to a pure skew statistic of a
single sample. That is precisely why it read as a measurement of something
external when it measured nothing but the panel's own right tail. The top five
values are `1.776e-6, 1.968e-6, 2.163e-6, 2.759e-6, 4.865e-6`; the max is 7.5x the
median [R].

**C1's own predeclaration selects the surviving case.** `C1_PREDECLARATION.md`
predeclared three readings: (A) `R ∈ [0.8, 1.25]` suites comparable, local scores
transfer 1:1; (B) `R < 0.8`; (C) `R > 1.25` local harder. C1 reported case (C).
Three independent routes land in **case (A)**: the median ratio `1.0005`, the
paired anchor `0.884`, and C1's own drop-top-two point estimate `1.2276`. C1's
predeclared case (A) is the one its data supports.

---

## 5. Source 4 — the observed refutation, recorded before any of the statistics

`SUBMISSION_RESULT_20260808.md`, written the day #326094 graded [R]:

> C1 predicted ~9.8e-8 hosted (local 1.62e-7 / suite-ratio 1.65). It graded at
> 1.83e-7 — 1.87x worse than projected, essentially at the local value, not the
> rescaled one.

Arithmetic check: R = 1.6517 predicts hosted `9.802734067e-8`; observed
`1.832e-7`; ratio **1.8689** [D], reproducing the recorded 1.87x. And the observed
hosted value sits at `1.1315x` the local value [D], reproducing "essentially at
the local value".

The document also named the mechanism correctly on the day: *"the 1.65x
suite-ratio was measured MC-vs-MC … It does NOT transfer to a structured
estimator"*, and explicitly marked `C1_REPORT`'s rescaling table **WRONG for
structured estimators** [R]. That correction was made ten days before the median
test and eleven before `gm_c1_bound`, and it was never propagated into the
downstream documents that kept quoting 1.65.

**This is a fourth, chronologically first, independent signal, and it is an
out-of-sample prediction that failed.** It carries more evidential weight than any
of the three retrospective statistics, because the projection was made before the
grade was known.

---

## 6. The noise arithmetic

### 6.1 The model route

S1b's per-net relative variance is `vD + (1 + vD)·vF` [R]. At the s17 bracket
`vD ∈ {0.08135950765, 0.1220}` with `vF = 0.36419956287` [R]:

| vD | per-net variance | per-net CV | SE of a 50-net mean | SE of a 100-net mean |
|---|---|---|---|---|
| 0.08135950765 | `0.475190168` | **`0.689340`** | **`9.7487 %`** | `6.8934 %` |
| 0.1220 | `0.530631910` | `0.728445` | **`10.3018 %`** | `7.2844 %` |
| 0.134 (§3.4 moment estimate) | `0.547002304` | `0.739596` | `10.4595 %` | `7.3960 %` |

All `[D]`, recomputed. The committed 1e6-suite SDs cross-check the bracket:
`1.7856461794e-8 / 1.83e-7 = 9.7576 %` and `1.8871029898e-8 / 1.83e-7 = 10.3120 %`
[D]. The ledger-260 figure of **9.83 %** sits inside `[9.75 %, 10.30 %]`, so the
anchor-SE correction is internally consistent with S1b's own model.

The lognormal fit of the hosted grade distribution also holds up:
`sigma_log = sqrt(ln(1 + 0.68934²)) = 0.6235278`, median
`1.832e-7 · exp(−sigma_log²/2) = 1.508348e-7`, predicted IQR
**`[9.905e-8, 2.2969e-7]`** against the measured `[1.0525e-7, 2.2575e-7]` — Q3
within **1.6 %**, Q1 within **5.9 %** [D vs O].

### 6.2 The measured route, which is better

The model is no longer needed for the anchor. Both suites' per-net dispersions are
now measured directly (§3.4): hosted CV **0.6286**, local CV **0.6950** [O]. The
model's 0.689 sits between them and slightly overstates the hosted side. The
measured SE of the hosted 50-net mean is **8.89 %**, not 9.75–10.30 %.

### 6.3 How far the anchor sits from each hypothesis

Two conventions, both reported, because the corpus's "~1.3 SE / ~5 SE" figures
come from the first and the measured data supports the second.

**Score-scale, model SE (the convention behind the quoted figures)** — hosted
predicted from the local anchor, compared against the observed hosted mean, in
units of the hosted 50-net SE:

| hypothesis | hosted prediction | z at vD = 0.0814 | z at vD = 0.1220 |
|---|---|---|---|
| R = 1 (parity) | `1.6190838e-7` | **1.19** (1.35 on the local scale) | 1.13 (1.28) |
| R = 1.6517 | `9.802734e-8` | **4.77** | 4.51 |

**Ratio-scale, measured SE, deterministic** — jackknife on `log(mean ratio)` over
both samples, no RNG anywhere:

| quantity | value | tag |
|---|---|---|
| SE of `log R` (jackknife, both samples) | **`0.113881`** | `[O]` |
| SE of `log R` (delta method on geometric means) | `0.100675` | `[O]` |
| SE of `log R` (model route, hosted 50 + local 100) | `0.119397` | `[D]` |
| **z vs parity** | **1.082** (geo 1.534; model 1.10–1.35) | `[D]` |
| **z vs R = 1.6517** | **5.488** (geo 6.518; score-scale 4.51–4.77) | `[D]` |

Both conventions agree on the finding that matters: **the anchor is about one
standard error from parity and about five from 1.65.** Parity is not refuted by
this observation; 1.65 is refuted several times over.

---

## 7. New this session — the two suites are disjoint

The hosted 50 and the local 100 were checked for overlap by net name for the first
time. `a1_hosted_ledger.json` carries all 50 hosted names with `idx 0..49`;
`kerdock_v3_official100.json` carries all 100 local names.

**Intersection: 0 names.** [O]

Consequences:

1. There is **no per-net pairing available**. The anchor is paired at the
   *artifact* level (same frozen estimator, same version pins) and unpaired at the
   *net* level. Every interval on R therefore carries both suites' sampling error
   in full; no variance cancels.
2. The divergence is a genuine **between-suite** question, not a
   measurement-repeatability question about the same networks. R has a true value
   that is not 1 unless the two 50/100-net draws happen to be equally difficult.
3. **A second paired anchor is cheap and is the settling check for this entire
   document.** Any second graded submission of an already-locally-scored artifact
   produces one more independent R. Two anchors would cut the interval on
   `log R` by roughly √2 and, more importantly, would separate sampling error
   from a real suite offset for the first time.

---

## 8. The kill, recorded context-indexed

Kills are context-indexed; an axis change is a premise change. Recorded so that
the retirement below cannot be over-read into axes it never touched.

- **What is retired:** the scalar `R = 1.652` (equivalently `1.6516655333837535`)
  as a local→hosted score conversion factor, in **both** directions.
- **Carrier:** plain budget-matched **antithetic Monte Carlo**, 57 344 samples,
  dense forward, final layer only. Not the Kerdock/MUB carrier. Not
  `row_blocked`. Not any design-based estimator.
- **Precision / convention:** adjusted final-layer score under
  `S = MSE × max(floor, C/B)`, pinned v0.14 subprocess runner, flopscope 0.10.0,
  seed 0, denominator = the grader's *printed* MC reference on the hosted public
  50 treated as exact.
- **Kill type:** distributional misread (Class 2) — a statistic computed correctly
  and read under an assumption its distribution does not satisfy — compounded by
  a failed out-of-sample prediction (§5). Not an arithmetic kill: the C1 run
  reproduces exactly (§2.1).
- **Tissue preserved, explicitly not killed:**
  - the MC-lane **median parity** `1.0005` — this is a *survivor*, and it is now
    load-bearing evidence for R ≈ 1;
  - the C1 panel itself and its dispersion statistics;
  - the `gm_c1_bound` bootstrap/jackknife machinery and its DEVIATION 2, which
    generalise to any future anchor;
  - the exclusion-channel bounds `[1.574, 2.356]` as an *undirected* sensitivity;
  - the anchor-SE correction of ledger 260 (§2.2), which is a real defect repair
    independent of the ratio artifact.
- **Detection rule to keep:** before any location statistic is used as a ratio
  between populations, report mean, median and max on both sides, and require the
  claimed level shift to survive on the median [R].

---

## 9. The uncertainty band every position statement must carry

Until a second paired anchor exists, any sentence of the form "we would sit at /
ahead of / behind X on the hosted board" must be qualified by this band:

| quantity | value | route |
|---|---|---|
| **R point estimate** | **0.884** | mean ratio, both sides recomputed `[O]` |
| **68 % interval** | **[0.790, 0.990]** | jackknife on `log R`, lognormal `[D]` |
| **95 % interval** | **[0.707, 1.105]** | jackknife on `log R`, lognormal `[D]` |
| 95 % via geometric means | [0.703, 1.044] | delta method `[D]` |
| 95 % via the S1b model SE | [0.700, 1.117] | model route `[D]` |

Three routes, one conclusion: **the interval contains 1.0 and excludes 1.65 by a
wide margin.**

**One-sided reading, and the reason for it.** The local side of the anchor is
public 0..99, which is **burned-descriptive** — the champion lineage was developed
against it [R, `GEN3_RECURSION_PACKET_20260808.md` §6, `SUBMISSION_DOSSIER_20260808.md`
§1]. The hosted side was completely out-of-sample: #326094 was the first live
submission of that artifact. An in-sample numerator over an out-of-sample
denominator biases `R = local/hosted` **downward**. The magnitude is unmeasured
`[A]`, but the direction is not in doubt, so:

> **Planning default: R = 1.0. Conservative arm: R = 0.884. Never use R > 1.**

Settling check for the burn bias, and it is the same check as §7: grade a second
artifact whose local score came from a split it was not tuned on.

---

## 10. Consequence table

Hosted projection = local ÷ R. Columns: parity, the anchor point, the 95 % band
edges, and the retired constant shown only so its size can be seen.

| candidate | local | **R = 1.000** | **R = 0.884** | R = 0.707 (lo) | R = 1.105 (hi) | ~~R = 1.6517~~ |
|---|---|---|---|---|---|---|
| kerdock_v3 (ledger 183) `[O]` | `1.6191e-7` | `1.6191e-7` | **`1.8313e-7`** | `2.2893e-7` | `1.4650e-7` | ~~`9.803e-8`~~ |
| row_blocked L1 champion `[R]` | `2.1218e-7` | `2.1218e-7` | `2.4000e-7` | `3.0001e-7` | `1.9199e-7` | ~~`1.2846e-7`~~ |
| two-axis L2 `[R]` | `2.1020e-7` | `2.1020e-7` | `2.3776e-7` | `2.9721e-7` | `1.9019e-7` | ~~`1.2727e-7`~~ |
| fold m=2, λ survives `[R*]` | `1.5677e-7` | `1.5677e-7` | `1.7732e-7` | `2.2167e-7` | `1.4185e-7` | ~~`9.492e-8`~~ |
| fold m=2 + 129@0.82 `[R*]` | `1.2856e-7` | `1.2856e-7` | `1.4541e-7` | `1.8178e-7` | `1.1632e-7` | ~~`7.784e-8`~~ |
| fold, λ dies @0.1 `[R*]` | `1.2088e-7` | `1.2088e-7` | `1.3673e-7` | `1.7092e-7` | `1.0938e-7` | ~~`7.319e-8`~~ |
| fold + 129@0.78, λ dies `[R*]` | `9.4283e-8` | `9.4283e-8` | `1.0664e-7` | `1.3331e-7` | `8.5309e-8` | ~~`5.708e-8`~~ |

The kerdock_v3 row at R = 0.884 returns `1.8313e-7`, the observed hosted grade, by
construction. That is the table's self-consistency check, not a prediction.

### 10.1 Against the declared front — Puffi `9.10e-8` `[R]`

Multiple of Puffi; **> 1 means behind Puffi**.

| candidate | R = 1.000 | R = 0.884 | R = 0.707 | R = 1.105 | ~~R = 1.6517~~ |
|---|---|---|---|---|---|
| kerdock_v3 `[O]` | 1.779 | 2.012 | 2.516 | 1.610 | ~~1.077~~ |
| row_blocked L1 `[R]` | 2.332 | 2.637 | 3.297 | 2.110 | ~~1.412~~ |
| two-axis L2 `[R]` | 2.310 | 2.613 | 3.266 | 2.090 | ~~1.399~~ |
| fold m=2, λ survives `[R*]` | 1.723 | 1.949 | 2.436 | 1.559 | ~~1.043~~ |
| fold m=2 + 129@0.82 `[R*]` | 1.413 | 1.598 | 1.998 | 1.278 | ~~**0.855**~~ |
| fold, λ dies @0.1 `[R*]` | 1.328 | 1.502 | 1.878 | 1.202 | ~~**0.804**~~ |
| fold + 129@0.78, λ dies `[R*]` | **1.036** | 1.172 | 1.465 | **0.937** | ~~**0.627**~~ |

### 10.2 Against ednacob `1.845e-8` `[R]`

Multiple of ednacob; all candidates are behind it on every branch.

| candidate | R = 1.000 | R = 0.884 | R = 0.707 | R = 1.105 | ~~R = 1.6517~~ |
|---|---|---|---|---|---|
| kerdock_v3 `[O]` | 8.78x | 9.93x | 12.41x | 7.94x | ~~5.31x~~ |
| row_blocked L1 `[R]` | 11.50x | 13.01x | 16.26x | 10.41x | ~~6.96x~~ |
| two-axis L2 `[R]` | 11.39x | 12.89x | 16.11x | 10.31x | ~~6.90x~~ |
| fold m=2, λ survives `[R*]` | 8.50x | 9.61x | 12.01x | 7.69x | ~~5.14x~~ |
| fold m=2 + 129@0.82 `[R*]` | 6.97x | 7.88x | 9.85x | 6.30x | ~~4.22x~~ |
| fold, λ dies @0.1 `[R*]` | 6.55x | 7.41x | 9.26x | 5.93x | ~~3.97x~~ |
| fold + 129@0.78, λ dies `[R*]` | 5.11x | 5.78x | 7.23x | 4.62x | ~~3.09x~~ |

*Note on the ednacob figure.* `1.845e-8` is the 2026-08-18 Discourse sweep [R,
`PHASE2_CONTRIBUTION_DRAFT_20260819.md` §…]. The Phase-1 snapshot in
`RAYAN53_FORENSICS_20260810.md` records ednacob at adjusted `4.62e-8` (raw
`9.11e-8`, C/B 0.507) [R]. The gap is a real leaderboard move, not a
transcription error; both are quoted where they appear. The anomaly flagged in
`DESIGNATION_POLICY_20260819.md` — that `1.845e-8` sits below what kaileh57's
Arb-certified LP permits — is unresolved and is not this document's business.

### 10.3 The inverted table — what local score buys a given hosted position

| target | R = 1.000 | R = 0.884 | R = 0.707 | R = 1.105 | ~~R = 1.6517~~ |
|---|---|---|---|---|---|
| match Puffi `9.10e-8` | `9.100e-8` | **`8.045e-8`** | `6.436e-8` | `1.006e-7` | ~~`1.503e-7`~~ |
| match ednacob `1.845e-8` | `1.845e-8` | `1.631e-8` | `1.305e-8` | `2.039e-8` | ~~`3.047e-8`~~ |

The retired constant made a local `1.503e-7` look like a tie with the front. The
honest map requires a local `8.0e-8`–`9.1e-8` for the same claim — a factor of
**1.66–1.87x** more MSE reduction than the corpus has been budgeting for.

---

## 11. What this does to the designation memo

`DESIGNATION_POLICY_20260819.md` compares local candidate scores directly against
hosted leaderboard numbers throughout. That is the **R = 1 assumption**, used
without being named. This document's finding is that R = 1 is the correct default
— so the memo's arithmetic is not wrong — but that it is carrying an unpriced
uncertainty which happens to be the largest one in its variance budget.

### 11.1 The §2.2 claim

> "At 9.4e-8 slot 1 would sit at or ahead of the declared front (Puffi 9.10e-8)."

That sentence is true at R = 1.000 (`9.428e-8`, 1.036x Puffi, essentially level)
and false at the anchor point R = 0.884 (`1.066e-7`, **1.172x Puffi, behind**) and
at the band's adverse edge R = 0.707 (`1.333e-7`, **1.465x**). It becomes a clear
win only at R ≥ 1.036 [D]. **The claim needs the band attached; it does not need
withdrawing.**

### 11.2 The W3 R-posture table omits the transfer term

W3 prices `P(beat rival)` from S1's suite-mean CV alone: **0.08541 at R=1, 0.03507
at R=6** [R]. I reproduce its Puffi leaf exactly — for the `9.91e-8` candidate,
`Φ(ln(9.10e-8 / 9.91e-8) / 0.085255) = 0.1586` against W3's printed 0.169 [D].

But that variance budget contains only the *future* suite's sampling noise. A
local→hosted statement additionally carries the **local anchor's own sampling
error**, measured at **6.950 %** on 100 nets (§3.4) — and rotation splitting
cannot reduce it, because R=6 is a within-suite variance dial while the transfer
is a between-suite quantity. Adding that one term, which is the minimum honest
addition and still excludes any true suite-offset variance:

| variance budget | log-sd | P(beat Puffi), candidate `9.91e-8` at R=1 |
|---|---|---|
| W3 as published, R = 1 | `0.08525` | **0.159** |
| W3 as published, R = 6 | `0.03506` | **0.008** |
| **+ local-anchor SE, R = 1** | `0.11000` | **0.219** |
| **+ local-anchor SE, R = 6** | `0.07784` | **0.137** |

[D, all four recomputed this session.]

W3's headline — R=6 collapses the Puffi overtake from ~0.17 to ~0.01, a 20x
reduction, "certainty of second against a one-in-six shot at first" — becomes
**0.219 → 0.137, a 1.6x reduction**, once the transfer term is present. The R
lever is real but far less decisive than published, in both of its directions:
R=6 neither locks the position nor extinguishes the reach, because the variance
it removes is not the variance that dominates.

The same table at the anchor point R = 0.884 puts the overtake at **≤ 0.03 under
every variance budget** [D]. The R-posture question and the transfer question are
not independent, and the transfer question is the larger of the two.

**Level statement.** §11.2 is `[D]` from `[O]` inputs. It assumes the transfer
uncertainty is independent of the rotation-split dial (structurally true) and
that S1's CV figures are the right suite-noise model (`[R]`, and the measured
hosted SE of 8.89 % supports the R=1 arm to within 4 %). It does **not** attempt
to price a true suite-difficulty offset, which one anchor cannot separate from
sampling error. Every number here is therefore a **lower bound on the uncertainty**,
in the same sense as `gm_c1_bound` DEVIATION 2.

---

## 12. Attacks run on this document's own conclusion

1. **"The anchor is a single lucky/unlucky hosted draw."** Partly true and
   already priced: the hosted 50-net mean carries 8.89 % measured SE, which is
   most of the 11.39 % on `log R`. It cannot rescue 1.65 — that would need a
   5.5-sigma draw — but it is exactly why the band in §9 is as wide as it is.
2. **"The mean ratio is itself skew-sensitive; that is what killed 1.65."** Tested
   directly. Geometric-mean ratio **0.857**, median ratio **0.784** [O]. Both are
   *more* adverse than the mean ratio, not less. The attack lands on the
   optimistic side of the conclusion and makes it slightly worse, which is
   reported rather than smoothed.
3. **"The hosted ledger's 3-digit rounding drives the result."** Tested by
   perturbing all 50 rows ±½ ulp: R moves to `0.8822 / 0.8860` [O]. It does not.
4. **"The local anchor is burned, so R is biased."** True, and it is the one
   attack that changes the recommendation: it pushes the honest R **up** toward
   and possibly past 1, which is why §9 sets the planning default at R = 1 rather
   than at the 0.884 point estimate.
5. **"Maybe the suites share nets and the whole framing is wrong."** Tested:
   zero name overlap across 150 nets (§7). The framing holds.
6. **What was not looked at.** No hosted read of any kind was performed (firewall).
   The "rank 13–14" claim in `C1_REPORT.md` remains **untested**, not merely
   unchanged [R, `gm_c1_bound` DEVIATION 1] — it needs a leaderboard read. No
   second paired anchor exists, so the true suite offset cannot be separated from
   sampling error by anything in this document.

---

## 13. Ledger and settling checks

| claim | level | settling check | cost |
|---|---|---|---|
| C1 panel statistics, R = 1.6517, median parity | `[O]` | none needed — recomputed from `c1_local_mc25.json` this session, exact | done |
| Anchor R = 0.884, both sides recomputed | `[O]` | none needed — `fold_ledger.json` record 183 + `kerdock_v3_official100.json` + `a1_hosted_ledger.json` | done |
| Suites disjoint | `[O]` | none needed — 0/150 name intersection | done |
| Band `[0.707, 1.105]` on R | `[D]` | **grade a second already-locally-scored artifact** — the single highest-value check in the campaign for this question | one submission slot |
| Burn bias direction (R biased low) | `[A]` | score an artifact on a split it was not developed against, then grade it | one clean split + one slot |
| True suite-difficulty offset vs sampling error | unresolved | ≥ 2 paired anchors | 2 slots |
| Fold-lane local scores `[R*]` | pending | **round-4 bill repair re-run**; `D-A3a` / `D-A3b` blocking | round-4 |
| §11.2 recomputed overtake probabilities | `[D]` | re-derive once the fold lane's bill is repaired and the local anchors are re-measured | round-4 |
| "rank 13–14" | untested | hosted leaderboard read | firewall-gated |

**Files read (all read-only).**
`experiments/gm_c1_bound/VERDICT.md`;
`experiments/c1_local_mc_calibration/{c1_local_mc25.json, C1_REPORT.md, C1_PREDECLARATION.md}`;
`experiments/t4_kerdock_descriptive_rescore/kerdock_v3_official100.json`;
`experiments/a_series_granular_adversarial/a1_hosted_ledger.json`;
`headroom/fold_ledger.json` (record 183);
`core/{CODEX_HANDOFF_20260810.md, SUBMISSION_RESULT_20260808.md, DESIGNATION_POLICY_20260819.md, SUBMISSION_DOSSIER_20260808.md, KILL_CONTEXT_INDEX_20260819.md, CONTINUATION_PLAN_20260817.md, GEN3_RECURSION_PACKET_20260808.md, PHASE2_CONTRIBUTION_DRAFT_20260819.md, RAYAN53_FORENSICS_20260810.md}`;
`experiments/fold_floor_splice/{FOLD_FLOOR_SPLICE_PRODUCTION_GATE.md, full.json}` (read-only, no execution).

**Nothing was written outside this file. No harness run, no FlopScope, no network,
no submission, no truth/scorer/holdout read, zero estimator compute.**
