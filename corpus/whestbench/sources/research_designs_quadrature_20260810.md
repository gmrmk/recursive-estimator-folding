# Research brief — quadrature point sets at d=256, N ~ 3e4–1e5 (MUB/Kerdock design vs alternatives)

Filed 2026-08-09 (dated 20260810 per task). Read-only literature sweep: arXiv + web (Semantic Scholar / publisher pages via search). Evidence levels are labeled per claim: **observed** (fetched this session), **derived** (exact arithmetic shown inline, machine-checked), **reported** (paper abstract/secondary source, not re-derived), **memory** (training-data recall, title may be approximate — verify before citing externally).

## 0. Context (measured facts, given)

Our set: 126 phased-Hadamard (Kerdock/MUB) frames × 256 directions = 32,256 lines, antipodally doubled to N = 64,512 points on S^255. Inner products exactly {0 (within-frame), ±1/16 (cross-frame)}. Exact spherical 2-design. Degree-4 error operator: three shells — suppressed constant mode ×1 (42× below bulk), mid shell ×125, flat bulk ×~N. Aggregate deg-4 error = 11% of iid; deg-6 = 40% of iid, no modal suppression at deg 6 (1.015 vs Haar).

**Identification (derived + reported):** this is a sub-collection of the Calderbank–Cameron–Kantor–Seidel (CCKS) extremal Euclidean line-set. For d = 2^m, m even, CCKS orthogonal spreads give the maximal set of d/2 + 1 = **129** real mutually unbiased bases in R^256 (standard basis + 128 phased-Hadamard frames from a Kerdock set of quadratic forms), i.e. d(d+2)/2 = 33,024 lines with exactly the angle set {0, 1/16}. Our 126 frames are 126 of these 129.

---

## Q1 — Is the 3-shell / single-suppressed-mode spectrum known?

**Verdict: the machinery that forces it is classical and well documented; the specific spectrum (shell multiplicities, 42× ratio, deg-4-only suppression) appears in no paper we found. Publishable as a worked example, not as new machinery.**

Why the structure is forced (derived, standard theory):

- The set is invariant under a large automorphism group G (the symplectic-spread normalizer inside the real Clifford group). By **Sobolev's theorem on invariant cubature** (memory: Sobolev 1962), the quadrature-error operator restricted to degree-k harmonics is G-equivariant, so its eigenvalues are constant on G-isotypic components of H_k(S^255). Few isotypic components ⇒ few shells. The mid-shell multiplicity **125 = (#frames − 1)** is the footprint of the frame-labeling permutation representation; on the completed 129-frame set the corresponding component is what the design property kills (see Q2).
- Equivalently in Delsarte language: the set carries a low-class association scheme, and error-operator eigenvalues are linear functionals of the scheme's eigenmatrix. Real MUB collections are exactly the **Q-bipartite Q-antipodal 4-class cometric schemes** — LeCompte, Martin, Owens, "On the equivalence between real mutually unbiased bases and a certain class of association schemes", European J. Combin. 31 (2010) (observed: users.wpi.edu/~martin/RESEARCH/Qmubs.pdf). Kerdock-derived schemes, Barnes–Wall connection, and formal duality: Abdukhalikov, Bannai, Suda, "Association schemes related to universally optimal configurations, Kerdock codes and extremal Euclidean line-sets", JCTA 116 (2009), arXiv:0802.1425 (observed).

Key papers:

| Paper | Relevance |
|---|---|
| Delsarte, Goethals, Seidel, "Spherical codes and designs", Geom. Dedicata 6 (1977) | LP framework; design bounds used throughout this brief |
| Calderbank, Cameron, Kantor, Seidel, "Z4-Kerdock codes, orthogonal spreads, and extremal Euclidean line-sets", Proc. LMS 75 (1997) 436–480 | Construction and extremality of exactly our line-set family (129 real MUBs in R^{2^m}) |
| Klappenecker, Rötteler, "Mutually unbiased bases are complex projective 2-designs", ISIT 2005, quant-ph/0502031 | Complex analog: maximal MUB sets ⇔ projective 2-designs with angle set {0, 1/d} |
| LeCompte–Martin–Owens 2010; Abdukhalikov–Bannai–Suda, arXiv:0802.1425 | Scheme structure behind the shell spectrum |
| Levenshtein, "Universal bounds for codes and designs", Handbook of Coding Theory (1998) (memory) | Closed-form LP quadrature nodes/weights (used in Q3) |

No hit for a published eigen-spectrum of the deg-4 error operator of MUB designs; nearest neighbors are frame-potential statements (Waldron, "An Introduction to Finite Tight Frames", Springer 2016; Waldron IEEE-IT 2017 sharpened Welch bounds — reported).

---

## Q2 — Do better point sets exist at N ~ 3e4–1e5 in d=256?

### Hard bounds first (derived; arithmetic machine-checked this session)

Delsarte–Goethals–Seidel lower bounds at d = 256:

| Exactness target | Minimum points (antipodal set) |
|---|---|
| 4-design (⇒5 by antipodality) | 2·C(257,2) = d(d+1) = **65,792** |
| 6-design (⇒7 by antipodality) | ~C(258,3)+C(257,2) = **2,861,952**; antipodal-7 form 2·C(258,3) = **5,658,112** |

Consequences:
- **No point set of ≤ 65,791 points — ours included at 64,512 — can have zero deg-4 error.** Our N misses the bound by exactly 1,280 points (2.0%). The measured "one suppressed mode short of exact" is the signature of sitting just under the tight bound.
- **No set below ~2.86M points can have zero deg-6 error, with or without weights** (the bound is a positive-definiteness/dimension argument that applies to positive-weight cubature; Möller 1979-type bounds are of the same size — reported). At N ≤ 1e5 the maximum achievable exact strength is t = 5.

### The Clifford-orbit question (KEY) — answered

- **Strength:** every orbit of the real Clifford group C_m ⊂ O(2^m) is a spherical **7-design** (not merely 3): the harmonic invariants of C_m vanish in degrees 1–7; the first nontrivial one is Σx_i^8 at degree 8. Sidelnikov, "Spherical 7-designs in 2^n-dimensional Euclidean space", J. Algebraic Combin. 10 (1999) 279–288 (observed); Nebe, Rains, Sloane, "The invariants of the Clifford groups", Des. Codes Cryptogr. 24 (2001) 99–121, arXiv:math/0001038 (observed). Some orbits are 11-designs (reported, errorcorrectionzoo.org/c/spherical_design). Complex side: the Clifford group is a unitary 3-design (Webb arXiv:1510.02769; Zhu arXiv:1510.02619, PRA 96, 062336) and stabilizer states are projective 3-designs (Kueng, Gross, arXiv:1510.02767) — all observed. Note complex projective 3-designs control only phase-invariant moments; for real-sphere quadrature the real Clifford result is the relevant one.
- **Orbit size at d=256:** the minimal orbit (orbit of e_1 = real stabilizer states = Barnes–Wall BW_256 minimal-vector directions) has 2^m ∏_{k=1}^{m-1}(2^k+1) lines = **162,569,721,600 lines = 3.25e11 points** (derived; formula sanity-checked at m=4: 2,160 lines = 4,320 vectors = BW_16 kissing number). Verified numerically this session.
- **Constructible per-net?** Mechanically yes (reported: standard Clifford factorizations — one orbit element = one Clifford matrix = product of Hadamard, diagonal-phase, and permutation layers, O(d log d) per apply) — but the orbit is 5.0e6× larger than our budget, and *any* 7-design needs ≥ 5.66M points anyway (DGS above), so **no Clifford-orbit design fits N ~ 64k. Exact deg-4+deg-6 via Clifford orbits is impossible at our scale. Verdict: does not dominate ours; not a viable mechanism at this N.** Random sub-sampling of the orbit destroys exactness (gives iid-from-orbit variance, no modal suppression).

### THE MAJOR FINDING — complete 126 → 129 frames: exact 5-design, deg-4 error ≡ 0

**Claim (derived, exact rational arithmetic):** the full CCKS set — all 129 real MUBs, 33,024 lines, N = 66,048 points — is an exact projective 2-design in RP^255, hence (being antipodal) an exact **spherical 5-design**: aggregate degree-4 (and 5) quadrature error exactly **zero**, versus our measured 11%.

Proof (one line of arithmetic). Per line, the 4th-power inner-product sum over the set is
  self 1 + within-frame 0 + cross-frame 128·256·(1/16)^4 = 1 + 32,768/65,536 = **3/2 exactly**.
The Welch/projective-2-design bound demands (1/N_L)·Σ_j t_ij^4 = N_L·3/(d(d+2)); with d(d+2) = 66,048 this forces N_L = 33,024 — **exactly** the 129-frame count (machine-checked: 2·33,024 = 256·258). Equality in the Welch bound ⇔ the 4th-moment tensor equals Haar's ⇔ projective 2-design; antipodal + Haar 4th moments ⇒ spherical 4-design ⇒ (antipodal) 5-design. The same arithmetic at 126 frames gives per-line sum 1.48828 > Welch RHS 1.46512 — excess ≈ 4.6% of iid in variance terms (machine-checked), order-consistent with the measured 11% under a different shell weighting. The identity 128·256/16^4 = 1/2 holds for every d = 2^m, m even: **maximal real MUB sets are spherical 5-designs in all these dimensions** (consistent with, and implicit in, CCKS "extremal"; we found no paper stating the 5-design property in this form — check CCKS §before citing).

Practical content:
- **Cost:** +3 frames (+2.4% points; +1,536 points). One of the three is the standard basis — its "transform" is free. The other two are phased-Hadamard frames from the two Kerdock quadratic forms missing from our 126. Same O(N d) effective evaluation via Hadamard structure. N = 66,048 is only **0.39% above the DGS floor 65,792** — within a whisker of the smallest 5-design any construction could ever give.
- **Verification checklist (cheap, do before adopting):** (i) build the full 129-frame spread from the standard Kerdock set; (ii) confirm inner-product multiset {0, ±1/16} over all cross pairs (this is the one assumption — that the completed spread is unbiased against all 126 existing frames; guaranteed if ours came from a standard orthogonal spread, needs a check if ours was ad hoc); (iii) numerically confirm deg-4 error operator ≈ 0 at working precision; (iv) re-measure deg-6.
- **Deg-6 does not improve:** per-line 6th-power sum = 1 + 65,536/16^6 per point-pair convention; against antipodal-iid the pure-G6 excess ratio is ≈ 0.97–1.05 (derived) — matching our measured "no suppression at degree 6". Completion buys deg-4 = 0 and leaves deg-6 ≈ as measured.
- Closure note: this is a *completion* of the Kerdock family, not a perturbation or mix; M180 (which killed perturbations/mixes) does not cover it. Whether the team rules it in-family is a judgment call — but it strictly dominates on deg-4 at essentially equal N and identical cost, so it should be tested regardless.

### Other candidate families at this scale (none dominate)

| Construction | Points at d=256 | Deg | Cost/point | Verdict |
|---|---|---|---|---|
| Completed CCKS (129 real MUBs) | 66,048 | exact 5 | Hadamard O(d log d), O(N d) net | **Winner at this N** |
| Victoir 2004, "Asymmetric cubature formulae with few points in high dimension for symmetric measures", SIAM J. Numer. Anal. (observed) | deg-5: d²+7d+1 ≈ 67,330; deg-7: (d³+21d²+20d+3)/3 ≈ **5.60M** | exact 5 / exact 7 | nodes are sparse signed vectors — very cheap dot products | deg-5 version slightly larger than completed CCKS, no advantage; **deg-7 version ≈ 5.6M points sits essentially at the antipodal-7 DGS floor 5.66M — the escape hatch if the budget ever grows 85×: exact deg-4 AND deg-6** |
| Arman, Bondarenko, Prymak, Radchenko, "A construction of spherical 5-designs with O(d²) points", arXiv:2606.01376 (observed) | ≤ 72d² ≈ 4.7M | exact 5 | via Sidon-set projective 2-designs | 71× more points than CCKS completion; general-d, loses at d=256 |
| Misawa, "Explicit construction of spherical 5- and 7-designs" (2026, via tight fusion frames; reported) | 5-designs O(d³); 7-designs O(d⁶) even d | 5 / 7 | — | Dominated at d=256 |
| Full real Clifford orbit / BW_256 kissing set | 3.25e11 | exact 7 (some 11) | O(d log d) per point | Infeasible N (see above) |
| Randomized structured orbits — SORF/ROM (Yu et al. 2016; Choromanski et al. 2017 — memory) | any N | none exact | HD-product O(d log d) | Unbiased, constant-factor variance cut only; strictly worse than our measured 11%/40% |
| Maximal orthoplectic fusion frames from MUBs + block designs (Bodmann–Haas, reported) | — | fusion-frame optimality, not spherical strength | — | Not a quadrature upgrade |

---

## Q3 — Weighted quadrature on the existing set

**Verdict: weights cannot rescue the 126-frame set, and are unnecessary on the 129-frame set.**

1. **Impossibility below the bound (derived + reported):** positive-weight cubature of degree 5 (antipodal, d=256) still requires ≥ ~65,792 nodes (DGS-type dimension bound; Möller 1979 form d²+d+1 = 65,793 for symmetric measures — either version). 64,512 < 65,792: **no weighting of our 126 frames achieves exact deg-4.** Weights can only shrink, not zero, the residual.
2. **Optimal weights are uniform on a transitive set (derived):** if Aut(X) is transitive on points (true for spread-symmetric frame sets), averaging any weight vector over Aut(X) never increases the (convex, Aut-invariant) error functional, so an optimal weighting exists that is Aut-invariant = constant. Per-frame weights only matter if the 126 frames split into inequivalent Aut-orbits (plausible for 126-of-129 — the 3 missing frames break symmetry). LP over ≤ a few frame-orbit weight classes zeroing the ×1 and ×125 shells is a 2-constraint linear solve — could kill both non-bulk shells of the deg-4 operator, but the bulk (rank ~N) is untouchable by construction, so the gain is bounded by the current non-bulk share. The 129-completion strictly dominates this move.
3. **Closed form (reported):** LP-dual optimal weights per inner-product class are the Christoffel numbers of Levenshtein's quadrature framework (Levenshtein 1998, Handbook ch. 6; systematized as node/weight systems in Boyvalenkov–Dragnev–Hardin–Saff–Stoyanova, "Universal lower bounds for potential energy of spherical codes", Constr. Approx. 44 (2016), arXiv:1503.07228, and "Universal upper and lower bounds on energy of spherical designs", arXiv:1509.07837 — both observed). The same machinery yields **certified LP lower bounds on the deg-6 error of any N=66,048 configuration** — the concrete check for whether 40%-of-iid is already near-optimal at this N (we suspect yes to within a small factor, since the pure-G6 frame-potential excess of any antipodal set is self-term dominated at 2/N and ours sits at ≈ 0.97–1.05 × that).
4. **Complex precedent that weights extend designs (observed):** Roy, Scott, "Weighted complex projective 2-designs from bases", J. Math. Phys. 48, 072110 (2007), quant-ph/0703025 — weighted unions of d+2 bases form exact 2-designs where unweighted MUB sets don't exist. The real analog would be a weighted union of our 129 frames with one extra non-MUB frame family — only worth exploring if the completion's unbiasedness check (Q2) fails.

---

## MECHANISM-GENERATOR — constructions outside the closed list

(Closed: perturbations of the Kerdock family, rotation fragmentation. Open: wholly different families with proven strength.)

1. **Spread completion to 129 real MUBs** — proven exact 5-design (this brief, Q2). Deg-4 → 0 at +2.4% points, identical transform cost. Highest priority; one afternoon to verify numerically.
2. **Victoir degree-7 thinned cubature** (Weyl-B orbits thinned by orthogonal arrays / combinatorial designs): exact 7-design-equivalent at ≈ 5.60M sparse-support nodes, essentially at the DGS floor. The only known route to deg-6 = 0; park until/unless N-budget grows ~85×. Nodes are k-sparse ±1/√k vectors ⇒ per-point cost below a Hadamard apply.
3. **Harmonic-index designs** (memory: Bannai–Okuda–Tagami, "Spherical designs of harmonic index t", J. Approx. Theory ~2015; Okuda–Yu on index-4 nonexistence): sets exact on H_6 *alone* evade the 2.86M six-design bound. An antipodal set exact on {H_2, H_4} (5-design) unioned/weighted with an index-6 component would need exactness on {2,4,6} = full 6-design ⇒ bound applies — so only *partial* deg-6 suppression is possible; the LP bound of item Q3.3 quantifies the ceiling. Mechanism: 2-orbit weighted union (129-MUB ∪ inequivalent Clifford sub-orbit, e.g. the 2d-point cross-polytope orbit or half-support RM(1,m) states) with weights solved to cancel the few G-invariant deg-6 shells. Unproven; the check is a small eigen-shell computation on the joint set.
4. **Intermediate Clifford sub-orbits**: orbits of groups between the spread normalizer and full C_8 interpolate 66,048 → 3.25e11 points; the first steps up (~1e5–1e6, guess level) might carry index-6 exactness before full 7-design strength. Generate-and-test: compute ΣΣG_6 for candidate sub-orbits; any hit beats item 3's LP ceiling honestly.
5. **Sidon-set projective 2-designs** (input to arXiv:2606.01376) — alternative exact-deg-4 family if a Kerdock-independent construction is ever wanted (e.g., for holdout-style independence arguments); 71× more points, so only of methodological interest.
6. **Weighted Roy–Scott-style extensions** (Q3.4) — fallback if completion fails unbiasedness.

## Bottom-line verdicts

- **Q1:** spectrum structure = Sobolev/association-scheme consequence, machinery classical (DGS 1977; LMO 2010; ABS 2009); the concrete spectrum unpublished. Mid-shell multiplicity 125 = frames−1 is diagnostic and disappears at completion.
- **Q2:** Yes, one construction strictly dominates on deg-4 at equal cost and ~equal N: the **completed 129-frame CCKS set — exact spherical 5-design at 66,048 points (0.39% above the theoretical floor), deg-4 error exactly 0 vs our 11%; deg-6 unchanged.** Nothing at N ≤ 1e5 can beat deg-6 exactly (bound 2.86M); Clifford orbits are 7-designs but their minimal orbit is 3.25e11 points — unusable here.
- **Q3:** weights provably cannot fix deg-4 at 126 frames (node-count bound), are uniform-optimal on transitive sets, and their per-class closed form is Levenshtein/BDHSS quadrature — useful only for the residual-deg-6 LP bound and for exotic unions.

## Primary sources (fetched or located this session)

- Sidelnikov, Spherical 7-designs in 2^n-dim space — https://link.springer.com/article/10.1023/A:1018723416627
- Nebe–Rains–Sloane, Invariants of the Clifford groups — https://arxiv.org/abs/math/0001038
- CCKS, Z4-Kerdock codes… extremal line-sets — https://www.math.stonybrook.edu/~mlyubich/Archive/Stock/Seidel.pdf
- Klappenecker–Rötteler, MUBs are complex projective 2-designs — https://ieeexplore.ieee.org/document/1523643/
- Kueng–Gross, stabilizer 3-designs — https://arxiv.org/pdf/1510.02767 ; Zhu — https://arxiv.org/abs/1510.02619 ; Webb — arXiv:1510.02769
- LeCompte–Martin–Owens, real MUBs ↔ association schemes — https://users.wpi.edu/~martin/RESEARCH/Qmubs.pdf
- Abdukhalikov–Bannai–Suda — https://arxiv.org/abs/0802.1425
- Victoir, asymmetric cubature — https://www.researchgate.net/publication/220179132
- Arman–Bondarenko–Prymak–Radchenko, 5-designs with O(d²) points — https://arxiv.org/abs/2606.01376
- BDHSS universal bounds — https://arxiv.org/abs/1509.07837 ; https://arxiv.org/pdf/1503.07228
- Roy–Scott, weighted projective 2-designs — https://pubs.aip.org/aip/jmp/article/48/7/072110/912068
- Spherical design index (secondary) — https://errorcorrectionzoo.org/c/spherical_design
