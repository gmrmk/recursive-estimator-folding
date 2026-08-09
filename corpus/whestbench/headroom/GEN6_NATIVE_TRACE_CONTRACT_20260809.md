# Generation 6 normalized native-trace contract

Status: **required evidence contract; no current implementation satisfies it**.

M200 proves a generated semantic/liveness stream. It is raw NumPy with native
cost marked `NOT_MEASURED`; it cannot resolve M199's accounting block. A lawful
target trace must execute this exact topology in one float64 process:

```text
(mu0=0, V0=I, tangent=0)
for k=1..31:
    (a_k,C_k,mu_k,V_k,J_k) = M179(mu_(k-1),V_(k-1),W_k)
    if k>1: tangent = M125b(tangent,W_k,J_k)
    slots_k = physical_provider(bound live layer k)
    delta_k = M198(slots_k,a_k,C_k,mu_k)
    tangent += delta_k
    release layer k except mu_k,V_k,tangent

(a_32,C_32,mu_32,V_32,J_32) = terminal_M179(mu_31,V_31,W_32)
terminal_tangent = M125b(tangent,W_32,J_32)
```

There are 31 source issuances and no source at `W_32`.

## Physical provider ABI

```text
emit(BoundLayer,
     out_aaaa[256], out_aaab[256,256], out_aabb[256,256], TraceSink)
```

`BoundLayer` borrows the exact live `W_k`, `mu_(k-1)`, `V_(k-1)`, `a_k`,
`C_k`, `mu_k`, `V_k`, and `J_k`, plus monotone generation and storage-version
receipts. It does not accept free substitute arrays. The slots must be finite,
float64, satisfy `aaaa==diag(aaab)` exactly, and have symmetric `aabb`.

A fixture, zero provider, `UNKNOWN` converted to zero, cubic parity oracle, or
caller-supplied unrelated covariance is an immediate block. For the only
current structured child, M205, the provider must additionally bind and emit
physical `K4`, directed `K31`, symmetric `K22`, and distinct `C211` owner
coefficients. Collision targets may not be zeroed as in M204/M156.

## Required trace events

Every operation and allocation records source location, dtype, shape,
input/output storage ID and write version, producer/consumer ancestry,
birth/death, FlopScope bill, native elapsed time, and one classification:
`shared`, `proved_replacement`, `additive`, or `unknown`.

Mandatory counts:

- 31 M179 source/background steps, 31 row means, 62 square background
  matmuls, and `31*32640=1,011,840` pair/Jacobian assemblies;
- 30 internal M125b transports, 31 injections, and one terminal transport;
- 31 M198 conversions and zero background/archive rebuilds;
- 31 real physical provider/compiler events;
- one charged `W_32` terminal `a,C,mu,V,J` path;
- if the M151 B=1 path is claimed: 93 map/emission calls, 3,968 coefficient
  calls, and 155 five-product batches must be observed, not inherited from a
  worksheet.

The current M198 copies of `a,C,mu` are additive and charged. A future zero-copy
borrow is a different mutation and needs parity/lifetime proof.

## Sharing rules

- Reading the same M179 `J_k` from M125b is a shared buffer, not a second
  Jacobian construction.
- M179 background maps and M125b tangent maps are additive because their
  operands and outputs differ.
- Sharing `W_k` or `V_(k-1)` as input is not arithmetic replacement.
- The standalone M125b cost is already inside M151; adding it again is a double
  count.
- M179's 31-layer archive does not replace the legacy 32-layer background
  without an executed call/result/lifetime deletion proof.
- M179's current Python code traverses pair moments separately for `V` and `J`;
  its ledger assumes a fused assembly. Native fusion needs exact parity and an
  executed bill before receiving credit.
- M206 proves M204's complete-domain Gram is not the strict M151 emission:
  their collision rows differ and one `B` does not determine the necessary
  correction. It receives zero arithmetic reuse credit. A new M205 caller may
  remove and replace the old strict caller only through a complete executed
  DAG/residual proof; that is architectural replacement, not sharing.

## Correct budget boundary

The conservative composed partial is

```text
98.013128528B
  + U_provider + U_M172 + U_M198 + U_terminal + U_runtime.
```

Only `1.986871472B` remains before all unknowns. The older
`10.291363760B` number is M151's isolated pre-M199 ceiling, not composed
headroom. A `9.723621632B` remainder exists only after a future trace proves
the exact legacy-background replacement; it is not current credit.

M206's no-credit raw lower envelope for M204's `B` and `u^T W` alone is
`2.084422144B`, already `0.097550672B` above the strict remainder before M198,
terminal, copies, allocation, or wall. Consequently the original M204 caller
is cost-killed. M205 remains blocked only as a different physical-owner caller
whose complete removal/replacement accounting has not been executed.

Residual seconds are charged at `1e11 FLOPs/s`. Physical allocator high-water
must be measured in the same process and remain at most 512 MiB; M200's logical
five-object ledger is not RSS evidence.

## Hostile gates

1. AST and runtime poison all raw NumPy compute/allocation on the target path.
2. Reject or explicitly charge f32, Python-list, noncontiguous, and implicit
   cast inputs.
3. Poison every full-archive/reference/labelled-recurrence helper.
4. Require the terminal output to depend on an explicitly billed `W_32` event.
5. Mutate alleged shared parents and verify consumers used the exact storage
   version; digest/value equality alone is insufficient.
6. Derive all subtraction/replacement rows from paired executed call IDs; no
   free-form negative worksheet entries.
7. Reject any fixture or omitted provider counter.
8. Cross-check M172 accepted-owner events, M198 copies/conversions, and source
   slot operations with trace deltas.
9. Charge allocations and wall time in process.

## Fail-closed dispositions

- `KILLED_NATIVE_SEMANTIC`: topology, parity, binding, lifetime, or trace
  completeness fails.
- `KILLED_PROVIDER_CONFIG_COST`: a real provider breaches the applicable cost,
  wall, or memory gate.
- `NATIVE_STREAM_SEMANTIC_PASS_PROVIDER_UNKNOWN`: native stream passes but the
  provider remains absent; no cost or estimator credit.
- `BLOCKED_OVERLAP`: any provider/replacement/copy/terminal/runtime term remains
  unknown. This is the current state.
- `COST_COHERENT_COMPONENT`: only a complete real-provider trace at or below
  100B with every sharing claim proved. It is still not an efficacy result.
