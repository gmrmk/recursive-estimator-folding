# M120 hostile theory audit: normal-ordered Price covariance adjoint

**Disposition: REPAIR, not IMPLEMENT.** M120 genuinely changes the algebra that
killed M119: it keeps the independent-coordinate diagonal exactly and changes
the all-output factor count from multiplicative to additive when the connected
Price residual `E` is omitted. The exact `R=I` M119 counterexample is therefore
not a counterexample to M120's base recurrence.

That is a representation result, not a closed estimator. As supplied, the
probe implements only a raw/Price covariance block. It omits the diagonal and
mean/covariance cross blocks of the actual central-covariance Gaussian closure,
has no weights-only feedback source, and gives no ownership partition with the
terminal Born diagrams. Once those required blocks are charged, the full
all-output adjoint has a **99.721B matmul lower bound** (`105.910B` including
the existing Gaussian background), above M119's 80B screen though below a
standalone 272B resource cap. Exact propagation of even one nonterminal `E`
insertion reintroduces multiplicative rank and is not resource-feasible.

The generated-only probes are real, correctly scoped evidence for the Price
block; they are not evidence for a complete feedback correction or an
estimator. No contest data, target, scorer, reference row, champion mutation,
or outcome run is used here.

## 1. Independent probe check and hashes

I independently reran the two supplied scripts under the local `whest-v014`
environment, with their generated He weights only:

```text
probe_price_split.py
  SHA-256 25A16322BAC8AB736E17E6A8D0B1B84ACDB790FD62CE343CFEA920E0857F0A4E

probe_repeated_pullback.py
  SHA-256 BE0E8040BF5949F7870221AD59467F3585B98A1EE3646F6F88A9AA2F59D75B5B
```

| command | independently reproduced generated-only result |
|---|---|
| `probe_price_split.py --width 256 --depth 32 --seeds 120001 120002 --aggregate-only` | mean `||E||_F/||K||_F = 0.01957003156`; q90 `.02549800195`; max `.03960089728` |
| same split probe | maximum over its one-step terminal-weight proxy: mean `.02988351662`, q90 `.03857627963`, maximum `.04123552470` |
| `probe_repeated_pullback.py --width 256 --depth 32 --seed 120101 --outputs 0 --ranks 0 --aggregate-only` | `E=0` Price-block reverse error `.03143572711`, cosine `.99959273440` |

The stated numbers are therefore reproducible. The evidence is narrower than
it first appears:

- The split probe uses two seeds and treats 62 layer records as an aggregate;
  layers within a network are not independent replications.
- Its one-step output probe uses the final weight column at *every* hidden
  layer. It is not the actual reverse-propagated output adjoint at those
  layers.
- The repeated-pullback test does reverse the `K circ A` block correctly for
  one generated output, but its own docstring excludes the other
  `(\mu,C)` Jacobian blocks. It is a component falsifier, not a correction
  oracle.
- `phi2_gauss10` is a fixed ten-point numerical CDF rule. The algebraic split
  is exact for the computed `K`; small `E` values still need a direct
  Plackett-integral or high-precision error certificate before being treated
  as accurate relative residuals. Its `rho` clipping and variance floor must
  be included in any numerical audit.

The split probe's signed `E` tails are also adverse to a generic low-rank
residual claim: its mean best rank-16/32/64 relative Frobenius tails are
`.3872/.2826/.1474`, with maxima `.8085/.6954/.5775`. A small total
`||E||_F/||K||_F` does not make `E` low rank.

## 2. Exact split and what it repairs

For a Gaussian preactivation `Z` with arbitrary means, define

\[
 p_i=\Pr(Z_i>0)=\Phi(\mu_i/\sigma_i),\qquad
 K_{ij}=\Pr(Z_i>0,Z_j>0).
\]

Then exactly

\[
 K=pp^T+D+E,\qquad
 D=\operatorname{diag}(p-p^2),\qquad
 E_{ii}=0. \tag{1}
\]

Off diagonal, `E_ij` is the connected gate covariance
`Cov(1{Z_i>0},1{Z_j>0})`. The full centred gate covariance is `D+E`;
`E` alone has zero trace and is generically indefinite. It must not be
passed to a PSD pivoted-Cholesky routine.

At M119's adversary `R=I`, `p=1/2` and

\[
 K=\tfrac14 {\bf1}{\bf1}^T+\tfrac14I,\qquad E=0. \tag{2}
\]

Thus M120 carries both parts that M119's rank-`r` Nyström truncation lost. It
really evades that exact 48.4% Schur-multiplier failure.

Let the all-output covariance-adjoint family have the shared symmetric CP
form

\[
 A_{ij,o}=\sum_{s=1}^{R}U_{is}U_{js}G_{os},
 \quad U\in{\mathbb R}^{n\times R},\quad G\in{\mathbb R}^{O\times R}. \tag{3}
\]

For the `pp^T` piece,

\[
 (pp^T)\circ A_o
 =(\operatorname{diag}(p)U)\operatorname{diag}(G_{o:})
   (\operatorname{diag}(p)U)^T, \tag{4}
\]

so the atom count is unchanged. For a raw Price diagonal contribution
`D circ A_o`, an affine covariance pullback with code convention
`z=h W+b`, `W in R^(n_prev x n)` is

\[
 W(D\circ A_o)W^T
 =\sum_{i=1}^{n} W_{:i}W_{:i}^T\,
    (p_i-p_i^2)A_{ii,o}. \tag{5}
\]

The `n` columns of `W` are shared atoms; only the coefficients vary by output.
This is exact and permutation covariant. The rank recurrence is therefore

\[
 R_{\ell-1}=R_\ell+n_\ell \quad(E=0), \tag{6}
\]

rather than M119's `R -> r_K R`. With 31 hidden ReLUs and `O=n=256`,
the terminal family begins with `R=O`; the largest source-facing factor bank
has at most `(O+31n)=8192` atoms. An individual output matrix can still have
rank `n` after one reset. The compression is across outputs through common
atoms, not a false claim of per-output low rank or an M08-style shared output
basis.

## 3. The complete central-covariance adjoint is not the probe

Equation (1) is the Price derivative of a raw bivariate ReLU moment and is
the exact off-diagonal covariance derivative. It is **not** by itself the
complete adjoint of the central-covariance Gaussian closure.

Write the ReLU moment map as

\[
 (m,V)=\mathcal R(\mu,C),\qquad
 m_i=\sigma_i\phi(\alpha_i)+\mu_i p_i,\quad
 \alpha_i=\mu_i/\sigma_i,\quad
 r_i=\partial m_i/\partial C_{ii}={\phi(\alpha_i)\over2\sigma_i}. \tag{7}
\]

For a mean adjoint `b^h_o` and covariance adjoint `A^h_o`, define the two
dense pair-derivative contractions, under a fixed symmetric-matrix pairing,

\[
 c^\mu_{i,o}=\mathcal L^\mu_i[A^h_o],\qquad
 c^v_{i,o}=\mathcal L^v_i[A^h_o], \tag{8}
\]

where `L^mu` differentiates `V` with respect to `mu_i` and `L^v` differentiates
`V` with respect to `C_ii`. Their diagonal entries are already nontrivial:

\[
 \partial_{\mu_i}V_{ii}=2m_i(1-p_i),\qquad
 \partial_{C_{ii}}V_{ii}=p_i-2m_i r_i. \tag{9}
\]

At zero mean the second value is
`1/2-1/(2 pi)=0.3408450569`, not `K_ii=p_i=1/2`. The one-dimensional
variance test therefore falsifies any assertion that the supplied `K circ A`
probe is the full covariance pullback, even when `E=0`.

The complete local reverse block has the form

\[
 \begin{aligned}
 b^z_{i,o} &=p_i b^h_{i,o}+c^\mu_{i,o},\\
 \delta^z_{i,o} &=r_i b^h_{i,o}+c^v_{i,o},\\
 A^z_{ij,o} &=K_{ij}A^h_{ij,o}\quad (i\ne j),\qquad
 A^z_{ii,o}=\delta^z_{i,o},\\
 b^{h,\mathrm{prev}}_o&=Wb^z_o,\qquad
 A^{h,\mathrm{prev}}_o=WA^z_oW^T. \tag{10}
 \end{aligned}
\]

Here `delta^z` is the adjoint of the input covariance diagonal. The exact
definitions of `L^mu,L^v` include the symmetric-slot factors; they are dense
functions of the bivariate Gaussian derivatives in the existing moment map.

The CP recurrence survives this repair, but the reset coefficient is not the
simple prompt value `(p-p^2) A_ii`. Carry the rank-preserving `pp` part first,
then append the `n` columns of `W` with

\[
 G^{\mathrm{reset}}_{o i}
 =\delta^z_{i,o}-p_i^2\sum_s U_{is}^2G_{os}. \tag{11}
\]

This can be signed. In the raw-second-moment formulation, (11) reduces to
the prompt's diagonal reset; in the central-covariance formulation it does
not. A variable change to raw moments does not remove the issue: converting
between raw second moments and covariance couples the mean and covariance
adjoints again.

The contractions in (8) remain CP-evaluable without an `n^3` output stack.
For either derivative kernel `L`,

\[
 [\mathcal L(A)]_{i,o}
 =\sum_s U_{is}(LU_{:s})_iG_{os}. \tag{12}
\]

Thus no additional atoms are needed: `c^mu` and `c^v` are ordinary `n x O`
mean/diagonal arrays, and their diagonal covariance contribution merges into
the same `n` reset atoms. This is M120's substantive positive result.

## 4. Target cost and memory

Use `n=O=256`, 31 hidden ReLU maps, and the FlopScope dense-matmul count

\[
 {\cal M}(a,b,c)=2abc-ac
\]

for an `a x b` by `b x c` product. Before the reverse step at hidden distance
`t` from the terminal, the base recurrence has `R_t=t n`, for `t=1,...,31`.
The mandatory all-output matmuls are:

| operation | calls | target-shape total |
|---|---:|---:|
| `diag(A) = G @ (U*U).T` | 31, `(O,R,n)` | 16.641B |
| `L_mu @ U`, then `(U*(L_mu@U)) @ G.T` | 62 | 33.251B |
| `L_v @ U`, then `(U*(L_v@U)) @ G.T` | 62 | 33.251B |
| affine `U_pp = W @ (p*U)` | 30, `(n,n,R)` | 15.572B |
| affine mean-adjoint `B = W @ Bz` | 30, `(n,n,O)` | 1.005B |
| **complete reverse matmul lower bound** | **215** | **99.721B** |

The Price-only component measured by the supplied repeated-pullback probe
omits the two `L` rows. Its corresponding lower bound is only
`16.641 + 15.572 + 1.005 = 33.218B`; this is why a partial algebra can look
cheap. Adding the audited Gaussian background makes the complete pre-source
account at least **105.910B**, before pointwise scaling, bivariate-CDF/
derivative construction, buffer copies, CP concatenation, source formation,
or a native FlopScope trace.

Therefore M120 does not fit the prior 80B analytic screen. It is not
statically over the standalone 272B ceiling, but its source is absent and no
integration budget follows from this component account. The terminal Born
contraction's 3.111B is not a valid feedback-source charge: adding it without
a diagram partition would double count `LLQ`, `LLLC`, and `LLQQ`.

At maximal `R=7936`, streaming float64 state is feasible but material:

| live item | approximate memory |
|---|---:|
| `U` and a next-`U` buffer | 31 MiB |
| `G` and a next-`G` buffer | 31 MiB |
| one `L U`/Hadamard contraction workspace | 16 MiB |
| two saved Gaussian covariance stacks | 31 MiB |
| `K,L_mu,L_v`, mean arrays, `B`, resets, small workspaces | under 4 MiB |
| **conservative streamed working set** | **about 113 MiB** |

Caching both derivative kernels for every layer instead of regenerating them
adds about 31 MiB. These numbers are below 512 MiB but must be checked in the
actual call graph; they do not include an exact `E` insertion or a source
state.

## 5. Why one `E` insertion is not a free repair

`E` is symmetric, zero diagonal, generally full rank, and indefinite. If
`E=sum_a lambda_a v_a v_a^T`, then applying it to (3) creates atoms

\[
 U_{:s}\circ v_a,\qquad s=1,\ldots,R,\quad a=1,\ldots,\operatorname{rank}E,
 \tag{13}
\]

with signed output coefficients `lambda_a G_os`. Thus an exact insertion maps
`R` to `R rank(E)`, not to `R+n`. The generated spectra do not support a
constant exact rank for `E`.

At the final hidden layer `R=n`, an exact full-rank insertion already creates
`n^2=65,536` atoms: `U` and `G` each occupy 128 MiB before the remaining
pullbacks. At a middle layer with `R=16n`, it creates 1,048,576 atoms and
about 2 GiB each for `U` and `G`. A dense all-output fallback has the same
problem after its next affine pullback.

A single insertion can be exact only if it is immediately contracted with a
declared local source and never propagated further; that is a terminal/local
diagnostic, not restoration of downstream mean/covariance feedback. Any
rank-truncated signed `E` insertion is a new approximation with the adverse
tails above and requires its own rank, symmetry, cost, and signed-contraction
falsifier. “At most one” is not a sufficient specification.

## 6. Symmetry, conditioning, and source ownership

The base CP state is permutation covariant: a hidden permutation permutes
rows of `U`, columns of the relevant weight matrix, and reset coefficient
columns together. It avoids M119's pivot/eigenspace tie selection because all
`n` reset atoms are retained.

It has a scaling gauge that must be fixed. A column rescaling
`U_:s -> c_s U_:s`, `G_:s -> G_:s/c_s^2` leaves (3) unchanged. Positive ReLU
gauges induce precisely such rescalings through `W`. Normalize atoms in
variance-standardized coordinates and transform `G` inversely; no hard
variance floor is gauge covariant. A zero-variance coordinate must be
quotiented exactly or fail closed.

Numerically, `p` near zero or one makes both `pU` and
`p(1-p)` small, while (11) can subtract nearly equal diagonal terms. Computing
`E=K-pp^T-D` by subtraction loses relative precision in the same regime.
Use the direct Plackett integral for the connected orthant covariance, retain
signed coefficients, and certify every variance/correlation clamp. Near
`|rho|=1`, bivariate derivatives are ill conditioned even though `K` is
bounded.

Finally, M120 is an adjoint weighting operator, not a non-Gaussian source.
If a future child supplies `delta mu_l,delta C_l`, it may use

\[
 \Delta J_o=\sum_l\{(b_l)_o^T\delta\mu_l+
                         \langle A_l{}_o,\delta C_l\rangle\}. \tag{14}
\]

It must first give an exact one-layer diagram-incidence table. The terminal
Born `LLQ/LLLC/LLQQ` sources already own their terminal projections; a
forward-plus-M120 union must subtract one owner before adding the other.
Compression, `E=0`, or a favorable Price-block cosine creates no new source
and does not license a forward/adjoint sum.

## 7. Strict target-free reopening protocol

No correction oracle may run until each preceding stage passes with frozen
ranks, source ownership, seeds, and call shapes.

1. **Algebraic closure.** Test the univariate value in (9), independent
   `R=I`, and random small central-covariance finite differences. The
   corrected CP recurrence (10)--(12), including signed resets, must match
   dense all-output adjoints to `1e-10` for `E=0` cases. The supplied
   `(p-p^2)A_ii` reset alone must be recorded as a deliberate raw-moment-only
   failure, not silently used for covariance.
2. **Generated small all-output falsifier.** Freeze widths `{8,12,16}`, depths
   `{2,3,4}`, three Philox networks per cell, and all outputs. Compare exact
   dense complete `(mu,C)` adjoints against the sealed `E=0` CP recurrence.
   Require global standardized-adjoint error at most `.05`, every-cell
   worst-output error at most `.10`, and the same limits for predeclared
   signed `(delta mu,delta C)` directional contractions. Test simultaneous
   permutations, positive gauges, and degenerate/near-zero variance cases to
   `1e-10`.
3. **Target-shape weights-only gate.** On four fresh generated width-256,
   depth-32 networks, report actual reverse-propagated all-output
   `||E circ A||/||K circ A||` at every layer--not the final-weight proxy--and
   full signed `E` tails. Require mean at most `.05` and maximum at most `.10`;
   report nonnormal suffix gain bounds. The native trace must contain the 215
   listed matmuls, remain below a predeclared component ceiling, and measure
   peak memory. A claimed <=80B complete closure fails this arithmetic before
   execution.
4. **Source and correction gate.** Only if 1--3 pass, seal one weights-only
   feedback source, its `LLQ/LLLC/LLQQ` ownership subtraction, and a
   generated-only correction bank. Compare sealed CP feedback with its dense
   same-source adjoint first; only then use independent split-stream Gaussian
   reference paths. Require `.80` signed retention and `.80` material-sign
   agreement in every stratum. An unresolved confidence interval, a selected
   `E` location/rank, or any post-reference coefficient is a kill.

## 8. Decision

**IMPLEMENT: no.** The current probes do not implement the complete
central-covariance adjoint, a source, or a costed estimator.

**REPAIR: yes, narrowly.** The `pp^T + D` shared-CP recurrence is a genuine
mechanism change. It exactly repairs M119's independent-coordinate
Schur-multiplier obstruction, preserves all-output/gauge/permutation structure,
and its corrected full-Jacobian version has additive--not multiplicative--rank
growth. It merits the frozen generated-only closure falsifier above.

**KILL: three invalid shortcuts.**

1. Kill any claim that `K circ A` with diagonal `p A_ii` is the full
   central-covariance pullback; the one-dimensional derivative is already
   different.
2. Kill any <=80B claim for the complete all-output `(mu,C)` recurrence; the
   mandatory matmul lower bound is 99.721B before background and scalar work.
3. Kill an exact-one-E-insertion claim unless it specifies a no-propagation
   local contraction or pays the rank multiplication in (13).

The cheapest next step is the target-free univariate-plus-small-width dense
Jacobian test in step 1. It either validates the corrected signed-reset CP
closure algebra or kills the only part of M120 that is currently new; it does
not require a correction oracle or any contest-facing computation.

## Local evidence used

- `m120_price_normal_ordered_adjoint/probe_price_split.py` and
  `probe_repeated_pullback.py` -- independently rerun generated-only probes
  and source hashes above.
- `adjoint_cumulant/REPORT.md` -- terminal Born ownership and the original
  full-adjoint bottleneck.
- `cavity_dyson/REPORT.md` -- missing fixed-instance higher-order source.
- `k4_tensor_sketch/REPORT.md` -- local spectral quality does not establish
  downstream signed-correction fidelity.
- `terra_m08_shared_2pi/REPORT.md` and `terra_composability/REPORT.md` --
  output-basis and forward/adjoint ownership constraints.
