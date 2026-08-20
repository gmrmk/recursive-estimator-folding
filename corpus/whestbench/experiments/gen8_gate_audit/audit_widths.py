"""TASK 2 -- width exposure of every promotion-eligible ledger record.

The production task is fixed at width 256, depth 32 (fold_ledger invariants:
"the fixed d=256,L=32 task").  The proposed width-transfer gate would require a
screen result's captured-signal statistic to be measured at >= 2 widths and to
extrapolate non-vanishing to n = 256.

For every ledger record whose status is promotion-eligible (screened / promoted
/ validated / survivor / component-pass), this script collects:

  * widths named in the ledger record's own prose,
  * widths recorded in the record's experiment artifacts (corpus/whestbench/
    experiments/<dir> and work/scorefloor_generation/<dir>), separated into
    MEASURED widths (per-case / per-state / per-cell fields) and MODELLED
    widths (cost-accounting / target-shape fields, which are arithmetic
    projections, not measurements),

and evaluates the two clauses of the proposed gate:

  clause 1: measured at >= 2 distinct widths
  clause 2: 256 among the measured widths (direct evidence at production width)

Read-only.  Writes only into gen8_gate_audit/.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
REPO = HERE.parents[3]
SHARE = REPO.parent.parent
SF = SHARE / "work" / "scorefloor_generation"
LEDGER = REPO / "corpus/whestbench/headroom/fold_ledger.json"

PROMOTION_STATUS = re.compile(
    r"screened|promoted|validated|survivor|component_pass|phase_a_pass|"
    r"_pass\b|pass_", re.I)
KILL_ONLY = re.compile(r"^killed", re.I)

WIDTH_KEYS = {"width", "n", "dim", "d", "widths", "n_width"}
MODEL_HINT = re.compile(r"cost|target|billed|arith|budget|envelope|projection|"
                        r"conservative|shape", re.I)

TEXT_WIDTH = re.compile(
    r"(?:\bn\s*=\s*(\d{1,4})\b)|(?:\bn(\d{2,4})\b)|(?:\bwidth[\s=]+(\d{1,4})\b)|"
    r"(?:\bd\s*=\s*(\d{1,4})\b)|(?:\bwidth-(\d{1,4})\b)", re.I)

SRC_WIDTH = re.compile(
    r"(?:\bWIDTHS?\s*=\s*[\(\[]?\s*([0-9,\s]+))|(?:\bwidth\s*=\s*(\d{1,4}))|"
    r"(?:\bWIDTH\s*=\s*(\d{1,4}))|(?:\bn\s*=\s*(\d{1,4})\b)|(?:\bn(\d{2,4})\b)")


def widths_from_source(dirs):
    out = set()
    for d in dirs:
        for p in list(d.rglob("*.py"))[:40] + list(d.rglob("*.md"))[:40]:
            if "__pycache__" in p.parts:
                continue
            try:
                t = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for m in SRC_WIDTH.finditer(t):
                for g in m.groups():
                    if not g:
                        continue
                    for tok in re.findall(r"\d{1,4}", g):
                        if int(tok) in PLAUSIBLE:
                            out.add(int(tok))
    return out

PLAUSIBLE = {4, 7, 8, 16, 32, 48, 56, 64, 72, 80, 96, 128, 160, 192, 256, 512}


def widths_from_text(txt):
    out = set()
    for m in TEXT_WIDTH.finditer(txt):
        for g in m.groups():
            if g and int(g) in PLAUSIBLE:
                out.add(int(g))
    return out


def walk_widths(obj, path, measured, modelled):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in WIDTH_KEYS and isinstance(v, int) and v in PLAUSIBLE:
                tgt = modelled if MODEL_HINT.search(".".join(path)) else measured
                tgt.add(v)
            walk_widths(v, path + [str(k)], measured, modelled)
    elif isinstance(obj, list):
        for v in obj[:4000]:
            walk_widths(v, path, measured, modelled)


def candidate_reports(rec_id):
    """Top-level *_REPORT.md / *_GATE.md files whose name tokens match the id."""
    toks = {t for t in re.split(r"[_\W]+", rec_id.lower()) if len(t) > 3}
    out = []
    for p in EXPERIMENTS.glob("*.md"):
        ntoks = {t for t in re.split(r"[_\W]+", p.stem.lower()) if len(t) > 3}
        if toks and len(toks & ntoks) >= max(2, len(toks) - 1):
            out.append(p)
    return out


def candidate_dirs(rec_id):
    dirs = []
    stems = {rec_id}
    stems.add(re.sub(r"^(gm_|m\d+[a-z]?_|t\d+_|s\d+[a-z]?_|u\d+_|a\d+_|v\d+_|n\d+[a-z]?_|wc\d+_)", "", rec_id))
    m = re.match(r"^(m\d+[a-z]?)_", rec_id)
    if m:
        stems.add(m.group(1))
    for root in (EXPERIMENTS, SF):
        if not root.exists():
            continue
        for d in root.iterdir():
            if not d.is_dir() or d.name == HERE.name:
                continue
            n = d.name
            if n == rec_id or rec_id.startswith(n) or n.startswith(rec_id):
                dirs.append(d)
                continue
            for s in stems:
                if len(s) >= 6 and (s in n or n in s):
                    dirs.append(d)
                    break
    return sorted(set(dirs))


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    rows = []
    for rec in ledger["candidates"]:
        st = rec["status"]
        if KILL_ONLY.match(st) or not PROMOTION_STATUS.search(st):
            continue
        blob = " ".join(str(rec.get(k, "")) for k in
                        ("mechanism", "prediction", "kill_condition", "result",
                         "status_note", "sensitivity", "bias_class"))
        text_w = widths_from_text(blob)
        measured, modelled = set(), set()
        dirs = candidate_dirs(rec["id"])
        for d in dirs:
            for jf in list(d.rglob("*.json"))[:60]:
                try:
                    if jf.stat().st_size > 8_000_000:
                        continue
                    data = json.loads(jf.read_text(encoding="utf-8", errors="replace"))
                except Exception:
                    continue
                walk_widths(data, [], measured, modelled)
        reports = candidate_reports(rec["id"])
        rep_w = set()
        for p in reports:
            rep_w |= widths_from_text(p.read_text(encoding="utf-8", errors="replace"))
        src_w = widths_from_source(dirs) if not (measured or text_w or rep_w) else set()
        all_measured = measured or text_w or rep_w or src_w
        rows.append({
            "id": rec["id"],
            "status": st,
            "widths_named_in_record_text": sorted(text_w),
            "widths_measured_in_artifacts": sorted(measured),
            "widths_in_harness_source": sorted(src_w),
            "widths_in_matched_reports": sorted(rep_w),
            "matched_report_files": [q.name for q in reports],
            "widths_modelled_only_in_artifacts": sorted(modelled - measured),
            "artifact_dirs": [str(d.relative_to(d.parents[1])) for d in dirs],
            "best_measured_width_set": sorted(all_measured),
            "measured_at_256": 256 in all_measured,
            "measured_at_2plus_widths": len(all_measured) >= 2,
            "gate_clause1_two_widths": len(all_measured) >= 2,
            "gate_clause2_reaches_256": 256 in all_measured,
        })

    exposed = [r for r in rows if r["best_measured_width_set"]
               and not r["measured_at_256"]]
    fail_2width = [r for r in rows if r["best_measured_width_set"]
                   and not r["measured_at_2plus_widths"]]
    no_width = [r for r in rows if not r["best_measured_width_set"]]

    import hashlib
    raw = LEDGER.read_bytes()
    out = {
        "ledger_snapshot": {
            "path": str(LEDGER.relative_to(REPO)),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "n_candidates": len(ledger["candidates"]),
            "note": "the ledger grew from 261 to 263 candidates during this audit; "
                    "a parallel session is appending gen8_* records. All Task-2 "
                    "counts below are pinned to this snapshot.",
        },
        "production_shape": {"width": 256, "depth": 32,
                             "source": "fold_ledger invariants.objective"},
        "n_promotion_eligible_records": len(rows),
        "n_with_no_width_parameter": len(no_width),
        "n_exposed_measured_below_256": len(exposed),
        "n_would_fail_two_width_clause": len(fail_2width),
        "rows": rows,
    }
    (HERE / "width_exposure.json").write_text(json.dumps(out, indent=1),
                                              encoding="utf-8")

    print(f"promotion-eligible records: {len(rows)}")
    print(f"  no width parameter at all:            {len(no_width)}")
    print(f"  measured ONLY below/without 256:      {len(exposed)}")
    print(f"  would FAIL the >=2-width clause:      {len(fail_2width)}")
    print("\n=== EXPOSED (supporting measurement not at width 256) ===")
    for r in exposed:
        print(f"  {r['id']:<42s} {r['status'][:28]:<28s} widths={r['best_measured_width_set']}")
    print("\n=== WOULD FAIL >=2-WIDTH CLAUSE ===")
    for r in fail_2width:
        print(f"  {r['id']:<42s} widths={r['best_measured_width_set']}")
    print("\n=== NO WIDTH PARAMETER (gate is not applicable as written) ===")
    for r in no_width:
        print(f"  {r['id']:<42s} {r['status'][:40]}")


if __name__ == "__main__":
    main()
