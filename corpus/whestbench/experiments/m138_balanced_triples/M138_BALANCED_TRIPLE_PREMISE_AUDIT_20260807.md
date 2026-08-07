# M138 balanced factored `[2,1,1]` triples — generated-only premise audit

**Verdict: KILLED_IMPLEMENTATION / PRESERVED_BALANCING_OPERATOR.**  The
operator is exactly unbiased, retains M133's fixed cost shape, and passes its
small algebraic oracles.  Its first output-functional premise screen does not
meet the predeclared variance gate at fixed `K=512`, so it is not promoted,
combined with M133, or used in any candidate evaluation.

This is a clean generated-only audit.  It opened no challenge weights,
instances, truths, scorer, leaderboard, submission package, or champion.

## One changed mechanism

M133 drew independent ordered triples from its O(n^2) factored proposal

```
q(i,j,k) = eps/[n(n-1)(n-2)]
         + (1-eps) r_i^2 r_j r_k
           (S_ij S_ik + S_ij S_jk + S_ik S_jk)/(Z_A+Z_B+Z_C),
eps = 0.05,
```

with `i,j,k` distinct, `S=abs(Q-I)`, and `r_i=||W_i||`.  M138 preserves that
proposal and its five rectangular output products exactly.  It only couples
the `K=512` rows:

1. randomized systematic allocation for the unchanged uniform/A/B/C mixture;
2. randomized systematic centres within each occupied A/B/C stratum; and
3. a randomized shifted-Hammersley/Latin conditional pair for the two
   neighbour inverse-CDF draws, followed by a uniform permutation of the K
   labelled output rows.

The retained optional antithetic OA variant was a more adverse preliminary
width-32 screen, so it is recorded but not selected as the M138 operator.
There is no score/envelope retuning and no full triple catalogue.

The motivation is classical randomized stratification, not a claim that
low-discrepancy coupling must help a nonsmooth ReLU response.  McKay, Beckman,
and Conover establish the unbiasedness/variance rationale for randomized
Latin hypercubes in the relevant class of computer experiments
([original paper](https://www.stat.cmu.edu/technometrics/70-79/VOL-21-02/v2102239.pdf)).
Cranley and Patterson give the random-shift principle used to make a
low-discrepancy point set into a stochastic integration rule
([original paper](https://epubs.siam.org/doi/10.1137/0713071)).  Neither result
implies an improvement for this weighted, discontinuous inverse-CDF map; that
is why the output test below is the gate.

## Exactness certificate

Let `C_t` be the mixture-bank label for row `t`.  Randomized systematic
allocation has `E[N_c]=K pi_c`.  The final uniform row permutation makes every
labelled row exchangeable, therefore

```
P(C_t=c) = E[N_c/K] = pi_c.
```

Conditional on an occupied factored bank, the same argument for the systematic
centre draw gives its declared centre distribution.  For a fixed labelled row,
the Latin first coordinate has a random stratum and jitter, and each shifted
radical-inverse coordinate has an independent uniform torus shift.  Its two
neighbour uniforms are consequently jointly `Unif([0,1)^2)`.  Inverse-CDF
sampling therefore gives the original A/B/C conditional law.  The rescue bank
uses the same construction in three coordinates and maps it bijectively to an
ordered distinct uniform triple.  Thus every labelled returned row has exactly
the original M133 `q(i,j,k)` marginal.

All ties and accidental collisions are deterministically killed: the first
neighbour's selected label is assigned zero mass before the second inverse
CDF, all inverse-CDF boundary ties select the next positive-mass interval, and
the code rejects a non-distinct row.  The 5% rescue retains positive support
for every distinct triple.  The singleton-order swap `(i,j,k)<->(i,k,j)` has
the same coefficient and twelve-slot feature; the existing `1/(2 K q)` scale
therefore owns each canonical `i;j<k` term exactly once.

For a background-frozen `q_0`, the M133/M138 pathwise derivative remains

```
d/dtheta E_q0[F(theta)/q0] = E_q0[Fdot(theta)/q0].
```

The sample dependence affects covariance, not the one-row marginal or the
pathwise identity.  No `qdot` term is legal or needed.

## Oracles and accounting

Six generated-only tests pass:

1. vectorized exact `[2,1,1]` oracle equals the canonical twelve-slot loop;
2. aggregate balanced rows recover the complete parent `q` marginal;
3. all rows are distinct and left/right permutation preserves the HH result;
4. a balanced draw passes the finite-difference frozen-`q` Frechet tangent;
5. complete M121 one-delay conversion plus M125b recurrence equals explicit
   suffix superposition for both mean and covariance; and
6. target accounting has zero additional rectangular products and zero triple
   catalogue entries.

At `n=256`, `K=512`, and 31 layers, the conservative scalar/copy/gather/sort
increment is `228,556,800` raw and `285,696,000` protected operations.  Added
to M133's already conservative complete first-order kappa-2 worksheet
`94.940940240B`, it is `95.226636240B`, below 100B.  This does **not** repair
any other M133/source/carrier uncertainty; it merely clears this mutation's
incremental accounting gate.

## Decisive output-functional premise screen

Each fresh generated cell used a valid Gaussian/ReLU chain of depth four.  At
every source layer it made the actual post-ReLU bridge, constructed the
quadratic `[2,1,1]` coefficient, applied the full M121 mean-and-covariance
conversion, and coalesced all sources through the M125b inhomogeneous suffix.
The metric is final mean-output MSE against a vectorized exact small-width
`[2,1,1]` reference.  It is **not** source Frobenius norm.

The fixed early premise screen used M133's four development seeds, 16
independent response randomizations per cell, `K=512` at every width, and no
common-random cancellation between iid and balanced arms.  The full
128-replicate development and disjoint confirmation were predeclared to run
only if this cheap premise met the effect direction.  It did not, so they were
not opened.

| width | balanced / iid final-output MSE | disposition |
|---:|---:|---|
| 12 | 0.68694 | local favorable but unstable |
| 16 | 1.08694 | adverse |
| 24 | 0.92815 | above gate |
| 32 | 1.00248 | adverse |

The required gate was pooled ratio `<=0.75`, an upper-90% ratio below `0.90`,
and no adverse width trend.  The screen violates all three: the width sequence
is nonmonotone/adverse, widths 16 and 32 are above parity, and cellwise upper
90% ratios ranged from `1.21` to `7.96`.  The independent antithetic-OA
variant also produced width-32 ratio `1.099` in the same fixed 16-replicate
premise, so it was not substituted after the fact.

## Salvage map

* **Preserved:** exact O(n^2) factored q; systematic centre construction;
  randomized conditional Latin/OA utility; deterministic collision/tie rules;
  frozen-q tangent; complete output-functional harness; cost calculation.
* **Killed implementation:** centre/systematic plus conditional OA balancing
  alone at `K=512` cannot safely repair M133's output-level variance deficit.
* **Untested, still open:** a new unbiased control variate or an exactly
  conditionally integrated observable.  That would be a different mechanism,
  must pay its own cost, and may not be relabelled as M138.

No efficacy or contest evaluation is authorized from this artifact.
