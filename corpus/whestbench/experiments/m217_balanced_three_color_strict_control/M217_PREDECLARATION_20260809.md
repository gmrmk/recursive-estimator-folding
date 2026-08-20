# M217 predeclaration -- balanced three-color strict-support control

Date: 2026-08-09. Frozen before implementation. M217 is generated-only,
response-free, and may not read challenge weights, truth, scorer output,
leaderboards, submissions, or efficacy records.

## Changed mechanism

M206 proves that M212's one-Gram rank-one compiler emits a complete-domain
control and cannot be treated as M151's strict pairwise-distinct control.
M215 investigates deterministic collision subtraction. M217 instead changes
the control randomization itself.

For width `n`, draw a uniformly random balanced partition `h` of labels into
three classes of fixed sizes `(n0,n1,n2)` differing by at most one. For a
fixed ordered triple of distinct labels,

```text
p3 = 6*n0*n1*n2 / [n*(n-1)*(n-2)].
```

For the rank-one coefficient `c(i,j,k)=-2*u_i^2*u_j*u_k`, define

```text
c_h(i,j,k) = c(i,j,k) * 1{h_i,h_j,h_k all distinct} / p3.
```

Every repeated-label row is exactly zero for every partition, while
`E_h[c_h]=c*1{i,j,k pairwise distinct}`. More strongly, conditional on the
drawn partition, the existing exact residual identity uses
`H_h=Delta-c_h`, so `source(c_h)+E_event[source(H_h)]=source(Delta)` without
depending on the partition expectation. The partition changes variance, not
bias.

The compiler must aggregate the six ordered color-role assignments using
three class-local self-Grams and class-local first moments. It may not build
an `n^3` table at target width and may not inject any collision row.

## Frozen gates

1. Exhaustively average all balanced colorings at widths 3--6 and recover the
   strict coefficient table to max absolute error `<=2e-13`.
2. At generated widths 3--9 and seeds `217001..217006`, compare the noncubic
   compiled `aaaa/aaab/aabb` source against M205's cubic parity oracle for the
   same colored table to `<=4e-11`.
3. Verify repeated-label support is bitwise zero, exact source conservation
   `source(T)=source(c_h)+source(T-c_h)`, positive gauge covariance, and
   pathwise joint label-permutation covariance.
4. A later target FlopScope 0.10.0 trace must use supported operations only,
   bill at most `1.600000000B` arithmetic, have hostile `bill+5e11*wall <=
   2.250000000B` on all five frozen seeds `217700001..217700005`, and peak at
   most 512 MiB. Backend packing is allowed; participant-created copies and
   temporaries must be explicit and billed.
5. No source-variance gate opens unless the algebra and native trace pass and
   an independent strict-distinct coefficient provider has passed its own
   identity/numerical gate. The later matched gate must include partition and
   nested-provider randomness in the full `F/(2q0)` contribution; coefficient-
   only variance is prohibited.

Kill this implementation on any gate failure. Preserve the coloring identity
and class-local compiler separately. This artifact grants no provider,
M198, terminal, MSE, score, or winner credit.

