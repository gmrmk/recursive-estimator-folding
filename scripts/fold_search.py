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
import math
import os
import platform
import re
import subprocess
import sys
import time
from contextlib import contextmanager
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
DENY_SEGMENTS = ("holdout", "heldout", "validation", "val", "truth",
                 "private", "eval", "gold", "answers", "scorer")
# "test" is deliberately absent: whole-token matching still hits the
# "_test_" in every unittest temp directory, and the campaign's protected
# concepts are holdout/truth/scorer, not developer test fixtures.
# Whole-token match so 'value'/'eval'/'interval' don't trip 'val', while a
# real path segment '/val/' or a string '.../holdout/truth.csv' does.
_DENY_RE = re.compile(
    r"(?<![a-z0-9])(" + "|".join(DENY_SEGMENTS) + r")(?![a-z0-9])")


def _deny_hit(text: str):
    m = _DENY_RE.search(str(text).lower())
    return m.group(1) if m else None
# Any run of digits with optional decimal/exponent, INCLUDING inside an
# identifier (no word boundary — the review showed 'run4821x' hid its code).
NUMERIC_RUN = re.compile(r"\d+\.\d+(?:[eE][-+]?\d+)?|\d+(?:[eE][-+]?\d+)?"
                         r"|\.\d+")


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


@contextmanager
def _locked(lock_path: Path, timeout: float = 30.0):
    """OS-level exclusive lock via O_CREAT|O_EXCL — cross-process and thread
    safe (the review demonstrated unlocked read-modify-write dropping and
    corrupting ledger/registry entries under parallel calls)."""
    lock_path = Path(str(lock_path) + ".lock")
    deadline = time.monotonic() + timeout
    fd = None
    while fd is None:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except (FileExistsError, PermissionError):
            # PermissionError: NTFS delete-pending window while the previous
            # holder's unlink settles — retry exactly like a held lock.
            if time.monotonic() > deadline:
                raise TimeoutError(f"could not acquire {lock_path}")
            time.sleep(0.01)
    try:
        yield
    finally:
        os.close(fd)
        try:
            os.unlink(str(lock_path))
        except OSError:
            pass


def _atomic_write(path: Path, text: str) -> None:
    """Write via temp + os.replace so a crash mid-write cannot truncate the
    target (the append-only ledger must survive power loss)."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(str(tmp), str(path))


def _load_ledger(ledger_path: Path) -> dict:
    return json.loads(Path(ledger_path).read_text(encoding="utf-8"))


def _killed_records(ledger: dict):
    for rec in ledger.get("candidates", []):
        if "killed" in str(rec.get("status", "")):
            yield rec


def _numeric_tokens(text: str) -> set:
    """Canonical numeric keys: parse each digit run to a float and normalize,
    so 0.7731, 0.77310, and 7.731e-1 collide (the same mechanism reworded).
    Keep only identifying magnitudes: >=3 significant figures OR integer >=1000.
    """
    keys = set()
    for m in NUMERIC_RUN.finditer(text):
        raw = m.group(0)
        try:
            val = float(raw)
        except ValueError:
            continue
        if "." in raw or "e" in raw.lower():
            digits = (raw.lstrip("-+0").replace(".", "")
                      .split("e")[0].split("E")[0])
            is_identifying = len(digits.rstrip("0")) >= 3
        else:
            is_identifying = abs(val) >= 1000
        if is_identifying and math.isfinite(val):
            keys.add(f"{val:.6e}")
    return keys


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
    if not (th["pass_when_lte"] < th["kill_when_gte"]):
        raise SpecError(
            "thresholds must satisfy pass_when_lte < kill_when_gte; an "
            "inverted spec collapses the gray zone into automatic KILL")
    wall = spec["budgets"].get("wall_seconds")
    if not isinstance(wall, (int, float)) or isinstance(wall, bool) or wall <= 0:
        raise SpecError(
            "budgets.wall_seconds must be a positive number; null/0 would "
            "pass timeout=None to the runner and remove the wall cap")
    runner = spec["runner"]
    for key in ("argv", "cwd", "readable_roots"):
        if key not in runner:
            raise SpecError(f"runner.{key} is required")


def _check_firewall(spec: dict, terminal: bool,
                    require_exists: bool = True) -> None:
    role = spec["evidence_role"]
    if role != "development" and not terminal:
        raise FirewallError(
            f"evidence_role {role!r} is terminal; predeclare it with "
            "terminal=True and its results can never feed mutation")
    if role != "development":
        return
    # cwd is inside the boundary too — the review reached holdout through a
    # denied cwd with relative reads while readable_roots looked clean.
    paths = (list(spec["runner"]["readable_roots"])
             + list(spec["frozen_inputs"])
             + [spec["runner"]["cwd"]])
    for p in paths:
        declared = Path(str(p))
        if require_exists and not declared.exists():
            raise FirewallError(
                f"declared path does not exist at predeclare time: {p} — "
                "a later-created junction there would bypass the resolve "
                "check, so nonexistent declarations are refused")
        try:
            resolved = declared.resolve()
        except OSError:
            resolved = declared
        hit = _deny_hit(str(declared)) or _deny_hit(str(resolved))
        if hit:
            raise FirewallError(
                f"development cell may not touch {hit!r} path: {p} "
                f"(resolves to {resolved})")
    # argv is scanned too: readable_roots is declarative, and an argv that
    # names a denied location is the cheapest honest tripwire we have short
    # of OS-level confinement (which stays a named [GAP] in the docs).
    for arg in spec["runner"]["argv"]:
        hit = _deny_hit(str(arg))
        if hit:
            raise FirewallError(
                f"development cell argv names a {hit!r} location: {arg!r}")


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
    registry.parent.mkdir(parents=True, exist_ok=True)
    with _locked(registry):
        seen = (json.loads(registry.read_text("utf-8"))
                if registry.exists() else {})
        if spec_hash in seen:
            raise KillFinalityError(
                f"byte-identical spec already predeclared as "
                f"{seen[spec_hash]!r}; never rerun an unchanged failure — "
                "name the causal adjustment")
        seen[spec_hash] = spec["id"]
        _atomic_write(registry, json.dumps(seen, indent=2))


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
    consumed = cell / "GATE_TOKEN.consumed"
    if consumed.exists() or not token.exists():
        # A stray consumed marker beside a live token is treated as spent:
        # fail closed rather than let Windows' rename FileExistsError leak.
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
    # Re-run the firewall at execution time: a junction created between
    # predeclare and run was a demonstrated bypass of the predeclare-only
    # resolve check. predeclare froze frozen_inputs into {path, sha256}
    # dicts, so present a string view for the scan.
    fw_view = dict(pd)
    fw_view["frozen_inputs"] = [item["path"] if isinstance(item, dict)
                                else item for item in pd["frozen_inputs"]]
    _check_firewall(fw_view, bool(pd.get("terminal")))
    # Consume the token BEFORE execution via an atomic O_CREAT|O_EXCL claim:
    # the review proved concurrent Path.rename on Windows lets multiple
    # racers through, while exclusive-create admits exactly one.
    token = cell / "GATE_TOKEN"
    consumed = cell / "GATE_TOKEN.consumed"
    try:
        fd = os.open(str(consumed), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise OneShotError("authorization already claimed by another caller")
    try:
        os.write(fd, token.read_bytes())
    finally:
        os.close(fd)
    try:
        token.unlink()
    except OSError:
        pass

    argv = pd["runner"]["argv"]
    wall_budget = pd["budgets"]["wall_seconds"]
    metric_key = pd["thresholds"]["metric"]
    started = time.monotonic()
    outcome, metrics, stdout_tail, exit_code = "COMPLETED", None, "", None
    try:
        proc = subprocess.run(
            argv, cwd=pd["runner"]["cwd"], capture_output=True, text=True,
            errors="replace", timeout=wall_budget)
        exit_code = proc.returncode
        stdout_tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
        stdout_tail = stdout_tail[0]
        if exit_code != 0:
            outcome = "PROTOCOL_KILL_MALFORMED_METRICS"
        else:
            try:
                metrics = json.loads(stdout_tail)
            except (json.JSONDecodeError, ValueError):
                metrics = None
                outcome = "PROTOCOL_KILL_MALFORMED_METRICS"
            else:
                # Shape + finiteness gates: a scalar, a missing declared
                # metric, or a NaN/Infinity must be a canonical protocol
                # kill, never a downstream crash or a fake gray zone.
                if (not isinstance(metrics, dict)
                        or metric_key not in metrics
                        or not isinstance(metrics[metric_key], (int, float))
                        or not math.isfinite(metrics[metric_key])):
                    outcome = "PROTOCOL_KILL_MALFORMED_METRICS"
    except subprocess.TimeoutExpired:
        outcome = "BUDGET_KILL_WALL"
    except Exception as exc:  # noqa: BLE001 — token is spent; a report MUST exist
        outcome = "PROTOCOL_KILL_MALFORMED_METRICS"
        stdout_tail = f"runner launch failed: {type(exc).__name__}: {exc}"
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
    _atomic_write(path, json.dumps(report, indent=2, sort_keys=True))
    return path


def _seeds_disagree(pd: dict, rep: dict) -> bool:
    """True when the spec declares seeds AND the runner reports the seeds it
    actually used (metrics.config.seeds convention) AND the two differ.

    Runners that do not report their seeds are not bound (older cells predate
    the convention); the check cannot fire on absence, only on contradiction.
    """
    declared = pd.get("seeds")
    metrics = rep.get("metrics")
    observed = None
    if isinstance(metrics, dict):
        config = metrics.get("config")
        if isinstance(config, dict):
            observed = config.get("seeds")
    if not declared or not isinstance(observed, list):
        return False
    return [int(s) for s in observed] != [int(s) for s in declared]


def verdict(cell, ledger_path) -> dict:
    """Compute PASS/KILL/INCONCLUSIVE mechanically and append to the ledger.

    Authenticated end to end (the review defeated the unauthenticated form
    four ways): the consumed token must exist and still hash-match the
    predeclaration; the report must bind to this cell and predeclaration and
    must re-derive its own body hash; and verdicts are one-shot.
    """
    cell = Path(cell)
    if (cell / "verdict.json").exists():
        raise FirewallError(
            "verdict already recorded; verdicts are one-shot — a re-verdict "
            "after editing evidence was a demonstrated kill-finality bypass")
    consumed = cell / "GATE_TOKEN.consumed"
    if not consumed.exists():
        raise SealError("no consumed authorization token: this cell never ran")
    pd_hash = sha256_file(cell / "predeclaration.json")
    if consumed.read_text("utf-8").strip() != pd_hash:
        raise SealError("predeclaration.json changed after the run")
    pd = json.loads((cell / "predeclaration.json").read_text("utf-8"))
    rep = json.loads((cell / "report.json").read_text("utf-8"))
    if rep.get("cell_id") != pd["id"]:
        raise SealError("report belongs to a different cell")
    if rep.get("predeclaration_sha256") != pd_hash:
        raise SealError("report was produced under a different predeclaration")
    body = {k: v for k, v in rep.items() if k != "report_sha256"}
    if sha256_bytes(json.dumps(body, indent=2, sort_keys=True)
                    .encode("utf-8")) != rep.get("report_sha256"):
        raise SealError("report body hash mismatch: report.json was edited")
    if pd.get("terminal"):
        raise FirewallError(
            "terminal cells are structurally unable to feed mutation; their "
            "reports are read by humans, never by the ledger")
    th = pd["thresholds"]
    if rep["outcome"] != "COMPLETED":
        result, status = "KILL", "killed_protocol"
    elif _seeds_disagree(pd, rep):
        # The harness never injects spec.seeds into the runner -- runners own
        # their seeds. A spec that declares one seed set while the runner
        # reports another is a replication-theatre hazard (demonstrated by
        # k32_base_sensitivity_v2: "fresh seed" spec, stale runner constant,
        # bit-identical rerun of observed data).
        result, status = "KILL", "killed_protocol"
    else:
        value = rep["metrics"][th["metric"]]
        if value >= th["kill_when_gte"]:
            result, status = "KILL", "killed"
        elif value <= th["pass_when_lte"]:
            result, status = "PASS_SCREEN", "screened"
        else:
            result, status = "INCONCLUSIVE", "blocked"

    record = {
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
    }
    ledger_path = Path(ledger_path)
    with _locked(ledger_path):
        ledger = _load_ledger(ledger_path)
        ledger["candidates"].append(record)
        _atomic_write(ledger_path, json.dumps(ledger, indent=2))
    out = {
        "verdict": result,
        "status_written": status,
        "cell_id": pd["id"],
        "confidence": pd["confidence"],
        "report_sha256": rep.get("report_sha256"),
    }
    _atomic_write(cell / "verdict.json",
                  json.dumps(out, indent=2, sort_keys=True))
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
