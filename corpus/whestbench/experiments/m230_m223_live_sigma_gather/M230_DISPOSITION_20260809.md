# M230 disposition: seam prototype integration-blocked

M230 is blocked before value or timing work. The required source operand does
not exist in current M223: a generated live `LayerPrecontext` exposes only
`a`, `C`, `layer`, `epoch`, and provenance; it does not retain or expose a
float64 `marginal_sigma_vector` equal to `sqrt(C_ii)`.

The preflight refuses all candidate vectors at this absent-provider seam,
including copies, wrong-epoch candidates, and conditional-sigma substitutes.
This is intentional: constructing `sqrt(diag(C))` in M230 would be a new,
unpaid source computation and would not demonstrate reuse of M223/M179's live
diagonal cache.

No inclusive gather, source evaluation, target trace, six-process wall gate,
or reuse-credit claim was run. M224 and M228 remain unchanged. A future child
may reopen this seam only if M223's actual live caller retains and exposes the
predeclared vector with layer/epoch/object provenance; it must then restart
from the frozen M230 contract and charge label packing plus both gathers.
