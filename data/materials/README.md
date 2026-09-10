# Optical-constant material library

This folder is the expandable material-property library used by the TPV simulator.

## Folder layout

```text
data/materials/
├── raw/          # Drop original CSV/Excel source files here.
├── processed/    # Canonical wavelength_um,n,k tables used by simulations.
├── manifest.json # Provenance, coverage, and representation metadata.
└── README.md
```

The initial library contains wavelength-dependent complex optical constants for:

- 30% porous SiO2
- Al2O3
- MgF2
- SiO2
- Ta2O5
- TiO2
- ZnS
- ZnSe

## Adding a new material

1. Put the original `.csv`, `.xlsx`, or `.xls` file in `data/materials/raw/`.
2. Use a descriptive filename such as `HfO2.xlsx`, `ZrO2.csv`, or `Si3N4_ALD_300C.xlsx`.
3. The first three numeric columns should be wavelength in **micrometers**, refractive index `n`, and extinction coefficient `k`. Header rows and a `Source:` note are allowed.
4. Run:

```bash
python scripts/standardize_materials.py
```

5. The script creates/updates the corresponding table in `processed/` and refreshes `manifest.json`.

The parser sorts wavelengths, averages duplicate wavelength rows, preserves a `Source:` note when present, and writes a standard three-column CSV.

## Simulation convention

```text
n_complex(lambda) = n(lambda) + i k(lambda)
```

with `k >= 0` denoting absorption.

The TMM solver can use one complex-index array per layer, so every layer may have its own wavelength-dependent dispersion and absorption.

## Range policy

The runtime material loader **does not extrapolate by default**. A simulation must lie inside the tabulated wavelength range of every material used. This avoids silently inventing optical constants outside their source data.

## Initial GitHub representation

The eight initial `processed/` tables are compact, error-controlled subsets of the full datasets supplied for this project. Every retained row is an actual source-data point. Linear interpolation reconstructs intermediate values. The corresponding interpolation-error metadata are recorded in `manifest.json`.

The `raw/` folder is intentionally a drop location for future original datasets. When a new raw CSV/Excel file is standardized locally, the full cleaned table is written to `processed/` unless a later compression step is explicitly requested.

## Provenance and physical meaning

Keep original source information whenever possible. Optical constants can depend strongly on deposition method, density, porosity, phase, impurities, film thickness, and temperature. Store physically distinct datasets under distinct filenames instead of treating a chemical formula as a single universal material.
