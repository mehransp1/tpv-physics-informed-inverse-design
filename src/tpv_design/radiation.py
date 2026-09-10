"""Thermal-radiation utilities used by the TPV forward model."""
from __future__ import annotations

import numpy as np
from scipy.constants import h, c, k, sigma


def planck_spectral_exitance(wavelength_m: np.ndarray, temperature_K: float) -> np.ndarray:
    """Blackbody hemispherical spectral exitance M_lambda in W m^-3.

    Integrating M_lambda over wavelength gives sigma*T^4.
    """
    wavelength_m = np.asarray(wavelength_m, dtype=float)
    if np.any(wavelength_m <= 0):
        raise ValueError("wavelengths must be positive")
    if temperature_K <= 0:
        raise ValueError("temperature_K must be positive")

    x = h * c / (wavelength_m * k * temperature_K)
    return (2 * np.pi * h * c**2 / wavelength_m**5) / np.expm1(x)


def blackbody_total_exitance(temperature_K: float) -> float:
    """Stefan-Boltzmann total blackbody exitance in W m^-2."""
    if temperature_K <= 0:
        raise ValueError("temperature_K must be positive")
    return sigma * temperature_K**4
