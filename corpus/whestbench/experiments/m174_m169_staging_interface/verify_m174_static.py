"""Static, response-free verifier for M174's M169 staging-interface audit.

It reads source text/AST and the frozen manifest.  It deliberately does not
import an estimator, FlopScope, benchmark, scorer, or any runner.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST = HERE / "M174_FROZEN_MANIFEST_20260807.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def module(path: str) -> ast.Module:
    return ast.parse(source(path), filename=path)


def names_in_function(tree: ast.Module, name: str) -> set[str]:
    function = next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name
    )
    return {node.id for node in ast.walk(function) if isinstance(node, ast.Name)}


def assert_static_contract() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = manifest["frozen_source_sha256"]
    for relative, expected in files.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise AssertionError(f"frozen input changed: {relative}: {actual} != {expected}")
    cost_root = ROOT.parent / "whest-v014" / "Lib" / "site-packages" / "flopscope"
    for relative, expected in manifest["frozen_installed_cost_source_sha256"].items():
        actual = sha256(cost_root / relative.removeprefix("flopscope/"))
        if actual != expected:
            raise AssertionError(f"frozen cost source changed: {relative}: {actual} != {expected}")

    base = source("base_estimator.py")
    if "def _diagonal_gaussian_pass" not in base or "var = fnp.ones" not in base:
        raise AssertionError("base no longer exposes the audited diagonal-only background")
    if "covariance_pre =" in base or "_relu_fullcov" in base:
        raise AssertionError("base unexpectedly acquired a full covariance ABI")

    fullcov_tree = module("fullcov_gaussian_mm/estimator.py")
    predict_names = names_in_function(fullcov_tree, "predict")
    if not {"mu", "covariance", "means"}.issubset(predict_names):
        raise AssertionError("fullcov sequential state shape changed")
    returns = [node for node in ast.walk(fullcov_tree) if isinstance(node, ast.Return)]
    if not any("fnp.stack(means" in ast.unparse(node.value) for node in returns if node.value):
        raise AssertionError("fullcov no longer returns only stacked means")

    m125 = source("m125_source_batched_forward_tangent/m125_forward_tangent.py")
    if "import numpy as np" not in m125 or "import flopscope" in m125:
        raise AssertionError("M125 carrier accounting boundary changed")
    if "len(sources) != len(weights) + 1" not in m125:
        raise AssertionError("M125 list-only chain contract changed")
    if "layer" in m125.split("def _validate_chain", 1)[1].split("def explicit", 1)[0]:
        raise AssertionError("M125 unexpectedly acquired layer-label validation")

    m122 = source("m122_nonzero_bridge_theory/m122_nonzero_bridge.py")
    if "mean.size > 8" not in m122:
        raise AssertionError("M122 target-width restriction changed")

    m129 = source("m129_source_frechet_tangent/m129_source_frechet.py")
    if "deliberately a small-width" not in m129 or "algebra oracle" not in m129:
        raise AssertionError("M129 reference-only scope changed")

    m169_tree = module("m169_m163_call_fusion/m169_fused_compiler.py")
    m169 = source("m169_m163_call_fusion/m169_fused_compiler.py")
    if "LAYERS = 31" not in m169 or "WIDTH = 256" not in m169:
        raise AssertionError("M169 target shape changed")
    if "fnp.stack(weights, axis=0, out=staged.weight)" not in m169:
        raise AssertionError("M169 no longer charges weight staging")
    if "fnp.stack(covariances, axis=0, out=staged.covariance)" not in m169:
        raise AssertionError("M169 no longer charges covariance staging")
    staged = next(node for node in m169_tree.body if isinstance(node, ast.ClassDef) and node.name == "StagedInputs")
    annotations = [node.target.id for node in staged.body if isinstance(node, ast.AnnAssign)]
    if annotations != ["weight", "covariance"]:
        raise AssertionError("M169 staged ABI unexpectedly contains labels/provenance")
    if "fnp.matmul(edge, w, out=x.z)" not in m169 or "fnp.matmul(x.lhs, x.rhs, out=x.product)" not in m169:
        raise AssertionError("M169 two-call compiler surface changed")

    runner = source("m169_m163_call_fusion/run_m169_native_trace.py")
    if "def generated_inputs" not in runner or "rng.standard_normal" not in runner:
        raise AssertionError("M169 trace is no longer generated-input-only")
    if "whestbench" in runner or "BaseEstimator" in runner:
        raise AssertionError("M169 trace unexpectedly acquired a production caller")

    # Float64 staging is exactly two billed units per element.  The compiler
    # itself owns 42,869,252 f64 elements; its own trace excludes caller-owned
    # raw inputs.  These are algebraic/liveness calculations, not a run.
    n, layers, itemsize = 256, 31, 8
    plane = n * n
    persistent_elements = (
        3 * n
        + 3 * plane
        + 7 * layers * plane
        + 12 * layers * plane
        + layers * n
        + 4
        + 2 * layers * plane
    )
    if persistent_elements != 42_869_252:
        raise AssertionError(f"unexpected M169 persistent elements: {persistent_elements}")
    fused_mib = persistent_elements * itemsize / 2**20
    if fused_mib != 327.0664367675781:
        raise AssertionError(f"unexpected M169 persistent MiB: {fused_mib}")

    per_stack_f64_bill = 2 * layers * plane
    extra_packing_bill = 2 * per_stack_f64_bill + 4 * per_stack_f64_bill + 2 * per_stack_f64_bill
    if extra_packing_bill != 32_505_856:
        raise AssertionError(f"unexpected M169 packing bill: {extra_packing_bill}")

    # Fixed B=8 alternative.  It retains only a current 8-layer V block, has
    # four blocks (8,8,8,7), and therefore eight batch-matmul dispatches.  The
    # total packed element count is unchanged, but the retained fused workspace
    # is 85.52151489257812 MiB for the largest block.
    block = 8
    block_elements = 3 * n + 3 * plane + 7 * block * plane + 12 * block * plane + block * n + 4 + 2 * block * plane
    block_mib = block_elements * itemsize / 2**20
    if block_mib != 85.52151489257812:
        raise AssertionError(f"unexpected B=8 workspace MiB: {block_mib}")

    return {
        "status": "STATIC_PASS_VERDICT_REPAIR",
        "m169_persistent_elements": persistent_elements,
        "m169_persistent_mib": fused_mib,
        "m169_explicit_packing_bill": extra_packing_bill,
        "b8_workspace_mib": block_mib,
        "b8_blocks": [8, 8, 8, 7],
        "b8_batch_matmul_dispatches": 8,
    }


def main() -> None:
    print(json.dumps(assert_static_contract(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
