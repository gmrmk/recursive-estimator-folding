# M116C B=4096 execution authorization audit — 2026-08-07

## Verdict: PASS_TO_EXECUTE

This is the separately source-bound authorization audit required by the M116c
release verifier. It authorizes **one and only one** generated-only B=4096
campaign invocation, and only after all of the following separate actions
complete:

1. Root installs the exact fixed release artifact at
   m116c_inplace_l3_b4096_draft/M116C_B4096_EXECUTION_RELEASE.json.
2. Root patches **only** the 64 hexadecimal digits in the sole excluded
   EXPECTED_EXECUTION_RELEASE_SHA256 source literal with that artifact's exact
   SHA-256. No other runner, contract, worker, operator, test, or audit byte
   may change.
3. A different agent independently verifies the installed artifact, its
   SHA-256, exact schema/payload, bound audit bytes and verdict, pinned
   runtime, source identities, fixed paths, and continued no-retry state
   before invoking the zero-argument entry point.

This is authorization for exactly the canonical one-shot
M116C_B4096_GENERATED_20260807 generated-only campaign. It creates no
submission, upload, public-target, scorer, champion, model-replacement, or
retry authority. It does not claim that the future numerical, wall, residual,
peak, or gate outcome will pass.

## Bound predecessor audit

The immediately preceding independent pre-execution audit is required evidence:

| Artifact | SHA-256 | Verdict |
|---|---|---|
| M116C_SECOND_INDEPENDENT_PREEXEC_AUDIT_20260807.md | 4036a2edfe906676a015967ff81b8f40f18257e92efbaa27150d0799b1930a0b | PASS_TO_FREEZE |

I re-hashed that exact current byte stream under the pinned environment. It
matches the required value above. The release must bind this authorization
audit's own final raw SHA-256 and this exact PASS_TO_EXECUTE verdict using the
following audit record:

    {
      "filename": "M116C_B4096_EXECUTION_AUTHORIZATION_AUDIT_20260807.md",
      "sha256": "<SHA-256 of this exact audit byte stream>",
      "verdict": "PASS_TO_EXECUTE"
    }

The filename has the required M116C_B4096_ prefix and is directly under the
fixed research_excursions directory. A release verifier must reject a
symlinked, escaped, unreadable, hash-mismatched, or non-PASS audit.

## Recomputed source, contract, and runtime identity

| Identity | SHA-256 / value |
|---|---|
| raw campaign contract | f289cd0ca1e81273cd45398e3b6d827d946197db989a8db638318665ede09ebf |
| raw runner | 6eecbfbe5c5c45dc5596d4946d2bbb78ef71466cdba6fde84e70118b4fad8333 |
| normalized runner seal | 66bbda5c7d5fe69551dc897e730e3ee4fc3e2dd677d314888387a27181737c2c |
| worker | bdc6d2a6666c65a370d68f43a743458e8a811ac8cd0ec57a3a3f7704571e6d56 |
| cost model | ee1d0dc3f9f15239cc7561c6437545c5c316f8148d9b70060217488428c6a2e3 |
| in-place L3 operator | 114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83 |
| protocol identity | c2fa4f35bacf4b8f37f9755d62b0eb927eb2d7aa09eaa76f5082d6f8bfff1246 |
| runtime identity | c7ee40a1ea4556b3dfc8617a91dbc176955bd03b9abcb9b4216e9533495214f7 |

The source inventory is exactly campaign_worker.py, cost_model.py, and
inplace_l3.py. The normalized seal is source-derived and excludes exactly the
one release-hash literal. The source has one such literal, currently the
all-zero unreleased sentinel:

    0000000000000000000000000000000000000000000000000000000000000000

There is no EXECUTION_TOKEN, and
run_authorized_generated_campaign has a zero-argument signature.

The recomputed pinned runtime is Python 3.14.4 at the contract path with
SHA-256 4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262;
NumPy 2.4.6, its pinned init hash
65d5e777b6d662ba19cb80800bef3eb999eda7aee51eea62c308feabf679dba4, and
build fingerprint fb5905933699a015e02a1e6254a9fc5aadc4a81f4ed03878632d09370684d1e0;
and FlopScope 0.10.0+np2.4.6 with init hash
f49c7b804649223c077505a3380a6fb2baa691e783564be433543fa0ae6f1b06.
OPENBLAS_NUM_THREADS, OMP_NUM_THREADS, MKL_NUM_THREADS, and
NUMEXPR_NUM_THREADS were each pinned to "1".

## Exact future release payload

The source recomputed expected_execution_release_payload to the following
canonical JSON object. The future artifact must carry exactly these fields and
values, plus only the authorization_audit record above:

    {
      "canonical_run_root": "C:\\Users\\strid\\Documents\\Codex\\2026-08-02\\https-chatgpt-com-share-6a5556ed-2e1c\\work\\scorefloor_generation\\m116c_inplace_l3_b4096_draft\\M116C_B4096_GENERATED_CAMPAIGN",
      "contract_sha256": "f289cd0ca1e81273cd45398e3b6d827d946197db989a8db638318665ede09ebf",
      "protocol_identity_sha256": "c2fa4f35bacf4b8f37f9755d62b0eb927eb2d7aa09eaa76f5082d6f8bfff1246",
      "retry_allowed": false,
      "run_id": "M116C_B4096_GENERATED_20260807",
      "runner_normalized_sha256": "66bbda5c7d5fe69551dc897e730e3ee4fc3e2dd677d314888387a27181737c2c",
      "runtime_identity_sha256": "c7ee40a1ea4556b3dfc8617a91dbc176955bd03b9abcb9b4216e9533495214f7",
      "schema": 1,
      "source_hashes": {
        "campaign_worker.py": "bdc6d2a6666c65a370d68f43a743458e8a811ac8cd0ec57a3a3f7704571e6d56",
        "cost_model.py": "ee1d0dc3f9f15239cc7561c6437545c5c316f8148d9b70060217488428c6a2e3",
        "inplace_l3.py": "114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83"
      },
      "status": "INDEPENDENT_EXECUTION_RELEASE"
    }

The dependency graph is noncyclic: the raw contract fixes the normalized
runner seal; the seal fixes all runner bytes except this one release-hash
literal; the release binds raw contract, source, runtime, protocol, canonical
root, no-retry, and audit identity; then and only then its SHA-256 replaces the
excluded literal. The release verifier hashes and parses the same captured
release bytes, so a hash-one/parse-another swap cannot alter the verified
payload.

## Last pre-release verification

Under the pinned runtime and one-thread environment:

* runner.load_contract, source identity, runtime identity, protocol identity,
  and expected payload recomputation all passed.
* The zero sentinel remained installed; the release file and canonical root
  were both absent before and after checking.
* python -m unittest test_inplace_l3.py test_campaign_harness.py passed
  **30/30** tests in 0.306 seconds.
* The contract remains B=4096, full rows 64,512, depth 32, owned workspace
  67,809,280 bytes, full hook 5,912,804,352 billed FLOPs/16 calls, and full
  trace 189,738,221,568 billed FLOPs/512 calls.
* M116b remains a separate consumed identity; this audit neither changes nor
  reuses it.

Any source, runtime, path, release, audit, or root-state drift invalidates this
authorization and requires a new independent audit rather than a retry.

