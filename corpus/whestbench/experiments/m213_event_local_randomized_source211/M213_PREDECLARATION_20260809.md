# M213 predeclaration — event-local randomized physical Source211 falsifier

Date: 2026-08-09. This document is frozen before M213 implementation or
execution. M213 is generated-only and response-free. It must not read a
challenge model, truth, scorer, response, weights, leaderboard, submission,
or efficacy record.

## New mechanism and exactness claim

For each labelled distinct event `(i,j,k)`, M213 draws **one** outer standard
normal `G`, conditions `X_j,X_k` on `X_i`, and evaluates the conditional
bivariate ReLU product using one M178 `Phi2` call and M131's conditional
centralization identity. The event variable is

`(ReLU(X_i)-m_i)^2 * E[(ReLU(X_j)-m_j)(ReLU(X_k)-m_k) | G]
 - V_ii V_jk - 2 V_ij V_ik - Tree_iijk`.

`m`, `V`, and `Tree` are local deterministic quantities calculated before the
draw. In particular the three covariance-product subtractands are *not*
estimated from outer draws. Therefore the claim is mathematical
exact-in-expectation under the declared Gaussian law and exact real-valued
local formulas; a frozen floating PRNG stream is only a reproducibility device,
not evidence of literal floating-point unbiasedness.

Collision physical owners are calculated on demand from local
univariate/bivariate moments and carry the same connected-minus-tree defect
semantics as the distinct coefficient:

- `K4[i] = kappa(Y_i,Y_i,Y_i,Y_i) - Tree_iiii`;
- `K31[i,j] = kappa(Y_i,Y_i,Y_i,Y_j) - Tree_iiij` for `i != j`;
- `K22[i,j] = kappa(Y_i,Y_i,Y_j,Y_j) - Tree_iijj` for `i != j`.

They populate M167/M205's complete Source211 collision rows with the forced
`1/6`, `1/3`, and `1/2` orbit factors. M213 emits no four-distinct wedge:
the `[1,1,1,1]` request returns an explicit unsupported sentinel with no
coefficient, never a numerical zero. M213 does not construct a rank-four
coefficient tensor and makes no source compiler, M198 converter, terminal,
response, or efficacy claim.

## Frozen generated cells, randomness, and reference-only checks

- Widths: `2, 3, 4, 5, 6, 7`.
- Generated Gaussian-state seeds: `213700002, 213700003, 213700004,
  213700005, 213700006, 213700007`, paired in order with the widths.
- Outer-draw seeds: `213710002, 213710003, 213710004, 213710005,
  213710006, 213710007`.
- Confidence blocks and draws per block: `12 x 64`; all blocks are disjoint.
- A fixed 64-node Gauss--Hermite calculation may be used only as a generated
  audit reference for the identity test. It is not the M213 provider, is not
  an accepted deterministic outer rule, and may not be retuned or used to
  replace the random outer draw.

The production event kernel receives the exact M179 local post-ReLU context
`(m,V,Tree)` and computes only its requested owner. It must never create an
all-pairs collision cache. A small-width all-owner table is an audit oracle
only. Before any M198 use, a future compiler must contract the coefficient
through the **next affine W** into Source211 slots; only then can M198 receive
the resulting source together with the **next pre-ReLU** context. M213 does
neither action.

## Frozen gates and stop rules

1. **Unbiasedness identity.** For every valid distinct event at widths 3--7,
   check the tower-property formula against the independent generated
   Gauss--Hermite audit reference. This is an identity check, not a claim that
   finite floating sampling is exactly unbiased. Width 2 has no distinct
   event and is recorded as vacuous for this gate.
2. **Confidence.** For the canonical `(0,1,2)` event at widths 3--7, the
   99% Student-t interval from the frozen 12 block means must contain the
   reference-only identity value. Failure rejects the provider candidate;
   passage is only a generated statistical consistency check.
3. **Gauge and permutation.** Positive diagonal gauge and label permutations
   must transform every physical collision owner and every distinct event
   coefficient covariantly. Tests must use no externally supplied weights.
4. **Ownership.** The complete table has exactly the M167/M205 collision
   mapping, retains all pairwise-distinct `[2,1,1]` entries, contains no
   M156-style collision zeroing, and contains no four-distinct wedge.
5. **Numerical/provider.** Every bivariate call must be on M178's SPD chart.
   The local Tallis pair reconstruction uses M178's value and all three first
   derivatives; its radius propagates `w_value`, `w_da`, `w_db`, and
   `w_drho`. On every frozen event, the resulting M178-local coefficient
   radius must be at most `2e-7 * (1 + abs(midpoint))`; a refusal, nonfinite
   radius, or breach fails the local provider gate. This means mathematically
   unbiased and numerically bounded, not literally bitwise unbiased. Full
   IEEE-roundoff, source-contraction, and output-bias certification remain
   integration work and are not silently claimed here.
6. **Cost.** A distinct event uses exactly one conditional M178 call. The
   precomputed local covariance cache may use M178 but its calls are listed
   separately. The only inherited worst-case bill is **4,048 charged FLOPs
   per M178 call** (3,984 static plus 64 epilogue); no 3,968-call or inclusive
   M198/source bill is claimed. Missing M198 context binding and a native
   source/compiler trace block provider-cost promotion.

M149's fixed `43/87` deterministic conditional quadrature remains killed for
its observed value/tangent certificate failures. M213 neither raises that
order nor loosens its certificates: a random outer draw is the changed
mechanism.

No source-variance efficacy, response variance, MSE, score, or leaderboard
experiment may be written or run unless the identity and provider gates have
both been independently passed. When such a future variance gate is
authorized, it must include M213's provider RNG nested with the base `q0`
randomness; legacy coefficient-only variance is insufficient.
