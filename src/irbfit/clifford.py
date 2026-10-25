"""Single-qubit Clifford group and Pauli transfer matrices (PTMs)."""
from __future__ import annotations

import numpy as np

_H = np.array([[0, 0, 1], [0, -1, 0], [1, 0, 0]], float)  # Hadamard as SO(3)
_S = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], float)  # S gate as SO(3)


def _key(m: np.ndarray) -> tuple:
    return tuple(np.round(m.ravel()).astype(int))


def build_group() -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    """Return (rotations, product table, inverse table) of the 24 Cliffords.

    ``table[a, b]`` is the index of "apply a, then b".
    """
    rots = [np.eye(3)]
    seen = {_key(rots[0])}
    frontier = [rots[0]]
    while frontier:
        new = []
        for r in frontier:
            for g in (_H, _S):
                n = g @ r
                if _key(n) not in seen:
                    seen.add(_key(n))
                    rots.append(n)
                    new.append(n)
        frontier = new
    assert len(rots) == 24
    idx = {_key(r): i for i, r in enumerate(rots)}
    table = np.zeros((24, 24), int)
    for a in range(24):
        for b in range(24):
            table[a, b] = idx[_key(rots[b] @ rots[a])]
    inv = np.array([int(np.where(table[a] == 0)[0][0]) for a in range(24)])
    return rots, table, inv


def ptm_from_rotation(r: np.ndarray, shift: np.ndarray | None = None) -> np.ndarray:
    """4x4 PTM (basis I,X,Y,Z) for a Bloch-sphere map v -> r v + shift."""
    p = np.zeros((4, 4))
    p[0, 0] = 1.0
    p[1:, 1:] = r
    if shift is not None:
        p[1:, 0] = shift
    return p


def rotation(axis: str, theta: float) -> np.ndarray:
    """SO(3) rotation by ``theta`` about x, y or z."""
    c, s = np.cos(theta), np.sin(theta)
    return {
        "x": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]),
        "y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
        "z": np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]),
    }[axis]
