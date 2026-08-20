#!/usr/bin/env python3
"""Build a deterministic, exhaustive failure-salvage atlas from the fold ledger.

The atlas is deliberately descriptive.  It does not promote a candidate or
infer that a preserved component composes with another one.  Its job is to
make omissions visible and to turn every historical result into typed input
for the next recursive-estimator-folding generation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "corpus" / "whestbench" / "headroom" / "fold_ledger.json"
DEFAULT_JSON = ROOT / "corpus" / "whestbench" / "headroom" / "GEN6_FAILURE_SALVAGE_ATLAS_20260809.json"
DEFAULT_MD = ROOT / "corpus" / "whestbench" / "headroom" / "GEN6_FAILURE_SALVAGE_ATLAS_20260809.md"


FAMILY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("sampling_and_design", ("sampl", "rqmc", "haar", "kerdock", "cubature", "frame", "rotation", "antipod", "great_circle", "point set", "design")),
    ("engineering_and_cost", ("strassen", "winograd", "wht", "flash", "row_block", "call fusion", "dispatch", "allocation", "buffer", "fold3", "liveness", "throughput", "backend")),
    ("analytic_moment_closure", ("fullcov", "gaussian", "moment", "copula", "closure", "tallis", "laplace", "terminal law")),
    ("higher_cumulant_source", ("cumulant", "k3", "k4", "hermite", "vertex", "chaos", "diagram", "collision", "source211", "source 211", "[2,1,1]", "price")),
    ("control_and_multifidelity", ("control", "anchor", "gls", "shrink", "ridgelet", "tangent", "multifidelity", "rao", "residual", "attenuation")),
    ("harmonic_and_symmetry", ("harmonic", "gegenbauer", "fourier", "spherical", "cymatic", "phase", "compact group", "gauge", "equivariant", "symmetry")),
    ("compression_and_low_rank", ("rank", "latent", "factor", "tensor", "hosvd", "nystrom", "quotient", "algebra", "jspace", "jacobian", "projector", "sketch")),
    ("endpoint_facet_and_coarea", ("endpoint", "facet", "boundary", "coarea", "owen", "phi2", "rank face", "rank-one", "rankone", "psd chart", "plackett")),
    ("routing_and_learned_surrogates", ("learned", "attention", "router", "mixture of experts", "moe", "physarum", "flatworm", "transformer", "maxent", "student", "distill")),
    ("robustness_and_protocol", ("guard", "fallback", "hostile", "failure", "protocol", "firewall", "canary", "package", "runbook", "dossier", "calibration", "postmortem")),
)


SOURCE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("truth_or_oracle_only", ("truth", "oracle", "target-dependent", "exact target")),
    ("sampled_network_paths", ("sample", "path", "haar", "rqmc", "rotation", "pilot", "hansen", "horvitz", "importance")),
    ("weights_only_analytic_state", ("weights-only", "weight-derived", "analytic", "fullcov", "covariance", "moment propagation", "backgroundarchive", "background archive")),
    ("endpoint_or_facet_geometry", ("endpoint", "facet", "boundary", "coarea", "rank face", "owen", "phi2", "plackett")),
    ("output_or_frame_statistics", ("output", "frame", "gls", "shrinkage", "centroid", "tomography")),
    ("offline_learned_features", ("learned", "student", "attention", "ridge", "cross-validation", "oof", "distill")),
    ("deterministic_compute_only", ("strassen", "winograd", "wht", "buffer", "flash", "dispatch", "guard", "package", "runbook")),
)


FAILURE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("nonidentifiability_or_missing_information", ("nonidentif", "does not identify", "no right-hand side", "no rhs", "cannot manufacture", "unobservable", "blind", "same unknown", "arbitrary")),
    ("variance_or_signal_to_noise", ("variance", "tail", "p99", "noise", "second moment", "importance", "hansen", "horvitz", "amplification")),
    ("bias_or_invalid_expectation", ("bias", "not exact", "unbiasedness", "double-count", "ownership failure", "invalid local", "not the full radon")),
    ("approximation_or_materiality", ("fidelity", "accuracy", "ratio", "worse", "miss", "below", "improve", "effect", "correlation", "r2", "score")),
    ("arithmetic_cost", ("flop", "over budget", "cost", "trillion", "o(n", "dense", "bill")),
    ("wall_calls_or_allocation", ("wall", "call", "allocation", "temporary", "backend", "throughput", "timeout")),
    ("memory_or_liveness", ("mib", "gib", "memory", "rss", "liveness", "zero-progress", "working set")),
    ("numerical_or_endpoint_coverage", ("nonfinite", "nan", "condition", "rank face", "endpoint", "singular", "remainder", "clipping", "ridge", "refuse")),
    ("missing_interface_or_provider", ("missing", "absent", "no provider", "no implementation", "no caller", "blocked", "interface", "compiler", "producer")),
    ("protocol_or_generalization", ("protocol", "leak", "holdout", "cross-seed", "generalization", "capacity", "firewall", "pretarget")),
    ("representation_not_closed", ("not closed", "trace collapse", "tumble", "omitted", "all-distinct", "full-state", "rank mismatch", "compress")),
    ("theorem_or_class_closure", ("theorem", "proved no-go", "no-go", "impossible", "subsum", "collapse theorem", "mediant")),
)


POSITIVE_WORDS = (
    "preserve", "retained", "retain", "survive", "passed", "pass", "exact",
    "identity", "component", "reusable", "opens", "repairs", "improved",
)
NEGATIVE_WORDS = (
    "killed", "kill", "failed", "fails", "worse", "missed", "blocked",
    "absent", "unresolved", "over budget", "nonident", "no ", "cannot",
)
REOPEN_WORDS = ("reopen", "next ", "requires", "until", "only after", "future", "must ")


def normalized_text(candidate: dict) -> str:
    return " ".join(
        str(candidate.get(key, ""))
        for key in ("id", "mechanism", "bias_class", "prediction", "kill_condition", "result", "status_note")
    ).lower()


def tags(text: str, rules: Iterable[tuple[str, tuple[str, ...]]], fallback: str) -> list[str]:
    found = [label for label, needles in rules if any(needle in text for needle in needles)]
    return found or [fallback]


def canonical_status(status: str) -> str:
    if status == "promoted":
        return "promoted"
    if status in {"validated", "package_validated"}:
        return "validated"
    if "killed" in status or "no_go" in status:
        return "killed_or_closed"
    if status == "blocked" or "blocked" in status or "absent" in status:
        return "blocked"
    if status == "proposed" or "open" in status or "unresolved" in status or "uncertain" in status:
        return "open_or_uncertain"
    if status == "screened" or "screened" in status:
        return "screened_component"
    return "preserved_component"


def sentences(value: str) -> list[str]:
    # Keep decimal points intact while splitting prose at sentence-like stops.
    return [part.strip() for part in re.split(r"(?<=[A-Za-z\]])[.!?]\s+|;\s+", value) if part.strip()]


def matching_sentences(value: str, needles: Iterable[str], limit: int = 3) -> list[str]:
    output: list[str] = []
    for sentence in sentences(value):
        lower = sentence.lower()
        if any(needle in lower for needle in needles):
            output.append(sentence)
        if len(output) >= limit:
            break
    return output


def build_record(index: int, candidate: dict) -> dict:
    text = normalized_text(candidate)
    status = canonical_status(str(candidate["status"]))
    result = str(candidate.get("result", ""))
    passed = matching_sentences(result, POSITIVE_WORDS)
    failed = matching_sentences(result + " " + str(candidate.get("kill_condition", "")), NEGATIVE_WORDS, limit=2)
    reopening = matching_sentences(result + " " + str(candidate.get("prediction", "")), REOPEN_WORDS, limit=2)
    if not passed:
        passed = [
            "No passed component is asserted; preserve the exact predeclaration, evidence, and falsifier as negative knowledge."
        ]
    if not failed:
        if status in {"promoted", "validated", "screened_component", "preserved_component"}:
            failed = ["No failed link is asserted at the recorded gate; downstream claims remain separate."]
        else:
            failed = ["The recorded kill condition fired; consult the bound result and do not infer family-wide impossibility."]
    if not reopening:
        reopening = [
            "Reopen only with a new observable, exact identity, circuit class, or resource proof that repairs the recorded first break; parameter drift is excluded."
        ]

    failure_tags = tags(text, FAILURE_RULES, "recorded_gate_only")
    if status in {"promoted", "validated"}:
        failure_tags = ["no_failure_at_recorded_gate"] + failure_tags

    return {
        "index": index,
        "id": candidate["id"],
        "raw_status": candidate["status"],
        "canonical_status": status,
        "operator_families": tags(text, FAMILY_RULES, "campaign_or_other"),
        "information_sources": tags(text, SOURCE_RULES, "unspecified_in_record"),
        "failure_boundaries": failure_tags,
        "passed_tissue": passed,
        "failed_link": failed,
        "reopening_condition": reopening,
        "prediction": candidate["prediction"],
        "kill_condition": candidate["kill_condition"],
        "result_present": bool(result),
    }


def summarize(records: list[dict]) -> dict:
    def count(field: str) -> dict[str, int]:
        values = Counter(item for record in records for item in record[field])
        return dict(sorted(values.items(), key=lambda item: (-item[1], item[0])))

    status_counts = Counter(record["canonical_status"] for record in records)
    uncertainties = [
        record["id"] for record in records
        if record["canonical_status"] in {"blocked", "open_or_uncertain", "screened_component", "preserved_component"}
    ]
    return {
        "total_records": len(records),
        "canonical_status_counts": dict(sorted(status_counts.items())),
        "operator_family_counts": count("operator_families"),
        "information_source_counts": count("information_sources"),
        "failure_boundary_counts": count("failure_boundaries"),
        "unresolved_or_component_ids": uncertainties,
    }


def build_payload(ledger_path: Path) -> dict:
    raw = ledger_path.read_bytes()
    ledger = json.loads(raw)
    records = [build_record(index, candidate) for index, candidate in enumerate(ledger["candidates"])]
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("ledger ids are not unique")
    for record in records:
        for field in (
            "operator_families", "information_sources", "failure_boundaries",
            "passed_tissue", "failed_link", "reopening_condition",
        ):
            if not record[field]:
                raise ValueError(f"{record['id']} has no {field}")
    return {
        "schema_version": 1,
        "purpose": "Exhaustive descriptive salvage atlas; non-evidentiary and non-promotional.",
        "ledger_sha256": hashlib.sha256(raw).hexdigest(),
        "invariants": ledger["invariants"],
        "summary": summarize(records),
        "records": records,
    }


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Generation 6 exhaustive failure-salvage atlas",
        "",
        "Status: deterministic descriptive derivation from the append-only fold ledger. It does not promote an estimator, authorize a contest run, or treat an empirical kill as a family-wide theorem.",
        "",
        f"Ledger SHA-256: `{payload['ledger_sha256']}`",
        f"Coverage: **{summary['total_records']}/{summary['total_records']} records**; every record has a status disposition, operator family, information source, failure boundary, preserved tissue, and reopening condition.",
        "",
        "## Coverage summary",
        "",
        "| canonical disposition | count |",
        "|---|---:|",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in summary["canonical_status_counts"].items())
    lines += ["", "### Failure boundaries (multi-label)", "", "| boundary | records |", "|---|---:|"]
    lines.extend(f"| {key} | {value} |" for key, value in summary["failure_boundary_counts"].items())
    lines += [
        "",
        "## Interpretation discipline",
        "",
        "- A killed implementation donates its exact identities, tests, diagnostics, and proved constraints; it does not donate its failed estimator unchanged.",
        "- A new child must repair the earliest failed causal link or add a genuinely new information variable. Renaming, sign flipping, rank/ridge drift, and affine mixing of cached losers are rejected before execution.",
        "- The exhaustive table is a search index. Composition still requires shared semantics, independent evidence, matched cost, and an interaction or residual-covariance test.",
        "- Entries marked open, screened, or preserved are uncertainties, not wins. Their prediction and kill condition remain the settling checks.",
        "",
        "## Exhaustive record table",
        "",
        "| # | id | disposition | families | information | failure boundary |",
        "|---:|---|---|---|---|---|",
    ]
    for record in payload["records"]:
        lines.append(
            "| {index} | `{id}` | {status} | {families} | {sources} | {failures} |".format(
                index=record["index"],
                id=md_escape(record["id"]),
                status=record["canonical_status"],
                families=md_escape(", ".join(record["operator_families"])),
                sources=md_escape(", ".join(record["information_sources"])),
                failures=md_escape(", ".join(record["failure_boundaries"])),
            )
        )
    lines += [
        "",
        "## Machine-readable tissue and reopening rules",
        "",
        "The companion JSON stores, for every row above, the extracted passed tissue, failed link, reopening condition, original prediction, and original kill condition. That file is the authoritative input to mutation generation.",
        "",
    ]
    return "\n".join(lines)


def serialized(payload: dict) -> tuple[str, str]:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n", render_markdown(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--check", action="store_true", help="fail if committed outputs are stale")
    args = parser.parse_args()

    payload = build_payload(args.ledger)
    json_text, md_text = serialized(payload)
    if args.check:
        failures = []
        for path, expected in ((args.json, json_text), (args.markdown, md_text)):
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                failures.append(str(path))
        if failures:
            raise SystemExit("stale or missing atlas outputs: " + ", ".join(failures))
        print(f"atlas is current: {payload['summary']['total_records']} records")
        return

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json_text, encoding="utf-8")
    args.markdown.write_text(md_text, encoding="utf-8")
    print(f"wrote exhaustive atlas: {payload['summary']['total_records']} records")


if __name__ == "__main__":
    main()
