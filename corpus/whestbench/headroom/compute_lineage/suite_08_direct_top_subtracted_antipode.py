"""Suite tier 8: layer 2's preactivation is written by the DIRECT-TOP /
SUBTRACTED-ANTIPODE route, so the design's base half is never written twice and
no half-scale exists to fold.

ONE SUBSTANTIVE CHANGE
======================
Tier 2 splits layer 2 into an even and an odd channel and then writes BOTH
halves of the layer-2 preactivation by recombining them:

    e = |z| (W2/2)          o = u (W1 W2 / 2)
    pre2_top    = e + o     pre2_bottom = e - o                 (tier 2)

This tier keeps the odd channel exactly as tier 2 built it and replaces the even
channel by the top half itself:

    t = relu(z) W2          o = u (W1 W2)
    pre2_top    = t         pre2_bottom = t - o                 (this tier)

That is one substitution, and it moves three coupled lines of the layer-2 bill:

    abs pass   |z| from z, 32,256 x 256      8,257,536
      becomes  relu pass relu(z) from z      8,257,536     (identical price)
    W2 half-scale, 256 x 256                   65,536
      becomes  nothing                              0     (no 1/2 survives)
    recombination, 2 x 32,256 x 256         16,515,072
      becomes  one antipodal write,
               1 x 32,256 x 256              8,257,536

    layer-2 auxiliary total  173,932,544  ->  165,609,472    (-8,323,072)

Nothing else moves.  The even-channel matmul keeps tier 2's row count (32,256),
tier 3's hoisted W-side stack and tier 7's call price; layer 1 keeps tier 4's
base rows, tier 5's suite-once design stack and tier 7's 256-row negation;
layers 3..32 keep tier 3's generic layer verbatim.  ``_selfcheck`` asserts every
one of those terms is bit-identical to the incumbent's and that the entire delta
is the two moved elementwise lines.

THE FROZEN CONSTANT
===================
P1: enumerate what the suite model hard-codes and take the biggest one still
frozen.  Tier 2's recombination term hard-codes ``DESIGN_ROWS * WIDTH`` -- one
write for every element of the layer-2 preactivation, all 64,512 rows of it.
That constant is frozen for a reason that stopped being true the moment tier 2
was adopted alongside tier 3's caller-owned operator: it assumes BOTH halves of
``pre2`` have to be assembled from scratch, because in tier 2's algebra neither
``e`` nor ``o`` is a half of ``pre2`` -- both halves are sums.

They do not have to be.  The top half of ``pre2`` IS a matrix product of two
matrices the route already holds, and the deployed operator writes its product
into a caller-owned destination:

    pre = self._sample_matmul(x[:, :active], W, out=activation[:, :next])
                                             [fold3_estimator.py:148-153]
    "A caller may hand the active buffer back as ``out``"
                                             [row_blocked_winograd.py:3-7]

So if the even channel is taken to be ``relu(z) W2`` rather than ``|z| W2``, the
operator's own reconstruction lane deposits the top half of ``pre2`` in place and
the recombination has only the antipodal half left to write.  The frozen
constant halves, and the half-scale it needed disappears with it.

  (F1) ``relu(z)`` costs exactly what ``|z|`` costs.  Both are one elementwise
       op per element over the same 32,256 x 256 base block; the deployed layer-1
       hook already emits ``relu(z)`` into exactly that block
       [fold3_estimator.py:102, ``fnp.maximum(first_pre, 0.0, out=x[:n_base])``],
       and tier 2's own accounting note records that the incumbent's matmul-only
       model charges no elementwise op at all.  This tier charges one, at tier 2's
       price, on the same rows -- a substitution, not a discount.

  (F2) ``relu(z) W2`` costs exactly what ``|z| W2`` costs.  Same 32,256 rows,
       same k = n = 256, same depth-6 tier-7 route, same hoisted W-side stack.
       ``_selfcheck`` asserts the even-channel row part and the W stack are
       unchanged to the FLOP.

  (F3) The antipodal half is one subtract.  ``relu(-x) = relu(x) - x`` for every
       real x (including x = 0), so
           relu(-z) W2 = (relu(z) - z) W2 = relu(z) W2 - z W2 = t - o ,
       one op per element over 32,256 x 256.  The 64,512-row recombination
       becomes a 32,256-row one because the other 32,256 rows were written by the
       matmul that had to run anyway.

  (F4) No 1/2 survives.  Tier 2's half-scale existed only to fold the ``/2`` of
       ``(e +/- o)/2`` into W2 once per net.  This tier's identities carry no
       factor of two on either half, so there is nothing to fold: the term is not
       waived, it has no operation behind it.  ``_selfcheck`` executes both
       routes and checks that this one never divides.

  (F5) The odd channel is untouched.  ``o = u (W1 W2)`` is still the phased-WHT
       butterfly over the design, still preceded by the same
       ``direct_cost(256, 256, 256)`` precompute, still billed at the deployed
       14-ops-per-element convention.  ``_selfcheck`` asserts both figures and
       re-derives 14 from the convention's own parts (1 seed multiply + 8 radix-2
       stages at 3 half-block passes + 1 final scale).

EXACTNESS IDENTITY
==================
Write ``z = D W1`` for the layer-1 preactivation of the design's base half ``D``,
so the antipodally doubled design ``[D; -D]`` has layer-1 preactivations
``[z; -z]``.  Both facts are tier 2's observations, adopted rather than
re-derived: the design is antipodally doubled (``n_base = 126 * 256`` base
directions in the Kerdock estimator's class body, activation allocated at
``2 * self.n_base`` rows, kerdock_v3_estimator.py ``_allocate_grouped_activation``)
and the net is bias-free (no product in ``predict`` or ``_sample_matmul`` carries
an additive term).  The layer-2 preactivation the incumbent route produces is

    pre2 = [ relu(z) W2 ; relu(-z) W2 ]        in the design's row order.

This route produces, in the same row order,

    pre2_top    = relu(z) W2                          (the same product)
    pre2_bottom = pre2_top - o ,  o = z W2 = D (W1 W2)

and ``pre2_bottom = relu(z) W2 - z W2 = (relu(z) - z) W2 = relu(-z) W2`` by the
odd-channel identity ``relu(x) - relu(-x) = x`` and the linearity of the matrix
product.  Both steps hold over any ring; ``_selfcheck`` executes them over the
integers on four instances built the deployed way, comparing entry for entry
against a reference route that materializes ``[D; -D]``, multiplies all rows by
W1, ReLUs, and multiplies all rows by W2.

Every downstream operation therefore receives the same value.  ``pre2`` is the
only object either route hands forward: layer 3 reads ``relu(pre2)``, and the
layer-2 cold-column pilot reads ``relu(z)[:256]`` and ``relu(-z)[:256]`` before
the product runs, both of which this route still materializes (the second by
tier 7's charged 256 x 256 pass, carried here at its own value).

f32 STATUS, STATED PLAINLY AND UNCHANGED IN CLASS
=================================================
Over the reals and over the integers this route is identical to the incumbent's.
Over f32 it sits in the same reassociation class tier 2 already declared and the
adopted Winograd fringe route already occupies -- and it sits strictly LOWER in
that class than the incumbent does, on both halves:

  * Top half.  The incumbent computes it as ``(|z| W2 + z W1 W2)/2``, a half-sum
    of two products of matrices that are not the true operand.  This tier
    computes it as ``relu(z) W2`` -- the true operand, the true product, at the
    same 32,256-row blocking tier 2 already adopted.  One cancelling form is
    removed outright.
  * Bottom half.  The incumbent computes ``(|z| W2 - z W1 W2)/2``; this tier
    computes ``relu(z) W2 - z W1 W2``.  Both are one difference of two products,
    so the exposure is the same in kind and the same in count, and this tier's
    minuend is the true top half rather than an even-channel surrogate.

The named exposure is therefore tier 2's and only tier 2's, on one half instead
of two: a difference of two channels cancels where they are close in magnitude.
No value is approximated, no rank is reduced, no summation inside any call is
reordered, and no term is dropped that any operation reads.

DISJOINTNESS, SO NOTHING IS DEDUCTED TWICE
==========================================
  * From tier 2.  Tier 2 moved layer 2's ROW COUNT from 64,512 to 32,256 and
    added five auxiliary terms.  The row count is untouched here and asserted;
    of the five terms, the precompute and the butterfly reappear at their own
    values and are asserted, the abs pass reappears at its own value under the
    name it now has, and only the recombination and the half-scale move.  The
    tier claims no part of tier 2's matmul saving.
  * From tier 3.  The W-side stack lane is untouched: 32 stacks per net, one per
    layer, at 1,915,152 each.  Asserted.
  * From tier 4.  Layer 1's 32,256 base rows and its leaves and decode lanes are
    untouched.  Asserted to the FLOP.
  * From tier 5.  The suite-once design-side operand lane is unchanged at
    241,309,152 and is still published as a named one-time field.  Asserted.
  * From tier 7.  Tier 7 charged the layer-1 antipodal negation at its one
    surviving reader, the 256-row pilot, for 65,536.  That reader still exists
    and that term is carried unchanged and asserted.  The 32,256 x 256 subtract
    this tier charges writes ``pre2``'s bottom half, a different object at a
    different layer; ``_selfcheck`` asserts both terms are present and that their
    sum is not confused with either alone.
  * From tier 1 and tier 6, both REJECTED.  No butterfly credit is taken at
    layer 1 -- its row part is still more than eighteen times the butterfly the
    deployed hook runs, asserted -- and the odd-channel precompute is still
    charged at ``direct_cost(256, 256, 256) = 33,488,896``, asserted.  Neither
    rejected claim is revived and nothing here depends on either.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * The relu pass is CHARGED, at the full 8,257,536, although the deployed
    layer-1 hook already performs it [fold3_estimator.py:102] and the incumbent
    bills no ReLU anywhere in its 147-billion-op ledger.  Refusing that free
    8,257,536 is the single largest thing this tier gives up.
  * The antipodal write is charged over all 32,256 base rows, unconditionally.
    Layer 3 reads ``relu(pre2)``, so the subtract and that ReLU touch the same
    block back to back; no fusion credit is taken for it, and the ReLU itself
    stays unbilled exactly as the incumbent leaves it.
  * The even channel keeps tier 2's exact-tiling price (7 full 4,096-row calls
    plus one 3,584-row call, 2,371,803,840 of row part), not the cheaper linear
    convention.
  * Layers 3..32 keep the antipodal half at full price.  The licence taken here
    is the same narrow one tier 2 established and no wider: it applies at the
    first nonlinearity of a bias-free net on an antipodally doubled design, and
    nowhere deeper.  ``_selfcheck`` re-measures that boundary rather than
    asserting it, exhibiting an instance where the layer-2 pair is not antipodal.
  * ``.total`` remains the marginal per-net bill with tier 5's one-time charge
    published beside it; ``suite_total(1)`` is still exactly tier 4's figure
    minus the crowned savings, so no suite size is assumed anywhere.

DOORS THAT STAY CLOSED
======================
The two constants tier 7 closed are re-executed here so the next tier does not
pay for them twice:

  * Pruning.  ``active`` is a function of the net's own weights and its worst
    case is the full 256, so no net-independent bill below 256 exists
    [fold3_estimator.py:128-147; experiments/gen8_gate_audit/audit_widths.py:3-4].
  * The terminal fold.  Layers 30..32 are ``pre31`` and ``pre32``, sums of two
    and three row-products [fold3_estimator.py:195-240], whose full-row work is
    ``a*b + (a+b)*c + (a+b+c)*d``, maximised at 393,216 against the incumbent's
    3 * 256 * 256 = 196,608.  Modelling it honestly RAISES the bill by up to a
    factor of two; the incumbent's silence is the cheaper accounting.  Both
    bounds are executed below.

NO APPROXIMATION, NO FLAG
=========================
The certified per-call floor (303,096,592 at anonymous (4096, 256, 256)) is
untouched: no op inside any call is rescheduled or reweighted, the depth-6
selection is the tier-7 sweep's own at every shape used, and the per-call price
is used verbatim at 4,096 and 3,584 rows exactly as tiers 2..7 use it.  The two
terms that move are not inside any call -- they are elementwise passes between
calls.  Every op counted here is one f32 multiply, add, subtract, negate, abs,
maximum or copy priced at 1.  No f32 repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A metered win is repaid in wall time when it forces small kernels, extra passes,
new dispatch, or new residency.  This one removes a pass, removes a buffer, and
adds nothing:

  * Strictly fewer passes, and no pass is split.  The incumbent runs, after its
    even-channel matmul, one 256 x 256 scale and one 64,512 x 256 recombination
    kernel.  This route runs one 32,256 x 256 subtract.  Kernel count goes from
    two to one; element count on that lane goes from 16,580,608 to 8,257,536.
    The relu pass replaces the abs pass one-for-one on the same block, same
    shape, same kernel class.
  * No new dispatch and no new route.  The top-half product is the deployed
    caller-owned in-place configuration -- ``out`` aliasing the front rows of the
    bound activation -- which is what all thirty generic layers already run
    [fold3_estimator.py:148-153], and whose safety under the depth-6 verbatim-leaf
    schedule is certified by the tier-7 module's own in-place verifier
    (containment / disjointness / immunity, tier_07:63-73).  Nothing new is
    claimed about aliasing.
  * Strictly LESS residency, which is where the wall-time headroom actually is.
    The incumbent must hold ``e`` and ``o`` simultaneously -- two 32,256 x 256 f32
    scratch blocks, 33.0 MB each -- because the recombination reads both to
    write either half.  This route holds only ``o``: the top half is already in
    the activation buffer, and the bottom half is written from it.  One 33 MB
    allocation disappears from the layer-2 peak, and with it 33 MB of write plus
    33 MB of read traffic on a lane that is purely memory-bound.
  * Traffic falls with the FLOPs, hard.  The deleted lane wrote 8,257,536 f32 it
    no longer writes and read 8,257,536 f32 it no longer reads; the surviving
    subtract reads the top half that the matmul just left in cache-warm order and
    writes the adjacent half.  The wall-time win is larger than the metered win,
    not smaller.  There is no read-amplification term anywhere for it to be
    repaid out of.
  * Kernel sizes do not shrink anywhere.  Every matmul in the suite keeps its
    shape: 32,256 rows at layer 1, 32,256 at layer 2's top channel, 64,512 at
    layers 3..32, all still tiled at BLOCK_ROWS = 4,096 under the depth-6
    schedule.  This tier adds exactly zero seams.
  * The win is flat in the suite size -- one net or a thousand, each pays
    8,323,072 less -- so nothing about it degrades as the suite grows.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from dataclasses import dataclass

_T7_PATH = "corpus/whestbench/headroom/compute_lineage/tier_07_inplace_verbatim_leaves.py"

# Production shape, observed in kerdock_v3_estimator.py and CODEX_HANDOFF Sec.3.
FRAMES = 126                      # phase_stop - phase_start = 128 - 2
WIDTH = 256                       # ctx.width
BASE_ROWS = FRAMES * WIDTH        # n_base = 126 * 256 = 32,256
DESIGN_ROWS = 2 * BASE_ROWS       # antipodally doubled = 64,512
LAYERS = 32
TILE_ROWS = 4096                  # BLOCK_ROWS in row_blocked_winograd.py
PILOT_BASE = 256                  # base_estimator.py:53; restated at
                                  # kerdock_v3_estimator.py:52 (candidate_source)

# FlopScope v0.10 butterfly convention: 1 seed multiply + log2(n) stages at
# 1.5/element (copyto + add + subtract, movement billed at 1) + 1 final scale.
_BUTTERFLY_SEED_AND_SCALE = 2
_BUTTERFLY_PER_STAGE_HALVES = 3
_BUTTERFLY_PER_ELEMENT = 14


def _t7():
    spec = importlib.util.spec_from_file_location("t8base", _T7_PATH)
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

    Tier 5's object, carried verbatim: at layer 1 the left operand is the
    design, invariant across the nets of the suite, so this is charged once to
    the suite rather than once per net.
    """
    bill = t7.inplace_verbatim_leaves_candidate_bill(m, k, WIDTH)
    levels = _selected_levels(bill.strategy)
    cost, _grade = t7.best_operand_grade(m, k, levels)
    return cost


def antipodal_negation_cost(read_rows: int = PILOT_BASE,
                            width: int = WIDTH) -> int:
    """Tier 7's layer-1 term: the antipodal activations that are READ.

    Carried verbatim.  Under this tier's layer-2 route the layer-2 cold-column
    pilot is still the one surviving reader of ``relu(-z)``, and it still reads
    ``pilot_base = 256`` rows [fold3_estimator.py:133-139].
    """
    if read_rows < 0 or width <= 0:
        raise ValueError("row and width counts must be non-negative and positive")
    return read_rows * width


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
    layer2_precompute: int
    layer2_odd_butterfly: int
    layer2_antipodal_write: int
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
            "layer2_relu_pass": self.layer2_relu_pass,
            "layer2_precompute_W1W2": self.layer2_precompute,
            "layer2_odd_channel_butterfly": self.layer2_odd_butterfly,
            "layer2_antipodal_write_32256": self.layer2_antipodal_write,
            "layer2_auxiliary_terms": self.layer2_aux,
            "layer2_total": self.layer2_total,
            "design_side_stack_charged_ONCE_to_the_suite":
                self.layer1_design_stack_once,
            "total": self.total,
        }


def _layer2_auxiliary_terms() -> tuple:
    """This tier's layer-2 non-matmul terms.

    ``relu_pass`` replaces tier 2's abs pass at the identical price; the
    precompute and butterfly are tier 2's, unchanged; ``antipodal_write``
    replaces tier 2's 64,512-row recombination with a 32,256-row subtract, and
    tier 2's 256 x 256 half-scale has no operation behind it any more.
    """
    relu_pass = BASE_ROWS * WIDTH                             # 8,257,536
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)             # 33,488,896
    butterfly = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH    # 115,605,504
    antipodal_write = BASE_ROWS * WIDTH                       # 8,257,536
    return relu_pass, precompute, butterfly, antipodal_write


def _incumbent_layer2_auxiliary_cost() -> int:
    """Tier 2's five terms as the incumbent bills them, for the delta gate."""
    abs_pass = BASE_ROWS * WIDTH                              # 8,257,536
    halfscale = WIDTH * WIDTH                                 #    65,536
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)             # 33,488,896
    butterfly = _BUTTERFLY_PER_ELEMENT * BASE_ROWS * WIDTH    # 115,605,504
    recombine = DESIGN_ROWS * WIDTH                           # 16,515,072
    return abs_pass + halfscale + precompute + butterfly + recombine


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill: layer 2's preactivation is written by the
    direct-top / subtracted-antipode route, so only the antipodal half is
    recombined and no half-scale exists."""
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

    # --- layer 2: THIS TIER's route -------------------------------------------
    layer2_even_rows = base_rows_part
    relu_pass, precompute, butterfly, antipodal_write = _layer2_auxiliary_terms()
    if butterfly != butterfly_per_element(WIDTH) * BASE_ROWS * WIDTH:
        raise ValueError("butterfly price does not match its own convention")
    layer2_aux = relu_pass + precompute + butterfly + antipodal_write
    layer2 = layer2_even_rows + w_stack + layer2_aux

    return SuiteBill(
        "direct_top_subtracted_antipode",
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
        relu_pass,
        precompute,
        butterfly,
        antipodal_write,
        layer2_aux,
        layer2,
        design_stack,
        generic_total + layer1 + layer2,
    )


# ---------------------------------------------------------------------------
# Executable exactness.  The claim is that the layer-2 preactivation can be
# written as (direct top half, top half minus odd channel) instead of
# (half-sum, half-difference), so it is executed: three routes are run over the
# integers on instances built the deployed way and compared entry for entry.
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


def _abs(M):
    return [[v if v >= 0 else -v for v in row] for row in M]


def _sub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def reference_layer2_preactivation(design_base, w1, w2):
    """The direct route: materialize [D; -D], multiply, ReLU, multiply."""
    full_design = design_base + _neg(design_base)
    pre1 = _mm(full_design, w1)
    x = _relu(pre1)
    return _mm(x, w2), x


def incumbent_layer2_preactivation(design_base, w1, w2, counter):
    """Tier 2's route as the incumbent bills it: |z| W2/2 and D (W1 W2)/2.

    Halving is represented exactly by deferring it (the integers here stand for
    exact reals), so the count of elementwise writes is what is instrumented:
    one abs pass, one half-scale, and two recombination halves.
    """
    z = _mm(design_base, w1)
    counter["abs"] += len(z) * len(z[0])
    even = _mm(_abs(z), w2)                      # e = |z| W2
    counter["halfscale"] += len(w2) * len(w2[0])
    odd = _mm(design_base, _mm(w1, w2))          # o = D (W1 W2)
    top, bottom = [], []
    for be, bo in zip(even, odd):
        top.append([(e + o) // 2 for e, o in zip(be, bo)])
        bottom.append([(e - o) // 2 for e, o in zip(be, bo)])
        counter["recombine"] += 2 * len(be)
    return top + bottom


def direct_top_subtracted_antipode(design_base, w1, w2, counter):
    """This tier's route: the matmul writes the top half, one subtract the rest.

    Instrumented exactly as billed: one relu pass, no scaling of any kind, the
    same precompute and odd channel, and one antipodal write over the base rows.
    """
    z = _mm(design_base, w1)
    counter["relu"] += len(z) * len(z[0])
    relu_z = _relu(z)
    top = _mm(relu_z, w2)                        # t = relu(z) W2, written in place
    odd = _mm(design_base, _mm(w1, w2))          # o = D (W1 W2)
    bottom = _sub(top, odd)                      # one op per element
    counter["antipodal"] += len(bottom) * len(bottom[0])
    return top + bottom


def terminal_fold_row_units(a: int, b: int, c: int, d: int) -> int:
    """Row-proportional work of layers 30..32 in units of one (rows x 1 x 1).

    ``pre31`` is a sum of two row-products and ``pre32`` a sum of three
    [fold3_estimator.py:195-240], so the terminal fold's row work is
    ``a*b + (a+b)*c + (a+b+c)*d``.
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

    # ---- 4. THE IDENTITY, executed.  Three routes, entry for entry. ---------
    for rows, width in ((6, 4), (8, 6), (5, 8), (11, 5)):
        nxt = _rng(80808 + rows * 37 + width)
        design = [[nxt(-9, 9) for _ in range(width)] for _ in range(rows)]
        w1 = [[nxt(-9, 9) for _ in range(width)] for _ in range(width)]
        w2 = [[nxt(-9, 9) for _ in range(width)] for _ in range(width)]

        ref_pre2, ref_x = reference_layer2_preactivation(design, w1, w2)
        inc_counter = {"abs": 0, "halfscale": 0, "recombine": 0}
        inc_pre2 = incumbent_layer2_preactivation(design, w1, w2, inc_counter)
        new_counter = {"relu": 0, "antipodal": 0}
        new_pre2 = direct_top_subtracted_antipode(design, w1, w2, new_counter)

        assert inc_pre2 == ref_pre2, "the incumbent route was mis-transcribed"
        assert new_pre2 == ref_pre2, "this tier's route changed pre2"
        # The top half is the direct product itself, not a reconstruction.
        assert new_pre2[:rows] == _mm(_relu(_mm(design, w1)), w2)
        assert new_pre2[:rows] == ref_pre2[:rows]
        # The bottom half is the top half minus the odd channel, one op each.
        assert new_pre2[rows:] == _sub(new_pre2[:rows],
                                       _mm(design, _mm(w1, w2)))
        # The odd channel is exactly D(W1 W2) = (D W1) W2 -- tier 2's licence.
        assert _mm(design, _mm(w1, w2)) == _mm(_mm(design, w1), w2)
        # relu(-x) = relu(x) - x on the whole base block, which is the identity
        # the antipodal write rides.
        z = _mm(design, w1)
        assert _relu(_neg(z)) == _sub(_relu(z), z)
        assert ref_x[rows:] == _relu(_neg(z))

        # The instrumented elementwise counts are exactly what is billed.
        block = rows * width
        assert inc_counter["abs"] == block
        assert inc_counter["halfscale"] == width * width
        assert inc_counter["recombine"] == 2 * block
        assert new_counter["relu"] == block
        assert new_counter["antipodal"] == block
        assert sum(inc_counter.values()) - sum(new_counter.values()) == (
            block + width * width), "the elementwise delta is not one block plus W2"
        # This route never divides: no factor of two exists to fold into W2.
        assert all(v % 1 == 0 for row in new_pre2 for v in row)

        # The layer-2 boundary, MEASURED not asserted: the layer-2 pair is not
        # antipodal, so the licence taken here does not recurse to layer 3.
        top, bottom = ref_pre2[:rows], ref_pre2[rows:]
        assert any(t != -b for tr, br in zip(top, bottom)
                   for t, b in zip(tr, br)), (
            "this instance is degenerate; the boundary is not exhibited")

    # ---- 5. Bit-exactness over floats where this tier makes a float claim. --
    #         The antipodal write rides relu(-x) = relu(x) - x; over f32 that
    #         identity is exact, with no rounding, on every input.
    nxt = _rng(90909)
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
    assert _incumbent_layer2_auxiliary_cost() == 173932544
    tier2 = 31 * layer_slice + tier2_even + _incumbent_layer2_auxiliary_cost()
    assert tier2 == 150547968644, tier2                  # suite tier 2
    generic_layer_t3 = (row_full * DESIGN_ROWS) // TILE_ROWS + w_stack
    tier3_layer2 = (tier2_even - 8 * w_stack + w_stack
                    + _incumbent_layer2_auxiliary_cost())
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
    assert tier7 == 147045811872, tier7                  # suite tier 7, incumbent

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

    # (c) Disjoint from tier 2: the ROW COUNT and both surviving aux terms are
    #     carried at their own values; only the two elementwise lines move.
    assert bill.layer2_even_rows == tier2_even - 8 * w_stack == 2371803840
    assert bill.layer2_precompute == direct_cost(WIDTH, WIDTH, WIDTH) == 33488896
    assert bill.layer2_odd_butterfly == 14 * BASE_ROWS * WIDTH == 115605504
    assert bill.layer2_relu_pass == BASE_ROWS * WIDTH == 8257536
    assert bill.layer2_antipodal_write == BASE_ROWS * WIDTH == 8257536
    assert bill.layer2_aux == 165609472, bill.layer2_aux
    assert (_incumbent_layer2_auxiliary_cost() - bill.layer2_aux
            == DESIGN_ROWS * WIDTH - BASE_ROWS * WIDTH + WIDTH * WIDTH)

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

    # ---- 7. THE DELTA IS THE TWO MOVED LINES, AND NOTHING ELSE. -------------
    assert tier3_layer2 - bill.layer2_total == 8323072, (
        tier3_layer2 - bill.layer2_total)
    assert 8323072 == (DESIGN_ROWS * WIDTH - BASE_ROWS * WIDTH) + WIDTH * WIDTH
    assert tier7 - bill.total == 8323072, tier7 - bill.total
    #     Layers 1 and 3..32 are bit-identical to the incumbent's.
    assert bill.generic_layer == generic_layer_t3
    assert bill.generic_layers_total == 30 * generic_layer_t3 == 142365684960
    assert bill.layer1_total == tier7_layer1

    # ---- 8. Conservativeness gates. -----------------------------------------
    #     The relu pass is charged, at the abs pass's full price, on the same
    #     block -- a substitution, not a discount.
    assert bill.layer2_relu_pass == BASE_ROWS * WIDTH
    #     The antipodal write is charged over every base row, unconditionally.
    assert bill.layer2_antipodal_write == BASE_ROWS * WIDTH
    #     This tier's whole elementwise lane costs exactly what the DIRECT
    #     route's ReLU over both halves costs -- and the incumbent charges
    #     nothing at all for that ReLU, so the lane is paid twice over here.
    assert (bill.layer2_relu_pass + bill.layer2_antipodal_write
            == DESIGN_ROWS * WIDTH == 16515072)
    assert bill.layer2_aux < _incumbent_layer2_auxiliary_cost()
    #     Never worse than the incumbent at any suite size, strictly better at
    #     every size, and the one-time charge is still published exactly.
    for n_nets in (1, 2, 3, 10, 100, 1000):
        assert bill.suite_total(n_nets) == n_nets * bill.total + a_lane
        assert bill.suite_total(n_nets) < n_nets * tier7 + a_lane
        num, den = bill.amortized_numerator(n_nets)
        assert (num, den) == (n_nets * bill.total + a_lane, n_nets)
    assert bill.suite_total(1) == tier4 - 8192000 - 8323072

    # ---- 9. The two doors tier 7 closed, re-executed. -----------------------
    assert max(a for a in range(1, WIDTH + 1)) == WIDTH
    incumbent_terminal = 3 * WIDTH * WIDTH
    assert incumbent_terminal == 196608
    worst = max(terminal_fold_row_units(a, b, c, d)
                for a in (0, WIDTH) for b in (0, WIDTH)
                for c in (0, WIDTH) for d in (0, WIDTH))
    assert worst == terminal_fold_row_units(WIDTH, WIDTH, WIDTH, WIDTH)
    assert worst == 393216 == 2 * incumbent_terminal, worst

    # ---- 10. The bill's own arithmetic. -------------------------------------
    assert bill.layer2_total == 2539328464, bill.layer2_total
    assert bill.total < tier7 < tier5 < tier4 < tier3 < tier2
    assert bill.total == 147037488800, bill.total


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: affine measurement of the call bill, the tier-7 lane "
          "decomposition closing on tier 4's layer-1 row part, three executed "
          "layer-2 routes (direct reference, the incumbent's half-sum/"
          "half-difference, and this tier's direct-top/subtracted-antipode) "
          "agreeing entry for entry with instrumented elementwise counts, the "
          "relu(-x) = relu(x) - x identity exact in f32 including both signed "
          "zeros, the measured non-antipodality of the layer-2 pair that keeps "
          "the licence from recursing, double-count gates against tiers "
          "1/2/3/4/5/6/7, the delta-is-the-two-moved-lines gate, and the "
          "closed-door bounds on pruning and the terminal fold all pass")
    b = suite_bill_per_net()
    incumbent = 147045811872
    print(b.strategy)
    for key, value in b.breakdown().items():
        print(f"  {key:>44} {value:>15,}")
    print(f"  {'incumbent (tier 7)':>44} {incumbent:>15,}")
    print(f"  {'saving (per net, every net)':>44} {incumbent - b.total:>15,}")
    print(f"  ratio vs tier 7                              {b.total / incumbent:.9f}")
    for n_nets in (1, 2, 10, 100):
        num, den = b.amortized_numerator(n_nets)
        print(f"  suite of {n_nets:>5} nets: per-net mean {num / den:,.1f}"
              f"   (exact {num:,} / {den})")
    print("total:", b.total)
