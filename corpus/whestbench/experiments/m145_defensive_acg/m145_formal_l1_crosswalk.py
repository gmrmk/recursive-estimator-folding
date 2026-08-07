"""Hash-bound Formal-L1 integration and protected-cost crosswalk for M145.

This file does not implement or run an efficacy estimator.  It proves that the
frozen M145 sidecar has named insertion points in the immutable Formal-L1
source and computes a conservative delta from native sidecar evidence plus
the exact split Winograd shape identity.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
FORMAL = HERE.parent / "row_blocked_production" / "candidate_source"

FORMAL_HASHES = {
    "estimator.py": "d32de9fb7fa8f953fc873eec91a39e66778215f8607fb03bebbbe1292ca5d432",
    "orthogonal_fold3.py": "24f2eebb1adf37f6be1392de57611c52cbaac7b04e319ff771533da54257796a",
    "fold3_estimator.py": "6952abc0a617e1fb32c64a4483f1539b79933c049f9190984460266bf357e116",
    "row_blocked_winograd.py": "876ac0f042239c88bb48205585d7175da1f956ed0c4b96d8d6f95f5be5ea74b5",
    "cost_model.py": "21b077a7bcdf244b9480e891a8b63ecee05427d2725ea30ef5d2fc016bc03023",
}

REQUIRED_TOKENS = {
    "orthogonal_fold3.py": [
        "n_frames = self.n_base // ctx.width",
        "q, _r = fnp.linalg.qr(raw)",
        "q.reshape((self.n_base, ctx.width)) * mean_radius",
    ],
    "fold3_estimator.py": [
        "first_pre = self._first_sample_matmul(z, mlp.weights[0])",
        "first_moment_residual = fnp.mean(x, axis=0) - exact_first_mean",
        "first_variance_residual = (",
        "sampled_kink = self._weighted_mean(",
        "self._weighted_mean(x, final_weights)",
        "final_mean = final_mean - self.moment_tangent_lambda * delta_mean",
    ],
    "estimator.py": [
        "n_base = 126 * 256",
        "RowBlockedBatchedWinograd(",
        "def _first_sample_matmul",
        "def _sample_matmul",
    ],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_formal_sources() -> dict:
    observed = {name: sha256(FORMAL / name) for name in FORMAL_HASHES}
    hash_pass = observed == FORMAL_HASHES
    missing: dict[str, list[str]] = {}
    for name, tokens in REQUIRED_TOKENS.items():
        source = (FORMAL / name).read_text()
        absent = [token for token in tokens if token not in source]
        if absent:
            missing[name] = absent
    return {
        "formal_source_directory": str(FORMAL),
        "expected_hashes": FORMAL_HASHES,
        "observed_hashes": observed,
        "hash_pass": hash_pass,
        "missing_hook_tokens": missing,
        "hook_pass": not missing,
    }


def direct_bill(m: int, k: int, n: int) -> int:
    return 2 * m * k * n - m * n


def one_level_winograd_bill(m: int, k: int = 256, n: int = 256) -> int:
    """Independently expand the exact Formal-L1 one-level full-width bill."""

    if min(m, k, n) <= 0 or m % 2 or k % 2 or n % 2:
        raise ValueError("the frozen full-width geometry is positive and even")
    hm, hk, hn = m // 2, k // 2, n // 2
    leaves = 7 * direct_bill(hm, hk, hn)
    left_fills = 7 * hm * hk
    right_fills = 7 * hk * hn
    output_adds = 7 * hm * hn
    return leaves + left_fills + right_fills + output_adds


def split_winograd_crosswalk() -> dict:
    first_full = one_level_winograd_bill(32_256)
    first_split = one_level_winograd_bill(1_024) + one_level_winograd_bill(31_232)
    later_full = one_level_winograd_bill(64_512)
    later_split = one_level_winograd_bill(2_048) + one_level_winograd_bill(62_464)
    if first_split - first_full != 114_688 or later_split - later_full != 114_688:
        raise AssertionError("Formal split identity changed")
    # One first hook and 28 ordinary hooks in range(1, depth-3).
    total_delta = (first_split - first_full) + 28 * (later_split - later_full)
    return {
        "first_full": first_full,
        "first_pilot_plus_main": first_split,
        "later_full": later_full,
        "later_pilot_plus_main": later_split,
        "per_hook_split_delta": 114_688,
        "first_hook_count": 1,
        "ordinary_hook_count": 28,
        "total_billed_split_delta": total_delta,
        "extra_matmul_call_upper": 29,
    }


def integration_hooks() -> list[dict]:
    return [
        {
            "source": "orthogonal_fold3.py:setup",
            "formal_owner": "126 setup-time Haar QR frames and E[chi_256] radius",
            "m145_change": "derive disjoint pilot_qr/main_qr children; store the same single 126-frame row bank; no QR in predict",
        },
        {
            "source": "fold3_estimator.py:predict before first_pre",
            "formal_owner": "radialized row directions",
            "m145_change": "evaluate four pilot frames first, freeze active/fold regimes and all-output even-energy proposal, then Householder-tilt 122 stored main frames in place",
        },
        {
            "source": "fold3_estimator.py:first_moment_residual/first_variance_residual",
            "formal_owner": "first-layer moment tangent source",
            "m145_change": "replace the two unweighted sample means with the exact complete-frame coefficient mean; the downstream tangent is linear and unchanged",
        },
        {
            "source": "fold3_estimator.py:_weighted_mean call sites",
            "formal_owner": "kink and on terminal sample means",
            "m145_change": "pass duplicated antipodal line coefficients; dead analytic pieces remain constant because frame coefficients sum to 126",
        },
        {
            "source": "fold3_estimator.py:predict finally",
            "formal_owner": "reusable setup frame bank",
            "m145_change": "apply the same self-inverse reflectors again in a finally block; native restoration defect 8.94e-8",
        },
    ]


def protected_cost_crosswalk() -> dict:
    formal_mean = 189_852_556_000.0
    formal_max = 222_405_357_000.0
    sidecar_billed = 357_099_678.0
    sidecar_residual_s = 0.022555597592145205
    residual_rate = 1.0e11
    split = split_winograd_crosswalk()
    # Six worst-shape added coefficient multiplications: two first-layer
    # residual means and four terminal _weighted_mean paths.  All are f32.
    weighted_mean_upper = 6 * 64_512 * 256
    # The native sidecar already prices 246 Householder matmul calls.  Reserve
    # an additional 50 ms for the 29 pilot/main split calls and adapter control
    # flow until a fully integrated generated runner exists.
    integration_residual_reserve_s = 0.050
    billed_delta = (
        sidecar_billed
        + split["total_billed_split_delta"]
        + weighted_mean_upper
    )
    effective_delta = (
        billed_delta
        + residual_rate * sidecar_residual_s
        + residual_rate * integration_residual_reserve_s
    )
    candidate_mean = formal_mean + effective_delta
    candidate_max = formal_max + effective_delta
    cost_ratio = candidate_mean / formal_mean
    return {
        "formal_mean_effective_compute": formal_mean,
        "formal_max_effective_compute": formal_max,
        "native_sidecar_billed": sidecar_billed,
        "native_sidecar_residual_seconds": sidecar_residual_s,
        "split_winograd_billed_delta": split["total_billed_split_delta"],
        "weighted_mean_billed_upper": weighted_mean_upper,
        "integration_residual_reserve_seconds": integration_residual_reserve_s,
        "protected_billed_delta": billed_delta,
        "protected_effective_delta": effective_delta,
        "projected_mean_effective_compute": candidate_mean,
        "projected_max_effective_compute": candidate_max,
        "mean_cost_ratio": cost_ratio,
        "below_258_4B_safety": candidate_max < 258.4e9,
        "below_272B_cliff": candidate_max < 272.0e9,
        "raw_ratio_required_for_primary_adjusted_ratio_0_8": 0.8 / cost_ratio,
        "adjusted_ratio_if_secondary_raw_ratio_0_75": 0.75 * cost_ratio,
        "memory_crosswalk": {
            "formal_measured_peak_mib": 474.859,
            "frame_bank_is_replacement_not_addition_bytes": 33_030_144,
            "incremental_live_scratch_reserve_mib": 5.0,
            "projected_peak_mib": 479.859,
            "below_512_mib": 479.859 < 512.0,
        },
    }


def full_crosswalk() -> dict:
    return {
        "status": "HASH_BOUND_FORMAL_L1_CROSSWALK_NO_EFFICACY",
        "source_verification": verify_formal_sources(),
        "hooks": integration_hooks(),
        "split_winograd": split_winograd_crosswalk(),
        "cost": protected_cost_crosswalk(),
    }
