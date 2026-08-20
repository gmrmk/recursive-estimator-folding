# M221 frozen native addendum

Written before the FlopScope sidecar or native runner exists.  This fills the
predeclaration's generated-issuer seed rule without changing any chart,
threshold, panel count, or gate.

- The 31 local width-7 contexts use seeds `221730001..221730031`, one per
  ordered block.
- For native seed `s`, Philox/NumPy's frozen default generator draws 128 outer
  normals per block and cycles through that block's canonical strict physical
  owners in lexicographic order.
- The resulting 3,968-row packed object is generated outside the timed region,
  exactly like M216's inherited archived local context.  Inside the timed
  BudgetContext all 18 runtime scalar columns are newly allocated and copied
  with charged `copyto`; every workspace array is also newly allocated there.
- Compile-time Simpson fractions/weights and Taylor coefficients are constants.
- A fallback row remains a native failure.  The seed rule is not changed if a
  context leaves the frozen chart.
