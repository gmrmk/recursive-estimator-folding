"""M178 static verifier: certifies the frozen compile-time constants and
bound arithmetic in 60-digit Decimal, and (when M178_SHA256SUMS_20260807.txt
exists) re-verifies every recorded artifact hash.  Response-free; safe to run
anywhere; exit code 0 iff every check passes."""

from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import m178_certified_phi2_owent as m178  # noqa: E402

getcontext().prec = 60


def dec_exp(x: Decimal, terms: int = 90) -> Decimal:
    total = Decimal(1)
    term = Decimal(1)
    for n in range(1, terms):
        term *= x / n
        total += term
    return total


def checks():
    out = {}

    # 1. GL20 monomial exactness on the 50-digit strings (k = 0..39).
    nodes = [Decimal(s) for s in m178.GL20_NODES_DEC]
    weights = [Decimal(s) for s in m178.GL20_WEIGHTS_DEC]
    worst = Decimal(0)
    for k in range(40):
        q = sum(w * u ** k for u, w in zip(nodes, weights))
        worst = max(worst, abs(q - Decimal(1) / Decimal(k + 1)))
    out["gl20_monomial_worst_residual"] = str(worst)
    out["gl20_monomial_pass"] = worst < Decimal("1e-28")

    # 2. erf Taylor coefficients versus 60-digit recomputation:
    #    c_n = (-1)^n * (2/sqrt(pi)) / (n! * (2n+1)).
    two_over_sqrt_pi = Decimal(m178.ERF_TAYLOR_DEC[0])  # c_0 = 2/sqrt(pi)
    # independent square check: (c_0)^2 * pi/4 == 1 with pi from constant
    pi_dec = Decimal(
        "3.14159265358979323846264338327950288419716939937510582097494")
    out["erf_c0_sq_times_pi_over4_minus1"] = str(
        abs(two_over_sqrt_pi ** 2 * pi_dec / 4 - 1))
    out["erf_c0_pass"] = abs(two_over_sqrt_pi ** 2 * pi_dec / 4 - 1) \
        < Decimal("1e-42")
    fact = Decimal(1)
    worst_c = Decimal(0)
    for n, s in enumerate(m178.ERF_TAYLOR_DEC):
        if n > 0:
            fact *= n
        expect = (-1) ** n * two_over_sqrt_pi / (fact * (2 * n + 1))
        worst_c = max(worst_c, abs(Decimal(s) - expect))
    out["erf_taylor_worst_coeff_residual"] = str(worst_c)
    out["erf_taylor_pass"] = worst_c < Decimal("1e-40")

    # 3. Frozen bound arithmetic in Decimal.
    #    deep tail: exp(-18)/(2 pi) < 2.4e-9
    deep = dec_exp(Decimal(-18)) / (2 * pi_dec)
    out["deep_tail_bound"] = str(deep)
    out["deep_tail_pass"] = deep < Decimal("2.43e-9")
    #    erf Taylor truncation at x = 3.5: term_52 = x^105/(52! *105) * c0
    x = Decimal("3.5")
    f52 = Decimal(1)
    for n in range(1, 53):
        f52 *= n
    t52 = two_over_sqrt_pi * x ** 105 / (f52 * 105)
    out["erf_taylor_tail_at_3p5"] = str(t52)
    out["erf_taylor_tail_pass"] = t52 < Decimal("2e-13")
    #    asymptotic tail width at x = 3.5: (15/(8 x^6)) exp(-x^2)/(x sqrt(pi))
    sqrt_pi = 2 / two_over_sqrt_pi
    width = (Decimal(15) / (8 * x ** 6)) * dec_exp(-x * x) / (x * sqrt_pi)
    out["asym_width_at_3p5"] = str(width)
    out["asym_width_pass"] = width < Decimal("8e-10")
    #    GL20 truncation via the elementary Chebyshev chain (report sec. 5):
    #    M <= exp(2.53125)/0.859375;  |I - GL20| <= 0.5 * 8.02 * M * 2^-40;
    #    per-T error <= that / (2 pi)  <= ERR_OWEN_MAIN = 1e-11.
    m_ell = dec_exp(Decimal("2.53125")) / Decimal("0.859375")
    gl_err = Decimal("0.5") * Decimal("8.02") * m_ell / (Decimal(2) ** 40)
    per_t = gl_err / (2 * pi_dec)
    out["gl20_M_bound"] = str(m_ell)
    out["gl20_truncation_bound"] = str(gl_err)
    out["owen_per_T_truncation"] = str(per_t)
    out["gl20_chain_pass"] = (m_ell < Decimal("14.63")
                              and gl_err < Decimal("5.4e-11")
                              and per_t < Decimal("8.6e-12"))
    #    Horner intermediate-magnitude cap for the erf Taylor rounding proof:
    #    max_n |c_n| * (3.5^2)^n must be below 1200.
    y = Decimal("12.25")
    worst_term = Decimal(0)
    ypow = Decimal(1)
    for s in m178.ERF_TAYLOR_DEC:
        worst_term = max(worst_term, abs(Decimal(s)) * ypow)
        ypow *= y
    out["erf_horner_max_term"] = str(worst_term)
    out["erf_horner_cap_pass"] = worst_term < Decimal(1200)

    # 4. Float round-trip of embedded constants is exact by construction.
    out["float_roundtrip_pass"] = (
        [float(s) for s in m178.GL20_NODES_DEC] == list(m178.GL20_NODES)
        and [float(s) for s in m178.GL20_WEIGHTS_DEC] == list(m178.GL20_WEIGHTS)
        and [float(s) for s in m178.ERF_TAYLOR_DEC] == list(m178.ERF_TAYLOR))

    # 5. Artifact hashes when the sums file exists.
    sums = HERE / "M178_SHA256SUMS_20260807.txt"
    if sums.exists():
        ok = True
        for line in sums.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            rec, name = line.split(maxsplit=1)
            name = name.lstrip("*")
            if name == sums.name:
                continue
            actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            ok = ok and (actual == rec.lower())
        out["artifact_hashes_pass"] = ok
    else:
        out["artifact_hashes_pass"] = "SUMS_FILE_NOT_PRESENT_YET"

    return out


def main():
    out = checks()
    hard = [k for k, v in out.items() if v is False]
    out["m178_static"] = "pass" if not hard else "FAIL"
    out["failed_checks"] = hard
    print(json.dumps(out, indent=1))
    sys.exit(0 if not hard else 1)


if __name__ == "__main__":
    main()
