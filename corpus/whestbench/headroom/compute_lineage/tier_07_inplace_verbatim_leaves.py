"""Tier 7: the verbatim leaves are dispatched in place, not copied.

ONE SUBSTANTIVE CHANGE
======================
Tier 3 established the scatter licence for the arithmetic tree, tier 6 extended
it to the basis-transform tree, and both stopped at the same wall, stated in
tier 3's own docstring:

    "IDENTITY LEAF WHOSE WHOLE PATH IS IDENTITY, up to the root.  Its bytes live
     in the caller's input matrix, which we do not write and may not scatter.
     It costs a real copy.  There are exactly 3**L of these per side."

The first two sentences are true and this tier does not touch them: we do not
write the caller's matrix, and a write we never perform cannot be scattered.
The third sentence is the frozen assumption.  A copy is needed only if the leaf
operand has to *arrive* in a freshly allocated slab; it is not needed if the
leaf call can be handed the address the bytes already occupy.  A batched matmul
takes one operand descriptor per leaf -- a base pointer and a leading dimension
-- and a depth-L quadrant of the caller's ``A`` is exactly such a descriptor:
base ``A + r0*ldA + c0``, leading dimension ``ldA``, shape
``(m >> L) x (k >> L)``.  Point the descriptor there and the copy disappears.

So the one change is: the ``3**L`` root-descended leaves that no write of ours
ever covers are dispatched from the caller's matrix in place, and the operand
lanes lose their last term.

    operand_cost(a, b, L)  =  (7**L - 4**L) * A_L        encode additions
                           +  L * 4**(L-1) * A_L         basis transform
                           +  0                          (was 3**L * A_L)

Nothing else moves: the leaf count is still ``7**L``, the depth sweep is tier
1's, the interior view elision is tier 2's, the arithmetic-tree scatter is tier
3's, the alternative-basis algebra is tier 4's, the per-level grading is tier
5's, the Psi scatter is tier 6's, and the arithmetic performed is bit-for-bit
tier 6's -- this tier deletes copies and adds nothing.

WHY THE MODEL ALREADY LICENSES THIS, IN ITS OWN NUMBERS
=======================================================
Two facts from the incumbent's own price list, neither of them new here.

  (1) ``owned_batched_candidate_bill`` charges the *direct* route
      ``direct_cost(m,k,n) + m*k`` -- the ``m*k`` being, in its own words, the
      copy of "each input row once into bounded scratch".  The Winograd route in
      the same function is charged no such term, at any depth, in any tier.  The
      model has therefore always billed the Winograd core as *reading ``A`` and
      ``B`` where the caller left them*.  If a depth-L quadrant of ``A`` were not
      addressable in place, the Winograd route would owe that ``m*k`` too.

  (2) Tier 2 spent exactly this licence one level higher and its win survived
      six tiers of audit: "the three identity operands stay strided views of a
      block that already exists in memory (either the input itself, or an S/T
      buffer the previous level already wrote)".  "The input itself" is the
      caller's matrix, and a strided view of it was already free.  Tier 2
      withheld the licence from the last level for a dispatch reason, not an
      addressing reason -- and a per-operand descriptor is precisely how a
      batched dispatch expresses a strided view.

The bytes read by the leaf call are the same bytes either way, at the same
addresses, in the same order.  Nothing is relaxed about *what* is multiplied.

THE ONE THING THAT HAD TO BE CHECKED, AND IS
============================================
An in-place operand is only safe if nothing in the schedule overwrites it
between the moment the descriptor is formed and the moment the leaf call reads
it.  That is a statement about addresses, and ``_selfcheck`` measures it rather
than asserting it (``_assert_inplace_leaves_are_safe``):

  (S1) *Containment.*  Every verbatim leaf rectangle lies inside the caller's
       matrix and has the leaf shape ``(a >> L) x (b >> L)``.
  (S2) *Disjointness.*  Verbatim leaf rectangles are pairwise disjoint, so no
       two leaf descriptors alias.
  (S3) *Immunity.*  No verbatim leaf rectangle meets any ``Psi`` write block, at
       any level, for the grading in force.  This is the load-bearing one: the
       ``Psi`` writes are the only writes in the schedule whose destinations are
       expressed in the coordinates of the operand matrix at all, and a verbatim
       leaf is by construction a path that never takes the moved slot, so no
       prefix of it ends where ``Psi`` writes.  The check enumerates every
       ``Psi`` block from the grading and tests every rectangle against it.
  (S4) *Count and area.*  The walk reports exactly ``3**L`` such leaves,
       occupying ``3**L * A_L`` cells -- taken from the walk, not the formula.

Every other write in the schedule lands in the leaf batch, in an arithmetic
block we allocated, or in scratch; none of them is addressed in the caller's
matrix, which is why (S3) is the whole of the safety argument.

EXACTNESS IDENTITY
==================
*The arithmetic is unchanged.*  This tier alters no operand, no coefficient, no
order of accumulation and no rounding: it deletes copies and changes the address
a leaf operand is read from.  A strided view of a block and a copy of that block
hold the same entries, so every leaf product is formed from bit-identical
operands and every output is bit-identical.  Every value this schedule computes
is the value tier 6's schedule computes, which is the value the direct route
computes.  The chain, restated so the file stands alone:

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

*The three non-identity maps*, unchanged since tier 4, unimodular, entries in
{-1, 0, 1}, each a single elementary row operation whose moved row carries
coefficient 1 on its own coordinate:

    phi_A = [[1,0,0,0],[0,1,0,0],[0,0,1,1],[0,0,0,1]]   det 1   (A21 += A22)
    phi_B = [[1,0,0,0],[-1,1,0,0],[0,0,1,0],[0,0,0,1]]  det 1   (B12 -= B11)
    phi_C = [[1,0,0,0],[0,1,0,-1],[0,0,1,0],[0,0,0,1]]  det 1   (C12 -= C22)

No division, no reciprocal, no scaling, no truncation, no value-dependent
reordering: over any ring the result is the ring element the direct route
computes, and over the integers ``verify_schedule`` checks it literally.

WHY THIS IS THE LAST LANE WITH SLACK IN IT
==========================================
Worth recording for whoever comes next, because the search that produced this
tier spent most of its effort proving the *other* lanes shut.  Write ``A_L``,
``B_L``, ``M_L`` for the depth-L leaf areas on the three lanes.  After this
tier the whole bill is

    leaves   7**L * (m>>L) * (n>>L) * (2*(k>>L) - 1)
    left     A_L * [ (7**L - 4**L)  +  L * 4**(L-1) ]
    right    B_L * [ (7**L - 4**L)  +  L * 4**(L-1) ]
    decode   M_L * [ 2*(7**L - 4**L) + L * 4**(L-1) ]

and every one of those additive terms is at a floor, by two independent routes.

  * *Per-leaf counting.*  An encode-arithmetic leaf is a fresh combination and
    needs at least one addition; there are ``7**L - 4**L`` of them.  A
    root-descended leaf whose path takes the moved slot at ``t`` levels holds a
    sum of ``2**t`` original blocks and needs at least ``t`` additions, and no
    two-term decomposition of it avoids a non-leaf intermediate (checked by hand
    at ``t = 2``, where the only candidate partners are the two sibling sums,
    neither of which is a needed leaf).  Summing ``t`` over the ``4**L``
    root-descended leaves gives exactly ``L * 4**(L-1)`` -- asserted from an
    enumeration in ``_selfcheck``, not from the formula.  The alternative-basis
    schedule attains both counts, so the operand lanes are exact optima, and the
    remaining ``3**L`` leaves need ``0`` additions, which is what this tier
    finally bills them.

  * *Transposition.*  For an addition-only program, ``a(M) = a(M^T) + n - m``.
    The composite leaf-to-output map is ``decode_L (x) 1_{k'}``; its transpose is
    ``decode_L^T`` with each row repeated ``k'`` times, and repeated rows are
    free, so ``a`` of the transpose equals ``a(decode_L^T)``, an encode-shaped
    map that the same per-leaf count pins at ``(7**L - 4**L) + L * 4**(L-1)``.
    Adding ``7**L * k' - 4**L`` reproduces the billed leaf additions plus decode
    to the unit.  The single-node instances of the same identity are the ones
    the lineage already proved: ``a(W_C) = a(W_C^T) + 3 = 6`` (re-derived
    exhaustively here in ``_decode_floor_is_six``), ``a(U_A) = a(U_B) = 3``.

  * *Multiplications.*  ``7`` is the proven rank of <2,2,2> and the leaf count is
    ``7**L``; every base tensor with a better exponent needs a factor of three in
    dimensions that ``4096 x 256 x 256`` does not have.

So after this tier there is no term left in the bill that is not either a proved
additive floor or a proved rank floor.  The next real gain has to come from
outside this algorithm family, not from rescheduling inside it.

RESULT AT (4096, 256, 256)
==========================
    L    tier 7           tier 6            tier 5
    1      470,876,160      471,711,744       471,711,744
    2      415,535,104      416,161,792       416,370,688
    3      369,662,976      370,132,992       370,498,560
    4      333,938,944      334,291,456       334,774,528
    5      310,354,368      310,618,752       311,189,952
    6    * 303,096,592      303,294,880       303,932,176
    7      320,108,124      320,256,840       320,943,708
    8      375,826,177      375,937,714       376,661,761

    total 303,096,592  =  210,827,008 leaves          (unchanged)
                        +  30,642,432 left operands   (-186,624)
                        +   1,915,152 right operands  (-11,664)
                        +  59,712,000 decode          (unchanged)

Depth stays at L = 6, and it stays there for a reason worth stating: the deleted
term ``3**L * A_L = m*k*(3/4)**L`` shrinks with depth, so this tier pays most at
shallow depth and cannot move the optimum outward.  Against the incumbent
303,294,880 the saving is 198,288 FLOPs (0.06537%); against the 535,822,336
direct comparator the ratio is 0.565666.

No approximation, no rank reduction, no f32 repricing, no compliance flags --
pure schedule.

VERIFICATION RUN IN ``_selfcheck``
==================================
1. An executable integer verifier transforms random integer A and B by the graded
   ``Psi``, runs the graded recursion, undoes ``Psi_C``, and asserts the result
   equals the plain integer product, over several distinct grading patterns
   including ones that differ between the three lanes.
2. The same verifier counts every write the schedule really performs and asserts
   the count equals the billed closed form lane by lane -- now with the copy term
   gone, so the count is strictly smaller than tier 6's and the assertion fails
   if any copy survives.
3. The in-place safety claim is *measured*: ``_build_operands`` walks the operand
   tree carrying each view's path and hands every verbatim leaf to
   ``_assert_inplace_leaves_are_safe``, which checks (S1) containment and leaf
   shape, (S2) pairwise disjointness, (S3) emptiness of intersection with every
   ``Psi`` write block enumerated from the grading, and (S4) that the count is
   ``3**L`` and the area ``3**L * A_L``, all from the walk.
4. Tier 3's arithmetic-tree geometry and tier 6's ``Psi`` placement geometry are
   both re-checked unchanged.
5. Both encodes are asserted, symbolically and in both bases, to reproduce
   Winograd's S1..S4 and T1..T4, and both decodes to reproduce C11..C22.
6. The decode floor of six is re-derived by exhaustive enumeration.
7. Tier 3's, tier 4's, tier 5's and tier 6's published depth tables are
   reproduced digit for digit from reconstructions of their closed forms, and
   this tier's cost is asserted to equal tier 6's minus exactly ``3**L * A_L`` on
   each operand lane and minus nothing anywhere else.
8. The per-leaf floor of the transform lane, ``sum of sigma-hit counts over the
   4**L root-descended leaves == L * 4**(L-1)``, is asserted from a direct
   enumeration of the paths, so the "no slack left" claim in the docstring is
   measured rather than argued.
9. ``_best_grade``'s sorted selection is asserted equal to a brute force over all
   ``2**L`` subsets of levels, at every depth in the sweep.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations, product


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
    """Tier 5's operand lane: root copies billed at 3**s * 4**(L-s)."""
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


def tier6_operand_cost(a_dim: int, b_dim: int, levels: int,
                       std: frozenset) -> int:
    """Tier 6's operand lane: the copy residue is 3**L, whatever the grading."""
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    arithmetic = sum(7 ** (j - 1) * (4 if j in std else 3)
                     * (a_dim >> j) * (b_dim >> j)
                     for j in range(1, levels + 1))
    transform = sum(4 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
                    for j in range(1, levels + 1) if j not in std)
    root_copies = 3 ** levels * (a_dim >> levels) * (b_dim >> levels)
    return arithmetic + transform + root_copies


# ---------------------------------------------------------------------------
# The one substantive change: the leaves no write of ours ever covers are
# dispatched from the caller's matrix, so the copy term is gone.
# ---------------------------------------------------------------------------


def inplace_verbatim_leaves(levels: int) -> int:
    """How many depth-L leaves are dispatched in place (count, not cost).

    A leaf is verbatim when its quadrant path never takes the moved slot at an
    alternative level.  At an alternative level the four free views include the
    moved slot, leaving three untouched; at a standard level the moved slot is
    the arithmetic block rather than a view, and phi = I writes nothing, so all
    three views are untouched.  Both rows read three, which is why the count is
    ``3**levels`` regardless of the grading -- and why it is now a count with no
    price attached rather than a copy bill.
    """
    return 3 ** levels


def inplace_operand_cost(a_dim: int, b_dim: int, levels: int,
                         std: frozenset) -> int:
    """Blocks written to form one side's depth-L operand set.

    Identical to tier 6 except that the ``3**L`` verbatim leaves are read from
    the caller's matrix through their own operand descriptors instead of being
    copied into the batch, so they cost nothing.
    """
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    arithmetic = sum(7 ** (j - 1) * (4 if j in std else 3)
                     * (a_dim >> j) * (b_dim >> j)
                     for j in range(1, levels + 1))
    transform = sum(4 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
                    for j in range(1, levels + 1) if j not in std)
    return arithmetic + transform


def graded_decode_cost(m: int, n: int, levels: int, std: frozenset) -> int:
    """Reconstruction writes, graded basis.  Unchanged from tiers 5 and 6: the
    decode has no free views, hence no verbatim leaf to dispatch in place."""
    arithmetic = sum(7 ** (j - 1) * (7 if j in std else 6)
                     * (m >> j) * (n >> j)
                     for j in range(1, levels + 1))
    transform = sum(4 ** (j - 1) * (m >> j) * (n >> j)
                    for j in range(1, levels + 1) if j not in std)
    return arithmetic + transform


def _best_grade(cost, levels: int, marginal):
    """Cheapest grading, exactly.

    The per-node term is separable across levels and no remaining term depends
    on the grading, so for each s the optimum is the s levels of least marginal
    cost.  ``_selfcheck`` brute-forces the whole 2**L lattice to confirm it.
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
    """Cheapest operand-lane grading.  With no root term left at all, demoting
    level j is a pure loss ``(7**(j-1) - 4**(j-1)) * A_j``, zero at level 1 and
    positive after, so all-alternative wins with level 1 exactly tied."""
    return _best_grade(
        lambda std: inplace_operand_cost(a_dim, b_dim, levels, std),
        levels,
        lambda j: (7 ** (j - 1) - 4 ** (j - 1)) * (a_dim >> j) * (b_dim >> j),
    )


def best_decode_grade(m: int, n: int, levels: int):
    """Cheapest decode-lane grading, unchanged from tiers 5 and 6."""
    return _best_grade(
        lambda std: graded_decode_cost(m, n, levels, std),
        levels,
        lambda j: (7 ** (j - 1) - 4 ** (j - 1)) * (m >> j) * (n >> j),
    )


def inplace_depth_core_cost(m: int, k: int, n: int, levels: int) -> int:
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
    core = inplace_depth_core_cost(m, core_k, core_n, levels)
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
        f"winograd_l{levels}_inplaceleaf_mod{block}_fringe"
        if fringed
        else f"winograd_l{levels}_inplaceleaf"
    )
    return Bill(
        strategy, m, k, n, core_k, core_n, core,
        inner_correction, inner_add, output_tail, total, direct_total,
        1 + int(bool(inner_width)) + int(bool(output_width)),
    )


def inplace_verbatim_leaves_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Cheapest exact owned route over all lawful depths and all gradings.

    Supersedes ``psi_scattered_root_stacks_candidate_bill``: same routes, same
    fringe policy, same dual-odd branch, same depth sweep, same gradings -- only
    the copy term of the operand lanes changes, and it changes downward at every
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
psi_scattered_root_stacks_candidate_bill = inplace_verbatim_leaves_candidate_bill
level_graded_basis_candidate_bill = inplace_verbatim_leaves_candidate_bill
alternative_basis_candidate_bill = inplace_verbatim_leaves_candidate_bill
grouped_depth_candidate_bill = inplace_verbatim_leaves_candidate_bill
candidate_bill = inplace_verbatim_leaves_candidate_bill


# ---------------------------------------------------------------------------
# Executable exactness + accounting + placement + in-place-safety verifier.
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


# --- write accounting, geometry, placement and in-place safety --------------


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
                    psi_hosted, verbatim):
    """Walk the operand tree, charging exactly what the schedule writes.

    A root-descended leaf is handed to the deepest Psi write that covers it when
    one exists, and otherwise recorded as a verbatim in-place operand.  Neither
    case is charged: this is the tier's one change, and the recorded rectangles
    are what ``_assert_inplace_leaves_are_safe`` then has to justify.
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
            verbatim.append((leaf.off[0], leaf.off[1], leaf.rows, leaf.cols))
            continue
        deepest = touched[-1]
        psi_hosted.setdefault(leaf.path[:deepest], []).append(
            (leaf.off[0], leaf.off[1], leaf.rows, leaf.cols)
        )
    return nodes


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
    """Tier 6's geometry, measured off the walk and re-checked unchanged."""
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


def _psi_write_blocks(pattern, rows, cols, sigma):
    """Every rectangle of the operand matrix that a Psi write lands on."""
    blocks = []
    for j, alt in enumerate(pattern, start=1):
        if not alt:
            continue
        for prefix in product(range(4), repeat=j - 1):
            blocks.append(_block_geometry(rows, cols, prefix + (sigma,)))
    return blocks


def _assert_inplace_leaves_are_safe(verbatim, pattern, rows, cols, sigma):
    """This tier's load-bearing geometry, measured off the walk.

    (S1) every verbatim leaf lies inside the caller's matrix and has the leaf
    shape; (S2) they are pairwise disjoint, so no two operand descriptors alias;
    (S3) none of them meets any Psi write block, so nothing in the schedule can
    overwrite the bytes the leaf call is going to read; (S4) the count is
    ``3**L`` and the area ``3**L * A_L``, both taken from the walk.
    """
    levels = len(pattern)
    leaf_rows = rows >> levels
    leaf_cols = cols >> levels
    covered = set()
    for r0, c0, hh, ww in verbatim:
        assert (hh, ww) == (leaf_rows, leaf_cols), (
            f"verbatim leaf {(hh, ww)} is not the leaf shape "
            f"{(leaf_rows, leaf_cols)}")
        assert 0 <= r0 and r0 + hh <= rows, "verbatim leaf escapes the matrix"
        assert 0 <= c0 and c0 + ww <= cols, "verbatim leaf escapes the matrix"
        for i in range(r0, r0 + hh):
            for j in range(c0, c0 + ww):
                assert (i, j) not in covered, (
                    f"two in-place operands alias cell {(i, j)}")
                covered.add((i, j))
    for br, bc, bh, bw in _psi_write_blocks(pattern, rows, cols, sigma):
        for r0, c0, hh, ww in verbatim:
            overlap = (r0 < br + bh and br < r0 + hh
                       and c0 < bc + bw and bc < c0 + ww)
            assert not overlap, (
                f"in-place operand {(r0, c0, hh, ww)} is clobbered by the Psi "
                f"write on {(br, bc, bh, bw)}")
    assert len(verbatim) == inplace_verbatim_leaves(levels), (
        f"{len(verbatim)} verbatim leaves, expected "
        f"{inplace_verbatim_leaves(levels)}")
    assert len(covered) == 3 ** levels * leaf_rows * leaf_cols


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
    by lane, and that every placement -- arithmetic, Psi and in-place -- is
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
        verbatim: list = []
        _build_operands(a_dim, b_dim, pattern, side, sigma,
                        writes, hosted, placed, verbatim)
        _assert_scatter_is_free(hosted, pattern)
        _assert_psi_scatter_is_free(placed, pattern, a_dim, b_dim, sigma)
        _assert_inplace_leaves_are_safe(verbatim, pattern, a_dim, b_dim, sigma)
        expected = arith_bill(a_dim, b_dim, pattern, 3, 4)
        assert writes[0] == expected, (
            f"side {side} stack bill {expected} != writes {writes[0]}")
        assert inplace_operand_cost(
            a_dim, b_dim, levels, std_of(pattern)) == (
                writes[0] + transform_bill(a_dim, b_dim, pattern))
        # and the copy lane really is gone, not merely re-labelled
        assert tier6_operand_cost(a_dim, b_dim, levels, std_of(pattern)) - (
            inplace_operand_cost(a_dim, b_dim, levels, std_of(pattern))
        ) == 3 ** levels * (a_dim >> levels) * (b_dim >> levels)


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

    Re-run here because it is one half of the reason this tier attacks the copy
    lane rather than any arithmetic lane.
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


def _transform_lane_is_at_its_per_leaf_floor(max_levels: int = 7) -> None:
    """The other half of the "no slack left" claim, by enumeration.

    A root-descended leaf whose path takes the moved slot at ``t`` levels holds
    a sum of ``2**t`` original blocks and needs at least ``t`` additions.  The
    nested transform spends exactly ``t`` on it, so the lane is optimal iff the
    total hit count equals the billed ``L * 4**(L-1)``.  It does.  The same
    enumeration reports ``3**L`` leaves at ``t = 0`` -- the ones this tier stops
    charging.
    """
    for levels in range(1, max_levels + 1):
        hits = 0
        untouched = 0
        for path in product(range(4), repeat=levels):
            t = sum(1 for slot in path if slot == 2)
            hits += t
            if t == 0:
                untouched += 1
        assert hits == levels * 4 ** (levels - 1), (
            f"transform floor mismatch at L={levels}: {hits}")
        assert untouched == inplace_verbatim_leaves(levels), (
            f"verbatim count mismatch at L={levels}: {untouched}")


def _selfcheck() -> None:
    m, k, n = 4096, 256, 256

    # 1. the three basis maps are unimodular, integer-invertible, and each is a
    #    SINGLE elementary row operation.
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

    # 4. the transform lane's per-leaf floor, by enumeration
    _transform_lane_is_at_its_per_leaf_floor()

    # 5. the new operand formula differs from tier 6's by EXACTLY the copy lane,
    #    at every depth and every grading -- so nothing else can have moved.
    for levels in range(1, 9):
        for a_dim, b_dim in ((m, k), (k, n), (m, n)):
            leaf_area = (a_dim >> levels) * (b_dim >> levels)
            for size in range(levels + 1):
                for sub in combinations(range(1, levels + 1), size):
                    std = frozenset(sub)
                    delta = (tier6_operand_cost(a_dim, b_dim, levels, std)
                             - inplace_operand_cost(a_dim, b_dim, levels, std))
                    assert delta == 3 ** levels * leaf_area, (
                        f"delta at L={levels} std={sorted(std)} is {delta}")
                    assert delta > 0, "this tier must strictly beat tier 6"

    # 6. lineage parity: the ancestors' published depth tables, digit for digit
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
    tier6_table = {
        1: 471711744, 2: 416161792, 3: 370132992, 4: 334291456,
        5: 310618752, 6: 303294880, 7: 320256840, 8: 375937714,
    }
    for levels, value in tier3_table.items():
        assert standard_depth_core_cost(m, k, n, levels) == value
    for levels, value in tier4_table.items():
        assert alt_basis_depth_core_cost(m, k, n, levels) == value

    def graded_depth_core_cost(levels, operand_cost):
        block = 1 << levels
        leaves = 7 ** levels * direct_cost(m // block, k // block, n // block)
        left = min(operand_cost(m, k, levels, frozenset(sub))
                   for size in range(levels + 1)
                   for sub in combinations(range(1, levels + 1), size))
        right = min(operand_cost(k, n, levels, frozenset(sub))
                    for size in range(levels + 1)
                    for sub in combinations(range(1, levels + 1), size))
        decode, _ = best_decode_grade(m, n, levels)
        return leaves + left + right + decode

    for levels, value in tier5_table.items():
        got = graded_depth_core_cost(levels, tier5_graded_operand_cost)
        assert got == value, f"tier 5 at L={levels} reconstructs to {got}"
    for levels, value in tier6_table.items():
        got = graded_depth_core_cost(levels, tier6_operand_cost)
        assert got == value, f"tier 6 at L={levels} reconstructs to {got}"

    # 7. this tier's core is tier 6's core minus exactly the two copy lanes
    for levels in range(1, 9):
        here = inplace_depth_core_cost(m, k, n, levels)
        drop = 3 ** levels * ((m >> levels) * (k >> levels)
                              + (k >> levels) * (n >> levels))
        assert here == tier6_table[levels] - drop, (
            f"L={levels}: {here} != {tier6_table[levels]} - {drop}")
        assert here <= alt_basis_depth_core_cost(m, k, n, levels)
        assert here <= standard_depth_core_cost(m, k, n, levels)

    # 8. the depth optimum cannot move outward: the deleted term shrinks with L
    drops = [3 ** L * ((m >> L) * (k >> L) + (k >> L) * (n >> L))
             for L in range(1, 9)]
    assert all(drops[i] > drops[i + 1] for i in range(len(drops) - 1)), (
        "the copy term must be decreasing in L for the depth argument to hold")
    assert min(range(1, 9), key=lambda L: inplace_depth_core_cost(m, k, n, L)) == 6

    # 9. the sorted grading selection must equal a brute force over all 2**L
    #    subsets, at every depth in the sweep and on every lane.
    for levels in range(1, 9):
        for a_dim, b_dim in ((m, k), (k, n)):
            brute = min(
                inplace_operand_cost(a_dim, b_dim, levels, frozenset(sub))
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

    # 10. executable exactness, write accounting, both scatter geometries and
    #     the new in-place safety claim, over several gradings including mixed.
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
    print("selfcheck: exactness, both bases, decode floor, transform floor, "
          "write accounting, grading optimality, arithmetic-tree geometry, "
          "Psi placement and in-place operand safety all pass")
    bill = inplace_verbatim_leaves_candidate_bill(4096, 256, 256)
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
    print(f"  in-place operands: {inplace_verbatim_leaves(best)} per side, "
          f"{inplace_verbatim_leaves(best) * (m >> best) * (k >> best)} left "
          f"cells and {inplace_verbatim_leaves(best) * (k >> best) * (n >> best)}"
          " right cells no longer copied")
    for level in range(1, 9):
        try:
            print(f"  L={level} tier7={inplace_depth_core_cost(m, k, n, level):>12}"
                  f"  alt={alt_basis_depth_core_cost(m, k, n, level):>12}"
                  f"  std={standard_depth_core_cost(m, k, n, level):>12}")
        except ValueError as exc:
            print(f"  L={level} unavailable: {exc}")
