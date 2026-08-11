# Gen-8 gate audit — verification of the proposed WIDTH-TRANSFER GATE

Date: 2026-08-10. Read-only audit. Writes confined to this directory. No git
operations, no submissions, no champion access, synthetic artifacts only.

**Proposal under audit** (commit `ad04e4a`, `GRAVEYARD_RUN.md` Finding 1):

> Before a screen result may promote, the mechanism's captured-signal statistic
> must be measured at **≥ 2 widths**, and its extrapolation to n = 256 must be
> non-vanishing.

**Verdict: do not adopt as written.** One of the six cited corpses is
width-caused; five are not. The gate's clause 1, applied to today's ledger,
would block ten promotion-eligible records whose single measured width *is* the
production width 256 — it fails the strongest evidence class in the corpus while
catching one failure mode that the corpus already catches by other means.

---

## Deviations, recorded first

1. **The ledger moved under the audit.** The task named 261 records; the file
   now holds **263**. A parallel session is appending `gen8_*` records. All
   Task-2 counts are pinned to
   `fold_ledger.json` sha256 `60c9c72a4aa64caebfe208ef63ca62906e0dc7dace48de81eed9846fac8189be`,
   546,363 bytes, 263 candidates. The two added records are both `killed` and
   change no promotion-eligible count.
2. **Corpse identification is by number-matching, not by id.** The graveyard's
   table names corpses in prose. Ids were recovered by matching its quoted
   numbers (`0.997502`, `8.8716`, `0.04738`, `2.475%`, `3.01e-15`) against the
   ledger; the mapping is recorded per corpse below and in `audit_results.json`.
3. **One confirmed width false positive.** `gm_u3_grid`'s "48" is the size of
   the empirical rotation pool (`build_pool_spec("empirical48")`), not a network
   width. `gm_u3_grid` has no width parameter. The machine output retains the
   raw extraction; this document corrects it.
4. **Task-3 scope.** 522 `.py` files under `corpus/whestbench/experiments`.
   `m245_*`, `m243_*`, `m244_*` were scanned but excluded from the finding set
   per the no-touch instruction; their hits are OS-portability guards
   (`st_file_attributes`, `O_BINARY`, `orig_argv`), not measurement defects.

---

## Task 1 — the six corpses

Tally: **1 CONFIRMED width-caused, 5 NOT width-caused, 0 indeterminate.**

The decisive check is mechanical and re-derivable: for four of the six, the
"screen" statistic and the "production" statistic are two aggregate fields of
**one file**, over **one set of eight cases**, all at **width 64**. Width was
never varied, so it cannot be the discriminating variable.

### C1 — Gate-aligned scalar split → `latent_gate_aligned_split` — **NOT width-caused**

Artifact `work/scorefloor_generation/latent_gate_split/fresh_n64_results.json`:
`cases` = 8, `MEASURED case widths` = **[64]**, depths [16, 32].
`aggregate.wins` = 8 and `aggregate.ratio` = 0.9975024218012577 are **fields of
the same object**. Width 256 appears in that file only under
`cost_accounting: {width: 256, depth: 32}` — a projected shape-billed
arithmetic model, not a measurement.

Record text: kill_condition *"n=64 aggregate ratio above 0.8, fewer than 6/8
wins, … or conservative target arithmetic at least 80B"*; result *"improved all
8/8 n64 cases, but aggregate ratio 0.997502 missed the <=0.8 materiality gate by
about 80x in effect size."*

It died of **effect size at the screen width**, inside its own predeclared
conjunction. There was no production rung and no promotion to prevent.

### C2 — RB conditional marginals → `latent_gate_rb_marginals` — **NOT width-caused**

Same shape: 8 cases, widths [64], `wins` = 8 and `ratio` = 0.9975023609978109 in
the same aggregate. Result: *"ratio 0.997502361 was only 6.08e-8 better than its
parent."*

The report *does* offer a width mechanism — *"the high-dimensional dilution law
in concrete form: … only `O(1/n)` variance into any one neuron"* — but that is
an interpretation of a **single-width** measurement (T explains 1.0304e-4 of
each coordinate's variance at n=64). No width law was measured here. The
mechanism story is width; the death was effect size at one width.

### C3 — q3 response-Gram recursion → `latent_gate_response_gram` — **NOT width-caused**

8 cases, widths [64], `wins` = 8, `ratio_to_baseline` = 0.9975023396798792, one
file. Result: *"passes PSD, n64 symmetry, 71.494B cost, and 8/8 wins versus
fullcov, but ratio 0.997502340 misses materiality."*

### C4 — Radial susceptibility compressor → `randomized_radial_susceptibility_compressor` — **NOT width-caused**

`one_step_results.json`: 24 states, **all at width 64**. The 8/8-versus-11/24
split is a **depth/layer** split, re-derived from the artifact:

| cell | wins |
|---|---|
| depth16 layer0 | 4/4 |
| depth32 layer0 | 4/4 |
| depth16 layer8 | 0/4 |
| depth16 layer14 | 1/4 |
| depth32 layer16 | 2/4 |
| depth32 layer30 | 0/4 |

The report says so in as many words: *"The result is sharply depth dependent."*
A width gate does not see this axis at all.

### C5 — Full-covariance 2n sigma mixture → `latent_full_sigma` — **NOT width-caused**

8 cases, widths [64], `wins` = **1**, `ratio` = 8.871600739504565. The
graveyard's "screen result" cell for this row is *"covariance matched to
3.01e-15"* — a **structural** covariance-recovery witness on the same
`n=64,L=16,seed=18560` member, not an accuracy screen at another width. Record:
*"Kill this one-frame sigma implementation; preserve the proof that … matching
second moments is insufficient because ReLU gate/angular structure is aliased."*
Cause: **angular/gate aliasing**, an information-content defect.

### C6 — Weight-identified latent q3,r2 → `weight_identified_latent_factor` — **CONFIRMED width-caused**

This one is real and it is the only one.

- Screen: `latent_factor_closure/premise_results.json`, case widths **[4, 8, 16]**,
  aggregate ratio 0.04738, 6/7 wins → `"survive_premise"`.
- Kill: `latent_factor_closure/adversarial_width_sweep.json`, groups at widths
  **[32, 64]** — (32, L16) 0.5606/5-of-6 wins, (32, L32) 0.9169/4-of-6,
  (64, L16) **2.9281 / 0 wins**, (64, L32) **1.5959 / 0 wins**.
- Mechanism measured across widths: top-two trace fraction
  4→0.8838, 8→0.6168, 16→0.3730, 32→0.2146, 64→0.1144, 128→0.0586, **256→0.0302**
  (16 fresh first-layer matrices per width).

Record: *"q=3,r=2 passed the original small-width premise but failed the
adversarial width law: 0/8 wins at n=64 … Top-two trace capture collapses from
88.4% at n=4 to 3.02% at n=256."*

Note what this corpse actually argues. The width sweep **already exists** — the
adversarial audit ran exactly clause 1 and clause 2, just *after* the premise
pass rather than before. C6 licenses *moving an existing practice earlier*, not
adding a new instrument. The audit also recorded a co-cause the gate would not
see: at the first layer, where the preactivation is exactly Gaussian,
`q3,r2` had max-abs error 0.01683 against fullcov's machine-zero — a bias
defect independent of width.

### Two collateral corrections to Finding 1

- **The "8/8 signature" holds for 3 of 6 rows, not 6.** By the graveyard's own
  table, C4 is "layer-0 8/8", C5 is a covariance witness (1/8 wins overall), and
  C6 is 6/7 at small width. The claimed cluster of six of "exactly that shape"
  is three.
- **"Kill conditions name widths 3, 4, and 64. None names width 256"** is true
  of the GEN6 atlas as scoped (5 of 223 records name width 64, none 256), but
  the base rate makes it thin: **218 of 223 kill conditions name no width at
  all**. In the fold ledger the same scan finds one kill_condition that *does*
  name 256 — `gm_latent_cubature`: *"conservative n=256,L=32 target arithmetic
  at least 80B."* The inference "gates are written at screen width" is not
  carried by width-silent text.
- **Finding 2 is confirmed, and it explains C1–C3.** The three corpses' baseline
  sums are bit-identical: `baseline_mse_sum = 0.0068680758149980555` in all
  three artifacts. Same comparator, same eight-case bank, same untouched parent
  term — which is exactly why the ratios agree to seven figures. The resolution
  rule Finding 2 proposes is the instrument these corpses call for.

---

## Task 2 — our own exposure

Pinned snapshot: 263 candidates. Promotion-eligible statuses (screened /
promoted / validated / survivor / component-pass / phase-A-pass): **60 records**.

### Records whose supporting measurement is not at width 256 — **8 genuine**

| id | status | measured widths |
|---|---|---|
| `conditional_corr_spectrum` | screened | 16 |
| `conditional_residual_cumulant_spectrum` | screened | 8, 16 |
| `conditional_residual_covariance_algebra` | screened | 8, 12, 16 |
| `cumulant_polynomial_quotient` | screened | 8, 16 |
| `m86_boundary_laplace_coarea` | phase_a_pass_phase_b_unresolved | 2, 3, 4 |
| `m126_repeated_output_source_contraction` | repair_blocked_independent_component_pass | 64 |
| `m198_source211_delay_one_adapter` | screened | 2–7 |
| `m200_streaming_overlap_fixture` | component_pass_streaming_semantics | 4, 7 |

(`gm_u3_grid` was flagged by the extractor and is a false positive — see
deviation 3.)

Of these, the four `conditional_*` / `cumulant_*` records are the ones the
proposed gate genuinely targets: their captured-signal statistics (rank-four
off-diagonal energy 0.9935 at n16; k3/k4 fidelity 0.9840–0.9940 at n8/n16;
coefficient identifiability *"locally identifiable … for n12/n16 but not
uniformly at n8"*) are fidelity fractions measured only in the screen band.
`m86`, `m198`, `m200` and `m126` are algebraic/structural conservation checks
(ownership conservation, streaming semantics, sector-integration identities)
where small width is the *point* of the fixture, not a shortcut.

### Records that would FAIL the ≥2-width clause — **14**, and this is the problem

**Ten of the fourteen fail it while measured at width 256 itself:**

`row_blocked_winograd` (screened), `row_blocked_winograd_production`
(**promoted**), `ple_flash_sidecar` (screened), `m80_kerdock_tangent_factorial`,
`m82_kerdock_vs_haar_variance`, `m156_extended_domain_star_control`,
`m172_selective_22_owner_fusion`, `wc1_winner_ablation_map`,
`v31_guards_m186_m187` (**validated**), `s12_finite_width_kernel_capstone`.

A promotion gate that rejects a record measured **at the production shape** for
not also having been measured somewhere else is inverted. `h4_random32256`, the
promoted champion component, has no width parameter at all and would sit
outside the gate entirely.

### The four REVIVED_SCREENED items

| id | width evidence | gate outcome |
|---|---|---|
| `gm_rankone_bill` | static bill pinned at **n = 256, layers = 31** (its own mechanism text), plus float32-parity identities at w = 3/4/5 and an n=256 He-scale compile check | **PASSES both clauses.** It self-declares width-256-specific in the *favourable* direction: its evidence is at production width. Demanding a second width would mean pricing a bill at a shape the task never runs. |
| `gm_c1_bound` | none — the measured object is a calibration constant R over 22 nets | **gate inapplicable** |
| `gm_u3_grid` | none — "48" is a rotation-pool size, not a width | **gate inapplicable** |
| `gm_u9_s4_d2` | none — suite-level tail/portfolio model | **gate inapplicable** |

Three of the four newest survivors have no width parameter, and the fourth is
already at 256. The gate as written would not have touched any of them.

---

## Task 3 — the M183 defect class

**Ground truth from the pinned venv.** `flopscope 0.10.0+np2.4.6` `OpRecord`
fields: `op_name, subscripts, shapes, flop_cost, cumulative, namespace,
flopscope_context_start_offset_s, flopscope_backend_duration_s,
flopscope_overhead_duration_s, resolved_dtype`. On a live record,
`hasattr(op,"dtypes")` is `False` and `hasattr(op,"name")` is `False`.

Scan: 522 files. 62 `getattr`-with-falsy-default sites, 991 reducer-over-
comprehension sites, 176 raw attribute-name mismatches, 55 token-in-source
detectors, 2 dead-name reads, 0 cross-artifact `.get` with an unknown key. These
were intersected with an empirical filter — 109 artifacts carrying a
zero-valued measured statistic — and each survivor was traced to its detector.

### Confirmed structurally void: 1

**`m183_f32_hotpath/run_m183_falsifier.py:58`**

```python
dts = getattr(op, "dtypes", None) or ()
names = [str(getattr(d, "name", d)) for d in (dts if isinstance(dts, (list, tuple)) else [dts])]
if any(("float64" in n) or ("complex" in n) for n in names):
```

All three sub-patterns at once: a `getattr` whose default is falsy, an `any()`
over the resulting empty tuple, and an attribute name that does not exist on the
installed API. `f64_share` could only ever be `0.0`.

Empirical verification, run this session in the pinned venv against a fixture
that is **100% float64 by construction** (two chained 256×256 matmuls,
`resolved_dtype` = `float64` on every op, 1.33955584e8 billed):

| detector | f64 billed | f64 share |
|---|---|---|
| suspect (`dtypes`) | 0.0 | **0.00%** |
| corrected (`resolved_dtype`) | 133,955,584 | **100.00%** |

Line 62 carries a second dead name, `getattr(op, 'name', '?')` — the field is
`op_name` — masked because the guarded branch never executes.

**Citations.** Fold ledger `m183_f32_hotpath_falsifier`: *"KILLED: f64-lane
billed = 0.0000e0 of 1.5803e11 total (0.00%)."* `PHASE1_WRITEUP_DRAFT_20260808.md`
line 129: *"M183 | float32 hot-path recast (the 'free 2x') | 0.00% f64-lane
billing — already clean | killed"*; and line 422, load-bearing: *"the fidelity
family formally retired the dtype-repricing escape (M183 measured the f64 SHARE
at 0.00%, which is invariant to how f64 is priced)."* Today's ledger record
`gen8_m183_detector_void` already retracts the figure; this audit reproduces its
claim independently (structural field list from the venv + the positive-fixture
run above) and confirms it.

The corpus already knew the correct name: `u2_fold3cap_bound/calib_summary_cost.py`
constructs `B.OpRecord(..., resolved_dtype="float32")`.

### Same shape, positive-capable — 7 (each cleared by a firing check)

| # | site | why it is not void | cited in |
|---|---|---|---|
| 2 | `gm_a4_constraint/verify_two_signal.py:64` bytecode needle scan | fires: run against `capped_fold3.py` it returns `['_tally']`. (Two needles occur there only inside a comment — bytecode correctly cannot see comments.) | `a4_hostile_inputs_battery` (screened) |
| 3 | `gm_m179_m199/run_depth32_identity_trace.py:134` legacy-tag scan | fires on an injected `m200.legacy_rebuild.full_archive`; the same run also carries an independent monkeypatch `LegacyCallCounter`, and the histogram it scans has 21 real operations | **`gm_m179_m199`** — the record that licenses the whole width-gate proposal |
| 4 | `v31_guards/run_v31_gates.py:202` `getattr(est,"last_guard_report",None)` | gate G2 is an explicit positive control: `m186_empty_regime_fired: true` on `f_negshift`, `m187_finite_output_fired: true` with 164 nonfinite entries replaced on `b_gain_1e3` | **`v31_guards_m186_m187`** — the only `validated` record |
| 5 | `m184_trichotomy_upward/run_m184_g0.py` certain-on detector (0.00% reduction) | the same detector reports max per-layer certain-on **39** and certain-dead **37** inside the same artifact; the 0.00% is a measured negative | `m184_trichotomy_upward_g0`; writeup line 130 |
| 6 | `m177_bivariate_relu_primitive.py:167-168` `hasattr(...,"owens_t")` / `"multivariate_normal_cdf"` | full enumeration confirms the negative: `flopscope.stats` = {cauchy, expon, laplace, logistic, lognorm, norm, truncnorm, uniform}; `norm` = {cdf, name, pdf, ppf}; nothing in `flopscope.stats` or `flopscope.numpy` matches owen/multivar/bivar under any spelling | `m177_bivariate_relu_value_jacobian_primitive` (no-go). Conclusion stands; the instrument would not survive a rename. |
| 7 | `t3_fold3_deterministic_cap/run_t3_gates.py:204,265` `getattr(capped,"last_cap_report",None)` | fail-closed: `report is None` sets `g1["pass"] = False` and clears `completed` in G2 | `t3_fold3_deterministic_cap` (screened) |
| 8 | `terra_m153_pilot_reuse/...:97` `getattr(estimator,"pilot_reuse_trace",[])` | trace has 3 entries, `removed_shape_bill` = 589,840,384; and the blocking assertion `only_three_formal_dispatches_removed` is computed from matmul dispatch-call deltas, independent of this attribute | `m153_exact_formal_prefix_reuse` |

### Cleared, with reason

`gm_m116_streams/probe_cheap.py` (`op` is a local operator, not an `OpRecord`;
`differing_words = 0` has a `max_abs` cross-check) · `gm_s17_reuse`
(`rel_err_ratio_costfloor = 0` is a bitwise reproduction check; the ratios
themselves are 1.63/2.37/1.37) · `pb1/m191` (odd-degree `design_rms = 0` is exact
antipodal cancellation; even degrees are non-zero) · `gm_flatworm_response_ladder`
(14/24 exact-zero permutation errors, but the max is 6.90e-14 — the instrument
fires) · `wc1_winner_ablation` (`"A_frames" in arms` matches; derived ratios
populated).

### The antidote already in the corpus

`m217_balanced_three_color_strict_control/run_m217_native_trace.py:119`:

```python
"matmul_calls": int(matmul.get("calls", -1)),
```

A **loud sentinel** rather than a falsy default. An absent key produces `-1`,
which is distinguishable from a true zero. Adopting `-1`/`None` sentinels plus a
mandatory positive-control fixture for every detector closes this class in a way
a width gate never could.

---

## Recommendation

**A width-only gate is not sufficient, and it is not the right instrument for
five of the six failures it was drawn from.** Generalize it:

1. **Replace clause 1 with a transfer clause over the mechanism's own
   sensitivity axis, not a hard-coded width.** Of the six corpses, one died on
   width, one on depth, one on angular/gate aliasing, and three on effect size at
   the screen width. The predeclaration should name the axis the mechanism is
   expected to be sensitive to and require two points on *that* axis. As written,
   clause 1 blocks ten records measured at the production width and misses the
   depth axis entirely.
2. **Keep clause 2, restated as evidence-at-production-shape.** "Measured at
   n = 256, or extrapolated with a measured law to n = 256" is the clause that
   would actually have caught C6 — and C6 shows the corpus already runs it, just
   after the premise pass. Move it before, do not invent it.
3. **Adopt Finding 2's resolution rule alongside.** It, not the width gate, is
   what C1–C3 argue for: their baselines are bit-identical, so they were one
   measurement, not three.
4. **Add the instrument-validity gate this audit's Task 3 implies.** No detector
   may produce a promotion- or kill-bearing null unless it has fired on a
   positive fixture in the same run. M183 shows the cost of the alternative: a
   structural zero that reached a published write-up and retired a whole
   family. That gate is cheap, applies to every axis, and is the one the record
   demonstrably needed.

---

## Files

- `GATE_AUDIT.md` (this document)
- `audit_results.json` — assembled machine-readable verdicts
- `corpse_verdicts.json` / `audit_corpses.py` — Task 1
- `width_exposure.json` / `audit_widths.py` — Task 2
- `verify_hits_results.json` / `verify_hits.py` — Task 3 empirical verification
- `scan_m183_class.py`, `scan_raw.json` — static defect-class scan
- `scan_structural_zeros.py`, `structural_zeros.json` — empirical zero-statistic scan
- `scan_dead_names.py`, `dead_names.json` — dead-name scan
- `scan_token_detectors.py`, `token_detectors.json` — token-detector polarity scan
- `_installed_api.json` — flopscope/whestbench API surface read from the pinned venv
- `_ref_GRAVEYARD_RUN.md` — `git show ad04e4a:corpus/whestbench/core/GRAVEYARD_RUN.md`
- `assemble.py`
