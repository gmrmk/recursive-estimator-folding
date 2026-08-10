# M211 predeclaration -- explicit packed level fusion

Date: 2026-08-09. Frozen before implementation or resource execution. M211 is
generated-only and response-free. Challenge weights, truth, scorer,
leaderboard, submissions, cached responses, and efficacy records are banned.

## Parent failure and one changed mechanism

M210 preserved the exact four-call level-fused Gram identity, but a hostile
allocator audit found two ownership defects: the in-place transpose sum
silently allocated a full temporary, and every batched matmul consumed
non-contiguous views whose native packing was absent from the allocation
ledger. Under M210's frozen stop rule this kills the native-resource claim.

M211 changes one mechanism only: storage ownership. Every matmul operand is
copied into a named, preallocated contiguous buffer, and transpose
symmetrization uses a named full-plane scratch buffer. Algebra, f64 precision,
depth three, 31-layer batching, four matmul calls, and all M205 source formulas
remain fixed.

## Frozen predictions and gates

- width 256, 31 layers, f64, recursion depth 3;
- exactly four matmul calls and four charged reshapes;
- exact matmul bill 1,167,925,248 and reshape bill 16,252,928;
- every left/right packed operand and transpose scratch appears in the
  allocation ledger; all matmul operands are C-contiguous;
- no overlapping transpose add and no untracked full-plane temporary;
- inclusive bill below 1.35B FLOPs, persistent arrays below 300 MiB, process
  RSS below 512 MiB, and no cubic Source211 coefficient table;
- five fresh generated processes, seeds 211700001..211700005, must each satisfy

  `inclusive_bill + 5 * 1e11 * residual_wall_s <= 1,986,871,472`.

Exact integer Gram parity, f64 M205 source parity <=2e-10, exact mirrored
symmetry, canonical layer order, unique objects, producer epoch, f64-only
inputs, and compile-after-stage remain fail-closed.

## Credit boundary

A pass earns only an explicit-memory resource-component result. It cannot
claim that M179 can retain all 31 factors, that M198 consumes the outputs in a
legal stream, or that physical K4/K31/K22/C211, residual proposals, terminal
response, source variance, MSE, score, or a winner exist.

## Stop rule

Any parity, ownership, contiguity, billing, memory, or five-process hostile
wall failure kills M211 without changing depth, layout, precision, or buffer
count. Preserve the explicit-packing identity separately.
