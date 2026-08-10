# M239 prelaunch erratum -- publish every post-intent failure

Date: 2026-08-09. Status: `SEALED_BEFORE_FIRST_AND_ONLY_LAUNCH`.

After the launch intent is durable, every execution, timeout, OS-launch,
postflight-hash, parsing, or other ordinary exception must still produce one
canonical result payload. The payload records the failing phase, exception
type/message, partial stdout/stderr, timeout and return-code state, available
postflight hashes, and parent stability. A parent mutation is a durable failed
result, not an uncaught exception.

If final no-overwrite hard-link publication itself fails, the runner must not
relaunch. M237's already-fsynced same-directory temporary payload is preserved;
the runner reports the publication exception and whether the temporary/final
paths exist. This is the sole permitted case in which the final result name is
absent after intent.

No M238 artifact, command, test list, threshold, timeout, or authorization is
changed by this erratum.

