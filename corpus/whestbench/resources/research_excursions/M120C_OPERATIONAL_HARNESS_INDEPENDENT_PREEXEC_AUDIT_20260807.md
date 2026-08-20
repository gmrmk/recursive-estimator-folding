# M120C operational harness independent preexecution audit - 2026-08-07

## Verdict: `REPAIR`

Do not create the schema-2 operational manifest and do not execute the
27-network/648-record grid. The mathematical R3 reference, actual recurrence
probe, frozen Philox plan, complete metric algebra, and representation tests
substantially pass. The operational freeze is nevertheless blocked by four
deterministic defects:

1. the manifest checker hashes different bytes from the bytes it parses;
2. the declared fixed result path is not the path the lifecycle publishes;
3. the gate object sent to JSON contains tuple keys and cannot be serialized;
4. a terminal-publication failure after RESULT can cause both RESULT and
   FAILURE to coexist.

The exact source closure also omits two modules imported and executed by the
CP implementation. These are repairable release/lifecycle defects, not a kill
of the M120 mechanism.

This audit did not edit any candidate source, create an operational manifest,
invoke `all_generated_metric_records`, execute the grid, or create the
canonical root, claim, result, failure, or terminal. A single bounded
width-16/depth-4 generated job was used to audit the real multi-hidden call
graph and representation invariant. All lifecycle mutations used temporary
directories.

## Frozen source identity

| file | SHA-256 |
|---|---|
| `m120c_protocol_config.py` | `492ede62bfd0b98ef26c4d6ea59a0237bc606a07e023dcd1f52479334582a119` |
| `m120c_protocol_harness.py` | `8c200f3cc1592456689af7a5e45337c6c24c5bfe566f000dc48fbf22938774eb` |
| `run_m120c_protocol.py` | `0538384ada4d71bc945a501549eb5476b89de99f2926dbc9bf2b03ca74fad623` |
| `m120c_analytic_dense_reference.py` | `f5e34f8ebc8ff2cafad63ccf55101155c802b01a36828bfc03edc820ad4a65f8` |
| `corrected_cp_jacobian.py` | `9bd61a90e53c1339a2717dcb3592865f75ff7a007db53952f3c9814d5d427f13` |
| `test_m120c_protocol.py` | `b22ed3a2c81edfe8938ec6b394d379062342cf5da7d3cfcd6aa341ff3ac2c838` |
| `test_m120c_operational_harness.py` | `489af4487ac73a25dd6901f2b9fd63f0cedabba15450a952e1491a5fec6583d2` |
| `test_m120c_analytic_dense_reference.py` | `09c5d12e7534683cdee907b8d61b21af437678604621bd9f0f7eb7b9d9cf5f1f` |
| `test_corrected_cp_jacobian.py` | `8981f955c24f6502a9a6945d96c66cf899430b1d46f43a9ea2fa1259a2a8df5d` |
| checked-in obsolete manifest | `61968d9818b398ddafa2f27b122ceae77e7968a1a6473d3e66d060950f38a3fe` |
| imported `fullcov.py` | `091989fbb2249f792f595020e2a475982fd6c5605e51b83065a1837cf51492f6` |
| imported `adjoint_born.py` | `f83a5299de16131a435598a74fd2d6f9c56af6c19b4e7505ae481f4f38ae08bd` |

The checked-in schema-1 manifest is not an execution release. Even when its
actual raw hash is supplied, `closed_manifest_errors` rejects it for schema,
root fields, fixed path, mode, atomic declaration, runtime, and source-key
set. No checked-in self-authorizing schema-2 manifest exists.

## R1: one-shot ownership and lifecycle - `REPAIR`

The positive structure is real. The runner has no CLI execution path. It
preflights the external manifest and canonical-root absence, then consumes an
`O_EXCL` claim before `all_generated_metric_records` can make the first Philox
draw. The canonical root and manifest path are derived from resolved source
locations. A failed or repeated claim leaves the root consumed. Pending
terminal files are same-directory, exclusive, file-fsynced, and atomically
replaced. Temporary-root tests confirmed publish-before-claim failure and
permanent claim no-retry behavior.

Three operational defects prevent closure.

### R1.1 Fixed result identity disagrees with the publisher

The externally sealed manifest would bind

```text
CONFIG.output_path =
  .../M120C_EXACT_GENERATED_OUTCOME/m120c_binding_result.json
```

but a successful lifecycle publishes

```text
.../M120C_EXACT_GENERATED_OUTCOME/M120C_RESULT.json
```

The parent directory agrees; the exact file identity does not. Thus the
manifest's purported fixed outcome is never written by the runner.

### R1.2 Passing gate objects are not JSON serializable

`evaluate_predeclared_gates` returns both cell maps with tuple keys such as
`(8,2)`. `run_authorized_m120c_grid` embeds that object directly in its result,
and `_write_exclusive` calls `json.dumps`. A synthetic complete 648-row gate
object failed exactly with

```text
TypeError: keys must be str, int, float, bool or None, not tuple
```

Because the pending file is opened before serialization, this also leaves a
consumed empty pending result. A grid that otherwise passes cannot publish its
declared success result.

### R1.3 RESULT and FAILURE are not mutually exclusive

The runner's `try` covers RESULT/FAILURE publication and subsequent TERMINAL
publication. If RESULT succeeds but TERMINAL raises, the catch block publishes
FAILURE. In an isolated lifecycle, an injected `os.replace` failure at that
exact boundary left

```text
.M120C_TERMINAL.json.pending
M120C_CLAIM.json
M120C_RESULT.json
M120C_FAILURE.json
```

This violates an unambiguous exactly-one-outcome invariant. If the first
outcome is FAILURE, the same catch path tries to publish FAILURE twice and can
abort before terminal evidence. A terminal failure must never reclassify an
already published outcome.

## R2: exact Philox computation and complete evidence - partial `PASS`, blocked publication

The frozen combinatorics pass independently:

```text
27 plan rows
27 unique Philox network seeds
72 unique Philox direction seeds
0 network/direction namespace overlap
648 unique (width,depth,replica,layer,output) keys
```

The dispatcher source iterates exactly that plan, validates every scheduled
representation transform, generates each job with
`Generator(Philox(seed))`, and requires exactly 648 records. The runner then
passes those records to the exact-coverage gate, which independently rejects
duplicates, omissions, and extras.

Synthetic 648-row mutations rejected missing, duplicate, extra, non-finite
complete-error, three-direction, and non-finite-direction cases. Directions
are four signed, unit, Philox pairs indexed only by width/depth/layer/direction;
there is no output, replica, outcome, or retry index. The stored state is
exactly `(D*b,D*A*D)` and the error denominator is the complete reference
state norm with a `1e-10` rejection boundary.

The bounded width-16/depth-4 job emitted all 48 hidden-layer/output rows. Call
instrumentation observed three analytic forward-moment calls, three analytic
local-kernel calls, and three analytic dense pullbacks. Every row had four
signed directions and a finite reference norm above the rejection floor. This
confirms that the approved analytic reference is operationally used and that
the dense reference and CP base are compared at every hidden layer and output.

The tuple-key JSON defect means the complete evidence cannot yet reach the
atomic result, so R2 is not operationally closed.

## R4: closed schema/source/runtime identity - `REPAIR`

The schema-2 checker has strong positive checks: exact root field set, status,
protocol, grid, firewall, runtime dictionary, atomic declaration, and exact
source-key set. An entirely in-memory valid schema-2 payload passed. Independent
mutations to schema, runtime, missing source, extra source, source hash, grid,
firewall, root fields, and the externally supplied digest all rejected. No
manifest file was created by these probes.

### R4.1 Manifest hash/use race

The verifier parses one read:

```text
raw = path.read_bytes()
manifest = json.loads(raw)
```

but later verifies `_sha256(path)`, which reads the path again. An in-memory
adversarial read returned a complete valid manifest first and unrelated `{}`
bytes second; supplying the hash of `{}` produced `errors == ()`. The external
digest therefore does not bind the identity that is actually parsed.

The verifier must compute `sha256(raw)` and parse that same captured byte
buffer. A regression must swap the second filesystem value and prove that no
second read can affect authorization.

### R4.2 Imported source closure is incomplete

`corrected_cp_jacobian.py` executes these imports at module load:

```text
scorefloor_generation/fullcov_gaussian_mm/fullcov.py
scorefloor_generation/adjoint_cumulant/adjoint_born.py
```

Neither file is in `EXPECTED_SOURCE_KEYS`, although both were included in the
earlier reviewed dependency set. The selected operational CP functions do not
call their exported approximate routines, but the modules are still imported
and executed before the harness exists. An exact executed-source closure must
either bind both hashes or refactor the operational CP carrier so it does not
import them.

The Python executable and NumPy init/version/path identity checks themselves
passed their mutation probes.

## R5: actual recurrence representation checks - `PASS` in scoped source

The schedule is deterministic and outcome-independent: each job derives one
permutation and positive gauge per hidden layer from a Philox namespace based
only on its frozen seed. Permutation validation rejects non-binary, non-square,
and non-bijective matrices; gauges must be finite and strictly positive.

`validate_operational_reparameterization` runs both the analytic-dense and CP
reverse recurrences on the original and simultaneously transformed network.
For every hidden layer and output it compares exact record identity,
standardized reference and CP states under permutation, complete error, and
transported signed contractions at `1e-10`. The existing bounded test and the
independent width-16/depth-4 multi-hidden probe both passed. The uncalled grid
dispatcher invokes this validator for every one of the 27 jobs.

R3's separate third audit already granted the analytic reference
`PASS_TO_INTEGRATE`; the operational call instrumentation above confirms that
the harness uses it rather than the clipped/floored finite-difference oracle.

## Firewall, tests, and absent outcome state

Static inspection of the operational call graph and its two imported Gaussian
modules found no network client, public/official result loader, target, scorer,
leaderboard, or champion access. Weights and directions are generated locally
from fixed Philox namespaces. The firewall is an exact manifest field.

Executed source-only checks:

- protocol, operational, analytic, and corrected-CP suites: **29/29 passed**;
- `py_compile` passed for all nine manifest-listed source/test modules;
- adversarial manifest/runtime/coverage/lifecycle probes described above;
- one bounded deepest/widest job and its actual representation check;
- no call to the 27-job dispatcher.

After all checks:

```text
out/                                      absent
M120C_EXACT_GENERATED_OUTCOME/            absent
operational schema-2 manifest             absent
canonical claim/result/failure/terminal   absent
```

## Required repair before re-audit

1. Make `CONFIG.output_path` and the successful lifecycle result path exactly
   identical, and test the equality.
2. Normalize cell gate maps to a stable JSON schema before publication; add a
   full synthetic 648-row JSON round-trip test.
3. Restructure the runner so computation chooses one outcome, exactly one
   RESULT or FAILURE is published, and TERMINAL failure cannot publish the
   opposite outcome. Add injected interruption tests after each publication
   boundary.
4. Hash and parse one captured manifest byte buffer; add a swap-race test.
5. Bind `fullcov.py` and `adjoint_born.py`, or eliminate their import-time
   participation from the operational CP module.
6. Recompute all source/test hashes and independently re-audit with the
   canonical root and external manifest still absent.

Until those repairs pass, the only honest state is `REPAIR`, not
`PASS_TO_EXTERNAL_FREEZE`.
