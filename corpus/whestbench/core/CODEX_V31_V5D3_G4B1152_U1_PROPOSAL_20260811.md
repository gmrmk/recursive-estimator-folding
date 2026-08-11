# V31-V5D3-G4B1152-U1: recursively compressed GUARDS child

Date: 2026-08-11  
Status: **ZERO-EVIDENCE, HIGHER-RISK STATIC CHILD PROPOSAL**  
Authority: source construction and deterministic synthetic contracts only; no
generated-network, truth, scorer, hosted, selection, launch, or submission authority.

## 1. Objective, family rank, and boundary

Replace only the eligible deep matrix products in Kerdock v3.1 GUARDS with a
three-level, fully materialized Winograd schedule, while keeping the estimator's
nodes, weights, pruning rules, folds, tangent correction, output guards, and score
law unchanged. Use four fixed 1,152-row atomic blocks per grouped call.

This is not V31-G4 and does not supersede it. V31-G4 remains the low-assumption
champion proposal because it preserves the parent float32 association and exact
analytical bill. V31-V5D3-G4B1152-U1 is a separate higher-upside child that changes
float32 association, can change rescue sets and later widths, owns a more complex
buffer lifetime, and increases native call count on the disclosed seed-11 tape.

Normative parent and evidence anchors:

- immutable GUARDS archive SHA-256
  `8382E269C9B32E0935492734DDF8182560120F7E9331621AA18839D5D1F4EA06`;
- `row_blocked_winograd.py` SHA-256
  `A3BF5C8014198E33037D6AEAFC3F4138A98908754BB82BFCF5ACDD92B1D9FCCA`;
- `cost_model.py` SHA-256
  `2A42E0D9CA3A80ECB4FF2BE302CCFAAACFA34BF6FE920B1EEA27FEB7AE798D68`;
- `fold3_estimator.py` SHA-256
  `68449E3EFE3B82A860B884A2BD05C9260E1EFBD138A343257CDC51AD38A63F6F`;
- `kerdock_v3_estimator.py` SHA-256
  `076D0A5D81891DDCBB4509DC6E2BFF5459D935B5556490A85D98DAC60759AACF`;
- GUARDS wrapper SHA-256
  `5E7D52156B330BF63AC4FF0E0F38D864B32677F82BC8ED4D1382787A27D3E0C9`;
- low-risk V31-G4 proposal SHA-256
  `77EED01B6A7EF002BED93B4B81A0F2C7F9499B3A0395D5820A70728B50B9A326`;
- M116 in-place L3 implementation record SHA-256
  `396302C171622E89ED5B0BD9A57FCD46A2DAEA04BD07F786F598A90324634C23`;
- M116 fused-L3 theory SHA-256
  `AE044F785078DC7C410594CD30E92AAF9AFBDB443BFB806D08DA91B373F26F9A`;
- production-schedule baseline/variant script
  `corpus/whestbench/experiments/uf1_attack_composition/step1_production_baseline.py`,
  SHA-256
  `3C4490AFE0B85195D7332D543391FE7FDD810D746C5A949CD3DAE116CA61B7C3`;
- production self-attack result
  `corpus/whestbench/experiments/uf1_attack_composition/step5_selfattack_and_verdict.json`,
  SHA-256
  `28037C4BCF406C7CD614FD3605CFFFDF6A080B48102B8B5BF1401691B0BA6C69`.

The parent archive and V31-G4 remain immutable and separately packageable. This
child receives no evidence, score, selection, or fallback credit from either.

## 2. Exact arithmetic class

Use the executable V5 schedule `(a,b,c)=(7,7,7)` at every one of three Winograd
levels: all seven left operands, seven right operands, and seven product/fold
destinations are explicitly materialized and billed. The unattained V1
`(4,4,7)` movement floor is forbidden as a source bill.

For

```text
D(m,k,n) = m*n*(2*k - 1)
kc = k - (k mod 8)        kt = k - kc
nc = n - (n mod 8)        nt = n - nc,
```

define the positive-width depth-three core and ragged completion by

```text
W3(m,kc,nc)
  = 343*D(m/8,kc/8,nc/8)
    + 651*(m*kc + kc*nc + m*nc)/64

V5(m,k,n)
  = W3(m,kc,nc)
    + 1[kt>0] * {D(m,kt,nc) + m*nc}
    + 1[nt>0] * {D(m,k,nt) + m*nt}.
```

The two additions are, respectively, the ragged-k correction add and owned
n-tail copy. Grouping changes native call count only and never discounts this
analytical bill.

The required exact hook-3 fixture `(m,k,n)=(64,512,253,255)` is:

```text
depth-three divisible core       5,556,520,011
ragged-k direct correction         143,990,784
correction add                      15,998,976
ragged-n direct tail               228,049,920
owned tail copy                        451,584
                                  -------------
total                             5,945,011,275
```

Any source, independent expansion, or metered receipt mismatch kills the child.

The arithmetic is exact over the re-associated real-expression tree. It is not
bitwise equivalent to the parent float32 tree, so every promotion comparison is
numerical and paired; bitwise-parent claims are forbidden.

## 3. Frozen static shape replay and provenance limit

The committed tape
`corpus/whestbench/experiments/uf1_attack_eligibility/attack_eligibility_raw.json`
has SHA-256
`6D6869253E0126920BC955D2C9BD19F7CD3B8CB3B875F943170C3D6A91DB8BD9`
and contains historical generated-network diagnostics for seeds 11--15.
The companion committed width-sequence census
`corpus/whestbench/experiments/uf1_attack_eligibility/attack_stage3.json`
has SHA-256
`39275EAFE5FFF2587BDAEC81AB16545C588EBB40243B55B30580AB08BB6C5FE6`;
the independent seed-11 sequence verifier
`corpus/whestbench/experiments/uf1_attack_eligibility/attack_verify.json`
has SHA-256
`94A97AEB95C42DCBE1680C1ED9103D0F697751D71FF4AFD10C8AD6466C5C4515`.
Five
additional judge shape sequences for seeds 21--25 produced the reported second
half below, but their raw tapes and hashes are not committed. Therefore only the
five-tape half is presently reproducible from this repository; the ten-tape mean
is a reported cross-check and receives no permanent-evidence status until all five
missing raw sequences, their generator, environment, and SHA-256 values are bound.

Retrospective current/V5 deep-hook totals are:

| Seed | Current | V5-d3 |
|---:|---:|---:|
| 11 | 154,720,254,241 | 116,618,302,059 |
| 12 | 151,088,919,681 | 117,699,592,290 |
| 13 | 163,753,789,297 | 127,773,730,077 |
| 14 | 148,253,240,205 | 112,592,670,771 |
| 15 | 145,498,000,151 | 111,528,316,074 |
| 21 | 155,038,228,331 | 118,430,384,268 |
| 22 | 141,204,825,804 | 110,703,752,775 |
| 23 | 148,305,556,567 | 115,209,486,861 |
| 24 | 175,017,313,723 | 131,038,699,176 |
| 25 | 148,006,959,800 | 112,624,126,083 |

The reported ten-tape means are `153,088,708,780.0` and
`117,421,906,043.4`; the mean saving is `35,666,802,736.6` charged operations,
with per-tape savings `21.6006%--25.1282%`. These are frozen-parent shape replays,
not a child execution, complete bill, efficacy result, or universal bound. Because
reassociation may alter every later active width, the realized child must emit and
bill its own complete dynamic tape.

## 4. Fixed source schedule

Freeze `GROUP=4`, V5 `BLOCK_ROWS=1152`, and one participant process/thread before
any child execution. Since `64,512 = 56*1,152`, each V5-positive-width hook has
exactly 56 atomic row blocks and 14 groups, with no row remainder.

For each eligible hook, in this exact order:

1. Pack the full three-level right hierarchy once for the hook.
2. Capture every divisible-core left dependency for all four blocks into owned
   outer, middle, and leaf-left banks.
3. Compute the full-left ragged-n tail into disjoint owned scratch.
4. Compute the ragged-k direct correction into disjoint owned scratch.
5. Execute one `(group,343)`-batched core matmul using the once-packed right
   hierarchy and owned product bank.
6. Fold leaf to middle, middle to outer, and outer to output in the exact V5 order.
7. Add the saved ragged-k correction in original row/output order.
8. Copy the saved ragged-n tail in original row/output order.

No output write may precede steps 2--4. The order applies to all reachable
shared-base front slices with physical row stride 256 and `n<k`, `n=k`, or
`n>k`. All activation, group, leaf, correction, tail, and overlay views are
bound in setup; no hot reshape, stack, concatenate, padding, implicit copy, or
RHS repacking per row group is allowed.

Seed 11 has one core-only, five one-ragged, and 22 both-ragged hooks. Its fixed
call count is therefore

```text
14 * (1 + 5*2 + 22*3) = 1,078 native matmul calls.
```

This is 534 calls above current GUARDS and 721 above the low-risk seed-11 V31-G4
proposal. The 385-call `GROUP=4, BLOCK_ROWS=4096` headline belongs to the killed
memory form and is unavailable to this child.

If `kc<8`, `nc<8`, the row count is not divisible by eight, the V5 bill is not
strictly lower, a required view cannot be proven noncopying, or the positive-width
precondition fails, replay the immutable parent dispatcher through prebound overlay
views. That fallback retains the parent's exact 4,096-row partition, final
3,072-row block, and 16-row-block chronology. Direct fallback reports
`core=0,total=16`; L1 fallback reports `core=16,total=16` for even `n` and
`core=16,total=32` for odd `n`. It retains the parent analytical bill and never
reinterprets the V5 1,152-row block size as a parent-fallback partition. Prebind the
parent's complete `19,349,504`-byte L1 banks as mutually exclusive views of the
same union backing, including direct scratch. No separate fallback allocation,
data-dependent group size, retry, padding, alternate recursion depth, or unbilled
source path is permitted. Zero-width behavior and M186/M187 meaning must match the
parent exactly.

## 5. Complete workspace and phase-union requirement

The source must own this complete maximum-width grouped workspace:

```text
outer banks              8,257,536 bytes =  7.875000000 MiB
middle banks            14,450,688 bytes = 13.781250000 MiB
leaf-left banks         25,288,704 bytes = 24.117187500 MiB
product banks           25,288,704 bytes = 24.117187500 MiB
right hierarchy          2,666,496 bytes =  2.542968750 MiB
ragged-k correction      4,718,592 bytes =  4.500000000 MiB
seven-column n-tail        129,024 bytes =  0.123046875 MiB
                       -----------
total                   80,799,744 bytes = 77.056640625 MiB
```

Direct fallback scratch must overlay the mutually exclusive correction bank.
The V5 workspace must replace the parent's `19,349,504`-byte L1 workspace and
be phase-unioned with the dead `16,515,072`-byte Kerdock WHT scratch. Allocate one
union backing during setup and bind its WHT and V5 views without copying. The
source must prove that no V5-bank read or write occurs before WHT completion, no
WHT read occurs afterward, and no separate simultaneous V5 allocation exists.

The committed unwrapped-core receipt
`corpus/whestbench/experiments/uf1_attack_memory/champ.jsonl` (SHA-256
`5AA12CACA82E959BC04BAC1950DAD69A722DC1F415FDF7280CCBC0C32C3FBAC2`)
measured `474,681,344` bytes = `452.69140625 MiB`; the verdict file SHA-256 is
`7C6083A437E32B04ED556BC755DE74CA7FE2C371CCA2188C45D3F3663379E682`.
This is an unwrapped parent measurement, not a child or whole-GUARDS receipt.

With the exact replacement, phase union, and derived 8 KiB healthy GUARDS mask,
the static projection is:

```text
452.69140625 - 18.453125 - 15.75 + 77.056640625 + 0.0078125
  = 495.552734375 MiB,
```

leaving `16.447265625 MiB` under the retained, self-imposed 512 MiB campaign
gate. Without the phase union the projection is `511.302734375 MiB`; that form is
killed as too fragile before source construction. A fresh isolated whole-wrapper
process-tree peak is mandatory; projections and allocator assumptions earn no RSS
PASS.

The `GROUP=4, BLOCK_ROWS=4096` form is statically killed: its depth-three core
workspace is `251.04296875 MiB`, and complete ragged scratch makes it
`267.48046875 MiB`, projecting the wrapper to `701.7265625 MiB`
(`685.9765625 MiB` even with WHT phase reuse). `GROUP=8` and 2,048-row variants
receive no silent substitution or survivor credit.

## 6. Static, synthetic, and implementation gates

Given the disclosed historical tapes, before observing any additional generated or
challenge network for this child, freeze source/runtime/backend hashes, dtype and
layout, dispatcher predicates, view plan, exception classes, thread counts, bills,
buffer lifetimes, cleanup, and the announced Phase-2 rules.

Required deterministic synthetic contracts are:

1. Exhaust all parent-reachable positive widths `1<=k,n<=256`, including every
   residue class mod 8, `n<k`, `n=k`, `n>k`, alias and nonalias output, direct
   fallback, correction-only, tail-only, both-ragged, and maximum-width shapes.
2. Force `k=0` and `n=0`; V5 must not run, and parent exception/M186 behavior,
   guard report, output, and complete bill must replay.
3. Independently expand every movement, direct correction, tail, copy, and leaf
   product. The hook-3 fixture and dynamic complete bill must match exactly.
4. For every finite fixture, require relative Frobenius error `<=3e-6`, maximum
   absolute error `<=2e-4`, exact output shape/row order/dtype, and exact frozen
   exception class. The reference is the pinned float64 direct product `R`. When
   `||R||_F>0`, relative error is `||Y_child-R||_F/||R||_F`; when `||R||_F=0`,
   require `Y_child` to be bitwise zero and record relative error as undefined,
   never zero or a favorable floor. No favorable clamp, retry, redraw, width repair,
   or output substitution is allowed.
5. Prove capture-before-write and phase-exclusive lifetime through poisoned-buffer,
   shared-base, delayed-backend, and allocator-order fixtures. Any implicit copy,
   unresolved alias, early overwrite, or late WHT read kills.
6. Record canonical deterministic numerical payloads separately from measured
   wall/RSS receipts. Meter joins use task key plus payload hash; schedule-sensitive
   wall/RSS never enter a bitwise payload-equivalence claim.

No generated-network or scorer run is authorized by this record. Source construction
may proceed only through the no-forward inspection and synthetic-fixture rung after
the official rules and pre-evidence manifest bind.

## 7. Fresh paired gate and promotion

Only after Sections 5--6 pass may a separately authorized fresh depth-32 paired
panel compare the already sealed child to immutable GUARDS. Every pair must use the
same weights, seed, production rotation, and input nodes in isolated processes.
The pre-evidence manifest must freeze the confidence level, paired resampling unit,
replicate count, simultaneous multiplicity family, interval method, material
margins, denominator domains, and failure handling before any panel value is read.

Require all of:

- final-output relative error `<=2e-5` on every pair, defined as
  `||Y_child-Y_GUARDS||_F/||Y_GUARDS||_F` for a positive denominator; if the
  GUARDS norm is zero, require exact equality and fail closed rather than floor;
- ReLU/gate mismatch fraction `<=2e-4` on every pair;
- raw-MSE parity under a predeclared two-sided bound; no point estimate alone;
- zero failures, retries, nonfinite outputs, M186/M187 drift, or unplanned branches;
- complete per-invocation operation budget, official critical-path wall, cleanup,
  return, and simultaneous process-tree RSS `<=512 MiB`;
- the child dynamic width/call/bill tape recorded atomically with its output;
- paired upper confidence bound for the complete effective-cost ratio below one
  with a predeclared material margin;
- paired upper confidence bound for the official complete adjusted-score ratio
  below one with a predeclared material margin. Report raw-MSE and effective-cost
  ratios separately; neither substitutes for this official-score gate.

Under the provisional Phase-1 residual conversion `1e11 operations/s`, the reported
parent-tape extra-residual break-even is `0.305011--0.439786 s`, mean
`0.356668 s`. On seed 11 the extra 534 calls versus GUARDS allow about
`0.714 ms` per added call; the extra 721 calls versus V31-G4 allow about
`0.528 ms`. These are planning divisions, not wall forecasts or official-score
claims. When residual charging applies, the per-invocation cost gate includes
`1e11*delta_residual < delta_analytical_charge` with the announced strict boundary.
If Phase 2 removes residual charging but still scores analytical operations, the
residual break-even is inapplicable; retain analytical-bill, absolute-wall, RSS,
raw-MSE, and official adjusted-score gates. If the complete paired score effect is
not material, the child is killed for ranking even if numerically valid.

## 8. Kill rules and disposition

Kill V31-V5D3-G4B1152-U1 on any missing raw-tape provenance presented as evidence,
unexplained bill mismatch, V1-floor substitution, buffer-union failure, hot view or
copy charge, RHS repack, output-before-capture, numerical threshold failure,
branch/guard drift, nonfinite result, failure/retry, resource breach, or nonmaterial
official-score effect. Never tune group size, block rows, recursion depth, tolerance,
or route after seeing child results.

The static arithmetic upside is credible but unearned: the reported ten-tape totals
span roughly `21.6006%--25.1282%`, but five lack committed raw-tape provenance; the
repository-reproducible seeds 11--15 span `21.9720%--24.6264%`. The engineering
risk is materially higher than V31-G4: recursive float32 reassociation, ragged
corrections, an exact phase-overlaid memory proof, more native calls, and a dynamic
child bill. Therefore V31-G4 remains the champion proposal; this child may overtake
it only after source, numerical, RSS, residual, fresh paired, and official-rule
gates all pass. GUARDS remains the sole integrated artifact.
