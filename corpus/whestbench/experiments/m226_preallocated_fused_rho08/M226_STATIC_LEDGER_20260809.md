# M226 frozen execution ledger

This ledger was written before M226 code, tests, or FlopScope probes.  It is a
prediction, not an observation.

- Persistent setup: two `empty` calls, `268N` float64 plus `2N` boolean
  elements, exactly `2,146N` bytes.
- Timed invocation: 171 calls, exactly `5,467N` billed FLOPs, zero runtime user
  allocation, and zero `empty`, `copyto`, `sum`, `max`, or `reshape` calls.
- Target at `N=3,968`: setup `8,515,328` bytes and timed bill `21,693,056`.
- The target gate remains raw wall strictly below
  `0.016133916999970098 s`, zero fallback/parity failures, hostile component at
  most `6,824,272,176`, and RSS at most 512 MiB in all five fresh processes.

Size-3 and size-9 generated probes must reproduce the affine ledger before the
first target run.  Any mismatch kills the frozen topology instead of changing
this file.
