# Predeclared mutation: factor the exact layer gauge

Date: 2026-08-06
Parent: clean-room PLE flash sidecar v1

## Diagnosed redundancy

The v1 coefficient atlas deliberately stores a layer axis, but its legal
closed-form response coefficients depend on `alpha`, not on layer identity.
The measured layer-symmetry defect is exactly zero. Therefore

```text
T[layer, alpha_index, primitive] = S[alpha_index, primitive]
```

is an exact tensor factorization, not an approximation. Layer identity is
still meaningful for the exact cyclic row-block schedule and is stored in a
small descriptor table.

## Changed mechanism

- Store one shared immutable `[8193, 2]` analytic atlas.
- Store 32 exact layer descriptors containing cyclic block shift, active
  width, and row-block width.
- Use layer descriptors for row routing; use the shared atlas for response
  lookup. No fitting and no estimator outcomes.

## Frozen gates

- Expanded responses agree with v1 mmap and direct analytic values to `2e-6`.
- Schedule/gauge error remains zero.
- Coefficient file size is at most `1/30` of v1.
- Setup-preload resident bytes are at most `1/30` of v1.
- Factorized best warm median lookup is <= `0.95` of v1 best warm median in
  the same process and frozen query sequence.
- Mmap first-touch is reported but not called physical-flash latency because
  operating-system page cache eviction is not controlled.

If the warm-latency gate fails, kill only the claim that factorization speeds
this Python/NumPy hot path; preserve its exact 32x storage/setup compression.
Promotion to WHestBench still requires a separate estimator-level gate.
