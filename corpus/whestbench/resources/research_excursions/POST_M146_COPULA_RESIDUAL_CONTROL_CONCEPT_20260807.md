# Post-M146 concept note: canonical-copula residual Hansen--Hurwitz

Date: 2026-08-07  
Status: **CONCEPT ONLY / NO IDENTIFIER / NO IMPLEMENTATION / NO AUTHORIZATION**  
Boundary: this note does not alter or reopen killed M146

## The changed mechanism

Use the preserved canonical rank-four latent copula as a deterministic
all-order control, not as a stand-alone approximation.  For each ordered
distinct `[2,1,1]` source label `e=(i,j,k)`, let

```text
G_e        = Delta_e F_e,
Gtilde_e   = Deltatilde_e F_e,
C          = (1/2) sum_e Gtilde_e,
H_e        = G_e - Gtilde_e.
```

`Deltatilde_e` must be the coefficient implied by one weights-only canonical
copula state frozen before sampling.  It must use the same partition,
ordered-singleton ownership, gauge, and source-to-output feature `F_e` as M131
and M133.  The new estimator is

```text
That = C + (1/K) [
    sum_pilot H_e/(2 q0(e))
  + sum_main  H_e/(2 q1(e | pilot))
].
```

The pilot-adaptive proposal is fitted to the exact residual magnitude
`||H_e||`, not `||G_e||`.  The hoped-for win is that a good deterministic
control makes the residual population much smaller and permits far fewer
exact M131 calls and narrower five-product batches.

## Unbiasedness certificate

If `C` is exactly the finite-population sum of the same `Gtilde_e` subtracted
inside every sampled `H_e`, and both proposals have full support, then

```text
E[H_E/(2q(E))] = (1/2) sum_e H_e = T - C.
```

Conditioning on the completed pilot gives the same M146 main-phase proof, so
`E[That]=T`.  The copula may be approximate; approximation quality affects
variance, not bias.  Numerical cubature error in `C` is bias unless certified
and separately bounded.

The clean certificate requires the copula state and any scale calibration to
be weights-only and frozen before the pilot.  If a scale is fitted from pilot
exact values, the safe form is instead a deterministic-count phase split:
the pilot estimates `T` under its pre-pilot control (or raw), while the main
phase uses `C(pilot)` plus main residuals under the corresponding frozen
pilot-fitted control.  Retroactively subtracting a pilot-fitted control from
the pilot terms is not covered by the proof.

## Double-count boundary

The exact ownership identity must be enforced at the `[2,1,1]` source level:

```text
final = common carrier + other owned partitions + C_[2,1,1]
        + residual_HH_[2,1,1].
```

Do not add the full copula transported correction and then also add the full
M133 `[2,1,1]` estimate.  Do not subtract a source coefficient while adding a
different output-space projection.  The copula's reported transported
correction mixes total-cumulance terms; unless its `[2,1,1]` projection is
explicit and its aggregate equals `(1/2)sum Gtilde_e`, it is not yet a valid
control for this estimator.  `[3,1]`, `[2,2]`, hard-edge, tree, and Gaussian
carrier terms must each remain owned exactly once.

## What the `~0.977` evidence does and does not buy

The canonical 49/201-node audits report transported correction fidelities
`0.97746/0.97788`.  If that number were the cosine for the same controlled
population and an optimal deterministic scale were available, the optimistic
orthogonal residual fractions would be

```text
1 - 0.97746^2 = 0.04457  (22.44x energy reduction),
1 - 0.97788^2 = 0.04375  (22.86x energy reduction).
```

That is only a ceiling argument.  The measured fidelity is an aggregate
transported-output cosine, not per-triple `[2,1,1]` residual variance, and it
does not certify the predictor norm, calibration, tails, or source-local
alignment.  The first falsifier must measure the exhaustive generated
population residual energy and p99 HH contribution before selecting `K`.

## Shared carrier and cost ledger

Potentially shared once, if the algebra is made identical:

- Gaussian mean/variance and rectified-marginal `Phi/phi` state;
- standardized bridge/covariance and rank-four factor construction;
- canonical factor gauge and downstream-weight contractions;
- M121/M125 base carrier and total-cumulance/Edgeworth response weights;
- the coefficient-free M133 feature banks and the final five-product scatter;
- setup-time response atlas and immutable factor tables.

Unique incremental work that must be traced:

- forming a coefficientwise `Deltatilde_e` interface from the copula state;
- proving or computing `C=(1/2)sum Gtilde_e` without an `O(n^3)` table;
- exact M131 calls for the residual samples;
- residual pilot scoring and any adaptive proposal scans; and
- phase-specific scale concatenation.

The published canonical-copula `74.566B` envelope and M133 `94.941B` envelope
cannot simply be added or declared shared.  The former includes `39.326B` of
inherited conditional-state work and `35.101B` of protected 49-node response
arithmetic; only a line-item integrated trace can establish overlap.  The
success condition is a fused control total plus residual sampler whose
complete protected cost and residual wall time beat M133 at matched MSE.

## Earliest kill tests

Kill the concept before response work if any of these fails:

1. coefficientwise/aggregate identity for `C` at machine precision;
2. exact partition ownership and gauge/permutation covariance;
3. exhaustive generated residual energy materially above the optimistic
   control target or p99 tail amplification;
4. inability to form `C` and sampled `Deltatilde_e` without dense triple
   materialization; or
5. a target-shape fused trace that does not repay control construction through
   fewer exact calls and smaller five-product batches.

This is the clean bootstrap of two preserved mechanisms: the copula supplies a
deterministic all-order baseline, and adaptive HH spends randomness only on its
signed exact residual.  It is conceptually unbiased, but only after the
coefficientwise ownership identity is constructed and certified.
