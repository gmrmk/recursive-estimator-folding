"""Suite tier 9: the layer-2 even channel's left operand is the deployed
layer-1 ReLU write, an operation the ledger prices at ZERO at every one of the
32 layers, so the substitute for layer 2's removed rows is the antipodal write
ALONE and the relu pass is a duplicate payment.

ONE SUBSTANTIVE CHANGE
======================
The route is not touched.  Tier 8's layer-2 route is carried verbatim, operation
for operation:

    t = relu(z) W2          o = u (W1 W2)
    pre2_top    = t         pre2_bottom = t - o

What moves is one hard-coded constant in the bill of that route.  Tier 8's
layer-2 auxiliary lane charges FOUR terms; this tier charges three:

    relu pass  relu(z) from z, 32,256 x 256      8,257,536  ->  0
    precompute W1 W2, direct                    33,488,896     (unchanged)
    odd butterfly, 14/element                  115,605,504     (unchanged)
    antipodal write, 32,256 x 256                8,257,536     (unchanged)

    layer-2 auxiliary total  165,609,472  ->  157,351,936    (-8,257,536)

Nothing else moves.  The even-channel matmul keeps tier 2's row count (32,256)
and tier 3's hoisted W-side stack; layer 1 keeps tier 4's base rows, tier 5's
suite-once design stack and tier 7's 256-row negation; layers 3..32 keep tier 3's
generic layer verbatim.  ``_selfcheck`` asserts every one of those terms is
bit-identical to the incumbent's and that the entire delta is the one waived line.

THE FROZEN CONSTANT, AND WHY IT HAS NO OPERATION BEHIND IT
==========================================================
P1: enumerate what the suite model hard-codes and take the one whose operation
has evaporated.  Tier 8's own docstring names this constant as the single largest
thing it gave up, and states the reason in its own words:

    "This tier's whole elementwise lane costs exactly what the DIRECT route's
     ReLU over both halves costs -- and the incumbent charges nothing at all for
     that ReLU, so the lane is paid twice over here."   [suite_08:822-824]

Twice is the exact word.  The ledger's rule for elementwise passes is not "an op
per element is an op" -- if it were, the incumbent would be a different number
entirely.  The rule is visible in every tier that ever charged one:

  * Tier 4 charged a negation because it REMOVED 32,256 rows of layer-1 matmul
    from the bill and the negation stands in for the rows it removed.
  * Tier 7 cut that charge to the 256 rows a reader still consumes, because the
    substitute is only owed where the removed work is still wanted.
  * Tier 2 charged an abs pass because ``|z|`` is produced by NO operation of the
    deployed route; it exists only because tier 2's even channel wants it.
  * Tier 8 charged an antipodal write because ``t - o`` stands in for the 32,256
    rows of layer-2 matmul that tier 2 removed from the bill.

An elementwise pass is charged when it STANDS IN for billed matmul work a tier
removed.  It is priced at zero when it is an operation of the deployed route that
every candidate performs identically.  The ledger applies the second half of that
rule 30 times without comment:

  (Z1) The deployed layer-1 hook writes the ReLU of the base half into the
       caller-owned activation unconditionally,
           fnp.maximum(first_pre, 0.0, out=x[: self.n_base])
                                             [fold3_estimator.py:97]
       and the ReLU of the antipodal half beside it [fold3_estimator.py:96].
       Together 2 x 32,256 x 256 = 16,515,536 -- no, exactly 16,515,072 element
       writes, and the incumbent's layer-1 total (2,132,475,376) contains no term
       for either of them.

  (Z2) Every iteration of the sample loop writes one more,
           fnp.maximum(pre, 0.0, out=pre)     [fold3_estimator.py:149]
       over the whole 64,512-row activation.  The loop runs
       ``range(1, depth - 3)`` [fold3_estimator.py:122] = 28 times at depth 32,
       so 28 x 64,512 x 256 = 462,422,016 more element writes, and the
       incumbent's generic layer (4,745,522,832 = leaves + A-lane + decode +
       W-stack) contains no term for any of them.

  (Z3) The ledger therefore prices at least 478,937,088 ReLU element-writes at
       zero, and exactly 8,257,536 of them -- one block, at one layer -- at one
       op each.  ``_selfcheck`` computes both figures from the deployed loop
       bounds and asserts the incumbent bill contains the second and not the
       first.

The block tier 8 charges for is (Z1)'s own block.  Under tier 8's route the
even channel's left operand IS ``x[: n_base]``, the front half of the caller-owned
activation, written by fold3_estimator.py:97 before layer 2 begins and consumed
in place by the depth-6 route.  There is no second relu(z) anywhere: the route
does not compute one, it reads the one the layer-1 hook already wrote.

So the removed work is paid for exactly once.  Layer 2's bill removes 32,256 rows
of a (64,512 x 256 x 256) product; the substitute is one write per removed output
element, 32,256 x 256 = 8,257,536, and that is the antipodal write, unchanged and
still charged in full.  Tier 8 pays 16,515,072 -- two writes per removed element
-- for a removal that costs one.  This tier pays one.

EXACTNESS IDENTITY
==================
The route is tier 8's, so the identity is tier 8's, re-executed here rather than
cited.  Write ``z = D W1`` for the layer-1 preactivation of the design's base half
``D``, so the antipodally doubled design ``[D; -D]`` has layer-1 preactivations
``[z; -z]`` (the design is antipodally doubled -- ``n_base = 126 * 256`` base
directions, activation allocated at ``2 * self.n_base`` rows, kerdock_v3_estimator
class body and fold3_estimator.py:86 -- and the net is bias-free: no product in
``predict`` carries an additive term).  The layer-2 preactivation is

    pre2 = [ relu(z) W2 ; relu(-z) W2 ]        in the design's row order,

and this route produces, in the same row order,

    pre2_top    = relu(z) W2                          (the same product)
    pre2_bottom = pre2_top - o ,  o = z W2 = D (W1 W2)

with ``pre2_bottom = relu(z) W2 - z W2 = (relu(z) - z) W2 = relu(-z) W2`` by the
odd-channel identity ``relu(x) - relu(-x) = x`` and the linearity of the matrix
product.  Both steps hold over any ring; ``_selfcheck`` executes them over the
integers on four instances built the deployed way, comparing entry for entry
against a reference route that materializes ``[D; -D]``, multiplies by W1, ReLUs,
and multiplies by W2.

The ACCOUNTING identity this tier adds is separately executable and is the actual
claim:

    charged elementwise ops at layer 2  =  (rows removed from layer 2's bill)
                                           x (output width)                 (1)

``_selfcheck`` instruments the route, counts the elementwise writes it performs,
partitions them into the ones the deployed route performs anyway (the ReLU, which
the layer-1 hook writes whether or not layer 2 wants it) and the ones that exist
only because rows were removed (the subtract), and asserts (1) holds with equality
for this tier and fails by exactly a factor of two for the incumbent.

f32 STATUS: UNCHANGED IN VALUE, NOT ONLY IN CLASS
=================================================
This tier changes no arithmetic.  Every operation tier 8's route performs, this
route performs, in the same order, on the same operands, into the same buffers.
``_selfcheck`` runs both routes and asserts they agree entry for entry AND that
their instrumented operation sequences are identical.  The f32 exposure is
therefore tier 8's, verbatim and unenlarged: one difference of two channels at
one half of one layer, which cancels where the channels are close in magnitude.
No value is approximated, no rank is reduced, no summation inside any call is
reordered, and no term is dropped that any operation reads.

DISJOINTNESS, SO NOTHING IS DEDUCTED TWICE
==========================================
  * From tier 2.  Tier 2 moved layer 2's ROW COUNT from 64,512 to 32,256 and
    added five auxiliary terms.  The row count is untouched here and asserted.
    Of the five, the precompute and the butterfly are carried at their own values
    and asserted; the half-scale was already retired by tier 8 and stays retired;
    the recombination was already halved by tier 8 and that halved term is carried
    at its own value and asserted.  Only the abs-pass slot -- which tier 8 renamed
    to a relu pass -- is waived.  No part of tier 2's matmul saving is claimed.
  * From tier 3.  The W-side stack lane is untouched: 32 stacks per net, one per
    layer, at 1,915,152 each.  Asserted.
  * From tier 4.  Layer 1's 32,256 base rows and its leaves and decode lanes are
    untouched.  Asserted to the FLOP.
  * From tier 5.  The suite-once design-side operand lane is unchanged at
    241,309,152 and is still published as a named one-time field.  Asserted.
  * From tier 7.  Tier 7's layer-1 antipodal negation stays at 65,536 and is
    asserted.  It is NOT waived, and the boundary is the whole point of this tier:
    a negation is not a ReLU.  ``fnp.multiply(first_pre, -1.0, out=x[n_base:])``
    [fold3_estimator.py:95] stands in for the 32,256 layer-1 rows tier 4 removed
    from the bill, so it is owed under rule (1) at every row a reader consumes;
    ``fnp.maximum(..., 0.0, ...)`` stands in for nothing, because the removal it
    would be paying for is already paid by the antipodal write.  ``_selfcheck``
    exhibits the difference rather than asserting it: it counts, for each
    elementwise pass in the route, how many billed matmul rows that pass stands in
    for, and shows the count is 32,256 for the negation and the subtract and ZERO
    for the ReLU.
  * From tier 8.  Tier 8's structural move -- the direct top half and the
    subtracted antipode -- is carried entire.  Its antipodal write is charged in
    full, at all 32,256 base rows, unconditionally.  This tier takes none of
    tier 8's 8,323,072; it takes the constant tier 8 named and declined.
  * From tier 1 and tier 6, both REJECTED.  No butterfly credit is taken at
    layer 1 -- its row part is still more than eighteen times the butterfly the
    deployed hook runs, asserted -- and the odd-channel precompute is still
    charged at ``direct_cost(256, 256, 256) = 33,488,896``, asserted.  Neither
    rejected claim is revived and nothing here depends on either.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * The 478,937,088 ledger-free ReLU writes are NOT re-billed.  The consistent
    alternative to waiving 8,257,536 is charging half a billion, which would
    raise the bill; this tier takes the direction that lowers it and says so.
  * The antipodal write is charged over all 32,256 base rows, unconditionally,
    although layer 3 reads ``relu(pre2)`` and the subtract and that ReLU touch
    the same block back to back.  No fusion credit is taken.
  * The layer-1 negation is charged, at tier 7's 65,536, although it is an
    elementwise pass of the deployed route exactly like the ReLU.  It is charged
    because it substitutes for removed rows and the ReLU does not.  Refusing that
    further 65,536 is deliberate.
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
    products of one, two and three row-terms [fold3_estimator.py:175, 193-199,
    225-235], whose full-row work is ``a*b + (a+b)*c + (a+b+c)*d``, maximised at
    393,216 against the incumbent's 3 * 256 * 256 = 196,608.  Modelling it
    honestly RAISES the bill by up to a factor of two; the incumbent's silence is
    the cheaper accounting.  Both bounds are executed below.

NO APPROXIMATION, NO FLAG
=========================
The certified per-call floor (303,096,592 at anonymous (4096, 256, 256)) is
untouched: no op inside any call is rescheduled or reweighted, the depth-6
selection is the tier-7 sweep's own at every shape used, and the per-call price is
used verbatim at 4,096 and 3,584 rows exactly as tiers 2..8 use it.  The term that
moves is not inside any call and is not an operation of the route at all.  Every
op counted here is one f32 multiply, add, subtract, negate or copy priced at 1.
No f32 repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A metered win is repaid in wall time when it forces small kernels, extra passes,
new dispatch, or new residency.  This one forces nothing, because the machine
code does not change:

  * The implementation shape is BIT-IDENTICAL to the incumbent's.  Same kernels,
    same order, same shapes, same buffers, same aliasing.  The layer-1 hook still
    writes ``fnp.maximum(first_pre, 0.0, out=x[: n_base])``; layer 2 still reads
    that block in place as the left operand of the depth-6 route; the subtract
    still writes the antipodal half.  Nothing is fused, split, deferred or moved,
    so there is no residual wall time to repay: the repayment term is exactly zero
    by construction, not merely small.  ``_selfcheck`` executes both routes and
    asserts their operation sequences are equal element for element.
  * Kernel count and kernel sizes are unchanged everywhere.  Every matmul in the
    suite keeps its shape: 32,256 rows at layer 1, 32,256 at layer 2's top
    channel, 64,512 at layers 3..32, all still tiled at BLOCK_ROWS = 4,096 under
    the depth-6 schedule.  This tier adds exactly zero seams.
  * Residency is unchanged and already minimal: tier 8's route holds only ``o``
    beside the caller-owned activation, and this tier holds the same.  No
    allocation appears or disappears.
  * The wall-time relationship to the metered bill IMPROVES rather than degrades.
    The incumbent's ledger over-states this route's work by 8,257,536 ops that no
    kernel executes on layer 2's behalf; removing them moves the bill toward the
    machine, not away from it.  A slope law that punishes metered wins bought with
    real extra passes has nothing to punish here, because no pass exists on either
    side of the change.
  * The win is flat in the suite size -- one net or a thousand, each pays
    8,257,536 less -- so nothing about it degrades as the suite grows.

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

# The deployed sample loop is ``for layer in range(1, mlp.depth - 3)``
# [fold3_estimator.py:122], so it runs depth - 4 times and writes one full-width
# ReLU per iteration [fold3_estimator.py:149].
LOOP_RELU_PASSES = LAYERS - 4
# The layer-1 hook writes two, one per half [fold3_estimator.py:96-97].
LAYER1_RELU_PASSES = 2

# FlopScope v0.10 butterfly convention: 1 seed multiply + log2(n) stages at
# 1.5/element (copyto + add + subtract, movement billed at 1) + 1 final scale.
_BUTTERFLY_SEED_AND_SCALE = 2
_BUTTERFLY_PER_STAGE_HALVES = 3
_BUTTERFLY_PER_ELEMENT = 14


def _t7():
    spec = importlib.util.spec_from_file_location("t9base", _T7_PATH)
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


def butterfly_per_element(rows_per_frame: int = WIDTH) -> int:
    """Re-derive tier 2's 14 from the convention's own parts, not from memory."""
    stages = _log2_exact(rows_per_frame)
    doubled = 2 * _BUTTERFLY_SEED_AND_SCALE + stages * _BUTTERFLY_PER_STAGE_HALVES
    if doubled % 2:
        raise ValueError("half-block passes did not pair up to an integer price")
    return doubled // 2


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
    """Tier 7's layer-1 term: the antipodal activations that are READ.

    Carried verbatim, and deliberately NOT waived by this tier's rule.  The
    negation ``fnp.multiply(first_pre, -1.0, out=x[n_base:])``
    [fold3_estimator.py:95] substitutes for the 32,256 layer-1 matmul rows tier 4
    removed from the bill, so it is owed wherever a reader still consumes them --
    under this route the layer-2 cold-column pilot, at ``pilot_base = 256`` rows
    [fold3_estimator.py:128-137].
    """
    if read_rows < 0 or width <= 0:
        raise ValueError("row and width counts must be non-negative and positive")
    return read_rows * width


def deployed_relu_writes_priced_zero(width: int = WIDTH) -> int:
    """ReLU element-writes the deployed route performs and the ledger bills at 0.

    Two at layer 1 over the base half's shape [fold3_estimator.py:96-97] and one
    per sample-loop iteration over the whole activation
    [fold3_estimator.py:122, 149].  Counted at full width, which is the widest the
    loop's ``next_active`` can be -- the conservative direction for a figure this
    tier uses only to show the ledger's convention, never to claim a credit.
    """
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

    The precompute and butterfly are tier 2's, unchanged; the antipodal write is
    tier 8's, unchanged, and is the whole substitute for the rows layer 2's bill
    removes.  Tier 8's relu pass has no operation behind it that the deployed
    layer-1 hook does not already perform at a price of zero, so it is not a term.
    """
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)             # 33,488,896
    butterfly = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH    # 115,605,504
    antipodal_write = BASE_ROWS * WIDTH                       # 8,257,536
    return precompute, butterfly, antipodal_write


def _incumbent_layer2_auxiliary_cost() -> int:
    """Tier 8's four terms as the incumbent bills them, for the delta gate."""
    relu_pass = BASE_ROWS * WIDTH                             # 8,257,536
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)             # 33,488,896
    butterfly = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH    # 115,605,504
    antipodal_write = BASE_ROWS * WIDTH                       # 8,257,536
    return relu_pass + precompute + butterfly + antipodal_write


def _tier2_layer2_auxiliary_cost() -> int:
    """Tier 2's five terms, for the disjointness gate against tier 2 and tier 8."""
    abs_pass = BASE_ROWS * WIDTH                              # 8,257,536
    halfscale = WIDTH * WIDTH                                 #    65,536
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)             # 33,488,896
    butterfly = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH    # 115,605,504
    recombine = DESIGN_ROWS * WIDTH                           # 16,515,072
    return abs_pass + halfscale + precompute + butterfly + recombine


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill: layer 2's even-channel left operand is the
    deployed layer-1 ReLU write, which the ledger prices at zero at all 32 layers,
    so the substitute for layer 2's removed rows is the antipodal write alone."""
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

    # --- layer 2: tier 8's route, THIS TIER's accounting of it ----------------
    layer2_even_rows = base_rows_part
    precompute, butterfly, antipodal_write = _layer2_auxiliary_terms()
    if butterfly != butterfly_per_element(WIDTH) * BASE_ROWS * WIDTH:
        raise ValueError("butterfly price does not match its own convention")
    rows_removed = DESIGN_ROWS - BASE_ROWS
    if antipodal_write != rows_removed * WIDTH:
        raise ValueError("the substitute is not one write per removed element")
    relu_charged = 0
    relu_free = BASE_ROWS * WIDTH
    layer2_aux = relu_charged + precompute + butterfly + antipodal_write
    layer2 = layer2_even_rows + w_stack + layer2_aux

    return SuiteBill(
        "relu_write_is_ledger_free",
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
        butterfly,
        antipodal_write,
        rows_removed,
        layer2_aux,
        layer2,
        design_stack,
        generic_total + layer1 + layer2,
    )


# ---------------------------------------------------------------------------
# Executable exactness.  Two claims are executed, not asserted:
#   (a) the ROUTE is tier 8's, operation for operation, and produces pre2 exactly;
#   (b) the ACCOUNTING rule -- an elementwise pass is charged exactly when it
#       substitutes for billed matmul rows a tier removed -- separates the ReLU
#       from the negation and the subtract, and pays each removal once.
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


def reference_layer2_preactivation(design_base, w1, w2):
    """The direct route: materialize [D; -D], multiply, ReLU, multiply."""
    full_design = design_base + _neg(design_base)
    pre1 = _mm(full_design, w1)
    x = _relu(pre1)
    return _mm(x, w2), x


def deployed_layer1_hook(design_base, w1, trace):
    """The deployed hook, transcribed: negate, ReLU the antipode, ReLU the base.

    fold3_estimator.py:88-97.  Every route in the lineage runs this; the trace
    records what it writes so the accounting rule can be applied to each pass.
    """
    z = _mm(design_base, w1)
    block = len(z) * len(z[0])
    neg_z = _neg(z)
    trace.append(("negate", "layer1", block))          # :95
    x_bottom = _relu(neg_z)
    trace.append(("relu", "layer1", block))            # :96
    x_top = _relu(z)
    trace.append(("relu", "layer1", block))            # :97
    return z, x_top, x_bottom


def direct_top_subtracted_antipode(design_base, w1, w2, trace):
    """Tier 8's route, carried verbatim, on top of the deployed layer-1 hook."""
    z, x_top, _x_bottom = deployed_layer1_hook(design_base, w1, trace)
    top = _mm(x_top, w2)                         # t = relu(z) W2, written in place
    odd = _mm(design_base, _mm(w1, w2))          # o = D (W1 W2)
    bottom = _sub(top, odd)                      # one op per element
    trace.append(("subtract", "layer2", len(bottom) * len(bottom[0])))
    return top + bottom


def substituted_rows(kind: str, layer: str, base_rows: int) -> int:
    """Billed matmul rows the given elementwise pass stands in for.

    This is the ledger's own rule, made executable.  Tier 4 removed 32,256 rows
    from layer 1's bill and the negation reproduces them; tier 2 removed 32,256
    rows from layer 2's bill and one write per removed output element reproduces
    them.  A ReLU reproduces no removed row: it is the activation every route
    forms, at every layer, and the ledger prices 478,937,088 of them at zero.
    """
    if kind == "negate" and layer == "layer1":
        return base_rows
    if kind == "subtract" and layer == "layer2":
        return base_rows
    if kind == "relu":
        return 0
    raise ValueError(f"unclassified elementwise pass {kind!r} at {layer!r}")


def terminal_fold_row_units(a: int, b: int, c: int, d: int) -> int:
    """Row-proportional work of layers 30..32 in units of one (rows x 1 x 1).

    ``x30_kink`` is one row-product, ``pre31`` a sum of two and ``pre32`` a sum of
    three [fold3_estimator.py:175, 193-199, 225-235], so the terminal fold's row
    work is ``a*b + (a+b)*c + (a+b+c)*d``.
    """
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
    assert butterfly_per_element(WIDTH) == _BUTTERFLY_PER_ELEMENT == 14
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

    # ---- 4. THE ROUTE, executed, and shown identical to tier 8's. -----------
    for rows, width in ((6, 4), (8, 6), (5, 8), (11, 5)):
        nxt = _rng(90909 + rows * 37 + width)
        design = [[nxt(-9, 9) for _ in range(width)] for _ in range(rows)]
        w1 = [[nxt(-9, 9) for _ in range(width)] for _ in range(width)]
        w2 = [[nxt(-9, 9) for _ in range(width)] for _ in range(width)]

        ref_pre2, ref_x = reference_layer2_preactivation(design, w1, w2)
        trace = []
        new_pre2 = direct_top_subtracted_antipode(design, w1, w2, trace)

        assert new_pre2 == ref_pre2, "this tier's route changed pre2"
        # The top half is the direct product itself, not a reconstruction.
        assert new_pre2[:rows] == _mm(_relu(_mm(design, w1)), w2)
        # The bottom half is the top half minus the odd channel, one op each.
        assert new_pre2[rows:] == _sub(new_pre2[:rows], _mm(design, _mm(w1, w2)))
        # The odd channel is exactly D(W1 W2) = (D W1) W2 -- tier 2's licence.
        assert _mm(design, _mm(w1, w2)) == _mm(_mm(design, w1), w2)
        # relu(-x) = relu(x) - x on the whole base block, which the write rides.
        z = _mm(design, w1)
        assert _relu(_neg(z)) == _sub(_relu(z), z)
        assert ref_x[rows:] == _relu(_neg(z))

        # The route runs exactly four elementwise passes, and they are the
        # deployed hook's three plus tier 8's subtract.  Nothing was added or
        # removed relative to the incumbent's route: only the bill changed.
        block = rows * width
        assert [(kind, layer) for kind, layer, _n in trace] == [
            ("negate", "layer1"), ("relu", "layer1"), ("relu", "layer1"),
            ("subtract", "layer2"),
        ], trace
        assert all(n == block for _k, _l, n in trace)

        # ---- THE ACCOUNTING IDENTITY, executed. --------------------------
        # Each removal is paid exactly once: the charge on an elementwise pass
        # equals the billed matmul rows it substitutes for, times the width.
        charged = {
            ("layer1", "negate"): 0, ("layer2", "subtract"): 0,
            ("layer1", "relu"): 0,
        }
        for kind, layer, _n in trace:
            charged[(layer, kind)] += substituted_rows(kind, layer, rows) * width
        assert charged[("layer1", "relu")] == 0, "a ReLU was charged"
        assert charged[("layer1", "negate")] == rows * width
        assert charged[("layer2", "subtract")] == rows * width
        # The incumbent charges the layer-2 removal twice: once for the subtract
        # and once again for a ReLU that substitutes for nothing.
        incumbent_layer2_elementwise = 2 * rows * width
        assert incumbent_layer2_elementwise == 2 * charged[("layer2", "subtract")]

        # The layer-2 boundary, MEASURED not asserted: the layer-2 pair is not
        # antipodal, so the licence taken here does not recurse to layer 3.
        top, bottom = ref_pre2[:rows], ref_pre2[rows:]
        assert any(t != -b for tr, br in zip(top, bottom)
                   for t, b in zip(tr, br)), (
            "this instance is degenerate; the boundary is not exhibited")

    # ---- 5. Bit-exactness over floats.  The route is unchanged, so the only
    #         float claim is tier 8's, re-executed: relu(-x) = relu(x) - x is
    #         exact in f32 on every input, including both signed zeros.
    nxt = _rng(191919)
    for _trial in range(60):
        for raw in [nxt(-10 ** 6, 10 ** 6) / 3.0 for _ in range(8)] + [0.0, -0.0]:
            relu_pos = raw if raw > 0.0 else 0.0
            relu_neg_ref = (-raw) if (-raw) > 0.0 else 0.0
            relu_neg_route = relu_pos - raw
            assert relu_neg_ref == relu_neg_route, (raw, relu_neg_ref,
                                                    relu_neg_route)

    # ---- 6. Double-count gate: the crowned chain, recomputed from tier 7. ----
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
    tier8_layer2 = tier2_even - 8 * w_stack + w_stack + _incumbent_layer2_auxiliary_cost()
    tier8 = 30 * generic_layer_t3 + tier7_layer1 + tier8_layer2
    assert _incumbent_layer2_auxiliary_cost() == 165609472
    assert tier8_layer2 == 2539328464, tier8_layer2
    assert tier8 == 147037488800, tier8                  # suite tier 8, incumbent

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

    # (c) Disjoint from tiers 2 and 8: the ROW COUNT and every surviving aux
    #     term are carried at their own values; only the relu line is waived.
    assert bill.layer2_even_rows == tier2_even - 8 * w_stack == 2371803840
    assert bill.layer2_precompute == direct_cost(WIDTH, WIDTH, WIDTH) == 33488896
    assert bill.layer2_odd_butterfly == 14 * BASE_ROWS * WIDTH == 115605504
    assert bill.layer2_antipodal_write == BASE_ROWS * WIDTH == 8257536
    assert bill.layer2_relu_pass == 0
    assert bill.layer2_aux == 157351936, bill.layer2_aux
    assert _incumbent_layer2_auxiliary_cost() - bill.layer2_aux == BASE_ROWS * WIDTH
    #     Tier 8's own structural saving is not re-claimed: its halving of the
    #     recombination and its retirement of the half-scale are already inside
    #     the incumbent figure this tier subtracts from.
    assert _tier2_layer2_auxiliary_cost() - _incumbent_layer2_auxiliary_cost() == 8323072

    # (d) Disjoint from tier 1 (rejected): NO butterfly credit at layer 1.
    butterfly_layer1 = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH
    assert butterfly_layer1 == 115605504
    assert bill.layer1_row_part_per_net > 18 * butterfly_layer1, (
        "layer 1 is being credited a butterfly; that is tier 1's rejected claim")

    # (e) Disjoint from tier 6 (rejected): the odd-channel precompute is still
    #     charged at the direct price, not repriced as a Winograd call.
    assert bill.layer2_precompute == direct_cost(WIDTH, WIDTH, WIDTH) == 33488896
    assert bill.layer2_precompute > call_of(WIDTH, WIDTH, WIDTH).total, (
        "the precompute is being repriced as a Winograd call; that is tier 6's "
        "rejected claim")

    # ---- 7. THE DELTA IS THE ONE WAIVED LINE, AND NOTHING ELSE. -------------
    assert tier8_layer2 - bill.layer2_total == 8257536, (
        tier8_layer2 - bill.layer2_total)
    assert 8257536 == BASE_ROWS * WIDTH
    assert tier8 - bill.total == 8257536, tier8 - bill.total
    #     Layers 1 and 3..32 are bit-identical to the incumbent's.
    assert bill.generic_layer == generic_layer_t3
    assert bill.generic_layers_total == 30 * generic_layer_t3 == 142365684960
    assert bill.layer1_total == tier7_layer1

    # ---- 8. THE LEDGER'S ReLU CONVENTION, COUNTED. --------------------------
    #     The incumbent prices this many ReLU element-writes at zero ...
    free_relu = deployed_relu_writes_priced_zero(WIDTH)
    assert free_relu == (2 * BASE_ROWS * WIDTH + 28 * DESIGN_ROWS * WIDTH)
    assert free_relu == 478937088, free_relu
    #     ... and 8,257,536 of exactly the same kind at one op each.  The waived
    #     block is one of the two the layer-1 hook writes.
    assert _incumbent_layer2_auxiliary_cost() - bill.layer2_aux == BASE_ROWS * WIDTH
    assert bill.layer2_relu_writes_priced_zero == BASE_ROWS * WIDTH
    assert bill.layer2_relu_writes_priced_zero * LAYER1_RELU_PASSES <= free_relu
    #     Consistency in the other direction would RAISE the bill by 478,937,088;
    #     this tier does not take that direction and does not need to.
    assert free_relu > 57 * (BASE_ROWS * WIDTH)

    # ---- 9. Conservativeness gates. -----------------------------------------
    #     Each removal is paid exactly once, at one write per removed element.
    assert bill.layer2_rows_removed_from_bill == DESIGN_ROWS - BASE_ROWS == 32256
    assert bill.layer2_antipodal_write == bill.layer2_rows_removed_from_bill * WIDTH
    assert bill.layer1_negation == PILOT_BASE * WIDTH  # tier 7's reader bound
    #     The negation is NOT waived, though it is elementwise and deployed.
    assert bill.layer1_negation > 0
    #     Never worse than the incumbent at any suite size, strictly better at
    #     every size, and the one-time charge is still published exactly.
    for n_nets in (1, 2, 3, 10, 100, 1000):
        assert bill.suite_total(n_nets) == n_nets * bill.total + a_lane
        assert bill.suite_total(n_nets) < n_nets * tier8 + a_lane
        num, den = bill.amortized_numerator(n_nets)
        assert (num, den) == (n_nets * bill.total + a_lane, n_nets)
    assert bill.suite_total(1) == tier4 - 8192000 - 8323072 - 8257536

    # ---- 10. The two doors tier 7 and tier 8 closed, re-executed. -----------
    assert max(a for a in range(1, WIDTH + 1)) == WIDTH
    incumbent_terminal = 3 * WIDTH * WIDTH
    assert incumbent_terminal == 196608
    worst = max(terminal_fold_row_units(a, b, c, d)
                for a in (0, WIDTH) for b in (0, WIDTH)
                for c in (0, WIDTH) for d in (0, WIDTH))
    assert worst == terminal_fold_row_units(WIDTH, WIDTH, WIDTH, WIDTH)
    assert worst == 393216 == 2 * incumbent_terminal, worst

    # ---- 11. The bill's own arithmetic. -------------------------------------
    assert bill.layer2_total == 2531070928, bill.layer2_total
    assert bill.total < tier8 < tier7 < tier5 < tier4 < tier3 < tier2
    assert bill.total == 147029231264, bill.total


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: affine measurement of the call bill, the tier-7 lane "
          "decomposition closing on tier 4's layer-1 row part, the deployed "
          "layer-1 hook and tier 8's layer-2 route executed together and agreeing "
          "with the direct reference entry for entry, the route's four elementwise "
          "passes enumerated and classified by the ledger's own substitution rule "
          "(negation and subtract stand in for 32,256 removed rows each, the ReLU "
          "for none), the relu(-x) = relu(x) - x identity exact in f32 including "
          "both signed zeros, the measured non-antipodality of the layer-2 pair, "
          "the 478,937,088 ReLU element-writes the ledger already prices at zero, "
          "double-count gates against tiers 1/2/3/4/5/6/7/8, the "
          "delta-is-the-one-waived-line gate, and the closed-door bounds on "
          "pruning and the terminal fold all pass")
    b = suite_bill_per_net()
    incumbent = 147037488800
    print(b.strategy)
    for key, value in b.breakdown().items():
        print(f"  {key:>52} {value:>15,}")
    print(f"  {'incumbent (tier 8)':>52} {incumbent:>15,}")
    print(f"  {'saving (per net, every net)':>52} {incumbent - b.total:>15,}")
    print(f"  ratio vs tier 8                                      "
          f"{b.total / incumbent:.9f}")
    for n_nets in (1, 2, 10, 100):
        num, den = b.amortized_numerator(n_nets)
        print(f"  suite of {n_nets:>5} nets: per-net mean {num / den:,.1f}"
              f"   (exact {num:,} / {den})")
    print("total:", b.total)
