# T3 build notes — fold3-39936 deterministic per-network cap

Date: 2026-08-08. Implements T3_PREDECLARATION.md exactly; gate results in
`t3_gate_results.json`.

## Deviations from the predeclaration

1. **n_eff floor at 1,024, not 256.** The predeclaration's equation admits any
   multiple of 256; the implementation never chooses n_eff < 1,024
   (= fold_pilot_base). Below 1,024 the parent shrinks its fold pilot
   (`pilot_n = min(fold_pilot_base, n_base)`), the realized partitions diverge
   from the pilot-identical simulation, and the cost model's premise is void —
   the predeclaration's own "pilot-identical simulation" requirement implies
   the floor. It is unreachable in practice: C_pred(1024) is a few percent of
   CAP for width-256 depth-32 networks. No gate exercises the floor.

No other deviations. Kill conditions, CAP = 244.8e9, the 256-multiple frame
constraint, verbatim parent delegation, and the finally-restore are as
predeclared.

## What was built

- `capped_fold3.py` — `Estimator(estimator_n39936.Estimator)`. Per network,
  before the main run:
  1. `_simulate_cap_sets()` replays the parent's active-set evolution on the
     first `fold_pilot_base = 1024` frame rows plus their antipodal images —
     row-for-row the same pilot rows the parent's own rescues (first 256+256
     rows) and fold refinements (1024+1024 rows) consult, so the recorded
     partition sizes match the real run for every n_eff >= 1024. The replay
     runs through `flopscope.numpy` on the tracked weights (it is
     mlp-dependent arithmetic, hence billed — the legality question resolved
     conservatively) and its actual bill is OBSERVED with live
     `flops.budget_summary_dict()["flops_used"]` tally reads rather than
     modeled.
  2. `predict_main_bill()` models the parent `predict()`'s bill op-by-op as a
     pure-Python integer function of (n, realized set sizes). The parent's
     own `_diagonal_gaussian_pass` is not modeled either: the simulation runs
     the identical call once and its observed bill is reused (identical ops =>
     identical bill).
  3. `C_pred(n) = sim_cost_observed + dp_cost_observed + predict_main_bill(n)`.
     n_eff = largest multiple of 256 <= 39,936 with C_pred(n_eff) <= 244.8e9
     (linear downward scan; C_pred is affine increasing in n).
  4. If n_eff < 39,936: slice `self._gaussian` to n_eff rows (a prefix of
     whole 256-row orthogonal frames — frames are iid, a prefix is
     statistically valid) and shadow `self.n_base = n_eff` on the instance;
     call the UNMODIFIED `super().predict(mlp, budget)`; restore the frame
     tensor and drop the instance shadow in `finally`. If n_eff = 39,936
     nothing is touched, so the parent runs verbatim on the original tensor
     (G3's bitwise no-op).
  Diagnostics land in `self.last_cap_report` (n_eff, C_pred, observed
  overheads, all set sizes); the estimator math is untouched.

- `run_t3_gates.py` — runs G1/G2/G3 per the predeclaration, prints per-gate
  PASS/KILL with numbers, writes `t3_gate_results.json`, stops at the first
  broken link. G4 (whest validate-package) is packaging-stage and out of this
  experiment's scope.

## Cost model terms

Per-op bills measured empirically on the pinned whest-v014 flopscope (probe
scripts under the session scratchpad; two probe passes, all formulas exact at
every probed shape):

| op | billed FLOPs |
|---|---|
| float32 matmul (m,k)@(k,n), incl. vec@mat m=1 | 2mkn − mn |
| pointwise unary/binary/compare/logical | 1 per element |
| mean axis=0 of (m,n) | m·n |
| sum/max/min axis=0 of (m,n) | (m−1)·n |
| concatenate | 1 per output element (×2 int64) |
| fancy-index gather | 4 per output element (int64 taken as 8) |
| sort / argsort | 8·n·ceil(log2 n) |
| flatnonzero | 1 per input element |
| arange | 4 per element |
| stack | 1 per output element |
| sqrt | 2 per element |
| exp, x**2 | 16 per element |
| float64 dtype rate | ×2 (everything stays float32) |

`predict_main_bill` walks `fold3_estimator.Estimator.predict` line by line
(radial_conditioning=True path: `final_weights is None`, no quartic weights):
first-layer matmul + antipodal ReLU assembly + residual moments; 28 pruning
layers (pilot concat/gathers/matmul/reduction/sort only when the cold set is
non-empty, then the (2n, a_prev)@(a_prev, a_next) sample matmul + ReLU); the
three fold layers with per-call bills for `pre31`/`pre32` (the parent
recomputes the folded inner products on every call — modeled per call); the
kink-mean / on-mean / dead assembly; `_assemble_vector`; the 31-layer tangent
recursion; the final stack. Dominant terms (the sample matmuls) are exact;
micro-terms (int gathers, empty-branch clamps) are approximated within a few
hundred FLOPs each.

Verification of the model before the gates: at n=4096 (16 frames), walk+dp vs
metered uncapped bill on two He nets: ratio 0.999658 and 0.999666 (model
underestimates the main run by ~0.034%; the observed simulation overhead term
then makes total C_pred a slight overestimate, which is the safe side of the
G1 window). Small-scale capped output was bitwise identical to the frozen
estimator.

## Known approximations / residual risk

- The simulation propagates the pilot rows as a (2048, ·) block; the real run
  propagates them inside the (2n, ·) block. I did not prove the two are
  bitwise identical row-for-row (BLAS blocking could round a near-zero pilot
  preactivation differently and flip one rescue decision — labeled
  hypothesis; the settling check is a row-for-row diff of the simulated
  block against a full run's pilot rows). Observed bound on the aggregate
  effect: on all four full-scale capped runs, C_pred_chosen matched the
  metered capped bill to ratio 0.99996, so any count drift is at or below
  the model's own 0.0035% micro-term gap. The parent computes its own
  selections — output correctness is never affected, only the cost estimate.
- The op-walk under-models the parent's bill by a constant ~8.55e6 FLOPs
  (0.0035% at full scale; observed as metered_capped − C_pred_chosen on all
  four capped runs). A network whose C_pred lands within 8.55e6 of CAP could
  therefore bill up to 8.55e6 over CAP — 0.0035% against G2's predeclared 2%
  tolerance and B − CAP = 27.2e9 of real headroom.
- Int64 gather rate was not probed directly (float32 gathers bill 4/element);
  taken as 8/element. Total int-gather volume is a few hundred elements per
  predict.
- `budget_summary_dict()` outside any BudgetContext returns a process-global
  cumulative tally; the implementation only uses deltas, which are coherent
  both inside and outside a context (outside one, nothing bills and the
  deltas are 0, which is then also the correct overhead).

## Gate results (2026-08-08 run) — ALL PASS

Full numbers in `t3_gate_results.json`.

**G1 (cost-model calibration) — PASS.** C_pred(39936) vs metered uncapped
billed FLOPs, window [0.98, 1.06], never under:

| net (He seed) | C_uncapped | C_pred(39936) | ratio |
|---|---|---|---|
| 11 | 2.3617e11 | 2.4295e11 | 1.0287 |
| 22 | 2.4212e11 | 2.4908e11 | 1.0287 |
| 33 | 2.2142e11 | 2.2790e11 | 1.0293 |

The consistent +2.9% is the observed cap-simulation overhead (≈6.8e9)
included in C_pred by design; the modeled main run itself sits at −0.0035%.

**G2 (adversarial worst case) — PASS.** He + 0.032 offset, per-layer
renormalized: zero analytically-cold units across layers 1..31; realized
active sets 256 at every pruning layer (pruning vanished, verified from the
capped run's own counts). n_eff = 31,232 < 39,936; run completed, output
finite; metered C = 2.4303e11 <= 2.4970e11 (CAP x 1.02) — in fact under CAP
itself. Diagnostic: the uncapped estimator bills 2.9949e11 on this net, which
would breach B = 2.72e11 — the exact historical failure mode the cap removes.

**G3 (bitwise no-op off the tail) — PASS, non-vacuous.** Nets 11 and 33 have
C_pred(39936) <= CAP: both chose n_eff = 39,936 and the capped output is
np.array_equal-BITWISE identical to the uncapped output. Net 22 sits above
CAP (2.4908e11), capped to n_eff = 39,168 (three frames trimmed), metered
capped bill 2.4445e11 <= CAP.

Cross-check of the whole chain: on all four capped runs (three G1 nets + the
adversarial net) C_pred(n_eff) matched the metered capped total at ratio
0.99996 — the simulation's partition counts match the real run's.

## Rerun commands

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& "C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\work\whest-v014\Scripts\python.exe" `
  "C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\t3_fold3_deterministic_cap\run_t3_gates.py"
```

Thread pinning (OPENBLAS/OMP/MKL/NUMEXPR = 1) is set inside the runner;
everything is single-process. Runtime: a few minutes (eight full-scale
predicts plus setups).
