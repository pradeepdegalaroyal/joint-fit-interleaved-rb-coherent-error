"""Gate-noise channels as PTMs: coherent over-rotation plus T1/T2 decay."""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

from .clifford import ptm_from_rotation, rotation

T2_OVER_T1 = 1.5


def process_infidelity(ptm: np.ndarray) -> float:
    """Average gate infidelity of a single-qubit channel versus identity."""
    f_pro = np.trace(ptm) / 4.0
    return float(1.0 - (2.0 * f_pro + 1.0) / 3.0)


def decay_ptm(tau: float) -> np.ndarray:
    """T1/T2 channel over a gate of duration ``tau`` (in units of T1)."""
    g1 = np.exp(-tau)
    g2 = np.exp(-tau / T2_OVER_T1)
    return ptm_from_rotation(np.diag([g2, g2, g1]), np.array([0.0, 0.0, 1.0 - g1]))


def coherent_ptm(axis: str, infidelity: float) -> np.ndarray:
    """Over-rotation about ``axis`` with the given average infidelity."""
    if infidelity <= 0:
        return np.eye(4)
    theta = 2.0 * np.arcsin(np.sqrt(1.5 * infidelity))
    return ptm_from_rotation(rotation(axis, theta))


def make_noise(total_infidelity: float, coherent_fraction: float, axis: str) -> np.ndarray:
    """Noise channel with fixed total infidelity, split coherent / incoherent."""
    r_coh = coherent_fraction * total_infidelity
    r_inc = total_infidelity - r_coh
    if r_inc > 1e-12:
        tau = brentq(lambda t: process_infidelity(decay_ptm(t)) - r_inc, 1e-9, 1.0)
        dec = decay_ptm(tau)
    else:
        dec = np.eye(4)
    return dec @ coherent_ptm(axis, r_coh)
