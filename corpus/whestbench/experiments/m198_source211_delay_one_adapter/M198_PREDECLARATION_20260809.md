# M198 predeclaration: labelled Source211 delay-one response adapter

Date: 2026-08-09
Status: `PREDECLARED_RESPONSE_FREE`

No challenge instance, truth, scorer, leaderboard, submission, champion
artifact, or source-efficacy outcome may be read by this gate. Generated
weights and independent dense algebra oracles only.

## One changed causal link

M163/M169 emits fourth-order repeated-output source slots

```text
Source211 = (aaaa[i], aaab[i,j], aabb[i,j])
```

while M125b consumes a signed post-ReLU moment tangent

```text
TangentState = (delta_mean[i], delta_covariance[i,j]).
```

M198 changes only the missing semantic conversion. It combines a labelled
Source211 with the **same layer's labelled pre-ReLU Gaussian context**
`(a_k,C_k)` and applies the first-order fourth-cumulant delay-one Edgeworth
response. It neither invents a trivariate source coefficient nor reinterprets
slot shapes as moments.

The converted source is injected after ReLU layer `k`; M125b may then apply
only `J_(k+1),...,J_31`. The zero-order background must remain frozen and may
never receive the signed tangent.

## Frozen slot reconstruction

For every pair `i != j`, M198 reconstructs only the entries actually used by
the delay-one response:

```text
T4[i,i,i,i] = aaaa[i]
T4[i,i,i,j] = aaab[i,j]
T4[i,i,j,j] = aabb[i,j]
T4[i,j,j,j] = aaab[j,i]
T4[j,j,j,j] = aaaa[j].
```

No order-three source is present in this arm. The response is exactly the
`t3=0` restriction of M124 `edgeworth_delay_one`, including its multiplicities
`1,4,6,4,1`, central-covariance subtraction, and singular-correlation refusal.

## Required labels and ownership

The immutable input contract is:

```text
LabelledSource211(
  relu_layer, producer_epoch, owner,
  aaaa[n], aaab[n,n], aabb[n,n])

DelayOneContext(
  relu_layer, producer_epoch,
  pre_mean[n], pre_covariance[n,n], post_mean[n])
```

The adapter rejects layer/epoch mismatches, nonfinite values, a non-symmetric
`aabb`, `aaaa != diag(aaab)`, an invalid Gaussian covariance, or an unsupported
owner policy. M172's live policy transfers only physical `[2,2]`; its legacy
K22 owner must be marked retired while `[4]` and `[3,1]` remain externally
owned. The adapter does not grant zero cost for K22 formation or transport.

## Frozen premise tests

1. **Dense oracle:** widths `2..7`, generated SPD contexts, and generated
   symmetric fourth tensors. Extract the three slots, convert them, and match
   M124 `edgeworth_delay_one(..., t3=0, t4=dense)` within `2e-10` absolute.
2. **Context necessity:** one nonzero Source211 under two distinct lawful
   Gaussian contexts must produce distinct tangents. This rejects a shape-cast
   implementation.
3. **Linearity:** with context fixed, `R(xS+yT)=xR(S)+yR(T)` within `2e-11`.
4. **Permutation covariance:** jointly permuting source and context permutes the
   tangent within `2e-11`.
5. **Positive-gauge covariance:** for positive diagonal `D`, transform the
   preactivation and fourth tensor by `D`; the result must transform as
   `(D delta_mean, D delta_covariance D)` within `2e-9` relative/absolute.
6. **Archive extension parity:** a one-pass generated context builder must emit
   the same post-ReLU `(mu,V)` and local Jacobian as M179 while retaining its
   already-computed `(a,C)`. A second background pass is forbidden from any
   future cost claim.
7. **Carrier identity:** converted labelled sources through explicit suffix
   superposition must equal the M125b inhomogeneous recurrence. A terminal
   `s_31` receives an empty suffix; adding terminal Born again must be detectable
   as a nonzero duplicate.
8. **Owner mutations:** retained legacy K22 ownership, collision re-zeroing, or
   layer/epoch relabelling must be rejected or produce a detected conservation
   mismatch.

## Static resource boundary

The mathematical adapter is `O(L n^2)` and uses no dense tensor, trivariate
quadrature, Kronecker product, Khatri--Rao action, or output-row regression.
This gate makes **no native cost pass**. A descendant must meter univariate
CDF/PDF/exp, pair loops, symmetrization, casts, and allocation together with
the M179 producer, M163/M169 compiler, M125b carrier, and fixed-B=8 liveness.
The integrated total—not a sum of separately favourable worksheets—must fit
the applicable hostile budget and memory limits.

## Kill and preservation rules

Kill M198 on any dense-oracle, label, symmetry, gauge, linearity, owner, or
carrier failure. Preserve the first-Born indexing theorem and the explicit
need for pre-ReLU context even if native cost later fails. Passing this gate is
only a semantic component pass; it does not open M172 variance, response
efficacy, ranking, or submission.
