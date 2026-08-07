# M111 causal-link attack: what the gate interferometer does and does not know

**Date:** 2026-08-07  
**Scope:** mathematics only. No contest weight, forward evaluator, target,
submission, or generated network was opened, run, or changed.  
**Disposition:** `causal sufficiency disproved`; the exact centered-pair
observable is retained, but its claimed connection to the deep output is an
ensemble-specific premise, not a consequence of `W1` and the ungated product.

## Executive result

The proposed M111 control is an exact, useful *measurement* of a normal-ordered
pair field of the first-layer gates.  It is not, however, a universal
measurement of the output residual.  There is a one-parameter family of
bias-free, depth-three ReLU networks with exactly the same `W1`, the same
ungated transport

\[
T=D W_2 W_3,
\]

and hence the same M111 control at every input, but with different spherical
means, different even directional residuals, and different covariance with
that identical control.  Thus no function of `(W1,T,Sigma)` can universally
provide M111's missing output-phase coefficient.

The strongest statement that survives is narrower: for the *specified random
weight ensemble*, an M111 coefficient can be a legitimate held-out control
coefficient if it empirically transfers.  It cannot be justified from the
first gate covariance and an ungated product alone.  A deep independent-gate
annealed reference also gives a hostile leading diagram: its two-leg overlap
is suppressed by `2^(-(L-2))`, with ordinary finite-width corrections of
relative order `L/n`.  This is not a theorem that the actual finite network
has zero overlap; it identifies precisely the nonperturbative/connected
mechanism that would have to be demonstrated to overcome the baseline.

## 1. Exact object and exact missing coefficient

For active normalized first-layer normals `a_i`, set

\[
v_i(U)={1\over2}\operatorname{sign}(a_i^T U),\qquad
\Sigma_{ik}=E[v_i(U)v_k(U)]={\arcsin(a_i^Ta_k)\over2\pi}.
\]

For one nondegenerate output column `t`, let `s=t^T Sigma t`.  Define the
centered pair atoms and the M111 observable by

\[
 \psi_{ik}(U)=v_i(U)v_k(U)-\Sigma_{ik}\quad(i<k),
\]
\[
 h_t(U)={2\over s}\sum_{i<k}t_i t_k\psi_{ik}(U).
 \tag{1}
\]

Equation (1) is just the normal-ordered-square identity: the diagonal terms
are identically zero because `v_i^2=Sigma_ii=1/4`.  It proves `E h_t=0`, but
not a relationship to the output.

Let `g(U)=(f(U)+f(-U))/2`; this is the even integrand actually relevant after
antipodal pairing, and `h_t` is already even.  Define

\[
B_{ik}(f)=E\big[(g-Eg)\psi_{ik}\big]
          =E[g v_i v_k]-(Eg)\Sigma_{ik}.                         \tag{2}
\]

Then the exact causal identity is

\[
 \operatorname{Cov}_U(g,h_t)
 ={2\over s}\sum_{i<k}t_i t_k B_{ik}(f).                         \tag{3}
\]

`B` is the connected output--two-gate tensor.  It contains every omitted
downstream gate and every amplitude dependence.  `Sigma` supplies only the
two-gate marginal; `T` supplies only an ungated signed path.  Neither
determines (2).

This statement can be made as an exact projection rather than a slogan.  Let
`Q=span{psi_ik:i<k}` in `L2(S^(d-1))` and write

\[
g-Eg=P_Q(g-Eg)+r,\qquad r\perp Q.
\]

Since `h_t` belongs to `Q`, there is no hidden remainder in (3):

\[
\langle g-Eg,h_t\rangle=\langle P_Q(g-Eg),h_t\rangle,
\qquad \langle r,h_t\rangle=0.                                 \tag{4}
\]

The unknown is exactly the `Q`-projection of the real gated network, not a
numerical approximation to `Sigma`.

## 2. The frame version and an explicit harmonic remainder

For a Haar orthonormal frame `Qe_1,...,Qe_d`, write

\[
 A_Q a={1\over d}\sum_{r=1}^d a(Qe_r).
\]

Antipodal duplicates do not change this expression when both fields are even.
If `a_l,b_l` denote degree-`l` spherical-harmonic projections and `P_l` is
normalized by `P_l(1)=1`, the standard conditional zonal identity at an
orthogonal pair gives

\[
 \operatorname{Cov}_Q(A_Qg,A_Qh_t)
 ={1\over d}\sum_{l\ge1}\{1+(d-1)P_l(0)\}\langle g_l,(h_t)_l\rangle .
 \tag{5}
\]

Only even degrees occur for `h_t` and the relevant part of `g`.  In particular
`P_2(0)=-1/(d-1)`, so the frame kills the degree-two contribution exactly.
The quantity that has to be nonzero for M111 is therefore the *higher-even*
part of (2), not the raw direction-level covariance.

For any even cut-off `K`, (5) has the controlled decomposition

\[
 C_{\rm frame}= {1\over d}\sum_{2\le l\le K}R_l
     \langle g_l,(h_t)_l\rangle+\mathcal R_K,
 \quad R_l=1+(d-1)P_l(0),
\]
\[
 |\mathcal R_K|\le {1\over d}
 \left(\sum_{l>K}R_l^2\|(h_t)_l\|_2^2\right)^{1/2}
 \left(\sum_{l>K}\|g_l\|_2^2\right)^{1/2}.                    \tag{6}
\]

The first factor in (6) is weights-only and can be bounded from the control;
the second is the real network's unobserved high-even residual.  This makes
the missing causal link explicit rather than burying it in a metaphor.

## 3. Rigorous counterexample: a continuum with identical M111

The counterexample uses two first-layer gates and one scalar output.  It
embeds in any larger input/hidden width by adding identically unconnected
coordinates, so it is a counterexample to any universal claim at width 256 as
well.  It is not claimed to be a typical He draw; that is unnecessary to
disprove sufficiency of `(W1,T)`.

Take `d>=2`, `W1=[e1,e2]`, and hence `D=I`, `a1=e1`, `a2=e2`.  For each
`a>=0`, let

\[
 W_2(a)=\begin{pmatrix}1&-a\\0&1\end{pmatrix},\qquad
 W_3(a)=\begin{pmatrix}1+a\\1\end{pmatrix}.                   \tag{7}
\]

Every member has the same ungated transport:

\[
 W_2(a)W_3(a)=\begin{pmatrix}1\\1\end{pmatrix}=t.             \tag{8}
\]

Put `r_1=(U_1)_+`, `r_2=(U_2)_+`.  Its final preactivation, and therefore its
final rectified output, is nonnegative and equals

\[
 f_a(U)=(1+a)r_1+(r_2-a r_1)_+
       =f_0(U)+(a r_1-r_2)_+,\qquad f_0=r_1+r_2.                 \tag{9}
\]

Meanwhile the M111 ingredients are independent of `a`:

\[
\Sigma={1\over4}I_2,\quad s={1\over2},\quad
h_t(U)=\operatorname{sign}(U_1)\operatorname{sign}(U_2).       \tag{10}
\]

Let `R=(U_1^2+U_2^2)^(1/2)`.  The angle in this plane is uniform and independent
of `R`, with

\[
 \bar R_d=E R={\Gamma(3/2)\Gamma(d/2)\over\Gamma((d+1)/2)}.
\]

The two elementary angular integrals are exact:

\[
 E[f_a-f_0]
 ={\bar R_d\over2\pi}\{a+\sqrt{1+a^2}-1\}>0,                 \tag{11}
\]
\[
 \operatorname{Cov}(f_a,h_t)
 ={\bar R_d\over2\pi}\{\sqrt{1+a^2}-1-a\}<0\quad(a>0),      \tag{12}
\]

where `Cov(f_0,h_t)=0`.  For (12), the positive first-quadrant contribution
is `sqrt(1+a^2)-1`; the fourth-quadrant contribution is `-a`.

Thus identical `W1`, `Sigma`, `T`, `s`, and pointwise `h_t` coexist with
different means and a continuously varying output-control covariance.  The
even part of `f_a-f_0` is also nonconstant: it is `a/2` at `e1` and zero at
`(e1+a e2)/sqrt(1+a^2)`.  Its ReLU wedge boundaries give an infinite even
harmonic tail.  Hence the directional residual harmonic content changes too.

Small generic perturbations of the added zero connections preserve the strict
inequalities in (11)--(12); the construction is not relying on a fragile
mean-zero equality.  The exact product equality can always be maintained by
the compensating factorization in (7).

### 3.1 Stronger: the He ensemble has the same hidden factorization fibre

The preceding construction already disproves a universal deterministic map.
There is also an exact measure-preserving transformation inside the stated He
ensemble.  Let `A` be any fixed non-monomial orthogonal matrix at an internal
width, and replace two adjacent hidden matrices by

\[
 W_2'=W_2A,\qquad W_3'=A^TW_3.                                  \tag{A1}
\]

The ungated product, and therefore `T`, is unchanged.  So are `W1`, `Sigma`,
and the entire pointwise M111 field.  The intervening computation instead
contains

\[
 \operatorname{ReLU}(rW_2A)A^TW_3,
\]

which generically differs from `ReLU(rW2)W3` because ReLU does not commute
with a non-monomial rotation.

If `W2,W3` are independent matrices with iid He Gaussian entries, `W2A` and
`A^TW3` are again independent matrices with iid He Gaussian entries.  Hence
(A1) maps the exact contest ensemble to itself while fixing M111.  The output
is therefore not almost surely a function of `(W1,T,Sigma)` under that
ensemble; a nonzero conditional output variation remains along an M111 fibre.
The strict inequalities in (A3)--(A4) persist under small weight
perturbations, an open set of positive He density, so this is not a
measure-zero witness.

For an explicit nonzero-control witness, take `W1=[e1,e2]`, `W2=I`, and
`W3=t=(1,1)^T`.  Let

\[
 A=\begin{pmatrix}c&-s_\theta\\s_\theta&c\end{pmatrix},
 \qquad c=\cos\theta,\quad s_\theta=\sin\theta,
 \quad 0<\theta<\pi/4.
\]

With `r_i=(U_i)_+`, the base and rotated-factorization scalar outputs obey

\[
 f_\theta=f_0+(c-s_\theta)(s_\theta r_1-cr_2)_+,
 \qquad f_0=r_1+r_2.                                           \tag{A2}
\]

Both are nonnegative before the final ReLU.  The product transport remains
`t`, so `h_t=sign(U1)sign(U2)` exactly as in (10).  Direct angular integration
gives, with the same `bar R_d` as above,

\[
 E[f_\theta-f_0]
 ={\bar R_d\over2\pi}(c-s_\theta)(1-c+s_\theta)>0,             \tag{A3}
\]
\[
 \operatorname{Cov}(f_\theta,h_t)
 ={\bar R_d\over2\pi}(c-s_\theta)(1-c-s_\theta)<0.             \tag{A4}
\]

Thus the ensemble-preserving rotation can leave a *nonzero* M111 field fixed
while changing both its target mean and its raw output covariance.  The even
part of (A2) is nonconstant and has a ReLU wedge boundary, so its higher-even
harmonic content changes as well.

For a compact quantified deterministic check, set `W2=W3=I2` and insert the
nonorthogonal shear `A=[[1,-1],[0,1]]` with its inverse.  The two-output map
changes from `(X_+,Y_+)` to `(X_+,max(X_+,Y_+))`, while `T=I2` and both M111
controls are identically zero because each output transport has one-gate
support.  For independent standard Gaussian `X,Y`, the second-output mean
changes from `1/sqrt(2*pi)` to `(1+sqrt(2))/(2*sqrt(pi))`, an exact gap
`1/(2*sqrt(pi))`.  This shear is not needed for ensemble preservation; it is
a numerical witness to the same lost-factorization information.

## 4. What the counterexample kills, and what it does not

It kills the following universal inference:

```text
(W1, D W2...WL, arcsine gate covariance)  ->  output residual phase
```

It does **not** kill the exact-zero identity, the invariances, or the
possibility that the stated Gaussian He ensemble has a nonzero average value
of (3).  It changes the required evidence:

1. `h_t` may be used only as a prospectively fixed control with independent
   held-frame validation.
2. A theoretical coefficient must condition on a factorization-aware object,
   such as the tensor `B_ik(f)` in (2), actual downstream gate correlations,
   or an explicitly justified posterior over factorizations given `T`.
3. No amount of better arithmetic for `Sigma` or the ungated product repairs
   this informational loss.  Those are already exact in the counterexample.

## 5. Annealed Hermite/Wiener-chaos calculation: the leading deep overlap

This section is deliberately labelled an **annealed reference calculation**,
not a theorem for the finite realized network.  It tests whether the simplest
diagram already supplies M111's desired phase.

Use a reference in which hidden gates after layer one are independent
Bernoulli-half masks, while each hidden matrix has entries of variance `2/n`.
For a row vector `x`, this gives the exact reference recursions

\[
 E\|xW\|^2=2\|x\|^2,\qquad E\|xW\Gamma\|^2=\|x\|^2.         \tag{13}
\]

There are `m=L-2` matrices between the first rectification and the final
linear readout.  Conditional on those matrices, write the actual penultimate
activation as `b(U)` and the ungated M111 pre-readout vector as

\[
 p(U)=\{v(U)^T D W_2\cdots W_{L-1}\}^T.
\]

For the last Gaussian readout `w`, let `Z=b^Tw` and `Q=p^Tw`.  The no-index-
collision (rainbow) contraction of (13), averaged over the first gate, gives

\[
 V_Z\simeq {2\over n},\qquad V_Q\simeq2^m,\qquad
 C=E[ZQ]\simeq\sqrt{2\over\pi n}.                              \tag{14}
\]

The last equality is the first-layer contraction
`E[r_1^T Dv]=n E[(a^TU)_+]\simeq sqrt(n/(2*pi))`; every matched
`W Gamma W^T` pair at later layers has unit gain.  In contrast, an ungated
`W W^T` pair has gain two.  Therefore the leading correlation is

\[
 r_0={C\over\sqrt{V_ZV_Q}}
 \simeq {1\over\sqrt\pi}\,2^{-m/2}
 ={1\over\sqrt\pi}\,2^{-(L-2)/2}.                              \tag{15}
\]

Here the fixed-network denominator `s=E_U Q(U)^2` has been replaced by its
annealed self-averaging value `V_Q`.  That is a large-width reference step,
not an exact identity; its possible failure is one reason the frozen M111
conditioning and tail gates remain necessary.

The sign field has the ordinary Gaussian Hermite expansion

\[
 v_i={1\over\sqrt{2\pi}}Z_i+\text{odd chaoses of order }3,5,\ldots .
\]

Consequently the leading part of `h_t` is a normal-ordered second chaos.  The
odd part `Z/2` of `ReLU(Z)=(Z+|Z|)/2` cannot couple to that even chaos.  For a
centered Gaussian pair `(Z,Q)`, direct conditioning gives

\[
 \operatorname{Cov}\left(\operatorname{ReLU}(Z),{Q^2\over V_Q}-1\right)
 ={C^2\over\sqrt{2\pi}\sqrt{V_Z}V_Q}
 ={\sqrt{V_Z}\over\sqrt{2\pi}}r_0^2.                           \tag{16}
\]

Thus the first available two-leg ReLU diagram pays

\[
 r_0^2\simeq {1\over\pi}\,2^{-(L-2)}.                          \tag{17}
\]

At `L=32`, this factor is about `2.96e-10` before the additional removal of
the degree-two frame component in (5).  Equation (17) is a baseline
suppression, not an upper bound on the real M111 covariance: actual
gate--weight dependencies can create connected diagrams absent from this
reference.

The conventional width accounting explains the next uncertainty.  A diagram
that joins two otherwise independent paths at one selected layer loses one
free index (`1/n`) but has `O(L)` possible layer locations.  The ordinary
finite-width correction to the rainbow result is therefore relative
`O(L/n)`; at the contest shape it is `1/8`, not a factor capable by itself of
repairing (17).  A successful M111 result would consequently be evidence for
a qualitatively different connected/resummed mechanism that removes some of
the missing-gate suppression, not for a routine low-order `L/n` correction.

## 6. Falsifiable uncertainty map

| Uncertainty | Mathematical content | What resolves it without story-telling |
|---|---|---|
| Factorization dependence | `B_ik(f)` is not fixed by `(W1,T)` | held frame covariance of (3), with whole networks as units |
| Deep gate mismatch | rainbow overlap has `2^(-(L-2))` penalty | a factorization-aware connected-diagram derivation or a stable held effect |
| Frame survival | degree two is exactly annihilated | measure/compute the `l>=4` part through (5), not raw-direction correlation |
| Finite-width rescue | ordinary corrections scale `L/n` | show a named diagram family whose multiplicity cancels the exponential mismatch |
| Heavy normalized tails | `s` can be small even when mean is exact | frozen `s`, kappa, and frame-tail gates before any output forward |

## Final disposition

M111 remains a correctly normal-ordered, symmetry-respecting **candidate
control**. Its causal story must be weakened from "the ungated transport
routes the true output phase" to "a pair-gate observable is tested for
ensemble-specific transferred covariance." The counterexample makes that
distinction rigorous.  The annealed calculation explains why the test is
hostile at depth 32: the simplest allowed overlap is both even-chaos and
deep-gate mismatched, while the frame removes its lowest even mode.

No coefficient, frequency, or backup mixture may be selected from this
analysis.  The only lawful promotion path is the already frozen independent
control-first and held-frame ladder.
