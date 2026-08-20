# M238 preimplementation erratum -- frozen target tape and gauge table

Date: 2026-08-09. Status: `SEALED_BEFORE_CODE_AND_TESTS`.

This erratum closes the two prenative review defects without changing M238's
mechanism, estimator, ceilings, seeds, gate order, or non-claims.

## Canonical target-tape generator

The target-shaped G0B/G0C tape is no longer described only as block diagonal.
It is generated exactly as follows under the pinned Python 3.14.4 / NumPy
2.4.6 environment.

1. Allocate C-contiguous little-endian/native float64 arrays
   `a[L,n], C[L,n,n], mu[L,n], V[L,n,n], p[L,n], r[L,n]` for
   `L=31,n=256`.
2. Initialize every inactive coordinate as an independent `N(0,1)` marginal:

   ```text
   a=0, Cqq=1, mu=1/sqrt(2*pi),
   Vqq=1/2-1/(2*pi), p=1/2, r=1/(2*sqrt(2*pi)),
   all inactive cross entries=0.
   ```

3. For one-based layer `ell`, construct the frozen existing parent state
   `M216.frozen_local_state(7, 221730000+ell)`. Construct
   `map_ell = Generator(Philox(238730000+ell)).permutation(256)[:7]`.
   Scatter, without arithmetic change, the parent's `mean`, `covariance`,
   `activation_mean`, and `activation_covariance` into the indexed seven-node
   block of `a,C,mu,V`.
4. On the same seven nodes compute only the frozen M179 unary definitions

   ```text
   sigma=sqrt(diag(C)); alpha=a/sigma
   p=Phi(alpha); r=phi(alpha)/(2*sigma).
   ```

   The resulting `mu,V` must already equal the M179 post-ReLU definitions; the
   packer may not repair or recompute them.
5. For each outer seed, start from the existing
   `M224.generated_native_batch(seed)`. Keep its float64 `g`. Set one-based
   `layer=repeat(1..31,128)` and map its canonical local labels through the
   corresponding `map_ell`. Store `layer,i,j,k` as C-contiguous signed int64
   and `g` as C-contiguous float64. No indices are supplied to the packer; it
   must form every gather index inside its billed invocation.

Canonical digest serialization updates SHA256, in the listed field order,
with `ascii(field_name) + NUL`, `ascii(dtype.str) + NUL`, the shape encoded as
little-endian signed int64, and C-order data bytes. Frozen digests are:

```text
tape a,C,mu,V,p,r:
  688463EBFC4CDB6EABEADABAF57A87F0FCB7B8DC26FA758B5ECE3C58CC802012

event receipt 221720001:
  BD6EB952F84034603BEDCF89D4542A350E0475CB21C94DC26637523A85A43479
event receipt 221720002:
  6872C6BDDEBF2C43A5CAB77D66CC7B34C7C94A15FE26EEB9E97D481E0F48BC43
event receipt 221720003:
  223F52DAD7D3BFECD8F142E3F423B154EFC8FD8CEF9DA00A87394CAB3DEB4F6B
event receipt 221720004:
  F8E533B2FD3EEA9BFF2C3776A77A5E131D06A6B2BE149DC1F1D1D9D773B249F3
event receipt 221720005:
  C1E1887D7300C8A3526B7DF8436A0B5CDE38C9C71FF7D3A0B7CAADE52329DA2F
```

The adversarial repeat uses the first receipt digest. Across all frozen target
events, `Vij,Vik,Vjk` have zero exact zeros and minimum absolute value
`2.9276288362745095e-06`; therefore the target does not make the tree/path
terms vacuous. A digest or nondegeneracy mismatch kills before G0C.

Tape/receipt construction remains outside component timing and receives zero
production or integration credit. Its bytes, construction wall, and owner
pointers are reported separately in every native row.

## Explicit positive-gauge degrees

For a co-acted positive diagonal gauge with event factors `di,dj,dk`, output
degrees are frozen as:

| Degree | Columns |
|---|---|
| `1` | `g`, `pair_rho` |
| `di` | `repeated_mean`, `repeated_sigma`, `repeated_activation_mean` |
| `dj` | left `pair_base`, `pair_slope`, `pair_sigma`, `activation_mean`, `marginal_sigma` |
| `dk` | right `pair_base`, `pair_slope`, `pair_sigma`, `activation_mean`, `marginal_sigma` |
| `di^2` | `activation_vii` |
| `dj*dk` | `activation_vjk` |
| `di*dj` | `activation_vij` |
| `di*dk` | `activation_vik` |
| `di^2*dj*dk` | `tree` |

The G0A gauge test applies independently varying positive factors, transforms
the tape and receipt jointly, and checks each row against this table. It may
not regenerate a favorable state after seeing a result.

## Literal M224 chart predicate

The previously named strict conditional chart means the unchanged M224
predicate, evaluated for both antithetic signs:

```text
abs(rho) <= 0.08
abs(alpha_left), abs(alpha_right), abs(t_left), abs(t_right) <= 0.8
0.8 <= pair_sigma_left/marginal_sigma_left <= 1.2
0.8 <= pair_sigma_right/marginal_sigma_right <= 1.2
abs((ReLU(ai+si*g)-mui)/si) <= 9
all values finite.
```

M238 must reproduce M224's membership exactly; it may neither widen this
predicate nor classify a refusal as zero.

