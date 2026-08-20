# M235 preimplementation erratum 4 -- official start boundary and mirror replay

Date: 2026-08-09. Sealed before every M235 test, implementation, native trace,
and G0 execution. This final lifecycle repair adds no estimator operation,
seed, or threshold tuning.

## Official SubprocessRunner start-response boundary

Every native receipt must exercise the pinned official
`whestbench.runner.SubprocessRunner.start()` path, not merely time a direct
`estimator.setup(ctx)` call. The measured interval starts immediately before
the host calls `SubprocessRunner.start(entrypoint, context, limits)` and ends
only when its successful `start` response has been read and the method
returns. It therefore includes:

- worker-process spawn and protocol startup;
- participant module and estimator-class load in the worker;
- SetupContext construction;
- the complete M235 setup receipt and workspace allocation;
- response serialization, transport, and host read.

The pinned worker uses `limits.setup_timeout_s=5.0` for the start-response
read. Every measured end-to-end start must be `<4.0 s`, retaining at least one
second below that official hard limit. A direct setup timer and the isolated
`<0.05 s` receipt timer from erratum 2 are retained as component diagnostics
and gates; neither substitutes for the end-to-end start-response gate.

Any worker import fallback, setup retry, prestarted persistent worker, warm
module cache credited from a prior candidate, or excluded process-spawn time
invalidates the receipt. The official lifecycle hashes in erratum 2 remain
binding.

## Paired primary and mirror processes

For every one of the five frozen `(setup_seed,A_seed,B_seed)` triples, launch
two independent fresh official-style processes with the same setup seed:

```text
primary: setup -> predict(A) -> predict(B) -> predict(A)
mirror:  setup -> predict(B) -> predict(A) -> predict(B).
```

There are exactly ten fresh processes. No process or setup-owned workspace is
shared between a primary/mirror pair. No prediction is a discarded warmup.
All 30 predictions independently pass exact M212/M235 call and bill receipts,
finite/symmetry, M235 component wall, both combined wall gates, and RSS.

Within each process, the repeated endpoint outputs must be bitwise identical:

```text
primary A1 == primary A2
mirror  B1 == mirror  B2.
```

Across the paired same-seed fresh processes, both source states must also be
bitwise identical in every `aaaa`, `aaab`, and `aabb` slot:

```text
primary A1 == primary A2 == mirror A
mirror  B1 == mirror  B2 == primary B.
```

Hostile audit outside the timed numerical kernels compares shapes, dtypes,
raw bytes, and SHA-256 digests. Any difference kills M235; numerical tolerance
is not allowed. The immutable setup receipts in the paired processes must
also have identical raw bytes/digests for their common setup seed, while their
object identities and data pointers are required to remain stable only within
each process.

This mirror proves both overwrite directions: B is not contaminated by a
preceding A, and A is not contaminated by a preceding B. The within-process
workspace/receipt identity and pointer invariants from erratum 3 remain in
force at setup return and after every prediction.

## Freeze rule

The ten-process pairing, exact order, end-to-end official start boundary,
strict `<4.0 s` margin, all-prediction resource gates, and bitwise cross-
instance comparisons are immutable M235 requirements. Reducing the process
count, discarding a cold call, comparing only A, using tolerance, or timing
setup below the official host/worker boundary creates a different child.
