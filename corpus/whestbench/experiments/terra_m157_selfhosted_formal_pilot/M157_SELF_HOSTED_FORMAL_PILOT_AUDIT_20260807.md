# M157 self-hosted Formal-pilot proposal reuse audit

## Disposition

**STRUCTURAL PASS; NOT DEPLOYED.** M157 is an isolated descendant of frozen
M145. It removes M145's separate 32-product dense proposal pilot and replaces
its proposal statistic with the even terminal-kink response of the Formal q0
pilot that the estimator already requires. It caches that q0 Formal state,
freezes q1, transforms only main frames, and then consumes the cached q0 state
when completing the estimator.

This is a new adaptive proposal law, not a numerical equivalence claim for
M145. No truth, labels, reference output, efficacy artifact, MSE, score,
leaderboard, submission, or champion change was opened or performed.

## Required q0/q1 order

Let `q0` denote M145's radius-scaled provisional pilot-frame law and let
`q1(. | q0, W)` be the uniform/ACG main-frame mixture produced from the pilot.
The only valid order is:

```text
analytic regimes from W
  -> Formal q0 pilot, including owned rescue/fold state
  -> even kink-only q0 signature and q1 fit
  -> q1 anchors, exact mixture weights, and frame coefficients
  -> transform 122 main frames only
  -> Formal main stream + cached q0 weighted contributions
  -> reverse transforms and canonical restoration
```

The q0 planner reads only provisional pilot rows, MLP weights, and analytic
regimes. It does not read a main row, q1 anchor, q1 weight, or response from a
transformed frame. The M157 event trace fixes that pilot/proposal/main order.

The proposal signature for pilot pair `i` is

```text
S_i = 1/2 [ K_Formal(z_i; W) + K_Formal(-z_i; W) ],
```

where `K_Formal` contains only the final coordinates that remain in Formal's
terminal kink regime. Dead and on coordinates are intentionally omitted. The
sidecar normalizes signature energy before forming its scatter, so a common
positive output-dimension scaling cancels from the probability vector; M157
nevertheless treats the `[1024, kink_count]` array and float32 operations as
the complete new proposal specification. On the target-shaped structural MLP,
`kink_count = 109`.

## Conditional importance argument

M157 preserves M145's existing centered frame coefficient construction. With
`N=126`, pilot-frame count `p=4`, main-frame count `m=122`, and
`w(x)=q0(x)/q1(x | q0,W)`, it uses

```text
c0 = N/p * (1 - wbar),    wbar = (1/m) sum_j w(X_j)
c1_j = N/m * w(X_j).
```

Conditioned on the entire q0 pilot and its fitted q1, independent main draws
satisfy `E_q1[w(X)]=1` and `E_q1[w(X) h(X)] = E_q0[h(X)]`. Hence the conditional
expectation of the centered pilot term is zero, while the main term has the
q0 target expectation. The proposal may be an arbitrary pilot-only function;
using `S` therefore adds no adaptive-importance bias provided the existing
M145 conditional-frame law and its exact sidecar density formula hold.

This argument preserves only the importance-weight/causality property. It
does not assert that Formal pruning, folding, analytic dead fills, float32
rounding, or M157's newly chosen proposal statistic make the estimator
unbiased for the original full MLP. Those are separate established limitations
and remain unchanged or unassessed here.

## Symmetry and coupling

Swapping a q0 pilot direction with its antipode swaps the two terms in `S_i`.
The signature and scatter are therefore sign-even. The q1 ACG component uses
an axial quadratic form and is mixed with the same uniform component as M145;
the unchanged sidecar supplies the corresponding bounded positive weights.

Only main frames receive Householder transforms. Pilot q0 frames remain
provisional, and a `finally` path reverses every applied transform then copies
the immutable canonical main bank. The two generated-only M157 predictions
have the same output digest and exactly restore the initial bank after each
call.

## Target-shaped structural result

The sealed trace executes one generated 256-wide/depth-32 He MLP twice under
FlopScope. It is not an outcome or efficacy run.

| quantity | M145 locked candidate trace | M157 first structural trace | difference |
|---|---:|---:|---:|
| billed FlopScope operations | 184,270,895,262 | 176,831,647,081 | -7,439,248,181 |
| recorded matmul dispatch calls | 701 | 669 | -32 |
| FlopScope `matmul` calls | 1,078 | 1,046 | -32 |
| local residual seconds | 0.140115606 | 0.130339808 | diagnostic only |

The 32 removed dense pilot dispatches have shape bill

```text
118,013,952 + 31 * 235,913,216 = 7,431,323,648.
```

The observed net bill reduction is 7,439,248,181. The additional 7,924,533
operations reflect removal of the dense pilot's tracked elementwise work net
of M157's q0-state copy/signature handling; it is a trace result, not an
analytic cost claim. The local residual comparison is not portable and must
not be multiplied into an official-runtime forecast.

M157 is maximal for this mechanism: all 32 dense proposal-pilot products are
gone, while the 669 remaining Formal/main dispatches match the corresponding
M145 non-dense structural schedule. Removing more would require a second
mechanism that changes Formal/main arithmetic rather than rehosting the
proposal on its already-required q0 state.

## Retained state and memory

The target plan retains the original q0 first activation plus the pilot tail
states needed after q1 coefficients exist. At the target shapes its explicit
state is 7,831,552 bytes (7.469 MiB):

```text
x1 copy          2,097,152 bytes
x29 owned bank    2,097,152 bytes
x30                999,424 bytes
x31              1,048,576 bytes
terminal kink      892,928 bytes
four retained fold/weight matrices 696,320 bytes
```

Most tail state and matrices already coexist in M145's later Formal path. The
reordering's material additional retained state is the 2 MiB q0 `x1` copy;
the separate dense pilot activation is removed. For arbitrary regimes the
retained q0 activation family is bounded by five 2048-by-256 float32 buffers
(10 MiB), plus small fold matrices. M145's 481.977 MiB locked local peak is
not a deployment authorization: a clean-process M157 RSS trace is still
mandatory because allocator lifetime and streamed-main overlap determine the
actual peak.

## Implemented structural scope

`m157_selfhosted_formal_pilot.py` implements the entire q0-plan/q1-main
reordering, output assembly, moment tangent, exact existing mixture-weight
sidecar, and restoration path. The structural test checks finite output,
event causality, no `pilot_surrogate:*` stage, bounded valid weights, q0 state
reuse after q1 freeze, and exact bank restoration. It does not compare M157's
output to M145 because the proposal statistic is intentionally different.

## Fail-closed next gate

Do not integrate M157 into M145 or the champion. Any next step requires all
of the following without opening an outcome artifact:

1. clean-worker target-shaped RSS and residual trace;
2. independent audit of the conditional-frame density assumptions and the
   centered q0/q1 weighting identity;
3. adversarial zero-kink, all-kink, and early-rescue structural cases;
4. independent numerical audit of the new proposal signature and float32
   proposal boundary behavior;
5. a new frozen manifest and hostile pre-execution review.
