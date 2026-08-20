"""Base-sensitivity of the surviving high-frequency Fourier-Stein control arm.

This is the never-run "free test" sketched at AGENT_CHANNEL.md:6988-6992 and
corrected at 7120-7135. The question it answers: is the k=2*sqrt(d) rung family
(the campaign's "k32" arm, the only accuracy-side mechanism that showed positive
cross-network transfer) a real high-degree structure, or an artifact of the one
512-row frame its beta was fitted against?

Development-only. No holdout, no net2/net3, no truth, no scorer, no sealed
manifest. The runner opens NO file at all: every network, rotation, base row and
anchor is generated from frozen seeds inside this process. Nothing here touches
the Lens-1 seal 55EBEBBB..., and none of the networks below is named in it.

DECLARED ASSUMPTIONS (each one is a gap the sources left open; see spec_draft.json
provenance for the citation of each gap):

 A1  a8/a16/a24/a32 are read as the four frozen deep axes anchored at layers
     8, 16, 24, 32 of the depth-32 stack. No source defines the prefix; the
     even spanning of a depth-32 network is the declared reading.
 A2  "k16"/"k32" are read as the paper's two frozen frequencies sqrt(d) and
     2*sqrt(d) at d=256 (DGFL paper line 359). This cell keeps d=256 exactly, so
     both labels stay literally true.
 A3  a_g is the normalized input-space pullback gradient of one selected deep
     preactivation inside a frozen pilot cell (DGFL line 329). Operationalized
     here as: pilot direction -> forward pass -> at layer L_g take the neuron of
     largest |preactivation| (ties to the lowest index) -> backprop that unit
     through the frozen ReLU masks to the input -> normalize.
 A4  The score inner product <.,.>_s is plain unweighted Euclidean over the
     all-layer post-ReLU stack. The paper never defines it.
 A5  The rung family that is fitted and transported is the four high-frequency
     rungs alone (the channel froze "all four k=32 rungs", not a joint bank with
     the dipoles). The four low-frequency rungs are fitted and transported as a
     contrast arm and never enter the gate.
 A6  The network width is narrowed from 256 to 12 (depth 32, input d=256, bias
     free He init all preserved). At width 256 this design costs 2.05e12 numpy
     FLOPs, 102x over the 2e10 ceiling. See FLOP_NOTE below.
 A7  The rotation fixture is shared across networks within a seed and
     independent across seeds. This is stricter pairing than the paper's
     per-network streams and it is what makes the per-net power deltas paired.
 A8  base2 is the production-side GUARDS126-style multi-frame design, not the
     dead MUB129 base named in the original free-test text. The substitution is
     a premise shift, declared in the spec.

FLOP_NOTE (analytic, matmul-dominant, reported again at runtime):
  network primal+tangent per row = 4*L1 + 4*(DEPTH-1)*WIDTH^2
                                 = 4*256*12 + 4*31*144 = 30144
  rows evaluated = 3 seeds * 2 bases * (2 fit nets * 8 fit Q
                   + 8 eval nets * 8 held Q) * ~508 rows = 243840
  network       = 243840 * 30144            = 7.35e9
  rung algebra  = 243840 * (8*3*P + 4*2*d)  = 2.80e9
  row rotation  = 3*2*16 * 2*Nprimary*d^2   = 3.20e9
  Haar QR       = 3*16 * (4/3)*d^3          = 1.07e9
  total                                     = 1.44e10  < 2e10
"""

from __future__ import annotations

import json
import math
import time

import numpy as np

Array = np.ndarray

# ---- frozen geometry -------------------------------------------------------
D = 256
WIDTH = 12
DEPTH = 32
P = WIDTH * DEPTH
RBAR = math.sqrt(D)                 # E||x|| scale for standard-normal input
K_LO = math.sqrt(D)                 # 16.0 -- the campaign's "k16" arm
K_HI = 2.0 * math.sqrt(D)           # 32.0 -- the campaign's "k32" arm
ANCHOR_LAYERS = (8, 16, 24, 32)     # A1
N_NETS = 10
FIT_NETS = (0, 1)                   # channel 6968: fit nets 0/1 only
EVAL_NETS = (2, 3, 4, 5, 6, 7, 8, 9)
N_FIT_Q = 8
N_HELD_Q = 8
SEEDS = (20260817, 20260818, 20260819)
N_PROBE_AXES = 64
MAX_DEGREE = 10

# ---- frozen numerics -------------------------------------------------------
RIDGE_SCALE = 2.0**-20              # DGFL eq (8)
SOLVE_RESIDUAL_TOL = 2.0**-40
CLEARANCE = 2.0**-30
COLLINEAR_TOL = 1e-6

# ---- frozen gate -----------------------------------------------------------
GATE_PASS = 0.9                     # channel 6989: cos(beta_a, beta_b) > 0.9
GATE_KILL = 0.6
INCONCLUSIVE_METRIC = 0.75          # forced value when the screen finds nothing
POWER_T = 2.0

_IDX = np.arange(D)
_BITS = np.stack([(_IDX >> i) & 1 for i in range(8)], axis=1).astype(np.int64)
_PAIRS = [(i, l) for i in range(8) for l in range(i + 1, 8)]


def r6(x: float) -> float:
    return float(np.round(float(x), 6))


# ---------------------------------------------------------------- bases -----
def hadamard(n: int) -> Array:
    """Sylvester Hadamard matrix; n must be a power of two."""
    h = np.ones((1, 1), dtype=np.float64)
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]])
    if h.shape[0] != n:
        raise ValueError("n must be a power of two")
    return h


def quadratic_phase(j: int) -> Array:
    """Frozen bent-style quadratic sign pattern for frame j.

    A linear (Hadamard-row) sign pattern would be useless here: for the Sylvester
    matrix H[r] * H[j] == H[r xor j], so linear phases only permute the rows of
    the same frame. A quadratic Boolean phase produces a genuinely distinct
    phased-Hadamard frame, which is the real-field analogue of the Kerdock /
    delta-set construction the production design is built from.
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
    """One complete 256-vector phased-Hadamard frame (antipodes added later)."""
    return hadamard(D) / math.sqrt(D)


def base2_primary() -> Array:
    """GUARDS126-style multi-frame base: 126 distinct frames, 2 vectors each.

    The full production-shaped object is 126 frames x 512 rows = 64512 rows,
    which costs 126x this cell's network budget (1.5e12 FLOPs, 75x over the
    ceiling). The declared subsample keeps the frame multiplicity -- the property
    under test -- and matches base1's row count to within 8 rows (504 vs 512).
    """
    h = hadamard(D)
    rows = []
    for j in range(1, 127):
        sign = quadratic_phase(j)
        frame = (h * sign[None, :]) / math.sqrt(D)
        rows.append(frame[(2 * j) % D])
        rows.append(frame[(2 * j + 1) % D])
    return np.asarray(rows, dtype=np.float64)


def with_antipodes(primary: Array) -> Array:
    return np.vstack([primary, -primary])


def coherence(primary: Array) -> float:
    gram = primary @ primary.T
    np.fill_diagonal(gram, 0.0)
    return float(np.max(np.abs(gram)))


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
    positive gate), matching dgfl1_f0.forward_jvp.
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
    """Frozen pre-Q pilot: the (m,b) plane and the four deep pullback axes (A3)."""
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

    axes, picked, clearances = [], [], []
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
        axes.append(grad / norm)
        picked.append(neuron)

    axes_arr = np.asarray(axes, dtype=np.float64)
    gram = axes_arr @ axes_arr.T
    np.fill_diagonal(gram, 0.0)
    max_align = float(np.max(np.abs(gram)))
    if max_align > 1.0 - COLLINEAR_TOL:
        raise ValueError("deep pullback axes are nearly collinear")

    return {
        "m": m,
        "b": b,
        "axes": axes_arr,
        "neurons": picked,
        "min_clearance": float(min(clearances)),
        "max_axis_alignment": max_align,
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
def ridge_fit(y: Array, z: Array, nets, q_idx, rungs) -> tuple[Array, dict]:
    """DGFL eq (8): beta = solve(G + lambda I, g) on centered dev rotations."""
    rung_count = len(rungs)
    gram = np.zeros((rung_count, rung_count), dtype=np.float64)
    cross = np.zeros(rung_count, dtype=np.float64)
    blocks = 0
    for w in nets:
        yw = y[w, q_idx, :]
        zw = z[w][np.ix_(q_idx, rungs)]
        ytil = yw - yw.mean(axis=0, keepdims=True)
        ztil = zw - zw.mean(axis=0, keepdims=True)
        gram += np.einsum("qrp,qsp->rs", ztil, ztil)
        cross += np.einsum("qrp,qp->r", ztil, ytil)
        blocks += len(q_idx)
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
    return beta, {
        "trace_G": trace,
        "lambda": lam,
        "cond_G": float(np.linalg.cond(a)),
        "solve_residual": residual,
        "residual_ok": bool(residual < SOLVE_RESIDUAL_TOL),
    }


def held_r2(y: Array, z: Array, nets, q_idx, rungs, beta: Array, cols=None):
    """Per-net held whole-rotation trace-variance reduction (DGFL eq 9 shape)."""
    out = []
    for w in nets:
        yw = y[w, q_idx, :]
        zw = z[w][np.ix_(q_idx, rungs)]
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
    """Hermite degree profile of cos(k a.u) as the row set actually resolves it.

    z = sqrt(d) * (a.u) is standard normal in the ideal continuum limit; a design
    that only integrates low-degree harmonics exactly will misreport the high
    degrees, which is precisely the mechanism by which a control that lives at
    degree >= 6 could be base-dependent.
    """
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
    moments = {}
    for j in range(1, 7):
        expected = float(np.prod(np.arange(1, 2 * j, 2)))
        ratio = np.mean(z ** (2 * j), axis=0) / expected
        moments[f"m{2*j}_ratio_mean"] = r6(np.mean(ratio))
        moments[f"m{2*j}_ratio_std"] = r6(np.std(ratio))
    return {
        "degree_energy_mean": [r6(v) for v in np.mean(energy, axis=1)],
        "degree_ge6_fraction_mean": r6(np.mean(high)),
        "degree_ge6_fraction_std": r6(np.std(high)),
        "moment_ratios": moments,
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

    store = {}
    stack_norms = []
    for name, primary in bases.items():
        y = np.full((N_NETS, len(rotations), P), np.nan)
        z = np.full((N_NETS, len(rotations), len(RUNGS), P), np.nan)
        for qi, q in enumerate(rotations):
            u = with_antipodes(primary @ q.T)
            for w in range(N_NETS):
                wanted = fit_q if w in FIT_NETS else held_q
                if qi not in wanted:
                    continue
                y0, zr, nrm = evaluate(nets[w], geoms[w], u)
                y[w, qi] = y0
                z[w, qi] = zr
                if name == "base1":
                    stack_norms.append(nrm)
        store[name] = (y, z)

    out = {"seed": seed}
    betas, fitdiag = {}, {}
    for name in bases:
        y, z = store[name]
        for arm, rungs in (("hi", HI), ("lo", LO)):
            beta, diag = ridge_fit(y, z, FIT_NETS, fit_q, rungs)
            betas[(name, arm)] = beta
            fitdiag[f"{name}_{arm}"] = diag

    # power screen: base1 beta on base1 held rotations, eval nets only
    y1, z1 = store["base1"]
    r2_hi = held_r2(y1, z1, EVAL_NETS, held_q, HI, betas[("base1", "hi")])
    r2_lo = held_r2(y1, z1, EVAL_NETS, held_q, LO, betas[("base1", "lo")])
    final_cols = list(range(P - WIDTH, P))
    r2_hi_final = held_r2(y1, z1, EVAL_NETS, held_q, HI, betas[("base1", "hi")], final_cols)

    # base2 self-consistency: does the base2 beta reduce base2 variance at all?
    y2, z2 = store["base2"]
    r2_hi_b2 = held_r2(y2, z2, EVAL_NETS, held_q, HI, betas[("base2", "hi")])

    # mean-zero probe of the control math (Proposition 1, finite-Q version)
    zz = z1[EVAL_NETS][:, held_q][:, :, HI, :]
    centre = np.linalg.norm(zz.mean(axis=1), axis=-1)
    scale = np.sqrt((zz**2).sum(axis=-1)).mean(axis=1)
    mean_zero_ratio = float(np.mean(centre / np.maximum(scale, 1e-300)))

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
        "paired_t_hi_base1": r6(paired_t(r2_hi)),
        "paired_t_lo_base1": r6(paired_t(r2_lo)),
        "mean_r2_hi_base1": r6(float(np.nanmean(r2_hi))),
        "mean_zero_ratio_hi": r6(mean_zero_ratio),
        "mean_zero_expected": r6(1.0 / math.sqrt(len(held_q))),
        "min_pilot_clearance": r6(min(g["min_clearance"] for g in geoms)),
        "max_axis_alignment": r6(max(g["max_axis_alignment"] for g in geoms)),
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
    started = time.perf_counter()
    kill = None
    bases = {"base1": base1_primary(), "base2": base2_primary()}

    try:
        per_seed = [run_seed(s, bases) for s in SEEDS]
    except Exception as exc:                       # predeclared implementation kill
        print(json.dumps({
            "cell": "k32_base_sensitivity",
            "implementation_kill": f"{type(exc).__name__}: {exc}",
            "metric": INCONCLUSIVE_METRIC,
            "phenomenon_absent": True,
            "wall_seconds": r6(time.perf_counter() - started),
        }))
        return

    pooled_r2 = [v for s in per_seed for v in s["_r2_hi"]]
    pooled_t = paired_t(pooled_r2)
    seed_means = [s["mean_r2_hi_base1"] for s in per_seed]
    noise_floor = float(np.std(seed_means, ddof=1))

    sign_table = np.array([np.sign(s["beta_base1_hi"]) for s in per_seed])
    signs_consistent = bool(np.all(sign_table == sign_table[0]) and np.all(sign_table[0] != 0))
    residuals_ok = all(d["residual_ok"] for s in per_seed for d in s["fit_diagnostics"].values())

    phenomenon_absent = bool(
        not math.isfinite(pooled_t) or pooled_t < POWER_T or not signs_consistent
    )

    signed = sorted(s["signed_cos_hi"] for s in per_seed)
    metric = INCONCLUSIVE_METRIC if phenomenon_absent else signed[len(signed) // 2]

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

    rows_eval = 3 * 2 * (len(FIT_NETS) * N_FIT_Q + len(EVAL_NETS) * N_HELD_Q)
    avg_rows = (2 * D + 2 * 252) / 2
    flops = (rows_eval * avg_rows * (4 * D * WIDTH + 4 * (DEPTH - 1) * WIDTH**2)
             + rows_eval * avg_rows * (len(RUNGS) * 3 * P + 8 * D)
             + len(SEEDS) * 2 * (N_FIT_Q + N_HELD_Q) * 2 * D * D * D
             + len(SEEDS) * (N_FIT_Q + N_HELD_Q) * (4.0 / 3.0) * D**3)

    for s in per_seed:
        s.pop("_r2_hi", None)

    print(json.dumps({
        "cell": "k32_base_sensitivity",
        "metric": r6(metric),
        "gate": {"pass_when_gte": GATE_PASS, "kill_when_lte": GATE_KILL,
                 "inconclusive_metric": INCONCLUSIVE_METRIC},
        "verdict": ("INCONCLUSIVE(phenomenon_absent)" if phenomenon_absent
                    else "PASS" if metric >= GATE_PASS
                    else "KILL" if metric <= GATE_KILL else "INCONCLUSIVE"),
        "phenomenon_absent": phenomenon_absent,
        "power_screen": {
            "pooled_paired_t": r6(pooled_t),
            "paired_t_required": POWER_T,
            "per_seed_paired_t": [s["paired_t_hi_base1"] for s in per_seed],
            "per_seed_mean_r2": [r6(v) for v in seed_means],
            "seed_noise_floor_std": r6(noise_floor),
            "rung_signs_consistent_across_seeds": signs_consistent,
            "contrast_lo_per_seed_paired_t": [s["paired_t_lo_base1"] for s in per_seed],
        },
        "transport": {
            "cos_beta_hi_per_seed": [s["cos_beta_hi"] for s in per_seed],
            "cos_beta_lo_per_seed": [s["cos_beta_lo"] for s in per_seed],
            "signs_preserved_hi_per_seed": [s["signs_preserved_hi"] for s in per_seed],
            "signs_preserved_lo_per_seed": [s["signs_preserved_lo"] for s in per_seed],
            "signs_base1_hi_per_seed": [[int(np.sign(v)) for v in s["beta_base1_hi"]] for s in per_seed],
            "signs_base2_hi_per_seed": [[int(np.sign(v)) for v in s["beta_base2_hi"]] for s in per_seed],
        },
        "second_signal_degree_energy": degrees,
        "bases": {
            "base1_rows": 2 * D, "base2_rows": 2 * 252,
            "base1_coherence": r6(coherence(bases["base1"])),
            "base2_coherence": r6(coherence(bases["base2"])),
            "cross_max_abs_inner": r6(float(np.max(np.abs(bases["base2"] @ bases["base1"].T)))),
        },
        "per_seed": per_seed,
        "solve_residuals_ok": residuals_ok,
        "config": {"d": D, "width": WIDTH, "depth": DEPTH, "p": P,
                   "k_hi": K_HI, "k_lo": K_LO, "anchor_layers": list(ANCHOR_LAYERS),
                   "fit_nets": list(FIT_NETS), "eval_nets": list(EVAL_NETS),
                   "fit_rotations": N_FIT_Q, "held_rotations": N_HELD_Q,
                   "seeds": list(SEEDS)},
        "flops_declared": float(f"{flops:.4g}"),
        "wall_seconds": r6(time.perf_counter() - started),
    }))


if __name__ == "__main__":
    main()
