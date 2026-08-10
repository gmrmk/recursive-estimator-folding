# PREDECLARATION — graveyard revival gm_a4_constraint

Written BEFORE any code is run. Search key: `a4_hostile_inputs_battery`.
Work dir: `corpus/whestbench/experiments/gm_a4_constraint/` (writes confined here).
Pinned python: `work/whest-v014/Scripts/python.exe`. No network, no submissions,
no truth/scorer/private/holdout reads, no git, no touch of m245_*/M243/M244.

## 1. The record under revival

`a4_hostile_inputs_battery` (fold_ledger.json, status `screened`). Its CONSTRAINT leg,
verbatim from the ledger `result` and `A3_A4_NOTES.md:106-110`:

> pruning-hostile nets bill up to 95.5% of B (4.5% worst-case headroom) -> ANY mutation
> adding billed work (incl. the M185 pruning guard) MUST carry the T3 deterministic cap.

Committed supporting number (a4_results.json, net `a_gain_1e-3`, mlp_seed 555001):
`billed_flops = 259,700,796,917`, `budget = 272,000,000,000`, `budget_breach = false`.

## 2. Mined revival mechanism (what I am testing, not advocating)

- **changed_premise:** U2 (`experiments/u2_fold3cap_bound/`, resolved 2026-08-10).
  `capped_fold3.py::_tally()` calls `flopscope.budget_summary_dict()`, which adds
  **exactly zero** to billed F but lands in the scored residual channel `lambda*R`
  and grows with process history — up to ~0.30 s / ~3.0e10 FLOP-equivalent (~11% of B)
  on the last nets of a single-process suite. A4's regime was COLD subprocesses, one
  net per run, so it is structurally blind to that channel.
- **revival_mechanism:** re-open A4's constraint leg in the graded (warm, single-process)
  regime and add a third M186/M187-shaped guard (read measured live headroom immediately
  before the final billed op; degrade to analytic means rather than breach).
- **expected_gain (on record, verbatim):** "A4's worst hostile net plus U2's measured
  residual = 289,700,796,917 = 1.065 B, a breach. Worse, a net sitting exactly at the
  T3 CAP (0.90 B) plus the same residual = 1.0103 B — the cap itself does not protect."

## 3. Governing equation / quantity

From `fold_ledger.json:invariants.score_formula` and `whestbench/budget.py:14-51`:

```
C   = F + lambda * R_sec ,  lambda = 1e11 FLOP/s
B   = 2.72e11
s_m = mse_m * max(0.1, C/B)
C > B  =>  budget failure  =>  zero-prediction  =>  s_m = mse(zeros)
CAP = 0.90 * B = 2.448e11   (T3 deterministic cap)
```

## 4. Cheapest falsifier, exactly as mined (two stages, no enlargement)

**Stage (a) — 30 seconds, zero compute.** The breach arithmetic
`259,700,796,917 + 3.0e10  vs  2.72e11`.
Mined claim: this "already falsifies A4's '4.5% worst-case headroom' as a graded-regime
statement".

**Stage (b) — one warm-process billing sweep, ONLY IF (a) leaves it alive.**
Instantiate 100 synthetic He nets sequentially in ONE process under frozen v3.1 +
capped_fold3 and record `C_i = billed F + lambda*R` by position.
- KILL the concern if C/B is flat by position AND max <= 0.955.
- CONFIRM (build the guard) if C/B rises with position AND any net at position >= 90
  crosses B.

## 5. Predicted outcome, ON RECORD, before running

I predict **stage (a) KILLS at step 0** and stage (b) is never reached. Reason predicted
in advance: the two addends are produced by two mutually exclusive estimator
configurations, so their sum is not a physically realizable C for any single net. I
commit to this prediction now and will report the opposite plainly if the evidence says
otherwise.

## 6. Exact gates (step 0), all two-sided

- **G0-A (arithmetic).** Compute `S = 259,700,796,917 + 3.0e10` and `S/B`.
  KILL if `S <= B`. Alive if `S > B`. (Predicted: S = 289,700,796,917 = 1.06507... B,
  so G0-A is expected to pass — the arithmetic alone is not the discriminator.)
- **G0-B (co-occurrence / regime coherence).** The two addends must be producible by ONE
  estimator configuration on ONE net. Mechanical checks, both required:
  - (B1) The residual source `budget_summary_dict` must be reachable from the code path
    that produced `F = 259,700,796,917`. Test: repo grep for `budget_summary_dict` /
    `_tally` and a read of the FROZEN v3 estimator source A4 actually invoked
    (`candidate_source_validator_v3/`). If the frozen v3 path never calls it, addend 2
    cannot occur in the regime that produced addend 1.
  - (B2) If the residual source lives only in `capped_fold3`, then under `capped_fold3`
    F must be able to reach 259,700,796,917. Test: read the cap enforcement in
    `capped_fold3.py` and check whether `F <= CAP = 2.448e11` is enforced. If it is,
    `F = 2.597e11` is unreachable in the regime that produces addend 2.
  - **KILL at step 0 if (B1) fails AND (B2) fails**, i.e. no single configuration can
    produce both addends. Alive if either holds.
- **G0-C (novelty).** If the ONLY coherent variant is `F = CAP = 2.448e11` plus the same
  residual = `2.748e11 = 1.0103 B`, check whether that statement is already committed in
  U2 (`U2_FOLD3CAP_BOUND.md` section 4 catastrophic tail, `K >~ 92`) and whether U2's
  one-line fix is already on disk / validated. If yes to both, the revival is
  re-litigation of a resolved uncertainty, not a new invalidation: **KILL**.
  Alive only if the coherent variant is NOT already committed or the fix is absent.

Stage (b) runs **only** if step 0 leaves the candidate alive on G0-B and G0-C.

## 7. Two-signal verification (required before any verdict)

1. Independent recomputation of every quoted ratio directly from the primary JSON
   (`a4_results.json`, `u2_findings.json`, `fold_ledger.json`) in a fresh process —
   not from the prose numbers in the mining record.
2. Mechanical source evidence for G0-B: grep counts + line-cited reads of the installed
   frozen v3 and `capped_fold3.py`, i.e. the installed artifact rather than any
   document's description of it.

Neither signal can be fooled by the other: (1) is arithmetic on committed data, (2) is
code reachability.

## 8. Kill condition for the WHOLE revival (stated once, honestly)

The revival is KILLED (record STAYS DEAD / constraint stands) if step 0 shows the mined
breach arithmetic is not realizable on one net AND the only realizable variant is
already-committed U2 content. A KILL that confirms the original record is a full success
and will be reported as such, with no retuning and no substitution of a different arm.

## 9. Deviations

None at predeclaration time. Any deviation is recorded at the top of VERDICT.md.
