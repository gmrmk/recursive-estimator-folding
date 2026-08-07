# M165: rank-face-subtracted Plackett mutation

## Decision

**SCREENED RANK-ONE SURVIVOR; GENERIC ALL-PSD PROVIDER REMAINS UNRESOLVED.** M162 correctly killed a fixed common-node rule applied to an opaque trivariate probability. M165 changes that failed link: it combines the Tallis raw-moment algebra, connected `[2,1,1]` cumulant, and M129 tree before taking the rank-face limit. On a centered near-rank-one path, the divergent probability-derivative terms cancel in the combined defect and leave a controlled fractional-power endpoint term.

This is not a generic provider and receives no operation credit. In particular, M154 supplies the needed anchor at rank one only; it cannot anchor a rank-two face. No response/truth/scorer/leaderboard/submission/champion information is accessed.

## 1. Combined object before differentiation

Let `T(u)` be Tallis's truncated-normal MGF from M162 and obtain the twelve raw moments `M_{p0p1p2}` by differentiation. Define the *combined* scalar

\[
\mathcal D(\Sigma)=\left[C_{211}-V_{00}V_{12}-2V_{01}V_{02}\right]
-\operatorname{tree}(0,0,1,2). \tag{1}
\]

This is `Delta_211`, not an individual `P3` derivative. Along a PSD opening

\[
\Sigma_\epsilon=aa^T+\epsilon B,\qquad B\vert_{a^\perp}\succeq0,\tag{2}
\]

the correct Plackett/Price integrand is

\[
G_B(\epsilon)={d\over d\epsilon}\mathcal D(\Sigma_\epsilon),\tag{3}
\]

after the entire raw-moment centralization and tree algebra has been applied. Differentiating `P3` first is invalid numerically: its threshold/correlation derivatives contain rank-face divergences that cancel only after (1) is assembled.

M154 owns both `D_0=mathcal D(aa^T)` and the one-sided PSD directional coefficient `D_B=G_B(0+)` for this rank-one anchor and direction. The rank-face-subtracted identity is

\[
\mathcal D(\Sigma_\epsilon)=D_0+\epsilon D_B+
2\epsilon\int_0^1v\,[G_B(\epsilon v^2)-D_B],dv. \tag{4}
\]

The `v^2` map is parameter aware: it isolates the only rank-face endpoint at `v=0`; it is not M149's fixed outer normal quadrature.

## 2. Centered equicorrelation prototype

The packet studies the exact positive-marginal path

\[
\Sigma_\epsilon=(1-\epsilon){\bf1}{\bf1}^T+\epsilon I,
\qquad 0<\epsilon<1. \tag{5}
\]

Condition on the common factor `Z`. With `s=sqrt(epsilon)`, each coordinate is
`sqrt(1-epsilon) Z+s E_i`, and the three rectified variables are conditionally independent. For powers `p=0,1,2`, the conditional moments are

\[
g_0=1,\quad g_1=s\phi(\alpha)+m\Phi(\alpha),\quad
g_2=(m^2+s^2)\Phi(\alpha)+ms\phi(\alpha),\quad\alpha=m/s. \tag{6}
\]

Every raw moment in (1) is the one-dimensional integral

\[
M_{pqr}=\int\phi(z)g_p(z)g_q(z)g_r(z)\,dz.\tag{7}
\]

The prototype uses (7) only as a high-precision reference and combines the central moment, cumulant, and M129 repeated tree *before* calculating the defect. It is not a runtime quadrature proposal.

For (5), high-precision values give

\[
\mathcal D(\Sigma_\epsilon)=D_0+D_B\epsilon+A\epsilon^{3/2}+O(\epsilon^2),\tag{8}
\]

with

\[
D_0=-0.9303111372675952035464968645\ldots,
\qquad D_B=3.983346315428913\ldots,
\qquad A\approx-1.4681.\tag{9}
\]

The `D_0` value is M154's exact common-factor identity; `D_B` is M154's exact rank-one cone tangent, represented in the prototype to the retained float64 source precision. At `epsilon=1e-6`, the independently integrated residual divided by `epsilon^(3/2)` lies in `(-1.49,-1.46)`.

Equation (8) implies

\[
G_B(u)=D_B+\tfrac32A\sqrt u+O(u).\tag{10}
\]

Substitution into (4) makes the endpoint integrand `O(epsilon^(3/2) v^2)` rather than singular. This is the desired analytical cancellation against the M154 rank-one limit.

## 3. What a rigorous M159 certificate would require

For each rank-one state and cone direction, a future implementation would need a symbolic factorization proving an interval bound such as

\[
\left|G_B(u)-D_B-\tfrac32 A_B\sqrt u\right|\le C_Bu,
\quad 0\le u\le\epsilon_*. \tag{11}
\]

Then (4) has the direct enclosure

\[
\left|\mathcal D-D_0-\epsilon D_B-A_B\epsilon^{3/2}\right|
\le\tfrac12 C_B\epsilon^2.\tag{12}
\]

That dimensionless enclosure may travel through M159's exact `2^(4e)` carrier. The generic kernel must still supply a mixed absolute/relative bound away from the endpoint and include all floating point and source-accumulation errors. The high-precision prototype provides none of these interval constants.

## 4. Rank-two, zero-face, and cost verdict

The mutation cannot meet the requested all-PSD scope:

- **Rank one / near rank one:** M154 provides `D_0,D_B`; (4) is a valid new analytic direction. The equicorrelation experiment demonstrates a nonzero `epsilon^(3/2)` term, so subtracting only the value is insufficient.
- **Rank two, positive marginals:** a separate rank-two anchor and directional derivative are required before (4) can be formed. M154 does not provide either. Taking an unanchored Plackett limit returns to M162's opaque endpoint problem.
- **Zero marginal variance:** the M159 deterministic/one-sided conic dispatch remains mandatory; correlation coordinates and an ordinary two-sided tangent are not defined there.
- **Interior SPD:** direct Plackett/Tallis jets remain mathematically available, but their cancellation must be factored before interval evaluation.

Consequently, a fixed parameter-aware split plus an analytic singular kernel is **not yet a rigorous generic solution within `606,720` billed operations**. The centered rank-one prototype shows that such a kernel exists in one direction; it does not provide the rank-two formulas, interval coefficients, jet implementation, or native cost trace needed to assert the cap. Raising fixed quadrature order would not address those missing proofs.

For clarity on the requested rank-two asymptotics: if a rank-two support plane has positive marginals and crosses every ReLU kink transversely, Price's distributional derivative gives a direction-dependent `O(epsilon)` boundary integral. That coefficient depends on the rank-two plane and its opening normal, not on M154's rank-one `D_0,D_B`. At a nontransverse contact (or any zero marginal) this expansion changes and must be handled by the explicit conic/zero-face route. Hence there is no single rank-two singular kernel that can be inferred from the rank-one subtraction in (4).

## 5. Tests and references

The isolated M165 tests use the pre-existing high-precision runtime only for a response-free reference:

1. exact common-factor limit agrees with M154 to `3e-14`;
2. the `epsilon=1e-3` high-precision interior value agrees with the independent M147 paired-order endpoint reference to `4e-9`;
3. subtraction of the M154 value and tangent leaves the nonzero `epsilon^(3/2)` remainder;
4. the prototype explicitly dispatches its one derived rank-one common-factor route and refuses a rank-two anchor or zero-marginal face rather than silently extending its domain.

The arguments use [Tallis (1961)](https://doi.org/10.1111/j.2517-6161.1961.tb00408.x) for the truncated MGF, [Plackett (1954)](https://doi.org/10.1093/biomet/41.3-4.351) for correlation differentiation, and [Price (1958)](https://doi.org/10.1109/TIT.1958.1057444) for Gaussian covariance differentiation. [Wang and Kennedy (1992)](https://doi.org/10.1016/0167-9473(92)90007-3) is retained as primary evidence that interval/automatic-differentiation self-validation is the appropriate missing numerical component.

## Disposition

`SCREENED_RANK1_RANK_FACE_SUBTRACTION_SURVIVOR; KILL_VALUE_ONLY_OR_OPAQUE_P3_DIFFERENTIATION; GENERIC_RANK2_ZERO_FACE_AND_606720_CERTIFICATE_UNRESOLVED`.
