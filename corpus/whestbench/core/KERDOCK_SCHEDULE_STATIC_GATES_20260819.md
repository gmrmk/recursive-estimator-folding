# KERDOCK-HOST DEPTH-2 SCHEDULE — THE TWO STATIC PAPER GATES (G-A, G-B)

Stamped: 2026-08-19. Executor: Fable, static-gate pass on
`core/MI_SOLVE_20260819.md` finding 2 / WAVE 1 (`W1.1` G-A eligibility, `W1.2` G-B
residual). Door under test: **`kerdock_host_depth2_winograd_schedule_pass`** — the
MERGE of idx 58/59's fused-L2 operator and idx 268's l2-fringe schedule, one door,
two operators, never two predeclarations.

## 0. Compliance and reading order

**Zero billed compute.** No harness, no FlopScope, no estimator execution, no scored
row, no cell predeclared, no seed consumed. Every `python` invocation in this pass ran
`python -B -P` with `PYTHONDONTWRITEBYTECODE=1` from a scratch directory outside the
corpus; the only corpus files touched were read-only source and recorded JSON
artifacts. `experiments/fold_floor_splice`, `experiments/frame_completion_129`,
`cells/` and `row_blocked_production` were **not written**; of those,
`experiments/fold_floor_splice`, `experiments/frame_completion_129` and `cells/` were
not read either, and `cells/` appears below only as a path string returned by one
`grep` over the corpus.

**The banned instrument.** The 2026-08-19 slope law
(`headroom/slope_cost_model.py`, `headroom/SLOPE_COST_MODEL_20260819.*`) is refuted in
round 1(b) and is **not used anywhere in this document**. It was not loaded, not
imported, and no number below derives from it.

**Reading order is the audit trail.** Each gate's threshold, denominator, and
ineligibility rule are written in a PREDECLARATION section that precedes the section
containing its number. Nothing below reorders that.

**Evidence tags on every number.** **[O]** observed by this pass (a file read here, a
command run here, an exact integer computed here from frozen source). **[D]** derived
here by arithmetic that is shown. **[R]** reported by a corpus record or an upstream
stage and not re-derived here. **[A]** an assumption this pass chose, named as such.

---

## 1. The frozen entrypoint, identified and hash-verified

The ledger route: idx 183 `t4_kerdock_v3_descriptive_rescore` names the artifact —
"execute the frozen Kerdock M71 v3 entrypoint exactly once … frozen estimator sha
`076D0A5D…` verified" [O, `headroom/fold_ledger.json` candidates[183].mechanism]. idx
206 `v31_guards_m186_m187` names the package that carries it — "frozen v3 + M186 …
+ M187 …; subclass-only" [O, candidates[206].mechanism]. The t4 dossier states the
full bracket: "estimator sha256 076D0A5D…9AACF verified before launch; sources
untouched" [O, `experiments/t4_kerdock_descriptive_rescore/T4_REPORT.md:6`], and the
t5-lineage guards dossier names the file: "riding along renamed
`kerdock_v3_estimator.py` (sha256 `076d0a5d…`)" [O,
`experiments/v31_guards/V31_NOTES.md:72`].

Verification run here [O]:

| file | sha256 |
|---|---|
| `experiments/v31_guards/package_source/kerdock_v3_estimator.py` | `076d0a5d81891ddcbb4509dc6e2bff5459d935b5556490a85d98dac60759aacf` |

Both ends of the recorded fingerprint match: prefix `076D0A5D` (idx 183, T4_REPORT,
V31_NOTES) and suffix `…9AACF` (T4_REPORT). The v3.1 guards subclass
`estimator.py` hashes `5e7d5215…` and states in its own header that it "only
subclasses and adds the two guards" [O]. **The analysed entrypoint is the frozen
v3 file at `076d0a5d…`.**

Its deployed route, read in source [O]:

- `_sample_matmul(values, weight, firing_rates, *, out)` →
  `self._winograd.multiply(values, weight, out=out)`, where `self._winograd` is
  `RowBlockedBatchedWinograd(2*n_base, width, BLOCK_ROWS)` and
  `BLOCK_ROWS = 4_096` [O, `row_blocked_winograd.py:20`]. **This is m71's row-local
  4096-row Winograd transfer.**
- `_first_sample_matmul(phases, weight, *, out)` → the phased-WHT butterfly:
  `fnp.multiply` of the phase table into the output, then a `log2(256) = 8`-stage
  in-place add/subtract butterfly against `self._wht_scratch`, then one scale by
  `MEAN_CHI_256/16` [O, lines 103–132]. **No `matmul` call occurs on this path.**
- The deep-hook loop is `for layer in range(1, mlp.depth - 3)` in the parent
  `fold3_estimator.Estimator.predict` [O, `fold3_estimator.py:122`], so at the
  production geometry width 256 / depth 32 it issues exactly **28** hook products,
  with the first product and the three terminal folded layers outside it.

---

## 2. G-A — PREDECLARATION (written before the number)

Verbatim from the authority, `MI_SOLVE_20260819.md` §W1.1:

> Gate: enumerate the 28 deep-hook matrix products on the frozen kerdock_v3
> entrypoint (sha 076D0A5D...), mark those covered by m71's row-local 4096-row
> Winograd transfer and the phased-WHT layer-1 butterfly (ineligible by
> construction). PREDECLARE CLOSED if eligible effective-bill share < 9%. Use idx
> 264's measured methodology, NOT a depth-1 dispatcher figure — the 57.4164% →
> 8.98%/6.12% error is precisely what killed U-F1.

**G-A.1 Threshold.** `eligible effective-bill share < 9%` → the door **CLOSES** on
G-A. `>= 9%` → G-A passes and G-B decides.

**G-A.2 Enumeration domain.** The 28 deep-hook matrix products issued by
`fold3_estimator.predict`'s `range(1, depth-3)` loop through
`kerdock_v3_estimator._sample_matmul`, at the production geometry width 256 /
depth 32. The first product (phased-WHT butterfly) and the three terminal folded
layers are outside the domain by construction.

**G-A.3 Ineligibility by construction — the two clauses, stated before use.**

1. **Phased-WHT layer-1 butterfly.** The first product is excluded. It issues no
   `matmul` and has no `(m,k,n)` contraction for a leaf schedule to split.
2. **m71's row-local 4096-row Winograd transfer.** Any FLOP a *one-level* row-local
   owned Winograd transfer already banks, or would bank at that shape, is m71's and
   is **not** the depth-2 schedule's. Concretely: the depth-2 door owns only the
   increment `best_one_level_owned_route − two_level_mod4_route`. The increment
   `frozen_deployed_charge − best_one_level_owned_route` is the one-level transfer's
   and is ineligible. This is the operational form of idx 264's "removing the
   already-Winograd double count".

**G-A.4 Denominator and normalisation — idx 264's measured methodology.** The
methodology is fixed by `experiments/uf1_attack_eligibility/attack_translate.py`
§C1 and its recorded outputs, which are the source of idx 264's surviving
`8.98% / 6.12%` pair [O, code read here; values [R] from the recorded JSON and
reproduced below]:

- denominator = the **measured matmul lane** of the frozen predict path
  (`matmul_lane_charged`), per net, over the recorded 5-net He panel
  (width 256 / depth 32, seeds 11–15);
- numerator = `(current_hook_charge − new_hook_charge)`, where the *current* charge
  is the frozen operator's already-Winograd bill, never the direct bill;
- `effective-bill share` = `(numerator / lane) / (1 − r_d)` with `r_d` the route's
  own ratio at the reference shape `(64512×256)@(256×256)`;
- reported as the mean over the 5 nets, with the 95% CI carried.

The **named trap**: `57.4164%` is a depth-1 *dispatcher* figure (fraction of the
direct hook bill sitting in shapes the dispatcher would send to Winograd at all),
measured on one net. It is not an eligibility for a deeper schedule and must not be
quoted as one. This pass does not use it.

**G-A.5 W0.10 companion, predeclared here.** Is idx 268's l2-fringe route applicable
on **leaf-shape grounds** — 49 leaves at `m/4, k/4, n/4` — to (a) the eligible hooks
and (b) the first-product WHT path? If inapplicable, m184's narrowed scope claim
survives on the schedule axis and the door loses its corroborating precedent.

---

## 3. G-A — the enumeration and the number

_(section written after §2; numbers below are the first appearance of any G-A
result in this document)_

### 3.1 The measurement basis, and why no estimator ran

The 28 hook shapes and their exact charges are already on disk. idx 264's hostile
eligibility fleet instrumented the frozen v3 predict path with a behaviour-preserving
logging subclass and recorded, per net, every hook's `(m,k,n)` and its exact FlopScope
charge, over 5 He nets at width 256 / depth 32, seeds 11–15 [O,
`experiments/uf1_attack_eligibility/attack_eligibility.py` read here;
`attack_eligibility_raw.json` read here]. That artifact is this pass's input, so
nothing re-executes.

Its own two-signal check is recorded and re-read here: all 140 hook charges (5 nets ×
28) equal `cost_model.owned_batched_candidate_bill(m,k,n).total` **exactly**, 140/140,
zero mismatches [O, `attack_translation.json`
`A_tape_verification_vs_frozen_cost_model`], and the shape sequence reconstructs
independently with `sequences_match: true`, `total_charged` bit-identical on repeat
[O, `attack_verify.json`]. So the deployed operator's bill is a closed form, and the
whole of G-A is exact integer arithmetic over that closed form.

**Lane structure, measured, 5 nets** [O, recomputed here from the recorded runs]:

| quantity | mean | CI95 |
|---|---|---|
| total charged per net | 165,153,439,008.8 | — |
| matmul lane per net | 163,356,937,908.8 | — |
| matmul share of total | 0.98912021 | [0.98815743, 0.99008298] |
| deep-hook share of the matmul lane | 0.93527808 | [0.91527606, 0.95528010] |
| non-hook matmul share of the lane (pilots, terminal folds, tangent loop) | 0.06472192 | — |
| **phased-WHT first product, share of total** | **0.00160475** | [0.00148629, 0.00172322] |

This corrects one figure the plan carries: MI_SOLVE quotes "the ~1.06% phased-WHT
lane". 1.088% is the **whole non-matmul lane**; the phased-WHT first product itself is
**0.160%** of the total charged bill. The 98.94% matmul figure is right to within
sampling: 98.912% measured [O/D].

### 3.2 The 28 deep-hook products, seed 11 (reference net)

`m = 2 × n_base = 2 × 126 × 256 = 64,512` on every hook; `k = |active|`,
`n = |next_active|`. "m71 cov" = the frozen operator selects a Winograd branch at that
shape. "L1 best" = the cheapest **one-level** owned route at that shape (frozen
branch, the odd-k outer-product branch, or the dual-odd branch — all one level, all
m71's row-local transfer). "L2 mod4" = idx 268's two-level route, 49 leaves at
`m/4,k/4,n/4`, priced **per 4096-row block** (the pessimistic accounting: the
`k×n` transform term is paid once per block, not hoisted). All integers [O].

| # | k | n | frozen charge (deployed) | m71 cov | L1 best | L1 route | L2 mod4 (blocked) | ΔFLOP L1 (INELIGIBLE) | ΔFLOP L2 (ELIGIBLE) | L2 leaf shape |
|--:|--:|--:|--:|:-:|--:|:--|--:|--:|--:|:--|
| 1 | 256 | 256 | 7,427,768,320 | yes | 7,427,768,320 | frozen winograd | 6,587,334,656 | 0 | 840,433,664 | exact |
| 2 | 256 | 253 | 7,345,191,168 | yes | 7,345,191,168 | frozen winograd | 6,518,679,552 | 0 | 826,511,616 | fringe n+1 |
| 3 | 253 | 255 | 8,323,854,336 | no | 7,320,288,654 | dual-odd | 6,515,198,928 | 1,003,565,682 | 805,089,726 | fringe k+1 n+3 |
| 4 | 255 | 253 | 8,324,112,384 | no | 7,320,514,446 | dual-odd | 6,515,198,928 | 1,003,597,938 | 805,315,518 | fringe k+3 n+1 |
| 5 | 253 | 248 | 8,095,804,416 | no | 7,116,170,040 | odd-k | 6,316,650,144 | 979,634,376 | 799,519,896 | fringe k+1 |
| 6 | 248 | 244 | 6,859,666,856 | yes | 6,859,666,856 | frozen winograd | 6,086,818,528 | 0 | 772,848,328 | exact |
| 7 | 244 | 239 | 6,615,226,618 | yes | 6,615,226,618 | frozen winograd | 5,889,654,064 | 0 | 725,572,554 | fringe n+3 |
| 8 | 239 | 227 | 7,000,713,216 | no | 6,159,474,097 | dual-odd | 5,503,960,448 | 841,239,119 | 655,513,649 | fringe k+3 n+3 |
| 9 | 227 | 223 | 6,531,581,952 | no | 5,747,816,697 | dual-odd | 5,139,272,320 | 783,765,255 | 608,544,377 | fringe k+3 n+3 |
| 10 | 223 | 217 | 6,243,987,456 | no | 5,495,441,868 | dual-odd | 4,902,942,240 | 748,545,588 | 592,499,628 | fringe k+3 n+1 |
| 11 | 217 | 218 | 6,103,544,832 | no | 5,368,706,532 | odd-k | 4,787,770,176 | 734,838,300 | 580,936,356 | fringe k+1 n+2 |
| 12 | 218 | 216 | 5,340,740,580 | yes | 5,340,740,580 | frozen winograd | 4,759,642,944 | 0 | 581,097,636 | fringe k+2 |
| 13 | 216 | 214 | 5,242,971,132 | yes | 5,242,971,132 | frozen winograd | 4,673,775,456 | 0 | 569,195,676 | fringe n+2 |
| 14 | 214 | 199 | 4,835,474,343 | yes | 4,835,474,343 | frozen winograd | 4,329,229,072 | 0 | 506,245,271 | fringe k+2 n+3 |
| 15 | 199 | 204 | 5,237,535,744 | no | 4,608,904,734 | odd-k | 4,115,702,640 | 628,631,010 | 493,202,094 | fringe k+3 |
| 16 | 204 | 195 | 4,517,393,034 | yes | 4,517,393,034 | frozen winograd | 4,036,161,024 | 0 | 481,232,010 | fringe n+3 |
| 17 | 195 | 207 | 5,207,279,616 | no | 4,585,550,641 | dual-odd | 4,109,269,248 | 621,728,975 | 476,281,393 | fringe k+3 n+3 |
| 18 | 207 | 189 | 5,048,967,168 | no | 4,446,589,630 | dual-odd | 3,975,553,680 | 602,377,538 | 471,035,950 | fringe k+3 n+1 |
| 19 | 189 | 189 | 4,608,866,304 | no | 4,060,189,084 | dual-odd | 3,622,376,912 | 548,677,220 | 437,812,172 | fringe k+1 n+1 |
| 20 | 189 | 182 | 4,438,619,136 | no | 3,907,680,742 | odd-k | 3,496,140,144 | 530,938,394 | 411,540,598 | fringe k+1 n+2 |
| 21 | 182 | 169 | 3,495,991,044 | yes | 3,495,991,044 | frozen winograd | 3,131,241,120 | 0 | 364,749,924 | fringe k+2 n+1 |
| 22 | 169 | 183 | 3,989,422,080 | no | 3,516,280,068 | dual-odd | 3,150,675,360 | 473,142,012 | 365,604,708 | fringe k+1 n+3 |
| 23 | 183 | 191 | 4,509,259,776 | no | 3,972,741,731 | dual-odd | 3,566,167,920 | 536,518,045 | 406,573,811 | fringe k+3 n+3 |
| 24 | 191 | 185 | 4,559,450,112 | no | 4,016,804,092 | dual-odd | 3,594,804,640 | 542,646,020 | 421,999,452 | fringe k+3 n+1 |
| 25 | 185 | 178 | 4,249,211,904 | no | 3,741,430,756 | odd-k | 3,348,956,800 | 507,781,148 | 392,473,956 | fringe k+1 n+2 |
| 26 | 178 | 174 | 3,516,764,601 | yes | 3,516,764,601 | frozen winograd | 3,157,096,768 | 0 | 359,667,833 | fringe k+2 n+2 |
| 27 | 174 | 163 | 3,224,455,857 | yes | 3,224,455,857 | frozen winograd | 2,900,756,096 | 0 | 323,699,761 | fringe k+2 n+3 |
| 28 | 163 | 182 | 3,826,400,256 | no | 3,370,513,293 | odd-k | 3,028,927,104 | 455,886,963 | 341,586,189 | fringe k+3 n+2 |
| | | | | | | | **totals** | **11,543,513,583** | **15,416,783,746** | |

The **INELIGIBLE** column is the whole content of G-A.3 clause 2: 11.54 B FLOPs per
net that a *one-level* row-local owned Winograd transfer already banks or would bank.
Crediting that column to a depth-2 schedule is the 2026-08-11 U-F1 error wearing a
new coat, and it is removed before the gate reads a number.

### 3.3 The route arithmetic, verified against idx 268's own recorded ratio

At the reference shape `(64512×256)@(256×256)` [O, exact integers computed here]:

```
direct                          8,439,201,792
frozen owned (m71, one level)   7,427,768,320    r_prod = 0.88015057621222
L2 mod-4 route, unblocked       6,582,603,776    vs one level = 0.886215548521578
L2 mod-4 route, 4096-blocked    6,587,334,656    vs one level = 0.886852466610052
```

`r_prod = 0.88015057621222` reproduces idx 264's surviving common-evidence constant
`r_prod = 0.88015058` to the ninth digit [O vs R] — the first independent signal that
this pass's cost models are the campaign's.
`grouped_l2_candidate_bill(4096,256,256).total / owned_batched_candidate_bill(4096,256,256).total
= 0.8866399221979091` [O] reproduces idx 268's recorded
`cost_model_route_ratio_4096x256x256 = 0.88664` to 5 significant digits [O vs R] —
the second signal.

### 3.4 THE G-A NUMBER

Applying G-A.4's normalisation, `share = (eligible saving / matmul lane) / (1 − r_ref)`
with `r_ref = 0.8868524666100517`, over the 5-net panel [O/D]:

| operator (both are inside the merged door) | eligible ΔFLOP / net | eligible saving / lane | **eligible effective-bill share** | CI95 |
|---|--:|--:|--:|---|
| **idx 268 l2-fringe** (mod-4 core + fringe) | 15,606,373,342 | 0.09555177 | **0.84448833** | [0.81838813, 0.87058853] |
| **idx 58/59 fused strict** (49-leaf core, L1 fallback elsewhere) | 2,216,269,776 | 0.01357238 | **0.11995299** | [0.07151861, 0.16838737] |

**G-A VERDICT: PASS.** Both operators of the merged door clear the predeclared
`< 9% ⇒ CLOSE` bar; the door's magnitude operator clears it by 9.4×. The gate does
not close the door.

### 3.5 What the gate would have said under three other readings (stated, not used)

The predeclared rule is §2's. These are reported because a reader is owed the
sensitivity, not because the verdict rests on them:

| reading | number | would have |
|---|--:|---|
| **predeclared** (§2, per-FLOP double-count removal, fringe route) | 84.45% | pass |
| predeclared rule, strict fused operator only | 12.00% | pass (CI95 low 7.15% dips under) |
| hard-exclusion: drop every product the frozen operator sends to Winograd, fringe route | 35.37% | pass |
| idx 264's own recorded d=2 **strict** row, verbatim, no L1 correction | **6.3615%** | **close** |

The last row is the one that matters, so it is stated in full. idx 264's artifact
computed depths 1–5, not only 4; its recorded `d2` aggregate is
`strict_eligible_share_of_direct_hook_bill = 0.13637955512972635` and
`effective_eligibility_strict = 0.06361509018149389` [R, `attack_translation.json`].
Its `d4` row reproduces idx 264's published pair exactly — `0.08975283928087245` and
`0.061210792169057074`, i.e. the "8.98% / 6.12%" of the ledger [O vs R], which is the
third signal that this pass is reading the right methodology.

**Why the 6.36% row does not govern.** idx 264's C1-STRICT recurses a hook only when
`2^d` divides `m`, `k` **and** `n`; at `d=2` that is 2–5 of 28 hooks per net, because
the Kerdock active-set trajectory produces `k, n` that are overwhelmingly not
multiples of four (seed 11: `k` runs 256, 256, 253, 255, 253, 248, … 163). idx 268's
operator is **not** C1-STRICT — its name says so and its cost model says so: it takes
the mod-4 core of *every* shape and pays an exact fringe. idx 264's own C2-SPLIT
variant is the one that matches it, and its recorded d=2 value is
`effective_eligibility_split = 0.6782463830100796` [R] — which still carries the L1
double count that §3.2's INELIGIBLE column removes. So the 6.36% figure is the
eligibility of a *different operator* than the one the door's magnitude leg deploys,
and quoting it against idx 268 would be the mirror image of the U-F1 trap: understating
a route by pricing it with a schedule it does not use.

### 3.6 W0.10 companion — leaf-shape applicability, answered

**(a) The eligible hooks: APPLICABLE, 28 of 28, on every net** [O]. The route needs
`m ≡ 0 (mod 4)` and a non-empty mod-4 core. `m = 64,512 = 4 × 16,128`; under the
frozen `BLOCK_ROWS = 4096` the row blocks are 15 × 4096 + 1 × 3072, and both 4096 and
3072 are multiples of 4, so the leaf shape `m/4` is integral at block level as well as
whole-product level. `core_k = k − k mod 4 ≥ 160 > 0` and `core_n ≥ 160 > 0` on every
observed shape. Split by leaf cleanliness, per net (seeds 11–15): exactly-clean
`winograd_l2_grouped` on **2 / 5 / 3 / 4 / 2** hooks, mod-4 fringe
`winograd_l2_mod4_fringe` on **26 / 23 / 25 / 24 / 26** hooks; 28 total each [O].

**(b) The first-product WHT path: NOT APPLICABLE** [O]. `_first_sample_matmul` issues
no `matmul`: it is `fnp.multiply` of the 126×256 phase table into the caller-owned
output, an 8-stage in-place `add`/`subtract` butterfly against `_wht_scratch`, and one
scalar `multiply`. There is no `(m,k,n)` contraction for 49 leaves to partition. Its
whole charge is 0.160% of the total billed bill [O/D], and it is already `O(n log n)`
where any leaf schedule prices `O(n^log2 7)`.

**Consequence for m184's scope annotation.** The companion's "if inapplicable" branch
does **not** fire. idx 268's route is applicable to 100% of the deep-hook lane, so the
door **keeps** its corroborating precedent, and m184's clause-narrowing is confirmed
necessary rather than merely tidy: the compiler-schedule mechanism m184 never
enumerated reaches the entire lane it measured. The annotation's own framing survives
unchanged, because applicability is not magnitude — idx 268's measured 8.5508%
flop-only / 5.0086% effective reductions still sit below m184's 15% kill bar and far
below its 20% promote bar [R]. The scope fix stays hygiene, not optimism.

---

## 4. G-B — PREDECLARATION (written before the number)

Verbatim from the authority, `MI_SOLVE_20260819.md` §W1.2:

> Gate: project delta-residual from the operator's own dispatch-count delta on the
> Kerdock route; PREDECLARE CLOSED if projected residual increase exceeds projected
> FLOP saving at lambda = 1e11. Empirical basis: idx 69's measured 0.194269-s point
> and idx 59's measured 69% erosion. Do NOT use the 2026-08-19 slope law (refuted in
> round 1(b)).

**G-B.1 Threshold.** `projected residual increase ≥ projected FLOP saving` (both in
FLOP-equivalents at λ = 1e11, i.e. 1 s of residual = 1e11 FLOPs) → the door **CLOSES**
on G-B. Otherwise G-B passes.

**G-B.2 Projected FLOP saving.** The eligible ΔFLOP from §3.4, per operator, per net —
not the deployment saving, so G-A and G-B price the same object.

**G-B.3 Licensed empirical basis, and nothing else.** Only (i) idx 69's measured
6144-row point — `analytical 0.965263 → effective 0.989874`, `residual 0.194269 s` —
and (ii) idx 59's measured erosion, 69% of the analytical cut lost to residual. The
2026-08-19 slope law is banned by the authority and is not loaded. Anything else that
appears below is labelled OUT-OF-BASIS and does not enter the verdict.

**G-B.4 Dispatch counts are read from source, not assumed.** `Δdispatches` for each
operator is computed from `RowBlockedBatchedWinograd.multiply`'s own call arithmetic
(`core_calls = ceil(m / BLOCK_ROWS)`, `total = core_calls × (1 + [n_c < n])`) against
the candidate route's `call_count` per block. Source is not empirical basis; it is the
operator's own definition.

---

## 5. G-B — the dispatch-count delta and the number

_(section written after §4)_

### 5.1 The dispatch-count delta, from source

Per net, over the 5-net panel, against each operator's own one-level baseline [O/D]:

| operator | Δdispatches / net | why |
|---|--:|---|
| **idx 58/59 fused strict** | **0** | one 49-leaf batched `matmul` replaces one 7-leaf batched `matmul`, block for block. `call_count` is 1 per block before and after. |
| **idx 268 l2-fringe** | **+227.2** | the mod-4 fringe adds an inner-correction call and/or an output-tail call per block on the 23–26 hooks per net that are not mod-4 clean. |

The measured frozen path issues 750.6 `matmul` calls per net [O, recorded op totals],
so the fringe route is a +30.3% dispatch-count change and the strict route is a 0.0%
dispatch-count change.

### 5.2 Route A — idx 59's measured erosion

idx 59's measured pair is `1.069%` of a `3.456%` analytical cut surviving into mean C
[R, MI_SOLVE F3], so the erosion fraction is
`1 − 1.069/3.456 = 0.6906828703703705` [D]. Applying it at λ = 1e11:

| operator | projected ΔFLOP | projected Δ(λR) = 0.6906829 × ΔFLOP | in seconds | fires? |
|---|--:|--:|--:|:-:|
| idx 268 fringe | 15,606,373,342 | 10,779,054,736 | 0.107791 s | **no** |
| idx 58/59 strict | 2,216,269,776 | 1,530,739,570 | 0.015307 s | **no** |

### 5.3 Route B — idx 69's measured triple, converted to an absolute Δresidual

idx 69 ran on the same 64,512-row / 28-hook / depth-32 geometry. Write `A` for its
baseline mean billed compute, `L = λ·R_base`, `D = λ·ΔR`. Its two measured ratios give
one exact linear relation [D]:

```
(0.965263·A + L + D) / (A + L) = 0.989874
  =>  D = 0.024611·A − 0.010126·L
```

and its measured residual pins `λ·R_child = 0.194269 × 1e11 = 19,426,900,000`, so
`L ∈ [0, 19,426,900,000]`. Bracketing `A` between this campaign's two measured billed
levels — the Kerdock host's own measured mean total 165,153,439,009 [O] and idx 53's
recorded max C 222.405e9 [R], an upper bound on any mean — gives four corners [D]:

```
A=165.153B L=0        D = 4,064,591,287     A=165.153B L=19.427B  D = 3,867,874,498
A=222.405B L=0        D = 5,473,609,455     A=222.405B L=19.427B  D = 5,276,892,666
                                       =>  D ∈ [3,867,874,498 , 5,473,609,455]
```

idx 69's own dispatch-count delta, from source: it moved 8192-row blocking to
6144-row blocking on `m = 64,512`, i.e. `ceil(64512/8192) = 8` blocks to
`ceil(64512/6144) = 11` blocks, over 28 hooks at 1 or 2 calls per block —
`Δdispatches₆₉ ∈ [28·3·1, 28·3·2] = [84, 168]` [D]. Scaling idx 69's absolute `D` by
`227.2 / Δdispatches₆₉` gives the Kerdock fringe route's projection at every corner:

| corner | scale | projected Δ(λR) | vs ΔFLOP 15,606,373,342 | fires? |
|---|--:|--:|:-:|:-:|
| `D` min, `Δ₆₉` = 168 | 1.3524 | 5,230,839,797 | below | no |
| midpoint, `Δ₆₉` = 126 | 1.8032 | 8,422,163,310 | below | no |
| `D` max, `Δ₆₉` = 84 | 2.7048 | 14,804,810,335 | below | **no** |

The worst corner is 94.9% of the projected FLOP saving and still does not reach it.
For the strict operator `Δdispatches = 0`, so Route B projects `Δ(λR) = 0`.

### 5.4 Route C — DISQUALIFIED, and the disqualification is the finding

The one construction that fires is idx 69's `100M-per-wrapper-call` proxy:
`227.2 × 1.0e8 = 22,720,000,000 ≥ 15,606,373,342` → would close.

It is disqualified, on idx 69's own verdict. The proxy is not a measurement; it is the
frozen shape-only dispatcher heuristic named in idx 69's mechanism — "choose direct,
L1, or L2 by a frozen shape-only analytical-bill plus 100M-per-wrapper-call proxy"
[R] — and idx 69's result kills it by name while preserving the operator underneath:
"Preserve exact L2 as the old non-promoted scored survivor and the call/memory traces;
**kill proxy and block-height retunes**" [R, verbatim]. Deciding G-B with an instrument
the source record explicitly killed would be the same error as reaching for the banned
slope law. It is reported and not used.

That sentence also re-reads the whole G-B premise. What idx 69 killed was **the
ladder** — the per-shape dispatcher and the block-height retunes — not the two-level
formulas. W1.2 names idx 69 as the residual channel's evidence; idx 69 names its own
dispatcher as the thing that must not be replicated. W3.1's cell inherits
`BLOCK_ROWS = 4096` frozen and runs no per-shape ladder, so it inherits none of the
dispatch-count delta that produced idx 69's 0.194269 s.

### 5.5 THE G-B NUMBER

| operator | projected FLOP saving | projected residual increase (λ=1e11) | ratio | verdict |
|---|--:|--:|--:|:-:|
| idx 268 l2-fringe | 15,606,373,342 | 10,779,054,736 (Route A) / 5.23–14.80 B (Route B) | 0.69 / 0.34–0.95 | **pass** |
| idx 58/59 fused strict | 2,216,269,776 | 1,530,739,570 (Route A) / 0 (Route B) | 0.69 / 0.00 | **pass** |

**G-B VERDICT: PASS.** On every licensed route, for both operators, the projected
residual increase is strictly below the projected FLOP saving. The gate does not close
the door.

> **VERIFIER OVERRIDE (2026-08-19, §8.3): this verdict is WITHDRAWN and G-B is
> NOT ESTABLISHED.** Route A cannot fire for any input by construction, and Route B's
> scaling denominator is contradicted by idx 69's own recorded call counts. Read §8
> before acting on this section.

### 5.6 Corroboration, OUT-OF-BASIS, reported and not used in the verdict

idx 268's own recorded metrics measure the erosion this gate projects, on this exact
route: `flop_only_ratio 0.914492`, `effective_compute_ratio 0.949914` over 24 nets
[R]. That is a measured cut of 8.5508% in FLOPs surviving as 5.0086% in effective
compute — a **survival fraction of 0.585746 and an erosion of 0.414254** [D], well
under the 1.0 that G-B would need. It agrees in direction and magnitude with Route A's
0.69 and Route B's 0.34–0.95.

The same figure gives the sharpest available check on this whole pass. Carry this
pass's static Kerdock-host ΔFLOP through idx 268's *measured* survival fraction, at
t4's recorded mean C = 178.463e9 [R]:

```
net effective saving = 0.585746 × 15,606,373,342 = 9,141,370,760
projected effective-C ratio = 1 − 9,141,370,760 / 178.463e9 = 0.948777
idx 268's own recorded effective_compute_ratio                = 0.949914
                                                    difference = 0.001137
```

and for the strict operator, with `Δdispatches = 0`:

```
projected effective-C ratio = 1 − 2,216,269,776 / 178.463e9 = 0.987581
idx 59's own measured paired mean-C ratio                    = 0.989313
                                                  difference = 0.001732
```

Two operators, two independent recorded measurements, both reproduced from static
source arithmetic to within 0.2 percentage points, with no estimator run.

**This resolves W3.1's declared observable.** W3.1 states: "The 0.95-vs-0.9893
projection gap is DECLARED as an observable: one of them is mispriced and the run must
say which." Neither is mispriced. They are two different eligibility surfaces of the
same door, and §3.4 measures the difference exactly: the strict fused core reaches
2.216 B FLOPs per net (2–5 mod-4-clean hooks), the mod-4 fringe route reaches
15.606 B (all 28 hooks). The gap is 7.04×, and it is arithmetic, not error.

---

## 6. DOOR STATUS

**OPEN.** G-A PASS and G-B PASS, read mechanically off §3.4 and §5.5. A sealed
`fold_search` cell per the plan's W3.1 sketch becomes fundable.

> **VERIFIER OVERRIDE (2026-08-19, §8): door status is HELD, not OPEN.** G-A survives
> hostile re-derivation unchanged; G-B does not. No cell is fundable on this document
> until §8.3's settling read is done. §8.6 states the exact remaining work.

Three findings the cell spec must carry, because they change W3.1 as written:

1. **Seal on idx 268's l2-fringe route, not idx 59's tar.** W3.1 currently prefers
   "idx 59's frozen seven-file tar … on evidence quality" and treats idx 268 as the
   magnitude option. §3.4 prices them: the strict fused operator's eligible surface on
   the Kerdock host is 1.36% of the matmul lane and projects an effective-C ratio of
   0.9876–0.9962, which **fails or barely grazes** W3.1's own `≤ 0.98` PASS bar
   before the run starts. The fringe route's eligible surface is 9.56% of the lane and
   projects 0.9488–0.9730, inside the PASS band on every route. Sealing the strict
   operator would spend the run on a predictable INCONCLUSIVE.
2. **`BLOCK_ROWS = 4096` must be frozen in the predeclaration and the per-shape
   ladder forbidden by name.** That is the difference between this cell and idx 69,
   in idx 69's own words.
3. **Declare `Δdispatches` as a first-class predeclared output.** The static
   projection is +227.2 matmul calls per net (+30.3%) for the fringe route and 0 for
   the strict route; the run either confirms that or falsifies this pass's G-B.
   **Corrected in §8.5**: +227.2 is measured against the *L1-best* baseline. Against
   the **frozen deployed incumbent** — which is what the cell's paired run actually
   compares to — the projection is **+508.8 calls per net (+67.8%)**. Predeclare the
   frozen-baseline figure, or the run falsifies the wrong number.

---

## 7. Verification, and the risk this document leaves

**Two independent signals per load-bearing claim.**

- **Entrypoint identity** — signal 1: `sha256` computed here on
  `kerdock_v3_estimator.py` = `076d0a5d…0759aacf` [O]; signal 2: three independent
  corpus records name the same fingerprint from two ends — idx 183's `076D0A5D…`,
  T4_REPORT's `076D0A5D…9AACF`, V31_NOTES' `076d0a5d…` [O]. A wrong file could not
  match both ends in three places.
- **Cost-model identity** — signal 1: `owned_batched_candidate_bill(64512,256,256)
  / direct = 0.88015057621222` computed here [O], against idx 264's surviving
  common-evidence constant `r_prod = 0.88015058` [R]; signal 2:
  `grouped_l2 / owned_batched` at `4096×256×256 = 0.8866399221979091` computed here
  [O], against idx 268's recorded `cost_model_route_ratio_4096x256x256 = 0.88664`
  [R]. Independent routes, independent records.
- **Hook shapes and charges** — signal 1: the recorded tape's 140/140 exact match to
  the frozen closed form [R, re-read here]; signal 2: `attack_verify.json`'s
  independent shape reconstruction, `sequences_match: true`, `total_charged` identical
  on repeat [O].
- **Methodology identity** — signal 1: this pass reads idx 264's `d4` aggregate and
  gets `0.08975283928087245 / 0.061210792169057074`, which is the ledger's
  "8.98%/6.12%" [O vs R]; signal 2: the `d1`–`d5` table is present in the same
  artifact, so the `d2` row this pass quotes was computed by the same code path in the
  same run, not reconstructed here.
- **The G-A/G-B conclusion** — signal 1: static ΔFLOP 15,606,373,342 and Δdispatches
  +227.2 computed here from frozen source [O/D]; signal 2: carried through idx 268's
  independently measured survival fraction it reproduces that record's own
  `effective_compute_ratio` to 0.0011, and the strict operator's variant reproduces
  idx 59's measured mean-C ratio to 0.0017 [D vs R]. **Qualified by §8.4**: only the
  fringe leg of this check is discriminating; the strict leg's agreement is an artifact
  of two offsetting differences and is withdrawn as a signal.

**Fresh signal, collected after the last edit to this document** [O]. The two closed
forms were re-typed from the source text into a throwaway script that imports **neither**
campaign cost model, and re-run: `L1(64512,256,256) = 7,427,768,320`,
`L2_blocked(64512,256,256) = 6,587,334,656`, `Δ = 840,433,664`,
`r_prod = 0.88015057621222`, and the independent form equals the recorded tape charge
on **28 of 28** seed-11 hooks. A transcription error in §3.2 or §3.3 could not survive
that. Re-confirmed in the same pass: the entrypoint sha256 is unchanged, and
`experiments/fold_floor_splice` (mtime 2026-08-19T00:35),
`experiments/frame_completion_129` (04:34), `row_blocked_production` (2026-08-07T15:26)
and `cells/` (04:00) all predate this document's 06:01 write, so none was modified;
a repo-wide search for `*.pyc` newer than 2026-08-19 returns nothing.

**Named risks, at their earned level.**

1. **The panel is 5 synthetic He nets, not the public 100.** Every share in §3 is
   [O] on `w256/d32`, seeds 11–15, and [A] as a stand-in for the public-100 shape
   distribution. The active-set trajectory drives `k, n` and therefore the mod-4
   fringe mix. Settling check, named and unrun: replay the same logging subclass over
   the public-100 shapes already recorded in
   `experiments/t4_kerdock_descriptive_rescore/kerdock_v3_official100.json`. Cost:
   one read, zero compute.
2. **The strict operator's eligible share has a CI95 that dips under the bar**
   (7.15%–16.84%). The door survives on the fringe operator, whose CI95 is
   [81.8%, 87.1%], nowhere near it. If the cell is sealed on the strict operator
   against finding 1 above, G-A must be re-read on the public-100 shapes first.
   **Sharpened by §8.2**: under idx 264's own recorded normaliser the strict
   operator's point estimate itself falls under the bar, not merely its CI95 low.
3. **Route B's `A` bracket is [A], not [O].** idx 69's baseline mean billed compute is
   not recorded anywhere this pass read; it is bracketed by two measured levels. The
   verdict does not turn on it — the widest corner still returns "does not fire" — but
   a recorded value would upgrade the bracket to a point.
4. **The blocked-vs-hoisted L2 transform term.** This pass priced the l2 route
   pessimistically, paying the `k×n` transform once per 4096-row block (16 times).
   The frozen one-level operator hoists its right-hand packing out of the row loop by
   construction; if the l2 operator can do the same, the eligible ΔFLOP rises by
   4.7 M FLOPs per hook and the verdict moves further from the bar. The pessimistic
   number is the one reported.
5. **Not verified, and named as such:** the deployed l2-fringe operator source
   (only its cost model was read — the executable operator lives in the Codex clone
   and was not opened); idx 268's 24-net receipts (quoted at [R] from the ledger, not
   re-aggregated here); idx 69's internal dispatch count (bracketed from source
   geometry — **the claim that it is nowhere recorded is retracted in §8.3**); and
   every MI statistic in the authority document, none of which this pass used or
   needed.

**Skipped deliberately, and named as skipped:** no cell was predeclared, no ledger
field was edited, no annotation was attached to idx 194, `experiments/fold_floor_splice`
and `experiments/frame_completion_129` and `cells/` were not read or written,
`row_blocked_production` was not read or written, the 2026-08-19 slope law was not
loaded, and no estimator, harness, FlopScope context or scored row was executed.

---

# 8. HOSTILE VERIFIER ADDENDUM — 2026-08-19T11:20Z

Appended by an independent verification pass. Nothing above §8 was rewritten except
one arithmetic correction and five cross-reference pointers, both sets itemised in
§8.7. Same compliance envelope as the document it audits: zero billed
compute, no harness, no FlopScope, no estimator execution, no cell predeclared, no
seed consumed; every `python` ran `python -B -P` with `PYTHONDONTWRITEBYTECODE=1`
from a scratch directory outside the corpus; the 2026-08-19 slope law was never
loaded. `experiments/fold_floor_splice`, `experiments/frame_completion_129`,
`cells/` and `experiments/row_blocked_production` were neither read nor written.

**Verdict: G-A confirmed. G-B not established. Door status HELD.**

## 8.1 What was re-derived from scratch, and what it returned

The verifier re-typed `direct_cost`, `batched_winograd_core_cost`,
`batched_winograd_l2_core_cost`, the frozen package's `owned_batched_candidate_bill`,
the clone's odd-k `owned_batched_candidate_bill`, the `dual_odd` branch and the mod-4
block of `grouped_l2_candidate_bill` **by hand from the source text**, importing
nothing from the corpus or the clone, and re-ran the whole of §3 over the recorded
5-net tape [O].

Every load-bearing G-A number in §1–§3 and §5.1–§5.5 reproduces **exactly**:

- entrypoint `sha256 076d0a5d81891ddcbb4509dc6e2bff5459d935b5556490a85d98dac60759aacf`;
- 28 deep hooks per net on all five seeds, corroborated three ways — `range(1, depth-3)`
  at `depth = 32` read in `fold3_estimator.py:122`, `n_deep_hooks: 28` in the recorded
  tape, and idx 264's own result text ("28 deep hook products per net, not ~32");
- all 140 recorded hook charges equal the re-typed frozen closed form, 140/140,
  zero mismatches — an independent reproduction of §3.1's tape check that shares no
  code with it;
- every cell of §3.2's 28-row seed-11 table, including both totals
  (ΔL1 11,543,513,583 and ΔL2 15,416,783,746) and all 28 route labels and leaf-shape
  tags;
- `r_prod = 0.88015057621222`, `r_ref = 0.8868524666100517`,
  `grouped_l2/owned @4096×256×256 = 0.8866399221979091`, and the 4,730,880-FLOP
  blocked-minus-hoisted gap of risk 4;
- eligible ΔFLOP 15,606,373,342 (fringe) and 2,216,269,776 (strict); leaf-cleanliness
  splits 2/5/3/4/2 and 26/23/25/24/26; `min core_k = min core_n = 160`;
- the lane structure means, 750.6 matmul calls per net, and all five CI95 pairs
  (see §8.7 — these were challenged and upheld, and the challenge exposed a defect in
  `attack_translate.py` instead);
- **Δdispatches = +227.2 per net** against the L1-best baseline — reproduced
  independently from `call_count` arithmetic, not taken from §5.1;
- every G-B figure in §5.2–§5.5: erosion 0.6906828703703705, Route A 10,779,054,736
  and 1,530,739,570, the Route-B bracket [3,867,874,498, 5,473,609,455], the three
  corners 5,230,839,797 / 8,422,163,310 / 14,804,810,335 and the 94.9% worst corner,
  and Route C's 22,720,000,000.

Ledger quotes were checked verbatim against `headroom/fold_ledger.json` [O]: idx 69's
mechanism and result sentences, idx 59's `mean C ratio .989312617` and tar sha, idx
53's `max child C 222.405357B`, idx 183's `mean C 178.463e9` and sha, idx 194's
`Projected net billed reduction < 15%; promote >= 20%`, idx 264's `r_prod = 0.88015058`
and its `8.98% / 6.12%`, and idx 268's full metrics block. All match. The recorded d2
and d4 aggregates in `attack_translation.json` match §3.5 to every digit printed.

Predeclaration order holds: §2 precedes §3, §4 precedes §5, and the thresholds are
transcribed from `MI_SOLVE_20260819.md` §W1.1/§W1.2 without loosening (§4 tightens
"exceeds" to "≥", which is the conservative direction). No number, constant or method
traceable to `headroom/slope_cost_model.py` or `SLOPE_COST_MODEL_20260819.*` appears
anywhere in the document; the banned instrument is named only in the compliance and
ban clauses.

## 8.2 G-A stands — and §3.5 understates one reading against the strict operator

**The G-A verdict is confirmed for the door.** The magnitude operator clears the 9%
bar under every normaliser the verifier could construct: 84.45% under §2's predeclared
`r_ref`, **42.65%** under idx 264's own recorded `r_d(d=2) = 0.7759509054763458`, and
9.56% unnormalised. The door does not close on G-A.

**But §3.5 is wrong about its own strict operator.** §3.5 argues that idx 264's
recorded 6.36% "is the eligibility of a *different operator*", because C1-STRICT
recurses only hooks with `4 | m, k, n` — 2–5 of 28. That is correct against the
*fringe* leg and false against the *strict* leg, which reaches exactly the same hooks.
Two signals [O/D]:

- idx 264's recorded `eligible_calls_strict` at d=2 is **[2, 5, 3, 4, 2]** across seeds
  11–15 — element for element the same as this document's `winograd_l2_grouped` exact
  counts in §3.6.
- Re-pricing this document's own strict eligibility surface with idx 264's recorded
  `r_d(d=2)` gives **6.058%**, against idx 264's recorded 6.3615% — 4.8% relative
  agreement, from two independent cost models.

So the row §3.5 labels "close" is measuring the door's strict operator, at the same
scale, and it closes it. The missing sensitivity row, stated here:

| reading | fringe | strict | strict would |
|---|--:|--:|---|
| §2 predeclared `r_ref = 0.88685` | 84.45% | 11.995% | pass |
| idx 264's recorded `r_d(d=2) = 0.77595`, same surfaces | 42.65% | **6.058%** | **close** |
| unnormalised saving / matmul lane | 9.555% | 1.357% | close |

The choice of `r_ref` was predeclared in §2 before any number appeared, and it is the
more coherent normaliser — its numerator and denominator share the one-level baseline,
where idx 264's do not. G-A therefore stands as ruled. What does not stand is the
document's presentation of the strict operator as a PASS: under the authority's own
words ("use idx 264's measured methodology") that operator's point estimate is under
the bar, not merely its CI95 lower end. §6 finding 1 already recommends against sealing
it; this makes that recommendation binding rather than advisory.

## 8.3 G-B is not established — the two licensed routes carry no discriminating weight

**Route A returns the same answer for every input it could ever be given.** It computes
`Δ(λR) = erosion × ΔFLOP` with `erosion = 0.6907 < 1`, so `Δ(λR) < ΔFLOP` identically,
for any operator and any ΔFLOP. A test whose output is fixed before its input is read
is not evidence, and §5.2 does not disclose this. Both of its rows would read exactly
the same if the eligibility surface were wrong by any factor.

**Route B's scaling denominator is contradicted by idx 69's own record.** §5.3 divides
idx 69's absolute residual by `Δdispatches₆₉ ∈ [84, 168]`, inferred from block
geometry (8192-row → 6144-row on `m = 64512`), and §7 risk 5 states that idx 69's
internal dispatch count is "never recorded". Both are wrong [O,
`headroom/fold_ledger.json` candidates[69], and `graph/graph.json`
`candidate::residual_aware_l2_dispatch_ladder`]:

- idx 69's **kill condition** is "…or **failure to reduce calls** on every frozen
  generated target", and its graph-node prediction reads "A changed dispatcher
  reduces … core calls on every generated target". Its mechanism prices calls at
  100M each precisely so the dispatcher will *avoid* them. It was a call-**reducing**
  experiment.
- Its result records the counts: "**core calls are 150/150 then 191/194**". Whatever
  the pairing, the magnitude of the change is at most 3 on a base of 150–194. It is
  not +84 to +168.

Consequences. idx 69's 0.194269 s residual cannot be attributed to a dispatch-count
increase, so §5.4's sentence "the dispatch-count delta that produced idx 69's
0.194269 s" is unsupported; the residual it measured belongs to the per-shape Python
dispatcher, the block-height retune and the alias-liveness billing change that idx 69
names. Scaling that number by `227.2 / Δ₆₉` is therefore not licensed at all — and if
one insists on the recorded `Δ₆₉ ≤ 3`, the scale factor exceeds 75 and Route B fires
by more than an order of magnitude, which is itself the reductio.

**Route C's disqualification is sound but its ground is answered elsewhere in the
corpus.** §5.4 rejects the 100M-per-call proxy because "the proxy is not a
measurement". The campaign holds a measurement of the same law, which this document
does not read and which `MI_SOLVE_20260819.md`'s own addendum flags as unpriced
(idx 250 `gm_m116_streams`: "Dispatches fell 512 to 160 and residual 0.933445 to
0.419197 s, confirming call-count domination a third time"). That is
**1.4609e-3 s per dispatch = 1.4609e8 FLOP-equivalents at λ = 1e11** [D] — 1.46× the
proxy idx 69 guessed. At +227.2 dispatches it projects 3.32e10, and at the
frozen-baseline +508.8 of §8.5 it projects 7.43e10, against a 1.5606e10 FLOP saving.
**It fires by 2.1× to 4.8×.** It is out of the authority's declared basis and does not
decide the gate; it does dispose of the reason §5.4 gave for setting the proxy aside.

**Net.** On the licensed basis G-B has one route whose verdict is independent of every
number in the document and one route whose denominator the source record contradicts.
The correct output is `G-B: NOT ESTABLISHED`, not `G-B: PASS`.

## 8.4 What actually supports the substantive conclusion — and it is in §5.6

The strongest evidence in the document that the residual increase does *not* swallow
the FLOP saving is the one thing §5.6 files as out-of-basis: idx 268's recorded
`effective_compute_ratio 0.949914 < 1` over 24 nets. Effective compute fell. Had the
residual increase exceeded the FLOP saving on this exact operator, that ratio would
have exceeded 1. Measured erosion is 41.4%, comfortably under the 100% the gate needs.

The verifier reproduces §5.6's fringe arithmetic and endorses it as a real check, with
one deflation: carried through idx 268's survival fraction the comparison reduces
algebraically to "this pass's `ΔFLOP / C = 8.745%` against idx 268's measured FLOP cut
`8.551%`", a **2.27% relative** agreement, not the 0.0011 absolute the text implies.

The **strict** leg of the same check is withdrawn. §5.6 projects the strict operator
at zero erosion (0.987581) and compares it to idx 59's measured 0.989313, which was
produced at 69% erosion from an analytical cut of 3.456% — where this pass's strict cut
is 1.242%, a factor of 2.78 apart. Two offsetting differences land the ratios near each
other. §7's "a wrong eligibility surface could not land on both recorded ratios" is
therefore true of the fringe leg and false of the strict leg.

## 8.5 The declared observable is stated against the wrong baseline

§5.1's +227.2 is `Δcalls` against **each operator's own one-level baseline** — correct
as written and independently reproduced. §6 finding 3 then declares it as the run's
predicted output. The run compares against the **frozen deployed incumbent**, which
dispatches *direct* (one call per block) on every odd-`k` hook where the L1-best route
would dispatch two or three. Recomputed here per net, seeds 11–15 [O/D]:

| baseline | Δcalls per net | as % of the frozen 750.6 |
|---|--:|--:|
| L1-best (§5.1 as written) | +227.2 | +30.3% |
| **frozen deployed incumbent (what the cell will measure)** | **+508.8** | **+67.8%** |

Per seed the frozen-baseline deltas are +624 / +432 / +448 / +464 / +576. Predeclaring
+30.3% would be falsified by a correct run, for a reason that has nothing to do with
the mechanism under test. This also more than doubles every dispatch-driven residual
projection in §8.3.

## 8.6 What would settle it — named, cheap, and unrun

1. **Read idx 69's call counts to a decision.** Recover which of "150/150" and
   "191/194" is parent and which is child. One read of idx 69's artifacts. Until then
   Route B has no denominator.
2. **Re-anchor the projection on a measured call-count law**, not a proxy: idx 250's
   1.4609e8 FLOP-equivalents per dispatch, or a fresh per-dispatch measurement on this
   host. Then re-run G-B on the §8.5 baseline. This requires the authority to widen
   W1.2's declared basis, which is an owner call, not a verifier's.
3. **Replay the logging subclass over the public-100 shapes** already recorded in
   `experiments/t4_kerdock_descriptive_rescore/kerdock_v3_official100.json` — the
   settling check §7 risk 1 already names. One read, zero compute. It also settles
   §8.2, since the mod-4 fringe mix drives both.

Until 1 and 2 land, **no `fold_search` cell should be predeclared on this document.**
G-A is banked and does not need redoing.

## 8.7 Every change this addendum made above §8

**One** arithmetic correction and five pointers. Nothing else in §0–§7 was touched.

| § | was | now | why |
|---|---|---|---|
| 5.6 | `0.585746 × 15,606,373,342 = 9,142,213,504`; ratio `0.948772`; difference `0.001142` | `9,141,370,760`; `0.948777`; `0.001137` | the printed product used a 4-significant-figure survival (0.5858 exactly reproduces 9,142,213,504) while the printed factor is 0.585746; the line is now self-consistent. The ratio also mis-rounded — `1 − 9,142,213,504/178.463e9` is 0.948772**5**, i.e. 0.948773. Nothing downstream moves. |

Pointers added, no text deleted: §5.5 verdict override, §6 door-status override,
§6 finding 3 baseline correction, §7 risk 2 sharpening, §7 risk 5 retraction, and the
§7 qualification of the two-signal claim on the G-A/G-B conclusion.

**The five CI95 pairs were challenged and the document won.** An earlier draft of this
addendum "corrected" them to `[0.98801662, 0.99022379]`, `[0.91235069, 0.95820547]`,
`[0.00146896, 0.00174054]`, `[0.81457088, 0.87440578]` and `[0.06443490, 0.17547107]`,
on the strength of a recompute that agreed with the recorded
`attack_translation.json`. That agreement was not a second signal: the recompute had
copied `attack_translate.py`'s own `ci95` helper, so both readings shared one defect.
Recomputed with an independently chosen critical value, the document's five pairs are
right and the edit was reverted. The incidental finding belongs to the campaign's
tooling, not to this document:

> **`attack_translate.py:53` has an off-by-one in its t-table lookup.** The table
> `{2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571}` keys `t(df = key − 1)`, and the
> helper indexes it at `.get(n - 1)`, returning `t(df = n − 2)`. At `n = 5` it fetches
> 3.182 where the two-sided 95% value for `df = 4` is 2.776, so **every CI95 in
> `attack_translation.json` is one degree of freedom too wide**, by the factor
> 2.776/3.182 = 0.8724. The point estimates and every `mean` field are unaffected, and
> no verdict anywhere in the campaign turns on an interval width — idx 264's headline
> pair 8.98%/6.12% and its d2 row are means. Correct the helper before any future gate
> reads an interval edge.

## 8.8 Verifier's own compliance evidence

- Fence mtimes, read fresh after the last edit above [O]:
  `experiments/fold_floor_splice` 2026-08-19T00:35:42, `experiments/frame_completion_129`
  2026-08-19T04:34:40, `cells/` 2026-08-19T04:00:17,
  `experiments/row_blocked_production` 2026-08-07T15:26:47 — all unchanged from the
  values §7 recorded, all predating this pass.
- `find . -name "*.pyc" -newermt 2026-08-19` over the whole corpus returns nothing [O].
- Files read by this pass, all read-only: the frozen `package_source/` sources, the
  l2-fringe `cost_model.py` in the Codex clone, `experiments/uf1_attack_eligibility/*`,
  `headroom/fold_ledger.json`, `graph/graph.json`, and `core/MI_SOLVE_20260819.md`.
- **Not verified by this pass, and named as such:** idx 268's 24-net receipts and idx
  250's residual numbers are carried at [R] from the ledger, not re-aggregated; the
  deployed l2-fringe executable was not opened, only its cost model; the pairing inside
  idx 69's "150/150 then 191/194" is unresolved and is §8.6 item 1; and the 5-net panel
  remains a stand-in for the public 100, exactly as §7 risk 1 states.

---

# 9. SETTLEMENT PASS — 2026-08-19T11:49Z

Appended by a third pass commissioned to discharge §8.6 items 1 and 2 and to correct
the defect §8.7 discovered in the campaign's tooling. **Append-only: this pass edited
nothing in §0–§8.** Where §9 supersedes an earlier verdict it says so here; no pointer
was inserted above. A reader who stops at §6 sees `HELD, not OPEN`, which errs on the
conservative side of §9.4's `CLOSED`, so the missing pointer cannot license a cell.

**Verdict, up front: G-B FIRES on the fringe operator at the baseline a real run would
face. Both legs of the merged door are now closed — the strict leg on G-A (§8.2), the
fringe leg on G-B (§9.2). Door status: CLOSED. §9.4 files the closure.**

## 9.0 Compliance, basis, and the D-labels

**Zero billed compute.** No harness, no FlopScope, no estimator execution, no scored
row, no cell predeclared, no seed consumed. Every `python` invocation ran `python -B -P`
with `PYTHONDONTWRITEBYTECODE=1` from a scratch directory outside the corpus. The
2026-08-19 slope law (`headroom/slope_cost_model.py`, `SLOPE_COST_MODEL_20260819.*`)
was not loaded, not imported, and no number below derives from it; it is named only in
this ban clause.

**Fences.** `experiments/fold_floor_splice`, `experiments/frame_completion_129`,
`cells/` and `experiments/row_blocked_production` were **not written**; their mtimes,
read after this pass's last edit [O], are `2026-08-19T00:35:42`, `2026-08-19T04:34:40`,
`2026-08-19T04:00:17` and `2026-08-07T15:26:47` — identical to the values §7 and §8.8
recorded. `find . -name "*.pyc" -newermt 2026-08-19` over the whole corpus returns
nothing [O]. **One read disclosure:** a corpus-wide
`grep -rn "core calls\|core_calls"` returned matching lines from
`experiments/fold_floor_splice/candidate_source/row_blocked_winograd.py` and
`experiments/frame_completion_129/arm{A,B,C}/row_blocked_winograd.py`. Those lines
appeared in a search result; no fenced file was opened and none was written. The
operator source this pass actually read is the unfenced frozen copy at
`experiments/v31_guards/package_source/row_blocked_winograd.py`.

**Files modified by this pass.** This document (§9 appended) and
`experiments/uf1_attack_eligibility/attack_translate.py` (§9.3, +11 lines: seven lines
of comment, one changed token, one three-line assertion; 293 → 304 lines [O]). **No
recorded artifact was regenerated:** `attack_translation.json` mtime is
`2026-08-10T21:39:38`, unchanged [O].

**Evidence tags** carry §0's meanings: **[O]** observed here, **[D]** derived here by
shown arithmetic, **[R]** reported by a record and not re-derived, **[A]** an
assumption named as such.

**The D-labels.** §8 carries no `D` numbering. The directive that commissioned this
section uses four labels, which map onto §8 as follows, and every use below cites the
subsection rather than the label so no inference rests on a definition outside this
document:

| label | §8 location | content |
|---|---|---|
| **D1** | §8.3 ¶1 | Route A is a tautology — `erosion × ΔFLOP < ΔFLOP` for every input |
| **D5** | §8.5 | the declared observable is stated against the wrong baseline; frozen-baseline Δcalls is +508.8/net, not +227.2 |
| **D6** | §8.2 | under idx 264's own recorded normaliser the **strict** operator's G-A point estimate is 6.058%, under the 9% bar |
| **D9** | §8.7 | `attack_translate.py` t-table off-by-one; every recorded CI95 is one df too wide |

---

## 9.1 §8.6 ITEM 1 — THE idx-69 PAIRING, SETTLED

### 9.1.1 The complete committed trail

`headroom/fold_ledger.json` `candidates[69]`, read here in full [O]:

- `id`: `residual_aware_l2_dispatch_ladder`; `status`: `killed`.
- `mechanism`: "Retain the exact fused L2 formulas but choose direct, L1, or L2 by a
  frozen shape-only analytical-bill plus100M-per-wrapper-call proxy, then recurse
  through larger-block and alias-liveness variants."
- `kill_condition`: "Any billing/parity/hash/memory failure, effective ratio above.980,
  residual above.170s, or failure to reduce calls on every frozen generated target."
- `prediction`: "A changed dispatcher reduces mean analytical work to at most.975 of
  L1, mean effective C to at most.980, residual to at most.170s, core calls on every
  generated target, and stays below512MiB with exact billing/parity."
- `result`: "Kill the ladder and do not replicate. The final6144 call-penalized child
  passes exact bills, static safety, micro/depth/full parity, hashes, and memory, but
  analytical ratio.965263 becomes effective ratio.989874; mean residual is.194269s,
  peaks503.324/510.926MiB, and core calls are150/150 then191/194. Exact8192 and7168
  variants reach effective.977468/.971401 but fail residual and memory; alias-liveness
  changes FlopScope billing. Preserve exact L2 as the old non-promoted scored survivor
  and the call/memory traces; kill proxy and block-height retunes. No new score row was
  read."

**The record points to no artifact, and no artifact exists in this corpus.** A
corpus-wide search for `150/150`, `191/194`, `503.324`, `510.926`, `7168` and
`residual.aware` returns exactly four carriers of the sentence — `fold_ledger.json`
`candidates[69]`, `headroom/GEN6_FAILURE_SALVAGE_ATLAS_20260809.json` index 69 (which
files the same clause under `passed_tissue`), `graph/graph.json` node
`candidate::residual_aware_l2_dispatch_ladder` (prediction and kill condition only, no
counts), and `headroom/mi_graph/mi_graph.json` — plus the three prose documents that
quote it (`HANDOFF_CODEX_SOL_20260808.md:373`, `MI_SOLVE_20260819.md:384`, and this
file). There is no idx-69 experiment directory, no call trace, no memory trace [O].

**Therefore §8.6 item 1 as written cannot be discharged: "one read of idx 69's
artifacts" has nothing to read.** The pairing is settled below from the record's own
internal arithmetic against an independent measured record, at **[D]**, not **[O]**.

### 9.1.2 The two admissible readings

The sentence uses a slash for a pair and "then" for a sequence, and the same result
sentence uses both idioms elsewhere ("peaks503.324/510.926MiB";
"Exact8192 and7168 variants reach effective.977468/.971401", where the slash order
follows the naming order). Two readings survive:

| reading | slash means | "then" means | Δcalls per target | Δcalls per net |
|---|---|---|---|--:|
| **A** | parent / child, within one target | the second target | 150→150 (0) and 191→194 (+3) | +1.5 |
| **B** | target 1 / target 2, within one arm | parent arm, then child arm | 150→191 (+41) and 150→194 (+44) | +42.5 |

Both fail the kill condition's call clause ("failure to reduce calls on every frozen
generated target"), which is why the record reports them inside its `but` clause.
Neither is +84 to +168, the bracket §5.3 inferred from block geometry — that bracket
is void under either reading, exactly as §8.3 states.

### 9.1.3 The discriminator — idx 250's measured per-dispatch laws

§5.3's algebraic conversion of idx 69's ratios into an absolute residual delta gives
`D ∈ [3,867,874,498 , 5,473,609,455]` FLOP-equivalents (reproduced exactly by the
verifier, §8.1). Dividing by each reading's Δcalls gives an implied per-dispatch cost,
which can be compared with the two per-dispatch laws the campaign has actually
measured (§9.2.2 defines both) [D]:

| reading | Δcalls/net | implied FLOP-eq per dispatch | × idx 250 host law | × campaign law |
|---|--:|---|--:|--:|
| **A** (mean +1.5) | 1.5 | 2,578,582,999 … 3,649,072,970 | 17.65 … 24.98 | 46.81 … 66.24 |
| **A** (max per-net +3) | 3 | 1,289,291,499 … 1,824,536,485 | 8.83 … 12.49 | 23.40 … 33.12 |
| **B** (mean +42.5) | 42.5 | 91,008,812 … 128,790,811 | **0.62 … 0.88** | 1.65 … 2.34 |

Reading B lands inside a factor 1.6 of a law measured independently on this host at
the same `m = 64,512`, `BLOCK_ROWS = 4,096`, depth-32 fixture. Reading A demands a
per-dispatch cost 8.8× to 66× every measured law in the corpus. A second, weaker
signal points the same way: **191 is prime**, so under reading A the second target's
parent count factors as (blocks per product) × (products) only as `1 × 191` or
`191 × 1` — the first makes the 8192-row blocking inert (one block covers the whole
matrix), the second is absurd. Under reading B the parent's 150 factors ordinarily at
any campaign block height (`3 × 50`, `2 × 75`).

**Settlement: reading B.** `150/150` is the **parent** on the two frozen generated
targets; `191/194` is the **child** on the same two targets, in the same order.
Δcalls = +41 and +44, per-net mean **+42.5** [D].

**Named caveat, at its earned level.** Reading A is not impossible: it survives if the
first target's row count `m` happens to sit in a band where
`ceil(m/8192) = ceil(m/6144)` (for example `m ∈ [8193, 12288]`), which makes every
L1→L2 conversion call-neutral there. No target row count is recorded anywhere, so this
cannot be closed by reading. The settlement is **[D]** on a cross-record consistency
argument, and §9.1.7 shows the gate does not depend on it.

### 9.1.4 Which arm is parent, which is child, and what geometry each ran

- **Parent (baseline arm).** The promoted fixed-**8192**-row L1 champion — idx 53
  `row_blocked_winograd_production`, "Port the exact fixed8192-row Winograd survivor
  into an immutable descendant of random32,256 fold3" [O, `candidates[53].mechanism`].
  idx 69's own prediction is written against it: "reduces mean analytical work to at
  most .975 of **L1**".
- **Child (candidate arm).** The final **6144**-row call-penalized rung of the ladder,
  after the 8192 and 7168 rungs failed residual and memory. The 6144 block height is
  the same one idx 58 composes ("the champion's fixed8192-row L1 fallback with a
  fixed6144-row fully fused two-level Winograd operator") [O, `candidates[58]`].
- **Geometry: NOT the Kerdock host.** `MI_SOLVE_20260819.md` states the composition
  check verbatim: "Composition verified unwalked: records naming '6144' =
  {58, 59, 69, 275}; records naming 'kerdock' = 41; intersection = 0" [O,
  `MI_SOLVE_20260819.md:370–371`]. idx 69 ran on the random32256 / row-blocked Haar
  lineage, on two frozen generated targets whose row counts are nowhere recorded.
  **§5.3's premise — "idx 69 ran on the same 64,512-row / 28-hook / depth-32
  geometry" — is unsupported and is withdrawn here.** It was the load-bearing
  assumption behind the `[84, 168]` bracket.

### 9.1.5 The honest per-dispatch attribution of the 0.194269 s residual: UNDEFINED

Three independent reasons, any one sufficient [O/D]:

1. **The numerator does not exist.** `0.194269 s` is a **level**, not a delta: the
   child's mean residual measured against an **absolute** gate. The kill condition
   reads "residual above.170s" [O], and the kill-context index confirms the reading —
   "RESIDUAL WALL-TIME ALONE KILLED IDX 117 (.6105 s), 118 (.3285 s), 69 (.194269 s)
   against a .170 s gate" [O, `KILL_CONTEXT_INDEX_20260819.md:30`]. No parent residual
   is recorded for idx 69 anywhere in the corpus. The only Δ available is §5.3's
   algebraic `D`, whose `A` bracket §7 risk 3 already labels **[A]**, not **[O]**.
2. **The denominator is unresolved and is zero somewhere.** +42.5 per net on the
   settled reading, +1.5 on the surviving alternative, and exactly 0 on at least one
   target under that alternative.
3. **The quotient is either impossible or redundant.** §9.1.3's table: 8.8×–66× every
   measured law, or inside a band the campaign already measures directly, at a lower
   variance, on the right geometry.

**There is no honest per-dispatch attribution of idx 69's residual.** The closest
defensible statement is the settled reading's `9.10e7 … 1.29e8 FLOP-eq/dispatch`, and
that number's only merit is that it agrees with idx 250 — which is to say idx 69 tells
the residual channel nothing idx 250 does not tell it better.

### 9.1.6 Can the residual be attributed to dispatch-count change at all? **No.**

**The record falsifies the dispatch-count story internally, and the falsifier is
invariant to the pairing.** `core_calls = ceil(m / BLOCK_ROWS)` — one batched `matmul`
per row block, incremented inside `for start in range(0, m, self.block_rows)`, with
`last_total_matmul_calls = core_calls * (1 + int(nc < n))` [O,
`experiments/v31_guards/package_source/row_blocked_winograd.py:71–72, 120–150,
167–168`]. At fixed `m`, a **larger** block height issues **fewer** core calls. So the
8192 and 7168 rungs each issue strictly fewer core calls than the 6144 child. The
record: "Exact8192 and7168 variants reach effective.977468/.971401 but **fail residual
and memory**" [O, verbatim]. Residual failed at every rung of the ladder, including
the two rungs with the fewest dispatches. **A quantity that fails identically when the
call count is reduced is not a function of the call count.**

**What the residual IS attributable to, in the record's own words:**

1. **The per-shape dispatcher.** "choose direct, L1, or L2 by a frozen shape-only
   analytical-bill plus100M-per-wrapper-call proxy" — Python decision work evaluated
   per product, on every product, on both arms' targets. The record kills it by name:
   "**kill proxy**".
2. **The block-height retunes.** The 8192 / 7168 / 6144 ladder itself, killed by name
   in the same clause: "**and block-height retunes**". The memory evidence points the
   same way — peaks 503.324 / 510.926 MiB against a 512 MiB gate, and the two
   larger-block rungs failing *memory* as well as residual.
3. **The billing instrument moving under the measurement.** "alias-liveness changes
   FlopScope billing" [O]. MI_SOLVE's own read of this record flags it as the one
   unpriced clause: "a billing-instrument dependency on ownership, i.e. the W0.4 axis
   contaminating the cost axis" [O, `MI_SOLVE_20260819.md` idx-69 entry].

What the record preserves is not a residual law: "Preserve exact L2 as the old
non-promoted scored survivor and **the call/memory traces**". It preserves the traces
and kills the two mechanisms that produced the wall.

### 9.1.7 What the settlement licenses for G-B: **nothing**

Route B is retired. Not because it returns the wrong sign — under **both** readings
and **both** Kerdock baselines it fires, as the arithmetic below shows — but because
its numerator is a level, its denominator is unrecorded, and its host is a different
carrier lineage [D]:

| reading | scale `227.2 / Δ₆₉` | projected Δ(λR) | vs ΔFLOP 15,606,373,342 | scale `508.8 / Δ₆₉` | vs ΔFLOP |
|---|--:|---|--:|--:|--:|
| A (Δ = 1.5) | 151.47 | 5.86e11 … 8.29e11 | 37.5× … 53.1× | 339.20 | 84× … 119× |
| B (Δ = 42.5) | 5.346 | 2.07e10 … 2.93e10 | 1.32× … 1.87× | 11.972 | 2.97× … 4.20× |

§5.3's "does not fire" rested entirely on the `[84, 168]` denominator, and that
denominator came from a geometry idx 69 did not run. **Route B is neither a PASS
instrument nor a FIRE instrument; it is not an instrument, and §5.3 is void.** Nothing
below uses it.

---

## 9.2 §8.6 ITEM 2 — G-B RE-RUN ON THE HONEST BASIS

### 9.2.1 PREDECLARATION (written before any number in this section)

**G-B threshold, transcribed unchanged from §4.1, which itself tightened `MI_SOLVE`
§W1.2's "exceeds" to "≥" in the conservative direction:**

> `projected residual increase ≥ projected FLOP saving`, both in FLOP-equivalents at
> `λ = 1e11` (1 s of residual = 1e11 FLOPs) → the door **CLOSES** on G-B. Otherwise
> G-B passes.

**Projected FLOP saving.** §3.4's eligible ΔFLOP, per operator, per net — unchanged,
so G-A and G-B still price the same object: **fringe 15,606,373,342**,
**strict 2,216,269,776** [R §3.4, reproduced exactly by the verifier at §8.1]. Seed 11
alone: fringe **15,416,783,746** [O, §3.2's ΔFLOP-L2 column re-summed here from the
28 printed rows — the sum reproduces the printed total exactly, which is this pass's
transcription check].

**Basis widening, recorded as the owner call §8.6 item 2 asked for.** §8.6 item 2
states that re-anchoring the projection on a measured call-count law "requires the
authority to widen W1.2's declared basis, which is an owner call, not a verifier's."
**The owner made that call in the directive commissioning this section** [R, directive
2026-08-19]. W1.2's declared basis is widened to admit measured per-dispatch
call-count laws. idx 69 remains nominally in the basis and, per §9.1.7, carries zero
weight. The 2026-08-19 slope law remains banned.

**Licensed instruments, named before use:**

- **(a)** idx 250 `gm_m116_streams`, the **host law** [O, `candidates[250].result`].
- **(b)** the **campaign law**, stated and verified verbatim inside that same record
  [O, same field].
- **(c)** the dispatch deltas: §5.1's own-baseline **+227.2/net**, and §8.5's (D5)
  frozen-baseline **+508.8/net** mean, per-seed **+624 / +432 / +448 / +464 / +576**
  over seeds 11–15.
- **(d)** idx 69 — licenses nothing (§9.1.7).

**Excluded, and why, before the numbers:** Route A (§5.2) is excluded by D1 — it
computes `erosion × ΔFLOP` with `erosion = 0.6907 < 1`, so its answer is fixed before
its input is read, and both of its rows would be identical if the eligibility surface
were wrong by any factor. Route C's `100M`-per-call proxy is excluded by idx 69's own
verdict (§5.4) and is in any case superseded by (a) and (b), which **measure** the
same law rather than guessing it.

### 9.2.2 The two measured laws

| law | source, verbatim | s per dispatch | FLOP-eq per dispatch at λ=1e11 |
|---|---|--:|--:|
| **host law** (idx 250) | "Dispatches fell 512 -> 160 (3.200x) and residual fell 0.933445 -> 0.419197 s (2.227x), confirming call-count domination a third time on new conditions" [O] | `0.514248/352 = 1.4609318e-3` | **146,093,181.8** |
| **campaign law** (m116b/m116c anchors, verified inside the same record) | "ledger anchors verified verbatim: m116b 0.6105131132 s at 1024 calls, m116c 0.3284645767 s at 512 calls; slope 5.508760478e-4, intercept 4.641604e-2" [O] | `0.2820485365/512 = 5.5087605e-4` | **55,087,604.8** |

Intercept re-derived here as a check: `0.3284645767 − 512 × 5.5087605e-4 =
0.0464160402`, against the record's `4.641604e-2` [D vs O]. The anchors are themselves
ledger-recorded residuals — idx 117 (.6105 s) and idx 118 (.3285 s) [O,
`KILL_CONTEXT_INDEX_20260819.md:30`].

**The two laws differ by 2.652×, and the record says why.** idx 250's status is
`BLOCKED_ESCALATE`; its own residual *gate* was declared NOT MEASURABLE because the
control arm ran 2.84× slow under host contention, and its record fits the slope on its
own arms at "1.461e-3 s/call (2.65x campaign)" and attributes the gap to contention
[O]. Only the residual **gate** was unmeasurable; the **paired** 512→160 dispatch and
0.933445→0.419197 s residual are both arms of one within-session comparison, which is
exactly what a slope needs and what contention inflates on both sides. So the host law
is an **upper** anchor and the campaign law a **lower** anchor. G-B is decided against
**both**, as a bracket, not a point.

### 9.2.3 THE G-B NUMBER — idx 268 l2-fringe operator

_(first appearance of any G-B result in this section; §9.2.1 precedes it)_

**Own (L1-best) baseline, +227.2/net — for the record only, not the baseline a run
faces** [D]:

| law | projected Δ(λR) | ΔFLOP | ratio | fires? |
|---|--:|--:|--:|:-:|
| host law | 33,192,370,909 | 15,606,373,342 | 2.1268 | **yes** |
| campaign law | 12,515,903,807 | 15,606,373,342 | 0.8020 | no |

The bracket straddles 1.0, so at the own baseline **G-B is NOT ESTABLISHED** in either
direction. This is the honest own-baseline record.

**Frozen deployed baseline, +508.8/net — the one a real run would face (D5)** [D]:

| law | projected Δ(λR) | ΔFLOP | ratio | fires? |
|---|--:|--:|--:|:-:|
| host law | 74,332,210,909 | 15,606,373,342 | 4.7629 | **yes** |
| **campaign law (conservative anchor)** | **28,028,573,315** | 15,606,373,342 | **1.7960** | **yes** |

Both ends of the bracket fire. **Per seed, at the conservative campaign law**, using
§8.5's recorded per-seed frozen-baseline deltas [D]:

| seed | Δcalls (frozen baseline) | projected Δ(λR), campaign law | ΔFLOP used | ratio | fires? |
|--:|--:|--:|--:|--:|:-:|
| 11 | +624 | 34,374,665,386 | 15,416,783,746 (seed-11 exact) | 2.2297 | yes |
| 12 | +432 | 23,797,845,267 | 15,606,373,342 (mean) | 1.5249 | yes |
| 13 | +448 | 24,679,246,944 | 15,606,373,342 (mean) | 1.5814 | yes |
| 14 | +464 | 25,560,648,620 | 15,606,373,342 (mean) | 1.6378 | yes |
| 15 | +576 | 31,730,460,356 | 15,606,373,342 (mean) | 2.0332 | yes |

Under the host law the same five seeds give 5.9132 / 4.0440 / 4.1938 / 4.3436 / 5.3920.
**The gate fires on 5 of 5 seeds under the weaker of the two measured laws, with a
worst-seed margin of 1.52×.** Only seed 11's ΔFLOP is printed per-seed in §3.2, so
seeds 12–15 are tested against the 5-net mean; for the verdict to flip at the
least-favourable seed the per-net eligible ΔFLOP would have to exceed 23.80e9, i.e.
1.52× the 5-net mean and 1.54× the seed-11 total — impossible, since the whole
eligible column is bounded by §3.2's construction and varies by well under 10% across
the panel.

**G-B verdict, fringe operator: FIRES. The door closes on G-B for the fringe leg.**

> **VERIFIER OVERRIDE (2026-08-19, §10.2): this verdict is WITHDRAWN.** Both tables
> above divide a **frozen-deployed-baseline** dispatch delta by an **L1-best-baseline**
> FLOP saving. The saving that +508.8 calls actually buys is `frozen − L2 =
> ΔL1 + ΔL2 = 26,960,297,329` on seed 11, not `ΔL2 = 15,416,783,746`. Baseline-matched,
> seed 11 at the campaign law is **1.2750×**, not the 2.2297× printed above. Read §10
> before acting on this section.

### 9.2.4 The strict operator — what actually establishes its zero

§5.1 records `Δdispatches = 0` for idx 58/59's fused strict operator, "by
construction". D1's tautology does not apply: Route A is not the instrument here, and
a zero delta is not the output of an erosion constant. What **does** establish it, and
what does not:

**What establishes it** [O/D]:

1. **Source arithmetic.** `core_calls` increments once per row block inside
   `for start in range(0, m, self.block_rows)`, and the tail predicate is
   `1 + int(nc < n)` [O, `row_blocked_winograd.py:120–150, 167–168`]. The strict fused
   operator substitutes one 49-leaf batched `matmul` for the one 7-leaf batched
   `matmul` at line 149, inside the same loop, at the same block height. Neither `m`,
   nor `block_rows`, nor `nc < n` changes. Call count is 1 per block before and after.
2. **D5's baseline defect cannot bite on this operator's eligible surface.** The
   strict operator's surface is exactly the mod-4-clean hooks (`4|k` and `4|n`). Over
   §3.2's 28 seed-11 rows, re-checked here row by row: **`m71 cov = yes` ⇔ `k` even, on
   28 of 28** [O/D]; and `4|k ⇒ k` even, so **every mod-4-clean hook is necessarily a
   hook the frozen deployed operator already routes through the same row-blocked
   Winograd loop.** Seed 11's clean set is `{hook 1 (256,256), hook 6 (248,244)}`, both
   `cov = yes`, count 2 — matching §3.6's `2/5/3/4/2` first entry, and their ΔFLOP-L2
   sum is 1,613,281,992 [O/D]. On the eligible surface the frozen-deployed baseline and
   the L1-best baseline are therefore the **same route**, and the substitution is
   block-for-block against both.

**What does not establish it, and is not settled here.** §3.4 describes the operator as
"49-leaf core, **L1 fallback elsewhere**". If "L1 fallback" means the **frozen deployed**
one-level route on the other 23–26 hooks, `Δdispatches = 0` exactly and the projected
residual increase is `0 < 2,216,269,776`. If it means **L1-best** (the cheapest
one-level route, including the odd-k and dual-odd branches the frozen operator does not
take), then against the frozen incumbent the operator carries the same call gap the
fringe route does — `508.8 − 227.2 = +281.6` calls per net [D from §8.5's two rows;
corroborated by the seed-11 hand count, 17 odd-`k` hooks × `ceil(64512/4096) = 16`
blocks = 272] — and G-B fires by **6.999×** (campaign law, 15,512,669,508) to
**18.563×** (host law, 41,139,840,000) against 2,216,269,776. **Settling check, named
and unrun: read the fallback clause in idx 58/59's package source. One read, zero
compute.**

**And the zero itself is not positive evidence.** A dispatch-count instrument returns
0 for any operator with a zero dispatch delta — an output fixed before the input is
read, which is D1's structural weakness transplanted onto a different route. The one
measurement that could positively establish the strict leg is idx 59's paired mean-C
ratio `.989312617 < 1`, and §8.4 already withdrew it for this purpose: idx 59 measured
a 3.456% analytical cut where this pass's strict cut is 1.242%, a factor of 2.78 apart.

**G-B verdict, strict operator: NOT ESTABLISHED.** It does not fire on the dispatch
channel under the "fallback = frozen incumbent" reading; nothing positively establishes
it at this host's 1.242% cut; and it fires under the other reading of its own fallback
clause. **Moot for the door: the strict leg is already CLOSED_GA (§8.2 / D6, point
estimate 6.058% under the 9% bar).**

### 9.2.5 G-B VERDICT

| operator | baseline | projected residual increase (λ=1e11) | projected FLOP saving | verdict |
|---|---|--:|--:|:-:|
| idx 268 l2-fringe | own (L1-best), +227.2 | 1.25e10 … 3.32e10 | 15,606,373,342 | NOT ESTABLISHED |
| **idx 268 l2-fringe** | **frozen deployed, +508.8 (D5)** | **2.80e10 … 7.43e10** | **15,606,373,342** | **FIRES** |
| idx 58/59 fused strict | frozen deployed, Δ = 0 or +281.6 (unsettled) | 0, or 1.55e10 … 4.11e10 | 2,216,269,776 | NOT ESTABLISHED |

**G-B: the door CLOSES on the fringe leg.** §5.5's `PASS` was withdrawn by §8.3 and is
now replaced, not restored: the correct output is **FIRES**, at the baseline the run
would actually face, under both measured laws, on every recorded seed.

> **VERIFIER OVERRIDE (2026-08-19, §10.2): row 2 of this table is withdrawn and with it
> the `FIRES`.** Its numerator is priced against the frozen deployed incumbent and its
> denominator against the L1-best route. Under either self-consistent pairing the
> conservative anchor does not deliver it: own-baseline `0.802×` (which row 1 already
> calls NOT ESTABLISHED), frozen-baseline `1.2750×` on seed 11 and `1.0324×` at the
> 5-net mean. **G-B on the fringe leg is NOT ESTABLISHED at the conservative anchor.**

---

## 9.3 D9 — THE CI95 HELPER, FIXED

**The defect** (§8.7, confirmed here by reading the file [O]). The table
`{2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571}` is keyed by **sample size `n`**
and yields the two-sided 95% `t` at `df = n − 1`. The helper indexed it at
`.get(n - 1, 1.96)`, returning `t(df = n − 2)`. Every `ci95` call site in
`attack_translate.py` passes a 5-element list (5 seeds) — 5 sites in `main()` plus this
section's new selfcheck, 39 invocations per run (1 + 5 depths × a 7-key loop + 3), and
every list is the 5-seed panel [O; corrected in §10.6 — the earlier text read "7 of 7",
which is the width of the key loop at lines 216–221, not a count of call sites] — so
every recorded interval used `t = 3.182` where `df = 4` requires `t = 2.776`.

**The fix — the minimal correct diff, one token** (the table keys were already right,
so the lookup is what moves):

```
-    t = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571}.get(n - 1, 1.96)
+    t = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571}.get(n, 1.96)
```

plus a comment naming the keying, and one module-level selfcheck that is **red on the
old behaviour and green on the new**:

```python
assert abs(ci95([0.0, 1.0, 2.0, 3.0, 4.0])[2]
           - (2.0 + 2.776 * math.sqrt(0.5))) < 1e-12, (
    "ci95 t-table lookup regressed: n=5 must use t(df=4)=2.776, not t(df=3)=3.182")
```

`stdev([0,1,2,3,4]) = sqrt(2.5)`, so the half-width is `t · sqrt(2.5)/sqrt(5)
= t · sqrt(0.5)`. Correct `hi = 3.962928424573856`; the old lookup gives
`hi = 4.250013777735594`. Evidence [O]: the assertion was executed against the real
file text after the last edit — green as written, and red when the single token is
reverted in the extracted block, with the implied `t` recovered as exactly 2.776 (new)
and 3.182 (old). `py_compile` of the whole file: OK. The file is pure ASCII.

**Annotation on the recorded artifact — not a rewrite.** `attack_translation.json` was
**not regenerated** (mtime `2026-08-10T21:39:38`, unchanged [O]).

> **Every `ci95` interval recorded in
> `experiments/uf1_attack_eligibility/attack_translation.json` is one degree of freedom
> too wide.** All of them were computed at `n = 5` with `t(df=3) = 3.182` instead of
> `t(df=4) = 2.776`; each recorded half-width is therefore too wide by the factor
> `2.776/3.182 = 0.8724073`, and the corrected interval is
> `mean ± 0.8724073 × (recorded half-width)`. **Point estimates and every `mean` field
> are unaffected.** No campaign verdict turns on an interval edge: idx 264's headline
> pair 8.98% / 6.12% and its `d2` row are means, §3.5's and §8.2's sensitivity rows are
> means, and §9.2's G-B decides on means. This annotation is the correction of record;
> the artifact keeps its history.

**Not affected: the five CI95 pairs printed in §3.1 and §3.4 of this document.** §8.7
records that they were challenged, recomputed with an independently chosen critical
value, and upheld — they never went through the defective helper. This pass did not
touch them.

---

## 9.4 DOOR STATUS — CLOSED

> **VERIFIER OVERRIDE (2026-08-19, §10.5): door status is HELD, not CLOSED, and the
> kill filed below is withdrawn.** The fringe leg's `CLOSED_GB` rests on the
> mixed-baseline comparison §10.2 corrects; the strict leg's `CLOSED_GA` is a label
> §8.2 itself declined to apply. §8's `HELD` stands. The operational consequence is
> unchanged — **no `fold_search` cell is fundable** — but no kill should be filed.

**`kerdock_host_depth2_winograd_schedule_pass`: CLOSED.** Both operators of the merged
door are closed, on different gates:

| leg | G-A | G-B | door |
|---|---|---|---|
| idx 58/59 fused strict | **CLOSED** — 6.058% under idx 264's own recorded normaliser, point estimate under the 9% bar (§8.2 / D6) | NOT ESTABLISHED (§9.2.4) | **CLOSED_GA** |
| idx 268 l2-fringe | PASS — 84.45% predeclared, 42.65% under idx 264's normaliser, 9.56% unnormalised (§3.4, §8.2) | **FIRES** — 1.80× to 4.76× at the frozen baseline, 5 of 5 seeds (§9.2.3) | **CLOSED_GB** |

§6's `OPEN` and §8's `HELD` are both superseded. **No `fold_search` cell is fundable on
this door.** §8.6's items 1 and 2 are discharged: item 1 by §9.1 (the artifacts do not
exist; the pairing is settled at [D] and the gate is invariant to it), item 2 by §9.2
(the projection is re-anchored on two measured laws and the corrected baseline).

### The closure record — context-indexed measured-static kill

| axis | value |
|---|---|
| **carrier** | `kerdock_mub` |
| **precision** | float32 (the frozen v3 entrypoint's dtype; not decisive on this kill) |
| **convention** | `residual_wall` |
| **mechanism** | `compiler_schedule` |
| **kill type** | **measured-static** — static exact enumeration over a recorded tape, priced by a *measured* per-dispatch law; zero billed compute, no estimator run, no seed consumed |
| **first break** | projected residual increase ≥ projected FLOP saving at λ=1e11 against the **frozen deployed** dispatch baseline: 2.80e10–7.43e10 FLOP-eq of residual against a 1.5606e10 FLOP saving, 1.80×–4.76×, on 5 of 5 seeds under the conservative anchor |
| **strict leg's break** | G-A: eligible effective-bill share 6.058% under idx 264's own recorded `r_d(d=2) = 0.7759509`, below the predeclared 9% bar |
| **instrument** | idx 250's measured host law 1.4609e-3 s/dispatch and the m116b/m116c campaign law 5.5088e-4 s/dispatch, both at λ=1e11; the 2026-08-19 slope law was **not** used |
| **reopening condition** | a measured per-dispatch law **on this host**, in a quiesced slot, that comes in below `ΔFLOP / Δcalls = 15,606,373,342 / 508.8 = 3.0673e7 FLOP-eq per dispatch` (= 3.0673e-4 s/dispatch; exact value 30,672,903.58, corrected from a printed 3.0674e7 in §10.6) — 1.80× below the campaign anchor and 4.76× below the host anchor; **or** an operator variant that reaches the fringe eligibility surface without the +508.8 dispatch delta. Parameter drift is excluded. **§10.2 withdraws this threshold: its numerator and denominator are measured against different baselines. Baseline-matched it is 4.3206e7 on seed 11.** |

**Preserved tissue — carried forward intact, none of it touched by the kill:**

1. **The G-A eligibility enumeration.** §3.2's 28-row seed-11 table with every
   `(k, n)`, frozen charge, m71 coverage, L1-best route, L2 mod-4 blocked price and
   both ΔFLOP columns; the totals ΔL1 11,543,513,583 and ΔL2 15,416,783,746; the 5-net
   leaf-cleanliness splits 2/5/3/4/2 exact and 26/23/25/24/26 fringe; `min core_k =
   min core_n = 160`; and §3.6's applicability answer — the l2-fringe route reaches
   28 of 28 deep hooks on every net, and the phased-WHT first product is structurally
   outside any leaf schedule. This survives the kill and is the reusable asset: it is
   the first exact statement of *how much* of the Kerdock deep-hook lane a depth-2
   schedule can reach, with m71's one-level double count removed per record.
2. **The 140-bill tape.** All 140 recorded hook charges (5 nets × 28) equal
   `cost_model.owned_batched_candidate_bill(m,k,n).total` exactly, 140/140, zero
   mismatches, reproduced independently by the verifier from re-typed source sharing no
   code with the original check (§3.1, §8.1). The deployed operator's bill is a closed
   form on this geometry.
3. **The two reproduced route prices.** `r_prod = 0.88015057621222` against idx 264's
   recorded `0.88015058`, and `grouped_l2/owned_batched @ 4096×256×256 =
   0.8866399221979091` against idx 268's recorded `0.88664`. Independent routes,
   independent records, both reproduced from re-typed frozen source (§3.3, §8.1).

Also preserved, and newly banked by this section: **the residual channel's two measured
per-dispatch laws** (§9.2.2) and **the finding that idx 69 is not a residual-channel
instrument** (§9.1) — both reusable by any future schedule proposal on either host.

---

## 9.5 Verification, the attack, and what this section leaves open

**Two independent signals per load-bearing claim.**

- **The per-dispatch law.** Signal 1: `(0.933445 − 0.419197)/(512 − 160) =
  1.4609318e-3 s/call`, computed here in exact rationals from the ledger's own
  numbers [O/D]. Signal 2: idx 250's record independently states the same slope from
  its own arm fit — "slope 1.461e-3 s/call (2.65x campaign)" — a different computation
  in the same record [O]. A third, disjoint anchor pair (m116b/m116c) gives the
  campaign law, whose intercept this pass re-derived to `0.0464160402` against the
  record's `4.641604e-2`.
- **The G-B verdict.** Signal 1: the projection at the frozen baseline under the
  **conservative** law, `508.8 × 5.5087605e7 = 2.8029e10` vs `1.5606e10`, ratio 1.796
  [D]. Signal 2: the same test run per seed on §8.5's five recorded deltas fires 5/5
  with a worst margin of 1.52×, and under the other measured law fires 5/5 with a worst
  margin of 4.04× — a verdict that survives both a change of instrument and a change of
  seed.
- **The §3.2 transcription.** The 28 ΔFLOP-L2 values re-keyed here from the printed
  table sum to exactly 15,416,783,746, the printed total [O/D]. A transcription error
  in the rows this section leans on could not survive that.
- **The `m71 cov ⇔ k even` structure.** Checked row by row over all 28 seed-11 rows,
  0 exceptions, and its consequence (`4|k ⇒ cov`) is what makes the strict operator's
  eligible surface baseline-independent [O/D].
- **D9's fix.** Signal 1: the file's own assertion executes green against the real
  file text after the last edit. Signal 2: reverting the single token in that same
  extracted text makes it red, with the implied `t` recovered as 3.182 (old) and 2.776
  (new) — the check discriminates the defect rather than merely passing.

**The attack, and it landed twice.**

1. *Counter-hypothesis: the closure is an artifact of picking the larger of two
   available per-dispatch laws.* Tested by re-running the whole gate on the smaller,
   independently anchored campaign law. It survives at the frozen baseline (1.796×) —
   **but it does not survive at the own baseline (0.802×)**. So the closure depends
   entirely on D5's baseline correction being right. That dependency is stated here
   rather than buried: if §8.5's frozen-baseline recomputation is wrong, the fringe
   leg reverts to NOT ESTABLISHED, not to PASS. §8.5's figure was computed
   independently of §5.1's and is per-seed, which is why this pass accepts it.
2. *Counter-hypothesis: the idx-69 pairing settlement is doing work in the verdict.*
   Tested by computing Route B under both readings and both baselines (§9.1.7): it
   fires at every corner. The settlement changes nothing about the door. It matters
   only for the record and for anyone who would reuse idx 69 as a residual instrument.

**Named risks, at their earned level.**

1. **The idx-69 pairing is [D], not [O].** No artifact exists in this corpus to settle
   it; the settlement rests on a cross-record consistency argument with idx 250 and on
   191 being prime. The alternative reading survives if the first target's row count
   sits in a call-neutral block band. Settling check: recover idx 69's call/memory
   traces from the Codex clone, if they were kept. Nothing in §9.4 depends on it.
2. **The strict operator's fallback clause is unsettled** (§9.2.4). It changes that
   leg's G-B from "does not fire" to "fires by 7×–19×", and changes nothing about the
   door, which is already CLOSED_GA on that leg.
3. **idx 250 is `BLOCKED_ESCALATE` and its host was contended.** That is why the host
   law is used only as the upper anchor of a bracket whose lower anchor is the
   campaign law. The gate fires at the lower anchor.
4. **The panel is still 5 synthetic He nets, not the public 100** (§7 risk 1,
   unchanged). §8.6 item 3 — replay the logging subclass over
   `experiments/t4_kerdock_descriptive_rescore/kerdock_v3_official100.json` — remains
   unrun. It would sharpen §3.4 and §8.2; it cannot rescue G-B, because the dispatch
   delta scales with the same fringe mix that drives the eligible ΔFLOP, so both sides
   of §9.2.3's ratio move together.
5. **Not verified by this pass, and named as such:** idx 268's 24-net receipts and idx
   250's residual numbers are carried at [R] from the ledger, not re-aggregated; the
   deployed l2-fringe and fused-strict executables were not opened; idx 69's targets'
   row counts are nowhere recorded and are not inferred here; and §8.5's +508.8 is
   carried at [R] from the verifier, not recomputed.

**Skipped deliberately, and named as skipped:** no cell was predeclared, no ledger field
was edited, no annotation was attached to any ledger record, no fenced path was opened
or written, the 2026-08-19 slope law was not loaded, `attack_translation.json` was not
regenerated, and no estimator, harness, FlopScope context or scored row was executed.

---

# 10. HOSTILE VERIFICATION OF THE SETTLEMENT PASS — 2026-08-19T12:15Z

Appended by a fourth, independent pass commissioned to verify §9: re-read idx 69's
record and check the pairing; re-derive the G-B arithmetic at both dispatch deltas and
check that the per-operator verdicts follow mechanically from §9.2.1's restated
thresholds; run the D9 selfcheck and confirm it is red on the reverted helper; check
the door status and its context-indexed framing. **Append-only below §9**, except the
three arithmetic corrections and four pointers itemised in §10.6.

**Verdict, up front. §9.1 is confirmed: §8.6 item 1 is discharged as far as the record
allows, the pairing settles at reading B, and the gate is invariant to it. §9.2 is
REJECTED: the comparison that closes the fringe leg divides a frozen-deployed-baseline
dispatch delta by an L1-best-baseline FLOP saving. §9.3's fix is confirmed by a real
mutant test. Door status: HELD, not CLOSED — §8's ruling stands, and no kill should be
filed.** The operational consequence does not change: **no `fold_search` cell is
fundable on this document.**

## 10.0 Compliance, and what this pass read

**Zero billed compute.** No harness, no FlopScope, no estimator execution, no scored
row, no cell predeclared, no seed consumed. Every `python` invocation ran
`python -B -P` with `PYTHONDONTWRITEBYTECODE=1` from a scratch directory outside the
corpus. The 2026-08-19 slope law was not loaded, not imported, and no number below
derives from it; it is named only in this clause. Both per-dispatch laws used below are
rebuilt here from ledger fields this pass read itself, so their provenance is
independent of that file.

**Fences.** `experiments/fold_floor_splice`, `experiments/frame_completion_129`,
`cells/` and `experiments/row_blocked_production` were not written and no file inside
them was opened. Their mtimes, stat'd after this pass's last edit [O]:
`2026-08-19T00:35:42`, `2026-08-19T04:34:40`, `2026-08-19T04:00:17`,
`2026-08-07T15:26:47` — identical to the values §7, §8.8 and §9.0 recorded.
`find . -name "*.pyc" -newermt 2026-08-19` over the whole corpus returns nothing [O].

**Read set** [O]: `headroom/fold_ledger.json` (candidates 53, 58, 59, 69, 117, 118, 250
and 268 printed in full), `core/KILL_CONTEXT_INDEX_20260819.md`,
`core/MI_SOLVE_20260819.md` lines 336–392, the frozen
`experiments/v31_guards/package_source/cost_model.py`,
`experiments/uf1_attack_eligibility/{attack_translate.py, attack_translation.json,
attack_eligibility_raw.json, attack_verify.json}`, and this document. **Modified:** this
document (§10 appended, plus §10.6's corrections and pointers). `attack_translation.json`
was not regenerated — mtime `2026-08-10T21:39:38`, read before and after every edit [O].

## 10.1 What reproduces exactly, and is confirmed

- **§9's append-only claim, proved mechanically.** `git diff --numstat` on this document
  before §10 was written: **602 insertions, 0 deletions**, single hunk
  `@@ -860,0 +861,602 @@` [O]. §0–§8 were untouched by §9.
- **idx 69's record.** Every clause §9.1.1 quotes — mechanism, kill condition,
  prediction, and the full result sentence including "core calls are150/150
  then191/194" — matches `candidates[69]` verbatim [O]. So does
  `KILL_CONTEXT_INDEX_20260819.md:30` and `MI_SOLVE_20260819.md:370–371`'s composition
  check (`intersection = 0`).
- **The two measured laws, rebuilt from the ledger in exact rationals** [O/D]:
  host `(0.933445 − 0.419197)/(512 − 160) = 64281/44000000 = 1.4609318182e-3 s`;
  campaign `(0.6105131132 − 0.3284645767)/(1024 − 512) = 564097073/1024000000000
  = 5.5087604785e-4 s`; ratio `2.6520`. The campaign anchors are themselves
  `candidates[117].result` (`.6105131132 s`, 1024 matmul calls) and
  `candidates[118].result` (`.3284645767 s`, 512 calls), read here — a second carrier
  of the same two points, independent of idx 250's transcription of them. The intercept
  re-derives to `0.0464160402` from **both** anchors.
- **Every G-B figure in §9.2.2–§9.2.5 reproduces to the printed digit** [O/D]:
  33,192,370,909 and 12,515,903,807 at +227.2; 74,332,210,909 and 28,028,573,315 at
  +508.8; the five campaign-law seed projections and their ratios 2.2297 / 1.5249 /
  1.5814 / 1.6378 / 2.0332; the five host-law ratios 5.9132 / 4.0440 / 4.1938 / 4.3436 /
  5.3920; the strict leg's 15,512,669,508 and 41,139,840,000; and the 23.80e9 flip
  threshold with its 1.52× and 1.54× multiples. The per-seed deltas mean to 508.8 exactly.
- **§5.3's algebra and bracket.** `D = 0.024611·A − 0.010126·L` re-derived from
  `(0.965263A + L + D)/(A + L) = 0.989874`; the four corners and
  `D ∈ [3,867,874,498 , 5,473,609,455]` reproduce [D].
- **§3.2, re-parsed from this document's own table text and checked row by row** [O/D]:
  28 rows; **0 violations** of `frozen − L1best = ΔL1` and `L1best − L2 = ΔL2`; both
  printed totals exact (ΔL1 11,543,513,583, ΔL2 15,416,783,746); `m71 cov = yes ⇔ k
  even` on **28 of 28**; the mod-4-clean set is `{hook 1 (256,256), hook 6 (248,244)}`,
  both `cov = yes`, ΔL2 sum **1,613,281,992**; 17 odd-`k` hooks; the route label
  `dual-odd` holds exactly when `k` and `n` are both odd. **§9.2.4's structural argument
  that the strict operator's dispatch delta is zero on its own eligible surface stands
  as written.**
- **D9's fix, with a mutant test.** The real file's text was executed with only the two
  corpus imports stubbed (they reach `flopscope`, and nothing in lines 47–67 uses them):
  **GREEN**, `ci95([0,1,2,3,4]) = (2.0, 0.03707157542614414, 3.962928424573856)`,
  implied `t = 2.776000`. The identical text with the single token reverted to
  `.get(n - 1, 1.96)`: **RED**, `AssertionError: ci95 t-table lookup regressed: n=5 must
  use t(df=4)=2.776, not t(df=3)=3.182`. With the assertion disarmed the reverted helper
  returns `hi = 4.250013777735594`, implied `t = 3.182000`; the half-width factor is
  `2.776/3.182 = 0.8724073` [O]. `py_compile` OK; the file is pure ASCII; the recorded
  artifact's `per_seed` arrays are length 5 everywhere, so the "5 seeds at every call
  site" claim holds [O].

**The pairing, independently strengthened.** Reading B stands, and the prime argument is
stronger than §9.1.3 states. Under `core_calls = ceil(m/BLOCK_ROWS)` a per-target total
is `B × Σ_products(1 + [tail])` with `B` common to every product, so a parent count of
**191** forces `B ∈ {1, 191}`. At `B = 191` the 6144-row child would issue 254–255, not
194; at `B = 1` the 8192-row blocking is inert and the whole block-height ladder does
nothing on that target. Reading A therefore requires both targets to be small enough
that block height is irrelevant, which the 503.324 / 510.926 MiB peaks contradict.
Independently: for reading A to imply even the campaign law, the parent's billed compute
`A` would have to be about `3.4e9`, two orders of magnitude under this lineage's
recorded `190–240e9`. §9.1.4's withdrawal of the Kerdock-geometry premise does not
rescue reading A, because `D` scales linearly in `A` and only a *smaller* `A` helps.
§9.1.5's "no honest per-dispatch attribution" and §9.1.6's falsifier — residual failed
at the 8192 and 7168 rungs, which issue **fewer** calls than the 6144 child — are both
sound.

## 10.2 THE DEFECT — the decisive comparison mixes two baselines

§3.2 defines its two ΔFLOP columns against different baselines, and §10.1 confirms the
definitions hold on all 28 rows:

```
ΔFLOP L1 (INELIGIBLE) = frozen_deployed_charge − L1_best        (m71's, per G-A.3 cl. 2)
ΔFLOP L2 (ELIGIBLE)   = L1_best − L2_mod4_blocked               (the depth-2 door's)
```

§9.2.3's decisive table divides **§8.5's frozen-deployed-baseline dispatch delta**
(+508.8/net; +624 on seed 11) by **§3.4's L1-best-baseline FLOP saving** (15,606,373,342;
15,416,783,746 on seed 11). Those are two different baselines. The FLOP saving that the
+508.8 calls actually buy is the whole drop from the incumbent:

```
frozen → L2  =  ΔL1 + ΔL2  =  11,543,513,583 + 15,416,783,746  =  26,960,297,329   (seed 11) [O]
```

That figure is re-summed here from §3.2's own columns, and equals `Σ frozen − Σ L2 =
154,720,254,241 − 127,759,956,912` computed independently down the other two columns [O].

**Why the pairing is not defensible on either reading.**

1. §9.2.1's own stated rationale for fixing the FLOP saving is "**unchanged, so G-A and
   G-B still price the same object**". Charging the gate +508.8 prices a different
   object — the full deployment — while crediting it only the depth-2 increment.
2. §2's predeclared G-A.3 clause 2 assigns the `frozen → L1-best` increment to m71 and
   not to this door. The +281.6 calls that separate the two deltas are *that same
   increment's* dispatch cost. A rule that refuses m71's FLOPs must also refuse m71's
   calls.
3. `MI_SOLVE_20260819.md` §W1.2, verbatim [O], gates on "delta-residual from **the
   operator's own dispatch-count delta**". §5.1 defines that as the own-baseline
   +227.2, and §8.1 reproduced it independently.
4. The decomposition is not two physical steps that can be separated. Routing an odd-`k`
   hook off the frozen direct branch is the single move that both banks ΔL1 and costs
   the extra calls.

**The two sub-moves, priced separately at the conservative campaign law** [D]:

| sub-move | Δcalls | projected Δ(λR) | ΔFLOP it banks | ratio | fires? |
|---|--:|--:|--:|--:|:-:|
| `frozen → L1-best` routing (m71's, INELIGIBLE) | +281.6 | 15,512,669,508 | 11,543,513,583 | 1.3438 | **yes** |
| `L1-best → L2` fringe (**the door's own step**) | +227.2 | 12,515,903,807 | 15,606,373,342 | 0.8020 | no |
| `frozen → L2` combined, seed 11, matched | +624 | 34,374,665,386 | 26,960,297,329 | **1.2750** | yes |

The residual-losing move is the routing step the door does **not** own. §9.2.3 charges
the door for it and credits it none of its saving.

## 10.3 What the corrected arithmetic says

**Seed 11, the one seed where both sides are exactly published** [D]:

| frame | numerator | denominator | ratio | §9.2.3 prints |
|---|--:|--:|--:|--:|
| campaign law, eligible-only denominator | 34,374,665,386 | 15,416,783,746 | 2.2297 | 2.2297 |
| **campaign law, baseline-matched** | 34,374,665,386 | **26,960,297,329** | **1.2750** | — |
| host law, baseline-matched | 91,162,145,455 | 26,960,297,329 | 3.3813 | — |

**5-net mean.** The matched denominator is `15,606,373,342 + mean ΔL1`, and mean ΔL1 is
not printed anywhere in this document. Two exact consequences [D]:

- the mean ratio is `1.0324` if mean ΔL1 equals seed 11's 11,543,513,583;
- the mean **stops firing entirely** once mean ΔL1 exceeds `28,028,573,315 −
  15,606,373,342 = 12,422,199,973`, i.e. only **7.61%** above seed 11's value.

So the printed headline `1.7960×` is recoverable only at `mean ΔL1 = 0`, which §3.2
refutes on 17 of 28 rows. §9.2.3's closing argument — that a flip "would have to exceed
23.80e9 … impossible, since the whole eligible column … varies by well under 10% across
the panel" — is false as a statement about the decision: the matched denominator is
already about 27e9 without the eligible column moving at all.

**The verdict that does follow mechanically from §9.2.1's threshold:**

| frame (self-consistent) | campaign law (conservative) | host law | G-B |
|---|--:|--:|---|
| own / L1-best: +227.2 vs 15,606,373,342 | 0.8020 — no | 2.1268 — yes | **NOT ESTABLISHED** |
| frozen deployed: +624 vs 26,960,297,329 (seed 11) | 1.2750 — yes | 3.3813 — yes | fires, margin 1.28× |
| frozen deployed: +508.8 vs 15.606e9 + mean ΔL1 | ≈1.03 — yes, at 1.0324 if mean ΔL1 = seed 11's | ≈2.74 — yes | fires, margin ≈1.03× |

Row 1 is §9.2.3's own first table and §9.2.3 already labels it NOT ESTABLISHED. Rows 2
and 3 fire at margins of 1.03×–1.28× at the conservative anchor, not the filed
1.80×–4.76×. A 1.03× margin on a projection carried across hosts from a two-point law is
not a closure this campaign can bank, and the predeclared frame says the opposite.
**G-B on the fringe leg: NOT ESTABLISHED.**

## 10.4 The strict leg's `CLOSED_GA` label

§9.4 files the strict leg as **CLOSED** on §8.2's 6.058%. §8.2 does not close it. Its
own words: "**G-A therefore stands as ruled**"; §2's predeclared `r_ref` "is the more
coherent normaliser — its numerator and denominator share the one-level baseline, where
idx 264's do not"; and the consequence it draws is that §6 finding 1's recommendation
*not to seal the strict operator* becomes "binding rather than advisory". Under the
threshold predeclared in §2 before any number appeared, the strict leg is **11.995%** and
passes; 6.058% comes from a normaliser selected after the number was known, which
inverts §0's own reading-order discipline. The owner's directive binds D6's correction —
§3.5 was wrong to dismiss idx 264's `d2` row as measuring a different operator, and
§8.2's two signals for that are confirmed — but the correction's honest label is **"do
not seal: fails G-A under the authority's named methodology, passes under the
predeclared normaliser"**, not `CLOSED_GA`.

## 10.5 DOOR STATUS — HELD

**`kerdock_host_depth2_winograd_schedule_pass`: HELD.** §8's ruling stands and §9.4's
`CLOSED` is withdrawn.

| leg | G-A | G-B | door |
|---|---|---|---|
| idx 58/59 fused strict | passes at 11.995% predeclared; 6.058% under idx 264's normaliser — **do not seal** (§10.4) | NOT ESTABLISHED (§9.2.4, unchanged) | **HELD** |
| idx 268 l2-fringe | PASS (§3.4, §8.2 — unchanged and confirmed) | **NOT ESTABLISHED** at the conservative anchor (§10.2–§10.3) | **HELD** |

**No kill is filed.** §9.4's context-indexed record is withdrawn as filed: its "first
break" is the mixed-frame ratio, and its reopening threshold inherits the same mismatch —
baseline-matched it is `26,960,297,329 / 624 = 4.3206e7` FLOP-eq per dispatch on seed 11,
41% above the `3.0673e7` filed. The four axes themselves are correctly drawn against
`KILL_CONTEXT_INDEX_20260819.md`'s doctrine (carrier, precision, convention, kill type;
`mechanism` is an addition, not a conflict), and `float32` is correctly marked
non-decisive — the framing is sound, the numbers it indexes are not.

**What is banked, unchanged.** §9.4's preserved-tissue list survives intact and this pass
re-derived all three items independently (§10.1): the G-A eligibility enumeration, the
140-bill tape, and the two reproduced route prices. So do §9's two genuinely new assets —
the residual channel's two measured per-dispatch laws, and the finding that idx 69 is not
a residual-channel instrument. **The operational guidance is unchanged from §8.6: no
`fold_search` cell is fundable on this document.**

**What would settle it, named and unrun.** (1) Compute mean ΔL1 over the 5-net panel from
the recorded tape and re-run §10.3's row 3 exactly — the tape and the frozen closed form
are already on disk, so this is static arithmetic at zero compute; it decides whether the
deployment frame fires at 1.03× or not at all. (2) Decide, as an owner call, which frame
W1.2 governs: the door's own increment (+227.2, the predeclared basis) or the deployment
(+508.8 with the matched denominator). §9 chose neither. (3) §8.6 item 3, the public-100
replay, remains unrun.

## 10.6 Every change this pass made above §10

Three arithmetic corrections and four pointers. No text was deleted.

| § | was | now | why |
|---|---|---|---|
| 9.1.7 | reading B at +227.2: `1.33× … 1.88×` | `1.32× … 1.87×` | exact values are 1.324920 and 1.874957; both had been rounded up, in the direction that overstates the fire. Route B is retired, so nothing moves. |
| 9.3 | "passes a 5-element list (5 seeds), 7 of 7" | the corrected count | there are 5 `ci95` call sites in `main()` plus the new selfcheck, and 39 invocations per run; "7" is the width of the key loop at lines 216–221. The substance — every list is the 5-seed panel — is confirmed [O]. |
| 9.4 | reopening condition `3.0674e7` / `3.0674e-4 s` | `3.0673e7` / `3.0673e-4 s` | `15,606,373,342 / 508.8 = 30,672,903.58` exactly. The derived 1.80× and 4.76× are unaffected. |

Pointers added: §9.2.3 verdict override, §9.2.5 table override, §9.4 door-status
override, and the §9.4 reopening-condition withdrawal.

## 10.7 Verification, the attack, and what this pass leaves open

**Two independent signals per load-bearing claim.**

- **The defect.** Signal 1: §3.2's column arithmetic, re-parsed from the document text
  and checked on all 28 rows with zero violations, gives `frozen − L2 = 26,960,297,329`
  two ways — as `ΔL1 + ΔL2` and as `Σ frozen − Σ L2` down the untouched columns [O].
  Signal 2: the same conclusion follows from the text alone, with no arithmetic — §9.2.1
  states the requirement ("G-A and G-B still price the same object") that its own choice
  (c) breaks, and W1.2 says "the operator's **own** dispatch-count delta" [O].
- **The two laws.** Signal 1: computed here in exact rationals from `candidates[250]`.
  Signal 2: the campaign anchors re-read from `candidates[117]` and `candidates[118]`
  themselves, a different record from the one that quotes them, with the intercept
  re-deriving to the same `0.0464160402` from either anchor [O/D].
- **D9.** Signal 1: green on the real file text. Signal 2: red on the same text with one
  token reverted, and the implied `t` recovered as 2.776 and 3.182 — the check
  discriminates the defect rather than merely passing [O].
- **Fences and artifact.** Signal 1: directory mtimes stat'd after the last edit, equal
  to three earlier passes' recorded values. Signal 2: the corpus-wide `*.pyc` sweep
  returns nothing, and `attack_translation.json`'s mtime is unchanged across every run
  [O].

**The attack, and where it landed.**

1. *Counter-hypothesis: the mismatch is cosmetic because the door only ever "owns" the
   eligible saving.* Tested by pricing the two sub-moves separately (§10.2). It is not
   cosmetic: the sub-move the door owns passes at 0.802× and the sub-move it does not own
   fails at 1.344×, so the mixed pairing inverts the attribution rather than blurring it.
2. *Counter-hypothesis: the correction reverses §9 and reopens the door.* It does not.
   Under the host law the gate fires in every frame, and under the campaign law it fires
   in the deployment frame at 1.03×–1.28×. The honest output is NOT ESTABLISHED, which is
   §8's HELD — not §5.5's PASS, and not §9.4's CLOSED. Nothing here funds a cell.
3. *Counter-hypothesis: §9.1's pairing settlement is doing hidden work.* Tested by
   re-deriving §9.1.7 at all four corners. It is not: Route B is retired, and every corner
   fires anyway.

**Named risks, at their earned level.**

1. **Mean ΔL1 is not computed here** — §10.3's row 3 carries `≈1.03` conditioned on the
   5-net mean matching seed 11's, and the exact figure needs the recorded tape re-priced
   through the L1-best route family. This is the one number that decides whether the
   deployment frame fires at all, and it is named as unrun, not estimated away.
2. **§8.5's +508.8 and its per-seed deltas are [R]** — carried from the §8 verifier by §9
   and not recomputed by either §9 or this pass. Every ratio in §10.3 inherits that.
3. **§9.2.4's "17 odd-`k` hooks × 16 blocks = 272" is a corroboration, not a check.** The
   frozen `cost_model.py` read here shows the incumbent issues 1 call per block on odd `k`
   and 2 when `n` is odd on even `k`; the L1-best odd-`k` and dual-odd branches live in
   the clone, which this pass did not open, so the per-hook L1-best call counts behind
   +281.6 are not verified here.
4. **Cross-host transfer.** §9.1.3 describes idx 250's law as measured "on this host" at
   the same fixture; idx 250's own record places it on a contended local laptop, where
   the campaign host is a different machine, and idx 69 ran on the campaign host. The
   discriminator in §9.1.3 survives by two orders of magnitude, so this changes no
   conclusion; the phrase is loose.
5. **Not verified by this pass:** idx 268's 24-net receipts and idx 250's residual numbers
   are carried at [R]; neither deployed executable was opened; the clone's cost model was
   not read; the 5-net panel remains a stand-in for the public 100.

**Skipped deliberately, and named as skipped:** no cell was predeclared, no ledger field
was edited, no annotation was attached to any ledger record, no fenced path was opened or
written, the 2026-08-19 slope law was not loaded, `attack_translation.json` was not
regenerated, and no estimator, harness, FlopScope context or scored row was executed.
