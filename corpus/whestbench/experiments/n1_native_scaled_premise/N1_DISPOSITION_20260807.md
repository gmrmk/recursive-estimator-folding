# N1 disposition: predeclared gate FIRED; mechanism not refuted; constraint relocated

Honest verdict on N1 as predeclared. No result is spun into a pass.

## Result vs predeclared gates

| N (samples) | MSE (mean of 3) | v = MSE*N | wall (s, local) |
|---|---|---|---|
| 64,512 | 5.334e-7 | 0.0344 | 1.66 |
| 129,024 | 3.696e-7 | 0.0477 | 3.27 |
| 258,048 | 3.051e-7 | 0.0787 | 6.35 |
| 516,096 | 1.253e-7 | 0.0647 | 12.71 |

- `v_ratio_max/min = 2.29` -> **KILL GATE 1 FIRED** (predeclared pass was
  `v_ratio < 1.5`). N1 as written does NOT pass.
- deterministic under fixed seed: **yes** (gate 3 clean).
- local wall at 516k = 12.71 s < 20 s (gate 2 clean locally).

## Diagnosis (why the gate fired, and what it does NOT mean)

The tested estimator is a PLAIN antipodal Monte-Carlo forward
(`z @ W -> ReLU`, antipodal pairing, no controls). Plain MC of the true
network is **unbiased by construction**: `E[sample mean] = true mean`, so
`bias^2 = 0` and the true `v = MSE*N` is mathematically CONSTANT in N. The
observed non-monotone `v` (0.0344, 0.0477, 0.0787, 0.0647) therefore cannot be
a bias floor — it is **3-replicate estimation noise** in the MSE estimate
itself. The gate `v_ratio < 1.5` was too tight for a 3-rep estimate whose
per-rep MSE varies at the ±30-50% level. N1 is UNDERPOWERED, not a refutation
of 1/N scaling.

Corroborating: MSE fell 4.26x (5.334e-7 -> 1.253e-7) for an 8x sample
increase. Sub-1/N in this noisy sample, but plainly large and monotone
downward — consistent with flat-`v` 1/N plus estimation noise, NOT a plateau.

## The constraint N1 actually surfaced: native throughput, not scaling

The binding number is WALL TIME. 516k samples cost 12.71 s on this laptop's
numpy BLAS (~24.6 us/sample through the 32-layer 256-wide forward). The
score budget is `C <= B` -> at most ~2.72 s of pure residual wall (Rules 5.2,
matmul run on the raw/native channel, billed_FLOPs ~ 0). Reaching joe_wanza's
5.21e-8 with plain MC (`v ~= 0.0344`) needs `N ~= 660k` -> ~16.5 s local, i.e.
~6x OVER budget on this machine. So the wipe-the-floor mechanism is
mathematically sound (unbiased MC reaches any MSE) but **gated on native
throughput being ~6x this laptop's numpy on the grading hardware** — the exact
unknown the deepened judgment (de9ea4e) named as answerable only by a graded
submission.

## Correct next step (per fold discipline: no in-test retune; a new test)

N2 (separate artifact) resolves the two real questions:
1. THROUGHPUT: measure samples/sec and effective GFLOP/s of an
   all-cores float32 forward at d=256/L=32, and the speedup factor the grading
   hardware must clear to fit 660k samples in 2.72 s.
2. SCALING (properly powered): 20-rep `v` at fixed N against a saved MC truth,
   to confirm `v` is flat (kills the N1 noise) for the unbiased family, and to
   pin `v` for the champion's radial-controlled (unbiased) variant (`v ~ 0.02`
   vs plain 0.034 -> ~1.7x fewer samples for the same MSE).

N1 preserved tissue: the mechanism is unbiased-sound; the champion frame is the
variance floor; the deploy is native and legal (Rules 5.2, with disclosure) but
throughput-gated. What died is only the N1 gate as written (too few reps).
