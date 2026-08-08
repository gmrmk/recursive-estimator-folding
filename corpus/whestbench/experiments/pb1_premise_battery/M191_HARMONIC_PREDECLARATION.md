# M191 predeclaration — spherical-harmonic exactness + trigonometric control

Date: 2026-08-08 (before code). Lightning-bolt provenance (user): "Jason
Padgett's trigonometric models" -> steelman: the ReLU net is a polytope
tessellation; its spherical mean decomposes in spherical harmonics; a
quadrature design's error spectrum starts at its first NON-EXACT degree.
Never tested in 199 ledger records (N4's controls were radial; the angular
harmonic structure of the design was never measured).

## Mechanism

1. The estimator integrates f(u) over the uniform sphere measure; E[Y] = 0
   for every harmonic of degree >= 1. Antipodal pairing already annihilates
   all ODD degrees exactly. Phased-Hadamard/MUB families are (weighted)
   spherical 2-designs, plausibly annihilating degree 2 exactly.
2. Therefore the design's angular error concentrates at the first non-exact
   even degree (predicted: 4). A degree-d harmonic CONTROL VARIATE — subtract
   the sampled projection onto an exactly-zero-mean harmonic basis — is
   unbiased by construction (trig identity, not Gaussian surrogacy: the M181
   bias trap does not apply) and removes exactly that error component.

## G0-a (DETERMINISTIC falsifier — no sampling, minutes)

Compute the Kerdock design's quadrature error on harmonic polynomials
directly: for the 64,512 antipodal directions {u_s} (one Haar rotation;
check 3 rotations), evaluate mean_s p(u_s) for random degree-2 and degree-4
harmonic polynomials p (exactly-zero-mean under uniform measure; construct
via traceless symmetric tensors contracted with u^{(k)} — pure linear
algebra). Report the design's RMS quadrature error per degree vs the iid-MC
RMS (1/sqrt(n) scale).
- If degree-2 error ~ 0 (2-design confirmed) and degree-4 error ~ iid-level:
  the design is blind above degree 2 -> the CV has room; PROCEED to G0-b.
- KILL if degree-4 error is ALSO ~0 (the design is a 4-design or better —
  then the residual variance is degree >= 6 structure and the CV family's
  ceiling is the degree-6 share, measure it before proceeding).

## G0-b (battery arm — cached truths, paired seeds)

Arm on the PB-1 battery: v3 estimate minus the sampled projection onto the
first non-exact degree's harmonic space, restricted to a tractable basis
(the final layer's dominant directions: project onto p(u) built from the
top-k right-singular directions of W_1 or the per-neuron effective input
maps — document the basis; the basis must be weight-derived, never
truth-derived). Gates: kill < 10% panel-MSE reduction; promote >= 15% with
CI excluding 10%. Billed delta reported; A4 cap respected.

## Honesty bound

If the final-layer functions' energy above the exact degree is spread across
many harmonics (high effective dimension), the sampled projection is itself
noisy and the CV gains little — that is exactly what G0-b measures. No claim
past measured sizes.

## Firewall
Deterministic G0-a local; G0-b on cached battery artifacts; frozen sources
untouched; no submissions.
