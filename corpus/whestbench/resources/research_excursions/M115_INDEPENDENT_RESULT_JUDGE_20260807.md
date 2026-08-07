# M115 independent result judge

Date: 2026-08-07  
Verdict: **CONFIRMED -- KILL_M115_REPAIRED_IMPLEMENTATION_NO_RETRY**.

This independent audit was read-only. It did not invoke the runner, generate a
candidate, retry the one-shot, access official/public/contest data, mutate a
champion, or submit anything.

## Terminal state and immutable lineage

The canonical root is consumed by one success-terminal run:

| field | verified value |
|---|---|
| run ID | m115-repaired-generated-only-115001-115004-v1 |
| claim status/time | permanent_m115_run_claim_consumed; 2026-08-07T12:56:06.242546+00:00 |
| result status | completed_generated_only_m115_repaired_one_shot |
| terminal status/time | terminal_success_m115_one_shot_consumed; 2026-08-07T12:56:24.951669+00:00 |
| manifest SHA-256 | 13744c7f023294fb17805e84ceeb8653dacecf1371b43d3e574d0786b26eac89 |
| calibration SHA-256 | 82e927d8a54f2a61fcfe48e542a624038b3ba0cb50f2dde592be28f21d21ebb1 |
| pinned runtime identity SHA-256 | 47a2d09283acdbc3465f9539b8fef44638b2a28e6179768d2290da5feea19202 |
| retry state | false in claim/terminal ledger; parameter retry and champion mutation are false |

The claim records claim_precedes_future_weight_generation=true. Its run ID,
canonical path, manifest/calibration hashes, and runtime-identity hash match
the terminal ledger. The root contains exactly the claim, raw NPZ, phase
events, result, terminal ledger, and four file-backed first-preactivation
banks. No durable-failure artifact or extra data artifact exists.

| artifact | bytes | independently computed SHA-256 |
|---|---:|---|
| M115_PERMANENT_RUN_CLAIM.json | 718 | a6bb8a5d51455144caf82f3705656d4d43f5b3701f901883d77c18383d87ee45 |
| M115_PHASE_EVENTS.json | 868 | 3b594ff0eed2d554ae8212db0763a8ccc3d5d33e4d98e32ae82774ca06549b3a |
| M115_RESULT.json | 343,943 | 8680a76dd696761c3fb008be439408da89fafa34a26250046bcd0b080b6ba6a2 |
| M115_TERMINAL_LEDGER.json | 2,045 | 39efe564277a6b5a20fc67bd36ba43e6fb307ae5dcb5d9aae463e07c4f703918 |
| m115_generated_only_evidence.npz | 1,025,434 | 4f643a115216cb53cef7bfeaa409db42ed68f0ca0e85091dcef4d0a36e7849bd |
| bank/network_0_first_pre_float64.npy | 26,214,528 | 7ac8b6afa776f94ffc427e4481623945f33503487330e055f8cb279a75ebe1fa |
| bank/network_1_first_pre_float64.npy | 26,214,528 | 86cc8765ffe16923a4b8ec3dd98ab3db448d64f8fcaaa5281e264427f7d81bff |
| bank/network_2_first_pre_float64.npy | 26,214,528 | 2d736187114b6406598566c3dea207a57e968b82d0393b23bf0c9aaa8ae086bd |
| bank/network_3_first_pre_float64.npy | 26,214,528 | a416a37feb80d98cab7539040294bc8c064ea04a12d8f538b08065a7a8de529e |

The terminal ledger's eight non-self artifact entries match direct hashes and
byte sizes. Its non-recursive self hash is independently checked above.

## Frozen input chain and firewall

Under the pinned Python 3.12.13 / NumPy 2.3.5 one-thread runtime, I invoked
only _config_guards(), _verify_runtime(), and
_verify_external_manifest(runtime). These read-only checks accepted the exact
nine-file source surface, manifest, calibration, all 14 closed-operation
evidence files, protocol, and data firewall. No screen function was called.

The manifest-referenced audits also match:

| audit | SHA-256 |
|---|---|
| pre-execution | 2b7eecf2b42c4f3f338ea3d3ccf5ecc6380f0ba9ee77e06b600def8e855334d6 |
| cost calibration | b915142b2f5ef9a2f481005dd35b98f0d72acdc69a941bde7c0bd945399227cb |

All 14 calibration-evidence hashes were independently rechecked:

~~~
base_0.json              9deec66dbc7b29afecc7678d3cd1fc39e06742f2e427f756f9f40aec0fa15696
base_1.json              dd406537147b9e5ab1d13ceb13f5177b56d9f63a7e09c115c0cc415f150aaa02
base_2.json              93b9fcf3f89ecad233d2ab9046a17de3c3c53f94cfe174f9baa957d9806d6499
base_3.json              8606f3d46416398010a3e6901ae21dc3d881720c05ca7b31055d7f428dee59ca
candidate_0.json         1c5977d356024d46ee8a6b3cd0ac2ff38932e68db0b12cb545fea2f9230b303d
candidate_1.json         2674fbb9493ebe350246ef34e2c6dde172eac16deca5cecc60fbe8c9c2f4bd0f
candidate_2.json         cf189481414a88eee2aeebe0a3f85cf33b4f5e203f55a7994f4a5a5646c6dd84
candidate_3.json         1b86b90e7edbce526be536d5b29de89a0f00c7048b0b0b65b5ac45e29e21bfad
equal_0.json             8a9db11c4143a3d3fc854f4960b626178475e9d04a4a731f4e96c26aa1f7e1b0
equal_1.json             10415f87d4ef968aedb6eb190bee2d77cb7fac5096b1d4feddd63e7fcf3f54fe
equal_2.json             69c0992205969328624016aa3fe142a22fc763c9bcf50a9ab6f1bcd63090a60a
equal_3.json             d5ab8ecee94d9ea3a2e87baed7c3485697ce47627dc433ac499f91f1125c6ec6
failure_lifecycle.json   70481c9f090ccdd52b84804e1fe2d4d1907e547a8f49ad8bb6264bfd86d4dc7a
success_lifecycle.json   898f5b2cfa3615c2c965af5e266236f88b76044efd85b1547f9c498a4650e0bc
~~~

The static validator rejects a free charged_cost_multiplier in manifest or
calibration. It recomputed rho = 2.994438216430221 from hashed closed
operation ledgers, not a manifest-supplied concession.

The phase ledger has the exact 13-event order: precheck complete for networks
0--3, the all-four-prechecks barrier, then evaluator start/complete pairs for
0--3. The result records fresh generated He networks only and
contest_or_champion_accesses=0. The sealed source/manifest prohibit contest
instances, truth, leaderboard/scorer, champion access, network calls,
submission, and champion replacement. No official/public/contest datum or
champion mutation is evidenced or authorized.

## Direct NPZ recomputation, not result-JSON trust

I loaded only m115_generated_only_evidence.npz with allow_pickle=False. Its
finite float64 arrays are frame_outputs (4,50,256),
crossfit_residuals (4,50,256), frame_controls (4,50,128), and two stored
four-value covariance arrays. For each network I recomputed:

~~~
T(X) = sum((X - mean_frame(X))^2) / (50 - 1)
raw_i = T(crossfit_residuals_i) / T(frame_outputs_i)
charged_i = rho * raw_i
~~~

| network | base T | corrected T | raw ratio | charged ratio |
|---:|---:|---:|---:|---:|
| 0 | 0.012579130614428080 | 0.018380688606794062 | 1.4612050045582385 | 4.375488107688285 |
| 1 | 0.011727116144596953 | 0.017956308618748428 | 1.5311785435860510 | 4.585019547092038 |
| 2 | 0.013775041518444418 | 0.020052051317378694 | 1.4556799186797025 | 4.358943579384538 |
| 3 | 0.010409401364693056 | 0.019330917392728596 | 1.8570633137747792 | 5.560861357097745 |

The stored covariance vectors equal the direct values exactly. Independently
enumerating all 4^4 = 256 ordered bootstrap draws, with frozen rho, gives:

~~~
charged geometric ratio                  4.695942317301860
charged pooled ratio                     4.6759235931211744
q90 order statistic                      zero index 230 (231st sorted value)
charged exact bootstrap q90              4.976822658533446
~~~

This is a deterministic enumeration of the four saved frozen-seed carriers,
not a Monte Carlo rerun. These NPZ-derived calculations agree with the result
JSON only as a post-hoc consistency check.

Every raw ratio is at least one, and the geometric, pooled, and bootstrap-q90
charged ratios all exceed the strict 0.90 gates. Every frozen kill reason
therefore applies, so the terminal KILL is correct and no retry is permitted.

## Exact-zero theorem is not this numerical carrier

Conditional on fixed first-layer axes and landmarks, each antipodally
symmetrized projective control psi_l(U) = (phi_l(U) + phi_l(-U))/2 has exact
spherical mean zero. That is an expectation identity; it does not assert that
this finite pseudo-random, cross-fitted four-network carrier must reduce trace
covariance. This carrier increased it on all four networks. The outcome
therefore confirms the prescribed implementation-specific KILL without
refuting the exact-zero theorem.

