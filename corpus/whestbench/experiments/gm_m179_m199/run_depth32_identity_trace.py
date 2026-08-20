"""gm_m179_m199 ARM B / ARM C': the 32-layer M179 producer through the frozen
M200 fixture harness, with independent legacy-call and lifetime surveillance.

L = 32 weight matrices per cell => H = 31 archived M179 source layers plus one
terminal layer that emits mu_32.  That is exactly the "32-layer M179 producer"
M199's blocking note said did not exist.

Frozen sources under experiments/m200_streaming_overlap_fixture/,
m179_background_archive_producer/, m198_source211_delay_one_adapter/ are
IMPORTED READ-ONLY.  Nothing there is edited.  Response-free: generated
He-Gaussian weights only.

Usage:  python run_depth32_identity_trace.py --cells 2:0,2:1,3:0 --out arm_b.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for _d in (
    "m125_source_batched_forward_tangent",
    "m167_collision_owner_unification",
    "m172_selective_22_owner_fusion",
    "m178_certified_phi2_owent",
    "m179_background_archive_producer",
    "m198_source211_delay_one_adapter",
    "m200_streaming_overlap_fixture",
):
    p = str(EXPERIMENTS / _d)
    if p not in sys.path:
        sys.path.insert(0, p)

import m200_streaming_overlap as m200            # noqa: E402
import m198_source211_delay_one_adapter as m198  # noqa: E402
import m179_background_producer as m179_producer  # noqa: E402

TOTAL_WEIGHTS = 32          # L: 31 archived source layers + terminal mu_32
SOURCE_LAYERS_H = 31
EXPECTED_COUNTS = {
    "background_steps": 31,
    "source_packets": 31,
    "conversions": 31,
    "injections": 31,
    "transports": 30,
    "terminal_responses": 1,
    "background_rebuilds_inside_stream": 0,
}
PARITY_GATE = 2.0e-12
MU32_GATE = 1.0e-12

ALLOWED_OPERATIONS = {
    "m200.initial_background.mean",
    "m200.initial_background.covariance",
    "m200.borrowed_weight_w_k",
    "m200.borrowed_terminal_weight_w_h_plus_1",
    "m200.terminal_w_h_plus_1_response",
    "m179.exact_step.pre_mean",
    "m179.exact_step.pre_covariance",
    "m179.exact_step.post_mean",
    "m179.exact_step.post_covariance",
    "m179.exact_step.jacobian.probability",
    "m179.exact_step.jacobian.mean_variance_derivative",
    "m179.exact_step.jacobian.price_kernel",
    "m179.exact_step.jacobian.h_mu",
    "m179.exact_step.jacobian.h_variance",
    "m198.context_copy.pre_mean",
    "m198.context_copy.pre_covariance",
    "m198.context_copy.post_mean",
    "m198.delay_one.convert_exact_m179_context_copy",
    "m125b.transport.current_m179_jacobian",
    "m125b.accumulator_after_source_injection",
    "fixture_source_bound_to",
}
# Legacy-family entry points that would mean the old 32-layer background call
# survived rather than being removed.
LEGACY_ENTRY_POINTS = (
    "build_extended_background",
    "build_labelled_carrier_maps",
    "labelled_inhomogeneous_source_recurrence",
)


class LegacyCallCounter:
    """Independent monkeypatch surveillance of the legacy background family."""

    def __init__(self) -> None:
        self.counts = {name: 0 for name in LEGACY_ENTRY_POINTS}
        self._originals = {}

    def install(self) -> None:
        for name in LEGACY_ENTRY_POINTS:
            original = getattr(m198, name)
            self._originals[name] = original

            def wrapper(*args, __name=name, __orig=original, **kwargs):
                self.counts[__name] += 1
                return __orig(*args, **kwargs)

            setattr(m198, name, wrapper)

    def restore(self) -> None:
        for name, original in self._originals.items():
            setattr(m198, name, original)

    def snapshot(self) -> dict:
        return dict(self.counts)


def cell_seed(width: int, replicate: int) -> int:
    """Same shape as m200.frozen_seed; depth field pinned to H = 31."""
    return 200_000_000 + 10_000 * width + 100 * SOURCE_LAYERS_H + replicate


def audit_event_ledger(records) -> dict:
    ops = {}
    bad_lifetime = []
    bad_dtype = []
    for r in records:
        ops[r.operation] = ops.get(r.operation, 0) + 1
        if r.death_order is None or r.death_order <= r.birth_order:
            bad_lifetime.append(r.logical_buffer_id)
        if r.dtype != "float64":
            bad_dtype.append(r.logical_buffer_id)
    unexpected = sorted(set(ops) - ALLOWED_OPERATIONS)
    legacy_named = sorted(
        op for op in ops
        if any(tag in op for tag in ("legacy", "rebuild", "build_extended_background",
                                     "full_archive"))
    )
    terminal = [r for r in records if r.logical_buffer_id == f"l{TOTAL_WEIGHTS}.post_mean"]
    return {
        "operation_histogram": dict(sorted(ops.items())),
        "distinct_operations": len(ops),
        "unexpected_operations": unexpected,
        "legacy_named_operations": legacy_named,
        "buffers_with_surviving_lifetime": bad_lifetime,
        "non_float64_buffers": bad_dtype,
        "m179_exact_step_post_mean_count": ops.get("m179.exact_step.post_mean", 0),
        "terminal_l32_post_mean_present": len(terminal) == 1,
        "terminal_l32_post_mean_digest": terminal[0].digest if terminal else None,
        "terminal_l32_post_mean_shape": list(terminal[0].shape) if terminal else None,
        "terminal_l32_post_mean_dtype": terminal[0].dtype if terminal else None,
        "terminal_l32_post_mean_birth_death": (
            [terminal[0].birth_order, terminal[0].death_order] if terminal else None),
    }


def run_cell(width: int, replicate: int) -> dict:
    t0 = time.perf_counter()
    seed = cell_seed(width, replicate)
    weights = m200.generated_weights(width, TOTAL_WEIGHTS, seed)
    assert len(weights) == TOTAL_WEIGHTS

    counter = LegacyCallCounter()
    counter.install()
    try:
        streamed = m200.run_streaming_overlap(weights, network_seed=seed)
        legacy_during_stream = counter.snapshot()
        t_stream = time.perf_counter() - t0

        t1 = time.perf_counter()
        reference = m200.full_archive_reference(weights, network_seed=seed)
        t_ref = time.perf_counter() - t1
        legacy_after_reference = counter.snapshot()
    finally:
        counter.restore()

    parity = max(
        float(np.max(np.abs(streamed.source_terminal_state.mean
                            - reference.source_terminal_state.mean))),
        float(np.max(np.abs(streamed.source_terminal_state.covariance
                            - reference.source_terminal_state.covariance))),
        float(np.max(np.abs(streamed.terminal_state.mean
                            - reference.terminal_state.mean))),
        float(np.max(np.abs(streamed.terminal_state.covariance
                            - reference.terminal_state.covariance))),
    )

    # Diagnostic only (NOT a gate): the scale the absolute 2e-12 gate sits on.
    ref_scale = max(
        float(np.max(np.abs(reference.source_terminal_state.mean))),
        float(np.max(np.abs(reference.source_terminal_state.covariance))),
        float(np.max(np.abs(reference.terminal_state.mean))),
        float(np.max(np.abs(reference.terminal_state.covariance))),
    )
    relative_parity = parity / ref_scale if ref_scale > 0 else float("inf")

    # --- G8: independent recomputation of mu_32 -----------------------------
    t2 = time.perf_counter()
    states = m179_producer.zero_order_recurrence(weights)
    mu32_independent = states[-1].mu
    t_indep = time.perf_counter() - t2
    indep_digest = m200._array_digest((f"l{TOTAL_WEIGHTS}.post_mean", mu32_independent))

    audit = audit_event_ledger(streamed.event_ledger)
    mu32_bitwise = (audit["terminal_l32_post_mean_digest"] == indep_digest)

    counts = {
        "background_steps": streamed.background_steps,
        "source_packets": streamed.source_packets,
        "conversions": streamed.conversions,
        "injections": streamed.injections,
        "transports": streamed.transports,
        "terminal_responses": streamed.terminal_responses,
        "background_rebuilds_inside_stream": streamed.background_rebuilds_inside_stream,
    }
    liveness = {
        "retained_previous_background": streamed.liveness.retained_previous_background,
        "retained_current_background": streamed.liveness.retained_current_background,
        "retained_tangent": streamed.liveness.retained_tangent,
        "retained_fixture_packet": streamed.liveness.retained_fixture_packet,
        "retained_scratch": streamed.liveness.retained_scratch,
        "retained_full_archive": streamed.liveness.retained_full_archive,
        "retained_dense_rank3": streamed.liveness.retained_dense_rank3,
        "retained_suffix_states": streamed.liveness.retained_suffix_states,
        "max_live_named_objects": streamed.liveness.max_live_named_objects,
    }

    gates = {
        "G1_counts": counts == EXPECTED_COUNTS,
        "G2_liveness": (all(v == 0 for k, v in liveness.items()
                            if k != "max_live_named_objects")
                        and liveness["max_live_named_objects"] <= 5),
        "G3_parity": parity <= PARITY_GATE,
        "G4_impulse_zero": reference.per_layer_impulse_max_abs == 0.0,
        "G5_no_legacy_call": all(v == 0 for v in legacy_during_stream.values()),
        "G6_ledger_clean": (not audit["unexpected_operations"]
                            and not audit["legacy_named_operations"]
                            and not audit["buffers_with_surviving_lifetime"]
                            and not audit["non_float64_buffers"]),
        "G7_terminal_mu32": (audit["terminal_l32_post_mean_present"]
                             and audit["m179_exact_step_post_mean_count"] == TOTAL_WEIGHTS
                             and bool(np.all(np.isfinite(mu32_independent)))
                             and float(np.max(np.abs(mu32_independent))) > 0.0),
        "G8_mu32_identity_bitwise": mu32_bitwise,
    }
    return {
        "cell": {"width": width, "replicate": replicate, "seed": seed,
                 "total_weights_L": TOTAL_WEIGHTS, "source_layers_H": SOURCE_LAYERS_H},
        "counts": counts,
        "liveness": liveness,
        "parity_max_abs": parity,
        "parity_gate": PARITY_GATE,
        "reference_state_max_abs_scale": ref_scale,
        "relative_parity_DIAGNOSTIC_NOT_A_GATE": relative_parity,
        "per_layer_impulse_max_abs": reference.per_layer_impulse_max_abs,
        "legacy_calls_during_measured_stream": legacy_during_stream,
        "legacy_calls_after_reference_construction": legacy_after_reference,
        "event_count": len(streamed.event_ledger),
        "ledger_audit": audit,
        "mu32_independent_digest": indep_digest,
        "mu32_max_abs": float(np.max(np.abs(mu32_independent))),
        "mu32_bitwise_identical_to_streamed_terminal": mu32_bitwise,
        "gates": gates,
        "cell_pass": all(gates.values()),
        "timing_s": {"stream": t_stream, "reference": t_ref,
                     "independent_recurrence": t_indep,
                     "total": time.perf_counter() - t0},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True,
                    help="comma list of width:replicate, e.g. 2:0,2:1,3:0")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = HERE / args.out
    cells = []
    for token in args.cells.split(","):
        w, r = token.split(":")
        cells.append((int(w), int(r)))
    with out.open("a", encoding="utf-8") as handle:
        for width, replicate in cells:
            try:
                record = run_cell(width, replicate)
            except Exception as exc:  # fail-closed observations are DATA
                record = {
                    "cell": {"width": width, "replicate": replicate,
                             "seed": cell_seed(width, replicate),
                             "total_weights_L": TOTAL_WEIGHTS},
                    "cell_pass": False,
                    "exception_type": type(exc).__name__,
                    "exception": str(exc),
                    "traceback": traceback.format_exc()[-2000:],
                }
            handle.write(json.dumps(record) + "\n")
            handle.flush()
            print(json.dumps({
                "width": width, "replicate": replicate,
                "pass": record.get("cell_pass"),
                "parity": record.get("parity_max_abs"),
                "rel_parity": record.get("relative_parity_DIAGNOSTIC_NOT_A_GATE"),
                "scale": record.get("reference_state_max_abs_scale"),
                "impulse": record.get("per_layer_impulse_max_abs"),
                "mu32_bitwise": record.get("mu32_bitwise_identical_to_streamed_terminal"),
                "legacy": record.get("legacy_calls_during_measured_stream"),
                "secs": (record.get("timing_s") or {}).get("total"),
                "exc": record.get("exception_type"),
            }), flush=True)


if __name__ == "__main__":
    main()
