# Submit-readiness checks (2026-08-08): wall safety PASS, billing levers surveyed

Two checks run while the upload is blocked on the user. Both are things that
would have been expensive to discover after spending a submission.

## 1. Wall-clock safety: PASS (this de-risks the submission)

The grader caps each MLP at **60 s** and runs participant code on **1 core
(2 vCPU)**; our local box has 16. If Kerdock overran the cap the submission
would fail outright — and a failed designated submission would be
catastrophic in the private re-run.

Measured from the T4 run (100 MLPs, local):

| candidate | wall mean | wall max | backend | overhead | residual mean / max |
|---|---:|---:|---:|---:|---:|
| Kerdock v3 | 2.86 s | **4.11 s** | 2.36 s | 0.42 s | 0.080 s / 0.137 s |
| two-axis L2 | 4.99 s | 6.96 s | — | — | 0.200 s / 0.271 s |

Kerdock's worst network finishes in 4.11 s against a 60 s cap — a **14.6x
margin**. The dominant term is flopscope backend time (2.36 s), and the
grader gives the backend **7 cores**, so it is not the part exposed to the
1-core pin. Even a 3-4x slowdown of the participant-side portion leaves the
cap untouched. Corroboration from the hosted side: our own #318609 ran ~1.0 s
per MLP on the grader against ~similar local timings.

Residual is also small and already inside our scored C: max 0.137 s = 1.37e10
FLOP-equivalents = 5.0% of budget. A tightening of residual accounting (the
scenario the rules reserve, RULES_V12_ANALYSIS §2) would cost us at most that
5%, while costing 22-47 s/MLP entries their entire run.

## 2. Billing-lever survey: no honest discount available to our family

The organizers state the FLOP model "gives favorable treatment to flopscope
primitives," which invites a search for primitives billed cheaply relative to
their statistical value. Surveyed the installed flopscope 0.10.0 API:

- `flopscope.numpy.fft._free` — **false lead**. Despite the filename it
  covers only utility ops (`fftfreq` n FLOPs, `fftshift` numel FLOPs), not
  free transforms.
- `flopscope._accumulation` — "Symmetry-aware einsum accumulation cost."
  Real discount, but it applies to **symmetric contractions** (the
  `W^T V W` sandwich of covariance propagation, ~2x). Our M178/M179 closure
  work already used `as_symmetric()` tags — and T2 killed the closure family
  as an estimator (bias 9.6e-5, 46x outside the boundary). No symmetry exists
  in the dense `X @ W` sampling matmuls that dominate Kerdock's cost.
- `linalg` decompositions, `stats` special functions: billed at analytical
  cost (erf/exp at 32 FLOPs/element) — these are billing *penalties*, not
  discounts, for our op mix.
- Bit-packing (32 bools per billed FLOP, organizer-sanctioned) applies to
  mask bookkeeping, which is not a material share of our bill.

Conclusion: our estimator family is already expressed in the primitives that
bill most favourably for it, and there is no unexploited legal discount. This
closes the "favorable primitives" question that the N-series had not directly
addressed.

## Status

Kerdock v3 is **cleared to submit**: validator-passed, 14.6x wall margin,
5% residual exposure, zero measured final-layer bias (N8c), and hosted
expectation ~9.8e-8 (C1). The upload is the only remaining step and is the
user's to perform.
