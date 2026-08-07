# M153: exact pilot-state reuse audit

## Disposition

**CONDITIONALLY EXACT, NOT DEPLOYED.** M153 proves a narrow pilot-state reuse
mechanism in an isolated descendant of M145. It cannot remove the 32 dense
proposal-pilot products. It can remove only the overlap with the Formal pilot
while every preceding Formal active set is the complete ordered width. The
target-shaped structural MLP has such a prefix through Formal layer 3 and
breaks at Formal layer 4. The frozen M145 sources, comparator, Formal-L1
dependencies, outcome protocol, and champion were not changed.

This audit opened no truth, labels, reference vector, efficacy artifact, score,
leaderboard, or submission, and did not change the champion. It uses one generated weights-only
MLP, the already permitted M145 structural setup seed, and a FlopScope trace.

## Algebra and ownership boundary

Let `G` be M145's 1024 pilot rows, and write

```text
D1 = [relu(G W1); relu(-G W1)]
D(l+1) = relu(Dl W(l+1))                  # dense proposal pilot
F1 = D1
F(l+1) = relu(Fl W(l+1)[A(l-1), A(l)])   # Formal pilot
```

Here `A0` is the complete ordered width and every later `Al` is the exact
Formal active set: analytic cold screening plus the owned first-256-pair
rescue. The proposal needs the final even dense activation `D32`; the Formal
path instead needs its own pruned/folded states.

Induction gives `Fl = Dl` exactly only while every prior active set is the full
ordered `0..255`. If the first omitted set is `B = I \ A`, the next dense
preactivation contains

```text
Dl[:, A] W[A, next] + Dl[:, B] W[B, next],
```

whereas Formal owns only the first term. The second term cannot be recovered
from the dense downstream activation without a new product; rescue has checked
only its owned 512 rows and cannot establish that it is zero on the remaining
pilot paths. A dense column slice is therefore rejected after the first
reduced active set. It also has a different FlopScope geometry and can change
float32 reduction rounding.

Consequently:

- The dense 32-layer pass remains required for the proposal law. Replacing it
  by Formal/folded values would alter the response statistic consumed by
  `fit_proposal_f32`.
- The universally safe overlap is exactly `formal:first:pilot`.
- A later overlap is safe only under the run-time full-width guard. In the
  frozen structural trace, Formal layers 2 and 3 are `2048 x 256 x 256`, so
  they share the complete prefix; Formal layer 4 is `2048 x 256 x 253`, so the
  guard stops. The theoretical maximum is a 29-product Formal prefix only for
  an all-active network; it is not a generic claim.

M153 caches the first preactivation and the post-ReLU dense states at layers 2
and 3. The first is copied bit-for-bit before the shared workspace is reused.
For layers 2 and 3 the cached state is re-fed to Formal's existing ReLU; the
ReLU is idempotent, including propagated NaNs and the normalized zero result.
No proposal random draw, coefficient, frame, main activation, rescue rule,
rounding path after the guard, or estimator target is changed.

## Target-shaped structural result

`M153_PILOT_PREFIX_REUSE_STRUCTURAL_TRACE_20260807.json` uses the exact M145
generated structural MLP only. It asserts all of the following:

- the 32 `pilot_surrogate:*` stages are identical in baseline and reuse;
- proposal state, final prediction, and restored frame bank are byte-equal;
- exactly these Formal dispatches are removed:
  `formal:first:pilot`, `formal:layer2:pilot`, and
  `formal:layer3:pilot`;
- `formal:layer4:pilot` remains dispatched normally;
- the dispatch total falls from 701 to 698 and FlopScope `matmul` calls fall
  from 1,078 to 1,075.

| quantity | baseline M145 | M153 prefix reuse | difference |
|---|---:|---:|---:|
| billed FlopScope operations | 184,270,895,262 | 183,681,317,022 | -589,578,240 |
| formal dispatch calls | 701 | 698 | -3 |
| FlopScope `matmul` calls | 1,078 | 1,075 | -3 |
| local residual seconds | 0.135879097 | 0.129084203 | -0.006794894 |

The removed shape bills total 589,840,384: one `1024 x 256 x 256` product
(118,013,952) plus two `2048 x 256 x 256` products (235,913,216 each). M153
adds one 1024-by-256 `copyto` to preserve the first preactivation, charged at
262,144 operations; thus the measured net bill change is exactly
`589,840,384 - 262,144 = 589,578,240` in this trace. The residual observation
is one local structural measurement, not an official-runtime forecast; it
must not be extrapolated, including at any higher residual conversion.

## Memory schedule

The retained state is bounded and released when consumed or when the first
full-width guard fails:

| state | bytes |
|---|---:|
| first pilot preactivation, `1024 x 256 x float32` | 1,048,576 |
| dense activation layer 2, `2048 x 256 x float32` | 2,097,152 |
| dense activation layer 3, `2048 x 256 x float32` | 2,097,152 |
| retained before Formal entry | 5,242,880 (5 MiB) |

The dense proposal forward uses a third 2048-by-256 work buffer while the two
retained activations remain live. Relative to M145's one mutable dense pilot
activation, this is 4 MiB more activation storage plus the 1 MiB first-pre
copy: a 5 MiB exact static increment. M145's locked local operational peak was
481.977 MiB, so simple object accounting places this schedule below 486.977
MiB. That is not a fresh resource authorization: a clean-process M153
working-set trace is mandatory before any promotion, because allocator and
FlopScope lifetimes can invalidate additive RSS reasoning.

## Causality, coupling, and estimator semantics

The cache is populated during the same pilot-only phase, before proposal
freezing and before the 122 main frames are transformed. Its use is a pure
memoization of already evaluated float32 state. Therefore the proposal map,
mixture weights, transported main rows, complete-frame coefficients, and any
existing estimator bias/unbiasedness status are unchanged. M153 neither adds a
new estimator claim nor repairs any existing one.

The matched comparator remains byte-for-byte M145 code and is not given
candidate pilot state. Candidate provisional-frame restoration is byte-equal
to baseline in the structural trace. Thus M153 does not loosen the matched
bank/seed coupling or let the comparator consume candidate-only responses.

## Static disposition and next gate

Do not merge this prototype into M145 or the champion. The only admissible
future integration is the exact guarded prefix mechanism shown here, followed
by all of these truth-free gates in a fresh worker:

1. target-shaped FlopScope and clean-process memory trace;
2. bitwise baseline/reuse output, proposal, and bank-restoration checks;
3. adversarial early-pruning structural test showing the cache releases and
   the first reduced Formal product is dispatched;
4. independent hostile audit and a new frozen manifest/hash set.

Any proposal to reuse a dense state at a reduced active width, substitute the
Formal final activation for `D32`, or access an outcome artifact fails closed.
