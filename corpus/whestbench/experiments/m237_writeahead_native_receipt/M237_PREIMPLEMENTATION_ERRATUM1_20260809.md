# M237 preimplementation erratum 1 -- Windows no-overwrite atomic publication

Date: 2026-08-09. Sealed after independent review and before every M237 code,
test, launch intent, worker invocation, or result. It supplements the frozen
predeclaration and manifest without changing the candidate or native gates.

```text
predeclaration SHA256
02934C3A34D9EF9F80CE9FCAC27A9F179A96FB200493E6BC01661765F1FBCBE8

manifest SHA256
9E68B52AF4CBA5B8AE0B93388029637A347045BE0A5D16B69ED004A4A0DE577D
```

## Exact publication primitive

`os.replace`, rename-with-replacement, truncate, and ordinary write-open on
the final result path are forbidden. M237 uses a same-volume NTFS hard-link
publication transaction with create-if-absent semantics.

Before launch intent or worker start, the runner performs one bounded
capability probe in the M237 directory:

1. require fixed probe-temp and probe-final paths absent;
2. create probe-temp with mode `xb`;
3. write frozen probe bytes, flush, and `os.fsync` the open file;
4. call `os.link(probe_temp, probe_final)` with both paths on the same volume;
5. require the link call succeeds only because probe-final did not exist;
6. reopen probe-final, verify exact bytes, then remove both probe names; and
7. require both probe paths absent before continuing.

Any unsupported link primitive, pre-existing probe path, write/flush/fsync,
link, reopen, verification, or cleanup failure kills fixed M237 before launch
intent and before a worker exists.

The real result transaction uses fixed same-directory paths:

```text
.M237_NATIVE_ONE_PROCESS_RESULT_20260809.json.tmp
M237_NATIVE_ONE_PROCESS_RESULT_20260809.json
```

Both must be absent at preflight and immediately before the transaction. The
runner creates the temporary path with mode `xb`, writes the complete
canonical UTF-8 JSON plus one terminal newline, flushes, and fsyncs. While the
temporary file is closed and the official scratch directory is still live,
the runner publishes with exactly:

```text
os.link(result_temp, result_final)
```

On Windows/NTFS this creates the final directory entry atomically and fails if
the final name already exists; it cannot overwrite an existing result. The
runner then reopens the final path, verifies byte identity with the temporary
path, parses the JSON, computes SHA256, and only after those checks removes the
temporary name. Root independently repeats final reopen/parse/hash and
requires the temporary path absent.

Any `FileExistsError`, link ambiguity, cross-volume path, different device
identity, missing final, byte mismatch, parse/hash failure, or temporary-path
cleanup failure is a binding M237 transport failure. If it occurs after the
launch intent, no second worker is permitted.

Static tests must monkeypatch a pre-existing final path and prove publication
refuses without altering its bytes. They must also prove pass and failure
payloads use the identical publication function. Test paths must be isolated
temporary paths and may not use or create either frozen execution artifact.
