# Public Discourse companion post (tact-scoped) — for review before posting

TITLE: [Phase 1 write-up] The non-Gaussianity wall at depth 32, measured
with certificates — and a falsification-ledger methodology (submission
#326094)

BODY (markdown):

The complete technical write-up (PDF) for submission **#326094** is filed
via the organizers' email channel. This public companion shares the two
results we believe are most useful to the community.

**1. The non-Gaussianity wall, measured with certificates.** Moment and
cumulant propagation is the natural white-box approach. We built it to the
strongest form we could certify — an exact zero-order full-covariance
Gaussian recurrence through all 32 layers (Owen-T/Phi2 pair moments with
per-call enclosure certificates; assembly agreeing with 30-digit references
to ~2e-9) — and measured where it lands at depth 32 against 400k-sample
Monte-Carlo truth:

- diagonal Gaussian closure: 7.18e-4 bias MSE
- exact full-covariance Gaussian closure: 9.61e-5
- a budget-matched sampling estimator: ~2.5e-7

Making the covariance exact buys ~7.5x over the diagonal closure; the
remaining ~340x is third-and-higher-cumulant structure that no
Gaussian-moment closure can represent at any compute multiplier. The
practical corollary we found sharpest: exact Gaussian structure pays when
SUBTRACTED (as a control) and fails when PREDICTED (as an estimator).

**2. A falsification-ledger methodology.** Every proposed improvement was
predeclared with a mechanism, a prediction, and a kill gate before
implementation; kills are final; the record is append-only (240+ entries).
Two extensions this week that we think generalize: (a) an
adversarial-closure pass — independent agents whose explicit mandate was to
BEAT the submission, each failure leaving a named obstruction on the record
rather than a shrug — so the optimality claim is earned by attack instead
of self-assessed; and (b) a graveyard re-measurement pass, re-reading every
historical kill against changed premises (tool repricings, corrected
statistics) and re-running the strongest sixteen: ten converted from
assumption to measured kill, honest dispositions for the rest. Both
practices are cheap relative to the compute they save.

(Estimator summary for context: a structured spherical design with exact
radial conditioning and structural pruning; the full construction,
measurements, and ledger are in the filed PDF.)

TACT SCOPE (withheld deliberately): design family/constants and component
recipe; S17 floor arithmetic and S(B) numbers; dispersion/decision-layer
statistics; the seed-side open question; all graveyard revival specifics;
anything competitor-facing. The full write-up goes to the judges privately.
