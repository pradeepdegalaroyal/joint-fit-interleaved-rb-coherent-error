"""IRB gate-error estimators: standard independent fits vs shot-aware joint fit."""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.optimize import least_squares

from .rb import RBData

D = 2


def _r_from_ratio(p_int: float, p_ref: float) -> float:
    return (D - 1) / D * (1.0 - p_int / p_ref)


def _sigma(y: np.ndarray, n_tot: int, weighted: bool) -> np.ndarray:
    if not weighted:
        return np.ones_like(y)
    yc = np.clip(y, 0.5 / n_tot, 1 - 0.5 / n_tot)
    return np.sqrt(yc * (1 - yc) / n_tot)


def _fit_single(m: np.ndarray, y: np.ndarray, sig: np.ndarray) -> np.ndarray:
    def f(t):
        return (t[0] * t[2] ** m + t[1] - y) / sig

    return least_squares(f, [0.5, 0.5, 0.995], bounds=([0, 0, 0.8], [1, 1, 1.0])).x


def independent(d: RBData, weighted: bool = False) -> float:
    """Textbook IRB: two separate 3-parameter fits, r from the decay ratio."""
    n = d.shots * d.n_seq
    pr = _fit_single(d.lengths, d.ref, _sigma(d.ref, n, weighted))[2]
    pi = _fit_single(d.lengths, d.itl, _sigma(d.itl, n, weighted))[2]
    return _r_from_ratio(pi, pr)


def joint(d: RBData, weighted: bool = True) -> float:
    """Joint fit: shared (A, B) across both curves, free (p_ref, p_int)."""
    n = d.shots * d.n_seq
    m = d.lengths
    sr, si = _sigma(d.ref, n, weighted), _sigma(d.itl, n, weighted)

    def f(t):
        a, b, pr, pi = t
        return np.concatenate([(a * pr**m + b - d.ref) / sr, (a * pi**m + b - d.itl) / si])

    x = least_squares(f, [0.5, 0.5, 0.995, 0.99], bounds=([0, 0, 0.8, 0.8], [1, 1, 1, 1])).x
    return _r_from_ratio(x[3], x[2])


METHODS: dict[str, Callable[[RBData], float]] = {
    "IRB (independent, unweighted)": lambda d: independent(d, False),
    "independent + shot weights": lambda d: independent(d, True),
    "joint fit, unweighted": lambda d: joint(d, False),
    "joint fit + shot weights": lambda d: joint(d, True),
}
