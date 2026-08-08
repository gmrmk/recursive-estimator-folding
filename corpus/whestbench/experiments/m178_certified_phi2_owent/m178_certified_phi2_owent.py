"""M178: certified fixed-cost normalized Phi2/Owen-T value-and-derivative evaluator.

Response-free numerical primitive on the SPD stratum of the M177 dispatch:
inputs are M159-normalized (a, b, rho) with finite binary64 a, b and
|rho| <= 1 - 2^-52.  All other strata refuse (M177 owns them).  Fail-closed,
deterministic, no clipping/ridge/floor, no adaptivity, no RNG, no API, and no
opaque CDF: Phi/phi are built here from charged elementary operations with
proven remainders (the installed billed normal-CDF surface exposes no error
contract and is deliberately not used).

Charged-cost discipline: every arithmetic operation on runtime data flows
through a Backend, so one code path serves plain evaluation, static charged
operation counting (installed FlopScope 0.10.0 cost table), and an actual
billed FlopScope trace.  Compile-time constants are free.

Governing predeclaration: M178_PREDECLARED_PROTOCOL_20260807.md (committed
before this file existed).
"""

from __future__ import annotations

from dataclasses import dataclass
import math

# --------------------------------------------------------------------------
# Certified compile-time constants (50-decimal-digit strings; float() rounds
# each correctly to binary64).  Generated with mpmath dps=50; certified by
# verify_m178_static.py (GL monomial residuals in 60-digit Decimal, erf
# coefficient recomputation) plus the perturbation lemma of the report.

GL20_NODES_DEC = (
    "0.00343570040745253760693880576433986088867643455",
    "0.0180140363610431043661669344013613890439698361",
    "0.0438827858743370470661237793983509434754076013",
    "0.0804415140888905883027354691492396573351853175",
    "0.12683404676992460369284746482217920484463466",
    "0.181973159636742487273581651886857031628305442",
    "0.244566499024586450997817974522374500787254335",
    "0.313146955642290219663725911487536381302126839",
    "0.386107074429177460959751902315712687628455531",
    "0.461736739433251333122679795300580894497601867",
    "0.538263260566748666877320204699419105502398133",
    "0.613892925570822539040248097684287312371544469",
    "0.686853044357709780336274088512463618697873161",
    "0.755433500975413549002182025477625499212745665",
    "0.818026840363257512726418348113142968371694558",
    "0.87316595323007539630715253517782079515536534",
    "0.919558485911109411697264530850760342664814683",
    "0.956117214125662952933876220601649056524592399",
    "0.981985963638956895633833065598638610956030164",
    "0.996564299592547462393061194235660139111323565",
)
GL20_WEIGHTS_DEC = (
    "0.00880700356957605915593098117592640818107155277",
    "0.02030071490019347066551997613746605493954532",
    "0.0313360241670545317847532675935208031758005383",
    "0.0416383707883523743623790716110231030500889143",
    "0.050965059908620217518375067740174938083345828",
    "0.0590972659807592086561886888556911435025206098",
    "0.0658443192245883134492472498740815674580552556",
    "0.0710480546591910256646491625335824665172577067",
    "0.074586493236301873393914368500984718346339952",
    "0.0763766935653629253490421659775487967459743226",
    "0.0763766935653629253490421659775487967459743226",
    "0.074586493236301873393914368500984718346339952",
    "0.0710480546591910256646491625335824665172577067",
    "0.0658443192245883134492472498740815674580552556",
    "0.0590972659807592086561886888556911435025206098",
    "0.050965059908620217518375067740174938083345828",
    "0.0416383707883523743623790716110231030500889143",
    "0.0313360241670545317847532675935208031758005383",
    "0.02030071490019347066551997613746605493954532",
    "0.00880700356957605915593098117592640818107155277",
)
ERF_TAYLOR_DEC = (
    "1.12837916709551257389615890312154517168810126",
    "-0.376126389031837524632052967707181723896033753",
    "0.112837916709551257389615890312154517168810126",
    "-0.0268661706451312517594323548362272659925738395",
    "0.00522397762544218784211184677371085727633380212",
    "-0.000854832702345085283254665835698140281581894893",
    "0.000120553329817896642510273387085635167915395434",
    "-0.0000149256503584062509774624193534595922180965775",
    "0.00000164621143658892474016129625221980796523124016",
    "-0.000000163658446912349243173930036770390265549304578",
    "0.0000000148071928158792172395460509458924525973180332",
    "-0.00000000122905553017179273529828881369067788357185256",
    "0.0000000000942275906465041097062021423829519710738420296",
    "-0.00000000000671136685516411037793462552585127999101438958",
    "0.00000000000044632242632864773449318938226104571368814906",
    "-0.0000000000000278351620721092135490376173883232810687232747",
    "1.63426140953671518943213283908716233547428318e-15",
    "-9.06397084280867247920342583023132051607585627e-17",
    "4.76334804051506811970150006093237564658641095e-18",
    "-2.37845988527742942549197708845476246860590021e-19",
    "1.13121872592463106822179398109433824726378181e-20",
    "-5.13620905458581105172686082224450366974696058e-22",
    "2.23087868027464520428540419552033997776888187e-23",
    "-9.28672901131905959230741802020493052725251471e-25",
    "3.71153285316322959896640005909550794881690639e-26",
    "-1.42639301807841764979885178741709717248649736e-27",
    "5.27910333251083455295656321903279795332448224e-29",
    "-1.88412442170420357782288114888039253552994989e-30",
    "6.49290997454456120177058040027704194574857418e-32",
    "-2.16303839011712442139639440570304728759595984e-33",
    "6.97373032879291480122334808396064426055528035e-35",
    "-2.17817485947960984574820395863594111568802919e-36",
    "6.5973565455392028981796562208684754946320115e-38",
    "-1.93952137250134865844268500387359071529208841e-39",
    "5.53912753442414152240664515172764611784185522e-41",
    "-1.53802736368316203237850509243141884157379481e-42",
    "4.1552489658106736795614102573299367485441184e-44",
    "-1.0930925207357808238125511667931004779953897e-45",
    "2.80184344002677928181617694837602651570930375e-47",
    "-7.00233511464011699772299983852496078252568611e-49",
    "1.70735948782891741611147218285022191919607779e-50",
    "-4.06394706183198091992445626831818911122193067e-52",
    "9.44839232862897524800363782270055171516583321e-54",
    "-2.14678788541422853803878432218536994330151249e-55",
    "4.7694215023247671810361143010757708137699588e-57",
    "-1.03657756704982729941932642929363517075830606e-58",
    "2.20496864426213848170076449428987378539050612e-60",
    "-4.59265585479012046580450387388484349476633974e-62",
    "9.37075399924960146588118273236812998287805573e-64",
    "-1.87376445666297947266640842102599177146809195e-65",
    "3.67332041999277163948464225112026109654140799e-67",
    "-7.06273296058004826933083699530071141729834774e-69",
)

GL20_NODES = tuple(float(s) for s in GL20_NODES_DEC)
GL20_WEIGHTS = tuple(float(s) for s in GL20_WEIGHTS_DEC)
ERF_TAYLOR = tuple(float(s) for s in ERF_TAYLOR_DEC)

INV_SQRT_TWO_PI = float("0.398942280401432677939946059934381868475858631")
INV_SQRT_TWO = float("0.707106781186547524400844362104849039284835938")
INV_TWO_PI = float("0.159154943091895335768883763372514362034459646")

# Domain / chart constants (all predeclared in the protocol).
RHO_MAX = 1.0 - 2.0 ** -52          # SPD acceptance bound; beyond -> refuse
TINY_MEAN = 1.0e-290                # |mean| <= TINY_MEAN dispatches to the
                                    # exact zero-mean limit: substitution
                                    # error <= phi(0)*1e-290 < 1e-291, and
                                    # above it every internal product stays
                                    # in the normal range where the per-op
                                    # relative rounding model is valid
ERF_TAYLOR_CUT = 3.5                # |x| <= 3.5: 52-term Taylor chart
ERF_SATURATE = 27.0                 # |x| >= 27: erf = +-1, width < 1e-300
OWEN_DEEP_TAIL_C = 18.0             # c = h^2 q^2 / 2 > 18 -> direct enclosure
F_EPILOGUE = 64                     # published surcharge covering the
                                    # uncharged certification-metadata
                                    # epilogue (error-sum scalar ops)

# Proven per-chart error constants (derivations: M178_REPORT sections 5-6).
ERR_ERF_TAYLOR = 5.0e-10            # truncation 1.7e-13 + Horner rounding
ERR_PHI = 1.0e-9                    # Phi(h) absolute, worst over charts
ERR_OWEN_MAIN = 1.0e-11             # GL20 truncation 8.6e-12 (elementary
                                    # Chebyshev-chain bound) + rounding
ERR_OWEN_DEEP = 1.22e-9             # half of exp(-18)/(2 pi) = 2.4239e-9
FLOAT_MAX = 1.7976931348623157e308
W_VALUE = 1.2e-8                    # value enclosure half-width (static)
W_QARG = 1.7e-9                     # T-argument conditioning term: the
                                    # formation of q (or g, r) carries
                                    # Delta_q <= u|rho|/s, and |dT/dq| <=
                                    # 1/(2 pi), so each of the two T calls
                                    # contributes <= u/(2 pi s_min) =
                                    # 8.4e-10; 1.7e-9 covers both
W_DA_ABS, W_DA_REL = 5.0e-9, 1.0e-8
W_DRHO_ABS, W_DRHO_REL = 5.0e-9, 1.2e-7


class Backend:
    """Plain binary64 execution; subclasses instrument the same code path."""

    name = "plain"

    def c(self, x):          # ingest a compile-time constant (free)
        return x

    def add(self, x, y):
        return x + y

    def sub(self, x, y):
        return x - y

    def mul(self, x, y):
        return x * y

    def div(self, x, y):
        return x / y

    def sqrt(self, x):
        return math.sqrt(x)

    def exp(self, x):
        return math.exp(x)

    def arctan(self, x):
        return math.atan(x)

    def absv(self, x):
        return abs(x)

    def lt(self, x, y):
        return x < y

    def le(self, x, y):
        return x <= y

    def eq(self, x, y):
        return x == y

    def raw(self, x):        # back to a Python float (free)
        return float(x)


class CountingBackend(Backend):
    """Static charged-operation counter on the measured installed FlopScope
    0.10.0 table: add/sub/mul/div/sqrt/abs/compare = 2, exp/arctan = 32."""

    name = "counting"
    COST = {"add": 2, "sub": 2, "mul": 2, "div": 2, "sqrt": 2, "abs": 2,
            "cmp": 2, "exp": 32, "arctan": 32}

    def __init__(self):
        self.flops = 0
        self.calls = {}

    def _charge(self, op):
        self.flops += self.COST[op]
        self.calls[op] = self.calls.get(op, 0) + 1

    def add(self, x, y):
        self._charge("add")
        return x + y

    def sub(self, x, y):
        self._charge("sub")
        return x - y

    def mul(self, x, y):
        self._charge("mul")
        return x * y

    def div(self, x, y):
        self._charge("div")
        return x / y

    def sqrt(self, x):
        self._charge("sqrt")
        return math.sqrt(x)

    def exp(self, x):
        self._charge("exp")
        return math.exp(x)

    def arctan(self, x):
        self._charge("arctan")
        return math.atan(x)

    def absv(self, x):
        self._charge("abs")
        return abs(x)

    def lt(self, x, y):
        self._charge("cmp")
        return x < y

    def le(self, x, y):
        self._charge("cmp")
        return x <= y

    def eq(self, x, y):
        self._charge("cmp")
        return x == y


class FlopscopeBackend(Backend):
    """Billed execution through flopscope.numpy one-element arrays.  Only
    lawful inside a flopscope BudgetContext; used by run_m178_static_audit
    to record the actual installed bill for the identical code path."""

    name = "flopscope"

    def __init__(self):
        import numpy as _np
        import flopscope.numpy as _fnp
        self._np = _np
        self._fnp = _fnp

    def c(self, x):
        return self._fnp.asarray(self._np.full(1, x, dtype=self._np.float64))

    def add(self, x, y):
        return self._fnp.add(x, y)

    def sub(self, x, y):
        return self._fnp.subtract(x, y)

    def mul(self, x, y):
        return self._fnp.multiply(x, y)

    def div(self, x, y):
        return self._fnp.divide(x, y)

    def sqrt(self, x):
        return self._fnp.sqrt(x)

    def exp(self, x):
        return self._fnp.exp(x)

    def arctan(self, x):
        return self._fnp.arctan(x)

    def absv(self, x):
        return self._fnp.abs(x)

    def lt(self, x, y):
        return bool(self._np.asarray(self._fnp.less(x, y)).reshape(-1)[0])

    def le(self, x, y):
        return bool(self._np.asarray(self._fnp.less_equal(x, y)).reshape(-1)[0])

    def eq(self, x, y):
        return bool(self._np.asarray(self._fnp.equal(x, y)).reshape(-1)[0])

    def raw(self, x):
        return float(self._np.asarray(x).reshape(-1)[0])


@dataclass(frozen=True)
class M178Result:
    """Value + first derivatives with certified enclosure half-widths."""

    refused: bool
    reason: str
    value: float
    d_a: float
    d_b: float
    d_rho: float
    w_value: float
    w_da: float
    w_db: float
    w_drho: float
    chart: str

    def enclosure(self):
        # refusals and any nonfinite value must never produce a plausible
        # interval (max/min would silently swallow NaN into (0.0, 1.0))
        if self.refused or math.isnan(self.value):
            nan = float("nan")
            return nan, nan
        lo = max(0.0, self.value - self.w_value)
        hi = min(1.0, self.value + self.w_value)
        return lo, hi


def _refuse(reason):
    nan = float("nan")
    return M178Result(True, reason, nan, nan, nan, nan, nan, nan, nan, nan,
                      "REFUSED")


def _erf_cert(bk, x):
    """(erf(x), absolute error bound).  Charts: 52-term Taylor |x|<=3.5,
    two-sided 4-term asymptotic tail, saturation |x|>=27."""
    ax = bk.absv(x)
    if bk.le(ax, bk.c(ERF_TAYLOR_CUT)):
        y = bk.mul(x, x)
        acc = bk.c(ERF_TAYLOR[-1])
        for coef in reversed(ERF_TAYLOR[:-1]):
            acc = bk.add(bk.mul(acc, y), bk.c(coef))
        return bk.mul(acc, x), ERR_ERF_TAYLOR
    if bk.le(bk.c(ERF_SATURATE), ax):
        one = bk.c(1.0) if not bk.lt(x, bk.c(0.0)) else bk.c(-1.0)
        return one, 1.0e-300
    # asymptotic two-sided enclosure midpoint, x in (3.5, 27)
    x2 = bk.mul(ax, ax)
    t = bk.div(bk.c(1.0), x2)
    s2 = bk.add(bk.sub(bk.c(1.0), bk.mul(bk.c(0.5), t)),
                bk.mul(bk.c(0.75), bk.mul(t, t)))
    half_gap = bk.mul(bk.c(15.0 / 16.0), bk.mul(t, bk.mul(t, t)))
    mid = bk.sub(s2, half_gap)
    pref = bk.div(bk.mul(bk.exp(bk.sub(bk.c(0.0), x2)),
                         bk.c(0.5641895835477562869480794515607725858441)),
                  ax)                       # exp(-x^2) / (x sqrt(pi))
    erfc = bk.mul(pref, mid)
    err = bk.raw(bk.mul(pref, half_gap)) + 1.0e-12
    if bk.lt(x, bk.c(0.0)):
        return bk.sub(erfc, bk.c(1.0)), err          # erf(x) = erfc(|x|) - 1
    return bk.sub(bk.c(1.0), erfc), err


def _Phi_cert(bk, h):
    """(Phi(h), absolute error bound <= ERR_PHI)."""
    x = bk.mul(h, bk.c(INV_SQRT_TWO))
    e, err = _erf_cert(bk, x)
    val = bk.add(bk.c(0.5), bk.mul(bk.c(0.5), e))
    return val, 0.5 * err + 1.0e-16


def _phi_cert(bk, h):
    """(phi(h), relative error bound)."""
    hh = bk.mul(h, h)
    val = bk.mul(bk.exp(bk.sub(bk.c(0.0), bk.mul(bk.c(0.5), hh))),
                 bk.c(INV_SQRT_TWO_PI))
    return val, 5.0e-13


def _owen_t_reduced(bk, h_abs, q):
    """(T(h, q), absolute error) for h >= 0, 0 <= q <= 1."""
    hq = bk.mul(h_abs, q)
    cc = bk.mul(bk.c(0.5), bk.mul(hq, hq))
    half_h2 = bk.mul(bk.c(0.5), bk.mul(h_abs, h_abs))
    if bk.lt(bk.c(OWEN_DEEP_TAIL_C), cc):
        upper = bk.mul(bk.mul(q, bk.exp(bk.sub(bk.c(0.0), half_h2))),
                       bk.c(INV_TWO_PI))
        mid = bk.mul(bk.c(0.5), upper)
        return mid, bk.raw(mid) + 1.0e-15   # enclosure [0, upper]
    pref = bk.mul(bk.mul(q, bk.exp(bk.sub(bk.c(0.0), half_h2))),
                  bk.c(INV_TWO_PI))
    q2 = bk.mul(q, q)
    total = bk.c(0.0)
    for u, w in zip(GL20_NODES, GL20_WEIGHTS):
        u2 = bk.c(u * u)                    # node constant, squared free
        num = bk.exp(bk.sub(bk.c(0.0), bk.mul(cc, u2)))
        den = bk.add(bk.c(1.0), bk.mul(q2, u2))
        total = bk.add(total, bk.mul(bk.c(w), bk.div(num, den)))
    return bk.mul(pref, total), ERR_OWEN_MAIN


def _owen_t_general(bk, h, num, s):
    """(T(h, q), absolute error) with q = num / (h * s), h != 0, s > 0.
    Signs via T(h,-q) = -T(h,q), T(-h,q) = T(h,q); |q| > 1 via the Owen
    reduction identity, with q*h computed stably as num / s."""
    zero = bk.c(0.0)
    if bk.eq(num, zero):
        return zero, 0.0
    h_abs = bk.absv(h)
    n_abs = bk.absv(num)
    d_abs = bk.mul(h_abs, s)
    neg = bk.lt(num, zero) != bk.lt(h, zero)     # sign(q) < 0
    if bk.le(n_abs, d_abs):
        q = bk.div(n_abs, d_abs)
        t, err = _owen_t_reduced(bk, h_abs, q)
    else:
        g = bk.div(n_abs, s)                     # |q| * h_abs, stable
        r = bk.div(d_abs, n_abs)                 # 1/|q| in (0, 1)
        phi_h, e1 = _Phi_cert(bk, h_abs)
        phi_g, e2 = _Phi_cert(bk, g)
        # overflow/underflow channel (adversarially found): g may reach +inf
        # (num overflow, or n_abs/s overflow) and r may underflow to exact 0.
        # Both are the exact q -> +-inf limit: Phi_cert(g) saturates to 1 and
        # the inner T vanishes; guarding here prevents inf*0 = NaN inside the
        # reduced quadrature.  Charged comparisons.
        if bk.le(g, bk.c(FLOAT_MAX)) and not bk.eq(r, bk.c(0.0)):
            t_inner, e3 = _owen_t_reduced(bk, g, r)
        else:
            t_inner, e3 = bk.c(0.0), 0.0
        t = bk.sub(bk.sub(bk.mul(bk.c(0.5), bk.add(phi_h, phi_g)),
                          bk.mul(phi_h, phi_g)),
                   t_inner)
        err = 1.5 * e1 + 1.5 * e2 + e3 + 3.0e-16
    # unconditional sign multiply keeps the charged count branch-independent
    sign = bk.c(-1.0) if neg else bk.c(1.0)
    return bk.mul(sign, t), err


def _derivatives(bk, a, b, rho, s):
    """Closed-form first derivatives on the SPD stratum."""
    t_a = bk.div(bk.sub(b, bk.mul(rho, a)), s)
    t_b = bk.div(bk.sub(a, bk.mul(rho, b)), s)
    phi_a, _ = _phi_cert(bk, a)
    phi_b, _ = _phi_cert(bk, b)
    Phi_ta, _ = _Phi_cert(bk, t_a)
    Phi_tb, _ = _Phi_cert(bk, t_b)
    d_a = bk.mul(phi_a, Phi_ta)
    d_b = bk.mul(phi_b, Phi_tb)
    ee = bk.mul(bk.c(0.5), bk.add(bk.mul(t_b, t_b), bk.mul(b, b)))
    d_rho = bk.mul(bk.exp(bk.sub(bk.c(0.0), ee)),
                   bk.div(bk.c(INV_TWO_PI), s))
    return d_a, d_b, d_rho


def evaluate(a, b, rho, backend=None):
    """Certified Phi2(a, b; rho) value and (d/da, d/db, d/drho) on the SPD
    stratum.  Fail-closed refusal for every other stratum."""
    bk = backend if backend is not None else Backend()
    A = bk.c(a)
    B = bk.c(b)
    R = bk.c(rho)
    fmax = bk.c(FLOAT_MAX)
    finite = (bk.le(bk.absv(A), fmax) and bk.le(bk.absv(B), fmax)
              and bk.le(bk.absv(R), fmax))
    if not finite:
        return _refuse("NONFINITE_INPUT")
    if not bk.le(bk.absv(R), bk.c(RHO_MAX)):
        return _refuse("NON_SPD_OR_RANK_ONE_CHART")

    # tiny-mean chart: below TINY_MEAN the subnormal range breaks the per-op
    # relative rounding model (adversarially demonstrated at 5e-324), so the
    # exact zero-mean limit is substituted; proven remainder < 1e-291.
    tiny = bk.c(TINY_MEAN)
    if bk.le(bk.absv(A), tiny):
        a = 0.0
        A = bk.c(0.0)
    if bk.le(bk.absv(B), tiny):
        b = 0.0
        B = bk.c(0.0)

    swapped = bk.lt(B, A)
    if swapped:
        a, b = b, a
        A, B = B, A

    one = bk.c(1.0)
    s2 = bk.mul(bk.sub(one, R), bk.add(one, R))
    s = bk.sqrt(s2)

    zero_probe = bk.c(0.0)
    a_is_zero = bk.eq(A, zero_probe)
    b_is_zero = bk.eq(B, zero_probe)

    chart = "SPD_GENERIC"
    if a_is_zero and b_is_zero:
        # Phi2(0,0;rho) = 1/4 + arcsin(rho)/(2 pi), arcsin via arctan(rho/s)
        v = bk.add(bk.c(0.25),
                   bk.mul(bk.c(INV_TWO_PI), bk.arctan(bk.div(R, s))))
        value, w_v = bk.raw(v), 1.0e-14
        chart = "SPD_DOUBLE_ZERO"
    else:
        Phi_a, ea = _Phi_cert(bk, A)
        Phi_b, eb = _Phi_cert(bk, B)
        if a_is_zero:
            # canonical order gives a = 0 <= b with b != 0, hence b > 0
            # exactly: T(0, q_a -> +inf) = +1/4 (swap invariant, no runtime
            # branch and therefore no unmetered comparison)
            t_a = bk.c(0.25)
            e_ta = 0.0
            chart = "SPD_ONE_ZERO"
        else:
            num_a = bk.sub(B, bk.mul(R, A))
            t_a, e_ta = _owen_t_general(bk, A, num_a, s)
        if b_is_zero:
            # canonical order gives a <= b = 0 with a != 0, hence a < 0
            # exactly: T(0, q_b -> -inf) = -1/4 (swap invariant)
            t_b = bk.c(-0.25)
            e_tb = 0.0
            chart = "SPD_ONE_ZERO"
        else:
            num_b = bk.sub(A, bk.mul(R, B))
            t_b, e_tb = _owen_t_general(bk, B, num_b, s)
        # delta predicate via sign comparisons only: the fp product a*b
        # underflows to +-0 for tiny nonzero inputs (adversarially found),
        # so the sign test must never touch the product.  Charged ops.
        a_neg = bk.lt(A, zero_probe)
        b_neg = bk.lt(B, zero_probe)
        apb = bk.add(A, B)
        apb_nonneg = bk.le(zero_probe, apb)
        either_zero = a_is_zero or b_is_zero
        if (not either_zero and a_neg == b_neg) \
                or (either_zero and apb_nonneg):
            delta = bk.c(0.0)
        else:
            delta = bk.c(0.5)
        v = bk.sub(bk.sub(bk.sub(bk.mul(bk.c(0.5), bk.add(Phi_a, Phi_b)),
                                 t_a),
                          t_b),
                   delta)
        value = bk.raw(v)
        w_v = min(W_VALUE,
                  0.5 * ea + 0.5 * eb + e_ta + e_tb + W_QARG + 1.0e-15)
        w_v = max(w_v, 1.0e-15)

    d_a, d_b, d_rho = _derivatives(bk, A, B, R, s)
    # enclosure-width bookkeeping is charged (abs + mul + add per output);
    # the residual scalar epilogue on certification metadata (error-sum
    # accumulation, <= ~15 ops) is covered by the published F_EPILOGUE
    # surcharge rather than metered inline.
    w_da_v = bk.add(bk.c(W_DA_ABS), bk.mul(bk.c(W_DA_REL), bk.absv(d_a)))
    w_db_v = bk.add(bk.c(W_DA_ABS), bk.mul(bk.c(W_DA_REL), bk.absv(d_b)))
    w_dr_v = bk.add(bk.c(W_DRHO_ABS),
                    bk.mul(bk.c(W_DRHO_REL), bk.absv(d_rho)))
    d_a_f, d_b_f, d_rho_f = bk.raw(d_a), bk.raw(d_b), bk.raw(d_rho)
    w_da_f, w_db_f = bk.raw(w_da_v), bk.raw(w_db_v)
    if swapped:
        d_a_f, d_b_f = d_b_f, d_a_f
        w_da_f, w_db_f = w_db_f, w_da_f

    return M178Result(
        refused=False, reason="",
        value=value, d_a=d_a_f, d_b=d_b_f, d_rho=d_rho_f,
        w_value=w_v,
        w_da=w_da_f,
        w_db=w_db_f,
        w_drho=bk.raw(w_dr_v),
        chart=chart,
    )
