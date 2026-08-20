"""Token-detector scan: `"<literal>" in <source-text>` measurements.

Same defect class as M183.  A detector whose positive evidence is a string
literal matched against foreign source text reports a clean negative both when
the property is genuinely absent AND when the literal is simply wrong (renamed,
reformatted, or never a real token).  Absence of the token is indistinguishable
from absence of the property.

For every such comparison in corpus/whestbench/experiments this scan records:
  * the literal,
  * whether the literal occurs ANYWHERE in the first-party tree (corpus +
    work/scorefloor_generation).  A literal that occurs nowhere but its own
    detector can never fire: the detector is a permanent no-op.
  * the polarity: FAIL-CLOSED (`if TOKEN not in src: raise`) is safe -- a wrong
    literal makes it fire spuriously.  FAIL-OPEN (`if TOKEN in src: raise`, or
    `flag = TOKEN in src`) is the M183 shape.

Read-only.  Writes only into gen8_gate_audit/.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
REPO = HERE.parents[3]
SHARE = REPO.parent.parent
SF = SHARE / "work" / "scorefloor_generation"

TEXTY = ("src", "source", "text", "txt", "body", "code", "content", "s", "base",
         "runner", "m125", "m122", "m129", "m169", "cap_src", "blob")


def corpus_text_index():
    blobs = []
    for root in (REPO / "corpus", SF):
        for p in root.rglob("*.py"):
            if "__pycache__" in p.parts or p.parent == HERE:
                continue
            try:
                blobs.append((p, p.read_text(encoding="utf-8", errors="replace")))
            except Exception:
                pass
    return blobs


def main():
    blobs = corpus_text_index()
    hits = []
    for p in sorted(EXPERIMENTS.rglob("*.py")):
        if "__pycache__" in p.parts or p.parent == HERE:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(txt)
        except Exception:
            continue
        lines = txt.splitlines()
        parents = {}
        for node in ast.walk(tree):
            for ch in ast.iter_child_nodes(node):
                parents[ch] = node

        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            if not node.ops or not isinstance(node.ops[0], (ast.In, ast.NotIn)):
                continue
            left = node.left
            if not (isinstance(left, ast.Constant) and isinstance(left.value, str)):
                continue
            lit = left.value
            if len(lit) < 4:
                continue
            rhs = node.comparators[0]
            rname = getattr(rhs, "id", None) or getattr(rhs, "attr", None) or ""
            if isinstance(rhs, ast.Call):
                rname = getattr(rhs.func, "id", None) or getattr(rhs.func, "attr", "") or ""
            if not any(t == rname or t in str(rname).lower() for t in TEXTY):
                continue

            negated = isinstance(node.ops[0], ast.NotIn)
            # walk up for a `not (...)` wrapper
            par = parents.get(node)
            if isinstance(par, ast.UnaryOp) and isinstance(par.op, ast.Not):
                negated = not negated
            # FAIL-CLOSED means the raise happens when the token is MISSING.
            fail_open = not negated

            where = [str(q.relative_to(REPO.parent.parent))
                     for q, b in blobs if lit in b and q != p]
            hits.append({
                "file": str(p.relative_to(EXPERIMENTS)),
                "line": node.lineno,
                "literal": lit,
                "scanned_var": rname,
                "polarity": "FAIL-OPEN (M183 shape)" if fail_open else "fail-closed (safe)",
                "occurs_elsewhere_in_first_party_tree": len(where),
                "example_locations": where[:3],
                "line_text": lines[node.lineno - 1].strip()[:180],
            })

    void = [h for h in hits
            if h["occurs_elsewhere_in_first_party_tree"] == 0
            and h["polarity"].startswith("FAIL-OPEN")]
    (HERE / "token_detectors.json").write_text(
        json.dumps({"all": hits, "permanently_void_fail_open": void}, indent=1),
        encoding="utf-8")
    print(f"token comparisons found: {len(hits)}")
    print(f"  fail-open: {sum(1 for h in hits if h['polarity'].startswith('FAIL-OPEN'))}")
    print(f"  PERMANENTLY VOID (fail-open AND literal occurs nowhere else): {len(void)}")
    for h in void:
        print(f"    {h['file']}:{h['line']}  {h['literal']!r}")
        print(f"        {h['line_text']}")


if __name__ == "__main__":
    main()
