# WhestBench native-kernel rules and runner audit

Research date: 2026-08-03

Scope: official challenge rules, official AIcrowd challenge material, and official `AIcrowd/whestbench` / `AIcrowd/flopscope` source. This audit answers whether a submission may ship and launch native binaries or shared libraries, what is actually packaged, and how non-FlopScope execution is charged. It does not implement or benchmark a native kernel.

## Bottom line

Under the currently rendered official Rules v12, a native CPU implementation is legally in bounds in principle. Section 5.2 explicitly says a submission may call “any other library, numerical backend, programming language, executable, or saved file,” and section 5.6 says participants may bundle “additional Python dependencies or precompiled artifacts.” The submission must remain importable as the required Python package and must obey the security, reproducibility, network, and compute-accounting rules.

Calling a participant-supplied shared library or executable during `predict()` does **not** make its work free. The canonical charge is

`C = F + lambda * R`, with `lambda = 1e11 FLOP/s`,

where `F` is analytically counted FlopScope work and `R` is residual wall time outside FlopScope dispatch. A synchronous custom native call made by the estimator is outside FlopScope dispatch, so its elapsed time is residual and consumes the same budget. If `C > B`, the grader substitutes the zero prediction. Valid entries receive multiplier `max(0.1, C / B)`; failures receive multiplier 1.

The public packager can technically ship ordinary `.so` files and native executables in directory mode because it includes regular files without an extension whitelist. However, the public sources do not disclose the production CPU model, CPU architecture/ISA, Linux distribution, glibc/libstdc++ ABI, dynamic-loader configuration, executable mount policy, seccomp/syscall policy, or thread affinity. Therefore the rules authorize native artifacts, but the exact portable compilation target cannot be proven from public material. Linux is documented in the official estimator-contract documentation; architecture and ABI are not.

## Exact legal boundary

Official current rules:

- Rules page: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/challenge_rules
- The rendered page identifies the document as Rules v12.
- Section 5.2: the entry is `estimator.py` under the current canonical starter-kit contract, and the Rules control conflicts.
- Section 5.2 expressly permits calling another library, numerical backend, programming language, executable, or saved file.
- Section 5.2 requires the artifact to be importable as a Python package and pass the current validator.
- Section 5.2 prohibits reading private data or grader state, changing FlopScope parameters, otherwise circumventing section 5.5 budget enforcement, relying on network access, and tampering with the grader. The passed MLP is the only legitimate per-instance input.
- Section 5.3 permits the sponsor to patch FlopScope, scoring, timing, per-MLP budget conversion, and security/accounting gaps, and to regrade affected entries consistently. In Phase 2 these changes are limited to material scoring, accounting, security, or operational fixes.
- Section 5.5 says effective cost combines analytically counted FLOPs and residual wall-clock time outside FlopScope at an unfavorable conversion rate. It explicitly says non-FlopScope code is permitted but its off-FlopScope computation is charged. Budget exceptions, malformed/non-finite output, memory failure, or wall-guard failure produce the zero-prediction fallback. Evaluation uses a fixed seed.
- Section 5.6 specifies 16 vCPUs, 64 GB RAM, a hard 60-second wall-clock cap per MLP, no network, CPU-only execution, Python 3.10+, FlopScope, WhestBench, and small standard utilities. SciPy, scikit-learn, JAX, PyTorch, Numba, and Cython are not preinstalled. It allows bundled additional Python dependencies or precompiled artifacts, while reiterating residual-time billing.

Official challenge page:

- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026
- The challenge description likewise states that FlopScope operations are analytically charged, while plain NumPy/Python-scalar/uninstrumented-library work is residual-time charged; the environment is standardized, isolated, CPU-only, dependency-pinned, and offline; artifacts must be in the tarball; and FlopScope tampering/private-state access is forbidden.

Important practical interpretation:

- **Permitted:** load a bundled model, table, shared library, or executable; use it as part of the estimator; accept the resulting residual-time charge; remain inside the memory, wall-time, and effective-compute budget.
- **Not permitted:** move numerical estimator work into `setup()` or another unmetered-looking path with the purpose/effect of evading section 5.5, hide work from the timing mechanism, alter FlopScope or the grader, use external services, or inspect private grader state.
- The official docs say artifact loading in `setup()` is zero FLOPs. That is a loading/initialization allowance, not authorization to perform the estimator’s hidden numerical computation outside `predict()`.

## Packaging and dependency facts

Official repository: https://github.com/AIcrowd/whestbench

### Limits

Source: https://github.com/AIcrowd/whestbench/blob/main/src/whestbench/limits.py

- `MAX_SUBMISSION_BYTES = 50 * 1024 * 1024`: 50 MiB total raw size of bundled files.
- `MAX_SUBMISSION_FILES = 50`: 50 bundled files.
- The limits module is used by both packaging and evaluation guards.

### Packager

Source: https://github.com/AIcrowd/whestbench/blob/main/src/whestbench/packaging.py

- Single-file mode packages only the chosen file as `estimator.py`; it cannot by itself carry a sibling native artifact.
- Directory mode requires `estimator.py` and recursively collects regular files except built-in ignores, secret patterns, and `.whestignore` matches.
- There is no file-extension whitelist. A regular `.so`, `.dll`, or executable is therefore not rejected merely for its extension.
- Symlinks and non-regular filesystem objects are skipped.
- Built-in ignores include VCS/virtual-environment/cache content, Python bytecode, the submission manifest, and archive extensions such as `.tar.gz`, `.tgz`, and `.zip`.
- Each bundled file is hashed in the generated manifest; the archive is a gzip tar containing those files plus the generated manifest.
- The packager validates that `estimator.py` imports and exposes the required estimator/`predict(mlp, budget)` contract before creating the package.
- `tarfile.add` normally records Unix mode metadata, but the public production extractor is not available, so preservation of an executable bit in the actual grading pipeline is not established by public source alone.

### Validator

Source: https://github.com/AIcrowd/whestbench/blob/main/src/whestbench/validation.py

- Validates the manifest schema and entrypoint, checks that declared members are regular files, and verifies SHA-256 hashes.
- Rejects symlinks and special files.
- Does not ban binary file types or executable modes.
- The source notes that the local validator is stricter than a tolerant private grader and references a private `whestbench-evaluator/worker/ingestion.py`; that production ingestion source is not public. Thus public local validation is useful evidence, but not a full audit of production extraction or syscall policy.

### Loading and vendoring

Sources:

- https://github.com/AIcrowd/whestbench/blob/main/src/whestbench/loader.py
- https://github.com/AIcrowd/whestbench/blob/main/src/whestbench/sdk.py
- https://github.com/AIcrowd/whestbench/blob/main/docs/how-to/ship-weights.md
- https://github.com/AIcrowd/whestbench/blob/main/docs/reference/cli-reference.md

Findings:

- The extracted submission directory is placed on `sys.path` before `estimator.py` is imported. Sibling pure-Python modules and packages can therefore be vendored if they are self-contained and fit the caps.
- `SetupContext.submission_dir` exposes the read-only extracted submission directory, allowing bundled data/artifacts to be located.
- Folder packaging is the documented way to ship helper modules, data, and subpackages.
- A bundled `requirements.txt` is not installed. The deprecated requirements option has no grading effect. “Not preinstalled” / “no requirements installation” does not contradict Rules v12’s permission to bundle dependencies: it means the submission must carry a self-contained vendored dependency or precompiled artifact rather than expecting `pip` to run.
- The official shipping guide says loading bundled artifacts during `setup()` has zero analytical FLOPs.
- A native shared library must either bundle its needed non-system libraries within the 50-file/50-MiB cap or rely on system libraries that happen to exist. The public materials do not publish the guaranteed system-library set or dynamic-loader/RPATH policy.

## Runner, failure, and residual-time behavior

Official sources:

- Estimator contract: https://github.com/AIcrowd/whestbench/blob/main/docs/reference/estimator-contract.md
- Runner: https://github.com/AIcrowd/whestbench/blob/main/src/whestbench/runner.py
- Worker: https://github.com/AIcrowd/whestbench/blob/main/src/whestbench/subprocess_worker.py
- Budget: https://github.com/AIcrowd/whestbench/blob/main/src/whestbench/budget.py
- Scoring: https://github.com/AIcrowd/whestbench/blob/main/src/whestbench/scoring.py
- FlopScope timing decomposition: https://github.com/AIcrowd/flopscope/blob/main/flopscope-client/src/flopscope/_budget.py

Findings:

- The public runner launches the participant worker as a Python subprocess and exchanges JSON messages over pipes.
- In the worker, the memory resource limit is set before participant code is imported. `setup()` is called before predictions. Only `predict()` is wrapped in the FlopScope `BudgetContext`.
- The official estimator-contract documentation says the grader uses a Linux subprocess, defaults to a 64-GB address-space cap, and treats hard kills, segmentation faults, and timeouts as failures producing the zero fallback.
- The public runner’s default setup response timeout is 5 seconds. The rules’ 60-second hard wall cap is stated per MLP. These details should not be used to justify numerical work in setup.
- FlopScope decomposes timing into backend time, overhead, and residual time. Backend time is the pure server NumPy kernel. Dispatch/wire/server-marshalling overhead is excluded. Residual is participant wall time outside FlopScope dispatch and is billed in `C = F + lambda * R`.
- Therefore a synchronous native child process or shared-library kernel invoked directly by `predict()` is residual work. If the call takes `t` seconds, it adds approximately `1e11 * t` to effective cost, independent of whatever analytical FLOPs the native code would have contained.
- Because residual accounting is elapsed wall time rather than summed CPU-seconds, parallel native work across available vCPUs can reduce residual wall time. That is an inference from the published formula and timing source, not a published promise about affinity, thread count, CPU architecture, or reproducible scaling. It remains subject to ordinary budget enforcement and the sponsor’s patch/regrade power; any deliberate accounting evasion is prohibited.
- Combined budget exhaustion is checked with strict `C > B`; equality is accepted. A valid prediction’s compute multiplier is `max(0.1, C / B)`. Invalid/failing predictions use the zero fallback and multiplier 1.

## Environment facts that are not public

The reviewed primary sources do not specify:

- CPU vendor/model or supported ISA extensions (for example AVX2/AVX-512)
- machine architecture (for example `x86_64` versus `aarch64`)
- Linux distribution, kernel, glibc, libstdc++, or other ABI versions
- whether executable mounts, `execve`, `fork`, or general child-process launches are restricted in production
- seccomp/AppArmor/container syscall policy
- dynamic loader search paths, RPATH treatment, or guaranteed shared system libraries
- thread affinity, SMT topology, or whether all 16 vCPUs are simultaneously available to participant native threads
- preservation of Unix executable permission bits by the production extractor

The Rules explicitly authorize an executable/precompiled artifact, and the public local worker does not contain an explicit participant subprocess/import denylist. Neither fact proves every production syscall or ABI detail. A robust implementation phase should obtain an organizer statement for the target ABI/ISA or validate a conservative, self-contained build through the official submission system. Until then, architecture-neutral Python plus a carefully selected fallback is safer than assuming a specific native target.

## Official organizer clarifications

- “How to use pytorch in this challenge”: https://discourse.aicrowd.com/t/how-to-use-pytorch-in-this-challenge/18040 — organizer response says PyTorch/NumPy/SciPy are not available and a shipped `requirements.txt` is not installed; the sandbox supplies FlopScope, WhestBench, and the standard library.
- “Memory usage limit”: https://discourse.aicrowd.com/t/memory-usage-limit/18039 — organizer clarification states a 4-GiB per-array remote limit and a live-array-count limit of ten million. These are separate from the 64-GB process-level cap in the rules/docs.

## Decision

**Legally viable:** yes, provided native execution is ordinary declared computation and all off-FlopScope time is accepted as residual cost.

**Technically packageable:** yes in directory mode as ordinary regular files, within 50 files and 50 MiB, with no runtime dependency installation.

**Technically portable on public evidence alone:** not yet established. The required Linux ABI, architecture/ISA, loader behavior, and production executable policy are under-specified. Native-kernel implementation should wait for one of: an official organizer ABI declaration, an official matching container, or a submission-system validation experiment.
