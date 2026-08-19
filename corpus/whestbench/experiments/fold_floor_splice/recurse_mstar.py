"""The /headroom-recursion engine run, specifically: derive the fold's break-even
residual multiplier m* as an independent second signal on the m-curve, via the
TRM recursive-refinement ladder over the claude CLI transport (no API key)."""
import json
from headroom_recursion import recurse, RecurseConfig, CLITransportClient

PROBLEM = """Exact derivation task. Show all arithmetic; give final answers to 4 significant figures.

Setup: a competition score is S = M * (C/B) with M fixed (the candidate is an exact
arithmetic reschedule, raw MSE unchanged), B = 272e9. Per-network cost law:
C = A + 1e11 * r, where A is analytical FLOPs and r is residual wall seconds.
Incumbent (the max-C network): A_inc = 203.59e9, C_inc = 222.405e9.
Folded candidate: A_new = 126.7e9; its residual is r_new = m * r_inc for an unknown
multiplier m >= 1, where r_inc is the incumbent's residual implied by the numbers above.

(a) Compute r_inc exactly from the setup. Derive C_new(m) and the score ratio
    S_new/S_inc as a function of m.
(b) Solve for the break-even m* where S_new = S_inc.
(c) Evaluate S_new/S_inc at m = 1, m = 2, m = 3.
(d) A public measurement of Strassen-Winograd recursion overhead reports, per sample:
    depth-2 residual-equivalents 2,662; depth-5 residual-equivalents 432,427. Assuming
    residual grows geometrically in recursion depth at the rate these two points imply,
    estimate the naive depth-6 residual-equivalents per sample, the implied multiplier
    relative to depth-2, and state clearly whether a NAIVE depth-6 transcription clears
    the m* from (b) - and therefore what an implementation must do instead (one sentence)."""

client = CLITransportClient(attempts=2, timeout_s=300.0)
cfg = RecurseConfig(n=3, T=2, halt_threshold=0.85)
trace = recurse(PROBLEM, client=client, config=cfg)
out = {
    "answer": trace.answer if hasattr(trace, "answer") else str(trace),
    "tiers": getattr(trace, "tier_path", None) or getattr(trace, "tiers", None),
    "calls": getattr(trace, "total_calls", None),
    "halted": getattr(trace, "halted", None),
}
print(json.dumps(out, default=str)[:6000])
