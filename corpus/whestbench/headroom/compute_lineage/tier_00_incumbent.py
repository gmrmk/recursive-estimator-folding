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


def batched_winograd_l2_core_cost(m: int, k: int, n: int) -> int:
    """Two Winograd levels with all 49 leaves in one batched product."""
    if min(m, k, n) <= 0 or any(value % 4 for value in (m, k, n)):
        raise ValueError("two Winograd levels require multiples of four")
    leaves = 49 * direct_cost(m // 4, k // 4, n // 4)
    transforms = 77 * (m * k + k * n + m * n) // 16
    return leaves + transforms


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

    One odd contracted column is handled as an exact real-arithmetic outer
    product after the even Winograd core.  Two simultaneous odd dimensions
    stay direct so the existing one-column scratch never has two owners.
    """
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
    # Add the outer product to the core and capture the aliased input column.
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
        output_mm, total, baseline, calls
    )


def owned_batched_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Exact bill for the caller-owned, blockwise in-place operator.

    Direct dispatch copies each input row once into bounded scratch.  The
    Winograd core keeps the frozen batched bill; only an odd output needs the
    final copy from its one-column pre-overwrite tail scratch.
    """
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


def grouped_l2_candidate_bill(m: int, k: int, n: int) -> Bill:
    """Select the cheapest exact owned route, including modulo-four fringes."""
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
                "winograd_batched_owned_dual_odd",
                m,
                k,
                n,
                core_k,
                core_n,
                core,
                inner_correction,
                inner_add,
                output_tail,
                total,
                baseline.direct,
                3,
            )
    if m % 4:
        return best

    core_k = k - k % 4
    core_n = n - n % 4
    if core_k == 0 or core_n == 0:
        return best
    inner_width = k - core_k
    output_width = n - core_n
    core = batched_winograd_l2_core_cost(m, core_k, core_n)
    inner_correction = (
        direct_cost(m, inner_width, core_n) if inner_width else 0
    )
    inner_add = m * core_n if inner_width else 0
    output_tail = (
        direct_cost(m, k, output_width) + m * output_width
        if output_width
        else 0
    )
    total = core + inner_correction + inner_add + output_tail
    if total >= best.total:
        return best
    strategy = (
        "winograd_l2_mod4_fringe"
        if inner_width or output_width
        else "winograd_l2_grouped"
    )
    return Bill(
        strategy,
        m,
        k,
        n,
        core_k,
        core_n,
        core,
        inner_correction,
        inner_add,
        output_tail,
        total,
        baseline.direct,
        1 + int(bool(inner_width)) + int(bool(output_width)),
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
