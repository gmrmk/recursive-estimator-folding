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
