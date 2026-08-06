# Goal-oriented adjoint cumulants: exact terminal fold, full-adjoint no-go

## Decision

**Hard-kill as a standalone WHestBench estimator. Preserve the terminal
first-Born operator as a proved low-cost component.**

The proposed observable adjoint does uncover a real factorization.  The
leading layerwise connected third- and fourth-cumulant sources can be
contracted into all 256 terminal diagonal cumulants using 92 dense matrix
products, without ever storing a third- or fourth-order tensor.  Four algebraic
tests pass, the installed FlopScope bills the complete isolated contraction at
`3.111411200B` FLOPs, and a synthetic small-network falsifier preserves the
material correction signs.

That success applies only to the terminal higher-cumulant channel on a frozen
Gaussian background.  The complete dual-weighted correction must also carry
the influence of each source through downstream **mean and covariance**
updates.  One exact ReLU covariance pullback turns every output's rank-one
covariance adjoint into a generic full-rank matrix.  For all `n` outputs this is
`O(n^3)` state and `O(n^4)` affine pullback work per layer.  The rank explosion
is an explicit small-`n` falsifier, not a loose tensor-counting argument.

On development indices 0--4 at the target `n=256,L=32` shape, the surviving
terminal operator reduces the full-covariance Gaussian baseline MSE by only
`2.12%` (`5.42816e-5 -> 5.31293e-5`).  It misses the registered `1.4e-6`
cheap-analytic gate by `37.95x` and regresses one of five networks.  No scorer,
locked row, or private instance was used.  The promoted champion remains the
frozen random-32,256 estimator.

## Frozen recursion contract

- Packet: `headroom_recursion/packet_adjoint_cumulant.json`.
- Champion: `h4_random32256`, SHA-256
  `1874f9cac4be962dbd4f919bffc38dedf23b428ea6cbd7847a813c87d7ba7333`.
- Official public0--99 champion score: raw `3.089512726e-7`, adjusted
  `2.257079776e-7`, mean `C=202.281790B`, max `C=250.488783B`, failures `0/100`.
- Hard resource ceiling: `C <= 272B`; promotion safety gate `Cmax < 258.4B`.
- Development firewall: indices 0--599; locked 600--799; prohibited 800--999;
  private untouched.
- Bias class of this mutation: deterministic, deliberately biased,
  leading-order/one-insertion Hermite-Born correction.
- Registered kill conditions: generic `n^4` state/work, correction-sign loss,
  duplication of a killed truncation, or budget failure before lower-order
  work.

This branch changes one mechanism only: it reverses the contraction order of
connected cumulant sources.  It does not import the killed H1 equivariant
residual fit, H2 sampler blend, or H3 rank-5 four-point sketch.

## 1. Frozen Gaussian background

For hidden ReLU layer `ell`, let the Gaussian background preactivation be

\[
Z_\ell=\mu_\ell+\xi_\ell,\qquad
\xi_\ell\sim N(0,C_\ell).
\]

Write the Gaussian derivative expectations

\[
w_{r,\ell i}=E[\rho^{(r)}(Z_{\ell i})],\qquad \rho(t)=\max(t,0).
\]

Locally, the centered Hermite expansion is

\[
\rho(\mu_i+\xi_i)-E\rho(\mu_i+\xi_i)
=w_{1i}\xi_i+\frac{w_{2i}}2:\!\xi_i^2\!:
+\frac{w_{3i}}6:\!\xi_i^3\!:+\cdots.
\]

The background means and full covariances are propagated with the already
audited full-covariance Gaussian moment matcher.  The adjoint operator does not
alter or refit that background.

## 2. Downstream response matrix

Let `P_ell` map a perturbation immediately after hidden ReLU `ell` to the final
preactivation under the linear response of every later ReLU.  With WHestBench
weights stored as `(input,output)`,

\[
P_{L-1}=W_L^T,
\qquad
P_{\ell-1}=P_\ell\operatorname{diag}(w_{1,\ell})W_\ell^T.
\]

Each `P_ell` is only `n x n`.  One reverse matrix product updates all final
outputs at once.

For one row `p` of `P_ell`, define

\[
v=C_\ell(p\odot w_{1,\ell}),
\qquad
u=p\odot w_{2,\ell}\odot v.
\]

The implementation stores rows, so it computes all `v` as

```text
V = (P * w1[None,:]) @ C.
```

## 3. Exact projected source identities

### Third cumulant

The local `LLQ` connected source is

\[
S^{(3)}_{ijk}=
w_{2i}w_{1j}w_{1k}C_{ij}C_{ik}+\text{two permutations}.
\]

Its exact goal projection is

\[
\boxed{
S^{(3)}[p,p,p]=3\sum_i p_iw_{2i}v_i^2.}
\]

This is the same Gaussian-source block present in the factorized BASE-k3
recurrence, but each source is projected once rather than appended to an
ever-growing forward CP state.

### Fourth cumulant

The retained fourth source contains the leading `LLLC` and `LLQQ` connected
diagrams.  Wick contraction gives

\[
\boxed{
S^{(4)}[p,p,p,p]
=4\sum_i p_iw_{3i}v_i^3+12u^TC_\ell u.}
\]

The first term chooses one cubic coordinate among four.  The second chooses
two quadratic coordinates; its connected Wick value is

\[
\operatorname{cum}(:\xi_a^2:,:\xi_b^2:,\xi_c,\xi_d)
=4C_{ab}(C_{ac}C_{bd}+C_{ad}C_{bc}).
\]

One additional matrix product, `U @ C`, evaluates the `LLQQ` term for every
output.  This is not a rank-5 reconstruction of a four-point vertex: it is the
exact projection of a specified local diagram family.

Summing the layer projections gives the terminal first-Born cumulants

\[
\kappa_{3,o}^{B}=\sum_\ell S^{(3)}_\ell[p_{\ell o}^{\otimes3}],
\qquad
\kappa_{4,o}^{B}=\sum_\ell S^{(4)}_\ell[p_{\ell o}^{\otimes4}].
\]

The final ReLU mutation tested

\[
\Delta m_o=rac{w_{3,Lo}}6\kappa_{3,o}^{B}
+\frac{w_{4,Lo}}{24}\kappa_{4,o}^{B},
\]

plus, as a recorded secondary variant, `w6*kappa3^2/72`.

## 4. What is and is not exact

The reverse code is algebraically exact for the declared first-Born hierarchy:

1. freeze `(mu,C)` at the Gaussian closure;
2. inject each displayed local source once;
3. transport historical order-3/order-4 sources through
   `diag(w1)^{tensor r}` only; and
4. request only terminal diagonal cumulants.

It omits source/source interactions, cumulant feedback into downstream means
and covariances, higher local Hermite diagrams such as the `Q^4` trace, and the
nonlinear terms of the full BASE-k3/k4 recurrence.  Therefore this is a biased
perturbative estimator even though its retained contractions are exact.

## 5. Exact FlopScope cost

There are 31 hidden sources at `L=32`:

- 31 products for `V`;
- 31 products for `U @ C`; and
- 30 reverse updates for `P`.

For distinct `256 x 256` operands the installed FlopScope bills each product
at `2n^3-n^2 = 33,488,896` FLOPs.  The static matmul total is therefore

\[
92(33,488,896)=3,080,978,432.
\]

The synthetic installed-runtime measurement is:

| Operation | Calls | Billed FLOPs |
|---|---:|---:|
| matmul | 92 | 3,080,978,432 |
| multiply | 464 | 24,337,664 |
| sum | 93 | 6,071,040 |
| add | 94 | 24,064 |
| **total** | | **3,111,411,200** |

Measured isolated residual wall time was `6.84 ms`.  This is an incremental
certificate only.  The frozen full-covariance background previously billed
about `6.189B` FLOPs; an integrated estimator would require a fresh official
cost run.  The contraction itself is comfortably below the budget and does
not fail the static resource gate.

## 6. Algebraic and sign falsifiers

`test_adjoint_born.py` contains four deterministic tests:

1. dense `S3` versus the projected formula (`rtol <= 3e-13`);
2. dense `S4` versus the projected formula (`rtol <= 2e-12`);
3. a three-hidden-layer dense forward `T/U` hierarchy versus the reverse
   terminal contraction (`rtol <= 3e-11`); and
4. the full covariance-adjoint rank explosion described below.

All four pass.

The independent synthetic sign premise used ten width-8, depth-4 He networks,
524,288 Gaussian inputs per network, and no dataset row.  Split-Monte-Carlo
cosines were `0.999993` for k3 and `0.999990` for k4, so sampling noise is not
the explanation for the result.

| Quantity | Born/truth cosine | Material-coordinate sign agreement |
|---|---:|---:|
| terminal k3 | 0.98195 | 91.14% |
| terminal k4 | 0.97530 | 98.72% |
| final k3 correction | 0.95142 | 98.33% |
| final k4 correction | 0.76211 | 93.33% |

The predeclared premise gate—positive correction cosine and at least 75% sign
agreement on the upper 75% absolute corrections—passes for both orders.

## 7. Why the complete dual cannot remain O(L n^3)

The terminal subchannel starts with rank-one higher-order observable adjoints,
which is why `P` suffices.  A complete score correction must also propagate the
effect of cumulants through the Gaussian mean/covariance recurrence.

For one output, the terminal covariance adjoint has rank-one form

\[
A_o=a_o w_o w_o^T.
\]

At zero mean, Price's theorem gives the exact off-diagonal derivative of a
Gaussian ReLU covariance map, holding marginal variances fixed:

\[
K_{ij}=P(Z_i>0,Z_j>0)
=\frac14+\frac{\arcsin(R_{ij})}{2\pi}.
\]

The ReLU pullback is the Hadamard product

\[
A_o\longmapsto K\odot A_o
=\operatorname{diag}(w_o)K\operatorname{diag}(w_o).
\]

For a generic correlation matrix, `K` has full rank.  Thus a single exact
pullback changes rank one into rank `n`.  The included width-8 falsifier obtains
exactly `rank 1 -> rank 8`.

After this step all `n` output slices are dense.  An affine pullback requires

\[
A_o\longmapsto W A_o W^T
\]

for every output: `O(n^3)` state and `O(n^4)` work per layer.  The slices do
not share a generic invariant basis.  Consequently the **complete**
all-output dual-weighted correction does not factor into `O(L n^3)` matrix and
Hadamard operations.

This is the goal-oriented form of the cavity/Dyson report's four-point-vertex
bottleneck.  Compressing the dense slices would need a new certified operator;
the existing rank-5 attempt cannot be reused because even its local optimal
ceiling reversed the downstream correction direction.

## 8. Target-shape premise and failure diagnosis

The bounded development probe used full-dataset indices 0--4 only, with no
official scorer:

| Method | Mean raw MSE | Change versus Gaussian |
|---|---:|---:|
| full-cov Gaussian | 5.428155e-5 | baseline |
| + adjoint-Born k3 | 5.325332e-5 | -1.89% |
| + adjoint-Born k3+k4 | 5.312933e-5 | -2.12% |
| + k3+k4+k3^2 | 5.319208e-5 | -2.01% |

The natural k3+k4 coefficients improve four of five networks but regress index
1.  The gain is real and too small by nearly two orders of magnitude.

There is nevertheless a sharp diagnostic success.  The old one-shot terminal
Hermite method predicted mean absolute skewness `0.0317`, while its public raw
oracle measured about `0.38`.  The adjoint-Born source accumulation predicts
mean absolute skewness `0.3867` across indices 0--4.  It therefore repairs the
specific **skew attenuation** caused by generating cumulants only at the last
hidden ReLU.  Its mean absolute excess-kurtosis prediction is `0.1277`, still
below the raw-oracle scale near `0.30`.

Why does the repaired skew not repair the score?  The full-covariance baseline
still has signed output-mean errors of roughly `0.002--0.005`.  Terminal
cumulant corrections have RMS scale only about `1e-3` and do not correct the
repeated Gaussian reclosure's downstream mean/covariance bias.  The exact
full-adjoint channel needed for that repair is precisely the channel whose
rank explodes.

## 9. Hyperassociations with earlier passes and failures

- **Final Hermite pass/failure:** the terminal Edgeworth formulas and raw
  cumulant oracle were right; the cumulant generator was wrong.  Layerwise
  adjoint sources restore k3 magnitude from `0.0317` to `0.3867`, validating
  that diagnosis.
- **Factor-k3 cost failure:** forward historical factor transport repeats old
  work and grows as `O(L^2 n^3)`.  Reversing only the terminal diagonal query
  folds the same leading Gaussian sources into `3.11B` incremental FLOPs.
- **Cavity/Dyson no-go:** the generic four-point state did not disappear.  It
  reappears exactly as dense output-specific covariance-adjoint slices when
  the full observable, rather than terminal cumulants, is differentiated.
- **Rank-5 k4 failure:** the present k4 formula avoids its failure because it
  projects each local `LLLC+LLQQ` source before transport.  It does not repair
  the rank-5 sketch's unstable recurrent vertex, so that branch remains dead.
- **H1 equivariant residual failure:** no offline residual model is used; the
  formulas are weight-analytic and symmetry-covariant by construction.
- **H2 coefficient-transfer failure:** no learned sampler/analytic mixing
  coefficient is fitted.  The natural cumulant coefficients are fixed by the
  Hermite expansion.  The index-1 regression is evidence against rescuing this
  result with post-hoc coefficient tuning.
- **Promoted random-32,256 champion:** nothing here passes the matched-screen
  gate needed to alter it.  The champion remains immutable.

## 10. Reproducibility and verdict

Files:

- `adjoint_born.py`: NumPy reference implementation and static matmul count;
- `test_adjoint_born.py`: dense tensor identities and rank falsifier;
- `run_sign_premise.py`: synthetic small-network sign test;
- `measure_flopscope.py`: isolated installed-runtime cost measurement;
- `public_premise.py`: guarded public0--4 target-shape premise; and
- `premise_results.json`: machine-readable summary.

Commands:

```powershell
..\..\whest-v014\Scripts\python.exe -m unittest -v test_adjoint_born.py
..\..\whest-v014\Scripts\python.exe run_sign_premise.py
..\..\whest-v014\Scripts\python.exe measure_flopscope.py
..\..\whest-v014\Scripts\python.exe public_premise.py
```

The strongest honest conclusion is two-part:

1. terminal goal projection is a valid new operator and explains where much of
   the missing skew is manufactured; but
2. it is not a winning estimator, while the full mean/covariance dual that
   might matter is generically outside the required `O(L n^3)` envelope.

This recursion leaf is recorded as a hard kill for promotion, with its exact
terminal fold preserved for future theory rather than silently tuned.

