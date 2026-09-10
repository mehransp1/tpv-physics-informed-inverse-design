from pathlib import Path
import sys

import numpy as np
from scipy.constants import sigma

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tpv_design.radiation import planck_spectral_exitance
from tpv_design.tpv import evaluate_tpv


def test_planck_integral_matches_stefan_boltzmann():
    # Log grid captures both tails sufficiently well for this numerical check.
    wl = np.geomspace(0.05e-6, 300e-6, 30000)
    T = 1800.0
    M = planck_spectral_exitance(wl, T)
    numeric = np.trapezoid(M, wl)
    exact = sigma * T**4
    assert abs(numeric/exact - 1.0) < 2e-4


def test_tpv_metrics_are_finite_for_transparent_filter():
    wl = np.linspace(0.2e-6, 30e-6, 5000)
    Tfilter = np.ones_like(wl)
    m = evaluate_tpv(
        wl,
        Tfilter,
        emitter_temperature_K=1800.0,
        bandgap_eV=0.72,
        cell_temperature_K=300.0,
    )
    assert 1.6 < m.cutoff_wavelength_um < 1.9
    assert m.jsc_A_cm2 > 0
    assert 0 < m.voc_V < 0.72
    assert 0 < m.fill_factor < 1
    assert m.pmax_W_cm2 > 0
    assert 0 < m.cell_efficiency < 1
    assert 0 < m.system_efficiency_no_recycling < 1
