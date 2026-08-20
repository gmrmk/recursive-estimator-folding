# M236 prenative erratum 2 -- transient current-payload input borrows

Date: 2026-08-09. Sealed after the GREEN compiler/static audit. The unexecuted
native entrypoint and runner had just been written under the prior approval;
this conflict was found by root's source audit before their static test or any
official-worker execution. No M236 native result, aggregate, or G0 exists.
This erratum narrows one literal conflict in erratum 1; it does not change the
compiler, block topology, arithmetic, bill, calls, memory owners, seeds,
thresholds, runner, or response ABI. The four-second runner/erratum timestamp
ordering is preserved as provenance and must not be represented as pre-code.

Frozen parent hashes:

```text
predeclaration  793786132F08CE71ABACE2BDA29ADE347ED2800B9615799F85BA7F71836E3CC1
manifest        3B9D3B43D7995FED5D1CA331B465F4DD71C236F0BA5F6D7497E392364D844CF2
erratum 1       54A63B652A7288EBE06C526C1B0300356DA7B3D8F79D9E9C0D0BA505127E56E1
GREEN module    6C9E9AF9727722CB6ADE5E1CDA56D3F7A0E7BF82EF35EBDAEFA8AA883A854B75
GREEN test      5E2DE041D68B0B07B437D5362D26195D4F7C7C5A1A45058E900BB4BB3AD4B722
```

## Unavoidable input-borrow exception

The pinned official worker supplies the current MLP as 32 float32 weight
arrays. The frozen M212 staging ledger requires two `fnp.stack` calls per
block. To feed the factor stack without a copy or changed operation, predict
may create exactly 31 transient read-only-use row views:

```text
factor_l = mlp.weights[31][l], l=0..30
shape=(256,), dtype=float32
```

Each factor view must share storage with the current carrier
`mlp.weights[31]`, have the exact row pointer implied by the carrier's first
stride, and be used only as an input to the corresponding frozen block's
factor `fnp.stack`. The 31 weight records must reference the exact current
owners `mlp.weights[0]` through `mlp.weights[30]`; no weight view or copy is
permitted.

Python record wrappers and slot lists own no numerical storage. They may hold
these current-payload references only during the current predict. Every block
slot is cleared in `finally` immediately after its two stack calls, the record
container is deleted before predict returns, and no estimator field, setup
owner, plan, audit buffer, output, closure, or returned value may retain a
factor-row borrow.

These borrows are not workspace, packing, allocation, copy, FLOP, memory-owner,
or sharing credit. Their underlying bytes are already owned by the official
current MLP payload and therefore are not added to the M236 numerical-owner
ledger. They do not relax the prohibition on predict-time output, workspace,
receipt, block-plan, or alias construction. Erratum 1's separately frozen
direct response view `mlp.weights[31][:32]` remains the only other payload
view permitted.

## Native audit additions

Before the official one-process run, the static harness test must prove from
the entrypoint that global record `l+1` binds weight `mlp.weights[l]` and
factor `mlp.weights[31][l]`, with no `copy`, `asarray`, `stack` outside the
frozen compiler, or retained record field. The same-worker gate must still
prove every slot is clear after each prediction and current-field identities
contain no payload-row objects.

Any additional current-payload slice, retained row borrow, input copy, changed
stack operation, or extra numerical owner kills fixed M236. All prior native
stop gates and the G0 closure remain unchanged.
