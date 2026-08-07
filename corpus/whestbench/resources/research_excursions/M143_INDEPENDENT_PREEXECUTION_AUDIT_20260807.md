# M143 independent pre-execution audit -- 2026-08-07

## Decision: REPAIR -- do not authorize the frozen generated screen yet

M143 has a valid algebraic proposal mechanism, but its pre-execution contract
is not yet precise enough to run its sole generated response screen. This audit
did not run that outcome. It used only generated matrices and static proposal
code. No contest loader, scorer, truth, leaderboard, submission, champion, or
private/public model access occurs in the audited M143 files; I found no target
leakage.

## What passes

### 1. Sign-scrambled diagonal path identity

Let `W[r]` map activation `r` to `r+1` and let `p[r]` be the ReLU mean
derivative at that output interface. With independent unit-variance Rademacher
signs at terminal coordinates and every hidden interface, cross-path terms
cancel exactly:

```text
E[R+1] = terminal_energy,
G[r]   = p[r]^2 o E[r+1],
E[r]   = W[r]^2 G[r].
```

The code implements this recurrence. An independent exhaustive three-map,
three-coordinate enumeration over two hidden diagonals and terminal signs
agrees with `diagonal_path_energies(...)[0]` to `3e-12`. The five existing M143
algebra tests also pass when directly invoked. They are pytest-style free
functions, so `unittest` alone discovers zero tests.

### 2. M143 correctly substitutes a strength into M133's three-tree law

For supplied nonnegative `tau`, `make_output_aware_proposal` is exactly

```text
h(i,j,k) = tau_i^2 tau_j tau_k [S_ij S_ik + S_ij S_jk + S_ik S_jk]
q(i,j,k) = .05/[n(n-1)(n-2)] + .95 h(i,j,k)/sum_distinct h.
```

for every ordered distinct triple. Independent enumeration verified this
probability equality and normalization. Thus the inherited `1/(2 K q)` HH
weight gives the canonical `j<k` M133 sum in expectation, assuming `Delta` and
`F` retain singleton-label symmetry. M143 does not approximate M131's exact
coefficient and cannot by itself introduce coefficient bias.

### 3. Invariance and arithmetic, with qualifications

Under hidden positive gauges

```text
W[r]' = D[r]^-1 W[r] D[r+1],   s[r]' = D[r] s[r],
```

the recurrence gives `E[r]' = D[r]^-2 E[r]`, so `s[r] sqrt(E[r])` is
invariant. I independently checked this over a simultaneous three-map gauge.
Permutation covariance follows by the same relabelling argument.

At `n=256, L=31`, M143's current worksheet computes

```text
raw = 3*n^2*L + 16*n*L = 6,221,824,
protected = ceil(1.25*raw) = 7,777,280 = .007777280B,
94.940940240B + .007777280B = 94.948717520B.
```

The latter base is M133's complete protected `K=512` envelope, including its
coefficient, buffer, and wall reserves; it is not the smaller raw M133 ledger
subtotal (`82.315792720B`). M143 adds no batched rectangular five-product
update. Its backward loop does contain a square and a square-matrix-by-vector
product per layer, accounted for by the three `n^2` terms.

## Required repairs before any generated response result is opened

### A. Repair the equation, index convention, and API

The pre-theory writes `tau_i = s_i sqrt(sum W[i,a]^2 h_next[a])`, while the
implemented cached recurrence includes `p[r,a]^2` in the same-layer row
energy. The direct helper omits that gate unless callers manually pass
`p[r]^2 o E[r+1]`. An accidental, materially different proposal is therefore
possible.

Replace the prose with the `E/G` equations above, explicitly state that
`p[r]` sits after `W[r]`, and define `tau[r]=s[r] o sqrt(E[r])`. Remove the
direct helper or rename its argument `gated_downstream_energy`; make the
runner use only `output_aware_node_strength_from_row_energy(s[r], E[r])`.
Add a test that the direct and cached paths agree when the gate is supplied.

### B. Declare and isolate the source-scale mechanism

M133 uses `||W_i||`; M143 uses `s_i sqrt(E_i)`. Even with constant suffix
energy, the latter is `s_i ||W_i||`, not M133 unless `s_i=1`. This source-scale
factor was a component of the M139 killed composite. It is a valid preserved
component, but M143 is not a one-mechanism child as currently claimed.

Before execution, define `s[r]` exactly as a physical statistic of the same
frozen Gaussian/ReLU background, state its positivity/fail-closed rule and
gauge law, and label M143 a composite `source-scale + diagonal-suffix-energy`
proposal. Predeclare a diagnostic third arm `s_i ||W_i||`; retain M143/M133 as
the primary gate. Add simultaneous all-layer permutation/gauge tests including
bridge and selected source-layer proposal probabilities.

### C. Make the zero-strength probability match the stated law

`make_output_aware_proposal` silently replaces `strength` by
`maximum(strength, finfo.tiny)`. Uniform rescue already gives full support and
the parent sampler handles zero strengths. This floor changes the published
`q_M143` for zero-strength nodes. Remove it and add an exact zero-strength
normalization/probability test, or declare the floored law everywhere. Removal
is the cleaner repair.

### D. Freeze conditional randomness and tangent scope

Add a generated runner and manifest fields for background, M133, M143, and
bootstrap RNG algorithms and child-seed derivations; whether the two proposals
use common random numbers; one immutable `q` snapshot per `(cell,layer,method)`;
the chain depth/generator; M131 quadrature settings; response reference;
bootstrap count/seed/unit; and named unopened confirmation widths/seeds.

HH draws must be independent child-stream variates after proposal construction.
They are intentionally conditional on, not unconditionally independent of,
the frozen background. No q adaptation after HH draws or exact coefficients is
allowed.

The stated frozen-q tangent is valid for M133's source/background tangent with
fixed network weights: `E_q0[Delta_dot F/(2q0)]`. For a weight tangent it must
be `E_q0[(Delta_dot F + Delta F_dot)/(2q0)]`, still without `qdot`. Either
prohibit the latter or implement and test it; the current generic claim is too
broad.

### E. Freeze dtype and complete the non-overlap cost crosswalk

The algebra module casts inputs to float64, while the target worksheet borrows
M133's f32-style proposal envelope. FlopScope bills float64 at twice float32,
so `.007777280B` is not a dtype-certified billed number. Either use a frozen
f32 target recursion and trace it, or charge the f64 path correctly.

The cost crosswalk must also state that M133's existing `48*n^2*L` proposal
table allowance is replaced, not reused for old and new tables. List abs/copy,
strength-weighted edge tables, normalizers, categorical sampling, the
square/matvec recurrence, allocation, and wall time in one FlopScope trace.
No native trace exists yet.

## Parent-interface finding

M121's one-delay conversion and M125b coalescing are valid generated carrier
diagnostics but remain `REPAIR` for an integrated target estimator. M143 may
use their frozen small-width implementation only as its proposal-variance
screen. It must not describe that as a target-ready integrated pipeline.

## Evidence hashes

| artifact | SHA-256 |
|---|---|
| M143 pre-theory | `30d98006ff34c57874870b83b7076692655340ff7bf2ec9761e37ce09eadac8b` |
| M143 module | `90e82fa5957ca653c228ffaa9935451ee5bc4986caffb12eaae54a7d313fb942` |
| M143 tests | `3b83bbceca044baabfac697fe995b4c59348f405d87253f80b1268694d91a971` |
| M143 manifest | `29e8687ea490926a22da6af195a81ed606d3547be5a1cb8396b42e2afc0e7b1b` |
| M133 implementation | `c296c95ede532c1451e0444b9d56b51e96287ef251b11de9cacee0df7d1ea6b1` |
| M139 generated runner | `cbc663f1a23ccd665b533ffc406080eccfa22edb3c3143775fe9f2d9f9dbe540` |
| M139 frozen result | `1e33f933f04cb5e39b9b88a184a40627d21d3a3b90a66dbe825985178e09a389` |
| M121 interface audit | `0754c6ed2c4a47d6b961df93e29d8480b66843fc5dfee15980ea9f370212828f` |
| M125b audit | `f975c4c115ac1b331ddfa47267f840f5d1fa797ebbac752de5aebad922856020` |

No empirical response result was run. Once all five repairs are made and
re-audited, the root may authorize exactly one frozen generated development
screen. It may not authorize confirmation, target evaluation, champion
replacement, or submission from the current M143 state.
