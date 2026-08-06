# Resource postmortem

## Scope and verdict

PIDs **18004** and **38460** were both Python workers launched by this branch's
`run_premise.py`.  They were stopped externally at approximately **24.6 GB**
and **13.8 GB** working set, respectively.  Do not rerun this harness.

**Kill the measurement-harness implementation only.  Leave the frozen
adaptive `tau=0.5` sparse-radial mathematical candidate pending.**  The run did
not complete the predeclared eight cases, so it supplies no final accuracy
verdict and no n=128 authorization.

## What happened

Both runs checkpointed the same first three width-64 cases and failed before
seed 18563 returned.  The second run streamed truth in batches of 2,048,
pinned OpenBLAS to one thread, and measured only about 42.5 MB peak working set
for each completed reference.  Therefore neither a `B*n` truth slab nor Haar/
trace-rank node growth explains the multi-gigabyte peak.

Static inspection localizes the nonreturning allocation path to the in-process
call of `reduce_components`: on the last equal-mass bin it can reach
`remaining > eps`, `capacity == 0`, and hence `take == 0`.  It then appends a
zero-weight `GaussianComponent` without changing `remaining` or `bin_mass`;
the only bin-advance branch is disabled because no next bin exists.  The list
can therefore grow without bound.

The harness made this dangerous because candidate inference ran in the same
process.  Its monitor could notice memory growth but could only raise after the
candidate call returned; the loop never returned.  There was no child-process
RSS limiter capable of terminating and checkpointing the stage.  Thus the
observed 24.6/13.8 GB is an orchestration/resource-containment failure around a
nonreturning implementation path, not evidence about sparse-radial estimator
accuracy or mathematical viability.

## Evidence retained

- Frozen candidate SHA-256: `A31FD01802FF79167EFE00C1B3B129C2744853D9AD0A9897C990AF5988C4F24C`.
- Frozen contract SHA-256: `DF2EF00FFF7B77FC365FC80536524DFEC388363F6A77993AA81C9C47C97A400A`.
- Streaming references for the three completed cases reproduced the earlier
  case ratios to reported precision while remaining far below 2 GB.
- Conditional n=128 was not run.
- No WHest data, truth array, holdout, scorer, or API was accessed.

Any future evaluation must run each estimator case in a separately killable
process with an externally enforced RSS/time limit and must repair/re-audit the
last-bin reducer before treating it as the same implementation.  Those changes
would require a new frozen premise; they are not made here.
