# M123 pretheory — implicit bridge-tree Krylov source factor

## Status and firewall

**KILLED PRETHEORY at the static compute/certificate gate.  No efficacy run is
authorised.**

M123 asks whether M122's exact implicit fourth-order Gram action can construct
a standardised rank-4 source factor at all 31 hidden sources while staying
below `152B` incremental effective compute over M120's `105.910B` floor.
Everything here is generated algebra and static arithmetic.  No contest,
public, private, scorer, champion, submission, or outcome data is reachable.

The killed implementation is a fixed block-Lanczos schedule.  The exact orbit
fusion is preserved as a reusable component for a different mutation.

## Frozen mathematical object

For the zero-mean path subset, with symmetric standardised bridge `Q`, let

```
S4_ijkl = sum_(p in 12 undirected labelled paths)
          Q_{p0,p1} Q_{p1,p2} Q_{p2,p3},
G = S4_(1) S4_(1)^T.
```

Simultaneous permutations of the three summed slots and exchange of the two
Gram copies reduce the 144 ordered path pairs to 16 exact orbits.  Thirteen
orbit matrices are explicitly constructible in `O(n^3)`; three remain generic
Khatri--Rao matrices but have exact `O(n^3)` actions.  The complete formulas
and generated `n<=8` checks are in the companion theory audit.

## Minimal fixed block-Lanczos schedule

The smallest possible block size is four.  In standardised coordinates use
the fixed, outcome-independent equivariant start

```
Zraw = [ 1, Q1, (Q circ Q)1, Q((Q circ Q)1) ],
Z0 R0 = qr(Zraw), without coordinate pivoting.
```

Fail closed when `sigma_min(Zraw) <= 2^-40 ||Zraw||_2`.  This happens at the
exact independent bridge `Q=I`; it is required rather than repaired by a
coordinate-dependent tie break.

The first nontrivial Krylov space is

```
K2(G,Z0) = span{Z0, G Z0}.
```

A block-Lanczos/Rayleigh--Ritz factor and its residual require two complete
Gram block actions:

```
W0 = G Z0
A0 = Z0^T W0
Q1 B1 = qr(W0 - Z0 A0)
W1 = G Q1 - Z0 B1^T
A1 = Q1^T W1
Q2 B2 = qr(W1 - Q1 A1)
T1 = [[A0, B1^T], [B1, A1]].
```

The top four eigenvectors of the `8 by 8` `T1` define the Ritz factor.  For a
Ritz vector with lower block coordinates `y1`, its exact residual norm is
`||B2 y1||_2`.  Predeclare projector tolerance `epsilon_P=1e-3`; an eventual
component would require a proved complement separation `delta` and

```
max residual / delta <= epsilon_P / 4,
delta > 2^-36 ||G||_2.
```

The division by four limits first-order error in a four-mode Tucker projector
to about `1e-3`.  A tie at the fourth/fifth boundary is fatal.  The common
shortcut `theta4-theta5 > 2 eta` is only a Ritz screen, not a proof of a true
gap; without an independently valid upper bound on the complement spectrum,
M123 must fail closed.

No observed spectrum selected block size, polynomial degree, or tolerance.
Deterministic block-Krylov theory cannot give a finite target-independent
iteration guarantee here because neither a fourth/fifth gap nor a nonzero
start overlap is proved.  Indeed `Q=I` gives a rank-one `Zraw` and a fully
symmetric boundary eigenspace.

## Frozen static cost gate

At `n=256`, one float32 square GEMM is billed

```
M(256,256,256) = 33,488,896.
```

The source algebra is float64, hence `66,977,792`, and the 25% safety factor is
applied once to the complete call count.

- Exact shared construction of the 13 easy orbit matrices: 19 square GEMMs
  per source layer.
- Exact action of the three hard fused orbits: 8 square GEMMs per vector.
- Rank-four block action: 32 square GEMMs per source layer.
- Layers: 31.

Therefore:

| fixed requirement | square calls | charged |
|---|---:|---:|
| easy setup, all layers | 589 | `49.312B` |
| one rank-4 block action, all layers | 992 | `83.052B` |
| static start plus one residual evaluation | 1,581 | `132.365B` |
| nontrivial `K2` factor plus residual | 2,573 | `215.417B` |

Even granting the unrelated implementation's best measured `0.779` L2
Strassen factor to every square product, the minimal nontrivial schedule is
`167.810B > 152B`.  This lower bound includes only the zero-mean path subset.
It excludes the nonzero-mean star terms, repeated-index collision cores,
31 source cores (`14.018B` already audited), source transports (`0.041B`),
dense defect/CP pairing (`16.641B` shape sum), bivariate response work,
copies, allocation, and residual wall time.  Adding omitted work only widens
the failure.

A zero-degree static Tucker factor can be residual-tested with one block
action.  Without the unverified Strassen credit, adding just the three already
audited source items raises it to `163.065B`.  With that credit it is
`133.812B` before every collision/nonzero-mean/scalar cost, but it is no longer
a nontrivial Krylov construction and has no deterministic top-four guarantee.
It is a separate possible mutation, not a rescue of M123.

## Nonzero-mean source boundary

M85/M122 is zero-mean.  At `alpha_i=mu_i/sigma_i != 0`, the local Hermite
coefficient of degree three is nonzero:

```
c1_i = sigma_i Phi(alpha_i)
c2_i = sigma_i phi(alpha_i)/2
c3_i = -sigma_i alpha_i phi(alpha_i)/6.
```

Consequently the weak-tree fourth cumulant contains both weighted paths
(two degree-two internal vertices) and weighted stars (one degree-three
centre).  The zero-mean 16-orbit path operator is only a necessary subset of
each later source, not the complete 31-source algebra.  Exact one/two-label
entries also require nonzero-mean bivariate cumulants.  No such complete
operator exists in M85/M122.  Because the necessary path subset already fails
the cost gate, M123 does not invent or outcome-test that missing extension.

## Invariance

For a hidden permutation `P`, `Q'=P^T Q P` and `Zraw'=P^T Zraw`.  Unpivoted QR
and block Krylov therefore transform the subspace by `P^T`; basis signs or
rotations are absorbed by the simultaneously transformed Tucker core.  A
fourth/fifth tie fails closed.

For a positive ReLU gauge `D`, compute everything from standardised `Q` and
restore physical scale only as `V=diag(sigma_h)U`.  Then `V'=DV` and with
`W'=D^-1W`, `W'^T V'=W^T V`.  Coordinate pivoting, unstandardised HOSVD, or a
tie break based on the first nonzero coordinate is prohibited.

## Disposition

`KILL_M123_FIXED_BLOCK_KRYLOV_NO_OUTCOME`.

Preserve:

- the exact 16-orbit reduction;
- the 19-GEMM easy setup;
- the three hard actions fused to eight GEMMs per vector;
- the standardise/factor/restore gauge rule; and
- the rank/gap/tie fail-closed conditions.

Reopen only after changing the failed mechanism: use a static equivariant
Tucker factor, reduce the number of source layers by a proved ownership rule,
or derive a direct response contraction that removes the factor construction.
Changing Lanczos tolerances or assuming a favourable spectrum is not a new
mechanism.

