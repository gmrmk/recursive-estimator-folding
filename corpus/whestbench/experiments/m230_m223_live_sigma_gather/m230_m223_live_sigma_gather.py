"""M230 preflight: refuse a gather until M223 exposes a real live sigma vector."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
M223_DIR = HERE.parent / "m223_m179_fused_physical_owner_packet"
if str(M223_DIR) not in sys.path:
    sys.path.insert(0, str(M223_DIR))

import m223_m179_fused_physical_owner_packet as m223  # noqa: E402


MUTATION = "M230"
M224_CODE_SHA256 = "6ABA2D0AB618FF5D678977CC07FC89962C09092B537AAFFC282E069C10DFDA7B"
REQUIRED_FIELD = "marginal_sigma_vector"


class M230IntegrationBlocked(RuntimeError):
    """The source caller does not expose the predeclared live operand."""


def make_generated_m223_context() -> m223.LayerPrecontext:
    """A generated M223-shaped layer used only to inspect its declared ABI."""
    a = np.asarray((0.37, -0.41, 0.19), dtype=np.float64)
    C = np.asarray(
        ((0.64, -0.21, 0.03), (-0.21, 1.69, 0.04), (0.03, 0.04, 0.81)),
        dtype=np.float64,
    )
    return m223.LayerPrecontext(7, 19, a, C, "m230-generated-seam-audit")


def audit_live_m223_sigma_provider(context: m223.LayerPrecontext) -> dict[str, object]:
    """Inspect the live context without deriving or installing a replacement vector."""
    vector = getattr(context, REQUIRED_FIELD, None)
    if not isinstance(vector, np.ndarray):
        return {
            "status": "SEAM_PROTOTYPE_INTEGRATION_BLOCKED",
            "reason": "M223_RETAINED_MARGINAL_SIGMA_VECTOR_ABSENT",
            "layer": context.layer,
            "epoch": context.epoch,
            "context_identity": id(context),
            "context_fields": tuple(sorted(vars(context))),
            "reuse_credit_authorized": False,
            "inclusive_trace_authorized": False,
        }
    return {
        "status": "LIVE_PROVIDER_PRESENT_UNVALIDATED",
        "reason": None,
        "layer": context.layer,
        "epoch": context.epoch,
        "context_identity": id(context),
        "vector_identity": id(vector),
        "reuse_credit_authorized": False,
        "inclusive_trace_authorized": False,
    }


def bind_live_sigma_vector(
    context: m223.LayerPrecontext,
    vector: np.ndarray,
    layer: int,
    epoch: int,
) -> np.ndarray:
    """Future integration guard; current M223 fails at the absent-field seam."""
    audit = audit_live_m223_sigma_provider(context)
    if audit["status"] != "LIVE_PROVIDER_PRESENT_UNVALIDATED":
        raise M230IntegrationBlocked(str(audit["reason"]))
    retained = getattr(context, REQUIRED_FIELD)
    if layer != context.layer or epoch != context.epoch:
        raise M230IntegrationBlocked("M223_LIVE_VECTOR_LAYER_EPOCH_SUBSTITUTION")
    if vector is not retained:
        raise M230IntegrationBlocked("M223_LIVE_VECTOR_COPY_OR_OBJECT_SUBSTITUTION")
    if vector.dtype != np.float64 or vector.ndim != 1 or vector.shape != context.a.shape:
        raise M230IntegrationBlocked("M223_LIVE_VECTOR_SHAPE_OR_DTYPE_SUBSTITUTION")
    expected = np.sqrt(np.diag(context.C))
    if not np.array_equal(vector, expected):
        raise M230IntegrationBlocked("M223_LIVE_VECTOR_CONDITIONAL_OR_VALUE_SUBSTITUTION")
    return vector


__all__ = [
    "M224_CODE_SHA256",
    "M230IntegrationBlocked",
    "REQUIRED_FIELD",
    "audit_live_m223_sigma_provider",
    "bind_live_sigma_vector",
    "make_generated_m223_context",
]
