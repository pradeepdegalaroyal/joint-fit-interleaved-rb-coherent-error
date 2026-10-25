import numpy as np

from irbfit.clifford import build_group
from irbfit.estimators import independent, joint
from irbfit.noise import make_noise, process_infidelity
from irbfit.rb import simulate


def test_group_size_and_inverse():
    rots, table, inv = build_group()
    assert len(rots) == 24
    assert all(table[a, inv[a]] == 0 for a in range(24))


def test_noise_infidelity_hits_target():
    for f in (0.0, 0.5, 1.0):
        n = make_noise(4e-3, f, "x")
        assert abs(process_infidelity(n) - 4e-3) < 3e-5


def test_noiseless_gate_gives_near_zero_error():
    rng = np.random.default_rng(0)
    n_ref = make_noise(3e-3, 0.0, "z")
    d = simulate(rng, n_ref, 5, np.eye(4), shots=2000, n_seq=6)
    assert abs(joint(d)) < 2e-3
    assert abs(independent(d)) < 4e-3


def test_incoherent_estimate_is_close():
    rng = np.random.default_rng(1)
    n_ref = make_noise(3e-3, 0.0, "z")
    n_g = make_noise(4e-3, 0.0, "x")
    d = simulate(rng, n_ref, 5, n_g, shots=2000, n_seq=10)
    assert abs(joint(d) - 4e-3) < 2.5e-3
