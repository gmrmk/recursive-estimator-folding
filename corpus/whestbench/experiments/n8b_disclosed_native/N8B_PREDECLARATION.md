# N8b predeclaration — disclosed native sampling backend (Rules 5.2)

Date: 2026-08-08 (before measurement). Second mutation of the honest stack.

## Mechanism and legality boundary

Route the sampler's forward passes through the verified K1 fused kernel
(numpy/BLAS f32, corpus k1_native_forward_kernel, bitwise-vs-naive verified)
as an off-flopscope backend priced by residual wall time at lambda = 1e11
FLOP-equiv/s, per Rules 5.2, with a FULL DISCLOSURE document shipped in the
package (what runs native, why, and the exact charging path). Categorically
distinct from the leaderboard arbitrage: every second of our native wall is
honestly charged through the residual meter; nothing is engineered to evade
it. Economics: metered f32 matmul bills ~2mkn analytical FLOPs; native
charges wall x 1e11, so the discount = sustained one-core FLOP/s / 1e11.

## Cheapest falsifier (G0, this session, before any build)

Measure the K1 fused kernel's sustained throughput PINNED TO ONE CORE
(OMP/MKL/OPENBLAS threads = 1, matching the grader's 1-physical-core pin) on
the standard workload (He nets, batched forward, f32). KILL if sustained
throughput < 1.2e11 FLOP/s — the discount would be <= 1.2x and not worth the
packaging complexity and hosted-hardware risk. Label: local hardware only;
the grader's clock is unknown (the k*-style risk applies and is disclosed).

## Build gates (only if G0 survives; build delegated)

- G1: integration into the Kerdock v3 scaffold with the draw stage and
  downstream UNCHANGED (backend-only mutation); bitwise-identical outputs to
  the metered path on matched inputs (K1's existing verification standard).
- G2: metered-vs-native paired cost on synthetic nets: effective C (billed +
  1e11 x wall) reduced by >= 1.3x with raw MSE bitwise-unchanged; memory
  within v3's envelope.
- G3: the disclosure document (backend inventory, charging path, measured
  throughputs, the honest-accounting distinction) + folder-mode package +
  validate-package + contract validate + member listing.

## Bias class / firewall

Backend-only mutation: zero statistical change (bitwise gate). Synthetic
nets only; no sealed cells; no submission; graded evidence at user-return.
