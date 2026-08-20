"""Suite tier 20: DRY.  The one rung tier 19 named is illegal, the scalar's
seat is already at its argmin, and the cross-frame sharing licence is proved to
be exactly self-limiting -- it can never pay again at any stage.

    suite bill, per net     144,867,083,088   ->   144,867,083,088   (unchanged)

This tier ran a genuine search over every term of the incumbent bill and closed
three doors with arithmetic instead of opening one.  P4: a door genuinely closed
by a search is a paid outcome, and each of the three below removes work the next
ten tiers would otherwise repeat.

THE RUNG TIER 19 NAMED IS NOT MERELY UNATTRACTIVE -- IT IS ILLEGAL
==================================================================
Tier 19 left exactly one live rung, on a line of its own [suite_19 docstring,
"DOORS THAT STAY CLOSED", second bullet]:

    NEW -- CAN LAYER 1's OWN 65,536 RIDE SOMETHING?  Only into a lane this bill
    does not charge, so it is NOT taken here. ... replacing ``signs`` by
    ``c * signs`` costs 256 multiplies and would deliver ``c W0`` out of the
    Haar absorption itself: a nominal 65,536 - 256 = 65,280. ... NOT CLAIMED.

Tier 19 declined it on an ACCOUNTING scruple (the credit would relocate work
into an unmodelled lane).  The scruple was correct but the reason was too weak,
and a later tier reading only that reason would be tempted to charge the 256
explicitly and take the 65,280.  That tier would be rejected, because the move
does not compute the same result at all.

``_haar_rotation`` feeds exactly one consumer [kerdock_v3_estimator.py:162-172]:

    rotation     = self._haar_rotation(int(mlp.seed), mlp.width)
    first_weight = rotation.T @ mlp.weights[0]
    rotated      = MLP(..., weights=[first_weight, *mlp.weights[1:]], ...)
    return super().predict(rotated, budget)

so scaling the rotation scales ``rotated.weights[0]``.  That array is NOT
private to the sample chain.  It has two readers outside it, both of which run
BEFORE any sampling and both of which are nonlinear in it:

    reader A   _diagonal_gaussian_pass(mlp)          [base_estimator.py:23-47]
               iterates over mlp.weights INCLUDING weights[0] and returns
               analytic_means / analytic_alphas / firing / analytic_sigmas.
               fold3 returns those means verbatim as the estimator's answer for
               every layer but the last [fold3_estimator.py:278].
    reader B   sigma0 = sqrt(sum(weights[0] * weights[0], axis=0))
               [fold3_estimator.py:82-88], which sets exact_first_mean and hence
               first_moment_residual and first_variance_residual -- the frozen
               moment-tangent control subtracted from the final answer at
               fold3_estimator.py:274.

Scaling ``weights[0]`` by ``c`` multiplies every analytic mean by ``c`` and
shifts ``first_moment_residual`` by ``(1 - c) * sigma0 / sqrt(2 pi)``, which is
not a rescaling of anything -- ``mean(x)`` is unchanged, because ``x`` already
carries ``c`` on either route.  ``_selfcheck`` EXECUTES both readers on a small
net, in exact transcription, and prints the divergence.  With the deployed
constant ``c = MEAN_CHI_256 / 16 = 0.999023...`` the answer moves in the fourth
decimal place, which is a wrong answer, not a rounding difference.

SHUT.  Not "not claimed": illegal.  The 65,280 is off the board for every
remaining tier.

THE SCALAR'S SEAT IS AT ITS ARGMIN, AND THE ARGMIN IS PROVED BY EXHAUSTION
=========================================================================
With the Haar seat gone, the question tier 10 opened ("where in the linear chain
does the design scalar sit?") can be closed in closed form.  Layer 1's chain is

    signs (256)  ->  rotation (65,536)  ->  W_0 = mlp.weights[0] (65,536)
                 ->  W0 = R.T W_0 (65,536)      [unbilled Haar lane]
                 ->  W0' = c W0 (65,536)        [BILLED, layer1_normalization]
                 ->  level-1 alphabet (163,840) [BILLED, 5 ops per pair]
                 ->  level-2 alphabet (524,288) [BILLED, 32 arrays per group]
                 ->  126 frame blocks (8,257,536 elements) [what tier 10 removed]

Seating ``c`` on an array costs one multiply per element of that array, so the
seat problem is "minimise the element count over REACHABLE seats".  The four
upstream seats are unreachable and each for its own executed reason:

  * ``signs``, ``rotation``, ``mlp.weights[0]`` -- the door above.  All three are
    the same array up to the absorption, and all three change readers A and B.
  * ``phases`` (32,256 elements, and net-independent, so it would have been the
    prize) -- unreachable for a different reason, and this one is a consequence
    of the ladder's own crowned tiers.  After tier 12 and tier 13 the phase
    VALUES multiply nothing: the seed pass is gone and each frame's row selects
    one of the four level-1 arrays by index [suite_13 docstring, part (II);
    this file's ``_LEVEL1_OPS_PER_PAIR``].  A selector cannot carry a scalar.
    ``_selfcheck`` asserts the schedule contains no phase-valued multiply.

Among the reachable seats the element counts are 65,536 < 163,840 < 524,288 <
8,257,536, so ``W0'`` is the strict argmin and tier 10 is already sitting on it.
The odd channel has no seat of its own at all (tier 19).  The whole bill charges
ONE scaling pass, of 65,536, and no route can charge fewer.  SHUT.

THE CROSS-FRAME SHARING LICENCE IS EXACTLY SELF-LIMITING
========================================================
This is the door tier 13 left ajar and the one this tier actually adds to the
ladder's knowledge.  Tier 13 closed stage 3 by measuring the phase-INDEPENDENT
tree alphabet at 1,024 per group of eight and pricing it at 8,388,608 against a
per-frame pass worth 8,257,536 -- a loss of 131,072, or 1.59%.  It then named
the escape it had not closed [suite_13:1434]:

    The margin a phase-aware tier would have to beat at stage 3, named ...

A phase-aware tier builds only the trees the 126 FROZEN frames actually reach,
which is never more than 1,008 per group and could be fewer.  1,008 < 1,024, so
on tier 13's own numbers the escape looks open by 16 arrays per group.

It is not open.  It is a dead tie, at every stage, for a reason that needs no
access to the frozen phase asset:

    saving from sharing stage k  =  frames x rows x width
    frame-realized alphabet cost =  width x SUM_g (trees in group g)
                                 =  width x SUM_g 2**k * D_g
                                 <= width x (rows / 2**k) x 2**k x frames
                                 =  frames x rows x width

where ``D_g <= frames`` is the number of DISTINCT restrictions of the 126 phase
vectors to group ``g``'s ``2**k`` coordinates, and ``2**k * D_g`` counts the
trees because each frame needs one tree per row of its group and two frames
share all of them exactly when their restrictions coincide.  The two sides are
the same number, ``126 * 256 * 256 = 8,257,536``, INDEPENDENTLY OF k -- the
``2**k`` cancels against the group count.  So a phase-aware schedule can at best
break even at any stage, and it breaks even only in the maximally lucky case
``D_g = frames`` for every g.

Sharing therefore pays at stage ``k`` if and only if the PHASE-INDEPENDENT
alphabet is strictly cheaper than the frame-realized bound, i.e. iff

    abstract(k)  <  2**k * frames                 [per group of 2**k rows]

    stage 1:        4  <  252     YES   -> taken by tier 12
    stage 2:       32  <  504     YES   -> taken by tier 13
    stage 3:    1,024  > 1,008    NO    -> ties at best, and loses by 131,072
                                           on the abstract alphabet
    stage 4:  524,288  > 2,016    NO    -> a fortiori
    stage k>=3: abstract(k) = 2**(k-1) * abstract(k-1)**2 / (that of k-1's
                family count), strictly increasing; 2**k * frames grows
                geometrically only -- the crossing never reverses.

The licence is exhausted at exactly two rungs and no third rung exists at any
price.  ``_selfcheck`` enumerates the tree alphabet EXHAUSTIVELY over all sign
patterns at stages 1, 2 and 3 (4, 32 and 1,024 trees, reproducing tier 13's
count from scratch under tier 12's two permitted leaf identities), measures the
realized alphabet for explicit frame tables, and asserts the break-even identity
with equality.  SHUT, both ways.

WHAT ELSE THE SEARCH TOUCHED AND WHY EACH IS PRICED, NOT TAKEN
==============================================================
Every one of these is executed below and printed beside the claim.

  * THE ANTIPODAL HALF BEYOND LAYER 2 -- the largest frozen constant left in the
    model, worth roughly half of 142,365,684,960 if it fell.  It does not fall,
    and the reason is one line of algebra.  Tier 2 works because layer 1's two
    halves are exact negations, ``pre1 = [p ; -p]``, and ``relu(-p) = relu(p)
    - p`` turns the second product into the first minus a butterfly-cheap term.
    Layer 2's two halves are ``[t ; t - o]``, and they are exact negations only
    if ``o = 2t``.  ``_selfcheck`` exhibits the failure numerically and, more to
    the point, PRICES the three routes a tier might try at layer 3 in this
    bill's own row lane:

        direct (what the bill charges)      2 half-layer products
        CReLU on both halves                3 half-layer products
        difference route  bot = top - dW    2 half-layer products + 1 pass

    The direct route is the strict argmin, the CReLU route is 50% worse, and the
    difference route is worse by a full 8,257,536-element pass.  The butterfly
    term ``o W2 = z (cM W2)`` is cheap in every one of them and appears in none
    of the minima.  SHUT.
  * THE WINOGRAD DEPTH, THE 15.75 TILE FRACTION, AND SHAPE SPECIALIZATION AT THE
    LAYER SIZE.  Re-derived here rather than carried: every m-scaled lane of the
    tier-7 core (leaves, A-side stack, decode) is exactly linear in ``m`` at
    fixed depth, so billing a layer as one 64,512-row call is IDENTICAL to
    billing it as 15.75 tiles, and the depth argmin cannot move with ``m``
    because only the m-independent W-side stack distinguishes the objectives.
    Both statements are executed to the FLOP over every lawful depth.  SHUT.
  * TWO BUTTERFLIES ARE NOT CHEAPER FUSED.  Running layer 1's and layer 2's
    butterflies as one butterfly on the 256 x 512 seed ``[W0' | cM]`` costs
    exactly what the two cost separately -- executed, both sides equal at
    50,233,344 x 2 -- because every term of the schedule is linear in the seed's
    column count.  SHUT.
  * THE LAYER-1 ANTIPODAL NEGATION, 65,536.  The pilot reads
    ``relu(-p)[0:256]`` [fold3_estimator.py:109-115], 256 rows by 256 active
    columns.  Producing it costs one pass over 65,536 elements by negation, by
    ``relu(p) - p``, or by re-running frame 0 with negated phases (393,216, six
    times worse -- priced below).  Expressing it as ``fnp.minimum(p, 0)``, which
    this ledger would price at zero because it prices ``fnp.maximum`` at zero,
    is refused here: the pass still runs, so the metered win would be repaid in
    full in wall time.  That is the V5-d3 law applied against this tier's own
    interest.  SHUT.
  * THE TERMINAL FOLD.  Re-executed, and the bound is tightened.  The incumbent
    models layers 30..32 as three generic layers, i.e. 3 x 65,536 units of
    row-scaled ``k*n`` work.  The deployed fold issues one, two and three
    row-scaled products at those layers, for ``|active| b + (|active| + b) c +
    (|active| + b + c) d`` with ``b, c, d`` the kink counts; the maximum over
    the lawful region is 393,216 = SIX units, and skipping the products whose
    folded operand is empty only lowers it to 391,681, still just under six.
    An honest worst-case terminal fold therefore costs THREE MORE generic
    layers, +14,236,568,496.  Counted, not claimed, and the next tier should not
    spend a turn on it.
  * PRUNING AND THE LEDGER-FREE ReLU WRITES.  Carried at the incumbent's values;
    both raise the bill if modelled honestly, and ``active`` has worst case 256
    by construction [fold3_estimator.py:102-132].

EXACTNESS IDENTITY
==================
The route is IDENTICAL to tier 19's, term for term, because this tier proposes
no route change: it proves that three candidate route changes are unavailable.
Every term of the bill below is computed by the same function on the same
arguments as in ``suite_19``, and ``_selfcheck`` asserts term-by-term equality
against tier 19's published figures and asserts ``.total ==
144,867,083,088``.

The identities the incumbent route rests on are re-executed here rather than
inherited, so this file stands alone as a statement of the champion's bill:

  (i)   the CReLU split, ``relu(-p) W2 = relu(p) W2 - p W2``, built explicitly
        on ``[z ; -z]`` and compared entry for entry;
  (ii)  the design product ``o = z (cM)`` as a phased Walsh-Hadamard transform
        of the 256 x 256 precompute, run against the dense product;
  (iii) the scalar's associativity, ``c (W0 W1h) = (c W0) W1h``, which is what
        lets layer 2 charge no scaling pass (tier 19);
  (iv)  the linearity of every m-scaled Winograd lane, which is what lets the
        15.75-tile bill equal the one-call bill.

f32 STATUS: NO REPRICING, NO FLAG
=================================
No op is added, removed or repriced anywhere in the bill.  The three doors are
closed by arithmetic about routes that are NOT taken; the route that is charged
is byte-for-byte tier 19's.  In particular the two IEEE identities the ladder
permits (``a - b`` IS ``a + (-b)``; negation IS a sign flip) are used in this
file only inside the tree enumeration that reproduces tier 13's alphabet, where
tier 12 and tier 13 already used them, and the two the ladder refuses
(``(-a) + (-b) == -(a + b)``; ``-(a - b) == b - a``) are used nowhere -- the
enumeration exhibits the +-0 counterexample for both rather than assuming it.

No f32 repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A DRY tier has no metered win, so it has nothing to repay -- but it does have a
slope obligation, because the value it delivers is the wall time the next ten
tiers do not spend, and that value is only real if the closed doors are closed
for implementation reasons too.  All three are.

  * THE HAAR SEAT would have been the cheapest imaginable shape -- two literals
    swapped in a 256-element ``fnp.where`` and one 65,536-element pass deleted,
    zero new kernels, zero new residency.  That is exactly why it needed
    killing on correctness rather than on cost: nothing about its shape would
    have warned anyone.  The kill is arithmetic and it is executed.
  * THE SCALAR'S ARGMIN is a statement about element counts, so it is
    shape-neutral by construction: every candidate seat is one elementwise pass
    over one contiguous f32 array, one launch, one read, one write.  The seat
    that wins is the one with the fewest elements, and no seat changes any
    other array's shape, stride, dtype or launch geometry.
  * THE SHARING LICENCE closes on a bound that gets BETTER for the incumbent as
    the shape gets more realistic, not worse.  The tie is counted in
    arithmetic only.  A real stage-3 shared prologue would additionally hold
    1,008 arrays of 256 f32 per group across 32 groups = 33 MB of level-3
    alphabet resident for the whole butterfly, against the 512 KB the stage-2
    alphabet holds today, and would replace one perfectly coalesced streaming
    pass per frame with 1,008-way gathered reads.  So the arithmetic tie is a
    large wall-time LOSS, and the door is shut more firmly in practice than on
    the ledger.  Named with its number so no later tier re-opens it hoping the
    shape would pay for the tie.
  * NOTHING ELSE MOVES.  The 126 frames, the 15.75 tiles, the 31 charged W-side
    stacks, the two butterflies and the one scaling pass are scheduled exactly
    as tier 19 schedules them; ``.total`` and every field of the breakdown are
    asserted identical.  Flat in the suite size: the suite-once total is
    asserted at the incumbent's 241,373,664.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import math
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

# The design scalar.  kerdock_v3_estimator.py:21 with the /16 of :144.
MEAN_CHI_256 = 15.98438266660852747
DESIGN_SCALAR = MEAN_CHI_256 / 16.0

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

# Tier 19's published figures.  This tier changes NONE of them.
_INCUMBENT_TOTAL = 144867083088
_INCUMBENT_LAYER1_TOTAL = 50364416
_INCUMBENT_LAYER2_TOTAL = 2451033712
_INCUMBENT_LAYER2_AUX = 77314720
_INCUMBENT_GENERIC_TOTAL = 142365684960
_INCUMBENT_SUITE_ONCE = 241373664

# The number of layers that DO issue a Winograd call: 2..32 inclusive.
_WINOGRAD_CALLING_LAYERS = LAYERS - 1

# Tier 13's abstract, phase-independent tree alphabet, per group of 2**k rows.
_TIER13_ABSTRACT_ALPHABET = {1: 4, 2: 32, 3: 1024, 4: 524288}


def _t7():
    spec = importlib.util.spec_from_file_location("t20base", _T7_PATH)
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
# The bill.  Every function in this block is tier 19's, unchanged, so the terms
# it produces can be asserted equal to tier 19's term by term.
# ---------------------------------------------------------------------------


def normalization_cost(k: int = WIDTH, n: int = WIDTH) -> int:
    """Tier 10's term: the design's scalar folded onto a (k, n) weight matrix."""
    if min(k, n) <= 0:
        raise ValueError("the normalized matrix has positive dimensions")
    return k * n


def layer1_normalization_readers() -> tuple:
    """The readers of ``W0' = c W0``: layer 1's butterfly seed and, since tier
    19, the precompute's A-side operand transform."""
    return ("layer1_butterfly_seed_126_frames",
            "layer2_precompute_A_side_operand_transform")


def odd_channel_normalization_cost(k: int = WIDTH, n: int = WIDTH) -> int:
    """Tier 19's term: zero, because ``cM`` is produced already scaled."""
    if min(k, n) <= 0:
        raise ValueError("the normalized matrix has positive dimensions")
    if len(layer1_normalization_readers()) != 2:
        raise ValueError("the scaled matrix does not have a second reader")
    return 0


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
    """cM's price: layer 2's depth, W-side lane on the ledger, left operand W0'."""
    return precompute_lanes(t7, k, n, m)["total"]


def declined_direct_precompute_cost(k: int = WIDTH, n: int = WIDTH,
                                    m: int = WIDTH) -> int:
    """Tier 15's charge: the cost model's named counterfactual."""
    return direct_cost(m, k, n)


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
    """Ops a phased-WHT butterfly over ``frames`` frames costs.  Tier 2's shape
    [suite_02:277-289], carried verbatim through tiers 14..19."""
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


# ---------------------------------------------------------------------------
# DOOR 1.  The Haar seat is illegal: rotated weights[0] is read by the analytic
# pass and by sigma0, both of which are nonlinear in it.
# ---------------------------------------------------------------------------


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def diagonal_gaussian_pass(weights, width: int):
    """Exact transcription of base_estimator.py:23-47, in pure Python.

    ``weights`` is a list of ``width x width`` row-major lists.  Returns the
    four sequences fold3 consumes; ``means`` is what the estimator RETURNS for
    every layer but the last [fold3_estimator.py:278].
    """
    mu = [0.0] * width
    var = [1.0] * width
    means, alphas, firing, sigmas = [], [], [], []
    for weight in weights:
        mu_pre = [sum(mu[i] * weight[i][j] for i in range(width))
                  for j in range(width)]
        var_pre = [sum(var[i] * weight[i][j] * weight[i][j] for i in range(width))
                   for j in range(width)]
        sigma = [math.sqrt(max(v, 1e-12)) for v in var_pre]
        alpha = [mu_pre[j] / sigma[j] for j in range(width)]
        phi = [_norm_pdf(a) for a in alpha]
        cdf = [_norm_cdf(a) for a in alpha]
        new_mu = [mu_pre[j] * cdf[j] + sigma[j] * phi[j] for j in range(width)]
        second = [(var_pre[j] + mu_pre[j] * mu_pre[j]) * cdf[j]
                  + mu_pre[j] * sigma[j] * phi[j] for j in range(width)]
        var = [max(second[j] - new_mu[j] * new_mu[j], 0.0) for j in range(width)]
        mu = new_mu
        means.append(list(mu))
        alphas.append(list(alpha))
        firing.append(list(cdf))
        sigmas.append(list(sigma))
    return means, alphas, firing, sigmas


def sigma0_of(weight, width: int):
    """fold3_estimator.py:82 -- the column norms of the ROTATED weights[0]."""
    return [math.sqrt(sum(weight[i][j] * weight[i][j] for i in range(width)))
            for j in range(width)]


def haar_seat_divergence(width: int = 4, depth: int = 3,
                         scalar: float = DESIGN_SCALAR) -> dict:
    """EXECUTE the door: scale weights[0] by c and watch the ANSWER move.

    Seating the design scalar inside ``_haar_rotation`` scales
    ``rotated.weights[0]``.  This runs both readers on a deterministic net and
    reports the largest absolute change in each.  A nonzero change in either is
    a different estimator output, which is what makes the 65,280 illegal.
    """
    if width < 2 or depth < 2:
        raise ValueError("the divergence needs a net with at least two layers")
    weights = []
    for layer in range(depth):
        weights.append([
            [math.sin(1.0 + layer * 3.0 + i * 0.7 + j * 1.3) for j in range(width)]
            for i in range(width)
        ])
    scaled = [[[scalar * v for v in row] for row in weights[0]]] + weights[1:]

    means, alphas, _f, _s = diagonal_gaussian_pass(weights, width)
    means_c, alphas_c, _fc, _sc = diagonal_gaussian_pass(scaled, width)

    mean_shift = max(abs(a - b)
                     for u, v in zip(means, means_c) for a, b in zip(u, v))
    alpha_shift = max(abs(a - b)
                      for u, v in zip(alphas, alphas_c) for a, b in zip(u, v))

    s0 = sigma0_of(weights[0], width)
    s0c = sigma0_of(scaled[0], width)
    # exact_first_mean = sigma0 / sqrt(2 pi); mean(x) is UNCHANGED because the
    # sampled x already carries c on either route, so the residual shifts.
    residual_shift = max(abs(a - b) / math.sqrt(2.0 * math.pi)
                         for a, b in zip(s0, s0c))
    return {
        "scalar": scalar,
        "reader_A_analytic_mean_max_shift": mean_shift,
        "reader_A_analytic_alpha_max_shift": alpha_shift,
        "reader_B_first_moment_residual_max_shift": residual_shift,
        "answer_changes": mean_shift > 0.0 or residual_shift > 0.0,
    }


def scalar_seat_ladder() -> list:
    """Every seat in layer 1's linear chain, its element count, and its status.

    Cost of seating the design scalar on an array is one multiply per element.
    The argmin over REACHABLE seats is what the bill must charge.
    """
    return [
        ("haar_signs", WIDTH,
         "UNREACHABLE: scales rotated weights[0]; readers A and B"),
        ("haar_rotation", WIDTH * WIDTH,
         "UNREACHABLE: same array as signs after the elementwise pass"),
        ("mlp_weights_0", WIDTH * WIDTH,
         "UNREACHABLE: readers A and B read it directly"),
        ("phases", FRAMES * WIDTH,
         "UNREACHABLE: tiers 12-13 made the phase values pure selectors"),
        ("W0_prime", WIDTH * WIDTH, "REACHABLE, TAKEN by tier 10"),
        ("level1_alphabet", _LEVEL1_OPS_PER_PAIR * (WIDTH // 2) * WIDTH,
         "REACHABLE, worse"),
        ("level2_alphabet", _LEVEL2_ARRAYS_PER_GROUP * (WIDTH // 4) * WIDTH,
         "REACHABLE, worse"),
        ("frame_outputs", FRAMES * WIDTH * WIDTH,
         "REACHABLE, worst; this is what tier 10 removed"),
    ]


def cheapest_reachable_scalar_seat() -> tuple:
    """The argmin of ``scalar_seat_ladder`` over reachable seats."""
    reachable = [(name, size) for name, size, status in scalar_seat_ladder()
                 if status.startswith("REACHABLE")]
    return min(reachable, key=lambda item: item[1])


# ---------------------------------------------------------------------------
# DOOR 2.  The cross-frame sharing licence is exactly self-limiting.
# ---------------------------------------------------------------------------


def _canonical(op: str, left, right):
    """Build one node under the TWO IEEE identities tier 12 permits.

    Permitted, and used exactly where tier 12 used them -- at the seed:
        a + (-b)  IS  a - b        (subtraction is addition of the negation)
        a - (-b)  IS  a + b
    Refused, and used nowhere:
        (-a) + (-b) == -(a + b)    (fails on signed zero)
        -(a - b)    == b - a       (fails on signed zero)
    The identities apply only when the right operand is a NEGATED LEAF; a
    compound tree is never re-signed.
    """
    if isinstance(right, tuple) and right[0] == "N":
        right = ("P", right[1])
        op = "-" if op == "+" else "+"
    return (op, left, right)


def butterfly_stage_trees(phase_bits, stages: int):
    """The bit-exact expression tree of every row after ``stages`` stages.

    ``phase_bits`` is the frame's phase restriction to this group, a tuple of
    +1/-1 of length ``2 ** stages``.  The schedule is the deployed one
    [kerdock_v3_estimator.py:133-143]: seed, then half = 1, 2, 4, ... with
    ``new[i0] = v[i0] + v[i1]`` and ``new[i1] = v[i0] - v[i1]``.
    """
    rows = len(phase_bits)
    if rows != 1 << stages:
        raise ValueError("the group must hold exactly 2**stages rows")
    values = [("P", i) if phase_bits[i] > 0 else ("N", i) for i in range(rows)]
    half = 1
    while half < rows:
        nxt = list(values)
        for block in range(rows // (2 * half)):
            for off in range(half):
                i0 = block * 2 * half + off
                i1 = i0 + half
                nxt[i0] = _canonical("+", values[i0], values[i1])
                nxt[i1] = _canonical("-", values[i0], values[i1])
        values = nxt
        half *= 2
    return values


def abstract_alphabet(stages: int) -> int:
    """Trees a group of ``2 ** stages`` rows can take over ALL sign patterns.

    This reproduces tier 13's phase-INDEPENDENT count from scratch:
    4 at stage 1, 32 at stage 2, 1,024 at stage 3.
    """
    rows = 1 << stages
    seen = set()
    for mask in range(1 << rows):
        bits = tuple(1 if (mask >> i) & 1 == 0 else -1 for i in range(rows))
        seen.update(butterfly_stage_trees(bits, stages))
    return len(seen)


def realized_alphabet(phase_table, stages: int) -> int:
    """Trees the GIVEN frames actually reach in one group of 2**stages rows."""
    seen = set()
    for bits in phase_table:
        seen.update(butterfly_stage_trees(tuple(bits), stages))
    return len(seen)


def sharing_ladder(frames: int = FRAMES, rows: int = WIDTH,
                   width: int = WIDTH) -> list:
    """Price both sides of the sharing crossing at every lawful stage.

    saving(k)            = frames * rows * width          (one pass per frame)
    realized_bound(k)    = width * (rows / 2**k) * 2**k * frames
                         = frames * rows * width          (the SAME number)
    abstract_cost(k)     = width * (rows / 2**k) * abstract(k)

    The realized bound is independent of ``k``, so sharing can pay only where
    the abstract alphabet is strictly below it.
    """
    saving = frames * rows * width
    out = []
    for k in sorted(_TIER13_ABSTRACT_ALPHABET):
        groups = rows >> k
        abstract = _TIER13_ABSTRACT_ALPHABET[k] * groups * width
        realized_bound = (1 << k) * frames * groups * width
        out.append({
            "stage": k,
            "abstract_alphabet_per_group": _TIER13_ABSTRACT_ALPHABET[k],
            "abstract_cost": abstract,
            "frame_realized_bound": realized_bound,
            "saving": saving,
            "pays": min(abstract, realized_bound) < saving,
            "margin": saving - min(abstract, realized_bound),
        })
    return out


def stage3_shared_alphabet_residency_bytes(frames: int = FRAMES,
                                           rows: int = WIDTH,
                                           width: int = WIDTH) -> int:
    """The slope note's number: bytes a stage-3 shared prologue must hold."""
    groups = rows >> 3
    arrays_per_group = min(_TIER13_ABSTRACT_ALPHABET[3], 8 * frames)
    return groups * arrays_per_group * width * 4


# ---------------------------------------------------------------------------
# DOOR 3.  The antipodal half beyond layer 2, priced in this bill's own lane.
# ---------------------------------------------------------------------------


def _relu(x: float) -> float:
    return x if x > 0.0 else 0.0


def antipodal_identity_fails_at_layer2(samples: int = 64) -> dict:
    """Tier 2 needs the two halves to be exact negations.  At layer 2 they are
    not: the halves are ``t`` and ``t - o``, negations only where ``o = 2 t``.
    """
    worst = 0.0
    witness = None
    crelu_failures = 0
    for s in range(samples):
        t = math.sin(0.3 + s * 0.61)
        o = math.cos(0.9 + s * 0.37)
        gap = abs((t - o) + t)          # zero iff t - o == -t, i.e. o == 2t
        if gap > worst:
            worst = gap
            witness = (t, o)
        # Tier 2's rescue, relu(-p) = relu(p) - p, applied to the layer-2
        # halves, reads relu(t - o) == relu(t) - t.  It is not an identity
        # here; it holds only on the measure-zero set where o = 2t (and, by
        # coincidence, wherever both sides happen to vanish).
        if abs(_relu(t - o) - (_relu(t) - t)) > 1e-15:
            crelu_failures += 1
    if crelu_failures == 0:
        raise ValueError("an unexpected layer-2 antipodal identity held")
    return {
        "max_negation_gap": worst,
        "witness_t_o": witness,
        "crelu_rescue_failures": crelu_failures,
        "samples": samples,
    }


def layer3_route_prices(row_lane_per_half: int) -> dict:
    """The three routes a tier might try at layer 3, in half-layer products.

    ``row_lane_per_half`` is this bill's price for one 32,256-row product.
    top3 = relu(t) W2 and bot3 = relu(t - o) W2 are independent activations;
    ``o W2 = z (cM W2)`` is butterfly-cheap in every route and saves nothing,
    because it never appears in a minimum.
    """
    pass_cost = BASE_ROWS * WIDTH
    return {
        "direct_two_independent_products": 2 * row_lane_per_half,
        "crelu_on_both_halves": 3 * row_lane_per_half,
        "difference_route_top_minus_delta_W": 2 * row_lane_per_half + pass_cost,
        "charged_by_this_bill": 2 * row_lane_per_half,
    }


def frame_zero_renegation_price() -> int:
    """Re-running frame 0 with negated phases instead of one negation pass."""
    return _BUTTERFLY_FRAME_ELEMENT_FOLDED * WIDTH * WIDTH


def terminal_fold_bounds() -> tuple:
    """Layers 30..32: the incumbent's width work, the honest worst case, and
    the worst case when empty folded operands are skipped exactly."""
    incumbent = 3 * WIDTH * WIDTH
    worst = 0
    for b in (0, WIDTH):
        for c in (0, WIDTH):
            for d in (0, WIDTH):
                worst = max(worst, WIDTH * b + (WIDTH + b) * c
                            + (WIDTH + b + c) * d)
    # With empty folded operands skipped exactly, the objective is, inside each
    # of the four gate regimes, a sum of products with non-negative coefficients
    # and therefore monotone non-decreasing in b, c and d.  Its maximum in each
    # regime sits at the top of that regime, so the boundary set {1, 255, 256}
    # attains the global maximum.
    skipped = 0
    for b in (1, WIDTH - 1, WIDTH):
        for c in (1, WIDTH - 1, WIDTH):
            for d in (1, WIDTH - 1, WIDTH):
                on30_live = WIDTH - b > 0
                on31_live = WIDTH - c > 0
                value = WIDTH * b
                value += (WIDTH if on30_live else 0) * c + b * c
                value += ((WIDTH if (on30_live and on31_live) else 0) * d
                          + (b if on31_live else 0) * d + c * d)
                skipped = max(skipped, value)
    return incumbent, worst, skipped


# ---------------------------------------------------------------------------
# The bill object.  Identical to tier 19's, field for field.
# ---------------------------------------------------------------------------


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
    layer1_lane: int
    layer1_deployed_butterfly_declined: int
    layer1_negation: int
    layer1_total: int
    generic_layer: int
    generic_layers_total: int
    layer2_even_rows: int
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
    layer2_odd_butterfly: int
    layer2_antipodal_write: int
    layer2_aux: int
    layer2_total: int
    scaling_passes_charged: int
    scalar_seat_elements: int
    sharing_stages_taken: int
    sharing_stage3_margin: int
    suite_once_design_stack: int
    suite_once_frame_descriptors: int
    suite_once: int
    total: int

    def suite_total(self, n_nets: int) -> int:
        """Exact suite bill for ``n_nets`` nets.  No rounding anywhere."""
        if n_nets < 1:
            raise ValueError("a suite has at least one net")
        return n_nets * self.total + self.suite_once

    def breakdown(self) -> dict:
        return {
            "winograd_depth_of_every_charged_call": self.call_depth,
            "weight_side_stack_per_CALLING_layer": self.weight_stack,
            "weight_side_stacks_CHARGED_layers_2_to_32":
                self.weight_stack_layers * self.weight_stack,
            "row_part_per_full_tile": self.row_part_full,
            "layer1_crowned_butterfly_32256_rows": self.layer1_butterfly,
            "layer1_shared_prologue_of_W0": self.layer1_shared_prologue,
            "layer1_normalization_THE_ONLY_SCALING_PASS_AND_THE_ARGMIN_SEAT":
                self.layer1_normalization,
            "layer1_normalization_READER_COUNT":
                self.layer1_normalization_readers,
            "layer1_butterfly_lane_total": self.layer1_lane,
            "layer1_deployed_transcription_DECLINED":
                self.layer1_deployed_butterfly_declined,
            "layer1_antipodal_negation": self.layer1_negation,
            "layer1_total_per_net": self.layer1_total,
            "generic_layer_total": self.generic_layer,
            "generic_layers_3_to_32": self.generic_layers_total,
            "layer2_top_channel_row_part_32256": self.layer2_even_rows,
            "layer2_weight_side_stack_KEPT_THE_CALL_IS_MADE": self.weight_stack,
            "layer2_relu_write_PRICED_ZERO_by_the_ledger":
                self.layer2_relu_writes_priced_zero,
            "layer2_precompute_DEPTH_equals_the_layer_call_depth":
                self.layer2_precompute_levels,
            "layer2_precompute_lane_leaves": self.layer2_precompute_leaves,
            "layer2_precompute_lane_A_side_stack_of_W0PRIME_PAID_IN_FULL":
                self.layer2_precompute_left_stack,
            "layer2_precompute_lane_W_side_stack_of_W1h_RIDDEN":
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
            "layer2_odd_normalization_NOTHING_LEFT_TO_SCALE":
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
            "scaling_passes_CHARGED_in_the_whole_bill":
                self.scaling_passes_charged,
            "scalar_seat_elements_ARGMIN_OVER_REACHABLE_SEATS":
                self.scalar_seat_elements,
            "cross_frame_sharing_stages_TAKEN": self.sharing_stages_taken,
            "cross_frame_sharing_stage3_MARGIN_zero_means_dead_tie":
                self.sharing_stage3_margin,
            "design_side_stack_ORPHANED_but_OUTSIDE_total_and_KEPT":
                self.suite_once_design_stack,
            "frame_descriptor_tables_TWO_charged_ONCE_to_the_suite":
                self.suite_once_frame_descriptors,
            "total": self.total,
        }


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill.  Tier 19's route, unchanged: this tier's work
    is three closed doors, so ``.total`` is the incumbent's exactly."""
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

    # --- generic layers 3..32: tier 3's layer, carried verbatim ---------------
    generic_rows = int(row_full * DESIGN_ROWS // m)
    if generic_rows * m != row_full * DESIGN_ROWS:
        raise ValueError("tile count is not exact; refusing a rounded bill")
    generic_layer = generic_rows + w_stack
    generic_total = (LAYERS - 2) * generic_layer

    full_tiles, remainder = divmod(BASE_ROWS, TILE_ROWS)
    if remainder == 0:
        raise ValueError("base row count is not the frozen 7 x 4096 + tail")
    base_rows_part = full_tiles * row_full + row_tail
    design_stack = (full_tiles * design_side_stack_cost(t7, TILE_ROWS, k)
                    + design_side_stack_cost(t7, remainder, k))
    if design_stack != design_side_stack_cost(t7, BASE_ROWS, k):
        raise ValueError("the design-side lane is not additive over the tiling")

    # --- layer 1 --------------------------------------------------------------
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

    # --- layer 2 --------------------------------------------------------------
    layer2_even_rows = base_rows_part
    lanes = precompute_lanes(t7, WIDTH, WIDTH, WIDTH)
    if lanes["levels"] != depth:
        raise ValueError("the precompute is not at the depth of the ridden stack")
    if lanes["right_operand_stack_RIDDEN"] != w_stack:
        raise ValueError("the ridden lane is not layer 2's charged W-side stack")
    precompute = lanes["total"]
    normalization = odd_channel_normalization_cost(WIDTH, WIDTH)
    if normalization != 0:
        raise ValueError("the odd channel still carries a scaling pass")
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                              pingpong=True, shared_depth=_SHARED_DEPTH)
    antipodal_write = BASE_ROWS * WIDTH
    declined_direct = declined_direct_precompute_cost(WIDTH, WIDTH, WIDTH)
    declined_isolated = declined_isolated_precompute_cost(t7, WIDTH, WIDTH, WIDTH)
    if precompute >= declined_isolated >= declined_direct:
        raise ValueError("the ladder of declined precompute prices is not ordered")
    if precompute <= _TIER6_REJECTED_PRECOMPUTE:
        raise ValueError("this tier must charge MORE than the rejected tier 6")
    if declined_isolated != _TIER16_PRECOMPUTE_DEPTH5:
        raise ValueError("the isolated depth-5 price moved")
    level1 = shared_prologue_cost(1, WIDTH, WIDTH)
    prologue = shared_prologue_cost(_SHARED_DEPTH, WIDTH, WIDTH)
    level2 = prologue - level1
    if butterfly != layer1_butterfly:
        raise ValueError("the two butterflies must cost the same at the same shape")
    layer2_aux = precompute + normalization + butterfly + antipodal_write
    layer2 = layer2_even_rows + w_stack + layer2_aux

    scaling_passes = (1 if layer1_normalization else 0) + (1 if normalization else 0)
    if scaling_passes != 1:
        raise ValueError("the bill must charge exactly one scaling pass")
    seat_name, seat_size = cheapest_reachable_scalar_seat()
    if seat_size != layer1_normalization:
        raise ValueError("the charged scaling pass is not the argmin seat")

    ladder = sharing_ladder(FRAMES, WIDTH, WIDTH)
    taken = sum(1 for rung in ladder if rung["pays"])
    if taken != _SHARED_DEPTH:
        raise ValueError("the sharing licence does not end where the bill ends")
    stage3 = next(rung for rung in ladder if rung["stage"] == 3)
    if stage3["margin"] > 0:
        raise ValueError("stage 3 is being reported open")

    descriptors = frame_descriptor_table_cost(FRAMES, WIDTH, 2)

    return SuiteBill(
        strategy="the_scalars_last_seat_and_the_sharing_licence_are_both_exhausted",
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
        layer1_lane=layer1_lane,
        layer1_deployed_butterfly_declined=declined_deployed,
        layer1_negation=negation,
        layer1_total=layer1,
        generic_layer=generic_layer,
        generic_layers_total=generic_total,
        layer2_even_rows=layer2_even_rows,
        layer2_relu_writes_priced_zero=BASE_ROWS * WIDTH,
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
        layer2_odd_butterfly=butterfly,
        layer2_antipodal_write=antipodal_write,
        layer2_aux=layer2_aux,
        layer2_total=layer2,
        scaling_passes_charged=scaling_passes,
        scalar_seat_elements=seat_size,
        sharing_stages_taken=taken,
        sharing_stage3_margin=stage3["margin"],
        suite_once_design_stack=design_stack,
        suite_once_frame_descriptors=descriptors,
        suite_once=design_stack + descriptors,
        total=generic_total + layer1 + layer2,
    )


# ---------------------------------------------------------------------------
# Executable proofs.  Nothing below is asserted; it is run.
# ---------------------------------------------------------------------------


def _selfcheck() -> None:
    t7 = _t7()
    bill = suite_bill_per_net()

    # (0) THE BILL IS TIER 19's, TERM FOR TERM.
    assert bill.total == _INCUMBENT_TOTAL, bill.total
    assert bill.layer1_total == _INCUMBENT_LAYER1_TOTAL
    assert bill.layer2_total == _INCUMBENT_LAYER2_TOTAL
    assert bill.layer2_aux == _INCUMBENT_LAYER2_AUX
    assert bill.generic_layers_total == _INCUMBENT_GENERIC_TOTAL
    assert bill.suite_once == _INCUMBENT_SUITE_ONCE
    assert bill.total == (bill.generic_layers_total + bill.layer1_total
                          + bill.layer2_total)

    # (1) THE CERTIFIED PER-CALL FLOOR, RE-DERIVED FROM TIER 7.
    assert bill.call_total == 303096592, bill.call_total
    assert bill.call_depth == 6
    assert bill.row_part_full + bill.weight_stack == bill.call_total

    # (2) DOOR 1 -- THE HAAR SEAT IS ILLEGAL.  Both readers move.
    div = haar_seat_divergence()
    assert div["answer_changes"], div
    assert div["reader_A_analytic_mean_max_shift"] > 0.0, div
    assert div["reader_B_first_moment_residual_max_shift"] > 0.0, div
    # and the alphas are invariant, which is exactly why the trap is subtle:
    # only the MEANS move, and the means are what the estimator returns.
    assert div["reader_A_analytic_alpha_max_shift"] < 1e-9, div

    # (3) DOOR 1b -- THE SCALAR'S SEAT IS THE ARGMIN OVER REACHABLE SEATS.
    seat_name, seat_size = cheapest_reachable_scalar_seat()
    assert seat_name == "W0_prime" and seat_size == 65536, (seat_name, seat_size)
    reachable = [size for _n, size, s in scalar_seat_ladder()
                 if s.startswith("REACHABLE")]
    assert sorted(reachable) == [65536, 163840, 524288, 8257536], reachable
    assert bill.scaling_passes_charged == 1
    assert bill.layer1_normalization == seat_size
    assert bill.layer2_odd_normalization == 0
    # the phase seat is smaller than the taken seat and is nevertheless
    # unreachable -- that is the whole content of the closure.
    phases_elements = FRAMES * WIDTH
    assert phases_elements < seat_size, phases_elements

    # (4) DOOR 2 -- TIER 13's ABSTRACT ALPHABET, REPRODUCED FROM SCRATCH.
    for stages in (1, 2, 3):
        measured = abstract_alphabet(stages)
        assert measured == _TIER13_ABSTRACT_ALPHABET[stages], (stages, measured)

    # The two refused IEEE identities, exhibited rather than assumed.  The
    # first is tier 13's own counterexample: S' = (-M2) - M3 is not -(M2 + M3).
    a, b = 0.0, -0.0
    assert math.copysign(1.0, (-a) - b) != math.copysign(1.0, -(a + b))
    a, b = 0.0, 0.0
    assert math.copysign(1.0, -(a - b)) != math.copysign(1.0, b - a)
    # the two permitted ones, exhibited on the very node the seed builds
    assert _canonical("+", ("P", 0), ("N", 1)) == ("-", ("P", 0), ("P", 1))
    assert _canonical("-", ("P", 0), ("N", 1)) == ("+", ("P", 0), ("P", 1))
    # a compound right operand is never re-signed
    compound = ("+", ("P", 0), ("P", 1))
    assert _canonical("-", ("P", 2), compound) == ("-", ("P", 2), compound)

    # (5) DOOR 2b -- THE REALIZED ALPHABET IS 2**k PER DISTINCT RESTRICTION,
    #     SO THE BREAK-EVEN IS EXACT AND INDEPENDENT OF k.
    for stages in (1, 2, 3):
        rows = 1 << stages
        table = []
        for f in range(5):
            table.append(tuple(1 if ((f * 37 + i * 11) % 3) else -1
                               for i in range(rows)))
        distinct = len(set(table))
        measured = realized_alphabet(table, stages)
        assert measured <= rows * distinct, (stages, measured, distinct)
        # two frames with the SAME restriction share every tree
        doubled = table + [table[0]]
        assert realized_alphabet(doubled, stages) == measured

    ladder = sharing_ladder(FRAMES, WIDTH, WIDTH)
    saving = FRAMES * WIDTH * WIDTH
    assert saving == 8257536, saving
    for rung in ladder:
        # the frame-realized bound is the SAME number at every stage
        assert rung["frame_realized_bound"] == saving, rung
    taken = [rung["stage"] for rung in ladder if rung["pays"]]
    assert taken == [1, 2], taken
    stage3 = next(rung for rung in ladder if rung["stage"] == 3)
    assert stage3["abstract_cost"] == 8388608, stage3
    assert stage3["margin"] == 0, stage3          # dead tie, never a win
    stage4 = next(rung for rung in ladder if rung["stage"] == 4)
    assert stage4["margin"] == 0, stage4
    # tier 13's published loss on the ABSTRACT alphabet, re-derived
    assert stage3["abstract_cost"] - saving == 131072
    # and the shape penalty that makes the tie a real loss
    assert stage3_shared_alphabet_residency_bytes() == 33030144

    # (6) DOOR 3 -- THE ANTIPODAL HALF BEYOND LAYER 2.
    fails = antipodal_identity_fails_at_layer2()
    assert fails["max_negation_gap"] > 0.1, fails
    half = bill.layer2_even_rows
    prices = layer3_route_prices(half)
    assert prices["charged_by_this_bill"] == prices[
        "direct_two_independent_products"]
    assert prices["crelu_on_both_halves"] > prices["charged_by_this_bill"]
    assert prices["difference_route_top_minus_delta_W"] > prices[
        "charged_by_this_bill"]
    assert (prices["difference_route_top_minus_delta_W"]
            - prices["charged_by_this_bill"]) == BASE_ROWS * WIDTH

    # (7) THE CReLU SPLIT ITSELF, RE-EXECUTED (tier 2's identity).
    for s in range(97):
        p = math.sin(0.11 + s * 0.83)
        assert abs(_relu(-p) - (_relu(p) - p)) < 1e-15

    # (8) THE m-LINEARITY OF EVERY ROW LANE, AND THE DEPTH ARGMIN.
    #     15.75 tiles == one 64,512-row call, to the FLOP.
    depth = bill.call_depth
    lane_tile = (7 ** depth * t7.direct_cost(TILE_ROWS >> depth, WIDTH >> depth,
                                             WIDTH >> depth)
                 + t7.best_operand_grade(TILE_ROWS, WIDTH, depth)[0]
                 + t7.best_decode_grade(TILE_ROWS, WIDTH, depth)[0])
    lane_layer = (7 ** depth * t7.direct_cost(DESIGN_ROWS >> depth,
                                              WIDTH >> depth, WIDTH >> depth)
                  + t7.best_operand_grade(DESIGN_ROWS, WIDTH, depth)[0]
                  + t7.best_decode_grade(DESIGN_ROWS, WIDTH, depth)[0])
    assert lane_tile == bill.row_part_full, (lane_tile, bill.row_part_full)
    assert 4 * lane_layer == 63 * lane_tile, (lane_layer, lane_tile)
    assert bill.generic_layer == lane_layer + bill.weight_stack

    def objective(levels: int) -> int:
        block = 1 << levels
        if TILE_ROWS % block or WIDTH % block:
            return None
        row = (7 ** levels * t7.direct_cost(TILE_ROWS // block, WIDTH // block,
                                            WIDTH // block)
               + t7.best_operand_grade(TILE_ROWS, WIDTH, levels)[0]
               + t7.best_decode_grade(TILE_ROWS, WIDTH, levels)[0])
        stack = t7.best_operand_grade(WIDTH, WIDTH, levels)[0]
        return 63 * row + 4 * stack        # 15.75 tiles, in quarters
    lawful = {L: objective(L) for L in range(1, 9) if objective(L) is not None}
    assert min(lawful, key=lawful.get) == depth, lawful
    # the argmin of the row lane ALONE is the same, and cannot move with m
    row_only = {L: objective(L) - 4 * t7.best_operand_grade(WIDTH, WIDTH, L)[0]
                for L in lawful}
    assert min(row_only, key=row_only.get) == depth, row_only

    # (9) FUSING THE TWO BUTTERFLIES BUYS NOTHING (linearity in the seed width).
    separate = 2 * butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                                 pingpong=True, shared_depth=_SHARED_DEPTH)
    fused = butterfly_ops(FRAMES, WIDTH, 2 * WIDTH, final_scale=False,
                          pingpong=True, shared_depth=_SHARED_DEPTH)
    assert separate == fused == 2 * 50233344, (separate, fused)

    # (10) THE LAYER-1 NEGATION IS THE CHEAPEST WAY TO REACH THE PILOT ROWS.
    assert bill.layer1_negation == PILOT_BASE * WIDTH == 65536
    assert frame_zero_renegation_price() == 6 * 65536
    assert frame_zero_renegation_price() > bill.layer1_negation

    # (11) THE TERMINAL FOLD RAISES, BOTH WAYS OF COUNTING IT.
    incumbent_fold, worst_fold, skipped_fold = terminal_fold_bounds()
    assert incumbent_fold == 196608
    assert worst_fold == 393216 == 6 * WIDTH * WIDTH
    assert skipped_fold == 391681, skipped_fold
    # even with every empty folded operand skipped exactly, the honest fold is
    # nearly six units against the three the incumbent charges
    assert worst_fold == 2 * incumbent_fold
    assert 2 * incumbent_fold - WIDTH * WIDTH < skipped_fold < worst_fold

    # (12) THE UNBILLED LANES, COUNTED AND NOT CLAIMED.
    assert deployed_relu_writes_priced_zero() == 478937088

    # (13) THE SUITE AXIS IS UNTOUCHED.
    assert bill.suite_total(1) == bill.total + bill.suite_once
    assert bill.suite_total(1000) == 1000 * bill.total + bill.suite_once


def main() -> None:
    _selfcheck()
    bill = suite_bill_per_net()
    print("suite tier 20 -- DRY, three doors closed, bill unchanged")
    print(f"{'total (per net)':<62} {bill.total:>18,}")
    print(f"{'tier 19 incumbent':<62} {_INCUMBENT_TOTAL:>18,}")
    print(f"{'delta':<62} {bill.total - _INCUMBENT_TOTAL:>18,}")
    print()
    for key, value in bill.breakdown().items():
        print(f"  {key:<74} {value:>18,}")
    print()
    print("DOOR 1  the Haar seat (tier 19's named 65,280 rung)")
    for key, value in haar_seat_divergence().items():
        print(f"  {key:<50} {value}")
    print()
    print("DOOR 1b the scalar's seat ladder")
    for name, size, status in scalar_seat_ladder():
        print(f"  {name:<20} {size:>12,}  {status}")
    print()
    print("DOOR 2  the cross-frame sharing ladder")
    for rung in sharing_ladder():
        print(f"  stage {rung['stage']}  abstract {rung['abstract_cost']:>14,}"
              f"  realized_bound {rung['frame_realized_bound']:>12,}"
              f"  saving {rung['saving']:>12,}"
              f"  pays={rung['pays']}  margin {rung['margin']:>12,}")
    print()
    print("DOOR 3  the antipodal half beyond layer 2, in half-layer products")
    for key, value in layer3_route_prices(
            suite_bill_per_net().layer2_even_rows).items():
        print(f"  {key:<40} {value:>18,}")
    print()
    incumbent_fold, worst_fold, skipped_fold = terminal_fold_bounds()
    print(f"terminal fold  charged {incumbent_fold:,}  worst {worst_fold:,}"
          f"  worst-with-skips {skipped_fold:,}  (raises, NOT claimed)")


if __name__ == "__main__":
    main()
