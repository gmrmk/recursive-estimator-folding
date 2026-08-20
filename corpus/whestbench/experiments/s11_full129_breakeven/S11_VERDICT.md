# S11 verdict — s11_full129_reopen_measured_breakeven

Date: 2026-08-09. Explicit reopen of killed `m81_full129_pareto`.
Question: does completing the 126-frame Kerdock design to the full 129-frame
real-MUB spread (deg-4 quadrature error -> 0, +1536 points) reduce the champion
MSE by more than the 2.326% break-even set by the extra point-count cost?

## VERDICT: RE-KILLED on the M81 break-even (now measured)

The degree-4-exactness-attributable champion-MSE reduction is **<= +0.18%**
(direct, point-count-matched measurement; upper bound), corroborated by the
committed m191 cv_deg4 control variate (**+0.42%**) and R^2_deg4 (**~0.2%**).
All three are an order of magnitude below the **2.32558%** break-even. Degree-4
exactness does not measurably move the champion MSE.

M81's **memory-margin kill ground still applies** and is untouched (see below).

---

## Deviations (recorded loudly, first)

1. **The gate quantity had to be isolated from a more-samples confound.** The
   task framed "fractional MSE reduction from setting the degree-4 error to 0"
   as if completing to 129 changes only degree-4 (degree-6 and the floor
   "essentially unchanged"). The direct measurement falsifies that model: the
   129-set also carries **+1536 points**, and the generic more-samples
   averaging on the degree-6+/floor part is the DOMINANT effect. A random-frame
   CONTROL (same +1536 points, degree-4 NOT zeroed) reduces MSE by +3.25% —
   essentially the same as the completion's raw +3.42%. So the raw
   completion-vs-126 reduction is NOT the degree-4 share. I isolated degree-4
   by holding point count fixed (completion@66048 vs control@66048). This is a
   methodological refinement of the predeclared measurement, not a retune of
   any gate: the gate threshold (2.33%) is unchanged; only the correct quantity
   to compare against it was clarified by the control.
2. **Point-count-matched control's own degree-4 error is inflated** (Phi4/Welch
   1.554 vs the 126-set's 1.016), so completion-vs-control is an UPPER bound on
   the true 126->129 degree-4 benefit — the real benefit is even smaller.
3. Plain numpy, no flopscope metering — the sanctioned G0 deviation (N8a/M181
   precedent), inherited via the read-only import of the m191/n8a machinery.

---

## 1. Break-even derivation + regime check

Adjusted score `S = MSE * max(0.1, C/B)`. Cost bills proportional to point
count.

- Cost ratio `C_129/C_126 = 66048/64512 = 1.0238095`.
- Metered-regime break-even: to improve `S`, need
  `MSE_129/MSE_126 < 64512/66048 = 0.9767442`, i.e. champion MSE must drop by
  **> 2.32558%** (matches the M81 ledger verbatim: "the raw MSE reduction must
  exceed 2.3256%").
- **Regime confirmed metered (above the 0.1 floor):** hosted #326094 adjusted
  1.832e-7 with MSE 2.818e-7 implies `C/B = 1.832e-7 / 2.818e-7 = 0.6501`,
  which is > 0.1, so the score is in the proportional (metered) regime and the
  2.32558% proportional break-even applies — NOT the floored regime (where the
  cost multiplier would be pinned at 0.1 and only MSE would matter).

## 2. Design verification — the completion IS an exact 5-design (deg-4 = 0)

`verify_design.py`, exact 4th-moment (Welch) identity on unit directions:

| set | per-line sum_j <v_i,v_j>^4 | Phi4 / Welch(3/(d(d+2))) | deg-4 error |
|---|---|---|---|
| 126-frame Kerdock (frozen sampler) | 1.48828125 | 1.015811 | present (1.58% excess) |
| **129-frame completion** | **1.5 exactly (min=max)** | **1.0000000000** | **identically 0** |
| control: 126 + 3 random frames | 2.3304 (mean) | 1.55362 | present (inflated) |

The completion adds phased-Hadamard indices 0 and 1 (the two frames trimmed off
the 128-frame Kerdock set to make 126) plus the standard/coordinate basis; all
three are unbiased against the 126 ({0, +/-1/16} inner products only). Two
independent signals agree: every line's 4th-moment sum is exactly 1.5, and that
matches the closed-form Welch bound 3/(d(d+2)) = 3/66048 to machine precision.

## 3. The degree-share measurement

**Committed data is INSUFFICIENT to pin the degree-4 SHARE from arithmetic
alone.** S6 gives the design's per-degree error OPERATOR (deg-4 tr(D^2),
3-shell eigenvalues, the suppressed constant mode) and m191-g0a the per-degree
error LEVELS (deg-4 rms/iid = 0.107, deg-6 = 0.40). Neither pins the champion
ESTIMAND's per-degree ENERGY E_l, which the share
`(E_4 D_4) / (sum_l E_l D_l)` requires. The estimand's degree-4 energy is
spread across the ~1.8e8-dim H_4 space (m191-g0b diagnostic), so the level
alone does not give the share. Committed proxies that DO bound the share:

- m191 **cv_deg4**: a direct degree-4 control variate on the 126 design removed
  **+0.42%** of champion MSE (aligned/removable share, 12-direction basis).
- m191 **R^2_deg4** = 0.18–0.23% (fraction of champion residual variance the
  degree-4 basis explains).

**Direct measurement (gold-standard falsifier).** Champion estimator (plain
final-layer antipodal ReLU mean) on 3 cached-truth synthetic nets
(width 256, depth 32; seeds 101/202/303), 64 rotation seeds/net across two
independent families (matched `900000+net*1000+rep`, reseed
`314159+net*1000+rep`), truth = m181 3.5M iid MC with noise floor subtracted.
`fhat_129 = (64512*fhat_126 + 1536*fhat_add)/66048`.

| comparison (pooled, 64 reps/net) | panel MSE ratio | reduction | 95% CI (ratio) |
|---|---|---|---|
| raw completion vs 126 (CONFOUNDED) | 0.96581 | +3.42% | [0.9443, 0.9868] |
| control: random 3 frames vs 126 | 0.96751 | +3.25% | [0.9465, 0.9892] |
| **deg-4 ISOLATED: completion vs control** | **0.99824** | **+0.176%** | **[0.9695, 1.0280]** |

- The raw completion reduction (+3.42%) and the control reduction (+3.25%) are
  statistically identical: **adding any 3 frames buys the reduction; degree-4
  exactness adds essentially nothing.**
- Degree-4 isolated (both at 66048 points, only difference is degree-4 = 0):
  **+0.176%**, with P(ratio < 1) = 0.54 — indistinguishable from zero.
- Fraction of total champion MSE by degree (from committed levels + this
  measurement): deg-4 ~= 0.2–0.4% (an order below break-even); the remainder is
  degree-6 (m191 error level 40% of iid) and higher/iid-like floor, none of
  which the completion improves.

## 4. Verdict vs the 2.33% gate

Gate quantity = **degree-4-attributable fractional MSE reduction = +0.18%**
(<= this; upper bound). Committed corroboration: cv_deg4 +0.42%, R^2_deg4 ~0.2%.

**+0.18% (and +0.42%) << 2.33% -> S11 RE-KILLED on the M81 break-even.**

Note for transparency: the RAW completion improves the adjusted score
(`S_129/S_126 = 0.96581 * 1.02381 = 0.9888`, point estimate). But (i) the raw
reduction's CI includes the 2.326% break-even, so it is not resolved; and
(ii) the control proves this improvement is the generic value of +1536 samples
(`S_ctrl/S_126 = 0.9906`, i.e. adding 3 RANDOM frames "improves" the score just
as much), NOT the value of degree-4 exactness. The distinctive property S11 is
about — deg-4 -> 0 — is worth <= 0.18%.

## 5. Does M81's memory-margin ground still apply?

**Yes, unchanged.** M81 was killed on two edges: (1) it never MEASURED the
variance value — measured here, and it FAILS the break-even; (2) its minimum
persistent memory increment is 1.75195 MiB against M71's frozen 1.44531 MiB
margin, crossing the 480 MiB safety gate. S11 addressed only edge (1). Edge (2)
is untouched and remains a hard blocker. Even if the variance value had cleared
(it did not), the memory margin would still have to be cleared by Sol before any
build. Both M81 grounds now stand.

## 6. Two-signal verification

- **Signal A (direct):** point-count-matched completion-vs-control =>
  degree-4 reduction +0.18% (upper bound).
- **Signal B (independent, committed):** m191 cv_deg4 direct degree-4 control
  variate on the 126 design => +0.42%; R^2_deg4 ~0.2%. Independent of A; agrees.
- **Reproduction checks:** `fhat_126` reproduces the cached m181 arm0 baseline
  bitwise (max|diff| = 0.0 on all 3 nets); two independent rotation families
  and the 5-design certificate (closed-form Welch = numerical per-line sum)
  agree.

## Files

- `run_s11.py` — direct-measurement runner (both seed families + control),
  writes `s11_stacks.npz`.
- `verify_design.py` — 5-design certificate (exact 4th-moment identity).
- `finalize_s11.py` — degree-4-isolated analysis from the saved stacks; writes
  `s11_results.json`.
- `s11_results.json` — machine-readable numbers, CIs, gate, verdict.
- `s11_stacks.npz` — per-rep fhat stacks (126 / completion-129 / control), both
  families, all nets.
