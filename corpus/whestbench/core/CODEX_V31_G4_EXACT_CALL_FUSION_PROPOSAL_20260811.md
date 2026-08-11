# V31-G4: exact row-group call fusion for GUARDS

Date: 2026-08-11  
Status: **ZERO-EVIDENCE STATIC COMPONENT PROPOSAL**  
Authority: source construction and synthetic contracts only; no generated-network,
truth, scorer, hosted, selection, launch, or submission authority.

## 1. Objective and epistemic boundary

Preserve the complete Kerdock v3.1 GUARDS estimator output and analytical bill,
while lowering only Python/native dispatch overhead by grouping four already-frozen
4,096-row blocks under one leading batch axis.

This is not a new estimator and cannot improve raw MSE. It can improve adjusted
score only under a rule that charges residual/wall overhead. If Phase 2 charges only
instrumented operations, or disallows this schedule, V31-G4 is score-neutral or
illegal and must stop.

Normative parent:

- archive SHA-256
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
  `5E7D52156B330BF63AC4FF0E0F38D864B32677F82BC8ED4D1382787A27D3E0C9`.

The original archive remains immutable and separately packageable. V31-G4 is a
new child package and never overwrites the parent or its selected/submitted copy.

## 2. Frozen mechanism

Keep `BLOCK_ROWS=4096`, row membership, row order, float32 pack formulas,
right-operand pack, seven Winograd leaves, fold order, direct-dispatch rule,
active-width decisions, terminal folds, guards, return dtype, and every reduction
unchanged.

Set `GROUP=4` before any execution. For an L1-selected product:

1. Pack the right operand exactly once, as in the parent.
2. Partition the 64,512 physical rows into the exact parent blocks:
   fifteen 4,096-row blocks followed by one 3,072-row block.
3. Process the full blocks in fixed groups `[4,4,4,3]` and the short block as
   `[1]`. Each group receives a new leading batch axis; no block is enlarged,
   padded, split, reordered, or paired with a different row.
4. Capture every member block's left Winograd children before writing any aliased
   output row.
5. If `n` is odd, compute the one-column direct tail for the same fixed group into
   disjoint `(GROUP, BLOCK_ROWS, 1)` scratch now, before the core call, exactly as
   the parent orders tail before core. Do not flatten it through a hot reshape.
6. Execute one batched `fnp.matmul` for the group's seven leaf banks. Pass the
   single three-dimensional packed right bank directly; native matmul performs the
   declared implicit broadcast over the new group prefix. Do not materialize or
   call `broadcast_to` on the right bank.
7. Reconstruct each block with the exact parent fold sequence, indexing children
   and products by group first, then leaf, and copy any odd tail back in parent row
   order.

Direct-dispatch hooks remain byte-for-byte on the parent loop in this family.
Grouping direct hooks is a different child and receives no V31-G4 credit.

No hot `reshape`, `stack`, `concatenate`, padding, or completion-order reduction is
allowed. The child explicitly moves the caller activation allocation to setup and
binds every row-group view there, or else supplies an independently metered proof
that its chosen construction is uncharged; parent `predict` currently owns that
allocation, so silent inheritance is forbidden. Any setup operation charged by the
announced rules remains in the complete bill. Views may not copy. The final two
matrix dimensions, their strides, and every per-leaf row association presented to
matmul remain exactly parent-equivalent; only the declared leading group axis and
the RHS broadcast batch strides may differ. A failed view/stride proof kills this
child.

## 3. Static call census

The committed seed-11 28-hook tape in
`corpus/whestbench/experiments/uf1_attack_eligibility/attack_eligibility_raw.json`
(SHA-256 `6D6869253E0126920BC955D2C9BD19F7CD3B8CB3B875F943170C3D6A91DB8BD9`)
is a diagnostic, not a universal network promise. It has:

- 11 L1-eligible hooks (`k` even), of which 5 have even `n` and 6 have odd `n`;
- 17 parent-direct hooks;
- 16 parent row blocks per hook.

Parent deep native matmul calls:

```text
5*16 + 6*(16 core + 16 tail) + 17*16 = 544.
```

V31-G4 calls on that same tape:

```text
5*5 + 6*(5 core + 5 tail) + 17*16 = 357.
```

This is a 187-call, 34.375% reduction on that tape. Runtime widths remain
shape-dynamic; the implementation groups every lawful L1 shape by the same fixed
rule and never selects `GROUP` from values, timing, seed, score, or prior output.

The 11 L1 hooks' parent analytical bill is `58,421,643,553`. V31-G4 must reproduce
that number exactly. Concurrency, batching, and fewer API calls never discount
charged arithmetic.

## 4. Memory schedule

At maximum width, keeping the parent 4 MiB direct scratch ungrouped, the grouped
workspace is:

```text
direct scratch                         4,194,304 bytes
grouped one-column tail                   65,536 bytes
grouped left children                 29,360,128 bytes
shared right children                    458,752 bytes
grouped products                      29,360,128 bytes
                                      ----------
total                                 63,438,848 bytes = 60.5 MiB
```

The parent workspace is `19,349,504` bytes, so the increment is `44,089,344`
bytes = `42.046875 MiB`. The committed core-only receipt
`corpus/whestbench/experiments/uf1_attack_memory/champ.jsonl:2` records
`474,681,344` bytes = `452.69140625 MiB` for the unmodified
`kerdock_v3_estimator.py`; `uf1_mem_verdict.json:59-62` binds that identity.
Adding the exact permanent-buffer delta projects `494.73828125 MiB`, and the
healthy GUARDS finite mask adds another derived `0.0078125 MiB`, for about
`494.746 MiB`. This is not a measured whole-wrapper peak. It leaves about
`17.254 MiB` under the retained, self-imposed 512 MiB campaign gate, not the
mechanically enforced contest limit. A source-lifetime proof and isolated
whole-wrapper process-tree receipt are mandatory before any resource PASS.

`GROUP=8` is excluded from this child: its row-dependent banks add roughly 98 MiB
over the parent and project above the retained 512 MiB campaign gate before new
lifecycle overhead. This is a family-risk choice, not a claim that the contest's
mechanically enforced memory limit is 512 MiB.

## 5. Exactness and synthetic contracts

Given the disclosed pre-existing seed-11 diagnostic, before any additional
generated/challenge network is constructed or observed for this child, seal all
source, runtime, backend, dtype, layout, thread, environment, bill, and archive
hashes, then run deterministic hand-constructed fixtures only.

Required contracts:

1. Exhaust every positive-width parent-reachable `1 <= k,n <= 256` dispatch
   class, including even/odd `n`, the 3,072-row remainder, nonaliasing, and every
   reachable shared-base front-slice geometry with physical row stride 256:
   `n<k`, `n=k`, and `n>k`. Direct fallback, zero-valued/finite extremes, and all
   active-width boundary transitions are mandatory. Separately force `k=0` and
   `n=0`: the grouped kernel must never run, and the exact parent exception, M186
   branch, guard report, output, and bill must replay unchanged.
2. Parent and V31-G4 outputs must be bitwise identical; finite/exception states,
   branch labels, active sets, guard reports, and final output hashes must match.
3. Analytical operation receipts must match exactly for every shape. Any billed
   reshape/copy/padding/setup delta must be included; any unexplained mismatch kills.
   The grouped child must also update `predicted_core_calls` and
   `row_blocked_bill_identity`: they report five L1 group calls per core/tail product
   at `m=64,512`, while direct-dispatch shapes continue to report sixteen.
4. The fixed 4,096-row partition and per-row float32 association must be proven and
   independently checked. The existing grouped-L3 experiment's zero-word mismatch
   is supporting architecture evidence only, not V31-G4 proof.
5. Peak RSS must be the simultaneous process-tree peak, and wall/residual must include
   setup, joins, cleanup, guards, and return. Normative participant execution is one
   process, one worker, and one participant-side native math thread. The trusted
   backend's process/thread allocation is inherited from and bound to the official
   rules; this child neither constrains nor enlarges it.
6. The immutable parent must replay exactly before the child receives any comparison
   credit. No parent failure, retry, alternate grouping, or post-result repair is
   allowed.

## 6. Promotion and kill rule

After official Phase-2 rules bind and the static/synthetic gates pass, a fresh paired
network panel may compare the already sealed child with immutable GUARDS. Promotion
requires all of:

- bitwise-identical complete outputs and identical guard/branch states on every pair;
- zero failures and strict complete per-invocation budget/resource compliance;
- identical charged analytical bill, unless an explicitly enumerated setup charge
  makes the child larger;
- a predeclared material reduction in the official adjusted score or its exact cost
  multiplier under the announced law, with a paired upper confidence bound below
  one;
- no regression on worst-case wall, simultaneous RSS, cleanup, or return.

Kill V31-G4 on any output bit change, branch/guard change, right-pack repetition,
hot view charge, padding, changed row partition, incomplete alias capture, resource
breach, or nonmaterial official-score effect. If residual time is absent from the
Phase-2 score, classify it as a useful engineering component at most, not a ranking
candidate.

## 7. Disposition

V31-G4 is the strongest current low-assumption implementation successor because it
does not ask a new statistical theorem to work. It also cannot close an order-of-
magnitude MSE gap: its best possible effect is cost-only. GUARDS remains the sole
integrated artifact until every gate above is earned.
