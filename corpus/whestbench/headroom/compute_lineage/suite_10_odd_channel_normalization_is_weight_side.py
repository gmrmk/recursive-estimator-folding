"""Suite tier 10: the odd channel's butterfly carries the DESIGN NORMALIZATION
as a whole-block final pass over 8,257,536 output elements, but the constant is
a scalar on a linear route and belongs on the 65,536-element matrix the route
builds itself -- so the butterfly's whole-block passes drop from two to one.

ONE SUBSTANTIVE CHANGE
======================
The route is not touched anywhere else.  Tier 8's layer-2 route is carried
verbatim, operation for operation, with tier 9's accounting of its elementwise
lane:

    t = relu(z) W2          o = z (W1 W2)
    pre2_top    = t         pre2_bottom = t - o

What moves is one hard-coded constant in the price of ``o``.  Tier 2 built the
odd channel as a phased-WHT butterfly and priced it by transcribing the deployed
layer-1 hook's op sequence verbatim, including that hook's closing pass:

    fnp.multiply(phases[:, :, None], weight[None, :, :], out=frames)   # E
    8 radix-2 stages, copyto + add + subtract on halves                # 12E
    fnp.multiply(output, MEAN_CHI_256 / 16.0, out=output)              # E
                                        [CODEX_HANDOFF_20260810.md:360-368]

The closing pass is one scalar multiply per output element -- E = 32,256 x 256 =
8,257,536 of them -- and the scalar is ``MEAN_CHI_256 / 16.0``, the design's own
radius normalization, net-independent and suite-independent.  A scalar commutes
with H and with diag(phase), so it can be applied to the 256 x 256 matrix the
odd channel multiplies instead of to the 8,257,536-element block it produces:

    odd-channel normalization pass, 32,256 x 256    8,257,536  ->     65,536
    butterfly per element                                 14  ->         13
    butterfly, 13 x 32,256 x 256                 115,605,504  ->107,347,968

    layer-2 auxiliary total  157,351,936  ->  149,159,936      (-8,192,000)

Nothing else moves.  The even-channel matmul keeps tier 2's row count (32,256)
and tier 3's hoisted W-side stack; the precompute keeps tier 2's direct price;
the antipodal write keeps tier 8's 8,257,536 in full; the relu pass stays waived
at tier 9's zero; layer 1 keeps tier 4's base rows, tier 5's suite-once design
stack and tier 7's 256-row negation; layers 3..32 keep tier 3's generic layer
verbatim.  ``_selfcheck`` asserts every one of those terms is bit-identical to
the incumbent's and that the entire delta is the one relocated constant.

THE FROZEN CONSTANT, AND WHY IT IS ON THE WRONG SIDE
====================================================
P1: enumerate what the suite model hard-codes and take the biggest constant with
no operation behind it.  Tier 2's module names this one in a line of its own:

    _BUTTERFLY_SEED_AND_SCALE = 2          [suite_02:252]

Two whole-block passes per butterfly, seed and scale, and every tier since has
inherited the 2 without re-deriving it.  The seed pass is irreducible: it is the
per-frame sign mask ``diag(phase_s)``, a different sign at every one of the
32,256 x 256 positions, and no scalar can stand in for it.  The scale pass is
not: it is ONE number, the same number at every position, the same number for
every frame, the same number for every net in the suite.

The odd channel is
                                                            (frame s)
    o_s  =  z_s M ,        z_s = (MEAN_CHI_256 / 16) H diag(phase_s) ,

with M = W1 W2 the 256 x 256 precompute the route builds itself.  Writing
c = MEAN_CHI_256 / 16 and using only that a scalar commutes with a linear map,

    o_s = c (H diag(phase_s) M) = H diag(phase_s) (c M) .                   (1)

The left-hand side is the incumbent's route: run the butterfly on M, then scale
E = 8,257,536 elements.  The right-hand side is this tier's: scale M's 65,536
elements once, then run the butterfly.  Same operations, same count of adds and
subtracts, same sign mask, one whole-block pass fewer.

WHY THE LICENCE IS THE LINEAGE'S OWN, NOT A NEW ONE
===================================================
P2: a structure-exploitation licence established at one boundary extends to the
adjacent tree.  This licence was established by tier 2 itself, twice, in the
tier that introduced the butterfly:

  * "the 1/2 on the odd channel is absorbed into the butterfly's existing final
     scale (MEAN_CHI_256/16 becomes MEAN_CHI_256/32, a power-of-two change of
     one constant, costing no op and introducing no rounding)"   [suite_02:181-183]
  * "the 1/2 on the even channel is one exact binary halving of W2, charged at
     65,536"                                                     [suite_02:183-184]

Tier 2 moved a scalar onto a 256 x 256 weight-side object and paid WIDTH x WIDTH
= 65,536 for it, rather than paying it on the row block.  That is exactly the
move made here, applied to the one scalar tier 2 did not move because it was
already sitting in the pass it was folding INTO.  This tier charges the same
65,536, in the same place, on the same side.

The deployed layer-1 hook is NOT disturbed.  Its 14 is a certified receipt
[CODEX_HANDOFF_20260810.md:370, second-signalled at
M184_G0_NOTES.md:80-83] for that hook, on that operand, at that call site, and
this bill does not price layer 1 as a butterfly at all -- tier 1's butterfly
credit at layer 1 was REJECTED and stays rejected, asserted below.  What tier 2
built is a SECOND butterfly, on a different operand (M, not W1), at a call site
the deployed route does not contain, and the candidate that runs it chooses
where its own constants sit.  Tier 2 exercised that choice; this tier exercises
it once more, on the constant tier 2 left where the transcription put it.

EXACTNESS IDENTITY
==================
Two claims, both executed below rather than asserted.

(I) The ROUTE.  Write z for the design's base half (32,256 rows), whose frame-s
block is c H diag(phase_s) -- 126 phased-Hadamard frames x 256 rows
[CODEX_HANDOFF_20260810.md:40; kerdock_v3_estimator class body, n_base =
126 * 256, phase_start = 2, phase_stop = 128] -- and the net is bias-free (no
product in ``predict`` carries an additive term).  The antipodally doubled
design [z; -z] has layer-1 preactivations [p; -p], p = z W1, and the layer-2
preactivation in the design's row order is

    pre2 = [ relu(p) W2 ; relu(-p) W2 ] .

This route produces, in the same row order,

    pre2_top    = relu(p) W2                          (the same product)
    pre2_bottom = pre2_top - o ,  o = p W2 = z (W1 W2)

with pre2_bottom = relu(p)W2 - pW2 = (relu(p) - p)W2 = relu(-p)W2 by the
odd-channel identity relu(x) - relu(-x) = x and the linearity of the matrix
product.  Unchanged from tier 8, re-executed here rather than cited.

(II) The NORMALIZATION.  Identity (1) above, which is this tier's actual claim:

    c (H diag(phase_s) M)  =  H diag(phase_s) (c M)     for every frame s.    (1)

``_selfcheck`` executes (1) over the INTEGERS on four instances, with H built the
deployed way (the butterfly run on the identity), phases drawn as +/-1, an
integer c, and M dense -- entry for entry, both frame-wise and on the assembled
32,256-row analogue -- and then runs the whole layer-2 route with the rescaled
odd channel against a reference that materializes [z; -z], multiplies by W1,
ReLUs, and multiplies by W2.

The ACCOUNTING identity this tier adds is separately executable:

    ops(butterfly with the scale folded)  +  (elements of M)
        =  ops(butterfly with a trailing scale)  -  (elements of the output)
                                                     + (elements of M)        (2)

``_selfcheck`` MEASURES both op counts off running butterflies at four sizes --
it does not evaluate the formula -- and asserts (2) with equality at each, then
asserts the closed form 1 + 1.5 log2(rows) per element reproduces the measured
count at rows = 256, where it is 13 and the incumbent's is 14.

f32 STATUS: REASSOCIATION CLASS, TIER 2's OWN, DECLARED NOT BURIED
==================================================================
Over the reals and over the integers the two routes are identical and
``_selfcheck`` checks that literally.  Over f32 the scalar sits one place
earlier, which is a reassociation of the same real arithmetic and is strictly
the WEAKER member of the class this ladder already lives in: tier 2 declared
itself a "REROUTE CLASS, NOT APPROXIMATION" [suite_02:186-196] for a move that
uses matrix-product associativity, u(W1 W2) in place of (u W1)W2, and the entire
call price every tier quotes is a depth-6 Winograd route, which is a
reassociation of a dense product. This tier reassociates one scalar multiply.

Three facts about that scalar, all executed below:

  * ``c * phase`` is EXACT for phase in {+1, -1}, so no rounding is introduced
    at the seed mask under either placement.
  * With c a power of two the two routes are bit-identical on every input,
    including both signed zeros -- executed, not argued.
  * With the deployed c = MEAN_CHI_256/16 the routes differ only by rounding
    placement; the measured relative gap on the executed instances is bounded
    below 1e-6 and reported, not hidden.  The incumbent's placement performs
    MORE roundings (one per output element, 8,257,536 of them) than this tier's
    (one per element of M, 65,536), so the move does not degrade conditioning:
    it removes roundings rather than adding them.

No value is approximated, no rank is reduced, no summation inside any call is
reordered, no term is dropped that any operation reads.  Every op counted here
is one f32 multiply, add, subtract, negate or copy priced at 1, the unit the
incumbent's call bill uses.  No f32 repricing, no compliance flag.

DISJOINTNESS, SO NOTHING IS DEDUCTED TWICE
==========================================
  * From tier 2.  The row count (32,256), the precompute (33,488,896) and the
    butterfly's SEED pass and STAGES are carried at tier 2's own values and
    asserted.  The abs pass was renamed by tier 8 and waived by tier 9; the
    half-scale was retired by tier 8; the recombination was halved by tier 8.
    None of those is touched.  Only the butterfly's final whole-block pass moves,
    and it moves to the very place -- a WIDTH x WIDTH weight-side scale, charged
    at 65,536 -- that tier 2 itself used for the other constant it folded.
  * From tier 3.  The W-side stack lane is untouched: 32 stacks per net, one per
    layer, at 1,915,152 each.  Asserted.
  * From tier 4.  Layer 1's 32,256 base rows and its leaves and decode lanes are
    untouched.  Asserted to the FLOP.
  * From tier 5.  The suite-once design-side operand lane is unchanged at
    241,309,152 and is still published as a named one-time field.  This tier adds
    NOTHING to it, though the cheaper placement of c is available there (see the
    conservative choices).  Asserted.
  * From tier 7.  The layer-1 antipodal negation stays at 65,536 for its 256
    pilot rows.  It is a different 65,536 from this tier's, at a different layer,
    on a different object, and both are asserted separately.
  * From tier 8.  The direct-top / subtracted-antipode structure is carried
    entire and its antipodal write is charged in full at all 32,256 base rows.
  * From tier 9.  The relu pass stays waived at zero and the ledger's
    478,937,088 free ReLU element-writes are re-counted below, unclaimed.
  * From tier 1 and tier 6, both REJECTED.  No butterfly credit is taken at
    layer 1 -- its row part is still more than eighteen times the butterfly the
    deployed hook runs, asserted -- and the odd-channel precompute is still
    charged at ``direct_cost(256, 256, 256) = 33,488,896``, asserted strictly
    above the tier-7 call price it is not repriced to.  Neither rejected claim is
    revived and nothing here depends on either.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * The normalization is charged at 65,536 PER NET, folded into the per-net
    precompute M.  The strictly cheaper placement exists and is declined: the
    phase signs are loaded once at setup from the frozen asset and are shared by
    every net of the suite, so ``c * phases`` (126 x 256 = 32,256 ops, exact
    because the phases are +/-1) is a SUITE-ONCE cost and would make this tier's
    per-net charge ZERO rather than 65,536.  Refusing that further 65,536 per net
    keeps tier 5's one-time lane untouched and keeps this tier's claim inside a
    single per-net term.
  * The butterfly's SEED pass is charged in full, at 1 op per element over all
    8,257,536, although its first radix-2 stage reads exactly what it writes and
    a fused signed first stage would cost 0.5/element less.  That is elementwise
    redistribution inside a pass and it is not taken.
  * The precompute is charged at the source's own direct price, not the tier-7
    route it would be entitled to (tier 6's rejected claim).
  * The antipodal write is charged over all 32,256 base rows, unconditionally.
  * The even channel keeps tier 2's exact-tiling price (7 full 4,096-row calls
    plus one 3,584-row call, 2,371,803,840 of row part).
  * Layers 3..32 keep the antipodal half at full price.  The licence is tier 2's,
    no wider: it applies at the first nonlinearity of a bias-free net on an
    antipodally doubled design, and nowhere deeper.  ``_selfcheck`` re-measures
    that boundary rather than asserting it.
  * ``.total`` remains the marginal per-net bill with tier 5's one-time charge
    published beside it; ``suite_total(1)`` is still exactly tier 4's figure minus
    the crowned savings, so no suite size is assumed anywhere.

DOORS THAT STAY CLOSED
======================
Re-executed here so the next tier does not pay for them twice:

  * Pruning.  ``active`` is a function of the net's own weights and its worst case
    is the full 256, so no net-independent bill below 256 exists
    [fold3_estimator.py:122-151].
  * The terminal fold.  Layers 30..32 are ``x30_kink``, ``pre31`` and ``pre32``,
    products of one, two and three row-terms, whose full-row work is
    ``a*b + (a+b)*c + (a+b+c)*d``, maximised at 393,216 against the incumbent's
    3 * 256 * 256 = 196,608.  Modelling it honestly RAISES the bill by up to a
    factor of two; the incumbent's silence is the cheaper accounting.  Both
    bounds are executed below.
  * The ledger-free ReLU writes.  478,937,088 of them, priced at zero by the
    incumbent at all 32 layers; re-billing them consistently would RAISE the bill
    by that amount.  Counted below, not claimed.

NO APPROXIMATION, NO FLAG
=========================
The certified per-call floor (303,096,592 at anonymous (4096, 256, 256)) is
untouched: no op inside any call is rescheduled or reweighted, the depth-6
selection is the tier-7 sweep's own at every shape used, and the per-call price
is used verbatim at 4,096 and 3,584 rows exactly as tiers 2..9 use it.  The term
that moves is not inside any call.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A metered win is repaid in wall time when it forces small kernels, extra passes,
new dispatch, or new residency.  This one forces none of those, and unlike tier
9 its slope is strictly favourable rather than merely neutral, because a real
pass disappears:

  * ONE FEWER FULL-BLOCK PASS, NOT ONE FEWER COUNTER.  The removed op is a whole
    streaming pass over the (126, 256, 256) f32 frame block -- 33.0 MB read and
    33.0 MB written, memory-bound end to end -- replaced by a 256 x 256 scale of
    262 kB that lands in cache beside the precompute that just produced it.  The
    metered saving is backed by removed traffic, so the wall-time slope moves the
    same way the bill does.
  * KERNEL COUNT GOES DOWN BY ONE PER NET, NOT UP.  The odd channel dispatches
    ``multiply(phases, M', out=frames)``, eight stages, and stops; the trailing
    ``multiply(output, c, out=output)`` is gone and the added scale rides the
    precompute's own epilogue (``M' = c * (W1 W2)`` is one 256 x 256 elementwise
    pass on a buffer already hot).  This tier adds zero seams and removes one.
  * NO NEW RESIDENCY.  The route holds what tier 8's held: ``o`` beside the
    caller-owned activation.  M' overwrites M in place; no allocation appears.
  * NO NEW FUSION OBLIGATION.  Nothing here depends on a compiler fusing
    anything, on a kernel being written, or on a shape being retiled.  The
    change is where one Python scalar multiplies, which is an edit to one line.
  * FLAT IN THE SUITE SIZE.  One net or a thousand, each pays 8,192,000 less,
    so nothing about the win degrades as the suite grows, and the removed traffic
    scales with it.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import inspect
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
PILOT_BASE = 256                  # base_estimator.py:53; restated at
                                  # kerdock_v3_estimator.py:52 (candidate_source)

# The deployed sample loop is ``for layer in range(1, mlp.depth - 3)``, so it
# runs depth - 4 times and writes one full-width ReLU per iteration; the layer-1
# hook writes two, one per half.
LOOP_RELU_PASSES = LAYERS - 4
LAYER1_RELU_PASSES = 2

# FlopScope v0.10 butterfly convention, split into its parts so the part that
# moves is nameable.  CODEX_HANDOFF_20260810.md:360-370 transcribes the deployed
# hook op by op: one seed multiply over the whole frame block, log2(rows)
# radix-2 stages at three half-block passes each, one final whole-block scale.
_BUTTERFLY_SEED = 1
_BUTTERFLY_FINAL_SCALE = 1
_BUTTERFLY_PER_STAGE_HALVES = 3
_BUTTERFLY_PER_ELEMENT = 14              # incumbent's, kept for the delta gate
_BUTTERFLY_PER_ELEMENT_FOLDED = 13       # this tier's: the scale is weight-side


def _t7():
    spec = importlib.util.spec_from_file_location("t10base", _T7_PATH)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def direct_cost(m: int, k: int, n: int) -> int:
    """The source's own counterfactual price, cost_model.py:8-11."""
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


def _log2_exact(n: int) -> int:
    if n < 1 or n & (n - 1):
        raise ValueError(f"{n} is not a power of two")
    return n.bit_length() - 1


def butterfly_per_element(rows_per_frame: int = WIDTH,
                          *, final_scale: bool) -> int:
    """Re-derive the per-element butterfly price from the convention's parts.

    ``final_scale`` selects whether the closing whole-block pass is part of the
    price.  It is for a butterfly whose normalization sits on its OUTPUT (the
    deployed layer-1 hook, and tier 2's transcription of it); it is not for a
    butterfly whose normalization has been folded into the 256 x 256 matrix the
    butterfly multiplies, which is this tier's odd channel.
    """
    stages = _log2_exact(rows_per_frame)
    whole_block = _BUTTERFLY_SEED + (_BUTTERFLY_FINAL_SCALE if final_scale else 0)
    doubled = 2 * whole_block + stages * _BUTTERFLY_PER_STAGE_HALVES
    if doubled % 2:
        raise ValueError("half-block passes did not pair up to an integer price")
    return doubled // 2


def butterfly_ops(frames: int, rows: int, out_width: int,
                  *, final_scale: bool) -> int:
    """Ops a phased-WHT butterfly over ``frames`` frames costs.

    Tier 2's own shape [suite_02:277-289]: whole-block passes at 1/element, plus
    three half-block passes per radix-2 stage.  Kept in half-block units so the
    count stays integral at any stage count, not only the even ones for which a
    per-element price exists.
    """
    if min(frames, rows, out_width) <= 0:
        raise ValueError("butterfly dimensions must be positive")
    elements = rows * out_width
    if elements % 2:
        raise ValueError("half-block passes need an even element count")
    stages = _log2_exact(rows)
    whole = _BUTTERFLY_SEED + (_BUTTERFLY_FINAL_SCALE if final_scale else 0)
    return frames * (whole * elements
                     + stages * _BUTTERFLY_PER_STAGE_HALVES * (elements // 2))


def odd_channel_normalization_cost(k: int = WIDTH, n: int = WIDTH) -> int:
    """This tier's term: the design's radius scalar, applied weight-side.

    ``c = MEAN_CHI_256 / 16`` multiplies the 256 x 256 precompute M = W1 W2 once
    per net, at one op per element of M, instead of multiplying the odd channel's
    32,256 x 256 output block.  Exactly the placement -- and exactly the price --
    tier 2 used for the other constant it folded [suite_02:183-184].
    """
    if min(k, n) <= 0:
        raise ValueError("the precompute has positive dimensions")
    return k * n


def _selected_levels(strategy: str) -> int:
    """Depth the tier-7 sweep chose, read off its own strategy string."""
    head, _, _rest = strategy.partition("_inplaceleaf")
    tag = head.rsplit("_", 1)[-1]
    if not tag.startswith("l") or not tag[1:].isdigit():
        raise ValueError(f"cannot read a Winograd depth from {strategy!r}")
    return int(tag[1:])


def weight_side_stack_cost(t7, k: int = WIDTH, n: int = WIDTH,
                           m: int = TILE_ROWS) -> int:
    """The m-independent lane of the crowned call bill: the W-side (k, n) stack."""
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, n)
    levels = _selected_levels(bill.strategy)
    cost, _grade = t7.best_operand_grade(k, n, levels)
    return cost


def design_side_stack_cost(t7, m: int, k: int = WIDTH) -> int:
    """The A-side (m, k) operand lane: a pure function of the LEFT operand.

    Tier 5's object, carried verbatim: at layer 1 the left operand is the design,
    invariant across the nets of the suite, so this is charged once to the suite
    rather than once per net.
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


@dataclass(frozen=True)
class SuiteBill:
    strategy: str
    call_total: int
    weight_stack: int
    row_part_full: int
    row_part_tail: int
    layers: int
    layer1_row_part_per_net: int
    layer1_design_stack_once: int
    layer1_negation: int
    layer1_negation_rows: int
    layer1_total: int
    generic_layer: int
    generic_layers_total: int
    layer2_even_rows: int
    layer2_relu_pass: int
    layer2_relu_writes_priced_zero: int
    layer2_precompute: int
    layer2_odd_normalization: int
    layer2_odd_butterfly_per_element: int
    layer2_odd_butterfly: int
    layer2_antipodal_write: int
    layer2_rows_removed_from_bill: int
    layer2_aux: int
    layer2_total: int
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
            "weight_side_stack_per_layer": self.weight_stack,
            "row_part_per_full_tile": self.row_part_full,
            "layer1_leaves_plus_decode_32256": self.layer1_row_part_per_net,
            "layer1_weight_side_stack": self.weight_stack,
            "layer1_antipodal_negation_read_rows": self.layer1_negation_rows,
            "layer1_antipodal_negation": self.layer1_negation,
            "layer1_total_per_net": self.layer1_total,
            "generic_layer_total": self.generic_layer,
            "generic_layers_3_to_32": self.generic_layers_total,
            "layer2_top_channel_row_part_32256": self.layer2_even_rows,
            "layer2_weight_side_stack": self.weight_stack,
            "layer2_relu_pass_CHARGED": self.layer2_relu_pass,
            "layer2_relu_write_PRICED_ZERO_by_the_ledger":
                self.layer2_relu_writes_priced_zero,
            "layer2_precompute_W1W2": self.layer2_precompute,
            "layer2_odd_normalization_WEIGHT_SIDE":
                self.layer2_odd_normalization,
            "layer2_odd_butterfly_ops_per_element":
                self.layer2_odd_butterfly_per_element,
            "layer2_odd_channel_butterfly": self.layer2_odd_butterfly,
            "layer2_antipodal_write_32256": self.layer2_antipodal_write,
            "layer2_rows_removed_from_the_bill":
                self.layer2_rows_removed_from_bill,
            "layer2_auxiliary_terms": self.layer2_aux,
            "layer2_total": self.layer2_total,
            "design_side_stack_charged_ONCE_to_the_suite":
                self.layer1_design_stack_once,
            "total": self.total,
        }


def _layer2_auxiliary_terms() -> tuple:
    """This tier's layer-2 non-matmul terms.

    The precompute and the antipodal write are tier 2's and tier 8's, unchanged.
    The relu pass is waived at tier 9's zero.  The butterfly loses its trailing
    whole-block scale, and the scalar it carried is charged once on the 256 x 256
    precompute instead.
    """
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)                    # 33,488,896
    normalization = odd_channel_normalization_cost(WIDTH, WIDTH)     #     65,536
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False)
    antipodal_write = BASE_ROWS * WIDTH                              #  8,257,536
    return precompute, normalization, butterfly, antipodal_write


def _incumbent_layer2_auxiliary_cost() -> int:
    """Tier 9's three terms as the incumbent bills them, for the delta gate."""
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)                    # 33,488,896
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=True)
    antipodal_write = BASE_ROWS * WIDTH                              #  8,257,536
    return precompute + butterfly + antipodal_write


def _tier8_layer2_auxiliary_cost() -> int:
    """Tier 8's four terms, for the disjointness gate against tiers 8 and 9."""
    return _incumbent_layer2_auxiliary_cost() + BASE_ROWS * WIDTH    # + relu pass


def _tier2_layer2_auxiliary_cost() -> int:
    """Tier 2's five terms, for the disjointness gate against tier 2."""
    abs_pass = BASE_ROWS * WIDTH                                     #  8,257,536
    halfscale = WIDTH * WIDTH                                        #     65,536
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)                    # 33,488,896
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=True)
    recombine = DESIGN_ROWS * WIDTH                                  # 16,515,072
    return abs_pass + halfscale + precompute + butterfly + recombine


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill: the odd channel's butterfly carries the design
    normalization on the 256 x 256 matrix it multiplies, not on the 8,257,536
    output elements it produces, so its whole-block passes drop from two to one."""
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

    # --- generic layers 3..32: tier 3's layer, carried verbatim ---------------
    generic_rows = int(row_full * DESIGN_ROWS // m)
    if generic_rows * m != row_full * DESIGN_ROWS:
        raise ValueError("tile count is not exact; refusing a rounded bill")
    generic_layer = generic_rows + w_stack
    generic_total = (LAYERS - 2) * generic_layer

    # --- layer 1: tiers 4, 5 and 7, carried verbatim --------------------------
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
    if PILOT_BASE > BASE_ROWS:
        raise ValueError("the pilot cannot read more rows than the half has")
    negation = antipodal_negation_cost(PILOT_BASE, WIDTH)
    layer1_rows_per_net = base_rows_part - design_stack
    layer1 = layer1_rows_per_net + w_stack + negation

    # --- layer 2: tier 8's route, tier 9's elementwise rule, THIS TIER's
    #     placement of the design normalization --------------------------------
    layer2_even_rows = base_rows_part
    precompute, normalization, butterfly, antipodal_write = _layer2_auxiliary_terms()
    per_element = butterfly_per_element(WIDTH, final_scale=False)
    if per_element != _BUTTERFLY_PER_ELEMENT_FOLDED:
        raise ValueError("the folded butterfly price is not the convention's own")
    if butterfly != per_element * BASE_ROWS * WIDTH:
        raise ValueError("butterfly price does not match its own convention")
    if normalization >= BASE_ROWS * WIDTH:
        raise ValueError("a weight-side scale cannot cost a row-block pass")
    rows_removed = DESIGN_ROWS - BASE_ROWS
    if antipodal_write != rows_removed * WIDTH:
        raise ValueError("the substitute is not one write per removed element")
    relu_charged = 0
    relu_free = BASE_ROWS * WIDTH
    layer2_aux = (relu_charged + precompute + normalization
                  + butterfly + antipodal_write)
    layer2 = layer2_even_rows + w_stack + layer2_aux

    return SuiteBill(
        "odd_channel_normalization_is_weight_side",
        call,
        w_stack,
        row_full,
        row_tail,
        LAYERS,
        layer1_rows_per_net,
        design_stack,
        negation,
        PILOT_BASE,
        layer1,
        generic_layer,
        generic_total,
        layer2_even_rows,
        relu_charged,
        relu_free,
        precompute,
        normalization,
        per_element,
        butterfly,
        antipodal_write,
        rows_removed,
        layer2_aux,
        layer2,
        design_stack,
        generic_total + layer1 + layer2,
    )


# ---------------------------------------------------------------------------
# Executable exactness.  Three claims are executed, not asserted:
#   (a) the SCALAR identity c (H diag(phase) M) = H diag(phase) (c M), over the
#       integers, frame-wise and on the assembled design;
#   (b) the ROUTE is tier 8's and produces pre2 exactly, with the odd channel
#       supplied by the rescaled butterfly;
#   (c) the ACCOUNTING identity: the measured op count of the folded butterfly
#       plus the elements of M equals the measured op count of the trailing-scale
#       butterfly minus the elements of the output, plus the elements of M.
# ---------------------------------------------------------------------------


def _rng(seed: int):
    state = seed

    def nxt(lo: int, hi: int) -> int:
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return lo + state % (hi - lo + 1)

    return nxt


def _mm(A, B):
    inner = len(B)
    return [[sum(A[i][t] * B[t][j] for t in range(inner))
             for j in range(len(B[0]))] for i in range(len(A))]


def _relu(M):
    return [[v if v > 0 else 0 for v in row] for row in M]


def _neg(M):
    return [[-v for v in row] for row in M]


def _sub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def _scale(M, c):
    return [[c * v for v in row] for row in M]


def butterfly_frame(phase, mat, scale, counter):
    """One phased-WHT frame, transcribed from the deployed hook, instrumented.

    ``phase`` is the frame's +/-1 sign vector, ``mat`` the matrix the butterfly
    multiplies, ``scale`` the trailing whole-block scalar (pass 1 to omit the
    pass entirely -- that is exactly what this tier does).  ``counter`` collects
    element-writes so the op count is MEASURED, never evaluated from a formula.
    CODEX_HANDOFF_20260810.md:360-368.
    """
    rows, width = len(mat), len(mat[0])
    frame = [[phase[i] * mat[i][j] for j in range(width)] for i in range(rows)]
    counter[0] += rows * width                                     # seed mask
    half = 1
    while half < rows:
        for base in range(0, rows, half * 2):
            for i in range(base, base + half):
                left, right = frame[i], frame[i + half]
                scratch = list(left)
                counter[0] += width                                # copyto
                frame[i] = [scratch[j] + right[j] for j in range(width)]
                counter[0] += width                                # add
                frame[i + half] = [scratch[j] - right[j] for j in range(width)]
                counter[0] += width                                # subtract
        half *= 2
    if scale != 1:
        frame = _scale(frame, scale)
        counter[0] += rows * width                                 # final scale
    return frame


def hadamard_by_butterfly(n: int):
    """H exactly as the deployed setup builds it: the butterfly run on I."""
    eye = [[int(i == j) for j in range(n)] for i in range(n)]
    return butterfly_frame([1] * n, eye, 1, [0])


def design_rows(phases, hadamard, c):
    """The design's base half: frame s contributes ``c H diag(phase_s)``."""
    rows = []
    for phase in phases:
        for h_row in hadamard:
            rows.append([c * h_row[i] * phase[i] for i in range(len(phase))])
    return rows


def odd_channel_trailing_scale(phases, mat, c, counter):
    """The incumbent's odd channel: butterfly on M, then scale the output."""
    out = []
    for phase in phases:
        out.extend(butterfly_frame(phase, mat, c, counter))
    return out


def odd_channel_folded_scale(phases, mat, c, counter):
    """This tier's odd channel: scale M once, then butterfly, no trailing pass."""
    scaled = _scale(mat, c)
    counter[0] += len(mat) * len(mat[0])                # the weight-side scale
    out = []
    for phase in phases:
        out.extend(butterfly_frame(phase, scaled, 1, counter))
    return out


def deployed_layer1_hook(design, w1, trace):
    """The deployed hook, transcribed: negate, ReLU the antipode, ReLU the base."""
    p = _mm(design, w1)
    block = len(p) * len(p[0])
    trace.append(("negate", "layer1", block))          # fold3_estimator.py:95
    trace.append(("relu", "layer1", block))            # :96
    trace.append(("relu", "layer1", block))            # :97
    return p, _relu(p), _relu(_neg(p))


def terminal_fold_row_units(a: int, b: int, c: int, d: int) -> int:
    """Row-proportional work of layers 30..32 in units of one (rows x 1 x 1)."""
    return a * b + (a + b) * c + (a + b + c) * d


def _selfcheck() -> None:
    t7 = _t7()
    call_of = t7.inplace_verbatim_leaves_candidate_bill

    # ---- 1. Shape anchors, from the deployed source's own constants. --------
    assert BASE_ROWS == 32256, BASE_ROWS
    assert DESIGN_ROWS == 64512, DESIGN_ROWS
    assert DESIGN_ROWS == 15.75 * TILE_ROWS
    assert BASE_ROWS == 7 * TILE_ROWS + 3584
    assert PILOT_BASE == 256 and PILOT_BASE < BASE_ROWS
    assert LOOP_RELU_PASSES == 28 and LAYER1_RELU_PASSES == 2

    # ---- 2. The call bill is affine in m; the constant is the W-side lane. ---
    probes = (512, 1024, 2048, 3072, 3584, 4096)
    bills = {rows: call_of(rows, WIDTH, WIDTH) for rows in probes}
    lo, hi = probes[0], probes[-1]
    slope_num, slope_den = bills[hi].total - bills[lo].total, hi - lo
    constant_num = bills[hi].total * slope_den - slope_num * hi
    assert constant_num % slope_den == 0, "affine fit is not integral"
    constant = constant_num // slope_den
    for rows in probes:
        assert slope_num * rows + constant * slope_den == bills[rows].total * slope_den, (
            f"call bill is not affine in m at m={rows}")
    assert constant == 1915152, constant

    params = tuple(inspect.signature(t7.best_operand_grade).parameters)
    assert params == ("a_dim", "b_dim", "levels"), params
    levels = _selected_levels(bills[TILE_ROWS].strategy)
    assert levels == 6, bills[TILE_ROWS].strategy
    w_stack, _g = t7.best_operand_grade(WIDTH, WIDTH, levels)
    assert w_stack == constant, (w_stack, constant)

    # The depth-6 selection is the tier-7 sweep's own at every shape used here.
    for rows in (TILE_ROWS, 3584, BASE_ROWS, DESIGN_ROWS):
        assert _selected_levels(call_of(rows, WIDTH, WIDTH).strategy) == 6, rows

    row_full = bills[TILE_ROWS].total - w_stack
    row_tail = bills[3584].total - w_stack
    assert row_tail * TILE_ROWS == row_full * 3584, "row lane is not proportional"

    # ---- 3. Tier 5's lane decomposition, re-derived, still closing exactly. --
    leaves = 7 ** levels * t7.direct_cost(
        BASE_ROWS >> levels, WIDTH >> levels, WIDTH >> levels)
    a_lane, _g = t7.best_operand_grade(BASE_ROWS, WIDTH, levels)
    decode, _g = t7.best_decode_grade(BASE_ROWS, WIDTH, levels)
    tier4_row_part = 7 * row_full + row_tail
    assert leaves + a_lane + decode + w_stack == call_of(
        BASE_ROWS, WIDTH, WIDTH).total, "lane decomposition does not close"
    assert leaves + a_lane + decode == tier4_row_part, (
        leaves + a_lane + decode, tier4_row_part)
    assert (leaves, a_lane, decode) == (1660262688, 241309152, 470232000), (
        leaves, a_lane, decode)

    # ---- 4. THE SCALAR IDENTITY, EXECUTED OVER THE INTEGERS. ----------------
    # c (H diag(phase) M) = H diag(phase) (c M), frame-wise and assembled, with
    # H built the deployed way and c an integer so the equality is exact.
    for n_rows, n_frames, width, c in ((4, 3, 5, 3), (8, 2, 4, 7),
                                       (4, 5, 3, 2), (8, 3, 6, 5)):
        nxt = _rng(101010 + n_rows * 131 + n_frames * 17 + width * 3 + c)
        hadamard = hadamard_by_butterfly(n_rows)
        phases = [[1 if nxt(0, 1) else -1 for _ in range(n_rows)]
                  for _ in range(n_frames)]
        mat = [[nxt(-9, 9) for _ in range(width)] for _ in range(n_rows)]

        counter_a, counter_b = [0], [0]
        trailing = odd_channel_trailing_scale(phases, mat, c, counter_a)
        folded = odd_channel_folded_scale(phases, mat, c, counter_b)
        assert trailing == folded, "the scalar does not commute with the route"

        # ... and both equal the definitional product z M, with z the design.
        z = design_rows(phases, hadamard, c)
        assert len(z) == n_frames * n_rows
        assert _mm(z, mat) == trailing, "the butterfly is not the design product"

        # ---- THE ACCOUNTING IDENTITY, MEASURED off the running routes. -----
        elements_out = n_frames * n_rows * width
        elements_m = n_rows * width
        assert counter_a[0] - counter_b[0] == elements_out - elements_m, (
            counter_a[0], counter_b[0], elements_out, elements_m)
        # The measured counts reproduce the convention's closed form exactly.
        assert counter_a[0] == butterfly_ops(
            n_frames, n_rows, width, final_scale=True), counter_a[0]
        assert counter_b[0] == butterfly_ops(
            n_frames, n_rows, width, final_scale=False) + elements_m, counter_b[0]
        # The seed mask is NOT waived: it survives in both counts at 1/element.
        assert counter_b[0] > elements_out, "the seed mask was waived"

    # The closed form at the production shape: 14 with the trailing pass, 13
    # without, and the difference is exactly one whole-block pass.
    assert butterfly_per_element(WIDTH, final_scale=True) == 14
    assert butterfly_per_element(WIDTH, final_scale=False) == 13
    assert butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=True) == 115605504
    assert butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False) == 107347968
    assert (butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=True)
            - butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False)
            == BASE_ROWS * WIDTH == 8257536)

    # ---- 5. THE ROUTE, executed, with the rescaled odd channel in place. ----
    for n_rows, n_frames, width, c in ((4, 2, 4, 3), (8, 2, 8, 2),
                                       (4, 3, 4, 5), (2, 4, 2, 7)):
        nxt = _rng(242424 + n_rows * 91 + n_frames * 13 + width + c)
        hadamard = hadamard_by_butterfly(n_rows)
        phases = [[1 if nxt(0, 1) else -1 for _ in range(n_rows)]
                  for _ in range(n_frames)]
        z = design_rows(phases, hadamard, c)
        w1 = [[nxt(-9, 9) for _ in range(width)] for _ in range(n_rows)]
        w2 = [[nxt(-9, 9) for _ in range(width)] for _ in range(width)]

        # Reference: materialize [z; -z], multiply, ReLU, multiply.
        full_design = z + _neg(z)
        ref_x = _relu(_mm(full_design, w1))
        ref_pre2 = _mm(ref_x, w2)

        # This tier's route: tier 8's structure, odd channel from the FOLDED
        # butterfly run on the precompute M = W1 W2.
        trace = []
        p, x_top, _x_bottom = deployed_layer1_hook(z, w1, trace)
        top = _mm(x_top, w2)                              # t = relu(p) W2
        precompute = _mm(w1, w2)                          # M = W1 W2
        odd = odd_channel_folded_scale(phases, precompute, c, [0])
        bottom = _sub(top, odd)
        trace.append(("subtract", "layer2", len(bottom) * len(bottom[0])))
        new_pre2 = top + bottom

        assert new_pre2 == ref_pre2, "this tier's route changed pre2"
        assert new_pre2[:len(z)] == _mm(_relu(_mm(z, w1)), w2)
        # The odd channel the folded butterfly produced IS z(W1 W2) = (z W1)W2.
        assert odd == _mm(z, precompute) == _mm(p, w2)
        # relu(-x) = relu(x) - x on the whole base block, which the write rides.
        assert _relu(_neg(p)) == _sub(_relu(p), p)
        # The route runs exactly four elementwise passes: the deployed hook's
        # three plus tier 8's subtract.  The odd channel added none.
        assert [(kind, layer) for kind, layer, _n in trace] == [
            ("negate", "layer1"), ("relu", "layer1"), ("relu", "layer1"),
            ("subtract", "layer2"),
        ], trace
        # The layer-2 boundary, MEASURED not asserted: the layer-2 pair is not
        # antipodal, so the licence taken here does not recurse to layer 3.
        assert any(a != -b for ra, rb in zip(ref_pre2[:len(z)], ref_pre2[len(z):])
                   for a, b in zip(ra, rb)), (
            "this instance is degenerate; the boundary is not exhibited")

    # ---- 6. f32: the reassociation class, stated by execution. --------------
    #     (i) c * phase is EXACT for phase in {+1, -1}: no rounding is added at
    #         the seed mask under either placement.
    nxt = _rng(313131)
    c_deployed = 15.98438266660852747 / 16.0
    for _trial in range(200):
        raw = nxt(-10 ** 6, 10 ** 6) / 7.0
        for sign in (1.0, -1.0):
            assert sign * raw == (raw if sign > 0 else -raw)
            assert (sign * c_deployed) * raw == sign * (c_deployed * raw)
    #     (ii) with c a power of two the two placements are BIT-IDENTICAL.
    for c_pow2 in (0.5, 2.0, 0.25, 8.0):
        for _trial in range(200):
            a = nxt(-10 ** 6, 10 ** 6) / 3.0
            b = nxt(-10 ** 6, 10 ** 6) / 3.0
            assert c_pow2 * (a + b) == (c_pow2 * a) + (c_pow2 * b)
            assert c_pow2 * (a - b) == (c_pow2 * a) - (c_pow2 * b)
        for zero in (0.0, -0.0):
            assert c_pow2 * (zero + 0.0) == (c_pow2 * zero) + (c_pow2 * 0.0)
    #     (iii) with the deployed c the placements differ only by rounding, and
    #           the gap is bounded well below any tolerance a reroute carries.
    worst = 0.0
    for _trial in range(4000):
        a = nxt(-10 ** 6, 10 ** 6) / 3.0
        b = nxt(-10 ** 6, 10 ** 6) / 3.0
        trailing = c_deployed * (a + b)
        folded = (c_deployed * a) + (c_deployed * b)
        denom = abs(trailing) if trailing else 1.0
        worst = max(worst, abs(trailing - folded) / denom)
    assert worst < 1e-6, worst
    #     (iv) the incumbent's placement performs strictly MORE roundings.
    assert BASE_ROWS * WIDTH > WIDTH * WIDTH

    # ---- 7. Double-count gate: the crowned chain, recomputed from tier 7. ----
    call = bills[TILE_ROWS].total
    assert call == 303096592, call
    assert 504 * call == 152760682368                    # suite tier 0
    layer_slice = call * DESIGN_ROWS // TILE_ROWS
    tier2_even = 7 * call + bills[3584].total
    assert tier2_even == 2387125056, tier2_even
    assert _tier2_layer2_auxiliary_cost() == 173932544
    tier2 = 31 * layer_slice + tier2_even + _tier2_layer2_auxiliary_cost()
    assert tier2 == 150547968644, tier2                  # suite tier 2
    generic_layer_t3 = (row_full * DESIGN_ROWS) // TILE_ROWS + w_stack
    tier3_layer2 = (tier2_even - 8 * w_stack + w_stack
                    + _tier2_layer2_auxiliary_cost())
    tier3 = 31 * generic_layer_t3 + tier3_layer2
    assert generic_layer_t3 == 4745522832, generic_layer_t3
    assert tier3_layer2 == 2547651536, tier3_layer2
    assert tier3 == 149658859328, tier3                  # suite tier 3
    tier4_layer1 = tier4_row_part + w_stack + BASE_ROWS * WIDTH
    tier4 = 30 * generic_layer_t3 + tier4_layer1 + tier3_layer2
    assert tier4_layer1 == 2381976528, tier4_layer1
    assert tier4 == 147295313024, tier4                  # suite tier 4
    tier5_layer1 = tier4_layer1 - a_lane
    tier5 = 30 * generic_layer_t3 + tier5_layer1 + tier3_layer2
    assert tier5 == 147054003872, tier5                  # suite tier 5
    tier7_layer1 = tier5_layer1 - BASE_ROWS * WIDTH + PILOT_BASE * WIDTH
    tier7 = 30 * generic_layer_t3 + tier7_layer1 + tier3_layer2
    assert tier7_layer1 == 2132475376, tier7_layer1
    assert tier7 == 147045811872, tier7                  # suite tier 7
    tier8_layer2 = tier2_even - 8 * w_stack + w_stack + _tier8_layer2_auxiliary_cost()
    tier8 = 30 * generic_layer_t3 + tier7_layer1 + tier8_layer2
    assert _tier8_layer2_auxiliary_cost() == 165609472
    assert tier8_layer2 == 2539328464, tier8_layer2
    assert tier8 == 147037488800, tier8                  # suite tier 8
    tier9_layer2 = tier8_layer2 - BASE_ROWS * WIDTH
    tier9 = 30 * generic_layer_t3 + tier7_layer1 + tier9_layer2
    assert _incumbent_layer2_auxiliary_cost() == 157351936
    assert tier9_layer2 == 2531070928, tier9_layer2
    assert tier9 == 147029231264, tier9                  # suite tier 9, incumbent

    bill = suite_bill_per_net()
    assert bill.weight_stack == w_stack == 1915152

    # (a) Disjoint from tier 3: the W-STACK lane is untouched, 32 per net.
    stacks_here = LAYERS * bill.weight_stack
    assert bill.total - stacks_here == (
        30 * (bill.generic_layer - w_stack)
        + (bill.layer1_total - w_stack)
        + (bill.layer2_total - w_stack))

    # (b) Disjoint from tiers 4, 5 and 7: layer 1 is bit-identical.
    assert bill.layer1_row_part_per_net + bill.layer1_design_stack_once == tier4_row_part
    assert bill.layer1_row_part_per_net == leaves + decode == 2130494688
    assert bill.layer1_design_stack_once == a_lane == 241309152
    assert bill.suite_once == a_lane
    assert bill.layer1_negation == PILOT_BASE * WIDTH == 65536
    assert bill.layer1_negation_rows == PILOT_BASE
    assert bill.layer1_total == tier7_layer1 == 2132475376
    #     This tier's 65,536 is a DIFFERENT object from tier 7's, at a different
    #     layer, and both are charged.
    assert bill.layer2_odd_normalization == 65536
    assert bill.layer1_negation == 65536
    assert bill.layer1_negation + bill.layer2_odd_normalization == 131072

    # (c) Disjoint from tiers 2, 8 and 9: the ROW COUNT and every surviving aux
    #     term are carried at their own values; only the trailing scale moves.
    assert bill.layer2_even_rows == tier2_even - 8 * w_stack == 2371803840
    assert bill.layer2_precompute == direct_cost(WIDTH, WIDTH, WIDTH) == 33488896
    assert bill.layer2_antipodal_write == BASE_ROWS * WIDTH == 8257536
    assert bill.layer2_relu_pass == 0
    assert bill.layer2_odd_butterfly_per_element == 13
    assert bill.layer2_odd_butterfly == 107347968, bill.layer2_odd_butterfly
    assert bill.layer2_aux == 149159936, bill.layer2_aux
    assert _incumbent_layer2_auxiliary_cost() - bill.layer2_aux == 8192000
    assert (_incumbent_layer2_auxiliary_cost() - bill.layer2_aux
            == BASE_ROWS * WIDTH - WIDTH * WIDTH)
    #     Tier 8's and tier 9's own savings are already inside the incumbent
    #     figure this tier subtracts from; neither is re-claimed.
    assert _tier2_layer2_auxiliary_cost() - _tier8_layer2_auxiliary_cost() == 8323072
    assert _tier8_layer2_auxiliary_cost() - _incumbent_layer2_auxiliary_cost() == 8257536

    # (d) Disjoint from tier 1 (rejected): NO butterfly credit at layer 1.
    butterfly_layer1 = 14 * BASE_ROWS * WIDTH
    assert butterfly_layer1 == 115605504
    assert bill.layer1_row_part_per_net > 18 * butterfly_layer1, (
        "layer 1 is being credited a butterfly; that is tier 1's rejected claim")
    #     The deployed layer-1 hook's certified 14 is not disturbed: this tier's
    #     13 is the price of a DIFFERENT butterfly, on M, at layer 2.
    assert butterfly_per_element(WIDTH, final_scale=True) == 14

    # (e) Disjoint from tier 6 (rejected): the odd-channel precompute is still
    #     charged at the direct price, not repriced as a Winograd call.
    assert bill.layer2_precompute > call_of(WIDTH, WIDTH, WIDTH).total, (
        "the precompute is being repriced as a Winograd call; that is tier 6's "
        "rejected claim")

    # ---- 8. THE DELTA IS THE ONE RELOCATED CONSTANT, AND NOTHING ELSE. ------
    assert tier9_layer2 - bill.layer2_total == 8192000, (
        tier9_layer2 - bill.layer2_total)
    assert 8192000 == BASE_ROWS * WIDTH - WIDTH * WIDTH
    assert tier9 - bill.total == 8192000, tier9 - bill.total
    #     Layers 1 and 3..32 are bit-identical to the incumbent's.
    assert bill.generic_layer == generic_layer_t3
    assert bill.generic_layers_total == 30 * generic_layer_t3 == 142365684960
    assert bill.layer1_total == tier7_layer1

    # ---- 9. THE LEDGER'S ReLU CONVENTION, COUNTED AND NOT CLAIMED. ----------
    free_relu = deployed_relu_writes_priced_zero(WIDTH)
    assert free_relu == (2 * BASE_ROWS * WIDTH + 28 * DESIGN_ROWS * WIDTH)
    assert free_relu == 478937088, free_relu
    assert bill.layer2_relu_writes_priced_zero == BASE_ROWS * WIDTH
    assert free_relu > 57 * (BASE_ROWS * WIDTH)

    # ---- 10. Conservativeness gates. ----------------------------------------
    assert bill.layer2_rows_removed_from_bill == DESIGN_ROWS - BASE_ROWS == 32256
    assert bill.layer2_antipodal_write == bill.layer2_rows_removed_from_bill * WIDTH
    #     The suite-once placement of c is DECLINED: suite_once is tier 5's lane
    #     and nothing was added to it.
    assert bill.suite_once == a_lane
    assert bill.layer2_odd_normalization > 0
    assert FRAMES * WIDTH < bill.layer2_odd_normalization * 2   # 32,256 < 131,072
    #     Never worse than the incumbent at any suite size, strictly better at
    #     every size, and the one-time charge is still published exactly.
    for n_nets in (1, 2, 3, 10, 100, 1000):
        assert bill.suite_total(n_nets) == n_nets * bill.total + a_lane
        assert bill.suite_total(n_nets) < n_nets * tier9 + a_lane
        num, den = bill.amortized_numerator(n_nets)
        assert (num, den) == (n_nets * bill.total + a_lane, n_nets)
    assert bill.suite_total(1) == tier4 - 8192000 - 8323072 - 8257536 - 8192000

    # ---- 11. The doors tiers 7, 8 and 9 closed, re-executed. ----------------
    assert max(a for a in range(1, WIDTH + 1)) == WIDTH
    incumbent_terminal = 3 * WIDTH * WIDTH
    assert incumbent_terminal == 196608
    worst_fold = max(terminal_fold_row_units(a, b, c, d)
                     for a in (0, WIDTH) for b in (0, WIDTH)
                     for c in (0, WIDTH) for d in (0, WIDTH))
    assert worst_fold == terminal_fold_row_units(WIDTH, WIDTH, WIDTH, WIDTH)
    assert worst_fold == 393216 == 2 * incumbent_terminal, worst_fold

    # ---- 12. The bill's own arithmetic. -------------------------------------
    assert bill.layer2_total == 2522878928, bill.layer2_total
    assert bill.total < tier9 < tier8 < tier7 < tier5 < tier4 < tier3 < tier2
    assert bill.total == 147021039264, bill.total


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: affine measurement of the call bill, the tier-7 lane "
          "decomposition closing on tier 4's layer-1 row part, the scalar "
          "identity c(H diag(phase) M) = H diag(phase)(cM) executed over the "
          "integers frame-wise and against the assembled design product, the "
          "butterfly op counts MEASURED off both running routes and agreeing "
          "with the convention's closed form (14 with the trailing pass, 13 "
          "without), tier 8's whole layer-2 route re-run with the folded odd "
          "channel and agreeing with the direct reference entry for entry, the "
          "f32 statements (sign folding exact, power-of-two placement "
          "bit-identical including signed zeros, deployed-c gap under 1e-6, "
          "fewer roundings than the incumbent), double-count gates against "
          "tiers 1/2/3/4/5/6/7/8/9, the delta-is-the-one-relocated-constant "
          "gate, and the closed-door bounds on pruning, the terminal fold and "
          "the ledger-free ReLU writes all pass")
    b = suite_bill_per_net()
    incumbent = 147029231264
    print(b.strategy)
    for key, value in b.breakdown().items():
        print(f"  {key:>52} {value:>15,}")
    print(f"  {'incumbent (tier 9)':>52} {incumbent:>15,}")
    print(f"  {'saving (per net, every net)':>52} {incumbent - b.total:>15,}")
    print(f"  ratio vs tier 9                                      "
          f"{b.total / incumbent:.9f}")
    for n_nets in (1, 2, 10, 100):
        num, den = b.amortized_numerator(n_nets)
        print(f"  suite of {n_nets:>5} nets: per-net mean {num / den:,.1f}"
              f"   (exact {num:,} / {den})")
    print("total:", b.total)
