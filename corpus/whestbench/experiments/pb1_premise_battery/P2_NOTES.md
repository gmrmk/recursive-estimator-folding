# G3-P2 rotation-SELECTION premise — run notes (2026-08-08)

## VERDICT: KILL — broken links: pilot-proxy correlation AND pilot cost

Governing predeclaration: GEN3_RECURSION_PACKET_20260808.md proposal G3-P2 +
the 2026-08-08 dispatch task. Harness: run_p2_rotation_selection.py.
Results: p2_results.json. Checkpoints: p2_partial_net{101,202,303}.npz.

## DEVIATIONS / INTERPRETATION DECISIONS (loud, none silent)

1. **"Pooled rho" implemented as Pearson on WITHIN-NET ranks** pooled over
   the 48 (net, rotation) points. Selection happens within a net, so the
   pooled statistic must not be driven by across-net scale. The naive
   raw-pooled spearman is reported as a diagnostic and it DISAGREES IN
   SIGN with the within-net version for the full proxy (−0.340 within-net
   vs +0.327 raw): net 202 has both the largest MSEs and the largest proxy
   values, so raw pooling manufactures a positive slope that does not
   exist within any net. The gate was applied to the within-net version
   (the one selection would actually use). Flagged because the two
   readings of "pooled" straddle the |0.3| gate with opposite signs —
   the proxy's pass is fragile either way.
2. **Pilot frames = frames 0..7 (deterministic).** The task said "e.g., 8
   frames". A 20-random-subset sensitivity sweep (seeded) was added as a
   non-gating diagnostic; it confirms the collapse is not the subset
   choice (pooled rho mean −0.03, sd 0.17, range [−0.29, +0.19]).
3. **Pilot cost gate applied to the CHEAPER of two honest estimates at
   k=8**: (a) dense plain-antipodal forward FLOPs = 1.691e10/candidate
   (6.22% of B); (b) pruned-pipeline scaling from the hosted champion's
   mean effective compute, 1.79e11 × (8/126) = 1.137e10/candidate (4.18%
   of B). Gate uses (b); BOTH fail at k=8 by 6.7–9.9x, so the choice does
   not affect the verdict.
4. **Oracle-of-k = exact expectation of min over uniformly random
   k-subsets** of the 16 measured rotations (order-statistic identity,
   cross-checked by full C(16,k) enumeration, asserted equal to rtol
   1e-12); k=16 is the plain min. Gains reported raw (governing, matches
   what the benchmark scores) with noise-subtracted diagnostics alongside.
5. No arms beyond the predeclared ones were run; no gate was retuned; the
   two failed gates stand as measured.

## Context note (not a deviation)

Measured within-net across-rotation MSE spread here is 4.7–11.1x under the
plain-antipodal downstream, vs M185's 2.3–8.7x under the full v3 pipeline —
same direction, wider because the plain downstream lacks the pipeline's
error-absorbing stages.

## Numbers of record

Panel single-rotation-mean MSE 3.413e-7. Oracle panel gains:
k=2 34.7%, k=4 51.9%, k=8 **61.6%** (bootstrap 95% CI [48.8%, 66.8%]),
k=16 66.1%. Per-net k=8 gains: net101 55.6%, net202 68.8%, net303 48.8%.
Q1 gate (>=20%) PASSES decisively — the headroom is real.

Full-proxy pooled rho = **−0.340** (per-net −0.43/−0.19/−0.41; bootstrap CI
[−0.61, −0.02]). Passes the |rho| >= 0.3 gate on the point estimate, but
note: the sign is NEGATIVE (higher frame-dispersion ⇒ LOWER error, the
opposite of the naive selector), the CI reaches −0.02, and the raw-pooled
diagnostic flips sign. A weak, fragile signal.

Pilot proxy (8 frames): rho vs MSE pooled **−0.089** (per-net −0.30/−0.26/
+0.29, sign-inconsistent; CI [−0.37, +0.18]); rho vs full proxy pooled
+0.035 — the 8-frame proxy does not even track the 126-frame proxy it
estimates. FAILS the >= 0.25 gate.

Pilot cost, k=8: **33.4% of B** (pruned-scaled; 49.7% dense) vs the < 5%
gate. FAILS by ~7x. Even k=1 costs 4.2–6.2% of B.

## Cross-checks (two-signal)

- Frame-mean decomposition == direct overall mean, asserted every forward
  (atol 1e-12).
- Oracle order-statistic identity == full enumeration, every net/k.
- Spearman via Pearson-on-ranks == 6Σd²/(n(n²−1)) formula, every rho.
- Bitwise repeat of net101/r0 after checkpoint reload: identical.
- Panel gain-of-8 re-derived by hand from the per-net rows: 0.6160, matches.
- k=8 pruned pilot cost re-derived by hand: 0.3343, matches.

## Constraint handed to Generation 4

The oracle headroom (61.6% at k=8) is REAL and remains unharvested; what
died is the predeclared truth-free proxy (frame-dispersion) and the pilot
economics. Any Gen-4 reopening must bring (a) a proxy computable from
weights alone or from O(1) frames with demonstrated within-net sign-stable
correlation, and (b) a selection stage costing < 5% of B — the present
frame-pilot construction cannot reach either.
