"""One simulated IRB experiment cell and its metrics."""
from __future__ import annotations

import numpy as np

from .estimators import METHODS
from .noise import make_noise, process_infidelity
from .rb import simulate

R_REF = 3e-3  # per-Clifford reference infidelity
R_GATE = 4e-3  # true infidelity of the interleaved gate (target quantity)
GATE_IDX = 5  # fixed non-trivial Clifford


def run_cell(seed: int, n_rep: int, shots: int, coh_frac: float, readout: float = 0.0,
             n_seq: int = 12) -> dict[str, np.ndarray]:
    """Estimate the gate error ``n_rep`` times; return signed errors per method."""
    rng = np.random.default_rng(seed)
    n_ref = make_noise(R_REF, coh_frac, "z")
    n_gate = make_noise(R_GATE, coh_frac, "x")
    truth = process_infidelity(n_gate)
    out: dict[str, list[float]] = {k: [] for k in METHODS}
    for _ in range(n_rep):
        d = simulate(rng, n_ref, GATE_IDX, n_gate, shots, n_seq, readout)
        for k, fn in METHODS.items():
            out[k].append(fn(d) - truth)
    return {k: np.array(v) for k, v in out.items()}


def summarize(errs: np.ndarray) -> tuple[float, float]:
    """Return (rmse, bias) of estimator errors."""
    return float(np.sqrt(np.mean(errs**2))), float(np.mean(errs))
