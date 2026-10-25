"""Simulated (interleaved) randomized benchmarking with exact PTM products."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .clifford import build_group, ptm_from_rotation

ROTS, TABLE, INV = build_group()
CLIFF_PTM = np.array([ptm_from_rotation(r) for r in ROTS])
LENGTHS = np.array([1, 10, 25, 50, 100, 150, 200, 300])


@dataclass
class RBData:
    """Observed survival frequencies for the reference and interleaved runs."""

    lengths: np.ndarray
    ref: np.ndarray
    itl: np.ndarray
    shots: int
    n_seq: int


def _survival(noisy: np.ndarray, seqs: np.ndarray, gate_idx: int | None,
              gate_noise: np.ndarray) -> np.ndarray:
    """Exact survival probabilities of |0> for a batch of sequences (+ inversion)."""
    n = seqs.shape[0]
    state = np.tile(np.array([1.0, 0.0, 0.0, 1.0]), (n, 1))
    ideal = np.zeros(n, int)
    if gate_idx is not None:
        gate = gate_noise @ CLIFF_PTM[gate_idx]
    for k in range(seqs.shape[1]):
        c = seqs[:, k]
        state = np.einsum("nij,nj->ni", noisy[c], state)
        ideal = TABLE[ideal, c]
        if gate_idx is not None:
            state = state @ gate.T
            ideal = TABLE[ideal, gate_idx]
    state = np.einsum("nij,nj->ni", noisy[INV[ideal]], state)
    return 0.5 * (1.0 + state[:, 3])


def simulate(rng: np.random.Generator, n_ref: np.ndarray, gate_idx: int, n_gate: np.ndarray,
             shots: int, n_seq: int = 12, readout: float = 0.0) -> RBData:
    """Run reference and interleaved RB; return noisy survival frequencies.

    ``n_ref`` is the PTM noise after every Clifford, ``n_gate`` the extra noise
    on the interleaved gate; ``readout`` is a symmetric bit-flip error.
    """
    noisy = np.array([n_ref @ c for c in CLIFF_PTM])
    ref = np.zeros(len(LENGTHS))
    itl = np.zeros(len(LENGTHS))
    for li, m in enumerate(LENGTHS):
        seqs = rng.integers(0, 24, (n_seq, m))
        counts = []
        for gi in (None, gate_idx):
            sv = _survival(noisy, seqs, gi, n_gate)
            counts.append(rng.binomial(shots, (1 - readout) * sv + readout * (1 - sv)).sum())
        ref[li], itl[li] = counts[0] / (shots * n_seq), counts[1] / (shots * n_seq)
    return RBData(LENGTHS.copy(), ref, itl, shots, n_seq)
