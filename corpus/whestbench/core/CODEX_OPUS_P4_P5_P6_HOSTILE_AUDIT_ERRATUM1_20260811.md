# Codex--Opus P4/P5/P6 Hostile Audit: Erratum 1

Date: 2026-08-11

Status: append-only mathematical correction; no scientific execution, proposal
seal, implementation, promotion, launch, or submission authority.

## 1. Exact parent and scope

This erratum binds and corrects only:

- `corpus/whestbench/core/CODEX_OPUS_P4_P5_P6_HOSTILE_AUDIT_20260811.md`;
- Git commit `c0e44c2`;
- SHA-256
  `A70395D7FBE388FD97689A85F021D03547CCA3CE710F901A49BD7317A35C9635`;
- parent sections 3.7 and 5.2.

The P4 degree-2 counterexample, the corrected P5 sphere measure, the P6
quadratic algebra, and the equation-level distinction between an input-space
anti-J operator and the killed diagonal odd/even surrogate remain unchanged.
The following corrections supersede the affected cost and covariance wording.

## 2. E1 -- the conditional sphere-JVP bill is not a sealed kill

Parent lines 312--322 gave the numbers

```text
85,094,178,120
 8,032,542,476
----------------
93,126,720,596
```

and therefore the conditional sum

```text
180,098,839,202 + 93,126,720,596
  = 273,225,559,798
  = 272,000,000,000 + 1,225,559,798.
```

Those additions are exact.  The archive independently binds the parent cost,
the 64,512 production rows, 28 sampled middle layers, the net-101 minimum and
maximum active widths, the terminal `a28/k30/k31/k32` counts, and the installed
one-level dispatcher.  It does **not** preserve the complete 28-layer active-
width vector or a line-by-line immutable reconstruction of the two quoted
tangent subtotals.  The subtotals are therefore quarantined as a reported
static worksheet pending an exact operand-census derivation and independent
reproduction.  They carry no theorem-level lower-bound or family-kill credit.

The corrected disposition is:

> The currently described unfused full-node sphere-JVP implementation is not
> cleared for production.  Before it may be called killed by cost or admitted
> as feasible, a separately frozen worksheet must bind every operand shape,
> dispatcher branch, vector operation, allocation, residual charge, and exact
> parent composition.  A fused, subset, or different carrier is a distinct
> implementation and is not closed by the conditional arithmetic above.

The zero-mean sphere identity and complete-frame degree-0/2 annihilation remain
exact.  They justify premise triage, not an unarchived cost conclusion.

## 3. E2 -- exact within-fold covariance normalization

For each fold separately, freeze `S_A>1` or `S_B>1` predeclared iid pilot
states.  For fold A, with raw layer states `h_s in R^n`, define

```text
hbar_A = (1/S_A) sum_s h_s,
z_s    = h_s - hbar_A,
Z_A    = [z_1 ... z_SA] in R^(n x S_A),
Sigmahat_A = Z_A Z_A^T / (S_A - 1).
```

Use the analogous definition for fold B.  Thus the previously unspecified
`empirical_centered_covariance` means the Bessel-normalized sample covariance,
not division by `S`.  This convention is unbiased for iid states with an
empirically fitted fold mean.  If the states are dependent, antipodally linked,
or taken from another structured design, this formula is not automatically
unbiased: the proposal must instead freeze and prove an exact design-specific
expectation correction or fail closed.  If a known, non-estimated mean is used,
the normalization and null rank change and must be declared separately.

The weight-only reference `Sigma_l^0` must be a centered covariance under the
same mean convention, not an uncentered ReLU second moment.  Its common exact
chart `W_l^0` must be fixed independently of folds A/B, square, and nonsingular,
with

```text
W_l^0 Sigma_l^0 (W_l^0)^T = I.
```

Whitening from either empirical fold is circular and cannot be full-rank when
`S<n`.  A rectangular or pseudowhitener is a different construction whose
subtracted null is the chart projector rather than `I_n`.  For the square
chart above, let

```text
Y_A = W_l^0 Z_A,
E_l^A = Y_A Y_A^T / (S_A - 1) - I.
```

This is exactly

```text
W_l^0 (Sigmahat_A - Sigma_l^0) (W_l^0)^T.
```

No epsilon ridge or floor is introduced.

## 4. E3 -- exact factorized residual action

The parent action must distinguish raw and chart coordinates.  For a raw JVP
`t_l=K_l^B q`, compute

```text
a_l = W_l^0 t_l,
r_l = Y_A^T a_l,
b_l = Y_A r_l / (S_A - 1) - a_l,
s_l = omega_l (W_l^0)^T b_l.
```

Then the reverse contribution is exactly

```text
(K_l^B)^T s_l
  = omega_l (J_l^B)^T E_l^A J_l^B q.
```

Summing the stopped-gradient sources in one reverse sweep and averaging the
per-state results over B gives `H_AtoB q`; interchange A and B for the other
direction.  This preserves the parent conclusion that a dense Jacobian and the
old all-output `O(n^4)` adjoint are unnecessary.

## 5. E4 -- the quoted anti-J action cost is not a lower bound

Parent lines 542--552 called

```text
[2*32 + 32] * (2*256^2 - 256) = 12,558,336
```

a static lower bill, then multiplied it to `12,859,736,064` and
`13,931,380,736`.  The arithmetic is correct for the declared partial
worksheet that assigns one dense `256 x 256` matrix-vector bill to each of 32
forward, 32 reverse, and 32 residual actions.  It is **not** an algorithmic
lower bound.

The factorized residual action above uses, before vector scaling and
subtraction,

```text
S(2n-1) + n(2S-1)
```

scalar operations for the two `Y` products.  At `n=256,S=128`, that expression
is `130,688`, compared with `130,816` for one dense `256 x 256` product.  This
does not by itself promise a material saving at the frozen dimensions; it does
prove that dense materialization is not compulsory and that no lower-bound
theorem was supplied.  Centering, formation or reuse of `Y`, whitening,
scaling, subtraction, JVP/VJP fusion, batching, Ritz work, memory, and residual
charges still require an exact implementation-specific bill.

Accordingly, the three parent totals survive only as a **partial static
worksheet for the declared precomputed-dense-`E` schedule**.  They do not price
the displayed implicit-`Y` route.  Any future proposal must freeze its actual
factorized or dense carrier and its complete FlopScope and wall/memory
accounting before a pilot.

## 6. E5 -- exact finite-sample null language

With empirical centering,

```text
rank(Y_A) <= S_A - 1,
rank(E_l^A + I) <= S_A - 1.
```

Therefore `E_l^A` has at least `n-S_A+1` exact eigenvalues `-1`.  For
`n=256,S_A=128`, the lower count is 129.  The corrected inference is:

> Negative eigenvalues are guaranteed even under the exact null, so their sign
> or count alone is non-evidence.  Under an alternative, a negative mode is not
> automatically a false discovery; it must beat the fully replayed null.

The required null must replay centering, normalization, whitening, both
cross-fit directions, construction and symmetrization of `H`, eigenselection,
and any rank choice under an exact null-preserving resampling or permutation.
A random rank-matched projector remains a useful orientation control, but it is
not a substitute for that finite-sample pipeline null.

## 7. E6 -- scope of the ideal break-even inequality

The parent inequality

```text
R^2 > r/(1+r)
```

is an ideal scalar-control threshold only when `R^2` is measured on an
independent fold, the coefficient is optimal without a fitting penalty, bias is
unchanged, and both parent and child remain on the same linear `C/B` score
branch.  It is not a universal contest-score theorem.  A proposal must use the
announced Phase-2 score law and bill before turning it into a gate.

## 8. Authority and disposition

This erratum was derived by static source and algebra review only.  It does not
authorize scientific execution and does not amend the sealed Codex--Opus
competition charter.  No anti-J proposal has yet been committed/revealed under
that charter, and GUARDS remains the only integrated artifact.

The truthful frontier after this correction is narrower and stronger:

- the operator interface remains mathematically coherent;
- the unavoidable rank-deficient null is now exactly normalized;
- a factorized action exists, so dense-residual cost is implementation-specific;
- neither feasibility nor cost-kill is earned without an immutable complete
  bill;
- no score, promotion, provider, or submission credit is granted.
