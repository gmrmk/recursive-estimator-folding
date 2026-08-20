"""Fable's INDEPENDENT M243 oracle (G0A formula oracle + G0B per-event oracle).

Implemented SOLELY from the two hash-verified frozen inputs:

  M243_PREDECLARATION_20260809.md
    sha256 a53e3cbf58b9bdc290e6abbf3323a1b7e5162a370774dcd918ddb2193340a9c3
  M243_FROZEN_MANIFEST_20260809.json
    sha256 2f788fdc8d91abb8cd43b9ce82140c12cc5707b49b9f815c56abae105b906895

No candidate/implementation code from the m243_event_local_q4_source_premise
folder was read.  Frozen SHARED corpus modules (hash-pinned by the manifest's
parent_sha256 block) are imported read-only:

  m178_certified_phi2_owent.py  -- certified Phi2 jet (actual-M178 arm)
  m133_ht_hidden_edge.py        -- Factored211Proposal q0 (uniform_mixture=0.05)
  m151_b1_forward_control.py    -- three-slot [2,1,1] source feature F_e
  m122_nonzero_bridge.py        -- per-node Hermite coefficients, tree
                                   convention, GH cross-check moments

Firewall: no B1 state, no dtilde, no residual H_e, no V_H, no M196 cells,
no response/truth/scorer/challenge-weight/submission machinery anywhere in
this module.  All failure paths raise (fail closed); there is no silent zero
fallback and no clipping.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import sys
from dataclasses import dataclass, field

import numpy as np
import mpmath as mp

# --------------------------------------------------------------------------
# Frozen constants (transcribed from the two hash-verified inputs only)
# --------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_EXPERIMENTS = os.path.dirname(_HERE)
FROZEN_DIR = os.path.join(_EXPERIMENTS, "m243_event_local_q4_source_premise")

PREDECLARATION_NAME = "M243_PREDECLARATION_20260809.md"
MANIFEST_NAME = "M243_FROZEN_MANIFEST_20260809.json"
PREDECLARATION_SHA256 = (
    "a53e3cbf58b9bdc290e6abbf3323a1b7e5162a370774dcd918ddb2193340a9c3")
MANIFEST_SHA256 = (
    "2f788fdc8d91abb8cd43b9ce82140c12cc5707b49b9f815c56abae105b906895")

# manifest parent_sha256 block (frozen shared corpus, hash-pinned)
PARENT_SHA256 = {
    "m122_nonzero_bridge.py":
        "c765fe24818f4ec8928a879e217a530077edff98f729555739202c1f7286f927",
    "m133_ht_hidden_edge.py":
        "c296c95ede532c1451e0444b9d56b51e96287ef251b11de9cacee0df7d1ea6b1",
    "m151_b1_forward_control.py":
        "520431079e63b4bb82c6fe3db997d875ce31fc4037538eb64ce7fea24bf55cd5",
    "m178_certified_phi2_owent.py":
        "fa3614a22c2250f69f4d891834cc1e7ca6bd8874d67575b87c7d3fa8598f1c5c",
}
SHARED_MODULE_PATHS = {
    "m122_nonzero_bridge.py":
        os.path.join(_EXPERIMENTS, "m122_nonzero_bridge_theory",
                     "m122_nonzero_bridge.py"),
    "m133_ht_hidden_edge.py":
        os.path.join(_EXPERIMENTS, "m133_ht_hidden_edge",
                     "m133_ht_hidden_edge.py"),
    "m151_b1_forward_control.py":
        os.path.join(_EXPERIMENTS, "m151_b1_forward_control",
                     "m151_b1_forward_control.py"),
    "m178_certified_phi2_owent.py":
        os.path.join(_EXPERIMENTS, "m178_certified_phi2_owent",
                     "m178_certified_phi2_owent.py"),
}

# G0A frozen grid (predeclaration section 8 / manifest g0a block)
MPMATH_DPS = (80, 100)
REFERENCE_SELF_TOL = 2e-12      # * (1+abs(reference))
FORMULA_TOL = 2e-10             # * (1+abs(reference))
EXPECTATION_TOL = 5e-8          # * (1+abs(reference))
INVARIANCE_TOL = 2e-10
TAIL_G = (0.0, 0.00390625, -0.00390625, 0.25, -0.25, 1.0, -1.0,
          2.5, -2.5, 5.0, -5.0, 8.0, -8.0, 10.0, -10.0, 16.0, -16.0)
G0A_GENERATED = ((3, 243700003), (5, 243700005), (7, 243700007))

# G0B frozen grid (predeclaration section 9 / manifest g0b block)
G0B_CELLS = {"P0": (24312001, 0.20), "P1": (24312002, 0.52)}
G0B_WIDTH = 12
EVENT_DRAWS_PER_CELL = 128
EVENT_STREAM_OFFSET = 100000000
UNIFORM_MIXTURE = 0.05
BOOTSTRAP_SEED = 2430002
BOOTSTRAP_REPLICATES = 20000
GATE_UPPER90_NQ4_NANTI = 0.50
GATE_UPPER90_NQ4_VDELTA = 0.20
GATE_P99_Q4_ANTI = 1.25

# Shard map (task directive; NOT in the predeclaration text -- see DEVIATIONS
# in FABLE_G0A_READINESS.md): shard s -> (cell, occurrence index range).
SHARDS = {0: ("P0", 0, 64), 1: ("P0", 64, 128),
          2: ("P1", 0, 64), 3: ("P1", 64, 128)}

WALL_CLOCK_CAP_S = 5400.0
MEMORY_CAP_MIB = 2048.0


class OracleHardFail(RuntimeError):
    """Any hash/q_e/precision/finiteness violation.  Fail closed, no retry."""


@dataclass(frozen=True)
class TypedRefusal:
    """Typed refusal per predeclaration section 7 (never a numeric value)."""
    stratum: str
    reason: str


# --------------------------------------------------------------------------
# Hash verification hooks
# --------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_frozen_inputs(frozen_dir: str = FROZEN_DIR) -> dict:
    """Hard-fail unless the predeclaration and manifest bytes match the
    frozen SHA-256 values.  Read-only: never writes into frozen_dir."""
    out = {}
    for name, want in ((PREDECLARATION_NAME, PREDECLARATION_SHA256),
                       (MANIFEST_NAME, MANIFEST_SHA256)):
        path = os.path.join(frozen_dir, name)
        if not os.path.isfile(path):
            raise OracleHardFail(f"frozen input missing: {path}")
        got = sha256_file(path)
        if got != want:
            raise OracleHardFail(
                f"frozen input hash mismatch for {name}: got {got}")
        out[name] = got
    return out


_MODULE_CACHE: dict = {}


def import_frozen(name: str):
    """Import a hash-pinned shared corpus module.  Hard-fail on any
    hash mismatch against the manifest parent_sha256 block."""
    if name in _MODULE_CACHE:
        return _MODULE_CACHE[name]
    path = SHARED_MODULE_PATHS[name]
    if not os.path.isfile(path):
        raise OracleHardFail(f"shared frozen module missing: {path}")
    got = sha256_file(path)
    if got != PARENT_SHA256[name]:
        raise OracleHardFail(
            f"shared module hash mismatch for {name}: got {got}")
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name[:-3]] = module   # dataclasses needs the registration
    spec.loader.exec_module(module)
    _MODULE_CACHE[name] = module
    return module


def validate_manifest(path: str | None = None) -> dict:
    """Parse the frozen manifest and hard-fail unless every field this
    oracle depends on equals its frozen expectation (format validation
    only -- the values are re-pinned constants, not new data)."""
    if path is None:
        path = os.path.join(FROZEN_DIR, MANIFEST_NAME)
    with open(path, "r", encoding="utf-8") as f:
        m = json.load(f)
    checks = [
        (m.get("candidate"), "M243"),
        (tuple(m["g0a"]["mpmath_dps"]), MPMATH_DPS),
        (tuple(m["g0a"]["tail_g"]), TAIL_G),
        (tuple(tuple(x) for x in m["g0a"]["generated_width_seed"]),
         G0A_GENERATED),
        (m["g0b"]["event_draws_per_cell"], EVENT_DRAWS_PER_CELL),
        (m["g0b"]["event_stream_offset"], EVENT_STREAM_OFFSET),
        (m["g0b"]["bootstrap_seed"], BOOTSTRAP_SEED),
        (m["g0b"]["bootstrap_replicates"], BOOTSTRAP_REPLICATES),
        (m["g0b"]["upper90_nq4_to_nanti"], GATE_UPPER90_NQ4_NANTI),
        (m["g0b"]["upper90_nq4_to_vdelta"], GATE_UPPER90_NQ4_VDELTA),
        (m["g0b"]["p99_q4_to_anti"], GATE_P99_Q4_ANTI),
    ]
    for got, want in checks:
        if got != want:
            raise OracleHardFail(
                f"manifest field mismatch: got {got!r}, expected {want!r}")
    cells = {c["name"]: (c["seed"], c["correlation_mix"], c["width"])
             for c in m["g0b"]["cells"]}
    for name, (seed, mix) in G0B_CELLS.items():
        if cells.get(name) != (seed, mix, G0B_WIDTH):
            raise OracleHardFail(f"manifest g0b cell mismatch for {name}")
    if "uniform_mixture=0.05" not in m["g0b"]["proposal"].replace(" ", ""):
        raise OracleHardFail("manifest proposal string mismatch")
    for k, v in PARENT_SHA256.items():
        if m["parent_sha256"].get(k) != v:
            raise OracleHardFail(f"manifest parent_sha256 mismatch for {k}")
    return m


# --------------------------------------------------------------------------
# Independent high-precision reference (mpmath).  Independently assembled:
# Phi2 by one-dimensional quadrature (NOT Owen-T), positive-part product
# moment from the standard bivariate formula.  Does not call M178 and does
# not use the proposed M243 beta/R closed forms.
# --------------------------------------------------------------------------

def _phi(x):
    return mp.npdf(x)


def _Phi(x):
    return mp.ncdf(x)


def _phi2(a, b, rho):
    s2 = (1 - rho) * (1 + rho)
    q = (a * a - 2 * rho * a * b + b * b) / (2 * s2)
    return mp.exp(-q) / (2 * mp.pi * mp.sqrt(s2))


def _Phi2(a, b, rho):
    """Phi2(a,b;rho) via a 1-D integral -- independent of the M178 method."""
    rho = mp.mpf(rho)
    if abs(rho) >= mp.mpf(1) - mp.mpf("1e-12"):
        raise OracleHardFail("Phi2 correlation at/beyond +-1: fail closed")
    if rho == 0:
        return _Phi(a) * _Phi(b)
    s = mp.sqrt((1 - rho) * (1 + rho))
    f = lambda t: _phi(t) * _Phi((b - rho * t) / s)
    return mp.quad(f, [-mp.inf, a])


def relu_mean_mp(m, s):
    s = mp.mpf(s)
    al = mp.mpf(m) / s
    return s * (al * _Phi(al) + _phi(al))


def relu_second_mp(m, s):
    s = mp.mpf(s)
    al = mp.mpf(m) / s
    return s * s * ((al * al + 1) * _Phi(al) + al * _phi(al))


def pospart_product_mp(m1, m2, s1, s2, rho):
    """E[relu(X1) relu(X2)] for bivariate normal (standard assembly)."""
    s1 = mp.mpf(s1)
    s2 = mp.mpf(s2)
    a1 = mp.mpf(m1) / s1
    a2 = mp.mpf(m2) / s2
    rho = mp.mpf(rho)
    if abs(rho) >= mp.mpf(1) - mp.mpf("1e-12"):
        raise OracleHardFail("pospart correlation at/beyond +-1: fail closed")
    s = mp.sqrt((1 - rho) * (1 + rho))
    val = ((a1 * a2 + rho) * _Phi2(a1, a2, rho)
           + a2 * _phi(a1) * _Phi((a2 - rho * a1) / s)
           + a1 * _phi(a2) * _Phi((a1 - rho * a2) / s)
           + s * s * _phi2(a1, a2, rho))
    return s1 * s2 * val


HE = (
    lambda g: g * 0 + 1,
    lambda g: g,
    lambda g: g * g - 1,
    lambda g: g * g * g - 3 * g,
    lambda g: g * g * g * g - 6 * g * g + 3,
)


def _require_strict(width_or_none, i, j, k):
    """Section 7 ownership: only pairwise-distinct (i,j,k).  Everything
    else is a TypedRefusal (never a number)."""
    if len({i, j, k}) != 3:
        return TypedRefusal("collision", f"non-pairwise-distinct ({i},{j},{k})")
    if width_or_none is not None:
        if not all(0 <= t < width_or_none for t in (i, j, k)):
            return TypedRefusal("range", f"label out of range ({i},{j},{k})")
    return None


def refuse_stratum(name: str) -> TypedRefusal:
    """[4], [3,1], [2,2], [1,1,1,1] requests must return a typed refusal."""
    if name not in ("[4]", "[3,1]", "[2,2]", "[1,1,1,1]"):
        raise OracleHardFail(f"unknown stratum request {name!r}")
    return TypedRefusal(name, "M243 emits no numeric value on this stratum")


# --------------------------------------------------------------------------
# Event context: everything deterministic per (cell, e=(i,j,k))
# --------------------------------------------------------------------------

@dataclass
class EventContext:
    mu: np.ndarray
    C: np.ndarray
    i: int
    j: int
    k: int
    dps: int
    # filled in __post_init__ at working precision self.dps
    sigma_i: mp.mpf = field(init=False)
    alpha_i: mp.mpf = field(init=False)
    m_i: mp.mpf = field(init=False)
    m_j: mp.mpf = field(init=False)
    m_k: mp.mpf = field(init=False)
    kj: mp.mpf = field(init=False)   # C_ij / sigma_i
    kk: mp.mpf = field(init=False)   # C_ik / sigma_i
    svj: mp.mpf = field(init=False)  # conditional std of X_j | G
    svk: mp.mpf = field(init=False)
    crho: mp.mpf = field(init=False)
    wick: mp.mpf = field(init=False)  # V_ii V_jk + 2 V_ij V_ik
    tree: mp.mpf = field(init=False)  # Tree_iijk (frozen convention)

    def __post_init__(self):
        ref = _require_strict(self.mu.size, self.i, self.j, self.k)
        if ref is not None:
            raise OracleHardFail(f"refusal in EventContext: {ref}")
        # node-value caches: every outer integral of this event at this
        # precision shares the same quadrature nodes, so r(g) and the
        # expensive nested-quadrature b(g) are evaluated once per node
        self._rc = {}
        self._bc = {}
        with mp.workdps(self.dps):
            mu, C = self.mu, self.C
            i, j, k = self.i, self.j, self.k
            self.sigma_i = mp.sqrt(mp.mpf(C[i, i]))
            self.alpha_i = mp.mpf(mu[i]) / self.sigma_i
            sj = mp.sqrt(mp.mpf(C[j, j]))
            sk = mp.sqrt(mp.mpf(C[k, k]))
            self.m_i = relu_mean_mp(mp.mpf(mu[i]), self.sigma_i)
            self.m_j = relu_mean_mp(mp.mpf(mu[j]), sj)
            self.m_k = relu_mean_mp(mp.mpf(mu[k]), sk)
            self.kj = mp.mpf(C[i, j]) / self.sigma_i
            self.kk = mp.mpf(C[i, k]) / self.sigma_i
            vj = mp.mpf(C[j, j]) - self.kj ** 2
            vk = mp.mpf(C[k, k]) - self.kk ** 2
            if vj <= 0 or vk <= 0:
                raise OracleHardFail("degenerate conditional variance")
            self.svj = mp.sqrt(vj)
            self.svk = mp.sqrt(vk)
            self.crho = (mp.mpf(C[j, k]) - self.kj * self.kk) / (
                self.svj * self.svk)
            # post-ReLU covariances for the Wick terms
            V_ii = relu_second_mp(mp.mpf(mu[i]), self.sigma_i) - self.m_i ** 2
            rho_jk = mp.mpf(C[j, k]) / (sj * sk)
            rho_ij = mp.mpf(C[i, j]) / (self.sigma_i * sj)
            rho_ik = mp.mpf(C[i, k]) / (self.sigma_i * sk)
            V_jk = pospart_product_mp(mu[j], mu[k], sj, sk, rho_jk) \
                - self.m_j * self.m_k
            V_ij = pospart_product_mp(mu[i], mu[j], self.sigma_i, sj, rho_ij) \
                - self.m_i * self.m_j
            V_ik = pospart_product_mp(mu[i], mu[k], self.sigma_i, sk, rho_ik) \
                - self.m_i * self.m_k
            self.wick = V_ii * V_jk + 2 * V_ij * V_ik
            self.tree = mp.mpf(tree_iijk(self.mu, self.C, i, j, k))

    # r(g) = (relu(mu_i + sigma_i g) - m_i)^2
    def r_of(self, g):
        v = self._rc.get(g)
        if v is None:
            x = mp.mpf(self.mu[self.i]) + self.sigma_i * g
            y = x if x > 0 else mp.mpf(0)
            v = (y - self.m_i) ** 2
            self._rc[g] = v
        return v

    # b(g) = E[(Y_j-m_j)(Y_k-m_k) | G=g], centers m_j,m_k unconditional
    def b_of(self, g):
        v = self._bc.get(g)
        if v is None:
            cmj = mp.mpf(self.mu[self.j]) + self.kj * g
            cmk = mp.mpf(self.mu[self.k]) + self.kk * g
            Ejk = pospart_product_mp(cmj, cmk, self.svj, self.svk, self.crho)
            Ej = relu_mean_mp(cmj, self.svj)
            Ek = relu_mean_mp(cmk, self.svk)
            v = Ejk - self.m_j * Ek - self.m_k * Ej + self.m_j * self.m_k
            self._bc[g] = v
        return v


# --------------------------------------------------------------------------
# Tree_iijk -- frozen M122 tree convention continued onto the (i,i,j,k)
# collision (single-entry evaluation of m122.tree_tensor_continuation).
# Per-node quantities come from the frozen m122 module itself; the bridge
# is the exact post-ReLU pair correlation from this oracle's reference.
# --------------------------------------------------------------------------

_TREE_STATE_CACHE: dict = {}


def _tree_state(mu: np.ndarray, C: np.ndarray):
    key = (mu.tobytes(), C.tobytes())
    if key in _TREE_STATE_CACHE:
        return _TREE_STATE_CACHE[key]
    m122 = import_frozen("m122_nonzero_bridge.py")
    n = mu.size
    sigma = np.sqrt(np.diag(C))
    alpha = mu / sigma
    mean1 = np.array([m122.power_hermite_coefficient(a, s, 1, 0)
                      for a, s in zip(alpha, sigma)])
    second = np.array([m122.power_hermite_coefficient(a, s, 2, 0)
                       for a, s in zip(alpha, sigma)])
    var = second - mean1 * mean1
    if np.any(var <= 0):
        raise OracleHardFail("degenerate rectified variance in tree state")
    scale = np.sqrt(var)
    h1 = np.array([m122.power_hermite_coefficient(a, s, 1, 1)
                   for a, s in zip(alpha, sigma)])
    h2 = np.array([m122.power_hermite_coefficient(a, s, 1, 2)
                   for a, s in zip(alpha, sigma)])
    h3 = np.array([m122.power_hermite_coefficient(a, s, 1, 3)
                   for a, s in zip(alpha, sigma)])
    if np.any(np.abs(h1) <= 1e-300):
        raise OracleHardFail("h1 too small for bridge normalization")
    g2 = h2 * scale / (h1 * h1)
    g3 = h3 * scale * scale / (h1 * h1 * h1)
    q = np.eye(n)
    with mp.workdps(40):
        for a in range(n):
            for b in range(a + 1, n):
                rho = C[a, b] / (sigma[a] * sigma[b])
                raw = pospart_product_mp(mu[a], mu[b], sigma[a], sigma[b], rho)
                val = float((raw - mean1[a] * mean1[b]) / (scale[a] * scale[b]))
                if not math.isfinite(val) or abs(val) > 1.0 + 2e-10:
                    raise OracleHardFail("invalid signed pair bridge")
                q[a, b] = q[b, a] = val
    state = (scale, q, g2, g3)
    _TREE_STATE_CACHE[key] = state
    return state


def tree_iijk(mu: np.ndarray, C: np.ndarray, i: int, j: int, k: int) -> float:
    """Single (i,i,j,k) entry of the order-4 M122 tree continuation."""
    import itertools
    scale, q, g2, g3 = _tree_state(np.asarray(mu, float), np.asarray(C, float))
    labels = (i, i, j, k)
    star = math.fsum(
        g3[center] * math.prod(q[center, labels[p]] for p in range(4)
                               if p != cp)
        for cp, center in enumerate(labels))
    path = 0.5 * math.fsum(
        g2[labels[p[1]]] * g2[labels[p[2]]]
        * q[labels[p[0]], labels[p[1]]]
        * q[labels[p[1]], labels[p[2]]]
        * q[labels[p[2]], labels[p[3]]]
        for p in itertools.permutations(range(4)))
    return math.prod(scale[list(labels)]) * (star + path)


# --------------------------------------------------------------------------
# Proposed closed forms, transcribed VERBATIM from the frozen predeclaration
# (sections 4 and 5).  These are the candidate-side hypotheses; the oracle
# computes them so gates 1 and 2 can compare them against direct integration.
# The "actual-M178 arm" evaluates the section-4 jet through the certified
# frozen M178 provider in float64.
# --------------------------------------------------------------------------

def _Phi_f(x):
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def _phi_f(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def R_closed(mu_i: float, sigma_i: float) -> list[float]:
    """Section 5 repeated-node add-backs (proposed closed forms)."""
    alpha = mu_i / sigma_i
    pi = _Phi_f(alpha)
    h = _phi_f(alpha)
    m = sigma_i * (alpha * pi + h)
    s = sigma_i
    return [
        s * s * ((alpha * alpha + 1) * pi + alpha * h) - m * m,
        2 * s * m * (1 - pi),
        2 * s * s * pi - 2 * s * m * h,
        2 * s * s * h + 2 * s * m * alpha * h,
        -2 * s * s * alpha * h - 2 * s * m * (alpha * alpha - 1) * h,
    ]


def beta_closed_m178(mu: np.ndarray, C: np.ndarray,
                     i: int, j: int, k: int) -> list[float]:
    """Section 4 one-jet coefficients via ONE certified M178 call (actual
    arm).  An M178 refusal or any nonfinite output fails closed."""
    ref = _require_strict(mu.size, i, j, k)
    if ref is not None:
        raise OracleHardFail(f"refusal in beta_closed_m178: {ref}")
    m178 = import_frozen("m178_certified_phi2_owent.py")
    sigma_i = math.sqrt(C[i, i])
    sj = math.sqrt(C[j, j])
    sk = math.sqrt(C[k, k])
    a = mu[j] / sj
    b = mu[k] / sk
    rho = C[j, k] / (sj * sk)
    delta = (1 - rho) * (1 + rho)
    p = C[i, j] / (sigma_i * sj)
    q = C[i, k] / (sigma_i * sk)
    res = m178.evaluate(a, b, rho)
    if res.refused or not all(map(math.isfinite,
                                  (res.value, res.d_a, res.d_b, res.d_rho))):
        raise OracleHardFail(f"M178 refusal/nonfinite: {res.reason}")
    P, A, B, D = res.value, res.d_a, res.d_b, res.d_rho
    la = a * _Phi_f(a) + _phi_f(a)
    lb = b * _Phi_f(b) + _phi_f(b)
    H = (a * b + rho) * P + b * A + a * B + delta * D - la * lb
    Ha = b * P + rho * A + B - lb * _Phi_f(a)
    Hb = a * P + A + rho * B - la * _Phi_f(b)
    Haa = (b - rho * a) * A + delta * D - lb * _phi_f(a)
    Hab = P
    Hbb = (a - rho * b) * B + delta * D - la * _phi_f(b)
    Haaa = -(rho + a * (b - rho * a)) * A - a * delta * D + a * lb * _phi_f(a)
    Haab = A
    Habb = B
    Hbbb = -(rho + b * (a - rho * b)) * B - b * delta * D + b * la * _phi_f(b)
    Haaaa = ((a * a * (b - rho * a) - b + 3 * rho * a) * A
             + (delta * a * a + 2 * rho * rho - 1) * D
             + (1 - a * a) * lb * _phi_f(a))
    Haaab = -a * A - rho * D
    Haabb = D
    Habbb = -b * B - rho * D
    Hbbbb = ((b * b * (a - rho * b) - a + 3 * rho * b) * B
             + (delta * b * b + 2 * rho * rho - 1) * D
             + (1 - b * b) * la * _phi_f(b))
    C0 = H
    C1 = p * Ha + q * Hb
    C2 = p * p * Haa + 2 * p * q * Hab + q * q * Hbb
    C3 = (p ** 3 * Haaa + 3 * p * p * q * Haab
          + 3 * p * q * q * Habb + q ** 3 * Hbbb)
    C4 = (p ** 4 * Haaaa + 4 * p ** 3 * q * Haaab + 6 * p * p * q * q * Haabb
          + 4 * p * q ** 3 * Habbb + q ** 4 * Hbbbb)
    return [sj * sk * c / math.factorial(r)
            for r, c in enumerate((C0, C1, C2, C3, C4))]


# --------------------------------------------------------------------------
# Outer oracle: adaptive integration against the standard normal weight,
# split at the ReLU kink(s), run at two precisions with an agreement check.
# Predeclaration says "split at g=-alpha_i"; the antithetic fold also has a
# kink at g=+alpha_i, so both are used as split points (subsumes the literal
# requirement; recorded as an interpretation decision).
# --------------------------------------------------------------------------

def outer_expectation(f, alpha_i, dps: int):
    with mp.workdps(dps):
        aa = abs(mp.mpf(alpha_i))
        pts = [-mp.inf, mp.inf] if aa < mp.mpf("1e-30") \
            else [-mp.inf, -aa, aa, mp.inf]
        return mp.quad(lambda g: f(g) * _phi(g), pts)


def _fold_Z(ctx: EventContext, coeffs, R_add):
    """Section 6 folded event Z_Q(g) with deterministic coefficients."""
    c = [mp.mpf(x) for x in coeffs]
    add = mp.fsum(ci * mp.mpf(Ri) for ci, Ri in zip(c, R_add))
    const = add - ctx.wick - ctx.tree

    def Z(g):
        acc = mp.mpf(0)
        for s in (1, -1):
            gs = s * g
            pc = mp.fsum(ci * HE[r](gs) for r, ci in enumerate(c))
            acc += ctx.r_of(gs) * (ctx.b_of(gs) - pc)
        return mp.mpf("0.5") * acc + const
    return Z


def _raw_Z(ctx: EventContext):
    const = -ctx.wick - ctx.tree
    return lambda g: ctx.r_of(g) * ctx.b_of(g) + const


# --------------------------------------------------------------------------
# Per-event oracle record (both arms) -- the G0B shard unit of work
# --------------------------------------------------------------------------

def _event_quantities(ctx: EventContext, beta_act, R_act) -> dict:
    """Every scalar this oracle reports for one event, computed at the
    context's precision in ONE pass (all integrals share the cached
    r(g)/b(g) node values)."""
    q: dict = {}
    with mp.workdps(ctx.dps):
        E = lambda f: outer_expectation(f, ctx.alpha_i, ctx.dps)
        RH = [E(lambda g, r=r: ctx.r_of(g) * HE[r](g)) for r in range(5)]
        BH = [E(lambda g, r=r: ctx.b_of(g) * HE[r](g)) for r in range(5)]
        beta_idl = [BH[r] / math.factorial(r) for r in range(5)]
        for r in range(5):
            q[f"R_ideal_{r}"] = RH[r]
            q[f"beta_ideal_{r}"] = beta_idl[r]
        q["Erb"] = E(lambda g: ctx.r_of(g) * ctx.b_of(g))
        q["delta"] = q["Erb"] - ctx.wick - ctx.tree
        specs = {
            "ANTI": ([0.0] * 5, [0.0] * 5),
            "Q2_actual": (list(beta_act[:3]) + [0.0, 0.0], R_act),
            "Q4_actual": (list(beta_act), R_act),
            "Q2_ideal": (beta_idl[:3] + [0.0, 0.0], RH),
            "Q4_ideal": (beta_idl, RH),
        }
        for name, (cf, Ra) in specs.items():
            Z = _fold_Z(ctx, cf, Ra)
            q[f"mean_{name}"] = E(Z)
            q[f"second_{name}"] = E(lambda g: Z(g) ** 2)
        Zr = _raw_Z(ctx)
        q["second_RAW1"] = E(lambda g: Zr(g) ** 2)
        q["gh2"] = mp.mpf("0.5") * (Zr(mp.mpf(1)) + Zr(mp.mpf(-1)))
    return q


def R_direct(mu, C, i, j, k, dps_pair=MPMATH_DPS, tol=REFERENCE_SELF_TOL):
    """E[r(G) He_r(G)], r=0..4, by direct two-precision integration."""
    vals = []
    for dps in dps_pair:
        ctx = EventContext(np.asarray(mu, float), np.asarray(C, float),
                           i, j, k, dps)
        with mp.workdps(dps):
            vals.append([outer_expectation(
                lambda g, r=r: ctx.r_of(g) * HE[r](g), ctx.alpha_i, dps)
                for r in range(5)])
    for lo, hi in zip(*vals):
        if abs(lo - hi) > tol * (1 + abs(hi)):
            raise OracleHardFail("two-precision disagreement in R_direct")
    return vals[1]


def beta_direct(mu, C, i, j, k, dps_pair=MPMATH_DPS, tol=REFERENCE_SELF_TOL):
    """E[b(G) He_r(G)]/r!, r=0..4, by direct two-precision integration."""
    vals = []
    for dps in dps_pair:
        ctx = EventContext(np.asarray(mu, float), np.asarray(C, float),
                           i, j, k, dps)
        with mp.workdps(dps):
            vals.append([outer_expectation(
                lambda g, r=r: ctx.b_of(g) * HE[r](g), ctx.alpha_i, dps)
                / math.factorial(r) for r in range(5)])
    for lo, hi in zip(*vals):
        if abs(lo - hi) > tol * (1 + abs(hi)):
            raise OracleHardFail("two-precision disagreement in beta_direct")
    return vals[1]


def oracle_event(mu, C, i, j, k, dps_pair=MPMATH_DPS,
                 tol=REFERENCE_SELF_TOL, tail_check=True) -> dict:
    """Full independent oracle for one strict [2,1,1] event.

    Reports, for the actual-M178 arm (float64 section-4/5 closed forms
    through the certified provider) and the ideal arm (direct-integration
    coefficients): Delta reference, E[Z] bias-contract residuals, and
    conditional variances of RAW1, RAW2, ANTI, Q2, Q4, plus the GH2
    two-call deterministic diagnostic value and bias.  Every reported
    scalar is computed at both frozen precisions and hard-fails on
    disagreement beyond tol*(1+abs(reference)).
    """
    mu = np.asarray(mu, float)
    C = np.asarray(C, float)
    ref = _require_strict(mu.size, i, j, k)
    if ref is not None:
        return {"refusal": ref.__dict__}

    beta_act = beta_closed_m178(mu, C, i, j, k)
    R_act = R_closed(float(mu[i]), math.sqrt(float(C[i, i])))

    ctx_lo = EventContext(mu, C, i, j, k, dps_pair[0])
    ctx_hi = EventContext(mu, C, i, j, k, dps_pair[1])
    q_lo = _event_quantities(ctx_lo, beta_act, R_act)
    q_hi = _event_quantities(ctx_hi, beta_act, R_act)
    for key, hi in q_hi.items():
        lo = q_lo[key]
        if not (mp.isfinite(lo) and mp.isfinite(hi)):
            raise OracleHardFail(f"nonfinite oracle quantity {key}")
        if abs(lo - hi) > tol * (1 + abs(hi)):
            raise OracleHardFail(
                f"two-precision disagreement on {key}: {lo} vs {hi}")

    delta = q_hi["delta"]
    arms = {}
    for name in ("ANTI", "Q2_actual", "Q4_actual", "Q2_ideal", "Q4_ideal"):
        mean = q_hi[f"mean_{name}"]
        var = q_hi[f"second_{name}"] - mean ** 2
        if not mp.isfinite(var) or var < -tol * (1 + abs(q_hi[f"second_{name}"])):
            raise OracleHardFail(f"nonfinite/negative variance for {name}")
        arms[name] = {"mean": float(mean), "var": float(max(var, 0)),
                      "bias_contract_residual": float(mean - delta)}
    raw_var = float(q_hi["second_RAW1"] - delta ** 2)
    arms["RAW1"] = {"mean": float(delta), "var": raw_var,
                    "bias_contract_residual": 0.0}
    # RAW2: mean of two iid raw calls (equal-two-call fair baseline)
    arms["RAW2"] = {"mean": float(delta), "var": raw_var / 2.0,
                    "bias_contract_residual": 0.0}
    # GH2 at nodes +-1: equal-two-call deterministic diagnostic (bias only)
    arms["GH2"] = {"value": float(q_hi["gh2"]),
                   "bias": float(q_hi["gh2"] - delta),
                   "note": "deterministic diagnostic; never an estimator"}

    if tail_check:
        with mp.workdps(dps_pair[0]):
            Z4 = _fold_Z(ctx_lo, list(beta_act), R_act)
            for g in TAIL_G:
                v = Z4(mp.mpf(g))
                if not mp.isfinite(v):
                    raise OracleHardFail(f"nonfinite Z_Q4 at g={g}")

    return {
        "event": [int(i), int(j), int(k)],
        "delta_reference": float(delta),
        "wick": float(ctx_hi.wick),
        "tree_iijk": float(ctx_hi.tree),
        "beta_actual_m178": [float(x) for x in beta_act],
        "beta_ideal": [float(q_hi[f"beta_ideal_{r}"]) for r in range(5)],
        "R_actual": [float(x) for x in R_act],
        "R_ideal": [float(q_hi[f"R_ideal_{r}"]) for r in range(5)],
        "arms": arms,
    }


def g0a_gate_check(record: dict,
                   formula_tol: float = FORMULA_TOL,
                   expectation_tol: float = EXPECTATION_TOL) -> dict:
    """G0A gates 1-3 for one event record: proposed closed forms vs the
    independent direct-integration references, and the bias contract."""
    def close(a, b, tol):
        return abs(a - b) <= tol * (1 + abs(b))
    g1 = all(close(a, b, formula_tol)
             for a, b in zip(record["R_actual"], record["R_ideal"]))
    g2 = all(close(a, b, formula_tol)
             for a, b in zip(record["beta_actual_m178"],
                             record["beta_ideal"]))
    g3 = all(abs(record["arms"][arm]["bias_contract_residual"])
             <= expectation_tol * (1 + abs(record["delta_reference"]))
             for arm in ("ANTI", "Q2_actual", "Q4_actual"))
    return {"gate1_R": g1, "gate2_beta": g2, "gate3_expectation": g3,
            "all": g1 and g2 and g3}


def delta_series_cross_check(mu, C, i, j, k, terms: int = 64) -> float:
    """Second, independent derivation of Delta via the frozen M122
    Hermite-series raw moments (two-signal verification).  Note: the M122
    Gauss-Hermite helper is NOT used here -- tensor GH on the ReLU kink
    converges too slowly to serve as a reference."""
    m122 = import_frozen("m122_nonzero_bridge.py")
    mu = np.asarray(mu, float)
    C = np.asarray(C, float)
    sig = np.sqrt(np.diag(C))
    al = mu / sig
    corr = C / np.outer(sig, sig)
    corr = 0.5 * (corr + corr.T)
    np.fill_diagonal(corr, 1.0)

    def single(a, p):
        return sig[a] ** p * m122.rectified_power_moment(float(al[a]), p)

    def pair(a, pa, b, pb):
        return m122.pair_raw_moment_series(
            float(al[a]), float(sig[a]), pa,
            float(al[b]), float(sig[b]), pb,
            float(corr[a, b]), terms=terms)

    def triple(pi, pj, pk):
        idx = [i, j, k]
        return m122.triple_raw_moment_series(
            al[idx], sig[idx], (pi, pj, pk),
            corr[np.ix_(idx, idx)], terms=terms)

    mi = single(i, 1)
    mj = single(j, 1)
    mk = single(k, 1)
    M4c = (triple(2, 1, 1)
           - mj * pair(i, 2, k, 1) - mk * pair(i, 2, j, 1)
           + mj * mk * single(i, 2)
           - 2 * mi * triple(1, 1, 1)
           + 2 * mi * mj * pair(i, 1, k, 1) + 2 * mi * mk * pair(i, 1, j, 1)
           + mi * mi * pair(j, 1, k, 1)
           - 3 * mi * mi * mj * mk)
    ctx = EventContext(mu, C, i, j, k, 40)
    return float(M4c - ctx.wick - ctx.tree)


# --------------------------------------------------------------------------
# Regeneration from the sampled manifest (G0A and G0B cells) + q_e checks
# --------------------------------------------------------------------------

def _cov2corr(M: np.ndarray) -> np.ndarray:
    d = np.sqrt(np.diag(M))
    if np.any(d <= 0):
        raise OracleHardFail("nonpositive diagonal in corr()")
    return M / np.outer(d, d)


def regenerate_g0a_cell(width: int, seed: int):
    """Section 8 generated cells: exact Philox recipe, order A, d, mu."""
    rng = np.random.Generator(np.random.Philox(seed))
    A = rng.normal(0, 0.12, size=(width, 3))
    d = rng.uniform(0.65, 1.35, size=width)
    Cm = A @ A.T + np.diag(d)
    Cm = 0.5 * (Cm + Cm.T)
    mu = rng.uniform(-0.6, 0.6, size=width)
    return mu, Cm


def g0a_cells() -> dict:
    """All five frozen G0A cells with their frozen events (deduplicated)."""
    cells = {}
    cells["A0"] = (np.array([-0.4, 0.1, 0.7]), np.eye(3), [(0, 1, 2)])
    scale = np.diag([0.7, 1.3, 1.8])
    corr = np.array([[1, .75, -.55], [.75, 1, -.10], [-.55, -.10, 1]])
    cells["A1"] = (np.array([-0.2, 0.45, -0.35]), scale @ corr @ scale,
                   [(0, 1, 2)])
    for width, seed in G0A_GENERATED:
        mu, Cm = regenerate_g0a_cell(width, seed)
        events = []
        for e in ((0, 1, 2), (width - 1, 0, 1)):
            if e not in events:
                events.append(e)
        cells[f"G{width}"] = (mu, Cm, events)
    return cells


def regenerate_g0b_cell(name: str):
    """Section 9 recipe, exact Philox call order.  corr() is read as the
    correlation normalization of the Gram matrix raw @ raw.T (see
    DEVIATIONS)."""
    seed, mix = G0B_CELLS[name]
    rng = np.random.Generator(np.random.Philox(seed))
    raw = rng.normal(size=(G0B_WIDTH, G0B_WIDTH))
    R0 = _cov2corr(raw @ raw.T)
    R = (1 - mix) * np.eye(G0B_WIDTH) + mix * R0
    R = 0.5 * (R + R.T)
    np.fill_diagonal(R, 1.0)
    scale = np.exp(rng.uniform(-0.35, 0.35, size=G0B_WIDTH))
    C = np.diag(scale) @ R @ np.diag(scale)
    C = 0.5 * (C + C.T)
    mu = rng.normal(0, 0.30, size=G0B_WIDTH)
    W = rng.normal(0, 1 / math.sqrt(13), size=(G0B_WIDTH, 13))
    return mu, C, W


def build_bridge(mu: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Exact post-ReLU bridge (signed pair correlation of relu outputs)."""
    _, q, _, _ = _tree_state(np.asarray(mu, float), np.asarray(C, float))
    return q


def build_proposal(mu, C, W):
    m133 = import_frozen("m133_ht_hidden_edge.py")
    q = build_bridge(mu, C)
    return m133.collision211_factored_proposal(
        q, W, uniform_mixture=UNIFORM_MIXTURE)


def draw_events(name: str, proposal) -> np.ndarray:
    seed, _ = G0B_CELLS[name]
    rng = np.random.Generator(np.random.Philox(seed + EVENT_STREAM_OFFSET))
    return proposal.sample(rng, EVENT_DRAWS_PER_CELL)


def q_e_check(proposal, i: int, j: int, k: int) -> float:
    """q_e verification hook: recompute q0(e), hard-fail on zero/nonfinite
    support or a collision (fail closed, section 9)."""
    ref = _require_strict(proposal.width, i, j, k)
    if ref is not None:
        raise OracleHardFail(f"drawn event refused: {ref}")
    q = proposal.probability(i, j, k)
    if not math.isfinite(q) or q <= 0.0:
        raise OracleHardFail(f"q_e check failed for ({i},{j},{k}): q={q}")
    return q


def feature_weight_sq(W: np.ndarray, i: int, j: int, k: int,
                      q_e: float) -> float:
    """||F_e/(2 q_e)||^2 with the complete M151 three-slot feature,
    flattened with all three slots present."""
    m151 = import_frozen("m151_b1_forward_control.py")
    src = m151.source_feature_211(W, i, j, k)
    flat = np.concatenate([np.ravel(src.aaaa), np.ravel(src.aaab),
                           np.ravel(src.aabb)])
    if not np.all(np.isfinite(flat)):
        raise OracleHardFail("nonfinite F_e")
    return float(flat @ flat) / (4.0 * q_e * q_e)


def feature_vector_over_2q(W, i, j, k, q_e) -> np.ndarray:
    m151 = import_frozen("m151_b1_forward_control.py")
    src = m151.source_feature_211(W, i, j, k)
    flat = np.concatenate([np.ravel(src.aaaa), np.ravel(src.aaab),
                           np.ravel(src.aabb)])
    return flat / (2.0 * q_e)


# --------------------------------------------------------------------------
# G0B aggregation + paired bootstrap (used AFTER all four shards finish)
# --------------------------------------------------------------------------

def aggregate_records(records: list[dict], W: np.ndarray,
                      replicates: int = BOOTSTRAP_REPLICATES,
                      seed: int = BOOTSTRAP_SEED) -> dict:
    """N_arm = mean_e[ w_e Var_G(Z_arm|e) ] over the q-sampled events;
    V_Delta = E||X||^2 - ||E X||^2 with X = Delta_e F_e/(2 q_e) (total
    variance of the vector estimate; see DEVIATIONS).  Paired bootstrap:
    one index resample drives every ratio in a replicate."""
    n = len(records)
    w = np.array([r["weight_sq"] for r in records])
    var = {a: np.array([r["arms"][a]["var"] for r in records])
           for a in ("ANTI", "Q2_actual", "Q4_actual")}
    X = np.stack([feature_vector_over_2q(W, *r["event"], r["q_e"])
                  * r["delta_reference"] for r in records])

    def stats(idx):
        N = {a: float(np.mean(w[idx] * var[a][idx])) for a in var}
        Xi = X[idx]
        vd = float(np.mean(np.sum(Xi * Xi, axis=1))
                   - np.sum(np.mean(Xi, axis=0) ** 2))
        contrib_anti = w[idx] * var["ANTI"][idx]
        contrib_q4 = w[idx] * var["Q4_actual"][idx]
        if vd <= 0 or N["ANTI"] <= 0:
            raise OracleHardFail("zero denominator in gate ratio")
        return (N["Q4_actual"] / N["ANTI"], N["Q4_actual"] / vd,
                float(np.percentile(contrib_q4, 99)
                      / np.percentile(contrib_anti, 99)),
                N, vd)

    point = stats(np.arange(n))
    rng = np.random.Generator(np.random.Philox(seed))
    boots = np.empty((replicates, 3))
    for t in range(replicates):
        idx = rng.integers(0, n, size=n)
        boots[t] = stats(idx)[:3]
    upper90 = np.percentile(boots[:, :2], 90, axis=0)
    return {
        "point": {"nq4_nanti": point[0], "nq4_vdelta": point[1],
                  "p99_ratio": point[2], "N": point[3], "V_Delta": point[4]},
        "upper90_nq4_nanti": float(upper90[0]),
        "upper90_nq4_vdelta": float(upper90[1]),
        "p99_ratio_point": point[2],
        "gates": {
            "upper90_nq4_nanti_lt_0.50": bool(upper90[0] < GATE_UPPER90_NQ4_NANTI),
            "upper90_nq4_vdelta_lt_0.20": bool(upper90[1] < GATE_UPPER90_NQ4_VDELTA),
            "p99_ratio_le_1.25": bool(point[2] <= GATE_P99_Q4_ANTI),
        },
    }


# --------------------------------------------------------------------------
# Resource discipline helpers (wall clock + RSS, checked in-loop)
# --------------------------------------------------------------------------

def rss_mib() -> float:
    """Current process resident set size in MiB (Windows via psapi,
    POSIX via /proc; returns nan if neither is available -- the runner
    then reports the memory check as UNAVAILABLE, loudly)."""
    try:
        if sys.platform == "win32":
            import ctypes
            import ctypes.wintypes as wt

            class PMC(ctypes.Structure):
                _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t),
                            ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t),
                            ("PeakPagefileUsage", ctypes.c_size_t)]
            pmc = PMC()
            pmc.cb = ctypes.sizeof(PMC)
            # HANDLE(-1) pseudo-handle: the raw GetCurrentProcess() return
            # is truncated by ctypes' default c_int restype on 64-bit
            ok = ctypes.windll.psapi.GetProcessMemoryInfo(
                wt.HANDLE(-1), ctypes.byref(pmc), pmc.cb)
            if ok:
                return pmc.WorkingSetSize / (1024.0 * 1024.0)
        else:
            with open("/proc/self/statm") as f:
                pages = int(f.read().split()[1])
            return pages * os.sysconf("SC_PAGE_SIZE") / (1024.0 * 1024.0)
    except Exception:
        pass
    return float("nan")
