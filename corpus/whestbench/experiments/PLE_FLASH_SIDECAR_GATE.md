# Predeclared gate: clean-room PLE flash sidecar

Date: 2026-08-06
Status before implementation: frozen premise gate

## Invariants

- Objective: test whether a Gemma-4-inspired per-layer embedding (PLE) *storage pattern* can reduce repeated analytic-response latency without changing the WHestBench estimator.
- Score boundary: this is a premise-only microbenchmark. It does not read WHestBench rows, weights, targets, scorer output, APIs, submission artifacts, or holdouts.
- Clean room: use only the public architectural principle that a decoder layer may receive a small layer-specific lookup embedding. Do not download, inspect, infer from, or call Gemma weights or outputs.
- Bias class: the direct formulas are analytic. Table lookup is a deterministic, linearly interpolated approximation with its interpolation error measured against the direct formula.
- Legal keys: layer index and quantized `alpha = mu / sigma`. Gate probability is derived from alpha. The separate exact row-block schedule may additionally use active width. No key or value may depend on truth, official outcomes, scorer behavior, or fitted labels.
- Legal values: dimensionless rectified-Gaussian mean and Hermite/Price coefficients, plus an exact cyclic row-block kernel schedule. All values are generated from closed-form equations with zero fitted parameters.
- Resource ceiling for this screen: immutable table files under 16 MiB total; setup-preloaded representation under 32 MiB; no network or accelerator requirement.
- Reproducibility: deterministic grid, schedules, queries, and seeds specified in source and manifest.
- Flash invariant: a file-backed memory map represents cold immutable storage. Arithmetic still runs on CPU and touched pages reside in RAM/page cache. The experiment must not claim that flash performs calculations or that a microbenchmark forcibly evicted the operating-system page cache.

## Proposed mechanism

For standardized preactivation `Z ~ N(alpha, 1)`, tabulate

```text
p(alpha)       = Phi(alpha)
m(alpha)       = alpha Phi(alpha) + phi(alpha)
a1(alpha)      = Phi(alpha)
a2(alpha)      = phi(alpha) / 2
a3(alpha)      = -alpha phi(alpha) / 6
a4(alpha)      = (alpha^2 - 1) phi(alpha) / 24
```

The `a_q` are the normalized Hermite coefficients of centered ReLU, with
`a_q = phi(alpha) He_(q-2)(-alpha) / q!` for `q >= 2`. A layer-indexed table
stores these immutable values. The layer coordinate selects a slice; it does
not alter the mathematics. An independent cyclic row-block schedule gives
each layer a deterministic offset while visiting every active row exactly
once.

Three frozen modes:

1. `direct`: evaluate the formulas with CPU transcendental functions.
2. `mmap`: open a read-only `.npy` table and interpolate from file-backed pages.
3. `preload`: copy selected layer slices once during setup, then interpolate from RAM.

## Predicted signature

- Interpolated coefficients agree with direct analytic values to <= `2e-6` maximum absolute error on the frozen query set.
- Probability/mean/Hermite identities and layer symmetry agree to <= `2e-6`.
- Every schedule is a permutation of the same exact row partition; cyclic gauge unrotation restores layer-0 order exactly.
- Warm lookup latency is lower than direct analytic evaluation for the frozen repeated-query workload in at least one lookup mode.
- Preload trades setup copy time and RAM for lower or equal repeated-query latency; mmap trades RAM commitment for possible page-fault latency.
- Conservative FlopScope-style accounting is reported; no performance claim may rely only on unbilled storage I/O.

## Frozen benchmark

- Depth 32, alpha grid `[-8, 8]` with 8193 equally spaced nodes.
- Six coefficient channels above, float32 packaged values, float64 direct reference.
- Active width 256, row block 32, eight blocks, cyclic offset `layer mod 8`.
- Query seed 20260806; 4096 query keys per repeat; layer keys uniform in `[0,31]`; alpha keys uniform in `[-7.75,7.75]`.
- 9 timing repeats after 3 warmups. Report median and p95. Also report mmap open time, first-touch time, preload setup time, file sizes, and array resident bytes.
- Benchmark modes must return their output so evaluation cannot be optimized away.

## Gates and dispositions

Passing lookup/cache component:

- correctness and symmetry gates pass;
- artifact size and RAM gates pass;
- at least one lookup mode has median repeated-query latency <= 0.90 times direct;
- conservative billed operations per query are lower than direct's declared analytic-operation proxy.

If interpolation fails, kill only the frozen grid/interpolation configuration and preserve the clean-room PLE storage principle and exact analytic generator. If mmap latency fails but preload passes, kill only flash-on-hot-path lookup and preserve flash as cold immutable packaging plus setup preload. If both lookup modes fail latency, preserve the schedule/manifest/correctness harness and record the failed mechanism as Python/NumPy gather overhead at this query scale. No result from this microbenchmark is promoted into the deployed estimator without a separate whole-estimator budget and matched-validation gate.
