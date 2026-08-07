# M120C independent result judge — 2026-08-07

## Verdict

**KILL_M120_CONNECTED_E_OMISSION_NO_RETRY**

The consumed M120C result is valid, complete, hash-bound, and internally reproducible. It is not corrupted. The frozen complete-adjoint protocol fails, so the M120 approximation that omits the connected zero-diagonal Price residual E is killed with no retry.

This judgment did not execute or regenerate any network, invoke the grid dispatcher, call the owner, modify a canonical artifact, access official/public/contest/champion/scorer data, or submit anything. It parsed the immutable canonical JSON directly. Reconstructing the 72 predeclared Philox direction vectors from their frozen direction-only seeds was the only random-number operation; it did not generate a network or evaluate the grid.

## Authorized lineage and artifact hashes

| Artifact | Required SHA-256 | Independently observed SHA-256 | Result |
|---|---|---|---|
| Installed sealed manifest v2 | a501fe1bf03d80b430eaa852be980d27822e1945f913b60f151ce1cd88cd1645 | a501fe1bf03d80b430eaa852be980d27822e1945f913b60f151ce1cd88cd1645 | PASS |
| Resealed release v2 | f7c10fab510a06b6177a5703cf622dd7a63c790d624bec40a80d4ed37aff1b73 | f7c10fab510a06b6177a5703cf622dd7a63c790d624bec40a80d4ed37aff1b73 | PASS |
| Installed-manifest PASS judge | 532f08f9d7479cfd4a6ef35c5a52e862fa28eca625a6d636a027d7a601e331c5 | 532f08f9d7479cfd4a6ef35c5a52e862fa28eca625a6d636a027d7a601e331c5 | PASS |
| M120C_CLAIM.json | d67328757378463dd22fb63fc747567b939d9781139790c70241e68a93b54d31 | d67328757378463dd22fb63fc747567b939d9781139790c70241e68a93b54d31 | PASS |
| m120c_binding_result.json | c77185f28de498aff3111b6916c5f5888e838c8008462089e6b59c3dea84ad93 | c77185f28de498aff3111b6916c5f5888e838c8008462089e6b59c3dea84ad93 | PASS |
| M120C_TERMINAL.json | 45ba65b2657222d0dccedcea36fea49e2383af0bd9595ba03ebef7363ce36e7c | 45ba65b2657222d0dccedcea36fea49e2383af0bd9595ba03ebef7363ce36e7c | PASS |

The installed PASS judge is the required independent authorization that follows the release's audit-not-execution state. It names the raw manifest digest above as the sole one-shot owner token. The permanent claim binds exactly that manifest digest, protocol M120C-EXACT-PREEXEC-v1, state claimed, and retry_allowed false.

The pinned Python 3.14.4 / NumPy 2.4.6 runtime still reports closed_manifest_errors(manifest, observed_digest) = (). All 11 manifest-bound source hashes therefore remain closed after execution.

## Canonical lifecycle integrity

The canonical root contains exactly three entries:

- M120C_CLAIM.json
- m120c_binding_result.json
- M120C_TERMINAL.json

There are no pending files, legacy result/failure files, duplicate outcomes, or alternate terminal artifacts. Claim, outcome, and terminal all reproduce the lifecycle's sorted, compact JSON encoding with a final newline.

The terminal names m120c_binding_result.json, binds its independently observed SHA-256 c77185f28de498aff3111b6916c5f5888e838c8008462089e6b59c3dea84ad93, and records status fail. The outcome itself records pass false and retry_allowed false.

The owner source checks for an existing canonical root before dispatch. The root is now permanently consumed, and the exclusive-claim lifecycle rejects any second attempt. I did not test that fact by calling the owner because doing so would violate the result-audit boundary; it follows directly from the sealed source and the present canonical state.

## Direct outcome parse and coverage

The canonical outcome is 5,638,403 bytes and contains exactly 648 records. I independently constructed the required key set

(width, depth, replica, input-facing layer, terminal output)

from widths 8/12/16, depths 2/3/4, three replicas, depth minus one layers, and every output.

| Integrity check | Observed |
|---|---:|
| Stored top-level record count | 648 |
| Parsed records | 648 |
| Required unique keys | 648 |
| Observed unique keys | 648 |
| Missing keys | 0 |
| Extra keys | 0 |
| Duplicate keys | 0 |
| Frozen dispatcher order | exact match |
| Shape failures | 0 |
| Records containing nonfinite arrays | 0 |
| Maximum covariance asymmetry | 2.7755575615628914e-17 |

Every record contains both standardized reference and standardized CP mean/covariance arrays, its reference norm, complete error, and four signed directional contractions.

## Independent recomputation from stored arrays

For every record I recomputed:

1. the complete reference norm from the stored standardized reference mean and covariance;
2. the complete relative error as the joint mean/covariance Frobenius error divided by that norm;
3. all four signed contractions against independently reconstructed unit directions from the frozen M120C-DIR-v1 Philox seed formula; and
4. the global means, every width/depth cell maximum, and the final Boolean gate.

No harness metric or gate evaluator was used for these calculations.

| Recomputed quantity | Maximum absolute discrepancy from stored value |
|---|---:|
| Reference norm, all 648 records | 0.0 |
| Complete error, all 648 records | 0.0 |
| Four signed contractions per record, 2,592 total | 0.0 |
| Every stored aggregate/gate leaf | 0.0 |

The outcome is therefore a faithful canonical ledger of the frozen computation rather than a damaged, truncated, or post-processed result.

## Frozen gate result

| Gate | Limit | Recomputed value | Result |
|---|---:|---:|---|
| Global mean complete error | at most 0.05 | 0.08401136710628065 | FAIL |
| Global mean absolute directional error | at most 0.05 | 0.00703568225271826 | PASS |
| Every-cell worst complete error | at most 0.10 | all 9 cells exceed | FAIL |
| Every-cell worst absolute directional error | at most 0.10 | 2 of 9 cells exceed | FAIL |

The exact cell maxima are:

| Cell | Worst complete error | Worst absolute directional error |
|---|---:|---:|
| w8 d2 | 0.16373987073587298 | 0.03290160730831711 |
| w8 d3 | 0.5878334212700304 | 0.10213390321877462 |
| w8 d4 | 0.6299931726901198 | 0.13140545865256545 |
| w12 d2 | 0.13954080891923532 | 0.034242025708748326 |
| w12 d3 | 0.28990579962782437 | 0.04537840234976838 |
| w12 d4 | 0.4116547263203532 | 0.0637301235914903 |
| w16 d2 | 0.15821386246391633 | 0.016444715560116917 |
| w16 d3 | 0.2932117719287561 | 0.03426957002957105 |
| w16 d4 | 0.37007383907249863 | 0.06516261459380115 |

The largest complete error is 0.6299931726901198 at key (8,4,1,0,6). The largest absolute signed contraction is 0.13140545865256545 at key (8,4,1,0,2), direction 0.

Further failure counts are:

- 404 of 648 complete errors exceed 0.05;
- 169 of 648 complete errors exceed 0.10;
- 28 of 2,592 directional values exceed 0.05;
- 4 of 2,592 directional values exceed 0.10.

The Boolean recomputation is exactly pass false. Failure does not depend on one borderline statistic: the global complete gate and every complete-error cell gate fail, while two directional cell gates independently fail.

## Exact CP-base algebra versus failed approximation

This verdict kills the omission of connected E, not the exact shared-CP implementation of its declared base recurrence.

The sealed preexecution lineage passed all 41 source-bound tests. Those tests include independent dense finite differences for the complete central mean/covariance pullback, exact CP-versus-dense equality for the E=0 recurrence, the signed diagonal reset, rank growth, permutation/positive-gauge covariance, and the analytic dense reference.

The stored result provides a second structural separation. At the terminal-adjacent reverse step, where exact and CP begin from the same incoming adjoint:

- maximum standardized mean discrepancy is 2.220446049250313e-16;
- maximum standardized covariance-diagonal discrepancy is 1.9081958235744878e-16; and
- 100% of the discrepancy energy in every nonzero row is off-diagonal covariance.

That is precisely the location of the omitted connected zero-diagonal Price residual E. After the omission is propagated through earlier reverse layers, it also perturbs the mean and covariance diagonal, reaching maximum absolute differences 0.02688500851235276 and 0.018732227898684436 respectively. This is expected propagation of the approximation error, not evidence that the CP factor/reset algebra malfunctioned.

Preserve:

- the exact central-covariance Jacobian and symmetric-slot factor of two;
- the exact separable Price component;
- the exact signed diagonal reset;
- the shared-CP factor transport and additive rank ledger;
- the analytic dense reference and complete stored evidence.

Kill:

- the claim that connected E may be omitted while retaining the frozen complete-adjoint accuracy gates through nonnormal depth;
- any promotion or correction experiment that depends on that omission;
- any retry, seed extension, threshold relaxation, or post-outcome addition of E under M120C.

A method that carries or approximates connected E would be a new mechanism requiring a new identifier, prospective theory, cost and source audit, independently frozen protocol, and fresh lifecycle. It is not a repair or retry of this consumed outcome.

## Consequence for M121

M121's one-affine, one-next-ReLU Edgeworth interface theorem remains a valid local theorem for a supplied finite symmetric k3/k4 source. The present M121 route, however, explicitly pairs the resulting mean/covariance defect with the cheap M120 all-output adjoint carrier. M120C has now falsified that carrier's connected-E omission.

Therefore M121 is blocked as currently specified. It cannot be promoted, implemented as an outcome candidate, or used for a correction experiment through the killed E=0 carrier. Its local interface may be preserved only as theory. Resumption requires either an independently valid exact/new carrier or a separately specified local-only contraction that does not rely on later E=0 propagation; either path is new prospective work.

## Consequence for M124

M124's shared-k3-projector source algebra is not numerically adjudicated by this M120C outcome. Its current manifest is DRAFT_NOT_FROZEN and execution_authorized false. Source-level algebra and projector research may remain as a separate draft.

However, M124 converts its projected source through the M121 delay-one interface and ultimately needs a valid downstream all-output carrier for end-to-end value. It may not inherit, bypass, or relabel the killed M120 E=0 carrier. No M124 execution or promotion may claim an end-to-end correction benefit from this branch until a new carrier dependency and non-overlapping prospective protocol are explicitly supplied and audited.

## Firewall and access provenance

The manifest/release firewall remains:

- generated networks only;
- no correction oracle or source construction;
- no public or contest outcomes;
- no targets;
- no scorer;
- no champion access; and
- no target-shape efficacy execution.

An AST scan of all 11 sealed sources found no networking-client imports. The canonical outcome contains no target, contest, champion, scorer, leaderboard, submission, public, or official string values. This judge used only local sealed artifacts and made no web, official-data, public-score, champion, scorer, or submission access.

## Final decision

The claim is consumed, the terminal is a valid hash-bound failure, the numeric ledger recomputes exactly, and no corruption exception exists.

**KILL_M120_CONNECTED_E_OMISSION_NO_RETRY**

No execution, retry, correction experiment, or submission is authorized by this judgment.

