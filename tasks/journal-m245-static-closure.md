# M245 static closure (Fable baton from Codex /root) — journal

## Goal (frozen — edit only if the user changes scope)
Repair S/O/A against the seven hostile-audit static blockers (apply_patch only; no
imports/compile/tests/science), freeze all six source hashes, obtain two independent
exact-hash static PASS verdicts, then run the four exact serial one-shot dummy GREEN
unittest commands (I1.7) from the authority directory. On all-green: GREEN receipt +
checksum per I1.8, single commit of six sources + two evidence files, concise status
append to AGENT_CHANNEL.md for Codex /root. HOLD on everything real: no shard, census,
trigger, aggregation, provider, fixture decode. Codex /root remains sole shard caller
(Erratum2 E2.4).

## Constraints / decisions (append-only, dated)
- 2026-08-10: Authority dir = corpus/whestbench/experiments/m245_canonical_unordered_replica_galerkin_spectrum
- 2026-08-10: Erratum1 active at commit 76b446c (parent 130391c, docs-only, 2 files). E1.6 permits adopting/editing the six drafts.
- 2026-08-10: Frozen tests (I1.1): P 355820f3…, R e7eceb02…, T 112869bf…, A 6d723cde… — never edit.
- 2026-08-10: Pre-repair source hashes verified == baton (P d0296d5e, R 6ab33386, W 3cce3474, S eb561076, O eb5b794f, A fc04e925).
- 2026-08-10: GREEN = I1.7 four commands, interpreter C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe, cwd = authority dir, serial, -B -m unittest -v, once each, no rerun on any failure (FAIL_IMPLEMENTATION_GREEN_STOP_NO_RERUN).
- 2026-08-10: I1.8 commit = exactly six sources + GREEN receipt + GREEN checksum, nothing else. Channel append is a separate commit.
- 2026-08-10: Do NOT create M245_SCIENTIFIC_STATIC_AUDIT_A/B json now — those belong to the later post-GREEN trigger sequence (I1.9). My two static verdicts are subagent reviews recorded in channel/journal only.
- 2026-08-10: Repairs limited to S/O/A. P/R/W byte-stable unless a blocker forces otherwise (none currently does).

## Done (append-only; each entry names its verification evidence)
- Re-anchor: git log confirms 76b446c=erratum1 (2 files, 165 insertions, parent 130391c); all 10 SHA256 (6 sources + 4 tests) match baton via Get-FileHash. Channel tail read: Codex /root sole caller stands, HOLD stands.
- Authority docs read: AUTHORIZATION (I1.1–I1.9), ERRATUM1 (E1.1–E1.6), ERRATUM2 (E2.1–E2.11) in full.
- Sources read in full: S (3425), O (1657), transport test (2808). P ladder semantics extracted (lines 844–995, 1195–1360: c=chol solve, P=d·c, V=K−P, V_beta=K−2β·d+β^TGβ, identity lhs=V_beta−V rhs=(β−c)^TG(β−c) gap=lhs, tau=2e-10K, solve gate 2e-20, curve classifier is float64 with x=float(P_str)/float(K_str) per W:686).
- Key compatibility facts (evidence: transport test full read): tests never call main/census/verify_committed_trigger/load_and_verify; never pass 3rd arg to validate_invocation_receipt; import check = forbidden-prefix list only; only build_final_shard_receipt_from_files has frozen signature; trigger/authority/source key tuples hardcoded in test → schema extension forbidden; dummy ladder numbers are inconsistent stubs → blocker-7 code must stay production-only (inside _validate_scientific_ledger_bindings).
- A checked: _validate_production_entry (A:2515) already binds GetCommandLineW argv + flags + interpreter + cwd + source hash. A needs no repair. Aggregation test never calls A.main.
- REPAIRS APPLIED (apply_patch only): S ×10 edits, O ×8 edits. Blocker 1: ACTIVATED_AUTHORITY_SHA256 (auth .md/.txt 46ba45dc/e0cd1409, erratum1 .md/.txt 5d089084/7bd73b14, RED-V2 sums 669df011) + FROZEN_SCIENTIFIC_TEST_SHA256 + GREEN receipt/checksum structural lineage, verified live+GO-blob at end of verify_committed_trigger (S) and _independently_verify_trigger (O). Blocker 2: exact audit schema (artifact/audited_source_sha256/reviewer_id/schema/status) + audited map == sources minus 3 self names, both files. Blocker 3: S post-finish _validate_meter_stream + validate_invocation_receipt(receipt,...) removed; _resource_meter_from_raw split into validating wrapper + pure _resource_meter_reductions; O post-finish reindex loop + _validate_meter_stream(outer) + self validate_terminal_witness removed. Blocker 4: preflight global ownership census (owner_by_name, temp refusal, non-regular refusal, artifact-without-intent refusal). Blocker 5: _EXPECTED_PRODUCTION_AUTHORITY_UNION global checked in _validate_authority_union; set in S production + by O on loaded supervisor. Blocker 6: _observed_windows_command_line_argv (GetCommandLineW+CommandLineToArgvW, mirrors A) + sys.orig_argv + flags + executable + cwd binding in S main, S census mode, O main; census payload argv = verified actual orig_argv. Blocker 7: _validate_reported_primary_ladder (exact Fraction pins for c-residual/P/V/V_beta/identity/tolerances/energy bounds + float64 Jacobi eigenrange Weyl-bounded) + _float_classify_curve_ladder port + _validate_reported_curve_report (label from reported gate evidence, fields pinned to recomputation), called at end of _validate_scientific_ledger_bindings.
- Static falsifier after last edit: ast.parse both files OK, stdlib-only imports, zero forbidden prefixes, zero mp.quad owners (venv python heredoc run). Leftover greps clean.
- CRITICAL INSIGHT: frozen tests have NEVER run against any implementation (GREEN is first-ever execution, one-shot). Reviewers must verify the whole dummy contract (all 4 tests vs all 6 sources), not just the delta.

- Pre-freeze fleet results (5 agents): hostile audit = 0 blockers, 2 RISK (O independent layer weaker than S — FIXED with assignments/commit/audit-path/reviewer/census-path pinning in _independently_verify_trigger; witness validators rely on caller pre-validation — documented, frozen signatures forbid change), 2 NOTE (curve port fail-closed divergence, eigen absolute tolerance — accepted). Transport compat = COMPAT_FAIL: frozen test _identity() carries synthetic L/W CPU counters (10000/20000) vs meter finals (12000/8000, 18000/12000); S's unconditional exact-equality check would kill 6 of 23 methods. FIXED: L/W counter equality now production_paths-gated (mirrors O's absolute-path gating); exit_code equality kept unconditional. Verified post-fix full receipt/witness/final trace passes and all 18+ assertRaises mutations still raise. P compat = COMPAT_FAIL ×3, ALL CONFIRMED BY MY OWN EXACT ARITHMETIC (venv python, no m245 imports): (1) precision_gate(1e6, 1e6+2e-6) False at prec53 [repr parse re-rounds to binary64], True at elevated precision — FIXED with mp.extraprec(100) wrapper; (2) ladder_energy_gates monotonicity: bad4-(4-tau) = -1.65e-16 exactly (violation real) but invisible at prec53 subtraction — FIXED with extraprec(100) around comparisons, tau kept ambient so test line 668 assertEqual(tau_K, float tau) still holds (verified mpf('2e-10')*mpf(10)@53 == 2.0e-10*10.0); (3) gaussian_interval_moments finite block: test float reference diverges from truth by up to 1.5e-7 (high-precision fix PROVEN impossible — places=13 fails degrees 10-20 even for exact module); mpmath@prec53 add/sub/mul is bitwise float64, endpoints ±0.75/1.25 give exact powers, pdf seeds already bit-match libm, and mp.erf@53 bit-matches math.erf at both endpoints → FIXED cdf_endpoint to erf spelling; erf-seeded recurrence reproduces float testref BITWISE all 21 degrees (max diff 0.0). _normal_cdf (erfc, tail-safe) unchanged for scientific paths; sole other production call site of moments is _integrate_polynomial_gaussian (line 811), tail-cancellation analysis: no gate impact at 80/100 dps. R compat = COMPAT_PASS (2 runtime-risk notes, favorable). A compat = COMPAT_PASS.
- FROZEN CANDIDATE HASHES (post-fix, ast-parse clean on P/S/O, evidence: venv hashlib run):
  P 4087adad00ede51734f7368738267be05b34c85662572883f14dd96ca6752062
  R 6ab33386ae985942b48b395eba7f78c724a3ad0805744b1ea42f3d31d8ab1326 (unchanged)
  W 3cce3474d1173c0252a8f2c98fc29a4404275cad0d988ace728a6639207e4047 (unchanged)
  S 983e598ce97a56848103efb249b3a249e738a3b32c56c124392de15b17dfe2bf
  O 71abeebac9968d519d9dc2ea14cd760256a86f384fe4d5e6f3f4e7b06f4141bf
  A fc04e9258bb52e5171c54948c5451449e9c96a07a39c9bbab942982371d47c01 (unchanged)
  Tests: 355820f3…/e7eceb02…/112869bf…/6d723cde… all byte-identical to I1.1 (verified same run).

- TWO INDEPENDENT STATIC PASS VERDICTS OBTAINED (evidence: both reviewer reports in-session). Reviewer A (authority-first): all ten hashes recomputed exact; I1.6 points 1-8 PASS with file:line; blockers 1-7 closure PASS with file:line; sharp edges re-derived (extraprec gate arithmetic, tau_K bit-equality, erf@53 == math.erf at ±0.75/1.25 over √2, L/W counter gating + mutation reachability). Reviewer B (test-first): all ten hashes exact; per-method verdicts across all 92 test methods in 4 suites (zero statically-detectable failures; ~22 methods classified bounded numeric-runtime-risk inherent to live quadrature); mechanical AST schema diff across all schema constants = zero drift; legality PASS under I1.4/I1.6, E1.3-E1.6, E2.3-E2.10; no fail-open/exec/eval/shell/import-side-effects. Reviewer B disclosed a transient _tmp_schema_dump.json it created+deleted in the authority dir — must re-verify cleanliness fresh before GREEN.
- GREEN AUTHORIZATION SATISFIED per E1.6: erratum1 active (76b446c), six candidate bytes frozen, I1.6 static gate independently passed twice.

## Next action (exactly ONE — overwrite, never a list)
Fresh pre-GREEN verification (10 hashes + interpreter hash 4b8c3912… + authority-dir census), then run the four I1.7 commands serially once each via a detached driver (no tool-timeout can kill a suite), capturing UTC intervals + exit codes + stdout/stderr for the GREEN receipt. Any nonzero exit = permanent stop, report, no rerun.

## Open questions (things only the user can answer)
(none)
