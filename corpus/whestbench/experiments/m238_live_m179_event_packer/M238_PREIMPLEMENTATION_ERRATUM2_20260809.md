# M238 preimplementation erratum 2 -- co-indexing and hostile binding

Date: 2026-08-09. Status: `SEALED_BEFORE_CODE_AND_TESTS`.

This erratum makes the live-state and binder semantics executable. It changes
no formula, source tape, threshold, cost ceiling, native seed, or gate order.

## Same-layer indexing

Tape row `ell-1` is frozen to the tuple

```text
(a_ell, C_ell, p_ell, r_ell, mu_ell, V_ell),
```

where `a_ell,C_ell,p_ell,r_ell` are the pre-ReLU/Jacobian quantities for weight
layer `ell`, and `mu_ell,V_ell` are the post-ReLU moments produced from that
same `a_ell,C_ell`. M238 does not inherit any older archive prose that calls
an entry's Jacobian `J_(ell+1)`. A shifted, previous-layer, next-layer, or
terminal Jacobian is a hard substitution failure.

Current `BackgroundEntry` is explicitly insufficient because it does not own
`a_ell,C_ell`; M238 receives no archive-reuse credit. The eventual producer
must issue one `LiveLayerContext` only after all six owners are co-live and
before its `a,C` workspace advances.

## Exact binder contract

The tape binder requires the exact six-name set and no extras. Every owner is
C-contiguous float64, finite, read-only for the bound lifetime, shape-exact,
and identified by object identity, data pointer, nbytes, strides, layer,
epoch, width, and producer generation. `C` and `V` are bitwise symmetric.

The receipt binder requires the exact five-name set `layer,i,j,k,g`; the four
index owners are C-contiguous signed int64 and `g` is C-contiguous float64.
All are finite/in-range where applicable and read-only. Every output/scratch
owner and every M226 column view has an analogous setup receipt. The binder
checks the exact 20 M226 names, float64 dtype, common event count, nonoverlap of
unrelated outputs, and one persistent owner lifetime through the unchanged
single M226 invocation.

Owner pointer/shape/stride/writeability receipts are re-enumerated immediately
before packing, after packing, and after M226 returns. Checking only a frozen
tuple is insufficient. A copied equal-valued owner, rebinding, post-issue
mutation, stale generation, duplicate consume, missing/overlapping 128-row
slice, or second consume fails. The completion bitmap must be exactly all 31
layers before M226 may bind.

`g` may remain a read-only receipt alias. The other 19 columns occupy
setup-owned persistent storage of at least `19*3968*8 = 603,136` logical bytes;
the full packer-owned slab/scratch/indices remain under the frozen 4 MiB gate.
Calling M226 once per layer is forbidden because it changes the validated
one-call topology.

## Added interior refusals

For selected `q in {i,j,k}`, require:

```text
Cqq > 0
Vqq > 0
1e-12 < p[q] <= 1
r[q] >= 0
```

and require positive finite conditional variances and Schur determinant.
Nonfinite eta/tree intermediates refuse. No floor, clip, sort, relabel, or
zero replacement is permitted. These checks occur before M226 binding and are
included in the frozen packer bill/call/wall gates.

The reduced tree is required to match M213 numerically under its separately
frozen tolerance; real-arithmetic identity does not authorize bitwise equality
after changing the floating-point DAG.

