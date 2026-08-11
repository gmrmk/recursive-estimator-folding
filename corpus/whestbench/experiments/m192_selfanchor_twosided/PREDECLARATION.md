# M192-SELFANCHOR predeclaration -- self-anchored two-sided contrast projection

Date: 2026-08-10.  Scope: cached synthetic G0 arithmetic only.  Zero forwards,
zero network generation, zero response evaluations, zero submissions.  Nothing
here is a submission candidate or evidence from any private evaluator.

Written BEFORE any number in this folder was computed.  The step-0 algebra
below was derived from `M192_M195_NOTES.md`, `run_m192_g0.py`,
`run_m194_g0.py`, `test_m192_m195_math.py`, and the M193 autopsy line in
`corpus/whestbench/headroom/fold_ledger.json`, all read before writing.

## Candidate

Replace M193's analytic anchor and M194's independent pilot with the
estimator's OWN uniform frame mean, `a_j = (1/126) 1^T x_j`, and run the
frozen M192 sum-one GLS machinery on the two-sided projected residual
covariance `P C_a P`, where `P = I - 1 1^T / 126`.

The claimed attraction: `P C_a P = P C_e P` exactly, so both anchor cross
terms and the `s 1 1^T` term vanish identically -- no truth, no pilot, no
analytic mean.

## STEP 0 -- the algebraic gate (free, may kill before any compute)

### 0.1 The M193 autopsy line, in full context

`corpus/whestbench/headroom/fold_ledger.json`, record `id =
m193_analytic_anchor_frame_gls`, field `result`:

> KILLED decisively: panel ratio 1057.899; per-network ratios 1530.06,
> 1108.71, 697.92. Exact autopsy: C_anchor=C_error+q1^T+1q^T+s11^T; s11 is
> harmless to an unshrunk sum-one rule, but Pq is not. The analytic error is
> 6.09e-4 to 1.88e-3 and correlates with frame contrasts, inflating median
> weight L1 to 5.76 and producing dominant bias.

`M192_M195_NOTES.md` lines 60-65 say the same thing: "The final rank-one term
is harmless under a sum-one constraint.  The two cross terms are harmless only
when `P q = 0`."

### 0.2 Does the sum-one GLS solution depend only on `P C P`?

Notation: `p = 126`, `u = 1/sqrt(p)`, `P = I - u u^T`.  Decompose any
symmetric `C` in the common/contrast splitting:

    C = alpha u u^T + u b^T + b u^T + A,
    alpha = u^T C u  (scalar),
    b     = P C u    (contrast vector, the COMMON-TO-CONTRAST CROSS BLOCK),
    A     = P C P    (contrast block).

Unbiasedness forces the sum-one constraint `1^T w = 1`.  Parametrise the
feasible set exactly: `w = w0 + v` with `w0 = 1/p` uniform and `v = P v`.
Then

    J(v) = w0^T C w0 + 2 w0^T C v + v^T C v
         = alpha/p + (2/sqrt(p)) b^T v + v^T A v.

Stationarity on the contrast subspace gives the constrained-GLS solution

    v* = -(1/sqrt(p)) A^+ b,        w* = 1/p - (1/sqrt(p)) (P C P)^+ P C u.

**The solution depends on the PAIR `(A, b)`, not on `A` alone.**  `A = P C P`
fixes the quadratic form; `b = P C u` is the entire linear term and is the
only thing that can move `w` off uniform.  If `b = 0` then `v* = 0` and
`w* = 1/p` exactly, for every `A` and every ridge.

This is not an artefact of my parametrisation.  It is visible in the frozen
M194 code: `run_m194_g0.py::_block_weights` computes `block` (= A) and
`cross` (= b, up to scale) and returns
`weights = uniform - (A + lambda tau P)^+ cross`.  With `cross = 0` the
returned weights are uniform by construction.  It is equally visible in the
frozen M192 code: `run_m192_g0.py::_weights` returns `w prop C^{-1} 1`, and
`C 1 = 0` makes `1` an exact eigenvector of the shrunk matrix
`(1-alpha) C + alpha tau I` with eigenvalue `alpha tau`, so `C_bar^{-1} 1 =
1/(alpha tau)` and the normalised `w` is exactly uniform.

### 0.3 What the self-anchor does to `b`

With `x_j = mu_j 1 + e_j` and the self-anchor `a_j = (1/p) 1^T x_j`:

    delta_j = mu_j - a_j = -(1/p) 1^T e_j,
    q       = E_j[delta_j e_j] = -(1/p) E_j[(1^T e_j) e_j] = -(1/p) C_e 1.

Therefore

    P C_a 1 = P C_e 1 + p P q          (because P 1 = 0 kills the 1 q^T and s terms)
            = P C_e 1 - P C_e 1
            = 0        EXACTLY.

Equivalently and more directly: the self-anchored residual is
`r_j = x_j - a_j 1 = P x_j = P e_j`, so `C_a = P C_e P` already, and
`C_a 1 = P C_e P 1 = 0` identically.  The common-mode residual
`ctilde_j = (1/p) 1^T x_j - a_j` is identically zero, so M194's `cross` block
is identically zero.

### 0.4 Step-0 verdict (recorded before compute)

The two-sided identity `P C_a P = P C_e P` is TRUE.  It is also USELESS under
the sum-one constraint.  The constrained solver needs `(A, b)`; the self-anchor
sets `b = 0` identically.

The sharper statement, which is the reconciliation the task asked for: the
self-anchor does not make `Pq` vanish.  It makes `Pq` equal to exactly minus
`1/p` times the cross block the solver needs, so the anchor contamination and
the signal cancel term by term.  The self-anchor is the unique anchor at which
the estimator has zero information about how to deviate from its own mean --
a fixed point, not a solution.  "s11 is harmless but Pq is not" is exactly
this: the projection that kills the harmless term also kills the load-bearing
one, because both live in the same one-sided contraction against `1`.

**STEP 0 KILLS THE CONSTRUCTION.**  Predicted deployable output: uniform
weights, hence panel MSE ratio exactly 1.0.

## PREDICTION ON RECORD

1. Self-anchored two-sided arm returns `w = 1/126` on every one of the 384
   folds, to floating-point roundoff (`max |w - 1/126| < 1e-12`).
2. Per-net ratios `1.000000` on all three nets; per-rotation ratios
   `1.000000` on all 48 rotations; panel ratio `1.000000`.
   Tolerance for "exactly 1": `|ratio - 1| < 1e-9`.
3. Result is invariant to the shrinkage `alpha` for every `alpha > 0`; at
   `alpha = 0` the solve is exactly singular (`1` is in the kernel of
   `P C_e P`) and must either raise or return numerical garbage.  Either is
   reported, neither is repaired.
4. The permutation null control returns `1.000000` as well -- the arm cannot
   distinguish real cross-output structure from destroyed structure, because
   it extracts none.
5. The positive control (same shuffle applied inside the frozen M192 oracle)
   moves the oracle from `~0.126` toward `~1.0`, proving the null control has
   power and that a `1.000000` in item 4 is a real null and not a dead probe.

Reasoning for the prediction: step 0, and nothing else.

## GATES (predeclared, binding)

- **KILL** if the self-anchored two-sided ratio `>= 1.0` on 2 of 3 nets, OR if
  step 0 shows the projection is unavailable / insufficient under the sum-one
  constraint.
- **SIGNAL** if ratio `<= 0.90` on `>= 2` of 3 nets AND the improvement holds
  out-of-fold.
- Anything else is **INCONCLUSIVE**, reported as such.

Two signals required for any non-kill verdict:
(a) out-of-fold evaluation only, never in-sample;
(b) a permutation/null control that shows no improvement.

No retuning past a failed gate.  No new arms.  Anchor scales, ridge values,
fold structure, alpha grid and rotation set are inherited frozen from M192 and
are not touched.

## What will be computed anyway, and why (declared deviation)

Step 0 kills.  I still run the step-1 numbers, **strictly as a
kill-confirmation with a falsifier**, because a predicted "exactly 1.000000"
is a sharp, refutable consequence of the step-0 algebra and observing it is a
genuinely independent second signal.

Falsifier: if any per-net or per-rotation ratio differs from 1 by more than
1e-9, my step-0 algebra is WRONG and the verdict must be reopened, not
patched.  If the ratio comes back below 1, the kill is withdrawn and I report
that I mis-derived the constrained solution.

This is a confirmation run, not a rescue attempt.  Nothing will be retuned on
its output.

## Arms actually executed

- **A0 CROSSCHECK**: re-run the frozen M192 oracle machinery on the same cache
  and reproduce `m192_g0_results.json` per-net ratios bitwise-or-near.
  Validates that my harness IS the M192 harness.
- **A1 SELF-ANCHOR / M192 SOLVER**: `_second_moment` replaced by the
  self-anchored `P S P` (row-centred sample second moment of the realised
  126x256 frame matrix over training outputs); everything else frozen from
  M192; `alpha = 0.25` frozen as in M193/M194 since the deployable arm has no
  truth for inner selection.  Full alpha sweep reported as robustness.
- **A2 SELF-ANCHOR / M194 SOLVER**: identical construction fed through the
  independent frozen `run_m194_g0._block_weights` with `anchor = column mean`.
  Two independent implementations of the same estimator.
- **A3 NULL CONTROL**: fit the A1 weights on training columns whose
  output-neuron index has been independently permuted within each of the 126
  frame rows (destroying cross-output coherence), then apply those weights to
  the UNSHUFFLED held columns and score against truth.  Baseline and scoring
  untouched, so the ratio stays interpretable.
- **A4 POSITIVE CONTROL (power check for A3)**: the same shuffle applied
  inside the frozen M192 truth-trained oracle covariance.  Declared as a
  control, not as a claim about M192.

Fold structure, rotations, nets, baseline and panel statistic are M192's:
8 outer folds by `j % 8`, 16 rotations, nets 101/202/303, uniform 126-frame
mean baseline, per-net ratio of rotation-mean MSEs, panel = geometric mean
over nets, 5000-draw paired bootstrap.

## Firewall

Reads: `experiments/pb1_premise_battery/p2_partial_net{101,202,303}.npz`,
`experiments/pb1_premise_battery/p2_results.json`,
`experiments/m181_terminal_smoothing/m181_truth_net{101,202,303}.npz`,
and the M192 source/result files.  All read-only, all cached, all committed.
Writes confined to this directory.  No git, no network, no submission, no
scorer/private/holdout access, no contact with m245.  Cached synthetic truths
are used only for scoring after weights are fixed.
