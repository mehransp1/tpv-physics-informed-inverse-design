"""Example: dispersive/absorbing SiO2-TiO2 quarter-wave TPV filter."""
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tpv_design.materials import load_material
from tpv_design.optics import unpolarized_rt


def main() -> None:
    material_root = ROOT / "data" / "materials"
    sio2 = load_material("SiO2", material_root=material_root)
    tio2 = load_material("TiO2", material_root=material_root)

    wavelength_um = np.linspace(0.5, 10.0, 1200)
    wavelength_m = wavelength_um * 1e-6
    n_sio2 = sio2.complex_index_um(wavelength_um)
    n_tio2 = tio2.complex_index_um(wavelength_um)

    design_um = 2.4
    nL0 = float(np.real(sio2.complex_index_um([design_um])[0]))
    nH0 = float(np.real(tio2.complex_index_um([design_um])[0]))
    dL = design_um * 1e-6 / (4 * nL0)
    dH = design_um * 1e-6 / (4 * nH0)

    pairs = 5
    n_layers = [x for _ in range(pairs) for x in (n_tio2, n_sio2)]
    d_layers = [x for _ in range(pairs) for x in (dH, dL)]

    R, T, A = unpolarized_rt(wavelength_m, n_layers, d_layers, angle_deg=0.0)

    print(f"Design wavelength: {design_um:.2f} um")
    print(f"TiO2 n({design_um:.1f} um) = {nH0:.4f}; d_H = {dH*1e9:.1f} nm")
    print(f"SiO2 n({design_um:.1f} um) = {nL0:.4f}; d_L = {dL*1e9:.1f} nm")
    print(f"Max |R+T+A-1| = {np.max(np.abs(R+T+A-1)):.3e}")
    print(f"Max stack absorptance = {np.max(A):.4f}")

    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.plot(wavelength_um, R, label="R")
    plt.plot(wavelength_um, T, label="T")
    plt.plot(wavelength_um, A, label="A")
    plt.axvline(design_um, linestyle=":", label="design wavelength")
    plt.xlabel("Wavelength (um)")
    plt.ylabel("Power fraction")
    plt.ylim(-0.02, 1.02)
    plt.legend()
    plt.tight_layout()
    plt.savefig(results / "dispersive_sio2_tio2_rt.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    main()
