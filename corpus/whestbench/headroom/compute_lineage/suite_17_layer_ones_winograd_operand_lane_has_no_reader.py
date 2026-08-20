"""Suite tier 17: layer 1 makes no Winograd call, so its Winograd operand lane
is charged for an array that nothing in the route ever reads.

Tier 14 stopped billing layer 1 as a Winograd row product and started billing it
as the phased-WHT butterfly the deployed hook actually runs; tier 15 kept that and
put the butterfly on the crowned schedule.  Neither tier touched the OTHER lane
tier 3 had attached to layer 1: the per-layer W-side operand stack, 1,915,152,
which is the depth-6 Winograd B-side transform of ``mlp.weights[0]``.

The incumbent says so itself, in three places, and prices the term for whoever
came next:

    "layer1_weight_side_stack_CHARGED_FOR_AN_UNMADE_CALL": 1,915,152
                                        [suite_16 breakdown key, verbatim]
    "tier 3's stack 1,915,152 charged for a Winograd call this route does not
     make"                              [suite_16 docstring, layer-1 inventory]
    "That is now the largest self-declared placeholder in the file and it is left
     standing for a later tier; it is priced below by
     ``next_rung_layer1_stack_price()`` at 1,915,152."      [suite_16 docstring]

This tier removes it.

    layer 1 total            52,279,568   ->      50,364,416
    suite bill, per net 144,870,660,864   -> 144,868,745,712

    (-1,915,152, or 0.00132% of the whole bill)

ONE SUBSTANTIVE CHANGE
======================
Exactly one term leaves the bill and no term changes value.  Everything else is
carried at the incumbent's figure and asserted term by term in ``_selfcheck``:

  * layer 1's butterfly 50,233,344, its shared prologue 688,128 inside that, its
    weight-side normalization 65,536, its pilot negation 65,536.  Layer 1 keeps
    every lane the deployed route actually performs.
  * layer 2 entire, 2,452,696,336: even-channel row part 2,371,803,840, W-side
    stack 1,915,152 (KEPT -- layer 2 makes the call), and the auxiliary lane
    78,977,344 with tier 16's precompute at 20,420,928 in it.
  * layers 3..32, 30 x 4,745,522,832 = 142,365,684,960, W-side stacks included.
  * the two suite-once fields, 241,309,152 and 64,512, at their exact incumbent
    values and outside ``.total``.
  * the certified per-call floor, 303,096,592 at the anonymous (4096, 256, 256).

THE FROZEN CONSTANT
===================
P1: take the biggest constant the model hard-codes without cause.  After sixteen
tiers the file's own inventory of unbacked charges has exactly one entry with a
number beside it, and this is it.  The constant is frozen for a plain historical
reason: tier 3 established "one W-side stack per layer, not per tile" and applied
it uniformly to all thirty-two layers, at a time when all thirty-two layers were
Winograd row products.  Eleven tiers later layer 1 stopped being one.  The lane
survived the operation that removed its consumer.

This is the same shape as tier 7, which is crowned: a term that two earlier tiers,
composed, had quietly emptied, re-billed at its surviving readers.  Here the count
of surviving readers is zero.

WHAT THE LANE IS, AND WHY NOTHING READS IT
==========================================
``weight_side_stack_cost(t7, 256, 256, 4096)`` is
``t7.best_operand_grade(256, 256, 6)`` -- the graded B-side operand transform that
a depth-6 in-place-leaf Winograd call builds from its right-hand operand before
the batched leaf matmul.  It materializes ``7**6 = 117,649`` blocks of 4 x 4, an
object of 1,882,384 f32.  Its only possible consumer is the leaf matmul of a
depth-6 Winograd call on that operand.

Layer 1 issues no such call.  The deployed first product is

    frames = phases[:, :, None] * weight[None, :, :]        # seed
    for eight radix-2 stages:  left, right = left+right, left-right
    output *= MEAN_CHI_256 / 16.0                           # scale
                            [kerdock_v3_estimator.py:132-145, ``_first_sample_matmul``]

and the three arrays it derives from ``mlp.weights[0]`` are the phase-signed seed,
the level-1 and level-2 shared arrays of tiers 12 and 13, and the normalization --
each of which IS billed here, at 49,545,216, 688,128 and 65,536 respectively.  The
Winograd B-stack is not among them and no later term reads it either: the odd
channel's precompute needs ``W0`` as an A-SIDE operand at depth 5, a different map
at a different depth, and pays for it separately at 1,092,032 inside tier 16's
20,420,928.  ``_selfcheck`` executes the layer-1 route from ``(phases, W0)`` alone
and reproduces the design row product exactly, which is the operational form of
"nothing else is read".

EXACTNESS IDENTITY
==================
Nothing about what is computed changes; a charge for an unbuilt array is dropped.
The identity the whole layer-1 lane rests on is tiers 14/15's, restated and
EXECUTED here rather than inherited on trust.  Write ``H`` for the normalized
Walsh matrix the deployed setup builds [kerdock_v3_estimator.py:24-38, :89],
``d_s`` in ``{-1, +1}**256`` for frame ``s``'s phase vector, and ``W0`` for the
Haar-absorbed first weight [kerdock_v3_estimator.py:162-172].  The design's base
half is the 126 stacked blocks ``D_s = H diag(d_s)``, and layer 1's preactivation
is

    P_s = D_s W0 = (H diag(d_s)) W0 = H (d_s * W0)                          (1)

The right-hand form is the butterfly: form ``d_s * W0`` by one signed elementwise
pass, then apply ``H`` by eight radix-2 add/subtract stages over the row axis.
Over the integers the two sides of (1) are equal entry for entry, and that is
EXECUTED below at widths 4, 8 and 16 over several frames, against a dense ``_mm``
of the explicitly formed ``H diag(d_s)``.  The scale ``c = MEAN_CHI_256/16`` is
carried on the 256 x 256 matrix by tier 10 and the identity ``H (d * (c W0)) =
c * H (d * W0)`` is executed too.

Layer 2's route is unchanged and re-executed for the same reason: with
``p = D W0``, ``t = relu(p) W1`` and ``o = p (W0 W1)``-side algebra,

    relu(-p) W1 = (relu(p) - p) W1 = t - o                                  (2)

is executed entry for entry, so the term this tier removes sits inside a route
that still computes what the champion computes.

Three claims, all run rather than asserted:

(I)   THE LAYER-1 ROUTE IS THE BUTTERFLY AND IT READS ONLY ``(phases, W0)``.  The
      route function below takes exactly those two arguments, calls no transform,
      and reproduces ``D_s W0`` at three widths.
(II)  THE REMOVED NUMBER IS THE MODULE'S OWN, NOT THIS TIER'S.  It is read back
      from ``t7.best_operand_grade(256, 256, 6)`` and asserted equal to the
      incumbent's published 1,915,152 and to the whole delta.
(III) EVERYTHING ELSE IS THE INCUMBENT'S, term by term, including the whole of
      layer 2 and the whole of layers 3..32.

DISJOINTNESS, SO NOTHING IS DEDUCTED TWICE
==========================================
  * From tier 3.  Tier 3's rule -- one W-side stack per LAYER rather than per tile
    -- is not weakened.  It still applies at all thirty-one layers that make a
    Winograd call, and the per-layer count is asserted to be 31, not 32, with the
    31 x 1,915,152 = 59,369,712 still in the bill.  This tier removes a stack from
    a layer, not a stack from a tile.
  * From tiers 14 and 15.  They changed WHAT layer 1 computes and how the
    butterfly is scheduled.  Every number they produced is carried unchanged:
    50,233,344, 688,128, 65,536, and tier 14's declined transcription 115,605,504.
    This tier changes only which lanes accompany them.
  * From tier 7.  Its 65,536 pilot negation is a different term with a live reader
    (``x[n_base : n_base + pilot_base]`` [fold3_estimator.py:105-110]); it is kept
    and asserted at PILOT_BASE x WIDTH.
  * From tier 5.  Its design-side A stack, 241,309,152, is orphaned by the
    IDENTICAL argument -- it too is a lane of the Winograd call tier 14 deleted --
    but it lives in ``suite_once``, outside ``.total``, so removing it cannot move
    the fitness in either direction.  It is therefore left at its exact incumbent
    value so that exactly one term in the bill moves (LAW 5).  This is stated
    rather than hidden, and ``_selfcheck`` asserts the field is unchanged and that
    ``.total`` never contained it.
  * From tier 16.  The precompute stays at 20,420,928 with all four of its lanes,
    including its own A-side stack of ``W0`` at depth 5, 1,092,032 -- which is why
    the removed depth-6 B-side stack is not the same object under another name.
    Asserted: the two are different function calls with different arguments and
    different values.
  * From the call ladder (tiers 8-10 of the prior ladder).  No within-call schedule
    is touched.  The per-call floor is re-derived from tier 7 and asserted at
    303,096,592.  This tier removes a lane of a call that is not issued; it does
    not reweight a lane of a call that is.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * The suite-once design stack, 241,309,152, is orphaned by the same argument and
    is NOT removed.  It is 126 times the size of what this tier claims.
  * The precompute is left at depth 5 and pays its own W-side stack at 1,092,032,
    although the depth-6 route would share layer 2's stack; that is priced below at
    18,823,840 and left for a later tier (see NEXT RUNG).
  * Layer 1 keeps the whole butterfly, the whole prologue, the normalization and
    the negation.  Nothing about the work layer 1 does is re-scheduled.
  * The thirty generic layers keep the antipodal half at full price; the ledger-free
    ReLU writes stay priced at zero; the terminal fold stays unmodelled.  All three
    are counted below and none is claimed.
  * ``.total`` remains the marginal per-net bill; no suite size is assumed.

THE NEXT RUNG, PRICED AND LEFT STANDING
=======================================
The precompute is ``W0 @ W1h`` with ``W1h = mlp.weights[1]`` -- the same matrix
layer 2 uses as the right-hand operand of its even-channel product, on the same
side.  At depth 5 the two B-side gradings are different objects.  At depth 6 they
are the SAME object: ``best_operand_grade(256, 256, 6)``, the 1,915,152 layer 2
already pays.  Depth 6 costs 20,738,992 standalone, but 18,823,840 with that lane
already on the ledger -- 1,597,088 below the 20,420,928 carried here.  It is
computed below by ``next_rung_precompute_at_depth_six()`` and printed beside the
claim.  It is NOT taken: it is a waiver, LAW 5 allows one change, and a waiver is
the construction tier 6 was rejected for -- it deserves its own adjudication with
its own side-and-depth proof, not a free ride on this one.

DOORS THAT STAY CLOSED
======================
Two are NEW, probed by this tier's own search and closed with arithmetic; the rest
are re-executed from the incumbent so the next tier does not pay for them twice.

  * NEW -- DOES THE ORPHAN ARGUMENT REACH ANY OTHER W-SIDE STACK?  No, and the
    boundary is exact.  A W-side stack is orphaned exactly when its layer issues no
    Winograd call.  Thirty-one layers do issue one: layers 3..32 through
    ``self._winograd.multiply`` [fold3_estimator.py:117-122 via
    kerdock_v3_estimator.py:147-149], and layer 2's even channel through the same
    call on 32,256 rows.  For each of them the stack is a LANE of a bill the file
    already pays: ``row_part_full + w_stack == 303,096,592`` exactly, so deleting
    it would leave the call underpaid rather than unread.  Executed below.  SHUT at
    31 layers; open at exactly one, which is the one this tier takes.
  * NEW -- IS THE LAYER-1 SHARED PROLOGUE SUITE-ONCE, LIKE THE FRAME DESCRIPTORS?
    Tier 5's licence is "an operand built from the DESIGN is built once for the
    suite".  The frame descriptor tables qualify: they are index tables over
    ``(frames, rows)`` and carry no weight.  The 688,128 prologue does not: its
    level-1 arrays are the pairwise sums and differences of the ROWS OF ``W0``, and
    ``W0`` is ``rotation.T @ mlp.weights[0]``, per net.  Executed below: two nets
    differing in one entry of ``mlp.weights[0]`` produce different level-1 arrays.
    SHUT; the prologue stays inside ``.total`` at 688,128.
  * CARRIED -- THE WINOGRAD DEPTH UNDER TIER 3's AMORTIZED OBJECTIVE.  Depth 6
    minimises both ``row(L)`` and ``15.75 * row(L) + stack(L)``; brute-forced below
    over every lawful depth.  SHUT.
  * CARRIED -- THE 15.75 TILE FRACTION.  The row lane is exactly linear in ``m``:
    ``4 * row(3072) == 3 * row(4096)`` and ``8 * row(3584) == 7 * row(4096)``,
    executed to the FLOP.  SHUT.
  * CARRIED -- THE TERMINAL FOLD.  Modelling layers 30..32 honestly RAISES the
    bill, to at most twice the incumbent's 196,608 of width work.  Both bounds
    executed.
  * CARRIED -- PRUNING.  ``active`` is a function of the net's own weights and its
    worst case is the full 256 [fold3_estimator.py:102-132].
  * CARRIED -- BUTTERFLY CREDIT AT LAYERS 2..32.  The butterfly exists because
    every entry of a design row has the same absolute value; ``relu(p)`` does not,
    and ``_selfcheck`` exhibits two entries of it with different absolute values.
  * CARRIED -- THE LEDGER-FREE ReLU WRITES, 478,937,088, priced at zero at all 32
    layers; re-billing them consistently would RAISE the bill.  Counted, not
    claimed.

f32 STATUS: NO ARITHMETIC AT ALL IS ADDED, REMOVED OR REORDERED.  NO FLAG.
==========================================================================
This tier is the rare one that cannot perturb a single floating-point value.  It
does not change a route, a depth, a schedule, an association order or an operand.
It deletes a charge for an array that the route never allocates, so the outputs of
the removed-charge route and the incumbent route are bit-identical by construction
-- the same program, billed once instead of once plus a phantom.  No value is
approximated, no rank is reduced, no summation is reordered, no term any operation
reads is dropped.  No f32 repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
The V5-d3 law asks whether a metered win is repaid in residual wall time.  Here
the meter and the clock move in the SAME direction, because the win is a deletion
rather than a re-route, and every quantity below moves down.

  * NO NEW KERNEL, NO NEW PASS, NO NEW DISPATCH.  The implementation shape of this
    tier is the empty diff: the deployed ``_first_sample_matmul`` never built a
    Winograd operand stack, so the code that runs before and after this tier is the
    same code.  There is nothing to batch or inline because nothing is added.
  * LAUNCH COUNT FALLS BY SIX, NOT RISES.  A depth-6 graded operand transform is
    six successive passes over the growing block stack; none of them is issued at
    layer 1 and the bill now agrees.  Against tier 16, which honestly reported a
    rise of fifteen launches, this tier reports a fall of six.
  * PEAK RESIDENCY FALLS BY 7.53 MB.  The unbuilt stack is ``7**6`` blocks of
    4 x 4 f32 = 1,882,384 elements.  It would have had to be live across the
    layer-1 butterfly, whose own working set is one 126 x 128 x 256 scratch
    [kerdock_v3_estimator.py:90-93] beside the 66 MB ``self._activation``.
  * GRANULARITY IS UNCHANGED.  No block shape anywhere in the schedule moves; the
    coarsest and finest kernels in the process are the ones tier 16 named.
  * FLAT IN THE SUITE SIZE.  One net or a thousand, each pays 1,915,152 less; no
    one-time field moves, and the suite-once total is asserted identical to the
    incumbent's 241,373,664.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass

_T7_PATH = "corpus/whestbench/headroom/compute_lineage/tier_07_inplace_verbatim_leaves.py"

# Production shape, observed in kerdock_v3_estimator.py and fold3_estimator.py.
FRAMES = 126                      # phase_stop - phase_start = 128 - 2
WIDTH = 256                       # ctx.width
BASE_ROWS = FRAMES * WIDTH        # n_base = 126 * 256 = 32,256
DESIGN_ROWS = 2 * BASE_ROWS       # antipodally doubled = 64,512
LAYERS = 32
TILE_ROWS = 4096                  # BLOCK_ROWS in row_blocked_winograd.py
PILOT_BASE = 256                  # base_estimator.py:53

# The deployed sample loop is ``for layer in range(1, mlp.depth - 3)``.
LOOP_RELU_PASSES = LAYERS - 4
LAYER1_RELU_PASSES = 2

# FlopScope v0.10 butterfly convention, split into its parts.
_BUTTERFLY_SEED = 1                       # whole-block signed write, per frame
_BUTTERFLY_FINAL_SCALE = 1                # whole-block; MEAN_CHI_256 / 16
_STAGE_HALVES_SCRATCH = 3                 # copyto + add + subtract   (deployed)
_STAGE_HALVES_PINGPONG = 2                # add + subtract            (tier 11)

# Tier 12's shared level-1 arrays and tier 13's shared level-2 alphabet.
_LEVEL1_OPS_PER_PAIR = 5
_LEVEL2_ARRAYS_PER_GROUP = 32
_SHARED_DEPTH = 2                         # tier 13 proved depth 3 loses

# Per-element receipts, kept apart so the chains in the docstring are executable.
_BUTTERFLY_PER_ELEMENT_DEPLOYED = 14      # tier 14's transcription
_BUTTERFLY_FRAME_ELEMENT_FOLDED = 6       # surviving per-frame stages, tier 13

# Suite tier 6, REJECTED: the depth-5 call with BOTH operand lanes waived.
_TIER6_REJECTED_PRECOMPUTE = 18236864

# Tier 16's published figures, carried so every one of them can be re-asserted.
_INCUMBENT_TOTAL = 144870660864
_INCUMBENT_LAYER1_TOTAL = 52279568
_INCUMBENT_LAYER2_TOTAL = 2452696336
_INCUMBENT_GENERIC_TOTAL = 142365684960
_INCUMBENT_SUITE_ONCE = 241373664

# The number of layers that DO issue a Winograd call: 2..32 inclusive.
_WINOGRAD_CALLING_LAYERS = LAYERS - 1


def _t7():
    spec = importlib.util.spec_from_file_location("t17base", _T7_PATH)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def direct_cost(m: int, k: int, n: int) -> int:
    """The source's own COUNTERFACTUAL price, cost_model.py:8-11."""
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


def _log2_exact(n: int) -> int:
    if n < 1 or n & (n - 1):
        raise ValueError(f"{n} is not a power of two")
    return n.bit_length() - 1


def _selected_levels(strategy: str) -> int:
    """Depth the tier-7 sweep chose, read off its own strategy string."""
    head, _, _rest = strategy.partition("_inplaceleaf")
    tag = head.rsplit("_", 1)[-1]
    if not tag.startswith("l") or not tag[1:].isdigit():
        raise ValueError(f"cannot read a Winograd depth from {strategy!r}")
    return int(tag[1:])


# ---------------------------------------------------------------------------
# THE ONE CHANGE: a W-side operand lane belongs to a layer only if that layer
# issues the Winograd call whose leaf matmul consumes it.  Layer 1 does not.
# ---------------------------------------------------------------------------


def weight_side_stack_cost(t7, k: int = WIDTH, n: int = WIDTH,
                           m: int = TILE_ROWS) -> int:
    """The m-independent lane of the crowned call bill: the W-side (k, n) stack.

    Tier 3's term.  It is a lane of ``inplace_verbatim_leaves_candidate_bill``:
    the graded B-side transform the depth-6 route builds before its leaf matmul.
    Charged once per layer that ISSUES that call.
    """
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    levels = _selected_levels(bill.strategy)
    cost, _grade = t7.best_operand_grade(k, n, levels)
    return cost


def layer1_weight_side_stack_declined(t7) -> int:
    """The charge this tier removes: layer 1's W-side stack, which has no reader.

    Layer 1's product is the phased-WHT butterfly
    [kerdock_v3_estimator.py:116-145].  It issues no Winograd call, so the depth-6
    B-side operand transform of ``mlp.weights[0]`` is never built and nothing ever
    reads it.  The value is the module's own, kept computable so the delta is
    checkable rather than asserted.
    """
    return weight_side_stack_cost(t7, WIDTH, WIDTH, TILE_ROWS)


def layer1_weight_derived_arrays(t7) -> dict:
    """Every array layer 1 derives from ``W0``, and what each is billed.

    The census that makes "nothing reads the stack" operational: three arrays are
    built and all three are paid; the fourth is the one being removed.
    """
    return {
        "phase_signed_seed_and_stages_PAID":
            _BUTTERFLY_FRAME_ELEMENT_FOLDED * BASE_ROWS * WIDTH,
        "shared_level1_and_level2_arrays_PAID":
            shared_prologue_cost(_SHARED_DEPTH, WIDTH, WIDTH),
        "weight_side_normalization_PAID": normalization_cost(WIDTH, WIDTH),
        "winograd_B_side_depth6_stack_NO_READER":
            layer1_weight_side_stack_declined(t7),
    }


# ---------------------------------------------------------------------------
# Carried machinery.  Every function below is the incumbent's, unchanged, so the
# terms it produces can be asserted equal to tier 16's term by term.
# ---------------------------------------------------------------------------


def precompute_lanes(t7, k: int = WIDTH, n: int = WIDTH,
                     m: int = WIDTH) -> dict:
    """Tier 16's four lanes for ``cM = c * (W0 @ W1h)``, each paid in full."""
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    levels = _selected_levels(bill.strategy)
    block = 1 << levels
    if m % block or k % block or n % block:
        raise ValueError("the precompute's shape does not carry the chosen depth")
    leaves = 7 ** levels * t7.direct_cost(m // block, k // block, n // block)
    left, _ = t7.best_operand_grade(m, k, levels)
    right, _ = t7.best_operand_grade(k, n, levels)
    decode, _ = t7.best_decode_grade(m, n, levels)
    lanes = {
        "levels": levels,
        "leaves": leaves,
        "left_operand_stack": left,
        "right_operand_stack": right,
        "decode": decode,
        "total": leaves + left + right + decode,
    }
    if lanes["total"] != bill.total:
        raise ValueError("the re-derived lanes do not sum to the module's bill")
    return lanes


def precompute_cost(t7, k: int = WIDTH, n: int = WIDTH, m: int = WIDTH) -> int:
    """cM's price under tier 16's rule: tier 7's call bill at its shape."""
    return precompute_lanes(t7, k, n, m)["total"]


def declined_direct_precompute_cost(k: int = WIDTH, n: int = WIDTH,
                                    m: int = WIDTH) -> int:
    """Tier 15's charge: the cost model's named counterfactual."""
    return direct_cost(m, k, n)


def deployed_operator_precompute_cost(t7, k: int = WIDTH, n: int = WIDTH,
                                      m: int = WIDTH) -> int:
    """The published fallback: the DEPLOYED operator's own one-level bill."""
    return t7.owned_batched_candidate_bill(m, k, n).total


def next_rung_precompute_at_depth_six(t7) -> int:
    """The next rung, priced and NOT taken.

    At depth 6 the precompute's right-hand operand grading is literally the array
    layer 2 already builds for ``W1``: same matrix, same side, same depth.  The
    remaining lanes cost 18,823,840, below the 20,420,928 carried here.  Left for
    its own tier because it is a waiver, and waivers get adjudicated alone.
    """
    levels = 6
    leaves = 7 ** levels * t7.direct_cost(
        WIDTH >> levels, WIDTH >> levels, WIDTH >> levels)
    left, _ = t7.best_operand_grade(WIDTH, WIDTH, levels)
    decode, _ = t7.best_decode_grade(WIDTH, WIDTH, levels)
    return leaves + left + decode


def shared_prologue_cost(depth: int, rows: int = WIDTH,
                         out_width: int = WIDTH) -> int:
    """Tier 12 + tier 13's frame-independent arrays, for ONE butterfly."""
    if depth not in (1, 2):
        raise ValueError("this schedule shares stage 1 or stages 1 and 2")
    if rows <= 0 or out_width <= 0:
        raise ValueError("a shared prologue needs positive dimensions")
    if rows % (1 << depth):
        raise ValueError(f"{rows} rows do not group evenly at depth {depth}")
    cost = _LEVEL1_OPS_PER_PAIR * (rows // 2) * out_width
    if depth >= 2:
        cost += _LEVEL2_ARRAYS_PER_GROUP * (rows // 4) * out_width
    return cost


def butterfly_ops(frames: int, rows: int, out_width: int, *,
                  final_scale: bool, pingpong: bool,
                  shared_depth: int = 0) -> int:
    """Ops a phased-WHT butterfly over ``frames`` frames costs.

    Tier 2's shape [suite_02:277-289], carried verbatim through tiers 14, 15 and
    16 and unchanged here so the four files' numbers are directly comparable.
    """
    if min(frames, rows, out_width) <= 0:
        raise ValueError("butterfly dimensions must be positive")
    elements = rows * out_width
    if elements % 2:
        raise ValueError("half-block passes need an even element count")
    stages = _log2_exact(rows)
    if shared_depth:
        if not pingpong:
            raise ValueError("the shared prologue is defined on the ping-pong body")
        depth = min(shared_depth, stages)
        remaining = stages - depth
        materialize = elements if remaining == 0 else 0
        whole = (_BUTTERFLY_FINAL_SCALE if final_scale else 0) * elements
        per_frame = (remaining * _STAGE_HALVES_PINGPONG * (elements // 2)
                     + materialize + whole)
        return (frames * per_frame
                + shared_prologue_cost(depth, rows, out_width))
    settle = 1 if (pingpong and stages % 2) else 0
    whole = _BUTTERFLY_SEED + (_BUTTERFLY_FINAL_SCALE if final_scale else 0) + settle
    halves = _STAGE_HALVES_PINGPONG if pingpong else _STAGE_HALVES_SCRATCH
    return frames * (whole * elements + stages * halves * (elements // 2))


def normalization_cost(k: int = WIDTH, n: int = WIDTH) -> int:
    """Tier 10's term: the design's scalar folded onto a (k, n) weight matrix."""
    if min(k, n) <= 0:
        raise ValueError("the normalized matrix has positive dimensions")
    return k * n


def deployed_first_product_cost(frames: int = FRAMES, rows: int = WIDTH,
                                out_width: int = WIDTH) -> int:
    """Tier 14's layer-1 price: the deployed hook's literal op sequence."""
    return butterfly_ops(frames, rows, out_width,
                         final_scale=True, pingpong=False)


def crowned_first_product_cost(frames: int = FRAMES, rows: int = WIDTH,
                               out_width: int = WIDTH) -> int:
    """Tier 15's layer-1 lane: tiers 10..13's crowned butterfly schedule."""
    return (butterfly_ops(frames, rows, out_width, final_scale=False,
                          pingpong=True, shared_depth=_SHARED_DEPTH)
            + normalization_cost(rows, out_width))


def frame_descriptor_table_cost(frames: int = FRAMES, rows: int = WIDTH,
                                tables: int = 2) -> int:
    """One index table per butterfly.  Charged twice though one would serve."""
    if min(frames, rows, tables) <= 0:
        raise ValueError("the descriptor tables have positive dimensions")
    return tables * frames * rows


def design_side_stack_cost(t7, m: int, k: int = WIDTH) -> int:
    """Tier 5's A-side (m, k) operand lane, kept as a published one-time field.

    Orphaned by this tier's own argument and deliberately NOT removed: it sits
    outside ``.total`` and cannot move the fitness, so removing it would be a
    second change for no gain.
    """
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, WIDTH)
    levels = _selected_levels(bill.strategy)
    cost, _grade = t7.best_operand_grade(m, k, levels)
    return cost


def antipodal_negation_cost(read_rows: int = PILOT_BASE,
                            width: int = WIDTH) -> int:
    """Tier 7's layer-1 term: the antipodal activations that are READ."""
    if read_rows < 0 or width <= 0:
        raise ValueError("row and width counts must be non-negative and positive")
    return read_rows * width


def deployed_relu_writes_priced_zero(width: int = WIDTH) -> int:
    """ReLU element-writes the deployed route performs and the ledger bills at 0."""
    return (LAYER1_RELU_PASSES * BASE_ROWS * width
            + LOOP_RELU_PASSES * DESIGN_ROWS * width)


def terminal_fold_bounds() -> tuple:
    """Layers 30..32: the incumbent's width work, and the honest upper bound."""
    incumbent = 3 * WIDTH * WIDTH
    worst = 0
    for b in (0, WIDTH):
        for c in (0, WIDTH):
            for d in (0, WIDTH):
                worst = max(worst, WIDTH * b + (WIDTH + b) * c
                            + (WIDTH + b + c) * d)
    return incumbent, worst


@dataclass(frozen=True)
class SuiteBill:
    strategy: str
    call_total: int
    weight_stack: int
    weight_stack_layers: int
    row_part_full: int
    row_part_tail: int
    layers: int
    layer1_butterfly: int
    layer1_normalization: int
    layer1_shared_prologue: int
    layer1_frame_element_price: int
    layer1_lane: int
    layer1_deployed_butterfly_declined: int
    layer1_winograd_row_part_declined: int
    layer1_weight_stack_declined: int
    layer1_negation: int
    layer1_negation_rows: int
    layer1_total: int
    generic_layer: int
    generic_layers_total: int
    layer2_even_rows: int
    layer2_relu_pass: int
    layer2_relu_writes_priced_zero: int
    layer2_precompute: int
    layer2_precompute_levels: int
    layer2_precompute_leaves: int
    layer2_precompute_left_stack: int
    layer2_precompute_right_stack: int
    layer2_precompute_decode: int
    layer2_precompute_direct_declined: int
    layer2_precompute_depth6_next_rung: int
    layer2_odd_normalization: int
    layer2_odd_level1_arrays: int
    layer2_odd_level2_arrays: int
    layer2_odd_shared_prologue: int
    layer2_odd_frame_element_price: int
    layer2_odd_butterfly: int
    layer2_antipodal_write: int
    layer2_aux: int
    layer2_total: int
    suite_once_design_stack: int
    suite_once_frame_descriptors: int
    suite_once: int
    total: int

    def suite_total(self, n_nets: int) -> int:
        """Exact suite bill for ``n_nets`` nets.  No rounding anywhere."""
        if n_nets < 1:
            raise ValueError("a suite has at least one net")
        return n_nets * self.total + self.suite_once

    def amortized_numerator(self, n_nets: int) -> tuple:
        """Per-net mean as an exact fraction ``(numerator, denominator)``."""
        return self.suite_total(n_nets), n_nets

    def breakdown(self) -> dict:
        return {
            "weight_side_stack_per_CALLING_layer": self.weight_stack,
            "weight_side_stacks_CHARGED_layers_2_to_32":
                self.weight_stack_layers * self.weight_stack,
            "row_part_per_full_tile": self.row_part_full,
            "layer1_crowned_butterfly_32256_rows": self.layer1_butterfly,
            "layer1_shared_prologue_of_W0": self.layer1_shared_prologue,
            "layer1_normalization_WEIGHT_SIDE": self.layer1_normalization,
            "layer1_butterfly_lane_total": self.layer1_lane,
            "layer1_deployed_transcription_DECLINED":
                self.layer1_deployed_butterfly_declined,
            "layer1_winograd_row_part_DECLINED":
                self.layer1_winograd_row_part_declined,
            "layer1_weight_side_stack_REMOVED_NO_READER":
                self.layer1_weight_stack_declined,
            "layer1_antipodal_negation": self.layer1_negation,
            "layer1_total_per_net": self.layer1_total,
            "generic_layer_total": self.generic_layer,
            "generic_layers_3_to_32": self.generic_layers_total,
            "layer2_top_channel_row_part_32256": self.layer2_even_rows,
            "layer2_weight_side_stack_KEPT_THE_CALL_IS_MADE": self.weight_stack,
            "layer2_relu_pass_CHARGED": self.layer2_relu_pass,
            "layer2_relu_write_PRICED_ZERO_by_the_ledger":
                self.layer2_relu_writes_priced_zero,
            "layer2_precompute_DEPTH": self.layer2_precompute_levels,
            "layer2_precompute_lane_leaves": self.layer2_precompute_leaves,
            "layer2_precompute_lane_A_side_stack_of_W0":
                self.layer2_precompute_left_stack,
            "layer2_precompute_lane_W_side_stack":
                self.layer2_precompute_right_stack,
            "layer2_precompute_lane_decode": self.layer2_precompute_decode,
            "layer2_precompute_W0_W1h": self.layer2_precompute,
            "layer2_precompute_DIRECT_COUNTERFACTUAL_DECLINED":
                self.layer2_precompute_direct_declined,
            "layer2_precompute_DEPTH6_NEXT_RUNG_not_taken":
                self.layer2_precompute_depth6_next_rung,
            "layer2_odd_normalization_WEIGHT_SIDE":
                self.layer2_odd_normalization,
            "layer2_odd_SHARED_level1_five_per_pair":
                self.layer2_odd_level1_arrays,
            "layer2_odd_SHARED_level2_thirtytwo_per_group":
                self.layer2_odd_level2_arrays,
            "layer2_odd_shared_prologue_total":
                self.layer2_odd_shared_prologue,
            "layer2_odd_channel_butterfly": self.layer2_odd_butterfly,
            "layer2_antipodal_write_32256": self.layer2_antipodal_write,
            "layer2_auxiliary_terms": self.layer2_aux,
            "layer2_total": self.layer2_total,
            "design_side_stack_ORPHANED_TOO_but_OUTSIDE_total_and_KEPT":
                self.suite_once_design_stack,
            "frame_descriptor_tables_TWO_charged_ONCE_to_the_suite":
                self.suite_once_frame_descriptors,
            "total": self.total,
        }


def _layer2_auxiliary_terms(t7) -> tuple:
    """Layer 2's non-matmul terms.  Tier 16's, carried unchanged."""
    precompute = precompute_cost(t7, WIDTH, WIDTH, WIDTH)             # 20,420,928
    normalization = normalization_cost(WIDTH, WIDTH)                  #     65,536
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                              pingpong=True, shared_depth=_SHARED_DEPTH)
    antipodal_write = BASE_ROWS * WIDTH                               #  8,257,536
    return precompute, normalization, butterfly, antipodal_write


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill: a W-side operand lane is charged only to a
    layer that issues the Winograd call whose leaf matmul reads it."""
    t7 = _t7()
    bill_full = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    bill_tail = t7.inplace_verbatim_leaves_candidate_bill(
        BASE_ROWS % TILE_ROWS, k, n
    )
    if bill_full.core_k != bill_tail.core_k or bill_full.core_n != bill_tail.core_n:
        raise ValueError("full and tail calls do not share a right-hand stack")
    if _selected_levels(bill_full.strategy) != _selected_levels(bill_tail.strategy):
        raise ValueError("full and tail calls sit at different Winograd depths")

    call = bill_full.total
    w_stack = weight_side_stack_cost(t7, k, n, m)
    row_full = call - w_stack
    row_tail = bill_tail.total - w_stack
    if row_full + w_stack != call:
        raise ValueError("the W-side stack is not a lane of the call bill")

    # --- generic layers 3..32: tier 3's layer, carried verbatim ---------------
    generic_rows = int(row_full * DESIGN_ROWS // m)
    if generic_rows * m != row_full * DESIGN_ROWS:
        raise ValueError("tile count is not exact; refusing a rounded bill")
    generic_layer = generic_rows + w_stack
    generic_total = (LAYERS - 2) * generic_layer

    # --- the Winograd row lane, computed so it can be DECLINED (tier 14) ------
    full_tiles, remainder = divmod(BASE_ROWS, TILE_ROWS)
    if remainder == 0:
        raise ValueError("base row count is not the frozen 7 x 4096 + tail")
    base_rows_part = full_tiles * row_full + row_tail
    design_stack = (full_tiles * design_side_stack_cost(t7, TILE_ROWS, k)
                    + design_side_stack_cost(t7, remainder, k))
    if design_stack != design_side_stack_cost(t7, BASE_ROWS, k):
        raise ValueError("the design-side lane is not additive over the tiling")
    if design_stack >= base_rows_part:
        raise ValueError("the design-side lane cannot exceed the row part")
    declined_row_part = base_rows_part - design_stack

    # --- layer 1: THE ONE CHANGE.  The butterfly lane is tier 15's entire, and
    #     the Winograd W-side lane that accompanied it is removed because the
    #     call whose leaf matmul would read it is never issued. ----------------
    if PILOT_BASE > BASE_ROWS:
        raise ValueError("the pilot cannot read more rows than the half has")
    declined_deployed = deployed_first_product_cost(FRAMES, WIDTH, WIDTH)
    if declined_deployed != _BUTTERFLY_PER_ELEMENT_DEPLOYED * BASE_ROWS * WIDTH:
        raise ValueError("tier 14's transcription is not at its certified 14/element")
    layer1_butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                                     pingpong=True, shared_depth=_SHARED_DEPTH)
    layer1_prologue = shared_prologue_cost(_SHARED_DEPTH, WIDTH, WIDTH)
    layer1_normalization = normalization_cost(WIDTH, WIDTH)
    layer1_lane = layer1_butterfly + layer1_normalization
    if layer1_lane != crowned_first_product_cost(FRAMES, WIDTH, WIDTH):
        raise ValueError("the layer-1 lane is not tier 15's crowned schedule price")
    if layer1_butterfly - layer1_prologue != (
            _BUTTERFLY_FRAME_ELEMENT_FOLDED * BASE_ROWS * WIDTH):
        raise ValueError("the surviving layer-1 stages are not one pass each")
    negation = antipodal_negation_cost(PILOT_BASE, WIDTH)
    orphan = layer1_weight_side_stack_declined(t7)
    if orphan != w_stack:
        raise ValueError("the removed lane is not tier 3's per-layer stack")
    layer1 = layer1_lane + negation

    # --- layer 2: tier 16's, carried verbatim.  Its stack is KEPT. ------------
    layer2_even_rows = base_rows_part
    lanes = precompute_lanes(t7, WIDTH, WIDTH, WIDTH)
    precompute, normalization, butterfly, antipodal_write = (
        _layer2_auxiliary_terms(t7)
    )
    declined_direct = declined_direct_precompute_cost(WIDTH, WIDTH, WIDTH)
    if precompute >= declined_direct:
        raise ValueError("tier 16's rule must still beat the counterfactual")
    if precompute <= _TIER6_REJECTED_PRECOMPUTE:
        raise ValueError("the carried precompute must exceed the rejected tier 6")
    level1 = shared_prologue_cost(1, WIDTH, WIDTH)
    prologue = shared_prologue_cost(_SHARED_DEPTH, WIDTH, WIDTH)
    level2 = prologue - level1
    frame_part = butterfly - prologue
    if frame_part != _BUTTERFLY_FRAME_ELEMENT_FOLDED * BASE_ROWS * WIDTH:
        raise ValueError("the surviving layer-2 stages are not one pass each")
    if level2 != _LEVEL2_ARRAYS_PER_GROUP * (WIDTH // 4) * WIDTH:
        raise ValueError("the level-2 alphabet is not 32 arrays per group of 4")
    if butterfly != layer1_butterfly:
        raise ValueError("the two butterflies must cost the same at the same shape")
    relu_charged = 0
    relu_free = BASE_ROWS * WIDTH
    layer2_aux = (relu_charged + precompute + normalization
                  + butterfly + antipodal_write)
    layer2 = layer2_even_rows + w_stack + layer2_aux

    descriptors = frame_descriptor_table_cost(FRAMES, WIDTH, 2)

    return SuiteBill(
        strategy="layer_ones_winograd_operand_lane_has_no_reader",
        call_total=call,
        weight_stack=w_stack,
        weight_stack_layers=_WINOGRAD_CALLING_LAYERS,
        row_part_full=row_full,
        row_part_tail=row_tail,
        layers=LAYERS,
        layer1_butterfly=layer1_butterfly,
        layer1_normalization=layer1_normalization,
        layer1_shared_prologue=layer1_prologue,
        layer1_frame_element_price=_BUTTERFLY_FRAME_ELEMENT_FOLDED,
        layer1_lane=layer1_lane,
        layer1_deployed_butterfly_declined=declined_deployed,
        layer1_winograd_row_part_declined=declined_row_part,
        layer1_weight_stack_declined=orphan,
        layer1_negation=negation,
        layer1_negation_rows=PILOT_BASE,
        layer1_total=layer1,
        generic_layer=generic_layer,
        generic_layers_total=generic_total,
        layer2_even_rows=layer2_even_rows,
        layer2_relu_pass=relu_charged,
        layer2_relu_writes_priced_zero=relu_free,
        layer2_precompute=precompute,
        layer2_precompute_levels=lanes["levels"],
        layer2_precompute_leaves=lanes["leaves"],
        layer2_precompute_left_stack=lanes["left_operand_stack"],
        layer2_precompute_right_stack=lanes["right_operand_stack"],
        layer2_precompute_decode=lanes["decode"],
        layer2_precompute_direct_declined=declined_direct,
        layer2_precompute_depth6_next_rung=next_rung_precompute_at_depth_six(t7),
        layer2_odd_normalization=normalization,
        layer2_odd_level1_arrays=level1,
        layer2_odd_level2_arrays=level2,
        layer2_odd_shared_prologue=prologue,
        layer2_odd_frame_element_price=_BUTTERFLY_FRAME_ELEMENT_FOLDED,
        layer2_odd_butterfly=butterfly,
        layer2_antipodal_write=antipodal_write,
        layer2_aux=layer2_aux,
        layer2_total=layer2,
        suite_once_design_stack=design_stack,
        suite_once_frame_descriptors=descriptors,
        suite_once=design_stack + descriptors,
        total=generic_total + layer1 + layer2,
    )


def incumbent_total() -> int:
    """Tier 16's bill, reconstructed from this file's own terms."""
    bill = suite_bill_per_net()
    return bill.total + bill.layer1_weight_stack_declined


def deployed_operator_fallback_total() -> int:
    """Tier 16's published fallback, carried so it can be compared."""
    t7 = _t7()
    bill = suite_bill_per_net()
    return (bill.total - bill.layer2_precompute
            + deployed_operator_precompute_cost(t7, WIDTH, WIDTH, WIDTH))


def next_rung_total() -> int:
    """What the next rung would reach.  Named, priced, NOT claimed."""
    bill = suite_bill_per_net()
    return (bill.total - bill.layer2_precompute
            + bill.layer2_precompute_depth6_next_rung)


# ---------------------------------------------------------------------------
# Executable exactness.  The claims are run, not asserted:
#   (a) layer 1's route is the butterfly, it reads only ``(phases, W0)``, and it
#       reproduces the design row product entry for entry;
#   (b) tier 10's scale folding is exact on that route;
#   (c) tier 8's layer-2 CReLU identity still closes;
#   (d) the recursed Winograd identity tier 16's precompute price rests on;
#   (e) the removed number is the module's own and is the WHOLE delta;
#   (f) the two NEW closed doors are executed;
#   (g) the carried closed doors are re-priced and NOT claimed.
# ---------------------------------------------------------------------------


def _rng(seed: int):
    state = seed

    def nxt(lo: int, hi: int) -> int:
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return lo + state % (hi - lo + 1)

    return nxt


def _mat(rows: int, cols: int, nxt, lo=-6, hi=6):
    return [[nxt(lo, hi) for _ in range(cols)] for _ in range(rows)]


def _mm(A, B):
    inner = len(B)
    return [[sum(A[i][t] * B[t][j] for t in range(inner))
             for j in range(len(B[0]))] for i in range(len(A))]


def _add(A, B):
    return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def _sub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def _relu(A):
    return [[v if v > 0 else 0 for v in row] for row in A]


def _neg(A):
    return [[-v for v in row] for row in A]


def _wht_rows(block):
    """The deployed radix-2 stage sequence over the row axis.

    Transcribed from ``kerdock_v3_estimator.py:134-143``: at half-width ``h`` the
    rows are viewed as ``(groups, 2, h)`` and each pair becomes ``(a+b, a-b)``.
    """
    rows = len(block)
    out = [row[:] for row in block]
    half = 1
    while half < rows:
        nxt = [None] * rows
        for start in range(0, rows, 2 * half):
            for off in range(half):
                a = out[start + off]
                b = out[start + half + off]
                nxt[start + off] = [x + y for x, y in zip(a, b)]
                nxt[start + half + off] = [x - y for x, y in zip(a, b)]
        out = nxt
        half *= 2
    return out


def _hadamard(width):
    """``H_width``, built the way the deployed setup builds it: the same butterfly
    run on the identity [kerdock_v3_estimator.py:24-38, :87-89]."""
    eye = [[1 if i == j else 0 for j in range(width)] for i in range(width)]
    return _wht_rows(eye)


def layer1_route(phase_signs, weight):
    """Layer 1, exactly as billed: a signed seed then radix-2 stages.

    It takes the phase vector and the weight matrix and NOTHING else.  No operand
    transform is formed, which is the operational content of "the depth-6 W-side
    stack has no reader".
    """
    seed = [[sign * value for value in weight[j]]
            for j, sign in enumerate(phase_signs)]
    return _wht_rows(seed)


def design_block(phase_signs, hadamard):
    """The design rows frame ``s`` would have contributed: ``H diag(d_s)``."""
    return [[hadamard[i][j] * phase_signs[j] for j in range(len(phase_signs))]
            for i in range(len(hadamard))]


def _winograd(A, B, levels):
    """The deployed operator's 2x2 identity, recursed ``levels`` times.

    ``row_blocked_winograd.py:110-116, 137-143, 157-163``.
    """
    if levels == 0:
        return _mm(A, B)
    m, k, n = len(A), len(B), len(B[0])
    hm, hk, hn = m // 2, k // 2, n // 2

    def q(M, r, c, hr, hc):
        return [row[c:c + hc] for row in M[r:r + hr]]

    a11, a12 = q(A, 0, 0, hm, hk), q(A, 0, hk, hm, hk)
    a21, a22 = q(A, hm, 0, hm, hk), q(A, hm, hk, hm, hk)
    b11, b12 = q(B, 0, 0, hk, hn), q(B, 0, hn, hk, hn)
    b21, b22 = q(B, hk, 0, hk, hn), q(B, hk, hn, hk, hn)
    s1 = _add(a21, a22)
    s2 = _sub(s1, a11)
    s3 = _sub(a11, a21)
    s4 = _sub(a12, s2)
    t1 = _sub(b12, b11)
    t2 = _sub(b22, t1)
    t3 = _sub(b22, b12)
    t4 = _sub(t2, b21)
    p1 = _winograd(a11, b11, levels - 1)
    p2 = _winograd(a12, b21, levels - 1)
    p3 = _winograd(s4, b22, levels - 1)
    p4 = _winograd(a22, t4, levels - 1)
    p5 = _winograd(s1, t1, levels - 1)
    p6 = _winograd(s2, t2, levels - 1)
    p7 = _winograd(s3, t3, levels - 1)
    c11 = _add(p1, p2)
    u = _add(p1, p6)
    c12 = _add(_add(u, p5), p3)
    c21 = _sub(_add(u, p7), p4)
    c22 = _add(_add(u, p7), p5)
    top = [l + r for l, r in zip(c11, c12)]
    bot = [l + r for l, r in zip(c21, c22)]
    return top + bot


def _selfcheck() -> None:
    t7 = _t7()
    bill = suite_bill_per_net()

    # ---- 1. THE LAYER-1 ROUTE IS THE BUTTERFLY, AND IT IS EXACT. ----------
    nxt = _rng(20260817)
    for width in (4, 8, 16):
        hadamard = _hadamard(width)
        w0 = _mat(width, width, nxt)
        for _frame in range(3):
            signs = [1 if nxt(0, 1) else -1 for _ in range(width)]
            routed = layer1_route(signs, w0)
            direct = _mm(design_block(signs, hadamard), w0)
            assert routed == direct, (
                "the butterfly does not reproduce the design row product")
            # (b) tier 10's scale lives on the 256x256 matrix; folding is exact.
            scaled = [[3 * v for v in row] for row in w0]
            assert layer1_route(signs, scaled) == [
                [3 * v for v in row] for row in routed]
    #     The route's whole input is (phases, W0): no third argument exists.
    assert layer1_route.__code__.co_argcount == 2

    # ---- 2. TIER 8's LAYER-2 IDENTITY STILL CLOSES ON THE SAME p. ---------
    width = 8
    hadamard = _hadamard(width)
    w0 = _mat(width, width, nxt)
    w1 = _mat(width, width, nxt)
    signs = [1 if nxt(0, 1) else -1 for _ in range(width)]
    p = layer1_route(signs, w0)
    t_top = _mm(_relu(p), w1)
    o = _mm(p, w1)
    assert _mm(_relu(_neg(p)), w1) == _sub(t_top, o), (
        "the CReLU antipodal identity does not close")
    #     and o is the butterfly on M = W0 @ W1, which is what the odd channel runs
    assert layer1_route(signs, _mm(w0, w1)) == o

    # ---- 3. THE RECURSED WINOGRAD IDENTITY THE PRECOMPUTE PRICE RESTS ON. -
    for levels in (1, 2, 3):
        side = 1 << levels
        for extra in (1, 2):
            a = _mat(side * extra, side * extra, nxt)
            b = _mat(side * extra, side * extra, nxt)
            assert _winograd(a, b, levels) == _mm(a, b), (
                f"depth-{levels} Winograd is not the product")

    # ---- 4. THE REMOVED NUMBER IS THE MODULE'S, AND IS THE WHOLE DELTA. ---
    assert bill.layer1_weight_stack_declined == t7.best_operand_grade(
        WIDTH, WIDTH, 6)[0] == 1915152
    assert bill.layer1_weight_stack_declined == bill.weight_stack
    assert incumbent_total() == _INCUMBENT_TOTAL
    assert incumbent_total() - bill.total == bill.layer1_weight_stack_declined
    assert bill.total == 144868745712
    #     It is a DIFFERENT object from the precompute's A-side stack of W0.
    assert bill.layer2_precompute_left_stack == t7.best_operand_grade(
        WIDTH, WIDTH, 5)[0] == 1092032
    assert bill.layer2_precompute_left_stack != bill.layer1_weight_stack_declined

    # ---- 5. EVERY OTHER TERM IS THE INCUMBENT'S, TERM BY TERM. ------------
    assert bill.call_total == 303096592
    assert bill.row_part_full == 301181440 and bill.row_part_tail == 263533760
    assert bill.generic_layer == 4745522832
    assert bill.generic_layers_total == _INCUMBENT_GENERIC_TOTAL
    assert bill.layer1_butterfly == 50233344
    assert bill.layer1_shared_prologue == 688128
    assert bill.layer1_normalization == 65536
    assert bill.layer1_lane == 50298880
    assert bill.layer1_negation == 65536
    assert bill.layer1_deployed_butterfly_declined == 115605504
    assert bill.layer1_winograd_row_part_declined == 2130494688
    assert bill.layer1_total == 50364416 == _INCUMBENT_LAYER1_TOTAL - 1915152
    assert bill.layer2_even_rows == 2371803840
    assert bill.layer2_precompute == 20420928
    assert bill.layer2_precompute_levels == 5
    assert bill.layer2_precompute_leaves == 16134720
    assert bill.layer2_precompute_right_stack == 1092032
    assert bill.layer2_precompute_decode == 2102144
    assert bill.layer2_precompute_direct_declined == 33488896
    assert bill.layer2_odd_normalization == 65536
    assert bill.layer2_odd_shared_prologue == 688128
    assert bill.layer2_odd_butterfly == 50233344
    assert bill.layer2_antipodal_write == 8257536
    assert bill.layer2_aux == 78977344
    assert bill.layer2_total == _INCUMBENT_LAYER2_TOTAL
    assert bill.suite_once_design_stack == 241309152
    assert bill.suite_once_frame_descriptors == 64512
    assert bill.suite_once == _INCUMBENT_SUITE_ONCE
    assert bill.total == (bill.generic_layers_total + bill.layer1_total
                          + bill.layer2_total)

    # ---- 6. NEW DOOR: THE ORPHAN ARGUMENT REACHES EXACTLY ONE LAYER. ------
    #     A W-side stack is a LANE of a call bill; where the call is issued the
    #     lane cannot be deleted without leaving the call underpaid.
    assert bill.row_part_full + bill.weight_stack == bill.call_total
    assert bill.generic_layer - bill.weight_stack == 15 * bill.row_part_full + (
        bill.row_part_full * 3 // 4)
    assert bill.layer2_even_rows == 7 * bill.row_part_full + bill.row_part_tail
    #     Stacks still charged: layers 2..32 inclusive, thirty-one of them.
    assert bill.weight_stack_layers == 31
    charged = bill.weight_stack_layers * bill.weight_stack
    assert charged == 59369712
    assert charged == (LAYERS - 2) * bill.weight_stack + bill.weight_stack
    #     Tier 3's per-LAYER rule is intact: still one stack, never 15.75.
    assert bill.generic_layer < 15.75 * (bill.row_part_full + bill.weight_stack)

    # ---- 7. NEW DOOR: THE LAYER-1 PROLOGUE IS NOT SUITE-ONCE. -------------
    #     Its level-1 arrays are pairwise sums/differences of the ROWS OF W0.
    width = 8
    wa = _mat(width, width, nxt)
    wb = [row[:] for row in wa]
    wb[0][0] += 1
    level1_a = [[x + y for x, y in zip(wa[2 * i], wa[2 * i + 1])]
                for i in range(width // 2)]
    level1_b = [[x + y for x, y in zip(wb[2 * i], wb[2 * i + 1])]
                for i in range(width // 2)]
    assert level1_a != level1_b, (
        "the prologue would be net-independent; re-open the suite-once door")
    #     The frame descriptor tables, by contrast, carry no weight at all and
    #     are the only design-only object; they are already suite-once.
    assert bill.suite_once_frame_descriptors == 2 * FRAMES * WIDTH

    # ---- 8. CARRIED DOOR: THE DEPTH IS STILL THE ARGMIN UNDER TIER 3. -----
    best_row, best_layer = None, None
    for levels in range(2, 9):
        if TILE_ROWS % (1 << levels) or WIDTH % (1 << levels):
            continue
        leaves = 7 ** levels * t7.direct_cost(
            TILE_ROWS >> levels, WIDTH >> levels, WIDTH >> levels)
        a_lane, _ = t7.best_operand_grade(TILE_ROWS, WIDTH, levels)
        w_lane, _ = t7.best_operand_grade(WIDTH, WIDTH, levels)
        d_lane, _ = t7.best_decode_grade(TILE_ROWS, WIDTH, levels)
        row = leaves + a_lane + d_lane
        amortized = 63 * row // 4 + w_lane
        if best_row is None or row < best_row[1]:
            best_row = (levels, row)
        if best_layer is None or amortized < best_layer[1]:
            best_layer = (levels, amortized)
    assert best_row[0] == 6 and best_layer[0] == 6, (
        "tier 3's discount moved the argmin; the depth is stale")
    assert best_row[1] == bill.row_part_full
    assert best_layer[1] == bill.generic_layer

    # ---- 9. CARRIED DOOR: THE ROW LANE IS EXACTLY LINEAR IN m. ------------
    def _row_lane(rows: int) -> int:
        b = t7.inplace_verbatim_leaves_candidate_bill(rows, WIDTH, WIDTH)
        return b.total - weight_side_stack_cost(t7, WIDTH, WIDTH, TILE_ROWS)

    assert 4 * _row_lane(3072) == 3 * _row_lane(TILE_ROWS)
    assert 8 * _row_lane(3584) == 7 * _row_lane(TILE_ROWS)

    # ---- 10. CARRIED DOORS THAT WOULD RAISE THE BILL. ---------------------
    incumbent_fold, honest_fold = terminal_fold_bounds()
    assert incumbent_fold == 196608 and honest_fold == 2 * incumbent_fold
    assert deployed_relu_writes_priced_zero(WIDTH) == 478937088
    #     The butterfly credit does not extend past a design row.
    hadamard = _hadamard(8)
    signs = [1 if nxt(0, 1) else -1 for _ in range(8)]
    row = design_block(signs, hadamard)[3]
    assert len({abs(v) for v in row}) == 1, "a design row is not equiamplitude"
    post = _relu(_mm(design_block(signs, hadamard), _mat(8, 8, nxt)))
    assert len({abs(v) for r in post for v in r}) > 1, (
        "the post-ReLU block is +-c; re-open the butterfly door")

    # ---- 11. CONSERVATIVENESS AND CONSISTENCY GATES. ----------------------
    assert bill.total < _INCUMBENT_TOTAL
    assert next_rung_total() < bill.total, "the next rung is a real, unclaimed rung"
    assert bill.layer2_precompute_depth6_next_rung == 18823840
    assert bill.total < deployed_operator_fallback_total()
    assert bill.suite_total(1) == bill.total + bill.suite_once
    assert bill.suite_total(1000) == 1000 * bill.total + bill.suite_once
    assert bill.amortized_numerator(4) == (bill.suite_total(4), 4)
    #     Nothing about the certified per-call floor moved.
    assert t7.inplace_verbatim_leaves_candidate_bill(
        TILE_ROWS, WIDTH, WIDTH).total == 303096592
    #     The layer-1 census: three arrays paid, one removed.
    census = layer1_weight_derived_arrays(t7)
    assert census["phase_signed_seed_and_stages_PAID"] == 49545216
    assert census["shared_level1_and_level2_arrays_PAID"] == 688128
    assert census["weight_side_normalization_PAID"] == 65536
    assert (census["phase_signed_seed_and_stages_PAID"]
            + census["shared_level1_and_level2_arrays_PAID"]
            + census["weight_side_normalization_PAID"]) == bill.layer1_lane
    assert census["winograd_B_side_depth6_stack_NO_READER"] == 1915152


if __name__ == "__main__":
    _selfcheck()
    b = suite_bill_per_net()
    for key, value in b.breakdown().items():
        print(f"{key:<62} {value:>18,}")
    print(f"{'TOTAL (per net)':<62} {b.total:>18,}")
    print(f"{'incumbent (tier 16)':<62} {incumbent_total():>18,}")
    print(f"{'delta':<62} {incumbent_total() - b.total:>18,}")
    print(f"{'next rung (depth-6 precompute), NOT claimed':<62} "
          f"{next_rung_total():>18,}")
    print(f"{'fallback: deployed operator, one level':<62} "
          f"{deployed_operator_fallback_total():>18,}")
