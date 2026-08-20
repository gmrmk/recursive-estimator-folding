# M145 deployable structural audit — 2026-08-07

## Disposition

**STRUCTURAL EXECUTION PASS; REMOTE RESOURCE PROJECTION FAIL; EFFICACY LOCKED.**

This audit opened no truth vector, reference label, error, score, public row, or
competition instance.  It used generated He networks only.  It does not
authorize an outcome screen, submission, designation, or champion mutation.

## Runtime repair found by the trace

The first pinned-runtime trace failed before prediction because `setup()` tried
to delete QR temporaries local to `signed_haar_radius_bank()`.  Those variables
had already left scope.  The descendant was repaired by removing that invalid
`del`; no estimator mathematics changed.  Four static/import tests pass after
the repair.

The trace used CPython 3.11, NumPy 2.4.6, and the real cached FlopScope
0.10.0+np2.4.6 package.  A narrow audit bridge supplied only `BaseEstimator`,
`SetupContext`, and `MLP` containers because the cached full WhestBench wheel's
optional pyarrow binary is not compatible with the available CPython runtime.
The bridge does not emulate any billed array operation.

## Frozen structural observations

Five fresh candidate processes used independently generated width-256,
depth-32 He networks and independently seeded signed-Haar frame banks.  Each
candidate executed twice to test restoration/replay.

| run | billed FLOPs | local residual s | local effective | matmul dispatches | operational peak MiB | 5x-residual effective |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 182,209,254,500 | 0.374436 | 219,652,884,734 | 701 | 368.25 | 369,427,405,672 |
| 1 | 161,124,559,109 | 0.148516 | 175,976,178,366 | 699 | 346.54 | 235,382,655,392 |
| 2 | 178,842,410,478 | 0.152163 | 194,058,740,102 | 698 | 353.96 | 254,924,058,598 |
| 3 | 183,063,504,620 | 0.166338 | 199,697,304,199 | 702 | 363.46 | 266,232,502,515 |
| 4 | 190,302,812,480 | 0.167895 | 207,092,301,347 | 704 | 376.68 | 274,250,256,815 |

All 5/5 first predictions were finite with no exception.  All 5/5 repeated
predictions were bitwise identical.  Both restoration defects were exactly
zero in every candidate process.  Candidate, matched comparator, and the
independently regenerated bank had the same SHA-256 in the paired trace:
`03fc693be4a6f6a609ba8d7e26c95fbb1389add936addd5068bc36ef481a206d`.

The matched comparator also completed without failure: 174,394,190,116 billed
FLOPs, 0.147623 s residual, 189,156,469,391 local effective compute, 669
recorded estimator matmul dispatches, and 333.45 MiB operational peak.

## Resource firewall

The contest budget is 272,000,000,000 effective FLOPs and prior official-runner
measurements showed roughly 5x local residual time for call-heavy candidates.
Under that pre-existing hostile projection, 2/5 candidate processes exceed the
budget; run 4 misses by 2.25B and the cold run misses by 97.43B.  Therefore the
declared zero-resource-failure gate is not met.  Local success is insufficient
because one over-budget evaluation is catastrophically expensive.

The localized mechanism survives: sign-correct Haar generation, conditional
Householder transport, exact restoration, identical comparator coupling, and
the f32 target primitive all passed their structural checks.  The deployable
configuration remains ineligible for efficacy until a response-free descendant
reduces call/residual exposure and independently re-passes this firewall.

## Next mutation allowed by the ledger

The pilot is evaluated once to construct the proposal and again by the formal
estimator.  A distinct descendant may memoize exactly reusable pilot states,
provided it proves identical proposal law and estimator ownership and fits the
memory gate.  Merely loosening the remote factor, removing the cold run, or
opening efficacy is forbidden.
