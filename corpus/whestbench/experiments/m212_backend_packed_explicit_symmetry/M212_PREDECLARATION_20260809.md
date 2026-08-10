# M212 predeclaration -- backend-packed matmul, explicit symmetry scratch

Date: 2026-08-09. Frozen before implementation or resource execution. M212 is
generated-only and response-free; challenge weights, truth, scorer,
leaderboard, submissions, cached responses, and efficacy records are banned.

## Failure fold and one changed boundary

M210's four-call level fusion passed its wall gate but used an overlapping
transpose add that NumPy satisfied with an unledgered full-plane temporary.
M211 made every matmul operand pack explicit and fixed the transpose, but one
of five frozen processes exceeded the hostile wall gate by 15.648130M.

M212 folds the surviving parts by changing one ownership boundary. Supported
`fnp.matmul` receives the same non-contiguous views as M210: under FlopScope's
official analytical model its cost is determined by operand shapes regardless
of backend packing, and backend execution belongs to that supported call. The
user-created transpose temporary is replaced by `copyto` into M210's already
owned full-plane scratch before the add. No other algebra, precision, layout,
depth, source formula, or dispatch count changes.

## Frozen predictions and gates

- width 256, 31 layers, f64, recursion depth 3;
- exactly four matmul calls and exact matmul bill 1,167,925,248;
- exactly four reshape calls and exact reshape bill 16,252,928;
- exactly one additional full-plane f64 `copyto`, predicted incremental bill
  4,063,232 over M210 and predicted inclusive bill 1,249,253,376;
- no `add(A, swapaxes(A), out=A)` or unledgered user temporary;
- M210's existing named scratch owns the transpose until the add completes;
- exact integer Gram, f64 M205 source parity <=2e-10, mirrored Gram/aabb,
  canonical binding, epoch, f64, and compile-after-stage gates remain fixed;
- five fresh processes, seeds 212700001..212700005, must remain finite, below
  512 MiB RSS, bill-identical, and each satisfy

  `inclusive_bill + 5 * 1e11 * residual_wall_s <= 1,986,871,472`.

## Credit boundary and stop rule

A pass earns only a meter-lawful isolated resource component. It grants no
M179 factor lifecycle, physical K4/K31/K22/C211 provider, M198 stream,
terminal cost, residual proposal, variance, MSE, score, or winner credit.

Any parity, billing, binding, memory, or hostile-wall failure kills M212. Do
not later add user packs, change depth, or retune the five-times wall rule.
