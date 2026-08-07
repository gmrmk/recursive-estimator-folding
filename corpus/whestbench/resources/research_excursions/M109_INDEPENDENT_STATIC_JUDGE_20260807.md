# M109 independent static judge — 2026-08-07

## Binary disposition

**FAIL — do not freeze or run a generated network for the current M109 draft.**

This is a static mathematical failure, not a finding about the broader family
of bounded gate-occupancy controls.  No MLP, contest instance, scorer, target,
or submission artifact was run or modified for this audit.

## Independent calculation of the spherical probability

For `U ~ Unif(S^(d-1))` and a unit vector `a`, `T=a.U` has density

```text
f_d(t) = Gamma(d/2) / (sqrt(pi) Gamma((d-1)/2))
         (1-t^2)^((d-3)/2),  -1<t<1.
```

Thus for `d=256` the exponent is **126.5**, and

```text
P(|T| <= 1/16) = I_(1/256)(1/2, 255/2)
               = 0.68174151824134440702724427524261793438128145340916676300176860652683781465121576471930478207314735154551264739774652570560463612775821697079...
```

I computed this without the draft's beta-polynomial route.  Put
`theta=asin(1/16)`, `J_0(theta)=theta`, and recursively define

```text
J_(2m)(theta) = sin(theta) cos(theta)^(2m-1)/(2m)
                + (2m-1)/(2m) J_(2m-2)(theta).
```

Then the exact probability is

```text
J_254(theta) / J_254(pi/2),
J_254(pi/2) = pi*binom(254,127)/(2*4^127).
```

I evaluated the recurrence at 140 Decimal digits, with `asin(1/16)` obtained
as `atan(1/sqrt(255))` and pi independently computed with Machin's formula.
The draft's embedded value is instead

```text
0.682130341244403596600209971528792...
```

and differs by `+0.000388823003059189572965696286...`.  It is exactly the
draft's stated finite polynomial, but that polynomial has the wrong exponent:
it integrates `(1-t^2)^126`, whereas `S^255` requires
`(1-t^2)^(253/2) = (1-t^2)^126.5`.

The prefactor written in the draft happens to be the correct `d=256` density
prefactor.  Pairing it with exponent 126 is not a normalized density.  This
is why the source test's independently named polynomial test would agree with
the erroneous embedded value: the test repeats the same dimensional mistake.

### Consequence

The implemented atom has conditional spherical mean

```text
E[h_j(U) | W] = p_true - p_draft
              = -0.000388823003059189572965696286...,
```

not zero.  Therefore both mixtures have this same nonzero mean, independently
of the frozen nonnegative mixture weights.  The exact-zero assertion, which is
the sole admissibility mechanism of M109, is false as written.

## Gauge and representation audit

The **uniform** normalized-axis mixture is invariant under the positive ReLU
gauge at the first hidden layer: `W1[:,j] -> c_j W1[:,j]`,
`W2[j,:] -> W2[j,:]/c_j` for `c_j>0`, because its axes are normalized and its
weights are uniform.

The draft's **squared-path** mixture is *not* invariant.  Under that same
function-preserving gauge its back-propagated path component at `j` gains a
factor `c_j^-2`, while the normalized gate axis is unchanged.  Its mixture
therefore changes even though the represented ReLU function does not.  The
per-layer normalization in `frozen_mixture_weights` only removes common
scalars; it cannot remove a coordinatewise `c_j^-2` factor.

If this branch is reopened after fixing the probability, a gauge-invariant
path proposal would need a new static proof.  A natural *new mutation* (not
approved here) is to multiply the first-layer path component by
`||W1[:,j]||^2` before its final normalization.  That cancels the first-layer
gauge factor, but it changes the specified operator and must start its own
full validation ladder.

Permutation invariance in the current source is sound, provided the matching
row/column relabeling is used.  The reuse identity
`first_pre/(rho_256*||W1[:,j]||)` is also algebraically sound if and only if
the supplied `first_pre` was actually formed as `(rho_256*Q)@W1` in the stated
row-point convention.

## Frame variance and tail audit

The bounded atom does solve the specific M108 amplitude pathology:

```text
-p <= h_j <= 1-p,
p(1-p) = 0.216... for an individual spherical direction.
```

Consequently neither individual atoms nor their convex mixtures can have the
astronomical unbounded-amplitude fourth moments that killed squared high-degree
zonals.  Antipodal pairing does not cancel this even atom, as the draft says.

But boundedness is not an efficacy result.  In a Haar frame the coordinates of
one axis obey `sum_i (a.q_i)^2=1`, so the 256 occupancy indicators are strongly
dependent at exactly this threshold (`c^2=1/256`).  For a weight-dependent
mixture of 256 nonorthogonal gate axes, the frame variance and standardized
kurtosis cannot be inferred from the one-axis beta law alone.  They require a
separate, preregistered target-free random-frame calculation.  No such
quantitative gate exists in the draft, and its current `2e-12` cosine guard is
not justified for an f32 L1 `first_pre`: it must be calibrated on an exact
known-input arithmetic test before any claimed reuse.

## Required corrections before any re-proposal

1. Replace the embedded probability with the value above; replace the false
   finite-polynomial identity and its duplicated test with the `J_254`
   recurrence (or an independently checked half-integer incomplete-beta
   implementation).
2. State the bias class after the correction: exact-zero conditional on a
   valid decoded spherical `first_pre`; reject rather than silently clip any
   material decode violation.
3. Split the two mixtures.  Uniform can be retained as a corrected fixed
   operator.  The squared-path version must either be labelled
   representation-dependent or replaced by a separately specified,
   gauge-invariant operator and new hash/validation ladder.
4. Before a network forward, freeze a target-free gate that independently
   checks: corrected `p` to >=80 decimal places; exact means on a
   deterministic spherical quadrature/symmetry construction; all stated
   permutation and positive-gauge invariances; f32 decode excursion bounds;
   and finite empirical frame variance/kurtosis for each predeclared mixture.
5. Only if every item passes may a new generated-network premise packet be
   authored.  That later packet must set regression, cost, and held-out
   covariance criteria before its first forward pass.

## Salvage map

Preserve: radialization; normalized W1 gate axes; the `first_pre` reuse
identity; bounded nodal occupancy as a classical operator; permutation
invariance; and the no-threshold-sweep firewall.

Kill only: the current exact M109 source/configuration, because its stated
mean is false.  The corrected uniform bounded-occupancy family remains
unresolved, not supported.
