# M192 x exact-control cross audit

Status: **read-only no-go/subsumption audit; no new candidate executed**.

The M192 truth-oracle premise is real and large, but the present exact-control
chain does not make its missing common-error statistic observable.

Let (n=126), (u=\mathbf 1/n), (P=I-\mathbf 1u^\top), and write one
output's frame vector as

\[
x_j=\mu_j\mathbf 1+e_j,\qquad z_j=Px_j=Pe_j,\qquad c_j=u^\top e_j.
\]

The sum-one GLS correction needs

\[
A=\mathbb E[z_jz_j^\top]=PC_eP,\qquad
b=\mathbb E[z_jc_j]=PC_eu.
\]

`A` is truth-free because projection removes the unknown mean. The observed
frame mean is (u^\top x_j=\mu_j+c_j), so it cannot identify (c_j). For any
weights-only or analytic anchor (a_j),

\[
u^\top x_j-a_j=c_j+(\mu_j-a_j),
\]

and therefore the estimated cross block is

\[
b+\mathbb E[Pe_j(\mu_j-a_j)].
\]

That extra term is exactly M193's anchor/contrast contamination. Output
cross-fitting prevents held-output self-fit, but it does not remove the truth
used to construct the training common error in M192.

## Why the exact-control components do not change the sigma-algebra

- M178/M179 provide an exact bivariate Gaussian primitive and exact
  zero-order/Jacobian background for that closure. They do not provide the
  fixed deep network's exact final mean.
- M198 converts an already supplied labelled fourth-order Source211 coefficient
  to a first-order delay-one tangent. It does not produce that coefficient or
  the full target mean.
- M125b transports an assembled signed source; transport creates no new common
  error observation.
- M148/M151 give an exact control-plus-full-support-residual identity for a
  particular `[2,1,1]` source contribution. M196 is still blocked before the
  native B=1 state/compiler/cost gate, and this is not an exact whole-output
  mean oracle.

Consequently these pieces currently define, at best, another anchor (a(W)).
They remain inside M193's failed information class unless one proves either
(a(W)=\mu) exactly or the exact orthogonality
(\mathbb E[Pe(\mu-a(W))]=0).

## Exhaustive residual trichotomy

1. A deterministic exact residual reconstructs (\mu). That is a new analytic
   truth-oracle assumption, not a salvage of current components.
2. An independent unbiased sampled residual is an independent pilot. M194's
   8-frame cross-noise norm was about five times the signal; a main-estimator
   scale pilot becomes cost-dilutive. M195 and M197 show the fixed-budget split
   loses Kerdock geometry and remains noisy.
3. A same-sample residual adds no sigma-algebra beyond the frame data, or has an
   unknown (\mathbb E[z\eta]). Without an independence identity it is not a
   lawful estimate of `b`.

## Closed mutations

- M193: analytic anchor contamination, ratio about `1057.9`.
- M194: independent-pilot SNR/cost failure.
- M195: two-way split geometry/cost failure.
- M197: three-way crossed cancellation is algebraically correct but worsens the
  panel (`1.3688x`).
- M148/M151/M196: exact residual idea survives, physical state/compiler/cost
  does not yet exist.
- M198/M200: semantic composition passes, but source/cost/variance remain
  unopened.

## Only lawful reopening contract

Predeclare an observable (S_j) and prove either

\[
S_j=\mu_j\quad\text{exactly},
\]

or

\[
\mathbb E[PX_j(\mu_j-S_j)\mid W]=0.
\]

If (S_j) is sampled, also prove conditional independence from `PX` and freeze
a cross-noise SNR gate before final MSE: the estimated noise cross norm must be
strictly below the target cross-block norm. No current artifact furnishes such
an (S_j), so M192 remains an oracle ceiling/byproduct opportunity, not a
deployable mutation.
