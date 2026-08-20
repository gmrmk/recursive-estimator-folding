# M195 predeclaration -- symmetric two-rotation half-design attenuation

Date: 2026-08-08.  Frozen after the M194 pilot-size autopsy and before M195
code or output inspection.  Because it reuses the same three-network P2 cache,
this gate is mechanistic only; it cannot promote or validate a candidate.

## Mutation and unchanged budget

M194 proved that an independent pilot makes the M192 covariance blocks
identifiable in expectation, but the pilot precision needed for a reliable
cross block costs more than its score benefit.  M195 removes that cost link:
two independent 63-frame half-designs each serve as both estimator and pilot
for the other.  Total evaluated frames remain 126.

For each network, pair rotation r with rotation r+8 for r=0,...,7.  Let A and B
be the first 63 complete-frame estimates from the respective rotations.  A
complete antipodal orthonormal frame retains exact radial conditioning and
degree-2 exactness.  The two halves lose the full Kerdock union's shared
degree-4 structure; this loss is charged empirically against the archived
126-frame main-rotation baseline at identical point count.

## Frozen operator

Split outputs by `j mod 8`.  On the training outputs of each fold define

    a = mean_frame(A),             z_A = A - 1 a^T,
    b = mean_frame(B),             z_B = B - 1 b^T,
    d = a - b,
    S_A = z_A z_A^T / n,           h_A = z_A d / (2n),
    S_B = z_B z_B^T / n,           h_B = -z_B d / (2n).

If the two Haar rotations are independent, `E[z_A error_B]=0` and

    h_A = Cov(z_A, (error_A + error_B)/2),
    h_B = Cov(z_B, (error_A + error_B)/2).

For K=63, `P_K=I-11^T/K`, `tau_g=tr(S_g)/(K-1)`, and frozen
`lambda=1/3`, solve within each contrast subspace

    v_g = -(S_g + lambda tau_g P_K)^+ h_g,
    1^T v_g = 0.

The held-output prediction is

    pred = (a+b)/2 + v_A^T A + v_B^T B.

Thus each group has total weight 1/2 and the complete rule sums to one.
Cross-fitting prevents a held output from influencing its weights.  Nonfinite
or singular fits fall back to the equal two-half mean and are counted as hard
gate failures.  No coefficient, split size, rotation pairing, or sign may be
retuned after inspection.

## Comparators and gates

Primary comparator: the full 126-frame uniform mean of rotation r, which has
the same number of evaluated frames as M195.  Diagnostic comparator: the
uncorrected equal mean of the two 63-frame halves, localizing any loss of the
Kerdock degree-4 structure.

Primary statistic: geometric mean across three networks of the ratio of mean
paired MSEs.  There is no sample-cost multiplier because both arms use exactly
126 complete frames.  Kill below 10-percent panel reduction, if any network
worsens, on any fallback, or on a nonfinite output.  Mechanistic survivor
requires at least 20-percent reduction on every network and a pair-cluster
bootstrap upper 95-percent ratio below 0.90.  Otherwise label unresolved.

## Firewall, bias, and next gate

G0 reads only cached synthetic P2 frame matrices and M181 truths.  Truth is
read only for final scoring.  No forward, private evaluator, submission, or
frozen source is touched.  M195 is an output-cross-fitted, data-dependent rule
with cross-fit bias.  A survivor must be re-predeclared on fresh whole networks
with output-permutation-equivariant folds, actual v3 pruning/frame attribution,
exact billing and wall time, untouched holdout, symmetry checks, and hostile
resource guards before it can compete with v3.1 GUARDS.
