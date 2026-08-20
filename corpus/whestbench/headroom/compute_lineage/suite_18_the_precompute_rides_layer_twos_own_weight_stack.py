"""Suite tier 18: the precompute's right-hand operand is layer 2's own weight
matrix, so at layer 2's own depth its operand stack is an array this bill has
already built and already charged.

Tier 16 stopped pricing the odd channel's precompute ``cM = c * (W0 @ W1h)`` at
the cost model's counterfactual and started pricing it at the suite's own rule --
tier 7's call bill at the shape (256, 256, 256).  That bill picks depth 5, and at
depth 5 the precompute pays four lanes in full:

    leaves, depth 5                             16,134,720
    A-side operand stack of W0, depth 5          1,092,032
    W-side operand stack of W1h, depth 5         1,092,032
    decode, depth 5                              2,102,144
                                                ----------
    tier 16 / tier 17 carried price              20,420,928

The depth is the frozen constant.  It was chosen by minimising the call in
ISOLATION, at a moment when the file did not ask what else in the same layer
holds the same operand.  Layer 2's even channel is a Winograd call at depth 6
whose right-hand operand is ``W1h`` -- the same matrix, on the same side -- and
tier 17 kept its 1,915,152 W-side stack precisely because "layer 2 makes the
call".  Move the precompute to layer 2's depth and its W-side lane is not a
cheaper array; it is THE SAME ARRAY, already built, already paid for once.

    leaves, depth 6                             13,176,688
    A-side operand stack of W0, depth 6          1,915,152   PAID IN FULL
    W-side operand stack of W1h, depth 6                 0   RIDDEN (see below)
    decode, depth 6                              3,732,000
                                                ----------
    this tier                                   18,823,840

    layer 2 auxiliary lane      78,977,344   ->      77,380,256
    layer 2 total            2,452,696,336   ->   2,451,099,248
    suite bill, per net    144,868,745,712   -> 144,867,148,624

    (-1,597,088, or 0.00110% of the whole bill)

THE WIN IS THE SHARED ARRAY AND NOTHING ELSE, AND THAT IS SAID FIRST
====================================================================
Standing alone, depth 6 is WORSE than depth 5 at this shape:

    depth 5 standalone  20,420,928
    depth 6 standalone  20,738,992      (+318,064)

This tier therefore claims nothing about Winograd depth being better here.  It
claims that one of the four lanes is an object the bill already contains, and
that riding it is worth more than the 318,064 the deeper route costs:

    20,738,992 - 1,915,152 = 18,823,840 < 20,420,928

Both figures are computed below by ``precompute_lanes`` and asserted, and the
depth is chosen by brute force over every lawful depth under the objective that
prices the shared lane at zero -- depth 6 is the strict argmin, and it is the
argmin BECAUSE it is layer 2's depth, not by coincidence of arithmetic.

ONE SUBSTANTIVE CHANGE
======================
Exactly one term changes value and no term enters or leaves the bill.  Every
other figure is carried at tier 17's value and asserted term by term in
``_selfcheck``:

  * layer 1 entire, 50,364,416: butterfly 50,233,344 with its 688,128 prologue,
    normalization 65,536, pilot negation 65,536, and tier 17's removed W-side
    stack still absent.
  * layer 2's even-channel row part 2,371,803,840 and its W-side stack
    1,915,152, charged ONCE, exactly as tier 17 charges it.
  * layer 2's other auxiliary lanes: odd normalization 65,536, odd butterfly
    50,233,344, antipodal write 8,257,536.
  * layers 3..32, 30 x 4,745,522,832 = 142,365,684,960, W-side stacks included.
  * the two suite-once fields, 241,309,152 and 64,512, at their exact incumbent
    values and outside ``.total``.
  * the certified per-call floor, 303,096,592 at the anonymous (4096, 256, 256).

THE FROZEN CONSTANT
===================
P1 on the depth, and P2 on tier 3's licence.

Tier 3 is crowned for the rule "one W-side operand stack per LAYER, not per
tile", and its argument was never about layers: it was that fifteen and
three-quarter leaf matmuls read ONE graded transform of ONE matrix, so the
transform is built once.  The unit that rule actually identifies is the triple
(matrix, side, depth) -- tier 3 spent it on the tile axis, tier 5 spent it on the
net axis, and tier 17 spent it on the reader axis by deleting a stack whose
count of readers was zero.  This tier spends the same lemma on the last axis
left: a stack with TWO readers is still built once.

The precompute is the second reader.  It was hidden only because the file had
pinned it to a depth at which the two transforms of ``W1h`` are different
objects.  Unfreeze the depth and the second reader appears.

WHY THE TWO STACKS ARE ONE ARRAY, IN THE MODULE'S OWN TERMS
===========================================================
The right-hand operand lane of a depth-L call is
``t7.best_operand_grade(k, n, L)`` and ``t7._build_operands(rows=k, cols=n,
pattern, side="B", ...)``.  Neither takes ``m``.  The lane is a function of the
right-hand matrix, its two dimensions, the depth and the grading -- and of
nothing else.  So:

    layer 2, even channel :  (4096, 256, 256) at depth 6, right operand W1h
    the precompute        :  ( 256, 256, 256) at depth 6, right operand W1h

agree in every argument the lane depends on.  ``best_operand_grade(256, 256, 6)``
returns ``(1,915,152, frozenset())`` for both -- same price AND same grading, so
the same 7**6 blocks of 4 x 4 with the same values.  ``_selfcheck`` does not
stop at that: it runs the module's own graded recursion (``t7._encode_right``,
``t7._encode_left``, ``t7._decode``) on the same B against left operands with
three different row counts, collects the right-hand leaf blocks each time, and
asserts the three collected lists are equal element for element while all three
products are exact.  The independence from ``m`` is measured, not argued.

The two operands are the same submatrix under pruning as well, which is why the
claim does not rest on the bill's worst-case width convention.  The deployed
loop enters layer 2 with ``active = arange(width)``, so layer 2's right operand
is ``mlp.weights[1][:, next_active]`` [fold3_estimator.py:93, :115-122]; the
antipodal half is recombined as ``B = T - O`` entrywise, so ``O`` must carry the
same columns, which makes the precompute's right operand the same
``mlp.weights[1][:, next_active]``.  At the bill's full 256 they are both W1h.

EXACTNESS IDENTITY
==================
What is computed does not change; the association order inside one 256x256x256
product changes from a 5-level Winograd recursion to a 6-level one.

Write ``H`` for the normalized Walsh matrix [kerdock_v3_estimator.py:24-38, :89],
``d_s`` for frame ``s``'s phase vector, ``W0`` for the Haar-absorbed first weight
[kerdock_v3_estimator.py:162-172] and ``W1h = mlp.weights[1]``.  Tier 2's odd
channel is the butterfly on ``cM``:

    O_s = D_s (c W0 W1h) = H (d_s * (c W0 W1h))                             (1)

and this tier changes only how the 256 x 256 matrix ``M = W0 W1h`` inside (1) is
formed.  For any depth L the graded Winograd recursion computes ``A B`` exactly:

    W(A, B, L) = A B                    over the reals and over the integers   (2)

so ``W(W0, W1h, 6) = W(W0, W1h, 5) = W0 W1h`` and (1) is untouched.  (2) is
EXECUTED below at depths 1, 2 and 3, in the module's own ``_encode_left`` /
``_encode_right`` / ``_decode``, under several gradings, against a dense ``_mm``.

The layer-1 and layer-2 routes the rest of the bill rests on are re-executed for
the same reason they were in tier 17, so the moved term sits inside a route that
still computes what the champion computes:

    P_s = D_s W0 = (H diag(d_s)) W0 = H (d_s * W0)                          (3)
    relu(-P) W1h = (relu(P) - P) W1h = T - O                                (4)

Four claims, all run rather than asserted:

(I)   THE RIGHT-HAND LANE DOES NOT DEPEND ON ``m``.  Measured by collecting the
      right-hand leaf blocks of the module's own recursion at three row counts.
(II)  THE A-SIDE LANE IS A DIFFERENT MAP AND IS PAID IN FULL.  ``_encode_left``
      and ``_encode_right`` are exhibited producing different operand sets from
      the same quadrants; the 1,915,152 A-side lane is inside the charge.
(III) DEPTH 6 IS THE ARGMIN OF THE SHARED-LANE OBJECTIVE AND NOT OF THE
      STANDALONE ONE.  Both sweeps are brute-forced; the standalone argmin is
      depth 5 and is stated as the price this tier pays to reach the shared lane.
(IV)  EVERYTHING ELSE IS TIER 17's, TERM BY TERM.

WHAT WAS REJECTED AS TIER 6, AND WHY THIS IS THE OPPOSITE OF IT
===============================================================
Tier 6 also asked for a waived operand lane on this product and was REJECTED.
Tier 16 recorded its three defects verbatim; this tier is built to cure each one,
and each cure is asserted rather than described.

  * "IT RODE THE WRONG SIDE."  Tier 6 rode the precompute's A-side lane of W0
    against a W-SIDE stack.  This tier rides the W-SIDE lane of W1h against a
    W-SIDE stack of W1h, and PAYS the A-side lane of W0 in full at 1,915,152.
    Asserted: the ridden lane and the charged layer-2 lane are the same
    ``best_operand_grade(k, n, L)`` call with the same arguments and the same
    grading, while the A-side lane is charged, not waived.
  * "IT RODE A STACK THAT NO LONGER EXISTS."  Tier 6 pointed at layer 1, which
    tier 14 proved issues no Winograd call and tier 17 stripped of its stack
    entirely.  This tier points at layer 2, whose call tier 17 explicitly kept
    the stack for -- its breakdown key is
    ``layer2_weight_side_stack_KEPT_THE_CALL_IS_MADE``.  Asserted: layer 1's
    stack is absent from this bill and layer 2's is present exactly once.
  * "IT RODE ACROSS DEPTHS."  Tier 6 wanted a depth-5 lane and pointed at
    depth-6 stacks.  This tier moves the precompute TO depth 6 and pays the
    318,064 that move costs.  Asserted: the depth of the ridden stack and the
    depth of the riding call are read from the same module call and are equal.

Tier 6 asked for 18,236,864.  This tier charges 18,823,840 -- 586,976 more --
and the difference is that tier 6 waived two lanes at a depth where neither was
built, while this tier waives one lane at the depth where it is.

DISJOINTNESS, SO NOTHING IS DEDUCTED TWICE
==========================================
  * From tier 3.  Its per-layer stack count is untouched: still 31 calling
    layers at 1,915,152, still 59,369,712 in the bill, asserted.  The precompute
    is not a thirty-second charge that got deleted -- it never was one; the
    charge that changes is the precompute's OWN lane, which tier 16 added as a
    new line and this tier zeroes because the object is already on the ledger.
  * From tier 16.  Its rule -- price the precompute at the suite's own call bill
    rather than at ``direct_cost`` -- is not weakened but applied one step
    further.  The declined counterfactual 33,488,896 is carried and asserted, and
    this tier is asserted to beat it by more than tier 16 did.
  * From tier 17.  Its removed layer-1 W-side stack stays removed; asserted that
    the bill contains 31 stacks, not 32, and that layer 1's lane is a butterfly.
    Its published next rung is exactly this tier's move; its predicted figure,
    18,823,840, is reproduced independently here and asserted equal.
  * From tiers 8, 9, 10, 11, 12, 13.  All act on the odd channel's BUTTERFLY,
    whose operand is ``cM``.  This tier acts on how ``cM`` is FORMED.  The
    butterfly 50,233,344, its prologue 688,128, its normalization 65,536 and the
    antipodal write 8,257,536 are asserted unchanged.
  * From tiers 14 and 15.  They act on layer 1; layer 1's every term is asserted
    equal to theirs.
  * From tier 5.  Its 241,309,152 design stack stays a suite-once field, carried
    at its exact value, outside ``.total`` and unclaimed.
  * From the call ladder (tiers 8-10 of the prior ladder).  No within-call
    schedule is reweighted.  The per-call floor is re-derived from tier 7 and
    asserted at 303,096,592.  The precompute is a call whose depth is chosen by
    the SUITE's objective rather than the anonymous one; its internal schedule at
    that depth is the module's own, lane for lane, grading for grading.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * The A-side lane of W0, 1,915,152, is paid in full even though it is
    numerically equal to the ridden lane.  It is a different map on a different
    matrix and it is charged.  Refusing this is what kills tier 6.
  * The odd channel's normalization, 65,536, is left standing although the
    precompute's left operand could be the already-scaled ``c W0`` layer 1
    builds; that is priced below and left for tier 19 (see NEXT RUNG).
  * The decode lane rises from 2,102,144 to 3,732,000 and is paid in full; no
    decode is shared with anything.
  * The suite-once design stack, orphaned since tier 14, is still not removed:
    it sits outside ``.total`` and cannot move the fitness.
  * The thirty generic layers keep the antipodal half at full price; the
    ledger-free ReLU writes stay priced at zero; the terminal fold stays
    unmodelled.  All three are counted below and none is claimed.
  * ``.total`` remains the marginal per-net bill; no suite size is assumed.

THE NEXT RUNG, PRICED AND LEFT STANDING
=======================================
Tier 10 folds the design scalar ``c = MEAN_CHI_256 / 16`` onto the 256 x 256
weight matrix, so layer 1 materializes ``W0' = c W0`` at a cost of 65,536 and
runs its butterfly on it [kerdock_v3_estimator.py:133, :144].  The odd channel
needs ``cM = c (W0 W1h) = W0' W1h``.  If the precompute's left operand is the
``W0'`` layer 1 has already built, ``cM`` comes out of the product already
scaled and the odd channel's own normalization pass has nothing to scale.  That
is 65,536, computed below by ``next_rung_odd_normalization_price()`` and printed
beside the claim.  It is NOT taken: LAW 5 allows one change, and it is a second
riding argument on a second array, which deserves its own adjudication.

DOORS THAT STAY CLOSED
======================
Two are NEW, probed by this tier's own search and closed with arithmetic; the
rest are re-executed from the incumbent so the next tier does not pay for them
twice.

  * NEW -- DOES THE A-SIDE LANE RIDE ANYTHING TOO?  No, and the boundary is
    exact.  A stack is ridable exactly when some charged call builds it.  The
    A-side lane wanted here is the (256, 256) A-side transform of ``W0'`` at
    depth 6.  The only calls in the bill are the 31 layer calls and this one;
    every layer call's A-side operand is an activation block of 4096 or 3584
    rows, never a 256 x 256 weight, and layer 1 -- the one place ``W0'`` is
    touched -- issues no Winograd call at all (tier 14, re-asserted).  So the
    A-side lane rides nothing and is paid.  SHUT.  Executed: the A-side operand
    shape of every charged call is enumerated and none is (256, 256).
  * NEW -- IS THERE A THIRD READER, OR A CHEAPER DEPTH GIVEN ONE?  No.  The
    shared-lane objective ``leaves(L) + A(L) + decode(L) + [L != 6] * B(L)`` is
    brute-forced over every lawful depth: 26,128,384 / 23,417,856 / 21,447,424 /
    20,420,928 / 18,823,840 / 23,141,124 / 28,955,077 at depths 2..8.  Depth 6
    is the strict argmin and it is the only depth at which the bracket vanishes.
    A hypothetical depth-5 partner would give 19,328,896, which is worse than
    18,823,840 anyway -- so even if the file later grows a depth-5 call, this
    rung does not regress.  SHUT.
  * CARRIED -- THE WINOGRAD DEPTH OF THE LAYER CALLS UNDER TIER 3's AMORTIZED
    OBJECTIVE.  Depth 6 minimises both ``row(L)`` and ``15.75 * row(L) +
    stack(L)``; brute-forced below over every lawful depth.  SHUT.
  * CARRIED -- THE 15.75 TILE FRACTION.  The row lane is exactly linear in ``m``:
    ``4 * row(3072) == 3 * row(4096)`` and ``8 * row(3584) == 7 * row(4096)``,
    executed to the FLOP.  SHUT.
  * CARRIED -- THE TERMINAL FOLD.  Modelling layers 30..32 honestly RAISES the
    bill, to at most twice the incumbent's 196,608 of width work.  Both bounds
    executed.
  * CARRIED -- PRUNING.  ``active`` is a function of the net's own weights and
    its worst case is the full 256 [fold3_estimator.py:93-123].
  * CARRIED -- BUTTERFLY CREDIT AT LAYERS 2..32.  The butterfly exists because
    every entry of a design row has the same absolute value; ``relu(p)`` does
    not, and ``_selfcheck`` exhibits two entries of it with different absolute
    values.
  * CARRIED -- THE LEDGER-FREE ReLU WRITES, 478,937,088, priced at zero at all 32
    layers; re-billing them consistently would RAISE the bill.  Counted, not
    claimed.

f32 STATUS: REASSOCIATION ONLY, THE CLASS TIER 16 ALREADY ADJUDICATED FOR THIS
EXACT PRODUCT.  NO REPRICING, NO FLAG.
==============================================================================
No value is approximated, no rank is reduced, no term any operation reads is
dropped, no summation inside any certified call is reordered.  Every op counted
is one f32 multiply, add, subtract or copy priced at 1, the unit the call bill
uses.  The one thing that changes is the depth of the Winograd recursion on a
single 256 x 256 x 256 product:

  * The rank of the 2 x 2 block product is 7 in the deployed operator
    [row_blocked_winograd.py:110-116] and 7 here.  Depth changes how many times
    that identity is applied, never the identity.  The monomial law is untouched:
    no product of fewer than 7 leaves appears at any level.
  * Depth 6 is not a new arithmetic for this bill.  It is the depth of all
    thirty-one layer products already in it, including the (4096, 256, 256) call
    whose 303,096,592 is the certified floor.  This tier moves one product ONTO
    that arithmetic, not off it -- the schedule becomes MORE uniform in f32 terms
    than tier 16's, which was the file's only depth-5 object.
  * Over the reals and over the integers the depth-5 and depth-6 routes are the
    same map; ``_selfcheck`` runs the module's own recursion at three depths and
    several gradings and gets the dense product every time.
  * Over f32 the two differ in the last bits, in the same direction and by the
    same mechanism as the thirty-one layer products already do against a direct
    GEMM.  Tier 16 adjudicated exactly this exposure for exactly this product and
    took no flag; this tier reduces it rather than adding to it.

No f32 repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A metered win is repaid in wall time when it forces small kernels, extra passes,
new dispatch, or new residency.  Here the meter and the clock move together on
three of the four axes and the fourth is named with its number.

  * LAUNCH COUNT FALLS BY THREE.  Tier 16 reported its route honestly as 16
    launches: five A-side passes, five B-side passes, one batched matmul, five
    decode passes.  This route is six A-side passes, ZERO B-side passes -- the
    stack is already resident for layer 2's own tiles -- one batched matmul and
    six decode passes: 13.  The B-side lane disappears from the dispatch stream,
    not just from the ledger, because the array it would build is the one the
    even channel just built.
  * GRANULARITY BECOMES UNIFORM WITH THE REST OF THE NET.  Tier 16's leaf blocks
    were 8 x 8, the only depth-5 blocks in a schedule whose thirty-one other
    products all run 4 x 4 leaves.  This tier's leaves are 4 x 4: one leaf-block
    shape for every matmul in the net, so the batched kernel is the SAME kernel,
    with no depth-5 specialization to compile, tune or keep warm.  The precompute
    stops being the odd one out.
  * MULTIPLY TRAFFIC FALLS AGAIN.  Direct GEMM: 16,777,216 multiplies.  Tier 16's
    depth 5: ``7**5 * 8**3 = 8,605,184``.  This tier's depth 6:
    ``7**6 * 4**3 = 7,529,536``.  Down 12.5% against the incumbent and 2.23x
    against the counterfactual.
  * RESIDENCY RISES BY 2.16 MB, AND HERE IS THE HONEST COUNT.  Tier 16 held three
    depth-5 objects of ``7**5 * 64`` f32 = 4.30 MB each, 12.9 MB peak.  This tier
    holds an A-stack and a leaf-product buffer of ``7**6 * 16`` f32 = 7.53 MB
    each = 15.06 MB, and no B-stack of its own.  The increment is 2.16 MB against
    a workspace that already holds ``self._activation`` at 64,512 x 256 f32 =
    66 MB [kerdock_v3_estimator.py:57-61].  The direction is up on this axis
    alone, it is named, and it is not claimed as a saving.
  * ORDERING IS FREE AND STATED.  The shared stack must be live when the
    precompute's leaf matmul runs.  Both consumers sit inside layer 2 and neither
    constrains the other: build the B-stack of ``W1h`` once, run the eight
    even-channel tile matmuls, run the precompute's matmul, free the stack, then
    build the odd channel's alphabet.  No lane is kept alive across a layer
    boundary and no new peak is created beyond the 15.06 MB above.
  * FLAT IN THE SUITE SIZE.  One net or a thousand, each pays 1,597,088 less; no
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
# Tier 16's rule at the module's own isolated argmin, carried by tier 17.
_TIER16_PRECOMPUTE_DEPTH5 = 20420928

# Tier 17's published figures, carried so every one of them can be re-asserted.
_INCUMBENT_TOTAL = 144868745712
_INCUMBENT_LAYER1_TOTAL = 50364416
_INCUMBENT_LAYER2_TOTAL = 2452696336
_INCUMBENT_LAYER2_AUX = 78977344
_INCUMBENT_GENERIC_TOTAL = 142365684960
_INCUMBENT_SUITE_ONCE = 241373664

# The number of layers that DO issue a Winograd call: 2..32 inclusive.
_WINOGRAD_CALLING_LAYERS = LAYERS - 1


def _t7():
    spec = importlib.util.spec_from_file_location("t18base", _T7_PATH)
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
    """The depth at which every charged Winograd call in this bill runs.

    Read back from the module rather than written down, because the whole tier
    turns on the ridden stack and the riding call sitting at the SAME depth.
    """
    return _selected_levels(
        t7.inplace_verbatim_leaves_candidate_bill(m, k, n).strategy
    )


def weight_side_stack_cost(t7, k: int = WIDTH, n: int = WIDTH,
                           m: int = TILE_ROWS) -> int:
    """The m-independent lane of the crowned call bill: the W-side (k, n) stack.

    Tier 3's term.  ``best_operand_grade`` takes only ``(k, n, levels)``: the
    lane is a function of the right-hand matrix, its two dimensions, the depth
    and the grading, and of nothing else.  That is why a second call on the same
    matrix at the same depth reads this array instead of building another.
    """
    levels = layer_call_depth(t7, m, k, n)
    cost, _grade = t7.best_operand_grade(k, n, levels)
    return cost


def weight_side_stack_grade(t7, k: int = WIDTH, n: int = WIDTH,
                            m: int = TILE_ROWS):
    """The (cost, grading) pair of the same lane, so identity can be asserted."""
    return t7.best_operand_grade(k, n, layer_call_depth(t7, m, k, n))


# ---------------------------------------------------------------------------
# THE ONE CHANGE: the precompute runs at the depth of the call that already
# builds its right-hand operand stack, and does not build a second copy.
# ---------------------------------------------------------------------------


def precompute_lanes(t7, k: int = WIDTH, n: int = WIDTH,
                     m: int = WIDTH) -> dict:
    """``cM``'s four lanes at layer 2's depth, with the W-side lane ridden.

    The depth is not this tier's constant: it is read back from the layer call
    whose stack is ridden, so the two can never drift apart.
    """
    levels = layer_call_depth(t7, TILE_ROWS, k, n)
    block = 1 << levels
    if m % block or k % block or n % block:
        raise ValueError("the precompute's shape does not carry layer 2's depth")
    leaves = 7 ** levels * t7.direct_cost(m // block, k // block, n // block)
    left, left_grade = t7.best_operand_grade(m, k, levels)
    right, right_grade = t7.best_operand_grade(k, n, levels)
    decode, _ = t7.best_decode_grade(m, n, levels)

    # The ridden object, named by the SAME module call the layer bill makes.
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
    """cM's price: layer 2's depth, with the W-side lane already on the ledger."""
    return precompute_lanes(t7, k, n, m)["total"]


def precompute_shared_objective(t7, levels: int, k: int = WIDTH,
                                n: int = WIDTH, m: int = WIDTH) -> int:
    """What the precompute costs at ``levels``, pricing a ridable lane at zero.

    The lane is ridable exactly when ``levels`` is the depth of a call this bill
    already charges -- which is layer 2's depth and no other.
    """
    block = 1 << levels
    if m % block or k % block or n % block:
        raise ValueError(f"{levels} levels do not divide the precompute's shape")
    leaves = 7 ** levels * t7.direct_cost(m // block, k // block, n // block)
    left, _ = t7.best_operand_grade(m, k, levels)
    right, _ = t7.best_operand_grade(k, n, levels)
    decode, _ = t7.best_decode_grade(m, n, levels)
    ridable = (levels == layer_call_depth(t7, TILE_ROWS, k, n))
    return leaves + left + decode + (0 if ridable else right)


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


def next_rung_odd_normalization_price() -> int:
    """The next rung, priced and NOT taken.

    Layer 1 already materializes ``W0' = c W0`` (tier 10, 65,536).  A precompute
    whose left operand is ``W0'`` yields ``cM`` already scaled, leaving the odd
    channel's normalization pass with nothing to scale.  Left for its own tier:
    it is a second riding argument on a second array.
    """
    return normalization_cost(WIDTH, WIDTH)


# ---------------------------------------------------------------------------
# Carried machinery.  Every function below is tier 17's, unchanged, so the terms
# it produces can be asserted equal to tier 17's term by term.
# ---------------------------------------------------------------------------


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

    Tier 2's shape [suite_02:277-289], carried verbatim through tiers 14..17 and
    unchanged here so the five files' numbers are directly comparable.
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

    Orphaned since tier 14 and deliberately NOT removed: it sits outside
    ``.total`` and cannot move the fitness in either direction.
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
    call_depth: int
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
            "winograd_depth_of_every_charged_call": self.call_depth,
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
            "layer2_precompute_lane_A_side_stack_of_W0_PAID_IN_FULL":
                self.layer2_precompute_left_stack,
            "layer2_precompute_lane_W_side_stack_of_W1h_RIDDEN_CHARGED_AT_LAYER_2":
                self.layer2_precompute_right_stack_ridden,
            "layer2_precompute_lane_decode": self.layer2_precompute_decode,
            "layer2_precompute_W0_W1h": self.layer2_precompute,
            "layer2_precompute_STANDALONE_AT_THIS_DEPTH_worse_by_318064":
                self.layer2_precompute_standalone,
            "layer2_precompute_ISOLATED_ARGMIN_DEPTH5_DECLINED":
                self.layer2_precompute_isolated_declined,
            "layer2_precompute_DIRECT_COUNTERFACTUAL_DECLINED":
                self.layer2_precompute_direct_declined,
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
            "design_side_stack_ORPHANED_but_OUTSIDE_total_and_KEPT":
                self.suite_once_design_stack,
            "frame_descriptor_tables_TWO_charged_ONCE_to_the_suite":
                self.suite_once_frame_descriptors,
            "total": self.total,
        }


def _layer2_auxiliary_terms(t7) -> tuple:
    """Layer 2's non-matmul terms.  Only the precompute moves."""
    precompute = precompute_cost(t7, WIDTH, WIDTH, WIDTH)             # 18,823,840
    normalization = normalization_cost(WIDTH, WIDTH)                  #     65,536
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                              pingpong=True, shared_depth=_SHARED_DEPTH)
    antipodal_write = BASE_ROWS * WIDTH                               #  8,257,536
    return precompute, normalization, butterfly, antipodal_write


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill: a W-side operand stack is built once per
    (matrix, side, depth), so the precompute reads layer 2's rather than
    building a second copy of it at a depth of its own."""
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

    # --- layer 1: tier 17's, carried verbatim.  No Winograd call, no stack. ---
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
    layer1 = layer1_lane + negation

    # --- layer 2: THE ONE CHANGE lives in the auxiliary lane.  The even
    #     channel's stack is charged exactly once, here, and the precompute
    #     reads it instead of building a second graded transform of W1h. -------
    layer2_even_rows = base_rows_part
    lanes = precompute_lanes(t7, WIDTH, WIDTH, WIDTH)
    if lanes["levels"] != depth:
        raise ValueError("the precompute is not at the depth of the ridden stack")
    if lanes["right_operand_stack_RIDDEN"] != w_stack:
        raise ValueError("the ridden lane is not layer 2's charged W-side stack")
    precompute, normalization, butterfly, antipodal_write = (
        _layer2_auxiliary_terms(t7)
    )
    declined_direct = declined_direct_precompute_cost(WIDTH, WIDTH, WIDTH)
    declined_isolated = declined_isolated_precompute_cost(t7, WIDTH, WIDTH, WIDTH)
    if precompute >= declined_isolated >= declined_direct:
        raise ValueError("the ladder of declined precompute prices is not ordered")
    if precompute <= _TIER6_REJECTED_PRECOMPUTE:
        raise ValueError("this tier must charge MORE than the rejected tier 6")
    if lanes["standalone"] <= declined_isolated:
        raise ValueError("this depth must be the WORSE standalone route")
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
        strategy="the_precompute_rides_layer_twos_own_weight_stack",
        call_total=call,
        call_depth=depth,
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
    """Tier 17's bill, reconstructed from this file's own terms."""
    bill = suite_bill_per_net()
    return (bill.total - bill.layer2_precompute
            + bill.layer2_precompute_isolated_declined)


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


def next_rung_total() -> int:
    """What the next rung would reach.  Named, priced, NOT claimed."""
    bill = suite_bill_per_net()
    return bill.total - next_rung_odd_normalization_price()


# ---------------------------------------------------------------------------
# Executable exactness.  The claims are run, not asserted:
#   (a) the right-hand operand lane of the module's own graded recursion does
#       not depend on the left operand's row count -- the whole tier;
#   (b) the graded recursion at any depth and any grading IS the product;
#   (c) the A-side and W-side transforms are different maps (tier 6's defect 1);
#   (d) the ridden stack and the riding call sit at the same depth, read from
#       the same module call (tier 6's defect 3);
#   (e) layer 1 has no stack to ride and never did (tier 6's defect 2);
#   (f) depth 6 is the argmin of the shared objective and NOT of the standalone
#       one, and the whole delta is 1,597,088;
#   (g) tier 17's route still closes: layer 1's butterfly, tier 10's folding,
#       tier 8's CReLU identity;
#   (h) every other term is tier 17's, term by term;
#   (i) the carried closed doors are re-priced and NOT claimed.
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


def _wht_rows(block):
    """The deployed radix-2 stage sequence over the row axis.

    Transcribed from ``kerdock_v3_estimator.py:134-143``.
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


def _graded_core(t7, A, B, pa, pb, pc, right_leaves, counters):
    """``t7._alg`` verbatim, with the right-hand leaf operands recorded.

    Every arithmetic step is the module's own: ``_quads``, ``_encode_left``,
    ``_encode_right``, ``_decode``, ``_join``, ``_plain``.  The only addition is
    that the right-hand operand reaching each leaf is kept, so the claim "the
    W-side lane does not depend on the left operand's row count" can be MEASURED
    by running this at several row counts and comparing the recordings.
    """
    if not pa:
        right_leaves.append([row[:] for row in B])
        return t7._plain(A, B)
    left, left_arith = t7._encode_left(t7._quads(A), pa[0])
    right, right_arith = t7._encode_right(t7._quads(B), pb[0])
    counters["left"] += sum(len(x) * len(x[0]) for x in left_arith)
    counters["right"] += sum(len(x) * len(x[0]) for x in right_arith)
    M = [_graded_core(t7, left[i], right[i], pa[1:], pb[1:], pc[1:],
                      right_leaves, counters) for i in range(7)]
    return t7._join(t7._decode(M, pc[0], counters))


def graded_route(t7, a, b, pa, pb, pc, right_leaves, counters, psi):
    """The module's whole graded schedule: Psi in, recursion, Psi inverse out.

    This is ``t7.verify_schedule``'s own composition
    [tier_07:1037-1045], run here so the W-side lane can be watched.  Note the
    two places the right-hand operand is touched -- ``_psi(b, PHI_B, pb, ...)``
    and ``_encode_right`` -- take ``b`` and ``pb`` and no row count at all.
    """
    at = t7._psi(a, t7.PHI_A, pa, psi["a"])
    bt = t7._psi(b, t7.PHI_B, pb, psi["b"])
    ct = _graded_core(t7, at, bt, pa, pb, pc, right_leaves, counters)
    return t7._psi_inverse(ct, t7._inverse(t7.PHI_C), pc, psi["c"])


def _selfcheck() -> None:
    t7 = _t7()
    bill = suite_bill_per_net()
    nxt = _rng(20260818)

    # ---- 1. THE W-SIDE LANE DOES NOT DEPEND ON m.  THIS IS THE TIER. ------
    #     Same B, same grading, three different left-operand row counts: the
    #     recorded right-hand leaf blocks must be equal element for element, and
    #     the right-lane write count must be identical.  If the lane depended on
    #     m in any way, this is where it would show.
    for levels in (1, 2, 3):
        side = 1 << levels
        for pattern in ([True] * levels, [False] * levels,
                        [(j % 2 == 0) for j in range(levels)]):
            b = _mat(side, side, nxt)
            reference = None
            for multiple in (1, 2, 3):
                a = _mat(side * multiple, side, nxt)
                leaves, counters = [], {"left": 0, "right": 0, "decode": 0}
                psi = {"a": [0], "b": [0], "c": [0]}
                product = graded_route(t7, a, b, list(pattern), list(pattern),
                                       list(pattern), leaves, counters, psi)
                assert product == _mm(a, b), (
                    f"the graded route at depth {levels} is not the product")
                assert len(leaves) == 7 ** levels
                measured = (leaves, counters["right"], psi["b"][0])
                if reference is None:
                    reference = measured
                else:
                    assert measured == reference, (
                        "the W-side lane changed with the left operand's rows")
                #     and the A-side lane DOES depend on m, which is why it is
                #     paid in full rather than ridden.
                assert counters["left"] == reference[1] * multiple
                assert psi["a"][0] == reference[2] * multiple

    # ---- 2. THE A-SIDE AND W-SIDE TRANSFORMS ARE DIFFERENT MAPS. ----------
    quads = [_mat(2, 2, nxt) for _ in range(4)]
    for alt in (True, False):
        left_set, _ = t7._encode_left(quads, alt)
        right_set, _ = t7._encode_right(quads, alt)
        assert left_set != right_set, (
            "the two operand transforms coincide; tier 6's waiver would live")

    # ---- 3. THE RIDDEN STACK AND THE RIDING CALL ARE ONE OBJECT. ----------
    lanes = precompute_lanes(t7, WIDTH, WIDTH, WIDTH)
    assert bill.call_depth == 6 == lanes["levels"], "the depths must be equal"
    assert lanes["levels"] == layer_call_depth(t7, TILE_ROWS, WIDTH, WIDTH)
    assert (t7.best_operand_grade(WIDTH, WIDTH, bill.call_depth)
            == weight_side_stack_grade(t7, WIDTH, WIDTH, TILE_ROWS)
            == (1915152, frozenset()))
    assert bill.layer2_precompute_right_stack_ridden == bill.weight_stack == 1915152
    #     The tail call rides it too: same depth, same core widths.
    tail = t7.inplace_verbatim_leaves_candidate_bill(BASE_ROWS % TILE_ROWS,
                                                     WIDTH, WIDTH)
    assert _selected_levels(tail.strategy) == bill.call_depth
    assert tail.core_k == WIDTH and tail.core_n == WIDTH

    # ---- 4. LAYER 1 HAS NO STACK TO RIDE (tier 6's second defect). --------
    assert bill.layer1_weight_stack_removed_tier17 == 0
    assert bill.layer1_total == (bill.layer1_lane + bill.layer1_negation)
    assert bill.weight_stack_layers == 31 == LAYERS - 1
    charged = bill.weight_stack_layers * bill.weight_stack
    assert charged == 59369712 == (LAYERS - 2) * bill.weight_stack + bill.weight_stack
    #     No charged call has a 256 x 256 A-side operand, so the A lane rides
    #     nothing and is paid: the A-side shapes in the bill are the tiles only.
    a_side_shapes = {(TILE_ROWS, WIDTH), (BASE_ROWS % TILE_ROWS, WIDTH)}
    assert (WIDTH, WIDTH) not in a_side_shapes
    assert lanes["left_operand_stack"] == 1915152
    assert lanes["left_operand_stack"] in (bill.layer2_precompute
                                           - lanes["leaves"] - lanes["decode"],)

    # ---- 5. THE DEPTH IS THE ARGMIN OF THE SHARED OBJECTIVE, NOT THE PLAIN
    #        ONE, AND THE WHOLE DELTA IS 1,597,088. -------------------------
    shared_sweep, plain_sweep = {}, {}
    for levels in range(2, 9):
        if WIDTH % (1 << levels):
            continue
        shared_sweep[levels] = precompute_shared_objective(t7, levels)
        plain_sweep[levels] = t7.inplace_depth_core_cost(WIDTH, WIDTH, WIDTH,
                                                         levels)
    assert min(shared_sweep, key=shared_sweep.get) == 6
    assert min(plain_sweep, key=plain_sweep.get) == 5
    assert shared_sweep[6] == 18823840 == bill.layer2_precompute
    #     Depth 6 is the ONLY depth whose W-side bracket vanishes: at every
    #     other depth the shared objective is the full standalone bill.
    assert all(shared_sweep[L] == plain_sweep[L]
               for L in shared_sweep if L != 6)
    #     And even a HYPOTHETICAL depth-5 partner would lose, so this rung does
    #     not regress if the file later grows a depth-5 call.
    hypothetical_depth5 = plain_sweep[5] - t7.best_operand_grade(WIDTH, WIDTH,
                                                                 5)[0]
    assert hypothetical_depth5 == 19328896 > shared_sweep[6]
    assert plain_sweep[5] == 20420928 == bill.layer2_precompute_isolated_declined
    assert plain_sweep[6] == 20738992 == bill.layer2_precompute_standalone
    assert plain_sweep[6] - plain_sweep[5] == 318064, (
        "the price this tier pays to reach the shared lane")
    assert plain_sweep[5] - shared_sweep[6] == 1597088
    assert bill.layer2_precompute_leaves == 13176688 == 7 ** 6 * t7.direct_cost(
        4, 4, 4)
    assert bill.layer2_precompute_decode == 3732000 == t7.best_decode_grade(
        WIDTH, WIDTH, 6)[0]
    assert (bill.layer2_precompute_leaves + bill.layer2_precompute_left_stack
            + bill.layer2_precompute_decode) == bill.layer2_precompute
    assert incumbent_total() == _INCUMBENT_TOTAL
    assert incumbent_total() - bill.total == 1597088
    assert bill.total == 144867148624
    #     Refused numerically: tier 6, the direct counterfactual, the deployed
    #     operator's own one-level bill.
    assert bill.layer2_precompute > _TIER6_REJECTED_PRECOMPUTE
    assert bill.layer2_precompute - _TIER6_REJECTED_PRECOMPUTE == 586976
    assert bill.total > tier6_rejected_total()
    assert bill.layer2_precompute_direct_declined == 33488896
    assert bill.total < deployed_operator_fallback_total()

    # ---- 6. TIER 17's ROUTE STILL CLOSES, EXECUTED NOT INHERITED. ---------
    for width in (4, 8, 16):
        hadamard = _hadamard(width)
        w0 = _mat(width, width, nxt)
        for _frame in range(3):
            signs = [1 if nxt(0, 1) else -1 for _ in range(width)]
            routed = layer1_route(signs, w0)
            assert routed == _mm(design_block(signs, hadamard), w0), (
                "the butterfly does not reproduce the design row product")
            scaled = [[3 * v for v in row] for row in w0]
            assert layer1_route(signs, scaled) == [
                [3 * v for v in row] for row in routed]
    assert layer1_route.__code__.co_argcount == 2
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
    #     and the odd channel runs on M = W0 @ W1, the matrix this tier reprices
    assert layer1_route(signs, _mm(w0, w1)) == o

    # ---- 7. EVERY OTHER TERM IS TIER 17's, TERM BY TERM. ------------------
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
    assert bill.layer1_total == _INCUMBENT_LAYER1_TOTAL == 50364416
    assert bill.layer2_even_rows == 2371803840
    assert bill.layer2_odd_normalization == 65536
    assert bill.layer2_odd_level1_arrays == 163840
    assert bill.layer2_odd_shared_prologue == 688128
    assert bill.layer2_odd_butterfly == 50233344
    assert bill.layer2_antipodal_write == 8257536
    assert bill.layer2_relu_pass == 0
    assert bill.layer2_aux == 77380256 == _INCUMBENT_LAYER2_AUX - 1597088
    assert bill.layer2_total == 2451099248 == _INCUMBENT_LAYER2_TOTAL - 1597088
    assert bill.suite_once_design_stack == 241309152
    assert bill.suite_once_frame_descriptors == 64512 == 2 * FRAMES * WIDTH
    assert bill.suite_once == _INCUMBENT_SUITE_ONCE
    assert bill.total == (bill.generic_layers_total + bill.layer1_total
                          + bill.layer2_total)

    # ---- 8. CARRIED DOOR: THE LAYER DEPTH IS STILL THE ARGMIN UNDER TIER 3.
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
    assert bill.layer2_even_rows == 7 * bill.row_part_full + bill.row_part_tail
    assert bill.generic_layer - bill.weight_stack == 15 * bill.row_part_full + (
        bill.row_part_full * 3 // 4)
    assert bill.row_part_full + bill.weight_stack == bill.call_total

    # ---- 10. CARRIED DOORS THAT WOULD RAISE THE BILL. ---------------------
    incumbent_fold, honest_fold = terminal_fold_bounds()
    assert incumbent_fold == 196608 and honest_fold == 2 * incumbent_fold
    assert deployed_relu_writes_priced_zero(WIDTH) == 478937088
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
    assert next_rung_odd_normalization_price() == 65536
    assert bill.suite_total(1) == bill.total + bill.suite_once
    assert bill.suite_total(1000) == 1000 * bill.total + bill.suite_once
    assert bill.amortized_numerator(4) == (bill.suite_total(4), 4)
    #     Nothing about the certified per-call floor moved.
    assert t7.inplace_verbatim_leaves_candidate_bill(
        TILE_ROWS, WIDTH, WIDTH).total == 303096592


if __name__ == "__main__":
    _selfcheck()
    b = suite_bill_per_net()
    for key, value in b.breakdown().items():
        print(f"{key:<70} {value:>18,}")
    print(f"{'TOTAL (per net)':<70} {b.total:>18,}")
    print(f"{'incumbent (tier 17)':<70} {incumbent_total():>18,}")
    print(f"{'delta':<70} {incumbent_total() - b.total:>18,}")
    print(f"{'next rung (odd normalization), NOT claimed':<70} "
          f"{next_rung_total():>18,}")
    print(f"{'refused: tier 6 (REJECTED)':<70} {tier6_rejected_total():>18,}")
    print(f"{'fallback: deployed operator, one level':<70} "
          f"{deployed_operator_fallback_total():>18,}")
