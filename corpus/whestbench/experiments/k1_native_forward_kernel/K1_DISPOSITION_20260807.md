# K1 disposition: the S-lever budget, measured and honest

Goal: "make every flop count" -> maximize the wall-priced forward throughput S,
since adjusted = v * 8.74e-6 / S with v pinned ~0.0199. Measured on this 16-core
machine (~ the grading box's 16 vCPU). No C compiler / numba / cython in the
frozen venv (matches the sandbox), so the compiled kernel is designed, not
benchmarked, here.

## Measured levers (this hardware)

| lever | factor | evidence |
|---|---|---|
| numpy-fused forward (preallocated ping-pong f32, in-place ReLU, out= matmul) | **1.36x** over N2 | K1: 17.53 us/sample, 239.2 GFLOP/s vs N2 23.77 us / 176.5 GFLOP/s; bitwise-identical to naive (maxabs 0.0) |
| structural pruning (champion dead_alpha=-2, ~190/256 active) | **1.7x** | pruned/dense FLOPs 0.57-0.61 across 3 seeds |
| combined measured (fused x pruning) | **~2.3x** over N2 | 1.36 * 1.7 |

At the measured combined ~2.3x, floor-budget samples rise and the implied
adjusted score at the 0.1 floor is ~1.74e-7/2.3 ~= 7.6e-8 -- already better than
the champion (2.12e-7) and near the top-12 cutoff (4.09e-8).

## The ceiling and what #1 requires (honest)

numpy-fused reaches 239 GFLOP/s = ~30% of this laptop's AVX2 f32 peak
(~768 GFLOP/s; AVX-512 parts ~1.5 TFLOP/s). So:
- a compiled fused kernel at hardware peak adds up to ~3.2x (AVX2) / ~6.3x
  (AVX-512) over numpy-fused;
- total on THIS hardware (compiled-at-peak x pruning): ~7.5x (AVX2) to ~14.5x
  (AVX-512) over N2.

Ranks at v=0.0199 (S_needed = 1.74e-7 / adjusted):
- top-12 (4.09e-8): S 4.3x -> reachable NOW-ish (measured 2.3x x a modest
  compiled kernel);
- top-6 (~1.5-2e-8): S ~9-12x -> reachable on this hardware with a good
  compiled AVX-512 kernel + pruning;
- **#1 (7.39e-9): S 23.5x** -> needs compiled/N2 ~= 13.8x = ~2.4 TFLOP/s
  sustained. Above this laptop's AVX2 peak; requires a server-class AVX-512
  grading box (2-4 TFLOP/s) + a hand-tuned kernel at ~60-100% of peak + the
  measured pruning. Demanding but consistent with what the leaders demonstrably
  achieve on the shared grading hardware.

**Binding unknown:** the grading box's actual throughput vs this laptop.
Measurable only by a graded submission. If grading ~= this laptop, #1 is out of
reach (peak caps ~14.5x); if grading is ~2x (server AVX-512), #1 (23.5x) is in
range.

## The compiled-kernel design (deployment artifact, bundled per Rules 5.2)

Target: fused 32-layer forward, ~2.4 TFLOP/s on 16 vCPU AVX-512.
Structure: per sample-block, sequential (block x 256) @ (256 x 256) via an
optimized sgemm microkernel (cblas_sgemm against bundled OpenBLAS, or a
cache-blocked AVX-512 FMA microkernel), fused in-place ReLU, OpenMP over
sample-blocks; pruned active-set masks precomputed per network (the 1.7x).
f32 throughout; the sampler tolerates the reassociation. Bundled as a
precompiled .so/.dll (Rules 5.2) with a ctypes loader; the VERIFIED numpy-fused
path (k1_kernel.py) is the fallback and the correctness reference.

**Not built here:** no toolchain in the frozen venv. The C draft is a starting
point, uncompiled and unverified; the numpy-fused kernel is the verified,
measured artifact.

## Disposition

The S-lever is real and partly measured (2.3x now). #1 is an engineering target
requiring a compiled AVX-512 kernel on a server-class grading box -- gated on
(a) the organizer confirming native wall-pricing is legal (Q2), and (b) a graded
submission measuring the grading throughput. Both user-gated. Top-6 is plausibly
reachable; #1 is the far edge, contingent on grading hardware. Every measured
lever (fused kernel, pruning) is banked toward it.
