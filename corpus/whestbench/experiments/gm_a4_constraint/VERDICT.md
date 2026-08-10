# VERDICT — gm_a4_constraint (revival of `a4_hostile_inputs_battery`, constraint leg)

**Result: KILL CONFIRMED AT STEP 0. The original record stands unchanged.**
Stage (b) was NOT run, exactly as the predeclared gate requires.

## DEVIATIONS (loud, top of file)

1. **One cosmetic harness fix after first execution.** The attack scan for `def _tally`
   initially matched its own source file (`verify_two_signal.py`), producing a spurious
   third entry. Fixed by excluding this directory; re-run is reported below. No gate
   number changed (the spurious entry was my own harness, and it also reported
   cap-present/fix-present, so it could not have flipped H1 either way).
2. **No other deviation.** Gates, arms, and numbers are exactly as predeclared in
   `PREDECLARATION.md`. No retuning after a failed gate. No arm was invented.
3. **Scope honestly bounded.** The mined stage-(a) arithmetic uses one specific residual
   source (U2's `budget_summary_dict` history scan). Whether the frozen v3 has some
   *other* history-growing residual source was NOT tested — it is outside the mined arm
   and I did not enlarge scope. Labeled as unmeasured, not as a surviving revival.

## 1. Predicted outcome, on record before running

`PREDECLARATION.md` §5: "I predict **stage (a) KILLS at step 0** and stage (b) is never
reached… the two addends are produced by two mutually exclusive estimator configurations,
so their sum is not a physically realizable C for any single net."

## 2. Observed — verbatim decisive numbers

Cost law (`fold_ledger.json:invariants.score_formula`, `whestbench/budget.py:14-51`):
`C = F + λ·R`, `λ = 1e11 FLOP/s`, `B = 2.72e11`, `C > B ⇒ budget failure ⇒ zero-prediction`.
B agrees across two independent sources (`u2_findings.json` and the ledger
`resource_ceiling` string): both `272000000000`.

### G0-A — arithmetic (the mined stage (a)): **PASSES, i.e. does not discriminate**

| quantity | value |
|---|---|
| A4 worst hostile net (`a_gain_1e-3`, mlp_seed 555001) billed F | **259,700,796,917** |
| F/B | **0.9547823416066177** (95.478 %) |
| A4-recorded headroom | 12,299,203,083 = **0.045217658393382355** (4.522 %) |
| A4-recorded `budget_breach` | `false` |
| U2 upper residual (K=100, single process) | **3.0e10** FLOP-equiv (= 0.30 s × 1e11); band [2.2e10, 3.7e10] |
| **SUM S = 259,700,796,917 + 3.0e10** | **289,700,796,917** |
| **S / B** | **1.0650764592536766** |

So the sum does exceed B. The arithmetic alone is *not* the discriminator, exactly as
predeclared. The discriminator is whether the two addends can co-occur on one net.

### G0-B — co-occurrence / regime coherence: **FAILS BOTH LEGS ⇒ KILL**

**B1 — is the residual source reachable from the path that produced F = 259,700,796,917?
NO.** A4's own traceback in `a4_results.json` names the frozen v3 at
`work/scorefloor_generation/kerdock_l1_owned_buffer/candidate_source_validator_v3/`.

- Static token count over all 6 `.py` files in that tree
  (`base_estimator, cost_model, estimator, fold3_estimator, fold_estimator,
  row_blocked_winograd`):
  `budget_summary_dict: 0`, `_tally: 0`, `summary_dict: 0`, `get_data(: 0`.
- Independent runtime check (import the estimator, walk the real first-party import
  closure, scan compiled code objects' `co_names`/`co_consts` recursively):
  closure = the same 6 modules, **`hits_union: []`**, `any_residual_source_reachable: false`.

**B2 — is F = 259,700,796,917 reachable in the regime that produces the residual? NO.**
The residual source lives only in `capped_fold3`, which enforces
`cap_billed_flops = 244.8e9` (= 0.9 B) by selecting `n_eff` such that
`C_pred(n_eff) <= cap` (`capped_fold3.py:256, 431, 439-443`).

- `259,700,796,917 > 244,800,000,000` — excess **14,900,796,917**.
- Independent MEASURED confirmation from `t3_gate_results.json`: capped metered F values
  `[242953633960, 244450742805, 227908524575, 243030949252]`, **max 244,450,742,805**
  (= 0.8987159661948529 B). A4's worst F exceeds that measured max by
  **15,250,054,112**. `a4_worst_F_reachable_under_cap: false`.
- The cap demonstrably binds on a would-breach net: G2's uncapped diagnostic metered
  **299,488,907,107** (`would_breach_B: true`) was trimmed `n_eff 39936 → 31232` to a
  capped metered **243,030,949,252`.

**Therefore the mined headline `289,700,796,917 = 1.065 B` is not a realizable C for any
single net under any configuration on disk.** It stacks an uncapped-frozen-v3 bill with a
cap-wrapper-only residual.

### G0-C — novelty of the only coherent variant: **FAILS ⇒ KILL**

The only coherent variant is a near-CAP net plus the same residual:
- from the source constant: `244,800,000,000 + 3.0e10 = 274,800,000,000 = **1.0102941176470588 B**`
- from the measured max: `244,450,742,805 + 3.0e10 = 274,450,742,805 = **1.0090100838419118 B**`

This is a breach — and it is **verbatim already-committed U2 content**
(`u2_findings.json:adjusted_delta.catastrophic_tail`: "near-CAP net (F/B~0.89) at suite
position K>=92 breaches C>B -> budget failure -> multiplier 1.0, zero-prediction…").
Moreover **U2's one-line fix is already on disk**: `capped_fold3.py:259-268` and
`package_source/estimator.py:260-268` both read
`get_active_budget().flops_used` (O(1) live read), with the U2 bound cited in the comment.
`u2_one_line_fix_already_on_disk: true` for both files. The 3.0e10 history residual does
not exist in the current code.

## 3. Attack pass (strongest counter-hypotheses, tested specifically)

- **H1 — an UNCAPPED estimator that also calls `_tally`, letting both addends co-occur.**
  Repo-wide scan: exactly **2** files define `_tally`
  (`t3_fold3_deterministic_cap/capped_fold3.py`, `.../package_source/estimator.py`).
  Both declare `cap_billed_flops = 244.8e9` and both carry the U2 fix.
  `any_uncapped_tally_caller: false`. **H1 does not land.**
- **H2 — the cap's cost model under-predicts enough for metered F to reach 259.7e9.**
  Observed `metered/predicted − 1` across all four T3-gate nets:
  `[3.5205750898e-05, 3.4992781041e-05, 3.7524251956e-05, 3.7380945147e-05]`,
  max **3.7524251955689536e-05** (0.00375 %). Under-prediction required to reach A4's
  worst F under the cap: **0.0608692684517973** (6.087 %) — a factor
  **1622.1314291268136** larger than the largest miss ever observed. **H2 does not land.**

## 4. Two-signal verification

| signal | independent of | result |
|---|---|---|
| S1: every ratio recomputed in a fresh pinned-python process from the primary committed JSON (`a4_results.json`, `u2_findings.json`, `fold_ledger.json`), never from the mining record's prose | the mining record | all quoted numbers reproduce; B agrees across two sources |
| S2a: runtime import-closure + bytecode `co_names`/`co_consts` scan | the static text grep | `hits_union: []` over the true 6-module closure |
| S2b: MEASURED capped F from `t3_gate_results.json` | the source constant `244.8e9` | max measured 244,450,742,805 < 259,700,796,917 |
| S2c: bit-repeat of `run_step0.py` | — | `results.json` sha256 identical across runs: `2025a069aee18d7d459f9b1466ba5cadcd7bbeeb617099ab888bd1c37774643a` |

## 5. What the original record got right, and its one real (unexploited) limit

A4's committed constraint is an **F-channel** statement — "pruning-hostile nets *bill* up
to 95.5 % of B … before any mutation that adds *billed* work" (`A3_A4_NOTES.md:106-110`) —
and U2's own table rules the residual "charged to billed FLOPs? **NO — exactly 0**"
(`U2_FOLD3CAP_BOUND.md` §2). The changed premise opens a different channel and does not
touch what A4 measured; U2 explicitly *extends* the cap constraint rather than retiring it.

The mining record's *framing* claim is nevertheless correct and worth recording:
A4 recorded no residual seconds at all (`a4_rows_record_residual_seconds: false`; its
regime was cold subprocesses, `subprocess_walls_s [12.0, 11.2]`), so "4.5 % worst-case
headroom" is an F-only statement and should be quoted as such. That is a labeling
correction to the record, not an invalidation, and it buys no mutation.

## 6. Files

- `PREDECLARATION.md` — written before any code
- `run_step0.py` → `results.json` (step-0 gates, bit-repeat verified)
- `verify_two_signal.py` → `verify_results.json` (signals 2a/2b/2c + attack)
- `VERDICT.md` (this file)

Firewall honored: synthetic/committed artifacts only; no estimator `predict()` was ever
called; no truth, scorer, private, or holdout read; no submission, network, or git; all
writes confined to this directory; `m243_*/m244_*/m245_*` untouched.
