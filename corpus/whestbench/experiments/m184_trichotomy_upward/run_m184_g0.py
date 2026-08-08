"""M184 G0 gate runner. Predeclared in M184_PREDECLARATION.md.

ONE mutation under test: extending the dead/on/kink trichotomy upward from
the 3 terminal layers (where frozen v3 already applies it) into the middle
layers 2..29 (weight indices 1..28) of width-256 depth-32 nets.  Static
count only -- no estimator build, no datasets, no submissions.

On 3 synthetic He f32 256x32 nets (t3-style, seeds 101/202/303; identical
construction to m180 run_m180_g0.py), using
  (i)  the analytic diagonal-Gaussian pass (alpha per neuron per layer), and
  (ii) one Kerdock pilot at the frozen design: the first 4 trimmed frames
       (1024 directions) + antipodes = 2048 paths at exact radius
       mean_chi(256), rotated by one Haar rotation seeded like v3's
       predict() (rotation seed = net seed).  The first 256 directions +
       antipodes = the 512-path pilot block, row-for-row v3's own loop
       pilot (pilot_base = 256); all 2048 rows = v3's fold pilot
       (fold_pilot_base = 1024).  DEVIATION (loud): the predeclaration
       names "one 512-path pilot"; the extra 3 frames are forwarded ONLY
       so the v3 baseline's fold-layer partitions can be replayed
       row-for-row (v3 consults 2048 fold-pilot rows).  Certain-on /
       certain-dead classification uses ONLY the 512-path block.

Certainty thresholds (predeclaration: "a margin that makes
misclassification probability < 1e-6 per neuron and STATE the
calculation"):
  certain-on(l, j):   alpha[l][j] > +6.7  AND  min over the 512 pilot
                      paths of the pre-activation > 0
  certain-dead(l, j): alpha[l][j] < -6.7  AND  max over the 512 pilot
                      paths of the pre-activation <= 0
  Calculation: under the diagonal-Gaussian surrogate for the sampling
  distribution the per-sample tail mass at |alpha| = 6.7 is
  Phi(-6.7) = erfc(6.7/sqrt(2))/2 ~= 1.04e-11.  Union bound over all
  n = 2 * 32,256 = 64,512 realized sample paths:
  64,512 * Phi(-6.7) ~= 6.7e-7 < 1e-6 per neuron.  (alpha = 4 would give
  64,512 * 3.2e-5 ~= 2 -- useless; hence 6.7, not the predeclaration's
  illustrative 4.)  The 512-path pilot min/max is the second,
  distribution-free signal on the pilot paths themselves.

Billed-FLOP model (v0.10 pricing conventions, per-op bills verbatim from
t3 capped_fold3.py: matmul 2mkn - mn; pointwise 1/elem; gather 4/output
element; sort 8 n ceil(log2 n); int concat 2/elem) with the v3-specific
substitutions: the loop sample matmul is billed by the frozen
RowBlockedBatchedWinograd owned bill (cost_model.owned_batched_candidate_
bill, ported verbatim as plain arithmetic) and the first product is the
exact phased-WHT butterfly (14 n w, counted op-by-op below).

INCREMENT ACCOUNTING (what M184 adds over v3, and only that):
  (a) dead-column skips: ZERO by construction.  v3's loop pruning drops
      every column with alpha < -2 whose 512-row pilot never fires;
      certain-dead (alpha < -6.7 AND pilot max <= 0) is a strict subset,
      so certain-dead intersect v3-active = empty (asserted numerically).
  (b) on-run linear composition: billed via a dynamic program over
      collapse schedules.  A segment [m+1 .. e] materializes only kink
      columns per-sample at layers m+1..e-1 (certain-on columns stay
      folded; each carrier's fold matrix is updated once per layer per
      net -- the W^3-style precompute -- billed at full matmul price),
      then collapses to a plain materialized activation at layer e.
      The length-1 segment reproduces v3's per-layer bill EXACTLY
      (asserted against an independently written v3 per-layer bill), so
      DP total <= v3 total always, and every saving is attributable to
      realized certain-on runs.  The M184 arm also pays, per fold step:
      the on-candidate pilot confirmation matmul, the extra index sorts,
      and all gathers at 4/element.
  (c) gather/sort overhead: charged inside both arms at the same prices.

Gates (predeclared): KILL if projected net billed reduction < 15%;
PROMOTE only if >= 20%.  Ambiguity resolution (conservative, stated):
gate on the per-net reductions -- KILL if ANY net < 15% or the geomean
< 15%; PROMOTE only if ALL nets >= 20% and the geomean >= 20%.

Firewall: synthetic nets only; the only file loaded is the frozen
estimator's shipped sampling asset kerdock_phases.npz (read-only); no
dataset, truth, scorer, or submission access; all writes stay inside
this experiment directory; single process, plain numpy (sanctioned).
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)

WIDTH, DEPTH = 256, 32
N_FRAMES = 126
N_BASE = N_FRAMES * WIDTH          # 32,256 base directions
BIG = 2 * N_BASE                   # 64,512 antipodal sample rows
G0_NET_SEEDS = (101, 202, 303)
MEAN_CHI_256 = 15.98438266660852747
DEAD_ALPHA = -2.0                  # frozen v3 base_estimator.dead_alpha
ON_ALPHA_FOLD = 3.0                # frozen v3 fold3_estimator.on_alpha
CERTAIN_ALPHA = 6.7                # M184 certainty margin (see docstring)
PILOT_DIRS = 256                   # v3 pilot_base
FOLD_PILOT_DIRS = 1024             # v3 fold_pilot_base
P2 = 2 * PILOT_DIRS                # 512 pilot paths
FP2 = 2 * FOLD_PILOT_DIRS          # 2048 fold-pilot paths
BLOCK_ROWS = 4096                  # frozen row_blocked_winograd.BLOCK_ROWS
KILL_REDUCTION = 0.15
PROMOTE_REDUCTION = 0.20
W = WIDTH


# ----------------------------------------------------------------- nets
def he_mlp_weights(seed: int) -> list[np.ndarray]:
    """He-init f32 width-256 depth-32 net (verbatim m180 run_m180_g0.py)."""
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


# ------------------------------------------------- Kerdock pilot points
def normalized_hadamard() -> np.ndarray:
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
    return (hadamard / 16.0).astype(np.float32)


def load_kerdock_pilot_frames() -> np.ndarray:
    """First FOLD_PILOT_DIRS/WIDTH trimmed frames as direction rows.

    Verbatim m180 load_kerdock_frames construction, sliced to 4 frames.
    Rows are at exact radius mean_chi(256).
    """
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    if phases.shape != (N_FRAMES, WIDTH):
        raise RuntimeError(f"unexpected trimmed phase shape {phases.shape}")
    h_norm = normalized_hadamard()
    count = FOLD_PILOT_DIRS // WIDTH
    frames = (
        MEAN_CHI_256 * (h_norm[None, :, :] * phases[:count, None, :])
    ).astype(np.float32)
    radii = np.linalg.norm(frames, axis=2)
    if not np.allclose(radii, MEAN_CHI_256, rtol=1e-5):
        raise RuntimeError("Kerdock directions lost the fixed radius")
    return frames.reshape(-1, WIDTH)


def haar_rotation(seed: int) -> np.ndarray:
    """Mirror of frozen estimator.py _haar_rotation (f32 QR, sign-fixed)."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    return (rotation * signs[None, :]).astype(np.float32)


# --------------------------------------------------- analytic diagonal pass
_ERF = np.vectorize(math.erf, otypes=[np.float64])


def diagonal_gaussian_pass_alphas(weights: list[np.ndarray]) -> list[np.ndarray]:
    """Float64 port of frozen base_estimator._diagonal_gaussian_pass.

    Returns only the per-layer alpha vectors (all this gate consumes).
    Deviation (analysis-side only): float64 instead of the estimator's
    float32; the +-6.7 threshold makes the classification insensitive to
    f32-vs-f64 differences and the frozen sources are untouched.
    """
    mu = np.zeros(WIDTH, dtype=np.float64)
    var = np.ones(WIDTH, dtype=np.float64)
    alphas = []
    for weight in weights:
        w64 = weight.astype(np.float64)
        mu_pre = mu @ w64
        var_pre = var @ (w64 * w64)
        sigma = np.sqrt(np.maximum(var_pre, 1e-12))
        alpha = mu_pre / sigma
        phi = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
        cdf = 0.5 * (1.0 + _ERF(alpha / math.sqrt(2.0)))
        mu = mu_pre * cdf + sigma * phi
        second = (var_pre + mu_pre * mu_pre) * cdf + mu_pre * sigma * phi
        var = np.maximum(second - mu * mu, 0.0)
        alphas.append(alpha)
    return alphas


# ------------------------------------------------------ pilot forward pass
def pilot_forward(weights: list[np.ndarray], points: np.ndarray):
    """Full-net f32 forward of the 2048 pilot paths; per-layer pre-acts.

    On these rows the full forward equals v3's pruned/folded pipeline
    exactly: a pruned column is (alpha < -2 AND pilot never fires), so its
    ReLU output is 0 on every pilot row -- identical contribution; and a
    fold/on-composed column has pilot min > 0, so ReLU is the identity on
    every pilot row.  Asserted numerically downstream.
    """
    first = points @ weights[0]
    x = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0,
    )
    pres = [None]  # index by weight layer; layer 0 handled antipodally above
    for layer in range(1, DEPTH):
        pre = x @ weights[layer]
        pres.append(pre)
        x = np.maximum(pre, np.float32(0.0))
    return pres


# --------------------------------------------------------- per-op bills
# Verbatim per-op conventions from t3 capped_fold3.py (v0.10 pricing).
def _mm(m: int, k: int, n: int) -> int:
    if m <= 0 or k <= 0 or n <= 0:
        return 0
    return 2 * m * k * n - m * n


def _sort_bill(m: int) -> int:
    if m < 2:
        return 8
    return 8 * m * max(1, math.ceil(math.log2(m)))


def _refine_bill(size: int, moved: int, rows: int) -> int:
    return (
        (rows - 1) * size + size + size + 8 * moved + size + size
        + 8 * (size - moved)
    )


def _pre31_bill(a28, o30, k30, cols, rows, w):
    if cols <= 0:
        return 0
    return (
        4 * a28 * o30 + 4 * o30 * w + 4 * o30 * cols
        + _mm(a28, o30, cols)
        + _mm(rows, a28, cols)
        + 4 * k30 * w + 4 * k30 * cols
        + _mm(rows, k30, cols)
        + rows * cols
    )


def _pre32_bill(a28, o31, k30, k31, cols, rows, w):
    if cols <= 0:
        return 0
    return (
        2 * (4 * o31 * w + 4 * o31 * cols)
        + 4 * k31 * w + 4 * k31 * cols
        + _mm(a28, o31, cols) + _mm(rows, a28, cols)
        + _mm(k30, o31, cols) + _mm(rows, k30, cols)
        + _mm(rows, k31, cols)
        + 2 * rows * cols
    )


# Verbatim ports of frozen cost_model.py (plain arithmetic, no flopscope).
def direct_cost(m: int, k: int, n: int) -> int:
    if min(m, k, n) <= 0:
        raise ValueError("matrix dimensions must be positive")
    return m * n * (2 * k - 1)


def batched_winograd_core_cost(m: int, k: int, n: int) -> int:
    if min(m, k, n) <= 0 or any(value % 2 for value in (m, k, n)):
        raise ValueError("one Winograd level requires positive even dimensions")
    leaf = 7 * direct_cost(m // 2, k // 2, n // 2)
    stack_fills = 7 * (m // 2) * (k // 2) + 7 * (k // 2) * (n // 2)
    output_adds = 7 * (m // 2) * (n // 2)
    return leaf + stack_fills + output_adds


def owned_winograd_bill(m: int, k: int, n: int) -> int:
    """Total billed FLOPs of RowBlockedBatchedWinograd.multiply(m,k,n).

    Port of cost_model.owned_batched_candidate_bill total (the frozen
    operator's own bill authority); returns 0 for empty shapes.
    """
    if m <= 0 or k <= 0 or n <= 0:
        return 0
    direct_owned = direct_cost(m, k, n) + m * k
    if m % 2 or k % 2:
        return direct_owned
    nc = n - (n % 2)
    if nc == 0:
        return direct_owned
    core = batched_winograd_core_cost(m, k, nc)
    output = n - nc
    output_mm = direct_cost(m, k, output) if output else 0
    total = core + output_mm
    if total >= direct_cost(m, k, n):
        return direct_owned
    tail_copy = m if output else 0
    total += tail_copy
    if total >= direct_owned:
        return direct_owned
    return total


# ------------------------------------------------------------ replay
def replay_net(weights):
    """All realized set sizes + M184 classification for one net."""
    alphas = diagonal_gaussian_pass_alphas(weights)
    points = ROTATED_POINTS_CACHE.pop("points")
    pres = pilot_forward(weights, points)

    pilot_rows = np.concatenate(
        (np.arange(PILOT_DIRS), FOLD_PILOT_DIRS + np.arange(PILOT_DIRS))
    )

    layers = []
    active = np.arange(WIDTH)
    for layer in range(1, DEPTH - 3):
        alpha = alphas[layer]
        pre_pilot = pres[layer][pilot_rows]        # 512-path pilot block
        structural = np.flatnonzero(alpha >= DEAD_ALPHA)
        cold = np.flatnonzero(alpha < DEAD_ALPHA)
        if cold.shape[0] > 0:
            fired = pre_pilot[:, cold].max(axis=0) > 0.0
            rescued = cold[np.flatnonzero(fired)]
        else:
            rescued = cold
        next_active = np.sort(np.concatenate((structural, rescued)))

        # M184 certainty classification (512-path block + analytic margin)
        cand_on = np.flatnonzero(alpha > CERTAIN_ALPHA)
        cand_on_active = np.intersect1d(cand_on, next_active)
        if cand_on_active.shape[0] > 0:
            confirmed = pre_pilot[:, cand_on_active].min(axis=0) > 0.0
            on_set = cand_on_active[np.flatnonzero(confirmed)]
        else:
            on_set = cand_on_active
        cand_dead = np.flatnonzero(alpha < -CERTAIN_ALPHA)
        if cand_dead.shape[0] > 0:
            silent = pre_pilot[:, cand_dead].max(axis=0) <= 0.0
            certain_dead = cand_dead[np.flatnonzero(silent)]
        else:
            certain_dead = cand_dead
        overlap = np.intersect1d(certain_dead, next_active)
        if overlap.shape[0] != 0:
            raise AssertionError(
                f"layer {layer}: certain-dead overlaps v3-active "
                f"({overlap.shape[0]} neurons) -- increment (a) premise broken"
            )
        # Consistency: v3-pruned columns are silent on ALL pilot rows
        pruned = np.setdiff1d(np.arange(WIDTH), next_active)
        if pruned.shape[0] > 0:
            if float(pres[layer][:, pruned].max(initial=-np.inf)) > 0.0:
                # fires on a fold-pilot row outside the 512 block: legal for
                # v3 (its rescue uses only the 512 block) -- not an error,
                # but check the 512 block itself is silent.
                if float(pre_pilot[:, pruned].max(initial=-np.inf)) > 0.0:
                    raise AssertionError(
                        f"layer {layer}: pruned column fires on the 512-path "
                        "pilot block -- replay inconsistent"
                    )

        layers.append({
            "layer": layer,
            "a_prev": int(active.shape[0]),
            "cold": int(cold.shape[0]),
            "rescued": int(rescued.shape[0]),
            "a_next": int(next_active.shape[0]),
            "cand_on": int(cand_on_active.shape[0]),
            "on": int(on_set.shape[0]),
            "kink": int(next_active.shape[0] - on_set.shape[0]),
            "certain_dead_all256": int(certain_dead.shape[0]),
            "certain_dead_in_active": int(overlap.shape[0]),
        })
        active = next_active

    a28 = int(active.shape[0])

    # Fold-layer partitions (v3 fold3 semantics; 2048 fold-pilot rows).
    fold = {"a28": a28}
    for tag, layer in (("30", DEPTH - 3), ("31", DEPTH - 2), ("32", DEPTH - 1)):
        alpha = alphas[layer]
        pre_fold_pilot = pres[layer]               # all 2048 rows
        dead = np.flatnonzero(alpha < DEAD_ALPHA)
        on = np.flatnonzero(alpha > ON_ALPHA_FOLD)
        kink = np.flatnonzero(
            np.logical_and(alpha >= DEAD_ALPHA, alpha <= ON_ALPHA_FOLD)
        )
        fold[f"d{tag}_init"] = int(dead.shape[0])
        fold[f"k{tag}_init"] = int(kink.shape[0])
        fold[f"o{tag}_init"] = int(on.shape[0])
        if dead.shape[0] > 0:
            fired = pre_fold_pilot[:, dead].max(axis=0) > 0.0
            rescued_f = dead[np.flatnonzero(fired)]
            dead = dead[np.flatnonzero(~fired)]
        else:
            rescued_f = dead
        if on.shape[0] > 0:
            crossed = pre_fold_pilot[:, on].min(axis=0) <= 0.0
            demoted = on[np.flatnonzero(crossed)]
            on = on[np.flatnonzero(~crossed)]
        else:
            demoted = on
        fold[f"r{tag}"] = int(rescued_f.shape[0])
        fold[f"dm{tag}"] = int(demoted.shape[0])
        fold[f"k{tag}"] = int(
            fold[f"k{tag}_init"] + rescued_f.shape[0] + demoted.shape[0]
        )
        fold[f"o{tag}"] = int(on.shape[0])
        if tag == "32":
            fold["d32"] = int(dead.shape[0])
    return layers, fold


# ------------------------------------------------------- v3 loop bill
def v3_layer_bill(row) -> int:
    """One v3 pruning-loop layer, op-by-op (fold3 predict + Kerdock
    winograd sample matmul).  Independently written; must equal
    segment_cost(m, m+1)."""
    a_prev, cold, rescued, a_next = (
        row["a_prev"], row["cold"], row["rescued"], row["a_next"]
    )
    total = 4 * W                                   # compares + flatnonzero x2
    if cold > 0:
        total += P2 * a_prev                        # pilot_x concatenate
        total += 4 * a_prev * W + 4 * a_prev * cold  # weight gathers
        total += _mm(P2, a_prev, cold)
        total += (P2 - 1) * cold + cold             # max, > 0
        total += cold + 8 * rescued                 # flatnonzero + gather
        total += 2 * a_next + _sort_bill(a_next)    # concat + sort
    total += 4 * a_prev * W + 4 * a_prev * a_next   # weight gathers
    total += owned_winograd_bill(BIG, a_prev, a_next)
    total += BIG * a_next                           # relu
    return total


# ---------------------------------------------------- M184 segment bill
def segment_cost(rows, m: int, e: int) -> int:
    """Billed cost of loop layers m+1..e with last collapse at layer m.

    rows: replay rows indexed so rows[l-1] is loop layer l (l = 1..28).
    Carriers: the anchor x_m (width a_m) plus one materialized kink block
    per fold step.  Fold steps (layers m+1..e-1) materialize only kink
    columns; the collapse step (layer e) materializes all a_e columns and
    resets to a single carrier.  Length-1 segments reproduce v3 exactly.
    """
    anchor_width = rows[m - 1]["a_next"] if m >= 1 else W
    carriers = [anchor_width]
    prev_on = 0            # on-columns pending from the previous fold step
    total = 0
    for l in range(m + 1, e + 1):
        row = rows[l - 1]
        final = (l == e)
        cold, rescued, a_next = row["cold"], row["rescued"], row["a_next"]
        o_l, k_l, cand = row["on"], row["kink"], row["cand_on"]

        total += 4 * W                              # v3 classification
        if not final:
            total += 2 * W                          # alpha > +6.7 cmp + fnz

        # ---- H precompute (fold matrices to this layer's W columns) ----
        if prev_on == 0:
            # previous step folded nothing: earlier carriers contribute 0;
            # a real implementation drops them.
            carriers = [carriers[-1]]
            total += 4 * carriers[0] * W            # plain row gather
        else:
            total += 4 * prev_on * W                # shared W[on_{l-1}, :] gather
            for c in carriers[:-1]:
                total += _mm(c, prev_on, W)         # P_i @ W[on, :]
            total += 4 * carriers[-1] * W           # last kink block: row gather

        r = len(carriers)
        csum = sum(carriers)

        # ---- pilot (cold rescue always; on-candidates on fold steps) ----
        pilot_cols = cold + (cand if not final else 0)
        if pilot_cols > 0:
            if prev_on == 0:
                # v3's code gathers W[layer][active, :] a second time inside
                # its pilot branch; capped_fold3 bills both.  Match it in the
                # plain-gather state so length-1 segments equal v3 exactly.
                total += 4 * carriers[0] * W
            total += P2 * csum                      # pilot row concatenate
            for c in carriers:
                total += 4 * c * pilot_cols         # H column slice gather
                total += _mm(P2, c, pilot_cols)
            total += (r - 1) * P2 * pilot_cols      # carrier adds
        if cold > 0:
            total += (P2 - 1) * cold + cold         # max, > 0
            total += cold + 8 * rescued             # flatnonzero + gather
            total += 2 * a_next + _sort_bill(a_next)
        if not final and cand > 0:
            total += (P2 - 1) * cand + cand         # min, > 0
            total += cand + 8 * o_l                 # flatnonzero + gather
            total += _sort_bill(o_l) + _sort_bill(k_l) + 2 * W  # index upkeep

        # ---- per-sample materialization ----
        target = a_next if final else k_l
        if target > 0:
            for c in carriers:
                total += 4 * c * target             # H column slice gather
                total += owned_winograd_bill(BIG, c, target)
            total += (r - 1) * BIG * target         # carrier adds
            total += BIG * target                   # relu

        if final:
            carriers = [a_next]
            prev_on = 0
        else:
            for c in carriers:
                total += 4 * c * o_l                # P_i = H_i[:, on_l] slice
            if k_l > 0:
                carriers = carriers + [k_l]
            prev_on = o_l
    return total


def m184_loop_bill(rows):
    """DP over collapse schedules; returns (cost, collapse layers)."""
    n_layers = len(rows)                            # 28
    best = [0] + [None] * n_layers
    back = [None] * (n_layers + 1)
    for e in range(1, n_layers + 1):
        for m in range(0, e):
            if best[m] is None:
                continue
            c = best[m] + segment_cost(rows, m, e)
            if best[e] is None or c < best[e]:
                best[e] = c
                back[e] = m
    schedule = []
    e = n_layers
    while e > 0:
        schedule.append(e)
        e = back[e]
    schedule.reverse()
    return best[n_layers], schedule


# ------------------------------------------------- common (shared) bill
def common_bill(fold) -> dict:
    """Everything outside the pruning loop; identical in both arms."""
    parts = {}
    # Haar rotation + rotation.T @ W0.  QR is billed by flopscope with a
    # price this static model cannot observe; 2*w^3 is a stated rough
    # stand-in (~0.02% of the total -- cannot move the verdict).
    parts["haar_qr_est"] = 2 * W ** 3 + _mm(W, W, W)
    # Analytic diagonal pass (modeled, ~rough smallness): per layer two
    # vec@mat, W*W square, ~40w pointwise chain.
    parts["diag_pass_est"] = DEPTH * (2 * _mm(1, W, W) + W * W + 40 * W)
    # Exact phased-WHT first product: phase multiply n*w, 8 butterfly
    # stages x (copy + add + subtract on n*w/2 each), final scale n*w.
    parts["first_product_wht"] = (
        N_BASE * W + 8 * 3 * (N_BASE * W // 2) + N_BASE * W
    )
    # Antipodal fill: negate + two ReLUs into the owned buffer (no concat).
    parts["antipodal"] = 3 * N_BASE * W
    # sigma0 / exact mean / residual chain.
    parts["first_residuals"] = (
        W * W + (W - 1) * W + 2 * W + 3 + W
        + BIG * W + W + BIG * W + BIG * W + 6 * W
        + 4 * W
    )

    # ---- fold section (verbatim structure from t3 predict_main_bill) ----
    a28 = fold["a28"]
    ft = 0
    ft += FP2 * a28                                 # pilot_x29 concatenate
    # layer30
    ft += 8 * W
    ft += 4 * a28 * W                               # weight30 gather
    k_run = fold["k30_init"]
    if fold["d30_init"] > 0:
        ft += 4 * a28 * fold["d30_init"] + _mm(FP2, a28, fold["d30_init"])
        ft += _refine_bill(fold["d30_init"], fold["r30"], FP2)
        k_run += fold["r30"]
        ft += 2 * k_run
    if fold["o30_init"] > 0:
        ft += 4 * a28 * fold["o30_init"] + _mm(FP2, a28, fold["o30_init"])
        ft += _refine_bill(fold["o30_init"], fold["dm30"], FP2)
        k_run += fold["dm30"]
        ft += 2 * k_run
    k30, o30 = fold["k30"], fold["o30"]
    ft += _sort_bill(k30)
    ft += 4 * a28 * k30 + _mm(BIG, a28, k30) + BIG * k30    # x30_kink
    ft += FP2 * k30
    # layer31
    ft += 8 * W
    k_run = fold["k31_init"]
    if fold["d31_init"] > 0:
        ft += _pre31_bill(a28, o30, k30, fold["d31_init"], FP2, W)
        ft += _refine_bill(fold["d31_init"], fold["r31"], FP2)
        k_run += fold["r31"]
        ft += 2 * k_run
    if fold["o31_init"] > 0:
        ft += _pre31_bill(a28, o30, k30, fold["o31_init"], FP2, W)
        ft += _refine_bill(fold["o31_init"], fold["dm31"], FP2)
        k_run += fold["dm31"]
        ft += 2 * k_run
    k31, o31 = fold["k31"], fold["o31"]
    ft += _sort_bill(k31)
    ft += _pre31_bill(a28, o30, k30, k31, BIG, W) + BIG * k31   # x31_kink
    ft += FP2 * k31
    # layer32
    ft += 8 * W
    ft += (4 * a28 * o30 + 4 * o30 * W + 4 * o30 * o31 + _mm(a28, o30, o31))
    ft += 4 * k30 * W + 4 * k30 * o31
    k_run = fold["k32_init"]
    if fold["d32_init"] > 0:
        ft += _pre32_bill(a28, o31, k30, k31, fold["d32_init"], FP2, W)
        ft += _refine_bill(fold["d32_init"], fold["r32"], FP2)
        k_run += fold["r32"]
        ft += 2 * k_run
    if fold["o32_init"] > 0:
        ft += _pre32_bill(a28, o31, k30, k31, fold["o32_init"], FP2, W)
        ft += _refine_bill(fold["o32_init"], fold["dm32"], FP2)
        k_run += fold["dm32"]
        ft += 2 * k_run
    k32, o32, d32 = fold["k32"], fold["o32"], fold["d32"]
    ft += _sort_bill(k32)
    if k32 > 0:
        ft += _pre32_bill(a28, o31, k30, k31, k32, BIG, W)
        ft += BIG * k32 + BIG * k32                 # relu + mean
    if o32 > 0:
        ft += BIG * a28 + BIG * k30 + BIG * k31     # three means
        ft += (4 * o31 * W + 4 * o31 * o32 + _mm(a28, o31, o32)
               + _mm(1, a28, o32))
        ft += (4 * o31 * W + 4 * o31 * o32 + _mm(k30, o31, o32)
               + _mm(1, k30, o32))
        ft += 4 * k31 * W + 4 * k31 * o32 + _mm(1, k31, o32)
        ft += 2 * o32
    if d32 > 0:
        ft += 4 * d32
    ft += 2 * W + W + _sort_bill(W) + 4 * W         # _assemble_vector
    parts["fold_section"] = ft

    # tangent recursion (verbatim predict_main_bill)
    per_layer = 2 * _mm(1, W, W) + W * W + 16 * W + W + 16 * W + 3 + W + 12 * W
    parts["tangent"] = (DEPTH - 1) * per_layer + 2 * W + DEPTH * W
    parts["total"] = sum(parts.values())
    return parts


# ---------------------------------------------------------------- main
ROTATED_POINTS_CACHE: dict = {}


def run_net(net_seed: int, base_points: np.ndarray) -> dict:
    weights = he_mlp_weights(net_seed)
    rotation = haar_rotation(net_seed)      # v3 predict(): seed = mlp.seed
    ROTATED_POINTS_CACHE["points"] = (base_points @ rotation.T).astype(
        np.float32
    )
    rows, fold = replay_net(weights)

    # cross-check: length-1 segments == independently written v3 bill
    for l in range(1, len(rows) + 1):
        a = v3_layer_bill(rows[l - 1])
        b = segment_cost(rows, l - 1, l)
        if a != b:
            raise AssertionError(
                f"net {net_seed} layer {l}: v3 bill {a} != len-1 segment {b}"
            )

    v3_loop = sum(v3_layer_bill(r) for r in rows)
    m184_loop, schedule = m184_loop_bill(rows)
    common = common_bill(fold)
    c_v3 = common["total"] + v3_loop
    c_m184 = common["total"] + m184_loop
    reduction = 1.0 - c_m184 / c_v3

    per_layer = []
    for r in rows:
        per_layer.append({
            **r,
            "on_frac_of_width": r["on"] / W,
            "on_frac_of_active": (r["on"] / r["a_next"]) if r["a_next"] else 0.0,
            "certain_dead_frac_of_width": r["certain_dead_all256"] / W,
            "v3_pruned": W - r["a_next"],
            "v3_layer_bill": v3_layer_bill(r),
        })
    return {
        "net_seed": net_seed,
        "per_layer": per_layer,
        "fold_dims": fold,
        "bills": {
            "common_parts": common,
            "v3_loop": int(v3_loop),
            "m184_loop": int(m184_loop),
            "v3_total": int(c_v3),
            "m184_total": int(c_m184),
            "loop_reduction": 1.0 - m184_loop / v3_loop,
            "total_reduction": reduction,
        },
        "m184_collapse_schedule": schedule,
        "increment_accounting": {
            "dead_column_increment_neurons": 0,
            "dead_note": (
                "certain-dead /\\ v3-active empty on every layer (asserted); "
                "v3's alpha<-2 + pilot rescue already prunes a strict "
                "superset of certain-dead columns"
            ),
        },
    }


def main() -> None:
    t0 = time.perf_counter()
    mean_chi_check = math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((WIDTH + 1.0) / 2.0)
        - math.lgamma(WIDTH / 2.0)
    )
    if abs(mean_chi_check - MEAN_CHI_256) > 1e-9:
        raise RuntimeError("mean chi constant does not match the formula")

    tail = 0.5 * math.erfc(CERTAIN_ALPHA / math.sqrt(2.0))
    per_neuron_misclass = BIG * tail
    if per_neuron_misclass >= 1e-6:
        raise RuntimeError(
            f"threshold {CERTAIN_ALPHA} misses the predeclared 1e-6 bound: "
            f"{per_neuron_misclass:.3e}"
        )

    base_points = load_kerdock_pilot_frames()
    nets = []
    for seed in G0_NET_SEEDS:
        net = run_net(seed, base_points)
        nets.append(net)
        b = net["bills"]
        print(
            f"net {seed}: v3 {b['v3_total']/1e9:.2f}G -> "
            f"m184 {b['m184_total']/1e9:.2f}G  "
            f"reduction {100*b['total_reduction']:.2f}% "
            f"(loop-only {100*b['loop_reduction']:.2f}%)  "
            f"collapse schedule {net['m184_collapse_schedule']}",
            flush=True,
        )
        print("  layer  a_prev a_next  on  kink  cand  cdead  on/active")
        for r in net["per_layer"]:
            print(
                f"   {r['layer']:>4}   {r['a_prev']:>5} {r['a_next']:>5} "
                f"{r['on']:>4} {r['kink']:>4} {r['cand_on']:>5} "
                f"{r['certain_dead_all256']:>5}  {r['on_frac_of_active']:.3f}"
            )

    reductions = [n["bills"]["total_reduction"] for n in nets]
    geomean = math.exp(sum(math.log(max(1e-12, 1.0 - r)) for r in reductions)
                       / len(reductions))
    agg_reduction = 1.0 - geomean
    min_reduction = min(reductions)

    killed = (agg_reduction < KILL_REDUCTION) or (min_reduction < KILL_REDUCTION)
    promoted = (not killed) and (agg_reduction >= PROMOTE_REDUCTION) and (
        min_reduction >= PROMOTE_REDUCTION
    )
    if killed:
        verdict = (
            f"KILL: projected billed reduction "
            f"{[f'{100*r:.2f}%' for r in reductions]} (aggregate "
            f"{100*agg_reduction:.2f}%, min {100*min_reduction:.2f}%) "
            f"< {100*KILL_REDUCTION:.0f}% gate"
        )
    elif promoted:
        verdict = (
            f"PROMOTE to G1: reductions "
            f"{[f'{100*r:.2f}%' for r in reductions]} (aggregate "
            f"{100*agg_reduction:.2f}%) >= {100*PROMOTE_REDUCTION:.0f}%"
        )
    else:
        verdict = (
            f"SURVIVES-KILL-NOT-PROMOTABLE: reductions "
            f"{[f'{100*r:.2f}%' for r in reductions]} (aggregate "
            f"{100*agg_reduction:.2f}%, min {100*min_reduction:.2f}%) in "
            f"[{100*KILL_REDUCTION:.0f}%, {100*PROMOTE_REDUCTION:.0f}%) band"
        )

    results = {
        "date": "2026-08-08",
        "predeclaration": "M184_PREDECLARATION.md",
        "gate": "G0",
        "config": {
            "width": WIDTH, "depth": DEPTH, "n_base": N_BASE,
            "n_total_antipodal": BIG,
            "net_seeds": list(G0_NET_SEEDS),
            "pilot_paths": P2,
            "fold_pilot_paths_for_v3_replay": FP2,
            "certain_alpha": CERTAIN_ALPHA,
            "per_neuron_misclass_bound": per_neuron_misclass,
            "misclass_calc": (
                "union bound under the diagonal-Gaussian surrogate: "
                f"64512 * Phi(-{CERTAIN_ALPHA}) = 64512 * {tail:.3e} = "
                f"{per_neuron_misclass:.3e} < 1e-6; pilot min/max over the "
                "512 paths is the second, distribution-free signal"
            ),
            "kill_reduction": KILL_REDUCTION,
            "promote_reduction": PROMOTE_REDUCTION,
            "billing": (
                "v0.10 pricing per t3 capped_fold3.py conventions: matmul "
                "2mkn-mn, pointwise 1/elem, gather 4/output elem, sort "
                "8n ceil(log2 n), int concat 2/elem; loop sample matmuls "
                "billed by the frozen owned_batched_candidate_bill "
                "(RowBlockedBatchedWinograd); first product billed as the "
                "exact phased-WHT butterfly (14 n w)"
            ),
        },
        "firewall": (
            "synthetic He nets only; only kerdock_phases.npz loaded "
            "(read-only, the estimator's own shipped sampling asset); no "
            "dataset/truth/scorer/submission; writes confined to the m184 "
            "experiment directory; plain numpy static count (sanctioned)"
        ),
        "nets": nets,
        "aggregate": {
            "per_net_reduction": reductions,
            "geomean_reduction": agg_reduction,
            "min_reduction": min_reduction,
        },
        "verdict": verdict,
        "wall_s": round(time.perf_counter() - t0, 1),
    }
    out_path = HERE / "m184_g0_results.json"
    out_path.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"\nVERDICT: {verdict}")
    print(f"results written to {out_path}")


if __name__ == "__main__":
    main()
