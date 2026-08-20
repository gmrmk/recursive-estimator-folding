# M226 predeclaration -- preallocated fused rho-.08 execution

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_CODE_AND_TESTS`.

M226 changes one mechanism only: the execution topology of M224's validated
strict-distinct atom.  M224 code hash
`6ABA2D0AB618FF5D678977CC07FC89962C09092B537AAFFC282E069C10DFDA7B` is
the immutable mathematical parent.  The antithetic identity, normalized
factorization, chart, `|rho|<=.08` proof, 16 Phi terms, 32 Simpson panels,
precision, radius, event set, context/outer seeds, and every numerical threshold
remain fixed.

Bias class remains exact in expectation in real arithmetic.  The environment
remains Python 3.14.4, NumPy 2.4.6, and FlopScope 0.10.0.  The component ceiling
is M214's `6,824,272,176`; peak RSS is at most 512 MiB.  No response, truth,
scorer, MSE, challenge weight, leaderboard datum, or variance result may be
used.

## Frozen topology

The kernel constructor runs once for the frozen event count and allocates two
persistent slabs: one float64 slab and one boolean slab.  All ndarray views and
shape metadata are created in setup.  Per invocation:

1. the 20 caller-owned sufficient-statistic columns are bound read-only by
   reference, with no staging allocation or copy;
2. every arithmetic/comparison operation writes to an explicit persistent
   `out` view;
3. alpha and `t` live directly in the combined eight-plane Phi argument slab,
   removing four argument copies;
4. the 16-term Horner seed starts as `c15*y+c14`, removing the zero-and-add
   initialization while preserving the polynomial exactly;
5. the weighted 33-node Simpson reduction is one explicit-out float64 matmul
   on a setup-hoisted `(2N,33)` view, with the same multiply-add bill;
6. the two-sign antithetic reduction is one `add`, and each two-sign maximum is
   one `maximum`; and
7. grid and scalar scratch storage is overwritten only after its mathematical
   lifetime ends.

No custom unmetered ufunc, JIT, hidden native extension, runtime allocation,
runtime reshape, or arithmetic outside FlopScope is permitted.  Setup
allocation is reported separately and peak RSS remains binding.  Returned
output views remain owned by the persistent kernel until its next invocation;
there is no output copy in the timed call.

## Frozen static ledger

For `N` events the persistent setup owns exactly `268N` float64 elements and
`2N` booleans: two `empty` calls and `2,146N` bytes.  At `N=3,968` this is
`8,515,328` bytes.  The timed invocation performs zero `empty`, `copyto`,
`sum`, `max`, or `reshape` calls and allocates zero user bytes.

The timed operation census is exactly 171 calls:

```text
abs 7                 add 37                divide 14
exp 3                 greater 1             greater_equal 2
isfinite 1            less_equal 6          logical_and 9
matmul 1              maximum 6             multiply 76
sqrt 2                subtract 6
```

The predicted bill is `5,467N`: `21,693,056` at the target.  The adjacent
static JSON freezes every operation component.  Before any target trace,
generated size-3 and size-9 probes must match the affine call/bill/allocation
ledger exactly.  A mismatch kills M226; the ledger is not patched from the
observation.

## Frozen native gates

The target remains 31 blocks x 128 events, with context seeds
`221730001..221730031` and outer seeds `221720001..221720005`.  Packed context
construction and persistent workspace construction occur before the measured
invocation.  Five isolated fresh Python processes must each satisfy:

```text
raw wall < 0.016133916999970098 seconds
raw speedup versus M216 > 100x
billed_flops == 21,693,056
billed_flops + 5e11*residual_wall_s <= 6,824,272,176
peak RSS <= 512 MiB
zero fallback, zero chart mismatch, zero resource/finite failures
native value and radius agree with frozen M224 inside M224's radius.
```

Every process is binding; a favorable minimum or median cannot rescue one slow
trace.  Any failure kills this implementation locally while preserving M224's
validated chart and any static topology facts that pass.  M226 does not open
variance under any outcome.
