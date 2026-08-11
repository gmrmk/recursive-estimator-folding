# Anti-J pre-mutation ladder — Erratum 1

Status: append-only mathematical and authority repair. This file grants no
scientific-execution, estimator-mutation, submission, or scorer authority.

Parent artifact:

- `CODEX_ANTI_J_PREMUTATION_LADDER_20260811.md`
- parent SHA-256
  `24CD6C4B7E65700A6EF84F7C651AEE206B40887D00576235652732FDA837E51E`
- disclosed in commit `9e20057`

The parent remains immutable. This erratum supersedes only the M4b/M5
mathematical object, multiplication side, endpoint claims, inherited design
debt, and related execution statements identified below. Every other gate in
the parent remains in force.

## E1 — the parent changed error objects between M4b and M5

The parent defined one full-design centered error `e(Q)` and used the
same-function involution identity

```text
<e, U_R e> / ||e||^2 = 1 - 2 ||Pi_- e||^2 / ||e||^2.
```

M5 does not average two copies of that same function. It averages two distinct
63-frame direction operators. Freeze their frame identities in the incumbent
phase order:

```text
D_A = incumbent complete frames 0..62,
D_B = incumbent complete frames 63..125.
```

Thus `D_A union D_B` restores exactly the incumbent's 126-frame **direction
multiset** when both use the same rotation. It does not automatically restore
the incumbent estimator: pilot, active-set, fold, guard, residual, and reducer
paths can couple the halves nonlinearly.

Any separable covariance premise must therefore freeze a distinct pilot `Pi`
from a PRNG/Haar substream independent of the held-out `Q`, use `Pi` for every
pilot-dependent decision in both arms, and hold the resulting path fixed while
measuring the two arm outputs. Conditional on weights and `Pi`, the production
covariance object is

```text
f_A(Q) = Y_A(Q) - E_Haar[Y_A(Q)],
f_B(Q) = Y_B(Q) - E_Haar[Y_B(Q)],

kappa_AB(R) = 2 <f_A, L_R f_B> / (||f_A||^2 + ||f_B||^2).
```

The inner product is first the evaluator-matched mean Euclidean output inner
product and Haar expectation within one fixed network and fixed `Pi`; declared
whole-network aggregation occurs afterward. The exact centering, independent
pilot, folding path, frame scaling, and output reducer must be frozen in any
proposal. If a proposed implementation instead lets the A arm choose shared
decisions, `f_B` becomes a two-argument function of both `Q` and `R Q`; the
one-argument identities in this erratum no longer apply and direct paired MSE
is mandatory.

For a self-adjoint involution `L_R`, write `f_A=f_A+ + f_A-` and similarly for
`f_B`. Then

```text
<f_A, L_R f_B> = <f_A+, f_B+> - <f_A-, f_B->,
<f_A,     f_B> = <f_A+, f_B+> + <f_A-, f_B->.
```

The parent's projection-norm identity is valid only in the special same-design
case `f_A=f_B`. It is retained solely as a positive-control theorem and cannot
stand in for the production cross-design covariance.

## E2 — the multiplication side was wrong for the implementation convention

The committed estimator names the sampled Haar matrix `rotation = Q` and forms

```text
first_weight = Q.T @ W1.
```

For canonical Kerdock row matrix `S`, the physical input rows are therefore

```text
X_Q = S @ Q.T.
```

For an input-coordinate reflection `R_AJ`, the reflected rows must be

```text
X_Q @ R_AJ = S @ Q.T @ R_AJ.
```

They are implemented by

```text
Q_prime = R_AJ @ Q,
```

because `Q_prime.T = Q.T @ R_AJ`. The parent's `Q_prime = Q @ R_AJ`
instead reflects canonical design coordinates. It is superseded.

The corrected induced action is the left action

```text
(L_R f)(Q) = f(R_AJ @ Q).
```

Left Haar invariance preserves the marginal law when `R_AJ` is fixed
conditional on weights and on a separately frozen pilot independent of the
held-out `Q`.

Before any network forward, a 2-by-2 noncommuting matrix-contract test must
prove that the implementation's transformed first product equals
`S @ Q.T @ R_AJ @ W1`, while the intentionally wrong-side control differs.
The central controls `R=I` and `R=-I` are insufficient because they commute
with every `Q`.

## E3 — corrected endpoints

For one fixed design operator `D`, exact-real antipodal symmetry gives

```text
rho_D(I)  = 1,
rho_D(-I) = 1,
```

provided its centered error variance is nonzero. Bitwise equality remains an
implementation test because floating reductions can depend on row order.

For the actual cross-design child,

```text
kappa_AB(I) = kappa_AB(-I)
            = 2 <f_A,f_B> / (||f_A||^2 + ||f_B||^2).
```

That endpoint value may take any value in `[-1,1]`. It equals `+1` only if the
two centered half-design errors are equal almost everywhere with equal norms.
The two endpoints recover the same A/B coupling, not two identical 63-frame
arms and not automatically the incumbent estimator path.

Reflection-attributable improvement relative to the repaired independent-pilot
`R=I` endpoint must occur at a noncentral reflection, but one predeclared
interior reflection can directly establish or refute its gate. The endpoint
fact does not require a rank sweep. Attribution requires three matched arms:

```text
W0
  -> repaired independent-pilot topology at R=I
  -> identical repaired topology at R=R_AJ.
```

Only the final contrast earns reflection credit. The independent pilot's own
cost, bias, residual wall, and memory are fully billed to the candidate.

## E4 — rank is not a covariance parameter

`rank(P)` labels a Grassmannian of orientations, not a scalar curve. A complete
rule `k -> P_k` must be frozen before writing `kappa(k)`.

An exact same-rank counterexample exists already in dimension three. Let

```text
A = B = E_12 + E_21,
f(Q) = tr(B Q A Q.T).
```

This centered function is antipodally even. The Householder operators
`R_i=I-2 e_i e_i.T` both have rank-one negative eigenspaces. Under the right
action, `R_1 A R_1=-A` and gives correlation `-1`, while `R_3 A R_3=A` and
gives correlation `+1`. The analogous left-action example transforms `B`.
Thus equal-rank reflections can give opposite extreme correlations.

The primary rank and orientation rule remain frozen before held-out covariance.
Any exploratory rank sweep requires a separate discovery panel, multiplicity
control, and fresh confirmation. Adding ranks does not create independent
rotation replicates.

## E5 — M192's cross-block theorem does not kill this mechanism

For sum-one GLS on a fixed frame covariance, define

```text
u = 1/sqrt(p) * 1,
P = I - u u.T,
A = P C P,
C = alpha u u.T + u b.T + b u.T + A,
```

the cross block `b=P C u` is indeed the only linear term that can move the
canonical pseudoinverse or positively ridged solution away from uniform.
Opus's self-anchor proof that `b=0` returns uniform weights is accepted as
static algebra. If `A` is singular, unregularized minimizers need not be unique;
that does not change the canonical/ridged conclusion.

M4b is different. It keeps equal arm weights and changes the common-mode
variance itself. For the two arm errors with covariance matrix `C_R`,

```text
Var((Y_A + Y_B)/2)
  = (Var_A + Var_B + 2 Cov_R) / 4
  = (Var_A + Var_B) (1 + kappa_AB(R)) / 4.
```

Under proved exchange symmetry and equal marginal variance, the GLS cross block
may be zero and uniform weights remain optimal while negative `Cov_R` still
lowers `alpha`. The repaired A/B topology plus an A-owned pilot does not itself
prove that symmetry. M192 is compatible with the coupling but neither selects
its arm weights nor falsifies it.

## E6 — the inherited M195 number is not bound to the repaired topology

M195 used the first 63 frames from each of two independent rotations. The
repaired child uses incumbent frames 0..62 under `Q` and frames 63..125 under
`R_AJ @ Q`, so `R=I` restores the incumbent direction multiset. A separately
generated independent pilot means it is still not automatically the incumbent
estimator path.

Consequently the parent's imported `r_ind=1.113996` and all numerical `kappa`
thresholds derived from it are suspended. They may be reinstated only after an
authorized cache-only assay computes the independent-rotation ratio for the
exact `D_A/D_B` split, the exact pilot/fold path, and the exact evaluator
reduction. Existing P2 and S11 caches have different documented matrix
association orders; bitwise compatibility is presently unverified.

For a matching topology, define the **variance-only** independent-half factor

```text
r_ind,var = (Var_A + Var_B) / (4 Var_incumbent),
r_var(R)  = r_ind,var * (1 + kappa_AB(R)).
```

An empirical independent-half MSE ratio cannot substitute for `r_ind,var`
unless the matching bias terms are separately shown equal. Without that
binding, direct paired MSE is the authority. This variance law also assumes
the coupling preserves both marginal arm variances. Ideal Haar with a fixed
independent pilot supplies that theorem conditionally; a deterministic seed
split must itself be frozen and validated and does not certify independence by
assertion.

## E7 — truth-free covariance is a premise screen, not a score certificate

Within one fixed network and conditional on a fixed independent pilot `Pi`,
truth cancels from the Haar-centered covariance:

```text
kappa_AB(R)
  = 1 - Var(Y_A - Y_B) / (Var(Y_A) + Var(Y_B)),
```

with the same evaluator inner product. Compute sufficient statistics within
each network first. For declared equal network weights, the panel statistic is

```text
kappa_panel = 2 sum_W Cov_W
              / sum_W (Var_A(W) + Var_B(W)).
```

Any nonuniform network weights must be applied consistently to numerator and
denominator. An arithmetic mean of per-network `kappa_W` does not support the
variance-ratio identity, though per-network values remain mandatory transfer
and heterogeneity diagnostics. Pooling raw outputs across networks would mix
different truths and invalidates the truth-cancellation identity. This
conditional statistic can screen covariance without reading truth.

It does not certify MSE because bias remains. Per fixed network `W`, define
`b_A(W)` and `b_B(W)` against that network's truth and define `kappa_W` from
the within-network Haar variances. The complete decomposition is

```text
MSE_pair = E_W[
    ||(b_A(W) + b_B(W))/2||^2
    + (Var_A(W) + Var_B(W))(1 + kappa_W(R))/4
].
```

A premise gate must use whole networks as clusters, a predeclared fixed sample
size or always-valid confidence sequence, and one frozen primary `P_AJ`.
Passing covariance earns only a separately authorized bias/score gate.

## E8 — authority and evidence quarantine

The sealed challenge charter and accepted amendment forbid new scientific
execution until both proposals are committed and revealed. The disclosed
ladder is expressly not a proposal and grants no execution authority.

Accordingly:

- post-charter R0 harmonic computations were not among the five disclosed
  grandfathered U-F1 runs and are process-unauthorized;
- post-charter M192 self-anchor measurements were not disclosed as in flight
  and are process-unauthorized;
- post-charter executions under `cmd2_static_diagnosis`--
  `absolute_gate_probe.py`, `threshold_bisect.py`, and the executable numerical
  portions of `independent_arithmetic_check.py`--are process-unauthorized and
  their outputs are quarantined. The original pre-charter `cmd2.err` log and
  static conclusions independently derivable from source remain admissible;
- a Codex authority auditor accidentally executed new NumPy comparisons of
  P2 frame means against S11 `f126` and M181 baseline arrays, plus a computed
  completion aggregate, despite an explicit no-execution instruction. Every
  resulting shape, hash, equality/mismatch, maximum-difference, and aggregate
  observation is quarantined and must not be cited as common evidence.

Static algebra and source inspection remain admissible. Owner adjudication may
admit a fully disclosed artifact prospectively and symmetrically as common
evidence, but cannot retroactively authorize its execution or erase the process
violation. Otherwise a fresh, prospectively authorized reproduction is
required; prose cannot self-ratify results.

## E9 — next lawful sequence

1. Codex seals one exact proposal hash. Opus seals one exact proposal under the
   accepted charter, or the owner first approves an append-only amendment that
   permits an exact canonical `NULL` proposal hash.
2. Both reveal exact bytes and independently verify both hashes.
3. Both write hostile rebuttals; `BOTH_KILLED` remains valid.
4. Reveals do not authorize execution. Only then may a separate immutable,
   owner-approved and charter-compliant authority authorize the no-forward
   matrix-contract test and exact cache census.
5. Any M4b network forward requires a distinct immutable predeclaration,
   implementation/test freeze, independent static PASS, resource meter,
   provisional receipt, and terminal witness.
6. No arm becomes a candidate without matching bias, variance, billed FLOPs,
   residual wall, peak memory, failure, transfer, and integrated-score evidence.

## Disposition

`W0`, Kerdock v3.1 GUARDS, remains the sole winner. The anti-J branch is an
unearned high-upside premise with a repaired mathematical target. No forward,
mutation, score gain, or contest credit is claimed.
