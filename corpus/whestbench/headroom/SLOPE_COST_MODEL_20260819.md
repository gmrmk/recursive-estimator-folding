# The slope cost model

**Residual wall seconds predicted from static dispatch structure — the companion to the FLOP cost model.**

Lane H4. 2026-08-19. Companion script: `slope_cost_model.py` (runs offline, no flopscope
needed, writes `SLOPE_COST_MODEL_20260819.json`).

---

## 0. Verdict first

The campaign has an exact model of one half of its own cost law and none of the other:

```
C = analytical_FLOPs  +  100e9 * residual_wall_time_s
    \_______________/     \___________________________/
     cost_model.py,         no model at all until now
     tier ladder,
     floor_candidate_bill
```

This document is the second half. It counts, by static analysis of the committed sources,
how many `flopscope.numpy` dispatch sites each route executes per network, fits a two-term
law, validates it against every residual measurement in the corpus plus one public
measurement, and files two falsifiable predictions.

**Three results that change how the residual channel should be reasoned about.**

1. **A per-call slope is not a machine constant.** Going from the parent `random32256` to
   the promoted row-blocked child raises native matmul dispatches by 92% (215.4 → 414.4)
   and *lowers* residual by 4.8% (0.168749 s → 0.160585 s). A constant 5.509e-4 s/call
   predicts +0.110 s and gets the sign wrong. The wide-GEMM slope is bounded above by
   **4.10e-5 s/call** and is consistent with zero; the v5d3 figure belongs to a different
   shape class (leaf contraction depth ≤ 32, not 128).
2. **Residual is a route-class step plus a sub-linear dispatch term, not a linear
   dispatch cost.** The best linear-in-`N_dispatch` fit requires a *negative* dispatch
   coefficient. The shipped form reaches R² 0.979 across five routes with a 2.0%
   cross-harness holdout error.
3. **This fold is not topic 18184.** 18184 loses 18 residual-equivalents per metered FLOP
   saved because it batches only 13% of its recursion. `depth6_winograd` batches 64% and
   **wins 2.66 : 1** — the two implementations sit a factor of 48 apart on the same
   arithmetic.

**Filed predictions** (falsifiable; the numbers are the point of the document):

| prediction | value | falsified if |
|---|---|---|
| fold's Public100 mean residual | **0.3586 s** | outside `[0.289, 0.428] s` |
| fold's residual multiplier vs incumbent | **2.233×** | outside `[1.80, 2.66]×` |
| fold's Public100 mean C | **158.42B** (ratio 0.8344) | — |
| fold's Public100 adjusted score | **1.770e-7** (incumbent 2.1218e-7) | — |
| 129-completion, incumbent ΔC | **+4.676B = +2.463%** of C | — |
| 129-completion, fold ΔC | **+2.887B = +1.823%** of C | — |
| residual share of the 129 penalty | **12.4%** incumbent, **0%** fold | — |

---

## 1. Hyperassociation (mandatory step, done before any design)

Graph: `graph/graph.json`, 710 nodes / 4,319 edges. Stripped: the 38 `descriptive_index`
nodes and the `target` shunt (`Winning legal adjusted score`, betweenness 0.3703 — it is a
scoring objective, not a mechanism, and routing through it makes every pair of nodes look
adjacent). Core after stripping: **671 nodes**. Insights 105–170 of
`DETERMINISTIC_INSIGHTS.md` read in full.

### 1.1 Nodes within 2 hops of the hypothesis's key objects

Seeds: `budget` (272B combined-budget law), `row_blocked_production`, `row_blocked_winograd`,
`allocation_wall`, `v5d3_static_replay`, `slope_law_double_witness`, `residual_dispatch_lane`,
`terminal_route_fold`, `small_gemm_wall`, `l3_call_residual_gate`, `absolute_wall_rule`,
`preallocated_strassen`, `integrated_batched_winograd`, `two_axis_winograd`,
`compute_lane_closure`, `ladder1_percall_floor`, `phase2_lambda_fork`, `fold39936`.

The 2-hop closure is **105 nodes**. The load-bearing ones, by hop:

**Hop 0/1 — the mechanism's own neighbourhood.**
`budget` (proved) · `row_blocked_production` (promoted_local_champion) ·
`row_blocked_winograd` (screened_engineering_survivor) · `allocation_wall` (measured
failure_mechanism) · `small_gemm_wall` (measured failure_mechanism) · `absolute_wall_rule`
(source_audited constraint) · `v5d3_static_replay` (committed_mechanism_sourceless) ·
`slope_law_double_witness` (measured_twice) · `residual_dispatch_lane`
(deployment_lane_open) · `l3_call_residual_gate` (frozen_pending falsifier) ·
`ladder1_percall_floor` (certified_crowned) · `terminal_route_fold` (live_queued) ·
`preallocated_strassen` / `integrated_batched_winograd` / `two_axis_winograd` ·
`compute_lane_closure` (proved no_go) · `fold39936` (demoted) · `phase2_lambda_fork`
(open_until_rules_post) · `m169_dispatch_fusion` (resource_survivor_conditional_staging) ·
`clone_l2fringe_recompute` (pass_screen_reproduced).

**Hop 2 — the ring that priced them.**
`compression_score_law` (proved) · `failure_gate` (predeclared, Cmax < 258.4B) ·
`flopscope_bom_receipt` (recovered: λ = 1e11 exact, matmul 98.94% of billed) ·
`exact_sampler_strassen` (rejected_algebra_preserved) · `m160_hostile_selfhost_audit`
(killed_resource) · `m164_exterior_native_audit` (killed_resource_no_efficacy) ·
`x5_residual_convention_refuted` (measured) · `codex_domain_history`
(uncommitted_measurements) · `owner_l2fringe_adoption` (adopted_compute_half) ·
`v31_guards` (validated_robust_candidate) · `random32256` (promoted_parent) ·
`r3_transfer_rung` (adopted) · `multiple_comparisons_fleet_hazard` (adopted) ·
`design_boundary_lemma` · `suite_ladder` · `compute_ceiling_correction` (landed) ·
`mub129_completion_lever` (killed_prior_art_and_power) ·
`inplace_row_ownership` (proved_component) · `m116b_inplace_l3` (campaign_harness_repair).

### 1.2 Every KILL node adjacent to this mechanism, and why the premise differs

The mechanism here is **a cost model of residual seconds**, not a new estimator. That is
the premise change that lets it live next to nine kills that would otherwise cover it.

| kill node | its premise / kill condition | why this premise differs |
|---|---|---|
| `allocation_wall` *(measured)* — "Python temporaries erase exact Strassen savings; L1 residual must fall below .00987 s for parity" | a candidate whose product temporaries are unpooled | Not a candidate. The kill is the model's **training signal**: it is the first campaign measurement that residual is allocation-shaped rather than call-shaped, which is the `kappa` term below. |
| `small_gemm_wall` *(measured)* — "seven half-width products plus Winograd traffic remain slower than one optimized full-width GEMM after allocation is repaired" | a **wall-time** microbenchmark at a 1.5× relative gate | `absolute_wall_rule` re-audits it: "relative 1.5x gate is policy; backend wall excluded from C". This model prices **residual**, from which backend wall is excluded by definition. The wall figure is reported separately as a deployment risk, never as a score term. |
| `exact_sampler_strassen` *(rejected_algebra_preserved)* — "bill ratio .795427 … allocation residual makes effective compute 8–45% worse" | whole-row Strassen with no preallocation | `DepthWinograd` pools all three operand lanes with hysteresis. The model *measures* what that pooling buys (κ = 0.140 s of pool churn remains, against the 8–45% the unpooled route lost). |
| `preallocated_strassen` *(rejected_score_operator_preserved)* — "batched score proxy .885099×, total wall 1.54559×, misses the frozen gate" | the frozen relative-wall gate | Same policy-versus-C distinction. Its score operator was preserved and is the incumbent's ancestor; the model consumes it as tissue. |
| `integrated_batched_winograd` *(rejected_score_operator_preserved)* — killed at **667.3 MiB** peak | the `< 512 MiB` process clause | **This kill is live against the fold**, not resolved: the fork measures 615.8 MiB. The model does not claim otherwise; §7 files it as the binding open risk. |
| `m203_terminal_contraction_circuit_no_go` *(killed_standard_exact_fusion)* | a new exact **fusion** of terminal contraction | No new fusion. The schedule being priced is `depth6_winograd`, already committed and self-checked over the integers. |
| `compute_lane_closure` *(proved no_go)* — "ReLU commutes only with nonnegative monomial matrices; rank-r breaks even at r = n/2" | **rank reduction** | Exact Winograd reassociation preserves the product bit-for-bit over any ring; no rank is reduced. |
| `m164_exterior_native_audit` *(killed_resource_no_efficacy)* — "residual is 9.456–10.639 ms versus 7.149 ms permitted" | a residual budget at the 10-ms scale on an exterior control | Different scale and different subject. Its real value here is what it *invalidated* — see the next row. |
| `m160_hostile_selfhost_audit` *(killed_resource)* — "maximum five-times-residual projection is 278.273B versus 258.4B" | the **×5 hostile-residual convention** | `x5_residual_convention_refuted` *(measured)*: "the 'roughly 5x' hostile-residual multiplier — the sole binding failure of five records — is observed at k ~ 1.0 on fresh hosted graded data." The convention is refuted, so this model does **not** apply a ×5 projection. See §1.4(1); this changed the deliverable. |
| `l3_call_residual_gate` *(frozen_pending falsifier)* — "32 calls per hook must keep whole-prediction residual at most .170 s and peak at most 464 MiB" | a residual ceiling of 0.170 s for a level-3 hook candidate | This is the closest thing to a direct falsifier and the model's prediction (0.3586 s) blows through it by 2.1×. The gate belongs to **M116b**, a different child, and it is `frozen_pending` rather than adopted; but the honest statement is that any successor inheriting a 0.170 s residual clause kills the fold on this model's own number. Filed in §7. |
| `mub129_completion_lever` *(killed_prior_art_and_power)* — "3 nets × 16 rotations has 5% power against a 0.45% effect" | the completion as a *candidate* | Prediction 2 does not revive it. It prices what the completion would cost, and independently reproduces the corpus's own 2.33% break-even. |
| `fold39936` *(demoted)* — "five combined-budget failures, max C 294.999B" | a recursive fold that blew the budget on **C**, including residual | Precisely the failure mode this model exists to predict before it happens. |

### 1.3 PRESERVED tissue this design reuses

Every one of these is consumed as-is; nothing is re-derived by hand.

- **`cost_model.py` closed forms** (`node_area_sum`, `psi_cost`, `owned_batched_candidate_bill`,
  `floor_candidate_bill`, `inplace_depth_core_cost`) — imported directly by the companion
  script, which has no flopscope dependency. The script re-proves five committed constants
  on import, so a drift in the frozen source fails the model rather than silently moving it.
- **`ladder1_percall_floor`** *(certified_crowned)* — `floor_candidate_bill(4096,256,256) ==
  303_096_592` reproduced; `realized_l6` 307,749,648 and the full realized depth table
  {2:420188160, 3:374316032, 4:338592000, 5:315007424, 6:307749648} reproduced against
  `full.json`'s committed `selfchecks`.
- **`budget`** *(proved)* — the C law, re-verified numerically: incumbent net0
  186,406,005,979 + 1e11 × 0.14525899999716785 = 200,931,905,978.72, matching the committed
  `effective_C` to the last digit.
- **`flopscope_bom_receipt`** *(recovered)* — λ = 1e11 exact and **matmul at 98.94% of
  billed**, used to split the 129-completion's FLOP delta.
- **`slope_law_double_witness`** *(measured_twice)* and **`v5d3_static_replay`** — the
  5.509e-4 s/call slope and the 18184 18:1 ratio, both reconciled in §5.
- **`row_blocked_winograd.py`'s `independently_expanded_bill`** — the second-derivation
  discipline this document copies: every counted quantity is derived twice.
- **`compression_score_law`** *(proved)* — "a child wins iff cost ratio × raw-MSE ratio is
  below one", used for the score consequence in §6.
- **`absolute_wall_rule`** *(source_audited)* — backend time excluded from residual charge.
  This is what makes a residual-only model the correct object.
- **`phase2_lambda_fork`** *(open_until_rules_post)* — the model's entire value is
  conditional on λ surviving; stated in §7 rather than buried.
- **`residual_dispatch_lane`** *(deployment_lane_open)* — "the G4 dispatch-slope successor
  attacking Python dispatch around folding, copying, add and sub". This model is the
  pricing instrument that lane has been missing.

### 1.4 The three most surprising adjacencies, and whether they changed the design

**(1) `M164 exterior-control native audit --invalidates_sole_binding_gate_of-->
`x5 hostile-residual convention refuted`.** Evidence on the edge:
"m145/m153/m157/m160/m163/m164 passed every structural gate and died only on a
reported-level ~5x residual multiplier observed at k ~ 1.0."

Six consecutive candidate deaths were caused by an accounting convention that later
measured as false. **This changed the deliverable.** A ×5 hostile projection on the fold
gives C = 122.6B + 5 × 35.9B = 302B, far past both the 258.4B safety gate and the 272B
cliff, and I had drafted that as a headline finding. The graph says the gate is refuted.
The finding was removed. Without this adjacency the document would have shipped a false
kill of its own subject.

**(2) `MUB 126->129 completion lever --prices_completion_below_breakeven--> Iterated
arc-cosine kernel variance predictor`.** Evidence: "degree-4 share 0.4497% against a
**2.33% point-count break-even**; three routes agree, one predictive."

The corpus already holds a break-even number for exactly the question Prediction 2 was
asked to answer — reached by point-count arithmetic and an arc-cosine kernel variance
predictor, sharing no machinery with dispatch counting. **This changed the design**: it
turned Prediction 2 from an unvalidated forecast into a cross-validated one (this model:
2.463%; corpus: 2.330%; **5.7% apart**), and it forced the addition of the residual/FLOP
decomposition, which is the only part the existing number does not carry.

**(3) `Preallocated Strassen--Winograd --reinterprets_non_score_failure_of--> Absolute
wall-time rule`.** Evidence: "relative 1.5x gate is policy; backend wall excluded from C."

The canonical Winograd kill of this lineage — `small_gemm_wall`, wall ratios
1.559 / 1.546 / 1.701 — was scored against a policy microbenchmark, not against C.
**This changed the model's variable set**: wall time was dropped as a predictor entirely.
The fold's 6× wall blow-up (2.8 s → 16.4 s per predict) is a deployment risk against the
frozen 20 s clause, not a score term, and the model prices residual alone and reports wall
separately. Had wall stayed in, the model would have been fitting the wrong dependent
variable, and the L5/L6 routes (22–28 s per predict) would have dominated the fit.

*Honourable mention*, methodologically: `Structural compute-lane closure
--occupies_unadjudicated_design_side_of--> Suite-level design-boundary ladder`, whose
evidence field reads "the graph carries no edge from the closure to any design-algebra
node — **the hole is absence, not refutation**." A graph that records the difference
between "killed" and "never adjudicated" is doing work that a reading list cannot.

---

## 2. What was counted, and how

### 2.1 The two routes

Both trees share `base_estimator.py` and `row_blocked_winograd.py` **byte-identically**
(verified by diff). The incumbent
(`experiments/row_blocked_production/candidate_source/`) routes its two sample-path hooks
through `RowBlockedBatchedWinograd`. The fold
(`experiments/fold_floor_splice/candidate_source/`) routes the same two hooks *and* six
full-height terminal-fold products through `DepthWinograd`
(`FOLD_PRODUCTS_THROUGH_OPERATOR = True`, the single shipped mechanism; the other three
flags are ported and default-off).

Per predict, at width 256, depth 32, `n_base = 126*256 = 32,256`:

- `for layer in range(1, mlp.depth - 3)` → **28** full-height products (m = 64,512)
- `_first_sample_matmul` → **1** half-height product (m = 32,256)
- fold fork only: `x @ weight30[:, kink30]`, `pre31(kink31, False)` (2 legs),
  `pre32(kink32, False)` (3 legs) → **6** more full-height products

### 2.2 Incumbent dispatch sites — `RowBlockedBatchedWinograd.multiply`

```
right pack, hoisted outside the row loop : 3 copyto + 4 subtract          =  7
per row block  : left stack 3 copyto + 1 add + 3 subtract                 =  7
                 one batched fnp.matmul (7 leaves in one dispatch)        =  1
                 reconstruction 6 add + 1 subtract                        =  7
                                                                            --
                                                                            15
dispatches(m) = 7 + 15 * ceil(m / 8192)
```

The operator returns `self.output[:m, :n]` — **a view of preallocated scratch** — so it
allocates nothing per call. That is the single structural difference from the fold that
the fit later identifies as dominant.

| m | blocks | dispatches | matmuls | fresh bytes |
|---|---:|---:|---:|---:|
| 64,512 | 8 | 127 | 8 | 0 |
| 32,256 | 4 | 67 | 4 | 0 |

**Per predict: 28 × 127 + 67 = 3,623 dispatches, 228 matmuls, 0 fresh bytes.**

### 2.3 Fold dispatch sites — `DepthWinograd.multiply_at_depth`

```
_prepare_right  : one ix_ gather + one copyto + L psi + 3L encode        = 2 + 4L
_core, per block: one copyto load + 11L lane ops + one fnp.matmul
                  + one copyto unload                                    = 3 + 11L
                  (11L = psi_left L, encode_left 3L, decode 6L, psi_c L)
plus one fnp.empty for the freshly allocated result                      = 1
```

`_rows_per_block(L)` depends on `self.width` and `L` **only** — never on the product's
live contracted width `k` or output width `n`. **The dispatch count of a depth-L product
is therefore invariant to how much of the layer is alive.** This is the property that lets
a residual delta measured on all-active synthetic nets transfer to the pruned Public100
suite, and it is why Prediction 1 is a prediction rather than an extrapolation.

| L | rows/block | blocks (m=64,512) | calls/core | dispatches/product | module's own counter |
|---:|---:|---:|---:|---:|---:|
| 2 | 31,968 | 3 | 25 | 86 | 84 |
| 3 | 18,208 | 4 | 36 | 159 | 152 |
| **4** | **10,352** | **7** | **47** | **348** | **328** |
| 5 | 5,856 | 12 | 58 | 719 | 672 |
| 6 | 3,264 | 20 | 69 | 1,407 | 1,308 |

`_core` returns `4 + 10*levels`; the true data-touching count is `3 + 11*levels`
(1 copyto load + L psi_left + 3L encode_left + 1 matmul + 6L decode + L psi_c + 1 copyto
unload). The module's counter under-reports the lane count by 3 per core call at L=4.
**Recorded, not trusted** — and §4.3 shows the filed prediction is invariant to which of
the three conventions is used.

### 2.4 Depth-route uptake, recovered from the FLOP receipts

Both routes run the same estimator, so every non-sample-product FLOP cancels:

```
T(inc) - T(L) = uptake(L) * ( S_fallback - S_depth(L) )
```

with `S_fallback = 211,691,454,464` and `S_depth(L)` from the transcribed
`realized_core_bill`. Against `full.json`:

| L | uptake |
|---:|---:|
| 3 | 0.9679 |
| 4 | 0.8923 |
| 5 | 0.7982 |
| 6 | 0.7643 |

Uptake falls monotonically with depth because `realized_depth_bill` needs multiples of
`2^L` and a fringed shape can lose to `owned_batched`. This is the mechanism behind the
measured FLOP saturation at L ≥ 5 (129.78B at L5 against 129.43B at L6, where the ideal
sweep predicts a further 3.5B). Recovering uptake from the receipts is what lets the
dispatch model be evaluated on the route the machine *took*, not the one the sweep would
take on ideal widths.

### 2.5 The route table

| route | N_dispatch | N_matmul | bytes_moved | fresh alloc | residual s |
|---|---:|---:|---:|---:|---:|
| incumbent | 3,623 | 228 | 6,602,817,536 | 0 | 0.1466 |
| fold L3 | 5,460 | 142 | 41,344,689,526 | 2,279,079,936 | 0.2938 |
| fold L4 | 11,222 | 246 | 64,313,839,352 | 2,279,079,936 | 0.3698 |
| fold L5 | 20,708 | 386 | 97,728,390,179 | 2,279,079,936 | 0.3698 |
| fold L6 | 38,159 | 592 | 159,197,069,457 | 2,279,079,936 | 0.4023 |

Residuals are `full.json` medians of three reps, averaged over the two synthetic nets.

---

## 3. What the data refutes

Read the table before reading the model. `N_dispatch` grows **10.5×** from incumbent to
L6; `bytes_moved` grows **24×**; residual grows **2.74×**. And L3 has *fewer* row blocks
and *fewer* matmul dispatches than the incumbent while carrying twice its residual.

Least squares over the five routes, with coefficient sign as the filter:

| form | R² | max rel err | verdict |
|---|---:|---:|---|
| `N_matmul + sqrt(N_dispatch)` | 0.9838 | 5.63% | **negative coefficient — unphysical** |
| `alloc_bytes + log2(N_dispatch)` | 0.9790 | 6.81% | shipped |
| `depth_route + log2(N_dispatch)` | 0.9790 | 6.81% | shipped (same fit; the indicator and the byte count are collinear here) |
| `N_matmul + log2(N_dispatch)` | 0.9758 | 6.88% | **negative coefficient** |
| **`N_dispatch + bytes_moved`** *(the form the brief proposed)* | 0.9731 | 7.84% | **negative dispatch coefficient (−1.86e-5 s/call) — refuted** |
| `N_dispatch` alone | 0.5298 | 71.7% | refuted |
| `bytes_moved` alone | 0.7150 | 47.2% | refuted |
| `N_matmul` alone | 0.3450 | 94.6% | refuted |

**The brief's two-parameter form `alpha*n_dispatch + beta*bytes_moved` does not survive.**
Its least-squares solution needs a negative dispatch coefficient, which is the algebra's
way of saying the two predictors are fighting: `bytes_moved` over-predicts the depth
routes and `N_dispatch` has to subtract the excess back out. A better form is justified
below.

### 3.1 The single cleanest refutation

Public100, `ROW_BLOCKED_WINOGRAD_PRODUCTION_REPORT.md`, one official run, paired:

| | matmul calls | residual | s/call |
|---|---:|---:|---:|
| parent `random32256` (plain `@`) | 215.41 | 0.168749 s | 7.834e-4 |
| child `random32256_rowwinograd8192` | 414.41 | 0.160585 s | 3.875e-4 |

**+92% native calls, −4.8% residual.** A constant per-call slope of 5.509e-4 predicts
+0.1096 s and gets the sign wrong. The measured wide-GEMM slope is bounded above by

```
|0.160585 - 0.168749| / (414.41 - 215.41)  =  4.10e-5 s/call
```

which is **13× below** the v5d3 figure and consistent with zero.

A per-call slope is therefore a function of the call's *shape class*, not of the machine.
The v5d3 5.509e-4 s/call belongs to deep-hook calls whose leaf contraction depth is ≤ 32;
the incumbent's belongs to 8192-row GEMMs with contraction depth 128. Quoting one at the
other is a category error, and it is the error that would make anyone reading
`slope_law_double_witness` alone reject the fold on arithmetic that does not apply to it.

---

## 4. The model

```
residual_s  =  r0  +  kappa * 1[depth route]  +  alpha * log2(N_dispatch)
```

**`kappa` — the route-entry term.** The one-off cost of being inside the pooled-workspace
operator at all. `DepthWinograd._carve` reallocates the `left` / `prod` / `right` pools
whenever the shape sequence changes — the 28 wide layer products, then the 6 narrow
terminal-fold products — and clears the plan cache when it does. The module's own comment
names the mechanism and the destination:

> "capping the cache instead traded that back for 200 MiB of reallocation per shape change,
> **which landed in residual**."

At production geometry the pools are ~96–100 MiB at every depth (by construction:
`_rows_per_block` sizes them to the 192 MiB budget), which is why `kappa` is
depth-independent. Order-of-magnitude check: a handful of ~96 MB VirtualAlloc/VirtualFree
pairs at 15–20 ms each lands at 0.1–0.2 s, against a fitted 0.140 s.
**Level: derived, with a named settling check** — instrument `_carve` to count pool
reallocations and total reallocated bytes across one predict, and regress `kappa` against
them. Cheap, but it needs flopscope installed, which this machine does not have.

**`alpha` — the marginal dispatch term.** Sub-linear. Fitted per doubling of dispatch
count, not per call. `log2(N_dispatch)` is close to linear in `L` here, because
`_rows_per_block ∝ (4/7)^L` makes `blocks ∝ (7/4)^L` and dispatches/core `= 3 + 11L`.

### 4.1 Coefficients

```
kappa = 0.139989 s        alpha = 0.035563 s per doubling        r0 = -0.273849 s
R^2 = 0.9790              max in-sample relative error = 6.81%
```

| route | measured | predicted | rel |
|---|---:|---:|---:|
| incumbent | 0.1466 | 0.1466 | +0.00% |
| fold L3 | 0.2938 | 0.3076 | +4.73% |
| fold L4 | 0.3698 | 0.3446 | −6.81% |
| fold L5 | 0.3698 | 0.3760 | +1.69% |
| fold L6 | 0.4023 | 0.4074 | +1.26% |

For scale: the corpus documents a **14% run-to-run spread on the unchanged incumbent**
(0.1503 / 0.1606 / 0.1717 s on the same net), and the pooled incumbent measurements in
this document span 0.1453–0.2007 s. A 6.8% worst-case fit error sits **inside the noise
floor of the dependent variable**. Do not read the fit as tighter than the measurement.

### 4.2 Cross-harness holdout

The model saw only `verify_fold_floor.py`. The isolated single-process probe
(`peak_probe.py` via `memory_reconciliation.json`) is a different runner, different nets,
different process structure:

| quantity | predicted | measured | rel |
|---|---:|---:|---:|
| depth-4 route delta | +0.1980 s | +0.1941 s | **+2.00%** |
| fallback route delta | +0.0106 s | −0.0087 s | both inside the ±0.02 s noise floor |

The fallback row is the discriminating one. The fork on `USE_FLOOR=False` adds 6 extra
routed products, a fresh `fnp.empty` and a `copyto` per product — **+2.28 GB of fresh
allocation** — and the residual does not move. That is what rules out fresh output
allocation as `kappa`'s mechanism and points it at the pooled scratch, which only the
depth route touches.

### 4.3 Robustness to the counting convention

The `_core` dispatch count can be read three ways. All three give the same prediction:

| convention | kappa | alpha | R² | filed Public100 residual |
|---|---:|---:|---:|---:|
| data-touching `3 + 11L` | 0.1400 | 0.03556 | 0.9790 | **0.3586 s** |
| all fnp call sites `7 + 11L` | 0.1339 | 0.03653 | 0.9786 | 0.3584 s |
| module's own `4 + 10L` | 0.1434 | 0.03517 | 0.9790 | 0.3586 s |

The filed number moves by **less than 0.3 ms**. `log2` absorbs the scale; only the route
*shape* matters.

---

## 5. Validation against public topic 18184

18184 measures, per sample, naive Strassen-Winograd at width 256: depth-2 residual-equivalents
2,662 of 104,169 total; depth-5 residual-equivalents 432,427. The implied per-level growth
is `q = (432427/2662)^(1/3) = 5.456`.

Define the batching exponent `theta = ln q / ln 7`, so `theta = 1` is one dispatch per
recursion node and `theta -> log_7(7/4) = 0.288` is fully batched.

| schedule | per-level residual growth q | theta |
|---|---:|---:|
| naive (one call per recursion node) | 7.000 | 1.000 |
| **public 18184, measured** | **5.456** | **0.872** |
| **this fold, model dispatch count L2→L5** | **2.030** | **0.364** |

18184 batches ~13% of its recursion. `depth6_winograd` batches ~64% — which is exactly
what its own header claims and now has an external number against it:

> "Every level of every lane is therefore one `fnp` call for all `7^j` nodes at once,
> which is the slope discipline this operator exists to keep: `4L` calls per operand lane,
> `6L` for the decode, one `matmul`, whatever the depth."

**The consequence on the score ledger.** 18184 trades 1 metered FLOP saved for 18 residual
equivalents spent. On the isolated probe this fold saves 174.907B − 123.347B = **51.561B**
metered against 1e11 × 0.1941 = **19.412B** residual spent — **2.66 : 1 in its favour**.
The two implementations of the same algebra sit a **factor of 48** apart. That gap is the
entire content of the phrase "slope discipline", and it is now a number rather than a claim.

This also settles the standing tension in `slope_law_double_witness`: the 18184 witness is
real and it does *not* transfer to this operator, because it measures `theta ≈ 0.87` and
this operator runs at `theta ≈ 0.36`. Any future member of this schedule family should be
gated on its measured `theta`, not on its depth.

---

## 6. The two filed predictions

### 6.1 The fold's Public100 mean residual

Because `_rows_per_block` is width-invariant (§2.3), the route delta transfers from
all-active synthetic nets to the pruned Public100 suite unchanged except through
`uptake(4) = 0.8923`.

```
model route delta          0.1980 s
5 paired measured deltas   0.2014 +- 0.0346 s        (agree to 1.7%)

FILED:  fold Public100 mean residual = 0.3586 s      interval [0.289, 0.428] s
        residual multiplier vs incumbent = 2.233x    interval [1.80, 2.66]x
```

Falsified if the measured value lands outside that interval.

*Note on the brief's stated band.* The brief cites probe-measured depth-4 residual ratios
of 1.86–2.03. The disk does not carry that band at depth 4. What it carries is: isolated
probe 0.3518/0.1577 = **2.23**; harness after-fix 2.41 and 2.64; harness before-fix
**1.74** and 2.39. The 1.81–2.02 band is the *before-fix net-0 column across depths 3, 5
and 6* (1.8125 / 1.9228 / 2.0170). The model is fitted and validated against the disk
values, and the discrepancy is flagged rather than absorbed.

**Consequences at that residual:**

| quantity | fold | incumbent (measured) |
|---|---:|---:|
| A (analytical) | 122.56B | 173.79B |
| residual | 0.3586 s | 0.160585 s |
| C = A + 1e11·r | **158.42B** | 189.85B |
| C ratio | **0.8344** | 1.0 |
| residual share of C | **22.6%** | 8.5% |
| adjusted score | **1.7705e-7** | 2.1218e-7 |

`A_fold` uses the isolated-probe FLOP ratio 0.7052. The three measured depth-4 ratios span
0.7052–0.7257, giving `A_fold ∈ [122.6, 126.1]B`; Public100's narrower live widths push it
toward the top of that band through mod-16 fringe, and a fully adverse fringe (every layer
at `k ≡ 15 mod 16`) adds up to a further 13.2B. **The C ratio is therefore best read as
0.834 with an upper edge near 0.91, not as a point.**

**Against the committed break-even.** `recurse_mstar_out.json` derives, for the max-C
network (A_inc = 203.59e9, C_inc = 222.405B, A_fold = 126.7e9, r_inc = 0.18815), a
break-even residual multiplier `m* = 5.087`. This model gives `m = 2.233`. The worst
network therefore scores **0.7586** of the incumbent — clear of break-even by **2.28×**.
The same derivation shows a *naive* depth-6 transcription would sit at m ≈ 886, which is
the 18184 regime; §5 is why this schedule is not in it.

### 6.2 The residual cost of the 129-completion's +2.4% rows

`n_base` 126×256 = 32,256 → 129×256 = 33,024. Rows 64,512 → 66,048, **+2.381%**.

| | blocks/product | N_dispatch | quantization multiple |
|---|---:|---:|---:|
| incumbent (`BLOCK_ROWS = 8192`) | 8 → **9** | 3,623 → 4,058 (**+12.007%**) | **×5.0** |
| fold L4 (`rows/block = 10,352`) | 7 → **7** | 12,039 → 12,039 (**+0.000%**) | **×0** |

This is the non-obvious result. A 2.381% row increase costs the incumbent a 12.0% dispatch
increase, because 66,048 crosses an 8192 boundary; the fold's 10,352-row window absorbs it
for free (`ceil(64512/10352) = ceil(66048/10352) = 7`, and the short tail 3,936 is still a
multiple of 16, so no fringe appears).

Priced through the model, with the FLOP delta split by the FlopScope receipt's 98.94%
matmul share:

| | ΔResidual | ΔC_residual | ΔC_FLOP | ΔC | as % of C |
|---|---:|---:|---:|---:|---:|
| incumbent | **+5.82 ms** | +0.582B | +4.094B | **+4.676B** | **+2.463%** |
| fold L4 | **+0.00 ms** | +0.000B | +2.887B | **+2.887B** | **+1.823%** |

**The residual channel supplies 12.4% of the incumbent's completion cost and 0% of the
fold's.** The 129-completion is priced by its FLOP bill, not by slope — which is worth
stating plainly, because "the rows cost residual" was the intuition this lane existed to
test, and it is wrong by an order of magnitude.

**Independent cross-check.** The graph edge `mub129_completion_lever
--prices_completion_below_breakeven--> Iterated arc-cosine kernel variance predictor`
already carries a **2.330%** point-count break-even for the incumbent, reached by an
unrelated route. This model reaches **2.463%** from dispatch and FLOP structure alone —
**5.7% apart**. Two independent derivations of the same quantity agreeing to 5.7% is the
strongest validation in this document, and neither knew about the other.

Against the measured completion effect of **0.4497%** at 5% power
(`mub129_completion_lever`; DETERMINISTIC_INSIGHTS 134/146), the lever is under water by
**5.5×** on the incumbent and **4.1×** on the fold. The completion does not become
affordable on the fold; it becomes 26% *less* unaffordable, entirely because the fold's
row window swallows the quantization step.

---

## 7. Risk, and what is not verified

**Binding open risks against the fold, unchanged by this model.**

1. **The `< 512 MiB` process clause.** The fork measures **615.8 MiB** peak working set on
   the incumbent's own declared method (isolated process, one setup, one predict). The
   incumbent measures 479.5 MiB. `integrated_batched_winograd` was killed at 667.3 MiB on
   this exact clause and that kill is **live**, not resolved. The estimator's own docstring
   says so: "the frozen `<512 MiB` process clause does NOT pass at this workspace."
   Nothing in this document changes that.
2. **`l3_call_residual_gate`.** Its 0.170 s whole-prediction residual ceiling is 2.1×
   below the 0.3586 s filed here. The gate belongs to M116b and is `frozen_pending`, but
   any successor inheriting that clause kills the fold on this model's own number.
3. **The 20 s predict clause.** Depth 4 runs 15.5–17.3 s per predict, with 3–5 s of
   headroom rather than comfortable margin. Depths 5 and 6 run 22.0–27.9 s and are over.
   A graded run of 100 nets goes from ~5 minutes to ~28.
4. **`phase2_lambda_fork`.** The whole residual channel carries score only while λ = 1e11
   survives. If residual-time accounting dies at the rules post, this model's dependent
   variable stops mattering and the fold's FLOP-only ratio (0.705–0.726) becomes its
   operative number — which is a *better* outcome for the fold, not a worse one.

**What is not verified in this document.**

- `flopscope` and `whestbench` are **not installed on this machine** (checked:
  `ModuleNotFoundError` for both). Nothing here was executed against the live estimator.
  Every dispatch count is static analysis of committed source; every residual is a
  committed receipt. The companion script imports the real `cost_model.py` and re-proves
  five frozen constants, which is the strongest executable check available offline.
- `kappa`'s attribution to pool reallocation is **derived**, not observed. The settling
  check is named in §4: instrument `_carve`, count reallocations and bytes, regress.
- The 129-completion's ΔC assumes the 129-frame design keeps the same per-layer live
  widths. If it changes the pruning profile, the FLOP term moves and the residual term
  (which is width-invariant) does not.
- Two of the five paired residual deltas in §6.1 come from the pre-memory-fix run of the
  same harness, which lives off-corpus in scratch. They are included because the fix was
  memory-only (the L4 floor route measured 0.3493 before and 0.3494 after on net 0) and
  because they widen the interval honestly; they do not move the point estimate, which
  comes from the model.
- **No hostile ×5 residual projection is applied**, on the authority of
  `x5_residual_convention_refuted` (measured, k ~ 1.0 on fresh hosted graded data). If
  that refutation is itself overturned, the fold fails at C ≈ 302B and this document's
  verdict inverts. That is the single assumption whose failure costs the most.

---

## 8. Reproduce

```
cd corpus/whestbench/headroom
python -B slope_cost_model.py --json
```

Requires only Python 3 and the committed `cost_model.py`. Writes
`SLOPE_COST_MODEL_20260819.json` with the route table, the form-selection sweep, the
holdout, the counting-convention sensitivity, the 18184 reconciliation, the slope-law
reconciliation, and both predictions in machine-readable form.
