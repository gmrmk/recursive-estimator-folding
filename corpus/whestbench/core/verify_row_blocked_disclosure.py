"""Re-derive the frozen-scalar disclosure for the DEPLOYED row_blocked host from source.

Stdlib only.  Reads `experiments/row_blocked_production/candidate_source/` as text,
parses it with `ast` and `tokenize`, and never imports it -- the estimator modules
pull in `flopscope` and `whestbench`, and this check must not touch the harness.
Run it with `-B` so no bytecode is written into a read-only tree.

This exists because the committed estimator section describes the `kerdock_v3` MRO
and was cited about this host, and because a false fitted-structure claim shipped
twice on that lineage.  Every number in the disclosure is re-derived here, and any
numeric constant in the fitted surface that the disclosure does not declare is a
failure -- silence is the failure mode this file exists to catch.

Usage:  python -B core/verify_row_blocked_disclosure.py [path-to-disclosure.md]
"""

from __future__ import annotations

import ast
import io
import re
import sys
import tokenize
from pathlib import Path

CORE = Path(__file__).resolve().parent
WHESTBENCH = CORE.parent
SRC = WHESTBENCH / "experiments/row_blocked_production/candidate_source"
KERDOCK_SRC = WHESTBENCH / "experiments/v31_guards/package_source"
DEFAULT_DOC = CORE / "SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819.md"

# The deployed method-resolution order, most-derived first.  Attribute lookup walks
# this list in order; the first definition wins.
MRO = ["estimator.py", "orthogonal_fold3.py", "fold3_estimator.py", "base_estimator.py"]
# Modules reached from the deployed path but not part of the class chain.
HELPERS = ["fold_estimator.py", "row_blocked_winograd.py", "cost_model.py"]

# --- what the disclosure declares -------------------------------------------------
# name -> (source text of the value, file that must own the winning definition)
DECLARED_SCALARS = {
    "n_base": ("126 * 256", "estimator.py"),
    "pilot_base": ("256", "orthogonal_fold3.py"),
    "fold_pilot_base": ("1_024", "orthogonal_fold3.py"),
    "dead_alpha": ("-2.0", "base_estimator.py"),
    "on_alpha": ("3.0", "fold3_estimator.py"),
    "moment_tangent_lambda": ("0.9807112198896164", "base_estimator.py"),
}
DECLARED_SWITCH = {"radial_conditioning": ("True", "orthogonal_fold3.py")}
# Values written in the tree that the MRO shadows.  Quoting one of these as deployed
# is the exact error the kerdock_v3 repair made.
DECLARED_SHADOWED = {
    ("n_base", "fold3_estimator.py"): "14_000",
    ("n_base", "base_estimator.py"): "14_000",
    ("radial_conditioning", "base_estimator.py"): "False",
    ("pilot_base", "base_estimator.py"): "256",
    ("fold_pilot_base", "fold3_estimator.py"): "1_024",
}
DECLARED_MODULE_CONSTANTS = {("BLOCK_ROWS", "row_blocked_winograd.py"): "8192"}

# Every NUMBER token the disclosure declares, per file.  Anything else is undeclared.
DECLARED_LITERALS = {
    "estimator.py": {"126", "256", "2"},
    "orthogonal_fold3.py": {"256", "1_024", "0.5", "1.0", "2.0"},
    "fold3_estimator.py": {
        "0", "1", "2", "3", "0.0", "0.5", "1.0", "2.0", "3.0", "1_024",
        "14_000",                                    # shadowed n_base
        "257.0", "66563.0", "2600.0", "537689.0",    # unreachable radial reweight
    },
    "base_estimator.py": {
        "0", "1", "2", "3.0", "0.0", "0.5", "1.0", "2.0", "1e-12", "32",
        "256", "14_000", "0.9807112198896164",
        "257.0", "66563.0", "2600.0", "537689.0",
    },
    "fold_estimator.py": {"0", "0.0"},
}

# Claims that must never appear live in this document.  The first six are the
# kerdock_v3 inheritance; the last four are false about this host specifically.
BANNED = [
    "no fitted constants", "zero fitted constants", "zero fitted structure",
    "correction-proof", "cannot overfit", "nothing tunable anywhere",
    "phased-hadamard", "exact spherical 2-design", "phase_start", "phase_stop",
]
WITHDRAWN = re.compile(
    r"\bfalse\b|\bnot\b|\bno\b|withdraw|erratum|prior draft|earlier draft|does not|"
    r"do not|never|absent|wrong|banned|fails on|committed section|kerdock",
    re.I,
)

failures: list[str] = []
checks = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global checks
    checks += 1
    if not ok:
        failures.append(f"{name}: {detail}")
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  -- {detail}" if detail else ""))


def read(fname: str, root: Path = SRC) -> str:
    return (root / fname).read_text(encoding="utf-8")


def class_attrs(src: str) -> dict[str, str]:
    """Class-body scalar assignments, as the exact source text of the value.

    `ast.unparse` normalises `1_024` to `1024`, so the raw segment is used instead --
    the disclosure quotes source text, and the check must compare what it quotes.
    """
    out: dict[str, str] = {}
    tree = ast.parse(src)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
                continue
            target = stmt.targets[0]
            if not isinstance(target, ast.Name):
                continue
            out[target.id] = ast.get_source_segment(src, stmt.value) or ""
    return out


def module_consts(src: str) -> dict[str, str]:
    out: dict[str, str] = {}
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id.isupper():
                out[target.id] = ast.get_source_segment(src, node.value) or ""
    return out


def literals(src: str) -> set[str]:
    return {
        tok.string
        for tok in tokenize.generate_tokens(io.StringIO(src).readline)
        if tok.type == tokenize.NUMBER
    }


def main() -> int:
    doc_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DOC
    doc = doc_path.read_text(encoding="utf-8", errors="replace")
    # Prose assertions are made against a whitespace-flattened copy: the document is
    # hard-wrapped at 80 columns, so a declared phrase can carry a newline in the
    # middle and a naive substring test then fails on formatting, not on content.
    flat = re.sub(r"\s+", " ", doc)
    sources = {f: read(f) for f in MRO + HELPERS}
    attrs = {f: class_attrs(sources[f]) for f in MRO}

    print("== the deployed MRO resolves where the disclosure says it does ==")
    for name, (value, owner) in {**DECLARED_SCALARS, **DECLARED_SWITCH}.items():
        winner = next((f for f in MRO if name in attrs[f]), None)
        check(
            f"{name} resolves in {owner} as {value}",
            winner == owner and attrs.get(owner, {}).get(name) == value,
            f"resolved in {winner} as {attrs.get(winner, {}).get(name)!r}",
        )

    print("\n== shadowed definitions are still where the disclosure says, unchanged ==")
    for (name, fname), value in DECLARED_SHADOWED.items():
        check(
            f"{fname} still writes {name} = {value} (shadowed)",
            attrs[fname].get(name) == value,
            f"found {attrs[fname].get(name)!r}",
        )

    print("\n== no undeclared class attribute anywhere in the MRO ==")
    known = set(DECLARED_SCALARS) | set(DECLARED_SWITCH)
    for fname in MRO:
        extra = sorted(set(attrs[fname]) - known)
        check(f"{fname} introduces no undeclared class attribute", not extra, f"{extra}")

    print("\n== module constants ==")
    for (name, fname), value in DECLARED_MODULE_CONSTANTS.items():
        found = module_consts(sources[fname]).get(name)
        check(f"{fname}: {name} = {value}", found == value, f"found {found!r}")
    # Cross-host: the committed section's 4,096 belongs to kerdock_v3, not here.
    kerdock_block = KERDOCK_SRC / "row_blocked_winograd.py"
    if kerdock_block.exists():
        other = module_consts(kerdock_block.read_text(encoding="utf-8")).get("BLOCK_ROWS")
        check(
            "kerdock_v3 host still carries a DIFFERENT BLOCK_ROWS",
            other is not None and other != DECLARED_MODULE_CONSTANTS[("BLOCK_ROWS", "row_blocked_winograd.py")],
            f"kerdock BLOCK_ROWS = {other!r}",
        )

    print("\n== no undeclared numeric constant in the fitted surface ==")
    for fname, allowed in DECLARED_LITERALS.items():
        found = literals(sources[fname])
        undeclared = sorted(found - allowed)
        missing = sorted(allowed - found)
        check(f"{fname}: every literal is declared", not undeclared, f"undeclared {undeclared}")
        check(f"{fname}: every declared literal still exists", not missing, f"vanished {missing}")

    print("\n== the carrier is Haar frames by QR from ctx.seed, not a frozen design ==")
    of3 = sources["orthogonal_fold3.py"]
    check("frames come from QR of a Gaussian", "fnp.linalg.qr(raw)" in of3)
    check("seeded per network by ctx.seed", "default_rng(ctx.seed)" in of3)
    check("radius is computed from width, not stored", "math.lgamma" in of3)
    absent = ["kerdock", "hadamard", "phased", "phase_start", "phase_stop", "mub"]
    for token in absent:
        hits = [f for f in MRO + HELPERS if token in sources[f].lower()]
        check(f"token {token!r} absent from the whole tree", not hits, f"present in {hits}")

    print("\n== the unreachable branches really are unreachable ==")
    # base_estimator.setup is dead because orthogonal_fold3.setup does not chain up.
    of3_setup = re.search(r"def setup\(self, ctx\)[^\n]*\n(.*?)(?=\n    def |\Z)", of3, re.S)
    check(
        "orthogonal_fold3.setup does not call super().setup",
        of3_setup is not None and "super().setup" not in of3_setup.group(1),
        "chaining up here would make the Sobol/Owen carrier live",
    )
    check(
        "estimator.setup DOES chain up (so the QR carrier runs)",
        "super().setup(ctx)" in sources["estimator.py"],
    )
    # base_estimator.predict is dead because fold3 defines its own.
    check(
        "fold3_estimator overrides predict",
        "def predict(" in sources["fold3_estimator.py"]
        and "def predict(" in sources["base_estimator.py"],
    )
    # The radial-reweight branch is the else of `if self.radial_conditioning:`.
    for fname in ("fold3_estimator.py", "base_estimator.py"):
        body = sources[fname]
        guard = body.find("if self.radial_conditioning:")
        q1 = body.find("257.0")
        check(
            f"{fname}: 257.0 sits inside the radial_conditioning else-branch",
            guard != -1 and q1 > guard,
            f"guard@{guard} literal@{q1}",
        )
    check(
        "deployed multiply() uses batched_candidate_bill, not candidate_bill",
        "batched_candidate_bill(m, k, n)" in sources["row_blocked_winograd.py"]
        and re.search(r"[^_]\bcandidate_bill\(", sources["row_blocked_winograd.py"]) is None,
    )

    print("\n== the document declares exactly what the source resolves ==")
    row = re.compile(r"^\| `([a-z_]+)` \| `([^`]+)` \| `([a-z_0-9]+\.py)` \|", re.M)
    tabled = {m.group(1): (m.group(2), m.group(3)) for m in row.finditer(doc)}
    check(
        "document tables the six selected scalars",
        set(tabled) >= set(DECLARED_SCALARS),
        f"tabled {sorted(tabled)}",
    )
    for name, (value, owner) in DECLARED_SCALARS.items():
        check(f"document row for {name} matches source", tabled.get(name) == (value, owner),
              f"document says {tabled.get(name)}")
    check("document states the count as six scalars", "six scalars" in doc)
    for literal in sorted(set().union(*DECLARED_LITERALS.values()) | {"8192"}):
        if len(literal) > 1:  # single digits are ambient in prose
            check(f"document mentions literal {literal}", literal in doc)

    print("\n== the host-confusion disclosure and the standing clauses ==")
    check("names the kerdock_v3 section and says it does not apply",
          "SECTION_ESTIMATOR_AND_CONSTANTS_20260812.md" in flat
          and "does not apply to this host" in flat)
    check("states the carrier as Haar frames", "Haar" in flat and "QR" in flat)
    check("discloses that n_base is selected here and forced on kerdock_v3",
          "forced on one lineage and selected on the other" in flat)
    check("carries the F7 forward clause with all three surfaces",
          all(s in flat for s in ("F7", "proxy choice", "selection-of-8", "frame count")))
    check("full.json numbers, if ever added, carry the repair caveat",
          ("full.json" not in flat) or ("pending round-4 bill repair re-run" in flat))
    live = []
    lines = doc.splitlines()
    for i, line in enumerate(lines):
        for b in BANNED:
            if b in line.lower():
                window = " ".join(lines[max(0, i - 2):i + 3])
                if not WITHDRAWN.search(window):
                    live.append(f"{b!r} @L{i+1}")
    check("no banned claim stated live", not live, f"found {live}")

    print(f"\n{checks - len(failures)}/{checks} checks passed")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
