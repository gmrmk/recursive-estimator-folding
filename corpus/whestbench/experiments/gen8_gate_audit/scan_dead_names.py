"""Dead-name scan: getattr/hasattr/dict-.get attribute names that exist NOWHERE.

The M183 defect is a *dead name*: `op.dtypes` names a field no object in the
process has, so the guarded read silently produced the falsy default forever.

This scan collects every string literal used as a getattr/hasattr attribute name
or as a dict `.get(key, <falsy>)` key inside corpus/whestbench/experiments, then
asks whether that name is ever DEFINED anywhere reachable:

  * the installed flopscope / whestbench API surface, or
  * any attribute assignment / def / dataclass field / dict key literal in the
    whole first-party tree (corpus + work/scorefloor_generation).

A name that is read but never written anywhere is a dead name: the read can only
ever produce its default, and a falsy default makes that an undetectable null
measurement.

Read-only.  Writes only into gen8_gate_audit/.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
REPO = HERE.parents[3]
SHARE = REPO.parent.parent
SF = SHARE / "work" / "scorefloor_generation"

FALSY = (None, 0, 0.0, "", False)


def falsy_default(node):
    if isinstance(node, ast.Constant) and node.value in FALSY:
        return True
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)) and not node.elts:
        return True
    if isinstance(node, ast.Dict) and not node.keys:
        return True
    return False


# ---------------------------------------------------------------- universe --
def defined_names(roots):
    names = set()
    for root in roots:
        for p in root.rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(txt)
            except Exception:
                continue
            for n in ast.walk(tree):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.add(n.name)
                elif isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
                    names.add(n.attr)
                elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
                    names.add(n.target.id)
                elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                    names.add(n.id)
                elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                    # dict key literals / json field names
                    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", n.value):
                        names.add(n.value)
                elif isinstance(n, ast.keyword) and n.arg:
                    names.add(n.arg)
    return names


def json_keys(roots):
    keys = set()
    for root in roots:
        for p in root.rglob("*.json"):
            if p.stat().st_size > 8_000_000 or p.parent == HERE:
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            stack = [data]
            while stack:
                o = stack.pop()
                if isinstance(o, dict):
                    keys.update(str(k) for k in o)
                    stack.extend(o.values())
                elif isinstance(o, list):
                    stack.extend(o[:500])
    return keys


def main():
    api = json.loads((HERE / "_installed_api.json").read_text(encoding="utf-8"))
    universe = set()
    for members in api.values():
        universe.update(members)
    universe |= defined_names([REPO / "corpus", SF])
    universe |= json_keys([REPO / "corpus" / "whestbench" / "experiments"])
    # builtins / stdlib attribute names that are legitimately platform-optional
    import builtins, os, sys, stat
    for mod in (builtins, os, sys, stat):
        universe.update(dir(mod))
    universe.update(dir(os.stat_result))
    import numpy as np
    universe.update(dir(np))

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
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            fn = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            key = None
            default_falsy = None
            kind = None
            if fn in ("getattr", "hasattr") and n.args and isinstance(n.args[0], ast.AST):
                if len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) \
                        and isinstance(n.args[1].value, str):
                    key = n.args[1].value
                    kind = fn
                    default_falsy = (fn == "hasattr") or (
                        len(n.args) == 3 and falsy_default(n.args[2]))
            elif fn == "get" and len(n.args) == 2 and isinstance(n.args[0], ast.Constant) \
                    and isinstance(n.args[0].value, str):
                key = n.args[0].value
                kind = "dict.get"
                default_falsy = falsy_default(n.args[1])
            if key is None or key in universe:
                continue
            hits.append({
                "file": str(p.relative_to(EXPERIMENTS)),
                "line": n.lineno,
                "kind": kind,
                "dead_name": key,
                "falsy_default": bool(default_falsy),
                "line_text": lines[n.lineno - 1].strip()[:200],
            })

    (HERE / "dead_names.json").write_text(json.dumps(hits, indent=1), encoding="utf-8")
    print(f"universe size: {len(universe)}")
    print(f"dead-name reads found: {len(hits)}")
    for h in hits:
        flag = "SILENT" if h["falsy_default"] else "loud  "
        print(f"{flag}  {h['file']}:{h['line']}  {h['kind']}({h['dead_name']!r})")
        print(f"          {h['line_text']}")


if __name__ == "__main__":
    main()
