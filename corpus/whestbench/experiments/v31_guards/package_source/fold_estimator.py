"""Regime helpers shared by the terminal-layer fold."""

from __future__ import annotations

import flopscope.numpy as fnp


def _initial_regimes(alpha, dead_alpha: float, on_alpha: float):
    dead = fnp.flatnonzero(alpha < dead_alpha)
    on = fnp.flatnonzero(alpha > on_alpha)
    kink = fnp.flatnonzero(
        fnp.logical_and(alpha >= dead_alpha, alpha <= on_alpha)
    )
    return dead, kink, on


def _refine_dead(dead, pilot_pre):
    if dead.shape[0] == 0:
        return dead, dead
    fired = fnp.max(pilot_pre, axis=0) > 0.0
    rescued = dead[fnp.flatnonzero(fired)]
    confirmed = dead[fnp.flatnonzero(~fired)]
    return confirmed, rescued


def _refine_on(on, pilot_pre):
    if on.shape[0] == 0:
        return on, on
    crossed = fnp.min(pilot_pre, axis=0) <= 0.0
    demoted = on[fnp.flatnonzero(crossed)]
    confirmed = on[fnp.flatnonzero(~crossed)]
    return confirmed, demoted
