# M145 cross-reference risk derivation (zero outcome)

Status: frozen mathematical specification only. No reference, risk, MSE, score,
rank, or efficacy outcome has been computed.

## 1. Reference construction

For a fixed network `W`, write

```text
I(W) = E_x f(x;W),                    x ~ N(0,I_256)
     = rho_256 E_u f(u;W),            u ~ Unif(S^255)
rho_256 = sqrt(2) Gamma(128.5)/Gamma(128)
        = 15.98438266660852747...
```

The second equality is exact in real arithmetic because the bias-free ReLU
network is positively one-homogeneous.  Let `D` contain one unit representative
from every row-line of the frozen 126-basis Kerdock design, so `|D|=32256`.
For an independent Haar matrix `Q` on `O(256)`, define

```text
R(Q) = rho_256/(2|D|) sum_{d in D} [f(Qd;W) + f(-Qd;W)].
```

For every fixed `d`, `Qd` is uniform on the sphere. Linearity of expectation
therefore gives `E_Q R(Q)=I(W)`. Dependence among points within one rotated
design affects variance, not the mean. Two independently seeded Haar rotations
give conditionally independent unbiased references `R1` and `R2`.

The implementation must evaluate the direct 32-layer network in float64 and
accumulate in float64. The cubature statement above is exact for the
mathematical network; finite-precision error is a separate numerical error and
must pass the independent-direct-evaluator gate in the protocol. It is not
silently declared unbiased.

## 2. Unbiased absolute risk

Fix `W` and condition on the realized estimator output `A`. Independence of the
reference generators from `A` is essential. Put

```text
delta = A-I,   R1=I+e1,   R2=I+e2,
E[e1|W]=E[e2|W]=0,        e1 independent of e2 conditional on W.
```

Then

```text
(A-R1).(A-R2)
  = (delta-e1).(delta-e2)
  = ||delta||^2 - delta.(e1+e2) + e1.e2.
```

Conditional expectation kills both linear terms. Independence gives
`E[e1.e2|W]=0`. Consequently,

```text
E[(A-R1).(A-R2)/256 | W,A] = ||A-I||^2/256 = MSE(A|W).
```

This remains true for a randomized estimator after taking an outer expectation,
provided its randomness is independent of both reference streams.

An individual cross-risk estimate may be negative. That is ordinary
finite-sample behavior of an unbiased estimator of a nonnegative quantity. A
negative estimate must not be clipped, discarded, replaced, or treated as a
failure.

## 3. Paired candidate-comparator cancellation

Use the same `R1,R2` for candidate `A` and comparator `B`. Subtraction gives

```text
[(A-R1).(A-R2) - (B-R1).(B-R2)]/256
 = [||A||^2-||B||^2 - (A-B).(R1+R2)]/256.
```

The noisy quadratic term `R1.R2` cancels exactly. Thus the statistic is unbiased
for `MSE(A|W)-MSE(B|W)` and usually has much less reference variance than the
difference of independently referenced absolute risks. Frozen cost multipliers
may be applied before subtraction if they are measured independently of the
reference streams; conditioning on those multipliers preserves the same proof.

For conditional covariance matrices `Sigma1,Sigma2`, direct expansion gives

```text
Var(risk_A | W,A)
  = [delta^T(Sigma1+Sigma2)delta + tr(Sigma1 Sigma2)] / 256^2,

Var(risk_A-risk_B | W,A,B)
  = [(A-B)^T(Sigma1+Sigma2)(A-B)] / 256^2.
```

The trace term is precisely the variance removed by common-reference pairing.

## 4. Frozen inference

There are eight independent `(R1,R2)` pairs for each of the 24 frozen generated
networks. Every pair is retained. In each of 100,000 joint hierarchical
bootstrap draws, network indices are resampled first and eight reference-pair
indices are resampled within every selected network occurrence. Candidate and
comparator use exactly the same resampled indices.

Absolute estimates, paired differences, and bootstrap draws are never clipped.
If a bootstrap comparator aggregate is nonpositive, the ratio is undefined for
promotion and the frozen experiment is declared ambiguous. The paired adjusted
risk difference remains the primary statistic because it avoids that unstable
division and benefits from the exact common-reference cancellation.

## 5. Compute boundary

One 64,512-path direct reference has a dense-matmul bill of 270,054,457,344
operations before activations and overhead. Sixteen references per network and
24 networks imply a dense-plus-activation lower bound of 103,903,848,824,832
operations. This is an offline validation campaign, never submitted estimator
compute. It is feasible only with a streamed one-basis-at-a-time implementation,
a wall-time dry run, and an independent audit. None of that execution is
authorized by this derivation.
