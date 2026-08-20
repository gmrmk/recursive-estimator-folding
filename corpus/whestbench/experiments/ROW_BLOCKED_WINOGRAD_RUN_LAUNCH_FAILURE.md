# Localized scorer-launch failure 1

The first invocation of the frozen `run_official.py` harness was wrapped in a
tool command with a 10-second outer timeout.  The wrapper terminated the
harness before WHest produced any JSON: both output and stderr files were zero
bytes, the metadata still said `running`, and no process remained.  No score
was observed and no estimator source byte changed.

This was not a candidate timeout, a WHest per-network timeout, or a Gate-B
result.  It was a local orchestration timeout inconsistent with the harness's
expected multi-minute duration.  The corrected invocation changed only the
outer tool timeout and ran the same hash-frozen harness and candidate.  It
completed once, returned zero, and its source-before/source-after hashes are
identical.  The failed invocation is retained as infrastructure evidence.
