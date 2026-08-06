# Cavity/Dyson/TAP branch: scoped hard no-go

## Decision

**Kill the proposed variance/skew Dyson-TAP closure as an identified
`O(L n^3)` estimator for the fixed-weight ReLU mean.**

This is not a universal complexity lower bound. It is a hard no-go for the
specific mechanism tested here: a self-consistent resummation whose state is
only mean/covariance/skew (plus a susceptibility or scalar self-energy), and
whose justification is imported from random-weight finite-width diagrams or
TAP/AMP. There are two independent failures:

1. a one-pass feed-forward graph has no Onsager self-reaction; and
2. covariance plus even the **full** third cumulant does not close a ReLU step.
   The first missing source is a joint four-point vertex, whose generic
   fixed-instance state/cost exceeds the requested envelope.

No public truth, scorer, target, or forward pass was consulted. The only score
number quoted below is the existing dossier's requested second-moment oracle
cap; it was not recomputed.

## Problem and conditioning

For fixed realized weights,

\[
h_0=X\sim N(0,I),\qquad z_\ell=W_\ell h_{\ell-1}+b_\ell,
\qquad h_\ell=\rho(z_\ell),\quad \rho(t)=\max(t,0),
\]

and the target is `E_X[f_W(X) | W]`. This conditioning is decisive. The
finite-width diagram papers average over random weights. Their zero odd moments,
neuron exchangeability, and Kronecker-delta vertex structures do not hold for a
generic realized `W`.

[Yaida (2020)](https://proceedings.mlr.press/v107/yaida20a.html) is particularly
diagnostic: even in the easier Gaussian-weight ensemble, the leading non-Gaussian
recursion needs a kernel, a two-point self-energy, and a connected four-point
vertex. The self-energy is not closed by itself. The more recent rank-four
Feynman treatment of [Guillen, Misof, and Gerken
(2025)](https://arxiv.org/abs/2508.11522) adds multiple vertex tensors rather
than collapsing them to one variance correction. [Dyer and Gur-Ari
(2020)](https://arxiv.org/abs/1909.11304) likewise derive wide-network power
counting from Gaussian parameter integrals; this identifies ensemble diagrams,
not a conditional input-integration algorithm.

## Why the Onsager term is exactly absent

At a feed-forward layer,

\[
z_{\ell i}=\sum_j W_{\ell,ij}h_{\ell-1,j}+b_{\ell i}.
\]

Remove the edge/summand from presynaptic neuron `j`. Its source activation
`h_{ell-1,j}` cannot change in response to `z_{ell i}`, because it is upstream:

\[
\frac{\partial h_{\ell-1,j}}{\partial z_{\ell i}}=0.
\]

Hence the same-edge reaction coefficient that an Onsager correction cancels is
zero. Correlations among the `h_{ell-1,j}` caused by their shared input are real,
but they are ordinary cross-covariances/cumulants; the covariance contribution
is already the sandwich `W_ell C_{ell-1} W_ell^T`. Adding a TAP reaction term
would double-count correlations or silently replace the DAG by a recurrent
model.

This is exactly where the cited TAP/AMP analogies stop. [Shamir and Sompolinsky
(2000)](https://doi.org/10.1103/PhysRevE.61.1839) treat recurrent neural
networks. [Fletcher and Rangan
(2017)](https://arxiv.org/abs/1706.06549) analyze iterative inverse inference;
algorithmic feedback/matrix reuse is essential to its Onsager terms. Neither
mechanism exists in one forward use of each `W_ell`.

### The global resolvent does not rescue the mechanism

Let `q=(q_1,...,q_L)` be any layer state and let `J` be the Jacobian of its
feed-forward recurrence. `J` is strictly block lower triangular, so

\[
J^L=0,\qquad (I-J)^{-1}=I+J+\cdots+J^{L-1}.
\]

Thus a global “Dyson resolvent” is only the finite depth-ordered propagation of
an **already specified** source. It cannot manufacture the omitted four-point
source. A geometric series that repeatedly inserts one same-layer reaction
instead enumerates paths not present in the feed-forward graph. This argument
does not ban diagram resummation in general; it kills the proposed
no-weight-reuse/TAP rationale.

## Smallest state that actually closes the tested approximation

Write the centered fixed-instance cumulants as

\[
m_i=E[h_i],\quad C_{ij}=\operatorname{cum}(h_i,h_j),\quad
T_{ijk}=\operatorname{cum}(h_i,h_j,h_k),\quad
U_{ijkl}=\operatorname{cum}(h_i,h_j,h_k,h_l).
\]

The dense linear step is exact:

\[
C^z=W C^h W^T,
\]

\[
T^z_{ijk}=\sum_{abc}W_{ia}W_{jb}W_{kc}T^h_{abc},
\]

\[
U^z_{ijkl}=\sum_{abcd}W_{ia}W_{jb}W_{kc}W_{ld}U^h_{abcd}.
\]

The state/cost implications for generic dense weights are:

| retained information | state | dense linear transport |
|---|---:|---:|
| `m,C` | `O(n^2)` | `O(n^3)` |
| full `T` | `O(n^3)` | `O(n^4)` by sequential mode products |
| full `U` / four-point vertex | `O(n^4)` | `O(n^5)` by sequential mode products |

Special factorized `k3` implementations can contract only the projections
needed for the mean in about `O(L n^3)`. That is a finite `k3` cumulant method,
not a new Dyson closure. Its factor count is part of the state and need not stay
bounded under generic ReLU/linear propagation. A fourth-order version needs an
independently justified separable or low-rank four-point vertex; the ensemble
delta structure in the cited Feynman papers is not such a factorization for a
fixed network.

For a leading finite-width **ensemble** expansion, Yaida's `(K,S,V)`—kernel,
self-energy, connected four-point vertex—is the smallest cited closed state.
For the **fixed instance**, loss of neuron exchangeability expands this to dense
coordinate tensors; with nonzero realized means/skew, the analogous truncated
state is at least `(m,C,T,U)`. Exact propagation of a ReLU law is an infinite
hierarchy, so `(m,C,T,U)` is only the smallest state for a fourth-order
perturbative closure, not an exact finite state.

## Algebraic closure falsifier

Mean/covariance/skew does not identify even the next ReLU mean. Consider two
centered two-dimensional laws:

- A: `X,Y` are independent standard Gaussians.
- B: `X` is standard Gaussian and `Y=S X`, with an independent Rademacher
  `S in {-1,+1}`.

Both have covariance `I`; every marginal is standard Gaussian; and **all full
third cumulants are zero**. But

\[
\operatorname{cum}_A(X,X,Y,Y)=0,
\qquad
\operatorname{cum}_B(X,X,Y,Y)=2.
\]

For the same next-layer row `w=(1,1)`,

\[
E_A[\rho(X+Y)]=\frac{1}{\sqrt{\pi}},\qquad
E_B[\rho(X+Y)]=\frac{1}{\sqrt{2\pi}}.
\]

Therefore no recurrence using only `(m,C,T)`—even full, not merely diagonal
skew—can uniquely determine the next ReLU mean on the class of non-Gaussian
joint laws. A scalar susceptibility or self-energy derived from those same
moments cannot restore the missing information. Any formula `Pi[C,T]` is an
extra distributional ansatz, not a consequence of cavity/TAP.

The example is an identifiability test, not a claim that either law is exactly a
benchmark hidden layer. To make a smaller state valid, one must prove that all
reachable fixed-weight ReLU laws lie in a narrower family on which the missing
four-point contraction is determined. No cited diagrammatic result proves that.

## Mapping to the second-moment oracle cap

The existing audit records that even an exact terminal `(mu,sigma)` Gaussian
closure caps the gain at `8.76e-7`. That is not a universal lower bound, but it
is a direct falsifier for any “better covariance solver” whose terminal ReLU
formula still uses only two moments: solving a Dyson equation for `C` more
accurately cannot beat an oracle that already supplied the exact terminal
`(mu,sigma)` to the same two-moment closure.

Skew is not enough to repair the logical gap. The counterexample above has the
same complete third-order state and different ReLU expectations. The diagram
literature independently points to the same missing object: a connected
four-point vertex feeds the two-point self-energy at leading non-Gaussian order.

The ARC depth law `MSE ~ c_K(L/n)^K` is only a conjectural scaling outside its
proved fixed-depth polynomial regime; see [Wu et al.
(2026)](https://arxiv.org/abs/2605.05179). This no-go therefore does **not** rely
on treating `(L/n)^K` as a theorem. It says the proposed resummation lacks a
closed fixed-instance state before any claimed depth acceleration can be
credited.

## Registered premise and hard falsifiers

### Premise required to revive the branch

There must exist a weight-computable fixed-instance four-point self-energy
representation

\[
U_\ell\longmapsto \{A_{\ell r}\}_{r=1}^{R},\qquad R=O(1)\text{ or }O(n),
\]

that is (i) closed under the dense linear/ReLU layer map to the claimed order,
(ii) retains every contraction affecting the output mean at that order, (iii)
does not use target/scorer information, and (iv) costs at most `O(L n^3)`.
Only then would a self-consistent vertex/Dyson update be an implementable new
method rather than `k2/k3` sequence extrapolation.

### Falsifiers met now

1. **Onsager test:** the leave-one-edge reaction derivative is zero on the DAG.
2. **Closure test:** the explicit pair of laws above shares `(m,C,T)` but gives
   different next ReLU means.
3. **Vertex test:** primary finite-width recursions require a connected
   four-point vertex to update the self-energy.
4. **Cost test:** a generic fixed-instance vertex is `O(n^4)` state and its dense
   transport is `O(n^5)`, outside the envelope.
5. **Conditioning test:** replacing that vertex by ensemble scalar/delta
   coefficients changes `E_X[.|W]` into an annealed random-weight approximation.
6. **Non-extrapolation test:** fitting/accelerating the `k2,k3` sequence does not
   specify the omitted diagram family and is not accepted as a Dyson derivation.

## Bottom line

There is no honest implementable `O(L n^3)` recurrence to report from this
branch. The strongest viable descendant is conditional: first discover and
prove a stable low-rank/separable representation of the **fixed-instance
four-point vertex**. Without that new structural theorem, cavity/TAP contributes
no reaction term, while Dyson iteration merely resums an unidentified closure.

The primary-source search ledger is
[`sources/research_cavity_dyson_primary.md`](../../../sources/research_cavity_dyson_primary.md).
