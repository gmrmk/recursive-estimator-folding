# M120B: corrected shared-CP coupled `(mu,C)` Jacobian implementation

> Superseded for protocol purposes by
> [`M120C_EXACT_PROTOCOL_HARNESS_20260807.md`](M120C_EXACT_PROTOCOL_HARNESS_20260807.md).
> This M120B note records a prior exploratory component run only.  Its former
> runner is now inert and its generated results are not binding evidence for
> M120C.

**Verdict: `READY_FOR_INDEPENDENT_COMPONENT_KILL`.**  The target-free
implementation validates the corrected algebra, including its central
covariance diagonal and signed reset, but the generated small-width dense
oracle rejects the `E=0` approximation required to make it cheap.  No
correction, source construction, terminal-Born composition, target, scorer,
contest/public outcome, champion access, or target-shape efficacy experiment
was accessed or executed.

## Scope and source ownership

This is a component audit only.  It implements the full Gaussian ReLU reverse
for mean and **central covariance** and its M120 normal-ordered `E=0` shared-CP
base.  It does not implement a weights-only feedback source.  Therefore the
following ownership remains explicitly absent:

- no `LLQ`, `LLLC`, or `LLQQ` source is formed;
- no terminal Born correction is added or subtracted;
- no correction oracle or full correction experiment exists in this directory.

The implementation is [`corrected_cp_jacobian.py`](../m120_price_normal_ordered_adjoint/corrected_cp_jacobian.py), the fixed generated-only runner is
[`run_corrected_cp_generated.py`](../m120_price_normal_ordered_adjoint/run_corrected_cp_generated.py), and the standard-library tests are
[`test_corrected_cp_jacobian.py`](../m120_price_normal_ordered_adjoint/test_corrected_cp_jacobian.py).

## Complete local pullback

Let `z ~ N(mu,C)`, `h = ReLU(z)`, `v_i=C_ii`,
`sigma_i=sqrt(v_i)`, `alpha_i=mu_i/sigma_i`, and

\[
p_i=\Phi(\alpha_i),\qquad r_i=\frac{\phi(\alpha_i)}{2\sigma_i}.
\]

For the post-ReLU mean `m` and central covariance `V`, the required diagonal
derivatives are

\[
\frac{\partial m_i}{\partial\mu_i}=p_i,\qquad
\frac{\partial m_i}{\partial v_i}=r_i,
\]

\[
\frac{\partial V_{ii}}{\partial\mu_i}=2m_i(1-p_i),\qquad
\frac{\partial V_{ii}}{\partial v_i}=p_i-2m_i r_i.
\]

At `mu=0`, `v=1`, this gives

\[
\frac{\partial\operatorname{Var}[\operatorname{ReLU}(Z)]}{\partial v}
=\frac12-\frac1{2\pi}=0.3408450569081046,
\]

not `.5`.  `.5` differentiates the raw second moment and misses the derivative
of `m_i^2`.  The central finite-difference oracle gave
`0.340845056906458`, an absolute error of `1.65e-12`.

For `i != j`, the covariance Price derivative is

\[
K_{ij}=P(z_i>0,z_j>0),
\]

and the full dense covariance block uses `K_ij A_ij` off diagonal.  Define
rowwise derivative matrices

\[
H^\mu_{ij}=\partial_{\mu_i}V_{ij},\qquad
H^v_{ij}=\partial_{v_i}V_{ij}.
\]

The tests generate these matrices by central differences of the existing
full-covariance Gaussian closure.  With symmetric covariance adjoints and the
Frobenius pairing, their exact contractions are

\[
c^x_i=2\sum_j A_{ij}H^x_{ij}-A_{ii}H^x_{ii},\qquad x\in\{\mu,v\}.
\]

Thus the complete local reverse is

\[
b_i^z=p_i b_i^h+c^\mu_i,
\qquad
\delta_i^z=r_i b_i^h+c^v_i,
\]

with the covariance diagonal overwritten by `delta`, not by `p_i A_ii`.

## Shared-CP realization and signed reset

For every terminal output simultaneously, store

\[
A^{h,o}=U\,\operatorname{diag}(G_o)\,U^T.
\]

The CP form of the cross contraction is

\[
c^x=2\,[U\odot(H^xU)]G^T-
\operatorname{diag}(A)\odot\operatorname{diag}(H^x).
\]

The base retains `p p^T` off diagonal.  Its pre-affine factors and reset are

\[
U_{pp}=\operatorname{diag}(p)U,
\qquad
G_{\rm reset,o i}=\delta^z_{i,o}-p_i^2\sum_sU_{is}^2G_{o s}.
\]

The reset is signed; it is represented by identity atoms locally.  Through an
affine map `W`, only `W @ U_pp` is a variable-rank GEMM; the reset identity
columns become literal columns of `W`.  This retains the rank ledger without
hiding reset work or incorrectly forcing a positive semidefinite diagonal.

## Dense-oracle and invariance results

The direct dense central-difference test differentiates every input mean,
every variance, and each independent symmetric off-diagonal covariance
coordinate.  It tests all output channels together.  On the `E=0` diagonal
covariance case (`width=4`, `outputs=5`, CP rank 7):

| comparison | norm of difference |
|---|---:|
| full dense analytic pullback vs direct finite-difference oracle, mean | `6.21e-11` |
| full dense analytic pullback vs direct finite-difference oracle, covariance | `5.71e-11` |
| shared CP base vs dense base, mean | `3.12e-15` |
| shared CP base vs dense base, covariance | `1.88e-15` |

The fixed generated network grid used widths `3,4,5`, depths `3,4` (depth
includes the final affine), two deterministic replicas each, and **all**
terminal outputs at each width.  Exact shared-CP/base agreement is strict:

| metric over all cases and outputs | result | gate |
|---|---:|---:|
| maximum CP/base mean relative error | `7.08e-15` | `1e-10` |
| maximum CP/base covariance relative error | `3.09e-15` | `1e-10` |

The generated rank ledgers are exactly `n,2n,...,depth*n`; for example,
width 5/depth 4 is `[5,10,15,20]`, while the ranks entering the three reverse
ReLU maps are `[5,10,15]`.

Strict representation tests also pass: a positive hidden gauge leaves the
terminal means unchanged and maps the input-facing adjoints as
`b' = D^-1 b`, `A' = D^-1 A D^-1`; a hidden permutation maps them as
`b' = P^T b`, `A' = P^T A P`.  The test tolerances are `1e-9`; observed errors
in the fixed width-4/depth-4 case are approximately `1.5e-11` for the gauge
covariance and `5.5e-12` for the permutation covariance.

## The required `E` gate fails

The full dense oracle retains the connected Price residual

\[
E=K-[pp^T+\operatorname{diag}(p-p^2)].
\]

This term is deliberately absent from the cheap shared-CP base.  The
predeclared all-output gate was mean relative covariance error at most `.05`
and maximum at most `.10`.  The direct generated-only comparison of the base
to the full dense recurrence gives:

| metric over all fixed cases and terminal outputs | result | gate |
|---|---:|---:|
| mean base/full covariance relative error | `0.3706` | `.05` |
| maximum base/full covariance relative error | `3.2006` | `.10` |

This is a clear rejection of the approximation, independent of correction
quality or any target.  The exact factorization tests validate the repair's
algebra but cannot promote the estimator, because making `E` exact would lose
the advertised bounded shared-CP recurrence.

## Independent cost cross-check

Using the report's FlopScope convention
`M(a,b,c)=2abc-ac`, `n=O=256`, and 31 hidden ReLU maps, the implementation
independently obtains:

| operation | calls | Flops |
|---|---:|---:|
| `diag(A)=G@(U*U).T` | 31 | `16,640,966,656` |
| one of the two cross blocks | 62 | `33,251,459,072` |
| affine `U_pp=W@(p*U)` | 30 | `15,572,336,640` |
| affine mean adjoint | 30 | `1,004,666,880` |
| complete reverse | **215** | **`99,720,888,320` = `99.72088832B`** |
| plus existing Gaussian background (`6.189B`) | — | **`105.90988832B`** |

So the earlier rounded `99.721B` reverse and `105.910B` including background
remain correct.  This excludes pointwise work, bivariate-CDF/derivative
construction, copies, and any absent source.

## Reproduction

```powershell
& 'work\whest-v014\Scripts\python.exe' `
  'work\scorefloor_generation\m120_price_normal_ordered_adjoint\test_corrected_cp_jacobian.py'

& 'work\whest-v014\Scripts\python.exe' `
  'work\scorefloor_generation\m120_price_normal_ordered_adjoint\run_corrected_cp_generated.py' --aggregate-only
```

The tests are all target-free and pass.  The runner intentionally returns
`READY_FOR_INDEPENDENT_COMPONENT_KILL`, because the distinct connected-Price
residual gate fails.  It must not be escalated into a correction or full
target experiment.
