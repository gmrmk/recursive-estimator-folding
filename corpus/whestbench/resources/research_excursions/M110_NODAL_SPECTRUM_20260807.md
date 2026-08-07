# M110: exact spectrum of the bounded nodal-tube atom

**Scope.**  This is an analytic, target-free audit of the corrected M110
atom only.  No MLP, contest scorer, generated network, candidate source,
champion, ledger, or graph was touched.  The calculations below use the
spherical law directly; they are not an inference from a network outcome.

## Operator and exact law

Let `d=256`, `c=1/sqrt(d)=1/16`, `U ~ Unif(S^255)`, and let `a` be a unit
axis.  Write `T=a.U`.  The candidate atom is

```text
h_c(T) = 1{|T| <= c} - p,
p = Pr(|T| <= c) = I_(1/256)(1/2,255/2).
```

The coordinate density is

```text
w(t) = [4^127/(pi * binom(254,127))] (1-t^2)^(253/2),  -1<t<1.
```

Thus the correct certified constant and scalar variance are

```text
p       = 0.6817415182413444070272442752426179343812814534091667630...
Var(h_c)= 0.2169700205473310781538703933178614407171519722092174217...
```

This explicitly uses exponent `253/2=126.5`; an exponent `126` is the
M109 static-gate error and is not reused here.

For normalized zonal Gegenbauer polynomials `P_l(1)=1`, define

```text
q_l = E[h_c(T) P_l(T)],       D_l = dim H_l.
```

The fraction of the scalar variance in degree `l` is

```text
s_l = D_l q_l^2 / Var(h_c).
```

Only positive even degrees occur.  I evaluated the integral as an exact
Gegenbauer polynomial recurrence with rational coefficients and a
half-integer incomplete-beta recurrence at 180 and 230 decimal digits.
The two precisions agree on the displayed values.  No fitted or sampled
quantities enter the table.

| degree | `s_l`, fraction of `Var(h_c)` | cumulative through degree |
|---:|---:|---:|
| 2 | 0.5439180089 | 0.5439180089 |
| 4 | 0.1805461008 | 0.7244641097 |
| 6 | 0.05237470065 | 0.7768388104 |
| 8 | 0.009142493851 | 0.7859813042 |
| 10 | 0.0000148199370 | 0.7859961241 |
| 12 | 0.003366470329 | 0.7893625945 |
| 14 | 0.009494851163 | 0.7988574456 |
| 16 | 0.01433174306 | 0.8131891887 |
| 18 | 0.01660752061 | 0.8297967093 |
| 20 | 0.01640679020 | 0.8462034995 |
| 24 | 0.01135585330 | 0.8719470182 |
| 28 | 0.005004001961 | 0.8849936114 |
| 32 | 0.0009724444172 | 0.8885589814 |
| 40 | 0.001164604760 | 0.8903314431 |
| 80 | 0.001047223100 | 0.9276291327 |
| 120 | 0.0004457792432 | 0.9446679062 |
| 160 | 0.0001002905639 | 0.9550400429 |
| 200 | 0.0000002067589 | 0.9623800106 |

The non-monotone high-degree entries are real cancellation structure from a
hard step at `|t|=1/16`, not a numerical tail artefact: the same values are
obtained from the independent recurrence.  The unlisted tail is positive and
is 0.0376199894 through degree 200.  Hence this is a bounded but broad
high-even-spectrum operator, rather than a single spherical eigenmode.

## What a Haar orthonormal frame removes

For a Haar orthonormal frame `(Q_1,...,Q_d)`, the degree-`l` part of its
average has variance relative to an average of `d` iid directions

```text
R_l = 1 + (d-1) P_l(0).
```

This follows from the addition theorem: distinct frame directions have inner
product zero.  At `d=256`:

| degree | `P_l(0)` | `R_l` |
|---:|---:|---:|
| 2 | `-1/255` | `0` |
| 4 | `4.5777065690e-5` | `1.0116731518` |
| 6 | `-8.8372713687e-7` | `0.9997746496` |
| 8 | `2.3701494092e-8` | `1.0000060439` |
| 10 | `-8.1107774461e-10` | `0.9999997932` |

So a complete frame exactly annihilates degree two, very slightly amplifies
degree four (1.167%), and is effectively iid for degree six and beyond.
Antipodal completion supplies no additional independent observation for this
even operator.

Applying these multipliers gives the exact single-axis frame-block variance

```text
Var[(1/256) sum_i h_c(a.Q_i)]
  = 0.00038832360776...,
```

consistent with the separate Dirichlet frame calculation.  Equivalently,
after a frame the retained spectral factor is `0.4581777857` of the original
scalar variance, divided by 256.  The frame does *not* convert the atom into
a clean high-degree measurement; it simply removes its largest low-degree
component.

## Relation to the old first-layer absolute-value control

Let `g(T)=|T|-E|T|`; an antithetic first-layer ReLU control differs only by a
constant factor, so correlations are unchanged.  Exact beta moments give

```text
E|T| = 0.04991650772160573031521023637...
Corr(h_c,g) = -0.8230466472... .
```

The degree-two contribution is not the whole overlap:

```text
Var(h_c)_(>=4) = 0.09895611898263688...
Var(g)_(>=4)   = 0.00017364869285869...
Cov_(>=4)      = -0.00231756516050998...
Corr_(>=4)     = -0.5590811725... .
```

After the Haar-frame multipliers the corresponding residual correlation is
`-0.5614832246...`.  Therefore M110 is genuinely not *identical* to the old
absolute-value control after degree-two removal, but it remains substantially
redundant.  A claimed win must come from a final-network correlation that
survives this strong first-layer overlap; geometry alone does not establish
one.

## Physics/cymatic variants, reduced to ordinary operators

| proposed metaphor | exact mathematical operator | status |
|---|---|---|
| outer cap / one-sided shell | `1{|T|>c}-(1-p)=-h_c` | **NO-GO:** exactly the same feature with sign reversed. |
| nodal count across W1 axes | a fixed weighted sum of `h_(a_j)` | **NO-GO as new mechanism:** this is precisely the existing occupancy mixture.  A nonlinear count has no weights-only known spherical mean for nonorthogonal W1 axes. |
| arbitrary annulus or two thresholds | centered `1{a<|T|<=b}` or a contrast of such indicators | **NO-GO now:** exact beta means exist, but neither scale is fixed by the ReLU gate or contest symmetry.  Selecting them after outcomes would be threshold tuning. |
| degree-four Chladni cell | `sign(P_4(T))-E sign(P_4(T))` | **different but research-only:** bounded and parameter-free once degree 4 is declared, yet it lacks a gate-kink reason and is more redundant with `|T|` after frame removal. |

For the final row, the two positive-cell boundaries are the two roots of
`P_4(t)`:

```text
|t| = 0.04621279955792190...  (d t^2 = 0.5467194478...)
|t| = 0.14471109229752366...  (d t^2 = 5.3609728599...).
```

It is a literal bounded hyperspherical Chladni/standing-wave partition.  Its
degree shares begin `(l=2,4,6,8)=(0.21533, 0.33822, 0.17874, 0.05888)`, but
its degree-`>=4` correlation with the absolute-value control is about
`-0.785`.  It is therefore a genuine different harmonic construction, not a
copy of M110, but an analytic **NO-GO for immediate implementation**: degree
four was selected by aesthetic spectral language rather than a ReLU-specific
identity, and the residual redundancy is worse than M110's.

## Decision

**GO only for the already-corrected, fixed-width M110 nodal-tube atom through
its independent static and fresh generated-only gates.**  The reason is not
an asserted hidden resonance: it is a bounded, exact-mean measurement of an
actual ReLU gate hyperplane, with substantial degree-`>=4` content that the
frame leaves observable.

**NO-GO for sacred-geometry/cymatic variants as immediate mutations.**  The
cap is algebraically identical, a nonlinear axis count loses its exact mean,
and the parameter-free Chladni-cell variant is spectrally more redundant with
the already-failed absolute-value family.  Preserve the harmonic decomposition
and exact frame multiplier as constraints for any future, independently
motivated operator.
