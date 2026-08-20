"""Tier 4: run the whole depth-L recursion in an alternative basis.

ONE SUBSTANTIVE CHANGE
======================
Tier 3 closed with the only door it could see:

    "The reconstruction lane, 37,710,848 and untouched since tier 1, is now the
     largest overhead term.  Its 7 adds per node are minimal in the standard
     basis (Probert 1976), so the only lawful door there is an
     alternative-basis <2,2,2;7> in the Karstadt-Schwartz sense."

This tier walks through it.  The single change is a change of coordinates:
conjugate the bilinear algorithm by three fixed unimodular 4x4 maps
``phi_A, phi_B, phi_C`` acting on the quadrant vector, so that every node of the
recursion runs on transformed blocks.  Probert's 15-addition bound is a bound in
the *standard* basis and says nothing about a conjugated one; the conjugated
algorithm computes the same products from the same operands and costs 12 linear
operations per node instead of 15, at the price of one O(n^2 log n) basis
change per matrix (a 4-ary tree, not a 7-ary one, which is why it is cheap).

Nothing else moves.  The leaf count is still 7**L, the fringe rule is the
incumbent's, the scatter licence is tier 3's, the depth sweep is tier 1's.

THE THREE MAPS, AND WHY THEY ARE THE ONES
=========================================
Write a = (A11, A12, A21, A22) and b = (B11, B12, B21, B22) for the quadrant
vectors, and let U_A, U_B (7x4) and W_C (4x7) be Winograd's encode/decode
matrices, so the standard algorithm is  c = W_C ((U_A a) * (U_B b)).  For any
invertible phi_A, phi_B, phi_C,

    (phi_C c) = (phi_C W_C) ( (U_A phi_A^-1 (phi_A a)) * (U_B phi_B^-1 (phi_B b)) )

is the same computation read in new coordinates.  The cost of a lane depends on
exactly one phi, so the three searches are independent.

*Encode.*  A row of ``U_A phi_A^-1`` is a free block -- no write at all, tier 3's
scatter rule -- exactly when it is a unit vector, and ``v phi_A^-1 = e_i`` iff
``v`` is the i-th row of phi_A.  So the number of free operands equals the
number of rows of phi_A that are themselves rows of U_A, and the maximum is 4
(phi_A has 4 rows).  Winograd's standard basis achieves only 3 (A11, A12, A22
are rows of U_A; A21 is not).  Taking the fourth row to be S1 = A21 + A22 -- in
the physical slot A21 already occupies, so the map is the in-place
``A21 += A22`` -- gives 4 free operands and leaves 3 arithmetic ones:

    phi_A : (a1,a2,a3,a4) -> (a1, a2, a3+a4, a4)          1 write / quadrant

    A11 = t1        A12 = t2        S1 = t3        A22 = t4      (free views)
    S2  = t3 - t1   S4  = t2 - S2   S3 = t4 - S2                 (3 writes)

    where t = phi_A a.   Check: S2 = -A11+A21+A22, S4 = A11+A12-A21-A22,
    S3 = A11-A21, digit for digit Winograd's four input additions minus one.

    phi_B : (b1,b2,b3,b4) -> (b1, b2-b1, b3, b4)          1 write / quadrant

    B11 = u1        T1 = u2         B21 = u3       B22 = u4      (free views)
    T2  = u4 - u2   T3 = T2 - u1    T4 = T2 - u3                 (3 writes)

    Check: T1 = B12-B11, T2 = B11-B12+B22, T3 = B22-B12,
    T4 = B11-B12-B21+B22.  Winograd's four right-hand additions minus one.

*Decode.*  In M-coordinates the four rows of W_C are

    C11 = M1+M2            C12 = M1+M3+M5+M6
    C21 = M1-M4+M6+M7      C22 = M1+M5+M6+M7

A vector in the row space is ``(a+b+c+d, a, b, -c, b+d, b+c+d, c+d)``.  Solving
for one nonzero coordinate has no solution, so no decode row is ever free; the
only 2-nonzero -- i.e. one-write -- directions are M1+M2, M3-M7 and M4+M5, and
their M6 coefficient is 0, so three of them can never span.  An exhaustive layer
enumeration (``_search_note`` records it) finds no row-space vector with M6
coefficient +-1 within two writes of {units, M1+M2, M3-M7, M4+M5}, so any decode
basis built on those three costs at least 6.  Six is attained, by the single
elementary map

    phi_C : (c1,c2,c3,c4) -> (c1, c2-c4, c3, c4)          1 write / quadrant

whose decode rows are C11, C12-C22 = M3-M7, C21, C22, scheduled as

    U2 = M1 + M6     U3 = U2 + M7     d3 = U3 - M4     d4 = U3 + M5
    d1 = M1 + M2     d2 = M3 - M7                                  (6 writes)

and whose inverse is the single in-place ``C12 += C22`` (1 write / quadrant).
Total per node: 3 + 3 + 6 = 12 against the standard basis's 4 + 4 + 7 = 15 --
the Karstadt-Schwartz count for <2,2,2;7>, reached here by direct search rather
than quoted.

WHY THE BASIS CHANGE IS PAID ONCE, NOT PER NODE
===============================================
Define Psi_A^0(A) = A and Psi_A^d(A) = the matrix whose four quadrant slots hold
Psi_A^{d-1} of the four outputs of phi_A.  Psi is linear, so for the depth-d
recursion run on Psi-transformed inputs, operand i of the top node is

    sum_j (U_A phi_A^-1)_ij Psi^{d-1}(t_j) = Psi^{d-1}( (U_A phi_A^-1 phi_A a)_i )
                                           = Psi^{d-1}( (U_A a)_i ),

i.e. *already* the correctly transformed operand for the remaining d-1 levels.
No transform occurs inside the recursion.  The transform tree therefore branches
4-ways, not 7-ways, and costs

    psi_cost(a, b, L) = sum_{j=1..L} 4**(j-1) * (a >> j) * (b >> j)

which is L*a*b/4 when 2**L divides both -- against the 7**(j-1) growth of every
lane it buys down.  At (4096, 256, 256), L = 6: 1,572,864 spent on the left
transform to save 9,689,856 of left operand writes.

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

    U2 = M1 + M6      U3 = U2 + M7

    C11 = M1 + M2     C12 = U2 + M5 + M3
    C21 = U3 - M4     C22 = U3 + M5

which expands term by term to C11 = A11 B11 + A12 B21, C12 = A11 B12 + A12 B22,
C21 = A21 B11 + A22 B21, C22 = A21 B12 + A22 B22 -- the block product.

This tier changes the coordinates in which that identity is written, not the
identity.  Formally, by induction on d:

    ALG'^d( Psi_A^d(A), Psi_B^d(B) ) = Psi_C^d( A B ).

The base case d = 0 is a plain product.  For the step, the display above shows
operand i of ALG'^d is Psi_A^{d-1}((U_A a)_i) and Psi_B^{d-1}((U_B b)_i), so by
hypothesis the recursive call returns Psi_C^{d-1}(M_i); linearity of Psi then
gives output slot p as Psi_C^{d-1}( (phi_C W_C M)_p ) = Psi_C^{d-1}( (phi_C c)_p ),
which is by definition slot p of Psi_C^d(c).  Undoing Psi_C^L at the end returns
A B exactly.

Every matrix in play -- phi_A, phi_B, phi_C and their inverses -- is unimodular
with entries in {-1, 0, 1}:

    phi_A = [[1,0,0,0],[0,1,0,0],[0,0,1,1],[0,0,0,1]]   det  1
    phi_B = [[1,0,0,0],[-1,1,0,0],[0,0,1,0],[0,0,0,1]]  det  1
    phi_C = [[1,0,0,0],[0,1,0,-1],[0,0,1,0],[0,0,0,1]]  det  1

so the transforms and their inverses are additions and subtractions only.  No
division, no reciprocal, no scaling, no truncation, no value-dependent
reordering: over any ring the result is the same ring element the direct route
computes, and over the integers the verifier below checks it literally.

WHAT IS BILLED
==============
    operand_cost(a, b, L)  = 4**L * (a>>L) * (b>>L)          root copies
                           + psi_cost(a, b, L)               basis change
                           + 3 * sum_j 7**(j-1) (a>>j)(b>>j) arithmetic operands

    decode_cost(m, n, L)   = 6 * sum_j 7**(j-1) (m>>j)(n>>j) reconstruction
                           + psi_cost(m, n, L)               inverse basis change

The root-copy term is now 4**L leaves of area a*b/4**L, i.e. exactly a*b: with
four free operands per node the all-identity leaves tile the transformed matrix
once, where tier 3's three tiled a strict subset (3**L).  That is a real
increase of 799,744 on the left lane at L = 5 -- and it is bought many times
over by the fourth free operand, which removes 7**(j-1) blocks per level.
Nothing is hidden in the trade: ``_selfcheck`` asserts the decomposition.

The scatter licence is inherited verbatim from tier 3 and is *tighter* here.  An
arithmetic block at level j hosts its all-identity descendants at level L; there
are 4**(L-j) of them, each of area (block area)/4**(L-j), so they tile the owner
exactly rather than covering (3/4)**(L-j) of it.  Disjointness is the same
distinct-quadrant-address argument, and ``verify_schedule`` asserts it on real
rectangles.

RESULT AT (4096, 256, 256)
==========================
    L    alternative basis      tier 3 (standard basis)
    1        471,990,272             471,711,744
    2        416,649,216             416,567,296
    3        370,777,088             371,653,632
    4        335,053,056             338,169,088
    5        311,468,480             319,026,624
    6      * 304,210,704             320,036,176
    7        321,222,236             351,987,132
    8        376,940,289             434,304,253

    total 304,210,704  =  210,827,008 leaves
                        +  31,691,008 left operands
                        +   1,980,688 right operands
                        +  59,712,000 decode

The basis change loses at L = 1 and L = 2 -- one extra free operand cannot repay
one extra transform level when there are only one or two levels to amortise it
over -- and wins from L = 3 on, which is the shape of self-check that licensed
tiers 2 and 3.  ``_depth_route`` therefore bills both bases at every depth and
keeps the cheaper, so no shape can regress against tier 3.

Because the overhead lanes shrank by roughly a quarter, the depth optimum moves
from L = 5 to L = 6, which tier 3 had missed by only 1,009,552.  Against the
incumbent 319,026,624 the saving is 14,815,920 FLOPs (4.644%); against the
535,822,336 direct comparator the ratio is 0.567745.

No approximation, no rank reduction, no f32 repricing, no compliance flags --
pure schedule.

VERIFICATION RUN IN ``_selfcheck``
==================================
1. An executable integer verifier transforms random integer A and B by Psi,
   runs the alternative-basis recursion to depth L, undoes Psi_C, and asserts
   the result equals the plain integer product.  Over the integers "exact" is
   literal and bit-for-bit.
2. The same verifier counts every write the schedule really performs -- one per
   element of every transform step, of every arithmetic operand at every level,
   of every root-descended identity leaf, and of every decode write -- and
   asserts the count equals the billed closed form, lane by lane.  The bill is
   measured off the schedule, not asserted about it.
3. It asserts the geometry: for every owner block the leaf rectangles it hosts
   are pairwise disjoint and lie inside its bounds.  This is the check that
   fails if the scatter were not free.
4. The three phi matrices are asserted unimodular with integer inverses, and the
   two encode maps are asserted to reproduce Winograd's S1..S4 and T1..T4
   symbolically, so a typo in the alternative basis cannot pass.
5. The standard-basis lane is recomputed here from tier 3's own formula and
   asserted equal to tier 3's published depth table, so the comparison in the
   result table is against a live number rather than a quoted one.

LEAD LEFT FOR A LATER TIER (not taken here; one change per tier)
================================================================
The decode lane is 6 writes per node.  Five is not reachable from the three
one-write directions (search above), but the search that would settle whether
*some* other basis reaches five -- a five-write schedule can contain at most one
non-row-space intermediate, which bounds the space -- did not run to completion
here and is left open.  The leaf lane, 210,827,008 and 69% of the bill, is
untouched since tier 0 and is where the next order of magnitude has to come
from; at L = 6 the leaf shape is (64, 4, 4), so a <4,4,4> scheme with fewer than
49 multiplications would land exactly there.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


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


# Tier 3's standard-basis lanes, kept so both bases can be billed and the
# cheaper kept.  Reproduced, never imported (rule 7).


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


# ---------------------------------------------------------------------------
# The one substantive change: the same recursion, read in an alternative basis.
# ---------------------------------------------------------------------------


def psi_cost(a_dim: int, b_dim: int, levels: int) -> int:
    """The basis change: one quadrant write per node of the 4-ary tree.

    phi_A, phi_B and phi_C are each a single elementary row operation, so one
    slot of the four is rewritten and the other three stay put as views.
    """
    return sum(4 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
               for j in range(1, levels + 1))


def alt_operand_cost(a_dim: int, b_dim: int, levels: int) -> int:
    """Blocks written to form one side's depth-L operand set, alternative basis.

    Four of the seven operands per node are free views of transformed quadrant
    slots (against three in the standard basis), so only three arithmetic blocks
    are materialised per node.  The all-identity leaves now tile the transformed
    matrix exactly, so the root-copy term is the full a*b.
    """
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    root_copies = 4 ** levels * (a_dim >> levels) * (b_dim >> levels)
    return (root_copies
            + psi_cost(a_dim, b_dim, levels)
            + 3 * node_area_sum(a_dim, b_dim, levels))


def alt_decode_cost(m: int, n: int, levels: int) -> int:
    """Six reconstruction writes per node, plus the inverse basis change."""
    return 6 * node_area_sum(m, n, levels) + psi_cost(m, n, levels)


def alt_basis_depth_core_cost(m: int, k: int, n: int, levels: int) -> int:
    """Depth-L batched Winograd core run in the alternative basis."""
    block = 1 << levels
    if min(m, k, n) <= 0 or any(value % block for value in (m, k, n)):
        raise ValueError(f"{levels} Winograd levels require multiples of {block}")
    leaves = 7 ** levels * direct_cost(m // block, k // block, n // block)
    return (leaves
            + alt_operand_cost(m, k, levels)
            + alt_operand_cost(k, n, levels)
            + alt_decode_cost(m, n, levels))


def _depth_route(m: int, k: int, n: int, levels: int, direct_total: int):
    """Bill both bases at this depth under the incumbent's mod-block fringe."""
    block = 1 << levels
    if m % block:
        return None
    core_k = k - k % block
    core_n = n - n % block
    if core_k == 0 or core_n == 0:
        return None
    inner_width = k - core_k
    output_width = n - core_n
    alt = alt_basis_depth_core_cost(m, core_k, core_n, levels)
    std = standard_depth_core_cost(m, core_k, core_n, levels)
    core = min(alt, std)
    basis = "alt" if alt <= std else "std"
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
        f"winograd_l{levels}_{basis}basis_mod{block}_fringe"
        if fringed
        else f"winograd_l{levels}_{basis}basis"
    )
    return Bill(
        strategy, m, k, n, core_k, core_n, core,
        inner_correction, inner_add, output_tail, total, direct_total,
        1 + int(bool(inner_width)) + int(bool(output_width)),
    )


def alternative_basis_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Cheapest exact owned route over all lawful depths and both bases.

    Supersedes ``ancestor_scattered_candidate_bill``: same routes, same fringe
    policy, same dual-odd branch, same depth sweep -- each depth is simply
    offered the alternative basis as well as the standard one, and keeps
    whichever is cheaper.
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
grouped_depth_candidate_bill = alternative_basis_candidate_bill
candidate_bill = alternative_basis_candidate_bill


# ---------------------------------------------------------------------------
# Executable exactness + accounting + geometry verifier.
# Pure integers, so "exact" is literal and bit-for-bit.
# ---------------------------------------------------------------------------

# phi matrices as row lists, acting on the quadrant vector (11, 12, 21, 22).
PHI_A = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]]
PHI_B = [[1, 0, 0, 0], [-1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
PHI_C = [[1, 0, 0, 0], [0, 1, 0, -1], [0, 0, 1, 0], [0, 0, 0, 1]]


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
    """Apply a 4x4 integer map to the four quadrant blocks."""
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


def _psi(X, phi, levels, writes):
    """Recursive basis change; one elementary slot rewrite per node."""
    if levels == 0:
        return X
    q = _apply_phi(_quads(X), phi)
    # exactly one of the four slots is a genuine new block (the phi matrices are
    # single elementary row operations); the other three are unchanged views.
    writes[0] += len(q[0]) * len(q[0][0])
    return _join([_psi(blk, phi, levels - 1, writes) for blk in q])


def _psi_inverse(X, phi_inv, levels, writes):
    if levels == 0:
        return X
    q = [_psi_inverse(blk, phi_inv, levels - 1, writes) for blk in _quads(X)]
    out = _apply_phi(q, phi_inv)
    writes[0] += len(out[0]) * len(out[0][0])
    return _join(out)


def _encode_left(t):
    """U_A phi_A^-1 applied to the four transformed left slots."""
    t1, t2, t3, t4 = t
    s2 = _lin(t3, t1, -1)
    s4 = _lin(t2, s2, -1)
    s3 = _lin(t4, s2, -1)
    #      free views:  t1 t2 . t4 t3 | arithmetic: s4 s2 s3
    return [t1, t2, s4, t4, t3, s2, s3], [s4, s2, s3], [0, 1, 3, 2]


def _encode_right(u):
    """U_B phi_B^-1 applied to the four transformed right slots."""
    u1, u2, u3, u4 = u
    t2 = _lin(u4, u2, -1)
    t3 = _lin(t2, u1, -1)
    t4 = _lin(t2, u3, -1)
    return [u1, u3, u4, t4, u2, t2, t3], [t4, t2, t3], [0, 2, 3, 1]


def _decode(M, counters):
    """phi_C W_C applied to the seven products: six writes.

    Slots are (C11, C12-C22, C21, C22) -- phi_C applied to the standard
    reconstruction, which is why C12 never has to be formed at all.
    """
    m1, m2, m3, m4, m5, m6, m7 = M
    u2 = _lin(m1, m6, 1)
    u3 = _lin(u2, m7, 1)
    d3 = _lin(u3, m4, -1)
    d4 = _lin(u3, m5, 1)
    d1 = _lin(m1, m2, 1)
    d2 = _lin(m3, m7, -1)
    counters["decode"] += 6 * len(m1) * len(m1[0])
    return [d1, d2, d3, d4]


def _alg(A, B, levels, counters):
    """Alternative-basis recursion on already-transformed operands."""
    if levels == 0:
        return _plain(A, B)
    left, left_arith, _ = _encode_left(_quads(A))
    right, right_arith, _ = _encode_right(_quads(B))
    counters["left"] += sum(len(x) * len(x[0]) for x in left_arith)
    counters["right"] += sum(len(x) * len(x[0]) for x in right_arith)
    M = [_alg(left[i], right[i], levels - 1, counters) for i in range(7)]
    return _join(_decode(M, counters))


# --- write accounting and geometry, on the same tree -----------------------


class _Node:
    """One operand-tree node plus the provenance the scatter schedule needs."""

    __slots__ = ("rows", "cols", "tag", "owner", "off")

    def __init__(self, rows, cols, tag, owner, off):
        self.rows = rows
        self.cols = cols
        self.tag = tag            # "root" | "arith" | "view"
        self.owner = owner
        self.off = off


def _build_operands(rows, cols, levels, side, writes, hosted):
    """Walk the operand tree, charging exactly what the scatter schedule writes."""
    root = _Node(rows, cols, "root", None, (0, 0))
    root.owner = root
    nodes = [root]
    for _ in range(levels):
        out = []
        for parent in nodes:
            h = parent.rows // 2
            w = parent.cols // 2
            offs = [(0, 0), (0, w), (h, 0), (h, w)]
            if side == "A":
                view_slots = [0, 1, 3, 2]      # t1, t2, t4, t3
                order = [("view", 0), ("view", 1), ("arith", None),
                         ("view", 3), ("view", 2), ("arith", None),
                         ("arith", None)]
            else:
                view_slots = [0, 2, 3, 1]      # u1, u3, u4, u2
                order = [("view", 0), ("view", 2), ("view", 3),
                         ("arith", None), ("view", 1), ("arith", None),
                         ("arith", None)]
            assert sorted(view_slots) == [0, 1, 2, 3], "views must tile the parent"
            for tag, slot in order:
                if tag == "arith":
                    node = _Node(h, w, "arith", None, (0, 0))
                    node.owner = node
                    writes[0] += h * w
                else:
                    node = _Node(
                        h, w, "view", parent.owner,
                        (parent.off[0] + offs[slot][0],
                         parent.off[1] + offs[slot][1]),
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


def _assert_scatter_is_free(hosted):
    """The load-bearing geometry: an owner's write can place all its leaves."""
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
        assert area == owner.rows * owner.cols, (
            "with four free operands the hosted leaves must tile the owner"
        )


def _inverse(phi):
    """Integer inverse of a unimodular 4x4, by Gauss-Jordan over Fractions."""
    from fractions import Fraction
    n = 4
    M = [[Fraction(x) for x in row] + [Fraction(int(i == j)) for j in range(n)]
         for i, row in enumerate(phi)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col])
        M[col], M[piv] = M[piv], M[col]
        f = M[col][col]
        M[col] = [x / f for x in M[col]]
        for r in range(n):
            if r != col and M[r][col]:
                g = M[r][col]
                M[r] = [x - g * y for x, y in zip(M[r], M[col])]
    inv = [[M[i][n + j] for j in range(n)] for i in range(n)]
    for row in inv:
        for x in row:
            assert x.denominator == 1, "phi is not unimodular"
    return [[int(x) for x in row] for row in inv]


def verify_schedule(m: int, k: int, n: int, levels: int, seed: int) -> None:
    """Assert the alternative-basis schedule is exact, that the bill matches its
    real writes lane by lane, and that every scattered placement tiles."""
    state = seed

    def nxt():
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return state % 19 - 9

    a = [[nxt() for _ in range(k)] for _ in range(m)]
    b = [[nxt() for _ in range(n)] for _ in range(k)]

    psi_a = [0]
    psi_b = [0]
    psi_c = [0]
    at = _psi(a, PHI_A, levels, psi_a)
    bt = _psi(b, PHI_B, levels, psi_b)

    counters = {"left": 0, "right": 0, "decode": 0}
    ct = _alg(at, bt, levels, counters)
    c = _psi_inverse(ct, _inverse(PHI_C), levels, psi_c)

    assert c == _plain(a, b), f"schedule is not exact at {(m, k, n, levels)}"

    # basis-change lanes
    assert psi_a[0] == psi_cost(m, k, levels), (
        f"left psi bill {psi_cost(m, k, levels)} != writes {psi_a[0]}")
    assert psi_b[0] == psi_cost(k, n, levels), (
        f"right psi bill {psi_cost(k, n, levels)} != writes {psi_b[0]}")
    assert psi_c[0] == psi_cost(m, n, levels), (
        f"decode psi bill {psi_cost(m, n, levels)} != writes {psi_c[0]}")

    # arithmetic operand lanes, measured on the executed recursion
    assert counters["left"] == 3 * node_area_sum(m, k, levels), (
        f"left arith bill {3 * node_area_sum(m, k, levels)} "
        f"!= writes {counters['left']}")
    assert counters["right"] == 3 * node_area_sum(k, n, levels), (
        f"right arith bill {3 * node_area_sum(k, n, levels)} "
        f"!= writes {counters['right']}")
    assert counters["decode"] == 6 * node_area_sum(m, n, levels), (
        f"decode bill {6 * node_area_sum(m, n, levels)} "
        f"!= writes {counters['decode']}")

    # scatter accounting and geometry, on the same tree
    for side, (a_dim, b_dim) in (("A", (m, k)), ("B", (k, n))):
        writes = [0]
        hosted: dict = {}
        _build_operands(a_dim, b_dim, levels, side, writes, hosted)
        _assert_scatter_is_free(hosted)
        expected = (3 * node_area_sum(a_dim, b_dim, levels)
                    + 4 ** levels * (a_dim >> levels) * (b_dim >> levels))
        assert writes[0] == expected, (
            f"side {side} stack bill {expected} != writes {writes[0]}")
        assert alt_operand_cost(a_dim, b_dim, levels) == (
            writes[0] + psi_cost(a_dim, b_dim, levels))


def _symbolic_encode_check() -> None:
    """The alternative encodes must reproduce Winograd's S1..S4 and T1..T4."""
    # basis vectors for the four quadrants, as integer 1x4 "matrices"
    def unit(i):
        return [[1 if j == i else 0 for j in range(4)]]

    a = [unit(i) for i in range(4)]                     # A11 A12 A21 A22
    t = _apply_phi(a, PHI_A)
    left, _, _ = _encode_left(t)
    want = [
        [1, 0, 0, 0],      # A11
        [0, 1, 0, 0],      # A12
        [1, 1, -1, -1],    # S4 = A11+A12-A21-A22
        [0, 0, 0, 1],      # A22
        [0, 0, 1, 1],      # S1 = A21+A22
        [-1, 0, 1, 1],     # S2 = -A11+A21+A22
        [1, 0, -1, 0],     # S3 = A11-A21
    ]
    assert [row[0] for row in left] == want, "left encode is not Winograd's"

    b = [unit(i) for i in range(4)]                     # B11 B12 B21 B22
    u = _apply_phi(b, PHI_B)
    right, _, _ = _encode_right(u)
    want_b = [
        [1, 0, 0, 0],      # B11
        [0, 0, 1, 0],      # B21
        [0, 0, 0, 1],      # B22
        [1, -1, -1, 1],    # T4 = B11-B12-B21+B22
        [-1, 1, 0, 0],     # T1 = B12-B11
        [1, -1, 0, 1],     # T2 = B11-B12+B22
        [0, -1, 0, 1],     # T3 = B22-B12
    ]
    assert [row[0] for row in right] == want_b, "right encode is not Winograd's"


def _search_note() -> None:
    """Re-run the decode-basis search that fixed six writes as the floor here.

    Enumerates every row-space vector reachable in one and in two block-writes
    from the units plus the three one-write directions, and asserts that none of
    them has an M6 coefficient of +-1 -- i.e. that no fourth, independent decode
    row is available inside two writes, so a basis on those three costs >= 6.
    """
    rows = [
        (1, 1, 0, 0, 0, 0, 0),       # C11
        (1, 0, 1, 0, 1, 1, 0),       # C12
        (1, 0, 0, -1, 0, 1, 1),      # C21
        (1, 0, 0, 0, 1, 1, 1),       # C22
    ]
    # Membership in the row space is orthogonality to its null space, which is
    # exact and needs no coefficient bound.
    null = [(1, -1, 0, 0, 0, -1, 0),
            (0, 0, 0, 1, -1, 1, 0),
            (0, 0, 1, 0, 0, -1, 1)]
    for r in rows:
        assert all(sum(x * y for x, y in zip(r, nb)) == 0 for nb in null)

    def in_space(v):
        return all(sum(x * y for x, y in zip(v, nb)) == 0 for nb in null)

    units = [tuple(1 if i == j else 0 for i in range(7)) for j in range(7)]
    seeds = units + [(1, 1, 0, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0, -1),
                     (0, 0, 0, 1, 1, 0, 0)]
    seeds = seeds + [tuple(-x for x in s) for s in seeds]

    def layer(prev, base):
        out = set()
        for w in prev:
            for z in base:
                for s in (1, -1):
                    out.add(tuple(p + s * q for p, q in zip(w, z)))
        return out

    # One write: any u +/- v over the seeds.  Two writes: one intermediate over
    # the seeds, then that intermediate combined with a seed (or itself).  A
    # schedule drawing on a *second* intermediate already costs three.
    one = layer(seeds, seeds)
    two = layer(one, set(seeds)) | {tuple(2 * x for x in w) for w in one}
    for name, reach in (("one write", one), ("two writes", two)):
        hits = [v for v in reach if in_space(v) and v[5]]
        assert not hits, f"a fourth decode row was reachable in {name}: {hits[:3]}"


def _selfcheck() -> None:
    m, k, n = 4096, 256, 256

    # 1. the three basis maps are unimodular with integer inverses, and each is
    #    a SINGLE elementary row operation.  That is what licenses charging one
    #    quadrant write per transform node: three slots keep their contents as
    #    views and the fourth is rewritten in place over the slot it already
    #    owns (its own coordinate appears with coefficient 1 in its new row).
    identity = [[int(i == j) for j in range(4)] for i in range(4)]
    for phi in (PHI_A, PHI_B, PHI_C):
        inv = _inverse(phi)
        prod = [[sum(phi[i][t] * inv[t][j] for t in range(4)) for j in range(4)]
                for i in range(4)]
        assert prod == identity
        assert all(abs(x) <= 1 for row in phi for x in row)
        assert all(abs(x) <= 1 for row in inv for x in row)
        for mat in (phi, inv):
            moved = [i for i in range(4) if mat[i] != identity[i]]
            assert len(moved) == 1, (
                f"{moved} slots move; the one-write-per-node charge assumes one")
            i = moved[0]
            assert mat[i][i] == 1, "the moved slot must be writable in place"

    # 2. the alternative encodes are Winograd's own operands, symbolically
    _symbolic_encode_check()

    # 3. the decode floor of six writes, re-derived by enumeration
    _search_note()

    # 4. lane decomposition: the fourth free operand removes one block per node
    #    and pays for it with the larger root tile plus the transform.
    for levels in range(1, 8):
        gain = node_area_sum(m, k, levels)
        extra_root = (4 ** levels - 3 ** levels) * (m >> levels) * (k >> levels)
        assert (standard_operand_stack_cost(m, k, levels)
                - alt_operand_cost(m, k, levels)
                == gain - extra_root - psi_cost(m, k, levels))
        assert (standard_reconstruction_cost(m, n, levels)
                - alt_decode_cost(m, n, levels)
                == node_area_sum(m, n, levels) - psi_cost(m, n, levels))

    # 5. lineage parity: the standard-basis lane reproduced here must equal
    #    tier 3's published depth table, digit for digit.
    tier3_table = {
        1: 471711744, 2: 416567296, 3: 371653632, 4: 338169088,
        5: 319026624, 6: 320036176, 7: 351987132, 8: 434304253,
    }
    for levels, value in tier3_table.items():
        assert standard_depth_core_cost(m, k, n, levels) == value, (
            f"standard basis at L={levels} is "
            f"{standard_depth_core_cost(m, k, n, levels)}, tier 3 says {value}")

    # 6. the basis change must lose at L=1 (nothing to amortise over) and win
    #    from L=3 on -- the shape of self-check that licensed tiers 2 and 3.
    assert alt_basis_depth_core_cost(m, k, n, 1) > standard_depth_core_cost(m, k, n, 1)
    for levels in range(3, 9):
        assert alt_basis_depth_core_cost(m, k, n, levels) < \
            standard_depth_core_cost(m, k, n, levels)

    # 7. executable exactness, write accounting and geometry at several shapes.
    for shape in ((8, 4, 4, 2), (16, 8, 8, 3), (8, 8, 8, 3),
                  (32, 16, 16, 4), (64, 8, 8, 3), (16, 16, 8, 3)):
        verify_schedule(*shape, seed=20260818)


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: exactness, basis algebra, write-accounting and scatter "
          "geometry all pass")
    bill = alternative_basis_candidate_bill(4096, 256, 256)
    print(bill.to_dict())
    print("total:", bill.total)
    best = 6
    print("breakdown of the selected core (L=%d):" % best)
    print("  leaves        ",
          7 ** best * direct_cost(4096 >> best, 256 >> best, 256 >> best))
    print("  left operands ", alt_operand_cost(4096, 256, best))
    print("  right operands", alt_operand_cost(256, 256, best))
    print("  decode        ", alt_decode_cost(4096, 256, best))
    for level in range(1, 9):
        try:
            print(f"  L={level} alt={alt_basis_depth_core_cost(4096, 256, 256, level):>12}"
                  f"  std={standard_depth_core_cost(4096, 256, 256, level):>12}")
        except ValueError as exc:
            print(f"  L={level} unavailable: {exc}")
