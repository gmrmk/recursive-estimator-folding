# M116C B=4096 second independent pre-execution audit — 2026-08-07

## Verdict: PASS_TO_FREEZE

This is a fresh hostile, source-only re-audit of the repaired M116c
authorization boundary. It grants **no execution authority**. No M116c
execution release, canonical root, claim, child, full 64,512-row/depth-32
prediction, terminal artifact, release/root/manifest, target, scorer, or
network action was created or run.

The previous sole defect—the importable EXECUTION_TOKEN capability—is closed.
I found no new authorization or source-integrity blocker in the scoped repair.

## Frozen subject and current hashes

| Subject | SHA-256 |
|---|---|
| campaign_contract.json | f289cd0ca1e81273cd45398e3b6d827d946197db989a8db638318665ede09ebf |
| campaign_runner.py raw bytes | 6eecbfbe5c5c45dc5596d4946d2bbb78ef71466cdba6fde84e70118b4fad8333 |
| campaign_runner.py normalized seal | 66bbda5c7d5fe69551dc897e730e3ee4fc3e2dd677d314888387a27181737c2c |
| campaign_worker.py | bdc6d2a6666c65a370d68f43a743458e8a811ac8cd0ec57a3a3f7704571e6d56 |
| cost_model.py | ee1d0dc3f9f15239cc7561c6437545c5c316f8148d9b70060217488428c6a2e3 |
| inplace_l3.py | 114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83 |
| test_campaign_harness.py | fcf1c4da66ebc2d4199e98870b400046c87fd4d4a3159763785bb3ec3cba2ecb |
| test_inplace_l3.py | 8ea9e38de9a6e61615a362c363e2a9312c0cd86196600d549465fda44fea1a8c |
| PRETHEORY.md | c9fec13eac40f604323bb296cf54146b9bf16c604fbce444434b12cbcdbae3fb |
| M116C_SOURCE_ONLY_REPORT.md | 1a4d2961ecafd4689aaa41aa83cf6f853b8b4d01b69de0127c426d5fc3737597 |

The contract's three non-runner source hashes exactly match the current worker,
cost-model, and operator bytes. Its normalized runner seal matches the current
runner. The M116c execution-release file and canonical campaign root were
absent before the checks and remain absent afterwards; no M116c *MANIFEST*
file exists.

## Authorization boundary: passed

* campaign_runner exports no EXECUTION_TOKEN.
* run_authorized_generated_campaign has an empty parameter list. A legacy
  token-shaped invocation is a TypeError; the genuine zero-argument call
  raised PermissionError, external execution release is not installed, before
  any canonical-root creation.
* The only source release literal is
  EXPECTED_EXECUTION_RELEASE_SHA256. It is the all-zero 64-hex sentinel, and
  source_bound_execution_release_sha256 reads the same all-zero value from the
  raw runner source rather than trusting a mutable imported global.
* The normalizer replaces exactly one instance of that literal. Replacing its
  64 digits in a temporary source copy left the seal unchanged; injecting a
  second matching literal failed with the required exactly-one error; any
  nonliteral source byte drift fails the contract seal.
* A direct AtomicCampaignLifecycle claim at the actual canonical root and a
  direct worker.run_generated_only_child call at the actual fixed claim path
  independently raised the same no-release PermissionError before mkdir,
  O_EXCL, probes, or child generation. This closes the prior parent-import
  bypass rather than merely hiding it behind the CLI.

The source-only CLI remains a PermissionError. retry_allowed is false in both
the contract and release schema; claims and terminal writes use exclusive,
non-overwriting paths and their interrupted-write tests consume the path.

## Noncyclic release and audit binding: passed

The future release payload is exact-schema-bound to:

* the run ID and protocol identity hash;
* the raw contract SHA-256;
* the normalized runner seal;
* the contracted raw worker/cost-model/operator hashes;
* the canonical runtime-identity hash;
* the fixed canonical run-root path; and
* retry_allowed=false.

The independently recomputed protocol identity hash is
c2fa4f35bacf4b8f37f9755d62b0eb927eb2d7aa09eaa76f5082d6f8bfff1246 and
the runtime-identity hash is
c7ee40a1ea4556b3dfc8617a91dbc176955bd03b9abcb9b4216e9533495214f7.

A release must additionally name a non-symlink M116C_B4096_ audit directly
under the fixed audit root, bind its raw SHA-256, carry verdict PASS_TO_EXECUTE,
and contain the exact PASS_TO_EXECUTE verdict heading in the bound audit bytes.
The verifier rejects foreign schema fields, altered contract/runtime/source
identity, invalid audit identity, absent audit, audit hash mismatch, and missing
PASS heading.

The dependency chain is noncyclic: the contract fixes the normalized runner
seal; that seal hashes every runner byte except the single release-hash
literal; a separately constructed release binds raw contract/source/runtime/
canonical/no-retry/audit identity; only its final SHA-256 is installed in the
excluded literal. Replacing that literal therefore leaves the runner seal—and
the already fixed contract—unchanged.

A two-valid-release synthetic swap test patched the release-file read so that
the file was replaced immediately after the first captured bytes. Verification
returned exactly the first, hash-bound payload. Thus a hash-one/parse-another
swap cannot substitute the second payload: SHA-256 and JSON parsing operate on
the single captured buffer. Temporary release and audit symlinks were both
rejected. A lexical constant override was rejected before its root existed.

For the canonical-root symlink case, I imported a temporary copy of the runner,
made only its temporary canonical root a symlink, and invoked both its path
assertion and lifecycle claim. Both rejected before mkdir and the redirected
target remained absent. This tested the real lexical/symlink control without
touching the real M116c root.

## Preserved B=4096 geometry, accounting, and gates

The repair did not alter the B=4096 operator or contract values:

| Item | Recomputed value |
|---|---:|
| block rows | 4,096 |
| full rows / depth / dtype | 64,512 / 32 / float32 |
| owned workspace | 67,809,280 bytes = 64.66796875 MiB |
| full hook bill | 5,912,804,352 |
| full hook calls | 16 |
| full trace calls | 512 |
| full trace bill, including 32 ReLUs | 189,738,221,568 |

The static contract gates remain micro rows [512, 4096], shallow relative
Frobenius <= 3e-6, depth-32 relative Frobenius <= 2e-5, ReLU mismatch <= 2e-4,
parent/child peak <= 464 MiB, prediction wall < 20 s, and absolute L3 residual
<= 0.170 s. The adverse unmeasured residual prior remains approximately
0.30525655660312625 s and is not presented as a success claim.

An independent bounded 4,096-row FlopScope operator probe (not a campaign)
returned the caller-left object, was finite, preserved the right operand and
unprocessed suffix, and reported one core/matmul call, 376,040,448 billed
FLOPs, and relative Frobenius 1.9649163152480837e-06. The actual 512-call full
lifecycle was not run.

## Verification executed

* Under the contract's pinned one-thread environment,
  python -m unittest test_inplace_l3.py test_campaign_harness.py completed
  **30/30** tests in 0.325 s.
* py_compile passed for campaign_runner.py, campaign_worker.py, cost_model.py,
  inplace_l3.py, and both test modules.
* Independent direct checks covered absent/fake/replaced release behavior,
  zero-argument parent, canonical lifecycle, child, all-zero source sentinel,
  exactly-one-literal normalization, raw/normalized hashes, fixed path
  overrides, temporary release/audit/canonical-root symlinks, and the
  hash-then-swap attack.
* No test called the full campaign entry after a valid release; the temporary
  release fixtures were supplied only to the internal verifier and never
  installed in the M116c source directory.

## M116b preservation

M116b remains the separate consumed B=2048 identity. Every source hash and
every audit-evidence hash listed in its frozen manifest still matches (7/7 and
6/6 respectively). Its three terminal artifacts remain present:

| Artifact | Current SHA-256 |
|---|---|
| M116B_B2048_CLAIM.json | dc28bcccd71822e8760bb2168aac9340bcf4b04bceea48071232077e9c5436b1 |
| M116B_B2048_FAILURE.json | a299f73e8880ae5b52d71d5403b97618aedaed76a988416b4bd4c5e7dc858e3b |
| M116B_B2048_TERMINAL.json | e7fa2cbc9d5b74a4cae1d748c87ddc7ea4857a8cd1095ad8046e10b1f1267fb1 |

No M116b file was edited, deleted, retried, or reused by this audit.

## Freeze handoff

The repaired source is **PASS_TO_FREEZE** as a pre-execution, source-only
candidate. This does not create or approve the later independent external
execution release, replacement of the zero sentinel, campaign launch, or any
result claim. Those remain separate authorities and future gates.

