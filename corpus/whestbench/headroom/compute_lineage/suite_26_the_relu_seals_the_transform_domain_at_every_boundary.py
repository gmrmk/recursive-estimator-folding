"""Suite tier 26: DRY, and the ladder's completion.  The largest rung left in
the bill is the Winograd transform domain carried ACROSS a layer boundary --
42,222,237,120, or 29.15% of the whole -- and the ReLU seals it at every one of
the thirty boundaries.  The odd channel's level-1 alphabet cannot be folded into
the precompute's decode.  And the two IEEE identities this ladder refuses are
priced once, for the entire bill, at 589,824.

    suite bill, per net     144,867,083,088   ->   144,867,083,088   (unchanged)

Tiers 20 and 25 emptied the two axes their winners had opened: tier 20 the
design scalar's seat and the cross-frame sharing licence, tier 25 the
shared-operand axis.  Both searches ran along the terms tiers 10..19 had already
touched, which are the auxiliary terms of layers 1 and 2 -- 1.73% of the bill.
This tier turns the search the other way and asks the question the ladder has
never asked in one place: where is the largest saving the bill would show if a
rung were free?  It is not in the auxiliary terms at all.  It is in the 98.27%
that thirty generic layers carry, and it has one name.

    per generic layer, 64,512 rows      leaves      3,320,525,376
                                        A-side lane   482,618,304
                                        decode lane   940,464,000
                                        W-side lane     1,915,152
                                                     --------------
                                                    4,745,522,832

Two of those four lanes exist only to leave and re-enter the alternative basis.
A route that kept a layer's output in the basis its own recursion produced it in
and handed it to the next layer's leaves there would delete both, at every
boundary but the last.  P4: a door genuinely closed by a search is a paid
outcome, and this is the biggest door the ladder will ever close.

DOOR 4.  THE TRANSFORM DOMAIN CANNOT CROSS THE ReLU
===================================================
The rung is real, it is enormous, and it sits directly beneath four tiers of
this ladder's own teaching that operand arrays are built once and read many
times.  Priced from this bill's own terms, over the thirty boundaries
2 -> 3, ..., 31 -> 32:

    decode lanes,  layers  2..31        27,743,688,000
    A-side lanes,  layers  3..32        14,478,549,120
                                       ----------------
    maximal rung                        42,222,237,120   (291,455 ppm of .total)

and its cheapest form, in which only the change of basis is elided and the
arithmetic blocks of both lanes are still paid:

    inverse-Psi in the decodes,  2..31     730,791,936
    Psi in the A-side lanes,     3..32     743,178,240
                                          --------------
    basis-transform-only rung            1,473,970,176   (10,174 ppm)

Both are shut by one fact, and ``_selfcheck`` EXECUTES it rather than asserting
it: the layer boundary carries a ReLU, and

    Psi(relu(C))  !=  relu(Psi(C)),

run on integer matrices through the module's own ``_psi`` with the module's own
``PHI_A`` at two levels.  The transform mixes entries; the ReLU does not.

The stronger form is the one that actually shuts the door, because a tier
holding only the inequality above would try to repair it with a cheap
elementwise correction applied in the transformed domain.  No such correction
exists, and the counterexample is executed: the check searches this file's own
deterministic stream for a pair of matrices ``C1``, ``C2`` and a position
``(i, j)`` with

    Psi(C1)[i][j] == Psi(C2)[i][j]      but
    Psi(relu(C1))[i][j] != Psi(relu(C2))[i][j],

which is exactly the statement that ``Psi(relu(.))`` is not a function of
``Psi(.)`` entry by entry.  Any repair must therefore read more than one entry
per output, which is another operand lane -- the lane the rung was trying to
delete.  SHUT at every boundary, in both forms.

    THE ONE BOUNDARY THE LADDER DOES CROSS, AND WHY IT DOES NOT GENERALIZE.
    Tier 2 crosses a ReLU for free at layer 1 -> 2, and a later tier will read
    that as licence.  It is not.  Tier 2's identity is ``relu(-p) = relu(p) -
    p``, a statement about the ANTIPODAL PAIR ``[p ; -p]`` that layer 1's design
    produces -- not a statement that ReLU commutes with a linear map.  It is
    re-executed below beside the failure above so the two are never confused,
    and it is already banked: the bill charges 32,256 even-channel rows, not
    64,512.  Layers 3..32 have no antipodal pair to trade on; tier 20 closed
    that separately by exhibiting ``[t ; t - o]``.

    THE LAST DECODE IS NOT IN THE RUNG.  Layer 32's decode produces the network
    output and can never be elided, so the rung is thirty decodes and thirty
    encodes, not thirty-one of each.  Counted that way above.

DOOR 5.  THE ALPHABET CANNOT BE FOLDED INTO THE PRECOMPUTE'S DECODE
===================================================================
Tier 25 shut the seam on the matmul side -- pushing ``W1h`` past layer 1's
alphabet costs 2, 8 or 128 times as many rows.  The seam on the DECODE side is
the mirror image and was never adjudicated, and unlike tier 25's it is worth
something.

``cM`` has exactly one reader in the whole bill.  After tiers 12 and 13 the
per-frame stages start at stage 3 and read a level-2 array; the level-2 arrays
are built from the level-1 arrays; and the level-1 arrays are built from ``cM``.
Nothing else touches it.  So a decode that emitted the four level-1 arrays
directly, and never materialized ``cM`` at all, would be legal in exact
arithmetic -- and priced at the decode's own outermost write rate it is a
saving, not a loss:

    charged   outermost reconstruction level of the decode        114,688
              level-1 alphabet, 5 ops per pair of rows            163,840
                                                                 ---------
                                                                  278,528
    fused     the same 7 writes per unit area over the alphabet's
              131,072 elements instead of cM's 65,536             229,376

    exact-arithmetic delta                                        -49,152

It is refused, and not on a scruple.  The charged route forms
``P_t = fl(cM[2t] + cM[2t+1])`` from two rows each of which is itself the
rounded sum of the decode's contributions; the fused route forms ``P_t`` from
those contributions in a single interleaved sum.  That is a REASSOCIATION, and
this ladder's exactness law is bit-identity, not mathematical equality.
``_selfcheck`` executes the divergence in the ledger's own working precision:
with contributions ``2**24, 1`` and ``-2**24, 1`` the charged order yields
``1.0`` and the fused order yields ``2.0`` in f32.  A 100% relative error is not
a rounding difference.  SHUT.

    AND THE DECODE CANNOT BE SHRUNK INSTEAD.  The obvious weaker move -- decode
    only the part of ``cM`` the alphabet reads -- is empty: the alphabet reads
    every one of ``cM``'s entries, four times each.  ``_selfcheck`` MEASURES the
    coverage map rather than reading it off the formula: it perturbs each entry
    of a probe matrix in turn, re-runs ``level1_alphabet``, and counts the
    readable arrays that move.  Every entry moves exactly four.  SHUT.

DOOR 6.  THE WHOLE PRICE OF THE TWO REFUSED IEEE IDENTITIES, PAID ONCE
======================================================================
Tiers 12, 13 and 25 each name the two identities the ladder refuses -- ``(-a) +
(-b) == -(a + b)`` and ``-(a - b) == b - a`` -- and none of them prices what the
refusal costs.  A later tier will notice the redundancy on its own, because it
is visible in tier 12's own array list, and will spend a turn re-deriving it.
It is derived here, once, for the whole bill.

The four level-1 arrays are ``P = a + b``, ``Q = a - b``, ``R = -a + b``,
``S = -a - b``.  As VALUES ``S = -P`` and ``R = -Q``, so the set is closed under
negation, and two consequences follow immediately:

    level 1   S and R could be sign flips of P and Q: FOUR ops per pair
              instead of five                                     -32,768
    level 2   a difference of level-1 arrays is a sum with the negated one,
              which is already in the set, so SIXTEEN arrays per group of four
              serve instead of thirty-two                        -262,144
                                                                 ---------
              per butterfly                                       294,912
              two butterflies                                     589,824

Both are unavailable, for the same reason, and ``_selfcheck`` executes it: the
value identities hold over the integers, and fail over f32 at signed zero.  With
``a = 1.0, b = -1.0`` the bits of ``-(a + b)`` are ``00000080`` and the bits of
``(-a) + (-b)`` are ``00000000``; with ``a = b`` the bits of ``-(a - b)`` are
``00000080`` and of ``b - a`` are ``00000000``.  The arrays are not the same
arrays, so ``S`` is not a legal sign flip of ``P`` and a level-2 difference is
not a legal sum.  589,824, or 4 ppm of the bill, is the entire standing price of
the ladder's exactness law, it is confined to the two butterfly prologues, and
it is OFF THE BOARD.  Named with its number so no later tier spends a turn on
it.

WHAT THE COMPLETION LEAVES STANDING, AND WHERE
==============================================
  * THE SUITE-ONCE RESIDUE, 241,341,408.  The design-side operand stack has had
    no reader since tier 14 orphaned it (241,309,152) and one of the two frame
    descriptor tables is redundant (32,256, tier 25).  Both are inside
    ``suite_once`` and outside ``.total``, so NO per-net tier can score either.
    Re-asserted here as the ladder's terminal residue; a suite-once adjudication
    is the only thing that can take them.  NOT CLAIMED.
  * THE CERTIFIED PER-CALL FLOOR, 303,096,592, re-derived at the anonymous
    (4096, 256, 256): depth 6 is the strict argmin of the call, of the
    15.75-tile layer objective and of layer 2's 7.875-tile objective, and the
    all-alternative grading is confirmed the argmin of each of the three lanes
    by BRUTE FORCE over the whole 2**6 grading lattice, not by the module's
    marginal shortcut.  That is what makes the two lanes door 4 attacks a floor
    rather than a default.
  * TIER 25's THREE DOORS, re-executed from this file's own terms: the fused
    32,512-row call (delta 0), the alphabet carry (worse by 18,660,000 /
    131,078,752 / 2,389,939,552 at stages 1, 2, 3) and the fused terminal stage
    (delta 0).
  * THE TERMINAL FOLD, PRUNING AND THE LEDGER-FREE ReLU WRITES.  All three
    raise the bill if modelled honestly (the fold's honest worst case is six
    row-scaled units against three charged; the ReLU writes are 478,937,088
    priced at zero).  Counted, none claimed.

EXACTNESS IDENTITY
==================
This tier proposes no route change, so the route is IDENTICAL to tier 19's, tier
20's and tier 25's, term for term: every term below is computed by the same
function on the same arguments, and ``_selfcheck`` asserts term-by-term equality
against the published figures and ``.total == 144,867,083,088``.

What is executed here is the exactness of the routes that are NOT taken, since a
door closed on cost is only closed if the route behind it was legal, and a door
closed on arithmetic is only closed if the divergence is shown:

  (i)    ``Psi(relu(C)) != relu(Psi(C))`` on integer matrices, through the
         module's own ``_psi`` and ``PHI_A``, at two levels -- door 4;
  (ii)   the entrywise refutation: two matrices agreeing at a transformed entry
         and disagreeing at the same entry after the ReLU, which kills every
         zero-cost elementwise repair -- door 4;
  (iii)  ``relu(-p) W1h = relu(p) W1h - p W1h``, re-run so the one nonlinearity
         the ladder does cross is visibly a statement about the antipodal pair;
  (iv)   the alphabet's coverage of ``cM``, MEASURED by perturbing every entry
         and re-running ``level1_alphabet`` -- door 5;
  (v)    the f32 reassociation divergence, 1.0 against 2.0 -- door 5;
  (vi)   the value-level negation closure of the level-1 and level-2 alphabets
         over the integers, and its f32 signed-zero failure, bit pattern for bit
         pattern -- door 6;
  (vii)  the identities the charged route itself rests on, re-run so this file
         stands alone: the CReLU split, the design product ``O_s = H diag(d_s)
         cM`` against the dense product, and the scalar's associativity
         ``c (W0 W1h) = (c W0) W1h``;
  (viii) the block-row identity and the alphabet identity behind tier 25's two
         legal-but-unpaid rungs.

f32 STATUS: NO REPRICING, NO FLAG
=================================
No op is added, removed or repriced anywhere in the bill; the route that is
charged is byte-for-byte tier 19's.  Doors 5 and 6 are closed BY the f32 law
rather than despite it, and the divergences are executed rather than asserted --
which is the first time this ladder has measured what its own exactness law
costs.  The two IEEE identities the ladder permits (``a - b`` IS ``a + (-b)``;
negation IS a sign flip) are used only where tiers 12 and 13 already used them.

No f32 repricing, no compliance flag.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
A DRY tier has no metered win to repay, and its value is the wall time the next
tiers do not spend -- which is only real if the doors are shut in the shape as
well as on the ledger.  All three are, and door 4 is shut hardest of all.

  * THE TRANSFORM-DOMAIN CARRY is the one rung whose shape would have been
    BETTER than its ledger: it deletes two full passes over a 64,512 x 256
    activation per layer, halves the traffic at every boundary and shortens the
    critical path.  That is precisely why it is priced and killed in full here
    rather than left to be rediscovered: the arithmetic forbids it, and no
    amount of implementation cleverness reaches a route the ReLU does not
    permit.  Named with both its numbers -- 42,222,237,120 and 1,473,970,176 --
    so no later tier re-opens it hoping the shape will pay for the algebra.
  * THE ALPHABET-INTO-DECODE FOLD would also be mildly positive in the shape
    (one fewer pass over 65,536 elements, and ``cM`` never resident), and it is
    refused anyway, because a 100% relative error at f32 is not a shape
    question.  The ladder does not buy wall time with wrong numbers.
  * THE REFUSED IDENTITIES would each save one whole-block pass in a butterfly
    prologue and would be shape-positive too.  Same answer, same law, and now
    with a number attached so the refusal is auditable rather than tacit.
  * NOTHING MOVES.  The 126 frames, the 15.75 tiles, the 31 charged W-side
    stacks, the two butterflies, the one scaling pass and the single 256-row
    precompute are scheduled exactly as tier 19 schedules them.  Flat in the
    suite size: ``.total`` and ``suite_once`` are asserted at 144,867,083,088
    and 241,373,664, and ``suite_total(n) = n * .total + suite_once`` is
    re-derived at n = 1 and n = 7.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import struct
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
    spec = importlib.util.spec_from_file_location("t26base", _T7_PATH)
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
# DOOR 4.  Carrying the Winograd transform domain ACROSS a layer boundary.
# ---------------------------------------------------------------------------


def decode_lane(t7, m: int, n: int = WIDTH, levels: int | None = None) -> int:
    """The reconstruction lane of a call at the bill's depth.

    Tier 4's decode under tier 5's grading: six arithmetic blocks per node of
    the 7-ary tree plus the inverse basis transform.  This is one of the two
    lanes door 4 attacks, so it is defined once and used everywhere.
    """
    if levels is None:
        levels = layer_call_depth(t7, TILE_ROWS, WIDTH, n)
    cost, _grade = t7.best_decode_grade(m, n, levels)
    return cost


def a_side_lane(t7, m: int, k: int = WIDTH, levels: int | None = None) -> int:
    """The A-side operand lane of a call at the bill's depth.

    Tier 7's operand lane: three arithmetic blocks per node plus the basis
    transform, with the ``3 ** levels`` verbatim leaves dispatched in place and
    therefore free.  The other lane door 4 attacks.
    """
    if levels is None:
        levels = layer_call_depth(t7, TILE_ROWS, k, WIDTH)
    cost, _grade = t7.best_operand_grade(m, k, levels)
    return cost


def leaf_lane(t7, m: int, k: int = WIDTH, n: int = WIDTH,
              levels: int | None = None) -> int:
    """The ``7 ** levels`` leaf products of a call, so a layer's four lanes add
    up to the charged layer and the rung is visibly INSIDE the bill."""
    if levels is None:
        levels = layer_call_depth(t7, TILE_ROWS, k, n)
    block = 1 << levels
    if m % block or k % block or n % block:
        raise ValueError(f"{m}x{k}x{n} does not carry {levels} Winograd levels")
    return 7 ** levels * t7.direct_cost(m // block, k // block, n // block)


def basis_transform_lane(m: int, n: int, levels: int) -> int:
    """``psi_cost``: the change-of-basis part of ONE lane, tier 4's term.

    Transcribed rather than imported so the cheapest form of door 4 can be
    priced from this file alone; ``_selfcheck`` asserts it equals the module's
    own ``psi_cost`` at every shape used.
    """
    if levels < 1:
        raise ValueError("a graded lane needs at least one level")
    if m <= 0 or n <= 0:
        raise ValueError("a graded lane has positive dimensions")
    return sum(4 ** (j - 1) * (m >> j) * (n >> j)
               for j in range(1, levels + 1))


def boundary_transform_carry(t7) -> dict:
    """Price the largest rung left in the bill, in both of its forms.

    A layer's output leaves the alternative basis through its decode; the next
    layer's activation re-enters it through its A-side operand lane.  If the two
    could be elided -- if a layer's output could be handed to the next layer's
    leaves in the basis the recursion already produced it in -- the bill would
    lose both lanes at every boundary but the last.  The cheapest form elides
    only the two basis transforms and still pays every arithmetic block.

    Both are shut by the ReLU that sits on the boundary; this function prices
    them, ``_selfcheck`` kills them.
    """
    levels = layer_call_depth(t7, TILE_ROWS, WIDTH, WIDTH)
    boundaries = LAYERS - 2                    # 2 -> 3, ..., 31 -> 32
    if boundaries != 30:
        raise ValueError("the boundary count is not the frozen thirty")
    # Decodes that could go: layer 2's (32,256 rows) and layers 3..31's.
    decodes = (decode_lane(t7, BASE_ROWS)
               + (boundaries - 1) * decode_lane(t7, DESIGN_ROWS))
    # A-side lanes that could go: layers 3..32's.
    encodes = boundaries * a_side_lane(t7, DESIGN_ROWS)
    psi_decodes = (basis_transform_lane(BASE_ROWS, WIDTH, levels)
                   + (boundaries - 1)
                   * basis_transform_lane(DESIGN_ROWS, WIDTH, levels))
    psi_encodes = boundaries * basis_transform_lane(DESIGN_ROWS, WIDTH, levels)
    maximal = decodes + encodes
    minimal = psi_decodes + psi_encodes
    if minimal >= maximal:
        raise ValueError("the basis-transform form is not the cheaper rung")
    return {
        "boundaries": boundaries,
        "decode_lanes_layers_2_to_31": decodes,
        "a_side_lanes_layers_3_to_32": encodes,
        "maximal_rung": maximal,
        "maximal_rung_ppm_of_total": maximal * 1000000 // _INCUMBENT_TOTAL,
        "basis_transform_only_rung": minimal,
        "basis_transform_only_ppm_of_total": minimal * 1000000 // _INCUMBENT_TOTAL,
        "layer32_decode_NOT_IN_THE_RUNG": decode_lane(t7, DESIGN_ROWS),
    }


# ---------------------------------------------------------------------------
# DOOR 5.  Folding the odd channel's level-1 alphabet into the decode that
# produces ``cM``.
# ---------------------------------------------------------------------------


def alphabet_into_decode_price(t7) -> dict:
    """Price the fold, at the decode's own outermost write rate.

    ``cM`` has one reader: the level-1 alphabet.  A decode emitting the four
    level-1 arrays directly would never materialize ``cM`` at all.  Its
    outermost reconstruction level would write the alphabet's 131,072 elements
    instead of ``cM``'s 65,536, at the same seven writes per unit of node area
    that ``graded_decode_cost`` charges at level 1 -- so the fold is a SAVING in
    exact arithmetic.  It is refused because it reassociates the decode's
    summation; ``_selfcheck`` executes the divergence in f32.
    """
    levels = layer_call_depth(t7, TILE_ROWS, WIDTH, WIDTH)
    node = (WIDTH >> 1) * (WIDTH >> 1)
    outermost = 6 * node + node                 # six arithmetic + one inverse Psi
    alphabet = _LEVEL1_OPS_PER_PAIR * (WIDTH // 2) * WIDTH
    charged_area = WIDTH * WIDTH
    fused_area = 4 * (WIDTH // 2) * WIDTH       # P, Q, R, S over half-height
    if fused_area % charged_area:
        raise ValueError("the alphabet is not a whole multiple of cM's area")
    fused = outermost * (fused_area // charged_area)
    return {
        "precompute_decode_total": decode_lane(t7, WIDTH, WIDTH, levels),
        "outermost_reconstruction_level": outermost,
        "level1_alphabet_charged": alphabet,
        "charged_pair": outermost + alphabet,
        "fused_outermost_at_the_same_write_rate": fused,
        "exact_arithmetic_delta": fused - (outermost + alphabet),
        "cM_area": charged_area,
        "alphabet_area": fused_area,
    }


# ---------------------------------------------------------------------------
# DOOR 6.  The standing price of the two IEEE identities the ladder refuses.
# ---------------------------------------------------------------------------


def refused_identity_family_price(butterflies: int = 2) -> dict:
    """What the ladder's exactness law costs, computed once for the whole bill.

    The four level-1 arrays are closed under negation AS VALUES, so under the
    two refused identities the level-1 build would be four ops per pair instead
    of five, and a level-2 DIFFERENCE would be a level-2 SUM against an array
    already in the set -- sixteen arrays per group of four instead of
    thirty-two.  Both are unavailable at f32 because of signed zero, executed in
    ``_selfcheck``.  The saving is confined to the two butterfly prologues:
    every other signed sum in the bill is a Winograd lane at the graded-basis
    argmin, and the per-frame stages need both outputs of every pair.
    """
    if butterflies < 1:
        raise ValueError("the bill charges at least one butterfly prologue")
    pairs = WIDTH // 2
    groups = WIDTH // 4
    level1_charged = _LEVEL1_OPS_PER_PAIR * pairs * WIDTH
    level1_under_identities = 4 * pairs * WIDTH
    level2_charged = _LEVEL2_ARRAYS_PER_GROUP * groups * WIDTH
    level2_under_identities = (_LEVEL2_ARRAYS_PER_GROUP // 2) * groups * WIDTH
    per_butterfly = ((level1_charged - level1_under_identities)
                     + (level2_charged - level2_under_identities))
    return {
        "level1_charged": level1_charged,
        "level1_under_the_refused_identities": level1_under_identities,
        "level2_charged": level2_charged,
        "level2_under_the_refused_identities": level2_under_identities,
        "per_butterfly": per_butterfly,
        "both_butterflies_OFF_THE_BOARD": butterflies * per_butterfly,
        "ppm_of_total": butterflies * per_butterfly * 1000000 // _INCUMBENT_TOTAL,
    }


# ---------------------------------------------------------------------------
# The ledger's working precision, so doors 5 and 6 are measured, not asserted.
# ---------------------------------------------------------------------------


def _f32(x: float) -> float:
    """Round to the nearest binary32, the precision the deployed route runs in."""
    return struct.unpack("<f", struct.pack("<f", x))[0]


def _add32(a: float, b: float) -> float:
    return _f32(_f32(a) + _f32(b))


def _sub32(a: float, b: float) -> float:
    return _f32(_f32(a) - _f32(b))


def _bits32(x: float) -> str:
    """The bit pattern, so ``+0.0`` and ``-0.0`` are distinguishable."""
    return struct.pack("<f", _f32(x)).hex()


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
    boundary_transform_carry_declined: int
    boundary_basis_transform_only_declined: int
    alphabet_into_decode_refused: int
    refused_identity_family: int
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
            "DOOR4_transform_domain_carried_across_the_ReLU_DECLINED":
                self.boundary_transform_carry_declined,
            "DOOR4_basis_transforms_only_DECLINED":
                self.boundary_basis_transform_only_declined,
            "DOOR5_level1_alphabet_folded_into_the_decode_REFUSED":
                self.alphabet_into_decode_refused,
            "DOOR6_the_two_refused_IEEE_identities_WHOLE_PRICE":
                self.refused_identity_family,
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

    # THE THREE DOORS THIS TIER CLOSES.  None of them touches a term of
    # ``.total``; they are carried on the bill so the printout is the
    # ladder's own record of what has been priced and refused.
    carry = boundary_transform_carry(t7)
    fold = alphabet_into_decode_price(t7)
    identities = refused_identity_family_price(2)
    if carry["maximal_rung"] <= layer2:
        raise ValueError("door 4 is not the largest rung in the bill")
    if fold["exact_arithmetic_delta"] >= 0:
        raise ValueError("door 5 is a loss, not a refused saving")

    return SuiteBill(
        strategy="the_relu_seals_the_transform_domain_at_every_boundary",
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
        boundary_transform_carry_declined=carry["maximal_rung"],
        boundary_basis_transform_only_declined=(
            carry["basis_transform_only_rung"]
        ),
        alphabet_into_decode_refused=-fold["exact_arithmetic_delta"],
        refused_identity_family=(
            identities["both_butterflies_OFF_THE_BOARD"]
        ),
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
# no door is shut on a route that was never legal:
#   (a) Psi does not commute with the ReLU, and Psi(relu(.)) is not a function
#       of Psi(.) entry by entry -- door 4, in both of its forms;
#   (b) the alphabet covers every entry of cM, and the fold that would skip
#       cM reassociates the decode -- door 5, measured in f32;
#   (c) the level-1 and level-2 alphabets are negation-closed over the
#       integers and not over f32 -- door 6, bit pattern for bit pattern;
#   (d) the identities the charged route rests on: the CReLU split, the phased
#       Walsh design product, and the scalar's associativity;
#   (e) tier 25's three doors, re-executed from this file's own terms.
# Integers everywhere except where the ledger's binary32 is the point.
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

    # (0) THIS TIER IS DRY: THE BILL IS TIER 19/20/25's, TERM FOR TERM. -------
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

    #     And the grading is the argmin by BRUTE FORCE over the whole 2**6
    #     lattice, for all three lanes -- not by the module's marginal
    #     shortcut.  This is what makes the two lanes door 4 attacks a floor.
    depth = bill.call_depth
    for lane, cost_of in (
        ("A-side", lambda std: t7.inplace_operand_cost(TILE_ROWS, WIDTH, depth,
                                                       std)),
        ("W-side", lambda std: t7.inplace_operand_cost(WIDTH, WIDTH, depth,
                                                       std)),
        ("decode", lambda std: t7.graded_decode_cost(TILE_ROWS, WIDTH, depth,
                                                     std)),
    ):
        best = None
        for mask in range(1 << depth):
            std = frozenset(j for j in range(1, depth + 1)
                            if mask >> (j - 1) & 1)
            value = cost_of(std)
            if best is None or value < best:
                best = value
        assert best == cost_of(frozenset()), lane
    assert (leaf_lane(t7, TILE_ROWS) + a_side_lane(t7, TILE_ROWS)
            + decode_lane(t7, TILE_ROWS) + bill.weight_stack) \
        == _CERTIFIED_CALL_FLOOR

    # (2) THE ROW LANE IS EXACTLY LINEAR IN m -- the reason door 1 is zero. ----
    unit = Fraction(bill.row_part_full, TILE_ROWS)
    for rows in (256, 512, 2048, 3072, 3584, 3840,
                 BASE_ROWS, BASE_ROWS + WIDTH, 32768, DESIGN_ROWS):
        assert Fraction(row_lane(t7, rows)) == unit * rows, rows
    assert row_lane(t7, BASE_ROWS % TILE_ROWS) == bill.row_part_tail
    assert 8 * row_lane(t7, 3584) == 7 * bill.row_part_full
    assert 4 * row_lane(t7, 3072) == 3 * bill.row_part_full
    assert row_lane(t7, WIDTH) == bill.layer2_precompute

    # (3) TIER 25's DOOR 1, re-executed.  The fused call is legal and zero. ---
    nxt = _rng(20250826)
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

    # (4) TIER 25's DOOR 2, re-executed: alphabet(cM) = alphabet(W0') W1h. ----
    cM = _mm(W0p, W1h)
    a1_left, a1_right = level1_alphabet(W0p), level1_alphabet(cM)
    assert len(a1_left) == len(a1_right) == 4
    for pair_left, pair_right in zip(a1_left, a1_right):
        for left_array, right_array in zip(pair_left, pair_right):
            assert _mm([left_array], W1h)[0] == right_array, \
                "the level-1 alphabet does not commute with W1h"
    a2_left, a2_right = level2_alphabet(W0p), level2_alphabet(cM)
    for group_left, group_right in zip(a2_left, a2_right):
        assert len(group_left) == _LEVEL2_ARRAYS_PER_GROUP
        for left_array, right_array in zip(group_left, group_right):
            assert _mm([left_array], W1h)[0] == right_array, \
                "the level-2 alphabet does not commute with W1h"
    carries = {c["stage"]: c for c in
               (alphabet_carry_price(t7, s) for s in (1, 2, 3))}
    assert carries[1]["worse_by"] == 18660000
    assert carries[2]["worse_by"] == 131078752
    assert carries[3]["worse_by"] == 2389939552
    assert bill.layer2_alphabet_carry_declined == carries[1]["route_total"]

    # (5) TIER 25's DOOR 3, re-executed: the fused terminal stage ties. -------
    write = fused_antipodal_final_stage()
    assert write["unfused_total"] == write["fused_total"] == 57802752
    assert write["delta"] == 0

    # (6) THE SHARED-DEPTH ARGMIN, re-derived over 0..3. ----------------------
    sweep = {d: butterfly_at_shared_depth(d) for d in (0, 1, 2, 3)}
    assert sweep[0] == 74317824 and sweep[1] == 57966592
    assert sweep[2] == 50233344 and sweep[3] == 50364416
    assert min(sweep, key=lambda d: sweep[d]) == _SHARED_DEPTH == 2
    assert sweep[2] == bill.layer2_odd_butterfly == bill.layer1_butterfly

    # ======================================================================
    # (7) DOOR 4.  THE RUNG IS INSIDE THE BILL, AND IT IS THE LARGEST ONE.
    # ======================================================================
    #     First: the four lanes of a generic layer add up to the charged layer,
    #     so the two lanes the rung would delete are not a modelling fiction.
    assert leaf_lane(t7, DESIGN_ROWS) == 3320525376
    assert a_side_lane(t7, DESIGN_ROWS) == 482618304
    assert decode_lane(t7, DESIGN_ROWS) == 940464000
    assert (leaf_lane(t7, DESIGN_ROWS) + a_side_lane(t7, DESIGN_ROWS)
            + decode_lane(t7, DESIGN_ROWS) + bill.weight_stack) \
        == bill.generic_layer == 4745522832
    #     ... and for layer 2's half-height even channel.
    assert (leaf_lane(t7, BASE_ROWS) + a_side_lane(t7, BASE_ROWS)
            + decode_lane(t7, BASE_ROWS)) == bill.layer2_even_rows
    assert a_side_lane(t7, BASE_ROWS) == 241309152 == bill.suite_once_design_stack
    #     The transcribed Psi term is the module's own.
    for rows in (TILE_ROWS, BASE_ROWS, DESIGN_ROWS, WIDTH):
        assert basis_transform_lane(rows, WIDTH, bill.call_depth) \
            == t7.psi_cost(rows, WIDTH, bill.call_depth), rows

    carry = boundary_transform_carry(t7)
    assert carry["boundaries"] == 30 == LAYERS - 2
    assert carry["decode_lanes_layers_2_to_31"] == 27743688000
    assert carry["a_side_lanes_layers_3_to_32"] == 14478549120
    assert carry["maximal_rung"] == 42222237120
    assert carry["maximal_rung_ppm_of_total"] == 291455
    assert carry["basis_transform_only_rung"] == 1473970176
    assert carry["basis_transform_only_ppm_of_total"] == 10174
    assert carry["maximal_rung"] == bill.boundary_transform_carry_declined
    assert carry["basis_transform_only_rung"] \
        == bill.boundary_basis_transform_only_declined
    #     It really is the largest single rung the bill contains: bigger than
    #     every other term except the leaf lane it does not touch.
    assert carry["maximal_rung"] > bill.layer2_total
    assert carry["maximal_rung"] > 30 * bill.weight_stack + bill.weight_stack
    assert carry["maximal_rung"] > 100 * bill.layer2_precompute

    # ---- AND IT IS SEALED.  Psi does not commute with the ReLU. ------------
    #     (a) the plain failure, on the module's own transform.
    pattern = [True, True]
    grid = _mat(4, 4, nxt)
    straight = t7._psi(grid, t7.PHI_A, list(pattern), [0])
    crossed = t7._psi(_relu(grid), t7.PHI_A, list(pattern), [0])
    assert crossed != _relu(straight), (
        "Psi commuted with the ReLU on this sample; re-open door 4")

    #     (b) the entrywise refutation, which kills every zero-cost elementwise
    #         repair applied in the transformed domain.  Two matrices agreeing
    #         at a transformed entry, disagreeing at the same entry after the
    #         ReLU: so Psi(relu(.)) is not a function of Psi(.) entry by entry.
    witness = None
    for _trial in range(4000):
        c1 = _mat(4, 4, nxt)
        c2 = _mat(4, 4, nxt)
        p1 = t7._psi(c1, t7.PHI_A, list(pattern), [0])
        p2 = t7._psi(c2, t7.PHI_A, list(pattern), [0])
        r1 = t7._psi(_relu(c1), t7.PHI_A, list(pattern), [0])
        r2 = t7._psi(_relu(c2), t7.PHI_A, list(pattern), [0])
        for i in range(4):
            for j in range(4):
                if p1[i][j] == p2[i][j] and r1[i][j] != r2[i][j]:
                    witness = (i, j, p1[i][j], r1[i][j], r2[i][j])
                    break
            if witness:
                break
        if witness:
            break
    assert witness is not None, (
        "no entrywise witness found; door 4 needs a wider search before it is "
        "declared shut")

    #     (c) the ONE nonlinearity this ladder does cross, re-run beside the
    #         failure so the two are never confused.  It is a statement about
    #         the antipodal pair, not about ReLU and a linear map.
    width = 8
    H = _hadamard(width)
    signs = [1 if nxt(0, 1) else -1 for _ in range(width)]
    scalar = 3                      # stands in for c = MEAN_CHI_256 / 16
    W0 = _mat(width, width, nxt)
    W0_scaled = _scale(scalar, W0)
    W1 = _mat(width, 5, nxt)
    P = layer1_route(signs, W0_scaled)
    assert P == _mm(design_block(signs, H), W0_scaled)
    cM_full = _mm(W0_scaled, W1)
    O_full = layer1_route(signs, cM_full)
    assert O_full == _mm(design_block(signs, H), cM_full) == _mm(P, W1)
    top = _mm(_relu(P), W1)
    assert _mm(_relu(_neg(P)), W1) == _sub(top, O_full), (
        "the CReLU split failed; the banked layer-2 route is not what is billed")
    assert _scale(scalar, _mm(W0, W1)) == _mm(W0_scaled, W1)
    before = [row[:] for row in W0_scaled]
    _ = layer1_route(signs, W0_scaled)
    assert W0_scaled == before, "layer 1 wrote its weight operand"
    #     ... and the pairing FAILS one layer later, which is tier 20's kill
    #         re-run here because door 4 would otherwise inherit it: layer 2's
    #         halves are ``[t ; t - o]``, and they are antipodal only if o = 2t.
    bottom = _sub(top, O_full)
    assert top != _neg(bottom), "layer 2's halves are antipodal; re-open"
    assert _relu(bottom) != _sub(_relu(top), top), (
        "the CReLU form closed on layer 2's OUTPUT halves; re-open tier 20's "
        "door")

    # ======================================================================
    # (8) DOOR 5.  THE ALPHABET CANNOT BE FOLDED INTO THE PRECOMPUTE'S DECODE.
    # ======================================================================
    fold = alphabet_into_decode_price(t7)
    assert fold["precompute_decode_total"] == 3732000 \
        == bill.layer2_precompute_decode
    assert fold["outermost_reconstruction_level"] == 114688
    assert fold["level1_alphabet_charged"] == 163840 \
        == bill.layer2_odd_level1_arrays
    assert fold["charged_pair"] == 278528
    assert fold["fused_outermost_at_the_same_write_rate"] == 229376
    assert fold["exact_arithmetic_delta"] == -49152
    assert fold["alphabet_area"] == 2 * fold["cM_area"] == 131072
    assert bill.alphabet_into_decode_refused == 49152

    #     (a) the decode cannot be shrunk instead: the alphabet reads EVERY
    #         entry of cM.  The coverage map is MEASURED -- each entry is
    #         perturbed and the four readable arrays are recomputed -- rather
    #         than read off the formula that would make it circular.
    probe = _mat(8, 4, nxt)
    base_arrays = [tuple(map(tuple, pair[1:]))
                   for pair in level1_alphabet(probe)]
    coverage = {}
    for i in range(len(probe)):
        for j in range(len(probe[0])):
            bumped = [row[:] for row in probe]
            bumped[i][j] += 1
            moved = 0
            for pair_base, pair_new in zip(base_arrays,
                                           level1_alphabet(bumped)):
                for old, new in zip(pair_base, tuple(map(tuple,
                                                         pair_new[1:]))):
                    if old != new:
                        moved += 1
            coverage[(i, j)] = moved
    assert len(coverage) == 8 * 4, "the coverage map is not the whole matrix"
    assert min(coverage.values()) > 0, (
        "some entry of cM is unread; a shrunken decode would be legal")
    assert set(coverage.values()) == {4}, (
        "cM's entries are not each read by exactly four readable arrays")

    #     ... and cM really does have ONE reader.  The odd channel's charged
    #         terms are exactly the level-1 build (from cM), the level-2 build
    #         (from level 1) and six per-frame stages (from level 2); the bill's
    #         own guards refuse any other shape, and no other term names cM.
    assert bill.layer2_odd_shared_prologue == (
        bill.layer2_odd_level1_arrays + bill.layer2_odd_level2_arrays)
    assert bill.layer2_odd_level1_arrays \
        == _LEVEL1_OPS_PER_PAIR * (WIDTH // 2) * WIDTH
    assert bill.layer2_odd_level2_arrays \
        == _LEVEL2_ARRAYS_PER_GROUP * (WIDTH // 4) * WIDTH
    assert (bill.layer2_odd_butterfly - bill.layer2_odd_shared_prologue) \
        == _BUTTERFLY_FRAME_ELEMENT_FOLDED * BASE_ROWS * WIDTH

    #     (b) the fold is a REASSOCIATION, and the ladder's exactness law is bit
    #         identity.  Executed in the ledger's own working precision.
    d1, d2 = _f32(2.0 ** 24), 1.0            # contributions to row 2t
    e1, e2 = _f32(-(2.0 ** 24)), 1.0         # contributions to row 2t+1
    charged_order = _add32(_add32(d1, d2), _add32(e1, e2))
    fused_order = _add32(_add32(_add32(d1, e1), d2), e2)
    assert charged_order == 1.0, charged_order
    assert fused_order == 2.0, fused_order
    assert charged_order != fused_order, (
        "the reassociation agreed here; door 5 needs a sharper witness")

    # ======================================================================
    # (9) DOOR 6.  THE STANDING PRICE OF THE TWO REFUSED IEEE IDENTITIES.
    # ======================================================================
    identities = refused_identity_family_price(2)
    assert identities["level1_charged"] == 163840
    assert identities["level1_under_the_refused_identities"] == 131072
    assert identities["level2_charged"] == 524288 \
        == bill.layer2_odd_level2_arrays
    assert identities["level2_under_the_refused_identities"] == 262144
    assert identities["per_butterfly"] == 294912
    assert identities["both_butterflies_OFF_THE_BOARD"] == 589824
    assert identities["ppm_of_total"] == 4
    assert bill.refused_identity_family == 589824

    #     (a) over the integers the closure is real: S = -P and R = -Q.
    seed = _mat(8, 6, nxt)
    for na, Pv, Qv, Rv, Sv in level1_alphabet(seed):
        assert Sv == [-v for v in Pv], "the level-1 set is not negation-closed"
        assert Rv == [-v for v in Qv], "the level-1 set is not negation-closed"
    #     ... and the thirty-two level-2 arrays take only sixteen VALUES.
    for group in level2_alphabet(seed):
        assert len(group) == 32
        assert len({tuple(a) for a in group}) == 16, (
            "the level-2 alphabet is not two copies of sixteen values")

    #     (b) and it is unavailable at f32, at signed zero, bit for bit.
    a, b = 1.0, -1.0
    assert _bits32(_f32(-_add32(a, b))) == "00000080"          # -(a + b)
    assert _bits32(_add32(-a, -b)) == "00000000"               # (-a) + (-b)
    assert _bits32(_f32(-_add32(a, b))) != _bits32(_add32(-a, -b))
    assert _bits32(_f32(-_sub32(1.0, 1.0))) == "00000080"      # -(a - b)
    assert _bits32(_sub32(1.0, 1.0)) == "00000000"             # b - a, a == b
    assert _bits32(_f32(-_sub32(1.0, 1.0))) != _bits32(_sub32(1.0, 1.0))
    #     The two identities the ladder DOES permit are exact, and are used.
    assert _sub32(3.5, 1.25) == _add32(3.5, -1.25)
    assert _bits32(-_f32(2.5)) == _bits32(_f32(-2.5))

    # (10) THE SUITE-ONCE RESIDUE: real, dead, and unscorable per net. --------
    rung = shared_descriptor_table_price(FRAMES, WIDTH)
    assert rung["charged_suite_once"] == 64512
    assert rung["suite_once_saving_NOT_CLAIMED"] == 32256
    assert rung["per_net_saving"] == 0
    assert bill.suite_once_design_stack == 241309152
    assert bill.suite_once == bill.suite_once_design_stack + 64512
    residue = bill.suite_once_design_stack + rung["suite_once_saving_NOT_CLAIMED"]
    assert residue == 241341408
    assert bill.suite_total(1000) - 1000 * bill.total == bill.suite_once

    # (11) THE CARRIED CONSERVATIVE CHOICES, counted and NOT claimed. ---------
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

    # (12) NOTHING MOVED.  The delta against the incumbent is exactly zero. ---
    assert bill.total - _INCUMBENT_TOTAL == 0
    assert incumbent_total() == _INCUMBENT_TOTAL == 144867083088


def main() -> None:
    bill = suite_bill_per_net()
    _selfcheck()
    t7 = _t7()
    print(f"strategy                  {bill.strategy}")
    print(f"suite bill, per net       {bill.total:,}")
    print(f"incumbent (tier 19/25)    {_INCUMBENT_TOTAL:,}")
    print(f"delta                     {bill.total - _INCUMBENT_TOTAL:,}   DRY")
    print()
    for key, value in bill.breakdown().items():
        print(f"  {key:<66} {value:,}")
    print()
    print("DOOR 4  the transform domain carried across a layer boundary")
    for key, value in boundary_transform_carry(t7).items():
        print(f"  {key:<56} {value:,}")
    print("DOOR 5  the level-1 alphabet folded into the precompute's decode")
    for key, value in alphabet_into_decode_price(t7).items():
        print(f"  {key:<56} {value:,}")
    print("DOOR 6  the standing price of the two refused IEEE identities")
    for key, value in refused_identity_family_price().items():
        print(f"  {key:<56} {value:,}")
    print("CARRIED tier 25's three doors, re-executed")
    print(f"  {'fused 32,512-row call, delta':<56} "
          f"{fused_precompute_call(t7)['delta']:,}")
    for stage in (1, 2, 3):
        print(f"  {'alphabet carry at stage ' + str(stage) + ', worse by':<56} "
              f"{alphabet_carry_price(t7, stage)['worse_by']:,}")
    print(f"  {'fused terminal stage, delta':<56} "
          f"{fused_antipodal_final_stage()['delta']:,}")
    print("RESIDUE suite-once, unscorable per net, NOT claimed")
    print(f"  {'orphaned design-side stack':<56} "
          f"{bill.suite_once_design_stack:,}")
    print(f"  {'second frame-descriptor table':<56} "
          f"{shared_descriptor_table_price()['suite_once_saving_NOT_CLAIMED']:,}")


if __name__ == "__main__":
    main()
