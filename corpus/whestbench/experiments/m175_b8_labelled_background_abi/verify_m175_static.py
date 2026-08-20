"""Static no-go verifier for M175's proposed B=8 staging ABI.

This verifier intentionally performs source/AST inspection only.  It does
not import the estimator or a FlopScope runner and opens no response,
competition, or outcome data.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST = HERE / "M175_FROZEN_MANIFEST_20260807.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def function(tree: ast.Module, name: str) -> ast.FunctionDef:
    return next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name
    )


def assert_static_contract() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for relative, expected in manifest["frozen_source_sha256"].items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise AssertionError(f"frozen source changed: {relative}: {actual} != {expected}")

    base = source("base_estimator.py")
    if "def _diagonal_gaussian_pass" not in base or "var = fnp.ones" not in base:
        raise AssertionError("base estimator no longer has the audited diagonal-only pass")
    if "covariance_pre =" in base or "_relu_fullcov" in base:
        raise AssertionError("base estimator unexpectedly acquired a full-covariance archive")

    fullcov = source("fullcov_gaussian_mm/estimator.py")
    fullcov_tree = ast.parse(fullcov, filename="fullcov_gaussian_mm/estimator.py")
    predict = function(fullcov_tree, "predict")
    predict_text = ast.unparse(predict)
    # The only retained history is `means`; the current `covariance` is
    # overwritten each layer.  This is insufficient for a block archive.
    if "means.append(mu)" not in predict_text or "covariances.append" in predict_text:
        raise AssertionError("fullcov state-retention contract changed")
    if "return fnp.stack(means, axis=0)" not in predict_text:
        raise AssertionError("fullcov return surface changed")
    # The existing closure is intentionally a clipped/floored GL10 numerical
    # approximation.  It cannot silently stand in for M125b's exact local
    # Jacobian background.
    for required in (
        "fnp.maximum(fnp.diag(covariance), 1e-24)",
        "fnp.clip(covariance / sigma_outer, -1.0 + 1e-12, 1.0 - 1e-12)",
        "def _phi2_gauss10",
    ):
        if required not in fullcov:
            raise AssertionError(f"fullcov numerical-closure marker disappeared: {required}")

    m125 = source("m125_source_batched_forward_tangent/m125_forward_tangent.py")
    if "import numpy as np" not in m125 or "import flopscope" in m125:
        raise AssertionError("M125b metering boundary changed")
    for required in (
        "class TangentState",
        "class LocalReluJacobian",
        "len(sources) != len(weights) + 1",
        "jacobians: list[LocalReluJacobian]",
    ):
        if required not in m125:
            raise AssertionError(f"M125b ABI marker missing: {required}")

    m156 = source("m156_extended_domain_star_control/m156_extended_domain_star_control.py")
    m163 = source("m163_exterior_collision_null/m163_exterior_collision_null.py")
    for required in (
        "Source211",
        "compile_exterior_star_control",
    ):
        if required not in m163:
            raise AssertionError(f"M163 source-slot surface changed: {required}")
    if "class Source211" not in m156 or "aaaa: Array" not in m156 or "aaab: Array" not in m156 or "aabb: Array" not in m156:
        raise AssertionError("Source211 slot layout changed")
    # A M163 Source211 carries fourth-order contraction slots.  It has neither
    # a post-ReLU mean/covariance tangent nor a Jacobian conversion rule.
    if "TangentState" in m163 or "LocalReluJacobian" in m163:
        raise AssertionError("M163 unexpectedly acquired a tangent conversion ABI")

    m169 = source("m169_m163_call_fusion/m169_fused_compiler.py")
    if "LAYERS = 31" not in m169 or "WIDTH = 256" not in m169:
        raise AssertionError("M169 target shape changed")
    if "all_layer_staging_required" not in m169:
        raise AssertionError("M169 no longer states all-layer staging contract")

    # Fixed response-free liveness arithmetic.  The M169 Workspace stores
    # `3*n + 3*n^2 + 7*B*n^2 + 12*B*n^2 + B*n + 4 + 2*B*n^2` f64 elements.
    n, itemsize, blocks = 256, 8, (8, 8, 8, 7)
    if sum(blocks) != 31 or blocks != (8, 8, 8, 7):
        raise AssertionError("M175 block schedule drifted")
    largest = max(blocks)
    workspace_elements = (
        3 * n + 3 * n * n + 7 * largest * n * n + 12 * largest * n * n
        + largest * n + 4 + 2 * largest * n * n
    )
    workspace_mib = workspace_elements * itemsize / 2**20
    block_v_mib = largest * n * n * itemsize / 2**20
    model_weight_mib = 31 * n * n * 4 / 2**20
    if workspace_mib != 85.52151489257812 or block_v_mib != 4.0 or model_weight_mib != 7.75:
        raise AssertionError("B=8 liveness arithmetic changed")

    return {
        "status": "NO_GO_CURRENT_CODE_EXACT_LABELLED_PRODUCER_ABSENT",
        "first_broken_link": "no exact, labelled, metered full-covariance/Jacobian producer for BackgroundArchive",
        "secondary_broken_link": "no M163 Source211-to-M125b TangentState conversion ownership or formula",
        "fixed_blocks": list(blocks),
        "largest_m169_workspace_mib": workspace_mib,
        "block_covariance_archive_mib": block_v_mib,
        "raw_f32_weight_archive_mib": model_weight_mib,
        "resource_certificate": False,
        "integration_runner_created": False,
    }


def main() -> None:
    print(json.dumps(assert_static_contract(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
