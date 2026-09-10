"""Baseline SiO2/ZrO2 quarter-wave TPV filter for a GaSb cell."""
from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

# Allow running this example before installing the package.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tpv_design.optics import hemispherical_rt, unpolarized_rt
from tpv_design.radiation import planck_spectral_exitance
from tpv_design.tpv import evaluate_tpv


def main() -> None:
    wavelength_um = np.linspace(0.3, 20.0, 1800)
    wavelength_m = wavelength_um * 1e-6

    # Baseline constant-index model. Replace with dispersive n(lambda), k(lambda)
    # data in the next research phase.
    n_sio2 = 1.45
    n_zro2 = 2.10
    design_wavelength_um = 2.40
    pairs = 5

    d_sio2_m = design_wavelength_um * 1e-6 / (4 * n_sio2)
    d_zro2_m = design_wavelength_um * 1e-6 / (4 * n_zro2)

    # Incident side -> substrate side: [high, low] repeated.
    n_layers = [n_zro2, n_sio2] * pairs
    d_layers_m = [d_zro2_m, d_sio2_m] * pairs

    R0, T0, A0 = unpolarized_rt(
        wavelength_m, n_layers, d_layers_m, angle_deg=0.0
    )

    # Lambertian/unpolarized angular average. A modest angle grid keeps this
    # example fast; increase the density for production dataset generation.
    R_h, T_h, A_h = hemispherical_rt(
        wavelength_m,
        n_layers,
        d_layers_m,
        angles_deg=np.linspace(0.0, 85.0, 24),
    )

    metrics = evaluate_tpv(
        wavelength_m,
        T_h,
        emitter_temperature_K=1800.0,
        bandgap_eV=0.72,
        cell_temperature_K=300.0,
        eqe=1.0,
    )

    print("=== Filter ===")
    print(f"Pairs: {pairs}")
    print(f"SiO2 quarter-wave thickness: {d_sio2_m*1e9:.1f} nm")
    print(f"ZrO2 quarter-wave thickness: {d_zro2_m*1e9:.1f} nm")
    print(f"Max |R+T+A-1| (hemispherical): {np.max(np.abs(R_h+T_h+A_h-1)):.3e}")

    print("\n=== Ideal radiative-limit TPV metrics ===")
    print(f"GaSb cutoff wavelength: {metrics.cutoff_wavelength_um:.3f} um")
    print(f"Incident power at cell: {metrics.incident_power_W_cm2:.3f} W/cm^2")
    print(f"Above-bandgap power: {metrics.above_bandgap_power_W_cm2:.3f} W/cm^2")
    print(f"Spectral efficiency: {100*metrics.spectral_efficiency:.2f} %")
    print(f"Jsc: {metrics.jsc_A_cm2:.3f} A/cm^2")
    print(f"Voc: {metrics.voc_V:.3f} V")
    print(f"Fill factor: {metrics.fill_factor:.3f}")
    print(f"Pmax: {metrics.pmax_W_cm2:.3f} W/cm^2")
    print(f"Cell efficiency: {100*metrics.cell_efficiency:.2f} %")
    print(
        "System efficiency (no reflected-photon recycling): "
        f"{100*metrics.system_efficiency_no_recycling:.2f} %"
    )

    fig_dir = ROOT / "results"
    fig_dir.mkdir(exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.plot(wavelength_um, R0, label="R, normal incidence")
    plt.plot(wavelength_um, T0, label="T, normal incidence")
    plt.plot(wavelength_um, R_h, "--", label="R, hemispherical avg")
    plt.axvline(metrics.cutoff_wavelength_um, linestyle=":", label="GaSb cutoff")
    plt.xlabel("Wavelength (um)")
    plt.ylabel("Power fraction")
    plt.ylim(-0.02, 1.02)
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "quarter_wave_rt.png", dpi=180)
    plt.close()

    emitter = planck_spectral_exitance(wavelength_m, 1800.0)
    transmitted = emitter * T_h
    plt.figure(figsize=(8, 5))
    plt.plot(wavelength_um, emitter / emitter.max(), label="1800 K blackbody")
    plt.plot(
        wavelength_um,
        transmitted / transmitted.max(),
        label="After filter",
    )
    plt.axvline(metrics.cutoff_wavelength_um, linestyle=":", label="GaSb cutoff")
    plt.xlabel("Wavelength (um)")
    plt.ylabel("Normalized spectral exitance")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "quarter_wave_thermal_spectrum.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    main()
