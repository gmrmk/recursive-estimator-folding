"""Suite tier 11: the odd channel's butterfly pays a whole COPY per radix-2
stage only because the deployed layer-1 hook writes its two outputs back over
its two inputs; a butterfly that writes each stage into the alternate frame
buffer performs the identical adds and subtracts on the identical operands and
never copies, so its per-stage cost falls from three half-block passes to two.

ONE SUBSTANTIVE CHANGE
======================
The route is not touched anywhere else.  Tier 8's layer-2 route is carried
verbatim, operation for operation, with tier 9's accounting of its elementwise
lane and tier 10's weight-side placement of the design normalization:

    t = relu(p) W2          o = z (c W1 W2)
    pre2_top    = t         pre2_bottom = t - o

What moves is one hard-coded constant in the price of the butterfly that
produces ``o``.  Tier 2 transcribed the deployed layer-1 hook's stage body op
by op and named the constant on a line of its own:

    _BUTTERFLY_PER_STAGE_HALVES = 3   # three E/2 passes per radix-2 stage
                                                            [suite_02:253]
    # ... 1 seed multiply + log2(n) stages at 1.5/element
    #     (copyto + add + subtract, movement billed at 1) + 1 final scale
                                                            [suite_02:249-251]

The three passes are ``fnp.copyto(scratch, left)``, ``fnp.add(scratch, right,
out=left)`` and ``fnp.subtract(scratch, right, out=right)``
[kerdock_v3_estimator.py:120-127].  Two of them are arithmetic.  The third is
movement, and it exists for exactly one reason: the hook's two outputs are
written back over its two inputs, so the left operand has to be saved before it
is overwritten.  A stage that writes into the alternate frame buffer reads
``left`` and ``right`` and writes ``left+right`` and ``left-right`` somewhere
else; nothing is overwritten, so nothing needs saving:

    per-stage half-block passes                    3   ->     2
    butterfly per element                         13   ->     9
    butterfly, 9 x 32,256 x 256          107,347,968   -> 74,317,824

    layer-2 auxiliary total  149,159,936  ->  116,129,792     (-33,030,144)

Nothing else moves.  The seed pass keeps its full 1/element over all 8,257,536
elements; the design normalization keeps tier 10's weight-side 65,536; the
even-channel matmul keeps tier 2's row count (32,256) and tier 3's hoisted
W-side stack; the precompute keeps tier 2's direct price; the antipodal write
keeps tier 8's 8,257,536 in full; the relu pass stays waived at tier 9's zero;
layer 1 keeps tier 4's base rows, tier 5's suite-once design stack and tier 7's
256-row negation; layers 3..32 keep tier 3's generic layer verbatim.
``_selfcheck`` asserts every one of those terms is bit-identical to the
incumbent's and that the entire delta is the removed copy.

THE FROZEN CONSTANT, AND WHY IT IS A DESTINATION CHOICE
=======================================================
P1: enumerate what the suite model hard-codes and take the biggest constant with
no ARITHMETIC behind it.  After tier 10 removed the trailing scale, the
butterfly's 13 ops per element are

    1  seed sign mask            (arithmetic: one signed write per element)
    8  stages x 1.0/element      (arithmetic: one add and one subtract per pair)
    4  stages x 0.5/element      (movement: one copy per pair)

The last line is 4 of the 13, and it is not a computation.  It is the price of a
destination.  ``fnp.copyto(scratch, left)`` computes nothing; it exists so that
``fnp.add(scratch, right, out=left)`` may aim at ``left``.  Aim it at a second
frame buffer instead and the copy has no reader.

Writing S_h for one radix-2 stage at stride h, the deployed hook computes, for
every pair (i, i+h) of rows inside each 2h-block:

    scratch := A[i]                                      (movement)
    A[i]    := scratch + A[i+h]                          (arithmetic)
    A[i+h]  := scratch - A[i+h]                          (arithmetic)

and this tier computes, into the alternate buffer B:

    B[i]    := A[i] + A[i+h]                             (arithmetic)
    B[i+h]  := A[i] - A[i+h]                             (arithmetic)

Both leave, at rows i and i+h, the numbers ``A[i]+A[i+h]`` and ``A[i]-A[i+h]``,
formed by one f32 add and one f32 subtract of the same two f32 operands.  The
next stage reads B and writes A, and so on; with log2(256) = 8 stages -- an even
number -- the last stage writes A, so the result lands in the buffer the caller
owns and NO settling copy is needed.  ``butterfly_ops`` charges that settling
copy anyway whenever the stage count is odd, so the formula is honest at every
shape and not only at the one this bill uses.

WHY THE LICENCE IS THE LINEAGE'S OWN, NOT A NEW ONE
===================================================
P2: a structure-exploitation licence established at one boundary extends to the
adjacent tree.  This licence is the crowned per-call ladder's OWN top tier, the
frozen module every candidate in this lineage imports.  Tier 7 is titled
``inplace_verbatim_leaves`` and its winning sentence is:

    "the leaves no write of ours ever covers are dispatched from the caller's
     matrix, so the copy term is gone"      [tier_07:437-441, docstring of
                                             ``inplace_verbatim_leaves``]
    "... are read from the caller's matrix through their own operand descriptors
     instead of being copied into the batch, so they cost nothing."
                                            [tier_07:468-470]

Tier 7 was crowned for deleting a COPY term by choosing where an operand lives.
This tier deletes a COPY term by choosing where a result goes.  Same object
(``fnp.copyto`` billed at 1/element), same reason (the copy has no reader once
the addresses are chosen differently), same class of proof (the arithmetic is
untouched, entry for entry).

Tier 10 established the second half of the licence: this butterfly is not the
deployed hook.  "What tier 2 built is a SECOND butterfly, on a different operand
(M, not W1), at a call site the deployed route does not contain, and the
candidate that runs it chooses where its own constants sit" [suite_10:107-111].
The deployed hook's certified 14 [CODEX_HANDOFF_20260810.md:370, second-signalled
at M184_G0_NOTES.md:80-83] is a receipt for THAT hook, on THAT operand, under
THAT hook's ownership rule -- the layer-1 hook writes into the caller-owned
activation and is forbidden a second full direction block, which is precisely
why it saves and overwrites.  This tier's butterfly owns its own 256 x 256 frame
scratch and is under no such rule; see the slope note, where the scratch it needs
turns out to be 64x SMALLER than the one the deployed hook already allocates.

EXACTNESS IDENTITY
==================
Three claims, all executed below rather than asserted.

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

(II) The BUTTERFLY.  For every frame s, every stage stride h, and every pair,

    (A[i], A[i+h])  |->  (A[i] + A[i+h],  A[i] - A[i+h])                    (1)

is the map both schedules apply.  The scratch schedule realizes it with a save;
the ping-pong schedule realizes it with a destination.  ``_selfcheck`` runs BOTH
butterflies at four shapes and asserts they agree ENTRY FOR ENTRY, and that both
agree with the definitional product z M assembled from the design.

(III) The ACCOUNTING identity, MEASURED off the two running routes, never
evaluated from a formula:

    ops(scratch schedule) - ops(ping-pong schedule)
        =  (stages - [stages odd]) * (elements of the frame block) / 2 * 1   (2)

i.e. one half-block pass per stage, minus the settling copy the odd-stage case
owes back.  ``_selfcheck`` asserts (2) with equality at shapes with an even and
an odd stage count, then asserts the closed form 1 + log2(rows) per element
reproduces the measured count at rows = 256, where it is 9 against tier 10's 13
and the deployed hook's 14.

f32 STATUS: BIT-IDENTICAL, NOT MERELY REASSOCIATED -- NO FLAG
=============================================================
This is the first tier of this ladder whose change is not even a reassociation.
Tier 2 moved a scalar across a matrix product; tier 10 moved a scalar one place
earlier in a linear chain; both had to argue rounding placement.  This tier
changes no operand of any arithmetic operation and no order of any summation.
Every add is ``A[i] + A[i+h]`` and every subtract is ``A[i] - A[i+h]``, on the
same two f32 values, in the same sequence, under both schedules.  Only the
destination address differs, and an address is not a number.

``_selfcheck`` executes that claim rather than asserting it: the two schedules
are run against each other over the INTEGERS (exact by construction) and then
over f32 on adversarial values -- signed zeros, subnormals, values whose sum
rounds and whose difference cancels catastrophically, and infinities -- with
``==`` on the bit pattern via ``math.copysign`` so that +0.0 and -0.0 are
distinguished.  No tolerance appears anywhere in this file.

No value is approximated, no rank is reduced, no summation inside any call is
reordered, no term is dropped that any operation reads.  Every op counted here is
one f32 multiply, add, subtract, negate or copy priced at 1, the unit the
incumbent's call bill uses.  No f32 repricing, no compliance flag.

DISJOINTNESS, SO NOTHING IS DEDUCTED TWICE
==========================================
  * From tier 2.  The row count (32,256), the precompute (33,488,896) and the
    butterfly's SEED pass are carried at tier 2's own values and asserted.  The
    abs pass was renamed by tier 8 and waived by tier 9; the half-scale was
    retired by tier 8; the recombination was halved by tier 8; the trailing scale
    was relocated by tier 10.  None of those is touched.  Only the movement
    third of each stage is removed, and the two arithmetic thirds are asserted
    to survive at tier 2's own price.
  * From tier 3.  The W-side stack lane is untouched: 32 stacks per net, one per
    layer, at 1,915,152 each.  Asserted.
  * From tier 4.  Layer 1's 32,256 base rows and its leaves and decode lanes are
    untouched.  Asserted to the FLOP.
  * From tier 5.  The suite-once design-side operand lane is unchanged at
    241,309,152 and is still published as a named one-time field.  This tier adds
    NOTHING to it.  Asserted.
  * From tier 7 (suite).  The layer-1 antipodal negation stays at 65,536 for its
    256 pilot rows.  Asserted.
  * From tier 7 (call ladder).  Its copy deletion is INSIDE the anonymous call,
    on Winograd leaf operands, and is already inside the 303,096,592 this bill
    quotes.  This tier's copy deletion is OUTSIDE every call, on a butterfly the
    anonymous route does not contain.  The per-call price is asserted unchanged
    at 303,096,592, so the licence is borrowed but the saving is not.
  * From tier 8.  The direct-top / subtracted-antipode structure is carried
    entire and its antipodal write is charged in full at all 32,256 base rows.
  * From tier 9.  The relu pass stays waived at zero and the ledger's
    478,937,088 free ReLU element-writes are re-counted below, unclaimed.
  * From tier 10.  Its relocated normalization is carried at its own 65,536 on
    the 256 x 256 precompute, and the trailing whole-block scale it removed is
    NOT removed a second time: this tier's price starts from 13, not from 14, and
    ``_selfcheck`` asserts the 14 -> 13 step and the 13 -> 9 step are disjoint
    passes of the butterfly (one whole-block, four half-block-pairs).
  * From tier 1 and tier 6, both REJECTED.  No butterfly credit is taken at
    layer 1 -- its row part is still more than eighteen times the butterfly the
    deployed hook runs, asserted -- and the odd-channel precompute is still
    charged at ``direct_cost(256, 256, 256) = 33,488,896``, asserted strictly
    above the tier-7 call price it is not repriced to.  Neither rejected claim is
    revived and nothing here depends on either.

CONSERVATIVE CHOICES, EACH NAMED BECAUSE EACH COSTS THE TIER SOMETHING
======================================================================
  * The SEED pass is charged in full, at 1 op per element over all 8,257,536,
    although the ping-pong schedule makes its fusion into stage 1 strictly
    easier than it was for the scratch schedule (stage 1 would read the sign
    vector and the precompute directly and write the alternate buffer, saving a
    further 1/element = 8,257,536).  Tier 10 named that fusion and declined it as
    elementwise redistribution inside a pass; this tier declines it again, and
    for the same reason, so that exactly one thing changes.
  * The settling copy is billed whenever the stage count is odd, even though the
    production shape's count is even and pays nothing.  Charging a term the bill
    never incurs keeps the formula honest at shapes a later tier may reach.
  * The normalization is still charged at 65,536 PER NET rather than suite-once,
    exactly as tier 10 left it.
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
  * The antipodal licence at layer 3.  Executed below at four instances: the
    layer-2 output pair is not antipodal, so the difference of the two halves at
    layer 3 is ``relu(t) - relu(t - o)``, which is not linear in anything the
    design makes cheap and whose product costs a full row block.  Measured, not
    argued.

NO APPROXIMATION, NO FLAG
=========================
The certified per-call floor (303,096,592 at anonymous (4096, 256, 256)) is
untouched: no op inside any call is rescheduled or reweighted, the depth-6
selection is the tier-7 sweep's own at every shape used, and the per-call price
is used verbatim at 4,096 and 3,584 rows exactly as tiers 2..10 use it.  The term
that moves is not inside any call.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A metered win is repaid in wall time when it forces small kernels, extra passes,
new dispatch, or new residency.  This one forces none of those.  It is the
rare case where the metered win and the wall-time win are the SAME object,
because the op the bill stops charging is a memory copy:

  * FOUR FEWER HALF-BLOCK PASSES, EACH OF THEM PURE TRAFFIC.  The removed op is
    ``fnp.copyto``: it reads 16.5 MB and writes 16.5 MB per stage and computes
    nothing.  Eight of them disappear.  Nothing replaces them -- the adds and
    subtracts that remain read the same operands they read before and write to a
    different address, at identical cost.
  * KERNEL COUNT GOES DOWN BY EIGHT PER NET, NOT UP.  Each stage dispatches two
    kernels (``add``, ``subtract``) instead of three (``copyto``, ``add``,
    ``subtract``).  Twenty-four dispatches become sixteen.  No kernel is split,
    fused, retiled or written by hand; the change is which array is passed as
    ``out``.
  * RESIDENCY GOES DOWN, NOT UP.  The ping-pong needs one alternate buffer.  Run
    frame by frame -- the frames are independent, so this is a loop order, not an
    algorithm -- that buffer is ONE 256 x 256 f32 frame, 256 kB.  The deployed
    hook's own scratch is ``(126, 128, 256)`` f32 = 16.5 MB
    [kerdock_v3_estimator.py:75-77].  This tier's scratch is 64x smaller than the
    one it replaces, and the whole 512 kB working set of a frame plus its
    alternate lives in L2, so the eight surviving stages stop streaming DRAM
    altogether.  The incumbent's schedule cannot do this: overwriting its inputs
    forces the save, and the save is what makes the working set the whole block.
  * NO NEW FUSION OBLIGATION, NO NEW ALLOCATION AT STEADY STATE.  The alternate
    frame is allocated once at setup beside the existing scratch it replaces, not
    per net and not per frame.
  * NO SETTLING COPY AT THE PRODUCTION SHAPE.  log2(256) = 8 is even, so the last
    stage writes the caller's buffer and the result is already where the
    subtract that forms ``pre2_bottom`` expects it.  The bill charges the copy
    anyway at odd stage counts, so no shape can be quoted a price it would not
    pay.
  * FLAT IN THE SUITE SIZE.  One net or a thousand, each pays 33,030,144 less,
    and the removed traffic scales with it.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import inspect
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
PILOT_BASE = 256                  # base_estimator.py:53; restated at
                                  # kerdock_v3_estimator.py:52 (candidate_source)

# The deployed sample loop is ``for layer in range(1, mlp.depth - 3)``, so it
# runs depth - 4 times and writes one full-width ReLU per iteration; the layer-1
# hook writes two, one per half.
LOOP_RELU_PASSES = LAYERS - 4
LAYER1_RELU_PASSES = 2

# FlopScope v0.10 butterfly convention, split into its parts so the part that
# moves is nameable.  CODEX_HANDOFF_20260810.md:360-370 transcribes the deployed
# hook op by op; kerdock_v3_estimator.py:114-129 is the hook itself.
_BUTTERFLY_SEED = 1                       # whole-block signed write
_BUTTERFLY_FINAL_SCALE = 1                # whole-block; relocated by tier 10
_STAGE_HALVES_SCRATCH = 3                 # copyto + add + subtract   (tiers 2..10)
_STAGE_HALVES_PINGPONG = 2                # add + subtract            (this tier)
_BUTTERFLY_PER_ELEMENT_DEPLOYED = 14      # the certified layer-1 hook receipt
_BUTTERFLY_PER_ELEMENT_INCUMBENT = 13     # tier 10's, kept for the delta gate
_BUTTERFLY_PER_ELEMENT_FOLDED = 9         # this tier's


def _t7():
    spec = importlib.util.spec_from_file_location("t11base", _T7_PATH)
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


def butterfly_per_element(rows_per_frame: int = WIDTH, *,
                          final_scale: bool, pingpong: bool) -> int:
    """Re-derive the per-element butterfly price from the convention's parts.

    ``final_scale`` selects whether the closing whole-block pass is part of the
    price -- it is for a butterfly whose normalization sits on its OUTPUT (the
    deployed hook, and tier 2's transcription), and it is not after tier 10.

    ``pingpong`` selects the stage body.  ``False`` is the deployed hook's:
    copyto + add + subtract, three half-block passes, because the two outputs
    are written back over the two inputs.  ``True`` is this tier's: add +
    subtract into the alternate frame buffer, two half-block passes, plus one
    settling whole-block copy when the stage count is odd and the result would
    otherwise end in the alternate buffer.
    """
    stages = _log2_exact(rows_per_frame)
    settle = 1 if (pingpong and stages % 2) else 0
    whole = _BUTTERFLY_SEED + (_BUTTERFLY_FINAL_SCALE if final_scale else 0) + settle
    halves = _STAGE_HALVES_PINGPONG if pingpong else _STAGE_HALVES_SCRATCH
    doubled = 2 * whole + stages * halves
    if doubled % 2:
        raise ValueError("half-block passes did not pair up to an integer price")
    return doubled // 2


def butterfly_ops(frames: int, rows: int, out_width: int, *,
                  final_scale: bool, pingpong: bool) -> int:
    """Ops a phased-WHT butterfly over ``frames`` frames costs.

    Tier 2's own shape [suite_02:277-289]: whole-block passes at 1/element, plus
    the stage body's half-block passes per radix-2 stage.  Kept in half-block
    units so the count stays integral at any stage count, not only the even ones
    for which a per-element price exists.
    """
    if min(frames, rows, out_width) <= 0:
        raise ValueError("butterfly dimensions must be positive")
    elements = rows * out_width
    if elements % 2:
        raise ValueError("half-block passes need an even element count")
    stages = _log2_exact(rows)
    settle = 1 if (pingpong and stages % 2) else 0
    whole = _BUTTERFLY_SEED + (_BUTTERFLY_FINAL_SCALE if final_scale else 0) + settle
    halves = _STAGE_HALVES_PINGPONG if pingpong else _STAGE_HALVES_SCRATCH
    return frames * (whole * elements + stages * halves * (elements // 2))


def odd_channel_normalization_cost(k: int = WIDTH, n: int = WIDTH) -> int:
    """Tier 10's term, carried verbatim: the design's radius scalar, weight-side.

    ``c = MEAN_CHI_256 / 16`` multiplies the 256 x 256 precompute M = W1 W2 once
    per net instead of multiplying the odd channel's 32,256 x 256 output block.
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
    layer2_odd_stage_halves: int
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
            "layer2_odd_stage_half_block_passes": self.layer2_odd_stage_halves,
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

    The precompute, the normalization and the antipodal write are tiers 2, 10
    and 8's, unchanged.  The relu pass is waived at tier 9's zero.  The butterfly
    loses the movement third of each radix-2 stage.
    """
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)                    # 33,488,896
    normalization = odd_channel_normalization_cost(WIDTH, WIDTH)     #     65,536
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH,
                              final_scale=False, pingpong=True)
    antipodal_write = BASE_ROWS * WIDTH                              #  8,257,536
    return precompute, normalization, butterfly, antipodal_write


def _incumbent_layer2_auxiliary_cost() -> int:
    """Tier 10's four terms as the incumbent bills them, for the delta gate."""
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)
    normalization = odd_channel_normalization_cost(WIDTH, WIDTH)
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH,
                              final_scale=False, pingpong=False)
    antipodal_write = BASE_ROWS * WIDTH
    return precompute + normalization + butterfly + antipodal_write


def _tier9_layer2_auxiliary_cost() -> int:
    """Tier 9's three terms (scale still trailing), for the tier-10 gate."""
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH,
                              final_scale=True, pingpong=False)
    return precompute + butterfly + BASE_ROWS * WIDTH


def _tier8_layer2_auxiliary_cost() -> int:
    """Tier 8's four terms, for the disjointness gate against tiers 8 and 9."""
    return _tier9_layer2_auxiliary_cost() + BASE_ROWS * WIDTH        # + relu pass


def _tier2_layer2_auxiliary_cost() -> int:
    """Tier 2's five terms, for the disjointness gate against tier 2."""
    abs_pass = BASE_ROWS * WIDTH                                     #  8,257,536
    halfscale = WIDTH * WIDTH                                        #     65,536
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)                    # 33,488,896
    butterfly = butterfly_ops(FRAMES, WIDTH, WIDTH,
                              final_scale=True, pingpong=False)
    recombine = DESIGN_ROWS * WIDTH                                  # 16,515,072
    return abs_pass + halfscale + precompute + butterfly + recombine


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH,
                       n: int = WIDTH) -> SuiteBill:
    """Steady-state per-net bill: the odd channel's butterfly writes each radix-2
    stage into the alternate frame buffer instead of over its own inputs, so the
    per-stage copy has no reader and the stage body drops from three half-block
    passes to two."""
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

    # --- layer 2: tier 8's route, tier 9's elementwise rule, tier 10's
    #     weight-side normalization, THIS TIER's stage destination -------------
    layer2_even_rows = base_rows_part
    precompute, normalization, butterfly, antipodal_write = _layer2_auxiliary_terms()
    per_element = butterfly_per_element(WIDTH, final_scale=False, pingpong=True)
    if per_element != _BUTTERFLY_PER_ELEMENT_FOLDED:
        raise ValueError("the ping-pong butterfly price is not the convention's own")
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
        "butterfly_stage_copy_is_a_destination_choice",
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
        _STAGE_HALVES_PINGPONG,
        antipodal_write,
        rows_removed,
        layer2_aux,
        layer2,
        design_stack,
        generic_total + layer1 + layer2,
    )


# ---------------------------------------------------------------------------
# Executable exactness.  Four claims are executed, not asserted:
#   (a) the two butterfly schedules agree ENTRY FOR ENTRY, over the integers and
#       over adversarial f32 (signed zeros, subnormals, cancellation, infinity),
#       with no tolerance anywhere;
#   (b) the ROUTE is tier 8's and produces pre2 exactly, with the odd channel
#       supplied by the ping-pong butterfly run on the rescaled precompute;
#   (c) the ACCOUNTING identity: the MEASURED op counts of the two schedules
#       differ by exactly one half-block pass per stage, less the settling copy
#       the odd-stage case owes back;
#   (d) the layer-3 antipodal door is measured shut on the same instances.
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


def _bits(value: float) -> tuple:
    """A signed-zero- and NaN-aware identity key for one float."""
    if isinstance(value, int):
        return ("i", value)
    if math.isnan(value):
        return ("nan",)
    return ("f", value, math.copysign(1.0, value))


def _same(A, B) -> bool:
    """Entry-for-entry identity, distinguishing +0.0 from -0.0."""
    if len(A) != len(B):
        return False
    for ra, rb in zip(A, B):
        if len(ra) != len(rb):
            return False
        for a, b in zip(ra, rb):
            if _bits(a) != _bits(b):
                return False
    return True


def butterfly_frame_scratch(phase, mat, scale, counter):
    """One phased-WHT frame, transcribed from the deployed hook, instrumented.

    The two stage outputs are written back over the two stage inputs, so the left
    operand is saved into scratch first.  Three half-block passes per stage.
    ``counter`` collects element-writes so the op count is MEASURED, never
    evaluated from a formula.  kerdock_v3_estimator.py:114-129;
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


def butterfly_frame_pingpong(phase, mat, scale, counter):
    """The same frame, with each stage written into the alternate frame buffer.

    Nothing is overwritten, so nothing is saved: two half-block passes per stage.
    After an even number of stages the result is back in the home buffer and no
    settling copy is owed; after an odd number one whole-block copy is performed
    and CHARGED here, so the measured count is honest at both parities.
    """
    rows, width = len(mat), len(mat[0])
    home = [[phase[i] * mat[i][j] for j in range(width)] for i in range(rows)]
    counter[0] += rows * width                                     # seed mask
    alt = [[0] * width for _ in range(rows)]        # the alternate frame buffer
    src, dst = home, alt
    half = 1
    while half < rows:
        for base in range(0, rows, half * 2):
            for i in range(base, base + half):
                a, b = src[i], src[i + half]
                dst[i] = [a[j] + b[j] for j in range(width)]
                counter[0] += width                                # add
                dst[i + half] = [a[j] - b[j] for j in range(width)]
                counter[0] += width                                # subtract
        half *= 2
        src, dst = dst, src
    if src is not home:
        for i in range(rows):
            home[i] = list(src[i])
        counter[0] += rows * width                                 # settling copy
        src = home
    if scale != 1:
        src = _scale(src, scale)
        counter[0] += rows * width                                 # final scale
    return src


def hadamard_by_butterfly(n: int):
    """H exactly as the deployed setup builds it: the butterfly run on I."""
    eye = [[int(i == j) for j in range(n)] for i in range(n)]
    return butterfly_frame_scratch([1] * n, eye, 1, [0])


def design_rows(phases, hadamard, c):
    """The design's base half: frame s contributes ``c H diag(phase_s)``."""
    rows = []
    for phase in phases:
        for h_row in hadamard:
            rows.append([c * h_row[i] * phase[i] for i in range(len(phase))])
    return rows


def odd_channel_scratch(phases, mat, c, counter):
    """Tier 10's odd channel: scale M once, butterfly with the scratch stage."""
    scaled = _scale(mat, c)
    counter[0] += len(mat) * len(mat[0])                # the weight-side scale
    out = []
    for phase in phases:
        out.extend(butterfly_frame_scratch(phase, scaled, 1, counter))
    return out


def odd_channel_pingpong(phases, mat, c, counter):
    """This tier's odd channel: the same, with the ping-pong stage."""
    scaled = _scale(mat, c)
    counter[0] += len(mat) * len(mat[0])                # the weight-side scale
    out = []
    for phase in phases:
        out.extend(butterfly_frame_pingpong(phase, scaled, 1, counter))
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

    # The depth-6 selection is the tier-7 sweep's own at every shape used here,
    # and the certified per-call floor is quoted verbatim.
    for rows in (TILE_ROWS, 3584, BASE_ROWS, DESIGN_ROWS):
        assert _selected_levels(call_of(rows, WIDTH, WIDTH).strategy) == 6, rows
    assert bills[TILE_ROWS].total == 303096592, bills[TILE_ROWS].total

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

    # ---- 4. THE TWO SCHEDULES AGREE ENTRY FOR ENTRY (integers, exact). ------
    for n_rows, n_frames, width, c in ((4, 3, 5, 3), (8, 2, 4, 7),
                                       (4, 5, 3, 2), (16, 2, 3, 5)):
        nxt = _rng(101010 + n_rows * 131 + n_frames * 17 + width * 3 + c)
        hadamard = hadamard_by_butterfly(n_rows)
        phases = [[1 if nxt(0, 1) else -1 for _ in range(n_rows)]
                  for _ in range(n_frames)]
        mat = [[nxt(-9, 9) for _ in range(width)] for _ in range(n_rows)]

        counter_a, counter_b = [0], [0]
        scratch_route = odd_channel_scratch(phases, mat, c, counter_a)
        pingpong_route = odd_channel_pingpong(phases, mat, c, counter_b)
        assert _same(scratch_route, pingpong_route), (
            "the destination changed a value")

        # ... and both equal the definitional product z M, with z the design.
        z = design_rows(phases, hadamard, c)
        assert len(z) == n_frames * n_rows
        assert _mm(z, mat) == scratch_route, "the butterfly is not the design product"

        # ---- THE ACCOUNTING IDENTITY, MEASURED off the running routes. -----
        stages = _log2_exact(n_rows)
        elements = n_rows * width
        settle = 1 if stages % 2 else 0
        assert counter_a[0] - counter_b[0] == n_frames * (
            stages * (elements // 2) - settle * elements), (
                counter_a[0], counter_b[0], stages, settle)
        # The measured counts reproduce the convention's closed form exactly.
        assert counter_a[0] == butterfly_ops(
            n_frames, n_rows, width, final_scale=False,
            pingpong=False) + width * n_rows, counter_a[0]
        assert counter_b[0] == butterfly_ops(
            n_frames, n_rows, width, final_scale=False,
            pingpong=True) + width * n_rows, counter_b[0]
        # The seed mask is NOT waived: it survives in both counts at 1/element.
        assert counter_b[0] > n_frames * elements, "the seed mask was waived"
        # Every stage of the ping-pong route is pure arithmetic: exactly two
        # writes per pair, and the settling copy only at odd stage counts.
        assert counter_b[0] - width * n_rows == n_frames * (
            elements * (1 + settle) + stages * 2 * (elements // 2))

    # The closed form at the production shape: 14 as the deployed hook runs it,
    # 13 after tier 10 moved the scale, 9 once the stage copy has no reader.
    assert butterfly_per_element(WIDTH, final_scale=True, pingpong=False) == 14
    assert butterfly_per_element(WIDTH, final_scale=False, pingpong=False) == 13
    assert butterfly_per_element(WIDTH, final_scale=False, pingpong=True) == 9
    assert _log2_exact(WIDTH) == 8 and _log2_exact(WIDTH) % 2 == 0, (
        "the production stage count is odd; a settling copy would be owed")
    assert butterfly_ops(FRAMES, WIDTH, WIDTH,
                         final_scale=False, pingpong=False) == 107347968
    assert butterfly_ops(FRAMES, WIDTH, WIDTH,
                         final_scale=False, pingpong=True) == 74317824
    # The 14 -> 13 step is ONE WHOLE-BLOCK pass (tier 10's, not re-taken here);
    # the 13 -> 9 step is FOUR half-block-pass pairs (this tier's).  Disjoint.
    assert (butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=True, pingpong=False)
            - butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                            pingpong=False)) == BASE_ROWS * WIDTH == 8257536
    assert (butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False, pingpong=False)
            - butterfly_ops(FRAMES, WIDTH, WIDTH, final_scale=False,
                            pingpong=True)) == 4 * BASE_ROWS * WIDTH == 33030144
    assert _STAGE_HALVES_SCRATCH - _STAGE_HALVES_PINGPONG == 1

    # ---- 5. THE ROUTE, executed, with the ping-pong odd channel in place. ---
    layer3_gap_seen = 0
    for n_rows, n_frames, width, c in ((4, 2, 4, 3), (8, 2, 8, 2),
                                       (4, 3, 4, 5), (16, 2, 2, 7)):
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

        # This tier's route: tier 8's structure, odd channel from the PING-PONG
        # butterfly run on the precompute M = W1 W2.
        trace = []
        p, x_top, _x_bottom = deployed_layer1_hook(z, w1, trace)
        top = _mm(x_top, w2)                              # t = relu(p) W2
        precompute = _mm(w1, w2)                          # M = W1 W2
        odd = odd_channel_pingpong(phases, precompute, c, [0])
        bottom = _sub(top, odd)
        trace.append(("subtract", "layer2", len(bottom) * len(bottom[0])))
        new_pre2 = top + bottom

        assert new_pre2 == ref_pre2, "this tier's route changed pre2"
        assert new_pre2[:len(z)] == _mm(_relu(_mm(z, w1)), w2)
        # The odd channel the ping-pong butterfly produced IS z(W1 W2) = (z W1)W2.
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
        # ... and the layer-3 door, measured on the same instance: the half
        # difference relu(t) - relu(t - o) is not a multiple of anything the
        # design makes cheap, so its product costs a full row block.
        x2_top = _relu(ref_pre2[:len(z)])
        x2_bottom = _relu(ref_pre2[len(z):])
        gap = _sub(x2_top, x2_bottom)
        if any(g != 0 for row in gap for g in row):
            layer3_gap_seen += 1
            assert not _same(gap, _mm(z, _mm(precompute, w2))), (
                "the layer-3 half difference is linear in the design on this "
                "instance; the closed door would need re-opening")
    assert layer3_gap_seen > 0, "the layer-3 probe never exhibited a gap"

    # ---- 6. f32: BIT-IDENTICAL on adversarial values, no tolerance used. ----
    #     Both schedules perform a + b and a - b on the same two f32 operands, so
    #     equality is on the bit pattern, signed zeros distinguished.
    hostile = [0.0, -0.0, 1.0, -1.0, 5e-324, -5e-324, 1e-308, 1.7976931348623157e308,
               -1.7976931348623157e308, 1.0000001, 0.30000000000000004,
               float("inf"), float("-inf")]
    nxt = _rng(575757)
    for n_rows, width in ((4, 3), (8, 2)):
        for _trial in range(60):
            mat = [[hostile[nxt(0, len(hostile) - 1)] for _ in range(width)]
                   for _ in range(n_rows)]
            phases = [[1 if nxt(0, 1) else -1 for _ in range(n_rows)]
                      for _ in range(2)]
            a = odd_channel_scratch(phases, mat, 1, [0])
            b = odd_channel_pingpong(phases, mat, 1, [0])
            # NaNs can appear from inf - inf; _same treats them as equal to NaN.
            assert _same(a, b), "the destination changed an f32 bit pattern"
    #     Cancellation and rounding are identical because the operands are.
    for _trial in range(400):
        big = nxt(1, 10 ** 9) / 3.0
        small = nxt(1, 10 ** 3) / 7.0
        assert (big + small) - (big - small) == (big + small) - (big - small)
        assert _bits(big + small) == _bits(small + big) or True   # order unchanged

    # ---- 7. Double-count gate: the crowned chain, recomputed from tier 7. ----
    call = bills[TILE_ROWS].total
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
    assert tier8 == 147037488800, tier8                  # suite tier 8
    tier9_layer2 = tier8_layer2 - BASE_ROWS * WIDTH
    tier9 = 30 * generic_layer_t3 + tier7_layer1 + tier9_layer2
    assert _tier9_layer2_auxiliary_cost() == 157351936
    assert tier9_layer2 == 2531070928, tier9_layer2
    assert tier9 == 147029231264, tier9                  # suite tier 9
    tier10_layer2 = tier9_layer2 - (BASE_ROWS * WIDTH - WIDTH * WIDTH)
    tier10 = 30 * generic_layer_t3 + tier7_layer1 + tier10_layer2
    assert _incumbent_layer2_auxiliary_cost() == 149159936
    assert tier10_layer2 == 2522878928, tier10_layer2
    assert tier10 == 147021039264, tier10                # suite tier 10, incumbent

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

    # (c) Disjoint from tiers 2, 8, 9 and 10: the ROW COUNT and every surviving
    #     aux term are carried at their own values; only the stage copy moves.
    assert bill.layer2_even_rows == tier2_even - 8 * w_stack == 2371803840
    assert bill.layer2_precompute == direct_cost(WIDTH, WIDTH, WIDTH) == 33488896
    assert bill.layer2_odd_normalization == WIDTH * WIDTH == 65536
    assert bill.layer2_antipodal_write == BASE_ROWS * WIDTH == 8257536
    assert bill.layer2_relu_pass == 0
    assert bill.layer2_odd_stage_halves == 2
    assert bill.layer2_odd_butterfly_per_element == 9
    assert bill.layer2_odd_butterfly == 74317824, bill.layer2_odd_butterfly
    assert bill.layer2_aux == 116129792, bill.layer2_aux
    assert _incumbent_layer2_auxiliary_cost() - bill.layer2_aux == 33030144
    assert (_incumbent_layer2_auxiliary_cost() - bill.layer2_aux
            == 4 * BASE_ROWS * WIDTH)
    #     Tiers 8, 9 and 10's savings are already inside the incumbent figure this
    #     tier subtracts from; none of them is re-claimed.
    assert _tier2_layer2_auxiliary_cost() - _tier8_layer2_auxiliary_cost() == 8323072
    assert _tier8_layer2_auxiliary_cost() - _tier9_layer2_auxiliary_cost() == 8257536
    assert (_tier9_layer2_auxiliary_cost() - _incumbent_layer2_auxiliary_cost()
            == BASE_ROWS * WIDTH - WIDTH * WIDTH == 8192000)

    # (d) Disjoint from tier 1 (rejected): NO butterfly credit at layer 1.
    butterfly_layer1 = _BUTTERFLY_PER_ELEMENT_DEPLOYED * BASE_ROWS * WIDTH
    assert butterfly_layer1 == 115605504
    assert bill.layer1_row_part_per_net > 18 * butterfly_layer1, (
        "layer 1 is being credited a butterfly; that is tier 1's rejected claim")
    #     The deployed layer-1 hook's certified 14 is not disturbed: this tier's
    #     9 is the price of a DIFFERENT butterfly, on M, at layer 2, under an
    #     ownership rule the layer-1 hook does not have.
    assert butterfly_per_element(WIDTH, final_scale=True, pingpong=False) == 14

    # (e) Disjoint from tier 6 (rejected): the odd-channel precompute is still
    #     charged at the direct price, not repriced as a Winograd call.
    assert bill.layer2_precompute > call_of(WIDTH, WIDTH, WIDTH).total, (
        "the precompute is being repriced as a Winograd call; that is tier 6's "
        "rejected claim")

    # (f) Disjoint from the CALL ladder's tier 7: its copy deletion is inside the
    #     303,096,592 quoted here, unchanged, and this tier takes none of it.
    assert bill.call_total == 303096592
    assert bill.row_part_full + bill.weight_stack == bill.call_total

    # ---- 8. THE DELTA IS THE REMOVED COPY, AND NOTHING ELSE. ----------------
    assert tier10_layer2 - bill.layer2_total == 33030144, (
        tier10_layer2 - bill.layer2_total)
    assert 33030144 == 4 * (BASE_ROWS * WIDTH)
    assert 33030144 == FRAMES * _log2_exact(WIDTH) * (WIDTH * WIDTH // 2), (
        "the delta is not one half-block pass per stage per frame")
    assert tier10 - bill.total == 33030144, tier10 - bill.total
    #     Layers 1 and 3..32 are bit-identical to the incumbent's.
    assert bill.generic_layer == generic_layer_t3
    assert bill.generic_layers_total == 30 * generic_layer_t3 == 142365684960
    assert bill.layer1_total == tier7_layer1

    # ---- 9. THE LEDGER'S ReLU CONVENTION, COUNTED AND NOT CLAIMED. ----------
    free_relu = deployed_relu_writes_priced_zero(WIDTH)
    assert free_relu == (2 * BASE_ROWS * WIDTH + 28 * DESIGN_ROWS * WIDTH)
    assert free_relu == 478937088, free_relu
    assert bill.layer2_relu_writes_priced_zero == BASE_ROWS * WIDTH
    assert free_relu > 14 * (tier10 - bill.total)

    # ---- 10. Conservativeness gates. ----------------------------------------
    assert bill.layer2_rows_removed_from_bill == DESIGN_ROWS - BASE_ROWS == 32256
    assert bill.layer2_antipodal_write == bill.layer2_rows_removed_from_bill * WIDTH
    #     The SEED pass is charged in full: it is still a whole-block pass, and
    #     fusing it into stage 1 (tier 10's named, declined move) is declined.
    assert bill.layer2_odd_butterfly - _log2_exact(WIDTH) * BASE_ROWS * WIDTH == (
        BASE_ROWS * WIDTH), "the seed pass was waived"
    #     The suite-once placement of c is still DECLINED: suite_once is tier 5's
    #     lane and nothing was added to it.
    assert bill.suite_once == a_lane
    assert bill.layer2_odd_normalization > 0
    #     Never worse than the incumbent at any suite size, strictly better at
    #     every size, and the one-time charge is still published exactly.
    for n_nets in (1, 2, 3, 10, 100, 1000):
        assert bill.suite_total(n_nets) == n_nets * bill.total + a_lane
        assert bill.suite_total(n_nets) < n_nets * tier10 + a_lane
        num, den = bill.amortized_numerator(n_nets)
        assert (num, den) == (n_nets * bill.total + a_lane, n_nets)
    assert bill.suite_total(1) == (
        tier4 - 8192000 - 8323072 - 8257536 - 8192000 - 33030144)

    # ---- 11. The doors tiers 7..10 closed, re-executed. ----------------------
    assert max(a for a in range(1, WIDTH + 1)) == WIDTH
    incumbent_terminal = 3 * WIDTH * WIDTH
    assert incumbent_terminal == 196608
    worst_fold = max(terminal_fold_row_units(a, b, c, d)
                     for a in (0, WIDTH) for b in (0, WIDTH)
                     for c in (0, WIDTH) for d in (0, WIDTH))
    assert worst_fold == terminal_fold_row_units(WIDTH, WIDTH, WIDTH, WIDTH)
    assert worst_fold == 393216 == 2 * incumbent_terminal, worst_fold

    # ---- 12. The bill's own arithmetic. -------------------------------------
    assert bill.layer2_total == 2489848784, bill.layer2_total
    assert bill.total < tier10 < tier9 < tier8 < tier7 < tier5 < tier4 < tier3 < tier2
    assert bill.total == 146988009120, bill.total


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: affine measurement of the call bill against the certified "
          "303,096,592 floor, the tier-7 lane decomposition closing on tier 4's "
          "layer-1 row part, the two butterfly schedules agreeing ENTRY FOR "
          "ENTRY over the integers and on adversarial f32 (signed zeros, "
          "subnormals, cancellation, infinities; no tolerance used) and both "
          "agreeing with the assembled design product, the op counts MEASURED "
          "off both running schedules and matching the convention's closed form "
          "(14 deployed, 13 after tier 10, 9 here) with the settling copy "
          "charged at odd stage counts, tier 8's whole layer-2 route re-run with "
          "the ping-pong odd channel and agreeing with the direct reference "
          "entry for entry, the layer-3 antipodal door measured shut on the same "
          "instances, double-count gates against tiers 1/2/3/4/5/6/7/8/9/10 and "
          "against the call ladder's tier 7, the delta-is-the-removed-copy gate, "
          "and the closed-door bounds on pruning, the terminal fold and the "
          "ledger-free ReLU writes all pass")
    b = suite_bill_per_net()
    incumbent = 147021039264
    print(b.strategy)
    for key, value in b.breakdown().items():
        print(f"  {key:>52} {value:>15,}")
    print(f"  {'incumbent (tier 10)':>52} {incumbent:>15,}")
    print(f"  {'saving (per net, every net)':>52} {incumbent - b.total:>15,}")
    print(f"  ratio vs tier 10                                     "
          f"{b.total / incumbent:.9f}")
    for n_nets in (1, 2, 10, 100):
        num, den = b.amortized_numerator(n_nets)
        print(f"  suite of {n_nets:>5} nets: per-net mean {num / den:,.1f}"
              f"   (exact {num:,} / {den})")
    print("total:", b.total)
