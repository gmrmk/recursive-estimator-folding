"""Frozen generated-only response protocol for M143.

This file is intentionally inert without a separate root authorization JSON.
It contains no challenge loader, scorer, truth, leaderboard, submission, or
champion path.  It compares three exactly unbiased proposals for the same
exhaustive generated M131 ``[2,1,1]`` component:

* ``m133``: the original ``||W_i||`` proposal;
* ``scale_only``: the preserved M139 component ``s_i ||W_i||``;
* ``m143``: ``s_i sqrt(E_i)`` with the sign-scrambled suffix path energy.

The exact sampled coefficient, five-product estimator, one-delay response,
and inhomogeneous carrier are identical in every arm.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for relative in (
    "m120_price_normal_ordered_adjoint",
    "m125_source_batched_forward_tangent",
    "m126_repeated_output_source_contraction",
    "m129_source_frechet_tangent",
    "m131_trivariate_boundary_stream",
    "m133_ht_hidden_edge",
    "m143_output_aware_proposal",
):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m120c_analytic_dense_reference import (  # noqa: E402
    analytic_local_kernels,
    analytic_relu_gaussian_moments,
)
from m125_forward_tangent import LocalReluJacobian, TangentState, tangent_stage  # noqa: E402
from m126_repeated_output_contractions import collision211_repeated_exact  # noqa: E402
from m129_source_frechet import Dual, build_state_frechet  # noqa: E402
from m131_trivariate_boundary_stream import (  # noqa: E402
    conditional_collision211_defect_dot,
    one_delay_edgeworth_source,
)
from m133_ht_hidden_edge import (  # noqa: E402
    collision211_factored_proposal,
    collision211_hh_batched,
)
from m143_output_aware_proposal import (  # noqa: E402
    diagonal_path_energies,
    freeze_factored_proposal,
    make_output_aware_proposal,
    output_aware_node_strength_from_row_energy,
    physical_relu_scale,
    scale_only_node_strength,
)


MANIFEST = HERE / "M143_GENERATED_PREMISE_MANIFEST_20260807.json"
RECEIPT_ROOT = HERE / "authorization_receipts"
MASTER_SEED = 143_000_007
METHOD_CODE = {"m133": 11, "scale_only": 23, "m143": 37}
SPLIT_CODE = {"development": 101, "confirmation": 211}
FAMILY_CODE = {"diagonal": 307, "iid_he": 401}
_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9._-]{16,128}$")

CONFIG: dict[str, Any] = {
    "chain": {
        "depth": 3,
        "covariance_factor_noise": 0.020,
        "covariance_ridge": 0.45,
        "mean_scale": 0.16,
        "weight_diagonal": 0.82,
        "weight_noise": 0.035,
        "families": {
            "diagonal": ".82*I+.035*normal",
            "iid_he": "normal(0,2/width) with no diagonal privilege",
        },
        "generator": "numpy.random.Generator(PCG64DXSM)",
    },
    "sampling": {
        "k_rule": "2*width",
        "uniform_rescue": 0.05,
        "repetitions": 64,
        "common_random_numbers_across_methods": False,
        "q_snapshot": "one deep immutable snapshot per cell/layer/method before coefficient construction",
    },
    "exact_coefficient": {
        "oracle": "M131 conditional_collision211_defect_dot",
        "coarse_order": 32,
        "fine_order": 48,
        "series_terms": 24,
        "max_value_disagreement": 4.0e-5,
    },
    "response": {
        "local": "complete linear M121 one_delay_edgeworth_source for only the [2,1,1] k4 component",
        "carrier": "M125b inhomogeneous coalescing through the frozen generated Gaussian chain",
        "reference": "exhaustive exact local [2,1,1] source at every layer propagated through the same response",
        "target_ready_claim": False,
    },
    "splits": {
        "development": {"widths": [5, 6], "seeds": [143701, 143702]},
        "confirmation": {"widths": [7, 8], "seeds": [143811]},
    },
    "bootstrap": {
        "resamples": 10000,
        "quantile": 0.90,
        "unit": "paired (cell, repetition) response-MSE record",
        "generator": "numpy.random.Generator(PCG64DXSM)",
        "child_key": "[MASTER_SEED,SPLIT_CODE,0xB007]",
    },
    "gates": {
        "primary": {
            "ratio": "M143/M133",
            "pooled_max": 0.75,
            "upper90_max": 0.90,
            "no_adverse_width_trend": True,
        },
        "attribution": {
            "ratio": "M143/scale_only",
            "pooled_max": 0.90,
            "upper90_max": 1.00,
            "no_adverse_width_trend": True,
        },
        "scale_only_vs_m133": "reported diagnostic; never selected or promoted alone",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def child_rng(*key: int) -> np.random.Generator:
    """One explicitly keyed PCG64DXSM child; no mutable parent RNG state."""

    sequence = np.random.SeedSequence([MASTER_SEED, *(int(value) for value in key)])
    return np.random.Generator(np.random.PCG64DXSM(sequence))


def canonical_receipt_path(nonce: str, receipt_root: Path = RECEIPT_ROOT) -> Path:
    if not isinstance(nonce, str) or _TOKEN_PATTERN.fullmatch(nonce) is None:
        raise PermissionError("authorization nonce must be a unique 16-128 character token")
    key = hashlib.sha256(nonce.encode("utf-8")).hexdigest()
    return (receipt_root.resolve() / f"m143-{key}.consumed.json").resolve()


def canonical_authorization_id(nonce: str) -> str:
    """Bind the public authorization identifier one-to-one to its nonce."""

    if not isinstance(nonce, str) or _TOKEN_PATTERN.fullmatch(nonce) is None:
        raise PermissionError("authorization nonce must be a unique 16-128 character token")
    return f"m143-{hashlib.sha256(nonce.encode('utf-8')).hexdigest()}"


def _absolute_bound_path(value: Any, name: str) -> Path:
    if not isinstance(value, str):
        raise PermissionError(f"{name} must be an absolute path string")
    path = Path(value)
    if not path.is_absolute():
        raise PermissionError(f"{name} must be absolute")
    return path.resolve()


def _validate_frozen_execution_artifacts() -> dict[str, Any]:
    manifest_document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    frozen_hashes = manifest_document.get("execution_artifact_hashes", {})
    if not frozen_hashes:
        raise PermissionError("manifest does not yet bind frozen execution artifacts")
    for relative, expected in frozen_hashes.items():
        artifact = (HERE / relative).resolve()
        if not artifact.is_file() or sha256(artifact) != expected:
            raise PermissionError(f"frozen execution artifact mismatch: {relative}")
    return manifest_document


def authorize(
    split: str,
    authorization_path: Path,
    output_path: Path,
    *,
    receipt_root: Path = RECEIPT_ROOT,
) -> dict[str, Any]:
    """Validate one authorization without consuming its atomic nonce receipt."""

    if split not in SPLIT_CODE:
        raise PermissionError("authorization split is invalid")
    if not authorization_path.is_file():
        raise PermissionError("a separate root authorization JSON is required")
    if not output_path.is_absolute():
        raise PermissionError("runner --output must be an absolute path")
    manifest_document = _validate_frozen_execution_artifacts()

    document = json.loads(authorization_path.read_text(encoding="utf-8"))
    manifest_hash = sha256(MANIFEST)
    if document.get("candidate") != "M143" or document.get("manifest_sha256") != manifest_hash:
        raise PermissionError("authorization does not bind the frozen M143 manifest")
    runner_hash = sha256(Path(__file__).resolve())
    if document.get("runner_sha256") != runner_hash:
        raise PermissionError("authorization does not bind the frozen M143 runner")
    if document.get("split") != split:
        raise PermissionError("authorization split does not match the requested split")
    if document.get(f"authorize_{split}") is not True:
        raise PermissionError(f"authorization does not open the {split} split")
    authorization_id = document.get("authorization_id")
    nonce = document.get("nonce")
    if not isinstance(authorization_id, str) or _TOKEN_PATTERN.fullmatch(authorization_id) is None:
        raise PermissionError("authorization_id must be a unique 16-128 character token")
    if not isinstance(nonce, str) or _TOKEN_PATTERN.fullmatch(nonce) is None:
        raise PermissionError("nonce must be a unique 16-128 character token")
    if authorization_id != canonical_authorization_id(nonce):
        raise PermissionError("authorization_id is not canonically bound to its nonce")
    authorized_output = _absolute_bound_path(
        document.get("authorized_output_path"), "authorized_output_path"
    )
    requested_output = output_path.resolve()
    if requested_output != authorized_output:
        raise PermissionError("runner output path differs from the authorization binding")
    if not requested_output.parent.is_dir():
        raise PermissionError("authorized output parent directory does not exist")
    expected_receipt = canonical_receipt_path(nonce, receipt_root)
    bound_receipt = _absolute_bound_path(
        document.get("consumption_receipt_path"), "consumption_receipt_path"
    )
    if bound_receipt != expected_receipt:
        raise PermissionError("authorization receipt path is not canonical for its nonce")

    information: dict[str, Any] = {
        "document": document,
        "authorization_file_path": str(authorization_path.resolve()),
        "authorization_file_sha256": sha256(authorization_path),
        "authorization_id": authorization_id,
        "nonce": nonce,
        "split": split,
        "authorized_output_path": str(authorized_output),
        "consumption_receipt_path": str(expected_receipt),
        "manifest_sha256": manifest_hash,
        "runner_sha256": runner_hash,
    }
    if split == "confirmation":
        information["validated_development"] = validate_development_result(
            document, receipt_root=receipt_root
        )
    information["manifest_status"] = manifest_document.get("status")
    return information


def _authorization_receipt_payload(information: dict[str, Any]) -> bytes:
    return json.dumps(
        {
            "candidate": "M143",
            "authorization_id": information["authorization_id"],
            "nonce": information["nonce"],
            "split": information["split"],
            "authorization_file_path": information["authorization_file_path"],
            "authorization_file_sha256": information["authorization_file_sha256"],
            "manifest_sha256": information["manifest_sha256"],
            "runner_sha256": information["runner_sha256"],
            "authorized_output_path": information["authorized_output_path"],
            "status": "consumed-before-response",
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def consume_authorization(information: dict[str, Any], *, receipt_root: Path = RECEIPT_ROOT) -> str:
    """Atomically consume a nonce before any response construction.

    The exclusive receipt is keyed only by the nonce in one fixed ledger root.
    It remains consumed even if the process later crashes or the authorized
    output is deleted.
    """

    expected = canonical_receipt_path(str(information["nonce"]), receipt_root)
    if expected != Path(str(information["consumption_receipt_path"])).resolve():
        raise PermissionError("authorization information has a noncanonical receipt")
    expected.parent.mkdir(parents=True, exist_ok=True)
    payload = _authorization_receipt_payload(information)
    try:
        descriptor = os.open(str(expected), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise PermissionError("authorization nonce has already been consumed") from exc
    try:
        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0:
                raise OSError("atomic authorization receipt write stalled")
            written += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return hashlib.sha256(payload).hexdigest()


def validate_consumed_authorization_receipt(
    information: dict[str, Any], *, receipt_root: Path = RECEIPT_ROOT
) -> str:
    """Require the exact atomic receipt bytes implied by an authorization."""

    expected_path = canonical_receipt_path(str(information["nonce"]), receipt_root)
    if expected_path != Path(str(information["consumption_receipt_path"])).resolve():
        raise PermissionError("authorization information has a noncanonical receipt")
    if not expected_path.is_file():
        raise PermissionError("authorization has no consumed nonce receipt")
    actual = expected_path.read_bytes()
    expected = _authorization_receipt_payload(information)
    if actual != expected:
        raise PermissionError("authorization receipt payload is incomplete or forged")
    return hashlib.sha256(actual).hexdigest()


def build_generated_chain(width: int, depth: int, cell_seed: int, split: str, family: str):
    if family not in FAMILY_CODE:
        raise ValueError("unknown generated-chain family")
    rng = child_rng(SPLIT_CODE[split], FAMILY_CODE[family], width, cell_seed, 0xBACC)
    factor = np.eye(width) + CONFIG["chain"]["covariance_factor_noise"] * rng.normal(
        size=(width, width)
    )
    covariance = factor @ factor.T + CONFIG["chain"]["covariance_ridge"] * np.eye(width)
    sigma = np.sqrt(np.diag(covariance))
    mean = rng.normal(scale=CONFIG["chain"]["mean_scale"], size=width) * sigma
    if family == "diagonal":
        weights = [
            CONFIG["chain"]["weight_diagonal"] * np.eye(width)
            + rng.normal(scale=CONFIG["chain"]["weight_noise"], size=(width, width))
            for _ in range(depth)
        ]
    else:
        weights = [
            rng.normal(scale=math.sqrt(2.0 / width), size=(width, width))
            for _ in range(depth)
        ]
    states = [(mean, covariance)]
    for weight in weights:
        activation_mean, activation_covariance = analytic_relu_gaussian_moments(
            states[-1][0], states[-1][1]
        )
        next_mean = activation_mean @ weight
        next_covariance = weight.T @ activation_covariance @ weight
        next_covariance = 0.5 * (next_covariance + next_covariance.T)
        states.append((next_mean, next_covariance))
    jacobians = []
    for next_mean, next_covariance in states[1:]:
        kernel = analytic_local_kernels(next_mean, next_covariance)
        jacobians.append(
            LocalReluJacobian(
                kernel.probability,
                kernel.mean_variance_derivative,
                kernel.price_kernel,
                kernel.h_mu,
                kernel.h_variance,
            )
        )
    return states, weights, jacobians


def add_state(left: TangentState, right: TangentState) -> TangentState:
    return TangentState(left.mean + right.mean, left.covariance + right.covariance)


def coalesced_response(
    sources: list[TangentState],
    weights: list[np.ndarray],
    jacobians: list[LocalReluJacobian],
) -> TangentState:
    response = sources[0]
    for index in range(1, len(sources)):
        response = tangent_stage(response, weights[index], jacobians[index])
        response = add_state(response, sources[index])
    return response


def zero_repeated(k4: dict[str, np.ndarray]) -> dict[str, Dual]:
    n = k4["k4_aaaa"].size
    zero_vector = np.zeros(n)
    zero_matrix = np.zeros((n, n))
    return {
        "k3_aaa": Dual(zero_vector.copy(), zero_vector.copy()),
        "k3_aab": Dual(zero_matrix.copy(), zero_matrix.copy()),
        "k4_aaaa": Dual(k4["k4_aaaa"], zero_vector.copy()),
        "k4_aaab": Dual(k4["k4_aaab"], zero_matrix.copy()),
        "k4_aabb": Dual(k4["k4_aabb"], zero_matrix.copy()),
    }


def exact_defect_table(tangent) -> np.ndarray:
    spec = CONFIG["exact_coefficient"]
    n = tangent.state.mean.size
    answer = np.zeros((n, n, n), dtype=np.float64)
    for repeated in range(n):
        for left in range(n):
            for right in range(left + 1, n):
                if len({repeated, left, right}) != 3:
                    continue
                value, _, certificate = conditional_collision211_defect_dot(
                    tangent,
                    repeated,
                    left,
                    right,
                    coarse_order=spec["coarse_order"],
                    fine_order=spec["fine_order"],
                    series_terms=spec["series_terms"],
                )
                if certificate.value_disagreement > spec["max_value_disagreement"]:
                    raise ArithmeticError("M131 paired quadrature failed its frozen certificate")
                answer[repeated, left, right] = value
                answer[repeated, right, left] = value
    return answer


def proposal_digest(proposal) -> str:
    digest = hashlib.sha256()
    for value in (
        proposal.absolute_residual,
        proposal.node_norm,
        proposal.center_a,
        proposal.center_b,
        proposal.center_c,
    ):
        digest.update(np.asarray(value, dtype=np.float64).tobytes(order="C"))
    digest.update(np.asarray(
        [proposal.z_a, proposal.z_b, proposal.z_c, proposal.uniform_mixture],
        dtype=np.float64,
    ).tobytes())
    return digest.hexdigest()


def build_cell(width: int, cell_seed: int, split: str, family: str):
    depth = CONFIG["chain"]["depth"]
    states, weights, jacobians = build_generated_chain(width, depth, cell_seed, split, family)
    tangents = [
        build_state_frechet(mean, covariance, np.zeros(width), np.zeros((width, width)))
        for mean, covariance in states[:-1]
    ]
    for tangent, (mean, covariance) in zip(tangents, states[:-1]):
        physical = physical_relu_scale(mean, np.diag(covariance))
        if not np.allclose(physical, tangent.state.relu_scale, rtol=2e-12, atol=2e-12):
            raise ArithmeticError("source-scale definition disagrees with the frozen M129 state")

    probabilities_after_weight = [jacobian.probability for jacobian in jacobians]
    row_energies = diagonal_path_energies(weights, probabilities_after_weight)

    # All proposal snapshots are complete before any exact coefficient table
    # is opened.  This ordering is part of the anti-adaptation firewall.
    layers: list[dict[str, Any]] = []
    for layer, (tangent, weight) in enumerate(zip(tangents, weights)):
        source_scale = tangent.state.relu_scale
        old = freeze_factored_proposal(
            collision211_factored_proposal(
                tangent.state.bridge, weight, uniform_mixture=CONFIG["sampling"]["uniform_rescue"]
            )
        )
        scale = freeze_factored_proposal(
            make_output_aware_proposal(
                tangent.state.bridge,
                scale_only_node_strength(weight, source_scale),
                uniform_mixture=CONFIG["sampling"]["uniform_rescue"],
            )
        )
        candidate = freeze_factored_proposal(
            make_output_aware_proposal(
                tangent.state.bridge,
                output_aware_node_strength_from_row_energy(source_scale, row_energies[layer]),
                uniform_mixture=CONFIG["sampling"]["uniform_rescue"],
            )
        )
        layers.append(
            {
                "weight": weight,
                "proposals": {"m133": old, "scale_only": scale, "m143": candidate},
                "proposal_sha256": {
                    "m133": proposal_digest(old),
                    "scale_only": proposal_digest(scale),
                    "m143": proposal_digest(candidate),
                },
            }
        )

    exact_sources: list[TangentState] = []
    for layer, tangent in enumerate(tangents):
        defect = exact_defect_table(tangent)
        layers[layer]["defect"] = defect
        exact_k4 = collision211_repeated_exact(defect, weights[layer])
        exact_sources.append(
            one_delay_edgeworth_source(
                zero_repeated(exact_k4), states[layer + 1][0], states[layer + 1][1]
            )
        )
    exact = coalesced_response(exact_sources, weights, jacobians).mean
    return states, weights, jacobians, layers, exact


def sample_cell(
    cell, repetition: int, method: str, split: str, family: str, width: int, cell_seed: int
) -> np.ndarray:
    states, weights, jacobians, layers, _exact = cell
    count = 2 * width
    sources: list[TangentState] = []
    for layer, item in enumerate(layers):
        proposal = item["proposals"][method]
        before = item["proposal_sha256"][method]
        rng = child_rng(
            SPLIT_CODE[split], FAMILY_CODE[family], width, cell_seed,
            METHOD_CODE[method], repetition, layer, 0xD2A
        )
        draws = proposal.sample(rng, count)
        if proposal_digest(proposal) != before:
            raise AssertionError("immutable proposal snapshot changed after sampling")
        defect = item["defect"]
        estimate = collision211_hh_batched(
            item["weight"],
            proposal,
            draws,
            lambda i, j, k: float(defect[i, j, k]),
        )
        sources.append(
            one_delay_edgeworth_source(
                zero_repeated(estimate), states[layer + 1][0], states[layer + 1][1]
            )
        )
    return coalesced_response(sources, weights, jacobians).mean


def bootstrap_upper90(
    numerator: np.ndarray, denominator: np.ndarray, split: str, scope_code: int
) -> float:
    spec = CONFIG["bootstrap"]
    rng = child_rng(SPLIT_CODE[split], 0xB007, scope_code)
    ratios = np.empty(spec["resamples"], dtype=np.float64)
    count = numerator.size
    for index in range(spec["resamples"]):
        choice = rng.integers(0, count, size=count)
        ratios[index] = float(np.mean(numerator[choice])) / float(np.mean(denominator[choice]))
    return float(np.quantile(ratios, spec["quantile"]))


def ratio_summary(
    numerator: np.ndarray,
    denominator: np.ndarray,
    widths: np.ndarray,
    split: str,
    scope_code: int,
) -> dict[str, Any]:
    by_width = {
        str(width): float(np.mean(numerator[widths == width]) / np.mean(denominator[widths == width]))
        for width in sorted(set(int(value) for value in widths))
    }
    return {
        "pooled": float(np.mean(numerator) / np.mean(denominator)),
        "upper90": bootstrap_upper90(numerator, denominator, split, scope_code),
        "by_width": by_width,
        "no_adverse_width_trend": by_width[str(max(map(int, by_width)))] <= by_width[str(min(map(int, by_width)))],
    }


def unavailable_ratio(reason: str) -> dict[str, Any]:
    return {
        "unavailable": True,
        "reason": reason,
        "pooled": None,
        "upper90": None,
        "by_width": {},
        "no_adverse_width_trend": False,
    }


def ratio_passes(value: dict[str, Any], gate: dict[str, Any]) -> bool:
    return bool(
        not value.get("unavailable", False)
        and value["pooled"] <= gate["pooled_max"]
        and value["upper90"] < gate["upper90_max"]
        and value["no_adverse_width_trend"]
    )


def stratified_gate_pass(
    pooled: dict[str, Any],
    by_family: dict[str, dict[str, Any]],
    gate: dict[str, Any],
    *,
    protocol_complete: bool,
) -> bool:
    """Require the frozen threshold conjunction pooled AND in every family."""

    return bool(
        protocol_complete
        and set(by_family) == set(FAMILY_CODE)
        and ratio_passes(pooled, gate)
        and all(ratio_passes(by_family[family], gate) for family in FAMILY_CODE)
    )


def _expected_development_keys() -> set[tuple[str, int, int, int]]:
    specification = CONFIG["splits"]["development"]
    repetitions = int(CONFIG["sampling"]["repetitions"])
    return {
        (family, int(width), int(cell_seed), repetition)
        for family in FAMILY_CODE
        for width in specification["widths"]
        for cell_seed in specification["seeds"]
        for repetition in range(repetitions)
    }


def _validate_complete_development_records(
    result: dict[str, Any],
) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    records = result.get("records")
    if not isinstance(records, list):
        raise PermissionError("development result has no record list")
    expected = _expected_development_keys()
    observed: dict[tuple[str, int, int, int], dict[str, Any]] = {}
    mse_fields = {f"mse_{method}" for method in METHOD_CODE}
    for record in records:
        if not isinstance(record, dict):
            raise PermissionError("development record is not an object")
        try:
            key = (
                str(record["family"]),
                int(record["width"]),
                int(record["cell_seed"]),
                int(record["repetition"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise PermissionError("development record key is malformed") from exc
        if key in observed:
            raise PermissionError("development result contains a duplicate record")
        values = {}
        for field in mse_fields:
            try:
                value = float(record[field])
            except (KeyError, TypeError, ValueError) as exc:
                raise PermissionError("development record is missing a method MSE") from exc
            if not math.isfinite(value) or value < 0.0:
                raise PermissionError("development record MSE is invalid")
            values[field] = value
        observed[key] = values
    if set(observed) != expected:
        raise PermissionError("development records do not exactly cover the frozen protocol")

    ordered_keys = sorted(expected)
    arrays = {
        method: np.asarray([observed[key][f"mse_{method}"] for key in ordered_keys])
        for method in METHOD_CODE
    }
    widths = np.asarray([key[1] for key in ordered_keys], dtype=np.int64)
    families = np.asarray([key[0] for key in ordered_keys])
    return arrays, widths, families


def _validate_complete_development_cells(result: dict[str, Any]) -> None:
    specification = CONFIG["splits"]["development"]
    expected = {
        (family, int(width), int(cell_seed))
        for family in FAMILY_CODE
        for width in specification["widths"]
        for cell_seed in specification["seeds"]
    }
    cells = result.get("cells")
    if not isinstance(cells, list):
        raise PermissionError("development result has no cell list")
    observed = set()
    for cell in cells:
        if not isinstance(cell, dict):
            raise PermissionError("development cell is not an object")
        try:
            key = (str(cell["family"]), int(cell["width"]), int(cell["cell_seed"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise PermissionError("development cell key is malformed") from exc
        if key in observed:
            raise PermissionError("development result contains a duplicate cell")
        observed.add(key)
        snapshots = cell.get("q_snapshot_sha256_by_layer")
        if not isinstance(snapshots, list) or len(snapshots) != CONFIG["chain"]["depth"]:
            raise PermissionError("development cell has incomplete proposal snapshots")
        for layer in snapshots:
            if not isinstance(layer, dict) or set(layer) != set(METHOD_CODE):
                raise PermissionError("development proposal snapshot methods are incomplete")
            if any(
                not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
                for value in layer.values()
            ):
                raise PermissionError("development proposal snapshot hash is malformed")
        means = cell.get("mean_mse")
        if not isinstance(means, dict) or set(means) != set(METHOD_CODE):
            raise PermissionError("development cell method summary is incomplete")
        if any(not math.isfinite(float(value)) or float(value) < 0.0 for value in means.values()):
            raise PermissionError("development cell method summary is invalid")
    if observed != expected:
        raise PermissionError("development cells do not exactly cover both frozen families")


def _recompute_development_gates(
    arrays: dict[str, np.ndarray], widths: np.ndarray, families: np.ndarray
) -> dict[str, Any]:
    primary = ratio_summary(arrays["m143"], arrays["m133"], widths, "development", 1)
    attribution = ratio_summary(
        arrays["m143"], arrays["scale_only"], widths, "development", 2
    )
    scale_diagnostic = ratio_summary(
        arrays["scale_only"], arrays["m133"], widths, "development", 3
    )
    primary_by_family = {
        family: ratio_summary(
            arrays["m143"][families == family],
            arrays["m133"][families == family],
            widths[families == family],
            "development",
            100 + FAMILY_CODE[family],
        )
        for family in FAMILY_CODE
    }
    attribution_by_family = {
        family: ratio_summary(
            arrays["m143"][families == family],
            arrays["scale_only"][families == family],
            widths[families == family],
            "development",
            200 + FAMILY_CODE[family],
        )
        for family in FAMILY_CODE
    }
    primary_pass = stratified_gate_pass(
        primary,
        primary_by_family,
        CONFIG["gates"]["primary"],
        protocol_complete=True,
    )
    attribution_pass = stratified_gate_pass(
        attribution,
        attribution_by_family,
        CONFIG["gates"]["attribution"],
        protocol_complete=True,
    )
    return {
        "ratios": {
            "m143_over_m133_primary": primary,
            "m143_over_m133_primary_by_family": primary_by_family,
            "m143_over_scale_only_attribution": attribution,
            "m143_over_scale_only_attribution_by_family": attribution_by_family,
            "scale_only_over_m133_diagnostic": scale_diagnostic,
        },
        "gate": {
            "primary_pass": bool(primary_pass),
            "attribution_pass": bool(attribution_pass),
            "confirmation_eligible": bool(primary_pass and attribution_pass),
        },
    }


def validate_development_result(
    confirmation_document: dict[str, Any],
    *,
    receipt_root: Path = RECEIPT_ROOT,
) -> dict[str, Any]:
    """Validate and independently recompute the confirmation prerequisite."""

    development_path = _absolute_bound_path(
        confirmation_document.get("development_result_path"), "development_result_path"
    )
    expected_result_hash = confirmation_document.get("development_result_sha256")
    if not isinstance(expected_result_hash, str) or not development_path.is_file():
        raise PermissionError("confirmation lacks its exact development result")
    actual_result_hash = sha256(development_path)
    if actual_result_hash != expected_result_hash:
        raise PermissionError("development result hash differs from confirmation binding")

    development_authorization_path = _absolute_bound_path(
        confirmation_document.get("development_authorization_path"),
        "development_authorization_path",
    )
    expected_authorization_hash = confirmation_document.get("development_authorization_sha256")
    if (
        not isinstance(expected_authorization_hash, str)
        or not development_authorization_path.is_file()
        or sha256(development_authorization_path) != expected_authorization_hash
    ):
        raise PermissionError("confirmation lacks the exact development authorization")
    development_authorization = authorize(
        "development",
        development_authorization_path,
        development_path,
        receipt_root=receipt_root,
    )

    result = json.loads(development_path.read_text(encoding="utf-8"))
    current_manifest = sha256(MANIFEST)
    current_runner = sha256(Path(__file__).resolve())
    if result.get("candidate") != "M143" or result.get("split") != "development":
        raise PermissionError("confirmation prerequisite is not an M143 development result")
    if result.get("manifest_sha256") != current_manifest:
        raise PermissionError("development result binds a stale manifest")
    if result.get("runner_sha256") != current_runner:
        raise PermissionError("development result binds a stale runner")
    if result.get("config") != CONFIG:
        raise PermissionError("development result configuration differs from frozen CONFIG")
    if result.get("protocol_failures") != []:
        raise PermissionError("development result contains protocol failures")

    provenance = result.get("authorization_provenance")
    if not isinstance(provenance, dict):
        raise PermissionError("development result lacks authorization provenance")
    receipt_path = Path(development_authorization["consumption_receipt_path"])
    receipt_hash = validate_consumed_authorization_receipt(
        development_authorization, receipt_root=receipt_root
    )
    expected_provenance = {
        "authorization_file_path": development_authorization["authorization_file_path"],
        "authorization_file_sha256": development_authorization["authorization_file_sha256"],
        "authorization_id": development_authorization["authorization_id"],
        "nonce": development_authorization["nonce"],
        "split": "development",
        "authorized_output_path": str(development_path),
        "consumption_receipt_path": str(receipt_path),
        "consumption_receipt_sha256": receipt_hash,
    }
    if provenance != expected_provenance:
        raise PermissionError("development authorization provenance is incomplete or forged")

    _validate_complete_development_cells(result)
    arrays, widths, families = _validate_complete_development_records(result)
    recomputed = _recompute_development_gates(arrays, widths, families)
    if result.get("ratios") != recomputed["ratios"] or result.get("gate") != recomputed["gate"]:
        raise PermissionError("stored development summaries differ from record recomputation")
    if not recomputed["gate"]["primary_pass"] or not recomputed["gate"]["attribution_pass"]:
        raise PermissionError("independently recomputed development gates do not pass")
    return {
        "development_result_path": str(development_path),
        "development_result_sha256": actual_result_hash,
        "development_authorization_path": str(development_authorization_path),
        "development_authorization_sha256": expected_authorization_hash,
        "recomputed": recomputed,
    }


def run_split(split: str) -> dict[str, Any]:
    specification = CONFIG["splits"][split]
    repetitions = CONFIG["sampling"]["repetitions"]
    records = []
    errors: dict[str, list[float]] = {method: [] for method in METHOD_CODE}
    width_units: list[int] = []
    cells = []
    protocol_failures: list[dict[str, Any]] = []
    family_units: list[str] = []
    for family in FAMILY_CODE:
        for width in specification["widths"]:
            for cell_seed in specification["seeds"]:
                try:
                    cell = build_cell(width, cell_seed, split, family)
                except (ArithmeticError, ValueError) as exc:
                    protocol_failures.append(
                        {
                            "family": family,
                            "width": width,
                            "cell_seed": cell_seed,
                            "failure": f"{type(exc).__name__}: {exc}",
                            "disposition": "fail target extrapolation; no seed retry or family removal",
                        }
                    )
                    continue
                exact = cell[-1]
                method_values = {
                    method: np.asarray(
                        [
                            sample_cell(
                                cell, repetition, method, split, family, width, cell_seed
                            )
                            for repetition in range(repetitions)
                        ]
                    )
                    for method in METHOD_CODE
                }
                method_error = {
                    method: np.mean((values - exact[None, :]) ** 2, axis=1)
                    for method, values in method_values.items()
                }
                for repetition in range(repetitions):
                    records.append(
                        {
                            "width": width,
                            "family": family,
                            "cell_seed": cell_seed,
                            "repetition": repetition,
                            **{
                                f"mse_{method}": float(method_error[method][repetition])
                                for method in METHOD_CODE
                            },
                        }
                    )
                    width_units.append(width)
                    family_units.append(family)
                    for method in METHOD_CODE:
                        errors[method].append(float(method_error[method][repetition]))
                cells.append(
                    {
                        "width": width,
                        "family": family,
                        "cell_seed": cell_seed,
                        "q_snapshot_sha256_by_layer": [
                            item["proposal_sha256"] for item in cell[3]
                        ],
                        "mean_mse": {
                            method: float(np.mean(method_error[method]))
                            for method in METHOD_CODE
                        },
                    }
                )
    arrays = {method: np.asarray(value) for method, value in errors.items()}
    widths = np.asarray(width_units)
    families = np.asarray(family_units)
    if widths.size == 0:
        return {
            "split": split,
            "cells": cells,
            "records": records,
            "protocol_failures": protocol_failures,
            "ratios": {
                "m143_over_m133_primary": unavailable_ratio("no certified generated cells"),
                "m143_over_scale_only_attribution": unavailable_ratio("no certified generated cells"),
                "scale_only_over_m133_diagnostic": unavailable_ratio("no certified generated cells"),
            },
            "gate": {
                "primary_pass": False,
                "attribution_pass": False,
                "confirmation_eligible": False,
            },
        }
    primary = ratio_summary(arrays["m143"], arrays["m133"], widths, split, 1)
    attribution = ratio_summary(arrays["m143"], arrays["scale_only"], widths, split, 2)
    scale_diagnostic = ratio_summary(arrays["scale_only"], arrays["m133"], widths, split, 3)
    primary_by_family = {
        family: (
            ratio_summary(
                arrays["m143"][families == family], arrays["m133"][families == family],
                widths[families == family], split, 100 + FAMILY_CODE[family]
            )
            if np.any(families == family)
            else unavailable_ratio("family has no certified cells")
        )
        for family in FAMILY_CODE
    }
    attribution_by_family = {
        family: (
            ratio_summary(
                arrays["m143"][families == family], arrays["scale_only"][families == family],
                widths[families == family], split, 200 + FAMILY_CODE[family]
            )
            if np.any(families == family)
            else unavailable_ratio("family has no certified cells")
        )
        for family in FAMILY_CODE
    }
    primary_gate = CONFIG["gates"]["primary"]
    attribution_gate = CONFIG["gates"]["attribution"]
    protocol_complete = not protocol_failures
    primary_pass = stratified_gate_pass(
        primary, primary_by_family, primary_gate, protocol_complete=protocol_complete
    )
    attribution_pass = stratified_gate_pass(
        attribution,
        attribution_by_family,
        attribution_gate,
        protocol_complete=protocol_complete,
    )
    return {
        "split": split,
        "cells": cells,
        "records": records,
        "protocol_failures": protocol_failures,
        "ratios": {
            "m143_over_m133_primary": primary,
            "m143_over_m133_primary_by_family": primary_by_family,
            "m143_over_scale_only_attribution": attribution,
            "m143_over_scale_only_attribution_by_family": attribution_by_family,
            "scale_only_over_m133_diagnostic": scale_diagnostic,
        },
        "gate": {
            "primary_pass": bool(primary_pass),
            "attribution_pass": bool(attribution_pass),
            "confirmation_eligible": bool(primary_pass and attribution_pass),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("development", "confirmation"), required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    authorization = authorize(args.split, args.authorization, args.output)
    if args.output.exists():
        raise FileExistsError("refusing to overwrite an existing protocol result")
    receipt_sha256 = consume_authorization(authorization)
    provenance = {
        "authorization_file_path": authorization["authorization_file_path"],
        "authorization_file_sha256": authorization["authorization_file_sha256"],
        "authorization_id": authorization["authorization_id"],
        "nonce": authorization["nonce"],
        "split": authorization["split"],
        "authorized_output_path": authorization["authorized_output_path"],
        "consumption_receipt_path": authorization["consumption_receipt_path"],
        "consumption_receipt_sha256": receipt_sha256,
    }
    result = {
        "candidate": "M143",
        "manifest_sha256": sha256(MANIFEST),
        "runner_sha256": sha256(Path(__file__)),
        "config": CONFIG,
        "authorization_provenance": provenance,
        "firewall": "fresh generated-only exact-[211] response diagnostic; no contest/leaderboard/submission access",
        **run_split(args.split),
    }
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
