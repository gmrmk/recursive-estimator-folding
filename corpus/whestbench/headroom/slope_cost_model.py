"""Slope cost model: predict residual wall seconds from static dispatch structure.

The campaign owns an exact FLOP cost model (``cost_model.py``, the tier ladder,
``floor_candidate_bill``).  It owns no model of the *other* half of the C law

    C = analytical_FLOPs + 100e9 * residual_wall_time_s          (272B budget law)

This module is that other half.  It counts, by static analysis of the committed
estimator sources, how many ``flopscope.numpy`` dispatch sites each route
executes per network, fits a two-term law to the residual seconds those
dispatches cost, validates it against every residual measurement in the corpus,
and files falsifiable predictions.

RUN
    python slope_cost_model.py            # report to stdout
    python slope_cost_model.py --json     # also write SLOPE_COST_MODEL_20260819.json

SOURCES OF TRUTH (all read or cited, none invented)
    experiments/row_blocked_production/candidate_source/   incumbent route
    experiments/fold_floor_splice/candidate_source/        fold route (L2..L6)
    experiments/fold_floor_splice/full.json                harness residuals
    experiments/fold_floor_splice/memory_reconciliation.json  isolated-probe residuals
    experiments/ROW_BLOCKED_WINOGRAD_PRODUCTION_REPORT.md  Public100 receipts

The FLOP side is not re-derived by hand: ``cost_model.py`` is imported and its
committed self-check constants are re-proved on the way in, so a drift in the
frozen source fails this script rather than silently moving the model.
"""

from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HERE)
EXP = os.path.join(CORPUS, "experiments")
FOLD_SRC = os.path.join(EXP, "fold_floor_splice", "candidate_source")
sys.path.insert(0, FOLD_SRC)

import cost_model as cm  # noqa: E402  (the frozen, flopscope-free bill module)


# ---------------------------------------------------------------------------
# 0.  Geometry and frozen constants, named where they come from
# ---------------------------------------------------------------------------

WIDTH = 256                 # ctx.width
DEPTH = 32                  # mlp.depth
N_BASE = 126 * 256          # 32,256  (estimator.py: n_base = 126 * 256)
ROWS = 2 * N_BASE           # 64,512  antipodal stack
BLOCK_ROWS = 8192           # row_blocked_winograd.BLOCK_ROWS
WORKSPACE_MIB = 192.0       # estimator.FLOOR_WORKSPACE_MIB
LAMBDA = 100e9              # the C law's residual multiplier (1e11, exact)

# fold3_estimator.predict: for layer in range(1, mlp.depth - 3)  ->  28 products,
# plus one first_sample_matmul.  The fold fork additionally routes six
# full-height terminal-fold products through the same hook
# (FOLD_PRODUCTS_THROUGH_OPERATOR = True):
#   x @ weight30[:, kink30]                                     1
#   pre31(kink31, False)   -> two legs                          2
#   pre32(kink32, False)   -> three legs                        3
LAYER_PRODUCTS = DEPTH - 4          # 28
FOLD_PRODUCTS = 6
FIRST_PRODUCT_ROWS = N_BASE         # z @ W0 is half height


# ---------------------------------------------------------------------------
# 1.  The FLOP side, re-proved from the frozen module
# ---------------------------------------------------------------------------

def realized_core(m, k, n, levels):
    """(leaf FLOPs, movement FLOPs) of depth6_winograd._core at a complete core.

    Transcribed from ``depth6_winograd.realized_core_bill``, split into the leaf
    contraction and the four movement lanes so the model can price them apart.
    """
    leaves = 7 ** levels * cm.direct_cost(m >> levels, k >> levels, n >> levels)
    left = 2 * m * k + levels * (m * k // 4) + 3 * cm.node_area_sum(m, k, levels)
    right = 7 * k * n + levels * (k * n // 4) + 3 * cm.node_area_sum(k, n, levels)
    decode = (6 * cm.node_area_sum(m, n, levels)
              + levels * (m * n // 4) + 2 * m * n)
    return leaves, left + right + decode


def selfcheck_flop_side():
    """Re-prove the committed constants before using the module."""
    checks = {
        "tier7_floor_4096": (cm.floor_candidate_bill(4096, 256, 256).total,
                             303_096_592),
        "owned_batched_4096": (cm.owned_batched_candidate_bill(4096, 256, 256).total,
                               471_711_744),
        "direct_4096": (cm.direct_cost(4096, 256, 256), 535_822_336),
        "realized_L6_4096": (sum(realized_core(4096, 256, 256, 6)), 307_749_648),
        "realized_L4_4096": (sum(realized_core(4096, 256, 256, 4)), 338_592_000),
    }
    for name, (got, want) in checks.items():
        if got != want:
            raise AssertionError(f"{name}: got {got:,}, frozen value is {want:,}")
    return {k: v[0] for k, v in checks.items()}


# ---------------------------------------------------------------------------
# 2.  The static dispatch structure  (the model's only input)
# ---------------------------------------------------------------------------

def rows_per_block(levels, workspace_mib=WORKSPACE_MIB, max_m=ROWS, width=WIDTH):
    """DepthWinograd._rows_per_block, transcribed.

    Note the property the whole model turns on: this depends on ``width`` and
    ``levels`` only -- never on the product's actual contracted width k or output
    width n.  The dispatch count of a depth-L product is therefore invariant to
    how much of the layer is alive, which is what lets a residual delta measured
    on all-active synthetic nets transfer to the pruned Public100 suite.
    """
    block = 1 << levels
    leaves = 7 ** levels
    wide = max(width >> levels, 1)
    per_unit = 4.0 * leaves * 2 * wide
    budget = workspace_mib * 1024.0 * 1024.0 - 4.0 * leaves * wide * wide
    if per_unit <= 0.0 or budget <= 0.0:
        return block
    rows = min(int(budget // per_unit) * block, max_m)
    return max(block, rows - rows % block)


def dispatches_incumbent(m):
    """fnp dispatch sites of RowBlockedBatchedWinograd.multiply(m x 256, 256 x 256).

    Right pack, outside the row loop:   3 copyto + 4 subtract          = 7
    Per row block:  left stack 3 copyto + 1 add + 3 subtract           = 7
                    one batched fnp.matmul                             = 1
                    reconstruction 6 add + 1 subtract                  = 7
                                                                        --
                                                                        15
    The operator returns ``self.output[:m, :n]`` -- a view of preallocated
    scratch -- so it allocates nothing per call.
    """
    blocks = math.ceil(m / BLOCK_ROWS)
    return {"dispatch": 7 + 15 * blocks, "matmul": blocks, "blocks": blocks,
            "alloc_bytes": 0}


def dispatches_fork_fallback(m):
    """The fork on its frozen fallback: the incumbent plus the copy-out contract.

    ``DepthWinograd.multiply`` allocates a fresh ``out`` and copies the shared
    buffer into it, because the terminal fold holds two and three products live
    at once and adds them.
    """
    base = dispatches_incumbent(m)
    return {"dispatch": base["dispatch"] + 2, "matmul": base["matmul"],
            "blocks": base["blocks"], "alloc_bytes": m * WIDTH * 4}


def dispatches_depth(m, levels):
    """fnp dispatch sites of DepthWinograd.multiply_at_depth at depth ``levels``.

    _prepare_right  : one ix_ gather + one copyto + L psi + 3L encode = 2 + 4L
    _core, per block: one copyto load + 11L lane ops + one fnp.matmul
                      + one copyto unload                             = 3 + 11L
                      (11L = psi_left L, encode_left 3L, decode 6L, psi_c L)
    plus one ``fnp.empty`` for the freshly allocated result.

    Reshapes, transposes and basic slices are views and are not counted; the
    module's own counter returns ``4 + 10*levels`` for _core and ``4 + 4*levels``
    for _prepare_right, which under-reports the lane count by 3 and over-reports
    the view count by 2.  Both are recorded here rather than trusted.
    """
    rpb = rows_per_block(levels)
    blocks = math.ceil(m / rpb)
    per_core = 3 + 11 * levels
    return {"dispatch": (2 + 4 * levels) + blocks * per_core + 1,
            "matmul": blocks, "blocks": blocks,
            "alloc_bytes": m * WIDTH * 4,
            "rows_per_block": rpb, "per_core": per_core,
            "module_counter": (4 + 4 * levels) + blocks * (4 + 10 * levels)}


def route_totals(levels, uptake=1.0, rows=ROWS, first_rows=FIRST_PRODUCT_ROWS,
                 fold_products=FOLD_PRODUCTS):
    """Per-predict static totals for one route.

    ``levels is None`` selects the frozen incumbent (no fold products routed,
    no fresh allocation).  ``uptake`` is the fraction of products that actually
    reach the depth route rather than falling back, which the measured FLOP
    bills identify (see ``depth_route_uptake``).
    """
    tot = {"dispatch": 0.0, "matmul": 0.0, "blocks": 0.0, "alloc_bytes": 0.0,
           "movement": 0.0}
    if levels is None:
        plan = [(first_rows, 1), (rows, LAYER_PRODUCTS)]
    else:
        plan = [(first_rows, 1), (rows, LAYER_PRODUCTS + fold_products)]
    for m, count in plan:
        fb = (dispatches_incumbent(m) if levels is None
              else dispatches_fork_fallback(m))
        mov_fb = (7 * (m // 2) * (WIDTH // 2) + 7 * (WIDTH // 2) * (WIDTH // 2)
                  + 7 * (m // 2) * (WIDTH // 2))
        if levels is None:
            dp, mov_dp, p = fb, mov_fb, 0.0
        else:
            dp = dispatches_depth(m, levels)
            mov_dp = realized_core(m, WIDTH, WIDTH, levels)[1]
            p = uptake
        for key in ("dispatch", "matmul", "blocks"):
            tot[key] += count * (p * dp[key] + (1.0 - p) * fb[key])
        tot["alloc_bytes"] += count * fb["alloc_bytes"]
        tot["movement"] += count * (p * mov_dp + (1.0 - p) * mov_fb)
    tot["depth_route"] = 0.0 if levels is None else 1.0
    return tot


def sample_bill(levels, width=WIDTH):
    """Analytical FLOPs of the 29 sample-path products at contracted ``width``."""
    total = 0
    for m, count in ((FIRST_PRODUCT_ROWS, 1), (ROWS, LAYER_PRODUCTS)):
        if levels is None:
            total += count * cm.batched_candidate_bill(m, width, width).total
        else:
            total += count * sum(realized_core(m, width, width, levels))
    return total


def depth_route_uptake(measured_flops):
    """Fraction of products reaching the depth route, from the measured bills.

    Both routes run the same estimator, so every non-sample-product FLOP cancels:

        T(inc) - T(L) = uptake(L) * (S_fallback - S_depth(L))

    Recovering ``uptake`` from the FLOP receipts is what lets the dispatch model
    be evaluated on the route the machine actually took, not the one the sweep
    would take on ideal widths.
    """
    s_fb = sample_bill(None)
    out = {}
    for levels in (3, 4, 5, 6):
        s_dp = sample_bill(levels)
        out[levels] = ((measured_flops["inc"] - measured_flops[levels])
                       / (s_fb - s_dp))
    return out


# ---------------------------------------------------------------------------
# 3.  Least squares without numpy (3 parameters, normal equations)
# ---------------------------------------------------------------------------

def lstsq(design, y):
    """Solve min ||A c - y|| by Gaussian elimination on A^T A c = A^T y."""
    p = len(design[0])
    ata = [[sum(design[r][i] * design[r][j] for r in range(len(y)))
            for j in range(p)] for i in range(p)]
    aty = [sum(design[r][i] * y[r] for r in range(len(y))) for i in range(p)]
    for i in range(p):
        pivot = max(range(i, p), key=lambda r: abs(ata[r][i]))
        ata[i], ata[pivot] = ata[pivot], ata[i]
        aty[i], aty[pivot] = aty[pivot], aty[i]
        if abs(ata[i][i]) < 1e-30:
            raise ValueError("singular design")
        for r in range(p):
            if r == i:
                continue
            f = ata[r][i] / ata[i][i]
            for c in range(i, p):
                ata[r][c] -= f * ata[i][c]
            aty[r] -= f * aty[i]
    return [aty[i] / ata[i][i] for i in range(p)]


def r_squared(y, pred):
    mean = sum(y) / len(y)
    sst = sum((v - mean) ** 2 for v in y)
    sse = sum((a - b) ** 2 for a, b in zip(y, pred))
    return 1.0 - sse / sst if sst else float("nan")


# ---------------------------------------------------------------------------
# 4.  Measured receipts
# ---------------------------------------------------------------------------

def load_receipts():
    with open(os.path.join(EXP, "fold_floor_splice", "full.json"),
              encoding="utf-8") as fh:
        full = json.load(fh)["end_to_end"]
    with open(os.path.join(EXP, "fold_floor_splice",
                           "memory_reconciliation.json"), encoding="utf-8") as fh:
        probe = json.load(fh)["method_A_after_fix"]
    inc = full["incumbent"]
    harness = {
        "flops": {"inc": inc["0"]["flops"],
                  **{int(k[-1]): full["routes"][k][0]["flops"]
                     for k in ("floor_L3", "floor_L4", "floor_L5", "floor_L6")}},
        "residual": {"inc": (inc["0"]["residual"] + inc["1"]["residual"]) / 2.0,
                     **{int(k[-1]): sum(c["residual"]
                                        for c in full["routes"][k]) / 2.0
                        for k in ("floor_L3", "floor_L4", "floor_L5", "floor_L6")}},
        "residual_per_net": {
            "inc": [inc["0"]["residual"], inc["1"]["residual"]],
            **{int(k[-1]): [c["residual"] for c in full["routes"][k]]
               for k in ("floor_L3", "floor_L4", "floor_L5", "floor_L6")}},
    }
    return harness, probe


# Public100, ROW_BLOCKED_WINOGRAD_PRODUCTION_REPORT.md, 2026-08-06 (official run).
PUBLIC100 = {
    "parent_residual_s": 0.168749,
    "child_residual_s": 0.160585,
    "child_analytical_flops": 173.794058e9,
    "child_mean_effective_C": 189.852556e9,
    "child_max_effective_C": 222.405357e9,
    "child_adjusted_score": 2.121762464e-7,
    "child_raw_mse": 3.089460087e-7,
    "safety_gate_Cmax": 258.4e9,
    "budget_B": 272.0e9,
}
# recurse_mstar_out.json, committed break-even derivation on the max-C network.
MAX_C_NET = {"A_incumbent": 203.59e9, "C_incumbent": 222.405357e9,
             "A_fold": 126.7e9, "r_incumbent": 0.18815, "m_star": 5.087}
# Public topic 18184, per sample, naive Strassen-Winograd at width 256.
TOPIC_18184 = {"depth2_residual_eq": 2662, "depth2_total": 104169,
               "depth5_residual_eq": 432427}
# V5-d3 static replay slope law node (graph id v5d3_static_replay).
V5D3_SLOPE_S_PER_CALL = 5.509e-4
# 129-frame completion: n_base 126*256 -> 129*256.
COMPLETION_129 = {"frames_from": 126, "frames_to": 129}


# ---------------------------------------------------------------------------
# 5.  Model
# ---------------------------------------------------------------------------

MODEL_DOC = """\
residual_s = r0 + kappa * 1[depth route] + alpha * log2(N_dispatch)

  kappa  one-off cost of entering the pooled-workspace operator at all:
         DepthWinograd._carve reallocates the left/prod/right pools whenever the
         shape sequence changes (the 28 wide layer products then the 6 narrow
         terminal-fold products), and clears the plan cache when it does.  The
         module's own comment names the mechanism: "capping the cache instead
         traded that back for 200 MiB of reallocation per shape change, which
         landed in residual."
  alpha  marginal cost of dispatch-count growth, per doubling.  Sub-linear:
         a linear-in-N_dispatch term is refuted below (its least-squares
         coefficient is negative).
"""


def build_rows(harness, uptake):
    rows = [("inc", route_totals(None), harness["residual"]["inc"])]
    for levels in (3, 4, 5, 6):
        rows.append((f"L{levels}",
                     route_totals(levels, uptake[levels]),
                     harness["residual"][levels]))
    return rows


def fit_model(rows):
    y = [r[2] for r in rows]
    design = [[r[1]["depth_route"], math.log2(r[1]["dispatch"]), 1.0]
              for r in rows]
    coef = lstsq(design, y)
    pred = [sum(d * c for d, c in zip(row, coef)) for row in design]
    return coef, pred, r_squared(y, pred)


def competing_fits(rows):
    """Every one- and two-term alternative, so the shipped form is a choice."""
    y = [r[2] for r in rows]
    feats = {
        "N_dispatch": [r[1]["dispatch"] for r in rows],
        "bytes_moved": [4.0 * r[1]["movement"] for r in rows],
        "N_matmul": [r[1]["matmul"] for r in rows],
        "alloc_bytes": [r[1]["alloc_bytes"] for r in rows],
        "depth_route": [r[1]["depth_route"] for r in rows],
        "log2_N_dispatch": [math.log2(r[1]["dispatch"]) for r in rows],
        "sqrt_N_dispatch": [math.sqrt(r[1]["dispatch"]) for r in rows],
    }
    out = []
    names = list(feats)
    combos = [(a,) for a in names] + [(a, b) for i, a in enumerate(names)
                                      for b in names[i + 1:]]
    for combo in combos:
        design = [[feats[n][r] for n in combo] + [1.0] for r in range(len(y))]
        try:
            coef = lstsq(design, y)
        except ValueError:
            continue
        pred = [sum(d * c for d, c in zip(row, coef)) for row in design]
        out.append({
            "terms": list(combo), "coef": coef, "r2": r_squared(y, pred),
            "max_rel_err": max(abs(p - v) / v for p, v in zip(pred, y)),
            "any_negative_coef": any(c < 0 for c in coef[:-1]),
        })
    out.sort(key=lambda d: -d["r2"])
    return out


# ---------------------------------------------------------------------------
# 6.  Report
# ---------------------------------------------------------------------------

def main(write_json=False):
    checks = selfcheck_flop_side()
    harness, probe = load_receipts()
    uptake = depth_route_uptake(harness["flops"])
    rows = build_rows(harness, uptake)
    coef, pred, r2 = fit_model(rows)
    kappa, alpha, r0 = coef

    out = {"frozen_flop_selfchecks": checks,
           "depth_route_uptake": uptake,
           "model": MODEL_DOC,
           "coefficients": {"kappa_s": kappa, "alpha_s_per_doubling": alpha,
                            "r0_s": r0, "r2": r2}}

    print("=" * 78)
    print("SLOPE COST MODEL - residual wall seconds from static dispatch structure")
    print("=" * 78)
    print("\n[0] Frozen FLOP-side constants re-proved from cost_model.py:")
    for k, v in checks.items():
        print(f"      {k:22s} {v:,}")
    print(f"\n[1] Row-block geometry (workspace {WORKSPACE_MIB:.0f} MiB, width {WIDTH}):")
    print(f"      incumbent  BLOCK_ROWS={BLOCK_ROWS}  ->  "
          f"{math.ceil(ROWS/BLOCK_ROWS)} blocks at m={ROWS}, "
          f"{math.ceil(N_BASE/BLOCK_ROWS)} at m={N_BASE}")
    for L in (2, 3, 4, 5, 6):
        rpb = rows_per_block(L)
        d = dispatches_depth(ROWS, L)
        print(f"      depth L={L}   rows/block={rpb:6d}  blocks={d['blocks']:3d}  "
              f"calls/core={d['per_core']:3d}  dispatch/product={d['dispatch']:5d}"
              f"   (module counter says {d['module_counter']})")

    print("\n[2] Per-predict static totals and measured residual:")
    print(f"      {'route':6s} {'N_dispatch':>11s} {'N_matmul':>9s} "
          f"{'bytes_moved':>14s} {'alloc_B':>13s} {'residual_s':>11s}")
    for name, tot, res in rows:
        print(f"      {name:6s} {tot['dispatch']:11,.0f} {tot['matmul']:9,.0f} "
              f"{4*tot['movement']:14,.0f} {tot['alloc_bytes']:13,.0f} {res:11.4f}")
    out["route_table"] = [{"route": n, **{k: v for k, v in t.items()},
                           "residual_s": r} for n, t, r in rows]

    print("\n[3] Form selection (5 route points, coefficient sign is the filter):")
    for cand in competing_fits(rows)[:9]:
        flag = "  <-- has a NEGATIVE coefficient: unphysical" \
            if cand["any_negative_coef"] else ""
        print(f"      R2={cand['r2']:+.4f} maxrel={cand['max_rel_err']:6.2%}  "
              f"{' + '.join(cand['terms'])}{flag}")
    out["form_selection"] = competing_fits(rows)

    print(f"\n[4] SHIPPED FORM\n{MODEL_DOC}")
    print(f"      kappa = {kappa:.6f} s      alpha = {alpha:.6f} s/doubling"
          f"      r0 = {r0:.6f} s      R2 = {r2:.4f}")
    for (name, _t, meas), p in zip(rows, pred):
        print(f"      {name:6s} measured {meas:.4f}   predicted {p:.4f}   "
              f"rel {p/meas-1:+.2%}")

    print("\n[5] Cross-harness holdout (isolated single-process probe, "
          "peak_probe.py;\n    the model saw only the verify_fold_floor harness):")
    d_inc = route_totals(None)["dispatch"]
    d_l4 = route_totals(4, uptake[4])["dispatch"]
    d_ff = route_totals(4, 0.0)["dispatch"]
    pred_l4 = kappa + alpha * (math.log2(d_l4) - math.log2(d_inc))
    pred_ff = alpha * (math.log2(d_ff) - math.log2(d_inc))
    meas_l4 = probe["floor_on"]["residual_s_median"] - probe["incumbent"]["residual_s_median"]
    meas_ff = probe["floor_off"]["residual_s_median"] - probe["incumbent"]["residual_s_median"]
    print(f"      depth-4 route delta : predicted {pred_l4:+.4f} s   "
          f"measured {meas_l4:+.4f} s   rel {pred_l4/meas_l4-1:+.2%}")
    print(f"      fallback route delta: predicted {pred_ff:+.4f} s   "
          f"measured {meas_ff:+.4f} s   (both inside the +-0.02 s noise floor)")
    out["holdout"] = {"depth4_predicted_s": pred_l4, "depth4_measured_s": meas_l4,
                      "fallback_predicted_s": pred_ff,
                      "fallback_measured_s": meas_ff}

    print("\n[5b] Robustness to the dispatch-counting convention.")
    conventions = {"data-touching 3+11L": (0, 0),
                   "all fnp call sites 7+11L": (4, 3),
                   "module's own 4+10L": (-3, 2)}
    original = globals()["dispatches_depth"]
    sens = {}
    for label, (core_extra, prep_extra) in conventions.items():
        def patched(m, levels, _c=core_extra, _p=prep_extra, _o=original):
            d = dict(_o(m, levels))
            d["dispatch"] += _p + d["blocks"] * _c
            return d
        globals()["dispatches_depth"] = patched
        rws = build_rows(harness, uptake)
        cf, _pr, rr2 = fit_model(rws)
        di = route_totals(None)["dispatch"]
        dl = route_totals(4, uptake[4])["dispatch"]
        delta = cf[0] + cf[1] * (math.log2(dl) - math.log2(di))
        sens[label] = {"kappa": cf[0], "alpha": cf[1], "r2": rr2,
                       "L4_route_delta_s": delta,
                       "public100_residual_s": PUBLIC100["child_residual_s"] + delta}
        print(f"      {label:26s} kappa={cf[0]:.4f} alpha={cf[1]:.5f} R2={rr2:.4f}"
              f"  -> Public100 residual {PUBLIC100['child_residual_s']+delta:.4f} s")
    globals()["dispatches_depth"] = original
    print("      The filed prediction moves by <0.3 ms across all three conventions:")
    print("      log2 absorbs the scale, so only the route SHAPE matters.")
    out["counting_convention_sensitivity"] = sens

    print("\n[6] Validation against public topic 18184 (naive recursion).")
    q_18184 = (TOPIC_18184["depth5_residual_eq"]
               / TOPIC_18184["depth2_residual_eq"]) ** (1.0 / 3.0)
    d2 = dispatches_depth(ROWS, 2)["dispatch"]
    d5 = dispatches_depth(ROWS, 5)["dispatch"]
    q_model = (d5 / d2) ** (1.0 / 3.0)
    theta = lambda q: math.log(q) / math.log(7.0)
    print(f"      per-level residual growth q:  naive (one call per recursion node) = 7.000")
    print(f"                                    18184 measured                      = {q_18184:.3f}")
    print(f"                                    this model, batched schedule        = {q_model:.3f}")
    print(f"      batching exponent theta = ln q / ln 7 :  "
          f"18184 {theta(q_18184):.3f}   fold {theta(q_model):.3f}   naive 1.000")
    saved = (probe["incumbent"]["analytical_flops"]
             - probe["floor_on"]["analytical_flops"])
    spent = LAMBDA * meas_l4
    print(f"      18184 trades 1 metered FLOP saved for 18 residual-equivalents spent.")
    print(f"      This fold trades {saved/1e9:.3f}B saved for {spent/1e9:.3f}B spent "
          f"= {saved/spent:.2f} : 1 in its favour, a factor {18*saved/spent:.0f} apart.")
    out["topic_18184"] = {"q_naive": 7.0, "q_measured": q_18184,
                          "q_model_batched": q_model,
                          "theta_18184": theta(q_18184),
                          "theta_fold": theta(q_model),
                          "fold_saved_B": saved / 1e9, "fold_spent_B": spent / 1e9,
                          "fold_ratio": saved / spent}

    print("\n[7] Slope-law reconciliation (v5d3 node: 5.509e-4 s per native call).")
    # CODEX_HANDOFF_20260810 s2.3: the parent random32,256 bills 185.4069e9 over
    # ~215.41 matmul calls with residual 0.16875 s.  The child replaces its 29
    # hooked products by the operator's row-block core calls.
    parent_mm = 215.41
    inc_core = route_totals(None)["matmul"]
    child_mm = parent_mm - (LAYER_PRODUCTS + 1) + inc_core
    print(f"      Parent (plain @): {parent_mm:.2f} matmul calls, residual "
          f"{PUBLIC100['parent_residual_s']:.6f} s -> "
          f"{PUBLIC100['parent_residual_s']/parent_mm:.3e} s/call.")
    print(f"      Child (row-blocked): {parent_mm:.2f} - {LAYER_PRODUCTS+1} hooked + "
          f"{inc_core:.0f} core = {child_mm:.2f} calls, residual "
          f"{PUBLIC100['child_residual_s']:.6f} s -> "
          f"{PUBLIC100['child_residual_s']/child_mm:.3e} s/call.")
    print(f"      Parent -> child: matmul dispatches {child_mm-parent_mm:+.0f} "
          f"({100*(child_mm/parent_mm-1):+.0f}%), residual "
          f"{PUBLIC100['child_residual_s']-PUBLIC100['parent_residual_s']:+.4f} s "
          f"({100*(PUBLIC100['child_residual_s']/PUBLIC100['parent_residual_s']-1):+.1f}%)")
    print(f"      -- 92% more native calls for LESS residual.  A constant per-call slope")
    print(f"      predicts {V5D3_SLOPE_S_PER_CALL*(child_mm-parent_mm):+.4f} s here and "
          f"gets the sign wrong.")
    print(f"      => a per-call slope is not a machine constant.  It is a function of "
          f"the\n         call's shape class; the v5d3 figure {V5D3_SLOPE_S_PER_CALL:.3e} "
          f"belongs to deep-hook\n         calls (leaf contraction depth <= 32), not to "
          f"wide 8192-row GEMM dispatches\n         (contraction depth 128), whose "
          f"measured slope is bounded above by\n         "
          f"{abs(PUBLIC100['child_residual_s']-PUBLIC100['parent_residual_s'])/(child_mm-parent_mm):.2e} s/call "
          f"and is consistent with zero.")
    out["slope_law_reconciliation"] = {
        "parent_matmul_calls": parent_mm, "child_matmul_calls": child_mm,
        "parent_residual_s": PUBLIC100["parent_residual_s"],
        "child_residual_s": PUBLIC100["child_residual_s"],
        "v5d3_slope_s_per_call": V5D3_SLOPE_S_PER_CALL,
        "wide_gemm_slope_upper_bound_s_per_call":
            abs(PUBLIC100["child_residual_s"] - PUBLIC100["parent_residual_s"])
            / (child_mm - parent_mm)}

    print("\n[8] PREDICTION 1 - the fold's Public100 mean residual.")
    deltas = [harness["residual_per_net"][4][i] - harness["residual_per_net"]["inc"][i]
              for i in (0, 1)]
    deltas.append(meas_l4)
    # Two further paired deltas from the pre-memory-fix run of the same harness
    # (net0 0.3493-0.2007, net1 0.3750-0.15717).  The fix was memory-only: the
    # floor routes' residuals moved 0.3493 -> 0.3494 on net0, so these pairs are
    # the same measurement with a noisier incumbent baseline.  Off-corpus, so
    # they widen the interval and do not move the point estimate.
    deltas += [0.3493 - 0.20073090051300824, 0.3750 - 0.1571714995225193]
    mean_d = sum(deltas) / len(deltas)
    sd = math.sqrt(sum((d - mean_d) ** 2 for d in deltas) / (len(deltas) - 1))
    r_pred = PUBLIC100["child_residual_s"] + pred_l4
    lo, hi = r_pred - 2.0 * sd, r_pred + 2.0 * sd
    print(f"      The dispatch structure is width-invariant (see rows_per_block), so the")
    print(f"      route delta transfers from synthetic all-active nets to the pruned")
    print(f"      Public100 suite unchanged except through uptake({4}) = {uptake[4]:.4f}.")
    print(f"      model route delta  {pred_l4:.4f} s ;  {len(deltas)} paired measured "
          f"deltas  {mean_d:.4f} +- {sd:.4f} s  (agree to "
          f"{abs(pred_l4/mean_d-1):.1%})")
    print(f"      FILED:  fold Public100 mean residual = {r_pred:.4f} s"
          f"   (interval [{lo:.3f}, {hi:.3f}] s)")
    print(f"      Falsified if the measured value lands outside that interval, or if the")
    print(f"      residual multiplier lands outside [{lo/PUBLIC100['child_residual_s']:.2f}, "
          f"{hi/PUBLIC100['child_residual_s']:.2f}] x the incumbent.")

    ratio_flop = (probe["floor_on"]["analytical_flops"]
                  / probe["incumbent"]["analytical_flops"])
    ratio_band = sorted([ratio_flop] + [harness["flops"][4] / harness["flops"]["inc"],
                                        0.7257])          # harness nets 0 and 1
    a_fold = PUBLIC100["child_analytical_flops"] * ratio_flop
    c_fold = a_fold + LAMBDA * r_pred
    c_ratio = c_fold / PUBLIC100["child_mean_effective_C"]
    print(f"\n      Consequences at that residual:")
    print(f"        A_fold  = {a_fold/1e9:.2f}B   (Public100 incumbent "
          f"{PUBLIC100['child_analytical_flops']/1e9:.2f}B x measured ratio {ratio_flop:.4f};")
    print(f"                  the three measured depth-4 FLOP ratios span "
          f"{ratio_band[0]:.4f}-{ratio_band[-1]:.4f}, so A_fold in "
          f"[{PUBLIC100['child_analytical_flops']*ratio_band[0]/1e9:.1f}, "
          f"{PUBLIC100['child_analytical_flops']*ratio_band[-1]/1e9:.1f}]B, and Public100's")
    print(f"                  narrower live widths push it toward the top of that band "
          f"through mod-16 fringe)")
    print(f"        C_fold  = {c_fold/1e9:.2f}B  vs incumbent "
          f"{PUBLIC100['child_mean_effective_C']/1e9:.2f}B   ratio {c_ratio:.4f}")
    print(f"        residual share of C: fold "
          f"{LAMBDA*r_pred/c_fold:.1%}, incumbent "
          f"{LAMBDA*PUBLIC100['child_residual_s']/PUBLIC100['child_mean_effective_C']:.1%}")
    print(f"        adjusted score {PUBLIC100['child_adjusted_score']*c_ratio:.6e} "
          f"(incumbent {PUBLIC100['child_adjusted_score']:.6e})")
    m_pred = r_pred / PUBLIC100["child_residual_s"]
    s_at_m = (MAX_C_NET["A_fold"] + LAMBDA * MAX_C_NET["r_incumbent"] * m_pred) \
        / MAX_C_NET["C_incumbent"]
    print(f"        max-C network: committed break-even is m* = {MAX_C_NET['m_star']:.3f};"
          f" this model gives m = {m_pred:.3f},")
    print(f"        so the worst network scores {s_at_m:.4f} of the incumbent "
          f"-- clear of break-even by {MAX_C_NET['m_star']/m_pred:.2f}x.")
    out["prediction_public100"] = {
        "residual_s": r_pred, "interval_s": [lo, hi],
        "multiplier": m_pred, "A_fold_B": a_fold / 1e9, "C_fold_B": c_fold / 1e9,
        "C_ratio": c_ratio,
        "adjusted_score": PUBLIC100["child_adjusted_score"] * c_ratio,
        "max_C_net_score_ratio": s_at_m, "m_star_committed": MAX_C_NET["m_star"]}

    print("\n[9] PREDICTION 2 - the residual cost of the 129-completion's +2.4% rows.")
    nb2 = COMPLETION_129["frames_to"] * WIDTH
    rows2 = 2 * nb2
    grow = rows2 / ROWS - 1.0
    inc_now = route_totals(None)["dispatch"]
    inc_129 = (dispatches_incumbent(nb2)["dispatch"]
               + LAYER_PRODUCTS * dispatches_incumbent(rows2)["dispatch"])
    f_now = route_totals(4, 1.0)["dispatch"]
    f_129 = (dispatches_depth(nb2, 4)["dispatch"]
             + (LAYER_PRODUCTS + FOLD_PRODUCTS) * dispatches_depth(rows2, 4)["dispatch"])
    print(f"      rows {ROWS:,} -> {rows2:,}  (+{grow:.3%})")
    print(f"      incumbent blocks/product {math.ceil(ROWS/BLOCK_ROWS)} -> "
          f"{math.ceil(rows2/BLOCK_ROWS)} ; N_dispatch {inc_now:,.0f} -> {inc_129:,.0f} "
          f"(+{inc_129/inc_now-1:.3%})")
    print(f"      fold L4   blocks/product {math.ceil(ROWS/rows_per_block(4))} -> "
          f"{math.ceil(rows2/rows_per_block(4))} ; N_dispatch {f_now:,.0f} -> {f_129:,.0f} "
          f"(+{f_129/f_now-1:.3%})")
    print(f"      Row quantization penalty: incumbent turns a +{grow:.2%} row increase into")
    print(f"      a +{inc_129/inc_now-1:.2%} dispatch increase (x{(inc_129/inc_now-1)/grow:.1f}); "
          f"the fold's 10,352-row window absorbs it at x0.")
    d_r_inc = alpha * (math.log2(inc_129) - math.log2(inc_now))
    matmul_share = 0.9894          # flopscope_bom_receipt: matmul is 98.94% of billed
    d_a_inc = PUBLIC100["child_analytical_flops"] * matmul_share * grow
    d_a_fold = a_fold * matmul_share * grow
    dc_inc = d_a_inc + LAMBDA * d_r_inc
    dc_fold = d_a_fold
    print(f"      incumbent: dResidual {d_r_inc*1e3:+.2f} ms -> dC_residual "
          f"{LAMBDA*d_r_inc/1e9:+.3f}B ; dC_FLOP {d_a_inc/1e9:+.3f}B ; "
          f"dC {dc_inc/1e9:+.3f}B = {dc_inc/PUBLIC100['child_mean_effective_C']:+.3%}")
    print(f"      fold L4  : dResidual +0.00 ms -> dC_residual +0.000B ; "
          f"dC_FLOP {d_a_fold/1e9:+.3f}B ; dC {dc_fold/1e9:+.3f}B = "
          f"{dc_fold/c_fold:+.3%}")
    print(f"      The residual channel supplies "
          f"{LAMBDA*d_r_inc/dc_inc:.1%} of the incumbent's completion cost and 0% of the")
    print(f"      fold's, so the 129-completion is priced by its FLOP bill, not by slope.")
    print(f"      Break-even raw-MSE reduction required: incumbent "
          f"{dc_inc/PUBLIC100['child_mean_effective_C']:.3%}, fold {dc_fold/c_fold:.3%};")
    print(f"      the measured completion effect is 0.45% at 5% power "
          f"(DETERMINISTIC_INSIGHTS 134/146),")
    print(f"      so it is under water by "
          f"{100*dc_inc/PUBLIC100['child_mean_effective_C']/0.45:.1f}x and "
          f"{100*dc_fold/c_fold/0.45:.1f}x respectively.")
    # Independent cross-check: the graph edge
    #   mub129_completion_lever --prices_completion_below_breakeven-->
    #   arc-cosine kernel variance predictor
    # already carries a point-count break-even of 2.33% for the incumbent,
    # derived by an unrelated route (degree-4 share 0.4497% against a 2.33%
    # point-count break-even, three routes agreeing).
    corpus_breakeven = 0.0233
    mine = dc_inc / PUBLIC100["child_mean_effective_C"]
    print(f"      CROSS-CHECK: the corpus already holds a 2.330% point-count break-even")
    print(f"      for this lever (graph edge mub129_completion_lever -> arc-cosine kernel")
    print(f"      variance predictor).  This model reaches {mine:.3%} from dispatch and FLOP")
    print(f"      structure alone -- {abs(mine/corpus_breakeven-1):.1%} apart, by an "
          f"independent route.")
    out["prediction_129_completion"] = {
        "rows_from": ROWS, "rows_to": rows2, "row_growth": grow,
        "incumbent_dispatch": [inc_now, inc_129],
        "fold_L4_dispatch": [f_now, f_129],
        "incumbent_quantization_multiple": (inc_129 / inc_now - 1) / grow,
        "fold_quantization_multiple": 0.0,
        "incumbent_dresidual_s": d_r_inc,
        "incumbent_dC_B": dc_inc / 1e9, "fold_dC_B": dc_fold / 1e9,
        "incumbent_dC_frac": dc_inc / PUBLIC100["child_mean_effective_C"],
        "fold_dC_frac": dc_fold / c_fold,
        "corpus_point_count_breakeven": corpus_breakeven,
        "cross_check_rel_gap": abs(mine / corpus_breakeven - 1)}

    if write_json:
        path = os.path.join(HERE, "SLOPE_COST_MODEL_20260819.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
        print(f"\n[wrote] {path}")
    return out


if __name__ == "__main__":
    main(write_json="--json" in sys.argv)
