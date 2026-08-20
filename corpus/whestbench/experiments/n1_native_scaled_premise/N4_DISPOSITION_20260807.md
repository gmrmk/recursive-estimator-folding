# N4 disposition: cheap v-levers exhausted; radial null CONFIRMS champion

Measured variance-per-sample v (= MSE*N, unbiased stages, 40 reps, generated
d=256/L=32 net, own 3M-sample truth). Response-free.

| stage | v | SEM | S_needed(joe_wanza 7.39e-9) at this v |
|---|---|---|---|
| plain iid | 0.0470 | 0.0076 | 55.5x |
| + antipodal | 0.0379 | 0.0055 | 44.9x |
| + radial (chi_256 mean-radius) | 0.0391 | 0.0050 | 46.3x |
| + RQMC Sobol | SKIPPED (no scipy in frozen venv) | | |

## Findings (each with its second signal)

1. **Radial control is a NULL lever here** — v 0.0391 (radial) vs 0.0379
   (antipodal) is within 1 SEM, and radial is nominally HIGHER. Second signal:
   base_estimator.py sets `radial_conditioning = False` with the comment
   "Full800 development testing rejected spherical-radial conditioning." Two
   independent signals agree — radial buys nothing on this problem. Not a
   failure of N4; a corroboration of the champion's own design choice.

2. **Antipodal gives a marginal, noisy reduction** (0.047 -> 0.038, ~1 SEM).
   Direction correct (antithetic variates), magnitude ~1.24x but not cleanly
   resolved at 40 reps.

3. **The measured non-QMC v (~0.038) is WORSE than the champion's 0.0199.**
   Therefore the champion's ~2x-lower v comes from the two levers N4 could not
   measure: Sobol-Owen QMC (scipy absent; matches the competition sandbox) and
   the q3 radial-weight control polynomial (base_estimator base_weights). NOT
   from geometry.

4. **v is hard to MEASURE** (SEM ~15% at 40 reps): the 256 per-neuron squared
   errors within one rep share the sample draw, so effective replication ~ reps,
   not reps*256. Differences below ~2x are not cleanly resolvable without paired
   common-random-number designs or many more reps. (Does not affect the
   estimator, which just needs many samples; only affects measuring v.)

## Implication (the honest redirect)

Via adjusted = v * 8.74e-6 / S, easing the #1 throughput bar means driving v
BELOW the champion's 0.0199. N4 rules out the cheap geometric route: radial is
null, antipodal is already in the champion. The remaining v-levers are:
- **Sobol-Owen QMC** (the champion's own; a deployable measurement needs a
  BUNDLED pure-numpy Sobol since scipy is not in the sandbox) — expected to
  recover the ~2x to reach 0.0199, but NOT below it (the champion already uses
  it);
- **the exact control-variate chain** (M178/M179 -> M176 -> Source211 -> M175
  -> the frozen M172 source-variance gate) — the ONLY corpus route to v below
  the champion's, and the reason M179 is on the critical path. Its payoff is
  gated at M172 with predeclared thresholds (upper-90 < 0.25).

So N4 redirects effort from cheap v-tricks (exhausted) to completing the exact
v-control artifact (M179 G4/G5) and, ultimately, the M172 variance gate — while
the S half stays gated on a graded submission. No cheap win was available; that
is the honest result, and it sharpens where the remaining leverage is.

## Preserved tissue

Radial-null is banked (do not reopen radial as a v-lever). Antipodal stays.
The champion's v=0.0199 is the frame constant (QMC+q3). The bundled-Sobol RQMC
measurement is the next cheap-ish v experiment; the exact-control chain is the
only route below 0.0199.
