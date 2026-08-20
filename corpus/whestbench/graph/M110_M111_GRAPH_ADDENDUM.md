# M110--M111 graph addendum

Date: 2026-08-07

## Measured closure of the single-axis nodal branch

M110 repaired both static defects in M109: the correct spherical probability

`I_(1/256)(1/2,255/2) = 0.681741518241344407...`

and the positive-ReLU-gauge repair

`||W1[:,j]||^2 * squared_downstream_path_energy[j]`.

The manifest-frozen, generated-only one-shot passed all exactness, symmetry,
source-hash, provenance, rank, tail, cosine, QR, and resource guards.  Its held
variance ratios were

`[1.064569787110, 1.153156708633, 1.058324546427, 1.025561470383]`.

The geometric ratio was `1.074387032715`, the conditionally pooled ratio was
`1.067688165548`, and the frozen cost-adjusted pooled proxy was
`2.156730094406`.  All four apparent training gains reversed on independent
held frames.  The graph therefore records a mechanism failure, not a theorem,
symmetry, or implementation failure: **independent-axis nodal amplitude does
not carry a stable output phase**.

The independently computed spectrum rules out a single magic frequency.  The
fixed gate-tube scalar variance is distributed broadly over even harmonics,
with shares `l2=.543918`, `l4=.180546`, `l6=.052375`, `l8=.009142`, and a
nonzero tail beyond degree 200.

## One-edge mutation

M111 changes only the failed phase edge.  For normalized W1 gate axes, define

`v_i(U) = 1{a_i.U>0} - 1/2`

and use the exact arcsine covariance

`Sigma_ik = E[v_i v_k] = asin(a_i.a_k)/(2*pi)`.

Let

`T = diag(||W1 columns||) @ W2 @ ... @ WL`.

The proposed per-output normal-ordered energy is

`h_j(U) = (v(U) @ T[:,j])^2 / (T[:,j]^T Sigma T[:,j]) - 1`.

The diagonal terms cancel because `v_i^2=Sigma_ii=1/4`, so every surviving
term is a centered `i != k` gate-pair interference.  The signed transport `T`
labels that interference by output phase.  This is not a threshold, degree,
ridge, or mixture retune of M110.

In exact arithmetic the candidate is mean-zero, antipodally even, input
rotation covariant, hidden-permutation invariant, and invariant under every
positive hidden ReLU gauge.  Those statements and the finite-precision source
are still under independent preexecution audit.  No M111 network has run.

## Graph conclusion

The updated graph has 169 nodes and 372 edges.  The principal god nodes remain
the legal objective (degree 68), the latent-factor closure gate (28), the
connected finite-width four-point vertex (19), and the permutation/gauge/O(256)
quotient (12).  M110 appears as a high-betweenness bridge because it closes a
large failed branch, **not** because it is viable.

The new surprising edge is

`connected finite-width four-point vertex -> pairwise gate-phase interference`.

That edge is explicitly a hypothesis: a normal-ordered quadratic gate field
is the first bounded exact-mean operator in this branch that touches
cross-neuron structure, but only the frozen held-frame gate can establish
useful covariance.  Its current confidence is deliberately `0.65`.

Theory-only backups are retained but not pooled with M111: a Bessel-centered
Herglotz cosine structure factor, a trace-free nematic degree-six cubic, and a
fixed 1:2 harmonic coupling.  They are separate future mutations, not a menu
for post-result selection.

## Causal-link red-team

The initial graph edge from the connected four-point vertex to pairwise gate
interference is now sharply bounded.  For the antipodally even network field
`g`, define

`B_ik = E[(g-Eg)*(v_i*v_k-Sigma_ik)]`.

Then the exact relation is

`Cov(g,h_T) = (2/s) * sum_(i<k) T_i*T_k*B_ik`.

The missing state is `B`, not `Sigma`.  It contains the actual downstream
ReLU factorization.  A nonmonomial orthogonal insertion

`W2' = W2*A,   W3' = A.T*W3`

preserves the iid-He joint law and the product `W2*W3`, hence fixes `W1`, `T`,
`Sigma`, and M111 pointwise, while generally changing the ReLU function and
its mean.  Therefore M111 is provably not a sufficient statistic for the
terminal connected defect, even along an ensemble-preserving fibre.

An annealed independent-gate calculation supplies a hostile quantitative
prior: the leading even two-leg overlap is proportional to
`pi^-1 * 2^(-(L-2))`, approximately `2.96e-10` at `L=32`, before a complete
frame annihilates degree two.  Ordinary relative `O(L/n)` corrections cannot
repair that exponential suppression.  A positive frozen screen would be
evidence for a different nonperturbative connected mechanism; it is not the
default prediction.

Graphify now sees 173 nodes and 380 edges.  The new future edge is not another
frequency: it is **factorization-aware layer-local gate energy**, which would
retain internal ReLU coordinates instead of collapsing them into `W2...WL`.
That child remains an unfrozen hypothesis and may be opened only after the
M111 disposition is recorded.

## M111 measured closure

M111 was subsequently source-frozen under manifest SHA-256
`ccbdb0a2a8bef9b81d7093abd79550ec903e0a246e5a8ec5996717dac7ef9ab9`
and executed exactly once on four generated target-shape networks.  Every
theorem, symmetry, float32/float64, PSD, gauge, tail, rank, cost, provenance,
and all-network control-first barrier check passed.  The 213-event ledger
places all four completed prechecks before the first of 200 evaluator frames.

The held trace-variance ratios were

`[1.018684200440, 1.034130062564, 1.022911631042, 1.037221540475]`.

The geometric and pooled ratios were `1.028208274440` and `1.030480925825`;
after the frozen `rho=1.04` charge they became `1.069336605417` and
`1.071700162858`, with charged whole-network bootstrap q90
`1.074168525998`.  An independent judge that imports no candidate code
recomputed the same numbers and returned evidence verdict `PASS` plus
scientific disposition `KILL_M111_EXACT_IMPLEMENTATION_NO_RETRY`.

This closes the hypothesized edge

`ungated signed transport -> stable downstream output phase`.

It does not close the exact pair-field theorem.  The result instead confirms
the causal red team: the missing object is the factorization-sensitive
connected tensor `B`, and the full matrix product `T` erases precisely the
intermediate ReLU coordinates that determine it.

Evidence hashes:

- raw NPZ: `4f82e547901ecba643ee648c74656818c429ca38a9d9290fa907c8db26fd752e`;
- raw metadata: `7f1e5186d3d553ec98f168d08fc407cf0cd390a1498307c1a271a349e086de1f`;
- independent result judge: `52b9dd282c46d87c5f9891e8cfe283f9e8778e97b6a86f4de10905395e7143f2`.

## M112 one-edge repair

M112 replaces the false output-phase label rather than retuning M111.  For
each independent Haar frame it forms

`C_r = V_r^T V_r / 256 - Sigma`

and the raw Gram `K_rs=<C_r,C_s>_F`.  A held row enters only linearly as
`K_h,T alpha`; because `E[C_h|W]=0` and the held frame is independent of the
training frames, the cross-fitted correction has conditional mean zero.
Training labels are actual nonlinear network outputs, so downstream gates
enter the learned coefficient instead of being replaced by `W2...WL`.

The new edge is therefore

`actual frame output fluctuation -> empirical frame-visible projection of B`.

Hard boundaries remain.  Complete frames annihilate degree two, so `C_r`
contains only even degrees at least four; forty training frames span no more
than forty of 32,640 off-diagonal gate-pair coordinates.  Held normalization,
cosine kernels, ordinary kernel centering, and shared-rotation MUB folds would
void the exact-zero proof.  M112 is a theory-screened generated-only premise,
not a champion or a claimed recovery of `B`.
