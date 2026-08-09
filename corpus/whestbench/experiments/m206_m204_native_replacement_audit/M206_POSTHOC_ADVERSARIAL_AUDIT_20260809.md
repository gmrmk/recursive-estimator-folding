# M206 post-hoc adversarial audit: M204 is not an arithmetic-identical M151 replacement

Disposition: **`KILLED_M204_ARITHMETIC_IDENTICAL_M151_REPLACEMENT_CLAIM`**.

This is a post-hoc, generated-only, response-free audit of one claim made
available by M204's algebra: that its one rank-one contraction could replace
the dense source-emission family already booked by M151. It is not a
predeclared candidate outcome, a source-variance result, a score result, a
response result, or a contest run. No model weights, truth, scorer, private
instances, leaderboard, or submission were read or invoked.

## Exact first mismatch

For a rank-one B=1 Rademacher pair with factor `u`, let

```text
a = u^T W
B = W^T diag(u^2) W
b = diag(B)
```

The complete-domain M204 lift has

```text
C_aaab = -6 [ diag(a^2) B + (b*a) a^T ]
C_aabb = -2 [ b(a^2)^T + (a^2)b^T + 4 diag(a)Bdiag(a) ]
C_aaaa = diag(C_aaab).
```

It exactly compiles the full table

```text
c_all(i,j,k) = -2 u_i^2 u_j u_k.
```

M151's `C_211` owner instead has

```text
c_151(i,j,k) = c_all(i,j,k) * 1{i,j,k pairwise distinct}.
```

Therefore the two agree on every distinct coefficient but disagree first on
collision rows, which M151 requires to be exactly zero. On a fixed generated
width-five fixture, the test compares the one-Gram lift to M156's
`compiled_extended_star_control(W, uu^T)` and obtains slot agreement, then
compares it to M151's `forward_b1_control_source` for the same padded 49-node
state and obtains a strictly nonzero source-slot difference. This is an owner
and residual-domain mismatch, not a floating-point tolerance issue.

The exact match is thus:

```text
one-Gram rank-one compiler == M156 complete-domain lift
```

not:

```text
one-Gram rank-one compiler == M151 strict C_211 source emission.
```

The residual required to make the lift unbiased is a new full-domain residual
law with collision terms. It cannot reuse M151's residual unchanged.

## One-B-only collision witness

When `u` is Rademacher, `diag(u^2)=I`, so `B=W^T W`. Collision corrections
expose, among other quantities,

```text
D = (W^2)^T(W^2).
```

M206's width-two witness uses `W0=I` and the 45-degree rotation
`W1=[[1,-1],[1,1]]/sqrt(2)`. Both give `B=I`; their `D` values are respectively
`I` and the all-`1/2` matrix. Hence a one-B-only reconstruction cannot infer
this collision statistic. This is deliberately not a claimed lower bound on
all possible arithmetic circuits: another circuit can use `W` directly, but
it is a new traced operation and cannot receive the asserted one-B reuse
credit.

## Strict cost arithmetic

M199's no-credit partial is

```text
M151 + M179 = 98.013128528B,
headroom     =  1.986871472B.
```

Pinned FlopScope 0.10.0 charges a 2D matmul `m x k @ k x n` as
`dtype_rate * (2mkn-mn)` (`work/whest-v014/.../flopscope/_flops.py`,
`matmul_cost`). With `n=256`, f64 rate two, and 31 source layers:

```text
B = W^T diag(u^2)W       2.076311552B
a = u^T W                0.008110592B
raw minimum               2.084422144B
raw excess                0.097550672B
```

Thus even the unprotected raw `B+a` accounting fails before source-slot
pointwise work, collision residual work, M172/M198 conversion, copies,
allocations, or residual wall time. Applying M151's 1.25 protection rule gives
`2.605527680B`, an excess of `0.618656208B`. For reference, a terminal
background propagation alone needs at least two f64 square products and one
f64 row product, `0.134217216B`; no terminal credit has been established.

M179 does not furnish `B`: its live covariance contraction is
`W^T V_prev W`, while the rank-one compiler requests `W^T diag(u^2) W`.
They are different operands and results except in a pathological special case.
Neither M179's live state nor M151's existing protected emission is therefore
shared by shape alone.

## Architectural replacement is a new estimator, not a reuse

The rank-one complete-domain algebra is preserved as
**`LIFTED_RANKONE_ALGEBRA_PRESERVED_DISTINCT_ESTIMATOR_COMPONENT`**. Any child
that wishes to use it must provide a new complete DAG and cannot inherit M151
source-emission credit. At minimum it needs all of the following:

1. A complete-domain physical owner and collision residual/proposal law,
   including a new variance gate; M206 performs neither variance nor MSE work.
2. An owner bridge accepted by M172/M198, because the existing M198 adapter
   consumes `m172_selective_22` ownership rather than an M151 rank-one C211
   packet.
3. A live M179 integration proving buffer identities. `W,a,C,mu,V,p,r,K,Hmu,Hv`
   must be bound to the source packet; an M179 covariance call is not `B`.
4. A target-shaped FlopScope trace that bills the rank-one state, `a`, `B`, all
   pointwise slot formation, collision/residual mechanics, 31 M198
   conversions, copies/frozen receipts, allocations, and wall time.
5. An explicit terminal `mu_32`/tangent response path. M179's 31-layer archive
   excludes that terminal.

M200's streaming fixture proves only response-free liveness of an opaque
packet: 31 source packets/conversions/injections, 30 internal transports, and
one terminal response. It supplies neither this physical source provider nor a
native cost certificate. Its frozen context copies are additive until charged.

## Reproducible falsifier

Run only:

```powershell
python -m unittest corpus/whestbench/experiments/m206_m204_native_replacement_audit/test_m206_m204_native_replacement_audit.py
```

The test performs fixed generated algebra at widths two and five. It has no
scorer, truth, proposal sampling, network instance, or response endpoint.

The smallest next lawful trace is not a performance test: it is a one-layer,
response-free FlopScope trace that emits the M151 strict source and the M204
complete lift from the same `W,u`, records all calls/buffers, and attempts a
collision correction. It must fail the claimed one-B identity before any
M179/M198 integration can be credited.
