# U-F1 — exact FLOP accounting for Strassen–Winograd under flopscope v0.10.0

Date: 2026-08-10. R0 arithmetic only. Governing predeclaration:
`corpus/whestbench/core/CODEX_ULTRAPLAN_20260810.md`, section **A1**.

Pinned interpreter `work/whest-v014/Scripts/python.exe`;
`flopscope 0.10.0+np2.4.6`, `numpy 2.4.6`.
No estimator source imported, no champion or `m245` module executed, no git,
no submission, no network. All writes confined to this directory.

---

## DEVIATIONS FROM THE TASK TEXT (recorded loudly, not absorbed)

1. **"EVERY temporary buffer materialization billed at 1/element" is not what
   the biller does, and taking it literally double-counts.** Metered:
   `fnp.empty` and `fnp.zeros` are charged **0**, slicing and `swapaxes` are
   charged **0**. A temporary that is *the result of* an elementwise op costs
   exactly the op — `fnp.add(x, y, out=T)` bills `|T|` once, not twice. Only a
   temporary produced by an explicit *copy* (`copyto`, `.copy()`, `concatenate`,
   `stack`) costs an extra 1/element. I therefore price four schedules
   (V1…V4 below) spanning "no explicit copies at all" to "the copy-then-add
   idiom our own M218 sidecar actually uses", and report the whole band rather
   than a single assumed one.
2. **"~32 such layers of (64512 x 256) @ (256 x 256)" is arithmetically
   inconsistent with the 145.138e9 matmul lane.** One such product bills
   8,439,201,792 FLOPs (confirmed below against CORPUS H35's recorded
   `8.4392B`). Thirty-two of them is 2.70e11, which is 1.86x the entire
   champion cost `C = 1.7683e11`. The reconciliation is that the deployed
   geometry is `n_base = 32256` (per
   `experiments/INTEGRATED_BATCHED_WINOGRAD_REPORT.md`), where one full-width
   layer bills 4,219,600,896 and 32 layers bill 1.350e11 — consistent with a
   145.138e9 matmul lane once ragged/folded widths are included. I therefore
   report r(d) at **both** M = 64512 and M = 32256 and show the ratio is
   M-independent to 1.1e-3 across M ∈ {8064, 32256, 64512}.
3. **The predeclared window is d = 0..5.** d = 6..8 is computed and reported
   separately as supplementary, and is not used for the verdict.

---

## 1. The price table, as metered (not as assumed)

Every number below is `BudgetContext.summary_dict()["flops_used"]` from a real
call on real synthetic float32 data. Source: `uf1_price_table.py` →
`uf1_price_table.json`; extra probes in `uf1_derive_and_verify.py`.

| operation | metered charge | exact formula | evidence |
|---|---|---|---|
| `matmul` (m,k)@(k,n) | 112 @ 4·4·4; 7,936 @ 16·16·16; 520,192 @ 64³; 16,744,448 @ (128,256)@(256,256) | **`2·m·k·n − m·n`** ( = `m·n·(2k−1)` ) | 8/8 shapes exact |
| `matmul` batched (b,m,k)@(b,k,n) | 6,720 @ b=7, 8³ | **`b·(2mkn − mn)`** — the `−mn` accumulator discount is granted **per batch item** | 5/5 shapes exact |
| `matmul` on strided views | 224 @ (8,4)@(4,4) | same formula; views are not repriced | exact |
| `matmul(..., out=)` | 1,920 @ (16,8)@(8,8) | same formula; `out=` adds nothing | exact |
| `add` / `subtract` / `multiply` | 16, 256, 1344, 4096 | **1 per element** | 4 shapes × 3 ops |
| same, with `out=` | identical | `out=` adds nothing | 12/12 |
| add into a *slice* destination | 64 @ 8×8 slice of 16×16 | 1 per written element | exact |
| `copyto`, `.copy()` | 256 @ 16², 1344 @ (7,3,8,8) | **1 per element** | exact |
| `concatenate`, `stack` | 128 for 2×(8×8) | **1 per element** | exact |
| `empty`, `zeros` | **0** | allocation is free | exact |
| slice view, `swapaxes` | **0** | views are free | exact |
| `take` (gather) | 256 for 64 elements | **4 per element** | exact |
| `sort` | 1,536 for n=64 | `4·n·⌈log2 n⌉` | exact |
| dtype rate | matmul 16²: f32 7,936 → f64 15,872; add 16²: 256 → 512; copyto 16²: 256 → 512 | **float64 = 2 × float32, applied uniformly to arithmetic *and* movement** | exact |

**Consequence that matters for U-F1:** because the dtype rate multiplies the
matmul term and the movement term by the *same* factor, **r(d) is exactly
dtype-independent**. Moving the lane to float64 changes C, never r(d).

One trap worth recording: `fnp.matmul(A, A)` on a *structurally symmetric*
array (e.g. `fnp.ones`) is discounted by the symmetry engine — 70 instead of
112 at 4×4. All pricing above uses distinct pseudorandom operands, which is the
correct regime for Strassen operands.

---

## 2. The charged cost at depth d — closed form

**Variant used for the headline: Strassen–Winograd with 15 additions**
(8 pre-additions + 7 post-additions), not classical Strassen's 18
(10 pre + 8 post). Reason: 15 is the minimum-addition form of the ⟨2,2,2⟩
rank-7 algorithm, and under v0.10.0 the additions are exactly what is now
billed, so the Winograd form is the one that gives Strassen its best possible
case. Classical-18 is priced alongside it (V3) so the verdict does not depend
on the choice.

Schedule (Douglas–Heroux–Slishman–Smith form), all destinations preallocated
with free `empty`, all sub-blocks taken as free strided views:

```
S1=A21+A22  S2=S1-A11  S3=A11-A21  S4=A12-S2         (4 ops on m/2 x k/2)
T1=B12-B11  T2=B22-T1  T3=B22-B12  T4=T2-B21         (4 ops on k/2 x n/2)
M1=A11*B11  M2=A12*B21  M3=S4*B22  M4=A22*T4
M5=S1*T1    M6=S2*T2    M7=S3*T3                     (7 sub-multiplies)
U1=M1+M2 ->C11   U2=M1+M6   U3=U2+M7   U4=U2+M5
U5=U4+M3 ->C12   U6=U3-M4 ->C21   U7=U3+M5 ->C22     (7 ops on m/2 x n/2)
```

Recursion splits **all three** of M, K, N (⟨2,2,2⟩); the tall row dimension is
split like the others, which is what makes 7 sub-multiplies available.

Per node the billed elementwise volume is `(a·mk + b·kn + c·mn)/4` with
`(a,b,c)` the op counts on the three block families:

| variant | (a, b, c) | what it models |
|---|---|---|
| **V1 `winograd15_floor`** | (4, 4, 7) | Winograd-15, views + `out=`, zero explicit copies — the **floor** |
| V2 `winograd15_batched` | (6, 6, 7) | V1 plus copying the 2 untransformed left (A11, A12) and 2 untransformed right (B11, B21) operands into the contiguous 7-stack a single batched `matmul` needs |
| V3 `strassen18_floor` | (5, 5, 8) | classical Strassen, 18 adds, still copy-free |
| V4 `m218_copy_idiom` | (11, 11, 12) | the schedule our own `m218_flopscope_sidecar.py` actually writes: `copyto` then `add` for all 7 transforms, 4 `copyto` + 8 add/sub in the recombination |

### Closed form

With `M, K, N` the product dims and `(a,b,c)` from the table:

```
matmul(d)   = (7/8)^d · 2·M·K·N  −  (7/4)^d · M·N
movement(d) = ( a·M·K + b·K·N + c·M·N ) / 3 · ( (7/4)^d − 1 )
charged(d)  = matmul(d) + movement(d)
classical   = 2·M·K·N − M·N

r(d) = charged(d) / classical
```

Two structural facts fall out of the metering and are easy to miss:

- The `−m·n` accumulator discount is granted **per matmul call and per batch
  item**, so splitting into `7^d` smaller multiplies multiplies that discount by
  `7^d`. That is the `−(7/4)^d·M·N` term: the matmul lane falls *faster* than
  the textbook `(7/8)^d`.
- The movement term grows as `(7/4)^d` but is anchored on `M·K + M·N`, not on
  `M·K·N`. On a tall product with K = N = 256 the additions start at 0.54% of
  the bill, so they only overtake the multiply saving very deep.

Implemented as exact integers in `uf1_derive_and_verify.py::strassen_charge`,
and independently as exact `Fraction` arithmetic in `closed_form_total`; the
two agree for every (variant, depth) tested (`assert` in the run).

### r(d), production shape (64512 × 256) @ (256 × 256), float32 or float64

| d | classical | V1 floor (Winograd-15) | V2 batched | V3 Strassen-18 | V4 M218 copy idiom |
|---:|---:|---:|---:|---:|---:|
| 0 | 8,439,201,792 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| 1 | | **0.878677** | 0.879659 | 0.879657 | 0.884561 |
| 2 | | **0.775951** | 0.778652 | 0.778647 | 0.792133 |
| 3 | | **0.692071** | 0.697781 | 0.697769 | 0.726274 |
| 4 | | **0.629184** | 0.640159 | 0.640137 | 0.694924 |
| 5 | | **0.592549** | 0.612737 | 0.612697 | 0.713479 |

At M = 32256 the same column reads 1.0, 0.878685, 0.775972, 0.692116, 0.629271,
0.592708 — identical to 4 decimals. Maximum spread of r(d) across
M ∈ {8064, 32256, 64512} is **1.12e-3**.

Absolute charged FLOPs at M = 64512, V1: d1 7,415,332,864 · d2 6,548,406,272 ·
d3 5,840,555,008 · d4 5,309,760,256 · d5 5,000,676,352.

Supplementary (outside the predeclared window): V1 r(6) = 0.592676,
r(7) = 0.649109, r(8) = 0.797048. **d = 5 is the global minimum** over d = 0..8
at width 256. For the copy-heavy V4 idiom the minimum is at d = 4 and the fold
turns *loss-making* (r > 1) at d = 7.

---

## 3. THE VERDICT

**Strassen–Winograd strictly reduces the charged FLOP bill at every recursion
depth d = 1..5 on the production shape, monotonically, under flopscope v0.10.0
pricing — and it does so under all four addition/copy schedules, including the
most copy-wasteful one our own code has ever written.**

Two adversarial checks were then run against that sentence
(`uf1_attack.py` → `uf1_attack.json`). One failed to break it and one landed;
both are reported, and the landed one changed the recommendation.

**Attack 1 — "the `−m·n` accumulator discount is a pricing exploit, so r(d) < 1
measures the biller, not Strassen." FAILED to break the result.** A *classical*
2×2 block decomposition (8 sub-multiplies + 4 accumulation adds, no Strassen)
was metered against the direct call at three shapes:
(256,64)@(64,64), (1024,128)@(128,128), (2048,256)@(256,256). All three price
**exactly equal** to the direct call — 2,080,768 / 33,423,360 / 267,911,168,
ratio 1.000000 with zero slack. The `7^d` accumulator discounts are exactly
cancelled by the accumulation additions blocking requires. There is no free
lunch in the price table, and the entire r(d) < 1 result is therefore
attributable to Strassen's 7-versus-8, which is the honest thing to be
measuring.

**Attack 2 — "depth 5 wins on FLOPs but cannot survive the numerical gate."
LANDED.** A fresh synthetic width-256 depth-32 He-initialised ReLU chain,
float32 Winograd at each depth against a float64 classical reference, 5 seeds
(`uf1_chain_seeds.json`):

| d | relative final error (mean / max over 5 seeds) | seeds passing frozen `≤2e-5` | worst ReLU gate mismatch fraction (gate `≤2e-4`) |
|---:|---|---:|---:|
| 0 | 1.07e-6 / 1.16e-6 | 5/5 | 4.8e-7 |
| 1 | 1.83e-6 / 1.99e-6 | 5/5 | 7.2e-7 |
| 2 | 3.33e-6 / 3.73e-6 | 5/5 | 9.5e-7 |
| 3 | 6.28e-6 / 7.10e-6 | 5/5 | 2.6e-6 |
| 4 | **1.19e-5 / 1.40e-5** | **5/5** | 5.0e-6 |
| 5 | **2.76e-5 / 3.11e-5** | **0/5** | 7.6e-6 |

Error grows ≈1.87x per level of recursion. The ReLU-gate criterion is never the
binding one; the relative-Frobenius criterion is. **Under the frozen
parity gate the deployable depth is 4, not 5.** (Harness cross-validation:
`INTEGRATED_BATCHED_WINOGRAD_REPORT.md` recorded `2.48581e-6` for its depth-1
32-layer chain; this independent numpy twin gives 2.59e-6 on its own seed and
1.83e-6 as a 5-seed mean — same magnitude, so the harness is measuring the
right thing.)

**How much that costs:** the FLOP-optimal depth is 5 (r = 0.5925, 1.50x
idealised score gain); the gate-passing depth is 4 (r = 0.6292, 1.44x). The
attack removes about 6% of the headline, not the conclusion.

One caveat stated in the other direction, because fairness requires it: the
`≤2e-5` parity gate is a **campaign** gate, not a scoring rule — the same
category as the `1.5x` wall-time gate that a later source audit found to be
"campaign policy, not a scoring rule". The binding scoring rule is
`r_C · r_MSE < 1`, and r = 0.5925 tolerates `r_MSE` up to **1.688**. Whether a
2.8e-5 relative drift in final activations moves MSE by more than 68.8% is
**unmeasured here** — R0 forbids estimator or scorer contact, so no `r_MSE`
number was collected at any depth. The settling check is a paired
per-network raw-MSE measurement at depth 4 and depth 5 on the already-touched
public units, which is exactly the R3 step the governing predeclaration
requires before any promotion. Until that runs, depth 5 is blocked on our own
parity gate and is neither confirmed nor disproved on score.

The v0.10.0 repricing of data movement does **not** overturn Strassen here, and
the reason is geometric rather than subtle: the additions scale as
`O(M·K + M·N)` while the multiplies scale as `O(M·K·N)` with `K = N = 256`.
Billing movement at 1/element costs Strassen 0.54% of the classical bill at
level 0, against a 12.1% multiply saving. Movement only wins the argument when
the leaf blocks get to about 4×4, i.e. depth 6+ at width 256.

**Strict margin at the optimum (d = 5, V1): r = 0.592549, i.e. a 40.75%
reduction** in the charged cost of the folded product. Even the pessimistic
V4 copy idiom yields 0.713479 at d = 5 and 0.694924 at its own optimum d = 4.

**This makes the `preallocated_strassen_winograd` kill non-binding on the
metric.** That kill was a wall-time ratio gate (1.559 / 1.546 / 1.701 against a
frozen 1.5). The wall-time gate was later audited as *campaign policy, not a
scoring rule* (`COMPRESSION_SCORE_CALCULUS_20260806.md`: FlopScope attributes
BLAS time to backend time and excludes it from charged residual). The scoring
rule bills FLOPs, and on FLOPs the family pays. **U-F1 resolves in favour of
the algebra.** Per the governing predeclaration this is *not* a reopening: it
becomes a predeclared Phase-2 candidate that must still cross R3 on recursion
depth and carry the instrument-validity gate. **No kernel code is written on
the strength of this result.**

### Adjusted-score translation

Champion, as given: `C = 1.7683e11`, `C/B = 0.650`, adjusted score `1.832e-7`.
Score law (`COMPRESSION_SCORE_CALCULUS_20260806.md`):
`score = MSE · max(0.1, C/B)`.

```
B          = C / (C/B)   = 1.7683e11 / 0.650      = 2.720462e11
raw MSE    = 1.832e-7 / max(0.1, 0.650)           = 2.818462e-7
matmul lane                                        = 145.138e9  (98.8719% of the
                                                     146.794e9 instrumented)
C(d)       = C − (1 − r(d)) · 145.138e9 · (eligible fraction)
score(d)   = raw MSE · max(0.1, C(d)/B)
```

Worked at d = 5, V1, whole lane eligible:

```
saved      = (1 − 0.592549) · 145.138e9 = 0.407451 · 145.138e9 = 59.137e9
C(5)       = 176.830e9 − 59.137e9       = 117.693e9
C(5)/B     = 117.693e9 / 272.046e9      = 0.432621      (well above the 0.1 floor)
score(5)   = 2.818462e-7 · 0.432621     = 1.21935e-7
improvement= 1.832e-7 / 1.21935e-7      = 1.5025x
```

Full table (V1 floor schedule):

| d | r(d) | **whole lane eligible** C/B → score → gain | **at our measured 57.4164% dispatch eligibility** C/B → score → gain |
|---:|---:|---|---|
| 1 | 0.878677 | 0.5853 → 1.6496e-7 → 1.1106x | 0.6128 → 1.7273e-7 → 1.0606x |
| 2 | 0.775951 | 0.5305 → 1.4951e-7 → 1.2253x | 0.5814 → 1.6386e-7 → 1.1180x |
| 3 | 0.692071 | 0.4857 → 1.3690e-7 → 1.3382x | 0.5557 → 1.5661e-7 → 1.1697x |
| 4 | 0.629184 | **0.4522 → 1.2744e-7 → 1.4375x** ← deepest gate-passing | **0.5364 → 1.5119e-7 → 1.2118x** ← deepest gate-passing |
| 5 | *0.592549* | *0.4326 → 1.2193e-7 → 1.5025x* (fails parity gate) | *0.5252 → 1.4802e-7 → 1.2376x* (fails parity gate) |

The 57.4164% column is not a guess: it is the measured eligible share of the
direct hook bill from `INTEGRATED_BATCHED_WINOGRAD_REPORT.md`, where 16 of 29
hooks dispatched Winograd. That figure was measured at **depth 1**; depth 4-5
need `k, n ≡ 0 (mod 16 or 32)`, so raw eligibility that deep is *worse*, not
better, unless padding is used — see the envelope below. The two columns
therefore bracket the honest range: **1.21x – 1.44x adjusted-score improvement
at the deepest gate-passing depth (d = 4)**, and 1.24x – 1.50x at the
FLOP-optimal but parity-failing d = 5. Both are before any MSE change, which
was not measured (R0 forbids scorer contact).

### Ragged-width envelope (arithmetic only, no kernel)

Depth d requires the contracted and output dims divisible by 2^d, and the
champion's folded active widths are ragged. Padding to the next multiple of
2^d and paying the full padded volume gives, per width W (M = 32256, K=N=W,
`uf1_eligibility_envelope.py`):

- 242 of the 249 widths in [8, 256] have `r_best < 1`; the smallest paying width
  is **W = 10**, and only 7 widths never pay at any depth.
- `r_best` chooses depth 5 for 56 widths, 4 for 76, 3 for 62, 2 for 32, 1 for 16,
  and 0 (direct) for 7.
- Mean `r_best` = 0.6809 over W ∈ [128, 256], 0.7523 over W ∈ [8, 256], which
  translate to **1.3549x** and **1.2552x** adjusted-score improvement.
- Capping depth at 4 to respect the parity gate (attack 2), those become
  `r_best` = 0.6941 / 0.7591 → **1.3353x** / **1.2465x**
  (`uf1_envelope_depth_capped.json`).

So an *adaptive-depth padded* dispatcher recovers most of the idealised
1.44x-at-d=4 figure even on ragged widths, and lands well above the 1.21x that
the current fixed-depth-1 eligibility rule delivers. That is an observation
about the arithmetic, not a kernel design; per the governing predeclaration no
kernel is written on the strength of A1.

---

## 4. Reconciliation with the rival (skye_nygaard, Discourse topic 18145)

Their claim: **1.5412x score improvement, attributed entirely to a cheaper
depth-5 Strassen–Winograd kernel.**

Inverting the score law, with MSE held fixed and the multiplier above its floor:

```
required whole-entry r_C = 1 / 1.5412                    = 0.648845
required C/B             = 0.650 · 0.648845              = 0.421749
required C               = 0.421749 · 2.720462e11        = 1.147353e11
required r on the matmul lane, if OUR cost decomposition held
                         = 1 − (1.7683e11 − 1.147353e11)/145.138e9
                         = 0.572168
```

Our depth-5 floor is **r = 0.592549**. So on *our* entry, with *our* cost
decomposition, depth-5 Winograd yields 1.5025x, which is **97.5% of their
claimed 1.5412x** — short by 3.4% in lane ratio, not by a factor.

Is the shortfall evidence against them? No. Three ordinary explanations each
close the gap on their side, and I cannot distinguish them from public data:

1. **Different residual overhead.** Our `C = 176.830e9` exceeds our instrumented
   `146.794e9` by 30.04e9 of residual-time charge that Strassen cannot touch.
   If their effective cost is closer to pure billed matmul — e.g. the
   `random32,256` profile at 99.684% matmul share — then the same
   `r_lane = 0.5925` gives `r_C = 1 − 0.98872·0.407451 = 0.5971`, a **1.675x**
   improvement, which *exceeds* 1.5412x. Their number is comfortably inside the
   achievable band for a matmul-saturated entry.
2. **Different baseline.** 1.5412x against a naive or unfolded parent is a
   different statement from 1.5412x against a champion that already folds dead,
   always-on, and kink neurons. Our lane is already compressed.
3. **Their `r_MSE ≈ 1` premise is one we can independently corroborate at
   shallow depth.** Their ablation attributes the gain "entirely" to the cheaper
   kernel, which implies `r_MSE ≈ 1`. Our own promoted depth-1 port measured
   `r_MSE = 0.999983` on public 0..99. So the premise is not exotic — though we
   have no measurement of it at depth 5 (see below).

**Assessment: their 1.5412x is arithmetically consistent with a depth-5
Strassen–Winograd fold and requires no error on their part.** The one
independent corroboration worth flagging is that **depth 5 is exactly the
FLOP-optimal depth at width 256** under this price table (r(5) = 0.592549 <
r(4) = 0.629184 and < r(6) = 0.592676). A rival who tuned depth empirically on
a 256-wide network would land on 5. That is a non-trivial agreement between
their reported design choice and our independently derived optimum, and it
raises rather than lowers my confidence in their report.

The one place their claim is testable and *strained* is numerical, not
arithmetic. Our 5-seed measurement puts float32 depth-5 Winograd at
2.76e-5 mean relative error on a 32-layer chain. If their estimator runs the
same float32 width-256 depth-32 geometry, they are carrying that drift into
their MSE. Their gain being "entirely" attributable to the cheaper kernel
implies they observed `r_MSE ≈ 1` despite it — which is possible (our own
depth-1 port measured `r_MSE = 0.999983` against a 2.5e-6 drift, and MSE is far
less sensitive than a Frobenius parity norm), but it is the assumption of
theirs I would probe first.

What would settle the reconciliation: their entry's matmul share of *effective*
(not billed) cost, their multiplier, and their measured `r_MSE`. None of the
three is in the public post.

---

## 5. Two-signal verification

**Signal A — analytic.** Exact integer recursion `strassen_charge`, and an
independent exact-`Fraction` closed form `closed_form_total`. They agree for
every (variant, depth) evaluated (asserted in-run, 4 variants × 6 depths × 2
row counts = 48 assertions).

**Signal B — metered.** A real recursive Strassen–Winograd built from
flopscope primitives (`sw_product`) run inside a `BudgetContext`, at the **full
production width K = N = 256** with the row count reduced 8x for tractability
(M = 8064; r(d) is M-independent to 1.1e-3, shown above).

| d | metered charged FLOPs | analytic prediction | exact match | metered r | rel. Frobenius vs float64 classical |
|---:|---:|---:|:--:|---:|---:|
| 0 | 1,054,900,224 | 1,054,900,224 | yes | 1.000000 | 2.85e-7 |
| 1 | 926,973,952 | 926,973,952 | yes | 0.878731 | 5.34e-7 |
| 2 | 818,708,480 | 818,708,480 | yes | 0.776100 | 1.02e-6 |
| 3 | 730,398,720 | 730,398,720 | yes | 0.692387 | 1.96e-6 |
| 4 | 664,367,104 | 664,367,104 | yes | 0.629791 | 3.99e-6 |
| 5 | 626,258,432 | 626,258,432 | yes | 0.593666 | 8.69e-6 |

Bit-exact at every depth, on top of three further shapes
((256,64)@(64,64), (1024,64)@(64,64), (512,128)@(128,128)) at depths 0–4 —
**21/21 exact matches**, and 15/15 of those also match the exact-`Fraction`
closed form. The Frobenius column is a second, *different* kind of
check: it confirms the metered code is actually computing A·B (so the FLOP
count is the count of a correct Winograd, not of a mis-wired one).

**Bitwise repeat:** depth-5 metering run twice → 626,258,432 both times.

**Signal C — reproduce numbers from our own cached record.** Independent of
both of the above:

| recorded, from our corpus | value | model |
|---|---|---|
| CORPUS H35 direct full-product bill | `8.4392B` | computed **8,439,201,792** — agrees to 2.1e-7 relative, and pins the lane at dtype rate 1.0 (float32) |
| Mutation B measured **billed** L1 ratio | `0.880151` | inside the model band [V1 0.878677 … V4 0.884561] |
| CORPUS H35 L2 hybrid ratio | `0.795427` | model band at d=2 is [0.775951 … 0.792133]; the recorded value sits **0.0033 above** the band |

The L2 hybrid miss is reported rather than fitted away. It means that
implementation charged about 27.8e6 elements more movement than even the
copy-then-add idiom — consistent with its documented `concatenate`/`stack`
packing graph, which the corpus itself blames ("The Python allocation graph
erases the saving"). The hard lower bound is respected in both cases: the
recorded 6.7128e9 exceeds the unavoidable depth-2 leaf-matmul bill of
6,423,330,816, and the recorded L1 7.4278e9 exceeds the depth-1 leaf bill of
7,369,850,880.

---

## Files

- `uf1_price_table.py` → `uf1_price_table.json` — metered price table
- `uf1_derive_and_verify.py` → `uf1_results.json` — closed form, verification,
  score translation, rival reconciliation, cached cross-checks
- `uf1_meter_production_width.py` → `uf1_production_width_metering.json` —
  metered Winograd at K = N = 256, d = 0..5, determinism repeat, depth 0..8
- `uf1_eligibility_envelope.py` → `uf1_eligibility_envelope.json` — ragged-width
  padding envelope
- `uf1_attack.py` → `uf1_attack.json` — adversarial pass (no-free-lunch pricing
  check; depth-32 chain parity), plus `uf1_chain_seeds.json` (5-seed repeat)
  and `uf1_envelope_depth_capped.json` (envelope re-run with depth capped at 4)
- `UF1_ACCOUNTING.md` — this document

`uf1_results.json` is the merged artifact and contains every block above.
