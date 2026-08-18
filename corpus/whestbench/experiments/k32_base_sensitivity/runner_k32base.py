"""Base-sensitivity of the surviving high-frequency Fourier-Stein control arm.

This is the never-run "free test" sketched at AGENT_CHANNEL.md:6988-6992 and
corrected at 7120-7135. The question it answers: is the k=2*sqrt(d) rung family
(the campaign's "k32" arm, the only accuracy-side mechanism that showed positive
cross-network transfer) a real high-degree structure, or an artifact of the one
512-row frame its beta was fitted against?

Development-only. No holdout, no truth, no scorer, no sealed manifest. The
runner opens NO file at all: every network, rotation, base row and anchor is
generated from frozen seeds inside this process. Nothing here touches the
Lens-1 seal, and none of the synthetic networks below (labels s0..s7) is named
in it. This cell tests the MECHANISM CLASS; it can neither discharge nor
authorize any decision about the sealed held networks.

DECLARED ASSUMPTIONS (each one is a gap the sources left open; see spec.json
provenance for the citation of each gap):

 A1  a8/a16/a24/a32 are read as the four frozen deep axes anchored at layers
     8, 16, 24, 32 of the depth-32 stack. No source defines the prefix; the
     even spanning of a depth-32 network is the declared reading.
 A2  "k16"/"k32" are read as the paper's two frozen frequencies sqrt(d) and
     2*sqrt(d) at d=256 (DGFL paper line 359). This cell keeps d=256 exactly,
     so both labels stay literally true.
 A3  a_g is the normalized input-space pullback gradient of one selected deep
     preactivation inside a frozen pilot cell (DGFL line 329). Operationalized:
     pilot direction -> forward pass -> at layer L_g take the neuron of largest
     |preactivation| (ties to lowest index) -> backprop through the frozen
     ReLU masks -> Gram-Schmidt against the already-accepted axes -> normalize.
     The deflation step is a declared addition: raw deep pullbacks align at
     0.42-0.86 pairwise at width 256 (measured in hostile review), so without
     it the four rungs collapse toward one and the ridge, not the data, sets
     beta. The pre-deflation alignment is reported in the output as evidence.
 A4  The score inner product <.,.>_s is plain unweighted Euclidean over the
     all-layer post-ReLU stack. The paper never defines it.
 A5  The rung family that is fitted and transported is the four high-frequency
     rungs alone (the channel froze the four k-high rungs, not a joint bank
     with the dipoles). The four low-frequency rungs are fitted and
     transported as a contrast arm and never enter the gate.
 A6  Width is 256 -- the challenge-net family, unnarrowed. (A width-12 draft
     was rejected in hostile review: 1-4 active units per layer makes a
     different, degenerate object.)
 A7  The rotation fixture is shared across networks within a seed and
     independent across seeds. This is stricter pairing than the paper's
     per-network streams and it is what makes the per-net power deltas paired.
 A8  base2 is a union of four complete distinct phased-Hadamard frames -- a
     GUARDS-style multi-frame design standing in for the dead MUB129 base the
     original free-test text named. Both bases are EXACT spherical 2-designs
     (A_2 = 0, verified in-output via Gegenbauer defects); they differ at the
     degree-4 defect by ~4x. This keeps the perturbation in the degree band
     the channel's mechanism implicates (degree >= 4) while holding the
     degree-2 design condition fixed -- the hostile-review requirement.

FLOP_NOTE (analytic, matmul-dominant, reported again at runtime):
  network primal+tangent per row = 4*D*W + 4*(DEPTH-1)*W^2
                                 = 4*256*256 + 4*31*65536 = 8.39e6
  rows per (net,rot): base1 512 + base2 2048 = 2560
  net-rot pairs per seed = 2 fit nets * 8 fit Q + 6 eval nets * 6 held Q = 52
  network  = 3 * 52 * 2560 * 8.39e6 = 3.35e12
  rungs    = 3 * 52 * 2560 * (8*3*P + 8*D)      ~ 8.0e10
  rotation = 3 * 14 * 1280 * 2*D^2               ~ 7.1e9
  Haar QR  = 3 * 14 * (4/3)*D^3                  ~ 9.4e8
  total                                          ~ 3.4e12
"""

from __future__ import annotations

import json
import math
import os
import time

import numpy as np

Array = np.ndarray

SMOKE = os.environ.get("K32_SMOKE") == "1"

# ---- frozen geometry -------------------------------------------------------
D = 256
WIDTH = 256
DEPTH = 32
P = WIDTH * DEPTH
RBAR = math.sqrt(D)                 # E||x|| scale for standard-normal input
K_LO = math.sqrt(D)                 # 16.0 -- the campaign's "k16" arm
K_HI = 2.0 * math.sqrt(D)           # 32.0 -- the campaign's "k32" arm
ANCHOR_LAYERS = (8, 16, 24, 32)     # A1
N_FRAMES_BASE2 = 4                  # A8
if SMOKE:
    N_NETS, N_FIT_Q, N_HELD_Q = 4, 2, 2
    SEEDS = (987654321,)
else:
    N_NETS, N_FIT_Q, N_HELD_Q = 8, 8, 6
    SEEDS = (20260817, 20260818, 20260819)
FIT_NETS = (0, 1)                   # channel 6968: fit nets 0/1 only
EVAL_NETS = tuple(range(2, N_NETS))
N_PROBE_AXES = 64
MAX_DEGREE = 10

# ---- frozen numerics -------------------------------------------------------
RIDGE_SCALE = 2.0**-20              # DGFL eq (8)
SOLVE_RESIDUAL_TOL = 2.0**-40
CLEARANCE = 2.0**-30
DEFLATION_TOL = 1e-8

# ---- frozen gate (metric = 1 - median signed cos; low is good) -------------
PASS_WHEN_LTE = 0.1                 # cos > 0.9 with signs preserved
KILL_WHEN_GTE = 0.4                 # cos < 0.6 or a sign flip
INCONCLUSIVE_METRIC = 0.25          # forced value when the screen finds nothing
POWER_T = 2.0

_IDX = np.arange(D)
_BITS = np.stack([(_IDX >> i) & 1 for i in range(8)], axis=1).astype(np.int64)
_PAIRS = [(i, l) for i in range(8) for l in range(i + 1, 8)]


def r6(x: float) -> float:
    return float(np.round(float(x), 6))


# ---------------------------------------------------------------- bases -----
def hadamard(n: int) -> Array:
    h = np.ones((1, 1), dtype=np.float64)
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]])
    if h.shape[0] != n:
        raise ValueError("n must be a power of two")
    return h


def quadratic_phase(j: int) -> Array:
    """Frozen bent-style quadratic sign pattern for frame j.

    Linear (Hadamard-row) phases only permute the same frame's rows; a
    quadratic Boolean phase produces a genuinely distinct phased frame, the
    real-field analogue of the Kerdock construction the production design uses.
    """
    bits28 = (j * 2654435761) & 0xFFFFFFF
    if bits28 == 0:
        raise ValueError("degenerate (linear) frame phase")
    q = np.zeros(D, dtype=np.int64)
    for t, (i, l) in enumerate(_PAIRS):
        if (bits28 >> t) & 1:
            q += _BITS[:, i] * _BITS[:, l]
    return np.where(q % 2 == 0, 1.0, -1.0)


def base1_primary() -> Array:
    """One complete 256-vector Sylvester-Hadamard frame (antipodes added later)."""
    return hadamard(D) / math.sqrt(D)


def base2_primary() -> Array:
    """Union of four COMPLETE distinct phased-Hadamard frames (A8).

    Each complete frame is an orthonormal basis, hence an exact 2-design; the
    union of exact 2-designs is an exact 2-design, so A_2 stays at machine
    zero while the degree-4 defect drops ~4x versus one frame. The degree-2
    condition is held fixed and only the implicated degrees move.
    """
    h = hadamard(D)
    frames = []
    for j in range(1, N_FRAMES_BASE2 + 1):
        sign = quadratic_phase(j)
        frames.append((h * sign[None, :]) / math.sqrt(D))
    return np.vstack(frames)


def with_antipodes(primary: Array) -> Array:
    return np.vstack([primary, -primary])


def gegenbauer_defects(rows: Array) -> dict:
    """Design defects A_l = mean_{i,j} Q_l(<u_i,u_j>), Q_l normalized Gegenbauer.

    A_l >= 0 always, with A_l = 0 exactly iff the row set integrates all
    degree-l harmonics exactly. This is the mechanism-fidelity check: both
    bases must show A_2 ~ 0 while differing at A_4.
    """
    gram = rows @ rows.T
    alpha = (D - 2) / 2.0
    c_prev = np.ones_like(gram)
    c_curr = 2.0 * alpha * gram
    v_prev, v_curr = 1.0, 2.0 * alpha
    out = {}
    for l in range(2, 7):
        c_next = (2.0 * (l - 1 + alpha) * gram * c_curr
                  - (l - 2 + 2.0 * alpha) * c_prev) / l
        v_next = (2.0 * (l - 1 + alpha) * v_curr - (l - 2 + 2.0 * alpha) * v_prev) / l
        c_prev, c_curr = c_curr, c_next
        v_prev, v_curr = v_curr, v_next
        if l in (2, 4, 6):
            out[f"A{l}"] = float(np.mean(c_curr) / v_curr)
    return out


# ------------------------------------------------------------- networks -----
def make_net(rng: np.random.Generator) -> list[Array]:
    weights = [rng.normal(0.0, math.sqrt(2.0 / D), size=(WIDTH, D))]
    for _ in range(DEPTH - 1):
        weights.append(rng.normal(0.0, math.sqrt(2.0 / WIDTH), size=(WIDTH, WIDTH)))
    return weights


def haar_rotation(rng: np.random.Generator) -> Array:
    a = rng.normal(size=(D, D))
    q, upper = np.linalg.qr(a)
    diag = np.diag(upper)
    return q * np.where(diag >= 0.0, 1.0, -1.0)


def forward_stack(weights: list[Array], x: Array, t: Array) -> tuple[Array, Array]:
    """Primal and one JVP through a bias-free ReLU MLP, all layers returned.

    Frozen convention at exactly zero preactivation: derivative 0 (strict
    positive gate).
    """
    outs, touts = [], []
    for weight in weights:
        pre = x @ weight.T
        tpre = t @ weight.T
        active = pre > 0.0
        x = np.where(active, pre, 0.0)
        t = np.where(active, tpre, 0.0)
        outs.append(x)
        touts.append(t)
    return np.concatenate(outs, axis=1), np.concatenate(touts, axis=1)


def pilot_geometry(weights: list[Array], rng: np.random.Generator) -> dict:
    """Frozen pre-Q pilot: the (m,b) plane and four deflated deep pullback axes."""
    pilot = rng.normal(size=D)
    pilot /= np.linalg.norm(pilot)
    m = rng.normal(size=D)
    m /= np.linalg.norm(m)
    b = rng.normal(size=D)
    b -= (b @ m) * m
    b /= np.linalg.norm(b)

    x = RBAR * pilot
    masks, pres = [], []
    for weight in weights:
        pre = weight @ x
        pres.append(pre)
        masks.append(pre > 0.0)
        x = np.where(pre > 0.0, pre, 0.0)

    raw_axes, picked, clearances = [], [], []
    active_per_layer = [int(mask.sum()) for mask in masks]
    for layer in ANCHOR_LAYERS:
        pre = pres[layer - 1]
        neuron = int(np.argmax(np.abs(pre)))
        clearances.append(float(abs(pre[neuron])))
        grad = weights[layer - 1][neuron, :].copy()
        for lower in range(layer - 1, 0, -1):
            grad = weights[lower - 1].T @ (masks[lower - 1] * grad)
        norm = float(np.linalg.norm(grad))
        if not math.isfinite(norm) or norm <= CLEARANCE:
            raise ValueError(f"degenerate pullback at layer {layer}")
        raw_axes.append(grad / norm)
        picked.append(neuron)

    raw = np.asarray(raw_axes, dtype=np.float64)
    gram = raw @ raw.T
    np.fill_diagonal(gram, 0.0)
    raw_max_align = float(np.max(np.abs(gram)))

    axes = []                                   # A3: Gram-Schmidt deflation
    for g in range(4):
        vec = raw[g].copy()
        for prev in axes:
            vec -= (vec @ prev) * prev
        residual = float(np.linalg.norm(vec))
        if residual < DEFLATION_TOL:
            raise ValueError(f"pullback axis {g} rank-collapsed under deflation")
        axes.append(vec / residual)

    return {
        "m": m,
        "b": b,
        "axes": np.asarray(axes, dtype=np.float64),
        "neurons": picked,
        "min_clearance": float(min(clearances)),
        "raw_max_axis_alignment": raw_max_align,
        "min_active_units": int(min(active_per_layer)),
    }


# ------------------------------------------------------------- controls -----
RUNGS = [(g, K_HI) for g in range(4)] + [(g, K_LO) for g in range(4)]
HI = list(range(0, 4))
LO = list(range(4, 8))


def evaluate(weights: list[Array], geom: dict, u: Array) -> tuple[Array, Array, float]:
    """Base output Y_0(Q) and the eight control features Z_r(Q) on one row set."""
    m, b, axes = geom["m"], geom["b"], geom["axes"]
    um = u @ m
    ub = u @ b
    ju = np.outer(um, b) - np.outer(ub, m)          # J u, J = b m^T - m b^T

    y, dy = forward_stack(weights, RBAR * u, RBAR * ju)
    y0 = y.mean(axis=0)

    dots = u @ axes.T                                # (N,4) a_g . u
    am = axes @ m
    ab = axes @ b
    jdots = um[:, None] * ab[None, :] - ub[:, None] * am[None, :]   # a_g . Ju

    z = np.empty((len(RUNGS), P), dtype=np.float64)
    for i, (g, k) in enumerate(RUNGS):
        phase = k * dots[:, g]
        h = np.cos(phase)
        lie = -k * np.sin(phase) * jdots[:, g]
        z[i] = (h[:, None] * dy + lie[:, None] * y).mean(axis=0)
    return y0, z, float(np.linalg.norm(y0))


# ------------------------------------------------------------------ fit -----
def ridge_fit(store: dict, nets, rungs) -> tuple[Array, dict]:
    """DGFL eq (8): beta = solve(G + lambda I, g) on centered dev rotations."""
    rung_count = len(rungs)
    gram = np.zeros((rung_count, rung_count), dtype=np.float64)
    cross = np.zeros(rung_count, dtype=np.float64)
    blocks = 0
    for w in nets:
        yw, zw = store[w]
        zw = zw[:, rungs, :]
        ytil = yw - yw.mean(axis=0, keepdims=True)
        ztil = zw - zw.mean(axis=0, keepdims=True)
        gram += np.einsum("qrp,qsp->rs", ztil, ztil)
        cross += np.einsum("qrp,qp->r", ztil, ytil)
        blocks += yw.shape[0]
    gram /= blocks
    cross /= blocks

    trace = float(np.trace(gram))
    if not math.isfinite(trace) or trace <= 0.0:
        raise ValueError("nonfinite or nonpositive tr(G)")
    lam = RIDGE_SCALE * trace / rung_count
    a = gram + lam * np.eye(rung_count)
    chol = np.linalg.cholesky(a)                      # one fixed float64 order
    beta = np.linalg.solve(chol.T, np.linalg.solve(chol, cross))
    residual = float(np.linalg.norm(a @ beta - cross) / max(np.linalg.norm(cross), 1e-300))
    if residual >= SOLVE_RESIDUAL_TOL:
        raise ValueError(f"ridge solve residual check failed: {residual}")
    return beta, {
        "trace_G": trace,
        "lambda": lam,
        "cond_G": float(np.linalg.cond(a)),
        "solve_residual": residual,
    }


def held_r2(store: dict, nets, rungs, beta: Array, cols=None):
    """Per-net held whole-rotation trace-variance reduction (DGFL eq 9 shape)."""
    out = []
    for w in nets:
        yw, zw = store[w]
        zw = zw[:, rungs, :]
        if cols is not None:
            yw = yw[:, cols]
            zw = zw[:, :, cols]
        corrected = yw - np.einsum("r,qrp->qp", beta, zw)
        v_unc = float(np.mean(np.sum((yw - yw.mean(axis=0)) ** 2, axis=1)))
        v_ctl = float(np.mean(np.sum((corrected - corrected.mean(axis=0)) ** 2, axis=1)))
        out.append(1.0 - v_ctl / v_unc if v_unc > 0.0 else float("nan"))
    return out


def paired_t(values) -> float:
    arr = np.asarray(values, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size < 2:
        return float("nan")
    sd = float(np.std(arr, ddof=1))
    if sd <= 0.0:
        return float("inf") if float(np.mean(arr)) > 0.0 else 0.0
    return float(np.mean(arr) / (sd / math.sqrt(arr.size)))


# ------------------------------------------------- second signal: degrees ---
def analytic_degree_energy(kappa: float, max_degree: int) -> list[float]:
    """cos(kappa z) = e^{-k^2/2} sum_j (-1)^j k^{2j} He_{2j}(z)/(2j)!  ->
    normalized degree-2j energy = kappa^{4j} / ((2j)! cosh(kappa^2))."""
    energies = []
    for n in range(max_degree + 1):
        if n % 2 == 1:
            energies.append(0.0)
        else:
            j = n // 2
            energies.append(kappa ** (4 * j) / (math.factorial(2 * j) * math.cosh(kappa**2)))
    total = sum(energies)
    return [e / total for e in energies]


def empirical_degree_energy(rows: Array, axes: Array, kappa: float, max_degree: int):
    """Hermite degree profile of cos(k a.u) as the row set actually resolves it."""
    z = math.sqrt(D) * (rows @ axes.T)                 # (N, A)
    f = np.cos(kappa * z)
    he_prev = np.ones_like(z)
    he = z.copy()
    coeffs = [np.mean(f * he_prev, axis=0)]
    coeffs.append(np.mean(f * he, axis=0))
    for n in range(1, max_degree):
        he_next = z * he - n * he_prev
        he_prev, he = he, he_next
        coeffs.append(np.mean(f * he, axis=0) / math.sqrt(math.factorial(n + 1)))
    energy = np.stack([c**2 for c in coeffs])           # (deg+1, A)
    energy = energy / np.sum(energy, axis=0, keepdims=True)
    high = np.sum(energy[6:], axis=0)
    return {
        "degree_energy_mean": [r6(v) for v in np.mean(energy, axis=1)],
        "degree_ge6_fraction_mean": r6(np.mean(high)),
        "degree_ge6_fraction_std": r6(np.std(high)),
    }


# ----------------------------------------------------------------- main -----
def run_seed(seed: int, bases: dict) -> dict:
    rng_net = np.random.Generator(np.random.PCG64DXSM(seed ^ 0x4E455453))
    rng_pilot = np.random.Generator(np.random.PCG64DXSM(seed ^ 0x50494C54))
    rng_rot = np.random.Generator(np.random.PCG64DXSM(seed ^ 0x524F5441))

    nets = [make_net(rng_net) for _ in range(N_NETS)]
    geoms = [pilot_geometry(w, rng_pilot) for w in nets]
    rotations = [haar_rotation(rng_rot) for _ in range(N_FIT_Q + N_HELD_Q)]
    fit_q = list(range(N_FIT_Q))
    held_q = list(range(N_FIT_Q, N_FIT_Q + N_HELD_Q))

    # compact per-net storage: fit nets store their fit rotations, eval nets
    # their held rotations -- nothing else is ever read.
    store = {}
    stack_norms = []
    for name, primary in bases.items():
        per_net = {}
        for w in range(N_NETS):
            wanted = fit_q if w in FIT_NETS else held_q
            yw = np.empty((len(wanted), P))
            zw = np.empty((len(wanted), len(RUNGS), P))
            per_net[w] = (yw, zw)
        for qi, q in enumerate(rotations):
            u = with_antipodes(primary @ q.T)
            for w in range(N_NETS):
                wanted = fit_q if w in FIT_NETS else held_q
                if qi not in wanted:
                    continue
                y0, zr, nrm = evaluate(nets[w], geoms[w], u)
                slot = wanted.index(qi)
                per_net[w][0][slot] = y0
                per_net[w][1][slot] = zr
                if name == "base1":
                    stack_norms.append(nrm)
        store[name] = per_net

    out = {"seed": seed}
    betas, fitdiag = {}, {}
    for name in bases:
        for arm, rungs in (("hi", HI), ("lo", LO)):
            beta, diag = ridge_fit(store[name], FIT_NETS, rungs)
            betas[(name, arm)] = beta
            fitdiag[f"{name}_{arm}"] = diag

    # power screen: base1 beta on base1 held rotations, eval nets only
    r2_hi = held_r2(store["base1"], EVAL_NETS, HI, betas[("base1", "hi")])
    r2_lo = held_r2(store["base1"], EVAL_NETS, LO, betas[("base1", "lo")])
    final_cols = list(range(P - WIDTH, P))
    r2_hi_final = held_r2(store["base1"], EVAL_NETS, HI, betas[("base1", "hi")], final_cols)

    # base2 self-consistency: does the base2 beta reduce base2 variance at all?
    r2_hi_b2 = held_r2(store["base2"], EVAL_NETS, HI, betas[("base2", "hi")])

    # mean-zero probe of the control math (Proposition 1, finite-Q version)
    ratios = []
    for w in EVAL_NETS:
        zw = store["base1"][w][1][:, HI, :]
        centre = float(np.linalg.norm(zw.mean(axis=0)))
        scale = float(np.mean(np.sqrt((zw**2).sum(axis=(1, 2)))))
        ratios.append(centre / max(scale, 1e-300))
    mean_zero_ratio = float(np.mean(ratios))

    out.update({
        "beta_base1_hi": [r6(v) for v in betas[("base1", "hi")]],
        "beta_base2_hi": [r6(v) for v in betas[("base2", "hi")]],
        "beta_base1_lo": [r6(v) for v in betas[("base1", "lo")]],
        "beta_base2_lo": [r6(v) for v in betas[("base2", "lo")]],
        "fit_diagnostics": {k: {kk: (r6(vv) if isinstance(vv, float) else vv)
                                for kk, vv in v.items()} for k, v in fitdiag.items()},
        "held_r2_hi_base1_per_net": [r6(v) for v in r2_hi],
        "held_r2_lo_base1_per_net": [r6(v) for v in r2_lo],
        "held_r2_hi_base2_per_net": [r6(v) for v in r2_hi_b2],
        "held_r2_hi_finallayer_per_net": [r6(v) for v in r2_hi_final],
        "paired_delta_hi_minus_lo_per_net": [r6(a - b) for a, b in zip(r2_hi, r2_lo)],
        "paired_t_hi_base1": r6(paired_t(r2_hi)),
        "paired_t_lo_base1": r6(paired_t(r2_lo)),
        "mean_r2_hi_base1": r6(float(np.nanmean(r2_hi))),
        "mean_zero_ratio_hi": r6(mean_zero_ratio),
        "mean_zero_expected": r6(1.0 / math.sqrt(len(held_q))),
        "min_pilot_clearance": r6(min(g["min_clearance"] for g in geoms)),
        "raw_max_axis_alignment": r6(max(g["raw_max_axis_alignment"] for g in geoms)),
        "min_active_units_any_layer": min(g["min_active_units"] for g in geoms),
        "min_stack_norm": r6(min(stack_norms)),
        "_r2_hi": r2_hi,
    })
    for arm in ("hi", "lo"):
        b1 = betas[("base1", arm)]
        b2 = betas[("base2", arm)]
        cos = float(b1 @ b2 / (np.linalg.norm(b1) * np.linalg.norm(b2)))
        signs_ok = bool(np.all(np.sign(b1) == np.sign(b2)) and np.all(np.sign(b1) != 0))
        out[f"cos_beta_{arm}"] = r6(cos)
        out[f"signs_preserved_{arm}"] = signs_ok
        out[f"signed_cos_{arm}"] = r6(cos if signs_ok else -abs(cos))
    return out


def main() -> None:
    # No blanket exception handler: an implementation failure must crash with a
    # non-zero exit so the harness records an honest PROTOCOL_KILL instead of a
    # fake in-band INCONCLUSIVE (hostile-review blocking finding).
    started = time.perf_counter()
    bases = {"base1": base1_primary(), "base2": base2_primary()}

    per_seed = [run_seed(s, bases) for s in SEEDS]

    seed_means = [s["mean_r2_hi_base1"] for s in per_seed]
    seed_ts = [s["paired_t_hi_base1"] for s in per_seed]
    noise_floor = (float(np.std(seed_means, ddof=1)) if len(seed_means) > 1
                   else float("nan"))

    sign_table = np.array([np.sign(s["beta_base1_hi"]) for s in per_seed])
    signs_consistent = bool(np.all(sign_table == sign_table[0]) and np.all(sign_table[0] != 0))

    # phenomenon gate: the effect must clear the bar in EVERY seed
    # independently (seed = the independent unit; within-seed values share one
    # fitted beta and one rotation fixture and are declared correlated).
    phenomenon_absent = bool(
        (not all(math.isfinite(t) and t >= POWER_T for t in seed_ts))
        or (not all(m > 0.0 for m in seed_means))
        or (not signs_consistent)
    )

    signed = sorted(s["signed_cos_hi"] for s in per_seed)
    if phenomenon_absent:
        metric = INCONCLUSIVE_METRIC
    else:
        metric = 1.0 - signed[len(signed) // 2]       # low = faithful transport

    degrees = {}
    probe_rng = np.random.Generator(np.random.PCG64DXSM(SEEDS[0] ^ 0x50524F42))
    probes = probe_rng.normal(size=(N_PROBE_AXES, D))
    probes /= np.linalg.norm(probes, axis=1, keepdims=True)
    for name, primary in bases.items():
        rows = with_antipodes(primary)
        for arm, k in (("hi", K_HI), ("lo", K_LO)):
            degrees[f"{name}_{arm}"] = empirical_degree_energy(
                rows, probes, k / math.sqrt(D), MAX_DEGREE)
    degrees["analytic_hi"] = [r6(v) for v in analytic_degree_energy(K_HI / math.sqrt(D), MAX_DEGREE)]
    degrees["analytic_lo"] = [r6(v) for v in analytic_degree_energy(K_LO / math.sqrt(D), MAX_DEGREE)]

    defects = {name: {k: float(f"{v:.4e}") for k, v in
                      gegenbauer_defects(with_antipodes(primary)).items()}
               for name, primary in bases.items()}

    rows_per_pair = 2 * D + 2 * N_FRAMES_BASE2 * D
    pairs = len(SEEDS) * (len(FIT_NETS) * N_FIT_Q + len(EVAL_NETS) * N_HELD_Q)
    flops = (pairs * rows_per_pair * (4 * D * WIDTH + 4 * (DEPTH - 1) * WIDTH**2)
             + pairs * rows_per_pair * (len(RUNGS) * 3 * P + 8 * D)
             + len(SEEDS) * (N_FIT_Q + N_HELD_Q) * (D + N_FRAMES_BASE2 * D) * 2 * D * D
             + len(SEEDS) * (N_FIT_Q + N_HELD_Q) * (4.0 / 3.0) * D**3)

    for s in per_seed:
        s.pop("_r2_hi", None)

    print(json.dumps({
        "cell": "k32_base_sensitivity",
        "smoke": SMOKE,
        "metric": r6(metric),
        "gate": {"pass_when_lte": PASS_WHEN_LTE, "kill_when_gte": KILL_WHEN_GTE,
                 "inconclusive_metric": INCONCLUSIVE_METRIC,
                 "metric_definition": "1 - median over seeds of signed cos(beta_base1_hi, beta_base2_hi); signed = cos if all four rung signs preserved else -abs(cos)"},
        "verdict_view": ("INCONCLUSIVE(phenomenon_absent)" if phenomenon_absent
                         else "TRANSPORT_HOLDS" if metric <= PASS_WHEN_LTE
                         else "TRANSPORT_BROKEN" if metric >= KILL_WHEN_GTE
                         else "INCONCLUSIVE"),
        "phenomenon_absent": phenomenon_absent,
        "power_screen": {
            "per_seed_paired_t": seed_ts,
            "paired_t_required_every_seed": POWER_T,
            "per_seed_mean_r2": [r6(v) for v in seed_means],
            "seed_noise_floor_std": r6(noise_floor) if math.isfinite(noise_floor) else None,
            "rung_signs_consistent_across_seeds": signs_consistent,
            "contrast_lo_per_seed_paired_t": [s["paired_t_lo_base1"] for s in per_seed],
            "unit_of_analysis_note": "seed is the independent unit; within-seed nets share one beta and one rotation fixture",
        },
        "transport": {
            "cos_beta_hi_per_seed": [s["cos_beta_hi"] for s in per_seed],
            "cos_beta_lo_per_seed": [s["cos_beta_lo"] for s in per_seed],
            "signs_preserved_hi_per_seed": [s["signs_preserved_hi"] for s in per_seed],
            "signs_preserved_lo_per_seed": [s["signs_preserved_lo"] for s in per_seed],
        },
        "second_signal_degree_energy": degrees,
        "second_signal_design_defects": defects,
        "bases": {
            "base1_rows_antipodal": 2 * D,
            "base2_rows_antipodal": 2 * N_FRAMES_BASE2 * D,
            "base2_frames": N_FRAMES_BASE2,
        },
        "per_seed": per_seed,
        "config": {"d": D, "width": WIDTH, "depth": DEPTH, "p": P,
                   "k_hi": K_HI, "k_lo": K_LO, "anchor_layers": list(ANCHOR_LAYERS),
                   "fit_net_labels": [f"s{w}" for w in FIT_NETS],
                   "eval_net_labels": [f"s{w}" for w in EVAL_NETS],
                   "fit_rotations": N_FIT_Q, "held_rotations": N_HELD_Q,
                   "seeds": list(SEEDS)},
        "flops_declared": float(f"{flops:.4g}"),
        "wall_seconds": r6(time.perf_counter() - started),
    }))


if __name__ == "__main__":
    main()
