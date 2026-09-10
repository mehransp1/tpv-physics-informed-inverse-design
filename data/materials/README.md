# Optical-constant material library

This folder is the expandable material-property library used by the TPV simulator.

## Folder layout

```text
data/materials/
├── raw/          # Original user/source CSV or Excel files. Keep these unchanged.
├── processed/    # Canonical wavelength_um,n,k CSV files used by simulations.
├── manifest.json # Auto-generated provenance and wavelength coverage summary.
└── README.md
```

## Adding a new material

1. Put the original `.csv`, `.xlsx`, or `.xls` file in `data/materials/raw/`.
2. Use a descriptive filename such as `HfO2.xlsx`, `ZrO2.csv`, or `Si3N4_ALD_300C.xlsx`.
3. The first three data columns must represent wavelength in **micrometers**, refractive index `n`, and extinction coefficient `k`. Header/source-note rows are allowed above the numeric data.
4. Run:

```bash
python scripts/standardize_materials.py
```

5. Commit the new raw file, generated processed CSV, and updated `manifest.json`.

The parser sorts wavelengths, averages duplicate wavelength rows, preserves a `Source:` note when present, and writes a standard three-column CSV.

## Simulation convention

The project uses

```text
n_complex(lambda) = n(lambda) + i k(lambda)
```

with `k >= 0` denoting absorption.

## Range policy

The runtime material loader **does not extrapolate by default**. A simulation must lie inside the measured/tabulated wavelength range of every material used. This avoids silently inventing optical constants outside their source data.

## Provenance

Keep original source information in the raw file whenever possible. Optical constants are sensitive to deposition method, density, porosity, phase, impurities, temperature, and film thickness, so two datasets with the same chemical formula should be stored as separate files when they represent different material conditions.
