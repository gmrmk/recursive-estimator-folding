# M202 signed-facet Feynman--Kac/SMC no-go

## Scope

Generation 6 Candidate D preserved M86's exact signed spherical-facet identity
and asked whether an unnormalized Feynman--Kac/SMC estimator could avoid exact
fan enumeration. M202 audits that mechanism only. It does not invalidate the
coarea identity.

No contest model, truth, scorer, leaderboard, submission, or private artifact
is used. The counterexample is a two-dimensional, width-two, depth-two ReLU
network and is verified with exact rational arithmetic.

## Exact identity and missing probability law

For a scalar homogeneous CPWL output `f`, the spherical mean is proportional to
the signed mass of **owned output facets**:

```text
sum_F integral_F [normal derivative of f] dH^(d-2).
```

Raw gate labels are not owners: cascaded ReLUs can label the same output facet
more than once. An absolute-particle proposal would need the global mass

```text
A = sum_F integral_F abs(jump_F) dH^(d-2)
```

and sign ratio `rho=abs(Z)/A`. Even the optimal absolute proposal has relative
variance `rho^(-2)-1` and signed ESS at most `N*rho^2`.

## Minimal sign-collapse and ownership witness

For `0<epsilon<1`, take

```text
f_epsilon(x) = ReLU(ReLU(x1))
               - (1-epsilon) ReLU(ReLU(x2))
             = [x1]_+ - (1-epsilon)[x2]_+.
```

On `S^1`, the two coordinate boundaries each meet the circle twice. The owned
output-facet masses are

```text
signed mass   Z = 2 epsilon,
absolute mass A = 2 (2-epsilon),
rho             = epsilon/(2-epsilon).
```

Thus `rho -> 0` as `epsilon -> 0`; there is no network-uniform polynomial
lower bound on signed ESS. Both ReLU layers label the same boundary, so a raw
gate sum doubles the correct owned-facet mass. The second-layer preactivation
also vanishes on an entire inactive arc, violating the regular-zero-set premise
of a naive Kac--Rice/Palm density.

## Why the proposed repairs do not open a distinct mechanism

- Kac--Rice rewrites a regular facet integral but still needs the owned deep
  zero-set sampler; zero plateaux and coincident boundaries violate the naive
  regularity assumptions.
- Crofton must include every crossing. A first-crossing rule is the Palm/HT
  inclusion-law problem already tested in M95.
- Russian-roulette smoothing has a `1/h` spike with probability `O(h)`, giving
  variance `Omega(1/h)` unless exact crossings are located; that returns to
  facet traversal.
- Absolute resampling retains the sign problem. Signed or self-normalized
  resampling is not an unbiased Feynman--Kac probability system.
- A brute operator-norm envelope must enumerate activation-pattern facets. The
  target first layer alone has `256*2^255=2^263` candidate central-hyperplane
  facet cells.

## Disposition

`KILLED_UNNORMALIZED_SIGNED_FACET_SMC_WITHOUT_OWNED_GENERATOR_AND_ESS_CERTIFICATE`.

Preserve M86's signed identity, output-jump collapse, and the small exact oracle.
Reopening requires a genuinely new analytically normalized generator of owned
output facets, plus a network-specific noncollapsing ESS and inclusive cost
certificate. No current Palm, coarea, Crofton, smoothing, or SMC artifact
provides that information.
