"""Tier 6: the basis-change writes are scattered into the leaf stack slots.

ONE SUBSTANTIVE CHANGE
======================
Tier 3 gave the *arithmetic* tree a scatter licence: an interior operand block,
at the moment it is written, may be written straight into the leaf batch-stack
slots its identity descendants occupy, instead of being written somewhere else
and then copied.  Tier 4 then introduced a second tree -- the alternative-basis
transform ``Psi`` -- and tier 5 graded it per level.  Neither tier ever gave
that second tree the licence tier 3 gave the first.  Every ``Psi`` write is
still billed as if it landed in a shadow copy of ``A``, and every leaf slot
descending from the root is billed a *second* time as a copy out of that shadow.

The one change here is to extend tier 3's scatter licence from the arithmetic
tree to the basis-transform tree.  A ``Psi`` write is a write like any other: it
chooses its destination.  Point it at the leaf stack slots covering the block it
writes, and the copy those slots would otherwise have needed disappears.

Nothing else moves: the leaf count is still 7**L, the depth sweep is tier 1's,
the interior view elision is tier 2's, the arithmetic-tree scatter is tier 3's,
the alternative-basis algebra is tier 4's, the per-level grading is tier 5's,
the arithmetic performed is bit-for-bit tier 5's.

WHICH COPIES SURVIVE, AND WHY THE ANSWER IS ``3**L``
====================================================
Each of the three basis maps is a *single* elementary row operation on the
quadrant vector, so at one node ``Psi`` rewrites exactly one quadrant slot --
call it ``sigma`` (slot 2, ``A21 += A22``, on the left; slot 1,
``B12 -= B11``, on the right).  A leaf position is named by its path
``(q_1, ..., q_L)`` of quadrant choices, and ``Psi`` touches that leaf at
level ``j`` if and only if ``q_j == sigma`` and level ``j`` is alternative.
The deepest touching level writes the leaf's final transformed value; direct
*that* write into the leaf's stack slot and the slot is filled for free.

So the leaves still needing a copy are exactly the root-descended free-view
leaves whose path never takes ``sigma`` at an alternative level.  Count the
choices level by level:

    alternative level -- four free views, one of them ``sigma``  ->  3 survivors
    standard level    -- three free views, and ``sigma`` is not among them
                         (in the standard basis that slot is the *arithmetic*
                         block S1 / T1, never a view), and phi = I writes
                         nothing anyway                          ->  3 survivors

Both rows read 3.  The surviving-copy count is therefore ``3**L``, *independent
of the grading* -- where tier 5 charged ``3**s * 4**(L-s)``:

    root copies      tier 5                    tier 6
    left lane        3 * 4**5 * 256 = 786,432  3**6 * 256 = 186,624
    right lane       3 * 4**5 *  16 =  49,152  3**6 *  16 =  11,664
                                               ------------------------
                                               saving       637,296

The grading sweep survives the change but its answer flips.  Tier 5's whole win
was that demoting level 1 to the identity multiplied the root lane by 3/4 for
free.  With the root lane now grading-blind, that purchase buys nothing, and the
marginal cost of demoting level ``j``, ``(7**(j-1) - 4**(j-1)) * A_j``, is zero
at level 1 and positive after -- so the optimum returns to all-alternative, with
level 1 exactly tied.  The two gradings cost the same to the last unit, which is
the cleanest possible confirmation that tier 5's saving has been *subsumed*
rather than double-counted: tier 5 bought ``mk/4 + kn/4`` of the root lane, and
this tier buys ``(4**L - 3**L)/4**L`` of it, the larger amount, by a different
mechanism that makes tier 5's mechanism redundant instead of additive.

EXACTNESS IDENTITY
==================
*The arithmetic is unchanged.*  This tier alters no operand, no coefficient, no
order of accumulation and no rounding: it changes the destination address of
writes that were already billed, and deletes copies that a write already
performed.  Every value the schedule computes is the value tier 5's schedule
computes, which is the value the direct route computes.  The chain, restated so
the file stands alone:

Winograd's seven-multiplication form of the 2x2 block product,

    S1 = A21 + A22    T1 = B12 - B11
    S2 = S1  - A11    T2 = B22 - T1
    S3 = A11 - A21    T3 = B22 - B12
    S4 = A12 - S2     T4 = T2  - B21

    M1 = A11 * B11    M2 = A12 * B21    M3 = S4 * B22    M4 = A22 * T4
    M5 = S1  * T1     M6 = S2  * T2     M7 = S3  * T3

    C11 = M1 + M2                 C12 = M1 + M3 + M5 + M6
    C21 = M1 - M4 + M6 + M7       C22 = M1 + M5 + M6 + M7

expands term by term to the block product.  Write it ``c = W_C ((U_A a) * (U_B b))``
on quadrant vectors.  For any invertible phi_A, phi_B, phi_C,

    (phi_C c) = (phi_C W_C) ( (U_A phi_A^-1)(phi_A a) * (U_B phi_B^-1)(phi_B b) )

is the same computation read in new coordinates.  With a level-indexed family
``(phi^(1), ..., phi^(L))`` define ``Psi^(L+1..L)(A) = A`` and ``Psi^(j..L)(A)``
= the matrix whose four quadrant slots hold ``Psi^(j+1..L)`` of the four outputs
of ``phi^(j)`` on A's quadrants.  ``Psi`` is linear, being a composition of
blockwise linear maps, and by induction on ``L-j+1``

    ALG^(j..L)( Psi_A^(j..L)(A), Psi_B^(j..L)(B) ) = Psi_C^(j..L)(A B),

because operand ``i`` of the top node is

    sum_p (U_A (phi_A^(j))^-1)_ip Psi_A^(j+1..L)(t_p)
        = Psi_A^(j+1..L)( (U_A (phi_A^(j))^-1 phi_A^(j) a)_i )
        = Psi_A^(j+1..L)( (U_A a)_i )                                [linearity]

so the induction hypothesis applies, and linearity of ``Psi_C`` returns output
slot ``p`` as ``Psi_C^(j+1..L)((phi_C^(j) c)_p)``.  Setting ``phi^(j) = I`` at
some levels changes nothing in that induction.  Undoing ``Psi_C^(1..L)`` returns
``A B`` exactly.

*The placement claim*, which is what this tier actually adds, is a statement
about addresses and is proved by construction rather than by algebra:

  (P1) *Distinctness.*  At every level the free views occupy pairwise distinct
       quadrant slots (asserted in ``_build_operands``), so distinct root-
       descended leaves have distinct paths and therefore occupy disjoint
       rectangles of the operand matrix.  A leaf slot never has two claimants.
  (P2) *Coverage.*  The level-``j`` ``Psi`` write of a root-descended block
       covers ``4**(L-j)`` leaf positions, all of them free-view leaves, and
       exactly ``3**(L-j)`` of them have that level as their deepest touch.  The
       write's area is ``4**(L-j)`` leaf areas and it needs to place ``3**(L-j)``
       of them, so the budget is never exceeded (asserted per level).
  (P3) *Ordering.*  ``Psi`` applies its levels top down, so for a leaf touched at
       levels ``j_1 < ... < j_r`` the level-``j_r`` write is last; every earlier
       write of that leaf's data is an intermediate that the next write reads,
       and reading it out of the leaf slot is the same read.  The slot's final
       contents are the fully transformed block.
  (P4) *Residue.*  A leaf whose path never takes ``sigma`` at an alternative
       level is never written by ``Psi`` at all: its transformed value equals the
       original block, and it is still charged a copy.  There are ``3**L`` of
       them, and they are the only copies this tier bills.

*The three non-identity maps*, unchanged from tier 4, unimodular, entries in
{-1, 0, 1}, each a single elementary row operation whose moved row carries
coefficient 1 on its own coordinate:

    phi_A = [[1,0,0,0],[0,1,0,0],[0,0,1,1],[0,0,0,1]]   det 1   (A21 += A22)
    phi_B = [[1,0,0,0],[-1,1,0,0],[0,0,1,0],[0,0,0,1]]  det 1   (B12 -= B11)
    phi_C = [[1,0,0,0],[0,1,0,-1],[0,0,1,0],[0,0,0,1]]  det 1   (C12 -= C22)

No division, no reciprocal, no scaling, no truncation, no value-dependent
reordering: over any ring the result is the ring element the direct route
computes, and over the integers ``verify_schedule`` checks it literally.

WHY THE OTHER LANES ARE NOT TOUCHED
===================================
The decode lane has no copy term to delete -- every one of a node's four outputs
is written, none is a free view -- and its per-node constant is already at the
proved floor.  Tier 5 closed that: choosing phi_C is choosing four independent
vectors spanning the row space of W_C, ``_decode_floor_is_six`` enumerates every
straight-line +/- program of length <= 5 and finds none, and the transposition
principle ``a(M^T) = a(M) + m - n`` gives ``a(W_C) = a(W_C^T) + 3 >= 6`` because
an encode-shaped 7-by-4 map has at most 4 unit rows.  The same bound gives
``a(U_A), a(U_B) >= 3``, both attained.  Composing levels does not loosen it: the
two-level encode is 49-by-16 with floor ``49 - 16 = 33``, which nested single
levels hit exactly (``3*A_1 + 21*A_2 = 33*A_2``), and the two-level decode is
16-by-49 with floor 66, which nesting also hits exactly.  So the arithmetic
overhead of this algorithm family is closed at every depth, the leaf lane sits at
Winograd's rank bound for <2,2,2>, and the copy lane attacked here was the only
lane left with slack in it.

RESULT AT (4096, 256, 256)
==========================
    L    tier 6           tier 5 (graded)   tier 4 (uniform alt)
    1      471,711,744       471,711,744       471,990,272
    2      416,161,792       416,370,688       416,649,216
    3      370,132,992       370,498,560       370,777,088
    4      334,291,456       334,774,528       335,053,056
    5      310,618,752       311,189,952       311,468,480
    6    * 303,294,880       303,932,176       304,210,704
    7      320,256,840       320,943,708       321,222,236
    8      375,937,714       376,661,761       376,940,289

    total 303,294,880  =  210,827,008 leaves          (unchanged)
                        +  30,829,056 left operands   (-599,808)
                        +   1,926,816 right operands  (-37,488)
                        +  59,712,000 decode          (unchanged)

Depth stays at L = 6.  Against the incumbent 303,932,176 the saving is 637,296
FLOPs (0.2097%); against the 535,822,336 direct comparator the ratio is 0.566036.

What is left is the leaf lane -- 210,827,008, now 69.5% of the bill and untouched
since tier 0 -- where rank 7 is optimal for <2,2,2> and every other exact base
tensor with a better exponent (<3,3,3;23> at log_3 23, Smirnov's <3,3,6;40>)
needs a factor of three in dimensions that 4096 x 256 x 256 does not have.  With
the arithmetic overhead proved minimal and the copy lane now down to its
``3**L`` residue, this family's schedule frontier is close to shut.

No approximation, no rank reduction, no f32 repricing, no compliance flags --
pure schedule.

VERIFICATION RUN IN ``_selfcheck``
==================================
1. An executable integer verifier transforms random integer A and B by the graded
   ``Psi``, runs the graded recursion, undoes ``Psi_C``, and asserts the result
   equals the plain integer product, over several distinct grading patterns
   including ones that differ between the three lanes.
2. The same verifier counts every write the schedule really performs and asserts
   the count equals the billed closed form lane by lane.
3. The new placement claim is *measured*, not asserted: ``_build_operands`` walks
   the operand tree carrying each view's path, decides per leaf whether ``Psi``
   ever writes it, charges a copy only when it does not, and hands every
   ``Psi``-placed leaf to ``_assert_psi_scatter_is_free``, which checks (P1)
   disjointness and containment inside the exact ``Psi`` write block, (P2) that
   each block places exactly ``3**(L-j)`` leaves and never exceeds its write
   budget, and that the per-level claimed area fits inside ``4**(j-1) * A_j``.
   The surviving copy count is asserted to be ``3**L`` from the walk, not from
   the formula.
4. The arithmetic-tree geometry of tier 3 is re-checked unchanged.
5. Both encodes are asserted, symbolically and in both bases, to reproduce
   Winograd's S1..S4 and T1..T4, and both decodes to reproduce C11..C22.
6. The decode floor of six is re-derived by exhaustive enumeration.
7. Tier 3's, tier 4's and tier 5's published depth tables are reproduced digit
   for digit from reconstructions of their closed forms, and this tier's cost is
   asserted to equal tier 5's minus exactly ``(3**s * 4**(L-s) - 3**L) * A_L``
   on each operand lane -- so the saving cannot be anything other than the copy
   lane.
8. ``_best_grade``'s sorted selection is asserted equal to a brute force over all
   2**L subsets of levels, at every depth in the sweep.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations


# ---------------------------------------------------------------------------
# Helpers copied from the lineage (self-contained by rule 7; never imported).
# ---------------------------------------------------------------------------


def direct_cost(m: int, k: int, n: int) -> int:
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


def batched_winograd_core_cost(m: int, k: int, n: int) -> int:
    """One batched leaf call with explicit stack fills and reconstruction."""
    if min(m, k, n) <= 0 or any(value % 2 for value in (m, k, n)):
        raise ValueError("one Winograd level requires positive even dimensions")
    leaf = 7 * direct_cost(m // 2, k // 2, n // 2)
    stack_fills = 7 * (m // 2) * (k // 2) + 7 * (k // 2) * (n // 2)
    output_adds = 7 * (m // 2) * (n // 2)
    return leaf + stack_fills + output_adds


@dataclass(frozen=True)
class Bill:
    strategy: str
    m: int
    k: int
    n: int
    core_k: int
    core_n: int
    core: int
    inner_correction: int
    inner_add: int
    output_tail: int
    total: int
    direct: int
    call_count: int

    def to_dict(self) -> dict:
        return asdict(self)


def batched_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Shape-only bill for the memory-bounded batched mutation."""
    baseline = direct_cost(m, k, n)
    if m % 2:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    kc = k - (k % 2)
    nc = n - (n % 2)
    inner = k - kc
    output = n - nc
    if kc == 0 or nc == 0 or (inner and output):
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    core = batched_winograd_core_cost(m, kc, nc)
    inner_mm = direct_cost(m, inner, nc) if inner else 0
    inner_add = (m * nc + m) if inner else 0
    output_mm = direct_cost(m, k, output) if output else 0
    total = core + inner_mm + inner_add + output_mm
    calls = 1 + int(bool(inner)) + int(bool(output))
    if total >= baseline:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    strategy = (
        "winograd_batched_preallocated_odd_k"
        if inner
        else "winograd_batched_preallocated"
    )
    return Bill(
        strategy, m, k, n, kc, nc, core, inner_mm, inner_add,
        output_mm, total, baseline, calls,
    )


def owned_batched_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Exact bill for the caller-owned, blockwise in-place operator."""
    base = batched_candidate_bill(m, k, n)
    direct_total = direct_cost(m, k, n) + m * k
    if base.strategy == "direct":
        return Bill("direct_owned", m, k, n, 0, 0, 0, 0, 0, 0,
                    direct_total, direct_cost(m, k, n), 1)
    tail_copy = m if base.output_tail else 0
    total = base.total + tail_copy
    if total >= direct_total:
        return Bill("direct_owned", m, k, n, 0, 0, 0, 0, 0, 0,
                    direct_total, direct_cost(m, k, n), 1)
    strategy = (
        "winograd_batched_owned_odd_k"
        if base.inner_correction
        else "winograd_batched_owned"
    )
    return Bill(
        strategy, m, k, n, base.core_k, base.core_n,
        base.core, base.inner_correction, base.inner_add,
        base.output_tail + tail_copy, total, direct_cost(m, k, n),
        base.call_count,
    )


def node_area_sum(a_dim: int, b_dim: int, levels: int) -> int:
    """One block per node of the 7-ary recursion tree, summed over L levels."""
    return sum(7 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
               for j in range(1, levels + 1))


def psi_cost(a_dim: int, b_dim: int, levels: int) -> int:
    """Tier 4: one quadrant write per node of the 4-ary transform tree."""
    return sum(4 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
               for j in range(1, levels + 1))


# Ancestor closed forms, reproduced so the new formula can be asserted against
# each of them (rule 7 forbids importing them).


def standard_operand_stack_cost(a_dim: int, b_dim: int, levels: int) -> int:
    """Tier 3: four arithmetic blocks per node plus 3**L root copies."""
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    return (4 * node_area_sum(a_dim, b_dim, levels)
            + 3 ** levels * (a_dim >> levels) * (b_dim >> levels))


def standard_reconstruction_cost(m: int, n: int, levels: int) -> int:
    """Tier 1..3: seven reconstruction writes per node."""
    return 7 * node_area_sum(m, n, levels)


def standard_depth_core_cost(m: int, k: int, n: int, levels: int) -> int:
    block = 1 << levels
    if min(m, k, n) <= 0 or any(value % block for value in (m, k, n)):
        raise ValueError(f"{levels} Winograd levels require multiples of {block}")
    return (7 ** levels * direct_cost(m // block, k // block, n // block)
            + standard_operand_stack_cost(m, k, levels)
            + standard_operand_stack_cost(k, n, levels)
            + standard_reconstruction_cost(m, n, levels))


def alt_operand_cost(a_dim: int, b_dim: int, levels: int) -> int:
    """Tier 4: three arithmetic blocks per node, 4**L root copies, plus Psi."""
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    return (4 ** levels * (a_dim >> levels) * (b_dim >> levels)
            + psi_cost(a_dim, b_dim, levels)
            + 3 * node_area_sum(a_dim, b_dim, levels))


def alt_decode_cost(m: int, n: int, levels: int) -> int:
    """Tier 4: six reconstruction writes per node, plus the inverse Psi."""
    return 6 * node_area_sum(m, n, levels) + psi_cost(m, n, levels)


def alt_basis_depth_core_cost(m: int, k: int, n: int, levels: int) -> int:
    block = 1 << levels
    if min(m, k, n) <= 0 or any(value % block for value in (m, k, n)):
        raise ValueError(f"{levels} Winograd levels require multiples of {block}")
    return (7 ** levels * direct_cost(m // block, k // block, n // block)
            + alt_operand_cost(m, k, levels)
            + alt_operand_cost(k, n, levels)
            + alt_decode_cost(m, n, levels))


def tier5_graded_operand_cost(a_dim: int, b_dim: int, levels: int,
                              std: frozenset) -> int:
    """Tier 5's operand lane: root copies still billed at 3**s * 4**(L-s)."""
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    arithmetic = sum(7 ** (j - 1) * (4 if j in std else 3)
                     * (a_dim >> j) * (b_dim >> j)
                     for j in range(1, levels + 1))
    transform = sum(4 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
                    for j in range(1, levels + 1) if j not in std)
    s = len(std)
    root_copies = (3 ** s * 4 ** (levels - s)
                   * (a_dim >> levels) * (b_dim >> levels))
    return arithmetic + transform + root_copies


# ---------------------------------------------------------------------------
# The one substantive change: the Psi write places the leaf, so only the leaves
# Psi never touches are still copied -- and there are 3**L of those, whatever
# the grading.
# ---------------------------------------------------------------------------


def surviving_root_copies(a_dim: int, b_dim: int, levels: int) -> int:
    """Leaf slots no Psi write can fill: paths that never take the moved slot.

    At an alternative level the four free views include the moved slot, leaving
    three that Psi never writes; at a standard level the moved slot is the
    arithmetic block, not a view, so all three views are untouched.  Both cases
    contribute a factor three, which is why this term does not see the grading.
    """
    return 3 ** levels * (a_dim >> levels) * (b_dim >> levels)


def psi_scattered_operand_cost(a_dim: int, b_dim: int, levels: int,
                               std: frozenset) -> int:
    """Blocks written to form one side's depth-L operand set.

    Identical to tier 5 except for the last term: the basis-change writes are
    scattered into the leaf stack slots they cover, so only the ``3**L`` leaves
    Psi never touches are still copied out of the root.
    """
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    arithmetic = sum(7 ** (j - 1) * (4 if j in std else 3)
                     * (a_dim >> j) * (b_dim >> j)
                     for j in range(1, levels + 1))
    transform = sum(4 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
                    for j in range(1, levels + 1) if j not in std)
    return arithmetic + transform + surviving_root_copies(a_dim, b_dim, levels)


def graded_decode_cost(m: int, n: int, levels: int, std: frozenset) -> int:
    """Reconstruction writes, graded basis.  Unchanged from tier 5: the decode
    has no free views, hence no copy term for a Psi write to absorb."""
    arithmetic = sum(7 ** (j - 1) * (7 if j in std else 6)
                     * (m >> j) * (n >> j)
                     for j in range(1, levels + 1))
    transform = sum(4 ** (j - 1) * (m >> j) * (n >> j)
                    for j in range(1, levels + 1) if j not in std)
    return arithmetic + transform


def _best_grade(cost, levels: int, marginal):
    """Cheapest grading, exactly.

    The per-node term is separable across levels and the remaining term depends
    on the grading only through ``s = len(std)`` (here, not at all), so for each
    s the optimum is the s levels of least marginal cost.  ``_selfcheck``
    brute-forces the whole 2**L lattice to confirm the sort is exact.
    """
    order = sorted(range(1, levels + 1), key=marginal)
    best_std = frozenset()
    best = cost(frozenset())
    for s in range(1, levels + 1):
        std = frozenset(order[:s])
        value = cost(std)
        if value < best:
            best, best_std = value, std
    return best, best_std


def best_operand_grade(a_dim: int, b_dim: int, levels: int):
    """Cheapest operand-lane grading.  With the root lane now grading-blind the
    marginal of demoting level j is a pure loss ``(7**(j-1) - 4**(j-1)) * A_j``,
    zero at level 1 and positive after, so all-alternative wins (level 1 tied)."""
    return _best_grade(
        lambda std: psi_scattered_operand_cost(a_dim, b_dim, levels, std),
        levels,
        lambda j: (7 ** (j - 1) - 4 ** (j - 1)) * (a_dim >> j) * (b_dim >> j),
    )


def best_decode_grade(m: int, n: int, levels: int):
    """Cheapest decode-lane grading, unchanged from tier 5."""
    return _best_grade(
        lambda std: graded_decode_cost(m, n, levels, std),
        levels,
        lambda j: (7 ** (j - 1) - 4 ** (j - 1)) * (m >> j) * (n >> j),
    )


def psi_scattered_depth_core_cost(m: int, k: int, n: int, levels: int) -> int:
    """Depth-L batched Winograd core under the cheapest per-lane grading."""
    block = 1 << levels
    if min(m, k, n) <= 0 or any(value % block for value in (m, k, n)):
        raise ValueError(f"{levels} Winograd levels require multiples of {block}")
    leaves = 7 ** levels * direct_cost(m // block, k // block, n // block)
    left, _ = best_operand_grade(m, k, levels)
    right, _ = best_operand_grade(k, n, levels)
    decode, _ = best_decode_grade(m, n, levels)
    return leaves + left + right + decode


def _depth_route(m: int, k: int, n: int, levels: int, direct_total: int):
    """Bill the core at this depth under the incumbent's fringe rule."""
    block = 1 << levels
    if m % block:
        return None
    core_k = k - k % block
    core_n = n - n % block
    if core_k == 0 or core_n == 0:
        return None
    inner_width = k - core_k
    output_width = n - core_n
    core = psi_scattered_depth_core_cost(m, core_k, core_n, levels)
    inner_correction = direct_cost(m, inner_width, core_n) if inner_width else 0
    inner_add = m * core_n if inner_width else 0
    output_tail = (
        direct_cost(m, k, output_width) + m * output_width
        if output_width
        else 0
    )
    total = core + inner_correction + inner_add + output_tail
    fringed = bool(inner_width or output_width)
    strategy = (
        f"winograd_l{levels}_psiscatter_mod{block}_fringe"
        if fringed
        else f"winograd_l{levels}_psiscatter"
    )
    return Bill(
        strategy, m, k, n, core_k, core_n, core,
        inner_correction, inner_add, output_tail, total, direct_total,
        1 + int(bool(inner_width)) + int(bool(output_width)),
    )


def psi_scattered_root_stacks_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Cheapest exact owned route over all lawful depths and all gradings.

    Supersedes ``level_graded_basis_candidate_bill``: same routes, same fringe
    policy, same dual-odd branch, same depth sweep, same gradings -- only the
    root-copy term of the operand lanes changes, and it changes downward at every
    depth and every grading, so no shape can regress against any ancestor.
    """
    baseline = owned_batched_candidate_bill(m, k, n)
    best = baseline

    # Incumbent's dual-odd branch, preserved unchanged.
    if m % 2 == 0 and k > 1 and n > 1 and k % 2 and n % 2:
        core_k = k - 1
        core_n = n - 1
        core = batched_winograd_core_cost(m, core_k, core_n)
        inner_correction = direct_cost(m, 1, core_n)
        inner_add = m * core_n + m
        output_tail = direct_cost(m, k, 1) + m
        total = core + inner_correction + inner_add + output_tail
        if total < best.total:
            best = Bill(
                "winograd_batched_owned_dual_odd", m, k, n, core_k, core_n,
                core, inner_correction, inner_add, output_tail, total,
                baseline.direct, 3,
            )

    levels = 2
    while (1 << levels) <= m and (1 << levels) <= min(k, n):
        route = _depth_route(m, k, n, levels, baseline.direct)
        if route is not None and route.total < best.total:
            best = route
        levels += 1
    return best


# Campaign-facing names.
level_graded_basis_candidate_bill = psi_scattered_root_stacks_candidate_bill
alternative_basis_candidate_bill = psi_scattered_root_stacks_candidate_bill
grouped_depth_candidate_bill = psi_scattered_root_stacks_candidate_bill
candidate_bill = psi_scattered_root_stacks_candidate_bill


# ---------------------------------------------------------------------------
# Executable exactness + accounting + placement verifier.
# Pure integers, so "exact" is literal and bit-for-bit.
# ---------------------------------------------------------------------------

PHI_A = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]]
PHI_B = [[1, 0, 0, 0], [-1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
PHI_C = [[1, 0, 0, 0], [0, 1, 0, -1], [0, 0, 1, 0], [0, 0, 0, 1]]
EYE = [[int(i == j) for j in range(4)] for i in range(4)]


def moved_slot(phi) -> int:
    """The single quadrant slot an elementary basis map rewrites."""
    moved = [i for i in range(4) if phi[i] != EYE[i]]
    assert len(moved) == 1, f"{moved} slots move; one write per node assumes one"
    assert phi[moved[0]][moved[0]] == 1, "moved slot must write in place"
    return moved[0]


def _quads(X):
    h = len(X) // 2
    w = len(X[0]) // 2
    return [
        [row[b * w:(b + 1) * w] for row in X[a * h:(a + 1) * h]]
        for a in (0, 1) for b in (0, 1)
    ]


def _join(q):
    h = len(q[0])
    w = len(q[0][0])
    out = [[0] * (2 * w) for _ in range(2 * h)]
    for idx, (ro, co) in enumerate(((0, 0), (0, w), (h, 0), (h, w))):
        for i in range(h):
            for j in range(w):
                out[ro + i][co + j] = q[idx][i][j]
    return out


def _lin(X, Y, sign):
    return [[X[i][j] + sign * Y[i][j] for j in range(len(X[0]))]
            for i in range(len(X))]


def _plain(A, B):
    return [[sum(A[i][t] * B[t][j] for t in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]


def _apply_phi(q, phi):
    h = len(q[0])
    w = len(q[0][0])
    out = []
    for row in phi:
        acc = [[0] * w for _ in range(h)]
        for t, coef in enumerate(row):
            if not coef:
                continue
            for i in range(h):
                for j in range(w):
                    acc[i][j] += coef * q[t][i][j]
        out.append(acc)
    return out


def _psi(X, phi, pattern, writes):
    """Graded basis change; one elementary slot rewrite per alternative node."""
    if not pattern:
        return X
    q = _quads(X)
    if pattern[0]:
        q = _apply_phi(q, phi)
        writes[0] += len(q[0]) * len(q[0][0])
    return _join([_psi(blk, phi, pattern[1:], writes) for blk in q])


def _psi_inverse(X, phi_inv, pattern, writes):
    if not pattern:
        return X
    q = [_psi_inverse(blk, phi_inv, pattern[1:], writes) for blk in _quads(X)]
    if pattern[0]:
        q = _apply_phi(q, phi_inv)
        writes[0] += len(q[0]) * len(q[0][0])
    return _join(q)


def _encode_left(t, alt):
    """The seven left operands, [A11, A12, S4, A22, S1, S2, S3] in both bases."""
    t1, t2, t3, t4 = t
    if alt:
        s2 = _lin(t3, t1, -1)
        s4 = _lin(t2, s2, -1)
        s3 = _lin(t4, s2, -1)
        return [t1, t2, s4, t4, t3, s2, s3], [s4, s2, s3]
    s1 = _lin(t3, t4, 1)
    s2 = _lin(s1, t1, -1)
    s3 = _lin(t1, t3, -1)
    s4 = _lin(t2, s2, -1)
    return [t1, t2, s4, t4, s1, s2, s3], [s1, s2, s3, s4]


def _encode_right(u, alt):
    """The seven right operands, [B11, B21, B22, T4, T1, T2, T3] in both bases."""
    u1, u2, u3, u4 = u
    if alt:
        t2 = _lin(u4, u2, -1)
        t3 = _lin(t2, u1, -1)
        t4 = _lin(t2, u3, -1)
        return [u1, u3, u4, t4, u2, t2, t3], [t4, t2, t3]
    t1 = _lin(u2, u1, -1)
    t2 = _lin(u4, t1, -1)
    t3 = _lin(u4, u2, -1)
    t4 = _lin(t2, u3, -1)
    return [u1, u3, u4, t4, t1, t2, t3], [t1, t2, t3, t4]


def _decode(M, alt, counters):
    """Alternative: six writes, slots (C11, C12-C22, C21, C22) = phi_C c.
    Standard: seven writes, slots (C11, C12, C21, C22) = c."""
    m1, m2, m3, m4, m5, m6, m7 = M
    area = len(m1) * len(m1[0])
    u2 = _lin(m1, m6, 1)
    u3 = _lin(u2, m7, 1)
    d1 = _lin(m1, m2, 1)
    d3 = _lin(u3, m4, -1)
    d4 = _lin(u3, m5, 1)
    if alt:
        d2 = _lin(m3, m7, -1)
        counters["decode"] += 6 * area
        return [d1, d2, d3, d4]
    u4 = _lin(u2, m5, 1)
    d2 = _lin(u4, m3, 1)
    counters["decode"] += 7 * area
    return [d1, d2, d3, d4]


def _alg(A, B, pa, pb, pc, counters):
    """Graded recursion on already-transformed operands."""
    if not pa:
        return _plain(A, B)
    left, left_arith = _encode_left(_quads(A), pa[0])
    right, right_arith = _encode_right(_quads(B), pb[0])
    counters["left"] += sum(len(x) * len(x[0]) for x in left_arith)
    counters["right"] += sum(len(x) * len(x[0]) for x in right_arith)
    M = [_alg(left[i], right[i], pa[1:], pb[1:], pc[1:], counters)
         for i in range(7)]
    return _join(_decode(M, pc[0], counters))


# --- write accounting, geometry and placement, on the same tree -------------


class _Node:
    """One operand-tree node plus the provenance the scatter schedule needs."""

    __slots__ = ("rows", "cols", "tag", "owner", "off", "born", "path")

    def __init__(self, rows, cols, tag, owner, off, born, path):
        self.rows = rows
        self.cols = cols
        self.tag = tag            # "root" | "arith" | "view"
        self.owner = owner
        self.off = off
        self.born = born          # level at which the owner block was written
        self.path = path          # quadrant path from the root, or None


def _block_geometry(rows, cols, path):
    """Absolute offset and size of the block a quadrant path names."""
    r = c = 0
    h, w = rows, cols
    for slot in path:
        h //= 2
        w //= 2
        r += (slot // 2) * h
        c += (slot % 2) * w
    return r, c, h, w


def _build_operands(rows, cols, pattern, side, sigma, writes, hosted,
                    psi_hosted):
    """Walk the operand tree, charging exactly what the schedule writes.

    A root-descended leaf is charged a copy only when no Psi write ever covers
    it; otherwise it is handed to the deepest Psi write that does, which places
    it for free.
    """
    root = _Node(rows, cols, "root", None, (0, 0), 0, ())
    root.owner = root
    nodes = [root]
    for level, alt in enumerate(pattern, start=1):
        out = []
        for parent in nodes:
            h = parent.rows // 2
            w = parent.cols // 2
            offs = [(0, 0), (0, w), (h, 0), (h, w)]
            if side == "A":
                order = ([("view", 0), ("view", 1), ("arith", None),
                          ("view", 3), ("view", 2), ("arith", None),
                          ("arith", None)]
                         if alt else
                         [("view", 0), ("view", 1), ("arith", None),
                          ("view", 3), ("arith", None), ("arith", None),
                          ("arith", None)])
            else:
                order = ([("view", 0), ("view", 2), ("view", 3),
                          ("arith", None), ("view", 1), ("arith", None),
                          ("arith", None)]
                         if alt else
                         [("view", 0), ("view", 2), ("view", 3),
                          ("arith", None), ("arith", None), ("arith", None),
                          ("arith", None)])
            slots = sorted(slot for tag, slot in order if tag == "view")
            assert slots == ([0, 1, 2, 3] if alt else
                             ([0, 1, 3] if side == "A" else [0, 2, 3])), slots
            # The slot Psi rewrites must be a free view exactly when the level
            # is alternative -- that is the whole hinge of this tier.
            assert (sigma in slots) == bool(alt), (
                f"moved slot {sigma} view-status {sigma in slots} "
                f"disagrees with alt={alt}")
            for tag, slot in order:
                if tag == "arith":
                    node = _Node(h, w, "arith", None, (0, 0), level, None)
                    node.owner = node
                    writes[0] += h * w
                else:
                    node = _Node(
                        h, w, "view", parent.owner,
                        (parent.off[0] + offs[slot][0],
                         parent.off[1] + offs[slot][1]),
                        parent.born,
                        None if parent.path is None else parent.path + (slot,),
                    )
                out.append(node)
        nodes = out
    copies = 0
    for leaf in nodes:
        if leaf.tag != "view":
            continue
        if leaf.owner.tag != "root":
            hosted.setdefault(id(leaf.owner), (leaf.owner, []))[1].append(
                (leaf.off[0], leaf.off[1], leaf.rows, leaf.cols)
            )
            continue
        touched = [j for j, (slot, alt)
                   in enumerate(zip(leaf.path, pattern), start=1)
                   if alt and slot == sigma]
        if not touched:
            writes[0] += leaf.rows * leaf.cols
            copies += 1
            continue
        deepest = touched[-1]
        psi_hosted.setdefault(leaf.path[:deepest], []).append(
            (leaf.off[0], leaf.off[1], leaf.rows, leaf.cols)
        )
    return nodes, copies


def _assert_scatter_is_free(hosted, pattern):
    """Tier 3's geometry: an owner's write can place all its leaves."""
    free_below = {}
    levels = len(pattern)
    for born in range(0, levels + 1):
        prod = 1
        for j in range(born + 1, levels + 1):
            prod *= 4 if pattern[j - 1] else 3
        free_below[born] = prod
    for owner, rects in hosted.values():
        covered = set()
        area = 0
        for r0, c0, hh, ww in rects:
            assert r0 >= 0 and c0 >= 0, "leaf rectangle starts outside its owner"
            assert r0 + hh <= owner.rows and c0 + ww <= owner.cols, (
                f"leaf rectangle {(r0, c0, hh, ww)} escapes owner "
                f"{(owner.rows, owner.cols)}"
            )
            for i in range(r0, r0 + hh):
                for j in range(c0, c0 + ww):
                    assert (i, j) not in covered, (
                        f"two leaves claim owner cell {(i, j)}"
                    )
                    covered.add((i, j))
            area += hh * ww
        leaf_area = rects[0][2] * rects[0][3]
        assert area == free_below[owner.born] * leaf_area, (
            "hosted leaf area must equal the grading's free-view product"
        )
        assert area <= owner.rows * owner.cols


def _assert_psi_scatter_is_free(psi_hosted, pattern, rows, cols, sigma):
    """This tier's load-bearing geometry, measured off the walk.

    For each Psi write that places leaves: the write really is a Psi write (its
    path ends at the moved slot on an alternative level), the leaves it places
    lie inside the block it writes, are pairwise disjoint, number exactly
    ``3**(L-j)``, and never exceed the write's area.  Per level the total placed
    area is checked against the level's whole Psi budget ``4**(j-1) * A_j``.
    """
    levels = len(pattern)
    per_level_area = {}
    for path, rects in psi_hosted.items():
        j = len(path)
        assert pattern[j - 1], f"Psi does not write at standard level {j}"
        assert path[-1] == sigma, (
            f"placing write at path {path} does not end at the moved slot")
        r0, c0, bh, bw = _block_geometry(rows, cols, path)
        covered = set()
        area = 0
        for lr, lc, lh, lw in rects:
            assert r0 <= lr and lr + lh <= r0 + bh, "leaf escapes the Psi block"
            assert c0 <= lc and lc + lw <= c0 + bw, "leaf escapes the Psi block"
            for i in range(lr, lr + lh):
                for jj in range(lc, lc + lw):
                    assert (i, jj) not in covered, "two leaves claim a Psi cell"
                    covered.add((i, jj))
            area += lh * lw
        assert len(rects) == 3 ** (levels - j), (
            f"Psi write at level {j} places {len(rects)} leaves, "
            f"expected {3 ** (levels - j)}")
        assert area <= bh * bw, "a Psi write cannot place more than it writes"
        per_level_area[j] = per_level_area.get(j, 0) + area
    for j, area in per_level_area.items():
        budget = 4 ** (j - 1) * (rows >> j) * (cols >> j)
        assert area <= budget, (
            f"level {j} places {area} but Psi only writes {budget}")


def _inverse(phi):
    """Integer inverse of a unimodular 4x4, by Gauss-Jordan over rationals."""
    n = 4
    M = [[(x, 1) for x in row] + [(int(i == j), 1) for j in range(n)]
         for i, row in enumerate(phi)]

    def sub(a, b):
        return (a[0] * b[1] - b[0] * a[1], a[1] * b[1])

    def mul(a, b):
        return (a[0] * b[0], a[1] * b[1])

    def div(a, b):
        return (a[0] * b[1], a[1] * b[0])

    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col][0])
        M[col], M[piv] = M[piv], M[col]
        f = M[col][col]
        M[col] = [div(x, f) for x in M[col]]
        for r in range(n):
            if r != col and M[r][col][0]:
                g = M[r][col]
                M[r] = [sub(x, mul(g, y)) for x, y in zip(M[r], M[col])]
    inv = []
    for i in range(n):
        row = []
        for j in range(n):
            num, den = M[i][n + j]
            assert num % den == 0, "phi is not unimodular"
            row.append(num // den)
        inv.append(row)
    return inv


def verify_schedule(m: int, k: int, n: int, pa, pb, pc, seed: int) -> None:
    """Assert the schedule is exact, that the bill matches its real writes lane
    by lane, and that every scattered placement -- arithmetic and Psi -- is
    legal."""
    levels = len(pa)
    assert len(pb) == levels and len(pc) == levels
    state = seed

    def nxt():
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return state % 19 - 9

    a = [[nxt() for _ in range(k)] for _ in range(m)]
    b = [[nxt() for _ in range(n)] for _ in range(k)]

    psi_a, psi_b, psi_c = [0], [0], [0]
    at = _psi(a, PHI_A, pa, psi_a)
    bt = _psi(b, PHI_B, pb, psi_b)

    counters = {"left": 0, "right": 0, "decode": 0}
    ct = _alg(at, bt, pa, pb, pc, counters)
    c = _psi_inverse(ct, _inverse(PHI_C), pc, psi_c)

    assert c == _plain(a, b), f"schedule is not exact at {(m, k, n, pa, pb, pc)}"

    def std_of(pattern):
        return frozenset(j for j, alt in enumerate(pattern, start=1) if not alt)

    def transform_bill(a_dim, b_dim, pattern):
        return sum(4 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
                   for j, alt in enumerate(pattern, start=1) if alt)

    assert psi_a[0] == transform_bill(m, k, pa)
    assert psi_b[0] == transform_bill(k, n, pb)
    assert psi_c[0] == transform_bill(m, n, pc)

    def arith_bill(a_dim, b_dim, pattern, alt_c, std_c):
        return sum(7 ** (j - 1) * (alt_c if alt else std_c)
                   * (a_dim >> j) * (b_dim >> j)
                   for j, alt in enumerate(pattern, start=1))

    assert counters["left"] == arith_bill(m, k, pa, 3, 4)
    assert counters["right"] == arith_bill(k, n, pb, 3, 4)
    assert counters["decode"] == arith_bill(m, n, pc, 6, 7)
    assert counters["decode"] + psi_c[0] == graded_decode_cost(
        m, n, levels, std_of(pc))

    for side, phi, (a_dim, b_dim), pattern in (
        ("A", PHI_A, (m, k), pa),
        ("B", PHI_B, (k, n), pb),
    ):
        sigma = moved_slot(phi)
        writes = [0]
        hosted: dict = {}
        placed: dict = {}
        _, copies = _build_operands(a_dim, b_dim, pattern, side, sigma,
                                    writes, hosted, placed)
        _assert_scatter_is_free(hosted, pattern)
        _assert_psi_scatter_is_free(placed, pattern, a_dim, b_dim, sigma)
        assert copies == 3 ** levels, (
            f"side {side} still copies {copies} leaves, expected {3 ** levels}")
        expected = (arith_bill(a_dim, b_dim, pattern, 3, 4)
                    + 3 ** levels * (a_dim >> levels) * (b_dim >> levels))
        assert writes[0] == expected, (
            f"side {side} stack bill {expected} != writes {writes[0]}")
        assert psi_scattered_operand_cost(
            a_dim, b_dim, levels, std_of(pattern)) == (
                writes[0] + transform_bill(a_dim, b_dim, pattern))


def _symbolic_encode_check() -> None:
    """Both bases must produce Winograd's own seven operands, symbolically."""

    def unit(i):
        return [[1 if j == i else 0 for j in range(4)]]

    want_a = [
        [1, 0, 0, 0],      # A11
        [0, 1, 0, 0],      # A12
        [1, 1, -1, -1],    # S4 = A11+A12-A21-A22
        [0, 0, 0, 1],      # A22
        [0, 0, 1, 1],      # S1 = A21+A22
        [-1, 0, 1, 1],     # S2 = -A11+A21+A22
        [1, 0, -1, 0],     # S3 = A11-A21
    ]
    want_b = [
        [1, 0, 0, 0],      # B11
        [0, 0, 1, 0],      # B21
        [0, 0, 0, 1],      # B22
        [1, -1, -1, 1],    # T4 = B11-B12-B21+B22
        [-1, 1, 0, 0],     # T1 = B12-B11
        [1, -1, 0, 1],     # T2 = B11-B12+B22
        [0, -1, 0, 1],     # T3 = B22-B12
    ]
    basis_vectors = [unit(i) for i in range(4)]
    for alt, phi_a, phi_b in ((True, PHI_A, PHI_B), (False, EYE, EYE)):
        left, _ = _encode_left(_apply_phi(basis_vectors, phi_a), alt)
        assert [row[0] for row in left] == want_a, (
            f"left encode is not Winograd's (alt={alt})")
        right, _ = _encode_right(_apply_phi(basis_vectors, phi_b), alt)
        assert [row[0] for row in right] == want_b, (
            f"right encode is not Winograd's (alt={alt})")

    products = [[[1 if j == i else 0 for j in range(7)]] for i in range(7)]
    counters = {"decode": 0}
    std = [row[0] for row in _decode(products, False, counters)]
    assert std == [
        [1, 1, 0, 0, 0, 0, 0],      # C11
        [1, 0, 1, 0, 1, 1, 0],      # C12
        [1, 0, 0, -1, 0, 1, 1],     # C21
        [1, 0, 0, 0, 1, 1, 1],      # C22
    ], "standard decode is not Winograd's"
    alt = [row[0] for row in _decode(products, True, counters)]
    assert alt[0] == std[0] and alt[2] == std[2] and alt[3] == std[3]
    assert alt[1] == [x - y for x, y in zip(std[1], std[3])], (
        "alternative decode slot 2 must be C12 - C22")


def _decode_floor_is_six() -> None:
    """Exhaustive: no phi_C reaches a five-write decode; six is the floor.

    Re-run here because it is the reason this tier attacks the copy lane rather
    than the decode lane.
    """
    def in_w(v):
        return (v[0] - v[1] - v[5] == 0 and v[3] - v[4] + v[5] == 0
                and v[2] - v[5] + v[6] == 0)

    for row in ((1, 1, 0, 0, 0, 0, 0), (1, 0, 1, 0, 1, 1, 0),
                (1, 0, 0, -1, 0, 1, 1), (1, 0, 0, 0, 1, 1, 1)):
        assert in_w(row)

    def canon(v):
        for x in v:
            if x > 0:
                return v
            if x < 0:
                return tuple(-y for y in v)
        return v

    def rank_of(vs):
        M = [list(v) for v in vs]
        r = 0
        for col in range(7):
            piv = next((i for i in range(r, len(M)) if M[i][col]), None)
            if piv is None:
                continue
            M[r], M[piv] = M[piv], M[r]
            p = M[r][col]
            for i in range(r + 1, len(M)):
                if M[i][col]:
                    f = M[i][col]
                    M[i] = [p * x - f * y for x, y in zip(M[i], M[r])]
            r += 1
            if r == len(M):
                break
        return r

    units = [tuple(1 if i == j else 0 for i in range(7)) for j in range(7)]

    def reachable(N):
        def dfs(t, avail, seen, wvecs, wrank):
            if wrank + (N - t) < 4:
                return False
            if t == N:
                return wrank == 4
            for i in range(len(avail)):
                ai = avail[i]
                for j in range(i, len(avail)):
                    aj = avail[j]
                    for s in (1, -1):
                        if i == j and s == -1:
                            continue
                        v = tuple(x + s * y for x, y in zip(ai, aj))
                        if not any(v):
                            continue
                        cv = canon(v)
                        if cv in seen:
                            continue
                        if in_w(cv):
                            nw = wvecs + [cv]
                            nr = rank_of(nw)
                            if nr == wrank:
                                nw, nr = wvecs, wrank
                        else:
                            nw, nr = wvecs, wrank
                        seen.add(cv)
                        avail.append(cv)
                        ok = dfs(t + 1, avail, seen, nw, nr)
                        avail.pop()
                        seen.discard(cv)
                        if ok:
                            return True
            return False

        return dfs(0, list(units), set(units), [], 0)

    for N in (4, 5):
        assert not reachable(N), f"a {N}-write decode exists; the floor is wrong"
    assert reachable(6), "the six-write decode must be reachable"


def _selfcheck() -> None:
    m, k, n = 4096, 256, 256

    # 1. the three basis maps are unimodular, integer-invertible, and each is a
    #    SINGLE elementary row operation -- which is what makes "the moved slot"
    #    well defined and the whole placement argument possible.
    for phi in (PHI_A, PHI_B, PHI_C):
        inv = _inverse(phi)
        prod = [[sum(phi[i][t] * inv[t][j] for t in range(4)) for j in range(4)]
                for i in range(4)]
        assert prod == EYE
        assert all(abs(x) <= 1 for row in phi for x in row)
        assert all(abs(x) <= 1 for row in inv for x in row)
        assert moved_slot(phi) == moved_slot(inv)
    assert _inverse(EYE) == EYE
    assert moved_slot(PHI_A) == 2 and moved_slot(PHI_B) == 1

    # 2. both bases produce Winograd's operands and reconstruct C, symbolically
    _symbolic_encode_check()

    # 3. the decode floor of six, re-derived exhaustively
    _decode_floor_is_six()

    # 4. the new operand formula differs from tier 5's by EXACTLY the copy lane,
    #    at every depth and every grading -- so nothing else can have moved.
    for levels in range(1, 9):
        for a_dim, b_dim in ((m, k), (k, n), (m, n)):
            leaf_area = (a_dim >> levels) * (b_dim >> levels)
            for size in range(levels + 1):
                for sub in combinations(range(1, levels + 1), size):
                    std = frozenset(sub)
                    delta = (tier5_graded_operand_cost(a_dim, b_dim, levels, std)
                             - psi_scattered_operand_cost(a_dim, b_dim,
                                                          levels, std))
                    assert delta == (3 ** size * 4 ** (levels - size)
                                     - 3 ** levels) * leaf_area, (
                        f"delta at L={levels} std={sorted(std)} is {delta}")
                    assert delta >= 0, "this tier may never bill more"

    # 5. lineage parity: the ancestors' published depth tables, digit for digit
    tier3_table = {
        1: 471711744, 2: 416567296, 3: 371653632, 4: 338169088,
        5: 319026624, 6: 320036176, 7: 351987132, 8: 434304253,
    }
    tier4_table = {
        1: 471990272, 2: 416649216, 3: 370777088, 4: 335053056,
        5: 311468480, 6: 304210704, 7: 321222236, 8: 376940289,
    }
    tier5_table = {
        1: 471711744, 2: 416370688, 3: 370498560, 4: 334774528,
        5: 311189952, 6: 303932176, 7: 320943708, 8: 376661761,
    }
    for levels, value in tier3_table.items():
        assert standard_depth_core_cost(m, k, n, levels) == value
    for levels, value in tier4_table.items():
        assert alt_basis_depth_core_cost(m, k, n, levels) == value

    def tier5_depth_core_cost(levels):
        block = 1 << levels
        leaves = 7 ** levels * direct_cost(m // block, k // block, n // block)
        left = min(tier5_graded_operand_cost(m, k, levels, frozenset(sub))
                   for size in range(levels + 1)
                   for sub in combinations(range(1, levels + 1), size))
        right = min(tier5_graded_operand_cost(k, n, levels, frozenset(sub))
                    for size in range(levels + 1)
                    for sub in combinations(range(1, levels + 1), size))
        decode, _ = best_decode_grade(m, n, levels)
        return leaves + left + right + decode

    for levels, value in tier5_table.items():
        assert tier5_depth_core_cost(levels) == value, (
            f"tier 5 at L={levels} reconstructs to "
            f"{tier5_depth_core_cost(levels)}, published {value}")

    # 6. the sorted grading selection must equal a brute force over all 2**L
    #    subsets, at every depth in the sweep and on every lane.
    for levels in range(1, 9):
        for a_dim, b_dim in ((m, k), (k, n)):
            brute = min(
                psi_scattered_operand_cost(a_dim, b_dim, levels, frozenset(sub))
                for size in range(levels + 1)
                for sub in combinations(range(1, levels + 1), size)
            )
            picked, _ = best_operand_grade(a_dim, b_dim, levels)
            assert picked == brute
        brute = min(
            graded_decode_cost(m, n, levels, frozenset(sub))
            for size in range(levels + 1)
            for sub in combinations(range(1, levels + 1), size)
        )
        picked, _ = best_decode_grade(m, n, levels)
        assert picked == brute

    # 7. no regression against any ancestor, at any depth
    for levels in range(1, 9):
        here = psi_scattered_depth_core_cost(m, k, n, levels)
        assert here <= tier5_depth_core_cost(levels)
        assert here <= alt_basis_depth_core_cost(m, k, n, levels)
        assert here <= standard_depth_core_cost(m, k, n, levels)
    assert psi_scattered_depth_core_cost(m, k, n, 6) < tier5_table[6]

    # 8. the grading flip this tier predicts: with the copy lane grading-blind,
    #    demoting level 1 is now exactly a tie and demoting level 2 a strict
    #    loss -- where tier 5 had them a strict win and a tie.
    for levels in range(2, 9):
        for a_dim, b_dim in ((m, k), (k, n)):
            allalt = psi_scattered_operand_cost(a_dim, b_dim, levels,
                                                frozenset())
            one = psi_scattered_operand_cost(a_dim, b_dim, levels,
                                             frozenset({1}))
            two = psi_scattered_operand_cost(a_dim, b_dim, levels,
                                             frozenset({1, 2}))
            assert allalt == one, "level 1 must be exactly tied"
            assert two > one, "level 2 must now be a strict loss"
            assert (tier5_graded_operand_cost(a_dim, b_dim, levels, frozenset())
                    > tier5_graded_operand_cost(a_dim, b_dim, levels,
                                                frozenset({1}))), (
                "tier 5's level-1 demotion was a strict win; the flip is real")

    # 9. executable exactness, write accounting, arithmetic-tree geometry and
    #    the new Psi placement, over several gradings including mixed ones.
    T, F = True, False
    for shape, pa, pb, pc in (
        ((8, 4, 4), [T, T], [T, T], [T, T]),
        ((8, 4, 4), [F, T], [F, T], [T, T]),
        ((8, 4, 4), [F, F], [F, F], [F, F]),
        ((16, 8, 8), [T, T, T], [T, T, T], [T, T, T]),
        ((16, 8, 8), [F, T, T], [F, T, T], [T, T, T]),
        ((16, 8, 8), [T, F, T], [F, T, F], [T, T, F]),
        ((8, 8, 8), [F, T, T], [T, F, T], [T, T, T]),
        ((32, 16, 16), [T, T, T, T], [T, T, T, T], [T, T, T, T]),
        ((32, 16, 16), [F, T, T, T], [F, T, T, T], [T, T, T, T]),
        ((64, 8, 8), [F, T, T], [T, T, F], [F, T, T]),
        ((16, 16, 8), [T, T, F], [F, F, T], [T, F, T]),
    ):
        verify_schedule(*shape, pa, pb, pc, seed=20260818)


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: exactness, both bases, decode floor, write accounting, "
          "grading optimality, arithmetic-tree geometry and Psi placement "
          "all pass")
    bill = psi_scattered_root_stacks_candidate_bill(4096, 256, 256)
    print(bill.to_dict())
    print("total:", bill.total)

    m, k, n = 4096, 256, 256
    best = 6
    left, sl = best_operand_grade(m, k, best)
    right, sr = best_operand_grade(k, n, best)
    decode, sd = best_decode_grade(m, n, best)
    print(f"breakdown of the selected core (L={best}):")
    print("  leaves        ",
          7 ** best * direct_cost(m >> best, k >> best, n >> best))
    print(f"  left operands  {left:>12}   standard levels {sorted(sl) or '[]'}")
    print(f"  right operands {right:>12}   standard levels {sorted(sr) or '[]'}")
    print(f"  decode         {decode:>12}   standard levels {sorted(sd) or '[]'}")
    print(f"  surviving copies: left {surviving_root_copies(m, k, best)}, "
          f"right {surviving_root_copies(k, n, best)}")
    for level in range(1, 9):
        try:
            print(f"  L={level} tier6={psi_scattered_depth_core_cost(m, k, n, level):>12}"
                  f"  alt={alt_basis_depth_core_cost(m, k, n, level):>12}"
                  f"  std={standard_depth_core_cost(m, k, n, level):>12}")
        except ValueError as exc:
            print(f"  L={level} unavailable: {exc}")
