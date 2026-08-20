# Kill-context index — all 276 records (regime-audit extractions, 2026-08-19)

Doctrine: kills are CONTEXT-INDEXED — carrier, precision, payoff convention, kill type
are axes; an axis change is a premise change. This file carries the cross-cutting
synthesis verbatim from the two extraction agents; their full per-record tables (every
record: carrier, precision, convention, killtype, numbers, preserved tissue) are in the
session transcript at
`C:\Users\strid\.claude\projects\C--Users-strid\7c1d8a18-611c-4493-9d65-0b4a9ad5fd33.jsonl`
(2026-08-19, the two "Extract kill contexts" task notifications). The fold ledger itself
(`../headroom/fold_ledger.json`) remains the source of truth for every number.

## Records 0–139 — cross-cutting observations (verbatim)

- CARRIER SPLIT. The Kerdock/MUB family appears explicitly at IDX 3, 70, 71, 72, 73, 74,
  79, 80, 81, 84 (plus MUB machinery referenced at 36, 66, 111). Haar-random /
  random-spherical carriers dominate: 0, 13-16, 40, 43, 53, 66, 68, 77, 87, 88, 105,
  109, 110, 111, 131. Zonal/Gegenbauer/Hermite harmonic bases: 1, 8, 23, 36, 38, 39,
  45, 47, 68, 76, 92, 97-104, 106, 107, 112, 113, 133. IDX 68 explicitly corrects a
  prior claim: the formal L1 geometry is "126 independent Haar frames with degree 2
  exactness, not a Kerdock MUB."
- PRECISION IS ALMOST NEVER NAMED ON MATH KILLS. float32/f32 appears only on
  engineering/arithmetic mutations (42, 46, 48, 50, 53, 58, 69) and the
  source-contraction cost family (127-130, 134, 135, 139); float64 at 52, 102, 125,
  126, 129, 134, 135; mixed-f32 explicitly at 128 and 130. IDX 15/16/40 are the FP32
  randomized-radial line. IDX 110 checks both f32 and f64.
- ONLY THREE KILLS WERE MEASURED ON THE FULL ADJUSTED SCORE: IDX 16 (96.1178x worse,
  multiplier 0.258849), IDX 59 (ratio .990674633, missed a .99 gate), and IDX 7
  (adjusted 1.3162e-4, 583.1x). IDX 53 is the promoted adjusted-score win. Everything
  else was killed on raw variance/fidelity, a cost wall, residual wall-time, or protocol.
- RESIDUAL WALL-TIME ALONE KILLED IDX 117 (.6105 s), 118 (.3285 s), 69 (.194269 s)
  against a .170 s gate, and eroded IDX 59's analytical win.
- PURE PREEXECUTION COST WALLS: 113 (390.066B vs 272B), 114 (283.763B vs 272B), 115
  (84.963B vs 80B), 123 (215.417B vs 152B), 86 (35.824B leaves .171B), 139 (5.191B vs
  5B), 80 (memory margin 1.75195 MiB vs 1.44531 MiB).
- "COMPONENTS PRESERVED" IS NEAR-UNIVERSAL: 8 of the last 20 records encode it in the
  status string. Recurring survivors: the M125b carrier, the M122 bridge algebra, the
  [2,1,1] quadratic jet, exact Price/Jacobian algebra, the Haar/Fubini + coarea
  identities.

Key single records: IDX 0 h4_random32256 (promoted root of the row_blocked lineage,
random spherical 32,256 base directions). IDX 3 kerdock_design (the ORIGINAL Kerdock
kill — cost, "structured-gate survival caused nonlinear cost excess" — later resurrected
via the phased WHT as M71/kerdock_v3). IDX 80 m81_full129_pareto (full129 A2=A4=0;
trim126 A4=.047422179; memory increment 1.75195 MiB vs 1.44531 MiB margin; raw MSE must
drop >2.3256% to improve adjusted). IDX 53 row_blocked_winograd_production (promoted:
2.1218e-7, raw MSE ratio .999983, max C 222.405B).

## Records 140–275 — cross-cutting observations (verbatim)

- CONVENTION SPLIT. Records 140-222 (the m141-m207 analytic/compiler lineage) are
  killed almost entirely on COST/FLOP budget (100B endpoint, 14.0191212B slot,
  10.291363760B allowance, 1.986871472B strict composed headroom) or on RESIDUAL WALL
  SECONDS (7.149 ms permitted, 5x/k=5 hostile projection, 258.4B gate), with only three
  raw-variance kills (159, 161's diagnostic, 179). Records 178-241 are the sampler
  lineage, killed on RAW MSE / variance ratio at predeclared G0 gates, with the
  adjusted score appearing mainly in 178, 183, 190, 199, 241. Records 242-275 are
  graveyard/re-audit falsifiers, mostly statistical or protocol verdicts.
- PRECISION RARELY STATED (~12 records). TWO RECORDS MAKE DTYPE DECISIVE: 251
  (gm_latent_cubature — the 80e9 gate has NO pinned dtype convention; f64 86.4B vs f32
  54.0B) and 252 (gm_rankone_bill — discharging dtype_multiplier=1 moves M204/M205 from
  ~4.5-4.9% over headroom to ~34% under).
- CARRIER. "Kerdock" dominant from 179 onward (126 phased-Hadamard frames x 256
  directions, antipodally doubled to 64512, Haar-rotated per net — established at n8a,
  record 186). MUB/5-design at 191, 228, 233, 259. random32256/row_blocked/
  randomized_radial at 178, 197, 248, 251, 263, 264. The 140-222 block names NO
  spherical carrier at all (PSD covariance blocks, HH proposals, rank faces).
- A_l COEFFICIENTS given explicitly only in 269-271 (base1 A2=0 A4=.0039518 A6=.0039054;
  base2 A2=0 A4=.00098823 A6=.00097615). The deg-4/deg-6 design-error ratios (~11% and
  ~40% of iid) come from 200, 203, 205, 228, 233.
- COMPONENT-PRESERVED PATTERN: analytic kills preserve IDENTITIES (exact-control law,
  HH theorem, collision-null identity, orientation proof, owner mappings, rank-face
  algebra, two-rectangle identity, lifted algebra); sampler kills preserve MEASUREMENTS
  (design spectra at 200/228, the 61.6% unharvested oracle at 204/245, S7/S8/S12
  physics laws).

Key single records: 183 t4_kerdock_v3_descriptive_rescore (Kerdock v3 LOCAL adjusted
1.6190837992e-7, raw 2.4938875569e-7, mult 0.656, max C 209.575B = 23% under B). 184
t5 dossier queue order: Kerdock v3 FIRST, then L2 (row_blocked), tangent, fold3-cap.
233 s11 (Kerdock completion: isolated deg-4 exactness worth +0.176%, 13x under
break-even). 204/245 (the 61.6% rotation-selection oracle, unharvested; proxies killed
on Kerdock). 266 r0 (degree 4 carries only 0.45% of estimator error ON KERDOCK; even
degrees >= 6 carry 99.55%). 256 gm_m179_m199 (the reachability wall record). 269-271
(k32 cells). 272-275 (m207/m207b/deg6/deg-ladder).

## The host fork (the index's material consequence)

Two promoted lineages, two carriers, two local scores: kerdock_v3 (structured, A_4
suppressed, LOCAL adjusted 1.619e-7 at t4) vs row_blocked_production (Haar frames, full
iid A_4, LOCAL 2.1218e-7, the winner fold's current host). The t5 dossier ranked
Kerdock v3 FIRST. The fold's schedule route applies to BOTH lineages' deep layers
(kerdock_v3's layer 1 is already the phased-WHT butterfly; M71/IDX 72 uses row-local
Winograd transfer). The 129-completion's value is LARGE only on the Haar host
(pre-registered band, amended) and ~0.176% on the Kerdock host (s11 + the dual-witness
certificate agree). The two win-paths are therefore:
(a) row_blocked + fold + 129-swap, vs (b) kerdock_v3 + fold.
Both project to ~1.2e-7 territory; they are NOT exclusive; the round-3 measurement and
the 129 cell adjudicate. The designation policy must weigh both hosts.
