"""Generate M198's independent high-precision rank-one derivative fixture.

Development-only.  This file intentionally imports no M124/M178/M179 code.
It needs ``mpmath`` and writes JSON to stdout; the checked-in fixture is what
the dependency-free unit test consumes.
"""

from __future__ import annotations

import json

import mpmath as mp


mp.mp.dps = 100
NODES = tuple(range(-4, 5))
W4 = (
    mp.mpf(7) / 240,
    -mp.mpf(2) / 5,
    mp.mpf(169) / 60,
    -mp.mpf(122) / 15,
    mp.mpf(91) / 8,
    -mp.mpf(122) / 15,
    mp.mpf(169) / 60,
    -mp.mpf(2) / 5,
    mp.mpf(7) / 240,
)
SQRT2 = mp.sqrt(2)
SQRT2PI = mp.sqrt(2 * mp.pi)


def phi(x):
    return mp.exp(-x * x / 2) / SQRT2PI


def Phi(x):
    return (1 + mp.erf(x / SQRT2)) / 2


def relu_mean(mean, sigma):
    alpha = mean / sigma
    return sigma * phi(alpha) + mean * Phi(alpha)


def relu_second(mean, sigma):
    alpha = mean / sigma
    return (mean * mean + sigma * sigma) * Phi(alpha) + mean * sigma * phi(alpha)


def raw_pair(mean_i, mean_j, sigma_i, sigma_j, rho):
    lower = -mean_i / sigma_i
    conditional_sigma = sigma_j * mp.sqrt(1 - rho * rho)

    def integrand(z):
        xi = mean_i + sigma_i * z
        conditional_mean = mean_j + rho * sigma_j * z
        return xi * phi(z) * relu_mean(conditional_mean, conditional_sigma)

    if lower < 0:
        return mp.quad(integrand, [lower, 0, mp.inf])
    return mp.quad(integrand, [lower, mp.inf])


def d4_9point(function, h):
    return sum(weight * function(node * h) for node, weight in zip(NODES, W4)) / h**4


def d4_richardson(function):
    coarse = d4_9point(function, mp.mpf(1) / 16)
    fine = d4_9point(function, mp.mpf(1) / 32)
    result = (64 * fine - coarse) / 63
    return result, abs(result - fine)


def serial(value):
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return mp.nstr(value, 45)


def build_case(n, coefficient):
    sigmas = [mp.mpf("0.75") + mp.mpf("0.15") * i for i in range(n)]
    alphas = [mp.mpf(x) for x in ("-0.7", "0.25", "0.9", "-0.35", "0.55")[:n]]
    means = [sigmas[i] * alphas[i] for i in range(n)]
    covariance = [
        [sigmas[i] * sigmas[j] * mp.mpf("0.55") ** abs(i - j) for j in range(n)]
        for i in range(n)
    ]
    raw_direction = [mp.mpf(i + 1) * (-1 if i % 2 else 1) for i in range(n)]
    norm = mp.sqrt(sum(value * value for value in raw_direction))
    direction = [sigmas[i] * raw_direction[i] / norm for i in range(n)]
    baseline_mean = [relu_mean(means[i], sigmas[i]) for i in range(n)]
    delta_mean = []
    delta_raw = [[mp.mpf(0) for _ in range(n)] for _ in range(n)]
    stability = []

    for i in range(n):
        derivative, error = d4_richardson(
            lambda t, i=i: relu_mean(means[i] + t * direction[i], sigmas[i])
        )
        delta_mean.append(coefficient * derivative / 24)
        stability.append(error)
        derivative, error = d4_richardson(
            lambda t, i=i: relu_second(means[i] + t * direction[i], sigmas[i])
        )
        delta_raw[i][i] = coefficient * derivative / 24
        stability.append(error)

    for i in range(n):
        for j in range(i + 1, n):
            rho = covariance[i][j] / (sigmas[i] * sigmas[j])
            derivative, error = d4_richardson(
                lambda t, i=i, j=j, rho=rho: raw_pair(
                    means[i] + t * direction[i],
                    means[j] + t * direction[j],
                    sigmas[i],
                    sigmas[j],
                    rho,
                )
            )
            delta_raw[i][j] = delta_raw[j][i] = coefficient * derivative / 24
            stability.append(error)

    delta_covariance = [
        [
            delta_raw[i][j]
            - delta_mean[i] * baseline_mean[j]
            - baseline_mean[i] * delta_mean[j]
            for j in range(n)
        ]
        for i in range(n)
    ]
    return {
        "case_id": f"rank1_n{n}_{'pos' if coefficient > 0 else 'neg'}",
        "layer": n,
        "epoch": 198900 + n,
        "mean": serial(means),
        "covariance": serial(covariance),
        "direction": serial(direction),
        "coefficient": serial(coefficient),
        "expected_delta_mean": serial(delta_mean),
        "expected_delta_covariance": serial(delta_covariance),
        "max_richardson_fine_correction_proxy": serial(max(stability)),
    }


def main():
    cases = []
    coefficients = (mp.mpf("0.125"), mp.mpf("-0.075"))
    for n in range(2, 6):
        cases.append(build_case(n, coefficients[n % 2]))
    payload = {
        "oracle": "mpmath_100dps_rank1_d4_no_m124_m178_m179",
        "finite_difference": "9-point fourth derivative; h=1/16,1/32; Richardson cancels h^6 and yields O(h^8)",
        "correction_proxy_note": "stored max is abs(Richardson-fine), an O(h^6) correction proxy, not a residual bound",
        "cases": cases,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
