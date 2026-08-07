"""M136: clean-room diagram attention residual resummation prototype.

This module deliberately contains no contest networks, scorer, leaderboard,
submission, champion, or public challenge labels.  It only knows how to make
fresh iid-He ReLU networks and use independent Gaussian Monte-Carlo streams
as teachers.  The model is deliberately small: its only fitted parameters are
linear causal-depth coefficients on fixed, equivariant diagram channels.

The channels are *not* claimed to be exact cumulants.  They are a symmetry
preserving feature family that explicitly contains the graph shapes which
blocked M126/M131: ABAB, ABBA, [2,1,1], and a one-delay response.  The point of
this file is to make a falsifiable learned-resummation test, not an assertion
that neural attention creates an analytic identity.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


EPS = 1.0e-12
CHANNELS = ("star_k3", "abab_k4", "abba_k4", "collision_211", "delayed", "edge_attention")
DEPTH_BASIS = 3


def _phi(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * np.asarray(x) ** 2) / math.sqrt(2.0 * math.pi)


def _Phi(x: np.ndarray) -> np.ndarray:
    # NumPy's minimal runtime has no vector erf; dimensions here are tiny.
    return 0.5 * (1.0 + np.vectorize(math.erf)(np.asarray(x) / math.sqrt(2.0)))


def rectified_normal_moments(mu: np.ndarray, std: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mean and second raw moment of ``max(N(mu,std^2),0)``."""
    safe = np.maximum(np.asarray(std), EPS)
    a = np.asarray(mu) / safe
    cdf, pdf = _Phi(a), _phi(a)
    mean = mu * cdf + safe * pdf
    second = (mu * mu + safe * safe) * cdf + mu * safe * pdf
    return mean, second


@dataclass(frozen=True)
class AnalyticState:
    """Diagonal Gaussian state, sufficient to canonicalize positive gauges."""

    means: tuple[np.ndarray, ...]
    variances: tuple[np.ndarray, ...]
    stds: tuple[np.ndarray, ...]
    correlations: tuple[np.ndarray, ...]
    normalized_weights: tuple[np.ndarray, ...]
    anchor: np.ndarray


def diagonal_gaussian_states(weights: Sequence[np.ndarray]) -> AnalyticState:
    """A fixed, deliberately low-order Gaussian anchor.

    It retains every dense signed weight and a generated correlation graph at
    each preactivation, but closes the *activation* covariance diagonally.
    This is a well-defined anchor, not an oracle for a fixed network.
    """
    if not weights:
        raise ValueError("at least one layer is required")
    n0 = np.asarray(weights[0]).shape[1]
    mean = np.zeros(n0, dtype=np.float64)
    variance = np.ones(n0, dtype=np.float64)
    means: list[np.ndarray] = []
    variances: list[np.ndarray] = []
    stds: list[np.ndarray] = []
    correlations: list[np.ndarray] = []
    normalized: list[np.ndarray] = []
    prev_scale = np.sqrt(np.maximum(variance + mean * mean, EPS))
    for w0 in weights:
        w = np.asarray(w0, dtype=np.float64)
        if w.shape[1] != mean.shape[0]:
            raise ValueError("incompatible weight shapes")
        mu = w @ mean
        var = (w * w) @ variance
        std = np.sqrt(np.maximum(var, EPS))
        raw_cov = (w * variance[None, :]) @ w.T
        corr = raw_cov / (std[:, None] * std[None, :])
        corr = 0.5 * (corr + corr.T)
        np.fill_diagonal(corr, 1.0)
        normalized.append(w * prev_scale[None, :] / std[:, None])
        means.append(mu)
        variances.append(var)
        stds.append(std)
        correlations.append(corr)
        mean, second = rectified_normal_moments(mu, std)
        variance = np.maximum(second - mean * mean, EPS)
        prev_scale = np.sqrt(np.maximum(second, EPS))
    anchor, _ = rectified_normal_moments(means[-1], stds[-1])
    return AnalyticState(
        tuple(means), tuple(variances), tuple(stds), tuple(correlations), tuple(normalized), anchor
    )


def _downstream_transport(normalized_weights: Sequence[np.ndarray]) -> tuple[np.ndarray, ...]:
    """Maps layer coordinates (rows) to final preactivation coordinates (cols)."""
    depth = len(normalized_weights)
    out = [None] * depth
    current = np.eye(normalized_weights[-1].shape[0], dtype=np.float64)
    for layer in range(depth - 1, -1, -1):
        out[layer] = current
        # If current maps h_l -> z_final, then W_l.T @ current maps
        # h_(l-1) -> z_final.  The transpose orientation is essential for
        # hidden-permutation equivariance; square widths otherwise hide it.
        current = normalized_weights[layer].T @ current
    return tuple(out)  # type: ignore[return-value]


def _collision211_source(e: np.ndarray) -> np.ndarray:
    """Exact scalar three-vertex [2,1,1] graph contraction.

    For each repeated vertex i this is
    sum_{j,k all distinct from i} (Eij*Eik + Eij*Ejk + Eik*Ejk).
    The closed form is quadratic in E and is used as a source channel only;
    it is not presented as the complete M122 cumulant.
    """
    r = e.sum(axis=1)
    row_square = (e * e).sum(axis=1)
    return r * r + 2.0 * (e @ r) - 3.0 * row_square


def signed_edge_attention(
    source_features: np.ndarray, destination_features: np.ndarray, normalized_weight: np.ndarray
) -> np.ndarray:
    """A parameter-free signed edge-attention primitive.

    ``normalized_weight`` has already quotiented out the positive ReLU gauge.
    Attention weights use content and edge magnitude, while the signed and
    squared signed-weight messages travel in separate channels.  This avoids
    treating a negative MLP weight as an attention probability.  A trainable
    child may replace the fixed identity projections below by shared channel
    maps; permutation equivariance remains because those maps never carry a
    neuron index.
    """
    source = np.asarray(source_features, dtype=np.float64)
    destination = np.asarray(destination_features, dtype=np.float64)
    w = np.asarray(normalized_weight, dtype=np.float64)
    if source.ndim != 2 or destination.ndim != 2 or source.shape[1] != destination.shape[1]:
        raise ValueError("source/destination tokens must have the same feature width")
    if w.shape != (destination.shape[0], source.shape[0]):
        raise ValueError("edge attention weight shape does not match its bipartite tokens")
    score = destination @ source.T / math.sqrt(max(source.shape[1], 1)) + 0.5 * np.log1p(np.abs(w))
    score -= score.max(axis=1, keepdims=True)
    attn = np.exp(score)
    attn /= attn.sum(axis=1, keepdims=True)
    return np.concatenate((attn @ source, (attn * w) @ source, (attn * w * w) @ source), axis=1)


def analytic_node_tokens(state: AnalyticState, layer: int) -> np.ndarray:
    """Gauge-invariant analytic tokens consumed by the edge-attention block."""
    alpha = state.means[layer] / np.maximum(state.stds[layer], EPS)
    return np.stack((alpha, _phi(alpha), -alpha * _phi(alpha)), axis=1)


def diagram_channels(state: AnalyticState) -> np.ndarray:
    """Compile per-output diagram features, shape ``(outputs, depth, 5)``.

    All products act on standardized weights/correlation graphs.  Thus a
    positive hidden-node rescaling cancels before this function, while a node
    permutation merely permutes rows/columns.  The final physical scale is
    restored once, by ``DiagramResummer.predict``.
    """
    depth = len(state.normalized_weights)
    outputs = state.normalized_weights[-1].shape[0]
    channels = np.zeros((outputs, depth, len(CHANNELS)), dtype=np.float64)
    transport = _downstream_transport(state.normalized_weights)
    for layer, (mu, std, corr, v) in enumerate(
        zip(state.means, state.stds, state.correlations, transport)
    ):
        e = corr.copy()
        np.fill_diagonal(e, 0.0)
        alpha = mu / np.maximum(std, EPS)
        # Dimensionless local derivatives.  Their role is a fixed analytic
        # state label, never a learned per-network coefficient.
        gamma2 = _phi(alpha)
        gamma3 = -alpha * _phi(alpha)

        # k3 star source.
        star = v.T @ (gamma3 * (e * e).sum(axis=1))

        # M126-style repeated-output ABAB/ABBA pair tables.  Keeping the full
        # pair construction (then taking the required diagonal) makes the
        # two graph slots explicit rather than smuggling them into a scalar.
        b2 = gamma2[:, None] * v
        b3 = gamma3[:, None] * v
        abab_table = b2.T @ (e @ b2)
        abba_table = b2.T @ (e @ b3)
        abab = np.diag(abab_table)
        abba = np.diag(abba_table)

        # M131/M122 [2,1,1] connected three-vertex source transported to the
        # output.  It retains the hollow collision ownership exactly.
        collision = v.T @ (gamma2 * gamma2 * _collision211_source(e))

        # One delayed covariance-response pass: a source at this layer is
        # transported to output pair space, acted on once, then read out.
        pair_response = b2.T @ (e @ b2)
        delayed = pair_response @ star

        # Actual edge-attention contribution.  Layer zero has no preceding
        # hidden Gaussian state, so its causal slot is exactly zero.  Each
        # later layer receives a signed bipartite message from the previous
        # analytic state and transports its fixed signed channel to output.
        attention = np.zeros(outputs, dtype=np.float64)
        if layer > 0:
            local_attention = signed_edge_attention(
                analytic_node_tokens(state, layer - 1),
                analytic_node_tokens(state, layer),
                state.normalized_weights[layer],
            )
            attention = v.T @ local_attention[:, 3:6].sum(axis=1)
        channels[:, layer, :] = np.stack((star, abab, abba, collision, delayed, attention), axis=1)
    return channels


def causal_feature_matrix(channels: np.ndarray) -> np.ndarray:
    """Fixed three-basis causal depth attention, preserving output order.

    The trainable residual head only chooses a coefficient for each diagram
    channel times each lag basis.  It cannot inspect raw weights directly.
    """
    outputs, depth, nch = channels.shape
    if nch != len(CHANNELS):
        raise ValueError("unexpected channel count")
    out = np.empty((outputs, nch * DEPTH_BASIS), dtype=np.float64)
    lags = (depth - 1 - np.arange(depth)) / max(depth - 1, 1)
    bases = np.stack((np.ones(depth), lags, lags * lags), axis=1)
    for c in range(nch):
        for b in range(DEPTH_BASIS):
            out[:, c * DEPTH_BASIS + b] = channels[:, :, c] @ bases[:, b]
    return out


@dataclass
class DiagramResummer:
    """Regularized causal residual head trained only on generated teachers."""

    ridge: float = 1.0e-3
    use_channels: tuple[int, ...] = tuple(range(len(CHANNELS)))
    feature_mean: np.ndarray | None = None
    feature_scale: np.ndarray | None = None
    beta: np.ndarray | None = None

    def _select(self, x: np.ndarray) -> np.ndarray:
        cols = [c * DEPTH_BASIS + b for c in self.use_channels for b in range(DEPTH_BASIS)]
        return x[:, cols]

    def fit(self, features: Iterable[np.ndarray], residuals: Iterable[np.ndarray]) -> "DiagramResummer":
        x = np.concatenate([self._select(np.asarray(a)) for a in features], axis=0)
        y = np.concatenate([np.asarray(a) for a in residuals], axis=0)
        if x.shape[0] != y.shape[0]:
            raise ValueError("feature/target row mismatch")
        self.feature_mean = x.mean(axis=0)
        self.feature_scale = np.maximum(x.std(axis=0), 1.0e-10)
        z = (x - self.feature_mean) / self.feature_scale
        design = np.column_stack((np.ones(z.shape[0]), z))
        penalty = np.eye(design.shape[1]) * self.ridge
        penalty[0, 0] = 0.0
        self.beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
        return self

    def predict_standardized(self, features: np.ndarray) -> np.ndarray:
        if self.feature_mean is None or self.feature_scale is None or self.beta is None:
            raise RuntimeError("model is not fitted")
        x = self._select(np.asarray(features))
        z = (x - self.feature_mean) / self.feature_scale
        return np.column_stack((np.ones(z.shape[0]), z)) @ self.beta

    def predict(self, weights: Sequence[np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        state = diagonal_gaussian_states(weights)
        features = causal_feature_matrix(diagram_channels(state))
        standardized = self.predict_standardized(features)
        estimate = state.anchor + state.stds[-1] * standardized
        return estimate, state.anchor, features


def iid_he_network(seed: int, width: int = 8, depth: int = 4) -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(seed)
    return tuple(rng.normal(0.0, math.sqrt(2.0 / width), size=(width, width)) for _ in range(depth))


def monte_carlo_teacher(
    weights: Sequence[np.ndarray], samples: int, seed: int, batch_size: int = 4096
) -> tuple[np.ndarray, np.ndarray]:
    """Independent Gaussian MC stream; returns mean and standard error."""
    rng = np.random.default_rng(seed)
    width = np.asarray(weights[0]).shape[1]
    total = np.zeros(np.asarray(weights[-1]).shape[0], dtype=np.float64)
    total_sq = total.copy()
    seen = 0
    while seen < samples:
        take = min(batch_size, samples - seen)
        x = rng.normal(size=(take, width))
        for w in weights:
            x = np.maximum(x @ np.asarray(w).T, 0.0)
        total += x.sum(axis=0)
        total_sq += (x * x).sum(axis=0)
        seen += take
    mean = total / samples
    var = np.maximum(total_sq / samples - mean * mean, 0.0)
    return mean, np.sqrt(var / samples)


def _bootstrap_ratio_ci(anchor: np.ndarray, candidate: np.ndarray, teacher: np.ndarray, draws: int = 20000) -> tuple[float, float, float]:
    """Network-grouped paired MSE ratio with deterministic bootstrap CI."""
    anchor_e = ((anchor - teacher) ** 2).mean(axis=1)
    candidate_e = ((candidate - teacher) ** 2).mean(axis=1)
    ratio = float(candidate_e.mean() / max(anchor_e.mean(), EPS))
    rng = np.random.default_rng(13620260807)
    ids = rng.integers(0, len(anchor_e), size=(draws, len(anchor_e)))
    rs = candidate_e[ids].mean(axis=1) / np.maximum(anchor_e[ids].mean(axis=1), EPS)
    return ratio, float(np.quantile(rs, 0.025)), float(np.quantile(rs, 0.975))


def _independent_teacher(weights: Sequence[np.ndarray], network_seed: int, samples_per_stream: int) -> tuple[np.ndarray, np.ndarray, dict]:
    a, sea = monte_carlo_teacher(weights, samples_per_stream, 1_000_003 + 17 * network_seed)
    b, seb = monte_carlo_teacher(weights, samples_per_stream, 2_000_003 + 17 * network_seed)
    combined = 0.5 * (a + b)
    combined_se = 0.5 * np.sqrt(sea * sea + seb * seb)
    z = np.abs(a - b) / np.maximum(np.sqrt(sea * sea + seb * seb), EPS)
    return combined, combined_se, {"max_stream_z": float(z.max()), "mean_stream_z": float(z.mean())}


def run_cleanroom_prototype(
    width: int = 8,
    depth: int = 4,
    train_networks: int = 24,
    holdout_networks: int = 16,
    samples_per_stream: int = 32768,
) -> dict:
    """One predeclared clean-room gate, with network-grouped holdout seeds.

    No parameter, seed, sample count, or channel family is selected after this
    function returns.  A pass requires the *upper* 95% bootstrap ratio below
    0.5, plus independent-teacher and exact-symmetry gates elsewhere.
    """
    train_seeds = tuple(range(136000, 136000 + train_networks))
    holdout_seeds = tuple(range(137000, 137000 + holdout_networks))

    train_x: list[np.ndarray] = []
    train_y: list[np.ndarray] = []
    teacher_diagnostics: list[dict] = []
    for seed in train_seeds:
        weights = iid_he_network(seed, width, depth)
        state = diagonal_gaussian_states(weights)
        teacher, _se, diag = _independent_teacher(weights, seed, samples_per_stream)
        train_x.append(causal_feature_matrix(diagram_channels(state)))
        train_y.append((teacher - state.anchor) / np.maximum(state.stds[-1], EPS))
        teacher_diagnostics.append(diag)

    full = DiagramResummer(ridge=1.0e-3).fit(train_x, train_y)
    # Matched baseline: same causal basis, same ridge and data; only the k3
    # star is admitted, which corresponds to low-order node messages.
    low = DiagramResummer(ridge=1.0e-3, use_channels=(0,)).fit(train_x, train_y)
    # Negative control: preserve within-network output structure but break the
    # network-to-label association before fitting.  This is intentionally done
    # once with a fixed RNG; it is neither an alternative candidate nor tuned.
    label_rng = np.random.default_rng(136909)
    shuffled_order = label_rng.permutation(len(train_y))
    shuffled = DiagramResummer(ridge=1.0e-3).fit(train_x, [train_y[i] for i in shuffled_order])

    teachers: list[np.ndarray] = []
    anchors: list[np.ndarray] = []
    full_predictions: list[np.ndarray] = []
    low_predictions: list[np.ndarray] = []
    shuffled_predictions: list[np.ndarray] = []
    holdout_se: list[np.ndarray] = []
    for seed in holdout_seeds:
        weights = iid_he_network(seed, width, depth)
        state = diagonal_gaussian_states(weights)
        feature = causal_feature_matrix(diagram_channels(state))
        teacher, se, diag = _independent_teacher(weights, seed, samples_per_stream)
        standardized_full = full.predict_standardized(feature)
        standardized_low = low.predict_standardized(feature)
        standardized_shuffled = shuffled.predict_standardized(feature)
        teachers.append(teacher)
        anchors.append(state.anchor)
        full_predictions.append(state.anchor + state.stds[-1] * standardized_full)
        low_predictions.append(state.anchor + state.stds[-1] * standardized_low)
        shuffled_predictions.append(state.anchor + state.stds[-1] * standardized_shuffled)
        holdout_se.append(se)
        teacher_diagnostics.append(diag)

    teacher_array = np.asarray(teachers)
    anchor_array = np.asarray(anchors)
    full_array = np.asarray(full_predictions)
    low_array = np.asarray(low_predictions)
    shuffled_array = np.asarray(shuffled_predictions)
    full_ratio = _bootstrap_ratio_ci(anchor_array, full_array, teacher_array)
    low_ratio = _bootstrap_ratio_ci(anchor_array, low_array, teacher_array)
    shuffled_ratio = _bootstrap_ratio_ci(anchor_array, shuffled_array, teacher_array)
    anchor_mse = float(((anchor_array - teacher_array) ** 2).mean())
    full_mse = float(((full_array - teacher_array) ** 2).mean())
    low_mse = float(((low_array - teacher_array) ** 2).mean())
    shuffled_mse = float(((shuffled_array - teacher_array) ** 2).mean())
    max_teacher_z = max(item["max_stream_z"] for item in teacher_diagnostics)
    # The z gate catches accidental shared RNG / a broken stream.  It is not
    # an acceptance test for model efficacy: 4 sigma is intentionally lenient.
    teacher_independence_pass = bool(max_teacher_z <= 6.0)
    pass_gate = bool(full_ratio[2] < 0.5 and teacher_independence_pass)
    return {
        "protocol": {
            "cleanroom_only": True,
            "width": width,
            "depth": depth,
            "train_network_seeds": train_seeds,
            "holdout_network_seeds": holdout_seeds,
            "samples_per_independent_stream": samples_per_stream,
            "teacher_streams": 2,
            "ridge": 1.0e-3,
            "promotion_gate": "held_network_bootstrap_upper95_ratio_lt_0.5_and_independent_teacher",
        },
        "heldout": {
            "anchor_mse": anchor_mse,
            "full_mse": full_mse,
            "low_order_mse": low_mse,
            "shuffled_label_mse": shuffled_mse,
            "full_over_anchor_ratio": full_ratio[0],
            "full_over_anchor_ratio_ci95": [full_ratio[1], full_ratio[2]],
            "low_over_anchor_ratio": low_ratio[0],
            "low_over_anchor_ratio_ci95": [low_ratio[1], low_ratio[2]],
            "shuffled_label_over_anchor_ratio": shuffled_ratio[0],
            "shuffled_label_over_anchor_ratio_ci95": [shuffled_ratio[1], shuffled_ratio[2]],
            "shuffled_label_null_rejected": bool(shuffled_ratio[2] >= 0.5),
            "mean_teacher_se": float(np.asarray(holdout_se).mean()),
            "max_teacher_stream_z": max_teacher_z,
            "teacher_independence_pass": teacher_independence_pass,
            "pass_gate": pass_gate,
        },
        "model": {
            "trained_parameters": int(len(full.beta) if full.beta is not None else 0),
            "channels": CHANNELS,
            "causal_depth_basis": DEPTH_BASIS,
            "low_order_parameters": int(len(low.beta) if low.beta is not None else 0),
        },
    }


def transform_hidden_permutation_and_gauge(
    weights: Sequence[np.ndarray], permutations: Sequence[np.ndarray], gauges: Sequence[np.ndarray]
) -> tuple[np.ndarray, ...]:
    """Apply W_l -> D_l P_l W_l P_{l-1}^T D_{l-1}^{-1}.

    ``permutations[l]`` lists old coordinates in each new coordinate order and
    ``gauges[l]`` is positive.  Entries for layer zero are required to cover
    the input coordinates; identity/ones are normally used there.
    """
    if len(permutations) != len(weights) + 1 or len(gauges) != len(weights) + 1:
        raise ValueError("need an input plus one transform per layer")
    transformed = []
    for l, w0 in enumerate(weights, start=1):
        w = np.asarray(w0)
        p, pp = np.asarray(permutations[l]), np.asarray(permutations[l - 1])
        d, dp = np.asarray(gauges[l]), np.asarray(gauges[l - 1])
        transformed.append((d[:, None] * w[p][:, pp]) / dp[None, :])
    return tuple(transformed)


def synthetic_polynomial_dataset(seed: int = 136, count: int = 48, width: int = 6) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact motif-representability task with a matched low-order baseline."""
    rng = np.random.default_rng(seed)
    xs, ys, low_xs = [], [], []
    # This predeclared target has nonzero weights on every hard motif.
    coeff = np.asarray([0.7, -0.5, 0.35, 0.9, -0.2])
    for _ in range(count):
        e = rng.normal(scale=0.16, size=(width, width))
        e = 0.5 * (e + e.T)
        np.fill_diagonal(e, 0.0)
        v = rng.normal(scale=0.4, size=(width, width))
        alpha = rng.normal(scale=0.5, size=width)
        gamma2, gamma3 = _phi(alpha), -alpha * _phi(alpha)
        star = v.T @ (gamma3 * (e * e).sum(axis=1))
        b2, b3 = gamma2[:, None] * v, gamma3[:, None] * v
        abab = np.diag(b2.T @ (e @ b2))
        abba = np.diag(b2.T @ (e @ b3))
        collision = v.T @ (gamma2 * gamma2 * _collision211_source(e))
        delayed = (b2.T @ (e @ b2)) @ star
        full = np.stack((star, abab, abba, collision, delayed), axis=1)
        xs.append(full)
        low_xs.append(full[:, :1])
        ys.append(full @ coeff)
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(low_xs)


def least_squares_mse(x: np.ndarray, y: np.ndarray, ridge: float = 1.0e-12) -> float:
    design = np.column_stack((np.ones(len(x)), x))
    penalty = ridge * np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    return float(np.mean((design @ beta - y) ** 2))


def target_cost_envelope(width: int = 256, depth: int = 32, dtype_multiplier: float = 1.0) -> dict:
    """Conservative target inference arithmetic worksheet, not a score claim."""
    square = 2 * width**3 - width**2
    source_layers = depth - 1
    # Fixed implementation budget: all feature construction is reduced to 24
    # square-equivalent calls/source layer.  This includes diagrams, response,
    # transport, and two signed edge-attention message banks.  Elementwise
    # arrays, reductions, and static model calls are granted a 2B allowance.
    calls_per_source_layer = 24
    raw = source_layers * calls_per_source_layer * square * dtype_multiplier
    protected = 1.25 * raw + 2.0e9 * dtype_multiplier
    parameter_count = 19  # intercept + six channels x three causal bases
    return {
        "width": width,
        "depth": depth,
        "square_matmul_bill": square * dtype_multiplier,
        "source_layers": source_layers,
        "square_equivalent_calls_per_source_layer": calls_per_source_layer,
        "raw_billed_flops": raw,
        "protected_billed_flops_including_2B_nonmatmul_reserve": protected,
        "trained_parameter_count": parameter_count,
        "below_80B": bool(protected < 80.0e9),
        "preconditions": [
            "all 24 calls must be realized without hidden dense pair tensors",
            "float32 parity must be independently demonstrated before using dtype_multiplier=1",
            "no teacher, synthetic corpus, or contest artefact is packaged at inference",
            "runtime wall/allocation audit must be charged separately",
        ],
    }


def main() -> None:
    result = run_cleanroom_prototype()
    result["target_envelope_fp32"] = target_cost_envelope()
    result["target_envelope_fp64"] = target_cost_envelope(dtype_multiplier=2.0)
    here = Path(__file__).resolve().parent
    (here / "M136_RESULTS_20260807.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
