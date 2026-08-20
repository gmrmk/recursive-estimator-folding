# Rules v12 read in full (2026-08-08): the public leaderboard is not the prize

Primary source: the challenge's Official Rules v12 page, read directly.
Quotes verbatim. This is the authoritative document ("In the event of an
inconsistency between these Rules and the starter kit, these Rules govern").

## 1. Prize ranking comes ONLY from the Private Re-evaluation (§5.4)

> "This re-run produces the final (private) leaderboard, and prize ranking is
> decided **exclusively from this re-run — not from any score visible on the
> public leaderboard during the Competition**."

The Private Re-evaluation runs **Sept 20-30, 2026** on "a separate, fresh,
never-seen test suite ... generated from private seeds that were not used
during either Phase 1 or Phase 2." Tentative winners announced ~Oct 1.

Consequence: today's #1 (dpskv5, 4e-10) is a public-leaderboard artifact.
It is not the prize ranking, and it never will be.

## 2. ARC has explicit authority to close the accounting gap, and says
## exploiters get no protection (§5.3)

> "Sponsor reserves the right to make changes to flopscope, the scoring
> pipeline, the timing guards, the per-MLP FLOP budget, the wall-time
> conversion rate, or any other grader-side component when material issues
> (**incorrect FLOP accounting, exploitable measurement gaps**, scoring bugs,
> security or integrity holes, or significant performance bugs) are
> uncovered."

> "**Solutions that rely on a behavior subsequently identified as a bug have
> no expectation that the bug will be preserved.**"

> "Sponsor may at its discretion **re-grade previously submitted Solutions**
> under the corrected grader ... Re-grades initiated by Sponsor do not count
> against any Participant's daily submission cap."

And §5.2 prohibits submissions that "attempt to modify the flopscope
accounting library, change its internal parameters, or **otherwise circumvent
the budget enforcement described in §5.5**."

ARC has already exercised this once (Aug 3: flopscope v0.10.0, "cost-model
fixes, residual-time safeguards"). The latitude narrows over time but
survives into Phase 2 for "a flopscope accounting error that meaningfully
changes effective budget usage," and into the Private Re-evaluation for
changes "strictly required to complete" it — with any such change triggering
"re-running all affected designated submissions."

## 3. What this means for the goal, concretely

Our campaign's honest-only stance is not a self-imposed handicap; it is the
rules-aligned position, and it is the one that survives a correction. The
entries above us burn 22-47 s of wall per MLP while being charged as though
they burned ~0 (see HOSTED_INTEL §6). If the residual charge is applied as
documented (1e11 FLOP-equivalents/second), 40 s alone is 14.7x the entire
per-MLP budget — those runs would fail outright, scoring the zero-prediction
penalty. Our candidates run ~1-3 s, ~100% instrumented, and are unaffected by
any tightening of that measurement.

So the honest path to the top of the ranking that actually pays is:
1. Submit our best honest estimator now (Phase 1 closes ~Aug 10 per the
   announced extension; the rules' original table says Jul 31 and is
   superseded by the Competition Site).
2. Keep improving it through Phase 2 (ends Sep 19).
3. **Designate it.** The private re-run on fresh seeds decides everything.

## 4. Corrections to earlier campaign notes

- **Designation count: the Rules say ONE.** §5.3: "each Participant must
  designate one (1) submission for the Private Re-evaluation as described in
  §6." The site's official-facts panel says "up to two nominated submissions,
  per phase." The Rules govern on inconsistency — **plan for one**, and
  confirm on the designation page. (This supersedes HOSTED_INTEL §5.)
- **Phase-end standings use all 100 MLPs** (50 public + 50 private,
  §5.4) — the live leaderboard shows only the public half, so even the
  Phase-1 standing is not what today's board displays.
- Submission cap is **per Team**, 50/day, resetting 00:00 UTC.
- LLM-assisted Solution development is explicitly permitted (§5.7 ref).
- The rules' timeline table (Phase 1 ending Jul 31, Phase 2 starting Aug 1)
  is superseded by the announced extension; the Site shows Phase 1 LIVE and
  Phase 2 UPCOMING as of today.

## 5. Standing instruction unchanged

We do not use the wall-time channel. It is prohibited by §5.2's
circumvention clause on the most natural reading, it is under active review,
and the rules explicitly deny any expectation that it will be preserved. Our
edge is that a correction costs us nothing and costs the current top
approximately everything.
