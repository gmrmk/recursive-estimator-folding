# M184 predeclaration — trichotomy upward (exact on-composition + sparsity)

Date: 2026-08-08 (before code). The last mined mechanism standing (M182 list
items 2+3, one family). Distinct from the killed M181: on-neuron
linearization is EXACT (ReLU = identity where the pre-activation is provably
positive for every sample), so the M181 bias verdict does not apply.

## Mechanism

Our fold3 applies the dead/on/kink trichotomy only at the 3 terminal layers.
M184 extends it upward: at middle layers, neurons whose pre-activation is
positive for ALL n samples (certain-on, confirmable by pilot + exact max
check) pass ReLU as identity; runs of on-neurons compose linearly (one
precomputed W-product per network replaces per-sample materialization), and
firing-sorted sparse matmuls skip dead columns — converting the measured rank
collapse (participation ratio 128 -> 5.2) into billed-FLOP reduction at
IDENTICAL output (exactness preserved bit-for-bit where composition applies).
Score effect: adjusted = MSE x C/B with MSE unchanged and C reduced, or
refill C with more samples for lower MSE — either way adjusted improves by
the billed-reduction factor.

## G0 (static falsifier first — minutes, no build)

On 3 synthetic He nets, from the diagonal pass + one 512-path pilot at the
Kerdock design: count per layer (2..28) the certain-on and certain-dead
fractions under the sampling distribution, and compute the billed-FLOP
reduction achievable by (a) dead-column skipping (v3 already does some — count
only the INCREMENT), (b) on-run linear composition, (c) 4/element-billed
gather overhead per v0.10 pricing (charge it against the saving honestly).
- KILL if the projected net billed reduction < 15%.
- PROMOTE to build only if >= 20% (margin over gather costs and estimator
  overhead).

## Ladder if promoted

G1 minimal-diff build (exactness gate: outputs bitwise-identical on
non-composed paths, exact-equal on composed ones); G2 paired factorial vs v3
(billed C ratio <= 0.85 at identical MSE, CI on the billed ratio); G3
package+validate+members; G4 one graded submission < 1.75e-7 (Phase-1 window
permitting — closes Aug 10 23:59 UTC; else it becomes the Phase-2 opener).

## Honesty bound

Mid-layer certain-on fractions at width 256 may be small (alpha must be large
for ALL 64k samples); the static count decides in minutes. Expected 1.15-1.5x
if the band's structure claims transfer; the 4.6e-8 tier likely needs more
than this one lever. No wall-tier claims.

## Firewall

Synthetic nets until G4; frozen candidates untouched; no overspend-bug
reliance; kills final.
