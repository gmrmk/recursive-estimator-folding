"""Scan for the M183 defect class in whestbench experiment scripts.

M183 defect (ground truth, verified 2026-08-10): the f64 detector read
`getattr(op, "dtypes", None) or ()` while flopscope 0.10.0's OpRecord exposes
`resolved_dtype` and no `dtypes`. The getattr default made the comprehension
empty, `any(...)` over empty is False, and the measurement returned a
STRUCTURAL ZERO (0.00% float64 share) on every program regardless of ground
truth.

Three sub-patterns are detected:
  (a) getattr(obj, "<literal>", <falsy default>)  -- silently yields
      empty/zero/None when the attribute is absent.
  (b) any(...)/all(...)/sum(...)/max(...)/min(...)/len(...) over a
      comprehension or generator, where emptiness of the iterable is
      indistinguishable from a true negative.
  (c) getattr / .get / attribute literals checked against the INSTALLED
      flopscope + whestbench API that do not exist there.

Read-only. Writes only into gen8_gate_audit/.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
API_JSON = HERE / "_installed_api.json"

FALSY_CONSTS = (None, 0, 0.0, "", False)

# Attribute names known to exist somewhere in the installed API surface.
api = json.loads(API_JSON.read_text(encoding="utf-8"))
API_NAMES = set()
for cls, members in api.items():
    API_NAMES.update(members)

# Names that clearly belong to flopscope/whestbench objects (the ones whose
# misspelling is a *silent* measurement defect rather than a crash).
FLOPSCOPE_HINT_ATTRS = {
    "op_name", "subscripts", "shapes", "flop_cost", "cumulative", "namespace",
    "resolved_dtype", "op_log", "flops_used", "flops_remaining", "summary",
    "summary_dict", "wall_time_s", "residual_wall_time_s", "elapsed_s",
    "flop_budget", "wall_time_limit_s", "flopscope_backend_time_s",
    "flopscope_overhead_time_s", "deduct", "deduct_after",
}


def is_falsy_default(node: ast.AST) -> tuple[bool, str]:
    if isinstance(node, ast.Constant) and node.value in FALSY_CONSTS:
        return True, repr(node.value)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)) and not node.elts:
        return True, "empty literal"
    if isinstance(node, ast.Dict) and not node.keys:
        return True, "{}"
    return False, ""


def src(node, lines):
    try:
        return ast.get_source_segment("\n".join(lines), node) or ""
    except Exception:
        return ""


def scan_file(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [{"file": str(path), "pattern": "PARSE_ERROR", "detail": str(exc)}]
    lines = text.splitlines()
    hits = []

    class V(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            fn = node.func
            fname = getattr(fn, "id", None) or getattr(fn, "attr", None)

            # (a) getattr with falsy default
            if fname == "getattr" and len(node.args) == 3:
                attr = node.args[1]
                attr_name = attr.value if isinstance(attr, ast.Constant) else None
                falsy, dtxt = is_falsy_default(node.args[2])
                if falsy and isinstance(attr_name, str):
                    hits.append({
                        "file": str(path.relative_to(EXPERIMENTS)),
                        "line": node.lineno,
                        "pattern": "a_getattr_falsy_default",
                        "attr": attr_name,
                        "default": dtxt,
                        "attr_in_installed_api": attr_name in API_NAMES,
                        "flopscope_shaped": attr_name in FLOPSCOPE_HINT_ATTRS,
                        "src": src(node, lines)[:220],
                        "line_text": lines[node.lineno - 1].strip()[:220],
                    })

            # (b) reducer over comprehension/generator
            if fname in {"any", "all", "sum", "max", "min", "len"} and node.args:
                a0 = node.args[0]
                if isinstance(a0, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
                    has_if = bool(getattr(a0, "generators", []) and
                                  any(g.ifs for g in a0.generators))
                    hits.append({
                        "file": str(path.relative_to(EXPERIMENTS)),
                        "line": node.lineno,
                        "pattern": "b_reducer_over_comprehension",
                        "reducer": fname,
                        "filtered": has_if,
                        "src": src(node, lines)[:220],
                        "line_text": lines[node.lineno - 1].strip()[:220],
                    })
            self.generic_visit(node)

        def visit_Attribute(self, node: ast.Attribute):
            # (c) attribute access on something named op/rec/budget/ctx/mlp
            base = node.value
            bname = getattr(base, "id", None) or getattr(base, "attr", None)
            if bname in {"op", "rec", "record", "budget", "ctx", "mlp", "oprec"}:
                if node.attr not in API_NAMES:
                    hits.append({
                        "file": str(path.relative_to(EXPERIMENTS)),
                        "line": node.lineno,
                        "pattern": "c_attr_not_in_installed_api",
                        "base": bname,
                        "attr": node.attr,
                        "line_text": lines[node.lineno - 1].strip()[:220],
                    })
            self.generic_visit(node)

    V().visit(tree)
    return hits


def main():
    files = sorted(p for p in EXPERIMENTS.rglob("*.py")
                   if "__pycache__" not in p.parts and p.parent != HERE)
    all_hits = []
    for f in files:
        all_hits.extend(scan_file(f))
    out = {
        "files_scanned": len(files),
        "hits": all_hits,
        "counts": {},
    }
    for h in all_hits:
        out["counts"][h["pattern"]] = out["counts"].get(h["pattern"], 0) + 1
    (HERE / "scan_raw.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("files scanned:", len(files))
    print("counts:", json.dumps(out["counts"], indent=1))

    print("\n=== (a) getattr falsy default, attribute NOT in installed API ===")
    for h in all_hits:
        if h["pattern"] == "a_getattr_falsy_default" and not h["attr_in_installed_api"]:
            print(f"{h['file']}:{h['line']}  attr={h['attr']!r} default={h['default']}")
            print("     ", h["line_text"])

    print("\n=== (c) attr on op/budget/ctx/mlp not in installed API ===")
    seen = set()
    for h in all_hits:
        if h["pattern"] == "c_attr_not_in_installed_api":
            k = (h["file"], h["base"], h["attr"])
            if k in seen:
                continue
            seen.add(k)
            print(f"{h['file']}:{h['line']}  {h['base']}.{h['attr']}")


if __name__ == "__main__":
    sys.exit(main())
