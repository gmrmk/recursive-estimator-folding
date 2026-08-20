# M145 deployable descendant repair -- 2026-08-07

## Disposition

**Structural source repair passed; runtime/resource gate is deliberately still
open.**  This is a new isolated descendant, not an edit to Formal-L1 or to the
earlier raw-QR M145 artifacts.

The third hostile audit found two correctness blockers.  Both now have distinct
mechanical repairs:

1. The shipped dependency closure is free of direct `numpy` imports.  An AST
   closure scan covers the three deployable M145 modules and every sealed
   Formal-L1 `.py` dependency.  It passes.  A guarded-import simulation with
   FlopScope/WhestBench stubs also imports the deployment module while rejecting
   ordinary NumPy if a shipped file attempts it.
2. Raw LAPACK QR is replaced with explicit `QD`, where
   `D=diag(sign(diag(R)))`, `sign(0)=+1`, for iid Gaussian `G=QR`.  This is the
   standard positive-diagonal QR representative and is Haar on `O(256)`.
   The pilot-conditioned right Householder map is therefore justified by Haar
   stabilizer invariance rather than by low-order projective simulations.

Candidate and comparator now build the same sign-corrected, radius-scaled bank
from the same domain-separated setup seeds.  They differ only after the pilot:
the candidate applies its frozen main-frame transport and the comparator does
not.  The saved canonical main-bank copy and exact restoration schedule are
preserved from the integrated parent.

## Cross-reference repair

The old proposed cross-reference protocol used float64 forward arithmetic.  It
is immutable historical material.  The descendant instead supplies a direct
FlopScope-float32 forward primitive and freezes an independent local-official
semantic-equivalence fixture.  No reference vector is generated until that
fixture and a streamed-vs-unchunked reduction test pass.

## Evidence actually run

`py_compile` passed on the deployment, direct-reference, runner, audit and
static-test sources.  The four static checks passed: import-closure scan,
guarded import-deny simulation, positive-diagonal sign algebra, and
radius-scaled Householder algebra.

The required pinned-runtime FlopScope trace did **not** run.  The local 0.10
cache is compiled for CPython 3.11, while the available interpreter is CPython
3.14; the other cache is FlopScope 0.8 and lacks `flopscope.numpy`.  Treating
either as the official 0.10 runtime would be a false certification.  The next
gate is a fresh official-runtime trace of both candidate and comparator that
records only costs, calls, memory, replay and failures.  It must precede any
efficacy authorization.

No efficacy, score, truth, reference output, leaderboard, submission or
champion state was touched.
