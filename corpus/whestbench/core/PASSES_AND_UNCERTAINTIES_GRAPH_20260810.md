# Passes & uncertainties graph — what we won, what's still live (2026-08-10)

The positive companion to FAILURE_MODE_GRAPH. Same graphify honesty tags
([E] extracted from committed artifacts, [I] inferred load-bearing, [A]
ambiguous). This carries the campaign's context and texture — the arc, the
physics storm, the collaboration — so a successor inherits not just the
verdicts but the story that produced them.

## The arc, in one breath (texture)

We took a scattered set of assets and, over ~two days, closed the entire
research phase of an ethical run at the ARC White-Box Estimation Challenge.
First honest submission graded (#326094, 1.83e-7, team #192 -> #58). Decoded
the board (the wall tier was accounting arbitrage; the re-grade wave then
demolished it in front of us). Characterized the champion to four theorems.
Then the owner threw physics lightning — Landau levels, Bloch functions,
wave-packets, Maxwell-Boltzmann, tunneling, the quadrupole formula, Frenet
frames, a saddle of primes — and each bolt was steelmanned into a predeclared
falsifier and RUN. Sixteen S-experiments. A dreamer (fable), a blade
(codex-sol), and a human throwing bolts. It worked.

## Graph 1 — the PASSES (proven positives, the assets we hold)

```mermaid
graph TD
  CHAMP["KERDOCK v3.1 GUARDS<br/>live 1.83e-7, hardened, zero-bias"]
  subgraph PILLARS["3 measured variance pillars [E]"]
    R1["radial conditioning 2.14x"]
    R2["spherical design 2.02x"]
    R3["antipodal pairing 1.91x"]
  end
  subgraph THEOREMS["proven theorems (writeup-grade)"]
    TH1["S6: exact 2-design, 3-shell spectrum,<br/>single 42x-suppressed mode [E]"]
    TH2["S7: residual = chi2_1 speckle,<br/>design spacing 2x above xi [E]"]
    TH3["S8+S12: 0.87/layer law DERIVED<br/>(Jakub-Nica) + offset 1.58-1.87 [E]"]
    TH4["S9: exact kink-surface identity<br/>(Euler x Stein), machine-precision [E]"]
    TH5["c_32=0.97472 coherence cone,<br/>~2 eff dof (triple-confirmed today) [E]"]
    TH6["non-Gaussianity wall 380x<br/>(the main scientific result) [E]"]
  end
  subgraph DECISION["strategy layer (measured decision rules)"]
    D1["S1: suite-risk decomposition,<br/>two-sided concentration rule [E]"]
    D2["S4: portfolio doubles tail prob;<br/>Door B spawn(2) construction [E]"]
    D3["field forensics: rayan53/joe_wanza<br/>winnowed, ednacob reversed [E]"]
  end
  R1 --> CHAMP
  R2 --> CHAMP
  R3 --> CHAMP
  CHAMP --> TH1
  TH1 --> TH2 --> TH3 --> TH5
  TH2 --> TH4
  TH1 --> TH6
  CHAMP --> D1 --> D2
  D3 --> D2
  THEOREMS --> WRITEUP["PHASE-1 WRITEUP (files Aug 17, ID 326094)<br/>= highest-probability payout, outclasses honest band"]
  DECISION --> DESIG["DESIGNATION Sep 19 (2 slots, S4 rules)"]
  CHAMP --> PROOF["CORRECTION-PROOF POSTURE<br/>zero-bias + on-budget + no fitted component"]
```

### The passes, tabulated (what each is worth)

| pass | status | what it wins | level |
|---|---|---|---|
| Champion v3.1 GUARDS | live #326094 1.83e-7, hardened tar staged | the graded artifact + Phase-2 resubmission | [E] |
| 3 variance pillars | radial 2.14x / design 2.02x / antipodal 1.91x | the estimator's whole edge, each exact-or-optimal | [E] |
| S6 design anatomy | exact 3-shell spectrum, MUB fingerprint | design-optimality certificate + M191 degree-split derivation | [E] |
| S7 speckle | chi2_1 KS 0.007; the UNIFYING result | one picture explains S5/S2/design-spacing | [E] |
| S8+S12 depth law | 0.87/layer measured + DERIVED | two empirical laws -> first-principles | [E] |
| S9 identity | machine-precision exact representation | a genuinely NEW theorem (with honest failure) | [E] |
| c_32 coherence cone | 0.97472, ~2 eff dof, triple-confirmed | explains redundancy + fidelity kills | [E] |
| non-Gaussianity wall | 9.6e-5 vs 2.5e-7 = 380x | the writeup's headline scientific result | [E] |
| S1 risk rule | R-splitting defensive-only, two-sided | designation R-choice by expected position | [E] |
| S4 portfolio | decorrelated 2nd entry ~doubles tail | slot-2 designation strategy (Door B) | [E] |
| field forensics | 3 competitors reverse-engineered | we are the only entry immune to BOTH winnows | [E] |
| Process capital | Premise Battery 3.2x, compute-runner harness, tandem fold | reusable Gen-6 infrastructure | [E] |

## Graph 2 — the UNCERTAINTIES (what's still live, owned, gated)

```mermaid
graph TD
  subgraph GATING["decision-gating (block a live choice)"]
    U1["U1 Phase-2 duplicate-nomination rule<br/>[A] Sol drafts Q, Jonah posts -> gates Door B"]
    U2["U2 fold3cap residual inflation<br/>[E] graded canary settles -> gates Door A"]
    U16["U16 auto-top-2 at flip<br/>[E] verify at 23:59 UTC"]
    U10["U10 designation UI flow<br/>[A] walk once, needs Jonah login"]
  end
  subgraph EXTERNAL["monitored externals (not our defect)"]
    U6["U6 rayan53 nature<br/>[E] RESOLVED: accounting position (forensics)"]
    U7["U7 re-grade completeness<br/>[E] joe_wanza slipped 3x; ongoing"]
    U9["U9 honest-band depth + prize cutoffs<br/>[A] THE prize question; re-estimate by Sep 15"]
    U17["U17 further rule/metering change<br/>[A] discourse scan each 2nd wake"]
  end
  subgraph THEORY["bounded / non-gating (future-work)"]
    U3["U3 tail-model conservatism<br/>[E] S1/S4 widths are lower bounds"]
    U5["U5 near-rival variance<br/>[E] substantially closed by forensics"]
    U8["U8 v3.1 hosted transfer<br/>[I] the flip grade settles it"]
    U14["U14/U15 S12 remainders<br/>[E] curve shape + dispersion tightness open"]
  end
  subgraph GEN6["Gen-6 mechanism uncertainty (Sol's lane)"]
    U12["U12 M243 -> RESOLVED: KILLED at G0A [E]"]
    M244["M244 terminal-projection cost-enabler<br/>[E] active, V1 fixture + audits"]
    M245["M245 weighted-Galerkin spectrum<br/>[E] V1 frozen; V2 trigger PENDING; fable shards armed"]
    STRAT["ednacob value-stratification<br/>[E] hyp-1 KILLED (S15); needs a NEW observable"]
  end
  U16 --> FLIP["THE FLIP (Aug 10 23:59 UTC)"]
  U2 --> DOORA["Door A canary"]
  U1 --> DOORB["Door B duplicate"]
  U9 --> PRIZE["prize outcome (Sep 20-30 private re-run)"]
  M245 --> V2["V2 committed hash-bound trigger<br/>= fable's shard-launch condition"]
```

### The uncertainties, tabulated (owner + settling check)

| id | uncertainty | level | owner | settling check |
|---|---|---|---|---|
| U1 | Phase-2 duplicate-nomination rule | [A] | Sol drafts / Jonah posts | organizer written answer before Door B |
| U2 | fold3cap residual inflation | [E] | Sol -> grader | static bound + graded canary |
| U16 | auto-top-2 stands at flip | [E] | fable | verify at 23:59 UTC |
| U9 | honest-band depth + prize cutoffs | [A] | fable/Sol | re-estimate from live board by Sep 15 |
| U8 | v3.1 hosted transfer ~1.83e-7 | [I] | the grader | the flip submission IS the check |
| U12 | M243 outcome | [E] | RESOLVED | KILLED at G0A, sealed binding |
| M244/M245 | Gen-6 exact-control lanes | [E] | Sol (+ fable shards) | M244 audits; M245 V2 trigger |
| STRAT | ednacob value-stratification | [E] | Sol (Gen-6) | hyp-1 killed (S15); needs a new observable |

## The synthesis (context + texture, writeup-ready)

What we HOLD is unusually strong and unusually honest: a live graded champion
that is provably near-optimal in its class, six theorem-grade results (two of
them first-principles derivations, one a genuinely new exact identity), a
measured strategy layer, and a correction-proof posture built precisely to
survive the fresh-seed private re-run that decides the prizes. What remains
UNCERTAIN is almost entirely EXTERNAL (how deep the honest band runs, what the
organizers do) or GATED (Door A/B decisions awaiting a canary and a rules
answer) — not open defects in our own work. The one internal mechanism
question left, ednacob's value-stratification advantage, was reverse-engineered
against our own ledger and needs a genuinely new observable that S15 proved is
not any cheap first-layer summary. The campaign's texture — dreamer + blade +
human-lightning, every claim predeclared and every kill final — is itself the
strongest evidence for the Algorithmic Contribution prize: this is what
rigorous, honest, reproducible research looks like, and the repository is the
receipt.
