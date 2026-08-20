# M234 predeclaration -- prebound explicit-Philox execution fold

Date: 2026-08-09. This document and its frozen manifest exist before any M234
implementation, M234 test, M234 native trace, or M234 source-efficiency
readout. M234 is generated-only and response-free. Challenge weights,
responses, truth, scorer, leaderboard data, submissions, cached outcomes, and
champion artifacts are forbidden.

## Objective, accounting boundary, and parent failure

The narrow objective is to determine whether M231's already-passed unbiased
`k=32` row estimator fits its frozen production resource envelope after one
composite execution/provenance repair. For every process the binding component
gate remains

```text
C_effective = C_M212 + C_M234
              + 5 * 1e11 * (r_M212 + r_M234)
            <= 3,727,757,440.
```

FlopScope `0.10.0+np2.4.6`, NumPy `2.4.6`, and the pinned Python 3.14 Windows
runtime under `work/whest-v014` define the accounting boundary. All positive-
bill array work stays inside the timed BudgetContexts. Audit-only hashes,
allocation ledgers, source inspections, shape/dtype/identity validation,
finite checks, symmetry checks, and receipt-law checks run outside those
contexts but remain mandatory hostile gates.

M231 passed its receipt law, unbiased algebra, exact bill, memory, and native
parity gates, but its five-process combined residual wall was
`4.848700220..5.171800120 ms`, above the frozen `3.227021568 ms` cap. M234 is a
failure fold of only that execution/provenance link. It is not a new
statistical mechanism and does not retune `k`, coefficients, seeds, residual,
or source-efficiency thresholds.

## Preserved estimator and bias class

M234 preserves M231's finite-population Horvitz-Thompson estimator exactly.
For `S=diag(u)W`, exact live

```text
p = S^T 1,  B = S^T S,  rho = diag(B),
```

and a uniform without-replacement row subset `H`, `|H|=32`, `g=8`, it forms

```text
that = g sum_(i in H) s_i^3
Ahat = g sum_(i in H) outer(s_i^2,s_i)
Ehat = g sum_(i in H) outer(s_i^3,s_i)
Dhat = g sum_(i in H) outer(s_i^2,s_i^2).
```

Only these four affine totals are sampled; `p`, `B`, and `rho` remain exact.
M215's unchanged affine collision formula is subtracted from M212:

```text
Chat_strict = Cfull_M212 - Chat_collision,
E[Chat_strict] = Cstrict,
E[Chat_strict + Rhat_D] = T_D.
```

The bias class remains exactly unbiased for every fixed generated rank-one
state. The M151 residual remains independent fixed-`q0`, `K=128`. No generic
Rao-Blackwell dominance claim is made.

## The sole composite repair

M234 changes no estimator arithmetic. It changes these four inseparable
execution/provenance details and nothing else:

1. **Explicit RNG owner.** Production constructs exactly
   `fnp.random.Generator(fnp.random.Philox(domain_seed))`; `default_rng`, an
   implicit bit generator, RNG reuse, retries, and state-dependent reseeding
   are forbidden.
2. **Empty-workspace hoist.** Before either BudgetContext, setup may allocate
   only the fixed-shape `fnp.empty` staged M212 inputs, M212 workspace, and
   M234 powers/cross workspaces. No fill, copy, stack, arange, permutation,
   gather, moment, source, or other value-dependent operation may be hoisted.
3. **Audit separation.** Runtime hashes, allocation ledger, host validation,
   finite/symmetry checks, receipt construction, and output digest happen
   outside the timed production body. They remain required in the five hostile
   traces and may kill the candidate.
4. **Static prebinding.** Canonical layer IDs, fixed shapes, expected epoch,
   scalar coefficients, and zero-value-independent views into the empty
   buffers are bound before timing. The timed correction receives this frozen
   plan; it may not reconstruct or validate static metadata.

This four-part change is one composite execution-topology repair of M231's
measured wall failure. It is not permission to change call shapes, fuse or
split positive-bill operations, alter arithmetic order, batch layers, change
precision, or claim compiler retirement.

## Frozen explicit Philox seed derivation

The random domain is `M234_ROW_PERMUTED_EXEC_V1`. Define

```text
MASK64       = 0xffffffffffffffff
DOMAIN_TAG64 = 0x4d3233345f455831       # ASCII "M234_EX1"
ROOT         = external_seed, required 0 <= ROOT <= MASK64
HIGH64       = DOMAIN_TAG64
               xor ((producer_epoch & 0xffffffff) << 32)
               xor ((31 & 0xff) << 24)
               xor ((256 & 0xffff) << 8)
               xor 32
DOMAIN_SEED  = ((HIGH64 & MASK64) << 64) | ROOT.
```

The expected producer epoch is the inherited generated-source epoch `231`.
This mapping is injective in the 64-bit external seed for the fixed domain and
binds epoch/layers/width/subset into the high word. Derivation and range/domain
validation occur before timing. Inside production, the explicit Philox
generator permutes the counted `(31,256)` integer label bank independently
along axis 1. The first 32 labels per layer are the receipt. The label bank is
not setup-hoisted: counted `arange`, zero-bill `broadcast_to`, and counted
`permuted` remain in production.

Pinned primitive evidence:

```text
flopscope/_registry.py
  D735DA7D36ECF05BA7B927452DB126FE297E33398F3903C59B886E1BC1228795
flopscope/numpy/random/_cost_formulas.py
  D14D86A2CA0700C0899318A9C7CD3F08E91AC80948682225D383D71E2D628F8F
flopscope/numpy/random/_counted_classes.py
  6D7AA1E9C4F7A135EF7487FAF6B645AEA61C74983FA780DAFFB68240C6DA3F0D
numpy/random/_philox.cp314-win_amd64.pyd
  8CEB13F5A97EB161FD7D93D2E597DC99D3387A76F32EF187A57103AC759BDA15
numpy/random/_generator.cp314-win_amd64.pyd
  69C5AA9B41C0A60EE8600A4C1434C86FA96DFC00F4CD3171AED9729AACAA549B
```

An audit probe confirmed that explicit `Generator(Philox(123))`, followed by
`arange`, `broadcast_to`, and one `permuted(axis=1)`, bills exactly `32,768`:
`1,024 + 0 + 31,744`. Construction of Philox and Generator is uncounted; its
wall remains inside production.

## Frozen production ABI and static plan

The setup plan owns references/views only; it contains no derived numeric
values:

```text
layer_ids      = (1,...,31)
epoch          = 231
shapes         = weight(31,256,256), powers(2,31,32,256),
                 cross(2,31,256,256)
views          = powers2, powers3, crossA, crossE,
                 rho_col, rho_row, p_col, p_row,
                 powersT, powers2T, scratchT, aaab_diag
scalars        = 12, 8, 4, 144, 96, 48, -192
```

All views are value-independent aliases of fixed empty/live buffers and add no
storage. External hostile validation proves plan identity, shape, dtype,
epoch, M212 receipt ownership, and domain seed before entering production.
The timed body contains no calls to an allocation ledger, hash routine,
`validate*`, host NumPy, sort/unique/set/list scan, finite check, symmetry
check, digest, adaptive branch, or exception-driven retry.

## Frozen exact FlopScope bill

Zero-bill `empty`, transpose/swapaxes/diagonal view construction, and static
Python metadata move outside production. The positive-bill circuit and total
remain exactly M231's:

```text
operation                            calls      exact billed FLOPs
arange(256,int64)                       1               1,024
broadcast_to(31,256)                    1                   0
random.Generator.permuted(axis=1)       1              31,744
take_along_axis selected S, f64         1           2,031,616
matmul (3 product-equivalents)          2         767,950,848
multiply                               16          57,901,056
add                                     9          36,569,088
sum                                     1             492,032
copyto                                  1              15,872
reshape                                 0                   0
TOTAL                                              864,993,280
```

No `empty`, `transpose`, `swapaxes`, or `diagonal` call may appear in M234's
timed correction operation receipt. Their absence does not change the bill
because each was zero-bill in M231. The composed arithmetic remains:

```text
M212                                1,249,253,376
M234                                  864,993,280
M212+M234                           2,114,246,656
retired M151 compiler envelope      3,727,757,440
raw arithmetic remainder            1,613,510,784
```

The `3.727757440B` figure is only a frozen comparison envelope. M234 receives
no M151 retirement credit without a later integrated ABI trace proving every
old operation and allocation absent.

## Frozen memory and five-process native gate

Numeric storage is unchanged from M231. Static view objects are metadata, not
new arrays:

```text
M234 incremental persistent          36.873046875 MiB
M234 incremental nominal peak        36.875000000 MiB
M212+M234 nominal persistent         138.955078125 MiB
fresh-process RSS cap                512.000000000 MiB
```

The exact frozen seeds are
`227700001,227700002,227700003,227700004,227700005`. Each runs in a fresh,
sequential pinned process. All five must have zero failure; exact constant
M212, M234, and combined bills; exact positive-bill calls; no forbidden timed
calls; matching hashes; valid unique receipts; finite symmetric sources; and
RSS below 512 MiB.

Both wall gates must pass in every process:

```text
r_M234 <= 0.002025121700262334 s
r_M212 + r_M234 <= 0.003227021568 s
2,114,246,656 + 5e11*(r_M212+r_M234) <= 3,727,757,440.
```

Whole-process wall and external audit wall are recorded diagnostically but do
not replace the official residual gate. A microbenchmark, median, warm rerun,
or theoretical estimate cannot substitute for all five hostile receipts.

## Frozen RED/GREEN order

No M234 implementation or test exists at freeze time. Strict TDD order is:

1. **RED static/provenance contract.** Tests fail only because the M234 module
   is absent. They require exact seed words, explicit Philox/Generator source,
   setup-hoist restrictions, static views/scalars, external validation, and no
   forbidden production code.
2. **GREEN premise/algebra.** At generated widths `3..9`, preserve M227/M231's
   cubic oracle, row-loop, gauge, zero, and `2e-10` algebra gates. At target
   shape, use M234's actual receipt to prove the collision delta against the
   M227 row oracle and exact source parity to `2e-9`.
3. **RED/GREEN native sidecar.** Freeze exact calls/bills and prove hostile
   validation is outside the correction context. Run the five seeds once in
   fresh sequential processes and aggregate all bill/wall/RSS gates.
4. **Only after a complete native pass, G0.** A native failure kills fixed
   M234. It may not be repaired or retuned under this ID.

## Source-efficiency and holdout firewall

If and only if the native gate passes, M234 inherits M227/M231's unopened G0
unchanged: the same 24 fresh cells, bootstrap seed `2270001`, 20,000
cell-cluster resamples, `upper90<0.99`, every cell `<1`, p99 ratio `<=1.25`,
and nonpositive width slopes. G1 remains state seeds
`22732001..22732104`, event seeds `22733001..22733008`, 16,384 events/cell,
and bootstrap seed `22730001`. The untouched holdout remains state seeds
`22732201..22732308` and event seeds `22734001..22734016`. No M161 diagnostic
cell becomes promotion evidence.

Parent artifacts are pinned as:

```text
M231_PREDECLARATION_20260809.md
  25C47D632C4426E8A2A05CD4DA3CF96F27D0685354DE7072536C4F1B5ACD3B0C
M231_FROZEN_MANIFEST_20260809.json
  C7BDF65BEB52CEF3D2BAC6BA569B4A47B8CC06DE3D57835A8DD8C344FD74B7D7
m231_flopscope_sidecar.py
  1431271863941F1EECB372AFA6B25EF682A9E41AE7A8F232CE81A7498B0CC9B2
M231_NATIVE_RESULTS_20260809.json
  41C681D908335129ADA3B25097D62BE1F12A80C1D226681F8BAE18EC2D2F5E3F
```

## Stop and credit rule

Any explicit-RNG, seed, setup ownership, static binding, audit-separation,
algebra, bill, call, wall, memory, or source-efficiency failure kills this
fully specified M234 implementation. No coefficient, `k`, allocation,
batching, precision, seed, threshold, or timer-boundary drift is allowed.

A native pass would grant only permission to open the already-frozen G0. It
would not grant compiler-retirement, final-output MSE, score, submission,
rank, prize, or winning-entry credit.
