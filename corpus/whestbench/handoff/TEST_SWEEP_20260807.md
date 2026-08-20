# Response-free test sweep - 2026-08-07

## Result

All 24 response-free M154-M177 test entry points passed against the frozen
source snapshot. Twenty-three run directly from this private corpus when its
external dependencies are supplied. M174 also passed from the original
source-equivalent layout because its historical verifier intentionally hashes
the organizer-authorized FlopScope installation at a fixed adjacent path.
The competition environment is not vendored into this repository.

This is a source/static/numerical contract pass. It is not an efficacy pass,
leaderboard result, winning claim, submission, or authorization to inspect a
sealed response.

## Frozen numerical environment

```text
Python 3.14.4
NumPy 2.4.6
WHestBench 0.14.0
FlopScope 0.10.0
mpmath 1.3.0 (isolated temporary target; M165/M168 only)
```

## Portability closures made for this handoff

- M157 originally could not import the Formal parent because the compact
  handoff omitted `row_blocked_production/candidate_source/`. The seven
  source-only dependencies are now included. Their text is identical to the
  frozen originals, apart from repository newline normalization. No results,
  challenge arrays, archives, or binaries were copied.
- M165 and M168 require `mpmath`. The exact optional pin is recorded in
  `requirements-repro.txt`; testing used an isolated temporary target and did
  not modify the pinned competition environment.
- M174's historical verifier deliberately binds to the installed FlopScope
  source hashes recorded in its manifest. It passed in the original layout.
  A fresh clone must mount/recreate the organizer-authorized environment at
  the expected relative location or audit those hashes externally. Do not
  vendor or silently weaken that check.

## Sweep accounting

```text
response-free entry points enumerated: 24
passes in frozen/source-equivalent layout: 24
mathematical or contract failures: 0
portable-clone environment dependencies: 3 entry points
  M165: mpmath 1.3.0
  M168: mpmath 1.3.0
  M174: organizer-authorized FlopScope source tree at frozen relative path
```

The earlier 20/24 partial sweep was therefore an environment/layout diagnosis,
not evidence against the mechanisms. M157 passed after the missing lawful
source dependency was restored; M165 and M168 passed after supplying the
declared high-precision library; M174 passed against the environment source
tree its manifest was designed to authenticate.
