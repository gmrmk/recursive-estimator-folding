# DGFL-1 source-contract slice

**Status:** `PASS_SOURCE_CONTRACT_SLICE_ONLY`  
**Manifest:** `71BD5DB7B882FFD1632DD9F767C0F9834B997DE2AF87E7466E9EC704CAEA65AC`  
**Source:** `BE3F9B9E664201F8BFDF7F085188317800B5E416EFBAC8AD2C33B82296222556`  
**Tests:** `8E3D543B45DD95268F2DFB7ADD7D27868FD5DB53DE122AB8B58771E224F728DD`

## Outcome

The exact manifest-bound command passed 16 of 16 source-only tests. It used the
pinned WHestBench 0.14.0 / FlopScope 0.10.0 environment, constructed no MLP,
read no truth or scorer, called no provider prediction, and spawned no worker.
The [verbatim transcript](F0_SOURCE_TEST_TRANSCRIPT.txt) has SHA-256
`B4509F60AB32AAF8434034CB5B01584845F0A46C8454ABC02DC0428F13A5A715`.

The slice closes several implementation questions. Both incumbent Q call sites
use instance dispatch, so a descendant can retain the exact first production
object without editing GUARDS. The real pinned QR path repeated byte-for-byte
and billed exactly `45,921,196` units per construction. Invocation-local state
is cleared between worker requests. Healthy, M186, and M187 complete base
returns all pass through one fail-closed state machine that forbids an
uncorrected post-Q return. The fixed 32 positive labels occupy distinct mutually
unbiased frames; their antipodes follow the incumbent positive-bank-then-negative-bank
order. Physical replay rows and the transported skew generator agree with W0's
absorbed-Q row-weight convention.

## Independently recomputed cost floor

Dividing the proposal's `17,146,314,752` tangent-core total by 4,096 rows gives
exactly `4,186,112 = 32 * 256 * 511`, one dense 256-wide matvec per layer. Against
the provisional W0 witness `259,700,821,492`, the necessary variance-reduction
orientations are:

- retained-primal tangent core only: `0.103055%`;
- primal replay plus tangent core: `0.205898%`;
- current closed mixed-precision component subtotal: `0.213908%`;
- current closed float64 component subtotal: `0.420472%`.

These values were recomputed locally from exact integers. They are floors on a
possible break-even condition, not evidence from another agent and not the
final bar: the W0 number is not a worst-case upper, and Pilot A, casts, route,
guards, cleanup, wall, RSS, and Phase-2 rules remain open.

## Boundary and next test

This directory is an inert contract harness, not provider code. Its executable
cost ledger deliberately returns `authorizes_generated_execution = false`.
The official Phase-2 evaluator and resource policy were not released at this
checkpoint, so no provider, multiprocessing, budget, score, or legality claim
is made.

The cheapest signal test that remains within this boundary is a separately
presealed hand-network covariance screen. It can ask whether the six fixed
dipole/Fourier controls explain held rotation variance without using challenge
weights, target truth, a scorer, or provider execution. A pass would establish
only `SCREENED_SYNTHETIC_SIGNAL`; it would not complete F0-S or authorize F1.
