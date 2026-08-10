# M233 disposition: killed at inclusive execution and allocation boundary

The new producer is semantically correct on its static gates: it preserves M205
factor/zero behavior, M224 values and radii, gauge, permutation, and strict
provenance refusal. It charges 174,592 additional FlopScope FLOPs for producer
operations above M228's 21,693,056 kernel bill.

Its first binding fresh trace fails the frozen execution gate: 18.9948 ms is
above 16.133917 ms and 84.9386x is below strict 100x. Per the predeclared
fail-closed rule, the other five processes were not run.

It also does not satisfy M233's requested no-free-setup boundary: the 325,872
bytes of producer workspace are disclosed in the 8,841,200-byte buffer ledger
but allocated before `BudgetContext` and the raw timer. That is a second kill
reason, not a result to reinterpret as upstream reuse credit.

M233 is a killed implementation. Its exact semantic identity, charged
operation census, and buffer accounting are preserved as salvage evidence; no
M212 or full-caller integration, variance, score, truth, response, or
challenge-weight work occurred.
