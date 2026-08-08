# M180 predeclaration — spherical design strength (the angular-variance axis)

Date: 2026-08-08 (before code). First mutation of the reopened program.
Champion: Kerdock v3, hosted-graded 1.832e-7 (#326094, rank #58). Target: the
honest 4x variance-per-FLOP gap to the 4.6e-8 tier.

## Why this family, and why it is not a killed leaf

By positive homogeneity the radial integral is exact; ALL estimator variance
is angular. The corpus never mutated the angular design itself: the 126-frame
Kerdock set was inherited from M71 and every prior mutation (N8a lattice swap,
N9 tangent/fold) operated AROUND it. N8a in fact measured the design's
strength (2.0-3.2x over conditioned MC) without asking whether a STRONGER
design exists. mub2_orthogonal_fold3 exists in the work tree with unresolved
disposition. Premise change that reopens the family: the hosted grader now
provides 6-minute rich-feedback validation, and the corrected calibration
says structured estimators grade near local values (SUBMISSION_RESULT).

## Mechanisms under test (ONE mutation: the design; variants are arms, all
predeclared here, no post-hoc additions)

- Arm A (baseline): the frozen Kerdock 126-frame design at native n.
- Arm B (MUB augmentation): mutually unbiased bases — complement the
  phased-Hadamard frames with additional MUB constructions to raise the
  design's effective strength at the same total n (reuse
  mub2_orthogonal_fold3 machinery where sound; read its disposition first).
- Arm C (coset-stratified rotations): split n across k Haar rotations
  stratified over cosets of the frame's symmetry group instead of one global
  rotation (k in {2,4,8} at matched total n).
- Arm D (randomized orthogonal re-mix): frames re-mixed by independent
  block-orthogonal transforms per frame (destroys inter-frame correlation
  structure that may dominate residual variance).

## G0 (cheapest falsifier, variance-only, no estimator build)

On 3 synthetic He nets at matched total n = 64,512 directions with matched
antipodal + radial conditioning and matched downstream (plain antipodal
forward mean, the N8a-sanctioned deviation): paired variance of each arm vs
Arm A across >= 12 rotation seeds.
- KILL an arm if variance reduction vs A < 10%.
- PROMOTE-to-build only the best arm and only if reduction >= 15% with a
  bootstrap CI excluding 10%.

## Build + validation ladder (only if an arm survives G0)

- G1: minimal-diff integration into the frozen v3 scaffold (design-only).
- G2: local paired factorial vs v3 (6 nets x 4 reps, ratio <= 0.87 with CI
  excluding 1.0; billed FLOPs within +2%; wall within 60s cap margins).
- G3: package + validate + member listing.
- G4 (NEW - the hosted instrument): ONE graded submission; PASS iff hosted
  adjusted < 1.75e-7 (a real improvement over #326094 outside grading noise).
  Requires user-permitted submit (classifier-gated).

## Honesty bound

Design-strength gains of 1.2-2x are plausible; 4x from this mutation alone is
not expected. The path to the 4.6e-8 tier is compounding gate-passers, and
each is reported at its measured size only. No claim about the wall tier.

## Firewall

Synthetic nets only until G4; frozen candidates untouched; no sealed cells;
no accounting bypass; one causal mutation; kills are final for the arm.
