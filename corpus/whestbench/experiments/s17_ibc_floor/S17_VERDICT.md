# S17 — sampling floor, S(B) envelope, and ednacob adjudication

Ledger id: `s17_information_complexity_lower_bound` · Date: 2026-08-10 · Runner:
`run_s17.py` · Results: `s17_results.json`

## VERDICT: GATE (i) — champion within 2× of the sampling floor; floor located

Pooled equal-FLOP ratio **champion / (σ²/N_eval) = 1.79** (per net 1.63, 2.37,
1.37; 2/3 nets < 2×, net 202 alone at 2.37). On the distinct-direction
accounting the ratio is **0.90** (0.82, 1.18, 0.69) — the champion sits *at* the
floor. Both accountings are inside the predeclared 2× band, so the sampling
floor is located and the champion sits essentially on it. ednacob is then
adjudicated (Part C): it sits **2.2×–4.0× below the best point-evaluation floor**
→ ednacob-honest is **impossible within point-evaluation**, requiring seed-side
extraction [strengthens M245].

This is a **lower-bound attempt**, not a minimax-optimality proof and not a
closure certificate. Achievable-envelope points below are **upper bounds** on
S(B); the ednacob floor-invariant gap is a **lower bound** (impossibility). They
are not conflated.

## Deviations from the predeclaration (recorded loudly)

1. **Design N in the floor formula.** The predeclaration's 4-term formula
   `(1/N²)[N·C(1)+n₀C(0)+n₊C(1/16)+n₋C(-1/16)]` with the S6 multiplicities closes
   *only* for the base set N = 32,256 (its census sums to 32,256²). The champion
   actually uses the **antipodally-doubled 64,512** design (confirmed:
   `s15_results.json` and `s16_results.json` config, `n_full=64512`,
   "residual = antipodal symmetrization"). I therefore **derived the exact
   5-shell doubled fingerprint** from the S6 base census by the {x,−x} map and
   used N = 64,512. It is exact: the shell counts sum to 64,512² bitwise, and the
   doubling makes the ±1/16 shells **sign-balanced** (the Kerdock +1/16 excess
   cancels — the odd part drops out). The base 4-term formula is also reported.
2. **The floor is read from the field variance σ²/N, not from the correlation
   kernel.** Plugging the S7 mean-field kernel into the exact fingerprint is
   numerically unstable (the cross-shell coefficient is 64,000; a sub-1e-3 error
   in c_even(1/16) moves the predicted inflation by O(10) — the naive plug-in
   returns 24.9, a documented artifact, not a floor). The single-rotation
   empirical shell averages collapse identically to zero variance. So the floor
   is anchored on σ² = Var(ybar) directly, and the correlation kernel is used
   only as corroborating evidence that the residual is decorrelated at the design
   spacing.
3. **N_eff formula.** As written, `N_eff = N·var/Var(field)` evaluates to the
   *ratio* (≈1.8), not an effective-sample count. I report the meaningful
   effective count `N_eff = Var(field)/var` (≈27k–47k) and the ratio separately.
4. **Champion aggregate.** The headline uses the leaderboard suite value
   2.818e-7; the exact per-net floor test uses the three committed synthetic nets
   (101/202/303), whose champion panel mean is 3.41e-7 — same regime. Ratios are
   computed per net (self-consistent σ² and champion MSE), not by mixing the
   suite MSE with a per-net σ².

None of these changes a gate threshold.

## Part A — the sampling floor (derivations, earned levels)

### A.1 Exact fingerprint (derived; the doubling is exact)

Base 32,256-set inner-product census (S6, exact dyadic, `s6_results.json`
→fingerprint) — **reported/observed**:

| shell | value t | multiplicity |
|---|---|---|
| diagonal | 1 | 32,256 |
| within-frame off-diag | 0 | **8,225,280** (= N·255) |
| cross-frame | +1/16 | **548,352,000** |
| cross-frame | −1/16 | **483,840,000** |

Sum incl. diagonal = 32,256² (checked). Antipodally doubling {x,−x} maps each
cross-frame base pair to 2 pairs at +1/16 and 2 at −1/16, giving the **exact
64,512 fingerprint** — **derived**:

| shell | value t | multiplicity | inflation coeff (mult/N_full) |
|---|---|---|---|
| diagonal | 1 | 64,512 | — (this is the 1) |
| antipode | −1 | 64,512 | 1 |
| within-frame | 0 | 32,901,120 | 510 |
| cross-frame | +1/16 | 2,064,384,000 | 32,000 |
| cross-frame | −1/16 | 2,064,384,000 | 32,000 |

Census sum = 4,161,798,144 = 64,512² (bitwise), ±1/16 shells equal (sign-balanced).

### A.2 Field variance and the floor (observed)

σ² = Var(ybar) over the 64,512 design, from the committed S5 arrays (two ways,
rel. diff 0.0): net 101 **7.900e-3**, 202 **1.600e-2**, 303 **1.112e-2**.

Equal-FLOP iid Monte-Carlo floor = σ²/N_eval, N_eval = 64,512 forward passes:

| net | σ² | champion MSE | σ²/64512 | **champ/floor** | σ²/32256 | champ/(σ²/32256) | N_eff = σ²/champ |
|---|---|---|---|---|---|---|---|
| 101 | 7.900e-3 | 1.997e-7 | 1.225e-7 | **1.63** | 2.449e-7 | 0.82 | 39,558 |
| 202 | 1.600e-2 | 5.872e-7 | 2.480e-7 | **2.37** | 4.961e-7 | 1.18 | 27,251 |
| 303 | 1.112e-2 | 2.369e-7 | 1.724e-7 | **1.37** | 3.449e-7 | 0.69 | 46,955 |
| **pooled** | | | | **1.79** | | **0.90** | ~38k |

Two accountings differ by exactly 2×: the champion evaluates 64,512 forwards but
those are 32,256 base directions and their antipodes (the estimator is the
antipodal symmetrization, S16). Counting forwards → 1.79×; counting distinct
directions → 0.90×. Effective independent draws N_eff ≈ 38k, i.e. ~60% of the
64,512 evaluations — the antipode of x carries correlated (even-harmonic)
information, so a pair of forwards is worth ~1.2 independent draws, not 2.

### A.3 Pseudo-randomness at the design spacing (observed, second signal)

The exact empirical shell correlations of the r=0 field at the design's own
inner products are **c(0) = −1.3e-3** (t=0, 90°) and **c_even(1/16) = −5.5e-6**
(t=±1/16, 86.42°): both ≈ 0. The residual is decorrelated at every design pair
spacing (design min angle 86.42° = arccos(1/16), ~2× the S7 speckle length
ξ ≈ 37–46°). This is the champion residual behaving as strong pseudo-randomness:
deterministic in the weights, but with no exploitable second-order structure at
the sampling geometry. Consistent with S6 (flat Bragg shelf, participation rank
≈ N) and S7 (design spacing 2× above ξ → independent draws).

### A.4 Gate

Pooled cost-matched ratio 1.79 < 2 (2/3 nets individually < 2; net 202 at 2.37
sits in the 2–4× band as modest per-net headroom). Distinct-direction ratio 0.90.
**GATE (i): champion within 2× of the sampling floor — floor located.** No
evidence of gate (iii) (a >4× better sampling scheme, which would contradict
S6/S7). The corpus's own standing claim — "our exact-2-design sampler is
near-optimal at ~2.8e-7" (RAYAN53_FORENSICS) — is reproduced from first
principles here.

## Part B — the S(B) envelope

Each point is labelled UPPER-BOUND/achievable or a limit. Log-log (FLOPs C vs
achievable MSE):

| regime | FLOPs C | achievable MSE | bound | level |
|---|---|---|---|---|
| (i) B~0, cheap observables | 0 | ≈ σ² (unreduced) | UPPER | observed (S15: covariates explain 1.56%) |
| (ii) analytic closure (deg≤2 exact) | ~0 | **9.6e-5** | UPPER/achievable | reported (T2/M181 full-cov) |
| (iii) our sampling budget (champion) | 1.768e11 | **2.818e-7** | UPPER/achievable | reported (leaderboard, C/B 0.65) |
| (iv) 5.27× budget sampling scaling | 9.32e11 | **5.35e-8** | UPPER/achievable | derived (1/N from champion; joe_wanza-class honest ref) |
| (v) B = ∞ | ∞ | 0 | limit | derived |

**Structure.** Two features. (a) A **budget-independent closure plateau** at
9.6e-5: analytic degree-≤2-exact integration removes only the exactly-integrable
part; more analytic closure does not lower it (S15: cheap first-layer covariates
add ≤1.56% out-of-sample R²). (b) A **1/N sampling line** through the champion
(2.818e-7 → 5.35e-8 at 5.27× budget), which is where all the achievable
variance reduction lives. The gap between the plateau and the sampling line —
the region a seed-side method could occupy **among the tested classes only** — is

  width = 9.6e-5 / 2.818e-7 = **340.7×** (raw); 9.6e-5 / 1.832e-7 = **524×** (adjusted).

This is a **map of tested classes**, not a proof that no untested output-side
method enters it.

### The computational entropy curve S(B)

S(B) is the least mean-squared error any estimator can reach with FLOP budget B
against the depth-32 He-network sphere-mean. It has two arms that meet nowhere
cheap. The horizontal arm is analytic: closing the network under a Gaussian
(degree-≤2-exact) ansatz costs almost no compute and buys you down to 9.6e-5,
where it stops dead — the residual past degree 2 is covariate-blind (S15) and
speckle-like (S7), so no further output-side closure we tested moves it. The
sloped arm is stochastic: point-sampling the exact-tight Kerdock 2-design drives
MSE down at the full 1/N rate, because the residual is pseudo-random at the
86.4° design spacing (Part A.3) — the design behaves as independent draws, and
the champion sits within 2× of that floor (Part A). The 340× vertical gap
between the plateau and the champion is not headroom *we* left on the table by
sampling badly; it is the price of information — you pay in FLOPs (the sloped
arm) or you accept 9.6e-5 (the plateau). The only way to sit *inside* that gap —
low MSE at low budget — is to leave the point-evaluation oracle entirely and
read the seed (the weights). That is exactly where ednacob is found (Part C),
and exactly the door M245 argues is the only one left.

## Part C — ednacob adjudication

ednacob: raw 9.11e-8 / adjusted 4.62e-8 / C/B 0.507 (1.379e11 FLOPs) / 119
entries. Champion: 2.818e-7 / C/B 0.650 (1.768e11 FLOPs). Variance-per-FLOP
(MSE×C): champion 4.98e4, ednacob 1.26e4 → ednacob **3.97× better per FLOP**
(matches the reported 3.96×).

**The point-evaluation floor is a FLOP invariant.** For any pure point sampler,
MSE×C ≥ σ²·(FLOPs per independent evaluation) = I_floor. The champion sits at
most 1.79× above I_floor (Part A), so I_floor ≤ I_champ/1.79 = 2.78e4; at the
tight end (champion exactly at the floor) I_floor = I_champ = 4.98e4. ednacob's
invariant is 1.26e4, which is

  **2.2× below I_floor (generous) to 4.0× below (tight).**

Equivalently in budget form: at 1.379e11 FLOPs and 2.74e6 FLOPs/forward, ednacob
can afford ≈ **50,300 forward passes**. Even granting every forward an
*independent* draw (the most generous point-eval case, no finite-width penalty),
the best point MSE is σ²_suite/50,300 = **2.02e-7** (σ²_suite ≈ 1.02e-2 backed
out from the champion). ednacob reports **9.11e-8 — 2.2× below the best possible
point-evaluation MSE at its own budget.** A point evaluator cannot extract more
independent information than it has function queries.

**Verdict.** ednacob-honest is **impossible within point-evaluation**. It
therefore either (a) uses **seed-side extraction** (exact-control / weight
access, outside the point-evaluation oracle) — which **strengthens M245**, or
(b) is **over-budget / mis-metered** — consistent with the ednacob forensics
band. The arithmetic (≥2.2× below the floor in every accounting) is high
confidence; the disambiguation between (a) and (b) is not ours to make from
firewall-clean data. Assumptions (moderate): ednacob operates in the
point-evaluation class at comparable per-forward cost, and σ²/N is the point
lower bound (valid absent seed-side control variates — which is the whole point).

## Two-signal verification

- **Fingerprint**: doubled census sums to 64,512² bitwise (independent of the
  σ² path) and the ±1/16 shells are exactly equal (sign-balanced) — a structural
  check of the derivation.
- **σ²**: Var(ybar) vs mean(r_global²) agree to rel. 0.0 (array-algebra
  cross-check).
- **Champion MSE**: equals cached-m181 arm0 to 6 digits (S16 crosscheck ratios
  0.99999) — an independent truth path; quoted, not re-read (firewall).
- **Ratio 1.79** lands in the S7-measured finite-width band [1.7, 2.2] (same
  slow-decorrelation origin) — corroborating, not a rigorous identity.
- **Reproducibility**: two runs bitwise-identical on every printed number.
- **Anchor reproduction**: the S(B) gap 340.7× and the ednacob 3.97× vpf
  reproduce the predeclaration's stated values from the committed constants.

## Limitations

- Per-net champion MSE rests on 16 rotation replicates (~36% relative SE each);
  the 3-net pooled ratio 1.79 has a wide t-CI. The gate verdict holds on the
  pooled mean and on 2/3 nets; net 202 alone would read gate (ii).
- The floor is σ²/N (field variance), NOT the correlation-kernel formula: the
  64,000× cross-shell coefficient makes the kernel path unusable at these scales,
  and single-rotation shell averages collapse. This is disclosed, not hidden.
- The even/odd harmonic split (why the two accountings differ by 2×) could not
  be verified: antipodal pairs are not identifiable from the S5 arrays (dmin is a
  net feature, not the geometric distance), so that decomposition is omitted
  rather than reported unverified.
- σ²_suite for Part C is backed out from the champion (≈1.02e-2); the ednacob
  impossibility is 2.2–4.0× and robust to this within a factor ~2.
- Everything here maps the **tested** method classes. It is a lower-bound
  *attempt* with gates, not a proof of minimax optimality and not a certificate
  that no untested output-side method sits inside the 340× gap.

## Files

- `run_s17.py` — exact fingerprint decomposition (4-term base + 5-term doubled),
  σ² from S5 arrays, floor/ratio/gate, S(B) envelope, ednacob invariant. No
  N² brute sum. Deterministic.
- `s17_results.json` — full numbers.
- `S17_VERDICT.md` — this file.
