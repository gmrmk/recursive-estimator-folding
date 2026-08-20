# M233 predeclaration -- owned retained-sigma producer plus M228 kernel

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_CODE_AND_TESTS`.

M233 owns a new `RetainedSigmaLayerInput` ABI. From 31 live layer covariance
diagonal vectors of width 256, it computes and retains
`marginal_sigma=sqrt(diagonal)` once, computes active counts and
`factor=marginal_sigma/sqrt(n_active)` with the M205 zero-diagonal rule, then
forms charged flattened event labels and one two-row vector gather for M224's
two singleton margins. The gathered margins feed M228's unchanged 171-call
kernel in the same `BudgetContext` and raw timer.

No allocation, sqrt, active-count work, factor division/copy, label
preparation, or gather is free. M233 is a newly owned producer; it claims no
current M205/M212 caller reuse. M212/full-caller integration is separate.

M224 math, rho `.08`, 16 Phi terms, 32 panels, radii, event shape `31*128`,
context/outer seeds, M228 kernel bill `5467N`, wall threshold
`0.016133916999970098`, and strict `>100x` speed gate are frozen. Target is
`L=31`, width `256`, `N=3968`. Static proof must cover M205 parity including
zeros, M224 value/radius parity, gauge/permutation, and provenance refusals.
Only then may six fresh frozen/adversarial traces run. Truth, responses,
scorer, MSE, weights, leaderboard, and variance remain forbidden.
