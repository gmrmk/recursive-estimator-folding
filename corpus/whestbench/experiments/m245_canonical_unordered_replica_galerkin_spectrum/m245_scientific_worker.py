"""M245 scientific worker and sole instrumented quadrature gateway.

The entry point is reachable only through the hash-bound intent and READY/GO
barrier.  It owns the sole ``mp.quad`` call site, binds authoritative
event-local cache scopes, records every request losslessly, and injects itself
into both independent scientific cores.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import types
from typing import Any, Callable


# These names are deliberately populated only after the intent and READY/GO
# barrier have been verified.  The imports remain lexically visible for the
# frozen static firewall, while importing this worker module itself is still a
# stdlib-only operation.
mp: Any = None
m245_primary_core: Any = None
m245_replica_core: Any = None


_ERROR_SEMANTICS = "heuristic_diagnostic_estimate_not_interval_certificate"
_BASE_PYTHON = r"C:\Python314\python.exe"
_VENV_PYTHON = r"C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe"
_QUAD_ROLES = {
    "outer_top_level",
    "nested_plackett",
    "nested_unary",
    "direct_analytic_gate",
    "direct_residual_gate",
    "direct_beta_residual_gate",
}


class M245ScientificWorkerError(Exception):
    """The scientific worker or quadrature gateway violated its contract."""


def _load_scientific_modules() -> tuple[Any, Any, Any]:
    """Install only the two frozen absolute import roots after READY/GO."""

    global mp, m245_primary_core, m245_replica_core
    if mp is None:
        authority_directory = Path(__file__).resolve().parent
        site_packages = Path(sys.executable).resolve().parent.parent / "Lib" / "site-packages"
        for path, label in (
            (authority_directory, "authority module directory"),
            (site_packages, "frozen venv site-packages"),
        ):
            try:
                identity = os.lstat(path)
            except OSError as exc:
                raise M245ScientificWorkerError(f"cannot lstat {label}: {exc}") from exc
            if (
                not stat.S_ISDIR(identity.st_mode)
                or getattr(identity, "st_file_attributes", 0) & 0x400
            ):
                raise M245ScientificWorkerError(
                    f"{label} is not a regular non-reparse directory"
                )
        required_hashes = {
            "m245_primary_core": os.environ.get("M245_PRIMARY_SOURCE_SHA256"),
            "m245_replica_core": os.environ.get("M245_REPLICA_SOURCE_SHA256"),
        }
        worker_expected = os.environ.get("M245_WORKER_SOURCE_SHA256")
        worker_raw = _secure_regular_bytes(Path(__file__).resolve())
        if (
            worker_expected is None
            or hashlib.sha256(worker_raw).hexdigest() != worker_expected
        ):
            raise M245ScientificWorkerError("executed worker source is not trigger-bound")
        # -P/-S remove ambient project/site injection. W adds only the frozen
        # venv root, then executes retained, hash-verified P/R source bytes.
        sys.path.insert(0, str(site_packages))
        import mpmath as loaded_mp

        def _load_retained_source(name: str) -> Any:
            expected = required_hashes[name]
            if (
                not isinstance(expected, str)
                or len(expected) != 64
                or any(character not in "0123456789abcdef" for character in expected)
            ):
                raise M245ScientificWorkerError(f"{name} source hash context is malformed")
            source_path = authority_directory / f"{name}.py"
            raw = _secure_regular_bytes(source_path)
            if hashlib.sha256(raw).hexdigest() != expected:
                raise M245ScientificWorkerError(f"{name} retained source hash drift")
            spec = importlib.util.spec_from_loader(
                name, loader=None, origin=str(source_path)
            )
            if spec is None:
                raise M245ScientificWorkerError(f"cannot create exact {name} module spec")
            module = types.ModuleType(name)
            module.__file__ = str(source_path)
            module.__loader__ = None
            module.__package__ = ""
            module.__spec__ = spec
            code = compile(raw, str(source_path), "exec", dont_inherit=True)
            prior = sys.modules.get(name)
            sys.modules[name] = module
            try:
                exec(code, module.__dict__)
            except BaseException:
                if prior is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = prior
                raise
            if (
                hashlib.sha256(_secure_regular_bytes(source_path)).hexdigest()
                != expected
            ):
                raise M245ScientificWorkerError(f"{name} changed after retained execution")
            return module

        # Lexical imports remain for the frozen static firewall only. Runtime
        # science is the exact retained-byte execution above.
        if False:  # pragma: no cover - static import contract only
            import m245_primary_core as _static_primary
            import m245_replica_core as _static_replica
        loaded_primary = _load_retained_source("m245_primary_core")
        loaded_replica = _load_retained_source("m245_replica_core")

        mp = loaded_mp
        m245_primary_core = loaded_primary
        m245_replica_core = loaded_replica
    return mp, m245_primary_core, m245_replica_core


def _canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _sha256(payload: object) -> str:
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def _mpf_tuple(value: Any) -> dict[str, Any]:
    converted = mp.mpf(value)
    sign, mantissa, exponent, bitcount = converted._mpf_
    return {
        "bitcount": int(bitcount),
        "exponent": int(exponent),
        "mantissa": str(int(mantissa)),
        "sign": int(sign),
    }


def _mpf_tuple_fraction(row: dict[str, Any]) -> Fraction:
    mantissa = int(row["mantissa"])
    exponent = int(row["exponent"])
    magnitude = (
        Fraction(mantissa << exponent, 1)
        if exponent >= 0 else Fraction(mantissa, 1 << -exponent)
    )
    return -magnitude if row["sign"] else magnitude


def _fraction_mpf_tuple(value: Fraction) -> dict[str, Any]:
    if value == 0:
        return {"bitcount": 0, "exponent": 0, "mantissa": "0", "sign": 0}
    sign = 1 if value < 0 else 0
    numerator = abs(value.numerator)
    denominator = value.denominator
    if denominator & (denominator - 1):
        raise M245ScientificWorkerError("quadrature error sum is not dyadic")
    exponent = -(denominator.bit_length() - 1)
    while numerator % 2 == 0:
        numerator //= 2
        exponent += 1
    return {
        "bitcount": numerator.bit_length(), "exponent": exponent,
        "mantissa": str(numerator), "sign": sign,
    }


def _finite(value: Any) -> bool:
    try:
        return bool(mp.isfinite(value))
    except (TypeError, ValueError):
        return False


def _endpoint(value: Any) -> dict[str, Any]:
    converted = mp.mpf(value)
    if mp.isinf(converted):
        return {"kind": "+inf" if converted > 0 else "-inf", "mpf": None}
    return {"kind": "finite", "mpf": _mpf_tuple(converted)}


def _json_panel_path(value: Any) -> list[Any]:
    if isinstance(value, (list, tuple)):
        result: list[Any] = []
        for item in value:
            if isinstance(item, (list, tuple)):
                result.append(_json_panel_path(item))
            elif isinstance(item, (str, int, bool)) or item is None:
                result.append(item)
            else:
                result.append(str(item))
        return result
    return [value if isinstance(value, (str, int, bool)) or value is None else str(value)]


def _instrumented_quad(
    integrand: Callable[..., Any],
    interval: Any,
) -> tuple[Any, Any]:
    """The only project call site permitted to invoke mpmath quadrature."""

    return mp.quad(
        integrand,
        interval,
        method="tanh-sinh",
        maxdegree=14,
        error=True,
    )


class QuadGateway:
    """Event-local, precision-local, losslessly metered quadrature gateway."""

    def __init__(self, *, shard_id: int, invocation_index: int, event_id: str) -> None:
        if type(shard_id) is not int or shard_id not in range(4):
            raise M245ScientificWorkerError("invalid shard context")
        if type(invocation_index) is not int or invocation_index not in (1, 2):
            raise M245ScientificWorkerError("invalid invocation context")
        if not isinstance(event_id, str) or not event_id:
            raise M245ScientificWorkerError("invalid event context")
        self.shard_id = shard_id
        self.invocation_index = invocation_index
        self.event_id = event_id
        self.ledger: list[dict[str, Any]] = []
        self._active_requests: list[int] = []
        self._completion_count = 0
        # The callable itself, not its integer id, is retained in every cache
        # key.  This prevents CPython id reuse from aliasing a later integral.
        # Unhashable callables simply bypass caching.
        self._cache: dict[tuple[Any, ...], tuple[Any, Any]] = {}
        self._outer_error_sums: dict[str, Fraction] = {}

    @property
    def current_request_index(self) -> int | None:
        """Read-only request index used by replica nested-call attribution."""

        return self._active_requests[-1] if self._active_requests else None

    def authoritative_scope(self, engine: str, precision_dps: int) -> str:
        if engine not in ("primary", "replica") or precision_dps not in (80, 100):
            raise M245ScientificWorkerError("quadrature engine or precision drift")
        return (
            f"S{self.shard_id}:I{self.invocation_index}:{self.event_id}:"
            f"{engine}:{precision_dps}:fresh"
        )

    def record_cache_hit(
        self,
        *,
        integrand: Callable[..., Any],
        interval: Any,
        engine: str,
        precision_dps: int,
        cache_scope_id: str,
        quantity: str,
        call_role: str,
        panel_path: Any,
        parent_request_index: int | None = None,
    ) -> tuple[Any, Any]:
        """Record only a hit proven against W's retained callable cache."""

        scope = self.authoritative_scope(engine, precision_dps)
        if call_role not in _QUAD_ROLES or not isinstance(quantity, str) or not quantity:
            raise M245ScientificWorkerError("cache-hit request metadata is malformed")
        values = list(interval)
        if len(values) < 2:
            raise M245ScientificWorkerError("cache-hit interval has fewer than two endpoints")
        inferred_parent = self.current_request_index
        if inferred_parent is None and parent_request_index is not None:
            raise M245ScientificWorkerError("cache-hit parent supplied without an active request")
        if parent_request_index is not None and parent_request_index != inferred_parent:
            raise M245ScientificWorkerError("cache-hit parent conflicts with active request")
        parent = inferred_parent
        effective_role = call_role
        if parent is not None and call_role == "outer_top_level":
            effective_role = "nested_plackett" if engine == "primary" else "nested_unary"
        panel = _json_panel_path(panel_path)
        try:
            hash(integrand)
        except TypeError as exc:
            raise M245ScientificWorkerError("unhashable callable cannot prove a retained cache hit") from exc
        key = (
            scope,
            quantity,
            effective_role,
            tuple(json.dumps(item, sort_keys=True) for item in panel),
            tuple(_canonical_json_bytes(_endpoint(item)) for item in values),
            integrand,
        )
        if key not in self._cache:
            raise M245ScientificWorkerError("record-only cache hit has no retained W cache entry")
        return self(
            integrand=integrand,
            interval=values,
            engine=engine,
            precision_dps=precision_dps,
            cache_scope_id=cache_scope_id,
            quantity=quantity,
            call_role=call_role,
            panel_path=panel_path,
            parent_request_index=parent_request_index,
        )

    def __call__(
        self,
        *,
        integrand: Callable[..., Any],
        interval: Any,
        engine: str,
        precision_dps: int,
        cache_scope_id: str,
        quantity: str,
        call_role: str,
        panel_path: Any,
        parent_request_index: int | None,
    ) -> tuple[Any, Any]:
        del cache_scope_id  # Core-provided logical scopes are never authoritative.
        scope = self.authoritative_scope(engine, precision_dps)
        if not isinstance(quantity, str) or not quantity:
            raise M245ScientificWorkerError("quadrature quantity is empty")
        if call_role not in _QUAD_ROLES:
            raise M245ScientificWorkerError("quadrature role is outside the frozen census")
        request_index = len(self.ledger)
        inferred_parent = self._active_requests[-1] if self._active_requests else None
        if inferred_parent is None and parent_request_index is not None:
            raise M245ScientificWorkerError("core supplied a parent without an active gateway request")
        if parent_request_index is not None and parent_request_index != inferred_parent:
            raise M245ScientificWorkerError("core-supplied parent conflicts with active gateway nesting")
        parent = inferred_parent
        nesting_depth = len(self._active_requests)
        if nesting_depth > 1:
            raise M245ScientificWorkerError("quadrature nesting exceeds one level")
        effective_role = call_role
        if nesting_depth == 1 and call_role == "outer_top_level":
            effective_role = "nested_plackett" if engine == "primary" else "nested_unary"
        try:
            interval_values = list(interval)
        except TypeError as exc:
            raise M245ScientificWorkerError("quadrature interval is not iterable") from exc
        if len(interval_values) < 2:
            raise M245ScientificWorkerError("quadrature interval has fewer than two endpoints")
        panel = _json_panel_path(panel_path)
        try:
            hash(integrand)
        except TypeError:
            cache_key = None
        else:
            cache_key = (
                scope,
                quantity,
                effective_role,
                tuple(json.dumps(item, sort_keys=True) for item in panel),
                tuple(_canonical_json_bytes(_endpoint(item)) for item in interval_values),
                integrand,
            )
        cache_hit = cache_key is not None and cache_key in self._cache
        saved_eps = +mp.eps
        entry: dict[str, Any] = {
            "shard_id": self.shard_id,
            "invocation_index": self.invocation_index,
            "event_id": self.event_id,
            "engine": engine,
            "precision_dps": precision_dps,
            "cache_scope_id": scope,
            "request_index": request_index,
            "completion_index": None,
            "parent_request_index": parent,
            "nesting_depth": nesting_depth,
            "quantity": quantity,
            "call_role": effective_role,
            "panel_path": panel,
            "interval_left": _endpoint(interval_values[0]),
            "interval_right": _endpoint(interval_values[-1]),
            "method": "tanh-sinh",
            "maxdegree": 14,
            "error_api": True,
            "error_semantics": _ERROR_SEMANTICS,
            "interval_certified": False,
            "saved_mp_eps_mpf": _mpf_tuple(saved_eps),
            "mp_quad_invoked": not cache_hit,
            "cache_disposition": "hit" if cache_hit else "miss",
            "returned_value_mpf": None,
            "returned_error_mpf": None,
            "value_finite": False,
            "error_finite": False,
            "error_le_saved_mp_eps_over_8": False,
            "exception_type": None,
            "exception_message_sha256": None,
            "pass": False,
        }
        self.ledger.append(entry)
        self._active_requests.append(request_index)
        try:
            if cache_hit:
                value, error = self._cache[cache_key]
            else:
                value, error = _instrumented_quad(integrand, interval_values)
                if cache_key is not None:
                    self._cache[cache_key] = (value, error)
            value_finite = _finite(value)
            error_finite = _finite(error)
            error_gate = error_finite and error >= 0 and error <= saved_eps / 8
            returned_error_tuple = _mpf_tuple(error)
            entry.update(
                {
                    "returned_value_mpf": _mpf_tuple(value),
                    "returned_error_mpf": returned_error_tuple,
                    "value_finite": value_finite,
                    "error_finite": error_finite,
                    "error_le_saved_mp_eps_over_8": bool(error_gate),
                    "pass": bool(value_finite and error_gate),
                }
            )
            if not entry["pass"]:
                raise M245ScientificWorkerError("quadrature finite/error gate failed")
            if nesting_depth == 0:
                error_key = f"{engine}:{precision_dps}:{quantity}"
                self._outer_error_sums[error_key] = (
                    self._outer_error_sums.get(error_key, Fraction(0))
                    + _mpf_tuple_fraction(returned_error_tuple)
                )
            return value, error
        except Exception as exc:
            if entry["exception_type"] is None:
                entry["exception_type"] = type(exc).__name__
                entry["exception_message_sha256"] = hashlib.sha256(str(exc).encode("utf-8")).hexdigest()
                entry["pass"] = False
            raise
        finally:
            if not self._active_requests or self._active_requests[-1] != request_index:
                raise M245ScientificWorkerError("quadrature nesting stack corruption")
            self._active_requests.pop()
            entry["completion_index"] = self._completion_count
            self._completion_count += 1

    def ledger_refs(self) -> list[dict[str, Any]]:
        refs: list[dict[str, Any]] = []
        for engine in ("primary", "replica"):
            for dps in (80, 100):
                rows = [
                    row
                    for row in self.ledger
                    if row["engine"] == engine and row["precision_dps"] == dps
                ]
                refs.append(
                    {
                        "count": len(rows),
                        "engine": engine,
                        "precision_dps": dps,
                        "sha256": _sha256(rows),
                    }
                )
        return refs

    def summary(self, *, gateway_source_sha256: str) -> dict[str, Any]:
        if not isinstance(gateway_source_sha256, str) or len(gateway_source_sha256) != 64:
            raise M245ScientificWorkerError("gateway source hash is malformed")
        completion_order = [
            row["request_index"]
            for row in sorted(self.ledger, key=lambda row: row["completion_index"])
        ]
        outer_errors = {
            key: _fraction_mpf_tuple(value)
            for key, value in sorted(self._outer_error_sums.items())
        }
        return {
            "actual_mp_quad_call_count": sum(row["mp_quad_invoked"] for row in self.ledger),
            "all_calls_pass": all(row["pass"] for row in self.ledger),
            "cache_hit_count": sum(row["cache_disposition"] == "hit" for row in self.ledger),
            "completion_request_order": completion_order,
            "gateway_source_sha256": gateway_source_sha256,
            "nested_call_count": sum(row["nesting_depth"] == 1 for row in self.ledger),
            "outer_call_count": sum(row["nesting_depth"] == 0 for row in self.ledger),
            "outer_panel_error_sums_mpf": outer_errors,
            "request_count": len(self.ledger),
        }


def _bind_authoritative_scope(payload: Any, authoritative_scope: str) -> Any:
    """Replace every logical core scope field with W's transport scope."""

    if isinstance(payload, dict):
        return {
            key: (
                authoritative_scope
                if key == "cache_scope_id"
                else _bind_authoritative_scope(value, authoritative_scope)
            )
            for key, value in payload.items()
        }
    if isinstance(payload, list):
        return [_bind_authoritative_scope(value, authoritative_scope) for value in payload]
    return payload


def evaluate_event(
    event: dict[str, Any],
    *,
    shard_id: int,
    invocation_index: int,
) -> dict[str, Any]:
    """Evaluate one already-decoded event through both independent cores."""

    _load_scientific_modules()
    event_id = event.get("event_id") if isinstance(event, dict) else None
    if not isinstance(event_id, str) or not event_id:
        raise M245ScientificWorkerError("decoded event lacks an event_id")
    gateway = QuadGateway(
        shard_id=shard_id,
        invocation_index=invocation_index,
        event_id=event_id,
    )
    primary_by_precision: dict[str, Any] = {}
    replica_by_precision: dict[str, Any] = {}
    primary_node_values: dict[str, list[str]] = {}
    for dps in (80, 100):
        primary = m245_primary_core.run_primary_event(
            event,
            dps,
            quad_gateway=gateway,
        )
        if tuple(m245_primary_core.FIXED_B_NODES) != tuple(m245_replica_core.FIXED_B_NODES):
            raise M245ScientificWorkerError("primary/replica fixed-node census drift")
        node_values: list[str] = []
        for node_index, node in enumerate(m245_primary_core.FIXED_B_NODES):
            def node_gateway(*, _node_index: int = node_index, **request: Any) -> tuple[Any, Any]:
                original_path = _json_panel_path(request.get("panel_path"))
                request["quantity"] = f"primary_replica_node_{_node_index}:conditional_Phi2"
                request["call_role"] = "direct_analytic_gate"
                request["panel_path"] = ["primary_replica_node", _node_index, *original_path]
                request["parent_request_index"] = None
                return gateway(**request)

            value, node_audit = m245_primary_core.primary_b_at_g(
                event, node, dps, quad_gateway=node_gateway
            )
            if node_audit.get("all_calls_pass") is not True:
                raise M245ScientificWorkerError("primary fixed-node quadrature gate failed")
            node_values.append(mp.nstr(value, n=dps, strip_zeros=False))
        primary_node_values[str(dps)] = node_values
        replica = m245_replica_core.run_replica_event(
            event,
            dps,
            quad_gateway=gateway,
            cache_scope_id=gateway.authoritative_scope("replica", dps),
        )
        primary_by_precision[str(dps)] = _bind_authoritative_scope(
            primary, gateway.authoritative_scope("primary", dps)
        )
        replica_by_precision[str(dps)] = _bind_authoritative_scope(
            replica, gateway.authoritative_scope("replica", dps)
        )

    refs = gateway.ledger_refs()
    for engine, results in (
        ("primary", primary_by_precision),
        ("replica", replica_by_precision),
    ):
        for dps in (80, 100):
            scope_rows = [
                row
                for row in gateway.ledger
                if row["engine"] == engine and row["precision_dps"] == dps
            ]
            audit = results[str(dps)].get("quadrature_audit")
            if not isinstance(audit, dict) or not scope_rows:
                raise M245ScientificWorkerError("core omitted its dynamic quadrature audit")
            audit["observed_call_count"] = len(scope_rows)
            audit["all_calls_pass"] = all(row["pass"] for row in scope_rows)
            if engine == "primary":
                audit["outer_call_count"] = sum(row["nesting_depth"] == 0 for row in scope_rows)
                audit["nested_plackett_call_count"] = sum(row["nesting_depth"] == 1 for row in scope_rows)
            else:
                audit["cache_scope_id"] = gateway.authoritative_scope(engine, dps)

    fixture_hashes = primary_by_precision["100"].get("fixture_array_sha256")
    if fixture_hashes != replica_by_precision["100"].get("fixture_array_sha256"):
        raise M245ScientificWorkerError("primary/replica fixture binding drift")
    integrated_by_precision: dict[str, Any] = {}
    for dps in (80, 100):
        primary = primary_by_precision[str(dps)]
        replica = replica_by_precision[str(dps)]
        integrated = m245_replica_core.primary_replica_integrated_gates(
            primary["mu_rb"], replica["mu_rep"], primary["K"], replica["K_rep"]
        )
        node_gates = [
            {
                "node": node,
                "primary": primary_value,
                "replica": replica_value,
                "pass": bool(m245_replica_core.primary_replica_node_gate(primary_value, replica_value)),
            }
            for node, primary_value, replica_value in zip(
                replica["fixed_b_nodes"], primary_node_values[str(dps)], replica["b_rep_at_nodes"]
            )
        ]
        integrated_by_precision[str(dps)] = {
            **integrated,
            "node_gates": node_gates,
            "nodes_pass": all(row["pass"] for row in node_gates),
            "pass": bool(integrated.get("pass") is True and all(row["pass"] for row in node_gates)),
        }
    primary_replica_pass = all(
        row.get("pass") is True for row in integrated_by_precision.values()
    )
    p80, p100 = primary_by_precision["80"], primary_by_precision["100"]
    r80, r100 = replica_by_precision["80"], replica_by_precision["100"]

    def primary_sequence_gate(low: Any, high: Any) -> bool:
        return (
            isinstance(low, list) and isinstance(high, list) and len(low) == len(high)
            and all(m245_primary_core.precision_gate(a, b) for a, b in zip(low, high))
        )

    cross_checks = {
        "primary_mu_K": all(
            m245_primary_core.precision_gate(p80[name], p100[name])
            for name in ("mu_rb", "K")
        ),
        "primary_R": primary_sequence_gate(p80["R"], p100["R"]),
        "primary_G": all(
            primary_sequence_gate(low_row, high_row)
            for low_row, high_row in zip(p80["G"], p100["G"])
        ),
        "primary_d": primary_sequence_gate(p80["d"], p100["d"]),
        "primary_beta": primary_sequence_gate(p80["beta"], p100["beta"]),
        "primary_blocks": all(
            low_block["Q"] == high_block["Q"]
            and primary_sequence_gate(low_block["c"], high_block["c"])
            and all(
                m245_primary_core.precision_gate(low_block[name], high_block[name])
                for name in ("P", "V", "V_beta")
            )
            for low_block, high_block in zip(p80["leading_blocks"], p100["leading_blocks"])
        ),
        "replica_integrated": all(
            m245_replica_core.precision_gate(r80[name], r100[name])
            for name in ("mu_rep", "M_same", "M_cross", "K_rep")
        ),
        "replica_all_fixed_nodes": all(
            m245_replica_core.precision_gate(low, high)
            for low, high in zip(r80["b_rep_at_nodes"], r100["b_rep_at_nodes"])
        ),
        "primary_all_fixed_nodes": all(
            m245_primary_core.precision_gate(low, high)
            for low, high in zip(primary_node_values["80"], primary_node_values["100"])
        ),
    }
    cross_precision_pass = all(cross_checks.values())
    analytic_pass = all(
        result["analytic_direct_checks"].get("all_pass") is True
        and all(block.get("cholesky_pass") is True for block in result["leading_blocks"])
        and all(block.get("solve_pass") is True for block in result["leading_blocks"])
        and all(block.get("energy_gate", {}).get("pass") is True for block in result["leading_blocks"])
        and all(block.get("ordinary_beta_identity", {}).get("pass") is True for block in result["leading_blocks"])
        for result in primary_by_precision.values()
    )
    ratios: dict[str, list[float]] = {}
    for precision in ("80", "100"):
        result = primary_by_precision[precision]
        energy = float(result["K"])
        ratios[precision] = [float(block["P"]) / energy for block in result["leading_blocks"]]
    curve_models = {
        model: m245_primary_core.classify_curve_ladder(
            event_id, model, ratios["80"], ratios["100"]
        )
        for model in ("Gompertz", "geometric", "logistic")
    }
    event_result = {
        "event_id": event_id,
        "fixture_array_sha256": fixture_hashes,
        "primary_by_precision": primary_by_precision,
        "replica_by_precision": replica_by_precision,
        "cross_precision_gates": {"checks": cross_checks, "pass": bool(cross_precision_pass)},
        "primary_replica_gates": {
            "by_precision": integrated_by_precision,
            "pass": bool(primary_replica_pass),
        },
        "analytic_solve_energy_beta_gates": {"pass": bool(analytic_pass)},
        "curve_report": {
            "labels": {name: report["label"] for name, report in curve_models.items()},
            "models": curve_models,
        },
        "quad_gateway_ledger_refs": refs,
        "only_future_bound": "0<=additional_explainable_energy_beyond_Q8<=K-P8",
        "gate_verdict": "PASS" if cross_precision_pass and primary_replica_pass and analytic_pass else "FAIL",
        "firewall": {
            "challenge_network_or_weights": False,
            "champion_output": False,
            "credentials": False,
            "hidden_compute": False,
            "leaderboard": False,
            "m125_response": False,
            "m151_source_arrays": False,
            "m178_code_or_credit": False,
            "m196_state": False,
            "m243_input_or_import": False,
            "network_service": False,
            "retry_or_clipping": False,
            "scorer": False,
            "sealed_cells": False,
            "submission": False,
            "truth": False,
        },
        "forbidden_credit": True,
    }

    return {
        "event_result": event_result,
        "quad_call_ledger": gateway.ledger,
        "quad_gateway": gateway.summary(
            gateway_source_sha256=os.environ["M245_WORKER_SOURCE_SHA256"]
        ),
    }


_V2_NAME = "M245_FROZEN_MANIFEST_V2_20260810.json"
_V2_SHA256 = "0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b"
_ASSIGNMENTS = {
    0: ("E00", "E01"),
    1: ("E02", "E03"),
    2: ("E04", "E05"),
    3: ("E06", "E07"),
}


def _secure_regular_bytes(path: Path) -> bytes:
    try:
        before = os.lstat(path)
    except OSError as exc:
        raise M245ScientificWorkerError(f"cannot lstat immutable input: {exc}") from exc
    attributes = getattr(before, "st_file_attributes", 0)
    if not stat.S_ISREG(before.st_mode) or attributes & 0x400:
        raise M245ScientificWorkerError("immutable input is not a regular non-reparse file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise M245ScientificWorkerError("immutable input identity changed during open")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    after = os.lstat(path)
    if (
        (after.st_dev, after.st_ino, after.st_size)
        != (before.st_dev, before.st_ino, before.st_size)
        or getattr(after, "st_mtime_ns", None) != getattr(before, "st_mtime_ns", None)
    ):
        raise M245ScientificWorkerError("immutable input changed during read")
    raw = b"".join(chunks)
    if len(raw) != before.st_size:
        raise M245ScientificWorkerError("immutable input short read")
    return raw


def _worker_context_from_intent() -> tuple[dict[str, Any], Path]:
    required = (
        "M245_SHARD_ID",
        "M245_INVOCATION_INDEX",
        "M245_EVENT_ID",
        "M245_INTENT_PATH",
        "M245_TRIGGER_SHA256",
        "M245_TRIGGER_COMMIT",
        "M245_PRIMARY_SOURCE_SHA256",
        "M245_REPLICA_SOURCE_SHA256",
        "M245_WORKER_SOURCE_SHA256",
    )
    if any(name not in os.environ for name in required):
        raise M245ScientificWorkerError("worker context environment is incomplete")
    if "PYTHONPATH" in os.environ or "PYTHONHOME" in os.environ:
        raise M245ScientificWorkerError("ambient Python path injection is forbidden")
    try:
        shard_id = int(os.environ["M245_SHARD_ID"])
        invocation_index = int(os.environ["M245_INVOCATION_INDEX"])
    except ValueError as exc:
        raise M245ScientificWorkerError("worker shard context is not canonical decimal") from exc
    if str(shard_id) != os.environ["M245_SHARD_ID"] or str(invocation_index) != os.environ["M245_INVOCATION_INDEX"]:
        raise M245ScientificWorkerError("worker shard context is not canonical decimal")
    if shard_id not in _ASSIGNMENTS or invocation_index not in (1, 2):
        raise M245ScientificWorkerError("worker shard context is outside census")
    event_id = _ASSIGNMENTS[shard_id][invocation_index - 1]
    if os.environ["M245_EVENT_ID"] != event_id:
        raise M245ScientificWorkerError("worker event assignment drift")
    intent_path = Path(os.environ["M245_INTENT_PATH"])
    raw = _secure_regular_bytes(intent_path)
    try:
        intent = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise M245ScientificWorkerError("worker intent is not canonical JSON") from exc
    if raw != _canonical_json_bytes(intent):
        raise M245ScientificWorkerError("worker intent bytes are not canonical")
    expected_keys = {
        "artifact", "schema", "shard_id", "invocation_index", "event_id",
        "trigger_entry_sha256", "trigger_commit", "namespace", "status",
    }
    if not isinstance(intent, dict) or set(intent) != expected_keys:
        raise M245ScientificWorkerError("worker intent schema drift")
    if (
        intent["artifact"] != "M245_SHARD_INVOCATION_INTENT"
        or intent["schema"] != "m245-shard-invocation-intent-v1"
        or intent["shard_id"] != shard_id
        or intent["invocation_index"] != invocation_index
        or intent["event_id"] != event_id
        or intent["trigger_entry_sha256"] != os.environ["M245_TRIGGER_SHA256"]
        or intent["trigger_commit"] != os.environ["M245_TRIGGER_COMMIT"]
        or intent["status"] != "DURABLE_ATTEMPT_BURNED"
    ):
        raise M245ScientificWorkerError("worker intent/context binding drift")
    return intent, intent_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="M245 fail-closed scientific worker")
    parser.parse_args(argv)
    expected_argv = [str(Path(__file__).resolve())]
    if [str(Path(value).resolve()) for value in sys.argv] != expected_argv:
        raise M245ScientificWorkerError("W.sys.argv drift")
    if (
        os.path.normcase(str(Path(sys.executable).resolve()))
        != os.path.normcase(str(Path(_VENV_PYTHON).resolve()))
        or os.path.normcase(str(Path(getattr(sys, "_base_executable", "")).resolve()))
        != os.path.normcase(str(Path(_BASE_PYTHON).resolve()))
    ):
        raise M245ScientificWorkerError("W logical/base interpreter drift")
    intent, _intent_path = _worker_context_from_intent()
    sys.stdout.write("M245_W_READY\n")
    sys.stdout.flush()
    if sys.stdin.readline().rstrip("\r\n") != "M245_W_GO":
        raise M245ScientificWorkerError("worker GO barrier refused")
    _loaded_mp, primary_core, _replica_core = _load_scientific_modules()
    manifest_path = Path(__file__).resolve().parent / _V2_NAME
    manifest = primary_core.load_verified_v2(manifest_path, _V2_SHA256)
    event_id = intent["event_id"]
    events = [row for row in manifest["fixtures"] if row.get("event_id") == event_id]
    if len(events) != 1:
        raise M245ScientificWorkerError("assigned event is absent or duplicated in V2")
    payload = evaluate_event(
        events[0],
        shard_id=int(intent["shard_id"]),
        invocation_index=int(intent["invocation_index"]),
    )
    raw = _canonical_json_bytes(payload)
    digest = hashlib.sha256(raw).hexdigest()
    sys.stdout.write(f"M245_W_EVENT {len(raw)} {digest}\n")
    sys.stdout.flush()
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()
    sys.stdout.write("M245_W_DONE\n")
    sys.stdout.flush()
    if sys.stdin.readline().rstrip("\r\n") != "M245_W_EXIT":
        raise M245ScientificWorkerError("worker EXIT barrier refused")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
