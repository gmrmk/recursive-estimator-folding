# M201 repeated-label contraction no-go

## Scope and provenance

Generation 6 Candidate A proposed commuting the downstream Source211
contraction through the exact one-dimensional conditional integral and then
collapsing the repeated-label axis. That mechanism and its width-3/4 symbolic
falsifier were written in `GEN6_DEFINITIVE_ATTACK_20260809.md` before this
derivation, but that parent planning document was not hash-frozen. M201 is
therefore recorded as an exact mathematical audit, not as an empirical
one-shot promotion experiment.

No contest row, truth, scorer, leaderboard, submission, or private artifact is
used. The executable witness uses exact integer/Fraction arithmetic.

## Exact conditional obstruction

For pairwise-distinct labels, conditioning on the repeated coordinate gives

```text
I_(i;jk) = integral phi(g) (mu_i + sigma_i g)^2 B^(i)_jk(g) dg,

B^(i)_jk(g) = E[(X_j)_+ (X_k)_+ | X_i = mu_i + sigma_i g].
```

Both the conditional mean and the Schur complement

```text
C^(i)_jk = C_jk - C_ji C_ik / C_ii
```

depend on `i`. Fubini permits contraction *inside each fixed-i integrand*, but
does not create one reusable `B_jk`: moving the `i` sum ahead of the primitive
requires an exact finite separation in the repeated-label mode.

## Width-3 rank witness

Take the full-rank integer source weight

```text
W = [[1,2,1],
     [2,1,3],
     [3,4,2]],        det(W)=5.
```

Let `d1=d_123=d_132`, `d2=d_213=d_231`, and
`d3=d_312=d_321`, with M151's exact half owner. Three entries of the emitted
`aaab` slot are

```text
[S00]   [ 72 144 216] [d1]
[S01] = [105 156 279] [d2]
[S02]   [ 75 168 207] [d3].
```

The determinant is exactly `116640`, so the downstream source-slot action
retains all three repeated-label coefficients. A generic M198 context does not
annihilate `aaab`. Any mechanism that collapses the repeated-label axis before
evaluating its `i`-dependent conditional law is therefore inexact even at
width 3.

This is already an interior obstruction: for

```text
C = D ((3/4) I + (1/4) 11^T) D,  D=diag(1,2,3),
mu = epsilon (1,2,-1), epsilon != 0,
```

`C` is full-rank SPD and the three noncentral conditional laws differ. M131's
surviving `Q3` term prevents cumulant/tree subtraction from converting them to
one pair-only object.

## Disposition

`KILLED_EXACT_COMMUTE_THEN_COLLAPSE_REPEATED_LABEL_AXIS`.

The lawful reassociation

```text
sum_i integral phi_i(x) x^p
              sum_(j,k distinct from i) Lambda(F_ijk) B^(i)_jk(x) dx
```

survives, but still has one trivariate/conditional channel per repeated label.
Moving the distinct projector introduces physical `[4]`, `[3,1]`, and `[2,2]`
collision owners; masking them reopens M155's Khatri action. A finite
Fourier/Hermite/polarization bank is an approximation, and an exact phase
integral is another trivariate quadrature.

This no-go is deliberately narrow. It does not prove that every future
arithmetic circuit for a specially structured approximate control is
impossible. It kills the generic exact contraction-before-enumeration mechanism
that Generation 6 Candidate A proposed.
