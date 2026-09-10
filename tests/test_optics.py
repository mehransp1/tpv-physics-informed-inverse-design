from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tpv_design.optics import multilayer_rt, unpolarized_rt


def test_empty_stack_in_air_is_transparent():
    wl = np.linspace(0.5e-6, 5e-6, 20)
    R, T, A = multilayer_rt(wl, [], [], n_incident=1.0, n_substrate=1.0)
    assert np.allclose(R, 0.0, atol=1e-12)
    assert np.allclose(T, 1.0, atol=1e-12)
    assert np.allclose(A, 0.0, atol=1e-12)


def test_lossless_stack_conserves_energy():
    wl = np.linspace(0.5e-6, 5e-6, 100)
    n_layers = [2.1, 1.45] * 4
    d_layers = [250e-9, 400e-9] * 4
    for angle in (0.0, 20.0, 40.0, 60.0):
        R, T, A = unpolarized_rt(wl, n_layers, d_layers, angle_deg=angle)
        assert np.max(np.abs(R + T + A - 1.0)) < 1e-10
        assert np.min(R) >= -1e-12
        assert np.min(T) >= -1e-12


def test_quarter_wave_stack_reflects_design_wavelength():
    lam0 = 2.4e-6
    nL, nH = 1.45, 2.10
    wl = np.array([lam0])
    n_layers = [nH, nL] * 5
    d_layers = [lam0 / (4*nH), lam0 / (4*nL)] * 5
    R, _, _ = unpolarized_rt(wl, n_layers, d_layers, angle_deg=0.0)
    assert R[0] > 0.90


def test_positive_extinction_coefficient_absorbs_not_amplifies():
    wl = np.array([1.0e-6])
    # Convention: n_complex = n + i*k with k > 0 for absorption.
    R, T, A = multilayer_rt(wl, [2.0 + 0.1j], [500e-9])
    assert 0 <= R[0] <= 1
    assert 0 <= T[0] <= 1
    assert A[0] > 0
    assert np.allclose(R + T + A, 1.0, atol=1e-10)
