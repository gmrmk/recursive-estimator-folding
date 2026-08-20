# uf1_attack_integrated — run log, deviations, file list

Date 2026-08-10. Pinned `work/whest-v014/Scripts/python.exe`,
flopscope `0.10.0+np2.4.6`, numpy `2.4.6`. Synthetic data only. No scorer,
no truth, no holdout, no dataset, no submission, no network, no git. All
writes confined to this directory. The frozen champion source was IMPORTED
read-only (`row_blocked_winograd.py`) and not modified; `sha`-relevant files
untouched.

## DEVIATIONS FROM THE TASK TEXT — recorded loudly

1. **The task's champion decomposition (`C = 1.7683e11`, matmul `145.138e9`
   of `146.794e9` instrumented = 98.87%) mixes two different objects.**
   `145.138e9 / 146.794e9` is **MLP #0** of `kerdock_v3_official100.json`,
   exactly. The 100-MLP means are `168.693e9 / 170.494e9` (98.94%). `C` is a
   mean. I therefore carry BOTH: an exact per-MLP integrated rescore of the
   cached 100-MLP run, and a mean-share translation onto the stated champion
   headline. They agree to 4e-4 in gain.

2. **The task frames the change as depth-0 -> depth-4. The deployed champion
   is already depth-1.** `kerdock_v3_estimator.py::_sample_matmul` dispatches
   `RowBlockedBatchedWinograd.multiply`, whose metered bill at
   (64512,256)@(256,256) is 7,427,768,320 — bit-exactly the closed form with
   schedule (a,b,c) = (7,7,7). The eligible lane is therefore ALREADY paying
   r(1). Every delta in this attack is measured against that real baseline,
   not against the direct product.

3. **The 100-MLP artifact used is kerdock v3 (adjusted 1.6191e-7), not v3.1
   GUARDS (1.832e-7).** It is the only scored artifact in the corpus carrying
   per-MLP `effective_compute` / `residual_wall_time_s`. No v3.1 GUARDS
   per-MLP breakdown exists here. Consequence: absolute scores in the per-MLP
   arm are v3's; the champion-headline arm uses the stated v3.1 numbers.
   Both arms are reported separately and never blended.

4. **`uf1_results` absolute cells d3/d4 do not equal their own closed form.**
   Recorded d3 `5,840,555,008` vs closed-form-and-metered `5,840,523,264`
   (delta 31,744); d4 `5,309,760,256` vs `5,309,811,712` (delta -51,456).
   Their **ratio** table (0.692071 / 0.629184) matches my metering to 6 dp,
   so this is a transcription defect in the absolute listing only, and the
   FLOP-only lane result is NOT affected.

5. **The corpus's own full-entry residual rate is noise-limited and I did not
   lean on it.** `INTEGRATED_BATCHED_WINOGRAD_REPORT.md` records residual
   0.159546 s (parent) vs 0.160284 s (child): a 0.46% difference between two
   single-shot 0.16 s numbers. Dividing by 240 or 336 extra calls gives
   3.08 or 2.20 us/call, which straddles the d4 break-even of 2.60 us/call.
   That arm is reported in `e_breakeven.json` and explicitly NOT used as the
   basis of the verdict; the controlled bare-loop floor is.

## Files

- `a_cost_law.py` / `.json` — the v0.10.0 integrated cost law, verified
  exactly (0.0 error) on 100 cached MLPs; residual-framing reconciliation.
- `b_meter_residual.py` / `.json` — metered flops + backend/overhead/residual
  for direct, the frozen champion kernel, and recursive Winograd d=1..4 at
  (32256|64512, 256)@(256,256); 3 reps each.
- `c_residual_floor.py` / `.json` — bare-loop per-flopscope-call residual
  floor (2000/500 calls, 5 reps, min taken).
- `d_integrated_score.py` / `.json` — exact-Fraction closed form; eligibility
  reconstruction; exact per-MLP integrated rescore; champion translation.
- `e_breakeven.py` / `.json` — break-even residual rate per depth; rate
  sensitivity; wall-time consequence.
- `f_final_verify.py` / `.json` — shape-correct floor; fresh-process bitwise
  repeat of the decisive d4 arm; final headline table.
- `_smoke.py` — small-shape smoke check used to validate the harness against
  `UF1_ACCOUNTING.md` Signal B (reproduced 1,054,900,224 / 926,973,952 /
  818,708,480 bit-exactly at M=8064).
