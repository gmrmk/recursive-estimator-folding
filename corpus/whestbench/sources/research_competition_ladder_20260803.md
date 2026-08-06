# Live competition ladder and rules audit — 2026-08-03

Accessed 2026-08-03. This file preserves the web lookup used to reassess the
frozen tangent candidate before any private submission.

## Official challenge page

Source: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026

- Phase II final-submission window: 2026-08-01 through 2026-09-19.
- Final evaluation/due diligence: 2026-09-20 through 2026-09-30.
- Results announcement: 2026-10-01.
- Phase-II Best Score prizes: USD 50,000 / 20,000 / 10,000.
- Algorithmic Contribution prize: USD 20,000.
- LLM assistance is explicitly allowed but must be honestly disclosed.
- FlopScope or accounting manipulation is explicitly prohibited.

## Public leaderboard

Source: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

The search index exposed the Phase-I public ladder. Leading rows included:

| Rank | Participant | Adjusted score | Final-layer MSE |
|---:|---|---:|---:|
| 1 | SKIBIDI_TOILET | 9.2e-9 | 9.24e-8 |
| 2 | williawa | 1.92e-8 | 1.925e-7 |
| 3 | joe_wanza | 2.77e-8 | 2.667e-7 |
| 4 | andrei_bulzan | 4.90e-8 | 1.189e-7 |
| 5 | abhinav_gorrepati | 5.23e-8 | 2.601e-7 |

The frozen tangent candidate's matched WHestBench 0.14 dev20 adjusted score is
2.77486e-7. Cross-dataset rank projection is not valid, but the order-of-
magnitude gap means the current candidate is not evidenced as a Best Score
contender. It remains a clean Algorithmic Contribution/fallback candidate.

## Townhall

Source: https://discourse.aicrowd.com/t/townhall-summary-recording/18078

- Participants may submit throughout Phase II and designate one final entry;
  designation locks at the actual Phase-II deadline.
- Only final-layer MSE is scored.
- Prize eligibility requires OSI-approved source release.
- LLM use is permitted and must be disclosed.

## Consequence

Do not equate the clean tangent-control improvement with proof of a winning
score. Preserve the frozen archive unchanged while researching public top-entry
methods and constructing a separate score-oriented candidate under a new,
explicit firewall. The untouched organizer private rerun remains the only
decisive test.
