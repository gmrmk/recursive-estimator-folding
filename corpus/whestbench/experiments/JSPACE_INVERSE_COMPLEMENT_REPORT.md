# JSpace inverse/complement control: final report

## Verdict

**Structural inversion is not salvaged. Terminate this control family.**

Bottom-Gram and top-Gram-orthogonal directions do improve on the failed top
Gram cell, by 29.87% and 24.64% in raw variance respectively. That relative
signal is real, but it is not a viable estimator: both inverse cells lose to no
control on all 16 fresh networks, remain more than four times worse in raw
variance, and become roughly 19-20 times worse after full independent-pilot
cost. Their design-error correlations are effectively zero.

The frozen factorial was run exactly once. There was no official data, scorer,
API, outcome-selected direction, tuning, or retry.

## Provenance

```text
gate SHA-256   66A9BAA48F3AB3D534E228FBB1C4CBBF777722078E82C0441C0885FD7BD68D48
result SHA-256 7BE623A905B41F93AC5637C870EE91F009E0F953AF4C5C61D81178A56A781723
environment    work/whest-starterkit/.venv/Scripts/python.exe
NumPy          2.4.6
executions     1
```

Fresh seed bands were separated for teacher, Gram pilot, Hutchinson probes,
coefficient pilot, isotropic directions, complement construction, and residual
rotations. `run_accuracy.py` refuses to run when the frozen result exists.

## Frozen factorial

| Direction link | Raw ratio | Full cost ratio | Cost-adjusted | Wins | Error correlation |
|---|---:|---:|---:|---:|---:|
| no control | 1.0000 | 1.0000 | 1.0000 | -- | -- |
| isotropic | 3.1790 | 1.7452 | 5.5479 | 0/16 | -0.0195 |
| top four terminal-Gram | 6.0549 | 4.4334 | 26.8436 | 0/16 | -0.0131 |
| bottom four terminal-Gram | **4.2461** | **4.4334** | **18.8247** | **0/16** | **-0.0058** |
| four directions in top-four complement | **4.5629** | **4.4374** | **20.2474** | **0/16** | **0.0229** |

The Gram-derived costs include the complete independent 128-state, four-probe
terminal-Gram pilot and eigensolve. The complement cell additionally charges
projection and QR. The isotropic cell is the best control, yet its raw ratio is
still 3.179 and it also loses on all networks.

Per-network raw ratios show no favorable hidden subgroup:

| Cell | Minimum | Median | Maximum |
|---|---:|---:|---:|
| isotropic | 1.508 | 2.970 | 9.514 |
| top four Gram | 1.561 | 4.234 | 12.357 |
| bottom four Gram | 1.468 | 2.526 | 11.911 |
| complement four | 1.302 | 3.451 | 9.705 |

## What the inversion teaches

The direction link is not completely irrelevant: avoiding the top sensitivity
eigenspace reduces the damage by about one quarter to one third. But the
absolute result falsifies the stronger hypothesis that the wrong end of the
Gram spectrum caused the failure. Even the best inverted cell adds over 3.2
times the no-control variance, before cost.

The shared defect is observability. Centered, exact-mean degree-6/8 Gegenbauer
features fit a little pilot variation, but the fitted correction does not track
the randomized-design integration error on new rotations. Median centered
pilot residual ratios are 0.938 (isotropic), 0.906 (top), 0.940 (bottom), and
0.941 (complement), while out-of-pilot error correlations collapse to roughly
zero. This is the approximate-mean/error-link obstruction in measured form.

Conditioning is not the culprit: median ridge conditions range only 6.50-8.50.
The design defects are degree 2 exactly zero, probed degree 4
`5.20e-18`, and degree 5 exactly zero. Every output is finite.

## Sign negation is not a mutation

For the frozen feature family,

```text
h_l(u; v) = P_l(<u,v>),  l in {6,8}.
```

Both degrees are even, so `P_l(-t)=P_l(t)` and therefore
`h_l(u;-v)=h_l(u;v)` pointwise. Replacing any direction by its negative leaves
every feature column, its span, the pilot fit, and the residual estimator
unchanged. The measured maximum feature difference is exactly `0.0`.
Sign-flipping is span-equivalent and cannot be promoted as another mutation.

The constructed complement is genuinely orthogonal to the top-four Gram
space: the maximum measured defect is `2.87e-15`. Thus this was a true
subspace inversion, not a sign relabeling.

## Frozen gate and termination

Both inverse cells pass the numerical, exact-design, complement/sign, finite,
and at-least-20%-better-than-top checks. Both fail every viability requirement:

- raw ratio at most 0.60;
- cost-adjusted ratio at most 0.90;
- wins on at least 12 of 16 networks;
- error correlation at least 0.40.

Five algebraic, deterministic, rotation-covariance, cost, gate-integrity, and
sign-equivalence tests pass after the run, and all sources compile in the WHest
environment. No accuracy experiment was repeated.

Preserve the terminal Gram object only as an offline diagnostic. Do not mutate
rank, degree, ridge, signs, or seeds on this evidence. The honest recursive
promotion decision is `terminate_structural_inversion_no_salvage`.

Machine-readable evidence is in [`accuracy_results.json`](accuracy_results.json)
and [`decision.json`](decision.json); the immutable contract is
[`PREDECLARED_GATE.md`](PREDECLARED_GATE.md).
