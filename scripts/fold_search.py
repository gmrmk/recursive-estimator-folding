"""fold_search — the operational spine of the recursive estimator search.

Mechanically enforces the campaign's fold contract, which until now lived as
prose in SKILL.md and discipline in agents' heads:

  predeclare -> (one-shot authorized) run -> mechanical verdict -> append-only
  ledger, with kill finality, frozen inputs, an evidence firewall that makes
  validation/holdout structurally unable to feed mutation, budget caps that
  fail closed, and a four-axis confidence report on every verdict.

Stdlib only.  Heavier runners (the clone's 24-pair measurement contract and
Windows job-object caps) plug in as the `runner.argv` of a cell; this module
is the authority layer around them, not a replacement for them.

Usage:
  python scripts/fold_search.py predeclare spec.json --cells DIR [--terminal]
  python scripts/fold_search.py run CELL_DIR
  python scripts/fold_search.py verdict CELL_DIR --ledger PATH
  python scripts/fold_search.py audit CELL_DIR
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


class SpecError(ValueError):
    """The predeclaration is structurally incomplete or malformed."""


class KillFinalityError(RuntimeError):
    """The spec collides with a killed record or repeats itself unchanged."""


class FirewallError(RuntimeError):
    """The spec or action crosses the development/terminal evidence boundary."""


class SealError(RuntimeError):
    """A frozen artifact changed between predeclare and run."""


class OneShotError(RuntimeError):
    """The cell's single development authorization is already consumed."""


REQUIRED_FIELDS = (
    "id", "hypothesis", "causal_mechanism", "cheapest_falsifier",
    "frozen_inputs", "seeds", "equal_budget_baseline", "thresholds",
    "budgets", "runner", "predicted_signature", "second_signal",
    "evidence_role", "confidence",
)
CONFIDENCE_AXES = ("implementation", "mechanism", "generalization", "compliance")
DENY_SEGMENTS = {"holdout", "validation", "truth", "private"}
# Numeric tokens precise enough to identify a mechanism (the MUB129 lesson:
# the ledger must be searched by number, not only by name).
NUMERIC_TOKEN = re.compile(r"\d+\.\d{3,}|\b\d{4,}\b")


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def _load_ledger(ledger_path: Path) -> dict:
    return json.loads(Path(ledger_path).read_text(encoding="utf-8"))


def _killed_records(ledger: dict):
    for rec in ledger.get("candidates", []):
        if "killed" in str(rec.get("status", "")):
            yield rec


def _numeric_tokens(text: str) -> set:
    return set(NUMERIC_TOKEN.findall(text))


def _check_spec(spec: dict) -> None:
    for field in REQUIRED_FIELDS:
        if field not in spec:
            raise SpecError(f"missing required field: {field}")
    conf = spec["confidence"]
    missing = [a for a in CONFIDENCE_AXES if a not in conf]
    if missing:
        raise SpecError(f"confidence must carry all four axes; missing {missing}")
    th = spec["thresholds"]
    for key in ("metric", "pass_when_lte", "kill_when_gte"):
        if key not in th:
            raise SpecError(f"thresholds.{key} is required")
    if "wall_seconds" not in spec["budgets"]:
        raise SpecError("budgets.wall_seconds is required")
    runner = spec["runner"]
    for key in ("argv", "cwd", "readable_roots"):
        if key not in runner:
            raise SpecError(f"runner.{key} is required")


def _check_firewall(spec: dict, terminal: bool) -> None:
    role = spec["evidence_role"]
    if role != "development" and not terminal:
        raise FirewallError(
            f"evidence_role {role!r} is terminal; predeclare it with "
            "terminal=True and its results can never feed mutation")
    paths = list(spec["runner"]["readable_roots"]) + list(spec["frozen_inputs"])
    if role == "development":
        for p in paths:
            parts = {seg.lower() for seg in Path(str(p)).parts}
            hit = parts & DENY_SEGMENTS
            if hit:
                raise FirewallError(
                    f"development cell may not touch {sorted(hit)} path: {p}")


def _check_kill_finality(spec: dict, ledger_path: Path, registry: Path) -> None:
    ledger = _load_ledger(ledger_path)
    killed_ids = set()
    killed_numbers = {}
    for rec in _killed_records(ledger):
        killed_ids.add(rec["id"])
        text = " ".join(str(rec.get(k, "")) for k in
                        ("mechanism", "prediction", "kill_condition"))
        for tok in _numeric_tokens(text):
            killed_numbers.setdefault(tok, rec["id"])
    if spec["id"] in killed_ids:
        raise KillFinalityError(
            f"id {spec['id']!r} is killed; kills are final — a premise change "
            "needs a new id and must clear the full ladder")
    own_text = " ".join(str(spec[k]) for k in
                        ("id", "hypothesis", "causal_mechanism"))
    for tok in _numeric_tokens(own_text):
        if tok in killed_numbers:
            raise KillFinalityError(
                f"numeric token {tok} collides with killed record "
                f"{killed_numbers[tok]!r}; search-the-ledger-by-number rule")
    spec_hash = sha256_bytes(canonical(spec))
    seen = json.loads(registry.read_text("utf-8")) if registry.exists() else {}
    if spec_hash in seen:
        raise KillFinalityError(
            f"byte-identical spec already predeclared as {seen[spec_hash]!r}; "
            "never rerun an unchanged failure — name the causal adjustment")
    seen[spec_hash] = spec["id"]
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(json.dumps(seen, indent=2), encoding="utf-8")


def predeclare(spec: dict, cells_dir, ledger_path, terminal: bool = False) -> Path:
    """Validate, firewall-check, collision-check, then freeze the cell."""
    cells_dir = Path(cells_dir)
    _check_spec(spec)
    _check_firewall(spec, terminal)
    _check_kill_finality(spec, Path(ledger_path),
                         cells_dir / ".spec_hashes.json")

    frozen = [{"path": str(p), "sha256": sha256_file(Path(p))}
              for p in spec["frozen_inputs"]]
    pd = dict(spec)
    pd["frozen_inputs"] = frozen
    pd["terminal"] = bool(terminal)
    pd["predeclared_at_utc"] = datetime.now(timezone.utc).isoformat()

    cell = cells_dir / spec["id"]
    cell.mkdir(parents=True, exist_ok=False)
    pd_path = cell / "predeclaration.json"
    pd_path.write_text(json.dumps(pd, indent=2, sort_keys=True),
                       encoding="utf-8")
    (cell / "GATE_TOKEN").write_text(sha256_file(pd_path), encoding="utf-8")
    return cell


def _seal_check(cell: Path, pd: dict) -> None:
    token = cell / "GATE_TOKEN"
    if not token.exists():
        raise OneShotError(
            "authorization token already consumed; the one development run "
            "is spent — a retry needs a new predeclaration with a named "
            "causal adjustment")
    if token.read_text("utf-8").strip() != sha256_file(cell / "predeclaration.json"):
        raise SealError("predeclaration.json changed after sealing")
    for item in pd["frozen_inputs"]:
        if sha256_file(Path(item["path"])) != item["sha256"]:
            raise SealError(f"frozen input changed: {item['path']}")


def run(cell) -> Path:
    """Consume the one-shot token and execute the declared runner."""
    cell = Path(cell)
    pd = json.loads((cell / "predeclaration.json").read_text("utf-8"))
    _seal_check(cell, pd)
    # Consume the token BEFORE execution: a crash mid-run must not leave a
    # second attempt open (fail closed).
    (cell / "GATE_TOKEN").rename(cell / "GATE_TOKEN.consumed")

    argv = pd["runner"]["argv"]
    wall_budget = pd["budgets"]["wall_seconds"]
    started = time.monotonic()
    outcome, metrics, stdout_tail, exit_code = "COMPLETED", None, "", None
    try:
        proc = subprocess.run(
            argv, cwd=pd["runner"]["cwd"], capture_output=True, text=True,
            timeout=wall_budget)
        exit_code = proc.returncode
        stdout_tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
        stdout_tail = stdout_tail[0]
        if exit_code != 0:
            outcome = "PROTOCOL_KILL_MALFORMED_METRICS"
        else:
            try:
                metrics = json.loads(stdout_tail)
            except (json.JSONDecodeError, ValueError):
                outcome = "PROTOCOL_KILL_MALFORMED_METRICS"
    except subprocess.TimeoutExpired:
        outcome = "BUDGET_KILL_WALL"
    wall_used = round(time.monotonic() - started, 3)

    git_head = None
    try:
        git_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).parent,
            capture_output=True, text=True, timeout=10).stdout.strip() or None
    except Exception:
        pass

    report = {
        "cell_id": pd["id"],
        "outcome": outcome,
        "metrics": metrics,
        "exit_code": exit_code,
        "stdout_last_line": stdout_tail,
        "wall_seconds_used": wall_used,
        "wall_seconds_budget": wall_budget,
        "evidence_role": pd["evidence_role"],
        "terminal_no_mutation": bool(pd.get("terminal")),
        "predeclaration_sha256": sha256_file(cell / "predeclaration.json"),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "argv": argv,
            "git_head": git_head,
        },
        "ran_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    body = json.dumps(report, indent=2, sort_keys=True)
    report["report_sha256"] = sha256_bytes(body.encode("utf-8"))
    path = cell / "report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True),
                    encoding="utf-8")
    return path


def verdict(cell, ledger_path) -> dict:
    """Compute PASS/KILL/INCONCLUSIVE mechanically and append to the ledger."""
    cell = Path(cell)
    pd = json.loads((cell / "predeclaration.json").read_text("utf-8"))
    rep = json.loads((cell / "report.json").read_text("utf-8"))
    if pd.get("terminal"):
        raise FirewallError(
            "terminal cells are structurally unable to feed mutation; their "
            "reports are read by humans, never by the ledger")
    th = pd["thresholds"]
    if rep["outcome"] != "COMPLETED":
        result, status = "KILL", "killed_protocol"
    else:
        value = rep["metrics"][th["metric"]]
        if value >= th["kill_when_gte"]:
            result, status = "KILL", "killed"
        elif value <= th["pass_when_lte"]:
            result, status = "PASS_SCREEN", "screened"
        else:
            result, status = "INCONCLUSIVE", "blocked"

    ledger = _load_ledger(Path(ledger_path))
    ledger["candidates"].append({
        "id": pd["id"],
        "status": status,
        "mechanism": pd["causal_mechanism"],
        "bias_class": pd.get("bias_class", "not_declared"),
        "prediction": pd["predicted_signature"],
        "kill_condition": json.dumps(th, sort_keys=True),
        "result": {
            "verdict": result,
            "metrics": rep["metrics"],
            "report_sha256": rep.get("report_sha256"),
            "outcome": rep["outcome"],
        },
    })
    Path(ledger_path).write_text(json.dumps(ledger, indent=2),
                                 encoding="utf-8")
    out = {
        "verdict": result,
        "status_written": status,
        "cell_id": pd["id"],
        "confidence": pd["confidence"],
        "report_sha256": rep.get("report_sha256"),
    }
    (cell / "verdict.json").write_text(json.dumps(out, indent=2, sort_keys=True),
                                       encoding="utf-8")
    return out


def audit(cell) -> dict:
    """Re-verify every recorded hash inside a cell; report, change nothing."""
    cell = Path(cell)
    pd = json.loads((cell / "predeclaration.json").read_text("utf-8"))
    problems = []
    for item in pd["frozen_inputs"]:
        p = Path(item["path"])
        if not p.exists():
            problems.append(f"missing frozen input {p}")
        elif sha256_file(p) != item["sha256"]:
            problems.append(f"hash drift on {p}")
    consumed = (cell / "GATE_TOKEN.consumed").exists()
    live = (cell / "GATE_TOKEN").exists()
    return {"cell_id": pd["id"], "problems": problems,
            "token": "consumed" if consumed else ("live" if live else "absent"),
            "has_report": (cell / "report.json").exists(),
            "has_verdict": (cell / "verdict.json").exists()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("predeclare")
    p.add_argument("spec"), p.add_argument("--cells", required=True)
    p.add_argument("--ledger", required=True)
    p.add_argument("--terminal", action="store_true")
    r = sub.add_parser("run"); r.add_argument("cell")
    v = sub.add_parser("verdict"); v.add_argument("cell")
    v.add_argument("--ledger", required=True)
    a = sub.add_parser("audit"); a.add_argument("cell")
    ns = ap.parse_args(argv)
    if ns.cmd == "predeclare":
        spec = json.loads(Path(ns.spec).read_text("utf-8"))
        cell = predeclare(spec, ns.cells, ns.ledger, terminal=ns.terminal)
        print(f"predeclared: {cell}")
    elif ns.cmd == "run":
        print(f"report: {run(ns.cell)}")
    elif ns.cmd == "verdict":
        print(json.dumps(verdict(ns.cell, ns.ledger), indent=2))
    elif ns.cmd == "audit":
        print(json.dumps(audit(ns.cell), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
