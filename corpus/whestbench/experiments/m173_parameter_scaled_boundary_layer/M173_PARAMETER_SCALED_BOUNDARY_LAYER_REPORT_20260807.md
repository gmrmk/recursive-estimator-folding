# M173: parameter-scaled boundary layer for the M171 near-parallel rank-two failure

## Decision

**SCREENED, CERTIFIED REPAIR OF M171'S HOSTILE TRANSVERSE RANK-TWO `Phi(u/eta)` CHANNEL ONLY.**  M173 changes exactly M171's failed fixed `GL10` panel on that channel.  It preserves M159's scale-carried ABI, M165's connected-first rank-face subtraction, and M168's transverse planar anchor and one-sided cone tangent.  It does not install an endpoint provider or change a champion.

The repair is deliberately narrow.  It proves a value enclosure below `2e-8` and a tangent enclosure below the current locked `2e-7` source tolerance, uniformly for every real predeclared `0 < eta <= 1/10`, provided that the connected-first amplitude and tangent envelopes stated below have been established symbolically.  It does **not** establish those envelopes for every M168 raw/indicator component, an SPD continuation, a coincident pair of kinks, or a zero-marginal face.  Those are separate unresolved links, not permissions to extrapolate this result.

## 1. Frozen parent boundary and the one changed mechanism

M171 correctly rejected the direct ten-node Gauss--Legendre derivative certificate.  On its transverse, positive-marginal hostile factor

\[
 L_\eta=((1,0),(1,\eta),(0,1)),\qquad 0<\eta<1,
\]

conditioning on `U=u` produces `Phi(u/eta)`.  At `u=eta`, its twentieth `u` derivative contains `eta^-20`; M171's exact GL10 remainder floor was already about `.00209` at `eta=1/10`.  That was an obstruction to the **unscaled physical-coordinate panel**, not a proof that the conditional primitive itself is unintegrable.

M173 changes no anchor or connected algebra.  It replaces only the singular channel's coordinate and its remainder proof.  The pair is selected deterministically in the existing rank-two factor chart, then its ordered-pair chart is frozen as

\[
 X_i=U,\qquad X_j=U+\eta V
\]

or the fixed sign-reflected equivalent.  The `eta` in this report is this chart coefficient; it is not inferred from an unnormalised factor determinant.  The ordered-pair chart and its amplitude bounds are mandatory certificate inputs.

## 2. Exact matched-asymptotic translation

Let `F` denote a connected-first normal-polynomial amplitude after M168's exact inner normal-interval reduction, and write `u_star` for the ordered pair's kink intersection.  Define

\[
 g(t)=\Phi(t)-{\bf1}\{t>0\},\qquad u=u_\star+\eta t.
\]

Splitting `Phi` into its step and its localized difference is an exact identity:

\[
 \int_{-\infty}^{\infty}F(u)\Phi\!\left({u-u_\star\over\eta}\right)du
 =\int_{u_\star}^{\infty}F(u)du
 +\eta\int_{-\infty}^{\infty}F(u_\star+\eta t)g(t)dt. \tag{1}
\]

The first term is a normal interval integral and remains in M168's analytic recurrence.  Equation (1), rather than an empirical node probe, removes the `eta^-20` differentiation scale.  The deterministic partition is

\[
 (-\infty,u_\star-8\eta],\quad [u_\star-8\eta,u_\star],\quad
 [u_\star,u_\star+8\eta],\quad [u_\star+8\eta,\infty). \tag{2}
\]

There is no adaptive subdivision and no retry.  On the central two intervals M173 uses the degree-nine Taylor expansion of `F(u_star+eta*t)`.  Its coefficient moments are the exact univariate quantities

\[
 m_q(8)=\int_{-8}^{8}t^qg(t)dt,
 \qquad
 R_9=\eta\sum_{q=0}^{9}{\eta^qF^{(q)}(u_\star)\over q!}m_q(8). \tag{3}
\]

Even `m_q` vanish by parity; odd moments have closed normal-tail recurrences.  Thus the layer spends **zero quadrature nodes**.  It is an analytic matched correction, not a disguised higher-order panel.

## 3. Predeclared range, envelope caps, and uniform value proof

The complete parameter range is every real `0 < eta <= 1/10`.  Before applying (3), a symbolic connected-first derivation must certify

\[
 \sup|F|\le 10^6,\qquad \sup|F'|\le10^6,\qquad
 \sup|F^{(10)}|\le3\cdot10^6. \tag{4}
\]

These are certificate gates, not data-tuned thresholds.  They are intentionally loose but finite; failure to derive them means refusal.

For `Q=1-Phi`,

\[
 \int |t|^{10}|g(t)|dt={2\over11}\mathbb E(Z_+)^{11}
 \le {10396\over11}. \tag{5}
\]

The last inequality follows from `z^11<=1+z^12` on the positive half-line and `E Z^12=10395`.  Taylor's theorem gives the layer remainder

\[
 E_{\rm in}^{(v)}\le
 {\eta^{11}(3\cdot10^6)\over10!}{10396\over11}. \tag{6}
\]

For the outer tails, `int_8^infinity Q(t)dt<=phi(8)`.  The strictly rational bound

\[
 \phi(8)<{1\over150\,000\,000\,000\,000} \tag{7}
\]

uses `e>1957/720` (the first seven positive terms of its series) and `sqrt(2*pi)>12/5` (from `pi>3`).  Hence

\[
 E_{\rm tail}^{(v)}\le2\eta(10^6)\phi(8). \tag{8}
\]

Both right sides increase on the entire declared eta interval, so `eta=1/10` is a uniform worst endpoint.  The frozen exact result is

\[
 E^{(v)}\le {76063\over8316000000000}
 =9.14658489658\ldots\cdot10^{-9}<2\cdot10^{-8}. \tag{9}
\]

This is an enclosure of the transformed singular channel, not a sampled comparison.

## 4. Tangent translation and enclosure

The coordinate must also be differentiated; freezing either `eta` or the moving pair intersection `u_star` would be incorrect.  With dot denoting the specified source tangent, equation (1)'s layer term has the exact derivative

\[
 \dot R=\int K(u_\star+\eta t)g(t)dt,
 \quad K(u)=\dot\eta\,[F(u)+(u-u_\star)F'(u)]
 +\eta[\dot F(u)+\dot u_\star F'(u)]. \tag{10}
\]

M173 predeclares `|eta_dot|<=1`, `|u_star_dot|<=1`, `sup|Fdot|<=10^6`, and `sup|K^(10)|<=3*10^6`; all must follow from the same connected-first symbolic kernel.  Taylor through degree nine gives

\[
 E_{\rm in}^{(t)}\le {\eta^{10}(3\cdot10^6)\over10!}{10396\over11}. \tag{11}
\]

Using `int_8^infinity tQ(t)dt<=Q(8)<=phi(8)/8`, the fixed tail bound is

\[
 E_{\rm tail}^{(t)}\le2\left[10^6\phi(8)
 +{\eta10^6\phi(8)\over8}+\eta10^6\phi(8)+\eta10^6\phi(8)\right]. \tag{12}
\]

At the same uniform endpoint this gives

\[
 E^{(t)}\le {12253\over129937500000}
 =9.42991822992\ldots\cdot10^{-8}<2\cdot10^{-7}. \tag{13}
\]

The tangent tolerance is the current locked M147 source certificate transported by M159's fixed dyadic carrier; M173 does not claim a new global tangent contract.

## 5. Deterministic cost allocation

M171's transparent bookkeeping model was `571,904` operations: seven wedge cells, 31 components, ten nodes, 256 arithmetic-equivalent operations per component-node, plus unchanged setup and exact boundary inventory.  M173 leaves 30 regular components at ten nodes and replaces the one hostile `Phi(u/eta)` channel in each of seven cells by its fixed ten-jet/tail calculation:

| allocation | charged operations |
|---|---:|
| unchanged setup and exact coarea boundaries | `16,384` |
| 7 cells x 30 regular components x 10 nodes x 256 | `537,600` |
| 7 deterministic analytic layer channels x 1,024 | `7,168` |
| total | `561,152` |

The maximum remains **ten nodes per channel**; the singular layer itself uses zero quadrature nodes.  `561,152 <= 606,720` is a static bookkeeping prediction, not a native operation trace.  The missing native trace and the absence of symbolic envelopes for every full connected cache entry mean no provider or billed-operation credit is claimed.

## 6. Kill gates and lawful scope

M173 fails closed if any of the following occurs: the ordered pair lacks a positive `eta` in `(0,1/10]`; a connected-first amplitude or tangent envelope cannot be proven; either bound above exceeds its locked tolerance; a native bill is asserted without a trace; or an implementation introduces a ridge, clipping, opaque CDF, adaptive retry, or response-derived selection.

This repair is limited to the **transverse, positive-marginal, near-parallel rank-two `Phi(u/eta)` channel**.  It does not lawfully extend to:

- SPD states: they need their own connected interval kernel and certified operation trace.
- Nontransverse rank-two faces: `eta=0` invalidates the transverse coordinate and requires a coincident-kink analysis.
- Zero-marginal PSD faces: M159's deterministic reduction and explicit one-sided conic tangent remain mandatory.
- Outward PSD tangents: they remain infeasible.

## Verification and disposition

Seven response-free unit tests check the exact partition, rational Gaussian-tail proof, endpoint-dominating uniform enclosure, positive-marginal transverse hostile family, fail-closed dispatch, and the under-cap bookkeeping calculation.  The static audit rechecks the two frozen exact fractions and the operation prediction.  No network, response, truth, scorer, leaderboard, submission, champion, opaque multivariate CDF, ridge, clipping, or adaptive retry was read or changed.

**Disposition:** `SCREENED_HOSTILE_TRANSVERSE_RANK2_LAYER_CERTIFICATE_ONLY; PRESERVE_M154_M165_M168_CONNECTED_FIRST_ANCHORS; NO_SPD_NONTRANSVERSE_ZERO_FACE_OR_NATIVE_PROVIDER_CREDIT`.
