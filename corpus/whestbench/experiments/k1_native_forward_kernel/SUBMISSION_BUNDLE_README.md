# Submission bundle — what is ready, and the steps that need you

Prepared while you were away. Everything response-free and local is done; the
three steps below need you at the machine (credentials / files / an outward
action I must not take on your behalf).

## What is ready (autonomous, done)

- **Verified fused forward kernel** (`k1_kernel.py`): bitwise-identical to the
  naive forward, 1.36x faster (allocation removal), with the champion's 1.7x
  structural pruning and a floor-budget planner. Measured: 239 GFLOP/s,
  17.5 us/sample on 16 cores.
- **The certified-provider artifact** (M178 + M179): complete, frozen, pushed —
  the $20k Algorithmic Contribution paper material.
- **Honest S-lever budget** (`K1_DISPOSITION_20260807.md`): #1 needs S~23.5x =
  a compiled AVX-512 kernel at ~2.4 TFLOP/s on a server-class grading box +
  pruning; top-6 (~9-12x) is reachable on this hardware class. The binding
  unknown is grading throughput, measurable only by a graded submission.
- **Organizer packet** (`corpus/whestbench/handoff/ORGANIZER_CLARIFICATION_QUESTIONS_20260807.md`):
  drafted, send-ready.

## Step 1 (BLOCKING for #1) — send the organizer packet

Send the six questions to the organizers. Q2 (is native wall-time pricing legal,
and will it be regraded?) determines whether the whole native-kernel #1 strategy
is viable; Q1 (multiplier floor 0.1 vs 0.5) sets the ceiling. **Do not have me
build/deploy the compiled kernel before Q2 is answered** — if native pricing is
patched (Rules 5.3) the strategy dies.

## Step 2 — graded baseline submission (measures S on the real hardware)

I cannot do this: it needs (a) the champion tar
`submission_formal_local_champion_l1_20260806.tar.gz` (sha256 bc2ec395...,
NOT on disk here), (b) AIcrowd credentials, (c) network. When you can:
submit the existing validated champion as a graded baseline. It returns the
single most decision-relevant number (grading throughput / whether native
pricing is honored) and costs nothing strategically (it is the fallback
champion, unchanged).

## Step 3 (after Q2 = yes) — build the compiled kernel

With native pricing confirmed legal, the compiled fused-forward kernel
(design in `K1_DISPOSITION`) is built in a toolchain environment (cc -O3
-march=native -fopenmp + cblas_sgemm, or a cache-blocked AVX-512 microkernel),
bundled precompiled per Rules 5.2 with the `k1_kernel.py` numpy fallback as the
correctness reference and a full native-computation disclosure. I can write and
drive that build the moment you confirm Q2 and provide a toolchain env.

## The honest bottom line

The mathematics is settled and the certified paper is done. #1 is now an
engineering + permission problem: a fast compiled kernel (buildable), on a
grading box fast enough (measurable only by submitting), with native pricing
permitted (organizer Q2). Steps 1 and 2 are yours; I take step 3 on your word.
