# M221 frozen static native ledger

This ledger was written before the first 3,968-event target native run.  It
freezes the exact affine bill and allocation predictions obtained from the only
pre-target FlopScope probes, at batch sizes 3 and 9.

- Both probes bill exactly `5,484` FLOPs/event and allocate exactly `3,002`
  bytes/event.
- For the frozen 3,968-event target, the predicted bill is `21,760,512` and the
  predicted charged allocation is `11,911,936` bytes.
- The operation-level components in the adjacent JSON sum exactly to the target
  bill.  No constant intercept was observed.
- A target trace passes the execution gate only if its bill and allocation equal
  these predictions, it has zero fallbacks, its raw timed wall is strictly below
  `0.016133916999970098 s`, its hostile component is at most `6,824,272,176`,
  and its peak RSS is at most `536,870,912` bytes.
- The independent numerical gate remains separately binding.  Variance remains
  unauthorized unless both the numerical and execution gates pass.
