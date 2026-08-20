# M143 second independent hostile re-audit -- 2026-08-07

## Decision: PASS

The repaired M143 authorization and confirmation firewall is internally
consistent and fail-closed for the declared experiment-governance threat
model.  Root may now create **exactly one** canonical, bound development
authorization for exactly one frozen development response screen.  That
authorization must use a new 16--128 character nonce, its canonical
`m143-SHA256(nonce)` authorization ID, the current manifest and runner hashes,
the exact `development` split, one absolute output path whose parent already
exists, and the canonical receipt path in M143's fixed default receipt ledger.
Root must not create a second development authorization or delete/alter the
receipt ledger.

This audit did not create an authorization, did not create the default receipt
directory or any default receipt, and did not call `build_cell`, `run_split`,
or any response/efficacy path.  It used only isolated temporary receipt ledgers
for the protocol tests.

## Independent verification

### Frozen identities

The supplied repaired hashes reproduce exactly:

| artifact | SHA-256 |
|---|---|
| runner | `1f0d31ec7e28d98cd84fc64fac3bc3a67293f6060d14f085f8f0005c92a9a81c` |
| manifest | `6338584fdf89813c6e6f0c2c46bc72ccbcb22b5d600a6766ba8d6bf319bce215` |
| protocol/firewall tests | `8113e1c580272a8432d34862d4fb876d45980df4dcabafbf72f168bd52901f78` |
| repaired pre-theory/report | `ca8cd457647027cd1bd5742cd540aaa2c27ffa92cda9532d2527ae8b0e550be0` |

All eight entries in `execution_artifact_hashes` match their current files:
the M143 proposal module and runner plus the M120, M125, M126, M129, M131,
and M133 dependencies.  The manifest, cost crosswalk, stored structural trace,
and root re-audit trace all parse as JSON.  The proposal module, runner, both
test sources, and structural-trace source compile with `py_compile`.

### Authorization identity and exact output binding

`authorize` requires and checks all of the following before it returns:

* candidate exactly `M143`;
* requested split exactly equal to the authorization's split and corresponding
  `authorize_<split>` exactly `true`;
* current manifest SHA-256 and current runner SHA-256;
* nonce and authorization ID matching the restricted 16--128 character token
  grammar;
* authorization ID exactly
  `m143-` plus the SHA-256 of the nonce;
* CLI output supplied as an absolute path and resolving exactly to the absolute
  bound output path;
* an existing output parent directory; and
* the bound receipt path resolving exactly to the nonce-derived path under the
  fixed receipt root.

The hostile tests reject stale manifest and runner hashes, the wrong split, a
noncanonical authorization ID, and a different output path.  The output is
ultimately opened in exclusive `x` mode, so replacement is also refused at the
write boundary.

### One-shot receipt order and durability

Static AST/source verification establishes the execution order

```text
authorize -> output-existence check -> consume_authorization -> run_split
           -> exclusive output creation.
```

`consume_authorization` derives the receipt solely from the nonce and fixed
ledger root, creates it with `O_WRONLY|O_CREAT|O_EXCL`, writes the canonical
payload completely, and `fsync`s it.  The payload binds the authorization file
absolute path and hash, candidate, ID, nonce, split, manifest, runner, and
authorized output.  Any pre-existing receipt rejects the nonce even if the
old output was deleted or a new authorization tries to bind that nonce to a
different output path.  A crash after exclusive creation leaves a receipt (even
if incomplete), so reuse still fails closed.  Confirmation later requires the
receipt bytes to equal the exact canonical payload rather than trusting its
existence or a claimed hash.

The independent test run verified output deletion and path-change resistance,
as well as forged receipt-payload rejection.  The default
`authorization_receipts` directory remained absent after all checks.

### Exact development prerequisite and independent confirmation gates

A confirmation authorization independently binds absolute development-result
and development-authorization paths and their exact SHA-256 values.  Validation
then re-authorizes that exact development authorization against the current
manifest, runner, development split, output, ID, nonce, and canonical receipt.
The development result must bind candidate `M143`, split `development`, current
manifest, current runner, and exact frozen `CONFIG`; its authorization
provenance must exactly equal the revalidated authorization and receipt.

Completeness is enforced as exact set equality, not a minimum count:

* both families, widths 5 and 6, both frozen cell seeds, and repetitions 0--63;
* one and only one record for every `(family,width,seed,repetition)` key;
* finite nonnegative MSEs for M133, scale-only, and M143 in every record;
* one and only one cell for every `(family,width,seed)` key;
* exactly three proposal-snapshot layers per cell and all three method hashes;
* all three finite nonnegative cell-level method summaries; and
* no protocol failures.

The validator rebuilds pooled and per-family M143/M133 primary summaries and
M143/scale-only attribution summaries directly from the complete record MSEs.
It deterministically reruns all 10,000 paired-record bootstrap resamples with
the frozen child streams, recomputes both width trends, applies strict upper
bounds, and requires the pooled **and both-family** conjunction for each gate.
Stored ratios and gate booleans must exactly equal the recomputation, but those
assertions cannot make a failing record set pass.  Tests reject forged failing
records with asserted `true` gates, missing records, stale candidate/manifest/
runner/config identities, protocol failures, forged receipts, and a different
confirmation output.  A structurally complete passing fixture is accepted only
after the independent record-level recomputation passes every gate.

## Reproduction record

* `21/21` pre-outcome tests passed: ten algebra tests and eleven protocol/
  firewall tests.
* Five Python sources compiled.
* Four JSON artifacts parsed.
* Every embedded execution hash and all four supplied repair hashes matched.
* Static ordering and both exclusive-create boundaries passed inspection.
* No authorization, response result, efficacy outcome, or default receipt was
  created.

## What a development PASS would still not prove

Even if the single authorized development screen passes both gates, it proves
only generated small-width proposal-variance evidence for the two-component
M143 proposal.  It does not prove confirmation performance, target-width or
contest performance, an integrated target-ready M121/M125 estimator, the
protected cost crosswalk as an integrated measured runtime, champion
replacement, or submission fitness.  Confirmation remains closed until a
separate post-development audit and a distinct one-shot confirmation
authorization bind the exact development authorization and result.

