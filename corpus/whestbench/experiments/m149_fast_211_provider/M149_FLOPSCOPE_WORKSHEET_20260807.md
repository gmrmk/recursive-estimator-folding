# M149 conservative cost worksheet

This worksheet covers only one local `[2,1,1]` coefficient plus tangent.
It is not a contest score or a response-cell trace.

| component | calls | favorable lower-bound billing | total |
|---|---:|---:|---:|
| fixed outer nodes | 87 bivariate calls | 48 angular evaluations/call x 10 | 41,760 |
| bridge pair statistics/tree | 3 bivariate calls | 48 x 10 | 1,440 |
| local conditional/tangent/scalar accumulation | fixed | 4,096 | 4,096 |
| **conservative worksheet total** | | | **47,296** |

The runtime also counts the actual number of angular evaluations returned by
M147.  It fails before returning if that count exceeds 8,000.  The worksheet
is under the frozen 102,400 billed-op reserve by 76,224 ops.  This is only a
FlopScope-like scalar worksheet: native `flopscope` integration must replace it
before any contest-facing use.

The nested outer rule is QUADPACK's fixed Patterson 43/87 sequence.  It
evaluates 87 nodes once; the 43 rule is a literal subset and supplies the
absolute value and tangent disagreement certificates.  The inner primitive is
M147's endpoint-safe Rosenbaum/Plackett analytic bivariate call, restricted by
the hard angular cap.  There is neither recursive subdivision nor adaptive
retry.
