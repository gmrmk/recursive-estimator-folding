# M230 predeclaration -- M223 live marginal-sigma gather seam

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_CODE_AND_TESTS`.

M230 changes one mechanism only: replace M228's Python-loop construction of
two marginal singleton-sigma columns with an inclusive FlopScope-metered
vector gather from a pre-existing, live M223/M179 diagonal marginal-sigma
vector. The gather must consume frozen event label indices and execute inside
the same raw timer and `BudgetContext` as M228's unchanged 171-call kernel.
No caller setup, label packing, gather, allocation, or sigma derivation is
free.

This mutation is conditional. The current M223 caller must actually retain and
expose one float64 vector whose elements are exactly `sqrt(C_ii)` for its live
layer/epoch. It must be the same object passed to M230, not a reconstructed,
copied, conditional, pair, or later-epoch substitute. If this is absent,
M230 stops as `SEAM_PROTOTYPE_INTEGRATION_BLOCKED`; it receives no reuse,
wall, or integrated-cost credit and does not run a target trace.

M224 math is frozen: parent code SHA256
`6ABA2D0AB618FF5D678977CC07FC89962C09092B537AAFFC282E069C10DFDA7B`,
`|rho|<=.08`, 16 Phi terms, 32 Simpson panels, event radii, 31x128 shape,
context seeds `221730001..221730031`, and outer seeds
`221720001..221720005`. The raw wall threshold remains
`0.016133916999970098` seconds and speedup remains strictly over 100x.

If and only if the live-vector preflight passes, label packing and two gathers
are charged in the inclusive ledger before M228 compute; no 171-call or
`5467N` kernel operation may be changed. Exact M224 values, radius, chart,
layer, epoch, context object identity, vector object identity, and rejection
of copies/wrong epoch/conditional sigma substitution are prerequisite gates.
Responses, truth, scorer, MSE, challenge weights, leaderboard, and variance
remain prohibited.
