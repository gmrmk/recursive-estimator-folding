# M203 exact terminal-contraction circuit audit

## Scope

Generation 6 Candidate B asked for an exact arithmetic circuit outside M170's
literal seven-product schedule. M203 searches polarization, phase/generating
codes, simultaneous packing, and recursive block Winograd for the generic
oriented `aaab` rank-3 and `aabb` rank-2 terminal channels.

No contest model, truth, scorer, leaderboard, submission, or private artifact
is used. The bill follows the recorded float64, 31-layer, 1.25 protection
convention and is independently executable.

## Closest exact circuit

Let `X=W`, `P=A W`, and `Q=A^T W`. Stack

```text
U3 = [2 X*P*Q; X^2*P; X^2*Q]     V3 = [X; Q; P]
Caaab = -3 U3^T V3

U2 = [X^2; 2 X*P]                 V2 = [P*Q; X*Q]
T = U2^T V2
Caabb = -2 (T + T^T)
Caaaa = diag(Caaab).
```

This is a genuine fusion: five tagged bilinear channels become two rectangular
contractions with inner dimensions `3n` and `2n`. It preserves the M166
orientation and collision-null algebra. It does not remove their generic
bilinear rank.

For one contraction, use the exact recursive bill

```text
D(m,k,n) = 2mkn - mn
R_0 = D
R_r = 7 R_(r-1)(m/2,k/2,n/2) + mk + kn + 2mn.
```

At `n=256`, the protected 31-layer terminal bill plus the already optimistic
exact triangular `AW,A^TW` projection is:

| depth | terminal rectangles | plus projection | over M151 slot |
|---:|---:|---:|---:|
| 3 | 9.069419520B | 11.649611520B | 1.358247760B |
| 4 | 8.320856320B | 10.901048320B | 0.609684560B |
| 5 | 7.963587520B | **10.543779520B** | **0.252415760B** |
| 6 | 8.171994320B | 10.752186320B | 0.460822560B |

Depth 5 is optimal among these levels and still exceeds M151's complete
`10.291363760B` allowance before feature construction, packing,
symmetrization, provider, M172/M198, allocation, or wall time. It exceeds the
strict M199 composed headroom `1.986871472B` by `8.556908048B`; even the
unlicensed background-replacement sensitivity leaves only `9.723621632B`,
which is `0.820157888B` short.

## Rank obstruction for algebraic relabellings

The generic `aaab` coefficient flattening has a `diag(2,1,1)` minor and the
`aabb` pair flattening has a `diag(1,2)` minor. Both determinants are nonzero
in characteristic zero. Polarization, real/complex phase coding, generating
functions, and reversible accumulation therefore cannot reduce the required
three and two independent channels; they only change basis. A concatenated
GEMM realizes the same rank through a wider inner dimension.

The audit does not prove a direct-sum theorem for every conceivable
simultaneous matrix-multiplication tensor. A future reopening needs an explicit
exact bilinear decomposition, generic-cell proof, and complete f64
operation/copy bill below the applicable headroom. Merely putting both outputs
inside one block call is not such a decomposition.

## Disposition

`KILLED_STANDARD_EXACT_TERMINAL_FUSION_COST`.

Preserve the two-rectangle exact identity and its depth-5 cost upper bound as
reusable tissue. It is the closest circuit found, but cannot unlock M151/M199.
M155's masked Khatri action, the M163 exterior collision policy, and M172 owner
transfer do not supply the missing physical compiler or cost credit.
