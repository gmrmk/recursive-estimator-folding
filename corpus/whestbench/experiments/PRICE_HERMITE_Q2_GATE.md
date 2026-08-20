# Predeclared gate: Price--Hermite higher-moment response

Frozen before the synthetic accuracy run on 2026-08-06.

## Scope and firewall

- Synthetic bias-free He-ReLU networks only: fresh widths `8,12,16`, depths
  `2,4`, and seeds declared in `run_fresh_oracle.py`.
- Candidate formation receives only cell probabilities, means, the preserved
  `D + U U'` covariance state (`rank(U)<=4`), and the next weight matrix.
- Activation paths are used only by the evaluation oracle after candidate
  formation. No WHest row, truth, scorer, submission, API, or holdout is read.
- This is a premise test, not a leaderboard candidate.

## First proof gate

Prove that moments through order two cannot identify conditional `k3,k4`, even
for one nonnegative coordinate. The witness must use two laws with identical
mean and variance but different third/fourth cumulants. Consequently this
candidate is explicitly a rectified-Gaussian response prior, not an exact
arbitrary-law recurrence.

## Frozen enlarged state

Within each conditional cell, coordinate `i` is represented as

```text
X_i - E X_i ~= a1_i H1(Z_i) + a2_i H2(Z_i),
Z ~ N(0,R),              R = diag(s^2) + B B'.
```

The marginal rectified-Gaussian threshold and scale are the unique values
matching the supplied coordinate mean and variance. The coefficients are not
fit:

```text
a1 = sigma Phi(alpha),      a2 = sigma phi(alpha)/2.
```

These are the exact first two probabilists'-Hermite/Price coefficients of
`relu(sigma*(alpha+z))`. The latent common factor is frozen as

```text
B_raw[i,:] = U[i,:] / a1_i;
B[i,:]     = B_raw[i,:] / max(1, ||B_raw[i,:]||_2);
s_i^2      = 1 - ||B[i,:]||_2^2.
```

Thus the degree-one response reproduces the supplied off-diagonal covariance
before the necessary correlation-row clipping. No oracle tensor, regression,
sample cumulant, seed selection, or post-metric coefficient is permitted.

For a next-row weight `w`, put `b=w*a1`, `d=w*a2`, and `D=diag(d)`. The frozen
responses are the exact cumulants of the degree-two chaos:

```text
k3 = 6 b' R D R b       + 8 tr((D R)^3),
k4 = 48 b' R D R D R b + 48 tr((D R)^4).
```

They are transported with the exact scalar law of total cumulance and the
already supplied conditional means/variances. The implementation must evaluate
the formulas using diagonal-plus-rank-four algebra, never a dense `n^3` or
`n^4` cumulant tensor.

## Frozen gates

1. **Identity:** fast diagonal-plus-low-rank `k3,k4` agree with dense formulas
   to relative error at most `1e-10` on deterministic tests.
2. **Formation:** changing oracle activation paths while holding
   `(p,m,D,U,W)` fixed cannot change the candidate.
3. **Symmetry:** coordinate permutation and positive coordinate gauge
   (`m->g*m`, `D->g^2 D`, `U->g U`, `W->g^-1 W`) change directional results by
   at most `1e-10` relative.
4. **Validity:** all latent residual variances are at least `-1e-12`; report the
   fraction of rows requiring factor-norm clipping.
5. **Accuracy:** aggregate total standardized `k3`, standardized `k4`, their
   combined fidelity, and Edgeworth-correction fidelity are each at least
   `0.80`; material correction signs are at least `0.80`. The candidate must
   also improve combined fidelity over the zero-conditional-cumulant baseline.
6. **Complexity:** conservative float64 arithmetic plus `25%` contingency,
   when added to the inherited `39.326B` conditional-state envelope, is below
   `80B` at `n=256,L=32,B=16,r=4`.

Failure localizes the rectified-Gaussian degree-two response prior or its
factor inversion. It does not invalidate the exact Price coefficients, the
quadratic-chaos cumulant identities, total cumulance, or the preserved
`<=12D` terminal contraction algebra.
