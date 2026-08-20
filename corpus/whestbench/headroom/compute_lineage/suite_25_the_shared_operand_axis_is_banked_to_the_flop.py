"""Suite tier 25: DRY.  Tier 18 banked the WHOLE of the shared-operand axis,
and this tier proves it to the FLOP: fusing the precompute into layer 2's own
call is exactly zero, no stage of layer 1's butterfly alphabet can carry the
precompute at any price, and the antipodal write cannot ride the odd
butterfly's final stage.

    suite bill, per net     144,867,083,088   ->   144,867,083,088   (unchanged)

Tiers 18 and 19 opened a direction and left it looking half-spent.  Tier 18
noticed that the precompute and layer 2's even-channel call share the right
operand ``W1h`` at the same depth, and rode the W-side stack.  Tier 19 noticed
that the precompute's LEFT operand can be layer 1's own ``W0'``, and retired the
odd channel's scaling pass.  Both are shared-operand moves, both paid, and both
leave the same obvious next rung sitting in plain sight:

    if the two calls share an operand, a depth and a grading, why are they two
    calls?  Stack ``W0'``'s 256 rows under ``relu(p)``'s 32,256 and issue ONE
    32,512-row product.

That rung is worth exactly nothing, and this tier executes the zero rather than
leaving the next ten tiers to discover it.  The same search closed two more
doors on the same axis.  P4: a door genuinely closed by a search is a paid
outcome.

THE FUSION OF THE PRECOMPUTE INTO LAYER 2's CALL IS EXACTLY ZERO
================================================================
The two products layer 2 issues against ``W1h`` are

    T  = relu(p) W1h        32,256 rows      [layer2_even_rows + w_stack]
    cM = W0'     W1h           256 rows      [layer2_precompute]

and stacking their left operands is exact, because a matrix product is
row-blockwise:  ``[relu(p) ; W0'] W1h = [relu(p) W1h ; W0' W1h] = [T ; cM]``.
``_selfcheck`` executes that block identity on integer matrices rather than
asserting it.  So the fused route is legal.  It is also worthless:

    split   row(32,256) + w_stack + row(256)   2,371,803,840
                                             +     1,915,152
                                             +    18,823,840  = 2,392,542,832
    fused   row(32,512) + w_stack             2,390,627,680
                                             +     1,915,152  = 2,392,542,832

    delta                                                                   0

and the zero is structural, not a coincidence of these three numbers.  After
tier 3 and tier 18 the call bill has exactly one m-INDEPENDENT lane -- the
W-side operand stack -- and that lane is already charged once and already
ridden.  Every other lane (leaves, A-side stack, decode) is exactly linear in
``m``, so splitting 32,512 rows into 32,256 + 256 costs the same as not
splitting them.  ``_selfcheck`` re-derives the linearity at 256, 512, 2,048,
3,072, 3,584, 3,840, 32,256, 32,512, 32,768 and 64,512 rows against
``row(4096) * m / 4096`` as an exact fraction, and asserts the fused shape's
depth argmin is still 6, so the two routes are compared at the same depth.

The rung is therefore not "small".  It is zero, and the next tier should not
spend a turn on it.

    THE FUSION IS ALSO STRICTLY WORSE IN THE SHAPE, WHICH IS WHY IT IS SHUT
    RATHER THAN MERELY UNPAID.  A single 32,512-row call needs its left operand
    contiguous.  ``relu(p)`` is rows 0..32,255 of ``self._activation``
    [kerdock_v3_estimator.py:79-82, fold3_estimator.py:74-90] and row 32,256 of
    that buffer is where the antipodal write puts ``T - O``; ``W0'`` is a
    separate 256 x 256 array.  So the fused call must first copy ``W0'`` into a
    contiguous slot -- 65,536 element-copies the ledger WOULD charge -- or run a
    strided gather.  Priced by ``fused_precompute_call()`` and printed beside the
    zero.  SHUT both ways.

NO STAGE OF LAYER 1's ALPHABET CAN CARRY THE PRECOMPUTE
=======================================================
This is the second rung tier 19 makes tempting, and it is the more dangerous of
the two because the identity behind it is TRUE and exact.

The odd butterfly's prologue builds, from ``cM``, the frame-independent arrays
tiers 12 and 13 crowned: four level-1 arrays per pair of rows and thirty-two
level-2 arrays per group of four.  Every one of them is a fixed signed sum of
ROWS of ``cM``, and ``cM = W0' W1h``, so every one of them is the SAME signed
sum of rows of ``W0'``, right-multiplied by ``W1h``:

    P_t(cM) = cM[2t] + cM[2t+1] = (W0'[2t] + W0'[2t+1]) W1h = P_t(W0') W1h

and likewise for ``Q``, ``R``, ``S`` and for all thirty-two level-2 arrays.
``_selfcheck`` EXECUTES this on integer matrices, array by array, at both
levels.  Layer 1 already builds and this bill already charges that alphabet, so
tier 3's licence would appear to hand layer 2 the alphabet of ``cM`` for the
price of one matmul -- retiring the precompute AND the odd prologue together.

It never pays, at any stage, for one reason that needs no arithmetic beyond a
row count: THE ALPHABET IS BIGGER THAN THE MATRIX IT IS BUILT FROM.  ``cM`` has
256 rows.  Layer 1's stage-k alphabet has

    stage 1     4 arrays x 128 pairs   =    512 rows   =   2 x 256
    stage 2    32 arrays x  64 groups  =  2,048 rows   =   8 x 256
    stage 3 1,024 arrays x  32 groups  = 32,768 rows   = 128 x 256

so pushing the ``W1h`` matmul PAST the alphabet construction multiplies the
matmul's row count by 2, 8 or 128.  Priced against the route this bill charges
(precompute 18,823,840 + odd prologue 688,128 = 19,511,968):

    stage 1   map 512 rows (37,647,680) then build level 2 (524,288)
                                                     38,171,968   +18,660,000
    stage 2   map 2,048 rows                        150,590,720  +131,078,752
    stage 3   map 32,768 rows                     2,409,451,520 +2,389,939,552

Every one of those maps already has the W-side stack ridden, so the comparison
is as generous to the alphabet route as tier 18's licence allows.  The three
counts 4, 32 and 1,024 are tier 12's and tier 13's crowned counts, and the
alphabet only grows above stage 3 [suite_13, suite_20], so no stage pays.  The
direct route is the strict argmin because ``cM`` is the SMALLEST array in the
chain that the alphabet is a function of -- which is tier 10's rule ("the
scalar rides the smallest array in the linear chain") read on the matmul rather
than on the scalar.  SHUT at every stage.

THE ANTIPODAL WRITE CANNOT RIDE THE ODD BUTTERFLY'S FINAL STAGE
===============================================================
The third rung, and the cheapest-looking of the three.  ``O`` is written by the
odd butterfly's last surviving stage and is read by exactly one thing: the
antipodal write ``bottom = T - O``.  A stage that wrote ``T - (x +- y)``
directly would delete a whole 8,257,536-element pass and a whole buffer round
trip.  It deletes neither op:

    unfused   6 stage-ops/element + 1 subtract/element   = 7 x 8,257,536
                                                         = 57,802,752
    fused     5 stage-ops/element + 2 ops/element        = 7 x 8,257,536
                                                         = 57,802,752

    delta                                                              0

because ``T - (x + y)`` is two element-ops however it is spelled: the ladder
does not permit reassociating it into one, and ``(T - x) - y`` is two as well.
``_selfcheck`` re-prices the butterfly with a two-op terminal stage and asserts
the tie to the op, and also asserts the VALUES agree -- the fused form performs
the identical add and the identical subtract on the identical operands in the
identical order, so it is not an f32 question at all.  SHUT.

THE ONE REDUNDANCY THE INCUMBENT NAMES, PRICED AND LEFT STANDING
================================================================
``frame_descriptor_table_cost``'s own docstring, carried unchanged since tier
13, says of the butterflies' index tables: "Charged twice though one would
serve."  It is right, and this tier proves why: the table a frame's row uses to
select its level-2 array is indexed by that frame's phase signs restricted to
the row's group of four, and by the row's position in the group.  It mentions
the seed matrix nowhere.  ``W0'`` and ``cM`` are different matrices with the
SAME selector, so one table serves both butterflies.

    frame descriptor tables, suite-once     64,512   ->   32,256   (-32,256)

It is NOT taken here, and the reason is arithmetic rather than scruple: the
tables are a SUITE-ONCE field.  They sit outside ``.total`` because they are a
function of the frozen phases alone and are built once for the whole suite, so
retiring one of them moves ``suite_once`` from 241,373,664 to 241,341,408 and
moves the per-net bill this ladder is scored on by EXACTLY ZERO.  Priced by
``shared_descriptor_table_price()`` and printed beside the claim; left for a
suite-once adjudication that can score it.  NOT CLAIMED.

WHAT ELSE THE SEARCH TOUCHED, RE-EXECUTED SO IT IS NOT RE-SPENT
===============================================================
  * THE DEPTH ARGMIN.  Depth 6 minimises the per-call bill, the per-layer
    objective ``15.75 * row(L) + stack(L)`` AND layer 2's half-size objective
    ``7.875 * row(L) + stack(L)``, brute-forced over every lawful depth.  The
    certified per-call floor is re-derived and asserted at 303,096,592 at the
    anonymous (4096, 256, 256).  SHUT.
  * THE SHARED BUTTERFLY DEPTH.  Sharing stages 1..d and paying the alphabet
    gives 74,317,824 / 57,966,592 / 50,233,344 / 50,364,416 at d = 0, 1, 2, 3.
    Depth 2 is the strict argmin; depth 3 loses by 131,072.  Re-executed from
    this file's own terms, not carried as a literal.  SHUT [tier 13, tier 20].
  * THE SCALING PASSES.  The bill charges exactly one, of 65,536, at layer 1.
    Asserted by enumerating every term.  Its seat is at its argmin and its
    upstream seats are illegal [tier 20]; carried, not re-derived.
  * THE ANTIPODAL HALF BEYOND LAYER 2, THE TERMINAL FOLD, PRUNING, AND THE
    LEDGER-FREE ReLU WRITES.  All four raise the bill if modelled honestly.
    Counted below, none claimed: the terminal fold's honest worst case is six
    row-scaled units against the three charged, and the ledger-free ReLU writes
    are 478,937,088 priced at zero.
  * THE SUITE-ONCE DESIGN STACK, orphaned since tier 14 at 241,309,152, still
    sits outside ``.total`` and still cannot move the fitness.

EXACTNESS IDENTITY
==================
This tier proposes no route change, so the route is IDENTICAL to tier 19's and
tier 20's, term for term: every term below is computed by the same function on
the same arguments, and ``_selfcheck`` asserts term-by-term equality against the
published figures and ``.total == 144,867,083,088``.

What is executed here is the exactness of the three routes that are NOT taken,
because a door closed on cost is only closed if the route behind it was legal:

  (i)   the block-row identity ``[A ; B] W = [A W ; B W]``, which is what makes
        the fused 32,512-row call a genuine rung rather than a mistake;
  (ii)  the alphabet identity ``alphabet(W0' W1h) = alphabet(W0') W1h``, run
        array by array at level 1 (na, P, Q, R, S) and at level 2 (all
        thirty-two sums and differences), which is what makes the alphabet route
        a genuine rung;
  (iii) the fused terminal stage ``T - (x + y)``, run against the unfused
        ``O = x + y ; T - O`` and shown equal operand for operand;
  (iv)  the identities the charged route itself rests on, re-run so this file
        stands alone: the CReLU split ``relu(-p) W1h = relu(p) W1h - p W1h``,
        the design product ``O_s = H diag(d_s) cM`` against the dense product,
        and the scalar's associativity ``c (W0 W1h) = (c W0) W1h`` (tier 19).

f32 STATUS: NO REPRICING, NO FLAG
=================================
No op is added, removed or repriced anywhere in the bill; the route that is
charged is byte-for-byte tier 19's.  The three doors are closed by arithmetic
about routes that are not taken, and none of the three would have needed an f32
concession either -- the block-row identity moves no summation, the alphabet
identity is the same signed sums in the same order, and the fused terminal stage
performs the identical add and subtract.  The two IEEE identities the ladder
permits (``a - b`` IS ``a + (-b)``; negation IS a sign flip) are used only where
tiers 12 and 13 already used them, and the two it refuses (``(-a) + (-b) ==
-(a + b)``; ``-(a - b) == b - a``) are used nowhere.

No f32 repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A DRY tier has no metered win to repay, but it carries the same slope
obligation as any other: the value it delivers is the wall time the next tiers
do not spend, and that value is only real if the doors are shut for
implementation reasons too.  All three are, and each is shut HARDER in the
shape than on the ledger.

  * THE FUSED CALL is zero on the ledger and negative twice over in the shape.
    It needs 65,536 element-copies (or a strided gather) to make
    ``[relu(p) ; W0']`` contiguous, because ``relu(p)`` occupies rows 0..32,255
    of the sampled activation and row 32,256 is the antipodal write's
    destination.  And it lengthens the critical path: today the 256-row
    precompute is a small independent launch whose result the odd butterfly
    waits on, while the 7.875 even-channel tiles proceed; fused, the odd
    butterfly waits for a 32,512-row call.  Fewer launches, later start.
  * THE ALPHABET ROUTE replaces a 256 x 256 f32 matmul (256 KB of output) with a
    512 x 256 or 2,048 x 256 one (512 KB or 2 MB), makes the butterfly's
    prologue depend on a matmul rather than on a resident array, and keeps
    layer 1's alphabet live across the whole of layer 2 instead of freeing it
    after layer 1's frames.  Named with its numbers so no later tier re-opens it
    hoping the shape would pay for the arithmetic.
  * THE FUSED TERMINAL STAGE ties on the ledger and loses on traffic: the stage
    would read three arrays per element instead of two, and it gives up the
    ping-pong's in-place write into the alternate frame buffer (tier 11), which
    is the property that made the stage one op in the first place.
  * THE DESCRIPTOR TABLE would be shape-free and mildly positive -- one 126 x
    256 index table resident instead of two -- but it is suite-once and cannot
    move the per-net bill.  Priced, not taken.
  * NOTHING MOVES.  The 126 frames, the 15.75 tiles, the 31 charged W-side
    stacks, the two butterflies, the one scaling pass and the single 256-row
    precompute are scheduled exactly as tier 19 schedules them.  Flat in the
    suite size: ``.total`` and ``suite_once`` are asserted at 144,867,083,088
    and 241,373,664.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from fractions import Fraction

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

# Tier 12 and tier 13's crowned alphabet counts, per group of ``2 ** stage``
# rows.  Level 1 costs FIVE ops but yields FOUR arrays that are read (``na`` is
# scratch for ``R`` and ``S``); the row count of the alphabet is what door 2
# needs, so the READ count is the one tabulated here.
_ALPHABET_ARRAYS_PER_GROUP = {1: 4, 2: _LEVEL2_ARRAYS_PER_GROUP, 3: 1024}

# Suite tier 6, REJECTED: the depth-5 call with BOTH operand lanes waived.
_TIER6_REJECTED_PRECOMPUTE = 18236864
# Tier 16's rule at the module's own isolated argmin, carried by tiers 17..19.
_TIER16_PRECOMPUTE_DEPTH5 = 20420928

# Tier 19/20's published figures, carried so every one can be re-asserted.
_INCUMBENT_TOTAL = 144867083088
_INCUMBENT_LAYER1_TOTAL = 50364416
_INCUMBENT_LAYER2_TOTAL = 2451033712
_INCUMBENT_LAYER2_AUX = 77314720
_INCUMBENT_GENERIC_TOTAL = 142365684960
_INCUMBENT_SUITE_ONCE = 241373664
_CERTIFIED_CALL_FLOOR = 303096592

# The number of layers that DO issue a Winograd call: 2..32 inclusive.
_WINOGRAD_CALLING_LAYERS = LAYERS - 1


def _t7():
    spec = importlib.util.spec_from_file_location("t25base", _T7_PATH)
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


def layer_call_depth(t7, m: int = TILE_ROWS, k: int = WIDTH,
                     n: int = WIDTH) -> int:
    """The depth at which every charged Winograd call in this bill runs."""
    return _selected_levels(
        t7.inplace_verbatim_leaves_candidate_bill(m, k, n).strategy
    )


def weight_side_stack_cost(t7, k: int = WIDTH, n: int = WIDTH,
                           m: int = TILE_ROWS) -> int:
    """Tier 3's term: the m-independent W-side (k, n) stack of the call bill."""
    levels = layer_call_depth(t7, m, k, n)
    cost, _grade = t7.best_operand_grade(k, n, levels)
    return cost


def weight_side_stack_grade(t7, k: int = WIDTH, n: int = WIDTH,
                            m: int = TILE_ROWS):
    """The (cost, grading) pair of the same lane, so identity can be asserted."""
    return t7.best_operand_grade(k, n, layer_call_depth(t7, m, k, n))


def row_lane(t7, m: int, k: int = WIDTH, n: int = WIDTH,
             levels: int | None = None) -> int:
    """The m-SCALED part of a call at the bill's depth: leaves + A-stack + decode.

    This is the whole call minus the one m-independent lane, tier 3's W-side
    operand stack.  Every door this tier closes is a statement about this
    function, so it is defined once and used everywhere.
    """
    if levels is None:
        levels = layer_call_depth(t7, TILE_ROWS, k, n)
    block = 1 << levels
    if m % block or k % block or n % block:
        raise ValueError(f"{m}x{k}x{n} does not carry {levels} Winograd levels")
    stack, _grade = t7.best_operand_grade(k, n, levels)
    return t7.inplace_depth_core_cost(m, k, n, levels) - stack


# ---------------------------------------------------------------------------
# DOOR 1.  Fusing the precompute into layer 2's own call.
# ---------------------------------------------------------------------------


def fused_precompute_call(t7, k: int = WIDTH, n: int = WIDTH) -> dict:
    """Price the 32,512-row fused call against the 32,256 + 256 split.

    ``[relu(p) ; W0'] W1h = [T ; cM]`` is exact (a product is row-blockwise), so
    the fused route is legal.  It is worth exactly zero: after tier 3 and tier
    18 the only m-INDEPENDENT lane in the call is the W-side operand stack, and
    that lane is charged once in both routes.  The contiguity copy the fused
    route needs is priced beside the zero and is NOT netted into the delta.
    """
    depth = layer_call_depth(t7, TILE_ROWS, k, n)
    stack = weight_side_stack_cost(t7, k, n, TILE_ROWS)
    fused_rows = BASE_ROWS + WIDTH
    split = row_lane(t7, BASE_ROWS, k, n) + stack + row_lane(t7, WIDTH, k, n)
    fused = row_lane(t7, fused_rows, k, n) + stack
    fused_depth = layer_call_depth(t7, fused_rows, k, n)
    return {
        "split_rows": (BASE_ROWS, WIDTH),
        "fused_rows": fused_rows,
        "depth": depth,
        "fused_depth": fused_depth,
        "split_total": split,
        "fused_total": fused,
        "delta": fused - split,
        "contiguity_copies_the_fusion_needs": WIDTH * WIDTH,
    }


# ---------------------------------------------------------------------------
# DOOR 2.  Carrying the precompute on layer 1's own butterfly alphabet.
# ---------------------------------------------------------------------------


def alphabet_rows(stage: int, rows: int = WIDTH) -> int:
    """Rows in layer 1's stage-``stage`` frame-independent alphabet.

    Tier 12's four level-1 arrays per PAIR and tier 13's thirty-two level-2
    arrays per GROUP OF FOUR, with tier 13's stage-3 count carried for the rung
    it already shut.  Every one of these is larger than the 256-row matrix it
    is built from, which is the whole of door 2.
    """
    if stage not in _ALPHABET_ARRAYS_PER_GROUP:
        raise ValueError(f"the ladder prices no stage-{stage} alphabet")
    group = 1 << stage
    if rows % group:
        raise ValueError(f"{rows} rows do not group evenly at stage {stage}")
    return _ALPHABET_ARRAYS_PER_GROUP[stage] * (rows // group)


def alphabet_carry_price(t7, stage: int) -> dict:
    """What it would cost to reach ``cM``'s alphabet through layer 1's.

    ``alphabet(W0' W1h) = alphabet(W0') W1h`` exactly, so the route is legal.
    Its matmul has ``alphabet_rows(stage)`` rows instead of ``cM``'s 256, and
    the W-side stack is ridden in BOTH routes (tier 18), so the comparison is as
    generous to the alphabet route as the ladder allows.  Any level below the
    one that is mapped must still be built from the mapped arrays.
    """
    rows = alphabet_rows(stage)
    mapped = row_lane(t7, rows)
    residue = 0
    if stage == 1:
        # Stage 1 arrives; the level-2 alphabet still has to be built from it.
        residue = _LEVEL2_ARRAYS_PER_GROUP * (WIDTH // 4) * WIDTH
    charged = precompute_cost(t7, WIDTH, WIDTH, WIDTH) + shared_prologue_cost(
        _SHARED_DEPTH, WIDTH, WIDTH
    )
    return {
        "stage": stage,
        "alphabet_rows": rows,
        "row_multiple_of_the_matrix": rows // WIDTH,
        "mapped_matmul": mapped,
        "levels_still_to_build": residue,
        "route_total": mapped + residue,
        "charged_route": charged,
        "worse_by": mapped + residue - charged,
    }


# ---------------------------------------------------------------------------
# DOOR 3.  Riding the antipodal write on the odd butterfly's final stage.
# ---------------------------------------------------------------------------


def fused_antipodal_final_stage() -> dict:
    """``T - (x +- y)`` is two element-ops, so the fusion is an exact tie."""
    elements = BASE_ROWS * WIDTH
    unfused = _BUTTERFLY_FRAME_ELEMENT_FOLDED * elements + elements
    fused = (_BUTTERFLY_FRAME_ELEMENT_FOLDED - 1) * elements + 2 * elements
    return {
        "unfused_stage_ops_per_element": _BUTTERFLY_FRAME_ELEMENT_FOLDED,
        "unfused_total": unfused,
        "fused_terminal_stage_ops_per_element": 2,
        "fused_total": fused,
        "delta": fused - unfused,
    }


# ---------------------------------------------------------------------------
# THE NAMED REDUNDANCY, PRICED AND LEFT STANDING (suite-once, outside .total).
# ---------------------------------------------------------------------------


def shared_descriptor_table_price(frames: int = FRAMES,
                                  rows: int = WIDTH) -> dict:
    """One index table serves both butterflies -- but the field is suite-once.

    The selector for frame ``s``'s row ``j`` is a function of ``d_s`` restricted
    to ``j``'s group of four and of ``j``'s position in that group.  It mentions
    the seed matrix nowhere, so ``W0'``'s butterfly and ``cM``'s butterfly read
    the SAME table.  The saving is real and it is 32,256 -- and it is entirely
    inside ``suite_once``, so it moves the per-net bill by zero.  NOT CLAIMED.
    """
    charged = frame_descriptor_table_cost(frames, rows, 2)
    shared = frame_descriptor_table_cost(frames, rows, 1)
    return {
        "charged_suite_once": charged,
        "one_table_would_serve": shared,
        "suite_once_saving_NOT_CLAIMED": charged - shared,
        "per_net_saving": 0,
    }


# ---------------------------------------------------------------------------
# Carried machinery.  Every function below is tier 19's, unchanged, so the terms
# it produces can be asserted equal to the incumbent's term by term.
# ---------------------------------------------------------------------------


def normalization_cost(k: int = WIDTH, n: int = WIDTH) -> int:
    """Tier 10's term: the design's scalar folded onto a (k, n) weight matrix."""
    if min(k, n) <= 0:
        raise ValueError("the normalized matrix has positive dimensions")
    return k * n


def layer1_normalization_readers() -> tuple:
    """The readers of ``W0' = c W0``, enumerated (tier 19)."""
    return ("layer1_butterfly_seed_126_frames",
            "layer2_precompute_A_side_operand_transform")


def odd_channel_normalization_cost(k: int = WIDTH, n: int = WIDTH) -> int:
    """Tier 19's zero: ``cM`` is produced already scaled, so nothing to scale."""
    if min(k, n) <= 0:
        raise ValueError("the normalized matrix has positive dimensions")
    if len(layer1_normalization_readers()) != 2:
        raise ValueError("the scaled matrix does not have a second reader")
    return 0


def odd_channel_normalization_ridden(k: int = WIDTH, n: int = WIDTH) -> int:
    """What tier 18 charged there, carried so the delta stays auditable."""
    return normalization_cost(k, n)


def precompute_lanes(t7, k: int = WIDTH, n: int = WIDTH,
                     m: int = WIDTH) -> dict:
    """``cM``'s four lanes at layer 2's depth, with the W-side lane ridden."""
    levels = layer_call_depth(t7, TILE_ROWS, k, n)
    block = 1 << levels
    if m % block or k % block or n % block:
        raise ValueError("the precompute's shape does not carry layer 2's depth")
    leaves = 7 ** levels * t7.direct_cost(m // block, k // block, n // block)
    left, left_grade = t7.best_operand_grade(m, k, levels)
    right, right_grade = t7.best_operand_grade(k, n, levels)
    decode, _ = t7.best_decode_grade(m, n, levels)

    shared, shared_grade = weight_side_stack_grade(t7, k, n, TILE_ROWS)
    if (right, right_grade) != (shared, shared_grade):
        raise ValueError("the two W-side stacks are not the same graded object")

    standalone = leaves + left + right + decode
    if standalone != t7.inplace_depth_core_cost(m, k, n, levels):
        raise ValueError("the re-derived lanes are not the module's core bill")
    return {
        "levels": levels,
        "leaves": leaves,
        "left_operand_stack": left,
        "right_operand_stack_RIDDEN": right,
        "decode": decode,
        "standalone": standalone,
        "total": leaves + left + decode,
    }


def precompute_cost(t7, k: int = WIDTH, n: int = WIDTH, m: int = WIDTH) -> int:
    """cM's price: layer 2's depth, W-side lane ridden, left operand W0'."""
    return precompute_lanes(t7, k, n, m)["total"]


def declined_direct_precompute_cost(k: int = WIDTH, n: int = WIDTH,
                                    m: int = WIDTH) -> int:
    """Tier 15's charge: the cost model's named counterfactual."""
    return direct_cost(m, k, n)


def deployed_operator_precompute_cost(t7, k: int = WIDTH, n: int = WIDTH,
                                      m: int = WIDTH) -> int:
    """The published fallback: the DEPLOYED operator's own one-level bill."""
    return t7.owned_batched_candidate_bill(m, k, n).total


def declined_isolated_precompute_cost(t7, k: int = WIDTH, n: int = WIDTH,
                                      m: int = WIDTH) -> int:
    """Tier 16's price: the module's argmin computed in ISOLATION, depth 5."""
    return t7.inplace_verbatim_leaves_candidate_bill(m, k, n).total


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


def stage3_shared_alphabet_cost(rows: int = WIDTH,
                                out_width: int = WIDTH) -> int:
    """Tier 13's stage-3 alphabet, carried so the depth sweep can run to 3."""
    group = 8
    if rows % group:
        raise ValueError("stage 3 needs groups of eight rows")
    return _ALPHABET_ARRAYS_PER_GROUP[3] * (rows // group) * out_width


def butterfly_ops(frames: int, rows: int, out_width: int, *,
                  final_scale: bool, pingpong: bool,
                  shared_depth: int = 0) -> int:
    """Ops a phased-WHT butterfly over ``frames`` frames costs (tier 2's shape)."""
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


def butterfly_at_shared_depth(depth: int, frames: int = FRAMES,
                              rows: int = WIDTH,
                              out_width: int = WIDTH) -> int:
    """The butterfly priced with stages ``1..depth`` shared, for depth 0..3.

    Depth 0 is tier 11's per-frame schedule with its seed pass; depths 1 and 2
    are tiers 12 and 13; depth 3 pays tier 13's 1,024-array group alphabet.  The
    argmin is depth 2, and this function is what proves it here rather than
    carrying the four numbers as literals.
    """
    elements = rows * out_width
    stages = _log2_exact(rows)
    if depth == 0:
        return frames * ((_BUTTERFLY_SEED * elements)
                         + stages * _STAGE_HALVES_PINGPONG * (elements // 2))
    if depth in (1, 2):
        return butterfly_ops(frames, rows, out_width, final_scale=False,
                             pingpong=True, shared_depth=depth)
    if depth == 3:
        return (frames * (stages - 3) * _STAGE_HALVES_PINGPONG * (elements // 2)
                + shared_prologue_cost(2, rows, out_width)
                + stage3_shared_alphabet_cost(rows, out_width))
    raise ValueError("the ladder prices shared depths 0..3")


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
    """Tier 5's A-side (m, k) operand lane, kept as a published one-time field."""
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
    call_depth: int
    weight_stack: int
    weight_stack_layers: int
    row_part_full: int
    row_part_tail: int
    layers: int
    layer1_butterfly: int
    layer1_normalization: int
    layer1_normalization_readers: int
    layer1_shared_prologue: int
    layer1_frame_element_price: int
    layer1_lane: int
    layer1_deployed_butterfly_declined: int
    layer1_winograd_row_part_declined: int
    layer1_weight_stack_removed_tier17: int
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
    layer2_precompute_right_stack_ridden: int
    layer2_precompute_decode: int
    layer2_precompute_standalone: int
    layer2_precompute_direct_declined: int
    layer2_precompute_isolated_declined: int
    layer2_precompute_fused_call_declined: int
    layer2_precompute_fusion_delta: int
    layer2_alphabet_carry_declined: int
    layer2_odd_normalization: int
    layer2_odd_normalization_ridden: int
    layer2_odd_level1_arrays: int
    layer2_odd_level2_arrays: int
    layer2_odd_shared_prologue: int
    layer2_odd_shared_depth: int
    layer2_odd_frame_element_price: int
    layer2_odd_butterfly: int
    layer2_antipodal_write: int
    layer2_antipodal_fusion_delta: int
    layer2_aux: int
    layer2_total: int
    scaling_passes_charged: int
    suite_once_design_stack: int
    suite_once_frame_descriptors: int
    suite_once_descriptor_rung_NOT_CLAIMED: int
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
            "winograd_depth_of_every_charged_call": self.call_depth,
            "certified_per_call_floor": self.call_total,
            "weight_side_stack_per_CALLING_layer": self.weight_stack,
            "weight_side_stacks_CHARGED_layers_2_to_32":
                self.weight_stack_layers * self.weight_stack,
            "row_part_per_full_tile": self.row_part_full,
            "layer1_crowned_butterfly_32256_rows": self.layer1_butterfly,
            "layer1_shared_prologue_of_W0PRIME": self.layer1_shared_prologue,
            "layer1_normalization_THE_ONLY_SCALING_PASS":
                self.layer1_normalization,
            "layer1_normalization_READER_COUNT":
                self.layer1_normalization_readers,
            "layer1_butterfly_lane_total": self.layer1_lane,
            "layer1_deployed_transcription_DECLINED":
                self.layer1_deployed_butterfly_declined,
            "layer1_winograd_row_part_DECLINED":
                self.layer1_winograd_row_part_declined,
            "layer1_weight_side_stack_REMOVED_BY_TIER_17":
                self.layer1_weight_stack_removed_tier17,
            "layer1_antipodal_negation": self.layer1_negation,
            "layer1_total_per_net": self.layer1_total,
            "generic_layer_total": self.generic_layer,
            "generic_layers_3_to_32": self.generic_layers_total,
            "layer2_top_channel_row_part_32256": self.layer2_even_rows,
            "layer2_weight_side_stack_KEPT_THE_CALL_IS_MADE": self.weight_stack,
            "layer2_relu_pass_CHARGED": self.layer2_relu_pass,
            "layer2_relu_write_PRICED_ZERO_by_the_ledger":
                self.layer2_relu_writes_priced_zero,
            "layer2_precompute_DEPTH_equals_the_layer_call_depth":
                self.layer2_precompute_levels,
            "layer2_precompute_lane_leaves": self.layer2_precompute_leaves,
            "layer2_precompute_lane_A_side_stack_of_W0PRIME":
                self.layer2_precompute_left_stack,
            "layer2_precompute_lane_W_side_stack_RIDDEN_TIER_18":
                self.layer2_precompute_right_stack_ridden,
            "layer2_precompute_lane_decode": self.layer2_precompute_decode,
            "layer2_precompute_W0PRIME_W1h_IS_cM_ALREADY_SCALED":
                self.layer2_precompute,
            "layer2_precompute_STANDALONE_AT_THIS_DEPTH":
                self.layer2_precompute_standalone,
            "layer2_precompute_ISOLATED_ARGMIN_DEPTH5_DECLINED":
                self.layer2_precompute_isolated_declined,
            "layer2_precompute_DIRECT_COUNTERFACTUAL_DECLINED":
                self.layer2_precompute_direct_declined,
            "DOOR1_fused_32512_row_call_TOTAL":
                self.layer2_precompute_fused_call_declined,
            "DOOR1_fusion_delta_EXACTLY_ZERO":
                self.layer2_precompute_fusion_delta,
            "DOOR2_cheapest_alphabet_carry_route_DECLINED":
                self.layer2_alphabet_carry_declined,
            "layer2_odd_normalization_NOTHING_LEFT_TO_SCALE":
                self.layer2_odd_normalization,
            "layer2_odd_normalization_TIER19_REMOVED":
                self.layer2_odd_normalization_ridden,
            "layer2_odd_SHARED_level1_five_ops_per_pair":
                self.layer2_odd_level1_arrays,
            "layer2_odd_SHARED_level2_thirtytwo_per_group":
                self.layer2_odd_level2_arrays,
            "layer2_odd_shared_prologue_total":
                self.layer2_odd_shared_prologue,
            "layer2_odd_shared_depth_ARGMIN": self.layer2_odd_shared_depth,
            "layer2_odd_channel_butterfly": self.layer2_odd_butterfly,
            "layer2_antipodal_write_32256": self.layer2_antipodal_write,
            "DOOR3_antipodal_write_fused_into_last_stage_delta":
                self.layer2_antipodal_fusion_delta,
            "layer2_auxiliary_terms": self.layer2_aux,
            "layer2_total": self.layer2_total,
            "scaling_passes_CHARGED_in_the_whole_bill":
                self.scaling_passes_charged,
            "design_side_stack_ORPHANED_but_OUTSIDE_total_and_KEPT":
                self.suite_once_design_stack,
            "frame_descriptor_tables_TWO_charged_ONCE_to_the_suite":
                self.suite_once_frame_descriptors,
            "descriptor_rung_SUITE_ONCE_ONLY_NOT_CLAIMED":
                self.suite_once_descriptor_rung_NOT_CLAIMED,
            "total": self.total,
        }


def _layer2_auxiliary_terms(t7) -> tuple:
    """Layer 2's non-matmul terms.  Tier 19's, unchanged."""
    precompute = precompute_cost(t7, WIDTH, WIDTH, WIDTH)             # 18,823,840
    normalization = odd_channel_normalization_cost(WIDTH, WIDTH)      #          0
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                              pingpong=True, shared_depth=_SHARED_DEPTH)
    antipodal_write = BASE_ROWS * WIDTH                               #  8,257,536
    return precompute, normalization, butterfly, antipodal_write


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill.  Identical to tier 19's, term for term.

    This tier is DRY: it proposes no route change.  What it adds are three
    executed zeros on the shared-operand axis tiers 18 and 19 opened -- the
    fused call, the alphabet carry and the fused antipodal write -- so the next
    tier does not spend a turn rediscovering that the axis is spent.
    """
    t7 = _t7()
    bill_full = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    bill_tail = t7.inplace_verbatim_leaves_candidate_bill(
        BASE_ROWS % TILE_ROWS, k, n
    )
    if bill_full.core_k != bill_tail.core_k or bill_full.core_n != bill_tail.core_n:
        raise ValueError("full and tail calls do not share a right-hand stack")
    depth = _selected_levels(bill_full.strategy)
    if depth != _selected_levels(bill_tail.strategy):
        raise ValueError("full and tail calls sit at different Winograd depths")

    call = bill_full.total
    if call != _CERTIFIED_CALL_FLOOR:
        raise ValueError("the certified per-call floor has moved")
    w_stack = weight_side_stack_cost(t7, k, n, m)
    row_full = call - w_stack
    row_tail = bill_tail.total - w_stack
    if row_full != row_lane(t7, m, k, n):
        raise ValueError("the row lane is not the call minus the W-side stack")

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

    # --- layer 1: tier 19's, carried verbatim --------------------------------
    if PILOT_BASE > BASE_ROWS:
        raise ValueError("the pilot cannot read more rows than the half has")
    declined_deployed = deployed_first_product_cost(FRAMES, WIDTH, WIDTH)
    if declined_deployed != _BUTTERFLY_PER_ELEMENT_DEPLOYED * BASE_ROWS * WIDTH:
        raise ValueError("tier 14's transcription is not at its certified 14/element")
    layer1_butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                                     pingpong=True, shared_depth=_SHARED_DEPTH)
    layer1_prologue = shared_prologue_cost(_SHARED_DEPTH, WIDTH, WIDTH)
    layer1_normalization = normalization_cost(WIDTH, WIDTH)
    readers = layer1_normalization_readers()
    if len(set(readers)) != 2:
        raise ValueError("W0' must have exactly the two enumerated readers")
    layer1_lane = layer1_butterfly + layer1_normalization
    if layer1_lane != crowned_first_product_cost(FRAMES, WIDTH, WIDTH):
        raise ValueError("the layer-1 lane is not tier 15's crowned schedule price")
    if layer1_butterfly - layer1_prologue != (
            _BUTTERFLY_FRAME_ELEMENT_FOLDED * BASE_ROWS * WIDTH):
        raise ValueError("the surviving layer-1 stages are not one pass each")
    negation = antipodal_negation_cost(PILOT_BASE, WIDTH)
    layer1 = layer1_lane + negation

    # --- layer 2: tier 19's terms, plus this tier's three executed zeros ------
    layer2_even_rows = base_rows_part
    lanes = precompute_lanes(t7, WIDTH, WIDTH, WIDTH)
    if lanes["levels"] != depth:
        raise ValueError("the precompute is not at the depth of the ridden stack")
    if lanes["right_operand_stack_RIDDEN"] != w_stack:
        raise ValueError("the ridden lane is not layer 2's charged W-side stack")
    precompute, normalization, butterfly, antipodal_write = (
        _layer2_auxiliary_terms(t7)
    )
    if normalization != 0:
        raise ValueError("the odd channel still carries a scaling pass")
    ridden_normalization = odd_channel_normalization_ridden(WIDTH, WIDTH)
    if ridden_normalization != layer1_normalization:
        raise ValueError("the removed pass is not the size of the array it rides")
    declined_direct = declined_direct_precompute_cost(WIDTH, WIDTH, WIDTH)
    declined_isolated = declined_isolated_precompute_cost(t7, WIDTH, WIDTH, WIDTH)
    if declined_isolated != _TIER16_PRECOMPUTE_DEPTH5:
        raise ValueError("tier 16's isolated argmin price has moved")
    if precompute >= declined_isolated >= declined_direct:
        raise ValueError("the ladder of declined precompute prices is not ordered")
    if precompute <= _TIER6_REJECTED_PRECOMPUTE:
        raise ValueError("this tier must charge MORE than the rejected tier 6")
    if lanes["standalone"] <= declined_isolated:
        raise ValueError("this depth must be the WORSE standalone route")

    # DOOR 1: the fused 32,512-row call.  Executed, and exactly zero.
    fusion = fused_precompute_call(t7, WIDTH, WIDTH)
    if fusion["fused_depth"] != depth:
        raise ValueError("the fused shape does not sit at the bill's depth")
    if fusion["delta"] != 0:
        raise ValueError("the fused call is not the exact zero this tier claims")
    if fusion["split_total"] != layer2_even_rows + w_stack + precompute:
        raise ValueError("the split side of door 1 is not layer 2's own terms")

    # DOOR 2: carrying the precompute on layer 1's alphabet.  Executed, worse.
    carries = [alphabet_carry_price(t7, stage)
               for stage in sorted(_ALPHABET_ARRAYS_PER_GROUP)]
    for carry in carries:
        if carry["row_multiple_of_the_matrix"] < 2:
            raise ValueError("an alphabet cannot be smaller than its own matrix")
        if carry["worse_by"] <= 0:
            raise ValueError(f"stage {carry['stage']} is being reported open")
    cheapest_carry = min(carries, key=lambda c: c["route_total"])

    # DOOR 3: the antipodal write on the last stage.  Executed, an exact tie.
    fused_write = fused_antipodal_final_stage()
    if fused_write["delta"] != 0:
        raise ValueError("the fused terminal stage is not the exact tie claimed")

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

    # The shared-depth argmin, re-derived rather than carried as a literal.
    sweep = {d: butterfly_at_shared_depth(d) for d in (0, 1, 2, 3)}
    if min(sweep, key=lambda d: sweep[d]) != _SHARED_DEPTH:
        raise ValueError("stage sharing does not end where the bill ends")
    if sweep[_SHARED_DEPTH] != butterfly:
        raise ValueError("the swept argmin is not the butterfly this bill charges")

    relu_charged = 0
    relu_free = BASE_ROWS * WIDTH
    layer2_aux = (relu_charged + precompute + normalization
                  + butterfly + antipodal_write)
    layer2 = layer2_even_rows + w_stack + layer2_aux

    scaling_passes = (1 if layer1_normalization else 0) + (1 if normalization else 0)
    if scaling_passes != 1:
        raise ValueError("the bill must charge exactly one scaling pass")

    descriptors = frame_descriptor_table_cost(FRAMES, WIDTH, 2)
    descriptor_rung = shared_descriptor_table_price(FRAMES, WIDTH)
    if descriptor_rung["per_net_saving"] != 0:
        raise ValueError("the descriptor rung is not a suite-once-only field")

    return SuiteBill(
        strategy="the_shared_operand_axis_is_banked_to_the_flop",
        call_total=call,
        call_depth=depth,
        weight_stack=w_stack,
        weight_stack_layers=_WINOGRAD_CALLING_LAYERS,
        row_part_full=row_full,
        row_part_tail=row_tail,
        layers=LAYERS,
        layer1_butterfly=layer1_butterfly,
        layer1_normalization=layer1_normalization,
        layer1_normalization_readers=len(readers),
        layer1_shared_prologue=layer1_prologue,
        layer1_frame_element_price=_BUTTERFLY_FRAME_ELEMENT_FOLDED,
        layer1_lane=layer1_lane,
        layer1_deployed_butterfly_declined=declined_deployed,
        layer1_winograd_row_part_declined=declined_row_part,
        layer1_weight_stack_removed_tier17=0,
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
        layer2_precompute_right_stack_ridden=lanes["right_operand_stack_RIDDEN"],
        layer2_precompute_decode=lanes["decode"],
        layer2_precompute_standalone=lanes["standalone"],
        layer2_precompute_direct_declined=declined_direct,
        layer2_precompute_isolated_declined=declined_isolated,
        layer2_precompute_fused_call_declined=fusion["fused_total"],
        layer2_precompute_fusion_delta=fusion["delta"],
        layer2_alphabet_carry_declined=cheapest_carry["route_total"],
        layer2_odd_normalization=normalization,
        layer2_odd_normalization_ridden=ridden_normalization,
        layer2_odd_level1_arrays=level1,
        layer2_odd_level2_arrays=level2,
        layer2_odd_shared_prologue=prologue,
        layer2_odd_shared_depth=_SHARED_DEPTH,
        layer2_odd_frame_element_price=_BUTTERFLY_FRAME_ELEMENT_FOLDED,
        layer2_odd_butterfly=butterfly,
        layer2_antipodal_write=antipodal_write,
        layer2_antipodal_fusion_delta=fused_write["delta"],
        layer2_aux=layer2_aux,
        layer2_total=layer2,
        scaling_passes_charged=scaling_passes,
        suite_once_design_stack=design_stack,
        suite_once_frame_descriptors=descriptors,
        suite_once_descriptor_rung_NOT_CLAIMED=(
            descriptor_rung["suite_once_saving_NOT_CLAIMED"]
        ),
        suite_once=design_stack + descriptors,
        total=generic_total + layer1 + layer2,
    )


def incumbent_total() -> int:
    """Tier 19/20's bill.  This tier is DRY, so it is the same number."""
    return suite_bill_per_net().total


def deployed_operator_fallback_total() -> int:
    """The published fallback, carried so it can be compared."""
    t7 = _t7()
    bill = suite_bill_per_net()
    return (bill.total - bill.layer2_precompute
            + deployed_operator_precompute_cost(t7, WIDTH, WIDTH, WIDTH))


def tier6_rejected_total() -> int:
    """What tier 6 asked for, computed here so it can be REFUSED numerically."""
    bill = suite_bill_per_net()
    return (bill.total - bill.layer2_precompute + _TIER6_REJECTED_PRECOMPUTE)


# ---------------------------------------------------------------------------
# Executable exactness.  Every route this tier DECLINES is executed first, so
# each door is shut on cost rather than on a hidden illegality:
#   (a) the block-row identity behind the fused call;
#   (b) the alphabet identity behind the alphabet carry, at levels 1 and 2;
#   (c) the fused terminal stage, operand for operand;
#   (d) the identities the charged route rests on: the CReLU split, the phased
#       Walsh design product, and the scalar's associativity.
# Integer matrices throughout, so nothing here depends on a float convention.
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


def _sub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def _relu(A):
    return [[v if v > 0 else 0 for v in row] for row in A]


def _neg(A):
    return [[-v for v in row] for row in A]


def _scale(s, A):
    return [[s * v for v in row] for row in A]


def _wht_rows(block):
    """The deployed radix-2 stage sequence over the row axis.

    Transcribed from ``kerdock_v3_estimator.py:121-130``.
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
    """``H_width``, built the way the deployed setup builds it."""
    eye = [[1 if i == j else 0 for j in range(width)] for i in range(width)]
    return _wht_rows(eye)


def layer1_route(phase_signs, weight):
    """Layer 1, exactly as billed: a signed seed then radix-2 stages."""
    seed = [[sign * value for value in weight[j]]
            for j, sign in enumerate(phase_signs)]
    return _wht_rows(seed)


def design_block(phase_signs, hadamard):
    """The design rows frame ``s`` would have contributed: ``H diag(d_s)``."""
    return [[hadamard[i][j] * phase_signs[j] for j in range(len(phase_signs))]
            for i in range(len(hadamard))]


def level1_alphabet(M):
    """Tier 12's frame-independent arrays, in the order the ladder charges them.

    ``na`` is scratch; ``P``, ``Q``, ``R``, ``S`` are the four arrays a frame's
    stage-1 output SELECTS from.  Five ops, four readable arrays -- which is why
    ``alphabet_rows(1)`` counts four per pair and ``_LEVEL1_OPS_PER_PAIR`` is
    five.
    """
    out = []
    for t in range(len(M) // 2):
        a, b = M[2 * t], M[2 * t + 1]
        na = [-x for x in a]
        P = [x + y for x, y in zip(a, b)]
        Q = [x - y for x, y in zip(a, b)]
        R = [x + y for x, y in zip(na, b)]
        S = [x - y for x, y in zip(na, b)]
        out.append((na, P, Q, R, S))
    return out


def level2_alphabet(M):
    """Tier 13's thirty-two arrays per group of four, as sums and differences."""
    lvl1 = level1_alphabet(M)
    groups = []
    for g in range(len(M) // 4):
        first = lvl1[2 * g][1:]
        second = lvl1[2 * g + 1][1:]
        arrays = []
        for u in first:
            for v in second:
                arrays.append([x + y for x, y in zip(u, v)])
        for u in first:
            for v in second:
                arrays.append([x - y for x, y in zip(u, v)])
        if len(arrays) != _LEVEL2_ARRAYS_PER_GROUP:
            raise ValueError("the level-2 alphabet is not thirty-two arrays")
        groups.append(arrays)
    return groups


def _selfcheck() -> None:
    t7 = _t7()
    bill = suite_bill_per_net()

    # (0) THIS TIER IS DRY: THE BILL IS TIER 19/20's, TERM FOR TERM. -----------
    assert bill.total == _INCUMBENT_TOTAL, bill.total
    assert bill.layer1_total == _INCUMBENT_LAYER1_TOTAL, bill.layer1_total
    assert bill.layer2_total == _INCUMBENT_LAYER2_TOTAL, bill.layer2_total
    assert bill.layer2_aux == _INCUMBENT_LAYER2_AUX, bill.layer2_aux
    assert bill.generic_layers_total == _INCUMBENT_GENERIC_TOTAL
    assert bill.suite_once == _INCUMBENT_SUITE_ONCE, bill.suite_once
    assert bill.total == bill.generic_layers_total + bill.layer1_total \
        + bill.layer2_total
    assert bill.call_total == _CERTIFIED_CALL_FLOOR, bill.call_total
    assert bill.call_depth == 6 and bill.weight_stack_layers == 31
    assert bill.scaling_passes_charged == 1
    assert bill.layer1_normalization == 65536
    assert bill.layer2_odd_normalization == 0
    assert bill.layer2_odd_normalization_ridden == 65536
    assert bill.suite_total(1) == bill.total + bill.suite_once
    assert bill.suite_total(7) == 7 * bill.total + bill.suite_once

    # (1) THE PER-CALL FLOOR AND THE DEPTH ARGMIN, RE-DERIVED. ----------------
    #     Depth 6 minimises the call, the 15.75-tile layer objective AND layer
    #     2's 7.875-tile objective.  Brute-forced over every lawful depth.
    call_by_depth, layer_by_depth, half_by_depth = {}, {}, {}
    for levels in range(1, 9):
        block = 1 << levels
        if WIDTH % block or TILE_ROWS % block:
            continue
        stack, _g = t7.best_operand_grade(WIDTH, WIDTH, levels)
        core = t7.inplace_depth_core_cost(TILE_ROWS, WIDTH, WIDTH, levels)
        row = core - stack
        call_by_depth[levels] = core
        layer_by_depth[levels] = 63 * row + 4 * stack       # 15.75 x row, x4
        half_by_depth[levels] = 63 * row + 8 * stack        #  7.875 x row, x8
    assert min(call_by_depth, key=lambda d: call_by_depth[d]) == 6
    assert min(layer_by_depth, key=lambda d: layer_by_depth[d]) == 6
    assert min(half_by_depth, key=lambda d: half_by_depth[d]) == 6
    assert call_by_depth[6] == _CERTIFIED_CALL_FLOOR

    # (2) THE ROW LANE IS EXACTLY LINEAR IN m -- the reason door 1 is zero. ----
    unit = Fraction(bill.row_part_full, TILE_ROWS)
    for rows in (256, 512, 2048, 3072, 3584, 3840,
                 BASE_ROWS, BASE_ROWS + WIDTH, 32768, DESIGN_ROWS):
        assert Fraction(row_lane(t7, rows)) == unit * rows, rows
    assert row_lane(t7, BASE_ROWS % TILE_ROWS) == bill.row_part_tail
    assert 8 * row_lane(t7, 3584) == 7 * bill.row_part_full
    assert 4 * row_lane(t7, 3072) == 3 * bill.row_part_full
    assert row_lane(t7, WIDTH) == bill.layer2_precompute

    # (3) DOOR 1.  The fused call is legal, and it is exactly zero. -----------
    nxt = _rng(20250825)
    relu_p = _relu(_mat(12, 8, nxt))
    W0p = _mat(8, 8, nxt)
    W1h = _mat(8, 5, nxt)
    stacked = [row[:] for row in relu_p] + [row[:] for row in W0p]
    fused_out = _mm(stacked, W1h)
    assert fused_out[:12] == _mm(relu_p, W1h), "block-row identity failed on T"
    assert fused_out[12:] == _mm(W0p, W1h), "block-row identity failed on cM"

    fusion = fused_precompute_call(t7, WIDTH, WIDTH)
    assert fusion["fused_rows"] == BASE_ROWS + WIDTH == 32512
    assert fusion["depth"] == fusion["fused_depth"] == 6
    assert fusion["split_total"] == fusion["fused_total"] == 2392542832
    assert fusion["delta"] == 0
    assert fusion["contiguity_copies_the_fusion_needs"] == 65536
    # Zero on the ledger, strictly worse once the copy the shape forces is
    # charged.  Named, not netted.
    assert fusion["fused_total"] + 65536 > fusion["split_total"]

    # (4) DOOR 2.  alphabet(cM) = alphabet(W0') W1h, executed array by array. --
    cM = _mm(W0p, W1h)
    a1_left, a1_right = level1_alphabet(W0p), level1_alphabet(cM)
    assert len(a1_left) == len(a1_right) == 4
    for pair_left, pair_right in zip(a1_left, a1_right):
        for left_array, right_array in zip(pair_left, pair_right):
            assert _mm([left_array], W1h)[0] == right_array, \
                "the level-1 alphabet does not commute with W1h"
    a2_left, a2_right = level2_alphabet(W0p), level2_alphabet(cM)
    assert len(a2_left) == len(a2_right) == 2
    for group_left, group_right in zip(a2_left, a2_right):
        assert len(group_left) == _LEVEL2_ARRAYS_PER_GROUP
        for left_array, right_array in zip(group_left, group_right):
            assert _mm([left_array], W1h)[0] == right_array, \
                "the level-2 alphabet does not commute with W1h"

    # ... so the route is legal, and it loses at every stage the ladder prices.
    assert alphabet_rows(1) == 512 and alphabet_rows(2) == 2048
    assert alphabet_rows(3) == 32768
    carries = {c["stage"]: c for c in
               (alphabet_carry_price(t7, s) for s in (1, 2, 3))}
    assert carries[1]["route_total"] == 38171968
    assert carries[1]["worse_by"] == 18660000
    assert carries[2]["route_total"] == 150590720
    assert carries[2]["worse_by"] == 131078752
    assert carries[3]["route_total"] == 2409451520
    assert carries[3]["worse_by"] == 2389939552
    for stage in (1, 2, 3):
        assert carries[stage]["row_multiple_of_the_matrix"] >= 2
        assert carries[stage]["worse_by"] > 0
    assert carries[1]["charged_route"] == bill.layer2_precompute \
        + bill.layer2_odd_shared_prologue == 19511968
    # The cheapest carry is the cheapest stage, and it is still worse.
    assert bill.layer2_alphabet_carry_declined == carries[1]["route_total"]

    # (5) DOOR 3.  The fused terminal stage is an exact tie, values and ops. ---
    x = _mat(6, 4, nxt)
    y = _mat(6, 4, nxt)
    T = _mat(6, 4, nxt)
    O = [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(x, y)]
    unfused_bottom = _sub(T, O)
    fused_bottom = [[t - (a + b) for t, a, b in zip(rt, rx, ry)]
                    for rt, rx, ry in zip(T, x, y)]
    assert unfused_bottom == fused_bottom, "the fused write changes the value"
    write = fused_antipodal_final_stage()
    assert write["unfused_total"] == write["fused_total"] == 57802752
    assert write["delta"] == 0
    assert (bill.layer2_odd_butterfly - bill.layer2_odd_shared_prologue
            + bill.layer2_antipodal_write) == write["unfused_total"]

    # (6) THE SHARED-DEPTH ARGMIN, re-derived over 0..3. ----------------------
    sweep = {d: butterfly_at_shared_depth(d) for d in (0, 1, 2, 3)}
    assert sweep[0] == 74317824 and sweep[1] == 57966592
    assert sweep[2] == 50233344 and sweep[3] == 50364416
    assert min(sweep, key=lambda d: sweep[d]) == _SHARED_DEPTH == 2
    assert sweep[3] - sweep[2] == 131072
    assert sweep[2] == bill.layer2_odd_butterfly == bill.layer1_butterfly

    # (7) THE DESCRIPTOR RUNG: real, suite-once, and NOT claimed. -------------
    rung = shared_descriptor_table_price(FRAMES, WIDTH)
    assert rung["charged_suite_once"] == 64512
    assert rung["one_table_would_serve"] == 32256
    assert rung["suite_once_saving_NOT_CLAIMED"] == 32256
    assert rung["per_net_saving"] == 0
    assert bill.suite_once_frame_descriptors == 64512
    assert bill.suite_once == bill.suite_once_design_stack + 64512
    assert bill.suite_once_design_stack == 241309152

    # (8) THE IDENTITIES THE CHARGED ROUTE RESTS ON, re-run so this file stands
    #     alone.  Width 8, exact integers, the deployed stage sequence. --------
    width = 8
    H = _hadamard(width)
    signs = [1 if nxt(0, 1) else -1 for _ in range(width)]
    scalar = 3                      # stands in for c = MEAN_CHI_256 / 16
    W0 = _mat(width, width, nxt)
    W0_scaled = _scale(scalar, W0)
    W1 = _mat(width, 5, nxt)

    #  (i) the scalar's associativity -- tier 19's identity.
    assert _scale(scalar, _mm(W0, W1)) == _mm(W0_scaled, W1)

    # (ii) the design product: the butterfly IS H diag(d_s) M, at both channels.
    P = layer1_route(signs, W0_scaled)
    assert P == _mm(design_block(signs, H), W0_scaled)
    cM_full = _mm(W0_scaled, W1)
    O_full = layer1_route(signs, cM_full)
    assert O_full == _mm(design_block(signs, H), cM_full)
    assert O_full == _mm(P, W1), "the odd channel is not P W1h"

    # (iii) the CReLU split the whole of layer 2 rests on.
    top = _mm(_relu(P), W1)
    assert _mm(_relu(_neg(P)), W1) == _sub(top, O_full)

    # (iv) the odd butterfly seeded from the alphabet route would agree -- so
    #      door 2 is shut on cost, not on a wrong answer.
    for group_left, group_right in zip(level2_alphabet(W0_scaled),
                                       level2_alphabet(cM_full)):
        for left_array, right_array in zip(group_left, group_right):
            assert _mm([left_array], W1)[0] == right_array

    # (9) W0' IS READ, NEVER WRITTEN, by layer 1 -- tier 19's precondition for
    #     the second reader, re-executed. -----------------------------------
    before = [row[:] for row in W0_scaled]
    _ = layer1_route(signs, W0_scaled)
    assert W0_scaled == before, "layer 1 wrote its weight operand"

    # (10) THE CARRIED CONSERVATIVE CHOICES, counted and NOT claimed. ---------
    incumbent_fold, worst_fold = terminal_fold_bounds()
    assert incumbent_fold == 3 * WIDTH * WIDTH == 196608
    assert worst_fold == 6 * WIDTH * WIDTH == 393216
    assert worst_fold > incumbent_fold          # honest modelling RAISES it
    assert deployed_relu_writes_priced_zero(WIDTH) == 478937088
    assert bill.layer2_relu_pass == 0
    assert tier6_rejected_total() < bill.total  # cheaper, and refused
    assert deployed_operator_fallback_total() > bill.total
    assert bill.layer2_precompute_direct_declined == 33488896
    assert bill.layer2_precompute_isolated_declined == _TIER16_PRECOMPUTE_DEPTH5

    # (11) NOTHING MOVED.  The delta against the incumbent is exactly zero. ---
    assert bill.total - _INCUMBENT_TOTAL == 0
    assert incumbent_total() == _INCUMBENT_TOTAL


def main() -> None:
    bill = suite_bill_per_net()
    _selfcheck()
    print(f"strategy                  {bill.strategy}")
    print(f"suite bill, per net       {bill.total:,}")
    print(f"incumbent (tier 19/20)    {_INCUMBENT_TOTAL:,}")
    print(f"delta                     {bill.total - _INCUMBENT_TOTAL:,}   DRY")
    print()
    for key, value in bill.breakdown().items():
        print(f"  {key:<62} {value:,}")
    print()
    t7 = _t7()
    print("DOOR 1  fused 32,512-row call")
    for key, value in fused_precompute_call(t7).items():
        print(f"  {key:<52} {value}")
    print("DOOR 2  carrying the precompute on layer 1's alphabet")
    for stage in (1, 2, 3):
        print(f"  {alphabet_carry_price(t7, stage)}")
    print("DOOR 3  antipodal write fused into the odd butterfly's last stage")
    for key, value in fused_antipodal_final_stage().items():
        print(f"  {key:<52} {value}")
    print("RUNG    the second frame-descriptor table (suite-once, NOT claimed)")
    for key, value in shared_descriptor_table_price().items():
        print(f"  {key:<52} {value}")


if __name__ == "__main__":
    main()
