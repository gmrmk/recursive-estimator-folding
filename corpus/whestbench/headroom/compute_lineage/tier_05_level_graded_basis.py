"""Tier 5: the basis is a per-level parameter, not one global choice.

ONE SUBSTANTIVE CHANGE
======================
Tier 1 unfroze the recursion depth: the incumbent had hard-coded two Winograd
levels, and sweeping ``L`` was worth 82 MFLOPs.  Tier 4 introduced a second
frozen constant without noticing it -- it picks ONE basis, ``phi``, and uses it
at *every* level of the recursion, then bills the all-alternative tree against
the all-standard tree and keeps the cheaper whole.  Nothing in the algebra
requires that.  ``Psi`` is a composition of per-level maps, and each level's map
is free to be a different element of GL_4 -- including the identity.

The one change here is to unfreeze that constant the same way tier 1 unfroze
depth: the basis becomes a *level-indexed family* ``(phi^(1), ..., phi^(L))``,
swept per lane, and the recursion keeps the cheapest grading.  Tier 4's route is
the member with every level alternative; tier 3's route is the member with every
level the identity.  The family strictly contains both, so no shape can regress
against either ancestor.

Nothing else moves: the leaf count is still 7**L, the depth sweep is tier 1's,
the interior view elision is tier 2's, the scatter licence is tier 3's, the
alternative-basis algebra at an alternative level is tier 4's, verbatim.

WHY A GRADED BASIS IS CHEAPER THAN EITHER PURE ONE
==================================================
Each lane pays three things, and only the first two are per-node.  Write
``A_j = (a>>j)(b>>j)`` for a level-j block area.  At level j the lane pays

    arithmetic operands   7**(j-1) * c_j * A_j      c_j = 3 alternative, 4 standard
    basis change             4**(j-1) * A_j         charged only at alternative levels
    root copies              F * A_L                F = product of the free-view counts

An alternative level buys ``c_j`` down from 4 to 3 -- worth ``7**(j-1) * A_j`` --
and pays ``4**(j-1) * A_j`` for the transform.  That trade is a *strict win from
level 2 on* and *exactly break-even at level 1*, where ``7**0 = 4**0 = 1``.

But the third term is not per-node, and tier 4 never priced it against the first
two.  The all-identity leaves tile the transformed matrix by branching four ways
per alternative level and only three ways per standard level, so

    F = 3**s * 4**(L-s)          s = number of standard levels,

and every level demoted to the identity multiplies the root lane by 3/4.  At
level 1 that demotion is free on the per-node side and worth ``ab/4`` on the root
side.  So the graded optimum is not "all alternative" -- it is "alternative
everywhere except the top", and the difference is exactly the quarter of the
root lane that tier 4 pays for a level-1 transform that buys it nothing:

    left  lane  31,691,008 -> 31,428,864      saving  262,144 = m*k/4
    right lane   1,980,688 ->  1,964,304      saving   16,384 = k*n/4
    decode lane 59,712,000 -> 59,712,000      unchanged: no root term to save
                                              -------
                                              278,528

Level 2 is the exact break-even of the same trade (``(7-4)*A_2 = 3ab/16`` against
a root saving of ``3ab/16``), which is why the sweep reports s=1 and s=2 tied and
s>=3 strictly worse.  ``_best_grade`` therefore does not assume a prefix; it
sorts the levels by their marginal cost and takes the cheapest s of them, and
``_selfcheck`` brute-forces all 2**L subsets to confirm the sort is exact.

The decode lane has no root-copy term -- every one of its four outputs is
written, none is a free view -- so its graded optimum is all-alternative, with
level 1 tied.  That asymmetry between the operand lanes and the decode lane is
the whole content of this tier, and it is invisible to any scheme that picks one
basis for the whole tree.

EXACTNESS IDENTITY
==================
The billed arithmetic is Winograd's seven-multiplication form of the 2x2 block
product,

    S1 = A21 + A22    T1 = B12 - B11
    S2 = S1  - A11    T2 = B22 - T1
    S3 = A11 - A21    T3 = B22 - B12
    S4 = A12 - S2     T4 = T2  - B21

    M1 = A11 * B11    M2 = A12 * B21    M3 = S4 * B22    M4 = A22 * T4
    M5 = S1  * T1     M6 = S2  * T2     M7 = S3  * T3

    C11 = M1 + M2                 C12 = M1 + M3 + M5 + M6
    C21 = M1 - M4 + M6 + M7       C22 = M1 + M5 + M6 + M7

which expands term by term to C11 = A11 B11 + A12 B21, C12 = A11 B12 + A12 B22,
C21 = A21 B11 + A22 B21, C22 = A21 B12 + A22 B22 -- the block product.  Write it
as ``c = W_C ((U_A a) * (U_B b))`` on the quadrant vectors.  For ANY invertible
phi_A, phi_B, phi_C,

    (phi_C c) = (phi_C W_C) ( (U_A phi_A^-1)(phi_A a) * (U_B phi_B^-1)(phi_B b) )

is the same computation read in new coordinates; the cost of a lane depends on
exactly one phi, so the three gradings are independent.  Taking phi = I recovers
the standard basis, so "standard" and "alternative" are two members of one
family, not two algorithms.

*The level-indexed transform.*  Given a family ``(phi^(1), ..., phi^(L))`` define

    Psi^(L+1..L)(A) = A
    Psi^(j..L)(A)   = the matrix whose four quadrant slots hold
                      Psi^(j+1..L) of the four outputs of phi^(j) on A's quadrants

Psi is linear, being a composition of blockwise linear maps.

*Claim.*  ``ALG^(1..L)( Psi_A^(1..L)(A), Psi_B^(1..L)(B) ) = Psi_C^(1..L)(A B)``,
where ``ALG^(j..L)`` is the recursion that at its top uses the encodes
``U_A (phi_A^(j))^-1``, ``U_B (phi_B^(j))^-1`` and the decode
``phi_C^(j) W_C``, and recurses with the family from j+1.

*Proof, by induction on L-j+1.*  For L-j+1 = 0 both sides are a plain product.
For the step: the four quadrant slots of ``Psi_A^(j..L)(A)`` hold
``Psi_A^(j+1..L)(t_p)`` where ``t = phi_A^(j) a``.  Operand i of the top node is

    sum_p (U_A (phi_A^(j))^-1)_ip Psi_A^(j+1..L)(t_p)
        = Psi_A^(j+1..L)( sum_p (U_A (phi_A^(j))^-1)_ip t_p )        [linearity]
        = Psi_A^(j+1..L)( (U_A (phi_A^(j))^-1 phi_A^(j) a)_i )
        = Psi_A^(j+1..L)( (U_A a)_i ),

which is precisely the correctly transformed operand for the remaining L-j
levels; the same computation on the right gives ``Psi_B^(j+1..L)((U_B b)_i)``.
By the induction hypothesis the recursive call returns ``Psi_C^(j+1..L)(M_i)``,
and linearity of Psi_C gives output slot p as
``Psi_C^(j+1..L)( (phi_C^(j) W_C M)_p ) = Psi_C^(j+1..L)( (phi_C^(j) c)_p )``,
which is by definition slot p of ``Psi_C^(j..L)(c)``.  Undoing ``Psi_C^(1..L)``
at the end returns A B exactly.  No transform ever occurs *inside* the
recursion, which is why the transform tree branches four ways and not seven.

Setting ``phi^(j) = I`` at some levels changes nothing in that induction --
``I`` is invertible and ``U_A I^-1 = U_A`` -- so a graded family is exact for the
same reason a uniform one is.

*The three non-identity maps*, unchanged from tier 4 and unimodular with entries
in {-1, 0, 1}:

    phi_A = [[1,0,0,0],[0,1,0,0],[0,0,1,1],[0,0,0,1]]   det  1   (A21 += A22)
    phi_B = [[1,0,0,0],[-1,1,0,0],[0,0,1,0],[0,0,0,1]]  det  1   (B12 -= B11)
    phi_C = [[1,0,0,0],[0,1,0,-1],[0,0,1,0],[0,0,0,1]]  det  1   (C12 -= C22)

Each is a single elementary row operation whose moved row carries coefficient 1
on its own coordinate, so the transform is one in-place quadrant write per node
and the inverse is the same shape.  No division, no reciprocal, no scaling, no
truncation, no value-dependent reordering: over any ring the result is the ring
element the direct route computes, and over the integers ``verify_schedule``
checks it literally.

TIER 4'S OPEN LEAD, CLOSED
==========================
Tier 4 left one lead: "the search that would settle whether *some* other basis
reaches five [decode writes] ... did not run to completion here and is left
open."  It is settled here, negatively, by two independent arguments, and
``_decode_floor_is_six`` runs the first of them:

1. *Exhaustive.*  Choosing phi_C is exactly choosing four independent vectors
   spanning the row space W of W_C, and a decode schedule is a straight-line
   +/- program computing them from the seven unit vectors (the products M1..M7
   are free).  ``_decode_floor_is_six`` enumerates every such program of length
   <= 5 -- with the sound pruning that a program of length N can raise the rank
   inside W by at most one per step, and that recomputing an already-available
   vector or its negation is never useful -- and finds none.  It then exhibits a
   6-step program, so 6 is the exact floor.  (315,022 nodes visited to refute 5;
   ~1.3 s.)

2. *Structural.*  By the transposition principle for linear +/- circuits, an
   m-by-n matrix M and its transpose satisfy a(M^T) = a(M) + m - n.  The decode
   is 4-by-7, so a(W) = a(W^T) + 3, and W^T is 7-by-4 -- an encode-shaped map.
   An encode-shaped map has at most 4 unit rows (phi has only 4 rows, and the
   seven columns of W_C are pairwise distinct so no two rows of W^T can share a
   unit), hence at least 3 of its 7 rows cost a write: a(W^T) >= 3, so
   a(W) >= 6.  The same argument gives a(U_A), a(U_B) >= 3, both attained.

So the per-node constant 3 + 3 + 6 = 12 is the exact floor for <2,2,2;7> in any
basis, and it cannot be redistributed either: the "+3" is structurally welded to
the 7-inputs-4-outputs lane, which is always the *output* lane of area m*n.
The linear overhead of this algorithm family is therefore closed, and this tier
takes the only lane left open -- the root-copy term, which is not per-node and
which no per-node argument prices.

RESULT AT (4096, 256, 256)
==========================
    L    graded          tier 4 (uniform alt)   tier 3 (uniform std)
    1      471,711,744        471,990,272           471,711,744
    2      416,370,688        416,649,216           416,567,296
    3      370,498,560        370,777,088           371,653,632
    4      334,774,528        335,053,056           338,169,088
    5      311,189,952        311,468,480           319,026,624
    6    * 303,932,176        304,210,704           320,036,176
    7      320,943,708        321,222,236           351,987,132
    8      376,661,761        376,940,289           434,304,253

    total 303,932,176  =  210,827,008 leaves          (unchanged)
                        +  31,428,864 left operands   (-262,144)
                        +   1,964,304 right operands  (-16,384)
                        +  59,712,000 decode          (unchanged)

The selected grading is: left lane standard at level 1 and alternative at levels
2-6; right lane the same; decode alternative at every level.  Depth stays at
L = 6.  Against the incumbent 304,210,704 the saving is 278,528 FLOPs (0.0916%);
against the 535,822,336 direct comparator the ratio is 0.567225.

The saving is small because it is the last of its kind: with the per-node
constant proved minimal above, ``m*k/4 + k*n/4`` is the entire remaining slack in
the overhead lanes of this family.  What is left is the leaf lane -- 210,827,008,
now 69.4% of the bill and untouched since tier 0 -- where rank 7 is optimal for
<2,2,2> (Winograd's lower bound), so the next order of magnitude has to come from
a base case that is not a 2x2 block product at all.

No approximation, no rank reduction, no f32 repricing, no compliance flags --
pure schedule.

VERIFICATION RUN IN ``_selfcheck``
==================================
1. An executable integer verifier transforms random integer A and B by the
   *graded* Psi, runs the graded recursion, undoes Psi_C, and asserts the result
   equals the plain integer product -- over several distinct grading patterns,
   including mixed ones where the three lanes are graded differently from each
   other.  Over the integers "exact" is literal and bit-for-bit.
2. The same verifier counts every write the schedule really performs -- one per
   element of every transform step, of every arithmetic operand at every level,
   of every root-descended identity leaf, and of every decode write -- and
   asserts the count equals the billed closed form, lane by lane, for each
   grading.  The bill is measured off the schedule, not asserted about it.
3. It asserts the geometry: for every owner block the leaf rectangles it hosts
   are pairwise disjoint, lie inside its bounds, and cover exactly the area the
   grading predicts (a full tiling only when every level below the owner is
   alternative).  This is the check that fails if the scatter were not free.
4. Both encodes are asserted, symbolically and in both bases, to reproduce
   Winograd's S1..S4 and T1..T4, and both decodes to reproduce C11, C12, C21,
   C22 -- so a typo in either basis cannot pass.
5. The graded lane formulas are asserted to reduce to tier 4's closed forms at
   the all-alternative grading and to tier 3's at the all-identity grading, and
   tier 3's and tier 4's published depth tables are reproduced digit for digit
   from those reductions.
6. ``_best_grade``'s sorted selection is asserted equal to a brute-force minimum
   over all 2**L subsets of levels, at every depth in the sweep.
7. The decode floor of six is re-derived by exhaustive enumeration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations


# ---------------------------------------------------------------------------
# Helpers copied verbatim from the lineage (self-contained by rule 7).
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


# Ancestor closed forms, reproduced (never imported, rule 7) so the graded
# formulas can be asserted to reduce to them at the two pure gradings.


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


# ---------------------------------------------------------------------------
# The one substantive change: the basis becomes a level-indexed parameter.
# ``std`` is the frozenset of levels (1-indexed) that use phi = I.
# ---------------------------------------------------------------------------


def graded_operand_cost(a_dim: int, b_dim: int, levels: int,
                        std: frozenset) -> int:
    """Blocks written to form one side's depth-L operand set, graded basis.

    An alternative level has four free views of transformed quadrant slots and
    three arithmetic blocks, and pays one transform write per node of the 4-ary
    tree.  A standard level (phi = I) has three free views and four arithmetic
    blocks, and pays no transform.  The all-identity leaves branch by the free
    count, so the root-copy tile is the product of those counts.
    """
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


def graded_decode_cost(m: int, n: int, levels: int, std: frozenset) -> int:
    """Reconstruction writes, graded basis.  No root-copy term: every one of
    the four outputs of a node is written, none is a free view."""
    arithmetic = sum(7 ** (j - 1) * (7 if j in std else 6)
                     * (m >> j) * (n >> j)
                     for j in range(1, levels + 1))
    transform = sum(4 ** (j - 1) * (m >> j) * (n >> j)
                    for j in range(1, levels + 1) if j not in std)
    return arithmetic + transform


def _best_grade(cost, levels: int, marginal):
    """Cheapest grading, exactly.

    The root term depends on the grading only through ``s = len(std)``, and the
    per-node term is separable across levels, so for each s the optimum is the s
    levels of least marginal per-node cost.  Sorting therefore decides the whole
    2**L lattice; ``_selfcheck`` brute-forces the lattice to confirm it.
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
    """Cheapest operand-lane grading.  Marginal cost of demoting level j to the
    identity is ``(7**(j-1) - 4**(j-1)) * A_j``: zero at level 1, rising after."""
    return _best_grade(
        lambda std: graded_operand_cost(a_dim, b_dim, levels, std),
        levels,
        lambda j: (7 ** (j - 1) - 4 ** (j - 1)) * (a_dim >> j) * (b_dim >> j),
    )


def best_decode_grade(m: int, n: int, levels: int):
    """Cheapest decode-lane grading.  Same marginal, but with no root term to
    buy, so it never pays to demote a level below the level-1 tie."""
    return _best_grade(
        lambda std: graded_decode_cost(m, n, levels, std),
        levels,
        lambda j: (7 ** (j - 1) - 4 ** (j - 1)) * (m >> j) * (n >> j),
    )


def graded_depth_core_cost(m: int, k: int, n: int, levels: int) -> int:
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
    """Bill the graded core at this depth under the incumbent's fringe rule."""
    block = 1 << levels
    if m % block:
        return None
    core_k = k - k % block
    core_n = n - n % block
    if core_k == 0 or core_n == 0:
        return None
    inner_width = k - core_k
    output_width = n - core_n
    core = graded_depth_core_cost(m, core_k, core_n, levels)
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
        f"winograd_l{levels}_gradedbasis_mod{block}_fringe"
        if fringed
        else f"winograd_l{levels}_gradedbasis"
    )
    return Bill(
        strategy, m, k, n, core_k, core_n, core,
        inner_correction, inner_add, output_tail, total, direct_total,
        1 + int(bool(inner_width)) + int(bool(output_width)),
    )


def level_graded_basis_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Cheapest exact owned route over all lawful depths and all gradings.

    Supersedes ``alternative_basis_candidate_bill``: same routes, same fringe
    policy, same dual-odd branch, same depth sweep -- each depth is simply
    offered every level-indexed basis grading instead of the two pure ones, and
    keeps the cheapest.  Tier 4's route is the all-alternative member and
    tier 3's is the all-identity member, so no shape can regress against either.
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
alternative_basis_candidate_bill = level_graded_basis_candidate_bill
grouped_depth_candidate_bill = level_graded_basis_candidate_bill
candidate_bill = level_graded_basis_candidate_bill


# ---------------------------------------------------------------------------
# Executable exactness + accounting + geometry verifier.
# Pure integers, so "exact" is literal and bit-for-bit.
# ---------------------------------------------------------------------------

PHI_A = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]]
PHI_B = [[1, 0, 0, 0], [-1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
PHI_C = [[1, 0, 0, 0], [0, 1, 0, -1], [0, 0, 1, 0], [0, 0, 0, 1]]
EYE = [[int(i == j) for j in range(4)] for i in range(4)]


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
    """The seven left operands.  Alternative: phi_A already folded S1 into slot
    3, so four slots are free views and three blocks are written.  Standard:
    phi_A = I, three free views and four blocks written.  Both return Winograd's
    operand list [A11, A12, S4, A22, S1, S2, S3]."""
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


# --- write accounting and geometry, on the same tree -----------------------


class _Node:
    """One operand-tree node plus the provenance the scatter schedule needs."""

    __slots__ = ("rows", "cols", "tag", "owner", "off", "born")

    def __init__(self, rows, cols, tag, owner, off, born):
        self.rows = rows
        self.cols = cols
        self.tag = tag            # "root" | "arith" | "view"
        self.owner = owner
        self.off = off
        self.born = born          # level at which the owner block was written


def _build_operands(rows, cols, pattern, side, writes, hosted):
    """Walk the operand tree, charging exactly what the scatter schedule writes."""
    root = _Node(rows, cols, "root", None, (0, 0), 0)
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
            for tag, slot in order:
                if tag == "arith":
                    node = _Node(h, w, "arith", None, (0, 0), level)
                    node.owner = node
                    writes[0] += h * w
                else:
                    node = _Node(
                        h, w, "view", parent.owner,
                        (parent.off[0] + offs[slot][0],
                         parent.off[1] + offs[slot][1]),
                        parent.born,
                    )
                out.append(node)
        nodes = out
    for leaf in nodes:
        if leaf.tag != "view":
            continue
        if leaf.owner.tag == "root":
            writes[0] += leaf.rows * leaf.cols
        else:
            hosted.setdefault(id(leaf.owner), (leaf.owner, []))[1].append(
                (leaf.off[0], leaf.off[1], leaf.rows, leaf.cols)
            )
    return nodes


def _assert_scatter_is_free(hosted, pattern):
    """The load-bearing geometry: an owner's write can place all its leaves."""
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
    """Assert the graded schedule is exact, that the bill matches its real
    writes lane by lane, and that every scattered placement is legal."""
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

    assert psi_a[0] == transform_bill(m, k, pa), (
        f"left psi bill {transform_bill(m, k, pa)} != writes {psi_a[0]}")
    assert psi_b[0] == transform_bill(k, n, pb), (
        f"right psi bill {transform_bill(k, n, pb)} != writes {psi_b[0]}")
    assert psi_c[0] == transform_bill(m, n, pc), (
        f"decode psi bill {transform_bill(m, n, pc)} != writes {psi_c[0]}")

    def arith_bill(a_dim, b_dim, pattern, alt_c, std_c):
        return sum(7 ** (j - 1) * (alt_c if alt else std_c)
                   * (a_dim >> j) * (b_dim >> j)
                   for j, alt in enumerate(pattern, start=1))

    assert counters["left"] == arith_bill(m, k, pa, 3, 4), (
        f"left arith bill {arith_bill(m, k, pa, 3, 4)} "
        f"!= writes {counters['left']}")
    assert counters["right"] == arith_bill(k, n, pb, 3, 4), (
        f"right arith bill {arith_bill(k, n, pb, 3, 4)} "
        f"!= writes {counters['right']}")
    assert counters["decode"] == arith_bill(m, n, pc, 6, 7), (
        f"decode bill {arith_bill(m, n, pc, 6, 7)} "
        f"!= writes {counters['decode']}")
    assert counters["decode"] + psi_c[0] == graded_decode_cost(
        m, n, levels, std_of(pc))

    for side, (a_dim, b_dim), pattern in (("A", (m, k), pa), ("B", (k, n), pb)):
        writes = [0]
        hosted: dict = {}
        _build_operands(a_dim, b_dim, pattern, side, writes, hosted)
        _assert_scatter_is_free(hosted, pattern)
        s = len(std_of(pattern))
        expected = (arith_bill(a_dim, b_dim, pattern, 3, 4)
                    + 3 ** s * 4 ** (levels - s)
                    * (a_dim >> levels) * (b_dim >> levels))
        assert writes[0] == expected, (
            f"side {side} stack bill {expected} != writes {writes[0]}")
        assert graded_operand_cost(a_dim, b_dim, levels, std_of(pattern)) == (
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

    # and both decodes must reconstruct C, in their own coordinates
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

    Choosing phi_C is choosing four independent vectors spanning the row space W
    of W_C.  A decode schedule is a straight-line +/- program computing them from
    the seven unit vectors.  Enumerate every such program of length <= 5.
    Pruning is sound: a step raises the rank inside W by at most one, and
    recomputing an already-available vector or its negation never helps.
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
        assert not reachable(N), f"a {N}-write decode exists; tier 4 was wrong"
    assert reachable(6), "the six-write decode must be reachable"


def _selfcheck() -> None:
    m, k, n = 4096, 256, 256

    # 1. the three basis maps are unimodular with integer inverses, and each is
    #    a SINGLE elementary row operation over the slot it already owns.  That
    #    is what licenses one quadrant write per transform node.
    for phi in (PHI_A, PHI_B, PHI_C):
        inv = _inverse(phi)
        prod = [[sum(phi[i][t] * inv[t][j] for t in range(4)) for j in range(4)]
                for i in range(4)]
        assert prod == EYE
        assert all(abs(x) <= 1 for row in phi for x in row)
        assert all(abs(x) <= 1 for row in inv for x in row)
        for mat in (phi, inv):
            moved = [i for i in range(4) if mat[i] != EYE[i]]
            assert len(moved) == 1, (
                f"{moved} slots move; the one-write-per-node charge assumes one")
            assert mat[moved[0]][moved[0]] == 1, "moved slot must write in place"
    assert _inverse(EYE) == EYE

    # 2. both bases produce Winograd's operands and reconstruct C, symbolically
    _symbolic_encode_check()

    # 3. tier 4's open lead, closed: six decode writes is the exact floor
    _decode_floor_is_six()

    # 4. the graded formulas must reduce to the two ancestors at the two pure
    #    gradings -- this is what makes the family a strict superset.
    for levels in range(1, 9):
        allalt = frozenset()
        allstd = frozenset(range(1, levels + 1))
        for a_dim, b_dim in ((m, k), (k, n), (m, n)):
            assert graded_operand_cost(a_dim, b_dim, levels, allalt) == \
                alt_operand_cost(a_dim, b_dim, levels)
            assert graded_operand_cost(a_dim, b_dim, levels, allstd) == \
                standard_operand_stack_cost(a_dim, b_dim, levels)
        assert graded_decode_cost(m, n, levels, allalt) == \
            alt_decode_cost(m, n, levels)
        assert graded_decode_cost(m, n, levels, allstd) == \
            standard_reconstruction_cost(m, n, levels)

    # 5. lineage parity: both ancestors' published depth tables, digit for digit
    tier3_table = {
        1: 471711744, 2: 416567296, 3: 371653632, 4: 338169088,
        5: 319026624, 6: 320036176, 7: 351987132, 8: 434304253,
    }
    tier4_table = {
        1: 471990272, 2: 416649216, 3: 370777088, 4: 335053056,
        5: 311468480, 6: 304210704, 7: 321222236, 8: 376940289,
    }
    for levels, value in tier3_table.items():
        assert standard_depth_core_cost(m, k, n, levels) == value, (
            f"standard basis at L={levels} is "
            f"{standard_depth_core_cost(m, k, n, levels)}, tier 3 says {value}")
    for levels, value in tier4_table.items():
        assert alt_basis_depth_core_cost(m, k, n, levels) == value, (
            f"alternative basis at L={levels} is "
            f"{alt_basis_depth_core_cost(m, k, n, levels)}, tier 4 says {value}")

    # 6. the sorted grading selection must equal a brute force over all 2**L
    #    subsets of levels, at every depth in the sweep and on every lane.
    for levels in range(1, 9):
        for a_dim, b_dim in ((m, k), (k, n)):
            brute = min(
                graded_operand_cost(a_dim, b_dim, levels, frozenset(sub))
                for size in range(levels + 1)
                for sub in combinations(range(1, levels + 1), size)
            )
            picked, _ = best_operand_grade(a_dim, b_dim, levels)
            assert picked == brute, (
                f"operand grading at L={levels} picked {picked}, brute {brute}")
        brute = min(
            graded_decode_cost(m, n, levels, frozenset(sub))
            for size in range(levels + 1)
            for sub in combinations(range(1, levels + 1), size)
        )
        picked, _ = best_decode_grade(m, n, levels)
        assert picked == brute, (
            f"decode grading at L={levels} picked {picked}, brute {brute}")

    # 7. the graded route can never be worse than either ancestor, at any depth
    for levels in range(1, 9):
        graded = graded_depth_core_cost(m, k, n, levels)
        assert graded <= alt_basis_depth_core_cost(m, k, n, levels)
        assert graded <= standard_depth_core_cost(m, k, n, levels)
    #    and it is strictly better than both at the selected depth
    assert graded_depth_core_cost(m, k, n, 6) < tier4_table[6]

    # 8. the level-1 demotion is free on the per-node side and worth a quarter
    #    of the root lane -- the arithmetic this tier rests on, stated as an
    #    identity rather than as prose.
    for levels in range(2, 9):
        for a_dim, b_dim in ((m, k), (k, n)):
            saving = (graded_operand_cost(a_dim, b_dim, levels, frozenset())
                      - graded_operand_cost(a_dim, b_dim, levels, frozenset({1})))
            assert saving == a_dim * b_dim // 4, (
                f"level-1 demotion at L={levels} saved {saving}, "
                f"expected {a_dim * b_dim // 4}")
        # level 2 is the exact break-even of the same trade
        assert (graded_operand_cost(m, k, levels, frozenset({1}))
                == graded_operand_cost(m, k, levels, frozenset({1, 2})))

    # 9. executable exactness, write accounting and geometry, over several
    #    gradings including ones that differ between the three lanes.
    T, F = True, False
    for shape, pa, pb, pc in (
        ((8, 4, 4), [F, T], [F, T], [T, T]),
        ((8, 4, 4), [T, T], [T, T], [T, T]),
        ((8, 4, 4), [F, F], [F, F], [F, F]),
        ((16, 8, 8), [F, T, T], [F, T, T], [T, T, T]),
        ((16, 8, 8), [T, F, T], [F, T, F], [T, T, F]),
        ((8, 8, 8), [F, T, T], [T, F, T], [T, T, T]),
        ((32, 16, 16), [F, T, T, T], [F, T, T, T], [T, T, T, T]),
        ((64, 8, 8), [F, T, T], [T, T, F], [F, T, T]),
        ((16, 16, 8), [T, T, F], [F, F, T], [T, F, T]),
    ):
        verify_schedule(*shape, pa, pb, pc, seed=20260818)


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: exactness, both bases, decode floor, write accounting, "
          "grading optimality and scatter geometry all pass")
    bill = level_graded_basis_candidate_bill(4096, 256, 256)
    print(bill.to_dict())
    print("total:", bill.total)

    best = 6
    m, k, n = 4096, 256, 256
    left, sl = best_operand_grade(m, k, best)
    right, sr = best_operand_grade(k, n, best)
    decode, sd = best_decode_grade(m, n, best)
    print(f"breakdown of the selected core (L={best}):")
    print("  leaves        ",
          7 ** best * direct_cost(m >> best, k >> best, n >> best))
    print(f"  left operands  {left:>12}   standard levels {sorted(sl) or '[]'}")
    print(f"  right operands {right:>12}   standard levels {sorted(sr) or '[]'}")
    print(f"  decode         {decode:>12}   standard levels {sorted(sd) or '[]'}")
    for level in range(1, 9):
        try:
            print(f"  L={level} graded={graded_depth_core_cost(m, k, n, level):>12}"
                  f"  alt={alt_basis_depth_core_cost(m, k, n, level):>12}"
                  f"  std={standard_depth_core_cost(m, k, n, level):>12}")
        except ValueError as exc:
            print(f"  L={level} unavailable: {exc}")
