# T4 report — Kerdock M71 v3's first score: a descriptive same-basis local best

Date: 2026-08-08. Predeclared: T4_PREDECLARATION.md (committed 448b717 BEFORE
the run). One run, executed exactly once, direct shell invocation (the burned
gate's Start-Process env-map failure mechanism structurally absent). Frozen
estimator sha256 076D0A5D…9AACF verified before launch; sources untouched.

## The run (public 0..99, seed 0, subprocess, whestbench 0.14.0, B=272e9)

| metric | value |
|---|---:|
| adjusted final-layer score | **1.6190837992231567e-7** |
| raw final-layer MSE | 2.493887556909158e-7 |
| mean score multiplier | 0.6561138779836238 |
| mean effective compute | 178.462975e9 |
| max per-network effective compute | 209.575026e9 (23% under B) |
| failures | **0/100** (all categories zero) |
| best / worst per-network adjusted | 4.357e-8 / 6.245e-7 |

Artifact: kerdock_v3_official100.json (+ stderr log, empty of errors).

## Paired against the sampler line (same 100 networks, descriptive)

| comparison | mean ratio | paired wins | bootstrap 95% CI (200k, seed 20260808) | P(better) |
|---|---:|---:|---|---:|
| Kerdock vs L2 (2.1020e-7) | 0.770267409 | 65/100 | [0.650767, 0.908152] | 0.999160 |
| Kerdock vs L1 (2.1218e-7) | 0.763084382 | 65/100 | [0.645064, 0.898964] | 0.999480 |

A 23-24% mean improvement carried by large per-network gains (only 65/100
wins but a heavy win-side tail; per-network spread is wider than the sampler
line's).

## Status of this number (predeclared, unchanged)

DESCRIPTIVE ONLY — public 0..99 is burned; this confers no validation and no
winner representation. What it changes is the PORTFOLIO ORDER for graded
evaluation at user-return: the already-packaged, validator-passed v3 tar
(`b55a1d8d…30af`, 33,344,900 bytes) moves to the front of the graded queue
alongside the L1 canary. Its one known hosted risk is memory: the hosted
audit records only a **1.445 MiB** memory-gate margin — the tightest of any
candidate — so its graded run is also its OOM test.

## Consequences for the dossier (T5)

1. Local same-basis descriptive ranking is now: **Kerdock v3 1.619e-7 <
   L2 2.102e-7 < L1 2.122e-7** (fold3cap: score-unknown by design;
   fold3-39936's 1.41e-7 remains a 5-net near-cliff number, not comparable).
2. The graded queue gains a fourth must-grade artifact; the designation
   decision rule (grader-evidence-first, private-rerun caveat) now most
   plausibly lands on Kerdock v3 IF it survives hosted memory.
3. The "zero-evidence lottery ticket" framing is retired: one predeclared
   descriptive run replaced it with the strongest same-basis number on the
   machine, at the largest compute safety margin.
