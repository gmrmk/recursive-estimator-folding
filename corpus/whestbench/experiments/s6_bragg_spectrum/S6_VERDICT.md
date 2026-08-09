# S6 — Bragg spectrum of the Kerdock design's degree-4 quadrature-error operator

Ledger id: `s6_bloch_design_bragg_spectrum` · Date: 2026-08-09 · Runner: `run_s6.py` · Results: `s6_results.json`

## VERDICT: KILL

The degree-4 deviation operator D = A − I/dim is **not** low-rank. Its
tr(D²) mass is spread almost perfectly flat across the entire 32,256-mode
design span: the top-100 eigenvalues carry **0.32 %** of tr(D²) (gate KILL
threshold: < 5 %; PASS required ≥ 50 %). Participation rank
tr(D²)²/tr(D⁴) = **32,266 ≈ N**. The crystallographic ("Bragg") structure
exists — the inner-product fingerprint has exactly three off-diagonal values
and the spectrum collapses to exactly three shells — but the shells sit at
≈ 1/N, i.e. the diffraction pattern is a flat shelf, not a set of spikes.
The one genuinely distinguished mode (the constant vector on the design =
the quadrature functional itself) is **suppressed 42× below the bulk**,
which is precisely M191's measured ~11 %-of-iid degree-4 advantage. So the
design's failure is delocalized (rank deficiency spread evenly, N ≪
dim H₄ = 1.83×10⁸), while its *success* is a single Bragg-suppressed mode.

## Deviations from the predeclaration (recorded loudly)

1. **Full-N Lanczos not run.** A full 32,256² kernel matvec costs ~10 s;
   ≥ 300 Lanczos iterations would blow the ~20-min budget. Took the
   predeclared fallback: uniformly-subsampled **16,000** directions (seed
   20260809) with the EXACT full-set tr(D²) from chunked pairwise sums, as
   the predeclaration prescribes.
2. On the subsample I used **dense `eigvalsh` (all 16,000 eigenvalues,
   float32)** instead of Lanczos top-k — strictly more information about
   the same predeclared object.
3. **Full-N top spectrum supplied by an exact closed form** derived from
   the bitwise-exact verified inner-product structure (not anticipated by
   the predeclaration; it is a derivation, not a new arm). It is validated
   by the structure-agnostic subsample eigensolve (max abs eigenvalue
   error 3.6×10⁻¹² over the whole sorted multiset) and by the exact
   pairwise tr(D²) (rel. diff 2.5×10⁻¹²).
4. **Inner-product fingerprint computed exactly over all N² pairs**, not a
   random pair sample: the unit-vector entries are exactly ±1/16 (dyadic),
   so every f64 inner product is bitwise exact; the exact census
   supersedes the predeclared sampled histogram.
5. Run 1 → run 2: one subsample *validation statistic* (predicted-vs-
   observed comparison) was mis-indexed in run 1 (it compared the observed
   top-126 against a predicted set whose constant mode is actually the
   *smallest* eigenvalue). Fixed to a full sorted-multiset comparison; all
   measured quantities were bitwise identical between the two runs.

None of these touch a gate definition or threshold.

## Normalization (as implemented)

- H_ℓ on S²⁵⁵, α = (d−2)/2 = 127. Reproducing kernel
  Z_ℓ(x,y) = m_ℓ·G_ℓ(⟨x,y⟩), G_ℓ(t) = C_ℓ^(α)(t)/C_ℓ^(α)(1).
- dim H₄ = (2ℓ+d−2)/ℓ · C(ℓ+d−3, ℓ−1) = **183,148,480** (cross-checked
  against C(d+ℓ−1,ℓ) − C(d+ℓ−3,ℓ−2), exact match); dim H₆ =
  **414,173,091,136**.
- C₄^(127)(t) = 181,742,080·t⁴ − 4,194,048·t² + 8,128 (exact rational
  recurrence); C₄^(127)(1) = 177,556,160.
- φ(x) = Z₄(x,·)/√m₄ ⇒ ‖φ‖ = 1, ⟨φ(x),φ(y)⟩ = G₄(⟨x,y⟩);
  A = (1/N)Σ φφᵀ ⇒ tr A = 1 exactly; nonzero spec(A) = spec(G),
  G = [G₄(⟨x_j,x_k⟩)]/N.
- tr(A²) = (1/N²)Σ_{j,k} G₄(⟨x_j,x_k⟩)²; D = A − I/m;
  tr(D²) = tr(A²) − 1/m; spec(D) = {λ_i(G) − 1/m} ∪ {−1/m, mult m−N}.
- Exact-rational identity checks passed: E[G_ℓ] = 0 and m_ℓ·E[G_ℓ²] = 1
  hold EXACTLY in `Fraction` arithmetic for ℓ = 4, 6.
- Design choice (predeclared option): unrotated 32,256 base set with
  even-degree kernels. For even ℓ, φ(−x) = φ(x), so the antipodally
  doubled 64,512 set yields the identical operator A; rotations conjugate
  A and leave the spectrum invariant.

## Inner-product fingerprint (exact census over all 32,256² pairs)

Max deviation from the k/256 grid: **0.0** (bitwise exact).

| value | count | location |
|---|---|---|
| 1 | 32,256 | diagonal only |
| 0 | 8,225,280 = N·255 | ALL within-frame off-diagonal pairs |
| +1/16 | 548,352,000 | cross-frame |
| −1/16 | 483,840,000 | cross-frame |

Exactly three off-diagonal values: the 126 phased-Hadamard frames are
orthonormal bases that are pairwise mutually unbiased (|⟨x,y⟩| = 1/√256
for every cross-frame pair) — the Kerdock MUB fingerprint. Note the sign
imbalance (+1/16 occurs 53.1 % of the time); it is invisible to even
kernels but is what powers the constant-mode cancellation below.

## Degree-4 spectrum (exact closed form, validated numerically)

Kernel values: G₄(0) = 4.5777066×10⁻⁵, G₄(±1/16) = −3.0873814×10⁻⁵.
With the verified structure, K = (1−g₀)I + (g₀−g₁)FFᵀ + g₁·11ᵀ (F = frame
indicators), so A has exactly three eigenvalue shells; D adds the −1/m sea:

| shell of D | eigenvalue | multiplicity | interpretation |
|---|---|---|---|
| mid | **3.1603445×10⁻⁵** | 125 | frame-contrast modes (+2 % over bulk) |
| bulk | 3.0995105×10⁻⁵ | 32,130 | generic design-span modes ≈ 1/N |
| top-1 | 7.2963×10⁻⁷ | 1 | constant vector = quadrature functional, **42× below bulk** |
| sea | −5.46×10⁻⁹ (−1/m) | 183,116,224 | orthocomplement of the design span |

tr(D²) = **3.09974863×10⁻⁵** — computed two independent ways:
exact pairwise sum 3.099748627×10⁻⁵ vs exact-rational closed form
3.099748627×10⁻⁵ (rel. diff 2.5×10⁻¹²). tr(A²) sits at 1.0000310/N,
i.e. within 3.1×10⁻⁵ of the rank-N frame-potential floor 1/N: the design
is a **near-perfectly tight rank-N frame on H₄**.

Top-20 eigenvalues of D: the 125-fold degenerate mid shell, all equal to
3.1603445214882744×10⁻⁵.

### Top-k concentration, sum of top-k eig² / tr(D²)

| k | full-N (closed form) | subsample observed (n=16,000) |
|---|---|---|
| 1 | 3.22×10⁻⁵ | 6.40×10⁻⁵ |
| 10 | 3.22×10⁻⁴ | 6.39×10⁻⁴ |
| 100 | **3.22×10⁻³** | **6.37×10⁻³** |
| 1000 | 3.11×10⁻² | 6.26×10⁻² |

Both columns are the flat-spectrum signature (top-k fraction ≈ k/N_eff);
the subsample doubles the fractions only because its N_eff is halved.
**Gate: top-100 = 0.32 % (full N) and 0.64 % (subsample) — both < 5 % ⇒
KILL by the predeclared rule.**

### Subsample validation (structure-agnostic second signal)

Uniform 16,000-direction subsample, seed 20260809; dense f32 `eigvalsh`.
Full sorted multiset vs the reduced-frame-matrix model prediction:
max abs eigenvalue error **3.55×10⁻¹²** (relative ~6×10⁻⁸ = f32
quantization) across all 16,000 eigenvalues. The suppressed constant mode
is directly observed: 3.2233998×10⁻⁵ vs predicted 3.2234001×10⁻⁵. Trace
checks: Σλ = 1.0000000005; Σμ² + sea = 6.2495502×10⁻⁵ vs pairwise
tr(D²)_sub = 6.2495502×10⁻⁵ (rel. 1×10⁻⁹). Eigenvalues archived in
`s6_sub_eigs.npz`.

## Degree-6 repeat (tr(D²) as predeclared; shells as free by-product)

G₆(0) = −8.8373×10⁻⁷, G₆(±1/16) = +9.5346×10⁻⁷, 1/m₆ = 2.4×10⁻¹².
tr(D₆²) = **3.10019826×10⁻⁵** (pairwise vs closed form rel. 8.1×10⁻¹³).
Shells: bulk 3.1002009×10⁻⁵ (×32,130), mid 3.0987428×10⁻⁵ (×125), top-1
3.1940888×10⁻⁵ (×1). Same flat verdict (top-100 fraction 0.31 %), with
one sharp difference: at degree 6 the constant mode is **not** suppressed
(λ_top ≈ 1.03/N ⇒ Haar-H₆ design/iid RMS = 1.015 — the design is
iid-level for generic degree-6 harmonics). The Kerdock ±1/16 phase
cancellation is tuned to degree 4 and stops there, which is exactly why
M191 found degree 6 as the first even degree with substantial error.

## M191 consistency check (sanity anchor — PASSED)

Archived (`pb1_premise_battery/m191_g0a_results.json`): deg-4
design/iid ratios **0.10668, 0.10719, 0.09829** (three rotations, 40
polys each) — the "~11 % of iid" number; deg-6: 0.3475, 0.4109, 0.4329.

| quantity | S6 direct recompute (200 polys) | S6 spectral prediction | M191 archived |
|---|---|---|---|
| deg-4 ratio | 0.10744 | 0.10778 | 0.107, 0.107, 0.098 |
| deg-6 ratio | 0.39423 | 0.40340 | 0.348, 0.411, 0.433 |

The spectral prediction is the zonal projection through the design's
exact kernel sums: E_a[err²] = Σ_ℓ m_ℓ·ĝ_ℓ²·S1_ℓ/N² (deg-6 includes the
H₄ leakage of t⁶); the identity (1/N²)ΣG_ℓ(t_jk) = λ_top^(ℓ) ties M191's
measured error directly to the single constant-mode eigenvalue. Agreement
with both the direct recompute and the archived numbers is within the
archived runs' own 40-poly sampling scatter. For Haar-random unit-norm
pure H₄ functions the aggregate design/iid RMS is √(N·λ_top) = **0.154**
(larger than 0.107 because M191's zonal t⁴ family carries an error-free
H₂/H₀ share in its normalization).

## Limitations

- The closed-form full-N spectrum rests on the verified exact 3-value
  inner-product structure; the verification is itself exact (dyadic
  arithmetic, max grid deviation 0.0), so the residual risk is a harness
  coding error, mitigated by the independent structure-agnostic subsample
  eigensolve and the exact-rational identity checks on all constants.
- The subsample arm is float32; its eigenvalues carry ~6×10⁻⁸ relative
  quantization, irrelevant at the 10⁻² shell separations probed.
- Degree-6 top spectrum was not numerically re-validated (predeclaration:
  tr(D²) only); its closed-form shells inherit the same verified
  structure.
- M191 direct recompute used the unrotated design + random a (rotation-
  invariant in distribution) and 200 polynomials vs M191's 40; population
  vs sample-std normalization differs at O(10⁻⁴) relative.
- Gate semantics: "top-100 eigenvalues" read as top-100 by |eigenvalue|
  of D; under the 125-fold mid-shell degeneracy any tie-breaking gives
  the same fraction.

## Files

- `run_s6.py` — harness (deterministic; two runs bitwise-identical on all
  measured quantities)
- `s6_results.json` — full numbers
- `s6_sub_eigs.npz` — subsample eigenvalues (f32) + subsample indices
- `S6_VERDICT.md` — this file
