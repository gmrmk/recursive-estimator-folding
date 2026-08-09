# M243 preimplementation erratum 3 -- authority closure

Date: 2026-08-09

This final no-code erratum closes the four authority gaps from the second
independent audit.  It was written before any M243 test, module, runner,
sampled manifest, launch intent, result, or evidence execution.

## Y1. Durable publication dependency

M243 binds exactly this committed helper:

```text
path = corpus/whestbench/experiments/m237_writeahead_native_receipt/
       m237_durable_native_receipt.py
sha256 = 774cef483c33b149524121144a4c5ede9141f094aa6fe5037414e31bddac873c
```

Only `canonical_json_bytes`, `write_launch_intent_exclusive`, and
`publish_native_result` may be imported.  M237's fixed filename constants are
not used; every M243 path is supplied explicitly.  Importing the helper alone
must create no file and launch no process.

## Y2. Codex-owned pre-shard sampled manifest

Only after a frozen G0A PASS, Codex may perform exactly one sampled-manifest
launch.  The binding paths are

```text
intent = M243_G0B_SAMPLE_INTENT_20260809.json
temp   = .M243_G0B_SAMPLED_EVENTS_20260809.json.tmp
final  = M243_G0B_SAMPLED_EVENTS_20260809.json
```

inside the M243 experiment directory.  All three must be absent beforehand.
The launch has a 60-second wall cap and 512-MiB peak-RSS cap.  A second intent,
timeout, partial result, or preexisting path fails and permanently closes all
G0B shards.

The builder alone regenerates P0/P1 `(mu,C,W)`, constructs the M147 bridge and
M133 proposal, and materializes the ordered 128+128 proposal draws with their
exact `q_e`.  It emits no coefficient, oracle, truth, response, variance, or
score value.  The canonical final JSON contains:

```text
all authority hashes and HEAD
cell names, seeds, stream seeds, widths, mixes
sha256(dtype.str || shape-json || C-order-bytes) for mu,C,W and bridge Q
ordered draw arrays and their same byte-level hashes
one q_e per ordered occurrence
q0 mass/support audit
intent and resource receipts.
```

The final canonical JSON SHA-256 is the sole shard-input manifest hash.  Fable
must regenerate every array, reproduce every hash and `q_e`, and refuse any
mismatch before its shard evaluates an event.

The execution order is now:

```text
G0A PASS
-> one Codex sampled-manifest launch
-> four immutable Fable shards
-> one Codex aggregation launch.
```

## Y3. Independent Delta reference and full conditional-pair radius

For every G0 event, `Delta_ref(e)` is the independent 100-dps direct outer
mean after the frozen 80/100 agreement gate passes.  Its Wick covariance and
M122/M126 tree polynomial are reimplemented with mpmath from independent
high-precision unary and pair moments.  Candidate M243 formulas are not
imported.  M147's binary64 `connected_minus_tree` receipt is reported as a
separate certificate/crosscheck and never defines `Delta_ref`.

Every `bias_Q(e)` is `mu_Q(e)-Delta_ref(e)`.

For an actual conditional singleton pair, let `x,y,rho_c,sjc,skc` be its
standardized means, correlation, and scales, and let the M178 half-widths be
`wP,wA,wB,wD`.  Freeze

```text
delta_c = (1-rho_c)(1+rho_c)
rad_raw = abs(sjc*skc) * (
            abs(x*y+rho_c)*wP + abs(y)*wA
            + abs(x)*wB + abs(delta_c)*wD)
          + 64*eps*(1+abs(raw_pair_center)).
```

The conditional unary means and fixed global centering terms carry an
additional `64*eps*(1+abs(centered_b))` rounding guard.  Expand final interval
endpoints outward with `math.nextafter`.  Multiplication by `r(g)`, antithetic
addition, polynomial subtraction, and analytic add-back each propagate
radii by absolute interval arithmetic plus the same 64-epsilon guard.  Thus
all four M178 widths, unary centering, products, and additions enter the
integrated `Z_Q` enclosure.

The generated state values themselves are fixed binary64 inputs, not interval
variables.  The direct actual-vs-`Delta_ref` bias gates remain binding even if
all local enclosures contain their references.

## Y4. Observable mpmath convergence criterion

Every frozen mpmath panel call uses
`mp.quad(...,method='tanh-sinh',maxdegree=12,error=True)`.  Sum the returned
absolute error estimates across panels.  At each of 80 and 100 dps require

```text
error_sum <= 1e-11*(1+abs(panel_sum)).
```

The existing 80/100 agreement gate is separately required.  Failure of the
error-sum bound is the observable `maxdegree=12` cap failure; no higher degree,
new panel, or retry is allowed.

## Y5. Precise firewall token

The bare `H` token in prior manifest prose means only

```text
M196 residual H_e := Delta_e-dtilde_e.
```

M243 `Htilde`, `Ha,...,Hbbbb`, and Hermite derivatives are required and legal.
G0 still forbids B1 state, `dtilde`, M196 residual `H_e`, `V_H`, and M196's
24 cells or seeds.

