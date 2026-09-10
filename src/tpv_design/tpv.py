"""Idealized TPV performance metrics built on a filter transmission spectrum."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.constants import h, c, k, e

from .radiation import planck_spectral_exitance, blackbody_total_exitance


@dataclass(frozen=True)
class TPVMetrics:
    cutoff_wavelength_um: float
    incident_power_W_cm2: float
    above_bandgap_power_W_cm2: float
    spectral_efficiency: float
    jsc_A_cm2: float
    j0_radiative_A_cm2: float
    voc_V: float
    vmpp_V: float
    jmpp_A_cm2: float
    fill_factor: float
    pmax_W_cm2: float
    cell_efficiency: float
    system_efficiency_no_recycling: float


def evaluate_tpv(
    wavelength_m: np.ndarray,
    transmittance: np.ndarray,
    *,
    emitter_temperature_K: float,
    bandgap_eV: float = 0.72,
    cell_temperature_K: float = 300.0,
    eqe: float = 1.0,
    voltage_samples: int = 4000,
) -> TPVMetrics:
    """Evaluate an ideal radiative-limit single-junction TPV cell.

    Notes
    -----
    - The filter transmittance is applied to blackbody hemispherical spectral
      exitance from the emitter.
    - EQE is constant for above-bandgap photons and zero below the bandgap.
    - Dark current is the radiative detailed-balance limit of an ideal cell.
    - Non-radiative recombination, series/shunt resistance, view factors,
      finite emitter emissivity, and photon recycling are not yet included.
    - `cell_efficiency` = Pmax / power transmitted to the cell.
    - `system_efficiency_no_recycling` = Pmax / (sigma*T_emitter^4).
    """
    wavelength_m = np.asarray(wavelength_m, dtype=float)
    transmittance = np.asarray(transmittance, dtype=float)

    if wavelength_m.shape != transmittance.shape:
        raise ValueError("wavelength_m and transmittance must have same shape")
    if np.any(wavelength_m <= 0):
        raise ValueError("wavelengths must be positive")
    if not 0 <= eqe <= 1:
        raise ValueError("eqe must be between 0 and 1")
    if bandgap_eV <= 0 or cell_temperature_K <= 0 or emitter_temperature_K <= 0:
        raise ValueError("bandgap and temperatures must be positive")
    if voltage_samples < 100:
        raise ValueError("voltage_samples must be >= 100")

    cutoff_m = h * c / (bandgap_eV * e)
    useful = wavelength_m <= cutoff_m

    emitter_M = planck_spectral_exitance(wavelength_m, emitter_temperature_K)
    incident_M = np.clip(transmittance, 0.0, None) * emitter_M

    P_incident = np.trapezoid(incident_M, wavelength_m)
    P_above = np.trapezoid(incident_M[useful], wavelength_m[useful])
    spectral_eff = P_above / P_incident if P_incident > 0 else 0.0

    photon_flux = incident_M * wavelength_m / (h * c)
    jsc_A_m2 = e * eqe * np.trapezoid(photon_flux[useful], wavelength_m[useful])

    # Ideal radiative saturation current: blackbody photon emission from the
    # cell into one hemisphere, integrated for E >= Eg.
    cell_M = planck_spectral_exitance(wavelength_m, cell_temperature_K)
    cell_photon_flux = cell_M * wavelength_m / (h * c)
    j0_A_m2 = e * np.trapezoid(cell_photon_flux[useful], wavelength_m[useful])

    if jsc_A_m2 <= 0 or j0_A_m2 <= 0:
        voc = vmpp = jmpp_A_m2 = pmax_AW_m2 = ff = 0.0
    else:
        vt = k * cell_temperature_K / e
        voc = vt * np.log1p(jsc_A_m2 / j0_A_m2)
        voltages = np.linspace(0.0, voc, voltage_samples)
        currents = jsc_A_m2 - j0_A_m2 * np.expm1(voltages / vt)
        powers = voltages * currents
        i_max = int(np.argmax(powers))
        vmpp = float(voltages[i_max])
        jmpp_A_m2 = float(currents[i_max])
        pmax_AW_m2 = float(powers[i_max])
        ff = pmax_AW_m2 / (voc * jsc_A_m2)

    emitter_total = blackbody_total_exitance(emitter_temperature_K)
    cell_eff = pmax_AW_m2 / P_incident if P_incident > 0 else 0.0
    system_eff = pmax_AW_m2 / emitter_total

    return TPVMetrics(
        cutoff_wavelength_um=cutoff_m * 1e6,
        incident_power_W_cm2=P_incident / 1e4,
        above_bandgap_power_W_cm2=P_above / 1e4,
        spectral_efficiency=float(spectral_eff),
        jsc_A_cm2=jsc_A_m2 / 1e4,
        j0_radiative_A_cm2=j0_A_m2 / 1e4,
        voc_V=float(voc),
        vmpp_V=float(vmpp),
        jmpp_A_cm2=jmpp_A_m2 / 1e4,
        fill_factor=float(ff),
        pmax_W_cm2=pmax_AW_m2 / 1e4,
        cell_efficiency=float(cell_eff),
        system_efficiency_no_recycling=float(system_eff),
    )
