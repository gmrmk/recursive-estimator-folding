# VERDICT - gm_m179_m199 (mining key `m179_exact_background_archive_producer`)

**Status: MEASURED. Gate result: KILL_CONFIRMED.**
M199's `BLOCKED_OVERLAP` stands. The 7.73675016B legacy background row stays
`unproved_replacement_candidate`.

## DEVIATIONS (recorded loudly, at the top)

1. **ARM C was not executed as predeclared.** The predeclaration called for one
   width-256, depth-32 run through the M200 fixture harness. It is not merely
   slow, it is doubly blocked, and both blocks are measured, not asserted:
   (i) `m167.complete_source_reference` - the M200 fixture's reference Source211
   algebra, reached 3x per layer through `m198.issue_m172_source` - is an
   O(n^3)-iteration Python triple loop with O(n^2) work inside. Measured L=4
   stream time rises 0.347 s (width 6) -> 27.160 s (width 28), empirical
   exponent 2.71-3.42, extrapolating past 1e5 s for a single width-256 depth-32
   cell; (ii) the composed path fail-closes at width 256 on **layer 12 of 32**
   (seed rep 0) and **layer 10 of 32** (rep 1), so the trace cannot be defined
   to layer 32 there at any speed. The predeclared fallback was taken: the
   largest sub-checks that fit.
2. **The predeclared ARM B grid (M200's frozen widths 2..7) does not survive
   depth 32.** 8 of those 12 cells fail closed before any trace exists. Scope
   was therefore extended UPWARD in width (10, 14, 24, 32) to obtain
   SPD-admissible depth-32 cells. Every attempted cell is reported, including
   all 8 fail-closed ones. No cell was dropped to make a gate pass.
3. **One diagnostic field was added mid-run** (`reference_state_max_abs_scale`
   and relative parity). It is labelled `_DIAGNOSTIC_NOT_A_GATE`. The
   predeclared absolute 2e-12 gate was NOT changed, and it is reported as
   FAILED where it failed. The four affected cells were re-run from scratch;
   the re-run reproduced the parity numbers bit for bit.
4. `mpmath` is absent from the pinned interpreter. Not needed: no arm of this
   falsifier requires it (M179's G1/G2 mpmath references are already frozen).

## What the original kill measured

M199 returned `BLOCKED_OVERLAP`, not `KILL_COST`. Its stated obstruction was
bookkeeping: "M125b books 32 layers; M179 archives layers 1-31 and omits
terminal mu_32", plus "no identical call/result/lifetime trace exists".

## What was predicted (on record, before any run)

B32 = 8,572,379,136 FLOPs, GATE 0 passes with margin 1.151242496e9; post-
replacement composed total 90.544265216B, headroom 9.455734784B; ARM B and
ARM C pass all gates, with named residual risks in this order: parity
degradation past the absolute 2e-12 gate at depth 32; fail-closed refusal;
wall-clock overrun.

## What was observed

### STEP 0 - the mined cost clause (b): PASS, every predicted digit landed

| quantity | value |
|---|---|
| matmul FLOPs/layer, re-metered live under flopscope 0.10.0 | 134,217,216 (= frozen 2026-08-07 value) |
| per-layer inclusive FLOPs | 267,886,848 (= frozen) |
| B31 (31-layer) | 8,304,492,288 (= ledger `m179_standalone_total` 8.304492288B) |
| **B32 (32-layer inclusive metered bill)** | **8,572,379,136 = 8.572379136B** |
| GATE 0 threshold | 9.723621632B |
| **margin** | **1.151242496B - PASS** |
| T_A post-replacement composed total | 90.544265216B, headroom 9.455734784B |
| T_B (M179 normalized to the legacy 1.25 reserve) | 92.687360000B, headroom 7.312640000B |
| strict no-replacement under conv. B | 100.089251600B (reproduces the ledger exactly) |

All five M199 ledger identities hold in exact rational arithmetic. The 4.76x
headroom expansion the revival claimed is arithmetically real and survives
BOTH reserve conventions - under the 1.25 convention the replacement is what
rescues a strict total that would otherwise sit at 100.0892516B, over the
endpoint.

### ARM B - the mined identity clause (a): PASS wherever the trace exists

10 depth-32 cells completed (widths 5,5,6,7,10,10,14,14,24,32; L = 32 weights
= 31 archived M179 layers + terminal mu_32). In every one of them:

- legacy-call surveillance (independent monkeypatch on
  `build_extended_background`, `build_labelled_carrier_maps`,
  `labelled_inhomogeneous_source_recurrence`): **0, 0, 0 calls** during the
  measured stream;
- event-ledger audit: **0** unexpected operations, **0** legacy-named
  operations, **0** buffers with a surviving lifetime, **0** non-float64
  buffers;
- operation counts exactly (31, 31, 31, 31, 30, 1, 0);
- liveness: all eight retained counters 0, max live named objects <= 5;
- per-layer impulse error **exactly 0.0**;
- `m179.exact_step.post_mean` emitted **32** times, i.e. terminal mu_32 exists;
- **mu_32 is BITWISE identical** (sha256 array digest) to mu_32 from an
  independent `m179_background_producer.zero_order_recurrence` call.

No legacy background call survives with distinct operands, result, dtype or
lifetime. Clause (a) does not falsify.

### The predeclared G3 absolute parity gate: FAILED in 3 of 10 cells

| cell | absolute parity | state magnitude | relative parity |
|---|---|---|---|
| w5 r0 | 1.862645149230957e-09 | 2.30e7 | 8.098e-17 |
| w5 r1 | 4.470348358154297e-08 | 1.15e8 | 3.899e-16 |
| w6 r1 | 5.4569682106375694e-12 | 1.18e4 | 4.614e-16 |
| w7 r0 | 1.8189894035458565e-12 | 9.47e3 | 1.921e-16 |
| w10 r0 | 8.526512829121202e-14 | 2.25e2 | 3.791e-16 |
| w10 r1 | 1.4210854715202004e-14 | 5.88e1 | 2.418e-16 |
| w14 r0 | 4.085620730620576e-13 | 1.38e3 | 2.970e-16 |
| w14 r1 | 5.684341886080802e-14 | 3.50e2 | 1.623e-16 |
| w24 r0 | 3.197442310920451e-14 | 7.26e1 | 4.405e-16 |
| w32 r0 | 8.526512829121202e-14 | 1.34e2 | 6.383e-16 |

Relative parity spans 8.098e-17 to 6.383e-16 across every completed cell -
float64 round-off (eps = 2.220446049250313e-16). The streaming composition is
numerically identical to the full-archive reference at depth 32. M200's 2e-12
gate is absolute and was frozen against a depth 3..6 grid where terminal
magnitudes are O(1); at depth 32 they reach 1.1e8, so the gate no longer means
what it meant. Reported as a literal predeclared failure; deliberately NOT
retuned.

### ARM C - the decisive result: the trace cannot be built at width 256

At the real composition width, the pre-ReLU covariance of the zero-order
recurrence loses positive semidefiniteness well before layer 32:

| seed | first layer with min eig <= 1e-12 | min eig L32 | max abs rho L32 | RHO_MAX violated |
|---|---|---|---|---|
| rep 0 | **12** | -1.068471e-11 | 0.942027049827 | never |
| rep 1 | **10** | -2.303857e-09 | 0.970721387933 | never |

min eig goes negative at layer 13 (rep 0) and layer 12 (rep 1). M198's
`DelayOneContext` refuses this fail-closed ("pre-ReLU covariance is not safely
SPD"), so the M200 streaming fixture - the identity trace M199 named as "the
only lawful child" - terminates at layer 10-12 of 32 at width 256.

Two precise corollaries, both worth carrying into the writeup:

1. **The 32-layer M179 producer itself IS reachable at width 256.** Its own
   guard is per-pair (|rho| <= RHO_MAX = 0.9999999999999998) and is never
   violated; the recurrence completes all 32 layers on both seeds. The extra
   layer costs 0.267886848B exactly as the revival claimed.
2. **M179's fail-closed strata are per-pair, not spectral.** `relu_moments`
   checks diagonal variance and pairwise rho, never the spectrum, so it
   silently ACCEPTS a numerically non-PSD covariance from layer 12-13 onward at
   width 256. The composed path is what catches it. The 31-layer archive was
   never validated for spectral PSD at depth, and that is a gap in our own
   record, not in M199's.

## Verdict logic

Both clauses of the mined cheapest falsifier come back clean: clause (b) passes
with 1.151242496B of margin, clause (a) shows no surviving legacy background
call anywhere the trace can be built. But the predeclared kill conditions
`KILL_PARITY` (G3 exceeded in 3 cells) and `KILL_REACHABILITY` (non-PSD
fail-close at the real width) both fired, and the second one is not a scale
artifact: without an identity trace at width 256 there is no evidence that
converts the 7.73675016B row from `unproved_replacement_candidate` to proved
replacement. M199's fourth denial ground stands, so M199's disposition stands.

The revival was right about the arithmetic and wrong about the reachability.
What killed it is a fact nobody had measured, because this composition had
never been run past depth 6: the zero-order full-covariance recurrence goes
numerically non-PSD at width 256 by layer 12 of 32.

## Non-claims

No estimator, variance, MSE, score, champion, promotion, or submission claim.
Phase-1 selection is untouched. M205's other blocker (a missing physical
K4/K31/K22 provider) is untouched. The remaining M199 denial ground about
numerical/reserve conventions is reported (GATE 0X), not resolved.

## Firewall attestation

Synthetic He-Gaussian weights only. No truth, scorer, holdout, private data,
leaderboard, submission, network, or git. All writes confined to this
directory. Frozen sources imported read-only and never edited. `m245_*`,
`M243`, `M244`, `tasks/`, `journal-m245*` untouched.
