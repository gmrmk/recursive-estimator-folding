"""Suite tier 27: DRY.  The one live equation in the neighbouring corpus -- the
terminal-route fold, 7,419,079,616 billed ops on the FOLDED layers 29..31,
rejected there on a 0.500% bar at 0.446% -- does not transfer, and the bar is
not why.  The bar was never the binding constraint.  The BASELINE is.

    suite bill, per net     144,867,083,088   ->   144,867,083,088   (unchanged)

Tiers 20, 25 and 26 closed the SAMPLED-schedule doors: the design scalar's last
seat, the cross-frame sharing licence, the shared-operand axis, and the Winograd
transform domain at every one of the thirty ReLU boundaries.  Not one of them
walked the FOLD route -- the three terminal layers the deployed champion does
not sample at all but folds [fold3_estimator.py:130-232].  That route is the
only place in either corpus where a MEASURED and UNCLAIMED saving still sits, so
it gets adjudicated here rather than left for the next ten tiers.

It is unclaimable, for three reasons, each executed rather than asserted, and
the first alone is fatal.  P4: a door genuinely closed by a search is a paid
outcome.

DOOR 7.  THE AMENDMENT IS ONE WINOGRAD LEVEL.  THIS BILL ALREADY CHARGES SIX
============================================================================
``route_terminal_matmul`` [terminal_route_census.py:47-93] is exactly one level:
seven half-size leaf products, three stack fills, one output add lane, and an
odd-dimension tail.  Every charged call in THIS bill runs at depth 6, which is
the strict argmin of the tier-7 module and is asserted as such in every file
from tier 14 onward.  At the bill's own shape the two prices are:

    charged, depth 6, (64,512, 256, 256)                4,745,522,832
    the amendment, depth 1, same shape                  7,427,768,320
                                                       ---------------
    regression, per terminal layer                      2,682,245,488
    over layers 30, 31, 32                              8,046,736,464

    suite bill under the amendment                    152,913,819,552

and the ordering is not an accident of one shape.  The module's own depth sweep
at the anonymous tile is monotone down to its argmin,

    depth 1   470,876,160   <- the amendment's depth
    depth 2   415,535,104
    depth 3   369,662,976
    depth 4   333,938,944
    depth 5   310,354,368
    depth 6   303,096,592   <- charged, the strict argmin
    depth 7   320,108,124
    depth 8   375,826,177

so depth 1 -- the amendment's depth -- is the WORST lawful route in the whole
eight-deep lattice, by 55.4%.  Scoring the amendment by its OWN accounting
rather than the module's does not rescue it, and does not even flatter it: its
depth-1 tile price is 471,711,744, slightly ABOVE the module's own depth-1 price
of 470,876,160, and 55.6% above the 303,096,592 this bill charges.  The same
holds at the only other shape in the bill, the 256-row precompute: the amendment
prices it at 29,589,504 where the bill charges 18,823,840.

THE WHOLE OF THE MEASURED SAVING IS THE GAP ``direct`` -> ONE LEVEL, AND THIS
BILL HAS NO ``direct``-PRICED PRODUCT.  ``direct_cost(m, k, n) = m n (2k - 1)``
[terminal_route_census.py:40-44] is the census's baseline because the champion's
terminal fold reaches ``fnp`` through a plain ``@`` -- the row-blocked Winograd
operator is installed on ``_sample_matmul`` and ``_first_sample_matmul`` only
[estimator.py:18-23], and the fold calls neither [fold3_estimator.py:146, :166-
170, :200-206].  The suite bill made the opposite choice at tier 3 and has never
revisited it: its direct counterfactual is a DECLINED field, carried at
33,488,896 so it can be refused in public.  A route that beats ``direct`` has
nothing to beat here.

DOOR 8.  REACHING THE AMENDMENT'S SHAPES COSTS 9,967,321,584 BEFORE IT RUNS
===========================================================================
The bill is 32-uniform across its thirty generic layers: layers 3..32 are billed
identically at (64,512, 256, 256), and the fold is not modelled.  Tier 19 named
that and bounded it in shape area only [suite_19 docstring, "CARRIED -- THE
TERMINAL FOLD"]: 196,608 charged against a worst case of 393,216, exactly 2x.
The amendment's shapes only exist inside the fold, so the fold has to be
modelled first.  This tier prices tier 19's 2x to the FLOP, off the champion's
own code, at the worst case the PRUNING door mandates:

    layer 30   x           @ W29[:, kink30]                        1 product
    layer 31   x           @ (W29[:, on29] W30[on29, kink31])
               x30_kink    @ W30[kink30, kink31]                   2 products
    layer 32   x           @ (folded29_to31_on W31[on30, kink32])
               x30_kink    @ (kink30_to31_on   W31[on30, kink32])
               x31_kink    @ W31[kink31, kink32]                   3 products

Six row-side products where the 32-uniform bill charges three -- which IS tier
19's 2x, now with lanes under it:

    charged, three generic layers                      14,236,568,496
    honest fold, EVERY credit granted                  24,203,890,080
                                                      ---------------
    the raise                                           9,967,321,584
      = 3 leaf lanes            9,961,576,128
      + 3 W-side stacks             5,745,456

EVERY CREDIT IS GRANTED, AND EACH ONE IS NAMED, BECAUSE EACH COSTS THE DOOR
SOMETHING.  Three A-side stacks are charged, not six: the six products read only
three distinct left arrays (``x`` three times, ``x30_kink`` twice,
``x31_kink`` once) and tier 3's licence is one operand array per (matrix, side,
depth) however many readers.  Three decodes are charged, not six: layers 31 and
32 sum their terms before one ReLU, and the decode is linear, so the sums are
taken in the transform domain and decoded once.  The twelve pilot products at
m = 2,048 [fold3_estimator.py:136-144, :173-177, :209-213] are charged at ZERO.
The folded weight products ``W29[:, on29] W30[on29, :]`` and its two successors
are charged at ZERO.  The two summation passes over 64,512 x 256 activations are
charged at ZERO.  With all five gifts the fold still costs 9,967,321,584 more
than not modelling it.

The leaf lane is what cannot be given away, and tier 25's structural zero does
not repeat here.  Fusing layer 32's three terms on the k axis -- legal, and
``_selfcheck`` executes the block identity ``[A|B|C] [P;Q;R] = AP + BQ + CR`` --
is WORSE by 948,721,536, because the leaf lane's ``2k - 1`` is not linear in k:
one (64,512, 768, 256) product costs 10,910,297,664 in leaves where three
(64,512, 256, 256) products cost 9,961,576,128.  Tier 25's zero lived on the m
axis, where every lane IS linear.  The k axis is not the m axis.

With the fold modelled AND the amendment applied to its six products:

    suite bill under fold + amendment                 175,197,124,512
    regression against the certified floor             30,330,041,424   (20.9%)

DOOR 9.  THE ONLY VERSION OF THE FOLD THAT PAYS IS DATA, NOT SHAPE
==================================================================
The fold's saving is real and it is large.  It is not a Winograd saving at all:
it is the collapse of consecutive LINEAR maps.  A channel in the ``on`` regime
never crosses zero on the pilot, so its ReLU is the identity and the two weight
matrices around it compose.  At the all-on extreme ``kink30 = kink31 = 0`` and
the whole terminal region is ONE row-side product:

    three charged generic layers                        14,236,568,496
    all-on fold: one product + two weight folds          4,787,000,816
                                                       ---------------
    saving                                               9,449,567,680   (6.52%)

That number is not claimable and the reason is the ladder's oldest one.  The
regimes come from thresholding ``analytic_alphas`` against ``dead_alpha = -2.0``
and ``on_alpha = 3.0`` [fold_estimator.py:8-14, base_estimator.py:54,
fold3_estimator.py:20, :131-133, :156-158, :189-191], and the alphas are a
function of the net's own weights.  The suite's carried PRUNING door already
fixes the worst case at the full 256 [suite_19 docstring, "CARRIED -- PRUNING"],
and a bill that charged the all-on collapse would be wrong on the first net that
has a kink.  ``_selfcheck`` runs the champion's own regime split on two alpha
vectors, one all-on and one all-kink, and exhibits the span: ONE row-side
product against SIX, from the same code, on the same shape, with only the data
changed.  The fold is a variance-and-cost gamble the deployment takes per net.
The suite bill is a per-net constant.  They are different objects.

THE BAR WAS NOT THE BINDING CONSTRAINT, AND SAYING SO IS THE POINT
==================================================================
The census rejected its own route because 0.446% missed a frozen 0.500%
[TERMINAL_ROUTE_CENSUS_VERDICT.md].  Measured against THIS bill the same
absolute saving reads differently, because this bill is 12.8% leaner than the
ledger the census measured:

    aggregate saving, ten nets                           7,419,079,616
    census ledger, ten nets                          1,662,212,339,906  4,463 ppm
    this bill, ten nets                              1,448,670,830,880  5,121 ppm
    the frozen bar                                                      5,000 ppm

So on this ledger the route CLEARS the bar it failed on its own, and it still
does not transfer.  Recording this explicitly is the whole reason the door is
worth a tier: a later reader who noticed only that 0.446% missed 0.500% by
0.054 points would reasonably conclude the rejection was arbitrary and re-open
the route.  It was arbitrary, and it was not what killed it.  What kills it is
that its baseline is a route this bill declined at tier 3 and has out-priced by
depth 6 ever since.

DOORS THAT STAY CLOSED, AND ONE THAT IS NOW NAMED WITH ITS NUMBER
=================================================================
  * NEW -- THE ODD-DIMENSION TAIL.  The amendment carries two extra strategies,
    ``winograd_odd_input`` and ``winograd_odd_output``, for shapes with one odd
    dimension [terminal_route_census.py:79-92].  They are vacuous here: every
    shape this bill charges -- 4,096, 3,584, 32,256, 64,512 rows and 256 on both
    weight axes -- is divisible by 64, let alone by 2, and ``_selfcheck``
    enumerates them and asserts the amendment's own branch selector returns the
    plain even route at each.  The odd tails are the census's answer to PRUNED
    widths (its own receipt shows k in {98, 101, 176} and n in 84..101), and
    pruned widths are what the PRUNING door refuses.  SHUT.
  * NEW -- THE ``direct`` BASELINE.  Enumerated: this bill charges no product at
    ``direct``.  The one ``direct`` figure in it, 33,488,896, is the precompute's
    DECLINED counterfactual and sits in a ``_declined`` field.  SHUT.
  * NEW -- THE k-AXIS FUSION OF THE TERMINAL SUM.  Legal, executed, and worse by
    948,721,536.  SHUT.
  * CARRIED -- TIER 20's THREE.  The Haar sign fold is ILLEGAL, not merely
    unclaimed (it moves the answer in the fourth decimal), the scalar's seat is
    at its argmin, and the sharing licence is self-limiting.  Re-asserted.
  * CARRIED -- TIER 25's THREE.  The fused 32,512-row call is exactly zero on the
    m axis; no butterfly stage can carry the precompute; the antipodal write
    cannot ride the odd butterfly's final stage.
  * CARRIED -- TIER 26's THREE.  The transform domain cannot cross a ReLU
    (42,222,237,120 and its 1,473,970,176 basis-only form), the level-1 alphabet
    cannot fold into the precompute's decode, and the two refused IEEE
    identities cost 589,824 standing.
  * CARRIED -- PRUNING, THE LEDGER-FREE ReLU WRITES (478,937,088) AND THE SUITE-
    ONCE RESIDUE (241,341,408).  All three counted, none claimed.

EXACTNESS IDENTITY
==================
This tier proposes no route change.  The route charged below is tier 19's, term
for term, computed by the same functions on the same arguments, and every term
is asserted equal to its published value with ``.total`` at 144,867,083,088.

A door closed on COST is only closed if the route behind it was legal, so what
is executed here is the exactness of the routes NOT taken:

  (i)   ONE WINOGRAD LEVEL IS EXACT.  The amendment's depth is run through the
        module's own graded recursion at levels = 1 and the product is asserted
        equal to the dense product.  Its price is refused; its arithmetic is not
        in question, which is what makes door 7 a cost door.
  (ii)  THE FOLD IS EXACT ON THE ``on`` CHANNELS.  ``relu`` is the identity on a
        channel that never crosses zero, so ``relu(X W29) W30 = X (W29 W30)``
        there -- executed on integer matrices with a strictly positive block,
        and executed to FAIL on a block with a sign change, which is the same
        statement door 9 rests on.
  (iii) THE k-AXIS BLOCK IDENTITY.  ``[A|B|C] [P;Q;R] = AP + BQ + CR``, executed
        on integer matrices, so the fusion door is shut on price and not on
        legality.
  (iv)  THE REGIME SPLIT IS A PARTITION.  ``_initial_regimes`` transcribed and
        run: dead, kink and on are disjoint and cover the width, at both
        extremes and at a mixed vector.
  (v)   THE IDENTITIES THE CHARGED ROUTE ITSELF RESTS ON, re-run so this file
        stands alone: the scalar's associativity ``c (W0 W1h) = (c W0) W1h``,
        ``W0'`` surviving layer 1 unmodified, ``O_s = P_s W1h``, and the CReLU
        split.

f32 STATUS: NO REPRICING, NO FLAG
=================================
No op is added, removed or repriced.  The route charged is byte-for-byte tier
19's.  The three doors are closed on integer arithmetic and on the module's own
integer cost model; none of them turns on a floating-point identity, so nothing
here touches the ladder's exactness law.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A DRY tier has no metered win to repay, and its value is the wall time the next
tiers do not spend -- which is only real if the doors are shut in the shape as
well as on the ledger.

  * DOOR 7 IS SHUT HARDER IN THE SHAPE THAN ON THE LEDGER.  The amendment's own
    receipt prices its workspace at 297,988,096 bytes, 284.2 MiB, for ONE
    preallocated full-row kernel [results.json, projected_terminal_workspace_
    bytes].  The route it would replace here is already resident: the row-blocked
    operator tiles at 4,096 rows precisely so the transform-domain working set
    stays bounded [row_blocked_winograd.py, BLOCK_ROWS].  Buying a 56.5%-worse
    ledger with 284 MiB of new peak is worse on both axes, which is why this
    door does not need the ledger to close.
  * DOOR 8 WOULD BE SHAPE-NEGATIVE TOO.  Modelling the fold honestly means six
    products where three are scheduled, three extra weight-side stacks, and two
    summation passes over 64,512 x 256 activations that the ledger above forgave
    and a machine would not.
  * DOOR 9 IS THE ONE THAT IS SHAPE-POSITIVE, AND IT IS STILL REFUSED.  The
    all-on collapse deletes two whole layer products and their traffic.  It is
    named with its number, 9,449,567,680 and 6.52% of the bill, so no later tier
    re-opens it hoping the shape will pay for the data-dependence.  It will not.
    The ladder does not buy wall time with a bill that is wrong on some nets.
  * NOTHING MOVES.  The 126 frames, the 15.75 tiles, the 31 charged W-side
    stacks, the two butterflies, the one scaling pass and the single 256-row
    precompute are scheduled exactly as tier 19 schedules them.  Flat in the
    suite size: ``.total`` and ``suite_once`` are asserted at 144,867,083,088 and
    241,373,664, and ``suite_total(n) = n * .total + suite_once`` is re-derived
    at n = 1 and n = 10, the census's own suite size.

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
        strategy="the_terminal_fold_is_billed_deeper_than_the_route_that_would_amend_it",
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

# ---------------------------------------------------------------------------
# THE AMENDMENT UNDER ADJUDICATION.  Transcribed from the neighbouring corpus:
#   src/whest_chamber/terminal_route_census.py:40-93     the route
#   reports/terminal-route-census/results.json           the receipt
#   research/TERMINAL_ROUTE_CENSUS_VERDICT.md            the 0.500% bar
# and from the deployed champion whose fold produces the shapes it prices:
#   row_blocked_production/candidate_source/fold3_estimator.py:130-232
#   row_blocked_production/candidate_source/fold_estimator.py:8-32
#   row_blocked_production/candidate_source/estimator.py:18-23
# ---------------------------------------------------------------------------

_CENSUS_NETS = 10
_CENSUS_AGGREGATE_BILL = 1662212339906        # the census's own ten-net ledger
_CENSUS_AGGREGATE_SAVING = 7419079616         # what its route would save on it
_CENSUS_BAR_PPM = 5000                        # the frozen 0.500%
_CENSUS_WORKSPACE_BYTES = 297988096           # 284.2 MiB of new peak

# The champion's regime thresholds [base_estimator.py:54, fold3_estimator.py:20].
DEAD_ALPHA = -2.0
ON_ALPHA = 3.0

# The three layers the champion folds: mlp.depth-3, -2, -1 with depth 32, which
# are this bill's generic layers 30, 31 and 32.
FOLDED_LAYERS = ("layer30", "layer31", "layer32")


def certified_floor() -> int:
    """Tier 19's bill, re-certified by the DRYs of tiers 20, 25 and 26."""
    return 144867083088


# ---------------------------------------------------------------------------
# DOOR 7.  The amendment is one Winograd level; this bill charges six.
# ---------------------------------------------------------------------------


def census_route_cost(m: int, k: int, n: int) -> tuple:
    """``route_terminal_matmul`` verbatim [terminal_route_census.py:47-93].

    Returns ``(selected_cost, strategy)``.  The odd-input and odd-output tails
    are transcribed even though every shape in this bill is even, because the
    door is only shut if the branch that would have applied is shown not to.
    """
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive integers")
    plain = direct_cost(m, k, n)
    if m % 2:
        return plain, "direct"
    core_k = k - k % 2
    core_n = n - n % 2
    odd_input = k - core_k
    odd_output = n - core_n
    if core_k == 0 or core_n == 0 or (odd_input and odd_output):
        return plain, "direct"
    half_m, half_k, half_n = m // 2, core_k // 2, core_n // 2
    selected = (7 * direct_cost(half_m, half_k, half_n)
                + 7 * half_m * half_k
                + 7 * half_k * half_n
                + 7 * half_m * half_n)
    if odd_input:
        selected += direct_cost(m, 1, core_n) + m * core_n + m
    if odd_output:
        selected += direct_cost(m, k, 1) + m
    if selected >= plain:
        return plain, "direct"
    if odd_input:
        return selected, "winograd_odd_input"
    if odd_output:
        return selected, "winograd_odd_output"
    return selected, "winograd"


def charged_call_shapes() -> tuple:
    """Every (m, k, n) this bill charges a Winograd call at."""
    return ((TILE_ROWS, WIDTH, WIDTH),              # the 15 full tiles
            (BASE_ROWS % TILE_ROWS, WIDTH, WIDTH),  # the 3,584-row tail
            (DESIGN_ROWS, WIDTH, WIDTH),            # a generic layer entire
            (WIDTH, WIDTH, WIDTH))                  # the layer-2 precompute


def amendment_against_the_charged_call(t7) -> dict:
    """DOOR 7 priced: the amendment's route against the route already charged."""
    bill = suite_bill_per_net()
    charged = bill.generic_layer
    selected, strategy = census_route_cost(DESIGN_ROWS, WIDTH, WIDTH)
    per_layer = selected - charged
    return {
        "charged_generic_layer_depth6": charged,
        "amendment_same_shape_depth1": selected,
        "amendment_strategy": strategy,
        "regression_per_terminal_layer": per_layer,
        "regression_over_layers_30_31_32": 3 * per_layer,
        "suite_bill_under_the_amendment": bill.total + 3 * per_layer,
        "direct_counterfactual_DECLINED": direct_cost(DESIGN_ROWS, WIDTH, WIDTH),
    }


def module_depth_sweep(t7, m: int = TILE_ROWS) -> dict:
    """The lattice the amendment's depth sits at the bottom of."""
    sweep = {}
    for levels in range(1, 9):
        if m % (1 << levels) or WIDTH % (1 << levels):
            continue
        sweep[levels] = t7.inplace_depth_core_cost(m, WIDTH, WIDTH, levels)
    return sweep


def amendment_own_accounting_at_the_tile() -> int:
    """The amendment scored by ITS accounting, not the module's, at the tile."""
    selected, _strategy = census_route_cost(TILE_ROWS, WIDTH, WIDTH)
    return selected


# ---------------------------------------------------------------------------
# DOOR 8.  Reaching the amendment's shapes means modelling the fold, and the
# fold is a raise.  This prices tier 19's shape-area 2x to the FLOP.
# ---------------------------------------------------------------------------


def terminal_fold_products(active: int = WIDTH, kink30: int = WIDTH,
                           kink31: int = WIDTH, kink32: int = WIDTH) -> tuple:
    """The champion's own terminal fold, enumerated [fold3_estimator.py:130-232].

    Each record is ``(layer, left_array, k, n)`` at ``m = DESIGN_ROWS``.  An
    empty regime drops the products it would have fed -- which is the whole of
    the fold's saving and the whole of its data-dependence (door 9).
    """
    if min(active, kink30, kink31, kink32) < 0:
        raise ValueError("regime widths are non-negative")
    products = []
    if kink30:
        products.append(("layer30", "x", active, kink30))
    if kink31:
        products.append(("layer31", "x", active, kink31))
        if kink30:
            products.append(("layer31", "x30_kink", kink30, kink31))
    if kink32:
        products.append(("layer32", "x", active, kink32))
        if kink30:
            products.append(("layer32", "x30_kink", kink30, kink32))
        if kink31:
            products.append(("layer32", "x31_kink", kink31, kink32))
    return tuple(products)


def _lanes(t7, m: int, k: int, n: int, levels: int) -> dict:
    block = 1 << levels
    if m % block or k % block or n % block:
        raise ValueError(f"{levels} levels do not divide ({m}, {k}, {n})")
    leaves = 7 ** levels * t7.direct_cost(m // block, k // block, n // block)
    a_side, _ = t7.best_operand_grade(m, k, levels)
    decode, _ = t7.best_decode_grade(m, n, levels)
    w_side, _ = t7.best_operand_grade(k, n, levels)
    return {"leaves": leaves, "a_side": a_side, "decode": decode,
            "w_side": w_side}


def terminal_fold_lanes(t7, products=None, route: str = "charged") -> dict:
    """The honest fold's bill, with EVERY credit this ladder can legally grant.

    Credits granted, each of which costs the door something:
      * one A-side stack per DISTINCT left array, not per product (tier 3's
        licence: one operand array per (matrix, side, depth), however many
        readers);
      * one decode per LAYER, not per product -- layers 31 and 32 sum their
        terms before a single ReLU and the decode is linear, so the sums are
        taken in the transform domain;
      * the twelve pilot products at m = 2,048, the folded weight products and
        the two summation passes over 64,512 x 256 activations are all charged
        at ZERO.

    ``route="charged"`` prices the six products the way this bill prices every
    other product.  ``route="amendment"`` prices them the census's way.
    """
    bill = suite_bill_per_net()
    if products is None:
        products = terminal_fold_products()
    if route not in ("charged", "amendment"):
        raise ValueError("route is 'charged' or 'amendment'")
    depth = bill.call_depth
    leaves = a_side = decode = w_side = 0
    if route == "amendment":
        total = sum(census_route_cost(DESIGN_ROWS, k, n)[0]
                    for _layer, _left, k, n in products)
    else:
        for _layer, _left, k, n in products:
            product_lanes = _lanes(t7, DESIGN_ROWS, k, n, depth)
            leaves += product_lanes["leaves"]
            w_side += product_lanes["w_side"]
        a_side = sum(t7.best_operand_grade(DESIGN_ROWS, k, depth)[0]
                     for _layer, _left, k, _n in _distinct_lefts(products))
        decode = sum(t7.best_decode_grade(DESIGN_ROWS, n, depth)[0]
                     for _layer, n in _distinct_layer_outputs(products))
        total = leaves + a_side + decode + w_side
    charged_uniform = len(FOLDED_LAYERS) * bill.generic_layer
    return {
        "products": len(products),
        "leaves": leaves,
        "a_side_stacks": a_side,
        "decodes": decode,
        "w_side_stacks": w_side,
        "honest_fold_total": total,
        "charged_32_uniform": charged_uniform,
        "raise_over_the_uniform_bill": total - charged_uniform,
    }


def _distinct_lefts(products) -> tuple:
    """One record per DISTINCT left array: tier 3's licence on the A side."""
    seen = {}
    for layer, left, k, n in products:
        if left not in seen:
            seen[left] = (layer, left, k, n)
    return tuple(seen.values())


def _distinct_layer_outputs(products) -> tuple:
    """One decode per layer output: the summed terms are decoded once."""
    seen = {}
    for layer, _left, _k, n in products:
        if layer not in seen:
            seen[layer] = n
    return tuple(seen.items())


def k_axis_fusion_of_the_terminal_sum(t7) -> dict:
    """Layer 32's three terms stacked on the k axis: legal, and WORSE.

    ``[A|B|C] [P;Q;R] = AP + BQ + CR`` is exact and ``_selfcheck`` executes it.
    It loses because the leaf lane's ``2k - 1`` is not linear in k, which is
    exactly why tier 25's structural zero on the m axis does not repeat here.
    """
    bill = suite_bill_per_net()
    depth = bill.call_depth
    one = _lanes(t7, DESIGN_ROWS, WIDTH, WIDTH, depth)
    split = 3 * one["leaves"] + 3 * one["a_side"] + one["decode"] + 3 * one["w_side"]
    fused_lanes = _lanes(t7, DESIGN_ROWS, 3 * WIDTH, WIDTH, depth)
    fused = sum(fused_lanes.values())
    return {
        "split_three_products_one_decode": split,
        "fused_64512_768_256": fused,
        "delta_fused_minus_split": fused - split,
        "split_leaves": 3 * one["leaves"],
        "fused_leaves": fused_lanes["leaves"],
    }


def suite_bill_under_fold_and_amendment(t7) -> dict:
    """The amendment's end state: the fold modelled, then its route applied."""
    bill = suite_bill_per_net()
    charged_fold = terminal_fold_lanes(t7, route="charged")
    amended_fold = terminal_fold_lanes(t7, route="amendment")
    uniform = charged_fold["charged_32_uniform"]
    return {
        "fold_modelled_charged_route": bill.total - uniform
                                       + charged_fold["honest_fold_total"],
        "fold_modelled_amendment_route": bill.total - uniform
                                         + amended_fold["honest_fold_total"],
        "regression_against_the_floor": (bill.total - uniform
                                         + amended_fold["honest_fold_total"]
                                         - bill.total),
    }


# ---------------------------------------------------------------------------
# DOOR 9.  The only version of the fold that pays is data, not shape.
# ---------------------------------------------------------------------------


def initial_regimes(alpha, dead_alpha: float = DEAD_ALPHA,
                    on_alpha: float = ON_ALPHA) -> tuple:
    """``_initial_regimes`` verbatim [fold_estimator.py:8-14], in plain Python."""
    dead = tuple(j for j, a in enumerate(alpha) if a < dead_alpha)
    kink = tuple(j for j, a in enumerate(alpha)
                 if dead_alpha <= a <= on_alpha)
    on = tuple(j for j, a in enumerate(alpha) if a > on_alpha)
    return dead, kink, on


def all_on_collapse_price(t7) -> dict:
    """What the fold saves when every terminal channel is ``on``.  NOT CLAIMED.

    With ``kink30 = kink31 = 0`` the ReLU is the identity on every channel the
    fold carries, the two weight matrices around it compose, and the whole
    terminal region is ONE row-side product plus two (256, 256, 256) weight
    folds.  The regimes are thresholds on ``analytic_alphas``, which are a
    function of the net's own weights, so this is a statement about DATA.  The
    bill charges the worst case, which is the full 256 [suite_19 docstring,
    "CARRIED -- PRUNING"].
    """
    bill = suite_bill_per_net()
    collapsed = terminal_fold_products(WIDTH, 0, 0, WIDTH)
    lanes = _lanes(t7, DESIGN_ROWS, WIDTH, WIDTH, bill.call_depth)
    weight_fold = t7.inplace_depth_core_cost(WIDTH, WIDTH, WIDTH,
                                             bill.call_depth)
    total = sum(lanes.values()) + 2 * weight_fold
    uniform = len(FOLDED_LAYERS) * bill.generic_layer
    return {
        "row_side_products": len(collapsed),
        "one_product_plus_two_weight_folds": total,
        "charged_32_uniform": uniform,
        "saving_NOT_CLAIMED": uniform - total,
        "ppm_of_total_NOT_CLAIMED": (uniform - total) * 10 ** 6 // bill.total,
        "worst_case_row_side_products": len(terminal_fold_products()),
    }


def census_bar_reading() -> dict:
    """The bar the census failed, read against BOTH ledgers.  Integers only."""
    bill = suite_bill_per_net()
    ours = bill.suite_total(_CENSUS_NETS) - bill.suite_once
    return {
        "aggregate_saving_ten_nets": _CENSUS_AGGREGATE_SAVING,
        "census_ledger_ten_nets": _CENSUS_AGGREGATE_BILL,
        "census_ppm": _CENSUS_AGGREGATE_SAVING * 10 ** 6 // _CENSUS_AGGREGATE_BILL,
        "this_bill_ten_nets": ours,
        "this_bill_ppm": _CENSUS_AGGREGATE_SAVING * 10 ** 6 // ours,
        "the_frozen_bar_ppm": _CENSUS_BAR_PPM,
        "workspace_bytes_the_amendment_adds": _CENSUS_WORKSPACE_BYTES,
    }


# ---------------------------------------------------------------------------
# Executable exactness for the three new doors, on top of tier 19's carried set.
# ---------------------------------------------------------------------------


def _hstack(blocks):
    return [sum((block[i] for block in blocks), []) for i in range(len(blocks[0]))]


def _vstack(blocks):
    return [row[:] for block in blocks for row in block]


def _add(A, B):
    return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def _selfcheck() -> None:
    t7 = _t7()
    bill = suite_bill_per_net()
    nxt = _rng(20260817)

    # ---- 0. NOTHING MOVED.  This is tier 19's bill, term for term. ---------
    assert bill.total == certified_floor() == 144867083088
    assert bill.call_depth == 6
    assert bill.call_total == 303096592
    assert bill.row_part_full == 301181440 and bill.row_part_tail == 263533760
    assert bill.generic_layer == 4745522832
    assert bill.generic_layers_total == _INCUMBENT_GENERIC_TOTAL == 142365684960
    assert bill.layer1_total == _INCUMBENT_LAYER1_TOTAL == 50364416
    assert bill.layer2_total == 2451033712 == _INCUMBENT_LAYER2_TOTAL - 65536
    assert bill.layer2_aux == 77314720 == _INCUMBENT_LAYER2_AUX - 65536
    assert bill.layer2_precompute == 18823840
    assert bill.layer2_odd_normalization == 0
    assert bill.layer2_odd_normalization_ridden == 65536
    assert bill.layer1_normalization == 65536
    assert bill.layer1_normalization_readers == 2
    assert bill.scaling_passes_charged == 1
    assert bill.weight_stack == 1915152 and bill.weight_stack_layers == 31
    assert bill.suite_once_design_stack == 241309152
    assert bill.suite_once == _INCUMBENT_SUITE_ONCE == 241373664
    assert incumbent_total() - bill.total == 65536      # tier 19's own delta
    assert incumbent_total() == 144867148624            # tier 18's ancestry
    assert bill.total == (bill.generic_layers_total + bill.layer1_total
                          + bill.layer2_total)
    assert bill.suite_total(1) == bill.total + bill.suite_once
    assert bill.suite_total(_CENSUS_NETS) == (_CENSUS_NETS * bill.total
                                              + bill.suite_once)
    #     The lane decomposition of a generic layer, which doors 8 and 9 use.
    lanes = _lanes(t7, DESIGN_ROWS, WIDTH, WIDTH, bill.call_depth)
    assert lanes == {"leaves": 3320525376, "a_side": 482618304,
                     "decode": 940464000, "w_side": 1915152}
    assert sum(lanes.values()) == bill.generic_layer

    # ---- 1. DOOR 7.  ONE LEVEL IS EXACT, AND IT IS THE WORST LAWFUL DEPTH. -
    #     (a) exact: the amendment's depth run through the module's own graded
    #         recursion reproduces the dense product.  The door is a COST door.
    for pattern in ([True], [False]):
        a = _mat(4, 2, nxt)
        b = _mat(2, 2, nxt)
        leaves, counters = [], {"left": 0, "right": 0, "decode": 0}
        psi = {"a": [0], "b": [0], "c": [0]}
        one_level = graded_route(t7, a, b, list(pattern), list(pattern),
                                 list(pattern), leaves, counters, psi)
        assert one_level == _mm(a, b), "one Winograd level is not exact"
        assert len(leaves) == 7, "one level is not seven leaf products"

    #     (b) the sweep: depth 1 is the bottom of the lattice, depth 6 the top.
    sweep = module_depth_sweep(t7, TILE_ROWS)
    assert set(sweep) == {1, 2, 3, 4, 5, 6, 7, 8}
    assert min(sweep, key=sweep.get) == 6
    assert max(sweep, key=sweep.get) == 1
    assert sweep[1] == 470876160 and sweep[6] == 303096592
    assert sweep == {1: 470876160, 2: 415535104, 3: 369662976, 4: 333938944,
                     5: 310354368, 6: 303096592, 7: 320108124, 8: 375826177}
    assert sweep[6] == bill.call_total - bill.weight_stack + t7.best_operand_grade(
        WIDTH, WIDTH, 6)[0]
    #     and the amendment's OWN accounting is not more generous than the
    #     module's depth 1 -- it is slightly harsher -- and is far above depth 6.
    own = amendment_own_accounting_at_the_tile()
    assert own == 471711744
    assert own > sweep[1], "the amendment is being scored too harshly"
    assert own > sweep[6], "the amendment beats the charged route -- re-open"
    assert own * 63 // 4 == 7429459968      # the same route, tiled 15.75 times

    #     (c) the price at the bill's own shape.
    door7 = amendment_against_the_charged_call(t7)
    assert door7["amendment_strategy"] == "winograd"
    assert door7["charged_generic_layer_depth6"] == 4745522832
    assert door7["amendment_same_shape_depth1"] == 7427768320
    assert door7["regression_per_terminal_layer"] == 2682245488
    assert door7["regression_over_layers_30_31_32"] == 8046736464
    assert door7["suite_bill_under_the_amendment"] == 152913819552
    assert door7["suite_bill_under_the_amendment"] > bill.total

    #     (d) the same at the only other shape in the bill, the precompute.
    precompute_selected, _s = census_route_cost(WIDTH, WIDTH, WIDTH)
    assert precompute_selected == 29589504
    assert precompute_selected > bill.layer2_precompute == 18823840
    assert precompute_selected < bill.layer2_precompute_direct_declined == 33488896

    #     (e) NO PRODUCT IN THIS BILL IS PRICED AT ``direct``, so the gap the
    #         amendment monetises does not exist here.
    for m, k, n in charged_call_shapes():
        routed = t7.inplace_verbatim_leaves_candidate_bill(m, k, n).total
        assert routed < direct_cost(m, k, n), (m, k, n)
    assert bill.layer2_precompute_direct_declined == direct_cost(WIDTH, WIDTH,
                                                                 WIDTH)

    #     (f) the odd-dimension tails are vacuous at every charged shape.
    for m, k, n in charged_call_shapes():
        assert m % 64 == k % 64 == n % 64 == 0, (m, k, n)
        _cost, strategy = census_route_cost(m, k, n)
        assert strategy == "winograd", (m, k, n, strategy)
    #         and they are NOT vacuous at the census's own pruned widths, which
    #         is what the PRUNING door refuses to model.  The transcription is
    #         checked against the census's OWN receipt, row for row
    #         [reports/terminal-route-census/results.json, seed 4681]:
    for m, k, n, expected_cost, expected_strategy in (
            (2048, 98, 84, 29869126, "winograd"),
            (2048, 98, 89, 31676148, "winograd_odd_output"),
            (2048, 101, 89, 36636672, "direct"),
            (64512, 98, 97, 1085850192, "winograd_odd_output"),
            (64512, 176, 98, 1967130088, "winograd"),
            (64512, 101, 97, 1257790464, "direct")):
        cost, strategy = census_route_cost(m, k, n)
        assert (cost, strategy) == (expected_cost, expected_strategy), (
            m, k, n, cost, strategy)

    # ---- 2. DOOR 8.  MODELLING THE FOLD IS A RAISE, PRICED TO THE FLOP. ----
    products = terminal_fold_products()
    assert len(products) == 6
    assert tuple(layer for layer, _l, _k, _n in products) == (
        "layer30", "layer31", "layer31", "layer32", "layer32", "layer32")
    assert tuple(left for _layer, left, _k, _n in products) == (
        "x", "x", "x30_kink", "x", "x30_kink", "x31_kink")
    assert len(_distinct_lefts(products)) == 3
    assert len(_distinct_layer_outputs(products)) == 3 == len(FOLDED_LAYERS)

    door8 = terminal_fold_lanes(t7, route="charged")
    assert door8["products"] == 6
    assert door8["leaves"] == 6 * lanes["leaves"] == 19923152256
    assert door8["a_side_stacks"] == 3 * lanes["a_side"] == 1447854912
    assert door8["decodes"] == 3 * lanes["decode"] == 2821392000
    assert door8["w_side_stacks"] == 6 * lanes["w_side"] == 11490912
    assert door8["honest_fold_total"] == 24203890080
    assert door8["charged_32_uniform"] == 14236568496 == 3 * bill.generic_layer
    assert door8["raise_over_the_uniform_bill"] == 9967321584
    #     and the raise is EXACTLY three leaf lanes plus three W-side stacks:
    #     the two lanes the tier-3 licence cannot waive.
    assert door8["raise_over_the_uniform_bill"] == (3 * lanes["leaves"]
                                                    + 3 * lanes["w_side"])
    #     which is tier 19's shape-area bound, now with FLOPs under it.
    incumbent_fold, honest_fold = terminal_fold_bounds()
    assert incumbent_fold == 3 * WIDTH * WIDTH == 196608
    assert honest_fold == 6 * WIDTH * WIDTH == 393216 == 2 * incumbent_fold
    assert len(products) == 6 and len(FOLDED_LAYERS) == 3   # the same 2x

    #     the fold's own exactness, executed: relu is the identity on an ``on``
    #     channel, so the two weight matrices around it compose -- and it FAILS
    #     the moment a channel crosses zero, which is door 9's whole content.
    for width in (4, 8):
        w29 = _mat(width, width, nxt)
        w30 = _mat(width, width, nxt)
        positive = [[nxt(1, 9) for _ in range(width)] for _ in range(3)]
        pre = _mm(positive, w29)
        if min(v for row in pre for v in row) > 0:
            assert _mm(_relu(pre), w30) == _mm(positive, _mm(w29, w30)), (
                "the on-channel fold is not the composed linear map")
        crossing = _mm(positive, [[-v for v in row] for row in w29])
        assert _mm(_relu(crossing), w30) != _mm(
            positive, _mm([[-v for v in row] for row in w29], w30)), (
            "a sign-crossing channel folded anyway -- door 9 is unsound")

    #     the k-axis fusion: exact, executed, and worse.
    A = _mat(6, 3, nxt); B = _mat(6, 3, nxt); C = _mat(6, 3, nxt)
    P = _mat(3, 4, nxt); Q = _mat(3, 4, nxt); R = _mat(3, 4, nxt)
    assert _mm(_hstack([A, B, C]), _vstack([P, Q, R])) == _add(
        _add(_mm(A, P), _mm(B, Q)), _mm(C, R)), "the k-axis block identity fails"
    fusion = k_axis_fusion_of_the_terminal_sum(t7)
    assert fusion["split_three_products_one_decode"] == 12355640496
    assert fusion["fused_64512_768_256"] == 13304362032
    assert fusion["delta_fused_minus_split"] == 948721536 > 0
    assert fusion["split_leaves"] == 9961576128
    assert fusion["fused_leaves"] == 10910297664
    #     the leaf lane is not linear in k, which is why tier 25's m-axis zero
    #     does not repeat: 3 * direct(1008, 4, 4) != direct(1008, 12, 4).
    assert 3 * t7.direct_cost(1008, 4, 4) == 84672
    assert t7.direct_cost(1008, 12, 4) == 92736
    #     while the m axis IS linear, exactly as tier 25 proved.
    assert 3 * t7.direct_cost(336, 4, 4) == t7.direct_cost(1008, 4, 4)

    #     the amendment's end state, with the fold modelled.
    end = suite_bill_under_fold_and_amendment(t7)
    assert end["fold_modelled_charged_route"] == 154834404672
    assert end["fold_modelled_amendment_route"] == 175197124512
    assert end["regression_against_the_floor"] == 30330041424
    assert end["fold_modelled_charged_route"] > bill.total
    assert end["fold_modelled_amendment_route"] > end["fold_modelled_charged_route"]

    # ---- 3. DOOR 9.  THE PAYING FOLD IS DATA.  THE SPAN IS EXECUTED. ------
    #     the regime split is a partition, at both extremes and in the middle.
    all_on = [9.0] * WIDTH
    all_kink = [0.0] * WIDTH
    mixed = [(-5.0 if j % 3 == 0 else 9.0 if j % 3 == 1 else 0.0)
             for j in range(WIDTH)]
    for alpha in (all_on, all_kink, mixed):
        dead, kink, on = initial_regimes(alpha)
        assert len(dead) + len(kink) + len(on) == WIDTH
        assert not (set(dead) & set(kink)) and not (set(kink) & set(on))
        assert not (set(dead) & set(on))
    assert initial_regimes(all_on) == ((), (), tuple(range(WIDTH)))
    assert initial_regimes(all_kink) == ((), tuple(range(WIDTH)), ())
    mixed_dead, mixed_kink, mixed_on = initial_regimes(mixed)
    assert len(mixed_dead) == sum(1 for j in range(WIDTH) if j % 3 == 0) == 86
    assert len(mixed_on) == sum(1 for j in range(WIDTH) if j % 3 == 1) == 85
    assert len(mixed_kink) == sum(1 for j in range(WIDTH) if j % 3 == 2) == 85

    #     the same code, the same shape, only the data changed: 1 product or 6.
    assert len(terminal_fold_products(WIDTH, 0, 0, WIDTH)) == 1
    assert len(terminal_fold_products(WIDTH, WIDTH, WIDTH, WIDTH)) == 6
    door9 = all_on_collapse_price(t7)
    assert door9["row_side_products"] == 1
    assert door9["worst_case_row_side_products"] == 6
    assert door9["one_product_plus_two_weight_folds"] == 4787000816
    assert door9["charged_32_uniform"] == 14236568496
    assert door9["saving_NOT_CLAIMED"] == 9449567680
    assert door9["ppm_of_total_NOT_CLAIMED"] == 65229          # 6.52%
    assert bill.total == certified_floor(), "door 9 was claimed -- it must not be"

    # ---- 4. THE BAR WAS NOT THE BINDING CONSTRAINT. -----------------------
    bar = census_bar_reading()
    assert bar["aggregate_saving_ten_nets"] == 7419079616
    assert bar["census_ledger_ten_nets"] == 1662212339906
    assert bar["census_ppm"] == 4463 < _CENSUS_BAR_PPM      # its own verdict
    assert bar["this_bill_ten_nets"] == 10 * bill.total == 1448670830880
    assert bar["this_bill_ppm"] == 5121 > _CENSUS_BAR_PPM   # and it CLEARS here
    assert bar["workspace_bytes_the_amendment_adds"] == 297988096
    #     and the route is refused anyway, which is the point of recording it.
    assert bill.total == certified_floor()

    # ---- 5. THE IDENTITIES THE CHARGED ROUTE ITSELF RESTS ON, re-run so this
    #        file stands alone.  Tier 19's, verbatim. -----------------------
    for width in (4, 8):
        hadamard = _hadamard(width)
        w0 = _mat(width, width, nxt)
        w1 = _mat(width, width, nxt)
        for c in (1, 3, -2):
            w0_prime = _scale(c, w0)
            signs = [1 if nxt(0, 1) else -1 for _ in range(width)]
            design = design_block(signs, hadamard)
            p = layer1_route(signs, w0_prime)
            assert p == _mm(design, w0_prime)
            cm_new = _mm(w0_prime, w1)
            assert cm_new == _scale(c, _mm(w0, w1))          # associativity
            o_new = layer1_route(signs, cm_new)
            assert o_new == _mm(p, w1) == _mm(design, cm_new)
            t_top = _mm(_relu(p), w1)
            assert _mm(_relu(_neg(p)), w1) == _sub(t_top, o_new)   # CReLU
    w0_prime = _mat(16, 16, nxt)
    before = [row[:] for row in w0_prime]
    signs = [1 if nxt(0, 1) else -1 for _ in range(16)]
    _ = layer1_route(signs, w0_prime)
    assert w0_prime == before, "layer 1 wrote its weight operand"

    # ---- 6. THE CARRIED DOORS, RE-ASSERTED AND NONE CLAIMED. -------------
    assert next_rung_haar_fold_price(WIDTH) == 65280         # tier 20: ILLEGAL
    assert deployed_relu_writes_priced_zero(WIDTH) == 478937088
    assert bill.layer2_relu_pass == 0
    assert tier6_rejected_total() < bill.total               # cheaper, refused
    assert deployed_operator_fallback_total() > bill.total
    assert bill.layer2_precompute_isolated_declined == _TIER16_PRECOMPUTE_DEPTH5
    assert bill.suite_once_frame_descriptors == 64512 == 2 * FRAMES * WIDTH
    #     the certified per-call floor is untouched.
    assert t7.inplace_verbatim_leaves_candidate_bill(
        TILE_ROWS, WIDTH, WIDTH).total == 303096592

    # ---- 7. NOTHING MOVED.  The delta against the floor is exactly zero. --
    assert suite_bill_per_net().total - certified_floor() == 0


def main() -> None:
    _selfcheck()
    t7 = _t7()
    bill = suite_bill_per_net()
    print(f"strategy                  {bill.strategy}")
    print(f"suite bill, per net       {bill.total:,}")
    print(f"certified floor (t19/26)  {certified_floor():,}")
    print(f"delta                     {bill.total - certified_floor():,}   DRY")
    print()
    for key, value in bill.breakdown().items():
        print(f"  {key:<70} {value:>18,}")
    print()
    print("DOOR 7  the amendment is one Winograd level; this bill charges six")
    for key, value in amendment_against_the_charged_call(t7).items():
        print(f"  {key:<62} {value if isinstance(value, str) else format(value, ',')}")
    sweep = module_depth_sweep(t7)
    print("  module depth sweep at (4096, 256, 256)")
    for levels, cost in sweep.items():
        if levels == 1:
            mark = "   <- the amendment's depth, the WORST lawful route"
        elif cost == min(sweep.values()):
            mark = "   <- charged"
        else:
            mark = ""
        print(f"    depth {levels:<56} {cost:>18,}{mark}")
    print(f"  {'amendment scored by ITS OWN accounting, per tile':<62} "
          f"{amendment_own_accounting_at_the_tile():,}")
    print()
    print("DOOR 8  reaching those shapes means modelling the fold, and that is a raise")
    for key, value in terminal_fold_lanes(t7).items():
        print(f"  {key:<62} {value:>18,}")
    for key, value in k_axis_fusion_of_the_terminal_sum(t7).items():
        print(f"  {key:<62} {value:>18,}")
    for key, value in suite_bill_under_fold_and_amendment(t7).items():
        print(f"  {key:<62} {value:>18,}")
    print()
    print("DOOR 9  the only version of the fold that pays is DATA, and it is NOT CLAIMED")
    for key, value in all_on_collapse_price(t7).items():
        print(f"  {key:<62} {value:>18,}")
    print()
    print("THE BAR WAS NOT THE BINDING CONSTRAINT")
    for key, value in census_bar_reading().items():
        print(f"  {key:<62} {value:>18,}")


if __name__ == "__main__":
    main()
