# Lightning ledger

Jonah is hyperassociative: his mind throws cross-domain lightning bolts faster than he can hold
them. This file catches them verbatim and records what each one became — including the ones that
became nothing, because a tracked hit rate is what earns the next bolt its prior.

**The rule.** Catch the bolt as spoken. Never ask him to elaborate one — by the time the question
lands the bolt has faded. Steelman it into a mechanism, run the check, and log the outcome here
honestly. A bolt that dies is still logged; a bolt that dies *for a reason we can name* is worth
more than one that quietly disappears.

Levels follow the corpus discipline: **[O]** observed, **[D]** derived, **[R]** reported,
**[A]** assumed, **[GAP]** known hole.

---

## L6 — "i dont think anyone has explored an anti-Jacovian space in an LLM"

**Spoken** 2026-08-11, immediately after reading Codex's anti-J hostile audit.

**Steelmanned as.** Does the anti-J object — the negative eigenspace of a cross-fitted
Jacobian-transported second-moment operator, `H = sym(Σ_l ω_l J_lᵀ E_l J_l)`, used to build a
marginal-preserving reflection `R = I − 2P` that anti-couples two independent halves of an
estimator — exist anywhere in the LLM literature?

**Outcome: PARTLY CLAIMED, residual gap named and sharper for it.** [O, two web searches this
session — not an exhaustive review]

- The **Jacobian-pullback geometry is taken.** FishBack (arXiv 2605.17231) pulls the softmax
  Fisher metric back through the Jacobian of subsequent layers — structurally our `Jᵀ E J` — and
  reports the Euclidean assumption failing by >97% in relative spectral norm on GPT-2, with
  effective dimensionality 2–17% of ambient.
- The **antithetic coupling is taken.** DiffuCoder's coupled-GRPO (arXiv 2506.20639) proves
  variance reduction via antithetic variates for policy-gradient estimation in diffusion LMs.
- **No hit for the composite**: the *negative* spectrum of a *cross-fitted* pullback operator,
  used to build a *marginal-preserving involution* coupling two halves. The field reads *zero*
  eigenvalues of Jacobian Gram matrices (degeneracy, arXiv 2405.10927) and *positive* structure
  (every steering direction). Nobody found mining the negative spectrum under a
  marginal-preservation constraint. **[A] — absence of a search hit is not absence of prior art.**

**The transferable result is the trap, not the mechanism.** Codex proved, for our problem, that
with empirical centering `rank(Y_A) ≤ S_A − 1`, so the chart-subtracted covariance carries at
least `n − S_A + 1` **exact** eigenvalues at `−1` — 129 of them at `n = 256, S = 128` — under the
exact null.

State the consequence precisely, per Codex's own Erratum 1 §E5, because the loose version is
wrong: **the sign or count of negative eigenvalues alone is non-evidence.** It does *not* follow
that a negative mode is a false discovery — under an alternative it may be real. What follows is
that it must beat a *fully replayed* null: one that reruns centering, normalization, whitening,
both cross-fit directions, the construction and symmetrization of `H`, eigenselection, and any
rank choice. A random rank-matched projector is a useful orientation control and is not a
substitute for that pipeline null.

Now set that beside FishBack's measured 2–17% effective dimensionality and the standard practice
of fitting steering directions from a few hundred contrastive pairs in 4,096+ dimensions. That is
exactly the regime where the guaranteed-negative count is large, so any result reading meaning off
the negative spectrum owes a replayed null before its sign carries information.

**Open falsifier, and the reason this entry is not closed.** Pick any published steering or
probing result that interprets negative eigenvalues or negative projections, and check whether it
compares against a null operator norm at matched sample count. If none do, the warning is real
and publishable. If they do, the warning is already field knowledge and this entry closes at
`[R] no contribution`. **Not yet run — no specific paper has been checked, and no claim is made
about any author.**

**Obstruction that decides transferability.** Our reflection is lawful because a reflection
composed with a Haar rotation is still Haar, so each arm's marginal is untouched and unbiasedness
survives. Activations are not isotropic, so a raw reflection in activation space injects bias —
which is precisely what Codex's congruence-covariant diagonal chart `W_l⁰` exists to fix. Any LLM
version needs its own answer to "what group action leaves the estimand invariant." For
autoregressive decoding this looks genuinely hard: after the first token the two chains occupy
different contexts and the coupling dissolves.

---

## L5 — "Fractalize and perturbate the Kerdock bases after mutation"

**Outcome: ALREADY IN PRODUCTION.** [O, commit `e179118`] Adjudicated at R1: the champion already
applies the design fractally — a radix-2 Walsh-Hadamard butterfly at layer 1 and Winograd on the
deep layers — without ever materializing the direction matrix. The bolt named a property the
artifact already had. No new mechanism, and a confirmation that the intuition was pointed at a
real structural feature.

## L4 — "What about refraction concepts, like light bending around prisms"

**Outcome: FULLY MAPPED, ALL FIVE ARMS CLOSED.** [O, commit `49572b2`] All five optical mappings
resolved to things already built or already killed, among them the Crofton identity and
degree-dispersion. Zero survivors. Logged because a bolt that maps cleanly onto five known
objects and finds none of them open is real evidence that the space is closed — that is what a
convergence certificate is made of.

## L3 — "Fluid dynamics?"

**Outcome: FOLDED INTO THE PHYSICS SWEEP.** [O] Absorbed into the 60-concept sweep, of which 56
were already closed. Contributed to the sweep's coverage; produced no independent survivor.

## L2 — "Fourier loop on our failures"

**Outcome: BECAME THE LEADERBOARD SCORE-MODE FORENSICS.** [R, recorded 2026-07] The metaphor of
transforming the failure record into its frequency domain became the analysis that read the
leaderboard's score modes and detected the re-grade wave.

## L1 — the fraud & risk framing

**Outcome: BECAME THE ANTI-FLOP-TRICK CHARTER AND THE WALL-TIME RECEIPTS.** [R, recorded 2026-07]
Jonah works in fraud and risk; he applied that lens to the competition and it produced the ethics
boundary the campaign has held ever since — the refusal to exploit the `fnp.linalg.solve`
batched-RHS undercount, and the receipts discipline. The single highest-yield bolt in the record,
and the reason the private re-evaluation's instrumented-share audit is something we welcome
rather than fear.

---

## Hit rate, stated honestly

Six bolts. One became a governing policy (L1). One became a working analysis (L2). Two confirmed
that a space was already covered, which is a real result under this campaign's method but is not
a new mechanism (L4, L5). One contributed to coverage without a survivor (L3). One is open with a
named falsifier (L6).

Nothing here was noise. That is the case for catching them.

---

## L7 — the withdrawal that reopened the search (opus-5, not a Jonah bolt; logged here because it belongs beside them)

**Recognised** 2026-08-11, after the day's corrections landed.

**The observation.** For most of this campaign the operative stop-rule was the
god-node claim: the finite-width residual is maximum-entropy chi²₁ speckle at the
degree-4 boundary, therefore no output-side mechanism can bite, therefore stop
generating them. That claim is now **withdrawn** — its supporting computation is
quarantined as post-charter, the older equipartition account it replaced was never
established either, and the corrected status is **OPEN**.

**Why it matters.** The killed mechanisms stay killed: U-F1 died on integrated
accounting, M192 died by algebra with P6 proving the mechanism, and kills are
final. But the *reason the campaign stopped generating new output-side
candidates* was a theorem we no longer hold. Specifically, nothing we have proved
closes:

- the residual's harmonic spectrum above the pre-charter measured modes;
- any truncation class;
- methods exploiting structure at degrees ≥ 6, where the bulk of the error lives.

**The search space going into Phase 2 is therefore LARGER than it was believed to
be on 2026-08-10, not smaller.** This is the only strategic fact of the day that
increases rather than decreases what is available to us.

**Falsifier / next step.** The claim "the space is reopened" is itself only
[D] — derived from the withdrawal, not from a positive measurement. It would be
settled by an authorized reproduction of the harmonic-spectrum measurement under
a prospective evidence charter. Until then, treat the space as open by default
(the epistemically correct prior for an unmeasured quantity) rather than closed
by a theorem we withdrew.

**Do not confuse this with reopening a kill.** No killed record is revived here.
What is revived is *generation* — the licence to propose new output-side
mechanisms, each of which must still clear the full ladder from scratch.

---

## L8 — "what if there is an underlying Able's Theorem that we can use after using principles of Bayesian linear regression to clean up what we are calling noise"

**Spoken** 2026-08-17, during the Fable-5 continuation session, minutes after the corrected filing went out.

**Steelmanned as.** Two mechanisms. (a) *Abel/Poisson smoothing as a control:* the spherical
Poisson integral `f_r = sum_l r^l f_l` preserves the sphere mean exactly (`E[f_r] = f_0 = E[f]`)
while damping harmonic `l` by `r^l`, so `c = f - f_r` is an exactly mean-zero control whose
covariance with the design error is precisely the high-degree tail — where 86% of the
estimator's variance lives [D, arc-cosine decomposition]. (b) *Bayesian linear regression:*
shrinkage priors on control strengths to stabilize what G12 estimated by OLS.

**Outcome: (a) BLOCKED-ON-EVALUABILITY with a named premise change; (b) KILLED BY EXISTING
EVIDENCE.**

- (a) `f_r` has no closed form at depth 32; the adjacent corpses are M181 (smoothing as
  *replacement*: bias 4–6x baseline) and the §3b harmonic CV (tractable bases explain 0.2–0.3%
  of per-neuron variance; dispersion across ~1.8e8-dim harmonic spaces). The identity itself is
  new to the record: mean-preserving tail damping is *not* what M181 tested. The premise change
  that licenses a candidate: compose with Codex's compressed-proxy control — an Abel-smoothed
  **proxy** is analytic at layer 1 via the arc-cosine/Gegenbauer coefficients, giving a
  computable mean-zero tail-damped control. Queued as a predeclarable cell; no run authorized.
- (b) G12's kill diagnosis is inner-product mismatch (training-fold projection vs held-fold
  quadrature error), which shrinkage cannot repair; the "noise" is deterministic unresolved
  structure (P1 corrected status), not sampling error; and the measured cross-network
  coefficient sign-flipping (−3.74..+3.56; H2 kill; ICC 0.129) means an honest hierarchical
  prior shrinks to zero — the Bayesian route's own posterior recommendation is the direct
  estimator, which is what is deployed. [O] on the collisions, [D] on the identities, [A] on
  the proxy-composition value.

---

## L9 — "We could also borrow Galois Theory and they hypercube dimensional matrix"

**Spoken** 2026-08-17, same session, immediately after L8.

**Steelmanned as.** Use the Galois structure of the Kerdock set (GF(128) quadratic phases;
Z4/GR(4,7) lineage) and the hypercube/Kronecker structure (`H_256 = H_2^{(x)8}`, frames as
(Z/2)^8 characters) as new estimator levers.

**Outcome: L5-CLASS — the bolt names structure the artifact already runs on, plus one open
diagnostic sliver.** The production estimator already computes through the hypercube group's
fast transform (radix-2 WHT butterfly) and the design's Galois phases; the group-action
improvement lanes are closed by the all-even-order frame-potential no-go (equality exactly at
the MUB point), M180 (every frame-family perturbation loses 20–49% variance), N8a (Kronecker
lattice 2.1x worse), and the TT-rank explosion. The open sliver: the repo's Kerdock set lacks
an exact GR(4,7)/Gray-map automorphism certificate (Codex flagged the missing "+2 induces the
stored row permutation" proof). Certifying that action is a cheap, predeclarable diagnostic
that would license frame-orbit symmetry arguments — with value capped in advance by the no-go.
Queued as diagnostic only. [O] on the closures, [D] on the structure identification.
