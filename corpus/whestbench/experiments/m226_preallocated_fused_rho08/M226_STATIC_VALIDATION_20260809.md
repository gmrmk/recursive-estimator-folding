# M226 static validation

Sealed before the first 3,968-event target trace.

The initial TDD implementation exposed one accounting-shape defect: the
two-sign Simpson output was supplied by a one-sign broadcast operand, so
FlopScope correctly billed 5,401 instead of the frozen 5,467 FLOPs/event.  The
mathematics was already correct.  The implementation was repaired by hoisting a
two-sign constant broadcast view in setup, matching the predeclared operand
topology.  The frozen ledger was not edited and no dummy arithmetic was added.

Both required pre-target probes now match exactly:

- size 3: 16,401 FLOPs, 6,438 setup bytes, 171 calls;
- size 9: 49,203 FLOPs, 19,314 setup bytes, 171 calls;
- zero `empty`, `copyto`, `sum`, `max`, or `reshape` runtime calls;
- zero fallback; and
- maximum M224 parity error `4.092863201132779e-18`.

The target prediction remains 21,693,056 FLOPs and 8,515,328 persistent setup
bytes.  Target timing is now authorized; variance is not.
