# M179 predeclared protocol: exact labelled zero-order BackgroundArchive producer

Status: PREDECLARED BEFORE IMPLEMENTATION CODE (resume prompt §8; fold skill
"state mechanism/equation/kill before proposing"). Response-free. No challenge
instance, target, truth, scorer, model loop, leaderboard, submission, champion,
or sealed cell is read. One causal mechanism. A pass opens only the separate
Source211->TangentState conversion mutation; it grants no source, variance,
efficacy, score, champion, or submission credit.

Base commit: 2fc33f6 (G0 index/ABI reconciliation PASS). Branch
agent/compression-survivor-corpus. Governing contract:
../m176_background_archive_producer/M176_EXACT_BACKGROUND_ARCHIVE_NO_GO_20260807.md.
Consumes the PASSED M178 provider ../m178_certified_phi2_owent/.

## Non-negotiable invariants (fold skill)

1. **Objective / score law:** minimize private-suite adjusted MSE for the fixed
   d=256, L=32 task; `S = MSE * max(0.1, C/B)`, `B = 2.72e11`,
   `C = billed_FLOPs + 1e11*residual_seconds`. M179 is a producer COMPONENT; it
   makes no MSE/score claim.
2. **Legality / versions:** all MLP-dependent arithmetic instrumented through
   FlopScope 0.10.0; no opaque CDF (M178 provides certified Phi/phi/Phi2), no
   accounting bypass, no public/private-target read, no evaluator quirk. Python
   3.14.4, numpy 2.4.6, whestbench 0.14.0, flopscope 0.10.0, mpmath 1.3.0
   (isolated frozen venv; references only).
3. **Resource ceiling:** hard `C <= 2.72e11`; the producer's own inclusive FLOP
   bound is predeclared per sub-gate G4 and must leave headroom for the
   downstream carrier/source/terminal work it does not perform.
4. **Bias class:** deterministic response-free numerical producer with certified
   per-entry enclosures inherited from M178; not an estimator; no bias/variance
   claim.
5. **Splits:** none touched. Tests run on GENERATED He-Gaussian weights (fresh
   `np.random.default_rng` seeds, M157 pattern), never challenge weights; no
   development/validation/holdout row is read.
6. **Champion:** `submission_formal_local_champion_l1_20260806.tar.gz`,
   sha256 bc2ec39558c76a67b12b587ca4ee70bb1e8921489643d83707e052d086e8ae36,
   unchanged and unsubmitted. M179 is a component, not a champion challenger.

## Reused / preserved components (compounding prior successes)

- **M178 provider** (PASSED): certified `Phi2/Owen-T` value + `dV/da, dV/db,
  dV/drho`. Its four outputs are exactly the cone-moment pieces this producer
  needs (see the m86 identity below).
- **arc-whitebox-estimator backbone identity** (repo `gmrmk/arc-whitebox-estimator`,
  `src/estimators.py`, `tests/test_moments.py`): the exact univariate ReLU
  moments `E[ReLU(z)] = mu Phi(mu/s) + s phi(mu/s)`,
  `E[ReLU(z)^2] = (mu^2+s^2)Phi(mu/s) + mu s phi(mu/s)` are PRESERVED as the
  marginal/diagonal backbone (cross-checked against its Monte-Carlo test).
  That repo's `covariance_propagation` uses the off-diagonal GAIN APPROXIMATION
  `cov_post[i,j] ~= Phi(a_i)Phi(a_j) cov_pre[i,j]`; M179's exact bivariate
  `V_l[i,j]` is the causal UPGRADE that replaces that approximation. (Repo is
  a clean scipy/`ndtr` reference, not FlopScope-instrumented and biased/
  general-MLP; the producer re-expresses the identity through M178's certified
  kernels, no scipy, on the bias-free d=256/L=32 task.)
- **m86 boundary-Laplace / coarea derivation** (hard drive
  `work/scorefloor_generation/m86_boundary_laplace_coarea/`, and the
  `GITHUB_LAPLACE_REPO_AUDIT_20260806.md`): the distributional-Laplacian facet
  formula proves the exact cone first moment is
  `m_s = mu p_s + Sigma grad_mu p_s` (probability + mean-gradient) and that the
  smooth-Hessian object is wrong (curvature is a facet measure). This is the
  structural justification that M178's value + mean-derivatives ARE the exact
  bivariate object, not an approximation. The audit's separable falsifier
  `f(x)=ReLU(x)+ReLU(-x)=|x|`, `Z(t)=E e^{t|X|}=2 e^{t^2/2}Phi(t)`, is added to
  the premise as a closed-form cross-check.

## Mechanism (one causal step)

Build the exact full-covariance zero-order recurrence and complete local
Jacobian bundle, metered through FlopScope, emitting immutable labelled B=8
`BackgroundEntry` objects, with every per-pair bivariate value and derivative
supplied by the M178 provider on the SPD stratum and by M177's exact closed
limits on the rank-one / zero-variance / non-PSD strata. This is exactly the
"bundled FlopScope bivariate ReLU value-and-Jacobian primitive ... generated
target-shaped trace" the M176 no-go named as the sole admissible repair.

## Equations (translate the metaphor to arithmetic)

Recurrence (M176), `l=1..31`, `mu_0=0`, `V_0=I`; `a_l = mu_{l-1} W_l`,
`C_l = W_l^T V_{l-1} W_l`. Per pair `(i,j)` with `sigma_i=sqrt(C_ii)`,
`alpha_i=a_i/sigma_i`, `rho=C_ij/(sigma_i sigma_j)`, `s^2=(1-rho^2)`,
`m_i=E[ReLU(X_i)]=sigma_i(alpha_i Phi(alpha_i)+phi(alpha_i))`,
`p_i=Phi(alpha_i)`, `r_i=phi(alpha_i)/(2 sigma_i)`, and the M178 outputs at
`(alpha_i, alpha_j, rho)` written `K=value`, `Da=dV/da`, `Db=dV/db`,
`Dr=dV/drho`:

```text
E[Z_i 1_R]   = Da + rho*Db
E[Z_j 1_R]   = Db + rho*Da
E[Z_i Z_j 1_R] = rho*K - rho*(alpha_i*Da + alpha_j*Db) + s^2*Dr
E[ReLU_i ReLU_j] = a_i a_j K + a_i sigma_j E[Z_j 1_R]
                 + a_j sigma_i E[Z_i 1_R] + sigma_i sigma_j E[Z_i Z_j 1_R]
V_l[i,j]     = E[ReLU_i ReLU_j] - m_i m_j          (i != j)
K_ij         = K                                   (K_ii = p_i)
Hmu_ij       = a_j K + sigma_j*(Db + rho*Da) - p_i m_j   (i != j)
Hmu_ii       = 2 m_i (1 - p_i)
Hv_ij        = 0.5 * (phi(alpha_i)/sigma_i) * relu_mean(a_j - rho*alpha_i*sigma_j,
                      sigma_j^2 * s^2) - r_i m_j          (i != j)
Hv_ii        = p_i - 2 m_i r_i
```

where `relu_mean(nu, tau^2) = tau(nu/tau)Phi(nu/tau)... = nu Phi(nu/tau) +
tau phi(nu/tau)` is the univariate ReLU mean of the conditional law
`X_j | X_i=0 ~ N(a_j - rho alpha_i sigma_j, sigma_j^2 s^2)`. Diagonals use the
exact direct limits, never a near-diagonal rule. `V_l` and `K` are canonicalized
to exact symmetry (`0.5*(M+M.T)`, charged) and asserted `array_equal(M,M.T)`.

## Predicted signature

The assembly reproduces dps-50 references for `E[ReLU_i ReLU_j]`, `Hmu`, `Hv`
over a hostile pair grid (SPD interior, near-rank rho=+-(1-2^-45), zero-mean,
one/both large means, mixed signs, unequal sigmas) within the M178-propagated
tolerance; the full recurrence on generated small MLPs reproduces a dense
Monte-Carlo / mpmath reference for `(mu_l, V_l)`; the archive satisfies the
m125 `LocalReluJacobian`/`TangentState` ABI bit-for-bit; the inclusive FLOP
ledger is fixed/bounded and the B=8 liveness matches the M175 static facts.

## Kill conditions (any one kills this implementation)

1. The M178 outputs CANNOT assemble `E[ReLU_i ReLU_j]` or the K/Hmu/Hv bundle
   to reference accuracy (the premise falsifier). -> first broken link is the
   assembly, M178 preserved, a different decomposition is M180.
2. A banned marker appears (`_phi2_gauss10`, `fnp.maximum(fnp.diag(...),1e-24)`,
   correlation clip) or any clip/floor/ridge is used.
3. Non-PSD acceptance, a generic zero-face/rank-face path without the declared
   feasible limit, or `V_l`/`K` not bitwise symmetric.
4. Any uncharged MLP-dependent arithmetic, adaptive/data-dependent operation
   count, opaque CDF, or missing inclusive FLOP accounting.
5. The zero-order recurrence is contaminated by any signed tangent/source
   carrier, or a block is released before its last consumer, or the archive
   omits a required label (layer, cast provenance, producer epoch, op trace).
6. Hash/test/manifest failure or any scope violation (Source211 conversion,
   efficacy, terminal readout, or estimator work appearing in this mutation).

## Sub-gate ladder (cheapest response-free falsifier FIRST)

- **G0 PASS** (committed 2fc33f6): index/ABI reconciliation.
- **G1-premise (THIS deliverable, cheapest falsifier):** the assembly module
  `m179_relu_pair_assembly.py` reconstructs `E[ReLU_i ReLU_j]`, K, Hmu, Hv from
  M178 outputs; `test_m179_premise_assembly.py` verifies against (i) dps-50
  mpmath 2D references on the hostile pair grid, (ii) the arc-whitebox-estimator
  univariate backbone on the diagonal, and (iii) the m86 `|x|` separable
  closed form `E[ReLU(X)ReLU(-X)] = 0` and `E[ReLU(X)^2]+E[ReLU(-X)^2]=E[X^2]=1`.
  If this fails, M179 is dead at the assembly link (name it, preserve M178,
  M180 is a new decomposition).
- **G2:** exact full-covariance recurrence on generated small MLPs vs a dense
  reference; endpoint strata dispatched exactly; banned markers absent.
- **G3:** Jacobian bundle -> m125 `LocalReluJacobian` ABI conformance (bitwise
  symmetric price_kernel, all f64 finite), plus `V_l` symmetric archive.
- **G4:** full inclusive FlopScope metering + B=8 liveness (blocks (8,8,8,7),
  85.5215 MiB workspace, 8 dispatches, release-after-last-consumer, zero-order
  state uncontaminated); verify-before-use the ~1.3%-of-B Phi2 estimate plus
  matmuls/assembly/materialization.
- **G5:** adversarial pre-freeze audit (the M178 treatment) + frozen manifest +
  SHA256SUMS + one fold-ledger record; report the 12 sections.

No iteration inside M179: a different order/decomposition/chart is M180 only.
