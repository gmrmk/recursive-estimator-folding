"""Suite tier 2: LAYER 2 is evaluated through the CReLU antipodal channel split.

ONE SUBSTANTIVE CHANGE
======================
The suite incumbent bills all 32 layers at one anonymous (4096, 256, 256) tile
price -- 32 x 15.75 x 303,096,592 -- and its own docstring names the frozen
assumption as the uniformity itself.  This tier breaks it at exactly one layer:
layer 2, whose 64,512 input rows are not 64,512 independent activations but
32,256 ANTIPODAL PAIRS, because the design is antipodally doubled and the net is
bias-free.  Layers 1 and 3..32 are left at the crowned tier-7 call price,
unchanged, and this tier does not touch them.

EXACTNESS IDENTITY
==================
Observed facts this rests on, both from the deployed source rather than from
memory:

  (F1) The design is antipodally doubled: 126 frames x 256 rows = 32,256 base
       directions, evaluated together with their negatives to give 64,512.
       [experiments/v31_guards/package_source/kerdock_v3_estimator.py:47,
        n_base = 126 * 256; core/CODEX_HANDOFF_20260810.md:397-399, "the code's
        output is (32256, 256) with antipodes by negation".]
  (F2) The network is bias-free.  [core/CORPUS.md:15, "a fixed, bias-free,
       width-256, depth-32 Gaussian-He MLP"; the deployed ``MLP`` carries
       ``weights`` and no bias term.]

Write W1 for the effective first-layer matrix (the deployed
``rotation.T @ mlp.weights[0]``) and W2 for the second, both 256 x 256, and let
u be a base design row.  By (F2) the first-layer preactivation is linear, so the
antipodal partner's preactivation is an exact negation:

    z  = u W1                    z(-u) = (-u) W1 = -z          [no bias term]

The pair's layer-1 activations are relu(z) and relu(-z), and for every real x

    relu(x) - relu(-x) = x                  (odd channel, exactly linear)
    relu(x) + relu(-x) = |x|                (even channel, nonlinear)

both identities holding at x = 0 as well.  Hence relu(z) = (|z| + z)/2 and
relu(-z) = (|z| - z)/2, and the pair's LAYER-2 PREACTIVATIONS are

    z2(+) = relu(z)  W2 = ( |z| W2  +  u (W1 W2) ) / 2
    z2(-) = relu(-z) W2 = ( |z| W2  -  u (W1 W2) ) / 2

exactly, over any ring.  The two rows of the pair therefore share ONE even
channel  e = |z| W2  and differ only by ONE odd channel  o = u (W1 W2).  The
even channel is a real matmul, but over 32,256 rows instead of 64,512 -- half
the rows.  The odd channel is not a matmul at all: u ranges over the design, and
the design is 126 phased-Hadamard frames, so with M = W1 W2 precomputed once per
net the whole odd channel is the SAME phased-WHT butterfly the deployed layer-1
hook already runs, with M substituted for W1:

    frame s's odd block  =  mean_chi * H diag(phase_s) M / 16
    [kerdock_v3_estimator.py:103-132, ``_first_sample_matmul``, verbatim shape]

So layer 2's paid matmul work is the even channel alone -- half the rows -- plus
one amortized 256-cubed precompute and one butterfly pass.

``_selfcheck`` proves this rather than arguing it: it builds the frame design by
the deployed construction, runs both routes over the integers, and asserts every
one of the 2 x F x n layer-2 preactivation rows is equal entry for entry,
including the exactness of the division by two (e +/- o is proved even, so the
halving is not a rounding step at all).

WHY IT DOES NOT RECURSE TO LAYER 3 (the boundary, stated because it is the gate)
===============================================================================
The split is free at layer 2 and nowhere deeper, and the reason is sharp: the
split is free exactly where the pair is ANTIPODAL IN PREACTIVATION.  At layer 1
the even part of the pair is identically zero -- z(-u) = -z(u) -- which is what
makes relu(z) - relu(-z) collapse to the linear z.  At layer 2 the even part is
e/2, which is not zero, so the pair (z2(+), z2(-)) is no longer a
plus/minus pair, and

    relu(z2(+)) - relu(z2(-))   !=   z2(+) - z2(-)

in general.  There is no linear odd channel at layer 3 to ride, and the generic
per-layer rewrite relu(x) = x/2 + |x|/2 buys nothing either: it turns one matmul
W3 relu(.) into TWO (a telescoped linear chain plus an even channel), which
costs more than it saves.  CReLU pays exactly once, at the first nonlinearity of
a bias-free net evaluated on an antipodally doubled design.  ``_selfcheck``
measures the boundary instead of asserting it: it exhibits, from the same
integer instance, coordinates where the layer-2 pair fails to be antipodal and
where the layer-3 pair difference is not the preactivation difference.

DOUBLE-COUNT GATE (checked hostilely; the tier survives it BECAUSE the butterfly
appears here as a COST, not as a credit)
===============================================================================
This is the gate that has to be answered in the presence of the staged layer-1
FWHT splice, and it is answered three ways.

  (1) *Against the incumbent.*  ``suite_00_incumbent.suite_bill_per_net``
      computes ``layers * tiles * call`` with ``layers, tiles = 32, 64512 / m``
      and ``call`` the shape-anonymous tier-7 bill at (4096, 256, 256).  The
      layer index never enters the price, and no antipodal or design structure
      appears anywhere in the tier-7 module, whose bill is a function of
      (m, k, n) alone.  Layer 2 is therefore billed for all 64,512 rows as
      independent rows, and the pair sharing this tier introduces is not a
      saving already banked.  ``_selfcheck`` asserts the incumbent total equals
      504 * call and the layer-2 slice equals 15.75 * call exactly.

  (2) *Against the layer-1 FWHT tier.*  The deployed layer-1 hook already
      evaluates the design by the phased-WHT butterfly and already emits only
      32,256 rows [kerdock_v3_estimator.py:103-132, 114].  That is precisely why
      the staged layer-1 splice is contested ground.  It does not contaminate
      this tier, because this tier CHARGES the butterfly instead of crediting
      it: the odd channel is one ADDITIONAL butterfly pass over a DIFFERENT
      matrix (M = W1 W2, not W1), billed here at full price, and no term of
      layer 1's bill is reduced by a single FLOP.  Whether the layer-1 splice
      is adopted or rejected, this tier's arithmetic is unchanged -- it composes
      by addition, not by sharing.  ``_selfcheck`` asserts layers 1 and 3..32
      together still cost exactly 31 * the incumbent layer slice.

  (3) *Against layer 1's own output.*  The route consumes |z| on the 32,256 base
      rows, which is elementwise-derived from preactivations layer 1 already
      produces; it re-charges none of layer 1's matmul.  It charges the abs pass
      anyway (8,257,536), even though the incumbent's matmul-only model charges
      no elementwise op at all -- including the 16,515,072 relu ops the direct
      layer-2 route needs and this route does not.  Every elementwise term in
      this bill is a conservative addition against a baseline that pays none.

The certified per-call floor (303,096,592 at anonymous (4096, 256, 256)) is
untouched: nothing inside a call is rescheduled.  The tier removes HALF THE
CALLS at one layer, because at that layer half the rows were the negatives of
the other half.

UNCLAIMED, ON PURPOSE
=====================
Two further savings this route makes available are deliberately NOT taken, so
that the one-substantive-change law is not quietly broken and the bill stays
conservative:

  * Layer 1 needs only the 32,256 base rows, and the deployed hook already emits
    only those.  Its bill stays at the incumbent's full 15.75 tiles here.
  * The antipodal negation pass that materializes the second half of layer 1's
    output becomes dead work under this route -- layer 2 no longer reads it.
    Not deducted.

WHAT IS CHARGED, CONSERVATIVELY
===============================
Per net, for layer 2 (call = 303,096,592, the crowned tier-7 price):

  even channel, 32,256 rows, EXACTLY TILED at BLOCK_ROWS = 4096:
      7 x call(4096, 256, 256)                          2,121,676,144
      1 x call(3584, 256, 256)                            265,448,912
                                                       ---------------
                                                        2,387,125,056
  |z| pass, 32,256 x 256                                    8,257,536
  W2 half-scale, 256 x 256 (exact in binary FP)                65,536
  precompute M = W1 W2, direct_cost(256,256,256)           33,488,896
  odd channel butterfly, 14 x 32,256 x 256                115,605,504
  recombination e +/- o, 2 x 32,256 x 256                  16,515,072
                                                       ---------------
  layer-2 CReLU route                                   2,561,057,600
  layer-2 incumbent slice, 15.75 x call                 4,773,771,324
  saving per net                                        2,212,713,724

Three conservative choices, each named because each costs the tier something:

  * The even channel is billed at its EXACT TILING (7 full 4096-row calls plus
    one 3584-row call), 2,387,125,056, not at the incumbent's linear
    7.875 x call = 2,386,885,662.  The tier-7 bill is affine in m, not linear --
    the right-hand stack fill is charged once per call regardless of m
    [CODEX_HANDOFF_20260810.md, "Row-linearity, stated exactly"] -- so the
    linear convention under-charges a partial tile by 239,394.  We pay it.
    The baseline stays at the incumbent's frozen 15.75 x call, which
    under-charges ITSELF by 478,788 against its own exact tiling.  Both slips
    are taken against this tier.
  * The butterfly is priced at the deployed FlopScope v0.10 convention of 14 ops
    per element -- 1 seed multiply, 8 radix-2 stages at 1.5 (copyto + add +
    subtract, movement billed at 1/element), 1 final scale -- not at the
    2048-add-per-row arithmetic-only count.  14 x 8,257,536 = 115,605,504, the
    same figure the deployed layer-1 hook bills [CODEX_HANDOFF_20260810.md §3;
    corroborated at experiments/m184_trichotomy_upward/M184_G0_NOTES.md:80-83].
    ``_selfcheck`` MEASURES the count off a running butterfly rather than
    asserting the formula.
  * The precompute is billed at the source's own ``direct_cost(m,k,n) =
    m*n*(2k-1)`` = 33,488,896, not at the cheaper tier-7 route it would in fact
    be entitled to.

The two constant folds are exact, not approximations: the 1/2 on the odd channel
is absorbed into the butterfly's existing final scale (MEAN_CHI_256/16 becomes
MEAN_CHI_256/32, a power-of-two change of one constant, costing no op and
introducing no rounding), and the 1/2 on the even channel is one exact binary
halving of W2, charged at 65,536.

REROUTE CLASS, NOT APPROXIMATION -- WITH THE FLAG STATED PLAINLY
================================================================
Over the reals and over the integers this route is bit-identical to the direct
route, and ``_selfcheck`` checks that literally.  Over f32 it is a
reassociation, and it is a stronger one than a pure summation reorder: it uses
matrix-product associativity, u(W1 W2) in place of (u W1)W2, and it forms
W2 relu(z) as the half-sum of two channels.  Both are the reschedule class the
adopted Winograd fringe route already sits in, and no value is approximated, no
rank is reduced, no term is dropped.  Flagged, not buried, and the one specific
exposure is named: e +/- o is a cancelling form wherever the two channels are
close in magnitude and opposite in sign, which is the same conditioning caveat
Strassen-class rerouting carries.  No f32 repricing: every op counted here is
one f32 multiply, add, subtract, sign flip or copy, priced at 1, the unit the
incumbent's call bill uses.

SLOPE NOTE (implementation shape, the V5-d3 law)
================================================
The metered win survives only if the route runs as few large kernels.  The shape
it runs in:

  * The even channel is the incumbent's own batched tile dispatch verbatim, only
    with 8 row-blocks instead of 16.  ``RowBlockedBatchedWinograd`` is already
    row-blocked at BLOCK_ROWS = 4096 and already constructed at
    ``2 * n_base`` rows, so halving the row count halves the block loop and
    changes no kernel, no packing and no operand layout.  This is the whole
    reason the win is not repaid in residual time: the deleted work is eight
    entire block iterations of the existing kernel, not a per-row special case.
  * The odd channel is ONE extra invocation of the existing
    ``_first_sample_matmul`` butterfly, on the existing ``_wht_scratch``
    (126, 128, 256) buffer, with M passed where W1 is passed today -- 126 frame
    blocks of 256 KiB f32, eight in-register butterfly passes each, one
    sequential sweep.  No new buffer, no new kernel, no new dispatch pattern.
  * The precompute M = W1 W2 is one 256x256x256 GEMM per net, hoisted out of the
    sample loop next to the existing ``rotation.T @ mlp.weights[0]`` fold, which
    is already done once per net in ``predict``.  It amortizes over the whole
    net, and at 33.5M against a 150.5G bill it is 0.02%.
  * The |z| pass and the recombination fuse into the loads they feed: |z| is a
    sign-clear on the layer-1 output tile as it is packed for the even-channel
    GEMM, and e +/- o is a single fused add/sub pass writing the two halves of
    the layer-2 output block that layer 3 then reads. Both are charged at full
    price above regardless of whether the fusion lands, so the accounting does
    not depend on it.
  * Layers 1 and 3..32 keep the incumbent's dispatch verbatim, so this tier adds
    exactly one new seam to the schedule and touches no other layer's shape.

Run with cwd = the repo root (relative import of the incumbent's tier-7 module).
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass

_T7_PATH = "corpus/whestbench/headroom/compute_lineage/tier_07_inplace_verbatim_leaves.py"

# Production shape, observed in kerdock_v3_estimator.py and CODEX_HANDOFF §3.
FRAMES = 126                      # phase_stop - phase_start = 128 - 2
WIDTH = 256                       # ctx.width
BASE_ROWS = FRAMES * WIDTH        # n_base = 126 * 256 = 32,256
DESIGN_ROWS = 2 * BASE_ROWS       # antipodally doubled = 64,512
LAYERS = 32
TILE_ROWS = 4096                  # BLOCK_ROWS in row_blocked_winograd.py

# FlopScope v0.10 butterfly convention: 1 seed multiply + log2(n) stages at
# 1.5/element (copyto + add + subtract, movement billed at 1) + 1 final scale.
_BUTTERFLY_SEED_AND_SCALE = 2
_BUTTERFLY_PER_STAGE_HALVES = 3   # three E/2 passes per radix-2 stage


def _t7():
    spec = importlib.util.spec_from_file_location("t7base", _T7_PATH)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def _log2_exact(n: int) -> int:
    if n < 1 or n & (n - 1):
        raise ValueError(f"{n} is not a power of two")
    return n.bit_length() - 1


def direct_cost(m: int, k: int, n: int) -> int:
    """The source's own counterfactual price, cost_model.py:8-11."""
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


def butterfly_ops(rows: int, width: int, out_width: int) -> int:
    """Ops one phased-WHT butterfly block costs at the deployed convention.

    ``rows`` design rows per frame (== width), ``out_width`` output columns.
    Two whole-block passes (seed multiply, final scale) plus 3 half-block passes
    per radix-2 stage.  Integer by construction: the halves pair up.
    """
    elements = rows * out_width
    if elements % 2:
        raise ValueError("half-block passes need an even element count")
    stages = _log2_exact(rows)
    return (elements * _BUTTERFLY_SEED_AND_SCALE
            + stages * _BUTTERFLY_PER_STAGE_HALVES * (elements // 2))


def even_channel_tiled_cost(call4096: int, call3584: int) -> int:
    """Exact tiling of 32,256 rows at BLOCK_ROWS = 4096: 7 full + one 3584."""
    full, remainder = divmod(BASE_ROWS, TILE_ROWS)
    if remainder != TILE_ROWS - 512:
        raise ValueError("row split is not the frozen 7 x 4096 + 3584")
    return full * call4096 + call3584


@dataclass(frozen=True)
class SuiteBill:
    strategy: str
    call_total: int
    layers: int
    tiles_per_layer: float
    layer2_even_matmul: int
    layer2_abs_pass: int
    layer2_w2_halfscale: int
    layer2_precompute: int
    layer2_odd_butterfly: int
    layer2_recombination: int
    layer2_total: int
    other_layers: int
    total: int

    def breakdown(self) -> dict:
        return {
            "layer2_even_matmul_32256_rows": self.layer2_even_matmul,
            "layer2_abs_pass": self.layer2_abs_pass,
            "layer2_w2_halfscale": self.layer2_w2_halfscale,
            "layer2_precompute_W1W2": self.layer2_precompute,
            "layer2_odd_channel_butterfly": self.layer2_odd_butterfly,
            "layer2_recombination": self.layer2_recombination,
            "layer2_total": self.layer2_total,
            "layers_1_and_3_to_32": self.other_layers,
            "total": self.total,
        }


def suite_bill_per_net(m: int = TILE_ROWS, k: int = WIDTH, n: int = WIDTH) -> SuiteBill:
    """Layer 2 through the CReLU antipodal split; every other layer untouched."""
    t7 = _t7()
    call = t7.inplace_verbatim_leaves_candidate_bill(m, k, n).total
    call_tail = t7.inplace_verbatim_leaves_candidate_bill(
        BASE_ROWS % TILE_ROWS, k, n
    ).total

    layer_slice = call * DESIGN_ROWS // m
    if layer_slice * m != call * DESIGN_ROWS:
        raise ValueError("tile count is not exact; refusing a rounded bill")

    even = even_channel_tiled_cost(call, call_tail)
    abs_pass = BASE_ROWS * WIDTH
    halfscale = WIDTH * WIDTH
    precompute = direct_cost(WIDTH, WIDTH, WIDTH)
    odd = FRAMES * butterfly_ops(WIDTH, WIDTH, WIDTH)
    recombine = DESIGN_ROWS * WIDTH

    layer2 = even + abs_pass + halfscale + precompute + odd + recombine
    others = (LAYERS - 1) * layer_slice
    return SuiteBill(
        "crelu_antipodal_channel_split_layer2",
        call,
        LAYERS,
        DESIGN_ROWS / m,
        even,
        abs_pass,
        halfscale,
        precompute,
        odd,
        recombine,
        layer2,
        others,
        layer2 + others,
    )


# ---------------------------------------------------------------------------
# Executable exactness.  Pure integers, so "identical results" is literal.
# ---------------------------------------------------------------------------


def _rng(seed: int):
    state = seed

    def nxt(lo: int, hi: int) -> int:
        nonlocal state
        state = (state * 1103515245 + 12345) % 2147483648
        return lo + state % (hi - lo + 1)

    return nxt


def _butterfly(phase: list, mat: list, scale: int, counter: list) -> list:
    """The deployed ``_first_sample_matmul`` block, op for op.

    Returns ``scale * H diag(phase) mat`` for the H the same butterfly builds,
    and counts every multiply, copy, add and subtract it performs.
    """
    n = len(phase)
    w = len(mat[0])
    frames = [[phase[i] * mat[i][j] for j in range(w)] for i in range(n)]
    counter[0] += n * w                                      # seed multiply
    half = 1
    while half < n:
        for base in range(0, n, half * 2):
            for i in range(base, base + half):
                left = frames[i]
                right = frames[i + half]
                scratch = list(left)
                counter[0] += w                              # copyto
                frames[i] = [scratch[j] + right[j] for j in range(w)]
                counter[0] += w                              # add
                frames[i + half] = [scratch[j] - right[j] for j in range(w)]
                counter[0] += w                              # subtract
        half *= 2
    out = [[scale * x for x in row] for row in frames]
    counter[0] += n * w                                      # final scale
    return out


def _hadamard_by_butterfly(n: int) -> list:
    """H exactly as the deployed setup builds it: the butterfly run on I."""
    eye = [[int(i == j) for j in range(n)] for i in range(n)]
    return _butterfly([1] * n, eye, 1, [0])


def _matmul(A: list, B: list) -> list:
    return [[sum(A[i][t] * B[t][j] for t in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]


def _relu(x: int) -> int:
    return x if x > 0 else 0


def _selfcheck() -> None:
    call_probe = _t7().inplace_verbatim_leaves_candidate_bill

    # ---- 1. Shape anchors, from the deployed source's own constants. -------
    assert BASE_ROWS == 32256, BASE_ROWS
    assert DESIGN_ROWS == 64512, DESIGN_ROWS
    assert DESIGN_ROWS == 2 * BASE_ROWS
    assert DESIGN_ROWS == 15.75 * TILE_ROWS
    assert BASE_ROWS == 7 * TILE_ROWS + 3584

    # ---- 2. The butterfly builds a real Hadamard matrix, and its op count
    #         is MEASURED off the running code, not read off the formula. ----
    for n in (8, 16, 32, 256):
        H = _hadamard_by_butterfly(n)
        assert all(abs(x) == 1 for row in H for x in row), f"H not +-1 at n={n}"
        gram = _matmul(H, [[H[c][r] for c in range(n)] for r in range(n)])
        assert gram == [[n if i == j else 0 for j in range(n)] for i in range(n)], (
            f"H is not Hadamard at n={n}")
        nxt = _rng(9091 + n)
        phase = [1 if nxt(0, 1) else -1 for _ in range(n)]
        mat = [[nxt(-9, 9) for _ in range(n)] for _ in range(n)]
        counter = [0]
        fast = _butterfly(phase, mat, 3, counter)
        slow = _matmul(
            [[3 * H[r][i] * phase[i] for i in range(n)] for r in range(n)], mat
        )
        assert fast == slow, f"butterfly is not scale*H*diag(phase)*M at n={n}"
        assert counter[0] == butterfly_ops(n, n, n), (
            f"n={n}: butterfly performed {counter[0]} ops, bill charges "
            f"{butterfly_ops(n, n, n)}")

    # Production width: the per-element price must be the deployed 14, and the
    # per-net odd-channel bill the deployed layer-1 hook's own 115,605,504.
    assert butterfly_ops(WIDTH, WIDTH, WIDTH) == 14 * WIDTH * WIDTH
    assert FRAMES * butterfly_ops(WIDTH, WIDTH, WIDTH) == 115605504
    assert FRAMES * WIDTH * WIDTH == 8257536

    # ---- 3. THE IDENTITY: both routes give bit-identical layer-2 rows. -----
    #         Built on the deployed construction: base rows are
    #         alpha * H diag(phase_s), full design = base rows and negatives,
    #         net bias-free, so layer-1 preactivations negate exactly.
    for n, frames, alpha in ((8, 3, 3), (16, 2, 1), (8, 4, 5)):
        H = _hadamard_by_butterfly(n)
        nxt = _rng(31337 + n * 100 + frames)
        phases = [[1 if nxt(0, 1) else -1 for _ in range(n)]
                  for _ in range(frames)]
        W1 = [[nxt(-9, 9) for _ in range(n)] for _ in range(n)]
        W2 = [[nxt(-9, 9) for _ in range(n)] for _ in range(n)]

        base = [[alpha * H[r][i] * phases[s][i] for i in range(n)]
                for s in range(frames) for r in range(n)]
        assert len(base) == frames * n
        full = base + [[-x for x in row] for row in base]

        # Direct route, as the incumbent bills it: every row independent.
        z_full = _matmul(full, W1)
        a_full = [[_relu(x) for x in row] for row in z_full]
        z2_direct = _matmul(a_full, W2)

        # Bias-freeness is what makes the pair antipodal in preactivation.
        for p in range(len(base)):
            assert z_full[len(base) + p] == [-x for x in z_full[p]], (
                "antipodal preactivation negation failed; the net is not "
                "bias-free or the design is not antipodally doubled")

        # CReLU route: one even channel and one odd channel per PAIR.
        z_base = z_full[: len(base)]
        even = _matmul([[abs(x) for x in row] for row in z_base], W2)
        M = _matmul(W1, W2)
        odd = _matmul(base, M)

        # The odd channel really is the same butterfly, frame by frame.
        odd_bf = []
        for s in range(frames):
            odd_bf.extend(_butterfly(phases[s], M, alpha, [0]))
        assert odd_bf == odd, "butterfly does not reproduce the odd channel"

        z2_crelu = [None] * len(full)
        for p in range(len(base)):
            for j in range(n):
                plus = even[p][j] + odd[p][j]
                minus = even[p][j] - odd[p][j]
                # The halving is exact, not a rounding step: e +/- o = 2*W2 relu.
                assert plus % 2 == 0 and minus % 2 == 0, (
                    "channel sum is odd; the /2 would not be exact")
            z2_crelu[p] = [(even[p][j] + odd[p][j]) // 2 for j in range(n)]
            z2_crelu[len(base) + p] = [
                (even[p][j] - odd[p][j]) // 2 for j in range(n)
            ]
        assert z2_crelu == z2_direct, (
            f"CReLU route differs from the direct route at n={n}, "
            f"frames={frames}, alpha={alpha}")

        # ---- 4. THE BOUNDARY, measured: it does not recurse to layer 3. ----
        # The layer-2 pair is not antipodal, so the layer-3 pair difference is
        # not the preactivation difference and no linear odd channel survives.
        not_antipodal = 0
        difference_breaks = 0
        for p in range(len(base)):
            plus = z2_direct[p]
            minus = z2_direct[len(base) + p]
            for j in range(n):
                if minus[j] != -plus[j]:
                    not_antipodal += 1
                if _relu(plus[j]) - _relu(minus[j]) != plus[j] - minus[j]:
                    difference_breaks += 1
        assert not_antipodal > 0, (
            "layer-2 pair is antipodal everywhere; the even channel would be "
            "zero and the boundary argument would be wrong")
        assert difference_breaks > 0, (
            "relu(a)-relu(b) == a-b everywhere at layer 2; the split would "
            "recurse and this docstring's boundary claim would be false")

    # ---- 5. Double-count gate, and single-change containment. --------------
    bill = suite_bill_per_net()
    call = bill.call_total
    assert call == 303096592, call
    incumbent = 504 * call
    assert incumbent == 152760682368, incumbent
    layer_slice = call * DESIGN_ROWS // TILE_ROWS
    assert layer_slice == 4773771324, layer_slice
    assert incumbent == LAYERS * layer_slice

    # Only layer 2 moves.  Layers 1 and 3..32 are the incumbent's, to the FLOP.
    assert bill.other_layers == (LAYERS - 1) * layer_slice
    assert bill.other_layers == incumbent - layer_slice
    assert bill.total == incumbent - layer_slice + bill.layer2_total
    assert bill.total < incumbent

    # The butterfly is a COST here, never a credit: layer 1 is not reduced, so
    # this tier composes with the layer-1 FWHT splice by addition, not sharing.
    assert bill.layer2_odd_butterfly > 0
    assert bill.other_layers % layer_slice == 0

    # ---- 6. Conservative-pricing gate: we bill the exact tiling, which is
    #         strictly above the incumbent's own linear convention. ----------
    call_tail = call_probe(3584, WIDTH, WIDTH).total
    linear = call * BASE_ROWS // TILE_ROWS
    assert linear * TILE_ROWS == call * BASE_ROWS
    assert bill.layer2_even_matmul == 7 * call + call_tail
    assert bill.layer2_even_matmul > linear, (
        "exact tiling must be the more expensive of the two conventions")
    # ...and the baseline stays at the incumbent's frozen linear slice, which
    # under-charges itself against its own exact tiling.  Slip taken against us.
    assert layer_slice < 15 * call + call_probe(3072, WIDTH, WIDTH).total

    # ---- 7. The bill's own arithmetic. -------------------------------------
    assert bill.layer2_even_matmul == 2387125056, bill.layer2_even_matmul
    assert bill.layer2_abs_pass == 8257536
    assert bill.layer2_w2_halfscale == 65536
    assert bill.layer2_precompute == 33488896
    assert bill.layer2_odd_butterfly == 115605504
    assert bill.layer2_recombination == 16515072
    assert bill.layer2_total == 2561057600, bill.layer2_total
    assert incumbent - bill.total == 2212713724
    assert bill.total == 150547968644, bill.total


if __name__ == "__main__":
    _selfcheck()
    print("selfcheck: Hadamard construction, MEASURED butterfly op count, "
          "CReLU exactness (bit-for-bit over the integers, exact halving), "
          "measured layer-3 non-recursion boundary, double-count gate, "
          "single-change containment and conservative-pricing gate all pass")
    b = suite_bill_per_net()
    incumbent = 504 * b.call_total
    print(b.strategy)
    for key, value in b.breakdown().items():
        print(f"  {key:>32} {value:>15,}")
    print(f"  {'incumbent':>32} {incumbent:>15,}")
    print(f"  {'saving':>32} {incumbent - b.total:>15,}")
    print(f"  ratio vs incumbent                {b.total / incumbent:.9f}")
    print("total:", b.total)
