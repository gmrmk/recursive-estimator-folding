# WC-1 — Winner catalog by ablation + proper ladder seeding

Date: 2026-08-08 (before code). User mandate: mine every part that WORKED,
do the same (measure it), and accelerate by SEEDING the ladders properly.

## The seeding principle

Every G0 so far started from zero and re-derived a truth. But the winners are
already composed in the champion v3. The correct seed for any future ladder
is: baseline = the full validated composition; each candidate = a measured
DELTA against it, on the cached-truth battery. Two payoffs:
1. **Winner audit (adversarial self-check).** Ablate each winner component
   (disable it) and measure the MSE it was buying. A component whose ablation
   costs ~0 is not load-bearing (candidate for removal to free budget); the
   component whose ablation costs the MOST is where the design's value
   concentrates and where a REPLACEMENT mutation has the highest ceiling.
2. **Marginal-value map for headroom.** The 34% budget headroom + the A4
   95.5%-worst-case constraint mean new billed work must be spent where it
   buys the most MSE. The ablation deltas ARE that map.

## Winner components to ablate (each an arm; subclass v3, disable one thing)

From the GEN3 packet's PROMOTED set, the ablatable ones:
- A_frames: replace the 126-frame phased-Hadamard design with matched-n
  radially-conditioned iid (isolates the design's spherical gain).
- A_radial: disable exact radial conditioning (sample true chi radius instead
  of the mean-radius sphere).
- A_prune: disable pilot-rescued pruning (dense forward, dead_alpha=-inf) —
  measures pruning's MSE cost/benefit AND its billed saving (the pruning that
  A1 tied to the tail).
- A_fold: disable 3-terminal-layer folding (sample all terminal layers).
- A_tangent: set moment_tangent_lambda = 0 (drop the first-layer control).
- A_antithetic: disable antipodal pairing (isolates the variance-halving).

Each arm reports: paired MSE ratio vs full v3 (>1 = the component helped) with
CI, billed-FLOP delta, and the WORST-NET ratio (does this component
disproportionately help/hurt the tail A1 found?).

## What the map seeds

- The largest-|delta| component with a KNOWN failed-replacement family (e.g.
  if A_tangent's value is large, the tangent-improvement family reopens with
  a higher ceiling than N9's +2.1% implied) becomes the next predeclared
  mutation, seeded at the SCREEN rung (skip premise — the ablation IS the
  premise evidence).
- Any near-zero-delta component that also bills is a removal candidate that
  frees headroom for M188/M189 (composes with PB-1).
- The tail-differential column (worst-net vs mean ratio per component) points
  the P1/M185 pruning work at the specific component driving the 11x hosted
  spread.

## Battery reuse / acceleration

Same cached truths (m181 3-net 3.5M; m185 80-net panel) and paired-seed
protocol as PB-1; independent output files (no race). Ablation arms are pure
subclass overrides — ~2 min/arm. One delegated agent, one results json, one
ledger batch-append.

## Gates (audit semantics, not promotion)

An ablation arm does not "promote"; it REPORTS. Flags: LOAD-BEARING if
disabling it worsens MSE >= 20% (its replacement family is a priority ladder);
REMOVABLE if disabling changes MSE < 3% AND it bills > 2% of B (free headroom);
TAIL-DRIVER if its worst-net delta exceeds its mean delta by >= 1.5x.

## Firewall
Cached artifacts + kerdock_phases.npz read-only; synthetic nets only; frozen
sources subclassed never edited; no submissions; ledger append.
