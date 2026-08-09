# M197 predeclaration -- three-rotation crossed covariance U-statistic

Date: 2026-08-08.  Written before the M197 runner or results exist.

## Frozen boundary

M197 is a same-cache mechanism falsifier only.  It reads the frozen P2 cache
for synthetic He networks 101, 202, and 303: 16 independent Haar rotations,
126 complete Kerdock frames per rotation, and 256 final outputs.  It reads
M181 cached truths only after all predictions are constructed, solely for
scoring.  It runs no forward pass, official scorer, submission, private
instance, or production source.

The prior M192 result is a truth-oracle covariance signal.  M193 showed that
the diagonal analytic anchor corrupts the required common/contrast covariance
block.  M194 showed an independent pilot estimates that block too noisily at
added cost.  M195 used two 63-frame independent rotations at equal total
frame count and was killed.  M197 changes the information topology, not a
ridge or subset tuning: each correction sees two independent pilot rotations
rather than one, with all 126 evaluated frames retained.

## Fixed geometry and pairing

Use exactly five disjoint rotation triples

    (0,1,2), (3,4,5), (6,7,8), (9,10,11), (12,13,14).

Within each rotation use exactly the first 42 complete frames.  Hence the
candidate evaluates 3 x 42 = 126 complete frames.  Rotation 15 is unused.
The primary comparator is the archived full 126-frame uniform mean from the
first rotation of the same triple; it also evaluates 126 frames.  The
diagnostic comparator is the uncorrected equal mean of all three 42-frame
groups.  No rotation, partition, frame prefix, lambda, or result-dependent
selection is allowed.

## Operator

For a triple, write X_r in R^(42 x 256) for r=0,1,2, let

    q_r = (1/42) 1^T X_r,
    Z_r = X_r - 1 q_r^T,
    P_42 = I - 11^T/42.

Split outputs by the fixed rule H_f = {j: j mod 8 = f}.  On training outputs
T_f, set

    A_r = Z_r[:,T_f] Z_r[:,T_f]^T / |T_f|,
    tau_r = tr(A_r)/41,
    h_r = Z_r[:,T_f] [q_r[T_f] - (q_s[T_f]+q_t[T_f])/2]
          / (3 |T_f|),

where {r,s,t}={0,1,2}.  Fix lambda=1/3 and solve in the contrast subspace

    v_r = -(A_r + lambda tau_r P_42)^+ h_r,
    1^T v_r = 0.

The held-output prediction is

    mhat_j = sum_r [(1/(3*42)) 1 + v_r]^T X_r[:,j].

The unknown target mean mu_j cancels algebraically from each q_r-q_-r.  Under
independent Haar rotations, E[Z_r(q_r-q_-r)] is the required r-th
common/contrast covariance.  The factor 1/3 is the fixed objective scaling
for the equal three-group baseline.  This is a cross-fitted, deliberately
biased data-dependent estimator, not an exact estimator.

## Required unit checks

Before scoring, the runner must verify for every fit that each v_r is finite
and sums to zero within 1e-10, and each combined 126-frame weight vector sums
to one within 1e-10.  It must also inject an arbitrary output-dependent vector
delta into every frame of all three groups and verify that every h_r is
unchanged to 1e-11 absolute tolerance.  This checks the unknown-mu
cancellation directly without consulting truth.

## Gates

Primary statistic: geometric mean across the three networks of the ratio of
mean candidate MSE to mean matched full-126 baseline MSE over the five
disjoint triples.  Report a triple-cluster bootstrap interval and the
uncorrected 3x42 diagnostic ratio.

Kill M197 if the panel reduction is below 10 percent, any network worsens,
any numerical fallback occurs, either unit check fails, or an output is
nonfinite.  Label it a same-cache mechanistic survivor only if every network
improves by at least 20 percent and the bootstrap upper ratio is below 0.90.
This gate cannot promote a submission.

## Legality and next action

M197 uses only permitted weights, setup rotations, and evaluated directions;
it charges all 126 frames and claims no free pilot.  If it survives, a new
production attribution/cost/whole-network protocol is required before any
competition use.  If it fails, preserve the crossed U-statistic derivation
and kill this R=3 fixed-budget implementation; do not retune R, frame subsets,
lambda, or triplets on this cache.
