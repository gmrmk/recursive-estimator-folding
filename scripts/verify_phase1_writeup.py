"""Re-derive every load-bearing number in the Phase-1 write-up from committed artifacts.

Stdlib only, no network, reads nothing outside the corpus.  Exit 0 if every
assertion holds, 1 otherwise.  This exists because four numbers in this document
were stated above their earned level on 2026-08-11/12 and each was caught by
reading a primary artifact rather than by care.  Care does not scale; this does.

Usage:  python scripts/verify_phase1_writeup.py [path-to-writeup.md]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DOC = ROOT / "corpus/whestbench/core/PHASE1_WRITEUP_DRAFT_20260808.md"
EXP = ROOT / "corpus/whestbench/experiments"

failures: list[str] = []
checks = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global checks
    checks += 1
    if not ok:
        failures.append(f"{name}: {detail}")
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  -- {detail}" if detail else ""))


def close(a: float, b: float, rel: float = 5e-3) -> bool:
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-30)


def load(rel: str):
    p = EXP / rel if not rel.startswith("/") else Path(rel)
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    doc_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DOC
    doc = doc_path.read_text(encoding="utf-8", errors="replace")

    print("== structural invariants (the recurring failure modes) ==")

    # The kill-count heading disagreed with its own table for two drafts.
    m = re.search(r"### 3\. Falsification ledger.*?\n(.*?)\n### 3b", doc, re.S)
    if m:
        rows = len(re.findall(r"^\| (?:N\d|M\d|N8[abc])", m.group(1), re.M))
        head = re.search(r"### 3\. Falsification ledger — (\w+) predeclared kills", doc)
        words = {"eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
        stated = words.get(head.group(1)) if head else None
        check("kill heading matches table row count", stated == rows,
              f"heading says {stated}, table has {rows}")

    # "Zero fitted constants" was published and false.  It must never return as a
    # live assertion -- but the document quotes it while withdrawing it, which is
    # the point of the errata, so only unmarked occurrences count.
    banned = ["no fitted constants", "zero fitted constants", "zero fitted structure",
              "correction-proof", "cannot overfit", "nothing tunable anywhere"]
    WITHDRAWN = re.compile(r"\bfalse\b|\bnot\b|withdraw|erratum|prior draft|earlier draft|"
                           r"v9 (?:said|asserted|claimed)|claimed", re.I)
    live = []
    lines = doc.splitlines()
    for i, line in enumerate(lines):
        for b in banned:
            if b.lower() in line.lower():
                window = " ".join(lines[max(0, i - 2):i + 3])
                if not WITHDRAWN.search(window):
                    live.append(f"{b!r} @L{i+1}")
    check("no banned absolute claims stated live", not live, f"found {live}")

    # E7 withdrew the unit-mixing ratio; it survived two drafts anyway.
    bare524 = len(re.findall(r"524x against adjusted", doc))
    check("withdrawn 524x not restated", bare524 == 0, f"{bare524} restatements")

    # The same quantity was printed as 340.7 in one section and 340.9 in another.
    ratios = set(re.findall(r"\*\*?340\.(\d)", doc))
    check("gap ratio stated consistently", ratios <= {"9"}, f"variants 340.{ratios}")

    print("\n== the seven development-selected constants, from the deployed MRO ==")
    src = (EXP / "v31_guards/package_source").read_bytes if False else None
    pkg = EXP / "v31_guards/package_source"
    kerdock = (pkg / "kerdock_v3_estimator.py").read_text(encoding="utf-8")
    base = (pkg / "base_estimator.py").read_text(encoding="utf-8")
    fold3 = (pkg / "fold3_estimator.py").read_text(encoding="utf-8")
    est = (pkg / "estimator.py").read_text(encoding="utf-8")

    def const(text: str, name: str) -> str | None:
        m = re.search(rf"^\s*{name}\s*=\s*([^\n#]+)", text, re.M)
        return m.group(1).strip() if m else None

    check("kerdock overrides n_base to 126*256", const(kerdock, "n_base") == "126 * 256")
    check("kerdock sets radial_conditioning True", const(kerdock, "radial_conditioning") == "True")
    check("phase window 2..128", (const(kerdock, "phase_start"), const(kerdock, "phase_stop")) == ("2", "128"))
    check("pilot_base 256", const(kerdock, "pilot_base") == "256")
    check("fold_pilot_base 1_024", const(kerdock, "fold_pilot_base") == "1_024")
    check("dead_alpha -2.0 inherited from base", const(base, "dead_alpha") == "-2.0")
    check("moment_tangent_lambda inherited", const(base, "moment_tangent_lambda") == "0.9807112198896164")
    # on_alpha is the seventh; it was omitted from the enumeration for two drafts.
    check("on_alpha 3.0 lives in fold3 and is NOT overridden",
          const(fold3, "on_alpha") == "3.0" and const(kerdock, "on_alpha") is None
          and const(est, "on_alpha") is None)
    check("shipping estimator adds no numeric constant",
          re.search(r"^\s*\w+\s*=\s*[-\d]", est.split("class Estimator")[1][:400], re.M) is None)
    check("document enumerates SEVEN selected constants",
          "on_alpha" in doc or "seven" in doc.lower(),
          "on_alpha absent from the write-up")

    print("\n== hosted anchor ==")
    try:
        led = load("a_series_granular_adversarial/a1_hosted_ledger.json")
        rows = led if isinstance(led, list) else led.get("rows", led.get("entries", []))
        walls = [r.get("wall_ms", r.get("wall_s", 0) * 1000) for r in rows if isinstance(r, dict)]
        if walls:
            check("hosted rows == 50", len(walls) == 50, f"{len(walls)} rows")
            check("hosted mean wall ~5.75 s", close(sum(walls) / len(walls) / 1000, 5.75, 2e-2),
                  f"{sum(walls)/len(walls)/1000:.4f} s")
            check("hosted max wall ~6.80 s", close(max(walls) / 1000, 6.80, 2e-2),
                  f"{max(walls)/1000:.4f} s")
    except Exception as exc:  # noqa: BLE001
        check("hosted ledger readable", False, repr(exc))

    print("\n== component ablations, error against bill ==")
    try:
        wc1 = load("wc1_winner_ablation/wc1_results.json")
        arms = wc1["arms"]
        # Compare numerically.  A substring test on 0.2510889... does not contain
        # "0.25109", which is how this check failed on its first run.
        prune = abs(arms["A_prune"]["component_billed_frac_of_B"])
        fold = abs(arms["A_fold"]["component_billed_frac_of_B"])
        check("pruning saving 25.109% of B", close(prune, 0.25109, 1e-4), f"{prune:.7f}")
        check("folding saving 4.828% of B", close(fold, 0.048279, 1e-4), f"{fold:.7f}")
        blob = json.dumps(wc1)
        check("isolated frame factor 2.016433", "2.016433" in blob or "2.01643" in blob)
        check("residual radial factor 1.0618308", "1.061830" in blob or "1.06183" in blob)
    except Exception as exc:  # noqa: BLE001
        check("wc1 results readable", False, repr(exc))

    print("\n== the design-axis closure ==")
    from fractions import Fraction as F
    lhs = F(2) + F(129 - 1, 128)
    rhs = F(3 * 512 * 129, 256 * 258)
    check("degree-4 moment identity holds at m=129 exactly", lhs == rhs, f"{lhs} vs {rhs}")
    check("and fails at 126, 128, 130",
          all(F(2) + F(m - 1, 128) != F(3 * 512 * m, 256 * 258) for m in (126, 128, 130)))
    check("DGS antipodal 4-design floor is 65792", 2 * (257 * 256 // 2) == 65792)
    check("deployed design is 1280 points short", 65792 - 126 * 256 * 2 == 1280)
    try:
        s11 = load("s11_full129_breakeven/s11_results.json")
        b = json.dumps(s11)
        check("S11 isolated degree-4 gain ~0.176%", "0.17598" in b or "0.1759" in b)
        check("S11 break-even bar 2.3256%", "2.32558" in b)
        check("S11 matched-point control present", "control_random3frames" in b)
    except Exception as exc:  # noqa: BLE001
        check("s11 results readable", False, repr(exc))

    print("\n== ledger ==")
    led = json.loads((ROOT / "corpus/whestbench/headroom/fold_ledger.json").read_text(encoding="utf-8"))
    n = len(led["candidates"])
    check("ledger record count matches the document", f"{n}-record" in doc or str(n) in doc,
          f"ledger has {n}")

    print("\n== reproducibility citation actually resolves ==")
    # The citation may wrap onto a continuation line, so judge the URL together
    # with whatever immediately follows it rather than the first line alone.
    for m in re.finditer(r"github\.com/gmrmk/recursive-estimator-folding(\S*)((?:\s*\n\s+/\S+)?)", doc):
        tail = (m.group(1) + m.group(2)).strip()
        bare = not tail or tail.rstrip(".,)") == ""
        # An erratum that quotes the old bare citation while withdrawing it is fine.
        context = doc[max(0, m.start() - 220):m.start()]
        excused = re.search(r"erratum|earlier draft|withdraw|cited the bare", context, re.I)
        check("repo citation resolves to the evidence, not the default branch",
              (not bare) or bool(excused),
              "bare root: default branch lacks the papers, this write-up, and the 267-record ledger")
    for path in ("corpus/whestbench/papers", "corpus/whestbench/core/PHASE1_WRITEUP_DRAFT_20260808.md"):
        on_main = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"main:{path}"],
                                 capture_output=True).returncode == 0
        check(f"KNOWN: {path} absent on default branch", not on_main,
              "present on main -- citation guidance may be stale" if on_main else "as expected")

    print(f"\n{checks - len(failures)}/{checks} checks passed")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
