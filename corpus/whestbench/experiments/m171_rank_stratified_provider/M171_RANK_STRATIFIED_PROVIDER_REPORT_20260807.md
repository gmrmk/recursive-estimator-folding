# M171: rank-stratified connected-first endpoint-provider certificate

Date: 2026-08-07  
Status: **KILLED IMPLEMENTATION — the proposed all-PSD, fixed-10-node provider does not obtain a uniform normalized error enclosure.  Preserve the rank-one and transverse-rank-two anchor algebra; do not grant endpoint or cost credit.**

## Firewall and scope

This mutation read only frozen local artifacts M147, M154, M159, M162, M165,
and M168.  It performs generated, response-free symbolic/rational checks.  It
does not read or call a network response, model, truth, scorer, leaderboard,
submission, champion, or target execution.  It has no adaptive retry, ridge,
correlation clipping, or opaque CDF-library call.

No primary research was needed: the mathematical inputs are the frozen local
Price/Tallis/Plackett analysis already documented in M154, M162, M165, and
M168.

## Predeclared one-mechanism candidate

The attempted single provider was deliberately narrow:

| Contract item | Predeclared choice |
|---|---|
| State ABI | M159 uniform dyadic carrier; the carrier is frozen for a JVP. |
| Object integrated | Connected `Delta_211 = cumulant - M129 tree`; no raw `P3` is exposed as the answer. |
| Rank one | M154 exact moving-kink value/Price anchor `(D0, DB)`. |
| Rank-one opening | M165 rank-face subtraction. |
| Transverse rank two | M168 planar wedge/coarea anchor and one-sided cone tangent `(D0, DB)`. |
| Full-rank continuation | From the selected lower-rank face, subtract `D0 + epsilon DB`, then use one fixed 10-node Gauss–Legendre interior panel. |
| Value tolerance | `2e-8` in M159 dimensionless units. |
| Tangent tolerance | `2e-7` in dimensionless units, the currently locked M147 collision-source certificate. |
| Operation prediction | `571,904 <= 606,720` arithmetic-equivalent operations/coefficient under the inherited M168 bookkeeping model. |

The algebraic subtraction is

\[
D(\epsilon)=D_0+\epsilon D_B+
2\epsilon\int_0^1v\,[G(\epsilon v^2)-D_B],dv. \tag{1}
\]

It is connected-first: centralisation, cumulant, and tree assembly are to
occur before the endpoint limit.  The M165 rank-one model
`G(u)-DB=(3/2)A sqrt(u)` makes (1) exactly
`D0 + epsilon DB + A epsilon^(3/2)`; the test proves this identity over
rationals.  This preserves the important M165 lesson that subtracting the
face value alone is insufficient.

The prediction is **not** a native bill and was never treated as one:

\[
4096+7(11+20)(256)(10)+16(3)(256)=571904. \tag{2}
\]

The predeclared kill gates were: a uniform value/tangent enclosure at the
stated tolerance; an exact/conic route for every nontransverse or zero-face
state; and a native bill not above `606720`.

## Rigorous regularity obstruction to the fixed-10 enclosure

The proposed M168 face rule has a positive-marginal, rank-two hostile family

\[
L_\eta=\begin{pmatrix}1&0\\1&\eta\\0&1\end{pmatrix},\qquad
0<\eta<1,\qquad \Sigma_\eta=L_\eta L_\eta^T. \tag{3}
\]

It is PSD of rank two and its marginal variances are `1`, `1+eta^2`, and `1`.
Its three pair determinants are `eta`, `1`, and `1`, so this is within M168's
transverse domain for every positive `eta`; the first two kink lines become
arbitrarily nearly parallel as `eta` decreases.

Conditioning its wedge on `U=u` produces the M168 Price-indicator primitive

\[
\Pr(U+\eta V>0\mid U=u)=\Phi(u/\eta). \tag{4}
\]

This is not a sampled counterexample.  It gives an exact derivative bound.
For the 20th derivative at `u=eta`,

\[
\left|{d^{20}\over du^{20}}\Phi(u/\eta)\right|
=|\operatorname{He}_{19}(1)|\,\phi(1)\,\eta^{-20}.
\]

The exact recurrence gives `He_19(1)=182135008`.  The elementary strict bound
`phi(1)>1/5` follows from `e<3` and `pi<22/7`; therefore every maximum-based
20th-derivative enclosure has

\[
M_{20}(\eta)>{182135008\over5}\eta^{-20}. \tag{5}
\]

For a 10-node Gauss–Legendre panel on a unit-length ungraded interval, the
rigorous derivative remainder coefficient is

\[
c_{10}={(10!)^4\over21(20!)^3}
={1\over1743978047317826790650019840000}. \tag{6}
\]

Thus any such enclosure must report at least

\[
c_{10}M_{20}(\eta)>c_{10}{182135008\over5}\eta^{-20}. \tag{7}
\]

At the entirely ordinary, still-transverse state `eta=1/10`, (7) is exactly

```text
675537109375000 / 323419945960784673
= 0.0020887305121772243757962514...
```

That is over `104,436` times the `2e-8` normalized value tolerance.  At
`eta=1/100` the lower floor is exactly `10^20` times larger.  Its supremum
therefore diverges as the pair becomes nontransverse.

This is a uniform-enclosure failure, not a claim that the actual GL10 error
equals the upper remainder expression.  It proves that the predeclared
fixed-panel derivative certificate cannot close.  To escape it, a successor
would need a new, explicitly proved connected symbolic cancellation of this
near-parallel Price primitive or a parameter-scaled interval construction.
Neither is supplied by M154/M165/M168, and either changes the failed
mechanism rather than just raising a quadrature order.

## Complete stratum disposition

| Stratum | Attempted route | Result |
|---|---|---|
| Rank one; all marginals positive | M154 exact moving-kink anchor; M165 subtraction for a one-sided opening. | **Preserved component.** |
| Rank two; all marginals positive; pairwise transverse | M168 planar wedge/coarea anchor/tangent, then the proposed fixed GL10 interior certificate. | Anchor is **preserved**, provider is **killed** by (7). |
| Rank two; any parallel/coincident kink pair | M168's transverse coarea proof is inapplicable. | **Explicitly refused.**  `eta=0` in (3) localizes the boundary. |
| Rank three SPD | Intended rank-two-anchor continuation (1). | **Unresolved/killed within this candidate:** no certified interior primitive remains after the rank-two obstruction. |
| Any zero marginal PSD face | M159 retains the dyadic state but correlation coordinates and an ordinary two-sided tangent are undefined. | **Explicitly refused** pending an exact deterministic reduction and a stated one-sided conic tangent. |
| Outward PSD-cone direction | Infeasible at the face. | **Refused.** |

Consequently the all-PSD claim cannot be made.  A physical float64 absolute
contract is also not restored: M159's scaled mantissa-plus-exponent ABI remains
the only valid representation choice for any later primitive.

## Tests and frozen evidence

`test_m171_rank_stratified_provider.py` has seven deterministic,
response-free tests.  It checks the predeclared tolerance/cost contract, the
rank-one `sqrt(epsilon)` subtraction identity, the rank-two PSD transverse
family, the exact Hermite/remainder enclosure, its `eta^-20` divergence,
nontransverse and zero-face refusals, and the final kill gate.

The command below passed all seven tests with the local bundled interpreter:

```powershell
& 'work\headroom-recursion\.venv\Scripts\python.exe' -m unittest discover `
  -s 'work\scorefloor_generation\m171_rank_stratified_provider' -p 'test_*.py' -v
```

The prior frozen response-free suites M154 (7), M159 (5), M165 (4), and M168
(4) also passed unchanged.  M168's suite remains a reference-only check, not
a provider authorization.

## Salvage map and final disposition

- **Killed implementation:** the all-PSD connected-first provider using one
  ungraded fixed <=10-node interior panel.
- **Preserved components:** M159 dyadic carrier/zero-face discipline; M154
  rank-one exact anchor; M165 `D0 + epsilon DB` plus fractional endpoint
  subtraction; M168 transverse rank-two coarea anchor and tangent inventory.
- **Failure boundary:** collapsing pairwise transversality creates an
  `eta^-20` derivative obstruction before the fixed GL10 remainder can be
  uniformly bounded; nontransverse and zero-marginal faces are separately
  unimplemented.
- **Unresolved family:** a new provider with a fully symbolic connected
  near-parallel cancellation or a parameter-scaled interval/complex-analytic
  enclosure, plus a native bill.  It must re-enter as a new mechanism with its
  own fixed gates.

**Exact M171 disposition:**
`KILL_FIXED10_ALL_PSD_RANK_STRATIFIED_PROVIDER; PRESERVE_M154_M165_M168_ALGEBRA; REFUSE_NONTRANSVERSE_RANK2_AND_ZERO_MARGINAL_FACES; NO_PROVIDER_OR_606720_COST_CREDIT.`
