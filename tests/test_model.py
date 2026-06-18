import numpy as np
import pytest

from cuerda.analysis import harmonic_table
from cuerda.config import Params
from cuerda.model import simulate, triangular_pluck


def test_triangular_pluck_peak_is_exact():
    x = np.linspace(0, 0.4, 5)
    u = triangular_pluck(x, xp=0.2, L=0.4, amplitude=0.5)

    assert u[2] == pytest.approx(0.5)
    assert u[0] == pytest.approx(0.0)
    assert u[-1] == pytest.approx(0.0)


def test_simulate_rejects_unstable_cfl():
    p = Params(f1=10000, fs=44100)

    with pytest.raises(ValueError, match="CFL"):
        simulate(p)


def test_fifth_harmonic_is_near_zero_when_pluck_is_one_fifth():
    p = Params(
        f1=220,
        fs=44100,
        duration=2,
        pluck_pos=0.2,
        pickup_pos=0.82,
        sigma0=0,
        sigma1=0,
    )

    result = simulate(p)
    rows = harmonic_table(p, result, modes=10)
    _, _, pred, sim = rows[4]

    assert pred < 1e-10
    assert sim < 0.05
