"""Suite tier 19: the odd channel's normalization pass has nothing to scale,
because the matrix its precompute multiplies is the scaled ``W0'`` layer 1
already builds and this bill already charges.

Tier 18 moved the odd channel's precompute ``cM = c * (W0 @ W1h)`` onto layer
2's own Winograd depth so its right-hand operand stack is layer 2's array rather
than a second copy.  It left one term standing and said so on a line of its own
[suite_18 docstring, "THE NEXT RUNG, PRICED AND LEFT STANDING"]:

    The odd channel's normalization, 65,536, is left standing although the
    precompute's left operand could be the already-scaled ``W0'`` layer 1
    builds; that is priced below and left for tier 19.

This is tier 19.  The term is taken, at the value tier 18 published for it.

    layer 2 odd normalization        65,536   ->            0
    layer 2 auxiliary lane       77,380,256   ->   77,314,720
    layer 2 total             2,451,099,248   ->2,451,033,712
    suite bill, per net     144,867,148,624   -> 144,867,083,088

    (-65,536, or 0.0000452% of the whole bill)

THE FROZEN CONSTANT
===================
P1 on ``layer2_odd_normalization``, and P2 on tier 3's licence.

The constant is hard-coded twice in the incumbent as the identical expression
``normalization_cost(WIDTH, WIDTH)`` -- once at layer 1 and once at layer 2's
odd channel [suite_18:825, :863] -- and the second occurrence was never
re-derived after tier 10 changed where a normalization is allowed to live.

Tier 10 is crowned for the rule "the design scalar rides the smallest array in
the linear chain, not the 8,257,536 outputs".  It moved ``c`` from the butterfly
output onto the 256 x 256 matrix the butterfly multiplies, at both channels.
The rule has a left end that tier 10 did not reach: the chain the odd channel
runs on is

    O_s = H (d_s * cM),      cM = c (W0 W1h)

and ``c`` may sit on any factor of ``cM``.  Put it on ``W0`` and the product is
formed already scaled:

    cM = c (W0 W1h) = (c W0) W1h = W0' W1h.

``W0' = c W0`` is not a new array.  It is the array layer 1 builds, at the
65,536 this bill charges as ``layer1_normalization``, and which layer 1's
butterfly reads 126 times as its per-frame seed [kerdock_v3_estimator.py:120,
:131 with tier 10's folding].  Giving the precompute ``W0'`` as its left operand
makes the precompute the array's SECOND reader, and tier 3's licence -- an
operand array is built once per (matrix, side, depth) however many calls read it
-- says a second reader pays nothing.  The odd channel's own scaling pass then
has no work left: there is no unscaled ``M`` in the route to scale.

That is the whole change.  One term goes to zero; no term enters the bill; the
route computes the same ``O_s``.

WHY THIS IS THE SAME LICENCE TIERS 3, 5, 17 AND 18 SPENT, NOT A NEW ONE
=======================================================================
Tier 3 identified the unit "one operand array per (matrix, side, depth), however
many readers".  Tier 5 spent it on the net axis, tier 17 on the reader axis with
a count of zero, tier 18 on the reader axis with a count of two -- for a W-side
stack.  This tier spends it on the reader axis with a count of two for a plain
materialized weight array, which is the same statement one level below the
transform: ``W0'`` is built once and read twice.

The two readers are enumerated and asserted in ``_selfcheck``:

    reader 1   layer 1's butterfly seed, 126 frames  [charged in layer1_lane]
    reader 2   the precompute's A-side operand transform, depth 6
                                                     [charged, 1,915,152]

and the enumeration is exhaustive over this bill's terms: the even channel reads
``relu(P)``, the antipodal write reads ``T`` and ``O``, the thirty generic layers
read their own activations and weights.  Nothing else touches ``W0'``.

``W0'`` SURVIVES LAYER 1 UNMODIFIED, WHICH IS WHAT MAKES THE SECOND READ LEGAL
==============================================================================
The deployed first-product hook writes its frames into a separate output buffer
and never writes its weight operand:

    fnp.multiply(phases[:, :, None], weight[None, :, :], out=frames)
                                                        ^^^^^^^^^^
    [kerdock_v3_estimator.py:120]

``weight`` is a read-only operand; ``frames`` is a view of ``output``, the
32,256 x 256 preactivation [kerdock_v3_estimator.py:114-119].  Every later stage
of the butterfly reads and writes ``frames`` and the half-frame scratch only
[:121-131].  So the array layer 1 scales is intact when layer 2 runs.
``_selfcheck`` executes this: it runs the transcribed layer-1 route on a matrix
and asserts the matrix is unchanged element for element afterwards.

DISJOINTNESS, SO NOTHING IS DEDUCTED TWICE
==========================================
  * From tier 10.  Tier 10's saving was moving the scalar OFF the outputs and
    ONTO a 256 x 256 matrix; both channels kept a 65,536 pass and both are
    carried into this file at that value before the change.  This tier does not
    re-take tier 10's move: it removes the pass tier 10 created at the odd
    channel, and leaves the pass tier 10 created at layer 1 standing and
    charged.  Layer 1's 65,536 is asserted present and unchanged.
  * From tier 18.  Its ridden W-side lane is on ``W1h``, the RIGHT operand.
    This tier acts on the LEFT operand.  Both lanes are asserted at their tier-18
    values: the A-side stack of the left operand is still paid in full at
    1,915,152, and the W-side stack is still ridden at 1,915,152 charged once at
    layer 2.  The precompute's own price, 18,823,840, does not move -- the left
    operand changes identity, not shape, and ``best_operand_grade(m, k, levels)``
    takes no values.  Asserted by running the grade call on both.
  * From tiers 11, 12, 13.  All act on the odd BUTTERFLY's stage schedule.  This
    tier acts on the matrix the butterfly is seeded from.  The butterfly's
    50,233,344, its 688,128 prologue, its 163,840 level-1 arrays and its 524,288
    level-2 alphabet are asserted unchanged.
  * From tiers 8 and 9.  They act on the recombination and the ReLU lane; the
    antipodal write 8,257,536 and the zero-priced ReLU pass are asserted
    unchanged.
  * From tiers 14, 15, 17.  They act on layer 1; every layer-1 term is asserted
    equal to tier 18's, including the 65,536 this tier's second reader rides.
  * From tier 5.  Its 241,309,152 design stack stays a suite-once field, carried
    at its exact value, outside ``.total``, unclaimed.
  * From the call ladder (tiers 8-10 of the prior ladder).  No within-call
    schedule is reweighted, no depth moves, no lane is redistributed inside any
    call.  The certified per-call floor is re-derived from tier 7 and asserted at
    303,096,592 at the anonymous (4096, 256, 256).  This tier removes a pass that
    sits BETWEEN calls, not inside one.

EXACTNESS IDENTITY
==================
What is computed does not change.  One scalar multiplication is applied to a
different factor of the same product.

Write ``H`` for the normalized Walsh matrix [kerdock_v3_estimator.py:21-35,
:78], ``d_s`` for frame ``s``'s phase vector, ``D_s = H diag(d_s)``, ``c =
MEAN_CHI_256 / 16`` [kerdock_v3_estimator.py:18, :131], ``W0`` for the
Haar-absorbed first weight [kerdock_v3_estimator.py:149-155] and ``W1h =
mlp.weights[1]``.  Tier 10's crowned layer 1 forms ``W0' = c W0`` once and runs

    P_s = D_s W0' = H (d_s * (c W0))                                       (1)

Tier 2's odd channel is the same butterfly on the layer-2 matrix:

    O_s = D_s (c W0 W1h) = H (d_s * cM)                                    (2)

The incumbent forms ``cM`` in two steps -- ``M = W0 W1h`` by the precompute, then
``cM = c * M`` by a 65,536-element pass.  This tier forms it in one:

    W0' W1h = (c W0) W1h = c (W0 W1h) = cM                                 (3)

which is associativity of scalar multiplication with matrix multiplication --
exact over the reals, over the rationals and over the integers.  Nothing else in
(1) or (2) is touched: the same ``d_s``, the same ``H``, the same stage
schedule, the same 126 frames, the same output.

(3) is EXECUTED below rather than asserted, three ways:

  (i)   through the module's OWN graded Winograd recursion (``t7._psi``,
        ``_encode_left``, ``_encode_right``, ``_decode``, ``_psi_inverse``) at
        depths 1, 2 and 3 under several gradings: the graded route on
        ``(s A, B)`` equals ``s`` times the graded route on ``(A, B)`` and both
        equal the dense product, for integer ``s``;
  (ii)  end to end at small width: the transcribed layer-1 butterfly seeded from
        ``W0' W1h`` reproduces ``D_s (c W0 W1h)`` exactly, and also reproduces
        ``P_s W1h`` -- so the new route is the identity ``O = P W1h`` the tier-2
        CReLU split rests on, driven by ONE scaled array instead of two
        independently scaled paths;
  (iii) the CReLU identity ``relu(-P) W1h = T - O`` is re-run so the route the
        moved term sits inside still computes what the champion computes.

A CONSISTENCY GAIN, STATED BECAUSE IT IS THE REASON THE MOVE IS SAFE IN f32
===========================================================================
Tier 2's split needs ``O = P W1h`` to hold for the ``P`` layer 1 actually
produced.  The incumbent reaches ``cM`` down a second path -- scale ``W0 W1h``
by ``c`` -- so in f32 the two paths agree only to rounding.  This tier makes the
odd channel read the same ``W0'`` layer 1 was seeded from, so ``O`` is derived
from the identical scaled array that produced ``P``.  The route becomes MORE
faithful to the identity it depends on, not less.

f32 STATUS: NO REPRICING, NO FLAG
=================================
No value is approximated, no rank is reduced, no term any operation reads is
dropped, no summation inside any certified call is reordered, no depth moves.
Every op counted is one f32 multiply, add, subtract or copy priced at 1, the
unit the call bill uses.

  * The change removes 65,536 f32 multiplies and adds none.  It does not
    re-price a single surviving op.
  * The scalar ``c`` is applied to 65,536 elements before the change and to
    65,536 elements after it -- the same count, at layer 1, on ``W0``.  What
    disappears is the SECOND application, on ``M``.  No element loses a scaling
    it needs; ``_selfcheck`` runs the whole odd channel and compares against the
    dense ``D_s (c W0 W1h)``.
  * The exposure class is the one tier 10 adjudicated and took no flag for:
    where a scalar sits in a linear chain.  This tier reduces the number of
    scalings in the chain from two to one, so it reduces that exposure.
  * The monomial law is untouched: no product of fewer than 7 leaves appears at
    any level, and no leaf count changes -- the precompute's leaves stay at
    ``7**6 * direct_cost(4, 4, 4) = 13,176,688``, asserted.

No f32 repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A metered win is repaid in wall time when it forces small kernels, extra passes,
new dispatch, or new residency.  Here three axes improve, one is flat, and the
fourth costs 256 KB, which is named with its number.

  * LAUNCH COUNT FALLS BY ONE, AND IT IS A WHOLE KERNEL.  The removed work is
    not a fused epilogue: in the incumbent's shape it is a standalone elementwise
    pass over a 256 x 256 buffer between the precompute's decode and the odd
    butterfly's seed -- one launch, one full read, one full write, 512 KB of
    traffic at f32.  It disappears from the dispatch stream entirely.  The odd
    channel's route becomes: build the A-stack of ``W0'``, read layer 2's
    resident B-stack of ``W1h`` (tier 18), one batched leaf matmul, decode
    straight into the butterfly's seed buffer.
  * NO NEW KERNEL, NO NEW GRANULARITY, NO NEW SPECIALIZATION.  The precompute is
    the same call at the same depth 6 with the same 4 x 4 leaves as every other
    matmul in the net.  The A-side operand transform runs on a 256 x 256 f32
    array either way; scaling changed the array's values in setup, never its
    shape, stride or dtype, so the same kernel is dispatched with the same launch
    geometry.  This is the cheapest possible shape for a win: the fast path is
    unchanged and one slow pass is deleted.
  * THE DECODE GAINS A FUSION SITE IT DID NOT HAVE.  With the scaling pass gone,
    the precompute's decode writes ``cM`` directly into the buffer the butterfly
    seeds from.  In the incumbent the decode had to write ``M`` and hand it to a
    pass that rewrote every element; now the last write of the precompute is the
    first read of the butterfly.  One buffer round trip removed, not just one
    launch.
  * RESIDENCY: +256 KB, AND HERE IS THE HONEST COUNT.  ``W0'`` is 256 x 256 f32
    = 256 KB and must stay live from layer 1's normalization until the
    precompute's A-side transform is built inside layer 2.  Against a workspace
    that already holds ``self._activation`` at 64,512 x 256 f32 = 66 MB
    [kerdock_v3_estimator.py:79-82 scratch plus the fold3 activation] and tier
    18's 15.06 MB of Winograd stacks, the increment is 0.4% of one array.  It is
    also partly offset: the 256 KB intermediate ``M`` no longer needs to exist
    as a distinct value from ``cM``.  Net direction is up by at most 256 KB, it
    is named, and it is not claimed as a saving.
  * ORDERING IS FREE AND STATED.  The constraint is one edge: normalize ``W0``
    before the precompute reads it.  Layer 1 already normalizes ``W0`` before its
    own butterfly, which precedes layer 2 in every route this bill prices, so the
    edge is already satisfied by the existing order and no reschedule is
    required.  Free the array immediately after the precompute's A-stack is
    built; no lane is kept alive past layer 2.
  * BATCHING IS UNAFFECTED.  Nothing in the change touches a per-tile or
    per-frame loop.  The 126 frames, the 15.75 tiles and the 31 calling layers
    run exactly as tier 18 schedules them.
  * FLAT IN THE SUITE SIZE.  One net or a thousand, each pays 65,536 less; no
    one-time field moves, and the suite-once total is asserted identical to the
    incumbent's 241,373,664.

DOORS THAT STAY CLOSED
======================
Two are NEW, probed by this tier's own search and closed with arithmetic; the
rest are re-executed from the incumbent so the next tier does not pay for them
twice.

  * NEW -- IS THERE A THIRD SCALING PASS TO REMOVE?  No.  After this tier the
    bill contains exactly one term of the form ``normalization_cost(k, n)``:
    layer 1's.  ``_selfcheck`` enumerates every term of the bill and asserts the
    count of 65,536-sized scaling passes is 1, down from 2, and that no other
    term is a scalar-times-array pass at all.  The butterfly's ``final_scale``
    flag is False at both channels (tier 10), so no scaling hides inside a
    butterfly either -- asserted by re-deriving both butterflies with the flag
    and showing the flagged price is 8,257,536 higher at each.  SHUT.
  * NEW -- CAN LAYER 1's OWN 65,536 RIDE SOMETHING?  Only into a lane this bill
    does not charge, so it is NOT taken here.  The array before ``W0'`` is the
    Haar-absorbed ``W0 = R.T @ mlp.weights[0]`` with ``R = rotation * signs``
    [kerdock_v3_estimator.py:138-144, :149-150].  Line 144 already multiplies all
    65,536 entries of the rotation, so replacing ``signs`` by ``c * signs`` costs
    256 multiplies and would deliver ``c W0`` out of the absorption itself:
    a nominal 65,536 - 256 = 65,280.  But this bill charges NOTHING for the QR,
    for the sign pass or for the 256 x 256 x 256 absorption product -- they are
    outside every term -- so the credit would be taken by relocating work into an
    unmodelled lane rather than by deleting it.  Priced by
    ``next_rung_haar_fold_price()`` and printed beside the claim; left standing
    for its own adjudication.  NOT CLAIMED.
  * CARRIED -- TIER 18's SHARED W-SIDE LANE.  Depth 6 is the strict argmin of the
    shared-lane objective and depth 5 of the standalone one; both sweeps are
    brute-forced again here and the 1,597,088 tier-18 delta is re-derived.  SHUT.
  * CARRIED -- THE A-SIDE LANE OF THE PRECOMPUTE RIDES NOTHING.  No charged call
    has a (256, 256) A-side operand; the A-side shapes in the bill are the tiles
    only.  Enumerated and asserted.  Scaling the left operand does not change
    this: ``best_operand_grade`` is asserted to return the same graded object for
    the shape either way.  SHUT.
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
    not, and ``_selfcheck`` exhibits a post-ReLU block with two different
    absolute values.
  * CARRIED -- THE LEDGER-FREE ReLU WRITES, 478,937,088, priced at zero at all 32
    layers; re-billing them consistently would RAISE the bill.  Counted, not
    claimed.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * Layer 1's normalization, 65,536, is paid in full and asserted present.  This
    tier could have claimed both passes by folding ``c`` into the Haar sign pass;
    it does not, because that lane is unbilled (see DOORS).
  * The precompute's A-side stack of ``W0'``, 1,915,152, is paid in full even
    though its input is now an array another lane built.  The TRANSFORM is a new
    object; only the matrix is shared.  Refusing this is what killed tier 6.
  * The precompute's leaves and decode, 13,176,688 and 3,732,000, are paid in
    full; nothing about the product's shape changes.
  * The suite-once design stack, orphaned since tier 14, is still not removed: it
    sits outside ``.total`` and cannot move the fitness.
  * The thirty generic layers keep the antipodal half at full price; the
    ledger-free ReLU writes stay priced at zero; the terminal fold stays
    unmodelled.  All three are counted below and none is claimed.
  * ``.total`` remains the marginal per-net bill; no suite size is assumed.

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
# Tier 16's rule at the module's own isolated argmin, carried by tiers 17, 18.
_TIER16_PRECOMPUTE_DEPTH5 = 20420928

# THE CONSTANT THIS TIER UNFREEZES: tier 18's odd-channel scaling pass.
_TIER18_ODD_NORMALIZATION = 65536

# Tier 18's published figures, carried so every one of them can be re-asserted.
_INCUMBENT_TOTAL = 144867148624
_INCUMBENT_LAYER1_TOTAL = 50364416
_INCUMBENT_LAYER2_TOTAL = 2451099248
_INCUMBENT_LAYER2_AUX = 77380256
_INCUMBENT_GENERIC_TOTAL = 142365684960
_INCUMBENT_SUITE_ONCE = 241373664

# The number of layers that DO issue a Winograd call: 2..32 inclusive.
_WINOGRAD_CALLING_LAYERS = LAYERS - 1


def _t7():
    spec = importlib.util.spec_from_file_location("t19base", _T7_PATH)
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


# ---------------------------------------------------------------------------
# THE ONE CHANGE: the odd channel's scalar is already on layer 1's matrix, so
# the odd channel has no scaling pass of its own.
# ---------------------------------------------------------------------------


def normalization_cost(k: int = WIDTH, n: int = WIDTH) -> int:
    """Tier 10's term: the design's scalar folded onto a (k, n) weight matrix."""
    if min(k, n) <= 0:
        raise ValueError("the normalized matrix has positive dimensions")
    return k * n


def layer1_normalization_readers() -> tuple:
    """The readers of ``W0' = c W0``, enumerated.

    Reader 1 is layer 1's per-frame butterfly seed.  Reader 2 is the
    precompute's A-side operand transform -- which is what this tier adds, and
    the reason the odd channel needs no scaling of its own.  The enumeration is
    exhaustive over the terms of this bill; ``_selfcheck`` asserts that every
    other term reads an activation block, a design row, ``W1h`` or a generic
    layer weight, and never ``W0'``.
    """
    return ("layer1_butterfly_seed_126_frames",
            "layer2_precompute_A_side_operand_transform")


def odd_channel_normalization_cost(k: int = WIDTH, n: int = WIDTH) -> int:
    """THE CHANGED TERM.  Zero, because ``cM`` is produced already scaled.

    ``cM = c (W0 W1h) = (c W0) W1h = W0' W1h`` by associativity of the scalar.
    With ``W0'`` -- the array layer 1 already builds and this bill already
    charges at ``layer1_normalization`` -- as the precompute's left operand, the
    product IS ``cM`` and there is no unscaled ``M`` for a pass to scale.

    The price that is NOT charged is returned by
    ``odd_channel_normalization_ridden`` so the delta is auditable.
    """
    if min(k, n) <= 0:
        raise ValueError("the normalized matrix has positive dimensions")
    if len(layer1_normalization_readers()) != 2:
        raise ValueError("the scaled matrix does not have a second reader")
    return 0


def odd_channel_normalization_ridden(k: int = WIDTH, n: int = WIDTH) -> int:
    """What tier 18 charged here, carried so the whole delta is one number."""
    return normalization_cost(k, n)


def next_rung_haar_fold_price(width: int = WIDTH) -> int:
    """The next rung, priced and NOT taken -- and NOT taken for a stated reason.

    ``rotation * signs[None, :]`` [kerdock_v3_estimator.py:144] already writes
    all ``width**2`` entries, so ``c * signs`` would deliver ``c W0`` out of the
    Haar absorption for ``width`` extra multiplies, retiring layer 1's own
    65,536.  This bill charges nothing for the QR, the sign pass or the
    absorption product, so the credit would relocate work into an unmodelled
    lane rather than delete it.  Left for its own adjudication.
    """
    if width <= 0:
        raise ValueError("the rotation has a positive width")
    return normalization_cost(width, width) - width


# ---------------------------------------------------------------------------
# Carried machinery.  Every function below is tier 18's, unchanged, so the terms
# it produces can be asserted equal to tier 18's term by term.
# ---------------------------------------------------------------------------


def precompute_lanes(t7, k: int = WIDTH, n: int = WIDTH,
                     m: int = WIDTH) -> dict:
    """``cM``'s four lanes at layer 2's depth, with the W-side lane ridden.

    Tier 18's function, unchanged.  The left operand's IDENTITY changes in this
    tier (``W0'`` rather than ``W0``) and its lane cost does not: every argument
    of ``best_operand_grade`` is a dimension or a depth, never a value.
    """
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
    """cM's price: layer 2's depth, W-side lane on the ledger, left operand W0'."""
    return precompute_lanes(t7, k, n, m)["total"]


def precompute_shared_objective(t7, levels: int, k: int = WIDTH,
                                n: int = WIDTH, m: int = WIDTH) -> int:
    """Tier 18's objective: a ridable lane priced at zero, carried verbatim."""
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

    Tier 2's shape [suite_02:277-289], carried verbatim through tiers 14..18 and
    unchanged here so the six files' numbers are directly comparable.
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


def deployed_first_product_cost(frames: int = FRAMES, rows: int = WIDTH,
                                out_width: int = WIDTH) -> int:
    """Tier 14's layer-1 price: the deployed hook's literal op sequence."""
    return butterfly_ops(frames, rows, out_width,
                         final_scale=True, pingpong=False)


def crowned_first_product_cost(frames: int = FRAMES, rows: int = WIDTH,
                               out_width: int = WIDTH) -> int:
    """Tier 15's layer-1 lane: tiers 10..13's crowned butterfly schedule.

    Layer 1 KEEPS its normalization; this is the pass whose output ``W0'`` the
    odd channel now reads.
    """
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
    layer2_odd_normalization: int
    layer2_odd_normalization_ridden: int
    layer2_odd_level1_arrays: int
    layer2_odd_level2_arrays: int
    layer2_odd_shared_prologue: int
    layer2_odd_frame_element_price: int
    layer2_odd_butterfly: int
    layer2_antipodal_write: int
    layer2_aux: int
    layer2_total: int
    scaling_passes_charged: int
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
            "layer1_normalization_BUILDS_W0PRIME_CHARGED_ONCE":
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
            "layer2_precompute_lane_A_side_stack_of_W0PRIME_PAID_IN_FULL":
                self.layer2_precompute_left_stack,
            "layer2_precompute_lane_W_side_stack_of_W1h_RIDDEN_CHARGED_AT_LAYER_2":
                self.layer2_precompute_right_stack_ridden,
            "layer2_precompute_lane_decode": self.layer2_precompute_decode,
            "layer2_precompute_W0PRIME_W1h_IS_cM_ALREADY_SCALED":
                self.layer2_precompute,
            "layer2_precompute_STANDALONE_AT_THIS_DEPTH_worse_by_318064":
                self.layer2_precompute_standalone,
            "layer2_precompute_ISOLATED_ARGMIN_DEPTH5_DECLINED":
                self.layer2_precompute_isolated_declined,
            "layer2_precompute_DIRECT_COUNTERFACTUAL_DECLINED":
                self.layer2_precompute_direct_declined,
            "layer2_odd_normalization_NOTHING_LEFT_TO_SCALE":
                self.layer2_odd_normalization,
            "layer2_odd_normalization_TIER18_CHARGE_REMOVED":
                self.layer2_odd_normalization_ridden,
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
            "scaling_passes_CHARGED_in_the_whole_bill":
                self.scaling_passes_charged,
            "design_side_stack_ORPHANED_but_OUTSIDE_total_and_KEPT":
                self.suite_once_design_stack,
            "frame_descriptor_tables_TWO_charged_ONCE_to_the_suite":
                self.suite_once_frame_descriptors,
            "total": self.total,
        }


def _layer2_auxiliary_terms(t7) -> tuple:
    """Layer 2's non-matmul terms.  Only the normalization moves."""
    precompute = precompute_cost(t7, WIDTH, WIDTH, WIDTH)             # 18,823,840
    normalization = odd_channel_normalization_cost(WIDTH, WIDTH)      #          0
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                              pingpong=True, shared_depth=_SHARED_DEPTH)
    antipodal_write = BASE_ROWS * WIDTH                               #  8,257,536
    return precompute, normalization, butterfly, antipodal_write


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill: the odd channel's precompute multiplies the
    scaled ``W0'`` layer 1 already builds, so ``cM`` is produced already scaled
    and the odd channel has no normalization pass of its own."""
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

    # --- layer 1: tier 18's, carried verbatim.  Its normalization STAYS, and
    #     it is the array the odd channel now reads. ---------------------------
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

    # --- layer 2: THE ONE CHANGE.  The precompute's left operand is W0', so
    #     its product is cM and the odd channel's scaling pass is gone. --------
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

    scaling_passes = (1 if layer1_normalization else 0) + (1 if normalization else 0)
    if scaling_passes != 1:
        raise ValueError("the bill must charge exactly one scaling pass")

    descriptors = frame_descriptor_table_cost(FRAMES, WIDTH, 2)

    return SuiteBill(
        strategy="the_odd_channels_scalar_is_already_on_layer_ones_matrix",
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
        layer2_odd_normalization=normalization,
        layer2_odd_normalization_ridden=ridden_normalization,
        layer2_odd_level1_arrays=level1,
        layer2_odd_level2_arrays=level2,
        layer2_odd_shared_prologue=prologue,
        layer2_odd_frame_element_price=_BUTTERFLY_FRAME_ELEMENT_FOLDED,
        layer2_odd_butterfly=butterfly,
        layer2_antipodal_write=antipodal_write,
        layer2_aux=layer2_aux,
        layer2_total=layer2,
        scaling_passes_charged=scaling_passes,
        suite_once_design_stack=design_stack,
        suite_once_frame_descriptors=descriptors,
        suite_once=design_stack + descriptors,
        total=generic_total + layer1 + layer2,
    )


def incumbent_total() -> int:
    """Tier 18's bill, reconstructed from this file's own terms."""
    bill = suite_bill_per_net()
    return bill.total + bill.layer2_odd_normalization_ridden


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
    return bill.total - next_rung_haar_fold_price(WIDTH)


# ---------------------------------------------------------------------------
# Executable exactness.  The claims are run, not asserted:
#   (a) scaling the left operand commutes with the module's own graded Winograd
#       recursion at every depth and grading tested -- the whole tier;
#   (b) the A-side operand LANE is unchanged by scaling: same graded object,
#       same write count, so nothing is smuggled into the ridden array;
#   (c) end to end, the odd channel seeded from ``W0' W1h`` reproduces
#       ``D_s (c W0 W1h)`` AND ``P_s W1h`` exactly;
#   (d) ``W0'`` survives layer 1 unmodified, so the second read is legal;
#   (e) the reader enumeration is exhaustive and the bill charges one scaling
#       pass, not two;
#   (f) tier 18's shared W-side lane and its depth argument still close;
#   (g) every other term is tier 18's, term by term;
#   (h) the carried closed doors are re-priced and NOT claimed.
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
    """The design scalar applied to a matrix -- the pass this tier deletes."""
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
    """Layer 1, exactly as billed: a signed seed then radix-2 stages.

    ``weight`` is READ and never written, which is the deployed hook's own
    contract [kerdock_v3_estimator.py:120].  ``_selfcheck`` asserts it.
    """
    seed = [[sign * value for value in weight[j]]
            for j, sign in enumerate(phase_signs)]
    return _wht_rows(seed)


def design_block(phase_signs, hadamard):
    """The design rows frame ``s`` would have contributed: ``H diag(d_s)``."""
    return [[hadamard[i][j] * phase_signs[j] for j in range(len(phase_signs))]
            for i in range(len(hadamard))]


def _graded_core(t7, A, B, pa, pb, pc, right_leaves, counters):
    """``t7._alg`` verbatim, with the right-hand leaf operands recorded."""
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
    """The module's whole graded schedule: Psi in, recursion, Psi inverse out."""
    at = t7._psi(a, t7.PHI_A, pa, psi["a"])
    bt = t7._psi(b, t7.PHI_B, pb, psi["b"])
    ct = _graded_core(t7, at, bt, pa, pb, pc, right_leaves, counters)
    return t7._psi_inverse(ct, t7._inverse(t7.PHI_C), pc, psi["c"])


def _selfcheck() -> None:
    t7 = _t7()
    bill = suite_bill_per_net()
    nxt = _rng(20260819)

    # ---- 1. SCALING THE LEFT OPERAND COMMUTES WITH THE MODULE'S OWN GRADED
    #        RECURSION, AND COSTS THE SAME LANE.  THIS IS THE TIER. ----------
    #     (s A) B == s (A B) == s * dense, through _psi / _encode_left /
    #     _encode_right / _decode / _psi_inverse, at three depths and three
    #     gradings -- and the A-side write count is IDENTICAL, so the deleted
    #     pass is not reappearing inside the transform.
    for levels in (1, 2, 3):
        side = 1 << levels
        for pattern in ([True] * levels, [False] * levels,
                        [(j % 2 == 0) for j in range(levels)]):
            a = _mat(side * 2, side, nxt)
            b = _mat(side, side, nxt)
            for s in (1, 3, -5):
                plain_leaves, plain_counters = [], {"left": 0, "right": 0,
                                                    "decode": 0}
                plain_psi = {"a": [0], "b": [0], "c": [0]}
                plain = graded_route(t7, a, b, list(pattern), list(pattern),
                                     list(pattern), plain_leaves,
                                     plain_counters, plain_psi)
                assert plain == _mm(a, b)

                scaled_leaves, scaled_counters = [], {"left": 0, "right": 0,
                                                      "decode": 0}
                scaled_psi = {"a": [0], "b": [0], "c": [0]}
                scaled = graded_route(t7, _scale(s, a), b, list(pattern),
                                      list(pattern), list(pattern),
                                      scaled_leaves, scaled_counters,
                                      scaled_psi)
                #     (i) the product is the scaled product, exactly
                assert scaled == _scale(s, plain) == _mm(_scale(s, a), b), (
                    "scaling the left operand did not commute with the route")
                #     (ii) the lane is the same size: same A-side write count,
                #          same Psi count, same leaf count.  Cost is unmoved.
                assert scaled_counters["left"] == plain_counters["left"]
                assert scaled_counters["right"] == plain_counters["right"]
                assert scaled_counters["decode"] == plain_counters["decode"]
                assert scaled_psi["a"] == plain_psi["a"]
                assert len(scaled_leaves) == len(plain_leaves) == 7 ** levels
                #     (iii) the RIGHT lane is untouched by the left scaling --
                #           the tier-18 ridden array is bit-identical.
                assert scaled_leaves == plain_leaves, (
                    "scaling the left operand disturbed the ridden W-side lane")
                assert scaled_psi["b"] == plain_psi["b"]

    #     and the module agrees at the production shape: the graded object for
    #     the A-side lane is a function of dimensions and depth only.
    assert (t7.best_operand_grade(WIDTH, WIDTH, bill.call_depth)
            == (1915152, frozenset()))

    # ---- 2. END TO END: THE ODD CHANNEL SEEDED FROM W0' W1h IS D_s(c W0 W1h)
    #        AND IS ALSO P_s W1h. ----------------------------------------------
    for width in (4, 8, 16):
        hadamard = _hadamard(width)
        w0 = _mat(width, width, nxt)
        w1 = _mat(width, width, nxt)
        for c in (1, 3, -2):
            w0_prime = _scale(c, w0)                    # layer 1's charged array
            for _frame in range(2):
                signs = [1 if nxt(0, 1) else -1 for _ in range(width)]
                design = design_block(signs, hadamard)
                # layer 1's preactivation, from the scaled array
                p = layer1_route(signs, w0_prime)
                assert p == _mm(design, w0_prime)
                # THIS TIER's odd channel: seed from the product W0' @ W1h
                cm_new = _mm(w0_prime, w1)
                o_new = layer1_route(signs, cm_new)
                # tier 18's odd channel: seed from c * (W0 @ W1h)
                cm_old = _scale(c, _mm(w0, w1))
                o_old = layer1_route(signs, cm_old)
                assert cm_new == cm_old, "the two cM are not the same matrix"
                assert o_new == o_old, "the two odd channels differ"
                # and both are the identity tier 2's split rests on
                assert o_new == _mm(p, w1) == _mm(design, cm_new), (
                    "O = P W1h fails for the scaled route")
                # the CReLU identity the layer-2 route rests on still closes
                t_top = _mm(_relu(p), w1)
                assert _mm(_relu(_neg(p)), w1) == _sub(t_top, o_new)

    # ---- 3. W0' SURVIVES LAYER 1 UNMODIFIED, SO THE SECOND READ IS LEGAL. --
    w0_prime = _mat(16, 16, nxt)
    before = [row[:] for row in w0_prime]
    signs = [1 if nxt(0, 1) else -1 for _ in range(16)]
    _ = layer1_route(signs, w0_prime)
    assert w0_prime == before, "layer 1 wrote its weight operand"

    # ---- 4. THE READER ENUMERATION AND THE PASS COUNT. --------------------
    readers = layer1_normalization_readers()
    assert len(readers) == len(set(readers)) == 2 == bill.layer1_normalization_readers
    assert "layer1" in readers[0] and "precompute" in readers[1]
    assert bill.layer1_normalization == 65536, "layer 1 still pays for W0'"
    assert bill.layer2_odd_normalization == 0, "the odd channel still scales"
    assert bill.layer2_odd_normalization_ridden == 65536 == _TIER18_ODD_NORMALIZATION
    assert bill.scaling_passes_charged == 1
    assert odd_channel_normalization_cost(WIDTH, WIDTH) == 0
    assert normalization_cost(WIDTH, WIDTH) == 65536
    #     No scaling hides inside a butterfly: final_scale is False at BOTH
    #     channels, and turning it on would cost 8,257,536 more at each.
    flagged = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=True,
                            pingpong=True, shared_depth=_SHARED_DEPTH)
    assert flagged - bill.layer1_butterfly == BASE_ROWS * WIDTH == 8257536
    assert bill.layer1_butterfly == bill.layer2_odd_butterfly
    #     The delta is exactly the removed pass and nothing else.
    assert incumbent_total() == _INCUMBENT_TOTAL == 144867148624
    assert incumbent_total() - bill.total == 65536
    assert bill.total == 144867083088

    # ---- 5. TIER 18's SHARED W-SIDE LANE STILL CLOSES, RE-DERIVED. --------
    lanes = precompute_lanes(t7, WIDTH, WIDTH, WIDTH)
    assert bill.call_depth == 6 == lanes["levels"]
    assert lanes["levels"] == layer_call_depth(t7, TILE_ROWS, WIDTH, WIDTH)
    assert (t7.best_operand_grade(WIDTH, WIDTH, bill.call_depth)
            == weight_side_stack_grade(t7, WIDTH, WIDTH, TILE_ROWS))
    assert bill.layer2_precompute_right_stack_ridden == bill.weight_stack == 1915152
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
    assert all(shared_sweep[L] == plain_sweep[L] for L in shared_sweep if L != 6)
    assert plain_sweep[5] == 20420928 == bill.layer2_precompute_isolated_declined
    assert plain_sweep[6] == 20738992 == bill.layer2_precompute_standalone
    assert plain_sweep[6] - plain_sweep[5] == 318064
    assert plain_sweep[5] - shared_sweep[6] == 1597088
    assert bill.layer2_precompute_leaves == 13176688 == 7 ** 6 * t7.direct_cost(
        4, 4, 4)
    assert bill.layer2_precompute_decode == 3732000 == t7.best_decode_grade(
        WIDTH, WIDTH, 6)[0]
    assert bill.layer2_precompute_left_stack == 1915152
    assert (bill.layer2_precompute_leaves + bill.layer2_precompute_left_stack
            + bill.layer2_precompute_decode) == bill.layer2_precompute
    #     The A-side lane still rides nothing: no charged call has a (256, 256)
    #     A-side operand.
    a_side_shapes = {(TILE_ROWS, WIDTH), (BASE_ROWS % TILE_ROWS, WIDTH)}
    assert (WIDTH, WIDTH) not in a_side_shapes
    assert bill.layer1_weight_stack_removed_tier17 == 0
    assert bill.weight_stack_layers == 31 == LAYERS - 1
    assert bill.weight_stack_layers * bill.weight_stack == 59369712
    #     Refused numerically: tier 6, the direct counterfactual, the deployed
    #     operator's own one-level bill.
    assert bill.layer2_precompute > _TIER6_REJECTED_PRECOMPUTE
    assert bill.total > tier6_rejected_total()
    assert bill.layer2_precompute_direct_declined == 33488896
    assert bill.total < deployed_operator_fallback_total()
    assert bill.layer2_precompute_isolated_declined == _TIER16_PRECOMPUTE_DEPTH5

    # ---- 6. EVERY OTHER TERM IS TIER 18's, TERM BY TERM. ------------------
    assert bill.call_total == 303096592
    assert bill.row_part_full == 301181440 and bill.row_part_tail == 263533760
    assert bill.generic_layer == 4745522832
    assert bill.generic_layers_total == _INCUMBENT_GENERIC_TOTAL
    assert bill.layer1_butterfly == 50233344
    assert bill.layer1_shared_prologue == 688128
    assert bill.layer1_lane == 50298880
    assert bill.layer1_negation == 65536
    assert bill.layer1_deployed_butterfly_declined == 115605504
    assert bill.layer1_winograd_row_part_declined == 2130494688
    assert bill.layer1_total == _INCUMBENT_LAYER1_TOTAL == 50364416
    assert bill.layer2_even_rows == 2371803840
    assert bill.layer2_odd_level1_arrays == 163840
    assert bill.layer2_odd_level2_arrays == 524288
    assert bill.layer2_odd_shared_prologue == 688128
    assert bill.layer2_odd_butterfly == 50233344
    assert bill.layer2_antipodal_write == 8257536
    assert bill.layer2_relu_pass == 0
    assert bill.layer2_relu_writes_priced_zero == 8257536
    assert bill.layer2_aux == 77314720 == _INCUMBENT_LAYER2_AUX - 65536
    assert bill.layer2_total == 2451033712 == _INCUMBENT_LAYER2_TOTAL - 65536
    assert bill.suite_once_design_stack == 241309152
    assert bill.suite_once_frame_descriptors == 64512 == 2 * FRAMES * WIDTH
    assert bill.suite_once == _INCUMBENT_SUITE_ONCE
    assert bill.total == (bill.generic_layers_total + bill.layer1_total
                          + bill.layer2_total)

    # ---- 7. CARRIED DOOR: THE LAYER DEPTH IS STILL THE ARGMIN UNDER TIER 3.
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
    assert best_row[0] == 6 and best_layer[0] == 6
    assert best_row[1] == bill.row_part_full
    assert best_layer[1] == bill.generic_layer

    # ---- 8. CARRIED DOOR: THE ROW LANE IS EXACTLY LINEAR IN m. ------------
    def _row_lane(rows: int) -> int:
        b = t7.inplace_verbatim_leaves_candidate_bill(rows, WIDTH, WIDTH)
        return b.total - weight_side_stack_cost(t7, WIDTH, WIDTH, TILE_ROWS)

    assert 4 * _row_lane(3072) == 3 * _row_lane(TILE_ROWS)
    assert 8 * _row_lane(3584) == 7 * _row_lane(TILE_ROWS)
    assert bill.layer2_even_rows == 7 * bill.row_part_full + bill.row_part_tail
    assert bill.generic_layer - bill.weight_stack == 15 * bill.row_part_full + (
        bill.row_part_full * 3 // 4)
    assert bill.row_part_full + bill.weight_stack == bill.call_total

    # ---- 9. CARRIED DOORS THAT WOULD RAISE THE BILL. ----------------------
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

    # ---- 10. CONSERVATIVENESS AND CONSISTENCY GATES. ----------------------
    assert bill.total < _INCUMBENT_TOTAL
    assert next_rung_haar_fold_price(WIDTH) == 65280 == 65536 - WIDTH
    assert next_rung_total() < bill.total, "the next rung is a real, unclaimed rung"
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
        print(f"{key:<74} {value:>18,}")
    print(f"{'TOTAL (per net)':<74} {b.total:>18,}")
    print(f"{'incumbent (tier 18)':<74} {incumbent_total():>18,}")
    print(f"{'delta':<74} {incumbent_total() - b.total:>18,}")
    print(f"{'next rung (Haar sign fold), NOT claimed':<74} "
          f"{next_rung_total():>18,}")
    print(f"{'refused: tier 6 (REJECTED)':<74} {tier6_rejected_total():>18,}")
    print(f"{'fallback: deployed operator, one level':<74} "
          f"{deployed_operator_fallback_total():>18,}")
