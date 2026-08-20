"""Static no-go verifier for M176's exact BackgroundArchive prerequisite.

This verifier is deliberately response-free.  It checks the only existing
target-shaped full-covariance producer and the independent M120 reference for
the contract violations recorded in the M176 audit.  It does not instantiate
an MLP, compute an estimator output, or inspect any benchmark data.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(text: str, fragment: str, label: str) -> None:
    if fragment not in text:
        raise AssertionError(f"missing audited evidence for {label}: {fragment!r}")


def main() -> None:
    production = (ROOT / "fullcov_gaussian_mm" / "estimator.py").read_text(encoding="utf-8")
    reference = (
        ROOT / "m120_price_normal_ordered_adjoint" / "m120c_analytic_dense_reference.py"
    ).read_text(encoding="utf-8")
    m125 = (ROOT / "m125_source_batched_forward_tangent" / "m125_forward_tangent.py").read_text(encoding="utf-8")

    # The only FlopScope path is a different, clipped/floored GL10 closure.
    require(production, "def _phi2_gauss10", "fixed GL10 bivariate approximation")
    require(production, "fnp.maximum(fnp.diag(covariance), 1e-24)", "variance floor")
    require(production, "fnp.clip(covariance / sigma_outer", "correlation clip")
    require(production, "return fnp.stack(means, axis=0)", "no covariance archive return")
    if "LocalReluJacobian" in production:
        raise AssertionError("production fullcov unexpectedly exports M125b local Jacobians")

    # M120 contains a useful fail-closed *NumPy* reference, not an installed
    # FlopScope implementation or a certified exact primitive.
    require(reference, "import numpy as np", "ordinary NumPy reference")
    require(reference, "QUADRATURE_TOLERANCE = 1.0e-13", "paired-order indicator")
    require(reference, "if abs(rho) >= 1.0 - ENDPOINT_MARGIN", "endpoint refusal")
    if "import flopscope" in reference:
        raise AssertionError("M120 reference unexpectedly became a FlopScope producer")

    # M125b consumes the five complete Jacobian blocks but intentionally does
    # not construct them; therefore it cannot serve as the producer either.
    require(m125, "class LocalReluJacobian", "M125b consumer contract")
    require(m125, "class TangentState", "M125b tangent consumer contract")
    if "analytic_local_kernels" in m125:
        raise AssertionError("M125b unexpectedly constructs its own background kernels")

    print("M176 static no-go verified: no exact labelled metered BackgroundArchive producer exists")


if __name__ == "__main__":
    main()
