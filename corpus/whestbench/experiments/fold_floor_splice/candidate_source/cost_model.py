"""Closed-form FlopScope billing for one preallocated Winograd level."""

from __future__ import annotations

from dataclasses import asdict, dataclass


def direct_cost(m: int, k: int, n: int) -> int:
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


def winograd_core_cost(m: int, k: int, n: int) -> int:
    """Seven leaf products + 8 input adds + 7 output adds + one copy.

    Dimensions are the complete, even core.  The copy initializes C11 from
    P1 because all four output quadrants are strided views of a full-width
    preallocated output.
    """
    if min(m, k, n) <= 0 or any(value % 2 for value in (m, k, n)):
        raise ValueError("one Winograd level requires positive even dimensions")
    leaf = 7 * direct_cost(m // 2, k // 2, n // 2)
    input_adds = m * k + k * n
    output_adds = 7 * (m // 2) * (n // 2)
    initialization_copy = (m // 2) * (n // 2)
    return leaf + input_adds + output_adds + initialization_copy


def batched_winograd_core_cost(m: int, k: int, n: int) -> int:
    """One batched leaf call with explicit stack fills and reconstruction."""
    if min(m, k, n) <= 0 or any(value % 2 for value in (m, k, n)):
        raise ValueError("one Winograd level requires positive even dimensions")
    leaf = 7 * direct_cost(m // 2, k // 2, n // 2)
    # Each seven-way operand stack has three copied identity blocks and four
    # arithmetic blocks.  Both cost one write per destination element.
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


def candidate_bill(m: int, k: int, n: int) -> Bill:
    baseline = direct_cost(m, k, n)
    if m % 2:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    kc = k - (k % 2)
    nc = n - (n % 2)
    if kc == 0 or nc == 0:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    core = winograd_core_cost(m, kc, nc)
    inner = k - kc
    output = n - nc
    inner_mm = direct_cost(m, inner, nc) if inner else 0
    inner_add = m * nc if inner else 0
    output_mm = direct_cost(m, k, output) if output else 0
    calls = 7 + int(bool(inner)) + int(bool(output))
    total = core + inner_mm + inner_add + output_mm
    # Preserve the original engineering limit.  Two simultaneous ragged
    # dimensions need nine matmul calls and therefore dispatch direct even if
    # their arithmetic bill is lower.
    if calls > 8 or total >= baseline:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    return Bill(
        "winograd_preallocated",
        m,
        k,
        n,
        kc,
        nc,
        core,
        inner_mm,
        inner_add,
        output_mm,
        total,
        baseline,
        calls,
    )


def batched_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Shape-only bill for the memory-bounded batched mutation.

    Odd contracted widths dispatch direct because Mutation B deliberately has
    no full-size correction buffer.  An odd output width appends one direct
    tail call.
    """
    baseline = direct_cost(m, k, n)
    if m % 2 or k % 2:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    nc = n - (n % 2)
    if nc == 0:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    core = batched_winograd_core_cost(m, k, nc)
    output = n - nc
    output_mm = direct_cost(m, k, output) if output else 0
    total = core + output_mm
    calls = 1 + int(bool(output))
    if total >= baseline:
        return Bill("direct", m, k, n, 0, 0, 0, 0, 0, 0, baseline, baseline, 1)
    return Bill(
        "winograd_batched_preallocated", m, k, n, k, nc, core, 0, 0,
        output_mm, total, baseline, calls
    )


def packed_candidate_bill(m: int, k: int, n: int) -> Bill:
    item = batched_candidate_bill(m, k, n)
    if item.strategy == "direct":
        return item
    return Bill(
        "winograd_packed_sequential", item.m, item.k, item.n,
        item.core_k, item.core_n, item.core, item.inner_correction,
        item.inner_add, item.output_tail, item.total, item.direct,
        7 + int(bool(item.output_tail)),
    )



# ---------------------------------------------------------------------------
# Floor lane (tier 7, ``winograd_l6_inplaceleaf``).
#
# Ported verbatim in arithmetic from
# ``headroom/compute_lineage/tier_07_inplace_verbatim_leaves.py``.  The
# ``owned_batched`` family above is untouched and remains the frozen fallback
# route; nothing here changes any bill the incumbent operator dispatches.
# ---------------------------------------------------------------------------


def owned_batched_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Exact bill for the caller-owned, blockwise in-place operator (tier 7)."""
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
    """One quadrant write per node of the 4-ary basis-transform tree."""
    return sum(4 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
               for j in range(1, levels + 1))


def inplace_operand_cost(a_dim: int, b_dim: int, levels: int,
                         std: frozenset) -> int:
    """Tier 7 operand lane: arithmetic blocks plus Psi, no copy residue."""
    if levels < 1:
        raise ValueError("a Winograd core needs at least one level")
    arithmetic = sum(7 ** (j - 1) * (4 if j in std else 3)
                     * (a_dim >> j) * (b_dim >> j)
                     for j in range(1, levels + 1))
    transform = sum(4 ** (j - 1) * (a_dim >> j) * (b_dim >> j)
                    for j in range(1, levels + 1) if j not in std)
    return arithmetic + transform


def graded_decode_cost(m: int, n: int, levels: int, std: frozenset) -> int:
    """Reconstruction writes under a level grading, plus the inverse Psi."""
    arithmetic = sum(7 ** (j - 1) * (7 if j in std else 6)
                     * (m >> j) * (n >> j)
                     for j in range(1, levels + 1))
    transform = sum(4 ** (j - 1) * (m >> j) * (n >> j)
                    for j in range(1, levels + 1) if j not in std)
    return arithmetic + transform


def _best_grade(cost, levels: int, marginal):
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
    return _best_grade(
        lambda std: inplace_operand_cost(a_dim, b_dim, levels, std),
        levels,
        lambda j: (7 ** (j - 1) - 4 ** (j - 1)) * (a_dim >> j) * (b_dim >> j),
    )


def best_decode_grade(m: int, n: int, levels: int):
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


def _floor_depth_route(m: int, k: int, n: int, levels: int, direct_total: int):
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


def floor_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Cheapest exact owned route over all lawful depths (tier-7 model).

    ``floor_candidate_bill(4096, 256, 256).total == 303_096_592``.  This is the
    analytical floor, not what any NumPy schedule can spend: it prices the
    ``3**L`` verbatim leaves at zero, which a per-leaf operand-descriptor
    dispatch buys and a single strided ``fnp.matmul`` cannot.  See
    ``depth6_winograd.realized_depth_bill`` for the schedule that is actually
    executed and billed.
    """
    baseline = owned_batched_candidate_bill(m, k, n)
    best = baseline
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
        route = _floor_depth_route(m, k, n, levels, baseline.direct)
        if route is not None and route.total < best.total:
            best = route
        levels += 1
    return best
