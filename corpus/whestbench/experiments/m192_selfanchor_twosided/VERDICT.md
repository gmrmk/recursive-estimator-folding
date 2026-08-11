# M192-SELFANCHOR verdict -- KILLED at step 0, confirmed numerically

Date: 2026-08-10.  Governing protocol: `PREDECLARATION.md` in this directory,
written and frozen before any number here was computed.  Cached-artifact
arithmetic only: zero forwards, zero network generation, zero response
evaluations, zero submissions, no git, no network, no scorer/private/holdout
access, no contact with m245.

## DEVIATIONS (read first)

1. **Step 1 was executed despite the step-0 kill.**  Predeclared as a
   kill-confirmation with an explicit falsifier ("if any ratio differs from 1
   by more than 1e-9 the step-0 algebra is wrong and the verdict reopens"), not
   as a rescue.  Nothing was retuned on its output.  The falsifier did not
   fire.
2. **A4 positive control is an addition beyond the task's two-signal
   requirement.**  Without it, the A3 null returning exactly 1.000 would be
   uninterpretable -- a dead probe and a real null look identical.  A4 shows
   the shuffle has power.  Declared as a control; it is not a claim about M192.
3. **"Shuffle the output-neuron index" was implemented as an independent
   permutation of the output index within each of the 126 frame rows, applied
   to the covariance-training block only.**  A single global permutation of the
   output index is a pure relabelling -- it only permutes the `j % 8` fold
   partition and destroys no structure -- so it would have been a control with
   zero power.  The per-row version destroys the cross-output coherence that
   the method claims to exploit while leaving the baseline and the scoring
   untouched.
4. **One test failed on first run and its tolerance was corrected.**  Verbatim:
   `AssertionError: Not equal to tolerance rtol=1e-08, atol=1e-16 ... [0]:
   -2.6978419498391304e-14 (ACTUAL), 0.0 (DESIRED)`.  Both sides were zero to
   double-precision roundoff against a signal scale of order 1; `atol=1e-16`
   was tighter than double precision permits at that scale.  The tolerance was
   made scale-relative (`atol = 1e-12 * ||P C_e 1||`) and two additional
   assertions were added requiring each side to be below `1e-12` of the signal
   scale.  No substantive claim was weakened.
5. `alpha = 0` raises `RuntimeError: GLS weights do not sum to one`.  This was
   predeclared as the expected exact singularity and was **not** repaired.
6. **A write escaped into the frozen directory and was reverted.**  The first
   run of `test_selfanchor_math.py` caused CPython to write
   `m192_cross_output_gls/__pycache__/run_m192_g0.cpython-314.pyc`.  The
   frozen module sets `sys.dont_write_bytecode` in its own body, which is too
   late to suppress its own cache file.  Cause fixed (the flag is now set in
   `test_selfanchor_math.py` before the frozen imports; the runner always had
   it), the `.pyc` deleted, and both scripts re-run to confirm the frozen
   `__pycache__` stays empty.  No frozen source, artifact or result file was
   modified -- all `m192_cross_output_gls` files retain their 2026-08-08
   mtimes, and that directory's own suite `test_m192_m195_math.py` still
   passes 5/5, including its frozen-disposition assertions.

## STEP 0 -- the crux, answered algebraically

**The two-sided identity is true.  It is also insufficient.  The construction
is impossible.**

The M193 autopsy line, in full, from `corpus/whestbench/headroom/fold_ledger.json`
record `m193_analytic_anchor_frame_gls`:

> Exact autopsy: C_anchor=C_error+q1^T+1q^T+s11^T; s11 is harmless to an
> unshrunk sum-one rule, but Pq is not.

Decompose any symmetric `C` with `u = 1/sqrt(p)`, `p = 126`, `P = I - u u^T`:

    C = alpha u u^T + u b^T + b u^T + A,   alpha = u^T C u,  b = P C u,  A = P C P.

Unbiasedness forces `1^T w = 1`.  Writing `w = 1/p + v` with `v = P v`,

    J(v) = alpha/p + (2/sqrt(p)) b^T v + v^T A v,
    v*   = -(1/sqrt(p)) A^+ b,
    w*   = 1/p - (1/sqrt(p)) (P C P)^+ P C u.

**The constrained-GLS solution depends on the pair `(A, b)`.**  `A = P C P`
supplies only the quadratic form -- the metric that converts a direction into a
weight.  `b = P C u` is the entire linear term and is the only object that can
move `w` off uniform.  `b = 0` implies `w = 1/p` for every `A` and every ridge.
`P C P` determines `A` and says nothing whatever about `b`.

Under the self-anchor `a_j = (1/p) 1^T x_j`:

    delta_j = mu_j - a_j = -(1/p) 1^T e_j,
    q       = E_j[delta_j e_j] = -(1/p) C_e 1,
    P C_a 1 = P C_e 1 + p P q = P C_e 1 - P C_e 1 = 0   EXACTLY.

Equivalently: the self-anchored residual is `r_j = P x_j = P e_j`, so
`C_a = P C_e P` already and `C_a 1 = 0` identically; M194's common-mode residual
`ctilde_j` is identically zero, so its cross block is identically zero.

So the reconciliation the task asked for is this: **the self-anchor does not
make `Pq` vanish.  It makes `Pq` equal to exactly minus `1/p` times the cross
block the solver needs, so the anchor contamination and the signal cancel term
for term.**  "s11 is harmless but Pq is not" is precisely the statement that
the harmless term and the load-bearing term both live in the same one-sided
contraction against `1`; a projection that annihilates one annihilates the
other.  The uniform frame mean is the unique anchor at which the estimator has
zero information about how to deviate from its own mean.  It is a fixed point,
not a solution.

Verified a second way, on synthetic data with no cache involved, in
`test_selfanchor_math.py` (5/5 pass):

- `m192._weights(C, alpha=0)` equals `1/p - (1/sqrt p)(PCP)^+ P C u` to 1e-8;
- two matrices with **identical** `P C P` and different `b` give different
  weights (so `PCP` alone cannot determine `w`);
- `b = 0` gives exactly uniform for every `alpha` in {0.25, 0.5, 0.75, 0.9, 0.99};
- `q = -(1/p) C_e 1` to 1e-10, hence `||P C_a 1|| / ||P C_e 1|| < 1e-12`;
- `m194._block_weights` returns `cross_norm < 1e-14` under the self-anchor and
  `> 1e-3` under a generic anchor.

## STEP 1 -- measured kill confirmation

Frozen M192 machinery imported unmodified from
`../m192_cross_output_gls/run_m192_g0.py` and `run_m194_g0.py`.  Same cache,
same 3 nets (101/202/303), same 16 rotations, same 8 outer folds by `j % 8`,
same uniform 126-frame-mean baseline, same panel statistic.

| arm | per-net ratios (101 / 202 / 303) | panel |
|---|---|---:|
| A0 harness crosscheck (frozen M192 oracle) | 0.146840 / 0.095677 / 0.143037 | 0.126193 |
| **A1 self-anchor, M192 solver, alpha=0.25** | **1.0000000000 / 1.0000000000 / 1.0000000000** | **1.0000000000000073** |
| A2 self-anchor, M194 solver (independent impl.) | 1.0000000000 / 1.0000000000 / 1.0000000000 | 1.0000000000000069 |
| A3 permutation null control | 1.0000000000 / 1.0000000000 / 1.0000000000 | 1.0000000000000597 |
| A4 positive control, oracle unshuffled | 0.146840 / 0.095677 / 0.143037 | 0.126193 |
| A4 positive control, oracle shuffled | 0.774569 / 0.596948 / 1.059396 | 0.788288 |

A0 reproduces the frozen archive with `max_abs_diff_vs_frozen = 0.0` and the
archived P2 baseline with `max_p2_baseline_crosscheck = 0.0` on all three nets.
The harness is the M192 harness.

A1 detail: 48/48 rotations within 2.9e-13 of 1.0; bootstrap 95 percent ratio
interval `[0.99999999999998, 1.00000000000004]` (degenerate, as a deterministic
uniform rule must be); `max |w - 1/126| = 1.46e-15`; median weight L1 exactly
1.0, max 1.0000000000000004; `max ||C 1|| / (||C|| sqrt(126)) = 4.50e-15` across
384 fits.  The returned weights are the uniform weights to machine precision.
Alpha sweep: identical panel 1.0 at alpha in {0.25, 0.5, 0.75, 0.9, 0.99}, with
`max |w - uniform|` shrinking monotonically from 1.46e-15 to 6.77e-17; alpha=0
raises, as predeclared.

A2 measures the killed quantity directly.  Median cross-block norm under the
self-anchor is `4.12e-19` (max `1.17e-18`); under the truth anchor it is
`1.26e-05` (min `3.69e-06`).  Ratio `3.26e-14`.  The self-anchor is not a noisy
estimator of `b` -- it is the exactly-zero estimator of `b`, 100 percent
attenuation with zero variance.

## Both required signals

**(a) Out-of-fold.**  Every reported number is out-of-fold: held outputs never
participate in their own weight fit, under M192's frozen `j % 8` partition.
No in-sample number is reported anywhere in this folder.

**(b) Permutation null control.**  A3 gives panel 1.0000000000000597, with
`max |w - uniform| = 8.85e-17` -- no improvement, as required.  A4 proves the
control is not a dead probe: the same shuffle applied inside the frozen M192
truth-trained oracle moves the panel from 0.126193 to 0.788288, destroying 88.5
percent of the oracle's log-gain.  The residual gain under shuffling is
expected and honest -- a per-row permutation preserves each frame's marginal
variance, so a diagonal-scale component of the frame covariance survives it.
The control has power; A3's 1.000 is a real null.

**Third, unrequested signal:** bitwise repeat.  Three full runs produced
byte-identical `results.json` apart from `runtime_seconds`.

## Gate call: KILLED

Predeclared kill condition: ratio `>= 1.0` on 2 of 3 nets, **or** step 0 shows
the projection unavailable/insufficient.  Both limbs fire.

The literal gate counter reads `2 of 3` rather than 3 of 3 only because net 101
lands at 0.9999999999999981, which is 1.9e-15 **below** 1.0 -- floating-point
roundoff on a rule that is provably exactly uniform, not an improvement.  The
honest statement is that all three nets are 1.0 to within 1.5e-14.

SIGNAL condition (`<= 0.90` on `>= 2` nets) fires on 0 of 3.  Not inconclusive:
the arm is exactly the uniform baseline, by an identity, with no free
parameter that could change it.

## What this buys the campaign

A5 checked the load-bearing identity numerically: the self-anchored sample
second moment equals `P C_m192 P` to a maximum relative Frobenius error of
`6.40e-15` over all 384 fits.  A1 therefore ran the frozen solver on the
**exact true contrast block** with `b = 0`, and returned exactly the baseline.

That makes this arm, despite being killed, an exact isolation experiment:

- true `A`, true `b`  -> panel 0.126193 (M192 oracle, 87.38 percent reduction)
- true `A`, `b = 0`   -> panel 1.000000 (this arm, 0.00 percent reduction)

**One hundred percent of the M192 oracle headroom is carried by the cross block
`b = P C_e 1 / sqrt(126)`.  The 126x126 contrast block `A` contributes nothing
on its own under the sum-one constraint; it is only the metric that converts
`b` into a weight direction.**

This unifies the five recorded failures rather than adding a sixth kind.  M193
(analytic anchor), M194 (independent pilot), M195 (symmetric halves), M197
(three-way crossed pilots) and this arm all fail on the same 126-vector `b`:
M193 by contaminating it with `p Pq` many orders larger than itself; M194 by
estimating it with cross-noise about 5x the signal; M195/M197 by paying design
structure for it; and the self-anchor by estimating it as exactly zero.  The
target is not "a better covariance" and not "a more accurate anchor" -- it is
`b` itself, whose median realized norm in the M194 normalization is 1.26e-05.
Any future arm should be quoted against that number before it is built.

The M192_M195_NOTES disposition stands unchanged and is reinforced: reopening
requires genuinely new information about the common frame error.  This arm
demonstrates that no rearrangement of the estimator's own outputs can supply
it, because every such rearrangement is a linear functional of the same
realized frames and the self-anchor is their sum-one fixed point.

## Files

- `PREDECLARATION.md` -- protocol, step-0 algebra, gates, prediction on record
- `VERDICT.md` -- this file
- `results.json` -- all arms, diagnostics, gate evaluation
- `run_selfanchor_g0.py` -- runner; imports frozen M192/M194 sources unmodified
- `test_selfanchor_math.py` -- 5 standalone step-0 algebra checks, no cache
- `run.stdout.log`, `run2.stdout.log` -- run transcripts (bitwise-identical results)

Reads were limited to `pb1_premise_battery/p2_partial_net{101,202,303}.npz`,
`pb1_premise_battery/p2_results.json`,
`m181_terminal_smoothing/m181_truth_net{101,202,303}.npz`, and the
`m192_cross_output_gls` sources and results.  Cached synthetic truths were used
only for scoring after weights were fixed.  Writes were confined to this
directory.
