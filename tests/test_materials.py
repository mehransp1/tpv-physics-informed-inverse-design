from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tpv_design.materials import load_material, parse_material_file, standardize_material_library
from tpv_design.optics import multilayer_rt


def test_shipped_sio2_material_is_available():
    mat = load_material("SiO2", material_root=ROOT / "data" / "materials")
    assert mat.name == "SiO2"
    assert len(mat.wavelength_um) >= 100
    assert mat.wavelength_range_um[0] <= 0.05
    assert mat.wavelength_range_um[1] >= 14.0
    assert np.all(mat.k >= 0)


def test_duplicates_are_averaged_and_sorted(tmp_path):
    path = tmp_path / "demo.csv"
    path.write_text(
        "Wavelength (um),n,k\n"
        "Source: demo,,\n"
        "2.0,2.0,0.2\n"
        "1.0,1.5,0.0\n"
        "2.0,2.2,0.4\n"
    )
    mat = parse_material_file(path)
    assert np.allclose(mat.wavelength_um, [1.0, 2.0])
    assert np.allclose(mat.n, [1.5, 2.1])
    assert np.allclose(mat.k, [0.0, 0.3])


def test_interpolation_and_range_guard():
    mat = load_material("SiO2", material_root=ROOT / "data" / "materials")
    x = np.array([1.0, 2.0, 3.0])
    nc = mat.complex_index_um(x)
    assert nc.shape == x.shape
    assert np.all(np.real(nc) > 0)
    assert np.all(np.imag(nc) >= 0)
    with pytest.raises(ValueError):
        mat.complex_index_um(np.array([20.0]))


def test_dispersive_layer_is_supported_by_tmm():
    mat = load_material("TiO2", material_root=ROOT / "data" / "materials")
    wl_um = np.linspace(0.5, 5.0, 100)
    n_complex = mat.complex_index_um(wl_um)
    R, T, A = multilayer_rt(wl_um * 1e-6, [n_complex], [500e-9])
    assert np.all(np.isfinite(R))
    assert np.all(np.isfinite(T))
    assert np.all(np.isfinite(A))
    assert np.max(np.abs(R + T + A - 1)) < 1e-10
    assert np.min(A) >= -1e-12


def test_standardization_writes_manifest_from_excel(tmp_path):
    root = tmp_path / "materials"
    (root / "raw").mkdir(parents=True)
    pd.DataFrame([
        ["Wavelength (um)", "n", "k"],
        ["Source: synthetic test", None, None],
        [0.5, 1.5, 0.0],
        [1.0, 1.4, 0.01],
    ]).to_excel(root / "raw" / "Demo.xlsx", index=False, header=False)
    manifest = standardize_material_library(root)
    assert len(manifest) == 1
    assert (root / "processed" / "Demo.csv").exists()
    assert (root / "manifest.json").exists()
