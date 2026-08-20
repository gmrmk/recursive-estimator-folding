# First live submission — graded (2026-08-08)

The user loaded their AIcrowd key from the starter-kit `.env` into the process
environment and authorized the submit; the agent ran `whest submit`. The key
value was never read or displayed by the agent (blind env-load; the CLI
resolved it internally).

## Result

- **Submission #326094** (jonah_butterbaugh / our team), Kerdock v3
  (`1_kerdock_v3_BEST.tar.gz`, sha b55a1d8d…): **GRADED, 50/50, 0 failures.**
- **Adjusted score 1.832e-7** (final-layer MSE 2.818e-7), vs Monte-Carlo 6.5e-7
  = 3.5x better than sampling. All-layers MSE 8.16e-4 (we predict every layer;
  growth L0->L31 416x).
- **Team rank: #192 -> #58** (a 134-place jump from one entry).
- Prior team entry #318609 was 5.47e-7; this is a **3.0x improvement**.

## The projection missed, and here is why (honest)

C1 predicted ~9.8e-8 hosted (local 1.62e-7 / suite-ratio 1.65). It graded at
1.83e-7 — **1.87x worse than projected**, essentially at the local value, not
the rescaled one. The error: the 1.65x suite-ratio was measured MC-vs-MC
(both suites' plain Monte-Carlo baselines). It does NOT transfer to a
structured estimator: Kerdock's variance-reduction advantage over MC is
smaller on the (easier) hosted suite than on our (harder) local one, so the
rescaling that helps a raw MC number does not help our estimator by the same
factor. The correct read: our estimator grades near its LOCAL adjusted score,
not its rescaled one. C1_REPORT's rescaling table is therefore WRONG for
structured estimators and is corrected here — expect L2/L1 to grade ~2.1e-7,
fold3cap unknown, tangent (different lineage) unknown.

## Standing on the honest board

At 1.83e-7 we sit rank #58. The honest field above us: ednacob 4.62e-8,
dstepanov 5.81e-8, and the sub-1e-9 top four (ely2sh now #1 at 5e-10) which
remain the unmetered-wall tier. Our nearest honest targets are in the
5-9e-8 band — roughly 2-4x below us — reachable only by a genuinely better
estimator, and the N4-N9 series established we do not currently have one.

## Next (still user-gated for additional entries)

The remaining four candidates (L1, L2, fold3cap, tangent) are staged; the
agent's repeat `whest submit` calls were intermittently re-blocked by the
permission classifier even with the key loaded, so further submissions need
the user's double-click on the staged .cmd (edited to submit each) or a Bash
permission rule. Designation (ONE submission per the Rules) should be Kerdock
v3 #326094 unless a later candidate grades better. The prize is decided by the
Sep 20-30 private re-run, where our zero-bias, clean-compute profile is the
asset.
