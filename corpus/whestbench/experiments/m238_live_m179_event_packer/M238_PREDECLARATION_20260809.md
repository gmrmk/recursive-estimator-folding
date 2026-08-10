# M238 predeclaration -- live M179 strict-distinct event packer

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_CODE_AND_TESTS`.

M238 changes one mechanism only: it replaces M221/M228's generated Python
`PackedBatch` construction with one preallocated, FlopScope-metered gather and
algebra pass from a provenance-bound M179 layer tape into M226's exact 20-column
ABI. M224's numerical atom, M226's 171-call kernel, the strict `[2,1,1]`
estimator, event proposal, outer normal draw, source coefficient, response,
and variance law are unchanged and remain outside this mutation.

This is an incremental packer component. The layer tape must already exist as
live float64 operands. M238 receives no credit for producing M179 states,
retaining the tape, producing event labels or `g`, running M226, or integrating
the full estimator.

## Frozen live inputs

`StackedLayerTape` is one immutable object for `L` one-based layers and one
producer epoch. It binds these exact owner arrays and their object/data-pointer
receipts:

```text
a   [L,n]       pre-ReLU means
C   [L,n,n]     pre-ReLU covariances, exactly symmetric
mu  [L,n]       post-ReLU means
V   [L,n,n]     post-ReLU covariances, exactly symmetric
p   [L,n]       M179 LocalReluJacobian.probability
r   [L,n]       M179 LocalReluJacobian.mean_variance_derivative
```

`StrictEventReceipt` binds `layer[L*K]`, canonical distinct labels
`i,j,k` with `j<k`, and `g[L*K]`. Every layer occurs exactly `K` times. The
receipt and tape share epoch/provenance. Duplicate, missing, reordered,
foreign-epoch, copied-owner, wrong-width, wrong-layer, noncanonical, or
non-strict events fail before a charged output write.

The target is frozen at `L=31`, `n=256`, `K=128`, `N=3968`. A target-shaped
generated tape is block-diagonal but has the literal target shapes and strides;
it is constructed before component timing and receives no production credit.

## Exact 20-column map

For event `(ell,i,i,j,k,g)`, put

```text
si2=Cii; si=sqrt(si2)
cij=Cij; cik=Cik
vj=Cjj-cij^2/si2; vk=Ckk-cik^2/si2
sj=sqrt(vj); sk=sqrt(vk)
cjk_i=Cjk-cij*cik/si2
rho=cjk_i/(sj*sk)
```

M238 emits the exact M226 names:

```text
g                         = receipt.g
repeated_mean             = ai
repeated_sigma            = si
repeated_activation_mean  = mui
pair_base_left/right      = aj, ak
pair_slope_left/right     = cij/si, cik/si
pair_sigma_left/right     = sj, sk
pair_rho                  = rho
activation_mean_left/right= muj, muk
activation_vii            = Vii
activation_vjk            = Vjk
activation_vij/vik        = Vij, Vik
marginal_sigma_left/right = sqrt(Cjj), sqrt(Ckk)
tree                      = tree_211(i,j,k)
```

No field may be supplied by M221's generated local-state oracle in the target
path. `g` is a read-only alias of the event receipt; every other event-dependent
value is gathered or computed inside the metered packer.

## Exact tree reduction

M213 defines `tree_211` through 12 undirected labelled paths plus four star
centres. With `d=Vii`, `x=Vij`, `y=Vik`, `z=Vjk`, M179's `p,r`, and

```text
eta2[q] = 2*r[q]/p[q]^2
eta3[q] = -2*a[q]*r[q]/(Cqq*p[q]^3),
```

the same tree is exactly

```text
2*x*y*(d*(eta2i^2+eta3i) + z*eta2j*eta2k)
+ 2*eta2i*(d*z+x*y)*(eta2j*x+eta2k*y)
+ z*(eta3j*x^2+eta3k*y^2).
```

The reduction follows from `eta2=gamma2/relu_scale` and
`eta3=gamma3/relu_scale^2`; all ReLU-scale denominators cancel along each
path/star. A dependency-free exact monomial-census test must prove equality of
the nine resulting monomials before numerical tests. This identity supplies a
tree column only; it does not supply a physical fourth cumulant or a response.

## Domain and fail-closed rules

All inputs and intermediates must be finite. Require `Cqq>0`, `p[q]>1e-12`,
`vj>0`, `vk>0`, and a strict conditional pair chart. No clipping, ridge,
absolute-value variance repair, label swap after issuance, rank-face limit,
fallback, or zero substitution is permitted. M226/M224's frozen rho-.08 chart
and all existing numerical refusals remain binding.

Positive diagonal gauge must scale every column by its declared label degree;
co-permuting tape and receipt must only permute labels. Tape/receipt owners and
all output views are immutable during a bound kernel invocation. The packer
may overwrite its own setup-owned scratch, never the tape or receipt.

## Frozen gate order

### G0A -- exact algebra and provenance

Before native work:

1. dependency-free monomial census returns zero difference terms;
2. widths `3..7`, seeds `238700003..238700007`, every strict owner, and
   `g in {0,+-.25,+-1,+-2.5}` match M221's reference 20 columns;
3. direct `tree_211` parity is `<=5e-13*(1+abs(reference))`;
4. M224 values/radii/chart decisions match within M224's certified radius;
5. positive-gauge, co-permutation, zero-write refusal, and all hostile
   provenance/lifetime substitutions pass; and
6. target-shaped staging has no dense rank-3 source, response, truth, scorer,
   challenge weight, or private-data dependency.

Any failure kills M238 before a native process.

### G0B -- static FlopScope contract

All fixed-shape buffers and views are allocated in setup. The measured packer
must include every integer index operation, gather, copy/write, square root,
division, multiply/add/subtract, finite/domain check, and tree operation. It
must have:

```text
incremental billed FLOPs <= 4,000,000
incremental operation calls <= 192
incremental persistent plus transient owned bytes <= 4 MiB
zero runtime empty/reshape/concatenate/sort
zero arithmetic or event-dependent mutation outside BudgetContext
```

The exact observed operation dictionary is evidence, not permission to raise a
frozen ceiling. Failure kills before native timing.

### G0C -- one bounded native aggregate

Only after G0A/G0B pass, one runner may execute five fresh processes for outer
seeds `221720001..221720005` plus one adversarial repeat of `221720001`.
Each process times the packer immediately followed by the unchanged already-
allocated M226 kernel. Every row must satisfy:

```text
combined bill <= 25,693,056
combined raw wall < 0.016133916999970098 s
raw speedup versus M216 > 100x
peak RSS <= 512 MiB
zero fallback/chart mismatch/allocation/provenance/finite failure
M224 value and radius parity inside the certified radius
```

One failed row kills M238. There is no retune, rerun, seed replacement, median
rescue, setup exclusion of event-dependent work, or threshold change.

## Explicit non-claims and next gate

Passing M238 would validate only the live-tape-to-M226 packer. Current M179
does not expose this stacked tape as an arithmetic-identical native owner, so
no M179 reuse/integration credit is available here. Variance, Source211
assembly, M125b transport, M198 conversion, terminal response, score, and
leaderboard gates remain closed. A later child may address the M179 producer
seam only if M238 passes all three gates.

