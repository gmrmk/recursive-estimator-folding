# Predeclared locked rung: JSpace-Gram-aligned degree-6/8 controls

This contract is frozen and hashed before any accuracy experiment. Execution
remains locked until an explicit follow-up after the independent JSpace judge.
No competition data, scorer, API, official row, or prior outcome may enter.

## Question

Can a cancellation-resistant input workspace estimated from an independent
pilot provide better directions for an exact-mean degree-`>=6` control than
isotropic directions or directions derived from the signed mean Jacobian?

The Jacobian here is only the terminal full input-to-output Jacobian. This rung
does not estimate intermediate `J_l`, identify a layer band, or claim an
all-layer workspace.

This is the required error-link test for the sole survivor of
`jspace_workspace_adapter`. It does not assume that an accurate workspace
improves spherical integration.

## Fresh bank and three-way separation

- 16 new bias-free He ReLU teachers, `d=16`, `L=8`.
- New seed band only:
  - teacher `7,901,003 + network`;
  - JSpace pilot `8,101,019 + network`;
  - Hutchinson probes `8,303,021 + network`;
  - coefficient pilot `8,501,047 + network`;
  - isotropic directions `8,701,069 + network`;
  - residual rotations `8,903,077 + 1000*network + rotation`.
- Independent JSpace pilot: 128 Gaussian states.
- Independent coefficient pilot: 128 Gaussian states.
- Independent residual bank: 32 Haar rotations of the complete real-MUB union
  in `R^16`, antipodally closed (288 spherical points, exact 5-design).
- No pilot is reused across these roles. No direction or seed is chosen from a
  residual/reference outcome.

## Frozen factorial

Every non-null control uses four unit input directions and normalized zonal
Gegenbauer degrees `{6,8}`, hence eight homogeneous features

```text
h_(k,l)(x) = ||x|| P_l(v_k.x/||x||),   E_N(0,I) h_(k,l)=0.
```

Compare:

1. `no_control`;
2. `isotropic_control`: first four columns of one deterministic-seed Haar
   matrix, independent of teacher outcomes;
3. `signed_mean_j_control`: top four right singular directions of the K=4
   Hutchinson signed mean `J_hat`, equivalently the top eigenvectors of
   `J_hat^T J_hat`;
4. `second_gram_control`: top four eigenvectors of the K=4 Hutchinson
   `G_hat=E[(J^Tz)(J^Tz)^T]`.

Both Jacobian-derived families use the same 128-state JSpace pilot and the same
nested four Rademacher probes. Eigenvectors are sorted descending and each sign
is fixed by making its largest-magnitude coordinate positive. No eigendirection
selection from downstream performance.

## Frozen coefficient fit and estimator

The previous spectral student was contaminated by a dominant constant mode and
tiny feature scale. Here the output-only ridge fit is fixed before outcomes:

1. subtract pilot column means from feature and teacher matrices;
2. divide each centered feature by its pilot RMS, floored at `1e-12`;
3. solve ridge with `lambda=1e-6*trace(Hs^T Hs)/8`;
4. transform coefficients back to the original zero-mean Gegenbauer features.

The pilot intercept is a fit nuisance only and is discarded: a constant is
integrated exactly and cannot alter the control estimator. On each independent
design rotation use

```text
I_hat = rho_16 * mean_U[f(U) - h(U) C],
```

because `E[h]=0`. Variation across rotations is exactly the design-surviving
even degree-`>=6` variance. The no-control cell is `rho_16 mean_U f(U)`.

## Frozen cost ledger

Charge separately for each method:

- all residual teacher forwards;
- coefficient-pilot teacher forwards;
- JSpace-pilot teacher forwards and K=4 VJPs for Jacobian-derived directions;
- signed/Gram accumulation and eigensolve;
- feature evaluation, centering/scaling, ridge Gram/RHS/solve, readout, and
  exact-mean bookkeeping.

No cross-method cache credit is used in the primary matched-cost ratio. Report

```text
(V_method/V_no_control) * (C_method/C_no_control).
```

The previously estimated 2.813B target-shape K=4/128-state cost applies only to
this single terminal/input Gram. Any layerwise extension is a separate rung and
must charge L-fold outer accumulation/storage plus the required activation/VJP
plumbing.

## Frozen promotion and localization gate

The primary `second_gram_control` survives only if all hold:

- aggregate degree-`>=6` design variance ratio `<=0.60`;
- cost-adjusted ratio `<=0.90`;
- raw variance improves on at least 12/16 networks;
- it beats `signed_mean_j_control` aggregate raw variance by at least 10%;
- median control/teacher randomized-design error correlation is `>=0.40`;
- median ridge condition number `<=1e8`;
- exact 5-design moments, Gaussian/spherical mean identities, seed separation,
  input rotation, hidden/output permutation, eigenvector sign convention,
  deterministic rerun, PSD, and finite checks pass.

Localize failure without mutation:

- if isotropic wins too, the spectral control mechanism—not alignment—survives;
- if signed and Gram tie, cancellation-resistant geometry did not transfer;
- if pointwise pilot fit improves but design variance does not, the prior
  low-degree/control null repeats;
- if Gram directions correlate with design error but lose after cost, preserve
  geometry only as an offline diagnostic;
- if all controls fail, terminate the JSpace estimator branch.

The active-subspace warning is binding: at target dimension, an even
degree-six residual captured by rank four can scale like `(4/256)^6`. No result
at `d=16` authorizes deployment without a larger-shape confirmation.

## Execution lock

`run_accuracy.py` must abort unless a separately created unlock file contains
this gate's exact SHA-256. The unlock file is intentionally absent in this
preparation rung. Unit tests may exercise algebra on tiny fixture networks but
must not instantiate the 16-network/32-rotation accuracy bank or write outcome
metrics.
