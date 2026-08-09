# M207 predeclaration -- zero-variance totality guard for M204 rank-one state

Date: 2026-08-09.  This child is predeclared after the M204 adversarial audit
found that `build_rank_one_b1_state(mu, V)` raises when every `V_ii` is zero.
It is response-free.  It does not read a contest model, truth, scorer,
leaderboard, submission, source-variance result, MSE, or score.

## One changed mechanism

M207 does not alter M204.  It supplies a separate wrapper for a labelled
background `(mu, V)`:

```text
if any V_ii > 0:  return the unmodified M204 construction
if all V_ii = 0:  omega_0 = omega_1 = 1/2,
                  conditional_mean_s = mu,
                  conditional_variance_s = 0,
                  u = 0,
                  d = 0.
```

The all-zero branch is the deterministic conditional moment functional.  Its
canonical covariance is zero, its M204 `dtilde` control is zero, and its
complete-domain source control is zero.  It carries the original deterministic
mean `mu`; it does not replace it with zero or reject the state merely because
the rank-one control is absent.

## Required generated-only checks

1. The unwrapped M204 constructor is shown to reject the all-zero case.
2. M207 returns a finite 49-node state with unit weight, `u=d=0`, zero
   canonical covariance, and a zero control/source on all-zero fixtures.
3. Mixed zero/nonzero diagonal rows remain valid and agree bit-for-bit with
   M204's original positive-active construction.
4. Positive-diagonal fixtures agree bit-for-bit with M204.
5. Hidden-label permutation and positive-gauge covariance hold, including
   all-zero and mixed-zero fixtures.
6. The complete ordered source compiler still agrees with the brute oracle.

Any failure kills M207.  A pass repairs only totality of the *response-free
rank-one state wrapper*.  It does not reopen M204's killed replacement premise,
does not provide a physical collision owner, and does not waive M204's cost,
provider, source-transport, or variance gates.

## Stop rule

Do not modify M204 in place.  Do not create a source-variance runner or run
any efficacy/score evaluation.  M207 stays a separately named algebraic guard.
