# M175 — fixed B=8 labelled background/source ABI audit

This is a response-free, source-only repair attempt for M174's first broken
link.  It freezes the only permitted schedule:

```text
immutable zero-order background block -> labelled W/mu/V/J/source bundle
-> independent M163 compile -> explicit source conversion -> M125b carrier
-> release block
```

The blocks are exactly `[8, 8, 8, 7]`.  A tangent carrier is never fed back
into the zero-order covariance recurrence.  The audit concludes that the
current repository has no exact, metered producer for the required bundle and
therefore does not create an integration runner or a resource claim.

`verify_m175_static.py` locks the no-go evidence against the frozen sources;
`test_m175_static.py` invokes it.  Neither imports a contestant estimator,
FlopScope runner, scorer, truth, model response, or leaderboard data.
